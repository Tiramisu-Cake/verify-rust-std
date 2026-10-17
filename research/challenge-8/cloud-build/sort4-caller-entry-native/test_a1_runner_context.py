"""Isolated synthetic tests for the pinned focused-error context parser."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).with_name("a1-runner.py")
SPEC = importlib.util.spec_from_file_location("a1_runner_context_test", PATH)
assert SPEC is not None and SPEC.loader is not None
RUNNER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)

ERROR = "verified/lib.rs(12,3): error: Cannot prove result<=32"
ALIAS = "__a1_impl_12_34_small_sort_threshold"
BODY = "verified/lib.rs(15,1-18,1): note: Verifying function '" + ALIAS + "'"
HEADER = ("verified/lib.rs(15,1-18,1): note: Function '" + ALIAS +
          "': Function prototype implementation check")


class SyntheticContext(unittest.TestCase):
    def check(self, text: str) -> bool:
        return RUNNER.body_entry_context(text, ERROR, alias=ALIAS, body_line=15)

    def test_body_entry_after_first_error(self):
        self.assertTrue(self.check(ERROR + "\n12 | return 33;\n" + BODY + "\n"))

    def test_header_only_is_not_body(self):
        self.assertFalse(self.check(ERROR + "\n" + HEADER + "\n"))

    def test_wrong_line_or_alias_is_not_body(self):
        self.assertFalse(self.check(ERROR + "\n" + BODY.replace("(15,", "(16,") + "\n"))
        self.assertFalse(self.check(ERROR + "\n" + BODY.replace(ALIAS, "other") + "\n"))

    def test_duplicate_or_prior_errors_refused(self):
        self.assertFalse(self.check(ERROR + "\n" + BODY + "\n" + BODY + "\n"))
        self.assertFalse(self.check("error: earlier\n" + ERROR + "\n" + BODY + "\n"))


if __name__ == "__main__":
    unittest.main()
