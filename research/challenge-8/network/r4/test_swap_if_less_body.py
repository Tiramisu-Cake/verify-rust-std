#!/usr/bin/env python3
"""Static service checks for the R4 candidate generator; no proof tools, no Cloud."""
import importlib.util
from pathlib import Path
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r4', HERE / 'swap-if-less-body.py')
r4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r4)


def git(*args):
    return subprocess.check_output(['git', '-C', str(HERE)] + list(args))


STD = git('cat-file', '-p', '40939f922bcb6fdc7ee0d30427fa861827043827')
PAIR = git('cat-file', '-p', r4.SELECT_RECOVER_PAIR_BLOB)
CAPTURE = git('cat-file', '-p', r4.SELECT_CAPTURE_BLOB)


class R4CandidateTests(unittest.TestCase):
    def test_positive_strip_restores_exact_body(self):
        crate, meta = r4.construct(STD, PAIR)
        body = r4.extract(STD)
        self.assertTrue(r4.strip_ghost(crate).endswith(body))
        self.assertEqual(meta['std_body_sha256'], r4.sha(body))
        self.assertIn(b'unsafe fn swap_if_less<T, F>', body)
        self.assertEqual(crate.count(b'__vf_callback_unwind_pair();'), 1)
        self.assertEqual(crate.count(b'lem recover_pair<T>'), 1)
        self.assertFalse(meta['proof_credit'])

    def test_ghost_regexes_equal_select_capture(self):
        for name in (b'GHOST_BLOCK = re.compile(rb"/\\*@.*?@\\*/(?:\\r?\\n)?", re.S)',
                     b'GHOST_LINE = re.compile(rb"(?m)^[ \\t]*//@[^\\r\\n]*(?:\\r?\\n|$)")'):
            self.assertIn(name, CAPTURE)

    def test_marker_immediately_before_call(self):
        lines = r4.construct(STD, PAIR)[0].split(b'\n')
        call = [i for i, l in enumerate(lines) if l.startswith(b'        let should_swap = is_less/*@')]
        self.assertEqual(len(call), 1)
        self.assertEqual(lines[call[0] - 1].strip(), b'} @*/')
        self.assertIn(b'__vf_callback_unwind_pair', lines[call[0] - 4])

    def test_negative_wrong_source(self):
        with self.assertRaisesRegex(SystemExit, 'SHA256 differs'):
            r4.construct(STD.replace(b'should_swap', b'should_swop', 1), PAIR)

    def test_negative_wrong_layer_blob(self):
        with self.assertRaisesRegex(SystemExit, 'layer blob differs'):
            r4.construct(STD, PAIR + b'\n')

    def test_negative_moved_anchor(self):
        old = r4.CALL
        try:
            r4.CALL = b'        let should_swap = is_less(&*v_a, &*v_b);\n'
            with self.assertRaisesRegex(SystemExit, 'comparator call anchor'):
                r4.construct(STD, PAIR)
        finally:
            r4.CALL = old

    def test_select_spec_is_bound_into_meta(self):
        crate, meta = r4.construct(STD, PAIR, b'/*@ // spec placeholder @*/\n')
        self.assertEqual(meta['select_pointer_spec_sha256'], r4.sha(b'/*@ // spec placeholder @*/\n'))


if __name__ == '__main__':
    unittest.main()
