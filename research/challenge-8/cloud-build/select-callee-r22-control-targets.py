#!/usr/bin/env python3
"""Inactive validator for fresh, exact R22 control diagnostic targets.

This module observes no tools and grants no classification or proof credit. A
caller supplies source bytes for every negative variant, the exact tool
lib.rsspec bytes, a fresh observed target map, and a verifier log to match.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import uuid
from typing import Any

SCHEMA = "select-r22-control-target-map-v1"
RESULT_SCHEMA = "select-r22-control-target-validation-v1"
VARIANTS = (
    "callee-false-normal", "callee-owner-duplicate", "callee-owner-loss",
    "callee-thread-duplicate", "no-retained-half", "omit-selected-own",
    "omit-unselected-own",
)
CALLEE_VARIANTS = set(VARIANTS[:4])
TOOL_SPEC_FILE = "bin/rust/std/lib.rsspec"
SPEC_PRECONDITION_LINE = {
    "omit-selected-own": 462,
    "omit-unselected-own": 463,
}
SPEC_PRECONDITION_INTENT = {
    "omit-selected-own": "first-selected-wrapper-own-precondition",
    "omit-unselected-own": "second-unselected-wrapper-own-precondition",
}
SPEC_PRECONDITION_TEXT = {
    "omit-selected-own": "        req MaybeUninit_pointer_own::<Element>()(t, a) &*&",
    "omit-unselected-own": "            MaybeUninit_pointer_own::<Element>()(t, b);",
}

FORGET_SIGNATURE = b"pub unsafe fn checked_forget_owned<T>(t: T)\n"
FORGET_BODY = b"{\n    let _ = ManuallyDrop::new(t);\n}"
FORGET_HALF_CONTRACT = (
    b"/*@\nreq thread_token(?tid) &*& tid == currentThread &*& [1/2] <T>.own(tid, t);\n@*/\n"
    b"/*@\nens thread_token(tid) &*& [1/2] <T>.own(tid, t);\n@*/\n"
    b"/*@\non_unwind_ens false;\n@*/\n")
FORGET_CONTRACTS = {
    "callee-false-normal": FORGET_HALF_CONTRACT.replace(
        b"ens thread_token(tid) &*& [1/2] <T>.own(tid, t);",
        b"ens thread_token(tid) &*& [1/2] <T>.own(tid, t) &*& false;"),
    "callee-owner-duplicate": FORGET_HALF_CONTRACT.replace(
        b"[1/2] <T>.own(tid, t);\n@*/\n/*@\non_unwind_ens",
        b"[1/2] <T>.own(tid, t) &*& [1/2] <T>.own(tid, t);\n@*/\n/*@\non_unwind_ens"),
    "callee-owner-loss": FORGET_HALF_CONTRACT.replace(
        b"ens thread_token(tid) &*& [1/2] <T>.own(tid, t);",
        b"ens thread_token(tid);"),
    "callee-thread-duplicate": FORGET_HALF_CONTRACT.replace(
        b"ens thread_token(tid) &*& [1/2] <T>.own(tid, t);",
        b"ens thread_token(tid) &*& thread_token(tid) &*& [1/2] <T>.own(tid, t);"),
}
SELECT_SIGNATURE = (
    b"pub fn select_unpredictable<Element>(\n"
    b"    condition: bool,\n    true_val: *const Element,\n"
    b"    false_val: *const Element,\n) -> *const Element\n")
FULL_CELL_ASSERT = (
    b"        /*@ assert *saved_guard.inner |-> ?selected_payload; @*/\n")
RETAINED_HALF_MERGE = (
    b"merge_fractions points_to::<*Element>(saved_guard.inner, _);")

_DIAGNOSTIC_MARKERS = (
    "error:", "fatal error", "cannot prove", "no matching heap chunks",
    "function leaks heap chunks", "assertion failure", "verification failed",
)
_LOCATION = re.compile(
    r"^(?P<file>.+)\((?P<line>[1-9][0-9]*),(?P<start>[1-9][0-9]*)-"
    r"(?P<end>[1-9][0-9]*)\): (?P<message>\S.*)$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_CHAR_LITERAL = re.compile(
    rb"'(?:[^\\'\n]|\\(?:x[0-9a-fA-F]{2}|u\{[0-9a-fA-F_]+\}|.))'")


class TargetError(ValueError):
    """Fail-closed source, target-map, or diagnostic mismatch."""


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise TargetError("R22-CONTROL-TARGETS: " + why)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _line(source: bytes, offset: int) -> int:
    return source[:offset].count(b"\n") + 1


def _select_function_bounds(source: bytes) -> tuple[int, int]:
    """Return bounds for the uniquely pinned select function body."""
    _need(source.count(SELECT_SIGNATURE) == 1,
          "exact select_unpredictable signature is absent or ambiguous")
    signature_at = source.index(SELECT_SIGNATURE)
    brace_at = signature_at + len(SELECT_SIGNATURE)
    while brace_at < len(source):
        while brace_at < len(source) and source[brace_at] in b" \t\r\n":
            brace_at += 1
        if source.startswith(b"//", brace_at):
            end = source.find(b"\n", brace_at + 2)
            brace_at = len(source) if end < 0 else end + 1
            continue
        if source.startswith(b"/*", brace_at):
            comment_start = brace_at
            brace_at += 2
            nested = 1
            while brace_at < len(source) and nested:
                if source.startswith(b"/*", brace_at):
                    nested += 1
                    brace_at += 2
                elif source.startswith(b"*/", brace_at):
                    nested -= 1
                    brace_at += 2
                else:
                    brace_at += 1
            _need(nested == 0, "unterminated comment after select signature")
            _need(comment_start < brace_at,
                  "malformed contract comment after select signature")
            continue
        break
    _need(brace_at < len(source) and source[brace_at:brace_at + 1] == b"{",
          "pinned select signature is not followed by its body")

    # Skip comments and literals so braces inside ghost annotations or text do
    # not create a false function boundary.
    depth = 0
    i = brace_at
    while i < len(source):
        if source.startswith(b"//", i):
            end = source.find(b"\n", i + 2)
            i = len(source) if end < 0 else end + 1
            continue
        if source.startswith(b"/*", i):
            i += 2
            nested = 1
            while i < len(source) and nested:
                if source.startswith(b"/*", i):
                    nested += 1
                    i += 2
                elif source.startswith(b"*/", i):
                    nested -= 1
                    i += 2
                else:
                    i += 1
            _need(nested == 0, "unterminated comment in select function")
            continue
        if source[i:i + 1] == b"'":
            # Rust lifetimes are apostrophes without a closing quote. Skip a
            # character literal, including escaped/unicode-brace forms.
            literal = _CHAR_LITERAL.match(source, i)
            if literal is not None:
                i = literal.end()
                continue
            i += 1
            continue
        if source[i:i + 1] == b'"':
            quote = source[i]
            i += 1
            while i < len(source):
                if source[i] == 0x5c:
                    i += 2
                elif source[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
            _need(i <= len(source) and source[i - 1:i] == bytes([quote]),
                  "unterminated quoted literal in select function")
            continue
        if source[i:i + 1] == b"{":
            depth += 1
        elif source[i:i + 1] == b"}":
            depth -= 1
            if depth == 0:
                return signature_at, i + 1
            _need(depth > 0, "unbalanced select function body")
        i += 1
    raise TargetError("R22-CONTROL-TARGETS: unterminated select function body")


def _source_anchor(variant: str, source: bytes) -> tuple[str, int]:
    _need(isinstance(source, bytes), "verified source must be bytes")
    if variant in CALLEE_VARIANTS:
        _need(source.count(FORGET_SIGNATURE) == 1 and
              source.count(FORGET_BODY) == 1,
              "checked_forget_owned signature/body is absent or ambiguous")
        contract = FORGET_CONTRACTS[variant]
        _need(source.count(contract) == 1,
              "variant-specific checked_forget_owned contract is absent or ambiguous")
        for other, value in FORGET_CONTRACTS.items():
            if other != variant:
                _need(source.count(value) == 0,
                      "source contains a different callee-control contract")
        contract_at = source.index(contract)
        sig_at = source.index(FORGET_SIGNATURE)
        body_at = source.index(FORGET_BODY, sig_at + len(FORGET_SIGNATURE))
        _need(sig_at < contract_at < body_at and
              source.index(FORGET_BODY) == body_at,
              "checked_forget_owned contract/signature/body order differs")
        if variant == "callee-owner-loss":
            return "verified/lib.rs", _line(source, body_at + FORGET_BODY.rindex(b"}"))
        ens_at = contract_at + contract.index(b"ens ")
        return "verified/lib.rs", _line(source, ens_at)

    if variant == "no-retained-half":
        start, end = _select_function_bounds(source)
        body = source[start:end]
        _need(body.count(FULL_CELL_ASSERT) == 1 and
              body.count(RETAINED_HALF_MERGE) == 1,
              "unique full-cell assert or retained-half merge in select body missing")
        merge_at = start + body.index(RETAINED_HALF_MERGE)
        assert_at = start + body.index(FULL_CELL_ASSERT)
        _need(merge_at < assert_at,
              "full-cell assert does not follow the retained-half merge")
        return "verified/lib.rs", _line(source, assert_at)

    _need(variant in SPEC_PRECONDITION_LINE, "unknown control variant")
    return TOOL_SPEC_FILE, SPEC_PRECONDITION_LINE[variant]


def _validate_provenance(provenance: object) -> dict[str, Any]:
    _need(isinstance(provenance, dict) and set(provenance) == {
        "build_id", "brief_log_sha256", "brief_log_index", "archive_id",
        "request_id"}, "per-row caller provenance is missing or has wrong fields")
    try:
        build_id = str(uuid.UUID(provenance["build_id"]))
    except (ValueError, AttributeError, TypeError):
        raise TargetError("R22-CONTROL-TARGETS: caller provenance build ID is invalid")
    _need(build_id == provenance["build_id"].lower(),
          "caller provenance build ID is not canonical")
    digest = provenance["brief_log_sha256"]
    _need(isinstance(digest, str) and _SHA256.fullmatch(digest) is not None,
          "caller provenance Brief log SHA-256 is invalid")
    index = provenance["brief_log_index"]
    _need(type(index) is int and index > 0,
          "caller provenance Brief log index is invalid")
    ids = (provenance["archive_id"], provenance["request_id"])
    _need(all(isinstance(value, str) and value.strip() and
              "\n" not in value and "\r" not in value for value in ids),
          "caller provenance archive/request IDs are invalid")
    return {"build_id": build_id, "brief_log_sha256": digest,
            "brief_log_index": index, "archive_id": ids[0],
            "request_id": ids[1]}


def _tool_spec_file_identity(tool_spec_file: object,
                             tool_home: object = None) -> str:
    _need(isinstance(tool_spec_file, str) and tool_spec_file,
          "exact tool-spec diagnostic path is required")
    if tool_spec_file == TOOL_SPEC_FILE:
        return TOOL_SPEC_FILE
    _need(tool_home is not None,
          "absolute tool-spec diagnostic path requires the caller tool home")
    expected = str(Path(tool_home).resolve() / TOOL_SPEC_FILE)
    _need(tool_spec_file == expected,
          "absolute diagnostic path is not the exact tool-home lib.rsspec")
    return expected


def _validate_target(variant: str, record: object, source: bytes,
                     tool_spec: bytes, tool_spec_identity: str) -> dict[str, Any]:
    _need(isinstance(record, dict), variant + ": target missing/null/wrong type")
    expected_keys = {"variant", "observed", "source_sha256", "tool_spec_sha256",
                     "file", "line", "start_column", "end_column", "message",
                     "provenance", "log_sha256"}
    if variant in SPEC_PRECONDITION_LINE:
        expected_keys.add("tool_precondition")
    _need(set(record) == expected_keys, variant + ": target field inventory differs")
    _need(record.get("variant") == variant and record.get("observed") is True,
          variant + ": target is unobserved or belongs to another row")
    source_digest = _sha(source)
    tool_digest = _sha(tool_spec)
    provenance = _validate_provenance(record.get("provenance"))
    _need(record.get("source_sha256") == source_digest and
          record.get("tool_spec_sha256") == tool_digest,
          variant + ": source or tool-spec SHA-256 differs")
    log_digest = record.get("log_sha256")
    _need(isinstance(log_digest, str) and _SHA256.fullmatch(log_digest) is not None,
          variant + ": verifier log SHA-256 is invalid")
    expected_file, expected_line = _source_anchor(variant, source)
    if variant in SPEC_PRECONDITION_LINE:
        expected_file = tool_spec_identity
    _need(record.get("file") == expected_file and
          type(record.get("line")) is int and record.get("line") == expected_line,
          variant + ": diagnostic file/line differs from exact source anchor")
    start, end = record.get("start_column"), record.get("end_column")
    _need(type(start) is int and type(end) is int and start > 0 and end > start,
          variant + ": diagnostic column range is invalid")
    message = record.get("message")
    _need(isinstance(message, str) and message.startswith("error: ") and
          "\n" not in message and "\r" not in message,
          variant + ": complete one-line verifier error message required")

    normalized = {
        "variant": variant, "observed": True,
        "source_sha256": source_digest, "tool_spec_sha256": tool_digest,
        "provenance": provenance, "log_sha256": log_digest,
        "file": expected_file, "line": expected_line,
        "start_column": start, "end_column": end, "message": message,
    }
    if variant in SPEC_PRECONDITION_LINE:
        precondition = record.get("tool_precondition")
        _need(isinstance(precondition, dict) and set(precondition) ==
              {"intent", "line_text"}, variant + ": tool precondition missing/wrong type")
        _need(precondition.get("intent") == SPEC_PRECONDITION_INTENT[variant],
              variant + ": wrong tool precondition identity")
        text = precondition.get("line_text")
        _need(isinstance(text, str) and text and "\n" not in text and "\r" not in text,
              variant + ": exact tool precondition line required")
        lines = tool_spec.splitlines()
        line_number = SPEC_PRECONDITION_LINE[variant]
        _need(len(lines) >= line_number,
              variant + ": pinned tool spec lacks the intended precondition line")
        try:
            actual = lines[line_number - 1].decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            raise TargetError("R22-CONTROL-TARGETS: tool precondition line is not UTF-8")
        _need(text == SPEC_PRECONDITION_TEXT[variant] and actual == text,
              variant + ": tool precondition line differs from exact intended source")
        normalized["tool_precondition"] = {
            "intent": precondition["intent"], "line_text": actual,
        }
    return normalized


def validate_target_map(target_map: object, sources: object,
                        tool_spec: bytes, *,
                        tool_spec_file: str = TOOL_SPEC_FILE,
                        tool_home=None) -> dict[str, Any]:
    """Validate a supplied map and return it as explicitly non-accepting.

    `sources` maps each of the seven control variant names to its exact verified
    source bytes. `target_map` is an observation input; no observed target is
    embedded in this module.
    """
    _need(isinstance(target_map, dict) and
          set(target_map) == {"schema", "targets"} and
          target_map.get("schema") == SCHEMA,
          "target map missing/null/wrong schema or field inventory")
    _need(isinstance(sources, dict) and set(sources) == set(VARIANTS),
          "source map missing/null/wrong type or seven-control inventory differs")
    _need(isinstance(tool_spec, bytes), "exact tool lib.rsspec bytes required")
    tool_spec_identity = _tool_spec_file_identity(tool_spec_file, tool_home)
    targets = target_map.get("targets")
    _need(isinstance(targets, dict) and set(targets) == set(VARIANTS),
          "target map missing/null/wrong type or seven-control inventory differs")
    normalized = {
        variant: _validate_target(variant, targets[variant], sources[variant],
                                  tool_spec, tool_spec_identity)
        for variant in VARIANTS
    }
    return {
        "schema": RESULT_SCHEMA,
        "status": "TARGET_MAP_VALIDATED_NOT_ACCEPTED",
        "provenance_status": "CALLER_DECLARED_PRIOR_OBSERVATIONS_CONSISTENT_NOT_AUTHENTICATED",
        "target_map_sha256": _sha(json.dumps(
            target_map, sort_keys=True, separators=(",", ":")).encode()),
        "targets": normalized,
        "accepted": False,
        "proof_credit": False,
    }


def _diagnostic_lines(log_text: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    for index, raw in enumerate(log_text.splitlines(), 1):
        line = raw.strip()
        lowered = line.casefold()
        if any(marker in lowered for marker in _DIAGNOSTIC_MARKERS):
            found.append((index, line))
    return found


def match_first_and_only_error(variant: str, target_map: object,
                               sources: object, tool_spec: bytes,
                               log_text: object, *, log_observation: object,
                               tool_spec_file: str = TOOL_SPEC_FILE,
                               tool_home=None) -> dict[str, Any]:
    """Bind the caller-declared prior log observation to its exact row/content."""
    _need(variant in VARIANTS, "wrong or unknown control row")
    validated_map = validate_target_map(
        target_map, sources, tool_spec, tool_spec_file=tool_spec_file,
        tool_home=tool_home)
    target = validated_map["targets"].get(variant)
    _need(isinstance(target, dict) and target.get("variant") == variant and
          target.get("observed") is True,
          "target row absent, null, unobserved, or wrong row")
    _need(isinstance(log_text, str) and log_text.strip(),
          "verifier log absent, null, or wrong type")
    _need(isinstance(log_observation, dict) and set(log_observation) == {
        "variant", "source_sha256", "log_sha256", "provenance"},
        "caller log observation is missing or has wrong fields")
    source = sources.get(variant) if isinstance(sources, dict) else None
    _need(isinstance(source, bytes), "selected verified source bytes are absent")
    log_digest = _sha(log_text.encode("utf-8"))
    _need(log_observation.get("variant") == variant and
          log_observation.get("source_sha256") == _sha(source) and
          log_observation.get("log_sha256") == log_digest and
          target.get("source_sha256") == log_observation.get("source_sha256") and
          target.get("log_sha256") == log_digest and
          _validate_provenance(log_observation.get("provenance")) ==
            target.get("provenance"),
          "caller log observation does not bind this row/source/content/provenance")
    diagnostics = _diagnostic_lines(log_text)
    _need(len(diagnostics) == 1,
          "verifier log must contain exactly one error/fatal diagnostic")
    diagnostic_line, diagnostic = diagnostics[0]
    match = _LOCATION.fullmatch(diagnostic)
    _need(match is not None,
          "sole verifier diagnostic has no exact file/line/column location")
    observed = {
        "file": match.group("file"),
        "line": int(match.group("line")),
        "start_column": int(match.group("start")),
        "end_column": int(match.group("end")),
        "message": match.group("message"),
    }
    expected = {key: target[key] for key in
                ("file", "line", "start_column", "end_column", "message")}
    _need(observed == expected,
          "sole verifier error differs from the exact fresh target record")
    return {
        "schema": "select-r22-control-diagnostic-observation-v1",
        "variant": variant,
        "diagnostic_line": diagnostic_line,
        "target": expected,
        "log_sha256": log_digest,
        "provenance_status": "CALLER_DECLARED_PRIOR_OBSERVATION_CONSISTENT_NOT_AUTHENTICATED",
        "matches_first_and_only_error": True,
        "accepted": False,
        "proof_credit": False,
    }
