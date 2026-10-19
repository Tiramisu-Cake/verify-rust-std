"""Isolated minimal string regressions; no compiler or proof pipeline imports."""
import importlib.util
from pathlib import Path
import sys
import unittest

_path = Path(__file__).with_name('a1-synthetic-inputs.py')
_spec = importlib.util.spec_from_file_location('a1_string_regression_parser', _path)
parser = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = parser
_spec.loader.exec_module(parser)


def value(literal):
    return parser.parse_records('(name=' + literal + ')')[0].fields[0][1].value


class StringRegression(unittest.TestCase):
    def test_observed_region_identifier(self):
        # D1 exact literal bytes 9362..9370: 225c275f5f353322.
        self.assertEqual(value(r'''"\'__53"'''), "'__53")
        self.assertEqual(value(r'''"'__53"'''), "'__53")

    def test_backslash_pair_is_not_an_apostrophe_escape(self):
        self.assertEqual(value(r'''"\\'__53"'''), "\\'__53")
        self.assertEqual(value(r'''"\\\'__53"'''), "\\'__53")
        self.assertNotEqual(value(r'''"\\'__53"'''), value(r'''"\'__53"'''))

    def test_json_and_unicode_values(self):
        self.assertEqual(value(r'''"a\"b\\c\/d"'''), 'a"b\\c/d')
        self.assertEqual(value(r'''"\u00e9\ud83d\ude42"'''), 'é🙂')
        self.assertEqual(value('"é🙂"'), 'é🙂')
        self.assertNotEqual(value('"é"'), value('"é"'))

    def test_unknown_malformed_and_unsupported_escapes(self):
        for raw in [r'''"\x41"''', r'''"\000"''', r'''"\a"''', r'''"\v"''',
                    r'''"\q"''', r'''"\u12"''', r'''"\uGGGG"''',
                    '"unclosed', '"trailing\\', '"raw\nnewline"']:
            with self.subTest(raw=raw), self.assertRaises(parser.ParseError):
                value(raw)

    def test_error_coordinate_after_c_apostrophe(self):
        raw = r'''"\'__53\q"'''
        with self.assertRaises(parser.ParseError) as caught:
            value(raw)
        self.assertEqual(caught.exception.__cause__.source_unicode_position,
                         raw.index('\\q'))


if __name__ == '__main__':
    unittest.main()
