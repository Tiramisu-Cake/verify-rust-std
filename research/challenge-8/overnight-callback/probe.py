#!/usr/bin/env python3
"""Generate and run the one-call callback diagnostic on GitHub-hosted Linux."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


PROFILE_SOURCE = "f76012fb518703b1d98e243ac4f487f16877cfcb"
SMALLSORT_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
STOCK_FNMUT_SHA256 = "599abd73bc551804b41f2d82aeb9c4a42d4c1c2b40396cbabfb2099c0abe1564"
SOURCE_CALL = b"is_less(&*v_base.add(1), &*v_base);"
CASES = ("callback_positive", "callback_false_post")
UNWIND_MATRIX_CASES = (
    "unwind_missing_marker",
    "unwind_duplicate_marker",
    "unwind_moved_marker",
    "unwind_foreign_marker",
    "unwind_false_post",
    "unwind_duplicate_f_owner",
    "unwind_duplicate_left_owner",
)
GHOST_BLOCK = re.compile(rb"/\*@.*?@\*/", re.S)
GHOST_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")
UNWIND_MARKER = re.compile(
    rb"        /\*@ \{\n"
    rb"            __vf_callback_unwind_pair\(\);\n"
    rb"            \{ close comparison_debt::<T>\([^\n]+\); \}\n"
    rb"            \{ recover_pair::<T>\(left, right\); \}\n"
    rb"        \} @\*/\n")


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hosted_only() -> None:
    need(os.environ.get("GITHUB_ACTIONS") == "true" and
         os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
         os.environ.get("RUNNER_OS") == "Linux",
         "callback probe is hosted-only (GitHub-hosted Linux required)")


def strip_ghost(data: bytes) -> bytes:
    data = GHOST_BLOCK.sub(b"", data)
    return GHOST_LINE.sub(b"", data)


def source_certificate(repo_root: Path, source_checkout: Path,
                       tool_home: Path) -> dict:
    source = repo_root / "library/core/src/slice/sort/shared/smallsort.rs"
    source_bytes = source.read_bytes()
    need(sha(source_bytes) == SMALLSORT_SHA256,
         "pinned SmallSort 26.10 source hash differs")
    need(source_bytes.count(SOURCE_CALL) == 1,
         "actual first comparator call is missing or ambiguous")

    vf_head = subprocess.run(
        ["git", "-C", str(source_checkout), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True).stdout.strip()
    need(vf_head == PROFILE_SOURCE,
         f"VeriFast source base differs: {vf_head}")
    effective_specs = tool_home / "bin/rust/std/lib.rsspec"
    effective_bytes = effective_specs.read_bytes()
    start_anchor = b"    trait FnMut<Args> {"
    end_anchor = b"    trait Fn<Args> {"

    def fnmut_clause(data: bytes) -> bytes:
        start = data.find(start_anchor)
        end = data.find(end_anchor, start + len(start_anchor))
        need(start >= 0 and end > start,
             "cannot locate the stock FnMut contract")
        return data[start:end]

    clause = fnmut_clause(effective_bytes)
    need(sha(clause) == STOCK_FNMUT_SHA256,
         "active profile changed the pinned stock FnMut contract")
    need(b"<Args>.own(t, args)" in clause and
         b"<Self>.own(t, self0)" in clause and
         b"<Self>.own(t, self1)" in clause and
         b"on_unwind_ens thread_token(t)" in clause,
         "stock FnMut resource contract shape differs")
    return {
        "classification": "SOURCE_BOUND_CALLBACK_DIAGNOSTIC",
        "proof_sha": subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip(),
        "verifast_source_base": vf_head,
        "small_sort_source": str(source.relative_to(repo_root)),
        "small_sort_sha256": sha(source_bytes),
        "actual_first_call": SOURCE_CALL.decode(),
        "stock_fnmut_clause_sha256": STOCK_FNMUT_SHA256,
        "active_fnmut_clause_matches_stock": True,
        "tool_home_fnmut_spec_sha256": sha(effective_bytes),
        "predeclared_functions": ["callback_positive", "callback_false_post"],
        "trusted_boundary": "stock 26.10 FnMut contract and compiler/source correspondence",
        "actual_sort4_proved": False,
    }


def select_case(template: bytes, name: str) -> bytes:
    begin = f"// CASE_BEGIN {name}\n".encode()
    end = f"// CASE_END {name}\n".encode()
    all_begins = [f"// CASE_BEGIN {case}\n".encode() for case in CASES]
    all_ends = [f"// CASE_END {case}\n".encode() for case in CASES]
    need(all(template.count(marker) == 1
             for marker in (*all_begins, *all_ends)),
         "fixture case markers are missing or duplicated")
    start = template.index(begin) + len(begin)
    stop = template.index(end, start)
    first_case = min(template.index(marker) for marker in all_begins)
    need(stop > start and start >= first_case,
         f"fixture case {name} is empty or out of order")
    # Keep the common ghost declarations, but never include an earlier case
    # when selecting a later one. That keeps each generated proof isolated.
    return template[:first_case] + template[start:stop]


def false_normal_post_span(source: bytes) -> tuple[int, int, int] | None:
    """Return (normal-ens start, end, false-line), all one-based."""
    lines = source.decode().splitlines()
    spans = []
    for start, line in enumerate(lines):
        if re.match(r"^\s*ens\b", line) is None:
            continue
        content = []
        end = None
        for index in range(start, len(lines)):
            content.append(lines[index])
            if ";" in lines[index]:
                end = index
                break
            if "@*/" in lines[index]:
                break
        if end is None:
            continue
        match = re.search(r"\bfalse\s*;", "\n".join(content))
        if match is None:
            continue
        false_line = start + 1 + "\n".join(content).count("\n", 0, match.start())
        spans.append((start + 1, end + 1, false_line))
    return spans[0] if len(spans) == 1 else None


def unwind_post_span(source: bytes) -> tuple[int, int]:
    lines = source.decode().splitlines()
    starts = [index for index, line in enumerate(lines)
              if re.match(r"^\s*on_unwind_ens\b", line)]
    need(len(starts) == 1, "unwind post is missing or ambiguous")
    start = starts[0]
    ends = [index for index in range(start, len(lines))
            if ";" in lines[index]]
    need(ends and all("@*/" not in line for line in lines[start:ends[0]]),
         "unwind post has no matching semicolon")
    return start + 1, ends[0] + 1


def matrix_source(template: bytes, variant: str) -> tuple[bytes, str]:
    """Mutate only a copy of the positive fixture; never relax its runtime call."""
    source = select_case(template, "callback_positive")
    target_fn = "callback_positive"
    markers = list(UNWIND_MARKER.finditer(source))
    need(len(markers) == 1, "positive callback marker shape changed")
    marker = markers[0].group()
    if variant == "unwind_missing_marker":
        source = source.replace(marker, b"", 1)
    elif variant == "unwind_duplicate_marker":
        source = source.replace(marker, marker + marker, 1)
    elif variant == "unwind_moved_marker":
        source = source.replace(marker, marker + b"\n", 1)
    elif variant == "unwind_foreign_marker":
        source = source.replace(b"fn callback_positive<",
                                b"fn callback_foreign<", 1)
        target_fn = "callback_foreign"
    else:
        start, end = unwind_post_span(source)
        lines = source.splitlines(keepends=True)
        post = b"".join(lines[start - 1:end])
        need(post.count(b"<F>.own(t, less_after)") == 1 and
             post.count(b"<T>.own(t, left_after)") == 1,
             "unwind post resource anchors changed")
        if variant == "unwind_false_post":
            amended = post.replace(b"<F>.own(t, less_after);",
                                   b"<F>.own(t, less_after) &*& false;", 1)
        elif variant == "unwind_duplicate_f_owner":
            amended = post.replace(
                b"<F>.own(t, less_after);",
                b"<F>.own(t, less_after) &*& <F>.own(t, less_after);", 1)
        elif variant == "unwind_duplicate_left_owner":
            amended = post.replace(
                b"<T>.own(t, left_after) &*&",
                b"<T>.own(t, left_after) &*& <T>.own(t, left_after) &*&", 1)
        else:
            raise ValueError(f"unknown unwind matrix variant: {variant}")
        need(amended != post, f"matrix post mutation was inert: {variant}")
        lines[start - 1:end] = [amended]
        source = b"".join(lines)
    need(source != select_case(template, "callback_positive"),
         f"matrix mutation was inert: {variant}")
    return source, target_fn


def mir_balanced_pairs(text: str) -> dict[int, int]:
    """Return matching () and [] delimiters, ignoring quoted strings."""
    pairs: dict[int, int] = {}
    stack: list[tuple[str, int]] = []
    quoted = False
    escaped = False
    for index, char in enumerate(text):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char in "([":
            stack.append((char, index))
        elif char in ")]":
            if not stack:
                continue
            opening, start = stack[-1]
            if (opening, char) in (("(", ")"), ("[", "]")):
                stack.pop()
                pairs[start] = index
    return pairs


def mir_enclosing_record(text: str, marker: str,
                         pairs: dict[int, int]) -> tuple[int, int]:
    marker_at = text.find(marker)
    need(marker_at >= 0 and text.find(marker, marker_at + 1) < 0,
         f"MIR marker missing or ambiguous: {marker}")
    candidates = [(start, end) for start, end in pairs.items()
                  if text[start] == "(" and start < marker_at < end]
    need(candidates, f"no balanced record contains MIR marker: {marker}")
    return min(candidates, key=lambda pair: pair[1] - pair[0])


def mir_list_records(text: str, marker: str,
                     pairs: dict[int, int]) -> list[str]:
    marker_at = text.find(marker)
    need(marker_at >= 0 and text.find(marker, marker_at + 1) < 0,
         f"MIR list missing or ambiguous: {marker}")
    start = text.find("[", marker_at + len(marker))
    need(start >= 0 and start in pairs,
         f"MIR list is not balanced: {marker}")
    end = pairs[start]
    result = []
    cursor = start + 1
    while cursor < end:
        while cursor < end and text[cursor] in " \t\r\n,":
            cursor += 1
        if cursor == end:
            break
        need(text[cursor] == "(" and cursor in pairs,
             f"unexpected MIR list entry for {marker}")
        item_end = pairs[cursor]
        result.append(text[cursor:item_end + 1])
        cursor = item_end + 1
    return result


def mir_local(record: str, context: str) -> str:
    matches = re.findall(r'local = \(name = "(_\d+)"\)', record)
    need(len(matches) == 1, f"expected one MIR local in {context}")
    return matches[0]


def mir_lhs(statement: str) -> str | None:
    match = re.search(r'lhsPlace = \(\s*local = \(name = "(_\d+)"\)',
                      statement)
    return match.group(1) if match else None


def callback_mir_alias_audit(decoded: bytes, mode: str, source: bytes,
                             case_name: str) -> dict:
    """Trace both actual call tuple fields back to the named source inputs."""
    text = decoded.decode(errors="replace")
    pairs = mir_balanced_pairs(text)
    body_start, body_end = mir_enclosing_record(
        text, f'defPath = "{case_name}"', pairs)
    body = text[body_start:body_end + 1]
    source_text = source.decode()
    source_lines = source_text.splitlines()
    left_lines = [index for index, line in enumerate(source_lines, 1)
                  if line.strip() == "left: *const T,"]
    right_lines = [index for index, line in enumerate(source_lines, 1)
                   if line.strip() == "right: *const T,"]
    need(len(left_lines) == len(right_lines) == 1,
         "source input declarations are missing or ambiguous")

    body_pairs = mir_balanced_pairs(body)
    body_local_decls = mir_list_records(body, "localDecls =", body_pairs)
    input_ids = {}
    for local_id, expected_line in (("_1", left_lines[0]),
                                    ("_2", right_lines[0])):
        rows = [row for row in body_local_decls
                if f'id = (name = "{local_id}")' in row]
        need(len(rows) == 1, f"source-bound input local is missing: {local_id}")
        line_match = re.search(
            r"sourceInfo = \(\s*span = \(\s*regular = \(\s*lo = \(.*?line = (\d+)",
            rows[0], re.S)
        need(line_match is not None and int(line_match.group(1)) == expected_line,
             f"MIR input {local_id} no longer maps to its source parameter")
        input_ids[local_id] = expected_line

    blocks = mir_list_records(body, "basicBlocks =", body_pairs)
    call_blocks = [block for block in blocks
                   if block.count('name = "core::ops::FnMut::call_mut"') == 1]
    need(len(call_blocks) == 1, "actual FnMut::call_mut block missing or ambiguous")
    block = call_blocks[0]
    block_pairs = mir_balanced_pairs(block)
    statements = mir_list_records(block, "statements =", block_pairs)
    terminator_start = block.find("terminator = (")
    need(terminator_start >= 0, "FnMut call block has no terminator")
    terminator = block[terminator_start:]
    call_args = mir_list_records(terminator, "args =", mir_balanced_pairs(terminator))
    need(len(call_args) == 2, "FnMut call does not have exactly receiver and Args")
    args_local = mir_local(call_args[1], "FnMut::call_mut Args operand")

    tuple_assignments = [statement for statement in statements
                         if mir_lhs(statement) == args_local and
                         "aggregateKind = (tuple = void)" in statement]
    need(len(tuple_assignments) == 1,
         "FnMut Args local has no unique two-field tuple assignment")
    tuple_record = tuple_assignments[0]
    tuple_operands = mir_list_records(
        tuple_record, "operands =", mir_balanced_pairs(tuple_record))
    need(len(tuple_operands) == 2, "FnMut Args tuple is not arity two")
    field_refs = [mir_local(operand, "FnMut Args tuple field")
                  for operand in tuple_operands]
    need(field_refs[0] != field_refs[1], "FnMut Args tuple duplicates a field local")

    chains = []
    for field_ref in field_refs:
        ref_assignments = [statement for statement in statements
                           if mir_lhs(statement) == field_ref and
                           "rhsRvalue = (" in statement and "ref = (" in statement]
        need(len(ref_assignments) == 1,
             f"tuple reference field has no unique borrow assignment: {field_ref}")
        ref_record = ref_assignments[0]
        ref_pairs = mir_balanced_pairs(ref_record)
        ref_place_start = ref_record.find("place = (")
        need(ref_place_start >= 0, "tuple reference assignment has no place")
        ref_open = ref_record.find("(", ref_place_start)
        ref_close = ref_pairs.get(ref_open)
        need(ref_close is not None, "tuple reference place is malformed")
        ref_place = ref_record[ref_open:ref_close + 1]
        borrow_local = mir_local(ref_place, "call-reference borrow place")
        ref_projection = re.search(r"projection = \[(.*?)\]", ref_place, re.S)
        need(ref_projection is not None and "deref = void" in ref_projection.group(1),
             "tuple field reference is not formed from its borrow local")

        borrow_assignments = [statement for statement in statements
                              if mir_lhs(statement) == borrow_local and
                              "rhsRvalue = (" in statement and "ref = (" in statement]
        need(len(borrow_assignments) == 1,
             f"call-reference borrow has no unique source assignment: {borrow_local}")
        borrow_record = borrow_assignments[0]
        borrow_pairs = mir_balanced_pairs(borrow_record)
        borrow_place_start = borrow_record.find("place = (")
        need(borrow_place_start >= 0, "source borrow assignment has no place")
        borrow_open = borrow_record.find("(", borrow_place_start)
        borrow_close = borrow_pairs.get(borrow_open)
        need(borrow_close is not None, "source borrow place is malformed")
        source_place = borrow_record[borrow_open:borrow_close + 1]
        source_local = mir_local(source_place, "source borrow place")
        projection = re.search(r"projection = \[(.*?)\]", source_place, re.S)
        need(projection is not None and "deref = void" in projection.group(1),
             "actual comparator reference is not a dereference of an input pointer")
        chains.append({"tuple_field_local": field_ref,
                       "borrow_local": borrow_local,
                       "source_input_local": source_local})

    need([chain["source_input_local"] for chain in chains] == ["_1", "_2"],
         "actual Args tuple fields do not preserve left/right source-input order")
    return {
        "classification": "ACTUAL_CALLBACK_MIR_ARGUMENT_ALIAS_CHECK",
        "mir_mode": mode,
        "passed": True,
        "source_input_lines": input_ids,
        "args_local": args_local,
        "field_chains": chains,
        "checked_both_actual_borrow_chains_and_fnmut_args_tuple": True,
        "trusted_boundary": (
            "pinned Rust MIR/source correspondence and ghost precreate_ref mapping; "
            "the structural check traces both input parameters through the actual "
            "FnMut::Args aggregate without assuming temporary-local numbers"
        ),
    }


def generate_case(repo_root: Path, source_checkout: Path, tool_home: Path,
                  case_name: str, destination: Path) -> dict:
    need(case_name in (*CASES, *UNWIND_MATRIX_CASES),
         f"unknown fixture case: {case_name}")
    template_path = Path(__file__).with_name("callback-cases.rs")
    template = template_path.read_bytes()
    selected, target_fn = (matrix_source(template, case_name)
                           if case_name in UNWIND_MATRIX_CASES
                           else (select_case(template, case_name), case_name))
    original = strip_ghost(selected)
    positive_runtime = strip_ghost(select_case(template, "callback_positive"))
    false_runtime = strip_ghost(select_case(template, "callback_false_post"))
    positive_runtime = positive_runtime.replace(
        b"pub unsafe fn callback_positive", b"pub unsafe fn CALLBACK")
    false_runtime = false_runtime.replace(
        b"pub unsafe fn callback_false_post", b"pub unsafe fn CALLBACK")
    need(positive_runtime == false_runtime,
         "positive and false-post fixtures differ in ghost-stripped Rust")
    need(b"left: *const T,\n    right: *const T,\n    is_less: &mut F," in original and
         b"F: FnMut(&T, &T) -> bool" in original,
         "callback input order or unrestricted generic FnMut bound changed")
    need(strip_ghost(selected) == original,
         "verified fixture does not strip to its original source")
    need(selected.count(b"pub unsafe fn " + target_fn.encode()) == 1 and
         selected.count(b"is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*left, &*right)") == 1,
         "selected fixture is not a single exact generic callback call")
    need(original.count(b"is_less(&*left, &*right)") == 1,
         "ghost-free fixture call expression differs")

    destination.mkdir(parents=True, exist_ok=False)
    (destination / "original").mkdir()
    (destination / "verified").mkdir()
    (destination / "original/lib.rs").write_bytes(original)
    (destination / "verified/lib.rs").write_bytes(selected)
    record = source_certificate(repo_root, source_checkout, tool_home)
    target_contract_span = false_normal_post_span(selected)
    if case_name == "callback_false_post":
        need(target_contract_span is not None,
             "false-post target normal ens span missing or ambiguous")
    else:
        need(target_contract_span is None,
             "positive case unexpectedly contains false in a normal post")
    record.update({
        "case": case_name,
        "target_function": target_fn,
        "unwind_matrix_variant": case_name if case_name in UNWIND_MATRIX_CASES else None,
        "unwind_marker_count": selected.count(b"__vf_callback_unwind_pair();"),
        "template_sha256": sha(template),
        "verified_sha256": sha(selected),
        "original_sha256": sha(original),
        "ghost_strip_exact": strip_ghost(selected) == original,
        "positive_false_ghost_stripped_runtime_identical": True,
        "target_function_count": 1,
        "actual_callback_call_count": 1,
        "expected_false_post_span": list(target_contract_span[:2])
            if target_contract_span else None,
        "expected_false_post_line": target_contract_span[2]
            if target_contract_span else None,
        "expected_unwind_post_span": list(unwind_post_span(selected)),
        "domain": "generic sized T and F: FnMut(&T, &T) -> bool; two separated initialized slots",
        "normal_post": "current full T resources for both slots and current F resource; unconstrained bool",
        "unwind_post": "current full T resources for both slots and current F resource; no result or rollback",
        "proof_premises": [],
        "effective_patches": "provided common O2/O3 tool profile; FnMut contract must remain stock",
    })
    if case_name in UNWIND_MATRIX_CASES:
        record["predeclared_functions"] = [target_fn]
    (destination / "fixture.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def run_stage(name: str, argv: list[str], root: Path, env: dict[str, str],
              source_hashes: dict[str, str], timeout_seconds: int,
              stdin_name: str | None = None,
              stdout_name: str | None = None) -> dict:
    paths = {rel: root / rel for rel in source_hashes}
    before = {rel: sha(path.read_bytes()) for rel, path in paths.items()}
    need(before == source_hashes,
         f"source differs before stage {name}")
    stdout_path = root / (stdout_name or f"{name}.log")
    stderr_path = root / f"{name}-stderr.log" if stdout_name else stdout_path
    with stdout_path.open("wb") as stdout:
        stderr = stderr_path.open("wb") if stderr_path != stdout_path else subprocess.STDOUT
        try:
            stdin = (root / stdin_name).open("rb") if stdin_name else open(os.devnull, "rb")
            try:
                status = subprocess.run(
                    ["/usr/bin/time", "-v", "-o", str(root / f"{name}-resources.txt"),
                     "timeout", "--signal=TERM", "--kill-after=10s",
                     f"{timeout_seconds}s", *argv],
                    cwd=root, env=env, stdin=stdin, stdout=stdout, stderr=stderr,
                    check=False).returncode
            finally:
                stdin.close()
        except OSError as exc:
            status = 127
            (stderr if stderr_path != stdout_path else stdout).write(
                f"stage launch error: {exc}\n".encode())
        finally:
            if stderr_path != stdout_path:
                stderr.close()
    after = {rel: sha(path.read_bytes()) for rel, path in paths.items()}
    record = {
        "argv": argv, "exit": status, "timeout_seconds": timeout_seconds,
        "source_before": before, "source_after": after,
        "source_exact": before == after == source_hashes,
        "stdout": stdout_path.name, "stderr": stderr_path.name,
    }
    (root / f"{name}-stage.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def run_case(repo_root: Path, source_checkout: Path, tool_home: Path,
             schema: Path, compiler_sysroot: str, evidence: Path,
             case_name: str, deadline_epoch: int,
             capture_ast_diagnostic: bool) -> dict:
    case_dir = evidence / case_name
    fixture = generate_case(repo_root, source_checkout, tool_home,
                            case_name, case_dir)
    hash_tool = lambda path: sha(path.read_bytes())
    compiler = subprocess.run(
        ["rustc", "--version", "--verbose"], check=True,
        capture_output=True, text=True).stdout
    fixture["hosted_profile"] = {
        "compiler_version_verbose": compiler,
        "tool_hashes": {
            name: hash_tool(tool_home / "bin" / name)
            for name in ("verifast", "vf-rust-mir-exporter", "refinement-checker")
        },
        "schema_sha256": hash_tool(schema),
        "effective_fnmut_contract_sha256": sha(
            (tool_home / "bin/rust/std/lib.rsspec").read_bytes()),
    }
    (case_dir / "fixture.json").write_text(
        json.dumps(fixture, indent=2, sort_keys=True) + "\n")
    source_hashes = {
        "original/lib.rs": fixture["original_sha256"],
        "verified/lib.rs": fixture["verified_sha256"],
    }
    env = os.environ.copy()
    for key in ("SORT4_MAYBEUNINIT_REPO_ROOT", "SORT4_SELECT_INTRINSIC_REPO_ROOT",
                "SORT4_POINTER_DROP_REPO_ROOT", "SORT4_MAYBEUNINIT_NEW_REPO_ROOT"):
        env.pop(key, None)
    env["PATH"] = str(tool_home / "bin") + os.pathsep + env.get("PATH", "")
    stages: dict[str, dict] = {}

    def stage_budget(cap: int) -> int | None:
        remaining = deadline_epoch - int(time.time())
        return min(cap, remaining - 10) if remaining > 10 else None

    def execute(name: str, argv: list[str], cap: int,
                stdin_name: str | None = None,
                stdout_name: str | None = None) -> dict:
        seconds = stage_budget(cap)
        if seconds is None:
            return {"exit": None, "skipped": "artifact and cleanup reserve"}
        return run_stage(name, argv, case_dir, env, source_hashes, seconds,
                         stdin_name, stdout_name)

    exporter = str(tool_home / "bin/vf-rust-mir-exporter")
    stages["normal-export"] = execute(
        "normal-export", [exporter, "verified/lib.rs",
                          f"--sysroot={compiler_sysroot}", "--edition", "2021"],
        90, stdout_name="normal-mir.bin")
    if stages["normal-export"]["exit"] == 0:
        stages["normal-decode"] = execute(
            "normal-decode", ["capnp", "decode", str(schema), "VfMir"],
            60, "normal-mir.bin", "normal-mir.txt")
    else:
        stages["normal-decode"] = {"exit": None, "skipped": "normal export failed"}

    stages["readonly-export"] = execute(
        "readonly-export", [exporter, "verified/lib.rs",
                            f"--sysroot={compiler_sysroot}", "--edition", "2021",
                            "--vf-rust-mir-exporter:preprocess-readonly"],
        90, stdout_name="readonly-mir.bin")
    if stages["readonly-export"]["exit"] == 0:
        stages["readonly-decode"] = execute(
            "readonly-decode", ["capnp", "decode", str(schema), "VfMir"],
            60, "readonly-mir.bin", "readonly-mir.txt")
    else:
        stages["readonly-decode"] = {"exit": None, "skipped": "readonly export failed"}

    alias_audits = {}
    verified_source = (case_dir / "verified/lib.rs").read_bytes()
    target_fn = fixture["target_function"]
    for mode in ("normal", "readonly"):
        mir_path = case_dir / f"{mode}-mir.txt"
        alias_audits[mode] = (callback_mir_alias_audit(
            mir_path.read_bytes(), mode, verified_source, target_fn)
                              if mir_path.is_file() else None)
    alias_audit_ok = all(row is not None and row["passed"]
                         for row in alias_audits.values())

    verifier = str(tool_home / "bin/verifast")
    verifier_argv = [verifier, "-rustc_args", "--edition 2021",
                     "-verbose", "1", "verified/lib.rs"]
    stages["full-verification"] = execute(
        "full-verification", verifier_argv, 180)
    if capture_ast_diagnostic:
        stages["ast-diagnostic"] = execute(
            "ast-diagnostic", [verifier, "-rustc_args", "--edition 2021",
                               "-verbose", "1", "-dump_ast_with_locs",
                               "verified-ast.txt", "verified/lib.rs"], 90)
    else:
        stages["ast-diagnostic"] = {"exit": None, "skipped": "not requested"}
    stages["refinement"] = execute(
        "refinement", [str(tool_home / "bin/refinement-checker"),
                       "--rustc-args", "--edition 2021",
                       "original/lib.rs", "verified/lib.rs"], 90)

    full_log_path = case_dir / "full-verification.log"
    full_log = full_log_path.read_text(errors="replace") if full_log_path.is_file() else ""
    target_headers = re.findall(
        rf"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): Verifying function '{re.escape(target_fn)}'",
        full_log)
    errors = [line for line in full_log.splitlines() if ": error:" in line]
    source_integrity = all(
        row.get("source_exact") is True for row in stages.values()
        if "source_exact" in row)
    support_stages = ("normal-export", "normal-decode", "readonly-export",
                      "readonly-decode", "refinement")
    support_ok = all(stages.get(name, {}).get("exit") == 0 for name in support_stages) and \
        alias_audit_ok
    classification = "INCONCLUSIVE"
    intended_negative = False
    if case_name == "callback_false_post" and support_ok and source_integrity and \
            stages["full-verification"]["exit"] == 1 and len(target_headers) == 1 and \
            len(errors) == 1:
        first_line, last_line = fixture["expected_false_post_span"]
        intended_negative = any(
            "Cannot prove false" in error and
            (location := re.search(r"verified/lib\.rs\((\d+),", error)) is not None and
            first_line <= int(location.group(1)) <= last_line
            for error in errors)
        if intended_negative:
            classification = "INTENDED_FALSE_NORMAL_POST"
    if case_name == "callback_positive" and support_ok and source_integrity and \
            stages["full-verification"]["exit"] == 0 and len(target_headers) == 1:
        classification = "DIAGNOSTIC_POSITIVE_CANDIDATE_REVIEW_REQUIRED"
    admission_certificates = {
        "unwind_missing_marker": ("callback_positive", 0,
                                  "exact callback fixture requires one marker; other bodies forbid it"),
        "unwind_duplicate_marker": ("callback_positive", 2,
                                    "exact callback fixture requires one marker; other bodies forbid it"),
        "unwind_moved_marker": ("callback_positive", 1,
                                "marker is not immediately before the actual call span"),
        "unwind_foreign_marker": ("callback_foreign", 1,
                                  "exact callback fixture requires one marker; other bodies forbid it"),
    }
    fatal_lines = [line for line in full_log.splitlines()
                   if line.startswith("Fatal error:")]
    certificate = admission_certificates.get(case_name)
    if certificate is not None and support_ok and source_integrity and \
            target_fn == certificate[0] and \
            fixture["unwind_marker_count"] == certificate[1] and \
            stages["full-verification"]["exit"] == 2 and \
            len(target_headers) == 0 and len(errors) == 0 and \
            fatal_lines == [
                'Fatal error: exception Failure("CALLBACK-UNWIND: '
                f'source/MIR certificate mismatch: {certificate[2]}")'
            ]:
        classification = "INTENDED_UNWIND_MARKER_ADMISSION_REJECTION"
        intended_negative = True
    if case_name == "unwind_false_post" and support_ok and source_integrity and \
            stages["full-verification"]["exit"] == 1 and len(target_headers) == 1 and \
            len(errors) == 1:
        first_line, last_line = fixture["expected_unwind_post_span"]
        if "Cannot prove false" in errors[0] and \
                (location := re.search(r"verified/lib\.rs\((\d+),", errors[0])) is not None and \
                first_line <= int(location.group(1)) <= last_line:
            classification = "INTENDED_FALSE_UNWIND_POST"
            intended_negative = True
    if case_name in {"unwind_duplicate_f_owner", "unwind_duplicate_left_owner"} and \
            support_ok and source_integrity and \
            stages["full-verification"]["exit"] == 1 and \
            len(target_headers) == 1 and len(errors) == 1:
        first_line, last_line = fixture["expected_unwind_post_span"]
        location = re.search(r"verified/lib\.rs\((\d+),", errors[0])
        if location is not None and first_line <= int(location.group(1)) <= last_line and \
                "No matching heap chunks" in errors[0]:
            classification = "INTENDED_DUPLICATE_UNWIND_OWNER_CANDIDATE_REVIEW_REQUIRED"
            intended_negative = True
    result = {
        "classification": classification,
        "accepted_callback_component": False,
        "actual_sort4_proved": False,
        "case": case_name,
        "target_function": target_fn,
        "source_integrity": source_integrity,
        "support_exports_decode_refinement_all_zero": support_ok,
        "target_timed_header_count": len(target_headers),
        "target_timed_headers": target_headers,
        "first_error": errors[0] if errors else None,
        "all_errors": errors,
        "intended_false_post": classification in
            {"INTENDED_FALSE_NORMAL_POST", "INTENDED_FALSE_UNWIND_POST"},
        "intended_negative": intended_negative,
        "actual_argument_alias_audit": alias_audits,
        "actual_argument_alias_audit_passed": alias_audit_ok,
        "normal_mir_sha256": sha((case_dir / "normal-mir.txt").read_bytes())
            if (case_dir / "normal-mir.txt").is_file() else None,
        "readonly_mir_sha256": sha((case_dir / "readonly-mir.txt").read_bytes())
            if (case_dir / "readonly-mir.txt").is_file() else None,
        "stages": stages,
    }
    (case_dir / "outcome.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"case": case_name,
                      "classification": classification,
                      "first_error": result["first_error"],
                      "stages": {name: stage.get("exit")
                                 for name, stage in stages.items()}},
                     sort_keys=True), flush=True)
    return result


def main() -> None:
    hosted_only()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source-checkout", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--case", choices=(*CASES, *UNWIND_MATRIX_CASES, "all"),
                        default="all")
    parser.add_argument("--unwind-matrix", action="store_true",
                        help="run isolated unwind admission and post controls")
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument("--prepare-only", action="store_true",
                        help="generate/hash isolated source pairs without invoking tools")
    parser.add_argument("--capture-ast-diagnostic", action="store_true",
                        help="run separate optional -dump_ast_with_locs diagnostic")
    args = parser.parse_args()
    args.repo_root = args.repo_root.resolve()
    args.source_checkout = args.source_checkout.resolve()
    args.tool_home = args.tool_home.resolve()
    args.schema = args.schema.resolve()
    args.evidence = args.evidence.resolve()
    need(args.schema.is_file() and args.tool_home.is_dir() and
         args.source_checkout.is_dir(), "pinned tool/source inputs are missing")
    args.evidence.mkdir(parents=True, exist_ok=False)
    need(args.unwind_matrix or args.case not in UNWIND_MATRIX_CASES,
         "unwind matrix case requires --unwind-matrix")
    names = ((*CASES, *UNWIND_MATRIX_CASES) if args.unwind_matrix else CASES) \
        if args.case == "all" else (args.case,)
    outcomes = {}
    if args.prepare_only:
        for case_name in names:
            record = generate_case(
                args.repo_root, args.source_checkout, args.tool_home,
                case_name, args.evidence / case_name)
            outcomes[case_name] = {
                "classification": "PREPARED_NOT_RUN",
                "ghost_strip_exact": record["ghost_strip_exact"],
                "verified_sha256": record["verified_sha256"],
                "original_sha256": record["original_sha256"],
            }
    else:
        for case_name in names:
            if args.deadline_epoch - int(time.time()) <= 15:
                outcomes[case_name] = {"classification": "NOT_RUN",
                                       "reason": "artifact and cleanup reserve"}
                continue
            outcomes[case_name] = run_case(
                args.repo_root, args.source_checkout, args.tool_home,
                args.schema, args.compiler_sysroot, args.evidence,
                case_name, args.deadline_epoch,
                args.capture_ast_diagnostic)
    aggregate = {
        "profile_source_base": PROFILE_SOURCE,
        "cases": outcomes,
        "all_accepted": False,
        "actual_sort4_proved": False,
    }
    (args.evidence / "summary.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
