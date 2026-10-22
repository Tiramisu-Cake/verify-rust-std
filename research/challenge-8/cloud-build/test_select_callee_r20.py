"""Synthetic service tests for the R20 callee lane helper, runner and recipe."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("r20_select_callee", HERE / "select-callee-r20.py")
CALLEE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CALLEE)
RECIPE = json.loads((HERE / "recipes/o26-select-callee-r20.json").read_text())
RUNNER = (HERE / "run-o26-select-callee-r20.sh").read_text()
ENV = {"SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
       "SORT4_R20_CALLEE_PHASE_ID": "SORT4-ACTUAL-SELECT-2026-10-22-R20"}
UNIT = (b"fn select_unpredictable() {\n"
        b"    /*@ assert *true_ptr |-> ?true_payload; @*/\n"
        b"    /*@ assert *false_ptr |-> ?false_payload; @*/\n"
        b"        crate::intrinsics::select_unpredictable(condition, true_val, false_val).assume_init()\n"
        b"}\n")


class FakeO26:
    def __init__(self, exit_code=1, raise_on=None):
        self.calls, self.exit_code, self.raise_on = [], exit_code, raise_on

    def proof_stage(self, repo, case, tool_home, schema, sysroot, deadline, name, label):
        if self.raise_on == name:
            raise RuntimeError("synthetic stage exception")
        self.calls.append((case, name, label, (case / "verified/lib.rs").read_bytes()))
        return {"status": "RAN", "exit": self.exit_code, "source_unchanged": True}


class Args:
    def __init__(self, root, deadline):
        self.repo = ROOT
        self.cloud_dir = HERE
        self.evidence = root
        self.tool_home = root / "tool"
        self.schema = root / "schema.capnp"
        self.compiler_sysroot = root / "sysroot"
        self.deadline_epoch = deadline


def make_case(root):
    case = root / "cases/candidate/capture" / CALLEE.CASE
    (case / "verified").mkdir(parents=True)
    (case / "original").mkdir()
    (case / "verified/lib.rs").write_bytes(UNIT)
    (case / "original/lib.rs").write_bytes(b"original\n")


class RepairStage(unittest.TestCase):
    def run_repair(self, fake, deadline_offset=3600, env=ENV):
        real_load = CALLEE.load
        def load(path, name, expected=None):
            return fake if path.name == "o26-recipe.py" else real_load(path, name, expected)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            make_case(root)
            import time
            with patch.dict(os.environ, env, clear=True), patch.object(CALLEE, "load", load):
                record = CALLEE.repair(Args(root, int(time.time()) + deadline_offset))
            saved = json.loads((root / "cases/r20-repair/r20-repair.json").read_text())
            original = (root / "cases/candidate/capture" / CALLEE.CASE / "verified/lib.rs").read_bytes()
        return record, saved, original

    def test_three_ghost_variants_run_on_copies_and_base_is_untouched(self):
        fake = FakeO26()
        record, saved, original = self.run_repair(fake)
        self.assertEqual(original, UNIT)
        self.assertEqual([c[1] for c in fake.calls], ["r20-both", "r20-true-only", "r20-false-only"])
        self.assertEqual([c[3].count(b"close_MaybeUninit_pointer_own") for c in fake.calls], [2, 1, 1])
        self.assertTrue(all(c[2] == "refresh" for c in fake.calls))
        self.assertEqual(saved, json.loads(json.dumps(record)))
        self.assertFalse(record["accepted"]) ; self.assertFalse(record["proof_credit"])
        self.assertEqual({v["stage"]["exit"] for v in record["variants"].values()}, {1})
        self.assertIs(record["complete"], True)

    def test_deadline_reserve_not_run_exits_nonzero_and_record_is_incomplete(self):
        fake = FakeO26()
        with self.assertRaises(SystemExit) as raised:
            self.run_repair(fake, deadline_offset=60)
        self.assertEqual(raised.exception.code, 3)
        self.assertEqual(fake.calls, [])

    def test_intermediate_record_is_marked_incomplete(self):
        with self.assertRaisesRegex(RuntimeError, "synthetic stage exception"):
            with tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                make_case(root)
                fake = FakeO26(raise_on="r20-true-only")
                real_load = CALLEE.load
                def load(path, name, expected=None):
                    return fake if path.name == "o26-recipe.py" else real_load(path, name, expected)
                import time
                try:
                    with patch.dict(os.environ, ENV, clear=True), patch.object(CALLEE, "load", load):
                        CALLEE.repair(Args(root, int(time.time()) + 3600))
                finally:
                    saved = json.loads((root / "cases/r20-repair/r20-repair.json").read_text())
                    self.assertIs(saved["complete"], False)
                    self.assertEqual(list(saved["variants"]), ["both"])

    def test_refusals_preserve_original_exception(self):
        for env in ({}, {**ENV, "SORT4_R20_CALLEE_PHASE_ID": "other"},
                    {**ENV, "GITHUB_ACTIONS": "true"}, {**ENV, "SMALLSORT_EXECUTION_PROVIDER": "local"}):
            with self.subTest(env=env), self.assertRaises(RuntimeError):
                self.run_repair(FakeO26(), env=env)
        with self.assertRaisesRegex(RuntimeError, "synthetic stage exception"):
            self.run_repair(FakeO26(raise_on="r20-true-only"))

    def test_transform_pin_matches_committed_bytes(self):
        raw = (ROOT / CALLEE.REPAIR_REL).read_bytes()
        self.assertEqual(CALLEE.sha(raw), CALLEE.REPAIR_SHA256)
        with tempfile.TemporaryDirectory() as temp:
            bad = Path(temp) / "x.py"
            bad.write_bytes(raw + b"\n")
            with self.assertRaises(RuntimeError):
                CALLEE.load(bad, "bad_pin", CALLEE.REPAIR_SHA256)


class Audit(unittest.TestCase):
    def test_audit_records_missing_partial_and_wrong_type_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            ev = Path(temp)
            (ev / "source-preflight-exit-code.txt").write_text("0\n")
            (ev / "candidate-capture-exit-code.txt").write_text("x\n")
            (ev / "source-preflight.json").write_text("{not json")
            out = ev / "proof-audit.json"
            args = type("A", (), {"evidence": ev, "output": out, "runner_exit": 2,
                                  "failed_stage": "candidate-capture"})
            record = CALLEE.audit(args)
            self.assertEqual(json.loads(out.read_text()), record)
        self.assertEqual(record["stage_exits"], {"source-preflight": 0, "candidate-capture": None})
        self.assertEqual(record["source_preflight"], {"unreadable": "source-preflight.json"})
        self.assertIsNone(record["baseline_proof"])
        self.assertFalse(record["evidence_complete"]) ; self.assertFalse(record["proof_credit"])

    def test_evidence_complete_requires_a_baseline_proof_that_ran(self):
        rows = ({"stage": {"status": "RAN", "exit": 1}}, True, 0), \
               ({"stage": {"status": "NOT_RUN_DEADLINE", "exit": None}}, False, 0), \
               ({"stage": {"status": "RAN", "exit": "1"}}, False, 0), \
               ({"stage": None}, False, 0), (None, False, 0), \
               ({"stage": {"status": "RAN", "exit": 1}}, False, 2)
        for proof, complete, runner_exit in rows:
            with self.subTest(proof=proof, runner=runner_exit), tempfile.TemporaryDirectory() as temp:
                ev = Path(temp)
                if proof is not None:
                    (ev / "cases/candidate").mkdir(parents=True)
                    (ev / "cases/candidate/proof-stage.json").write_text(json.dumps(proof))
                args = type("A", (), {"evidence": ev, "output": ev / "a.json",
                                      "runner_exit": runner_exit, "failed_stage": "x"})
                self.assertIs(CALLEE.audit(args)["evidence_complete"], complete)


class RunnerAndRecipe(unittest.TestCase):
    def test_runner_syntax_lane_guard_and_stage_order(self):
        subprocess.run(["bash", "-n", str(HERE / "run-o26-select-callee-r20.sh")], check=True)
        self.assertIn('"$1" == o26-select-callee-r20', RUNNER)
        self.assertIn('"${SORT4_R20_CALLEE_PHASE_ID:-}" == SORT4-ACTUAL-SELECT-2026-10-22-R20', RUNNER)
        order = ["stage provider-overlays", "stage source-preflight", "stage package-index",
                 "stage console-build", "stage candidate-capture", "stage candidate-source-compare",
                 "stage candidate-proof"]
        positions = [RUNNER.index(x) for x in order]
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn("o26-refresh-audit.py", RUNNER)
        self.assertNotIn("stage r20-repair-variants", RUNNER)
        self.assertNotIn("select-callee-r20.py\" repair", RUNNER)

    def test_evidence_directory_exists_before_any_write_or_stage(self):
        mk = RUNNER.index('mkdir "$ev"\n')
        self.assertLess(RUNNER.index('[[ ! -e "$ev" ]]'), mk)
        self.assertLess(mk, RUNNER.index('mkdir "$ev/cases"\n'))
        writes = [m.start() for m in re.finditer(r'> "\$ev/', RUNNER)]
        self.assertTrue(writes)
        self.assertLess(mk, min(writes))
        self.assertLess(mk, RUNNER.index("\nstage "))
        self.assertLess(mk, RUNNER.index('python3 "$cloud_dir/provider.py"'))
        self.assertNotIn("run-sort4-c1-current-recovery", RUNNER)
        self.assertIn("0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a", RUNNER)

    def test_recipe_is_minimal_exact_and_in_scope(self):
        self.assertEqual(RECIPE["lane"], "o26-select-callee-r20")
        self.assertIn(RECIPE["entrypoint"], RECIPE["infra_paths"])
        for key in ("proof_paths", "infra_paths"):
            paths = RECIPE[key]
            self.assertEqual(paths, sorted(set(paths)))
            self.assertTrue(all(p.startswith(("research/challenge-8/", "library/core/")) for p in paths))
            self.assertTrue(all((ROOT / p).is_file() for p in paths), key)
        self.assertFalse(any("a1-actual-body" in p or "A1-ACTUAL" in p or "actual-sort4-c2" in p
                             for p in RECIPE["proof_paths"] + RECIPE["infra_paths"]))

    def test_runner_repo_paths_are_transported(self):
        refs = set(re.findall(r'\$proof_root/research/challenge-8/([A-Za-z0-9_./-]+)', RUNNER))
        for ref in refs:
            self.assertIn("research/challenge-8/" + ref, RECIPE["proof_paths"], ref)
        manifest = json.loads((ROOT / "research/challenge-8/overnight-linkage/O26-PROFILE-MANIFEST.json").read_text())
        refresh = json.loads((ROOT / "research/challenge-8/overnight-assume-actual/O26-REFRESH-PROFILE.json").read_text())
        for row in manifest["patches_in_application_order"] + refresh["refresh_patches"]:
            self.assertIn("research/challenge-8/" + row["path"], RECIPE["proof_paths"])
        for name in ("o26-recipe.py", "o26-refresh-recipe.py", "provider.py", "select-callee-r20.py"):
            self.assertIn("research/challenge-8/cloud-build/" + name, RECIPE["infra_paths"])


if __name__ == "__main__":
    unittest.main()
