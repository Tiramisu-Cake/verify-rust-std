#!/usr/bin/env python3
"""Fail-closed Cloud discovery audit for the isolated strictCUT control matrix."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess


BASE_CAPTURE_SHA = "01422a459e82a29dd962e28e2b0984cb073efff5886d32cc1884d7b5895e7f34"
TEMPLATE_SHA = "7cb5c8a8a2541da30af188c8731ee13276c59b206e5ed58a78e909852719359e"
PATCHES = {
    "verifast-strict-lft-cut-26.10.patch": "d557082b0c17771acd7386ad6caca7bc139877cf1ca513d9570da210b1b542d8",
    "verifast-cut-relocate-callback-TESTONLY.patch": "e7189430eca9a48ed49d280131bd22987af8d05ed43a88f9c4a5c9767e57bb9e",
    "verifast-cut-relocate-translated-ids-TEST.patch": "fa862fe86406d95eb921f2935b2e4f6cf048c5366ece8d8836e5fcd7b41a9145",
}
POSITIVES = ("positive_basic", "ordinary_unmarked", "positive_early_return",
             "positive_direct_unwind")
NEGATIVES = (
    "negative_wrong_marker", "negative_duplicate_marker",
    "negative_marker_outside_binding", "negative_unknown_binding",
    "negative_nested_marker", "negative_malformed_marker",
    "negative_type_name_after_cut", "negative_type_argument_after_cut",
    "negative_typed_chunk_survives_cut", "negative_unclosed_fractional_access",
    "negative_reserved_half_after_lifetime_end", "negative_end_lifetime_twice",
)
CASES = POSITIVES + NEGATIVES
STAGE_SUPPORT = ("normal-export", "normal-decode", "readonly-export",
                 "readonly-decode", "refinement")
ERROR = re.compile(r"(?m)^(?:[^\n]*: error:.*|Fatal error:.*)$")
LOCATION = re.compile(r"^verified/lib\.rs\(([^)]+)\): error:")
BOUNDARY = {
    "negative_wrong_marker": ("marker enclosure", "end_lft_binding needs one enclosing ghost block containing only its let_lft declaration"),
    "negative_duplicate_marker": ("unique marker", "Strict lifetime binding expects exactly one cut marker per body"),
    "negative_marker_outside_binding": ("marker enclosure", "end_lft_binding needs one enclosing ghost block containing only its let_lft declaration"),
    "negative_unknown_binding": ("marker enclosure", "end_lft_binding needs one enclosing ghost block containing only its let_lft declaration"),
    "negative_nested_marker": ("marker enclosure", "end_lft_binding needs one enclosing ghost block containing only its let_lft declaration"),
    "negative_malformed_marker": ("marker syntax", "end_lft_binding expects exactly one named lifetime type and no arguments"),
    "negative_type_name_after_cut": ("type scope", "cmp"),
    "negative_type_argument_after_cut": ("type scope", "cmp"),
    "negative_typed_chunk_survives_cut": ("live typed heap chunk", "A lifetime-scoped heap chunk is still live at the binding end"),
    "negative_unclosed_fractional_access": ("remaining lifetime token", "lifetime_token"),
    "negative_reserved_half_after_lifetime_end": ("remaining lifetime token", "lifetime_token"),
    "negative_end_lifetime_twice": ("remaining lifetime token", "lifetime_token"),
}
OPEN_GATES = (
    "false normal-post and false unwind-post negatives",
    "incoming CFG edge and source-position mutation negatives",
    "renewed StorageLive and all-path liveness",
    "alias/address escape and pointer provenance",
    "outer-variable, nested-bound, and hidden heap-term retention",
    "heap ownership and bound retention for actual sort4",
    "combined S6 and no-cut regression",
    "actual sort4 AST scope and full source admission",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def need(value: bool, why: str) -> None:
    if not value:
        raise RuntimeError(why)


def load(path: Path) -> dict:
    need(path.is_file(), f"missing {path}")
    return json.loads(path.read_text())


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(("git", "-C", str(root), *args))


def relocation_module(cloud_dir: Path):
    spec = importlib.util.spec_from_file_location(
        "strict_cut_prior_audit", cloud_dir / "cut-relocate-audit.py")
    need(spec is not None and spec.loader is not None, "missing relocation audit module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def capture_module(proof_root: Path):
    spec = importlib.util.spec_from_file_location(
        "strict_cut_matrix_source",
        proof_root / "research/challenge-8/overnight-lifetime/capture.py")
    need(spec is not None and spec.loader is not None, "missing matrix capture module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight(a, overlaid: bool = False) -> dict:
    prior = a.relocation_evidence
    proof = a.proof_root / "research/challenge-8/overnight-lifetime"
    if not overlaid:
        need(sha(proof / "capture.py") == BASE_CAPTURE_SHA,
             "capture.py no longer has frozen pre-overlay bytes")
    need(sha(proof / "cases.rs") == TEMPLATE_SHA, "matrix template pin changed")
    for name, digest in PATCHES.items():
        need(sha(proof / name) == digest, f"patch pin changed: {name}")
    need(git(a.production_source, "diff", "--binary", "HEAD") ==
         a.production_applied_patch.read_bytes(), "production diff changed")
    baseline = load(prior / "production-snapshot.json")
    source_audit = load(prior / "source-audit.json")
    diagnostic = load(prior / "diagnostic-audit.json")
    module = relocation_module(a.cloud_dir)
    current = module.compare(
        a.production_source, a.relocation_source, a.stock_home,
        prior / "cut-translator-before-relocation.ml",
        prior / "cut-verifast-before-relocation.ml", baseline)
    need(current == source_audit == diagnostic.get("source_audit"),
         "current isolated tool differs from audited relocation tool")
    need(module.classify(prior / "relocation", 0, current) == diagnostic,
         "prior F-bound proof artifacts no longer match their audit")
    need(git(a.relocation_source, "diff", "--binary", "HEAD") ==
         (prior / "relocation-applied.patch").read_bytes(),
         "isolated relocation patch changed")
    need(diagnostic.get("classification") == "FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY" and
         diagnostic.get("raw_capture_exit") == 0 and
         diagnostic.get("accepted") is False and
         all(diagnostic.get("checks", {}).values()),
         "same-build distinct F-bound diagnostic did not reach full VF0")
    need(load(prior / "relocation/summary.json").get("classification") ==
         "FIXTURE_FULL_VF0_DIAGNOSTIC_ONLY", "prior relocated proof changed")
    need((prior / "raw-capture-exit-code.txt").read_text().strip() == "0",
         "prior relocation capture exit changed")
    need(sha(a.relocation_source / "bin/verifast") ==
         source_audit["relocation_console_sha256"], "isolated console bytes changed")
    manifest = load(prior / "provider-overlay-manifest.json")
    need(manifest.get("guard_only") is True and
         manifest.get("path") ==
         "research/challenge-8/overnight-lifetime/capture-relocate.py" and
         manifest.get("base_sha256") ==
         "31fc83eea22c92ee73b1fc17a79f24ca057c343fbca2699673b4a6bc5c93bb10" and
         manifest.get("provider_sha256") == sha(a.cloud_dir / "provider.py"),
         "prior provider overlay is not guard-only")
    return {"classification": "STRICT_CUT_PREFLIGHT_COMPLETE",
            "production_unchanged": True, "isolated_tool_unchanged": True,
            "patch_chain_pinned": True, "distinct_f_bound_full_vf0": True,
            "prior_relocation_classification": diagnostic["classification"],
            "relocation_console_sha256": source_audit["relocation_console_sha256"],
            "matrix_template_sha256": TEMPLATE_SHA, "accepted": False}


def read_case(a, case: str, opt_in: bool) -> dict:
    key = case if opt_in else "opt-in-absent"
    run_dir = a.evidence / "cases" / key
    inner = run_dir / (case if opt_in else case + "-without-opt-in")
    report = load(inner / "result.json")
    summary = load(run_dir / "summary.json")
    need(len(summary.get("cases", [])) == 1 and summary["cases"][0] == report,
         f"{key}: capture summary differs from case")
    need(report.get("case") == case and report.get("strict_lifetime_opt_in") is opt_in,
         f"{key}: wrong case or opt-in mode")
    need(report.get("accepted") is False and
         report.get("source_strip_identity") is True, f"{key}: source audit failed")
    source_hashes = report.get("source_hashes", {})
    need(set(source_hashes) == {"verified/lib.rs", "original/lib.rs"},
         f"{key}: source pair inventory changed")
    for rel, expected in source_hashes.items():
        need(sha(inner / rel) == expected, f"{key}: source pair changed")
    source_module = capture_module(a.proof_root)
    selected = source_module.select_case(
        (a.proof_root / "research/challenge-8/overnight-lifetime/cases.rs").read_bytes(),
        case)
    need(selected == (inner / "verified/lib.rs").read_bytes() and
         source_module.strip_ghost(selected) == (inner / "original/lib.rs").read_bytes(),
         f"{key}: selected source or ghost-strip relation changed")
    stages = report.get("stages", {})
    stage_exits = {name: row.get("exit") for name, row in stages.items()}
    need(all(stage_exits.get(s) == 0 and stages[s].get("source_exact") is True
             for s in STAGE_SUPPORT), f"{key}: export/decode/refinement failed")
    need(report.get("decoded_body_inventory_ok") is True,
         f"{key}: target body admission failed")
    mir = {}
    target = case
    for mode in ("normal", "readonly"):
        inventory = report["decoded_body_inventory"].get(mode, {})
        mir_bin = inner / f"{mode}-mir.bin"
        mir_txt = inner / f"{mode}-mir.txt"
        need(mir_bin.is_file() and mir_bin.stat().st_size > 0 and
             mir_txt.is_file() and mir_txt.stat().st_size > 0,
             f"{key}: incomplete full {mode} MIR")
        full = mir_txt.read_text(errors="replace")
        need(sha(mir_txt) == inventory.get("full_decoded_sha256") and
             len(mir_txt.read_bytes()) == inventory.get("full_decoded_bytes") and
             inventory.get("target_count") == 1 and
             inventory.get("source_path_present") is True and
             inventory.get("ghost_decl_block_present") is True and
             full.count(f'defPath = "{target}"') == 1 and
             inventory.get("same_unit_callee_count") ==
             (1 if case == "positive_direct_unwind" else 0),
             f"{key}: full {mode} MIR inventory changed")
        mir[mode] = {"bin_sha256": sha(mir_bin), "full_text_sha256": sha(mir_txt),
                     "target_body_sha256": inventory.get("target_body_sha256"),
                     "bytes": mir_txt.stat().st_size}
        if case == "positive_direct_unwind":
            need('name = "cut_maybe_unwind"' in full and
                 "unwindAction = (continue = void)" in full,
                 f"{key}: direct Continue missing in {mode} MIR")
    log = (inner / "full-verification.log").read_text(errors="replace")
    errors = ERROR.findall(log)
    need(errors == report.get("full_error_lines"), f"{key}: error inventory changed")
    target_header = f"Verifying function '{target}'"
    need(log.count(target_header) == report.get("target_headers"),
         f"{key}: target header count changed")
    if case == "positive_direct_unwind":
        callee_header = "Verifying function 'cut_maybe_unwind'"
        need(log.count(callee_header) == 1 and log.count(target_header) == 1 and
             log.index(callee_header) < log.index(target_header),
             "direct unwind callee proof must precede target proof")
    code = stage_exits.get("full-verification")
    if opt_in and case in POSITIVES:
        need(code == 0 and not errors and report.get("target_headers") == 1 and
             report.get("classification") == "POSITIVE_CANDIDATE_REVIEW_REQUIRED",
             f"{key}: positive did not prove")
    elif opt_in:
        need(code in (1, 2) and len(errors) == 1 and
             report.get("classification") ==
             "INTENDED_NEGATIVE_CANDIDATE_REVIEW_REQUIRED",
             f"{key}: negative missed reviewed candidate predicate")
        obligation, predicate = BOUNDARY[case]
        need(predicate in errors[0], f"{key}: wrong first proof obligation")
        if obligation == "type scope":
            need(any(word in errors[0].lower() for word in
                     ("no such", "unknown", "unbound", "not in scope", "undeclared")),
                 f"{key}: wrong type-scope error")
        if obligation == "remaining lifetime token":
            need("No matching" in errors[0], f"{key}: wrong lifetime-token error")
    else:
        need(code in (1, 2) and len(errors) == 1 and
             "Strict lifetime binding requires explicit overnight opt-in" in errors[0] and
             report.get("classification") ==
             "OPT_IN_ABSENT_INTENDED_REJECTION_CANDIDATE",
             "opt-in-absent rejection missed")
    source_match = LOCATION.match(errors[0]) if errors else None
    location = source_match.group(1) if source_match else None
    error_location = f"verified/lib.rs({location})" if location else None
    caller_note_location = None
    if opt_in and case == "negative_end_lifetime_twice":
        # The missing precondition is attributed to its pinned rsspec, while
        # VeriFast reports the second, failing call in a separate source note.
        spec_location = (str(a.relocation_source) +
                         "/bin/rust/rust_belt/lifetime_logic.rsspec(78,9-23)")
        first_call = "verified/lib.rs(14,13-25): Verifying call"
        second_call = "verified/lib.rs(15,13-25): Verifying call"
        caller_note = "verified/lib.rs(15,13-25): note: Verifying call"
        target_line = ("verified/lib.rs(9,1-17,2): Verifying function "
                       "'negative_end_lifetime_twice'")
        need(location is None and errors == [
                 spec_location + ": error: No matching heap chunks: "
                 "lifetime_token(cmp_k)"] and
             log.count(target_line) == 1 and
             log.count(first_call) == 1 and
             log.count(second_call) == 1 and
             log.count(caller_note) == 1 and
             0 <= log.index(target_line) < log.index(first_call) <
             log.index(second_call) < log.index(errors[0]) <
             log.index(caller_note),
             f"{key}: pinned callee precondition/caller attribution differs")
        error_location = spec_location
        caller_note_location = "verified/lib.rs(15,13-25)"
    else:
        need(not errors or location is not None,
             f"{key}: first error has no source location")
    result = {"case": case, "strict_lifetime_opt_in": opt_in,
            "classification": report["classification"], "accepted": False,
            "source_hashes": source_hashes, "mir": mir,
            "stage_exits": stage_exits, "target_headers": report.get("target_headers"),
            "callee_headers": report.get("callee_headers"),
            "first_error": errors[0] if errors else None,
            "first_error_source_location": location,
            "expected_obligation": (BOUNDARY[case][0] if opt_in and case in NEGATIVES else
                                    "explicit opt-in gate" if not opt_in else None),
            "expected_predicate": (BOUNDARY[case][1] if opt_in and case in NEGATIVES else
                                   "Strict lifetime binding requires explicit overnight opt-in"
                                   if not opt_in else None),
            "error_count": len(errors), "normal_post": report.get("normal_post"),
            "unwind_post": report.get("unwind_post")}
    if caller_note_location is not None:
        result["first_error_location"] = error_location
        result["first_error_caller_note_location"] = caller_note_location
    return result


def final(a) -> dict:
    pre = preflight(a, overlaid=True)
    overlay = load(a.evidence / "provider-overlay-manifest.json")
    need(overlay.get("guard_only") is True and
         overlay.get("base_sha256") == BASE_CAPTURE_SHA and
         overlay.get("path") == "research/challenge-8/overnight-lifetime/capture.py" and
         overlay.get("provider_sha256") ==
         sha(a.cloud_dir / "provider.py") and
         overlay.get("overlay_sha256") ==
         sha(a.proof_root / overlay["path"]), "current guard-only overlay changed")
    expected = set(CASES) | {"opt-in-absent"}
    need({p.name for p in (a.evidence / "cases").iterdir()} == expected,
         "unexpected or missing control case directory")
    rows = [read_case(a, case, True) for case in CASES]
    rows.append(read_case(a, "positive_basic", False))
    exits = load(a.evidence / "capture-exits.json")
    need(set(exits) == expected and all(exits[key] == 0 for key in expected),
         "capture helper failed before complete case classification")
    return {"classification": "CONTROLS_DISCOVERY_REVIEW_REQUIRED",
            "accepted": False, "strictcut_accepted": False,
            "actual_sort4_accepted": False, "preflight": pre,
            "source_and_mir_pin_status": "recorded for fresh manual review, not pre-approved",
            "cases": rows, "open_gates": OPEN_GATES}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=("preflight", "final"))
    for key in ("production-source", "production-applied-patch", "stock-home",
                "relocation-source", "relocation-evidence", "proof-root", "cloud-dir",
                "evidence", "output"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    try:
        result = preflight(a) if a.mode == "preflight" else final(a)
    except Exception as exc:
        result = {"classification": "INCONCLUSIVE", "accepted": False,
                  "strictcut_accepted": False, "actual_sort4_accepted": False,
                  "reason": str(exc), "open_gates": OPEN_GATES}
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if result["classification"] == "INCONCLUSIVE":
        raise SystemExit("strictCUT control discovery inconclusive: " + result["reason"])


if __name__ == "__main__":
    main()
