"""Seal only this review directory; never mutates reviewed inputs."""
import hashlib,json,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;B=H.with_name('batch-r5-r1-stable');G=H.parents[5]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 p=json.loads((B/'PINS.json').read_text());t=json.loads((H/'TARGETED-TESTS.json').read_text());inv=json.loads((H/'INVARIANCE.json').read_text())
 assert t['status']=='PASS' and t['test_count']==28 and len(t['repetitions'])==6 and all(r['pass'] for r in t['repetitions'])
 assert len(t['failure_probes'])==3 and t['transcript_sha256']==sha(H/'TARGETED-TESTS.txt')
 assert t['test_r5_sha256']==sha(Path(p['control']['worktree'])/'ch8-s1-control/test_r5.py')
 assert inv['status']=='PASS' and inv['package_files']==84 and inv['manifest_hashes']==83
 assert json.loads((H/'REEXECUTED-VALIDATION.json').read_text())['state']=='STATIC_TEST_ONLY_DELTA_PASS'
 for kind in ('control','source','tool'):
  path=p[kind]['worktree']
  for field,rev in [('sha','HEAD'),('tree','HEAD^{tree}'),('parent','HEAD^')]:
   assert subprocess.check_output(['git','-C',path,'rev-parse',rev],text=True).strip()==p[kind][field]
  assert not subprocess.check_output(['git','-C',path,'status','--porcelain=v1'])
 subprocess.run(['git','-C',str(G),'diff','--exit-code','805dfa3af4','--',str(H.with_name('go-r5-r1').relative_to(G))],check=True)
 closures=[{'id':'R14-R5-01','status':'CLOSED','basis':'Prior closure plus independently checked exact12min minimum and final-object136PASS446.377637895s; legacy/setup/job/campaign unchanged'}, {'id':'R14-R5-02','status':'CLOSED','basis':'Exact service/packer/collector/runtime invariance to prior APPROVE2ed; four final-object portable regressions PASS'}]
 save('CLOSURES.json',{'verdict':'APPROVE','blocking_findings':[],'prior_review':'2ed2c8ef2f6b9d6460494b85594e3a5f08387a7f','closures':closures,'historical_33PASS_1FAIL_and_isolated_FAIL':'PRESERVED_NOT_RELABELLED'})
 save('REPORT.json',{'verdict':'APPROVE','task_id':p['task_id'],'package':'2906a5b6d3b8451e5b49417714f75e3f9a4af148','control':p['control'],'source':p['source'],'tool':p['tool'],'blocking_findings':[],'targeted_tests':28,'targeted_seconds':t['elapsed_seconds'],'repetitions':6,'failure_subcases':3,'final_Validate':'INSPECTED_AUTHOR_EVIDENCE_136PASS446.377637895s','reviewer_full_Validate_executions':0,'reviewer_check_source_executions':0,'cap_minutes':12,'margin':'1.612984027146456926344455403','closures':closures,'authority':'ROOT_EXACT_GO_REQUEST_ONLY; NO_GO_OR_DISPATCH','root_hold':'805dfa3af4 UNCHANGED','W11':'UNTOUCHED','settings':'UNCHANGED; Fast OFF','native_compiler_fullrunner_CI':'NOT_RUN','proof_credit':'NONE','ledger_budget_reservation':'UNTOUCHED'})
 (H/'HANDOFF.md').write_text('''# W14 — APPROVE; root exact GO-request only

New immutable review of package2906a5b6d3b8451e5b49417714f75e3f9a4af148.
Control63535098ab85c70c8707eee0afd65f53c9ef566a;
tree20f53f18eaafe276a3f1ea74102cbc7c6f3985ac;
sole parent9e14e033f9ee31522b571c127609dcdff76d230b.
Requestd87434d250a1a430c565d8e0612e5a3987f7a811b6cfd9091c268865ff3498b1;
workflow80d1273b9564a16eb4619089db5604ccccdfaa1cb7a155e9703d169c14b58c90.
Sourcebd62e54df1b4749154790aa3db3cc7978f547f75;
tool0aac16ef62da9e9d5645782d458593e5d78143ba; exact clean pins.

No blockers. R14-R5-01/02 CLOSED; priorreview2ed and old33/1+repeatFAIL preserved.
84files83hashes; six patch replays; shallow7/5/2; six-path delta with runtime unchanged.
Reviewer28PASS14.943931344s, exactly3 normal+3 delayed repetitions and forced failure cleanup.
Author final136PASS446.377637895s inspected; cap12min/margin1.612984x;
check-source14.229315844s inspected; reviewer fullValidate/check-source executions0.

Root may finalize exact GO-request for this approved logical r5-r1 candidate.
Existing805dfa HOLD and all go-r5-r1 files remain untouched by reviewer.
No GO issued, dispatch/push/CI/ledger/budget/reservation changes or new proof credit.
W11 independent stub-confirm review untouched. Fast OFF/settings preserved.
Containing ownpaths [skip ci] review commit supplies immutable review identity;
self-reference excluded. REPORT.md and JSON evidence describe assurance/limits.
''')
 save('FINAL-CHECKS.json',{'status':'PASS','inputs_exact_and_clean':True,'root805dfa_hold_unchanged':True,'targeted_transcript_hash_checked':True,'package84_manifest83_checked':True,'inherited_package_and_review_exact':True,'no_compiler_fullrunner_CI_push':True,'no_ledger_budget_mutations':True,'W11_untouched':True,'reviewer_fullValidate_count':0,'reviewer_check_source_count':0})
 files=sorted(x for x in H.iterdir() if x.is_file() and x.name!='MANIFEST.sha256')
 (H/'MANIFEST.sha256').write_text(''.join(sha(x)+'  '+x.name+'\n' for x in files))
 print('APPROVE;',len(files)+1,'review files;',len(files),'manifest hashes; ownpaths only')
if __name__=='__main__':main()
