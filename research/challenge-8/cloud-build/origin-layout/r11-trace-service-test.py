#!/usr/bin/env python3
"""Small synthetic env/exception boundary checks; no actual preparation or tools."""
import importlib.util
from pathlib import Path
import unittest
s=importlib.util.spec_from_file_location('r11_callback_trace',Path(__file__).with_name('first-callback.py'))
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
    def run_case(self, profile, *, prefix=False, actual=True, result=None, error=None):
        original={m.R11_LABEL_TRACE_ENV:'inherited', m.R9_GUARD_TRACE_ENV:'inherited',
                  m.R9_GUARD_RETURN_RECOVERY_ENV:'inherited','OTHER':'retained'}
        seen=[]
        def execute(case,args,env):
            seen.append(env)
            self.assertEqual((case,args),('case','args'))
            if error: raise error
            return result
        if error:
            with self.assertRaises(type(error)) as caught:
                m._execute_case_with_r9_trace(execute,'case','args',original,profile=profile,prefix=prefix,actual_callback_case=actual)
            self.assertIs(caught.exception,error)
        else:
            got=m._execute_case_with_r9_trace(execute,'case','args',original,profile=profile,prefix=prefix,actual_callback_case=actual)
            self.assertIs(got,result)
        self.assertEqual(original[m.R11_LABEL_TRACE_ENV],'inherited')
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
if __name__=='__main__':unittest.main()
