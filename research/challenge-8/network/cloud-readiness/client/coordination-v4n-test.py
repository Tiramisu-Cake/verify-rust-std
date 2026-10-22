#!/usr/bin/env python3
"""Disposable local checks for the v4 (four owners, cap 3) candidate; no Cloud calls."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import coordination

spec = importlib.util.spec_from_file_location('v4n_transition', HERE / 'coordination-v4n-transition.py')
transition = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transition)

# Deployed v3 coordinator (Select = Merge client blob), read from Git.
V3_BLOB = '1fd8b97bb11130325e5e9ea5ee3bf57b9adf0caf'


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


class CoordinatorV4NetworkTests(unittest.TestCase):
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
            with self.assertRaisesRegex(RuntimeError, 'occupied'):
                coordination.reserve(record(self.root, 'network'))

    def test_v4_four_owners_cap_three(self):
        with coordination.locked():
            self.envelope(4)
            self.assertEqual(coordination.protocol(), (4, 3))
            for owner in ('network', 'select-sort4', 'merge'):
                coordination.reserve(record(self.root, owner))
            with self.assertRaisesRegex(RuntimeError, 'occupied'):
                coordination.reserve(record(self.root, 'verifast'))
            with self.assertRaisesRegex(RuntimeError, 'Owner or ledger'):
                coordination.reserve(record(self.root, 'network', 'other-token'))
            coordination.clear('token-merge')
            with self.assertRaisesRegex(RuntimeError, 'Unsupported v4'):
                coordination.reserve(record(self.root, 'fifth'))
            with self.assertRaisesRegex(RuntimeError, 'Unsupported v4'):
                coordination.request('fifth', 'P', self.root / 'fifth.json', '2099-01-01T00:00:00Z')
            coordination.request('network', 'P', self.root / 'network.json', '2099-01-01T00:00:00Z')
            self.assertEqual([r['owner'] for r in coordination.reservations()], ['network', 'select-sort4'])

    def test_v4_rejects_wrong_cap_and_unknown_owner_record(self):
        with coordination.locked():
            self.envelope(4, cap=4)
            with self.assertRaisesRegex(RuntimeError, 'Unsupported Cloud Build coordination protocol'):
                coordination.protocol()
            self.envelope(4, [record(self.root, 'refinedrust-feasibility')])
            with self.assertRaisesRegex(RuntimeError, 'Unsupported v4'):
                coordination.reservations()

    def test_deployed_v3_client_fails_closed_on_v4(self):
        v3 = load_v3()
        v3.COORDINATION = coordination.COORDINATION
        with coordination.locked():
            self.envelope(4, [record(self.root, 'network')])
        with v3.locked():
            for call in (v3.protocol, v3.reservations,
                         lambda: v3.require_capacity('merge', self.root / 'merge.json')):
                with self.assertRaisesRegex(RuntimeError, 'Unsupported Cloud Build coordination protocol'):
                    call()

    def clients(self, mutate=None):
        source = (HERE / 'coordination.py').read_bytes()
        sha = hashlib.sha256(source).hexdigest()
        clients, acks = {}, {}
        for owner in sorted(coordination.V4_OWNERS):
            root = self.root / owner
            path = root / transition.CLIENT_PATH
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(source if owner != mutate else source + b'#')
            clients[owner] = root
            ack = self.root / (owner + '-ack.json')
            ack.write_text(json.dumps({'owner': owner, 'coordination_sha256': sha, 'infra_commit': 'b' * 40}))
            acks[owner] = ack
        return clients, acks, source

    def test_migration_preserves_records_and_requires_all_owners(self):
        first = {**record(self.root, 'select-sort4'), 'build_id': 'live'}
        second = record(self.root, 'merge')
        with coordination.locked():
            self.envelope(3, [first, second])
        clients, acks, source = self.clients()
        with patch.object(transition.subprocess, 'check_output', return_value=source):
            partial = dict(clients); partial.pop('network')
            with self.assertRaisesRegex(RuntimeError, 'all four'):
                transition.migrate(partial, acks)
            result = transition.migrate(clients, acks)
        self.assertEqual(result['active_tokens'], ['token-select-sort4', 'token-merge'])
        with coordination.locked():
            self.assertEqual(coordination.protocol(), (4, 3))
            self.assertEqual(coordination.reservations(), [first, second])
        with patch.object(transition.subprocess, 'check_output', return_value=source):
            with self.assertRaisesRegex(RuntimeError, 'only from the v3'):
                transition.migrate(clients, acks)

    def test_migration_refuses_stale_client_or_bad_ack(self):
        with coordination.locked():
            self.envelope(3)
        clients, acks, source = self.clients(mutate='verifast')
        with patch.object(transition.subprocess, 'check_output', return_value=source):
            with self.assertRaisesRegex(RuntimeError, 'differs'):
                transition.migrate(clients, acks)
        clients, acks, source = self.clients()
        bad = json.loads(Path(acks['network']).read_text()); bad['coordination_sha256'] = '0' * 64
        Path(acks['network']).write_text(json.dumps(bad))
        with patch.object(transition.subprocess, 'check_output', return_value=source):
            with self.assertRaisesRegex(RuntimeError, 'ACK'):
                transition.migrate(clients, acks)
        with coordination.locked():
            self.assertEqual(coordination.protocol(), (3, 3))


if __name__ == '__main__':
    unittest.main()
