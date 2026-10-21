"""Isolated R14 phase and P1 receipt identity checks; no proof pipeline."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent

def load(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

RUNNER = load('r14_pin_runner', 'a1-runner.py')
RECEIPTS = load('r14_pin_receipts', 'a1-summary-receipt.py')

class P1Identity(unittest.TestCase):
    def test_final_receipt_and_source_profile_pins_are_not_interchangeable(self):
        receipt = dict(classification='A1_TOOL_BUILT_UNRUN_PROOF', phase_id=RUNNER.PHASE,
                       build_exit=0, proof_credit=False, console_binary_sha256='1' * 64,
                       exporter_binary_sha256='2' * 64, final_schema_sha256='3' * 64)
        env = dict(SORT4_A1_PROFILE_SHA256='4' * 64, PROOF_SHA='5' * 40, INFRA_SHA='6' * 40)
        result = RUNNER.p1_run_identity(receipt, RECEIPTS, env)
        self.assertEqual(set(result), {'tool_id','profile_id','proof_id','infra_id','target_id'})
        self.assertEqual(result['profile_id'], env['SORT4_A1_PROFILE_SHA256'])
        self.assertEqual(result['tool_id'], RECEIPTS.tool_id(
            dict(verifier='1' * 64, exporter='2' * 64, schema='3' * 64)))
        for key in ('console_binary_sha256', 'exporter_binary_sha256', 'final_schema_sha256'):
            self.assertNotEqual(RUNNER.p1_run_identity(dict(receipt, **{key:'a' * 64}), RECEIPTS, env)['tool_id'], result['tool_id'])
        for key in receipt:
            for bad in (None, True if key == 'proof_credit' else False, 'wrong'):
                with self.subTest(key=key, value=bad), self.assertRaises(RuntimeError):
                    RUNNER.p1_run_identity(dict(receipt, **{key:bad}), RECEIPTS, env)
        for key in env:
            for bad in (None, False, 'wrong', 'f' * (40 if key == 'SORT4_A1_PROFILE_SHA256' else 64)):
                with self.subTest(key=key, value=bad), self.assertRaises(RuntimeError):
                    RUNNER.p1_run_identity(receipt, RECEIPTS, dict(env, **{key:bad}))

if __name__ == '__main__':
    unittest.main()
