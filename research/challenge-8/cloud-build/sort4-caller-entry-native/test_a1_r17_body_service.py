"""Synthetic R17 service routing; no actual proof/source preparation."""
from pathlib import Path
_r16 = Path(__file__).with_name('test_a1_r16_body_service.py')
_source = _r16.read_text().replace('a1-actual-body-r16.py', 'a1-actual-body-r17.py')
exec(compile(_source, str(_r16), 'exec'))

class R17ResourceHelperControls(unittest.TestCase):
    def make_helper(self, case_name, helper_name):
        case = ActualBodyServiceTests().make_case()
        meta = dict(case[3], name=helper_name, mir_target='sort4_stable',
                    actual_c1_recovery=True, actual_scope_relocation=True,
                    actual_hrtb_output=True, generated_source_sha256=sha(case[1]),
                    first_comparator_line=7)
        return case_name, case[1], case[2], meta

    def test_both_exact_resource_helpers_drop_hrtb_and_keep_source_guards(self):
        for case_name, helper_name in (
            ('missing-fourth-end-token-negative', 'missing_fourth_end_token_negative'),
            ('false-old-value-array-post-negative', 'false_old_value_array_post_negative'),
        ):
            case = self.make_helper(case_name, helper_name)
            routed = BODY.route_resource_control(case)
            self.assertEqual(routed[:3], case[:3])
            self.assertTrue(case[3]['actual_hrtb_output'])
            self.assertNotIn('actual_hrtb_output', routed[3])
            self.assertEqual(routed[3], {k:v for k,v in case[3].items() if k != 'actual_hrtb_output'})
            c4 = FakeC4(support=False)
            env = {'SORT4_HRTB_OUTPUT': 'ambient', 'SORT4_HRTB_OUTPUT_TARGETS': 'ambient'}
            with tempfile.TemporaryDirectory() as temp:
                row = BODY.run_case(None, c4, Path('/synthetic/tool'), env, Path(temp),
                    routed, FakeGates(), FakeGrammar({}), {'tool_hashes': {}})
                persisted = json.loads((Path(temp) / case_name / 'body-result.json').read_text())
            self.assertEqual(json.loads(json.dumps(row)), persisted)
            self.assertNotIn('SORT4_HRTB_OUTPUT', c4.support_env)
            self.assertNotIn('SORT4_HRTB_OUTPUT_TARGETS', c4.support_env)
            self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_SCOPE_RELOCATION'], '1')
            self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_C1_RECOVERY'], '1')
            self.assertFalse(row['proof_credit'])

    def test_malformed_or_unknown_helpers_refuse_without_mutation(self):
        case = self.make_helper('missing-fourth-end-token-negative', 'missing_fourth_end_token_negative')
        for delta in ({'name': 'sort4_stable'}, {'name': 'unknown'}, {'mir_target': 'other'},
                      {'actual_c1_recovery': False}, {'actual_scope_relocation': None},
                      {'generated_source_sha256': '0'*64}, {'first_comparator_line': True},
                      {'first_comparator_line': 0}):
            with self.subTest(delta=delta), self.assertRaises(RuntimeError):
                BODY.route_resource_control((*case[:3], dict(case[3], **delta)))
        with self.assertRaises(RuntimeError):
            BODY.route_resource_control(('unknown', *case[1:]))
