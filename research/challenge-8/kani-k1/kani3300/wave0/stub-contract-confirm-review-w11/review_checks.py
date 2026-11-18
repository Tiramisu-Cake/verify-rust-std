#!/usr/bin/env python3
"""Independent static and bounded Python/mock checks of the pinned W15 packet."""
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
PACKET = HERE.parent / 'stub-contract-confirm'
REPO = HERE.parents[5]
PACKAGE = '5ba4f444f6fa1882b4eb6ac6d773f76cfc9c6531'
CODE = PACKET / 'source/tests/script-based-pre/stub-contract-confirm'
sys.path.insert(0, str(CODE))
import runner
import service
import check_service as author_samples


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(argv, cwd=None, env=None):
    return subprocess.check_output(argv, cwd=cwd, env=env, stderr=subprocess.PIPE)


def main():
    evidence = {'scope': 'STATIC_PYTHON_MOCK_ONLY', 'checks': []}

    def checked(name, condition):
        assert condition, name
        evidence['checks'].append(name)

    pins = json.loads((PACKET / 'PINS.json').read_text())
    stock = Path(pins['stock']['worktree'])
    control = Path(pins['control']['worktree'])
    relative = PACKET.relative_to(REPO).as_posix()
    files = sorted(p for p in PACKET.rglob('*') if p.is_file())
    tracked = command(['git', 'ls-tree', '-r', '--name-only', PACKAGE, '--', relative], REPO).decode().splitlines()
    checked('exact package 31 files', len(files) == len(tracked) == 31)
    identities = []
    for file in files:
        path = file.relative_to(REPO).as_posix()
        committed = command(['git', 'show', PACKAGE + ':' + path], REPO)
        checked('committed bytes ' + file.relative_to(PACKET).as_posix(), file.read_bytes() == committed)
        identities.append({'path': file.relative_to(PACKET).as_posix(), 'sha256': sha(committed), 'bytes': len(committed)})
    manifest = json.loads((PACKET / 'MANIFEST.json').read_text())
    checked('manifest 30 entries excluding itself', len(manifest['files']) == 30 and
            {x['path'] for x in manifest['files']} == {x['path'] for x in identities} - {'MANIFEST.json'})
    for item in manifest['files']:
        checked('manifest identity ' + item['path'], item in identities)
    expected = {
        'request_sha256': '21749d215a2851d971e58f16727d7589af3468adffe086afa4a558cf026841c4',
        'profile_sha256': '9f230f8fac56230a468f043e294bc77a745b50d5a16a47a7857eb0be4af5cae5',
        'control_patch_sha256': '915b02209ce2f8439c71239856b02aef6c58486236301f9e23902323b12608a4',
        'fix_candidate_patch_sha256': 'd3221b7ed70707ae39c479eed0bccc1f89f25e5ae5215356a117a8b7f718be08'}
    checked('owner exact digests', all(pins[k] == v for k, v in expected.items()))
    checked('owner exact workflow digest', sha((PACKET / 'source/.github/workflows/slow-tests.yml').read_bytes()) ==
            '0a537ae2e8f74f5864324237f761b2fe3b6a07982216b2e82ad9feca06d6011c')
    checked('canonical request binding', sha(runner.canonical(pins['request_binding'])) == expected['request_sha256'])
    request = json.loads((PACKET / 'CI-REQUEST.json').read_text())
    for slot in request['commands']['slots']:
        mapped = [arg.replace('${STOCK}', str(runner.SOURCE)).replace('${CONTROL}', str(runner.ROOT))
                  .replace('${SCRATCH}', '/synthetic-scratch') for arg in slot['argv']]
        checked('request and runtime argv identical: ' + slot['slot'], mapped == runner.argv_for(
            slot['slot'], '/synthetic-scratch/' + slot['slot'] + '.json',
            '/synthetic-scratch/' + slot['slot'] + '-target'))
    checked('request and runtime environment identical', request['environment'] == runner.ENV)
    checked('declared diagnostic and stream caps identical',
            request['caps']['stream_bytes'] == service.STREAM_CAP and
            request['caps']['diagnostic_block_bytes'] == service.BLOCK_CAP and
            request['caps']['diagnostic_blocks_per_stream'] == service.BLOCK_COUNT and
            request['caps']['group_rss_bytes'] == service.RSS_CAP)
    heads = {}
    for role, root in [('stock', stock), ('control', control)]:
        record = {key: command(['git', 'rev-parse', ref], root).decode().strip() for key, ref in
                  [('head', 'HEAD'), ('tree', 'HEAD^{tree}'), ('parent', 'HEAD^')]}
        parents = command(['git', 'show', '-s', '--format=%P', 'HEAD'], root).decode().split()
        checked(role + ' exact clean sole-parent nonshallow tree',
                all(record[k] == pins[role][k] for k in record) and parents == [pins[role]['parent']]
                and command(['git', 'status', '--porcelain'], root) == b''
                and command(['git', 'rev-parse', '--is-shallow-repository'], root).strip() == b'false')
        heads[role] = record
    diff = command(['git', 'diff', '--binary', runner.BASE, pins['control']['head']], control)
    checked('control patch exact binary diff', diff == (PACKET / 'control.patch').read_bytes())
    with tempfile.TemporaryDirectory(prefix='w11-patch-replay-') as directory:
        replay = Path(directory) / 'repo'
        command(['git', 'clone', '--quiet', '--shared', '--no-checkout', str(stock), str(replay)])
        command(['git', 'read-tree', runner.BASE], replay)
        command(['git', 'apply', '--cached', str(PACKET / 'control.patch')], replay)
        tree = command(['git', 'write-tree'], replay).decode().strip()
        checked('control patch replay exact tree', tree == pins['control']['tree'])
        command(['git', 'read-tree', runner.BASE], replay)
        command(['git', 'apply', '--cached', '--check', str(PACKET / 'fix-clear-error.patch')], replay)
        checked('separate fix patch applicability', True)
    evidence['package_inventory'] = identities
    evidence['heads'] = heads

    # Exercise rejection at the producer boundary, with realistic process records.
    mutations = [
        ('wrong closure', lambda p: p['diagnostics'][0].update(header='error: Failed to find contract closure `__kani_check_f` in function `f`')),
        ('wrong function', lambda p: p['diagnostics'][0].update(header='error: Failed to find contract closure `__kani_recursion_check_f` in function `other`')),
        ('generic compiler failure', lambda p: p['diagnostics'][0].update(header='error: build failed')),
        ('additional primary error', lambda p: p['diagnostics'].append({'header': 'error[E0308]: mismatched types'})),
        ('incomplete diagnostics', lambda p: p.update(diagnostics_complete=False)),
        ('incomplete stderr', lambda p: p['streams']['stderr'].update(complete=False)),
        ('timeout', lambda p: p.update(termination='TIMEOUT')),
        ('rss cap', lambda p: p.update(termination='RSS_CAP')),
        ('output cap', lambda p: p.update(termination='OUTPUT_CAP')),
        ('spawn error', lambda p: p.update(termination='SPAWN_ERROR')),
        ('missing exit', lambda p: p.update(exit=None)),
        ('mixed verification evidence', lambda p: p.update(property_inventory={'ordinary_stub': []})),
    ]
    for name, mutate in mutations:
        proc = author_samples.failure()
        mutate(proc)
        checked('reject ' + name, runner.observe('ordinary', proc, None)['outcome'] == 'INCONCLUSIVE')
    for slot in ('provider', 'verified'):
        state = author_samples.state('MISSING_CONTRACT_CLOSURE')
        state['slots'][slot]['observation']['outcome'] = 'NOT_RUN'
        checked('provider registration alone insufficient: ' + slot, runner.classify(state)[0] == 'INCONCLUSIVE')
    for slot in runner.SLOTS:
        proc, doc = author_samples.sample(slot)
        proc['property_inventory'][runner.SLOTS[slot][1]][0]['description'] = 'unrelated successful assertion'
        checked('semantic assertion required: ' + slot, runner.observe(slot, proc, doc)['outcome'] == 'INCONCLUSIVE')

    cases = ['valid_missing', 'valid_success', 'explicit_unsupported', 'malformed_export',
             'partial_export', 'oversized_export', 'failed_provider']
    outcomes = {}
    for case in cases:
        with tempfile.TemporaryDirectory(prefix='w11-slot-mock-') as directory:
            calls = []
            def mock_execute(argv, cwd, timeout, env):
                slot = next(k for k, (_, name) in runner.SLOTS.items() if name == argv[argv.index('--harness') + 1])
                calls.append(slot)
                proc, doc = author_samples.sample(slot)
                if slot == 'ordinary' and case != 'valid_success':
                    proc, doc = author_samples.failure(runner.UNSUPPORTED if case == 'explicit_unsupported' else None), None
                if slot == 'provider' and case == 'failed_provider':
                    proc, doc = author_samples.failure('error: provider failed'), None
                export = Path(argv[argv.index('--export-json') + 1])
                if slot == 'ordinary' and case == 'malformed_export':
                    export.write_text('{')
                elif slot == 'ordinary' and case == 'oversized_export':
                    export.write_text(' ' * (2 * 1024 * 1024 + 1))
                elif slot == 'ordinary' and case == 'partial_export':
                    _, doc = author_samples.sample(slot)
                    doc['run_state'] = 'PARTIAL'
                    export.write_text(json.dumps(doc))
                elif doc:
                    export.write_text(json.dumps(doc))
                return proc | {'argv': argv, 'cwd': str(cwd), 'environment': env}
            value = author_samples.state()
            with patch.object(runner, 'OUT', Path(directory)), patch.object(runner, 'execute', mock_execute):
                runner.run_slots(value)
                stored = runner.load()
            checked('all slots retained: ' + case, calls == list(runner.SLOTS) and set(stored['slots']) == set(runner.SLOTS))
            digest = stored.pop('integrity')
            checked('artifact canonical digest: ' + case, sha(runner.canonical(stored)) == digest['canonical_payload_sha256'])
            # Replay observation and invocation validation from the artifact contents.
            for slot, record in stored['slots'].items():
                runner.check_invocation(slot, record['process'])
                doc = record['observation'].get('export')
                observation = runner.observe(slot, record['process'], doc)
                if record['export_inventory']['present'] and not record['export_inventory']['complete']:
                    observation = {'outcome': 'INCONCLUSIVE', 'reason': 'incomplete export'}
                elif record['export_inventory']['present'] and doc is None:
                    observation = {'outcome': 'INCONCLUSIVE', 'reason': 'export present without retained successful document'}
                record['observation'] = observation
            classification = runner.classify(stored)[0]
            expected_classification = {'valid_missing': 'DEFECT_PRESENT', 'valid_success': 'DEFECT_ABSENT'}.get(case, 'INCONCLUSIVE')
            checked('replayed classification: ' + case, classification == expected_classification)
            outcomes[case] = classification

    for setup in ('failure', 'cancelled', 'skipped', 'UNKNOWN'):
        with tempfile.TemporaryDirectory(prefix='w11-finish-mock-') as directory:
            with patch.object(runner, 'OUT', Path(directory)), patch.object(runner, 'snapshot', return_value={'problems': [], 'tools': {}}), \
                    patch.object(runner, 'execute', side_effect=AssertionError('native execution forbidden')), \
                    patch.dict(os.environ, {'SC_SETUP_OUTCOME': setup, 'SC_JOB_STATUS': 'failure'}):
                runner.save(author_samples.state('MISSING_CONTRACT_CLOSURE'))
                checked('finish retained after setup ' + setup, runner.main('finish') == 0)
                checked('setup failure inconclusive ' + setup, runner.load()['classification'] == 'INCONCLUSIVE')

    # Service diagnostic capacity is independent of the head/tail preview.
    header = author_samples.failure()['diagnostics'][0]['header']
    blocks, complete = service.diagnostics(header + '\n' + 'x' * 5000)
    checked('diagnostic byte cap conservative', not complete and not blocks[0]['complete'])
    blocks, complete = service.diagnostics('\n'.join('error: other' for _ in range(33)))
    checked('diagnostic count cap conservative', not complete and len(blocks) == 32)
    with tempfile.TemporaryDirectory(prefix='w11-middle-diagnostic-') as directory:
        program = 'print("x\\n" * 5000 + ' + repr(header) + ' + "\\nerror: aborting due to 1 previous error\\n" + "y\\n" * 5000);raise SystemExit(101)'
        proc = service.execute([sys.executable, '-c', program], Path(directory), 2)
        # The long final summary block is deliberately incomplete, so credit is refused.
        checked('full error retention cap refuses hidden suffix', proc['exit'] == 101 and
                runner.observe('ordinary', proc, None)['outcome'] == 'INCONCLUSIVE')

    evidence.update(status='PASS', check_count=len(evidence['checks']), mock_outcomes=outcomes,
                    native={'main': 'NOT_RUN', 'fixed': 'NOT_RUN', 'MIR': 'NOT_RUN', 'confirmation': 'NOT_RUN'},
                    compiler_or_full_runner_executed=False)
    print(json.dumps(evidence, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
