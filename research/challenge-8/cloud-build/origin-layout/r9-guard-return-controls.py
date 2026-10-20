#!/usr/bin/env python3
"""Source-bound synthetic and hosted controls for R9 guard-return recovery."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
R7_HELPER_PATH = HERE / "r7-late-admission-controls.py"
_spec = importlib.util.spec_from_file_location("r9_r7_receipt_helpers", R7_HELPER_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("R7 strict source/stage receipt helpers are unavailable")
_r7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r7)


CAMPAIGN = "r9-guard-return-controls-v1"
R9_PROFILE = "experimental-merge-guard-current-return-r9-v1"
TRACE_ENV = "SMALLSORT_R9_GUARD_TRACE"
RECOVERY_ENV = "SMALLSORT_R9_GUARD_RETURN_RECOVERY"
STAGES = ("exporter", "decode", "refinement", "verifast")
SUCCESS_STATUSES = {"SUCCESS", "SUCCEEDED", "COMPLETED"}
SETUP_EXIT_CODES = {124, 125, 126, 127, 134, 137, 139}

MARKER = b"guard_current_return_recover();"
END_READONLY = b"end_ref_readonly::<u64>(r9_guard_ref);"
WRONG_ORIGIN = b"assert [1/2](*r9_tmp_origin |-> ?r9_tmp_current);"
WRONG_ORIGIN_MUTANT = b"assert [1/2](*begin |-> ?r9_tmp_current);"
HALF_ASSERT = WRONG_ORIGIN

# Resource mappings are deliberately narrow. A case remains inconclusive until
# its source target, pre-recovery native binding, exact diagnostic, and stage
# receipts all agree. Update predicate/spec strings only from reviewed native
# evidence; a generic nonzero verifier exit is never a match.
CASES = {
    "omit_end": {
        "kind": "resource",
        "target_anchor": HALF_ASSERT,
        "expected_predicates": ("points_to",),
        "expected_spec": None,
    },
    "duplicate_end": {
        "kind": "resource",
        "target_anchor": END_READONLY,
        "target_occurrence": 2,
        "expected_predicates": ("ref_readonly_end_token",),
        "expected_spec": ("bin/rust/aliasing.rsspec(50,",),
    },
    "wrongorigin": {
        "kind": "resource",
        "target_anchor": WRONG_ORIGIN_MUTANT,
        "expected_predicates": ("points_to", "*begin", "begin |->"),
        "expected_spec": None,
    },
    "duplicate_marker": {
        "kind": "admission",
        "target_anchor": MARKER,
        "expected_stage": "verifast",
        "expected_error": "R9 guard-return marker is ambiguous",
    },
    "missing_marker": {
        "kind": "admission",
        "target_anchor": b"assert ref_readonly_end_token::<u64>(?r9_guard_ref, ?r9_tmp_origin, ?r9_tmp_share);",
        "expected_stage": "verifast",
        "expected_error": "R9 guard-return recovery target body is missing its checked source marker",
    },
}

EVENT_PREFIX = "R9_GUARD_EVENT "
_EVENT_KEYS = ("function", "def_hash", "mir_fingerprint", "mir_phase", "body_span",
               "block", "cleanup", "at", "kind", "outcome", "key", "selected",
               "selected_hash", "guard", "normal_target", "unwind", "receiver",
               "recovery", "tmp", "storage_live", "heap_total", "selected_total", "shown")
_FIELD_START = re.compile(r"(?:^|\s)(" + "|".join(_EVENT_KEYS) + r")=")
_ERROR = re.compile(r"^.*\berror:.*$", re.IGNORECASE | re.MULTILINE)
_SRC_LOC = re.compile(r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\)")
_EXEC_LOC = re.compile(r"verified/lib\.rs\((\d+),\d+[^\n]*Executing statement")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _not_run(name: str, reason: str, **fields) -> dict:
    return {"case": name, "classification": "NOT_RUN", "matched": False,
            "accepted": False, "proof_credit": False, "reason": reason, **fields}


def _inconclusive(name: str, reason: str, **fields) -> dict:
    return {"case": name, "classification": "INCONCLUSIVE", "matched": False,
            "accepted": False, "proof_credit": False, "reason": reason, **fields}


def _source_pair(source_case: Path, source_record: dict) -> tuple[bytes, bytes]:
    original, verified = _r7._source_pair(source_case, source_record)
    if (source_record.get("profile") != R9_PROFILE or
            source_record.get("prefix") is not False or
            source_record.get("late_callback_scope_recovery_requested") is not True or
            source_record.get("mutation") is not None):
        raise ValueError("source_record is not the exact positive fullbody R9 case")
    if verified.count(MARKER) != 1 or verified.count(END_READONLY) != 1:
        raise ValueError("R9 source lacks its unique guard-return recovery block")
    return original, verified


def _strict_stage_receipts(case: Path, stages, original_sha: str,
                           verified_sha: str, expected_codes: dict,
                           *, allow_verifast_proof_failure: bool = False) -> dict:
    rows = {}
    all_ok = type(stages) is dict
    for name in STAGES:
        receipt_path = case / f"{name}-stage.json"
        row = {"admitted": False, "reason": "stage receipt is absent"}
        if receipt_path.is_file():
            try:
                receipt = json.loads(receipt_path.read_text())
                code = receipt.get("exit_code") if type(receipt) is dict else None
                status = receipt.get("status") if type(receipt) is dict else None
                pair = {"original/lib.rs": original_sha,
                        "verified/lib.rs": verified_sha}
                source_before = receipt.get("source_before") if type(receipt) is dict else None
                source_after = receipt.get("source_after") if type(receipt) is dict else None
                source_ok = (type(source_before) is dict and source_before == pair and
                             source_after == pair and receipt.get("source_unchanged") is True)
                code_ok = type(code) is int and type(stages) is dict and type(stages.get(name)) is int
                expected = expected_codes.get(name)
                if allow_verifast_proof_failure and name == "verifast":
                    code_ok = code_ok and code == stages.get(name) and code not in SETUP_EXIT_CODES
                else:
                    code_ok = code_ok and code == expected and stages.get(name) == expected
                # Existing stage helpers admit absent/SUCCESS runner status;
                # the typed per-stage exit code records verifier refusal.
                status_ok = (status is None or
                             (type(status) is str and status in SUCCESS_STATUSES))
                ok = (type(receipt) is dict and receipt.get("stage") == name and
                      code_ok and source_ok and status_ok)
                row = {"admitted": ok, "exit_code": code if type(code) is int else None,
                       "status": status if type(status) is str else None,
                       "source_identity_matches": source_ok, "status_matches": status_ok,
                       "exit_code_matches": code_ok}
            except (OSError, json.JSONDecodeError, AttributeError, TypeError) as error:
                row = {"admitted": False,
                       "reason": f"invalid stage receipt: {type(error).__name__}: {error}"}
        rows[name] = row
        all_ok = all_ok and row["admitted"]
    return {"admitted": bool(all_ok), "stages": rows}


def _source_intact(case: Path, original_sha: str, verified_sha: str,
                   execution) -> dict:
    hashes = {}
    for rel in ("original/lib.rs", "verified/lib.rs"):
        path = case / rel
        hashes[rel] = _sha(path.read_bytes()) if path.is_file() else None
    expected = {"original/lib.rs": original_sha, "verified/lib.rs": verified_sha}
    ok = hashes == expected and type(execution) is dict and execution.get(
        "source_unchanged_at_every_stage") is True
    return {"admitted": ok, "hashes_after": hashes}


def _event_fields(line: str) -> dict:
    fields = {}
    payload = line[len(EVENT_PREFIX):] if line.startswith(EVENT_PREFIX) else line
    matches = list(_FIELD_START.finditer(payload))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(payload)
        fields[match.group(1)] = payload[match.end():end].strip()
    return fields


def _qualified_event(line: str, recovery: str | None = None) -> bool:
    if not line.startswith(EVENT_PREFIX):
        return False
    fields = _event_fields(line)
    required = ("function", "def_hash", "mir_fingerprint", "mir_phase", "body_span",
                "block", "cleanup", "at", "kind", "outcome", "key", "selected",
                "selected_hash", "guard", "normal_target", "unwind", "receiver")
    if any(not fields.get(key) for key in required):
        return False
    if (fields.get("kind") != "selected_drop" or fields.get("outcome") != "returning" or
            fields.get("cleanup") != "true"):
        return False
    if recovery is not None and fields.get("recovery") != recovery:
        return False
    return True


def _baseline_gate(source_case: Path, original: bytes, verified: bytes) -> dict:
    original_sha, verified_sha = _sha(original), _sha(verified)
    exact_source = ((source_case / "original/lib.rs").is_file() and
                    (source_case / "verified/lib.rs").is_file() and
                    _sha((source_case / "original/lib.rs").read_bytes()) == original_sha and
                    _sha((source_case / "verified/lib.rs").read_bytes()) == verified_sha)
    stages = {}
    for name in STAGES:
        try:
            item = json.loads((source_case / f"{name}-stage.json").read_text())
            stages[name] = item.get("exit_code") if type(item) is dict else None
        except (OSError, json.JSONDecodeError, AttributeError):
            stages[name] = None
    expected = {"exporter": 0, "decode": 0, "refinement": 0,
                "verifast": stages["verifast"]}
    receipts = _strict_stage_receipts(source_case, stages, original_sha, verified_sha,
                                      expected, allow_verifast_proof_failure=True)
    log_path = source_case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    lines = log.splitlines()
    before = [line for line in lines if _qualified_event(line, "before")]
    complete = [line for line in lines if _qualified_event(line, "complete")]
    before_fields = _event_fields(before[0]) if len(before) == 1 else {}
    complete_fields = _event_fields(complete[0]) if len(complete) == 1 else {}
    same_event = (len(before) == 1 and len(complete) == 1 and
                  all(before_fields.get(k) == complete_fields.get(k) for k in
                      ("function", "def_hash", "mir_fingerprint", "mir_phase", "body_span",
                       "block", "cleanup", "kind", "outcome", "key", "selected",
                       "selected_hash", "guard", "normal_target", "unwind", "receiver")) and
                  lines.index(before[0]) < lines.index(complete[0]))
    code = stages.get("verifast")
    verifier_not_setup = type(code) is int and code in (0, 1)
    admitted = (exact_source and receipts["admitted"] and
                all(type(stages.get(name)) is int and stages[name] == 0
                    for name in ("exporter", "decode", "refinement")) and
                verifier_not_setup and same_event)
    return {"admitted": admitted, "source_exact": exact_source,
            "source_hashes": {"original": original_sha, "verified": verified_sha},
            "stages": stages, "stage_receipt_gate": receipts,
            "selected_cleanup_return_before_count": len(before),
            "selected_cleanup_return_complete_count": len(complete),
            "return_binding_matches": same_event,
            "selected_drop_binding": ({key: complete_fields.get(key) for key in
                ("function", "def_hash", "key", "selected", "selected_hash", "guard")}
                if same_event else None),
            "recovery_completion_observed": len(complete) == 1,
            "verifast_log_sha256": _sha(log.encode()),
            "reason": None if admitted else
                "exact fullbody source, strict stage receipts, cleanup returning event, and recovery completion are required"}


def _marker_span(source: bytes) -> tuple[int, int, bytes]:
    starts = [m.start() for m in re.finditer(re.escape(MARKER), source)]
    if len(starts) != 1:
        raise ValueError("expected exactly one R9 guard-return marker")
    block_start = source.rfind(b"/*@ {", 0, starts[0])
    block_end = source.find(b"} @*/", starts[0])
    if block_start < 0 or block_end < 0:
        raise ValueError("R9 guard-return marker block is not uniquely bounded")
    block_end += len(b"} @*/")
    block = source[block_start:block_end]
    if block.count(MARKER) != 1:
        raise ValueError("R9 guard-return marker block is ambiguous")
    return block_start, block_end, block


def _mutate(name: str, source: bytes) -> tuple[bytes, int]:
    spec = CASES[name]
    if name in {"omit_end", "duplicate_end", "wrongorigin"}:
        start, end, block = _marker_span(source)
        if name == "omit_end":
            if block.count(END_READONLY) != 1:
                raise ValueError("omit_end requires one original readonly end command")
            changed = block.replace(END_READONLY + b"\n", b"", 1)
        elif name == "duplicate_end":
            if block.count(END_READONLY) != 1:
                raise ValueError("duplicate_end requires one original readonly end command")
            changed = block.replace(END_READONLY + b"\n",
                                    END_READONLY + b"\n        " + END_READONLY + b"\n", 1)
        else:
            if block.count(WRONG_ORIGIN) != 1:
                raise ValueError("wrongorigin requires one half-share assertion")
            changed = block.replace(WRONG_ORIGIN, WRONG_ORIGIN_MUTANT, 1)
        mutated = source[:start] + changed + source[end:]
        target_anchor = spec["target_anchor"]
        occurrence = spec.get("target_occurrence", 1)
        starts = [m.start() for m in re.finditer(re.escape(target_anchor), mutated)]
        if len(starts) < occurrence:
            raise ValueError(f"{name}: diagnostic target anchor is absent")
        pos = starts[occurrence - 1]
    elif name == "duplicate_marker":
        start, end, block = _marker_span(source)
        mutated = source[:end] + b"\n" + block + source[end:]
        # StaticError is attached to the outer PureStmt location, not the
        # marker invocation within that block.
        pos = mutated.find(b"/*@ {")
    elif name == "missing_marker":
        start, end, block = _marker_span(source)
        if block.count(MARKER) != 1:
            raise ValueError("missing_marker requires one original marker")
        changed = block.replace(MARKER + b"\n", b"", 1)
        mutated = source[:start] + changed + source[end:]
        # The missing-marker diagnostic uses the enclosing function signature
        # location (fn_sig_loc), not the recovery assertion location.
        declarations = list(re.finditer(
            rb"(?m)^[ \t]*(?:pub(?:\([^)]*\))?[ \t]+)?unsafe[ \t]+fn[ \t]+\w+", mutated))
        prior = [match for match in declarations if match.start() < start]
        if not prior:
            raise ValueError("missing_marker enclosing unsafe function signature is absent")
        pos = prior[-1].start()
    else:
        raise ValueError(f"unsupported R9 guard-return control: {name}")
    line = mutated[:pos].count(b"\n") + 1
    return mutated, line


def _stage_gate(case: Path, execution, meta: dict) -> dict:
    if type(execution) is not dict:
        return {"admitted": False, "reason": "execute_case returned a non-object"}
    stages = execution.get("stages")
    expected = meta["expected_stages"]
    expected_codes = dict(expected)
    receipts = _strict_stage_receipts(case, stages, meta["original_sha256"],
                                     meta["verified_sha256"], expected_codes)
    return receipts


def _error_lines(log: str) -> list[str]:
    return _ERROR.findall(log)


def _last_executed_line_before(log: str, error_line: str) -> int | None:
    prefix = log.split(error_line, 1)[0]
    matches = _EXEC_LOC.findall(prefix)
    return int(matches[-1]) if matches else None


def _native_pre_binding(log: str, expected_binding=None) -> dict:
    rows = [line for line in log.splitlines() if _qualified_event(line, "before")]
    fields = _event_fields(rows[0]) if len(rows) == 1 else {}
    if type(expected_binding) is dict:
        binding_matches = all(fields.get(key) == value
                              for key, value in expected_binding.items())
    else:
        binding_matches = True
    return {"admitted": len(rows) == 1 and binding_matches, "count": len(rows),
            "binding_matches_baseline": binding_matches,
            "event": rows[0] if len(rows) == 1 else None}


def _classify(name: str, case: Path, meta: dict, execution) -> dict:
    spec = CASES[name]
    if type(execution) is not dict:
        return _inconclusive(name, "execute_case returned a non-object",
                             expected_diagnostic=meta.get("expected_diagnostic"))
    stages = execution.get("stages")
    source_gate = _source_intact(case, meta["original_sha256"],
                                 meta["verified_sha256"], execution)
    stage_gate = _stage_gate(case, execution, meta)
    log_path = case / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    errors = _error_lines(log)
    base = {**meta, "case": name, "source_gate": source_gate,
            "stage_receipt_gate": stage_gate, "errors": errors,
            "accepted": False, "proof_credit": False}
    if not stage_gate.get("admitted") or not source_gate.get("admitted"):
        return {**base, "classification": "INCONCLUSIVE", "matched": False,
                "reason": "exact mutant source/stage receipts did not pass"}
    if spec["kind"] == "admission":
        expected_error = spec.get("expected_error")
        stage = spec["expected_stage"]
        if expected_error is None:
            return {**base, "classification": "INCONCLUSIVE_EXPECTED_DIAGNOSTIC_UNSET",
                    "matched": False,
                    "reason": "admission diagnostic mapping is explicitly unset"}
        error_location = _SRC_LOC.search(errors[0]) if len(errors) == 1 else None
        exact = (len(errors) == 1 and expected_error in errors[0] and
                 error_location is not None and
                 int(error_location.group(1)) == meta["expected_error_line"] and
                 type(stages) is dict and stages.get(stage) == 1)
        return {**base,
                "classification": "EXPECTED_ADMISSION_REJECTION" if exact else "INCONCLUSIVE",
                "matched": exact,
                "expected_frontend_error": expected_error,
                "frontend_error_match": exact,
                "reason": None if exact else "exact mapped frontend error/stage was not observed"}

    before = _native_pre_binding(log, meta.get("baseline_drop_binding"))
    target_line = meta.get("expected_error_line")
    direct_errors = [(error, _SRC_LOC.search(error)) for error in errors]
    direct_at_target = [(error, match) for error, match in direct_errors
                        if match and int(match.group(1)) == target_line]
    spec_errors = [(error, spec_name) for error in errors
                   for spec_name in (spec.get("expected_spec") or ()) if spec_name in error]
    target_executed = bool(target_line and re.search(
        rf"verified/lib\.rs\({target_line},\d+[^\n]*Executing statement", log))
    if len(errors) != 1:
        return {**base, "classification": "INCONCLUSIVE", "matched": False,
                "native_pre_recovery_binding": before,
                "reason": "expected exactly one targeted verifier error"}
    error = errors[0]
    last_line = _last_executed_line_before(log, error)
    predicates = spec["expected_predicates"]
    predicate_match = any(word.lower() in error.lower() for word in predicates)
    target_match = bool(direct_at_target and target_executed and last_line == target_line)
    canonical_match = bool(spec.get("expected_spec") and spec_errors and
                           target_executed and last_line == target_line)
    expected_verifast_error = type(stages) is dict and stages.get("verifast") == 1
    # The `before` receipt must bind this failure to the selected cleanup Drop;
    # `complete` must be absent because a target failure precedes completion.
    completed = any(_qualified_event(line, "complete") for line in log.splitlines())
    matched = (before["admitted"] and not completed and expected_verifast_error and
               predicate_match and (target_match or canonical_match))
    return {**base,
            "classification": "EXPECTED_RESOURCE_REFUSAL" if matched else "INCONCLUSIVE",
            "matched": matched, "native_pre_recovery_binding": before,
            "target_line_executed": target_executed,
            "last_executed_line_before_error": last_line,
            "error_at_target": target_match,
            "canonical_spec_error_last_at_target": canonical_match,
            "expected_predicate_match": predicate_match,
            "recovery_completion_absent": not completed,
            "reason": None if matched else
                "requires exact cleanup-return binding, targeted predicate/spec error, and last execution at target"}


def run(evidence: Path, args, env: dict, execute_case, source_case: Path,
        source_record: dict) -> dict:
    """Run source-bound R9 recovery controls; never grant proof credit."""
    evidence = Path(evidence)
    result = {"schema": CAMPAIGN, "profile": getattr(args, "profile", None),
              "accepted": False, "proof_credit": False, "all_matched": False,
              "classification": "INCONCLUSIVE", "cases": {}}
    if evidence.exists():
        reason = "refusing to reuse R9 guard-return control evidence directory"
        result["cases"] = {name: _not_run(name, reason) for name in CASES}
        return result
    try:
        evidence.mkdir(parents=True)
        source_case = Path(source_case)
        original, verified = _source_pair(source_case, source_record)
        if getattr(args, "profile", None) != R9_PROFILE:
            raise ValueError("active profile is not the exact R9 guard-return profile")
        if type(env) is not dict:
            raise ValueError("parent environment must be a dictionary")
    except Exception as error:
        reason = f"source/profile setup failed: {type(error).__name__}: {error}"
        result["cases"] = {name: _not_run(name, reason) for name in CASES}
        _write_receipt(evidence, result)
        return result

    baseline = _baseline_gate(source_case, original, verified)
    result["baseline"] = baseline
    if not baseline["admitted"]:
        result["cases"] = {name: _not_run(name, "R9 fullbody baseline admission prerequisite failed",
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
    for name, spec in CASES.items():
        try:
            mutant, expected_line = _mutate(name, verified)
            case = evidence / name
            (case / "original").mkdir(parents=True)
            (case / "verified").mkdir()
            (case / "original/lib.rs").write_bytes(original)
            (case / "verified/lib.rs").write_bytes(mutant)
            failure_stage = spec.get("expected_stage", "verifast")
            expected_stages = {stage: (1 if stage == failure_stage else 0)
                               for stage in STAGES}
            meta = {"expected_error_line": expected_line,
                    "case_name": name,
                    "baseline_drop_binding": baseline.get("selected_drop_binding"),
                    "expected_diagnostic": spec.get("expected_error"),
                    "expected_predicates": list(spec.get("expected_predicates", ())),
                    "original_sha256": _sha(original),
                    "verified_sha256": _sha(mutant),
                    "baseline_verified_sha256": _sha(verified),
                    "expected_stages": expected_stages,
                    "proof_credit": False}
            (case / "case.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
            case_env = dict(env) if type(env) is dict else {}
            case_env[TRACE_ENV] = "1"
            case_env[RECOVERY_ENV] = "1"
            execution = execute_case(case, args, case_env)
            results[name] = _classify(name, case, meta, execution)
        except Exception as error:
            results[name] = _inconclusive(name,
                f"mutant setup/execution/classification failed: {type(error).__name__}: {error}",
                baseline_admitted=True)
    result["cases"] = results
    result["all_matched"] = (set(results) == set(CASES) and
                             all(row.get("matched") is True for row in results.values()))
    result["classification"] = ("ALL_INTENDED_R9_GUARD_RETURN_CONTROLS_MATCHED"
                                if result["all_matched"] else "INCONCLUSIVE")
    _write_receipt(evidence, result)
    return result


def _write_receipt(evidence: Path, result: dict) -> None:
    try:
        (evidence / "aggregate.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    except OSError:
        result["classification"] = "INCONCLUSIVE"
        result["all_matched"] = False
        result["aggregate_write_error"] = "could not persist aggregate receipt"
