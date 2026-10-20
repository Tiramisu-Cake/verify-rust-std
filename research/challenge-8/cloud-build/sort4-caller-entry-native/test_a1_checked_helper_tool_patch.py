"""Static controls for the verifier-side checked-helper stage patch."""
from __future__ import annotations

from pathlib import Path
import subprocess
import unittest


HERE = Path(__file__).resolve().parent
PATCH = HERE / "checked-threshold-contract.patch"


class CheckedHelperToolPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patch = PATCH.read_text()

    def test_patch_is_well_formed_and_stage_is_narrow(self):
        parsed = subprocess.run(
            ["git", "apply", "--numstat", str(PATCH)],
            check=True, capture_output=True, text=True,
        )
        self.assertIn("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
                      parsed.stdout)
        self.assertIn('| Some "checked-helper" ->', self.patch)
        self.assertIn('Some "a1_cleanup_option_ref"', self.patch)
        self.assertIn('"SORT4_A1_CHECKED_HELPER_SOURCE_SHA256"', self.patch)
        self.assertIn('"SORT4_A1_CHECKED_HELPER_BLOCK_SHA256"', self.patch)

    def test_helper_source_hash_focus_and_body_are_bound(self):
        for required in (
            'focus_argument () = "verified/lib.rs:" ^ line',
            'digest_file "verified/lib.rs"',
            '"lem a1_cleanup_option_ref<\'a, T>(value: std::option::Option<&\'a T>)"',
            'line body_end <> "}"',
            'checked helper declaration is not unique in source',
        ):
            self.assertIn(required, self.patch)

    def test_helper_proof_does_not_publish_or_broaden_caller_focus(self):
        self.assertIn(
            '| None | Some "bodies" | Some "interface" | Some "checked-helper" -> false',
            self.patch,
        )
        self.assertIn('| Some "caller" -> true', self.patch)
        self.assertIn('if publication_requested () then begin', self.patch)
        self.assertIn('if focus_argument () <> observer_focus () then', self.patch)
        self.assertIn('Sys.getenv_opt "SORT4_A1_STAGE" <> Some "checked-helper" then begin',
                      self.patch)
        self.assertIn('body stage cannot verify another method or generic caller',
                      self.patch)

    def test_existing_unwind_inventory_and_profile_controls_remain(self):
        for required in (
            'Args.ignore_unwind_paths || Args.skip_specless_fns ||',
            'Args.ignore_ref_creation || Args.allow_ignore_ref_creation',
            'Some "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"',
            'if List.length impls <> 2 then reject "exactly two actual impls required"',
            '"full impl method inventory differs"',
        ):
            self.assertIn(required, self.patch)


if __name__ == "__main__":
    unittest.main()
