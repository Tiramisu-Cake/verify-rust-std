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
CURRENT_BUILD_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
TOOL_HOME = Path("/synthetic/tool")


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
                     log_text: str, *, tool_spec: bytes,
                     stage: dict | None = None,
                     log_path: str | None = None) -> dict:
    raw = log_text.encode("utf-8")
    source_hashes = {
        "original/lib.rs": hashlib.sha256(b"synthetic original source").hexdigest(),
        "verified/lib.rs": hashlib.sha256(source).hexdigest(),
    }
    if stage is None:
        stage = {
            "status": "RAN", "exit": 1,
            "argv": [str(TOOL_HOME / "bin/verifast"), "-rustc_args",
                     "--edition 2021", "-verbose", "1", "verified/lib.rs"],
            "source_before": source_hashes, "source_after": source_hashes,
            "source_unchanged": True, "intrinsic_gate_active": True,
            "pointer_drop_gate_active": True,
            "stdout": "r20-merged-optin.log", "stderr": "r20-merged-optin.log",
        }
    return {
        "build_id": CURRENT_BUILD_ID,
        "variant": variant,
        "source_hashes": source_hashes,
        "tool_spec_sha256": hashlib.sha256(tool_spec).hexdigest(),
        "log_path": log_path or TARGET.CURRENT_LOG_RELATIVE.format(variant=variant),
        "log_sha256": hashlib.sha256(raw).hexdigest(),
        "stage": stage,
    }


def _match(variant: str, log_text: str, *, observation: dict | None = None,
           target_map: dict | None = None):
    target = (target_map or _ACTIVE_MAP)["targets"][variant]
    raw = log_text.encode("utf-8") if isinstance(log_text, str) else None
    observation_text = log_text if isinstance(log_text, str) else _log(target)
    current = observation or _log_observation(
        variant, _ACTIVE_SOURCES[variant], target, observation_text,
        tool_spec=_ACTIVE_TOOL_SPEC)
    return TARGET.match_first_and_only_error(
        variant, target_map or _ACTIVE_MAP, _ACTIVE_SOURCES, _ACTIVE_TOOL_SPEC,
        log_text, log_bytes=raw, log_observation=current,
        expected_build_id=CURRENT_BUILD_ID, tool_home=TOOL_HOME)


def _log(record: dict, *, file=None, line=None, start=None, end=None,
         message=None) -> str:
    return (f"{file if file is not None else record['file']}"
            f"({line if line is not None else record['line']},"
            f"{start if start is not None else record['start_column']}-"
            f"{end if end is not None else record['end_column']}): "
            f"{message if message is not None else record['message']}\n")


class R22ControlTargetHelperTests(unittest.TestCase):
    def setUp(self):
        global _ACTIVE_MAP, _ACTIVE_SOURCES, _ACTIVE_TOOL_SPEC
        self.sources = _sources()
        self.tool_spec = _tool_spec()
        self.map = _target_map(self.sources, self.tool_spec)
        _ACTIVE_MAP, _ACTIVE_SOURCES, _ACTIVE_TOOL_SPEC = (
            self.map, self.sources, self.tool_spec)

    def test_all_seven_caller_declared_targets_bind_to_source_and_tool_bytes(self):
        result = TARGET.validate_target_map(self.map, self.sources, self.tool_spec)
        self.assertEqual(result["schema"], TARGET.RESULT_SCHEMA)
        self.assertEqual(set(result["targets"]), set(TARGET.VARIANTS))
        self.assertIs(result["accepted"], False)
        self.assertIs(result["proof_credit"], False)
        for variant in TARGET.VARIANTS:
            target = self.map["targets"][variant]
            log = _log(target) + "Elapsed time: 1.2s\n"
            match = _match(variant, log)
            self.assertTrue(match["matches_first_and_only_error"])
            self.assertIs(match["accepted"], False)
            self.assertEqual(match["variant"], variant)
            self.assertNotEqual(match["log_sha256"], target["log_sha256"])
            self.assertEqual(match["current_build_id"], CURRENT_BUILD_ID)

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
        with_char_literals = original.replace(
            b"    let true_payload",
            b"    let brace = '{'; let escaped = '\\u{7d}';\n"
            b"    let true_payload", 1)
        self.assertEqual(TARGET._source_anchor(variant, with_char_literals)[1],
                         line + 1)
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
        result = _match("callee-owner-duplicate", good)
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
                    _match("callee-owner-duplicate", log)
        with self.assertRaises(TARGET.TargetError):
            _match("callee-owner-loss", good)

    def test_current_observation_is_distinct_from_prior_provenance(self):
        variant = "no-retained-half"
        target = self.map["targets"][variant]
        log = _log(target)
        observation = _log_observation(
            variant, self.sources[variant], target, log, tool_spec=self.tool_spec)
        matched = _match(variant, log, observation=observation)
        self.assertTrue(matched["matches_first_and_only_error"])
        self.assertNotEqual(observation["build_id"], target["provenance"]["build_id"])
        original_prior = dict(target["provenance"])
        mutations = (
            lambda o: o.update(variant="omit-selected-own"),
            lambda o: o.update(build_id="not-a-uuid"),
            lambda o: o.update(tool_spec_sha256="0" * 64),
            lambda o: o.update(log_sha256="0" * 64),
            lambda o: o.update(log_path="other.log"),
            lambda o: o["source_hashes"].update(**{"verified/lib.rs": "0" * 64}),
            lambda o: o["stage"].update(exit=0),
            lambda o: o["stage"].update(pointer_drop_gate_active=False),
            lambda o: o["stage"].update(argv=["wrong"]),
        )
        for mutate in mutations:
            bad = {**observation, "source_hashes": dict(observation["source_hashes"]),
                   "stage": dict(observation["stage"])}
            mutate(bad)
            with self.subTest(mutate=mutate), self.assertRaises(TARGET.TargetError):
                _match(variant, log, observation=bad)
        self.assertEqual(target["provenance"], original_prior)

    def test_prior_log_hash_is_not_current_log_hash(self):
        variant = "callee-false-normal"
        target = self.map["targets"][variant]
        current = _log(target) + "Elapsed: 17.4s\n"
        match = _match(variant, current)
        self.assertTrue(match["matches_first_and_only_error"])
        self.assertEqual(match["log_sha256"],
                         hashlib.sha256(current.encode()).hexdigest())
        self.assertNotEqual(match["log_sha256"], target["log_sha256"])

    def test_wrong_native_build_extra_errors_and_invalid_utf8_refuse(self):
        variant = "callee-owner-loss"
        target = self.map["targets"][variant]
        log = _log(target)
        observation = _log_observation(
            variant, self.sources[variant], target, log, tool_spec=self.tool_spec)
        with self.assertRaises(TARGET.TargetError):
            TARGET.match_first_and_only_error(
                variant, self.map, self.sources, self.tool_spec, log,
                log_bytes=log.encode(), log_observation=observation,
                expected_build_id="bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                tool_home=TOOL_HOME)
        with self.assertRaises(TARGET.TargetError):
            TARGET.match_first_and_only_error(
                variant, self.map, self.sources, self.tool_spec, log +
                "verified/lib.rs(1,1-2): error: extra\n",
                log_bytes=(log + "verified/lib.rs(1,1-2): error: extra\n").encode(),
                log_observation=_log_observation(
                    variant, self.sources[variant], target,
                    log + "verified/lib.rs(1,1-2): error: extra\n",
                    tool_spec=self.tool_spec),
                expected_build_id=CURRENT_BUILD_ID, tool_home=TOOL_HOME)
        with self.assertRaises(TARGET.TargetError):
            TARGET.match_first_and_only_error(
                variant, self.map, self.sources, self.tool_spec, "�\n" + log,
                log_bytes=b"\xff\n" + log.encode(),
                log_observation=observation,
                expected_build_id=CURRENT_BUILD_ID, tool_home=TOOL_HOME)


if __name__ == "__main__":
    unittest.main()
