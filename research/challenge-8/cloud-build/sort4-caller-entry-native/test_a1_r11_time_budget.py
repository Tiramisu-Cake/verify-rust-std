"""Isolated R11 time/exit capture service tests; no Cloud or proof work."""
import base64
import datetime
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

CLOUD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CLOUD))
SPEC = importlib.util.spec_from_file_location('r11_time_control', CLOUD / 'control.py')
CONTROL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTROL)

class TimeBudget(unittest.TestCase):
    def config(self, seconds, lane='smoke-error', phase=None):
        phase = CONTROL.A1_R11_PHASE if phase is None else phase
        profile = json.dumps({'authorization_phase_id': phase,
                              'experiment_protocol_phase_id': CONTROL.A1_PHASE}).encode()
        with patch.object(CONTROL.subprocess, 'check_output', return_value=profile):
            return CONTROL.config('a'*40, 'b'*40, lane, seconds, 'synthetic-time', phase_id=phase)

    def test_explicit_package_and_teardown_reserve_at_boundaries(self):
        for seconds in (90, 300, 1000, 1200):
            with self.subTest(seconds=seconds):
                budget = CONTROL.r11_time_budget(seconds)
                self.assertEqual(budget['package_reserve'] + budget['work_seconds'], seconds)
                self.assertGreaterEqual(budget['work_seconds'], 30)
                self.assertLess(budget['soft_margin'], budget['work_seconds'])
                if seconds >= 300:
                    self.assertEqual(budget['package_reserve'], 240)
                if seconds >= 1000:
                    self.assertEqual(budget['soft_margin'], 60)
                body = self.config(seconds)['steps'][0]['args'][1]
                self.assertIn(f"+ {budget['work_seconds']} - {budget['soft_margin']}", body)
                self.assertIn(f'"{budget["work_seconds"]}s"', body)
                self.assertIn('--kill-after=10s', body)

    def test_missing_null_wrongtype_or_out_of_range_time_is_refused(self):
        for value in (None, '1200', True, 1200.0, 89, 1201):
            with self.subTest(value=value), self.assertRaises(ValueError):
                CONTROL.r11_time_budget(value)

    def test_historical_phase_time_plan_unchanged(self):
        body = self.config(900, phase=CONTROL.A1_R9_PHASE)['steps'][0]['args'][1]
        self.assertIn('+ 830 - 15', body)
        self.assertIn('"830s"', body)

    def test_1200_reaches_normal_admission_but_1201_never_requests(self):
        class Clock(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return cls.fromisoformat(CONTROL.A1_R11_START.replace('Z', '+00:00')).astimezone(tz)
        ledger = json.loads((Path(__file__).parent / 'BUDGET-A1-CHECKED-CALLER-2026-10-21-R11.json').read_text())
        ledger.update(status='AUTHORIZED', builds=[], active_build=None, remaining_build_seconds=3600, used_build_seconds=0)
        args = SimpleNamespace(phase_id=CONTROL.A1_R11_PHASE, owner='select-sort4', command='submit',
                               lane='o26-sort4-c1-current-recovery', source_mode='pinned-objects', timeout=1200)
        class ReachedAdmission(Exception): pass
        with patch.object(CONTROL.datetime, 'datetime', Clock), patch.object(CONTROL.coordination, 'request', side_effect=ReachedAdmission):
            with self.assertRaises(ReachedAdmission):
                CONTROL.run_command(args, Path('/unused'), ledger, Path('/unused/ledger'))
            args.timeout = 1201
            with self.assertRaises(SystemExit):
                CONTROL.run_command(args, Path('/unused'), ledger, Path('/unused/ledger'))

    def run_generated_body(self, lane):
        cfg = self.config(1000, lane=lane)
        raw = b'{"synthetic":"config continuity"}\n'
        encoded = base64.b64encode(gzip.compress(raw)).decode()
        with tempfile.TemporaryDirectory(prefix='r11-generated-exit-') as td:
            root = Path(td)
            body = cfg['steps'][0]['args'][1].replace('$$', '$').replace('/workspace', str(root))
            env = dict(os.environ, SUBMITTED_CONFIG_SHA=hashlib.sha256(raw).hexdigest(),
                       **{'CONFIG_PART_'+str(i): encoded if i == 0 else '' for i in range(8)})
            result = subprocess.run(['bash', '-ceu', body], capture_output=True, text=True, env=env)
            evidence = root / 'evidence'
            return result, (evidence/'run-exit.txt').read_text(), (evidence/'full-stdout.log').read_text(), (evidence/'full-stderr.log').read_text()

    def test_original_error_exit_and_partial_output_survive_outer_success(self):
        result, code, out, err = self.run_generated_body('smoke-error')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(code, '42\n')
        self.assertIn('CONTROLLED_ERROR_START', out)
        self.assertIn('deliberate exit 42', err)

    def test_original_timeout_and_partial_output_survive(self):
        result, code, out, err = self.run_generated_body('smoke-timeout')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(code, '124\n')
        self.assertIn('INTERNAL_TIMEOUT_START', out)

if __name__ == '__main__': unittest.main()
