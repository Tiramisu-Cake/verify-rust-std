"""R12 registration and lossless transport service tests; no proof work."""
from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import lzma
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
CLOUD = HERE.parent
ROOT = CLOUD.parents[2]
sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r12_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)

PHASE = "SORT4-CHECKED-HELPER-CALLER-2026-10-21-R12"
PROFILE_NAME = "A1-CHECKED-HELPER-R12-PROFILE-2026-10-21.json"
LEDGER_NAME = "BUDGET-A1-CHECKED-HELPER-2026-10-21-R12.json"
START = "2026-10-21T06:14:26Z"
MAIN = "2026-10-21T08:14:26Z"
DEADLINE = "2026-10-21T08:44:26Z"
LANE = "o26-sort4-c1-current-recovery"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class R12Registration(unittest.TestCase):
    def test_fresh_account_profile_and_existing_history_are_separate(self):
        profile = json.loads((HERE / PROFILE_NAME).read_text())
        # Authorization is an immutable published snapshot; the live ledger
        # changes legitimately while Builds are active and after closeout.
        initial_candidate = "f274662fc8f45ae1455bac141c8236f322ca2269"
        ledger_path = (HERE / LEDGER_NAME).relative_to(ROOT).as_posix()
        ledger = json.loads(subprocess.check_output(
            ["git", "show", initial_candidate + ":" + ledger_path],
            cwd=ROOT, text=True))
        self.assertEqual(profile["authorization_phase_id"], PHASE)
        self.assertEqual(profile["phase"], PHASE)
        self.assertEqual(profile["experiment_protocol_phase_id"], CONTROL.A1_PHASE)
        self.assertEqual(profile["account"], LEDGER_NAME)
        self.assertEqual((profile["start_utc"], profile["main_deadline_utc"],
                          profile["deadline_utc"]), (START, MAIN, DEADLINE))
        self.assertEqual(profile["status"], "R12_AUTHORIZED_NOT_RUN")
        self.assertFalse(profile["proof_credit"])
        self.assertEqual(profile["execution_mode"], "full-matrix")
        self.assertEqual(profile["build_timeout_seconds"], 1200)
        self.assertEqual(profile["stage_budget_estimate"]["execute_timeout_seconds"], 960)
        self.assertEqual(profile["stage_budget_estimate"]["nominal_work_deadline_seconds"], 900)
        self.assertEqual(ledger["phase"], PHASE)
        self.assertEqual(ledger["owner"], "select-sort4")
        self.assertEqual(ledger["allowed_lanes"], [LANE])
        self.assertEqual(ledger["ceiling_build_seconds"], 3600)
        self.assertEqual(ledger["maximum_build_timeout_seconds"], 1200)
        self.assertEqual((ledger["start_utc"], ledger["main_deadline_utc"],
                          ledger["deadline_utc"]), (START, MAIN, DEADLINE))
        self.assertEqual(ledger["status"], "AUTHORIZED")
        self.assertEqual(ledger["carry_forward_seconds"], 0)
        self.assertEqual(ledger["used_build_seconds"] + ledger["remaining_build_seconds"] +
                         ledger["unused_retired_seconds"], 3600)
        self.assertEqual(ledger["used_build_seconds"],
                         sum(row["build_seconds"] for row in ledger["builds"]
                             if row.get("accounted") is True))
        self.assertTrue(all(row["phase_id"] == PHASE and
                            row["owner"] == "select-sort4" and row["lane"] == LANE
                            for row in ledger["builds"]))
        self.assertIsNone(ledger["active_build"])

        old_profile = json.loads((HERE / "A1-CHECKED-CALLER-R11-PROFILE-2026-10-21.json").read_text())
        old_ledger = json.loads((HERE / "BUDGET-A1-CHECKED-CALLER-2026-10-21-R11.json").read_text())
        self.assertEqual(old_profile["authorization_phase_id"], CONTROL.A1_R11_PHASE)
        self.assertEqual(old_ledger["phase"], CONTROL.A1_R11_PHASE)
        self.assertEqual(old_ledger["status"], "CLOSED")
        self.assertGreater(len(old_ledger["builds"]), 0)

        for key, filename in (("a1_entry_sha256", "a1-entry-r12.py"),
                              ("a1_runner_sha256", "a1-runner-r12.py"),
                              ("a1_source_runner_sha256", "a1-runner.py")):
            self.assertEqual(profile[key], sha(HERE / filename), key)
        self.assertEqual(profile["a1_helper_sha256"]["a1-focus-backend.py"],
                         sha(HERE / "a1-focus-backend.py"))
        self.assertEqual(profile["a1_helper_sha256"]["a1-tool.py"],
                         sha(HERE / "a1-tool.py"))
        self.assertTrue(profile["ghost_grammar_preflight_enabled"])
        self.assertEqual(profile["a1_ghost_grammar_sha256"], sha(HERE / "a1-ghost-grammar.py"))
        self.assertEqual(profile["a1_checked_cleanup_import_sha256"],
                         "0ee7ebcc19c7a21bbe329d70e6e763ee43c7647b556ad6184982997ec4fa911f")

    def test_coordinator_recipe_lane_and_core_route_select_only_r12_profile(self):
        recipe = json.loads((CLOUD / "recipes/o26-sort4-c1-current-recovery.json").read_text())
        canonical = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
        self.assertIn(canonical + PROFILE_NAME, recipe["proof_paths"])
        self.assertIn(canonical + "a1-ghost-grammar.py", recipe["proof_paths"])
        for name in (PROFILE_NAME, "a1-entry-r12.py", "a1-runner-r12.py"):
            self.assertIn(canonical + name, recipe["infra_paths"])
        lane = (CLOUD / "run-sort4-c1-current-recovery.sh").read_text()
        self.assertLess(lane.index(PHASE), lane.index(CONTROL.A1_R11_PHASE))
        self.assertIn("a1-entry-r12.py", lane)
        self.assertIn("a1-entry-r11.py", lane)
        self.assertEqual(CONTROL.A1_R12_PROFILE, canonical + PROFILE_NAME)
        self.assertEqual(CONTROL.r12_time_budget(1200), {
            "package_reserve": 240, "work_seconds": 960, "soft_margin": 60})
        self.assertEqual(CONTROL.r12_time_budget(1000), {
            "package_reserve": 240, "work_seconds": 760, "soft_margin": 60})
        for invalid in (89, 1201, True, 1000.0):
            with self.subTest(timeout=invalid), self.assertRaises(ValueError):
                CONTROL.r12_time_budget(invalid)

    def test_r12_coordinator_capacity_and_historical_local_cap(self):
        self.assertIsNone(CONTROL.legacy_a1_occupied_limit(PHASE))
        self.assertEqual(CONTROL.legacy_a1_occupied_limit(CONTROL.A1_R11_PHASE), 2)
        coord = CONTROL.coordination
        ongoing = [{"id": f"build-{i}", "tags": []} for i in range(3)]
        with patch.object(coord, "protocol", return_value=(3, 3)), \
             patch.object(coord, "reservations", return_value=[]):
            coord.require_capacity("select-sort4", "/tmp/r12-ledger.json", ongoing[:2])
            with self.assertRaisesRegex(RuntimeError, "All Cloud Build slots"):
                coord.require_capacity("select-sort4", "/tmp/r12-ledger.json", ongoing)
            with self.assertRaisesRegex(RuntimeError, "Unsupported v3 Cloud Build owner"):
                coord.require_capacity("other-owner", "/tmp/r12-ledger.json", ongoing[:1])

    def test_ghost_grammar_gate_and_blocker_preserve_failures(self):
        runner_spec = importlib.util.spec_from_file_location("r12_grammar_gate_runner", HERE / "a1-runner.py")
        runner = importlib.util.module_from_spec(runner_spec)
        sys.modules[runner_spec.name] = runner
        runner_spec.loader.exec_module(runner)
        log_hash = "a" * 64
        tool_hash = "b" * 64
        tool_identity_hash = "9" * 64
        source_hash = "c" * 64
        pair = {"verified/lib.rs": source_hash, "original/lib.rs": "d" * 64}
        variant = {"stage": {"classification": "TERMINAL", "exit": 0,
                             "log_sha256": log_hash},
                   "source_pair_sha256": pair,
                   "source_sha256": source_hash, "original_sha256": "d" * 64,
                   "tool_binary_sha256_after": tool_hash,
                   "tool_identity_sha256_after": tool_identity_hash,
                   "same_active_tool_after_stage": True}
        positive = {**variant, "status": "GRAMMAR_POSITIVE_PASS",
                    "syntax_status": "GRAMMAR_SYNTAX_PASS",
                    "body_probe_status": "MINI_UNIT_EXIT_ZERO_NOT_CANONICAL_PROOF",
                    "body_verified": False, "helper_body_end_line": 12,
                    "ast_path": "/workspace/ast.ml",
                    "ast_sha256": "e" * 64,
                    "ast_selection": {"classification": "ONE_SOURCE_INTERVAL_SELECTED_CHECKED_LEMMA",
                                     "body_count_from_intervals": 1,
                                     "selected": {"name": "a1_cleanup_option_ref", "kind": "lemma"},
                                     "proof_credit": False}}
        negative = {**variant, "stage": {"classification": "TERMINAL", "exit": 1,
                                          "log_sha256": log_hash},
                    "status": "EXPECTED_GRAMMAR_REJECTION",
                    "diagnostic_match": {"matched": True,
                                         "expected_diagnostic": "expected error",
                                         "expected_source_line": 20,
                                         "diagnostics": ["verified/lib.rs(20,1): error: expected error"]}}
        good = {"schema": "a1-ghost-grammar-preflight-v1", "status": "GRAMMAR_SYNTAX_PREFLIGHT_PASS",
                "build_id": "build-r12", "project_id": "smallsort-ci",
                "phase_id": "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17",
                "authorization_phase_id": PHASE, "profile_sha256": "f" * 64,
                "tool_binary_sha256": tool_hash, "tool_identity_sha256": tool_identity_hash,
                "proof_credit": False, "caller_receipt": False, "body_verified": False,
                "body_probe_status": "MINI_UNIT_EXIT_ZERO_NOT_CANONICAL_PROOF",
                "source_identity": {key: {"verified_source_sha256": source_hash,
                                           "original_source_sha256": "d" * 64,
                                           "source_pair_sha256": pair}
                                    for key in ("positive", "negative_fully_qualified",
                                                "negative_import_inside_block")},
                "variants": {"positive": positive, "negative_fully_qualified": negative,
                             "negative_import_inside_block": negative}}
        receipt = {"console_binary_sha256": tool_hash}
        self.assertTrue(runner.r12_ghost_grammar_passed(
            good, build_id="build-r12", project_id="smallsort-ci",
            profile_sha256="f" * 64, tool_receipt=receipt))
        for bad in (None, "PASS", {**good, "status": "GRAMMAR_PREFLIGHT_BLOCKED"},
                    {**good, "variants": {"positive": positive}},
                    {**good, "variants": {**good["variants"], "positive": {"status": "NOT_RUN"}}},
                    {**good, "authorization_phase_id": "other"},
                    {**good, "status": "GRAMMAR_PREFLIGHT_INCONCLUSIVE",
                     "variants": {"positive": {"status": "NOT_RUN_DEADLINE"}}},
                    {**good, "variants": {**good["variants"],
                        "positive": {**positive, "stage": None}}}):
            with self.subTest(bad=type(bad).__name__):
                self.assertFalse(runner.r12_ghost_grammar_passed(
                        bad, build_id="build-r12", project_id="smallsort-ci",
                        profile_sha256="f" * 64,
                        tool_receipt=receipt))
                detail = runner.r12_ghost_preflight_blocker(None, bad)
                state = {"case_status": {case: {"status": "PLANNED"}
                                         for case in runner.CASE_ORDER}}
                stopped = runner.r12_stop_before_dependent_cases(
                    state, detail=detail, execution_events=[], observations={})
                self.assertEqual(stopped["first_causal_stage"],
                                 "ghost-grammar-preflight")
                self.assertEqual(len(stopped["case_status"]), 26)
                self.assertTrue(all(row["status"] == "NOT_RUN"
                                    for row in stopped["case_status"].values()))
        known_leak = {**good, "body_probe_status": "KNOWN_BODY_LEAK_OBSERVED"}
        leak_positive = {**positive, "stage": {"classification": "TERMINAL", "exit": 1,
                                                 "log_sha256": log_hash},
                         "body_probe_status": "KNOWN_BODY_LEAK_OBSERVED",
                         "body_probe_diagnostic": {
                             "matched": True, "expected_source_line": 12,
                             "expected_diagnostic":
                                 "Function leaks heap chunks: own(ref_typeid(...))(...)",
                             "diagnostics": ["verified/lib.rs(12,1): error: "
                                             "Function leaks heap chunks: "
                                             "own(ref_typeid('a_typeid,T_typeid))(t,0)"]}}
        known_leak["variants"] = {**good["variants"], "positive": leak_positive}
        self.assertTrue(runner.r12_ghost_grammar_passed(
            known_leak, build_id="build-r12", project_id="smallsort-ci",
            profile_sha256="f" * 64, tool_receipt=receipt))
        for bad_positive in (
                {**leak_positive, "body_probe_diagnostic": {
                    **leak_positive["body_probe_diagnostic"], "expected_source_line": 11}},
                {**leak_positive, "body_probe_diagnostic": {
                    "matched": True, "expected_source_line": 12,
                    "diagnostics": ["verified/lib.rs(12,1): error: unrelated failure"]}},
                {**leak_positive, "body_probe_diagnostic": {
                    "matched": True, "expected_source_line": 12,
                    "diagnostics": ["verified/lib.rs(12,1): error: Cannot prove "
                                    "own(ref_typeid('a_typeid,T_typeid))(t,0)"]}},
                {**leak_positive, "body_probe_diagnostic": {
                    "matched": True, "expected_source_line": 12,
                    "diagnostics": ["verified/lib.rs(12,1): error: unrelated; "
                                    "Function leaks heap chunks: "
                                    "own(ref_typeid('a_typeid,T_typeid))(t,0)"]}},
                {**positive, "ast_path": None}):
            rejected = {**good, "variants": {**good["variants"],
                                               "positive": bad_positive}}
            self.assertFalse(runner.r12_ghost_grammar_passed(
                rejected, build_id="build-r12", project_id="smallsort-ci",
                profile_sha256="f" * 64, tool_receipt=receipt))
        body_error = {**leak_positive, "status": "GRAMMAR_POSITIVE_UNEXPECTED_ERROR",
                      "syntax_status": "BLOCKED_UNCLASSIFIED_VERIFIER_ERROR",
                      "body_probe_status": "UNEXPECTED_VERIFIER_ERROR",
                      "body_probe_diagnostic": {"matched": False,
                          "expected_source_line": 12,
                          "diagnostics": ["verified/lib.rs(12,1): error: unrelated"]}}
        invalid_positive = [
            {**positive, "ast_path": None},
            {**positive, "ast_selection": {**positive["ast_selection"],
                                            "body_count_from_intervals": 2}},
            {**positive, "source_pair_sha256": {**pair,
                "verified/lib.rs": "0" * 64}},
            {**positive, "tool_binary_sha256_after": "0" * 64},
            body_error,
            {**leak_positive, "body_probe_diagnostic": {
                **leak_positive["body_probe_diagnostic"], "expected_source_line": 11}},
            {**leak_positive, "body_probe_diagnostic": {
                "matched": False, "expected_source_line": 12,
                "diagnostics": ["verified/lib.rs(12,1): error: unrelated failure"]}},
        ]
        for bad_positive in invalid_positive:
            base = (known_leak if bad_positive.get("body_probe_status") ==
                    "KNOWN_BODY_LEAK_OBSERVED" else good)
            rejected = {**base, "variants": {**base["variants"],
                                                "positive": bad_positive}}
            self.assertFalse(runner.r12_ghost_grammar_passed(
                rejected, build_id="build-r12", project_id="smallsort-ci",
                profile_sha256="f" * 64, tool_receipt=receipt))
            detail = runner.r12_ghost_preflight_blocker(None, rejected)
            state = {"case_status": {case: {"status": "PLANNED"}
                                     for case in runner.CASE_ORDER}}
            stopped = runner.r12_stop_before_dependent_cases(
                state, detail=detail, execution_events=[], observations={})
            self.assertEqual(stopped["first_causal_stage"], "ghost-grammar-preflight")
            self.assertTrue(all(row["status"] == "NOT_RUN"
                                for row in stopped["case_status"].values()))
        full_state = {"case_status": {case: {"status": "PLANNED"}
                                       for case in runner.CASE_ORDER}}
        full_stopped = runner.r12_stop_before_dependent_cases(
            full_state, detail={"status": "GRAMMAR_PREFLIGHT_BLOCKED"},
            execution_events=[], observations={}, execution_mode="full-matrix")
        self.assertEqual(full_stopped["classification"],
                         "A1_FULL_MATRIX_BLOCKED_LIFECYCLE")
        self.assertEqual(full_stopped["target_scope"]["mode"], "full-matrix")
        self.assertEqual(full_stopped["target_scope"]["case_ids"],
                         list(runner.CASE_ORDER))
        self.assertEqual(full_stopped["matrix_validation"],
                         "blocked-before-dependent-cases")
        original = {"adapter_error": "RuntimeError: expected diagnostic unavailable",
                    "failed_stage": "ghost-grammar", "stage": {"exit": 23},
                    "artifacts": {"log_sha256": log_hash}, "proof_credit": False}
        retained = runner.r12_ghost_preflight_blocker(original, None)
        self.assertEqual(retained, original)
        self.assertEqual(retained["stage"]["exit"], 23)
        self.assertEqual(retained["artifacts"]["log_sha256"], log_hash)
        self.assertEqual(runner.r12_ghost_preflight_blocker(None, None)["status"],
                         "GRAMMAR_PREFLIGHT_MISSING")
        error_detail = {"adapter_error": "VerifierStageError: stage timeout",
                        "stage": {"classification": "RUNNING", "exit": None},
                        "artifacts": {"partial_log_sha256": log_hash},
                        "execution_started": True, "proof_credit": False}
        for observed, action in ((error_detail, None), (None, None),
                                 (None, {"status": "NOT_RUN_DEADLINE",
                                         "execution_started": False}),
                                 (None, {"status": "GRAMMAR_PREFLIGHT_BLOCKED",
                                         "error": "bad metadata"})):
            detail = runner.r12_ghost_preflight_blocker(observed, action)
            state = {"case_status": {case: {"status": "PLANNED"}
                                     for case in runner.CASE_ORDER}}
            events = [{"case_id": "ghost-grammar-preflight",
                       "event": "blocking_preflight", "proof_credit": False}]
            stopped = runner.r12_stop_before_dependent_cases(
                state, detail=detail, execution_events=events,
                observations={"ghost-grammar-preflight": observed})
            self.assertEqual(stopped["first_causal_stage"], "ghost-grammar-preflight")
            self.assertEqual(stopped["first_blocker"], detail)
            self.assertEqual(len(stopped["case_status"]), 26)
            self.assertTrue(all(row["status"] == "NOT_RUN" and not row["proof_credit"]
                                for row in stopped["case_status"].values()))
        self.assertEqual(runner.r12_ghost_preflight_blocker(
            error_detail, None)["stage"], error_detail["stage"])

    def test_core_profile_registry_and_coordinator_environment(self):
        runner_spec = importlib.util.spec_from_file_location("r12_core_runner", HERE / "a1-runner.py")
        self.assertIsNotNone(runner_spec)
        self.assertIsNotNone(runner_spec.loader)
        runner = importlib.util.module_from_spec(runner_spec)
        sys.modules[runner_spec.name] = runner
        runner_spec.loader.exec_module(runner)
        profile = json.loads((HERE / PROFILE_NAME).read_text())
        self.assertIsNotNone(runner.load_r12_ghost_grammar(ROOT, profile))
        old_profile = json.loads((HERE / "A1-CHECKED-CALLER-R11-PROFILE-2026-10-21.json").read_text())
        self.assertIsNone(runner.load_r12_ghost_grammar(ROOT, old_profile))
        plan = runner.preflight_plan(json.loads((HERE / PROFILE_NAME).read_text()))
        self.assertEqual(plan["classification"], "PLANNED_UNRUN_MATRIX")
        self.assertEqual(plan["case_count"], 26)
        tool_spec = importlib.util.spec_from_file_location("r12_tool_registry", HERE / "a1-tool.py")
        focus_spec = importlib.util.spec_from_file_location("r12_focus_registry", HERE / "a1-focus-backend.py")
        self.assertIsNotNone(tool_spec)
        self.assertIsNotNone(tool_spec.loader)
        self.assertIsNotNone(focus_spec)
        self.assertIsNotNone(focus_spec.loader)
        tool = importlib.util.module_from_spec(tool_spec)
        focus = importlib.util.module_from_spec(focus_spec)
        tool_spec.loader.exec_module(tool)
        focus_spec.loader.exec_module(focus)
        self.assertEqual(tool.FOCUS_PROFILE_NAMES[PHASE], PROFILE_NAME)
        self.assertEqual(focus.PROFILE_BINDINGS[PHASE], PROFILE_NAME)

        entry_spec = importlib.util.spec_from_file_location("r12_entry_constants", HERE / "a1-entry-r12.py")
        adapter_spec = importlib.util.spec_from_file_location("r12_runner_constants", HERE / "a1-runner-r12.py")
        self.assertIsNotNone(entry_spec)
        self.assertIsNotNone(entry_spec.loader)
        self.assertIsNotNone(adapter_spec)
        self.assertIsNotNone(adapter_spec.loader)
        entry = importlib.util.module_from_spec(entry_spec)
        adapter = importlib.util.module_from_spec(adapter_spec)
        entry_spec.loader.exec_module(entry)
        adapter_spec.loader.exec_module(adapter)
        self.assertEqual(entry.AUTHORIZATION_PHASE, PHASE)
        self.assertEqual(adapter.AUTHORIZATION_PHASE, PHASE)
        self.assertEqual(adapter.PROFILE.name, PROFILE_NAME)

        ledger = json.loads((HERE / LEDGER_NAME).read_text())
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        self.assertEqual(CONTROL.authorized_phase(args, ledger).isoformat(),
                         "2026-10-21T08:44:26+00:00")
        for changed in ({"owner": "merge-sort"}, {"start_utc": "2026-10-21T06:14:27Z"},
                        {"maximum_build_timeout_seconds": 900}):
            bad = dict(ledger, **changed)
            with self.subTest(changed=changed), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, bad)

        profile_bytes = (HERE / PROFILE_NAME).read_bytes()
        full_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                           text=True).strip()
        with patch.object(CONTROL.subprocess, "check_output", return_value=profile_bytes):
            env = CONTROL.envs(full_sha, full_sha, LANE, PHASE)
        self.assertIn("SORT4_A1_AUTHORIZATION_PHASE_ID=" + PHASE, env)
        self.assertIn("SORT4_A1_PHASE_ID=" + CONTROL.A1_PHASE, env)
        self.assertIn("SORT4_A1_CHECKED_TRAIT_CONTRACT=1", env)
        self.assertIn("SORT4_A1_PROFILE_SHA256=" + sha(HERE / PROFILE_NAME), env)

    def test_lossless_r12_restore_roundtrip_corruption_and_historical_codec_routes(self):
        source = json.dumps(
            {"embedded": "NUL\u0000 and newline\n", "array": [None, True, 1, 1.0],
             "unicode": "λ\U0001f642"}, ensure_ascii=False,
            separators=(",", ":")).encode("utf-8") + b"\xff\x00trailer"
        encoded, command = CONTROL.source_restore_transport(source, PHASE)
        with tempfile.TemporaryDirectory() as tmp:
            command = command.replace("/workspace", tmp)
            proc = subprocess.run(
                ["bash", "-ceu", "set -o pipefail\n" + command],
                env={"PATH": __import__("os").environ["PATH"],
                     "SOURCE_RESTORE_BYTES": encoded},
                capture_output=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual((Path(tmp) / "source-input.py").read_bytes(), source)
        self.assertEqual(lzma.decompress(base64.b64decode(encoded)), source)
        self.assertIn("lzma.decompress", command)

        with tempfile.TemporaryDirectory() as tmp:
            _, command = CONTROL.source_restore_transport(b"expected", PHASE)
            proc = subprocess.run(
                ["bash", "-ceu", "set -o pipefail\n" + command.replace("/workspace", tmp)],
                env={"PATH": __import__("os").environ["PATH"],
                     "SOURCE_RESTORE_BYTES": "AAAA"}, capture_output=True)
            self.assertNotEqual(proc.returncode, 0)
            output = Path(tmp) / "source-input.py"
            self.assertFalse(output.exists() and output.read_bytes() == b"expected")

        script = (CLOUD / "source-input.py").read_bytes()
        for phase in (CONTROL.A1_R10_PHASE, CONTROL.A1_R11_PHASE):
            old_encoded, old_command = CONTROL.source_restore_transport(script, phase)
            self.assertEqual(lzma.decompress(base64.b64decode(old_encoded)), script)
            self.assertIn("lzma.decompress", old_command)
        r9_encoded, r9_command = CONTROL.source_restore_transport(script, CONTROL.A1_R9_PHASE)
        self.assertEqual(r9_encoded, base64.b64encode(gzip.compress(script, mtime=0)).decode())
        self.assertIn("gzip --decompress", r9_command)

    def test_real_length_config_preserves_full_token_and_all_existing_limits(self):
        full_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                           text=True).strip()
        profile_bytes = json.dumps({"authorization_phase_id": PHASE,
                                    "experiment_protocol_phase_id": CONTROL.A1_PHASE}).encode()
        for suffix in ("0" * 32, "f" * 32):
            token = "dispatch-" + suffix
            with patch.object(CONTROL.subprocess, "check_output", return_value=profile_bytes):
                cfg = CONTROL.config(full_sha, full_sha, LANE, 1200, token,
                                     b"x" * 540827, PHASE)
            self.assertIn(token, cfg["tags"])
            self.assertEqual(cfg["timeout"], "1200s")
            self.assertLessEqual(len(cfg["substitutions"]), 200)
            self.assertTrue(all(len(value.encode()) <= 4000
                                for value in cfg["substitutions"].values()))
            self.assertTrue(all(len(arg.encode()) <= 10000
                                for step in cfg["steps"] for arg in step["args"]))
            self.assertTrue(any(name.startswith("_SOURCE_")
                                for name in cfg["substitutions"]))
            restore_env = next(value for value in cfg["steps"][0]["env"]
                               if value.startswith("SOURCE_RESTORE_BYTES="))
            restored = lzma.decompress(base64.b64decode(restore_env.split("=", 1)[1]))
            self.assertEqual(restored, (CLOUD / "source-input.py").read_bytes())
            self.assertIn("960 - 60", cfg["steps"][0]["args"][1])
            submitted = json.loads(json.dumps(cfg))
            for key in submitted["substitutions"]:
                if key.startswith("_SOURCE_"):
                    submitted["substitutions"][key] = "placeholder"
            compressed = gzip.compress((json.dumps(submitted, separators=(",", ":")) + "\n").encode(), mtime=0)
            self.assertLessEqual(len(base64.b64encode(compressed)), 28000)


if __name__ == "__main__":
    unittest.main()
