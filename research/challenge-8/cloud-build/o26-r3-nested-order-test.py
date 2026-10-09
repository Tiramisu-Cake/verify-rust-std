#!/usr/bin/env python3
"""Cloud-only R3 declaration-scheduling TEST; no production proof acceptance."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
from types import SimpleNamespace


ROOT = Path("research/challenge-8")
MANIFEST = ROOT / "overnight-assume-actual/O26-R3-NESTED-BEFORE-OUTER-TEST.json"
TRANSLATOR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
PAIR = ("SORT4_R3_NESTED_ORDER_TEST_REPO_ROOT", "SORT4_R3_NESTED_ORDER_TEST")
CASE = "nine-body-wrapper-input-relation"
SOURCE = "a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463"
ORIGINAL = "466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5"
UNIT = "407acbaea262ba908ed88434231e9fce1128678840f5d929deaad71838290a92"
BODY8 = "e0508d6cfb436bc1bcd04737ad74e37b357d17e9ec3c2a226ee961f7036eae9a"
R3_TRANSLATOR = "34a03879b45377570eab81ee384ade01ebea9d5d216eb6223c6c742c5819dc15"
R3_PATCH = "da62de4fe2a166e15e298d7a8f333e6524267392f36e3c196b81726299a47f8a"
TEST_TRANSLATOR = "85962191c8613fbddae4931f65e32da06abca3df158d0dcb92cc21c4411986a6"
TEST_PATCH = "d7712df4a72167b3ac55f611e693176a065051de95ba85123a859373ed0b1e26"
MARK = "SORT4-R3-NESTED-BEFORE-OUTER-TEST:"
NAMES = (
    "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
    "sort4_checked_as_mut_ptr", "sort4_checked_pointer_drop",
    "sort4_checked_generic_drop", "checked_transmute_neo_pointer",
    "checked_assume_init_pointer", "checked_forget_owned",
    "select_unpredictable",
    "<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop",
)
ROW = re.compile(re.escape(MARK) +
                 r" (before|after)\[(\d+)\] body_name=(.*?) module=(.*?) "
                 r"fn=(.*?) type=FuncBody loc=(\S+) ast_sha256=([0-9a-f]{64})")
SUMMARY = re.compile(re.escape(MARK) +
                     r" exact nine-body one-item permutation, signatures=(\d+) "
                     r"signatures_sha256_before=([0-9a-f]{64}) "
                     r"signatures_sha256_after=([0-9a-f]{64}) "
                     r"and prior predicates/ghosts unchanged")
ERROR = re.compile(r"(?m)^.*: error: .*|^Error:.*$|^Fatal error:.*$")


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(path: Path) -> str:
    need(path.is_file(), f"missing TEST artifact: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> dict:
    need(path.is_file(), f"missing TEST JSON: {path}")
    return json.loads(path.read_text())


def write(path: Path, row: dict) -> None:
    path.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"module unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def modules(a):
    r2 = load("o26_r3_nested_r2", a.cloud_dir / "o26-wrapper-profile.py")
    r3 = load("o26_r3_nested_r3", a.cloud_dir / "o26-r3-profile.py")
    return r2, r3


def certificate(a) -> dict:
    m = read(a.proof_root / MANIFEST)
    parent = read(a.proof_root / ROOT /
                  "overnight-assume-actual/O26-WRAPPER-INPUT-RELATION-PROFILE.json")
    need(m.get("classification") ==
         "EXPERIMENTAL_O26_R3_NESTED_BEFORE_OUTER_TEST_NOT_ACCEPTED" and
         parent.get("classification") ==
         "EXPERIMENTAL_O26_WRAPPER_INPUT_RELATION_COMPONENT24_NOT_ACCEPTED" and
         m.get("parent_profile") ==
         "overnight-assume-actual/O26-WRAPPER-INPUT-RELATION-PROFILE.json" and
         m.get("parent_translator_sha256") ==
         parent.get("new_translator_sha256") == R3_TRANSLATOR and
         parent.get("component24_patch_sha256") == R3_PATCH and
         m.get("test_patch") ==
         "overnight-assume-actual/verifast-r3-nested-before-outer-TEST.patch" and
         m.get("test_patch_sha256") == TEST_PATCH and
         m.get("test_translator_sha256") == TEST_TRANSLATOR and
         m.get("source") == {
             "verified_sha256": SOURCE, "original_sha256": ORIGINAL,
             "unit_sha256": UNIT,
             "nested_body8_sha256": BODY8,
         } and
         parent["source"]["unit_sha256"] == UNIT and
         parent["source"]["body_sha256"][8] == BODY8 and
         parent["source"]["verified_sha256"] == SOURCE and
         parent["source"]["original_sha256"] == ORIGINAL and
         m.get("opt_in") == {PAIR[0]: "exact proof root", PAIR[1]: "1"} and
         m.get("source_runtime_spec_kernel_parser_exporter_refiner_modified") is False and
         m.get("mutation_controls_complete") is False and
         m.get("actual_nested_drop_credit") is False and
         m.get("verification_accepted") is False and m.get("accepted") is False,
         "R3 nested-order TEST manifest differs")
    need(sha(a.proof_root / ROOT / m["test_patch"]) == TEST_PATCH and
         sha(a.proof_root / ROOT / parent["component24_patch"]) == R3_PATCH and
         sha(a.r3_source / TRANSLATOR) == R3_TRANSLATOR,
         "R3 nested-order patch or parent translator changed")
    captured = read(a.r3_evidence / "capture-check.json")
    capture_summary = read(a.r3_evidence / "capture/summary.json")
    snapshot = read(a.r3_evidence / "tool-identity.json")
    r2, _ = modules(a)
    current = r2.tool_snapshot(a.r3_source, a.proof_root)
    case = a.r3_evidence / "capture" / CASE
    need(captured.get("classification") ==
         "R3_SOURCE_MIR_GRAPH_PINNED_DIAGNOSTIC" and
         captured.get("normal_readonly_refinement_complete") is True and
         captured.get("all_nine_body_records_and_ten_marshal_files_hashed") is True and
         captured.get("typed_outer_mir_exact") is True and
         captured.get("accepted") is False and
         snapshot.get("r3") == current and
         sha(case / "verified/lib.rs") == SOURCE and
         sha(case / "original/lib.rs") == ORIGINAL and
         sha(case / "normal-mir.txt") ==
         parent["observed_capture"]["normal_whole_decoded_mir_sha256"] and
         sha(case / "readonly-mir.txt") ==
         parent["observed_capture"]["readonly_whole_decoded_mir_sha256"],
         "R3 same-source full MIR/refinement or tool certificate absent")
    snapshots = capture_summary.get("fingerprint", {}).get("snapshots", {})
    expected = {"unit": UNIT,
                **{f"body-{i}": value
                   for i, value in enumerate(parent["source"]["body_sha256"])}}
    need(set(snapshots) == set(expected) and
         all(snapshots[label].get("file") ==
             f"actual-nested-9-{label}.marshal" and
             sha(case / snapshots[label]["file"]) ==
             snapshots[label].get("sha256") == digest
             for label, digest in expected.items()),
         "R3 ten Marshal snapshots changed after capture")
    for mode in ("normal", "readonly"):
        rows = capture_summary.get("full_body_capture", {}).get(mode, {}).get("bodies", [])
        need(len(rows) == 9 and
             all(row.get("index") == i and
                 row.get("file") == f"{mode}-body-{i}-full-mir.txt" and
                 sha(case / row["file"]) == row.get("sha256")
                 for i, row in enumerate(rows)),
             f"R3 {mode} nine body texts changed after capture")
    return {"classification": "R3_NESTED_ORDER_INPUT_PINNED",
            "manifest": m, "parent_profile_sha256":
            sha(a.proof_root / ROOT / m["parent_profile"]),
            "r3_snapshot": current,
            "r3_capture_check_sha256": sha(a.r3_evidence / "capture-check.json"),
            "source_sha256": SOURCE, "original_sha256": ORIGINAL,
            "verification_accepted": False, "accepted": False}


def test_identity(a, save: bool = True) -> dict:
    baseline = read(a.evidence / "input-certificate.json")["r3_snapshot"]
    r2, _ = modules(a)
    need(r2.tool_snapshot(a.r3_source, a.proof_root) == baseline,
         "R3 parent tool changed during TEST")
    test = r2.tool_snapshot(a.test_source, a.proof_root)
    need(test["head"] == baseline["head"] and
         test["effective_rsspec_sha256"] ==
         baseline["effective_rsspec_sha256"] and
         test["proof_std_sha256"] == baseline["proof_std_sha256"] and
         set(test["modified_tracked_source_sha256"]) ==
         set(baseline["modified_tracked_source_sha256"]) and
         all(test["modified_tracked_source_sha256"][k] ==
             baseline["modified_tracked_source_sha256"][k]
             for k in baseline["modified_tracked_source_sha256"]
             if k != str(TRANSLATOR)) and
         all(test["critical_source_sha256"][k] ==
             baseline["critical_source_sha256"][k]
             for k in baseline["critical_source_sha256"]
             if k != str(TRANSLATOR)) and
         all(test["binary_sha256"][k] == baseline["binary_sha256"][k]
             for k in baseline["binary_sha256"] if k != "bin/verifast") and
         test["critical_source_sha256"][str(TRANSLATOR)] ==
         TEST_TRANSLATOR and
         test["modified_tracked_source_sha256"][str(TRANSLATOR)] ==
         TEST_TRANSLATOR and
         test["binary_sha256"]["bin/verifast"] !=
         baseline["binary_sha256"]["bin/verifast"],
         "scheduled TEST changed kernel/spec/parser/exporter/refiner or other source")
    result = {"classification": "R3_NESTED_ORDER_TRANSLATOR_CONSOLE_ONLY",
              "parent": baseline, "test": test,
              "test_patch_sha256": TEST_PATCH,
              "verification_accepted": False, "accepted": False}
    if save:
        write(a.evidence / "test-tool-identity.json", result)
    return result


def proof(a) -> dict:
    need(read(a.evidence / "test-tool-identity.json").get("classification") ==
         "R3_NESTED_ORDER_TRANSLATOR_CONSOLE_ONLY", "TEST tool absent")
    need(not any(os.environ.get(k) for k in PAIR),
         "inherited scheduling TEST opt-in forbidden")
    _, r3 = modules(a)
    source_case = a.r3_evidence / "capture" / CASE
    case = a.evidence / "case"
    need(not case.exists(), "TEST source case already exists")
    shutil.copytree(source_case, case, symlinks=False)
    need(sha(case / "verified/lib.rs") == SOURCE and
         sha(case / "original/lib.rs") == ORIGINAL,
         "TEST case changed R3 source bytes")
    args = SimpleNamespace(proof_root=a.proof_root, cloud_dir=a.cloud_dir,
                           schema=a.test_source /
                           "src/rust_frontend/vf_mir/vf_mir.capnp",
                           compiler_sysroot=a.compiler_sysroot,
                           deadline_epoch=a.deadline_epoch)
    os.environ[PAIR[0]] = str(a.proof_root)
    os.environ[PAIR[1]] = "1"
    try:
        stage = r3.proof_stage(args, case, a.test_source,
                               "r3-nested-before-outer", True)
    finally:
        for key in PAIR:
            os.environ.pop(key, None)
    result = {"classification": "R3_NESTED_ORDER_FULL_PROOF_RAN",
              "stage": stage, "source_sha256": SOURCE,
              "verification_accepted": False, "accepted": False}
    write(a.evidence / "proof-stage.json", result)
    proof_log = (case / "r3-nested-before-outer.log").read_text(errors="replace")
    print("R3 NESTED FULL PROOF LOG BEGIN", flush=True)
    print(proof_log, end="" if proof_log.endswith("\n") else "\n", flush=True)
    print("R3 NESTED FULL PROOF LOG END", flush=True)
    return result


def inventory(text: str) -> dict:
    rows = {"before": {}, "after": {}}
    for phase, number, body_name, module, name, loc, digest in ROW.findall(text):
        index = int(number)
        need(index in range(9) and index not in rows[phase],
             "duplicate or out-of-range AST declaration inventory")
        rows[phase][index] = (body_name, module, name, loc, digest)
    summary = SUMMARY.findall(text)
    need(len(summary) == 1 and summary[0][0] == "3" and
         summary[0][1] == summary[0][2] and
         all(set(rows[k]) == set(range(9)) for k in rows) and
         [rows["before"][i][0] for i in range(9)] == list(NAMES) and
         [rows["after"][i][0] for i in range(9)] ==
         list(NAMES[:7]) + [NAMES[8], NAMES[7]] and
         sorted(rows["before"].values()) == sorted(rows["after"].values()),
         "R3 AST function/signature permutation certificate incomplete")
    return {"rows": rows, "signature_count": 3,
            "signature_ast_sha256_before": summary[0][1],
            "signature_ast_sha256_after": summary[0][2],
            "exact_one_item_multiset": True}


def artifacts(root: Path, paths: list[Path]) -> dict:
    result = {}
    for path in paths:
        need(path.is_relative_to(root) and path.is_file() and
             path.stat().st_size > 0, f"missing TEST evidence: {path}")
        result[str(path.relative_to(root))] = {
            "sha256": sha(path), "bytes": path.stat().st_size}
    need(len(result) == len(paths), "duplicate TEST artifact")
    return result


def audit(a) -> dict:
    e = a.evidence
    source = read(e / "input-certificate.json")
    identity = read(e / "test-tool-identity.json")
    final = read(e / "test-tool-identity-after.json")
    proof_result = read(e / "proof-stage.json")
    stage = proof_result.get("stage", {})
    case = e / "case"
    log_path = case / "r3-nested-before-outer.log"
    text = log_path.read_text(errors="replace")
    rows = inventory(text)
    headers = [text.find("Verifying function '" + name + "'") for name in NAMES]
    outer = headers[7]
    nested = headers[8]
    before_outer = text[:outer] if outer >= 0 else text
    nested_stop = text.find("Function 'select_unpredictable':", nested)
    if nested_stop < 0:
        nested_stop = outer
    nested_segment = text[nested:nested_stop]
    nested_return_leak = (
        nested_stop > nested >= 0 and
        nested_segment.count("Executing return statement") == 2 and
        nested_segment.count("Leak check.") == 2 and
        nested_segment.count("Consuming function lifetime token") == 2 and
        nested_segment.count("Freeing locals.") == 2 and
        "verified/lib.rs(169,33-48): Verifying call" in nested_segment)
    all_errors = ERROR.findall(text)
    proof_complete = (
        stage.get("status") == "RAN" and stage.get("exit") in (0, 1, 2) and
        stage.get("source_unchanged") is True and
        stage.get("source_before") == stage.get("source_after") and
        stage.get("source_before", {}).get("verified/lib.rs") == SOURCE and
        stage.get("source_before", {}).get("original/lib.rs") == ORIGINAL and
        stage.get("intrinsic_gate_active") is True and
        stage.get("pointer_drop_gate_active") is True and
        all(p >= 0 for p in headers) and
        headers[:7] == sorted(headers[:7]) and
        headers[6] < nested < outer and
        ERROR.search(before_outer) is None and
        nested_return_leak and
        (not all_errors if stage.get("exit") == 0 else
         len(all_errors) == 1 and ": error:" in all_errors[0]))
    need(a.runner_exit == 0 and
         source.get("classification") == "R3_NESTED_ORDER_INPUT_PINNED" and
         identity.get("classification") ==
         "R3_NESTED_ORDER_TRANSLATOR_CONSOLE_ONLY" and
         identity == final and
         proof_result.get("classification") ==
         "R3_NESTED_ORDER_FULL_PROOF_RAN" and
         sha(case / "verified/lib.rs") == SOURCE and
         sha(case / "original/lib.rs") == ORIGINAL and
         proof_complete,
         "R3 scheduled nested full normal/unwind return/leak proof boundary incomplete")
    paths = [e / name for name in (
        "input-certificate.json", "test-tool-identity.json",
        "test-tool-identity-after.json", "proof-stage.json",
        "test-patch.patch", "test-console-build.log", "test-console-ldd.txt")]
    paths += [case / name for name in (
        "verified/lib.rs", "original/lib.rs", "normal-mir.bin",
        "normal-mir.txt", "readonly-mir.bin", "readonly-mir.txt",
        "capture-summary.json", "r3-nested-before-outer.log")]
    paths += [case / f"{mode}-body-{i}-full-mir.txt"
              for mode in ("normal", "readonly") for i in range(9)]
    paths += [case / f"actual-nested-9-{label}.marshal"
              for label in ("unit", *(f"body-{i}" for i in range(9)))]
    return {"classification": "R3_NESTED_ORDER_TEST_DIAGNOSTIC_COMPLETE",
            "diagnostic_complete": True,
            "nested_normal_unwind_return_leak_log_observed": True,
            "seven_prefix_then_nested_then_outer": True,
            "ast_inventory": rows, "proof_exit": stage["exit"],
            "first_source_error_after_outer": all_errors[0]
            if all_errors else None,
            "mutation_controls_complete": False,
            "actual_nested_drop_credit": False,
            "actual_helper_proved": False,
            "verification_accepted": False, "accepted": False,
            "artifacts": artifacts(e, paths),
            "open_gates": ["source/unit/body and AST corruption controls",
                           "production declaration-scheduling admissibility",
                           "outer full normal/unwind/leak/resource proof"]}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("preflight", "test-identity", "proof",
                                    "final-identity", "audit"))
    for name in ("proof-root", "cloud-dir", "r3-source", "test-source",
                 "r3-evidence", "evidence", "compiler-sysroot"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--deadline-epoch", type=int, required=True)
    p.add_argument("--runner-exit", type=int, default=0)
    p.add_argument("--failed-stage", default="complete")
    a = p.parse_args()
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         not os.environ.get("GITHUB_ACTIONS"), "Cloud Build required")
    if a.mode == "preflight":
        write(a.evidence / "input-certificate.json", certificate(a))
    elif a.mode == "test-identity":
        test_identity(a)
    elif a.mode == "proof":
        proof(a)
    elif a.mode == "final-identity":
        current = test_identity(a, save=False)
        need(current == read(a.evidence / "test-tool-identity.json"),
             "TEST tool changed during proof")
        write(a.evidence / "test-tool-identity-after.json", current)
    else:
        try:
            result = audit(a)
        except Exception as exc:
            result = {"classification": "INCONCLUSIVE",
                      "diagnostic_complete": False,
                      "reason": str(exc),
                      "runner_exit": a.runner_exit,
                      "failed_stage": a.failed_stage,
                      "mutation_controls_complete": False,
                      "actual_nested_drop_credit": False,
                      "verification_accepted": False, "accepted": False}
        write(a.evidence / "diagnostic-audit.json", result)
        if result["classification"] == "INCONCLUSIVE":
            raise SystemExit("R3 nested-order TEST inconclusive: " + result["reason"])


if __name__ == "__main__":
    main()
