#!/usr/bin/env python3
"""Source-bound Cloud admission mutants for the R7 late callback scope."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


CAMPAIGN = "r7-late-callback-admission-controls-v1"
R7_PROFILE = "experimental-merge-late-callback-recovery-r7-v1"
R8_PROFILE = "experimental-merge-owned-array-allocation-r8-v1"
R9_PROFILE = "experimental-merge-guard-current-return-r9-v1"
R10_PROFILE = "experimental-merge-moving-gap-r10-v1"
R11_PROFILE = "experimental-merge-label-storage-r11-v1"
SUPPORTED_PROFILES = (R7_PROFILE, R8_PROFILE, R9_PROFILE, R10_PROFILE, R11_PROFILE)
STAGES = ("exporter", "decode", "refinement", "verifast")
BASELINE_DIAGNOSTIC = "MERGE_LATE_CALLBACK_RECOVERY"
CASES = {
    "missing_outer_unwind_flag": {
        "expected_error": "Late callback scope requires a preceding fresh lifetime and outer unwind flag",
        "anchor": b"late_callback_scope_begin::<'late>()",
    },
    "wrong_recovery_ref": {
        "expected_error": "Late callback recovery does not match the exact scoped loan return",
        "anchor": b"late_callback_recover::<'late>()",
    },
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _inconclusive(name: str, reason: str, **fields) -> dict:
    return {"case": name, "classification": "INCONCLUSIVE", "matched": False,
            "accepted": False, "proof_credit": False, "reason": reason, **fields}


def _not_run(name: str, reason: str, **fields) -> dict:
    return {"case": name, "classification": "NOT_RUN", "matched": False,
            "accepted": False, "proof_credit": False, "reason": reason, **fields}


def _source_pair(source_case: Path, source_record: dict) -> tuple[bytes, bytes]:
    original = (source_case / "original/lib.rs").read_bytes()
    verified = (source_case / "verified/lib.rs").read_bytes()
    if (_sha(original) != source_record.get("original_sha256") or
            _sha(verified) != source_record.get("verified_sha256")):
        raise ValueError("R7 fullbody source hashes do not match source_record")
    if (source_record.get("profile") not in SUPPORTED_PROFILES or
            source_record.get("prefix") is not False or
            source_record.get("late_callback_scope_recovery_requested") is not True or
            source_record.get("mutation") is not None):
        raise ValueError("source_record is not the positive fullbody R7 case")
    return original, verified


def _mutate(name: str, source: bytes) -> tuple[bytes, int]:
    spec = CASES[name]
    if name == "missing_outer_unwind_flag":
        lines = source.splitlines(keepends=True)
        found = [index for index, line in enumerate(lines)
                 if line.strip() == b"//@ let r7_late_unwind = false;"]
        if len(found) != 1:
            raise ValueError("expected exactly one outer late unwind flag declaration")
        del lines[found[0]]
        mutated = b"".join(lines)
        marker = spec["anchor"]
    elif name == "wrong_recovery_ref":
        marker = b"late_callback_recover::<'late>()"
        starts = [m.start() for m in re.finditer(re.escape(marker), source)]
        if len(starts) != 1:
            raise ValueError("expected exactly one late recovery marker")
        block_end = source.find(b"} @*/", starts[0])
        if block_end < 0:
            raise ValueError("late recovery marker block is unterminated")
        before, block, after = source[:starts[0]], source[starts[0]:block_end], source[block_end:]
        old = b"end_ref_readonly::<u64>(r4_cmp_tmp_ref);"
        if block.count(old) != 1:
            raise ValueError("expected exactly one tmp end_ref_readonly in late recovery")
        mutated = before + block.replace(old,
            b"end_ref_readonly::<u64>(r4_cmp_sift_ref);", 1) + after
    else:
        raise ValueError(f"unsupported R7 admission mutant: {name}")
    lines = mutated.splitlines()
    needle = spec["anchor"]
    matches = [index + 1 for index, line in enumerate(lines) if needle in line]
    if len(matches) != 1:
        raise ValueError(f"{name}: expected exactly one diagnostic source marker")
    return mutated, matches[0]


def _stage_receipts(case: Path, stages: dict, expected: dict[str, int],
                    original_sha: str, verified_sha: str) -> dict:
    rows = {}
    admitted = isinstance(stages, dict)
    for stage in STAGES:
        path = case / f"{stage}-stage.json"
        row = {"admitted": False, "reason": "stage receipt is absent"}
        if path.is_file():
            try:
                receipt = json.loads(path.read_text())
                before = receipt.get("source_before") if isinstance(receipt, dict) else None
                after = receipt.get("source_after") if isinstance(receipt, dict) else None
                source_ok = (isinstance(before, dict) and before == after and
                             before.get("original/lib.rs") == original_sha and
                             before.get("verified/lib.rs") == verified_sha)
                status = receipt.get("status") if isinstance(receipt, dict) else None
                status_ok = status is None or status in {"SUCCESS", "SUCCEEDED", "COMPLETED"}
                expected_code = expected[stage]
                ok = (isinstance(receipt, dict) and receipt.get("stage") == stage and
                      type(receipt.get("exit_code")) is int and
                      receipt.get("exit_code") == expected_code and
                      type(stages.get(stage)) is int and stages.get(stage) == expected_code and
                      receipt.get("source_unchanged") is True and source_ok and status_ok)
                row = {"admitted": ok, "exit_code": receipt.get("exit_code") if isinstance(receipt, dict) else None,
                       "source_unchanged": receipt.get("source_unchanged") if isinstance(receipt, dict) else None,
                       "source_identity_matches": source_ok, "status_matches": status_ok}
            except (OSError, json.JSONDecodeError, AttributeError, TypeError) as error:
                row = {"admitted": False, "reason": f"invalid stage receipt: {error}"}
        rows[stage] = row
        admitted = admitted and row["admitted"]
    return {"admitted": admitted, "stages": rows}


def _source_intact(case: Path, expected_original: str, expected_verified: str,
                   execution: dict) -> dict:
    hashes = {}
    for relative in ("original/lib.rs", "verified/lib.rs"):
        path = case / relative
        hashes[relative] = _sha(path.read_bytes()) if path.is_file() else None
    admitted = (hashes == {"original/lib.rs": expected_original,
                           "verified/lib.rs": expected_verified} and
                execution.get("source_unchanged_at_every_stage") is True)
    return {"admitted": admitted, "hashes_after": hashes}


def _baseline_gate(source_case: Path, original: bytes, verified: bytes) -> dict:
    original_sha, verified_sha = _sha(original), _sha(verified)
    source_ok = ((source_case / "original/lib.rs").is_file() and
                 (source_case / "verified/lib.rs").is_file() and
                 _sha((source_case / "original/lib.rs").read_bytes()) == original_sha and
                 _sha((source_case / "verified/lib.rs").read_bytes()) == verified_sha)
    stages = {}
    for stage in STAGES:
        path = source_case / f"{stage}-stage.json"
        try:
            receipt = json.loads(path.read_text())
            stages[stage] = receipt.get("exit_code")
        except (OSError, json.JSONDecodeError, AttributeError):
            stages[stage] = None
    expected = {"exporter": 0, "decode": 0, "refinement": 0,
                "verifast": stages["verifast"]}
    receipt_gate = _stage_receipts(source_case, stages, expected, original_sha, verified_sha)
    log_path = source_case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    diagnostic_lines = [line for line in log.splitlines() if BASELINE_DIAGNOSTIC in line]
    frontend_observed = len(diagnostic_lines) == 1
    verifier_status_ok = (type(stages["verifast"]) is int and stages["verifast"] not in (125, 127))
    admitted = (source_ok and receipt_gate["admitted"] and
                all(stages[s] == 0 for s in ("exporter", "decode", "refinement")) and
                verifier_status_ok and frontend_observed)
    return {"admitted": admitted, "source_exact": source_ok,
            "source_hashes": {"original": original_sha, "verified": verified_sha},
            "stages": stages, "stage_receipt_gate": receipt_gate,
            "frontend_diagnostic_observed": frontend_observed,
            "verifast_log_sha256": _sha(log.encode()),
            "reason": None if admitted else "baseline source/stage/frontend admission gate did not pass"}


def _classify(name: str, case: Path, meta: dict, execution) -> dict:
    if not isinstance(execution, dict):
        execution = {"execution_receipt_error": "execute_case returned a non-object"}
    stages = execution.get("stages")
    if not isinstance(stages, dict):
        stages = {}
    source_gate = _source_intact(case, meta["original_sha256"], meta["verified_sha256"], execution)
    expected_stages = {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 1}
    receipt_gate = _stage_receipts(case, stages, expected_stages,
                                   meta["original_sha256"], meta["verified_sha256"])
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = re.findall(r"^.*\berror:.*$", log, re.M | re.I)
    expected_line = meta["expected_error_line"]
    at_line = (len(errors) == 1 and re.search(
        rf"verified/lib\.rs\({expected_line},\d+(?:-\d+(?:,\d+)?)?\): error:", errors[0]) is not None)
    message_match = bool(errors and meta["expected_error"] in errors[0])
    matched = (source_gate["admitted"] and receipt_gate["admitted"] and
               stages.get("exporter") == 0 and stages.get("decode") == 0 and
               stages.get("refinement") == 0 and stages.get("verifast") == 1 and
               at_line and message_match)
    return {**meta, "case": name,
            "classification": "EXPECTED_ADMISSION_REJECTION" if matched else "INCONCLUSIVE",
            "matched": matched, "accepted": False, "proof_credit": False,
            "source_gate": source_gate, "stage_receipt_gate": receipt_gate,
            "error_at_expected_line": at_line,
            "error_match": message_match, "errors": errors,
            "evidence_class": "source-bound frontend admission negative only; no proof credit"}


def run(evidence: Path, args, env: dict, execute_case, source_case: Path,
        source_record: dict) -> dict:
    """Run only exact-source R7 admission mutants in the hosted caller."""
    evidence = Path(evidence)
    result = {"schema": CAMPAIGN, "profile": getattr(args, "profile", R7_PROFILE), "accepted": False,
              "proof_credit": False, "all_matched": False,
              "classification": "INCONCLUSIVE", "cases": {}}
    if evidence.exists():
        reason = "refusing to reuse R7 admission-control evidence directory"
        result["cases"] = {name: _not_run(name, reason) for name in CASES}
        return result
    try:
        evidence.mkdir(parents=True)
        source_case = Path(source_case)
        original, verified = _source_pair(source_case, source_record)
        if getattr(args, "profile", None) not in SUPPORTED_PROFILES:
            raise ValueError("active profile is not a supported late-recovery profile")
    except Exception as error:
        reason = f"source/profile setup failed: {type(error).__name__}: {error}"
        result["cases"] = {name: _not_run(name, reason) for name in CASES}
        return result
    baseline = _baseline_gate(source_case, original, verified)
    result["baseline"] = baseline
    if not baseline["admitted"]:
        result["cases"] = {name: _not_run(name, "baseline frontend admission prerequisite failed",
                                          baseline_admitted=False) for name in CASES}
        result["blocker"] = baseline["reason"]
        _write_receipt(evidence, result)
        return result
    if not callable(execute_case):
        result["cases"] = {name: _not_run(name, "hosted execute_case callback is unavailable",
                                          baseline_admitted=True) for name in CASES}
        _write_receipt(evidence, result)
        return result
    results = {}
    for name in CASES:
        try:
            mutant, expected_line = _mutate(name, verified)
            case = evidence / name
            (case / "original").mkdir(parents=True)
            (case / "verified").mkdir()
            (case / "original/lib.rs").write_bytes(original)
            (case / "verified/lib.rs").write_bytes(mutant)
            meta = {"expected_error": CASES[name]["expected_error"],
                    "expected_error_line": expected_line,
                    "original_sha256": _sha(original), "verified_sha256": _sha(mutant),
                    "baseline_verified_sha256": _sha(verified),
                    "expected_stages": {"exporter": 0, "decode": 0,
                                        "refinement": 0, "verifast": 1},
                    "proof_credit": False}
            (case / "case.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
            execution = execute_case(case, args, env)
            results[name] = _classify(name, case, meta, execution)
        except Exception as error:
            results[name] = _inconclusive(name,
                f"mutant setup/execution/classification failed: {type(error).__name__}: {error}",
                baseline_admitted=True)
    result["cases"] = results
    result["all_matched"] = (set(results) == set(CASES) and
                             all(row.get("matched") is True for row in results.values()))
    result["classification"] = ("ALL_INTENDED_ADMISSION_REJECTIONS" if result["all_matched"]
                                else "INCONCLUSIVE")
    _write_receipt(evidence, result)
    return result


def _write_receipt(evidence: Path, result: dict) -> None:
    try:
        (evidence / "aggregate.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n")
    except OSError:
        result["classification"] = "INCONCLUSIVE"
        result["all_matched"] = False
        result["aggregate_write_error"] = "could not persist aggregate receipt"
