#!/usr/bin/env python3
"""Write this review only after successful independent checks."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def dump(name, value):
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    inputs = json.loads((OUT/'INPUTS.json').read_text())
    pins = inputs['pins']
    checks = json.loads((OUT/'CHECKS.json').read_text())
    tests = json.loads((OUT/'TEST-PROVENANCE.json').read_text())
    discriminator = json.loads((OUT/'DISCRIMINATOR.json').read_text())
    extractor = json.loads((OUT/'EXTRACTOR-CHECKS.json').read_text())
    assert checks['status'] == 'STATIC_PASS'
    assert tests['count'] == 23 and tests['exit_code'] == 0
    assert discriminator['outcomes']['frozen']['status'] == 'STATIC_PASS'
    assert discriminator['outcomes']['proposed']['status'] == 'REJECT'
    assert extractor['status'] == 'PASS'
    closure = {'id':'R14-03','priority':'P2','status':'CLOSED',
               'scope':'Exact gate-only patch ONLY; historical e783 review and frozen control remain immutable',
               'control':pins['proposed_local_control'],'patch':pins['patch'],
               'basis':'Exact frozen nested-call discriminator changes from silent accept to unresolved-path rejection; nested supported paths resolve once with original token offsets; unsupported grouped/index/block/call-result callees reject',
               'evidence':['DISCRIMINATOR.json','EXTRACTOR-CHECKS.json','FINAL-TESTS.txt','CHECKS.json'],
               'assurance':'OFFLINE_STATIC_SYNTHETIC_ONLY','native_compile':'NOT_RUN','proof_credit':'NONE'}
    dump('FINDING-CLOSURE.json',closure)
    (OUT/'FINDING-CLOSURE.md').write_text('''R14-03/P2 CLOSED for exact gate patch
1dfaf5a1fa2d748e81bea4093018eb65972d7cfc807e47c0d1f7ad39565f8cba
at local control0e97a487d8b7f8e8cbced5dbe2b6909c7150c695 ONLY.

The identical frozen review mutation ((missing_static))() is silently accepted
by frozen0e8 and rejected as unresolved by the proposed gate, after removing only
synthetic lexical_source_sha256. Supported nested static paths are recorded once;
original token indices retain local callable scope/order. Legitimate full paths,
aliases/local functions/local callable values and deeper nesting are exercised.
Unsupported callable forms receive explicit fail-closed diagnostics. Baseline map
is exactly unchanged:77 calls/8 functions/11 contexts. Independent23/23 targeted
final-object tests pass, including affected alias/cfg controls. Precursor failure
is preserved and has no acceptance credit. Method/type/trait/MIR limits remain.

R14-01 and R14-02 closure is inherited unchanged. No historical review finding
record or frozen source/control/GO is rewritten. NOT_AN_EXECUTABLE_CI_PACKAGE;
payload/request/ancestry rebinding and required next-candidate review/GO remain.
No native compile, verifier, full runner, CI or integration; proof credit NONE.
''')
    report = {'schema':'ch8-s2-r1403-gate-only-same14-review-v1',
              'task_id':inputs['task_id'],'issued':inputs['issued'],'verdict':'APPROVE',
              'finding':closure,'new_blockers':[], 'package_commit':inputs['package_commit'],
              'frozen_review':pins['frozen_review'],'frozen_package':pins['frozen_package'],
              'frozen_source':pins['frozen_source'],'frozen_control':pins['frozen_control'],
              'local_control':pins['proposed_local_control'],'patch':pins['patch'],
              'review_scope':'Bounded call_paths/extractor/guard/new tests only; no broad audit',
              'R14-01':'CLOSED_INHERITED_UNCHANGED','R14-02':'CLOSED_INHERITED_UNCHANGED',
              'validation':checks,'targeted_tests':tests,
              'additional_extractor_checks':{'supported_cases':21,'depth_max_tested':4096,'unsupported_cases':9},
              'baseline_map':'EXACT77_STATIC_CALLS8_FUNCTIONS11_CONTEXTS_UNCHANGED',
              'package_status':'NOT_AN_EXECUTABLE_CI_PACKAGE',
              'precursor_failure':'PRESERVED_NO_ACCEPTANCE_CREDIT; checker identical; final test inserts semicolon to distinguish separate block from callable expression',
              'limits':['Finite token extractor/guard only; no general Rust parser or arbitrary syntax completeness',
                        'Methods/macros remain inventoried without dispatch resolution credit',
                        'Associated-type/trait selection, typing, expansion, borrow checking, MIR and native compile NOT_RUN'],
              'owner_reported_context':{'run':'44328364855','outcome':'FAILED_PREBUILD_VALIDATE_1MIN','roots':0,'charged':0,
                                       'assurance':'OWNER_SUPPLIED; NOT_REAUDITED_IN_THIS_GATE_REVIEW',
                                       'timeout10min_audit_task':'16a; independently prepared by NEW13; outside this review'},
              'integration':'NOT_PERFORMED; exact approved patch may be selected for separately bound next candidate; required review/GO remain',
              'historical_GO':'UNCHANGED; no CI credit or exception transfer',
              'native_compile':'NOT_RUN','verifier':'NOT_RUN','full_runner':'NOT_RUN','CI':'NOT_RUN',
              'causal_repair':'NOT_RUN','actual_r3_unit_body':'UNKNOWN','proof_credit':'NONE','closed_proof_obligations':0,
              'external_actions':{key:0 for key in ('compiler','CI','push','PR','issue','ledger','budget','integration','subagents')},
              'Fast':'OFF_PER_OWNER_UNCHANGED','settings':'CURRENT_UNCHANGED',
              'next':'Local HANDOFF to original13 current new role; exact patch only, no automatic CI',
              'review_commit':'Containing commit; full SHA in READY, omitted here to avoid circular identity'}
    dump('REPORT.json',report)
    (OUT/'REPORT.md').write_text('''# SAME14 gate-only delta — APPROVE; R14-03 CLOSED

Approval covers ONLY patch SHA256
**1dfaf5a1fa2d748e81bea4093018eb65972d7cfc807e47c0d1f7ad39565f8cba**,
package **4eccefc670602b58f25f9c55a27da2d844cdcf18**, proposed local control
**0e97a487d8b7f8e8cbced5dbe2b6909c7150c695**,
tree **b980862474e3630c459ee147def4fa45f3ea42fd**, sole parent
**0e8c836857344866564e1423ad5d8d28bbc4106b**.
Task task6db728b62b62d6d98d683f3d2cf6fb824dd6cc68, issued owner17:54.
No new blocker was found in this bounded delta. No implementation was changed.

## Closure and bounded code review

At lexical_bindings.py:62-71, the new iterative delimiter pass validates balance
and maps closing delimiters to their actual opening positions. Lines93-107 unwrap
only complete parentheses around an already-supported static path. They yield one
record with the original path token offset, preserving downstream local-value
scope and declaration-order checks. The covered set marks the outer callable
boundary; nested argument calls remain separate records.

Lines102-105 reject call-result confusion such as factory(argument)(). The final
guard at115-119 rejects unsupported grouped/index/block callees instead of dropping
them. Tuple/deref/member/closure/computed-call forms have distinguishing reject
tests. Parenthesized receivers still produce METHOD inventory only; no method
or type-resolution credit is added. Unsupported syntax may be conservatively
rejected. This is a finite extractor repair, not a general Rust expression parser.

The exact frozen-review mutation `fn sort13_weak() { ((missing_static))();`
has the same mutated-source hash as e783's discriminator. Independent actual
gate execution with only synthetic lexical_source_sha256 removed reproduces
frozen0e8 STATIC_PASS with77 calls and proposed-gate REJECT for unresolved
missing_static. All other request fields are unchanged. DISCRIMINATOR.json records
this paired execution. R14-03/P2 therefore closes for this exact proposed patch.
The historical e783 review remains unchanged; R14-01/R14-02 closure is inherited.

## Independent targeted validation

INPUTS.json records committed package/task hashes, exact local/frozen identities
and the reviewed patch. Only lexical_bindings.py and new test_r1403_lexical.py
differ from0e8. AST outside call_paths is identical. The patch bytes match the
exact committed binary/full-index diff and replay to treeb980862 in an isolated
temporary index. No worktree integration was performed.

This review independently ran **23/23 final-object targeted tests**, covering
the new extractor/full-gate discriminator, existing lexical and chained-alias
controls, and selected cfg/PFC controls. FINAL-TESTS.txt and TEST-PROVENANCE.json
record this run; the author's transcript is preserved separately. The full96
runner suite was not repeated. A further independent extractor check covers21
supported path/depth cases through4096 parentheses,9 unsupported nested callable
forms, nested argument calls and METHOD inventory. All pass.

Legitimate full paths, aliases, local functions and local callable values are
exercised at direct/single/double/deeper depths. Callable declaration order and
block scope retain rejecting controls. Extractor depths2048 and4096 are tested;
the implementation is iterative and imposes no fixed parenthesis-depth bound.
This does not claim unlimited resources or complete Rust syntax support.

The unmodified exact source passes the proposed gate with its exact lexical hash
map. Its entire returned baseline map equals both the frozen gate's result and
the committed baseline map: **77 calls,8 functions,11 cfg contexts**, unchanged.
No source/model/contracts/oracles/cfg/caps/tool/runner/workflow change occurs.
The old request and payload bytes deliberately remain unrebound.

The package preserves the precursor23-test run with one expectation failure.
Its checker hash equals the final checker's hash. Only the synthetic test adds
a semicolon after a separate block so it reaches the intended unresolved-binding
diagnostic. That precursor run receives no acceptance credit; the successful final
run and this independent successful run are distinct evidence.

PRESERVATION.json verifies frozen package474e, reviewe783 and GO6db bytes against
their original commits before and after checks. Exact frozen sourcebd62/control0e8
worktrees and the proposed local control remain clean and at their pinned HEADs.
Nothing rewrites historical review, GO, evidence or ledger state.

## Approval boundary and handoff

**NOT_AN_EXECUTABLE_CI_PACKAGE.** Approval permits selecting only this exact patch
for the separately prepared next candidate. Integration must bind its actual
payload/request and ancestry, with the required candidate review and fresh GO.
This review performs no integration and grants no compiler/CI/dispatch authority.
The frozen one-run exception supplies no next-revision CI credit.

Owner supplied run44328364855 as failed in prebuild Validate's1-minute step,
0 roots/charged0. Those facts are owner-reported context, not reaudited here.
NEW13's separate task16a timeout10min/audit preparation is outside this review;
this gate-only approval does not approve that workflow change or its package.

Method/macro expansion, associated-type/trait selection, typing, borrowing and
MIR remain outside the lexical gate. Native compile/verifier/full runner/CI and
causal repair NOT_RUN; actual R3 failing unit/body UNKNOWN. No independent B1/B2
proof credit; closed proof obligations0. No push/PR/issue/ledger/budget/integration
or external message. Current settings and Fast OFF per owner preserved; no subagents.

HANDOFF.md routes the result locally to original13's current new role. All review
outputs are confined to r14-03-gate-backlog-review and committed with [skip ci].
''')
    (OUT/'HANDOFF.md').write_text('''READY — SAME14 gate-only APPROVE; R14-03/P2 CLOSED.

Package4eccefc670602b58f25f9c55a27da2d844cdcf18.
Exact approved patch SHA256
1dfaf5a1fa2d748e81bea4093018eb65972d7cfc807e47c0d1f7ad39565f8cba.
Proposed local control0e97a487d8b7f8e8cbced5dbe2b6909c7150c695,
treeb980862474e3630c459ee147def4fa45f3ea42fd,
sole parent0e8c836857344866564e1423ad5d8d28bbc4106b.

23/23 independent final-object targeted tests PASS. Exact frozen fail-open becomes
unresolved-path rejection. Baseline map unchanged77 calls/8 functions/11 contexts.
Additional bounded extractor/guard tests PASS; precursor failure preserved without
acceptance credit. R14-01/R14-02 closure inherited; no new blocker in this delta.

Original13 current NEW13 role: only the exact approved patch may be integrated
into the separately prepared next candidate. Bind actual payload/request and
ancestry; required candidate review and fresh GO remain. Task16a timeout/audit
work is separate and is not approved by this gate-only review.

NOT_AN_EXECUTABLE_CI_PACKAGE. No automatic integration or CI authority. Frozen
sourcebd62/control0e8, package474e, reviewe783 and GO6db unchanged; no exception
or historical CI credit transfers. No compiler/CI/push/ledger/budget/integration
operation. Fast OFF/settings unchanged; no subagents; proof credit NONE.
This HANDOFF is a local artifact; no message was sent to another party.
Review commit: containing commit, full SHA supplied in READY.
''')
    files = sorted(p for p in OUT.iterdir() if p.is_file() and p.name != 'MANIFEST.sha256')
    (OUT/'MANIFEST.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.name+'\n' for p in files))
    print('SEALED APPROVE; R14-03 CLOSED; exact gate patch ONLY; '+str(len(files))+' hashes')


if __name__ == '__main__':
    main()
