#!/usr/bin/env python3
"""Bounded static plan review. Reads committed Git blobs only; no native tools."""
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
BASE = 'research/challenge-8/kani-k1/'
TASK = '1b4280d0cc0625bcb35aa108ffd602a6a20db1fc'
PLAN = '7253272c427eb9b564c79350ef73b231fa124298'
PRIOR = 'e43156f54416491b8688db0cb28325ccf8238d1d'
INTAKE = '842984040e87b8b8594653634b72df7d800ca198'
REVIEW = '3c7bd65cf0bb758cb82dc56ef71a8b8e23efd5c0'
ADMISSION = '9bb6e2b7a18e338f532ec817f8acfd7515fc2fc9'
PP = BASE + 'kani3300/ch8-s4/network-after-s4p1-plan-r1/'
OLD = BASE + 'kani3300/ch8-s4/network-after-s4p1-plan/'
CHECKS = []

def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])

def blob(rev, path):
    return git('show', rev + ':' + path)

def get(rev, path):
    return json.loads(blob(rev, path))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def need(ok, label):
    if not ok:
        raise AssertionError(label)
    CHECKS.append(label)

def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def manifest(rev, prefix, name):
    raw = blob(rev, prefix + name)
    files = git('ls-tree', '-r', '--name-only', rev, prefix).decode().splitlines()
    if name.endswith('.sha256'):
        entries = {}
        for line in raw.decode().splitlines():
            digest, path = line.split(maxsplit=1)
            entries[path.lstrip('*')] = {'sha256': digest}
    else:
        entries = json.loads(raw)['files']
    need(set(files) == {prefix + n for n in entries} | {prefix + name}, rev[:8] + ' exact manifest coverage')
    for path, info in entries.items():
        need(not Path(path).is_absolute() and '..' not in Path(path).parts, 'safe manifest path ' + path)
        data = blob(rev, prefix + path)
        need(sha(data) == info['sha256'] and ('bytes' not in info or len(data) == info['bytes']), 'committed manifest hash ' + rev[:8] + '/' + path)
    return {'commit': rev, 'path': prefix + name, 'manifest_sha256': sha(raw), 'files': len(files), 'hashes': len(entries), 'status': 'MATCH'}

def main():
    manifests = [manifest(PLAN, PP, 'MANIFEST.sha256'), manifest(PRIOR, OLD, 'MANIFEST.sha256'),
                 manifest(REVIEW, BASE + 'kani3300/ch8-s4/run-44481580554-review-w14/', 'MANIFEST.json'),
                 manifest(ADMISSION, BASE + 'kani3300/ch8-s4/admission-s4p1-r1-fallback/', 'MANIFEST.json')]
    need(manifests[0]['files'] == 10 and manifests[0]['hashes'] == 9, 'final plan 10 files / 9 hashes')
    need(manifests[1]['files'] == 11 and manifests[1]['hashes'] == 10, 'inherited plan 11 files / 10 hashes')
    final_inputs = get(PLAN, PP + 'INPUTS.json')
    old_inputs = get(PRIOR, OLD + 'INPUTS.json')
    dependencies = []
    for label, entries, expected in [('final', final_inputs['dependencies'], 23), ('old', old_inputs['dependencies'], 8)]:
        need(len(entries) == expected, label + ' exact dependency cardinality')
        for dep in entries:
            data = blob(dep['commit'], dep['path'])
            need(sha(data) == dep['sha256'] and ('bytes' not in dep or len(data) == dep['bytes']), label + ' dependency ' + dep['commit'][:8] + ':' + dep['path'])
            dependencies.append({**dep, 'independent_status': 'MATCH'})
    old_paths = git('ls-tree', '-r', '--name-only', PRIOR, OLD).decode().splitlines()
    need(all(blob(PRIOR, n) == blob(PLAN, n) for n in old_paths), 'all 11 sealed old plan files unchanged at final plan')
    citations = get(PRIOR, OLD + 'SOURCE-CITATIONS.json')
    need(len(citations['items']) == 12 and sum(len(i['ranges']) for i in citations['items']) == 26, '12 source citations / 26 ranges')
    source_checks = []
    for citation in citations['items']:
        data = blob(citation['commit'], citation['path'])
        need(citation['commit'] == old_inputs['pins']['source']['sha'] and sha(data) == citation['file_sha256'], citation['id'] + ' exact source commit/file SHA')
        need(git('rev-parse', citation['commit'] + ':' + citation['path']).decode().strip() == citation['git_blob'], citation['id'] + ' exact Git blob')
        for bounds in citation['ranges']:
            excerpt = b''.join(data.splitlines(keepends=True)[bounds['start']-1:bounds['end']])
            need(sha(excerpt) == bounds['sha256'], citation['id'] + ' exact range ' + str(bounds['start']) + ':' + str(bounds['end']))
        source_checks.append({**citation, 'independent_status': 'MATCH', 'assurance': 'STATIC_PINNED_SOURCE_ONLY; no compiler/MIR/native proof'})
    evidence = get(PLAN, PP + 'EVIDENCE-BINDING.json')
    reviewed = get(REVIEW, BASE + 'kani3300/ch8-s4/run-44481580554-review-w14/RESULT.json')
    admitted = get(ADMISSION, BASE + 'kani3300/ch8-s4/admission-s4p1-r1-fallback/ADMISSION.json')
    need(final_inputs['review_commit'] == REVIEW and final_inputs['admission_commit'] == ADMISSION and final_inputs['intake_commit'] == INTAKE, 'actual review/admission/intake bound')
    need(evidence['review']['limits_verbatim'] == reviewed['limits'] and evidence['review']['disposition'] == reviewed['disposition'] and evidence['review']['blocking_findings_count'] == 0, 'exact actual review limits/disposition, zero blockers')
    for projection, actual in zip(evidence['admission']['cases'], admitted['cases']):
        need(projection['id'] == actual['id'] and projection['domain'] == actual['reviewed_intake_record_unchanged']['domain'] and projection['decision'] == actual['decision'], projection['id'] + ' exact bounded external admission')
        need(projection['exact_location_packet_canonical_sha256'] == sha(canonical(actual['exact_location_packet'])), projection['id'] + ' full admitted metadata packet fingerprint')
    need(len(evidence['admission']['cases']) == 2 and evidence['new_network_native_evidence'] is False and evidence['new_proof_credit'] == 'NONE', 'two external Cell cases; no network evidence/credit transfer')
    recommendation = get(PLAN, PP + 'RECOMMENDATION.json')
    partitions = get(PRIOR, OLD + 'PARTITIONS.json')
    need(recommendation['recommended'] == partitions['recommended'] and recommendation['coverage'] == partitions['coverage'], 'partition geometry/domain/oracles unchanged')
    need(recommendation['role_obligations'] == partitions['role_obligations'], 'role prerequisites inherited explicitly; no silent weakening')
    length_sets = [r['lengths'] for r in recommendation['recommended']]
    need(length_sets == [[0, 1], [2], [3], [4]] and sorted(sum(length_sets, [])) == list(range(5)) and len(sum(length_sets, [])) == len(set(sum(length_sets, []))), 'disjoint exact full-u8 union 0..4')
    need(all(r['mode'] == 'Original' and r['geometry'] == 'V34/base1' and r['summary_edges'] == [] for r in recommendation['recommended']), 'all partitions Original V34/base1 no summaries')
    controls = ['checker_order_corrupt', 'checker_count_corrupt', 'sort13_weak', 's4p_cell_count_corrupt']
    need(recommendation['controls'] == controls, 'all four original negative controls retained')
    dag = get(PRIOR, OLD + 'CALLER-DAG.json')
    for row in dag['rows']:
        n = row['n']
        need(row['T'] == 'u8' and row['F'] == 'KeyLess<u8>' and row['base'] == 1 and row['unwind'] == 36, 'n' + str(n) + ' concrete T/F/base/unwind')
        calls = row['insert_calls']
        need([c['prefix'] for c in calls] == list(range(1, n)), 'n' + str(n) + ' insertion prefixes exactly 1..n-1')
        for call in calls:
            p = call['prefix']
            need(call['begin_absolute'] == 1 and call['tail_absolute'] == p+1 and call['tail_relative'] == p and call['span'] == [1, p+2] and call['binding'].startswith('OPEN'), 'n' + str(n) + ' prefix' + str(p) + ' exact span/frame and OPEN binding')
    need(dag['proposed_summary_edges_enabled'] == [] and all(e['summary_edge_status'] == e['caller_binding'] == e['current_frozen_source_provider_proof'] == 'OPEN' and e['use_in_recommended_campaign'] == 'NONE; execute actual callee body' for e in dag['summary_edges']), 'all three provider/caller edges OPEN and disabled')
    resource = get(PRIOR, OLD + 'RESOURCE.json')
    need(resource['actual'] == evidence['network_cost_unchanged'], 'network costs retained byte-equivalent projection')
    scenario = resource['scenarios'][0]
    need(scenario['serial_slots'] == 8 and scenario['campaign_arithmetic_envelope_seconds'] == 8*720+180+240 == 6180 and scenario['remaining_campaign_arithmetic_seconds'] == 6900-6180 == 720, 'eight-row envelope arithmetic 6180 plus720 margin; not fit')
    need(resource['scenarios'][1]['campaign_arithmetic_envelope_seconds'] == 9*720+180+240 == 6900, 'five-singleton alternative nine-slot arithmetic no spare margin')
    cost = get(INTAKE, BASE + 'kani3300/ch8-s4/run-44481580554/COST.json')
    for actual, historical in zip(resource['actual'], cost['rows'][6:]):
        need(actual['wholechild_seconds'] == historical['execution']['elapsed_seconds'] and actual['compile_elapsed_upper_bound_seconds'] == historical['compile_elapsed_upper_bound_seconds'] and actual['sampled_rss_peak_kib'] == historical['execution']['rss_peak_kib'] and actual['cutoff_cause'] == historical['cutoff_cause'] == 'CHILD600_WALL_INCLUDING_COMPILE', actual['id'] + ' exact supplied wall-censored facts')
    # Static witness assignments establish predicate consistency only. They do
    # not execute a sort, predict CBMC fit, or prove the actual native path SAT.
    role_rows = []
    assertions = ['ACTIVE_CONCRETE_MODEL', 'SORTED_FULL_VALUE_COUNT', 'FULL_OUTSIDE_FRAME', 'ARBITRARY_OUTSIDE_CANARY']
    for r in recommendation['recommended']:
        lengths = r['lengths']
        degenerate = lengths == [0, 1]
        covers = [f'N{n:02}' for n in lengths]
        if not degenerate:
            covers += ['UNSORTED', 'DUPLICATE', 'NONCONSTANT', 'MAX_DESCENDING']
        covers += ['USEFUL_RETURN']
        need(len(covers) == (3 if degenerate else 6), r['id'] + ' precise feasible cover set')
        assignments = []
        for n in lengths:
            need(1+n <= 34 and 0 < 1 and 33 >= 1+n, r['id'] + ' nonempty outside complement/canary')
            assignments.append({'role': f'N{n:02}', 'n': n, 'active_input': [0]*n, 'candidate_output': [0]*n})
        if not degenerate:
            n = lengths[0]
            descending = list(range(n-1, -1, -1))
            output = list(reversed(descending))
            need(n >= 2 and descending[0] > descending[-1] and output[0] < output[-1] and collections.Counter(descending) == collections.Counter(output), r['id'] + ' nontrivial source-predicate witness consistency')
            assignments += [{'role': role, 'n': n, 'active_input': descending, 'candidate_output': output} for role in ['UNSORTED', 'NONCONSTANT', 'MAX_DESCENDING']]
            assignments.append({'role': 'DUPLICATE', 'n': n, 'active_input': [0]*n, 'candidate_output': [0]*n})
        assignments.append({'role': 'USEFUL_RETURN', 'n': lengths[0], 'active_input': [0]*lengths[0], 'candidate_output': [0]*lengths[0]})
        need({a['role'] for a in assignments} == set(covers), r['id'] + ' every expected cover has a feasible static assignment')
        role_rows.append({'design_id': r['id'], 'lengths': lengths, 'mode': 'Original', 'target': None, 'type': 'u8', 'comparator': 'KeyLess<u8>', 'allocation': 34, 'base': 1, 'unwind': 36, 'assertion_roles': {a: 'SUCCESS' for a in assertions}, 'cover_roles': {c: 'SATISFIED' for c in covers}, 'cover_count': len(covers), 'structurally_not_applicable_roles': ['UNSORTED', 'DUPLICATE', 'NONCONSTANT', 'MAX_DESCENDING_AT_OLD_HI_2_OR_4'] if degenerate else [], 'static_assignments': assignments, 'source_active_site_count': 4, 'native_property_count': 'UNKNOWN_UNTIL_SAME_INVOCATION_EXPORT'})
    need(sum(x['cover_count'] for x in role_rows) == 21 and 4*4+5 == 21, 'new proposal source21 assertions/21covers, distinct from native counts')
    write('INPUTS.json', {'schema': 'network-plan-w14-review-inputs-v1', 'authority': 'User11:59 plan review then original13 implementation; root exact task issued', 'task_commit': TASK, 'task_path': BASE + 'TASK-CH8-S4-NETWORK-PLAN-REVIEW-W14.md', 'task_sha256': sha(blob(TASK, BASE + 'TASK-CH8-S4-NETWORK-PLAN-REVIEW-W14.md')), 'root_inputs': {'commit': TASK, 'path': BASE + 'kani3300/ch8-s4/network-plan-review-emitter-inputs/INPUTS.json', 'sha256': sha(blob(TASK, BASE + 'kani3300/ch8-s4/network-plan-review-emitter-inputs/INPUTS.json'))}, 'plan_commit': PLAN, 'plan_HANDOFF_sha256': sha(blob(PLAN, PP + 'HANDOFF.md')), 'plan_manifest_sha256': manifests[0]['manifest_sha256'], 'prior_plan_commit': PRIOR, 'intake_commit': INTAKE, 'intake_review_commit': REVIEW, 'admission_commit': ADMISSION, 'source': citations['source'], 'tool': citations['tool'], 'owned_path': str(HERE.relative_to(REPO)), 'settings': 'Current SolHigh/FastOFF preserved without settings/model actions; no subagents'})
    write('DEPENDENCIES.json', {'status': 'MATCH', 'manifests': manifests, 'final_dependencies': 23, 'old_dependencies': 8, 'items': dependencies, 'sealed_old_plan_unchanged': True, 'review_replay_repeated': False, 'acquisition': False})
    write('SOURCE-CHECKS.json', {'schema': 'network-plan-w14-source-checks-v1', 'status': 'PASS', 'citations': source_checks, 'citations_count': 12, 'ranges_count': 26, 'DAG': dag, 'semantic_assessment': 'Source-selected N0/1 return before scratch; N2..4 no_merge=true, region=n<9, presorted_len1, insertion offset1, absolute tails2..n. No swap/sort4 substitution, summary/caller/provider edges remain OPEN. Direct roots do not prove trait dispatch.', 'assurance': 'STATIC_ONLY; sourceunwind36 does not prove native exhaustion; no compiler/export/MIR/verification executed'})
    write('ROLE-SAT-CONTRACT.json', {'schema': 'network-plan-w14-offline-implementation-role-contract-v1', 'status': 'REQUIRED_ACCEPTANCE_CONTRACT_FOR_FUTURE_PACKAGE', 'rows': role_rows, 'execution_order': controls + [recommendation['recommended'][i]['id'] for i in [1,2,3,0]], 'positive_source_assertion_sites': 16, 'negative_source_assertion_sites': 5, 'total_source_assertion_sites': 21, 'total_source_cover_sites': 21, 'native_counts': 'UNKNOWN; never equate source sites with native property count', 'exact_label_binding': 'Implementation must bind each listed semantic role to a unique exact literal label/source file/line/hash in the new request; source_check must reject missing/extra/wrong role/domain/status/label. Do not predict native property ordinals; obtain same-invocation exported IDs.', 'zero_one_resolution': 'Pair predicates include n>=2 and old max-descending n==2/4; all are false on{0,1}. Omit those four cover sites only for the new explicitly exact degenerate root and record structural N/A in the new profile. This is not acceptance of UNSAT native cover records. Keep four assertions even when trivially true. Nontrivial N2/N3/N4 each retain all four witness kinds, descending at that exact singleton length.', 'native_cover_gate': 'Every actually declared and exported cover must be SATISFIED. Any UNSATISFIABLE/UNREACHABLE/unknown/missing/wrong-type cover continues to reject. No global N/A or UNSAT exception, no future-run location transfer.', 'feasibility_assurance': 'Static candidate assignments consistent with predicates/full multiplicities only; actual native SAT/normal return remains UNKNOWN until actual same-invocation results.'})
    regressions = [
        {'boundary': 'new exact profile/request/terminal/portable seal', 'required': 'Use an explicitly versioned exact profile/request and compatible terminal/seal routing; bind to new request-derived schema constants, never terminal-derived schema. Old S4P1 profile/fixtures remain unchanged. All new planned selected_roots exactly genuine int8 in complete/partial/STOPPED/prefix0 states.'},
        {'boundary': 'role/SAT inventory', 'required': 'Per-root exact assertions/covers3/6/6/6 and positive order n2,n3,n4,N01. Structural N/A metadata only for exactN01; all declared covers SAT. Reject omission/duplication/extra label/wrong literal/file/line/class/status/domain/type/cfg/producer count. Nontrivial witness removal is a failing regression.'},
        {'boundary': 'source/model/cfg gates', 'required': 'Bind new harness IDs/cfg/module registrations to new source SHA and source hashes. Keep actual algorithms/contracts/oracle/model and full-u8 V34/base1/frame/canary unchanged. Preserve ordinary/cfg-PFC/contract-stack all32subset/nonempty projection/lexical reader gates and B01/B02. No stub_verified/assumed summary/provider edges.'},
        {'boundary': 'runner service error paths and portable replay', 'required': 'Existing Cloud preflight plus targeted synthetic success/error/timeout/partial/missing/null/wrong-type/explicitNOT_RUN/source-stage-target mismatch; local/upload-only equality and durable seal mutation rejection. Preserve original exits/exceptions/errno, interruptedUNKNOWN versus laterNOT_RUN, no malformed terminal normalization. Complete full required CI validation matrix on final new package, not in this plan review.'},
        {'boundary': 'protected identity and safe serial execution', 'required': 'E0/pre/workerBEFORE/AFTER/controllerpost source/tool/request/cfg/binary/export/namespaces/Original-null remain strict in all states. Observed mismatch/read-error globally STOP; only genuine missing-AFTER interrupted recovery with verified shutdown/cleanup and protected post, never erasing observed errors. Retain all ownership/reap/survivor and serial continuation controls.'},
        {'boundary': 'qualification/history/location', 'required': 'Producer U-REJECT_ALL/proposalDISABLED/unsupported-guard/error/unknown/location/count checks unchanged. Retain every guard status including SUCCESS and each U for source-local review. Old five merge/fallback exact cases and optional old sort4 case apply only original runs. Neither admission9bb nor same lib.rs:0:0 permits a rule for new roots.'},
        {'boundary': 'resources/future dispatch', 'required': 'Child600 includes compile180; slot720/controller180/cleanup240/campaign6900/outer7500/step7560/phase8100/setup1800/job180min and output16MiB/1MiB/8MiB/256MiB unchanged. Ceff=min(6,12,A-2)GiB, local6 sampledPGID/outer12 owned/reserve2. Exact final nested runtime/setup/deadline/reserve eligibility needs independent package review before root/coordinatorGO+ledger. 6180 arithmetic is not measured fit.'}
    ]
    write('IMPLEMENTATION-GATES.json', {'schema': 'network-plan-w14-implementation-gates-v1', 'status': 'MANDATORY_BEFORE_EXECUTABLE_PACKAGE_ACCEPTANCE', 'root_may_issue_offline_implementation_after_committed_review': True, 'worker': 'Original CURRENT13', 'required': regressions, 'acceptance_contract': 'ROLE-SAT-CONTRACT.json', 'proof_credit': 'NONE', 'execution_GO': 'NOT_GRANTED', 'review_scope': 'This review sets concrete acceptance criteria for the explicitly deferred role map. It does not apply a role/schema change or approve uncommitted implementation.'})
    limits = ['Network native inventory/roles/SAT/U/guards/location/unwind and fit remain UNKNOWN; source-predicate feasibility is not actual native SAT.', 'Only direct full-u8 u8/KeyLess Original N0..4 initializedV34/base1 helper cases; no generic trait/caller/init/provider/universal summary/ownership/panic/MIR/B1B2/fullN16N32 credit.', 'All insertion p1/p2/p3 provider/caller edges OPEN and disabled; no swap/sort4 substitution or Cell fallback/DIAG_INIT_OPEN merge transfer.', 'Mandatory per-root exact role/SAT map and schema/profile/reader/gate regressions in ROLE-SAT-CONTRACT/IMPLEMENTATION-GATES before future executable package approval.', 'All old strict gates/history/exact-case admissions/caps retained; no CI, new admission, parser/policy rule, accounting, publication or resource escalation by this review.']
    findings = {'schema': 'network-plan-w14-findings-v1', 'disposition': 'APPROVE', 'blocking_findings': [], 'nonblocking_findings': [], 'repair_required': False, 'implementation_acceptance_contract': 'ROLE-SAT-CONTRACT.json', 'required_future_package_gates': 'IMPLEMENTATION-GATES.json', 'scope': 'Approval of the bounded plan for root-issued offline implementation only; no executable package/CI approval.', 'limits': limits, 'if_later_localized_findings': 'Original13 immutable planrepair plus SAME14delta; no reviewer source/plan edits'}
    write('FINDINGS.json', findings)
    write('RESULT.json', {'schema': 'network-plan-w14-review-result-v1', 'status': 'READY', 'disposition': 'APPROVE', 'reviewed_plan': PLAN, 'task_commit': TASK, 'blocking_findings_count': 0, 'source_citations': 12, 'source_ranges': 26, 'final_dependencies': 23, 'old_dependencies': 8, 'root_next': 'Verify actual committed review/HANDOFF/manifest, then issue exact offline implementation task to original13 with acceptance contracts. Review exact newsource/control/harness package before any separate root/coordinatorGO+ledger/CI.', 'implementation_permitted': 'ROOT_ISSUED_OFFLINE_ONLY_AFTER_COMMITTED_REVIEW_CHECK', 'execution_GO': False, 'new_qualification': False, 'proof_obligations_closed': 0, 'proof_credit': 'NONE', 'limits': limits})
    write('COST-REVIEW.json', {'status': 'SOURCE_REPORTED_COST_MATCH', 'actual': resource['actual'], 'caps': cost['caps'], 'setup_seconds': 1800, 'job_minutes': 180, 'eight_row_arithmetic_seconds': 6180, 'remaining_campaign_arithmetic_seconds': 720, 'five_singleton_alternative_arithmetic_seconds': 6900, 'fit': 'UNKNOWN; future exact package nested envelope/deadline/setup/reserve check mandatory', 'memory_increase': 'NOT_SELECTED; no observed RSS trigger or evidence more memory cures wall timeout', 'subphase_uncensored_time_peak': 'UNKNOWN'})
    write('PROVENANCE.json', {'task_commit': TASK, 'plan_commit': PLAN, 'inherited_plan_commit': PRIOR, 'intake_commit': INTAKE, 'review_commit': REVIEW, 'admission_commit': ADMISSION, 'authority': 'User11:59 + exact root-issued task; fresh14 CURRENT continuation', 'method': 'Main-reviewer static semantic inspection plus committed-manifest/dependency/source-range checks. No duplicate intake/review replay, artifact acquisition, raw/ZIP/GCS/native/compiler/exporter/fullValidate/CI.', 'writes': str(HERE.relative_to(REPO)), 'source_policy_ledger_edits': False, 'subagents': 0, 'settings_actions': [], 'native_property_ids_counts_SAT': 'UNKNOWN; no predicted native counts or ordinals', 'role_map_assurance': 'Explicit required acceptance contract for existing plan prerequisites; no active schema/profile/role/policy implementation'})
    write('VALIDATION.json', {'status': 'PASS', 'checks_count': len(CHECKS), 'checks': CHECKS, 'scope': 'Targeted static plan only; no host/native/fullValidate tests or replays', 'manifests': manifests})
    (HERE / 'REVIEW.md').write_text(f'''# Independent W14 network plan review

**APPROVE** exact final plan `{PLAN}`, inheriting sealed `{PRIOR}`. Zero findings. This approval permits root to issue the user-authorized offline implementation task to original13. The exact new source/control/harness package still needs independent review and separate root/coordinatorGO+ledger before CI.

Final10files/9hashes, inherited11files/10hashes, final23 dependencies and old8 dependencies MATCH. All12 source citations/26 exact ranges independently match pinned source985; all prior plan files are preserved at finalSHA. Review3c7 and subsequent admission9bb are correctly separate and bound. The admitted two Original Cell cases retain their exact finite context; historical NOT_APPLIED records are not rewritten and confer no network/provider/generic/init/MIR credit.

The source path is correct. N0/1 return before scratch. N2..4 set no_merge, use region length<9 and presorted_len1, then insertion_sort_shift_left offset1 and insert_tail prefix1/2/3 at absolute begin1/tails2/3/4. No swap/sort4/sort9/merge replacement occurs. The p1 report is bounded SOURCE_REPORTED and is not an enabled provider; every current-source provider/caller/induction binding stays OPEN. The full-byte pure comparator, owned fullcount snapshot/post and all34 outside checks/canary remain; no type/domain/oracle/initialization weakening is approved. Sourceunwind36 is not native exhaustion proof; direct helper roots do not prove trait dispatch.

The exact disjoint union{{0,1}}|{{2}}|{{3}}|{{4}}=0..4 at initializedV34/base1 is sound as a coverage partition. Preserve all34 independent fullu8 values and Original/nulltarget/no summaries. Controls first in original order, then n2,n3,n4,N01. Native network evidence remains UNKNOWN_CENSORED.

The plan expressly defers exact role registration until implementation. This review resolves its acceptance boundary without treating unimplemented roles as evidence. Every positive root retains four SUCCESS assertion roles: active concrete model, sorted/fullcount, complete outside frame and arbitrary outside canary. N01 declares exactly three SAT covers(N0,N1,usefulreturn). N2/N3/N4 each declare exactly six SAT covers(exact length,unsorted,duplicate,nonconstant,descending at that exact singleton,usefulreturn). Their counts are3/6/6/6; total21 source covers and21 source assertion sites including five original negative assertion sites. Native expanded counts remain UNKNOWN. ROLE-SAT-CONTRACT.json supplies exact semantic sets and static witness assignments; the future package must bind literal labels/files/lines/hashes and observed native IDs.

Old pair predicates explicitly require n>=2, and old descending predicates require n==2/4, so they are infeasible onN01. Represent only those degenerate sites as structural N/A in the exact new root profile, with no exported site to require SAT; keep every nontrivial witness in each n2/n3/n4 root. Do not add general UNSAT/N/A acceptance. Every declared/exported cover must remain SATISFIED; UNSAT/UNREACHABLE/unknown/missing continues to reject. Static satisfying assignments establish predicate consistency, not native reachability or solver completion. Future exact package review enforces this contract before executable approval.

IMPLEMENTATION-GATES.json names the required new exact schema/profile/request/terminal/seal routing; request-derived genuine selectedint8 across complete/partial/STOPPED/prefix0; source/model/cfg-PFC/ordinary/contract-stack/lexical gates; all-state protected identity and B01/B02; reader local/upload equality and malformed schema/count rejection; runner success/error/timeout/partial/missing/null/wrongtype/NOT_RUN/source-stage-target regressions plus existing preflight/final matrix. Existing strict U/guard/location/status gates remain unchanged. These are implementation acceptance requirements, not checks purportedly run on nonexistent code.

Eight slots at720 plus180controller+240cleanup yield6180s,720s arithmetic margin in6900. Five singleton positives plusfourcontrols give6900 with no spare margin under that screen. Neither establishes fit: actual nested child600inclcompile180/slot720/outer7500/step7560/phase8100/setup1800/job180min/deadline/reserve must be checked on the future package. Existing local6/outer12/reserve2 and output limits stay fixed. Actual old network601.428/601.401s and compileupper48.195/45.976s with sampledRSS3515064/3516320KiB are wall-censored; exact backend phase and uncensored time/peak remain UNKNOWN. No memory cure or speedup is inferred.

All prior alternatives remain unselected: no swap/sort4 substitution, assumed DAG, V6 geometry lifting, five-singleton campaign, child900 or memory increase. N5..32, other geometry/init/T/F, generic caller/ownership/panic/provider/universal summaries/MIR/B1B2/fullN16N32 remain OPEN. No general location rule or transfer of the old five exact merge/fallback cases(optional historical sort4 is separate). No acquisition/native/fullValidate/CI/source/policy/ledger/model/settings/delegation action was taken. Localized later findings go to original13 immutable repair and SAME14delta.
''')
    (HERE / 'HANDOFF.md').write_text(f'''# READY — independent W14 network plan review

Use the full40-character containing Git commit returned with this HANDOFF; MANIFEST.json hashes every other own file and containing Git commit binds the manifest.

**APPROVE**, zero findings, exact finalplan `{PLAN}` / HANDOFF `{sha(blob(PLAN, PP + 'HANDOFF.md'))}`. Task/inputs exact `{TASK}`. Sealed priorplan `{PRIOR}` preserved; source985/tool0aac/intake842/review3c7/admission9bb bound. Final10files9hashes/23deps plus old11files10hashes/8deps/12sourcecitations26ranges MATCH. No duplicate intake/acquisition/replay/native/fullValidate.

Recommend exact fullu8 Original/null{{0,1}},{{2}},{{3}},{{4}} initializedV34/base1, actual insertion path prefix1/2/3, four old fixednegative controls then n2/n3/n4/N01, no enabled summaries. ROLE-SAT-CONTRACT.json concretizes the implementation acceptance sets: four SUCCESS roles each; declared SAT covers3/6/6/6, nativecountsUNKNOWN; degenerate impossible pair/max-hi sites are structural N/A only in exactN01, never a general UNSAT waiver. Every nontrivial witness remains. All existing model/fullcount/frame/canary/checks/strictness retained.

Root rechecks actual committed READY/manifest, then may issue exact user-authorized offline implementation to original13 with ROLE-SAT-CONTRACT and IMPLEMENTATION-GATES mandatory. New exactsource/control/harness package independent review plus final envelope eligibility/root+coordinatorGO+ledger remain separate. This is not CI/executionGO or new qualification/admission.

Network remains UNKNOWN; old Cell admissions do not prove u8network. All provider/caller/MIR edges OPEN. Capped costs601.428/601.401 child600includingcompileupper48.195/45.976; sampledRSS below6GiB is not a memory-cure argument. Eightrow6180s is screening arithmetic, not fit; caps unchanged. General init/provider/ownership/panic/universal/generic/MIR/B1B2/fullN16N32 OPEN. CommonemitterUNKNOWN; no general/future location rule.

Read REVIEW/RESULT/FINDINGS, ROLE-SAT-CONTRACT, IMPLEMENTATION-GATES, SOURCE-CHECKS, DEPENDENCIES, COST-REVIEW and VALIDATION. Static validation `{len(CHECKS)}` checks PASS. No source/control/policy/ledger edits, native/acquisition/raw/ZIP/GCS/fullValidate/CI/push/accounting/subagents/model/settings actions. Current high/FastOFF preserved without settings actions. Findings later: original13 immutableplanrepair+SAME14delta. Authorized plan review complete.
''')
    (HERE / 'READY.md').write_text('READY: APPROVE; zero findings.\nExact containing fullSHA returned with HANDOFF.\nRoot-issued offline implementation only; future exact-package review and root/coordinatorGO+ledger remain mandatory. No CI authorization.\n')
    seal = {'schema': 'network-plan-w14-immutable-review-manifest-v1', 'status': 'READY', 'files': {}, 'excluded': ['MANIFEST.json'], 'identity': 'Containing Git commit binds manifest; return exact fullSHA with HANDOFF'}
    for p in sorted(HERE.iterdir()):
        if p.is_file() and p.name != 'MANIFEST.json':
            data = p.read_bytes()
            seal['files'][p.name] = {'bytes': len(data), 'sha256': sha(data)}
    write('MANIFEST.json', seal)
    print(json.dumps({'status': 'READY', 'disposition': 'APPROVE', 'checks': len(CHECKS), 'files': len(seal['files'])+1, 'hashes': len(seal['files']), 'manifest_sha256': sha((HERE / 'MANIFEST.json').read_bytes())}))

if __name__ == '__main__':
    main()
