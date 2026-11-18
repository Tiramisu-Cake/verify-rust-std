#!/usr/bin/env python3
"""Commit-object inventories/hashes and immutable frozen-input verification."""
import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PINS.json').read_text())
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def sha(data):return hashlib.sha256(data).hexdigest()

def inventory(repo,base,head):
    names=git(repo,'diff','--name-status',base,head).decode().splitlines();rows=[]
    for line in names:
        status,path=line.split('\t')
        rec={'status':status,'path':path}
        for label,rev in [('base',base),('target',head)]:
            exists=subprocess.run(['git','-C',str(repo),'cat-file','-e',rev+':'+path],capture_output=True).returncode==0
            rec[label]=({'blob':git(repo,'rev-parse',rev+':'+path).decode().strip(),
                         'sha256':sha(git(repo,'show',rev+':'+path))} if exists else None)
        rows.append(rec)
    return {'base':base,'target':head,'paths':rows}

def main():
    records={}
    for label in ('source','control'):
        item=P[label];repo=Path(item['worktree']);old=item['derivation_'+label]
        for kind,base in [('frozen_r4',old),('sole_parent',item['parent']),('candidate_baseline',item['base'] if label=='source' else P['tool']['sha'])]:
            records[label+'_'+kind]=inventory(repo,base,item['sha'])
    source_delta=records['source_frozen_r4']['paths']
    assert len(source_delta)==1 and source_delta[0]['path'].endswith('/sorting_s2_batch.rs')
    S=Path(P['source']['worktree']);C=Path(P['control']['worktree'])
    assert git(S,'diff','--numstat',P['source']['derivation_source'],P['source']['sha']).decode().split('\t')[:2]==['1','1']
    for rel in ('ch8-s1-control/pack_evidence.py','ch8-s1-control/collect.py','ch8-s1-control/rich_evidence.py',
       'ch8-s1-control/rustc_diagnostics.py','ch8-s1-control/check_package.py','ch8-s1-control/negative_oracle.py','.github/workflows/ch8-s2.yml'):
        assert git(C,'show',P['control']['derivation_control']+':'+rel)==git(C,'show',P['control']['sha']+':'+rel),rel
    frozen=[]
    for dirname,rev in [('batch-r4','4e2801660d89d75a1357a420c78cd435159c35b3'),('review-batch-r4','f5dd71722f82ac59e37152927a5f4dd9eee6ea1a')]:
        directory=HERE.with_name(dirname);rel=str(directory.relative_to(Path('/root/verify-rust-std-kani3300-g0')))
        for p in directory.iterdir():
            if p.is_file():assert p.read_bytes()==git(HERE,'show',rev+':'+rel+'/'+p.name),p
        frozen.append({'package':dirname,'commit':rev,'files':sum(p.is_file() for p in directory.iterdir()),'status':'UNCHANGED_COMMITTED_BYTES'})
    records.update(frozen_packages=frozen,scope='Full source baseline and stock-control deltas, plus bounded frozen-r4 delta and sole-parent deltas; no proof claim')
    (HERE/'FULL-INVENTORIES.json').write_text(json.dumps(records,indent=2)+'\n')
    print('PASS: full inventories; sole parents; one-line source repair; protected control bytes; frozen packages unchanged')
if __name__=='__main__':main()
