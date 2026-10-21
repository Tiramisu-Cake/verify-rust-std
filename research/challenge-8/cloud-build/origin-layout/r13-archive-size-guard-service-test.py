#!/usr/bin/env python3
"""Small local tests for the R13 pre-upload archive-size guard."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
GUARD_PATH = HERE / "r13-archive-size-guard.py"
spec = importlib.util.spec_from_file_location("r13_archive_size_guard_test", GUARD_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("R13 archive guard unavailable")
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

INFRA = "1" * 40
PROOF = "2" * 40
BUILD = "68d2fe9c-bb4b-494e-844d-1a779d8d9f41"
ENV = {"INFRA_SHA": INFRA, "PROOF_SHA": PROOF, "CLOUD_BUILD_ID": BUILD}


def synthetic_card(**overrides):
    value = {"schema": guard.MODE_SCHEMA, "mode": "synthetic-upload",
             "payload_bytes": guard.SYNTHETIC_PAYLOAD_BYTES,
             "threshold_bytes": guard.DOCUMENTED_THRESHOLD_BYTES,
             "archive_limit_bytes": guard.ARCHIVE_LIMIT_BYTES,
             "threshold_source": guard.THRESHOLD_SOURCE, "proof_attempted": False}
    value.update(overrides)
    return value


def proof_card(**overrides):
    value = {"schema": guard.MODE_SCHEMA, "mode": "proof-r11",
             "archive_limit_bytes": guard.ARCHIVE_LIMIT_BYTES}
    value.update(overrides)
    return value


def policy(**overrides):
    value = {"schema": guard.POLICY_SCHEMA,
             "parallel_composite_upload_enabled_effective": "False",
             "parallel_composite_upload_threshold": "150M",
             "proof_sha": PROOF, "infra_sha": INFRA, "build_id": BUILD,
             "parallel_composite_upload_enabled_env": "False",
             "sdk_image": "synthetic", "service_account": "synthetic",
             "bucket": "gs://synthetic"}
    value.update(overrides)
    return value


class R13ArchiveGuardTests(unittest.TestCase):
    def test_threshold_parser_uses_binary_sdk_units_and_fails_closed(self):
        self.assertEqual(guard.parse_sdk_threshold("150M"), 157_286_400)
        self.assertEqual(guard.parse_sdk_threshold("150MiB"), 157_286_400)
        self.assertEqual(guard.parse_sdk_threshold("157286400"), 157_286_400)
        for bad in (None, "", "0M", "-1M", "1.5M", "NaN", "150MB/s", 150):
            with self.subTest(value=bad), self.assertRaises(ValueError):
                guard.parse_sdk_threshold(bad)

    def test_synthetic_and_proof_boundaries(self):
        threshold = guard.DOCUMENTED_THRESHOLD_BYTES
        cap = guard.ARCHIVE_LIMIT_BYTES
        for size in (cap - 1, cap):
            result = guard.validate_archive_size(size, synthetic_card(), policy(), ENV)
            self.assertTrue(result["accepted"], result)
            self.assertEqual(result["effective_threshold_bytes"], threshold)
        self.assertFalse(guard.validate_archive_size(cap + 1, synthetic_card(), policy(), ENV)["accepted"])
        self.assertFalse(guard.validate_archive_size(threshold, synthetic_card(), policy(), ENV)["accepted"])
        lower = guard.validate_archive_size(threshold + 1, synthetic_card(), policy(), ENV)
        self.assertTrue(lower["accepted"], lower)
        # Proof publication shares the upper cap and has no synthetic lower bound.
        proof = guard.validate_archive_size(1, proof_card(), policy(), ENV)
        self.assertTrue(proof["accepted"], proof)
        self.assertFalse(guard.validate_archive_size(cap + 1, proof_card(), policy(), ENV)["accepted"])

    def test_malformed_cards_policy_and_runtime_identities_fail_closed(self):
        good = synthetic_card()
        bad_cards = [
            None, [], {**good, "schema": "wrong"}, {**good, "extra": 1},
            {**good, "payload_bytes": True}, {**good, "payload_bytes": 268435456.0},
            {**good, "archive_limit_bytes": None}, {**good, "proof_attempted": 0},
        ]
        for card in bad_cards:
            with self.subTest(card=card):
                self.assertFalse(guard.validate_archive_size(guard.ARCHIVE_LIMIT_BYTES,
                                  card, policy(), ENV)["accepted"])
        for bad_policy in (
            None, [], {**policy(), "schema": "wrong"},
            {**policy(), "parallel_composite_upload_enabled_effective": False},
            {**policy(), "parallel_composite_upload_enabled_effective": "true"},
            {**policy(), "parallel_composite_upload_threshold": None},
            {**policy(), "parallel_composite_upload_threshold": "garbage"},
            {**policy(), "infra_sha": "3" * 40},
            {**policy(), "proof_sha": "bad"},
            {**policy(), "build_id": "bad"},
        ):
            with self.subTest(policy=bad_policy):
                self.assertFalse(guard.validate_archive_size(guard.ARCHIVE_LIMIT_BYTES,
                                  good, bad_policy, ENV)["accepted"])
        for env in ({}, {**ENV, "INFRA_SHA": "short"}, {**ENV, "PROOF_SHA": "3" * 40},
                    {**ENV, "CLOUD_BUILD_ID": "not-a-uuid"}):
            with self.subTest(env=env):
                self.assertFalse(guard.validate_archive_size(guard.ARCHIVE_LIMIT_BYTES,
                                  good, policy(), env)["accepted"])

    def test_cli_writes_diagnostic_for_normal_success_and_synthetic_refusal(self):
        with tempfile.TemporaryDirectory(prefix="r13-guard-") as temporary:
            root = Path(temporary)
            archive = root / "evidence.tar.gz"
            archive.write_bytes(b"tiny local archive")
            card_path = root / "mode.json"
            policy_path = root / "upload-policy.json"
            diagnostic_path = root / "archive-size-check.json"
            policy_path.write_text(json.dumps(policy()))
            card_path.write_text(json.dumps(proof_card()))
            with patch.dict(os.environ, ENV, clear=False):
                result = guard.main(["--archive", str(archive), "--mode-card", str(card_path),
                                     "--policy", str(policy_path), "--diagnostic", str(diagnostic_path)])
                self.assertEqual(result, 0)
                accepted = json.loads(diagnostic_path.read_text())
                self.assertTrue(accepted["accepted"])
                self.assertEqual(accepted["actual_archive_bytes"], len(b"tiny local archive"))
                self.assertEqual(accepted["archive_limit_bytes"], guard.ARCHIVE_LIMIT_BYTES)
                self.assertEqual(accepted["effective_threshold_bytes"], 157_286_400)
                self.assertEqual(accepted["build_id"], BUILD)

                card_path.write_text(json.dumps(synthetic_card()))
                result = guard.main(["--archive", str(archive), "--mode-card", str(card_path),
                                     "--policy", str(policy_path), "--diagnostic", str(diagnostic_path)])
            self.assertEqual(result, 1)
            refused = json.loads(diagnostic_path.read_text())
            self.assertFalse(refused["accepted"])
            self.assertIn("exceed", refused["reason"])
            self.assertEqual(refused["actual_archive_bytes"], len(b"tiny local archive"))

    def test_cli_reports_oversize_without_allocating_large_file(self):
        with tempfile.TemporaryDirectory(prefix="r13-guard-stat-") as temporary:
            root = Path(temporary)
            archive = root / "evidence.tar.gz"
            archive.write_bytes(b"stub")
            card_path = root / "mode.json"
            policy_path = root / "upload-policy.json"
            diagnostic_path = root / "archive-size-check.json"
            card_path.write_text(json.dumps(proof_card()))
            policy_path.write_text(json.dumps(policy()))
            original_stat = Path.stat

            def fake_stat(path, *args, **kwargs):
                if path == archive and kwargs.get("follow_symlinks", True):
                    return types.SimpleNamespace(st_size=guard.ARCHIVE_LIMIT_BYTES + 1)
                return original_stat(path, *args, **kwargs)

            with patch("pathlib.Path.stat", fake_stat), patch.dict(os.environ, ENV, clear=False):
                result = guard.main(["--archive", str(archive), "--mode-card", str(card_path),
                                     "--policy", str(policy_path), "--diagnostic", str(diagnostic_path)])
            self.assertEqual(result, 1)
            diagnostic = json.loads(diagnostic_path.read_text())
            self.assertFalse(diagnostic["accepted"])
            self.assertEqual(diagnostic["actual_archive_bytes"], guard.ARCHIVE_LIMIT_BYTES + 1)
            self.assertEqual(diagnostic["archive_limit_bytes"], guard.ARCHIVE_LIMIT_BYTES)
            self.assertIn("exceeds", diagnostic["reason"])

    def test_cli_rejects_symlink_archive(self):
        with tempfile.TemporaryDirectory(prefix="r13-guard-link-") as temporary:
            root = Path(temporary)
            actual = root / "actual.tar.gz"
            actual.write_bytes(b"tiny")
            archive = root / "evidence.tar.gz"
            archive.symlink_to(actual)
            card_path = root / "mode.json"
            policy_path = root / "policy.json"
            diagnostic_path = root / "diagnostic.json"
            card_path.write_text(json.dumps(proof_card()))
            policy_path.write_text(json.dumps(policy()))
            result = guard.main(["--archive", str(archive), "--mode-card", str(card_path),
                                 "--policy", str(policy_path), "--diagnostic", str(diagnostic_path)])
            self.assertEqual(result, 1)
            self.assertIn("non-symlink", json.loads(diagnostic_path.read_text())["reason"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
