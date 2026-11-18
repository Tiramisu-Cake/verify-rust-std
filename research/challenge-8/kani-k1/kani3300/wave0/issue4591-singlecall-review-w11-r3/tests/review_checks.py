#!/usr/bin/env python3
"""Reviewer offline identity/replay/inventory checks. No Rust or CI execution.

Uses only Git, Python and the installed YAML reader. Temporary indexes and
objects live outside the source repository. Prints evidence; changes no input.
"""
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import yaml

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parents[1]
G0 = Path('/root/verify-rust-std-kani3300-g0')
SRC = Path('/root/kani-issue4591-singlecall-r3-w15')
REL = 'research/challenge-8/kani-k1/kani3300/wave0/issue4591-singlecall-r3'
PKG = G0 / REL
DELIVERY = '5162af47e12611de4102ba20b0135b17c1d79d7d'
TASK = '98dde2de28e13381092f20c082ba90f90ce34773'
C = 'f82934ca97caaa1270d5279054aa950173868be5'
B = '6fca00af805b5c62b58e3e3f29eef183d6939907'
M = '969f4648980a8e66cd0ca32fd3e714a55ac32cef'
TREE = '2ff34bc99ec3fe63579202c196f0ca288e318919'
checks, replays = [], []


def run(argv, **kwargs):
    return subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          check=False, **kwargs)


def git(repo, *args):
    p = run(['git', '-C', str(repo), *args])
    if p.returncode:
        raise RuntimeError((p.args, p.returncode, p.stderr.decode()))
    return p.stdout


def check(name, ok, detail=None):
    checks.append(dict(name=name, status='PASS' if ok else 'FAIL', detail=detail))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(name):
    return json.loads((PKG / name).read_bytes())


def blob(ref, path):
    return git(SRC, 'show', ref + ':' + path)


manifest, pins = load('MANIFEST.json'), load('SOURCE-PINS.json')
committed = git(G0, 'ls-tree', '-r', '--name-only', DELIVERY, '--', REL).decode().splitlines()
actual = sorted(str(p.relative_to(G0)) for p in PKG.rglob('*') if p.is_file())
check('exact delivery has 38 files and complete working copy',
      len(committed) == 38 and actual == committed)
for path in committed:
    check('delivered bytes ' + path.removeprefix(REL + '/'),
          (G0 / path).read_bytes() == git(G0, 'show', DELIVERY + ':' + path))
check('manifest covers exactly 37 other files',
      set(manifest['files']) == {str(p.relative_to(PKG)) for p in PKG.rglob('*')
                                if p.is_file() and p.name != 'MANIFEST.json'})
for path, info in manifest['files'].items():
    data = (PKG / path).read_bytes()
    check('manifest seal ' + path, sha(data) == info['sha256'] and len(data) == info['bytes'])
check('CI request exact owner pin', sha((PKG / 'CI-REQUEST.json').read_bytes()) ==
      '8fb98acee9861fb9a94133d060d568fd0b7735d5840fcd9fdf7fc2fc6aacf4bc')
check('task review bytes unchanged',
      (G0 / 'research/challenge-8/kani-k1/TASK-KANI-4591-SINGLE-CALL-REVIEW-W11.md').read_bytes() ==
      git(G0, 'show', TASK + ':research/challenge-8/kani-k1/TASK-KANI-4591-SINGLE-CALL-REVIEW-W11.md'))
for item in load('inputs/FROZEN-INPUTS.json')['files']:
    data = git(G0, 'show', item['commit'] + ':' + item['path'])
    check('frozen history ' + item['path'],
          sha(data) == item['sha256'] and (G0 / item['path']).read_bytes() == data)
check('source exact HEAD/tree/soleparent/clean',
      git(SRC, 'rev-parse', 'HEAD', 'HEAD^{tree}', 'HEAD^').decode().splitlines() == [C, TREE, B]
      and git(SRC, 'show', '-s', '--format=%P', C).decode().strip() == B
      and not git(SRC, 'status', '--porcelain'))
check('base sole parent main', git(SRC, 'show', '-s', '--format=%P', B).decode().strip() == M)
changed = git(SRC, 'diff', '--name-only', B, C).decode().splitlines()
check('two fixtures only', changed == pins['repair_changed_paths'] and len(changed) == 2)
check('source diff whitespace', run(['git', '-C', str(SRC), 'diff', '--check', B, C]).returncode == 0)
for directory in ['kani-compiler', 'kani-driver', '.github', 'scripts', 'library']:
    check('whole tree unchanged from failed base ' + directory,
          git(SRC, 'rev-parse', B + ':' + directory) == git(SRC, 'rev-parse', C + ':' + directory))
for directory in ['.github', 'scripts', 'library']:
    check('whole tree unchanged from reviewed main ' + directory,
          git(SRC, 'rev-parse', M + ':' + directory) == git(SRC, 'rev-parse', C + ':' + directory))
for path, info in {**pins['protected_files'], **pins['all_workflows']}.items():
    check('main/base/candidate protected ' + path,
          blob(M, path) == blob(B, path) == blob(C, path)
          and sha(blob(C, path)) == info['sha256'])
for path, refs in pins['file_pins'].items():
    for ref, info in refs.items():
        check('source file pin ' + path + '@' + ref[:8],
              sha(blob(ref, path)) == info['sha256'] and
              git(SRC, 'rev-parse', ref + ':' + path).decode().strip() == info['blob'])
excerpts = load('SOURCE-EXCERPTS.json')['excerpts']
for e in excerpts:
    # The package stores joined source lines, omitting the range's final LF.
    # Compare that declared representation without dropping content/blank lines.
    lines = blob(e['ref'], e['path']).decode().splitlines()
    actual_blob = git(SRC, 'rev-parse', e['ref'] + ':' + e['path']).decode().strip()
    check('source excerpt ' + e['path'] + ':' + str(e['start_line']) + '@' + e['ref'][:8],
          '\n'.join(lines[e['start_line'] - 1:e['end_line']]) == e['text'] and
          ('blob' not in e or actual_blob == e['blob']), {'git_blob': actual_blob})

# Actual independent replays: private object store and index, source is read-only.
common = Path(git(SRC, 'rev-parse', '--git-common-dir').decode().strip())
if not common.is_absolute():
    common = (SRC / common).resolve()
with tempfile.TemporaryDirectory(prefix='same11-r3-replay-') as tmp:
    repo = Path(tmp) / 'replay.git'
    init = run(['git', 'init', '--bare', '--quiet', str(repo)])
    check('temporary replay repository', init.returncode == 0)
    env = dict(os.environ, GIT_ALTERNATE_OBJECT_DIRECTORIES=str(common / 'objects'))
    for start, patches in [(B, ['repair.patch']), (M, ['full-main.patch']),
                            (M, ['compiler-main.patch', 'regression-main.patch'])]:
        commands = [['read-tree', start]]
        for patch in patches:
            commands.extend([['apply', '--cached', '--check', str(PKG / patch)],
                             ['apply', '--cached', str(PKG / patch)]])
        commands.append(['write-tree'])
        receipts = []
        for args in commands:
            argv = ['git', '--git-dir', str(repo), *args]
            p = run(argv, env=env)
            receipts.append(dict(argv=argv, exit=p.returncode, stdout=p.stdout.decode(),
                                 stderr=p.stderr.decode()))
        tree = receipts[-1]['stdout'].strip()
        check('independent patch replay ' + '+'.join(patches),
              all(r['exit'] == 0 for r in receipts) and tree == TREE, tree)
        replays.append(dict(start=start, patches=patches, tree=tree, commands=receipts))

# Inspect exact workflow projections, including job conditions/retries/step order.
inventory = load('WORKFLOW-INVENTORY.json')['workflows']
ci = load('CI-REQUEST.json')
for path, parsed in inventory.items():
    check('fresh workflow parse ' + path,
          yaml.load(blob(M, path), Loader=yaml.BaseLoader) == parsed)
for name, jobs in ci['native_jobs'].items():
    check('full native job definitions ' + name,
          yaml.load(blob(C, '.github/workflows/' + name), Loader=yaml.BaseLoader)['jobs'] == jobs)
check('full push scope 5+4+2+1 instances',
      ci['native_instances'] == 12 and set(ci['native_jobs']) == {'kani.yml', 'format-check.yml', 'deny.yml'}
      and set(ci['native_jobs']['kani.yml']['regression']['strategy']['matrix']['os']) ==
      {'macos-15-intel', 'macos-15', 'ubuntu-22.04', 'ubuntu-24.04', 'ubuntu-24.04-arm'})

# Minimal independent function inventory: top-level fixture declarations only.
# It is deliberately not Rust parsing, name resolution, or generated MIR.
def declarations(data):
    text = data.decode()
    result = {}
    for match in re.finditer(r'(?m)^((?:#\[[^\n]*\]\n)*)fn (\w+)[^\n{]*\{', text):
        end = text.find('\n}', match.end()) + 2
        if end < match.end():
            raise ValueError('fixture grammar requires a top-level closing brace')
        result[match[2]] = dict(attrs=match[1].strip().splitlines(),
                               text=text[match.start():end])
    return result

rows, pfc_rows, modified = [], [], []
oracle = {(r['path'], r['harness']): r for r in load('REGRESSION-ORACLE.json')['harnesses']}
for path in pins['test_paths']:
    old, new = blob(B, path), blob(C, path)
    if path.endswith('.expected'):
        check('all golden bytes unchanged ' + path, old == new)
        continue
    before, after = declarations(old), declarations(new)
    check('existing declarations retained ' + path, before.keys() <= after.keys())
    for name in before:
        if before[name] != after[name]:
            modified.append([path, name])
    for name, item in after.items():
        if not any(a.startswith('#[kani::proof') for a in item['attrs']):
            continue
        row = dict(path=path, harness=name, attributes=item['attrs'],
                   unchanged=before.get(name) == item)
        rows.append(row)
        declared = oracle.get((path, name))
        check('oracle declaration ' + path + ':' + name,
              declared is not None and item['attrs'] == declared['attributes']
              and declared['native_repair'] == 'NOT_RUN')
        if any(a.startswith('#[kani::proof_for_contract(') for a in item['attrs']):
            pfc_rows.append(row)
check('38 harnesses, 13 PFC, 36 unchanged', len(rows) == 38 and len(pfc_rows) == 13
      and sum(r['unchanged'] for r in rows) == 36 and len(oracle) == 38)
check('only two old harness declarations modified', sorted(modified) == sorted([
    ['tests/kani/FunctionContracts/ordinary_stub.rs', 'replacement_contract_target'],
    ['tests/expected/function-contract/ordinary_stub_fail.rs', 'replacement_provider_postcondition']]))
positive = [{'x': x, 'provider_result': x + 3, 'provider_post': True, 'caller_post': True,
             'u8_no_overflow': x + 3 <= 255} for x in range(16)]
negative = dict(x=1, provider_result=1, provider_ensures_zero=False,
                caller_ensures_identity=True, no_requires=True)
check('bounded positive arithmetic admitted domain', all(r['u8_no_overflow'] for r in positive))
check('bounded negative provider/caller distinction',
      negative['provider_result'] != 0 and negative['provider_result'] == negative['x'])

native = load('native/CONNECTED-METADATA.json')['runs']
jobs = [j for r in native for j in r['jobs']]
counts = dict(collections.Counter(j['conclusion'] for j in jobs))
check('compact native projection accounts all12 terminal jobs', len(jobs) == 12 and
      len({j['id'] for j in jobs}) == 12 and counts == {'success': 7, 'failure': 1, 'cancelled': 4}
      and all(r['selected_fields']['head_sha'] == B for r in native))
check('compact native workflow outcomes',
      {r['selected_fields']['id']: r['selected_fields']['conclusion'] for r in native} ==
      {44399789701: 'failure', 44399789719: 'success', 44399789794: 'success'})
gate_receipts = []
for head in [C, B]:
    argv = [sys.executable, '-B', str(PKG / 'check_push_head.py'), str(SRC), head]
    p = run(argv)
    data = json.loads(p.stdout)
    check('actual gate rejects unpublished/frozen head ' + head[:8],
          p.returncode == 1 and data['status'] == 'REJECT' and not data['authorization_granted'])
    gate_receipts.append(dict(argv=argv, exit=p.returncode, result=data))
check('source still clean after read-only review', not git(SRC, 'status', '--porcelain'))
result = dict(status='PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL',
              package=DELIVERY, source=C, tree=TREE, checks=checks, replays=replays,
              harness_inventory=rows, pfc_inventory=pfc_rows, source_arithmetic=dict(
                  positive=positive, negative=negative), native_projection_counts=counts,
              actual_gate_rejections=gate_receipts,
              assurance='Independent static Git/source/replay checks; committed connected metadata projection only',
              native_repair='NOT_RUN', limitations=[
                  'No Rust parsing/typechecking/name resolution, expansion, generated MIR or verifier execution.',
                  'Arithmetic rows are reviewer calculations tied to manually reviewed source, not program execution.',
                  'No fresh native metadata query, raw log, archive, or configured-binary attestation.',
                  'Rejected actual heads and metadata mocks do not establish a valid future final-head receipt.'])
print(json.dumps(result, indent=2))
sys.exit(result['status'] != 'PASS')
