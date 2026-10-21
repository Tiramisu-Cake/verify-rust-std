"""Run existing isolated service controls against the new R16 body adapter.

Only hand-written fake source-support/stage objects are used. No construction,
compiler, exporter, refiner or verifier runs on the VPS.
"""
from pathlib import Path

_original_tests = Path(__file__).with_name('test_a1_actual_body_service.py')
_test_source = _original_tests.read_text().replace(
    'HERE / "a1-actual-body.py"', 'HERE / "a1-actual-body-r16.py"')
exec(compile(_test_source, str(_original_tests), 'exec'))

import json

class R16AdditionalStageControls(unittest.TestCase):
    def run_synthetic(self, c4):
        harness = ActualBodyServiceTests()
        with tempfile.TemporaryDirectory() as temp:
            row = harness.run_case(temp, c4)
            persisted = json.loads((Path(temp) / 'synthetic-body/body-result.json').read_text())
        self.assertEqual(json.loads(json.dumps(row)), persisted)
        self.assertFalse(row['proof_credit'])
        return row

    def test_null_missing_wrong_type_support_preserves_error_snapshot(self):
        class Malformed(FakeC4):
            def source_support(self, *args, **kwargs):
                return {}, self.value
        for value in (None, [], 'bad', {}, {'paired_support_passed': None},
                      {'paired_support_passed': 'true'}):
            with self.subTest(value=value):
                c4 = Malformed()
                c4.value = value
                row = self.run_synthetic(c4)
                self.assertFalse(row['passed'])
                self.assertNotIn('verification', row)
                self.assertEqual(c4.stage_calls, 0)
                self.assertEqual(row['source_support'], value)

    def test_timeout_partial_explicit_not_run_preserve_original_stage(self):
        class TerminalVariant(FakeC4):
            def stage(self, *args, **kwargs):
                normal = super().stage(*args, **kwargs)
                return {**normal, **self.variant}
        for variant in ({'exit': 124}, {'classification': 'TIMEOUT', 'exit': 124},
                        {'classification': 'NOT_RUN', 'exit': None},
                        {'classification': 'PARTIAL', 'exit': None},
                        {'exit': '0'}, {'exit': None}):
            with self.subTest(variant=variant):
                c4 = TerminalVariant()
                c4.variant = variant
                row = self.run_synthetic(c4)
                self.assertFalse(row['passed'])
                for key, value in variant.items():
                    self.assertEqual(row['verification'][key], value)

    def test_source_support_exception_preserves_original_exception(self):
        class Broken(FakeC4):
            def source_support(self, *args, **kwargs):
                raise ValueError('synthetic original source-stage exception')
        row = self.run_synthetic(Broken())
        self.assertEqual(row['error'], 'ValueError: synthetic original source-stage exception')
        self.assertFalse(row['passed'])
        self.assertNotIn('verification', row)

    def test_wrong_target_selection_cannot_close_obligation(self):
        stage = {'classification': 'TERMINAL', 'exit': 0,
                 'log_sha256': sha(b'complete\n')}
        for selected in ('wrong-target', None):
            row = BODY.classify(stage, b'complete\n', selection={
                'classification': 'SOURCE_BOUND_FULL_BODY_INTERVAL',
                'name': selected, 'body_count_from_intervals': 1},
                paired=True, immutable=True, expected_name='synthetic-body')
            self.assertFalse(row['passed'])
