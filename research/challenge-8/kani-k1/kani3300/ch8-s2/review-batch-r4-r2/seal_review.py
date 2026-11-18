#!/usr/bin/env python3
"""Seal the completed local combined review; never edits candidate inputs."""
import hashlib
import json
from pathlib import Path

H = Path(__file__).resolve().parent
def load(name): return json.loads((H/name).read_text())
def write(name, value): (H/name).write_text(json.dumps(value, indent=2)+'\n')
i = load('INPUTS.json')
c = load('CHECKS.json')
t = load('TARGETED-TESTS.json')
assert c['status'] == 'PASS' and t['exit_code'] == 0 and t['count'] == 3
p = i['pins']
report = {
    'schema': 'ch8-s2-r4-r2-final-combined-delta-review-v1',
    'task_id': i['task_id'], 'issued': i['issued'],
    'verdict': 'APPROVE', 'package_commit': i['package_commit'],
    'source': p['source'], 'control': p['control'], 'tool': p['tool'],
    'request_sha256': p['control']['request_sha256'],
    'workflow_sha256': p['control']['workflow_sha256'],
    'scope': 'Final six-path combined delta relative to frozen0e8 only; inherit unchanged f5/e783/ccb6 facts; no compiler or broad source audit',
    'changed_paths': c['checks']['six_path_delta'],
    'dependencies': {k:v['commit'] for k,v in i['dependencies'].items()},
    'original_findings': [
        {'id':'R14-01', 'status':'CLOSED_INHERITED', 'basis':'Unchanged exact bd62 source and f5/e783 review dependencies; no native compilation claim'},
        {'id':'R14-02', 'status':'CLOSED_INHERITED', 'basis':'Unchanged ordinary/CFG/contract gates, source and all request policy fields'},
        {'id':'R14-03', 'status':'CLOSED', 'basis':'ccb6 exact gate-only APPROVE/CLOSED; approved lexical extractor and new regression module bytes inherited exactly; actual explicit final Validate command includes the module'}
    ],
    'new_findings': [],
    'assessment': [
        'Workflow is structurally identical to frozen0e8 except Validate timeout1->10min and appended reviewed test module; no other cap or action changed',
        'check_package AST outside check_yaml is identical, including build/control/fallback/types. New exact cap/order/list assertions strengthen integration checks; sum177->186 is a maxima accounting change only',
        'Request delta is exactly entry_g0/control_reference/ci_changed_paths/ci_payload_sha256. Full-stock, parent and frozen-delta inventories match all paths and endpoint blobs/hashes, including deleted stock paths; payload hashes cover every present changed file except self-request',
        'Source delta is empty; source fixtures/maps and all protected runner/collector/packer/diagnostic/decoder/oracle bytes match inherited candidate; no algorithm/model/domain/contracts/oracles delta',
        'Every timeout-audit step matches the final workflow command/action/inputs/cap. Keep source60s on recorded host13.638509s; other setup caps stay unchanged with duration UNKNOWN. No evidence warrants speculative increases',
        'Aggregate clock begins inside Begin setup budget after job initialization; subsequent actual setup reduces min(900,int(1800-elapsed)) build allowance. Expired remainder rejects before execute; end>1800 rejects with receipt. Setup maxima3120s and all-step maxima186min grant no additional elapsed budget',
        'Pinned final Validate records107 tests PASS380.011575s; check-source PASS13.638509s. Exact commands, monotonic arithmetic, source/control/tool/request/workflow identities and transcript hashes match; module loader inventories107 tests, including9 gate tests. These are recorded host measurements, not reviewer remeasurements',
        'Earlier timeout-only precursor remains separate with no final acceptance credit. OldCI remains coordinator-supplied PREBUILD_VALIDATION_TIMEOUT, partial tests not suitePASS; historical packets/GO/ledger remain unchanged'
    ],
    'validation': {
        'input_package': '65_FILES_64_HASHES_COMMITTED_MATCH',
        'dependency_manifests': 'ALL_COMMITTED_BYTES_MATCH',
        'full_inventories': c['checks']['inventories'],
        'patch_replays': '6_EXACT_TREE_MATCH',
        'checkout_depths': {'control':7,'source':5,'tool':2},
        'workflow_mutations_rejected': c['checks']['workflow']['rejected_mutations'],
        'reviewer_targeted_tests': t,
        'inherited_final_tests': {'count':107,'exit_code':0,'elapsed_seconds':380.011575071,'scope':'RECORDED_EXACT_FINAL_COMMITTED_OBJECT; NOT_RERUN'},
        'inherited_check_source': {'exit_code':0,'elapsed_seconds':13.63850858,'scope':'RECORDED_EXACT_FINAL_COMMITTED_OBJECT; NOT_RERUN'},
        'evidence': ['INPUTS.json','CHECKS.json','TARGETED-TESTS.json','TARGETED-TESTS.txt','review_checks.py']
    },
    'invariants': {'aggregate_setup_seconds':1800,'job_minutes':180,'backend_seconds':600,'compile_seconds':900,'root_sum_seconds':6600,'group_seconds':7500,'internal_seconds':8100,'proof_step_seconds':7560,'rss_GiB':12,'headroom_GiB':2,'serial':1,'roots':11,'covers':20,'exact_negatives':6,'DIAGNOSTIC_ASSUMED':'PRESERVED','copy_identity_limits':'PRESERVED','B01_B02':'PRESERVED'},
    'historical_CI': {'run':'44328364855/1','assurance':'OWNER_COORDINATOR_SUPPLIED_NOT_REAUDITED','classification':'PREBUILD_VALIDATION_TIMEOUT','step4':'Native FAILURE72s; partial tests not suitePASS','later_stages':'SKIPPED','roots':0,'charge':0,'accounting':'REFERENCE_ONLY_NO_EDITS'},
    'limits': ['Offline static/synthetic combined integration review only', 'Finite lexical extractor scope and method/macro/type/MIR limits inherited from ccb6; no syntax-completeness or compiler-success claim', 'Future GitHub timing/timeout outcome and actual CI setup remainder UNKNOWN', 'Native compile/causal repair NOT_RUN; actual R3 failing unit UNKNOWN', 'No independent B1/B2 proof credit or closed proof obligations', 'Approval is not CI GO; spent one-run exception does not transfer'],
    'native_compile':'NOT_RUN','causal_repair':'NOT_RUN','actual_r3_unit':'UNKNOWN','proof_credit':'NONE','closed_proof_obligations':0,
    'external_actions': {k:0 for k in ('compiler','verifier','full_runner','CI','push','PR','issue','ledger','reservation','budget','source_edits','subagents')},
    'settings':'CURRENT_PRESERVED; FAST_OFF_PER_OWNER; NO_SETTINGS_TOGGLES',
    'next':'Separate root GO-request for these exact r4-r2 pins only; coordinator alone authorizes GO/dispatch/accounting',
    'review_commit':'Containing commit; full SHA in READY; self-reference excluded'
}
write('REPORT.json', report)
(H/'REPORT.md').write_text('''# W14 — final combined r4-r2 delta review

**APPROVE.** No new localized findings. Owner18:19 issued combined review; explicit `/new` overrides task reuse-context. Review is limited to the final six-path delta; unchanged f5/e783/ccb6 facts are inherited through verified committed dependencies.

Exact package `3cdec7455c52d93903a31e005c7e42204fa502e1` has65 files/64 manifest hashes matching committed bytes. Control `d33a0900da19d865f20ccaa76e1ee27065c5a671`, tree `fe7c05829a6374da2cb11a3b3c993aaf9082a7c7`, sole parent `9e14e033f9ee31522b571c127609dcdff76d230b`. Source `bd62e54df1b4749154790aa3db3cc7978f547f75` / tree `dc2e7a7f258719a05c65bbb9b1e2c7f1e8271ac8` unchanged and clean. Tool `0aac16ef62da9e9d5645782d458593e5d78143ba` unchanged.

Request SHA256 `d7f4561810178e9eb553d83a04de343f2512aff18bbca0dbd4864472712d4d73`; workflow SHA256 `b70c7dff34fe5ae12985dc0ba44f2791cca3bb288e774416f1eb405ab90b090b`.

Validate1→10min is the only timeout change. Workflow otherwise changes only by appending `test_r1403_lexical.py`. Gate-only review `ccb6a60731866bcc8fc6dd6e6cbdf4c2a9fd4653` APPROVE/CLOSED matches exact gate package/control/patch and both inherited files. R14-01/R14-02 remain CLOSED by unchanged dependencies; R14-03 remains CLOSED with integration now checked.

`check_yaml` enforces the exact cap/order/two-command list and updated maxima sum186. All other check_package AST, build/control/fallback and scalar types are identical. Request changes are confined to entry/reference/inventory/hash rebinding. All six inventories match complete path sets and both endpoint hashes, including deleted stock workflows; all payload/source/map/fixture hashes match. Six patch replays produce exact trees; shallow checkout7/5/2 checks pass. Protected runner/diagnostic/collector/packer/oracle/B01/B02 bytes and11roots/20covers/6 negatives remain unchanged.

Each of12 timeout-audit entries matches actual final command/action/inputs/cap. Recorded check-source13.638509s supports keeping60s on this host; future GitHub time is UNKNOWN. Other setup timeouts remain unchanged without speculative increases. Setup aggregate1800s begins at the timestamp in Begin setup budget; build gets at most min(900,int(1800-elapsed)). Earlier setup consumes this allowance, expired starts reject without execute, and end>1800 rejects with receipt. Step maxima186min and setup maxima3120s are not elapsed allowances. Job180min and backend600/compile900/rootsum6600/group7500/internal8100/proofstep7560/RSS12+2GiB/serial1 remain.

Recorded final-object Validate PASS107 tests/380.011575s and check-source PASS13.638509s have matching commands, monotonic arithmetic, exact source/control/tool/request/workflow provenance and transcript hashes. The actual explicit module list loads107 tests, including9 approved gate tests. Earlier timeout-only precursor remains separate without final credit. No full suite or source timing was rerun. Reviewer ran only3 changed workflow/cap/order/mocked aggregate tests (PASS), plus6 rejecting workflow mutations and static checks. The build executor was mocked; no compiler was invoked.

Old run44328364855/1 remains coordinator-supplied PREBUILD_VALIDATION_TIMEOUT: native step4 FAILURE72s, partial tests not suitePASS, later stages SKIPPED,0roots, charge0 reference only. Future CI duration/timeout outcome and remaining setup time are UNKNOWN. Native compile and causal repair NOT_RUN; actual R3 failing unit UNKNOWN. DIAGNOSTIC_ASSUMED, copy-identity and finite lexical-gate limits remain; no B1/B2 proof credit, no closed proof obligations.

Evidence: INPUTS.json (all exact dependency/file hashes), CHECKS.json (inventories/replays/inheritance/mutations/timing-record validation), TARGETED-TESTS.json/txt. Reports and helpers write only this review directory; original packets remain immutable. Fast OFF/settings preserved, no subagents. No compiler/verifier/full runner/CI/push/PR/issue/source/ledger/budget changes.

Approval is not CI GO. Previous one-run exception is spent. Next: separate root GO-request for these exact r4-r2 pins; coordinator alone GO/dispatch/accounting.
''')
(H/'HANDOFF.md').write_text('''READY — APPROVE, final combined r4-r2 delta only.

Package3cdec7455c52d93903a31e005c7e42204fa502e1; control d33a0900da19d865f20ccaa76e1ee27065c5a671/tree fe7c05829a6374da2cb11a3b3c993aaf9082a7c7/sole parent9e14e033f9ee31522b571c127609dcdff76d230b. Source bd62e54df1b4749154790aa3db3cc7978f547f75 unchanged.

Request d7f4561810178e9eb553d83a04de343f2512aff18bbca0dbd4864472712d4d73; workflow b70c7dff34fe5ae12985dc0ba44f2791cca3bb288e774416f1eb405ab90b090b. Exact gate inheritance ccb6 APPROVE/CLOSED and final module wiring checked. No new findings to original13.

Targeted changed tests3 PASS;6 workflow mutations rejected; inventories, manifests, payload/maps,6 exact patch replays and shallow7/5/2 PASS. Inherited107 final tests PASS380.011575s and check-source PASS13.638509s validated as pinned records; no rerun. Full details and immutable dependencies: REPORT.json and INPUTS.json.

Next is separate root GO-request r4-r2 only. This review grants no CI/dispatch/accounting authorization and transfers no spent exception. Future CI timing UNKNOWN; compile/causal repair NOT_RUN; actual R3 unit UNKNOWN; no proof credit. Existing packets/inputs/settings remain unchanged; no external actions.

Full review SHA is supplied in READY after own-path [skip ci] commit; omitted from packet to avoid circular self-hash.
''')
manifest = ''.join(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n'
                   for path in sorted(H.iterdir()) if path.is_file() and path.name != 'MANIFEST.sha256')
(H/'MANIFEST.sha256').write_text(manifest)
print('APPROVE sealed:', len(manifest.splitlines())+1, 'files;', len(manifest.splitlines()), 'hashes')
