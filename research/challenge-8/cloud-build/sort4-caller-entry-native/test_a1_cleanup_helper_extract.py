"""Synthetic parity checks for the inactive extracted helper; no proof tools."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load isolated module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ORIGINAL = load("a1_cleanup_extract_original", HERE / "a1-runner.py")
EXTRACTED = load("a1_cleanup_extract_candidate", HERE / "a1-cleanup-helper.py")
AST_GATES = load("a1_cleanup_extract_ast_gates", HERE / "a1-ast-gates.py")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def fixture_source() -> bytes:
    return (b"// fixture prefix\n"
            b"//@ use std::option::{Option, Option::None, Option::Some};\n"
            b"/*@\n"
            b"lem a1_cleanup_option_ref<'a, T>(value: std::option::Option<&'a T>)\n"
            b"    req thread_token(?t) &*& std::option::Option_own::<&'a T>(t, value);\n"
            b"    ens thread_token(t);\n"
            b"{\n"
            b"    open std::option::Option_own::<&'a T>(t, value);\n"
            b"    match value {\n"
            b"        Option::None => {}\n"
            b"        Option::Some(r) => {}\n"
            b"    }\n"
            b"}\n"
            b"@*/\n"
            b"fn caller() {}\n")


def metadata(source: bytes) -> dict:
    lines = source.splitlines(keepends=True)
    start, end, body_start, body_end = 3, 14, 4, 13
    block = b"".join(lines[start - 1:end])
    digest = sha(block)
    return {"name": "a1_cleanup_option_ref", "kind": "lemma",
            "source_start_line": start, "source_end_line": end,
            "source_sha256": digest, "source_bytes_sha256": digest,
            "body_start_line": body_start, "body_end_line": body_end}


def ast_text(*, duplicate=False, ambiguous=False, external=False,
             kind="manual_lemma", header_location=None, close_location=None) -> str:
    kind_node = {
        "manual_lemma": "Lemma (false, None)",
        "auto_lemma": "Lemma (true, None)",
        "triggered_lemma": 'Lemma (false, Some ("trigger"))',
        "regular": "Regular",
    }[kind]
    header = header_location or 'loc "verified/lib.rs(4,5-26)"'
    close = close_location or 'loc "verified/lib.rs(13,1)"'
    def func() -> str:
        return (f'Func ({header}, {kind_node}, [], None, '
                '"a1_cleanup_option_ref", [], false, (None, None), None, false, '
                f'Some (([], {close})), false, [])')
    declarations = [func()]
    if duplicate:
        declarations.append(func())
    if ambiguous:
        declarations.append(
            'Func (loc "verified/lib.rs(2,5-10)", Regular, [], None, '
            '"other_body", [], false, (None, None), None, false, '
            'Some (([], loc "verified/lib.rs(4,1)")), false, [])')
    if external:
        declarations.append(
            'Func (loc "external/lib.rs(2,5-10)", Regular, [], None, '
            '"external_body", [], false, (None, None), None, false, '
            'Some (([], loc "external/lib.rs(4,1)")), false, [])')
    return ('[PackageDecl (loc "verified/lib.rs(1,1)", "", [], [' +
            '; '.join(declarations) + '])]')


def outcome(module, ast: str, source: bytes, meta: object):
    try:
        return ("return", module.select_checked_cleanup_helper_lemma(
            ast, AST_GATES, source, meta))
    except Exception as exc:
        return ("raise", type(exc).__name__, str(exc))


class ExtractedHelperTests(unittest.TestCase):
    def assert_parity(self, ast: str, source: bytes, meta: object):
        self.assertEqual(outcome(EXTRACTED, ast, source, meta),
                         outcome(ORIGINAL, ast, source, meta))

    @staticmethod
    def source_definition(path: Path, name: str) -> str:
        text = path.read_text()
        tree = ast.parse(text)
        node = next(item for item in tree.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and item.name == name)
        return "".join(text.splitlines(keepends=True)[node.lineno - 1:node.end_lineno])

    def test_extracted_definitions_are_verbatim(self):
        for name in ("_need", "_ast_source_span", "_ast_source_coordinates",
                     "select_checked_cleanup_helper_lemma"):
            with self.subTest(function=name):
                self.assertEqual(self.source_definition(HERE / "a1-cleanup-helper.py", name),
                                 self.source_definition(HERE / "a1-runner.py", name))

    def test_acceptance_and_external_definition(self):
        source = fixture_source()
        meta = metadata(source)
        for ast in (ast_text(), ast_text(external=True)):
            with self.subTest(external="external_body" in ast):
                self.assert_parity(ast, source, meta)
                result = EXTRACTED.select_checked_cleanup_helper_lemma(
                    ast, AST_GATES, source, meta)
                self.assertEqual(result["classification"],
                                 "ONE_SOURCE_INTERVAL_SELECTED_CHECKED_LEMMA")
                self.assertEqual(result["body_count_from_intervals"], 1)
                self.assertFalse(result["proof_credit"])

    def test_metadata_type_identity_bounds_and_block_hash_refusals(self):
        source = fixture_source()
        good = metadata(source)
        variants = [
            ("name", good | {"name": "other"}),
            ("kind", good | {"kind": "function"}),
            ("missing-bound", {key: value for key, value in good.items()
                                if key != "body_end_line"}),
            ("bool-bound", good | {"body_start_line": True}),
            ("reversed", good | {"source_start_line": 14}),
            ("out-of-file", good | {"source_end_line": 99}),
            ("source-hash", good | {"source_sha256": "0" * 64}),
            ("metadata-hash", good | {"source_bytes_sha256": "1" * 64}),
            ("wrong-source", source.replace(b"ens thread_token(t);",
                                             b"ens thread_token(?t);", 1), good),
        ]
        for item in variants:
            label, *rest = item
            candidate_source, meta = ((rest[0], rest[1]) if len(rest) == 2
                                      else (source, rest[0]))
            with self.subTest(refusal=label):
                self.assert_parity(ast_text(), candidate_source, meta)
                self.assertEqual(outcome(EXTRACTED, ast_text(), candidate_source, meta)[0],
                                 "raise")

    def test_source_delimiter_and_declaration_ambiguity_refusals(self):
        source = fixture_source()
        meta = metadata(source)
        bad_delimiter = source.replace(b"/*@\n", b"/* \n", 1)
        duplicate_declaration = source + (
            b"/*@\nlem a1_cleanup_option_ref<'a, T>()\n@*/\n")
        for label, candidate_source, ast in (
                ("bad-delimiter", bad_delimiter, ast_text()),
                ("duplicate-source-name", duplicate_declaration, ast_text()),
                ("duplicate-ast-name", source, ast_text(duplicate=True)),
                ("overlapping-ast-interval", source, ast_text(ambiguous=True))):
            with self.subTest(refusal=label):
                self.assert_parity(ast, candidate_source, meta)
                self.assertEqual(outcome(EXTRACTED, ast, candidate_source, meta)[0],
                                 "raise")

    def test_manual_lemma_and_trigger_controls(self):
        source = fixture_source()
        meta = metadata(source)
        for kind in ("auto_lemma", "triggered_lemma", "regular"):
            with self.subTest(kind=kind):
                ast = ast_text(kind=kind)
                self.assert_parity(ast, source, meta)
                self.assertEqual(outcome(EXTRACTED, ast, source, meta)[0], "raise")

    def test_bad_header_close_coordinates_and_ast_interval_refusals(self):
        source = fixture_source()
        meta = metadata(source)
        bad_cases = (
            ast_text(header_location='loc "verified/lib.rs(4,6-26)"'),
            ast_text(close_location='loc "verified/lib.rs(13,2)"'),
            ast_text(header_location='loc "verified/lib.rs(4,26-5,5)"'),
            ast_text(close_location='loc "verified/lib.rs(12,1)"'),
        )
        for index, ast in enumerate(bad_cases):
            with self.subTest(case=index):
                self.assert_parity(ast, source, meta)
                self.assertEqual(outcome(EXTRACTED, ast, source, meta)[0], "raise")


if __name__ == "__main__":
    unittest.main()
