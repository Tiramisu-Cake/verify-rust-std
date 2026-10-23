#!/usr/bin/env python3
"""Static source-contract checks for the R23 array/slice predicate-expression fix."""
from __future__ import annotations

from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "r20-array-slice-content.rs"


def check(source: str) -> None:
    required = (
        "pred_ctor r20_u64_array3_content(t: thread_id_t, p: *u64)() =\n"
        "    array::<u64>(p, 3, ?current) &*& foreach(current, own::<u64>(t));",
        "strip_pointer_metadata(s as pointer) as *u64 == p &*& s.len() == 3;",
        "ens <[u64]>.full_borrow_content(t, s)();",
        "req <[u64]>.full_borrow_content(t, s)() &*&",
        "req full_borrow(k, r20_u64_array3_content(t, p)) &*&",
        "ens full_borrow(k, <[u64]>.full_borrow_content(t, s));",
        "req full_borrow(k, <[u64]>.full_borrow_content(t, s)) &*&",
        "ens full_borrow(k, r20_u64_array3_content(t, p));",
        "full_borrow_implies(k, r20_u64_array3_content(t, p), <[u64]>.full_borrow_content(t, s));",
        "full_borrow_implies(k, <[u64]>.full_borrow_content(t, s), r20_u64_array3_content(t, p));",
        "r20_array3_content_to_slice(t, p, s);",
        "r20_slice_content_to_array3(t, p, s);",
    )
    for text in required:
        if text not in source:
            raise AssertionError(f"required source contract missing: {text}")
    if source.count("s.len() == 3") != 4:
        raise AssertionError("all array/slice conversion and borrow contracts must retain length 3")
    if source.count("strip_pointer_metadata(s as pointer) as *u64 == p") != 4:
        raise AssertionError("all array/slice conversions must retain the exact pointer-metadata relation")
    if source.count("produce_lem_ptr_chunk implies(") != 4:
        raise AssertionError("both implication directions must remain in both full-borrow lemmas")
    direct_constructor_lines = [line.strip() for line in source.splitlines()
                                if "slice_full_borrow_content::<u64>" in line]
    if (sum(line.startswith("open ") for line in direct_constructor_lines) != 1 or
            sum(line.startswith("close ") for line in direct_constructor_lines) != 1):
        raise AssertionError("direct slice constructor must retain its checked open/close")
    for line in direct_constructor_lines:
        if not (line.startswith("open ") or line.startswith("close ")):
            raise AssertionError("direct slice constructor must remain only in its checked open/close")
    if source.count("<[u64]>.full_borrow_content(t, s)") != 10:
        raise AssertionError("all first-class slice content expressions must use the typed type-predicate definition")
    if source.count("<[u64]>.full_borrow_content(t, s)()") != 2:
        raise AssertionError("top-level typed predicate assertions must apply the predicate value")
    if ("full_borrow(k, <[u64]>.full_borrow_content(t, s)())" in source or
            "implies(r20_u64_array3_content(t, p), <[u64]>.full_borrow_content(t, s)())" in source):
        raise AssertionError("full_borrow and implies take the predicate value without top-level application")
    if "assume" in source.lower() or "admit" in source.lower():
        raise AssertionError("helper must not add trusted assumptions")


class ArraySliceContentServiceTests(unittest.TestCase):
    def test_typed_predicate_contracts_preserve_resources_and_both_directions(self):
        check(SOURCE.read_text())

    def test_generic_constructor_cannot_reappear_in_first_class_borrow_position(self):
        current = SOURCE.read_text()
        broken = current.replace(
            "ens full_borrow(k, <[u64]>.full_borrow_content(t, s));",
            "ens full_borrow(k, slice_full_borrow_content::<u64>(t, s));", 1)
        self.assertNotEqual(current, broken)
        with self.assertRaises(AssertionError):
            check(broken)

    def test_pointer_or_length_constraints_cannot_be_dropped(self):
        current = SOURCE.read_text()
        broken = current.replace("s.len() == 3", "s.len() == 2", 1)
        self.assertNotEqual(current, broken)
        with self.assertRaises(AssertionError):
            check(broken)


if __name__ == "__main__":
    unittest.main()
