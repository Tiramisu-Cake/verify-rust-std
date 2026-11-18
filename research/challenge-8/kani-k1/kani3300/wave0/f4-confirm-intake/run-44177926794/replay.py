#!/usr/bin/env python3
"""Read-only compact intake replay. No runner/service/native execution or writes.

The reviewed parser is reused through an explicit compact-to-parser adapter.
Discarded export envelope fields are producer-attested, not recovered evidence.
Only AST-selected pure oracle functions are loaded from the exact trigger object.
"""
import ast
import collections
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
REPO = next(p for p in OUT.parents if (p / '.git').exists())
WAVE = OUT.parent.parent
KANI = Path('/root/kani-f4-confirm-w15')
TRIGGER = 'bbbe2d18d2f6e1be7fd410e1d6f746c98bb92b79'
CONTROL = '1ec3318f5e2c39afb701aa7a5578d4ea0a721224'
BASE = 'faffcee3bca2770c03bd21c3bde89cc8f6f7a14e'
TREE = '34a402bd4ebbabf3ec611327097475c8cb46cfba'
BASE_TREE = '09b828b47c93e90e140e8c41f9048109a2f4a786'
PACKAGE = '1bd7d58e6cafc64c36c4012651751c038d3e9c64'
REVIEW = '8c37ad792ead0ac22161e2e2d10d8dadcd2837e1'
REL = 'research/challenge-8/kani-k1/kani3300/wave0/'
FIXTURE = 'tests/script-based-pre/delayed-shared-body/'
RUNTIME = Path('/home/runner/work/kani/kani')
PROFILE_HASH = '2e6a6cf8ba9b698c95a857bddfc7dd6e5c98391f6c66062f915a8784022e0568'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)


def blob(repo, revision, path):
    return git(repo, 'show', revision + ':' + path)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(name):
    return json.loads((OUT / name).read_text())


def check(ok, reason):
    if not ok:
        raise ValueError(reason)


REQUEST_BYTES = blob(REPO, PACKAGE, REL + 'f4-confirm/CI-REQUEST.json')
check(sha(REQUEST_BYTES) == '2d6a573807ae873b0d1c02522eaf25ae39a5a1552076f1bc734a28c842c0eb60', 'request hash')
REQUEST = json.loads(REQUEST_BYTES)
PROFILE_BYTES = blob(KANI, TRIGGER, '.github/f4-confirm/profile.json')
check(sha(PROFILE_BYTES) == PROFILE_HASH, 'profile hash')
PROFILE = json.loads(PROFILE_BYTES)
RUNNER = blob(KANI, TRIGGER, FIXTURE + 'runner.py')
check(sha(RUNNER) == PROFILE['source_sha256'][FIXTURE + 'runner.py'], 'runner hash')
oracle_ast = ast.parse(RUNNER)
allowed = {'Unknown', 'require', 'parse_document', 'argv_for', 'environment', 'signature', 'classify'}
nodes = [n for n in oracle_ast.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in allowed]
check({n.name for n in nodes} == allowed, 'pure oracle extraction')
ORACLE = {'collections': collections, 're': re, 'ROOT': RUNTIME,
          'HERE': RUNTIME / FIXTURE, 'TARGET': PROFILE['target'],
          'UNINIT': 'Undefined Behavior: Reading from an uninitialized pointer',
          'NAMES': ['delayed_harness', 'initialized_control_harness']}
exec(compile(ast.Module(body=nodes, type_ignores=[]), '<exact-trigger-pure-oracles>', 'exec'), ORACLE)


def validate_pins():
    if (OUT / 'MANIFEST.json').exists():
        manifest = load('MANIFEST.json')
        check(set(manifest['files']) == {p.name for p in OUT.iterdir() if p.is_file() and p.name != 'MANIFEST.json'}, 'intake manifest namespace')
        for name, identity in manifest['files'].items():
            data = (OUT / name).read_bytes()
            check(identity == {'bytes': len(data), 'sha256': sha(data)}, 'intake member integrity: ' + name)
    for rev, tree, parent in [(TRIGGER, TREE, CONTROL), (CONTROL, TREE, BASE)]:
        check(git(KANI, 'show', '-s', '--format=%T %P', rev).decode().strip() == tree + ' ' + parent, 'local commit chain')
    check(git(KANI, 'rev-parse', BASE + '^{tree}').decode().strip() == BASE_TREE, 'main tree')
    remote = load('github-commits.json')
    check(len(remote) == 3, 'remote chain count')
    for commit, rev, tree, parent in zip(remote, [TRIGGER, CONTROL, BASE], [TREE, TREE, BASE_TREE], [CONTROL, BASE, None]):
        check(commit['sha'] == rev and commit['tree']['sha'] == tree, 'remote commit/tree')
        if parent:
            check([p['sha'] for p in commit['parents']] == [parent], 'remote ancestry')
    run = load('github-run.json')
    check((run['id'], run['run_attempt'], run['status'], run['conclusion'], run['head_sha'], run['head_branch']) ==
          (44177926794, 1, 'completed', 'failure', TRIGGER, 'f4-confirm-ci/main-20261118'), 'run identity/terminal')
    check(run['repository']['full_name'] == 'Tiramisu-Cake/kani' and run['head_commit']['tree_id'] == TREE, 'repository/tree')
    jobs = load('github-jobs.json')['jobs']
    check(len(jobs) == 1 and jobs[0]['status'] == 'completed' and jobs[0]['conclusion'] == 'failure', 'job terminal')
    for step in jobs[0]['steps']:
        check(step['conclusion'] == ('failure' if step['name'] == 'Compare initialization checks' else 'success'), 'step gate')
    artifacts = load('github-artifacts.json')['artifacts']
    check(len(artifacts) == 1, 'artifact count')
    art = artifacts[0]
    check(art['name'] == 'f4-confirm-44177926794-1' and art['id'] == 14369704819 and not art['expired'], 'artifact identity')
    check(art['workflow_run']['id'] == run['id'] and art['workflow_run']['head_sha'] == TRIGGER, 'artifact run binding')
    verification = load('artifact-verification.json')
    check(art['digest'] == 'sha256:' + verification['archive_sha256'] and verification['digest_checked_before_extraction'] is True,
          'pre-extraction digest receipt')
    check(verification['archive_bytes'] == art['size_in_bytes'] == 14719, 'compact archive bound')
    check(verification['members'] == [{'name': 'result.json', 'bytes': (OUT / 'result.json').stat().st_size,
                                     'sha256': sha((OUT / 'result.json').read_bytes())}], 'member binding')
    check(verification['members'][0]['bytes'] <= 2097152, 'member cap')
    review = json.loads(blob(REPO, REVIEW, REL + 'f4-confirm-review/REVIEW.json'))
    check(review['candidate_g0'] == PACKAGE and review['findings'] == [] and review['verdict'] == 'APPROVE', 'review binding')
    check(not git(REPO, 'diff', PACKAGE, 'HEAD', '--', REL + 'f4-confirm'), 'immutable package changed')
    check(sha(blob(KANI, TRIGGER, REQUEST['workflow']['file'])) == REQUEST['workflow']['sha256'], 'workflow hash')
    check(PROFILE['source_sha256'] == REQUEST['profile']['source_sha256'], 'profile/request sources')
    for path, digest in PROFILE['source_sha256'].items():
        check(sha(blob(KANI, TRIGGER, path)) == digest, 'source hash: ' + path)
    # Bind the trigger payload bytes to the independently reviewed g0 package.
    paths = git(REPO, 'ls-tree', '-r', '--name-only', PACKAGE, '--', REL + 'f4-confirm/source/').decode().splitlines()
    for path in paths:
        suffix = path.removeprefix(REL + 'f4-confirm/source/')
        check(blob(REPO, PACKAGE, path) == blob(KANI, TRIGGER, suffix), 'reviewed payload: ' + suffix)
    # Exact complete tree delta independently excludes any compiler/driver/library fix.
    changes = git(KANI, 'diff', '--name-status', BASE, TRIGGER).decode().splitlines()
    for change in changes:
        status, path = change.split('\t')
        check(path.startswith((FIXTURE, '.github/f4-confirm/')) or path == '.github/workflows/f4-confirm.yml'
              or (status == 'D' and path.startswith('.github/workflows/')), 'compiler fix or unrelated delta')
    return changes


def parser_adapter(record, wanted):
    """Only adapter constants below are synthetic; all property data are retained.

    schema_version, run_state, outcome, per-harness kind/cover flags were enforced
    by the reviewed producer but not retained verbatim in this compact format.
    This adapter replays its property/partition/failure/exit oracle; it cannot
    independently re-read the discarded export envelope or regular stdout.
    """
    doc = copy.deepcopy(record['native_configuration'])
    doc.update(schema_version='0.1.0', run_state='COMPLETE', outcome={'kind': 'COMPLETED'})
    doc['harnesses'] = []
    for name, h in record['harnesses'].items():
        check(h['properties'] == record['property_inventory'][name], 'compact/native property binding')
        for failed in h['failed_properties']:
            native = next(p for p in h['properties'] if p['id'] == failed['id'])
            source = Path(failed['file'])
            # Native regular output renders the standalone absolute export path
            # relative to the recorded cwd. This does not alter semantic IDs.
            if source.is_absolute():
                source = source.relative_to(Path(record['cwd']))
            check(native['location'].startswith(str(source) + ':' + failed['line'] + ':'), 'native failure source binding')
        entry = copy.deepcopy(h)
        entry.update(name=name, outcome={'kind': 'COMPLETED', 'verdict': h['verdict']},
                     is_automatically_generated=False, is_bounded=False, covers={'total': 0})
        doc['harnesses'].append(entry)
    return ORACLE['parse_document'](doc, wanted, record)


def validate_payload(value, changes):
    check(value['schema'] == 'kani-f4-confirm-v2', 'compact schema')
    for stage in ('source_before', 'source_run', 'source_after'):
        s = value[stage]
        check(s['problems'] == [] and s['base'] == BASE and s['base_tree'] == BASE_TREE and s['head'] == TRIGGER
              and s['tree'] == TREE and s['control'] == CONTROL, 'snapshot ' + stage)
        check(s['source_sha256'] == PROFILE['source_sha256'] and s['profile_sha256'] == PROFILE_HASH
              and s['changes'] == changes, 'snapshot source hash/delta ' + stage)
    tools = value['source_run']['tools']
    check(set(tools) == {'cargo', 'rustc', 'cbmc', 'kani-driver', 'kani-compiler'}, 'built tool inventory')
    for name, identity in tools.items():
        check(re.fullmatch('[0-9a-f]{64}', identity['sha256']) is not None, 'tool digest ' + name)
    build = value['build']
    check(build['argv'] == ['cargo', 'build-dev'] and build['cwd'] == str(RUNTIME) and build['exit'] == 0
          and build['termination'] == 'EXITED' and build['signal'] is None and build['timeout_seconds'] == 900, 'build gate')
    commands = REQUEST['commands']['six_runs']
    check(set(value['runs']) == {'uninitialized_control'} | {c['label'] for c in commands}, 'seven slots')
    runs = copy.deepcopy(value['runs'])
    for label, record in runs.items():
        standalone = label == 'uninitialized_control'
        command = None if standalone else next(c for c in commands if c['label'] == label)
        wanted = ['uninitialized_control'] if standalone else command['expected_harnesses']
        argv = record['argv']
        scratch = str(Path(argv[argv.index('--export-json') + 1]).parent)
        check(re.fullmatch('/tmp/f4-confirm-[A-Za-z0-9_-]+', scratch) is not None, 'scratch namespace')
        declared = REQUEST['commands']['standalone_control_argv'] if standalone else command['argv']
        expected = [x.replace('${REPO}', str(RUNTIME)).replace('${SCRATCH}', scratch) for x in declared]
        check(argv == expected and record['cwd'] == str(RUNTIME / FIXTURE), 'exact argv/cwd ' + label)
        env = ORACLE['environment']()
        if standalone:
            env['RUSTFLAGS'] = '--edition=2021'
        check(all(k in record['environment'] and record['environment'][k] == v for k, v in env.items()), 'environment ' + label)
        check(record['environment']['PATH'] == build['environment']['PATH'], 'PATH changed')
        check(record['termination'] == 'EXITED' and record['signal'] is None and record['timeout_seconds'] == 120, 'native termination')
        for name, identity in tools.items():
            check(record['resolved_tools'][name] == identity['path'], 'native tool path ' + name)
        check(record['resolved_tools']['cargo-kani'] == str(RUNTIME / 'scripts/cargo-kani'), 'cargo wrapper path')
        config = record['native_configuration']
        check(config['kani_commit'] == TRIGGER and config['kani_commit_dirty'] is False, 'native source identity')
        check(config['tools'] == {'cbmc': '6.11.0 (cbmc-6.11.0)', 'kani': '0.68.0',
                                  'rustc': '1.102.0-nightly (3ef0c22cd 2026-11-11)'}, 'native versions')
        for digest in ('export_sha256', 'output_sha256'):
            check(re.fullmatch('[0-9a-f]{64}', record[digest]) is not None, 'native digest field')
        record['harnesses'] = parser_adapter(record, wanted)
        record['classification'] = 'COMPLETE'  # recomputed, never accepted from summary
    for record in [build] + list(runs.values()):
        check(isinstance(record['elapsed_seconds'], (int, float)) and record['elapsed_seconds'] >= 0, 'measured time')
        for key, cap in [('stderr_first_lines', 18), ('stderr_tail', 8)]:
            check(len(record[key]) <= cap and all(isinstance(s, str) and len(s) <= 500 for s in record[key]), 'diagnostic bounds')
    classification, differences = ORACLE['classify'](runs)
    return classification, differences, runs


def semantic_delta(single, paired):
    left, right = collections.Counter(ORACLE['signature'](single)), collections.Counter(ORACLE['signature'](paired))
    return {'removed': [{'identity': list(k), 'multiplicity': n} for k, n in sorted((left - right).items())],
            'added': [{'identity': list(k), 'multiplicity': n} for k, n in sorted((right - left).items())]}


def main():
    changes = validate_pins()
    value = load('result.json')
    classification, differences, runs = validate_payload(value, changes)
    if sys.argv[1:] == ['--self-test']:
        count = 0
        for mutation in ('schema', 'missing_slot', 'argv', 'partition', 'property', 'unsupported', 'exit', 'snapshot'):
            bad = copy.deepcopy(value)
            rec = bad['runs']['uninitialized_control']
            if mutation == 'schema': bad['schema'] = 'wrong'
            elif mutation == 'missing_slot': del bad['runs']['control_first/paired']
            elif mutation == 'argv': rec['argv'].append('--unknown')
            elif mutation == 'partition': rec['harnesses']['uninitialized_control']['checks']['success'] += 1
            elif mutation == 'property': rec['property_inventory']['uninitialized_control'].pop()
            elif mutation == 'unsupported': rec['harnesses']['uninitialized_control']['unsupported_constructs'][0]['status'] = 'FAILURE'
            elif mutation == 'exit': rec['exit'] = 0
            elif mutation == 'snapshot': bad['source_after']['head'] = BASE
            try:
                validate_payload(bad, changes)
            except (ValueError, KeyError, TypeError):
                count += 1
            else:
                raise AssertionError('accepted corruption: ' + mutation)
        no_summary = copy.deepcopy(value)
        no_summary.update(classification='DEFECT_ABSENT_FOR_TEST', differences=[], reason='untrusted summary')
        for r in no_summary['runs'].values(): r['classification'] = 'UNTRUSTED'
        check(validate_payload(no_summary, changes)[:2] == (classification, differences), 'summary dependence')
        print(json.dumps({'status': 'PASS', 'rejected_corruptions': count, 'summary_independence': 'PASS'}))
        return
    deltas = {}
    for mode in ('delayed_first', 'control_first'):
        for case, name in [('delayed_alone', 'delayed_harness'), ('control_alone', 'initialized_control_harness')]:
            deltas[mode + '/' + name] = semantic_delta(runs[mode + '/' + case]['harnesses'][name], runs[mode + '/paired']['harnesses'][name])
    print(json.dumps({'classification': classification, 'differences': differences, 'semantic_deltas': deltas,
                      'exact_runs': runs, 'source_snapshots': {k: value[k] for k in ('source_before', 'source_run', 'source_after')},
                      'build': value['build'], 'pins_status': 'PASS', 'order_coverage': 'UNKNOWN',
                      'adapter_boundary': 'Discarded envelope and raw native streams are producer-attested; no synthetic adapter constant is new evidence.'}, indent=2, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, subprocess.CalledProcessError, StopIteration) as error:
        print(json.dumps({'classification': 'INCONCLUSIVE', 'reason': str(error)}))
        sys.exit(2)
