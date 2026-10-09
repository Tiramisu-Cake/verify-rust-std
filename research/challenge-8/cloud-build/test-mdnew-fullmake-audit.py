#!/usr/bin/env python3
"""Isolated classifier checks against GNUmakefile's observed echo spacing."""
import importlib.util,unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('mdnew_fullmake_audit',Path(__file__).with_name('mdnew-fullmake-audit.py'))
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)

class MakeOutputTest(unittest.TestCase):
 def test_completed_make_echo_and_mysh_summary(self):
  # `echo "  MYSH     " testsuite` in GNUmakefile adds an argument separator.
  output='  MYSH      assignments/run_model_solutions\n  RUN  json_tests\n  MYSH      testsuite\n0 failed processes\n'
  audit.verify_make_completion(output)
 def test_missing_root_completion(self):
  with self.assertRaisesRegex(audit.Failure,'root and assignments'):
   audit.verify_make_completion('  MYSH      assignments/run_model_solutions\n0 failed processes\n')
 def test_failed_summary(self):
  with self.assertRaisesRegex(audit.Failure,'zero-failed'):
   audit.verify_make_completion('  MYSH      assignments/run_model_solutions\n  MYSH      testsuite\n1 failed processes\n')

if __name__=='__main__':unittest.main()
