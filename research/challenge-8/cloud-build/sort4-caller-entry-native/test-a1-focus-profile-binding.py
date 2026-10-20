#!/usr/bin/env python3
"""Pure synthetic tests for the focused backend's profile authorization map."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "a1-focus-backend.py"
PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
R6 = "SORT4-PACKAGE-SCOPE-NATIVE-PROOF-2026-10-20-R6"
R7 = "SORT4-PACKAGING-NATIVE-PROOF-2026-10-20-R7"
R8 = "SORT4-POST-MIGRATION-NATIVE-PROOF-2026-10-20-R8"
R9 = "SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9"
PROFILE_NAMES = {
    R6: "A1-SCOPE-S3-PROFILE-2026-10-20.json",
    R7: "A1-PACKAGING-R7-PROFILE-2026-10-20.json",
    R8: "A1-POST-MIGRATION-R8-PROFILE-2026-10-20.json",
    R9: "A1-NATIVE-INTERFACE-R9-PROFILE-2026-10-20.json",
}


def load_backend():
    spec = importlib.util.spec_from_file_location(
        "isolated_a1_focus_backend", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load focused backend")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FocusProfileBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="a1-focus-profile-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.backend = load_backend()
        self.profile_dir = self.root / self.backend.HERE
        self.profile_dir.mkdir(parents=True)
        self.profiles = {phase: self.make_profile(phase) for phase in (R6, R7, R8, R9)}
        self.write_all_profiles()

    @staticmethod
    def make_profile(authorization):
        return {
            "authorization_phase_id": authorization,
            "phase_id": PHASE,
            "experiment_protocol_phase_id": PHASE,
            "profile_pin_source": "coordinator-environment",
            "proof_sha": None,
            "infra_sha": None,
            "cloud_build_enabled": True,
            "profile_accepted": False,
            "synthetic_identity": authorization,
        }

    def profile_path(self, authorization):
        return self.profile_dir / PROFILE_NAMES[authorization]

    def write_profile(self, authorization, raw=None):
        path = self.profile_path(authorization)
        if raw is None:
            raw = (json.dumps(self.profiles[authorization], sort_keys=True) + "\n").encode()
        path.write_bytes(raw)
        return path

    def write_all_profiles(self):
        for authorization in (R6, R7, R8, R9):
            self.write_profile(authorization)

    def env_for(self, authorization, profile=None):
        path = self.profile_path(authorization)
        if profile is None:
            profile = self.profiles[authorization]
        return {
            "SORT4_A1_AUTHORIZATION_PHASE_ID": authorization,
            "SORT4_A1_PHASE_ID": PHASE,
            "SORT4_A1_PROFILE_SHA256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    def validate(self, authorization, profile=None, env=None):
        if profile is None:
            profile = self.profiles[authorization]
        if env is None:
            env = self.env_for(authorization, profile)
        return self.backend.validate_profile_binding(self.root, profile, env)

    def test_exact_r6_r7_r8_and_r9_bindings_select_their_canonical_profiles(self):
        for authorization in (R6, R7, R8, R9):
            with self.subTest(authorization=authorization):
                self.assertEqual(self.validate(authorization),
                                 self.profile_path(authorization))

    def test_historical_r7_profile_pins_remain_recorded(self):
        repo_root = HERE.parents[3]
        profile_path = HERE / PROFILE_NAMES[R7]
        profile = json.loads(profile_path.read_text())
        env = {
            "SORT4_A1_AUTHORIZATION_PHASE_ID": R7,
            "SORT4_A1_PHASE_ID": PHASE,
            "SORT4_A1_PROFILE_SHA256": hashlib.sha256(
                profile_path.read_bytes()).hexdigest(),
        }

        # Exercise the pure active-consumer validator against the real published
        # R7 profile, then check its transport recipe and byte pins. No gate,
        # compiler, extractor, or runner preparation is invoked here.
        self.assertEqual(
            self.backend.validate_profile_binding(repo_root, profile, env),
            profile_path,
        )
        recipe_path = repo_root / "research/challenge-8/cloud-build/recipes/o26-sort4-c1-current-recovery.json"
        recipe = json.loads(recipe_path.read_text())
        proof_paths = set(recipe["proof_paths"])
        infra_paths = set(recipe["infra_paths"])
        canonical = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
        profile_rel = canonical + PROFILE_NAMES[R7]
        entry_rel = canonical + "a1-entry-r7.py"
        runner_rel = canonical + "a1-runner-r7.py"
        core_rel = canonical + "a1-runner.py"
        helper_rel = canonical + "a1-focus-backend.py"
        self.assertIn(profile_rel, proof_paths)
        self.assertIn(entry_rel, infra_paths)
        self.assertIn(runner_rel, infra_paths)
        self.assertIn(core_rel, proof_paths)

        file_pins = {
            "a1_entry_sha256": entry_rel,
            "a1_runner_sha256": runner_rel,
            "a1_source_runner_sha256": core_rel,
        }
        for key, relpath in file_pins.items():
            with self.subTest(pin=key):
                if key == "a1_source_runner_sha256":
                    # Frozen historical identity; active R9 core is checked below.
                    actual = "f635fb5026e0f5a88b54366c155b8dc94eaa837200fa957b4641b1c5074a90bb"
                else:
                    actual = hashlib.sha256((repo_root / relpath).read_bytes()).hexdigest()
                self.assertEqual(profile[key], actual)
        release = json.loads((HERE / "A1-PACKAGING-R7-S2-RELEASE-2026-10-20.json").read_text())
        self.assertEqual(profile["a1_helper_sha256"]["a1-focus-backend.py"],
                         release["helper_pins"]["a1-focus-backend.py"])
        self.assertNotEqual(profile["a1_helper_sha256"]["a1-focus-backend.py"],
                            hashlib.sha256((repo_root / helper_rel).read_bytes()).hexdigest())

    def test_published_r8_profile_is_connected_to_current_transport_and_files(self):
        repo_root = HERE.parents[3]
        profile_path = HERE / PROFILE_NAMES[R8]
        profile = json.loads(profile_path.read_text())
        env = {
            "SORT4_A1_AUTHORIZATION_PHASE_ID": R8,
            "SORT4_A1_PHASE_ID": PHASE,
            "SORT4_A1_PROFILE_SHA256": hashlib.sha256(
                profile_path.read_bytes()).hexdigest(),
        }
        self.assertEqual(
            self.backend.validate_profile_binding(repo_root, profile, env),
            profile_path,
        )
        recipe_path = repo_root / "research/challenge-8/cloud-build/recipes/o26-sort4-c1-current-recovery.json"
        recipe = json.loads(recipe_path.read_text())
        proof_paths = set(recipe["proof_paths"])
        infra_paths = set(recipe["infra_paths"])
        canonical = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
        profile_rel = canonical + PROFILE_NAMES[R8]
        entry_rel = canonical + "a1-entry-r8.py"
        runner_rel = canonical + "a1-runner-r8.py"
        core_rel = canonical + "a1-runner.py"
        helper_rel = canonical + "a1-focus-backend.py"
        self.assertIn(profile_rel, proof_paths)
        self.assertIn(
            "research/challenge-8/cloud-build/sort4-native-c1-bound/"
            "NATIVE-RUST-FOCUS-DEAD-CODE-SCOPE-MANIFEST.json", proof_paths)
        self.assertIn(
            "research/challenge-8/cloud-build/sort4-native-c1-bound/"
            "native-rust-focus-dead-code-scope.patch", proof_paths)
        self.assertIn(entry_rel, infra_paths)
        self.assertIn(runner_rel, infra_paths)
        self.assertIn(core_rel, proof_paths)
        for key, relpath in {
            "a1_entry_sha256": entry_rel,
            "a1_runner_sha256": runner_rel,
        }.items():
            with self.subTest(pin=key):
                self.assertEqual(profile[key], hashlib.sha256(
                    (repo_root / relpath).read_bytes()).hexdigest())
        # R8 remains a historical profile. Its focus helper pin must remain
        # recorded even though the active helper now also registers R9.
        self.assertRegex(profile["a1_helper_sha256"]["a1-focus-backend.py"],
                         r"\A[0-9a-f]{64}\Z")
        self.assertNotEqual(
            profile["a1_helper_sha256"]["a1-focus-backend.py"],
            hashlib.sha256((repo_root / helper_rel).read_bytes()).hexdigest(),
        )
        r7_profile = json.loads(
            (HERE / "A1-PACKAGING-R7-PROFILE-2026-10-20.json").read_text())
        # Preserve historical pins rather than reconstructing them from the
        # advancing active R9 source. R9 below remains byte-bound to live files.
        self.assertEqual(profile["a1_source_runner_sha256"],
                         "776ccb08bdbc547c609549d126439f36477b964e830de10cfc203a1dcef90435")
        self.assertEqual(profile["first_matrix_cases"],
                         r7_profile["first_matrix_cases"])
        for key in ("compiler_commit", "compiler_toolchain", "target",
                    "std_source_sha256", "tool_head", "kernel_sha256",
                    "r_patch_sha256", "c_patch_sha256",
                    "pointer_width", "execution_mode"):
            with self.subTest(semantic_input=key):
                self.assertEqual(profile[key], r7_profile[key])
        native = dict(profile["native_interface_reference"])
        native["translator_sha256"] = r7_profile["native_interface_reference"]["translator_sha256"]
        self.assertEqual(native, r7_profile["native_interface_reference"])
        # R8 is a frozen historical profile. The active source overlay advances
        # under R9, so preserve and check its recorded R8 pins here; the R9 test
        # below binds the current patch, manifest, and source transitions.
        self.assertEqual(profile["native_signature_manifest_sha256"],
                         "4b1c5b3a51c5ecb10b8dc2445bfb98bfce615146c46ca872ef8d0793a0d177f2")
        self.assertEqual(profile["native_signature_patch_sha256"],
                         "89ad6a9dbe8501167c435e40250f1ad0757cd362342a1db6047b7297b3d27e77")
        self.assertEqual(
            profile["native_interface_reference"]["translator_sha256"],
            "4be0d553bc99ee638ef173f2d6b48d9f2ef6ed6bb3245d6b3cf032afbb86d799")
        for name in ("NATIVE-SMALL-SORT-IMPL-SIGNATURE-MANIFEST.json", "native-small-sort-impl-signature.patch"):
            self.assertIn("research/challenge-8/cloud-build/sort4-caller-entry-native/" + name, proof_paths)
        lane_script = (repo_root / "research/challenge-8/cloud-build/run-sort4-c1-current-recovery.sh").read_text()
        self.assertIn("a1-entry-r8.py", lane_script)
        self.assertIn(R8, lane_script)

    def test_published_r9_profile_is_connected_to_current_transport_and_files(self):
        repo_root = HERE.parents[3]
        profile_path = HERE / PROFILE_NAMES[R9]
        profile = json.loads(profile_path.read_text())
        env = {
            "SORT4_A1_AUTHORIZATION_PHASE_ID": R9,
            "SORT4_A1_PHASE_ID": PHASE,
            "SORT4_A1_PROFILE_SHA256": hashlib.sha256(
                profile_path.read_bytes()).hexdigest(),
        }
        self.assertEqual(
            self.backend.validate_profile_binding(repo_root, profile, env),
            profile_path,
        )
        recipe_path = repo_root / "research/challenge-8/cloud-build/recipes/o26-sort4-c1-current-recovery.json"
        recipe = json.loads(recipe_path.read_text())
        proof_paths = set(recipe["proof_paths"])
        infra_paths = set(recipe["infra_paths"])
        canonical = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
        profile_rel = canonical + PROFILE_NAMES[R9]
        entry_rel = canonical + "a1-entry-r9.py"
        runner_rel = canonical + "a1-runner-r9.py"
        core_rel = canonical + "a1-runner.py"
        helper_rel = canonical + "a1-focus-backend.py"
        self.assertIn(profile_rel, proof_paths)
        self.assertIn(entry_rel, infra_paths)
        self.assertIn(runner_rel, infra_paths)
        self.assertIn(core_rel, proof_paths)
        for key, relpath in {
            "a1_entry_sha256": entry_rel,
            "a1_runner_sha256": runner_rel,
            "a1_source_runner_sha256": core_rel,
        }.items():
            with self.subTest(pin=key):
                self.assertEqual(profile[key], hashlib.sha256(
                    (repo_root / relpath).read_bytes()).hexdigest())
        for name, relpath in (("a1-focus-backend.py", helper_rel),
                               ("a1-tool.py", canonical + "a1-tool.py")):
            self.assertEqual(profile["a1_helper_sha256"][name],
                             hashlib.sha256((repo_root / relpath).read_bytes()).hexdigest())
        lane_script = (repo_root / "research/challenge-8/cloud-build/run-sort4-c1-current-recovery.sh").read_text()
        self.assertIn("a1-entry-r9.py", lane_script)
        self.assertIn(R9, lane_script)
        self.assertIn(profile_rel, proof_paths)
        self.assertIn("A1_R9_PHASE", (repo_root / "research/challenge-8/cloud-build/control.py").read_text())
        signature_manifest_path = HERE / "NATIVE-SMALL-SORT-IMPL-SIGNATURE-MANIFEST.json"
        signature_manifest = json.loads(signature_manifest_path.read_text())
        translator = "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
        transition = signature_manifest["files"][translator]
        self.assertEqual(signature_manifest["phase_id"], R9)
        self.assertEqual(profile["native_signature_manifest_sha256"],
                         hashlib.sha256(signature_manifest_path.read_bytes()).hexdigest())
        self.assertEqual(profile["native_signature_patch_sha256"],
                         hashlib.sha256((HERE / "native-small-sort-impl-signature.patch").read_bytes()).hexdigest())
        self.assertEqual(transition["base_sha256"], profile["r_representation_after"][translator])
        self.assertEqual(transition["result_sha256"], profile["r_after"][translator])
        self.assertEqual(profile["native_interface_reference"]["translator_sha256"], transition["result_sha256"])
        self.assertEqual(profile["c_before"], profile["r_after"])
        self.assertEqual(profile["c_after"][translator], transition["after_unchanged_c_patch_sha256"])

    def test_rejects_unknown_or_cross_paired_authorization(self):
        for authorization in (
                "SORT4-UNKNOWN-R8",
                "SORT4-MAYBEUNINIT-UNION-KIND-2026-10-20-R4"):
            with self.subTest(authorization=authorization):
                unknown = {**self.env_for(R7),
                           "SORT4_A1_AUTHORIZATION_PHASE_ID": authorization}
                with self.assertRaisesRegex(RuntimeError, "unknown A1 authorization"):
                    self.validate(R7, self.profiles[R7], unknown)
        for authorization in (None, [], {"old": R6}):
            with self.subTest(authorization=authorization):
                unknown = {**self.env_for(R7),
                           "SORT4_A1_AUTHORIZATION_PHASE_ID": authorization}
                with self.assertRaisesRegex(RuntimeError, "unknown A1 authorization"):
                    self.validate(R7, self.profiles[R7], unknown)
        with self.assertRaisesRegex(RuntimeError, "decoded profile identity"):
            self.validate(R6, self.profiles[R7], self.env_for(R6))
        with self.assertRaisesRegex(RuntimeError, "decoded profile identity"):
            self.validate(R7, self.profiles[R6], self.env_for(R7))

    def test_rejects_missing_wrong_or_malformed_profile_sha(self):
        env = self.env_for(R7)
        for value in (None, "", "0" * 64, "not-a-sha"):
            with self.subTest(profile_sha=value):
                candidate = dict(env)
                if value is None:
                    candidate.pop("SORT4_A1_PROFILE_SHA256")
                else:
                    candidate["SORT4_A1_PROFILE_SHA256"] = value
                with self.assertRaisesRegex(RuntimeError, "profile file SHA"):
                    self.validate(R7, self.profiles[R7], candidate)

    def test_rejects_missing_or_cross_paired_profile_path(self):
        env = self.env_for(R7)
        self.profile_path(R7).unlink()
        with self.assertRaisesRegex(RuntimeError, "profile file SHA"):
            self.validate(R7, self.profiles[R7], env)
        self.write_profile(R7, self.profile_path(R6).read_bytes())
        candidate = self.env_for(R7)
        with self.assertRaisesRegex(RuntimeError, "decoded profile identity"):
            self.validate(R7, self.profiles[R7], candidate)

    def test_rejects_bad_phase_protocol_and_acceptance_metadata(self):
        invalid = (
            ("environment-phase", {}, {"SORT4_A1_PHASE_ID": "SORT4-OTHER-PHASE"}),
            ("profile-phase", {"phase_id": None}, {}),
            ("protocol", {"experiment_protocol_phase_id": None}, {}),
            ("authorization", {"authorization_phase_id": None}, {}),
            ("pin-source", {"profile_pin_source": "local"}, {}),
            ("proof-sha", {"proof_sha": "unexpected"}, {}),
            ("infra-sha", {"infra_sha": "unexpected"}, {}),
            ("cloud-enabled", {"cloud_build_enabled": "true"}, {}),
            ("profile-accepted", {"profile_accepted": True}, {}),
        )
        for label, profile_changes, env_changes in invalid:
            with self.subTest(label=label):
                profile = dict(self.profiles[R7])
                profile.update(profile_changes)
                self.write_profile(
                    R7, (json.dumps(profile, sort_keys=True) + "\n").encode())
                env = self.env_for(R7, profile)
                env.update(env_changes)
                with self.assertRaisesRegex(RuntimeError, "profile identity"):
                    self.validate(R7, profile, env)

    def test_rejects_non_object_and_malformed_json(self):
        with self.assertRaisesRegex(RuntimeError, "profile must be an object"):
            self.backend.validate_profile_binding(
                self.root, None, self.env_for(R7))
        with self.assertRaisesRegex(RuntimeError, "profile must be an object"):
            self.validate(R7, [], self.env_for(R7))
        path = self.write_profile(R7, b"not-json\n")
        env = self.env_for(R7)
        env["SORT4_A1_PROFILE_SHA256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(RuntimeError, "profile JSON"):
            self.validate(R7, self.profiles[R7], env)


if __name__ == "__main__":
    unittest.main(verbosity=2)
