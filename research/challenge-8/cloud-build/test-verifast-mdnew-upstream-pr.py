#!/usr/bin/env python3
"""Small synthetic classifier controls; this never runs compiler or VeriFast."""
import importlib.util
from pathlib import Path
import hashlib
import json
import tempfile
import re

path=Path(__file__).with_name('mdnew-upstream-pr-audit.py')
spec=importlib.util.spec_from_file_location('mdnew_upstream_pr_audit',path)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

commands=list(m.TRACES)
def line(command, body=''):
    return f'Starting process 1: purely_unsafe/manuallydrop_new_cfg$ {command}\n{body}' \
           f'PASS: purely_unsafe/manuallydrop_new_cfg$ {command} (0.01s)\n'
valid=''.join(line(c, ('[1]0 errors found (8 statements verified)\n' if c in commands[:2] else
                       '[1]false_normal_post.rs(12,1): error: Cannot prove false\n' if 'false_normal_post' in c else
                       '[1]shared_false_unwind.rs(17,1): error: Cannot prove false\n' if 'shared_false_unwind' in c else
                       '[1]dead_code_pre.rs(1,1-7,2): dead code\n' if 'dead_code_pre' in c else '')) for c in commands)
assert m.verify_trace(valid,0)['mysh_commands']==5
controls=(
    ('missing', valid.replace(line(commands[0],'[1]0 errors found (8 statements verified)\n'),''), 0, 'INCOMPLETE_EVIDENCE'),
    ('early diagnostic', valid.replace('[1]dead_code_pre.rs(1,1-7,2): dead code\n','')+
     '[9]dead_code_pre.rs(1,1-7,2): dead code\n', 0, 'EARLY_OR_WRONG_DIAGNOSTIC'),
    ('wrong diagnostic', valid.replace('dead_code_pre.rs(1,1-7,2): dead code',
                                        'dead_code_pre.rs(1,1): error: Cannot prove false'),
     0, 'EARLY_OR_WRONG_DIAGNOSTIC'),
    ('nonzero runner', valid, 1, 'EARLY_OR_WRONG_DIAGNOSTIC'),
    ('timeout', valid, 124, 'TIMEOUT'),
    ('disabled unwind', valid+'-ignore_unwind_paths\n', 0, 'EARLY_OR_WRONG_DIAGNOSTIC'),
)
for name,log,code,kind in controls:
    try: m.verify_trace(log,code)
    except m.AuditFailure as error: assert error.kind==kind,(name,error.kind)
    else: raise AssertionError(f'{name} control passed')

with tempfile.TemporaryDirectory(prefix='mdnew-pr-stage-audit-') as temp:
    root=Path(temp); log=root/'stage.log'; status=root/'stage-exit.txt'; resources=root/'stage-resources.txt'
    log.write_text('stage output\n'); status.write_text('0\n'); resources.write_text('elapsed: 1s\n')
    record={'run':{'path':log.name,'sha256':hashlib.sha256(log.read_bytes()).hexdigest(),
                   'exit_status':0,'exit_status_path':status.name,'resources_path':resources.name,
                   'resources_sha256':hashlib.sha256(resources.read_bytes()).hexdigest()}}
    assert m.verify_stage(root,record,'run')=='PASS'
    for name,change,kind in (
        ('missing log',lambda r:r.update(run={**r['run'],'path':'missing.log'}),'MISSING_EVIDENCE'),
        ('exit mismatch',lambda r:status.write_text('1\n'),'INCOMPLETE_EVIDENCE'),
        ('resource mismatch',lambda r:resources.write_text('tampered\n'),'INCOMPLETE_EVIDENCE')):
        log.write_text('stage output\n'); status.write_text('0\n'); resources.write_text('elapsed: 1s\n')
        record['run']['sha256']=hashlib.sha256(log.read_bytes()).hexdigest()
        record['run']['resources_sha256']=hashlib.sha256(resources.read_bytes()).hexdigest()
        broken={'run':dict(record['run'])}; change(broken)
        try: m.verify_stage(root,broken,'run')
        except m.AuditFailure as error: assert error.kind==kind,(name,error.kind)
        else: raise AssertionError(f'{name} stage control passed')
    log.write_text('stage output\n'); resources.write_text('elapsed: 1s\n'); status.write_text('1\n')
    record['run'].update({'exit_status':1,'sha256':hashlib.sha256(log.read_bytes()).hexdigest(),
                          'resources_sha256':hashlib.sha256(resources.read_bytes()).hexdigest()})
    try: m.verify_stage(root,record,'run')
    except m.AuditFailure as error: assert error.kind=='EARLY_OR_WRONG_DIAGNOSTIC'
    else: raise AssertionError('nonzero stage control passed')
    status.write_text('124\n'); record['run']['exit_status']=124
    try: m.verify_stage(root,record,'run')
    except m.AuditFailure as error: assert error.kind=='TIMEOUT'
    else: raise AssertionError('mandatory stage timeout control passed')
    record['make_test_run']=dict(record['run'])
    assert m.verify_stage(root,record,'make_test_run',(0,124,125,137))=='TIMEOUT'

# Exercise audit() through its accepted result serialization path with temporary
# native case evidence and mocked stage/provenance readers.
with tempfile.TemporaryDirectory(prefix='mdnew-pr-audit-success-') as temp:
    root=Path(temp); all_logs=root/'allprooflogs'; cases=all_logs/'cases/manuallydrop-native'
    all_logs.mkdir(parents=True); cases.mkdir(parents=True)
    script=('cd purely_unsafe\n'+'\n'.join(m.REGISTRATION)+'\ncd ..\n').encode()
    (all_logs/'selected-manuallydrop-registration.mysh').write_bytes(script)
    (all_logs/'native-registration.log').write_text(valid)
    (all_logs/'rust-testsuite.log').write_text('mocked pass\n')
    (all_logs/'make-test.log').write_text('NOT_RUN: synthetic budget control\n')
    case_commands={'forget':commands[0],'shared_cleanup':commands[1],
      'false_normal_post':commands[2],'shared_false_unwind':commands[3],
      'dead_code_pre':commands[4]}
    synthetic={}; m.FIXTURES={}
    for index,(name,command) in enumerate(case_commands.items()):
        source=f'synthetic fixture {name}\n'.encode(); source_hash=hashlib.sha256(source).hexdigest(); blob=f'{index+1:040x}'
        m.FIXTURES[name]=(source_hash,blob)
        start=re.search(r'(?m)^Starting process \d+: (?:[^\n]*\$ )?'+re.escape(command)+r'$',valid)
        after=valid[start.end():]; finish=re.search(r'(?m)^PASS: (?:[^\n]*\$ )?'+re.escape(command)+r' \(',after)
        end=valid.find('\n',start.end()+finish.start()); case_trace=valid[start.start():end+1]
        case_dir=cases/name; case_dir.mkdir()
        (case_dir/'source.rs').write_bytes(source); (case_dir/'native-mysh-trace.log').write_text(case_trace)
        item={'path':f'tests/rust/purely_unsafe/manuallydrop_new_cfg/{name}.rs','command':command,
              'source_sha256':source_hash,'git_blob':blob,'trace_path':'native-mysh-trace.log',
              'trace_sha256':hashlib.sha256(case_trace.encode()).hexdigest()}
        (case_dir/'case.json').write_text(json.dumps(item,indent=2,sort_keys=True)+'\n'); synthetic[name]=item
    native={'selected_commands':m.REGISTRATION,'selected_script_sha256':hashlib.sha256(script).hexdigest(),
      'registration_sha256':m.REGISTRATION_SHA256,'registration_git_blob':m.REGISTRATION_BLOB,
      'registration_run':{'exit_status':0},'rust_suite_run':{},'make_test_run':{'path':'make-test.log'},'case_evidence':synthetic}
    (all_logs/'native-input.json').write_text(json.dumps(native,indent=2,sort_keys=True)+'\n')
    (cases/'selected-registration.mysh').write_bytes(script)
    (cases/'manifest.json').write_text(json.dumps(native,indent=2,sort_keys=True)+'\n')
    m.verify_stage=lambda *args,**kwargs: ('NOT_RUN' if len(args)>2 and args[2]=='make_test_run' else 'PASS')
    m.verify_provenance=lambda *args,**kwargs:{'mocked_pins':True}
    accepted=m.audit(root/'tool',all_logs)
    assert accepted['accepted'] is True
    assert json.loads(json.dumps(accepted))['selected_registration']['dead_code_diagnostic'] is True

recipe=json.loads((path.parent/'recipes/verifast-mdnew-upstream-pr.json').read_text())
assert all(recipe[key]==sorted(set(recipe[key])) for key in ('infra_paths','proof_paths'))
print({'synthetic_trace_controls':len(controls)+1,'synthetic_stage_controls':7,
       'accepted_audit_json_serialization':True,'compiler_or_verifier_execution':False,'passed':True})
