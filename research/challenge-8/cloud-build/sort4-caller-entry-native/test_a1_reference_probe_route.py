"""Isolated R13 preflight handoff, no compiler/preparer/full runner."""
import ast
from collections.abc import Mapping
from pathlib import Path
import unittest

SOURCE = Path(__file__).with_name('a1-runner.py')
TREE = ast.parse(SOURCE.read_text())
RUN = next(n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
OUTER = next(n for n in RUN.body if isinstance(n, ast.If) and
             ast.unparse(n.test) == "helpers is not None and result.get('tool_reconstructed')")
BRANCH = next(n for n in OUTER.body if isinstance(n, ast.If) and
              'reference_own_preflight_enabled' in ast.unparse(n.test))
FN = ast.FunctionDef(name='route', args=ast.arguments(posonlyargs=[],args=[ast.arg(arg='profile'),ast.arg(arg='value')],kwonlyargs=[],kw_defaults=[],defaults=[]),
    body=[ast.Assign(targets=[ast.Name(id='action',ctx=ast.Store())],value=ast.Lambda(args=ast.arguments(posonlyargs=[],args=[],vararg=ast.arg(arg='args'),kwonlyargs=[],kw_defaults=[],kwarg=ast.arg(arg='kwargs'),defaults=[]),body=ast.Name(id='value',ctx=ast.Load()))), BRANCH,
          ast.Return(value=ast.Constant(value='CANONICAL_CONTINUED'))],decorator_list=[])
MODULE = ast.fix_missing_locations(ast.Module(body=[FN],type_ignores=[]))
CODE = compile(MODULE, str(SOURCE), 'exec')

class ReferenceProbeRoute(unittest.TestCase):
    def invoke(self, value, mode='native-p1-target'):
        result={'case_status':{str(i):{} for i in range(26)}}
        ns={'Mapping':Mapping,'AUTHORIZATION_PHASE':'R13','R13_AUTHORIZATION_PHASE':'R13',
            'result':result,'_jsonable':lambda v:v,'CASE_ORDER':list(result['case_status']),
            'execution_events':[], 'observations':{},'persist_progress':lambda:None,
            '_atomic_json_write':lambda *a:None,'_report_value_for_disk':lambda v,*a:v,
            'partial_audit_path':None}
        exec(CODE,ns)
        answer=ns['route']({'execution_mode':mode,'reference_own_preflight_enabled':True},value)
        return answer,result
    def valid(self):
        return {'passed':True,'variants':{str(i):{'stage':{'classification':'TERMINAL','exit':0}} for i in range(7)}}
    def test_only_complete_positive_preflight_continues_canonical(self):
        self.assertEqual(self.invoke(self.valid())[0],'CANONICAL_CONTINUED')
        answer,result=self.invoke(self.valid(),'reference-own-probe')
        self.assertIs(answer,result)
        self.assertFalse(result['accepted'])
        self.assertFalse(result['matrix_admission'])
    def test_missing_partial_wrongtype_and_unclassified_stop(self):
        for value in (None,{}, {'passed':True,'variants':None},
                      {'passed':True,'variants':'wrong'}, {'passed':False,'variants':{}},
                      {'passed':True,'variants':{'one':{'stage':{'exit':0}}}}):
            with self.subTest(value=value):
                answer,result=self.invoke(value)
                self.assertIs(answer,result)
                self.assertFalse(result['diagnostic_complete'])
                self.assertIsNone(result['proof_attempted'])
                self.assertTrue(all(r['status']=='NOT_RUN' for r in result['case_status'].values()))
        for bad in (None,'0',False):
            value=self.valid();value['variants']['0']['stage']['exit']=bad
            answer,result=self.invoke(value)
            self.assertIs(answer,result)
            self.assertFalse(result['diagnostic_complete'])
        value=self.valid();value['variants']['0']['stage']['classification']='RUNNING'
        self.assertIs(self.invoke(value)[0].get('accepted'),False)
    def test_telemetry_exception_without_returned_stage_remains_unknown(self):
        value={'passed':False,'variants':{str(i):{'status':'INCONCLUSIVE','error_type':'OSError','error':'stage-progress write failed'} for i in range(7)}}
        answer,result=self.invoke(value)
        self.assertIs(answer,result)
        self.assertIsNone(result['proof_attempted'])
        self.assertFalse(result['diagnostic_complete'])
        self.assertEqual(result['reference_own_probe'],value)
if __name__=='__main__':unittest.main()
