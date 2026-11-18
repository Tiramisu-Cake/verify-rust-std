#!/usr/bin/env python3
"""Gate-only exact-object backlog evidence. No executable CI package is produced."""
import copy,hashlib,importlib.util,json,os,subprocess,sys,tempfile
from pathlib import Path
H=Path(__file__).resolve().parent
G=Path('/root/verify-rust-std-kani3300-g0')
C=Path('/root/kani-ch8-s2-r14-03-gate-backlog-w13');Q=C/'ch8-s1-control'
F=Path('/root/kani-ch8-s2-r4-r1-w13');S=Path('/root/verify-rust-std-ch8-s2-r4-r1-w13')
BASE='0e8c836857344866564e1423ad5d8d28bbc4106b'
ENTRY='6db728b62b62d6d98d683f3d2cf6fb824dd6cc68'
REVIEW='e7837b0f70e235399e53f8da1b48a4a84b33f693'
sys.dont_write_bytecode=True;sys.path.insert(0,str(Q))
import lexical_bindings as l,cfg_pfc as c

def git(repo,*args,env=None):return subprocess.check_output(['git','-C',str(repo),*args],env=env)
def val(repo,*args):return git(repo,*args).decode().strip()
def sha(data):return hashlib.sha256(data).hexdigest()
def dump(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
def identity(repo):return {'worktree':str(repo),'sha':val(repo,'rev-parse','HEAD'),'tree':val(repo,'rev-parse','HEAD^{tree}'),'parent':val(repo,'rev-parse','HEAD^')}

def main():
    local=identity(C);frozen=identity(F);source=identity(S)
    assert frozen['sha']==BASE and source['sha']=='bd62e54df1b4749154790aa3db3cc7978f547f75'
    assert local['parent']==BASE
    for repo in (C,F,S):assert not val(repo,'status','--porcelain=v1'),repo
    paths=val(C,'diff','--name-only',BASE,local['sha']).splitlines()
    assert paths==['ch8-s1-control/lexical_bindings.py','ch8-s1-control/test_r1403_lexical.py']
    request_bytes=(Q/'CI-REQUEST.json').read_bytes();assert request_bytes==(F/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    assert sha(request_bytes)=='9d165365933b6bc117311d7d52568f834bc2f083c2272800803a84883f286717'
    # Verify frozen package/review/GO bytes against their original commits.
    preservation=[]
    prefix='research/challenge-8/kani-k1/kani3300/ch8-s2/'
    for directory,rev in [('batch-r4-r1','474e0b4209554bdd69c4303410192d2d472af4a2'),('review-batch-r4-r1',REVIEW),('go-r4-r1',ENTRY)]:
        files={}
        for p in sorted((G/prefix/directory).iterdir()):
            if not p.is_file():continue
            assert p.read_bytes()==git(G,'show',rev+':'+prefix+directory+'/'+p.name),p
            files[p.name]=sha(p.read_bytes())
        preservation.append({'directory':directory,'commit':rev,'files_sha256':files,'status':'UNCHANGED_COMMITTED_BYTES'})
    patch=git(C,'diff','--binary','--full-index',BASE,local['sha']);(H/'PATCH.patch').write_bytes(patch)
    with tempfile.TemporaryDirectory(prefix='r1403-index-') as tmp:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
        subprocess.run(['git','-C',str(C),'read-tree',BASE],env=env,check=True)
        subprocess.run(['git','-C',str(C),'apply','--cached',str(H/'PATCH.patch')],env=env,check=True)
        assert git(C,'write-tree',env=env).decode().strip()==local['tree']
    pins={'status':'NOT_AN_EXECUTABLE_CI_PACKAGE','entry_g0':ENTRY,'task_document':'research/challenge-8/kani-k1/TASK-CH8-S2-R14-03-BACKLOG-W13.md',
          'task_document_sha256':sha((G/'research/challenge-8/kani-k1/TASK-CH8-S2-R14-03-BACKLOG-W13.md').read_bytes()),
          'frozen_review':REVIEW,'frozen_package':'474e0b4209554bdd69c4303410192d2d472af4a2','frozen_control':frozen,'frozen_source':source,
          'proposed_local_control':local,'changed_paths':paths,
          'patch':{'path':'PATCH.patch','sha256':sha(patch),'base':BASE,'target':local['sha'],'target_tree':local['tree'],'replay':'EXACT_TREE_MATCH'},
          'unchanged_frozen_request_sha256':sha(request_bytes),'request_binding':'FROZEN_REFERENCE_ONLY; local payload map deliberately NOT_REBOUND',
          'workflow_sha256':sha((C/'.github/workflows/ch8-s2.yml').read_bytes()),
          'review_status':'AUTHOR_FIX_FOR_SAME14_GATE_ONLY_REVIEW; INDEPENDENT_CLOSURE_PENDING',
          'current_GO':'UNCHANGED; one-run deferral belongs only to frozen bd62/0e8 inputs',
          'next_integration':'Rebind payload/request and ancestry; independent review and fresh GO required; no automatic integration',
          'native_compile':'NOT_RUN','CI':'NOT_RUN','proof_credit':'NONE','g0_commit':'commit containing this directory; self-reference excluded'}
    dump('PINS.json',pins);dump('PRESERVATION.json',preservation)
    dump('CHANGED-FILES.json',[{'path':p,'before_sha256':sha(git(C,'show',BASE+':'+p)) if p.endswith('/lexical_bindings.py') else None,'after_sha256':sha((C/p).read_bytes())} for p in paths])
    # The frozen checker is loaded read-only with the same unchanged support code.
    spec=importlib.util.spec_from_file_location('frozen_r1403_lexical',F/'ch8-s1-control/lexical_bindings.py')
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    request=json.loads(request_bytes);sources=json.loads((Q/'S2-SOURCE.json').read_text())
    assert (Q/'S2-SOURCE.json').read_bytes()==(F/'ch8-s1-control/S2-SOURCE.json').read_bytes()
    baseline=l.check(S,request);assert baseline==old.check(S,request)
    summary={'status':baseline['status'],'functions':len(baseline['functions']),'static_calls':sum(len(f['static_calls']) for f in baseline['functions']),'contexts':len(baseline['contexts'])}
    trials=[]
    with tempfile.TemporaryDirectory(prefix='r1403-gate-') as tmp:
        root=Path(tmp)
        for rel,text in sources.items():
            p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        semantic=copy.deepcopy(request);removed=semantic.pop('lexical_source_sha256')
        assert all(semantic[k]==v for k,v in request.items() if k!='lexical_source_sha256')
        for depth in (0,1,2,8):
            expression='('*depth+'missing_static'+')'*depth+'();'
            mutation=sources[l.BATCH].replace('fn sort13_weak() {','fn sort13_weak() { '+expression,1)
            (root/l.BATCH).write_text(mutation)
            row={'depth':depth,'expression':expression,'mutated_source_sha256':sha(mutation.encode()),'gates':{}}
            for name,gate in [('frozen',old),('proposed',l)]:
                try:
                    d=gate.check(root,semantic)
                    outcome={'status':d['status'],'static_calls':sum(len(f['static_calls']) for f in d['functions'])}
                except c.GateError as e:outcome={'status':'REJECT','diagnostic':str(e)}
                row['gates'][name]=outcome
            assert row['gates']['proposed']['status']=='REJECT'
            assert 'unresolved static path' in row['gates']['proposed']['diagnostic']
            assert row['gates']['frozen']['status']==('REJECT' if depth<2 else 'STATIC_PASS')
            trials.append(row)
    dump('DISCRIMINATOR.json',{'source':source,'proposed_control':local,'frozen_review':REVIEW,
         'exact_frozen_request_sha256':sha(request_bytes),'only_removed_request_keys':['lexical_source_sha256'],
         'removed_hash_map_sha256':sha(json.dumps(removed,sort_keys=True,separators=(',',':')).encode()),
         'all_other_request_fields':'EXACTLY_UNCHANGED','baseline':summary,'baseline_map':'EXACTLY_EQUAL_FROZEN_AND_PROPOSED',
         'cases':trials,'scope':'Actual lexical gates over temporary fixtures; no Rust execution or typing claim'})
    print('STATIC_PASS: exact frozen source map unchanged; frozen nested skip reproduced; proposed direct/single/double/deeper reject; exact patch replay; frozen GO/input preservation')

if __name__=='__main__':main()
