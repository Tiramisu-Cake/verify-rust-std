"""Synthetic R23 callee-lane registration checks; no Cloud dispatch."""
from __future__ import annotations

import base64
import importlib.util
import json
import lzma
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
CLOUD = HERE.parent
LEDGER = HERE / "BUDGET-A1-ACTUAL-SELECT-2026-10-23-R23.json"
PHASE = "SORT4-ACTUAL-SELECT-2026-10-23-R23"
ROUTE_MARKER = "SORT4-ACTUAL-SELECT-2026-10-23-R21"
REPO = CLOUD.parents[2]
INSIDE = "2026-10-23T07:45:00Z"
LANE = "o26-select-callee-r20"
OTHER_LANE = "o26-sort4-c1-current-recovery"

sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location("r23_registration_control", CLOUD / "control.py")
CONTROL = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CONTROL
spec.loader.exec_module(CONTROL)


def clock(text):
    import datetime as real
    fixed = real.datetime.fromisoformat(text.replace("Z", "+00:00"))

    class Fixed(real.datetime):
        @classmethod
        def now(cls, tz=None):
            return fixed if tz is not None else fixed.replace(tzinfo=None)

        @classmethod
        def utcnow(cls):
            return fixed.replace(tzinfo=None)
    return SimpleNamespace(datetime=Fixed, timezone=real.timezone,
                           timedelta=real.timedelta)


def at(text):
    return patch.object(CONTROL, "datetime", clock(text))


def authorized_ledger():
    return {
        "phase": PHASE,
        "phase_id": PHASE,
        "status": "AUTHORIZED",
        "authorization": "synthetic isolated R23 registration test",
        "owner": "select-sort4",
        "task_id": "select-callee-acceptance-autonomous-2026-10-23-r23",
        "ceiling_build_seconds": 3600,
        "allowed_lanes": [LANE],
        "start_utc": "2026-10-23T07:37:19Z",
        "main_deadline_utc": "2026-10-23T09:37:19Z",
        "deadline_utc": "2026-10-23T10:07:19Z",
        "maximum_builds": None,
        "maximum_build_timeout_seconds": 1200,
        "report_reserve_seconds": 240,
    }


class R23CalleeRegistration(unittest.TestCase):
    def test_exact_window_and_single_approved_lane(self):
        self.assertEqual(CONTROL.A1_R23_PHASE, PHASE)
        self.assertEqual((CONTROL.A1_R23_START, CONTROL.A1_R23_MAIN_DEADLINE,
                          CONTROL.A1_R23_DEADLINE, CONTROL.A1_R23_CEILING),
                         ("2026-10-23T07:37:19Z", "2026-10-23T09:37:19Z",
                          "2026-10-23T10:07:19Z", 3600))
        self.assertEqual(CONTROL.A1_R23_LANES, {LANE})
        recipe = json.loads((CLOUD / "recipes" / (LANE + ".json")).read_text())
        self.assertEqual(recipe["lane"], LANE)
        with at(INSIDE):
            deadline = CONTROL.authorized_phase(
                SimpleNamespace(phase_id=PHASE, owner="select-sort4"), authorized_ledger())
        self.assertEqual(deadline.isoformat(), "2026-10-23T10:07:19+00:00")

    def test_installed_ledger_is_a_fresh_r23_account(self):
        ledger = json.loads(LEDGER.read_text())
        self.assertEqual((ledger["phase"], ledger["phase_id"], ledger["status"]),
                         (PHASE, PHASE, "AUTHORIZED"))
        self.assertEqual((ledger["ceiling_build_seconds"], ledger["carry_seconds"]), (3600, 0))
        self.assertEqual(ledger["used_build_seconds"] + ledger["remaining_build_seconds"],
                         3600)
        for key, value in authorized_ledger().items():
            if key != "authorization":
                self.assertEqual(ledger[key], value, key)

    def test_exact_fresh_account_required(self):
        args = SimpleNamespace(phase_id=PHASE, owner="select-sort4")
        mismatches = (
            {"owner": "other"}, {"start_utc": "2026-10-22T22:25:07Z"},
            {"main_deadline_utc": "2026-10-23T00:25:07Z"},
            {"deadline_utc": "2026-10-23T00:55:07Z"},
            {"deadline_utc": "2026-10-23T00:55:05Z"},
            {"maximum_build_timeout_seconds": 1201}, {"maximum_builds": 1},
            {"allowed_lanes": [OTHER_LANE]}, {"allowed_lanes": [LANE, OTHER_LANE]},
            {"ceiling_build_seconds": 3601}, {"report_reserve_seconds": 239},
            {"status": "CLOSED"}, {"phase": "SORT4-ACTUAL-SELECT-2026-10-23-R21"},
        )
        for delta in mismatches:
            with self.subTest(delta=delta), at(INSIDE), self.assertRaises(SystemExit):
                CONTROL.authorized_phase(args, dict(authorized_ledger(), **delta))
        with at("2026-10-23T10:07:19Z"), self.assertRaisesRegex(SystemExit, "deadline has passed"):
            CONTROL.authorized_phase(args, authorized_ledger())

    def test_runner_marker_reuses_r20_variable_with_r23_value(self):
        def forbidden(*_args, **_kwargs):
            raise AssertionError("callee lane must not read the A1 profile")
        with patch.object(CONTROL.subprocess, "check_output", forbidden):
            env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        # The route marker stays the R21 literal of the approved candidate.
        self.assertIn("SORT4_R20_CALLEE_PHASE_ID=" + ROUTE_MARKER, env)
        self.assertIn("SORT4_R23_SESSION_PHASE_ID=" + PHASE, env)
        self.assertNotIn("SORT4_R20_CALLEE_PHASE_ID=" + PHASE, env)
        self.assertIn("LANE=" + LANE, env)
        self.assertFalse(any(item.startswith("SORT4_A1_") for item in env))
        with self.assertRaises(SystemExit):
            CONTROL.envs("a" * 40, "b" * 40, OTHER_LANE, PHASE)

    def test_timeout_budget_and_source_transport(self):
        config = CONTROL.config("a" * 40, "b" * 40, LANE, 1200, "token", phase_id=PHASE)
        self.assertEqual(config["timeout"], "1200s")
        execute_script = config["steps"][0]["args"][1]
        self.assertIn(" + 960 - 60 ", execute_script)
        self.assertIn('"960s"', execute_script)
        for invalid in (269, 1201):
            with self.subTest(seconds=invalid), self.assertRaises(ValueError):
                CONTROL.config("a" * 40, "b" * 40, LANE, invalid, "token", phase_id=PHASE)

        payload = b"synthetic R23 source payload\x00"
        encoded, command = CONTROL.source_restore_transport(payload, PHASE)
        self.assertEqual(lzma.decompress(base64.b64decode(encoded)), payload)
        self.assertIn("lzma.decompress", command)
        old_encoded, old_command = CONTROL.source_restore_transport(payload, CONTROL.A1_R21_PHASE)
        self.assertEqual(lzma.decompress(base64.b64decode(old_encoded)), payload)
        self.assertEqual(command, old_command)

        legacy_encoded, legacy_command = CONTROL.source_restore_transport(payload, "unrelated-phase")
        import gzip
        self.assertEqual(gzip.decompress(base64.b64decode(legacy_encoded)), payload)
        self.assertIn("gzip --decompress", legacy_command)

    def test_submit_refuses_after_main_window_and_out_of_range_timeout(self):
        def forbidden(*_args, **_kwargs):
            raise AssertionError("Cloud/coordinator reached")
        cases = (("2026-10-23T09:37:19Z", 1200, "main window ended"),
                 (INSIDE, 269, "timeout must be270..1200"),
                 (INSIDE, 1201, "timeout must be270..1200"),
                 (INSIDE, 600, "requires full timeout 1200"),
                 ("2026-10-23T09:13:00Z", 1200, "do not fit main window"))
        for now, timeout, reason in cases:
            args = SimpleNamespace(command="submit", phase_id=PHASE, owner="select-sort4",
                                   timeout=timeout, lane=LANE, source_mode="pinned-objects",
                                   infra_sha="a" * 40, proof_sha="b" * 40)
            with self.subTest(now=now, timeout=timeout), at(now), \
                    patch.object(CONTROL, "invoke", forbidden), \
                    patch.object(CONTROL.coordination, "request", forbidden), \
                    self.assertRaisesRegex(SystemExit, reason):
                CONTROL.run_command(args, None, authorized_ledger(), None)

    def test_route_marker_matches_every_pinned_consumer_literal(self):
        """Static control: the exported marker equals each pinned route literal."""
        import hashlib
        import re
        env = CONTROL.envs("a" * 40, "b" * 40, LANE, PHASE)
        exported = [item.split("=", 1)[1] for item in env
                    if item.startswith("SORT4_R20_CALLEE_PHASE_ID=")]
        self.assertEqual(exported, [ROUTE_MARKER])
        patch_path = (REPO / "research/challenge-8/overnight-assume-actual" /
                      "verifast-r22-fractional-forget-26.10.patch")
        raw = patch_path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "219f3dc0ffcae5422cf7daa4e052291b7d5ee04a64a80dd4728519704961de8d")
        literals = re.findall(rb'getenv_opt "SORT4_R20_CALLEE_PHASE_ID" =\s*\+?\s*Some "([^"]+)"', raw)
        self.assertEqual(len(literals), 3)
        self.assertEqual({item.decode() for item in literals}, {ROUTE_MARKER})
        for name in ("select-callee-r21-fractional.py",
                     "select-callee-r21-fractional-proof-entry.py"):
            text = (CLOUD / name).read_text()
            self.assertEqual(re.findall(r"^PHASE = '([^']+)'$", text, re.M),
                             [ROUTE_MARKER], name)
        runner = (CLOUD / "run-o26-select-callee-r20.sh").read_text()
        self.assertIn('"${SORT4_R20_CALLEE_PHASE_ID:-}" == ' + ROUTE_MARKER, runner)
        # A phase-valued marker would be refused by the pinned translator.
        self.assertNotIn(PHASE.encode(), raw)

    def test_parser_fix_is_pinned_transported_and_parser_only(self):
        """Static control for the R22 coefficient/type-predicate parser patch."""
        import hashlib
        rel = ("research/challenge-8/overnight-assume-actual/"
               "verifast-r22-coef-typepred-parser-26.10.patch")
        raw = (REPO / rel).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(digest,
                         "dfdaff604314ecf0e27c44320811096f05a8bd8833910c59321fdec33de7b0e5")
        files = [line for line in raw.decode().splitlines() if line.startswith("+++ ")]
        self.assertEqual(files, ["+++ b/src/rust_frontend/vf_mir_translator/rust_parser.ml"])
        added = [line[1:] for line in raw.decode().splitlines()
                 if line.startswith("+") and not line.startswith("+++")]
        self.assertIn('          ] -> CoefAsn (l, coef, p)', added)
        self.assertNotIn("SORT4", "".join(added))
        recipe = json.loads((CLOUD / "recipes" / (LANE + ".json")).read_text())
        self.assertIn(rel, recipe["proof_paths"])
        runner = (CLOUD / "run-o26-select-callee-r20.sh").read_text()
        self.assertIn(digest, runner)
        for pin in ("7bf12f1205ecf033e3bf66f11b4326c20d2876d68e19006d5db59f3e45ae91c2",
                    "6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246"):
            self.assertIn(pin, runner)
        order = [runner.index(marker) for marker in (
            "stage fractional-refresh-apply", "stage parser-refresh-check",
            "stage parser-refresh-apply", "stage console-build")]
        self.assertEqual(order, sorted(order))
        # The translator pin is re-asserted after the parser patch.
        after = runner[runner.index("stage parser-refresh-apply"):]
        self.assertIn("cadaa80ab55e6fb3f53ccfcae1ab05dc953a2cb69a17616654d49dad6350478f",
                      after[:after.index("deps_archive=")])

    def test_fractional_patch_ghost_literals_match_transform_and_pins(self):
        """Static control: patch ghost text and rows equal the R22 transform/pins."""
        import importlib.util as iu
        transform_path = REPO / "research/challenge-8/overnight-assume-actual/r21_fractional_forget.py"
        spec_ = iu.spec_from_file_location("r22_fractional_transform", transform_path)
        transform = iu.module_from_spec(spec_)
        spec_.loader.exec_module(transform)
        raw = (REPO / "research/challenge-8/overnight-assume-actual/"
               "verifast-r22-fractional-forget-26.10.patch").read_text()
        half = transform.RETURNED_GUARD_HALF.decode()
        merge_line = [line for line in half.splitlines() if "merge_fractions" in line]
        self.assertEqual(merge_line,
                         ["             merge_fractions points_to::<*Element>(saved_guard.inner, _); } @*/"])
        # open_owner certificate: the first two transform lines verbatim.
        first_two = half.splitlines(keepends=True)[:2]
        literal = "".join('+      "%s" ^\n' % line.replace("\n", "\\n") for line in first_two)
        self.assertIn(literal, raw)
        # expected ghost statement list: the same block without indentation.
        ghost = ("/*@ { open [1/2] <select_unpredictable::DropOnPanic<*Element>>.own(t, saved_guard);"
                 "\\n             merge_fractions points_to::<*Element>(saved_guard.inner, _); } @*/")
        self.assertIn('+      "' + ghost + '";', raw)
        self.assertNotIn("merge_fractions *saved_guard.inner", raw)
        pins = json.loads((REPO / "research/challenge-8/task-history/select-callee-r22/"
                           "FRACTIONAL-FINGERPRINT-INPUT.json").read_text())
        for name, row in pins["variants"].items():
            snaps = row["fingerprint"]["snapshots"]
            entry = '("%s", "%s", "%s", "%s", "%s")' % (
                name, row["verified_sha256"], snaps["body-6"]["sha256"],
                snaps["body-7"]["sha256"], snaps["unit"]["sha256"])
            self.assertIn(entry, raw, name)

    def test_historical_r21_and_r20_admission_constants_unchanged(self):
        self.assertEqual((CONTROL.A1_R21_START, CONTROL.A1_R21_MAIN_DEADLINE,
                          CONTROL.A1_R21_DEADLINE, CONTROL.A1_R21_CEILING),
                         ("2026-10-22T19:54:55Z", "2026-10-22T21:54:55Z",
                          "2026-10-22T22:24:55Z", 3600))
        self.assertEqual(CONTROL.A1_R21_LANES, {LANE})
        self.assertEqual((CONTROL.A1_R20_START, CONTROL.A1_R20_DEADLINE),
                         ("2026-10-22T15:41:28Z", "2026-10-22T18:11:28Z"))
        r21 = dict(authorized_ledger(), phase=CONTROL.A1_R21_PHASE,
                   phase_id=CONTROL.A1_R21_PHASE,
                   start_utc=CONTROL.A1_R21_START,
                   main_deadline_utc=CONTROL.A1_R21_MAIN_DEADLINE,
                   deadline_utc=CONTROL.A1_R21_DEADLINE,
                   task_id="select-callee-acceptance-autonomous-2026-10-23-r21")
        with at("2026-10-22T20:30:00Z"):
            CONTROL.authorized_phase(SimpleNamespace(phase_id=CONTROL.A1_R21_PHASE,
                                                     owner="select-sort4"), r21)
        # The R21 window cannot be reused under the R23 phase.
        with at(INSIDE), self.assertRaises(SystemExit):
            CONTROL.authorized_phase(SimpleNamespace(phase_id=PHASE, owner="select-sort4"),
                                     dict(r21, phase=PHASE, phase_id=PHASE))

if __name__ == "__main__":
    unittest.main()
