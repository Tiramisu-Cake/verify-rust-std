#!/usr/bin/env python3
"""Hosted-only acceptance/rejection checks for the pinned RAPx renderer format.

Run on GitHub-hosted Actions, never on the editing server.  Samples follow
rapx-0.7.50/src/verify/{driver,report,display}.rs debug-contracts and report
formats; the real six-case run remains the evidence for actual detector behavior.
"""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).with_name("classify-rapx-applicability.py")
spec = importlib.util.spec_from_file_location("rapx_classifier", SOURCE)
classifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(classifier)


def log_line(message, level="INFO"):
    return f"2026-10-06T00:00:00Z|RAPx|{level}|: {message}"


def contract(target):
    # driver.rs::print_target_contracts, then fmt_contract_expanded for the
    # six JSON primitives of core::ptr::copy_nonoverlapping.
    return "\n".join([
        log_line("[rapx::debug-contracts] Expanded Contract Assertions"),
        log_line("-  --- method: copy -----------------------------------------"),
        log_line(f"  fn {target}"),
        log_line("  [Unsafe Callees]:"),
        log_line("  `- fn core::ptr::copy_nonoverlapping::<T>(src: *const T, dst: *mut T, count: usize)"),
        log_line("    |- Align(src, T)"),
        log_line("    |- Align(dst, T)"),
        log_line("    |- ValidPtr(src, T, count)"),
        log_line("    |- ValidPtr(dst, T, count)"),
        log_line("    |- NonOverlap(dst, src, T, count)"),
        log_line("    `- ValidNum(size_of(T) * count <= isize::MAX)"),
        "",
    ])


def verification(target, failed=None, paths=1, bb=3, verdict=None,
                 vm_proved="ProvedByRule", other_failed=None, unknown=None):
    # report.describe() is one rap_debug! call with lines following the header;
    # display.rs then prints one final function/checkpoint/path/verdict summary.
    defid_path = target.replace("rapx_applicability::", "rapx_applicability[1234]::", 1)
    rows = [log_line(f"[rapx::verify::diagnostics] function DefId(0:17 ~ {defid_path}): {6 * paths} check item(s)", "DEBUG")]
    for prop in range(6):
        for path in range(paths):
            check = prop * paths + path
            result = "Unknown" if prop == unknown else "Failed" if prop in (failed, other_failed) else "Proved"
            vm = result if result in ("Unknown", "Failed") else vm_proved
            rows.append(f"  check #{check}: checkpoint #0, bb{bb}, path #{path}, property #{prop} Some({classifier.KINDS[prop]}), result {result}")
            rows.append(f"vm-check: {vm}")
    if verdict is None:
        verdict = "UNSOUND" if failed is not None else "SOUND"
    rows.extend([log_line("============================================================"),
                 log_line(f"[rapx::verify] function: {target}"),
                 log_line("============================================================"),
                 log_line("  --- unsafe checkpoints ---"),
                 log_line(f"      unsafe checkpoint: bb{bb} -> core::ptr::copy_nonoverlapping::<T>")])
    for path in range(paths):
        rows.append(log_line(f"        path bb0, bb{bb}, path{path}:"))
        if unknown in (0, 1):
            rows.append(log_line("          ├── Align | Unknown", "WARN"))
            rows.append(log_line("          ├── Align | Proved"))
        elif failed is None:
            rows.append(log_line("          ├── Align | Proved (x2)"))
        else:
            rows.append(log_line("          ├── Align | Failed", "WARN"))
            rows.append(log_line("          ├── Align | Proved"))
        if other_failed == 2 or other_failed == 3:
            rows.append(log_line("          ├── ValidPtr | Failed", "WARN"))
            rows.append(log_line("          ├── ValidPtr | Proved"))
        else:
            rows.append(log_line("          ├── ValidPtr | Proved (x2)"))
        for kind in ("NonOverlap", "ValidNum"):
            rows.append(log_line(f"          ├── {kind} | Proved"))
    rows.append(log_line(f"  result: {verdict} (1 unproved, 0 hazard)" if verdict == "UNSOUND"
                         else f"  result: {verdict}", "WARN" if verdict == "UNSOUND" else "INFO"))
    return "\n".join(rows) + "\n"


class ClassifierTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.name = "zst_source_misaligned"
        self.target = "rapx_applicability::zst::source_misaligned::copy"
        self.contract_text = contract(self.target)
        self.verify_text = verification(self.target, failed=0)

    def classify(self, name=None, verify=None, contracts=None, exit_code=0,
                 contract_exit_code=0, same_file=False):
        name = name or self.name
        vpath = self.base / "verify.log"
        cpath = vpath if same_file else self.base / "contracts.log"
        vpath.write_text(self.verify_text if verify is None else verify)
        if not same_file:
            cpath.write_text(self.contract_text if contracts is None else contracts)
        return classifier.classify(name, exit_code, vpath, cpath, contract_exit_code)

    def outcome(self, expected, **kwargs):
        record = self.classify(**kwargs)
        self.assertEqual(record["outcome"], expected, record)
        return record

    def test_all_six_fixture_names_have_their_own_target_and_align_mapping(self):
        for name, (expectation, module, bad_arg) in classifier.CASES.items():
            with self.subTest(name=name):
                target = f"rapx_applicability::{module}::copy"
                failed = None if expectation == "positive" else (0 if bad_arg == "src" else 1)
                self.outcome("PROVED_VALID" if failed is None else "INTENDED_DETECTION",
                             name=name, contracts=contract(target),
                             verify=verification(target, failed=failed))

    def test_multiple_paths_and_smt_proofs(self):
        record = self.outcome("INTENDED_DETECTION", verify=verification(
            self.target, failed=0, paths=2, vm_proved="ProvedBySmt"))
        self.assertEqual(record["path_count"], 2)
        self.assertEqual(len(record["align_rows"]), 4)

    def test_aligned_obligation_detection_survives_derived_validptr_failure(self):
        record = self.outcome("INTENDED_DETECTION", verify=verification(
            self.target, failed=0, other_failed=2))
        self.assertEqual(len(record["other_failed_rows"]), 1)

    def test_sound_miss_is_distinct_from_detection(self):
        self.outcome("SOUND_MISS", verify=verification(self.target))

    def test_debug_contracts_only_never_counts_as_verification(self):
        self.outcome("MISSING_TARGET_OR_CHECKPOINT", verify=self.contract_text)
        self.outcome("MISSING_LOG", same_file=True)

    def test_wrong_function_or_contract_cannot_be_borrowed(self):
        other = "rapx_applicability::u64_controls::source_misaligned::copy"
        self.outcome("MISSING_TARGET_OR_CHECKPOINT", verify=verification(other, failed=0))
        self.outcome("CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED", contracts=contract(other))
        self.outcome("MISSING_TARGET_OR_CHECKPOINT",
                     verify=self.verify_text + verification(other, failed=0))
        wrong_defid = self.verify_text.replace(
            "rapx_applicability[1234]::zst::source_misaligned::copy",
            "rapx_applicability[1234]::u64_controls::source_misaligned::copy")
        self.outcome("MISSING_OR_UNPARSEABLE_OBLIGATION", verify=wrong_defid)

    def test_wrong_checkpoint_cannot_be_borrowed(self):
        self.outcome("MISSING_OR_UNPARSEABLE_OBLIGATION",
                     verify=self.verify_text.replace("checkpoint #0, bb3", "checkpoint #1, bb3"))
        self.outcome("MISSING_OR_UNPARSEABLE_OBLIGATION",
                     verify=self.verify_text.replace("checkpoint #0, bb3", "checkpoint #0, bb4"))
        self.outcome("MISSING_OR_UNPARSEABLE_OBLIGATION",
                     verify=self.verify_text.replace("unsafe checkpoint: bb3", "unsafe checkpoint: bb4"))

    def test_missing_duplicate_and_wrong_property_rows_fail_closed(self):
        line = "  check #0: checkpoint #0, bb3, path #0, property #0 Some(Align), result Failed\nvm-check: Failed\n"
        self.outcome("MISSING_OR_UNPARSEABLE_OBLIGATION", verify=self.verify_text.replace(line, ""))
        self.outcome("MISSING_OR_UNPARSEABLE_OBLIGATION", verify=self.verify_text.replace(line, line + line))
        self.outcome("CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED",
                     verify=self.verify_text.replace("property #0 Some(Align)", "property #0 Some(ValidPtr)"))
        self.outcome("MISSING_OR_UNPARSEABLE_OBLIGATION",
                     verify=self.verify_text.replace("path #0, property #0", "path #1, property #0"))
        self.outcome("MISSING_OR_UNPARSEABLE_OBLIGATION",
                     verify=self.verify_text.replace("vm-check: Failed", "vm-check: ProvedByRule"))
        self.outcome("SUMMARY_DIAGNOSTIC_MISMATCH",
                     verify=self.verify_text.replace("          ├── ValidPtr | Proved (x2)\n", ""))

    def test_missing_contract_primitive_fails_closed(self):
        self.outcome("CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED",
                     contracts=self.contract_text.replace("    |- Align(src, T)\n", ""))
        self.outcome("CONTRACT_EVIDENCE_MISSING_OR_UNMAPPED",
                     contracts=self.contract_text.replace("Align(src, T)", "Align(dst, T)"))
        self.outcome("MISSING_LOG", contracts="")

    def test_unknown_unsupported_warning_and_command_failure_are_distinct(self):
        self.outcome("UNKNOWN", verify=verification(
            self.target, failed=None, unknown=0, verdict="UNSOUND"))
        self.outcome("UNSUPPORTED_OPERATION", verify=self.verify_text + log_line("unsupported operation: foo", "WARN"))
        self.outcome("UNEXPECTED_WARNING", verify=self.verify_text + log_line("Skipping function after panic", "WARN"))
        self.outcome("COMMAND_FAILURE", exit_code=2)
        self.outcome("CONTRACT_COMMAND_FAILURE", contract_exit_code=2)
        self.outcome("TIMEOUT", exit_code=124)

    def test_unrelated_failure_is_not_intended_detection(self):
        self.outcome("UNRELATED_FAILURE", verify=verification(self.target, failed=1))
        self.outcome("UNRELATED_FAILURE", verify=verification(self.target, failed=0, verdict="SOUND"))
        self.outcome("ALIGN_PROVED_OTHER_FAILURE", verify=verification(
            self.target, failed=None, other_failed=2, verdict="UNSOUND"))

    def test_ansi_and_rapx_prefix_are_removed(self):
        ansi = self.verify_text.replace("Align | Failed", "\x1b[31mAlign | Failed\x1b[0m")
        self.outcome("INTENDED_DETECTION", verify=ansi)


if __name__ == "__main__":
    unittest.main()
