"""Synthetic route/pin checks for inactive R21 transport modules only."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
PROFILE_PATH = HERE / "A1-ACTUAL-BODY-R21-TRANSPORT-PROFILE.json"
R19_PROFILE_PATH = HERE / "A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load isolated module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ENTRY = load("a1_entry_r21_transport_test", HERE / "a1-entry-r21.py")
RUNNER = load("a1_runner_r21_transport_test", HERE / "a1-runner-r21.py")
BODY = load("a1_actual_body_r21_transport_test", HERE / "a1-actual-body-r21.py")
TOOL = load("a1_tool_r21_transport_test", HERE / "a1-tool-r21.py")
ORIGINAL_BODY = load("a1_actual_body_r17_transport_oracle", HERE / "a1-actual-body-r17.py")
ORIGINAL_TOOL = load("a1_tool_r17_transport_oracle", HERE / "a1-tool-r17.py")
PROFILE = json.loads(PROFILE_PATH.read_text())
R19_PROFILE = json.loads(R19_PROFILE_PATH.read_text())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_source(path: Path, name: str) -> str:
    text = path.read_text()
    tree = ast.parse(text)
    node = next(item for item in tree.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name == name)
    return "".join(text.splitlines(keepends=True)[node.lineno - 1:node.end_lineno])


def route_env() -> dict:
    return {
        "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
        "SORT4_R21_BODY_PHASE_ID": "SORT4-ACTUAL-SELECT-2026-10-23-R21",
        "LANE": "o26-sort4-body-r21",
        "CLOUD_BUILD_ID": "synthetic-build-id",
        "CLOUD_BUILD_PROJECT_ID": "synthetic-project",
    }


def active_test_profile() -> dict:
    profile = copy.deepcopy(PROFILE)
    profile["cloud_build_enabled"] = True
    return profile


class R21BodyTransportTests(unittest.TestCase):
    def test_profile_routes_only_new_lane_and_pins_all_transport_modules(self):
        self.assertEqual(ENTRY.ROUTED_PROFILE, PROFILE_PATH.name)
        self.assertEqual(RUNNER.ROUTED_PROFILE,
                         Path(ENTRY.HERE) / PROFILE_PATH.name)
        self.assertEqual(BODY.ROUTED_PROFILE,
                         Path(ENTRY.HERE) / PROFILE_PATH.name)
        self.assertEqual(ENTRY.EXECUTION_PHASE_ID, PROFILE["execution_authority_phase_id"])
        self.assertEqual(ENTRY.EXECUTION_LANE, PROFILE["execution_lane"])
        self.assertEqual(PROFILE["execution_authority_phase_id"],
                         "SORT4-ACTUAL-SELECT-2026-10-23-R21")
        self.assertEqual(PROFILE["execution_lane"], "o26-sort4-body-r21")
        for field, filename in (
                ("a1_entry_sha256", "a1-entry-r21.py"),
                ("a1_runner_sha256", "a1-runner-r21.py"),
                ("a1_actual_body_sha256", "a1-actual-body-r21.py"),
                ("a1_cleanup_helper_sha256", "a1-cleanup-helper.py"),
                ("a1_tool_sha256", "a1-tool-r21.py")):
            with self.subTest(pin=field):
                self.assertEqual(PROFILE[field], digest(HERE / filename))
        self.assertEqual(PROFILE["a1_tool_sha256"],
                         PROFILE["a1_helper_sha256"]["a1-tool-r21.py"])
        self.assertNotIn("a1_source_runner_sha256", PROFILE)
        self.assertNotIn("a1-tool-r17.py", PROFILE["a1_helper_sha256"])
        self.assertFalse(PROFILE["cloud_build_enabled"])
        self.assertEqual(PROFILE["status"], "TRANSPORT_INACTIVE")
        self.assertTrue(PROFILE["dispatch_blockers"])

    def test_r19_source_tool_model_and_annotation_bounds_are_preserved(self):
        changed = {
            "a1_actual_body_sha256", "a1_cleanup_helper_sha256", "a1_entry_sha256",
            "a1_runner_sha256", "a1_source_runner_sha256", "a1_tool_sha256",
            "a1_helper_sha256", "execution_authority_phase_id", "execution_lane",
            "transport_parent_profile_sha256", "candidate_version", "phase", "account", "task_id",
            "start_utc", "main_deadline_utc", "deadline_utc", "checkpoint_utc",
            "cloud_build_enabled", "status", "dispatch_blockers",
            "registration_rationale", "source_transport_scope", "session_preparation",
        }
        for key, value in R19_PROFILE.items():
            if key in changed:
                continue
            with self.subTest(profile_field=key):
                self.assertEqual(PROFILE[key], value)
        original_helpers = dict(R19_PROFILE["a1_helper_sha256"])
        r21_helpers = dict(PROFILE["a1_helper_sha256"])
        original_helpers.pop("a1-tool-r17.py")
        r21_helpers.pop("a1-tool-r21.py")
        self.assertEqual(r21_helpers, original_helpers)
        self.assertEqual(PROFILE["phase_id"], R19_PROFILE["phase_id"])
        self.assertEqual(PROFILE["authorization_phase_id"],
                         "SORT4-ACTUAL-C2-2026-10-21-R17")
        self.assertEqual(PROFILE["experiment_protocol_phase_id"],
                         "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17")
        self.assertEqual(PROFILE["transport_parent_profile_sha256"], digest(R19_PROFILE_PATH))

    def test_fresh_route_acceptance_and_execution_authority_refusals(self):
        profile = active_test_profile()
        env = route_env()
        ENTRY.require_execution_route(env, profile)
        RUNNER.require_runner_route(env, profile)
        BODY.require_body_route(env, profile)
        TOOL.require_r21_route(env, profile)
        # The old R17 authorization value is protocol metadata, not a dispatch credential.
        protocol_only = dict(env, SORT4_A1_AUTHORIZATION_PHASE_ID=
                             "SORT4-ACTUAL-C2-2026-10-21-R17")
        for gate in (ENTRY.require_execution_route,):
            gate(protocol_only, profile)
        self.assertNotIn("SORT4_A1_AUTHORIZATION_PHASE_ID", env)

        for key, bad in (
                ("SMALLSORT_EXECUTION_PROVIDER", "local"),
                ("SORT4_R21_BODY_PHASE_ID", "SORT4-ACTUAL-SELECT-2026-10-23-R20"),
                ("LANE", "o26-select-callee-r20"),
                ("CLOUD_BUILD_ID", ""),
                ("GITHUB_ACTIONS", "true")):
            candidate = dict(env, **{key: bad})
            for label, gate in (("entry", ENTRY.require_execution_route),
                                ("runner", RUNNER.require_runner_route),
                                ("body", BODY.require_body_route),
                                ("tool", TOOL.require_r21_route)):
                with self.subTest(env_key=key, gate=label), self.assertRaises(RuntimeError):
                    gate(candidate, profile)
        expired_only = {key: value for key, value in env.items()
                        if key != "SORT4_R21_BODY_PHASE_ID"}
        expired_only["SORT4_A1_AUTHORIZATION_PHASE_ID"] = \
            "SORT4-ACTUAL-C2-2026-10-21-R17"
        for gate in (ENTRY.require_execution_route, RUNNER.require_runner_route,
                     BODY.require_body_route, TOOL.require_r21_route):
            with self.subTest(gate=gate.__module__), self.assertRaises(RuntimeError):
                gate(expired_only, profile)

    def test_profiles_must_be_exact_new_route_and_active_before_use(self):
        env = route_env()
        profile = active_test_profile()
        mutations = (
            ("old-profile", R19_PROFILE),
            ("wrong-authority", profile | {"execution_authority_phase_id": "old"}),
            ("wrong-lane", profile | {"execution_lane": "o26-select-callee-r20"}),
            ("wrong-backend-auth", profile | {"authorization_phase_id": "old"}),
            ("wrong-backend-phase", profile | {"phase_id": "old"}),
            ("wrong-action", profile | {"body_action": "diagnostic-only"}),
            ("inactive", PROFILE),
        )
        gates = (ENTRY.require_execution_route, RUNNER.require_runner_route,
                 BODY.require_body_route, TOOL.require_r21_route)
        for label, candidate in mutations:
            for gate in gates:
                with self.subTest(profile=label, gate=gate.__module__), self.assertRaises(RuntimeError):
                    gate(env, candidate)

    def test_path_gate_refuses_outside_workspace(self):
        ENTRY.require_workspace_paths({"proof_root": Path("/workspace/proof")})
        with self.assertRaisesRegex(RuntimeError, "outside workspace"):
            ENTRY.require_workspace_paths({"proof_root": Path("/tmp/proof")})

    def test_full_body_contract_source_inventory_and_cleanup_import_are_retained(self):
        self.assertEqual(BODY.SOURCE_SHA, ORIGINAL_BODY.SOURCE_SHA)
        self.assertEqual(BODY.COUNTS, {
            b"is_less(": 5,
            b"hint::select_unpredictable(": 8,
            b"ptr::copy_nonoverlapping(": 4,
        })
        self.assertEqual(BODY.CONTRACT, ORIGINAL_BODY.CONTRACT)
        body_text = (HERE / "a1-actual-body-r21.py").read_text()
        self.assertIn("a1-cleanup-helper.py", body_text)
        self.assertIn("profile['a1_cleanup_helper_sha256']", body_text)
        self.assertIn("cleanup_helper.select_checked_cleanup_helper_lemma", body_text)
        self.assertNotIn("a1-runner.py", body_text)
        self.assertNotIn("a1_source_runner_sha256", body_text)
        original_body_defs = {node.name for node in ast.parse(
            (HERE / "a1-actual-body-r17.py").read_text()).body
            if isinstance(node, ast.FunctionDef)}
        for name in sorted(original_body_defs - {"run"}):
            with self.subTest(body_function=name):
                self.assertEqual(function_source(HERE / "a1-actual-body-r21.py", name),
                                 function_source(HERE / "a1-actual-body-r17.py", name))

    def test_tool_reconstruction_overlay_and_control_functions_remain_verbatim(self):
        excluded = {"require_r21_route", "run_focus_dead_code_scope_regression",
                    "cloud_gate"}
        original_tree = ast.parse((HERE / "a1-tool-r17.py").read_text())
        r21_tree = ast.parse((HERE / "a1-tool-r21.py").read_text())
        original_names = {node.name for node in original_tree.body
                          if isinstance(node, ast.FunctionDef)}
        r21_names = {node.name for node in r21_tree.body
                     if isinstance(node, ast.FunctionDef)}
        self.assertEqual(r21_names, original_names | {"require_r21_route"})
        for name in sorted(original_names - excluded):
            with self.subTest(tool_function=name):
                self.assertEqual(function_source(HERE / "a1-tool-r21.py", name),
                                 function_source(HERE / "a1-tool-r17.py", name))
        tool_text = (HERE / "a1-tool-r21.py").read_text()
        self.assertIn("SORT4_R21_BODY_PHASE_ID", tool_text)
        self.assertIn("SORT4_A1_PHASE_ID", tool_text)
        self.assertIn("SORT4_A1_AUTHORIZATION_PHASE_ID=AUTH", (HERE / "a1-actual-body-r21.py").read_text())
        self.assertIn("profile_path = Path(a.proof_root) / HERE / profile_name", tool_text)
        self.assertNotIn("A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json", tool_text)
        self.assertNotIn("a1-tool-r17.py", (HERE / "a1-actual-body-r21.py").read_text())


if __name__ == "__main__":
    unittest.main()
