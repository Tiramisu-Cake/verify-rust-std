#!/usr/bin/env python3
"""Fail-closed review-candidate audit for strictCUT false-post Cloud controls."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

CASES = {"normal-false": "positive_basic",
         "unwind-false": "positive_direct_unwind"}
SUPPORT = ("normal-export", "normal-decode", "readonly-export",
           "readonly-decode", "refinement")
ERROR = re.compile(r"^verified/lib\.rs\((\d+),([^)]+)\): error: (.+)$")
LOC_FIELD = re.compile(r"\b(startLine|startCol|endLine|endCol)\s*=\s*\d+")
SPAN_COORD = re.compile(r"\b(line|pos)\s*=\s*\d+")
TRACE_ENTRY = re.compile(r"(?m)^\s*\d+\.\d+s: [^\n]*: Verifying function '([^']+)'\s*$")
OPEN_GATES = (
    "exact first false-post verifier diagnostics and spans require human review",
    "all-path liveness and source/MIR CFG mutation negatives",
    "alias/address escape and pointer provenance",
    "outer-variable, nested-bound, heap, and hidden heap-term retention",
    "combined S6/no-cut regression and actual sort4 admission",
)


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError(why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    need(path.is_file(), f"missing {path}")
    return json.loads(path.read_text())


def import_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def quoted_end(data: str, start: int) -> int:
    need(data[start] == '"', "MIR quoted value expected")
    escaped = False
    for at in range(start + 1, len(data)):
        if escaped:
            escaped = False
        elif data[at] == "\\":
            escaped = True
        elif data[at] == '"':
            return at + 1
    raise RuntimeError("unclosed MIR quoted value")


def balanced_end(data: str, start: int) -> int:
    need(data[start] == "(", "MIR parenthesized value expected")
    depth = 0
    at = start
    while at < len(data):
        if data[at] == '"':
            at = quoted_end(data, at)
            continue
        if data[at] == "(":
            depth += 1
        elif data[at] == ")":
            depth -= 1
            if depth == 0:
                return at + 1
        at += 1
    raise RuntimeError("unclosed MIR span value")


def raw_fields(data: str) -> list[str]:
    """Extract every unescaped MIR raw field; quoted contents are indivisible."""
    found = []
    at = 0
    while at < len(data):
        if data[at] == '"':
            at = quoted_end(data, at)
        elif data.startswith('raw = "', at):
            begin = at + len("raw = ")
            at = quoted_end(data, begin)
            found.append(data[begin:at])
        else:
            at += 1
    return found


def proof_entries(log: str, name: str) -> list[int]:
    """Positions of timestamped proof entries; diagnostic `note:` lines are excluded."""
    return [match.start() for match in TRACE_ENTRY.finditer(log)
            if match.group(1) == name]


def normalize_coordinates(data: str, pattern: re.Pattern[str]) -> str:
    out = []
    at = 0
    while at < len(data):
        if data[at] == '"':
            end = quoted_end(data, at)
            out.append(data[at:end])
            at = end
        else:
            match = pattern.match(data, at)
            if match:
                out.append(match.group(1) + " = 0")
                at = match.end()
            else:
                out.append(data[at])
                at += 1
    return "".join(out)


def normalize_mir(data: str, target_raw: str | None = None,
                  canonical_raw: str | None = None) -> str:
    """Normalize only source coordinates and one reviewed contract raw field."""
    out = []
    at = 0
    changed_raw = 0
    while at < len(data):
        if data[at] == '"':
            end = quoted_end(data, at)
            out.append(data[at:end])
            at = end
        elif data.startswith("span = (", at) or data.startswith("impSpan = (", at):
            tag = "impSpan = " if data.startswith("impSpan = (", at) else "span = "
            end = balanced_end(data, at + len(tag))
            out.append(normalize_coordinates(data[at:end], SPAN_COORD))
            at = end
        elif data.startswith('raw = "', at):
            begin = at + len("raw = ")
            end = quoted_end(data, begin)
            token = data[begin:end]
            if token == target_raw:
                changed_raw += 1
                token = canonical_raw
            out.append("raw = " + token)
            at = end
        else:
            match = LOC_FIELD.match(data, at)
            if match:
                out.append(match.group(1) + " = 0")
                at = match.end()
            else:
                out.append(data[at])
                at += 1
    need(changed_raw == (1 if target_raw is not None else 0),
         "target contract raw replacement is not unique in complete MIR")
    return "".join(out)


def audit_case(a, key: str, capture, prepare) -> dict:
    case = CASES[key]
    baseline = a.controls_evidence / "cases" / case / case
    root = a.evidence / "cases" / key
    record = load(root / "capture-result.json")
    manifest = load(a.evidence / "source-manifest.json")["cases"][key]
    old, new = prepare.MUTANTS[key][1:]
    parent = (baseline / "verified/lib.rs").read_bytes()
    changed = (root / "verified/lib.rs").read_bytes()
    original = (root / "original/lib.rs").read_bytes()
    need(parent.count(old) == 1 and parent.count(new) == 0 and
         changed == parent.replace(old, new, 1),
         f"{key}: source is not exactly one target post replacement")
    need(changed.count(new) == 1 and
         original == (baseline / "original/lib.rs").read_bytes() and
         capture.strip_ghost(changed) == original,
         f"{key}: runtime source differs")
    need(manifest.get("parent_case") == case and
         manifest.get("parent_verified_sha256") == sha(baseline / "verified/lib.rs") and
         manifest.get("mutant_verified_sha256") == sha(root / "verified/lib.rs") and
         manifest.get("original_sha256") == sha(root / "original/lib.rs") and
         manifest.get("post_line_one_based") == changed.count(b"\n", 0,
             changed.index(new)) + 1 and
         manifest.get("only_target_post_changed") is True and
         manifest.get("runtime_source_unchanged") is True,
         f"{key}: source manifest differs")
    need(record.get("classification") == "FALSE_POST_CAPTURE_REVIEW_REQUIRED" and
         record.get("case") == key and record.get("target_function") == case and
         record.get("accepted") is False and
         record.get("actual_sort4_accepted") is False and
         record.get("source_hashes") ==
         {"verified/lib.rs": sha(root / "verified/lib.rs"),
          "original/lib.rs": sha(root / "original/lib.rs")},
         f"{key}: capture source identity differs")
    stages = record.get("stages", {})
    stage_exits = {name: row.get("exit") for name, row in stages.items()}
    need(all(stage_exits.get(name) == 0 and
             stages[name].get("source_exact") is True for name in SUPPORT) and
         record.get("support_stages_complete") is True,
         f"{key}: source/MIR/refinement support stage failed")
    inventory = record.get("decoded_body_inventory", {})
    mode_rows = {}
    for mode in ("normal", "readonly"):
        row = inventory.get(mode, {})
        text_path = root / f"{mode}-mir.txt"
        bin_path = root / f"{mode}-mir.bin"
        base_text = baseline / f"{mode}-mir.txt"
        base_bin = baseline / f"{mode}-mir.bin"
        need(all(p.is_file() and p.stat().st_size > 0
                 for p in (text_path, bin_path, base_text, base_bin)),
             f"{key}: incomplete paired {mode} MIR")
        data = text_path.read_text(errors="replace")
        old_data = base_text.read_text(errors="replace")
        old_raw = raw_fields(old_data)
        new_raw = raw_fields(data)
        expected_old = '"' + old.decode() + '"'
        expected_new = '"' + new.decode() + '"'
        old_body = capture.target_body(old_data, case)
        new_body = capture.target_body(data, case)
        need(old_body is not None and new_body is not None and
             'contract = (' in old_body and 'contract = (' in new_body and
             'inputs = [' in old_body and 'inputs = [' in new_body and
             ('raw = ' + expected_old) in old_body.split('inputs = [', 1)[0] and
             ('raw = ' + expected_new) in new_body.split('inputs = [', 1)[0],
             f"{key}: changed raw value is not the target contract post")
        raw_differences = [index for index, (before, after) in
                           enumerate(zip(old_raw, new_raw)) if before != after]
        need(len(old_raw) == len(new_raw) and len(raw_differences) == 1 and
             old_raw[raw_differences[0]] == expected_old and
             new_raw[raw_differences[0]] == expected_new,
             f"{key}: contract raw fields differ beyond the target post")
        normalized = normalize_mir(data, expected_new, expected_old)
        baseline_normalized = normalize_mir(old_data)
        need(row.get("full_decoded_bytes") == text_path.stat().st_size and
             row.get("full_decoded_sha256") == sha(text_path) and
             row.get("mir_binary_sha256") == sha(bin_path) and
             row.get("target_count") == 1 and
             row.get("same_unit_callee_count") ==
             (1 if key == "unwind-false" else 0) and
             row.get("source_path_present") is True and
             row.get("ghost_decl_block_present") is True and
             data.count(f'defPath = "{case}"') == 1 and
             normalized == baseline_normalized,
             f"{key}: complete {mode} MIR graph differs beyond source spans/post raw")
        if key == "unwind-false":
            need(row.get("direct_continue") is True and
                 "unwindAction = (continue = void)" in old_data,
                 f"{key}: direct Continue unwind absent in {mode} MIR")
        mode_rows[mode] = {
            "mutant_full_mir_sha256": sha(text_path),
            "baseline_full_mir_sha256": sha(base_text),
            "mutant_binary_sha256": sha(bin_path),
            "baseline_binary_sha256": sha(base_bin),
            "normalized_full_mir_sha256": hashlib.sha256(
                normalized.encode()).hexdigest(),
            "baseline_normalized_full_mir_sha256": hashlib.sha256(
                baseline_normalized.encode()).hexdigest(),
            "reviewed_contract_raw_change_only": True,
            "complete_graph_equal_after_source_coordinate_and_contract_raw_redaction": True,
        }
    log_path = root / "full-verification.log"
    log = log_path.read_text(errors="replace")
    errors = [line for line in log.splitlines()
              if ": error:" in line or line.startswith("Fatal error:")]
    target_header = f"Verifying function '{case}'"
    target_entries = proof_entries(log, case)
    legacy_headers = record.get("header_count_semantics") is None
    need(record.get("header_count_semantics") in (None, "trace_entry_v1") and
         record.get("target_headers") ==
         (log.count(target_header) if legacy_headers else len(target_entries)) and
         len(target_entries) == 1,
         f"{key}: target trace-entry inventory differs")
    need(errors == record.get("full_error_lines") and
         record.get("first_error") == (errors[0] if errors else None) and
         (legacy_headers or record.get("target_headers") == 1),
         f"{key}: target proof/error inventory differs")
    callee_entries = proof_entries(log, "cut_maybe_unwind")
    callee_header = "Verifying function 'cut_maybe_unwind'"
    legacy_callee_before = (log.count(callee_header) == 1 and
                            log.count(target_header) == 1 and
                            log.index(callee_header) < log.index(target_header))
    expected_callee_before = (
        (legacy_callee_before if legacy_headers else
         len(callee_entries) == 1 and callee_entries[0] < target_entries[0])
        if key == "unwind-false" else None)
    need(record.get("callee_headers") ==
         (log.count(callee_header) if legacy_headers else len(callee_entries)) and
         record.get("callee_before_target") == expected_callee_before,
         f"{key}: capture header metadata differs from raw log")
    if key == "unwind-false":
        need(len(callee_entries) == 1 and callee_entries[0] < target_entries[0],
             "unwind callee must prove before target")
    else:
        need(len(callee_entries) == 0, "normal control gained an unrelated callee")
    need(stage_exits.get("full-verification") in (1, 2) and len(errors) == 1 and
         target_entries[0] < log.index(errors[0]),
         f"{key}: first failure did not follow target proof header")
    match = ERROR.match(errors[0])
    need(match is not None, f"{key}: first failure has no target source span")
    error_line = int(match.group(1))
    source_lines = changed.decode().splitlines()
    post_line = manifest["post_line_one_based"]
    target_end_line = len(source_lines) - list(reversed(source_lines)).index("}")
    # The target-specific span is not yet observed under this profile. The
    # false-post predicate text is pinned by the existing 26.10 control.
    expected_first = (error_line in (post_line, target_end_line) and
                      match.group(3) ==
                      "Cannot prove condition. (Cannot prove false.)")
    need(expected_first, f"{key}: first error is not the expected false-post boundary")
    return {"case": key, "parent_case": case, "classification":
            "FALSE_POST_FIRST_BOUNDARY_CANDIDATE_REVIEW_REQUIRED",
            "accepted": False, "first_error": errors[0],
            "first_error_source_line": error_line,
            "target_post_line": post_line, "target_end_line": target_end_line,
            "stage_exits": stage_exits, "source_hashes": record["source_hashes"],
            "mir": mode_rows,
            "actual_target_trace_entries": len(target_entries),
            "actual_callee_trace_entries": len(callee_entries),
            "callee_before_target":
                (callee_entries[0] < target_entries[0]) if key == "unwind-false" else None,
            "actual_callee_before_target":
                (callee_entries[0] < target_entries[0]) if key == "unwind-false" else None,
            "capture_header_count_semantics":
                "legacy_substring_includes_notes" if legacy_headers else "trace_entry_v1"}


def main() -> None:
    p = argparse.ArgumentParser()
    for key in ("proof-root", "controls-evidence", "evidence", "cloud-dir", "output"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args()
    try:
        prior = load(a.evidence / "prior-controls-audit.json")
        need(prior.get("classification") == "CONTROLS_DISCOVERY_REVIEW_REQUIRED" and
             prior.get("accepted") is False and
             prior.get("strictcut_accepted") is False,
             "same-build strictCUT matrix control absent")
        need(prior == load(a.controls_evidence / "diagnostic-audit.json"),
             "prior control audit changed")
        prepare = import_module("strict_cut_false_post_prepare",
                                a.cloud_dir / "strict-cut-false-posts-prepare.py")
        capture = import_module("strict_cut_frozen_capture",
                                a.proof_root / "research/challenge-8/overnight-lifetime/capture.py")
        manifest = load(a.evidence / "source-manifest.json")
        need(manifest.get("classification") ==
             "FALSE_POST_SOURCES_PREPARED_DIAGNOSTIC_ONLY" and
             set(manifest.get("cases", {})) == set(CASES) and
             manifest.get("accepted") is False,
             "false-post source manifest incomplete")
        rows = [audit_case(a, key, capture, prepare) for key in CASES]
        exits = load(a.evidence / "capture-exits.json")
        need(set(exits) == set(CASES) and all(code == 0 for code in exits.values()),
             "false-post capture helper failed")
        result = {"classification": "FALSE_POST_CONTROLS_DISCOVERY_REVIEW_REQUIRED",
                  "accepted": False, "strictcut_accepted": False,
                  "actual_sort4_accepted": False, "cases": rows,
                  "open_gates": OPEN_GATES}
    except Exception as exc:
        result = {"classification": "INCONCLUSIVE", "accepted": False,
                  "strictcut_accepted": False, "actual_sort4_accepted": False,
                  "reason": str(exc), "open_gates": OPEN_GATES}
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if result["classification"] == "INCONCLUSIVE":
        raise SystemExit("strictCUT false-post controls inconclusive: " + result["reason"])


if __name__ == "__main__":
    main()
