"""Pinned source/AST selector for the checked cleanup-helper lemma.

This module is an inactive transport extraction. It grants no proof credit and
does not perform compiler, verifier, or reconstruction work.
"""
from __future__ import annotations

import hashlib
import re
from typing import Any, Mapping


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("A1-RUNNER: " + why)


def _ast_source_span(location: Any) -> tuple[int, int] | None:
    """Parse pinned Ast.string_of_loc line bounds for verified/lib.rs only."""
    if not isinstance(location, tuple) or len(location) != 2 or location[0] != "loc":
        raise RuntimeError("A1-RUNNER: malformed location-bearing AST node")
    value = location[1]
    match = re.fullmatch(
        r"(?:.*/)?verified/lib\.rs\(([1-9][0-9]*),[0-9]+"
        r"(?:-(?:([1-9][0-9]*),)?[0-9]+)?\)", value)
    if match is None:
        return None
    lo = int(match.group(1))
    hi = int(match.group(2)) if match.group(2) else lo
    _need(hi >= lo, "AST source span order")
    return lo, hi


def _ast_source_coordinates(location: Any) -> tuple[int, int, int, int] | None:
    """Parse exact line/column bounds for a pinned verified-source location."""
    if not isinstance(location, tuple) or len(location) != 2 or location[0] != "loc":
        raise RuntimeError("A1-RUNNER: malformed location-bearing AST node")
    match = re.fullmatch(
        r"(?:.*/)?verified/lib\.rs\(([1-9][0-9]*),([1-9][0-9]*)"
        r"(?:-(?:([1-9][0-9]*),)?([1-9][0-9]*))?\)", location[1])
    if match is None:
        return None
    sl, sc = int(match.group(1)), int(match.group(2))
    el = int(match.group(3)) if match.group(3) else sl
    ec = int(match.group(4)) if match.group(4) else sc
    _need((el, ec) >= (sl, sc), "AST source coordinate order")
    return sl, sc, el, ec


def select_checked_cleanup_helper_lemma(ast_text: str, ast_gates,
                                        source_bytes: bytes,
                                        metadata: Mapping[str, Any]) -> dict:
    """Bind the checked helper AST to its exact certified source and lemma span."""
    _need(isinstance(source_bytes, bytes) and isinstance(metadata, Mapping) and
          metadata.get("name") == "a1_cleanup_option_ref" and
          metadata.get("kind") == "lemma",
          "checked cleanup helper source identity/type")
    bounds = ("source_start_line", "source_end_line", "body_start_line",
              "body_end_line")
    _need(all(type(metadata.get(key)) is int and metadata[key] > 0
              for key in bounds),
          "checked cleanup helper source bounds")
    lines = source_bytes.splitlines(keepends=True)
    start, end = metadata["source_start_line"], metadata["source_end_line"]
    body_start, body_end = metadata["body_start_line"], metadata["body_end_line"]
    _need(1 <= start <= body_start < body_end <= end <= len(lines),
          "checked cleanup helper source/body interval")
    block = b"".join(lines[start - 1:end])
    digest = hashlib.sha256(block).hexdigest()
    _need(digest == metadata.get("source_sha256") ==
          metadata.get("source_bytes_sha256") and
          lines[start - 1].strip() == b"/*@" and
          lines[end - 1].strip() == b"@*/",
          "checked cleanup helper source block hash/boundaries")
    matches = [index for index, line in enumerate(lines, 1)
               if re.match(rb"\s*lem\s+a1_cleanup_option_ref\b", line)]
    _need(matches == [body_start] and
          lines[body_start - 1].startswith(b"lem a1_cleanup_option_ref<'a, T>") and
          lines[body_end - 1].strip() == b"}",
          "checked cleanup helper source declaration is missing or ambiguous")
    rows = ast_gates.functions(ast_text)
    named = [row for row in rows if row.get("name") == metadata["name"]]
    _need(len(named) == 1, "one exact checked cleanup helper AST function required")
    row = named[0]
    _need(row.get("kind") == "definition",
          "checked cleanup helper AST Func must be a definition")
    lemma_auto, lemma_trigger = ast_gates.node(row["fields"][1], "Lemma", 2)
    _need(ast_gates.atom(lemma_auto) == "false",
          "checked cleanup helper AST lemma must be manual (auto=false)")
    ast_gates.atom(lemma_trigger, "None")
    func_span = _ast_source_span(row["fields"][0])
    header_coords = _ast_source_coordinates(row["fields"][0])
    body, = ast_gates.node(row["fields"][10], "Some", 1)
    _, close = ast_gates.node(body, "tuple", 2)
    close_span = _ast_source_span(close)
    close_coords = _ast_source_coordinates(close)
    name_bytes = metadata["name"].encode("ascii")
    header = lines[body_start - 1]
    name_col = header.find(name_bytes) + 1
    close_col = lines[body_end - 1].find(b"}") + 1
    _need(name_col > 0 and close_col > 0 and header_coords ==
          (body_start, name_col, body_start, name_col + len(name_bytes)) and
          func_span == (body_start, body_start) and
          close_span is not None and close_span == (body_end, body_end) and
          close_coords is not None and close_coords[0] == body_end and
          close_coords[1] == close_col,
          "checked cleanup helper AST header/close locations differ from certified body")
    effective_span = (func_span[0], close_span[1])
    selected = []
    for candidate in rows:
        if candidate.get("kind") != "definition":
            continue
        span = _ast_source_span(candidate["fields"][0])
        if span is None:
            continue
        candidate_body, = ast_gates.node(candidate["fields"][10], "Some", 1)
        _, candidate_close = ast_gates.node(candidate_body, "tuple", 2)
        close = _ast_source_span(candidate_close)
        _need(close is not None and close[1] >= span[0],
              "AST definition effective interval is malformed")
        effective = (span[0], close[1])
        if effective[0] <= body_start <= effective[1]:
            selected.append(candidate)
    _need(len(selected) == 1 and selected[0] is row,
          "helper focus line selects an ambiguous AST function interval")
    return {"classification": "ONE_SOURCE_INTERVAL_SELECTED_CHECKED_LEMMA",
            "focus_line": body_start, "body_count_from_intervals": 1,
            "selected": {"name": row["name"], "kind": "lemma",
                         "func_span": effective_span,
                         "header_span": func_span, "close_span": close_span,
                         "effective_span": effective_span,
                         "header_coordinates": header_coords,
                         "close_coordinates": close_coords},
            "source_block_sha256": digest, "proof_credit": False}
