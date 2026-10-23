"""Isolated tests for the main-command-only Cloud Build metadata snapshot."""
from __future__ import annotations

import contextlib
import copy
import builtins
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

CLOUD = Path(__file__).resolve().parent
ROOT = CLOUD.parents[2]
sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("status_snapshot_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


def result(stdout, returncode=0, stderr=""):
    return SimpleNamespace(stdout=stdout, returncode=returncode, stderr=stderr)


class StatusMetadataSnapshot(unittest.TestCase):
    def setUp(self):
        self.query = ["builds", "describe", "build-a", "--region=global", "--format=json"]
        self.metadata = {"id": "build-a", "status": "WORKING",
                         "tags": ["dispatch-a"], "nested": {"value": 1}}

    def test_repeated_exact_describe_is_cached_and_copies_are_independent(self):
        run = MagicMock(return_value=result(json.dumps(self.metadata)))
        with patch.object(CONTROL.subprocess, "run", run), CONTROL.status_metadata_snapshot(True):
            first = CONTROL.invoke(self.query)
            first["nested"]["value"] = 99
            first["tags"].append("changed")
            second = CONTROL.invoke(self.query)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(second, self.metadata)
        self.assertIsNot(first, second)
        self.assertIsNot(first["nested"], second["nested"])

    def test_build_ids_and_nonexact_query_arguments_are_separate(self):
        run = MagicMock(side_effect=[result('{"id":"build-a"}'),
                                    result('{"id":"build-b"}'),
                                    result('{"id":"build-a","detail":true}'),
                                    result('{"id":"build-a"}')])
        alternate = self.query[:-1] + ["--format=json(id,status)"]
        with patch.object(CONTROL.subprocess, "run", run), CONTROL.status_metadata_snapshot(True):
            CONTROL.invoke(self.query)
            CONTROL.invoke(["builds", "describe", "build-b", "--region=global", "--format=json"])
            CONTROL.invoke(alternate)
            CONTROL.invoke(self.query)
        self.assertEqual(run.call_count, 3)

    def test_contexts_are_fresh_and_disabled_context_does_not_cache(self):
        run = MagicMock(side_effect=[result('{"value":1}'), result('{"value":2}'),
                                    result('{"value":3}'), result('{"value":4}')])
        with patch.object(CONTROL.subprocess, "run", run):
            with CONTROL.status_metadata_snapshot(True):
                self.assertEqual(CONTROL.invoke(self.query)["value"], 1)
                self.assertEqual(CONTROL.invoke(self.query)["value"], 1)
            with CONTROL.status_metadata_snapshot(True):
                self.assertEqual(CONTROL.invoke(self.query)["value"], 2)
            with CONTROL.status_metadata_snapshot(False):
                self.assertEqual(CONTROL.invoke(self.query)["value"], 3)
                self.assertEqual(CONTROL.invoke(self.query)["value"], 4)
        self.assertEqual(run.call_count, 4)

    def test_errors_timeouts_and_bad_json_are_rethrown_and_retryable(self):
        cases = (
            (RuntimeError, [result("", 1, "provider failure"), result('{"ok":true}')]),
            (subprocess.TimeoutExpired,
             [subprocess.TimeoutExpired(["gcloud"], 20), result('{"ok":true}')]),
            (json.JSONDecodeError, [result("{"), result('{"ok":true}')]),
        )
        for error_type, outcomes in cases:
            with self.subTest(error_type=error_type.__name__):
                run = MagicMock(side_effect=outcomes)
                with patch.object(CONTROL.subprocess, "run", run), CONTROL.status_metadata_snapshot(True):
                    with self.assertRaises(error_type):
                        CONTROL.invoke(self.query)
                    self.assertEqual(CONTROL.invoke(self.query), {"ok": True})
                self.assertEqual(run.call_count, 2)

    def test_cache_is_restored_after_context_exception(self):
        run = MagicMock(side_effect=[result('{"call":1}'), result('{"call":2}')])
        with patch.object(CONTROL.subprocess, "run", run):
            with self.assertRaisesRegex(ValueError, "abort status"):
                with CONTROL.status_metadata_snapshot(True):
                    CONTROL.invoke(self.query)
                    raise ValueError("abort status")
            self.assertIsNone(CONTROL._STATUS_METADATA_CACHE)
            self.assertEqual(CONTROL.invoke(self.query), {"call": 2})
        self.assertEqual(run.call_count, 2)

    def test_json_null_and_wrong_types_preserve_return_values(self):
        for text, expected in (("null", None), ("[]", []), ('"wrong type"', "wrong type")):
            with self.subTest(text=text):
                run = MagicMock(return_value=result(text))
                with patch.object(CONTROL.subprocess, "run", run), CONTROL.status_metadata_snapshot(True):
                    self.assertEqual(CONTROL.invoke(self.query), expected)
                    self.assertEqual(CONTROL.invoke(self.query), expected)
                self.assertEqual(run.call_count, 1)

    def test_mutating_operations_are_never_cached(self):
        args = ["builds", "cancel", "build-a", "--region=global", "--format=json"]
        run = MagicMock(side_effect=[result('{"cancelled":true}'),
                                    result('{"cancelled":false}')])
        with patch.object(CONTROL.subprocess, "run", run), CONTROL.status_metadata_snapshot(True):
            self.assertEqual(CONTROL.invoke(args), {"cancelled": True})
            self.assertEqual(CONTROL.invoke(args), {"cancelled": False})
        self.assertEqual(run.call_count, 2)

    def test_integrated_status_reconciliation_reuses_one_build_read(self):
        build_id = "build-status-r24"
        token = "dispatch-status-r24"
        owner = "select-sort4"
        phase = "SORT4-ACTUAL-SELECT-2026-10-24-R24"
        ledger_path = ROOT / "research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-24-R24.json"
        item = {"dispatch_token": token, "owner": owner, "phase_id": phase,
                "build_id": build_id, "accounted": False, "reserved_seconds": 1260,
                "submitted_config_sha256": "a" * 64}
        ledger = {"phase": phase, "builds": [item.copy()], "used_build_seconds": 0,
                  "ceiling_build_seconds": 21600, "remaining_build_seconds": 21600,
                  "active_build": build_id}
        record = {"dispatch_token": token, "owner": owner, "phase_id": phase,
                  "ledger": str(ledger_path), "item": item.copy(), "build_id": build_id}
        api_build = {"id": build_id, "name": "operations/build-status-r24",
                     "status": "WORKING", "tags": [token], "createTime": "2026-10-23T11:00:00Z",
                     "startTime": "2026-10-23T11:00:01Z"}
        run = MagicMock(return_value=result(json.dumps(api_build)))
        args = SimpleNamespace(command="status", build_id=build_id, phase_id=None,
                               owner=owner, ledger=ledger_path, state_dir=None)
        parser = MagicMock()
        parser.parse_args.return_value = args
        with tempfile.TemporaryDirectory() as temp:
            args.state_dir = Path(temp) / "state"
            with patch.object(CONTROL.argparse, "ArgumentParser", return_value=parser), \
                 patch.object(CONTROL, "read", side_effect=lambda _path: copy.deepcopy(ledger)), \
                 patch.object(CONTROL, "write"), \
                 patch.object(CONTROL.coordination, "locked", return_value=contextlib.nullcontext()), \
                 patch.object(CONTROL.coordination, "reservations", return_value=[record]), \
                 patch.object(CONTROL.coordination, "submitted"), \
                 patch.object(CONTROL.subprocess, "run", run), \
                 patch.object(builtins, "print") as print_mock:
                CONTROL.main()
        self.assertEqual(run.call_count, 1)
        self.assertEqual(print_mock.call_count, 1)
        self.assertIn(build_id, str(print_mock.call_args))


if __name__ == "__main__":
    unittest.main()
