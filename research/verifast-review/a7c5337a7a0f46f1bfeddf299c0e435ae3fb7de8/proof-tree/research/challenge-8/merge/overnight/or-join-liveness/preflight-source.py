#!/usr/bin/env python3
"""Extract the unchanged actual bounded case for seventh-profile admission.

The retained pointer-prove.read_cases owns extraction semantics. This tool
does not invoke a compiler, verifier, refiner, or proof classifier.
"""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--pointer-prove", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pin = json.loads(args.manifest.read_text(encoding="utf-8"))
    if pin.get("component") != "MIR-OR-JOIN-LIVENESS" or \
            pin.get("admission_state") != "EXPERIMENTAL_CLOUD_TRIAL":
        raise ValueError("seventh component has no exact Cloud trial admission")
    expected_fixture = pin.get("admitted_fixture_sha256")
    if not isinstance(expected_fixture, str) or len(expected_fixture) != 64:
        raise ValueError("no admitted exact bounded fixture hash")
    if digest(args.fixture) != expected_fixture:
        raise ValueError("bounded fixture hash mismatch")
    expected_harness = pin.get("retained_pointer_prove_sha256")
    if not isinstance(expected_harness, str) or len(expected_harness) != 64:
        raise ValueError("no admitted retained proof harness hash")
    if digest(args.pointer_prove) != expected_harness:
        raise ValueError("retained proof harness hash mismatch")
    if args.output.exists():
        raise ValueError("refusing to reuse seventh-profile preflight output")
    args.output.mkdir(parents=True)
    spec = importlib.util.spec_from_file_location(
        "or_join_retained_pointer_prove", args.pointer_prove)
    if spec is None or spec.loader is None:
        raise ValueError("retained pointer-prove loader is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest, _ = module.read_cases(
        args.fixture, args.output, ["bidirectional_merge_len23"])
    if manifest.get("case_order") != ["bidirectional_merge_len23"]:
        raise ValueError("bounded case extraction selected the wrong source")
    case = args.output / "bidirectional_merge_len23"
    expected_source = pin.get("admitted_source_sha256")
    if not isinstance(expected_source, str) or len(expected_source) != 64:
        raise ValueError("no admitted exact prepared source hash")
    if digest(case / "verified/lib.rs") != expected_source:
        raise ValueError("prepared verified source hash mismatch")
    signature_line = pin.get("admitted_signature_line")
    guard_line = pin.get("admitted_guard_line")
    if not isinstance(signature_line, int) or not isinstance(guard_line, int) or \
            signature_line < 1 or guard_line <= signature_line:
        raise ValueError("no exact signature/guard source location pins")
    lines = (case / "verified/lib.rs").read_text(encoding="utf-8").splitlines()
    if len(lines) < guard_line + 2 or not lines[signature_line - 1].startswith(
            "unsafe fn bidirectional_merge<T: FreezeMarker, F: FnMut(&T, &T) -> bool>(") or \
            lines[guard_line - 1] != "        if left != left_end || right != right_end {" or \
            lines[guard_line] != "            panic_on_ord_violation();" or \
            lines[guard_line + 1] != "        }" or \
            lines.count("        if left != left_end || right != right_end {") != 1:
        raise ValueError("exact bounded signature/guard/panic source changed")
    result = {
        "profile": "MIR-OR-JOIN-LIVENESS-EXPERIMENTAL",
        "fixture_sha256": digest(args.fixture),
        "retained_pointer_prove_sha256": digest(args.pointer_prove),
        "case": "bidirectional_merge_len23",
        "original_sha256": digest(case / "original/lib.rs"),
        "verified_sha256": digest(case / "verified/lib.rs"),
        "accepted": False,
    }
    (args.output / "or-join-preflight.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError, KeyError,
            json.JSONDecodeError) as exc:
        print(f"MIR-OR-JOIN-LIVENESS preflight refusal: {exc}",
              file=sys.stderr)
        raise SystemExit(2)
