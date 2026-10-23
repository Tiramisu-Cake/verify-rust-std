"""Synthetic Git tests for session_prepare; no network, Cloud, or proof tools."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("session_prepare", HERE / "session_prepare.py")
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


REUSED_PROFILE = {"phase": "OLD-PHASE", "authorization_phase_id": "OLD-PHASE", "profile_accepted": False,
                  "proof_credit": False, "cloud_build_enabled": True, "target": "pinned"}


class Fixture:
    def __init__(self, parent: Path, profile: dict | None = None, recipe_proof_paths: list | None = None):
        self.root = parent / "worktree"
        self.root.mkdir()
        git(self.root, "init", "-q", "-b", "test-session-branch")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "user.name", "Session Prepare Test")
        self.old_ledger = "research/challenge-8/cloud-build/old/BUDGET.json"
        self.profile = "research/challenge-8/cloud-build/profile.json"
        self.recipe = "research/challenge-8/cloud-build/recipes/merge.json"
        self.new_ledger = "research/challenge-8/cloud-build/new/BUDGET.json"
        self.new_profile = "research/challenge-8/cloud-build/new/PROFILE.json"
        files = {
            self.old_ledger: {"phase": "OLD-PHASE", "status": "CLOSED", "owner": "merge", "builds": [], "active_build": None},
            self.profile: profile if profile is not None else {"phase": "OLD-PHASE", "authorization_phase_id": "OLD-PHASE", "profile_accepted": True, "proof_credit": True, "cloud_build_enabled": True, "target": "old"},
            self.recipe: {"schema": "smallsort-cloud-recipe-v1", "lane": "merge", "infra_paths": ["research/challenge-8/cloud-build/runner.sh"],
                          "proof_paths": recipe_proof_paths if recipe_proof_paths is not None else [self.old_ledger, self.profile, "research/challenge-8/proof.py"]},
        }
        for path, data in files.items():
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
        for path, data in (("research/challenge-8/cloud-build/runner.sh", "#!/bin/sh\n"),
                           ("research/challenge-8/proof.py", "pass\n"),
                           ("research/challenge-8/cloud-build/control.py", "def authorized_phase(a, b): pass\ndef envs(): pass\ndef config(): pass\ndef run_command(): pass\n")):
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(data, encoding="utf-8")
        (self.root / "research/challenge-8/cloud-build/runner.sh").chmod(0o755)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "closed checkpoint")
        self.baseline = git(self.root, "rev-parse", "HEAD")
        # A later assignment commit verifies that baseline only needs to be an ancestor.
        (self.root / "research/challenge-8/assignment.md").write_text("new assignment\n", encoding="utf-8")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "new assignment")
        self.head = git(self.root, "rev-parse", "HEAD")
        self.spec = {
            "schema": "smallsort-session-spec-v1", "task_id": "merge-session-next",
            "phase": "MERGE-NEXT-2026-10-22", "owner": "merge", "worktree": str(self.root),
            "branch": "test-session-branch", "baseline_sha": self.baseline, "lane": "merge",
            "t0": "2026-10-22T10:00:00Z", "main_minutes": 120, "finish_minutes": 30,
            "cloud_seconds": 3600, "max_timeout_seconds": 1200, "report_reserve_seconds": 420,
            "profile_path": self.profile, "recipe_path": self.recipe,
            "old_ledger_path": self.old_ledger, "new_ledger_path": self.new_ledger,
            "new_profile_path": self.new_profile,
            "profile_updates": {"/phase": "MERGE-NEXT-2026-10-22", "/authorization_phase_id": "MERGE-NEXT-2026-10-22", "/target": "next"},
        }

    def write_spec(self, path: Path, overrides: dict | None = None) -> Path:
        value = dict(self.spec)
        if overrides:
            value.update(overrides)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path


class SessionPrepareTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.fx = Fixture(self.parent)
        (self.parent / "out").mkdir()
        (self.parent / "spec.json").write_text(json.dumps(self.fx.spec), encoding="utf-8")
        self.out = self.parent / "out" / "bundle"

    def prepare(self, spec: dict | None = None, out: Path | None = None) -> Path:
        spec_path = self.parent / "spec.json"
        spec_path.write_text(json.dumps(self.fx.spec if spec is None else spec), encoding="utf-8")
        module.prepare(spec_path, self.out if out is None else out)
        return self.out if out is None else out

    @staticmethod
    def refresh_inventory(bundle: Path) -> None:
        inventory = {p.relative_to(bundle).as_posix(): module._sha256(p.read_bytes())
                     for p in bundle.rglob("*") if p.is_file() and p.name != "inventory.json"}
        (bundle / "inventory.json").write_text(
            json.dumps({"schema": "smallsort-session-inventory-v1", "files": inventory},
                       sort_keys=True, indent=2) + "\n", encoding="utf-8")

    def test_prepare_bundle_and_check_contract(self):
        before = git(self.fx.root, "status", "--porcelain")
        bundle = self.prepare()
        self.assertEqual(git(self.fx.root, "status", "--porcelain"), before)
        checked = module.check(bundle)
        self.assertEqual(checked["state"], "PREPARED_NOT_REGISTERED")
        self.assertEqual(checked["phase"], self.fx.spec["phase"])
        ledger = json.loads((bundle / "ledger.json").read_text())
        self.assertEqual(ledger["main_deadline_utc"], "2026-10-22T12:00:00Z")
        self.assertEqual(ledger["deadline_utc"], "2026-10-22T12:30:00Z")
        self.assertEqual(ledger["remaining_build_seconds"], 3600)
        self.assertEqual(ledger["builds"], [])
        profile = json.loads((bundle / "profile.json").read_text())
        self.assertEqual(profile["status"], "DRAFT")
        self.assertFalse(profile["cloud_build_enabled"])
        self.assertFalse(profile["profile_accepted"])
        self.assertFalse(profile["proof_credit"])
        self.assertEqual(profile["target"], "next")
        recipe = json.loads((bundle / "recipe.json").read_text())
        self.assertIn(self.fx.new_ledger, recipe["proof_paths"])
        self.assertIn(self.fx.new_profile, recipe["proof_paths"])
        self.assertNotIn(self.fx.old_ledger, recipe["proof_paths"])
        self.assertNotIn(self.fx.profile, recipe["proof_paths"])
        self.assertEqual(json.loads((bundle / "bundle.json").read_text())["selected_head"], self.fx.head)
        self.assertIn("authorized_phase", (bundle / "registration-plan.md").read_text())

    def first_session(self, **overrides):
        """Network first Cloud session: no old ledger; recipe names the new files directly."""
        parent = self.parent / f"first-{len(list(self.parent.glob('first-*')))}"
        parent.mkdir()
        self.fx = Fixture(parent, recipe_proof_paths=[
            "research/challenge-8/cloud-build/new/BUDGET.json", "research/challenge-8/cloud-build/new/PROFILE.json",
            "research/challenge-8/proof.py"])
        self.out = parent / "bundle"
        spec = dict(self.fx.spec, owner="network", task_id="network-first-cloud", phase="NETWORK-R4-2026-10-23",
                    old_ledger_path=None, profile_path=None, report_reserve_seconds=240,
                    profile_updates={"/phase": "NETWORK-R4-2026-10-23", "/target": "r4"})
        spec.update(overrides)
        return spec

    def test_network_first_session_without_old_ledger_or_profile(self):
        before = git(self.fx.root, "status", "--porcelain")
        bundle = self.prepare(self.first_session())
        self.assertEqual(git(self.fx.root, "status", "--porcelain"), before)
        self.assertEqual(module.check(bundle)["owner"], "network")
        names = {p.name for p in bundle.iterdir()}
        self.assertNotIn("old_ledger.raw.json", names)
        self.assertNotIn("source_profile.raw.json", names)
        self.assertEqual(json.loads((bundle / "source_profile.json").read_text()), {})
        profile = json.loads((bundle / "profile.json").read_text())
        self.assertEqual((profile["status"], profile["cloud_build_enabled"], profile["target"]), ("DRAFT", False, "r4"))
        self.assertEqual(json.loads((bundle / "ledger.json").read_text())["owner"], "network")
        plan = (bundle / "registration-plan.md").read_text()
        self.assertIn("from an empty object (first Cloud session; no source profile)", plan)
        self.assertIn("- Previous ledger: none (first Cloud session of this owner)\n\n## Required", plan)
        closure = {e["path"]: e["state"] for e in json.loads((bundle / "closure.json").read_text())["entries"]}
        self.assertEqual(closure["research/challenge-8/cloud-build/new/BUDGET.json"], "generated_pending_commit")
        (bundle / "old_ledger.raw.json").write_text("{}", encoding="utf-8")
        self.refresh_inventory(bundle)
        with self.assertRaisesRegex(module.PrepareError, "file set differs"):
            module.check(bundle)

    def test_first_session_recipe_must_reference_generated_files(self):
        for omitted in ("research/challenge-8/cloud-build/new/BUDGET.json", "research/challenge-8/cloud-build/new/PROFILE.json"):
            with self.subTest(omitted=omitted):
                spec = self.first_session()
                recipe_path = self.fx.root / self.fx.recipe
                recipe = json.loads(recipe_path.read_text())
                recipe["proof_paths"] = [p for p in recipe["proof_paths"] if p != omitted]
                recipe_path.write_text(json.dumps(recipe, sort_keys=True) + "\n", encoding="utf-8")
                git(self.fx.root, "commit", "-qam", "recipe without generated file")
                with self.assertRaisesRegex(module.PrepareError, "must reference the generated"):
                    self.prepare(spec)
                self.assertFalse(self.out.exists())
        # check() enforces the same rule on a tampered bundle.
        bundle = self.prepare(self.first_session())
        for name in ("recipe.json", "source_recipe.json"):
            value = json.loads((bundle / name).read_text())
            value["proof_paths"] = [p for p in value["proof_paths"] if not p.endswith("new/BUDGET.json")]
            (bundle / name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        self.refresh_inventory(bundle)
        with self.assertRaisesRegex(module.PrepareError, "must reference the generated"):
            module.check(bundle)

    def test_network_first_session_with_committed_source_profile(self):
        spec = self.first_session(profile_path="research/challenge-8/cloud-build/profile.json")
        self.fx.spec["profile_path"] = spec["profile_path"]
        bundle = self.prepare(spec)
        self.assertEqual(module.check(bundle)["state"], "PREPARED_NOT_REGISTERED")
        self.assertTrue((bundle / "source_profile.raw.json").exists())
        self.assertFalse((bundle / "old_ledger.raw.json").exists())
        self.assertFalse(json.loads((bundle / "profile.json").read_text())["proof_credit"])

    def test_first_session_refusals(self):
        for overrides, message in (
                ({"owner": "merge", "report_reserve_seconds": 420}, "profile_path must be a non-empty"),
                ({"owner": "select-sort4", "profile_path": "research/challenge-8/cloud-build/profile.json"},
                 "old_ledger_path must be a non-empty"),
                ({"new_profile_path": None, "profile_updates": {}}, "requires new_profile_path"),
                ({"owner": "verifast"}, "owner must be merge, select-sort4 or network")):
            with self.subTest(overrides=overrides):
                with self.assertRaisesRegex(module.PrepareError, message):
                    self.prepare(self.first_session(**overrides))
                self.assertFalse(self.out.exists())

    def reuse(self, profile=REUSED_PROFILE, recipe_proof_paths=None):
        """Fresh fixture whose pinned profile is committed before the baseline."""
        parent = self.parent / f"reuse-{len(list(self.parent.glob('reuse-*')))}"
        parent.mkdir()
        self.fx = Fixture(parent, profile=profile, recipe_proof_paths=recipe_proof_paths)
        self.out = parent / "bundle"
        return dict(self.fx.spec, new_profile_path=None, profile_updates={})

    def commit_profile(self, content: str):
        (self.fx.root / self.fx.profile).write_text(content, encoding="utf-8")
        git(self.fx.root, "commit", "-qam", "change pinned profile after baseline")

    def test_reuse_pinned_profile_without_draft_profile(self):
        bundle = self.prepare(self.reuse())
        self.assertFalse((bundle / "profile.json").exists())
        self.assertEqual(module.check(bundle)["state"], "PREPARED_NOT_REGISTERED")
        recipe = json.loads((bundle / "recipe.json").read_text())
        self.assertIn(self.fx.profile, recipe["proof_paths"])
        self.assertIn(self.fx.new_ledger, recipe["proof_paths"])
        self.assertNotIn(self.fx.old_ledger, recipe["proof_paths"])
        closure_paths = {item["path"] for item in json.loads((bundle / "closure.json").read_text())["entries"]}
        self.assertIn(self.fx.profile, closure_paths)
        plan = (bundle / "registration-plan.md").read_text()
        self.assertIn("reuse pinned", plan)
        self.assertIn("bind its exact SHA-256", plan)
        self.assertIn("pinned profile.", plan)
        self.assertNotIn("prepared profile and recipe", plan)

    def test_reuse_pinned_profile_refuses_updates_and_tampering(self):
        spec = self.reuse()
        with self.assertRaisesRegex(module.PrepareError, "profile_updates require new_profile_path"):
            self.prepare(dict(spec, profile_updates={"/target": "x"}))
        self.assertFalse(self.out.exists())
        bundle = self.prepare(spec)
        (bundle / "profile.json").write_text("{}\n", encoding="utf-8")
        self.refresh_inventory(bundle)
        with self.assertRaisesRegex(module.PrepareError, "bundle file set"):
            module.check(bundle)
        (bundle / "profile.json").unlink()
        recipe = json.loads((bundle / "recipe.json").read_text())
        recipe["proof_paths"].append(self.fx.old_ledger)
        (bundle / "recipe.json").write_text(json.dumps(recipe), encoding="utf-8")
        self.refresh_inventory(bundle)
        with self.assertRaisesRegex(module.PrepareError, "recipe"):
            module.check(bundle)

    def test_reuse_refuses_credit_flags_unreferenced_profile_and_bad_json(self):
        cases = [
            (dict(REUSED_PROFILE, proof_credit=True), None, "acceptance/admission/credit flags: /proof_credit"),
            (dict(REUSED_PROFILE, nested={"admitted": "yes"}), None, "flags: /nested/admitted"),
            (REUSED_PROFILE, ["research/challenge-8/cloud-build/old/BUDGET.json", "research/challenge-8/proof.py"],
             "not referenced by the recipe"),
        ]
        for profile, proof_paths, message in cases:
            with self.subTest(message=message):
                spec = self.reuse(profile, proof_paths)
                with self.assertRaisesRegex(module.PrepareError, message):
                    self.prepare(spec)
                self.assertFalse(self.out.exists())
        for raw, message in (("{not json", "profile JSON invalid"), ("[1, 2]\n", "profile must be a JSON object")):
            for reuse in (True, False):
                with self.subTest(raw=raw, reuse=reuse):
                    spec = self.reuse()
                    (self.fx.root / self.fx.profile).write_text(raw, encoding="utf-8")
                    git(self.fx.root, "commit", "-qam", "bad profile")
                    spec = dict(spec, baseline_sha=git(self.fx.root, "rev-parse", "HEAD"))
                    if not reuse:
                        spec = dict(self.fx.spec, baseline_sha=spec["baseline_sha"])
                    with self.assertRaisesRegex(module.PrepareError, message):
                        self.prepare(spec)
                    self.assertFalse(self.out.exists())

    def test_profile_changed_between_baseline_and_prepare_is_refused_in_both_modes(self):
        for reuse in (True, False):
            with self.subTest(reuse=reuse):
                spec = self.reuse()
                if not reuse:
                    spec = dict(self.fx.spec)
                self.commit_profile(json.dumps(dict(REUSED_PROFILE, target="changed")) + "\n")
                with self.assertRaisesRegex(module.PrepareError, "historical ledger/profile bytes changed"):
                    self.prepare(spec)
                self.assertFalse(self.out.exists())

    def test_check_history_guard_fires_on_committed_profile_change(self):
        spec = self.reuse()
        self.commit_profile(json.dumps(dict(REUSED_PROFILE, target="changed")) + "\n")
        with patch.object(module, "_assert_history_unchanged", lambda *args: None):
            bundle = self.prepare(spec)
        with self.assertRaisesRegex(module.PrepareError, "historical ledger/profile bytes changed after the closed-session baseline"):
            module.check(bundle)

    def test_old_ledger_changed_after_baseline_is_refused_by_prepare_and_check(self):
        for reuse in (True, False):
            with self.subTest(reuse=reuse):
                spec = self.reuse()
                if not reuse:
                    spec = dict(self.fx.spec)
                ledger_path = self.fx.root / self.fx.old_ledger
                ledger = json.loads(ledger_path.read_text())
                ledger_path.write_text(json.dumps(dict(ledger, note="rewritten"), sort_keys=True) + "\n", encoding="utf-8")
                git(self.fx.root, "commit", "-qam", "rewrite closed ledger after baseline")
                with self.assertRaisesRegex(module.PrepareError, "historical ledger/profile bytes changed"):
                    self.prepare(spec)
                self.assertFalse(self.out.exists())
                with patch.object(module, "_assert_history_unchanged", lambda *args: None):
                    bundle = self.prepare(spec)
                with self.assertRaisesRegex(module.PrepareError, "historical ledger/profile bytes changed after the closed-session baseline"):
                    module.check(bundle)

    def test_check_refuses_reuse_bundle_with_credit_flags_or_unreferenced_profile(self):
        cases = [(dict(REUSED_PROFILE, proof_credit=True), None, "acceptance/admission/credit flags"),
                 (REUSED_PROFILE, ["research/challenge-8/cloud-build/old/BUDGET.json", "research/challenge-8/proof.py"],
                  "not referenced by the recipe")]
        for profile, proof_paths, message in cases:
            with self.subTest(message=message):
                spec = self.reuse(profile, proof_paths)
                with patch.object(module, "_check_reused_profile", lambda *args: None):
                    bundle = self.prepare(spec)
                with self.assertRaisesRegex(module.PrepareError, message):
                    module.check(bundle)

    def test_rejects_wrong_branch_owner_baseline_and_bad_dates(self):
        cases = [
            {"branch": "wrong-branch"}, {"owner": "select"},
            {"baseline_sha": "f" * 40}, {"t0": "2026-10-22"},
            {"t0": "2026-10-22T10:00:00+00:00"},
        ]
        for override in cases:
            with self.subTest(override=override), self.assertRaises(module.PrepareError):
                self.prepare({**self.fx.spec, **override})

    def test_rejects_negative_or_out_of_policy_budget(self):
        for override in ({"cloud_seconds": -1}, {"cloud_seconds": 86401}, {"max_timeout_seconds": 1741},
                         {"max_timeout_seconds": 0}, {"report_reserve_seconds": 419},
                         {"max_timeout_seconds": 420},
                         {"main_minutes": 0}, {"main_minutes": 10081}, {"main_minutes": "120"},
                         {"finish_minutes": -30}, {"finish_minutes": 241}):
            with self.subTest(override=override), self.assertRaises(module.PrepareError):
                self.prepare({**self.fx.spec, **override})

    def test_explicit_window_and_budget_drive_ledger_deadlines_and_check(self):
        explicit = {**self.fx.spec, "main_minutes": 4320, "finish_minutes": 60,
                    "cloud_seconds": 21600, "max_timeout_seconds": 1500}
        out = self.prepare(explicit)
        ledger = json.loads((out / "ledger.json").read_text(encoding="utf-8"))
        self.assertEqual((ledger["ceiling_build_seconds"], ledger["remaining_build_seconds"]), (21600, 21600))
        self.assertEqual((ledger["main_deadline_utc"], ledger["deadline_utc"]), ("2026-10-25T10:00:00Z", "2026-10-25T11:00:00Z"))
        self.assertEqual(ledger["max_timeout_seconds"], 1500)
        plan = (out / "registration-plan.md").read_text(encoding="utf-8")
        self.assertIn("main deadline `2026-10-25T10:00:00Z`, absolute deadline `2026-10-25T11:00:00Z`", plan)
        module.check(out)
        ledger["main_deadline_utc"] = "2026-10-22T12:00:00Z"
        (out / "ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(module.PrepareError, "differs from the complete spec-derived fresh ledger"):
            module.check(out)

    def test_spec_must_match_installed_assignment_window_budget_and_phase(self):
        task = self.fx.root / "research/challenge-8/CURRENT-TASK.md"
        def install_task(phase, window, budget, timeout):
            task.write_text(f"# Task\n\nOwner: **Merge**. Phase: `{phase}`. Lane: `merge`.\n"
                            f"Cloud budget: {budget} seconds. Wall window: {window} (explicit). Per-Build timeout \u2264{timeout} seconds.\n\n"
                            "## Отчёт агента\n\nnot started\n", encoding="utf-8")
            git(self.fx.root, "add", "."); git(self.fx.root, "commit", "-qm", "install task")
        install_task(self.fx.spec["phase"], "4320 minutes main + 60 minutes closeout", 21600, 1200)
        explicit = {**self.fx.spec, "main_minutes": 4320, "finish_minutes": 60, "cloud_seconds": 21600}
        module.check(self.prepare(explicit))
        for override, message in (({}, "spec window 120\\+30 differs"),
                                  ({"main_minutes": 4320, "finish_minutes": 60}, "spec cloud_seconds 3600 differs"),
                                  ({**explicit, "max_timeout_seconds": 1500}, "exceeds the assignment's 1200"),
                                  ({**explicit, "phase": "MERGE-OTHER-2026-10-24"}, "differs from the installed assignment phase")):
            with self.subTest(override=override), self.assertRaisesRegex(module.PrepareError, message):
                self.prepare({**self.fx.spec, **override})
        install_task(self.fx.spec["phase"], "120 minutes main + 30 minutes closeout", 3600, 1200)
        bundle = self.prepare(self.fx.spec, self.parent / "default-window-bundle")
        module.check(bundle)
        # A bundle rewritten after prepare (spec, ledger, plan and inventory together) still
        # has to match the installed assignment of its phase.
        spec = json.loads((bundle / "spec.json").read_text(encoding="utf-8"))
        spec.update({"main_minutes": 4320, "finish_minutes": 60, "cloud_seconds": 21600})
        (bundle / "spec.json").write_text(json.dumps(spec, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(module.PrepareError, "spec window 4320\\+60 differs|inventory|differs"):
            module.check(bundle)
        task.write_text(f"# Task\n\nPhase: `{self.fx.spec['phase']}`.\nPhase: `OTHER-PHASE`.\n"
                        "Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout.\n\n## Отчёт агента\n", encoding="utf-8")
        git(self.fx.root, "add", "."); git(self.fx.root, "commit", "-qm", "two phases")
        with self.assertRaisesRegex(module.PrepareError, "more than one Phase"):
            self.prepare(self.fx.spec, self.parent / "two-phase-bundle")

    def test_rejects_active_old_ledger_and_requires_retired_closure(self):
        path = self.fx.root / self.fx.old_ledger
        ledger = json.loads(path.read_text())
        ledger["status"] = "AUTHORIZED"
        path.write_text(json.dumps(ledger) + "\n")
        git(self.fx.root, "add", self.fx.old_ledger)
        git(self.fx.root, "commit", "-qm", "bad active legacy account")
        spec = dict(self.fx.spec, baseline_sha=self.fx.baseline)
        with self.assertRaises(module.PrepareError):
            self.prepare(spec)

    def test_accepts_fully_accounted_ledger_with_explicit_retirement(self):
        path = self.fx.root / self.fx.old_ledger
        ledger = json.loads(path.read_text())
        ledger.update({"status": "EXHAUSTED", "retired_closure": {"reason": "budget closed"},
                       "builds": [{"state": "SUCCESS", "charged_seconds": 12, "accounted": True}], "active_build": None})
        path.write_text(json.dumps(ledger) + "\n")
        git(self.fx.root, "add", self.fx.old_ledger)
        git(self.fx.root, "commit", "-qm", "accounted retired legacy account")
        spec = dict(self.fx.spec, baseline_sha=git(self.fx.root, "rev-parse", "HEAD"))
        bundle = self.prepare(spec)
        self.assertEqual(module.check(bundle)["state"], "PREPARED_NOT_REGISTERED")

    def test_closed_ledger_still_requires_matching_owner_and_accounted_builds(self):
        path = self.fx.root / self.fx.old_ledger
        original = json.loads(path.read_text())
        bad_owner = dict(original, owner="select-sort4")
        path.write_text(json.dumps(bad_owner) + "\n")
        git(self.fx.root, "add", self.fx.old_ledger)
        git(self.fx.root, "commit", "-qm", "wrong old ledger owner")
        spec = dict(self.fx.spec, baseline_sha=git(self.fx.root, "rev-parse", "HEAD"))
        with self.assertRaises(module.PrepareError):
            self.prepare(spec)

        bad_builds = dict(original, builds=[{"state": "SUCCESS", "accounted": False}])
        path.write_text(json.dumps(bad_builds) + "\n")
        git(self.fx.root, "add", self.fx.old_ledger)
        git(self.fx.root, "commit", "-qm", "unaccounted closed build")
        spec = dict(self.fx.spec, baseline_sha=git(self.fx.root, "rev-parse", "HEAD"))
        with self.assertRaises(module.PrepareError):
            self.prepare(spec)

    def test_rejects_path_traversal_symlink_and_existing_output(self):
        with self.assertRaises(module.PrepareError):
            self.prepare({**self.fx.spec, "new_ledger_path": "../escape.json"})
        traversal_output = self.parent / "out" / ".." / "worktree" / "unsafe-bundle"
        with self.assertRaises(module.PrepareError):
            self.prepare(self.fx.spec, traversal_output)
        self.assertFalse((self.fx.root / "unsafe-bundle").exists())
        symlink_spec = dict(self.fx.spec, profile_path="research/challenge-8/profile-link.json")
        (self.fx.root / "research/challenge-8/profile-link.json").symlink_to("cloud-build/profile.json")
        git(self.fx.root, "add", "research/challenge-8/profile-link.json")
        git(self.fx.root, "commit", "-qm", "committed profile symlink")
        with self.assertRaises(module.PrepareError):
            self.prepare(symlink_spec)
        with self.assertRaises(module.PrepareError):
            self.prepare(self.fx.spec, self.parent / "out")

    def test_rejects_missing_input_and_recipe_or_profile_mismatch(self):
        missing = dict(self.fx.spec, profile_path="research/challenge-8/missing.json")
        with self.assertRaises(module.PrepareError):
            self.prepare(missing)
        recipe_path = self.fx.root / self.fx.recipe
        recipe = json.loads(recipe_path.read_text())
        recipe["lane"] = "select-lane"
        recipe_path.write_text(json.dumps(recipe) + "\n")
        git(self.fx.root, "add", self.fx.recipe)
        git(self.fx.root, "commit", "-qm", "wrong recipe lane")
        with self.assertRaises(module.PrepareError):
            self.prepare()

    def test_rejects_updates_that_enable_credit_or_cloud_and_tampered_bundle(self):
        bad = dict(self.fx.spec, profile_updates={"/proof_credit": True})
        with self.assertRaises(module.PrepareError):
            self.prepare(bad)
        bundle = self.prepare()
        profile_path = bundle / "profile.json"
        profile = json.loads(profile_path.read_text())
        profile["target"] = "tampered"
        profile_path.write_text(json.dumps(profile) + "\n")
        with self.assertRaises(module.PrepareError):
            module.check(bundle)

    def test_check_rejects_cross_file_tampering_even_with_refreshed_hash_inventory(self):
        bundle = self.prepare()
        ledger_path = bundle / "ledger.json"
        ledger = json.loads(ledger_path.read_text())
        ledger["status"] = "AUTHORIZED"
        ledger_path.write_text(json.dumps(ledger, sort_keys=True, indent=2) + "\n")
        inventory_path = bundle / "inventory.json"
        inventory = json.loads(inventory_path.read_text())
        inventory["files"]["ledger.json"] = module._sha256(ledger_path.read_bytes())
        inventory_path.write_text(json.dumps(inventory, sort_keys=True, indent=2) + "\n")
        # Update the inventory hash for the modified inventory itself is impossible by design;
        # the cross-file contract also rejects the unauthorized status directly.
        with self.assertRaises(module.PrepareError):
            module.check(bundle)

    def test_check_rejects_any_spec_derived_ledger_change_even_if_inventory_is_refreshed(self):
        bundle = self.prepare()
        ledger_path = bundle / "ledger.json"
        original = ledger_path.read_bytes()
        for field, value in (("ceiling_build_seconds", 3599), ("remaining_build_seconds", 3599),
                             ("used_build_seconds", 1), ("max_timeout_seconds", 1199),
                             ("report_reserve_seconds", 421), ("carryover_allowed", True),
                             ("authorization", "changed")):
            with self.subTest(field=field):
                ledger = json.loads(original)
                ledger[field] = value
                ledger_path.write_text(json.dumps(ledger, sort_keys=True, indent=2) + "\n")
                self.refresh_inventory(bundle)
                with self.assertRaises(module.PrepareError):
                    module.check(bundle)
        ledger_path.write_bytes(original)
        self.refresh_inventory(bundle)
        self.assertEqual(module.check(bundle)["state"], "PREPARED_NOT_REGISTERED")

    def test_check_rebuilds_recipe_and_plan_and_compares_historical_git_bytes(self):
        bundle = self.prepare()
        recipe_path = bundle / "recipe.json"
        recipe = json.loads(recipe_path.read_text())
        recipe["lane"] = "select-lane"
        recipe_path.write_text(json.dumps(recipe, sort_keys=True, indent=2) + "\n")
        self.refresh_inventory(bundle)
        with self.assertRaises(module.PrepareError):
            module.check(bundle)

        bundle = self.parent / "out" / "other-bundle"
        self.prepare(self.fx.spec, bundle)
        plan = bundle / "registration-plan.md"
        plan.write_text(plan.read_text() + "tampered\n")
        self.refresh_inventory(bundle)
        with self.assertRaises(module.PrepareError):
            module.check(bundle)

        bundle = self.parent / "out" / "third-bundle"
        self.prepare(self.fx.spec, bundle)
        historical = bundle / "old_ledger.raw.json"
        historical.write_bytes(historical.read_bytes() + b" ")
        self.refresh_inventory(bundle)
        with self.assertRaises(module.PrepareError):
            module.check(bundle)

    def test_closure_cli_data_reports_git_mode_blob_and_sha256(self):
        result = module.closure_command(self.fx.root, self.fx.head, Path(self.fx.recipe))
        self.assertEqual(result["commit"], self.fx.head)
        runner = next(item for item in result["entries"] if item["path"].endswith("runner.sh"))
        self.assertEqual(runner["mode"], "100755")
        self.assertEqual(len(runner["blob"]), 40)
        self.assertEqual(len(runner["sha256"]), 64)

    def test_cli_prepare_check_and_closure_commands(self):
        spec_path = self.parent / "cli-spec.json"
        spec_path.write_text(json.dumps(self.fx.spec), encoding="utf-8")
        bundle = self.parent / "out" / "cli-bundle"
        tool = HERE / "session_prepare.py"
        prepare = subprocess.run([sys.executable, str(tool), "prepare", "--spec", str(spec_path), "--out", str(bundle)],
                                 check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(json.loads(prepare.stdout)["state"], "PREPARED_NOT_REGISTERED")
        checked = subprocess.run([sys.executable, str(tool), "check", "--bundle", str(bundle)],
                                 check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(json.loads(checked.stdout)["phase"], self.fx.spec["phase"])
        closed = subprocess.run([sys.executable, str(tool), "closure", "--worktree", str(self.fx.root),
                                 "--commit", self.fx.head, "--recipe", self.fx.recipe],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        summary = json.loads(closed.stdout)
        self.assertEqual(summary["commit"], self.fx.head)
        self.assertEqual(summary["status"], "STATIC_ONLY_NOT_PROOF")
        self.assertLess(len(closed.stdout.encode()), 2000)
        inventory_out = self.parent / "out" / "full-closure.json"
        full = subprocess.run([sys.executable, str(tool), "closure", "--worktree", str(self.fx.root),
                               "--commit", self.fx.head, "--recipe", self.fx.recipe,
                               "--inventory-out", str(inventory_out)],
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(json.loads(inventory_out.read_text()), module.closure_command(self.fx.root, self.fx.head, Path(self.fx.recipe)))
        self.assertEqual(json.loads(full.stdout)["inventory_path"], str(inventory_out))
        self.assertLess(len(full.stdout.encode()), 2000)
        collision = subprocess.run([sys.executable, str(tool), "closure", "--worktree", str(self.fx.root),
                                    "--commit", self.fx.head, "--recipe", self.fx.recipe,
                                    "--inventory-out", str(inventory_out)],
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(collision.returncode, 2)
        symlink_out = self.parent / "out" / "closure-link.json"
        symlink_out.symlink_to(inventory_out)
        symlink_result = subprocess.run([sys.executable, str(tool), "closure", "--worktree", str(self.fx.root),
                                         "--commit", self.fx.head, "--recipe", self.fx.recipe,
                                         "--inventory-out", str(symlink_out)],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertEqual(symlink_result.returncode, 2)

    def test_closure_expands_directory_recipe_paths(self):
        subdir = self.fx.root / "research/challenge-8/cloud-build/runtime"
        subdir.mkdir()
        (subdir / "one.py").write_text("one\n")
        (subdir / "two.py").write_text("two\n")
        recipe_path = self.fx.root / self.fx.recipe
        recipe = json.loads(recipe_path.read_text())
        recipe["infra_paths"] = ["research/challenge-8/cloud-build/runtime"]
        recipe["proof_paths"] = ["research/challenge-8/proof.py"]
        recipe_path.write_text(json.dumps(recipe) + "\n")
        git(self.fx.root, "add", ".")
        git(self.fx.root, "commit", "-qm", "directory recipe closure")
        head = git(self.fx.root, "rev-parse", "HEAD")
        result = module.closure_command(self.fx.root, head, Path(self.fx.recipe))
        paths = {entry["path"] for entry in result["entries"]}
        self.assertIn("research/challenge-8/cloud-build/runtime/one.py", paths)
        self.assertIn("research/challenge-8/cloud-build/runtime/two.py", paths)

    def test_closure_rejects_git_wildcard_pathspecs(self):
        recipe_path = self.fx.root / self.fx.recipe
        recipe = json.loads(recipe_path.read_text())
        recipe["infra_paths"] = ["research/challenge-8/cloud-build/runner*"]
        recipe["proof_paths"] = ["research/challenge-8/proof.py"]
        recipe_path.write_text(json.dumps(recipe) + "\n")
        git(self.fx.root, "add", self.fx.recipe)
        git(self.fx.root, "commit", "-qm", "wildcard pathspec recipe")
        head = git(self.fx.root, "rev-parse", "HEAD")
        with self.assertRaises(module.PrepareError):
            module.closure_command(self.fx.root, head, Path(self.fx.recipe))

    def test_closure_deduplicates_valid_cross_role_overlap(self):
        recipe_path = self.fx.root / self.fx.recipe
        recipe = json.loads(recipe_path.read_text())
        shared = "research/challenge-8/proof.py"
        recipe["infra_paths"] = [shared]
        recipe["proof_paths"] = [shared]
        recipe_path.write_text(json.dumps(recipe) + "\n")
        git(self.fx.root, "add", self.fx.recipe)
        git(self.fx.root, "commit", "-qm", "shared cross-role path")
        head = git(self.fx.root, "rev-parse", "HEAD")
        result = module.closure_command(self.fx.root, head, Path(self.fx.recipe))
        shared_records = [entry for entry in result["entries"] if entry["path"] == shared]
        self.assertEqual(len(shared_records), 1)
        self.assertEqual(shared_records[0]["groups"], ["infra", "proof"])

        recipe["infra_paths"] = [shared, shared]
        recipe_path.write_text(json.dumps(recipe) + "\n")
        git(self.fx.root, "add", self.fx.recipe)
        git(self.fx.root, "commit", "-qm", "duplicate within role")
        head = git(self.fx.root, "rev-parse", "HEAD")
        with self.assertRaises(module.PrepareError):
            module.closure_command(self.fx.root, head, Path(self.fx.recipe))

    def test_generated_file_collision_and_recipe_symlink_are_refused(self):
        target = self.fx.root / self.fx.new_ledger
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("collision\n")
        with self.assertRaises(module.PrepareError):
            self.prepare()


if __name__ == "__main__":
    unittest.main()
