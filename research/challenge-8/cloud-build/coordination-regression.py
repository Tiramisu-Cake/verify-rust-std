#!/usr/bin/env python3
"""Cloud-only, isolated regression of the cross-worktree client boundary."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import multiprocessing
import os
from pathlib import Path
import sys


sys.dont_write_bytecode = True
PHASE = 'COORDINATION-REGRESSION'
CREATED = '2026-10-09T01:00:00Z'
STARTED = '2026-10-09T01:00:01Z'
FINISHED = '2026-10-09T01:00:12.125Z'


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'cannot load {path.name}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def within_workspace(value: Path) -> Path:
    path = value.resolve()
    if not path.is_relative_to(Path('/workspace')):
        raise SystemExit('regression paths must resolve inside /workspace')
    return path


def fixture(base: Path, coord, *, owner: str = 'foreign', missing: bool = False,
            build_id: str | None = None, rejection: bool = False):
    """Create an isolated reservation and both ledgers; return observed paths."""
    coord.COORDINATION = base / 'coordination'
    caller = base / 'caller' / 'BUDGET.json'
    foreign = base / 'foreign' / 'BUDGET.json'
    state = base / 'foreign-state'
    state.mkdir(parents=True)
    (state / 'sentinel.json').write_bytes(b'{"foreign_state":"unchanged"}\n')
    token = 'dispatch-' + base.name.replace('_', '-')
    item = {'dispatch_token': token, 'owner': owner, 'phase_id': PHASE,
            'build_id': build_id, 'reserved_seconds': 660, 'status': 'DISPATCH_PENDING'}
    ledger = {'phase': PHASE, 'ceiling_build_seconds': 1000,
              'used_build_seconds': 0, 'remaining_build_seconds': 1000,
              'active_build': token, 'builds': [] if missing else [item.copy()]}
    coord.write(caller, {**ledger, 'active_build': None, 'builds': []})
    coord.write(foreign, ledger)
    record = {'dispatch_token': token, 'owner': owner, 'phase_id': PHASE,
              'ledger': str(foreign), 'state_dir': str(state), 'item': item.copy(),
              'build_id': build_id}
    if rejection:
        record['validation_rejection'] = True
        record['rejection_reason'] = 'API INVALID_ARGUMENT; synthetic fixture'
    with coord.locked():
        coord.reserve(record)
    return {'caller': caller, 'foreign': foreign, 'state': state,
            'token': token, 'record': record, 'item': item}


def file_tree(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): sha(p.read_bytes())
            for p in sorted(root.rglob('*')) if p.is_file()}


def preserved(paths: dict, before_ledger: bytes, before_state: dict[str, str]) -> None:
    need(paths['foreign'].read_bytes() == before_ledger, 'foreign ledger bytes changed')
    need(file_tree(paths['state']) == before_state, 'foreign state tree changed')


def expect_error(action, phrase: str) -> str:
    try:
        action()
    except RuntimeError as error:
        need(phrase in str(error), f'wrong rejection: {error}')
        return str(error)
    raise AssertionError(f'expected refusal containing {phrase!r}')


class FakeAPI:
    def __init__(self, token: str, *, listed=None, build=None, error: bool = False):
        self.token, self.listed, self.build, self.error = token, listed, build, error
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str]):
        self.calls.append(list(args))
        if self.error:
            raise RuntimeError('synthetic Cloud API unavailable')
        if args[:2] == ['builds', 'list']:
            need('--filter=tags:' + self.token in args, 'lookup omitted exact token filter')
            return self.listed if self.listed is not None else []
        if args[:2] == ['builds', 'describe']:
            need(self.build is not None and args[2] == self.build['id'],
                 'describe did not use resolved Build ID')
            return self.build.copy()
        raise AssertionError(f'unexpected fake API operation: {args}')


def terminal(build_id: str, token: str, *, tags: list[str] | None = None) -> dict:
    return {'id': build_id, 'tags': [token] if tags is None else tags,
            'status': 'SUCCESS', 'createTime': CREATED, 'startTime': STARTED,
            'finishTime': FINISHED}


def run_case(name: str, work: Path, control, coord, action) -> dict:
    base = work / name
    base.mkdir()
    try:
        observations = action(base, control, coord)
        return {'case': name, 'passed': True, 'observations': observations}
    except Exception as error:
        return {'case': name, 'passed': False,
                'error_type': type(error).__name__, 'error': str(error)}


def missing_foreign(base, control, coord):
    paths = fixture(base, coord, missing=True)
    before, state = paths['foreign'].read_bytes(), file_tree(paths['state'])
    fake = FakeAPI(paths['token'])
    control.invoke = fake
    with coord.locked():
        error = expect_error(lambda: control.reconcile_global('caller', paths['caller']),
                             'Foreign ledger lacks reserved token')
    preserved(paths, before, state)
    need(coord.active() is not None, 'missing foreign token cleared global reservation')
    need(not fake.calls, 'missing foreign token made Cloud API call')
    return {'refusal': error, 'foreign_ledger_sha256': sha(before),
            'foreign_state': state, 'mock_calls': fake.calls}


def missing_foreign_ledger(base, control, coord):
    paths = fixture(base, coord)
    paths['foreign'].unlink()
    state = file_tree(paths['state'])
    fake = FakeAPI(paths['token'])
    control.invoke = fake
    with coord.locked():
        try:
            control.reconcile_global('caller', paths['caller'])
        except FileNotFoundError:
            pass
        else:
            raise AssertionError('missing foreign ledger was silently reconstructed')
    need(not paths['foreign'].exists(), 'missing foreign ledger was created')
    need(file_tree(paths['state']) == state and coord.active() is not None,
         'missing foreign ledger changed state or cleared reservation')
    need(not fake.calls, 'missing foreign ledger made Cloud API call')
    return {'foreign_ledger_present': False, 'foreign_state': state,
            'active_token': coord.active()['dispatch_token'], 'mock_calls': fake.calls}


def uncertain_foreign(base, control, coord):
    paths = fixture(base, coord)
    before, state = paths['foreign'].read_bytes(), file_tree(paths['state'])
    fake = FakeAPI(paths['token'], listed=[])
    control.invoke = fake
    with coord.locked():
        control.reconcile_global('caller', paths['caller'])
    preserved(paths, before, state)
    need(coord.active() is not None, 'zero-match token cleared global reservation')
    need(len(fake.calls) == 1, 'uncertain submission did not make one token lookup')
    return {'active_token': coord.active()['dispatch_token'],
            'foreign_ledger_sha256': sha(before), 'foreign_state': state,
            'mock_calls': fake.calls}


def conflicting_ids(base, control, coord):
    paths = fixture(base, coord, build_id='build-record')
    ledger = coord.read(paths['foreign'])
    ledger['builds'][0]['build_id'] = 'build-ledger'
    coord.write(paths['foreign'], ledger)
    before, state = paths['foreign'].read_bytes(), file_tree(paths['state'])
    fake = FakeAPI(paths['token'])
    control.invoke = fake
    with coord.locked():
        error = expect_error(lambda: control.reconcile_global('caller', paths['caller']),
                             'Build IDs conflict')
    preserved(paths, before, state)
    need(coord.active() is not None and not fake.calls, 'conflicting IDs changed gate')
    return {'refusal': error, 'foreign_ledger_sha256': sha(before),
            'foreign_state': state, 'mock_calls': fake.calls}


def wrong_tag(base, control, coord):
    paths = fixture(base, coord, build_id='build-wrong-tag')
    before, state = paths['foreign'].read_bytes(), file_tree(paths['state'])
    fake = FakeAPI(paths['token'], build=terminal('build-wrong-tag', paths['token'],
                                                 tags=['other-token']))
    control.invoke = fake
    with coord.locked():
        error = expect_error(lambda: control.reconcile_global('caller', paths['caller']),
                             'does not carry the reserved dispatch token')
    preserved(paths, before, state)
    need(coord.active() is not None, 'wrong tag cleared global reservation')
    need(not (coord.COORDINATION / 'last-owner.json').exists(), 'wrong tag altered turn')
    return {'refusal': error, 'foreign_ledger_sha256': sha(before),
            'foreign_state': state, 'mock_calls': fake.calls}


def api_error(base, control, coord):
    paths = fixture(base, coord, build_id='build-api-error')
    before, state = paths['foreign'].read_bytes(), file_tree(paths['state'])
    fake = FakeAPI(paths['token'], error=True)
    control.invoke = fake
    with coord.locked():
        error = expect_error(lambda: control.reconcile_global('caller', paths['caller']),
                             'synthetic Cloud API unavailable')
    preserved(paths, before, state)
    need(coord.active() is not None, 'API error cleared global reservation')
    return {'refusal': error, 'foreign_ledger_sha256': sha(before),
            'foreign_state': state, 'mock_calls': fake.calls}


def foreign_terminal(base, control, coord):
    paths = fixture(base, coord, build_id='build-foreign-terminal')
    before, state = paths['foreign'].read_bytes(), file_tree(paths['state'])
    fake = FakeAPI(paths['token'], build=terminal('build-foreign-terminal', paths['token']))
    control.invoke = fake
    with coord.locked():
        control.reconcile_global('caller', paths['caller'])
    receipt = coord.read(coord.COORDINATION / 'receipts' / (paths['token'] + '.json'))
    preserved(paths, before, state)
    need(coord.active() is None, 'terminal foreign Build retained global reservation')
    need(receipt['status'] == 'SUCCESS' and receipt['build_seconds'] == 13 and
         receipt['owner'] == 'foreign' and receipt['ledger'] == str(paths['foreign']),
         'terminal receipt identity or conservative charge incorrect')
    return {'receipt': receipt, 'foreign_ledger_sha256': sha(before),
            'foreign_state': state, 'mock_calls': fake.calls}


def own_terminal(base, control, coord):
    paths = fixture(base, coord, owner='caller', build_id='build-own-terminal')
    fake = FakeAPI(paths['token'], build=terminal('build-own-terminal', paths['token']))
    control.invoke = fake
    with coord.locked():
        control.reconcile_global('caller', paths['foreign'])
        ledger = coord.read(paths['foreign'])
        control.reconcile(paths['state'], ledger, paths['foreign'])
        first = coord.read(paths['foreign'])
        control.reconcile(paths['state'], first, paths['foreign'])
    final = coord.read(paths['foreign'])
    item = final['builds'][0]
    need(coord.active() is None, 'own terminal Build retained global reservation')
    need(item['accounted'] is True and item['build_seconds'] == 13 and
         final['used_build_seconds'] == 13 and final['remaining_build_seconds'] == 987,
         'own terminal account not charged exactly once')
    need(len([c for c in fake.calls if c[:2] == ['builds', 'describe']]) == 2,
         'own account unexpectedly repeated terminal API describe')
    return {'first_used_seconds': first['used_build_seconds'],
            'second_used_seconds': final['used_build_seconds'],
            'item_status': item['status'],
            'own_ledger_sha256': sha(paths['foreign'].read_bytes()),
            'mock_calls': fake.calls}


def rejected_resume(base, control, coord):
    paths = fixture(base, coord, owner='caller', rejection=True)
    fake = FakeAPI(paths['token'], listed=[])
    control.invoke = fake
    with coord.locked():
        control.reconcile_global('caller', paths['foreign'])
    receipt_path = coord.COORDINATION / 'receipts' / (paths['token'] + '.json')
    receipt = coord.read(receipt_path)
    need(coord.active() is None and receipt['build_seconds'] == 0 and
         receipt['validation_rejection'] is True and 'INVALID_ARGUMENT' in receipt['reason'],
         'definitive rejection receipt or clear incorrect')
    before_calls = len(fake.calls)
    with coord.locked():
        ledger = coord.read(paths['foreign'])
        control.reconcile(paths['state'], ledger, paths['foreign'])
    final = coord.read(paths['foreign'])
    need(len(fake.calls) == before_calls, 'owner resume queried API despite 0s receipt')
    need(final['builds'][0]['accounted'] is True and
         final['builds'][0]['status'] == 'NOT_CREATED_INVALID_ARGUMENT' and
         final['used_build_seconds'] == 0 and final['remaining_build_seconds'] == 1000,
         'owner resume did not preserve zero-second rejection')
    return {'receipt': receipt, 'resumed_status': final['builds'][0]['status'],
            'resumed_used_seconds': final['used_build_seconds'],
            'own_ledger_sha256': sha(paths['foreign'].read_bytes()),
            'mock_calls': fake.calls}


def reserve_worker(directory: str, token: str, queue) -> None:
    import coordination
    coordination.COORDINATION = Path(directory)
    try:
        with coordination.locked():
            coordination.reserve({'dispatch_token': token})
        queue.put({'token': token, 'result': 'reserved'})
    except RuntimeError:
        queue.put({'token': token, 'result': 'blocked'})


def two_process_lock(base, control, coord):
    directory = base / 'coordination'
    context = multiprocessing.get_context('fork')
    queue = context.Queue()
    processes = [context.Process(target=reserve_worker,
                                 args=(str(directory), f'dispatch-contender-{i}', queue))
                 for i in range(2)]
    for process in processes:
        process.start()
    for process in processes:
        process.join(15)
        if process.is_alive():
            process.terminate()
            process.join(5)
            raise AssertionError('coordination flock contention did not finish')
    need(all(process.exitcode == 0 for process in processes), 'contender process failed')
    results = [queue.get(timeout=2) for _ in processes]
    need(sorted(row['result'] for row in results) == ['blocked', 'reserved'],
         'flock/reserve admitted more or fewer than one contender')
    chosen = coord.read(directory / 'active.json')['dispatch_token']
    need(chosen in [row['token'] for row in results if row['result'] == 'reserved'],
         'active token does not match winning contender')
    return {'contenders': results, 'active_token': chosen, 'mock_calls': []}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cloud-dir', type=Path, required=True)
    parser.add_argument('--work-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cloud_dir = within_workspace(args.cloud_dir)
    work = within_workspace(args.work_root)
    output = within_workspace(args.output)
    need(work.is_relative_to(Path('/workspace/smallsort-work')),
         'regression work root must be disposable Cloud workspace')
    need(output.is_relative_to(Path('/workspace/evidence/allprooflogs/cases')),
         'regression summary must remain in case evidence')
    provider = load(cloud_dir / 'provider.py', 'coordination_regression_provider')
    identity = provider.require_supported_provider()
    need(identity.get('provider') == 'cloud-build', 'real Cloud Build provider required')
    need(os.environ.get('GITHUB_ACTIONS') is None, 'GitHub identity prohibited')
    work.mkdir(parents=True, exist_ok=False)
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(cloud_dir))
    coord = load(cloud_dir / 'coordination.py', 'coordination')
    control = load(cloud_dir / 'control.py', 'coordination_regression_control')
    need(control.coordination is coord, 'control imported a different coordination module')
    cases = [('foreign_missing_token', missing_foreign),
             ('foreign_missing_ledger', missing_foreign_ledger),
             ('foreign_uncertain_zero_matches', uncertain_foreign),
             ('foreign_conflicting_ids', conflicting_ids),
             ('foreign_wrong_tag', wrong_tag),
             ('foreign_api_error', api_error),
             ('foreign_terminal', foreign_terminal),
             ('own_terminal_exact_charge', own_terminal),
             ('validation_rejection_owner_resume', rejected_resume),
             ('two_process_one_reservation', two_process_lock)]
    results = [run_case(name, work, control, coord, action) for name, action in cases]
    complete = all(row['passed'] for row in results)
    summary = {'classification': 'COORDINATION_REGRESSION_COMPLETE' if complete else 'INCONCLUSIVE',
               'diagnostic_complete': complete, 'verification_accepted': False,
               'provider': identity,
               'source_sha256': {name: sha((cloud_dir / name).read_bytes()) for name in
                                 ('control.py', 'coordination.py', 'coordination-regression.py')},
               'case_count': len(cases), 'passed_count': sum(row['passed'] for row in results),
               'cases': results,
               'limits': 'Synthetic API and isolated /workspace state; no real Cloud API or proof theorem.'}
    (output / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'classification': summary['classification'],
                      'passed_count': summary['passed_count'],
                      'case_count': summary['case_count']}), flush=True)
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
