#!/usr/bin/env python3
"""Synthetic checks of mac_autoharness (run: python3 -B test_mac_autoharness.py)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mac_autoharness as mac  # noqa: E402

P = "slice::sort::shared::smallsort::verify::"


def block(t, name, status="SUCCESSFUL", vt="10.0", covers=(1, 1), checks=(0, 5, 2), prefix=P):
    out = [f"Thread {t}: Checking harness {prefix}{name}..."]
    if checks:
        out += [f"Thread {t}: SUMMARY:", f"Thread {t}:  ** {checks[0]} of {checks[1]} failed ({checks[2]} unreachable)"]
    if covers:
        out.append(f"Thread {t}:  ** {covers[0]} of {covers[1]} cover properties satisfied")
    if status:
        out.append(f"Thread {t}: VERIFICATION:- {status}")
    if vt is not None:
        out.append(f"Thread {t}: Verification Time: {vt}s")
    return out


def footer(total, ok):
    return [f"Complete - {ok} successfully verified harnesses, {total - ok} failures, {total} total."]


class T(unittest.TestCase):
    def run_case(self, lines, expected, cands, sizes=None, exit_code="0"):
        """cands: (group, covers or '*', short name); sizes default to the observed group sizes."""
        if sizes is None:
            sizes = {}
            for g, _, _ in cands:
                sizes[g] = sizes.get(g, 0) + 1
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            if lines is not None:
                (d / "log").write_text("\n".join(lines) + "\n")
            (d / "exp").write_text("\n".join(P + n for n in expected) + "\n")
            (d / "cand").write_text("\n".join(f"{g} {c} {P}{n}" for g, c, n in cands) + "\n")
            return mac.summarize(d / "log", d / "exp", d / "cand", sizes, 300.0, exit_code, {})

    def dec(self, s, g):
        return s["groups"][g]["decision"]

    def test_clean_run_admit_and_demote(self):
        a, b = block(1, "a", vt="100.0"), block(2, "b", vt="400.0")
        lines = [x for pair in zip(a, b) for x in pair] + footer(2, 2)
        s = self.run_case(lines, ["a", "b"], [("g1", 1, "a"), ("g2", 1, "b")])
        self.assertTrue(s["evidence_integrity"] and s["job_success"])
        self.assertEqual(s["rows"][P + "a"]["time_s"], 100.0)
        self.assertEqual((self.dec(s, "g1"), self.dec(s, "g2")), ("ADMIT", "DEMOTE"))

    def test_package_demoted_as_whole(self):
        lines = block(1, "a") + block(2, "b", vt="400.0") + footer(2, 2)
        s = self.run_case(lines, ["a", "b"], [("m9", 1, "a"), ("m9", 1, "b")])
        self.assertEqual(self.dec(s, "m9"), "DEMOTE")

    def test_group_size_enforced(self):
        lines = block(1, "a") + block(2, "b") + footer(2, 2)
        with self.assertRaises(ValueError):
            self.run_case(lines, ["a", "b"], [("m9", 1, "a")], sizes={"m9": 2})
        with self.assertRaises(ValueError):
            self.run_case(lines, ["a", "b"], [("m9", 1, "a"), ("x", 1, "a")], sizes={"m9": 1, "x": 1})
        with self.assertRaises(ValueError):
            self.run_case(lines, ["a", "b"], [("zz", 1, "a")], sizes={"m9": 1})
        with self.assertRaises(ValueError):
            self.run_case(lines, ["a"], [("m9", 1, "zzz")])

    def test_integrity_blocks_all_groups(self):
        base = block(1, "a") + block(2, "b")
        cases = {
            "other_missing": (base + footer(2, 2), ["a", "b", "c"], "0"),
            "no_footer": (base, ["a", "b"], "0"),
            "exit1_footer_clean": (base + footer(2, 2), ["a", "b"], "1"),
            "footer_total_mismatch": (base + footer(3, 3), ["a", "b"], "0"),
            "rustc_error": (["error[E0425]: cannot find value"] + base + footer(2, 2), ["a", "b"], "0"),
            "overlap": (["Thread 1: Checking harness " + P + "z..."] + base + footer(3, 2), ["a", "b", "z"], "1"),
            "prefixed_orphan": (base + ["Thread 99: Verification Time: 999s"] + footer(2, 2), ["a", "b"], "0"),
            "unclosed_tail": (base + ["Thread 3: Checking harness num::x..."], ["a", "b"], "0"),
            "log_absent": (None, ["a", "b"], "1"),
            "success_with_failed_checks": (block(1, "a") + block(2, "b", checks=(1, 5, 0)) + footer(2, 2),
                                           ["a", "b"], "0"),
        }
        for label, (lines, expected, rc) in cases.items():
            with self.subTest(label):
                s = self.run_case(lines, expected, [("g", 1, "a")], exit_code=rc)
                self.assertFalse(s["evidence_integrity"], label)
                self.assertFalse(s["job_success"], label)
                self.assertEqual(self.dec(s, "g"), "BLOCKED", label)

    def test_explained_timeout_keeps_other_groups(self):
        lines = (block(1, "a") + ["Thread 2: Checking harness " + P + "b...", "Thread 2: CBMC timed out. x",
                                  "Thread 2: VERIFICATION:- FAILED", "Thread 2: Verification Time: 600.1s"]
                 + block(2, "c") + footer(3, 2))
        s = self.run_case(lines, ["a", "b", "c"], [("g1", 1, "a"), ("g2", 1, "b")], exit_code="1")
        self.assertTrue(s["evidence_integrity"], s["integrity_problems"])
        self.assertFalse(s["job_success"])
        self.assertEqual(s["rows"][P + "b"]["status"], "TIMEOUT")
        self.assertEqual((self.dec(s, "g1"), self.dec(s, "g2")), ("ADMIT", "DEMOTE"))

    def test_timeout_marker_without_time_then_reuse(self):
        lines = (["Thread 1: Checking harness " + P + "a...", "Thread 1: VERIFICATION:- FAILED",
                  "Thread 1: CBMC timed out. x"] + block(1, "b") + footer(2, 1))
        s = self.run_case(lines, ["a", "b"], [("g", 1, "a")], exit_code="1")
        self.assertTrue(s["evidence_integrity"], s["integrity_problems"])
        self.assertEqual(s["rows"][P + "a"]["status"], "TIMEOUT")
        self.assertIsNone(s["rows"][P + "a"]["time_s"])

    def test_classes(self):
        lines = (block(1, "a") + ["Thread 1: Checking harness " + P + "b...",
                                  "Thread 1: CBMC appears to have run out of memory"]
                 + block(2, "c", covers=None) + block(3, "d", covers=(0, 1))
                 + block(1, "e", status="FAILED", checks=(1, 5, 0)) + block(2, "f", covers=(2, 2)) + footer(6, 4))
        s = self.run_case(lines, list("abcdef"), [(g, 1, g) for g in "abcdef"], exit_code="1")
        self.assertTrue(s["evidence_integrity"], s["integrity_problems"])
        got = {g: self.dec(s, g) for g in "abcdef"}
        self.assertEqual(got, {"a": "ADMIT", "b": "DEMOTE", "c": "BLOCKED", "d": "BLOCKED",
                               "e": "CORRECTNESS_FAILURE", "f": "BLOCKED"})

    def test_star_covers_and_zero_vt(self):
        lines = block(1, "a", vt="0.0", covers=(3, 3)) + footer(1, 1)
        s = self.run_case(lines, ["a"], [("returns", "*", "a")])
        self.assertEqual(self.dec(s, "returns"), "ADMIT")
        self.assertEqual(s["rows"][P + "a"]["time_s"], 0.0)

    def test_other_failure_or_oom_requires_review(self):
        for label, other in (("failed", block(2, "x", status="FAILED", checks=(1, 5, 0), prefix="num::")),
                             ("oom", ["Thread 2: Checking harness num::x...",
                                      "Thread 2: CBMC appears to have run out of memory"])):
            with self.subTest(label):
                s = self.run_case(block(1, "a") + other + footer(2, 1), ["a"], [("g", 1, "a")], exit_code="1")
                self.assertTrue(s["evidence_integrity"], s["integrity_problems"])
                self.assertFalse(s["job_success"])
                self.assertTrue(s["manual_review_required"])
                self.assertEqual(self.dec(s, "g"), "ADMIT_PENDING_REVIEW")

    def test_candidate_timeout_needs_no_review(self):
        lines = (block(1, "a") + ["Thread 2: Checking harness " + P + "b...", "Thread 2: CBMC timed out. x"]
                 + footer(2, 1))
        s = self.run_case(lines, ["a", "b"], [("g1", 1, "a"), ("g2", 1, "b")], exit_code="1")
        self.assertFalse(s["manual_review_required"])
        self.assertEqual((self.dec(s, "g1"), self.dec(s, "g2")), ("ADMIT", "DEMOTE"))

    def test_missing_or_signal_exit_blocks(self):
        lines = block(1, "a") + block(2, "b", status="FAILED", checks=(1, 5, 0)) + footer(2, 1)
        for rc in ("MISSING", "", "x1", "137"):
            with self.subTest(rc):
                s = self.run_case(lines, ["a", "b"], [("g", 1, "a")], exit_code=rc)
                self.assertFalse(s["evidence_integrity"])
                self.assertEqual(self.dec(s, "g"), "BLOCKED")

    def test_contradictory_status_blocks(self):
        b = block(1, "a")
        lines = b[:4] + ["Thread 1: VERIFICATION:- FAILED"] + b[4:] + footer(1, 1)
        s = self.run_case(lines, ["a"], [("g", 1, "a")])
        self.assertFalse(s["evidence_integrity"])
        self.assertEqual(self.dec(s, "g"), "BLOCKED")
        lines = b[:3] + b[2:] + footer(1, 1)
        s = self.run_case(lines, ["a"], [("g", 1, "a")])
        self.assertFalse(s["evidence_integrity"])


class Mac4(T):
    def test_autoharness_functions_and_should_panic(self):
        lines = (block(1, "a")
                 + ["Thread 2: Autoharness: Checking function num::f against all possible inputs...",
                    "Thread 2:  ** 0 of 5 failed", "Thread 2: VERIFICATION:- SUCCESSFUL",
                    "Thread 2: Verification Time: 0.1s"]
                 + block(3, "x_should_panic", checks=(1, 5, 0), prefix="num::") + footer(2, 2))
        s = self.run_case(lines, ["a"], [("g", 1, "a")])
        self.assertTrue(s["evidence_integrity"], s["integrity_problems"])
        self.assertEqual(self.dec(s, "g"), "ADMIT")

    def test_smallsort_success_with_failed_checks_still_blocks(self):
        lines = block(1, "a", checks=(1, 5, 0)) + footer(1, 1)
        s = self.run_case(lines, ["a"], [("g", 1, "a")])
        self.assertFalse(s["evidence_integrity"])


if __name__ == "__main__":
    unittest.main()
