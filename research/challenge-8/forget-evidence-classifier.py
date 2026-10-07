#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Strict parsing and classification of VeriFast timed function evidence.

Diagnostic notes that quote a function header are deliberately not treated as
execution headers.  Callers must provide the exact expected timed function
list for the unit; duplicates, omissions, and unlisted functions fail closed.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
import re
from typing import Any, Mapping, Sequence


_TIMED_HEADER = re.compile(
    r"^\s*(?P<seconds>\d+\.\d+s): (?P<file>.+?)\((?P<location>\d+,\d+-[^)]+)\): "
    r"Verifying function '(?P<function>[^']+)'\s*$"
)
_ERROR = re.compile(r"^(?P<location>.+?): error: (?P<message>.*)$")


@dataclass(frozen=True)
class TimedFunction:
    seconds: str
    file: str
    location: str
    function: str
    start_line: int
    end_line: int
    body_execution_seen: bool
    return_seen: bool
    leak_check_seen: bool


def timed_functions(log: str) -> list[TimedFunction]:
    """Parse only timed execution headers and their log slices."""
    lines = log.splitlines()
    starts: list[tuple[int, re.Match[str]]] = []
    for index, line in enumerate(lines):
        match = _TIMED_HEADER.fullmatch(line)
        if match is not None:
            starts.append((index, match))

    result: list[TimedFunction] = []
    for ordinal, (index, match) in enumerate(starts):
        end = starts[ordinal + 1][0] if ordinal + 1 < len(starts) else len(lines)
        body = lines[index + 1:end]
        result.append(TimedFunction(
            seconds=match.group("seconds"),
            file=match.group("file"),
            location=match.group("location"),
            function=match.group("function"),
            start_line=index + 1,
            end_line=end,
            body_execution_seen=any("Executing statement" in line for line in body),
            return_seen=any("Executing return statement" in line for line in body),
            leak_check_seen=any("Leak check." in line for line in body),
        ))
    return result


def _errors(log: str) -> list[dict[str, str]]:
    errors = []
    for line in log.splitlines():
        match = _ERROR.match(line)
        if match:
            errors.append({"location": match.group("location"),
                           "message": match.group("message"),
                           "line": line})
    return errors


def _has_dead_code(log: str) -> bool:
    return any(re.search(r"\bdead code\b", line, flags=re.IGNORECASE)
               is not None for line in log.splitlines())


def exact_unit_evidence(
    log: str,
    expected_functions: Sequence[str],
) -> dict[str, Any]:
    """Return exact timed-header and per-function body evidence for a unit.

    `expected_functions` is an exact, ordered declaration list for the functions
    expected to be checked in this verifier invocation.  The output includes a
    per-function trace; it does not infer a proof result by itself.
    """
    functions = timed_functions(log)
    actual = [function.function for function in functions]
    counts = Counter(actual)
    expected = list(expected_functions)
    return {
        "expected_functions": expected,
        "timed_functions": [asdict(function) for function in functions],
        "actual_function_names": actual,
        "function_list_exact": actual == expected,
        "duplicate_functions": sorted(name for name, count in counts.items()
                                       if count != 1),
        "missing_functions": [name for name in expected if counts[name] == 0],
        "unknown_functions": [name for name in actual if name not in expected],
        "all_body_executed": bool(functions) and all(
            function.body_execution_seen for function in functions),
        "all_returned": bool(functions) and all(
            function.return_seen for function in functions),
        "all_leak_checked": bool(functions) and all(
            function.leak_check_seen for function in functions),
    }


def _exact_expected_error(
    error: Mapping[str, str],
    expected: Mapping[str, Any],
) -> bool:
    """Match the first diagnostic at its exact source obligation."""
    location = error["location"]
    message = error["message"]
    file = str(expected["file"])
    line = int(expected["line"])
    if not re.search(re.escape(file) + r"\(" + str(line) + r",\d+(?:-|\))",
                     location):
        return False
    exact_message = expected.get("message")
    if exact_message is not None:
        return message == exact_message
    required = expected.get("message_contains")
    return isinstance(required, str) and required in message


def classify_unit(
    log: str,
    exit_code: int,
    expected_functions: Sequence[str],
    *,
    positive: bool,
    expected_error: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Classify one complete VeriFast invocation, rejecting partial evidence.

    Positive units require exit 0, no errors or dead-code diagnostics, exact
    timed function coverage, and a return plus leak check for every function.
    Negative units require exit 1 and exactly one first error at the specified
    file/line/message; leak failures must occur after that function returned
    and reached its leak check.  Any missing, duplicate, unknown, or untimed
    expected function leaves the result unaccepted.
    """
    unit = exact_unit_evidence(log, expected_functions)
    errors = _errors(log)
    dead_code = _has_dead_code(log)
    target_error = bool(errors and expected_error is not None and
                        _exact_expected_error(errors[0], expected_error))
    functions = {function.function: function for function in timed_functions(log)}
    negative_body_ok = True
    if expected_error is not None:
        function_name = expected_error.get("function")
        if function_name is not None:
            function = functions.get(str(function_name))
            negative_body_ok = function is not None and function.body_execution_seen
            if expected_error.get("kind") == "leak":
                negative_body_ok = bool(negative_body_ok and function and
                                        function.return_seen and function.leak_check_seen)

    common = (unit["function_list_exact"] and not unit["duplicate_functions"] and
              not unit["missing_functions"] and not unit["unknown_functions"] and
              not dead_code)
    if positive:
        accepted = (common and exit_code == 0 and not errors and
                    unit["all_body_executed"] and unit["all_returned"] and
                    unit["all_leak_checked"])
        classification = "POSITIVE" if accepted else "INCONCLUSIVE"
    else:
        accepted = (common and exit_code == 1 and len(errors) == 1 and
                    target_error and negative_body_ok)
        classification = "INTENDED_NEGATIVE" if accepted else "INCONCLUSIVE"

    return {
        "classification": classification,
        "accepted": accepted,
        "exit_code": exit_code,
        "dead_code_seen": dead_code,
        "error_count": len(errors),
        "first_error": errors[0] if errors else None,
        "expected_error_matched": target_error,
        "negative_body_evidence": negative_body_ok,
        **unit,
    }


def self_test() -> dict[str, Any]:
    """Small deterministic parser/classifier mutation suite (no subprocesses)."""
    expected = ["crate::first", "crate::second"]
    good = (
        "0.010s: verified/lib.rs(3,1-8,2): Verifying function 'crate::first'\n"
        "Executing statement\nExecuting return statement\nLeak check.\n"
        "verified/lib.rs(3,1-8,2): note: Verifying function 'crate::first'\n"
        "0.020s: verified/lib.rs(10,1-15,2): Verifying function 'crate::second'\n"
        "Executing statement\nExecuting return statement\nLeak check.\n"
    )
    baseline = classify_unit(good, 0, expected, positive=True)
    note_only = classify_unit(
        "verified/lib.rs(3,1-8,2): note: Verifying function 'crate::first'\n",
        0, expected, positive=True)
    duplicate = classify_unit(good +
        "0.030s: verified/lib.rs(3,1-8,2): Verifying function 'crate::first'\n"
        "Executing statement\nExecuting return statement\nLeak check.\n",
        0, expected, positive=True)
    missing = classify_unit(good.split("0.020s:")[0], 0, expected, positive=True)
    unknown = classify_unit(good.replace("crate::second", "crate::other"),
                            0, expected, positive=True)
    dead_code = classify_unit(good + "verified/lib.rs(1,1): dead code\n",
                              1, expected, positive=True)
    checks = {
        "baseline_passes": baseline["accepted"],
        "diagnostic_note_is_not_a_timed_header":
            len(timed_functions(good)) == 2,
        "note_only_log_cannot_pass": not note_only["accepted"],
        "duplicate_timed_header_rejected": not duplicate["accepted"],
        "missing_expected_function_rejected": not missing["accepted"],
        "unknown_function_rejected": not unknown["accepted"],
        "dead_code_with_exit_one_rejected": not dead_code["accepted"],
    }
    return {"pass": all(checks.values()), "checks": checks}
