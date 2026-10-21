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

class R17IndexedCallbackControls(unittest.TestCase):
    def make_case(self, **delta):
        case = R16HrtbOutputRouteControls().make_target_case()
        meta = dict(case[3], actual_c2_recovery=True,
                    callback_call_lines=[7,11,15,19,23], c2_comparator_line=11)
        meta.update(delta)
        return *case[:3], meta

    def run_route(self, case):
        c4 = FakeC4(support=False)
        env = {'SORT4_ACTUAL_BODY_C2_RECOVERY':'ambient',
               'SORT4_ACTUAL_BODY_SECOND_CALL_LINE':'ambient',
               'SORT4_ACTUAL_BODY_CALL_LINES':'ambient'}
        with tempfile.TemporaryDirectory() as temp:
            row = BODY.run_case(None, c4, Path('/synthetic/tool'), env, Path(temp),
                case, FakeGates(), FakeGrammar({}), {'tool_hashes':{}})
            persisted = json.loads((Path(temp) / case[0] / 'body-result.json').read_text())
        self.assertEqual(json.loads(json.dumps(row)), persisted)
        self.assertEqual(env['SORT4_ACTUAL_BODY_C2_RECOVERY'],'ambient')
        self.assertFalse(row['proof_credit'])
        return c4

    def test_exact_indexed_route_and_ambient_isolation(self):
        c4 = self.run_route(self.make_case())
        self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_C2_RECOVERY'],'1')
        self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_SECOND_CALL_LINE'],'11')
        self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_CALL_LINES'],'7,11,15,19,23')
        c4 = self.run_route(ActualBodyServiceTests().make_case())
        for key in ('SORT4_ACTUAL_BODY_C2_RECOVERY','SORT4_ACTUAL_BODY_SECOND_CALL_LINE',
                    'SORT4_ACTUAL_BODY_CALL_LINES'):
            self.assertNotIn(key,c4.support_env)

    def test_bad_call_sites_or_missing_scope_refuse_before_stages(self):
        for delta in ({'callback_call_lines':None},{'callback_call_lines':[]},
                      {'callback_call_lines':'7,11,15,19,23'},
                      {'callback_call_lines':[True,11,15,19,23]},
                      {'callback_call_lines':[7,11,11,19,23]},
                      {'callback_call_lines':[7,15,11,19,23]},
                      {'c2_comparator_line':12},{'actual_scope_relocation':False},
                      {'actual_c1_recovery':False}):
            c4=FakeC4()
            with self.subTest(delta=delta), tempfile.TemporaryDirectory() as temp:
                with self.assertRaises(RuntimeError):
                    BODY.run_case(None,c4,Path('/synthetic/tool'),{},Path(temp),
                        self.make_case(**delta),FakeGates(),FakeGrammar({}),{'tool_hashes':{}})
                self.assertEqual(c4.stage_calls,0)
                self.assertEqual(list(Path(temp).iterdir()),[])

    def test_coordinates_are_derived_from_five_handwritten_synthetic_lines(self):
        # Arbitrary service data only; no actual std source constructor.
        text=b'\n'.join(b'let c'+str(i).encode()+b' = is_less(fake);' for i in range(1,6))+b'\n'
        case=('fake',text,text,{'actual_c1_recovery':True})
        routed=BODY.refresh_callback_coordinates(case)
        self.assertEqual(routed[3]['callback_call_lines'],[1,2,3,4,5])
        self.assertEqual(routed[3]['generated_source_sha256'],sha(text))
        for bad in (text.replace(b'c2',b'c1'),text.replace(b'let c3 = is_less(fake);\n',b'')):
            with self.assertRaises(RuntimeError):
                BODY.refresh_callback_coordinates(('fake',bad,bad,case[3]))
