#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted integrity controls for the helper fixture/certificate builders.

These checks do not replace MIR, refinement or proof-negative controls.
"""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HERE = Path(__file__).resolve().parent
G1 = load(HERE / "prepare-forget-frames.py", "overnight_g1")
A1 = load(HERE / "prepare-assume-init-2610.py", "overnight_a1")


class SourceAndContractControls(unittest.TestCase):
    def test_separate_contract_clauses_and_ghost_stripping(self):
        g1_original, g1_verified, _ = G1.fixture("symbolic_frame")
        self.assertEqual(g1_verified.count(b"/*@\nreq "), 2)
        self.assertEqual(g1_verified.count(b"/*@\nens "), 2)
        self.assertEqual(g1_verified.count(b"/*@\non_unwind_ens "), 2)
        self.assertEqual(G1.strip_ghost(g1_verified), g1_original)

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
        for module in (G1, A1):
            with self.subTest(module=module.__name__):
                self.assertEqual(set(module.POSITIVES) & set(module.NEGATIVES), set())
                self.assertEqual(len(module.VARIANTS), len(set(module.VARIANTS)))


class FullMirControls(unittest.TestCase):
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
