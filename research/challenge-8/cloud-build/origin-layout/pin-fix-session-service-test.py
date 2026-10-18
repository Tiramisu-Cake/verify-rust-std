#!/usr/bin/env python3
"""Synthetic admission/service tests for the 2026-10-18 pin-fix Build.

Only temporary files and mocked coordinator/Cloud/Git APIs are used. No Cloud
Build, real coordinator state, proof tool, compiler, or verifier is invoked.
"""
from __future__ import annotations

import contextlib
import copy
import datetime
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CONTROL_PATH = ROOT / "research/challenge-8/cloud-build/control.py"
LEDGER_PATH = HERE / "PIN-FIX-BUDGET-20261018.json"
HISTORICAL_LEDGER_PATH = HERE / "FIRST-CALLBACK-BUDGET-20261017.json"
PHASE = "MERGE-FIRST-CALLBACK-PIN-FIX-2026-10-18"
START = "2026-10-18T08:41:55Z"
MAIN = "2026-10-18T10:41:55Z"
DEADLINE = "2026-10-18T11:11:55Z"
INFRA = "1" * 40
PROOF = "2" * 40


def load_control():
    import sys
    sys.path.insert(0, str(CONTROL_PATH.parent))
    spec = importlib.util.spec_from_file_location("pin_fix_control_under_test", CONTROL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("control.py could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


control = load_control()


class FixedDateTime(datetime.datetime):
    current = datetime.datetime(2026, 10, 18, 9, 0, tzinfo=datetime.timezone.utc)

    @classmethod
    def now(cls, tz=None):
        return cls.current.astimezone(tz) if tz else cls.current.replace(tzinfo=None)


def base_ledger():
    # Keep the fixture stable when the real account is later charged/closed.
    return {
        "phase": PHASE,
        "owner": "merge",
        "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 960,
        "used_build_seconds": 0,
        "remaining_build_seconds": 960,
        "builds": [],
        "active_build": None,
        "status": "AUTHORIZED",
        "start_utc": START,
        "main_deadline_utc": MAIN,
        "deadline_utc": DEADLINE,
        "max_builds": 1,
        "max_timeout_seconds": 900,
        "authorization": "synthetic explicit owner authorization",
    }


def args_for(command="submit", **changes):
    values = dict(command=command, phase_id=PHASE, ledger=LEDGER_PATH,
                  owner="merge", lane="merge", timeout=900,
                  source_mode="pinned-objects", infra_sha=INFRA, proof_sha=PROOF)
    values.update(changes)
    return types.SimpleNamespace(**values)


class PinFixSessionServiceTest(unittest.TestCase):
    def setUp(self):
        self.ledger_before = LEDGER_PATH.read_bytes()
        self.historical_before = HISTORICAL_LEDGER_PATH.read_bytes()
        self.clock_patch = patch.object(control.datetime, "datetime", FixedDateTime)
        self.clock_patch.start()
        self.addCleanup(self.clock_patch.stop)

    def tearDown(self):
        self.assertEqual(LEDGER_PATH.read_bytes(), self.ledger_before)
        self.assertEqual(HISTORICAL_LEDGER_PATH.read_bytes(), self.historical_before)

    def authorize(self, args=None, ledger=None):
        return control.authorized_phase(args or args_for(), ledger or base_ledger())

    def test_approved_phase_and_request(self):
        self.assertEqual(self.authorize(), datetime.datetime.fromisoformat(DEADLINE.replace("Z", "+00:00")))
        calls = []
        with patch.object(control.coordination, "locked", contextlib.nullcontext), \
             patch.object(control.coordination, "read", side_effect=lambda p: base_ledger()), \
             patch.object(control.coordination, "request", side_effect=lambda *xs: calls.append(xs)), \
             contextlib.redirect_stdout(io.StringIO()):
            with tempfile.TemporaryDirectory(prefix="pin-fix-request-") as temp:
                # main() accepts only ledgers inside this worktree. Exercise the
                # same request route through run_command with the real account.
                request_args = args_for("request")
                control.run_command(request_args, Path(temp), base_ledger(), LEDGER_PATH)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0:2], ("merge", PHASE))
        self.assertEqual(Path(calls[0][2]), LEDGER_PATH.resolve())
        self.assertEqual(calls[0][3], DEADLINE)

    def test_approved_submit_service_path_with_all_external_calls_mocked(self):
        ledger = base_ledger()
        args = args_for()
        writes = {}
        invocations = []
        def fake_invoke(command):
            invocations.append(command)
            if "submit" in command:
                return {"id": "synthetic-build-id", "status": "QUEUED"}
            return []
        class Loader:
            @staticmethod
            def exec_module(module):
                module.make_payload = lambda *unused: b'{"synthetic":true}'
        fake_spec = types.SimpleNamespace(loader=Loader())
        def expected_git_bytes(command, **kwargs):
            if command[:2] == ["git", "cat-file"]:
                return b""
            if command[:2] == ["git", "show"]:
                return (ROOT / command[-1].split(":", 1)[1]).read_bytes()
            raise AssertionError(f"unexpected mocked Git command: {command}")
        def fake_write_bytes(path, data):
            writes[Path(path)] = bytes(data)
        with tempfile.TemporaryDirectory(prefix="pin-fix-submit-") as temp, \
             patch.object(control.datetime, "datetime", FixedDateTime), \
             patch.object(control, "invoke", side_effect=fake_invoke), \
             patch.object(control.subprocess, "run", return_value=types.SimpleNamespace(returncode=0)), \
             patch.object(control.subprocess, "check_output", side_effect=expected_git_bytes), \
             patch.object(control.importlib.util, "spec_from_file_location", return_value=fake_spec), \
             patch.object(control.importlib.util, "module_from_spec", return_value=types.SimpleNamespace()), \
             patch.object(control.coordination, "request"), \
             patch.object(control.coordination, "require_capacity"), \
             patch.object(control.coordination, "reserve"), \
             patch.object(control.coordination, "update"), \
             patch.object(control.coordination, "submitted"), \
             patch.object(control, "write", side_effect=lambda p, value: writes.__setitem__(Path(p), copy.deepcopy(value))), \
             patch.object(control.coordination, "write_bytes", side_effect=fake_write_bytes):
            control.run_command(args, Path(temp), ledger, LEDGER_PATH.resolve())
        self.assertEqual(len(invocations), 2)
        self.assertIn("builds", invocations[0])
        submit_call = invocations[1]
        self.assertIn("builds", submit_call)
        self.assertIn("submit", submit_call)
        self.assertTrue(any(path.name.endswith(".json") for path in writes))
        self.assertEqual(ledger["builds"][0]["timeout_seconds"], 900)
        self.assertEqual(ledger["builds"][0]["reserved_seconds"], 960)
        self.assertEqual(ledger["builds"][0]["source_mode"], "pinned-objects")

    def test_wrong_account_identity_and_limits_refuse(self):
        cases = [
            ("phase id", args_for(phase_id="OTHER-PHASE"), None),
            ("owner arg", args_for(owner="other"), None),
            ("ledger owner", None, {"owner": "other"}),
            ("ledger path", args_for(ledger=HERE / "wrong.json"), None),
            ("ceiling", None, {"ceiling_build_seconds": 961}),
            ("allowed lane", None, {"allowed_lanes": ["merge", "other"]}),
            ("start", None, {"start_utc": "2026-10-18T08:41:56Z"}),
            ("main deadline", None, {"main_deadline_utc": "2026-10-18T10:41:56Z"}),
            ("deadline", None, {"deadline_utc": "2026-10-18T11:11:56Z"}),
            ("max builds", None, {"max_builds": 2}),
            ("max timeout", None, {"max_timeout_seconds": 901}),
            ("used budget", None, {"used_build_seconds": 1}),
            ("remaining below ceiling", None, {"remaining_build_seconds": 959}),
            ("remaining above ceiling", None, {"remaining_build_seconds": 961}),
        ]
        for label, args, changes in cases:
            with self.subTest(label=label):
                ledger = base_ledger()
                if changes:
                    ledger.update(changes)
                with self.assertRaises(SystemExit):
                    self.authorize(args, ledger)

    def test_insufficient_remaining_budget_refuses_before_submit(self):
        ledger = base_ledger()
        ledger["remaining_build_seconds"] = 959
        invocations = []
        with patch.object(control, "invoke", side_effect=lambda command: invocations.append(command) or []), \
             patch.object(control.subprocess, "run", side_effect=AssertionError("Git must not run")), \
             patch.object(control.subprocess, "check_output", side_effect=AssertionError("Git must not run")):
            with self.assertRaisesRegex(SystemExit, "Pin-fix phase differs from explicit owner authorization"):
                control.run_command(args_for(), Path("/tmp/synthetic-pin-fix"), ledger, LEDGER_PATH.resolve())
        self.assertEqual(invocations, [])

    def test_wrong_lane_source_timeout_and_build_state_refuse(self):
        cases = [
            ("wrong lane", args_for(lane="smoke-success"), None),
            ("wrong source", args_for(source_mode="public-git"), None),
            ("timeout short", args_for(timeout=899), None),
            ("timeout long", args_for(timeout=901), None),
            ("missing builds field", None, "missing-builds"),
            ("nonempty builds", None, "nonempty-builds"),
            ("active build", None, "active-build"),
        ]
        for label, args, state in cases:
            with self.subTest(label=label):
                ledger = base_ledger()
                if state == "missing-builds":
                    del ledger["builds"]
                elif state == "nonempty-builds":
                    ledger["builds"] = [{"status": "FAILURE"}]
                elif state == "active-build":
                    ledger["active_build"] = "old-build"
                with self.assertRaises((SystemExit, KeyError)):
                    self.authorize(args, ledger)

    def test_time_boundaries_refuse(self):
        cases = [
            ("before start", datetime.datetime(2026, 10, 18, 8, 41, 54, tzinfo=datetime.timezone.utc)),
            ("main cutoff", datetime.datetime(2026, 10, 18, 10, 41, 55, tzinfo=datetime.timezone.utc)),
            ("absolute expiration", datetime.datetime(2026, 10, 18, 11, 11, 55, tzinfo=datetime.timezone.utc)),
        ]
        for label, now in cases:
            with self.subTest(label=label):
                FixedDateTime.current = now
                with self.assertRaises(SystemExit):
                    self.authorize()
        FixedDateTime.current = datetime.datetime(2026, 10, 18, 9, 0, tzinfo=datetime.timezone.utc)


if __name__ == "__main__":
    unittest.main(verbosity=2)
