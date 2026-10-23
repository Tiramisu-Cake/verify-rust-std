"""Static controls for the inactive R23 fractional MIR layout overlay."""
from __future__ import annotations

from pathlib import Path
import re
import unittest

HERE = Path(__file__).resolve().parent
PATCH = HERE / "verifast-r23-fractional-mir-layout-26.10.patch"
BASE_SHA256 = "2d6f1950bd95b655560c767c54af8facfecde724f29a72c4218b65b6c6438c19"
OVERLAY_SHA256 = "cadaa80ab55e6fb3f53ccfcae1ab05dc953a2cb69a17616654d49dad6350478f"
PATCH_SHA256 = "68810eb486d494cb49e158a13eab55b19464fad1b724bd9025cf5960b6c5bc17"

FRACTIONAL = {
    "body_locals": 46,
    "body_blocks": 29,
    "owner_cleanup_target": 28,
    "owner_cleanup_edges": 10,
    "forget_block": 18,
    "forget_arg": "_36",
    "forget_destination": "_35",
    "forget_normal": 19,
    "forget_cleanup": 28,
    "forget_drop_flag": "_45",
    "forget_guard_move": ("_36", "_28"),
    "pointer_drop_block": 15,
    "pointer_drop_arg": "_32",
    "pointer_drop_destination": "_31",
    "pointer_drop_normal": 16,
    "pointer_drop_cleanup": 28,
    "assume_init_block": 24,
    "assume_init_arg": "_41",
    "assume_init_destination": "_0",
    "assume_init_normal": 25,
    "assume_init_cleanup": 28,
    "cleanup_switch": ("_45", (26, 27)),
    "cleanup_resume_block": 26,
    "cleanup_drop": ("_28", 26, "Terminate"),
}

LEGACY_NINE = {
    "body_blocks": 25,
    "forget_arg": "_32",
    "forget_destination": "_31",
    "forget_normal": 15,
    "forget_cleanup": 24,
    "pointer_drop_arg": "_28",
    "assume_init_arg": "_37",
    "assume_init_normal": 21,
    "assume_init_cleanup": 24,
}


class FractionalLayoutOverlayStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patch = PATCH.read_text()

    def test_new_coordinates_are_finite_and_differ_from_legacy(self):
        for field in (
            "forget_arg", "forget_destination", "forget_normal",
            "forget_cleanup", "pointer_drop_arg", "assume_init_arg",
            "assume_init_normal", "assume_init_cleanup", "body_blocks",
        ):
            with self.subTest(field=field):
                self.assertNotEqual(FRACTIONAL[field], LEGACY_NINE.get(field))

    def test_synthetic_layout_rejects_wrong_coordinates_and_unadmitted_row(self):
        def admits(layout, owner_row_admitted):
            return owner_row_admitted and layout == FRACTIONAL

        self.assertTrue(admits(dict(FRACTIONAL), True))
        self.assertFalse(admits(dict(FRACTIONAL), False))
        self.assertFalse(admits(dict(LEGACY_NINE), True))
        for field, value in FRACTIONAL.items():
            wrong = dict(FRACTIONAL)
            wrong[field] = ("wrong-coordinate" if isinstance(value, str)
                            else (-1, -1) if isinstance(value, tuple)
                            else value + 1)
            with self.subTest(field=field):
                self.assertFalse(admits(wrong, True))

    def test_fractional_gate_and_exact_owner_row_binding_are_present(self):
        self.assertIn("actual_fractional_variant := fractional_variant", self.patch)
        self.assertIn("actual_fractional_variant := None", self.patch)
        self.assertIn("Some \"1\",Some variant,Some admitted", self.patch)
        self.assertIn("variant = admitted", self.patch)

    def test_every_fractional_coordinate_is_pinned_in_overlay(self):
        expected_fragments = (
            '46, 29 when fractional -> "_41", 25, 28',
            'if fractional then 28 else if nine then 24 else 23',
            'if fractional then 29 else 25',
            'if fractional then 18 else 14',
            'if fractional then "_34", "_35", "_36", "_45", "_36", "_28"',
            'then "_32" else if !Sort4SelectIntrinsic.actual_owner_admitted',
            'then LocalDeclIdRd.name_get (PlaceRd.local_get place) = "_41"',
            'then 19 else 15',
            'then "_35" else "_31"',
            '<> [26;27]',
            'UnwindActionRd.Terminate',
        )
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.patch)

    def test_overlay_does_not_change_pins_or_default_nine_layout(self):
        removed = [line[1:] for line in self.patch.splitlines()
                   if line.startswith("-") and not line.startswith("---")]
        added = [line[1:] for line in self.patch.splitlines()
                 if line.startswith("+") and not line.startswith("+++")]
        self.assertFalse(any("fractional_rows" in line or
                             '("positive", "' in line or
                             "cleanup_edges" in line or
                             re.search(r"[0-9a-f]{64}", line)
                             for line in removed))
        self.assertIn('42, 25 when not fractional -> "_37", 21, 24',
                      "\n".join(added))
        self.assertIn('["_37"; "_26"]', "\n".join(added))
        self.assertIn('if fractional then 28 else 24', "\n".join(added))
        self.assertIn('if fractional then 19 else 15', "\n".join(added))
        self.assertIn('then "_36" else "_32"',
                      "\n".join(added))
        self.assertIn('then "_35" else "_31"',
                      "\n".join(added))

    def test_patch_identity_is_documented(self):
        design = (HERE / "R23-FRACTIONAL-MIR-LAYOUT-CANDIDATE.md").read_text()
        self.assertIn(BASE_SHA256, design)
        self.assertIn(OVERLAY_SHA256, design)
        self.assertIn(PATCH_SHA256, design)


if __name__ == "__main__":
    unittest.main()
