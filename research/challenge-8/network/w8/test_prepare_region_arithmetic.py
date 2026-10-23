"""Synthetic-byte tests only; never reads repository proof or Rust inputs."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).with_name("prepare-region-arithmetic.py")
SPEC = importlib.util.spec_from_file_location("prepare_region_arithmetic", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


SOURCE = b"synthetic pinned source bytes\n"
HEADER = b"fixpoint int synthetic_definition(int x) { return x; }\n"
POSITIVE = b'''/*@
lemma void w8_prefix_in_bounds(int n) requires true; ensures true; { }
lemma void w8_split_and_prefix_facts(int n) requires true; ensures true; { }
lemma void w8_prefix_choice_facts() requires true; ensures true; { }
@*/
'''
FRAGMENTS = {
    "len25-both-prefixes-9": b'''/*@
lemma void negative_a() requires true; ensures true; {
    // TARGET_ASSERTION
    assert false;
}
@*/
''',
    "region8-prefix-9": b'''/*@
lemma void negative_b() requires true; ensures true; {
    // TARGET_ASSERTION
    assert false;
}
@*/
''',
    "len33-fits32": b'''/*@
lemma void negative_c() requires true; ensures true; {
    // TARGET_ASSERTION
    assert false;
}
@*/
''',
}


def synthetic_fixture(root: Path | None = None):
    inputs = {"header": HEADER, "positive": POSITIVE, **FRAGMENTS}
    paths = {
        "header": "synthetic/header.gh",
        "positive": "synthetic/positive.c",
        "len25-both-prefixes-9": "synthetic/a.inc",
        "region8-prefix-9": "synthetic/b.inc",
        "len33-fits32": "synthetic/c.inc",
    }
    manifest = {
        "schema": prepare.INPUT_SCHEMA,
        "state": "UNVERIFIED_STATIC_PREPARATION",
        "proof_credit": False,
        "parser_input_binding": "NOT_ESTABLISHED",
        "source": {
            "commit": prepare.SOURCE_COMMIT,
            "blob": prepare.SOURCE_BLOB,
            "path": prepare.SOURCE_PATH,
            "sha256": digest(SOURCE),
        },
        "inputs": {
            name: {"path": paths[name], "sha256": digest(data)}
            for name, data in inputs.items()
        },
        "positive_body_inventory": list(prepare.EXPECTED_POSITIVE_BODIES),
        "negative_controls": [
            {"id": name, "target_marker": "TARGET_ASSERTION",
             "expected_diagnostic_predicate": None}
            for name in prepare.REQUIRED_NEGATIVE_IDS
        ],
    }
    if root is not None:
        (root / "library/core/src/slice/sort/shared").mkdir(parents=True)
        (root / prepare.SOURCE_PATH).write_bytes(SOURCE)
        for name, data in inputs.items():
            path = root / paths[name]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    return manifest, SOURCE, inputs


def assemble_synthetic(manifest, source, inputs):
    with mock.patch.object(prepare, "SOURCE_SHA256", digest(source)):
        return prepare.assemble_units(manifest, source, inputs)


class PrepareRegionArithmeticTests(unittest.TestCase):
    def test_assemble_success_has_four_units_inventory_and_target_lines(self):
        manifest, source, inputs = synthetic_fixture()
        units, metadata = assemble_synthetic(manifest, source, inputs)
        self.assertEqual(set(units), {
            "positive.c", "region-arithmetic.gh",
            "negative-len25-both-prefixes-9.c",
            "negative-region8-prefix-9.c",
            "negative-len33-fits32.c",
        })
        self.assertEqual(metadata["positive_body_inventory"], prepare.EXPECTED_POSITIVE_BODIES)
        self.assertEqual([x["target_marker_line_in_fragment"] for x in metadata["negative_controls"]], [3, 3, 3])
        self.assertEqual([x["target_assertion_line_in_fragment"] for x in metadata["negative_controls"]], [4, 4, 4])
        expected_negative_names = ["negative_a", "negative_b", "negative_c"]
        for control in metadata["negative_controls"]:
            unit_lines = units[control["unit"]].decode().splitlines()
            self.assertRegex(unit_lines[control["target_assertion_line_in_assembled_unit"] - 1], r"\bassert\b")
            self.assertEqual(len(control["body_inventory"]), 4)
            self.assertEqual(control["body_inventory"][:3], prepare.EXPECTED_POSITIVE_BODIES)
            self.assertEqual(control["body_inventory"][3], expected_negative_names.pop(0))
        self.assertEqual(metadata["schema"], prepare.OUTPUT_SCHEMA)
        self.assertTrue(all(x["expected_diagnostic_predicate"] is None for x in metadata["negative_controls"]))
        self.assertFalse(metadata["proof_credit"])
        self.assertEqual(metadata["parser_input_binding"], "NOT_ESTABLISHED")

    def test_rejects_source_and_input_hash_mismatch(self):
        manifest, source, inputs = synthetic_fixture()
        with self.assertRaisesRegex(prepare.PreparationError, "source SHA-256 pin mismatch"):
            prepare.assemble_units(manifest, source, inputs)
        with mock.patch.object(prepare, "SOURCE_SHA256", digest(source)):
            with self.assertRaisesRegex(prepare.PreparationError, "source bytes"):
                prepare.assemble_units(manifest, source + b"changed", inputs)
        changed = dict(inputs)
        changed["header"] += b"changed"
        with self.assertRaisesRegex(prepare.PreparationError, "header SHA-256"):
            assemble_synthetic(manifest, source, changed)

    def test_rejects_wrong_source_identity_and_bad_manifest_types(self):
        manifest, source, inputs = synthetic_fixture()
        wrong = json.loads(json.dumps(manifest))
        wrong["source"]["commit"] = "0" * 40
        with self.assertRaisesRegex(prepare.PreparationError, "source commit mismatch"):
            assemble_synthetic(wrong, source, inputs)
        for key, value in (("schema", None), ("proof_credit", None),
                           ("parser_input_binding", None), ("inputs", None)):
            wrong = json.loads(json.dumps(manifest))
            wrong[key] = value
            with self.assertRaises(prepare.PreparationError):
                assemble_synthetic(wrong, source, inputs)

    def test_rejects_ambiguous_marker_and_incomplete_body_inventory(self):
        manifest, source, inputs = synthetic_fixture()
        changed = dict(inputs)
        changed["region8-prefix-9"] += b"// TARGET_ASSERTION\n"
        manifest = json.loads(json.dumps(manifest))
        manifest["inputs"]["region8-prefix-9"]["sha256"] = digest(changed["region8-prefix-9"])
        with self.assertRaisesRegex(prepare.PreparationError, "exactly one target marker"):
            assemble_synthetic(manifest, source, changed)

        manifest, source, inputs = synthetic_fixture()
        changed = dict(inputs)
        changed["region8-prefix-9"] = changed["region8-prefix-9"].replace(b"\n", b"\r\n")
        manifest["inputs"]["region8-prefix-9"]["sha256"] = digest(changed["region8-prefix-9"])
        with self.assertRaisesRegex(prepare.PreparationError, "LF line endings"):
            assemble_synthetic(manifest, source, changed)

        manifest, source, inputs = synthetic_fixture()
        manifest["positive_body_inventory"] = manifest["positive_body_inventory"][:-1]
        with self.assertRaisesRegex(prepare.PreparationError, "incomplete or out of order"):
            assemble_synthetic(manifest, source, inputs)

    def test_rejects_bodyless_extra_or_unchecked_lemma_and_header_lemma(self):
        manifest, source, inputs = synthetic_fixture()
        changed = dict(inputs)
        changed["positive"] = POSITIVE.replace(
            b"lemma void w8_split_and_prefix_facts(int n) requires true; ensures true; { }",
            b"lemma void w8_split_and_prefix_facts(int n) requires true; ensures true;",
        )
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["positive"]["sha256"] = digest(changed["positive"])
        with self.assertRaisesRegex(prepare.PreparationError, "no explicit body"):
            assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["positive"] = POSITIVE.replace(b"{ }", b"{ assume(false); }")
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["positive"]["sha256"] = digest(changed["positive"])
        with self.assertRaisesRegex(prepare.PreparationError, "assume/assume_correct/lemma_auto"):
            assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["header"] += b"/*@ assume_correct(true); @*/\n"
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["header"]["sha256"] = digest(changed["header"])
        with self.assertRaisesRegex(prepare.PreparationError, "assume/assume_correct/lemma_auto"):
            assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["header"] += b"lemma void header_lemma() requires true; ensures true; { }\n"
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["header"]["sha256"] = digest(changed["header"])
        with self.assertRaisesRegex(prepare.PreparationError, "header definitions closure"):
            assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["header"] += b"/*@ lemma void ghost_header_lemma() requires true; ensures true; { } @*/\n"
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["header"]["sha256"] = digest(changed["header"])
        with self.assertRaisesRegex(prepare.PreparationError, "header definitions closure"):
            assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["header"] += b"// assume lemma_auto in prose is ignored\n"
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["header"]["sha256"] = digest(changed["header"])
        assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["header"] += b"assume(false);\n"
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["header"]["sha256"] = digest(changed["header"])
        with self.assertRaisesRegex(prepare.PreparationError, "assume/assume_correct/lemma_auto"):
            assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["positive"] += b"/*@ lemma void unexpected() requires true; ensures true; { } @*/\n"
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["positive"]["sha256"] = digest(changed["positive"])
        with self.assertRaisesRegex(prepare.PreparationError, "body inventory mismatch"):
            assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["len25-both-prefixes-9"] = b'''/*@
lemma void negative_a() requires true; ensures true;
    // TARGET_ASSERTION
    assert false;
@*/
'''
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["len25-both-prefixes-9"]["sha256"] = digest(changed["len25-both-prefixes-9"])
        with self.assertRaisesRegex(prepare.PreparationError, "no explicit body"):
            assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["len25-both-prefixes-9"] = FRAGMENTS["len25-both-prefixes-9"].replace(
            b"assert false;", b"lemma_auto(); assert false;")
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["len25-both-prefixes-9"]["sha256"] = digest(changed["len25-both-prefixes-9"])
        with self.assertRaisesRegex(prepare.PreparationError, "assume/assume_correct/lemma_auto"):
            assemble_synthetic(wrong, source, changed)

        changed = dict(inputs)
        changed["len25-both-prefixes-9"] = FRAGMENTS["len25-both-prefixes-9"].replace(
            b"assert false;", b"assume_correct(true); assert false;")
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["len25-both-prefixes-9"]["sha256"] = digest(changed["len25-both-prefixes-9"])
        with self.assertRaisesRegex(prepare.PreparationError, "assume/assume_correct/lemma_auto"):
            assemble_synthetic(wrong, source, changed)

    def test_rejects_null_or_unchecked_negative_fragment(self):
        manifest, source, inputs = synthetic_fixture()
        wrong = json.loads(json.dumps(manifest))
        wrong["negative_controls"][0]["expected_diagnostic_predicate"] = "claimed"
        with self.assertRaisesRegex(prepare.PreparationError, "unpinned/null"):
            assemble_synthetic(wrong, source, inputs)
        wrong = json.loads(json.dumps(manifest))
        del wrong["negative_controls"][0]["expected_diagnostic_predicate"]
        with self.assertRaisesRegex(prepare.PreparationError, "unpinned/null"):
            assemble_synthetic(wrong, source, inputs)

        changed = dict(inputs)
        changed["len25-both-prefixes-9"] = b"/*@ lemma void n() requires true; ensures true; { } @*/\n"
        wrong = json.loads(json.dumps(manifest))
        wrong["inputs"]["len25-both-prefixes-9"]["sha256"] = digest(changed["len25-both-prefixes-9"])
        with self.assertRaisesRegex(prepare.PreparationError, "exactly one target marker"):
            assemble_synthetic(wrong, source, changed)

    def test_output_is_new_only_and_partial_write_is_cleaned(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            dest = root / "out"
            prepare.write_new_output_directory(dest, {"a.bin": b"a"})
            self.assertEqual((dest / "a.bin").read_bytes(), b"a")
            with self.assertRaisesRegex(prepare.PreparationError, "already exists"):
                prepare.write_new_output_directory(dest, {"a.bin": b"overwrite"})
            self.assertEqual((dest / "a.bin").read_bytes(), b"a")

            partial = root / "partial"
            with self.assertRaisesRegex(prepare.PreparationError, "artifact name"):
                prepare.write_new_output_directory(partial, {"first.bin": b"written", "bad/name": b"no"})
            self.assertFalse(partial.exists())

            original_open = open
            def fail_on_second(path, mode):
                if Path(path).name == "second.bin":
                    raise OSError("synthetic writer failure")
                return original_open(path, mode)
            failed = root / "failed"
            with mock.patch("builtins.open", side_effect=fail_on_second):
                with self.assertRaisesRegex(OSError, "synthetic writer failure"):
                    prepare.write_new_output_directory(failed, {"first.bin": b"one", "second.bin": b"two"})
            self.assertFalse(failed.exists())

    def test_cli_provider_gate_precedes_manifest_or_source_reads(self):
        with mock.patch.object(prepare, "require_supported_provider", side_effect=RuntimeError("gate")) as gate:
            with self.assertRaisesRegex(RuntimeError, "gate"):
                prepare.main(["--manifest", "/missing/manifest", "--repo-root", "/missing/repo",
                              "--output-dir", "/missing/output"])
            gate.assert_called_once_with()

    def test_cli_success_uses_only_synthetic_files_and_writes_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest, _, _ = synthetic_fixture(root)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            out = root / "prepared"
            with mock.patch.object(prepare, "SOURCE_SHA256", digest(SOURCE)), \
                 mock.patch.object(prepare, "require_supported_provider", return_value={"provider": "synthetic-mock"}):
                self.assertEqual(prepare.main(["--manifest", str(manifest_path), "--repo-root", str(root),
                                               "--output-dir", str(out)]), 0)
            metadata = json.loads((out / "prepared-metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["schema"], prepare.OUTPUT_SCHEMA)
            self.assertFalse(metadata["proof_credit"])
            self.assertEqual(metadata["provider"]["provider"], "synthetic-mock")
            self.assertTrue((out / "region-arithmetic.gh").is_file())

    def test_cli_rejects_symlink_input_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest, _, _ = synthetic_fixture(root)
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            outside = root / "outside.inc"
            outside.write_bytes(FRAGMENTS["len25-both-prefixes-9"])
            symlink = root / "synthetic/a.inc"
            symlink.unlink()
            symlink.symlink_to(outside)
            out = root / "prepared"
            with mock.patch.object(prepare, "SOURCE_SHA256", digest(SOURCE)), \
                 mock.patch.object(prepare, "require_supported_provider", return_value={"provider": "synthetic-mock"}):
                with self.assertRaisesRegex(prepare.PreparationError, "must not traverse a symlink"):
                    prepare.main(["--manifest", str(manifest_path), "--repo-root", str(root),
                                  "--output-dir", str(out)])
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
