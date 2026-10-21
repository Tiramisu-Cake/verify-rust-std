#!/usr/bin/env python3
"""Isolated source-construction checks for the P0c Copy cleanup hypothesis."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("a1_fixtures_cleanup", HERE / "a1-fixtures.py")
assert SPEC is not None and SPEC.loader is not None
fixtures = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixtures)
GHOST_SPEC = importlib.util.spec_from_file_location(
    "a1_observer_cleanup_ghost_strip",
    HERE.parent / "sort4-native-c1-bound" / "ghost-strip.py")
assert GHOST_SPEC is not None and GHOST_SPEC.loader is not None
ghost = importlib.util.module_from_spec(GHOST_SPEC)
sys.modules[GHOST_SPEC.name] = ghost
GHOST_SPEC.loader.exec_module(ghost)


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
        self.assertNotIn(b"use std::option", lemma)
        self.assertTrue(lemma.startswith(b"/*@\n"))
        self.assertTrue(lemma.endswith(b"@*/\n"))
        self.assertIn(b"lem a1_cleanup_option_ref<'a, T>", lemma)
        self.assertIn(b"std::option::Option_own::<&'a T>(t, value)", lemma)
        self.assertIn(b"thread_token(?t)", lemma)
        self.assertIn(b"ens thread_token(t);", lemma)
        self.assertIn(b"open std::option::Option_own::<&'a T>(t, value);", lemma)
        self.assertIn(b"Option::None => {}", lemma)
        self.assertIn(b"Option::Some(r) => { open shared_ref_type_own::<'a, T>()(t, r); }", lemma)
        self.assertNotIn(b"Option::Some(r) => {}", lemma)
        self.assertNotIn(b"std::option::Option::None", lemma)
        self.assertNotIn(b"std::option::Option::Some", lemma)
        self.assertNotIn(b"'_", lemma)
        self.assertNotIn(b"assume", lemma)
        self.assertNotIn(b"axiom", lemma)
        self.assertNotIn(b"leak", lemma)
        self.assertNotIn(b"forget", lemma)
        self.assertNotIn(b"type_interp", lemma)

    def test_helper_gate_metadata_binds_exact_unique_source_and_body_lines(self):
        synthetic = (b"header one\nheader two\n" + fixtures.OPTION_CLEANUP_IMPORT +
                     fixtures.OPTION_CLEANUP_LEMMA + b"tail\n")
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
        self.assertEqual(lines[metadata["source_start_line"] - 2],
                         fixtures.OPTION_CLEANUP_IMPORT)
        self.assertNotEqual(metadata["source_sha256"],
                            fixtures._sha(fixtures.OPTION_CLEANUP_IMPORT +
                                          fixtures.OPTION_CLEANUP_LEMMA))

        with self.assertRaises(fixtures.FixtureError):
            fixtures._checked_cleanup_helper_metadata(synthetic + fixtures.OPTION_CLEANUP_LEMMA)
        with self.assertRaises(fixtures.FixtureError):
            fixtures._checked_cleanup_helper_metadata(
                b"header\n" + fixtures.OPTION_CLEANUP_LEMMA)
        with self.assertRaises(fixtures.FixtureError):
            fixtures._checked_cleanup_helper_metadata(synthetic.replace(
                b"Option::None => {}", b"Option::Some => {}", 1))

    def test_import_and_both_constructor_patterns_are_separate_closed_source_forms(self):
        import_line = fixtures.OPTION_CLEANUP_IMPORT
        lemma = fixtures.OPTION_CLEANUP_LEMMA
        self.assertEqual(import_line, b"//@ use std::option::{Option, Option::None, Option::Some};\n")
        self.assertEqual(lemma.count(b"/*@"), 1)
        self.assertEqual(lemma.count(b"@*/"), 1)
        self.assertNotIn(b"use ", lemma)
        self.assertEqual(lemma.count(b"Option::None => {}"), 1)
        self.assertEqual(lemma.count(
            b"Option::Some(r) => { open shared_ref_type_own::<'a, T>()(t, r); }"), 1)
        self.assertNotIn(b"Option::Some(r) => {}", lemma)
        self.assertNotIn(b"std::option::Option::None", lemma)
        self.assertNotIn(b"std::option::Option::Some", lemma)
        self.assertEqual((import_line + lemma).count(
            b"use std::option::{Option, Option::None, Option::Some};"), 1)

    def test_metadata_rejects_combined_batch_nonadjacent_or_duplicate_import(self):
        helper = fixtures.OPTION_CLEANUP_LEMMA
        standalone = fixtures.OPTION_CLEANUP_IMPORT
        with self.assertRaises(fixtures.FixtureError):
            fixtures._checked_cleanup_helper_metadata(
                b"header\n" + helper.replace(b"/*@\n", b"/*@\n" + standalone, 1))
        with self.assertRaises(fixtures.FixtureError):
            fixtures._checked_cleanup_helper_metadata(
                b"header\n" + standalone + b"\n" + helper)
        with self.assertRaises(fixtures.FixtureError):
            fixtures._checked_cleanup_helper_metadata(
                b"header\n" + standalone + standalone + helper)

    def test_p0c_and_false31_cleanup_once_at_entry_before_runtime_calls(self):
        for false31, expected_assertion in ((False, b"assert len <= 32;"),
                                             (True, b"assert len <= 31;")):
            with self.subTest(false31=false31):
                generated, _ = fixtures._observer(SIGNATURE, GUARD, false31=false31)
                renamed = SIGNATURE.replace(b"pub fn quicksort<",
                                            b"fn a1_guard_observer<", 1)
                entry = b"        //@ a1_cleanup_option_ref(left_ancestor_pivot);\n"
                source_prefix = GUARD[:GUARD.index(
                    b"            T::small_sort(v, scratch, is_less);")]
                self.assertTrue(generated.startswith(renamed + entry + source_prefix))
                self.assertIn(expected_assertion, generated)
                self.assertEqual(generated.count(CLEANUP), 1)
                self.assertEqual(generated.count(b"return;"), 2)
                self.assertNotIn(b"core::mem::drop(left_ancestor_pivot)", generated)
                cleanup_at = generated.index(CLEANUP)
                for runtime_call in (b"v.len();", b"T::small_sort_threshold()"):
                    self.assertLess(cleanup_at, generated.index(runtime_call))
                self.assertLess(generated.index(b"T::small_sort_threshold()"),
                                generated.index(expected_assertion))
                self.assertLess(generated.index(b"assert requirement <= 48;"),
                                generated.index(b"return;"))
                self.assertNotIn(b"left_ancestor_pivot = None", generated)
                expected_runtime = renamed + source_prefix + \
                    b"\n        let requirement = len + 16;\n        return;\n    }\n" \
                    b"    // A1 diagnostic cut: non-base continuation is intentionally not present.\n" \
                    b"    return;\n}\n}\n"
                self.assertEqual(ghost.strip_ghost(generated), expected_runtime)

    def test_p1_cleanup_once_at_entry_and_runtime_bytes_unchanged_after_ghost_strip(self):
        generated = fixtures._p1_caller(SIGNATURE, GUARD)
        entry = b"        //@ a1_cleanup_option_ref(left_ancestor_pivot);\n"
        prefix = SIGNATURE + entry + GUARD
        self.assertTrue(generated.startswith(prefix))
        tail = generated[len(prefix):]
        self.assertIn(b"A1 diagnostic cut: non-base continuation", tail)
        self.assertIn(b"A1 checked ghost cleanup", tail)
        self.assertEqual(tail.count(CLEANUP), 0)
        self.assertEqual(generated.count(CLEANUP), 1)
        self.assertNotIn(b"core::mem::drop(left_ancestor_pivot)", tail)
        self.assertEqual(tail.count(b"return;"), 1)
        cleanup_at = generated.index(CLEANUP)
        for runtime_call in (b"v.len();", b"T::small_sort_threshold()",
                             b"T::small_sort(v, scratch, is_less);"):
            self.assertLess(cleanup_at, generated.index(runtime_call))
        runtime_before = SIGNATURE + GUARD + \
            b"\n        // A1 diagnostic cut: non-base continuation after original call is absent.\n" \
            b"        // A1 checked ghost cleanup for the arbitrary Option parameter.\n" \
            b"        return;\n    }\n}\n"
        self.assertEqual(ghost.strip_ghost(generated), runtime_before)


if __name__ == "__main__":
    unittest.main()
