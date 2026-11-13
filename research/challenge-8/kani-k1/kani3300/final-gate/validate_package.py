#!/usr/bin/env python3
"""Read-only Git/Python preparation checks; never a Rust/proof tool invocation."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
C1 = Path('/root/kani-fix-3300-worker14')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def check(condition, message):
    if not condition:
        raise ValueError(message)


def read(name):
    return json.loads((HERE / name).read_text())


def source(root, record, tree_key='tree'):
    check(git(root, 'rev-parse', 'HEAD').decode().strip() == record['sha'], str(root) + ' HEAD')
    if tree_key in record:
        check(git(root, 'rev-parse', 'HEAD^{tree}').decode().strip() == record[tree_key], str(root) + ' tree')
    check(not git(root, 'status', '--porcelain', '--untracked-files=all').strip(), str(root) + ' dirty')
    for path, digest in record.get('files', {}).items():
        check(hashlib.sha256((root / path).read_bytes()).hexdigest() == digest, str(root) + ' hash: ' + path)


def main():
    manifest = read('EXPORT-MANIFEST.json')
    export = manifest['final_export']
    check(export['sha'] == '1658f4cadfa83139e41180ce3865e23f79d889aa', 'frozen C1 commit')
    check(export['tree'] == 'bfb5eb9db13ffb91ec4585b7c7ef41ddfe0008fb', 'frozen C1 tree')
    source(C1, export)
    for path, tree in export['subtrees'].items():
        check(git(C1, 'rev-parse', 'HEAD:' + path).decode().strip() == tree, 'C1 subtree ' + path)
    std = Path('/root/verify-rust-std-kani-traitpfc')
    source(std, manifest['smallsort'])
    check(git(std, 'rev-parse', 'HEAD:library').decode().strip() == manifest['smallsort']['library_tree'], 'std library tree')
    import yaml
    records = {}
    for name in ('CI-OVERLAY.json', 'REPLAY-OVERLAY.json', 'REPLAY-CI-OVERLAY.json'):
        record = read(name)
        clone = Path(record['clone'])
        source(clone, {k: record[k] for k in ('sha', 'tree')})
        diff = git(clone, 'diff', '--binary', record['base'], record['sha'])
        check(diff == (HERE / record['patch']).read_bytes(), name + ' patch drift')
        check(hashlib.sha256(diff).hexdigest() == record['patch_sha256'], name + ' patch digest')
        subprocess.run(['git', '-C', str(clone), 'diff', '--check', record['base'], record['sha']], check=True)
        changed = git(clone, 'diff', '--name-only', record['base'], record['sha']).decode().splitlines()
        if name == 'REPLAY-OVERLAY.json':
            check(set(changed) == {'library/core/src/slice/sort/shared/smallsort/verify.rs', 'library/core/src/slice/sort/shared/smallsort/verify/replay_uninit_controls.rs'}, 'std test overlay scope')
        else:
            check(record['base'] == export['sha'], name + ' C1 base')
            check(git(clone, 'rev-parse', 'HEAD^').decode().strip() == export['sha'], name + ' direct parent')
            prefix = 'scripts/kani3300-gate/' if name == 'CI-OVERLAY.json' else 'scripts/kani3300-replay/'
            check(all(p.startswith(('.github/workflows/', prefix)) for p in changed), name + ' CI-only scope/export preservation')
            workflows = list((clone / '.github/workflows').glob('*.yml'))
            check(len(workflows) == 1, name + ' stock workflow leakage')
            workflow = yaml.load(workflows[0].read_text(), Loader=yaml.BaseLoader)
            check(set(workflow['on']) == {'workflow_dispatch'}, name + ' trigger')
            subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-s', prefix, '-p', 'test_*.py'], cwd=clone, check=True)
        records[name] = record
    a = Path(records['CI-OVERLAY.json']['clone'])
    binding = json.loads((a / 'scripts/kani3300-gate/binding.json').read_text())
    check(binding['files'] == export['files'] and binding['subtrees'] == export['subtrees'], 'Gate A binding drift')
    code = 'import sys; sys.path.insert(0,sys.argv[1]); from receipt import validate_binding; import json; validate_binding(json.load(open(sys.argv[2])))'
    subprocess.run([sys.executable, '-B', '-c', code, str(a / 'scripts/kani3300-gate'), str(a / 'scripts/kani3300-gate/binding.json')], cwd=C1, check=True)
    replay = read('REPLAY-REQUEST.json')
    check(replay['status'] == 'NOT_RUN_C1_FROZEN' and replay['tool_export_sha'] == export['sha'] and replay['tool_export_tree'] == export['tree'], 'replay C1 binding')
    check(replay['run_budget'] is None and replay['authorization'] == 'PREPARATION_ONLY', 'no dispatch authorization')
    check(len(replay['roots']) == 12, 'twelve root/profile rows')
    rows = {r['id']: r for r in replay['roots']}
    for row in rows.values():
        check(row['status'] == 'NOT_RUN' and row['generated_property_binding'] is None, 'no invented result/property binding')
        argv = row['argv']
        check(argv[-3:] == ['--cbmc-args', '--object-bits', '12'], 'object bits')
        check('--no-assert-contracts' in argv and 'function-contracts' in argv, 'contracts')
        check(('uninit-checks' in argv) == row['uninit'], 'uninit profile')
        pair = rows[row['companion']]
        check(pair['selector'] == row['selector'] and pair['source_unwind'] == row['source_unwind'], 'ON/OFF root/unwind drift')
        check(row['environment'] == pair['environment'], 'ON/OFF cfg drift')
        normalized = [x.replace(row['id'], '<ROW>') for x in argv]
        paired = [x.replace(pair['id'], '<ROW>') for x in pair['argv']]
        for values in (normalized, paired):
            if 'uninit-checks' in values:
                index = values.index('uninit-checks')
                del values[index - 1:index + 1]
        check(normalized == paired, 'ON/OFF flags drift')
    b = Path(records['REPLAY-CI-OVERLAY.json']['clone'])
    check((b / 'scripts/kani3300-replay/request.json').read_bytes() == (HERE / 'REPLAY-REQUEST.json').read_bytes(), 'Gate B embedded request drift')
    check((b / 'scripts/kani3300-replay/replay-test-only.patch').read_bytes() == (HERE / 'replay-test-only.patch').read_bytes(), 'Gate B embedded patch drift')
    check(json.loads((b / 'scripts/kani3300-replay/c1-source-binding.json').read_text()) == binding, 'Gate B source binding drift')
    oracle = read('REPLAY-ORACLES.json')
    check(oracle['tool_export_sha'] == export['sha'] and oracle['tool_export_tree'] == export['tree'], 'oracle C1 identity')
    check(len(oracle['strong_oracles']) == 8 and len(oracle['modes']) == 6 and len(oracle['composition']['roots']) == 7, 'oracle inventory')
    for path, digest in oracle['source_trace_hashes'].items():
        check(hashlib.sha256((C1 / path).read_bytes()).hexdigest() == digest, 'source trace hash')
    strong = json.loads((C1 / 'tests/json-handler/uninit-contract-oracles/oracles.json').read_text())
    expected = [{'id': r['id'], 'input': r['input'], 'sha256': r['sha256'], 'root': r['root'], 'verdict': r['verdict'], 'binding_status': r['binding']['status']} for r in strong['cases']]
    check(oracle['strong_oracles'] == expected, 'exact frozen strong oracle summaries')
    for row in strong['cases']:
        check(hashlib.sha256((C1 / row['input']).read_bytes()).hexdigest() == row['sha256'], 'strong oracle input hash')
    modes = json.loads((C1 / 'tests/json-handler/uninit-contract-mode-boundaries/roots.json').read_text())
    check(oracle['modes'] == modes['roots'], 'exact frozen mode expectations')
    result = read('RESULT-template.json')
    check(result['gate_a']['status'] == result['gate_b']['status'] == 'NOT_RUN', 'execution NOT_RUN')
    print('STATIC_PACKAGE_OK; Python synthetic tests only; proof/CI/shell runtime NOT_RUN')


if __name__ == '__main__':
    main()
