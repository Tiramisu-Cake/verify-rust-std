#!/usr/bin/env python3
"""Small synthetic campaign capture-policy tests; no proof/toolchain execution."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r23_capture_callback', HERE/'first-callback.py')
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)

class CapturePolicyTests(unittest.TestCase):
    def test_legacy_absence_preserves_prior_opt_in(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(m._owned_nll_capture_allowed(Path(d)))

    def test_r23_policy_absence_fails_before_execution(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/m.R23_LEDGER_NAME).write_text('{}')
            with self.assertRaises(RuntimeError): m._owned_nll_capture_allowed(root)

    def test_exact_policy_disables_capture_without_env_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/m.R23_CAPTURE_POLICY_NAME).write_text(json.dumps(m.R23_CAPTURE_POLICY))
            self.assertFalse(m._owned_nll_capture_allowed(root))
        env={m.VF_EXPORT_OWNED_NLL_FACTS:'1'}
        self.assertNotIn(m.VF_EXPORT_OWNED_NLL_FACTS,m._campaign_environment(env))
        self.assertEqual(env,{m.VF_EXPORT_OWNED_NLL_FACTS:'1'})

    def test_corrupt_policy_cannot_enable_a_third_capture(self):
        values=[None, [], 'false', True, {}]
        for key,value in [('phase_id','OLD'),('completed_capture_cycles',1),
                          ('completed_capture_cycles',3),('completed_capture_cycles',True),
                          ('completed_capture_cycles','2'),('owned_nll_capture_enabled',True),
                          ('owned_nll_capture_enabled',0),('mode','capture')]:
            row=copy.deepcopy(m.R23_CAPTURE_POLICY); row[key]=value; values.append(row)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); p=root/m.R23_CAPTURE_POLICY_NAME
            for value in values:
                p.write_text(json.dumps(value))
                with self.subTest(value=value), self.assertRaises(RuntimeError):
                    m._owned_nll_capture_allowed(root)
            p.write_text('{')
            with self.assertRaises(RuntimeError): m._owned_nll_capture_allowed(root)

    def test_directory_and_symlink_policy_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); p=root/m.R23_CAPTURE_POLICY_NAME;p.mkdir()
            with self.assertRaises(RuntimeError):m._owned_nll_capture_allowed(root)
            p.rmdir();other=root/'other';other.write_text(json.dumps(m.R23_CAPTURE_POLICY));p.symlink_to(other)
            with self.assertRaises(RuntimeError):m._owned_nll_capture_allowed(root)

if __name__=='__main__':unittest.main()
