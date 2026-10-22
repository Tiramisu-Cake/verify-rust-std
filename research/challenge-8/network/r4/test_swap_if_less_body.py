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
        namespace = {}
        exec(b'import re\n' + b'\n'.join(l for l in CAPTURE.split(b'\n')
                                         if l.startswith((b'GHOST_BLOCK = ', b'GHOST_LINE = '))), namespace)
        self.assertEqual((namespace['GHOST_BLOCK'].pattern, namespace['GHOST_BLOCK'].flags),
                         (r4.GHOST_BLOCK.pattern, r4.GHOST_BLOCK.flags))
        self.assertEqual((namespace['GHOST_LINE'].pattern, namespace['GHOST_LINE'].flags),
                         (r4.GHOST_LINE.pattern, r4.GHOST_LINE.flags))

    def test_layer_excludes_fixtures_and_negative_case(self):
        crate = r4.construct(STD, PAIR)[0]
        for absent in (b'CASE_BEGIN', b'recover_pair_missing_reserved_half', b'r15_recover_pair_type_anchor',
                       b'join_four_owned_cells'):
            self.assertNotIn(absent, crate)
        self.assertEqual(crate.count(b'pred comparison_debt<T>('), 1)

    def test_marker_immediately_before_call(self):
        lines = r4.construct(STD, PAIR)[0].split(b'\n')
        call = [i for i, l in enumerate(lines) if l.startswith(b'        let should_swap = is_less/*@')]
        self.assertEqual(len(call), 1)
        self.assertEqual(lines[call[0] - 1].strip(), b'} @*/')
        self.assertIn(b'__vf_callback_unwind_pair', lines[call[0] - 4])

    def test_control_matrix(self):
        variants, _ = r4.matrix(STD, PAIR)
        self.assertEqual(set(variants), set(r4.EXPECTED))
        body = r4.extract(STD)
        positive = variants['positive']
        self.assertEqual(positive.count(b'unsafe { swap_if_less(v_base, 0, 1, is_less) };'), 1)
        self.assertIn(b'unsafe { swap_if_less(v_base, 0, 0, is_less) };', variants['equal-pos'])
        self.assertIn(b'*mut ()', variants['caller-zst'])
        for name in r4.NEGATIVES:
            v = variants[name]
            self.assertNotEqual(v, positive)
            if name in r4.CALLERLESS:
                self.assertEqual(r4.strip_ghost(v), r4.strip_ghost(r4.construct(STD, PAIR)[0]), name)
            else:
                self.assertEqual(r4.strip_ghost(v), r4.strip_ghost(positive), name)  # ghost-only mutation
                self.assertTrue(v.endswith(r4.GENERIC_CALLER), name)
        for name in r4.REACH:
            v = variants[name]
            self.assertEqual(v.count(r4.ASSERT_FALSE), 1, name)
            self.assertEqual(r4.strip_ghost(v), r4.strip_ghost(
                variants['caller-zst' if name.endswith('zst') else 'positive']), name)
        for name, v in variants.items():
            self.assertIn(body, r4.strip_ghost(v), name)

    def test_cli_refuses_existing_output(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            std = Path(d) / 'smallsort.rs'; std.write_bytes(STD)
            pair = Path(d) / 'pair.rs'; pair.write_bytes(PAIR)
            run = lambda out: subprocess.run(['python3', '-B', str(HERE / 'swap-if-less-body.py'), str(std), str(pair), str(out)],
                                             capture_output=True, text=True)
            first = run(Path(d) / 'out')
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(len(list((Path(d) / 'out').glob('*.rs'))), len(r4.EXPECTED))
            again = run(Path(d) / 'out')
            self.assertNotEqual(again.returncode, 0)
            self.assertIn('must not exist', again.stdout + again.stderr)

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

    def test_negative_select_spec_refused_until_p2(self):
        for spec in (b'/*@ lem foo() req true; ens false; { assume(false); } @*/\nfn select_unpredictable(){}',
                     b'/*@ // placeholder @*/\n', b''):
            with self.assertRaisesRegex(SystemExit, 'P2'):
                r4.construct(STD, PAIR, spec)
        self.assertEqual(r4.construct(STD, PAIR)[1]['select_pointer_layer'], 'ABSENT (P2)')


if __name__ == '__main__':
    unittest.main()
