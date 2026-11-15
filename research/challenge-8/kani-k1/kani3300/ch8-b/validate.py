#!/usr/bin/env python3
"""Offline research-to-committed-CI binding. No compiler or external calls."""
import csv, hashlib, json, pathlib, subprocess, sys
here=pathlib.Path(__file__).resolve().parent
repo=here.parents[4]
check=json.loads((here/'CHECKPOINT.json').read_text())
ci=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('/root/kani-ch8-b-census-w14')
def git(r,*a): return subprocess.check_output(['git','-C',str(r),*a])
def sha(b): return hashlib.sha256(b).hexdigest()
head=check['ci_commit']
req=json.loads((here/'CI-REQUEST.json').read_text())
for name in ('CI-REQUEST.json','roots.json'):
    assert (here/name).read_bytes()==git(ci,'show',head+':scripts/ch8-b-census/'+name)
roots=json.loads((here/'roots.json').read_text())
base=git(repo,'show',req['inventory']['g0_sha']+':'+req['inventory']['path']+'/baseline-roots.tsv')
assert sha(base)==req['inventory']['baseline_sha256']
old=list(csv.DictReader(base.decode().splitlines(),delimiter='\t'))
assert len(old)==len(roots)==235
assert {(r['harness'],int(r['ubuntu_partition'])) for r in old}=={(r['root'],r['shard']) for r in roots}
assert all(r['ubuntu_partition']==r['macos_partition'] for r in old)
assert not any(r['intended_invalid_value'] for r in roots)
changes=git(ci,'diff','--name-only',req['kani']['sha'],head).decode().splitlines()
assert changes and all(p in {'.github/workflows/'+n for n in ('ch8-b-census.yml','kani.yml','deny.yml','format-check.yml')} or p.startswith('scripts/ch8-b-census/') for p in changes)
assert '[skip ci]' in git(ci,'show','-s','--format=%B',head).decode()
assert check['accounting']=={'dispatches':0,'pushes':0,'local_builds':0,'ledger_writes':0}
print(json.dumps({'status':'PASS','ci_commit':head,'roots':235,'inventory_sha256':sha((here/'roots.json').read_bytes()),'proof_credit':'NONE'}))
