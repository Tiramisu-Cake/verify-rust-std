#!/usr/bin/env python3
"""Small synthetic env/exception boundary checks; no actual preparation or tools."""
import importlib.util
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('r11_callback_trace',Path(__file__).with_name('first-callback.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
    def run_case(self, profile, *, prefix=False, actual=True, result=None, error=None):
        class Args: pass
        args=Args()
        original={m.R11_LABEL_TRACE_ENV:'inherited', m.R11_LABEL_PLACEMENT_ENV:'inherited', m.R9_GUARD_TRACE_ENV:'inherited',
                  m.R9_GUARD_RETURN_RECOVERY_ENV:'inherited','OTHER':'retained'}
        seen=[]
        def execute(case,args,env):
            seen.append(env)
            self.assertEqual((str(case),args),(str(Path('case')),args))
            if error: raise error
            return result
        if error:
            with self.assertRaises(type(error)) as caught:
                m._execute_case_with_r9_trace(execute,Path('case'),args,original,profile=profile,prefix=prefix,actual_callback_case=actual)
            self.assertIs(caught.exception,error)
        else:
            got=m._execute_case_with_r9_trace(execute,Path('case'),args,original,profile=profile,prefix=prefix,actual_callback_case=actual)
            self.assertIs(got,result)
        self.assertEqual(original[m.R11_LABEL_TRACE_ENV],'inherited')
        self.assertEqual(original[m.R11_LABEL_PLACEMENT_ENV],'inherited')
        self.assertEqual(seen[0]['OTHER'],'retained')
        return seen[0]
    def test_r11_actual_only_and_input_unchanged(self):
        e=self.run_case(m.R11_PROFILE,result={'stages':{'verifast':1}})
        self.assertEqual(e[m.R11_LABEL_TRACE_ENV],'1')
        self.assertEqual(e[m.R9_GUARD_RETURN_RECOVERY_ENV],'1')
    def test_prefix_and_non_actual_clear_inherited_trace(self):
        for opts in ({'prefix':True},{'actual':False}):
            e=self.run_case(m.R11_PROFILE,**opts)
            self.assertNotIn(m.R11_LABEL_TRACE_ENV,e)
            self.assertNotIn(m.R9_GUARD_RETURN_RECOVERY_ENV,e)
    def test_legacy_profiles_never_enable_r11(self):
        for profile in m.SUPPORTED_PROFILES:
            if profile!=m.R11_PROFILE:
                self.assertNotIn(m.R11_LABEL_TRACE_ENV,self.run_case(profile))
    def test_errors_keep_original_exception(self):
        self.run_case(m.R11_PROFILE,error=RuntimeError('synthetic stage failure'))
        self.run_case(m.R11_PROFILE,error=TimeoutError('synthetic deadline'))
    def test_partial_missing_null_and_not_run_results_unchanged(self):
        for result in (None,{}, {'stages':None}, {'status':'NOT_RUN'}, {'exit_code':124}, {'stage_receipts':[]}, 'wrong-type'):
            self.run_case(m.R11_PROFILE,result=result)

    def test_native_placement_flag_is_only_fullbody_with_receipt(self):
        class Args: pass
        args=Args()
        receipt={'profile':m.R11_PROFILE,'cloud_build_id':'build'}
        seen=[]
        def execute(case,got_args,env):
            seen.append((env, getattr(got_args,'r11_native_run',None)))
            return {'stages':{'exporter':0,'decode':0}}
        result=m._execute_case_with_r9_trace(
            execute,Path('evidence/full_body/cases/actual_three_current_full_posts'),args,
            {m.R11_LABEL_PLACEMENT_ENV:'inherited'},profile=m.R11_PROFILE,
            actual_callback_case=True,r11_native_fullbody=True,validated_receipt=receipt)
        self.assertEqual(seen[0][0][m.R11_LABEL_PLACEMENT_ENV],'1')
        self.assertEqual(seen[0][0][m.R11_LABEL_TRACE_ENV],'1')
        self.assertIs(seen[0][1],receipt)
        self.assertFalse(hasattr(args,'r11_native_run'))
        self.assertEqual(result['stages']['decode'],0)

    def test_native_context_restores_previous_value_on_exception(self):
        class Args: r11_native_run='old'
        args=Args(); receipt={'profile':m.R11_PROFILE}
        failure=RuntimeError('synthetic')
        def execute(case,got_args,env):
            self.assertIs(got_args.r11_native_run,receipt)
            raise failure
        with self.assertRaises(RuntimeError) as caught:
            m._execute_case_with_r9_trace(
                execute,Path('evidence/full_body/cases/actual_three_current_full_posts'),args,{},
                profile=m.R11_PROFILE,actual_callback_case=True,r11_native_fullbody=True,
                validated_receipt=receipt)
        self.assertIs(caught.exception,failure)
        self.assertEqual(args.r11_native_run,'old')

    def test_native_path_rejects_missing_tuple_and_prefix_non_r11_are_isolated(self):
        class Args: pass
        args=Args()
        with self.assertRaisesRegex(RuntimeError,'validated current R11 receipt'):
            m._execute_case_with_r9_trace(
                lambda *a: self.fail('execute should not run'),
                Path('evidence/full_body/cases/actual_three_current_full_posts'),args,{},
                profile=m.R11_PROFILE,actual_callback_case=True,r11_native_fullbody=True)
        for profile,prefix,actual in ((m.R11_PROFILE,True,True),(m.R10_PROFILE,False,True)):
            seen=[]
            m._execute_case_with_r9_trace(lambda c,a,e: seen.append(e),Path('case'),args,
                {m.R11_LABEL_PLACEMENT_ENV:'inherited'},profile=profile,prefix=prefix,
                actual_callback_case=actual)
            self.assertNotIn(m.R11_LABEL_PLACEMENT_ENV,seen[0])
            self.assertFalse(hasattr(args,'r11_native_run'))

    def test_placement_replay_env_enables_complete_r11_trace_bundle(self):
        original={m.R11_LABEL_TRACE_ENV:'inherited',m.R9_GUARD_TRACE_ENV:'inherited',
                  m.R9_GUARD_RETURN_RECOVERY_ENV:'inherited',
                  m.R11_LABEL_PLACEMENT_ENV:'inherited','OTHER':'kept'}
        scoped=m._r11_storage_placement_env(original)
        self.assertEqual(scoped[m.R11_LABEL_TRACE_ENV],'1')
        self.assertEqual(scoped[m.R11_LABEL_PLACEMENT_ENV],'1')
        self.assertEqual(scoped[m.R9_GUARD_TRACE_ENV],'1')
        self.assertEqual(scoped[m.R9_GUARD_RETURN_RECOVERY_ENV],'1')
        self.assertEqual(scoped['OTHER'],'kept')
        self.assertEqual(original[m.R11_LABEL_PLACEMENT_ENV],'inherited')
if __name__=='__main__':unittest.main()
