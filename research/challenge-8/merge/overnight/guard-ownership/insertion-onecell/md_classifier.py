"""Pure classifier for saved tracked-ManuallyDrop VeriFast logs.

This module deliberately has no runner, filesystem, or proof-tool imports.
"""
from __future__ import annotations

import re


_HEADER = re.compile(
    r"^\s*\d+(?:\.\d+)?s: [^\s(]+\([0-9]+,[0-9]+"
    r"(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying function '([^']+)'$", re.M)
_ERROR = re.compile(r"^.*\berror:.*$", re.I | re.M)
_DEAD = re.compile(r"^.*dead code.*$", re.I | re.M)


def _segments(log: str, name: str) -> list[str]:
    headers = list(_HEADER.finditer(log))
    found = []
    for i, match in enumerate(headers):
        function = match.group(1)
        if function == name or function.startswith(name + "<"):
            end = headers[i + 1].start() if i + 1 < len(headers) else len(log)
            found.append(log[match.start():end])
    return found


def _executed_at(text: str, line: object) -> bool:
    if line is None:
        return False
    return re.search(
        rf"verified/lib\.rs\({re.escape(str(line))},\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", text) is not None


def _at_line(text: str, line: object) -> bool:
    if line is None:
        return False
    return re.search(rf"\({re.escape(str(line))},\d+(?:-\d+(?:,\d+)?)?\)", text) is not None


def _source_hashes(execution: dict, meta: dict) -> bool:
    expected = meta.get("source_sha256")
    before = execution.get("source_before", {})
    after = execution.get("source_after", {})
    return bool(expected and before.get("original/lib.rs") == expected and
                before.get("verified/lib.rs") == expected and
                after == before and
                execution.get("source_unchanged_at_every_stage") is True)


def _verified_error_at(error: str, line: object) -> bool:
    if line is None:
        return False
    return re.search(rf"verified/lib\.rs\({re.escape(str(line))},\d+(?:-\d+(?:,\d+)?)?\): error:",
                     error) is not None


def _spec_error_at(error: str, line: object) -> bool:
    if line is None:
        return False
    return re.search(rf"aliasing\.rsspec\({re.escape(str(line))},\d+(?:-\d+(?:,\d+)?)?\): error:",
                     error) is not None


def classify_log(name: str, log: str, meta: dict, execution: dict) -> dict:
    """Classify one saved control log; missing evidence is always inconclusive."""
    errors = _ERROR.findall(log)
    dead = _DEAD.findall(log)
    segments = _segments(log, name)
    segment = segments[0] if len(segments) == 1 else ""
    stages = execution.get("stages", {})
    frontend_ok = all(stages.get(stage) == 0 for stage in
                      ("exporter", "decode", "refinement"))
    body_seen = len(segments) == 1
    read_seen = _executed_at(segment, meta.get("read_line"))
    return_seen = "Executing return statement" in segment
    leak_seen = "Leak check." in segment
    gate_kind = "PROOF"
    matched = False

    if name in {"positive_manually_drop_after_merge", "positive"}:
        matched = (_source_hashes(execution, meta) and frontend_ok and
                   stages.get("verifast") == 0 and body_seen and read_seen and
                   return_seen and leak_seen and not errors and not dead and
                   "0 errors found" in segment)
    elif name == "negative_missing_reference_initialization":
        target_line = meta.get("target_line")
        spec_line = meta.get("spec_init_line", 88)
        pred = re.compile(r"ref_initialized\s*<\s*i32\s*>", re.I)
        exact_target_diagnostic = any(
            "No matching heap chunks" in error and pred.search(error) and
            (_verified_error_at(error, target_line) or _spec_error_at(error, spec_line))
            for error in errors)
        # The intended source call must itself have executed in the one named body.
        target_executed = (_executed_at(segment, target_line) or
                           any("No matching heap chunks" in error and pred.search(error) and
                               _verified_error_at(error, target_line) for error in errors))
        matched = (_source_hashes(execution, meta) and frontend_ok and
                   stages.get("verifast") == 1 and body_seen and target_executed and
                   len(errors) == 1 and exact_target_diagnostic and not dead)
    elif name == "negative_missing_precreated_reference":
        gate_kind = "ADMISSION_ONLY"
        target_line = meta.get("target_line")
        matched = (_source_hashes(execution, meta) and frontend_ok and
                   stages.get("verifast") == 1 and len(errors) == 1 and
                   _verified_error_at(errors[0], target_line) and
                   "Taking the address of this expression is not supported" in errors[0] and
                   not dead)
    elif name == "negative_read_without_permission":
        target_line = meta.get("target_line", meta.get("read_line"))
        right_error = (len(errors) == 1 and
                       "No matching heap chunks" in errors[0] and
                       re.search(r"points_to\s*<\s*i32\s*>", errors[0], re.I) is not None and
                       _verified_error_at(errors[0], target_line))
        matched = (_source_hashes(execution, meta) and frontend_ok and
                   stages.get("verifast") == 1 and body_seen and read_seen and
                   right_error and not dead and not leak_seen)

    return {
        "case": name,
        "classification": "REGRESSION_MATCHED" if matched else "INCONCLUSIVE",
        "body_seen": body_seen,
        "return_seen": return_seen,
        "leak_seen": leak_seen,
        "read_seen": read_seen,
        "errors": errors,
        "dead_code": dead,
        "gate_kind": gate_kind,
    }
