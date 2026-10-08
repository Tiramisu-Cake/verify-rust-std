#!/usr/bin/env python3
"""Hosted-only source/ADT negatives for the local H2b certificate.

This runner never labels a Rust-source mutation as a typed-MIR mutation.
The separate H2c source-gate overlay is required for the attribute cases.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load():
    import importlib.util
    import sys
    path = HERE / "capture-guard-linkage.py"
    spec = importlib.util.spec_from_file_location("h2b_admission_link", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing local H2b linkage runner: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LINKAGE = load()
H2A = LINKAGE.H2A
H2B = LINKAGE.H2B
LINK = LINKAGE.LINK
REPO = LINKAGE.REPO
VARIANTS = (
    "positive", "repr_packed", "repr_c", "repr_align", "extra_field",
    "field_alias", "extra_ghost", "guard_cast_operand",
)
SOURCE_REASONS = {
    "repr_packed": "local guard unreviewed pre-ADT source",
    "repr_c": "local guard unreviewed pre-ADT source",
    "repr_align": "local guard unreviewed pre-ADT source",
    "field_alias": "local guard unreviewed pre-ADT source",
    "extra_field": "local guard exact source/ghost owner",
    "extra_ghost": "local guard exact source/ghost owner",
    "guard_cast_operand": "local guard exact source/ghost owner",
}


def once_replace(data: bytes, old: bytes, new: bytes) -> bytes:
    LINKAGE.require(data.count(old) == 1, f"mutation marker not unique: {old!r}")
    return data.replace(old, new, 1)


def fixture(method: bytes, struct_body: bytes, drop_body: bytes,
            variant: str) -> tuple[bytes, bytes]:
    LINKAGE.require(variant in VARIANTS, "unknown H2b admission variant")
    _, verified = LINKAGE.source_pair(method, struct_body, drop_body,
                                      "positive", template_active=True)
    if variant in ("repr_packed", "repr_c", "repr_align"):
        attr = {
            "repr_packed": b"#[repr(packed)]\n",
            "repr_c": b"#[repr(C)]\n",
            "repr_align": b"#[repr(align(16))]\n",
        }[variant]
        verified = once_replace(verified, b"struct DropOnPanic<T>",
                                attr + b"struct DropOnPanic<T>")
    elif variant == "extra_field":
        verified = once_replace(verified, b"inner: *mut T,",
                                b"inner: *mut T,\n        extra: (),")
        verified = once_replace(verified, b"DropOnPanic { inner: slot }",
                                b"DropOnPanic { inner: slot, extra: () }")
    elif variant == "field_alias":
        verified = once_replace(verified, b"struct DropOnPanic<T>",
                                b"type GuardPointer<T> = *mut T;\n"
                                b"struct DropOnPanic<T>")
        verified = once_replace(verified, b"inner: *mut T,",
                                b"inner: GuardPointer<T>,")
    elif variant == "extra_ghost":
        verified = once_replace(
            verified,
            b"//@ open <DropOnPanic<T>>.full_borrow_content(_t, self)();",
            b"//@ assert true;\n            "
            b"//@ open <DropOnPanic<T>>.full_borrow_content(_t, self)();")
    elif variant == "guard_cast_operand":
        verified = once_replace(
            verified, b"unsafe { self.inner.drop_in_place() }",
            b"unsafe { (self.inner as *mut T).drop_in_place() }")
    original = H2A.CONSTRUCTOR.strip_ghost_annotations(verified)
    LINKAGE.require(H2A.CONSTRUCTOR.strip_ghost_annotations(verified) == original
                    and original.count(b"struct DropOnPanic<T>") == 1
                    and original.count(LINKAGE.METHOD_SIGNATURE) == 1
                    and original.count(b"impl Drop for OrdinaryDrop") == 1,
                    "H2b admission fixture lost source identity or controls")
    return original, verified


def classify(case: Path, variant: str, stages: dict) -> dict:
    complete = all(stages.get(k, {}).get("exit") == 0 for k in (
        "normal-export", "normal-decode", "readonly-export", "readonly-decode",
        "refinement"))
    intact = all(s.get("source_unchanged") is True for s in stages.values())
    log_file = case / "full-verification.log"
    log = log_file.read_text(errors="replace") if log_file.exists() else ""
    errors = LINK.ERR.findall(log)
    fatal = [line for line in log.splitlines() if line.startswith("Fatal error:")]
    accepted = "SORT4-GENERIC-GUARD: source/MIR local link accepted" in log
    method_entry = "Verifying function 'sort4_checked_generic_drop'" in log
    guard_entry = "Verifying function '<DropOnPanic<T> as std::ops::Drop>::drop'" in log
    expected = SOURCE_REASONS.get(variant)
    classification = "INCONCLUSIVE"
    if variant == "positive":
        inherited = LINKAGE.classify(case, "positive", stages, True)
        if inherited["classification"] == "H2B_LOCAL_NOMINAL_DROP_CANDIDATE_PROVED":
            classification = "H2B_LOCAL_POSITIVE_PROVED"
    elif (complete and intact and stages.get("full-verification", {}).get("exit") == 2
          and len(fatal) == 1 and not errors and not accepted
          and not method_entry and not guard_entry and expected is not None
          and fatal[0] == 'Fatal error: exception Failure("SORT4-GENERIC-GUARD: certificate mismatch: '
                          + expected + '")'):
        classification = "EXACT_SOURCE_ADMISSION_REJECTED"
    result = {
        "variant": variant, "classification": classification,
        "component_accepted": False, "actual_nested_drop_proved": False,
        "typed_mir_mutation": False, "expected_source_rejection": expected,
        "frontend_refinement": complete, "source_integrity": intact,
        "full_verifier_exit": stages.get("full-verification", {}).get("exit"),
        "first_error": errors[0] if errors else None, "fatal": fatal,
        "gate_accepted": accepted, "method_entered": method_entry,
        "guard_entered": guard_entry, "stages": stages,
    }
    LINK.write_json(case / "admission-classification.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--guard-root", type=Path, required=True)
    parser.add_argument("--template-root", type=Path, required=True)
    parser.add_argument("--variants", nargs="+", choices=VARIANTS,
                        default=list(VARIANTS))
    args = parser.parse_args()
    LINKAGE.require(os.environ.get("GITHUB_ACTIONS") == "true" and
                    os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
                    os.environ.get("RUNNER_OS") == "Linux",
                    "GitHub-hosted Linux required")
    LINKAGE.require(args.guard_root.resolve() == REPO and
                    args.template_root.resolve() == REPO,
                    "H2a and H2b roots must be the same exact repository")
    evidence = args.evidence.resolve()
    LINKAGE.require(not evidence.exists(), f"refusing overwrite: {evidence}")
    evidence.mkdir(parents=True)
    os.environ["SORT4_GUARD_REPO_ROOT"] = str(REPO)
    os.environ["SORT4_GUARD_TEMPLATE_REPO_ROOT"] = str(REPO)
    method_body, method_cert = H2A.source_certificate()
    struct_body, drop_body, guard_cert = H2B.source_certificate()
    method = LINKAGE.checked_method(method_body)
    cert = {"generic_method": method_cert, "guard": guard_cert,
            "local_method_sha256": LINK.sha(method),
            "actual_nested_drop_proved": False,
            "admission_overlay": "H2c pre-ADT source check required"}
    LINK.write_json(evidence / "source-certificate.json", cert)
    results = []
    for variant in args.variants:
        case = evidence / variant
        case.mkdir()
        (case / "original").mkdir()
        (case / "verified").mkdir()
        original, verified = fixture(method, struct_body, drop_body, variant)
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        LINK.write_json(case / "fixture.json", {
            "variant": variant, "source_certificate": cert,
            "original_sha256": LINK.sha(original),
            "verified_sha256": LINK.sha(verified),
            "ghost_strip_identity":
                H2A.CONSTRUCTOR.strip_ghost_annotations(verified) == original,
            "same_unit_ordinary_drop": True,
            "actual_nested_drop_proved": False,
            "typed_mir_mutation": False,
        })
        results.append(classify(case, variant, H2A.run_case(case, args)))
    LINK.write_json(evidence / "summary.json", {
        "classification": "H2B_SOURCE_ADMISSION_DIAGNOSTIC_ONLY",
        "component_accepted": False, "actual_nested_drop_proved": False,
        "typed_mir_mutation_coverage": False,
        "source_certificate": cert, "results": results,
    })


if __name__ == "__main__":
    main()
