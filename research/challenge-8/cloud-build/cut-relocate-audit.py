#!/usr/bin/env python3
"""Source and proof-stage audit for the unaccepted CUT relocation TEST."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HEAD = "f76012fb518703b1d98e243ac4f487f16877cfcb"
TRACKED = ("src/verifast.ml", "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
           "src/rust_frontend/vf_mir_translator/rust_parser.ml",
           "src/rust_frontend/vf_mir/vf_mir.capnp")
BINARIES = ("bin/verifast", "bin/vf-rust-mir-exporter", "bin/refinement-checker",
            "bin/vf-cxx-ast-exporter", "bin/libz3.so")
CUT_PATHS = {"src/verifast.ml", "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"}
SOURCE_SHA = "66bf5a6edc0188f560e72ac5a6a5636f2dcda47c65aa295ac21008fc7702e2d8"
ORIGINAL_SHA = "9b41aef507c8c61ec786bfacc8e12ede656286213e393a0d07436a8879dc569e"
MIR_SHA = {"normal": "10356bf128753db09e17b968e859957121cb3f5a2684c3b608abd4152f150f76",
           "readonly": "9fdee7643ff66e8f3a12fc37b489100b7280ded0489a20ab1da11c67f24032c4"}
BASE_ERROR = ("verified/lib.rs(84,9-38): error: Strict lifetime binding "
              "has unresolved inference in entry outer type")
TRANSLATED_IDS_PATCH_SHA = "fa862fe86406d95eb921f2935b2e4f6cf048c5366ece8d8836e5fcd7b41a9145"
TRANSLATED_IDS_PATCH_NAME = "verifast-cut-relocate-translated-ids-TEST.patch"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(("git", "-C", str(root), *args))


def specs(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): sha(p.read_bytes())
            for p in sorted((root / "bin/rust").rglob("*.rsspec"))}


def snapshot(root: Path) -> dict:
    need(git(root, "rev-parse", "HEAD").strip().decode() == HEAD, "VeriFast source pin changed")
    return {"head": HEAD,
            "tracked": {p: sha((root / p).read_bytes()) for p in TRACKED},
            "binaries": {p: sha((root / p).read_bytes()) for p in BINARIES},
            "specs": specs(root),
            "diff_sha256": sha(git(root, "diff", "--binary", "HEAD")),
            "modified_files": git(root, "diff", "--name-only", "HEAD").decode().splitlines()}


def compare(prod: Path, moved: Path, stock: Path, before: Path,
            cut_verifast: Path, baseline: dict) -> dict:
    need(snapshot(prod) == baseline, "production source, specifications or binaries changed")
    need(git(moved, "rev-parse", "HEAD").strip().decode() == HEAD,
         "relocation source HEAD differs")
    before_translator = before.read_bytes()
    moved_translator = (moved / TRACKED[1]).read_bytes()
    need(moved_translator != before_translator, "relocation translator delta absent")
    need((moved / TRACKED[0]).read_bytes() == cut_verifast.read_bytes(),
         "relocation changed strict CUT kernel bytes")
    need((moved / TRACKED[0]).read_bytes() != (prod / TRACKED[0]).read_bytes(),
         "strict CUT kernel delta absent")
    for rel in TRACKED[2:]:
        need((moved / rel).read_bytes() == (prod / rel).read_bytes(),
             f"unexpected source delta: {rel}")
    need(specs(moved) == baseline["specs"], "effective specification inventory or bytes changed")
    for rel in BINARIES[1:]:
        need((moved / rel).read_bytes() == (prod / rel).read_bytes(), f"tool binary changed: {rel}")
        need((moved / rel).read_bytes() == (stock / rel).read_bytes(), f"tool binary differs from stock: {rel}")
    modified = set(git(moved, "diff", "--name-only", "HEAD").decode().splitlines())
    need(modified == set(baseline["modified_files"]) | CUT_PATHS,
         f"unexpected relocation source inventory: {sorted(modified)}")
    return {"production_unchanged": True, "specs_equal": True,
            "exporter_refiner_schema_equal": True,
            "relocation_only_translator": True, "cut_verifast_unchanged": True,
            "modified_files": sorted(modified),
            "production_console_sha256": baseline["binaries"]["bin/verifast"],
            "relocation_console_sha256": sha((moved / "bin/verifast").read_bytes()),
            "cut_before_relocation_translator_sha256": sha(before_translator),
            "relocated_translator_sha256": sha(moved_translator),
            "accepted": False}


def classify(capture: Path, raw_exit: int, source_audit: dict) -> dict:
    path = capture / "summary.json"
    report = json.loads(path.read_text()) if path.is_file() else {}
    proof_inputs = capture.parent / "required-proof-files-sha256.txt"
    input_rows = proof_inputs.read_text().splitlines() if proof_inputs.is_file() else []
    patch_pin = sum(row.startswith(TRANSLATED_IDS_PATCH_SHA + "  ") and
                    row.endswith("/" + TRANSLATED_IDS_PATCH_NAME)
                    for row in input_rows) == 1
    root = capture / "callback-positive"
    stages = report.get("stages", {})
    required = ("normal-export", "normal-decode", "readonly-export",
                "readonly-decode", "refinement")
    support = all(stages.get(s, {}).get("exit") == 0 for s in required)
    source_pair = (report.get("source_pair_exact_at_end") is True and
                   report.get("source_hashes") ==
                   {"verified/lib.rs": SOURCE_SHA, "original/lib.rs": ORIGINAL_SHA} and
                   sha((root / "verified/lib.rs").read_bytes()) == SOURCE_SHA and
                   sha((root / "original/lib.rs").read_bytes()) == ORIGINAL_SHA)
    body = report.get("body_admission") is True and report.get("body_hashes") == MIR_SHA
    mir = {mode: (root / f"{mode}-mir.txt").read_text(errors="replace")
           if (root / f"{mode}-mir.txt").is_file() else "" for mode in MIR_SHA}
    direct_continue = all("unwindAction = (continue = void)" in value for value in mir.values())
    baseline_log = (root / "baseline-verification.log").read_text(errors="replace") \
        if (root / "baseline-verification.log").is_file() else ""
    moved_log = (root / "relocated-verification.log").read_text(errors="replace") \
        if (root / "relocated-verification.log").is_file() else ""
    baseline_errors = [line for line in baseline_log.splitlines()
                       if ": error:" in line or line.startswith("Fatal error:")]
    baseline = (stages.get("baseline-verification", {}).get("exit") in (1, 2) and
                len(baseline_errors) == 1 and baseline_errors[0].startswith(BASE_ERROR) and
                baseline_log.count("Verifying function 'callback_positive'") == 1 and
                report.get("baseline_first_boundary_preserved") is True)
    moved_lines = [line for line in moved_log.splitlines() if "STRICT-RELOCATE inner=" in line]
    moved_ids = [re.search(r"STRICT-RELOCATE inner=(_\d+) translated=(\$_\d+) "
                           r"type=(.+) addresstaken=false$", line)
                 for line in moved_lines]
    ast_trace = (len(moved_ids) == 6 and all(moved_ids) and
                 {m.group(1) for m in moved_ids if m} == {f"_{n}" for n in range(27, 33)} and
                 all(m.group(2) == "$" + m.group(1) for m in moved_ids if m) and
                 moved_log.count("STRICT-RELOCATE outer_removed=6 inner_insertions=1") == 1 and
                 report.get("relocated_declaration_trace_six") is True and
                 report.get("relocated_exactly_one_inner_insertion") is True)
    entry = moved_log.count("Verifying function 'callback_positive'") == 1
    result_class = report.get("classification")
    diagnosed = result_class in ("FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY",
                                 "NEXT_PROOF_BLOCKER_DIAGNOSTIC_ONLY")
    if result_class == "FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY":
        diagnosed = (diagnosed and stages.get("relocated-verification", {}).get("exit") == 0 and
                     report.get("relocated_full_zero_errors") is True and
                     bool(report.get("relocated_verified_source_leak_checks")) and
                     not report.get("relocated_dead_code"))
    if result_class == "NEXT_PROOF_BLOCKER_DIAGNOSTIC_ONLY":
        diagnosed = (diagnosed and stages.get("relocated-verification", {}).get("exit") in (1, 2) and
                     bool(report.get("relocated_first_error")))
    matched = (raw_exit == 0 and patch_pin and support and source_pair and body and direct_continue and
               baseline and ast_trace and entry and diagnosed)
    return {"classification": result_class if matched else "INCONCLUSIVE",
            "accepted": False, "actual_sort4_proved": False,
            "raw_capture_exit": raw_exit, "source_audit": source_audit,
            "source_hashes": report.get("source_hashes"), "body_hashes": report.get("body_hashes"),
            "baseline_first_error": report.get("baseline_first_error"),
            "relocated_first_error": report.get("relocated_first_error"),
            "stage_exits": {k: v.get("exit") for k, v in stages.items()},
            "checks": {"translated_ids_patch_pin": patch_pin,
                       "support": support, "exact_source_pair": source_pair,
                       "complete_target_mir_pins": body, "direct_unwind_continue": direct_continue,
                       "baseline_boundary": baseline, "ast_six_removed_one_inserted": ast_trace,
                       "relocated_proof_entry": entry, "diagnostic_outcome": diagnosed},
            "unwind_storage_dead_assumed": False,
            "open_gates": ["all-path liveness", "alias/address escape", "heap and bound retention",
                           "source/MIR mutation negatives", "normal and unwind recovery review",
                           "combined S6 and no-cut regression", "actual sort4 admission"]}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("snapshot", "compare", "classify"))
    p.add_argument("--production-source", type=Path, required=True)
    p.add_argument("--snapshot", type=Path)
    p.add_argument("--relocation-source", type=Path)
    p.add_argument("--stock-home", type=Path)
    p.add_argument("--before-relocation", type=Path)
    p.add_argument("--cut-verifast", type=Path)
    p.add_argument("--capture", type=Path)
    p.add_argument("--raw-exit", type=int)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    if a.mode == "snapshot":
        result = snapshot(a.production_source)
    else:
        need(all((a.snapshot, a.relocation_source, a.stock_home,
                  a.before_relocation, a.cut_verifast)),
             "missing relocation comparison inputs")
        result = compare(a.production_source, a.relocation_source, a.stock_home,
                         a.before_relocation, a.cut_verifast,
                         json.loads(a.snapshot.read_text()))
        if a.mode == "classify":
            need(a.capture is not None and a.raw_exit is not None, "missing capture outcome")
            result = classify(a.capture, a.raw_exit, result)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if a.mode == "classify" and result["classification"] == "INCONCLUSIVE":
        raise SystemExit("CUT relocation diagnostic is inconclusive")


if __name__ == "__main__":
    main()
