"""Seal only after exact final Validate PASS; no native/CI/accounting actions."""
from pathlib import Path
import hashlib,json,shutil,subprocess
MAIN=Path('/root/verify-rust-std-kani3300-g0')
BASE=MAIN/'research/challenge-8/kani-k1'
OUT=BASE/'kani3300/ch8-s4/s4p-1-r1'
OLD=BASE/'kani3300/ch8-s4/s4p-1'
D=lambda b:hashlib.sha256(b).hexdigest()
def read(name):return json.loads((OUT/name).read_text())
def put(name,data):(OUT/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
final=read('FINAL-VALIDATE.json');pins=read('PINS.json');request=read('CI-REQUEST.json')
assert final['exit_code']==0 and not final['timed_out'] and final['execution_count']==1
assert final['clean_after'] and final['margin_at_18_minutes']>=1.5 and final['limit_seconds']==1080
assert final['control_sha']==pins['control']['sha'] and final['control_tree']==pins['control']['tree']
assert final['request_sha256']==pins['request']['sha256']
summary=json.loads((OUT/'FINAL-VALIDATE.stdout').read_text().splitlines()[-1])
assert summary['success'] and summary['errors']==summary['failures']==0
assert summary['test_counts']=={'legacy':136,'s3':56,'s32':35,'bridge1':40,'s4p':38}
status='READY_FOR_ROOT_CHECK_AND_SAME14_DELTA_NOT_GO'
validation={'actual_final_validate_execution_count':1,'tests':sum(summary['test_counts'].values()),'test_counts':summary['test_counts'],
    'exit_code':final['exit_code'],'elapsed_seconds':final['elapsed_seconds'],'internal_elapsed_seconds':summary['elapsed_seconds'],
    'margin_at_18_minutes':final['margin_at_18_minutes'],'required_margin':1.5,
    'control_sha':pins['control']['sha'],'control_tree':pins['control']['tree'],'request_sha256':pins['request']['sha256']}
pins.update(status=status,offline_validation=validation,
    cfg_power_set={'independent_keys':5,'unique_projections':32,'sorting_enabled':16,'ACTIVE_guard_contexts':4},
    terminal_schema_required='ch8-s4p-1-campaign-v1',
    finding_status={'R14-01':'AUTHOR_FIXED_TARGETED_AND_EXACT_FINAL_VALIDATE_PASS_PENDING_SAME14',
        'R14-02':'AUTHOR_FIXED_TARGETED_AND_EXACT_FINAL_VALIDATE_PASS_PENDING_SAME14'},
    final_validate_receipt_sha256=D((OUT/'FINAL-VALIDATE.json').read_bytes()),
    old_final_validate_reference='HISTORY-PRESERVATION.json; historical E941 302 PASS only')
put('PINS.json',pins)
put('FINDING-CLOSURES.json',{'schema':'ch8-s4p1-gate-repair-author-findings-v1',
    'review':pins['independent_review'],'review_verdict_preserved':'REQUEST_CHANGES',
    'independent_closure':'PENDING_SAME14','control':pins['control'],'request_sha256':pins['request']['sha256'],
    'findings':[
        {'id':'R14-01','author_disposition':'FIXED_PENDING_INDEPENDENT_DELTA_REVIEW',
            'change':'Power set derives from actual key count via 1 << len(keys); no source/hash/normalization/required-path weakening.',
            'evidence':['CONTROL-REPAIR.patch','MAP-CONTRACT_STACKS.json','PREFLIGHT.json','TEST-LIST.json','tests/targeted-02.json','FINAL-VALIDATE.stderr'],
            'observed':{'unique_cfg_subsets':32,'sorting_enabled':16,'complete_ACTIVE_guard_contexts':4},
            'regression':'Actual emitted gate/report plus observed old/new declarations and nonempty wrapper-to-direct normalization comparisons in each ACTIVE context.'},
        {'id':'R14-02','author_disposition':'FIXED_PENDING_INDEPENDENT_DELTA_REVIEW',
            'change':'Exact trusted literal terminal schema, real str equality, checked before count and legacy_collect on local and compact-upload readers.',
            'evidence':['CONTROL-REPAIR.patch','tests/TERMINAL-SCHEMA-MATRIX.json','tests/review-reproducer.json','TEST-LIST.json','FINAL-VALIDATE.stderr'],
            'observed':{'original24_malformed_rejections':24,'total_malformed_rejections':78,'genuine_acceptances':6,'malformed_legacy_collection_calls':0},
            'variants':['missing','null','old bridge','int123','bool true','bool false','float','list','object','empty','unknown','old S3','old S32'],
            'states':['FULL8','STOPPED0','PARTIAL0'],'routes':['LOCAL','UPLOAD_ONLY'],
            'preserved':'Genuine prefixes0..8, selected int8, old7/8/9 schemas/counts and legacy source gates included in exact final Validate.'}],
    'new_proof_credit':'NONE','GO':'NOT_AUTHORIZED'})
put('VALIDATION.json',{'status':'OFFLINE_STATIC_AND_SERVICE_PASS','actual_final_validate':final,'test_summary':summary,
    'targeted_before_final':read('tests/targeted-02.json'),'source_preflight':'PREFLIGHT.json and four actual MAP reports',
    'patch_trees_replayed':6,'shallow_depths':{'control':7,'source':5,'tool':2},'selected_literal_assertion_sites':21,
    'selected_literal_cover_sites':30,'native_property_counts':'UNKNOWN','all_caps_unchanged':True,
    'native_compile_proof_cost_fit':'NOT_RUN','proof_credit':'NONE',
    'precursor_failures':'HISTORY-PRESERVATION.json, PRECURSORS.json, tests/packet-precursor-01.* and expected review-reproducer nonzero retained',
    'full_validate_repeated_after_pass':False})
precursors=read('PRECURSORS.json');precursors['packet_helper_failure']='tests/packet-precursor-01.json/.py; gitlink treated as blob, fixed in helper only; no candidate or Validate change'
put('PRECURSORS.json',precursors)
shutil.copyfile('/tmp/s4p1_r1_packet.py',OUT/'prepare_packet.py')
shutil.copyfile('/tmp/s4p1_r1_seal.py',OUT/'seal_packet.py')
checkpoint=read('CHECKPOINT.json');checkpoint.update(status=status,request_sha256=pins['request']['sha256'],
    final_validate=validation,frozen_author=pins['frozen_author'],frozen_review=pins['independent_review'],
    claims=[{'claim':'R14-01 repair: real gate emits all32 unique subsets with16 sorting and4 ACTIVE contexts; nonempty actual normalization comparisons pass.',
        'assurance':'STATIC_SOURCE_GATE_AND_CI_SELECTED_REGRESSION_PASS','evidence':['MAP-CONTRACT_STACKS.json','tests/targeted-02.json','FINAL-VALIDATE.stderr']},
        {'claim':'R14-02 repair: all original24 and78 total malformed terminal schemas reject on both routes before collection;6 genuine controls accept.',
        'assurance':'AUTHENTIC_SYNTHETIC_WRITER_PUBLIC_READER_SERVICE_TEST_PASS','evidence':['tests/TERMINAL-SCHEMA-MATRIX.json','FINAL-VALIDATE.stderr']},
        {'claim':'Exact final committed control workflow Validate executed once,305 tests PASS,unchanged18min with>=1.5 margin.',
        'assurance':'OBSERVED_LOCAL_TEST_EXECUTION_NOT_CI_OR_NATIVE','evidence':['FINAL-VALIDATE.json','FINAL-VALIDATE.stdout','FINAL-VALIDATE.stderr']}],
    all_other_source_tool_scope_caps_and_control_entries_preserved=True,
    independent14='PENDING_SAME14_DELTA; author fixes are not independent closures',GO='NOT_AUTHORIZED',
    next='Root verifies committed READY exact fullpins/manifest; issue existing TASK-CH8-S4P1-GATE-DELTA-W14.md at989 to SAME CURRENT14 with this exact g0, HANDOFF and pins. Only independent both CLOSED/exact APPROVE/no blockers -> root recheck and GO request.',
    publication_CI_native_raw_GCS='NOT_PERFORMED',accounting='TRACKING_ONLY_NO_WRITES',
    rejected_approaches=['No source or tool changes','No cap/domain/mode/role/cover/cache changes','No malformed terminal normalization or terminal-derived expected schema','No child of E941','No subagents or old26d/1ff/1079 continuation'])
put('CHECKPOINT.json',checkpoint)
(OUT/'CURRENT-TASK.md').write_text('# W13 S4P1 gate repair\n\nExact repair task '+pins['repair_task']+'.\nHigh/FastOFF; no subagents/model changes.\n\nResult: '+status+'.\nR14-01/02 author fixes validated; SAME14 independent delta closure remains pending.\nExact final Validate once:305 tests PASS, '+format(final['elapsed_seconds'],'.3f')+'s, '+format(final['margin_at_18_minutes'],'.6f')+'x at unchanged18min.\nSource/tool/scope/caps and historical author590/E941/review4856/302PASS are unchanged.\nNo CI/native/publication/accounting/GO. See PINS/HANDOFF/DELTA-REVIEW14-REQUEST.\n')
pintext=f'''- Repair task: `{pins['repair_task']}`; original task `{pins['implementation_task']}`; frozen plan `{pins['frozen_plan']}`.
- Frozen author: `{pins['frozen_author']}`; frozen review: `{pins['independent_review']}`.
- Source: `{pins['source']['sha']}`, tree `{pins['source']['tree']}`, sole parent `{pins['source']['sole_parent']}`; repo `{pins['source']['repo']}`.
- Control: `{pins['control']['sha']}`, tree `{pins['control']['tree']}`, sole parent `{pins['control']['sole_parent']}`; repo `{pins['control']['repo']}`.
- Stock tool: `{pins['tool']['sha']}`, tree `{pins['tool']['tree']}`, parent `{pins['tool']['parents'][0]}`; repo `{pins['tool']['repo']}`.
- Request SHA256: `{pins['request']['sha256']}`; workflow SHA256: `{pins['request']['workflow_sha256']}`; payload118, request self-hash excluded.
- Validate script SHA256: `{final['script_sha256']}`; final receipt SHA256: `{pins['final_validate_receipt_sha256']}`.
- Final stdout SHA256: `{final['stdout']['sha256']}`; stderr SHA256: `{final['stderr']['sha256']}`.
'''
(OUT/'HANDOFF.md').write_text(f'''# S4P1 gate repair READY for root and SAME14 delta

{status}. Both findings have author fixes and passing regressions; independent closure and GO are pending.

{pintext}
R14-01 derives enumeration from the five actual keys. Real report has32 unique subsets,16 sorting-enabled and4 complete ACTIVE guard contexts. CI-selected regression observes the real baseline/projected declarations and requires meaningful wrapper-to-direct contract comparisons in all4 contexts. Exact normalization, source hashes and required-path gates remain.

R14-02 requires the trusted literal `ch8-s4p-1-campaign-v1` as an actual string before legacy collection, for LOCAL and UPLOAD_ONLY. Authentic real writer/finalizer/public collector/compact packer tests reject78 malformed cases, including all original24, with zero malformed collection calls; all6 genuine state/route controls accept. Missing/null/nonstring/old/empty/unknown cases are distinguished. Genuine prefixes0..8/int8 and all legacy7/8/9 controls remain selected and pass.

The exact workflow Validate command ran ONCE on the clean committed control:305 tests PASS (legacy136/S3=56/S32=35/bridge40/S4P=38), exit0, {final['elapsed_seconds']:.6f}s, {final['margin_at_18_minutes']:.9f}x margin at unchanged18min. Targeted regressions ran first. No fullsuite was repeated after PASS. See FINAL-VALIDATE.* and TEST-LIST.json.

All6 complete patch trees replay exactly; shallow control7/source5/tool2 pass. The control is a sibling with sole9e14, not a child of E941. Only request payload inventory/hashes, the two gate boundaries, Validate selection and one test module differ from E941. Source985/tool0aac, eight Original/null rows, domains/full34u8/base1/length blocks, roles/covers/caps/workflow/shared runtime/lexer cache remain exact. HISTORY-PRESERVATION retains author590/E941/old302PASS/review4856 and all historical failures. One packet-helper gitlink failure and the expected first-schema rejection from the disposable sealed reproducer are preserved separately.

Root checks this exact committed packet, then issues `TASK-CH8-S4P1-GATE-DELTA-W14.md` at `{pins['repair_task']}` to SAME current14, with full g0 reported externally. New review output: `kani3300/ch8-s4/s4p-1-review-r1/`. Both independent CLOSED + exact APPROVE + no blockers precede root recheck and GO-request only. No independent review or GO is claimed here.

The user coordinator separately publishes exact source985, creates a NONSKIP SAME-TREE SIBLING of this final control with sole9e14, and dispatches/accounts only after authorization. Future head/ref/run UNKNOWN. No CI, compiler/rustfmt/verifier/native runner, publication/push, raw/full/GCS, ledger/accounting, subagent or model change occurred. New proof credit NONE; native compile/proof/exhaustion/cost/fit and all general/provider/init/type/caller/MIR/B1/B2 obligations remain OPEN.

`MANIFEST.sha256` covers all packet files except itself; g0 and manifest digest are reported externally to avoid a self-hash loop.
''')
(OUT/'DELTA-REVIEW14-REQUEST.md').write_text(f'''# Prepared request for SAME14 delta review — not issued

Root must first check the committed READY packet, manifest and exact pins below. Use existing task `TASK-CH8-S4P1-GATE-DELTA-W14.md` at `{pins['repair_task']}` in the existing SAME CURRENT14 context; no subagent or old-thread revival. Output only new immutable `kani3300/ch8-s4/s4p-1-review-r1/`.

{pintext}
Independently close R14-01 and R14-02 from frozen review4856. Check real full32/16/4 gate/map and nonempty normalization regression; authentic original24/expanded78 malformed rejects and6 genuine controls, no observation collection before schema admission, genuine prefixes0..8/int8 and old7/8/9. Inspect exactly five-file delta in CONTROL-REPAIR.patch, complete preservation, payload/request binding, exact final305 PASS once with {final['margin_at_18_minutes']:.9f}x margin, six patch trees and shallow7/5/2.

The source/tool/caps/profile/runtime invariance supports inheritance of unaffected fullreview4856 conclusions only. Do not repeat full Validate without a concrete concern. Preserve original review REQUEST_CHANGES and all historical evidence. Author fixes are not independent CLOSED. Both independently CLOSED/exact APPROVE/no blockers -> root recheck -> GO-request only; publication/run/ledger remain user coordinator duties. Actual future head/ref/run UNKNOWN; no automatic CI/native/raw/GCS/accounting.
''')
(OUT/'READY.md').write_text(f'''# READY — root check and SAME14 delta required

{status}

Control `{pins['control']['sha']}` / tree `{pins['control']['tree']}` / sole `{pins['control']['sole_parent']}`.
Source `{pins['source']['sha']}` and tool `{pins['tool']['sha']}` unchanged.
Request `{pins['request']['sha256']}`; workflow `{pins['request']['workflow_sha256']}`.
Final exact Validate ONCE:305 PASS, exit0, {final['elapsed_seconds']:.6f}s, margin {final['margin_at_18_minutes']:.9f}x at18min.
R14-01 actual32/16/4; R14-02 original24+expanded78 reject before collection,6 genuine accept.
See HANDOFF/PINS/DELTA-REVIEW14-REQUEST. Independent closure and GO pending. No native/proof/CI/publication/accounting; credit NONE.
''')
# Seal after all generated documents/scripts have their final bytes.
files=sorted(p for p in OUT.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256')
(OUT/'MANIFEST.sha256').write_text(''.join(D(path.read_bytes())+'  '+str(path.relative_to(OUT))+'\n' for path in files))
print(json.dumps({'status':status,'files':len(files)+1,'hashes':len(files),'manifest_sha256':D((OUT/'MANIFEST.sha256').read_bytes()),'final_validate':validation}),flush=True)
