#!/usr/bin/env python3
"""Small synthetic replay of the isolated report classifier, no tool execution."""
import ast
import copy
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent
RUNNER = HERE.parents[1] / 'merge/cloud-build/merge.sh'
source = RUNNER.read_text().split("<<'COMPILEAUDIT'\n", 1)[1].split('\nCOMPILEAUDIT', 1)[0]
tree = ast.parse(source)
assert all(node.names[0].name in {'json', 'pathlib', 'sys'} for node in tree.body if isinstance(node, ast.Import))
assert not any(isinstance(node, ast.ImportFrom) for node in ast.walk(tree))
code = compile(source, str(RUNNER)+':COMPILEAUDIT', 'exec')  # Python report classifier only
with tempfile.TemporaryDirectory(prefix='merge-len1-audit-service-') as temporary:
    root = Path(temporary)
    base, prep, candidate = [root/x for x in ('base', 'preparation', 'candidate')]
    for path in (base, prep, candidate, root/'checked-minimal-bridge', root/'checked-profile-smoke'):
        path.mkdir()
    (base/'source-build-exit-code.txt').write_text('0\n')
    (prep/'source-prepared.json').write_text(json.dumps({'classification':'PREPARED_ONLY_NO_COMPILE_OR_PROOF_CREDIT','compiler_attempted':False,'proof_attempted':False}))
    compile_report = {'classification':'COMPILE_ONLY_NO_PROOF_CREDIT','accepted':False,'proof_attempted':False,'stages':{name:{'exit_code':0} for name in ('exporter-build','decoder-build','translator-build','console-build')}}
    (candidate/'compile-preflight.json').write_text(json.dumps(compile_report))
    (candidate/'postbuild-source-hash-check-exit-code.txt').write_text('0\n')
    retained = {'cases':{'ordinary_call_normal_unwind':'PASS'}, 'classifier_controls_passed':True}
    (root/'checked-profile-smoke/aggregate.json').write_text(json.dumps(retained))
    summary = {'all_matched':True,'accepted':False,'schema':'merge-minimal-len1-interface-v1','exact_case_sets':True,'campaign':'len1-minimal-v1','cases':{str(i):'synthetic' for i in range(12)}}
    outcomes = {}
    for label in ('positive', 'missing_case', 'accepted', 'not_matched', 'wrong_campaign', 'wrong_schema', 'compile_failed', 'smoke_failed', 'dispatcher_failed'):
        row = copy.deepcopy(summary)
        (candidate/'postbuild-source-hash-check-exit-code.txt').write_text('1\n' if label=='compile_failed' else '0\n')
        smoke = copy.deepcopy(retained)
        if label=='missing_case': row['cases'].pop('0')
        if label=='accepted': row['accepted']=True
        if label=='not_matched': row['all_matched']=False
        if label=='wrong_campaign': row['campaign']='bridge-minimal-v1'
        if label=='wrong_schema': row['schema']='merge-minimal-guard-bridge-v1'
        if label=='smoke_failed': smoke['classifier_controls_passed']=False
        (root/'checked-profile-smoke/aggregate.json').write_text(json.dumps(smoke))
        (root/'checked-minimal-bridge/aggregate.json').write_text(json.dumps(row))
        old_argv=sys.argv
        try:
            sys.argv=['isolated-audit',str(root/'audit.json'),'1' if label=='dispatcher_failed' else '0',str(base),str(prep),str(candidate),'len1-minimal']
            exec(code, {'__builtins__':__builtins__})
        finally:
            sys.argv=old_argv
        result=json.loads((root/'audit.json').read_text())
        assert result['diagnostic_complete'] is (label=='positive'),label
        assert result['accepted'] is False
        if label=='positive': assert result['classification']=='MINIMAL_LEN1_INTERFACE_COMPONENT_DIAGNOSTIC'
        outcomes[label]=result['diagnostic_complete']
print(json.dumps({'classification':'PASS_SERVICE_ONLY','mutations_rejected':len(outcomes)-1,'proof_attempted':False,'accepted':False}))
