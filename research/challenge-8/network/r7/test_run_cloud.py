"""Synthetic tests for the R7 Cloud runner; no source extraction or proof tools."""
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r7_cloud_tested", HERE / "run-cloud.py")
runner = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(runner)
compiler_identity_impl = runner.compiler_identity


class SyntheticRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence = self.root / "evidence"
        self.evidence.mkdir()
        self.tool = self.root / "tool"
        self.tool.mkdir()
        self.profile_path = self.root / "R7-profile.json"
        self.profile_path.write_text("synthetic pinned profile\n")
        self.args = type("Args", (), {"evidence": str(self.evidence), "tool_home": str(self.tool)})()
        self.calls = []
        self.mode = "success"
        self.profile = {
            "verifier": {"args": ["-rustc_args", "--edition 2021", "-skip_specless_fns", "-verbose", "1",
                                    "verified/lib.rs"], "timeout_seconds": 180},
            "refiner": {"args": ["--rustc-args", "--edition 2021", "original/lib.rs", "verified/lib.rs"],
                        "timeout_seconds": 180},
            "compiler": {"commit": "a" * 40},
            "target": {"symbol": runner.FUNCTION, "contract": runner.CONTRACT,
                       "expected_named_bodies": 1, "minimum_statement_records": 1},
        }
        self.patches = [
            patch.object(runner, "validate_extraction", return_value={
                "commit": runner.SOURCE_COMMIT, "git_blob": runner.SOURCE_BLOB,
                "target_statement_lines": [6, 7], "sha256": runner.SOURCE_SHA256,
            }),
            patch.object(runner, "tool_identities", side_effect=self.fake_tool_identities),
            patch.object(runner, "compiler_identity", return_value={
                "toolchain": runner.TOOLCHAIN, "commit": "a" * 40,
                "target": "x86_64-unknown-linux-gnu", "abi": "LP64",
                "version": "synthetic rustc --version --verbose", "accepted": True,
            }),
            patch.object(runner, "source_unchanged", return_value=True),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        exporter_patch = patch.object(runner, "extractor_identity", return_value={
            "path": "synthetic-exporter", "sha256": "c" * 64,
        })
        exporter_patch.start()
        self.addCleanup(exporter_patch.stop)

    def fake_extract(self, _proof_root, evidence):
        source = self.root / runner.SOURCE_REL
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b"synthetic pinned source\n")
        for relative, payload in {
            "verified/lib.rs": b"verified lib", "original/lib.rs": b"original lib",
            "verified/smallsort.rs": b"verified spec", "original/smallsort.rs": b"original spec",
            "extraction.json": b"{}", "source-spans/has_efficient_in_place_swap.rs": b"target",
        }.items():
            path = evidence / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)

    def fake_tool_identities(self, _tool_home, _proof_root, evidence):
        inventory = evidence / "tool-inventory.json"
        inventory.write_text('{"files": []}\n')
        paths = {}
        for key, relative in (("verifier", "bin/verifast"), ("refiner", "bin/refinement-checker"),
                              ("exporter", "bin/vf-rust-mir-exporter")):
            path = self.tool / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"synthetic {key}\n")
            paths[key] = {"path": str(path), "sha256": "c" * 64}
        source_extractor = self.root / "extractor.py"
        source_extractor.write_text("synthetic source extractor\n")
        paths["source_extractor"] = {"path": str(source_extractor), "sha256": "d" * 64}
        paths["verifier"]["sha256"] = runner.CONSOLE_SHA256
        paths.update({"tool_home": str(self.tool), "archive_sha256": runner.ARCHIVE_SHA256,
                      "tool_commit": runner.TOOL_COMMIT, "verifier": paths["verifier"]})
        return paths

    def fake_commands(self, label, argv, cwd, log_path, timeout=runner.TIMEOUT_SECONDS):
        self.calls.append((label, argv, cwd, timeout))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if self.mode == "timeout" and label == "verifier":
            log_path.write_text("partial verifier trace\n")
            return {"label": label, "argv": argv, "state": "TIMEOUT", "exit": None,
                    "timeout_seconds": timeout, "exception": {"type": "TimeoutExpired", "message": "timeout"}}
        if self.mode == "exception" and label == "verifier":
            log_path.write_text("partial before exception\n")
            return {"label": label, "argv": argv, "state": "EXCEPTION", "exit": None,
                    "timeout_seconds": timeout, "exception": {"type": "OSError", "message": "synthetic"}}
        if self.mode == "not-run" and label == "verifier":
            return {"label": label, "argv": argv, "state": "NOT_RUN", "exit": None,
                    "timeout_seconds": timeout}
        if label == "verifier" and self.mode == "error-exit":
            log_path.write_text("Verifying function 'smallsort::has_efficient_in_place_swap'\nerror: synthetic\n")
            return {"label": label, "argv": argv, "state": "EXITED", "exit": 1,
                    "log": str(log_path), "log_sha256": runner.sha(log_path.read_bytes()),
                    "timeout_seconds": timeout}
        if label == "verifier":
            if self.mode == "no-target":
                log_path.write_text("Verifying function 'smallsort::other'\n")
            else:
                log_path.write_text(
                    "Verifying function 'smallsort::has_efficient_in_place_swap'\n"
                    "verified/smallsort.rs(6,1): Executing statement\n")
        else:
            log_path.write_text("refinement: unchanged\n")
            if self.mode == "mutate-input":
                (self.evidence / "verified/smallsort.rs").write_text("mutated proof input\n")
        result_label, result_argv, result_hash = label, argv, runner.sha(log_path.read_bytes())
        if self.mode == "wrong-label" and label == "verifier":
            result_label = "unexpected"
        if self.mode == "wrong-argv" and label == "verifier":
            result_argv = ["wrong"]
        if self.mode == "wrong-log-hash" and label == "verifier":
            result_hash = "f" * 64
        result_exit = True if self.mode == "bool-exit" and label == "verifier" else 0
        return {"label": result_label, "argv": result_argv, "cwd": str(cwd), "state": "EXITED", "exit": result_exit,
                "log": str(log_path), "log_sha256": result_hash,
                "timeout_seconds": timeout}

    def run_case(self, mode="success", provider=None):
        self.mode = mode
        self.evidence = self.root / f"evidence-{len(list(self.root.glob('evidence-*')))}"
        self.evidence.mkdir()
        self.args.evidence = str(self.evidence)
        return runner.execute(
            self.args, {"INFRA_ROOT": str(self.root), "PROOF_ROOT": str(self.root)},
            provider_check=provider or (lambda _root: {"provider": "cloud-build", "project": "smallsort-ci",
                                                       "region": "global"}),
            profile_loader=lambda _root, _env: (self.profile, {"path": str(self.profile_path), "sha256": runner.sha(self.profile_path.read_bytes())}),
            extractor=self.fake_extract, command_runner=self.fake_commands,
        )

    def test_success_requires_exact_target_trace_and_both_zero_exits(self):
        code, result = self.run_case()
        self.assertEqual(code, 0)
        self.assertTrue(result["accepted"])
        self.assertFalse(result["proof_credit"])
        self.assertFalse(result["audit"]["accepted"])
        self.assertTrue(result["audit"]["component_accepted"])
        self.assertEqual([item[0] for item in self.calls], ["verifier", "refiner"])
        self.assertEqual([item[3] for item in self.calls], [180, 180])

    def test_proof_inputs_must_remain_unchanged_during_tools(self):
        code, result = self.run_case("mutate-input")
        self.assertEqual(code, 2)
        self.assertFalse(result["accepted"])
        self.assertFalse(result["proof_inputs_unchanged"])
        before = {item["input"]: item.get("sha256") for item in result["input_snapshot_before"]}
        after = {item["input"]: item.get("sha256") for item in result["input_snapshot_after"]}
        self.assertNotEqual(before["evidence/verified/smallsort.rs"],
                            after["evidence/verified/smallsort.rs"])

    def test_receipt_label_argv_hash_and_bool_exit_are_rejected(self):
        for mode in ("wrong-label", "wrong-argv", "wrong-log-hash", "bool-exit"):
            with self.subTest(mode=mode):
                self.calls.clear()
                code, result = self.run_case(mode)
                self.assertEqual(code, 2)
                self.assertFalse(result["accepted"])
                self.assertFalse(result["command_validations"]["verifier"])
                self.assertTrue(result["commands"][0]["validation_errors"])

    def test_compiler_failure_preserves_returncode_output_and_timeout(self):
        evidence = self.root / "compiler-evidence"
        evidence.mkdir()
        profile = {"compiler": {"commit": runner.COMPILER_COMMIT,
                                 "target": "x86_64-unknown-linux-gnu", "data_model": "LP64"}}
        output = "rustc 1.0\ncommit-hash: deadbeef\nhost: wrong-target\n"
        with patch.object(runner.subprocess, "run", return_value=subprocess.CompletedProcess(
                ["rustc"], 17, stdout=output)):
            failed = compiler_identity_impl(profile, evidence)
        self.assertEqual(failed["exit"], 17)
        self.assertEqual(failed["raw_output"], output)
        self.assertFalse(failed["accepted"])
        with patch.object(runner.subprocess, "run", side_effect=subprocess.TimeoutExpired(
                ["rustc"], 180, output=b"partial rustc version")):
            timed_out = compiler_identity_impl(profile, evidence)
        self.assertEqual(timed_out["state"], "TIMEOUT")
        self.assertIsNone(timed_out["exit"])
        self.assertEqual(timed_out["raw_output"], "partial rustc version")
        self.assertEqual(timed_out["exception"]["timeout_seconds"], 180)

    def test_verifier_error_still_runs_refiner_and_preserves_exit(self):
        code, result = self.run_case("error-exit")
        self.assertEqual(code, 2)
        self.assertEqual([item[0] for item in self.calls], ["verifier", "refiner"])
        self.assertEqual(result["commands"][0]["exit"], 1)
        self.assertEqual(result["commands"][1]["exit"], 0)

    def test_timeout_exception_and_partial_log_are_retained(self):
        for mode, state in (("timeout", "TIMEOUT"), ("exception", "EXCEPTION")):
            with self.subTest(mode=mode):
                self.calls.clear()
                code, result = self.run_case(mode)
                self.assertEqual(code, 2)
                self.assertEqual(result["commands"][0]["state"], state)
                self.assertEqual(result["commands"][0]["exception"]["type"],
                                 "TimeoutExpired" if mode == "timeout" else "OSError")
                self.assertEqual(result["commands"][1]["label"], "refiner")
                snapshot_names = {row["path"] for row in result["evidence_snapshot"]}
                self.assertIn("logs/verifier.log", snapshot_names)

    def test_not_run_is_never_accepted_and_refiner_still_runs(self):
        code, result = self.run_case("not-run")
        self.assertEqual(code, 2)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["commands"][0]["state"], "NOT_RUN")
        self.assertEqual(result["commands"][1]["label"], "refiner")

    def test_missing_null_wrong_type_and_target_mismatch_are_fail_closed(self):
        malformed = [
            {},
            {"state": None, "exit": 0},
            {"state": "EXITED", "exit": "0"},
        ]
        for record in malformed:
            with self.subTest(record=record):
                self.mode = "success"
                count = 0

                def malformed_commands(label, argv, cwd, log_path, timeout=180):
                    nonlocal count
                    count += 1
                    if count == 1:
                        return dict(record)
                    return self.fake_commands(label, argv, cwd, log_path, timeout)

                self.evidence = self.root / f"malformed-{len(list(self.root.glob('malformed-*')))}"
                self.evidence.mkdir()
                self.args.evidence = str(self.evidence)
                code, result = runner.execute(
                    self.args, {"INFRA_ROOT": str(self.root), "PROOF_ROOT": str(self.root)},
            provider_check=lambda _root: {"provider": "cloud-build", "project": "smallsort-ci",
                                                  "region": "global"},
                    profile_loader=lambda _root, _env: (self.profile, {"path": str(self.profile_path),
                                                                         "sha256": runner.sha(self.profile_path.read_bytes())}),
                    extractor=self.fake_extract, command_runner=malformed_commands,
                )
                self.assertEqual(code, 2)
                self.assertFalse(result["accepted"])
                for key, value in record.items():
                    self.assertEqual(result["commands"][0].get(key), value)
                self.assertTrue(result["commands"][0]["validation_errors"])
                self.assertIsInstance(result["evidence_snapshot"], list)
        self.calls.clear()
        with patch.object(runner, "validate_extraction", side_effect=RuntimeError(
                "extraction source-stage-target mismatch: specified_function")):
            code, result = self.run_case("success")
        self.assertEqual(code, 2)
        self.assertIn("source-stage-target mismatch", result["error"]["message"])
        self.assertEqual(self.calls, [])

    def test_provider_failure_precedes_extraction_and_tool_calls(self):
        extracted = []
        def forbidden_extract(*_args):
            extracted.append(True)
        code, result = runner.execute(
            self.args, {"INFRA_ROOT": str(self.root), "PROOF_ROOT": str(self.root)},
            provider_check=lambda _root: (_ for _ in ()).throw(RuntimeError("wrong provider")),
            profile_loader=lambda _root, _env: (self.profile, {"path": str(self.profile_path),
                                                                 "sha256": runner.sha(self.profile_path.read_bytes())}),
            extractor=forbidden_extract, command_runner=self.fake_commands,
        )
        self.assertEqual(code, 2)
        self.assertFalse(extracted)
        self.assertEqual(self.calls, [])
        self.assertIn("wrong provider", result["error"]["message"])


if __name__ == "__main__":
    unittest.main()
