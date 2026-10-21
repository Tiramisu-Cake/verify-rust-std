"""Synthetic controls for the source-stage negative body-entry attestation."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "a1_body_entry_context_test_runner", HERE / "a1-runner.py")
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)

ERROR = "verified/lib.rs(44,1): error: Cannot prove result<=32"
ALIASES = {
    "default16": "__a1_impl_12_34_small_sort_threshold",
    "freeze32": "__a1_impl_21_22_small_sort_threshold",
}
DEFAULT_ALIAS = object()


def body_note(alias: str, line: int = 15) -> str:
    return (f"verified/lib.rs({line},1-18,1): note: "
            f"Verifying function '{alias}'")


def header_note(alias: str, line: int = 15) -> str:
    return (f"verified/lib.rs({line},1-18,1): note: Function '{alias}': "
            "Function prototype implementation check")


class BodyEntryContextTests(unittest.TestCase):
    def check(self, log: str, *, alias=DEFAULT_ALIAS,
              body_line=15, first_error: str = ERROR):
        return RUNNER.body_entry_context(
            log, first_error,
            alias=(ALIASES["default16"] if alias is DEFAULT_ALIAS else alias),
            body_line=body_line)

    def test_exact_post_error_body_frame_for_default_and_freeze_aliases(self):
        for alias in ALIASES.values():
            with self.subTest(alias=alias):
                self.assertTrue(self.check(ERROR + "\n" + body_note(alias) + "\n",
                                           alias=alias))

    def test_header_only_missing_wrong_alias_and_wrong_line_refuse(self):
        alias = ALIASES["default16"]
        self.assertFalse(self.check(ERROR + "\n" + header_note(alias) + "\n"))
        self.assertFalse(self.check(ERROR + "\n"))
        self.assertFalse(self.check(ERROR + "\n" + body_note("other") + "\n"))
        self.assertFalse(self.check(ERROR + "\n" + body_note(alias, line=16) + "\n"))

    def test_duplicate_body_frames_multiple_errors_and_prior_note_refuse(self):
        alias = ALIASES["default16"]
        note = body_note(alias)
        self.assertFalse(self.check(ERROR + "\n" + note + "\n" + note + "\n"))
        self.assertFalse(self.check("error: earlier\n" + ERROR + "\n" + note + "\n"))
        self.assertFalse(self.check(note + "\n" + ERROR + "\n"))

    def test_exact_first_error_and_metadata_are_required(self):
        alias = ALIASES["freeze32"]
        self.assertFalse(self.check(ERROR + "\n" + body_note(alias) + "\n",
                                    alias=alias, first_error="other error"))
        for first_error, bad_alias, body_line in (
                (None, alias, 15), (ERROR, None, 15),
                (ERROR, alias, 0), (ERROR, alias, "15")):
            with self.subTest(first_error=first_error, alias=bad_alias,
                              body_line=body_line):
                with self.assertRaises(RuntimeError):
                    self.check(ERROR + "\n" + body_note(alias) + "\n",
                               alias=bad_alias, body_line=body_line,
                               first_error=first_error)

    def test_negative_candidate_can_receive_nonproof_execution_attestation(self):
        alias = ALIASES["default16"]
        candidate = {
            "candidate_passed": True,
            "classification": "INTENDED_FOCUSED_FAILURE_CANDIDATE",
            "proof_credit": False,
            "body_verified": False,
            "first_error": ERROR,
            "error_context": {"stage": "impl-body",
                              "body_frame_observed": True,
                              "header_frame_observed": False},
        }
        structure = {
            "bound_impls": {"default16": {
                "compiler_impl_id": "impl-12", "compiler_item_id": "item-34",
                "source_line": 15}},
            "threshold_posts": {"impls": {"default16": {
                "alias": alias, "compiler_impl_id": "impl-12",
                "compiler_item_id": "item-34"}}},
        }
        raw = {"focus_source_line": 12, "focus": "verified/lib.rs:12",
               "compiler_item_identity_observed": {"compiler_item_id": "item-34"}}
        interval = {"body_count_from_intervals": 1, "focus_line": 12,
                    "selected": {"name": alias}}
        with patch.object(RUNNER, "FOCUS_SEMANTICS_PINS", {}):
            receipt = RUNNER.attest_focused_execution(
                "N-default-contract", tool=HERE, profile={
                    "a1_focus_semantics_sha256": {}}, raw=raw,
                structure=structure, interval=interval, candidate=candidate,
                verifier_log=ERROR + "\n" + body_note(alias) + "\n")
        self.assertEqual(receipt["classification"],
                         "RUNNER_REPORTED_FOCUSED_BODY_AND_CONFORMANCE")
        self.assertTrue(receipt["focus_body_reached"])
        self.assertFalse(receipt["focus_body_verified"])
        self.assertTrue(receipt["focus_conformance_verified"])
        self.assertFalse(receipt["proof_credit"])


if __name__ == "__main__":
    unittest.main()
