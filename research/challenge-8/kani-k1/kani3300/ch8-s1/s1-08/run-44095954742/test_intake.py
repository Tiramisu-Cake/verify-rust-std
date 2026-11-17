"""Small synthetic regressions for the changed timing/partial-group adapter only."""
import unittest

from intake import compare_inventory, merge_diagnostic_row, union_domain
from timing import measure, summarize


def harness(seconds=10, verdict='SUCCESS', kind='COMPLETED'):
    return {'name': 'root', 'resources': {'verification_time_s': seconds},
            'outcome': {'kind': kind, **({'verdict': verdict} if kind == 'COMPLETED' else {})}}


class TimingTests(unittest.TestCase):
    def test_completed_and_changed_verdict_cohorts(self):
        s = measure(harness(10), harness(16), 'SUCCESS', True, 600)
        self.assertEqual((s['delta_s'], s['completed_ratio_s108_over_s107'], s['cohort']),
                         (6, 1.6, 'SUCCESS_SUCCESS'))
        f = measure(harness(10, 'FAILURE'), harness(20, 'FAILURE'), 'DETECTED', True, 600)
        v = measure(harness(), harness(20, 'FAILURE'), 'SUCCESS', True, 600)
        self.assertEqual(f['cohort'], 'INTENDED_FAILURE_FAILURE')
        self.assertEqual(v['cohort'], 'VERDICT_CHANGED')
        summary = summarize([{**x, 'compatible': True} for x in (s, f, v)])
        self.assertEqual(set(summary), {'SUCCESS_SUCCESS', 'INTENDED_FAILURE_FAILURE', 'VERDICT_CHANGED'})
        self.assertTrue(all(x['rows'] == 1 for x in summary.values()))

    def test_timeout_is_censored_with_cutoff_bound(self):
        t = measure(harness(300), harness(600.05, kind='TIMEOUT'), 'SUCCESS', True, 600)
        self.assertEqual(t['cohort'], 'TIMEOUT_CENSORED')
        self.assertIsNone(t['delta_s'])
        self.assertIsNone(t['completed_ratio_s108_over_s107'])
        self.assertEqual(t['censoring']['observed_s108_elapsed_s'], 600.05)
        self.assertEqual(t['censoring']['completion_time_ratio_lower_bound'], 2)
        summary = summarize([{**t, 'compatible': True}])['TIMEOUT_CENSORED']
        self.assertEqual(summary['comparable_completed_pairs'], 0)
        self.assertIsNone(summary['s108_completed_seconds_sum'])

    def test_missing_null_wrong_types_and_not_run_are_unknown(self):
        cases = [harness(None), harness(False), harness('12'), harness(-1), harness(float('nan')),
                 {'resources': None, 'outcome': {'kind': 'NOT_RUN'}},
                 {'resources': [], 'outcome': None}, {}]
        for new in cases:
            with self.subTest(new=new):
                t = measure(harness(), new, 'SUCCESS', True, 600)
                self.assertIsNone(t['delta_s'])
                self.assertIsNone(t['completed_ratio_s108_over_s107'])

    def test_zero_baseline_and_incompatible_domains(self):
        t = measure(harness(0), harness(4), 'SUCCESS', True, 600)
        self.assertEqual(t['delta_s'], 4)
        self.assertEqual(t['ratio_status'], 'UNKNOWN_ZERO_BASELINE')
        self.assertIsNone(t['completed_ratio_s108_over_s107'])
        for timeout in (False, True):
            t = measure(harness(10), harness(600, kind='TIMEOUT' if timeout else 'COMPLETED'),
                        'SUCCESS', False, 600)
            self.assertIsNone(t['delta_s'])
            self.assertIsNone(t['completed_ratio_s108_over_s107'])
            if timeout:
                self.assertIsNone(t['censoring']['completion_time_ratio_lower_bound'])


class PartialAdapterTests(unittest.TestCase):
    def test_reviewed_union_label_metadata_preserves_timing_domain(self):
        old = {'id': 'u', 'member_row_ids': ['n0', 'n1'], 'required_cover_messages': ['return'],
               'required_success_messages': ['old'], 'qualification': 'old metadata'}
        new = {**old, 'required_success_messages': [], 'required_success_roles': ['label'],
               'qualification': 'fresh labels, offline'}
        self.assertEqual(union_domain([old]), union_domain([new]))
        for key, value in (('member_row_ids', ['n0']), ('required_cover_messages', [])):
            self.assertNotEqual(union_domain([old]), union_domain([{**new, key: value}]))

    def test_source_success_or_timeout_cannot_promote_failed_group(self):
        original = {'id': 'cell', 'status': 'NOT_RUN', 'outcome': 'UNKNOWN'}
        projection = {'id': 'cell', 'status': 'UNKNOWN', 'outcome': 'UNKNOWN',
                      'selector': 'root', 'group': 'cell-u34', 'reason': 'missing RESULTS'}
        for kind in ('COMPLETED', 'TIMEOUT'):
            export = harness(kind=kind)
            result = merge_diagnostic_row(original, projection, export)
            self.assertEqual((result['status'], result['outcome']), ('UNKNOWN', 'UNKNOWN'))
            self.assertFalse(result['group_admitted'])
            self.assertEqual(result['reason'], 'missing RESULTS')
            self.assertNotIn('n_properties', result)
            self.assertEqual(original['status'], 'NOT_RUN')

    def test_wrong_root_or_promoted_projection_rejected(self):
        original = {'id': 'cell'}
        projection = {'id': 'cell', 'status': 'UNKNOWN', 'outcome': 'UNKNOWN',
                      'selector': 'root', 'group': 'cell-u34'}
        for change in ({'id': 'other'}, {'selector': 'other'}, {'group': 'other'},
                       {'outcome': 'RECORDED'}, {'status': 'OBSERVED'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                merge_diagnostic_row(original, {**projection, **change}, harness())

    def test_inventory_diff_uses_correct_baseline_and_current_names(self):
        result = compare_inventory([{'id': 'p', 'status': 'SUCCESS'}],
                                   [{'id': 'p', 'status': 'UNREACHABLE'}])
        self.assertEqual(result['changed'][0]['fields']['status'],
                         {'s107': 'SUCCESS', 's108': 'UNREACHABLE'})


if __name__ == '__main__':
    unittest.main()
