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
    "kind": "diagnostic", "purpose": "lane smoke", "runner": "ubuntu-latest", "harness_timeout_minutes": 10,
    "harnesses": [{"name": P + "smoke::ok", "expect": "SUCCESS"},
                  {"name": P + "smoke::control", "expect": "FAILED"}],
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
TAIL = "\nSummary:\nVerification failed for - x\nComplete - 1 successfully verified harnesses, 1 failures, 2 total.\n"
TIME = "\tMaximum resident set size (kbytes): 4096000\n\tElapsed (wall clock) time (h:mm:ss or m:ss): 41:02.11\n"


def summ(log, req=None, time=TIME, exit_code=1, request_error=None):
    text = json.dumps(req if req is not None else REQ)
    return k.summarize(text, log, time, exit_code, "a" * 40, "b" * 40, request_error)


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
        self.assertIn("--exact", args)
        self.assertIn("--jobs=1", args)
        self.assertIn("10m", args)

    def test_rejections(self):
        self.bad(lambda r: r.update(schema="x"), "schema")
        self.bad(lambda r: r.update(extra=1), "unknown")
        self.bad(lambda r: r.pop("purpose"), "missing")
        self.bad(lambda r: r.update(request_id="Bad ID"), "request_id")
        self.bad(lambda r: r.update(agent="select"), "agent")
        self.bad(lambda r: r.update(kind="proof"), "kind")
        self.bad(lambda r: r.update(runner="windows-latest"), "runner")
        self.bad(lambda r: r.pop("runner"), "missing")
        self.bad(lambda r: r.update(purpose="a\nb"), "purpose")
        self.bad(lambda r: r.update(harness_timeout_minutes=31), "harness_timeout")
        self.bad(lambda r: r.update(harness_timeout_minutes=True), "harness_timeout")
        self.bad(lambda r: r.update(kind="measurement", harness_timeout_minutes=12), "measurement")
        self.bad(lambda r: r.update(harnesses=[]), "1..20")
        self.bad(lambda r: r["harnesses"].append(dict(r["harnesses"][0])), "duplicate")
        self.bad(lambda r: r["harnesses"][0].update(expect="PASS"), "expect")
        self.bad(lambda r: r["harnesses"][0].update(note="x"), "exactly")

    def test_rejects_names_outside_experiment_module(self):
        for name in ["slice::sort::shared::smallsort::verify::h", "x; rm -rf /", P + "a b", P, P + "ok::"]:
            req = copy.deepcopy(REQ)
            req["harnesses"][0]["name"] = name
            with self.assertRaises(k.RequestError):
                k.validate_request(req)

    def test_total_budget(self):
        req = copy.deepcopy(REQ)
        req["harness_timeout_minutes"] = 30
        req["harnesses"] = [{"name": P + f"h{i}", "expect": "SUCCESS"} for i in range(6)]
        with self.assertRaises(k.RequestError):
            k.validate_request(req)


class SummaryTests(unittest.TestCase):
    def test_complete_with_expectations(self):
        s = summ(OK_BLOCK + FAIL_BLOCK + TAIL)
        self.assertEqual(s["status"], "COMPLETE")
        self.assertTrue(s["expectation_met"])
        ok, control = s["harnesses"]
        self.assertEqual((ok["status"], ok["time_s"], ok["unreachable"], ok["covers_all_satisfied"]), ("SUCCESS", 1.25, 2, True))
        self.assertEqual(control["status"], "FAILED")
        self.assertIn("smoke.rs", control["failed_checks"][0])
        self.assertEqual(s["resources"]["max_rss_kb"], 4096000)
        self.assertEqual(s["complete_line"]["total"], 2)

    def test_unexpected_failure_breaks_expectation(self):
        req = copy.deepcopy(REQ)
        req["harnesses"][1]["expect"] = "SUCCESS"
        s = summ(OK_BLOCK + FAIL_BLOCK, req)
        self.assertEqual(s["status"], "COMPLETE")
        self.assertFalse(s["expectation_met"])

    def test_timeout(self):
        log = OK_BLOCK + f"Checking harness {P}smoke::control...\nCBMC timed out. You may want to rerun your proof with a larger timeout\nVERIFICATION:- FAILED\n"
        s = summ(log)
        self.assertEqual(s["harnesses"][1]["status"], "TIMEOUT")
        self.assertFalse(s["expectation_met"])

    def test_partial_and_unknown(self):
        s = summ(OK_BLOCK)
        self.assertEqual(s["status"], "PARTIAL")
        self.assertEqual(s["harnesses"][1]["status"], "NOT_RUN")
        s = summ(OK_BLOCK + f"Checking harness {P}smoke::control...\nKilled\n")
        self.assertEqual(s["harnesses"][1]["status"], "UNKNOWN")
        self.assertEqual(s["status"], "PARTIAL")

    def test_compile_error(self):
        log = "   Compiling core v0.0.0\nerror[E0599]: no method named `clone` found\n  --> library/core/src/x.rs:1:1\nerror: could not compile `core`\n"
        s = summ(log)
        self.assertEqual(s["status"], "COMPILE_ERROR")
        self.assertTrue(any("E0599" in line for line in s["compile_errors"]))
        self.assertTrue(all(h["status"] == "NOT_RUN" for h in s["harnesses"]))

    def test_missing_log_and_invalid_request(self):
        s = summ(None)
        self.assertEqual(s["status"], "RUNNER_ERROR")
        self.assertFalse(s["expectation_met"])
        s = k.summarize("{not json", OK_BLOCK, TIME, 0, None, None)
        self.assertEqual(s["status"], "REQUEST_INVALID")
        s = summ(OK_BLOCK, request_error="validate step failed")
        self.assertEqual(s["status"], "REQUEST_INVALID")
        s = k.summarize(None, OK_BLOCK, TIME, 0, None, None)
        self.assertEqual(s["status"], "REQUEST_INVALID")

    def test_missing_or_garbled_time_file(self):
        self.assertEqual(summ(OK_BLOCK + FAIL_BLOCK, time=None)["resources"]["time_file"], "MISSING")
        self.assertEqual(summ(OK_BLOCK + FAIL_BLOCK, time="garbage")["resources"]["time_file"], "UNPARSED")
        mac = "      301.52 real       290.10 user         5.33 sys\n  8589934592  maximum resident set size\n"
        res = summ(OK_BLOCK + FAIL_BLOCK, time=mac)["resources"]
        self.assertEqual((res["max_rss_kb"], res["wall"], res["time_file"]), (8388608, "301.52s", "PARSED"))

    def test_should_panic_success_and_cover_shortfall(self):
        req = copy.deepcopy(REQ)
        req["kind"] = "measurement"
        req["harnesses"] = [{"name": P + "smoke::ok", "expect": "SUCCESS"}]
        log = OK_BLOCK.replace("2 of 2 cover", "1 of 2 cover").replace("SUCCESSFUL", "SUCCESSFUL (encountered one or more panics as expected)")
        s = summ(log, req)
        self.assertEqual(s["harnesses"][0]["status"], "SUCCESS")
        self.assertTrue(s["expectation_met"])
        self.assertFalse(s["measurement_ok"])

    def test_measurement_time_limit(self):
        req = copy.deepcopy(REQ)
        req["kind"] = "measurement"
        req["harnesses"] = [{"name": P + "smoke::ok", "expect": "SUCCESS"}]
        self.assertTrue(summ(OK_BLOCK, req)["measurement_ok"])
        self.assertFalse(summ(OK_BLOCK.replace("1.25s", "600.5s"), req)["measurement_ok"])

    def test_bounds_and_truncation(self):
        many = "".join(f"Failed Checks: check {i} " + "x" * 600 + "\n" for i in range(30))
        log = f"Checking harness {P}smoke::control...\n{many}VERIFICATION:- FAILED\n"
        s = summ(OK_BLOCK + log)
        row = s["harnesses"][1]
        self.assertEqual(len(row["failed_checks"]), k.MAX_FAILED_CHECKS)
        self.assertTrue(row["failed_checks_truncated"])
        self.assertTrue(all(len(c) <= k.MAX_LINE_CHARS + 20 for c in row["failed_checks"]))
        errors = "".join(f"error: e{i}\n" for i in range(200))
        s = summ(errors)
        self.assertEqual(len(s["compile_errors"]), k.MAX_COMPILE_LINES)
        self.assertTrue(s["compile_errors_truncated"])
        self.assertLessEqual(len(k.render_md(summ(OK_BLOCK + log)).encode()), k.MAX_MD_BYTES)

    def test_duplicate_and_unrequested_blocks(self):
        log = OK_BLOCK + OK_BLOCK + FAIL_BLOCK + f"Checking harness {P}other::h...\nVERIFICATION:- SUCCESSFUL\n"
        s = summ(log)
        self.assertEqual(s["unrequested_blocks"], [P + "other::h"])
        self.assertTrue(any("more than once" in n for n in s["notes"]))

    def test_nonzero_exit_with_all_success_is_noted(self):
        req = copy.deepcopy(REQ)
        req["harnesses"] = [{"name": P + "smoke::ok", "expect": "SUCCESS"}]
        s = summ(OK_BLOCK, req, exit_code=137)
        self.assertTrue(any("exited 137" in n for n in s["notes"]))


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(Path(k.__file__)), *args], capture_output=True, text=True)

    def test_validate_summarize_gate_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "req.json").write_text(json.dumps(REQ))
            (d / "kani.log").write_text(OK_BLOCK + FAIL_BLOCK)
            r = self.run_cli("validate", str(d / "req.json"), "--args-out", str(d / "args"), "--runner-out", str(d / "runner"))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual((d / "runner").read_text().strip(), "ubuntu-latest")
            self.assertIn("--exact", (d / "args").read_text().split("\n"))
            r = self.run_cli("summarize", "--request", str(d / "req.json"), "--log", str(d / "kani.log"),
                             "--time", str(d / "missing"), "--exit-code", "1", "--out-dir", str(d / "out"))
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(self.run_cli("gate", str(d / "out" / "summary.json")).returncode, 0)
            (d / "kani.log").write_text(OK_BLOCK)
            self.run_cli("summarize", "--request", str(d / "req.json"), "--log", str(d / "kani.log"), "--out-dir", str(d / "out2"))
            self.assertEqual(self.run_cli("gate", str(d / "out2" / "summary.json")).returncode, 1)
            self.assertEqual(self.run_cli("gate", str(d / "nope.json")).returncode, 3)

    def test_validate_rejects_bad_request(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "req.json"
            p.write_text(json.dumps({**REQ, "kind": "x"}))
            r = self.run_cli("validate", str(p), "--args-out", str(Path(d) / "args"))
            self.assertEqual(r.returncode, 2)
            self.assertIn("REQUEST_INVALID", r.stderr)
            self.assertFalse((Path(d) / "args").exists())


if __name__ == "__main__":
    unittest.main()
