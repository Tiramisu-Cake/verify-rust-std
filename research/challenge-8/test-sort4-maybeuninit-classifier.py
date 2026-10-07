#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted self-checks for strict MaybeUninit classification and MIR mutations."""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path


if os.environ.get("GITHUB_ACTIONS") != "true" or \
        os.environ.get("RUNNER_ENVIRONMENT") != "github-hosted" or \
        os.environ.get("RUNNER_OS") != "Linux":
    raise SystemExit("MaybeUninit classifier tests require GitHub-hosted Linux Actions")

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "sort4_maybeuninit_matrix", HERE / "check-maybeuninit-new-pointer.py")
if spec is None or spec.loader is None:
    raise SystemExit("cannot load MaybeUninit matrix")
matrix = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = matrix
spec.loader.exec_module(matrix)


MIR_SAMPLE = '''prefix = (keep = void),
defPath = "sort4_certified_maybeuninit::sort4_checked_maybeuninit_new",
      inputs = [
        (rawPtr = (mutability = (not = void))) ],
      localDecls = [ ],
      basicBlocks = [
        (id = (index = 0),
          statements = [
            ( sourceInfo = (line = 21), kind = (storageLive = (name = "_2")) ),
            ( sourceInfo = (line = 21), kind = (storageLive = (name = "_3")) ),
            ( sourceInfo = (line = 21), kind = (
                assign = (lhsPlace = (local = (name = "_3")),
                  rhsRvalue = (
                    use = (
                      copy = (
                        local = (name = "_1")))))) ) ],
          terminator = (call = void)),
        (id = (index = 1),
          statements = [
            (sourceInfo = (line = 21), kind = (
                assign = (
                  lhsPlace = (
                    local = (name = "_0")),
                  rhsRvalue = (aggregate = (unionActiveField = 1)))) ) ],
          terminator = (return = void)) ],
      impSpan = (sentinel = void),
suffix = (keep = void)
'''


class StrictNegativeGateTests(unittest.TestCase):
    def test_every_gate_is_required(self) -> None:
        keys = (
            "proof_expected", "integrity_and_frontend_ok", "verifier_failed",
            "target_obligation", "intended_message", "no_applicability_rejection",
            "named_probe_entered", "error_in_named_probe", "constructor_body_checked",
            "external_call_count_exact", "redirect_count_exact",
        )
        valid = {key: True for key in keys}
        self.assertTrue(matrix.strict_proof_negative(valid))
        for key in keys:
            with self.subTest(missing=key):
                corrupted = dict(valid, **{key: False})
                self.assertFalse(matrix.strict_proof_negative(corrupted))
                corrupted.pop(key)
                self.assertFalse(matrix.strict_proof_negative(corrupted))

    def test_pointee_is_unowned_in_caller_fixture(self) -> None:
        cert = matrix.certify_repository_sources(HERE.parents[1])
        _, verified, _ = matrix.constructor_source(cert)
        probe = verified.split(b"pub unsafe fn sort4_checked_maybeuninit_frame_probe", 1)[1]
        self.assertNotIn(b"*val |->", probe)
        self.assertIn(b"[?f](*frame |-> ?frame_value)", probe)
        self.assertIn(b"*other |-> ?other_value", probe)
        self.assertIn(b"std::mem::MaybeUninit::inner(wrapped) == some(val)", probe)


class RawMirMutationTests(unittest.TestCase):
    def test_each_mutation_changes_only_constructor_body(self) -> None:
        prefix, _ = MIR_SAMPLE.split('defPath = "', 1)
        _, suffix = MIR_SAMPLE.split("      impSpan = (", 1)
        for mutation in matrix.MIR_MUTATIONS:
            with self.subTest(mutation=mutation):
                mutated = matrix.mutate_constructor_mir(MIR_SAMPLE, mutation)
                self.assertNotEqual(mutated, MIR_SAMPLE)
                self.assertTrue(mutated.startswith(prefix))
                self.assertTrue(mutated.endswith("      impSpan = (" + suffix))

    def test_unknown_or_ambiguous_body_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            matrix.mutate_constructor_mir(MIR_SAMPLE, "unlisted")
        with self.assertRaises(ValueError):
            matrix.mutate_constructor_mir(MIR_SAMPLE + MIR_SAMPLE, "operand")


if __name__ == "__main__":
    unittest.main()
