#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted integrity controls for the helper fixture/certificate builders.

These checks do not replace MIR, refinement or proof-negative controls.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


HERE = Path(__file__).resolve().parent
G1 = load(HERE / "prepare-forget-frames.py", "overnight_g1")
A1 = load(HERE / "prepare-assume-init-2610.py", "overnight_a1")
PRIMITIVE = load(HERE / "prepare-a1-primitive-matrix.py",
                 "overnight_a1_primitive")


class SourceAndContractControls(unittest.TestCase):
    def test_separate_contract_clauses_and_ghost_stripping(self):
        g1_original, g1_verified, _ = G1.fixture("symbolic_frame")
        self.assertEqual(g1_verified.count(b"/*@\nreq "), 1)
        self.assertEqual(g1_verified.count(b"/*@\nens "), 1)
        self.assertEqual(g1_verified.count(b"/*@\non_unwind_ens "), 1)
        self.assertEqual(G1.strip_ghost(g1_verified), g1_original)
        self.assertEqual(g1_original.count(G1.FORGET_BODY), 1)
        self.assertNotIn(b"checked_forget_generic(t)", g1_original)
        call_original, call_verified, _ = G1.fixture("no_cell")
        self.assertEqual(call_verified.count(b"/*@\nreq "), 2)
        self.assertEqual(call_verified.count(b"/*@\nens "), 2)
        self.assertEqual(call_verified.count(b"/*@\non_unwind_ens "), 2)
        self.assertEqual(call_original.count(G1.FORGET_BODY), 1)
        self.assertEqual(call_original.count(b"checked_forget_generic(t)"), 1)
        self.assertEqual(G1.strip_ghost(call_verified), call_original)

        body = A1.METHOD_BODY.replace(b"::<T>", b"::<*const Element>")
        body = body.replace(b"transmute_neo(self)", b"transmute_neo(storage)")
        a1_original, a1_verified, _ = A1.fixture_source(body, "initialized")
        self.assertEqual(a1_verified.count(b"/*@\nreq "), 2)
        self.assertEqual(a1_verified.count(b"/*@\nens "), 2)
        self.assertEqual(a1_verified.count(b"/*@\non_unwind_ens "), 2)
        self.assertEqual(A1.strip_ghost(a1_verified), a1_original)
        self.assertNotIn(b"*storage |->", a1_verified)
        self.assertNotIn(b"*p |->", a1_verified)

    def test_invalid_contract_clause_shape_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "separate complete"):
            G1.ghost(b"req true; ens true; on_unwind_ens false;")
        with self.assertRaisesRegex(ValueError, "separate complete"):
            A1.ghost(b"req true;\nens true;")

    def test_all_proof_negatives_name_distinct_obligations(self):
        for module in (G1, A1, PRIMITIVE):
            with self.subTest(module=module.__name__):
                self.assertEqual(set(module.POSITIVES) & set(module.NEGATIVES), set())
                self.assertEqual(len(module.VARIANTS), len(set(module.VARIANTS)))


class FullMirControls(unittest.TestCase):
    def test_transmute_manifest_requires_exact_cast_kind_and_body(self):
        original = (
            '    ( defKind = (function = void), '
            'defPath = "checked_transmute_neo_pointer", '
            'inputs = [], localDecls = [], '
            'basicBlocks = [(kind = (transmute = void), '
            'operand = (move = (local = "_3", projection = [])), '
            'ty = (rawPtr = (param = "Element")))] )'
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decoded = root / "decoded.txt"
            manifest = root / "reviewed.json"
            decoded.write_text(original)
            _, body = A1.complete_function_record(original,
                                                   A1.TRANSMUTE_ADAPTER_NAME)
            template = {
                "reviewed": True,
                "reviewed_by": "hosted-test-control",
                "target": "transmute",
                "source_sha256": A1.SOURCE_SHA,
                "typed_pointer_only": True,
                "adapter_defpath": A1.TRANSMUTE_ADAPTER_NAME,
                "adapter_full_mir_sha256": A1.digest(body.encode()),
                "expected_calls": [],
                "expected_cast_kind": "transmute",
            }
            manifest.write_text(json.dumps(template))
            with mock.patch.object(A1, "certify_source", return_value=(
                b"", {"source_sha256": A1.SOURCE_SHA})):
                self.assertEqual(A1.check_mir(decoded, manifest, root)["target"],
                                 "transmute")
                altered = original.replace("transmute = void",
                                           "boxDerefTransmute = void")
                decoded.write_text(altered)
                with self.assertRaisesRegex(ValueError, "complete adapter typed MIR"):
                    A1.check_mir(decoded, manifest, root)
                template["adapter_full_mir_sha256"] = A1.digest(altered.strip().encode())
                manifest.write_text(json.dumps(template))
                with self.assertRaisesRegex(ValueError, "transmute body inventory"):
                    A1.check_mir(decoded, manifest, root)
                manifest.write_text(json.dumps(template | {
                    "adapter_full_mir_sha256": A1.digest(body.encode())}))
                for old, new in (
                    ("move =", "copy ="),
                    ("projection = []", "projection = [(boxAsNonNull = void)]"),
                    ('param = "Element"', 'param = "OtherElement"'),
                    ("rawPtr =", "uint ="),
                ):
                    with self.subTest(mutation=old):
                        decoded.write_text(original.replace(old, new))
                        with self.assertRaisesRegex(ValueError,
                                                    "complete adapter typed MIR"):
                            A1.check_mir(decoded, manifest, root)

    def test_complete_record_hash_rejects_extra_block_and_wrong_identity(self):
        original = (
            '    ( defKind = (function = void), defPath = "checked_assume_init_pointer", '
            'inputs = [], localDecls = [], basicBlocks = [(index = 0)] )'
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decoded = root / "decoded.txt"
            manifest = root / "reviewed.json"
            decoded.write_text(original)
            defpath, body = A1.complete_function_record(original, A1.ADAPTER_NAME)
            self.assertEqual(body, original.strip())
            manifest.write_text(json.dumps({
                "reviewed": True,
                "reviewed_by": "hosted-test-control",
                "target": "method",
                "source_sha256": A1.SOURCE_SHA,
                "typed_pointer_only": True,
                "adapter_defpath": defpath,
                "adapter_full_mir_sha256": A1.digest(body.encode()),
                "expected_calls": ["assert_inhabited", "transmute_neo"],
            }))
            with mock.patch.object(A1, "certify_source", return_value=(
                b"", {"source_sha256": A1.SOURCE_SHA})):
                with self.assertRaisesRegex(ValueError, "call inventory"):
                    A1.check_mir(decoded, manifest, root)
                mutated = original.replace("(index = 0)", "(index = 0), (index = 1)")
                decoded.write_text(mutated)
                with self.assertRaisesRegex(ValueError, "complete adapter typed MIR"):
                    A1.check_mir(decoded, manifest, root)
                decoded.write_text(original.replace(A1.ADAPTER_NAME,
                                                    A1.ADAPTER_NAME + "_impostor"))
                with self.assertRaisesRegex(ValueError, "MIR function identity"):
                    A1.check_mir(decoded, manifest, root)

    def test_unreviewed_manifest_cannot_accept_matching_bytes(self):
        sample = (
            '    ( defKind = (function = void), defPath = "checked_assume_init_pointer", '
            'inputs = [], localDecls = [], basicBlocks = [] )'
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decoded = root / "decoded.txt"
            manifest = root / "capture.json"
            decoded.write_text(sample)
            manifest.write_text(json.dumps({
                "reviewed": False,
                "target": "method",
                "source_sha256": A1.SOURCE_SHA,
                "typed_pointer_only": True,
                "adapter_defpath": A1.ADAPTER_NAME,
                "adapter_full_mir_sha256": A1.digest(sample.strip().encode()),
                "expected_calls": ["assert_inhabited", "transmute_neo"],
            }))
            with mock.patch.object(A1, "certify_source", return_value=(
                b"", {"source_sha256": A1.SOURCE_SHA})):
                with self.assertRaisesRegex(ValueError, "reviewed applicability"):
                    A1.check_mir(decoded, manifest, root)


if __name__ == "__main__":
    if (os.environ.get("GITHUB_ACTIONS") != "true" or
            os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted"):
        raise SystemExit("certificate tests run only on GitHub-hosted Actions")
    unittest.main()
