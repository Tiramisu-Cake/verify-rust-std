#!/usr/bin/env python3
"""Render the immutable intake views and hash manifest from bounded projections."""
import hashlib,json
from datetime import datetime
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_bytes())
def write(n,s):(HERE/n).write_text(s.rstrip()+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    result=read('RESULT.json');q=read('QUALIFICATION.json');cost=read('COST.json');validation=read('VALIDATION.json');provenance=read('PROVENANCE.json');integ=read('artifact-integrity.json')
    rows={r['id']:r for r in q['rows']};job=cost['job'];fmt=lambda x:f'{x:.3f}' if isinstance(x,(int,float)) else 'UNKNOWN'
    table=['| Row | Native | Properties | U | SUCCESS guards | Compile upper bound s | Native verification s | Whole child s | RSS KiB |','| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in cost['rows']:
        z=rows[r['id']];guard=len(z['unsupported_guards']) if isinstance(z['unsupported_guards'],list) else 'UNKNOWN'
        table.append(f"| {r['id']} | {z['native_verdict']} | {z['native_property_count']} | {z['U_count']} | {guard} | {fmt(r['compile_elapsed_upper_bound_seconds'])} | {fmt(r['native_verification_time_s'])} | {fmt(r['execution']['elapsed_seconds'])} | {r['execution']['rss_peak_kib']} |")
    report='''# READY — run44460583125/attempt1 terminal intake

Classification: **SELECTED_PARTIAL; native2 SUCCESS +3 exact negative FAILURE +2 child wall timeouts; strict0; no admission/proof credit.** Connected GitHub reports completed/failure. Seven actual singleton native starts occur in the planned order; all seven durable completion seals replay identically from fresh materialized and upload-only inputs. Completion includes preservation of unsuccessful/partial observations, not qualification.

'''+ '\n'.join(table)+f'''

Campaign elapsed is {cost['campaign_elapsed_seconds']:.9f}s. The reported52s insert and223s sort9 correspond to native `resources.verification_time_s` ({cost['rows'][3]['native_verification_time_s']:.9f}s and {cost['rows'][4]['native_verification_time_s']:.9f}s), not whole-child cost. Setup total is {cost['setup']['setup_total_seconds']:.9f}s, of which the exported tool build execution is {cost['setup']['elapsed_seconds']:.3f}s. GitHub job spans `{job['started_at']}` to `{job['completed_at']}`. Step summaries confirm Validate, identities, setup, build, fallback and upload success; the actual-leaves step failed. Individual CI test statuses are not exported in this compact payload.

The three negative rows each retain exactly one FAILURE with the intended literal label: S2_NEG_CHECKER_ORDER, S2_NEG_CHECKER_COUNT and S2_NEG_SORT13_WEAK. They are fixed fixtures. sort13_weak uses descending[12..0] and the ordinary s2_swap_seam→weak_swap stub; it is not an arbitrary13-byte positive proof. All targets are null for Original rows; only insert registers ProofForContract(insert_tail), its concrete u8/KeyLess provider, SUCCESS DFCC call links and located checked ensures.

Insert and sort9 each have four exact located SUCCESS source roles (active span, sorted/full-value count, every outside value frame, arbitrary outside canary) and all five required SAT covers. The whole source plan has19 assertion sites and46 covers; those are not predicted native property counts. The five completed inventories contain602 properties. The fallback22 covers, including each17 length cover, and network14 covers, including each9 length cover, remain UNKNOWN along with their assertions: neither partial export contains a completed native inventory. No empty partial array is treated as zero U, zero guards or success.

Every observed native property and status is retained in NATIVE-PROPERTIES.json. All28 U have invocation-specific source-local arithmetic/definedness arguments and exact source contexts in QUALIFICATION.json; these arguments carry SOURCE_REPORTED location assurance, not independent property/MIR origin or an admission. All7 unsupported guards are retained with exact IDs, descriptions, locations and SUCCESS status (4 insert,3 sort9). They cover pointer-allocation reasoning, caller_location and panic runtime. SUCCESS guards do not remove the strict unsupported-construct rejection. Strict REJECT_ALL U/proposalDISABLED also rejects all five completed rows. All seven original canonical `s3_expected_match` and sealed expected_match values remain false.

The two positive observations are provisional S1/Profilesv4 bounded candidates for review of their U/guards/domain/bindings, separately from the immutable strict verdict and any later root/coordinator admission. They do not create an initialization leaf, provider summary, B1/B2/MIR/generic proof or closed obligation. The three exact negative label observations are separately recorded.

The five completed inventories have no missing/null/wrong-type/zero location; frozen rich readers ACCEPT each. All71 class=unreachable/status=SUCCESS records are positively located and retained separately from28 status=UNREACHABLE U. No new metadata exception is proposed or applied. Location completeness of the two incomplete inventories is UNKNOWN. Old f740/ff193 admissions remain limited to their original run/property IDs. Shared emitter/source/MIR origin is UNKNOWN; no wildcard/location/parser/policy/history change follows from this intake.

The exact source/tool/request/export/argv/cfg/start/namespace and native core registrations are checked per row. PROTECTED.json retains E0, pre, worker BEFORE/AFTER and controller-post binary snapshots for kani_driver, kani_compiler and cbmc; all required hashes are present and match. Worker source_before/source_after and current source_under_test records match the request, including failures. These observations do not supply the producer's missing compiler instance/compilation ID, AST/MIR/property edges, effective contract clauses or physical inode identity. Those fields stay UNKNOWN in the binding metadata projections.

Both capped rows reached STOCK_INITIAL_EXPORT_OBSERVED and a native root start, with compile markers37.293s and36.091s under180s. Each hit the outer child600 wall timer, including compilation; termination_reason=timeout, timed_out=true, originalexit=-15 and signal15. Their observed PGID RSS peaks3007384/3883252KiB remain below effective6291456KiB; outer census peaks3031420/3907572KiB remain below12582912KiB. This is not an RSS/compile/slot/global cutoff. Native results and verification duration are censored; exact symex/backend subphase and exclusive backend timing remain UNKNOWN. Per-row effective caps use min(6GiB,12GiB,available−2GiB), with exported admission availability and reserve. Slot720, actual worker wall710, campaign6900, setup1800 and job180min caps remain unchanged.

All seven child shutdowns and exclusive-subreeper PID/starttime containment/reaping are verified; worker exits0, no supervisor cutoff/global STOP or surviving owned processes. Fallback timeout is followed by the network launch after cleanup; the final network timeout is followed by terminal packaging/upload. Both timed rows retain the original RunnerError and incomplete export/rich states. Lifecycle diagnostics retain64 events per row and explicitly report omitted counts; verified final containment is a separate observation, not a claim of complete diagnostic history. RSS is nominal50ms non-atomic owned-PGID sampling, not a kernel/cgroup/tree peak. Component maxima are not simultaneous. No speedup is claimed against earlier variable-base insertion geometry.

Scope remains exact: insertion has arbitrary34 u8 backing, base1/tail1/span2 (1/16 I-D1 geometry,1/256 old grid), not universal insert. sort9 uses arbitrary34 u8 backing/base1/len9 and the actual25-swap body. Fallback has Cell<u8>/KeyLess<Cell<u8>>, arbitrary logical bytes and symbolicN0..16; network has u8/KeyLess and symbolicN0..8, not full32. Normal-return value/frame checks do not establish generic trait dispatch, mutating callbacks, ownership, panic/unwind or actual initialization-mask theorems. All10 deferred categories, including merge/provider,34 sort8 caller contexts, positive13 and fullN16/N32, remain open in ROOTS.json.

Prior independent B01/B02 closures are pinned and projected in B01-B02.json. The actual source/control/request/tool identities match that reviewed same-tree repair. This intake runs bounded readers and source-only checks; it does not rerun fullValidate, compiler, verifier or CI. The historical review conclusion is not a new review of this intake.

'''+f"Validation: {validation['checks_count']} bounded checks PASS; {len(validation['adverse_tests'])} adverse controls reject missing/tampered sealed members, changed protected binary and missing/null/bool/string/wrong selected_roots on both local/upload routes, including STOPPED and zero-completion terminal scenarios. No type normalization. See VALIDATION.json.\n"
    report=report.replace('exclusive-subreeper','exclusive-subreaper')
    write('RESULT.md',report)
    write('PREFIX.md',f'''# Portable completed prefix

Run `python3 replay.py` from this directory with the recorded Git objects/worktrees available. It freezes the exact reviewed control's Python/fixture closure in a fresh temporary directory, validates all105 compact member hashes, source and control payload pins, all-state protected snapshots, native registration and export bindings, then compares `s34_campaign.collect(materialized)` with public `collect(upload-only)` using the sole original compact member. Neither route invokes native tools or runner main. Original evidence is byte-exact after adverse tests; temporary materialization is removed on exit.

Actual terminal: SELECTED_PARTIAL, selected_roots genuine integer7, no global_stop, no missing selected groups; prefix is all seven rows in ordered INPUTS. Failed/timed rows are completed observation records. Strict qualification remains false. The replay leaves no fabricated missing exports or rewritten history.

B01 type/cardinality controls cover local and upload-only routes, full selected partial and STOPPED scenarios with7 or0 completed references. Missing/null/bool/string/0/6/8 rejects at the exact cardinality gate. These are synthetic adverse copies, never changes to authentic evidence. Prior independently reviewed full7/stopped2/partial2/stopped0/partial0 accept/reject coverage and B02 standalone repair remain pinned in B01-B02.json; no full host suite is rerun.

Run `python3 render.py` only after a deliberate new correction before sealing. It writes the report views and MANIFEST.json. Post-commit corrections must be a NEW immutable correction packet; do not rewrite the sealed intake. Root checks the committed manifest, exact pins, original payload hashes, replay completeness/limits and COST; Review14 follows a separate root check and is not issued here.
''')
    write('HANDOFF.md',f'''# READY for root check — run44460583125/1

Task `{provenance['task']}` plus terminal addendum `{provenance['terminal_addendum']}` executed in the requested new directory only. Classification: **2 native positive SUCCESS;3 exact intended negative FAILURE;2 child600 WALL timeouts; strict0; SOURCE_REPORTED provisional candidates2; no admission/proof credit.** Campaign {cost['campaign_elapsed_seconds']:.9f}s; insert51.863257375s and sort9223.202229754s are native verification_time_s. See RESULT.md and COST.json for distinct compilation/whole-child/setup scopes, effective caps, sampling, cleanup and censoring.

All7 singleton starts and portable completion seals are present; materialized/upload-only replay agrees. Five completed inventories are fully located, with28 assessed U and7 retained SUCCESS unsupported guards. Two incomplete inventories,17/9 symbolic-length covers and native timings remain UNKNOWN. No location exception is proposed/applied. Native compiler/MIR/property binding gaps remain UNKNOWN. UREJECT_ALL/proposalDISABLED and original producer history are preserved.

Root should verify this directory at the exact fullg0 commit returned in the handoff, all MANIFEST.json bytes/hashes, sourcef1bdf11902252ad1178f42403c253ae710fecbaf, triggerc2bbdb972cfe0e6f7472cf8bd93f1fa7c5e87acd/reviewedcontrold675ef70dc1ada13330efc0990c2e1d6b0d21a5a same tree6280a305cba669f59ae82119fcf5374115ecacf7, stocktool0aac16ef62da9e9d5645782d458593e5d78143ba, request23c137a331acb92610b3f0cf2192a0e16081dbf0815a35fc3c8d88742c0a1fa3, workflow317f92181bee9470ddf65471def7154fcacbf1e6fb7913220ca1f154ca915a55, artifact14501442643/namech8-s3-2-44460583125-1/374679B/digest{integ['sha256']}, compact member/payload hashes and105-member completeness.

Validation PASS: {validation['checks_count']} checks/{len(validation['adverse_tests'])} adverse controls. Reproduce with `python3 replay.py` in a disposable copy of the committed directory to preserve sealed bytes; no acquisition rerun is needed. Dependencies and reader hashes are in PROVENANCE.json. Current high/FastOFF retained; no subagents/model changes. No CI/native/raw/full/GCS/ledger/budget/policy/source/control writes or push. No review issued: separately authorized Review14 follows root check. No S4 implementation or next run authorized by this intake. Return any findings to CURRENT11 as an immutable correction.
''')
    files={p.name:{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='MANIFEST.json'}
    manifest={'schema':'s34-intake-manifest-v1','status':'READY','scope':'THIS_DIRECTORY_ONLY','self_excluded':True,'files':files,'file_count':len(files),'task':provenance['task'],'terminal_addendum':provenance['terminal_addendum'],'proof_credit':'NONE'}
    (HERE/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'READY','manifest_members':len(files),'manifest_sha256':sha((HERE/'MANIFEST.json').read_bytes())}))
if __name__=='__main__':main()
