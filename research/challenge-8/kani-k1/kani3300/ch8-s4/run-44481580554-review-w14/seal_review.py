#!/usr/bin/env python3
"""Render and seal only this independent review packet; never run evidence tools."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
BASE = 'research/challenge-8/kani-k1/'
INTAKE = '842984040e87b8b8594653634b72df7d800ca198'
TASK = '0f39a22f0148755e7ba881736e77b54f74b01cb5'
ROOT = '27cdf2a7e7895344aa3be9c47b2867a9298c3e0f'
PACKET = BASE + 'kani3300/ch8-s4/run-44481580554/'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def blob(rev, path, repo=REPO):
    return subprocess.check_output(['git', '-C', str(repo), 'show', rev + ':' + path])

def read(name):
    return json.loads((HERE / name).read_bytes())

def intake(name):
    return json.loads(blob(INTAKE, PACKET + name))

def write(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def check():
    manifest = read('MANIFEST.json')
    actual = {p.name for p in HERE.iterdir() if p.is_file()}
    assert actual == set(manifest['files']) | {'MANIFEST.json'}
    for name, info in manifest['files'].items():
        data = (HERE / name).read_bytes()
        assert len(data) == info['bytes'] and sha(data) == info['sha256'], name
    print(json.dumps({'seal': 'PASS', 'files': len(actual), 'hashes': len(manifest['files']), 'manifest_sha256': sha((HERE / 'MANIFEST.json').read_bytes())}))

def main():
    if '--check' in sys.argv:
        check()
        return
    valid = read('VALIDATION.json')
    replay = read('REPLAY.json')
    assert valid['status'] == replay['status'] == 'PASS'
    assert valid['independent_checks_count'] == 566 and all(replay['projection_matches'].values())
    source = intake('PROVENANCE.json')
    rootpath = BASE + 'kani3300/ch8-s4/s4p1-intake-review-network-plan-inputs/'
    root = json.loads(blob(ROOT, rootpath + 'INPUTS.json'))
    inputs = {
        'schema': 's4p1-independent-w14-review-inputs-v1',
        'authority': 'User11:43 /new14 independent intake+location review; no subagents/model changes',
        'review_task': {'commit': TASK, 'path': BASE + 'TASK-CH8-S4P1-R1-INTAKE-LOCATION-REVIEW-W14.md', 'sha256': sha(blob(TASK, BASE + 'TASK-CH8-S4P1-R1-INTAKE-LOCATION-REVIEW-W14.md'))},
        'root_inputs': {'commit': ROOT, 'path': rootpath, 'files': {n: sha(blob(ROOT, rootpath + n)) for n in ['INPUTS.json', 'ROOT-DECISION.md']}},
        'intake': root['intake'], 'root_replay_claims': root['root_verification'],
        'independent_replay': 'REPLAY.json', 'pins': source['source_tool_control_trigger'],
        'request_sha256': source['request_sha256'], 'workflow_sha256': source['workflow_sha256'],
        'terminal_task_inputs': {n: sha(blob(TASK, BASE + 'kani3300/ch8-s4/postrun-s4p-1-r1-terminal/' + n)) for n in ['INPUTS.json', 'NATIVE-METADATA.json']},
        'qualification_task_sha256': sha(blob(TASK, BASE + 'TASK-CH8-S4P1-R1-QUALIFICATION-LOCATION-W11.md')),
        'owned_path': str(HERE.relative_to(REPO)),
        'settings_constraint': 'Preserve current SolHigh/FastOFF; no model/settings actions or delegation performed',
        'execution_boundary': 'Offline hashes/static source/pure frozen reporting readers only; no acquisition/raw/ZIP/GCS/native/fullValidate/CI/source/policy/ledger edits'
    }
    write('INPUTS.json', inputs)
    limits = [
        'Both network inventories, roles, SAT, U and guard counts remain UNKNOWN_CENSORED, never zero or NOT_RUN.',
        'Only initialized V34/base1 Cell<u8>/KeyLess<Cell<u8>> fallback N0..2 and N3..4 are provisional bounded SOURCE_REPORTED candidates. No admission by this review.',
        'At most a fallback union N0..4 after a separate completed root/coordinator admission; no Cell-to-u8 network transfer.',
        'Producer strict0/8, UNKNOWN fallback receipts, U-REJECT_ALL and disabled proposal remain unchanged.',
        'Actual common emitter, positive source/AST/MIR/caller causal origin and physical inode identity remain UNKNOWN.',
        'Fallback5..16/network5..32/general/provider/initmask/function-summary/ownership/panic/generic trait/fullN16N32 and independent B1/B2 credit remain OPEN/NONE.',
        'No enabled summary edges; bounded leaves are not universal or stub_verified provider contracts.',
        'No new run, policy/runtime parser change, admission, resource escalation, accounting or publication is authorized.'
    ]
    finding = {'schema': 's4p1-w14-independent-findings-v1', 'status': 'READY', 'intake_commit': INTAKE, 'disposition': 'APPROVE_INTAKE_WITH_PRESERVED_LIMITS', 'blocking_findings': [], 'blocking_findings_count': 0, 'nonblocking_findings': [], 'repair_required': False, 'location_recommendation': 'RECOMMEND_TWO_EXACT_CASES', 'location_status': 'NOT_APPLIED', 'admission': False, 'proof_credit': 'NONE', 'constraints': limits, 'correction_route_if_later_needed': 'Original CURRENT11 immutable correction plus SAME14 delta; reviewer never edits intake/source/evidence.'}
    write('FINDINGS.json', finding)
    proposal = intake('LOCATION-PROPOSAL.json')
    props = intake('NATIVE-PROPERTIES.json')
    protected = intake('PROTECTED.json')
    quals = intake('QUALIFICATION.json')['rows']
    cases = []
    for case in proposal['cases']:
        rid = case['root']
        q = next(x for x in quals if x['id'] == rid)
        epoch = next(x for x in protected['epochs'] if x['id'] == rid)
        cases.append({**case, 'independent_recommendation': 'RECOMMEND_EXACT_METADATA_CASE_ONLY',
                      'exact_status_partition': q['status_counts'], 'exact_class_status_partition': q['class_status_counts'],
                      'all_other_property_count': len(props[rid]['properties']) - 1,
                      'located_roles_and_covers': [{'required': r['required'], 'native_matches': r['native_matches']} for r in q['literal_roles']],
                      'located_U_count': q['U_count'], 'located_SUCCESS_guards': q['unsupported_guards'],
                      'extra_failures': q['failed_properties'],
                      'native_registration': q['native_registration'],
                      'protected_identity': {'intake_commit': INTAKE, 'baseline_sha256': sha(json.dumps(protected['baseline'], sort_keys=True, separators=(',', ':')).encode()), 'epoch_sha256': sha(json.dumps(epoch, sort_keys=True, separators=(',', ':')).encode()), 'baseline_epoch': 'E0', 'controller_context': epoch['lifecycle']['context'], 'native_invocation_id': case['invocation_id'], 'native_namespace': case['namespace'], 'controller_and_native_invocation_ids_are_distinct': True, 'all_five_binary_snapshots_equal_E0': epoch['all_five_equal_E0'], 'worker_protected_reader': epoch['protected'], 'full_intake_PROTECTED_sha256': sha(blob(INTAKE, PACKET + 'PROTECTED.json'))}})
    write('LOCATION-DECISION.json', {
        'schema': 's4p1-w14-exact-location-recommendation-v1', 'status': 'NOT_APPLIED',
        'recommendation': 'RECOMMEND_TWO_EXACT_CASES', 'review_disposition_is_separate': finding['disposition'],
        'intake_commit': INTAKE, 'cases': cases,
        'conditions': proposal['constraints'] + [
            'Root must first verify this actual committed READY packet, manifest and complete exact identity tuples; coordinator/root then make a separate recorded decision.',
            'Keep full property ID and display ID, class unreachable, status SUCCESS, description unreachable code, both location keys present-null, full display and cardinality exactly one per specified invocation.',
            'All other records remain positively located; exact inventories/counts, four literal SUCCESS roles, every length/witness SAT, four source-local U arguments, three SUCCESS guards and successful unwind per fallback are independent gates.',
            'Preserve the complete protected baseline/controller/native tuple; controller worker IDs and native compiler invocation IDs occupy distinct namespaces and are not equated.',
            'Hypothetical packet equality tests are a proposal-boundary test, not an active parser fix or proof of emitter provenance.'
        ],
        'old_original_decisions': proposal['old_packets'],
        'old_comparison': 'Original sort4same f740 and merge8 ff193 exact decisions and their reviews are valid only for their original runs. Same null/display-zero/class/status shape does not transfer admission or establish a common emitter.',
        'shared_emitter_source_MIR_origin': 'UNKNOWN', 'general_rule': 'NOT_RECOMMENDED',
        'adverse_controls': {'count': 66, 'result': 'ALL_REJECT', 'reproduced': 'REPLAY.json', 'scope': proposal['test_scope']},
        'admission': False, 'producer_or_history_changed': False, 'runtime_parser_policy_changed': False
    })
    coverage = [
        {'requirement': '1 identity/native terminal', 'assessment': 'PASS_SOURCE_REPORTED', 'evidence': ['INPUTS.json', 'REPLAY.json'], 'detail': 'Exact source985/tool0aac/control2db/trigger563 trees and sole parents; author5b0/revieweff6/GO1f9; request3d135/workflowa567. Native run44481580554/attempt1/push completed FAILURE. Transport digest is historical sealed metadata, distinct from independently rehashed compact member/payload; no reacquisition.'},
        {'requirement': '2 protected modes/epochs', 'assessment': 'PASS_SOURCE_REPORTED', 'evidence': ['REPLAY.json', 'LOCATION-DECISION.json'], 'detail': 'All eight Original/null rows use singleton selectors/fresh native namespaces. E0/pre/worker BEFORE/AFTER/controller post match; all source/controller pair readers pass; no recorded errors ignored. No absent AFTER recovery needed. Exact frozen readers reject observed errors in all states; B01/B02 protections and gate closures inherited from reviewed control, not newly proven by native result.'},
        {'requirement': '3 four fixed negative controls', 'assessment': 'PASS_EXACT_LITERAL_OBSERVATIONS', 'evidence': ['QUALIFICATION-AUDIT.json'], 'detail': 'One exact located FAILURE each: S2_NEG_CHECKER_ORDER/COUNT/SORT13_WEAK and S4_NEG_CELL_COUNT. sort13 is fixed descending [12..0], only permitted ordinary weak_swap seam. Cell control uses initialized V34 interior [1..3], [0,1]->[0,0]; source still sorted, ACTIVE native SUCCESS/count FAILURE; no actual-sort bug claim.'},
        {'requirement': '4 actual model/body/roles/SAT', 'assessment': 'FALLBACK_SOUND_PROVISIONAL_SOURCE_REPORTED; NETWORK_UNKNOWN', 'evidence': ['QUALIFICATION-AUDIT.json', 'LOCATION-DECISION.json', 'SOURCE-REVIEW.json'], 'detail': 'All34 independent logical u8 values, V34/base1, exact inclusive N0..2/3..4, Cell new/get/set/full-value model and actual small_sort_fallback body; no positive stubs/providers. Four literal SUCCESS roles and 8/7 SAT covers for fallback including3/2 length covers plus five feasible block witnesses. Network3/2 length covers and witnesses are required but unobserved. No impossible N0/1 UNSORTED/duplicate/nonconstant witness. Source21assert/30cover sites differ from594 native records. Each fallback has one native unwind SUCCESS.'},
        {'requirement': '5 qualification/U/guard/location', 'assessment': 'PASS_WITH_PRESERVED_LIMITS', 'evidence': ['QUALIFICATION-AUDIT.json', 'LOCATION-DECISION.json', 'FINDINGS.json'], 'detail': 'All594 records/statuses/counts retained;26 individual source-local U arguments reviewed; seven located unsupported SUCCESS guards retained. U definedness is not independent emitted-property proof. Two full exact class-unreachable SUCCESS location records differ from status UNREACHABLE. Strict0, receipts UNKNOWN, REJECT_ALL/proposalDISABLED unchanged.'},
        {'requirement': '6 prefix and terminal schema', 'assessment': 'PASS_AUTHENTIC_READERS', 'evidence': ['REPLAY.json'], 'detail': 'Eight ordered starts and durable seals including timed-out unknown rows; selected_roots genuine int8 from request inventory, exact realstr terminal ch8-s4p-1-campaign-v1 before collection. Fresh local/upload-only collectors agree, no missing selected groups/global stop. 29 authentic adverse checks reject malformed schema/count, missing/changed sealed export and drift. No malformed terminal normalization or proof reconstructed.'},
        {'requirement': '7 costs/caps/cleanup', 'assessment': 'PASS_CENSORED_COST_CLASSIFICATION', 'evidence': ['COST-AUDIT.json'], 'detail': 'Both network cutoffs are CHILD600_WALL_INCLUDING_COMPILE, not observed RSS/compile180/slot/outer/global cap. Signal15/original-15, verified shutdown/reap, no survivors; safe serial continuation/sealing. Effective min(6GiB,12GiB,available-2GiB)=6291456KiB observed for each row. Nominal50ms PGID/owned-census RSS only; event omissions retained in sealed COST. Setup721.679s total, campaign1779.707s and native timing distinct; no uncensored/backend/truepeak inference.'},
        {'requirement': '8 bounded scope/no admission', 'assessment': 'PASS_NO_CREDIT', 'evidence': ['RESULT.json', 'FINDINGS.json'], 'detail': 'Only exact finite fallback candidates eligible for separate location/admission decision; possible union0..4 later. Network native result remains UNKNOWN. All general/init/provider/caller/MIR/B1B2/fullN16N32 obligations remain open; no summary enabled by paths below9.'}
    ]
    write('AUDIT-COVERAGE.json', {'schema': 's4p1-w14-eight-requirements-v1', 'all_eight_audited': True, 'items': coverage})
    src_repo = Path('/root/verify-rust-std-ch8-s4p-1-w13')
    src_sha = source['source_tool_control_trigger']['source']['sha']
    citations = []
    spans = [
        ('library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_partition.rs', 21, 85),
        ('library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs', 30, 62),
        ('library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs', 78, 120),
        ('library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs', 137, 157),
        ('library/core/src/slice/sort/shared/smallsort.rs', 220, 224),
        ('library/core/src/slice/sort/shared/smallsort.rs', 332, 374),
        ('library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs', 130, 150),
        ('library/core/src/ptr/const_ptr.rs', 1470, 1482),
        ('library/core/src/fmt/mod.rs', 815, 824),
        ('library/core/src/num/uint_macros.rs', 3215, 3228)
    ]
    for path, lo, hi in spans:
        data = blob(src_sha, path, src_repo)
        lines = data.decode().splitlines()
        citations.append({'commit': src_sha, 'path': path, 'file_sha256': sha(data), 'first_line': lo, 'last_line': hi, 'text': '\n'.join(f'{i+1}: {lines[i]}' for i in range(lo-1, hi))})
    write('SOURCE-REVIEW.json', {'status': 'REVIEWED', 'citations': citations,
        'U_argument_assessment': [
            '18 checker U instances: after valid equal-length snapshot gate, L<=CAP32 bounds i,j and count increments; early false return explains status without asserting emitted reachability. Cell fixture L2 uses logical get/set; fixed sort13 L13, checker_count L32.',
            'Eight fallback U instances: is_power_of_two(align) on normal continuation implies align>=1 before align-1; fmt shift count1<usize64 proves shift definedness only, not no lost bits; abs_diff each branch orders unsigned subtraction. Arguments are site-local and do not establish AST/MIR/emitter binding.'
        ],
        'full_count_reason': 'active_post checks equal length and all input full-byte values with multiplicities; these account for the entire equal-length output, leaving no novel output. Cell uses get for full logical value; comparator is stateless logical less.',
        'frame_reason': 'Each of34 outside indices is checked after the actual call; arbitrary outside canary is additional. No count/fewkeys/frame oracle weakening.',
        'actual_paths': 'fallback len>=2 calls insertion_sort_shift_left(v,1); network N<=4 returns for<2 or runs presorted_len1 insertion, no_merge true, with no sort9/sort13/merge summary edge enabled. This is source reasoning, not completed network verification.',
        'causal_binding': 'UNKNOWN; source hashes and lines alone do not establish MIR/emitter or physical execution causality', 'proof_credit': 'NONE'})
    result = {'schema': 's4p1-w14-independent-review-result-v1', 'status': 'READY', 'intake_commit': INTAKE, 'disposition': finding['disposition'], 'blocking_findings_count': 0, 'location_recommendation': 'RECOMMEND_TWO_EXACT_CASES', 'location_status': 'NOT_APPLIED', 'native': {'success': 2, 'intended_negative_failure': 4, 'wall_censored_unknown': 2}, 'strict_expected_matches': '0/8', 'observed_native_properties': 594, 'source_local_U_arguments': 26, 'retained_SUCCESS_guards': 7, 'independent_checks': 566, 'replay': {'checks': 1163, 'adverse': 29, 'location_adverse': 66, 'primary_projections': '11/11 MATCH', 'supplemental_projections': '9/9 MATCH', 'supplemental_checks': 220}, 'admission': False, 'proof_obligations_closed': 0, 'proof_credit': 'NONE', 'limits': limits, 'next': 'Root verify actual review commit/HANDOFF/manifest, then separate root+coordinator exact location/admission decision. No automatic implementation or CI.'}
    write('RESULT.json', result)
    write('PROVENANCE.json', {'schema': 's4p1-w14-independent-review-provenance-v1', 'task_commit': TASK, 'root_input_commit': ROOT, 'reviewed_intake_commit': INTAKE, 'member_sha256': source['member_sha256'], 'payload_sha256': source['uncompressed_payload_sha256'], 'artifact_transport_digest': source['artifact_metadata']['digest'], 'artifact_metadata_assurance': 'Sealed intake snapshot compared to exact task snapshot; no new live API observation or transport reacquisition.', 'source_control_tool_trigger': source['source_tool_control_trigger'], 'request_sha256': source['request_sha256'], 'workflow_sha256': source['workflow_sha256'], 'independent_manifest_verification': '36 committed files,35 hashes plus manifest SHA, compact430087B/payload and all119 member hashes', 'reader_execution': 'Exact pinned replay.py/audit.py and frozen118 pure reporting files, source static gates, disposable local/upload replay; no runner main/fullValidate/native invocation.', 'review_harness_note': 'Initial temporary-path wiring stopped before replay at relative_to; corrected using disposable Git-directory reference. No intake/evidence edit and no failed proof result normalized.', 'history': 'Original intake and old f740/ff193 admissions preserved. Prior305 host validation remains historical regression evidence only.', 'external_or_mutating_actions': [], 'settings_actions': [], 'subagents': 0, 'written_scope': str(HERE.relative_to(REPO)), 'independence': 'Fresh W14 main review; no delegated review or author intake/source changes.'})
    table = '\n'.join('| ' + ' | '.join(str(v) for v in [q['id'], q['native_verdict'], q['native_property_count'], q['U_count']]) + ' |' for q in quals)
    (HERE / 'REVIEW.md').write_text(f'''# Independent W14 S4P1-r1 intake and location review

Disposition: **APPROVE_INTAKE_WITH_PRESERVED_LIMITS**. No blocking or nonblocking findings. Exact intake `{INTAKE}` / task `{TASK}` / root inputs `{ROOT}`. All eight requirements are individually addressed in AUDIT-COVERAGE.json.

Location recommendation: **RECOMMEND_TWO_EXACT_CASES**, separately **NOT_APPLIED**. LOCATION-DECISION.json pins each full dictionary, same-invocation inventory/counts, role/cover/U/guard partitions and protected tuple. Root must verify the actual committed review, then root/coordinator independently decide any location/admission change. No active producer, parser or policy changes follow from this review.

| Root | Native verdict | Properties | Status U |
| --- | --- | --- | --- |
{table}

Strict expected matches remain0/8. Two fallback native SUCCESS inventories have228/227 records, each220 checks(216SUCCESS+4U), covers8/7 SAT. Exactly one unlocated class=`unreachable`/status=`SUCCESS` record per fallback, full selector`.unreachable.1`, both file/line present-null and exact lib.rs:0:0 display. All other227/226 properties are positively located. Four literal SUCCESS roles, length SAT3/2 plus five feasible witnesses, three SUCCESS guards and one unwind SUCCESS per fallback remain mandatory gates. Class unreachable SUCCESS is distinct from status UNREACHABLE.

Four negatives each contain one intended located literal FAILURE; the Cell control also has ACTIVE SUCCESS. Source [0,1]->[0,0] is still sorted and fails count; sort13weak is fixed descending [12..0]. No claim that actual sorting failed. Positive fallback source uses all34 independent full logical bytes, initialized Cell new/get/set, V34/base1, exact N0..2/3..4, actual small_sort_fallback, no positive stubs/providers. Full multiplicity count and complete outside frame remain intact. U arguments are sound site-local definedness explanations under stated premises, not independently established emitted-property/MIR proofs. Every observed unsupported SUCCESS guard remains recorded, without general support claims.

The sealed packet is complete at36 committed files/35 manifest hashes and119 structured members. Independent566 checks pass. Exact frozen reporting rerun reproduces1163 checks,29 authentic reader adverse checks,66 hypothetical location adverse checks,220 supplemental checks,11/11 main and9/9 supplemental projections. The66 tests restrict a hypothetical exact packet boundary; they do not fix a runtime reader or prove a common emitter. Fresh local/upload-only replay agrees; selected_roots is genuine int8, terminal schema exact, all8 ordered starts/seals, no global stop. Protected E0/pre/worker BEFORE/AFTER/controller post checks pass for every row, including UNKNOWN rows; original errors, epochs, omitted events, exits and supervision remain in the immutable intake. No missing-AFTER recovery was used.

Both network results remain UNKNOWN after CHILD600_WALL_INCLUDING_COMPILE: wholechild601.428/601.401s; initial-export compile upper48.195/45.976s; sampled RSS3515064/3516320KiB against observed effective6291456KiB. Signal15/original exit-15, verified shutdown/reap/no survivors; outer/slot/compile180/RSS cutoff not observed. Native verification time/peak and exact backend/symex subphase remain censored UNKNOWN. Fallback native verification140.741771488/144.622441392s differs from wholechild189.05/193.6s, setup total721.679s and campaign1779.707s. Sampled nonatomic PGID/owned-census RSS does not establish a kernel/cgroup/tree true peak. Caps unchanged; no inference that more memory solves the wall timeout.

Old sort4same f740/merge8 ff193 and their independently reviewed exact cases were compared only in original-run scope. Same display-zero/null shape is not common-emitter, source or MIR proof. No suffix/wildcard/stdlib/unreachable waiver, coordinate substitution or future-run rule is recommended.

Only two finite fallback SOURCE_REPORTED candidates may proceed to a separate exact admission decision; possible union0..4 remains conditional. Network, fallback5..16/network5..32/general/initmask/provider/function-summary/caller/ownership/panic/generic trait/fullN16N32/MIR/B1B2 remain OPEN/NONE. No proof obligations closed. ProducerUNKNOWN, U-REJECT_ALL, proposalDISABLED and history unchanged. No acquisition/raw/ZIP/GCS/native/fullValidate/CI/model/settings/delegation/source/policy/ledger/publication action.
''')
    (HERE / 'HANDOFF.md').write_text(f'''# READY — independent W14 immutable handoff

Use the full40-character containing Git commit returned with this HANDOFF. MANIFEST.json hashes every own packet file except itself; containing Git commit binds the manifest. Read RESULT.json, REVIEW.md, FINDINGS.json and the separate LOCATION-DECISION.json.

Reviewed intake `{INTAKE}` exactly; task `{TASK}`, root inputs/decision `{ROOT}`. Intake manifest `{root['intake']['manifest_sha256']}`, intake HANDOFF `{root['intake']['HANDOFF_sha256']}`. Source985/tool0aac/control2db/trigger563 plus author5b0/revieweff6/GO1f9/request3d135/workflowa567 preserved in INPUTS/PROVENANCE.

Disposition APPROVE_INTAKE_WITH_PRESERVED_LIMITS; zero findings. Separate location recommendation RECOMMEND_TWO_EXACT_CASES, status NOT_APPLIED. Full exact IDs/dictionaries/cardinality/invocations/counts/all-other-located roles/covers/U/guards/protected identities are in LOCATION-DECISION.json. Common emitter/source/MIR origin UNKNOWN. Original f740/ff193 do not transfer.

Independent566 checks PASS; exact offline replay1163/29adverse/66locationadverse plus220 supplemental checks,11main+9supplemental projections MATCH. 36files/35hashes/119structured members independently checked;594 native properties/26source-local U/7SUCCESS guards. Native2fallback SUCCESS/4intended FAILURE/2network wall-censored UNKNOWN; strict0/8, originalUNKNOWN/U-REJECT_ALL/proposalDISABLED/history unchanged. No qualification/admission/proof credit.

Both network600wholechild wall inclcompile,601.428/601.401s, compile upper48.195/45.976s, sampled RSS3515064/3516320KiB at effective6291456KiB. Native inventory/backend phase/uncensored timing UNKNOWN. COST-AUDIT.json retains scope/caps/cleanup/censoring. At most exact Cell fallback N0..4 may later be joined after separate admission; no u8network/init/provider/summary/universal/MIR/B1B2/fullN16N32 transfer.

Root rechecks this actual committed READY and manifest first. Root/coordinator alone make a separate exact location/admission decision; no automatic implementation/CI/accounting. Findings, if later identified, return original CURRENT11 as immutable correction plus SAME14delta; reviewer never edits intake. Source-only network planning may bind this actual fullSHA/verdict and limits. No new acquisition/raw/ZIP/GCS/native/fullValidate/CI/source/policy/ledger edits or subagents/model/settings actions. Current high/FastOFF constraint preserved without settings actions.

Validation: `python3 seal_review.py --check` is a pure own-manifest check. `review.py` repeats only bounded offline reporting/static checks, never native/fullValidate. Authorized independent review is complete; root/coordinator decisions remain outside this packet.
''')
    (HERE / 'READY.md').write_text('READY: APPROVE_INTAKE_WITH_PRESERVED_LIMITS; zero findings.\nSeparate location recommendation RECOMMEND_TWO_EXACT_CASES / NOT_APPLIED.\nUse actual containing full40-character Git SHA returned with HANDOFF.md.\nNo admission/proof credit/automatic implementation/CI.\n')
    manifest = {'schema': 's4p1-w14-immutable-review-manifest-v1', 'status': 'READY', 'files': {}, 'excluded': ['MANIFEST.json'], 'identity': 'Containing exact full Git commit binds manifest; returned with HANDOFF', 'scope': str(HERE.relative_to(REPO))}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name != 'MANIFEST.json':
            data = path.read_bytes()
            manifest['files'][path.name] = {'bytes': len(data), 'sha256': sha(data)}
    write('MANIFEST.json', manifest)
    check()

if __name__ == '__main__':
    main()
