#!/usr/bin/env python3
"""Synthetic tests for cover_parser.py (prototype). Standard library only; no Kani, no real logs.

All logs below are hand-written synthetic records in the terse shape described in COVER-PARSER.md.
None of them is, or summarizes, a real CI log; no test asserts anything about historical covers.

    python3 -B research/challenge-8/audit-2026-11-03/test_cover_parser.py
"""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cover_parser as cp  # noqa: E402

NS = "slice::sort::shared::smallsort::verify::"
A, B, C = NS + "synthetic::alpha", NS + "synthetic::beta", NS + "synthetic::gamma"
NEG = NS + "synthetic::negative_mutant"
IDENT = {"source_commit": "1" * 40, "library_tree": "2" * 40}


def manifest(rows=None, suite="ordinary", **extra):
    m = {"format": cp.MANIFEST_FORMAT, "suite": suite,
         "harnesses": rows if rows is not None else [{"name": A, "expect": "SUCCESS", "covers_total": 2}]}
    m.update(extra)
    return m


def block(name, status="SUCCESSFUL", covers=(2, 2), checks=(0, 100), worker=None, failed=(), time="1.5"):
    lines = [f"Checking harness {name}..."]
    if checks is not None:
        lines.append(f" ** {checks[0]} of {checks[1]} failed")
    for d in failed:
        lines.append(f"Failed Checks: {d}")
    if covers is not None:
        lines.append(f" ** {covers[0]} of {covers[1]} cover properties satisfied")
    if status is not None:
        lines.append(f"VERIFICATION:- {status}")
    if time is not None:
        lines.append(f"Verification Time: {time}s")
    if worker is not None:
        lines = [f"Thread {worker}: {l}" for l in lines]
    return lines


def complete(success, failures):
    return [f"Complete - {success} successfully verified harnesses, {failures} failures, {success + failures} total."]


def log(*parts):
    out = []
    for p in parts:
        out.extend(p)
    return "\n".join(out) + "\n"


def run(m, *texts, exit_=0, ident=None):
    return cp.run(m, [(f"log{i + 1}", t) for i, t in enumerate(texts)], exit_, ident or {})


class SingleAndWorkers(unittest.TestCase):
    def test_single_success_passes(self):
        r = run(manifest(), log(block(A), complete(1, 0)))
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(cp.exit_code(r), 0)
        self.assertEqual(r["success_rows_passed"], 1)

    def test_two_interleaved_workers_bound_by_worker_not_last_checking_line(self):
        # Worker 1 starts alpha, worker 2 starts beta, then alpha's results arrive after beta's
        # Checking line. A "last Checking harness" parser would give alpha's covers 1/2 to beta.
        a, b = block(A, covers=(2, 2), worker=1), block(B, covers=(1, 2), worker=2)
        interleaved = [a[0], b[0]] + a[1:] + b[1:]
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 2},
                      {"name": B, "expect": "SUCCESS", "covers_total": 2}])
        r = run(m, log(interleaved, complete(2, 0)))
        rows = {x["name"]: x for x in r["rows"]}
        self.assertEqual(rows[A]["verdict"], "PASS")
        self.assertEqual(rows[A]["worker"], "1")
        self.assertEqual(rows[B]["verdict"], "FAIL")
        self.assertIn("1 of 2 cover(s) unreached", rows[B]["reason"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_two_interleaved_workers_all_good_passes(self):
        a, b = block(A, worker=1), block(B, worker=2)
        interleaved = [a[0], b[0], a[1], b[1], b[2], a[2], a[3], b[3], b[4], a[4]]
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 2},
                      {"name": B, "expect": "SUCCESS", "covers_total": 2}])
        self.assertEqual(run(m, log(interleaved, complete(2, 0)))["verdict"], "PASS")

    def test_unprefixed_result_line_while_workers_open_is_not_bound(self):
        a = block(A, worker=1)
        text = log([a[0], " ** 2 of 2 cover properties satisfied"], a[1:], complete(1, 0))
        r = run(manifest(), text)
        self.assertNotEqual(r["verdict"], "PASS")
        self.assertTrue(any("without an open harness" in p for p in r["incomplete"]))

    def test_partition_logs_union(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 2},
                      {"name": B, "expect": "SUCCESS", "covers_total": 2}])
        r = run(m, log(block(A), complete(1, 0)), log(block(B), complete(1, 0)))
        self.assertEqual(r["verdict"], "PASS", r)


class CoversAndResults(unittest.TestCase):
    def test_unreached_cover_fails(self):
        r = run(manifest(), log(block(A, covers=(1, 2)), complete(1, 0)))
        self.assertEqual(r["verdict"], "FAIL")
        self.assertNotEqual(cp.exit_code(r), 0)

    def test_missing_result_is_incomplete(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 2},
                      {"name": B, "expect": "SUCCESS", "covers_total": 2}])
        r = run(m, log(block(A), complete(1, 0)))
        self.assertEqual(r["verdict"], "INCOMPLETE")
        self.assertIn(f"{B}: no result record", r["incomplete"])

    def test_missing_cover_record_is_incomplete(self):
        r = run(manifest(), log(block(A, covers=None), complete(1, 0)))
        self.assertEqual(r["verdict"], "INCOMPLETE")

    def test_cover_total_differs_from_manifest(self):
        r = run(manifest(), log(block(A, covers=(3, 3)), complete(1, 0)))
        self.assertEqual(r["verdict"], "FAIL")

    def test_unknown_status_token(self):
        r = run(manifest(), log(block(A, status="MAYBE"), complete(0, 1)))
        self.assertNotEqual(r["verdict"], "PASS")

    def test_timeout_is_not_pass(self):
        lines = block(A, status="FAILED", covers=None, time=None) + ["CBMC timed out. You may want to rerun."]
        r = run(manifest(), log(lines, complete(0, 1)))
        row = r["rows"][0]
        self.assertEqual(row["status"], "TIMEOUT")
        self.assertIn("resource cap, not a counterexample", row["reason"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_oom_is_not_pass(self):
        lines = [f"Checking harness {A}...", "CBMC appears to have run out of memory. You may want to rerun."]
        r = run(manifest(), log(lines, complete(0, 1)))
        self.assertEqual(r["rows"][0]["status"], "OUT_OF_MEMORY")
        self.assertNotEqual(r["verdict"], "PASS")

    def test_truncated_log_is_incomplete(self):
        text = log(block(A)[:3])  # no status/time, no Complete line
        r = run(manifest(), text)
        self.assertEqual(r["verdict"], "INCOMPLETE")
        self.assertEqual(r["rows"][0]["status"], "PARTIAL")
        self.assertTrue(any("no 'Complete" in p for p in r["incomplete"]))

    def test_truncated_after_last_block_without_complete(self):
        r = run(manifest(), log(block(A)))
        self.assertEqual(r["verdict"], "INCOMPLETE")


class MalformedIdentityCounts(unittest.TestCase):
    def test_malformed_cover_counts(self):
        r = run(manifest(), log(block(A, covers=(3, 2)), complete(1, 0)))
        self.assertEqual(r["rows"][0]["status"], "MALFORMED")
        self.assertEqual(r["verdict"], "FAIL")

    def test_non_numeric_counts(self):
        r = run(manifest(), log(block(A, covers=("two", 2)), complete(1, 0)))
        self.assertNotEqual(r["verdict"], "PASS")

    def test_complete_count_mismatch(self):
        r = run(manifest(), log(block(A), complete(2, 0)))
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue(any("'Complete' says" in f for f in r["fail"]))

    def test_malformed_complete_line(self):
        text = log(block(A), ["Complete - 1 successfully verified harnesses, 0 failures, 5 total."])
        self.assertNotEqual(run(manifest(), text)["verdict"], "PASS")

    def test_identity_mismatch(self):
        m = manifest(identity=IDENT)
        r = run(m, log(block(A), complete(1, 0)), ident={**IDENT, "library_tree": "3" * 40})
        self.assertEqual(r["verdict"], "FAIL")

    def test_identity_missing_is_incomplete(self):
        r = run(manifest(identity=IDENT), log(block(A), complete(1, 0)), ident={"source_commit": "1" * 40})
        self.assertEqual(r["verdict"], "INCOMPLETE")

    def test_identity_match_passes(self):
        r = run(manifest(identity=IDENT), log(block(A), complete(1, 0)), ident=dict(IDENT))
        self.assertEqual(r["verdict"], "PASS")


class DuplicatesConflicts(unittest.TestCase):
    def test_duplicate_identical_records_not_pass(self):
        r = run(manifest(), log(block(A), block(A), complete(2, 0)))
        self.assertEqual(r["verdict"], "INCOMPLETE")
        self.assertIn("duplicate", r["rows"][0]["reason"])

    def test_conflicting_records_across_partitions_fail(self):
        r = run(manifest(), log(block(A), complete(1, 0)), log(block(A, covers=(1, 2)), complete(1, 0)))
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("conflicting", r["rows"][0]["reason"])

    def test_restart_on_same_worker_before_end(self):
        a = block(A, worker=1)
        text = log(a[:2], block(B, worker=1), complete(1, 0))
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 2},
                      {"name": B, "expect": "SUCCESS", "covers_total": 2}])
        self.assertNotEqual(run(m, text)["verdict"], "PASS")

    def test_unexpected_smallsort_row_fails(self):
        r = run(manifest(), log(block(A), block(C), complete(2, 0)))
        self.assertEqual(r["verdict"], "FAIL")
        self.assertTrue(any("not in the manifest" in f for f in r["fail"]))

    def test_other_namespace_rows_kept_apart(self):
        other = "num::verify::check_unchecked_add_i8"
        r = run(manifest(), log(block(other, covers=None), block(A), complete(2, 0)))
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(r["other_namespaces"], {"num": 1})
        self.assertEqual(r["success_rows_passed"], 1)


class VerifierExit(unittest.TestCase):
    def test_verifier_exit_1_with_full_covers_is_not_pass_and_preserved(self):
        r = run(manifest(), log(block(A), complete(1, 0)), exit_=1)
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(cp.exit_code(r), 1)

    def test_verifier_exit_unknown_is_incomplete(self):
        r = run(manifest(), log(block(A), complete(1, 0)), exit_=None)
        self.assertEqual(r["verdict"], "INCOMPLETE")

    def test_parser_failure_with_verifier_exit_preserved(self):
        r = run(manifest(), log(block(A, covers=(0, 2)), complete(1, 0)), exit_=137)
        self.assertEqual(cp.exit_code(r), 137)


class Expectations(unittest.TestCase):
    def test_unknown_cover_total_not_treated_as_zero(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": "UNKNOWN"}])
        r = run(m, log(block(A, covers=None), complete(1, 0)))
        self.assertEqual(r["verdict"], "INCOMPLETE")
        self.assertIn("UNKNOWN (not treated as 0)", r["rows"][0]["reason"])

    def test_missing_cover_total_defaults_to_unknown(self):
        m = manifest([{"name": A, "expect": "SUCCESS"}])
        self.assertEqual(run(m, log(block(A), complete(1, 0)))["verdict"], "INCOMPLETE")

    def test_explicit_zero_rejected_without_policy(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 0}])
        r = run(m, log(block(A, covers=None), complete(1, 0)))
        self.assertEqual(r["verdict"], "INPUT_ERROR")
        self.assertEqual(cp.exit_code(r), 12)

    def test_explicit_zero_allowed_by_policy(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 0}],
                     cover_policy={"explicit_zero_allowed": True})
        self.assertEqual(run(m, log(block(A, covers=None), complete(1, 0)))["verdict"], "PASS")

    def test_explicit_zero_but_covers_reported(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 0}],
                     cover_policy={"explicit_zero_allowed": True})
        self.assertEqual(run(m, log(block(A, covers=(1, 1)), complete(1, 0)))["verdict"], "FAIL")

    def test_negative_in_ordinary_set_is_input_error(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 2},
                      {"name": NEG, "expect": "FAILED", "expect_check": "oracle", "covers_total": 1}])
        r = run(m, log(block(A), complete(1, 0)))
        self.assertEqual(r["verdict"], "INPUT_ERROR")
        self.assertTrue(any("ordinary set" in e for e in r["fail"]))

    def test_controls_suite_expected_failure_counted_separately(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 2},
                      {"name": NEG, "expect": "FAILED", "expect_check": "oracle", "covers_total": 1}],
                     suite="controls", expected_verifier_exit=1)
        neg = block(NEG, status="FAILED", covers=(1, 1), checks=(1, 50), failed=['"oracle mismatch"'])
        r = run(m, log(block(A), neg, complete(1, 1)), exit_=1)
        self.assertEqual(r["verdict"], "PASS", r)
        self.assertEqual(r["success_rows_passed"], 1)
        self.assertEqual(r["expected_failures_met"], 1)

    def test_controls_failure_at_wrong_check(self):
        m = manifest([{"name": NEG, "expect": "FAILED", "expect_check": "oracle", "covers_total": 1}],
                     suite="controls", expected_verifier_exit=1)
        neg = block(NEG, status="FAILED", covers=(1, 1), checks=(1, 50), failed=['"index out of bounds"'])
        self.assertEqual(run(m, log(neg, complete(0, 1)), exit_=1)["verdict"], "FAIL")

    def test_controls_without_declared_exit_is_input_error(self):
        m = manifest([{"name": NEG, "expect": "FAILED", "expect_check": "oracle", "covers_total": 1}],
                     suite="controls")
        self.assertEqual(run(m, log(complete(0, 0)))["verdict"], "INPUT_ERROR")

    def test_panic_cut_root_with_only_panic_cover_is_input_error(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 1, "panic_cut": True,
                       "covers": [{"label": "panic stub reached", "kind": "panic"}]}])
        self.assertEqual(run(m, log(block(A, covers=(1, 1)), complete(1, 0)))["verdict"], "INPUT_ERROR")

    def test_panic_cut_root_with_route_witness(self):
        covers = [{"label": "normal return", "kind": "route"}, {"label": "panic stub reached", "kind": "panic"}]
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 2, "panic_cut": True, "covers": covers}])
        self.assertEqual(run(m, log(block(A, covers=(2, 2)), complete(1, 0)))["verdict"], "PASS")
        r = run(m, log(block(A, covers=(1, 2)), complete(1, 0)))
        self.assertEqual(r["verdict"], "FAIL")
        self.assertIn("route witness not established", r["rows"][0]["reason"])

    def test_manifest_expected_count_mismatch(self):
        self.assertEqual(run(manifest(expected_count=202), log(block(A), complete(1, 0)))["verdict"], "INPUT_ERROR")

    def test_manifest_duplicate_name(self):
        m = manifest([{"name": A, "expect": "SUCCESS", "covers_total": 2}] * 2)
        self.assertEqual(run(m, log(block(A), complete(1, 0)))["verdict"], "INPUT_ERROR")

    def test_no_log_is_not_pass(self):
        self.assertEqual(cp.run(manifest(), [], 0, {})["verdict"], "INCOMPLETE")


class Cli(unittest.TestCase):
    def test_cli_round_trip_and_exit(self):
        with tempfile.TemporaryDirectory() as d:
            mp, lp = os.path.join(d, "m.json"), os.path.join(d, "a.log")
            with open(mp, "w") as f:
                json.dump(manifest(identity=IDENT), f)
            with open(lp, "w") as f:
                f.write(log(block(A), complete(1, 0)))
            args = ["--manifest", mp, "--log", lp, "--verifier-exit", "0",
                    "--identity", "source_commit=" + "1" * 40, "--identity", "library_tree=" + "2" * 40]
            out, err = io.StringIO(), io.StringIO()
            with redirect_stdout(out), redirect_stderr(err):
                code = cp.main(args)
            self.assertEqual(code, 0, err.getvalue())
            self.assertEqual(json.loads(out.getvalue())["verdict"], "PASS")
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(cp.main(args[:6]), 11)  # identities not observed -> INCOMPLETE
                self.assertEqual(cp.main(["--manifest", mp, "--log", lp, "--verifier-exit", "2"]), 2)
                self.assertEqual(cp.main(["--manifest", mp, "--identity", "bogus=1"]), 12)


if __name__ == "__main__":
    unittest.main(verbosity=1)
