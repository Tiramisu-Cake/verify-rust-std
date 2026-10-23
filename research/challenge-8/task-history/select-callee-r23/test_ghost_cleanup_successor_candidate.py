"""Synthetic static controls for the unverified R23 ghost-edge patch.

No VeriFast, rustc, exporter, decoder, proof preparation, or Cloud service is
invoked. The fixture is the exact R23 raw CFG inventory, not typed MIR input.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
INVENTORY = json.loads((HERE / 'CFG-INVENTORY.json').read_text())
PATCH = (HERE / 'ghost-cleanup-successor-fractional.patch').read_text()
REAL_CALLS = {
    'std::ptr::mut_ptr::<impl *mut T>::drop_in_place',
    'std::mem::forget',
    'std::mem::MaybeUninit::<T>::assume_init',
}


def translated_successors(*, admitted_fractional: bool, body: str,
                          builtin_ghost: bool, normal: int | None,
                          unwind: int | None) -> list[int]:
    """Model the intended AST successor accounting only."""
    raw = ([normal] if normal is not None else []) + (
        [unwind] if unwind is not None else [])
    if admitted_fractional and body == 'select_unpredictable' and builtin_ghost:
        return [normal] if normal is not None else []
    return raw


class GhostCleanupSuccessorCandidateTests(unittest.TestCase):
    def test_patch_is_one_scoped_translator_change(self):
        self.assertTrue(PATCH.startswith(
            '--- a/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml\n'
            '+++ b/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml\n'))
        self.assertEqual(PATCH.count('@@ '), 1)
        self.assertEqual(PATCH.count(
            '!Sort4SelectIntrinsic.actual_fractional_variant <> None'), 2)
        self.assertIn('State.body_name = "select_unpredictable"', PATCH)
        self.assertIn('else targets', PATCH)
        self.assertIn('([ ghost_stmt ], successors)', PATCH)
        self.assertIn('([Ast.NoopStmt call_loc], successors)', PATCH)
        self.assertNotIn('reportDeadCode', PATCH)
        self.assertNotIn('vfconsole', PATCH)

    def test_raw_fractional_inventory_stays_seven_ghost_plus_three_real(self):
        edges = INVENTORY['cleanup_predecessors']
        self.assertEqual(len(edges), 10)
        self.assertTrue(all(edge['unwind_cleanup'] == 28 for edge in edges))
        ghost = [edge for edge in edges if edge['callee'] == 'VeriFast_ghost_command']
        real = [edge for edge in edges if edge['callee'] != 'VeriFast_ghost_command']
        self.assertEqual(len(ghost), 7)
        self.assertEqual(len(real), 3)
        self.assertEqual({edge['callee'] for edge in real}, REAL_CALLS)

    def test_only_fractional_builtin_ghost_lowers_to_its_normal_successor(self):
        ghost = [edge for edge in INVENTORY['cleanup_predecessors']
                 if edge['callee'] == 'VeriFast_ghost_command']
        for edge in ghost:
            with self.subTest(block=edge['block']):
                self.assertEqual(translated_successors(
                    admitted_fractional=True, body='select_unpredictable',
                    builtin_ghost=True, normal=edge['normal_target'],
                    unwind=edge['unwind_cleanup']), [edge['normal_target']])
                self.assertEqual(translated_successors(
                    admitted_fractional=False, body='select_unpredictable',
                    builtin_ghost=True, normal=edge['normal_target'],
                    unwind=edge['unwind_cleanup']),
                    [edge['normal_target'], edge['unwind_cleanup']])
                self.assertEqual(translated_successors(
                    admitted_fractional=True, body='other_body',
                    builtin_ghost=True, normal=edge['normal_target'],
                    unwind=edge['unwind_cleanup']),
                    [edge['normal_target'], edge['unwind_cleanup']])

    def test_all_real_call_unwind_edges_and_normal_successors_survive(self):
        real = [edge for edge in INVENTORY['cleanup_predecessors']
                if edge['callee'] in REAL_CALLS]
        for edge in real:
            with self.subTest(block=edge['block'], callee=edge['callee']):
                self.assertEqual(translated_successors(
                    admitted_fractional=True, body='select_unpredictable',
                    builtin_ghost=False, normal=edge['normal_target'],
                    unwind=edge['unwind_cleanup']),
                    [edge['normal_target'], edge['unwind_cleanup']])

    def test_ghost_without_unwind_keeps_its_normal_successor(self):
        self.assertEqual(translated_successors(
            admitted_fractional=True, body='select_unpredictable',
            builtin_ghost=True, normal=15, unwind=None), [15])
        self.assertEqual(translated_successors(
            admitted_fractional=True, body='select_unpredictable',
            builtin_ghost=True, normal=None, unwind=None), [])


if __name__ == '__main__':
    unittest.main()
