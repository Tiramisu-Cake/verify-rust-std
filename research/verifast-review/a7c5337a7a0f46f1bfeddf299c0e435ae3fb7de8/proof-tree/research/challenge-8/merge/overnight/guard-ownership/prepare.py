#!/usr/bin/env python3
"""Prepare annotation-only, exact-source CopyOnDrop payload-own diagnostics.

Preparation edits bytes only. Verification and compilation belong to the
authorized Cloud Build; this module must never invoke either locally.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "copy-on-drop-prepare.py"


def load_base():
    spec = importlib.util.spec_from_file_location("copy_on_drop_prepare_pinned", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError("pinned direct-Drop preparer unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


B = load_base()
PROFILE = "copy-on-drop-payload-own-diagnostic-v2"

# The by-value v is the exact three-field initializer used by generated FBC.
# The fraction is the existing source-read permission, while every T owner is
# supplied once. In particular, this definition cannot refer to guard `self`.
OWN = b"""/*@
pred<T> <CopyOnDrop<T>>.own(t, v;) =
    type_interp::<T>() &*&
    0 <= v.len &*& v.len <= usize::MAX &*&
    0 < std::mem::size_of::<T>() &*&
    std::mem::size_of::<T>() <= isize::MAX &*&
    v.len * std::mem::size_of::<T>() <= isize::MAX &*&
    0 < std::mem::size_of::<CopyOnDrop<T>>() &*&
    0 < std::mem::align_of::<CopyOnDrop<T>>() &*&
    v.src as usize != 0 &*& v.dst as usize != 0 &*&
    v.src as usize % std::mem::align_of::<T>() == 0 &*&
    v.dst as usize % std::mem::align_of::<T>() == 0 &*&
    object_pointer_within_limits(v.src, v.len * std::mem::size_of::<T>()) == true &*&
    object_pointer_within_limits(v.dst, v.len * std::mem::size_of::<T>()) == true &*&
    v.src as usize <= usize::MAX - v.len * std::mem::size_of::<T>() &*&
    v.dst as usize <= usize::MAX - v.len * std::mem::size_of::<T>() &*&
    pointer_within_limits(v.src) == true &*&
    pointer_within_limits(v.src + v.len) == true &*&
    pointer_within_limits(v.dst) == true &*&
    pointer_within_limits(v.dst + v.len) == true &*&
    (v.len == 0 ||
        v.src as usize + v.len * std::mem::size_of::<T>() <= v.dst as usize ||
        v.dst as usize + v.len * std::mem::size_of::<T>() <= v.src as usize) &*&
    [?f]v.src[..v.len] |-> ?src_values &*&
    v.dst[..v.len] |-> _ &*&
    foreach(src_values, own::<T>(t));
@*/

"""

PURE_ONLY = OWN.replace(
    b"    [?f]v.src[..v.len] |-> ?src_values &*&\n"
    b"    v.dst[..v.len] |-> _ &*&\n"
    b"    foreach(src_values, own::<T>(t));",
    b"    true;",
)
if PURE_ONLY == OWN:
    raise RuntimeError("missing-payload control failed to remove payload")

PROOF_FALSE = b"    assert false; // TARGET: payload-admitted prototype control\n"
BODY_FALSE = B.FALSE_LINE
OWN_INSERT = b"}\n\nimpl<T> Drop for CopyOnDrop<T> {"
SAFETY_OPEN = b"    open <CopyOnDrop<T>>.own(_t, *self);\n"
CONSTRUCTOR_LINE = b"        let drop_guard = CopyOnDrop { src: scratch_base, dst: v_base, len };"
CONSTRUCTOR = (b"fn source_guard_construction<T>(scratch_base: *const T, v_base: *mut T,\n"
               b"                                len: usize) -> CopyOnDrop<T> {\n"
               b"    {\n" + CONSTRUCTOR_LINE + b"\n"
               b"        drop_guard\n"
               b"    }\n"
               b"}\n")
PAYLOAD_BODY = OWN.split(b".own(t, v;) =\n", 1)[1].split(b";\n@*/", 1)[0]
CONSTRUCTOR_PAYLOAD = (PAYLOAD_BODY.replace(b"v.src", b"scratch_base")
                       .replace(b"v.dst", b"v_base")
                       .replace(b"v.len", b"len"))
CONSTRUCTOR_CONTRACT = (b"/*@\nreq thread_token(?t) &*& 2 <= len &*&\n" +
                        CONSTRUCTOR_PAYLOAD + b";\n@*//*@\n"
                        b"ens thread_token(t) &*&\n"
                        b"    <CopyOnDrop<T>>.own(t, result) &*&\n"
                        b"    2 <= result.len &*&\n"
                        b"    result.src == scratch_base &*&\n"
                        b"    result.dst == v_base &*& result.len == len;\n"
                        b"@*//*@ on_unwind_ens false; @*/")
CONSTRUCTOR_CLOSE = b"        //@ close <CopyOnDrop<T>>.own(t, drop_guard);\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def line_at(data: bytes, needle: bytes) -> int:
    if data.count(needle) != 1:
        raise ValueError(f"expected one target {needle!r}")
    return data[:data.index(needle)].count(b"\n") + 1


def extract(source: Path, output: Path, report_path: Path) -> dict:
    data = source.read_bytes()
    if sha(data) != B.SOURCE_SHA256 or B.git_blob(data) != B.SOURCE_GIT_BLOB:
        raise ValueError("exact SmallSort source identity changed")
    if data.count(B.BLOCK_START) != 1 or data.count(B.BLOCK_END) != 1:
        raise ValueError("CopyOnDrop anchors changed or ambiguous")
    start = data.index(B.BLOCK_START)
    end = data.index(B.BLOCK_END, start) + len(b"}\n\n")
    block = data[start:end]
    if len(block) != B.BLOCK_BYTES or sha(block) != B.BLOCK_SHA256:
        raise ValueError("exact actual guard/Drop body changed")
    original = B.CRATE_PREFIX + block
    if data.count(CONSTRUCTOR_LINE) != 1:
        raise ValueError("actual source construction statement changed or ambiguous")
    if original.count(OWN_INSERT) != 1 or original.count(B.DROP_SIGNATURE) != 1:
        raise ValueError("guard predicate or Drop contract insertion is ambiguous")
    if B.CONTRACT.count(SAFETY_OPEN) != 1:
        raise ValueError("pinned safety proof open changed")
    original_body_open = original.index(b"{", original.index(B.DROP_SIGNATURE))

    def make(own: bytes, proof_false: bool, body_false: bool) -> bytes:
        contract = B.CONTRACT.replace(SAFETY_OPEN, SAFETY_OPEN +
                                      (PROOF_FALSE if proof_false else b""), 1)
        verified = original.replace(OWN_INSERT,
                                    b"}\n\n" + own + b"impl<T> Drop for CopyOnDrop<T> {", 1)
        verified = verified.replace(B.DROP_SIGNATURE, B.DROP_SIGNATURE + contract, 1)
        if body_false:
            offset = original_body_open + len(own) + len(contract)
            if verified[offset] != ord("{"):
                raise ValueError("actual Drop body offset changed")
            newline = verified.index(b"\n", offset) + 1
            verified = verified[:newline] + BODY_FALSE + verified[newline:]
        stripped = verified.replace(own, b"", 1).replace(contract, b"", 1)
        if body_false:
            stripped = stripped.replace(BODY_FALSE, b"", 1)
        if stripped != original:
            raise ValueError("verified case changes runtime source")
        if verified.count(B.COPY_CALL) != 1:
            raise ValueError("actual dynamic full-length copy is absent")
        return verified

    configs = {
        "positive": (OWN, False, False),
        "prototype_false": (OWN, True, False),
        "first_body_false": (OWN, False, True),
        "missing_payload": (PURE_ONLY, False, False),
    }
    if output.exists() or report_path.exists():
        raise FileExistsError("refusing to reuse guard evidence paths")
    rows = {}
    for name, (own, proof_false, body_false) in configs.items():
        verified = make(own, proof_false, body_false)
        case = output / name
        (case / "original").mkdir(parents=True)
        (case / "verified").mkdir()
        (case / "original/lib.rs").write_bytes(original)
        (case / "verified/lib.rs").write_bytes(verified)
        row = {
            "original_sha256": sha(original),
            "verified_sha256": sha(verified),
            "custom_own_sha256": sha(own),
            "direct_contract_sha256": sha(B.CONTRACT),
            "runtime_source_identical_after_ghost_strip": True,
            "copy_call_line": line_at(verified, B.COPY_CALL),
            "actual_copy_call_line": line_at(verified, B.COPY_CALL),
            "expected_actual_target": B.TARGET,
            "expected_own_nonfalse": own == OWN,
        }
        if proof_false:
            false_column_start = PROOF_FALSE.index(b"false") + 1
            row["intended_failure"] = {
                "stage": "verifast_prototype",
                "line": line_at(verified, PROOF_FALSE),
                "predicate": "false",
                "column_start": false_column_start,
                "column_end": false_column_start + len(b"false"),
            }
        if body_false:
            false_line = line_at(verified, BODY_FALSE)
            false_column_start = BODY_FALSE.index(b"false") + 1
            row["intended_failure"] = {
                "stage": "verifast_actual_body",
                "line": false_line,
                "predicate": "false",
            }
            row["negative_target_line"] = false_line
            row["negative_column_start"] = false_column_start
            row["negative_column_end"] = false_column_start + len(b"false")
            row["negative_predicate"] = "false"
        if name == "missing_payload":
            row["intended_failure"] = {
                "stage": "verifast_prototype",
                "predicate": "source/destination/foreach resource absent",
                "location": "prototype entailment of unchanged direct Drop req",
                "source_requirement_line": line_at(verified,
                    b"    [?f]src[..len] |-> ?src_values &*&"),
            }
        rows[name] = row
    # A separate conditional witness copies one physical runtime statement
    # exactly from smallsort.rs:279. Its inputs are supplied resources, not a
    # claim that the whole caller has established them. Both extracted source
    # variants retain the original actual Drop body and custom non-False own.
    constructor_original = original + b"\n" + CONSTRUCTOR
    constructor_verified = make(OWN, False, False) + b"\n"
    constructor_verified += CONSTRUCTOR.replace(
        b" -> CopyOnDrop<T> {", b" -> CopyOnDrop<T>" + CONSTRUCTOR_CONTRACT + b" {", 1)
    constructor_verified = constructor_verified.replace(
        CONSTRUCTOR_LINE + b"\n",
        CONSTRUCTOR_LINE + b"\n" + CONSTRUCTOR_CLOSE, 1)
    stripped_constructor = (constructor_verified.replace(OWN, b"", 1)
                            .replace(B.CONTRACT, b"", 1)
                            .replace(CONSTRUCTOR_CONTRACT, b"", 1)
                            .replace(CONSTRUCTOR_CLOSE, b"", 1))
    if (stripped_constructor != constructor_original or
            constructor_original.count(CONSTRUCTOR_LINE) != 1 or
            constructor_verified.count(CONSTRUCTOR_LINE) != 1):
        raise ValueError("constructor witness changed non-ghost runtime source")
    case = output / "constructor"
    (case / "original").mkdir(parents=True)
    (case / "verified").mkdir()
    (case / "original/lib.rs").write_bytes(constructor_original)
    (case / "verified/lib.rs").write_bytes(constructor_verified)
    rows["constructor"] = {
        "original_sha256": sha(constructor_original),
        "verified_sha256": sha(constructor_verified),
        "custom_own_sha256": sha(OWN),
        "direct_contract_sha256": sha(B.CONTRACT),
        "constructor_contract_sha256": sha(CONSTRUCTOR_CONTRACT),
        "source_constructor_line_sha256": sha(CONSTRUCTOR_LINE),
        "source_constructor_line": data[:data.index(CONSTRUCTOR_LINE)].count(b"\n") + 1,
        "witness_constructor_line": line_at(constructor_verified, CONSTRUCTOR_LINE),
        "runtime_source_identical_after_ghost_strip": True,
        "copy_call_line": line_at(constructor_verified, B.COPY_CALL),
        "actual_copy_call_line": line_at(constructor_verified, B.COPY_CALL),
        "expected_actual_target": B.TARGET,
        "expected_own_nonfalse": True,
        "conditional_supplied_payload": True,
        "scope": "only exact source construction statement under separately supplied payload",
    }
    report = {
        "profile": PROFILE,
        "source_sha256": sha(data),
        "source_git_blob": B.SOURCE_GIT_BLOB,
        "source_block_sha256": sha(block),
        "original_extraction_sha256": sha(original),
        "direct_contract_sha256": sha(B.CONTRACT),
        "custom_own_sha256": sha(OWN),
        "scope": "nonvacuous guard own to exact actual Drop prototype/direct body only",
        "accepted": False,
        "cases": rows,
    }
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
        raise SystemExit(f"payload-own source preparation refused: {error}")
