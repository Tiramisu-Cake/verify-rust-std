"""Synthetic scope/ordering tests, no compiler/source extraction or verifier."""
import copy
import importlib.util
from pathlib import Path
import unittest
spec = importlib.util.spec_from_file_location('r11_boundary_runner', Path(__file__).with_name('a1-runner.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

G = 'if len <= T::small_sort_threshold() {'
A = '//@ assert len <= 31;'

class Boundary(unittest.TestCase):
    def binding(self, start=2, end=5):
        return {'caller': 'a1_guard_observer', 'mir_body_span': {
            'lo': {'source_path': 'verified/lib.rs', 'line': start},
            'hi': {'source_path': 'verified/lib.rs', 'line': end}}}

    def test_second_original_caller_guard_does_not_ambiguate_selected_observer(self):
        lines = ['', 'fn a1_guard_observer() {', G, A, '}', 'fn quicksort() {', G, '}']
        self.assertEqual(runner._false31_source_boundary(lines, self.binding()), (3, 4, (2, 5)))
        self.assertEqual(runner._false31_source_boundary([A, *lines[1:]], self.binding()), (3, 4, (2, 5)))

    def test_duplicate_reversed_missing_and_outside_assertions_fail(self):
        for lines in (['', G, G, A, ''], ['', A, G, '', ''], ['', G, '', '', A],
                      ['', G, A, A, ''], ['', '', '', '', '']):
            with self.subTest(lines=lines), self.assertRaises(RuntimeError):
                runner._false31_source_boundary(lines, self.binding(2, 4))

    def test_unbound_wrong_caller_path_type_and_ranges_fail(self):
        lines = ['', '', G, A, '']
        cases = [None, {}, {'caller': 'quicksort'}, {'caller': 'a1_guard_observer', 'mir_body_span': None}]
        for endpoint, key, value in [('lo', 'source_path', 'original/lib.rs'),
                                     ('hi', 'source_path', 'other.rs'),
                                     ('lo', 'line', True), ('hi', 'line', '5'),
                                     ('lo', 'line', 0), ('hi', 'line', 99), ('hi', 'line', 1)]:
            binding = copy.deepcopy(self.binding())
            binding['mir_body_span'][endpoint][key] = value
            cases.append(binding)
        for binding in cases:
            with self.subTest(binding=binding), self.assertRaises(RuntimeError):
                runner._false31_source_boundary(lines, binding)

if __name__ == '__main__':
    unittest.main()
