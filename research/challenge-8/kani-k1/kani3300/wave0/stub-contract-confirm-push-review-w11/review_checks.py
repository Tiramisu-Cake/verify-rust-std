#!/usr/bin/env python3
"""Independent W11 push delta review: Git/static/Python mocks only."""
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PACKET = HERE.parent / 'stub-contract-confirm-push'
OLD = HERE.parent / 'stub-contract-confirm'
REPO = HERE.parents[5]
PACKAGE = '5bb7ec9a01099148242421b0eb837c496e209c66'
CODE = PACKET / 'source/tests/script-based-pre/stub-contract-confirm'
sys.path.insert(0, str(CODE))
import runner
import final_head
import push_identity
import check_service as samples
import yaml


def command(argv, cwd=None, env=None):
    return subprocess.check_output(argv, cwd=cwd, env=env, stderr=subprocess.PIPE)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    checks = []
    evidence = {'scope': 'STATIC_PYTHON_DISPOSABLE_GIT_MOCK_ONLY'}

    def checked(label, condition):
        assert condition, label
        checks.append(label)

    pins = read(PACKET / 'PINS.json')
    control = Path(pins['control']['worktree'])
    stock = Path(pins['stock']['worktree'])
    def git(*args, cwd=control):
        return command(['git', *args], cwd).decode().strip()
    relative = str(PACKET.relative_to(REPO))
    tracked = git('ls-tree', '-r', '--name-only', PACKAGE, '--', relative, cwd=REPO).splitlines()
    files = sorted(p for p in PACKET.rglob('*') if p.is_file())
    checked('exact package 37 files', len(files) == len(tracked) == 37)
    inventory = []
    for file in files:
        name = str(file.relative_to(PACKET))
        raw = command(['git', 'show', PACKAGE + ':' + str(file.relative_to(REPO))], REPO)
        checked('committed package bytes ' + name, raw == file.read_bytes())
        inventory.append({'path': name, 'sha256': sha(raw), 'bytes': len(raw)})
    manifest = read(PACKET / 'MANIFEST.json')['files']
    checked('36 manifest hashes exact coverage', len(manifest) == 36 and
            {x['path'] for x in manifest} == {x['path'] for x in inventory} - {'MANIFEST.json'})
    for entry in manifest:
        checked('manifest identity ' + entry['path'], entry in inventory)
    expected = {'request_sha256': '45b074506bd6e40e2f25bc1fc3603d1491bbbfda4c7a4295e40ec785cecb651c',
                'profile_sha256': 'ceb930a5b7764799880ac48ad6318bbaf6e14d6af70ea98abbe9da82107af148',
                'workflow_sha256': '720cc99642dfdce815773145d0d37820c29cf1f8e85b4cec87e70247dfff8edd'}
    checked('owner exact digest pins', all(pins[k] == v for k, v in expected.items()))
    checked('owner exact control pins', pins['control']['head'] == 'e9f0e9a38bf679fead630c44eec3bc08ebb9202b'
            and pins['control']['tree'] == '76ffe2048b88d45c759d0b297362c2c4981e7ad6'
            and pins['control']['parent'] == runner.BASE)
    checked('canonical request', sha(runner.canonical(pins['request_binding'])) == expected['request_sha256'])
    for label, root in [('control', control), ('stock', stock)]:
        checked(label + ' clean exact Git identities', git('status', '--porcelain', cwd=root) == '' and
                git('rev-parse', 'HEAD', cwd=root) == pins[label]['head'] and
                git('rev-parse', 'HEAD^{tree}', cwd=root) == pins[label]['tree'] and
                git('show', '-s', '--format=%P', 'HEAD', cwd=root) == pins[label]['parent'])
    for commit, path in [(pins['prior']['package_commit'], OLD),
                         (pins['prior']['review_commit'], HERE.parent / 'stub-contract-confirm-review-w11'),
                         (pins['prior']['old_GO_commit'], HERE.parent / 'stub-contract-confirm-go')]:
        rel = str(path.relative_to(REPO))
        checked('historical object immutable ' + path.name,
                git('rev-parse', commit + ':' + rel, cwd=REPO) == git('rev-parse', 'HEAD:' + rel, cwd=REPO)
                and git('diff', 'HEAD', '--', rel, cwd=REPO) == '')
    with tempfile.TemporaryDirectory(prefix='w11-push-patch-') as temp:
        replay = Path(temp) / 'repo'
        command(['git', 'clone', '-q', '--shared', '--no-checkout', str(control), str(replay)])
        for patch_name, base in [('control.patch', runner.BASE),
                                 ('trigger-delta.patch', pins['prior']['control_commit'])]:
            command(['git', 'read-tree', base], replay)
            command(['git', 'apply', '--cached', str(PACKET / patch_name)], replay)
            checked(patch_name + ' replay exact resulting tree',
                    git('write-tree', cwd=replay) == pins['control']['tree'])
    old_code = OLD / 'source/tests/script-based-pre/stub-contract-confirm'
    for name in ('Cargo.lock', 'Cargo.toml', 'src/lib.rs', 'service.py', 'workflow_checks.py'):
        checked('byte invariant ' + name, (CODE / name).read_bytes() == (old_code / name).read_bytes())
    for name in ('ORACLES.md', 'result.schema.json', 'SOURCES.json'):
        checked('byte invariant ' + name, (PACKET / name).read_bytes() == (OLD / name).read_bytes())
    def functions(path):
        return {n.name: ast.dump(n, include_attributes=False) for n in ast.parse(path.read_text()).body
                if isinstance(n, ast.FunctionDef)}
    before, after = functions(old_code / 'runner.py'), functions(CODE / 'runner.py')
    checked('runner AST only snapshot changes', before.keys() == after.keys() and
            [name for name in before if before[name] != after[name]] == ['snapshot'])
    checked('runner module constants invariant',
            [ast.dump(n) for n in ast.parse((old_code / 'runner.py').read_text()).body if isinstance(n, ast.Assign)] ==
            [ast.dump(n) for n in ast.parse((CODE / 'runner.py').read_text()).body if isinstance(n, ast.Assign)])
    old_workflow = yaml.load((OLD / 'source/.github/workflows/slow-tests.yml').read_text(), Loader=yaml.BaseLoader)
    new_workflow = yaml.load((PACKET / 'source/.github/workflows/stub-contract-confirm.yml').read_text(), Loader=yaml.BaseLoader)
    checked('only exact push event and branch filter', new_workflow.pop('on') ==
            {'push': {'branches': ['stub-contract-confirm-ci/**']}})
    old_workflow.pop('on')
    for key in ('SC_CONTROL_HEAD', 'SC_CONTROL_TREE', 'SC_REQUEST_SHA256'):
        old_workflow['jobs']['confirm']['env'].pop(key)
    checked('all workflow jobs otherwise invariant', old_workflow == new_workflow)
    request = read(PACKET / 'CI-REQUEST.json')
    prior_request = read(OLD / 'CI-REQUEST.json')
    for key in ('commands', 'environment', 'caps'):
        checked('request invariant ' + key, request[key] == prior_request[key])

    # Real reviewed Git objects in disposable clones; no source worktree edits.
    with tempfile.TemporaryDirectory(prefix='w11-push-independent-') as temp:
        temp = Path(temp)
        local_control, local_stock = temp / 'control', temp / 'stock'
        command(['git', 'clone', '-q', '--depth=2', control.as_uri(), str(local_control)])
        command(['git', 'clone', '-q', '--depth=2', stock.as_uri(), str(local_stock)])
        checked('real control depth2', git('rev-list', '--count', 'HEAD', cwd=local_control) == '2'
                and git('rev-parse', '--is-shallow-repository', cwd=local_control) == 'true')
        checked('real stock depth2', git('rev-list', '--count', 'HEAD', cwd=local_stock) == '2'
                and git('rev-parse', '--is-shallow-repository', cwd=local_stock) == 'true')
        event_path = temp / 'event.json'
        head, ref = pins['control']['head'], pins['publication']['ref']
        event = {'repository': {'full_name': 'Tiramisu-Cake/kani'}, 'ref': ref, 'after': head,
                 'before': '0' * 40, 'created': True, 'deleted': False, 'forced': False,
                 'head_commit': {'id': head, 'message': git('show', '-s', '--format=%B', head)}}
        event_path.write_text(json.dumps(event))
        clean = {k: v for k, v in os.environ.items() if not k.startswith(('SC_', 'GITHUB_'))}
        env = clean | {'GITHUB_EVENT_NAME': 'push', 'GITHUB_REPOSITORY': 'Tiramisu-Cake/kani',
                       'GITHUB_SHA': head, 'GITHUB_REF': ref, 'GITHUB_EVENT_PATH': str(event_path)}
        with patch.object(runner, 'ROOT', local_control), patch.object(runner, 'SOURCE', local_stock), \
                patch.object(runner, 'PROFILE', local_control / '.github/stub-contract-confirm/profile.json'), \
                patch.object(runner, 'OUT', temp / 'out'), patch.dict(os.environ, env, clear=True):
            observed = runner.snapshot()
            checked('real reviewed shallow snapshot canonical binding', not observed['problems'] and
                    observed['request'] == pins['request_binding'] and observed['request_sha256'] == expected['request_sha256'])
            def reject(label):
                with patch.object(runner, 'execute', side_effect=AssertionError('native build forbidden')):
                    checked(label + ' snapshot rejected', bool(runner.snapshot()['problems']))
                    checked(label + ' rejected before build', runner.main('build') == 1)
            for bad in ('pull_request', 'pull_request_target', 'workflow_dispatch', 'schedule', '', 'workflow_run'):
                with patch.dict(os.environ, {'GITHUB_EVENT_NAME': bad}):
                    reject('event ' + repr(bad))
            for bad in ('refs/heads/main', 'refs/tags/stub-contract-confirm-ci/test',
                        'refs/heads/stub-contract-confirm-ci', push_identity.PREFIX,
                        push_identity.PREFIX + 'x.lock', push_identity.PREFIX + 'a..b'):
                with patch.dict(os.environ, {'GITHUB_REF': bad}):
                    reject('ref ' + bad)
            for key, bad in [('created', None), ('created', 'true'), ('deleted', 0), ('forced', 0),
                             ('after', head.upper()), ('before', None), ('inputs', None)]:
                event_path.write_text(json.dumps(event | {key: bad}))
                reject('payload ' + key + '=' + repr(bad))
            for key in ('created', 'forced', 'deleted', 'head_commit', 'repository', 'ref', 'after', 'before'):
                broken = copy.deepcopy(event); del broken[key]
                event_path.write_text(json.dumps(broken)); reject('missing payload ' + key)
            event_path.write_text(json.dumps(event))
            for key in ('SC_CONTROL_HEAD', 'SC_CONTROL_TREE', 'SC_REQUEST_SHA256'):
                with patch.dict(os.environ, {key: ''}):
                    reject('empty legacy input ' + key)
            for key in ('GITHUB_SHA', 'GITHUB_REF', 'GITHUB_EVENT_PATH'):
                with patch.dict(os.environ, {key: ''}):
                    reject('empty context ' + key)
        # Gate uses full object identities; the runtime uses platform context.
        before_gate = (git('rev-parse', 'HEAD'), git('status', '--porcelain'))
        gate = final_head.check(control, head, ref, expected['request_sha256'], pins)
        checked('exact candidate final gate PASS', gate['status'] == 'FINAL_HEAD_REQUEST_GATE_PASS')
        checked('candidate gate readonly', before_gate == (git('rev-parse', 'HEAD'), git('status', '--porcelain')))
        evidence['final_candidate_gate'] = gate
        def gate_reject(label, final=head, expected_request=expected['request_sha256'], changed=pins, actual_ref=ref):
            try:
                final_head.check(local_control, final, actual_ref, expected_request, changed)
            except (ValueError, subprocess.SubprocessError):
                checked(label, True)
            else:
                raise AssertionError(label)
        # Use objects only in the disposable repo. commit-tree never changes HEAD.
        def make_commit(message, tree=pins['control']['tree'], parents=(runner.BASE,)):
            args = ['-c', 'user.name=W11 review test', '-c', 'user.email=test@example.invalid',
                    'commit-tree', tree]
            for parent in parents:
                args += ['-p', parent]
            return git(*args, '-m', message, cwd=local_control)
        # Full parent metadata is required by the offline gate, unlike runtime depth2.
        command(['git', 'fetch', '-q', '--unshallow', 'origin'], local_control)
        sibling = make_commit('W11 disposable non-skip publication sibling')
        derived = final_head.check(local_control, sibling, ref, None, pins)
        checked('sibling derives fresh exact request', derived['status'] == 'DERIVED_REQUIRES_EXACT_REQUEST_GATE'
                and derived['request_sha256'] != expected['request_sha256'])
        checked('sibling exact request gate PASS', final_head.check(local_control, sibling, ref,
                derived['request_sha256'], pins)['status'] == 'FINAL_HEAD_REQUEST_GATE_PASS')
        gate_reject('sibling rejects stale candidate request', final=sibling)
        for bad in ('', '0' * 64, expected['profile_sha256'], expected['request_sha256'].upper()):
            gate_reject('wrong request digest ' + repr(bad), expected_request=bad)
        gate_reject('wrong publication ref', actual_ref=push_identity.PREFIX + 'different')
        gate_reject('final requires exact SHA', final='HEAD')
        changed = copy.deepcopy(pins); changed['profile_sha256'] = '0' * 64
        gate_reject('profile digest mismatch', changed=changed)
        gate_reject('different final tree', final=make_commit('wrong tree', tree=pins['stock']['tree']))
        gate_reject('child of candidate rejected', final=make_commit('extra child', parents=(head,)))
        gate_reject('merge final rejected', final=make_commit('merge', parents=(runner.BASE, head)))
        for marker in ('[SKIP CI]', '[ci skip]', '[no ci]', '[skip actions]', '[actions skip]', 'skip-checks: true'):
            gate_reject('no silent skip publication ' + marker, final=make_commit('publication\n\n' + marker))
        command(['git', 'checkout', '-q', '--detach', sibling], local_control)
        event['after'] = sibling
        event['head_commit'] = {'id': sibling, 'message': git('show', '-s', '--format=%B', sibling, cwd=local_control)}
        event_path.write_text(json.dumps(event))
        with patch.object(runner, 'ROOT', local_control), patch.object(runner, 'SOURCE', local_stock), \
                patch.object(runner, 'PROFILE', local_control / '.github/stub-contract-confirm/profile.json'), \
                patch.dict(os.environ, env | {'GITHUB_SHA': sibling}, clear=True):
            snapshot = runner.snapshot()
            checked('real tree sibling runtime rebinds request', not snapshot['problems'] and
                    snapshot['request'] == derived['request_binding'] and snapshot['request_sha256'] == derived['request_sha256'])
        evidence['sibling_gate'] = derived

    # Replay the prior strict partial-export contract on the new actual request.
    outcomes = {}
    for case in ('valid_missing', 'valid_success', 'explicit_unsupported', 'malformed_export',
                 'partial_export', 'oversized_export', 'null_export', 'failed_provider'):
        with tempfile.TemporaryDirectory(prefix='w11-push-replay-') as temp:
            calls = []
            def execute(argv, cwd, timeout, env):
                slot = next(k for k, (_, name) in runner.SLOTS.items() if name == argv[argv.index('--harness') + 1])
                calls.append(slot)
                proc, doc = samples.sample(slot)
                if slot == 'ordinary' and case != 'valid_success':
                    proc, doc = samples.failure(runner.UNSUPPORTED if case == 'explicit_unsupported' else None), None
                if slot == 'provider' and case == 'failed_provider':
                    proc, doc = samples.failure('error: provider failed'), None
                export = Path(argv[argv.index('--export-json') + 1])
                if slot == 'ordinary' and case == 'malformed_export':
                    export.write_text('{')
                elif slot == 'ordinary' and case == 'oversized_export':
                    export.write_text(' ' * (2 * 1024 * 1024 + 1))
                elif slot == 'ordinary' and case == 'partial_export':
                    _, doc = samples.sample(slot); doc['run_state'] = 'PARTIAL'
                    export.write_text(json.dumps(doc))
                elif slot == 'ordinary' and case == 'null_export':
                    export.write_text('null')
                elif doc:
                    export.write_text(json.dumps(doc))
                return proc | {'argv': argv, 'cwd': str(cwd), 'environment': env}
            value = samples.state()
            value['source_before']['request_sha256'] = expected['request_sha256']
            with patch.object(runner, 'OUT', Path(temp)), patch.object(runner, 'execute', execute):
                runner.run_slots(value)
                stored = runner.load()
            checked('three slots retained ' + case, calls == list(runner.SLOTS))
            integrity = stored.pop('integrity')
            checked('compact digest ' + case, sha(runner.canonical(stored)) == integrity['canonical_payload_sha256'])
            for slot, record in stored['slots'].items():
                proc = record['process']
                runner.check_invocation(slot, proc)
                checked('invocation binding ' + case + '/' + slot,
                        proc['invocation_identity']['request_sha256'] == expected['request_sha256'] and
                        sha(runner.canonical(proc['invocation_identity'])) == proc['invocation_sha256'])
                doc = record['observation'].get('export')
                observation = runner.observe(slot, proc, doc)
                if record['export_inventory']['present'] and (not record['export_inventory']['complete'] or doc is None):
                    observation = {'outcome': 'INCONCLUSIVE', 'reason': 'present export not retained as successful document'}
                record['observation'] = observation
            expected_outcome = {'valid_missing': 'DEFECT_PRESENT', 'valid_success': 'DEFECT_ABSENT'}.get(case, 'INCONCLUSIVE')
            checked('strict export replay ' + case, runner.classify(stored)[0] == expected_outcome)
            outcomes[case] = expected_outcome
    evidence.update(status='PASS', check_count=len(checks), checks=checks, package_inventory=inventory,
                    strict_replay_outcomes=outcomes, compiler_or_CI_executed=False,
                    remote_publication_preconditions='NOT_CHECKED; coordinator must check before separately authorized publication',
                    native='NOT_RUN', independent_proof_credit='NONE')
    print(json.dumps(evidence, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
