"""Synthetic target-map controls; no verifier, compiler, or Cloud work."""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
CHALLENGE = HERE.parent
TARGET = None
TRANSFORM = None


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


TARGET = load("select_callee_r22_control_targets_test",
              HERE / "select-callee-r22-control-targets.py")
TRANSFORM = load("select_callee_r22_transform_test",
                 CHALLENGE / "overnight-assume-actual/r21_fractional_forget.py")
REPAIR = load("select_callee_r22_repair_test",
              CHALLENGE / "overnight-assume-actual/r20_final_select_repair.py")


def _base_source() -> bytes:
    return (
        b"pub unsafe fn checked_forget_owned<T>(t: T)\n" +
        TRANSFORM.FORGET_OLD_CONTRACT + TRANSFORM.FORGET_BODY + b"\n\n" +
        TARGET.SELECT_SIGNATURE + b"/*@ synthetic function contract; @*/\n{\n"
        b"    let true_payload = true_val;\n"
        b"    let false_payload = false_val;\n" +
        TRANSFORM.OPEN_WRAPPERS_ANCHOR +
        b"    let guard = DropOnPanic { inner: guard };\n" +
        TRANSFORM.CLOSE_OWNER_FULL +
        b"        drop.drop_in_place();\n" +
        TRANSFORM.SAVED_GUARD_FULL +
        b"        crate::mem::forget(guard);\n" +
        TRANSFORM.RETURNED_GUARD_FULL +
        REPAIR.PAYLOAD_ASSERTS[0] + REPAIR.PAYLOAD_ASSERTS[1] +
        REPAIR.SELECTED_BLOCK + REPAIR.FINAL_CALL + b"}\n")


def _sources() -> dict[str, bytes]:
    base = _base_source()
    return {variant: TRANSFORM.transform(base, variant)
            for variant in TARGET.VARIANTS}


def _tool_spec() -> bytes:
    lines = [b"// synthetic rsspec line"] * 463
    lines[461] = TARGET.SPEC_PRECONDITION_TEXT["omit-selected-own"].encode()
    lines[462] = TARGET.SPEC_PRECONDITION_TEXT["omit-unselected-own"].encode()
    return b"\n".join(lines) + b"\n"


def _provenance(variant: str) -> dict:
    index = TARGET.VARIANTS.index(variant) + 1
    return {
        "build_id": f"00000000-0000-0000-0000-{index:012d}",
        "brief_log_sha256": hashlib.sha256(
            f"brief-log:{variant}".encode()).hexdigest(),
        "brief_log_index": index,
        "archive_id": f"archive-{variant}",
        "request_id": f"request-{variant}",
    }


def _target_map(sources: dict[str, bytes], tool_spec: bytes) -> dict:
    targets = {}
    for variant, source in sources.items():
        file, line = TARGET._source_anchor(variant, source)
        record = {
            "variant": variant, "observed": True,
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "tool_spec_sha256": hashlib.sha256(tool_spec).hexdigest(),
            "file": file, "line": line,
            "start_column": 21, "end_column": 25,
            "message": f"error: synthetic exact diagnostic for {variant}",
            "provenance": _provenance(variant),
            "log_sha256": "0" * 64,
        }
        if variant in TARGET.SPEC_PRECONDITION_LINE:
            text = tool_spec.splitlines()[line - 1].decode()
            record["tool_precondition"] = {
                "intent": TARGET.SPEC_PRECONDITION_INTENT[variant],
                "line_text": text,
            }
        targets[variant] = record
    for target in targets.values():
        target["log_sha256"] = hashlib.sha256(_log(target).encode()).hexdigest()
    return {"schema": TARGET.SCHEMA, "targets": targets}


def _log_observation(variant: str, source: bytes, record: dict,
                     log_text: str) -> dict:
    return {
        "variant": variant,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "log_sha256": hashlib.sha256(log_text.encode()).hexdigest(),
        "provenance": record["provenance"],
    }


def _log(record: dict, *, file=None, line=None, start=None, end=None,
         message=None) -> str:
    return (f"{file if file is not None else record['file']}"
            f"({line if line is not None else record['line']},"
            f"{start if start is not None else record['start_column']}-"
            f"{end if end is not None else record['end_column']}): "
            f"{message if message is not None else record['message']}\n")


class R22ControlTargetHelperTests(unittest.TestCase):
    def setUp(self):
        self.sources = _sources()
        self.tool_spec = _tool_spec()
        self.map = _target_map(self.sources, self.tool_spec)

    def test_all_seven_caller_declared_targets_bind_to_source_and_tool_bytes(self):
        result = TARGET.validate_target_map(self.map, self.sources, self.tool_spec)
        self.assertEqual(result["schema"], TARGET.RESULT_SCHEMA)
        self.assertEqual(set(result["targets"]), set(TARGET.VARIANTS))
        self.assertIs(result["accepted"], False)
        self.assertIs(result["proof_credit"], False)
        for variant in TARGET.VARIANTS:
            target = self.map["targets"][variant]
            log = _log(target)
            match = TARGET.match_first_and_only_error(
                variant, self.map, self.sources, self.tool_spec, log,
                log_observation=_log_observation(
                    variant, self.sources[variant], target, log))
            self.assertTrue(match["matches_first_and_only_error"])
            self.assertIs(match["accepted"], False)
            self.assertEqual(match["variant"], variant)

    def test_callee_and_no_retained_lines_are_derived_from_unique_anchors(self):
        expected_lines = {
            variant: TARGET._source_anchor(variant, self.sources[variant])[1]
            for variant in TARGET.VARIANTS[:5]
        }
        self.assertEqual(expected_lines["callee-false-normal"],
            expected_lines["callee-owner-duplicate"])
        self.assertEqual(expected_lines["callee-false-normal"],
            expected_lines["callee-thread-duplicate"])
        self.assertGreater(expected_lines["callee-owner-loss"],
                           expected_lines["callee-false-normal"])
        for variant in TARGET.VARIANTS[:5]:
            self.assertEqual(self.map["targets"][variant]["line"],
                             expected_lines[variant])

    def test_no_retained_anchors_are_scoped_to_exact_select_function(self):
        variant = "no-retained-half"
        original = self.sources[variant]
        line = TARGET._source_anchor(variant, original)[1]
        other = (b"\npub fn unrelated() {\n" + TARGET.RETAINED_HALF_MERGE +
                 b"\n" + TARGET.FULL_CELL_ASSERT + b"}\n")
        self.assertEqual(TARGET._source_anchor(variant, original + other)[1], line)
        with self.assertRaises(TARGET.TargetError):
            TARGET._source_anchor(variant,
                original.replace(TARGET.SELECT_SIGNATURE,
                                 TARGET.SELECT_SIGNATURE +
                                 TARGET.SELECT_SIGNATURE, 1))
        spoofed = original.replace(
            TARGET.FULL_CELL_ASSERT,
            TARGET.FULL_CELL_ASSERT + TARGET.FULL_CELL_ASSERT, 1)
        with self.assertRaises(TARGET.TargetError):
            TARGET._source_anchor(variant, spoofed)

    def test_omission_targets_require_pinned_spec_rows_and_intended_precondition(self):
        for variant, line in TARGET.SPEC_PRECONDITION_LINE.items():
            target = self.map["targets"][variant]
            self.assertEqual(target["line"], line)
            self.assertEqual(target["file"], TARGET.TOOL_SPEC_FILE)
            self.assertEqual(target["tool_precondition"]["line_text"],
                             self.tool_spec.splitlines()[line - 1].decode())
            self.assertEqual(target["tool_precondition"]["line_text"],
                             TARGET.SPEC_PRECONDITION_TEXT[variant])
        broken = _target_map(self.sources, self.tool_spec)
        broken["targets"]["omit-selected-own"]["tool_precondition"]["intent"] = \
            TARGET.SPEC_PRECONDITION_INTENT["omit-unselected-own"]
        with self.assertRaises(TARGET.TargetError):
            TARGET.validate_target_map(broken, self.sources, self.tool_spec)

    def test_tool_spec_path_is_exact_relative_or_exact_tool_home_path(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp).resolve()
            absolute = str(home / TARGET.TOOL_SPEC_FILE)
            absolute_map = _target_map(self.sources, self.tool_spec)
            for variant in TARGET.SPEC_PRECONDITION_LINE:
                absolute_map["targets"][variant]["file"] = absolute
            result = TARGET.validate_target_map(
                absolute_map, self.sources, self.tool_spec,
                tool_spec_file=absolute, tool_home=home)
            self.assertEqual(result["targets"]["omit-selected-own"]["file"], absolute)
            with self.assertRaises(TARGET.TargetError):
                TARGET.validate_target_map(
                    absolute_map, self.sources, self.tool_spec,
                    tool_spec_file="/other/tool/bin/rust/std/lib.rsspec",
                    tool_home=home)

    def test_absent_null_wrong_type_unobserved_or_wrong_row_refuse(self):
        bad_maps = [None, [], {"schema": TARGET.SCHEMA},
                    dict(self.map, unexpected=None)]
        for bad in bad_maps:
            with self.subTest(bad=type(bad).__name__), self.assertRaises(TARGET.TargetError):
                TARGET.validate_target_map(bad, self.sources, self.tool_spec)
        for replacement in (None, [], {}):
            broken = _target_map(self.sources, self.tool_spec)
            broken["targets"]["callee-owner-loss"] = replacement
            with self.subTest(target=replacement), self.assertRaises(TARGET.TargetError):
                TARGET.validate_target_map(broken, self.sources, self.tool_spec)
        broken = _target_map(self.sources, self.tool_spec)
        del broken["targets"]["callee-owner-loss"]
        with self.assertRaises(TARGET.TargetError):
            TARGET.validate_target_map(broken, self.sources, self.tool_spec)
        for mutation in (
            lambda row: row.update(observed=False),
            lambda row: row.update(variant="no-retained-half"),
            lambda row: row.update(source_sha256="0" * 64),
            lambda row: row.update(tool_spec_sha256="0" * 64),
            lambda row: row.update(file="wrong.rs"),
            lambda row: row.update(line=row["line"] + 1),
            lambda row: row.update(start_column="21"),
            lambda row: row.update(provenance=None),
            lambda row: row["provenance"].update(brief_log_index=0),
            lambda row: row["provenance"].update(archive_id=""),
            lambda row: row.update(log_sha256="invalid"),
        ):
            broken = _target_map(self.sources, self.tool_spec)
            mutation(broken["targets"]["callee-false-normal"])
            with self.subTest(mutation=mutation), self.assertRaises(TARGET.TargetError):
                TARGET.validate_target_map(broken, self.sources, self.tool_spec)
        broken = _target_map(self.sources, self.tool_spec)
        broken["targets"]["extra"] = {}
        with self.assertRaises(TARGET.TargetError):
            TARGET.validate_target_map(broken, self.sources, self.tool_spec)

    def test_duplicate_missing_contract_body_and_full_cell_anchors_refuse(self):
        for variant in TARGET.VARIANTS[:4]:
            source = self.sources[variant]
            if variant == "callee-owner-loss":
                bad = source.replace(TARGET.FORGET_BODY, b"{\n    changed();\n}", 1)
            else:
                bad = source.replace(TARGET.FORGET_CONTRACTS[variant], b"", 1)
            altered = dict(self.sources, **{variant: bad})
            with self.subTest(variant=variant), self.assertRaises(TARGET.TargetError):
                TARGET.validate_target_map(self.map, altered, self.tool_spec)
        variant = "callee-false-normal"
        source = self.sources[variant]
        duplicated_signature = source.replace(
            TARGET.FORGET_SIGNATURE, TARGET.FORGET_SIGNATURE * 2, 1)
        altered = dict(self.sources, **{variant: duplicated_signature})
        with self.assertRaises(TARGET.TargetError):
            TARGET.validate_target_map(self.map, altered, self.tool_spec)
        duplicated_body = source.replace(
            TARGET.FORGET_BODY, TARGET.FORGET_BODY + TARGET.FORGET_BODY, 1)
        altered = dict(self.sources, **{variant: duplicated_body})
        with self.assertRaises(TARGET.TargetError):
            TARGET.validate_target_map(self.map, altered, self.tool_spec)
        variant = "no-retained-half"
        bad = self.sources[variant].replace(TARGET.FULL_CELL_ASSERT, b"", 1)
        altered = dict(self.sources, **{variant: bad})
        with self.assertRaises(TARGET.TargetError):
            TARGET.validate_target_map(self.map, altered, self.tool_spec)
        duplicated = self.sources[variant].replace(
            TARGET.FULL_CELL_ASSERT,
            TARGET.FULL_CELL_ASSERT + TARGET.FULL_CELL_ASSERT, 1)
        altered = dict(self.sources, **{variant: duplicated})
        with self.assertRaises(TARGET.TargetError):
            TARGET.validate_target_map(self.map, altered, self.tool_spec)

    def test_only_exact_single_diagnostic_matches_and_extra_errors_refuse(self):
        target = self.map["targets"]["callee-owner-duplicate"]
        good = _log(target)
        result = TARGET.match_first_and_only_error(
            "callee-owner-duplicate", self.map, self.sources, self.tool_spec, good,
            log_observation=_log_observation(
                "callee-owner-duplicate", self.sources["callee-owner-duplicate"],
                target, good))
        self.assertTrue(result["matches_first_and_only_error"])
        bad_logs = (
            good + "verified/lib.rs(4,1-2): error: another failure\n",
            "Fatal error: verifier crashed\n" + good,
            _log(target, file="other/lib.rs"),
            _log(target, line=target["line"] + 1),
            _log(target, start=target["start_column"] + 1),
            _log(target, end=target["end_column"] + 1),
            _log(target, message="error: only a matching prefix"),
            "Cannot prove unrelated condition\n",
            "",
            None,
        )
        for log in bad_logs:
            supplied_log = good if log is None else log
            with self.subTest(log=log), self.assertRaises(TARGET.TargetError):
                TARGET.match_first_and_only_error(
                    "callee-owner-duplicate", self.map, self.sources,
                    self.tool_spec, log,
                    log_observation=_log_observation(
                        "callee-owner-duplicate",
                        self.sources["callee-owner-duplicate"], target,
                        supplied_log))
        with self.assertRaises(TARGET.TargetError):
            TARGET.match_first_and_only_error(
                "callee-owner-loss", self.map, self.sources, self.tool_spec, good,
                log_observation=_log_observation(
                    "callee-owner-loss", self.sources["callee-owner-loss"],
                    self.map["targets"]["callee-owner-loss"], good))

    def test_log_observation_must_bind_row_source_content_and_caller_provenance(self):
        variant = "no-retained-half"
        target = self.map["targets"][variant]
        log = _log(target)
        observation = _log_observation(variant, self.sources[variant], target, log)
        self.assertTrue(TARGET.match_first_and_only_error(
            variant, self.map, self.sources, self.tool_spec, log,
            log_observation=observation)["matches_first_and_only_error"])
        mutations = (
            lambda o: o.update(variant="omit-selected-own"),
            lambda o: o.update(source_sha256="0" * 64),
            lambda o: o.update(log_sha256="0" * 64),
            lambda o: o["provenance"].update(request_id="other-request"),
            lambda o: o["provenance"].update(build_id=
                "00000000-0000-0000-0000-000000000999"),
        )
        for mutate in mutations:
            bad = {**observation, "provenance": dict(observation["provenance"])}
            mutate(bad)
            with self.subTest(mutate=mutate), self.assertRaises(TARGET.TargetError):
                TARGET.match_first_and_only_error(
                    variant, self.map, self.sources, self.tool_spec, log,
                    log_observation=bad)


if __name__ == "__main__":
    unittest.main()
