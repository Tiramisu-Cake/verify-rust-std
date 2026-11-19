"""Bounded PR5159 identity, scope, harness and expected-matcher review checks."""
from pathlib import Path
import hashlib,json,re,subprocess
OUT=Path(__file__).resolve().parent
MAIN=Path('/root/verify-rust-std-kani3300-g0')
BASE=MAIN/'research/challenge-8/kani-k1'
INPUT=BASE/'kani3300/wave0/open-pr-slop-next-inputs-20261119/pr-5159'
SOURCE=Path('/root/kani-pr5159-slop-readonly-20261119')
TASK='98784e2ade6135d3177b0ad14c9ab88777ab6aa2'
D=lambda raw:hashlib.sha256(raw).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(SOURCE),*args])
r=json.loads((INPUT/'INPUTS.json').read_text())
for path in [INPUT/'INPUTS.json',INPUT/'CONNECTED-PR.json',INPUT/'SOURCE.patch',INPUT/'PR-BODY.snapshot.md',INPUT.parent/'STYLE-UPSTREAM-RULES.snapshot.md',INPUT.parent/'ROOT-DECISION.md']:
    raw=subprocess.check_output(['git','-C',str(MAIN),'show',TASK+':'+str(path.relative_to(MAIN))]);assert raw==path.read_bytes()
assert git('rev-parse','HEAD').decode().strip()==r['head']
assert git('rev-parse','HEAD^{tree}').decode().strip()==r['head_tree']
assert git('merge-base',r['head'],r['base_snapshot']).decode().strip()==r['merge_base']
assert not git('status','--porcelain=v1')
assert len(git('show','-s','--format=%P',r['head']).decode().split())==2
assert set(git('diff','--name-only',r['merge_base'],r['head']).decode().splitlines())==set(r['changed_files'])
for name,item in r['changed_files'].items():
    raw=(SOURCE/name).read_bytes();assert D(raw)==item['sha256'] and len(raw)==item['bytes']
    assert git('rev-parse',r['head']+':'+name).decode().strip()==item['git_blob']
assert git('diff','--binary','--full-index',r['merge_base'],r['head'])==(INPUT/'SOURCE.patch').read_bytes()
assert D((INPUT/'SOURCE.patch').read_bytes())==r['diff_sha256']
assert D((INPUT/'PR-BODY.snapshot.md').read_bytes())==r['PR_body_sha256']
connected=json.loads((INPUT/'CONNECTED-PR.json').read_text());assert connected['body']==(INPUT/'PR-BODY.snapshot.md').read_text()
rs=[name for name in r['changed_files'] if name.endswith('.rs') and name.startswith('tests/')]
tests={name:re.findall(r'#\[kani::proof\]\s*(?:pub\s+)?(?:unsafe\s+)?fn\s+(\w+)',(SOURCE/name).read_text()) for name in rs}
assert len(rs)==3 and sorted(len(names) for names in tests.values())==[1,1,6]
assert not any('kani-verify-fail' in (SOURCE/name).read_text() for name in rs)
assert all('// compile-flags: --edition 2021' in (SOURCE/name).read_text() for name in rs)
# Port TestCx's existing substring/consecutive-line matcher; run no upstream driver.
def contains(lines,parts):
    return any(all(part.strip() in line for part,line in zip(parts,lines[start:])) for start in range(len(lines)-len(parts)+1))
def accepts(output,expected):
    lines=output.split('\n');pending=[]
    for line in expected.split('\n'):
        if line.endswith('\\'):pending.append(line[:-1])
        else:
            pending.append(line)
            if not contains(lines,pending):return False
            pending=[]
    return not pending or contains(lines,pending)
oracle_checks=[]
for name in r['changed_files']:
    if not name.endswith('.expected'):continue
    expected=(SOURCE/name).read_text()
    assert 'VERIFICATION:- FAILED' in expected and 'Failed Checks:' in expected
    assert not any(word in expected.lower() for word in ('panicked at','internal compiler error','unimplemented!'))
    assert not accepts('error: compiler setup failed',expected)
    message=expected.splitlines()[1]
    incomplete='Status: FAILURE\n'+message+'\nFailed Checks: '+message+'\nVERIFICATION:- FAILED\ninternal compiler error: synthetic tail failure'
    assert accepts(incomplete,expected)
    harness=tests[name[:-len('.expected')]+'.rs'][0]
    stronger='Checking harness '+harness+'...\n'+expected+'Complete - 0 successfully verified harnesses, 1 failures, 1 total.\n'
    assert not accepts(incomplete,stronger)
    assert accepts('Checking harness '+harness+'...\n'+incomplete.split('\ninternal compiler error:')[0]+'\nComplete - 0 successfully verified harnesses, 1 failures, 1 total.',stronger)
    oracle_checks.append({'file':name,'setup_only_rejected':True,'intended_diagnostic_required':message,'incomplete_failure_output_currently_matches':True,'named_harness_and_complete_summary_rejects_that_output':True,'native_crash_reproduced':False})
receipt={'schema':'pr5159-static-review-checks-v1','status':'STATIC_CHECKS_PASS','task':TASK,'head':r['head'],'tree':r['head_tree'],'base_merge_base':r['merge_base'],
 'exact_changed_blobs_verified':6,'merge_head_not_premerge':True,'source_clean':True,'source_test_files':3,'proof_harnesses':tests,'total_proof_harnesses':8,
 'positive_harnesses':6,'negative_expected_harnesses':2,'test_flags':'edition2021, explicit manual proof harnesses; no skip/verify-fail or additional kani flags',
 'oracle_checks':oracle_checks,'scope':'Identity and literal-source/matcher checks only; no compiler/MIR/native or CI execution',
 'native_main_fail_head_pass':'NOT_RUN','supported_diagnostics_preserved':True,'source_edits':False}
(OUT/'STATIC-CHECKS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('status','exact_changed_blobs_verified','total_proof_harnesses','positive_harnesses','negative_expected_harnesses','native_main_fail_head_pass')}))
