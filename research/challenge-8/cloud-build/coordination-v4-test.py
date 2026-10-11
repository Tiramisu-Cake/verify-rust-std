#!/usr/bin/env python3
"""Synthetic, disposable coordinator checks; no Cloud or proof tool imports."""

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

spec = importlib.util.spec_from_file_location('coordination_v4_transition', HERE / 'coordination-v4-transition.py')
transition = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transition)
OWNERS = ('select-sort4', 'merge', 'verifast', 'refinedrust-feasibility')
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


def record(base, owner):
    return {'owner': owner, 'phase_id': 'PHASE', 'ledger': str(base / (owner + '.json')),
            'state_dir': str(base / (owner + '-state')), 'dispatch_token': 'token-' + owner,
            'build_id': None,
            'item': {'owner': owner, 'phase_id': 'PHASE', 'dispatch_token': 'token-' + owner,
                     'status': 'DISPATCH_PENDING'},
            'submitted_utc': '2026-10-12T00:00:00Z', 'receipt': {'sha256': 'a' * 64}}


class CoordinatorV4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='refinedrust-feasibility-v4-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        old = coordination.COORDINATION
        coordination.COORDINATION = self.root / 'coordinator'
        self.addCleanup(setattr, coordination, 'COORDINATION', old)
        old_proc_root = transition.PROC_ROOT
        transition.PROC_ROOT = self.root / 'proc'
        transition.PROC_ROOT.mkdir()
        self.addCleanup(setattr, transition, 'PROC_ROOT', old_proc_root)
        self.read_ongoing_original = transition.read_ongoing
        inventory_patch = patch.object(transition, 'read_ongoing', return_value=[])
        self.mock_inventory = inventory_patch.start()
        self.addCleanup(inventory_patch.stop)

    def migrate(self, clients, acks):
        return transition.migrate(clients, acks, configuration=transition.CLOUD_IDENTITY[0],
                                  account=transition.CLOUD_IDENTITY[1],
                                  project=transition.CLOUD_IDENTITY[2])

    def activate(self, version=4, records=(), **extra):
        coordination.write(coordination.COORDINATION / 'active.json',
                           {'schema_version': version, 'max_active': version,
                            'reservations': list(records), **extra})

    def test_version_preservation_and_four_owners(self):
        with coordination.locked():
            for version in (2, 3, 4):
                self.activate(version, meta={'started_utc': '2026-10-12T00:00:00Z'})
                coordination.reserve(record(self.root, OWNERS[0]))
                coordination.clear('token-' + OWNERS[0])
                self.assertEqual(coordination.protocol(), (version, version))
                self.assertEqual(coordination.read(coordination.COORDINATION / 'active.json')['meta'],
                                 {'started_utc': '2026-10-12T00:00:00Z'})
            for owner in OWNERS:
                coordination.reserve(record(self.root, owner))
            self.assertEqual(len(coordination.reservations()), 4)
            with self.assertRaisesRegex(RuntimeError, 'occupied'):
                coordination.reserve(record(self.root, 'fifth'))
            with self.assertRaisesRegex(RuntimeError, 'Owner or ledger'):
                coordination.reserve({**record(self.root, OWNERS[1]), 'dispatch_token': 'new-token'})
            other = record(self.root, 'fifth')
            other['ledger'] = str(self.root / OWNERS[1] / '..' / (OWNERS[1] + '.json'))
            with self.assertRaisesRegex(RuntimeError, 'Owner or ledger'):
                coordination.reserve(other)
            with self.assertRaisesRegex(RuntimeError, 'changed'):
                coordination.clear('unknown-token')
            with self.assertRaisesRegex(RuntimeError, 'disappeared'):
                coordination.update(record(self.root, 'fifth'))
            coordination.clear('token-' + OWNERS[3])
            with self.assertRaisesRegex(RuntimeError, 'Unsupported v4'):
                coordination.reserve(record(self.root, 'fifth'))

    def test_untracked_pending_and_exact_updates(self):
        first, second = record(self.root, OWNERS[0]), record(self.root, OWNERS[1])
        with coordination.locked():
            self.activate(records=[first])
            ongoing = [{'id': 'build-first', 'tags': [first['dispatch_token']]},
                       {'id': 'external-one', 'tags': []}, {'id': 'external-two', 'tags': []},
                       {'id': 'external-three', 'tags': []}]
            with self.assertRaisesRegex(RuntimeError, 'occupied'):
                coordination.require_capacity(OWNERS[1], second['ledger'], ongoing)
            coordination.require_capacity(OWNERS[1], second['ledger'], ongoing[:2])
            coordination.reserve(second)
            updated = {**second, 'build_id': 'build-merge', 'observed_utc': 'now'}
            partial_update = updated.copy()
            partial_update.pop('receipt')
            coordination.update(partial_update)
            self.assertEqual(coordination.active(OWNERS[0]), first)
            self.assertEqual(coordination.active(OWNERS[1]), updated)
            with self.assertRaisesRegex(RuntimeError, 'Build ID changed'):
                coordination.update({**updated, 'build_id': 'different'})
            with self.assertRaisesRegex(RuntimeError, 'identity changed'):
                coordination.update({**updated, 'ledger': str(self.root / 'other')})
            with self.assertRaisesRegex(RuntimeError, 'duplicate ongoing Build ID'):
                coordination.require_capacity(OWNERS[2], self.root / 'vf.json', [ongoing[0], ongoing[0]])
            with self.assertRaisesRegex(RuntimeError, 'duplicate ongoing Build token'):
                coordination.require_capacity(OWNERS[2], self.root / 'vf.json',
                                              [{'id': 'x', 'tags': ['token-x', 'token-x']}])
            with self.assertRaisesRegex(RuntimeError, 'matches multiple'):
                coordination.require_capacity(OWNERS[2], self.root / 'vf.json',
                                              [{'id': 'build-merge', 'tags': [first['dispatch_token']]}])
            with self.assertRaisesRegex(RuntimeError, 'conflicts'):
                coordination.require_capacity(OWNERS[2], self.root / 'vf.json',
                                              [{'id': 'build-merge', 'tags': []}])
            coordination.clear(first['dispatch_token'])
            self.assertEqual(coordination.reservations(), [updated])

    def test_corrupted_records_fail_closed(self):
        valid = record(self.root, OWNERS[0])
        corruptions = [
            [valid, {**valid, 'dispatch_token': 'other'}],
            [{**valid, 'ledger': 'relative.json'}],
            [{**valid, 'dispatch_token': ''}],
            [{**valid, 'state_dir': 'relative'}],
            [{**valid, 'build_id': 12}],
            [{**valid, 'owner': 'unregistered'}],
            [{**valid, 'item': {'dispatch_token': 'conflicting'}}],
            [{**valid, 'build_id': 'top',
              'item': {**valid['item'], 'build_id': 'different'}}],
            [valid, {**record(self.root, OWNERS[1]), 'build_id': 'same'},
             {**record(self.root, OWNERS[2]), 'build_id': 'same'}],
        ]
        for records in corruptions:
            with self.subTest(records=records), coordination.locked():
                self.activate(records=records)
                with self.assertRaises(RuntimeError):
                    coordination.reservations()
        with coordination.locked():
            self.activate()
            with self.assertRaisesRegex(RuntimeError, 'Unsupported'):
                coordination.write(coordination.COORDINATION / 'active.json',
                                   {'schema_version': 5, 'max_active': 5, 'reservations': []})
                coordination.protocol()

    def test_ack_issuance_is_read_only(self):
        clients, _ = self.clients()
        root = clients[OWNERS[0]]
        before = sorted(str(p.relative_to(root)) for p in root.rglob('*'))
        git, ancestor = self.git_mock()
        with git, ancestor:
            ack = transition.make_ack(OWNERS[0], root, 'a' * 40, 'b' * 40,
                                      'refs/heads/owner-' + OWNERS[0], self.review(OWNERS[0]))
        self.assertEqual(ack['owner'], OWNERS[0])
        self.assertEqual(ack['infra_commit'], 'b' * 40)
        self.assertEqual(before, sorted(str(p.relative_to(root)) for p in root.rglob('*')))
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'owner-reviewed'):
            transition.make_ack(OWNERS[0], root, 'a' * 40, 'b' * 40,
                                'refs/heads/owner-' + OWNERS[0], {})

    def test_origin_requires_exact_github_fork(self):
        self.assertTrue(transition.project_origin('https://github.com/Tiramisu-Cake/verify-rust-std.git'))
        self.assertTrue(transition.project_origin('git@github.com:Tiramisu-Cake/verify-rust-std.git'))
        self.assertTrue(transition.project_origin('ssh://git@github.com/Tiramisu-Cake/verify-rust-std.git'))
        self.assertFalse(transition.project_origin(
            'https://evil.example/Tiramisu-Cake/verify-rust-std.git'))
        self.assertFalse(transition.project_origin(
            'https://github.com.evil.example/Tiramisu-Cake/verify-rust-std.git'))

    def test_api_inventory_uses_explicit_identity_and_region(self):
        with patch.object(transition.subprocess, 'check_output', return_value='[]') as command:
            self.assertEqual(self.read_ongoing_original(*transition.CLOUD_IDENTITY), [])
        args, kwargs = command.call_args
        self.assertEqual(args[0], ['gcloud', '--configuration=smallsort-ci',
                                   '--account=smallsort-dispatcher@smallsort-ci.iam.gserviceaccount.com',
                                   '--project=smallsort-ci', 'builds', 'list', '--ongoing',
                                   '--region=global', '--format=json'])
        self.assertEqual(kwargs['timeout'], transition.API_TIMEOUT_SECONDS)
        with self.assertRaisesRegex(RuntimeError, 'canonical project account'):
            self.read_ongoing_original('other', transition.CLOUD_IDENTITY[1], transition.CLOUD_IDENTITY[2])

    def test_migration_refuses_inconsistent_api_inventory(self):
        clients, acks = self.clients()
        first = record(self.root, OWNERS[0])
        with coordination.locked():
            self.activate(version=3, records=[first])
        before = (coordination.COORDINATION / 'active.json').read_bytes()
        git, ancestor = self.git_mock()
        self.mock_inventory.return_value = [{'id': 'external-' + str(i), 'tags': []}
                                             for i in range(4)]
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'exceeds v4 capacity'):
            self.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)
        self.mock_inventory.return_value = [{'id': 'same', 'tags': []}, {'id': 'same', 'tags': []}]
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'duplicate ongoing Build ID'):
            self.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)
        self.mock_inventory.return_value = [
            {'id': 'one', 'tags': [first['dispatch_token']]},
            {'id': 'two', 'tags': [first['dispatch_token']]},
        ]
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'conflicts'):
            self.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)

    def test_item_only_build_ids_are_unique_and_match_api(self):
        clients, acks = self.clients()
        first = record(self.root, OWNERS[0])
        first['item']['build_id'] = 'item-only-id'
        second = record(self.root, OWNERS[1])
        second['item']['build_id'] = 'item-only-id'
        with coordination.locked():
            self.activate(version=3, records=[first, second])
        before = (coordination.COORDINATION / 'active.json').read_bytes()
        git, ancestor = self.git_mock()
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'duplicate reservation Build ID'):
            self.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)

        with coordination.locked():
            self.activate(version=3, records=[first])
        before = (coordination.COORDINATION / 'active.json').read_bytes()
        self.mock_inventory.return_value = [{'id': 'other-id', 'tags': [first['dispatch_token']]}]
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'conflicts with reserved token or Build ID'):
            self.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)
        self.mock_inventory.return_value = [{'id': 'item-only-id', 'tags': [first['dispatch_token']]}]
        with git, ancestor:
            result = self.migrate(clients, acks)
        self.assertEqual(result['occupied_slots'], 1)

    def test_legacy_minimal_records_read_but_cannot_migrate(self):
        minimal = {'owner': OWNERS[0], 'ledger': str(self.root / 'old-ledger.json'),
                   'dispatch_token': 'old-token'}
        clients, acks = self.clients()
        for version in (2, 3):
            with coordination.locked():
                self.activate(version=version, records=[minimal])
                self.assertEqual(coordination.reservations(), [minimal])
            before = (coordination.COORDINATION / 'active.json').read_bytes()
            if version == 3:
                git, ancestor = self.git_mock()
                with git, ancestor, self.assertRaisesRegex(RuntimeError, 'reservation'):
                    self.migrate(clients, acks)
                self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)

    def test_dispatcher_conflict_and_inaccessible_process_refuse_without_write(self):
        clients, acks = self.clients()
        with coordination.locked():
            self.activate(version=3)
        before = (coordination.COORDINATION / 'active.json').read_bytes()
        process = transition.PROC_ROOT / '1234'
        process.mkdir()
        (process / 'cmdline').write_bytes(
            b'python3\0/tmp/another-client/research/challenge-8/cloud-build/control.py\0submit\0')
        git, ancestor = self.git_mock()
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'Dispatcher command'):
            self.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'Dispatcher command'):
            transition.make_ack(OWNERS[0], clients[OWNERS[0]], 'a' * 40, 'b' * 40,
                                'refs/heads/owner-' + OWNERS[0], self.review(OWNERS[0]))
        (process / 'cmdline').unlink()
        (process / 'cmdline').mkdir()  # IsADirectoryError stands in for unreadable /proc data.
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'Cannot audit live process'):
            self.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)

    def test_dispatcher_starting_after_preflight_refuses_under_lock(self):
        clients, acks = self.clients()
        with coordination.locked():
            self.activate(version=3)
        before = (coordination.COORDINATION / 'active.json').read_bytes()
        calls = 0

        def start_after_preflight():
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError('Dispatcher command is running')

        git, ancestor = self.git_mock()
        with git, ancestor, patch.object(transition, 'audit_dispatchers', side_effect=start_after_preflight):
            with self.assertRaisesRegex(RuntimeError, 'Dispatcher command'):
                self.migrate(clients, acks)
        self.assertEqual(calls, 2)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)

    def clients(self):
        clients, acks = {}, {}
        source = (HERE / 'coordination.py').read_bytes()
        for owner in OWNERS:
            root = self.root / owner
            folder = root / 'research/challenge-8/cloud-build'
            folder.mkdir(parents=True)
            (folder / 'coordination.py').write_bytes(source)
            (folder / 'control.py').write_bytes(CONTROL)
            clients[owner] = root
            ack = self.root / (owner + '-ack.json')
            ack.write_text(json.dumps({'owner': owner, 'coordination_sha256': hashlib.sha256(source).hexdigest(),
                                       'control_sha256': hashlib.sha256(CONTROL).hexdigest(),
                                       'baseline_control_commit': 'a' * 40, 'infra_commit': 'b' * 40,
                                       'published_ref': 'refs/heads/owner-' + owner,
                                       'review_receipt': self.review(owner)}))
            acks[owner] = ack
        return clients, acks

    def review(self, owner):
        return {'owner': owner, 'review_status': transition.REVIEW_STATUS,
                'baseline_control_commit': 'a' * 40,
                'control_sha256': hashlib.sha256(CONTROL).hexdigest()}

    def git_mock(self):
        def output(args, **kwargs):
            if args[-2:] == ['get-url', 'origin']:
                return 'https://github.com/Tiramisu-Cake/verify-rust-std.git\n'
            if 'ls-remote' in args:
                return 'b' * 40 + '\t' + args[-1] + '\n'
            if args[-1].endswith('coordination.py'):
                return (HERE / 'coordination.py').read_bytes()
            return CONTROL
        return patch.object(transition.subprocess, 'check_output', side_effect=output), patch.object(
            transition.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0))

    def test_migration_empty_active_and_ack_mismatch(self):
        clients, acks = self.clients()
        with coordination.locked():
            self.activate(version=3, metadata={'created': '2026-10-12'})
        before = (coordination.COORDINATION / 'active.json').read_bytes()
        wrong = json.loads(acks[OWNERS[3]].read_text())
        wrong['control_sha256'] = '0' * 64
        acks[OWNERS[3]].write_text(json.dumps(wrong))
        git, ancestor = self.git_mock()
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'acknowledgment'):
            self.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)
        acks[OWNERS[3]].write_text(json.dumps({**wrong, 'control_sha256': hashlib.sha256(CONTROL).hexdigest()}))
        with git, ancestor:
            result = self.migrate(clients, acks)
        self.assertEqual(result['active_tokens'], [])
        self.assertEqual(coordination.read(coordination.COORDINATION / 'active.json')['metadata'],
                         {'created': '2026-10-12'})
        self.assertEqual(coordination.protocol(), (4, 4))
        with git, ancestor, self.assertRaisesRegex(RuntimeError, 'existing v3'):
            self.migrate(clients, acks)

    def test_active_migration_preserves_every_field_and_old_client_refuses(self):
        clients, acks = self.clients()
        records = [record(self.root, OWNERS[0]), record(self.root, OWNERS[1])]
        records[0]['build_id'] = 'live-id'
        with coordination.locked():
            self.activate(version=3, records=records, timestamp='2026-10-12T00:00:00Z',
                          receipt={'source': 'old'})
        before = coordination.read(coordination.COORDINATION / 'active.json')
        git, ancestor = self.git_mock()
        with git, ancestor:
            self.migrate(clients, acks)
        self.assertEqual(coordination.read(coordination.COORDINATION / 'active.json'),
                         {**before, 'schema_version': 4, 'max_active': 4})
        with coordination.locked():
            coordination.reserve(record(self.root, OWNERS[3]))
            self.assertEqual(coordination.protocol(), (4, 4))
            self.assertEqual(coordination.read(coordination.COORDINATION / 'active.json')['receipt'],
                             {'source': 'old'})
        # The frozen v3 client code rejects the new envelope without altering it.
        old_source = subprocess.check_output(['git', '-C', str(HERE), 'show',
            '6e1a8e59c56669abe5e6ec2013478e45ed2cc267:research/challenge-8/cloud-build/coordination.py'])
        old_path = self.root / 'coordination-v3.py'
        old_path.write_bytes(old_source)
        old_spec = importlib.util.spec_from_file_location('historical_coordination_v3', old_path)
        old = importlib.util.module_from_spec(old_spec)
        old_spec.loader.exec_module(old)
        old.COORDINATION = coordination.COORDINATION
        with self.assertRaisesRegex(RuntimeError, 'Unsupported Cloud Build coordination protocol'):
            old.reservations()

    def test_migration_rejects_corruption_and_unpublished_commit(self):
        clients, acks = self.clients()
        with coordination.locked():
            self.activate(version=3, records=[{**record(self.root, OWNERS[0]), 'dispatch_token': ''}])
        before = (coordination.COORDINATION / 'active.json').read_bytes()
        git, ancestor = self.git_mock()
        with git, ancestor, self.assertRaises(RuntimeError):
            self.migrate(clients, acks)
        self.assertEqual((coordination.COORDINATION / 'active.json').read_bytes(), before)
        with coordination.locked():
            self.activate(version=3)
        with git, ancestor:
            ack = json.loads(acks[OWNERS[0]].read_text())
            with patch.object(transition.subprocess, 'check_output', side_effect=lambda args, **kwargs:
                              ('c' * 40 + '\t' + args[-1]) if 'ls-remote' in args else
                              ('https://github.com/Tiramisu-Cake/verify-rust-std.git\n' if 'get-url' in args else
                               ((HERE / 'coordination.py').read_bytes() if args[-1].endswith('coordination.py') else CONTROL))):
                with self.assertRaisesRegex(RuntimeError, 'published branch tip'):
                    transition.check_client(OWNERS[0], clients[OWNERS[0]], ack,
                                            hashlib.sha256((HERE / 'coordination.py').read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
