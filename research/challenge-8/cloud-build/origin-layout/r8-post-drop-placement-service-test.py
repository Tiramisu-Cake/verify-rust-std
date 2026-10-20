#!/usr/bin/env python3
"""Synthetic placement regression only; no actual preparation or proof."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r8_placement', HERE / 'first-callback.py')
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)
WRAPPER = b'pub unsafe fn b2_three_from_local<F: FnMut(&u64, &u64) -> bool>(is_less: &mut F)'
CLOSE = b'        }\n    }\n}\n\n'
OLD = SimpleNamespace(WRAPPER_SIGNATURE=WRAPPER)


class PlacementTests(unittest.TestCase):
    def test_unrelated_identical_helper_braces_are_preserved(self):
        prefix = b'helper\n' + CLOSE + b'insert_tail fixture\n'
        fixture = prefix + CLOSE + WRAPPER + b'/*@ contract @*/\n{}\n'
        result = campaign._prepare_post_drop_recovery(fixture, OLD)
        self.assertTrue(result.startswith(prefix))
        self.assertEqual(result.count(campaign.GUARD_POST_DROP_RECOVERY), 1)
        self.assertTrue(result.endswith(campaign.GUARD_POST_DROP_RECOVERY +
                        b'}\n\n' + WRAPPER + b'/*@ contract @*/\n{}\n'))

    def test_missing_and_ambiguous_boundaries_fail_closed(self):
        for fixture in (CLOSE + b'wrong_wrapper', (CLOSE + WRAPPER) * 2):
            with self.subTest(fixture=fixture), self.assertRaises(ValueError):
                campaign._prepare_post_drop_recovery(fixture, OLD)


if __name__ == '__main__':
    unittest.main(verbosity=2)
