#!/usr/bin/env python3
"""Produce final review routing docs from actual final-object receipts only."""
import datetime,hashlib,json,platform,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def load(n):return json.loads((H/n).read_text())
def dump(n,v):(H/n).write_text(json.dumps(v,indent=2)+'\n')
P=load('PINS.json');v=load('RELEASE-FINAL-VALIDATE-TIMING.json');s=load('RELEASE-CHECK-SOURCE-TIMING.json');proof=load('RELEASE-TEST-PROVENANCE.json')
assert v['status']==s['status']=='PASS' and proof['execution_count']==proof['check_source_execution_count']==1
assert v['provenance']['control']['sha']==P['control']['sha'] and v['elapsed_seconds']<600 and s['elapsed_seconds']<60
C=Path(P['control']['worktree']);sys.dont_write_bytecode=True;sys.path.insert(0,str(C/'ch8-s1-control'))
import check_package,r5_profile
wf=check_package.load_yaml((C/'.github/workflows/ch8-s2.yml').read_text());job=wf['jobs']['s2_batch']
audit=[]
for index,step in enumerate(job['steps'],1):
    known=v if step['name']=='Validate control and synthetic wrapper' else s if step['name']=='Check all source identities' else None
    audit.append({'index':index,'name':step['name'],'command':step.get('run'),'action':step.get('uses'),
      'cap_seconds':step['timeout-minutes']*60,'measured_this_machine_seconds':known['elapsed_seconds'] if known else 'UNKNOWN',
      'scope':'LOCAL_STATIC_SYNTHETIC_ONLY' if known else 'NOT_RUN_CURRENT_R5',
      'decision':'KEEP_FROZEN_TIMEOUT; r5 setup/step/job caps not increased'})
dump('TIMEOUT-AUDIT.json',{'candidate':P['control'],'steps':audit,'setup_seconds':1800,
    'setup_origin':'Begin setup budget epoch; stock tool setup/build share1800. Proof root compilations are separately inside campaign child slots.',
    'campaign':r5_profile.CAPS,'formula':'9*720+180+240=6900; worker710 plus parent durable-publication10 inside each720',
    'child_compile_arithmetic':'9*600=5400 child wall; 9*180=1620 compile subcaps INSIDE child walls, not extra',
    'job_arithmetic':'1800+7560+900=10260<=10800; sum step maxima186min is not elapsed or a grant',
    'counter_policy':'One monotonic campaign; cleanup alarm6660 and hard6900. No per-root reset, retry, resumed solver or slack extra roots.',
    'actual_GitHub_r5_duration':'UNKNOWN_NOT_RUN','future_timeout_absence':'NOT_CLAIMED','proof_credit':'NONE'})
(H/'TIMEOUT-AUDIT.md').write_text(f'''# r5 timeout/cost scope

Actual final Validate: {proof['test_count']} tests PASS, {v['elapsed_seconds']:.9f}s monotonic; actual final check-source PASS, {s['elapsed_seconds']:.9f}s. Each final command ran ONCE on control{P['control']['sha']}. Host measurements only; future GitHub duration UNKNOWN. Validate remains600s, check-source60s.

All remaining setup step durations are UNKNOWN for r5; caps unchanged. Shared setup1800s starts at the setup epoch and includes installation/stock tool build (<=min900/remaining). It does not mean reused root compilation. Nine fresh root compilations have compile subcaps9x180=1620s INSIDE9x600=5400 child walls. Each full slot720 includes bounded pre/post/kill/reap/metadata and publication: worker710 plus10 publication reserve.9x720+180controller+240cleanup=6900, inside outer7500/internal8100/workflow-step7560. Job180min remains;1800+7560+900reserve=10260<=10800. All step maxima sum186min is not elapsed and cannot enlarge the job/aggregate clocks.

One monotonic campaign clock; no new clock per group and no automatic extra root/retry using slack. The cleanup alarm at6660 reserves240s; hard6900 and step7560/job10800 remain independent ceilings. Earlier admission failure/global deadline yields explicit partial/unstarted statuses, not a smaller secretly granted solver timeout. A preflight that cannot leave a full600 child allowance does not start that child.

Inner stock harness timeout600 is a CBMC bound. External child600 includes compile, instrumentation and verification; external cutoff is not relabelled backend TIMEOUT600. Late cleanup cannot clear a latched cutoff; parent publication cutoff forces UNKNOWN. Partial captures retain original exit/signal/error and completeness markers.

RSS effective min(6GiB,available-2GiB,outer12GiB) is polled non-atomic PGID VmRSS, possible overshoot, not strict root/tree/kernel/cgroup memory. Outer guard samples observed-owned PID VmRSS separately. Subreaper/pidfd ownership/reaping and unexpected-PG rejection are lifecycle checks, not stronger memory measurements. Source-reported comm-class maxima are not simultaneous and are not added.

Old authoritative intake5ca has compile polling upper bound35.5s vs native Cargo30.49s, RSS interruption12.002GiB sampled PGID and all11 final outcomes UNKNOWN. These are past exact-run facts, not a forecast or causal model-cost estimate. Root quota recommendation+1 minimum/+3 working (cap17) is NOT GRANTED; actual item2 remains10/14, total39/43. No CI/ledger/reservation/budget action here.
''')
state='READY_FOR_INDEPENDENT14_R5_REVIEW'
checkpoint={'task_id':P['task_id'],'state':state,'source':P['source'],'control':P['control'],'tool':P['tool'],
    'plan':P['plan_commit'],'intake':P['intake_commit'],'W11_dependency':'RESOLVED_EXACT_5ca',
    'selected':{'roots':9,'positive_expectations':4,'exact_negative_expectations':5,'required_covers':16},
    'deferred':list(r5_profile.DEFERRED),'full_obligations':{'roots':11,'covers':20,'negatives':6},
    'final_validate':{'tests':proof['test_count'],'seconds':v['elapsed_seconds'],'exit':0,'executions':1},
    'final_check_source':{'seconds':s['elapsed_seconds'],'exit':0,'executions':1},
    'review14':'PENDING_NEW_R5_COMBINED_CANDIDATE','GO':'PENDING_SEPARATE_COORDINATOR_DECISION','dispatch_authority':'NONE',
    'native_r5_compiler_roots_solver':'NOT_RUN','proof_credit':'NONE','independent_B1_B2':'NONE','closed_proof_obligations':0,
    'budget_actual':{'item2_used':10,'item2_cap':14,'total_used':39,'total_cap':43,'future_r5_attempts_max':1,'reservation':False},
    'recommendation_NOT_GRANTED':{'minimum_extra':1,'working_extra':3,'suggested_cap':17},
    'external_actions':{k:0 for k in ('CI','push','PR','issue','ledger','budget','reservation','source_edit','tool_edit','compiler','verifier','subagent')},
    'Fast':'OFF_NOT_TOGGLED','settings':'PRESERVED','remaining_limits':['Native CI/runtime timing and stock children not run here','Sampled PGID/PID RSS is not strict root/tree memory','Profilesv4/PFC compiler-instance/assertion-origin gaps remain UNKNOWN; no new qualification','general32 pair deferred to S3 proved leaves/summary work; no reduced-domain variant','Current four remaining attempts do not guarantee S3/S4/full16/32/final matrix'],
    'next':'Independent14 review exact package/control/profile/request/workflow/delta; then separate root/coordinator GO only',
    'closure_reason':'All authorized control implementation and offline/static/synthetic package preparation complete; no compiler/CI/dispatch authority. Review and GO are required separate steps.',
    'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
dump('CHECKPOINT.json',checkpoint)
(H/'CURRENT-TASK.md').write_text('Runtime: Codex. W13 '+P['task_id']+'. '+state+'. Exact pins PINS.json. Source/tool unchanged; r5 native/CI NOT_RUN; review14 and separate GO PENDING.\n')
(H/'STATUS.md').write_text(state+'\n9 selected /16 covers /5 negatives; general32 pair deferred; canonical11/20/6 retained. Offline Validate PASS; native r5 NOT_RUN.\n')
request=f'''# r5 exact candidate — independent14 review request

READY_FOR_INDEPENDENT14_R5_REVIEW. This is a local routing artifact, not a message, review approval, reservation or GO. New r5 combined candidate review PENDING; prior combined7c0a05 review and inherited R14 closures apply only to unchanged gate bytes, not this new scheduler/policy delta.

Package identity: containing ownpaths-only [skip ci] commit; full SHA in READY (self-reference excluded). Plan `{P['plan_commit']}` and authoritative intake `{P['intake_commit']}` are bound in INPUTS/PROVENANCE and preserved immutable. Intake resolves the earlier plan's pending W11 input. Owner19:12 refinements override the provisional plan order; no separate plan rewrite.

Source `{P['source']['sha']}`, tree `{P['source']['tree']}`, parent `{P['source']['parent']}` unchanged and clean. Stock tool `{P['tool']['sha']}`, tree `{P['tool']['tree']}` unchanged. Control `{P['control']['sha']}`, tree `{P['control']['tree']}`, sole parent `{P['control']['parent']}`; sibling of d33, not its child. Checkout control/source/tool7/5/2. Request SHA256 `{P['control']['request_sha256']}`; workflow SHA256 `{P['control']['workflow_sha256']}`. Full-stock-relative63 changed paths/46 payload hashes (request self-hash external) are exact; patches/replays/shallow metadata are in PATCHES/VALIDATION.

One job/shared checkout/setup/stock tool build, nine serial singleton stock verify-std calls. Actual order: checker_order_corrupt → checker_count_corrupt → swap_pfc → sort13_weak → merge32_real → sort13_assumed → merge_count_corrupt → merge_order_corrupt → summary_witness. Every call has one exact qualified selector/jobs1; native start header must match that singleton. No JSON-sort dependence, stock driver fork, goto reuse or bare CBMC. Nine independent compilations budgeted; fresh target/namespace/export/source/tool/cfg/stub/PFC/request/binary/origin records for each invocation.

Selected9=4 expected positives/5 exact negatives/16 required covers. Canonical full11/20/6 retained. Both general32 roots are DEFERRED_NOT_SELECTED/UNKNOWN to S3 proved leaves/summary encoding; no reduced-domain variant. Source/PFC/model/copy maps are canonical inherited references on the same bytes; SCHEDULE/QUALIFICATION/PROPERTY-COVER maps explicitly distinguish selected and deferred. Registration-only sort8 remains unproved/unselected. Assumed sort13/general32 and copy-seam negatives do not acquire actual-callee/general proof credit.

Local RSS/child timeout/compile error/no RESULTS/decoder or unexpected verdict produce local honest receipts and continue only after ownership cleanup and intact identities. Supervisor records PID/PGID/start-time, limits, original exits/signals/errors, monotonic times, cutoff latch, kill/reap and sampled scopes. Linux subreaper/pidfds handle adopted descendants. Any observed PG outside worker/declared driver sessions, including exited/zombie detached groups, rejects admission; after a PG-only worker snapshot such an escape cannot be silently accepted. Unreaped/unknown containment, source/tool/request/binary/storage drift or hard global bounds abort with explicit remaining statuses. Unsealed started workers are INTERRUPTED/UNKNOWN; intent-only state stays UNSEALED_INVOCATION_UNKNOWN. Raw supervision is saved before admission, not lost on global errors. No missing cost is converted to0.

Completed rows and their group evidence are fsynced/hash-sealed before next launch. Later failure/fallback does not overwrite those bytes. Legacy explicit-group fallback remains strict before r5 starts (unchanged B-01 tests); once r5-state exists that API cannot overwrite prefix. Always finish invokes the unchanged protected compact packer in finally even if fallback errors. Artifact/output/export caps are aggregate across the campaign. Physical storage/compact-cap failures retain explicit incomplete/omission markers, not false complete proof.

Child600 includes compile180 and instrumentation/backend; stock inner600 remains distinct. Full slot720 =worker710 +10 publication reserve;9×720+180controller+240cleanup=6900, within7500/8100/step7560; setup1800/job180min unchanged. Local effective6GiB and outer12GiB+2headroom remain sampled PGID/observed-PID VmRSS with possible overshoot, not strict root/tree/kernel memory. One monotonic clock, cleanup alarm6660/hard6900, no extra roots/retries/slack attempt. See TIMEOUT-AUDIT and CAP-MAP.

Actual final Validate command from the final committed workflow: PASS, {proof['test_count']} tests, {v['elapsed_seconds']:.9f}s monotonic, ONE final-object execution. Actual check-source PASS, {s['elapsed_seconds']:.9f}s, ONE final-object execution. These are this-machine Python/static/synthetic measurements. Native Rust/stock roots/solver/CI NOT_RUN; future GitHub durations UNKNOWN. Final validation explicitly includes test_r5.py plus all prior actual modules. Earlier c154/ac9 passes/failures and development process/fixture errors remain PRECURSOR-* / DEVELOPMENT-NOTES, with no final acceptance credit; final provenance references only `{P['control']['sha']}`.

New deltas: r5_profile.py/r5_campaign.py/r5_runtime.py/test_r5.py; bounded isolated path and protected PID capture in runner; strict legacy adapters in s2_policy/check_package/collect; workflow profile/one controller/finish; explicit legacy-only fixtures in test_runner/test_s107/test_s2 (assertions unchanged). Protected source gates/lexical/ordinary/copy checks, original diagnostic decoder/packer, binding metadata and B-01/B-02 tests remain byte-identical to d33; legacy validation/collector/fallback/build bodies retained verbatim except function rename. Review ownership cleanup, late-cutoff admission, aggregate caps, durable partial/fallback, request/profile/YAML cross-bindings and absence of unsupported proof credit.

Budget ACTUAL item2=10/14,total39/43, four remaining; at most ONE future r5 workflow attempt after this independent review14 plus separate coordinator GO. Root recommendation minimum+1/working+3 (cap17) NOT GRANTED/APPLIED. No ledger/reservation/refund/cap edits or CI/push/PR/issue/source publication. No guarantee four attempts suffice for S3/S4/all16/32/matched final. User/coordinator alone chooses later work.

Profilesv4/PFC bounded source-reported trust and unknown compiler-instance/type/MIR/property/cover-origin gaps remain. Source coordinates/fresh UUIDs/compilation success are not independent proof. Closed proof obligations0, independent B1/B2 NONE, proof credit NONE. Current model/tier/settings preserved; Fast OFF not toggled; no subagents. Final commits use Tiramisu-Cake <igkharin@gmail.com>.
'''
(H/'REVIEW14-REQUEST.md').write_text(request);(H/'HANDOFF.md').write_text(request)
dump('HOST-PROVENANCE.json',{'platform':platform.platform(),'python':sys.version,'python_executable':sys.executable,'scope':'Current machine only; no native r5 or future CI timing claim'})
print(state,proof['test_count'],v['elapsed_seconds'],s['elapsed_seconds'])
