#!/usr/bin/env python3
"""Synthetic service tests for run-cloud.py; no Cloud or VeriFast execution."""
import importlib.util
import json
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("n13_run_cloud_tested", HERE / "run-cloud.py")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

PAIR13 = [(i, i + 1) for i in range(45)]
LINES13 = list(range(10, 55))
PAIR9 = [(i, i + 1) for i in range(25)]
LINES9 = list(range(100, 125))
CLOUD = {
    "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
    "CLOUD_BUILD_ID": "synthetic-cloud-build",
    "CLOUD_BUILD_PROJECT_ID": "smallsort-ci",
    "CLOUD_BUILD_REGION": "global",
    "NETWORK_PROFILE_SHA256": "a" * 64,
}


class FakeRanks:
    composition_calls = []

    @staticmethod
    def generic_bridge():
        return "generic bridge source"

    @staticmethod
    def domain13_members():
        return "domain13 member source"

    @staticmethod
    def composition(n, pairs, exact=True):
        FakeRanks.composition_calls.append((n, exact))
        return f"composition {n} exact={exact} pairs={len(pairs)}"

    @staticmethod
    def negative_missing_equiv_trans():
        return "missing equivalence transitivity source", {
            "expected_predicate": "false", "target_line": 8,
            "expected_bodies": ["negative_missing_equiv_trans"],
        }

    @staticmethod
    def negative_exact_post(kind, pairs):
        return f"negative exact {kind} {len(pairs)}", {
            "expected_predicate": "false", "target_line": 19,
            "expected_bodies": ["network13_finite_swo_order", f"negative_exact_{kind}"],
        }


class FakeProve:
    TIMEOUT_SECONDS = 180

    @staticmethod
    def extract(n):
        return (PAIR13, LINES13) if n == 13 else (PAIR9, LINES9)


def fake_result(spec, sha, log_sha, log_path, result_overrides=None):
    negative = spec["negative"]
    bodies = negative.get("expected_bodies", ["positive_body"]) if negative else ["positive_body"]
    result = {
        "case": spec["name"],
        "negative": negative,
        "exit": 1 if negative else 0,
        "source_sha256": sha,
        "log_sha256": log_sha,
        "log": str(log_path),
        "source_unchanged": True,
        "accepted": True,
        "expected_bodies": bodies,
        "visited_bodies": list(bodies),
        "errors": ["expected assertion error"] if negative else [],
        "leak_checks": len(bodies),
        "return_checks": len(bodies),
    }
    if negative:
        result["classifier_rejection_controls"] = {
            "other_line": True, "other_predicate": True, "no_body_execution": True,
            "no_target_execution": True, "other_column": True, "timeout": True,
            "source_changed": True,
        }
    if result_overrides:
        result.update(result_overrides)
    return result


class RunCloudTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.profile_path = self.root / runner.PROFILE_RELATIVE
        self.profile_path.parent.mkdir(parents=True)
        self.tool_home = self.root / "tool"
        (self.tool_home / "bin").mkdir(parents=True)
        (self.tool_home / "bin/verifast").write_bytes(b"synthetic console")
        self.mode = "success"
        self.generated = []
        self.profile = {}
        FakeRanks.composition_calls.clear()

        def run_case(tool, evidence, name, source, negative=None):
            case = {"name": name, "source": source, "negative": negative}
            self.generated.append(case)
            spec = {"name": name, "negative": negative}
            source_sha = runner.digest(source.encode())
            source_path = evidence / f"{name}.c"
            log_path = evidence / f"{name}.log"
            source_path.write_text(source)
            log_path.write_text("synthetic verifier log")
            log_sha = runner.digest(log_path.read_bytes())
            if self.mode == "timeout":
                log_path.write_text("partial verifier output")
                raise TimeoutError("synthetic verifier timeout")
            if self.mode == "error-exit":
                return fake_result(spec, source_sha, log_sha, log_path,
                                   {"exit": 1, "accepted": False, "errors": ["verifier error"]})
            if self.mode == "missing":
                return {"exit": 0, "source_sha256": source_sha}
            if self.mode == "null":
                return fake_result(spec, source_sha, log_sha, log_path, {"log_sha256": None})
            if self.mode == "wrong-type":
                return fake_result(spec, source_sha, log_sha, log_path, {"return_checks": "one"})
            if self.mode == "bad-source-identity":
                return fake_result(spec, source_sha, log_sha, log_path, {"source_sha256": "c" * 64})
            if self.mode == "bad-log-identity":
                return fake_result(spec, source_sha, log_sha, log_path, {"log_sha256": "d" * 64})
            return fake_result(spec, source_sha, log_sha, log_path)

        self.fake_prove = types.SimpleNamespace(TIMEOUT_SECONDS=180, extract=FakeProve.extract,
                                                run_case=run_case)
        self.fake_ranks = FakeRanks
        provider = types.SimpleNamespace(require_supported_provider=lambda: {"provider": "cloud-build"})
        self.patches = [
            patch.object(runner, "load_module", return_value=provider),
            patch.object(runner, "load_profile", side_effect=self.load_profile),
            patch.object(runner, "source_identity", return_value={"sha256": runner.SOURCE_SHA256}),
            patch.object(runner, "tool_identity", return_value={"sha256": runner.TOOL_SHA256}),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

    def load_profile(self, environ):
        return self.profile, {"path": str(self.profile_path), "sha256": "a" * 64}

    def prepare_profile(self, stage, targets=None):
        specs = runner.matrix(stage, self.fake_prove, self.fake_ranks, PAIR13)
        expected = [s["target"] for s in specs]
        if stage in ("controls", "controls-order"):
            expected.append("classifier-reject-controls-7")
        self.profile = {
            "schema": "smallsort-network-n13-execution-profile-v1",
            "status": "EXECUTION_CANDIDATE_PINNED", "accepted": False, "proof_credit": False,
            "source": {"commit": "cd371e035c7e573760c43bf934d53e8118ee3e7d",
                       "path": str(runner.SOURCE_RELATIVE), "sha256": runner.SOURCE_SHA256,
                       "git_blob": runner.SOURCE_BLOB, "sort9_calls": 25, "sort13_calls": 45},
            "stages": {stage: {"targets": targets if targets is not None else expected,
                               "timeout_seconds": sum(s["timeout_seconds"] for s in specs),
                               "build_timeout_seconds": sum(s["timeout_seconds"] for s in specs) + 375}},
        }

    def invoke(self, stage="exact"):
        evidence = self.root / f"evidence-{len(list(self.root.glob('evidence-*')))}"
        code = runner.main(["--tool-home", str(self.tool_home), "--evidence", str(evidence), "--stage", stage],
                           dict(CLOUD, INFRA_ROOT=str(self.root)),
                           dependencies=(self.fake_prove, self.fake_ranks))
        return code, evidence, json.loads((evidence / "results.json").read_text())

    def test_exact_success_records_identities_targets_and_snapshots(self):
        self.prepare_profile("exact")
        code, evidence, summary = self.invoke()
        self.assertEqual(code, 0)
        self.assertTrue(summary["complete"])
        self.assertFalse(summary["proof_credit"])
        self.assertEqual(summary["execution_profile"]["sha256"], "a" * 64)
        self.assertEqual(summary["targets"][0]["target"], "exact-n13-full-post")
        row = summary["cases"][0]
        self.assertEqual(row["state"], "OBSERVED_VALID")
        self.assertEqual(row["result"]["source_sha256"], row["generated_sha256"])
        self.assertIsInstance(row["snapshot_before"], list)
        self.assertIsInstance(row["snapshot_after"], list)
        self.assertTrue((evidence / "results.json").is_file())

    def test_timeout_preserves_exception_and_partial_artifacts(self):
        self.prepare_profile("exact")
        self.mode = "timeout"
        code, _evidence, summary = self.invoke()
        row = summary["cases"][0]
        self.assertEqual(code, 2)
        self.assertEqual(row["state"], "ERROR")
        self.assertEqual(row["exception"]["type"], "TimeoutError")
        names = {item["name"] for item in row["snapshot_after"]}
        self.assertIn("network13_finite_swo_order.c", names)
        self.assertIn("network13_finite_swo_order.log", names)

    def test_error_exit_is_inconclusive_and_preserved(self):
        self.prepare_profile("exact")
        self.mode = "error-exit"
        code, _evidence, summary = self.invoke()
        self.assertEqual(code, 2)
        result = summary["cases"][0]["result"]
        self.assertEqual(result["exit"], 1)
        self.assertEqual(result["errors"], ["verifier error"])
        self.assertEqual(summary["cases"][0]["state"], "INCONCLUSIVE")

    def test_missing_null_and_wrong_type_results_fail_closed(self):
        self.prepare_profile("exact")
        for mode, expected in (("missing", "missing fields"), ("null", "wrong-typed"),
                               ("wrong-type", "wrong-typed")):
            with self.subTest(mode=mode):
                self.mode = mode
                code, _evidence, summary = self.invoke()
                self.assertEqual(code, 2)
                self.assertIn(expected, summary["cases"][0]["result"]["runner_error"])

    def test_saved_source_and_log_hashes_must_match_reported_identities(self):
        self.prepare_profile("exact")
        for mode in ("bad-source-identity", "bad-log-identity"):
            with self.subTest(mode=mode):
                self.mode = mode
                code, _evidence, summary = self.invoke()
                self.assertEqual(code, 2)
                self.assertIn("identity", summary["cases"][0]["result"]["runner_error"])

    def test_source_stage_and_target_mismatches_refuse_before_case(self):
        self.prepare_profile("preflight")
        with self.subTest("stage"):
            code, _evidence, summary = self.invoke("exact")
            self.assertEqual(code, 2)
            self.assertIn("no stage record", summary["errors"][0]["message"])
            self.assertEqual(summary["cases"][0]["state"], "NOT_RUN")
            self.assertEqual(self.generated, [])
        self.prepare_profile("exact", targets=["wrong-target"])
        with self.subTest("target"):
            code, _evidence, summary = self.invoke("exact")
            self.assertEqual(code, 2)
            self.assertIn("target list mismatch", summary["errors"][0]["message"])
            self.assertEqual(summary["cases"][0]["state"], "NOT_RUN")
            self.assertEqual(self.generated, [])
        self.prepare_profile("exact")
        self.profile["source"]["sha256"] = "c" * 64
        with self.subTest("source"):
            code, _evidence, summary = self.invoke("exact")
            self.assertEqual(code, 2)
            self.assertIn("source SHA256 mismatch", summary["errors"][0]["message"])
            self.assertEqual(self.generated, [])

    def test_negative_gate_requires_all_seven_controls_and_preserves_exit(self):
        self.prepare_profile("controls")
        code, _evidence, summary = self.invoke("controls")
        self.assertEqual(code, 0)
        self.assertEqual(len(summary["cases"]), 2)
        self.assertTrue(all(case["result"]["exit"] == 1 for case in summary["cases"]))
        self.assertTrue(all(case["gate"] is True for case in summary["cases"]))
        self.assertIn("classifier-reject-controls-7", [t["target"] for t in summary["targets"]])

    def test_order_control_runs_in_its_own_stage(self):
        self.prepare_profile("controls-order")
        code, _evidence, summary = self.invoke("controls-order")
        self.assertEqual(code, 0)
        self.assertEqual([row["target"] for row in summary["cases"]], ["exact-n13-order-post"])
        self.assertIn("classifier-reject-controls-7", [t["target"] for t in summary["targets"]])
        controls = summary["cases"][0]["result"]["classifier_rejection_controls"]
        self.assertEqual(len(controls), 7)
        self.assertTrue(all(value is True for value in controls.values()))

    def test_revised_stage_matrix_and_case_limits(self):
        expected = {
            "preflight": (["generic-swo-bridge", "domain13-members"], [180, 180]),
            "exact": (["exact-n13-full-post"], [420]),
            "controls": (["missing-equiv-trans", "exact-n13-membership-post"], [180, 420]),
            "controls-order": (["exact-n13-order-post"], [420]),
            "regressions": (["exact-n9-regression", "universal-n13-regression"], [180, 360]),
            "regressions-n9": (["exact-n9-regression"], [180]),
            "regressions-n13": (["universal-n13-regression"], [360]),
        }
        for stage, (targets, limits) in expected.items():
            with self.subTest(stage=stage):
                cases = runner.matrix(stage, self.fake_prove, self.fake_ranks, PAIR13)
                self.assertEqual([case["target"] for case in cases], targets)
                self.assertEqual([case["timeout_seconds"] for case in cases], limits)

    def test_n9_only_regression_runs_without_generating_universal_case_or_credit(self):
        self.prepare_profile("regressions-n9")
        FakeRanks.composition_calls.clear()
        code, _evidence, summary = self.invoke("regressions-n9")
        self.assertEqual(code, 0)
        self.assertTrue(summary["complete"])
        self.assertFalse(summary["proof_credit"])
        self.assertEqual([row["target"] for row in summary["cases"]], ["exact-n9-regression"])
        self.assertEqual((summary["stage_timeout_seconds"], summary["build_timeout_seconds"]), (180, 555))
        self.assertEqual(FakeRanks.composition_calls, [(9, True)])
        self.assertEqual([row["name"] for row in self.generated], ["network9_finite_swo_order"])

    def test_n9_only_build_timeout_mismatch_stays_not_run(self):
        self.prepare_profile("regressions-n9")
        self.profile["stages"]["regressions-n9"]["build_timeout_seconds"] = 554
        FakeRanks.composition_calls.clear()
        code, _evidence, summary = self.invoke("regressions-n9")
        self.assertEqual(code, 2)
        self.assertIn("case/build timeout envelope", summary["errors"][0]["message"])
        self.assertEqual(summary["cases"][0]["state"], "NOT_RUN")
        self.assertEqual(FakeRanks.composition_calls, [(9, True)])
        self.assertEqual(self.generated, [])

    def test_n13_only_regression_runs_without_generating_n9_or_credit(self):
        self.prepare_profile("regressions-n13")
        FakeRanks.composition_calls.clear()
        code, _evidence, summary = self.invoke("regressions-n13")
        self.assertEqual(code, 0)
        self.assertTrue(summary["complete"])
        self.assertFalse(summary["proof_credit"])
        self.assertEqual([row["target"] for row in summary["cases"]], ["universal-n13-regression"])
        self.assertEqual((summary["stage_timeout_seconds"], summary["build_timeout_seconds"]), (360, 735))
        self.assertEqual(FakeRanks.composition_calls, [(13, False)])
        self.assertEqual([row["name"] for row in self.generated], ["network13_symbolic_swo_composition"])


if __name__ == "__main__":
    unittest.main()
