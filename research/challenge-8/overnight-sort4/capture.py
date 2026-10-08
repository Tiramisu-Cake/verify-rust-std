#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Capture exact sort4_stable source, full MIR, and the first verifier boundary.

This hosted-only diagnostic is intentionally not an actual sort4 proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time


SOURCE_REL = Path("library/core/src/slice/sort/shared/smallsort.rs")
SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
FUNCTION_HEADER = (
    b"pub unsafe fn sort4_stable<T, F: FnMut(&T, &T) -> bool>(\n"
    b"    v_base: *const T,\n"
    b"    dst: *mut T,\n"
    b"    is_less: &mut F,\n"
    b") "
)
NEXT_SOURCE_ANCHOR = (
    b"\n\n/// SAFETY: The caller MUST guarantee that `v_base` is valid for 8 reads and"
)
SOURCE_CALL_COUNTS = {
    b"is_less(": 5,
    b"hint::select_unpredictable(": 8,
    b"ptr::copy_nonoverlapping(": 4,
}
FNMUT_TARGET = "FnMut::call_mut"
GHOST_BLOCK = re.compile(rb"/\*@.*?@\*/(?:\r?\n)?", re.S)
GHOST_LINE = re.compile(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)")
FNMUT_CALL_NAME = re.compile(r'fnDef = \(\s*id = \(\s*name = "([^"]+)"')
FUNCTION_DEF = re.compile(r'defPath = "([^"]+)"')

PREFIX = (
    b"#![feature(const_trait_impl)]\n"
    b"#![allow(internal_features)]\n\n"
    b"use std::{hint, ptr};\n\n"
)
CAPTURE_CONTRACT = b"""/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    *is_less |-> ?less_before &*& <F>.own(t, less_before);
@*/
/*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
/*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
"""

MEMORY_PRE_INTERIOR_LEMMA = b"""/*@
lem interior_pointer_limits<T>(base: *T, count: usize, index: usize)
    req [?f]base[..count] |-> ?xs &*& 1 <= count &*& 0 <= index &*& index <= count;
    ens [f]base[..count] |-> xs &*& pointer_within_limits(base + index) == true;
{
    open array(base, count, xs);
    points_to_limits(base);
    close [f]array(base, count, xs);
    note(0 <= std::mem::size_of::<T>());
    array_inv::<T>();
    mul_mono_l(0, index, std::mem::size_of::<T>());
    mul_mono_l(index, count, std::mem::size_of::<T>());
    note(pointer_within_limits(base));
    note(pointer_within_limits(base + count));
}
@*/
"""
MEMORY_PRE_BOUND_CALL = (
    b"        //@ interior_pointer_limits::<T>(v_base, 4, 1);\n"
)
BORROW_PREFIX_SPLIT_LEMMA = b"""/*@
lem split_four_owned_cells<T>(base: *T, t: thread_id_t)
    req base[..4] |-> ?xs &*& foreach(xs, own::<T>(t));
    ens *base |-> ?first &*& <T>.own(t, first) &*&
        *(base + 1) |-> ?second &*& <T>.own(t, second) &*&
        *(base + 2) |-> ?third &*& <T>.own(t, third) &*&
        *(base + 3) |-> ?fourth &*& <T>.own(t, fourth) &*&
        xs == cons(first, cons(second, cons(third, cons(fourth, nil))));
{
    open array(base, 4, xs);
    assert xs == cons(?first0, ?rest0);
    open foreach(xs, own::<T>(t));
    open own::<T>(t)(first0);
    open array(base + 1, 3, rest0);
    assert rest0 == cons(?second0, ?tail0);
    open foreach(rest0, own::<T>(t));
    open own::<T>(t)(second0);
    open array(base + 2, 2, tail0);
    assert tail0 == cons(?third0, ?rest1);
    open foreach(tail0, own::<T>(t));
    open own::<T>(t)(third0);
    open array(base + 3, 1, rest1);
    assert rest1 == cons(?fourth0, ?empty0);
    open foreach(rest1, own::<T>(t));
    open own::<T>(t)(fourth0);
    open array(base + 4, 0, empty0);
    open foreach(empty0, own::<T>(t));
}
@*/
"""
BORROW_PREFIX_FIRST_CALL = b"""        //@ interior_pointer_limits::<T>(v_base, 4, 1);
        //@ split_four_owned_cells::<T>(v_base, t);
        //@ close_full_borrow_content::<T>(t, v_base + 1);
        //@ close_full_borrow_content::<T>(t, v_base);
        //@ borrow(cmp_k, <T>.full_borrow_content(t, v_base + 1));
        //@ borrow(cmp_k, <T>.full_borrow_content(t, v_base));
        //@ share_full_borrow::<T>(cmp_k, t, v_base + 1);
        //@ share_full_borrow::<T>(cmp_k, t, v_base);
        //@ let left_ref = precreate_ref(v_base + 1);
        //@ let right_ref = precreate_ref(v_base);
        //@ init_ref_share::<T>(cmp_k, t, left_ref);
        //@ init_ref_share::<T>(cmp_k, t, right_ref);
        //@ close_ref_own::<'cmp, T>(left_ref);
        //@ close_ref_own::<'cmp, T>(right_ref);
        //@ close <(&'cmp T, &'cmp T)>.own(t, std_tuple_2_::<&'cmp T, &'cmp T> { 0: left_ref, 1: right_ref });
        //@ open_frac_borrow(cmp_k, ref_initialized_(left_ref), 1/4);
        //@ open [?left_fraction]ref_initialized_::<T>(left_ref)();
        //@ open_frac_borrow(cmp_k, ref_initialized_(right_ref), 1/4);
        //@ open [?right_fraction]ref_initialized_::<T>(right_ref)();
        let c1 = is_less/*@::<F, (&'cmp T, &'cmp T), 'cmp>@*/(&*v_base.add(1), &*v_base);"""
BORROW_PREFIX_UNSAFE_ANCHOR = b"    unsafe {\n"
BORROW_PREFIX_LIFETIME_SCOPE = (
    b"    //@ let cmp_k = begin_lifetime();\n"
    b"    unsafe {\n"
    b"/*@ let_lft 'cmp = cmp_k; @*/\n"
)
MEMORY_PRE_CONTRACT = b"""/*@
req thread_token(?t) &*& t == currentThread &*&
    type_interp::<T>() &*& type_interp::<F>() &*&
    0 < std::mem::size_of::<T>() &*&
    v_base[..4] |-> ?source_before &*&
    foreach(source_before, own::<T>(t)) &*&
    array_::<T>(dst, 4, ?destination_before) &*&
    *is_less |-> ?less_before &*& <F>.own(t, less_before);
@*/
/*@
ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    v_base[..4] |-> ?source_after &*&
    foreach(source_after, own::<T>(t)) &*&
    array_::<T>(dst, 4, ?destination_after) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
/*@
on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&
    v_base[..4] |-> ?source_after &*&
    foreach(source_after, own::<T>(t)) &*&
    array_::<T>(dst, 4, ?destination_after) &*&
    *is_less |-> ?less_after &*& <F>.own(t, less_after);
@*/
"""
MEMORY_PRE_INTENDED_NORMAL_POST = (
    "thread_token(t), type_interp<T/F>, current initialized v_base[..4] with "
    "foreach(current_values, own<T>), initialized dst[..4], and current F.own; "
    "destination values carry no second T.own sequence."
)
MEMORY_PRE_INTENDED_UNWIND_POST = (
    "thread_token(t), type_interp<T/F>, current initialized v_base[..4] with "
    "foreach(current_values, own<T>), unchanged optional dst[..4] storage "
    "(all five callbacks precede the first write), and current F.own."
)
MEMORY_PRE_PARTIAL_NORMAL_POST = (
    "active diagnostic ens: current source values and exactly one own<T> per "
    "source element, current optional dst[..4] storage, and current F.own; "
    "does not claim dst is initialized after normal return."
)
MEMORY_PRE_PARTIAL_UNWIND_POST = (
    "active diagnostic on_unwind_ens: current source values and exactly one "
    "own<T> per source element, current optional dst[..4] storage, and current "
    "F.own; does not establish full panic-path restoration."
)


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strip_ghost(source: bytes) -> bytes:
    source = GHOST_BLOCK.sub(b"", source)
    return GHOST_LINE.sub(b"", source)


def extract_target(source: bytes) -> tuple[bytes, int]:
    require(source.count(FUNCTION_HEADER) == 1,
            "actual sort4_stable signature is absent or ambiguous")
    start = source.index(FUNCTION_HEADER)
    open_brace = start + len(FUNCTION_HEADER)
    require(source[open_brace:open_brace + 1] == b"{",
            "signature no longer ends at the actual function body")
    tail = source.find(NEXT_SOURCE_ANCHOR, open_brace)
    require(tail > open_brace and source[tail - 1:tail] == b"}",
            "function closing brace or next source anchor changed")
    target = source[start:tail]
    for fragment, expected in SOURCE_CALL_COUNTS.items():
        require(target.count(fragment) == expected,
                f"actual source call inventory changed: {fragment.decode()}")
    require(target.count(b"ptr::copy_nonoverlapping(") == 4,
            "actual four-copy tail is missing or ambiguous")
    require(target.index(b"let c1 = is_less(") <
            target.index(b"ptr::copy_nonoverlapping(min, dst, 1);"),
            "comparisons must remain before the first destination write")
    require(target.rfind(b"let c5 = is_less(") <
            target.index(b"ptr::copy_nonoverlapping(min, dst, 1);"),
            "last comparison must remain before the first destination write")
    return target, start


def source_certificate(repo: Path, source: bytes | None = None) -> tuple[bytes, dict]:
    path = repo / SOURCE_REL
    actual = path.read_bytes() if source is None else source
    actual_sha = digest(actual)
    require(actual_sha == SOURCE_SHA256,
            f"SmallSort source hash mismatch: {actual_sha}")
    blob = subprocess.run(["git", "-C", str(repo), "hash-object", str(path)],
                          check=True, capture_output=True, text=True).stdout.strip()
    require(blob == SOURCE_BLOB, f"SmallSort source Git blob mismatch: {blob}")
    target, start = extract_target(actual)
    return target, {
        "source_path": str(SOURCE_REL),
        "source_sha256": SOURCE_SHA256,
        "source_git_blob": SOURCE_BLOB,
        "target_byte_start": start,
        "target_source_sha256": digest(target),
        "target_signature": FUNCTION_HEADER.decode() + "{",
        "target_runtime_source_exact": True,
        "generic_domain": "all sized T; F: FnMut(&T, &T) -> bool",
        "source_call_counts": {
            "FnMut_callback_expression": SOURCE_CALL_COUNTS[b"is_less("],
            "select_unpredictable": SOURCE_CALL_COUNTS[b"hint::select_unpredictable("],
            "copy_nonoverlapping": SOURCE_CALL_COUNTS[b"ptr::copy_nonoverlapping("],
        },
        "all_five_comparisons_precede_first_write": True,
    }


def source_certificate_control(repo: Path, source: bytes,
                               source_record: dict) -> dict:
    old = b"let c1 = is_less(&*v_base.add(1), &*v_base);"
    altered = b"let c1 = false;"
    require(source.count(old) == 1,
            "cannot construct the one-token source-alter control")
    changed = source.replace(old, altered, 1)
    rejected = False
    try:
        source_certificate(repo, changed)
    except ValueError as exc:
        rejected = "SmallSort source hash mismatch" in str(exc)
    require(rejected, "source certificate accepted an altered comparator operation")
    return {
        "classification": "EXPECTED_SOURCE_CERTIFICATE_REJECTION",
        "alteration": "replace the first actual comparator call with `false`",
        "original_source_sha256": source_record["source_sha256"],
        "altered_source_sha256": digest(changed),
        "rejected_at": "pinned source SHA before extraction or MIR",
    }


def write_fixture(repo: Path, out: Path, memory_pre: bool = False,
                  borrow_prefix: bool = False) -> dict:
    require(not (memory_pre and borrow_prefix),
            "memory-pre and borrow-prefix modes are mutually exclusive")
    source = (repo / SOURCE_REL).read_bytes()
    target, source_record = source_certificate(repo, source)
    negative = source_certificate_control(repo, source, source_record)
    open_brace = target.index(b"{")
    if memory_pre or borrow_prefix:
        anchor = b"        let c1 = is_less(&*v_base.add(1), &*v_base);"
        require(target.count(anchor) == 1,
                "first actual pointer-add anchor is absent or ambiguous")
        verified_target = target.replace(anchor,
            BORROW_PREFIX_FIRST_CALL if borrow_prefix else
            MEMORY_PRE_BOUND_CALL + anchor, 1)
        if borrow_prefix:
            require(verified_target.count(BORROW_PREFIX_UNSAFE_ANCHOR) == 1,
                    "actual sort4 unsafe block for lifetime scope is ambiguous")
            verified_target = verified_target.replace(
                BORROW_PREFIX_UNSAFE_ANCHOR,
                BORROW_PREFIX_LIFETIME_SCOPE, 1)
        contract = MEMORY_PRE_CONTRACT
        lemma = (MEMORY_PRE_INTERIOR_LEMMA + BORROW_PREFIX_SPLIT_LEMMA
                 if borrow_prefix else MEMORY_PRE_INTERIOR_LEMMA)
    else:
        verified_target = target
        contract = CAPTURE_CONTRACT
        lemma = b""
    verified = (PREFIX + lemma + verified_target[:open_brace] + contract +
                verified_target[open_brace:])
    original = strip_ghost(verified)
    require(original == PREFIX + target,
            "ghost stripping did not recover exact source signature and body")
    require(original.count(target) == strip_ghost(verified).count(target) == 1,
            "target source function is duplicated or changed")
    require(not out.exists(), f"refusing to overwrite fixture directory: {out}")
    (out / "original").mkdir(parents=True)
    (out / "verified").mkdir()
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)
    record = {
        "classification": ("BORROW_PREFIX_DIAGNOSTIC_NOT_A_SORT4_PROOF"
                            if borrow_prefix else
                            "MEMORY_PRE_DIAGNOSTIC_NOT_A_SORT4_PROOF"
                            if memory_pre else "CAPTURE_ONLY_NOT_A_SORT4_PROOF"),
        "fixture_mode": ("borrow_prefix" if borrow_prefix else
                         "memory_pre" if memory_pre else "capture_only"),
        "source_certificate": source_record,
        "source_alter_control": negative,
        "capture_contract": (
            "positive-size T; four initialized source elements with one own<T> "
            "each; four optional destination cells; current F own; exact actual "
            "source+owners/current F/dst memory post"
            if memory_pre or borrow_prefix else
            "thread/type resources and current comparator resource only; no element or pointer permissions"),
        "memory_pre_bound_lemma": (
            "checked historical interior_pointer_limits<T>(v_base, 4, 1), "
            "inserted immediately before the unchanged first v_base.add(1)"
            if memory_pre or borrow_prefix else None),
        "borrow_prefix_protocol": (
            "checked split_four_owned_cells<T> opens existing array/foreach "
            "into four separate initialized cells and exactly four owners; "
            "fresh cmp lifetime/full borrows for actual v_base+1 and v_base; "
            "stock share/precreate/init_ref_share/close_ref_own and tuple Args.own; "
            "direct-unwind recovery is not installed in this diagnostic"
            if borrow_prefix else None),
        "full_generic_domain": "all sized T, including ZST, with F: FnMut(&T, &T) -> bool",
        "memory_pre_domain_restriction": (
            "0 < size_of::<T>(); ZST excluded from this diagnostic; no Copy, "
            "Freeze, or comparator-purity premise"
            if memory_pre or borrow_prefix else None),
        "intended_full_normal_post": (
            MEMORY_PRE_INTENDED_NORMAL_POST if memory_pre or borrow_prefix else None),
        "intended_full_unwind_post": (
            MEMORY_PRE_INTENDED_UNWIND_POST if memory_pre or borrow_prefix else None),
        "active_partial_normal_diagnostic_post": (
            MEMORY_PRE_PARTIAL_NORMAL_POST if memory_pre or borrow_prefix else None),
        "active_partial_unwind_diagnostic_post": (
            MEMORY_PRE_PARTIAL_UNWIND_POST if memory_pre or borrow_prefix else None),
        "partial_first_callback_resource_debt": (
            "Not added: no ref/precreate/borrow resource is manufactured by this "
            "memory-pre fixture. If the actual first reference needs a checked "
            "borrow protocol, preserve its concrete borrow_end/ref_initialized "
            "debt in a separately reviewed continuation; do not hide it in this post."
            if memory_pre else
            "The prefix adds real borrow debt for two cells. No direct-unwind "
            "recovery hook is included, so this is not a full-target proof."
            if borrow_prefix else None),
        "full_generic_safety_contract": "NOT_PROVED",
        "normal_target_posts": (
            "active diagnostic partial memory post; no dst initialization guarantee"
            if memory_pre or borrow_prefix else
            "capture-only token/type resources and current comparator resource"),
        "unwind_target_posts": (
            "full current-source/current-owner, optional dst and F/thread/type "
            "target is active but expected to fail at direct-unwind debt"
            if borrow_prefix else
            "active diagnostic partial memory post; no full unwind restoration claim"
            if memory_pre else
            "capture-only token/type resources and current comparator resource"),
        "normal_source_sha256": digest(original),
        "verified_source_sha256": digest(verified),
        "ghost_strip_identity": strip_ghost(verified) == original,
        "runtime_body_and_signature_unchanged": True,
        "sorting_property_claimed": False,
        "actual_sort4_proved": False,
    }
    require(record["ghost_strip_identity"], "fixture source pair differs after ghost stripping")
    (out / "fixture.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def balanced_record(decoded: str, opening: int) -> str:
    require(decoded[opening] == "(", "MIR function record opening missing")
    depth = 0
    in_string = False
    escaped = False
    for at in range(opening, len(decoded)):
        ch = decoded[at]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return decoded[opening:at + 1]
    raise ValueError("MIR function record is unterminated")


def complete_function_record(decoded: str, basename: str) -> tuple[str, str]:
    matches = [match for match in FUNCTION_DEF.finditer(decoded)
               if match.group(1) == basename or
               match.group(1).endswith("::" + basename)]
    require(len(matches) == 1,
            f"MIR target function is absent or ambiguous: {basename}")
    match = matches[0]
    lead = decoded.rfind("    ( defKind =", 0, match.start())
    require(lead >= 0, "MIR function record start is missing")
    opening = decoded.index("(", lead)
    record = balanced_record(decoded, opening)
    require(match.group(0) in record and "basicBlocks = [" in record and
            "localDecls = [" in record and "inputs = [" in record,
            "target MIR record is not the complete typed function graph")
    return match.group(1), record


def graph_inventory(decoded_path: Path, out: Path, mode: str) -> dict:
    decoded = decoded_path.read_text(errors="strict")
    defpath, record = complete_function_record(decoded, "sort4_stable")
    fnmut_calls = FNMUT_CALL_NAME.findall(record)
    fnmut_calls = [name for name in fnmut_calls if FNMUT_TARGET in name]
    require(len(fnmut_calls) == SOURCE_CALL_COUNTS[b"is_less("],
            f"MIR callback call count differs from exact source: {len(fnmut_calls)}")
    block_at = record.index("basicBlocks = [")
    locals_at = record.index("localDecls = [")
    require(locals_at < block_at, "pinned MIR local/block field order changed")
    block_section = record[block_at:]
    block_ids = re.findall(r"\( id = \(index = (\d+)\)", block_section)
    require(bool(block_ids), "complete target record has no decodable basic blocks")
    unwind_lines = [line.strip() for line in record.splitlines()
                    if "unwindAction =" in line]
    require(len(unwind_lines) >= len(fnmut_calls),
            "MIR omitted one or more comparator call unwind actions")
    cleanup_lines = [line.strip() for line in record.splitlines()
                     if "isCleanup = true" in line]
    targets = FNMUT_CALL_NAME.findall(record)
    path = out / f"{mode}-sort4-full-mir.txt"
    path.write_text(record)
    inventory = {
        "classification": "UNREVIEWED_COMPLETE_GRAPH_CAPTURE",
        "mode": mode,
        "def_path": defpath,
        "decoded_mir_sha256": digest(decoded.encode()),
        "full_function_record_path": path.name,
        "full_function_record_sha256": digest(record.encode()),
        "full_function_record_bytes": len(record.encode()),
        "complete_record_fields_present": ["inputs", "localDecls", "basicBlocks"],
        "basic_block_indices": block_ids,
        "basic_block_count": len(block_ids),
        "local_declaration_count": len(re.findall(r"id = \(name = \"", record[locals_at:block_at])),
        "source_comparator_calls": SOURCE_CALL_COUNTS[b"is_less("],
        "mir_fnmut_call_targets": fnmut_calls,
        "mir_call_target_names": targets,
        "unwind_action_lines": unwind_lines,
        "unwind_action_count": len(unwind_lines),
        "cleanup_block_marker_lines": cleanup_lines,
        "cleanup_block_count": len(cleanup_lines),
        "cleanup_inventory_reviewed": False,
    }
    (out / f"{mode}-graph-inventory.json").write_text(
        json.dumps(inventory, indent=2, sort_keys=True) + "\n")
    return inventory


def run_stage(name: str, argv: list[str], root: Path, env: dict[str, str],
              fixture_hashes: dict[str, str], deadline: int,
              cap: int, stdin_name: str | None = None,
              stdout_name: str | None = None) -> dict:
    paths = {rel: root / rel for rel in fixture_hashes}
    before = {rel: digest(path.read_bytes()) for rel, path in paths.items()}
    require(before == fixture_hashes, f"fixture source changed before {name}")
    seconds = min(cap, deadline - int(time.time()) - 10)
    if seconds <= 0:
        return {"exit": None, "skipped": "deadline/artifact reserve"}
    stdout_path = root / (stdout_name or f"{name}.log")
    stderr_path = root / f"{name}-stderr.log" if stdout_name else stdout_path
    with stdout_path.open("wb") as stdout:
        stderr = stderr_path.open("wb") if stderr_path != stdout_path else subprocess.STDOUT
        try:
            stdin = (root / stdin_name).open("rb") if stdin_name else open(os.devnull, "rb")
            try:
                result = subprocess.run(
                    ["/usr/bin/time", "-v", "-o", str(root / f"{name}-resources.txt"),
                     "timeout", "--signal=TERM", "--kill-after=10s",
                     f"{seconds}s", *argv],
                    cwd=root, env=env, stdin=stdin, stdout=stdout,
                    stderr=stderr, check=False).returncode
            finally:
                stdin.close()
        finally:
            if stderr_path != stdout_path:
                stderr.close()
    after = {rel: digest(path.read_bytes()) for rel, path in paths.items()}
    record = {
        "argv": argv, "exit": result, "timeout_seconds": seconds,
        "fixture_before": before, "fixture_after": after,
        "fixture_integrity": before == after == fixture_hashes,
        "stdout": stdout_path.name, "stderr": stderr_path.name,
    }
    (root / f"{name}-stage.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record


def execute(args: argparse.Namespace) -> dict:
    require(os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux",
            "sort4 capture is restricted to GitHub-hosted Linux")
    args.repo_root = args.repo_root.resolve()
    args.tool_home = args.tool_home.resolve()
    args.schema = args.schema.resolve()
    args.evidence = args.evidence.resolve()
    require(args.schema.is_file() and args.tool_home.is_dir(),
            "pinned hosted tool inputs are missing")
    args.evidence.mkdir(parents=True, exist_ok=False)
    fixture_dir = args.evidence / "fixture"
    fixture = write_fixture(args.repo_root, fixture_dir, args.memory_pre,
                            args.borrow_prefix)
    hashes = {"original/lib.rs": fixture["normal_source_sha256"],
              "verified/lib.rs": fixture["verified_source_sha256"]}
    env = os.environ.copy()
    env["PATH"] = str(args.tool_home / "bin") + os.pathsep + env.get("PATH", "")
    tool_names = ("verifast", "vf-rust-mir-exporter", "refinement-checker")
    tool_hashes = {name: digest((args.tool_home / "bin" / name).read_bytes())
                   for name in tool_names}
    source_hash_before = fixture["source_certificate"]["source_sha256"]
    compiler = subprocess.run(["rustc", "--version", "--verbose"],
                              check=True, capture_output=True, text=True).stdout
    profile = {
        "proof_sha": subprocess.run(
            ["git", "-C", str(args.repo_root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip(),
        "source_sha256": fixture["source_certificate"]["source_sha256"],
        "tool_hashes": tool_hashes,
        "schema_sha256": digest(args.schema.read_bytes()),
        "compiler_version_verbose": compiler,
        "capture_only": not args.memory_pre and not args.borrow_prefix,
        "memory_pre_diagnostic": args.memory_pre,
        "borrow_prefix_diagnostic": args.borrow_prefix,
        "fixture_mode": fixture["fixture_mode"],
        "actual_sort4_proved": False,
    }
    (args.evidence / "hosted-profile.json").write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n")

    exporter = str(args.tool_home / "bin/vf-rust-mir-exporter")
    verifier = str(args.tool_home / "bin/verifast")
    stages: dict[str, dict] = {}

    def run(name: str, argv: list[str], cap: int,
            stdin: str | None = None, stdout: str | None = None) -> dict:
        return run_stage(name, argv, fixture_dir, env, hashes,
                         args.deadline_epoch, cap, stdin, stdout)

    stages["normal-export"] = run(
        "normal-export", [exporter, "verified/lib.rs",
                          f"--sysroot={args.compiler_sysroot}", "--edition", "2021"],
        100, stdout="normal-mir.bin")
    if stages["normal-export"].get("exit") == 0:
        stages["normal-decode"] = run(
            "normal-decode", ["capnp", "decode", str(args.schema), "VfMir"],
            60, "normal-mir.bin", "normal-mir.txt")
    else:
        stages["normal-decode"] = {"exit": None, "skipped": "normal export failed"}
    stages["readonly-export"] = run(
        "readonly-export", [exporter, "verified/lib.rs",
                            f"--sysroot={args.compiler_sysroot}", "--edition", "2021",
                            "--vf-rust-mir-exporter:preprocess-readonly"],
        100, stdout="readonly-mir.bin")
    if stages["readonly-export"].get("exit") == 0:
        stages["readonly-decode"] = run(
            "readonly-decode", ["capnp", "decode", str(args.schema), "VfMir"],
            60, "readonly-mir.bin", "readonly-mir.txt")
    else:
        stages["readonly-decode"] = {"exit": None, "skipped": "readonly export failed"}

    normal_graph = None
    readonly_graph = None
    if stages["normal-decode"].get("exit") == 0:
        normal_graph = graph_inventory(fixture_dir / "normal-mir.txt",
                                       args.evidence, "normal")
    if stages["readonly-decode"].get("exit") == 0:
        readonly_graph = graph_inventory(fixture_dir / "readonly-mir.txt",
                                         args.evidence, "readonly")

    stages["full-verification"] = run(
        "full-verification", [verifier, "-rustc_args", "--edition 2021",
                              "-verbose", "1", "verified/lib.rs"], 240)
    stages["refinement"] = run(
        "refinement", [str(args.tool_home / "bin/refinement-checker"),
                       "--rustc-args", "--edition 2021",
                       "original/lib.rs", "verified/lib.rs"], 120)
    full_log = (fixture_dir / "full-verification.log").read_text(errors="replace")
    headers = re.findall(
        r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): Verifying function 'sort4_stable'",
        full_log)
    errors = [line for line in full_log.splitlines() if ": error:" in line]
    support_keys = ("normal-export", "normal-decode", "readonly-export",
                    "readonly-decode", "refinement")
    support_ok = all(stages.get(key, {}).get("exit") == 0 for key in support_keys)
    source_after = (args.repo_root / SOURCE_REL).read_bytes()
    source_repository_integrity = digest(source_after) == source_hash_before
    fixture_integrity = all(row.get("fixture_integrity") is True
                            for row in stages.values()
                            if "fixture_integrity" in row)
    tool_hashes_after = {
        name: digest((args.tool_home / "bin" / name).read_bytes())
        for name in tool_names
    }
    tool_integrity = tool_hashes_after == tool_hashes
    source_integrity = fixture_integrity and source_repository_integrity
    graph_complete = normal_graph is not None and readonly_graph is not None
    result = {
        "classification": fixture["classification"],
        "accepted_component": False,
        "actual_sort4_proved": False,
        "full_generic_safety_contract_proved": False,
        "support_export_decode_refinement_all_zero": support_ok,
        "full_graphs_captured": graph_complete,
        "normal_graph": normal_graph,
        "readonly_graph": readonly_graph,
        "source_integrity": source_integrity,
        "fixture_integrity": fixture_integrity,
        "repository_source_integrity": source_repository_integrity,
        "tool_integrity": tool_integrity,
        "tool_hashes_before": tool_hashes,
        "tool_hashes_after": tool_hashes_after,
        "target_verifier_header_count": len(headers),
        "target_verifier_headers": headers,
        "full_verification_exit": stages["full-verification"].get("exit"),
        "first_verifier_error": errors[0] if errors else None,
        "all_verifier_errors": errors,
        "source_alter_control": fixture["source_alter_control"],
        "fixture": fixture,
        "stages": stages,
    }
    (args.evidence / "outcome.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification": result["classification"],
                      "first_verifier_error": result["first_verifier_error"],
                      "stages": {key: row.get("exit") for key, row in stages.items()},
                      "full_graphs_captured": graph_complete}, sort_keys=True),
          flush=True)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    parser.add_argument(
        "--memory-pre", action="store_true",
        help=("opt into a separate positive-size memory-pre diagnostic with "
              "initialized source array, optional destination storage, and "
              "the checked first-pointer-add bounds lemma"))
    parser.add_argument(
        "--borrow-prefix", action="store_true",
        help=("opt into the first actual comparator borrow/share/precreate "
              "diagnostic; direct-unwind recovery is not installed"))
    args = parser.parse_args()
    args.compiler_sysroot = str(Path(args.compiler_sysroot).resolve())
    execute(args)


if __name__ == "__main__":
    main()
