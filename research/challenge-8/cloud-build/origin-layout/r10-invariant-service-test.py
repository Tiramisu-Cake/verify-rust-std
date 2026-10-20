#!/usr/bin/env python3
"""Pure synthetic annotation assembly; never prepares actual source/toolchain."""
import ast
import importlib.util
from pathlib import Path
import re
import unittest
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r10_annotation_assembly', HERE/'first-callback.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
SYNTHETIC = b"""fn synthetic() {
        loop {
            /*@ let_lft 'late = r5_late_k; @*/
            synthetic_copy();
        }
    }
    /*@ {
        guard_current_return_recover();
    } @*/
}
"""
def runtime(data):
    clean = re.sub(rb'/\*.*?\*/|//[^\n]*', b'', data, flags=re.S)
    return b''.join(clean.split())
class Tests(unittest.TestCase):
    def test_checked_head_position_and_runtime_identity(self):
        result = m._prepare_r10_moving_gap(SYNTHETIC)
        self.assertEqual(runtime(result), runtime(SYNTHETIC))
        self.assertIn(b"loop {\n            /*@ let_lft 'late = r5_late_k; @*/\n" +
                      m.R10_MOVING_GAP_INVARIANT, result)
        self.assertEqual(result.count(m.R10_MOVING_GAP_INVARIANT), 1)
        self.assertEqual(result.count(m.R10_BREAK_PREP), 1)
        self.assertNotIn(b'note(sift == begin + 1)', m.R10_ITERATION_PREP)
        self.assertNotIn(b'array::<u64>(begin, 3,', m.R10_MOVING_GAP_INVARIANT)
        self.assertNotIn(b'begin_lifetime', m.R10_MOVING_GAP_INVARIANT)
        self.assertIn(b'if sift == begin + 1 {', m.R10_MOVING_GAP_INVARIANT)
        self.assertIn(b'} else {', m.R10_MOVING_GAP_INVARIANT)
        self.assertNotIn(b' + 1 ?', m.R10_MOVING_GAP_INVARIANT)
        self.assertLess(result.index(b"let_lft 'late"), result.index(m.R10_MOVING_GAP_INVARIANT))
        self.assertLess(result.index(m.R10_MOVING_GAP_INVARIANT), result.index(m.R10_ITERATION_PREP))
        self.assertNotIn(b'assume', result)
        self.assertNotIn(b'leak', result)
    def test_missing_ambiguous_reentry_and_wrong_exit_fail_closed(self):
        for bad in (b'', SYNTHETIC+SYNTHETIC, m._prepare_r10_moving_gap(SYNTHETIC),
                    SYNTHETIC.replace(b'guard_current_return_recover();', b'other();')):
            with self.subTest(source=bad[:24]):
                with self.assertRaises(ValueError):
                    m._prepare_r10_moving_gap(bad)
    def test_all_edited_python_syntax(self):
        ast.parse((HERE/'first-callback.py').read_bytes())
if __name__ == '__main__':
    unittest.main()
