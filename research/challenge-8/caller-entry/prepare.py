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
CASES = ("prefix-native", "bridge-positive", "range-negative", "duplicate-negative")
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
    cases = (HERE / "bridge-cases.rs").read_bytes()
    marker = b"// CASE " + name.encode() + b"\n"
    _need(cases.count(marker) == 1, f"case block missing or ambiguous: {name}")
    start = cases.index(marker) + len(marker)
    end = cases.find(b"// END CASE\n", start)
    _need(end >= 0, f"case block unterminated: {name}")
    body = cases[start:end]
    body = re.sub(rb"(?m)^//(?!@)[^\r\n]*(?:\r?\n|$)", b"", body)
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


def _source_line(source: bytes, offset: int) -> int:
    return source.count(b"\n", 0, offset) + 1


def prepare(repo: Path, out: Path, case: str) -> dict:
    """Generate one cloud fixture. This function performs no compilation/proof."""
    _need(case in CASES, f"unknown case {case!r}; expected one of {CASES}")
    _need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
          "GITHUB_ACTIONS" not in os.environ and
          os.environ.get("LANE") == "o26-sort4-caller-entry",
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

    scratch_at = caller.index(SCRATCH_LINE)
    prefix_end = scratch_at + len(SCRATCH_LINE)
    prefix = caller[:prefix_end]
    cond1_at = caller.index(SORT8_CONDITION, prefix_end)
    cond2_at = caller.index(SORT4_CONDITION, cond1_at)
    cond3_at = caller.index(ELSE_CONDITION, cond2_at)
    cond1 = caller[cond1_at:cond1_at + len(SORT8_CONDITION)]
    cond2 = caller[cond2_at:cond2_at + len(SORT4_CONDITION)]
    cond3 = caller[cond3_at:cond3_at + len(ELSE_CONDITION)]
    call_anchor = b"sort4_stable(v_base, scratch_base, is_less);"
    call_at = caller.index(call_anchor)
    _need(b"is_less(" not in prefix and b"ptr::copy_nonoverlapping(" not in prefix,
          "callback or copy appears before the first call in the preserved prefix")
    case_body = _case_source(case)
    indented_case = b"            " + case_body.replace(b"\n", b"\n            ").rstrip()
    branch = (b"\n\n        " + cond1 + b"\n            return;\n        " + cond2 + b"\n" +
              indented_case + b"\n        " + cond3 + b"\n            return;\n        }\n    }\n}")
    fragment = prefix + branch
    lemma = _lemma(memory_pre) if case == "bridge-positive" else b""
    common_preamble = FEATURES + freeze_marker + b"\n"
    verified = common_preamble + lemma + fragment
    original = common_preamble + _ghost_strip(fragment)
    _need(_ghost_strip(verified) == original,
          "ghost-stripped verified fragment differs from constructed original fragment")
    _need(not any(token in verified for token in (b"assume", b"admit", b"unchecked")),
          "fixture contains a forbidden assumption/admission marker")
    _need(b"sort8_stable(" not in fragment and b"insert_tail(" not in fragment and
          b"sort4_stable(v_base.add(len_div_2)" not in fragment,
          "diagnostic fragment crossed its explicit first-call boundary")
    _need(call_anchor not in fragment,
          "diagnostic fragment must stop at the first callsite without invoking sort4")

    out.mkdir(parents=True)
    (out / "original").mkdir()
    (out / "verified").mkdir()
    (out / "actual-caller.rs").write_bytes(caller + b"\n")
    (out / "original/lib.rs").write_bytes(original)
    (out / "verified/lib.rs").write_bytes(verified)

    line_targets = {}
    for label, needle in (
        ("positive_identity_lemma", b"c1_entry_identity::<T, F>"),
        ("positive_size_guard", b"if (0 < std::mem::size_of::<T>())"),
        ("range_negative_split", b"array_split::<T>(v_base, len + 1);"),
        ("duplicate_negative_authority", b"v_base[..len] |-> ?xs"),
        ("source_sort8_condition", SORT8_CONDITION),
        ("source_sort4_condition", SORT4_CONDITION),
    ):
        if needle in verified:
            line_targets[label] = verified[:verified.index(needle)].count(b"\n") + 1
    line_lists = {}
    for label, needle in (
        ("thread_token", b"assert thread_token(?t);"),
        ("current_thread", b"assert t == currentThread;"),
        ("type_interp_T", b"assert type_interp::<T>();"),
        ("type_interp_F", b"assert type_interp::<F>();"),
        ("source_array", b"assert v_base[..len] |-> ?source_all;"),
        ("source_owners", b"assert foreach(source_all, own::<T>(t));"),
        ("source_array_split", b"array_split::<T>(v_base, 4);"),
        ("source_owners_split", b"foreach_split(source_all, own::<T>(t), 4);"),
        ("maybeuninit_pointer", b"let mu_base = strip_pointer_metadata"),
        ("scratch_length", b"let scratch_len = ptr_len(scratch);"),
        ("maybeuninit_array", b"assert mu_base[..scratch_len] |-> ?mu_all;"),
        ("maybeuninit_owners", b"assert foreach(mu_all, own::<MaybeUninit<T>>(t));"),
        ("maybeuninit_array_split", b"array_split::<MaybeUninit<T>>(mu_base, 4);"),
        ("maybeuninit_array_unroll", b"open array::<MaybeUninit<T>>(mu_base"),
        ("maybeuninit_open_lemma", b"std::mem::open_MaybeUninit::<T>(mu_base"),
        ("optional_cell", b"assert *scratch_base |-> ?option0;"),
        ("array_optional_close", b"close array_::<T>(scratch_base"),
        ("destination_array_for_c1", b"assert array_::<T>(scratch_base, 4, ?destination_before);"),
        ("pointer_limits", b"assert pointer_within_limits(scratch_base"),
        ("positive_size_guard", b"if (0 < std::mem::size_of::<T>())"),
        ("identity_lemma_call", b"c1_entry_identity::<T, F>"),
        ("maybeuninit_close_lemma", b"std::mem::close_MaybeUninit_<T>(mu_base"),
        ("maybeuninit_array_join", b"array_join::<MaybeUninit<T>>(mu_base);"),
        ("source_array_join", b"array_join::<T>(v_base);"),
        ("source_owner_append", b"foreach_append(take(4, source_all), drop(4, source_all));"),
        ("range_negative", b"array_split::<T>(v_base, len + 1);"),
        ("duplicate_negative", b"assert v_base[..len] |-> ?xs"),
    ):
        matches = list(re.finditer(re.escape(needle), verified))
        if matches:
            line_lists[label] = [verified[:match.start()].count(b"\n") + 1 for match in matches]

    record = {
        "classification": "SOURCE_LINKED_CALLER_ENTRY_DIAGNOSTIC_FRAGMENT_NOT_FULL_CALLER_PROOF",
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
            "caller_runtime_source_exact": True, "caller_signature_and_body_brace_balanced": True,
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
        "fragment_boundary": "first sort4_stable callsite is linked by source certificate; diagnostic branch stops there and returns",
        "source_mapped_condition_bytes": {
            "sort8_condition": cond1.decode(), "sort4_selected_condition": cond2.decode(),
            "else_condition": cond3.decode(), "preserved_verbatim_from_actual_caller": True,
            "prefix_source_byte_start": caller_start,
            "prefix_source_byte_end_exclusive": caller_start + prefix_end,
            "sort8_condition_byte_start": caller_start + cond1_at,
            "sort4_selected_condition_byte_start": caller_start + cond2_at,
            "else_condition_byte_start": caller_start + cond3_at,
            "first_sort4_call_byte_start": caller_start + call_at,
            "first_sort4_call_source": call_anchor.decode(),
        },
        "prefix_source_exact_through_scratch_base": prefix == caller[:prefix_end],
        "branch_conditions_exact": True, "no_comparator_or_copy_before_first_sort4": True,
        "first_sort4_runtime_call_in_fragment": False,
        "sort8_or_later_call_summaries": False,
        "case_constraints": {
            "prefix-native": "no added proof requirement or post; native generated mutable-reference entry only",
        "bridge-positive": "identity boundary entailment uses exact captured c1 pre inside a ghost positive-size guard; ZST branch gap retained",
            "range-negative": "array_split at len+1 is intended out-of-range authority control",
            "duplicate-negative": "duplicate whole-array authority assertion is intended duplicate-authority control",
        }[case],
        "targeted_ghost_statement_lines": line_targets,
        "targeted_ghost_statement_line_lists": line_lists,
        "generated": {
            "actual-caller.rs": _sha(caller + b"\n"),
            "original/lib.rs": _sha(original), "verified/lib.rs": _sha(verified),
        },
        "ghost_strip_identity": _ghost_strip(verified) == original,
        "no_assume_admit_or_unchecked": True,
        "no_comparator_purity_or_freeze_semantic_axiom": True,
        "not_claimed": ["full caller refinement", "sort4 proof", "sort8 summary", "second sort4/c2 summary"],
        "bridge_positive_static_limitations": [
            "open/close MaybeUninit lemma statements, pointer casts/provenance, and cell equality after restoration require cloud verifier confirmation",
            "the full MaybeUninit foreach owner remains opaque and framed",
            "if stock lemmas cannot establish matching pointer permissions or restored cell equality, that remains a proof blocker",
        ] if case == "bridge-positive" else [],
    }
    (out / "fixture.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return record
