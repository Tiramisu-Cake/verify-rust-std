#!/usr/bin/env python3
"""Seal successful final-object gate-only evidence; never integrate or dispatch."""
import ast,hashlib,json,re,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent
G=Path('/root/verify-rust-std-kani3300-g0')

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])

def main():
    p=json.loads((H/'PINS.json').read_text());control=p['proposed_local_control'];C=Path(control['worktree']);Q=C/'ch8-s1-control'
    assert git(C,'rev-parse','HEAD').decode().strip()==control['sha']
    assert not git(C,'status','--porcelain=v1').decode().strip()
    transcript=(H/'TESTS.txt').read_text();match=re.search(r'Ran ([0-9]+) tests in ([0-9.]+)s',transcript)
    assert match and transcript.endswith('\nOK\n')
    tests={'status':'PASS','control':control,'request_sha256':sha(Q/'CI-REQUEST.json'),
           'execution':'ACTUAL_FINAL_COMMITTED_LOCAL_CONTROL; TEMPORARY_SOURCE_MUTATIONS_ONLY',
           'argv':['python3','-m','unittest','-v','test_r1403_lexical','test_cfg_pfc.LexicalBindingTests','test_cfg_pfc.RepairAliasTests','test_cfg_pfc.CfgPfcTests.test_full_target_and_attribute_aliases','test_cfg_pfc.CfgPfcTests.test_missing_wrong_cfg_cfg_attr_and_disabled_pfc'],
           'workdir':str(Q),'env':{'PYTHONDONTWRITEBYTECODE':'1'},'exit_code':0,'test_count':int(match[1]),'elapsed_seconds':float(match[2]),'transcript_sha256':sha(H/'TESTS.txt'),
           'scope':'New extractor/full lexical-gate discriminators and affected existing lexical/alias/cfg tests only; full96 NOT_REPEATED',
           'native_compiler':'NOT_RUN','verifier':'NOT_RUN','CI':'NOT_RUN','proof_credit':'NONE'}
    assert tests['test_count']==23
    dump('TEST-PROVENANCE.json',tests)
    before=ast.parse(git(C,'show',control['parent']+':ch8-s1-control/lexical_bindings.py').decode())
    after=ast.parse((Q/'lexical_bindings.py').read_text())
    def outside_call_paths(tree):
        tree.body=[n for n in tree.body if not (isinstance(n,ast.FunctionDef) and n.name=='call_paths')]
        return ast.dump(tree,include_attributes=False)
    assert outside_call_paths(before)==outside_call_paths(after)
    for file in (Q/'lexical_bindings.py',Q/'test_r1403_lexical.py'):ast.parse(file.read_text())
    for record in json.loads((H/'PRESERVATION.json').read_text()):
        for file,digest in record['files_sha256'].items():
            path=G/'research/challenge-8/kani-k1/kani3300/ch8-s2'/record['directory']/file
            assert sha(path)==digest,path
    for obj in (p['frozen_source'],p['frozen_control']):
        assert git(obj['worktree'],'rev-parse','HEAD').decode().strip()==obj['sha']
        assert not git(obj['worktree'],'status','--porcelain=v1').decode().strip()
    assert sha(H/'PATCH.patch')==p['patch']['sha256']
    assert sha(Q/'CI-REQUEST.json')==p['unchanged_frozen_request_sha256']
    subprocess.run(['git','-C',str(C),'diff','--check',control['parent'],control['sha']],check=True)
    discriminator=json.loads((H/'DISCRIMINATOR.json').read_text())
    exact=next(x for x in discriminator['cases'] if x['depth']==2)
    assert exact['gates']['frozen']['status']=='STATIC_PASS' and exact['gates']['proposed']['status']=='REJECT'
    assert exact['mutated_source_sha256']=='ac46aa6f9acdf70382b9b21367445b141e7ec115c2e7436d821c2980865a9edb'
    validation={'status':'STATIC_PASS','package_status':'NOT_AN_EXECUTABLE_CI_PACKAGE','control':control,
       'code_delta':'call_paths ONLY; AST outside call_paths identical','tests':tests,'patch_replay':p['patch'],
       'baseline_map':'EXACTLY_EQUAL_FROZEN_AND_PROPOSED; 77 calls/8 functions/11 contexts',
       'frozen_GO_and_review_and_package':'UNCHANGED_COMMITTED_BYTES_BEFORE_AND_AFTER',
       'source_and_model_and_request_and_workflow_and_caps':'UNCHANGED',
       'payload_request_ancestry_rebinding':'NOT_PERFORMED; required for any next integration',
       'independent_review':'PENDING_SAME14_GATE_ONLY_DELTA','finding':'AUTHOR_FIX_SUBMITTED; NOT_INDEPENDENTLY_CLOSED',
       'native_compile':'NOT_RUN','proof_credit':'NONE'}
    dump('VALIDATION.json',validation)
    pins=f'''Proposed local control {control['sha']}
Tree {control['tree']}
Sole parent {control['parent']}
Worktree {control['worktree']}
Patch SHA256 {p['patch']['sha256']}
Entry G0/task commit {p['entry_g0']}
Frozen review {p['frozen_review']}
Frozen source {p['frozen_source']['sha']}
Frozen control {p['frozen_control']['sha']}
Frozen request reference SHA256 {p['unchanged_frozen_request_sha256']}
G0 output identity is the commit containing this directory, reported in READY.
'''
    body=f'''NOT_AN_EXECUTABLE_CI_PACKAGE. Author fix for SAME14 gate-only delta review;
R14-03 independent closure remains pending. R14-01/R14-02 remain CLOSED in frozen review.

{pins}
The proposed control is a new child of frozen0e8 in an isolated worktree. Exactly
two paths differ: lexical_bindings.py and new targeted test_r1403_lexical.py.
Only call_paths changes in the checker; AST outside it is identical. Fixtures,
source/model/contracts, cfg, oracles, caps, tool, runner and workflows are unchanged.

call_paths now unwraps complete nested parentheses around its supported static
paths iteratively; token offsets still identify the actual path for lexical scope
checks. Direct/single/double/deeper paths resolve once, including qualified paths,
aliases, local functions and callable values. Tested extractor depths reach2048.
The guard rejects unsupported grouped/index/block/direct-call-result callee forms
with line diagnostics; it prevents tuple/deref/member/closure/computed-call shapes
from disappearing through the repaired parenthesis path. Parenthesized receiver
method calls remain explicitly inventoried as METHOD, without resolution credit.

The exact review mutation fn sort13_weak() {{ ((missing_static))(); is replayed
through both actual frozen and proposed lexical gates on temporary fixtures.
Only lexical_source_sha256 is removed; all other request fields are unchanged.
Its SHA256 matches frozen review. Frozen gate silently accepts77 calls; proposed
gate rejects unresolved missing_static. Direct/single/depth8 unbound forms reject.
The exact unmodified source is accepted and its entire baseline map equals the
frozen map:77 static calls,8 functions,11 contexts.

{tests['test_count']}/{tests['test_count']} actual final-committed-object targeted tests pass. These include new
discriminators plus affected existing lexical, alias and selected cfg/PFC controls.
Full96 runner suite NOT_REPEATED. An initial targeted run had one diagnostic-expectation
mismatch in a synthetic scope test; an explicit semicolon now separates its block.
The checker bytes did not change. PRECURSOR-TESTS.txt/PRECURSOR-NOTES.json preserve
that failure without acceptance credit; the successful final run is separate.
TEST-PROVENANCE.json binds the actual transcript;
DISCRIMINATOR.json records full-gate rejection, and PATCH.patch replays to the exact tree.
PRESERVATION.json confirms frozen package474e, reviewe783 and GO6db bytes unchanged,
with clean exact frozen source/control worktrees checked before and after testing.

This is a finite token extractor/guard repair, not a general Rust expression parser
or complete name/type checker. Supported parentheses contain one already-supported
path. Other callable-expression coverage is limited to the explicitly guarded
forms; no broader syntax completeness is claimed. Methods, associated-type/trait
selection, executable expansion, typing, borrow checking and MIR remain outside
scope. Rust snippets are scanner input only. Native compile/verifier/full runner/CI
and causal repair NOT_RUN; actual R3 failing unit/body UNKNOWN; proof credit NONE.

The frozen bd62/0e8 one-run GO and its scoped R14-03 deferral are unchanged. That
exception applies only to its exact inputs and supplies no next-revision CI credit.
This child deliberately retains the old payload/request/workflow bytes and ancestry;
they are NOT rebound to this patch. Next integration must rebind payload/request and
ancestry, receive independent review and fresh GO. No automatic integration.
No compiler/CI/rerun/cancel/push/PR/issue/source publication/ledger/reservation/budget
operation or external message. Current settings retained; Fast OFF per owner unchanged;
no subagents. SAME14 gate-only delta review is the next local handoff.
'''
    (H/'REPORT.md').write_text('# R14-03 gate backlog — author fix for review\n\n'+body)
    (H/'HANDOFF.md').write_text('# READY — SAME14 gate-only delta review\n\n'+body)
    (H/'REVIEW14-REQUEST.md').write_text('# SAME14 gate-only delta review request\n\nPlease review only the two-path patch against frozen0e8 and R14-03.\nAdjudicate nested path extraction and unsupported-expression guards; do not\nintegrate, rebind current GO inputs or prepare CI from this backlog.\n\n'+body)
    files=sorted(file for file in H.iterdir() if file.is_file() and file.name!='MANIFEST.sha256')
    (H/'MANIFEST.sha256').write_text(''.join(sha(file)+'  '+file.name+'\n' for file in files))
    print('READY: '+str(tests['test_count'])+' targeted tests, exact discriminator/patch/preservation; NOT_AN_EXECUTABLE_CI_PACKAGE')
if __name__=='__main__':main()
