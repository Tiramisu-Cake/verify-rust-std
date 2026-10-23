"""Static R23 source/row/transport bindings; no actual proof tooling."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[3]
HIST = ROOT / 'research/challenge-8/task-history/select-callee-r23'
CLOUD = ROOT / 'research/challenge-8/cloud-build'
PATCHES = ROOT / 'research/challenge-8/overnight-assume-actual'


class R23Pins(unittest.TestCase):
    def test_strict_consumer_accepts_all_fresh_rows(self):
        spec = importlib.util.spec_from_file_location('r23_pin_consumer', CLOUD / 'select-callee-r21-fractional-proof.py')
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        record = json.loads((HIST / 'FRACTIONAL-FINGERPRINT-INPUT.json').read_text())
        pins = m.fingerprint_to_pins(record)
        self.assertIs(m.validate_pins(pins), pins)
        patch = (PATCHES / 'verifast-r23-fractional-forget-26.10.patch').read_text()
        for name, row in pins['cases'].items():
            expected = '("%s", "%s", "%s", "%s", "%s")' % (name, row['verified_sha256'], row['snapshots']['body-6']['sha256'], row['snapshots']['body-7']['sha256'], row['snapshots']['unit']['sha256'])
            self.assertEqual(patch.count(expected), 1)

    def test_patch_changes_only_reviewed_r22b_rows(self):
        record = json.loads((HIST / 'FRACTIONAL-FINGERPRINT-INPUT.json').read_text())
        mask = r'^\+      \("(?:' + '|'.join(re.escape(k) for k in record['variants']) + r')",.*$'
        before = (PATCHES / 'verifast-r22b-fractional-forget-26.10.patch').read_text()
        after = (PATCHES / 'verifast-r23-fractional-forget-26.10.patch').read_text()
        self.assertEqual(re.sub(mask, 'ROW', before, flags=re.M), re.sub(mask, 'ROW', after, flags=re.M))

    def test_runner_and_recipe_bind_fresh_proof_inputs(self):
        pins = json.loads((HIST / 'PROOF-PINS.json').read_text())
        raw = (ROOT / pins['patch']).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), pins['patch_sha256'])
        runner = (CLOUD / 'run-o26-select-callee-r20.sh').read_text()
        self.assertIn(pins['patch_sha256'], runner)
        self.assertEqual(runner.count(pins['translator_sha256']), 1)
        cfg = json.loads((HIST / 'CFG-PROOF-PINS.json').read_text())
        self.assertEqual(hashlib.sha256((ROOT / cfg['patch']).read_bytes()).hexdigest(), cfg['patch_sha256'])
        self.assertEqual(runner.count(cfg['translator_sha256']), 2)
        self.assertIn(cfg['patch_sha256'], runner)
        self.assertIn('stage r21-fractional-proof python3', runner)
        self.assertNotIn('stage r21-fractional-fingerprint ', runner)
        self.assertIn('select-callee-r21-proof-audit.py', runner)
        recipe = json.loads((CLOUD / 'recipes/o26-select-callee-r20.json').read_text())
        self.assertIn(pins['patch'], recipe['proof_paths'])
        self.assertIn('research/challenge-8/task-history/select-callee-r23/FRACTIONAL-FINGERPRINT-INPUT.json', recipe['proof_paths'])

    def test_receipt_retains_actual_reader_and_brief_identity(self):
        receipt = json.loads((HIST / 'FINGERPRINT-739F982D-READ.json').read_text())
        observed = json.loads((HIST / 'FINGERPRINT-739F982D-ROOT.json').read_text())
        for key, value in receipt['identity'].items():
            self.assertEqual(value, observed[key])
        self.assertEqual(receipt['reader_execution_commit'], '395533a54da8495af70ae68e9e5425a10e3d2e84')
        self.assertIs(receipt['execution_is_later_reviewed_revision'], False)
        self.assertEqual(len(receipt['requests']), 166)
        self.assertLess(receipt['post_validation']['maximum_string_codepoints'], 512)


if __name__ == '__main__':
    unittest.main()
