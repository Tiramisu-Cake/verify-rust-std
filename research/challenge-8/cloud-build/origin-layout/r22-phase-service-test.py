#!/usr/bin/env python3
"""Synthetic R22 phase admission checks; no Cloud calls or proof execution."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0]))
spec = importlib.util.spec_from_file_location("r22_control", HERE.parents[0] / "control.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
callback_spec = importlib.util.spec_from_file_location("r22_first_callback", HERE / "first-callback.py")
callback = importlib.util.module_from_spec(callback_spec)
sys.modules[callback_spec.name] = callback
callback_spec.loader.exec_module(callback)
provider_spec = importlib.util.spec_from_file_location(
    "r22_provider_overlays", HERE.parents[1] / "merge/cloud-build/provider-overlays.py")
provider = importlib.util.module_from_spec(provider_spec)
sys.modules[provider_spec.name] = provider
provider_spec.loader.exec_module(provider)
prove_spec = importlib.util.spec_from_file_location(
    "r22_onecell_prove", HERE.parents[1] / "merge/overnight/guard-ownership/insertion-onecell/prove.py")
prove = importlib.util.module_from_spec(prove_spec)
sys.modules[prove_spec.name] = prove
prove_spec.loader.exec_module(prove)


def account():
    return {
        "phase": m.R22_PHASE, "phase_id": m.R22_PHASE, "owner": "merge",
        "authorization_model": "bounded-cloud-budget", "authorization": m.R22_AUTHORIZATION,
        "schema": "smallsort-prepared-session-ledger-v1", "task_id": m.R22_TASK_ID,
        "status": "AUTHORIZED", "allowed_lanes": ["merge"],
        "ceiling_build_seconds": 3600, "used_build_seconds": 0, "spent_build_seconds": 0,
        "retired_seconds": 0, "remaining_build_seconds": 3600, "max_builds": None,
        "maximum_builds": None,
        "max_timeout_seconds": 1200, "maximum_build_timeout_seconds": 1200,
        "report_reserve_seconds": 420, "builds": [], "active_build": None,
        "start_utc": m.R22_START, "main_deadline_utc": m.R22_MAIN_DEADLINE,
        "deadline_utc": m.R22_DEADLINE, "carryover_allowed": False, "carry_seconds": 0,
        "publication_gate_path": m.R14_GATE_PATH, "profile_path": m.R22_PROFILE_PATH,
        "baseline_profile_sha256": m.R22_PROFILE_SHA256,
        "starting_source_sha": m.R22_STARTING_SOURCE_SHA,
        "starting_tool_commit": m.R22_STARTING_TOOL_COMMIT, "baseline_sha": m.R22_BASELINE_SHA,
    }


def args(**overrides):
    values = {
        "phase_id": m.R22_PHASE, "owner": "merge",
        "ledger": HERE / "CURRENT-RECOVERY-R22-BUDGET-20261023.json",
        "command": "submit", "infra_sha": "a" * 40, "proof_sha": "a" * 40,
        "lane": "merge", "timeout": 1200, "source_mode": "pinned-objects",
    }
    values.update(overrides)
    return type("Args", (), values)()


def clock(moment):
    real = m.datetime.datetime

    class Frozen(real):
        @classmethod
        def now(cls, tz=None):
            return real.fromisoformat(moment)

    return patch.object(m.datetime, "datetime", Frozen)


class R22PhaseTests(unittest.TestCase):
    def setUp(self):
        self.clock = clock("2026-10-23T08:00:00+00:00")
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def test_exact_phase_account_source_gate_and_upload_routing(self):
        with patch.object(m, "r14_read_selected_gate") as gate, \
             patch.object(m, "r22_validate_sources") as source:
            m.authorized_phase(args(), account())
        gate.assert_called_once_with("a" * 40)
        source.assert_called_once_with(m.R22_PROBE_SOURCE, "a" * 40)
        self.assertTrue(m.required_upload_guard(m.R22_PHASE))
        for phase in (m.R17_PHASE, m.R18_PHASE, m.R19_PHASE, m.R20_PHASE):
            self.assertTrue(m.required_upload_guard(phase))

    def test_prepared_ledger_and_old_phase_cannot_dispatch(self):
        for status, phase in (("PREPARED_NOT_REGISTERED", m.R22_PHASE),
                              ("AUTHORIZED", m.R20_PHASE), ("AUTHORIZED", m.R19_PHASE)):
            ledger = account(); ledger.update(status=status, phase=phase, phase_id=phase)
            with self.subTest(status=status, phase=phase), self.assertRaises(SystemExit):
                m.authorized_phase(args(phase_id=phase, command="request"), ledger)

    def test_account_identity_pins_types_and_budget_fail_closed(self):
        bad = (
            ("owner", "select"), ("authorization", "draft"), ("allowed_lanes", ["select"]),
            ("task_id", "old-task"), ("maximum_builds", 3),
            ("ceiling_build_seconds", True), ("max_timeout_seconds", 1201),
            ("maximum_build_timeout_seconds", 1199), ("start_utc", "2026-10-22T22:25:32Z"),
            ("main_deadline_utc", "2026-10-23T00:25:32Z"),
            ("deadline_utc", "2026-10-23T00:55:32Z"), ("report_reserve_seconds", 419),
            ("carryover_allowed", True), ("carry_seconds", 1),
            ("publication_gate_path", "other"), ("profile_path", "other"),
            ("baseline_profile_sha256", "0" * 64), ("starting_source_sha", "0" * 40),
            ("starting_tool_commit", "0" * 40), ("baseline_sha", "0" * 40),
            ("remaining_build_seconds", 3599), ("used_build_seconds", -1),
            ("used_build_seconds", True), ("spent_build_seconds", 1),
            ("retired_seconds", 1), ("active_build", "dispatch-x"), ("builds", None),
            ("builds", [{"owner": "select", "phase_id": m.R22_PHASE}]), ("max_builds", 3),
        )
        for key, value in bad:
            ledger = account(); ledger[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(SystemExit):
                m.authorized_phase(args(command="request"), ledger)
        missing = account(); del missing["active_build"]
        with self.assertRaises(SystemExit):
            m.authorized_phase(args(command="request"), missing)

    def test_submit_requires_same_full_pinned_source_merge_and_valid_timeout(self):
        for values in (
            {"owner": "select"}, {"lane": "select"}, {"source_mode": "public-git"},
            {"infra_sha": "b" * 40}, {"timeout": 1201}, {"timeout": 509},
            {"timeout": True}, {"ledger": HERE / "other.json"},
        ):
            with self.subTest(values=values), self.assertRaises(SystemExit):
                m.authorized_phase(args(**values), account())

    def test_window_edges_and_queue_reserve(self):
        cases = (("2026-10-23T07:43:59+00:00", "request"),
                 ("2026-10-23T09:44:00+00:00", "request"),
                 ("2026-10-23T09:44:00+00:00", "submit"))
        for moment, command in cases:
            with self.subTest(moment=moment), clock(moment), self.assertRaises(SystemExit):
                m.authorized_phase(args(command=command), account())
        # At the last main-window second, the maximum timeout and queue reserve
        # still fit before the absolute cutoff.
        with clock("2026-10-23T09:22:59+00:00"), patch.object(m, "r14_read_selected_gate"), \
             patch.object(m, "r22_validate_sources"):
            m.authorized_phase(args(timeout=1200), account())
        with clock("2026-10-23T09:22:59+00:00"), patch.object(m, "r14_read_selected_gate"), \
             patch.object(m, "r22_validate_sources"):
            m.authorized_phase(args(timeout=510), account())

    def test_final_recheck_rejects_main_crossing_and_absolute_deadline(self):
        real = m.datetime.datetime
        now = [real.fromisoformat("2026-10-23T08:10:00+00:00")]

        class MovingClock(real):
            @classmethod
            def now(cls, tz=None): return now[0]

        for later in ("2026-10-23T09:44:00+00:00", "2026-10-23T10:14:01+00:00"):
            now[0] = real.fromisoformat("2026-10-23T08:10:00+00:00")

            def slow(*_): now[0] = real.fromisoformat(later)

            with self.subTest(later=later), patch.object(m.datetime, "datetime", MovingClock), \
                 patch.object(m, "r14_read_selected_gate"), patch.object(m, "r22_validate_sources", side_effect=slow), \
                 self.assertRaises(SystemExit):
                m.authorized_phase(args(timeout=1200), account())
        with clock("2026-10-23T09:22:59+00:00"), self.assertRaises(SystemExit):
            m.r22_final_deadline_check(args(timeout=1800), account())

    def test_full_envelope_must_fit_main(self):
        with clock("2026-10-23T09:23:01+00:00"), self.assertRaises(SystemExit):
            m.authorized_phase(args(timeout=1200), account())
        with clock("2026-10-23T09:23:01+00:00"), self.assertRaises(SystemExit):
            m.r22_final_deadline_check(args(timeout=1200), account())

    def test_recipe_delta_and_historical_closure_are_exact(self):
        recipe_path = HERE.parents[0] / "recipes/merge.json"
        selected_recipe = json.loads(recipe_path.read_text())
        pruned_inputs = "research/challenge-8/cloud-build/origin-layout/R11-INPUTS-20261021.json"
        retained_start = "research/challenge-8/cloud-build/origin-layout/R11-START-20261021.json"
        pruned_build1 = "research/challenge-8/cloud-build/origin-layout/R11-BUILD1-RESULT-20261021.json"
        self.assertIn(pruned_inputs, m.R22_REMOVED_PATHS)
        self.assertNotIn(pruned_inputs, selected_recipe["proof_paths"])
        self.assertIn(pruned_build1, m.R22_REMOVED_PATHS)
        self.assertNotIn(pruned_build1, selected_recipe["proof_paths"])
        self.assertIn(retained_start, selected_recipe["proof_paths"])
        runtime_paths = selected_recipe["proof_paths"] + selected_recipe["infra_paths"]
        for rel in runtime_paths:
            if rel.endswith((".py", ".sh")):
                body = (HERE.parents[3] / rel).read_text()
                self.assertNotIn(pruned_inputs, body, rel)
                self.assertNotIn(pruned_build1, body, rel)
        prove_source = (HERE.parents[3] / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py").read_text()
        self.assertIn("R11-START-20261021.json", prove_source)
        self.assertNotIn(pruned_inputs, prove_source)
        self.assertNotIn(pruned_build1, prove_source)
        old = sorted({"a", "b", *m.R22_REMOVED_PATHS})
        before = {"schema": "smallsort-cloud-recipe-v1", "lane": "merge", "infra_paths": ["i"], "proof_paths": old}
        selected = dict(before, proof_paths=sorted(({"a", "b"} | m.R22_ADDED_PATHS)))
        m.r22_validate_recipe_delta(before, selected)
        for bad in (dict(selected, lane="select"), dict(selected, proof_paths=list(reversed(selected["proof_paths"]))),
                    dict(selected, proof_paths=sorted({"a", *m.R22_ADDED_PATHS})),
                    dict(selected, proof_paths=sorted({"a", "b", *m.R22_ADDED_PATHS, "extra"}))):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                m.r22_validate_recipe_delta(before, bad)
        paths = {m.R21_LEDGER_PATH, m.R20_LEDGER_PATH, m.R19_LEDGER_PATH, m.R18_LEDGER_PATH, m.R17_LEDGER_PATH, m.R16_LEDGER_PATH,
                 m.R13_MODE_PATH, m.R14_GATE_PATH, m.R17_PROFILE_PATH, m.R22_PROFILE_PATH}
        tree = {p: ("100644", "blob", hashlib.sha1(p.encode()).hexdigest()) for p in paths}
        m.r22_validate_historical_closure(paths, tree, dict(tree))
        changed = dict(tree); changed[m.R20_LEDGER_PATH] = ("100644", "blob", "0" * 40)
        with self.assertRaises(SystemExit):
            m.r22_validate_historical_closure(paths, tree, changed)

    def test_wrong_source_and_candidate_pins_fail_closed(self):
        with self.assertRaises(SystemExit):
            m.r22_validate_sources("0" * 40, "a" * 40)
        with self.assertRaises(SystemExit):
            m.r22_validate_sources(m.R22_PROBE_SOURCE, "not-a-sha")
        root = HERE.parents[2]
        import subprocess
        show = lambda rel: subprocess.check_output(["git", "show", m.R22_PROBE_SOURCE + ":" + rel], cwd=root)
        baseline_profile, baseline_patch = show(m.R22_PROFILE_PATH), show(m.R17_PATCH_PATH)
        baseline_provider = show(m.R17_PROVIDER_OVERLAYS_PATH)
        m.r22_validate_candidate_pins(baseline_profile, baseline_profile, baseline_profile,
                                      baseline_patch, baseline_provider, baseline_provider,
                                      baseline_provider)
        candidate_profile = (HERE / "GLUE-PROFILE.json").read_bytes()
        candidate_patch = (HERE / "r9-guard-return-trace.patch").read_bytes()
        candidate_provider = (HERE.parents[1] / "merge/cloud-build/provider-overlays.py").read_bytes()
        self.assertEqual(m.r22_validate_candidate_pins(
            baseline_profile, candidate_profile, candidate_profile, candidate_patch,
            baseline_provider, candidate_provider, candidate_provider), "r22-owned-nll-diagnostic")
        compile_profile = subprocess.check_output(
            ["git", "show", "4ee2a25345e7362d4c3872178e326f956d96ab1b:" + m.R22_PROFILE_PATH], cwd=root)
        compile_patch = subprocess.check_output(["git", "show", "4ee2a25345e7362d4c3872178e326f956d96ab1b:" + m.R17_PATCH_PATH], cwd=root)
        self.assertEqual(m.r22_validate_candidate_pins(
            baseline_profile, compile_profile, compile_profile, compile_patch,
            baseline_provider, candidate_provider, candidate_provider), "r22-compile-fix")
        legacy = show(m.R20_METADATA_TEST_PATH)  # any other bytes
        for index, value in ((0, legacy), (1, legacy), (2, legacy), (3, legacy), (4, legacy), (5, legacy), (6, legacy)):
            values = [baseline_profile, candidate_profile, candidate_profile, candidate_patch,
                      baseline_provider, candidate_provider, candidate_provider]
            values[index] = value
            with self.subTest(index=index), self.assertRaises(SystemExit):
                m.r22_validate_candidate_pins(*values)
        for index, value in ((0, None), (1, None), (2, None), (3, None),
                             (4, None), (5, None), (6, None)):
            values = [baseline_profile, candidate_profile, candidate_profile, candidate_patch,
                      baseline_provider, candidate_provider, candidate_provider]
            values[index] = value
            with self.subTest(null_index=index), self.assertRaises(SystemExit):
                m.r22_validate_candidate_pins(*values)
        partial = json.loads(candidate_profile)
        del partial["r22_owned_nll_registration"]["tool_source_paths"]
        partial_bytes = (json.dumps(partial, indent=2, ensure_ascii=False) + "\n").encode()
        for index, value in ((1, partial_bytes), (2, partial_bytes),
                             (3, candidate_patch + b"x"), (5, candidate_provider + b"\n"),
                             (6, candidate_provider + b"\n")):
            values = [baseline_profile, candidate_profile, candidate_profile, candidate_patch,
                      baseline_provider, candidate_provider, candidate_provider]
            values[index] = value
            with self.subTest(partial_or_off_by_one=index), self.assertRaises(SystemExit):
                m.r22_validate_candidate_pins(*values)
        for field, value in (("exporter_source_sha256", None),
                             ("exporter_source_sha256", 17),
                             ("schema_sha256", None),
                             ("refiner_core_source_sha256", 17),
                             ("translator_sha256", None),
                             ("translator_sha256", "e5fe47a16b1a94dcfd07d7d7c0355d4e5acb999650f00498d11606909960dde3"[:-1] + "0"),
                             ("effective_tool_commit", None),
                             ("effective_tool_commit", "419ff27dcee1a31a9f62e8db69049adb725bdbe0"),
                             ("guard_return_trace_patch_sha256", None)):
            malformed = json.loads(candidate_profile)
            malformed[field] = value
            malformed_bytes = (json.dumps(malformed, indent=2, ensure_ascii=False) + "\n").encode()
            with self.subTest(profile_pin=(field, value)), self.assertRaises(SystemExit):
                m.r22_validate_candidate_pins(baseline_profile, malformed_bytes, malformed_bytes,
                                              candidate_patch, baseline_provider,
                                              candidate_provider, candidate_provider)
        wrong_tool = candidate_profile.replace(m.R22_OWNED_NLL_TOOL_COMMIT.encode(), b"0" * 40)
        with self.assertRaises(SystemExit):
            m.r22_validate_candidate_pins(baseline_profile, wrong_tool, wrong_tool, candidate_patch,
                                          baseline_provider, candidate_provider, candidate_provider)

    def test_r22_historical_closure_allows_only_profile_extension(self):
        path = m.R22_PROFILE_PATH
        required = {m.R21_LEDGER_PATH, m.R20_LEDGER_PATH, m.R19_LEDGER_PATH, m.R18_LEDGER_PATH,
                    m.R17_LEDGER_PATH, m.R16_LEDGER_PATH, m.R13_MODE_PATH, m.R14_GATE_PATH,
                    m.R17_PROFILE_PATH, path}
        old = {item: ("100644", "blob", "a" * 40) for item in required}
        old["other"] = ("100644", "blob", "b" * 40)
        candidate = dict(old, **{path: ("100644", "blob", "c" * 40)})
        m.r22_validate_historical_closure(set(old), old, candidate)
        changed_other = dict(candidate, other=("100644", "blob", "d" * 40))
        with self.assertRaises(SystemExit):
            m.r22_validate_historical_closure(set(old), old, changed_other)
        malformed_profile = dict(candidate, **{path: ("100755", "blob", "c" * 40)})
        with self.assertRaises(SystemExit):
            m.r22_validate_historical_closure(set(old), old, malformed_profile)

    def test_callback_accepts_exact_r22_extension_and_keeps_r20_tuple(self):
        git = lambda rev, rel: __import__("subprocess").check_output(
            ["git", "show", rev + ":" + rel], cwd=HERE.parents[3])
        r20_baseline = git("e278869253e5a1e553d0ac0c1bc7adb5221b681e", m.R22_PROFILE_PATH)
        baseline = git(m.R22_PROBE_SOURCE, m.R22_PROFILE_PATH)
        candidate = (HERE / "GLUE-PROFILE.json").read_bytes()
        old_provider = git("e278869253e5a1e553d0ac0c1bc7adb5221b681e", m.R17_PROVIDER_OVERLAYS_PATH)
        r20_provider = git(m.R22_PROBE_SOURCE, m.R17_PROVIDER_OVERLAYS_PATH)
        old_patch = git("e278869253e5a1e553d0ac0c1bc7adb5221b681e", m.R17_PATCH_PATH)
        r20_patch = git(m.R22_PROBE_SOURCE, m.R17_PATCH_PATH)
        self.assertFalse(m.r20_validate_candidate_pins(
            r20_baseline, r20_baseline, r20_baseline, old_patch,
            old_provider, old_provider, old_provider))
        self.assertTrue(m.r20_validate_candidate_pins(
            r20_baseline, baseline, baseline, r20_patch,
            old_provider, r20_provider, r20_provider))
        with __import__("tempfile").TemporaryDirectory(prefix="r22-profile-") as temporary:
            path = Path(temporary) / "profile.json"
            path.write_bytes(baseline)
            self.assertTrue(callback._r20_metadata_registration_matches(
                path, callback.R11_PROFILE, json.loads(baseline)))
            path.write_bytes(r20_baseline)
            self.assertTrue(callback._r19_registration_matches(path, callback.R11_PROFILE))
            path.write_bytes(candidate)
            self.assertTrue(callback._r22_owned_nll_registration_matches(
                path, callback.R22_PROFILE))
            self.assertTrue(callback._r19_registration_matches(path, callback.R22_PROFILE))
            self.assertTrue(callback._r17_registration_matches(
                path, callback.R22_PROFILE, {"profile": callback.R22_PROFILE}))
            card = json.loads(candidate)
            self.assertEqual(provider.profile_identity(card), provider.R22_OWNED_NLL_PROFILE)
            selected = provider.files_for_profile(provider.R22_OWNED_NLL_PROFILE)
            self.assertEqual(selected["research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py"],
                             m.R22_OWNED_NLL_PROVIDER_PROVE_SHA256)
            with self.assertRaises(SystemExit):
                provider.profile_identity(dict(card, profile=provider.R22_OWNED_NLL_PROFILE))
            compile_card = json.loads(__import__("subprocess").check_output([
                "git", "show", "4ee2a25345e7362d4c3872178e326f956d96ab1b:" + m.R22_PROFILE_PATH], cwd=HERE.parents[3]))
            self.assertEqual(provider.profile_identity(compile_card), provider.R22_PROFILE)
            bad = json.loads(candidate)
            bad["r22_owned_nll_registration"]["tool_source_paths"] = []
            path.write_text(json.dumps(bad, indent=2) + "\n")
            self.assertFalse(callback._r22_owned_nll_registration_matches(
                path, callback.R22_PROFILE))

    def test_onecell_profile_dispatch_accepts_only_exact_r22_and_r20_extensions(self):
        baseline = (HERE / "R17-BASELINE-PROFILE-20261021.json").read_bytes()
        current = json.loads((HERE / "GLUE-PROFILE.json").read_bytes())
        old_bytes = __import__("subprocess").check_output([
            "git", "show", m.R22_PROBE_SOURCE + ":" + m.R22_PROFILE_PATH], cwd=HERE.parents[3])
        old = json.loads(old_bytes)
        self.assertTrue(prove.admit_r17_profile_extension_if_present(old, baseline))
        self.assertTrue(prove.admit_r17_profile_extension_if_present(current, baseline))
        corruptions = []
        value = json.loads(json.dumps(current)); value["r22_owned_nll_registration"] = "partial"; corruptions.append(value)
        value = json.loads(json.dumps(current)); del value["r22_owned_nll_registration"]["tool_source_paths"]; corruptions.append(value)
        value = json.loads(json.dumps(current)); value["r22_compile_fix_registration"]["tool_source_paths"] = []; corruptions.append(value)
        value = json.loads(json.dumps(current)); value["r22_owned_nll_registration"]["candidate_tool_commit"] = "0" * 40; corruptions.append(value)
        value = json.loads(json.dumps(current)); value["r22_compile_fix_registration"]["tool_source_paths"] = ["src/rust_frontend/vf_mir_exporter/src/lib.rs"]; corruptions.append(value)
        value = json.loads(json.dumps(current)); value["effective_tool_commit"] = prove.R20_TOOL_COMMIT; corruptions.append(value)
        value = json.loads(json.dumps(current)); value["exporter_source_sha256"] = "0" * 64; corruptions.append(value)
        value = json.loads(json.dumps(current)); value["translator_sha256"] = "0" * 64; corruptions.append(value)
        value = json.loads(json.dumps(current)); value["guard_return_trace_patch_sha256"] = "0" * 64; corruptions.append(value)
        value = json.loads(json.dumps(current)); value["ordered_patch_chain"][-1]["path"] = "unrelated.patch"; corruptions.append(value)
        value = json.loads(json.dumps(current)); value["kernel_sha256"] = "0" * 64; corruptions.append(value)
        value = json.loads(json.dumps(current)); del value["r22_compile_fix_registration"]; corruptions.append(value)
        for corrupted in corruptions:
            with self.subTest(registration=corrupted.get("r22_compile_fix_registration")), self.assertRaises(ValueError):
                prove.admit_r17_profile_extension_if_present(corrupted, baseline)
        with self.assertRaises(ValueError):
            prove.admit_r17_profile_extension_if_present(current, baseline + b" ")

    def test_owned_nll_capture_env_is_exact_case_scoped_and_preserves_results(self):
        outcomes = [
            {"exit_code": 0, "classification": "PASS"},
            {"exit_code": 2, "classification": "ERROR"},
            {"classification": "PARTIAL"}, {}, None, "wrong-type",
            {"classification": "NOT_RUN"}, {"source_stage_target": "mismatch"},
        ]
        original_env = {"VF_EXPORT_OWNED_NLL_FACTS": "inherited"}
        for outcome in outcomes:
            observed = {}
            def execute(case, args, case_env):
                observed.update(case_env)
                return outcome
            result = callback._execute_case_with_r9_trace(
                execute, Path("case"), object(), original_env, profile=callback.R11_PROFILE,
                actual_callback_case=True, owned_nll_capture=True)
            self.assertIs(result, outcome)
            self.assertEqual(observed.get(callback.VF_EXPORT_OWNED_NLL_FACTS), "1")
            self.assertEqual(original_env[callback.VF_EXPORT_OWNED_NLL_FACTS], "inherited")
        for actual_case, enabled in ((False, True), (True, False)):
            observed = {}
            def execute(case, args, case_env):
                observed.update(case_env)
                return {"classification": "NOT_RUN"}
            result = callback._execute_case_with_r9_trace(
                execute, Path("case"), object(), original_env, profile=callback.R11_PROFILE,
                actual_callback_case=actual_case, owned_nll_capture=enabled)
            self.assertEqual(result, {"classification": "NOT_RUN"})
            self.assertNotIn(callback.VF_EXPORT_OWNED_NLL_FACTS, observed)
        import subprocess
        for error in (TimeoutError("synthetic timeout"),
                      subprocess.TimeoutExpired(["synthetic"], 1), SystemExit(7)):
            def fail(case, args, case_env):
                raise error
            with self.assertRaises(type(error)) as raised:
                callback._execute_case_with_r9_trace(
                    fail, Path("case"), object(), {}, profile=callback.R11_PROFILE,
                    actual_callback_case=True, owned_nll_capture=True)
            self.assertIs(raised.exception, error)

    def test_r22_provider_overlay_keeps_public_r11_runtime_profile_name(self):
        path = "research/challenge-8/merge/overnight/run.sh"
        original = (HERE.parents[3] / path).read_bytes()
        for selector in (provider.R22_PROFILE, provider.R22_OWNED_NLL_PROFILE):
            transformed = provider.transform(path, original, {"network_sha": "a" * 64}, profile=selector)
            self.assertIn(b"experimental-merge-label-storage-r11-v1", transformed)
            self.assertNotIn(selector.encode(), transformed)

    def test_execute_budget_preserves_reserve_and_780_second_cap(self):
        for timeout, execute in ((510, 90), (1200, 780)):
            cfg = m.config("a" * 40, "a" * 40, "merge", timeout, "r22-synthetic-token")
            self.assertEqual(m.r17_validate_execute_budget(cfg, timeout), execute)
        for timeout in (509, 1201, True, "1200"):
            with self.subTest(timeout=timeout), self.assertRaises(SystemExit):
                m.r17_validate_execute_budget({}, timeout)

    def test_publisher_ast_keeps_config_fixed_and_routes_r22_guard(self):
        import subprocess
        root = HERE.parents[2]
        baseline = subprocess.check_output(["git", "show",
            m.R14_PROBE_SOURCE + ":research/challenge-8/cloud-build/control.py"], cwd=root).decode()
        current = (HERE.parents[0] / "control.py").read_text()
        m.r14_validate_publisher_control(baseline, current)
        broken = current.replace(",'MERGE-CALLER-ACCEPTANCE-R22-2026-10-23')", ")", 1)
        with self.assertRaises(SystemExit):
            m.r14_validate_publisher_control(baseline, broken)

    def test_reconcile_syncs_r22_spent_seconds_alias(self):
        ledger = account()
        ledger["builds"] = [{"dispatch_token": "dispatch-r22-test", "owner": "merge",
            "phase_id": m.R22_PHASE, "build_id": "build-r22-test", "reserved_seconds": 1260,
            "accounted": False}]
        completed = {"status": "FAILURE", "createTime": "2026-10-22T22:40:00Z",
                     "startTime": "2026-10-22T22:40:01Z", "finishTime": "2026-10-22T22:55:00Z"}
        import tempfile
        with tempfile.TemporaryDirectory(prefix="r22-terminal-reconcile-") as temporary:
            root = Path(temporary)
            with patch.object(m.coordination, "COORDINATION", root / "coordinator"), \
                 patch.object(m, "invoke", return_value=completed):
                m.reconcile(root / "state", ledger, root / "R22-ledger.json")
        self.assertEqual(ledger["used_build_seconds"], 900)
        self.assertEqual(ledger["remaining_build_seconds"], 2700)
        self.assertEqual(ledger["spent_build_seconds"], 900)


if __name__ == "__main__":
    unittest.main()
