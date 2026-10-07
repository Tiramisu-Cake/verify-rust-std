#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted diagnostic of the stock exporter's normal-mode actual select MIR.

This reads one immutable, manifest-checked S6v2 projected fixture. It exports
and decodes MIR only; no verifier, refiner, patched console, or proof runs here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import urllib.error
import urllib.request
import zipfile


REPO = "Tiramisu-Cake/verify-rust-std"
RUN_ID = 37645561507
SOURCE_SHA = "85ec1711700ff85c899b18b7e021f076aeddb8e6"
ARTIFACT_ID = 11493408570
ARTIFACT_NAME = "smallsort-select-compact-evidence-37645561507-1"
COMPACT_SHA = "b160edcd347c02ffafcd94ac0258e805d488bed10a500b64cd3e632b5d8d49ae"
EXPORTER_SHA = "2b8ebb5373d0bdd82cc163f5a298a4291b89dcdb8630a01bf74149987f2d5e0c"
SCHEMA_SHA = "7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9"
FIXTURE_PREFIX = ("current/select-pointer/actual-drop-integration/"
                  "actual_select_pointer_drop_projection/")
SOURCE_HASHES = {
    "verified/lib.rs": "8a82b1807350193c0511ea723f2d4080d3cd49f2aa0cdab4f7945c74519fff67",
    "original/lib.rs": "37e5cae44a581124a3272667aa5cb932d6f8a595b779117ef6481d54509a465b",
    "fixture.json": "a35b2c75713365257c74a0bdac14b0e64c282b5a5a8b2a0820b4b5ec0babe699",
}
GHOSTS = (
    "//@ std::mem::open_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);",
    "//@ std::mem::open_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);",
    "//@ if (condition) { } else { }",
    "//@ std::mem::close_MaybeUninit::<*Element>(true_ptr as *std::mem::MaybeUninit<*Element>);",
    "//@ std::mem::close_MaybeUninit::<*Element>(false_ptr as *std::mem::MaybeUninit<*Element>);",
)


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def api_json(path: str, token: str) -> dict:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/{path}",
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {token}",
                 "X-GitHub-Api-Version": "2022-11-28"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def download_compact(token: str) -> tuple[bytes, dict]:
    run = api_json(f"actions/runs/{RUN_ID}", token)
    artifact = api_json(f"actions/artifacts/{ARTIFACT_ID}", token)
    require(run.get("id") == RUN_ID and run.get("head_sha") == SOURCE_SHA and
            run.get("head_repository", {}).get("full_name") == REPO and
            run.get("run_attempt") == 1 and
            run.get("status") == "completed",
            "source run identity is not pinned S6v2 completion")
    require(artifact.get("id") == ARTIFACT_ID and
            artifact.get("name") == ARTIFACT_NAME and
            artifact.get("expired") is False and
            artifact.get("workflow_run", {}).get("id") == RUN_ID,
            "source compact artifact identity differs")
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/artifacts/{ARTIFACT_ID}/zip",
        headers={"Accept": "application/vnd.github+json",
                 "Authorization": f"Bearer {token}",
                 "X-GitHub-Api-Version": "2022-11-28"},
    )
    try:
        urllib.request.build_opener(NoRedirect).open(request, timeout=45)
    except urllib.error.HTTPError as error:
        require(error.code == 302 and bool(error.headers.get("Location")),
                "artifact download did not return a signed redirect")
        location = error.headers["Location"]
    else:
        raise ValueError("artifact download unexpectedly returned a body")
    with urllib.request.urlopen(location, timeout=90) as response:
        outer = response.read(16 * 1024 * 1024 + 1)
    require(len(outer) <= 16 * 1024 * 1024, "artifact ZIP exceeds diagnostic limit")
    from io import BytesIO
    with zipfile.ZipFile(BytesIO(outer)) as z:
        require(z.namelist() == ["sort4-select-compact-evidence.zip"],
                "artifact ZIP has an unexpected member inventory")
        compact = z.read("sort4-select-compact-evidence.zip")
    require(sha(compact) == COMPACT_SHA, "source compact ZIP digest differs")
    return compact, {"run_id": RUN_ID, "source_sha": SOURCE_SHA,
                     "artifact_id": ARTIFACT_ID, "artifact_name": ARTIFACT_NAME,
                     "artifact_size": artifact.get("size_in_bytes"),
                     "outer_zip_sha256": sha(outer),
                     "compact_zip_sha256": COMPACT_SHA}


def authenticate_fixture(compact: bytes, case: Path) -> dict:
    require(all(len(value) == 64 and re.fullmatch(r"[0-9a-f]{64}", value)
                for value in SOURCE_HASHES.values()),
            "fixture source digest pin is malformed")
    from io import BytesIO
    with zipfile.ZipFile(BytesIO(compact)) as z:
        manifest = json.loads(z.read("COMPACT-EVIDENCE-MANIFEST.json"))
        current = manifest["current_source"]
        require(current.get("run_id") == str(RUN_ID) and
                current.get("head_sha") == SOURCE_SHA and
                current.get("repository") == REPO and
                current.get("run_attempt") == "1" and
                current.get("compact_artifact_name") == ARTIFACT_NAME,
                "compact manifest source identity differs")
        names = set(z.namelist())
        require(len(names) == len(z.namelist()), "duplicate compact ZIP entry")
        included = [entry for entry in manifest["entries"]
                    if entry.get("included") is True]
        require({entry["compact_entry"] for entry in included} ==
                names - {"COMPACT-EVIDENCE-MANIFEST.json"} and
                len(included) == len(names) - 1,
                "compact manifest member inventory differs")
        by_name = {}
        for entry in included:
            name = entry["compact_entry"]
            parts = PurePosixPath(name)
            require(not parts.is_absolute() and ".." not in parts.parts and
                    (name.startswith("current/") or name.startswith("o4/")),
                    "unsafe compact member name")
            data = z.read(name)
            require(sha(data) == entry["sha256"] and
                    len(data) == entry["file_size"] and
                    f"{z.getinfo(name).CRC:08x}" == entry["crc32"],
                    f"compact manifest member digest differs: {name}")
            by_name[name] = data
        fixture = {}
        for rel, expected in SOURCE_HASHES.items():
            data = by_name[FIXTURE_PREFIX + rel]
            require(sha(data) == expected, f"projected {rel} differs from S6v2 pin")
            path = case / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            if rel == "fixture.json":
                fixture = json.loads(data)
        require(fixture.get("variant") == "actual_select_pointer_drop_projection" and
                fixture.get("tool_profile") ==
                "experimental-source-linked-select-pointer-drop-v2" and
                fixture.get("final_verified_sha256") == SOURCE_HASHES["verified/lib.rs"] and
                fixture.get("final_original_sha256") == SOURCE_HASHES["original/lib.rs"] and
                fixture.get("projection_ghosts_exact") is True and
                fixture.get("verified_ghost_strip_exact") is True,
                "archived projected fixture metadata differs")
        source = (case / "verified/lib.rs").read_text()
        require(tuple(line.strip() for line in source.splitlines()
                      if line.strip().startswith("//@")) == GHOSTS,
                "projected source does not contain exactly five pinned ghosts")
        summaries = {}
        for name in ("pointer-drop-matrix", "matrix", "intrinsic-matrix",
                     "constructor-regressions"):
            rel = f"current/select-pointer/{name}/summary.json"
            data = by_name[rel]
            summaries[name] = {"sha256": sha(data)}
            parsed = json.loads(data)
            if name != "constructor-regressions":
                require(parsed.get("accepted_component") is True and
                        parsed.get("tool_profile") ==
                        "experimental-source-linked-select-pointer-drop-v2",
                        f"archived {name} was not accepted in S6v2")
                summaries[name]["accepted_component"] = True
        return {"manifest_sha256": sha(z.read("COMPACT-EVIDENCE-MANIFEST.json")),
                "fixture_source_sha256": SOURCE_HASHES,
                "prior_s6v2_summaries": summaries}


def source_hashes(case: Path) -> dict[str, str]:
    return {rel: sha((case / rel).read_bytes()) for rel in SOURCE_HASHES}


def command_result(command: list[str], case: Path, stdout: Path,
                   stderr: Path, env: dict[str, str]) -> dict:
    with stdout.open("wb") as out, stderr.open("wb") as err:
        try:
            result = subprocess.run(command, cwd=case, env=env, stdout=out,
                                    stderr=err, timeout=150, check=False)
            status = result.returncode
        except subprocess.TimeoutExpired:
            status = 124
    return {"argv": command, "exit_code": status,
            "stdout_sha256": sha(stdout.read_bytes()),
            "stderr_sha256": sha(stderr.read_bytes())}


def summarize_mir(decoded: str) -> dict:
    marker = 'defPath = "select_unpredictable",'
    require(decoded.count(marker) == 1, "normal MIR actual body is not unique")
    body = decoded.split(marker, 1)[1].split("\n    ( defKind = ", 1)[0]
    require(body.count("localDecls = [") == 1 and
            body.count("basicBlocks = [") == 1 and
            body.count("ghostStmts = [") == 1,
            "normal MIR actual body sections differ")
    locals_text = body.split("localDecls = [", 1)[1].split("basicBlocks = [", 1)[0]
    blocks_text = body.split("basicBlocks = [", 1)[1].split("ghostStmts = [", 1)[0]
    ghost_text = (body.split("ghostStmts = [", 1)[1]
                  .split("\n      unsafety =", 1)[0])
    local_names = re.findall(r'^        \( mutability = .*?\n          id = \(name = "([^"]+)"\)',
                             locals_text, re.MULTILINE)
    block_ids = [int(item) for item in re.findall(
        r'^        \( id = \(index = (\d+)\)', blocks_text, re.MULTILINE)]
    entries = list(re.finditer(r'^        \( raw = "([^"]+)"', ghost_text,
                               re.MULTILINE))
    ghosts = []
    for index, entry in enumerate(entries):
        section = ghost_text[entry.start():
                             entries[index + 1].start() if index + 1 < len(entries)
                             else len(ghost_text)]
        coords = [(int(a), int(b)) for a, b in re.findall(
            r'line = (\d+),\s*col = \(pos = (\d+)\)', section)]
        explicit = re.search(
            r'startLine = (\d+),\s*startCol = (\d+),\s*'
            r'endLine = (\d+),\s*endCol = (\d+)', section)
        require(len(coords) == 2 and explicit is not None,
                f"normal MIR ghost {index} has ambiguous coordinates")
        ghosts.append({"raw": entry.group(1), "regular_lo": coords[0],
                       "regular_hi": coords[1],
                       "explicit_start": [int(explicit[1]), int(explicit[2])],
                       "explicit_end": [int(explicit[3]), int(explicit[4])]})
    require([g["raw"] for g in ghosts] == list(GHOSTS),
            "normal MIR five raw ghosts differ from source")
    call_names = re.findall(r'name = "((?:std|core)::[^"\n]+)"', blocks_text)
    call_names = [name for name in call_names if
                  name in {"std::mem::MaybeUninit::<T>::new",
                           "std::mem::MaybeUninit::<T>::as_mut_ptr",
                           "std::intrinsics::select_unpredictable",
                           "std::ptr::mut_ptr::<impl *mut T>::drop_in_place",
                           "std::mem::MaybeUninit::<T>::assume_init"}]
    return {"actual_body_unique": True,
            "local_count": len(local_names), "locals": local_names,
            "basic_block_count": len(block_ids), "basic_block_ids": block_ids,
            "selected_callees": call_names, "ghosts": ghosts,
            "full_typed_mir_retained": "normal-mir.txt"}


def main() -> int:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "normal MIR diagnostic requires GitHub-hosted Linux")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=False)
    case = evidence / "projected-fixture"
    case.mkdir()
    token = os.environ.get("GH_TOKEN", "")
    require(bool(token), "GitHub artifact read token missing")
    require(sha((args.stock_home / "bin/vf-rust-mir-exporter").read_bytes()) ==
            EXPORTER_SHA, "stock exporter byte hash differs")
    require(sha(args.schema.read_bytes()) == SCHEMA_SHA,
            "frozen Cap'n Proto schema hash differs")
    compact, artifact = download_compact(token)
    provenance = authenticate_fixture(compact, case)
    before = source_hashes(case)
    require(before == SOURCE_HASHES, "projected fixture changed after extraction")
    env = os.environ.copy()
    env["PATH"] = str(args.stock_home / "bin") + os.pathsep + env.get("PATH", "")
    env["LD_LIBRARY_PATH"] = (str(Path(args.compiler_sysroot) / "lib") + os.pathsep +
                              str(args.stock_home / "bin") + os.pathsep +
                              env.get("LD_LIBRARY_PATH", ""))
    env["RUST_LOG"] = "trace"
    command = [str(args.stock_home / "bin/vf-rust-mir-exporter"),
               "verified/lib.rs", f"--sysroot={args.compiler_sysroot}",
               "--edition", "2021"]
    # Pinned exporter lib.rs::run_compiler appends these three defaults itself.
    effective_compiler_argv = command + [
        "-Coverflow_checks=off", "--crate-type=lib", "--error-format=json"]
    require(not any("preprocess-readonly" in item for item in command),
            "normal exporter command accidentally selects readonly mode")
    (evidence / "normal-command.json").write_text(
        json.dumps({"mode": "normal", "exporter_argv": command,
                    "expected_effective_compiler_argv": effective_compiler_argv,
                    "working_directory": "projected-fixture",
                    "stock_exporter_sha256": EXPORTER_SHA,
                    "schema_sha256": SCHEMA_SHA}, indent=2) + "\n")
    exporter = command_result(command, case, evidence / "normal-mir.bin",
                              evidence / "normal-exporter.log", env)
    compiler_args_match = re.search(
        r'Calling the Rust Compiler with args: (\[[^\n]+\])',
        (evidence / "normal-exporter.log").read_text(errors="replace"))
    observed_args = (json.loads(compiler_args_match.group(1))
                     if compiler_args_match else None)
    exporter["effective_compiler_argv_observed"] = observed_args
    exporter["effective_compiler_argv_exact"] = (
        observed_args == effective_compiler_argv)
    after_export = source_hashes(case)
    decode = None
    after_decode = None
    graph = None
    graph_error = None
    if exporter["exit_code"] == 0:
        with (evidence / "normal-mir.bin").open("rb") as mir_bin, \
             (evidence / "normal-mir.txt").open("wb") as mir_text, \
             (evidence / "capnp-decode.log").open("wb") as err:
            proc = subprocess.run(
                ["capnp", "decode", str(args.schema.resolve()), "VfMir"],
                stdin=mir_bin, stdout=mir_text, stderr=err, cwd=case,
                env=env, timeout=150, check=False)
        decode = {"argv": ["capnp", "decode", str(args.schema.resolve()), "VfMir"],
                  "exit_code": proc.returncode,
                  "stdout_sha256": sha((evidence / "normal-mir.txt").read_bytes()),
                  "stderr_sha256": sha((evidence / "capnp-decode.log").read_bytes())}
        after_decode = source_hashes(case)
        if proc.returncode == 0:
            try:
                graph = summarize_mir((evidence / "normal-mir.txt").read_text())
            except ValueError as error:
                graph_error = str(error)
    integrity = {"before": before, "after_export": after_export,
                 "after_decode": after_decode,
                 "unchanged_after_export": before == after_export,
                 "unchanged_after_decode": before == after_decode}
    (evidence / "source-integrity.json").write_text(
        json.dumps(integrity, indent=2, sort_keys=True) + "\n")
    accepted = (exporter["exit_code"] == 0 and
                exporter["effective_compiler_argv_exact"] and
                decode is not None and
                decode["exit_code"] == 0 and
                integrity["unchanged_after_export"] and
                integrity["unchanged_after_decode"] and graph is not None)
    classification = ("DIAGNOSTIC_EXPORT_DECODED" if accepted else
                      "DIAGNOSTIC_COMPILER_ARGS_UNCONFIRMED"
                      if not exporter["effective_compiler_argv_exact"] else
                      "DIAGNOSTIC_EXPORT_DECODED_GRAPH_UNPARSED"
                      if decode is not None and decode["exit_code"] == 0 and
                         integrity["unchanged_after_decode"] else
                      "DIAGNOSTIC_EXPORT_OR_DECODE_FAILED")
    summary = {"classification": classification,
               "is_component_acceptance": False,
               "is_proof": False,
               "source": artifact, "authenticated_fixture": provenance,
               "tool": {"stock_exporter_sha256": EXPORTER_SHA,
                        "schema_sha256": SCHEMA_SHA,
                        "compiler_sysroot": args.compiler_sysroot},
               "exporter": exporter, "decode": decode,
               "source_integrity": integrity,
               "normal_actual_mir": graph,
               "normal_graph_parse_error": graph_error}
    (evidence / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": summary["classification"],
                      "local_count": graph["local_count"] if graph else None,
                      "basic_block_count": graph["basic_block_count"] if graph else None,
                      "ghost_count": len(graph["ghosts"]) if graph else None},
                     sort_keys=True))
    return 0 if accepted else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        if "--evidence" in sys.argv:
            index = sys.argv.index("--evidence") + 1
            if index < len(sys.argv):
                try:
                    failure_dir = Path(sys.argv[index]).resolve()
                    failure_dir.mkdir(parents=True, exist_ok=True)
                    failure_summary = failure_dir / "summary.json"
                    if not failure_summary.exists():
                        failure_summary.write_text(json.dumps({
                            "classification": "DIAGNOSTIC_SETUP_INCONCLUSIVE",
                            "is_proof": False,
                            "is_component_acceptance": False,
                            "error": f"{type(exc).__name__}: {exc}",
                            "source_run_id": RUN_ID,
                            "source_sha": SOURCE_SHA,
                            "source_artifact_id": ARTIFACT_ID,
                            "source_compact_sha256": COMPACT_SHA,
                            "stock_exporter_sha256": EXPORTER_SHA,
                            "schema_sha256": SCHEMA_SHA,
                        }, indent=2, sort_keys=True) + "\n")
                except OSError:
                    pass
        print(f"normal MIR capture setup error: {type(exc).__name__}: {exc}",
              file=sys.stderr)
        raise
