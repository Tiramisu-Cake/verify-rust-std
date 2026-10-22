#!/usr/bin/env python3
"""Local service checks for the derived Network client; no Cloud calls, no proof tools."""
import argparse
import datetime
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
spec = importlib.util.spec_from_file_location('network_control', HERE / 'control.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)

NOW = datetime.datetime.now(datetime.timezone.utc)
iso = lambda d: d.strftime('%Y-%m-%dT%H:%M:%SZ')
REG = {'ceiling': 3600, 'lanes': frozenset({'network-r4'}), 'start_utc': iso(NOW - datetime.timedelta(minutes=5)),
       'main_deadline_utc': iso(NOW + datetime.timedelta(minutes=115)),
       'deadline_utc': iso(NOW + datetime.timedelta(minutes=145)),
       'profile': 'research/challenge-8/network/r4/PROFILE.json', 'profile_sha256': '0' * 64, 'timeout': (270, 1200)}


def ledger(**over):
    base = {'phase': 'NETWORK-TEST', 'owner': 'network', 'status': 'AUTHORIZED', 'authorization': 'test',
            'ceiling_build_seconds': 3600, 'allowed_lanes': ['network-r4'], 'start_utc': REG['start_utc'],
            'main_deadline_utc': REG['main_deadline_utc'], 'deadline_utc': REG['deadline_utc']}
    base.update(over)
    return base


def args(**over):
    base = dict(phase_id='NETWORK-TEST', owner='network', timeout=900)
    base.update(over)
    return argparse.Namespace(**base)


class NetworkClientTests(unittest.TestCase):
    def test_committed_table_is_empty(self):
        self.assertEqual(control.NETWORK_PHASES, {})
        with self.assertRaisesRegex(SystemExit, 'not registered'):
            control.authorized_phase(args(), ledger())

    def test_inherited_select_phase_unreachable(self):
        a = args(phase_id=control.A1_R19_PHASE, owner='select-sort4')
        with self.assertRaisesRegex(SystemExit, 'not registered'):
            control.authorized_phase(a, ledger(phase=control.A1_R19_PHASE, owner='select-sort4'))

    def test_registered_phase(self):
        with patch.dict(control.NETWORK_PHASES, {'NETWORK-TEST': REG}):
            self.assertEqual(control.authorized_phase(args(), ledger()), control.utc(REG['deadline_utc']))
            for a, l, why in ((args(owner='select-sort4'), ledger(), 'only owner network'),
                              (args(), ledger(owner='merge'), 'only owner network'),
                              (args(), ledger(allowed_lanes=['other']), 'lanes'),
                              (args(), ledger(ceiling_build_seconds=1800), 'ceiling'),
                              (args(), ledger(deadline_utc=iso(NOW + datetime.timedelta(hours=9))), 'deadline_utc'),
                              (args(), ledger(status='CLOSED'), 'Phase account'),
                              (args(phase_id='OTHER'), ledger(), 'must match')):
                with self.assertRaisesRegex(SystemExit, why):
                    control.authorized_phase(a, l)

    def test_past_deadline(self):
        past = dict(REG, deadline_utc=iso(NOW - datetime.timedelta(minutes=1)))
        with patch.dict(control.NETWORK_PHASES, {'NETWORK-TEST': past}):
            with self.assertRaisesRegex(SystemExit, 'deadline has passed'):
                control.authorized_phase(args(), ledger(deadline_utc=past['deadline_utc']))

    def test_submit_gate(self):
        with patch.dict(control.NETWORK_PHASES, {'NETWORK-TEST': REG}):
            control.network_submit_gate(args())
            for t in (269, 1201):
                with self.assertRaisesRegex(SystemExit, 'timeout'):
                    control.network_submit_gate(args(timeout=t))
        ended = dict(REG, main_deadline_utc=iso(NOW - datetime.timedelta(seconds=1)))
        with patch.dict(control.NETWORK_PHASES, {'NETWORK-TEST': ended}):
            with self.assertRaisesRegex(SystemExit, 'main window ended'):
                control.network_submit_gate(args())
        early = dict(REG, start_utc=iso(NOW + datetime.timedelta(minutes=1)))
        with patch.dict(control.NETWORK_PHASES, {'NETWORK-TEST': early}):
            with self.assertRaisesRegex(SystemExit, 'not started'):
                control.network_submit_gate(args())

    def test_budget_and_naive_time(self):
        self.assertEqual(control.network_time_budget(900)['work_seconds'], 660)
        for bad in (269, 1201, 900.0):
            with self.assertRaises(ValueError):
                control.network_time_budget(bad)
        with self.assertRaises(ValueError):
            control.utc('2026-10-22T10:00:00')

    def test_profile_binding(self):
        with patch.dict(control.NETWORK_PHASES, {'NETWORK-TEST': REG}):
            with patch.object(control.subprocess, 'check_output', return_value=b'x'):
                with self.assertRaisesRegex(SystemExit, 'profile bytes differ'):
                    control.network_env('a' * 40, 'NETWORK-TEST')
            good = dict(REG, profile_sha256=control.digest(b'x'))
            with patch.dict(control.NETWORK_PHASES, {'NETWORK-TEST': good}), \
                    patch.object(control.subprocess, 'check_output', return_value=b'x'):
                self.assertEqual(control.network_env('a' * 40, 'NETWORK-TEST'),
                                 ['NETWORK_PHASE_ID=NETWORK-TEST', 'NETWORK_PROFILE_SHA256=' + control.digest(b'x')])


if __name__ == '__main__':
    unittest.main()
