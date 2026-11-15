"""Synthetic tests for the B3 T1 comparator; no Kani/CBMC tools are run."""

import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
import copy
from pathlib import Path
from unittest.mock import patch

MODULE = Path("/root/kani-b3-t1/.github/b3-t1/compare.py")
spec = importlib.util.spec_from_file_location("b3_compare", MODULE)
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)
REAL_RUN = subprocess.run


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Fixture:
    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.payloads = {}
        self.rows = {"control" if i == 0 else row: {
            "expected_harnesses": [f"h-{i}"], "captured_harnesses": [f"h-{i}"], "exit": 1
        } for i, row in enumerate(["control", *compare.PERF_ROWS])}
        self.indexes = {}
        for arm in ("A1", "B1", "A2"):
            (self.root / arm).mkdir()
            recs = {}
            for i, row in enumerate(self.rows):
                harness = f"h-{i}"
                for kind in ("final", "linked", "symtab", "metadata"):
                    key = f"{kind}/{row}/{harness if kind == 'final' else 'evidence'}"
                    data = f"{kind} {row} baseline\n".encode()
                    if arm == "B1" and row == "control" and kind == "final":
                        data = b"model control wrapper changed\n"
                    recs[key] = self.add_record(arm, key, row, kind, data,
                                               harness if kind == "final" else None)
            self.indexes[arm] = {"complete": True, "records": recs, "rows": copy.deepcopy(self.rows),
                                 "tools": {name: ("c" if arm == "B1" and name in {"kani-driver", "kani-compiler"}
                                                   else "a") * 64 for name in compare.REQUIRED_TOOLS},
                                 "locks": {name: "e" * 64 for name in compare.REQUIRED_LOCKS}}
            self.save(arm)

    def add_record(self, arm, key, row, kind, data, harness=None):
        path_name = hashlib.sha256(key.encode()).hexdigest() + ".goto"
        path = self.root / arm / "files" / path_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self.payloads[(arm, key)] = data
        rec = {"sha256": digest(data), "path": f"files/{path_name}", "kind": kind, "row": row}
        if harness is not None:
            rec.update(harness=harness, argv=["cbmc", "--json-ui", "--json-ui"], cwd="/work/src")
        return rec

    def update_data(self, arm, key, data):
        rec = self.indexes[arm]["records"][key]
        (self.root / arm / rec["path"]).write_bytes(data)
        self.payloads[(arm, key)] = data
        rec["sha256"] = digest(data)
        self.save(arm)

    def save(self, arm):
        (self.root / arm / "index.json").write_text(json.dumps(self.indexes[arm]))

    def mutate_record(self, arm, key, field, value):
        self.indexes[arm]["records"][key][field] = value
        self.save(arm)

    def close(self):
        self.tmp.cleanup()


def fake_dump(argv, **kwargs):
    kwargs["stdout"].write(f"dump {' '.join(argv)}\n".encode())
    kwargs["stderr"].write(b"")
    return subprocess.CompletedProcess(argv, 0)


def fake_run(argv, **kwargs):
    if argv[0] == "diff":
        return REAL_RUN(argv, **kwargs)
    return fake_dump(argv, **kwargs)


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.fx = Fixture()

    def tearDown(self):
        self.fx.close()

    def run_compare(self):
        return compare.compare(self.fx.root, "/mock/goto-instrument")

    def test_control_detected_perf_equal_pending_review(self):
        with patch.object(compare.subprocess, "run", side_effect=fake_run) as run:
            result = self.run_compare()
        self.assertEqual(result["status"], "CONTROL_WRAPPER_REVIEW_REQUIRED")
        self.assertTrue(result["perf_models_equal"])
        self.assertEqual(result["control_expectation"], "tag-<union>::<arm>")
        self.assertEqual(run.call_count, 6)
        self.assertTrue((self.fx.root / "compare/RESULT.json").is_file())
        self.assertTrue(list((self.fx.root / "compare").rglob("*.diff")))

    def test_perf_named_model_difference_is_pending_review(self):
        key = f"final/{compare.PERF_ROWS[0]}/h-1"
        data = b"changed perf model\n"
        self.fx.update_data("B1", key, data)
        with patch.object(compare.subprocess, "run", side_effect=fake_run):
            result = self.run_compare()
        self.assertFalse(result["perf_models_equal"])
        self.assertEqual(result["perf_differences"], [key])
        self.assertEqual(result["status"], "CONTROL_WRAPPER_REVIEW_REQUIRED")

    def test_a_a_difference_dumps_common_models_and_reports_provenance_without_b_conclusion(self):
        key = f"final/{compare.PERF_ROWS[0]}/h-1"
        data = b"A2 generated a distinct model\n"
        self.fx.update_data("A2", key, data)
        self.fx.indexes["A2"]["tools"]["cbmc"] = "f" * 64
        self.fx.save("A2")
        with patch.object(compare.subprocess, "run", side_effect=fake_run) as run:
            result = self.run_compare()
        self.assertEqual(result["status"], "INCONCLUSIVE_AA")
        self.assertEqual(result["control_gate"], "NOT_EVALUATED")
        self.assertEqual(result["a_a_hash_differences"], [key])
        self.assertIn("tools.cbmc", result["metadata_drift"])
        self.assertIn(f"records.{key}.sha256", result["metadata_drift"])
        self.assertEqual(result["differing_model_records"], [key])
        self.assertEqual(result["diffs"], [{"record": key, "classification": "A_A_MODEL_DRIFT_INCONCLUSIVE"}])
        self.assertEqual(len(list((self.fx.root / "compare/A1-A2").rglob("*.diff"))), 2)
        self.assertEqual(run.call_count, 6)
        self.assertFalse("control_differences" in result)

    def test_control_symtab_only_difference_is_invalid(self):
        final_key = "final/control/h-0"
        symtab_key = "symtab/control/evidence"
        self.fx.update_data("B1", final_key, self.fx.payloads[("A1", final_key)])
        self.fx.update_data("B1", symtab_key, b"changed symtab only\n")
        result = self.run_compare()
        self.assertEqual(result["status"], "INVALID")
        self.assertEqual(result["control_gate"], "INVALID_CONTROL")
        self.assertTrue(any("final model is insensitive" in error for error in result["errors"]))

    def test_sanitized_pair_names_are_collision_resistant(self):
        self.assertNotEqual(compare._record_ident("x/y"), compare._record_ident("x_y"))

    def test_control_insensitive_is_invalid(self):
        key = "final/control/h-0"
        data = self.fx.payloads[("A1", key)]
        self.fx.update_data("B1", key, data)
        result = self.run_compare()
        self.assertEqual(result["status"], "INVALID")
        self.assertEqual(result["control_gate"], "INVALID_CONTROL")

    def test_backend_argv_change_is_invalid(self):
        key = f"final/{compare.PERF_ROWS[0]}/h-1"
        self.fx.mutate_record("B1", key, "argv", ["cbmc", "--different"])
        self.assertEqual(self.run_compare()["status"], "INVALID")

    def test_invalid_input_matrix(self):
        cases = [
            ("records", None), ("rows", []), ("tools", {}), ("locks", None),
        ]
        for field, value in cases:
            with self.subTest(field=field):
                original = self.fx.indexes["A1"][field]
                self.fx.indexes["A1"][field] = value
                self.fx.save("A1")
                self.assertEqual(self.run_compare()["status"], "INVALID")
                self.fx.indexes["A1"][field] = original
                self.fx.save("A1")

    def test_missing_file_hash_mismatch_wrong_type_and_empty_fields_invalid(self):
        key = f"final/{compare.PERF_ROWS[0]}/h-1"
        rec = self.fx.indexes["A1"]["records"][key]
        with self.subTest(error="hash"):
            old = rec["sha256"]
            rec["sha256"] = "0" * 64
            self.fx.save("A1")
            self.assertEqual(self.run_compare()["status"], "INVALID")
            rec["sha256"] = old
            self.fx.save("A1")
        with self.subTest(error="path missing"):
            old = rec["path"]
            rec["path"] = "missing.goto"
            self.fx.save("A1")
            self.assertEqual(self.run_compare()["status"], "INVALID")
            rec["path"] = old
            self.fx.save("A1")
        for field, value in (("argv", None), ("cwd", "relative"), ("row", ""), ("kind", None)):
            with self.subTest(field=field):
                old = rec.get(field)
                rec[field] = value
                self.fx.save("A1")
                self.assertEqual(self.run_compare()["status"], "INVALID")
                rec[field] = old
                self.fx.save("A1")

    def test_nonzero_dump_fails_closed_and_logs_exit(self):
        def fail(argv, **kwargs):
            kwargs["stdout"].write(b"partial")
            kwargs["stderr"].write(b"failure")
            return subprocess.CompletedProcess(argv, 7)
        with patch.object(compare.subprocess, "run", side_effect=fail):
            result = self.run_compare()
        self.assertEqual(result["status"], "INVALID")
        self.assertEqual(result["control_gate"], "INVALID_DUMP")
        log = next((self.fx.root / "compare").rglob("A1.symbol-table.json"))
        self.assertEqual(json.loads(log.read_text())["exit"], 7)

    def test_timeout_is_logged_and_invalid(self):
        def timeout(argv, **kwargs):
            raise subprocess.TimeoutExpired(argv, compare.DUMP_TIMEOUT_SECONDS)
        with patch.object(compare.subprocess, "run", side_effect=timeout):
            result = self.run_compare()
        self.assertEqual(result["status"], "INVALID")
        self.assertEqual(result["control_gate"], "INVALID_DUMP")
        log = next((self.fx.root / "compare").rglob("A1.symbol-table.json"))
        details = json.loads(log.read_text())
        self.assertTrue(details["timed_out"])
        self.assertEqual(details["timeout_seconds"], 120)

    def test_row_inventory_and_tool_requirements(self):
        # Replace one expected perf name while preserving the count.
        self.fx.indexes["A1"]["rows"]["wrong-perf-name"] = self.fx.indexes["A1"]["rows"].pop(compare.PERF_ROWS[-1])
        self.fx.save("A1")
        self.assertEqual(self.run_compare()["status"], "INVALID")
        self.fx.indexes["A1"]["rows"][compare.PERF_ROWS[-1]] = self.fx.indexes["A1"]["rows"].pop("wrong-perf-name")
        del self.fx.indexes["A1"]["tools"]["kissat"]
        self.fx.save("A1")
        self.assertEqual(self.run_compare()["status"], "INVALID")

    def test_lock_file_paths_and_exit_code_are_required(self):
        lock = next(iter(self.fx.indexes["A1"]["locks"]))
        del self.fx.indexes["A1"]["locks"][lock]
        self.fx.save("A1")
        self.assertEqual(self.run_compare()["status"], "INVALID")
        self.fx.indexes["A1"]["locks"][lock] = "e" * 64
        self.fx.indexes["A1"]["rows"]["control"]["exit"] = 0
        self.fx.save("A1")
        self.assertEqual(self.run_compare()["status"], "INVALID")

    def test_final_record_must_match_harness_inventory_exactly(self):
        key = f"final/{compare.PERF_ROWS[0]}/h-1"
        del self.fx.indexes["A1"]["records"][key]
        self.fx.save("A1")
        self.assertEqual(self.run_compare()["status"], "INVALID")

    def test_duplicate_final_record_is_invalid(self):
        row = compare.PERF_ROWS[0]
        key = f"final/{row}/duplicate"
        self.fx.indexes["A1"]["records"][key] = self.fx.add_record("A1", key, row, "final", b"duplicate", "h-1")
        self.fx.save("A1")
        self.assertEqual(self.run_compare()["status"], "INVALID")


if __name__ == "__main__":
    unittest.main()
