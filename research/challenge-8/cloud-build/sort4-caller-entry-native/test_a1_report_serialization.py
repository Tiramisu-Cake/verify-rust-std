"""Lossless R9 report disk view; AST-only extraction, no runner/proof execution."""
import ast
import copy
import json
from pathlib import Path
from collections.abc import Mapping
import unittest

SOURCE = Path(__file__).with_name("a1-runner.py")
TREE = ast.parse(SOURCE.read_text())
PHASE_ASSIGN = next(node for node in TREE.body if isinstance(node, ast.Assign) and
                    any(isinstance(target, ast.Name) and target.id == "AUTHORIZATION_PHASE"
                        for target in node.targets))
CASE_ORDER_ASSIGN = next(node for node in TREE.body if isinstance(node, ast.Assign) and
                         any(isinstance(target, ast.Name) and target.id == "CASE_ORDER"
                             for target in node.targets))
REPORT_FUNCTION = next(node for node in TREE.body if isinstance(node, ast.FunctionDef) and
                       node.name == "_report_value_for_disk")
CODE = compile(ast.Module(body=[PHASE_ASSIGN, CASE_ORDER_ASSIGN, REPORT_FUNCTION], type_ignores=[]),
               str(SOURCE), "exec")
NS = {"Mapping": Mapping}
exec(CODE, NS)
PHASE = "SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9"
NS["AUTHORIZATION_PHASE"] = PHASE
CASE_ORDER = NS["CASE_ORDER"]
report_value_for_disk = NS["_report_value_for_disk"]


def pointer_get(root, pointer):
    if pointer == "":
        return root
    if not pointer.startswith("/"):
        raise AssertionError("invalid JSON pointer")
    value = root
    for token in pointer[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def expand_report(disk_value):
    expanded = copy.deepcopy(disk_value)
    for row in expanded.get("observed_rows", []):
        reference = row.pop("observation_ref", None)
        if reference is not None:
            if reference.get("schema") != "a1-observation-ref-v1":
                raise AssertionError("unknown reference schema")
            row["observation"] = copy.deepcopy(pointer_get(expanded, reference["json_pointer"]))
    expanded.pop("report_serialization", None)
    return expanded


def sample_report():
    case_ids = list(CASE_ORDER)
    observation = {
        "status": "PARTIAL", "blob": "repeated semantic observation " * 180,
        "source_units": [{"unit_id": "unit/α", "source_id": "src~β"}],
        "normal_unwind": {"outcome": "unwind-observed", "proof_credit": False},
        "error": {"kind": "collector-error", "message": "synthetic"},
        "not_run": {"status": "NOT_RUN", "observed_stage": None, "proof_credit": False},
        "partial": {"status": "PARTIAL", "artifact": {"path": None}},
        "missing_artifact_path": {"status": "ERROR", "artifact": {}},
        "unsigned_128": (1 << 127) + 0x123456789ABCDEF,
    }
    details = {case_id: {**observation, "case_id": case_id} for case_id in case_ids}
    # Non-matrix observations are part of the source record and must remain in the map.
    details["prepare-admission-controls"] = {
        "status": "ERROR", "adapter_error": "CallBindingError: synthetic",
        "progress": {"partial": True, "artifact": {"path": None}},
    }
    return {
        "authorization_phase_id": PHASE,
        "classification": "A1_RUNNER_OBSERVED_LIFECYCLE",
        "proof_credit": False, "accepted": False,
        "matrix_complete": False, "diagnostic_complete": False,
        "case_order": case_ids,
        "case_status": {case_id: {"status": "NOT_RUN", "proof_credit": False}
                        for case_id in case_ids},
        "source_units": observation["source_units"],
        "execution_events": [{"event": "normal-unwind", "proof_credit": False}],
        "observed_rows": [
            {"case_id": case_id, "source_id": f"src-{i}", "unit_id": f"unit-{i}",
             "observation": copy.deepcopy(details[case_id]),
             "status": {"status": "NOT_RUN", "proof_credit": False}}
            for i, case_id in enumerate(case_ids)],
        "observation_details": details,
        "first_blocker": {"event": "adapter_error", "case_id": "prepare-admission-controls"},
    }


class ReportSerializationTests(unittest.TestCase):
    def test_r9_disk_pointers_roundtrip_all_26_rows_and_unknown_details(self):
        original = sample_report()
        disk = report_value_for_disk(original, PHASE)
        self.assertIsNot(disk, original)
        self.assertEqual(disk["report_serialization"], {
            "kind": "row-pointer-v1", "lossless": True, "proof_credit": False})
        self.assertEqual(len(disk["observed_rows"]), 26)
        self.assertEqual([row["case_id"] for row in disk["observed_rows"]], list(CASE_ORDER))
        self.assertEqual(disk["observed_rows"][0]["status"], original["observed_rows"][0]["status"])
        self.assertIn("prepare-admission-controls", disk["observation_details"])
        self.assertEqual(expand_report(json.loads(json.dumps(disk))), original)
        for key in ("case_order", "case_status", "source_units", "execution_events",
                    "first_blocker", "proof_credit", "accepted", "matrix_complete"):
            self.assertEqual(expand_report(disk)[key], original[key])

    def test_pointer_escapes_unicode_slash_and_tilde_case_ids(self):
        case_id = "ユニコード/one~two"
        observation = {"status": "PARTIAL", "proof_credit": False}
        value = {"authorization_phase_id": PHASE, "observed_rows": [
                    {"case_id": case_id, "observation": copy.deepcopy(observation)}],
                 "observation_details": {case_id: observation}}
        disk = report_value_for_disk(value, PHASE)
        self.assertEqual(disk["observed_rows"][0]["observation_ref"], {
            "schema": "a1-observation-ref-v1",
            "json_pointer": "/observation_details/ユニコード~1one~0two"})
        self.assertEqual(expand_report(disk), value)

    def test_repeated_observations_reduce_size_without_losing_payload(self):
        original = sample_report()
        original_json = json.dumps(original, sort_keys=True)
        disk = report_value_for_disk(original, PHASE)
        disk_json = json.dumps(disk, sort_keys=True)
        self.assertLess(len(disk_json), len(original_json) * 3 // 4)
        self.assertEqual(expand_report(json.loads(disk_json)), original)
        first_id = CASE_ORDER[0]
        self.assertEqual(original["observed_rows"][0]["observation"],
                         original["observation_details"][first_id])

    def test_wrong_phase_and_malformed_root_shapes_are_noop(self):
        original = sample_report()
        for value, phase in (
            (original, "another-phase"),
            ({**original, "authorization_phase_id": "another-phase"}, PHASE),
            ({**original, "observed_rows": None}, PHASE),
            ({**original, "observation_details": None}, PHASE),
            ({**original, "observation_details": []}, PHASE),
            ({**original, "report_serialization": {"kind": "prior"}}, PHASE),
        ):
            with self.subTest(phase=phase, keys=tuple(value)):
                self.assertIs(report_value_for_disk(value, phase), value)

    def test_older_authorization_phases_never_enable_r9_compaction(self):
        current = sample_report()
        for older_phase in (
                "SORT4-PACKAGE-SCOPE-NATIVE-PROOF-2026-10-20-R6",
                "SORT4-PACKAGING-NATIVE-PROOF-2026-10-20-R7",
                "SORT4-POST-MIGRATION-NATIVE-PROOF-2026-10-20-R8"):
            with self.subTest(older_phase=older_phase):
                NS["AUTHORIZATION_PHASE"] = older_phase
                old_report = {**current, "authorization_phase_id": older_phase}
                self.assertTrue(report_value_for_disk(old_report, older_phase) is old_report)
                self.assertTrue(report_value_for_disk(current, older_phase) is current)
        NS["AUTHORIZATION_PHASE"] = PHASE

    def test_missing_null_and_wrongtype_observations_remain_inline(self):
        base = sample_report()
        rows = [
            {"case_id": "missing", "observation": {"status": "PARTIAL"}},
            {"case_id": "null", "observation": None},
            {"case_id": "wrong", "observation": "source-error"},
            {"case_id": "valid", "observation": {"status": "PARTIAL"}},
        ]
        details = {"null": None, "wrong": {"status": "PARTIAL"},
                   "valid": {"status": "PARTIAL"}}
        partial = {**base, "observed_rows": rows, "observation_details": details}
        disk = report_value_for_disk(partial, PHASE)
        self.assertEqual(disk["observed_rows"][:3], rows[:3])
        self.assertEqual(disk["observed_rows"][3]["observation_ref"], {
            "schema": "a1-observation-ref-v1", "json_pointer": "/observation_details/valid"})
        self.assertEqual(expand_report(disk), partial)

    def test_conflicting_values_or_duplicate_case_ids_keep_entire_report_inline(self):
        base = sample_report()
        conflict = copy.deepcopy(base)
        conflict["observed_rows"][0]["observation"]["status"] = "different"
        self.assertTrue(report_value_for_disk(conflict, PHASE) is conflict)
        bool_integer = {**base, "observed_rows": [
            {"case_id": "one", "observation": {"value": True}}],
            "observation_details": {"one": {"value": 1}}}
        self.assertTrue(report_value_for_disk(bool_integer, PHASE) is bool_integer)
        duplicate = copy.deepcopy(base)
        duplicate["observed_rows"][1]["case_id"] = duplicate["observed_rows"][0]["case_id"]
        self.assertTrue(report_value_for_disk(duplicate, PHASE) is duplicate)

    def test_nonmapping_rows_and_nonstring_case_ids_are_noop(self):
        base = sample_report()
        for row in (None, {"case_id": 7, "observation": {"status": "PARTIAL"}}):
            malformed = {**base, "observed_rows": [row]}
            self.assertTrue(report_value_for_disk(malformed, PHASE) is malformed)


if __name__ == "__main__":
    unittest.main()
