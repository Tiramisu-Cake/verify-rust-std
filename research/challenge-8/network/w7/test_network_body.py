#!/usr/bin/env python3
"""Static service checks for the W7 generator; no proof tools, no Cloud."""
import importlib.util
import re
from pathlib import Path
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w7', HERE / 'network-body.py')
w7 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w7)
git = lambda *a: subprocess.check_output(['git', '-C', str(HERE)] + list(a))
STD = git('cat-file', '-p', '40939f922bcb6fdc7ee0d30427fa861827043827')
PAIR = git('cat-file', '-p', w7.r4.SELECT_RECOVER_PAIR_BLOB)
SOURCE_MAP = (HERE.parent.parent / 'networks' / 'SOURCE-MAP.md').read_text()


class W7Tests(unittest.TestCase):
    def test_strip_and_pairs_match_source_map(self):
        for n, (name, _, calls) in w7.NETWORKS.items():
            crate, meta = w7.construct(STD, PAIR, n)
            body = w7.extract(STD, n)
            self.assertTrue(w7.strip_ghost(crate).endswith(body))
            pairs = re.findall(rb'swap_if_less\(v_base, (\d+), (\d+), is_less\);', body)
            rows = re.findall(r'^\| ' + str(n) + r' \| \d+–\d+ \| (.*) \|$', SOURCE_MAP, re.M)
            expected = [tuple(p) for r in rows for p in re.findall(r'\((\d+),(\d+)\)', r)]
            self.assertEqual([(a.decode(), b.decode()) for a, b in pairs], expected)
            self.assertEqual(len(pairs), calls)
            self.assertEqual(crate.count(b'unsafe fn swap_if_less<T, F>'), 1)
            self.assertIn(('lem split_owned_cells%d<T>' % n).encode(), crate)
            self.assertIn(('lem join_owned_cells%d<T>' % n).encode(), crate)
            self.assertFalse(meta['proof_credit'])
            for forbidden in (b'assume', b'CASE_BEGIN'):
                self.assertNotIn(forbidden, crate)

    def test_ghost_only_between_split_and_join(self):
        crate = w7.construct(STD, PAIR, 9)[0]
        tail = crate[crate.index(b'fn sort9_optimal'):]
        self.assertLess(tail.index(b'split_owned_cells9'), tail.index(b'swap_if_less(v_base, 0, 3'))
        self.assertGreater(tail.index(b'join_owned_cells9'), tail.rindex(b'swap_if_less(v_base, '))

    def test_lemmas_have_no_trusted_bodies(self):
        crate = w7.construct(STD, PAIR, 13)[0]
        for name in (b'split_owned_cells13', b'join_owned_cells13'):
            block = crate[crate.index(b'lem ' + name):]
            block = block[:block.index(b'@*/')]
            self.assertIn(b'{\n', block)
            self.assertNotIn(b'assume', block)

    def test_negative_wrong_source(self):
        with self.assertRaisesRegex(SystemExit, 'SHA256 differs'):
            w7.construct(STD.replace(b'sort9_optimal(region', b'sort9_optimal(regoin', 1), PAIR, 9)


if __name__ == '__main__':
    unittest.main()
