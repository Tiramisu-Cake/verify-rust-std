#!/usr/bin/env python3
"""Independent static/Git audit. No suite, compiler, native runner or network."""
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
PACKAGE = '792ca31fa8e5e80380498d9903d9115cdae42d40'
REL = 'research/challenge-8/kani-k1/kani3300/ch8-s3/s3-2-r1'
P = ROOT / REL
checks = collections.Counter()


def need(ok, group):
    assert ok, group
    checks[group] += 1


def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def obj(repo, commit, path):
    return git(repo, 'show', commit + ':' + path)


def doc(name):
    return json.loads((P / name).read_bytes())


pins = doc('PINS.json')
request = doc('CI-REQUEST.json')
files = git(ROOT, 'ls-tree', '-r', '--name-only', PACKAGE, '--', REL).decode().splitlines()
need(len(files) == 36, 'package_inventory')
for file in files:
    need((ROOT / file).read_bytes() == obj(ROOT, PACKAGE, file), 'immutable_package_bytes')
manifest = (P / 'MANIFEST.sha256').read_text().splitlines()
need(len(manifest) == 35, 'package_inventory')
names = []
for line in manifest:
    digest, name = line.split(maxsplit=1)
    name = name.removeprefix('*')
    names.append(name)
    need(sha((P / name).read_bytes()) == digest, 'package_manifest')
need(set(names) == {Path(f).name for f in files} - {'MANIFEST.sha256'}, 'package_inventory')

identities = {}
for label in ('source', 'control', 'tool'):
    pin = pins[label]
    repo = Path(pin['worktree'])
    actual = {key: git(repo, 'rev-parse', value).decode().strip()
              for key, value in [('sha', 'HEAD'), ('tree', 'HEAD^{tree}') ]}
    need(actual['sha'] == pin['sha'] and actual['tree'] == pin['tree'], 'clean_pins')
    need(not git(repo, 'status', '--porcelain=v1'), 'clean_pins')
    if 'sole_parent' in pin:
        need(git(repo, 'rev-list', '--parents', '-n', '1', pin['sha']).decode().split()
             == [pin['sha'], pin['sole_parent']], 'sole_parents')
    identities[label] = {**actual, 'worktree': str(repo)}
source = Path(pins['source']['worktree'])
control = Path(pins['control']['worktree'])
tool = Path(pins['tool']['worktree'])
delta = git(source, 'diff', '--name-only', pins['source']['frozen_reference'], pins['source']['sha']).decode().splitlines()
need(delta == pins['source']['delta_paths'], 'frozen_source_delta')
for rel, digest in pins['control']['protected_exact_bytes'].items():
    before = obj(control, pins['control']['frozen_reference'], rel)
    after = obj(control, pins['control']['sha'], rel)
    need(before == after == (control / rel).read_bytes() and sha(after) == digest, 'protected_modules')
need((P / 'CI-REQUEST.json').read_bytes() == (control / 'ch8-s1-control/CI-REQUEST.json').read_bytes(), 'request_workflow')
need((P / 'WORKFLOW.yml').read_bytes() == (control / '.github/workflows/ch8-s2.yml').read_bytes(), 'request_workflow')
need(sha((P / 'CI-REQUEST.json').read_bytes()) == pins['request']['sha256'], 'request_workflow')
need(sha((P / 'WORKFLOW.yml').read_bytes()) == pins['request']['workflow_sha256'], 'request_workflow')
changed = git(control, 'diff', '--name-only', pins['tool']['sha'], pins['control']['sha']).decode().splitlines()
deleted = git(control, 'diff', '--diff-filter=D', '--name-only', pins['tool']['sha'], pins['control']['sha']).decode().splitlines()
need(changed == request['ci_changed_paths'] and len(changed) == 101, 'payload_inventory')
need(deleted == request['ci_deleted_paths'] and len(deleted) == 16, 'payload_inventory')
need(set(request['ci_payload_sha256']) == set(changed) - set(deleted) - {'ch8-s1-control/CI-REQUEST.json'}, 'payload_inventory')
for rel, digest in request['ci_payload_sha256'].items():
    need(sha((control / rel).read_bytes()) == digest, 'payload_hashes')
for rel, digest in request['changed_file_sha256'].items():
    need(sha((source / rel).read_bytes()) == digest, 'source_hashes')
for rel, text in json.loads((control / 'ch8-s1-control/S32-SOURCE.json').read_bytes()).items():
    need((source / rel).read_text() == text, 'source_fixture')

for dep in doc('DEPENDENCIES.json')['dependencies']:
    data = obj(ROOT, dep['commit'], dep['path'])
    need(sha(data) == dep['sha256'] and len(data) == dep['bytes'], 'dependency_bindings')
    need(git(ROOT, 'rev-parse', dep['commit'] + ':' + dep['path']).decode().strip() == dep['blob'], 'dependency_blobs')
    need((ROOT / dep['path']).read_bytes() == data, 'dependency_current_bytes')
plan_dir = P.parent / 's3-2-capped-offline-prep'
plan_inputs = json.loads((plan_dir / 'INPUTS.json').read_bytes())
need(len(plan_inputs['dependencies']) == 24, 'plan_dependency_inventory')
for dep in plan_inputs['dependencies']:
    data = obj(ROOT, dep['commit'], dep['path'])
    need(sha(data) == dep['sha256'] and len(data) == dep['bytes']
         and git(ROOT, 'rev-parse', dep['commit'] + ':' + dep['path']).decode().strip() == dep['blob'], 'plan_dependencies')
for cit in json.loads((plan_dir / 'SOURCE-CITATIONS.json').read_bytes())['citations']:
    data = obj(ROOT, cit['commit'], cit['path'])
    need(sha(b''.join(data.splitlines(keepends=True)[cit['line_start']-1:cit['line_end']]))
         == cit['range_sha256'], 'plan_citations')
task = 'research/challenge-8/kani-k1/TASK-CH8-S3-2-IMPLEMENT-REVIEW-W14.md'
need((ROOT / task).read_bytes() == obj(ROOT, pins['task'], task), 'issued_review_task')
for cit in doc('SOURCE-CITATIONS.json')['harnesses']:
    data = (source / cit['path']).read_bytes()
    need(sha(data) == cit['file_sha256'], 'citation_files')
    selected = b''.join(data.splitlines(keepends=True)[cit['line_start']-1:cit['line_end']])
    need(sha(selected) == cit['range_sha256'], 'citation_ranges')
boundary = json.loads((P.parent / 's3-2/SOURCE-CITATIONS.json').read_bytes())
for cit in boundary['citations']:
    data = obj(cit['repository'], cit['commit'], cit['path'])
    selected = b''.join(data.splitlines(keepends=True)[cit['line_start']-1:cit['line_end']])
    need(sha(selected) == cit['range_sha256'], 'init_boundary_citations')

order = ['checker_order_corrupt', 'checker_count_corrupt', 'sort13_weak', 'i_p01_b1_16',
         'm8_s32_d00_allinit', 'i_p16_b1_16', 'm8_s32_d00_partial_diag', 'm8_s40_d16_partial_diag']
need([row['id'] for row in request['rows']] == order, 'eight_row_binding')
roots = doc('ROOT-BINDINGS.json')
need(roots['roots'] == request['rows'] and roots['source_bindings'] == request['source_bindings'], 'eight_row_binding')
need(roots['effective_flags'] == pins['flags'] == request['flags'], 'fixed_flags')
need(request['qualification_inventory'] == order[3:6] and request['diagnostic_only_inventory'] == order[6:], 'scope_classification')
rolemap = doc('ROLE-COVER-MAP.json')['selected']
domains = doc('DOMAIN-UNWIND.json')['roots']
role_count = covers = 0
for i, row in enumerate(request['rows']):
    rid = row['id']
    scope = row['scope_classification']
    expected = 'FIXED_NEGATIVE_CONTROL' if i < 3 else 'BOUNDED_ACTUAL_BODY_PFC_CANDIDATE' if i < 6 else 'DIAGNOSTIC_ONLY_INITIALIZATION_OPEN'
    need(scope['category'] == expected and scope['qualification_eligible'] is (3 <= i < 6)
         and scope['eligible_as_init_leaf_or_provider_summary'] is False and scope['proof_credit'] == 'NONE', 'scope_classification')
    need(rolemap[i]['id'] == domains[i]['id'] == rid and rolemap[i]['roles'] == row['roles']
         and rolemap[i]['scope_classification'] == domains[i]['scope_classification'] == scope, 'row_map_binding')
    binding = request['source_bindings'][rid]
    lines = (source / binding['file']).read_text().splitlines()
    for role in row['roles']:
        need(lines[role['line']-1] == role['source_line'] and role['file'] == binding['file']
             and role['source_sha256'] == binding['sha256'], 'literal_coordinates')
        role_count += 1
        covers += role['class'] == 'cover'
    for location in binding['locations']:
        need(lines[location['line']-1] == location['source'], 'root_coordinates')
need((role_count, covers) == (58, 32), 'literal_inventory')
gates = doc('SOURCE-GATES.json')
for name, gate in gates.items():
    need(gate['status'] == 'STATIC_PASS' and gate['source_sha'] == pins['source']['sha']
         and gate['source_tree'] == pins['source']['tree'], 'gate_identity')
    for rel, digest in gate['source_files_sha256'].items():
        need(sha((source / rel).read_bytes()) == digest, 'gate_hash_binding')
    key = {'ordinary': 'ordinary_contract_source_sha256', 'cfg_pfc': 'cfg_pfc_source_sha256',
           'contract_stacks': 'contract_stack_source_sha256', 'lexical': 'lexical_source_sha256'}[name]
    need(gate['source_files_sha256'] == request[key], 'gate_request_binding')
    contexts = gate.get('rows', gate.get('contexts'))
    need(len(contexts) == 8 and [c.get('id', c.get('row')) for c in contexts] == order, 'gate_contexts')
need(len(gates['contract_stacks']['cfg_projection_invariance']) == 16, 'cfg_projections')

replays = []
for patch in doc('PATCHES.json'):
    data = (P / (patch['name'] + '.patch')).read_bytes()
    need(sha(data) == patch['patch_sha256'] and len(data) == patch['bytes'], 'patch_binding')
    repo = Path(patch['repository'])
    with tempfile.TemporaryDirectory(prefix='s32-review-index-') as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
        git(repo, 'read-tree', patch['base'], env=env)
        subprocess.run(['git', '-C', str(repo), 'apply', '--cached', '--whitespace=nowarn', '-'], input=data, env=env, check=True)
        tree = git(repo, 'write-tree', env=env).decode().strip()
    need(tree == patch['expected_tree'] == patch['replayed_tree'], 'patch_tree_replays')
    replays.append({'name': patch['name'], 'tree': tree, 'status': 'MATCH'})
ancestry = []
for case in doc('ANCESTRY.json'):
    repo = Path(pins[case['case']]['worktree'])
    seen = set()
    frontier = {case['expected_head']}
    for level in range(case['depth']):
        following = set()
        for commit in frontier - seen:
            parts = git(repo, 'rev-list', '--parents', '-n', '1', commit).decode().split()
            seen.add(commit)
            following.update(parts[1:])
        frontier = following - seen
    need(set(case['required_objects']) <= seen, 'shallow_graph_reachability')
    ancestry.append({'case': case['case'], 'depth': case['depth'], 'required_commits_reachable': True,
                     'scope': 'Local commit graph, no new clone or remote-fetch claim'})

final = doc('FINAL-VALIDATE.json')
summary = json.loads((P / 'FINAL-VALIDATE.stdout.txt').read_bytes())
transcript = (P / 'FINAL-VALIDATE.stderr.txt').read_text()
need(final['summary'] == summary and final['control_sha'] == pins['control']['sha'], 'validate_receipt')
need(summary['control_tree'] == pins['control']['tree'] and summary['request_sha256'] == pins['request']['sha256'], 'validate_receipt')
need(summary['success'] is True and summary['errors'] == summary['failures'] == final['exit_code'] == 0, 'validate_receipt')
need([int(count) for count, seconds in re.findall(r'^Ran (\d+) tests in ([\d.]+)s$', transcript, re.M)]
     == [136, 56, 35], 'validate_transcript')
need(len(re.findall(r'^OK$', transcript, re.M)) == 3, 'validate_transcript')
need(len(re.findall(r'^test_.* \.\.\. ok$', transcript, re.M)) == 227, 'validate_transcript')
need(final['execution_count_on_exact_candidate'] == 1 and final['elapsed_seconds'] < 1080
     and final['margin'] == 1080 / final['elapsed_seconds'] and final['margin'] >= 1.5, 'validate_margin')

insertion = {(b, p) for b in range(1, 17) for p in range(1, 17)}
selected = {(b, p) for b in range(1, 17) for p in (1, 16)}
merge = {(s, d) for s in range(41) for d in range(41) if s+8 <= d or d+8 <= s}
need(len(insertion) == 256 and len(selected) == 32 and selected <= insertion, 'domain_arithmetic')
need(len(merge) == 1122 and sum(s+8 <= d for s, d in merge) == 561
     and sum(d+8 <= s for s, d in merge) == 561 and (32, 0) in merge, 'domain_arithmetic')
need(8*720+180+240 == 6180 <= 6900 and 600*8 == 4800, 'cap_arithmetic')
need(pins['flags'] == json.loads(obj(control, pins['control']['frozen_reference'], 'ch8-s1-control/CI-REQUEST.json'))['flags'], 'fixed_flags')
need(pins['caps'] == request['s3']['caps'], 'fixed_caps')
need(pins['caps'] == plan_inputs['caps_reference'] and pins['flags'] == plan_inputs['flags_reference'], 'plan_caps_flags')
matrix = json.loads((ROOT / 'research/challenge-8/kani-k1/kani3300/ch8-s4/offline-matrix/MATRIX.json').read_bytes())
need(len(matrix['length_instances']) == 100 and len(matrix['consumer_classes']) == 14
     and len(matrix['dispatch']) == 6, 'remaining_matrix_inventory')
contexts = [(n, side, n if side == 0 else n+8, 0 if side == 0 else n//2)
            for n in range(16, 33) for side in (0, 1)]
need(len(contexts) == 34 and len(set(contexts)) == 34
     and (32, 0, 32, 0) in contexts and (32, 1, 40, 16) in contexts, 'caller_context_arithmetic')
intake = json.loads((plan_dir / 'INTAKE-BINDING.json').read_bytes())
cost = {row['id']: row for row in intake['cost_rows']}
need(cost['s3_insert_tail_u8_rel16']['execution']['termination_reason'] == 'rss_cap'
     and cost['s3_insert_tail_u8_rel16']['execution']['elapsed_seconds'] == 112.349
     and cost['s3_merge8_u8_same_alloc']['execution']['termination_reason'] == 'timeout'
     and cost['s3_merge8_u8_same_alloc']['execution']['elapsed_seconds'] == 600.205, 'cost_metric_distinction')
need(round(cost['s3_merge8_u8_separate']['native_verification_time_s']) == 151
     and round(cost['s3_sort4_u8_same_alloc']['native_verification_time_s']) == 212, 'cost_metric_distinction')
# Witness arithmetic checks feasibility of declared value premises only. This
# deliberately does not simulate a Rust kernel or certify native cover reachability.
for p in (1, 16):
    prefix = [1] * p
    need(prefix == sorted(prefix) and 2 >= prefix[-1] and 0 < prefix[0]
         and 1 == prefix[0] and len(set(prefix+[2])) > 1, 'cover_premise_witnesses')
for a, b in [([0,1,2,3], [4,5,6,7]), ([4,5,6,7], [0,1,2,3]),
             ([0,1,2,3], [3,4,5,6]), ([0,2,4,6], [1,3,5,7])]:
    need(a == sorted(a) and b == sorted(b) and all(0 <= x <= 255 for x in a+b)
         and len(set(a+b)) > 1, 'cover_premise_witnesses')

result = {'schema': 's3-2-r1-independent14-input-audit-v1', 'status': 'PASS',
          'package': PACKAGE, 'root_observed_head': git(ROOT, 'rev-parse', 'HEAD').decode().strip(),
          'identities': identities, 'checks': dict(checks), 'total_assertions': sum(checks.values()),
          'package_files': 36, 'manifest_hashes': 35, 'patch_replays': replays, 'ancestry': ancestry,
          'literal_sites': role_count, 'cover_sites': covers,
          'coverage': {'insertion': [32, 256], 'allinit_merge': [1, 1122], 'partial_provider_contexts_closed': 0},
          'final_validate': {'source_reported_tests': 227, 'new_executions': 0, 'receipt_and_transcript_audited': True,
                             'elapsed_seconds': final['elapsed_seconds'], 'margin': final['margin']},
          'limits': ['Static Git/source/receipt audit; no native, compiler, verifier or CI execution',
                     'Transcript does not independently establish elapsed runtime or historical invocation uniqueness',
                     'No AST/MIR/provenance or independent initializedness/formal proof credit']}
(HERE / 'INPUT-AUDIT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'assertions': result['total_assertions'], 'checks': result['checks']}, sort_keys=True))
