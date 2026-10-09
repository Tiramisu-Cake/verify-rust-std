#!/usr/bin/env python3
"""Prepare the V3 nonprecise-own source guard constructor fragment."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
V2_PATH = HERE.parent / "prepare.py"
spec = importlib.util.spec_from_file_location("guard_constructor_v2_prep", V2_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("V2 guard constructor preparer unavailable")
V2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V2)
P = V2.P
B = V2.B
PROFILE = "copy-on-drop-source-construction-full-source-nonprecise-current-fragment-v3b"

# V2's source permission and owner payload are retained byte-for-byte; only
# dropping the semicolon changes the pinned predicate precision annotation.
OWN = V2.OWN.replace(b".own(t, v;) =", b".own(t, v) =", 1)
CONSTRUCTOR_CONTRACT = V2.CONSTRUCTOR_CONTRACT
if (OWN == V2.OWN or OWN.count(b".own(t, v) =") != 1 or
        OWN.split(b".own(t, v) =\n", 1)[1] !=
        V2.OWN.split(b".own(t, v;) =\n", 1)[1]):
    raise RuntimeError("V3 must retain the exact V2 payload with nonprecise own")

CONSTRUCTOR_FALSE = b"        //@ assert false; // TARGET: first constructor-body control\n"
STRUCT_END = b"}\n\nimpl<T> Drop for CopyOnDrop<T> {"
CONSTRUCTOR_RUNTIME = P.CONSTRUCTOR.replace(
    b"fn source_guard_construction", b"unsafe fn source_guard_construction", 1)
if CONSTRUCTOR_RUNTIME == P.CONSTRUCTOR:
    raise RuntimeError("constructor witness function anchor changed")

ROUNDTRIP = (
    b"        //@ close <CopyOnDrop<T>>.own(t, drop_guard);\n"
    b"        //@ open <CopyOnDrop<T>>.own(t, drop_guard);\n"
    b"        //@ assert scratch_base[..len] |-> ?current_src_values &*& v_base[..len] |-> _ &*& foreach(current_src_values, own::<T>(t));\n"
    b"        //@ close <CopyOnDrop<T>>.own(t, drop_guard);\n")


def sha(data: bytes) -> str:
    return P.sha(data)


def line_at(data: bytes, needle: bytes) -> int:
    if data.count(needle) != 1:
        raise ValueError(f"expected one target {needle!r}")
    return data[:data.index(needle)].count(b"\n") + 1


def extract(source: Path, output: Path, report_path: Path) -> dict:
    data = source.read_bytes()
    if sha(data) != B.SOURCE_SHA256 or B.git_blob(data) != B.SOURCE_GIT_BLOB:
        raise ValueError("exact SmallSort source identity changed")
    if data.count(B.BLOCK_START) != 1 or data.count(B.BLOCK_END) != 1 or \
            data.count(P.CONSTRUCTOR_LINE) != 1:
        raise ValueError("struct, Drop, or constructor source anchor ambiguous")
    start = data.index(B.BLOCK_START)
    end = data.index(B.BLOCK_END, start) + len(b"}\n\n")
    entire_block = data[start:end]
    if len(entire_block) != B.BLOCK_BYTES or sha(entire_block) != B.BLOCK_SHA256:
        raise ValueError("actual source guard/Drop block changed")
    if entire_block.count(STRUCT_END) != 1:
        raise ValueError("struct/Drop boundary changed")
    struct_bytes = entire_block.split(STRUCT_END, 1)[0] + b"}\n\n"
    if struct_bytes.count(b"struct CopyOnDrop<T> {") != 1 or \
            b"impl<T> Drop" in struct_bytes:
        raise ValueError("isolated fragment does not contain exactly the private struct")
    source_line = data[:data.index(P.CONSTRUCTOR_LINE)].count(b"\n") + 1
    if source_line != 279:
        raise ValueError("physical constructor statement moved")
    original = B.CRATE_PREFIX + struct_bytes + CONSTRUCTOR_RUNTIME
    signature = b" -> CopyOnDrop<T> {"
    if original.count(signature) != 1 or original.count(P.CONSTRUCTOR_LINE) != 1:
        raise ValueError("constructor fragment runtime shape changed")
    common = original.replace(b"\nunsafe fn source_guard_construction",
                              b"\n" + OWN + b"unsafe fn source_guard_construction", 1)
    common = common.replace(signature,
                            b" -> CopyOnDrop<T>" + CONSTRUCTOR_CONTRACT + b" {", 1)
    marker = P.CONSTRUCTOR_LINE + b"\n"
    if common.count(marker) != 1:
        raise ValueError("constructor body statement is not unique")
    if output.exists() or report_path.exists():
        raise FileExistsError("refusing to reuse construction evidence paths")
    rows = {}
    for name, false_line in (("positive", b""),
                             ("first_body_false", CONSTRUCTOR_FALSE)):
        verified = common.replace(marker, marker + ROUNDTRIP + false_line, 1)
        stripped = (verified.replace(OWN, b"", 1)
                    .replace(CONSTRUCTOR_CONTRACT, b"", 1)
                    .replace(ROUNDTRIP, b"", 1))
        if false_line:
            stripped = stripped.replace(false_line, b"", 1)
        if stripped != original:
            raise ValueError(f"{name}: ghost stripping changed runtime fragment")
        case = output / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        row = {"original_sha256": sha(original),
               "verified_sha256": sha(verified),
               "source_statement_line": source_line,
               "source_statement_sha256": sha(P.CONSTRUCTOR_LINE),
               "verified_statement_line": line_at(verified, P.CONSTRUCTOR_LINE),
               "runtime_source_identical_after_ghost_strip": True}
        if false_line:
            column = false_line.index(b"false") + 1
            row["intended_failure"] = {
                "stage": "verifast_runtime_constructor",
                "line": line_at(verified, false_line),
                "column_start": column, "column_end": column + len(b"false"),
                "predicate": "false"}
        rows[name] = row
    report = {"profile": PROFILE,
              "source_sha256": sha(data),
              "source_git_blob": B.SOURCE_GIT_BLOB,
              "complete_guard_drop_block_sha256": sha(entire_block),
              "isolated_struct_sha256": sha(struct_bytes),
              "exact_own_sha256": sha(OWN),
              "constructor_contract_sha256": sha(CONSTRUCTOR_CONTRACT),
              "v2_full_source_own_sha256": sha(V2.OWN),
              "own_payload_body_matches_v2": True,
              "nonprecise_own": True,
              "full_source_permission_only": True,
              "roundtrip_sha256": sha(ROUNDTRIP),
              "source_constructor_line": source_line,
              "source_constructor_sha256": sha(P.CONSTRUCTOR_LINE),
              "no_drop_impl_in_fragment": True,
              "unsafe_wrapper_for_conditional_explicit_contract": True,
              "accepted": False, "cases": rows}
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
        raise SystemExit(f"V3 constructor fragment preparation refused: {error}")
