"""Isolated flag-scope checks; no source preparation or toolchain execution."""
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('r24_checked_entry', Path(__file__).with_name('select-callee-r21-fractional-proof-entry.py'))
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)

class CheckedEntry(unittest.TestCase):
    def setUp(self):
        self.env = {'SMALLSORT_EXECUTION_PROVIDER':'cloud-build', E.PHASE_ENV:E.PHASE,
                    E.R24_SESSION_ENV:E.R24_SESSION_PHASE, E.OPT_IN_KEY:'1'}
        self.events = []
        self.failure = None
        def ast(**kwargs):
            self.events.append(('ast', os.environ.get(E.CHECKED_OUTCOMES_KEY)))
            return {'complete': True, 'accepted': False}
        def proof(*args):
            self.events.append(('proof', os.environ.get(E.CHECKED_OUTCOMES_KEY),
                                os.environ.get(E.VARIANT_KEY)))
            if self.failure:
                raise self.failure
            return {'status':'RAN', 'exit':1, 'source_unchanged':True}
        self.kw = dict(runtime={'proof':SimpleNamespace(VARIANTS=('positive','omit-selected-own')),
                               'o26':SimpleNamespace(proof_stage=proof),
                               'ast_inventory':SimpleNamespace(run_positive_ast_inventory=ast),
                               'capture':None}, repo=Path('/fake'), case=Path('/fake/case'),
                       name='r20-merged-optin', tool_home=Path('/fake/tool'), schema=Path('/fake/schema'),
                       compiler_sysroot=Path('/fake/sysroot'), deadline_epoch=42,
                       expected_sources={}, expected_snapshots={}, positive_ast_inventory=True)

    def test_all_variants_only_proof_has_flag_and_environment_restored(self):
        with patch.dict(os.environ,self.env,clear=True):
            before=dict(os.environ)
            for variant in ('positive','omit-selected-own'):
                result=E.run_proof_stage(**self.kw,variant=variant,checked_pointer_outcomes=True)
                self.assertEqual(dict(os.environ),before)
                self.assertEqual(result['exit'],1)
                self.assertTrue(result['r24_checked_pointer_outcomes_requested'])
            self.assertEqual(self.events,[('ast',None),('proof','1','positive'),('proof','1','omit-selected-own')])

    def test_default_off_retains_proof_and_ast_behavior(self):
        with patch.dict(os.environ,self.env,clear=True):
            result=E.run_proof_stage(**self.kw,variant='positive')
        self.assertNotIn('r24_checked_pointer_outcomes_requested',result)
        self.assertEqual(self.events,[('ast',None),('proof',None,'positive')])

    def test_exception_identity_and_cleanup(self):
        self.failure=LookupError('original proof error')
        with patch.dict(os.environ,self.env,clear=True):
            before=dict(os.environ)
            with self.assertRaises(LookupError) as caught:
                E.run_proof_stage(**self.kw,variant='positive',checked_pointer_outcomes=True)
            self.assertIs(caught.exception,self.failure)
            self.assertEqual(dict(os.environ),before)

    def test_refuse_ambient_malformed_or_wrong_route_before_execution(self):
        cases=[({E.CHECKED_OUTCOMES_KEY:'1'},True),({E.R24_SESSION_ENV:'wrong'},True),
               ({E.PHASE_ENV:'wrong'},True),({'SMALLSORT_EXECUTION_PROVIDER':'local'},True),
               ({'GITHUB_ACTIONS':'true'},True),({},'1'),({},1)]
        for changes,option in cases:
            with self.subTest(changes=changes,option=option),patch.dict(os.environ,{**self.env,**changes},clear=True):
                before=dict(os.environ)
                with self.assertRaises(RuntimeError):
                    E.run_proof_stage(**self.kw,variant='positive',checked_pointer_outcomes=option)
                self.assertEqual(dict(os.environ),before)
        self.assertEqual(self.events,[])

if __name__=='__main__':
    unittest.main()
