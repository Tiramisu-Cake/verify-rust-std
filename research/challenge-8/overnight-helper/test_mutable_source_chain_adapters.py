"""Synthetic tests for mutable source generation; never prepare real std."""
from __future__ import annotations

import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HELPER = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MUT_SOURCE = load("p2_mut_parallel_source",
                  HELPER / "prepare-actual-helper-capture-mut-parallel.py")
OWNER_LINKED = load("p2_mut_owner_linked_source_test",
                    HELPER / "prepare-actual-owner-linked-mut.py")
NESTED = load("p2_mut_nested_source_test",
              ROOT / "research/challenge-8/overnight-guard-actual/prepare-actual-nested-drop-mut.py")
NINE = load("p2_mut_nine_source_test",
            ROOT / "research/challenge-8/overnight-assume-actual/prepare-actual-nine-body-mut.py")
OWNER = OWNER_LINKED.load_modules()[0]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def synthetic_a1_const_pair():
    """Pinned A1 source shapes, synthesized without reading repository std."""
    a1 = NINE.load_a1()
    tx_body = a1.TRANSMUTE_BODY.replace(
        b"Src::SIZE",
        b"<MaybeUninit<*const Element> as SizedTypeProperties>::SIZE").replace(
        b"Dst::SIZE", b"<*const Element as SizedTypeProperties>::SIZE")
    tx_contract = a1.ghost(
        b"req thread_token(?tid) &*& tid == currentThread &*& "
        b"std::mem::MaybeUninit::inner(src) == some(?p) &*& "
        b"std::mem::MaybeUninit_pointer_own::<Element>()(tid, src);\n"
        b"ens thread_token(tid) &*& result == p &*& "
        b"raw_ptr_own::<Element>()(tid, result);\n"
        b"on_unwind_ens false;")
    tx = (b"pub unsafe fn " + a1.TRANSMUTE_ADAPTER_NAME.encode() +
          b"<Element>(src: MaybeUninit<*const Element>) -> *const Element\n" +
          tx_contract + tx_body + b"\n")
    as_body = a1.METHOD_BODY.replace(b"::<T>", b"::<*const Element>").replace(
        b"transmute_neo(self)", b"transmute_neo(storage)")
    as_contract = a1.ghost(
        b"req thread_token(?tid) &*& tid == currentThread &*& "
        b"std::mem::MaybeUninit::inner(storage) == some(?p) &*& "
        b"std::mem::MaybeUninit_pointer_own::<Element>()(tid, storage);\n"
        b"ens thread_token(tid) &*& result == p &*& "
        b"raw_ptr_own::<Element>()(tid, result);\n"
        b"on_unwind_ens false;")
    assume = (b"pub unsafe fn " + a1.ADAPTER_NAME.encode() +
              b"<Element>(storage: MaybeUninit<*const Element>) -> *const Element\n" +
              as_contract + as_body + b"\n")
    pair = tx + b"\n" + assume
    if (pair.count(b"*const Element") != 7 or
            pair.count(b"assert_inhabited::<*const Element>()") != 1 or
            pair.count(b"transmute_unchecked(src)") != 1 or
            pair.count(b"transmute_neo(storage)") != 1):
        raise AssertionError("synthetic A1 source shape drifted")
    return pair


class MutableSourceChain(unittest.TestCase):
    def test_parallel_fixture_writer_is_const_independent_and_capture_only(self):
        body = b"{\n    crate::mem::forget(guard);\n}"
        source = {"target_specialization": "T = *mut Element; Element unrestricted",
                  "runtime_body_exact": True, "exact_body_sha256": digest(body),
                  "hint_sha256": MUT_SOURCE.HINT_SHA256,
                  "maybe_uninit_sha256": MUT_SOURCE.MAYBE_SHA256}
        original, verified, record = MUT_SOURCE.build_pair_from_body(body, source)
        self.assertEqual(OWNER.strip_ghost(verified), original)
        self.assertEqual(record["classification"],
                         "MUTABLE_SOURCE_FIXTURE; CAPTURE ONLY")
        self.assertEqual(record["typed_mir_binding_established"], False)
        self.assertEqual(record["proof_credit"], 0)
        text = (HELPER / "prepare-actual-helper-capture-mut-parallel.py").read_text()
        self.assertNotIn("prepare-actual-helper-capture.py", text)
        self.assertNotIn("load_const", text)
        self.assertNotIn(b"*const Element", verified)

    def test_linker_type_adapter_rewrites_only_fixture_types_and_preserves_body(self):
        source = (b"pub fn ctor<Element>(p: *const Element) -> "
                  b"MaybeUninit<*const Element> { unreachable!() }\n")
        expected = (b"pub fn ctor<Element>(p: *mut Element) -> "
                    b"MaybeUninit<*mut Element>")
        out, info = OWNER_LINKED.rewrite_component(source, 2, expected, "test constructor")
        self.assertEqual(out.count(expected), 1)
        self.assertNotIn(b"*const Element", out)
        self.assertEqual(info["const_element_type_sites"], 2)
        bad_sources = (
            (source, 1, expected),
            (b"pub fn bad(p: *const *const Element);\n", 1, b"pub fn bad(p: *mut *mut Element)"),
        )
        for bad, count, signature in bad_sources:
            with self.assertRaises(ValueError):
                OWNER_LINKED.rewrite_component(bad, count, signature, "bad source")

    def test_nested_drop_and_owned_forget_adapters_preserve_runtime(self):
        method = METHOD = b"pub unsafe fn sort4_checked_generic_drop<T>(slot: *mut T) { drop_in_place(slot); }\n"
        base = (
            b"use std::mem::MaybeUninit;\n"
            b"struct DropOnPanic<T> { inner: T }\n"
            b"impl<T> Drop for DropOnPanic<T> { }\n"
            b"pub fn select_unpredictable<Element>(\n"
            b"    condition: bool,\n    true_val: *mut Element,\n"
            b"    false_val: *mut Element,\n) -> *mut Element {\n"
            b"        crate::mem::forget(guard);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"}\n")
        owner_open = (
            b"        /*@ open <select_unpredictable::DropOnPanic<*Element>>.own(t, guard); @*/\n"
            b"        /*@ assert *guard.inner |-> ?selected_payload; @*/\n"
            b"        /*@ open raw_ptr_own::<Element>()(t, selected_payload); @*/\n")
        base = base.replace(b"        crate::mem::forget(guard);\n",
                            owner_open + b"        crate::mem::forget(guard);\n", 1)
        original = OWNER.strip_ghost(base)
        six_original, six, stage = NESTED.insert_generic_drop(
            base, original, method, OWNER.strip_ghost)
        self.assertTrue(stage["ghost_strip_identity"])
        owned_method = b"pub unsafe fn checked_forget_owned<T>(t: T) { ManuallyDrop::new(t); }\n"
        seven_original, seven, owned_stage = NESTED.insert_owned_forget(
            six, six_original, owned_method, b"use std::mem::MaybeUninit;\n",
            OWNER.strip_ghost)
        self.assertEqual(OWNER.strip_ghost(seven), seven_original)
        self.assertIn(NESTED.SAVED_GUARD, seven)
        self.assertIn(NESTED.RETURNED_GUARD, seven)
        self.assertTrue(owned_stage["saved_guard_transfer"])
        self.assertEqual(seven_original.count(b"crate::mem::forget(guard);"), 1)

    def test_nine_body_adapter_finitely_specializes_pinned_a1_types(self):
        a1 = NINE.load_a1()
        const_pair = synthetic_a1_const_pair()
        self.assertEqual(const_pair.count(b"*const Element"), 7)
        pair, adapted = NINE.adapt_a1_pair_mut(const_pair, a1)
        self.assertEqual(pair.count(b"*mut Element"), 7)
        self.assertNotIn(b"*const Element", pair)
        self.assertEqual(pair.replace(b"*mut Element", b"*const Element"), const_pair)
        self.assertEqual(adapted["const_pointer_type_sites"],
                         {"transmute": 4, "assume_init": 3})
        seven = (
            NINE.OLD_FEATURE + NINE.OLD_IMPORT +
            b"pub unsafe fn checked_forget_owned<T>(t: T) { synthetic_forget(t); }\n" +
            b"pub fn select_unpredictable<Element>(\n"
            b"    condition: bool,\n    true_val: *mut Element,\n"
            b"    false_val: *mut Element,\n) -> *mut Element {\n"
            b"        crate::mem::forget(guard);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"}\n")
        seven_original = OWNER.strip_ghost(seven)
        original, verified, stage = NINE.insert_a1_pair(
            seven_original, seven, pair, {"typed_mir_binding": False},
            OWNER.strip_ghost)
        self.assertEqual(verified[verified.index(NINE.ACTUAL_MARKER):],
                         seven[seven.index(NINE.ACTUAL_MARKER):])
        self.assertEqual(original[original.index(NINE.ACTUAL_MARKER):],
                         seven_original[seven_original.index(NINE.ACTUAL_MARKER):])
        self.assertTrue(stage["ghost_strip_identity"])
        self.assertEqual(verified.count(b"transmute_unchecked(src)"), 1)
        self.assertEqual(verified.count(b"transmute_neo(storage)"), 1)
        self.assertEqual(verified.count(b"assert_inhabited::<*mut Element>()"), 1)
        self.assertTrue(stage["a1_pair_inserted_before_owned_forget"])
        ordered = [b"pub unsafe fn checked_transmute_neo_pointer",
                   b"pub unsafe fn checked_assume_init_pointer", NINE.FORGET_MARKER,
                   NINE.ACTUAL_MARKER]
        positions = [verified.index(marker) for marker in ordered]
        self.assertEqual(positions, sorted(positions))
        forget_line = b"pub unsafe fn checked_forget_owned<T>(t: T) { synthetic_forget(t); }\n"
        for bad in (seven.replace(forget_line, b""),
                    seven.replace(forget_line, forget_line * 2),
                    seven.replace(forget_line, b"") + forget_line):
            with self.subTest(anchor=bad), self.assertRaises(ValueError):
                NINE.insert_a1_pair(OWNER.strip_ghost(bad), bad, pair, {}, OWNER.strip_ghost)
        self.assertNotIn(b"*const Element", verified)
        seven = (
            NINE.OLD_FEATURE + NINE.OLD_IMPORT +
            b"pub unsafe fn checked_forget_owned<T>(t: T) { synthetic_forget(t); }\n" +
            b"pub fn select_unpredictable<Element>(\n"
            b"    condition: bool,\n    true_val: *mut Element,\n"
            b"    false_val: *mut Element,\n) -> *mut Element {\n"
            b"        crate::mem::forget(guard);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"}\n")
        seven_original = OWNER.strip_ghost(seven)
        original, verified, stage = NINE.insert_a1_pair(
            seven_original, seven, pair, {"typed_mir_binding": False},
            OWNER.strip_ghost)
        self.assertEqual(verified[verified.index(NINE.ACTUAL_MARKER):],
                         seven[seven.index(NINE.ACTUAL_MARKER):])
        self.assertEqual(original[original.index(NINE.ACTUAL_MARKER):],
                         seven_original[seven_original.index(NINE.ACTUAL_MARKER):])
        self.assertTrue(stage["ghost_strip_identity"])
        self.assertEqual(verified.count(b"transmute_unchecked(src)"), 1)
        self.assertEqual(verified.count(b"transmute_neo(storage)"), 1)
        self.assertNotIn(b"*const Element", verified)

    def test_mutable_route_imports_no_const_writer(self):
        paths = (
            HELPER / "prepare-actual-owner-linked-mut.py",
            ROOT / "research/challenge-8/overnight-guard-actual/prepare-actual-nested-drop-mut.py",
            ROOT / "research/challenge-8/overnight-assume-actual/prepare-actual-nine-body-mut.py",
        )
        joined = "\n".join(path.read_text() for path in paths)
        self.assertNotIn("prepare-actual-helper-capture.py\"", joined)
        self.assertNotIn("load_const()", joined)
        self.assertNotIn("overnight-linkage/check-intrinsic-drop-linkage.py", joined)
        self.assertIn("prepare-actual-helper-capture-mut-parallel.py", joined)
        self.assertIn("require_cloud_provider", joined)
        self.assertIn("typed_mir_binding_established", joined)

    def test_full_mutable_source_chain_to_fractional_candidate_on_synthetic_bytes(self):
        body = (
            b"{\n"
            b"    let true_ptr = true_val.as_mut_ptr();\n"
            b"    let false_ptr = false_val.as_mut_ptr();\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val);\n"
            b"        let guard = DropOnPanic { inner: guard };\n"
            b"        drop.drop_in_place();\n"
            b"        crate::mem::forget(guard);\n"
            b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()\n"
            b"}")
        source_cert = {"target_specialization": "T = *mut Element; Element unrestricted",
                       "runtime_body_exact": True,
                       "exact_body_sha256": digest(body)}
        _, helper_verified, _ = MUT_SOURCE.build_pair_from_body(body, source_cert)
        const_components = (
            (b"pub fn ctor<Element>(p: *const Element) -> MaybeUninit<*const Element>;\n",
             2, b"pub fn ctor<Element>(p: *mut Element) -> MaybeUninit<*mut Element>"),
            (b"pub fn asptr<Element>(p: &mut MaybeUninit<*const Element>) "
             b"-> *mut *const Element { p as *mut *const Element }\n",
             3, b"pub fn asptr<Element>(p: &mut MaybeUninit<*mut Element>) "
                b"-> *mut *mut Element"),
            (b"pub unsafe fn drop_ptr<Element>(p: *mut *const Element) {}\n",
             1, b"pub unsafe fn drop_ptr<Element>(p: *mut *mut Element)"),
        )
        support = b""
        for source, count, signature in const_components:
            adapted, _ = OWNER_LINKED.rewrite_component(source, count, signature,
                                                         "synthetic S6 component")
            support += adapted
        mixed = (support + b"struct DropOnPanic<T> { inner: T }\n"
                 b"impl<T> Drop for DropOnPanic<T> {\n"
                 b"            unsafe { self.inner.drop_in_place() }\n}\n"
                 + helper_verified)
        self.assertNotIn(b"*const Element", mixed)
        canonical = OWNER_LINKED.canonical_actual_contract(mixed,
                                                           OWNER_LINKED.load_modules()[2])
        original = OWNER.strip_ghost(canonical)
        owner_candidate, _ = OWNER_LINKED.apply_owner_projection(canonical, original)
        method = b"pub unsafe fn sort4_checked_generic_drop<T>(slot: *mut T) { drop_in_place(slot); }\n"
        six_original, six_verified, _ = NESTED.insert_generic_drop(
            owner_candidate, original, method, OWNER.strip_ghost)
        r21 = NINE.load(NINE.HERE / "r21_fractional_forget.py",
                        "p2_mut_full_chain_r21")
        owned_method = (r21.FORGET_SIGNATURE + r21.FORGET_OLD_CONTRACT +
                        r21.FORGET_BODY + b"\n")
        seven_original, seven_verified, _ = NESTED.insert_owned_forget(
            six_verified, six_original, owned_method,
            b"use std::mem::MaybeUninit;\n", OWNER.strip_ghost)
        a1 = NINE.load_a1()
        pair, _ = NINE.adapt_a1_pair_mut(synthetic_a1_const_pair(), a1)
        nine_original, nine_verified, _ = NINE.insert_a1_pair(
            seven_original, seven_verified, pair, {}, OWNER.strip_ghost)
        final = NINE.apply_fractional_candidate(
            nine_original, nine_verified,
            {"specialization": "T = *mut Element; Element unrestricted"})[0]
        self.assertEqual(OWNER.strip_ghost(final), nine_original)
        self.assertNotIn(b"*const Element", final)
        self.assertIn(b"close [1/2] raw_ptr_own::<Element>()", final)
        self.assertIn(b"selected_payload", final)
        self.assertEqual(final.count(b"crate::mem::forget(guard);"), 1)


if __name__ == "__main__":
    unittest.main()
