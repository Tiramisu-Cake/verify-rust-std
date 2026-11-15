#!/usr/bin/env python3
"""Prepare bounded CI rows from committed source; never runs proof/build/CI."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = Path('/root/verify-rust-std-ch8-profiles-w11')
BASE = '872d5a43380752786415bc00d2a12ce0e930cb37'
PREFIX = 'library/core/src/slice/sort/shared/smallsort/verify/'
MOD = 'slice::sort::shared::smallsort::verify::'

def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()

def source(rel):
    return subprocess.check_output(['git', '-C', str(ROOT), 'show', f'HEAD:{PREFIX}{rel}'], text=True)

rows = []
def add(module, name, mode, profile, geometry, unwind, failures=None, companion=None):
    rows.append({'id': name, 'selector': MOD + module + '::' + name,
                 'source_selector': 'core::' + MOD + module + '::' + name,
                 'source_file': PREFIX + module.replace('::', '/') + '.rs',
                 'mode': mode, 'profile': profile, 'geometry': geometry,
                 'unwind': unwind, 'expected': 'DETECTED' if failures else 'SUCCESS',
                 'allowed_failure_descriptions': failures or [], 'leaf_companion': companion,
                 'cfg': ['kani_smallsort_controls'] if failures else [],
                 'covers': 'Every emitted cover must be SAT; bind complete descriptions and IDs from this exact row export.',
                 'timeout_seconds': 600, 'planned_seconds': 60, 'state': 'NOT_RUN',
                 'replacement_inventory': 'Only the declared wrapper in Replace mode; its real helper body must run in PFC. Other rows real bodies, except existing frame-negative PFC.',
                 'property_binding': None})

network = source('network.rs')
merge = source('merge.rs')
profiles = source('merge/profiles.rs')
forwarding = source('forwarding_contracts.rs')
for n, p in [('u8','LtU8'), ('i32','LtI32'), ('u64','LtU64')]:
    add('network', f'swap_contract_four_positions_{n}', 'PFC:swap_profile', p,
        'backing4; distinct symbolic indices in0..4', None)
for name, tag in re.findall(r'^swap_contract_exact_array_case!\(\s*(\w+),\s*(\w+)\s*\)', network, re.M):
    add('network', name, 'PFC:swap_profile', tag, 'exact backing2; both orientations', 180)
for name, tag, n in re.findall(r'^swap_contract_arbitrary_indices_case!\(\s*(\w+),\s*(\w+),\s*(\d+)\s*\)', network, re.M):
    add('network', name, 'PFC:swap_profile', tag, f'backing{n}; distinct symbolic indices', 25)
for name, lo, hi in re.findall(r'^insert_tail_start1_group_case!\(\s*(\w+),\s*(\d+),\s*(\d+),', network, re.M):
    add('network', name, 'PFC:insert_tail_profile', 'LtU64', f'backing17; begin1; tail{lo}..{hi}', 25)
add('network', 'contract_insert_tail_u8_prefix', 'PFC:insert_tail_profile', 'LtU8', 'backing17; begin0; tail1..16; source solver cadical', 18)
for name, arbitrary, ty, tag in re.findall(r'^define_sort4_contract_and_comparator_harnesses!\(\s*(\w+),\s*(\w+),\s*(.*?),\s*(\w+)\s*\)', merge, re.M|re.S):
    add('merge', name, 'PFC:sort4_profile', tag, f'{ty}; separate exact src4/dst4; uninitialized destination', 34)
for name, tag in re.findall(r'^define_small_merge_contract_harness!\(\s*(\w+),\s*(\w+)\s*\)', merge, re.M):
    add('merge', name, 'PFC:merge_profile', tag, 'separate exact src/dst; N2,3,4; sorted halves', 34)
for name, tag, n in re.findall(r'^define_merge_contract_harness!\(\s*(\w+),\s*(\w+),\s*(\d+)\s*\)', merge, re.M):
    add('merge', name, 'PFC:merge_profile', tag, f'separate exact src/dst; N{n}; sorted halves', 34)
add('merge', 'merge_scratch48_contract_u8_n9', 'PFC:merge_profile', 'LtU8', 'source first9 in either stable/general scratch48; separate initialized dst9', 34)
for name, tag in re.findall(r'^profile_relation_case!\(\s*(\w+),\s*([^\n)]+)\)', network, re.M):
    add('network', name, 'Original', tag, 'two arbitrary full element values; pure models before/after', 180)
for name, profile in [('stable_cell_n2','Cell<u8>/upper7'),('unstable_byte_n2','u8/upper7'),('freeze_noncopy_n2','NonCopyU8/upper7')]:
    add('forwarding_contracts', name, 'PFC:concrete_forwarder', profile, 'active pair[1..3] in backing4; stable scratch_len0..2 initialized slot0/uninit tail', 16)
for name, profile, geometry, unwind, companion in [
    ('profile_swap_consumer_u8_backing4','LtU8','backing4; distinct symbolic indices0..4',6,'swap_contract_four_positions_u8'),
    ('profile_sort4_consumer_u64','Sort4ReadU64','separate exact src4/dst4',34,'sort4_contract_u64_n4'),
    ('profile_sort4_consumer_b16','Sort4ReadB16','separate exact src4/dst4',34,'sort4_contract_bytes16_n4'),
    ('profile_insert_consumer_u8_backing17','LtU8','backing17; begin0; tail1..16',18,'contract_insert_tail_u8_prefix'),
    ('profile_merge_consumer_u8_len4','LtU8','separate exact src4/dst4; sorted halves',34,'merge_contract_u8_n2_to4')]:
    add('merge::profiles', name, 'Replace:profile_wrapper', profile, geometry, unwind, companion=companion)
controls = [
    ('profile_wrong_f_swap_rejected_u8','BadCmpU8','backing2 [0,2]',None,'bad-profile swap transfer rejected','swap_contract_four_positions_u8'),
    ('profile_wrong_f_sort4_rejected_u64','BadCmpU64','src4 [0,2,4,6]; separate dst4',34,'bad-profile sort4 order rejected','sort4_contract_u64_n4'),
    ('profile_wrong_f_insert_rejected_u8','BadCmpU8','[0,4,2]; begin0/tail2; sorted prefix',6,'bad-profile insert order rejected','contract_insert_tail_u8_prefix'),
    ('profile_wrong_f_merge_rejected_u8','BadRelationU8','src2 [0,2]; singleton halves; separate dst2',6,'bad-relation merge order rejected','merge_contract_u8_n2_to4'),
    ('profile_bad_relation_rejected_u8','BadRelationU8','values0,2',None,'bad comparator-model relation rejected','profile_relation_lt_u8'),
    ('profile_full_value_checker_rejects_payload_change_u8','LtU8','arbitrary exact src4/dst4; post-return low payload-bit mutation',6,'full-value checker detects payload corruption','same-root real LtU8 sort4 stage; no summary admission')]
for name, profile, geometry, unwind, failure, companion in controls:
    add('merge::profiles', name, 'Original', profile, geometry, unwind, [failure], companion)
add('forwarding_contracts','rejects_always_true','Original','test-only always_true static closures','three branches; exact pair[0,2]; real stable/unstable/Freeze entries',16,
    ['bad stable adapter relation rejected','bad unstable adapter relation rejected','bad Freeze adapter relation rejected'],'all three forwarding PFCs')
add('forwarding_contracts','rejects_payload_corruption','Original','u8/upper7','exact pair arbitrary; independent probe; post-return payload flip',16,
    ['full-value checker rejects payload corruption'],'unstable_byte_n2')
add('helper_contracts','swap_safety_u8_backing4','PFC:swap_if_less','arbitrary_less::<u8> FnDef','backing4; symbolic a,b including equality',8)
add('helper_contracts','rejects_swap_comparator_writing_outside_frame_u8','PFC:swap_if_less','effectful captured-counter closure','backing4; indices0,1; captured counter outside frame',None,
    ['<generated modifies property for captured comparisons; bind identity before accepting DETECTED>'],'swap_safety_u8_backing4')
assert len(rows) == len({r['selector'] for r in rows})
assert sum(r['mode'].startswith('PFC') for r in rows) == 38  # 36 migrated + existing frame pair
assert len([r for r in rows if 'profile_relation_' in r['id']]) == 11
assert len(rows) == 62, len(rows)
for r in rows:
    for failure in r['allowed_failure_descriptions']:
        if not failure.startswith('<'):
            s = {'merge::profiles': profiles,'forwarding_contracts': forwarding}.get(r['selector'].removeprefix(MOD).rsplit('::',1)[0], '')
            assert f'"{failure}"' in s, (r['id'], failure)
flags = ['-Z','unstable-options','./library']
for opt in ['function-contracts','mem-predicates','float-lib','c-ffi','loop-contracts','quantifiers','stubbing','export-json']:
    flags += ['-Z',opt]
flags += ['--no-assert-contracts','--harness','<ROW_SELECTOR>','--exact','--jobs','1',
          '--harness-timeout','600s','--target-dir','<ROW_OUT>/target','--export-json','<ROW_OUT>/export.json',
          '--output-format=regular','--cbmc-args','--object-bits','12']
manifest = {'schema':'ch8-profiles-ci-request-v1','state':'PREPARED_NOT_AUTHORIZED_NOT_RUN',
    'bucket':'Profiles-ON','coordinator_only':True,'dispatch_cap':3,'dispatch_charged':0,
    'source': {'base':BASE,'commit':git('rev-parse','HEAD'),'tree':git('rev-parse','HEAD^{tree}'),
               'patch':'source.patch','patch_sha256':hashlib.sha256((HERE/'source.patch').read_bytes()).hexdigest()},
    'off_tool':{'commit':'0aac16ef62da9e9d5645782d458593e5d78143ba','tree':'9d8bc9312bf955ef126d32b819b3cd0ed105ed2b',
                'pin_override':'CI-control external KANI_TOML_FILE or exact prebuilt bound binary; base cd355b0b must not be used'},
    'off_argv':['<EXACT_KANI_BINARY>','verify-std'] + flags,
    'off_flags':{'object_bits':12,'uninit':False,'valid_value':False,'slicing':'default','checks':'default',
                 'unwinding_assertions':True,'no_assert_contracts':True,'source_unwind':'honor each source attr; none means default, no new bound'},
    'stages':[
        {'id':'PROFILES-01','state':'NOT_RESERVED_NOT_RUN','mode':'OFF','rows':'all rows, in declared order; gate Replace on matching PFC acceptance',
         'scope':'All migrated PFCs, all11 relations, five matched consumers, new control oracles and unchanged frame pair'},
        {'id':'PROFILES-02','state':'DEFERRED_NOT_READY_NOT_RESERVED_NOT_RUN','mode':'ON','owner':'worker15',
         'gate':'Reviewed OFF result, freeze source/CI payload/tool/flags and all row instances anew; no OFF evidence credited as ON',
         'candidate_safety_pin':'14bc57fdb99960240c4944845a3d985c8af4dcf7','candidate_safety_tree':'1efb6e4dfa69d346df8e23741d11839b1932403d',
         'tool_pin_state':'CANDIDATE_REFERENCE_ONLY_NOT_ADMITTED','rows':'same exact full instance matrix; unsupported row is STOP for its domain, never silently omitted for full qualification',
         'uninit':True,'valid_value':'Separate future qualification; not silently enabled/claimed by uninit ON',
         'argv':'Freeze later; add supported -Z uninit-checks to exact OFF organizer vector on frozen safety pin'},
        {'id':'PROFILES-03','state':'CONDITIONAL_NOT_RESERVED_NOT_RUN','mode':'TARGETED_CORRECTIVE_OR_REPRO',
         'gate':'Concrete earlier result; coordinator GO within bucket3. No automatic retry/sweep/new codegen project.'}],
    'caps':{'runner':'ubuntu-24.04','jobs':1,'max_parallel':1,'concurrent_runs':1,'workflow_minutes':180,
            'setup_seconds':1800,'row_seconds':600,'proof_phase_seconds':8400,'closeout_seconds':600,
            'rss_kib':6291456,'rss_gib':6,'stdout_bytes_per_row':1048576,'stderr_bytes_per_row':1048576,
            'export_bytes_per_row':8388608,'artifact_bytes':268435456,
            'planned_row_seconds':len(rows)*60,'cost_assurance':'UNMEASURED_ESTIMATE; hard caps do not promise completion'},
    'rows':rows,
    'pre_dispatch_gate':['Independent source review plus coordinator/worker14 CI payload and root inventory review.',
        'Exact CI-control/workflow/runner SHA and hashes bound separately; no CI implementation or reservation supplied by this request.',
        'Actual kani list must confirm exact crate-relative selectors; no fallback substring root matching.',
        'Compiler/lowering inventory must bind same P/T/F/geometry/mode; hidden indirect/FnDef shim/layout blocker is STOP.',
        'No expected generated property IDs/counts invented. Bind complete property/cover/replacement metadata from exact-head outputs.',
        'Compiler/driver/backend/binary/target identities and source-clean hashes captured; no local preparation/extraction/compiler.',
        'All actual accepted runs/attempts charged by coordinator in unchanged ledger before retry.'],
    'oracle':['Every positive completed with zero unexpected failures and all emitted covers SAT.',
        'Each negative completed with exactly its named semantic failures (forwarding branch root requires all three), no unrelated failure.',
        'Frame control must fail generated effectful-counter modifies property, independently mapped; no unsupported/setup failure accepted.',
        'Require preceding payload/order/count success checks and reachability covers; preserve probe and full-value bytes.',
        'Unsupported, timeout, missing/partial/truncated/null/wrong-type output or identity mismatch is UNKNOWN/STOP; no SUCCESS by absence.',
        'Preserve original exit/signal/status. Store raw KiB and GiB via /1048576, costs, failed/success property inventories and cover statuses.',
        'OFF and ON are separate results; new wrapper instance cannot inherit historical FnPtr or helper arbitrary-FnDef admission.'],
    'proof_credit':'NONE'}
(HERE/'CI-REQUEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'rows':len(rows),'pfc':sum(r['mode'].startswith('PFC') for r in rows),
                  'request_sha256':hashlib.sha256((HERE/'CI-REQUEST.json').read_bytes()).hexdigest()}))
