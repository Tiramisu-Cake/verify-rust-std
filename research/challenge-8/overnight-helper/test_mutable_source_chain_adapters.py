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

    def test_nine_body_adapter_inserts_generic_a1_without_changing_helper_suffix(self):
        a1 = NINE.load_a1()
        pair = (
            b"pub unsafe fn " + a1.TRANSMUTE_ADAPTER_NAME.encode() +
            b"<Src, Dst>(src: Src) -> Dst { transmute_unchecked(src) }\n"
            b"pub unsafe fn " + a1.ADAPTER_NAME.encode() +
            b"<T>(storage: T) -> T { transmute_neo(storage) }\n")
        seven = (
            NINE.OLD_FEATURE + NINE.OLD_IMPORT +
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
        pair = (
            b"pub unsafe fn " + a1.TRANSMUTE_ADAPTER_NAME.encode() +
            b"<Src, Dst>(src: Src) -> Dst { transmute_unchecked(src) }\n"
            b"pub unsafe fn " + a1.ADAPTER_NAME.encode() +
            b"<T>(storage: T) -> T { transmute_neo(storage) }\n")
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
