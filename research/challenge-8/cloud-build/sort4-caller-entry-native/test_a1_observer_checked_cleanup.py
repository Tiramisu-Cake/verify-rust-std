#!/usr/bin/env python3
"""Isolated source-construction checks for the P0c Copy cleanup hypothesis."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("a1_fixtures_cleanup", HERE / "a1-fixtures.py")
assert SPEC is not None and SPEC.loader is not None
fixtures = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixtures)


SIGNATURE = b"""pub fn quicksort<T, F: FnMut(&T, &T) -> bool>(
    mut v: &mut [T],
    scratch: &mut [MaybeUninit<T>],
    mut limit: u32,
    mut left_ancestor_pivot: Option<&T>,
    is_less: &mut F,
) {
"""

GUARD = b"""    loop {
        let len = v.len();
        if len <= T::small_sort_threshold() {
            T::small_sort(v, scratch, is_less);
        }
        // Synthetic source boundary before the original small_sort call.
        T::small_sort(v, scratch, is_less);
    }
"""

CLEANUP = b"core::mem::drop(left_ancestor_pivot);"


class ObserverCleanupConstructionTests(unittest.TestCase):
    def test_p0c_and_false31_keep_signature_and_guard_and_cleanup_each_exit(self):
        for false31, expected_assertion in ((False, b"assert len <= 32;"),
                                             (True, b"assert len <= 31;")):
            with self.subTest(false31=false31):
                generated, _ = fixtures._observer(SIGNATURE, GUARD, false31=false31)
                renamed = SIGNATURE.replace(b"pub fn quicksort<",
                                            b"fn a1_guard_observer<", 1)
                source_prefix = GUARD[:GUARD.index(
                    b"            T::small_sort(v, scratch, is_less);")]
                self.assertTrue(generated.startswith(renamed + source_prefix))
                self.assertIn(expected_assertion, generated)
                self.assertEqual(generated.count(CLEANUP), 2)
                self.assertEqual(generated.count(b"return;"), 2)
                first_cleanup = generated.index(CLEANUP)
                self.assertLess(generated.index(b"T::small_sort_threshold()"),
                                generated.index(expected_assertion))
                self.assertLess(generated.index(b"assert requirement <= 48;"),
                                first_cleanup)
                self.assertEqual(generated.count(CLEANUP + b"\n        return;"), 1)
                self.assertEqual(generated.count(CLEANUP + b"\n    return;"), 1)
                self.assertNotIn(b"left_ancestor_pivot = None", generated)

    def test_p1_original_prefix_unchanged_and_cleanup_is_labeled_diagnostic_tail(self):
        generated = fixtures._p1_caller(SIGNATURE, GUARD)
        prefix = SIGNATURE + GUARD
        self.assertTrue(generated.startswith(prefix))
        tail = generated[len(prefix):]
        self.assertIn(b"A1 diagnostic cut: non-base continuation", tail)
        self.assertIn(b"A1 diagnostic cleanup hypothesis", tail)
        self.assertEqual(tail.count(CLEANUP), 1)
        self.assertEqual(tail.count(b"return;"), 1)
        self.assertLess(tail.index(CLEANUP), tail.index(b"return;"))


if __name__ == "__main__":
    unittest.main()
