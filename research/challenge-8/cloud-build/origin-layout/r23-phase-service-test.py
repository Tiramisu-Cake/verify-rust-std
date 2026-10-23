#!/usr/bin/env python3
"""Synthetic exact R23 registration checks; no Cloud or proof execution."""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))
spec = importlib.util.spec_from_file_location('r23_control', HERE.parent / 'control.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def account():
    return json.loads((ROOT / m.R23_LEDGER_PATH).read_text())


def args(**changes):
    values = dict(phase_id=m.R23_PHASE, owner='merge', ledger=ROOT / m.R23_LEDGER_PATH,
                  command='submit', infra_sha='a' * 40, proof_sha='a' * 40,
                  lane='merge', timeout=1200, source_mode='pinned-objects')
    values.update(changes)
    return type('Args', (), values)()


def clock(moment):
    real = datetime.datetime
    class Frozen(real):
        @classmethod
        def now(cls, tz=None):
            return real.fromisoformat(moment)
    return patch.object(m.datetime, 'datetime', Frozen)


class R23PhaseTests(unittest.TestCase):
    def setUp(self):
        self.timer = clock('2026-10-23T11:00:00+00:00')
        self.timer.start()
        self.addCleanup(self.timer.stop)

    def test_exact_authorization_routes_source_upload_and_fixed_envelope(self):
        with patch.object(m, 'r14_read_selected_gate') as gate, patch.object(m, 'r23_validate_sources') as sources:
            m.authorized_phase(args(), account())
        gate.assert_called_once_with('a' * 40)
        sources.assert_called_once_with(m.R23_PROBE_SOURCE, 'a' * 40)
        self.assertTrue(m.required_upload_guard(m.R23_PHASE))
        cfg = m.config('a' * 40, 'a' * 40, 'merge', 1200, 'synthetic', r13_required=True)
        m.r17_validate_execute_budget(cfg, 1200)

    def test_wrong_account_identity_and_ledger_shapes_fail_closed(self):
        for key, value in (
            ('owner', 'select'), ('phase', m.R22_PHASE), ('phase_id', m.R22_PHASE),
            ('status', 'PREPARED_NOT_REGISTERED'), ('schema', 'wrong'),
            ('authorization', 'draft'), ('authorization_model', 'other'),
            ('task_id', 'old'), ('baseline_sha', '0' * 40),
            ('baseline_profile_sha256', '0' * 64), ('starting_tool_commit', '0' * 40),
            ('starting_source_sha', '0' * 40), ('allowed_lanes', ['select']),
            ('profile_path', 'other'), ('publication_gate_path', 'other'),
            ('start_utc', m.R22_START), ('main_deadline_utc', m.R22_MAIN_DEADLINE),
            ('deadline_utc', m.R22_DEADLINE), ('ceiling_build_seconds', True),
            ('ceiling_build_seconds', 3600), ('max_builds', 2), ('maximum_builds', 2),
            ('max_timeout_seconds', 1199), ('maximum_build_timeout_seconds', 1199),
            ('report_reserve_seconds', 419), ('carryover_allowed', True), ('carry_seconds', 1),
            ('remaining_build_seconds', 14399), ('used_build_seconds', True),
            ('used_build_seconds', -1), ('spent_build_seconds', 1), ('retired_seconds', 1),
            ('active_build', 'active'), ('builds', None), ('builds', [None]),
        ):
            ledger = account(); ledger[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(SystemExit):
                m.authorized_phase(args(command='request'), ledger)
        ledger = account(); del ledger['active_build']
        with self.assertRaises(SystemExit): m.authorized_phase(args(command='request'), ledger)

    def test_wrong_submit_route_and_short_timeout_refused(self):
        for changes in (dict(owner='select'), dict(ledger=HERE/'other.json'),
                        dict(lane='select'), dict(source_mode='public-git'),
                        dict(infra_sha='b'*40), dict(timeout=1199), dict(timeout=1201), dict(timeout=True)):
            with self.subTest(changes=changes), self.assertRaises(SystemExit):
                m.authorized_phase(args(**changes), account())

    def test_accounted_builds_and_budget_consistency(self):
        ledger = account()
        ledger['builds'] = [dict(owner='merge', phase_id=m.R23_PHASE, status='FAILURE',
                                accounted=True, build_id='synthetic-build', build_seconds=400)]
        ledger.update(used_build_seconds=400, spent_build_seconds=400, remaining_build_seconds=14000)
        m.authorized_phase(args(command='request'), ledger)
        for key, value in (('owner', 'network'), ('phase_id', m.R22_PHASE), ('accounted', False),
                           ('status', 'WORKING'), ('build_id', None), ('build_seconds', True), ('build_seconds', 399)):
            bad = copy.deepcopy(ledger); bad['builds'][0][key] = value
            with self.subTest(key=key), self.assertRaises(SystemExit):
                m.authorized_phase(args(command='request'), bad)

    def test_window_edges_and_final_recheck(self):
        for moment in ('2026-10-23T10:44:59+00:00', '2026-10-26T10:45:00+00:00'):
            with clock(moment), self.assertRaises(SystemExit):
                m.authorized_phase(args(command='request'), account())
        with clock('2026-10-26T10:24:00+00:00'), patch.object(m, 'r14_read_selected_gate'), patch.object(m, 'r23_validate_sources'):
            m.authorized_phase(args(), account())
        with clock('2026-10-26T10:24:01+00:00'), self.assertRaises(SystemExit):
            m.authorized_phase(args(), account())
        with clock('2026-10-26T10:24:01+00:00'), self.assertRaises(SystemExit):
            m.r23_final_deadline_check(args(), account())
        real = datetime.datetime
        for later in ('2026-10-26T10:24:01+00:00', '2026-10-26T11:46:00+00:00'):
            now = [real.fromisoformat('2026-10-23T11:00:00+00:00')]
            class Moving(real):
                @classmethod
                def now(cls, tz=None): return now[0]
            def slow(*_): now[0] = real.fromisoformat(later)
            with patch.object(m.datetime, 'datetime', Moving), patch.object(m, 'r14_read_selected_gate'), \
                    patch.object(m, 'r23_validate_sources', side_effect=slow), self.assertRaises(SystemExit):
                m.authorized_phase(args(), account())

    def test_exact_recipe_and_immutable_historical_closure(self):
        old = json.loads(subprocess.check_output(['git','show',m.R23_PROBE_SOURCE+':research/challenge-8/cloud-build/recipes/merge.json'],cwd=ROOT))
        selected = json.loads((HERE.parent/'recipes/merge.json').read_bytes())
        m.r23_validate_recipe_delta(old, selected)
        for bad in (dict(selected, lane='other'), dict(selected, proof_paths=selected['proof_paths']+['extra']),
                    dict(selected, proof_paths=old['proof_paths'])):
            with self.assertRaises(SystemExit): m.r23_validate_recipe_delta(old, bad)
        paths = {p for p in old['proof_paths'] if 'BUDGET' in Path(p).name.upper()} | {m.R13_MODE_PATH,m.R14_GATE_PATH,m.R17_PROFILE_PATH,m.R23_PROFILE_PATH}
        tree = {p: ('100644','blob',hashlib.sha1(p.encode()).hexdigest()) for p in paths}
        m.r23_validate_historical_closure(paths, tree, dict(tree))
        for path in paths:
            changed = dict(tree); changed[path] = ('100644','blob','0'*40)
            with self.subTest(path=path), self.assertRaises(SystemExit):
                m.r23_validate_historical_closure(paths, tree, changed)

    def test_provider_parser_binds_only_reviewed_runner_delta(self):
        source = (ROOT/m.R17_PROVIDER_OVERLAYS_PATH).read_bytes()
        pins = m.r23_parse_provider_pin_tables(source)
        self.assertEqual(pins['R22_FILES'], pins['R22_OWNED_NLL_FILES'])
        self.assertEqual(pins['R22_FILES'][m.R23_PLACEMENT_PATH], m.R23_PLACEMENT_SHA256)
        self.assertEqual(pins['R22_FILES'][m.R23_COMPAT_PATH], m.R23_COMPAT_SHA256)
        for wrong in (None, b'{}', source.replace(m.R23_PLACEMENT_SHA256.encode(), b'0'*64),
                      source.replace(m.R23_PROVE_SHA256.encode(), b'0'*64),
                      source.replace(m.R23_COMPAT_SHA256.encode(), b'0'*64)):
            with self.assertRaises(SystemExit): m.r23_parse_provider_pin_tables(wrong)
        with self.assertRaises(SystemExit): m.r22_parse_provider_pin_tables(source)

    def test_exact_candidate_tuple_and_wrong_types_fail_closed(self):
        show = lambda p: subprocess.check_output(['git','show',m.R23_PROBE_SOURCE+':'+p],cwd=ROOT)
        profile = show(m.R23_PROFILE_PATH)
        provider = (ROOT/m.R17_PROVIDER_OVERLAYS_PATH).read_bytes()
        values = [profile, profile, profile, show(m.R17_PATCH_PATH), show(m.R17_PROVIDER_OVERLAYS_PATH), provider, provider]
        m.r23_validate_candidate_pins(*values)
        current_values = [profile, (ROOT/m.R23_PROFILE_PATH).read_bytes(),
            (ROOT/m.R23_PROFILE_PATH).read_bytes(), (ROOT/m.R17_PATCH_PATH).read_bytes(),
            show(m.R17_PROVIDER_OVERLAYS_PATH), provider, provider]
        m.r23_validate_candidate_pins(*current_values)
        for index in (1, 2, 3):
            bad = list(current_values); bad[index] += b'x'
            with self.subTest(source_index=index), self.assertRaises(SystemExit):
                m.r23_validate_candidate_pins(*bad)
        for index in range(7):
            for wrong in (None, True, {}, values[index]+b'x'):
                bad = list(values); bad[index] = wrong
                with self.subTest(index=index, wrong_type=type(wrong).__name__), self.assertRaises(SystemExit):
                    m.r23_validate_candidate_pins(*bad)
        with self.assertRaises(SystemExit): m.r23_validate_sources('0'*40,'a'*40)
        with self.assertRaises(SystemExit): m.r23_validate_sources(m.R23_PROBE_SOURCE,None)


if __name__ == '__main__': unittest.main()
