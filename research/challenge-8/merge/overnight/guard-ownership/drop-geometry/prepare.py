#!/usr/bin/env python3
"""Prepare exact-source canonical FBC to actual Drop geometry diagnostics.

This is byte preparation only. The hosted proof runner owns all executable work.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"pinned preparation unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


V3 = load("geometry_constructor_v3", HERE.parent / "construction/nonprecise-v3/prepare.py")
P = V3.P
B = V3.B
PROFILE = "copy-on-drop-canonical-fbc-self-geometry-diagnostic-v3"
OWN = V3.OWN
PROTOTYPE_FALSE = b"    assert false; // TARGET: canonical prototype entry\n"
BODY_FALSE = B.FALSE_LINE
SAFETY_OPEN = P.SAFETY_OPEN
FIELD_BINDING = (
    b"    assert (*self).src |-> ?guard_src &*& (*self).dst |-> ?guard_dst &*& "
    b"(*self).len |-> ?guard_len;\n")
GEOMETRY = (
    b"    assert (self as *mut CopyOnDrop<T>) as usize != 0;\n",
    b"    assert (self as *mut CopyOnDrop<T>) as usize % std::mem::align_of::<CopyOnDrop<T>>() == 0;\n",
    b"    assert object_pointer_within_limits(self as *mut CopyOnDrop<T>, std::mem::size_of::<CopyOnDrop<T>>()) == true;\n",
    b"    assert (self as *mut CopyOnDrop<T>) as usize <= usize::MAX - std::mem::size_of::<CopyOnDrop<T>>();\n",
    b"    assert (guard_len == 0 || (self as *mut CopyOnDrop<T>) as usize + std::mem::size_of::<CopyOnDrop<T>>() <= guard_src as usize || guard_src as usize + guard_len * std::mem::size_of::<T>() <= (self as *mut CopyOnDrop<T>) as usize);\n",
    b"    assert (guard_len == 0 || (self as *mut CopyOnDrop<T>) as usize + std::mem::size_of::<CopyOnDrop<T>>() <= guard_dst as usize || guard_dst as usize + guard_len * std::mem::size_of::<T>() <= (self as *mut CopyOnDrop<T>) as usize);\n",
)
GEOMETRY_NAMES = ("self_nonnull", "self_alignment", "self_object_limits",
                  "self_address_no_overflow", "self_source_disjoint",
                  "self_destination_disjoint")


def line_at(data: bytes, needle: bytes) -> int:
    if data.count(needle) != 1:
        raise ValueError(f"source annotation must occur once: {needle!r}")
    return data[:data.index(needle)].count(b"\n") + 1


def extract(source: Path, output: Path, report_path: Path) -> dict:
    data = source.read_bytes()
    if P.sha(data) != B.SOURCE_SHA256 or B.git_blob(data) != B.SOURCE_GIT_BLOB:
        raise ValueError("exact SmallSort source identity changed")
    if data.count(B.BLOCK_START) != 1 or data.count(B.BLOCK_END) != 1:
        raise ValueError("exact guard/Drop anchors changed")
    start = data.index(B.BLOCK_START)
    end = data.index(B.BLOCK_END, start) + len(b"}\n\n")
    block = data[start:end]
    if len(block) != B.BLOCK_BYTES or P.sha(block) != B.BLOCK_SHA256:
        raise ValueError("actual guard/Drop source block changed")
    original = B.CRATE_PREFIX + block
    if (original.count(P.OWN_INSERT) != 1 or
            original.count(B.DROP_SIGNATURE) != 1 or
            original.count(B.COPY_CALL) != 1 or
            B.CONTRACT.count(SAFETY_OPEN) != 1 or
            b"safety_proof {\n" not in B.CONTRACT or
            OWN != V3.OWN):
        raise ValueError("guard/source/contract insertion anchors changed")
    if output.exists() or report_path.exists():
        raise FileExistsError("refusing to reuse geometry evidence paths")
    body_open = original.index(b"{", original.index(B.DROP_SIGNATURE))
    rows = {}
    for name in ("positive", "prototype_false", "first_body_false"):
        inserted = ((PROTOTYPE_FALSE if name == "prototype_false" else b"") +
                    FIELD_BINDING + b"".join(GEOMETRY))
        contract = B.CONTRACT.replace(SAFETY_OPEN, SAFETY_OPEN + inserted, 1)
        if contract == B.CONTRACT or contract.split(b"safety_proof {\n", 1)[0] != \
                B.CONTRACT.split(b"safety_proof {\n", 1)[0]:
            raise ValueError("direct Drop req/ens/unwind was changed")
        verified = original.replace(P.OWN_INSERT,
                                    b"}\n\n" + OWN + b"impl<T> Drop for CopyOnDrop<T> {", 1)
        verified = verified.replace(B.DROP_SIGNATURE, B.DROP_SIGNATURE + contract, 1)
        if name == "first_body_false":
            open_offset = body_open + len(OWN) + len(contract)
            if verified[open_offset] != ord("{"):
                raise ValueError("actual Drop body offset changed")
            newline = verified.index(b"\n", open_offset) + 1
            verified = verified[:newline] + BODY_FALSE + verified[newline:]
        stripped = verified.replace(OWN, b"", 1).replace(contract, b"", 1)
        if name == "first_body_false":
            stripped = stripped.replace(BODY_FALSE, b"", 1)
        if stripped != original or verified.count(B.COPY_CALL) != 1:
            raise ValueError(f"{name}: runtime source or full-count copy changed")
        case = output / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        row = {"original_sha256": P.sha(original),
               "verified_sha256": P.sha(verified),
               "custom_own_sha256": P.sha(OWN),
               "direct_original_contract_sha256": P.sha(B.CONTRACT),
               "direct_asserted_contract_sha256": P.sha(contract),
               "direct_req_ens_unwind_sha256": P.sha(B.CONTRACT.split(b"safety_proof {\n", 1)[0]),
               "runtime_source_identical_after_ghost_strip": True,
               "copy_call_line": line_at(verified, B.COPY_CALL),
               "actual_copy_call_line": line_at(verified, B.COPY_CALL),
               "geometry_assertions": [
                   {"label": label, "line": line_at(verified, assertion),
                    "column_start": assertion.index(b"assert") + 1,
                    "column_end": assertion.index(b"assert") + 1 + len(b"assert"),
                    "assertion_sha256": P.sha(assertion)}
                   for label, assertion in zip(GEOMETRY_NAMES, GEOMETRY)],
               "field_binding_line": line_at(verified, FIELD_BINDING),
               "expected_actual_target": B.TARGET}
        if name == "prototype_false":
            col = PROTOTYPE_FALSE.index(b"false") + 1
            row["intended_failure"] = {
                "stage": "verifast_canonical_prototype", "predicate": "false",
                "line": line_at(verified, PROTOTYPE_FALSE),
                "column_start": col, "column_end": col + len(b"false")}
        if name == "first_body_false":
            col = BODY_FALSE.index(b"false") + 1
            row["negative_target_line"] = line_at(verified, BODY_FALSE)
            row["negative_column_start"] = col
            row["negative_column_end"] = col + len(b"false")
            row["negative_predicate"] = "false"
        rows[name] = row
    report = {"profile": PROFILE, "source_sha256": P.sha(data),
              "source_git_blob": B.SOURCE_GIT_BLOB,
              "source_block_sha256": P.sha(block),
              "original_extraction_sha256": P.sha(original),
              "direct_original_contract_sha256": P.sha(B.CONTRACT),
              "direct_req_ens_unwind_sha256": P.sha(B.CONTRACT.split(b"safety_proof {\n", 1)[0]),
              "custom_own_sha256": P.sha(OWN),
              "v3_full_source_own_sha256": P.sha(V3.OWN),
              "nonprecise_own": True, "accepted": False,
              "actual_drop_compatibility": "OPEN", "cases": rows}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    extract(args.source, args.output, args.report)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"geometry preparation refused: {error}")
