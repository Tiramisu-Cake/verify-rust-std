"""Synthetic service tests for kani_k1.py. Run: python3 -B -m unittest discover -s research/challenge-8/kani-k1/tools"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kani_k1 as k  # noqa: E402

P = "slice::sort::shared::smallsort::kani_k1::"
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


def summ(log, req=None, time=TIME, exit_code=1, request_error=None, build_outcome="success"):
    text = json.dumps(req if req is not None else REQ)
    return k.summarize(text, log, time, exit_code, "a" * 40, "b" * 40, request_error,
                       {"id": "1", "attempt": "1", "image_os": "ubuntu24", "image_version": "x"}, {"f": "0" * 64},
                       build_outcome)


ONLY_OK = [{"name": P + "smoke::ok", "expect": "SUCCESS"}]


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
        for name in ["slice::sort::shared::smallsort::verify::h", "x; rm -rf /", P + "a b", P, P + "ok::",
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
        self.assertFalse(s["measurement_ok"])
        self.assertFalse(k.gate_ok(s))
        odd_format = OK_BLOCK.replace("2 of 2 cover properties satisfied", "2/2 covers ok") + tail(1, 0)
        self.assertFalse(summ(odd_format, req, exit_code=0)["measurement_ok"])
        short = OK_BLOCK.replace("2 of 2 cover", "1 of 2 cover") + tail(1, 0)
        self.assertFalse(summ(short, req, exit_code=0)["measurement_ok"])
        slow = OK_BLOCK.replace("1.25s", "600.5s") + tail(1, 0)
        self.assertFalse(summ(slow, req, exit_code=0)["measurement_ok"])
        self.assertTrue(summ(OK_BLOCK + tail(1, 0), req, exit_code=0)["measurement_ok"])

    def test_diagnostic_gate_ignores_measurement_bounds(self):
        req = req_with(kind="diagnostic", harnesses=ONLY_OK)
        no_cover = OK_BLOCK.replace(" ** 2 of 2 cover properties satisfied\n", "") + tail(1, 0)
        s = summ(no_cover, req, exit_code=0)
        self.assertIsNone(s["measurement_ok"])
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
                                ("failure", "Kani build failed"), ("verify-skipped", "60-minute")):
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


if __name__ == "__main__":
    unittest.main()
