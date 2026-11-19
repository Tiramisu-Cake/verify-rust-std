#!/usr/bin/env python3
"""Independent exact-object delta verification; no native tools or full Validate."""
import ast
import hashlib
import importlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
CANDIDATE = '9c4ce67e06a652413fa72d9678f93962da5a2e1e'
BASE = 'bcc103354d1418feeda043c6b955b38bb4393598'
REVIEW = '4bd906e8fe1e2dc78afef74d32db8b9e14c2db7e'
TASK = '0414fdbdf784f07abb1ca6a7c020d1c8064c8e39'
ROOT = 'research/challenge-8/kani-k1/kani3300/ch8-s3-s4/'
PREFIX = ROOT + 'bridge-1-r1/'
CHECKS = []
def git(repo, *args, env=None, data=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env, input=data)
def blob(repo, rev, name): return git(repo, 'show', rev + ':' + name)
def sha(b): return hashlib.sha256(b).hexdigest()
def raw(name): return blob(REPO, CANDIDATE, PREFIX + name)
def read(name): return json.loads(raw(name))
def need(value, label):
    if not value: raise AssertionError(label)
    CHECKS.append(label)
def write(name, value): (HERE/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def main():
    pins=read('PINS.json'); request=read('CI-REQUEST.json')
    need(pins['implementation_task']==TASK, 'exact issued task')
    need(blob(REPO, CANDIDATE, 'research/challenge-8/kani-k1/TASK-CH8-S3S4-BRIDGE1-COUNT-DELTA-W14.md') == blob(REPO,TASK,'research/challenge-8/kani-k1/TASK-CH8-S3S4-BRIDGE1-COUNT-DELTA-W14.md'), 'task bytes preserved; owner issuance overrides prepared wording')
    prior=json.loads(blob(REPO, REVIEW, ROOT+'bridge-1-review/FINDINGS.json'))
    need(prior['disposition']=='REQUEST_CHANGES' and prior['candidate']==BASE, 'historical review remains REQUEST_CHANGES')
    tracked=git(REPO,'ls-tree','-r','--name-only',CANDIDATE,PREFIX).decode().splitlines()
    manifest={}
    for line in raw('MANIFEST.sha256').decode().splitlines():
        digest,name=line.split('  ',1)
        need(name not in manifest and sha(raw(name))==digest, 'manifest '+name); manifest[name]=digest
        need((HERE.with_name('bridge-1-r1')/name).read_bytes()==raw(name), 'working packet exact '+name)
    need(len(tracked)==56 and len(manifest)==55 and set(tracked)=={PREFIX+n for n in manifest}|{PREFIX+'MANIFEST.sha256'}, '56 files55hashes complete sealed packet')
    identities={}
    for kind in ('source','control','tool'):
        v=pins[kind]; repo=Path(v['worktree'])
        need(git(repo,'rev-parse','HEAD').decode().strip()==v['sha'],kind+' exact HEAD')
        need(git(repo,'rev-parse',v['sha']+'^{tree}').decode().strip()==v['tree'],kind+' exact tree')
        need(git(repo,'show','-s','--format=%P',v['sha']).decode().split()==v['parents'],kind+' exact parents')
        need(not git(repo,'status','--porcelain=v1').strip(),kind+' full clean status')
        ancestors=git(repo,'rev-list','--max-count='+str(v['depth']),v['sha']).decode().splitlines()
        need(set(v['required_commits_available'])<=set(ancestors),kind+' required commits within checkout depth')
        identities[kind]={**v,'verified_ancestors':ancestors}
    source=Path(pins['source']['worktree']); control=Path(pins['control']['worktree']); sr=pins['source']['sha']; cr=pins['control']['sha']
    oldpins=json.loads(blob(REPO,BASE,ROOT+'bridge-1/PINS.json'))
    for kind in ('source','tool'):
        need(all(pins[kind][k]==oldpins[kind][k] for k in ('sha','tree','parents','depth')),kind+' exact prior reviewed object inheritance')
    oldcr=oldpins['control']['sha']; oldreq=json.loads(blob(control,oldcr,'ch8-s1-control/CI-REQUEST.json'))
    need(pins['control']['parents']==oldpins['control']['parents']==['9e14e033f9ee31522b571c127609dcdff76d230b'], 'control siblings sole9e14')
    expected=['ch8-s1-control/'+n for n in ('CI-REQUEST.json','s34_campaign.py','s34_validate.py','test_s34.py','test_s34_paths.py')]
    need(git(control,'diff','--name-only',oldcr,cr).decode().splitlines()==expected,'only5 control paths changed across complete trees')
    need(set(request)==set(oldreq) and [k for k in request if request[k]!=oldreq[k]]==['ci_payload_sha256'], 'all request semantic fields exact; only payload map delta')
    need(set(request['ci_payload_sha256'])==set(oldreq['ci_payload_sha256']) and [k for k in request['ci_payload_sha256'] if request['ci_payload_sha256'][k]!=oldreq['ci_payload_sha256'][k]]==expected[1:], 'only4 payload hashes changed')
    need(raw('CI-REQUEST.json')==blob(control,cr,'ch8-s1-control/CI-REQUEST.json') and sha(raw('CI-REQUEST.json'))==pins['request']['sha256'], 'exact request package/control/hash')
    need(raw('WORKFLOW.yml')==blob(control,cr,'.github/workflows/ch8-s2.yml')==blob(control,oldcr,'.github/workflows/ch8-s2.yml') and sha(raw('WORKFLOW.yml'))==pins['request']['workflow_sha256'],'workflow byte exact')
    need(git(control,'diff','--full-index',oldcr,cr)==raw('COUNT-REPAIR.patch'),'count repair patch exact complete delta')
    for k in ('std_sha','std_tree','tool_sha','tool_tree'):
        v=pins['source' if k.startswith('std') else 'tool']['tree' if k.endswith('tree') else 'sha']
        need(request[k]==v,'operative identity '+k)
    deps=read('DEPENDENCIES.json')
    for name,v in deps['source'].items(): need(v['source_sha']==sr and sha(blob(source,sr,name))==v['sha256'],'source dependency '+name)
    for v in deps['authored_inputs']: need(sha(blob(REPO,v['commit'],v['path']))==v['sha256'],'committed dependency '+v['path'])
    for name,digest in request['ci_payload_sha256'].items(): need(sha(blob(control,cr,name))==digest,'payload '+name)
    need(len(request['ci_payload_sha256'])==100,'100 payload hashes')
    for name,digest in read('PRESERVATION.json')['protected_python_exact_bytes'].items():
        need(sha(blob(control,cr,name))==digest and blob(control,cr,name)==blob(control,oldcr,name),'protected exact '+name)
    need(len(read('PRESERVATION.json')['protected_python_exact_bytes'])==58,'58 protected controls')
    for name,digest in read('PRESERVATION.json')['count_repair']['unchanged_package_maps'].items():
        need(sha(raw(name))==digest and raw(name)==blob(REPO,BASE,ROOT+'bridge-1/'+name),'inherited source/domain/cfg/oracle/resource map '+name)
    precursors=read('PRECURSORS.json')
    for v in precursors['historical_immutable']: need(sha(blob(REPO,v['commit'],v['path']))==v['sha256'],'immutable historical receipt '+v['path'])
    validation=read('VALIDATION.json'); final=read('validation/final-validate.json'); result=json.loads(raw('validation/final-validate.stdout'))
    need(result==validation['result'] and result['control_sha']==cr and result['control_tree']==pins['control']['tree'] and result['request_sha256']==pins['request']['sha256'],'final stdout exact object')
    tests=read('TEST-LIST.json'); expectedids=[t for suite in tests['suites'].values() for t in suite['expanded_ids']]
    stderr=raw('validation/final-validate.stderr').decode()
    observed=re.findall(r'^\w+ \(([^)]+)\) \.\.\. ok$',stderr,re.M)
    need(observed==expectedids and len(observed)==tests['expected_total']==267 and not re.search(r'^FAILED|^FAIL:|^ERROR:',stderr,re.M),'all267 individual synthetic service statuses exact ordered list')
    need([result[k] for k in ('legacy_tests','protected_s3_1_tests','protected_s3_2_tests','bridge1_tests')]==[136,56,35,40] and result['success'] and result['errors']==result['failures']==0,'267 final PASS suites')
    need(validation['actual_final_validate_execution_count']==validation['source_preflight_execution_count']==1,'author receipts report once final and source preflight')
    need(final['elapsed_seconds']==validation['elapsed_seconds']==pins['offline_validation']['elapsed_seconds'] and final['margin_at_18_minutes']==1080/final['elapsed_seconds']==validation['margin_at_18_minutes']>=1.5,'632.582333 seconds18minute margin1.707287643')
    for name in ('final-validate','control-preflight','source-preflight','targeted-count','standalone-portable'):
        rec=read('validation/'+name+'.json')
        need(rec['exit_code']==0 and rec['control_sha']==rec['head_after']==cr and rec['control_tree']==pins['control']['tree'] and rec['control_parents']==pins['control']['parents'] and rec['tracked_clean'] and rec['tracked_clean_after'], 'clean exact PASS receipt '+name)
    need(raw('validation/standalone-portable.stderr').decode().rstrip().endswith('OK') and 'Ran 1 test' in raw('validation/standalone-portable.stderr').decode(),'corrected standalone real PASS receipt')
    tree=ast.parse(blob(control,cr,'ch8-s1-control/s34_validate.py'))
    selections=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NEW' for t in n.targets))
    four=['test_s34_paths.RealPathWriterTests.test_selected_count_'+n for n in ('real_writer_and_both_readers','stopped_and_partial_prefix','without_completions','requires_validated_request_inventory')]
    need(all(t in selections and t in observed and t in tests['suites']['bridge1']['selection'] for t in four),'four new count regressions execute in exact CI Validate')
    need('test_s34.PortableReplayTests.test_same_invocation_stock_rich_metadata_and_upload_only_replay' not in observed,'standalone separate truthful receipt not silently in selected267')
    patches=[]
    with tempfile.TemporaryDirectory(prefix='bridge1-delta-static-') as d:
        tmp=Path(d)
        for i,p in enumerate(read('PATCHES.json')):
            repo=source if p['file'].startswith('SOURCE-') else control; b=raw(p['file'])
            need(sha(b)==p['sha256'],'exact patch '+p['file'])
            env=dict(os.environ,GIT_INDEX_FILE=str(tmp/('index'+str(i))))
            git(repo,'read-tree',p['base'],env=env);git(repo,'apply','--cached','--whitespace=nowarn','-',env=env,data=b)
            t=git(repo,'write-tree',env=env).decode().strip()
            need(t==p['expected_tree']==p['replayed_tree'],'independent replay '+p['file']);patches.append({**p,'independent_tree':t})
        need(len(patches)==6,'six independent patch tree replays')
        sys.path.insert(0,str(control/'ch8-s1-control'))
        policy=importlib.import_module('s34_policy');report=policy.validate_source(source,request)
        need(report['status']=='STATIC_PASS' and all(x['status']=='STATIC_PASS' for x in report['reports'].values()),'four source static gates PASS')
        write('SOURCE-GATES.json',{'status':'PASS','source':sr,'control':cr,'reports':{k:{'status':v['status'],'files':len(v['source_files_sha256']),'limits':v.get('limits',[])} for k,v in report['reports'].items()},'proof_credit':'NONE','type_MIR_resolution':'NOT_ESTABLISHED'})
    write('IDENTITY-REVIEW.json',{'candidate':CANDIDATE,'task':TASK,'baseline_candidate':BASE,'inherited_full_review':REVIEW,'identities':identities,'request_sha256':pins['request']['sha256'],'workflow_sha256':pins['request']['workflow_sha256'],'tracked_files':56,'manifest_hashes':55,'changed_paths':expected,'patch_replays':patches,'full_review_inheritance':'Exact source/tool objects, all non-delta control tree entries, all request semantics and8 scope maps; no new broad source review or proof credit','author_validation':validation,'reviewer_fullValidate_runs':0})
    write('STATIC-VALIDATION.json',{'status':'PASS','count':len(CHECKS),'checks':CHECKS,'native_or_fullValidate_run':False,'proof_credit':'NONE'})
    print(json.dumps({'status':'PASS','checks':len(CHECKS),'patch_replays':len(patches),'selected_tests':len(observed),'candidate':CANDIDATE}))
if __name__=='__main__': main()
