#!/usr/bin/env python3
"""Prepare exact local r2 identity/patch/input bindings; never dispatches."""
import hashlib,json,os,subprocess,tempfile
from pathlib import Path
OUT=Path(__file__).resolve().parent
G0=OUT.parents[5]
CONTROL=Path('/root/kani-ch8-s3-1-r2-control-w13')
SOURCE=Path('/root/verify-rust-std-ch8-s3-1-final-w13');TOOL=Path('/root/kani-upstream-ch8-s1')
FROZEN='fc29b93b1e333b73e55e2872701c80d9927f3b02'
TASK='e2ea94d04c9d9977ac9cde891c13a73ee65f2ec4'
INTAKE='1d8a06c8bd418de6261a1cbbb24ea0f35bae1712'
BASE='research/challenge-8/kani-k1/'
PACKAGE='0902ad2d84e5e5c4d9bb3b01d5c7f7671e84b38d'
REVIEW='27040e2cd8d3564e5d0a929b8f68ca38a5a61432'
GO='99291133b2ee82d3ccd03a116f8f4cf4855f7e86'
def run(repo,*args,env=None):return subprocess.check_output(['git','-C',str(repo),*args],env=env)
def git(repo,*args):return run(repo,*args).decode().strip()
def sha(data):return hashlib.sha256(data).hexdigest()
def write(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
def pin(repo):return {'worktree':str(repo),'sha':git(repo,'rev-parse','HEAD'),'tree':git(repo,'rev-parse','HEAD^{tree}'),'parent':git(repo,'rev-parse','HEAD^')}
def patch(repo,name,base,target):
    data=run(repo,'diff','--binary',base,target);path=OUT/name;path.write_bytes(data)
    with tempfile.TemporaryDirectory() as d:
        env=dict(os.environ,GIT_INDEX_FILE=d+'/index');run(repo,'read-tree',base,env=env)
        run(repo,'apply','--cached','--binary',str(path),env=env)
        tree=git(repo,'rev-parse',target+'^{tree}');actual=run(repo,'write-tree',env=env).decode().strip();assert tree==actual
    return {'patch':name,'base':base,'target':target,'tree':tree,'sha256':sha(data),'status':'EXACT_TREE_MATCH_VIA_ISOLATED_INDEX'}
def main():
    pins={k:pin(repo) for k,repo in [('control',CONTROL),('source',SOURCE),('tool',TOOL)]}
    assert pins['control']['sha']=='cb63033ffcde918f4341146e56373476b8eeb569'
    assert pins['control']['parent']=='9e14e033f9ee31522b571c127609dcdff76d230b'
    assert pins['source']['sha']=='513341f41ce53833a279571401c924bdddddb6c8'
    assert pins['tool']['sha']=='0aac16ef62da9e9d5645782d458593e5d78143ba'
    for repo in (CONTROL,SOURCE,TOOL):assert not git(repo,'status','--porcelain=v1')
    h=CONTROL/'ch8-s1-control';request=(h/'CI-REQUEST.json').read_bytes();workflow=(CONTROL/'.github/workflows/ch8-s2.yml').read_bytes()
    q=json.loads(request)
    for name,digest in q['ci_payload_sha256'].items():assert sha((CONTROL/name).read_bytes())==digest
    for name,data in [('CI-REQUEST.json',request),('WORKFLOW.yml',workflow),('FIXTURE-REGRESSION.py',(h/'test_s3_paths.py').read_bytes())]:(OUT/name).write_bytes(data)
    pins.update(task=TASK,intake=INTAKE,frozen_control=FROZEN,frozen_package=PACKAGE,frozen_review=REVIEW,spent_GO=GO,
        request_sha256=sha(request),workflow_sha256=sha(workflow),fixture_sha256=sha((h/'test_s3_paths.py').read_bytes()),
        status='READY_FOR_SAME14_DELTA',same14_review='PENDING',GO='NEW_ROOT_GO_REQUIRED_AFTER_APPROVAL',package_g0='SELF: commit containing MANIFEST.sha256; full SHA supplied in handoff response',native='NOT_RUN',proof_credit=0)
    write('PINS.json',pins)
    patches=[patch(CONTROL,'CONTROL-PARENT.patch',pins['control']['parent'],pins['control']['sha']),
             patch(CONTROL,'CONTROL-DELTA.patch',FROZEN,pins['control']['sha']),
             patch(CONTROL,'CONTROL-CANDIDATE.patch',pins['tool']['sha'],pins['control']['sha']),
             patch(SOURCE,'SOURCE-PARENT.patch',pins['source']['parent'],pins['source']['sha'])]
    write('PATCHES.json',patches)
    ancestry=[]
    for kind,depth,base in [('control',7,pins['tool']['sha']),('source',5,'99e8456d200fff1299ee5756279cddb23921dc65'),('tool',2,pins['tool']['parent'])]:
        repo={'control':CONTROL,'source':SOURCE,'tool':TOOL}[kind];chain=git(repo,'rev-list','--first-parent','--max-count='+str(depth),pins[kind]['sha']).splitlines()
        assert len(chain)==depth and chain[-1]==base
        ancestry.append({'kind':kind,'head':pins[kind]['sha'],'depth':depth,'chain':chain,'status':'MATCH'})
    write('ANCESTRY.json',ancestry)
    dependencies=[]
    def include(commit,path,dest):
        data=run(G0,'show',commit+':'+path);target=OUT/dest;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        dependencies.append({'commit':commit,'path':path,'blob':git(G0,'rev-parse',commit+':'+path),'sha256':sha(data),'bytes':len(data),'copy':dest})
    include(TASK,BASE+'TASK-CH8-S3-1-PATH-FIX-W13.md','inputs/TASK-W13.md')
    include(TASK,BASE+'TASK-CH8-S3-1-PATH-DELTA-W14.md','inputs/TASK-W14.md')
    for name in ('HANDOFF.md','BEFORE-DIFF.md','BEFORE-DIFF.json','SOURCE-TRACE.json','PREFIX-REPLAY.md','PREFIX-REPLAY.json','NATIVE.json','RESULT.json','COST.json'):
        include(INTAKE,BASE+'kani3300/ch8-s3/run-44405927807/'+name,'inputs/intake/'+name)
    for name in ('PINS.json','CHECKPOINT.json','CLOSURE.json','MANIFEST.sha256'):
        include(PACKAGE,BASE+'kani3300/ch8-s3/s3-1-r1/'+name,'inputs/frozen-package/'+name)
    for name in ('REPORT.md','FINDINGS.json','MANIFEST.sha256'):
        include(REVIEW,BASE+'kani3300/ch8-s3/s3-1-review-r1/'+name,'inputs/frozen-review/'+name)
    maps=[]
    for name in ('ROOT-BINDINGS.json','ROLE-COVER-MAP.json','DOMAIN-UNWIND.json','PROVIDER-DAG.json','U-SITE-PROPOSAL.json','FULL-OBLIGATIONS.md'):
        data=run(G0,'show',PACKAGE+':'+BASE+'kani3300/ch8-s3/s3-1-r1/'+name);(OUT/name).write_bytes(data)
        maps.append({'file':name,'sha256':sha(data),'status':'BYTE_IDENTICAL_TO_FROZEN_PACKAGE','commit':PACKAGE})
    # The four-path delta must contain no common reader/writer/policy change.
    delta=git(CONTROL,'diff','--name-only',FROZEN,pins['control']['sha']).splitlines()
    assert set(delta)=={'ch8-s1-control/'+x for x in ('CI-REQUEST.json','s3_campaign.py','s3_validate.py','test_s3_paths.py')}
    write('INPUTS.json',{'task':TASK,'intake':INTAKE,'dependencies':dependencies,'immutable_source_scope_maps':maps,
        'source_tool_unchanged':True,'delta_paths':delta,'legacy_byte_identity':'runner.py, all legacy writers/readers/policies/tests unchanged from fc29',
        'historical_physical_identity':'UNKNOWN','historical_artifact_transformed':False,'prohibited_actions_performed':[]})
    write('PRECURSORS.json',{'records':[
        {'file':'PRECURSOR-1.stderr.txt','state':'FAILED','reason':'17 fixture assertions: native memory preflight correctly refused below2GiB headroom; no production change; fixed synthetic resource telemetry'},
        {'file':'PRECURSOR-2.stderr.txt','state':'9PASS','elapsed_seconds':36.705,'scope':'before adding actual killed worker test and workflow command extraction'},
        {'file':'PRECURSOR-KILLED.stderr.txt','state':'1PASS','scope':'actual forked Python worker SIGKILL before native callback'},
        {'file':'TARGETED.json','state':'20PASS_AND_FROZEN_EXPECTED_FAILURE','scope':'exact final test bytes before control freeze'}],
        'initial_shell_typo':'First heredoc used child-relative path in child cwd; no test file written. Corrected immediately; no production effect.',
        'final_validate_execution_count':1,'native':'NOT_RUN'})
    print(json.dumps({'control':pins['control'],'request_sha256':pins['request_sha256'],'workflow_sha256':pins['workflow_sha256'],'patches':len(patches),'dependencies':len(dependencies),'scope_maps':len(maps)}))
if __name__=='__main__':main()
