"""Isolated synthetic dispatcher admission tests; no API or state mutation."""
import datetime
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

CLOUD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CLOUD))
SPEC = importlib.util.spec_from_file_location('a1_dispatch_control_test', CLOUD / 'control.py')
CONTROL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTROL)


def account():
    return dict(phase=CONTROL.A1_PHASE, status='AUTHORIZED', authorization='synthetic owner authorization',
                owner='select-sort4', ceiling_build_seconds=960, remaining_build_seconds=960,
                allowed_lanes=list(CONTROL.A1_LANES), start_utc=CONTROL.A1_START,
                main_deadline_utc=CONTROL.A1_MAIN_DEADLINE, deadline_utc=CONTROL.A1_DEADLINE,
                maximum_builds=1, maximum_build_timeout_seconds=900, builds=[], active_build=None)


class FrozenDateTime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 10, 17, 10, 0, 0, tzinfo=datetime.timezone.utc).astimezone(tz)


class SyntheticDispatcherAdmission(unittest.TestCase):
    def setUp(self):
        self.clock = patch.object(CONTROL.datetime, 'datetime', FrozenDateTime)
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def args(self):
        return SimpleNamespace(phase_id=CONTROL.A1_PHASE, owner='select-sort4',
                               command='submit', lane='o26-sort4-c1-current-recovery',
                               source_mode='pinned-objects', timeout=900)

    def test_exact_account_admitted(self):
        CONTROL.authorized_phase(self.args(), account())

    def test_wrong_account_fields_refused(self):
        for key, bad in [('ceiling_build_seconds', 1920), ('owner', 'other'),
                         ('maximum_builds', 2), ('maximum_build_timeout_seconds', 901),
                         ('start_utc', '2026-10-17T00:28:49Z'),
                         ('deadline_utc', '2026-10-17T12:28:23Z'),
                         ('main_deadline_utc', '2026-10-17T11:58:23Z'),
                         ('allowed_lanes', ['smoke-success']), ('status', 'CLOSED')]:
            with self.subTest(key=key):
                ledger = account(); ledger[key] = bad
                with self.assertRaises(SystemExit):
                    CONTROL.authorized_phase(self.args(), ledger)

    def test_second_build_refused_before_request(self):
        ledger = account(); ledger['builds'] = [{'status': 'SUCCESS'}]
        with patch.object(CONTROL.coordination, 'request', side_effect=AssertionError('must not request')):
            with self.assertRaisesRegex(SystemExit, 'one Build'):
                CONTROL.run_command(self.args(), Path('/unused'), ledger, Path('/unused/ledger'))

    def test_timeout_not_900_refused_before_request(self):
        args = self.args(); args.timeout = 899
        with patch.object(CONTROL.coordination, 'request', side_effect=AssertionError('must not request')):
            with self.assertRaisesRegex(SystemExit, 'timeout 900'):
                CONTROL.run_command(args, Path('/unused'), account(), Path('/unused/ledger'))

    def test_environment_has_only_new_phase(self):
        with patch.object(CONTROL.subprocess, 'check_output', return_value=b'synthetic-profile'):
            env = CONTROL.envs('a' * 40, 'b' * 40, self.args().lane, CONTROL.A1_PHASE)
        self.assertIn('SORT4_A1_PHASE_ID=' + CONTROL.A1_PHASE, env)
        self.assertIn('SORT4_A1_CHECKED_TRAIT_CONTRACT=1', env)
        self.assertIn('SORT4_A1_PROFILE_SHA256=' + CONTROL.digest(b'synthetic-profile'), env)
        self.assertFalse(any(x.startswith('SORT4_ACTUAL_CALLER_ENTRY_PHASE=') for x in env))


if __name__ == '__main__':
    unittest.main()
