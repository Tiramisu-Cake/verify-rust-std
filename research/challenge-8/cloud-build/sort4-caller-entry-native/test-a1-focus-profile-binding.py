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
R10 = "SORT4-DELIVERABLE-NATIVE-PROOF-2026-10-20-R10"
R11 = "SORT4-CHECKED-CALLER-NATIVE-PROOF-2026-10-21-R11"
PROFILE_NAMES = {
    R6: "A1-SCOPE-S3-PROFILE-2026-10-20.json",
    R7: "A1-PACKAGING-R7-PROFILE-2026-10-20.json",
    R8: "A1-POST-MIGRATION-R8-PROFILE-2026-10-20.json",
    R9: "A1-NATIVE-INTERFACE-R9-PROFILE-2026-10-20.json",
    R10: "A1-DELIVERABLE-NATIVE-R10-PROFILE-2026-10-20.json",
    R11: "A1-CHECKED-CALLER-R11-PROFILE-2026-10-21.json",
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
        self.profiles = {phase: self.make_profile(phase) for phase in (R6, R7, R8, R9, R10, R11)}
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
        for authorization in (R6, R7, R8, R9, R10, R11):
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

    def test_exact_r6_r7_r8_r9_and_r10_bindings_select_their_canonical_profiles(self):
        for authorization in (R6, R7, R8, R9, R10, R11):
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
        }.items():
            with self.subTest(pin=key):
                self.assertEqual(profile[key], hashlib.sha256(
                    (repo_root / relpath).read_bytes()).hexdigest())
        self.assertEqual(profile["a1_source_runner_sha256"],
                         "a45c9c74b8f63354f6342a3f00e317e2eca980a44fe4a2715fc2e242d88ba555")
        self.assertEqual(hashlib.sha256(profile_path.read_bytes()).hexdigest(),
                         "a1be5bef10b27946185df84cf6b8fb7fde4417c05cf4bc08d0f75de1c8462f97")
        historically_advanced = {
            "a1-fixtures.py": "6d2cd0956ed5d9821be1dd32f731f201e5aea52ae4f06a676d8dfc5c17355d25",
            "a1-ast-gates.py":
                "917d51a52d9383beb56f52ff22415e62f81ee60a2a8a16ae40e08c17b36c2c58",
            "a1-compiler-inventory.py":
                "6394ec909e6d6a7e77988279c382d531d61b10c7ca02e23672291c4622fe95e5",
            "a1-focus-backend.py":
                "6e3d5303500c0601dc4fc886bcdaaf78c911147d4fa90bc5eab2b768dc0d0a82",
            "a1-tool.py":
                "eafe5058e0369c77205d62a0cd46ffe5ca564f2902b3a1b8371f1fcbc559e7b1",
        }
        for name, expected in profile["a1_helper_sha256"].items():
            with self.subTest(historical_r9_helper=name):
                self.assertRegex(expected, r"\A[0-9a-f]{64}\Z")
                if name in historically_advanced:
                    self.assertEqual(expected, historically_advanced[name])
                    self.assertNotEqual(expected, hashlib.sha256(
                        (HERE / name).read_bytes()).hexdigest())
                else:
                    self.assertEqual(expected, hashlib.sha256(
                        (HERE / name).read_bytes()).hexdigest())
        lane_script = (repo_root / "research/challenge-8/cloud-build/run-sort4-c1-current-recovery.sh").read_text()
        self.assertIn("a1-entry-r9.py", lane_script)
        self.assertIn(R9, lane_script)
        self.assertIn(profile_rel, proof_paths)
        self.assertIn("A1_R9_PHASE", (repo_root / "research/challenge-8/cloud-build/control.py").read_text())
        # Historical R9 source pins stay frozen as the active R10 overlay advances.
        self.assertEqual(profile["native_signature_manifest_sha256"],
                         "29b0bcc0b28034fdcf8997dddc07bc3b0365fbf074b6be096d07cdbc802eadb9")
        self.assertEqual(profile["native_signature_patch_sha256"],
                         "1c56d36e1feeb52112c4da0eb90c5985b548db7c4f836bb6971d1a826effd2a2")

    def test_published_r11_profile_is_bound_to_current_registration_closure(self):
        repo_root = HERE.parents[3]
        profile_path = HERE / PROFILE_NAMES[R11]
        profile = json.loads(profile_path.read_text())
        env = {
            "SORT4_A1_AUTHORIZATION_PHASE_ID": R11,
            "SORT4_A1_PHASE_ID": PHASE,
            "SORT4_A1_PROFILE_SHA256": hashlib.sha256(profile_path.read_bytes()).hexdigest(),
        }
        self.assertEqual(self.backend.validate_profile_binding(repo_root, profile, env), profile_path)
        recipe = json.loads((repo_root / "research/challenge-8/cloud-build/recipes/o26-sort4-c1-current-recovery.json").read_text())
        canonical = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
        profile_rel = canonical + PROFILE_NAMES[R11]
        entry_rel = canonical + "a1-entry-r11.py"
        runner_rel = canonical + "a1-runner-r11.py"
        core_rel = canonical + "a1-runner.py"
        self.assertEqual(recipe["entrypoint"], "research/challenge-8/cloud-build/run-o26-sort4-c1-current-recovery.sh")
        self.assertIn(profile_rel, recipe["proof_paths"])
        self.assertIn(entry_rel, recipe["infra_paths"])
        self.assertIn(runner_rel, recipe["infra_paths"])
        self.assertIn(core_rel, recipe["proof_paths"])
        for pin, rel in (("a1_entry_sha256", entry_rel), ("a1_runner_sha256", runner_rel),
                         ("a1_source_runner_sha256", core_rel)):
            with self.subTest(pin=pin):
                self.assertEqual(profile[pin], hashlib.sha256((repo_root / rel).read_bytes()).hexdigest())
        for name, expected in profile["a1_helper_sha256"].items():
            with self.subTest(helper=name):
                self.assertEqual(expected, hashlib.sha256((HERE / name).read_bytes()).hexdigest())
        self.assertEqual(profile["authorization_phase_id"], R11)
        self.assertEqual(profile["phase_id"], PHASE)
        self.assertEqual(profile["experiment_protocol_phase_id"], PHASE)
        self.assertEqual(profile["maximum_build_timeout_seconds"], 1200)
        self.assertEqual(profile["proof_credit"], False)
        self.assertEqual(profile["profile_accepted"], False)
        tool_spec = importlib.util.spec_from_file_location(
            "isolated_a1_tool_profile_registry", HERE / "a1-tool.py")
        self.assertIsNotNone(tool_spec)
        self.assertIsNotNone(tool_spec.loader)
        tool = importlib.util.module_from_spec(tool_spec)
        tool_spec.loader.exec_module(tool)
        self.assertEqual(tool.FOCUS_PROFILE_NAMES[R11], PROFILE_NAMES[R11])
        lane_script = (repo_root / "research/challenge-8/cloud-build/run-sort4-c1-current-recovery.sh").read_text()
        self.assertIn("a1-entry-r11.py", lane_script)
        self.assertIn(R11, lane_script)
        control = (repo_root / "research/challenge-8/cloud-build/control.py").read_text()
        self.assertIn("A1_R11_PHASE", control)

        signature_manifest_path = HERE / "NATIVE-SMALL-SORT-IMPL-SIGNATURE-MANIFEST.json"
        signature_manifest = json.loads(signature_manifest_path.read_text())
        translator = "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
        transition = signature_manifest["files"][translator]
        self.assertEqual(signature_manifest["phase_id"], R10)
        self.assertEqual(profile["native_signature_manifest_sha256"],
                         hashlib.sha256(signature_manifest_path.read_bytes()).hexdigest())
        self.assertEqual(profile["native_signature_patch_sha256"],
                         hashlib.sha256((HERE / "native-small-sort-impl-signature.patch").read_bytes()).hexdigest())
        self.assertEqual(transition["base_sha256"], profile["r_representation_after"][translator])
        self.assertEqual(transition["result_sha256"], profile["r_after"][translator])
        self.assertEqual(profile["native_interface_reference"]["translator_sha256"], transition["result_sha256"])
        self.assertEqual(profile["c_before"], profile["r_after"])
        # R11 adds a checked-helper command stage after the historical R10 C
        # overlay. The immutable native-signature manifest still describes R10.
        self.assertEqual(profile["c_patch_sha256"], hashlib.sha256(
            (HERE / "checked-threshold-contract.patch").read_bytes()).hexdigest())
        self.assertEqual(profile["c_after"][translator],
                         "9f065ebe4937cc08383ccd8791e956558202a5ab7a045f0bef74d229234a4a71")

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
