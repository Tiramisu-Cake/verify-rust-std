#!/usr/bin/env python3
"""Synthetic pin/dispatch/admission tests; never invoke any proof/Cloud tool."""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


compat = load('r1_compat', HERE/'generated-glue-compatibility-controls.py')
dispatch = load('r1_dispatch', HERE/'first-comparator-dispatch.py')
control = load('r1_control', HERE.parent/'control.py')
V8 = 'experimental-merge-actual-glue-body-v8'
FIRST = 'experimental-merge-first-callback-u64-v1'


class Clock(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 10, 18, 19, 30, tzinfo=datetime.timezone.utc)


class ServiceTests(unittest.TestCase):
    def test_actual_profile_pins_have_immutable_provenance(self):
        tool = '/root/verifast-merge-actual-glue'
        source = 'src/refinement_checker/refinement_checker.ml'
        for name, commit, manifest in (
            (V8, 'a158398e336edce9817f62a55733a3470a986d7b', 'GLUE-PROFILE-V8-20261012.json'),
            (FIRST, '52ba7e2506af993007675269111a24d15406d58b', 'GLUE-PROFILE.json')):
            with self.subTest(profile=name):
                data = subprocess.check_output(['git', '-C', tool, 'show', f'{commit}:{source}'])
                expected = compat.PINNED_REFINER_SOURCE_SHA256_BY_PROFILE[name]
                self.assertEqual(hashlib.sha256(data).hexdigest(), expected)
                self.assertEqual(json.loads((HERE/manifest).read_text())['refiner_core_source_sha256'], expected)
                self.assertEqual(data.decode().count(compat.LEGACY_DROP_DEFAULTS), 2)
                self.assertEqual(data.decode().count('kind=Drop {'), 2)

    def test_synthetic_gate_refuses_unknown_corruption_and_wrong_count(self):
        with tempfile.TemporaryDirectory() as temp:
            source, binary = Path(temp)/'source.ml', Path(temp)/'refiner'
            binary.write_bytes(b'synthetic non-executable binary identity')
            valid = (compat.LEGACY_DROP_DEFAULTS+'\n')*2
            source.write_text(valid)
            expected = hashlib.sha256(source.read_bytes()).hexdigest()
            with patch.object(compat, 'PINNED_REFINER_SOURCE_SHA256_BY_PROFILE', {V8: expected, FIRST: expected}):
                for profile in (V8, FIRST):
                    self.assertTrue(compat._synthetic_defaults_gate(source, binary, profile)['matched'])
                self.assertFalse(compat._synthetic_defaults_gate(source, binary, 'unknown')['matched'])
                source.write_bytes(b'X'+source.read_bytes()[1:])
                self.assertFalse(compat._synthetic_defaults_gate(source, binary, FIRST)['matched'])
            for count in (0, 1, 3):
                source.write_text((compat.LEGACY_DROP_DEFAULTS+'\n')*count)
                expected = hashlib.sha256(source.read_bytes()).hexdigest()
                with patch.object(compat, 'PINNED_REFINER_SOURCE_SHA256_BY_PROFILE', {FIRST: expected}):
                    self.assertFalse(compat._synthetic_defaults_gate(source, binary, FIRST)['matched'])

    def test_dispatch_receipts_cannot_claim_skip_or_invocation_contradictorily(self):
        binding = {'proof_sha': 'a'*40, 'profile': FIRST, 'profile_sha256': 'b'*64, 'tool_commit': 'c'*40}
        with tempfile.TemporaryDirectory() as temp:
            for status, ready in [('NOT_RUN_PREREQUISITE_FAILED', False), ('DISPATCHED', True),
                                  ('CAMPAIGN_RETURNED', True), ('INCONCLUSIVE_CAMPAIGN_EXCEPTION', True)]:
                row = dispatch.record(Path(temp), status=status, binding=binding,
                                      prerequisites={'b1_matched': ready})
                self.assertFalse(row['accepted'])
                self.assertFalse(row['proof_credit'])
                self.assertEqual(json.loads((Path(temp)/'first-comparator-dispatch/classification.json').read_text()), row)
            for status, ready in [('NOT_RUN_PREREQUISITE_FAILED', True), ('DISPATCHED', False)]:
                with self.assertRaises(ValueError):
                    dispatch.record(Path(temp), status=status, binding=binding, prerequisites={'b1_matched': ready})
            with self.assertRaises(ValueError):
                dispatch.record(Path(temp), status='DISPATCHED', binding={}, prerequisites={'b1_matched': True})

    def test_time_window_allows_sequential_attempts_without_old960cap(self):
        path = HERE/'FIRST-COMPARATOR-R1-BUDGET-20261018.json'
        ledger = json.loads(path.read_text())
        ledger.update(status='AUTHORIZED', builds=[{'status': 'FAILURE', 'accounted': True}],
                      used_build_seconds=1600, remaining_build_seconds=17360)
        args = SimpleNamespace(phase_id=ledger['phase'], ledger=path, owner='merge', command='submit',
                               timeout=900, lane='merge', source_mode='pinned-objects')
        with patch.object(control.datetime, 'datetime', Clock):
            self.assertEqual(control.authorized_phase(args, ledger).isoformat(), '2026-10-18T21:34:30+00:00')
            for field, value in [('owner', 'other'), ('timeout', 901), ('lane', 'stock'), ('source_mode', 'public-git')]:
                altered = copy.copy(args); setattr(altered, field, value)
                with self.assertRaises(SystemExit): control.authorized_phase(altered, ledger)
        for when in ('2026-10-18T19:04:29+00:00', '2026-10-18T21:04:30+00:00', '2026-10-18T21:34:30+00:00'):
            class BoundaryClock(datetime.datetime):
                @classmethod
                def now(cls, tz=None): return datetime.datetime.fromisoformat(when)
            # fromisoformat uses the original class method and no external operation.
            with patch.object(control.datetime, 'datetime', BoundaryClock):
                with self.assertRaises(SystemExit): control.authorized_phase(args, ledger)


if __name__ == '__main__':
    unittest.main(verbosity=2)
