#!/usr/bin/env python3
"""Record successful actual final-object unittest transcript after exit 0."""
import hashlib,json,re,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
p=json.loads((H/'PINS.json').read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for key in ('source','control'):
    obj=p[key];repo=obj['worktree']
    assert subprocess.check_output(['git','-C',repo,'rev-parse','HEAD'],text=True).strip()==obj['sha']
    assert subprocess.check_output(['git','-C',repo,'rev-parse','HEAD^{tree}'],text=True).strip()==obj['tree']
    assert not subprocess.check_output(['git','-C',repo,'status','--porcelain=v1'],text=True).strip()
q=Path(p['control']['worktree'])/'ch8-s1-control'
assert sha(q/'CI-REQUEST.json')==p['control']['request_sha256']
t=(H/'TARGETED-TESTS.txt').read_text();m=re.search(r'Ran ([0-9]+) tests in ([0-9.]+)s',t)
assert m and t.endswith('\nOK\n')
proof={'source_sha':p['source']['sha'],'source_tree':p['source']['tree'],
       'control_sha':p['control']['sha'],'control_tree':p['control']['tree'],
       'request_sha256':p['control']['request_sha256'],'workflow_sha256':p['control']['workflow_sha256'],
       'argv':['python3','-m','unittest','-v','test_runner.py','test_s107.FinalizationTests','test_s2.py','test_cfg_pfc.py','test_rustc_diagnostics.py','test_contract_stacks.py'],
       'workdir':str(q),'env':{'PYTHONDONTWRITEBYTECODE':'1'},'exit_code':0,
       'test_count':int(m[1]),'elapsed_seconds':float(m[2]),'transcript_sha256':sha(H/'TARGETED-TESTS.txt'),
       'execution':'ACTUAL_FINAL_COMMITTED_SOURCE_CONTROL_REQUEST_WORKFLOW_IDENTITIES',
       'precursor_tests_used_for_final_acceptance':False,
       'scope':'Python/static/synthetic only, including existing runner service success/error/timeout/partial/missing/null/wrong-type/NOT_RUN/mismatch controls. No native compiler, expansion, Kani/CBMC, verifier, full runner or CI.',
       'native_compile':'NOT_RUN','actual_causal_CI_unit':'UNKNOWN','proof_credit':'NONE'}
(H/'TEST-PROVENANCE.json').write_text(json.dumps(proof,indent=2)+'\n')
print('Recorded '+str(proof['test_count'])+' successful actual final-object tests')
