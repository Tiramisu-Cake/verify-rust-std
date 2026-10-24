"""Static native-patch checks; no Rust preparation or actual tool execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[3]
HISTORY = REPO / 'research/challenge-8/task-history/select-callee-r24'
GENERATOR = HISTORY / 'w4-control-fingerprint-r24.py'
SPEC = importlib.util.spec_from_file_location('r24_control_fingerprint_authoring', GENERATOR)
GEN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GEN)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class NativeDataPatchTests(unittest.TestCase):
    def test_exact_manifest_and_additive_patch_reconstruction(self):
        manifest = json.loads((HISTORY / 'W4-CONTROL-FINGERPRINT-MANIFEST.json').read_text())
        patch = (REPO / manifest['patch']['path']).read_bytes()
        self.assertEqual(sha(patch), manifest['patch']['sha256'])
        self.assertEqual(sha(GENERATOR.read_bytes()), manifest['generator_sha256'])
        # This exact historical source is authoring scratch, never a tool run.
        base_path = Path('/tmp/r24-translator-contract-native-exit.ml')
        if not base_path.is_file():
            self.skipTest('exact authoring base is unavailable; manifest checks passed')
        base = base_path.read_bytes()
        self.assertEqual(sha(base), GEN.BASE_SHA256)
        generated = GEN.generate(base)
        self.assertEqual(sha(generated), manifest['result_translator_sha256'])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
            source.parent.mkdir(parents=True)
            source.write_bytes(base)
            target = root / 'candidate.patch'
            target.write_bytes(patch)
            subprocess.run(['git', '-C', str(root), 'apply', '--check', str(target)], check=True)
            subprocess.run(['git', '-C', str(root), 'apply', str(target)], check=True)
            self.assertEqual(source.read_bytes(), generated)
            subprocess.run(['git', '-C', str(root), 'apply', '-R', str(target)], check=True)
            self.assertEqual(source.read_bytes(), base)
        with self.assertRaisesRegex(ValueError, 'exact f83'):
            GEN.generate(base + b'\n')

    def test_default_inactive_and_fail_closed_dispatch(self):
        self.assertIn('| None, None, None -> Ok ()', GEN.DISPATCH)
        self.assertIn('unknown data environment key', GEN.DISPATCH)
        self.assertIn('partial environment', GEN.DISPATCH)
        self.assertIn('exact R24/R21/provider/profile/lane route required', GEN.PROBE)
        self.assertIn('fresh canonical nonsymlink evidence directory required', GEN.PROBE)
        self.assertIn('Open_excl', GEN.PROBE)
        self.assertIn('exact single sort4_stable body required', GEN.PROBE)
        self.assertIn('if hash source <> expected_source then refuse', GEN.PROBE)
        self.assertIn('Marshal.to_string (D.decode_vf_mir vf_mir)', GEN.PROBE)
        self.assertIn('Marshal.to_string (D.decode_body body)', GEN.PROBE)
        self.assertTrue(GEN.PROBE.rstrip().endswith('refuse "snapshot complete; no proof rule admitted"'))
        self.assertNotIn('translate_body', GEN.PROBE)
        self.assertNotIn('assume', GEN.PROBE)
        self.assertIn(r'\"body_proof_run\":false', GEN.PROBE)
        self.assertIn(r'\"caller_body_proof_admission\":false', GEN.PROBE)
        self.assertIn(r'\"proof_credit\":0', GEN.PROBE)


if __name__ == '__main__':
    unittest.main()
