#!/usr/bin/env python3
"""Cloud-only C4/selector integration. Importing this file does no proof work."""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import lzma
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

HERE = Path("research/challenge-8/cloud-build/verifast-c4-select-integration")
TOOL_HEAD = "f76012fb518703b1d98e243ac4f487f16877cfcb"
SCHEMA = "src/rust_frontend/vf_mir/vf_mir.capnp"
TRANSLATOR = "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
CONTROLS = ("c4-normal-missing-close", "c4-unwind-missing-close",
            "c4-normal-omit-join", "c4-unwind-omit-join", "normal-false-post",
            "c1-unwind-false-assert", "c2-unwind-false-assert",
            "c3-unwind-false-assert", "c4-unwind-false-assert")
HELPERS = ("recover_pair", "join_four_owned_cells", "selected_four_limits",
           "split_selected_four", "join_selected_four")
PARENT_PAIRS = (
    ("SORT4_WRAPPER_REBASE_REPO_ROOT", "SORT4_WRAPPER_REBASE_ADMISSION"),
    ("SORT4_WRAPPER_INPUT_RELATION_REPO_ROOT", "SORT4_WRAPPER_INPUT_RELATION_ADMISSION"),
    ("SORT4_R3_GHOST_SCOPE_TEST_REPO_ROOT", "SORT4_R3_GHOST_SCOPE_TEST"),
    ("SORT4_R3_RECEIVER_TEST_REPO_ROOT", "SORT4_R3_RECEIVER_TEST"),
    ("SORT4_R3_GHOST_COLUMN_TEST_REPO_ROOT", "SORT4_R3_GHOST_COLUMN_TEST"),
    ("SORT4_R3_COLUMN_NESTED_TEST_REPO_ROOT", "SORT4_R3_COLUMN_NESTED_TEST"),
    ("SORT4_R3_FRAME_TEST_REPO_ROOT", "SORT4_R3_FRAME_TEST"),
    ("SORT4_R3_FRAME_SHADOW_TEST_REPO_ROOT", "SORT4_R3_FRAME_SHADOW_TEST"),
    ("SORT4_R3_CLEANUP_PROJECTION_TEST_REPO_ROOT", "SORT4_R3_CLEANUP_PROJECTION_TEST"),
)
OWNER_GATES = ("SORT4_ACTUAL_OWNER_REPO_ROOT", "SORT4_ACTUAL_OWNER_ADMISSION",
               "SORT4_ACTUAL_OWNER_NINE_ADMISSION", "SORT4_ACTUAL_NESTED_H2_REPO_ROOT",
               "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT", "SORT4_A1_NINE_REPO_ROOT")
BASE_GATES = ("SORT4_MAYBEUNINIT_REPO_ROOT", "SORT4_SELECT_INTRINSIC_REPO_ROOT",
              "SORT4_POINTER_DROP_REPO_ROOT", "SORT4_GUARD_REPO_ROOT",
              "SORT4_GUARD_TEMPLATE_REPO_ROOT", "SORT4_A1_LINK_REPO_ROOT")
ERROR = re.compile(r"(?m)^.*: error: .*|^Error:.*$|^Fatal error:.*$")


def need(value, message):
    if not value:
        raise RuntimeError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def finish(a, result):
    result.setdefault("accepted", False)
    result.setdefault("verification_accepted", False)
    result.setdefault("diagnostic_complete", False)
    output = a.evidence / "result.json"
    record(output, result)
    record(a.evidence.parents[1] / "proof-audit.json", {
        "classification": result["classification"], "accepted": False,
        "verification_accepted": False,
        "diagnostic_complete": result["diagnostic_complete"],
        "result_path": "cases/integration/result.json",
        "result_sha256": sha(output),
        "intended_negative_credit": False})


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"missing module {path}")
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    parent = str(path.parent)
    sys.path.insert(0, parent)
    try:
        spec.loader.exec_module(value)
    finally:
        sys.path.remove(parent)
    return value


def manifest(a):
    data = json.loads(a.manifest.read_text())
    need(data.get("classification") == "EXPERIMENTAL_C4_SELECT_INTEGRATION" and
         data.get("accepted") is False and
         data.get("tool_base_sha") == TOOL_HEAD,
         "integration manifest identity differs")
    for label in ("tool_c4", "selector_integration", "composition"):
        path = a.proof_root / HERE / (label.replace("_", "-") + ".patch")
        need(path.is_file() and sha(path) == data[label + "_patch_sha256"],
             label + " patch pin differs")
    return data


def stage(a, name, command, cwd, env=None, cap=180, stdin=None, stdout=None):
    seconds = min(cap, a.deadline_epoch - int(time.time()) - 25)
    need(seconds > 0, "deadline before " + name)
    log = a.evidence / (name + ".log")
    resources = a.evidence / (name + "-resources.txt")
    clean = os.environ.copy()
    for key in (*OWNER_GATES, *BASE_GATES,
                "SORT4_SELECTOR_REACHABLE_UNWIND_MUTANT",
                "SORT4_C4_FIRST_SELECT_ADMISSION_MUTANT",
                "SORT4_C4_FIRST_SELECT_CONTROL", "SORT4_CURRENT_BOUND_AST_EXPORT",
                *(key for pair in PARENT_PAIRS for key in pair)):
        clean.pop(key, None)
    with log.open("wb") as stream:
        inp = stdin.open("rb") if stdin else subprocess.DEVNULL
        out = stdout.open("wb") if stdout else stream
        try:
            code = subprocess.run(["/usr/bin/time", "-v", "-o", str(resources),
                "timeout", "--signal=TERM", "--kill-after=10s", str(seconds) + "s", *command],
                cwd=cwd, env={**clean, **(env or {}), "PWD": str(cwd)},
                stdin=inp, stdout=out, stderr=stream, check=False).returncode
        finally:
            if stdin:
                inp.close()
            if stdout:
                out.close()
    result = {"exit": code, "argv": command, "cwd": str(cwd),
              "seconds": seconds, "log_sha256": sha(log),
              "stdout_sha256": sha(stdout) if stdout and stdout.exists() else None,
              "proof_credit": False}
    record(a.evidence / (name + "-stage.json"), result)
    return result, log.read_text(errors="replace")


def restore_modules(a, data):
    pack_path = a.proof_root / HERE / "source-modules.json"
    need(sha(pack_path) == data["source_modules_pack_sha256"], "source module pack pin differs")
    pack = json.loads(pack_path.read_text())
    need(pack["schema"] == "canonical-source-modules-v1" and
         pack["source_commit"] == data["source_modules_provenance_commit"] and
         len(pack["files"]) == data["source_modules_count"], "source pack provenance differs")
    def restore_object(kind, oid, blob):
        expected = hashlib.sha1((kind + " " + str(len(blob)) + "\0").encode() + blob).hexdigest()
        need(expected == oid, "canonical " + kind + " object identity differs")
        actual = subprocess.check_output(["git", "-C", str(a.proof_root),
            "hash-object", "-w", "-t", kind, "--stdin"], input=blob).decode().strip()
        need(actual == oid, "restored object identity differs")
    for oid, encoded in pack["trees"].items():
        restore_object("tree", oid, base64.b64decode(encoded, validate=True))
    rows = []
    seen = set()
    for row in pack["files"]:
        rel = Path(row["path"])
        need(not rel.is_absolute() and ".." not in rel.parts and
             rel.as_posix().startswith("research/challenge-8/") and
             rel.suffix == ".py" and row["path"] not in seen, "invalid source module path")
        seen.add(row["path"])
        blob = row["text"].encode()
        need(hashlib.sha256(blob).hexdigest() == row["sha256"], "canonical module SHA256 differs")
        restore_object("blob", row["oid"], blob)
        committed = subprocess.check_output(["git", "-C", str(a.proof_root),
            "rev-parse", "HEAD:" + row["path"]], text=True).strip()
        need(committed == row["oid"], "module differs from pinned proof commit")
        mode = subprocess.check_output(["git", "-C", str(a.proof_root),
            "ls-tree", "HEAD", "--", row["path"]], text=True).split()[0]
        need(mode == row["mode"] and mode in ("100644", "100755"), "module mode differs")
        target = a.proof_root / rel
        need(not target.is_symlink() and all(not parent.is_symlink() for parent in target.parents),
             "source module path traverses symlink")
        need(not target.exists() or target.read_bytes() == blob, "existing canonical module differs")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        target.chmod(0o755 if mode == "100755" else 0o644)
        need(sha(target) == row["sha256"], "materialized module bytes differ")
        rows.append({key: row[key] for key in ("path", "oid", "sha256")})
    record(a.evidence / "restored-source-modules.json", {"pack_sha256": sha(pack_path),
        "modules": rows, "content_changed": False, "proof_credit": False})


def materialize_delivered_inputs(a):
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build", "Cloud-only input materialization")
    data = json.loads(a.manifest.read_text())
    allowed = {"tool-c4.patch": "tool_c4_patch_sha256",
               "source-modules.json": "source_modules_pack_sha256"}
    rows = data["compressed_delivery"]
    need(len(rows) == 2 and {r["raw_path"] for r in rows} == set(allowed), "exact two delivery inputs required")
    observed = []
    for row in rows:
        name = row["raw_path"]
        need(row["path"] == name + ".xz", "delivery compressed path differs")
        compressed = a.proof_root / HERE / row["path"]
        target = a.proof_root / HERE / name
        need(not target.exists() and not target.is_symlink() and
             all(not p.is_symlink() for p in target.parents), "delivery target is not unused/safe")
        need(sha(compressed) == row["compressed_sha256"], "compressed input SHA256 differs")
        size = row["raw_size"]
        need(type(size) is int and 0 < size <= 1048576, "delivery raw size outside exact lane bound")
        decoder = lzma.LZMADecompressor(format=lzma.FORMAT_XZ)
        raw = decoder.decompress(compressed.read_bytes(), max_length=size + 1)
        need(decoder.eof and not decoder.unused_data and len(raw) == size, "delivery stream/length differs")
        need(hashlib.sha256(raw).hexdigest() == row["raw_sha256"] == data[allowed[name]], "delivery raw SHA256 differs")
        relative = str(HERE / name)
        expected = subprocess.check_output(["git", "-C", str(a.proof_root), "rev-parse", "HEAD:" + relative], text=True).strip()
        mode = subprocess.check_output(["git", "-C", str(a.proof_root), "ls-tree", "HEAD", "--", relative], text=True).split()[0]
        need(mode == "100644", "delivery raw mode differs")
        actual = hashlib.sha1(("blob " + str(len(raw)) + "\0").encode() + raw).hexdigest()
        need(actual == expected, "delivery raw Git blob differs")
        target.write_bytes(raw)
        target.chmod(0o644)
        written = subprocess.check_output(["git", "-C", str(a.proof_root), "hash-object", "-w", str(target)], text=True).strip()
        need(written == expected and sha(target) == row["raw_sha256"], "materialized input identity differs")
        observed.append({**row, "git_blob": expected, "mode": mode})
    record(a.evidence / "compressed-delivery.json", {"rows": observed, "proof_credit": False})


def preflight(a):
    materialize_delivered_inputs(a)
    data = manifest(a)
    restore_modules(a, data)
    recipe = module(a.cloud_dir / "o26-recipe.py", "integration_provider_overlay")
    recipe.overlay(a.proof_root, a.cloud_dir / "provider.py",
                   a.evidence / "provider-overlay.json")
    record(a.evidence / "manifest-pin.json", {"manifest_sha256": sha(a.manifest),
        "proof_sha": subprocess.check_output(["git", "-C", str(a.proof_root),
        "rev-parse", "HEAD"], text=True).strip(), "patches":
        {key: data[key + "_patch_sha256"] for key in ("tool_c4", "selector_integration", "composition")}})


def apply(a):
    data = manifest(a)
    need(subprocess.check_output(["git", "-C", str(a.tool_home), "rev-parse", "HEAD"],
        text=True).strip() == TOOL_HEAD, "stock tool checkout differs")
    for label in ("tool_c4", "selector_integration", "composition"):
        path = a.proof_root / HERE / (label.replace("_", "-") + ".patch")
        for operation, args in (("check", ["--check"]), ("apply", [])):
            completed = subprocess.run(["git", "-C", str(a.tool_home), "apply", *args,
                str(path)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, check=False)
            (a.evidence / f"{label}-{operation}.log").write_text(completed.stdout)
            need(completed.returncode == 0, f"{label} {operation} failed")
    record(a.evidence / "applied-tool.json", {"patches":
        {key: data[key + "_patch_sha256"] for key in ("tool_c4", "selector_integration", "composition")},
        "changed_files": subprocess.check_output(["git", "-C", str(a.tool_home),
            "diff", "--name-only"], text=True).splitlines()})


def pin(a):
    data = manifest(a)
    expected = data["effective_hashes"]
    required = {TRANSLATOR, SCHEMA, "bin/rust/std/lib.rsspec", "src/verifast.ml",
                "src/rust_frontend/vf_mir_translator/rust_parser.ml"}
    need(isinstance(expected, dict) and required <= set(expected),
         "effective tool/spec hashes incomplete")
    historical = json.loads((a.proof_root /
        "research/challenge-8/overnight-linkage/O26-PROFILE-MANIFEST.json").read_text())
    for name in ("bin/vf-rust-mir-exporter", "bin/refinement-checker"):
        need(sha(a.tool_home / name) == historical["hosted_profile_hashes"][name],
             "stock exporter/refiner hash differs")
    actual = {name: sha(a.tool_home / name) for name in expected}
    actual["bin/verifast"] = sha(a.tool_home / "bin/verifast")
    expected_with_console = {"bin/verifast": actual["bin/verifast"], **expected}
    record(a.evidence / "effective-hashes.json", {"expected": expected, "actual": actual,
        "exact": actual == expected_with_console})
    need(actual == expected_with_console, "effective tool/spec hash mismatch")
    seal = a.evidence / "effective-console-sha256.txt"
    if seal.is_file():
        need(seal.read_text().strip() == actual["bin/verifast"],
             "console binary changed after integration pin")
    else:
        seal.write_text(actual["bin/verifast"] + "\n")


def prepare(a):
    first = module(a.proof_root / "research/challenge-8/overnight-callback/prepare-actual-sort4-first-call.py", "integration_first")
    c2 = module(a.cloud_dir / "sort4-native-entry-c1/c2_discovery.py", "integration_c2")
    c3 = module(a.cloud_dir / "sort4-c3-bound-prefix/driver.py", "integration_c3")
    c4 = module(a.cloud_dir / "sort4-c4-bound-prefix/driver.py", "integration_c4")
    shadow = module(a.proof_root / "research/challenge-8/overnight-assume-actual/prepare-wrapper-input-relation-frame-shadow.py", "integration_shadow")
    c1case = a.evidence / "c1-fixture"
    first_record = first.prepare(a.proof_root, c1case)
    c2case = a.evidence / "c2-discovery-fixture"
    shutil.copytree(c1case, c2case, symlinks=True)
    pin_path = a.proof_root / "research/challenge-8/cloud-build/sort4-native-entry-c1/C2-SOURCE-PIN.json"
    pin_data = json.loads(pin_path.read_text())
    draft_path = a.proof_root / "research/challenge-8/cloud-build/sort4-native-entry-c1/C2-ANNOTATION-DRAFT.rs"
    verified = c2case / "verified/lib.rs"
    original = c2case / "original/lib.rs"
    annotated, c2_record = c2.prepare_c2_bytes(verified.read_bytes(), original.read_bytes(),
        draft_path.read_bytes(), pin_data)
    verified.write_bytes(annotated)
    c3case, c3_record = c3.prepare(a)
    c4case, c4_record = c4.prepare(a)
    shadow_root = a.evidence / "selector-capture"
    shadow_record = shadow.write_case(a.proof_root, shadow_root)
    selector_case = shadow_root / shadow.CASE_NAME
    record(a.evidence / "source-preparation.json", {"first": first_record,
        "c2": c2_record, "c3": c3_record, "c4": c4_record,
        "selector": shadow_record, "selector_case": str(selector_case)})
    return c4case, selector_case, shadow_record


def source_prepare(a):
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") in ("verifast-c4-select-integration",
                                     "verifast-native-zst-integration",
                                     "verifast-slice-binding-integration") and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud integration lane required")
    data = manifest(a)
    c4case, selector_case, source = prepare(a)
    admitted_source(selector_case / "verified/lib.rs", data["selector_source_sha256"])
    admitted_source(c4case / "verified/lib.rs", data["c4_source_sha256"])
    admission = source_admission_mutants(a, c4case, data["c4_source_sha256"])
    regression_mod = module(a.cloud_dir / "verifast-c4-select-integration/regressions.py",
                            "integration_source_prepare_regressions")
    fixture_report = regression_mod.prepare_source_fixtures(
        a, a.evidence / "regression-fixtures")
    # Materialize the source half of composition now. The exported selector AST
    # is deliberately left for the later verified producer stage.
    composition = a.evidence / "composition-fixture"
    shutil.copytree(c4case, composition, symlinks=True)
    (composition / "selector").mkdir()
    shutil.copyfile(selector_case / "verified/lib.rs", composition / "selector/lib.rs")
    record(a.evidence / "source-preparation.json", {
        "classification": "CLOUD_SOURCE_PREPARATION_ONLY", "proof_credit": False,
        "selector_source_sha256": sha(selector_case / "verified/lib.rs"),
        "c4_source_sha256": sha(c4case / "verified/lib.rs"),
        "admission_mutants": admission,
        "regression_fixtures": fixture_report,
        "composition_source_ready": True,
        "composition_ast": "NOT_PREPARABLE_BEFORE_VERIFIED_SELECTOR_RUN"})


def capture(a, case: Path, label: str, names=None):
    stages = {}
    inventories = {}
    for mode, extra in (("normal", []),
                        ("readonly", (["--crate-type", "lib"] if names else []) +
                         ["--vf-rust-mir-exporter:preprocess-readonly"])):
        binary = a.evidence / f"{label}-{mode}-mir.bin"
        decoded = a.evidence / f"{label}-{mode}-mir.txt"
        stages[mode + "-export"], _ = stage(a, f"{label}-{mode}-export",
            [str(a.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
             "--sysroot=" + str(a.compiler_sysroot), "--edition", "2021", *extra],
            case, stdout=binary)
        need(stages[mode + "-export"]["exit"] == 0, label + " MIR export failed")
        stages[mode + "-decode"], _ = stage(a, f"{label}-{mode}-decode",
            ["capnp", "decode", str(a.tool_home / SCHEMA), "VfMir"], case,
            stdin=binary, stdout=decoded)
        need(stages[mode + "-decode"]["exit"] == 0, label + " MIR decode failed")
        if names:
            content = decoded.read_text()
            order = [content.find('defPath = "' + name + '"') for name in names]
            need(all(value >= 0 for value in order) and order == sorted(order),
                 label + " nine-body decoded MIR order differs")
            capture_mod = module(a.proof_root / "research/challenge-8/overnight-helper/prepare-assume-init-2610.py",
                                 "integration_nine_capture_" + mode)
            rows = []
            for index, name in enumerate(names):
                actual_name, body = capture_mod.complete_function_record(content, name)
                need(actual_name == name and bool(body), label + " body record mismatch")
                target = a.evidence / f"{label}-{mode}-body-{index}-full-mir.txt"
                target.write_text(body)
                rows.append(sha(target))
            inventories[mode] = {"whole_decoded_mir_sha256": sha(decoded),
                                 "body_sha256": rows}
        else:
            capture_mod = module(a.proof_root / "research/challenge-8/overnight-sort4/capture.py",
                                 "integration_sort4_capture_" + mode)
            inventories[mode] = capture_mod.graph_inventory(decoded, a.evidence, label + "-" + mode)
    stages["refinement"], _ = stage(a, label + "-refinement",
        [str(a.tool_home / "bin/refinement-checker"), "--rustc-args", "--edition 2021",
         "original/lib.rs", "verified/lib.rs"], case)
    need(stages["refinement"]["exit"] == 0, label + " source refinement failed")
    record(a.evidence / (label + "-capture.json"), {"stages": stages,
        "verified_sha256": sha(case / "verified/lib.rs"),
        "original_sha256": sha(case / "original/lib.rs"),
        "inventories": inventories, "proof_credit": False})
    return inventories


def selector_env(a):
    env = {"SORT4_ACTUAL_C4_FIRST_SELECT_TEST": "0", "SORT4_ACTUAL_AST_SCOPE_TEST": "0", "SORT4_ACTUAL_C1_PREFIX_TEST": "0",
           "SORT4_ACTUAL_C2_DISCOVERY_TEST": "0", "SORT4_ACTUAL_C2_BOUND_PREFIX_TEST": "0",
           "SORT4_ACTUAL_C3_CAPTURE_TEST": "0", "SORT4_ACTUAL_C3_BOUND_PREFIX_TEST": "0",
           "SORT4_ACTUAL_C4_CAPTURE_TEST": "0", "SORT4_ACTUAL_C4_BOUND_PREFIX_TEST": "0",
           "SORT4_STRICT_LFT_CUT": "0", "SORT4_C4_BOUND_CONTROL": "none",
           "SORT4_C1_PREFIX_CONTROL": "none", "SORT4_C1_OUTPUT_EQ": "0",
           "SORT4_C2_BOUND_CONTROL": "none", "SORT4_C3_BOUND_CONTROL": "none",
           "SORT4_C3_CAPTURE_SOURCE_SHA256": "", "SORT4_C4_CAPTURE_SOURCE_SHA256": ""}
    for root, flag in PARENT_PAIRS:
        env[root] = str(a.proof_root)
        env[flag] = "1"
    # The actual nine-body selector has its own nested/A1-nine admission.
    # Generic-guard/template and A1-link certificates describe different units;
    # retain them in the process sanitizer but do not opt this unit into them.
    for key in BASE_GATES[:3]:
        env[key] = str(a.proof_root)
    env["SORT4_SELECT_PROFILE"] = "experimental-s6-26.10-v1"
    env.update({"SORT4_ACTUAL_OWNER_REPO_ROOT": str(a.proof_root),
                "SORT4_ACTUAL_OWNER_ADMISSION": "1",
                "SORT4_ACTUAL_OWNER_NINE_ADMISSION": "1",
                "SORT4_ACTUAL_NESTED_H2_REPO_ROOT": str(a.proof_root),
                "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT": str(a.proof_root),
                "SORT4_A1_NINE_REPO_ROOT": str(a.proof_root)})
    return env


def c4_env():
    env = {"SORT4_ACTUAL_C4_FIRST_SELECT_TEST": "0", "SORT4_C1_OUTPUT_EQ": "0", "SORT4_ACTUAL_AST_SCOPE_TEST": "1", "SORT4_STRICT_LFT_CUT": "1",
           "SORT4_ACTUAL_C4_BOUND_PREFIX_TEST": "1", "SORT4_C4_BOUND_CONTROL": "none",
           "SORT4_ACTUAL_C1_PREFIX_TEST": "0", "SORT4_ACTUAL_C2_DISCOVERY_TEST": "0",
           "SORT4_ACTUAL_C2_BOUND_PREFIX_TEST": "0", "SORT4_ACTUAL_C3_CAPTURE_TEST": "0",
           "SORT4_ACTUAL_C3_BOUND_PREFIX_TEST": "0", "SORT4_ACTUAL_C4_CAPTURE_TEST": "0",
           "SORT4_C1_PREFIX_CONTROL": "none", "SORT4_C1_OUTPUT_EQ": "0",
           "SORT4_C2_BOUND_CONTROL": "none", "SORT4_C3_BOUND_CONTROL": "none",
           "SORT4_C3_CAPTURE_SOURCE_SHA256": "", "SORT4_C4_CAPTURE_SOURCE_SHA256": ""}
    return env


def proof(a, label, case, env, cap=600):
    command = [str(a.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
               "-verbose", "2", "verified/lib.rs"]
    before = (sha(case / "verified/lib.rs"), sha(case / "original/lib.rs"))
    result, log = stage(a, label, command, case, env, cap)
    after = (sha(case / "verified/lib.rs"), sha(case / "original/lib.rs"))
    need(before == after, label + " changed source")
    errors = ERROR.findall(log)
    headers = re.findall(r"Verifying function '([^']+)'", log)
    result.update({"errors": errors, "headers": headers,
                   "dead_code": re.findall(r"(?m)^.*: dead code$", log),
                   "source_pair": {"verified": before[0], "original": before[1]},
                   "zero_errors": "0 errors found (" in log,
                   "return_seen": "Executing return statement" in log,
                   "leak_check_seen": "Leak check." in log})
    record(a.evidence / (label + "-proof.json"), result)
    return result, log


def admitted_source(path, expected):
    """Pinned annotation/source admission, before any compiler or proof callback."""
    actual = sha(path)
    need(actual == expected, "SORT4-C4-BOUND: verified source SHA256 differs: " + str(path))
    return actual


def source_admission_mutants(a, c4case, expected):
    capture_mod = module(a.proof_root / "research/challenge-8/overnight-lifetime/capture.py",
                         "composition_source_ghost_strip")
    source = (c4case / "verified/lib.rs").read_bytes()
    original_runtime = capture_mod.strip_ghost(source)
    rows = {}
    for name in ("source", "contract"):
        case = a.evidence / ("composition-admission-" + name)
        case.mkdir()
        if name == "source":
            old, new = b"let min = hint::select_unpredictable(c3, c, a);", b"let min = hint::select_unpredictable(c3, c, d);"
        else:
            old, new = b"\nens thread_token(t) &*&", b"\nens true &*&"
        need(source.count(old) == 1, name + " mutation site is not unique")
        mutated = source.replace(old, new, 1)
        path = case / "lib.rs"
        path.write_bytes(mutated)
        log = ""
        try:
            admitted_source(path, expected)
        except RuntimeError as error:
            log = str(error)
        runtime = capture_mod.strip_ghost(mutated)
        exact = ("source SHA256 differs" in log and mutated != source and
                 ((runtime == original_runtime) == (name == "contract")))
        (case / "preflight.log").write_text(log + "\n")
        row = {"stage": {"exit": 2 if log else 0, "headers": [], "compiler_or_extractor_started": False},
               "intended_refusal": "EXACT_TARGET_REFUSAL" if exact else "INCONCLUSIVE",
               "refusal_marker": "SORT4-C4-BOUND: verified source SHA256 differs", "classification": "ADMISSION_REFUSAL",
               "mutation_fingerprints": {"expected": expected, "mutated": sha(path),
                   "runtime_before": hashlib.sha256(original_runtime).hexdigest(),
                   "runtime_after": hashlib.sha256(runtime).hexdigest()},
               "raw_log_sha256": hashlib.sha256((log + "\n").encode()).hexdigest(), "raw_log": log, "proof_credit": False, "preflight_only": True}
        record(case / "result.json", row)
        rows[name] = row
    return rows


def run(a):
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") in ("verifast-c4-select-integration",
                                     "verifast-native-zst-integration",
                                     "verifast-slice-binding-integration") and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud integration lane required")
    data = manifest(a)
    pin(a)
    os.environ["VERIFAST_MDNEW_FIXTURE_DIR"] = str(a.proof_root / HERE / "mdnew-fixtures")
    c4case, selector_case, source = prepare(a)
    admitted_source(selector_case / "verified/lib.rs", data["selector_source_sha256"])
    admitted_source(c4case / "verified/lib.rs", data["c4_source_sha256"])
    admission_mutants = source_admission_mutants(a, c4case, data["c4_source_sha256"])
    selector_names = source.get("source_order")
    need(isinstance(selector_names, list) and len(selector_names) == 9,
         "selector nine-body source order unavailable")
    selector_mir = capture(a, selector_case, "selector", selector_names)
    c4_mir = capture(a, c4case, "c4")
    old = json.loads((a.proof_root /
        "research/challenge-8/overnight-assume-actual/O26-R3-FRAME-SHADOW-TEST.json").read_text())
    observed = old["observed_capture"]
    selector_mir_exact = all(selector_mir[mode]["body_sha256"] ==
        observed[mode + "_body_sha256"] and
        selector_mir[mode]["whole_decoded_mir_sha256"] ==
        observed[mode + "_whole_decoded_mir_sha256"] for mode in ("normal", "readonly"))
    c4_profile = json.loads((a.proof_root /
        "research/challenge-8/cloud-build/sort4-c4-bound-prefix/profile.json").read_text())
    c4_mir_exact = (c4_mir["normal"]["full_function_record_sha256"] ==
        c4_profile["normal_full_mir_sha256"] and
        c4_mir["readonly"]["full_function_record_sha256"] ==
        c4_profile["readonly_full_mir_sha256"])
    record(a.evidence / "mir-pins.json", {"selector_exact": selector_mir_exact,
        "c4_exact": c4_mir_exact, "selector": selector_mir, "c4": c4_mir})
    actual_sources = {"selector": sha(selector_case / "verified/lib.rs"),
                      "c4": sha(c4case / "verified/lib.rs")}
    expected_sources = {"selector": data["selector_source_sha256"],
                        "c4": data["c4_source_sha256"]}
    if actual_sources != expected_sources or not selector_mir_exact or not c4_mir_exact:
        finish(a, {"classification": "CAPTURE_ONLY_INPUT_MISMATCH",
            "actual_source_hashes": actual_sources, "expected_source_hashes": expected_sources,
            "selector_mir_exact": selector_mir_exact, "c4_mir_exact": c4_mir_exact,
            "selector_proof": "NOT_RUN", "c4_proof": "NOT_RUN",
            "composition": "NOT_RUN_PENDING_TOOL_EXTENSION", "accepted": False})
        return
    stages = {}
    # A fresh AST fingerprint must precede all selector admission opt-ins.
    # Do not inherit the old translator's hashes without this comparison.
    fingerprint_env = selector_env(a)
    for key in (*OWNER_GATES, *BASE_GATES,
                "SORT4_SELECTOR_REACHABLE_UNWIND_MUTANT",
                "SORT4_C4_FIRST_SELECT_ADMISSION_MUTANT",
                "SORT4_C4_FIRST_SELECT_CONTROL", "SORT4_CURRENT_BOUND_AST_EXPORT",
                *(key for pair in PARENT_PAIRS for key in pair)):
        fingerprint_env.pop(key, None)
    fingerprint_env.update({"SORT4_NESTED_FINGERPRINT_MODE": "9",
        "SORT4_NESTED_FINGERPRINT_EVIDENCE_DIR": str(selector_case),
        "SORT4_NESTED_FINGERPRINT_SOURCE_SHA256": actual_sources["selector"]})
    fingerprint, fingerprint_log = proof(a, "selector-fingerprint-refusal",
        selector_case, fingerprint_env, 150)
    source_pins = old["source"]
    expected_fingerprints = {"unit": source_pins["unit_sha256"],
        **{f"body-{i}": value for i, value in enumerate(source_pins["body_sha256"])}}
    fresh_fingerprints = {}
    for label in expected_fingerprints:
        path = selector_case / ("actual-nested-9-" + label + ".marshal")
        fresh_fingerprints[label] = sha(path) if path.is_file() else None
    fingerprint_exact = (fingerprint["exit"] == 2 and
        "SORT4-ACTUAL-NESTED-FINGERPRINT: diagnostic refusal: snapshot complete; no proof rule admitted" in fingerprint_log and
        "Verifying function '" not in fingerprint_log and
        not re.search(r"(?m)^.*: error: .*", fingerprint_log) and
        fresh_fingerprints == expected_fingerprints)
    record(a.evidence / "selector-fingerprint.json", {"stage": fingerprint,
        "expected": expected_fingerprints, "fresh": fresh_fingerprints,
        "exact": fingerprint_exact, "proof_credit": False})
    if not fingerprint_exact:
        finish(a, {"classification": "CAPTURE_ONLY_FINGERPRINT_MISMATCH",
            "source_hashes": actual_sources, "fresh_fingerprints": fresh_fingerprints,
            "expected_fingerprints": expected_fingerprints,
            "selector_proof": "NOT_RUN", "c4_proof": "NOT_RUN",
            "composition": "NOT_RUN_PENDING_TOOL_EXTENSION", "accepted": False})
        return
    exported_ast = a.evidence / "selector-final-ast.marshal"
    export_env = selector_env(a)
    export_env["SORT4_C4_SELECT_AST_EXPORT"] = str(exported_ast)
    selector, selector_log = proof(a, "selector-positive", selector_case, export_env)
    frame_audit = module(a.cloud_dir / "o26-r3-frame-test.py",
                         "integration_frame_log_audit").log_proof_evidence(
                             selector_log, {"exit": selector["exit"]})
    nested = "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop"
    main = "select_unpredictable"
    header = selector["headers"]
    selector_verification_order = [*selector_names[:7], nested, main]
    selector_name_set = set(selector_verification_order)
    selector_header_order = [name for name in header if name in selector_name_set]
    selector_headers_exact = (
        len(selector_names) == 9 and set(selector_names[7:]) == {nested, main} and
        all(header.count(name) == 1 for name in selector_verification_order) and
        selector_header_order == selector_verification_order)
    selector_ok = (selector["exit"] == 0 and not selector["errors"] and
        not selector["dead_code"] and selector["zero_errors"] and
        selector["return_seen"] and selector["leak_check_seen"] and
        selector_headers_exact and
        header.index(nested) < header.index(main) and
        frame_audit["prefix7_ordered"] and frame_audit["nested_before_outer"] and
        frame_audit["helper_full_normal_unwind_observed"] and
        frame_audit["nested_full_normal_unwind_observed"] and
        frame_audit["outer_full_normal_unwind_observed"])
    if selector_ok:
        if data.get("producer_seal_discovery") is True:
            need(exported_ast.is_file() and
                 "producer_location_alias_partition=preserved" in selector_log,
                 "sharing discovery producer artifact/certificate missing")
            outer_case = a.evidence.parents[1] / "source-preparation/regression-fixtures/negative_outer_bound_escape"
            outer_mir = capture(a, outer_case, "outer-discovery",
                                ["negative_outer_bound_escape"])
            finish(a, {"classification": "PRODUCER_SEAL_DISCOVERY_ONLY",
                "diagnostic_complete": False, "composition_positive": False,
                "selector_full_nine_body": True,
                "producer_discovery": {"producer_ast_sha256": sha(exported_ast),
                    "manifest_sha256": sha(a.manifest), "profile_id": data["profile_id"],
                    "proof_sha": os.environ.get("PROOF_SHA"),
                    "build_id": os.environ.get("CLOUD_BUILD_ID"),
                    "effective_tool": json.loads((a.evidence / "effective-hashes.json").read_text())["actual"],
                    "selector_mir": selector_mir, "pre_ast_fingerprints": fresh_fingerprints,
                    "nine_body_audit": frame_audit, "proof_log_sha256": selector["log_sha256"],
                    "receipt_created_only_after_full_nine_body_proof": True},
                "outer_mir": outer_mir, "consumer_admission": "NOT_RUN_UNSEALED_DISCOVERY"})
            return
        need(exported_ast.is_file() and sha(exported_ast) == data["producer_final_ast_sha256"],
             "fresh successful producer final AST differs from reviewed fixed pin")
        record(a.evidence / "producer-receipt.json", {
            "manifest_sha256": sha(a.manifest), "profile_id": data["profile_id"],
            "proof_sha": os.environ.get("PROOF_SHA"), "build_id": os.environ.get("CLOUD_BUILD_ID"),
            "effective_tool": json.loads((a.evidence / "effective-hashes.json").read_text())["actual"],
            "effective_hashes": data["effective_hashes"], "producer_ast_sha256": sha(exported_ast),
            "selector_source_sha256": actual_sources["selector"], "selector_mir": selector_mir,
            "pre_ast_fingerprints": fresh_fingerprints, "nine_body_audit": frame_audit,
            "proof_log_sha256": hashlib.sha256(selector_log.encode()).hexdigest(),
            "receipt_created_only_after_full_nine_body_proof": True})
    stages["selector"] = {"positive": selector, "full_nine_body": selector_ok,
                          "exact_nine_header_sequence": selector_headers_exact,
                          "filtered_header_sequence": selector_header_order,
                          "proof_audit": frame_audit}
    if selector_ok:
        reachable_env = selector_env(a)
        reachable_env["SORT4_SELECTOR_REACHABLE_UNWIND_MUTANT"] = "1"
        row, log = proof(a, "selector-reachable-unwind-mutant", selector_case, reachable_env, 180)
        fingerprint = re.findall(r"old_edge_sha256=([a-f0-9]{64}) new_edge_sha256=([a-f0-9]{64})", log)
        marker = "owner shared cleanup predecessor inventory"
        exact = (row["exit"] in (1, 2) and not row["headers"] and marker in log and
                 "body_index=7 body=select_unpredictable line=194" in log and
                 "old_action=Unreachable new_action=Cleanup(38)" in log and
                 "cleanup_predecessors=18->19" in log and len(fingerprint) == 1 and
                 fingerprint[0][0] != fingerprint[0][1] and
                 "source_sha256=" + actual_sources["selector"] in log and
                 "unit_sha256=" + source_pins["unit_sha256"] in log)
        admission_mutants["reachable_unwind"] = {"stage": row, "raw_log": log,
            "raw_log_sha256": hashlib.sha256(log.encode()).hexdigest(),
            "refusal_marker": marker, "mutation_fingerprints": fingerprint,
            "admitted_unit_sha256": source_pins["unit_sha256"],
            "decoded_whole_mir_sha256": selector_mir["normal"]["whole_decoded_mir_sha256"],
            "classification": "ADMISSION_REFUSAL", "proof_credit": False,
            "intended_refusal": "EXACT_TARGET_REFUSAL" if exact else "INCONCLUSIVE"}
    c4, c4log = proof(a, "c4-positive", c4case, c4_env())
    target = c4log.find("Verifying function 'sort4_stable'")
    c4_pre = c4case / "actual-c4-bound-pre-ast.ml"
    c4_post = c4case / "actual-c4-bound-post-ast.ml"
    c4_post_text = c4_post.read_text() if c4_post.is_file() else ""
    c4_ast_exact = (c4_pre.is_file() and sha(c4_pre) == c4_profile["pre_ast_sha256"] and
        c4_post.is_file() and
        c4_post_text.count('"std::ops::FnMut::call_mut"') == 4 and
        c4_post_text.count('"#register_type_projection_equality"') == 4 and
        "UNBOUND_LIFETIME_DECL_PLACEHOLDER" not in c4_post_text)
    c4_ok = (c4["exit"] == 0 and not c4["errors"] and not c4["dead_code"] and
        c4["zero_errors"] and c4["return_seen"] and c4["leak_check_seen"] and
        c4_ast_exact and
        target >= 0 and all(c4log.find("Verifying function '" + name + "'") >= 0 and
            c4log.find("Verifying function '" + name + "'") < target for name in HELPERS) and
        "SORT4-C4-BOUND admitted " in c4log)
    stages["c4"] = {"positive": c4, "positive_ok": c4_ok,
        "ast_exact": c4_ast_exact, "pre_ast_sha256": sha(c4_pre) if c4_pre.is_file() else None,
        "post_ast_sha256": sha(c4_post) if c4_post.is_file() else None,
        "controls": {}}
    composition_ok = False
    composition = {"state": "NOT_RUN_PARENT_FAILED"}
    if selector_ok and c4_ok and exported_ast.is_file():
        consumer = a.evidence / "composition-fixture"
        shutil.copytree(c4case, consumer, symlinks=True)
        (consumer / "selector").mkdir()
        shutil.copyfile(selector_case / "verified/lib.rs", consumer / "selector/lib.rs")
        receipt = json.loads((a.evidence / "producer-receipt.json").read_text())
        need(receipt["producer_ast_sha256"] == data["producer_final_ast_sha256"] == sha(exported_ast) and
             receipt["manifest_sha256"] == sha(a.manifest) and
             receipt["proof_sha"] == os.environ.get("PROOF_SHA") and
             receipt["build_id"] == os.environ.get("CLOUD_BUILD_ID") and
             receipt["receipt_created_only_after_full_nine_body_proof"],
             "same-run checked producer receipt differs")
        original_blob = exported_ast.read_bytes()
        relocated_blob = original_blob.replace(b"verified/lib.rs", b"selector/lib.rs")
        need(relocated_blob.replace(b"selector/lib.rs", b"verified/lib.rs") == original_blob,
             "AST path relocation is not reversible")
        env = c4_env()
        env.update({"SORT4_ACTUAL_C4_BOUND_PREFIX_TEST": "0",
            "SORT4_ACTUAL_C4_FIRST_SELECT_TEST": "1",
            "SORT4_C4_SELECT_AST_IMPORT": str(exported_ast),
            "SORT4_C4_SELECT_AST_EXPORT_SHA256": sha(exported_ast),
            "SORT4_C4_SELECT_AST_RELOCATED_SHA256": hashlib.sha256(relocated_blob).hexdigest(),
            "SORT4_C4_SELECT_SELECTOR_SOURCE_SHA256": actual_sources["selector"]})
        result, raw = proof(a, "composition-positive", consumer, env)
        target = raw.find("Verifying function 'sort4_stable'")
        composition_header_order = [name for name in result["headers"]
                                    if name in selector_name_set]
        composition_headers_exact = (
            all(result["headers"].count(name) == 1
                for name in selector_verification_order) and
            composition_header_order == selector_verification_order)
        composition_ok = (result["exit"] == 0 and not result["errors"] and
            not result["dead_code"] and result["zero_errors"] and
            result["return_seen"] and result["leak_check_seen"] and
            "SORT4-C4-SELECT-AST: importing nine definitions" in raw and
            ("typed location-only certificate paths=" + str(data["producer_typed_location_endpoints"]) +
             " ordinary_strings=0 ref_sharing=none unsupported=none location_alias_partition=preserved") in raw and
            "producer_location_alias_partition=preserved" in selector_log and
            target >= 0 and composition_headers_exact and
            all(raw.find("Verifying function '" + name + "'") < target
                for name in selector_verification_order) and
            result["headers"].index(nested) < result["headers"].index(main))
        composition = {"state": "PASS_PENDING_REVIEW" if composition_ok else "FAIL",
            "positive": result,
            "same_kernel_reverified_nine_bodies": composition_ok and composition_headers_exact,
            "exact_nine_header_sequence": composition_headers_exact,
            "filtered_header_sequence": composition_header_order,
            "required_verification_order": selector_verification_order,
            "export_sha256": sha(exported_ast),
            "relocated_sha256": hashlib.sha256(relocated_blob).hexdigest(),
            "location_occurrences": original_blob.count(b"verified/lib.rs"),
            "typed_location_endpoints": data["producer_typed_location_endpoints"],
            "location_only_audit": "TYPED_CERTIFICATE_OBSERVED_REVIEW_PENDING" if composition_ok else "NOT_CONFIRMED",
            "original_posts_preserved": True, "raw_ptr_own_pointee_rights": False}
        composition["controls"] = {}
        if composition_ok:
            for control in ("wrong-selected-original", "normal-false-post",
                            "c4-normal-omit-join", "c4-unwind-missing-close",
                            "leak-thread-token", "leak-current-four-cell-frame"):
                ctrlcase = a.evidence / ("composition-control-" + control)
                shutil.copytree(consumer, ctrlcase, symlinks=True)
                ctrlenv = env.copy()
                if control in ("wrong-selected-original", "leak-thread-token", "leak-current-four-cell-frame"):
                    ctrlenv["SORT4_C4_FIRST_SELECT_CONTROL"] = control
                else:
                    ctrlenv["SORT4_C4_BOUND_CONTROL"] = control
                row, log = proof(a, "composition-control-" + control, ctrlcase, ctrlenv)
                target = log.find("Verifying function 'sort4_stable'")
                first_error = log.find(row["errors"][0]) if row["errors"] else -1
                row["target_before_first_error"] = target >= 0 and first_error > target
                if control == "wrong-selected-original":
                    selector_headers_before_c4 = all(
                        row["headers"].count(name) == 1 and
                        log.find("Verifying function '" + name + "'") < target
                        for name in selector_names)
                    exact_error = (len(row["errors"]) == 1 and
                        re.fullmatch(r"verified/lib\.rs\(487,19-55\): error: Assertion might not hold\. \(Cannot prove false\.\)",
                                     row["errors"][0]) is not None)
                    row["intended_negative"] = (
                        "EXACT_TARGET_VC_OBSERVED" if row["exit"] in (1, 2) and
                        row["target_before_first_error"] and
                        "SORT4-C4-SELECT-AST: importing nine definitions" in log and
                        selector_headers_before_c4 and exact_error
                        else "PENDING_RAW_VC_REVIEW")
                    row["raw_vc_review"] = "PENDING_INDEPENDENT_REVIEW"
                else:
                    expected_line, expected_message = {
                        "normal-false-post": (315, "Cannot prove condition"),
                        "c4-normal-omit-join": (317, "foreach"),
                        "c4-unwind-missing-close": (68, "comparison_debt"),
                        "leak-thread-token": (315, "thread_token"),
                        "leak-current-four-cell-frame": (316, "No matching heap chunks"),
                    }[control]
                    exact = (row["exit"] in (1, 2) and row["target_before_first_error"] and
                             len(row["errors"]) == 1 and expected_message in row["errors"][0] and
                             re.search(r"verified/lib\.rs\(" + str(expected_line) + r",\d+(?:-|\))", row["errors"][0]) is not None and
                             all(row["headers"].count(name) == 1 and
                                 log.find("Verifying function '" + name + "'") < target for name in selector_names))
                    if control.startswith("leak-"):
                        exact = exact and ("SORT4-C4-FIRST-SELECT-SEMANTIC-CONTROL: " + control + " at source-487 after selector") in log
                    row["intended_negative"] = "EXACT_TARGET_VC_OBSERVED" if exact else "PENDING_RAW_VC_REVIEW"
                    row["expected_post_line"] = expected_line
                    row["expected_predicate"] = expected_message
                row["raw_vc_review"] = "PENDING_INDEPENDENT_REVIEW"
                row["export_sha256"] = sha(exported_ast)
                composition["controls"][control] = row
        for name, mode, marker in (
            ("type", "type", "TYPE: exact original first selector call/type/operands"),
            ("Move", "move", "MOVE: exact original first selector operand setup"),
            ("edge", "edge", "EDGE: source-derived normal/unwind successor identity")):
            mutant_case = a.evidence / ("composition-admission-" + name)
            shutil.copytree(consumer, mutant_case, symlinks=True)
            mutant_env = env.copy()
            mutant_env["SORT4_C4_FIRST_SELECT_ADMISSION_MUTANT"] = mode
            row, log = proof(a, "composition-admission-" + name, mutant_case, mutant_env, 180)
            fingerprints = re.findall(r"SORT4-C4-FIRST-SELECT-ADMISSION-MUTANT: (\w+) old=([a-f0-9]{32}) new=([a-f0-9]{32}) pre_ast=([a-f0-9]{64})", log)
            exact = (row["exit"] in (1, 2) and not row["headers"] and marker in log and
                     len(fingerprints) == 1 and fingerprints[0][1] != fingerprints[0][2] and
                     fingerprints[0][3] == c4_profile["pre_ast_sha256"])
            admission_mutants[name] = {"stage": row, "raw_log": log,
                "raw_log_sha256": hashlib.sha256(log.encode()).hexdigest(), "refusal_marker": marker,
                "mutation_fingerprints": fingerprints, "classification": "ADMISSION_REFUSAL",
                "intended_refusal": "EXACT_TARGET_REFUSAL" if exact else "INCONCLUSIVE", "proof_credit": False}
    stages["composition"] = composition
    parents_only = os.environ.get("SORT4_C4_SELECT_DIAGNOSTIC_STAGE") == "parents-and-composition"
    if parents_only:
        stages["regressions"] = {"classification": "DEFERRED_AFFECTED_GATES",
            "unchanged_baseline_evidence": "af4e44a3-ff6b-4d66-b6a0-7bd65f2f1e09",
            "completion_gates": {"ready": False, "blockers": [
                "affected_regression_gates_pending_separate_run_and_review"]}}
    else:
        regressions = module(a.cloud_dir / "verifast-c4-select-integration/regressions.py", "integration_regressions")
        stages["regressions"] = regressions.run(a, a.tool_home, selector_case, c4case,
            selector_env(a), c4_env(), stage, proof, composition.get("controls", {}), admission_mutants, capture)
    if c4_ok and not parents_only:
        inherited = data["inherited_c4_controls"]
        need(inherited["source_sha256"] == actual_sources["c4"] and
             inherited["pre_ast_sha256"] == sha(c4_pre) and
             inherited["kernel_sha256"] == data["effective_hashes"]["src/verifast.ml"] and
             set(inherited["rows"]) == set(CONTROLS), "inherited C4 control inputs differ")
        stages["c4"]["controls"] = inherited["rows"]
        stages["c4"]["control_evidence_reuse"] = inherited["eligibility"]
    control_reached = c4_ok and len(stages["c4"]["controls"]) == len(CONTROLS) and all(
        row["exit"] in (1, 2) and row["target_entry_before_first_error"]
        for row in stages["c4"]["controls"].values())
    classification = ("INTEGRATION_POSITIVES_AND_CONTROL_TARGETS_REACHED"
                      if selector_ok and control_reached and composition_ok else "INTEGRATION_DIAGNOSTIC_INCOMPLETE")
    regression_gates = stages["regressions"].get("completion_gates", {})
    composition_controls_complete = (
        len(composition.get("controls", {})) == 6 and all(
            row.get("intended_negative") == "EXACT_TARGET_VC_OBSERVED" and
            row.get("raw_vc_review") == "REVIEWED" for row in
            composition.get("controls", {}).values()))
    c4_controls_reviewed = (len(stages["c4"]["controls"]) == len(CONTROLS) and all(
        row.get("intended_negative") == "EXACT_TARGET_VC_OBSERVED" and
        row.get("raw_vc_review") == "REVIEWED"
        for row in stages["c4"]["controls"].values()))
    completion_blockers = []
    if not selector_ok:
        completion_blockers.append("selector_positive_gate_failed")
    if not c4_ok:
        completion_blockers.append("c4_positive_gate_failed")
    if not composition_ok:
        completion_blockers.append("composition_positive_gate_failed_or_not_run")
    if not control_reached:
        completion_blockers.append("c4_control_targets_not_all_reached")
    if not regression_gates.get("ready", False):
        completion_blockers.extend(regression_gates.get("blockers", [
            "regression_completion_gates_unavailable"]))
    if not composition_controls_complete:
        for name, row in composition.get("controls", {}).items():
            if row.get("intended_negative") != "EXACT_TARGET_VC_OBSERVED":
                completion_blockers.append("composition_control_not_exact:" + name)
            elif row.get("raw_vc_review") != "REVIEWED":
                completion_blockers.append("composition_control_raw_review_pending:" + name)
        if len(composition.get("controls", {})) != 6:
            completion_blockers.append("composition_control_set_incomplete")
    if not c4_controls_reviewed:
        for name, row in stages["c4"]["controls"].items():
            if row.get("intended_negative") != "EXACT_TARGET_VC_OBSERVED":
                completion_blockers.append("c4_control_raw_vc_not_confirmed:" + name)
            elif row.get("raw_vc_review") != "REVIEWED":
                completion_blockers.append("c4_control_raw_review_pending:" + name)
        if len(stages["c4"]["controls"]) != len(CONTROLS):
            completion_blockers.append("c4_control_set_incomplete")
    diagnostic_complete = not completion_blockers
    if not diagnostic_complete:
        classification = "INTEGRATION_DIAGNOSTIC_INCOMPLETE"
    finish(a, {"classification": classification,
        "diagnostic_complete": diagnostic_complete,
        "completion_blockers": completion_blockers,
        "source_hashes": actual_sources, "stages": stages,
        "selector_full_nine_body": selector_ok, "c4_positive": c4_ok,
        "c4_controls_reached_target": control_reached,
        "c4_controls_intended_vc_review": "PENDING_RAW_REVIEW",
        "composition": composition,
        "composition_positive": composition_ok,
        "target_contract_proved": False, "actual_source_accepted": False,
        "verification_accepted": False, "accepted": False})
    pin(a)
    need(diagnostic_complete, classification)


def outer_capture(a):
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "verifast-c4-select-integration",
         "Cloud-only outer MIR capture required")
    need(manifest(a).get("outer_capture_only") is True, "exact outer capture mode required")
    data = manifest(a)
    for name, expected in data["stock_effective_hashes"].items():
        need(sha(a.tool_home / name) == expected, "outer capture exporter/refiner pin differs")
    need(sha(a.tool_home / SCHEMA) == data["effective_hashes"][SCHEMA],
         "outer capture schema pin differs")
    case = a.evidence.parents[1] / "source-preparation/regression-fixtures/negative_outer_bound_escape"
    pins = capture(a, case, "outer-discovery", ["negative_outer_bound_escape"])
    finish(a, {"classification": "OUTER_MIR_CAPTURE_ONLY", "outer_mir": pins,
               "diagnostic_complete": False, "consumer_admission": "NOT_RUN_CAPTURE_ONLY"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="mode", required=True)
    for mode in ("preflight", "source-prepare", "apply", "pin", "run", "outer-capture"):
        command = sub.add_parser(mode)
        command.add_argument("--proof-root", type=Path, required=True)
        command.add_argument("--manifest", type=Path, required=True)
        command.add_argument("--evidence", type=Path, required=True)
        if mode in ("apply", "pin", "run", "outer-capture"):
            command.add_argument("--tool-home", type=Path, required=True)
        if mode in ("preflight", "source-prepare", "run", "outer-capture"):
            command.add_argument("--cloud-dir", type=Path, required=True)
        if mode in ("run", "outer-capture"):
            command.add_argument("--compiler-sysroot", type=Path, required=True)
            command.add_argument("--deadline-epoch", type=int, required=True)
    failure = sub.add_parser("failure")
    failure.add_argument("--evidence", type=Path, required=True)
    failure.add_argument("--stage", required=True)
    failure.add_argument("--exit-code", type=int, required=True)
    a = parser.parse_args()
    a.evidence = a.evidence.resolve()
    if a.mode == "failure":
        finish(a, {"classification": "SETUP_OR_EXECUTION_FAILURE",
            "failed_stage": a.stage, "exit_code": a.exit_code, "accepted": False,
            "intended_negative": False})
        return
    a.proof_root = a.proof_root.resolve()
    a.manifest = a.manifest.resolve()
    if hasattr(a, "cloud_dir"):
        a.cloud_dir = a.cloud_dir.resolve()
    need(all(str(value).startswith("/workspace/") for value in
        (a.proof_root, a.manifest, a.evidence)), "Cloud workspace paths required")
    if a.mode == "preflight":
        preflight(a)
    elif a.mode == "source-prepare":
        source_prepare(a)
    elif a.mode == "outer-capture":
        outer_capture(a)
    elif a.mode == "apply":
        apply(a)
    elif a.mode == "pin":
        pin(a)
    else:
        run(a)


if __name__ == "__main__":
    main()
