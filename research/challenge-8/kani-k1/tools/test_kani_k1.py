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
        self.bad({**part, "controls": True}, "no uninit_checks, no controls")
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


if __name__ == "__main__":
    unittest.main()
