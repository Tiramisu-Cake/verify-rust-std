"""Synthetic service tests for kani_k1.py. Run: python3 -B -m unittest discover -s research/challenge-8/kani-k1/tools"""
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kani_k1 as k  # noqa: E402

P = "slice::sort::shared::smallsort::verify::"
REQ = {
    "schema": "kani-k1-run-request-v1", "request_id": "smoke-001", "agent": "coordinator",
    "kind": "measurement", "purpose": "lane smoke", "runner": "ubuntu-latest", "harness_timeout_minutes": 10,
    "harnesses": [{"name": P + "smoke::ok", "expect": "SUCCESS"},
                  {"name": P + "smoke::control", "expect": "FAILED", "expect_check": "has_efficient_in_place_swap"}],
}
OK_BLOCK = f"""Checking harness {P}smoke::ok...
VERIFICATION RESULT:
 ** 0 of 12 failed (2 unreachable)

 ** 2 of 2 cover properties satisfied

VERIFICATION:- SUCCESSFUL
Verification Time: 1.25s
"""
FAIL_BLOCK = f"""Checking harness {P}smoke::control...
Failed Checks: assertion failed: has_efficient_in_place_swap::<[u8; 9]>()
 File: "library/core/src/slice/sort/shared/smallsort/kani_k1/smoke.rs", line 20, in control
VERIFICATION RESULT:
 ** 1 of 3 failed

VERIFICATION:- FAILED
Verification Time: 0.5s
"""


def tail(success, failures):
    total = success + failures
    return f"\nSummary:\nVerification failed for - x\nComplete - {success} successfully verified harnesses, {failures} failures, {total} total.\n"


GOOD_LOG = OK_BLOCK + FAIL_BLOCK + tail(1, 1)
TIME = "\tMaximum resident set size (kbytes): 4096000\n\tElapsed (wall clock) time (h:mm:ss or m:ss): 41:02.11\n"


def req_with(**changes):
    req = copy.deepcopy(REQ)
    req.update(changes)
    return req


def summ(log, req=None, time=TIME, exit_code=1, request_error=None, build_outcome="success", inventory_text=None):
    text = json.dumps(req if req is not None else REQ)
    return k.summarize(text, log, time, exit_code, "a" * 40, "b" * 40, request_error,
                       {"id": "1", "attempt": "1", "image_os": "ubuntu24", "image_version": "x"}, {"f": "0" * 64},
                       build_outcome, inventory_text=inventory_text)


ONLY_OK = [{"name": P + "smoke::ok", "expect": "SUCCESS"}]


class InventoryPrefixScopeTests(unittest.TestCase):
    def test_inventory_uses_supported_list_without_harness_filter(self):
        script = (Path(__file__).parent / "gcb-k1.sh").read_text()
        self.assertNotIn("--harness 'slice::sort::shared::smallsort::verify::'", script)
        self.assertIn('timeout --kill-after=30 60m "$PWD/kani_build/scripts/kani" list', script)


class RequestTests(unittest.TestCase):
    def bad(self, mutate, needle):
        req = copy.deepcopy(REQ)
        mutate(req)
        with self.assertRaises(k.RequestError) as cm:
            k.validate_request(req)
        self.assertIn(needle, str(cm.exception))

    def test_valid_and_args(self):
        args = k.kani_args(k.validate_request(copy.deepcopy(REQ)))
        self.assertEqual(args[:4], ["--harness", P + "smoke::ok", "--harness", P + "smoke::control"])
        for flag in ("--exact", "--jobs=1", "10m", "--output-format=terse"):
            self.assertIn(flag, args)

    def test_rejections(self):
        self.bad(lambda r: r.update(schema="x"), "schema")
        self.bad(lambda r: r.update(extra=1), "unknown")
        self.bad(lambda r: r.pop("purpose"), "missing")
        self.bad(lambda r: r.pop("runner"), "missing")
        self.bad(lambda r: r.update(request_id="Bad ID"), "request_id")
        self.bad(lambda r: r.update(request_id="ok\n"), "request_id")
        self.bad(lambda r: r.update(agent="select"), "agent")
        self.bad(lambda r: r.update(kind="proof"), "kind")
        self.bad(lambda r: r.update(runner="windows-latest"), "runner")
        self.bad(lambda r: r.update(purpose="a\nb"), "purpose")
        self.bad(lambda r: r.update(harness_timeout_minutes=31), "harness_timeout")
        self.bad(lambda r: r.update(harness_timeout_minutes=True), "harness_timeout")
        self.bad(lambda r: r.update(harness_timeout_minutes=12), "measurement")
        self.bad(lambda r: r.update(harnesses=[]), "1..20")
        self.bad(lambda r: r["harnesses"].append(dict(r["harnesses"][0])), "duplicate")
        self.bad(lambda r: r["harnesses"][0].update(expect="PASS"), "expect")
        self.bad(lambda r: r["harnesses"][0].update(note="x"), "entry")
        self.bad(lambda r: r["harnesses"][0].update(expect_check="x"), "expect_check")
        self.bad(lambda r: r["harnesses"][1].pop("expect_check"), "expect_check")
        self.bad(lambda r: r["harnesses"][1].update(expect_check="a\nb"), "expect_check")

    def test_non_string_values_are_request_errors(self):
        for key in ("agent", "kind", "runner"):
            self.bad(lambda r, key=key: r.update({key: ["x"]}), key)
        self.bad(lambda r: r["harnesses"][0].update(expect={"a": 1}), "expect")
        self.bad(lambda r: r["harnesses"][0].update(name=["x"]), "harness name")

    def test_rejects_names_outside_experiment_module(self):
        for name in ["slice::sort::shared::smallsort::kani_k1::h", "x; rm -rf /", P + "a b", P, P + "ok::",
                     P + "ok\n", P + "ok\n--harness x"]:
            req = copy.deepcopy(REQ)
            req["harnesses"][0]["name"] = name
            with self.assertRaises(k.RequestError):
                k.validate_request(req)

    def test_total_budget(self):
        req = req_with(kind="diagnostic", harness_timeout_minutes=30,
                       harnesses=[{"name": P + f"h{i}", "expect": "SUCCESS"} for i in range(6)])
        with self.assertRaises(k.RequestError):
            k.validate_request(req)

    def test_inventory_request_is_explicit_whole_job_lane(self):
        inventory = {**REQ, "runner": k.STANDARD_RUNNER, "kind": "inventory", "harness_timeout_minutes": 60,
                     "harnesses": [], "inventory": True}
        self.assertEqual(k.validate_request(inventory), inventory)
        self.assertEqual(k.kani_args(inventory), [])
        self.assertEqual(k.verification_mode("inventory"), "inventory")
        for bad in ({**inventory, "inventory": 1}, {**inventory, "runner": "ubuntu-latest"},
                    {**inventory, "inventory": False}, {**inventory, "harnesses": ONLY_OK},
                    {**inventory, "harness_timeout_minutes": 61}, {**inventory, "controls": "yes"},
                    {**inventory, "kani_jobs": 1}):
            with self.assertRaises(k.RequestError):
                k.validate_request(bad)

    def test_inventory_gate_requires_success_and_bound_complete_artifact(self):
        req = {**REQ, "runner": k.STANDARD_RUNNER, "kind": "inventory", "harness_timeout_minutes": 60,
               "harnesses": [], "inventory": True, "controls": True}
        req_text = json.dumps(req)
        names = P + "a\n" + P + "b\n"
        fields = [f"schema={k.INVENTORY_SCHEMA}", f"request_id={req['request_id']}",
                  f"request_sha256={hashlib.sha256(req_text.encode()).hexdigest()}", "build_id=build-1",
                  "head_sha=" + "a" * 40, "kani_commit=" + "b" * 40, "count=2",
                  f"names_sha256={hashlib.sha256(names.encode()).hexdigest()}"]
        artifact = "\n".join(fields) + "\n\n" + names
        good = k.summarize(req_text, "warning: stub", None, 0, "a" * 40, "b" * 40,
                           run={"id": "build-1"}, inventory_text=artifact)
        self.assertEqual(good["status"], "COMPLETE")
        self.assertTrue(k.gate_ok(good))
        self.assertEqual(good["inventory_result"]["count"], 2)
        for log, code, inv in (("warning", 1, artifact), ("warning", 0, None),
                               ("warning", 0, artifact.replace("count=2", "count=3"))):
            summary = k.summarize(req_text, log, None, code, "a" * 40, "b" * 40,
                                  run={"id": "build-1"}, inventory_text=inv)
            self.assertFalse(k.gate_ok(summary), summary)


class SummaryTests(unittest.TestCase):
    def test_complete_with_expectations(self):
        s = summ(GOOD_LOG)
        self.assertEqual(s["status"], "COMPLETE", s["inconsistencies"])
        self.assertTrue(s["expectation_met"])
        self.assertTrue(s["measurement_ok"])
        self.assertTrue(k.gate_ok(s))
        ok, control = s["harnesses"]
        self.assertEqual((ok["status"], ok["time_s"], ok["unreachable"]), ("SUCCESS", 1.25, 2))
        self.assertEqual((control["status"], control["failed_located"]), ("FAILED", 1))
        self.assertEqual(control["failed_checks"][0]["location"], "library/core/src/slice/sort/shared/smallsort/kani_k1/smoke.rs:20")
        self.assertIn("has_efficient", control["failed_checks"][0]["description"])
        self.assertEqual(s["resources"]["max_rss_kb_whole_run"], 4096000)
        self.assertEqual(s["tooling_sha256"], {"f": "0" * 64})
        self.assertTrue(any("unreachable" in n for n in s["notes"]))

    def test_failed_expectation_requires_a_located_check(self):
        unlocated = GOOD_LOG.replace(' File: "library/core/src/slice/sort/shared/smallsort/kani_k1/smoke.rs", line 20, in control\n', "")
        s = summ(unlocated)
        self.assertEqual(s["status"], "COMPLETE")
        self.assertFalse(s["expectation_met"])
        crashed = OK_BLOCK + f"Checking harness {P}smoke::control...\nVERIFICATION:- FAILED\nVerification Time: 3.0s\n" + tail(1, 1)
        self.assertFalse(summ(crashed)["expectation_met"])

    def test_expect_check_must_match(self):
        req = copy.deepcopy(REQ)
        req["harnesses"][1]["expect_check"] = "precondition"
        self.assertFalse(summ(GOOD_LOG, req)["expectation_met"])
        req["harnesses"][1]["expect_check"] = "smallsort"  # appears only in the file path
        self.assertFalse(summ(GOOD_LOG, req)["expectation_met"])
        # needle in an unlocated check while another check supplies the location
        mixed = GOOD_LOG.replace("Failed Checks: assertion failed: has_efficient",
                                 "Failed Checks: precondition violated\nFailed Checks: assertion failed: has_efficient")
        req["harnesses"][1]["expect_check"] = "precondition"
        self.assertFalse(summ(mixed, req)["expectation_met"])
        req["harnesses"][1]["expect_check"] = "has_efficient"
        self.assertTrue(summ(mixed, req)["expectation_met"])

    def test_unexpected_failure_breaks_expectation(self):
        req = copy.deepcopy(REQ)
        req["harnesses"][1] = {"name": P + "smoke::control", "expect": "SUCCESS"}
        s = summ(GOOD_LOG, req)
        self.assertEqual(s["status"], "COMPLETE")
        self.assertFalse(s["expectation_met"])
        self.assertFalse(k.gate_ok(s))

    def test_measurement_requires_parsed_and_satisfied_covers(self):
        req = req_with(harnesses=ONLY_OK)
        no_cover = OK_BLOCK.replace(" ** 2 of 2 cover properties satisfied\n", "") + tail(1, 0)
        s = summ(no_cover, req, exit_code=0)
        self.assertTrue(s["expectation_met"])
        self.assertTrue(s["measurement_ok"])
        self.assertTrue(k.gate_ok(s))
        controls_req = req_with(controls=True, runner=k.STANDARD_RUNNER, harnesses=ONLY_OK)
        self.assertFalse(summ(no_cover, controls_req, exit_code=0)["measurement_ok"])
        odd_format = OK_BLOCK.replace("2 of 2 cover properties satisfied", "2/2 covers ok") + tail(1, 0)
        self.assertFalse(summ(odd_format, controls_req, exit_code=0)["measurement_ok"])
        short = OK_BLOCK.replace("2 of 2 cover", "1 of 2 cover") + tail(1, 0)
        self.assertFalse(summ(short, controls_req, exit_code=0)["measurement_ok"])
        slow = OK_BLOCK.replace("1.25s", "600.5s") + tail(1, 0)
        self.assertFalse(summ(slow, req, exit_code=0)["measurement_ok"])
        self.assertTrue(summ(OK_BLOCK + tail(1, 0), controls_req, exit_code=0)["measurement_ok"])

    def test_autoharness_literal_workflow_command_and_validation(self):
        req = {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER, "harness_timeout_minutes": 240,
               "harnesses": [], "inventory": True}
        k.validate_request(req)
        k.validate_request(dict(req, harness_timeout_minutes=270))
        with self.assertRaises(k.RequestError):
            k.validate_request(dict(req, harness_timeout_minutes=271))
        for key in ("controls", "uninit_checks", "valid_value_checks", "worker_index", "worker_total", "kani_jobs"):
            bad = dict(req, **{key: (True if key in ("controls", "uninit_checks", "valid_value_checks") else 3)})
            with self.assertRaises(k.RequestError):
                k.validate_request(bad)
        workflow = (Path(__file__).parents[4] / ".github/workflows/kani.yml").read_text()
        command = k.extract_autoharness_command(workflow)
        for flag in ("--include-pattern", "--exclude-pattern", "--harness-timeout 10m", "--default-unwind 1000",
                     "--jobs=3", "--output-format=terse", "| tee autoharness-verification.log", "gzip autoharness-verification.log"):
            self.assertIn(flag, command)
        self.assertIn("conversions::to_*", workflow)

    def test_autoharness_step_preserves_pipeline_exit_through_gzip(self):
        workflow = (Path(__file__).parents[4] / ".github/workflows/kani.yml").read_text()
        command = k.extract_autoharness_command(workflow)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "scripts").mkdir()
            stub = root / "scripts/run-kani.sh"
            stub.write_text("#!/usr/bin/env bash\necho simulated-kani-output\nexit \"${SIM_EXIT:-0}\"\n")
            stub.chmod(0o755)
            script = root / "autoharness.sh"
            script.write_text(command)
            failed = subprocess.run(["bash", "-e", "-o", "pipefail", str(script)], cwd=root,
                                    env={**os.environ, "SIM_EXIT": "7"}, capture_output=True)
            self.assertEqual(failed.returncode, 7)
            self.assertTrue((root / "autoharness-verification.log").exists())
            self.assertFalse((root / "autoharness-verification.log.gz").exists())
            success = subprocess.run(["bash", "-e", "-o", "pipefail", str(script)], cwd=root,
                                     env={**os.environ, "SIM_EXIT": "0"}, capture_output=True)
            self.assertEqual(success.returncode, 0)
            self.assertTrue((root / "autoharness-verification.log.gz").exists())

    def test_gcb_stage_route_and_dispatch_validation_without_script_output(self):
        self.assertEqual(k.verification_mode("autoharness"), "autoharness")
        self.assertEqual(k.verification_mode("diagnostic"), "selected")
        self.assertEqual(k.verification_mode("partition"), "partition")
        shell = (Path(__file__).parent / "gcb-k1.sh").read_text()
        self.assertIn('= autoharness ]; then', shell)
        self.assertIn('= selected ]; then', shell)
        request = {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER, "harness_timeout_minutes": 240,
                   "harnesses": [], "inventory": True}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path, args_path, runner_path = root / "request.json", root / "args", root / "runner"
            request_path.write_text(json.dumps(request))
            result = subprocess.run([sys.executable, str(Path(__file__).parent / "kani_k1.py"), "validate",
                                     str(request_path), "--args-out", str(args_path), "--runner-out", str(runner_path),
                                     "--require-runner", k.STANDARD_RUNNER], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(runner_path.read_text().strip(), k.STANDARD_RUNNER)

    def test_autoharness_thread_timeout_without_time_and_duplicate_names(self):
        name = "intrinsics::verify::check_typed_swap_u8"
        log = (f"Thread 1: Checking harness {name}...\nThread 1: VERIFICATION:- TIMEOUT\n"
               f"Thread 2: Checking harness {name}...\nThread 2: VERIFICATION:- SUCCESSFUL\n"
               "Thread 2: Verification Time: 2.5s\n" + tail(1, 1))
        req = {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER, "harness_timeout_minutes": 240,
               "harnesses": []}
        s = summ(log, req, exit_code=1)
        self.assertEqual(s["status"], "COMPLETE")
        self.assertEqual(s["started_count"], 2)
        self.assertEqual([r["status"] for r in s["harnesses"]], ["TIMEOUT", "SUCCESS"])
        self.assertIsNone(s["harnesses"][0]["time_s"])
        self.assertEqual(s["counts"]["TIMEOUT"], 1)

    def test_kani_timeout_marker_closes_failed_thread_before_next_checking(self):
        lines = []
        for i in range(22):
            thread = i % 3 + 1
            name = f"std::harmonic_{i}"
            lines.append(f"Thread {thread}: Checking harness {name}...")
            if i < 13:
                lines.extend((f"Thread {thread}: VERIFICATION:- FAILED",
                              f"Thread {thread}: CBMC timed out. You may want to try increasing the harness timeout."))
            else:
                lines.extend((f"Thread {thread}: VERIFICATION:- SUCCESSFUL",
                              f"Thread {thread}: Verification Time: {i}.5s"))
        lines.append("Complete - 9 successfully verified harnesses, 13 failures, 22 total.")
        req = {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER, "harness_timeout_minutes": 240,
               "harnesses": []}
        s = summ("\n".join(lines), req, exit_code=1)
        self.assertEqual(s["status"], "COMPLETE")
        self.assertEqual(s["counts"]["TIMEOUT"], 13)
        self.assertEqual(s["counts"]["SUCCESS"], 9)
        self.assertEqual(s["inconsistencies"], [])
        self.assertFalse(s["expectation_met"])
        self.assertEqual(s["autoharness"]["timed_count"], 9)

    def test_timeout_marker_at_eof_is_timeout_without_verification_time(self):
        req = {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER, "harness_timeout_minutes": 240,
               "harnesses": []}
        log = ("Thread 2: Checking harness std::cut_off...\nThread 2: VERIFICATION:- FAILED\n"
               "Thread 2: CBMC timed out. You may want to try increasing the harness timeout.\n")
        s = summ(log, req, exit_code=124)
        self.assertEqual(s["status"], "PARTIAL")
        self.assertEqual(s["harnesses"][0]["status"], "TIMEOUT")
        self.assertIsNone(s["harnesses"][0]["time_s"])

    def test_autoharness_truncated_started_block_is_missing_result(self):
        req = {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER, "harness_timeout_minutes": 240,
               "harnesses": []}
        log = "Thread 3: Checking harness std::duplicate...\n"
        s = summ(log, req, exit_code=124)
        self.assertEqual(s["status"], "PARTIAL")
        self.assertEqual(s["harnesses"][0]["status"], "MISSING_RESULT")

    def test_autoharness_aggregate_precedes_truncated_rows(self):
        req = {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER, "harness_timeout_minutes": 240,
               "harnesses": []}
        s = summ("", req, exit_code=0)
        s["status"] = "COMPLETE"
        s["expectation_met"] = True
        s["autoharness"] = {"started_count": 300, "counts": {"SUCCESS": 300},
                            "sum_verification_time_s": 1234.5, "timed_count": 300, "slowest": []}
        s["harnesses"] = [{"name": f"std::h{i}", "expect": "workflow", "status": "SUCCESS", "time_s": 1.0}
                          for i in range(300)]
        text = k.render_md(s)
        self.assertIn("autoharness started: 300", text)
        self.assertIn("sum Verification Time: 1234.5 s over 300 timed harnesses", text)
        self.assertIn("summary.md truncated", text)

    def test_autoharness_summary_distinguishes_work_budget_from_harness_timeout(self):
        req = {**REQ, "kind": "autoharness", "runner": k.STANDARD_RUNNER,
               "harness_timeout_minutes": 270, "harnesses": []}
        text = k.render_md(summ("", req, exit_code=124))
        self.assertIn("whole-job work budget 270 min", text)
        self.assertIn("per-harness settings from the checked-out workflow", text)
        self.assertNotIn("per-harness timeout 270", text)

    def test_diagnostic_gate_ignores_measurement_bounds(self):
        req = req_with(kind="diagnostic", harnesses=ONLY_OK)
        no_cover = OK_BLOCK.replace(" ** 2 of 2 cover properties satisfied\n", "") + tail(1, 0)
        s = summ(no_cover, req, exit_code=0)
        self.assertIsNone(s["measurement_ok"])
        self.assertTrue(k.gate_ok(s))

    def test_peaks_keep_simultaneous_roles_and_ambiguous_harness_attribution(self):
        lines = ["samples=3", "total_rss_peak_kb=9000", "total_peak_s=8",
                 "role=cbmc simultaneous_rss_peak_kb=5000 peak_s=8",
                 "cbmc_pid=123 peak_kb=4500 first_s=4 last_s=8 peak_s=8 active=T1:foo,T2:bar hint=worker",
                 "solver_pid=124 cmd=kissat peak_kb=2000 first_s=6 last_s=8 peak_s=7 active=T1:foo,T2:bar",
                 "cgroup_event_oom=0", "cgroup_event_delta_oom=0", "dmesg_oom=none_seen"]
        peaks = k.parse_peaks("\n".join(lines))
        self.assertEqual(peaks["total_peak_s"], 8)
        self.assertEqual(peaks["roles"][0]["simultaneous_rss_peak_kb"], "5000")
        self.assertEqual(len(peaks["processes"]), 2)
        self.assertIn("T2:bar", peaks["processes"][0]["active"])
        self.assertEqual(peaks["cgroup_events"]["cgroup_event_delta_oom"], "0")

    def test_memory_peaks_keep_cgroup_and_dmesg_oom_tail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "peaks.txt"
            dmesg = subprocess.CompletedProcess(["dmesg"], 0, "kernel: Killed process 42 (cbmc)\n", "")
            with patch.object(k, "_cgroup_events", side_effect=[{"oom_kill": 1}, {"oom_kill": 2}]), \
                 patch.object(k.subprocess, "run", return_value=dmesg):
                k.sample_memory(log, 0.01, max_seconds=0, proc=root / "proc")
            text = log.read_text()
            self.assertLess(len(text.encode()), 7900)
            self.assertIn("cgroup_event_delta_oom_kill=1", text)
            self.assertTrue(text.rstrip().endswith("dmesg_oom=kernel: Killed process 42 (cbmc)"))

    def test_same_build_metadata_joins_manual_and_hashed_autoharness_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manual_model = root / "manual-harness.out"
            auto_model = root / "sha1_deadbeef_autoharness.out"
            proof_for_contract = {"pretty_name": "slice::proof_for_contract::<u8>", "mangled_name": "_Rproofv0",
                                  "goto_file": "manual-harness.symtab.out",
                                  "attributes": {"kind": {"ProofForContract": {"target_fn": "sort"}}}}
            auto_harness = {"pretty_name": "core::slice::sort::autoharness_target", "mangled_name": "_Rauto",
                            "goto_file": str(auto_model.with_suffix(".symtab.out")),
                            "attributes": {"kind": "Proof"}}
            null_goto = {"pretty_name": None, "mangled_name": None, "goto_file": None}
            metadata = root / "libcore-abc.kani-metadata.json"
            metadata.write_text(json.dumps({"crate_name": "core", "proof_harnesses": [null_goto, proof_for_contract, auto_harness],
                                            "test_harnesses": [], "contracted_functions": []}))
            manual = k.resolve_cbmc_metadata(["cbmc", "--object-bits", "12", str(manual_model),
                                              "--verbosity", "9", "--json-ui"], root,
                                             head_sha="a" * 40, kani_commit="b" * 40, build_id="build-1")
            self.assertEqual(manual["attribution"], "direct")
            self.assertEqual(manual["direct_harness"], proof_for_contract["pretty_name"])
            self.assertEqual(manual["metadata_group"], "proof_harnesses")
            self.assertEqual(manual["metadata_sha256"], hashlib.sha256(metadata.read_bytes()).hexdigest())
            self.assertEqual((manual["head_sha"], manual["kani_commit"], manual["build_id"]),
                             ("a" * 40, "b" * 40, "build-1"))
            auto = k.resolve_cbmc_metadata(["cbmc", str(auto_model)], root)
            self.assertEqual(auto["attribution"], "direct")
            self.assertEqual(auto["direct_harness"], auto_harness["pretty_name"])
            self.assertEqual(auto["model_path"], str(auto_model.resolve()))

    def test_relative_goto_file_uses_process_cwd_not_metadata_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cwd = root / "project"
            model_dir = cwd / "target/kani_verify_std/target/debug/deps"
            model_dir.mkdir(parents=True)
            metadata = model_dir / "libstd.kani-metadata.json"
            row = {"pretty_name": "std::autoharness_target", "mangled_name": "_Rhashed",
                   "goto_file": "target/kani_verify_std/target/debug/deps/hashed_autoharness.symtab.out"}
            metadata.write_text(json.dumps({"proof_harnesses": [row], "test_harnesses": []}))
            model = "target/kani_verify_std/target/debug/deps/hashed_autoharness.out"
            result = k.resolve_cbmc_metadata(["cbmc", "--object-bits", "12", model,
                                              "--verbosity", "9", "--json-ui"], cwd)
            self.assertEqual(result["attribution"], "direct")
            self.assertEqual(result["direct_harness"], row["pretty_name"])
            self.assertEqual(result["model_path"], str((cwd / model).resolve()))

    def test_metadata_join_fails_closed_on_duplicate_conflict_and_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model = root / "proof.out"
            row = {"pretty_name": "crate::proof", "mangled_name": "_Rproof", "goto_file": "proof.symtab.out"}
            path = root / "crate.kani-metadata.json"
            path.write_text(json.dumps({"proof_harnesses": [row], "test_harnesses": []}))
            first = k.resolve_cbmc_metadata(["cbmc", "proof.out"], root)
            self.assertEqual(first["attribution"], "direct")
            path.write_text(json.dumps({"proof_harnesses": [row, {**row, "pretty_name": "crate::other"}],
                                        "test_harnesses": []}))
            stat = path.stat()
            os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 5_000_000_000))
            cached = k._METADATA_INDEX_CACHE[f"{root.resolve()}|cwd={root.resolve()}"]
            cached["checked_s"] = 0
            conflict = k.resolve_cbmc_metadata(["cbmc", "proof.out"], root)
            self.assertEqual(conflict["attribution"], "metadata-ambiguous")
            absent = k.resolve_cbmc_metadata(["cbmc", "missing.out"], root / "elsewhere")
            self.assertEqual(absent["attribution"], "metadata-not-found")

    def test_active_set_never_becomes_direct_but_solver_inherits_exact_cbmc_match(self):
        active_only = {"10": {"pid": "10", "cmd": "cbmc", "attribution": "metadata-not-found",
                              "active_at_peak": {"1": "crate::proof"}},
                       "11": {"pid": "11", "cmd": "kissat", "ppid": "10", "active_at_peak": {"1": "crate::proof"}}}
        k.finalize_process_records(active_only)
        self.assertEqual(active_only["10"]["attribution"], "active-set-ambiguous")
        self.assertEqual(active_only["10"]["metadata_resolution"], "metadata-not-found")
        self.assertEqual(active_only["11"]["attribution"], "active-set-ambiguous")
        self.assertEqual(active_only["11"]["metadata_resolution"], "metadata-not-found")
        self.assertNotIn("harness", active_only["11"])
        exact = {"20": {"pid": "20", "cmd": "cbmc", "attribution": "direct", "direct_harness": "crate::proof",
                        "metadata_path": "/target/libcrate.kani-metadata.json", "metadata_sha256": "c" * 64,
                        "metadata_group": "proof_harnesses", "metadata_match_count": 1, "metadata_file_count": 1,
                        "model_path": "/target/proof.out", "head_sha": "a" * 40, "kani_commit": "b" * 40,
                        "build_id": "build-2"},
                 "21": {"pid": "21", "cmd": "kissat", "ppid": "20", "active_at_peak": {"1": "other"}}}
        k.finalize_process_records(exact)
        self.assertEqual(exact["21"]["attribution"], "direct")
        self.assertEqual(exact["21"]["direct_harness"], "crate::proof")
        self.assertEqual(exact["21"]["parent_cbmc_pid"], "20")
        self.assertEqual(exact["21"]["metadata_sha256"], "c" * 64)

    def test_out_of_memory_status(self):
        # Kani's form for a CBMC killed by SIGKILL (seen in job 10): no time line, OOM text after the status.
        oom = (f"Checking harness {P}smoke::ok...\n\nCBMC failed\nVERIFICATION:- FAILED\n"
               "CBMC appears to have run out of memory. You may want to rerun your proof in an environment with "
               "additional memory or use stubbing to reduce the size of the code the verifier reasons about.\n")
        s = summ(oom + FAIL_BLOCK + tail(0, 2))
        self.assertEqual(s["status"], "COMPLETE")
        self.assertEqual(s["harnesses"][0]["status"], "OUT_OF_MEMORY")
        self.assertFalse(s["expectation_met"])
        self.assertIn("OUT_OF_MEMORY", k.render_md(s))
        req = req_with(harnesses=[{"name": P + "smoke::ok", "expect": "FAILED", "expect_check": "memory"}])
        self.assertFalse(summ(oom + tail(0, 1), req)["expectation_met"])

    def test_memcap(self):
        req = req_with(harnesses=ONLY_OK)
        log = OK_BLOCK + tail(1, 0)
        enforced = "state=ENFORCED\nmax_bytes=13958643712\nswap=off\npeak_bytes=4294967296\noom_kill=0\n"

        def run(text, tracked=True):
            return k.summarize(json.dumps(req), log, TIME, 0, "a" * 40, "b" * 40, None, {}, {}, "success",
                               text, tracked)
        s = run(enforced)
        self.assertTrue(s["measurement_ok"])
        self.assertEqual(s["resources"]["memcap"]["max_bytes"], 13958643712)
        self.assertIn("ENFORCED, limit 13.00 GiB, cgroup peak incl. page cache 4.00 GiB, OOM kills 0, swap off",
                      k.render_md(s))
        self.assertIsNone(run(None, tracked=False)["resources"]["memcap"])
        self.assertTrue(run(None, tracked=False)["measurement_ok"])
        for text, state in ((None, "MISSING"), ("state=UNAVAILABLE\nreason=no cgroup v2\n", "UNAVAILABLE"),
                            ("garbage", "UNPARSED")):
            s = run(text)
            self.assertEqual(s["resources"]["memcap"]["state"], state)
            self.assertFalse(s["measurement_ok"])
            self.assertTrue(any("memory cap" in n for n in s["notes"]))
        self.assertIn("no cgroup v2", " ".join(run("state=UNAVAILABLE\nreason=no cgroup v2\n")["notes"]))
        killed = run(enforced.replace("oom_kill=0", "oom_kill=1"))
        self.assertEqual(killed["status"], "INCONSISTENT")
        self.assertIn("cgroup OOM kills 1 differ from 0 OUT_OF_MEMORY harness(es)", killed["inconsistencies"])
        self.assertFalse(k.gate_ok(killed))
        swap_on = run(enforced.replace("swap=off", "swap=on"))
        self.assertFalse(swap_on["measurement_ok"])
        self.assertTrue(any("swap not confirmed off" in n for n in swap_on["notes"]))
        oom = (f"Checking harness {P}smoke::ok...\nVERIFICATION:- FAILED\n"
               "CBMC appears to have run out of memory. You may want more memory.\n")
        diag = req_with(kind="diagnostic", harnesses=ONLY_OK)

        def run_diag(text, log_text):
            return k.summarize(json.dumps(diag), log_text, TIME, 1, "a" * 40, "b" * 40, None, {}, {}, "success",
                               text, True)
        self.assertEqual(run_diag(enforced.replace("oom_kill=0", "oom_kill=1"), oom + tail(0, 1))["status"], "COMPLETE")
        # SIGKILL from outside the cgroup: Kani still says out of memory, the cgroup counted no OOM kill.
        self.assertEqual(run_diag(enforced, oom + tail(0, 1))["status"], "INCONSISTENT")
        self.assertEqual(run_diag(enforced.replace("oom_kill=0", "oom_kill=2"), oom + tail(0, 1))["status"], "INCONSISTENT")
        compile_oom = run_diag(enforced.replace("oom_kill=0", "oom_kill=1"), "error: could not compile `core`\n")
        self.assertEqual(compile_oom["status"], "RUNNER_ERROR")
        self.assertTrue(any("during compilation" in n for n in compile_oom["notes"]))
        diag = req_with(kind="diagnostic", harnesses=ONLY_OK)
        s = k.summarize(json.dumps(diag), log, TIME, 0, "a" * 40, "b" * 40, None, {}, {}, "success",
                        "state=UNAVAILABLE\n", True)
        self.assertTrue(k.gate_ok(s))

    def test_counts_line_with_extra_suffix(self):
        log = OK_BLOCK.replace("(2 unreachable)", "(2 unreachable, 1 undetermined)") + FAIL_BLOCK + tail(1, 1)
        self.assertEqual(summ(log)["harnesses"][0]["unreachable"], 2)
        log = OK_BLOCK.replace("(2 unreachable)", "(2 undetermined, 1 unreachable)") + FAIL_BLOCK + tail(1, 1)
        self.assertEqual(summ(log)["harnesses"][0]["unreachable"], 1)
        log = OK_BLOCK.replace("(2 unreachable)", "(2 undetermined)") + FAIL_BLOCK + tail(1, 1)
        self.assertIsNone(summ(log)["harnesses"][0]["unreachable"])
        self.assertEqual(summ(GOOD_LOG)["harnesses"][1]["unreachable"], 0)

    def test_should_panic_success(self):
        req = req_with(harnesses=ONLY_OK)
        log = OK_BLOCK.replace("SUCCESSFUL", "SUCCESSFUL (encountered one or more panics as expected)") + tail(1, 0)
        s = summ(log, req, exit_code=0)
        self.assertEqual(s["harnesses"][0]["status"], "SUCCESS")
        self.assertTrue(k.gate_ok(s))

    def test_cross_checks_make_inconsistent(self):
        s = summ(OK_BLOCK + FAIL_BLOCK)  # no Complete line
        self.assertEqual(s["status"], "INCONSISTENT")
        self.assertFalse(k.gate_ok(s))
        s = summ(OK_BLOCK + FAIL_BLOCK + tail(2, 1))
        self.assertEqual(s["status"], "INCONSISTENT")
        req = req_with(harnesses=ONLY_OK)
        s = summ(OK_BLOCK + tail(1, 0), req, exit_code=137)
        self.assertEqual(s["status"], "INCONSISTENT")
        s = summ(GOOD_LOG, exit_code=0)
        self.assertEqual(s["status"], "INCONSISTENT")
        s = summ(GOOD_LOG, exit_code=None)
        self.assertEqual(s["status"], "INCONSISTENT")
        extra = OK_BLOCK + FAIL_BLOCK + f"Checking harness {P}other::h...\nVERIFICATION:- SUCCESSFUL\nVerification Time: 1s\n" + tail(2, 1)
        s = summ(extra)
        self.assertEqual(s["unrequested_blocks"], [P + "other::h"])
        self.assertEqual(s["status"], "INCONSISTENT")
        s = summ(OK_BLOCK + OK_BLOCK + FAIL_BLOCK + tail(1, 1))
        self.assertEqual(s["status"], "INCONSISTENT")

    def test_timeout_detection_is_exact(self):
        log = OK_BLOCK + f"Checking harness {P}smoke::control...\nCBMC timed out. You may want to rerun your proof with a larger timeout\nVERIFICATION:- FAILED\n" + tail(1, 1)
        s = summ(log)
        self.assertEqual(s["harnesses"][1]["status"], "TIMEOUT")
        self.assertFalse(s["expectation_met"])
        prose = FAIL_BLOCK.replace("assertion failed: has_efficient", "assertion failed: request timed out has_efficient")
        s = summ(OK_BLOCK + prose + tail(1, 1))
        self.assertEqual(s["harnesses"][1]["status"], "FAILED")
        trailing = GOOD_LOG + "note: some other job timed out\n"
        self.assertEqual(summ(trailing)["harnesses"][1]["status"], "FAILED")

    def test_partial_and_unknown(self):
        s = summ(OK_BLOCK + tail(1, 0))
        self.assertEqual(s["status"], "PARTIAL")
        self.assertEqual(s["harnesses"][1]["status"], "NOT_RUN")
        s = summ(OK_BLOCK + f"Checking harness {P}smoke::control...\nKilled\n")
        self.assertEqual(s["harnesses"][1]["status"], "UNKNOWN")
        self.assertEqual(s["status"], "PARTIAL")

    def test_no_harness_output_classification(self):
        rustc = "   Compiling core v0.0.0\nerror[E0599]: no method named `clone` found\n  --> library/core/src/x.rs:1:1\nerror: could not compile `core`\n"
        s = summ(rustc)
        self.assertEqual(s["status"], "COMPILE_ERROR")
        self.assertTrue(any("E0599" in line for line in s["errors"]))
        self.assertTrue(all(h["status"] == "NOT_RUN" for h in s["harnesses"]))
        self.assertEqual(summ("error: unexpected argument '--harness-timeout' found\n")["status"], "TOOL_ERROR")
        s = summ("time: illegal option -- o\n", exit_code=1)
        self.assertEqual(s["status"], "RUNNER_ERROR")

    def test_missing_log_and_invalid_request(self):
        s = summ(None, build_outcome="failure")
        self.assertEqual(s["status"], "RUNNER_ERROR")
        self.assertTrue(any("Kani build failed" in n for n in s["notes"]))
        self.assertFalse(k.gate_ok(s))
        self.assertEqual(k.summarize("{not json", OK_BLOCK, TIME, 0, None, None)["status"], "REQUEST_INVALID")
        self.assertEqual(summ(OK_BLOCK, request_error="validate step failed")["status"], "REQUEST_INVALID")
        self.assertEqual(k.summarize(None, OK_BLOCK, TIME, 0, None, None)["status"], "REQUEST_INVALID")

    def test_build_outcome_notes(self):
        for outcome, needle in (("deps-failure", "dependencies"), ("not-started", "before request validation"),
                                ("failure", "Kani build failed"), ("verify-skipped", "job cap")):
            s = summ(None, build_outcome=outcome)
            self.assertEqual(s["status"], "RUNNER_ERROR")
            self.assertTrue(any(needle in n for n in s["notes"]), (outcome, s["notes"]))

    def test_time_file_formats(self):
        self.assertEqual(summ(GOOD_LOG, time=None)["resources"]["time_file"], "MISSING")
        self.assertEqual(summ(GOOD_LOG, time="garbage")["resources"]["time_file"], "UNPARSED")
        mac = "      301.52 real       290.10 user         5.33 sys\n  8589934592  maximum resident set size\n"
        res = summ(GOOD_LOG, time=mac)["resources"]
        self.assertEqual((res["max_rss_kb_whole_run"], res["wall_whole_run"], res["time_file"]), (8388608, "301.52s", "PARSED"))

    def test_bounds_and_truncation(self):
        many = "".join(f"Failed Checks: check {i} " + "x" * 600 + "\n" for i in range(30))
        log = OK_BLOCK + f"Checking harness {P}smoke::control...\n{many}VERIFICATION:- FAILED\nVerification Time: 1s\n" + tail(1, 1)
        row = summ(log)["harnesses"][1]
        self.assertEqual(len(row["failed_checks"]), k.MAX_FAILED_CHECKS)
        self.assertTrue(row["failed_checks_truncated"])
        self.assertTrue(all(len(c["description"]) <= k.MAX_LINE_CHARS + 20 for c in row["failed_checks"]))
        s = summ("".join(f"error: e{i}\n" for i in range(200)))
        self.assertEqual(len(s["errors"]), k.MAX_ERROR_LINES)
        self.assertTrue(s["errors_truncated"])
        self.assertLessEqual(len(k.render_md(summ(log)).encode()), k.MAX_MD_BYTES)

    def test_file_bindings(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "x"
            f.write_bytes(b"abc")
            b = k.file_bindings([str(f), str(Path(d) / "missing")])
            self.assertEqual(b[str(f)], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
            self.assertEqual(b[str(Path(d) / "missing")], "MISSING")


RES_REQ = {**REQ, "kind": "resource", "runner": "gcb-e2-highmem-4", "harness_timeout_minutes": 720, "harnesses": ONLY_OK}
PEAKS = ("interval_ms=2000\nsamples=300\nelapsed_s=598\ntotal_rss_peak_kb=22020096\n"
         "cmd=cbmc peak_kb=1048576 first_s=500 last_s=598\n"
         "cmd=goto-instrument peak_kb=20971520 first_s=120 last_s=480\n"
         "cmd=kani-compiler peak_kb=1572864 first_s=2 last_s=110\n")


class ResourceLaneTests(unittest.TestCase):
    def bad(self, req, needle):
        with self.assertRaises(k.RequestError) as cm:
            k.validate_request(req)
        self.assertIn(needle, str(cm.exception))

    def test_kind_and_runner_pair(self):
        k.validate_request(copy.deepcopy(RES_REQ))
        self.bad({**RES_REQ, "runner": "circleci-linux-large"}, "kind resource")
        self.bad({**RES_REQ, "kind": "measurement", "harness_timeout_minutes": 10}, "kind resource")
        self.bad({**RES_REQ, "kind": "diagnostic"}, "kind resource")
        self.bad({**RES_REQ, "harness_timeout_minutes": 721}, "1..720")
        self.bad({**REQ, "kind": "diagnostic", "harness_timeout_minutes": 31}, "1..30")
        self.bad({**RES_REQ, "harnesses": [{"name": P + f"h{i}", "expect": "SUCCESS"} for i in range(2)]}, "exceeds 720")

    def test_resource_caps_agree(self):
        # k1g.sh dispatch, gcb-k1.sh and kani_k1.py must allow the same resource total, or dispatch rejects
        # requests the lane would run (or the reverse).
        here = Path(__file__).resolve().parent
        k1g = (here / "k1g.sh").read_text()
        gcb = (here / "gcb-k1.sh").read_text()
        self.assertIn(f"RESOURCE_MAX_TOTAL_MINUTES={k.RESOURCE_MAX_TIMEOUT_MINUTES}", k1g)
        self.assertIn('--max-total-minutes "$RESOURCE_MAX_TOTAL_MINUTES"', k1g)
        self.assertIn(f"MAX_TOTAL_MINUTES={k.RESOURCE_MAX_TIMEOUT_MINUTES}", gcb)

    def test_gcb_inventory_uses_kani_list_generated_json_file(self):
        gcb = (Path(__file__).resolve().parent / "gcb-k1.sh").read_text()
        self.assertIn('"$PWD/kani_build/scripts/kani" list $unstable_args ./library --std --format json', gcb)
        self.assertNotIn('list $unstable_args ./library --std --format json >', gcb)
        self.assertIn("test -s kani-list.json", gcb)
        self.assertIn("--listing kani-list.json", gcb)
        self.assertIn('Path("kani-list.json").unlink(missing_ok=True)', gcb)

    def run_res(self, log, peaks=PEAKS, tracked=True, exit_code=0):
        return k.summarize(json.dumps(RES_REQ), log, TIME, exit_code, "a" * 40, "b" * 40, None, {}, {}, "success",
                           None, False, peaks, tracked)

    def test_resource_summary(self):
        s = self.run_res(OK_BLOCK + tail(1, 0))
        self.assertEqual(s["status"], "COMPLETE")
        self.assertIsNone(s["measurement_ok"])
        self.assertTrue(k.gate_ok(s))
        self.assertTrue(any("never a PASS" in n for n in s["notes"]))
        peaks = s["resources"]["peaks"]
        self.assertEqual(peaks["state"], "PARSED")
        self.assertEqual([c["cmd"] for c in peaks["commands"]], ["goto-instrument", "kani-compiler", "cbmc"])
        md = k.render_md(s)
        self.assertIn("`goto-instrument` 20.00 GiB (>16 GB), seen 120–480 s", md)
        self.assertIn("`kani-compiler` 1.50 GiB (≤13 GiB)", md)
        self.assertIn("largest sampled sum of RSS 21.00 GiB", md)
        self.assertIsNone(summ(OK_BLOCK + tail(1, 0), req_with(harnesses=ONLY_OK))["resources"]["peaks"])

    def test_peaks_missing_or_garbage(self):
        for text, state in ((None, "MISSING"), ("garbage\n", "UNPARSED")):
            s = self.run_res(OK_BLOCK + tail(1, 0), text)
            self.assertEqual(s["resources"]["peaks"]["state"], state)
            self.assertTrue(any("memory peaks" in n for n in s["notes"]))
        many = "samples=1\n" + "".join(f"cmd=p{i} peak_kb={i} first_s=0 last_s=0\n" for i in range(20))
        many += "cmd=bad peak_kb=x first_s=0 last_s=0\n"
        peaks = k.parse_peaks(many)
        self.assertEqual(len(peaks["commands"]), k.PEAKS_TOP)
        self.assertTrue(peaks["commands_truncated"])
        self.assertEqual(peaks["commands"][0]["cmd"], "p19")

    def test_extended_peak_timestamps_and_sampler_records_are_bounded(self):
        text = ("interval_ms=2000\nsamples=2\nelapsed_s=2\ntotal_rss_peak_kb=300\ntotal_peak_s=2\n"
                "cmd=cbmc peak_kb=200 first_s=0 last_s=2 peak_s=2\n")
        parsed = k.parse_peaks(text)
        self.assertEqual(parsed["total_peak_s"], 2)
        self.assertEqual(parsed["commands"][0]["peak_s"], 2)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            proc = root / "proc"
            out = root / "peaks.txt"
            log = root / "kani.log"
            for pid, name, rss in (("100", "cbmc", "2048"), ("101", "kani-driver", "1024")):
                directory = proc / pid
                directory.mkdir(parents=True)
                (directory / "status").write_text(f"Name:\t{name}\nVmRSS:\t{rss} kB\nVmHWM:\t{rss} kB\n")
                (directory / "cmdline").write_bytes(("kani " + P + "heavy").encode() if name == "cbmc" else b"")
            log.write_text(f"Checking harness {P}heavy...\n")
            k.sample_memory(out, 0.01, 0.04, proc=proc, log=log)
            saved = out.read_text()
            self.assertIn("total_peak_s=", saved)
            self.assertIn("cmd=cbmc peak_kb=2048", saved)
            self.assertIn("cbmc_pid=100", saved)
            self.assertIn("driver_s=", saved)
            self.assertIn("harness_s=", saved)
            self.assertLess(len(saved), 8000)

    def test_time_rss_above_sampled_peak(self):
        big = "\tMaximum resident set size (kbytes): 25165824\n"
        s = k.summarize(json.dumps(RES_REQ), OK_BLOCK + tail(1, 0), big, 0, "a" * 40, "b" * 40, None, {}, {},
                        "success", None, False, PEAKS, True)
        self.assertTrue(any("grew between samples" in n for n in s["notes"]))
        self.assertFalse(any("grew between samples" in n for n in self.run_res(OK_BLOCK + tail(1, 0))["notes"]))

    def test_ledger(self):
        builds = [
            {"id": "a", "startTime": "2026-10-26T10:00:00Z", "finishTime": "2026-10-26T10:10:01.5Z", "timeout": "2400s"},
            {"id": "b", "finishTime": "2026-10-26T10:00:00Z", "timeout": "5400s"},          # cancelled while queued
            {"id": "c", "startTime": "2026-10-26T11:00:00Z", "timeout": "5400s"},           # running
            {"id": "d", "timeout": "600.5s"},                                               # queued
        ]
        self.assertEqual(k.ledger(builds), (4, 11, 90 + 11))
        self.assertEqual(k.ledger([]), (0, 0, 0))
        for bad in ({"id": "x"}, {"id": "x", "timeout": "90m"}, {"id": "x", "timeout": 5400}):
            with self.assertRaises(ValueError):
                k.ledger([bad])
        with self.assertRaises(ValueError):
            k.ledger({"builds": []})
        cli = subprocess.run([sys.executable, "-B", str(Path(k.__file__)), "ledger"], input=json.dumps(builds),
                             capture_output=True, text=True)
        self.assertEqual(cli.stdout.split(), ["4", "11", "101"])
        bad = subprocess.run([sys.executable, "-B", str(Path(k.__file__)), "ledger"], input='[{"id": "x"}]',
                             capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, "")

    def test_ledger_priced_by_pool(self):
        hi, std = "projects/p/locations/r/workerPools/k1-highmem4", "projects/p/locations/r/workerPools/k1-standard4"
        builds = [
            {"id": "a", "startTime": "2026-10-26T10:00:00Z", "finishTime": "2026-10-26T10:10:00Z", "options": {"pool": {"name": hi}}},
            {"id": "b", "startTime": "2026-10-27T10:00:00Z", "finishTime": "2026-10-27T10:20:00Z", "options": {"pool": {"name": std}}},
            {"id": "c", "timeout": "1800s", "options": {"pool": {"name": std}}},
        ]
        n, used, reserved = k.ledger(builds, {hi: 0.03, std: 0.02})
        self.assertEqual(n, 3)
        self.assertAlmostEqual(used, 10 * 0.03 + 20 * 0.02)
        self.assertAlmostEqual(reserved, 30 * 0.02)
        for bad in ({"id": "x", "timeout": "60s"}, {"id": "x", "timeout": "60s", "options": {"pool": {"name": "other"}}}):
            with self.assertRaises(ValueError):
                k.ledger([bad], {hi: 0.03})
        cli = subprocess.run([sys.executable, "-B", str(Path(k.__file__)), "ledger", "--price", f"{hi}=0.03",
                              "--price", f"{std}=0.02"], input=json.dumps(builds), capture_output=True, text=True)
        self.assertEqual(cli.stdout.split(), ["3", "0.7000", "0.6000"])
        for price in ("x=0", "=0.1", f"{hi}=abc"):
            bad = subprocess.run([sys.executable, "-B", str(Path(k.__file__)), "ledger", "--price", price],
                                 input="[]", capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2, price)

    def test_ledger_selected_ids_and_unreadable_reservation(self):
        highmem, standard = "highmem", "standard"
        builds = [
            {"id": "a", "startTime": "2026-10-26T10:00:00Z", "finishTime": "2026-10-26T10:10:00Z",
             "options": {"pool": {"name": highmem}}},
            {"id": "b", "timeout": "120s", "options": {"pool": {"name": standard}}},
            {"id": "other", "timeout": "bad", "options": {"pool": {"name": "unpriced"}}},
        ]
        prices = {highmem: 0.03, standard: 0.02}
        self.assertEqual(k.ledger_selected(builds, ["a", "b"], prices), (2, 0.3, 0.04))
        for ids, rows, needle in ((["missing"], builds, "found 0 times"), (["a", "a"], builds, "unique"),
                                  (["b"], [builds[1] | {"timeout": None}], "unreadable timeout")):
            with self.assertRaises(ValueError) as cm:
                k.ledger_selected(rows, ids, prices)
            self.assertIn(needle, str(cm.exception))
        command = [sys.executable, "-B", str(Path(k.__file__)), "ledger", "--price", "highmem=0.03",
                   "--price", "standard=0.02", "--id", "a", "--id", "b"]
        cli = subprocess.run(command, input=json.dumps(builds[:2]), capture_output=True, text=True)
        self.assertEqual(cli.returncode, 0)
        self.assertEqual(cli.stdout.split(), ["2", "0.3000", "0.0400"])
        for args, source in ((["--id", "missing"], builds), (["--id", "a", "--id", "a"], builds),
                             (["--id", "b"], [{**builds[1], "timeout": "unreadable"}])):
            bad = subprocess.run(command[:command.index("--id")] + args,
                                 input=json.dumps(source), capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2)
            self.assertNotEqual(bad.stderr, "")

    def test_inventory_extract_page_and_binding(self):
        req = {**REQ, "runner": k.STANDARD_RUNNER, "kind": "diagnostic", "inventory": True}
        request_text = json.dumps(req)
        listing = {"file-version": "0.1", "standard-harnesses": {"core": [P + "proof::one", "other::h"]},
                   "contract-harnesses": {"core": [P + "proof::two"]}}
        names = k.extract_inventory(listing)
        self.assertEqual(names, [P + "proof::one", P + "proof::two"])
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "inventory.txt"
            k.write_inventory(listing, request_text, "a" * 40, "c" * 40, "build-1", path)
            summary = {"request": {"request_id": req["request_id"], "inventory": True},
                       "request_sha256": __import__("hashlib").sha256(request_text.encode()).hexdigest(),
                       "run": {"id": "build-1"}, "head_sha": "a" * 40, "kani_commit": "c" * 40}
            page = k.inventory_page(path.read_text(), summary, 1, 1)
            self.assertIn("total=2", page)
            self.assertIn("next_offset=done", page)
            self.assertIn("proof::two", page)
            self.assertIn("request_sha256=", page)
            with self.assertRaises(ValueError):
                k.inventory_page(path.read_text(), {**summary, "request_sha256": "wrong"}, 0, 1)
        summary_data = {"request": {"request_id": "x"}, "request_sha256": "hash", "head_sha": "head",
                        "run": {"id": "build"}, "harnesses": [
                            {"name": P + "proof::one", "status": "SUCCESS", "time_s": 2.0,
                             "checks_failed": 0, "checks_total": 3, "covers_satisfied": 2, "covers_total": 2},
                            {"name": P + "proof::two", "status": "TIMEOUT", "time_s": 10.0,
                             "checks_failed": None, "checks_total": None, "covers_satisfied": None,
                             "covers_total": None}]}
        page = k.summary_page(summary_data, 1, 1)
        self.assertIn("request_sha256=hash", page)
        self.assertIn("TIMEOUT\t10.0", page)
        self.assertIn("next_offset=done", page)
        with self.assertRaises(ValueError):
            k.summary_page(summary_data, 0, 81)

    def test_standard_pool_runner(self):
        std = {**REQ, "runner": k.STANDARD_RUNNER, "harnesses": ONLY_OK}
        k.validate_request(copy.deepcopy(std))
        k.validate_request({**std, "kind": "diagnostic", "harness_timeout_minutes": 30})
        self.bad({**std, "kind": "resource", "harness_timeout_minutes": 60}, "kind resource")
        # A lane cap above the kind's own never raises it.
        many = {**std, "kind": "diagnostic", "harness_timeout_minutes": 30,
                "harnesses": [{"name": P + f"h{i}", "expect": "SUCCESS"} for i in range(6)]}
        with self.assertRaises(k.RequestError) as cm:
            k.validate_request(many, 720)
        self.assertIn("exceeds 150", str(cm.exception))
        with self.assertRaises(k.RequestError):
            k.validate_request({**REQ, "harnesses": [{"name": P + f"h{i}", "expect": "SUCCESS"} for i in range(5)]}, 40)

    def test_kani_jobs(self):
        diag = {**REQ, "runner": k.STANDARD_RUNNER, "kind": "diagnostic", "harnesses": ONLY_OK}
        self.assertIn("--jobs=1", k.kani_args(k.validate_request(copy.deepcopy(diag))))
        self.assertIn("--jobs=2", k.kani_args(k.validate_request({**diag, "kani_jobs": 2})))
        self.assertIn("--jobs=1", k.kani_args(k.validate_request({**REQ, "kani_jobs": 1})))
        self.assertIn("--jobs=3", k.kani_args(k.validate_request({**diag, "kani_jobs": 3})))
        self.bad({**diag, "kani_jobs": True}, "kani_jobs must be")
        self.bad({**diag, "kind": "measurement", "kani_jobs": 2}, "only for kind diagnostic")
        self.bad({**diag, "runner": "circleci-linux-large", "kani_jobs": 2}, "only for kind diagnostic")
        self.bad({**diag, "jobs": 2}, "unknown request keys")
        s = k.summarize(json.dumps({**diag, "kani_jobs": 2}), OK_BLOCK + tail(1, 0), TIME, 0, "a" * 40, "b" * 40,
                        None, {}, {}, "success")
        self.assertEqual(s["request"]["kani_jobs"], 2)
        self.assertTrue(any("concurrently" in n for n in s["notes"]))
        self.assertIn("harnesses in parallel 2", k.render_md(s))

    def test_diagnostic_harness_cap_is_standard_pool_only_and_budgeted(self):
        entries = [{"name": P + f"h{i}", "expect": "SUCCESS"} for i in range(80)]
        req = {**REQ, "runner": k.STANDARD_RUNNER, "kind": "diagnostic", "harness_timeout_minutes": 1,
               "harnesses": entries}
        k.validate_request(req)
        with self.assertRaises(k.RequestError):
            k.validate_request({**req, "runner": "ubuntu-latest"})
        with self.assertRaises(k.RequestError):
            k.validate_request({**req, "harness_timeout_minutes": 2})
        with self.assertRaises(k.RequestError):
            k.validate_request({**req, "harnesses": entries + [{"name": P + "h80", "expect": "SUCCESS"}]})
        partition = {**req, "kind": "partition", "harnesses": [], "worker_index": 1, "worker_total": 2,
                     "kani_jobs": 3}
        with self.assertRaises(k.RequestError):
            k.validate_request(partition)

    def test_machine_memcap_gates_measurement_on_swap(self):
        std = {**REQ, "runner": k.STANDARD_RUNNER, "harnesses": ONLY_OK}

        def run(memcap):
            return k.summarize(json.dumps(std), OK_BLOCK + tail(1, 0), TIME, 0, "a" * 40, "b" * 40, None, {}, {},
                               "success", memcap, True)
        ok = run("state=MACHINE\nmax_bytes=17179869184\nswap=off\nreason=Cloud Build pool, no cgroup cap\n")
        self.assertTrue(ok["measurement_ok"])
        self.assertTrue(k.gate_ok(ok))
        self.assertIn("MACHINE (no cgroup cap; the machine's memory 16.00 GiB is the limit), swap off", k.render_md(ok))
        self.assertFalse(any("verify memory cap" in n for n in ok["notes"]))
        swap = run("state=MACHINE\nmax_bytes=17179869184\nswap=on (SwapTotal 2097148 kB)\n")
        self.assertFalse(swap["measurement_ok"])
        self.assertFalse(k.gate_ok(swap))
        self.assertTrue(any("swap not confirmed off" in n for n in swap["notes"]))
        self.assertFalse(run(None)["measurement_ok"])          # tracked but missing

    def test_worker_prefixed_output_under_kani_jobs(self):
        # Shape of Cloud Build run 22e18888 (kani_jobs=2): every line carries its worker prefix.
        real = (f"Thread 0: Checking harness {P}smoke::control...\n"
                f"Thread 1: Checking harness {P}smoke::ok...\n"
                "Thread 0: \nThread 0: VERIFICATION RESULT:\nThread 0:  ** 1 of 3 failed\n"
                "Thread 0: Failed Checks: assertion failed: has_efficient_in_place_swap::<[u8; 9]>()\n"
                'Thread 0:  File: "library/core/src/slice/sort/shared/smallsort/kani_k1/smoke.rs", line 20, in control\n'
                "Thread 0: \nThread 0: VERIFICATION:- FAILED\nThread 0: Verification Time: 0.03475437s\n\n"
                "Thread 1: \nThread 1: VERIFICATION RESULT:\nThread 1:  ** 0 of 12 failed (2 unreachable)\nThread 1: \n"
                "Thread 1:  ** 2 of 2 cover properties satisfied\nThread 1: \nThread 1: VERIFICATION:- SUCCESSFUL\n"
                "Thread 1: Verification Time: 0.04272855s\n\nManual Harness Summary:\n"
                f"Verification failed for - {P}smoke::control\n"
                "Complete - 1 successfully verified harnesses, 1 failures, 2 total.\n")
        diag = {**REQ, "runner": k.STANDARD_RUNNER, "kind": "diagnostic", "kani_jobs": 2}

        def run(log):
            return k.summarize(json.dumps(diag), log, TIME, 1, "a" * 40, "b" * 40, None, {}, {}, "success")
        s = run(real)
        self.assertEqual(s["status"], "COMPLETE", s["inconsistencies"])
        self.assertTrue(k.gate_ok(s))
        ok, control = s["harnesses"]
        self.assertEqual((ok["status"], ok["time_s"], ok["covers_satisfied"], ok["unreachable"]), ("SUCCESS", 0.04272855, 2, 2))
        self.assertEqual((control["status"], control["failed_located"]), ("FAILED", 1))
        self.assertTrue(control["failed_checks"][0]["location"].endswith("smoke.rs:20"))
        # A worker that starts a second harness inside its open block breaks attribution.
        broken = real.replace("Thread 0: Verification Time: 0.03475437s\n", f"Thread 0: Checking harness {P}smoke::x...\n")
        b = run(broken)
        self.assertTrue(any("interleaved" in i for i in b["inconsistencies"]))
        self.assertFalse(k.gate_ok(b))
        # An unprefixed result line while a worker block is open cannot be attributed: fail closed.
        orphan = real.replace("Thread 1: VERIFICATION:- SUCCESSFUL\n", "CBMC timed out. You may want to rerun\n"
                              "Thread 1: VERIFICATION:- SUCCESSFUL\n")
        o = run(orphan)
        self.assertTrue(any("without a worker prefix" in i for i in o["inconsistencies"]))
        self.assertFalse(k.gate_ok(o))
        # Sequential (unprefixed) output is unchanged.
        self.assertEqual(run(GOOD_LOG)["status"], "COMPLETE")

    def test_ledger_price_must_be_finite(self):
        for price in ("p=nan", "p=inf", "p=-1"):
            bad = subprocess.run([sys.executable, "-B", str(Path(k.__file__)), "ledger", "--price", price],
                                 input="[]", capture_output=True, text=True)
            self.assertEqual(bad.returncode, 2, price)

    def test_uninit_checks(self):
        diag = {**REQ, "runner": k.STANDARD_RUNNER, "kind": "diagnostic", "harnesses": ONLY_OK}
        args = k.kani_args(k.validate_request({**diag, "uninit_checks": True}))
        self.assertEqual(args[args.index("-Z") + 1], "uninit-checks")
        self.assertNotIn("uninit-checks", k.kani_args(k.validate_request(copy.deepcopy(diag))))
        self.assertNotIn("uninit-checks", k.kani_args(k.validate_request({**REQ, "uninit_checks": False})))
        self.bad({**diag, "uninit_checks": 1}, "true or false")
        self.bad({**diag, "kind": "measurement", "uninit_checks": True}, "only for kind diagnostic")
        self.bad({**diag, "runner": "circleci-linux-large", "uninit_checks": True}, "only for kind diagnostic")
        s = k.summarize(json.dumps({**diag, "uninit_checks": True}), OK_BLOCK + tail(1, 0), TIME, 0, "a" * 40,
                        "b" * 40, None, {}, {}, "success")
        self.assertTrue(s["request"]["uninit_checks"])
        self.assertTrue(any("outside CI" in n for n in s["notes"]))
        self.assertIn("uninit checks on", k.render_md(s))

    def test_valid_value_checks(self):
        diag = {**REQ, "runner": k.STANDARD_RUNNER, "kind": "diagnostic", "harnesses": ONLY_OK}
        args = k.kani_args(k.validate_request({**diag, "valid_value_checks": True}))
        self.assertEqual(args[args.index("-Z") + 1], "valid-value-checks")
        both = k.kani_args(k.validate_request({**diag, "uninit_checks": True, "valid_value_checks": True}))
        self.assertIn("uninit-checks", both)
        self.assertIn("valid-value-checks", both)
        self.assertNotIn("valid-value-checks", k.kani_args(k.validate_request(copy.deepcopy(diag))))
        self.assertNotIn("valid-value-checks", k.kani_args(k.validate_request({**REQ, "valid_value_checks": False})))
        self.bad({**diag, "valid_value_checks": 1}, "true or false")
        self.bad({**diag, "kind": "measurement", "valid_value_checks": True}, "only for kind diagnostic")
        self.bad({**diag, "runner": "circleci-linux-large", "valid_value_checks": True}, "only for kind diagnostic")
        s = k.summarize(json.dumps({**diag, "valid_value_checks": True}), OK_BLOCK + tail(1, 0), TIME, 0, "a" * 40,
                        "b" * 40, None, {}, {}, "success")
        self.assertTrue(s["request"]["valid_value_checks"])
        self.assertTrue(any("valid-value-checks on" in n for n in s["notes"]))
        self.assertIn("valid-value checks on", k.render_md(s))

    def test_controls_cfg(self):
        std = {**REQ, "runner": k.STANDARD_RUNNER, "harnesses": ONLY_OK}
        k.validate_request({**std, "controls": True})
        k.validate_request({**std, "kind": "diagnostic", "controls": True})
        self.bad({**std, "controls": "yes"}, "true or false")
        self.bad({**REQ, "controls": True}, "only for runner")
        self.assertNotIn("kani_smallsort_controls", " ".join(k.kani_args(k.validate_request({**std, "controls": True}))))
        with tempfile.TemporaryDirectory() as d:
            req, args, rf = Path(d) / "r.json", Path(d) / "a.txt", Path(d) / "rf.txt"
            for controls, want in ((True, "--cfg kani_smallsort_controls"), (False, ""), (None, "")):
                body = dict(std) if controls is None else {**std, "controls": controls}
                req.write_text(json.dumps(body))
                cli = subprocess.run([sys.executable, "-B", str(Path(k.__file__)), "validate", str(req), "--args-out",
                                      str(args), "--rustflags-out", str(rf)], capture_output=True, text=True)
                self.assertEqual(cli.returncode, 0, cli.stderr)
                self.assertEqual(rf.read_text(), want + "\n")
        s = k.summarize(json.dumps({**std, "controls": True}), OK_BLOCK + tail(1, 0), TIME, 0, "a" * 40, "b" * 40,
                        None, {}, {}, "success")
        self.assertTrue(s["request"]["controls"])
        self.assertTrue(any("outside the CI set" in n for n in s["notes"]))
        self.assertIn("controls cfg on", k.render_md(s))
        core = (Path(__file__).resolve().parents[4] / "library/core/Cargo.toml").read_text()
        self.assertIn(f"'cfg({k.CONTROLS_CFG})'", core)

    def test_partition_kind(self):
        part = {**REQ, "kind": "partition", "runner": k.STANDARD_RUNNER, "harnesses": [], "harness_timeout_minutes": 180,
                "worker_index": 2, "worker_total": 4, "kani_jobs": 2}
        k.validate_request(copy.deepcopy(part))
        self.assertEqual(k.partition_env(part), ["WORKER_INDEX=2", "WORKER_TOTAL=4", "KANI_JOBS=2"])
        mac = {**part, "runner": "macos-latest"}
        del mac["kani_jobs"]
        k.validate_request(copy.deepcopy(mac))
        self.assertEqual(k.partition_env(mac), ["WORKER_INDEX=2", "WORKER_TOTAL=4"])
        self.assertEqual(k.partition_env({**REQ}), [])
        self.bad({**part, "runner": "circleci-linux-large"}, "kind partition runs only")
        self.bad({**part, "worker_index": 5}, "worker_index")
        self.bad({k2: v for k2, v in part.items() if k2 != "worker_total"}, "worker_index")
        self.bad({**part, "harnesses": ONLY_OK}, "harnesses: []")
        self.bad({**part, "controls": True}, "no valid_value_checks, no controls")
        self.bad({**part, "harness_timeout_minutes": 301}, "1..300")
        self.bad({**REQ, "worker_index": 1, "worker_total": 4}, "only for kind partition")
        other = "core::num::verify::checked_add_u8"

        def log(blocks, total=None, ok=None):
            body = "".join(blocks)
            n = total if total is not None else len(blocks)
            return body + tail(ok if ok is not None else n, n - (ok if ok is not None else n))
        ok_other = OK_BLOCK.replace(f"{P}smoke::ok", other)

        def hdr(*names):
            return "Running verification for harnesses:\n" + "".join(n + "\n" for n in names) + "Compiling core\n"
        s = k.summarize(json.dumps(part), hdr(P + "smoke::ok", other) + "Thread 0: " + OK_BLOCK.replace("\n", "\nThread 0: ").rstrip("Thread 0: ")
                        + "\n" + ok_other + tail(2, 0), TIME, 0, "a" * 40, "b" * 40, None, {}, {}, "success")
        self.assertEqual(s["status"], "COMPLETE", s["inconsistencies"])
        self.assertTrue(k.gate_ok(s))
        self.assertEqual(s["partition"]["harness_count"], 2)
        self.assertEqual(s["partition"]["smallsort_kani_k1_count"], 1)
        self.assertIn("Partition 2/4", k.render_md(s))
        f = k.summarize(json.dumps(part), hdr(other, P + "smoke::control") + ok_other + FAIL_BLOCK + tail(1, 1), TIME, 1, "a" * 40, "b" * 40, None, {},
                        {}, "success")
        self.assertEqual(f["status"], "COMPLETE")
        self.assertFalse(k.gate_ok(f))
        self.assertEqual(f["partition"]["failures"][0]["name"], P + "smoke::control")
        self.assertIn("Not SUCCESS", k.render_md(f))
        cut = k.summarize(json.dumps(part), hdr(other) + ok_other, TIME, 124, "a" * 40, "b" * 40, None, {}, {}, "success")
        self.assertEqual(cut["status"], "PARTIAL")
        self.assertFalse(k.gate_ok(cut))
        short = k.summarize(json.dumps(part), hdr(other, P + "smoke::ok") + ok_other + tail(1, 0), TIME, 0,
                            "a" * 40, "b" * 40, None, {}, {}, "success")
        self.assertTrue(any("assigned 2 harnesses but 1" in i for i in short["inconsistencies"]))
        self.assertFalse(k.gate_ok(short))
        nolist = k.summarize(json.dumps(part), ok_other + tail(1, 0), TIME, 0, "a" * 40, "b" * 40, None, {}, {}, "success")
        self.assertTrue(any("worker harness list missing" in i for i in nolist["inconsistencies"]))
        with self.assertRaises(k.RequestError):
            k.validate_request(copy.deepcopy(part), 120)
        self.assertEqual(k.summarize(json.dumps(part), None, TIME, None, "a" * 40, "b" * 40, None, {}, {},
                                     "failure")["status"], "RUNNER_ERROR")
        with tempfile.TemporaryDirectory() as d:
            req, args, pe = Path(d) / "r.json", Path(d) / "a.txt", Path(d) / "p.env"
            req.write_text(json.dumps(part))
            cli = subprocess.run([sys.executable, "-B", str(Path(k.__file__)), "validate", str(req), "--args-out",
                                  str(args), "--partition-out", str(pe), "--max-total-minutes", "720"],
                                 capture_output=True, text=True)
            self.assertEqual(cli.returncode, 0, cli.stderr)
            self.assertEqual(pe.read_text(), "WORKER_INDEX=2\nWORKER_TOTAL=4\nKANI_JOBS=2\n")

    def test_require_runner_repeatable(self):
        with tempfile.TemporaryDirectory() as d:
            req, args = Path(d) / "r.json", Path(d) / "a.txt"
            for runner, rc in ((k.STANDARD_RUNNER, 0), ("circleci-linux-large", 2)):
                req.write_text(json.dumps({**REQ, "runner": runner, "harnesses": ONLY_OK}))
                cli = subprocess.run([sys.executable, "-B", str(Path(k.__file__)), "validate", str(req), "--args-out",
                                      str(args), "--require-runner", k.RESOURCE_RUNNER, "--require-runner",
                                      k.STANDARD_RUNNER], capture_output=True, text=True)
                self.assertEqual(cli.returncode, rc, cli.stderr)

    def test_tool_killed_before_harness_output(self):
        s = self.run_res("error: goto-instrument was killed\n", exit_code=1)
        self.assertEqual(s["status"], "TOOL_ERROR")
        self.assertFalse(k.gate_ok(s))

    def test_sample_memory_fake_proc(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            for pid, name, hwm, rss in (("10", "goto instr", 900, 800), ("11", "cbmc", 300, 300)):
                (d / "proc" / pid).mkdir(parents=True)
                (d / "proc" / pid / "status").write_text(f"Name:\t{name}\nVmHWM:\t {hwm} kB\nVmRSS:\t {rss} kB\n")
            (d / "proc" / "12").mkdir()
            (d / "proc" / "12" / "status").write_text("Name:\tkthreadd\n")
            out = d / "peaks.txt"
            k.sample_memory(out, 0.05, max_seconds=0.12, proc=d / "proc")
            peaks = k.parse_peaks(out.read_text())
            self.assertEqual(peaks["state"], "PARSED")
            self.assertGreaterEqual(peaks["samples"], 2)
            self.assertEqual(peaks["total_rss_peak_kb"], 1100)
            self.assertEqual([(c["cmd"], c["peak_kb"]) for c in peaks["commands"]], [("goto_instr", 900), ("cbmc", 300)])

    def test_sampler_binds_cbmc_and_direct_child_solver_to_same_build_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            model = root / "proof-model.out"
            metadata = root / "libcore.kani-metadata.json"
            row = {"pretty_name": "core::proof_for_contract::<u8>", "mangled_name": "_Rproof",
                   "goto_file": "proof-model.symtab.out", "attributes": {"kind": "Proof"}}
            metadata.write_text(json.dumps({"proof_harnesses": [row], "test_harnesses": []}))
            proc_root = root / "proc"
            for pid, name, ppid in (("101", "cbmc", "1"), ("102", "kissat", "101")):
                process = proc_root / pid
                process.mkdir(parents=True)
                (process / "status").write_text(f"Name:\t{name}\nVmHWM:\t 900 kB\nVmRSS:\t 800 kB\n")
                (process / "stat").write_text(f"{pid} ({name}) S {ppid} 0 0\n")
                if name == "cbmc":
                    (process / "cmdline").write_bytes(f"cbmc\0--no-malloc-may-fail\0{model}\0".encode())
                    os.symlink(root, process / "cwd")
            out, memory = root / "peaks.txt", root / "harness-memory.jsonl"
            dmesg = subprocess.CompletedProcess(["dmesg"], 1, "", "permission denied")
            with patch.object(k, "_cgroup_events", return_value={}), patch.object(k.subprocess, "run", return_value=dmesg):
                k.sample_memory(out, 0.01, max_seconds=0, proc=proc_root, harness_out=memory,
                                head_sha="a" * 40, kani_commit="b" * 40, build_id="build-3")
            records = {row["pid"]: row for row in map(json.loads, memory.read_text().splitlines())}
            for pid in ("101", "102"):
                self.assertEqual(records[pid]["attribution"], "direct")
                self.assertEqual(records[pid]["harness"], row["pretty_name"])
                self.assertEqual(records[pid]["metadata_sha256"], hashlib.sha256(metadata.read_bytes()).hexdigest())
                self.assertEqual((records[pid]["head_sha"], records[pid]["kani_commit"], records[pid]["build_id"]),
                                 ("a" * 40, "b" * 40, "build-3"))
                self.assertEqual((records[pid]["first_s"], records[pid]["last_s"]), (0, 0))
            self.assertEqual(records["102"]["parent_cbmc_pid"], "101")

    def test_sample_mem_cli_stops_on_sigterm(self):
        import signal
        import time
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "peaks.txt"
            proc = subprocess.Popen([sys.executable, "-B", str(Path(k.__file__)), "sample-mem", "--out", str(out),
                                     "--interval", "0.2"])
            for _ in range(50):
                if out.exists():
                    break
                time.sleep(0.1)
            proc.send_signal(signal.SIGTERM)
            self.assertEqual(proc.wait(timeout=10), 0)
            self.assertEqual(k.parse_peaks(out.read_text())["state"], "PARSED")


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(Path(k.__file__)), *args], capture_output=True, text=True)

    def test_validate_summarize_gate_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "req.json").write_text(json.dumps(REQ))
            (d / "kani.log").write_text(GOOD_LOG)
            r = self.run_cli("validate", str(d / "req.json"), "--args-out", str(d / "args"), "--runner-out", str(d / "runner"))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("--exact", (d / "args").read_text().split("\n"))
            self.assertEqual((d / "runner").read_text().strip(), "ubuntu-latest")
            common = ["--request", str(d / "req.json"), "--log", str(d / "kani.log"), "--time", str(d / "missing"),
                      "--run-id", "42", "--run-attempt", "1", "--bind", str(d / "req.json")]
            r = self.run_cli("summarize", *common, "--exit-code", "1", "--out-dir", str(d / "out"))
            self.assertEqual(r.returncode, 0, r.stderr)
            summary = json.loads((d / "out" / "summary.json").read_text())
            self.assertEqual(summary["run"]["id"], "42")
            self.assertIn(str(d / "req.json"), summary["tooling_sha256"])
            self.assertEqual(self.run_cli("gate", str(d / "out" / "summary.json")).returncode, 0)
            self.run_cli("summarize", *common, "--exit-code", "0", "--out-dir", str(d / "out2"))
            self.assertEqual(self.run_cli("gate", str(d / "out2" / "summary.json")).returncode, 1)
            self.assertEqual(self.run_cli("gate", str(d / "nope.json")).returncode, 3)
            (d / "memcap.txt").write_text("state=ENFORCED\nmax_bytes=1\npeak_bytes=1\noom_kill=0\n")
            self.run_cli("summarize", *common, "--exit-code", "1", "--memcap", str(d / "memcap.txt"), "--out-dir", str(d / "out3"))
            self.assertEqual(json.loads((d / "out3" / "summary.json").read_text())["resources"]["memcap"]["state"], "ENFORCED")
            self.run_cli("summarize", *common, "--exit-code", "1", "--memcap", str(d / "absent"), "--out-dir", str(d / "out4"))
            self.assertEqual(json.loads((d / "out4" / "summary.json").read_text())["resources"]["memcap"]["state"], "MISSING")
            self.assertIsNone(summary["resources"]["memcap"])

    def test_lane_limits(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "req.json"
            p.write_text(json.dumps({**REQ, "runner": "circleci-linux-large"}))
            ok = self.run_cli("validate", str(p), "--args-out", str(Path(d) / "a"), "--max-total-minutes", "40",
                              "--require-runner", "circleci-linux-large")
            self.assertEqual(ok.returncode, 0, ok.stderr)
            wrong = self.run_cli("validate", str(p), "--args-out", str(Path(d) / "b"), "--require-runner", "ubuntu-latest")
            self.assertEqual(wrong.returncode, 2)
            self.assertIn("only runner", wrong.stderr)
            many = {**REQ, "runner": "circleci-linux-large",
                    "harnesses": [{"name": P + f"h{i}", "expect": "SUCCESS"} for i in range(5)]}
            p.write_text(json.dumps(many))
            over = self.run_cli("validate", str(p), "--args-out", str(Path(d) / "c"), "--max-total-minutes", "40")
            self.assertEqual(over.returncode, 2)
            self.assertIn("40 minutes", over.stderr)

    def test_validate_rejects_bad_request(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "req.json"
            for bad in ({**REQ, "kind": "x"}, {**REQ, "agent": ["x"]}):
                p.write_text(json.dumps(bad))
                r = self.run_cli("validate", str(p), "--args-out", str(Path(d) / "args"))
                self.assertEqual(r.returncode, 2)
                self.assertIn("REQUEST_INVALID", r.stderr)
                self.assertNotIn("Traceback", r.stderr)
                self.assertFalse((Path(d) / "args").exists())


NATIVE_ENTRY = {"suite": "kani", "mode": "kani", "file": "FunctionContracts/repro.rs",
                "expect": "fail", "diagnostic": "expected `fn`", "require_success": True}
NATIVE_REQ = {**REQ, "kind": "kani-tests", "runner": k.STANDARD_RUNNER, "harnesses": [],
              "harness_timeout_minutes": 29, "test_timeout_seconds": 180, "kani_tests": [NATIVE_ENTRY]}


def native_log(entry=NATIVE_ENTRY, result="FAILED"):
    name = k.native_name(entry)
    failure = (f"\nfailures:\n\n---- {name} stdout ----\n"
               "error: test failed: expected verification success, got failure\n"
               "status: exit status: 1\n"
               f'command: "kani" "tests/{entry["suite"]}/{entry["file"]}"\n'
               "stderr:\nerror: expected `fn`\n\nfailures:\n    " + name + "\n") if result == "FAILED" else ""
    return (f"running 1 test\ntest {name} ... {result}\n" + failure +
            f"test result: {'FAILED' if result == 'FAILED' else 'ok'}. "
            f"{0 if result == 'FAILED' else 1} passed; {1 if result == 'FAILED' else 0} failed; "
            "0 ignored; 0 measured; 999 filtered out; finished in 0.12s\n")


class NativeTests(unittest.TestCase):
    def test_typed_manifest_and_limits(self):
        self.assertEqual(k.validate_request(copy.deepcopy(NATIVE_REQ)), NATIVE_REQ)
        self.assertEqual(k.kani_args(NATIVE_REQ), [])
        self.assertEqual(k.verification_mode("kani-tests"), "kani-tests")
        malformed = [dict(NATIVE_REQ, kani_tests=[]), dict(NATIVE_REQ, kani_tests=[NATIVE_ENTRY, NATIVE_ENTRY]),
                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "suite": "unknown"}]),
                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "file": "../x.rs"}]),
                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "file": ""}]),
                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "diagnostic": "unrelated"}]),
                     dict(NATIVE_REQ, kani_tests=[{**NATIVE_ENTRY, "require_success": False}]),
                     dict(NATIVE_REQ, test_timeout_seconds=0), dict(NATIVE_REQ, test_timeout_seconds=True),
                     dict(NATIVE_REQ, harness_timeout_minutes=30), dict(NATIVE_REQ, controls=False),
                     dict(NATIVE_REQ, runner="ubuntu-latest"), dict(REQ, kani_tests=[NATIVE_ENTRY])]
        for request in malformed:
            with self.subTest(request=request), self.assertRaises(k.RequestError):
                k.validate_request(request)
        with self.assertRaises(k.RequestError):
            k.validate_request(NATIVE_REQ, 28)
        expected = {"suite": "ui", "mode": "expected", "file": "error.rs", "expect": "pass",
                    "require_success": False, "diagnostic": "specific error"}
        k.validate_native_manifest([expected])
        positive = {key: value for key, value in {**expected, "require_success": True}.items() if key != "diagnostic"}
        k.validate_native_manifest([positive])
        for bad in ({key: value for key, value in expected.items() if key != "diagnostic"},
                    {**expected, "require_success": True}, {**expected, "mode": "ui"}):
            with self.assertRaises(k.RequestError):
                k.validate_native_manifest([bad])

    def test_exact_args_and_expected_success_policy(self):
        argv = k.native_argv(NATIVE_ENTRY, 180, Path("/tmp/out"))
        self.assertEqual(argv[:6], ["cargo", "run", "-p", "compiletest", "--", "--suite"])
        self.assertEqual(argv[argv.index("--exact") + 1], "[kani] kani/FunctionContracts/repro.rs")
        self.assertNotIn("--require-success", argv)
        pos = {**NATIVE_ENTRY, "mode": "expected", "suite": "expected", "expect": "pass"}
        self.assertIn("--require-success", k.native_argv(pos, 180, Path("/tmp/out")))
        self.assertNotIn("--require-success", k.native_argv({**pos, "require_success": False}, 180, Path("/tmp/out")))

    def test_completed_native_failure_only_and_own_diagnostic(self):
        own = "error: expected `fn`\n --> tests/kani/FunctionContracts/repro.rs:4:1\n"
        good = k.parse_native_test(NATIVE_ENTRY, native_log(), 1, own)
        self.assertEqual(good["status"], "EXPECTED_REPRO_FAILURE", good)
        self.assertEqual(good["time_s"], 0.12)
        cases = [("error: could not compile `compiletest`\n" + own, 1, own, False),
                 (native_log(), 124, own, False), (native_log(), -9, own, False),
                 (native_log(), 1, own, True), (native_log() + "thread 'main' panicked at x\n", 1, own, False),
                 (native_log(), 1, "other error", False), # matching diagnostic only in console/another test
                 (native_log(), 1, None, False), (native_log(), 1, own + "signal: 9\n", False),
                 (native_log(), 1, own + "thread 'rustc' panicked at x\n", False),
                 (native_log().replace("status: exit status: 1", "status: signal: 9"), 1, own, False),
                 (native_log().replace("expected verification success, got failure", "unrelated panic"), 1, own, False),
                 (native_log().replace('"tests/kani/FunctionContracts/repro.rs"', '"other.rs"'), 1, own, False),
                 (native_log(), 0, own, False), (native_log().replace("running 1 test", "running 0 tests"), 1, own, False),
                 (native_log().replace(k.native_name(NATIVE_ENTRY), "[kani] kani/other.rs"), 1, own, False),
                 (native_log() + native_log(), 1, own, False),
                 (native_log().split("test result:")[0], 1, own, False),
                 (native_log().replace("0 passed; 1 failed", "1 passed; 0 failed"), 1, own, False),
                 (native_log().replace("0 ignored", "1 ignored"), 1, own, False),
                 (native_log().replace("... FAILED", "... ignored"), 1, own, False),
                 (native_log().replace("finished in 0.12s", "finished in damaged"), 1, own, False)]
        for text, code, output, timeout in cases:
            with self.subTest(text=text[:80], code=code, output=output, timeout=timeout):
                self.assertEqual(k.parse_native_test(NATIVE_ENTRY, text, code, output, timeout)["status"], "ERROR")
        passed = {**NATIVE_ENTRY, "expect": "pass"}; passed.pop("diagnostic")
        self.assertEqual(k.parse_native_test(passed, native_log(passed, "ok"), 0, "SUCCESS FAILED")["status"], "PASS")
        self.assertEqual(k.parse_native_test(passed, "VERIFICATION:- SUCCESSFUL", 0, "")["status"], "ERROR")
        self.assertEqual(k.parse_native_test(passed, native_log(passed, "ok"), 1, "")["status"], "ERROR")

    def test_negative_expected_native_pass_needs_own_diagnostic(self):
        entry = {"suite": "ui", "mode": "expected", "file": "error.rs", "expect": "pass",
                 "require_success": False, "diagnostic": "specific error"}
        self.assertEqual(k.parse_native_test(entry, native_log(entry, "ok"), 0, "specific error")["status"], "PASS")
        self.assertEqual(k.parse_native_test(entry, native_log(entry, "ok") + "specific error", 0, "other")["status"], "ERROR")

    def test_patch_path_hash_and_fresh_pin_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); tree = root / "kani"; tree.mkdir()
            def git(*args):
                return subprocess.run(["git", "-C", str(tree), *args], capture_output=True, text=True, check=True).stdout.strip()
            git("init", "-q")
            (tree / "base").write_text("base\n")
            git("add", "base")
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture")
            pin = git("rev-parse", "HEAD")
            research = root / "research"; research.mkdir()
            patch_path = research / "tests.patch"
            contents = ("diff --git a/tests/kani/FunctionContracts/repro.rs b/tests/kani/FunctionContracts/repro.rs\n"
                        "new file mode 100644\n--- /dev/null\n+++ b/tests/kani/FunctionContracts/repro.rs\n"
                        "@@ -0,0 +1 @@\n+fn test() {}\n")
            patch_path.write_text(contents)
            request = {**NATIVE_REQ, "kani_patch": {"path": "research/tests.patch", "sha256": hashlib.sha256(contents.encode()).hexdigest()}}
            k.validate_request(request)
            for path in ("../tests.patch", "/absolute.patch", "research/../tests.patch", "research//tests.patch"):
                with self.assertRaises(k.RequestError):
                    k.validate_request({**request, "kani_patch": {**request["kani_patch"], "path": path}})
            (research / "link.patch").symlink_to(patch_path)
            (root / "linked").symlink_to(research)
            for bad in ({**request["kani_patch"], "path": "research/missing.patch"},
                        {**request["kani_patch"], "path": "research/link.patch"},
                        {**request["kani_patch"], "path": "linked/tests.patch"},
                        {**request["kani_patch"], "sha256": "0" * 64}):
                with self.assertRaises(k.RequestError):
                    k.patch_bytes({**request, "kani_patch": bad}, root)
            with self.assertRaises(k.RequestError):
                k.prepare_kani(request, root, tree, "0" * 40)
            info = k.prepare_kani(request, root, tree, pin)
            self.assertNotEqual(info["tree"], git("rev-parse", "HEAD^{tree}"))
            self.assertEqual(git("rev-parse", "HEAD"), pin)
            self.assertIn("repro.rs", info["diffstat"])
            with self.assertRaises(k.RequestError): # already applied/dirty is forbidden
                k.prepare_kani(request, root, tree, pin)
            git("reset", "--hard", "HEAD")
            patch_path.write_text(contents.replace("/repro.rs", "/absent.rs").replace("+fn test() {}", "+conflict"))
            request["kani_patch"]["sha256"] = hashlib.sha256(patch_path.read_bytes()).hexdigest()
            with self.assertRaises(k.RequestError): # selector missing after successful apply
                k.prepare_kani(request, root, tree, pin)
            git("reset", "--hard", "HEAD")
            patch_path.write_text("diff --git a/base b/base\n--- a/base\n+++ b/base\n@@ -1 +1 @@\n-missing context\n+replacement\n")
            request["kani_patch"]["sha256"] = hashlib.sha256(patch_path.read_bytes()).hexdigest()
            with self.assertRaises(k.RequestError):
                k.prepare_kani(request, root, tree, pin)
            self.assertEqual(git("status", "--porcelain"), "")

    def summary(self):
        text = json.dumps(NATIVE_REQ)
        info = {"pin": "b" * 40, "patch": None, "tree": "c" * 40, "version": "kani 0.68.0",
                "diffstat": "", "kani_build_s": 12, "compiletest_build_s": 2}
        row = k.parse_native_test(NATIVE_ENTRY, native_log(), 1, "error: expected `fn`\n")
        row.update(argv=k.native_argv(NATIVE_ENTRY, 180, Path("/tmp/out/native-0")), cwd="/workspace/src/kani_build",
                   env={"RUST_TEST_THREADS": "1"}, wall_s=1)
        native = {"schema": k.NATIVE_SCHEMA, "head_sha": "a" * 40, "build_id": "build-1",
                  "request_sha256": hashlib.sha256(text.encode()).hexdigest(), "tree": info["tree"], "complete": True,
                  "binaries": {"kani_profile": "release", "compiletest_profile": "dev", "paths": {
                      "kani": {"invoked": "/kani/scripts/kani"}, "compiletest": {"invoked": "/kani/target/debug/compiletest"},
                      **{name: {"invoked": "/kani/target/kani/bin/" + name, "release": "/kani/target/release/" + name,
                                "resolved": "/kani/target/release/" + name, "sha256": "e" * 64}
                         for name in ("kani-driver", "kani-compiler")}}}, "tests": [row]}
        def summarize(report=native, build=info, outcome="success", code=0):
            return k.summarize(text, None, None, code, "a" * 40, "b" * 40, run={"id": "build-1"},
                               build_outcome=outcome, native_text=json.dumps(report), kani_build_text=json.dumps(build))
        return native, info, summarize

    def test_structured_report_gate_and_binding(self):
        native, info, summarize = self.summary()
        summary = summarize()
        self.assertTrue(k.gate_ok(summary), summary)
        self.assertIsNone(summary["kani_exit_code"])
        self.assertEqual(summary["native_runner_exit_code"], 0)
        self.assertIn("EXPECTED_REPRO_FAILURE", k.render_md(summary))
        self.assertIn("EXPECTED_REPRO_FAILURE", k.summary_page(summary, 0, 20))
        bad_reports = [None, {}, {**native, "head_sha": "d" * 40}, {**native, "build_id": "other"},
                       {**native, "request_sha256": "f" * 64}, {**native, "tree": "d" * 40},
                       {**native, "complete": False}, {**native, "tests": []},
                       {**native, "tests": native["tests"] * 2}, {**native, "binaries": {}},
                       {**native, "tests": [{**native["tests"][0], "status": "ERROR"}]},
                       {**native, "tests": [{**native["tests"][0], "argv": ["bad"]}]},
                       {**native, "tests": [{**native["tests"][0], "env": {"RUST_TEST_THREADS": "2"}}]},
                       {**native, "tests": [{**native["tests"][0], "exit_code": 0}]},
                       {**native, "tests": [{**native["tests"][0], "time_s": None}]},
                       {**native, "tests": [{**native["tests"][0], "diagnostic": None}]},
                       {**native, "tests": [{**native["tests"][0], "errors": ["timeout"]}]}]
        for bad in bad_reports:
            self.assertFalse(k.gate_ok(summarize(bad)), bad)
        for bad in (None, {}, {**info, "pin": "d" * 40}, {**info, "version": ""}, {**info, "tree": "bad"}):
            self.assertFalse(k.gate_ok(summarize(build=bad)), bad)
        self.assertFalse(k.gate_ok(summarize(outcome="failure")))
        for code in (None, 1, 124, -9):
            self.assertFalse(k.gate_ok(summarize(code=code)))

    def test_native_pagination_is_bounded_and_explicit(self):
        native, info, summarize = self.summary()
        summary = summarize()
        page = json.loads(k.native_page(summary, 0, 1))
        self.assertEqual(page["count"], 1)
        self.assertIsNone(page["next_offset"])
        self.assertIn("argv", page["tests"][0])
        self.assertIn("binaries", page)
        summary["native"]["tests"] *= 5
        for row in summary["native"]["tests"]:
            row["extra"] = "x" * 3000
        text = k.native_page(summary, 0, 4)
        self.assertLessEqual(len(text.encode()), 12000)
        page = json.loads(text)
        self.assertEqual(page["next_offset"], page["count"])
        self.assertLess(page["count"], 4)
        with self.assertRaises(ValueError):
            k.native_page(summary, 0, 5)

    def test_pinned_multiline_version_and_invalid_identity_diagnostics(self):
        native, info, summarize = self.summary()
        version = "Kani Rust Verifier 0.68.0 (standalone)\nCBMC 6.8.0"
        summary = summarize(build={**info, "version": version})
        self.assertTrue(k.gate_ok(summary), summary)
        self.assertEqual(summary["kani_build"]["version"], version)
        self.assertIn("version `Kani Rust Verifier 0.68.0 (standalone); CBMC 6.8.0`", k.render_md(summary))
        for value in ("", "line\n" * 9, "x" * 401, ["Kani"], None):
            failed = summarize(build={**info, "version": value})
            self.assertFalse(k.gate_ok(failed))
            self.assertIsNone(failed["kani_exit_code"])
            self.assertEqual(failed["native_runner_exit_code"], 0)
            self.assertEqual(failed["diagnostic_artifacts"]["kani_build"]["version"], value)
            self.assertEqual(failed["diagnostic_artifacts"]["native"], native)
            page = json.loads(k.native_page(failed, 0, 1))
            self.assertEqual(page["validation"], "UNVALIDATED_DIAGNOSTIC_ONLY")
            self.assertFalse(page["gate"])
            self.assertEqual(page["tests"], native["tests"])
        failed = summarize(report={**native, "complete": False})
        self.assertFalse(k.gate_ok(failed))
        self.assertEqual(json.loads(k.native_page(failed, 0, 1))["validation"], "UNVALIDATED_DIAGNOSTIC_ONLY")
        self.assertEqual(k.diagnostic_json(None), {"state": "MISSING"})
        self.assertEqual(k.diagnostic_json("{")["state"], "INVALID_JSON")
        self.assertEqual(k.diagnostic_json("x" * (128 * 1024 + 1))["state"], "OVERSIZED")

    def test_wall_timeout_and_deadline_never_invoke_tools_late(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); log = root / "test.log"
            code, timeout, _ = k.bounded_command([sys.executable, "-c", "import time; time.sleep(10)"], root, log, 0.05)
            self.assertTrue(timeout)
            self.assertEqual(code, -9)
            with patch.object(k.subprocess, "Popen") as popen:
                self.assertEqual(k.bounded_command(["never-run"], root, log, -1), (None, True, 0.0))
                popen.assert_not_called()

    def test_runner_writes_partial_report_and_no_cross_test_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def command(argv, tree, log, seconds, env, stderr_log=None):
                self.assertEqual(env["RUST_TEST_THREADS"], "1")
                self.assertLessEqual(seconds, 210)
                log.write_text(native_log())
                stderr_log.write_text("")
                base = Path(argv[argv.index("--build-base") + 1]) / "FunctionContracts/repro/repro"
                base.parent.mkdir(parents=True)
                base.with_suffix(".out").write_text("")
                base.with_suffix(".err").write_text("error: expected `fn`\n")
                return 1, False, 0.2
            with patch.object(k, "native_binary_identity", return_value={"kani_profile": "release"}), patch.object(k, "bounded_command", side_effect=command):
                k.run_native(NATIVE_REQ, root, root / "out", k.time.time() + 100, {"tree": "a" * 40})
            report = json.loads((root / "out/native.json").read_text())
            self.assertTrue(report["complete"])
            self.assertEqual(report["tests"][0]["status"], "EXPECTED_REPRO_FAILURE")
            with patch.object(k, "native_binary_identity", return_value={}), patch.object(k, "bounded_command", side_effect=OSError("exec failed")):
                with self.assertRaises(OSError):
                    k.run_native(NATIVE_REQ, root, root / "error", k.time.time() + 100, {})
            self.assertFalse(json.loads((root / "error/native.json").read_text())["complete"])

    def test_patch_supported_diagnostic_without_changing_old_args(self):
        req = req_with(kind="diagnostic", runner=k.STANDARD_RUNNER)
        patched = {**req, "kani_patch": {"path": "research/p.patch", "sha256": "1" * 64}}
        self.assertEqual(k.kani_args(k.validate_request(patched)), k.kani_args(k.validate_request(req)))
        self.assertEqual(k.verification_mode(patched["kind"]), "selected")
        self.assertFalse(k.gate_ok(k.summarize(json.dumps(patched), GOOD_LOG, TIME, 1, "a" * 40, "b" * 40, build_outcome="success")))
        info = {"pin": "b" * 40, "patch": patched["kani_patch"], "tree": "c" * 40, "version": "kani 0.68.0"}
        summary = k.summarize(json.dumps(patched), GOOD_LOG, TIME, 1, "a" * 40, "b" * 40,
                              build_outcome="success", kani_build_text=json.dumps(info))
        self.assertTrue(k.gate_ok(summary), summary)

    def test_release_binary_paths_must_match_and_debug_driver_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in ("target/release/kani-driver", "target/release/kani-compiler", "target/kani/bin/kani-driver",
                             "target/kani/bin/kani-compiler", "scripts/kani", "target/debug/compiletest"):
                p = root / relative; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b"fixture")
            info = k.native_binary_identity(root)
            self.assertEqual(info["kani_profile"], "release")
            (root / "target/debug/kani-driver").write_bytes(b"debug")
            with self.assertRaises(k.RequestError):
                k.native_binary_identity(root)
            (root / "target/debug/kani-driver").unlink()
            (root / "target/kani/bin/kani-compiler").write_bytes(b"different")
            with self.assertRaises(k.RequestError):
                k.native_binary_identity(root)


class NativeOutputEvidenceTests(unittest.TestCase):
    def assert_excerpt_bounds(self, excerpt):
        self.assertLessEqual(len(json.dumps(excerpt, ensure_ascii=False, indent=2).encode()), k.NATIVE_EXCERPT_BYTES)
        self.assertLessEqual(len(excerpt["records"]), k.NATIVE_EXCERPT_LINES)
        self.assertTrue(excerpt["diagnostic_only"])
        self.assertEqual(excerpt["selected_line_count"], len(excerpt["records"]))
        for source in k.NATIVE_OUTPUT_SOURCES:
            records = [r for r in excerpt["records"] if r["source"] == source]
            self.assertEqual([r["line"] for r in records], sorted({r["line"] for r in records}))
            for record in records:
                self.assertLessEqual(len(record["text"]), 220)
                self.assertLessEqual(len(json.dumps(record["text"], ensure_ascii=False).encode()), 260)

    def test_terse_and_regular_failures_precede_error_tail_context(self):
        checks = ['Failed Checks: assertion failed', 'File: "test.rs", line 3',
                  '  Check 1: success', '  - Status: SUCCESS', '  - Description: "ignore success"',
                  '  Check 2: failing.assertion', '  - Status: FAILURE',
                  '  - Description: "regular failure"', '  - Location: test.rs:4:2']
        text = "error: ordinary\n" * 100 + "\n".join(checks) + "\n" + "tail\n" * 100
        expected = [101, 102, 106, 107, 108, 109]
        # Exactly enough lines for failure context: error/tail must not consume any slots first.
        with patch.object(k, "NATIVE_EXCERPT_LINES", 6):
            excerpt = k.native_output_excerpt({"kani_stdout": text})
            self.assert_excerpt_bounds(excerpt)
        self.assertEqual([r["line"] for r in excerpt["records"]], expected)
        self.assertEqual(excerpt["failed_check_line_count"], 6)
        self.assertEqual(excerpt["omitted_failed_check_line_count"], 0)
        self.assertIn("failed-check", excerpt["selection"])
        # Worker prefixes and regular blank separators retain the original source lines.
        threaded = "\n".join("Thread 1: " + line for line in checks[:2] + [""] + checks[5:])
        excerpt = k.native_output_excerpt({"kani_stderr": threaded})
        self.assertEqual(excerpt["failed_check_line_count"], 6)
        self.assertEqual(excerpt["omitted_failed_check_line_count"], 0)

    def test_many_failed_checks_unicode_escaping_and_exact_omission_count(self):
        rows = []
        for i in range(80):
            rows.extend([f"Check {i}: " + "界İ" * 1000,
                         "- Status: FAILURE",
                         '- Description: "' + "\x00\t\\界" * 1000 + ' error near end"',
                         "- Location: test.rs:123"])
        for text in ("\n".join(rows), "\n".join("Failed Checks: " + "界" * 2000 for _ in range(100))):
            excerpt = k.native_output_excerpt({"kani_stdout": text})
            self.assert_excerpt_bounds(excerpt)
            self.assertGreater(excerpt["omitted_failed_check_line_count"], 0)
            self.assertEqual(excerpt["failed_check_line_count"], len(text.splitlines()))
            self.assertEqual(excerpt["omitted_failed_check_line_count"],
                             len(text.splitlines()) - len(excerpt["records"]))
            self.assertTrue(any(r["clipped"] for r in excerpt["records"]))
            self.assertTrue(all(r["start_char"] == 0 for r in excerpt["records"]))

    def test_regular_success_block_is_not_failed_context(self):
        text = 'Check 1: good\n- Status: SUCCESS\n- Description: good\n- Location: here\n'
        excerpt = k.native_output_excerpt({"kani_stdout": text})
        self.assert_excerpt_bounds(excerpt)
        self.assertEqual(excerpt["failed_check_line_count"], 0)
        self.assertEqual(excerpt["omitted_failed_check_line_count"], 0)

    def test_compiletest_stdout_and_stderr_are_separate_without_changing_exit(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); out = root / "stdout"; err = root / "stderr"
            code, timeout, _ = k.bounded_command(
                [sys.executable, "-c", "import sys; print('own stdout'); print('own stderr', file=sys.stderr); sys.exit(3)"],
                root, out, 5, stderr_log=err)
            self.assertEqual((code, timeout), (3, False))
            self.assertEqual(out.read_text(), "own stdout\n")
            self.assertEqual(err.read_text(), "own stderr\n")

    def test_source_paths_hashes_and_raw_vs_rendered_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); paths = {s: root / s for s in k.NATIVE_OUTPUT_SOURCES}
            paths["compiletest_stdout"].write_text("error: expected `fn`\n")
            paths["compiletest_stderr"].write_text("compiletest failed\n")
            paths["kani_stdout"].write_text("")
            raw = json.dumps({"rendered": "error: expected `fn`\n"}).encode()
            paths["kani_stderr"].write_bytes(raw)
            texts, sources = k.native_output_sources(paths, "expected `fn`")
            self.assertEqual(texts["kani_stderr"], raw.decode())
            self.assertTrue(sources["compiletest_stdout"]["expected_fn_error_line_found"])
            self.assertTrue(sources["kani_stderr"]["required_substring_found"])
            self.assertFalse(sources["kani_stderr"]["expected_fn_error_line_found"])
            self.assertFalse(sources["compiletest_stdout"]["used_for_gate_diagnostic"])
            self.assertTrue(sources["kani_stderr"]["used_for_gate_diagnostic"])
            self.assertEqual(sources["kani_stderr"]["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(sources["kani_stderr"]["bytes"], len(raw))
            self.assertEqual(sources["kani_stderr"]["path"], str(paths["kani_stderr"]))
            paths["kani_stderr"].unlink()
            texts, sources = k.native_output_sources(paths, "expected `fn`")
            self.assertIsNone(texts["kani_stderr"])
            self.assertFalse(sources["kani_stderr"]["available"])
            self.assertIsNone(sources["kani_stderr"]["sha256"])

    def test_excerpt_bounds_error_priority_tail_unicode_and_long_lines(self):
        texts = {source: "early error " + source + "\n" + "noise\n" * 200
                 + "界" * 10000 + " error far into a Unicode line\n"
                 + "control error " + "\x00" * 2000 + "\n" + "tail " + source + "\n"
                 for source in k.NATIVE_OUTPUT_SOURCES}
        excerpt = k.native_output_excerpt(texts)
        self.assertLessEqual(len(json.dumps(excerpt, ensure_ascii=False, indent=2).encode()), 4096)
        self.assertLessEqual(len(excerpt["records"]), 60)
        self.assertGreater(excerpt["omitted_line_count"], 0)
        self.assertTrue(excerpt["diagnostic_only"])
        for source in k.NATIVE_OUTPUT_SOURCES:
            records = [r for r in excerpt["records"] if r["source"] == source]
            self.assertTrue(any("early error " + source in r["text"] for r in records))
            self.assertTrue(any(r["text"] == "tail " + source for r in records))
            self.assertEqual([r["line"] for r in records], sorted({r["line"] for r in records}))
        clipped = k.native_output_excerpt({"kani_stderr": "x" * 10000 + " error: detail"})
        record = clipped["records"][0]
        self.assertIn("error: detail", record["text"])
        self.assertTrue(record["clipped"])
        self.assertGreater(record["start_char"], 0)
        unicode_line = k.native_output_excerpt({"kani_stderr": "İ" * 10000 + " error: Unicode context"})
        self.assertIn("error: Unicode context", unicode_line["records"][0]["text"])
        empty = k.native_output_excerpt({})
        self.assertEqual(empty["selected_line_count"], 0)
        self.assertEqual(empty["omitted_line_count"], 0)

    def run_case(self, root, entry=NATIVE_ENTRY, terminal="FAILED", own_err="error: different failure\n", stderr="stderr error context\n", own_out="Kani stdout tail\n"):
        request = {**NATIVE_REQ, "kani_tests": [entry]}
        def command(argv, tree, log, seconds, env, stderr_log=None):
            log.write_text(native_log(entry, terminal))
            stderr_log.write_text(stderr)
            base = Path(argv[argv.index("--build-base") + 1]) / Path(entry["file"]).parent / Path(entry["file"]).stem / Path(entry["file"]).stem
            base.parent.mkdir(parents=True)
            base.with_suffix(".out").write_text(own_out)
            if own_err is not None:
                base.with_suffix(".err").write_text(own_err)
            # This unrelated file must never supply gate diagnostics or excerpt text.
            (root / "foreign.err").write_text("FOREIGN error: expected `fn`\n")
            return (1 if terminal == "FAILED" else 0), False, 0.2
        with patch.object(k, "native_binary_identity", return_value={"kani_profile": "release"}), patch.object(k, "bounded_command", side_effect=command):
            k.run_native(request, root, root / "out", k.time.time() + 100, {})
        return json.loads((root / "out/native.json").read_text())["tests"][0]

    def test_failed_repro_excerpt_does_not_grant_console_or_foreign_diagnostic_credit(self):
        with tempfile.TemporaryDirectory() as d:
            row = self.run_case(Path(d))
            self.assertEqual(row["native_status"], "FAILED")
            self.assertEqual(row["status"], "ERROR")
            self.assertIsNone(row["diagnostic"])
            self.assertIsNone(row["diagnostic_provenance"]["selected_source"])
            self.assertTrue(row["output_sources"]["compiletest_stdout"]["required_substring_found"])
            self.assertFalse(row["output_sources"]["kani_stderr"]["required_substring_found"])
            excerpt = json.dumps(row["output_excerpt"])
            self.assertIn("different failure", excerpt)
            self.assertIn("stderr error context", excerpt)
            self.assertNotIn("FOREIGN", excerpt)
            self.assertEqual({r["source"] for r in row["output_excerpt"]["records"]}, set(k.NATIVE_OUTPUT_SOURCES))
        with tempfile.TemporaryDirectory() as d:
            missing = self.run_case(Path(d), own_err=None, own_out="error: expected `fn`\n")
            self.assertEqual(missing["status"], "ERROR")
            self.assertIsNone(missing["diagnostic"])
            self.assertIsNone(missing["diagnostic_provenance"]["selected_source"])
            self.assertTrue(missing["output_sources"]["kani_stdout"]["required_substring_found"])
            self.assertFalse(missing["output_sources"]["kani_stderr"]["available"])

    def test_failed_check_text_never_supplies_required_compiler_diagnostic(self):
        for text in ("Failed Checks: expected `fn`\nFile: test.rs\n",
                     'Check 1: fn\n- Status: FAILURE\n- Description: "expected `fn`"\n- Location: test.rs\n'):
            with self.subTest(text=text), tempfile.TemporaryDirectory() as d:
                row = self.run_case(Path(d), own_out=text, own_err="other failure\n")
                self.assertEqual(row["status"], "ERROR")
                self.assertIn("repro diagnostic is not an actual compiler error", row["errors"])
                self.assertGreater(row["output_excerpt"]["failed_check_line_count"], 0)
                self.assertTrue(row["output_excerpt"]["diagnostic_only"])
                native, _, summarize = NativeTests().summary()
                native["tests"][0].update(row)
                self.assertFalse(k.gate_ok(summarize(report=native)))

    def test_excerpt_condition_includes_failed_positive_and_successful_negative(self):
        passed = {key: value for key, value in {**NATIVE_ENTRY, "expect": "pass"}.items() if key != "diagnostic"}
        for entry, terminal, excerpt_required in ((passed, "FAILED", True), (NATIVE_ENTRY, "ok", True), (passed, "ok", False)):
            with self.subTest(expect=entry["expect"], terminal=terminal), tempfile.TemporaryDirectory() as d:
                row = self.run_case(Path(d), entry, terminal)
                self.assertEqual("output_excerpt" in row, excerpt_required)
                if terminal == "ok" and entry["expect"] == "pass":
                    self.assertEqual(row["status"], "PASS")
                else:
                    self.assertEqual(row["status"], "ERROR")

    def test_own_stderr_match_remains_gate_source_and_excerpt_pages_fit(self):
        with tempfile.TemporaryDirectory() as d:
            row = self.run_case(Path(d), own_err="error: expected `fn`\n" + "extra error detail\n" * 500)
            self.assertEqual(row["status"], "EXPECTED_REPRO_FAILURE")
            self.assertEqual(row["diagnostic_provenance"]["selected_source"], "kani_stderr")
            native, info, summarize = NativeTests().summary()
            native["tests"][0].update({key: row[key] for key in ("output_sources", "output_excerpt", "diagnostic_provenance")})
            summary = summarize(report=native)
            self.assertTrue(k.gate_ok(summary), summary)
            text = k.native_page(summary, 0, 1)
            self.assertLessEqual(len(text.encode()), 12000)
            page = json.loads(text)
            self.assertEqual(page["tests"][0]["output_excerpt"], row["output_excerpt"])
            failed = summarize(report={**native, "complete": False})
            page = json.loads(k.native_page(failed, 0, 1))
            self.assertEqual(page["validation"], "UNVALIDATED_DIAGNOSTIC_ONLY")
            self.assertFalse(page["gate"])
            self.assertIn("output_excerpt", page["tests"][0])


class NativeFieldPageTests(unittest.TestCase):
    def summary(self):
        return {"run": {"id": "field-build"}, "head_sha": "a" * 40, "request_sha256": "b" * 64,
                "status": "INCONSISTENT", "diagnostic_artifacts": {"native": {"tests": [
                    {"file": "test.rs", "errors": ["界" * 1000 for _ in range(15)],
                     "argv": ["cargo", "run"], "env": {"A": "one", "B": "two"},
                     "diagnostic": "界\\\x00" * 2000, "nullable": None,
                     "output_excerpt": {"diagnostic_only": True, "records": [{"text": str(i)} for i in range(5)]}}
                ]}}}

    def test_large_record_array_pages_preserve_identity_and_continuation(self):
        summary = self.summary()
        with self.assertRaisesRegex(ValueError, "one native record"):
            k.native_page(summary, 0, 1)
        start, received = 0, []
        while True:
            text = k.native_field_page(summary, 0, "errors", start, 80, summary_file="/cache/summary.json", summary_sha256="c" * 64)
            self.assertLessEqual(len(text.encode()), k.MAX_MD_BYTES)
            page = json.loads(text)
            self.assertEqual((page["build_id"], page["offset"], page["file"]), ("field-build", 0, "test.rs"))
            self.assertEqual(page["summary_file"], "/cache/summary.json")
            self.assertEqual(page["summary_sha256"], "c" * 64)
            self.assertEqual(page["validation"], "UNVALIDATED_DIAGNOSTIC_ONLY")
            self.assertTrue(page["diagnostic_only"])
            self.assertEqual(page["start"], start)
            self.assertEqual(page["count"], len(page["value"]))
            received.extend(page["value"])
            if page["next_start"] is None:
                break
            self.assertGreater(page["next_start"], start)
            start = page["next_start"]
        self.assertEqual(received, summary["diagnostic_artifacts"]["native"]["tests"][0]["errors"])

    def test_nested_records_strings_objects_scalars_and_empty_fields(self):
        summary = self.summary()
        page = lambda field, start=0, count=80: json.loads(k.native_field_page(summary, 0, field, start, count))
        self.assertEqual(page("output_excerpt.records", 2, 2)["value"], [{"text": "2"}, {"text": "3"}])
        self.assertEqual(page("output_excerpt.records.2.text")["value"], "2")
        self.assertEqual(page("env", 1, 1)["value"], {"B": "two"})
        self.assertEqual(page("argv")["value"], ["cargo", "run"])
        self.assertIsNone(page("nullable")["value"])
        self.assertIs(page("output_excerpt.diagnostic_only")["value"], True)
        self.assertEqual(page("diagnostic", 1, 4)["value"], "\\\x00界\\")
        self.assertEqual(page("diagnostic")["units"], "unicode-codepoints")
        native = summary["diagnostic_artifacts"]["native"]
        native["tests"][0].update(empty_list=[], empty_dict={}, empty_str="")
        for field, value in (("empty_list", []), ("empty_dict", {}), ("empty_str", "")):
            self.assertEqual(page(field)["value"], value)
            self.assertIsNone(page(field)["next_start"])
        summary["native"] = native
        self.assertEqual(page("errors")["validation"], "VALIDATED")
        self.assertTrue(page("errors")["diagnostic_only"])

    def test_bad_bounds_unknown_fields_missing_reports_and_oversized_unit(self):
        for offset, field, start, count in ((1, "errors", 0, 1), (-1, "errors", 0, 1),
                (0, "absent", 0, 1), (0, "errors", -1, 1), (0, "errors", 16, 1),
                (0, "errors", 0, 0), (0, "errors", 0, 81), (0, "env.absent", 0, 1),
                (0, "output_excerpt.records.5", 0, 1), (0, "", 0, 1), (0, "env..A", 0, 1)):
            with self.subTest(offset=offset, field=field, start=start, count=count), self.assertRaises(ValueError):
                k.native_field_page(self.summary(), offset, field, start, count)
        for summary in (None, [], {}, {"native": None}, {"diagnostic_artifacts": None},
                        {"native": {"tests": None}}, {"native": {"tests": [None]}},
                        {"native": {"tests": []}}):
            with self.subTest(summary=summary), self.assertRaises(ValueError):
                k.native_field_page(summary, 0, "errors")
        summary = self.summary()
        summary["diagnostic_artifacts"]["native"]["tests"][0]["errors"] = ["界" * k.MAX_MD_BYTES]
        with self.assertRaisesRegex(ValueError, "one native field unit"):
            k.native_field_page(summary, 0, "errors")
        # A caller can drill into the oversized item and page its string instead.
        text = k.native_field_page(summary, 0, "errors.0")
        self.assertEqual(json.loads(text)["next_start"], 80)


if __name__ == "__main__":
    unittest.main()
