#!/usr/bin/env python3
"""Disposable local coordinator protocol checks; no Cloud calls or proof tools."""

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

spec = importlib.util.spec_from_file_location('coordination_v3_transition', HERE / 'coordination-v3-transition.py')
transition = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transition)


def record(base, owner, token=None):
    return {'owner': owner, 'phase_id': 'PHASE', 'ledger': str(base / (owner + '.json')),
            'state_dir': str(base / (owner + '-state')),
            'dispatch_token': token or ('token-' + owner), 'build_id': None,
            'item': {'status': 'DISPATCH_PENDING'}}


CONTROL = b'''import coordination
SELECT_PHASE='P'
SELECT_DEADLINE='D'
def authorized_phase(a): return SELECT_PHASE
def run():
    coordination.locked()
    coordination.reservations()
    coordination.require_capacity('x', '/tmp/x')
    coordination.reserve({})
    coordination.update({})
    coordination.clear('x')
'''


class CoordinatorV3Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        old = coordination.COORDINATION
        coordination.COORDINATION = self.root / 'coordination'
        self.addCleanup(setattr, coordination, 'COORDINATION', old)

    def activate(self, records=()):
        coordination.write(coordination.COORDINATION / 'active.json',
                           {'schema_version': 3, 'max_active': 3, 'reservations': list(records)})

    def test_default_v2_and_v3_three_owners(self):
        with coordination.locked():
            coordination.reserve(record(self.root, 'select-sort4'))
            self.assertEqual(coordination.protocol(), (2, 2))
            coordination.clear('token-select-sort4')
            self.assertEqual(coordination.protocol(), (2, 2))
            self.activate()
            for owner in ('select-sort4', 'merge', 'verifast'):
                coordination.reserve(record(self.root, owner))
            self.assertEqual(len(coordination.reservations()), 3)
            with self.assertRaisesRegex(RuntimeError, 'occupied'):
                coordination.reserve(record(self.root, 'fourth'))
            with self.assertRaisesRegex(RuntimeError, 'Owner or ledger'):
                coordination.reserve(record(self.root, 'merge', 'other-token'))
            duplicate_ledger = record(self.root, 'fourth')
            duplicate_ledger['ledger'] = str(self.root / 'merge.json')
            with self.assertRaisesRegex(RuntimeError, 'Owner or ledger'):
                coordination.reserve(duplicate_ledger)
            coordination.clear('token-verifast')
            aliased_ledger = record(self.root, 'verifast')
            aliased_ledger['ledger'] = str(self.root / 'ignored' / '..' / 'merge.json')
            with self.assertRaisesRegex(RuntimeError, 'Owner or ledger'):
                coordination.reserve(aliased_ledger)
            with self.assertRaisesRegex(RuntimeError, 'Unsupported v3'):
                coordination.reserve(record(self.root, 'fourth'))

    def test_unresolved_untracked_and_peer_preservation(self):
        first = record(self.root, 'select-sort4')
        second = record(self.root, 'merge')
        with coordination.locked():
            self.activate([first])
            ongoing = [{'id': 'visible-first', 'tags': [first['dispatch_token']]},
                       {'id': 'external', 'tags': []}]
            coordination.require_capacity('merge', second['ledger'], ongoing)
            coordination.reserve(second)
            with self.assertRaisesRegex(RuntimeError, 'occupied'):
                coordination.require_capacity('verifast', self.root / 'verifast.json', ongoing)
            updated = {**second, 'build_id': 'build-merge'}
            coordination.update(updated)
            self.assertEqual(coordination.active('select-sort4'), first)
            coordination.clear(first['dispatch_token'])
            self.assertEqual(coordination.reservations(), [updated])
            self.assertEqual(coordination.protocol(), (3, 3))
            with self.assertRaisesRegex(RuntimeError, 'Build ID changed'):
                coordination.update({**updated, 'build_id': 'other'})

    def clients(self):
        clients, acks = {}, {}
        source = (HERE / 'coordination.py').read_bytes()
        hash_value = hashlib.sha256(source).hexdigest()
        for owner in sorted(coordination.V3_OWNERS):
            root = self.root / owner
            folder = root / 'research/challenge-8/cloud-build'
            folder.mkdir(parents=True)
            (folder / 'coordination.py').write_bytes(source)
            (folder / 'control.py').write_bytes(CONTROL)
            clients[owner] = root
            ack = self.root / (owner + '-ack.json')
            ack.write_text(json.dumps({'owner': owner, 'coordination_sha256': hash_value,
                                       'control_sha256': hashlib.sha256(CONTROL).hexdigest(),
                                       'baseline_control_commit': 'a' * 40,
                                       'infra_commit': 'b' * 40}))
            acks[owner] = ack
        return clients, acks

    def test_migration_preserves_active_records_and_rejects_old_v2(self):
        first = record(self.root, 'select-sort4')
        first['build_id'] = 'live-build'
        second = record(self.root, 'merge')
        clients, acks = self.clients()
        with coordination.locked():
            coordination.save_reservations([first, second])
        def committed(args):
            return (HERE / 'coordination.py').read_bytes() if args[-1].endswith('coordination.py') else CONTROL
        with patch.object(transition.subprocess, 'check_output', side_effect=committed), \
                patch.object(transition.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)):
            result = transition.migrate(clients, acks)
        self.assertEqual(result['active_tokens'], [first['dispatch_token'], second['dispatch_token']])
        envelope = coordination.read(coordination.COORDINATION / 'active.json')
        self.assertEqual(envelope, {'schema_version': 3, 'max_active': 3,
                                    'reservations': [first, second]})
        # Execute the exact v2 reader from the pre-transition protocol commit.
        source = subprocess.check_output(['git', '-C', str(HERE), 'show',
            '4058e8bf45eb567e4656d953274c96bf8488a7a3:research/challenge-8/cloud-build/coordination.py'])
        old_path = self.root / 'coordination-v2.py'
        old_path.write_bytes(source)
        old_spec = importlib.util.spec_from_file_location('historical_coordination_v2', old_path)
        old = importlib.util.module_from_spec(old_spec)
        old_spec.loader.exec_module(old)
        old.COORDINATION = coordination.COORDINATION
        with self.assertRaisesRegex(RuntimeError, 'Unsupported Cloud Build coordination protocol'):
            old.reservations()
        with coordination.locked():
            coordination.reserve(record(self.root, 'verifast'))
            coordination.clear(second['dispatch_token'])
            self.assertEqual(coordination.protocol(), (3, 3))

    def test_migration_rejects_incomplete_adoption_without_writing(self):
        clients, acks = self.clients()
        with coordination.locked():
            coordination.save_reservations([record(self.root, 'select-sort4')])
        before = (coordination.COORDINATION / 'active.json').read_bytes()
        bad = json.loads(acks['merge'].read_text())
        bad['coordination_sha256'] = '0' * 64
        acks['merge'].write_text(json.dumps(bad))
        with patch.object(transition.subprocess, 'check_output', return_value=CONTROL):
            with self.assertRaisesRegex(RuntimeError, 'acknowledgment'):
                transition.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
