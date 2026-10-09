#!/usr/bin/env python3
"""Fail-closed source/profile admission for MIR-OR-JOIN-LIVENESS.

This is an input gate for a separately named Cloud-only experimental profile.
It does not parse MIR, prove reachability, or classify a VeriFast result.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--baseline-translator", type=Path, required=True)
    parser.add_argument("--component-patch", type=Path, required=True)
    parser.add_argument("--component-translator", type=Path, required=True)
    parser.add_argument("--case", default="positive")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    require(manifest.get("component") == "MIR-OR-JOIN-LIVENESS",
            "wrong component manifest")
    require(manifest.get("verifast_commit") ==
            "f76012fb518703b1d98e243ac4f487f16877cfcb",
            "wrong VeriFast source pin")
    require(manifest.get("baseline_profile") ==
            "existing-six-patch-experimental-unaccepted",
            "wrong baseline profile")
    require(manifest.get("admission_state") ==
            "EXPERIMENTAL_CLOUD_TRIAL",
            "component has not been explicitly activated for a Cloud trial")
    require(sha256(Path(__file__)) ==
            manifest.get("admission_checker_sha256"),
            "admission checker hash mismatch")
    if args.case == "positive":
        source_pin = {
            "sha256": manifest.get("admitted_source_sha256"),
            "signature_line": manifest.get("admitted_signature_line"),
            "guard_line": manifest.get("admitted_guard_line"),
        }
    else:
        controls = manifest.get("control_sources")
        require(isinstance(controls, dict),
                "control source allowlist is missing")
        source_pin = controls.get(args.case)
        require(isinstance(source_pin, dict) and
                source_pin.get("expected_gate") == "DEAD_PROOF",
                "control source/case has no explicit proof-negative pin")
    admitted = source_pin.get("sha256")
    require(isinstance(admitted, str) and len(admitted) == 64,
            "no admitted source hash; diagnostic source is not permission")
    for path, key in (
        (args.baseline_translator, "baseline_translator_sha256"),
        (args.component_patch, "component_patch_sha256"),
        (args.component_translator, "component_translator_sha256"),
    ):
        expected = manifest.get(key)
        require(isinstance(expected, str) and
                sha256(path) == expected,
                f"{key} mismatch")
    require(sha256(args.source) == admitted,
            "admitted source hash mismatch")

    signature_line = source_pin.get("signature_line")
    guard_line = source_pin.get("guard_line")
    require(isinstance(signature_line, int) and signature_line > 0,
            "no admitted signature line")
    require(isinstance(guard_line, int) and guard_line > signature_line,
            "no admitted guard line")
    source_lines = args.source.read_text(encoding="utf-8").splitlines()
    require(len(source_lines) >= guard_line + 3,
            "bounded source body is truncated")
    require(source_lines[signature_line - 1].startswith(
        "unsafe fn bidirectional_merge<T: FreezeMarker, "
        "F: FnMut(&T, &T) -> bool>("),
        "bounded function signature/source location changed")
    require(source_lines[guard_line - 1] ==
            "        if left != left_end || right != right_end {",
            "short-circuit guard/source location changed")
    require(source_lines[guard_line] ==
            "            panic_on_ord_violation();",
            "real panic body/source location changed")
    require(source_lines[guard_line + 1] == "        }",
            "real panic body closing/source location changed")
    require(source_lines.count(
        "        if left != left_end || right != right_end {") == 1,
        "guard source spelling is not unique")
    print(f"MIR-OR-JOIN-LIVENESS exact source/profile admission passed: "
          f"{args.case}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"MIR-OR-JOIN-LIVENESS refusal: {exc}", file=sys.stderr)
        raise SystemExit(2)
