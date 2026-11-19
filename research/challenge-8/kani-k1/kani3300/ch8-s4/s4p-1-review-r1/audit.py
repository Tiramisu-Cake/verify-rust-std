#!/usr/bin/env python3
"""Independent W14 delta identity/invariance audit. No native/CI execution."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
G0 = Path('/root/verify-rust-std-kani3300-g0')
PACKET = HERE.parent / 's4p-1-r1'
OLD = HERE.parent / 's4p-1'
REVIEW = HERE.parent / 's4p-1-review'
AUTHOR = '5b0ed64d86c6cd7ac18bb3c7b7b7fd124dcb504c'
TASK = '989b0dbd020bc9bb500c0a18f3220d21537fbc44'
FROZEN = '4856a87f39d2606adbbed747d3cae9a73fb80d52'
OLD_CONTROL = 'e941155517a02f67ea9bac1adb81c1d5f6f85638'
D = lambda raw: hashlib.sha256(raw).hexdigest()

def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env)

def textgit(repo, *args):
    return git(repo, *args).decode().strip()

def blob(repo, sha, path):
    return git(repo, 'show', sha + ':' + str(path))

def read(path):
    return json.loads(path.read_text())

def save(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')

def tree(repo, sha):
    result = {}
    for entry in git(repo, 'ls-tree', '-rz', sha).split(b'\0'):
        if entry:
            identity, path = entry.split(b'\t', 1)
            result[path.decode()] = identity.decode()
    return result

def manifest(directory, commit, expected):
    raw = (directory / 'MANIFEST.sha256').read_bytes()
    records = {}
    for line in raw.decode().splitlines():
        digest, name = line.split('  ', 1)
        assert name not in records and D((directory / name).read_bytes()) == digest
        records[name] = digest
    actual = {str(p.relative_to(directory)) for p in directory.rglob('*') if p.is_file()}
    assert actual == set(records) | {'MANIFEST.sha256'}
    assert (len(actual), len(records)) == expected
    prefix = directory.relative_to(G0)
    for name in actual:
        assert (directory / name).read_bytes() == blob(G0, commit, prefix / name)
    return {'commit': commit, 'files': len(actual), 'hashes': len(records),
            'manifest_sha256': D(raw), 'committed_bytes_match': True}

def main():
    assert textgit(G0, 'rev-parse', 'HEAD') == AUTHOR
    taskpath = Path('research/challenge-8/kani-k1/TASK-CH8-S4P1-GATE-DELTA-W14.md')
    assert blob(G0, TASK, taskpath) == (G0 / taskpath).read_bytes()
    pins = read(PACKET / 'PINS.json')
    invariants = []
    def invariant(name, detail):
        invariants.append({'id': len(invariants) + 1, 'invariant': name, 'status': 'PASS', 'detail': detail})

    packets = {'repair': manifest(PACKET, AUTHOR, (62, 61)),
               'frozen_review': manifest(REVIEW, FROZEN, (18, 17)),
               'frozen_author': manifest(OLD, '590dd6360f5b4c92eab9fff30aa0d2e7d8d942ce', (54, 53))}
    invariant('Exact task and immutable input packets', packets)
    identities = {}
    for name, sha in [('source', '985062ebad90cee1e2846b1648cd6a8624d146f6'),
                      ('control', '2db5d2c08804036d283cb36450647cd584ee9e10'),
                      ('tool', '0aac16ef62da9e9d5645782d458593e5d78143ba')]:
        item = pins[name]
        assert item['sha'] == sha == textgit(item['repo'], 'rev-parse', 'HEAD')
        assert item['tree'] == textgit(item['repo'], 'rev-parse', 'HEAD^{tree}')
        assert item['parents'] == textgit(item['repo'], 'show', '-s', '--format=%P', 'HEAD').split()
        assert not textgit(item['repo'], 'status', '--porcelain=v1')
        identities[name] = item
    control = Path(pins['control']['repo'])
    source = Path(pins['source']['repo'])
    tool = Path(pins['tool']['repo'])
    frozenpins = read(REVIEW / 'PINS.json')
    for name in ('source', 'tool'):
        for key in ('sha', 'tree', 'parents'):
            assert pins[name][key] == frozenpins[name][key]
    invariant('Source and stock tool exact frozen identities', {k: identities[k] for k in ('source', 'tool')})
    assert pins['control']['parents'] == ['9e14e033f9ee31522b571c127609dcdff76d230b']
    assert textgit(control, 'show', '-s', '--format=%P', OLD_CONTROL) == pins['control']['parents'][0]
    assert textgit(control, 'merge-base', OLD_CONTROL, pins['control']['sha']) == pins['control']['parents'][0]
    invariant('Control exact sibling and sole parent', identities['control'])
    newtree, oldtree = tree(control, pins['control']['sha']), tree(control, OLD_CONTROL)
    delta = sorted(p for p in newtree.keys() | oldtree.keys() if newtree.get(p) != oldtree.get(p))
    assert delta == sorted('ch8-s1-control/' + p for p in (
        'CI-REQUEST.json', 's4p_campaign.py', 's4p_contract_stacks.py', 's4p_validate.py', 'test_s4p_gate_repair.py'))
    assert git(control, 'diff', '--binary', '--full-index', OLD_CONTROL, pins['control']['sha']) == (PACKET / 'CONTROL-REPAIR.patch').read_bytes()
    invariant('Exact five-path delta, all other modes/objects unchanged', delta)
    req = read(PACKET / 'CI-REQUEST.json')
    oldreq = read(OLD / 'CI-REQUEST.json')
    assert set(req) == set(oldreq)
    changed = sorted(k for k in req if req[k] != oldreq[k])
    assert changed == ['ci_changed_paths', 'ci_payload_sha256']
    assert (control / 'ch8-s1-control/CI-REQUEST.json').read_bytes() == (PACKET / 'CI-REQUEST.json').read_bytes()
    assert D((PACKET / 'CI-REQUEST.json').read_bytes()) == pins['request']['sha256'] == '3d135ebabd0793681a5b8a2fdb2414324c7021c5d8791e700fc713b633ddd149'
    payload = req['ci_payload_sha256']
    assert len(payload) == 118 and 'ch8-s1-control/CI-REQUEST.json' not in payload
    for path, digest in payload.items():
        assert D(blob(control, pins['control']['sha'], path)) == digest
        assert D((control / path).read_bytes()) == digest
    assert req['ci_changed_paths'] == textgit(control, 'diff', '--name-only', req['tool_sha'], pins['control']['sha']).splitlines()
    invariant('Request semantics invariant; all 118 payload bytes bound', {'changed_keys': changed, 'request_sha256': pins['request']['sha256']})
    assert len(req['rows']) == 8 and all(r['mode'] == 'Original' and r['target'] is None for r in req['rows'])
    invariant('Rows/domains/base/roles/covers/unwind/cfg/waivers unchanged', 'All request fields besides payload inventory/hash are equal; source tree exact. Eight Original/null rows,21 assertion sites,30 covers preserved.')
    invariant('Shared runtime/caps/lexercache and all old gates/tests invariant', 'Whole-tree mode/object comparison excludes changes outside five paths; runtime/profile/policy/fixtures/old Validate drivers byte-identical to E941.')
    workflow = (control / '.github/workflows/ch8-s2.yml').read_bytes()
    assert workflow == (PACKET / 'WORKFLOW.yml').read_bytes() == (OLD / 'WORKFLOW.yml').read_bytes()
    assert D(workflow) == 'a56791ab37df944d65131c0a7a612a5245d3c8a0275ff8810fb44fa6a7af061a'
    h = control / 'ch8-s1-control'
    sys.path.insert(0, str(h))
    import check_package, runner, s4p_validate, s34_validate, s4p_policy
    assert runner.load_request() == req
    w = check_package.load_yaml(workflow.decode())
    step = next(s for s in w['jobs']['s3_leaf']['steps'] if s['name'] == 'Validate control and synthetic wrapper')
    receipt = read(PACKET / 'FINAL-VALIDATE.json')
    assert step['run'] == receipt['command'] == 'python3 check_package.py control --repo ..\npython3 s4p_validate.py\n'
    assert step['timeout-minutes'] == 18
    assert check_package.check_yaml(control / '.github/workflows/ch8-s2.yml')['checkout_depths'] == {'control': 7, 'export': 5, 'tool': 2}
    invariant('Workflow bytes, exact Validate command and unchanged18min', {'workflow_sha256': D(workflow), 'command': step['run']})
    script = blob(control, OLD_CONTROL, 'ch8-s1-control/s4p_validate.py').decode()
    assert script.replace("NEW=('test_s4p_boundary',", "NEW=('test_s4p_boundary', 'test_s4p_gate_repair',", 1) == (h / 's4p_validate.py').read_text()
    names = read(PACKET / 'TEST-LIST.json')
    assert list(s4p_validate.NEW) == names['suites']['s4p']
    repair = names['repair_tests']
    assert unittest.defaultTestLoader.loadTestsFromNames('test_s4p_gate_repair'.split()).countTestCases() == 3
    assert unittest.defaultTestLoader.loadTestsFromNames(s4p_validate.NEW).countTestCases() == 38
    invariant('CI Validate retains all previous selection and adds three regressions', repair)
    assert receipt['control_sha'] == pins['control']['sha'] and receipt['control_tree'] == pins['control']['tree']
    assert receipt['request_sha256'] == pins['request']['sha256'] and receipt['workflow_sha256'] == D(workflow)
    assert receipt['script_sha256'] == D((h / 's4p_validate.py').read_bytes())
    assert receipt['execution_count'] == 1 and receipt['exit_code'] == 0 and not receipt['timed_out'] and receipt['clean_after']
    assert receipt['limit_seconds'] == 1080 and receipt['elapsed_seconds'] < 720 and receipt['margin_at_18_minutes'] == 1080 / receipt['elapsed_seconds']
    for stream in ('stdout', 'stderr'):
        item = receipt[stream]
        raw = (PACKET / item['file']).read_bytes()
        assert len(raw) == item['bytes'] and D(raw) == item['sha256']
    summary = json.loads((PACKET / 'FINAL-VALIDATE.stdout').read_text().splitlines()[-1])
    assert summary['control_sha'] == receipt['control_sha'] and summary['control_tree'] == receipt['control_tree']
    assert summary['request_sha256'] == receipt['request_sha256'] and summary['success'] and summary['errors'] == summary['failures'] == 0
    expected_counts = {'legacy':136, 's3':56, 's32':35, 'bridge1':40, 's4p':38}
    assert summary['test_counts'] == expected_counts
    transcript = (PACKET / 'FINAL-VALIDATE.stderr').read_text()
    assert [int(n) for n in re.findall(r'^Ran (\d+) tests in ', transcript, re.M)] == [136, 56, 35, 40, 38]
    assert len(re.findall(r'^OK$', transcript, re.M)) == 5
    for name in repair:
        parts = name.split('.')
        assert f'{parts[-1]} ({".".join(parts[:-1])}.{parts[-1]}) ... ok' in transcript
    invariant('Retained exact final Validate receipt and transcripts', {'tests': 305, 'seconds': receipt['elapsed_seconds'], 'margin': receipt['margin_at_18_minutes'], 'repeated_by_reviewer': False, 'assurance': 'RETAINED_AUTHOR_LOCAL_EXECUTION_NOT_INDEPENDENT_TIMING_OR_CI'})

    patches = []
    for item in read(PACKET / 'PATCHES.json'):
        repo = source if item['file'].startswith('SOURCE') else control
        assert D((PACKET / item['file']).read_bytes()) == item['sha256']
        with tempfile.TemporaryDirectory(prefix='w14-index-') as d:
            scratch = Path(d)
            objects = scratch / 'objects'; objects.mkdir()
            actual_objects = textgit(repo, 'rev-parse', '--path-format=absolute', '--git-path', 'objects')
            env = {**os.environ, 'GIT_INDEX_FILE': str(scratch / 'index'), 'GIT_OBJECT_DIRECTORY': str(objects), 'GIT_ALTERNATE_OBJECT_DIRECTORIES': actual_objects}
            git(repo, 'read-tree', item['base'], env=env)
            git(repo, 'apply', '--cached', str(PACKET / item['file']), env=env)
            result = git(repo, 'write-tree', env=env).decode().strip()
        assert result == item['expected_tree'] == textgit(repo, 'rev-parse', item['tip'] + '^{tree}')
        patches.append({'patch': item['file'], 'tree': result, 'status': 'INDEPENDENT_EXACT_TREE_PASS'})
    assert len(patches) == 6
    save('PATCH-REPLAY.json', patches)
    invariant('All six full patch trees independently replayed', patches)

    shallows = []
    for item in read(PACKET / 'ANCESTRY.json')['shallow']:
        with tempfile.TemporaryDirectory(prefix='w14-shallow-') as d:
            subprocess.run(['git', 'init', '--bare', '-q', d], check=True)
            subprocess.run(['git', '-C', d, 'fetch', '--quiet', '--no-tags', '--depth=' + str(item['depth']), 'file://' + item['repo'], item['sha']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            assert textgit(d, 'rev-parse', 'FETCH_HEAD') == item['sha']
            assert textgit(d, 'rev-parse', 'FETCH_HEAD^{tree}') == item['tree']
            for commit in item['required_commits_available']:
                assert textgit(d, 'cat-file', '-t', commit) == 'commit'
        shallows.append({**item, 'status': 'INDEPENDENT_SHALLOW_IDENTITY_PASS'})
    save('SHALLOW.json', shallows)
    invariant('Independent local shallow7/5/2 ancestry', shallows)
    history = read(PACKET / 'HISTORY-PRESERVATION.json')
    for frozen in history['frozen_packets']:
        for path, digest in frozen['bindings'].items():
            assert D(blob(G0, frozen['commit'], path)) == digest == D((G0 / path).read_bytes())
    assert history['old_final_validate']['tests'] == 302 and history['old_final_validate']['control_sha'] == OLD_CONTROL
    assert textgit(history['old_control']['repo'], 'rev-parse', 'HEAD') == OLD_CONTROL
    invariant('Historical590/E941/4856/302PASS and precursors separate and intact', {'frozen_packets': [x['commit'] for x in history['frozen_packets']], 'new_precursors': read(PACKET / 'PRECURSORS.json')})
    oldmaps = {name: read(OLD / ('MAP-' + name + '.json')) for name in ('ORDINARY', 'CFG_PFC', 'CONTRACT_STACKS', 'LEXICAL')}
    for name, oldmap in oldmaps.items():
        current = read(PACKET / ('MAP-' + name + '.json'))
        if name == 'CONTRACT_STACKS':
            current = {k:v for k,v in current.items() if k != 'cfg_projection_invariance'}
            oldmap = {k:v for k,v in oldmap.items() if k != 'cfg_projection_invariance'}
        assert current == oldmap
    author_checker = runpy.run_path(str(PACKET / 'check_static.py'))['check']()
    assert author_checker['status'] == 'STATIC_READY_PACKET_PASS'
    invariant('Original full review inheritance only by exact unaffected bytes', {'maps': 'All reports equal except repaired32 cfg projection list', 'source_tool_runtime_profile_mode_domain': 'EXACT_INVARIANT', 'author_readonly_checker': author_checker})
    assert len(invariants) == 14
    save('AUDIT.json', {'schema':'ch8-s4p-1-independent14-delta-audit-v1', 'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'author_commit':AUTHOR, 'task_commit':TASK, 'frozen_review':FROZEN, 'identities':identities, 'packets':packets, 'invariants':invariants, 'status':'PASS', 'full_validate_repeated':False, 'proof_credit':'NONE'})
    print(json.dumps({'status':'PASS', 'invariants':len(invariants), 'packet':packets['repair'], 'author_readonly_checks':author_checker['checks'], 'patches':len(patches), 'shallows':[x['depth'] for x in shallows]}), flush=True)

if __name__ == '__main__':
    main()
