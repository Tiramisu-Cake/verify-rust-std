#!/usr/bin/env python3
"""Offline package checks only. Does not run/import any Rust or control code."""
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
SOURCE_REPO = Path('/root/verify-rust-std-ch8-s3-1-final-w13')
checks = []


def git(repo, *args):
    return subprocess.check_output(['git', *args], cwd=repo)


def check(condition, name):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(name):
    return json.loads((HERE / name).read_text())


inputs = load('INPUTS.json')
proposal = load('PROPOSAL.json')
citations = load('SOURCE-CITATIONS.json')['citations']
check(inputs['task'] == 'fbd666ffb1ba9b3b2b34b1bd1450105cb0cb666f'
      and inputs['intake'] == '1d8a06c8bd418de6261a1cbbb24ea0f35bae1712'
      and inputs['source'] == '513341f41ce53833a279571401c924bdddddb6c8'
      and inputs['tool'] == '0aac16ef62da9e9d5645782d458593e5d78143ba',
      'Exact task/intake/source/tool pins')
task = git(REPO, 'show', inputs['task'] + ':' + inputs['task_path'])
check(task == (REPO / inputs['task_path']).read_bytes()
      and digest(task) == inputs['task_sha256'], 'Task matches issued Git object')

sealed = {}
for name, ref in inputs['frozen_intake_files'].items():
    data = git(REPO, 'show', ref['commit'] + ':' + ref['path'])
    check(data == (REPO / ref['path']).read_bytes()
          and digest(data) == ref['sha256'] and len(data) == ref['bytes'],
          'Unchanged sealed structured intake: ' + name)
    sealed[name] = json.loads(data)
manifest = sealed['MANIFEST.json']['files']
check(all(ref['sha256'] == manifest[name]['sha256']
          and ref['bytes'] == manifest[name]['bytes']
          for name, ref in inputs['frozen_intake_files'].items()
          if name != 'MANIFEST.json'), 'Structured input hashes match sealed manifest')

source_bytes = {}
for path, ref in inputs['source_files'].items():
    data = git(SOURCE_REPO, 'show', ref['commit'] + ':' + path)
    check(digest(data) == ref['sha256'] and len(data) == ref['bytes'],
          'Frozen source file hash: ' + path)
    source_bytes[path] = data
for name, c in citations.items():
    data = source_bytes[c['path']]
    check(c['commit'] == inputs['source']
          and digest(data) == c['file_sha256']
          and git(SOURCE_REPO, 'rev-parse', c['commit'] + ':' + c['path']).decode().strip() == c['git_blob']
          and data.decode().splitlines()[c['start_line'] - 1:c['end_line']] == c['lines'],
          'Exact frozen source citation: ' + name)

native = sealed['NATIVE.json']
reported = sealed['PROVENANCE.json']['protected_source']['expected']
check(inputs['source_tree'] == reported['std_tree']
      == git(SOURCE_REPO, 'rev-parse', inputs['source'] + '^{tree}').decode().strip()
      and inputs['tool_tree'] == reported['tool_tree']
      and inputs['source'] == reported['std_sha']
      and inputs['tool'] == reported['tool_sha'],
      'Frozen Git source tree agrees with source-reported provenance; tool pin retained')
model_path = next(p for p in source_bytes if p.endswith('/sorting_model.rs'))
check(model_path not in reported['changed_file_sha256']
      and model_path not in sealed['PROVENANCE.json']['protected_source']['source_under_test']['file_sha256']
      and 'model_file_observation' in proposal['binding_limits']
      and all('model_file_observation' in r['binding_gaps'] for r in proposal['rows']),
      'Explicit gap: model text pinned by Git, not an emitted per-file source-under-test hash')
observed = [r for r in native['rich_failed_or_unreachable'] if r['status'] == 'UNREACHABLE']
rows = proposal['rows']
check(len(rows) == len(observed) == 8 and [r['native'] for r in rows] == observed
      and len({r['native']['id'] for r in rows}) == 8
      and {r['native']['id'] for r in rows} == set(native['harness']['checks']['unreachable']),
      'Exactly eight distinct native U rows retained verbatim; no missing/extra rows')
expected = {4: (100, 'i += 1'), 5: (106, 'before.values[i]'),
            6: (111, 'before.values[j]'), 7: (111, 'old_count += 1'),
            8: (112, 'values[j].value()'), 9: (112, 'new_count += 1'),
            10: (113, 'j += 1'), 11: (118, 'i += 1')}
for row in rows:
    n = row['native']
    c = row['source_candidate']
    line, expression = expected[int(n['id'].rsplit('.', 1)[1])]
    check(n['class'] == 'assertion' and int(n['line']) == line == c['line']
          and c['expression_candidate'] == expression and expression in c['exact_line']
          and c['exact_line'] == source_bytes[c['file']].decode().splitlines()[line - 1]
          and c['file_sha256'] == digest(source_bytes[c['file']])
          and all(key in citations for key in c['citations'])
          and row['premises'] == ['P1', 'P2', 'P3', 'P4', 'P5']
          and row['local_reason'] and row['invalidation']
          and row['caller_observations']['native_call_stack'] == 'UNKNOWN'
          and row['loop_instance_observations']['native_iteration'] == 'UNKNOWN'
          and all(key in proposal['binding_limits'] for key in row['binding_gaps']),
          'Per-row candidate text, premises and explicit binding limits: ' + n['id'])

check(native['harness']['checks']['total'] == 24
      and native['harness']['checks']['success'] == 15
      and len(native['harness']['checks']['failure']) == 1
      and native['harness']['failed_properties'][0]['description'] == 'S2_NEG_CHECKER_ORDER'
      and native['harness']['failed_properties'][0]['status'] == 'FAILURE'
      and native['harness']['covers']['total'] == 0
      and proposal['native_summary']['intended_failure'] == native['harness']['failed_properties'][0],
      'Observed 15 SUCCESS / 1 intended literal FAILURE / 8 U / 0 covers')

model = source_bytes[next(p for p in source_bytes if p.endswith('/sorting_model.rs'))].decode().splitlines()
caller = source_bytes[next(p for p in source_bytes if p.endswith('/sorting_s2_batch.rs'))].decode().splitlines()
check(model[8] == 'const CAP: usize = 32;'
      and model[35].strip() == 'fn value(&self) -> u8 { *self }'
      and model[91].strip() == 'if !before.valid || before.len > CAP || values.len() > CAP || before.len != values.len() {'
      and model[94:101] == ['    let mut i = 1;', '    while i < before.len {',
                           '        if values[i].value() < values[i - 1].value() {',
                           '            return false;', '        }', '        i += 1;', '    }']
      and caller[138].strip() == 'let input = [1u8,2]; let out = [2u8,1];'
      and 'snapshot::<u8,KeyLess<u8>>(&input),&out' in caller[139],
      'Fixed source predicate/return and exact length-two caller premises')
# Only scalar sanity checks on the two explicit counterfactuals. No solver,
# executable Rust semantics, compiler-origin binding or general proof is claimed.
before = (1, 2)
out = (2, 1)
snapshot_valid, snapshot_len = True, len(before)
guard = not snapshot_valid or snapshot_len > 32 or len(out) > 32 or snapshot_len != len(out)
check(not guard and 1 < snapshot_len and out[1] < out[0]
      and 0 <= 1 - 1 < len(out), 'Scalar sanity: valid len2; first predicate 1<2 true')
sorted_out = (1, 2)
check(not (sorted_out[1] < sorted_out[0]) and not (out[1] >= out[0]),
      'Scalar counterfactual sensitivity: sorted out / reversed predicate remove first return')

policy = sealed['INPUTS.json']['prior_intake_pins']['U_policy']
check(policy == inputs['current_policy'] == proposal['current_policy']
      and policy['mode'] == 'REJECT_ALL' and policy['enabled'] is False
      and policy['unknown'] == policy['role_unreachable'] == 'REJECT'
      and proposal['proposal_state'] == inputs['proposal_state'] == 'DISABLED'
      and proposal['enabled'] is False and proposal['control_admitted'] is False
      and proposal['independent_B1'] is False and proposal['independent_B2'] is False
      and proposal['proof_credit'] == proposal['qualification'] == proposal['proof_obligations_closed'] == 0
      and all(r['original_status_preserved'] == 'UNREACHABLE'
              and r['admission'] == 'REJECT_ALL' and r['role_success'] is False
              and r['proof_credit'] == 0 for r in rows),
      'REJECT_ALL / DISABLED / no role-U success / zero qualification and credit')
prefix = sealed['PREFIX-REPLAY.json']
check(prefix['global_stop'] is True and prefix['completed_prefix'] == []
      and prefix['rows'][0]['status'] == 'INTERRUPTED'
      and prefix['rows'][0]['outcome'] == 'UNKNOWN'
      and all(r['status'] == 'NOT_RUN' for r in prefix['rows'][1:])
      and inputs['historical']['controller'] == 'STOPPED'
      and inputs['historical']['completed_prefix'] == 0
      and inputs['historical']['qualification'] == inputs['historical']['proof_credit'] == 0,
      'Historical STOPPED/prefix0/INTERRUPTED-UNKNOWN and later8 NOT_RUN unchanged')
check(inputs['invocation'] == sealed['PROVENANCE.json']['invocation']
      and proposal['new_acquisition'] is False and proposal['new_native_execution'] is False,
      'Recorded invocation/cfg unchanged; no acquisition or native execution in validation')
check(not git(REPO, 'diff', '--name-only', inputs['base_g0'], '--',
              '.', ':(exclude)' + str(HERE.relative_to(REPO))).strip(),
      'No tracked changes outside owned output since clean base g0')
print(json.dumps({'status': 'PASS', 'scope': 'Offline static text/identity/completeness and scalar counterfactual checks only',
                  'checks_count': len(checks), 'checks': checks,
                  'rows': 8, 'qualification': 0, 'proof_credit': 0,
                  'independent_B1': False, 'independent_B2': False,
                  'native_execution': 'NOT_RUN', 'new_acquisition': False}, indent=2))
