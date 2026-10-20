"""Synthetic regression for positive and own-false31 receipt input binding."""
from __future__ import annotations

import copy
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load isolated module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RUNNER = load("a1_positive_receipt_runner_test", HERE / "a1-runner.py")
FIXTURES = load("a1_positive_receipt_admission_fixtures", HERE / "test_a1_contract_admission.py")
RECEIPTS = load("a1_positive_receipt_writer", HERE / "a1-summary-receipt.py")
BUILD = "11111111-2222-3333-4444-555555555555"
PROOF, INFRA, PROFILE = "1" * 40, "2" * 40, "3" * 64
HASHES = {"verified": "a" * 64, "original": "b" * 64,
          "verifier": "c" * 64, "exporter": "d" * 64, "schema": "e" * 64}
BOUND = {
    "default16": {"compiler_impl_id": "10", "compiler_item_id": "11"},
    "freeze32": {"compiler_impl_id": "20", "compiler_item_id": "21"},
}
NATIVE_POSTS = {"normal": "normal-contract", "unwind": "unwind-contract"}


class Observer:
    @staticmethod
    def observe(case_id, normal, readonly, certificate, source):
        return {"binding": {"mir_body_span": {"lo": {"line": 123}}}}


def base_expected_cases():
    expected = FIXTURES.expected_cases()
    for case_id, impl in (("P0a", "default16"), ("P0b", "freeze32"),
                          ("N-default-contract", "default16"),
                          ("N-freeze-contract", "freeze32")):
        expected[case_id]["focused_item_id"] = BOUND[impl]["compiler_item_id"]
    return expected


def certificate():
    return {"cases": {
        "P0a": {"source_id": "source:baseline-pair", "unit_id": "unit:default-threshold",
                "source_file": "P0c.rs"},
        "P0b": {"source_id": "source:baseline-pair", "unit_id": "unit:freeze-threshold",
                "source_file": "P0c.rs"},
        "P0c": {"source_id": "source:baseline-pair", "unit_id": "unit:P0c",
                "source_file": "P0c.rs"},
        "N-false31": {"source_id": "source:false31-pair", "unit_id": "unit:false31",
                      "source_file": "N-false31.rs"},
    }}


class PositiveReceiptBindingTests(unittest.TestCase):
    def invoke(self, directory: Path, *, mode="positive", raw_mutations=None):
        evidence = directory / "evidence"
        source_package = directory / "source-package"
        evidence.mkdir()
        source_package.mkdir()
        cases = certificate()["cases"]
        receipt_case = "P0c" if mode == "positive" else "N-false31"
        source_file = cases[receipt_case]["source_file"]
        (source_package / source_file).write_text("fn a1_guard_observer() {}\n")
        fixture = evidence / "a1-fixtures" / receipt_case / "verified"
        fixture.mkdir(parents=True)
        (fixture / "lib.rs").write_text("fn a1_guard_observer() {}\n")
        normal = directory / "normal-mir.txt"
        readonly = directory / "readonly-mir.txt"
        normal.write_text("normal")
        readonly.write_text("readonly")

        if mode == "positive":
            source_cases = ("P0a", "P0b")
            source_pairs = ({"verified": HASHES["verified"], "original": HASHES["original"]},) * 2
            expected = base_expected_cases()
        else:
            source_cases = ("N-false31", "N-false31")
            source_pairs = ({"verified": HASHES["verified"], "original": HASHES["original"]},) * 2
            false_identity = {"source_id": cases["N-false31"]["source_id"],
                              "unit_id": cases["N-false31"]["unit_id"]}
            expected = base_expected_cases()
            for case_id in ("P0a", "P0b", "P0c", "P-dispatch", "P1"):
                expected[case_id].update(false_identity)

        positive = {}
        for index, (impl, case_id) in enumerate(zip(("default16", "freeze32"), source_cases)):
            raw = {**cases[case_id], "build_id": BUILD,
                   "source_pair_sha256": dict(source_pairs[index]),
                   "artifacts": {"normal-mir.txt": {"path": str(normal)},
                                 "readonly-mir.txt": {"path": str(readonly)}}}
            for (which, field), value in (raw_mutations or {}).items():
                if which == impl:
                    if value is MISSING:
                        raw.pop(field, None)
                    else:
                        raw[field] = value
            observed = {"body_count": 1, "compiler_identity": {"impl": impl, **BOUND[impl]},
                        "normal_posts_preserved": True, "unwind_posts_preserved": True,
                        "focus_body_verified": True, "focus_conformance_verified": True}
            positive["P0a" if impl == "default16" else "P0b"] = {
                "raw": raw,
                "structure": {"bound_impls": copy.deepcopy(BOUND),
                              "threshold_posts": {"native": copy.deepcopy(NATIVE_POSTS)}},
                "execution_attestation": observed,
                "proof_candidate": {"classification": "FOCUSED_VF0_CANDIDATE"},
            }

        helpers = {
            "a1-contract-admission.py": FIXTURES.admission,
            "a1-summary-receipt.py": RECEIPTS,
            "a1-call-binding.py": Observer,
        }
        tool_receipt = {"console_binary_sha256": HASHES["verifier"],
                        "exporter_binary_sha256": HASHES["exporter"],
                        "final_schema_sha256": HASHES["schema"]}
        args = SimpleNamespace(evidence=evidence)
        written = {}

        def write_receipt(path, gate, **pins):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic receipt\n")
            written.update(gate=gate, pins=pins)

        env = {"CLOUD_BUILD_ID": BUILD, "PROOF_SHA": PROOF, "INFRA_SHA": INFRA}
        pair_source_case = "P0a" if mode == "positive" else "N-false31"
        with patch.dict(os.environ, env), patch.object(RECEIPTS, "write_cloud_receipt",
                                                       side_effect=write_receipt):
            result = RUNNER.publish_positive_threshold_receipt(
                args, tool=directory / "tool", tool_receipt=tool_receipt,
                certificate={"cases": cases}, source_package=source_package,
                positive=positive, expected_cases=expected, helpers=helpers,
                profile_sha256=PROFILE, pair_source_case=pair_source_case,
                receipt_case=receipt_case)
        return result, written, positive

    def test_distinct_positive_units_are_admitted_against_their_own_certificate_cases(self):
        with tempfile.TemporaryDirectory(prefix="a1-receipt-positive-") as temp:
            result, written, positive = self.invoke(Path(temp))
        gate = written["gate"]
        self.assertEqual(gate.expected_impl_inputs, {
            "default16": {"source_id": "source:baseline-pair", "unit_id": "unit:default-threshold"},
            "freeze32": {"source_id": "source:baseline-pair", "unit_id": "unit:freeze-threshold"},
        })
        self.assertEqual(gate.implementations["default16"]["unit_id"], positive["P0a"]["raw"]["unit_id"])
        self.assertEqual(gate.implementations["freeze32"]["unit_id"], positive["P0b"]["raw"]["unit_id"])
        self.assertTrue(gate.common_summary_available)
        self.assertTrue(str(result[1]).endswith("a1-threshold-summary.receipt"))

    def test_wrong_or_swapped_raw_ids_are_rejected_without_admission(self):
        mutations = (
            {("freeze32", "unit_id"): "unit:default-threshold"},
            {("default16", "unit_id"): "unit:freeze-threshold"},
            {("freeze32", "source_id"): "source:other-pair"},
        )
        for change in mutations:
            with self.subTest(change=change), tempfile.TemporaryDirectory(prefix="a1-receipt-wrong-") as temp:
                with self.assertRaisesRegex(RuntimeError, "raw source/unit identity"):
                    self.invoke(Path(temp), raw_mutations=change)

    def test_missing_null_and_wrong_type_raw_identity_fail_explicitly(self):
        for impl, field, value in (
                ("default16", "source_id", MISSING),
                ("default16", "unit_id", None),
                ("freeze32", "source_id", 7),
                ("freeze32", "unit_id", [])):
            change = {(impl, field): value}
            with self.subTest(change=change), tempfile.TemporaryDirectory(prefix="a1-receipt-metadata-") as temp:
                with self.assertRaisesRegex(RuntimeError, "raw source/unit identity"):
                    self.invoke(Path(temp), raw_mutations=change)

    def test_own_false31_receipt_uses_its_own_certified_identity_for_both_impls(self):
        with tempfile.TemporaryDirectory(prefix="a1-receipt-false31-") as temp:
            _, written, positive = self.invoke(Path(temp), mode="false31")
        gate = written["gate"]
        own = {"source_id": "source:false31-pair", "unit_id": "unit:false31"}
        self.assertEqual(dict(gate.expected_impl_inputs["default16"]), own)
        self.assertEqual(dict(gate.expected_impl_inputs["freeze32"]), own)
        for impl, case in (("default16", "P0a"), ("freeze32", "P0b")):
            self.assertEqual(dict(gate.implementations[impl])["source_id"], own["source_id"])
            self.assertEqual(dict(gate.implementations[impl])["unit_id"], own["unit_id"])
            self.assertEqual(positive[case]["raw"]["source_id"], own["source_id"])
            self.assertEqual(positive[case]["raw"]["unit_id"], own["unit_id"])
        self.assertTrue(gate.common_summary_available)


class _Missing:
    pass


MISSING = _Missing()


if __name__ == "__main__":
    unittest.main(verbosity=2)
