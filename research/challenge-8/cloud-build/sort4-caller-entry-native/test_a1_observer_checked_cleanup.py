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

CLEANUP = b"//@ a1_cleanup_option_ref(left_ancestor_pivot);"


class ObserverCleanupConstructionTests(unittest.TestCase):
    def test_checked_ghost_lemma_is_generic_and_consumes_both_option_variants(self):
        lemma = fixtures.OPTION_CLEANUP_LEMMA
        self.assertTrue(lemma.startswith(b"/*@\n"))
        self.assertTrue(lemma.endswith(b"@*/\n"))
        self.assertIn(b"lem a1_cleanup_option_ref<'a, T>", lemma)
        self.assertIn(b"std::option::Option_own::<&'a T>(t, value)", lemma)
        self.assertIn(b"thread_token(?t)", lemma)
        self.assertIn(b"ens thread_token(t);", lemma)
        self.assertIn(b"open std::option::Option_own::<&'a T>(t, value);", lemma)
        self.assertIn(b"std::option::Option::None => {}", lemma)
        self.assertIn(b"std::option::Option::Some(r) => {}", lemma)
        self.assertNotIn(b"'_", lemma)
        self.assertNotIn(b"assume", lemma)
        self.assertNotIn(b"axiom", lemma)
        self.assertNotIn(b"leak", lemma)
        self.assertNotIn(b"forget", lemma)
        self.assertNotIn(b"type_interp", lemma)

    def test_helper_gate_metadata_binds_exact_unique_source_and_body_lines(self):
        synthetic = b"header one\nheader two\n" + fixtures.OPTION_CLEANUP_LEMMA + b"tail\n"
        metadata = fixtures._checked_cleanup_helper_metadata(synthetic)
        lines = synthetic.splitlines(keepends=True)
        start = metadata["source_start_line"] - 1
        end = metadata["source_end_line"]
        self.assertEqual(b"".join(lines[start:end]), fixtures.OPTION_CLEANUP_LEMMA)
        self.assertEqual(metadata["source_sha256"], fixtures._sha(fixtures.OPTION_CLEANUP_LEMMA))
        self.assertEqual(metadata["name"], "a1_cleanup_option_ref")
        self.assertEqual(metadata["kind"], "lemma")
        self.assertEqual(lines[metadata["body_start_line"] - 1].strip(),
                         b"lem a1_cleanup_option_ref<'a, T>(value: std::option::Option<&'a T>)")
        self.assertEqual(lines[metadata["body_end_line"] - 1].strip(), b"}")
        self.assertEqual(lines[metadata["source_end_line"] - 1].strip(), b"@*/")

        with self.assertRaises(fixtures.FixtureError):
            fixtures._checked_cleanup_helper_metadata(synthetic + fixtures.OPTION_CLEANUP_LEMMA)
        with self.assertRaises(fixtures.FixtureError):
            fixtures._checked_cleanup_helper_metadata(synthetic.replace(
                b"Option::None", b"Option::Some", 1))

    def test_p0c_and_false31_keep_signature_and_guard_and_call_cleanup_each_exit(self):
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
                self.assertNotIn(b"core::mem::drop(left_ancestor_pivot)", generated)
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
        self.assertIn(b"A1 checked ghost cleanup", tail)
        self.assertEqual(tail.count(CLEANUP), 1)
        self.assertNotIn(b"core::mem::drop(left_ancestor_pivot)", tail)
        self.assertEqual(tail.count(b"return;"), 1)
        self.assertLess(tail.index(CLEANUP), tail.index(b"return;"))


if __name__ == "__main__":
    unittest.main()
