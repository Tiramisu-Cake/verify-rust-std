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

class R16ScopeRouteControls(unittest.TestCase):
    def test_scope_opt_in_is_source_bound_and_negative_switch_is_separate(self):
        case = ActualBodyServiceTests().make_case()
        base = dict(case[3], actual_c1_recovery=True,
                    generated_source_sha256=sha(case[1]), first_comparator_line=7,
                    actual_scope_relocation=True)
        for control, expected in ((None, '1'), ('scope-opt-in-off', '0')):
            c4 = FakeC4(support=False)
            meta = dict(base, **({'frontend_control': control} if control else {}))
            env = {'preserved': 'yes'}
            with tempfile.TemporaryDirectory() as temp:
                result = BODY.run_case(None, c4, Path('/synthetic/tool'), env, Path(temp),
                    (*case[:3], meta), FakeGates(), FakeGrammar({}), {'tool_hashes': {}})
            self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_SCOPE_RELOCATION'], expected)
            self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_C1_RECOVERY'], '1')
            self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_SOURCE_SHA256'], sha(case[1]))
            self.assertEqual(env, {'preserved': 'yes'})
            self.assertEqual(c4.stage_calls, 0)
            self.assertFalse(result['proof_credit'])

    def test_scope_opt_in_without_actual_source_metadata_refuses(self):
        case = ActualBodyServiceTests().make_case()
        c4 = FakeC4()
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(RuntimeError):
            BODY.run_case(None, c4, Path('/synthetic/tool'), {}, Path(temp),
                (*case[:3], dict(case[3], actual_scope_relocation=True)),
                FakeGates(), FakeGrammar({}), {'tool_hashes': {}})
        self.assertEqual(c4.source_support_targets, [])

class R16HrtbOutputRouteControls(unittest.TestCase):
    def make_target_case(self, **metadata):
        base = ActualBodyServiceTests().make_case()
        meta = dict(base[3], name='sort4_stable', actual_c1_recovery=True,
                    generated_source_sha256=sha(base[1]), first_comparator_line=7,
                    actual_scope_relocation=True, actual_hrtb_output=True)
        meta.update(metadata)
        return ('actual-sort4', base[1], base[2], meta)

    def run_route(self, case):
        c4 = FakeC4(support=False)
        env = {'preserved': 'yes', 'SORT4_HRTB_OUTPUT': 'ambient',
               'SORT4_HRTB_OUTPUT_TARGETS': 'ambient-target'}
        with tempfile.TemporaryDirectory() as temp:
            result = BODY.run_case(None, c4, Path('/synthetic/tool'), env, Path(temp),
                case, FakeGates(), FakeGrammar({}), {'tool_hashes': {}})
        self.assertEqual(env, {'preserved': 'yes', 'SORT4_HRTB_OUTPUT': 'ambient',
                               'SORT4_HRTB_OUTPUT_TARGETS': 'ambient-target'})
        self.assertEqual(c4.stage_calls, 0)
        self.assertFalse(result['proof_credit'])
        return c4

    def test_full_target_enables_both_hrtb_keys_and_existing_controls_inherit_them(self):
        for control in (None, 'wrong-source-sha', 'wrong-first-call-line',
                        'opt-in-off', 'scope-opt-in-off'):
            with self.subTest(control=control):
                meta = {} if control is None else {'frontend_control': control}
                enabled = self.run_route(self.make_target_case(**meta))
                self.assertEqual(enabled.support_env['SORT4_HRTB_OUTPUT'], '1')
                self.assertEqual(enabled.support_env['SORT4_HRTB_OUTPUT_TARGETS'], 'sort4_stable')
                self.assertEqual(enabled.support_env['SORT4_ACTUAL_BODY_C1_RECOVERY'],
                                 '0' if control == 'opt-in-off' else '1')
                self.assertEqual(enabled.support_env['SORT4_ACTUAL_BODY_SCOPE_RELOCATION'],
                                 '0' if control == 'scope-opt-in-off' else '1')

        disabled = self.run_route(self.make_target_case(frontend_control='hrtb-opt-in-off'))
        self.assertNotIn('SORT4_HRTB_OUTPUT', disabled.support_env)
        self.assertNotIn('SORT4_HRTB_OUTPUT_TARGETS', disabled.support_env)
        self.assertEqual(disabled.support_env['SORT4_ACTUAL_BODY_C1_RECOVERY'], '1')
        self.assertEqual(disabled.support_env['SORT4_ACTUAL_BODY_SCOPE_RELOCATION'], '1')

        # Other mini/helper bodies cannot inherit the two opt-in keys.
        baseline = self.run_route(ActualBodyServiceTests().make_case())
        self.assertNotIn('SORT4_HRTB_OUTPUT', baseline.support_env)
        self.assertNotIn('SORT4_HRTB_OUTPUT_TARGETS', baseline.support_env)

    def test_missing_actual_source_or_scope_refuses_before_source_mutation(self):
        cases = (
            self.make_target_case(generated_source_sha256=None),
            self.make_target_case(actual_scope_relocation=False),
        )
        for case in cases:
            with self.subTest(meta=case[3]), tempfile.TemporaryDirectory() as temp:
                c4 = FakeC4()
                env = {'preserved': 'yes'}
                with self.assertRaises(RuntimeError):
                    BODY.run_case(None, c4, Path('/synthetic/tool'), env, Path(temp),
                        case, FakeGates(), FakeGrammar({}), {'tool_hashes': {}})
                self.assertEqual(c4.source_support_targets, [])
                self.assertEqual(c4.stage_calls, 0)
                self.assertEqual(env, {'preserved': 'yes'})
                self.assertEqual(list(Path(temp).iterdir()), [])
