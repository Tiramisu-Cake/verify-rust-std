"""Read-only exact-package audit; patch replay uses temporary indexes only."""
import ast, decimal, hashlib, importlib.util, json, os, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent; B=H.with_name('batch-r5-r1-stable'); G=H.parents[5]
PACKAGE='2906a5b6d3b8451e5b49417714f75e3f9a4af148'
PRIOR='2ed2c8ef2f6b9d6460494b85594e3a5f08387a7f'
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def sha(data):return hashlib.sha256(data).hexdigest()
def save(name,value):(H/name).write_text(json.dumps(value,indent=2)+'\n')
def main():
 p=json.loads((B/'PINS.json').read_text()); C=Path(p['control']['worktree']); Q=C/'ch8-s1-control'
 assert p['task_id']=='task6d7c4739def196654459faf05b7e1c36ace03e93'
 files=git(G,'ls-tree','-r','--name-only',PACKAGE,'--',str(B.relative_to(G))).decode().splitlines()
 assert len(files)==84
 for name in files:assert (G/name).read_bytes()==git(G,'show',PACKAGE+':'+name),name
 manifest=(B/'MANIFEST.sha256').read_text().splitlines(); assert len(manifest)==83
 for line in manifest:
  digest,name=line.split(maxsplit=1);assert sha((B/name.lstrip('*')).read_bytes())==digest,name
 old='d67bd1ecd555030c46a06b8462d0313ea416711a'; new=p['control']['sha']
 changed=git(C,'diff','--name-only',old,new).decode().splitlines()
 assert changed==['.github/workflows/ch8-s2.yml','ch8-s1-control/CI-REQUEST.json','ch8-s1-control/check_package.py','ch8-s1-control/r5_profile.py','ch8-s1-control/test_r5.py','ch8-s1-control/test_s2.py']
 def tree(rev):return {line.split('\t',1)[1]:line.split('\t',1)[0] for line in git(C,'ls-tree','-r',rev).decode().splitlines()}
 before,after=tree(old),tree(new); assert before.keys()==after.keys()
 same=[n for n in before if before[n]==after[n]];assert len(same)+6==len(before)
 def methods(raw):
  node=ast.parse(raw);return {(cl.name,fn.name):ast.dump(fn,include_attributes=False) for cl in node.body if isinstance(cl,ast.ClassDef) for fn in cl.body if isinstance(fn,ast.FunctionDef)}
 a=methods(git(C,'show',old+':ch8-s1-control/test_r5.py'));b=methods((Q/'test_r5.py').read_bytes())
 altered=[k for k in a if a[k]!=b[k]];assert altered==[('ProcessTests','test_escaped_setsid_child_found_and_reaped')]
 assert len(b)==len(a)+4
 for directory,commit in [(H.with_name('batch-r5-r1'),'dc8d28b0117737e95ccc9b91eb470c1a3c42a635'),(H.with_name('review-batch-r5-r1'),PRIOR)]:
  for name in git(G,'ls-tree','-r','--name-only',commit,'--',str(directory.relative_to(G))).decode().splitlines():
   assert (G/name).read_bytes()==git(G,'show',commit+':'+name)
 # Reexecute the reviewed author's static checks without writing to its packet.
 spec=importlib.util.spec_from_file_location('packet_audit',B/'validate_package.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 m.dump=lambda name,value:save('REEXECUTED-'+name,value)
 m.main()
 timing=json.loads((B/'STABLE-FINAL-VALIDATE-TIMING.json').read_text());D=decimal.Decimal
 seconds=D(timing['monotonic_end_ns']-timing['monotonic_start_ns'])/D(10**9)
 assert seconds==D('446.377637895') and D(720)/seconds>=D('1.5')
 assert (D('1.5')*seconds/D(60)).to_integral_value(rounding=decimal.ROUND_CEILING)==12
 prior=json.loads((B/'PRECURSOR-STABLE-FINAL-VALIDATE-TIMING.json').read_text())
 assert D(660)/D(str(prior['elapsed_seconds']))<D('1.5')
 log=(B/'STABLE-FINAL-VALIDATE.txt').read_text();assert len([x for x in log.splitlines() if x.endswith(' ... ok')])==136
 reviewlog=(B/'PRIOR-REVIEW-TARGETED-TESTS.txt').read_text();assert 'FAILED (failures=1)' in reviewlog and 'Ran 34 tests' in reviewlog
 save('INVARIANCE.json',{'status':'PASS','changed_paths':changed,'unchanged_tree_entries':len(same),'total_tree_entries':len(before),'old_test_methods':len(a),'new_test_methods':len(b),'altered_existing_test_methods':altered,'production_runtime_campaign_collector_runner_packer_protected_controls':'EXACT_GIT_BLOBS_UNCHANGED','prior_package_and_review':'ALL_COMMITTED_BYTES_UNCHANGED','package_files':len(files),'manifest_hashes':len(manifest),'source_tool':'EXACT_CLEAN_PINS','full_validate_reviewer_executions':0})
 save('VALIDATE-MARGIN.json',{'status':'PASS','assurance':'INSPECTED_AUTHOR_FINAL_OBJECT_EVIDENCE_NOT_REVIEWER_FULL_EXECUTION','control':p['control'],'tests':136,'monotonic_seconds':str(seconds),'cap_minutes':12,'ratio':str(D(720)/seconds),'smallest_whole_minutes':12,'precursor_seconds':prior['elapsed_seconds'],'precursor_11min_margin':'FAIL_PRESERVED','check_source_seconds':json.loads((B/'STABLE-CHECK-SOURCE-TIMING.json').read_text())['elapsed_seconds'],'setup_aggregate_seconds':1800,'job_minutes':180,'campaign_seconds':6900,'strict_legacy_minutes':10,'future_CI_timing':'UNKNOWN','proof_credit':'NONE'})
 save('INPUTS.json',{'task':'TASK-CH8-S2-R5-TEST-STABILITY-REVIEW-W14.md','task_id':p['task_id'],'owner_override':'21:46 /new overrides prepared reuse context; fresh main review; no subagents','package':PACKAGE,'pins':p,'pins_sha256':sha((B/'PINS.json').read_bytes()),'prior_review':PRIOR,'package_file_hashes':{str(Path(n).relative_to(B.relative_to(G))):sha((G/n).read_bytes()) for n in files},'settings':'UNCHANGED; Fast OFF','constraints':'No candidate edits, compiler, full runner, CI, push, ledger or budget mutation; W11 untouched'})
 print('PASS:84 files/83 hashes; exact six-path delta; inherited closures; margin; patch/shallow replay')
if __name__=='__main__':main()
