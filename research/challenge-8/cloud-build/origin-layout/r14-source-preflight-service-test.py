#!/usr/bin/env python3
"""Pure R14 source-closure and publication-path tests; no Cloud or proof tools."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE.parent))
CONTROL_PATH = "research/challenge-8/cloud-build/control.py"
RUN_MERGE = "research/challenge-8/cloud-build/run-merge.sh"
spec = importlib.util.spec_from_file_location("r14_preflight", HERE / "r14-source-preflight.py")
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)
spec = importlib.util.spec_from_file_location("r14_control_test", HERE.parent / "control.py")
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


def expected_additions():
    return {
        preflight.GATE_PATH, preflight.LEDGER_PATH,
        "research/challenge-8/cloud-build/origin-layout/r14-source-preflight.py",
    }


class R14PublisherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probe_control = subprocess.check_output(
            ["git", "show", f"{preflight.PROBE_SOURCE}:{CONTROL_PATH}"], cwd=ROOT
        ).decode()
        cls.current_control = (ROOT / CONTROL_PATH).read_text()

    def test_current_publisher_keeps_guard_policy_and_marker_order(self):
        control.r14_validate_publisher_control(self.probe_control, self.current_control)

    def test_policy_guard_order_suppression_and_marker_mutants_refuse(self):
        guard_line = next(line for line in self.current_control.splitlines()
                          if "SDK_PYTHON /workspace/proof/research/challenge-8/cloud-build/origin-layout/r13-archive-size-guard.py --archive" in line)
        first_copy = next(line for line in self.current_control.splitlines()
                          if 'gcloud --configuration=smallsort-ci --account=ACCOUNT --project=smallsort-ci storage cp --if-generation-match=0 "/workspace/out/$file"' in line)
        swapped = self.current_control.replace(guard_line, "__R14_SWAP__", 1).replace(first_copy, guard_line, 1).replace("__R14_SWAP__", first_copy, 1)
        cases = {
            "policy true": self.current_control.replace(
                "export CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False",
                "export CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=True", 1),
            "guard removed": self.current_control.replace("r13-archive-size-guard.py --archive", "r13-archive-guard-removed.py --archive", 1),
            "guard after upload": swapped,
            "guard suppressed": self.current_control.replace("r13-archive-size-guard.py --archive", "r13-archive-size-guard.py --archive || true", 1),
            "R14 marker false": self.current_control.replace("'MERGE-PUBLICATION-GATE-PROOF-R14-2026-10-21'", "'OTHER-PHASE'"),
            "R14 call marker false": self.current_control.replace("r13_required=required_upload_guard(a.phase_id))", "r13_required=False)", 1),
        }
        for label, changed in cases.items():
            with self.subTest(label=label), self.assertRaises(SystemExit):
                control.r14_validate_publisher_control(self.probe_control, changed)

    def test_missing_required_card_dispatcher_is_a_runtime_closure_mismatch(self):
        before = {CONTROL_PATH: ("100644", "blob", "a"*40), RUN_MERGE: ("100755", "blob", "b"*40),
                  "research/challenge-8/cloud-build/recipes/merge.json": ("100644", "blob", "c"*40),
                  "research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json": ("100644", "blob", "d"*40),
                  "research/challenge-8/cloud-build/package-evidence.py": ("100644", "blob", "e"*40)}
        after = dict(before)
        after[CONTROL_PATH] = ("100644", "blob", "f"*40)
        for path in expected_additions(): after[path] = ("100644", "blob", "1"*40)
        control.r14_validate_runtime_maps(before, after, expected_additions())
        for mutation in ("marker false", "other publisher change"):
            bad = dict(after)
            if mutation == "marker false": bad[RUN_MERGE] = ("100755", "blob", "2"*40)
            else: bad["research/challenge-8/cloud-build/package-evidence.py"] = ("100644", "blob", "3"*40)
            with self.subTest(mutation=mutation), self.assertRaises(SystemExit):
                control.r14_validate_runtime_maps(before, bad, expected_additions())

    def test_missing_or_changed_mode_card_fails_closed(self):
        before = {"schema": "merge-r13-upload-mode-v1", "mode": "synthetic-upload",
                  "payload_bytes": 268435456, "threshold_bytes": 157286400,
                  "archive_limit_bytes": 536870912,
                  "threshold_source": "https://docs.cloud.google.com/storage/docs/parallel-composite-uploads",
                  "proof_attempted": False}
        after = {"schema": "merge-r13-upload-mode-v1", "mode": "proof-r11", "archive_limit_bytes": 536870912}
        control.r14_validate_mode_transition(before, after)
        for bad in (None, {}, dict(after, mode="synthetic-upload"), dict(after, archive_limit_bytes=1)):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                control.r14_validate_mode_transition(before, bad)

    def test_changed_or_missing_runtime_path_is_refused(self):
        before = {CONTROL_PATH: ("100644", "blob", "a"*40), RUN_MERGE: ("100755", "blob", "b"*40),
                  "research/challenge-8/cloud-build/recipes/merge.json": ("100644", "blob", "c"*40),
                  "research/challenge-8/cloud-build/origin-layout/R13-UPLOAD-MODE-20261021.json": ("100644", "blob", "d"*40)}
        after = dict(before); after[CONTROL_PATH] = ("100644", "blob", "e"*40)
        for path in expected_additions(): after[path] = ("100644", "blob", "1"*40)
        missing = dict(after); missing.pop(RUN_MERGE)
        with self.assertRaises(SystemExit): control.r14_validate_runtime_maps(before, missing, expected_additions())
        changed = dict(after); changed[RUN_MERGE] = ("100755", "blob", "2"*40)
        with self.assertRaises(SystemExit): control.r14_validate_runtime_maps(before, changed, expected_additions())

    def test_recipe_fields_other_than_exact_registration_paths_are_frozen(self):
        before = {"schema": "smallsort-cloud-recipe-v1", "lane": "merge",
                  "entrypoint": "run-merge.sh", "infra_paths": ["run-merge.sh"],
                  "proof_paths": ["a.py", "z.py"]}
        after = dict(before, proof_paths=["a.py", "new.py", "z.py"])
        control.r14_validate_recipe_delta(before, after, {"new.py"})
        for field, bad in (("baseline_sha", "f"*40), ("baseline_paths", ["changed.py"]), ("unknown", True)):
            changed = dict(after); changed[field] = bad
            with self.subTest(field=field), self.assertRaises(SystemExit):
                control.r14_validate_recipe_delta(before, changed, {"new.py"})
        with self.assertRaises(SystemExit):
            control.r14_validate_recipe_delta(before, dict(before, proof_paths=["z.py"]), set())

    def test_closed_r13_ledger_is_pinned_to_checkpoint_not_probe_state(self):
        probe = ("100644", "blob", "a"*40)
        closed = ("100644", "blob", "b"*40)
        control.r14_validate_historical_ledger(probe, closed, closed)
        for bad in (("100644", "blob", "c"*40), ("100755", "blob", "b"*40), None):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                control.r14_validate_historical_ledger(probe, bad, closed)

    def test_local_service_tests_are_committed_bytes_without_recipe_membership(self):
        self.assertEqual(len(preflight.LOCAL_TEST_PATHS), 2)
        for path in preflight.LOCAL_TEST_PATHS:
            self.assertNotIn(path, preflight.R14_ADDITIONS)
        fake_git = lambda *args: (ROOT / args[-1].split(":", 1)[-1]).read_bytes()
        with patch.object(preflight, "git", side_effect=fake_git):
            preflight.validate_local_tests()


if __name__ == "__main__":
    unittest.main()
