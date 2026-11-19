#!/usr/bin/env python3
"""Render immutable terminal handoff from verified bounded projections."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def read(n):return json.loads((HERE/n).read_bytes())
def main():
 result=read('RESULT.json');v=read('VALIDATION.json');a=read('AUDIT-VALIDATION.json');cost=read('COST.json');integ=read('artifact-integrity.json');roots=read('ROOTS.json')['rows'];pins=read('INPUTS.json')['terminal_inputs']
 assert result['status']=='READY' and v['status']==a['status']=='PASS'
 table='| Root | Native verdict | Receipt | Whole child s | Compile/export bound s | Native verification s |\n|---|---|---|---:|---:|---:|\n'
 for r,c in zip(roots,cost['rows']):
  native=r['native_verdict'].replace('UNKNOWN_INCOMPLETE_EXPORT','UNKNOWN (censored)');nv=c['native_verification_time_s'];nv=f'{nv:.9f}' if isinstance(nv,(int,float)) else 'UNKNOWN'
  table+=f"| `{r['id']}` | {native} | {r['canonical_status']} | {c['execution']['elapsed_seconds']:.3f} | {c['compile_elapsed_upper_bound_seconds']:.3f} | {nv} |\n"
 text=f'''# READY — run44481580554 attempt1 terminal intake

SELECTED_PARTIAL; native2 SUCCESS,4 exact intended negative FAILURE,2 child600 wall timeouts. Strict producer matches0; admission/proof credit NONE. All8 planned roots started once in order, with8 fresh singleton namespaces and8 hash-verified durable completion seals. Actual terminal schema is the exact string `ch8-s4p-1-campaign-v1`, selected_roots is genuine integer8, no global stop or missing selected group. Fresh local materialization and public upload-only collection agree.

The two fallback native successes are exact bounded SOURCE_REPORTED candidates for independent review at initialized V34/base1, all34 independent logical u8 values, Cell<u8>/KeyLess<Cell<u8>>, N0..2 and N3..4. Four located SUCCESS roles per block,3/2 located per-length SAT covers and five feasible SAT witnesses per block are observed. No witness is claimed for impossible N0/1 conditions. Every native unwind check in those blocks is SUCCESS; this is distinct from the source unwind36 derivation. Each fallback receipt remains UNKNOWN because exactly one classunreachable/statusSUCCESS system property has present-null file/line and a lib.rs:0:0 display. This class differs from statusUNREACHABLE U. The frozen rich reader rejects both after reconciling all native count/status/guard partitions. Authentic-field streaming reconstruction confirms the frozen parser preserves display text and converts the zero sentinel to present-null coordinates; it does not establish the actual emitter, positive source coordinate or MIR origin.

The four negative fixtures have exactly the intended located labels S2_NEG_CHECKER_ORDER, S2_NEG_CHECKER_COUNT, S2_NEG_SORT13_WEAK and S4_NEG_CELL_COUNT. S4_NEG_CELL_ACTIVE is located SUCCESS; checker-only [0,1]->[0,0] corruption preserves order and violates full counts. It is not an actual-callee defect. sort13weak is the fixed descending fixture, not arbitrary len13 proof.

Across6 completed native inventories:594 properties,26 individual statusUNREACHABLE records with pinned source-local definedness arguments,7 retained SUCCESS unsupported guards. Their source contexts and limits are preserved in U-ARGUMENTS/GUARD-ARGUMENTS. Unsupported operations receive no generic support claim. Source21 assertions/30 covers are site plans, not native counts. Both network native inventories, roles, covers, U and guards are censored UNKNOWN, never zero/NOT_RUN. Unselected larger domains remain NOT_SELECTED, separately from started network UNKNOWN.

{table}
Campaign elapsed is {cost['campaign_elapsed_seconds']:.9f}s. Fallback native verification metrics140.741771488/144.622441392s differ from wholechild189.050/193.600s, compile/export46.453/46.890s, campaign and setup. Setup total is {cost['setup']['setup_total_seconds']:.9f}s and exported tool build execution is {cost['setup']['elapsed_seconds']:.3f}s. These scopes are distinct; no invented backend timing or speedup.

Both network cutoffs are independently bound to child600 wholechild wall, including compilation: observed601.428/601.401s, initial export48.195/45.976s below compile180, signal15/originalexit-15, sampled PGID RSS3,515,064/3,516,320KiB below Ceff6,291,456KiB. Observed availability14,944,724/15,301,516KiB yields Ceff=min(local6GiB,outer12GiB,A-2GiB)=6GiB. No observed compile180/RSS/outer/slot/global cutoff. Owned shutdown/reap/cleanup is verified, serial continuation follows cleanup. RSS is nominal50ms nonatomic owned PGID VmRSS; outer12GiB owned census and reserve2GiB remain unchanged. True kernel/cgroup/tree peak, RSS at signal, exact symex/backend phase and uncensored native verification time remain UNKNOWN. No resource escalation is proposed or applied.

LOCATION-PROPOSAL recommends only the two exact authenticated packets for independent14 and a separate root/coordinator decision. It remains NOT_APPLIED, binds run/attempt/full IDs/display IDs/selector/invocation/namespace/protected tuple/member digests/full property inventory, requires both null keys and exactly one offending record per block, and preserves every other role/cover/U/guard/count and producer result. Oldsort4same f740 and merge8 ff193 packets plus their exact independent reviews were compared; the display/null/class/status structure is similar, while IDs and invocation/protected identities differ. Existing original-run admissions never transfer. Shared emitter/source/MIR origin UNKNOWN. No global/suffix/unreachable/stdlib waiver or runtime/parser/policy edit.

Validation: {v['checks_count']} replay/integrity/source/native checks, {a['checks_count']} supplemental dependency/source/guard/length/epoch checks, {len(v['adverse_tests'])} targeted terminal/cardinality/seal/protected mutations, {len(v['location_adverse_tests'])} hypothetical exact-location adverse mutations; all PASS/reject as required. Source/tool/control/request/cfg/export/binaries bind through E0,pre,workerBEFORE/AFTER,controllerpost for all states. Protected read errors/drift are not erased; original structured runtime diagnostics/errno are retained. This run needs no missing-inner-AFTER recovery. Prior exact reviewR14-01/02 closures and author/review manifests independently hash-checked; host305 remains regression evidence only. No full host/native rerun.

One compact member was acquired using the existing bounded reader after connected metadata/digest verification. Artifact14510873270,416580 transport bytes, sha256:{integ['sha256']}; sole retained member group-evidence.json.gz,{integ['payload_bytes']} bytes, sha256:{integ['payload_sha256']}; uncompressed payload sha256:{integ['uncompressed_sha256']};119 structured members all sizes/hashes checked. ZIP transport existed only in bounded memory and was not saved; no raw/full logs/archives/GCS were read or retained. Evidence data was never executed.

Qualification/admission remains false. No generic trait/type/caller/ownership/panic/initmask/dstinit/provider/summary/MIR/B1/B2/fullN16N32 credit; fallback5..16/network5..32/general obligations OPEN. Below9 concrete paths enable no sort4/merge8/sort9 assumed summary. Any future finite union0..4 requires completed observations, independent review and separate admission.

Settings high/FastOFF preserved; no subagents/model changes. No source/control/caps/active parser/policy/ledger/accounting edits, compiler/cargo/rustc/Kani/CBMC/verifier/fullrunner/CI/rerun/cancel/push/PR/comment/cron actions. Owned output only.
'''
 (HERE/'READY.md').write_text(text)
 (HERE/'HANDOFF.md').write_text(f'''# Immutable READY handoff — W11

Use the full40-character g0 commit returned with this handoff, containing this directory. MANIFEST.json covers every packet file except itself; Git commit identity covers the manifest. Root verifies that exact commit and manifest before issuing independent14. The intake author does not issue or decide review, metadata admission or functional qualification.

Starting task `{read('INPUTS.json')['task_commit']}`, inherited base task `{read('INPUTS.json')['base_task']}`. Source `{pins['package']['source']['sha']}`, stock tool `{pins['package']['tool']['sha']}`, reviewed control `{pins['package']['control']['sha']}`, actual push head `{pins['expected_run']['head']}`, shared tree `{pins['expected_run']['tree']}`. Author `{pins['package']['g0']}`, review `{pins['independent_review']['g0']}`, consumed GO `{pins['root_go']['g0']}`. Request `{pins['request']['sha256']}`, workflow `{pins['request']['workflow_sha256']}`. Native run44481580554/attempt1 completedFAILURE, exact head/ref/tree; artifact14510873270 digest `{pins['artifact']['digest']}`.

Read READY.md and RESULT.json, then QUALIFICATION, METADATA-GAP, LOCATION-PROPOSAL/COMPARISON, COST, PREFIX, PROTECTED, PROVENANCE, MANIFEST, U-ARGUMENTS, GUARD-ARGUMENTS and LENGTH-ROLES-SAT. `python3 replay.py` followed by `python3 audit.py` reproduces offline projections with the pinned local Git objects; scripts only use the compact packet, source gates and frozen pure readers. No acquisition, native runner or full Validate is part of replay. `python3 seal.py --check` checks all packet hashes. Do not reacquire the artifact.

Verified result:8 starts/seals, local/upload agreement, no global stop; native2 fallback SUCCESS/4 intended negative FAILURE/2 network child600 wall timeouts; strict0 and admission/proof credit NONE.594 native properties,26 U arguments,7 SUCCESS guards. Two exact fallback location proposals NOT_APPLIED. Network native inventory/roles/SAT/U/guards UNKNOWN. Both networks are wall-censored with compile180 and sampled RSS effective6GiB not reached; exact costs/availability/cleanup in COST. Setup/campaign/native metrics remain separate.

Independent14 next: review the exact immutable packet, source-local U/guard reasoning, role/SAT and location cardinalities, all-state protected/prefix semantics, and cost/censoring. Root/coordinator separately decides any exact metadata admission; no original-run exception transfers. Source-only network plan13 may consume COST/QUALIFICATION limits and pinned identities only; this handoff grants no implementation, resource escalation or native/CI retry.

No worker admission. No ledger/accounting/push/source/control/caps/model changes. high/FastOFF preserved, no subagents. Completion reason: the authorized terminal intake and reviewable proposal/cost handoff are finished; residual UNKNOWNs are recorded rather than promoted to credit.
''')
 print(json.dumps({'render':'PASS','ready':'READY.md','handoff':'HANDOFF.md'}))
if __name__=='__main__':main()
