"""Seal review artifacts after successful independent checks; no candidate edits."""
import hashlib,json
from pathlib import Path
OUT=Path(__file__).resolve().parent.parent
pins=json.loads((OUT/'inputs/package/PINS.json').read_text())
audit=json.loads((OUT/'INPUT-AUDIT.json').read_text())
main=json.loads((OUT/'tests/review-execution.json').read_text())
recovery=json.loads((OUT/'tests/recovery-execution.json').read_text())
assert main['state']=='PASS' and recovery['state']=='PASS'
assert 'Ran 26 tests' in (OUT/'tests/review.stderr.txt').read_text()
assert 'Ran 1 test' in (OUT/'tests/recovery.stderr.txt').read_text()
for rec in (main,recovery):
    assert rec['exit_code']==0
    for name,h in rec['artifacts'].items():assert hashlib.sha256((OUT/'tests'/name).read_bytes()).hexdigest()==h
PACKAGE='0902ad2d84e5e5c4d9bb3b01d5c7f7671e84b38d'
def save(name,value):
    path=OUT/name;assert not path.exists(),name
    path.write_text(value if isinstance(value,str) else json.dumps(value,indent=2)+'\n')
findings={'schema':'ch8-s3-1-independent14-delta-findings-v1','disposition':'APPROVE','candidate_g0':PACKAGE,'control':pins['control'],'source':pins['source'],'tool':pins['tool'],'request_sha256':pins['request_sha256'],'workflow_sha256':pins['workflow_sha256'],'frozen_review':'610dcd6858415792050a9aba7e0d7859afd7d727','findings':[
{'id':'R14-02','priority':'P1','status':'CLOSED','blocking':False,'closure':'Shared protected reader runs independent of worker state before local sealing and on portable replay. Affirmative error/drift cannot be erased by matching controller AFTER; unknown/malformed required evidence rejects. Verified interrupted absence remains recoverable. Original errors/exits and completed prefix survive stopped replays.','locations':['ch8-s1-control/s3_evidence.py:21','ch8-s1-control/s3_campaign.py:188','ch8-s1-control/s3_campaign.py:362'],'evidence':['tests/review-execution.json','tests/test_delta14.py','tests/recovery-execution.json','tests/test_recovery14.py']},
{'id':'R14-01','priority':'P2','status':'CLOSED','blocking':False,'closure':'Actual S3 CompileMonitor and source_under_test_record use explicit request-derived std/tool SHA/tree. Current base_std_sha equals source513; historical patch ancestry is separate. Same strict provenance reader runs at local finalization and portable replay; all four identity fields reject missing/null/type/stale mismatches. Legacy defaults/fixtures/policy remain invariant.','locations':['ch8-s1-control/runner.py:507','ch8-s1-control/runner.py:1041','ch8-s1-control/runner.py:1090','ch8-s1-control/s3_evidence.py:58'],'evidence':['tests/review-execution.json','tests/test_delta14.py','INPUT-AUDIT.json']}],
'blocking_findings':[],'new_findings':[],'native_compile_proof_fit_CI':'NOT_RUN','proof_credit':'NONE','B1_B2_credit':'NONE','GO':'ROOT_GO_REQUEST_ONLY; root decision and coordinator launch still separate','budget_action':'NONE; latest owner reference31/31+11/17=42/48 supersedes frozen41'}
save('FINDINGS.json',findings)
validation={'schema':'ch8-s3-1-independent14-delta-validation-v1','disposition':'APPROVE','independent_tests':{'main':main,'main_tests':26,'interrupted_recovery':recovery,'recovery_tests':1,'total':27},'input_audit':'INPUT-AUDIT.json','author_final_validate':audit['checks']['author_final_validate'],'full_validate_rerun':False,'author_frozen_reproduction':'Three PASS checks reproduce old bugs on1dfc only; inherited frozen record, not independent repair acceptance.','interrupted_precursor':'PRECURSORS.json; excluded from final counts','review_harness_precursor':'tests/AUDIT-PRECURSOR.json; incorrect metadata key corrected before successful audit; no candidate edit','native_compile_Kani_CBMC_full_native_runner_fit_CI':'NOT_RUN','proof_credit':'NONE'}
save('VALIDATION.json',validation)
save('REPORT.md',f'''# Independent14 delta: APPROVE — R14-02 and R14-01 CLOSED

Owner00:33 explicit `/new14` overrides prepared current context. Task
`cd90cf0bde2d7658a2dfe690dd2887bdd72aefb6`; review of exact repaired package
`{PACKAGE}`. Both original findings are independently **CLOSED**; no blocking
or new finding remains in this bounded delta. Root GO-request only; no launch.

| Input | Exact identity |
|---|---|
| Control | `{pins['control']['sha']}` |
| Control tree / sole parent | `{pins['control']['tree']}` / `{pins['control']['parent']}` |
| Frozen source | `{pins['source']['sha']}` |
| Source tree / parent | `{pins['source']['tree']}` / `{pins['source']['parent']}` |
| Stock tool | `{pins['tool']['sha']}`, tree `{pins['tool']['tree']}` |
| Request SHA256 | `{pins['request_sha256']}` |
| Workflow SHA256 | `{pins['workflow_sha256']}` |

## R14-02 / P1 — CLOSED

`s3_evidence.protected` checks the recorded worker evidence before state-specific
result handling. Local `root_outcome` and portable `collect` both call it. Source
capture errors, snapshot errors, identity drift, unreadable/malformed binaries,
explicit UNKNOWN and malformed required evidence reject. COMPLETE, FAILED,
IN_PROGRESS and INTERRUPTED cannot bypass recorded observations. Matching durable
controller E0/pre/post does not erase a worker error.

Independent campaign tests vary four states, three status labels and two errors
(24 combinations). Each stops at the third invocation with exactly two sealed
prefix roots, matching controller AFTER and six later roots NOT_RUN. Fallback
retains prefix hashes, original worker bytes, exception and exit -9. The author
regressions additionally cover missing/null/unknown states and protected fields.
Sixteen resealed portable state/error mutations reject through the shared reader.
Four actual-writer-shaped stopped campaigns (FAILED/COMPLETE × source/binary
errors) preserve original exception, error records, exit -15 and signal15 in
identical local/upload-only results, with explicit GLOBAL_STOPPED_PENDING_REVIEW.

Absence remains distinct. The existing interrupted-worker continuation regression
passes. A separate independent synthetic interruption check begins with actual
writer-shaped evidence, removes genuinely absent inner source/binary AFTER,
retains verified shutdown and matching durable controller AFTER, and updates the
bound interruption records/seal. Both local and upload-only readers agree: UNKNOWN,
original exit -15, no global stop, later roots retained. This tests reader recovery,
not an actual native process termination. Present error or malformed AFTER cannot
use this absence route. No baseline reset or blanket ESRCH exemption was added;
owned-process lifecycle code and late-publication behavior are unchanged.

## R14-01 / P2 — CLOSED

The actual S3 `_run_group` supplies request-derived std_sha/std_tree/tool_sha/
tool_tree to CompileMonitor and its group record. `source_under_test_record`
writes those same identities, current pre-overlay base_std_sha=513341 and separate
historical_patch_base_std_sha=99e845. Binding metadata copies the actual record.
The shared provenance reader compares against the request at local finalization
and replay, including interrupted sealed groups; it does not merely compare two
potentially stale copies. Actual writer execution is synthetic with native calls
substituted, rather than a fabricated corrected compilation receipt.

Independent execution of the author regressions confirms actual writers, metadata,
legacy defaults and local-finalizer rejection of corrupted writers. The additional
portable matrix mutates all four fields at compile, source_under_test and group
locations across missing/null/array/integer/stale values: 60 rejections. Metadata
artifact hashes, binding references and seals are recomputed, so rejection is the
provenance guard rather than incidental storage corruption. Existing source/target,
request/selector, rich/native-metadata, error-path and late-publication checks pass.
Legacy defaults remain bd62/0aac without added tree fields. The delta leaves all
legacy fixtures, policy and historical evidence unchanged.

## Exact inputs, preserved scope and timing

INPUT-AUDIT.json independently verifies all34 committed package files/all33
manifest hashes, source/control/tool HEAD/tree/sole parent/clean status, request
and workflow bytes, request payload/source hashes, three patch replays to exact
control tree, and audited checkout ancestry7/5/2. Original55-file e8a8 package and
19-file review610d remain exact. The six frozen source/domain/role/U maps match
byte-for-byte. Only the declared seven CONTROL paths differ from1dfc.

Source-semantic/domain/cfg/PFC/U-policy review is inherited from frozen610d by
exact source/tool/map bytes; no broad source audit or new proof claim is made.
Nine roots, full-byte domains, positive actual bodies,71 literal source sites,
44 covers, unwind bounds, disabled U proposal/reject-ALL-U and all caps remain
unchanged. Workflow bytes are identical, including Validate18min, setup1800,
job180min and checkout depths7/5/2. Existing scope gaps in610d remain OPEN.

The author's exact final Validate receipt, script and transcripts agree:
136 legacy +46 S3/repair =182 PASS; execution_count1; elapsed490.471224626s;
1080/elapsed=2.2019640414655, above1.5. Monotonic arithmetic and transcript hashes
match final fc29/request/workflow pins. This is audited author local static/
synthetic evidence, not an independently witnessed CI run. Full Validate was not
rerun; no concrete concern required it. Precursors are not relabelled as final.

Independent final review:26 targeted tests PASS/{main['elapsed_seconds']:.6f}s,
plus1 recovery test PASS/{recovery['elapsed_seconds']:.6f}s, total27 PASS. The
expanded reviewer matrix is outside the workflow Validate timing measurement.
Exact commands, timestamps, stdout/stderr and hashes are in tests/ and VALIDATION.
The old targeted.stdout/stderr are preserved as INTERRUPTED PRECURSOR with hashes;
they contribute zero final tests. A reviewer audit-helper wrong-key exception is
recorded separately; correcting the helper caused no candidate change.

## Disposition and handoff

**APPROVE; R14-02 CLOSED; R14-01 CLOSED.** This satisfies the independent delta
review gate for these exact identities. Next is root GO decision only. User
coordinator alone may separately launch/account prospective item2 attempt12/17
after root consent; this review performs no dispatch or accounting action.
Latest owner budget reference31/31+11/17=42/48 supersedes frozen author's41;
that historical metadata difference is informational and not a blocker.

Native compile, compiler expansion, Kani/CBMC, full native runner, proof/fit and
CI remain NOT_RUN. Qualified leaves0, proof obligations closed0, independent
B1/B2 credit NONE. No candidate/source edit, compiler/cargo/rustfmt, CI, push,
PR/issues, raw evidence, ledger/reservation/budget action, subagent or model/settings
change occurred. High/Fast OFF instructions were preserved.
''')
save('HANDOFF.md',f'''# APPROVE — SAME14 delta complete

Exact package `{PACKAGE}`; control `{pins['control']['sha']}`,
tree `{pins['control']['tree']}`, sole parent `{pins['control']['parent']}`.
Frozen source `{pins['source']['sha']}` and tool `{pins['tool']['sha']}` unchanged.
Request `{pins['request_sha256']}`; workflow `{pins['workflow_sha256']}`.

R14-02 **CLOSED**, R14-01 **CLOSED**, blocking findings0. REPORT.md/FINDINGS.json
and INPUT-AUDIT.json contain disposition, exact pins and scope. Independent27
synthetic targeted checks PASS. Author final182PASS/490.471224626s/margin2.201964x
is receipt-audited; no extra full Validate. Old partial transcripts remain
INTERRUPTED PRECURSOR, excluded from final evidence.

**Root GO-request only.** Root decision still separate; only user coordinator
launches/accounts prospective12/17 after consent. Latest reference42/48
(31/31+11/17), superseding frozen41, metadata-only; no accounting action here.
Native compile/proof/fit/full native runner/CI NOT_RUN; independent proof credit0.
Original package/review/control and candidate/source/tool unchanged; no push/PR/
issues/ledger/subagents/model/settings changes. Output is immutable at its review
commit, restricted to this directory with [skip ci].
''')
save('CURRENT-TASK.md','''# Independent14 — COMPLETE

Owner00:33 /new14; task cd90cf0bde2d7658a2dfe690dd2887bdd72aefb6.
Runtime Codex; current high/FastOFF preserved, no subagents/model changes.
APPROVE; R14-02 CLOSED; R14-01 CLOSED. Exact pins in INPUT-AUDIT/FINDINGS.
Root GO-request only; no launch/accounting. Latest owner reference42/48.
Native/proof/fit/CI NOT_RUN, proofcredit0. See REPORT.md and HANDOFF.md.
''')
save('CHECKPOINT.json',{'status':'COMPLETE_APPROVE','task':'cd90cf0bde2d7658a2dfe690dd2887bdd72aefb6','candidate':PACKAGE,'findings':{'R14-02':'CLOSED','R14-01':'CLOSED'},'evidence':['INPUT-AUDIT.json','FINDINGS.json','VALIDATION.json','PRECURSORS.json'],'open':['root GO decision','coordinator-only prospective12/17 launch/accounting after consent','native compile/proof/fit NOT_RUN; inherited broader scope gaps remain OPEN'],'next':'root GO-request only','proof_credit':0,'budget_action':'NONE; latest reference42/48','closure_reason':'Authorized bounded independent delta review complete; both findings closed; no other work authorized.'})
files=sorted(p for p in OUT.rglob('*') if p.is_file() and p!=OUT/'MANIFEST.sha256')
save('MANIFEST.sha256',''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(OUT))+'\n' for p in files))
print(json.dumps({'disposition':'APPROVE','findings':'R14-02 CLOSED; R14-01 CLOSED','independent_tests':27,'manifest_files':len(files),'root_GO':'REQUEST_ONLY'}))
