#!/usr/bin/env python3
"""Cloud-only constructor for source-certified A1 diagnostic fixture inputs.

Import is inert. The executable entry point is restricted to the authorized
Cloud Build phase and /workspace paths. Constructed source is diagnostic input;
this module neither launches nor claims compilation or verification.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any


PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
SOURCE_COMMIT = "a22282dac3765c7d9948e6edfb0ae74102a4280b"
SMALLSORT = "library/core/src/slice/sort/shared/smallsort.rs"
QUICKSORT = "library/core/src/slice/sort/stable/quicksort.rs"
SHARED = "library/core/src/slice/sort/shared/mod.rs"
MARKER = "library/core/src/marker.rs"
SOURCE_PINS = {
    SMALLSORT: "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1",
    QUICKSORT: "4a41df6bc7c4e0a6fcb655fde9bf73ed62f3a675ca805f2f766919ce249d8f4c",
    SHARED: "fa9eec2901bafba25c9c1e1684df76dbb1f86e0bbd04f18f3e67cee54dcdfcc8",
    # Derived from the pinned source commit because the A1 source manifest has
    # no separate marker.rs hash. The source commit and exact declaration span
    # are both recorded in every certificate.
    MARKER: "f7e098f8b9ad1a6dded90b81fd943afbe6c8d60934354838998880fe05f80755",
}

# Inclusive one-based source spans from the A1 source review. Each span also
# has a semantic anchor checked below, so shifted/stale lines fail closed.
SPANS = {
    "trait": (SMALLSORT, 18, 28, b"pub(crate) trait StableSmallSortTypeImpl"),
    "default_impl": (SMALLSORT, 30, 47, b"impl<T> StableSmallSortTypeImpl for T"),
    "freeze_impl": (SMALLSORT, 49, 63, b"impl<T: FreezeMarker> StableSmallSortTypeImpl for T"),
    "threshold_constants": (SMALLSORT, 173, 188, b"const SMALL_SORT_FALLBACK_THRESHOLD: usize = 16;"),
    "helper_prefix": (SMALLSORT, 220, 254, b"fn small_sort_general_with_scratch<T: FreezeMarker"),
    "helper_full": (SMALLSORT, 220, 293, b"fn small_sort_general_with_scratch<T: FreezeMarker"),
    "quicksort_signature": (QUICKSORT, 16, 22, b"pub fn quicksort<T, F: FnMut(&T, &T) -> bool>("),
    "quicksort_guard_and_call": (QUICKSORT, 23, 29, b"    loop {"),
    "freeze_marker_import_and_block": (SHARED, 3, 13, b"use crate::marker::Freeze;"),
    "std_freeze_declaration": (MARKER, 900, 908, b"pub unsafe auto trait Freeze {}"),
}

SOURCE_FILES = {
    "trait": "StableSmallSortTypeImpl (full original prototype)",
    "default_impl": "default impl, including default threshold and insertion call",
    "freeze_impl": "Freeze impl, including threshold and actual helper call",
    "threshold_constants": "source definitions for 16, 32, and 32+16 scratch length",
    "helper_prefix": "actual helper bytes through the first sort4_stable boundary",
    "helper_full": "full actual helper source used only to form the diagnostic prefix cuts",
    "quicksort_signature": "unrestricted actual quicksort signature",
    "quicksort_guard_and_call": "original guard, generic small_sort call, and return",
    "freeze_marker_import_and_block": "Freeze import and original FreezeMarker block",
    "std_freeze_declaration": "original std::marker::Freeze declaration provenance",
}

OBSERVER_SUFFIX = {
    "P0c": """\n        //@ assert len <= 32;\n        let requirement = len + 16;\n        //@ assert requirement <= 48;\n        return;\n    }\n    // A1 diagnostic cut: non-base continuation is intentionally not present.\n    return;\n}\n}\n""",
    "N-false31": """\n        //@ assert len <= 31;\n        let requirement = len + 16;\n        //@ assert requirement <= 48;\n        return;\n    }\n    // A1 diagnostic cut: non-base continuation is intentionally not present.\n    return;\n}\n}\n""",
}


class FixtureError(ValueError):
    """The pinned input, source span, or generated fixture contract is invalid."""


def _need(ok: bool, why: str) -> None:
    if not ok:
        raise FixtureError(why)


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read_sources(source_root: Path) -> dict[str, bytes]:
    sources = {}
    for rel, expected in SOURCE_PINS.items():
        path = source_root / rel
        _need(path.is_file(), f"source file missing: {rel}")
        raw = path.read_bytes()
        _need(_sha(raw) == expected, f"source SHA-256 mismatch: {rel}")
        sources[rel] = raw
    return sources


def _span(raw: bytes, start: int, end: int, anchor: bytes, label: str) -> bytes:
    lines = raw.splitlines(keepends=True)
    _need(1 <= start <= end <= len(lines), f"invalid source span: {label}")
    result = b"".join(lines[start - 1:end])
    _need(anchor in result, f"source span anchor mismatch: {label}")
    return result


def _items(sources: dict[str, bytes]) -> tuple[dict[str, bytes], dict[str, Any]]:
    items: dict[str, bytes] = {}
    inventory: dict[str, Any] = {
        "source_commit": SOURCE_COMMIT,
        "files": {rel: {"sha256": _sha(raw)} for rel, raw in sources.items()},
        "items": {},
        "source_impl_inventory": {
            "default16": {
                "source_impl_identity": "impl<T> StableSmallSortTypeImpl for T",
                "source_item": "StableSmallSortTypeImpl::small_sort_threshold",
                "compiler_impl_id": None, "compiler_item_id": None,
            },
            "freeze32": {
                "source_impl_identity": "impl<T: FreezeMarker> StableSmallSortTypeImpl for T",
                "source_item": "StableSmallSortTypeImpl::small_sort_threshold",
                "compiler_impl_id": None, "compiler_item_id": None,
            },
        },
        "compiler_inventory_status": "PENDING_CLOUD_COMPILER_QUERY",
    }
    for name, (rel, start, end, anchor) in SPANS.items():
        raw = _span(sources[rel], start, end, anchor, name)
        items[name] = raw
        inventory["items"][name] = {
            "file": rel,
            "line_start": start,
            "line_end": end,
            "sha256": _sha(raw),
            "exact_bytes_base64": base64.b64encode(raw).decode("ascii"),
            "description": SOURCE_FILES[name],
        }
    # The std Freeze declaration is provenance only; including it as a local
    # lang-trait definition would duplicate the compiler's builtin item.
    inventory["items"]["std_freeze_declaration"]["emitted_as_source"] = False
    return items, inventory


def _assert_source_relations(items: dict[str, bytes]) -> None:
    _need(b"default fn small_sort_threshold()" in items["default_impl"],
          "default threshold body missing")
    _need(b"SMALL_SORT_FALLBACK_THRESHOLD" in items["default_impl"],
          "default threshold no longer uses source constant")
    _need(b"fn small_sort_threshold()" in items["freeze_impl"] and
          b"SMALL_SORT_GENERAL_THRESHOLD" in items["freeze_impl"],
          "Freeze threshold body missing or changed")
    _need(b"insertion_sort_shift_left(v, 1, is_less)" in items["default_impl"],
          "actual default insertion call missing")
    _need(b"small_sort_general_with_scratch(v, scratch, is_less)" in items["freeze_impl"],
          "actual Freeze helper call missing")
    _need(b"SMALL_SORT_GENERAL_THRESHOLD: usize = 32" in items["threshold_constants"] and
          b"SMALL_SORT_FALLBACK_THRESHOLD: usize = 16" in items["threshold_constants"] and
          b"SMALL_SORT_GENERAL_SCRATCH_LEN: usize = SMALL_SORT_GENERAL_THRESHOLD + 16"
          in items["threshold_constants"], "source threshold/scratch constants mismatch")
    _need(b"use crate::marker::Freeze;" in items["freeze_marker_import_and_block"] and
          b"pub(crate) trait FreezeMarker {}" in items["freeze_marker_import_and_block"] and
          b"impl<T: Freeze> FreezeMarker for T {}" in items["freeze_marker_import_and_block"],
          "original FreezeMarker block mismatch")
    _need(b"pub unsafe auto trait Freeze {}" in items["std_freeze_declaration"],
          "original Freeze declaration not found")
    _need(b"T::small_sort_threshold()" in items["quicksort_guard_and_call"] and
          b"T::small_sort(v, scratch, is_less);" in items["quicksort_guard_and_call"],
          "original generic guard/call missing")
    helper = items["helper_prefix"]
    for token in (b"if len < 2", b"scratch.len() < len + 16", b"intrinsics::abort()",
                  b"v.as_mut_ptr()", b"scratch.as_mut_ptr() as *mut T",
                  b"size_of::<T>() <= 16", b"len >= 16", b"else if len >= 8",
                  b"sort4_stable(v_base, scratch_base, is_less);"):
        _need(token in helper, f"helper prefix requirement missing: {token.decode(errors='replace')}")


def _freeze_marker_block(items: dict[str, bytes]) -> bytes:
    original = items["freeze_marker_import_and_block"]
    lines = original.splitlines(keepends=True)
    _need(len(lines) == 11, "FreezeMarker source span changed line count")
    block = b"".join(lines[5:])  # Original source lines 8..13, without crate-local import.
    _need(block.startswith(b"/// SAFETY:") and b"trait FreezeMarker" in block,
          "FreezeMarker block extraction mismatch")
    return block


def _threshold_mutation(items: dict[str, bytes], impl_name: str) -> tuple[dict[str, bytes], dict[str, Any]]:
    changed = dict(items)
    name, token = (("default_impl", b"SMALL_SORT_FALLBACK_THRESHOLD")
                   if impl_name == "default16" else
                   ("freeze_impl", b"SMALL_SORT_GENERAL_THRESHOLD"))
    original = items[name]
    _need(original.count(token) == 1, f"{impl_name} mutation token is not unique")
    changed[name] = original.replace(token, b"33", 1)
    mutation_id = "N-default-contract" if impl_name == "default16" else "N-freeze-contract"
    cert = {
        "mutation_id": mutation_id,
        "mutated_impl": impl_name,
        "original_item_sha256": _sha(original),
        "mutated_item_sha256": _sha(changed[name]),
        "mutation": f"replace {token.decode()} return expression with literal 33",
        "unchanged_other_impl_sha256": _sha(
            items["freeze_impl"] if impl_name == "default16" else items["default_impl"]),
        "original_source_pair_sha256": {
            "default_impl": _sha(items["default_impl"]),
            "freeze_impl": _sha(items["freeze_impl"]),
        },
        "mutated_source_pair_sha256": {
            "default_impl": _sha(changed["default_impl"]),
            "freeze_impl": _sha(changed["freeze_impl"]),
        },
        "intended_stage": "impl body post / common threshold conformance",
        "intended_predicate": "result<=32",
        "source_refusal_is_not_intended_negative": True,
    }
    return changed, cert


def _root_prefix(items: dict[str, bytes]) -> bytes:
    return b"""#![feature(freeze, min_specialization, rustc_attrs, core_intrinsics)]
#![allow(dead_code, unused_variables, unreachable_code)]
use std::marker::Freeze;
use std::intrinsics;
use std::mem::{size_of, MaybeUninit};
""" + _freeze_marker_block(items) + b"\n" + items["threshold_constants"] + b"\n" + \
        items["trait"] + b"\n" + items["default_impl"] + b"\n" + items["freeze_impl"] + b"\n"


def _helper_prefix_cut(helper: bytes) -> bytes:
    """Retain source guards/pointer setup, with labeled cuts before operations."""
    sort8 = helper.index(b"sort8_stable(")
    sort4 = helper.index(b"sort4_stable(")
    fallback = helper.index(b"} else {\n            ptr::copy_nonoverlapping", sort4)
    else_if = helper.index(b"} else if len >= 8 {", sort8, sort4)
    return (helper[:sort8] +
            b"// A1 CUT before first sort8_stable call.\n            return;\n" +
            helper[else_if:else_if + len(b"} else if len >= 8 {\n")] +
            b"    // A1 CUT before first sort4_stable call.\n            return;\n" +
            helper[fallback:fallback + len(b"} else {\n")] +
            b"    // A1 CUT before fallback pointer copy.\n            return;\n        };\n    }\n}\n")


def _diagnostic_cut_dependencies(helper_cut: bytes) -> bytes:
    return b"\n// A1 UNPROVED dependency; never target or consume as a summary.\n" + helper_cut + b"\n// A1 UNPROVED DIAGNOSTIC CUT. Never target or consume this body as a summary.\n" + b"""fn insertion_sort_shift_left<T, F: FnMut(&T, &T) -> bool>(
    _v: &mut [T], _offset: usize, _is_less: &mut F,
) { panic!("A1 unproved insertion cut") }
"""


def _observer(signature: bytes, guard: bytes, *, false31: bool = False) -> tuple[bytes, str]:
    _need(signature != b"" and b"FnMut(&T, &T) -> bool" in signature,
          "unrestricted source signature missing")
    guard = guard.replace(b"    loop {", b"    loop {", 1)
    _need(b"let len = v.len();" in guard and b"T::small_sort_threshold()" in guard,
          "source guard fragment mismatch")
    renamed = signature.replace(b"pub fn quicksort<", b"fn a1_guard_observer<", 1)
    _need(renamed != signature, "diagnostic observer rename did not match source")
    if false31:
        body = renamed + guard[:guard.index(b"            T::small_sort(v, scratch, is_less);")] + \
            OBSERVER_SUFFIX["N-false31"].encode()
    else:
        body = renamed + guard[:guard.index(b"            T::small_sort(v, scratch, is_less);")] + \
            OBSERVER_SUFFIX["P0c"].encode()
    return body, "quicksort -> a1_guard_observer (diagnostic item-name-only rename)"


def _p1_caller(signature: bytes, guard: bytes) -> bytes:
    _need(b"T::small_sort(v, scratch, is_less);" in guard, "P1 original small_sort call absent")
    return signature + guard + b"\n        // A1 diagnostic cut: non-base continuation after original call is absent.\n" \
        b"        return;\n    }\n}\n"


def _compose(items: dict[str, bytes], *, caller_kind: str, helper_cut: bytes,
             source_id: str, mutation: str | None = None) -> tuple[bytes, dict[str, Any]]:
    selected = dict(items)
    mutation_cert = None
    if mutation is not None:
        selected, mutation_cert = _threshold_mutation(items, mutation)
    prefix = _root_prefix(selected) + _diagnostic_cut_dependencies(helper_cut)
    observer, rename = _observer(selected["quicksort_signature"],
                                 selected["quicksort_guard_and_call"],
                                 false31=caller_kind == "N-false31")
    original_caller = _p1_caller(selected["quicksort_signature"],
                                 selected["quicksort_guard_and_call"])
    caller = observer + b"\n" + original_caller
    source = prefix + b"\n" + caller
    targets = {
        "P0a": ["default16.small_sort_threshold"],
        "P0b": ["freeze32.small_sort_threshold"],
        "P0c": ["a1_guard_observer"],
        "N-false31": ["a1_guard_observer"],
        "P1": [],
    }
    if mutation:
        target = "default16" if mutation == "default16" else "freeze32"
        targets[caller_kind] = [f"{target}.small_sort_threshold"]
    target_list = targets[caller_kind]
    info = {
        "case_id": mutation_cert["mutation_id"] if mutation_cert else caller_kind,
        "source_id": source_id,
        "unit_id": _sha(source + json.dumps(target_list, sort_keys=True).encode()),
        "source_pair_id": _sha(source),
        "generated_source_sha256": _sha(source),
        "caller_kind": caller_kind,
        "diagnostic_rename": rename,
        "actual_trait_item_call_retained": True,
        "threshold_trait_call_retained": caller_kind in ("P0c", "N-false31"),
        "common_summary_available": False,
        "common_summary_required_for_this_fixture": caller_kind == "P0c" and mutation is None,
        "helper_and_insertion_cuts": [
            {"name": "insertion_sort_shift_left", "verified": False, "summary_eligible": False},
            {"name": "small_sort_general_with_scratch", "verified": False,
             "summary_eligible": False},
        ],
        "verified_target_allowlist": target_list,
        "required_prior_threshold_summaries": (["default16.small_sort_threshold", "freeze32.small_sort_threshold"]
                                                if caller_kind == "P0c" and mutation is None else []),
        "P1_proof_credit": False,
        "common_contract_spec_injected": False,
        "compiler_impl_item_identity_bound": False,
        "executable_proof_ready": False,
        "mutation_certificate": mutation_cert,
    }
    return source, info


def construct(source_root: Path) -> dict[str, Any]:
    """Build in-memory source/cert records; caller controls Cloud-only writes."""
    _require_cloud_phase()
    _need(str(source_root.resolve()).startswith("/workspace/"),
          "source root must be a Cloud workspace path")
    sources = _read_sources(source_root)
    items, inventory = _items(sources)
    _assert_source_relations(items)
    helper = items["helper_full"]
    helper_cut = _helper_prefix_cut(helper)
    for token in (b"if len < 2", b"scratch.len() < len + 16", b"intrinsics::abort()",
                  b"v.as_mut_ptr()", b"len / 2", b"scratch.as_mut_ptr() as *mut T",
                  b"size_of::<T>() <= 16", b"len >= 16", b"else if len >= 8"):
        _need(token in helper_cut, f"helper prefix lost required source decision: {token!r}")
    _need(b"sort8_stable(" not in helper_cut and b"sort4_stable(" not in helper_cut and
          b"ptr::copy_nonoverlapping" not in helper_cut,
          "helper operation crossed an explicit diagnostic cut")
    inventory["helper_cut"] = {
        "file": SMALLSORT, "line_start": 220, "cut_before_line": 254,
        "prefix_sha256": _sha(helper_cut),
        "prefix_bytes_base64": base64.b64encode(helper_cut).decode("ascii"),
        "next_source_expression": "sort8_stable, then sort4_stable, then pointer-copy fallback",
        "explicit_labeled_cuts": ["before sort8 calls", "before first sort4 call", "before pointer-copy fallback"],
        "cut_is_diagnostic_only": True,
        "embedded_in_each_generated_rust_unit": True,
        "summary_eligible": False,
        "original_short_span_sha256": _sha(items["helper_prefix"]),
        "full_helper_span_sha256": _sha(helper),
    }
    source_id = _sha(json.dumps({"source_commit": SOURCE_COMMIT,
                                 "source_pins": SOURCE_PINS}, sort_keys=True).encode())

    cases = {}
    for name, caller in (("P0a", "P0a"), ("P0b", "P0b"), ("P0c", "P0c"),
                         ("P-dispatch", "P0c"), ("P1", "P1"), ("N-false31", "N-false31")):
        source, record = _compose(items, caller_kind=caller, helper_cut=helper_cut, source_id=source_id)
        record["case_id"] = name
        if name == "P-dispatch":
            record["verified_target_allowlist"] = []
            record["intended_stage"] = "translated trait-call AST and dispatch inspection"
            record["unit_id"] = _sha(source + b"P-dispatch:shape-only")
        cases[name] = {"source": source, "record": record}
    for name, impl in (("N-default-contract", "default16"),
                       ("N-freeze-contract", "freeze32")):
        source, record = _compose(items, caller_kind="P0c", helper_cut=helper_cut, source_id=source_id, mutation=impl)
        cases[name] = {"source": source, "record": record}

    # Keep exact source item bytes available to the runner as an inventory,
    # while preventing a cut fixture from claiming original full dependency proof.
    inventory["positive_source_sha256"] = cases["P0c"]["record"]["generated_source_sha256"]
    inventory["positive_unit_byte_identical_cases"] = ["P0a", "P0b", "P0c", "P-dispatch", "P1"]
    _need(len({cases[k]["record"]["generated_source_sha256"] for k in inventory["positive_unit_byte_identical_cases"]}) == 1,
          "positive cases must use byte-identical generated Rust source")
    inventory["call_graph"] = [
        {"from": "StableSmallSortTypeImpl::small_sort_threshold", "to": "default16.small_sort_threshold"},
        {"from": "StableSmallSortTypeImpl::small_sort_threshold", "to": "freeze32.small_sort_threshold"},
        {"from": "default16.small_sort", "to": "insertion_sort_shift_left", "verified": False},
        {"from": "freeze32.small_sort", "to": "small_sort_general_with_scratch", "verified": False},
        {"from": "small_sort_general_with_scratch", "to": "sort8_stable/sort4_stable", "verified": False},
        {"from": "quicksort guard", "to": "StableSmallSortTypeImpl::small_sort_threshold"},
        {"from": "quicksort base case", "to": "StableSmallSortTypeImpl::small_sort"},
    ]
    return {"source_inventory": inventory, "cases": cases}


def _require_cloud_phase() -> None:
    _need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build",
          "A1 fixture construction is Cloud Build only")
    _need(os.environ.get("SORT4_A1_PHASE_ID") == PHASE,
          "wrong or missing exact A1 phase id")
    _need(bool(os.environ.get("CLOUD_BUILD_ID")) and bool(os.environ.get("CLOUD_BUILD_PROJECT_ID")),
          "Cloud Build BUILD_ID/PROJECT_ID are required")


def _cloud_guard(output: Path) -> None:
    _require_cloud_phase()
    resolved = output.resolve()
    _need(str(resolved).startswith("/workspace/"), "output must be under /workspace")


def _write_package(package: dict[str, Any], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    certificate = {
        "schema": "a1-source-certified-fixtures-v1",
        "phase_id": PHASE,
        "source_inventory": package["source_inventory"],
        "cases": {},
        "proof_credit": False,
        "execution_performed": False,
    }
    (output / "helper-prefix.fragment").write_text(
        base64.b64decode(package["source_inventory"]["helper_cut"]["prefix_bytes_base64"])
        .decode("utf-8") + "\n// A1 CUT immediately before first sort4_stable call.\n")
    for case_id, case in package["cases"].items():
        path = output / f"{case_id}.rs"
        path.write_bytes(case["source"])
        certificate["cases"][case_id] = {
            **case["record"], "source_file": path.name,
            "target_id_is_part_of_unit_id": True,
            "mutation_certificate": case["record"]["mutation_certificate"],
        }
    (output / "source-certificate.json").write_text(
        json.dumps(certificate, sort_keys=True, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _cloud_guard(args.output)
    package = construct(args.source_root)
    _write_package(package, args.output)


if __name__ == "__main__":
    main()
