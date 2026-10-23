"""Isolated static/synthetic controls for the R24 translator overlay."""

import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HISTORY = ROOT / "task-history" / "select-callee-r24"
PATCH = HISTORY / "checked-pointer-outcomes-r24.patch"
PINS = HISTORY / "CHECKED-OUTCOMES-PINS.json"


def admit(env, certs, ignore_unwind=False):
    """Synthetic opt-in gate matching the documented admission contract."""
    flag = env.get("SORT4_R24_CHECKED_POINTER_OUTCOMES")
    if flag is None:
        return False
    if flag != "1":
        raise ValueError("flag")
    if env.get("SORT4_R24_SESSION_PHASE_ID") != "SORT4-ACTUAL-SELECT-2026-10-24-R24":
        raise ValueError("session phase")
    if env.get("SORT4_R20_CALLEE_PHASE_ID") != "SORT4-ACTUAL-SELECT-2026-10-23-R21":
        raise ValueError("route")
    if not all(certs.values()) or ignore_unwind:
        raise ValueError("certificates/unwind")
    return True


def exact_call(row, expected):
    """Synthetic exact-shape guard: any changed edge or operand refuses."""
    if row != expected:
        raise ValueError("call shape")
    return True


class CheckedPointerOutcomeTests(unittest.TestCase):
    def test_pins_and_patch_hash(self):
        pins = json.loads(PINS.read_text())
        self.assertEqual(hashlib.sha256(PATCH.read_bytes()).hexdigest(), pins["patch_sha256"])
        self.assertEqual(pins["base_translator_sha256"], "103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44")
        self.assertEqual(len(pins["projects"]), 2)

    def test_patch_reproduces_pinned_translator(self):
        base = pathlib.Path("/tmp/r24-translator103.ml")
        if not base.exists():
            self.skipTest("pinned external translator baseline unavailable")
        pins = json.loads(PINS.read_text())
        self.assertEqual(hashlib.sha256(base.read_bytes()).hexdigest(), pins["base_translator_sha256"])
        with tempfile.TemporaryDirectory(prefix="r24-translator-patch-") as temp:
            root = pathlib.Path(temp)
            target = root / "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
            target.parent.mkdir(parents=True)
            shutil.copyfile(base, target)
            subprocess.run(["git", "apply", str(PATCH)], cwd=root, check=True)
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), pins["result_translator_sha256"])

    def test_patch_is_opt_in_checked_result_only(self):
        patch = PATCH.read_text()
        self.assertIn('"SORT4_R24_CHECKED_POINTER_OUTCOMES"', patch)
        self.assertIn('Some "SORT4-ACTUAL-SELECT-2026-10-24-R24"', patch)
        self.assertIn('Some "SORT4-ACTUAL-SELECT-2026-10-23-R21"', patch)
        self.assertIn("FnCallResult (result_of_outcome fn_loc call)", patch)
        self.assertIn("checked_r24_pointer_outcome ->", patch)
        self.assertNotIn("(!Sort4SelectIntrinsic.actual_certified ||", patch)
        self.assertIn("SORT4-R24-CHECKED-POINTER-OUTCOMES", patch)
        self.assertNotIn("ignore_unwind_paths :=", patch)

    def test_default_off_and_wrong_route_refusal(self):
        self.assertFalse(admit({}, {}))
        env = {
            "SORT4_R24_CHECKED_POINTER_OUTCOMES": "1",
            "SORT4_R24_SESSION_PHASE_ID": "SORT4-ACTUAL-SELECT-2026-10-24-R24",
            "SORT4_R20_CALLEE_PHASE_ID": "SORT4-ACTUAL-SELECT-2026-10-23-R21",
        }
        certs = dict(intrinsic=True, owner=True, nine=True, pointer_drop=True, a1_nine=True, a1_link=True, fractional=True)
        self.assertTrue(admit(env, certs))
        for field in ("SORT4_R24_SESSION_PHASE_ID", "SORT4_R20_CALLEE_PHASE_ID"):
            changed = dict(env, **{field: "wrong"})
            with self.assertRaises(ValueError):
                admit(changed, certs)
        with self.assertRaises(ValueError):
            admit(dict(env, SORT4_R24_CHECKED_POINTER_OUTCOMES="true"), certs)
        with self.assertRaises(ValueError):
            admit(env, dict(certs, a1_link=False))
        with self.assertRaises(ValueError):
            admit(env, certs, ignore_unwind=True)

    def test_selected_call_shape_and_drift(self):
        expected = dict(callee="mut_ptr.drop_in_place", ty="*const Element", operand="Move(_32)", destination="_31", normal=16, cleanup=28)
        self.assertTrue(exact_call(expected, expected))
        for field, value in (("ty", "*mut Element"), ("operand", "Copy(_32)"),
                             ("destination", "_30"), ("normal", 17), ("cleanup", 27),
                             ("callee", "other")):
            changed = dict(expected, **{field: value})
            with self.assertRaises(ValueError):
                exact_call(changed, expected)

    def test_assume_init_call_shape_and_drift(self):
        expected = dict(callee="MaybeUninit.assume_init", ty="*const Element", operand="Move(_41)", destination="_0", normal=25, cleanup=28)
        self.assertTrue(exact_call(expected, expected))
        for field, value in (("ty", "*mut Element"), ("operand", "Copy(_41)"),
                             ("destination", "_1"), ("normal", 24), ("cleanup", 27),
                             ("callee", "other")):
            changed = dict(expected, **{field: value})
            with self.assertRaises(ValueError):
                exact_call(changed, expected)


if __name__ == "__main__":
    unittest.main()
