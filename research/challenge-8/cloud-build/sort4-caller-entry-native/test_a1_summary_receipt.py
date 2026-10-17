"""Synthetic checks for cross-source/tool summary reuse and premature release."""
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


fixtures = load("a1_admission_test_inputs", HERE / "test_a1_contract_admission.py")
receipt = load("a1_summary_receipt", HERE / "a1-summary-receipt.py")
HASHES = dict(zip(receipt.HASH_FIELDS, (c * 64 for c in "abcde")))
BUILD = "11111111-2222-3333-4444-555555555555"
PROOF, INFRA, PROFILE = "1" * 40, "2" * 40, "3" * 64
PINS = {"tool_id": receipt.tool_id(HASHES), "profile_id": PROFILE,
        "proof_id": PROOF, "infra_id": INFRA, "target_id": receipt.TARGET}
INVENTORY = {"default16": {"compiler_impl_id": "10", "compiler_item_id": "11"},
             "freeze32": {"compiler_impl_id": "20", "compiler_item_id": "21"}}


def expected_case_manifest():
    cases = fixtures.expected_cases()
    for case_id, impl in (("P0a", "default16"), ("P0b", "freeze32"),
                          ("N-default-contract", "default16"),
                          ("N-freeze-contract", "freeze32")):
        cases[case_id]["focused_item_id"] = INVENTORY[impl]["compiler_item_id"]
    return cases


def make_gate(count=2):
    gate = fixtures.admission.A1Admission(INVENTORY, PINS, fixtures.IMPL_INPUTS,
                                         expected_case_manifest())
    for impl in ("default16", "freeze32")[:count]:
        row = fixtures.implementation(impl)
        row.update(PINS, build_id=BUILD, source_pair_id=receipt.source_pair_id(HASHES))
        row["inventory"] = [{"impl": name, **ids} for name, ids in INVENTORY.items()]
        row["compiler_identity"] = {"impl": impl, **INVENTORY[impl]}
        row["focused_item_id"] = INVENTORY[impl]["compiler_item_id"]
        gate.record_implementation(row)
    return gate


def render(gate, **changes):
    args = dict(build=BUILD, proof=PROOF, infra=INFRA, profile=PROFILE, hashes=HASHES,
                caller_focus="verified/lib.rs:100")
    args.update(changes)
    return receipt.render_receipt(gate, **args)


class ReceiptTests(unittest.TestCase):
    def test_one_impl_or_collector_success_cannot_publish(self):
        for count in (0, 1):
            gate = make_gate(count)
            gate.report_build(terminal_success=True, collector_success=True)
            with self.assertRaises(receipt.ReceiptError):
                render(gate)

    def test_receipt_binds_actual_source_pair_not_shared_std_revision(self):
        changed = dict(HASHES, verified="f" * 64)
        with self.assertRaises(receipt.ReceiptError):
            render(make_gate(), hashes=changed)

    def test_different_binary_schema_profile_proof_infra_or_build_cannot_reuse(self):
        for key in ("verifier", "exporter", "schema"):
            with self.subTest(key=key), self.assertRaises(receipt.ReceiptError):
                render(make_gate(), hashes=dict(HASHES, **{key: "f" * 64}))
        for changes in (dict(profile="4" * 64), dict(proof="4" * 40),
                        dict(infra="4" * 40),
                        dict(build="66666666-2222-3333-4444-555555555555")):
            with self.subTest(changes=changes), self.assertRaises(receipt.ReceiptError):
                render(make_gate(), **changes)

    def test_missing_or_other_file_focus_cannot_publish(self):
        for focus in ("", "verified/lib.rs:0", "original/lib.rs:100", "../verified/lib.rs:100"):
            with self.subTest(focus=focus), self.assertRaises(receipt.ReceiptError):
                render(make_gate(), caller_focus=focus)

    def test_missing_source_pair_binding_cannot_publish(self):
        gate = fixtures.admission.A1Admission(INVENTORY, PINS, fixtures.IMPL_INPUTS,
                                         expected_case_manifest())
        for impl in INVENTORY:
            row = fixtures.implementation(impl)
            row.update(PINS, build_id=BUILD)
            row["inventory"] = [{"impl": name, **ids} for name, ids in INVENTORY.items()]
            row["compiler_identity"] = {"impl": impl, **INVENTORY[impl]}
            row["focused_item_id"] = INVENTORY[impl]["compiler_item_id"]
            gate.record_implementation(row)
        with self.assertRaises(receipt.ReceiptError):
            render(gate)

    def test_receipt_is_bounded_explicitly_runner_reported_and_complete(self):
        raw = render(make_gate())
        self.assertLessEqual(len(raw), 2048)
        self.assertEqual(len(raw.splitlines()), 18)
        self.assertIn("default_impl=10\ndefault_item=11\nfreeze_impl=20\nfreeze_item=21\n", raw)
        self.assertTrue(raw.endswith("assurance=runner-reported-both-actual-bodies-and-native-conformance\n"))


if __name__ == "__main__":
    unittest.main()
