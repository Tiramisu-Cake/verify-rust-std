"""Seal only after actual exact final Validate PASS. No native/CI/accounting."""
from pathlib import Path
import hashlib,json,re,subprocess
OUT=Path(__file__).resolve().parent
D=lambda b:hashlib.sha256(b).hexdigest()
read=lambda name:json.loads((OUT/name).read_text())
def put(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
pins=read('PINS.json');final=read('FINAL-VALIDATE.json');request=read('CI-REQUEST.json')
assert final['status']=='PASS' and final['exit_code']==0 and not final['timed_out'] and final['clean_after']
assert final['execution_count']==1 and final['limit_seconds']==1080 and final['margin_at_18_minutes']>=1.5
assert final['control_sha']==pins['control']['sha'] and final['control_tree']==pins['control']['tree']
assert final['request_sha256']==pins['request']['sha256']==read('PREFLIGHT.json')['request_sha256']
summary=json.loads((OUT/'FINAL-VALIDATE.stdout').read_text().splitlines()[-1])
assert summary['success'] and summary['failures']==summary['errors']==0
assert summary['test_counts']=={'legacy':136,'s3':56,'s32':35,'bridge1':40,'s4p':38,'s4p2':39}
precursor=read('tests/control-321c266-precursor/FINAL-VALIDATE.json')
assert precursor['control_sha']=='321c266daf58309ae3eadc6d5c3f358766938ac0'
assert precursor['execution_count']==1
status='READY_FOR_ROOT_FULLPIN_CHECK_AND_W14_EXACT_PACKAGE_REVIEW_NOT_GO'
validation={'actual_final_validate_execution_count':1,'tests':sum(summary['test_counts'].values()),'test_counts':summary['test_counts'],
    'exit_code':0,'elapsed_seconds':final['elapsed_seconds'],'internal_elapsed_seconds':summary['elapsed_seconds'],
    'margin_at_18_minutes':final['margin_at_18_minutes'],'required_margin':1.5,'control_sha':pins['control']['sha'],
    'control_tree':pins['control']['tree'],'request_sha256':pins['request']['sha256'],
    'different_object_precursor':'tests/control-321c266-precursor/FINAL-VALIDATE.json; not final package acceptance',
    'concrete_reason_for_final_object_change':'tests/fallback-empty-object-precursor.json; present {} terminal must not be normalized into absence'}
pins.update(status=status,offline_validation=validation,final_validate_receipt_sha256=D((OUT/'FINAL-VALIDATE.json').read_bytes()))
put('PINS.json',pins)
finding=read('AUTHOR-FINDING.json');finding['final_validate']={'status':'PASS','control':final['control_sha'],'receipt_sha256':D((OUT/'FINAL-VALIDATE.json').read_bytes())}
put('AUTHOR-FINDING.json',finding)
margin=read('MARGIN-PROPOSAL.json');margin.update(status='UNSELECTED_PRECURSOR_PROPOSAL_NOT_NEEDED_BY_FINAL_MEASURED_PASS',
    final_actual_control=final['control_sha'],final_elapsed_seconds=final['elapsed_seconds'],final_margin_at_18_minutes=final['margin_at_18_minutes'],
    final_gate_pass=True,proposal_selected=False,current_actual_validate_minutes=18)
put('MARGIN-PROPOSAL.json',margin)
put('VALIDATION.json',{'status':'OFFLINE_STATIC_AND_SYNTHETIC_SERVICE_PASS','actual_final_validate':final,'test_summary':summary,
    'targeted_tests_before_final':['tests/targeted-01.json','tests/targeted-03.json','tests/targeted-04.json','tests/targeted-05.json'],
    'failed_targeted_retained':'tests/targeted-02.json plus exact stdout/stderr; relative -c import path corrected and ordinary no-replacement guard made explicit',
    'preflight':'PREFLIGHT.json and all four MAP files bound to final exact request; no preflight lexer/gate cache',
    'patch_tree_replays':6,'shallow_depths':{'control':7,'source':5,'tool':2},'selected_source_assertions':21,'selected_source_covers':21,
    'native_property_counts':'UNKNOWN','caps_unchanged':True,'native_compile_proof_cost_fit':'NOT_RUN','proof_credit':'NONE',
    'prior_candidate_validate':precursor,'prior_candidate_retired_for_concrete_finding':True,
    'final_candidate_validate_repeated':False,'full_suite_repeated_after_pass_without_concrete_finding':False})
precursors=read('PRECURSORS.json');precursors.update(actual_final_validate_runs_so_far=1,total_full_workflow_validate_executions=2,retired_object_full_validate_runs=1,
    same_final_object_full_validate_runs=1,different_object_precursor=precursor,
    concrete_finding='tests/fallback-empty-object-precursor.json; observed {} rewrite on321; isolated sibling4059 with regression, no source/tool/cap change',
    precursor_files='tests/control-321c266-precursor/ retains original PINS/request/workflow/provenance/scripts and exact stdout/stderr/receipt on true321 object',
    final_preflight='PREFLIGHT.json final c6abee request; tests/preflight-01.json and precursor/PREFLIGHT.json retain earlier true requests',
    helper_files='implement.py/configure.py are construction precursors; do not rerun sealed construction/sealing/final validation helpers')
put('PRECURSORS.json',precursors)
historical=Path('/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s4/s4p-1-r1/PINS.json')
old=json.loads(historical.read_text())
put('HISTORY-PRESERVATION.json',{'baseline_source':'985062ebad90cee1e2846b1648cd6a8624d146f6','baseline_control':'2db5d2c08804036d283cb36450647cd584ee9e10',
    'historical_s4p1_validate':old['offline_validation'],'historical_validate_is_s4p2_evidence':False,
    'baseline_packet_path':str(historical.parent),'baseline_packet_pinfile_sha256':D(historical.read_bytes()),
    'new_source_preservation':'SOURCE-PRESERVATION.json; only new module and exact append after old verify.rs prefix',
    'new_control_preservation':'CONTROL-PRESERVATION.json; old profiles/fixtures/gates/tests/runtime/lexer cache exact; shared schema dispatch audited',
    'author_precursor_321':{'sha':precursor['control_sha'],'tree':precursor['control_tree'],'result':precursor,'retired_for_concrete_empty_object_finding':True},
    'old_exact_admissions':'Historical exact run/ID scope preserved; no emitter/common-location/Cell-transfer rule',
    'historical_records_relabelled':False,'download_verified_changed':False,'ledger_accounting_changed':False})
selected=read('TEST-LIST.json')['expanded_new_tests']
gates=read('IMPLEMENTATION-GATES.json')
put('GATE-COVERAGE.json',{'status':'AUTHOR_VALIDATED_PENDING_INDEPENDENT_EXACT_REVIEW','implementation_gates':gates['required'],
    'evidence':{'new_exact_profile_request_terminal_portable_seal':['CI-REQUEST.json','WORKFLOW.yml','TEST-LIST.json','FINAL-VALIDATE.stderr'],
    'roles_SAT_modes_native_counts':['ROLE-ORACLE-COVER.json','ROOTS.json','tests/targeted-01.json','FINAL-VALIDATE.stderr'],
    'source_model_cfg_ordinary_PFC_contract_stack_lexical':['PREFLIGHT.json','MAP-ORDINARY.json','MAP-CFG_PFC.json','MAP-CONTRACT_STACKS.json','MAP-LEXICAL.json'],
    'protected_identity_service_error_cleanup_serial_caps':['tests/targeted-03.json','tests/targeted-04.json','FINAL-VALIDATE.stderr','RUNNER-DISPATCH.patch'],
    'empty_object_fallback_no_normalization':['tests/fallback-empty-object-precursor.json','tests/targeted-05.json','CONTROL-FALLBACK-REPAIR.patch','FINAL-VALIDATE.stderr'],
    'old_profiles_history_and_unchanged_caps':['CONTROL-PRESERVATION.json','HISTORY-PRESERVATION.json','RESOURCE.json','FINAL-VALIDATE.stdout']},
    'new_tests_actually_selected':selected,'old_suites_actually_selected':summary['test_counts'],
    'source_role_sites_only':{'assertions':21,'covers':21,'native_counts':'UNKNOWN'},'native_compile_proof_credit':'NOT_RUN_NONE'})
timing=[]
for path in sorted((OUT/'tests').glob('targeted-*.json')):
    item=json.loads(path.read_text());stderr=path.with_suffix('.stderr').read_text();m=re.search(r'Ran (\d+) tests? in ([0-9.]+)s',stderr)
    timing.append({'file':str(path.relative_to(OUT)),'request_sha256':item['request_sha256'],'exit_code':item['exit_code'],
        'wall_seconds':item['elapsed_seconds'],'unittest_tests':int(m[1]) if m else 'UNKNOWN','unittest_seconds':float(m[2]) if m else 'UNKNOWN'})
put('TEST-TIMING.json',{'targeted':timing,'retired_object':precursor,'actual_final':validation,'native_cost_or_fit':'NOT_RUN'})
checkpoint=read('CHECKPOINT.json');checkpoint.update(status=status,source=pins['source'],control=pins['control'],tool=pins['tool'],
    request_sha256=pins['request']['sha256'],final_validate=validation,
    claims=[{'claim':'Four new actual network roots, exact fixed controls then n2,n3,n4,N0..1; Original/null, full34 independentu8/base1, 4SUCCESS roles each, SAT6/6/6/3 source sites.',
        'assurance':'EXACT_STATIC_SOURCE_REQUEST_BINDING_AND_SYNTHETIC_SERVICE_PASS_NOT_NATIVE','evidence':['ROOTS.json','ROLE-ORACLE-COVER.json','SOURCE-PRESERVATION.json']},
        {'claim':'Actual source preflight gates and full64 cfg power set include all32 legacy contexts and8 active nonempty normalizations.',
        'assurance':'OBSERVED_STATIC_GATE_AND_CI_SELECTED_REGRESSIONS','evidence':['PREFLIGHT.json','MAP-CONTRACT_STACKS.json','FINAL-VALIDATE.stderr']},
        {'claim':'Exact committed final workflow Validate executed once; all344 selected tests pass at unchanged18min and>=1.5 margin.',
        'assurance':'OBSERVED_OFFLINE_EXECUTION_NOT_CI_NATIVE_OR_PROOF','evidence':['FINAL-VALIDATE.json','FINAL-VALIDATE.stdout','FINAL-VALIDATE.stderr']}],
    open=read('OPEN-OBLIGATIONS.json')['open'],blocker=None,new_proof_obligations_closed=0,new_qualified_leaves=0,proof_credit='NONE',
    runtime='SolHigh/FastOFF; no subagents/model changes',GO='NOT_GRANTED',publication_CI_native='NOT_PERFORMED',accounting='TRACKING_ONLY_NO_WRITES',
    completion_reason='Authorized offline implementation, targeted fixes/tests, exact final validation and sealed review package complete; independent review/GO remain separate',
    next='Root fullpin/manifest check, SAME W14 independent exact-package review; only exact APPROVE/no blockers -> root GO request for one bounded8root attempt by user coordinator')
put('CHECKPOINT.json',checkpoint)
(OUT/'CURRENT-TASK.md').write_text('# W13 S4P2 offline implementation\n\nRuntime: Codex. Task '+pins['task']+'. SolHigh/FastOFF preserved; no subagents/model changes.\n\nResult: '+status+'.\nSource '+pins['source']['sha']+'; control '+pins['control']['sha']+'; stock tool '+pins['tool']['sha']+'.\nActual final Validate once:344 tests PASS, '+format(final['elapsed_seconds'],'.6f')+'s, margin '+format(final['margin_at_18_minutes'],'.9f')+'x at unchanged18min.\nOne separate321 precursor retained on its true object; retired for the reproduced present-empty-terminal normalization defect and replaced by a narrowly repaired sibling.\nNo native/CI/push/ledger/summary/model changes; proof credit NONE. Exact package W14 review and root GO remain pending.\n')
pintext=f'''Source `{pins['source']['sha']}`, tree `{pins['source']['tree']}`, sole parent `{pins['source']['sole_parent']}`; repo `{pins['source']['repo']}`.

Control `{pins['control']['sha']}`, tree `{pins['control']['tree']}`, sole parent `{pins['control']['sole_parent']}`; repo `{pins['control']['repo']}`.

Stock tool `{pins['tool']['sha']}`, tree `{pins['tool']['tree']}`, sole parent `{pins['tool']['sole_parent']}`; repo `{pins['tool']['repo']}`.

Request SHA256 `{pins['request']['sha256']}`; workflow SHA256 `{pins['request']['workflow_sha256']}`; complete payload137 with request self-hash excluded.
'''
(OUT/'HANDOFF.md').write_text(f'''# S4P2 author READY for root and W14 exact-package review

{status}. Task `{pins['task']}` (root corrected notification typo), plan `{pins['plan']}`, plan review `{pins['plan_review']}`. Plan approval is not executable approval. Full g0 commit is returned externally; the containing commit binds MANIFEST.json without a self-hash loop.

{pintext}
The exact8 Original/null roots are fixed checker_order_corrupt, checker_count_corrupt, sort13_weak, s4p_cell_count_corrupt, then the new actual network n2/n3/n4/N0..1 roots. ROOTS.json maps all PLAN designIDs to actual selectors. Four SUCCESS source assertion roles per positive bind literal labels, predicates, file/line/hash and exact domain. Source cover counts in execution order are6/6/6/3, total21; N0..1 alone records the four impossible pair/max-hi roles as structural N/A on exact profile/domain/source/hash. Every actually declared native cover must still be SATISFIED. Source assertions total21; actual native property counts/status/SAT/unwind remain UNKNOWN/NOT_RUN.

All34 backing bytes are independent fullu8, allocation34/base1 and active [1,1+n). The unchanged oracle checks full-value sorting/counts, every outside frame element and arbitrary outside canary. Actual small_sort_network N0/1 returns immediately; N2/3/4 executes insertion prefix1 with1/2/3 tail insertions. No sort4/swap replacement, stubs, assumed summary or provider edge is enabled. Old negative source bytes/labels, fixed descending sort13weak and Cell [0,1]->[0,0] checker corruption remain exact. Production kernel/contracts/models and all old harness bytes are preserved; old verify.rs is an exact prefix followed only by the guarded module append.

The new request/profile/terminal/seal schemas are versioned. Public local and upload-only readers check the trusted actual-string terminal schema and genuine selected_roots int8 before common collection, including STOPPED0/partial and all valid prefixes0..8. New writer/worker/terminal/sealed replay rows explicitly require Original/null. Protected E0/pre/worker BEFORE/AFTER/controller post, FAILED-state drift/read-errors, verified interrupted recovery, source/tool/request/cfg/binary/export/namespace identity, process ownership/reap/cleanup, original errors/exits/errno, serial continuation, durable atomic seals, strictU/guards/location checks and bounded B01/B02 stay in force. No emitter investigation11 or historical admission applies a new rule here.

Actual source preflight passed on the final exact request, preserving all four complete maps. The power set derives from actual6 keys:64 unique contexts, all32 legacy contexts,32 sorting-enabled and8 complete ACTIVE normalization contexts. Nonempty wrapper/direct comparisons remain meaningful. Pure full-text lexer caching is restricted to Validate, returns fresh lists, restores on exceptions and caches no runtime reads/gates/reports/test results. Old profiles/gates/tests/fixtures/runtime/lexer cache files remain byte-identical; only the small shared dispatch/explicit-target additions are diff-audited.

Exact final committed-control workflow Validate ran ONCE:344 tests PASS (legacy136, S3=56, S32=35, bridge40, S4P1=38, S4P2=39), exit0, {final['elapsed_seconds']:.6f}s, margin {final['margin_at_18_minutes']:.9f}x at unchanged18min. Targeted tests ran first; the39 new regressions are actually selected by s4p2_validate.py. All6 complete patch trees replay exactly, and shallow control7/source5/tool2 identities pass. FINAL-VALIDATE.* retains exact command/stdout/stderr/exit/timing/identities.

During author audit the present-empty-object fallback was reproduced on candidate321c266: it rewrote {{}} as a missing terminal. That true-object candidate and Validate output remain under tests/control-321c266-precursor/. Final4059c900 is a separate sole9e14 sibling, with only the explicit file-presence check, distinguishing regression and two payload digests changed. No result is relabelled to another object. Historical S4P1 305PASS/550.637729s remains its original2db evidence. The earlier failed targeted02, all subsequent targeted receipts and original preflight request bindings are preserved.

Caps are unchanged: child600 includescompile180,slot720,controller180,cleanup240,campaign6900,outer7500,step7560,phase8100,setup1800/job180min; local6GiB sampled ownedPGID,outer12GiB ownedcensus,reserve2GiB, Ceff=min(6,12,A-2); outputs16MiB/1MiB/export8MiB/artifact256MiB. Eight-slot6180 is arithmetic, not measured fit or cgroup/kernel peak. No volume STOP, cap escalation, auto retry/enable/cron/dispatch.

Workflow .github/workflows/ch8-s2.yml on uninit-ci/ch8-s4p-* uses the final request/Validate/campaign. Historical artifact prefix ch8-s3-2-${{{{ github.run_id }}}}-${{{{ github.run_attempt }}}} is intentional; portable format is retained. No native/CI/push/publication/accounting/ledger/subagents/model changes occurred. SolHigh/FastOFF preserved. Proof credit NONE; all largerN/general/type/init/ownership/panic/provider/caller/MIR/B1/B2/native fit obligations remain OPEN.

Root verifies this exact committed packet and issues TASK-CH8-S4P2-EXACT-PACKAGE-REVIEW-W14.md to SAME W14 with full pins/HANDOFF/manifest. Only exact independent APPROVE/no blockers permits a root GO request for ONE bounded8root attempt. User coordinator separately publishes exact source, creates a NONSKIP SAME-TREE control sibling with sole9e14, and binds actual head/ref/run/accounting. Those future identities are UNKNOWN; no executable approval or GO is claimed here.
''')
(OUT/'REVIEW14-REQUEST.md').write_text(f'''# SAME W14 exact S4P2 package review request

Prepared for root issuance after its fullpin/manifest check; not independently reviewed or GO.

Task `{pins['task']}` and TASK-CH8-S4P2-EXACT-PACKAGE-REVIEW-W14.md. Review the exact containing g0 commit returned externally, this MANIFEST.json, HANDOFF.md and PINS.json. Own NEW kani3300/ch8-s4/s4p-2-review/ only; no reviewer source edits, native/CI/push/ledger/modelchanges/subagents.

{pintext}
Audit all ROLE-SAT-CONTRACT/IMPLEMENTATION-GATES, source preservation, exact8 ordered Original/null rows, full-u8V34/base1 oracle/roles/SAT3/6/6/6 and exact N01-only structural N/A, actual insertion path and no enabled summary/provider. Inspect all four prebuild maps, complete64 cfg contexts retaining legacy32, actual new module/lexical/import/alias/local-callable checks, protected lifecycle/worker/FAILED drift/read-errors/cleanup and both public reader routes with true string schema/int8/modes/prefixes/seals. Check the isolated empty-object fallback repair and preserved true-object precursor; no historical/emitter exception transfer.

Actual final Validate once on this exact committed final control:344 PASS, {final['elapsed_seconds']:.6f}s, {final['margin_at_18_minutes']:.9f}x at18min. All6 patch trees and shallow7/5/2 pass. Keep source-site inventory distinct from native UNKNOWN/NOT_RUN and independent proof NONE. Check unchanged caps and future eligibility; no repeat full suite absent concrete concern. Commit exact REVIEW/FINDINGS/provenance/manifest/HANDOFF, return fullSHA to root. Plan e287 approval does not approve this executable package.
''')
(OUT/'READY.md').write_text(f'''# READY for root and W14 exact-package review

{status}.

Final control `{pins['control']['sha']}`; source `{pins['source']['sha']}`; stock tool `{pins['tool']['sha']}`.

Actual final Validate ONCE:344 PASS, {final['elapsed_seconds']:.6f}s, margin {final['margin_at_18_minutes']:.9f}x at18min. Six exact patch-tree replays and shallow7/5/2 PASS. See HANDOFF/PINS/MANIFEST/REVIEW14-REQUEST. Independent exact-package approval and GO pending; native/CI/proof/fit NOT_RUN, credit NONE.
''')
files={}
for path in sorted(OUT.rglob('*')):
    if not path.is_file() or path.name=='MANIFEST.json':continue
    assert not path.is_symlink();raw=path.read_bytes();files[str(path.relative_to(OUT))]={'bytes':len(raw),'sha256':D(raw)}
put('MANIFEST.json',{'schema':'ch8-s4p-2-immutable-packet-manifest-v1','status':'READY','files':files,
    'excluded':['MANIFEST.json'],'identity':'Containing g0 commit binds manifest; actual fullSHA returned externally'})
print(json.dumps({'status':status,'files':len(files),'tests':validation['tests'],'elapsed_seconds':final['elapsed_seconds'],'margin':final['margin_at_18_minutes']}),flush=True)
