#!/usr/bin/env python3
"""Bounded combined review: read pinned objects; write only this review packet."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
P = H.with_name('batch-r4-r2')
G = Path('/root/verify-rust-std-kani3300-g0')
PACKAGE = '3cdec7455c52d93903a31e005c7e42204fa502e1'
pins = json.loads((P/'PINS.json').read_text())
C, S, T = (Path(pins[k]['worktree']) for k in ('control', 'source', 'tool'))
F = pins['frozen_control']
checks = {}

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def gs(repo, *args):
    return git(repo, *args).decode().strip()

def obj(repo, rev, path):
    return git(repo, 'show', rev+':'+path)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def dump(name, value):
    (H/name).write_text(json.dumps(value, indent=2)+'\n')

def snapshot(directory, rev):
    rel = str(directory.relative_to(G))
    paths = gs(G, 'ls-tree', '-r', '--name-only', rev, '--', rel).splitlines()
    assert paths
    hashes = {}
    for path in paths:
        data = obj(G, rev, path)
        assert (G/path).read_bytes() == data, path
        hashes[str(Path(path).relative_to(directory.relative_to(G)))] = sha(data)
    lines = (directory/'MANIFEST.sha256').read_text().splitlines()
    seen = set()
    for line in lines:
        digest, name = line.split('  ', 1)
        assert name not in seen and hashes[name] == digest, name
        seen.add(name)
    assert seen == set(hashes)-{'MANIFEST.sha256'}
    return {'commit': rev, 'files': len(paths), 'manifest_entries': len(lines),
            'status': 'COMMITTED_BYTES_AND_MANIFEST_MATCH', 'sha256': hashes}

assert gs(G, 'rev-parse', 'HEAD') == PACKAGE
assert not gs(G, 'status', '--porcelain', '--untracked-files=no')
package = snapshot(P, PACKAGE)
assert package['files'] == 65 and package['manifest_entries'] == 64
contents = json.loads((P/'PACKAGE-CONTENTS.json').read_text())['files']
assert contents == {k:v for k,v in package['sha256'].items()
                    if k not in ('MANIFEST.sha256', 'PACKAGE-CONTENTS.json')}
dependencies = {}
for name, rev in [('review-batch-r4', 'f5dd71722f82ac59e37152927a5f4dd9eee6ea1a'),
                  ('review-batch-r4-r1', 'e7837b0f70e235399e53f8da1b48a4a84b33f693'),
                  ('r14-03-gate-backlog-review', pins['gate_dependency']['review_commit']),
                  ('batch-r4-r1', pins['frozen_package']),
                  ('r14-03-gate-backlog', pins['gate_dependency']['candidate_package'])]:
    dependencies[name] = snapshot(H.with_name(name), rev)
identities = {}
for key, repo in [('control', C), ('source', S), ('tool', T)]:
    expected = pins[key]
    actual = {'sha': gs(repo, 'rev-parse', 'HEAD'), 'tree': gs(repo, 'rev-parse', 'HEAD^{tree}'),
              'parent': gs(repo, 'rev-parse', 'HEAD^'), 'dirty': gs(repo, 'status', '--porcelain')}
    assert all(actual[k] == expected[k] for k in ('sha', 'tree', 'parent'))
    assert not actual['dirty']
    assert gs(repo, 'rev-list', '--parents', '-n', '1', 'HEAD').split() == [actual['sha'], actual['parent']]
    identities[key] = actual
assert pins['source']['sha'] == 'bd62e54df1b4749154790aa3db3cc7978f547f75'
assert pins['control']['sha'] == 'd33a0900da19d865f20ccaa76e1ee27065c5a671'
assert pins['control']['tree'] == 'fe7c05829a6374da2cb11a3b3c993aaf9082a7c7'
assert pins['control']['parent'] == '9e14e033f9ee31522b571c127609dcdff76d230b'
delta = gs(C, 'diff', '--name-only', F, 'HEAD').splitlines()
assert delta == json.loads((P/'CONTROL-DELTA.json').read_text())['paths'] and len(delta) == 6
assert git(C, 'diff', '--binary', '--full-index', F, 'HEAD') == (P/'CONTROL-DELTA.patch').read_bytes()
checks['identities'] = identities
checks['six_path_delta'] = delta

# Verify every supplied full-stock/parent/delta path and both endpoint hashes.
inventories = json.loads((P/'FULL-INVENTORIES.json').read_text())
for name, inventory in inventories.items():
    repo = S if name.startswith('source') else C
    a, b = inventory['base'], inventory['target']
    actual = gs(repo, 'diff', '--name-status', a, b).splitlines()
    assert actual == [x['status']+'\t'+x['path'] for x in inventory['paths']], name
    for row in inventory['paths']:
        for side, rev in [('base', a), ('target', b)]:
            value = row[side]
            if value is not None:
                assert gs(repo, 'rev-parse', rev+':'+row['path']) == value['blob']
                assert sha(obj(repo, rev, row['path'])) == value['sha256']
checks['inventories'] = {k:len(v['paths']) for k,v in inventories.items()}

q = C/'ch8-s1-control'
r = json.loads((q/'CI-REQUEST.json').read_text())
old_r = json.loads(obj(C, F, 'ch8-s1-control/CI-REQUEST.json'))
allowed = {'entry_g0', 'ci_changed_paths', 'ci_payload_sha256', 'control_reference'}
assert {k for k in r.keys() | old_r.keys() if r.get(k) != old_r.get(k)} == allowed
assert r['ci_changed_paths'] == gs(C, 'diff', '--name-only', pins['tool']['sha'], 'HEAD').splitlines()
assert set(r['ci_payload_sha256']) == {p for p in r['ci_changed_paths'] if (C/p).is_file()}-{'ch8-s1-control/CI-REQUEST.json'}
for path, digest in r['ci_payload_sha256'].items():
    assert sha((C/path).read_bytes()) == digest
assert sha((q/'CI-REQUEST.json').read_bytes()) == pins['control']['request_sha256'] == 'd7f4561810178e9eb553d83a04de343f2512aff18bbca0dbd4864472712d4d73'
assert sha((C/'.github/workflows/ch8-s2.yml').read_bytes()) == pins['control']['workflow_sha256'] == 'b70c7dff34fe5ae12985dc0ba44f2791cca3bb288e774416f1eb405ab90b090b'
assert (P/'CI-REQUEST.json').read_bytes() == (q/'CI-REQUEST.json').read_bytes()
assert (P/'WORKFLOW.yml').read_bytes() == (C/'.github/workflows/ch8-s2.yml').read_bytes()
for field in ('changed_file_sha256', 'cfg_pfc_source_sha256', 'contract_stack_source_sha256', 'ordinary_contract_source_sha256', 'lexical_source_sha256'):
    for path, digest in r[field].items():
        assert sha((S/path).read_bytes()) == digest
for path, text in json.loads((q/'S2-SOURCE.json').read_text()).items():
    assert (S/path).read_text() == text
for record in json.loads((P/'MAP-PROVENANCE.json').read_text()):
    data = (P/record['file']).read_bytes()
    assert sha(data) == record['sha256']
    assert data == obj(G, pins['frozen_package'], str(P.with_name('batch-r4-r1').relative_to(G)/record['file']))
for record in json.loads((P/'RUNNER-INVARIANCE.json').read_text())['files']:
    assert sha(obj(C, F, record['path'])) == record['frozen_sha256']
    assert sha((C/record['path']).read_bytes()) == record['candidate_sha256']
    if record['status'] == 'BYTE_IDENTICAL':
        assert record['frozen_sha256'] == record['candidate_sha256']
assert len(r['rows']) == 11 and sum(x['required_cover_count'] for x in r['rows']) == 20
assert sum('oracle' in x for x in r['rows']) == 6
checks['request_rebinding'] = {'changed_fields': sorted(allowed), 'payload_files': len(r['ci_payload_sha256']), 'rows_covers_negatives': [11,20,6], 'all_other_request_fields': 'IDENTICAL'}

integration = json.loads((P/'GATE-INTEGRATION.json').read_text())
gate_report = json.loads(obj(G, integration['review_commit'], str(H.with_name('r14-03-gate-backlog-review').relative_to(G)/'REPORT.json')))
assert gate_report['verdict'] == 'APPROVE' and gate_report['finding']['status'] == 'CLOSED'
assert gate_report['local_control']['sha'] == integration['approved_control']['sha']
assert gate_report['patch']['sha256'] == integration['patch_sha256']
for path, digest in integration['exact_inherited_files'].items():
    assert sha((C/path).read_bytes()) == digest
    assert (C/path).read_bytes() == obj(C, integration['approved_control']['sha'], path)
checks['gate_dependency'] = integration

def ast_without(text, name):
    tree = ast.parse(text)
    tree.body = [n for n in tree.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) or n.name != name]
    return ast.dump(tree, include_attributes=False)

assert ast_without(obj(C,F,'ch8-s1-control/check_package.py'), 'check_yaml') == ast_without((q/'check_package.py').read_bytes(), 'check_yaml')
checks['check_package_outside_check_yaml'] = 'AST_IDENTICAL_INCLUDING_BUILD_CONTROL_FALLBACK_TYPES'
sys.path.insert(0, str(q))
import check_package as cp
import unittest
wf = cp.load_yaml((C/'.github/workflows/ch8-s2.yml').read_text())
old_wf = cp.load_yaml(obj(C, F, '.github/workflows/ch8-s2.yml').decode())
expected_wf = copy.deepcopy(old_wf)
expected_wf['jobs']['s2_batch']['steps'][2]['timeout-minutes'] = 10
expected_wf['jobs']['s2_batch']['steps'][2]['run'] = expected_wf['jobs']['s2_batch']['steps'][2]['run'].replace('test_contract_stacks.py', 'test_contract_stacks.py test_r1403_lexical.py')
assert wf == expected_wf
steps = wf['jobs']['s2_batch']['steps']
assert cp.check_yaml(C/'.github/workflows/ch8-s2.yml')['step_timeout_sum_minutes'] == 186
mutation_names = []
with tempfile.TemporaryDirectory(prefix='r4r2-review-mutations-') as tmp:
    for case in ('drop-module', 'drop-preflight', 'reverse-commands', 'extra-command', 'redistribute-cap', 'swap-source-validate'):
        doc = copy.deepcopy(wf); ss = doc['jobs']['s2_batch']['steps']; v = ss[2]
        if case == 'drop-module': v['run'] = v['run'].replace(' test_r1403_lexical.py', '')
        if case == 'drop-preflight': v['run'] = v['run'].splitlines()[1]
        if case == 'reverse-commands': v['run'] = '\n'.join(reversed(v['run'].splitlines()))
        if case == 'extra-command': v['run'] += 'true\n'
        if case == 'redistribute-cap': v['timeout-minutes'] -= 1; ss[6]['timeout-minutes'] += 1
        if case == 'swap-source-validate': ss[2], ss[6] = ss[6], ss[2]
        import yaml
        path = Path(tmp)/'workflow.yml'; path.write_text(yaml.safe_dump(doc))
        try: cp.check_yaml(path)
        except AssertionError: mutation_names.append(case)
        else: raise AssertionError('accepted workflow mutation: '+case)
checks['workflow'] = {'only_changes': 'VALIDATE_1_TO_10_AND_APPEND_REVIEWED_MODULE', 'rejected_mutations': mutation_names, 'caps_minutes': [s['timeout-minutes'] for s in steps], 'job_minutes': 180}

audit = json.loads((P/'TIMEOUT-AUDIT.json').read_text())
for index, (step, row) in enumerate(zip(steps, audit['steps']), 1):
    assert row['index_1based'] == index and row['name'] == step['name']
    assert row['cap_seconds'] == step['timeout-minutes']*60
    assert row['previous_cap_seconds'] == old_wf['jobs']['s2_batch']['steps'][index-1]['timeout-minutes']*60
    assert row['command'] == step.get('run') and row['action'] == step.get('uses') and row['action_inputs'] == step.get('with')
assert len(audit['steps']) == len(steps) == 12
assert audit['aggregate_setup']['cap_seconds'] == 1800 and audit['job']['minutes'] == 180
checks['timeout_audit'] = {'steps': 12, 'exact_commands_caps_actions': 'MATCH', 'aggregate_seconds':1800, 'maxima_not_elapsed': True, 'actual_CI_remaining': 'UNKNOWN'}

timings = {}
for name, step in [('ACTUAL-FINAL-VALIDATE',steps[2]), ('ACTUAL-CHECK-SOURCE',steps[6])]:
    rec = json.loads((P/(name+'-TIMING.json')).read_text())
    assert rec['status'] == 'PASS' and rec['exit_code'] == 0
    assert rec['command'] == step['run']
    for k in ('control','source','tool'):
        for field in ('sha','tree','parent'): assert rec['provenance'][k][field] == pins[k][field]
    for field in ('request_sha256','workflow_sha256'): assert rec['provenance'][field] == pins['control'][field]
    assert rec['elapsed_seconds'] == (rec['monotonic_end_ns']-rec['monotonic_start_ns'])/1e9
    assert sha((P/(name+'.txt')).read_bytes()) == rec['transcript_sha256']
    timings[name] = rec
log = (P/'ACTUAL-FINAL-VALIDATE.txt').read_text()
assert 'Ran 107 tests in 379.149s' in log and log.endswith('\nOK\n')
assert len(re.findall(r'^test_.* \.\.\. ok$', log, re.M)) == 107
assert len(re.findall(r'^test_.*\(test_r1403_lexical\..* \.\.\. ok$', log, re.M)) == 9
command = steps[2]['run'].splitlines()[1].split()
suite = unittest.defaultTestLoader.loadTestsFromNames([n.removesuffix('.py') for n in command[4:]])
assert suite.countTestCases() == 107
proof = json.loads((P/'FINAL-TEST-PROVENANCE.json').read_text())
assert proof['execution_count'] == proof['check_source_execution_count'] == 1
assert all(proof[k] == v for k,v in timings['ACTUAL-FINAL-VALIDATE'].items())
assert json.loads((P/'PRECURSOR-NOTES.json').read_text())['control_sha'] != pins['control']['sha']
checks['timing_provenance'] = {'status':'CONSISTENT_PINNED_HOST_RECORDS', 'final_tests':107, 'gate_module_tests':9, 'suite_rerun':False, 'source_timing_rerun':False, 'execution_counts':'RECORDED_ONE_EACH; NOT_REMEASURED', 'receipts':timings, 'future_CI_duration':'UNKNOWN'}

# Reuse the packet's reviewed static replay/shallow helpers, never its writer/main.
spec = importlib.util.spec_from_file_location('packet_static_helpers', P/'validate_package.py')
helper = importlib.util.module_from_spec(spec); spec.loader.exec_module(helper)
checks['patch_replays'] = []
for item in json.loads((P/'PATCHES.json').read_text()):
    assert sha((P/item['path']).read_bytes()) == item['sha256']
    checks['patch_replays'].append(helper.replay(S if item['path'].startswith('SOURCE') else C, item))
checks['shallow'] = [helper.shallow(C,pins['control']['sha'],7,pins['tool']['sha']), helper.shallow(S,pins['source']['sha'],5,pins['source']['base']), helper.shallow(T,pins['tool']['sha'],2,pins['tool']['sha'])]
dump('INPUTS.json', {'package_commit':PACKAGE, 'task_id':'task16a4f1d3e9ca438396d9226ea3d13ffaa88150fe', 'issued':'owner18:19 combined review; explicit /new overrides task reuse-context', 'pins':pins, 'package':package, 'dependencies':dependencies, 'task_documents_sha256':{n:sha((G/'research/challenge-8/kani-k1'/n).read_bytes()) for n in ('TASK-CH8-S2-R4-R2-TIMEOUT-DELTA-W14.md','TASK-CH8-S2-R4-R2-VALIDATE-TIMEOUT-W13.md')}})
dump('CHECKS.json', {'status':'PASS', 'scope':'FINAL_COMBINED_SIX_PATH_DELTA_ONLY', 'checks':checks, 'static_helper_reuse':'Pinned validate_package.py replay/shallow only; main not executed; no input writes'})
print('PASS: exact package/dependencies/pins, six-path delta, full inventories, payload/maps/protected bytes, gate inheritance, workflow mutations, timing records, 6 patch replays, shallow7/5/2. No suite or timing rerun.')
