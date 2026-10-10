#!/usr/bin/env python3
"""Build cloud-only, source-linked first-sort4 caller-entry diagnostics."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

SOURCE_REL = Path("library/core/src/slice/sort/shared/smallsort.rs")
SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
MARKER_REL = Path("library/core/src/marker.rs")
SHARED_REL = Path("library/core/src/slice/sort/shared/mod.rs")
CAPTURE_REL = Path("research/challenge-8/overnight-sort4/capture.py")
HERE = Path(__file__).resolve().parent
CASES = ("prefix-native", "source-frame-positive", "bridge-positive", "range-negative",
         "duplicate-negative", "native-scratch-frame", "source-post-negative",
         "source-typed-frame-positive", "source-typed-missing-T-negative",
         "source-typed-missing-F-negative")
FUNCTION_NAME = b"fn small_sort_general_with_scratch<T: FreezeMarker, F: FnMut(&T, &T) -> bool>("
SCRATCH_LINE = b"        let scratch_base = scratch.as_mut_ptr() as *mut T;"
SORT8_CONDITION = b"if const { size_of::<T>() <= 16 } && len >= 16 {"
SORT4_CONDITION = b"} else if len >= 8 {"
ELSE_CONDITION = b"} else {"
TRAIT_START = (b"/// SAFETY: this is safety relevant, how does this interact with the soundness holes in\n"
               b"/// specialization?\n")
TRAIT_END = b"impl<T: Freeze> FreezeMarker for T {}"
FEATURES = (b"#![feature(freeze, rustc_attrs, core_intrinsics)]\n"
            b"#![allow(internal_features)]\n\n"
            b"use std::{intrinsics, mem::{MaybeUninit, size_of}};\n"
            b"use std::marker::Freeze;\n\n")


def _need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _brace_end(data: bytes, opening: int) -> int:
    """Return matching Rust brace, ignoring strings and nested comments."""
    _need(data[opening:opening + 1] == b"{", "expected opening brace")
    depth = 0
    i = opening
    state = "code"
    block_depth = 0
    while i < len(data):
        pair = data[i:i + 2]
        ch = data[i:i + 1]
        if state == "line":
            if ch in (b"\n", b"\r"):
                state = "code"
        elif state == "block":
            if pair == b"/*":
                block_depth += 1
                i += 1
            elif pair == b"*/":
                block_depth -= 1
                i += 1
                if block_depth == 0:
                    state = "code"
        elif state == "string":
            if ch == b"\\":
                i += 1
            elif ch == b'"':
                state = "code"
        elif state == "char":
            if ch == b"\\":
                i += 1
            elif ch == b"'":
                state = "code"
        elif pair == b"//":
            state = "line"
            i += 1
        elif pair == b"/*":
            state = "block"
            block_depth = 1
            i += 1
        elif ch == b'"':
            state = "string"
        elif ch == b"'" and i + 2 < len(data) and data[i + 2:i + 3] == b"'":
            state = "char"
        elif ch == b"{":
            depth += 1
        elif ch == b"}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unclosed Rust function body")


def _extract_function(source: bytes) -> tuple[bytes, int, int]:
    _need(source.count(FUNCTION_NAME) == 1, "caller function header absent or ambiguous")
    start = source.index(FUNCTION_NAME)
    opening = source.index(b"{", start + len(FUNCTION_NAME))
    end = _brace_end(source, opening)
    function = source[start:end]
    _need(function.count(b"sort4_stable(") == 2,
          "actual caller must contain the two original sort4 calls")
    _need(function.count(SORT8_CONDITION) == 1 and function.count(SORT4_CONDITION) == 1,
          "original branch conditions are absent or ambiguous")
    _need(function.index(b"sort4_stable(v_base, scratch_base, is_less);") <
          function.index(b"sort4_stable(v_base.add(len_div_2), scratch_base.add(len_div_2), is_less);") ,
          "first sort4 source call changed")
    return function, start, end


def _extract_shared_trait(shared: bytes) -> tuple[bytes, int]:
    _need(shared.count(TRAIT_START) == 1, "FreezeMarker source anchor absent or ambiguous")
    start = shared.index(TRAIT_START)
    end = shared.index(TRAIT_END, start) + len(TRAIT_END)
    return shared[start:end] + b"\n", start


def _extract_freeze_definition(marker: bytes) -> tuple[bytes, int]:
    anchor = (b"#[lang = \"freeze\"]\n#[unstable(feature = \"freeze\", issue = \"121675\")]\n"
              b"pub unsafe auto trait Freeze {}")
    _need(marker.count(anchor) == 1, "core Freeze definition anchor changed")
    start = marker.index(anchor)
    return anchor, start


def _memory_pre_contract(capture: bytes) -> bytes:
    tree = ast.parse(capture.decode("utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "MEMORY_PRE_CONTRACT"
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            _need(isinstance(value, bytes), "capture memory-pre contract is not bytes")
            return value
    raise ValueError("MEMORY_PRE_CONTRACT missing from capture.py")


def _case_source(name: str) -> bytes:
    if name.startswith("source-typed-"):
        path = HERE / (name + ".gh")
        _need(path.is_file(), f"typed source case is missing: {name}")
        body = path.read_bytes()
        _need(body.startswith(b"/*@\n") and body.rstrip().endswith(b"@*/"),
              f"typed source case must be one ghost block: {name}")
        return body[len(b"/*@\n"):].rstrip()[:-len(b"@*/")].strip(b"\r\n")
    cases = (HERE / "bridge-cases.rs").read_bytes()
    marker = b"// CASE " + name.encode() + b"\n"
    _need(cases.count(marker) == 1, f"case block missing or ambiguous: {name}")
    start = cases.index(marker) + len(marker)
    end = cases.find(b"// END CASE\n", start)
    _need(end >= 0, f"case block unterminated: {name}")
    body = cases[start:end]
    body = re.sub(rb"(?m)^//(?!@)[^\r\n]*(?:\r?\n|$)", b"", body)
    body = re.sub(rb"/\*@(.*?)@\*/", lambda m: m.group(1), body, flags=re.S)
    body = re.sub(rb"(?m)^[ \t]*return;[ \t]*(?:\r?\n|$)", b"", body)
    return body.strip(b"\r\n")


def _ghost_strip(source: bytes) -> bytes:
    source = re.sub(rb"/\*@.*?@\*/(?:\r?\n)?", b"", source, flags=re.S)
    return re.sub(rb"(?m)^[ \t]*//@[^\r\n]*(?:\r?\n|$)", b"", source)


def _lemma(memory_pre: bytes) -> bytes:
    match = re.search(rb"/\*@\s*req\s+(.*?)\s*;\s*@\*/", memory_pre, re.S)
    _need(match is not None, "cannot read exact c1 precondition from capture.py")
    req = match.group(1).strip()
    ens = req.replace(b"?", b"")
    return (b"/*@\nlem c1_entry_identity<T, F>(v_base: *T, dst: *T, is_less: *F)\n"
            b"    req " + req + b";\n    ens " + ens + b";\n{}\n@*/\n")


def _source_identity_lemma() -> bytes:
    return (
        b"/*@\n"
        b"lem c1_source_identity<T, F>(v_base: *T, is_less: *F, t: thread_id_t, "
        b"source4: list<T>, less: F)\n"
        b"    req thread_token(t) &*& t == currentThread &*& "
        b"v_base[..4] |-> source4 &*& foreach(source4, own::<T>(t)) &*& "
        b"*is_less |-> less &*& <F>.own(t, less);\n"
        b"    ens thread_token(t) &*& t == currentThread &*& "
        b"v_base[..4] |-> source4 &*& foreach(source4, own::<T>(t)) &*& "
        b"*is_less |-> less &*& <F>.own(t, less);\n"
        b"{}\n"
        b"@*/\n"
    )


def _source_typed_identity_lemma() -> bytes:
    resources = (b"type_interp::<T>() &*& type_interp::<F>() &*& "
                 b"thread_token(t) &*& t == currentThread &*& "
                 b"v_base[..4] |-> source4 &*& foreach(source4, own::<T>(t)) &*& "
                 b"*is_less |-> less &*& <F>.own(t, less)")
    return (b"/*@\nlem c1_source_typed_identity<T, F>(v_base: *T, is_less: *F, t: thread_id_t, "
            b"source4: list<T>, less: F)\n    req " + resources + b";\n    ens " + resources +
            b";\n{}\n@*/\n")


def _source_line_bytes(source: bytes, anchor: bytes) -> tuple[bytes, int]:
    _need(source.count(anchor) == 1, f"source operation absent or ambiguous: {anchor!r}")
    at = source.index(anchor)
    start = source.rfind(b"\n", 0, at) + 1
    end = source.find(b"\n", at)
    _need(end >= 0, f"source operation is not newline terminated: {anchor!r}")
    return source[start:end + 1], start


def _native_entry_function(caller: bytes) -> tuple[bytes, dict[str, tuple[int, bytes]]]:
    """Build a separate native entry lemma from exact read-only caller operations."""
    header_end = caller.find(b"{")
    _need(header_end >= 0, "caller function opening brace absent")
    header = caller[:header_end + 1]
    operations = (
        ("len", b"let len = v.len();"),
        ("v_base", b"let v_base = v.as_mut_ptr();"),
        ("len_div_2", b"let len_div_2 = len / 2;"),
        ("scratch_base", SCRATCH_LINE.strip()),
    )
    copied: dict[str, tuple[int, bytes]] = {}
    lines: list[bytes] = []
    for name, anchor in operations:
        line, offset = _source_line_bytes(caller, anchor)
        copied[name] = (offset, line)
        lines.append(line)
    offsets = [copied[name][0] for name, _ in operations]
    _need(offsets == sorted(offsets), "read-only source operations changed order")
    unsafe_line, unsafe_offset = _source_line_bytes(caller, b"unsafe {")
    _need(caller.rfind(b"    unsafe {", 0, copied["scratch_base"][0]) == unsafe_offset,
          "unsafe block anchor is not the source scratch block")
    body = (header + b"\n" + lines[0] + lines[1] + lines[2] + unsafe_line + lines[3] +
            b"        /*@ if (len >= 8) {\n")
    copied["unsafe"] = (unsafe_offset, unsafe_line)
    return body, copied


def _source_line(source: bytes, offset: int) -> int:
    return source.count(b"\n", 0, offset) + 1


def prepare(repo: Path, out: Path, case: str) -> dict:
    """Generate one cloud fixture. This function performs no compilation/proof."""
    _need(case in CASES, f"unknown case {case!r}; expected one of {CASES}")
    _need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          "GITHUB_ACTIONS" not in os.environ and
          (os.environ.get("LANE") == "o26-sort4-caller-entry" or
           (os.environ.get("LANE") == "o26-sort4-c1-current-recovery" and
            ((os.environ.get("SORT4_NATIVE_C4_PHASE") == "1" and
              os.environ.get("SORT4_NATIVE_C4_PHASE_ID") == "SORT4-NATIVE-C4-CLOUD-2026-10-10") or
             (os.environ.get("SORT4_NATIVE_OPAQUE_PHASE") == "1" and
              os.environ.get("SORT4_NATIVE_OPAQUE_PHASE_ID") == "SORT4-NATIVE-OPAQUE-CLOUD-2026-10-10")))),
          "caller-entry preparation is restricted to the designated cloud-build lane")
    repo = repo.resolve()
    out = out.resolve()
    workspace = Path("/workspace").resolve()
    _need(repo == workspace or workspace in repo.parents,
          "caller-entry repo must be under /workspace")
    _need(out == workspace or workspace in out.parents,
          "caller-entry output must be under /workspace")
    _need(not out.exists(), f"refusing to overwrite output directory: {out}")

    source = (repo / SOURCE_REL).read_bytes()
    source_hash = _sha(source)
    _need(source_hash == SOURCE_SHA256, f"SmallSort SHA-256 mismatch: {source_hash}")
    blob = subprocess.run(
        ["git", "-C", str(repo), "hash-object", str(repo / SOURCE_REL)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    _need(blob == SOURCE_BLOB, f"SmallSort Git blob mismatch: {blob}")
    caller, caller_start, caller_end = _extract_function(source)
    shared = (repo / SHARED_REL).read_bytes()
    marker = (repo / MARKER_REL).read_bytes()
    freeze_marker, freeze_marker_start = _extract_shared_trait(shared)
    freeze_def, freeze_def_start = _extract_freeze_definition(marker)
    memory_pre = _memory_pre_contract((repo / CAPTURE_REL).read_bytes())

    native_body, copied_ops = _native_entry_function(caller)
    case_body = _case_source(case)
    case_body = b"assert len >= 8; // FIRST_SORT4_CALLSITE_BOUNDARY\n" + case_body
    indented_case = b"            " + case_body.replace(b"\n", b"\n            ").rstrip()
    fragment = native_body + indented_case + b"\n        } @*/\n    }\n}"
    source_lemma = (_source_typed_identity_lemma()
                    if case.startswith("source-typed-") else
                    _source_identity_lemma()
                    if case in ("source-frame-positive", "source-post-negative") else b"")
    bridge_lemma = _lemma(memory_pre) if case == "bridge-positive" else b""
    common_preamble = FEATURES + freeze_marker + b"\n" + source_lemma + bridge_lemma
    verified = common_preamble + fragment
    original = FEATURES + freeze_marker + b"\n" + _ghost_strip(fragment)
    _need(_ghost_strip(verified) == original,
          "ghost-stripped verified fragment differs from constructed native entry function")
    _need(not any(token in verified for token in (b"assume", b"admit", b"unchecked")),
          "fixture contains a forbidden assumption/admission marker")
    _need(not any(token in fragment for token in (
        b"sort8_stable(", b"sort4_stable(", b"insert_tail(",
        b"ptr::copy_nonoverlapping(", b"scratch.len() <", b"if const {",
        b"size_of::<T>() <= 16")),
        "standalone entry lemma must not project actual caller control flow")

    out.mkdir(parents=True)
    (out / "original").mkdir()
    (out / "verified").mkdir()
    (out / "actual-caller.rs").write_bytes(caller + b"\n")
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)

    marker_line = b"assert len >= 8; // FIRST_SORT4_CALLSITE_BOUNDARY"
    line_targets = {}
    for label, needle in (
        ("first_sort4_callsite_boundary", marker_line),
        ("source_sort8_condition", marker_line),
        ("source_sort4_condition", marker_line),
        ("source_array", b"assert v_base[..len] |-> ?source_all;"),
        ("source_subset_four", b"assert v_base[..4] |-> ?first_four;"),
        ("source_identity_lemma", b"c1_source_identity::<T, F>"),
        ("source_typed_identity_lemma", b"c1_source_typed_identity::<T, F>"),
        ("produce_type_interp_T", b"produce_type_interp::<T>();"),
        ("produce_type_interp_F", b"produce_type_interp::<F>();"),
        ("leak_type_interp_T", b"leak type_interp::<T>();"),
        ("leak_type_interp_F", b"leak type_interp::<F>();"),
        ("positive_identity_lemma", b"c1_entry_identity::<T, F>"),
        ("positive_size_guard", b"if (0 < std::mem::size_of::<T>() && scratch_len >= 4)"),
        ("bridge_scratch_guard", b"scratch_len >= 4"),
        ("range_negative_split", b"array_split::<T>(v_base, 9);"),
        ("duplicate_negative_authority", b"v_base[..len] |-> ?xs"),
        ("native_scratch_array", b"assert mu_base[..scratch_len] |-> ?mu_all;"),
        ("source_post_negative", b"assert less_after != less_before;"),
    ):
        if needle in verified:
            at = verified.index(needle)
            line_targets[label] = verified[:at].count(b"\n") + 1
    if case.startswith("source-typed-"):
        typed_marker = {
            "source-typed-frame-positive": b"// SOURCE_TYPED_IDENTITY_CALL",
            "source-typed-missing-T-negative": b"// SOURCE_TYPED_IDENTITY_CALL",
            "source-typed-missing-F-negative": b"// SOURCE_TYPED_IDENTITY_CALL",
        }[case]
        _need(verified.count(typed_marker) == 1, "typed identity call marker absent or ambiguous")
        at = verified.index(typed_marker)
        line_targets["source_typed_identity_call"] = verified[:at].count(b"\n") + 1
    boundary_line = verified[:verified.index(marker_line)].count(b"\n") + 1
    artificial_compatibility_targets = (
        "inline_const_value_path_filter", "overflow_runtime_size_guard",
        "overflow_runtime_len_guard", "overflow_array_invariant",
        "overflow_large_type_mono", "overflow_small_type_bound",
        "scratch_success_path_filter", "original_scratch_len_plus_16_check",
        "source_sort8_condition", "source_sort4_condition",
    )
    for label in artificial_compatibility_targets:
        line_targets.setdefault(label, boundary_line)
    line_lists = {}
    for label, needle in (
        ("thread_token", b"assert thread_token(?t);"),
        ("current_thread", b"assert t == currentThread;"),
        ("source_array", b"assert v_base[..len] |-> ?source_all;"),
        ("source_owners", b"assert foreach(source_all, own::<T>(t));"),
        ("source_array_split", b"array_split::<T>(v_base, 4);"),
        ("source_owners_split", b"foreach_split(source_all, own::<T>(t), 4);"),
        ("source_identity_lemma", b"c1_source_identity::<T, F>"),
        ("source_typed_identity_lemma", b"c1_source_typed_identity::<T, F>"),
        ("native_scratch_array", b"assert mu_base[..scratch_len] |-> ?mu_all;"),
        ("native_scratch_owners", b"assert foreach(mu_all, own::<std::mem::MaybeUninit<T>>(t));"),
        ("positive_size_guard", b"if (0 < std::mem::size_of::<T>() && scratch_len >= 4)"),
        ("identity_lemma_call", b"c1_entry_identity::<T, F>"),
        ("range_negative", b"array_split::<T>(v_base, 9);"),
        ("duplicate_negative", b"assert v_base[..len] |-> ?xs"),
        ("source_post_negative", b"assert less_after != less_before;"),
    ):
        matches = list(re.finditer(re.escape(needle), verified))
        if matches:
            line_lists[label] = [verified[:match.start()].count(b"\n") + 1 for match in matches]

    operation_map = {
        name: {
            "source_byte_start": caller_start + offset,
            "caller_relative_byte_start": offset,
            "source_line": _source_line(caller, offset),
            "statement_sha256": _sha(line),
            "exact_statement_bytes": line.decode(),
            "verified_source_line": _source_line(verified, verified.find(line)),
            "lemma_byte_start": verified.find(line),
        }
        for name, (offset, line) in copied_ops.items()
    }
    record = {
        "classification": "SOURCE_LINKED_STANDALONE_NATIVE_ENTRY_RESOURCE_DIAGNOSTIC_NOT_CALLER_PROOF",
        "case": case,
        "cloud_only": True,
        "execution_provider": "cloud-build",
        "lane": "o26-sort4-caller-entry",
        "prepare_runs_no_compiler_or_verifier": True,
        "source_certificate": {
            "path": str(SOURCE_REL), "sha256": source_hash, "git_blob": blob,
            "full_original_caller_path": "actual-caller.rs",
            "full_original_caller_sha256": _sha(caller),
            "caller_byte_start": caller_start, "caller_byte_end_exclusive": caller_end,
            "caller_start_line": _source_line(source, caller_start),
            "caller_signature_sha256": _sha(caller[:caller.find(b"{")]),
            "caller_runtime_source_exact": True,
            "caller_signature_and_body_brace_balanced": True,
            "native_entry_signature_exact": True,
            "native_entry_is_separate_resource_lemma": True,
            "native_entry_signature": caller[:caller.find(b"{")].decode(),
        },
        "freeze_marker_certificate": {
            "shared_path": str(SHARED_REL), "shared_sha256": _sha(shared),
            "exact_trait_impl_sha256": _sha(freeze_marker.rstrip(b"\n")),
            "byte_start": freeze_marker_start, "core_marker_path": str(MARKER_REL),
            "core_marker_sha256": _sha(marker), "Freeze_definition_sha256": _sha(freeze_def),
            "Freeze_definition_byte_start": freeze_def_start, "FreezeMarker_source_exact": True,
        },
        "memory_pre_contract_sha256": _sha(memory_pre),
        "memory_pre_contract_source": str(CAPTURE_REL) + ":MEMORY_PRE_CONTRACT",
        "source_mapped_condition_bytes": {
            "operation_map": operation_map,
            "all_operations_are_read_only": True,
            "source_runtime_identity_claim": False,
            "caller_cfg_projection_claim": False,
            "ghost_boundary_marker": "FIRST_SORT4_CALLSITE_BOUNDARY",
            "ghost_boundary_is_artificial": True,
            "selected_applicability_basis": (
                "At the actual first sort4 call, len >= 8. Intervening length/pointer reads and "
                "guard checks do not mutate source/F/MU heap resources; no comparator or copy "
                "precedes the call. This separate lemma does not prove those guards or const-branch selection."
            ),
        },
        "native_entry_contract": {
            "signature_is_exact_actual_caller_signature": True,
            "full_native_precondition_from_generated_mutable_reference_contract": True,
            "automatic_native_normal_post_checked": True,
            "automatic_native_unwind_post_checked": True,
            "automatic_native_leak_check_required": True,
            "native_post_source": "stock generated contract for the exact signature; not hand-written or strengthened",
            "native_post_capture_status": "must be captured and hashed by the Cloud collector",
            "all_lengths_admitted": True,
            "all_scratch_lengths_admitted": True,
            "zst_admitted": True,
            "no_runtime_guard_or_caller_cfg_projection": True,
        },
        "type_interp_disposition": ({
            "source-frame-positive": "no type_interp assertion or production; no type_interp caller premise claimed",
            "bridge-positive": "stock produce_type_interp::<T/F>() in the real diagnostic function, followed by explicit stock leak type_interp::<T/F>(); trusted logical production, not native heap derivation",
            "other_cases": "no explicit type_interp production",
            case: ("stock produce_type_interp::<T/F>() in the real diagnostic function; both stock chunks are required/returned by the checked identity lemma and explicitly leaked after frame restoration"
                   if case == "source-typed-frame-positive" else
                   "stock peer chunk produced; this chunk's producer is omitted to target the checked identity lemma's matching type_interp precondition; first-error attribution awaits Cloud review"),
        } if case.startswith("source-typed-") else {
            "source-frame-positive": "no type_interp assertion or production; no type_interp caller premise claimed",
            "bridge-positive": "stock produce_type_interp::<T/F>() in the real diagnostic function, followed by explicit stock leak type_interp::<T/F>(); trusted logical production, not native heap derivation",
            "other_cases": "no explicit type_interp production",
        }),
        "bridge_diagnostic_subdomain": {
            "guard": "ghost condition size_of<T>() > 0 && scratch_len >= 4",
            "caller_scratch_success_implies_lower_bound_claim": False,
            "scope_note": "condition selects a diagnostic subdomain only; no caller CFG or arithmetic proof is included",
        } if case == "bridge-positive" else None,
        "fragment_boundary": "standalone same-signature native entry resource lemma; no actual caller CFG projection",
        "original_prefix_source_sha256": None,
        "original_prefix_reconstructed_by_removing_exact_insertions": False,
        "filtered_fragment_has_runtime_path_filter": False,
        "filtered_fragment_path": None,
        "diagnostic_prefix_insertions": [],
        "diagnostic_fragment_prefix_byte_identical_to_source": False,
        "ghost_strip_pair_scope": "standalone native entry resource diagnostic; actual full caller preserved separately",
        "branch_conditions_exact": False,
        "no_comparator_or_copy_before_first_sort4": True,
        "first_sort4_runtime_call_in_fragment": False,
        "sort8_or_later_call_summaries": False,
        "case_constraints": {
            "prefix-native": "native entry contract only; artificial len>=8 ghost boundary has no assertions",
            "source-frame-positive": "source4 owners/F/thread subset; explicit identity lemma; full source frame restored; no type_interp or destination resources",
            "bridge-positive": "diagnostic is ghost-guarded by size_of<T>() > 0 and scratch_len >= 4; stock type_interp production/leak is explicit; MU restoration remains unresolved",
            "range-negative": "under len==8, split at constant 9 gives bounded out-of-range authority control without len+1 overflow",
            "duplicate-negative": "duplicate whole-array authority assertion is the intended duplicate-authority control",
            "native-scratch-frame": "asserts native MaybeUninit array/owners and leaves them untouched",
            "source-post-negative": "after source4 identity lemma, false current-value post is the intended negative",
            "source-typed-frame-positive": "stock T/F type_interp production, checked source4/F/thread identity, complete native frame restoration and both stock logical chunk leaks; typed logical-subset diagnostic only",
            "source-typed-missing-T-negative": "omits only stock T type_interp producer; exact callee first-error classification awaits fresh Cloud evidence",
            "source-typed-missing-F-negative": "omits only stock F type_interp producer; exact callee first-error classification awaits fresh Cloud evidence",
        }[case],
        **({"typed_source_control": {
            "checked_identity_helper": "c1_source_typed_identity",
            "requires_and_returns": ["type_interp<T>", "type_interp<F>", "thread_token(currentThread)",
                                      "source4 owners", "F cell", "F.own"],
            "stock_producers_executed_by_real_native_function": {
                "T": "produce_type_interp::<T>()" if case != "source-typed-missing-T-negative" else None,
                "F": "produce_type_interp::<F>()" if case != "source-typed-missing-F-negative" else None,
            },
            "missing_producer_negative_credit": "INCONCLUSIVE_UNTIL_FRESH_EXACT_FIRST_ERROR_REVIEW",
            "type_chunks_claimed_from_native_heap": False,
            "actual_caller_or_sort4_applicability": False,
        }} if case.startswith("source-typed-") else {}),
        "targeted_ghost_statement_lines": line_targets,
        "targeted_ghost_statement_line_lists": line_lists,
        "targeted_ghost_statement_line_kinds": {
            "first_sort4_callsite_boundary": "artificial ghost boundary inside standalone resource lemma",
            **{label: "compatibility alias to artificial ghost boundary; not an actual source statement"
               for label in artificial_compatibility_targets},
        },
        "expected_negative_first_error": {
            "range-negative": {"marker": "RANGE_AUTHORITY_CONTROL", "obligation": "array_split at 9 with len==8"},
            "duplicate-negative": {"marker": "DUPLICATE_AUTHORITY_CONTROL", "obligation": "duplicate whole-array array authority"},
            "source-post-negative": {"marker": "SOURCE_CURRENT_VALUE_POST_CONTROL", "obligation": "false current-value post after identity lemma"},
        }.get(case),
        "generated": {
            "actual-caller.rs": _sha(caller + b"\n"),
            "original/lib.rs": _sha(original), "verified/lib.rs": _sha(verified),
        },
        "ghost_strip_identity": _ghost_strip(verified) == original,
        "no_assume_admit_or_unchecked": True,
        "no_comparator_purity_or_freeze_semantic_axiom": True,
        "not_claimed": ["full caller proof", "caller CFG/branch selection", "sort4 proof", "sort8 summary",
                        "c1 MU identity/owner restoration", "type_interp derived from native heap"],
        "bridge_positive_static_limitations": [
            "open/close MaybeUninit lemma statements, pointer casts/provenance, and cell equality after restoration require cloud verifier confirmation",
            "the full MaybeUninit foreach owner remains opaque and framed",
            "no inverse new_maybe_uninit(inner(old)) law is assumed",
        ] if case == "bridge-positive" else [],
    }
    (out / "fixture.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record
