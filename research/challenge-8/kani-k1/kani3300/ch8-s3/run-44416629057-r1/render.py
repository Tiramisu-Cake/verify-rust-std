#!/usr/bin/env python3
"""Render corrected reporting views; inherited evidence and policy stay unchanged."""
import json,hashlib,subprocess
from pathlib import Path
P=Path(__file__).resolve().parent
def read(n):return json.loads((P/n).read_text())
def text(n,s):(P/n).write_text(s.rstrip()+'\n')
def sha(b):return hashlib.sha256(b).hexdigest()
q=read('QUALIFICATION.json');cost=read('COST.json');result=read('RESULT.json');gap=read('METADATA-GAP.json');replay=read('PREFIX-REPLAY.json');prov=read('PROVENANCE.json');inventory=read('INVENTORY.json')
rows=q['rows']
admission=read('ADMISSION-REFERENCE.json')
limits='Exact reversible location metadata gate accepted by coordinator+planner at f74025e493a627962842e8f7bc6a2766d33dd300, based on review a9fe0055aab3279e3f5bb71bde9667925da80e65 and base intake d29ab46dbbb45d7106fa30c3ac04bb419a2ac286. ADMISSION-REFERENCE.json retains the full exact property tuple, present null file/line, counts, protected identities and constraints. Actual source origin/lowering remain UNKNOWN. Overall qualification awaits SAME14 reporting delta and root/coordinator case assessment; no whole-S3/B1/B2/caller/generic proof credit. Producer UNKNOWN, strict0/9, REJECT_ALL and disabled U proposal stay unchanged; no runtime reader patch.'
guard_table='| Root | Native ID | Description | Class | Status | File | Line |\n|---|---|---|---|---|---|---|\n'
for rid,guards in q['successful_unsupported_guard_inventory']['roots'].items():
 for g in guards:
  cells=[rid,g['id'],g['description'],g['class'],g['status'],g['file'],g['line']]
  guard_table+='| '+' | '.join(str(x).replace('|','&#124;').replace('\n',' ') for x in cells)+' |\n'

table='| Root | Native | Checks S/F/U | Covers SAT/required | Literal roles | S1 assessment |\n|---|---|---:|---:|---|---|\n'
for r in rows:
 c=r['native_check_counts'];v=r['native_verdict'];roles=[x for x in r['literal_roles'] if x['class']=='assertion'];cover=[x for x in r['literal_roles'] if x['class']=='cover']
 state='exact location gate admitted; overall pending delta' if r['id']=='s3_sort4_u8_same_alloc' else 'provisional source-reported' if v else 'no completed result'
 table+=f"| {r['id']} | {v['verdict'] if v else 'UNKNOWN'} | {c.get('SUCCESS',0)}/{c.get('FAILURE',0)}/{c.get('UNREACHABLE',0)} | {sum(x['exact_match'] for x in cover)}/{len(cover)} | {sum(x['exact_match'] for x in roles)}/{len(roles)} | {state} |\n"
text('QUALIFICATION.md',f'''# S1 criteria assessment — run44416629057

{table}

Checks exclude covers. Zero counts on unfinished roots mean no property inventory exported, not zero obligations. All seven completed native results have exact singleton selectors and same-invocation literal source-site bindings. The three negatives each fail exactly their intended assertion: S2_NEG_CHECKER_ORDER at sorting_s2_batch.rs:140, S2_NEG_CHECKER_COUNT at134, S2_NEG_SORT13_WEAK at149. There are no additional failures, failed unwinding checks or safety failures in these completed inventories. Producer failure_kind PANICS_ONLY on negatives is the stock classification of the intended literal assertion, not evidence of an incidental panic. Each of the four completed positive exports retains four SUCCESS unsupported_construct guards, sixteen total. Exact native arrays, including trace_available, remain in NATIVE.json and are explicitly projected per root in QUALIFICATION.json and INVENTORY.json. Successful guards are distinct from executed unsupported failures; FAILED/UNKNOWN guards are never accepted as SUCCESS. Strict producer expected_observation rejects these nonempty arrays independently of U.

{guard_table}

Strict producer outcome remains **0/9 expected matches**: REJECT_ALL, proposal DISABLED, unknown/role-U rejected. No policy, ledger qualification or native verdict is rewritten. S1 criteria yield six provisionally eligible source-reported results and sort4same with its exact location metadata gate accepted. The two capped leaves have no completed native result. {limits}

Every U occurrence has its own root, full producer ID/class/description/status, site, exact source hash/context, effective cfg, provider context, predicate, premises and source-local argument in QUALIFICATION.json/U_instances (42 entries). No U is waived because of a status, cover, library name or whitelist. Arguments cover guarded abs_diff subtraction, constant formatting shift, guarded align-1, guarded allocation-size division, sort4 boolean offsets, merge length8 arithmetic, and each guarded checker index/count increment. Frozen93f158 is a disabled reference; no historical instance is substituted for this invocation and no proposal argument is automatically reused. Independent caller-to-MIR origin remains UNKNOWN.

PFC source-reported registration and contracted-function context match native core metadata for all six candidates; actual-body targets are swap_if_less, sort4_stable, insert_tail and bidirectional_merge. Selected PFC harnesses have no ordinary/verified stubs. The sort13 weak negative uses the fixed descending length13 [12u8,11,10,9,8,7,6,5,4,3,2,1,0] fixture at source513341f sorting_s2_batch.rs:147, the source-bound sort13_fault_network caller copy and exact ordinary s2_swap_seam -> weak_swap replacement. Its one intended literal failure and eight U arguments apply to that fixture; it is never an actual sort13 proof. Existing ordinary/cfg/provider/contract-stack/lexical static gates passed in the inherited exact intake/review audit and were not rerun. This is Profiles v4 SOURCE_REPORTED assurance, not independent MIR/compiler transformation proof.

Positive symbolic byte values remain full0..255. The three negative fixtures retain their fixed domains; sort13_weak is fixed descending length13. Domain/backing/offset/order, concrete u8/KeyLess, source/outside frame, canaries, destination MaybeUninit and typed post-call loads are per-row bindings in JSON. Stock checks and successful system checks stay visible. No separate experimental uninit-checks or valid-value-checks flags were enabled; no independent initialization theorem is claimed. SAT covers (24/44 selected positive source covers observed) show witnesses at exact required source sites; they do not prove U, frame, generic allocation or callers. Forty-four covers and71 total literal role sites are source inventories, not native check counts. Completed inventories contain43 literal role sites; incomplete leaves retain the remaining28 as UNKNOWN.

Positive SUCCESS roles, with exact producer matches and coordinates in JSON:

'''+ '\n'.join('- '+r['id']+': '+', '.join(x['description'] for x in r['literal_roles'] if x['class']=='assertion') for r in rows if r['mode']=='PFC') + '''

No assumed summary is promoted. S3-2 must preserve exact identities and caller geometry, value domain, frame/init/locality and provider applicability, and obtain whatever root/coordinator admission decisions remain required.
''')
ct='| Root | Compile upper bound s | Native verification s | Child elapsed s | Sampled PGID max KiB | Termination |\n|---|---:|---:|---:|---:|---|\n'
for x in cost['rows']:
 e=x['execution'];v=x['native_verification_time_s'];ct+=f"| {x['id']} | {x['compile_elapsed_upper_bound_seconds']:.3f} | {v if isinstance(v,(int,float)) else 'UNKNOWN'} | {e['elapsed_seconds']:.3f} | {e['rss_peak_kib']} | {e.get('termination_reason','completed')} |\n"
text('COST.md',f'''# Cost and censoring

{ct}

Campaign elapsed1454.135514967s; all nine launched serially and all nine sealed. Native job22:59:00–23:31:25Z on2026-11-18. Validate149s, source identity5s, tool setup68s, once-only tool build259s, roots step1455s (second-resolution GitHub metadata). Setup and build succeeded; roots step failed. Campaign SELECTED_PARTIAL/native workflow failure is separate from each root verdict.

Compile values are upper bounds for STD_PROJECT_COMPILATION_AND_LINK_UNTIL_INITIAL_EXPORT, not compiler CPU and not exact exclusive compilation. Native verification values are stock per-harness resources. Symex/backend phase times/steps/VCC and per-root component RSS are UNKNOWN_NOT_EXPORTED. No whole-child or censored duration is labeled native verification time. No matched speedup claim.

insert_tail: execution.termination_reason=rss_cap, timed_out=false,112.349s; original exit-15/signal15, verified child shutdown, worker exit0 and containment verified; next merge8separate ran. Local sampled PGID max6326988KiB exceeds cap6291456KiB (overshoot35532KiB); outer sampled peak6344420KiB is below12582912KiB. Exact runner loop samples RSS, updates maximum, then breaks on the first value above cap; thus6326988KiB is the reconstructed triggering RSS sample. RSS at subsequent SIGTERM/kill and precise phase are UNKNOWN. Compilation boundary was already observed at34.680s; backend component sampled max6312480KiB is a non-simultaneous component peak, not an independently timed kill-phase measurement.

merge8same: execution.termination_reason=timeout, timed_out=true,600.205s; original exit-15/signal15, verified child shutdown, worker exit0 and containment verified; sort13weak ran next. This is whole-child600s including the35.105s compile upper bound, not CBMC verification600s. PGID sampled peak2558128KiB; RSS at trigger/kill UNKNOWN. No local RSS breach, supervisor cutoff, slot720 cutoff or outer/global stop is recorded. The compile180s subcap was not the trigger for either leaf. Supervised worker limit710s plus publication reserve10s fits slot720s. Neither campaign6900/outer7500 nor phase8100/global caps fired.

All containment/cleanup records and original exits are preserved in COST.json. Polling is non-atomic PGID VmRSS (0.05s); component peaks are by comm and non-simultaneous; outer census is another sampling scope. None is a true kernel/cgroup/tree peak. Unfinished verification durations are censored and cannot be recovered by subtracting compile from elapsed. 600 minus compile upper bound is envelope arithmetic only, not a phase duration.
''')
text('METADATA-GAP.md',f'''# sort4same location gap — exact metadata gate accepted; runtime repair NOT_APPLIED

Exactly one offending record in the authenticated compact properties.json:

- ID/display_id: `{gap['offending_records'][0]['id']}`
- class `unreachable`, status `SUCCESS`, description `unreachable code`.
- normalized `file` and `line` fields are **present null**, not absent.
- location_display is `{gap['offending_records'][0]['location_display']}`.

The file string and zero line/column survive the compact rich export. Positive source coordinates do not. The stock JSON successful-property representation has a success count and non-success buckets; it does not export this successful check's individual SourceLocation. Native per-check CBMC JSON is not in the compact package. The harness registration's valid source line70 is a different record and cannot repair this property. Its true source origin remains UNKNOWN.

Exact tool0aac SourceLocation Display formats stored file/line/column fields; this display contains lib.rs:0:0. CONTROLcb6303 rich_evidence.RegularEvidence._record requires `[1-9][0-9]*` for line and therefore maps both normalized fields to null while preserving display. validate:213–217 requires nonempty file plus positive decimal line OR an exact location_exception. The S1-07 exception map does not contain this harness/property tuple. runner._run_group:1178 raises ValueError; exception path persists properties.json INCOMPLETE and receipt FAILED; controller root_outcome preserves UNKNOWN, seals it and continues. No property was lost.

The frozen reader reproduces the exact rejection after checking every count/status bucket. An isolated parser reconstruction from authentic structured fields reproduces display and normalized nulls. This is a recognized display shape with a zero sentinel rejected by location qualification, not a compact projection accidentally omitting valid coordinates. No actual positive coordinate can be recovered from the retained fields. Compiler/lowering reason for the sentinel is UNKNOWN.

This is a successful system unreachable-code check, not a literal assertion role, cover, failed panic or unwind property. All five positive assertion roles and seven covers bind exactly and independently at their valid leaf source coordinates; all5 U sites have separate source-local arguments. Native SUCCESS351/356 checks,5U,7SAT covers remains separate from rich metadata failure and strict rejection.

{gap['repair_proposal']}

{gap['regression_proposal']}

{limits}

The repair proposal above remains historical NOT_APPLIED runtime work. No exception, policy, source, reader or artifact was changed.
''')
text('PREFIX-REPLAY.md',f'''# Portable completed-prefix replay

Exact cb63033ffcde918f4341146e56373476b8eeb569 source readers verify all nine completion seals, their structured-file hashes and prefix order. A fresh path containing only group-evidence.json.gz produces exactly the same collector object as the materialized133 structured members: `{replay['collector_state']}`, global_stop=false, selected_missing_groups=[]. Three canonical UNKNOWN rows remain UNKNOWN: sort4same metadata failure, insert_tail RSS stop, merge8same timeout. Completion seals establish durable observations and continuation, not successful qualification.

Every selected invocation has a distinct target namespace, exact singleton argv/selector/native start, requested cfg/unwind, exact request/source/tool/compile binding and verified containment. All five recorded inventories (baseline E0, controller pre, worker BEFORE, worker AFTER, controller post) have equal canonical absolute paths and recorded SHA256s for each binary. No controller recovery or recorded error suppression was used. E1..E9 contexts are preserved in INVENTORY.json. Physical inode/device/realpath identity and unobserved intermediate bytes remain UNKNOWN.

Frozen protected-reader mutation rejects an altered worker binary hash. Authentic evidence bytes stay unchanged. sort4same reader replay independently reproduces the metadata rejection. The base d29 VALIDATION.json records those inherited checks; current VALIDATION.json pins its hash and records only the new reporting checks. No full runner, compiler or solver was run.
''')
text('RESULT.md',f'''# READY — S3-1-r2 terminal intake

Run44416629057/attempt1, push, exact7497ecdb3934585634f5f04e4ff7c6cc42450c0b: native completed/failure; campaign SELECTED_PARTIAL1454.135514967s, no global stop, all9 completion seals. Four native SUCCESS, three intended literal negative FAILURE, two unfinished/capped leaves. Strict producer expected matches0/9; S1 assessment6 provisional source-reported plus sort4same exact location metadata gate accepted; overall qualification pending.

{limits}

{table}

sort4same metadata cause: exactly one successful system check has display lib.rs:0:0; positive-line decoder nulls both normalized coordinates and existing exact exception does not apply. Native property and every intended role/cover remain present. Full diagnosis, historical NOT_APPLIED runtime proposal, and accepted exact metadata gate: METADATA-GAP.md/json and ADMISSION-REFERENCE.json.

insert_tail stopped on local RSS cap112.349s, not child600. merge8same stopped on whole-child timeout600.205s including compilation. Both retain exit-15/SIGTERM15, verified shutdown/containment, worker0, and continuation. COST.md/json keeps actual native times separate from elapsed/censored values.

The sealed d29 intake acquired only artifact14482022386/ch8-s3-1-44416629057-1, transport481904bytes, digest `{prov['artifact']['digest']}` verified before its extraction per the preserved receipt and prior review. This correction does not reacquire or independently rehash the unavailable transport. No transport ZIP saved. Sole member group-evidence.json.gz SHA256 `{prov['payload_sha256']}`;133 structured records individually checked by the inherited exact intake/review audit; this correction rechecks only the relevant structured members. INPUTS and PROVENANCE pin task03ad6ec5, source513341f, tool0aac16e, controlcb63033, review12c4dc5, GOc59d410 and disabled proposal93f158e by full commits. MANIFEST binds this new immutable reporting correction; CHANGE-MAP.json records exact changed/copied/added file hashes against d29 intake. Compact payload, all native outcomes/counts, all42 U records/arguments, roles, covers, PFC/context, portable prefix and resource-cost observations remain unchanged. sort13_weak is fixed descending length13 [12u8,11,10,9,8,7,6,5,4,3,2,1,0] with the exact ordinary weak_swap seam. Four completed positives retain four SUCCESS unsupported guards each, sixteen total.

Use QUALIFICATION.json for each native property/site/context/U argument, INVENTORY.json for exact request/argv/epochs/namespace/binary/source bindings, NATIVE.json for compact native counts/statuses, PREFIX-REPLAY.json for durable replay, and HANDOFF.md for S3-2 constraints. No policy/source/control/CI/accounting action or push was performed; high/FastOFF/no subagents preserved.
''')
text('HANDOFF.md',f'''# READY to root — immutable W14-01/W14-02 reporting correction for SAME14 delta

Read RESULT.md, QUALIFICATION.md/json, METADATA-GAP.md/json, COST.md/json, PREFIX-REPLAY.json and manifest. Four native successful actual-body leaf observations are usable as source-reported planning inputs: swap geometry, sort4 separate, merge8 separate, and conditional sort4 same. Three literal negatives were detected at the intended sites. Strict REJECT_ALL still qualifies none. S1 eligibility is provisional; independent proof NONE. Both findings are author-repaired and await SAME14 exact delta.

{limits}

All42 U instances have individual source-local definedness arguments and native links; root/coordinator must assess them under S1 without enabling historical proposal93f158. sort4same has the narrowly scoped location-only gate accepted as pinned in ADMISSION-REFERENCE.json; its authentic record and full native/role inventory are retained. No valid positive source origin was invented. The original worker may implement the NOT_APPLIED repair under separate authorization/review; this intake changes no reader.

W14-01: sort13_weak is the fixed descending length13 [12u8,11,10,9,8,7,6,5,4,3,2,1,0] at sorting_s2_batch.rs:147, exact sort13_fault_network caller copy and ordinary s2_swap_seam -> weak_swap. One intended failure/eight U arguments remain unchanged. W14-02: each completed positive has four exact SUCCESS unsupported guards, sixteen total, retained in native arrays and per-root qualification/inventory/report. Missing, altered, FAILED or UNKNOWN guard inventories are rejected by reporting checks; strict producer still rejects nonempty arrays.

For S3-2 preserve full independent positive byte values, concrete KeyLess<u8>, exact source/tool/cfg/PFC context and backing/offset/init/frame geometry. swap is backing34/base0..20/indices0..12. sort4 separate is src6/dst6 at1; same allocation is backing48 with disjoint length4 ranges0..44. merge8 separate is src10/dst10 at1 with sorted halves4+4. There is no completed insert_tail length2..17 or same-allocation merge8 proof; their failed resource envelopes are112.349s RSS6GiB and600.205s whole-child respectively. They are not ready summaries.

No generic T/F, arbitrary allocation, sort8/13/16/32 caller, assumed summary, panic/unwind/Drop or locality theorem is supplied. Typed post-call loads and frame roles remain source-reported observations within pinned stock checks; initialization/provider and caller applicability obligations cannot be dropped. The PFC native registration is not an independent MIR proof. Keep all required controls, covers, sorting safety separation and remaining metadata qualifications. SAME14/CURRENT110 consumes this exact committed correction before root/coordinator overall case assessment; planner13 may use the bounded observations; no duplicate DAG design or implementation was done here.

No policy/source/control/runtime/CI/accounting actions, reruns, cancellation, push, PR or external message. Ledgeraf484c6 unchanged (reference only). Historical evidence remains immutable. Base d29ab46dbbb45d7106fa30c3ac04bb419a2ac286, review a9fe0055aab3279e3f5bb71bde9667925da80e65 and task/admission f74025e493a627962842e8f7bc6a2766d33dd300 are pinned. CORRECTIONS.json records author closure of BOTH W14-01/W14-02 pending SAME14 delta. CHANGE-MAP.json and MANIFEST give exact file bindings. READY fullg0 is returned in the final response; commit records the exact package without a self-referential commit field.
''')
# Pin exact source of the decoder/display diagnosis and final consistency checks.
tool_trace={}
for rel in ['kani-driver/src/cbmc_output_parser.rs','kani-driver/src/cbmc_property_renderer.rs','kani-driver/src/frontend/schema_utils.rs']:
    b=subprocess.check_output(['git','-C','/root/kani-ch8-s3-1-r2-control-w13','show','0aac16ef62da9e9d5645782d458593e5d78143ba:'+rel])
    tool_trace[rel]={'sha256':sha(b),'bytes':len(b),'tool_commit':'0aac16ef62da9e9d5645782d458593e5d78143ba'}
prov['metadata_diagnosis_tool_sources']=tool_trace
text('PROVENANCE.json',json.dumps(prov,indent=2))
v=read('VALIDATION.json')
assert len(q['U_instances'])==42 and all(x['source_local_argument'] and x['predicate'] and x['source_context'] for x in q['U_instances'])
assert sum(len(x['literal_roles']) for x in rows)==71
assert sum(sum(y['exact_match'] for y in x['literal_roles']) for x in rows)==43
assert all(not x['strict_expected_match'] for x in rows)
assert sum(x['native_check_counts'].get('UNREACHABLE',0) for x in rows)==42
assert all(x['execution']['child_shutdown_verified'] and x['containment']['verified'] for x in cost['rows'])
assert [x['execution'].get('termination_reason') for x in cost['rows']]==[None,None,None,None,None,'rss_cap',None,'timeout',None]
v['final_consistency']={'status':'PASS','source_literal_sites':71,'completed_native_literal_sites':43,'unresolved_literal_sites':28,'U_instances':42,'tool_source_trace_pinned':True,'manifest_validation':'SHA256+length and hash-manifest agreement checked after rendering; manifests exclude themselves'}
text('VALIDATION.json',json.dumps(v,indent=2))
# Renderer consistency checks apply to newly generated views only.
for filename in ('QUALIFICATION.md','RESULT.md','HANDOFF.md'):
 body=(P/filename).read_text()
 assert 'fixed descending length13' in body.lower(), filename
 assert 'sixteen total' in body, filename
 assert 'overall qualification' in body.lower(), filename
 assert 'arrays are empty' not in body, filename
for rid,guards in q['successful_unsupported_guard_inventory']['roots'].items():
 assert len(guards)==4 and all(g['status']=='SUCCESS' for g in guards)
 assert next(r for r in rows if r['id']==rid)['unsupported_constructs']==guards
 assert next(r for r in inventory['selected'] if r['id']==rid)['unsupported_constructs']==guards
 for g in guards:
  assert all(str(g[k]) in (P/'QUALIFICATION.md').read_text() for k in ('id','description','class','status','file','line'))
v['renderer_checks']={'status':'PASS','guard_records':16,'domain_summary':'fixed descending length13; positive full-byte domains unchanged','admission_scope':'exact metadata gate only; overall qualification pending SAME14 delta'}
text('VALIDATION.json',json.dumps(v,indent=2))
base=P.with_name('run-44416629057')
excluded=['MANIFEST.json','MANIFEST.sha256','CHANGE-MAP.json']
delta={}
for f in sorted(P.iterdir()):
 if f.is_file() and f.name not in excluded:
  old=base/f.name
  before={'sha256':sha(old.read_bytes()),'bytes':old.stat().st_size} if old.exists() else None
  after={'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size}
  delta[f.name]={'disposition':'ADDED' if before is None else 'UNCHANGED' if before==after else 'CHANGED','before':before,'after':after}
text('CHANGE-MAP.json',json.dumps({'base_commit':'d29ab46dbbb45d7106fa30c3ac04bb419a2ac286','review_commit':'a9fe0055aab3279e3f5bb71bde9667925da80e65','admission_commit':'f74025e493a627962842e8f7bc6a2766d33dd300','base_path':str(base.relative_to(P.parents[5])),'excluded_self_and_manifests':excluded,'files':delta},indent=2))
# Bind every owned artifact. Manifest files necessarily exclude themselves.
files={str(f.relative_to(P)):{'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size} for f in sorted(P.rglob('*')) if f.is_file() and f.name not in ['MANIFEST.json','MANIFEST.sha256']}
text('MANIFEST.json',json.dumps({'schema':'S3-intake-reporting-correction-manifest-v1','base_commit':'d29ab46dbbb45d7106fa30c3ac04bb419a2ac286','review_commit':'a9fe0055aab3279e3f5bb71bde9667925da80e65','admission_commit':'f74025e493a627962842e8f7bc6a2766d33dd300','files':files,'excluded':['MANIFEST.json','MANIFEST.sha256'],'transport_zip_saved':False,'artifact_id':14482022386,'transport_digest':prov['artifact']['digest'],'member_sha256':prov['payload_sha256']},indent=2))
text('MANIFEST.sha256','\n'.join(v['sha256']+'  '+k for k,v in files.items()))
sealed=read('MANIFEST.json')
hash_manifest={name:digest for digest,name in (line.split('  ',1) for line in (P/'MANIFEST.sha256').read_text().splitlines())}
assert set(sealed['files'])==set(hash_manifest)=={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and f.name not in sealed['excluded']}
for name,meta in sealed['files'].items():
 assert meta=={'sha256':sha((P/name).read_bytes()),'bytes':(P/name).stat().st_size} and hash_manifest[name]==meta['sha256']
print(json.dumps({'files':len(files),'bytes':sum(v['bytes'] for v in files.values()),'manifest_sha256':sha((P/'MANIFEST.json').read_bytes())}))
