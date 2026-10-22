#!/usr/bin/env python3
"""Disposable local checks for v4 (select-sort4/merge/network, cap 3); no Cloud calls.

Transition tests use real temporary Git repositories with a bare `origin`, so
ancestry, changed-path and publication checks run against Git, not mocks.
"""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import coordination

spec = importlib.util.spec_from_file_location('v4_transition', HERE / 'coordination-v4-transition.py')
transition = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transition)

# Deployed v3 coordinator (Select = Merge client blob), read from Git.
V3_BLOB = '1fd8b97bb11130325e5e9ea5ee3bf57b9adf0caf'
DISPATCHER = b'''import coordination
def f():
    with coordination.locked():
        coordination.reservations(); coordination.require_capacity(); coordination.reserve()
        coordination.update(); coordination.clear(); coordination.request()
'''


def load_v3():
    source = subprocess.check_output(['git', '-C', str(HERE), 'cat-file', '-p', V3_BLOB])
    module = type(sys)('coordination_v3')
    exec(compile(source, 'coordination_v3', 'exec'), module.__dict__)
    return module


def record(base, owner, token=None):
    return {'owner': owner, 'phase_id': 'PHASE', 'ledger': str(base / (owner + '.json')),
            'state_dir': str(base / (owner + '-state')),
            'dispatch_token': token or ('token-' + owner), 'build_id': None,
            'item': {'status': 'DISPATCH_PENDING'}}


def run(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL).decode().strip()


class Base(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        old = coordination.COORDINATION
        coordination.COORDINATION = self.root / 'coordination'
        self.addCleanup(setattr, coordination, 'COORDINATION', old)

    def envelope(self, version, records=(), cap=3):
        coordination.write(coordination.COORDINATION / 'active.json',
                           {'schema_version': version, 'max_active': cap, 'reservations': list(records)})


class CoordinatorV4Tests(Base):
    def test_v3_behaviour_unchanged_network_refused(self):
        with coordination.locked():
            self.envelope(3)
            with self.assertRaisesRegex(RuntimeError, 'Unsupported v3'):
                coordination.reserve(record(self.root, 'network'))
            with self.assertRaisesRegex(RuntimeError, 'Unsupported v3'):
                coordination.request('network', 'P', self.root / 'network.json', '2099-01-01T00:00:00Z')
            self.assertFalse((coordination.COORDINATION / 'requests' / 'network.json').exists())
            for owner in ('select-sort4', 'merge', 'verifast'):
                coordination.reserve(record(self.root, owner))
            self.assertEqual(coordination.protocol(), (3, 3))

    def test_v4_three_owners_verifast_refused_cap_three(self):
        with coordination.locked():
            self.envelope(4)
            self.assertEqual(coordination.protocol(), (4, 3))
            for owner in ('verifast', 'fifth'):
                with self.assertRaisesRegex(RuntimeError, 'Unsupported v4'):
                    coordination.reserve(record(self.root, owner))
                with self.assertRaisesRegex(RuntimeError, 'Unsupported v4'):
                    coordination.request(owner, 'P', self.root / (owner + '.json'), '2099-01-01T00:00:00Z')
            self.assertFalse(any((coordination.COORDINATION / 'requests').glob('*.json')))
            coordination.reserve(record(self.root, 'network'))
            coordination.reserve(record(self.root, 'select-sort4'))
            with self.assertRaisesRegex(RuntimeError, 'Owner or ledger'):
                coordination.reserve(record(self.root, 'network', 'other-token'))
            # An untracked project Build occupies the third slot.
            with self.assertRaisesRegex(RuntimeError, 'occupied'):
                coordination.require_capacity('merge', self.root / 'merge.json', [{'id': 'x', 'tags': []}])
            coordination.reserve(record(self.root, 'merge'))
            self.assertEqual(len(coordination.reservations()), 3)
            coordination.clear('token-merge')
            coordination.request('network', 'P', self.root / 'network.json', '2099-01-01T00:00:00Z')
            self.assertEqual([r['owner'] for r in coordination.reservations()], ['network', 'select-sort4'])

    def test_v4_rejects_wrong_cap_and_foreign_owner_record(self):
        with coordination.locked():
            self.envelope(4, cap=4)
            with self.assertRaisesRegex(RuntimeError, 'Unsupported Cloud Build coordination protocol'):
                coordination.protocol()
            for owner in ('verifast', 'refinedrust-feasibility'):
                self.envelope(4, [record(self.root, owner)])
                with self.assertRaisesRegex(RuntimeError, 'Unsupported v4'):
                    coordination.reservations()

    def test_deployed_v3_client_fails_closed_on_v4(self):
        v3 = load_v3()
        v3.COORDINATION = coordination.COORDINATION
        with coordination.locked():
            self.envelope(4, [record(self.root, 'network')])
        with v3.locked():
            for call in (v3.protocol, v3.reservations,
                         lambda: v3.require_capacity('verifast', self.root / 'verifast.json')):
                with self.assertRaisesRegex(RuntimeError, 'Unsupported Cloud Build coordination protocol'):
                    call()


class TransitionTests(Base):
    def setUp(self):
        super().setUp()
        old = transition.EXPECTED_CLIENTS
        transition.EXPECTED_CLIENTS = {o: ((self.root / o).resolve(), 'branch-' + o) for o in coordination.V4_OWNERS}
        self.addCleanup(setattr, transition, 'EXPECTED_CLIENTS', old)

    def make_client(self, owner, control=DISPATCHER, extra=None, coord=None, push=True, moved=None):
        origin = self.root / (owner + '-origin.git')
        root = self.root / owner
        subprocess.check_call(['git', 'init', '-q', '--bare', str(origin)])
        subprocess.check_call(['git', 'init', '-q', '-b', 'branch-' + owner, str(root)])
        run(root, 'config', 'user.email', 't@t'); run(root, 'config', 'user.name', 't')
        run(root, 'remote', 'add', 'origin', str(origin))
        base_control = root / transition.BASELINE_CONTROL.get(owner, transition.CONTROL)
        base_control.parent.mkdir(parents=True, exist_ok=True)
        base_control.write_bytes(control)
        if owner != 'network':
            (root / transition.COORDINATION).write_bytes(b'# v3\n')
        if moved:
            (root / moved).parent.mkdir(parents=True, exist_ok=True)
            (root / moved).write_bytes((HERE / 'coordination.py').read_bytes())
        run(root, 'add', '-A'); run(root, 'commit', '-qm', 'baseline')
        baseline = run(root, 'rev-parse', 'HEAD')
        installed = root / transition.COORDINATION
        installed.parent.mkdir(parents=True, exist_ok=True)
        installed.write_bytes(coord if coord is not None else (HERE / 'coordination.py').read_bytes())
        (root / transition.CONTROL).write_bytes(DISPATCHER)
        if extra:
            (root / extra).write_text('x')
        if moved:
            (root / moved).unlink()
        run(root, 'add', '-A'); run(root, 'commit', '-qm', 'adopt')
        adopted = run(root, 'rev-parse', 'HEAD')
        if push:
            run(root, 'push', '-q', 'origin', 'branch-' + owner)
        ack = self.root / (owner + '-ack.json')
        ack.write_text(json.dumps({
            'owner': owner, 'branch': 'branch-' + owner,
            'coordination_sha256': hashlib.sha256(installed.read_bytes()).hexdigest(),
            'control_sha256': hashlib.sha256(DISPATCHER).hexdigest(),
            'infra_commit': adopted, 'baseline_control_commit': baseline}))
        return root, ack

    def clients(self, **special):
        clients, acks = {}, {}
        for owner in sorted(coordination.V4_OWNERS):
            clients[owner], acks[owner] = self.make_client(owner, **special.get(owner, {}))
        return clients, acks

    def test_migration_requires_idle_and_three_owners(self):
        clients, acks = self.clients()
        self.assertEqual(transition.verify_clients(clients, acks),
                         hashlib.sha256((HERE / 'coordination.py').read_bytes()).hexdigest())
        partial = dict(clients); partial.pop('network')
        with self.assertRaisesRegex(RuntimeError, 'all three'):
            transition.migrate(partial, acks, list)
        with self.assertRaisesRegex(RuntimeError, 'each v4 owner'):
            transition.mapping(['merge=a', 'select-sort4=b', 'verifast=c'], 'client')
        with self.assertRaisesRegex(RuntimeError, 'all three'):
            transition.mapping(['merge=a', 'select-sort4=b'], 'client')
        live = {**record(self.root, 'select-sort4'), 'build_id': 'live'}
        with coordination.locked():
            self.envelope(3, [live])
        with self.assertRaisesRegex(RuntimeError, 'reservation'):
            transition.migrate(clients, acks, list)
        with coordination.locked():
            self.envelope(3)
            coordination.request('merge', 'P', self.root / 'merge.json', '2000-01-01T00:00:00Z')
        with self.assertRaisesRegex(RuntimeError, 'turn request'):
            transition.migrate(clients, acks, list)
        coordination.withdraw('merge')
        with self.assertRaisesRegex(RuntimeError, 'ongoing'):
            transition.migrate(clients, acks, lambda: [{'id': 'foreign'}])
        with coordination.locked():
            self.assertEqual(coordination.protocol(), (3, 3))
        result = transition.migrate(clients, acks, list)
        self.assertEqual(result['before'], {'schema_version': 3, 'max_active': 3, 'reservations': []})
        self.assertEqual(result['after'], {'schema_version': 4, 'max_active': 3, 'reservations': []})
        with self.assertRaisesRegex(RuntimeError, 'only from the v3'):
            transition.migrate(clients, acks, list)

    def test_migration_refuses_unpublished_or_changed_clients(self):
        cases = [({'merge': {'push': False}}, 'not published'),
                 ({'select-sort4': {'extra': 'research/x.txt'}}, 'beyond the client'),
                 ({'network': {'moved': 'research/old/coordination.py'}}, 'beyond the client'),
                 ({'network': {'control': DISPATCHER + b'#'}}, 'dispatcher changed'),
                 ({'merge': {'coord': b'# other\n'}}, 'differs'),
                 ({'select-sort4': {'control': b'import coordination\n'}}, 'dispatcher changed')]
        for special, message in cases:
            with self.subTest(message=message):
                self.temp.cleanup(); Path(self.temp.name).mkdir()
                with coordination.locked():
                    self.envelope(3)
                clients, acks = self.clients(**special)
                with self.assertRaisesRegex(RuntimeError, message):
                    transition.migrate(clients, acks, list)
                with coordination.locked():
                    self.assertEqual(coordination.protocol(), (3, 3))
        self.temp.cleanup(); Path(self.temp.name).mkdir()
        with coordination.locked():
            self.envelope(3)
        clients, acks = self.clients()
        good = json.loads(Path(acks['network']).read_text())
        for key, value in (('coordination_sha256', '0' * 64), ('control_sha256', '0' * 64),
                           ('owner', 'verifast'), ('branch', 'other'),
                           ('baseline_control_commit', good['infra_commit'])):
            with self.subTest(key=key):
                Path(acks['network']).write_text(json.dumps({**good, key: value}))
                with self.assertRaises(RuntimeError):
                    transition.migrate(clients, acks, list)
        Path(acks['network']).write_text(json.dumps(good))
        swapped = dict(clients, merge=clients['select-sort4'])
        with self.assertRaisesRegex(RuntimeError, 'dispatcher worktree'):
            transition.migrate(swapped, acks, list)
        merge_ack = Path(acks['merge']).read_text()
        Path(acks['merge']).write_text('[]')
        with self.assertRaisesRegex(RuntimeError, 'JSON object'):
            transition.migrate(clients, acks, list)
        Path(acks['merge']).write_text(merge_ack)
        with coordination.locked():
            self.assertEqual(coordination.protocol(), (3, 3))
        transition.migrate(clients, acks, list)

    def test_inventory_output_empty_or_not_list_refused(self):
        from unittest.mock import patch
        for output in (b'', b'  \n', b'{}'):
            with self.subTest(output=output), patch.object(transition.subprocess, 'check_output', return_value=output):
                with self.assertRaises(RuntimeError):
                    transition.ongoing_builds()
        with patch.object(transition.subprocess, 'check_output', return_value=b'[]'):
            self.assertEqual(transition.ongoing_builds(), [])

    def test_rollback_only_without_network(self):
        with coordination.locked():
            self.envelope(3)
        with self.assertRaisesRegex(RuntimeError, 'only from the v4'):
            transition.rollback()
        merge = record(self.root, 'merge')
        with coordination.locked():
            self.envelope(4, [merge, record(self.root, 'network')])
        with self.assertRaisesRegex(RuntimeError, 'reservation present'):
            transition.rollback()
        with coordination.locked():
            self.envelope(4, [merge])
            coordination.request('network', 'P', self.root / 'network.json', '2099-01-01T00:00:00Z')
        with self.assertRaisesRegex(RuntimeError, 'request present'):
            transition.rollback()
        coordination.withdraw('network')
        result = transition.rollback()
        self.assertEqual(result['after'], {'schema_version': 3, 'max_active': 3, 'reservations': [merge]})
        with coordination.locked():
            self.assertEqual(coordination.reservations(), [merge])


if __name__ == '__main__':
    unittest.main()
