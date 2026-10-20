"""Isolated R11 core consumer tests; imports are inert, no proof preparation."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).parent
R11 = 'SORT4-CHECKED-CALLER-NATIVE-PROOF-2026-10-21-R11'
PROFILE = 'A1-CHECKED-CALLER-R11-PROFILE-2026-10-21.json'


def load(name):
    spec = importlib.util.spec_from_file_location('r11_test_' + name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNNER = load('a1-runner')


class CoreActivation(unittest.TestCase):
    def test_exact_profile_maps_and_target_plan(self):
        self.assertEqual(load('a1-focus-backend').PROFILE_BINDINGS[R11], PROFILE)
        self.assertEqual(load('a1-tool').FOCUS_PROFILE_NAMES[R11], PROFILE)
        profile = dict(phase_id=RUNNER.PHASE, profile_accepted=False,
                       first_matrix_status='NOT_RUN', execution_mode='native-p1-target',
                       authorization_phase_id=R11)
        plan = RUNNER.preflight_plan(profile)
        self.assertEqual(plan['case_count'], 26)
        self.assertFalse(plan['dispatch_ready'] or plan['matrix_complete'] or plan['proof_credit'])
        for bad in (None, RUNNER.PHASE, R11 + '-other'):
            with self.subTest(bad=bad), self.assertRaises(RuntimeError):
                RUNNER.preflight_plan({**profile, 'authorization_phase_id': bad})

    def test_json_roundtrip_preserves_all_values_and_source_bytes(self):
        values = [None, True, False, 0, 1, -1, 1.25, '', 'α/β~γ\n\u0000', [], {},
                  [None, True, {'source': 'pub fn caller() {}\n'}]]
        details = {case: {'values': copy.deepcopy(values), 'case': case}
                   for case in [*RUNNER.CASE_ORDER, 'α/~']}
        original = dict(authorization_phase_id=R11, observation_details=details,
                        observed_rows=[dict(case_id=case, observation=copy.deepcopy(obs))
                                       for case, obs in details.items()], proof_credit=False)
        before = copy.deepcopy(original)
        serialized = RUNNER._report_value_for_disk(original, R11)
        disk = json.loads(json.dumps(serialized, ensure_ascii=False))
        for row in disk['observed_rows']:
            tokens = row['observation_ref']['json_pointer'].split('/')[1:]
            value = disk
            for token in tokens:
                value = value[token.replace('~1', '/').replace('~0', '~')]
            self.assertEqual(value, original['observation_details'][row['case_id']])
        self.assertEqual(original, before)
        self.assertFalse(disk['proof_credit'])
        self.assertEqual(disk['observation_details'], details)

    def test_errors_partial_conflicts_duplicates_and_cross_phase_are_preserved(self):
        for row_obs, detail in [(None, None), ('bad', {}), ({'x': True}, {'x': 1}),
                                ({'x': 1}, {'x': 1.0}), ({'x': 'a'}, {'x': 'b'})]:
            report = dict(authorization_phase_id=R11, observed_rows=[
                dict(case_id='P1', observation=row_obs)], observation_details={'P1': detail})
            result = RUNNER._report_value_for_disk(report, R11)
            self.assertEqual(result, report)
        for report in (None, [], {}, {'authorization_phase_id': R11, 'observed_rows': None},
                       {'authorization_phase_id': R11, 'observation_details': {},
                        'observed_rows': [None]},
                       {'authorization_phase_id': R11, 'observation_details': {'P1': {}},
                        'observed_rows': [{'case_id': 'P1', 'observation': {}},
                                          {'case_id': 'P1', 'observation': {}}]}):
            self.assertIs(RUNNER._report_value_for_disk(report, R11), report)
        partial = {'authorization_phase_id': R11, 'observed_rows': [
            {'case_id': 'P1', 'observation': {'status': 'NOT_RUN', 'artifact': None}}],
            'observation_details': {}}
        self.assertIs(RUNNER._report_value_for_disk(partial, R11), partial)
        self.assertIs(RUNNER._report_value_for_disk(partial, RUNNER.PHASE), partial)


if __name__ == '__main__':
    unittest.main()
