from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("w4-contract-input-diagnostic.py")
BASE_PATH = Path("/tmp/r24-translator-native5170.ml")
SPEC = importlib.util.spec_from_file_location("w4_contract_input_diagnostic", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


@unittest.skipUnless(BASE_PATH.is_file(), "pinned static translator input is not mounted")
class ContractInputGeneratorTests(unittest.TestCase):
    def test_exact_pinned_base_only_gets_diagnostic_additions(self) -> None:
        base = BASE_PATH.read_bytes()
        patched = GEN.generate(base)
        text = patched.decode("utf-8")
        restored = text.replace(GEN.PROBE + "\n" + GEN.PROBE_ANCHOR,
                                GEN.PROBE_ANCHOR, 1)
        restored = restored.replace(GEN.DISPATCH + GEN.DISPATCH_ANCHOR,
                                    GEN.DISPATCH_ANCHOR, 1)
        self.assertEqual(restored.encode(), base)
        self.assertEqual(hashlib.sha256(base).hexdigest(), GEN.BASE_SHA256)
        self.assertIn("contract inputs matched; no proof rule admitted", text)
        self.assertIn("typed_call_linkage=UNKNOWN", text)
        self.assertIn("caller_body_proof_admission\\\":false", text)
        self.assertIn("SORT4-R24-W4-CONTRACT-INPUTS: diagnostic refusal:", text)

    def test_mut_pointer_refusal_precedes_normalized_pointer_ast_arm(self) -> None:
        exact_arm = GEN.PROBE.index('when case <> "mut-pointer" -> Some spec')
        mut_guard = GEN.PROBE.index('when case = "mut-pointer" &&')
        self.assertLess(exact_arm, mut_guard)
        self.assertIn('contains_text header_bytes "true_val: *mut Element,"',
                      GEN.PROBE)

    def test_patch_applies_to_exact_translator_path(self) -> None:
        base = BASE_PATH.read_bytes()
        patched = GEN.generate(base)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"
            target.parent.mkdir(parents=True)
            target.write_bytes(base)
            patch = root / "change.patch"
            patch.write_text("".join(__import__("difflib").unified_diff(
                base.decode().splitlines(keepends=True),
                patched.decode().splitlines(keepends=True),
                fromfile="a/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
                tofile="b/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
                n=3)), encoding="utf-8")
            subprocess.run(["git", "apply", "--check", str(patch)],
                           cwd=root, check=True, capture_output=True)
            subprocess.run(["git", "apply", str(patch)], cwd=root, check=True,
                           capture_output=True)
            self.assertEqual(target.read_bytes(), patched)

    def test_bad_base_and_closed_case_surface_refuse(self) -> None:
        with self.assertRaises(ValueError):
            GEN.generate(b"not the pinned translator")
        self.assertEqual(list(GEN.CASE_ROWS), [
            "positive", "false-normal", "false-unwind", "duplicate-thread",
            "mut-pointer", "extra-declaration",
        ])
        mode = GEN.expected_mode()
        self.assertFalse(mode["accepted"])
        self.assertFalse(mode["publication_allowed"])
        self.assertEqual(mode["proof_credit"], 0)
        mode["cases"].clear()
        self.assertEqual(len(GEN.expected_mode()["cases"]), 6)


class HeaderSyntaxRegressionTests(unittest.TestCase):
    def test_all_closed_headers_use_the_existing_nontrailing_parameter_grammar(self):
        import json
        repo = MODULE_PATH.parents[4]
        rel = "research/challenge-8/cloud-build/sort4-caller-entry-native/w4-select-callee-r24.rsspec"
        header = (repo / rel).read_bytes()
        previous = subprocess.run(
            ["git", "show", "881ed4be929aaa1c86e9e68bd1519b33127981db:" + rel],
            cwd=repo, check=True, capture_output=True).stdout
        self.assertEqual(header, previous.replace(
            b"    false_val: *const Element,\n", b"    false_val: *const Element\n", 1))
        self.assertEqual(len(previous) - len(header), 1)
        manifest = json.loads(MODULE_PATH.with_name("W4-CONTRACT-HEADER-VARIANTS.json").read_text())
        for case, row in manifest["cases"].items():
            mutation = row["replacement"]
            variant = header if mutation is None else header.replace(
                mutation["from"].encode(), mutation["to"].encode(), 1)
            params = variant.split(b"(", 1)[1].split(b")", 1)[0].rstrip()
            self.assertFalse(params.endswith(b","), case)
            self.assertEqual(hashlib.sha256(variant).hexdigest(), row["sha256"])
            self.assertEqual(len(variant), row["bytes"])
            self.assertEqual(GEN.CASE_ROWS[case], (row["sha256"], row["bytes"]))


if __name__ == "__main__":
    unittest.main()
