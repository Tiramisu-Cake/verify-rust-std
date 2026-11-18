#!/usr/bin/env python3
"""Create exact immutable-object review maps. No dispatch/compiler/network."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.with_name('batch-r4')
SOURCE = Path('/root/verify-rust-std-ch8-s2-r4-r1-w13')
CONTROL = Path('/root/kani-ch8-s2-r4-r1-w13')
Q = CONTROL/'ch8-s1-control'
OLD_SOURCE = '16aa3557742e1b8a8b64b3b3d49da23d988027f8'
OLD_CONTROL = 'db81e62d76cfa193b1d7fe8e8ebbecead7e20ef8'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
BASE = '99e8456d200fff1299ee5756279cddb23921dc65'
SP = '97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a'
CP = '9e14e033f9ee31522b571c127609dcdff76d230b'
ENTRY = 'cf40e805eb47a5f11efdf27a62b06caf2bc2adff'
DIAGNOSTIC = '04c61ba50ae4d62caaf87ed84b90e84e958c184f'


def git(repo,*args):
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()


def blob(repo,rev,path):
    return subprocess.check_output(['git','-C',str(repo),'show',rev+':'+path])


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,value): (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
def identity(repo):
    return {'worktree':str(repo),'sha':git(repo,'rev-parse','HEAD'),
            'tree':git(repo,'rev-parse','HEAD^{tree}'),'parent':git(repo,'rev-parse','HEAD^')}


def seal():
    files=sorted(p.name for p in HERE.iterdir() if p.is_file() and p.name not in ('MANIFEST.sha256','PACKAGE-CONTENTS.json'))
    write('PACKAGE-CONTENTS.json',{'files':{n:sha(HERE/n) for n in files},
          'self_reference':'PACKAGE-CONTENTS.json and MANIFEST.sha256 excluded from contents; manifest includes contents'})
    files.append('PACKAGE-CONTENTS.json')
    (HERE/'MANIFEST.sha256').write_text(''.join(sha(HERE/n)+'  '+n+'\n' for n in sorted(files)))


def main():
    sys.path.insert(0,str(Q))
    import runner,cfg_pfc,ordinary_contracts,contract_stacks,s2_correspondence,lexical_bindings
    r=runner.load_request();s=identity(SOURCE);c=identity(CONTROL);tool=identity(Path('/root/kani-upstream-ch8-s1'))
    assert s['parent']==SP and c['parent']==CP and tool['sha']==TOOL
    for repo in (SOURCE,CONTROL): assert not git(repo,'status','--porcelain=v1')
    s.update(base=BASE,derivation_source=OLD_SOURCE)
    c.update(base=CP,derivation_control=OLD_CONTROL,request_sha256=sha(Q/'CI-REQUEST.json'),workflow_sha256=sha(CONTROL/'.github/workflows/ch8-s2.yml'))
    pins={'schema':'ch8-s2-batch-r4-r1-pins-v1','task_id':'task'+ENTRY,'entry_g0':ENTRY,
          'source':s,'control':c,'tool':tool,'checkout_depths':{'control':7,'source':5,'tool':2},
          'previous_package':'4e2801660d89d75a1357a420c78cd435159c35b3',
          'frozen_diagnostic':DIAGNOSTIC,'actual_causal_CI_unit':'UNKNOWN',
          'frozen_review':'f5dd71722f82ac59e37152927a5f4dd9eee6ea1a','original_task':'043f659cb6ec8512fc0215aa52357369464f4cad','review14':'PENDING_SAME14_DELTA_REVIEW','dispatch_authority':'NONE',
          'native_compile':'NOT_RUN','causal_repair':'NOT_RUN','proof_credit':'NONE',
          'package_commit':'git commit containing this file; excluded to avoid circular identity'}
    for name,value in [('PINS.json',pins),('IDENTITIES.json',pins),('SOURCE.json',s),('CONTROL.json',c)]:write(name,value)
    shutil.copyfile(Q/'CI-REQUEST.json',HERE/'CI-REQUEST.json')
    shutil.copyfile(CONTROL/'.github/workflows/ch8-s2.yml',HERE/'WORKFLOW.yml')
    for name in ('cfg_pfc.py','ordinary_contracts.py','contract_stacks.py','s2_correspondence.py','s2_policy.py','test_cfg_pfc.py','lexical_bindings.py'):
        shutil.copyfile(Q/name,HERE/name)
    cfg=cfg_pfc.check(SOURCE,r);ordinary=ordinary_contracts.check(SOURCE,r);stacks=contract_stacks.check(SOURCE,r)
    write('NAME-RESOLUTION-MAP.json',lexical_bindings.check(SOURCE,r))
    write('CFG-PFC-MAP.json',cfg);write('ORDINARY-STUB-CONTRACT-MAP.json',ordinary);write('CONTRACT-STACK-MAP.json',stacks)
    write('COPY-CORRESPONDENCE.json',s2_correspondence.check((SOURCE/s2_correspondence.BATCH).read_text(),(SOURCE/s2_correspondence.SMALLSORT).read_text()))
    rows=[]
    for row,gate in zip(r['rows'],cfg['rows']):
        assert row['id']==gate['id']
        rows.append({'row':row,'source_binding':r['source_bindings'][row['id']],'cfg_pfc':gate})
    write('ROOT-BINDINGS.json',rows)
    files=sorted(set(r['changed_file_sha256'])|set(r['cfg_pfc_source_sha256'])|set(r['contract_stack_source_sha256'])|set(r['ordinary_contract_source_sha256'])|set(r['lexical_source_sha256'])|
                 {'library/contracts/safety/src/lib.rs','library/contracts/safety/src/kani.rs','library/contracts/safety/src/runtime.rs','library/contracts/safety/build.rs'})
    write('SOURCE-MAP.json',{'sha':s['sha'],'tree':s['tree'],'files':{p:sha(SOURCE/p) for p in files},
          'delta_from_frozen_r4':git(SOURCE,'diff','--name-only',OLD_SOURCE,s['sha']).splitlines(),
          'original_smallsort_and_all_contracts':'BYTE_IDENTICAL_TO_FROZEN_R4','variants':r['variants']})
    write('MODEL-MAP.json',{'source_sha':s['sha'],'route':'STUB_VERIFIED_ORIGINAL_SORT8_CONTRACT',
          'relation':'Full u8 order and all256 value multiplicities, initialized-byte havoc of dst8/temp8, original exact frame/domain',
          'sort13':'DIAGNOSTIC_ASSUMED; original swap contract unchanged',
          'general32':'DIAGNOSTIC_ASSUMED; sort8, insert_tail and merge contracts unchanged',
          'negative_faults':'No-op swap and copy-only merge via uncontracted S2-local seams in operation-identical caller copies',
          'qualification':'NOT_RUN; registration only; no leaf proof inferred','proof_credit':'NONE'})
    write('QUALIFICATION-ASSUMPTIONS.json',{'selected_roots':[x['id'] for x in r['rows']],
          'selected_covers':sum(x['required_cover_count'] for x in r['rows']),
          'negative_oracles':{x['id']:x['oracle'] for x in r['rows'] if 'oracle' in x},
          'unselected_registration':'sort8_registration_only is active same-cfg but NOT SELECTED, NOT EXECUTED, NOT QUALIFIED',
          'assumed_roots':r['diagnostic_assumed_inventory'],'native_compile':'NOT_RUN',
          'actual_causal_CI_unit':'UNKNOWN','closed_proof_obligations':0,'proof_credit':'NONE'})
    write('ENVELOPE.json',{'budgets':r['budgets'],'flags':r['flags'],'execution_groups':r['execution_groups'],
          'backend_seconds':600,'compile_seconds':900,'root_sum_seconds':6600,'group_seconds':7500,
          'internal_seconds':8100,'step_seconds':7560,'setup_seconds':1800,'job_minutes':180,
          'serial':1,'RSS_GiB':12,'headroom_GiB':2,'checkout':{'control':7,'source':5,'tool':2}})
    oldr=json.loads(blob(CONTROL,OLD_CONTROL,'ch8-s1-control/CI-REQUEST.json'))
    for key in ('budgets','flags','execution_groups','variants','replacement_unions','formal_expected_inventory','diagnostic_assumed_inventory','qualification_inventory'):
        assert r[key]==oldr[key],key
    assert [x['required_cover_messages'] for x in r['rows']]==[x['required_cover_messages'] for x in oldr['rows']]
    assert [x.get('failure_description') for x in r['rows']]==[x.get('failure_description') for x in oldr['rows']]
    invariance=[]
    for path in git(CONTROL,'ls-tree','-r','--name-only',OLD_CONTROL,'--','ch8-s1-control').splitlines():
        if not path.endswith('.py'):continue
        old=blob(CONTROL,OLD_CONTROL,path);new=(CONTROL/path).read_bytes()
        kind='BYTE_IDENTICAL' if old==new else 'NECESSARY_GATE_OR_TEST_DELTA'
        if path.endswith('/runner.py'):
            assert old.decode().replace(OLD_SOURCE,s['sha']).replace('135f4549d1e8d6f69f1935c817f4c42bb917b756',s['tree'])==new.decode()
            kind='TWO_SOURCE_IDENTITY_LITERALS_ONLY'
        invariance.append({'path':path,'frozen_r4_sha256':hashlib.sha256(old).hexdigest(),'candidate_sha256':sha(CONTROL/path),'status':kind})
    for item in invariance:
        if item['path'].endswith(('/pack_evidence.py','/rustc_diagnostics.py','/test_rustc_diagnostics.py','/check_package.py','/collect.py','/rich_evidence.py','/negative_oracle.py')):
            assert item['status']=='BYTE_IDENTICAL',item
    assert blob(CONTROL,OLD_CONTROL,'.github/workflows/ch8-s2.yml')==(CONTROL/'.github/workflows/ch8-s2.yml').read_bytes()
    write('RUNNER-INVARIANCE.json',{'reference':OLD_CONTROL,'candidate':c['sha'],'files':invariance,
          'B01_B02':'UNCHANGED_COLLECTOR_PACKER_DECODER_ERROR_CONTROLS','workflow':'BYTE_IDENTICAL_TO_FROZEN_R4'})
    changed={}
    for label,repo,base in [('source',SOURCE,OLD_SOURCE),('control',CONTROL,OLD_CONTROL)]:
        changed[label]=[{'path':p,'sha256':sha(repo/p)} for p in git(repo,'diff','--name-only',base,'HEAD').splitlines()]
        (HERE/(label.upper()+'-DELTA-NUMSTAT.txt')).write_text(git(repo,'diff','--numstat',base,'HEAD')+'\n')
    write('CHANGED-FILES.json',changed)
    patches=[]
    for name,repo,base,target in [('SOURCE-CANDIDATE.patch',SOURCE,BASE,s),('SOURCE-PARENT.patch',SOURCE,SP,s),('SOURCE-DELTA.patch',SOURCE,OLD_SOURCE,s),
                                  ('CONTROL-CANDIDATE.patch',CONTROL,TOOL,c),('CONTROL-PARENT.patch',CONTROL,CP,c),('CONTROL-DELTA.patch',CONTROL,OLD_CONTROL,c)]:
        (HERE/name).write_bytes(subprocess.check_output(['git','-C',str(repo),'diff','--binary','--full-index',base,target['sha']]))
        patches.append({'path':name,'base':base,'target':target['sha'],'target_tree':target['tree'],'sha256':sha(HERE/name)})
    write('PATCHES.json',patches)
    diag=HERE.with_name('r3-closure-diagnostic');rel='research/challenge-8/kani-k1/kani3300/ch8-s2/r3-closure-diagnostic'
    refs={}
    for p in sorted(diag.iterdir()):
        if p.is_file():
            assert p.read_bytes()==blob(HERE,DIAGNOSTIC,rel+'/'+p.name)
            refs[p.name]=sha(p)
    write('SOURCE-DIAGNOSTIC-REFERENCE.json',{'g0':DIAGNOSTIC,'path':str(diag),'files_sha256':refs,
          'frozen':'UNCHANGED','mechanism':'Conditional ordinary replacement-body/original-instance contract metadata mismatch',
          'actual_causal_CI_unit':'UNKNOWN','native_confirmation':'NOT_RUN','V-W':'NOT_RUN_SUPERSEDED','V-R':'NOT_RUN_SUPERSEDED'})
    write('CHECKPOINT.json',{'task_id':'task'+ENTRY,'state':'READY_FOR_SAME14_DELTA_REVIEW','source':s,'control':c,
          'claims':['All4 contracted ordinary bindings removed across3 selected roots', '23 ordinary binding records audited in11 contexts; no active target contracts',
                    'Same-cfg verified PFC gate and ordinary gate execute via existing check-source before setup/build', '3 local caller copies exact after declared renames; R14-01 correct sort4 lexical binding', 'R14-02 chained aliases resolved or fail closed in both gates', '8 added/changed functions and all static paths checked before build in ALL11 contexts'],
          'actual_causal_CI_unit':'UNKNOWN','native_compile':'NOT_RUN','causal_repair':'NOT_RUN','proof_credit':'NONE','closed_proof_obligations':0,
          'review14':'PENDING_SAME14_DELTA_REVIEW','frozen_review':'f5dd71722f82ac59e37152927a5f4dd9eee6ea1a','closed_findings':'AUTHOR_FIXED_FOR_REVIEW_R14-01_R14-02; INDEPENDENT_CLOSURE_PENDING','next_step':'SAME Independent14 delta exact candidate review, then separate exact GO-request; coordinator alone dispatches after GO',
          'ledger_reference':'a4e8bdd22f:29/29+9/14=38/43; historical r0..r3 charged0, unchanged',
          'external_actions':{'compiler':0,'CI':0,'push':0,'issue':0,'PR':0,'ledger':0,'reservation':0,'budget':0},
          'Fast':'OFF_PER_OWNER_NOT_TOGGLED','model_tier':'UNCHANGED','subagents':0,'blocker':None})
    (HERE/'CURRENT-TASK.md').write_text('Runtime: Codex. W13 task'+ENTRY+'. READY_FOR_SAME14_DELTA_REVIEW. Exact pins in PINS.json; compiler/CI/push/ledger NOT_RUN.\n')
    print(json.dumps(pins,indent=2))


if __name__=='__main__':
    if '--seal' in sys.argv:seal()
    else:main()
