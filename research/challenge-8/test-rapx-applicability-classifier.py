#!/usr/bin/env python3
"""Hosted-only replay and adversarial mutation of the six original RAPx logs.

Requires --evidence-dir pointing at the downloaded run37508888778 artifact's
rapx-applicability directory.  Mutations use temporary copies only.
"""
import argparse
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).with_name("classify-rapx-applicability.py")
spec = importlib.util.spec_from_file_location("rapx_classifier", SOURCE)
classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier)
EVIDENCE_DIR = None


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise AssertionError(f"Mutation anchor occurs {text.count(old)} time(s): {old!r}")
    return text.replace(old, new, 1)


def remove_line(text, needle):
    lines = text.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if needle in line]
    if len(matches) != 1:
        raise AssertionError(f"Line anchor occurs {len(matches)} time(s): {needle!r}")
    del lines[matches[0]]
    return "".join(lines)


def duplicate_line(text, needle):
    lines = text.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if needle in line]
    if len(matches) != 1:
        raise AssertionError(f"Line anchor occurs {len(matches)} time(s): {needle!r}")
    lines.insert(matches[0], lines[matches[0]])
    return "".join(lines)


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = {}
        for name in classifier.CASES:
            verify_path = EVIDENCE_DIR / f"{name}.log"
            contract_path = EVIDENCE_DIR / f"{name}-contracts.log"
            cls.original[name] = (verify_path.read_text(), contract_path.read_text())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)

    def replay(self, name="zst_source_misaligned", verify=None, contracts=None,
               exit_code=0, contract_exit_code=0):
        original_verify, original_contracts = self.original[name]
        verify_path = self.work / f"{name}-verify.log"
        contract_path = self.work / f"{name}-contracts.log"
        verify_path.write_text(original_verify if verify is None else verify)
        contract_path.write_text(original_contracts if contracts is None else contracts)
        return classifier.classify(name, exit_code, verify_path, contract_path,
                                   contract_exit_code)

    def reject(self, name="zst_source_misaligned", verify=None, contracts=None,
               expected=None, **kwargs):
        record = self.replay(name, verify, contracts, **kwargs)
        self.assertFalse(record["evidence_complete"], record)
        if expected:
            self.assertEqual(record["outcome"], expected, record)
        return record

    def test_authentic_six_case_replay_and_aggregate(self):
        records = [self.replay(name) for name in classifier.CASES]
        self.assertTrue(all(r["evidence_complete"] for r in records), records)
        self.assertEqual([r["outcome"] for r in records], [
            "PROVED_VALID", "SOUND_MISS", "SOUND_MISS", "PROVED_VALID",
            "INTENDED_ALIGN_DETECTION_WITH_OTHER_UNPROVED",
            "INTENDED_ALIGN_DETECTION_WITH_OTHER_UNPROVED",
        ])
        for record in records:
            with self.subTest(case=record["case"]):
                self.assertEqual(len(record["diagnostic"]["rows"]), 8)
                self.assertEqual([r["property"] for r in record["diagnostic"]["rows"]],
                                 list(range(8)))
                self.assertEqual([r["role"] for r in record["align_rows"]],
                                 ["Align(src,T)", "Align(dst,T)"])
                self.assertEqual(record["summary"]["path_description"],
                                 classifier.CASES[record["case"]][3])
        source = records[4]
        destination = records[5]
        self.assertEqual([r["property"] for r in source["other_failed_rows"]], [6])
        self.assertEqual([r["property"] for r in source["unknown_rows"]], [3])
        self.assertEqual(destination["other_failed_rows"], [])
        self.assertEqual([r["property"] for r in destination["unknown_rows"]], [5])
        aggregate = classifier.summarize(records)
        self.assertEqual(aggregate["gate_outcome"], "NO-GO")
        self.assertTrue(aggregate["commands_succeeded"])
        self.assertTrue(aggregate["evidence_parsed"])
        self.assertEqual(aggregate["primitive_result_counts"],
                         {"Proved": 43, "Failed": 3, "Unknown": 2})
        self.assertEqual(len(aggregate["records"]), 6)
        roundtrip = classifier.summarize(json.loads(json.dumps(records)))
        self.assertEqual(roundtrip["gate_outcome"], "NO-GO")
        self.assertTrue(roundtrip["evidence_parsed"])
        self.assertEqual(roundtrip["primitive_result_counts"], aggregate["primitive_result_counts"])

    def test_aggregate_rejects_missing_case_duplicate_case_and_unparsed_case(self):
        records = [self.replay(name) for name in classifier.CASES]
        self.assertEqual(classifier.summarize(records[:-1])["gate_outcome"], "NO-GO")
        self.assertFalse(classifier.summarize(records[:-1])["evidence_parsed"])
        doubled = records[:-1] + [records[0]]
        self.assertFalse(classifier.summarize(doubled)["evidence_parsed"])
        bad = dict(records[0], evidence_complete=False)
        self.assertEqual(classifier.summarize([bad] + records[1:])["gate_outcome"], "NO-GO")
        forged = dict(records[1], evidence_complete=False, outcome="SOUND_MISS")
        self.assertEqual(classifier.summarize([forged])["gate_outcome"], "INCONCLUSIVE")
        contradictory = dict(records[1], outcome="PROVED_VALID")
        self.assertFalse(classifier.summarize([records[0], contradictory] + records[2:])["evidence_parsed"])
        changed_summary = dict(records[1], summary=dict(records[1]["summary"], verdict="UNSOUND"))
        self.assertFalse(classifier.summarize([records[0], changed_summary] + records[2:])["evidence_parsed"])
        self.assertFalse(classifier.summarize([[]] + records[1:])["evidence_parsed"])
        bad = dict(records[0], raw_exit_code=2)
        self.assertFalse(classifier.summarize([bad] + records[1:])["commands_succeeded"])

    def test_only_std_and_core_copy_aliases_are_accepted(self):
        verify, contracts = self.original["zst_source_misaligned"]
        alias_contract = replace_once(contracts,
            "fn std::ptr::copy_nonoverlapping::<T>",
            "fn core::ptr::copy_nonoverlapping::<T>")
        alias_summary = replace_once(verify,
            "unsafe checkpoint: bb3 -> core::ptr::copy_nonoverlapping",
            "unsafe checkpoint: bb3 -> std::ptr::copy_nonoverlapping")
        self.assertEqual(self.replay(verify=alias_summary, contracts=alias_contract)["outcome"],
                         "SOUND_MISS")
        self.reject(contracts=replace_once(contracts,
                    "fn std::ptr::copy_nonoverlapping::<T>",
                    "fn alloc::ptr::copy_nonoverlapping::<T>"),
                    expected="CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED")
        self.reject(contracts=replace_once(contracts,
                    "fn std::ptr::copy_nonoverlapping::<T>(src: *const T, dst: *mut T, count: usize)",
                    "fn std::ptr::copy_nonoverlapping::<T>(dst: *mut T, src: *const T, count: usize)"),
                    expected="CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED")
        self.reject(verify=replace_once(verify,
                    "unsafe checkpoint: bb3 -> core::ptr::copy_nonoverlapping",
                    "unsafe checkpoint: bb3 -> alloc::ptr::copy_nonoverlapping"))

    def test_function_and_defid_contamination(self):
        verify, contracts = self.original["zst_source_misaligned"]
        self.reject(verify=replace_once(verify,
                    "[rapx::verify] function: zst::source_misaligned::copy",
                    "[rapx::verify] function: zst::destination_misaligned::copy"))
        self.reject(contracts=replace_once(contracts,
                    "fn zst::source_misaligned::copy",
                    "fn zst::destination_misaligned::copy"),
                    expected="CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED")
        self.reject(contracts=contracts + "\n00:00:00|RAPx|INFO|: fn foreign::copy\n",
                    expected="CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED")
        self.reject(verify=replace_once(verify,
                    "DefId(0:44 ~ rapx_applicability[e215]::zst::source_misaligned::copy)",
                    "DefId(0:45 ~ rapx_applicability[e215]::zst::destination_misaligned::copy)"))
        self.reject(verify=replace_once(verify, "DefId(0:44 ~", "DefId(0:99 ~"))
        self.reject(verify=duplicate_line(verify,
                    "[rapx::verify] function: zst::source_misaligned::copy"))

    def test_checkpoint_path_property_and_vm_binding(self):
        verify, _ = self.original["zst_source_misaligned"]
        self.reject(verify=replace_once(verify,
                    "check #0: checkpoint #0, bb3, path #0, property #0 Some(Align)",
                    "check #0: checkpoint #1, bb3, path #0, property #0 Some(Align)"))
        self.reject(verify=replace_once(verify,
                    "check #0: checkpoint #0, bb3, path #0, property #0 Some(Align)",
                    "check #0: checkpoint #0, bb4, path #0, property #0 Some(Align)"))
        self.reject(verify=replace_once(verify,
                    "check #0: checkpoint #0, bb3, path #0, property #0 Some(Align)",
                    "check #0: checkpoint #0, bb3, path #1, property #0 Some(Align)"))
        self.reject(verify=replace_once(verify,
                    "property #0 Some(Align), result Proved",
                    "property #1 Some(Align), result Proved"))
        self.reject(verify=replace_once(verify,
                    "property #0 Some(Align), result Proved",
                    "property #0 Some(NonNull), result Proved"))
        self.reject(verify=replace_once(verify,
                    "unsafe checkpoint: bb3 -> core::ptr::copy_nonoverlapping",
                    "unsafe checkpoint: bb4 -> core::ptr::copy_nonoverlapping"))
        self.reject(verify=replace_once(verify,
                    "path [0, 5, 1, 2, 6, 3]:",
                    "path [0, 5, 1, 2, 6, 4]:"))
        self.reject(verify=replace_once(verify,
                    "check #0: checkpoint #0, bb3, path #0, property #0 Some(Align), result Proved\nvm-check: ProvedByRule",
                    "check #0: checkpoint #0, bb3, path #0, property #0 Some(Align), result Proved\nvm-check: Failed"))

    def test_missing_duplicate_extra_unparsed_diagnostic_rows(self):
        verify, _ = self.original["zst_source_misaligned"]
        self.reject(verify=remove_line(verify, "check #0: checkpoint #0"))
        self.reject(verify=duplicate_line(verify, "check #0: checkpoint #0"))
        self.reject(verify=replace_once(verify, "check #0: checkpoint #0",
                                         "CHECK #0: checkpoint #0"))
        self.reject(verify=replace_once(verify,
                    "check #0: checkpoint #0, bb3, path #0, property #0 Some(Align), result Proved\nvm-check: ProvedByRule",
                    "check #0: checkpoint #0, bb3, path #0, property #0 Some(Align), result Proved\nvm_check: ProvedByRule"))
        self.reject(verify=duplicate_line(verify,
                    "[rapx::verify::diagnostics] function DefId(0:44"))

    def test_src_dst_contract_and_summary_cannot_be_swapped(self):
        verify, contracts = self.original["zst_source_misaligned"]
        self.reject(contracts=replace_once(contracts,
                    "|- Align(src, T)", "|- Align(dst, T)"),
                    expected="CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED")
        self.reject(contracts=remove_line(contracts, "|- Align(src, T)"),
                    expected="CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED")
        self.reject(verify=remove_line(verify, "Align | Proved (x2)"))
        self.reject(verify=replace_once(verify,
                    "Align | Proved (x2)", "Align | Failed (x2)"))
        self.reject(verify=replace_once(verify,
                    "result: SOUND", "result: UNSOUND (0 unproved, 0 hazard)"))
        self.reject(verify=remove_line(verify, "result: SOUND"))
        self.reject(verify=verify + "\n00:00:00|RAPx|INFO|:       unsafe checkpoint: bb3 -> core::ptr::copy_nonoverlapping\n")
        self.reject(verify=verify + "\n00:00:00|RAPx|INFO|:   result: SOUND\n")

    def test_unknown_and_other_failed_are_preserved_not_green(self):
        source = self.replay("u64_source_misaligned")
        destination = self.replay("u64_destination_misaligned")
        for record in (source, destination):
            self.assertTrue(record["evidence_complete"])
            self.assertEqual(record["targeted_align_status"], "FAILED_EXPECTED_ALIGN")
            self.assertEqual(record["outcome"],
                             "INTENDED_ALIGN_DETECTION_WITH_OTHER_UNPROVED")
            self.assertTrue(record["unknown_rows"])
        self.assertFalse(classifier.summarize([
            self.replay(name) for name in classifier.CASES if name not in
            ("zst_source_misaligned", "zst_destination_misaligned")
        ])["evidence_parsed"])

    def test_warnings_unsupported_command_failure_and_print_only(self):
        verify, contracts = self.original["zst_source_misaligned"]
        self.reject(verify=verify + "\n00:00:00|RAPx|WARN|: unsupported operation\n",
                    expected="UNSUPPORTED_OPERATION")
        self.reject(verify=verify + "\n00:00:00|RAPx|WARN|: Skipping target after panic\n",
                    expected="UNEXPECTED_WARNING")
        self.reject(verify=contracts)
        self.reject(exit_code=124, expected="TIMEOUT")
        self.reject(exit_code=2, expected="COMMAND_FAILURE")
        self.reject(contract_exit_code=2, expected="COMMAND_FAILURE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args, remaining = parser.parse_known_args()
    EVIDENCE_DIR = args.evidence_dir
    unittest.main(argv=[sys.argv[0], *remaining])
