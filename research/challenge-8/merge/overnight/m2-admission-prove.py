#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only exact-shape admission controls for the pinned tuple-2 expansion."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
POINTER_PROVE = HERE / "pointer-prove.py"
VALID_FIXTURE = HERE / "callback-cases.rs"
PRELUDE_REL = Path("bin/rust/prelude.rsspec")
CALLBACK_PATCH = HERE / "callback.patch"
EXPECTED_PRELUDE_SHA256 = "d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5"
EXPECTED_CALLBACK_SHA256 = "0a006df94f04d6425d70280967d6652bdd33ccb88ead4a44f02a2e36775aaa5e"
SHAPE_ERROR = "std_tuple_2_ ownership expansion requires the pinned two-field tuple shape"
DECL = re.compile(
    rb"(?m)^(?P<prefix>[ \t]*(?:pub[ \t]+)?struct[ \t]+std_tuple_2_<)"
    rb"(?P<params>[^>\r\n]+)(?P<middle>>[ \t]*\()(?P<fields>[^)\r\n]*)(?P<suffix>\)[^\r\n]*)$"
)
DIAGNOSTIC = re.compile(
    r"(?m)^([^\r\n]+)\((\d+),(\d+)-(?:((?:\d+),))?(\d+)\): error: ([^\r\n]+)$"
)
SHAPES = {
    "renamed_parameters": ("A, B", "T1, T2"),
    "reordered_parameters": ("T2, T1", "T1, T2"),
    "wrong_parameter_count": ("T1", "T1, T2"),
    "reordered_fields": ("T1, T2", "T2, T1"),
    "missing_field": ("T1, T2", "T1"),
    "extra_field": ("T1, T2", "T1, T2, T1"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tree_manifest(root: Path) -> dict[str, str]:
    manifest = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            manifest[relative] = "symlink:" + os.readlink(path)
        elif path.is_file():
            manifest[relative] = digest(path.read_bytes())
        elif path.is_dir():
            manifest[relative] = "directory"
    return manifest


def mutate_declaration(prelude: bytes, params: str, fields: str) -> bytes:
    matches = list(DECL.finditer(prelude))
    if len(matches) != 1:
        raise RuntimeError(f"expected one parseable tuple-2 declaration, found {len(matches)}")
    match = matches[0]
    changed = (prelude[:match.start()] + match.group("prefix") + params.encode("ascii") +
               match.group("middle") + fields.encode("ascii") + match.group("suffix") +
               prelude[match.end():])
    if changed == prelude:
        raise RuntimeError("shape control failed to alter the tuple-2 declaration")
    return changed


def hosted_guard() -> None:
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or
            os.environ.get("RUNNER_OS") != "Linux" or
            os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):
        raise RuntimeError("M2 admission controls require hosted Linux Actions on overnight/merge-26.10")
    expected_sha = os.environ.get("GITHUB_SHA")
    if not expected_sha:
        raise RuntimeError("GITHUB_SHA is required for exact-dispatch admission evidence")
    actual_sha = subprocess.run(["git", "rev-parse", "HEAD"], check=True,
                                capture_output=True, text=True).stdout.strip()
    if actual_sha != expected_sha:
        raise RuntimeError("checkout HEAD differs from dispatched GITHUB_SHA")


def run_pointer(args, tool_home: Path, evidence: Path, env: dict[str, str]) -> dict:
    command = [sys.executable, str(POINTER_PROVE), "--tool-home", str(tool_home),
               "--compiler-sysroot", args.compiler_sysroot, "--schema", str(args.schema),
               "--fixture", str(VALID_FIXTURE), "--cases", "tuple2_field_resources",
               "--profile", "m2-exact-tuple2-admission-shape-controls-v1",
               "--evidence", str(evidence)]
    completed = subprocess.run(command, env=env, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"pointer-prove failed with exit code {completed.returncode}: {evidence}")
    classification_path = evidence / "cases/tuple2_field_resources/classification.json"
    if not classification_path.is_file():
        raise RuntimeError(f"pointer-prove did not retain tuple2 classification: {classification_path}")
    return json.loads(classification_path.read_text())


def shape_rejection_ok(classification: dict, log: str, fixture_sha: str,
                       baseline_fixture_sha: str, source_hash: str,
                       expected_source_hash: str) -> tuple[bool, dict]:
    stages = classification.get("stages", {})
    matches = list(DIAGNOSTIC.finditer(log))
    parsed = None
    if len(matches) == 1:
        match = matches[0]
        end_line = int(match.group(4)[:-1]) if match.group(4) else int(match.group(2))
        parsed = {
            "file": match.group(1), "line": int(match.group(2)),
            "column_start": int(match.group(3)), "end_line": end_line,
            "column_end": int(match.group(5)), "message": match.group(6),
        }
    valid = (
        stages == {"exporter": 0, "decode": 0, "verifast": 1, "refinement": 0} and
        classification.get("source_unchanged_at_every_stage") is True and
        classification.get("full_positive_gate") is False and
        classification.get("visited_bodies") == [] and
        classification.get("body_execution_records", {}).get("tuple2_field_resources", 0) == 0 and
        fixture_sha == baseline_fixture_sha and source_hash == expected_source_hash and
        len(classification.get("error_lines", [])) == 1 and parsed is not None and
        parsed["file"].endswith("bin/rust/prelude.rsspec") and parsed["line"] == 15 and
        parsed["end_line"] == 15 and parsed["column_start"] == 8 and
        parsed["column_end"] == 20 and parsed["message"] == SHAPE_ERROR
    )
    return valid, parsed or {}


def shape_mutation_controls(classification: dict, log: str, fixture_sha: str,
                            baseline_fixture_sha: str, source_hash: str,
                            expected_source_hash: str) -> dict[str, bool]:
    accepted, _ = shape_rejection_ok(classification, log, fixture_sha,
                                     baseline_fixture_sha, source_hash,
                                     expected_source_hash)
    controls = {"exact_control_accepted": accepted}
    for key in ("exporter", "decode", "verifast", "refinement"):
        mutant = dict(classification)
        mutant["stages"] = dict(classification.get("stages", {}))
        mutant["stages"][key] = 0 if mutant["stages"].get(key) != 0 else 1
        controls[f"wrong_stage_{key}_rejected"] = not shape_rejection_ok(
            mutant, log, fixture_sha, baseline_fixture_sha, source_hash,
            expected_source_hash)[0]
    controls["wrong_message_rejected"] = not shape_rejection_ok(
        classification, log.replace(SHAPE_ERROR, "synthetic shape error"), fixture_sha,
        baseline_fixture_sha, source_hash, expected_source_hash)[0]
    controls["wrong_location_rejected"] = not shape_rejection_ok(
        classification, log.replace("(15,8-20): error", "(15,9-20): error"),
        fixture_sha, baseline_fixture_sha, source_hash, expected_source_hash)[0]
    controls["altered_source_rejected"] = not shape_rejection_ok(
        classification, log, fixture_sha, baseline_fixture_sha, "altered-source-hash",
        expected_source_hash)[0]
    mutant_entry = dict(classification)
    mutant_entry["visited_bodies"] = ["tuple2_field_resources"]
    controls["body_entry_rejected"] = not shape_rejection_ok(
        mutant_entry, log, fixture_sha, baseline_fixture_sha, source_hash,
        expected_source_hash)[0]
    mutant_execution = dict(classification)
    mutant_execution["body_execution_records"] = {"tuple2_field_resources": 1}
    controls["body_execution_rejected"] = not shape_rejection_ok(
        mutant_execution, log, fixture_sha, baseline_fixture_sha, source_hash,
        expected_source_hash)[0]
    return controls


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-home", type=Path, required=True,
                        help="complete callback.patch experimental tool home built by hosted run.sh")
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    hosted_guard()
    if args.evidence.exists():
        raise RuntimeError(f"refusing to reuse evidence directory: {args.evidence}")
    if digest(CALLBACK_PATCH.read_bytes()) != EXPECTED_CALLBACK_SHA256:
        raise RuntimeError("callback.patch differs from the reviewed pinned profile")
    prelude_path = args.tool_home / PRELUDE_REL
    baseline_prelude = prelude_path.read_bytes()
    if digest(baseline_prelude) != EXPECTED_PRELUDE_SHA256:
        raise RuntimeError("tool-home prelude differs from the reviewed pinned baseline")
    if not args.schema.is_file():
        raise RuntimeError(f"pinned schema missing: {args.schema}")
    fixture_sha = digest(VALID_FIXTURE.read_bytes())
    args.evidence.mkdir(parents=True)
    baseline_tree = tree_manifest(args.tool_home)
    report = {
        "profile": "m2-exact-tuple2-admission-shape-controls-v1",
        "source_sha": os.environ["GITHUB_SHA"],
        "callback_patch_sha256": EXPECTED_CALLBACK_SHA256,
        "baseline_prelude_sha256": EXPECTED_PRELUDE_SHA256,
        "fixture_sha256": fixture_sha,
        "status": {},
        "shape_controls": {},
        "visibility_control": "not expressible through pinned prelude parser: tuple fields are always parsed Public",
    }
    base_env = dict(os.environ)
    baseline_classification = run_pointer(args, args.tool_home, args.evidence / "valid-control", base_env)
    if baseline_classification.get("classification") != "PASS" or not baseline_classification.get("full_positive_gate"):
        raise RuntimeError("unchanged tuple2_field_resources full positive gate did not pass")
    report["status"]["valid_control"] = baseline_classification["classification"]
    baseline_metadata = json.loads((args.evidence /
        "valid-control/cases/tuple2_field_resources/metadata.json").read_text())
    expected_source_hash = baseline_metadata.get("verified_sha256")
    if not expected_source_hash or baseline_metadata.get("ghost_strip_exact_bytes") is not True:
        raise RuntimeError("valid tuple fixture lacks exact source-admission evidence")
    all_controls_pass = True
    with tempfile.TemporaryDirectory(prefix="m2-tuple2-tool-homes-") as scratch:
        scratch_path = Path(scratch)
        for index, (name, (params, fields)) in enumerate(SHAPES.items()):
            clone = scratch_path / f"{index}-{name}"
            shutil.copytree(args.tool_home, clone, symlinks=True)
            clone_prelude = clone / PRELUDE_REL
            before = clone_prelude.read_bytes()
            if before != baseline_prelude:
                raise RuntimeError(f"{name}: fresh full tool-home copy changed before mutation")
            clone_prelude.write_bytes(mutate_declaration(before, params, fields))
            changed_tree = tree_manifest(clone)
            differences = sorted(path for path in set(baseline_tree) | set(changed_tree)
                                 if baseline_tree.get(path) != changed_tree.get(path))
            if differences != [PRELUDE_REL.as_posix()]:
                raise RuntimeError(f"{name}: copied tool home differs beyond exact prelude declaration: {differences}")
            mutant_env = dict(base_env)
            bin_path = str(clone / "bin")
            mutant_env["LD_LIBRARY_PATH"] = bin_path + (":" + mutant_env["LD_LIBRARY_PATH"]
                                                          if mutant_env.get("LD_LIBRARY_PATH") else "")
            case_evidence = args.evidence / name
            classification = run_pointer(args, clone, case_evidence, mutant_env)
            log = (case_evidence / "cases/tuple2_field_resources/verifast.log").read_text(
                errors="replace")
            observed_fixture_sha = json.loads((case_evidence / "cases/tuple2_field_resources/metadata.json").read_text())
            source_hash = observed_fixture_sha.get("verified_sha256", "")
            accepted, diagnostic = shape_rejection_ok(classification, log, fixture_sha,
                                                       fixture_sha, source_hash,
                                                       expected_source_hash)
            controls = shape_mutation_controls(classification, log, fixture_sha,
                                                fixture_sha, source_hash,
                                                expected_source_hash)
            controls_ok = all(controls.values())
            all_controls_pass &= accepted and controls_ok
            report["shape_controls"][name] = {
                "classification": "EXPECTED_SHAPE_REJECTION" if accepted else "INCONCLUSIVE",
                "exact_diagnostic": diagnostic,
                "stages": classification.get("stages"),
                "body_entered": bool(classification.get("visited_bodies")),
                "body_execution_records": classification.get("body_execution_records"),
                "tool_home_changed_paths": differences,
                "classifier_fail_closed_mutations": controls,
                "classifier_controls_passed": controls_ok,
            }
            print(f"{name}: {report['shape_controls'][name]['classification']}", flush=True)
    report["classifier_controls_passed"] = all_controls_pass
    report["tuple_resource_and_hrtb_status"] = (
        "not run by this shape-only component; retain separate proof/admission classifications")
    (args.evidence / "m2-admission.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.evidence / "aggregate.json").write_text(json.dumps({
        "classifier_controls_passed": all_controls_pass,
        "valid_tuple_control": report["status"]["valid_control"],
        "shape_controls": {name: row["classification"]
                           for name, row in report["shape_controls"].items()},
        "visibility_control": report["visibility_control"],
    }, indent=2) + "\n")
    return 0 if all_controls_pass else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"M2 admission control failed: {error}", file=sys.stderr)
        sys.exit(2)
