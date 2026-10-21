"""Synthetic runner binding tests; no Cloud stages or verifier execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

runner = load("a1_redirect_runner_binding_test", "a1-runner.py")
matrix = load("a1_redirect_matrix_binding_test", "a1-matrix-classifier.py")


class GhostStrip:
    @staticmethod
    def strip_ghost(source):
        return source


class RedirectControlBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.package = self.root / "package"
        self.fixture = self.root / "fixture"
        self.package.mkdir()
        (self.fixture / "verified").mkdir(parents=True)
        (self.fixture / "original").mkdir()
        self.source = b"trait T { fn call(); }\n"
        (self.package / "P0c.rs").write_bytes(self.source)
        (self.fixture / "verified/lib.rs").write_bytes(self.source)
        (self.fixture / "original/lib.rs").write_bytes(self.source)
        self.cert_path = self.package / "source-certificate.json"
        self.cert_path.write_text("immutable certificate bytes\n", encoding="utf-8")
        self.case = {"source_file": "P0c.rs",
                     "source_id": "1" * 64, "unit_id": "2" * 64,
                     "generated_source_sha256": hashlib.sha256(self.source).hexdigest()}
        self.pair = {"verified": self.case["generated_source_sha256"],
                     "original": self.case["generated_source_sha256"]}
        self.raw = {"case_id": "P0c", "focus_case_id": "P0c",
                    "source_id": self.case["source_id"], "unit_id": self.case["unit_id"],
                    "source_certificate_sha256": runner._sha(self.cert_path),
                    "build_id": "test-build",
                    "source_pair_sha256": dict(self.pair),
                    "paired_support": {"paired_support_passed": True},
                    "artifacts": {"proof-ast.ml": {"sha256": None}},
                    "evidence_root": str(self.root / "focus"),
                    "stages": {"verification": {"classification": "TERMINAL", "exit": 2}}}
        (self.root / "focus").mkdir()
        self.log = self.root / "focus/verification.log"
        self.log.write_text(
            'Fatal error: exception Failure("SORT4-A1-CONTRACT: '
            'legacy clause-ignoring redirect attempted at common call")\n',
            encoding="utf-8")
        self.raw["stages"]["verification"]["log_sha256"] = runner._sha(self.log)
        self.control = {"SORT4_A1_FORCE_LEGACY_REDIRECT": "1",
                        "SORT4_A1_CHECKED_TRAIT_CONTRACT": "1",
                        "source_pair_sha256": self.case["generated_source_sha256"]}
        self.expected_control = dict(self.control)
        self.control_path = self.root / "redirect.json"
        self.write_control()
        self.control_sha = runner._sha(self.control_path)
        self.a1_env = {key: None for key in runner.A1_HELPER_ENV_KEYS}
        self.a1_env.update({"SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
                            "SORT4_A1_PHASE_ID": runner.PHASE,
                            "SORT4_A1_CHECKED_TRAIT_CONTRACT": "1",
                            "SORT4_A1_STAGE": "caller",
                            "SORT4_A1_PROFILE_SHA256": "3" * 64,
                            "SORT4_A1_FORCE_LEGACY_REDIRECT": "1",
                            "CLOUD_BUILD_ID": "test-build"})
        self.raw["checked_helper_proof"] = {
            "schema": "a1-checked-cleanup-helper-prerequisite-v1",
            "status": "HELPER_BODY_VERIFIED_SAME_BUILD", "case_id": "P0c",
            "proof_credit": False,
            "source_id": self.case["source_id"], "unit_id": self.case["unit_id"],
            "build_id": "test-build", "profile_sha256": "3" * 64,
            "source_certificate_sha256": runner._sha(self.cert_path),
            "source_pair_sha256": {"verified/lib.rs": self.pair["verified"],
                                    "original/lib.rs": self.pair["original"]},
            "environment_identity": {"caller_mode": "caller", "caller_a1": self.a1_env}}

    def write_control(self):
        self.control_path.write_text(json.dumps(self.control, sort_keys=True), encoding="utf-8")

    def bind(self, raw=None):
        return runner._source_case_input_identity(
            self.fixture, GhostStrip, certificate_path=self.cert_path,
            certificate_case=self.case, raw=self.raw if raw is None else raw)

    def redirect_class(self, raw=None, *, identity=True):
        return runner.classify_redirect_observation(
            self.raw if raw is None else raw,
            expected_source_sha256=self.case["generated_source_sha256"],
            expected_source_id=self.case["source_id"],
            expected_unit_id=self.case["unit_id"],
            expected_build_id="test-build",
            expected_evidence_root=self.root / "focus",
            input_identity_verified=identity)

    def matrix_observation(self, raw=None, *, control_doc=None, expected_control_sha=None):
        raw = self.raw if raw is None else raw
        bound = self.bind(raw)
        control_doc = (json.loads(self.control_path.read_text(encoding="utf-8"))
                       if control_doc is None else control_doc)
        expected_control_sha = self.control_sha if expected_control_sha is None else expected_control_sha
        control_identity = (
            expected_control_sha == self.control_sha and
            runner._sha(self.control_path) == expected_control_sha and
            control_doc == self.expected_control)
        env_identity = (bound is not None and
            runner._redirect_caller_environment_verified(
                raw, expected_source_id=self.case["source_id"],
                expected_unit_id=self.case["unit_id"],
                expected_certificate_sha256=runner._sha(self.cert_path),
                expected_source_pair=bound["source_pair_sha256"],
                expected_build_id="test-build", expected_profile_sha256="3" * 64))
        identity = bound is not None and control_identity and env_identity
        classified = self.redirect_class(raw, identity=identity)
        observation = {
            "proof_credit": False,
            "source_id": self.case["source_id"],
            "unit_id": self.case["unit_id"],
            "input_identity_verified": identity,
            "input_sha256": runner._sha(self.control_path),
            "classifier": classified,
        }
        expected = {"source_id": self.case["source_id"], "unit_id": self.case["unit_id"],
                    "control_input_sha256": expected_control_sha}
        return matrix.classify_case("N-clause-redirect", observation,
                                    expected_input=expected,
                                    run_pins={"tool_id": "a" * 64,
                                              "profile_id": "b" * 64,
                                              "proof_id": "c" * 40,
                                              "infra_id": "d" * 40,
                                              "target_id": "R14-TEST"},
                                    build_id="test-build", expected_inventory={})

    def test_real_producer_shaped_pre_ast_partial_binds_and_reaches_matrix_gate(self):
        partial_identity = self.bind()
        self.assertIsNotNone(partial_identity)
        partial = {"classification": "INCONCLUSIVE_CURRENT_STAGE", "case_id": "P0c",
                   "raw": self.raw, "structure": None, "proof_credit": False,
                   "observed_input_ids": partial_identity["input_ids"],
                   "observed_input_sha256": partial_identity["source_pair_sha256"],
                   "source_identity_verified": True}
        self.assertIsNone(partial["raw"]["artifacts"]["proof-ast.ml"]["sha256"])
        self.assertEqual(self.redirect_class(partial["raw"])["classification"],
                         "LEGACY_REDIRECT_REFUSAL_OBSERVED")
        result = self.matrix_observation(partial["raw"])
        self.assertTrue(result["matrix_gate_passed"], result)
        self.assertFalse(result["record"]["proof_credit"])

    def test_source_pair_ids_certificate_and_current_bytes_fail_closed(self):
        mutations = []
        for key, value in (("source_id", None), ("unit_id", "0" * 64),
                           ("source_certificate_sha256", None),
                           ("source_pair_sha256", {"verified": "0" * 64,
                                                    "original": self.pair["original"]}),
                           ("source_pair_sha256", {"verified": self.pair["verified"],
                                                    "original": self.pair["original"],
                                                    "extra": "x"})):
            bad = dict(self.raw); bad[key] = value
            mutations.append((key, bad))
        for name, bad in mutations:
            with self.subTest(name=name):
                self.assertIsNone(self.bind(bad))
                self.assertFalse(self.matrix_observation(bad)["matrix_gate_passed"])
        (self.fixture / "verified/lib.rs").write_bytes(self.source + b"// stale\n")
        self.assertIsNone(self.bind())
        self.assertFalse(self.matrix_observation()["matrix_gate_passed"])

    def test_certified_source_package_and_original_copy_are_current(self):
        (self.package / "P0c.rs").write_bytes(self.source + b"// package drift\n")
        self.assertIsNone(self.bind())
        (self.package / "P0c.rs").write_bytes(self.source)
        (self.fixture / "original/lib.rs").write_bytes(self.source + b"// original drift\n")
        self.assertIsNone(self.bind())

    def test_control_file_identity_fail_closed(self):
        self.control["SORT4_A1_FORCE_LEGACY_REDIRECT"] = "0"
        self.write_control()
        self.assertFalse(self.matrix_observation()["matrix_gate_passed"])

    def test_environment_source_binding_is_required(self):
        bad = dict(self.raw)
        bad["checked_helper_proof"] = dict(self.raw["checked_helper_proof"])
        bad["checked_helper_proof"]["environment_identity"] = {
            "caller_mode": "caller", "caller_a1": dict(self.a1_env,
                SORT4_A1_FORCE_LEGACY_REDIRECT=None)}
        self.assertFalse(self.matrix_observation(bad)["matrix_gate_passed"])
        self.assertNotEqual(self.redirect_class(bad, identity=False)["classification"],
                            "LEGACY_REDIRECT_REFUSAL_OBSERVED")

    def test_terminal_exit_log_and_first_diagnostic_are_exact(self):
        mutations = []
        for stage in ({"classification": "SETUP_FAILURE", "exit": 2,
                       "log_sha256": runner._sha(self.log)},
                      {"classification": "TERMINAL", "exit": 124,
                       "log_sha256": runner._sha(self.log)},
                      {"classification": "TERMINAL", "exit": True,
                       "log_sha256": runner._sha(self.log)},
                      {"classification": "TERMINAL", "exit": 2,
                       "log_sha256": "0" * 64}):
            bad = dict(self.raw)
            bad["stages"] = {"verification": stage}
            mutations.append(bad)
        for bad in mutations:
            self.assertNotEqual(self.redirect_class(bad)["classification"],
                                "LEGACY_REDIRECT_REFUSAL_OBSERVED")
            self.assertFalse(self.matrix_observation(bad)["matrix_gate_passed"])
        self.log.write_text("Fatal error: unrelated setup failure\n" +
            'Fatal error: exception Failure("SORT4-A1-CONTRACT: '
            'legacy clause-ignoring redirect attempted at common call")\n', encoding="utf-8")
        self.raw["stages"]["verification"]["log_sha256"] = runner._sha(self.log)
        self.assertNotEqual(self.redirect_class()["classification"],
                            "LEGACY_REDIRECT_REFUSAL_OBSERVED")
        self.assertFalse(self.matrix_observation()["matrix_gate_passed"])

    def test_missing_or_wrong_evidence_path_fails_closed(self):
        for stage in ({"verification": None}, {},
                      {"verification": {"classification": None, "exit": 2,
                                         "log_sha256": runner._sha(self.log)}}):
            bad = dict(self.raw)
            bad["stages"] = stage
            self.assertNotEqual(self.redirect_class(bad)["classification"],
                                "LEGACY_REDIRECT_REFUSAL_OBSERVED")
        bad = dict(self.raw)
        bad["evidence_root"] = str(self.root / "other")
        self.assertNotEqual(self.redirect_class(bad)["classification"],
                            "LEGACY_REDIRECT_REFUSAL_OBSERVED")
        self.log.unlink()
        self.assertNotEqual(self.redirect_class()["classification"],
                            "LEGACY_REDIRECT_REFUSAL_OBSERVED")


if __name__ == "__main__":
    unittest.main()
