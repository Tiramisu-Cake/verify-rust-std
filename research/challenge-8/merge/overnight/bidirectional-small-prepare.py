#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only exact-source preparer for the bounded len-2/3 profile."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load preparation module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def option_stage_ghost() -> str:
    return r"""/*@
pred bidirectional_small_optional_slot<T>(len: usize, slot: *mut T; old: option<T>) =
    if len == 3 { *slot |-?-> old } else { old == none };

// Reattribute exactly one existing current cell to a full-pointer-equal alias.
// Provenance and metadata equality are required; no permission is produced by
// address arithmetic and no source owner is duplicated or reset to a snapshot.
lem bidirectional_small_current_cell_alias<T>(t: thread_id_t,
        original: *T, selected: *T)
    req original as pointer == selected as pointer &*&
        *original |-> ?current_value &*& <T>.own(t, current_value);
    ens *selected |-> current_value &*& <T>.own(t, current_value);
{
    assert original as pointer == selected as pointer;
}

// Check either of the two forward-left cursor cells in a context that does
// not assume which one is selected.  The actual odd-copy caller invokes this
// after deriving left == src from left_nonempty; keeping that stronger fact
// out of this contract makes both checked proof branches feasible here.
lem bidirectional_small_left_cell_association<T>(t: thread_id_t,
        src: *T, left: *const T, last_src: *const T, value: T)
    req (left == src || left == src + 1) &*& last_src == left &*&
        0 < std::mem::size_of::<T>() &*&
        std::mem::size_of::<T>() <= isize::MAX &*&
        0 < std::mem::align_of::<T>() &*&
        0 < src as usize &*& 0 < (src + 1) as usize &*&
        src as usize % std::mem::align_of::<T>() == 0 &*&
        (src + 1) as usize % std::mem::align_of::<T>() == 0 &*&
        pointer_within_limits(src) == true &*&
        pointer_within_limits(src + 1) == true &*&
        object_pointer_within_limits(src, std::mem::size_of::<T>()) == true &*&
        object_pointer_within_limits(src + 1, std::mem::size_of::<T>()) == true &*&
        (if left == src {
            *src |-> value &*& <T>.own(t, value)
         } else {
            *(src + 1) |-> value &*& <T>.own(t, value)
         });
    ens *last_src |-> value &*& <T>.own(t, value);
{
    if left == src {
        assert last_src == src;
        assert last_src as pointer == src as pointer;
        bidirectional_small_current_cell_alias::<T>(t, src as *T, last_src as *T);
        assert *last_src |-> ?odd_src0;
    } else {
        assert left == src + 1;
        assert last_src == src + 1;
        assert last_src as pointer == (src + 1) as pointer;
        bidirectional_small_current_cell_alias::<T>(t, (src + 1) as *T, last_src as *T);
        assert *last_src |-> ?odd_src1;
    }
}

fix bidirectional_small_option_same<T>(old_value: option<T>, new_value: option<T>) -> bool {
    old_value == new_value
}

fix bidirectional_small_option_is_some<T>(value: option<T>) -> bool {
    match value {
        none => false,
        some(ignored_payload) => true
    }
}

lem bidirectional_small_option_same_reflexive<T>(value: option<T>)
    req true;
    ens bidirectional_small_option_same::<T>(value, value) == true;
{
    match value {
        none => {
            assert bidirectional_small_option_same::<T>(value, value) == true;
        }
        some(payload) => {
            assert bidirectional_small_option_same::<T>(value, value) == true;
        }
    }
}

fix bidirectional_small_unwind_options<T>(len: usize,
        old0: option<T>, old1: option<T>, old2: option<T>,
        now0: option<T>, now1: option<T>, now2: option<T>) -> bool {
    if len == 2 {
        (bidirectional_small_option_same::<T>(old0, now0) &&
         bidirectional_small_option_same::<T>(old1, now1)) ||
        (bidirectional_small_option_is_some::<T>(now0) &&
         bidirectional_small_option_same::<T>(old1, now1)) ||
        (bidirectional_small_option_is_some::<T>(now0) &&
         bidirectional_small_option_is_some::<T>(now1))
    } else if len == 3 {
        (bidirectional_small_option_same::<T>(old0, now0) &&
        bidirectional_small_option_same::<T>(old1, now1) &&
        bidirectional_small_option_same::<T>(old2, now2)) ||
        (bidirectional_small_option_is_some::<T>(now0) &&
        bidirectional_small_option_same::<T>(old1, now1) &&
        bidirectional_small_option_same::<T>(old2, now2)) ||
        (bidirectional_small_option_is_some::<T>(now0) &&
        bidirectional_small_option_is_some::<T>(now1) &&
        bidirectional_small_option_is_some::<T>(now2))
    } else {
        false
    }
}

lem bidirectional_small_unwind_unchanged<T>(len: usize,
        old0: option<T>, old1: option<T>, old2: option<T>)
    req len == 2 || len == 3;
    ens bidirectional_small_unwind_options::<T>(len,
        old0, old1, old2, old0, old1, old2) == true;
{
    bidirectional_small_option_same_reflexive::<T>(old0);
    bidirectional_small_option_same_reflexive::<T>(old1);
    if len == 3 {
        bidirectional_small_option_same_reflexive::<T>(old2);
    }
    assert bidirectional_small_unwind_options::<T>(len,
        old0, old1, old2, old0, old1, old2) == true;
}
@*/
"""


def c1_separation(i: int, j: int) -> str:
    src = f"(v as *T) as usize + {i} * std::mem::size_of::<T>()"
    dst = f"dst as usize + {j} * std::mem::size_of::<T>()"
    return f"({src} + std::mem::size_of::<T>() <= {dst} || {dst} + std::mem::size_of::<T>() <= {src})"


def bidirectional_contract23() -> str:
    lines = [
        "/*@",
        "req thread_token(?t) &*& t == currentThread &*&",
        "    type_interp::<T>() &*& type_interp::<F>() &*&",
        "    (ptr_len(v) == 2 || ptr_len(v) == 3) &*&",
        "    0 < std::mem::size_of::<T>() &*&",
        "    3 * std::mem::size_of::<T>() <= isize::MAX &*&",
        "    0 < std::mem::align_of::<T>() &*&",
        "    0 < (v as *T) as usize &*& 0 < dst as usize &*&",
        "    (v as *T) as usize % std::mem::align_of::<T>() == 0 &*&",
        "    dst as usize % std::mem::align_of::<T>() == 0 &*&",
        "    (v as *T) as usize <= usize::MAX - ptr_len(v) * std::mem::size_of::<T>() &*&",
        "    dst as usize <= usize::MAX - ptr_len(v) * std::mem::size_of::<T>() &*&",
        "    object_pointer_within_limits(v as *T, ptr_len(v) * std::mem::size_of::<T>()) == true &*&",
        "    object_pointer_within_limits(dst, ptr_len(v) * std::mem::size_of::<T>()) == true &*&",
        "    pointer_within_limits(v as *T) == true &*&",
        "    pointer_within_limits((v as *T) + 1) == true &*&",
        "    pointer_within_limits((v as *T) + 2) == true &*&",
        "    pointer_within_limits((v as *T) + ptr_len(v)) == true &*&",
        "    pointer_within_limits(dst) == true &*&",
        "    pointer_within_limits(dst + 1) == true &*&",
        "    pointer_within_limits(dst + 2) == true &*&",
        "    pointer_within_limits(dst + ptr_len(v)) == true &*&",
        "    ((v as *T) as usize + ptr_len(v) * std::mem::size_of::<T>() <= dst as usize ||",
        "     dst as usize + ptr_len(v) * std::mem::size_of::<T>() <= (v as *T) as usize) &*&",
        "    c1_one_pointer_domain::<T>((v as *T) as *mut T) &*&",
        "    c1_one_pointer_domain::<T>(((v as *T) + 1) as *mut T) &*&",
        "    c1_one_pointer_domain::<T>(dst) &*&",
        "    c1_one_pointer_domain::<T>(dst + 1) &*&",
        "    (if ptr_len(v) == 3 {",
        "        c1_one_pointer_domain::<T>(((v as *T) + 2) as *mut T) &*&",
        "        c1_one_pointer_domain::<T>(dst + 2)",
        "     } else { true }) &*&",
        "    (v as *T) as pointer != ((v as *T) + 1) as pointer &*&",
        "    (if ptr_len(v) == 3 { (v as *T) as pointer != ((v as *T) + 2) as pointer } else { true }) &*&",
    ]
    for i in range(3):
        for j in range(3):
            cond = "ptr_len(v) == 3" if i == 2 and j == 2 else (
                "ptr_len(v) == 3" if i == 2 or j == 2 else None)
            relation = c1_separation(i, j)
            lines.append(
                f"    (if {cond} {{ {relation} }} else {{ true }}) &*&"
                if cond else f"    {relation} &*&"
            )
    lines += [
        "    *((v as *T)) |-> ?source0 &*& <T>.own(t, source0) &*&",
        "    *((v as *T) + 1) |-> ?source1 &*& <T>.own(t, source1) &*&",
        "    (if ptr_len(v) == 3 { *((v as *T) + 2) |-> ?source2 &*& <T>.own(t, source2) } else { true }) &*&",
        "    *dst |-?-> ?dst0 &*& *(dst + 1) |-?-> ?dst1 &*&",
        "    bidirectional_small_optional_slot::<T>(ptr_len(v), dst + 2, ?dst2) &*&",
        "    *is_less |-> ?f0 &*& <F>.own(t, f0);",
        "@*//*@",
        "ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&",
        "    *((v as *T)) |-> ?source0_after &*& <T>.own(t, source0_after) &*&",
        "    *((v as *T) + 1) |-> ?source1_after &*& <T>.own(t, source1_after) &*&",
        "    (if ptr_len(v) == 3 { *((v as *T) + 2) |-> ?source2_after &*& <T>.own(t, source2_after) } else { true }) &*&",
        "    *dst |-> ?out0 &*& *(dst + 1) |-> ?out1 &*&",
        "    (if ptr_len(v) == 3 { *(dst + 2) |-> ?out2 } else { true }) &*&",
        "    *is_less |-> ?f1 &*& <F>.own(t, f1);",
        "@*//*@",
        "on_unwind_ens thread_token(t) &*& type_interp::<T>() &*& type_interp::<F>() &*&",
        "    *((v as *T)) |-> ?source0_unwind &*& <T>.own(t, source0_unwind) &*&",
        "    *((v as *T) + 1) |-> ?source1_unwind &*& <T>.own(t, source1_unwind) &*&",
        "    (if ptr_len(v) == 3 { *((v as *T) + 2) |-> ?source2_unwind &*& <T>.own(t, source2_unwind) } else { true }) &*&",
        "    *dst |-?-> ?partial0 &*& *(dst + 1) |-?-> ?partial1 &*&",
        "    (if ptr_len(v) == 3 {",
        "        *(dst + 2) |-?-> ?partial2 &*&",
        "        bidirectional_small_unwind_options::<T>(ptr_len(v), dst0, dst1, dst2, partial0, partial1, partial2) == true",
        "     } else {",
        "        bidirectional_small_unwind_options::<T>(ptr_len(v), dst0, dst1, none, partial0, partial1, none) == true",
        "     }) &*&",
        "    *is_less |-> ?f_unwind &*& <F>.own(t, f_unwind);",
        "    @*/",
    ]
    return "\n".join(lines)


def insert_len23_invariant(body: str) -> str:
    loop = "        for _ in 0..len_div_2 {\n"
    src_init = "    let src = v.as_ptr();\n"
    odd_source = "            let last_src = if left_nonempty { left } else { right };\n"
    if body.count(loop) != 1 or body.count(src_init) != 1 or body.count(odd_source) != 1:
        raise RuntimeError("bidirectional cursor/loop/odd-copy anchors changed")
    body = body.replace(src_init, src_init + "    //@ size_align::<T>();\n", 1)

    contract = bidirectional_contract23()
    pure_start = contract.index("    (ptr_len(v) == 2")
    pure_end = contract.index("    *((v as *T)) |->")
    pure_geometry = " ".join(contract[pure_start:pure_end].split())
    invariant = (
        "            //@ inv thread_token(t) &*& t == currentThread &*& "
        "type_interp::<T>() &*& type_interp::<F>() &*& lifetime_token(func_lft) &*& "
        + pure_geometry + " "
        "len == ptr_len(v) &*& (len == 2 || len == 3) &*& len_div_2 == 1 &*& "
        "src == (v as *T) &*& iter |-> ?iteration &*& "
        "iteration.start == 1 &*& iteration.end == 1 &*& "
        "std::ops::struct_Range_padding::<usize>(mir_stack_addr(34)) &*& "
        "(*mir_stack_addr(34)).start |-> ?range_result_start &*& "
        "(*mir_stack_addr(34)).end |-> ?range_result_end &*& "
        "std::ops::struct_Range_padding::<usize>(mir_stack_addr(35)) &*& "
        "(*mir_stack_addr(35)).start |-> ?range_input_start &*& "
        "(*mir_stack_addr(35)).end |-> ?range_input_end &*& "
        "struct_std_tuple_3__padding::<*T, *T, *T>(mir_stack_addr(53)) &*& "
        "(*mir_stack_addr(53)).0 |-?-> ?up_field0 &*& "
        "(*mir_stack_addr(53)).1 |-?-> ?up_field1 &*& "
        "(*mir_stack_addr(53)).2 |-?-> ?up_field2 &*& "
        "struct_std_tuple_3__padding::<*T, *T, *T>(mir_stack_addr(65)) &*& "
        "(*mir_stack_addr(65)).0 |-?-> ?down_field0 &*& "
        "(*mir_stack_addr(65)).1 |-?-> ?down_field1 &*& "
        "(*mir_stack_addr(65)).2 |-?-> ?down_field2 &*& "
        "*(src as *T) |-> ?inv_source0 &*& <T>.own(t, inv_source0) &*& "
        "*(src + 1) |-> ?inv_source1 &*& <T>.own(t, inv_source1) &*& "
        "(if len == 3 { *(src + 2) |-> ?inv_source2 &*& <T>.own(t, inv_source2) } else { true }) &*& "
        "*is_less |-> ?inv_f &*& <F>.own(t, inv_f) &*& "
        "*dst |-?-> dst0 &*& *(dst + 1) |-?-> dst1 &*& "
        "bidirectional_small_optional_slot::<T>(len, dst + 2, dst2) &*& "
        "left == src &*& right == src + 1 &*& left_rev == src &*& "
        "right_rev == src + (len - 1) &*& dst_1 == dst &*& "
        "dst_rev == dst + (len - 1);\n"
        "            //@ { size_align::<T>(); if len == 3 { bidirectional_small_unwind_unchanged::<T>(len, dst0, dst1, dst2); } else { bidirectional_small_unwind_unchanged::<T>(len, dst0, dst1, none); } }\n"
        "            //@ { address_stride_aligned(src as usize, len - 1, std::mem::size_of::<T>(), std::mem::align_of::<T>()); open c1_one_pointer_domain::<T>(src as *mut T); open c1_one_pointer_domain::<T>((src + 1) as *mut T); open c1_one_pointer_domain::<T>(dst); open c1_one_pointer_domain::<T>(dst + 1); }\n"
        "            //@ { address_stride_aligned(dst as usize, len - 1, std::mem::size_of::<T>(), std::mem::align_of::<T>()); open bidirectional_small_optional_slot::<T>(len, dst + 2, dst2); if len == 3 { open c1_one_pointer_domain::<T>((src + 2) as *mut T); open c1_one_pointer_domain::<T>(dst + 2); } }\n"
    )
    body = body.replace(loop, loop + invariant, 1)
    # The one forward merge leaves left at src or src+1 and right at src+1
    # or src+2.  In the left-nonempty branch, strict cursor ordering derives
    # left == src.  The checked helper has a broader precondition without that
    # ordering fact, so both left-cell associations are verified in its body.
    # The actual call remains on the derived src cell and uses existing chunks.
    odd_source_cases = (
        "            //@ { assert len == 3; if left_nonempty { assert left == src; "
        "assert *left |-> ?left_current; bidirectional_small_left_cell_association::<T>(t, src as *T, left, last_src, left_current); } else { "
        "if right == src + 1 { assert last_src == src + 1; assert last_src as pointer == (src + 1) as pointer; bidirectional_small_current_cell_alias::<T>(t, (src + 1) as *T, last_src as *T); "
        "assert *last_src |-> ?odd_src1; } "
        "else { assert right == src + 2; assert last_src == src + 2; assert last_src as pointer == (src + 2) as pointer; bidirectional_small_current_cell_alias::<T>(t, (src + 2) as *T, last_src as *T); "
        "assert *last_src |-> ?odd_src2; } } }\n"
    )
    return body.replace(odd_source, odd_source + odd_source_cases, 1)


def main() -> None:
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or
            os.environ.get("GITHUB_REF") != "refs/heads/overnight/merge-26.10"):
        raise RuntimeError("bounded bidirectional preparation requires own GitHub-hosted Actions branch")
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("refusing existing generated fixture")

    base = load_module("merge_bidirectional_base_prepare", HERE / "bidirectional-prepare.py")
    gate = load_module("merge_stock_source_gate", HERE.parent / "stock-26.10/prove.py")
    admission = gate.admit_source()
    source = SOURCE.read_text()
    strip_diff_path = args.output.with_suffix(".strip-diff.json")
    freeze_source = base.FREEZE_SOURCE.read_text()
    if (freeze_source.count(base.FREEZE_TRAIT) != 1 or
            sha(base.FREEZE_TRAIT.encode()) != base.FREEZE_TRAIT_SHA256):
        raise RuntimeError("exact repository FreezeMarker declaration changed")

    helper = load_module("merge_actual_prepare", HERE / "actual-prepare.py")
    out = "#![feature(unboxed_closures, core_intrinsics)]\n#![allow(dead_code)]\nuse core::ptr;\nuse core::intrinsics;\ntrait FreezeMarker {}\n"
    domain_source = (HERE / "pointer-domain-cases.rs").read_text()
    ghost_start = domain_source.index("/*@")
    ghost_end = domain_source.index("@*/", ghost_start) + 3
    domain_ghost = domain_source[ghost_start:ghost_end]
    out += domain_ghost + "\n" + option_stage_ghost()
    out += "// CASE_BEGIN bidirectional_merge_len23\n"
    records: dict[str, object] = {}
    for name in ("merge_up", "merge_down"):
        prepared, record = base.actual_helper(
            name, source, gate.SIGNATURES[name], helper, strip_diff_path)
        out += prepared + "\n"
        records[name] = record

    panic = base.extract(source, base.PANIC_SIGNATURE, "panic_on_ord_violation")
    if sha(panic.encode()) != base.PANIC_BODY_SHA256:
        raise RuntimeError("panic_on_ord_violation exact repository body changed")
    prepared_panic = panic[:panic.index("{")] + base.panic_contract() + panic[panic.index("{"):]
    base.require_strip_exact("panic_on_ord_violation", prepared_panic, panic, strip_diff_path)
    out += prepared_panic + "\n"
    records["panic_on_ord_violation"] = {
        "exact_source_sha256": sha(panic.encode()),
        "accepted_source_body_sha256": base.PANIC_BODY_SHA256,
        "fixture_body_sha256": sha(prepared_panic.encode()),
        "body_present": True,
        "normal_post": "false",
        "unwind_post": "thread_token(t) (caller frame preserved)",
        "contract_basis": "exact unconditional panic body; no normal return or added termination premise",
    }

    bidir = base.extract(source, gate.SIGNATURES["bidirectional_merge"], "bidirectional_merge")
    verified = bidir[:bidir.index("{")] + bidirectional_contract23() + bidir[bidir.index("{"):]
    verified = insert_len23_invariant(verified)
    base.require_strip_exact("bidirectional_merge", verified, bidir, strip_diff_path)
    out += verified + "\n// CASE_END bidirectional_merge_len23\n"
    records["bidirectional_merge"] = {
        "exact_source_sha256": sha(bidir.encode()),
        "fixture_body_sha256": sha(verified.encode()),
        "ghost_strip_exact": True,
        "body_present": True,
        "domain": "len=2 or len=3; positive stride/alignment; bounded separate source/destination spans; explicit C1 one-cell domains and pairwise separation",
        "source_resources": "current T points-to and owner for indices 0/1; index 2 conditional on len=3",
        "destination_resources": "arbitrary writable initialized-or-uninitialized options for indices 0/1; index 2 conditional on len=3; no destination T.own",
        "normal_post": "current source values/owners and F owner; every destination option Some; no destination owner or ordering claim",
        "unwind_post": "checked option-match relation: unchanged options before first copy; only slot 0 Some after forward copy; all present slots Some before guard panic",
        "loop_invariant": "one Some/body iteration for len_div_2=1, complete source/destination/F frame, old options, cursor positions and Range/tuple stack facts at MIR IDs 34/35/53/65",
        "stack_role_certification": "pending fresh exact-source/case certification; no claim inherited from len2 profile",
        "caller_derivation": "allocation/provenance to explicit per-cell C1 premises remains open",
        "scope_warning": "bounded actual-body diagnostic, not a generic safe caller or whole merge proof",
    }
    args.output.write_text(out)
    args.output.with_suffix(".admission.json").write_text(json.dumps({
        "source_admission": admission,
        "checked_domain_ghost_sha256": sha(domain_ghost.encode()),
        "panic_on_ord_violation_body_sha256": base.PANIC_BODY_SHA256,
        "freeze_marker_declaration_sha256": base.FREEZE_TRAIT_SHA256,
        "freeze_marker_adapter": "empty local declaration only; no blanket impl or Freeze/purity theorem",
        "scope": "exact unchanged bidirectional_merge len=2-or-3 with actual merge_up/down/panic bodies; experimental and unaccepted pending hosted matrix",
        "cases": records,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
