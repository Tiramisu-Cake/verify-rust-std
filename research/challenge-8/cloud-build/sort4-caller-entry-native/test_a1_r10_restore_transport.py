"""Lossless config transport tests; decodes source bytes, never executes them."""
import base64
import copy
import gzip
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLOUD = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CLOUD))
spec = importlib.util.spec_from_file_location('r10_restore_control', CLOUD/'control.py')
CONTROL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CONTROL)

class RestoreTransport(unittest.TestCase):
    def test_exact_generated_decoder_roundtrips_both_codecs(self):
        source = (CLOUD/'source-input.py').read_bytes()
        for phase in (CONTROL.A1_R9_PHASE, CONTROL.A1_R10_PHASE):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as td:
                encoded, command = CONTROL.source_restore_transport(source, phase)
                command = command.replace('/workspace', td)
                r = subprocess.run(['bash', '-ceu', 'set -o pipefail\n'+command],
                                   env={**os.environ, 'SOURCE_RESTORE_BYTES': encoded},
                                   capture_output=True)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual((Path(td)/'source-input.py').read_bytes(), source)
                if phase == CONTROL.A1_R9_PHASE:
                    self.assertEqual(encoded, base64.b64encode(gzip.compress(source, mtime=0)).decode())
                    self.assertEqual(CONTROL.source_restore_transport(source, None), CONTROL.source_restore_transport(source, CONTROL.A1_R9_PHASE))
                    self.assertIn('base64 --decode | gzip --decompress', command)

    def test_corruption_fails_before_valid_output(self):
        for phase in (CONTROL.A1_R9_PHASE, CONTROL.A1_R10_PHASE):
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as td:
                _, command = CONTROL.source_restore_transport(b'not executed', phase)
                r = subprocess.run(['bash', '-ceu', 'set -o pipefail\n'+command.replace('/workspace', td)],
                                   env={**os.environ, 'SOURCE_RESTORE_BYTES': 'AAAA'}, capture_output=True)
                self.assertNotEqual(r.returncode, 0)
                output = Path(td)/'source-input.py'
                self.assertFalse(output.exists() and output.read_bytes() == b'not executed')

    def test_real_length_tokens_keep_caps_and_headroom(self):
        repo = CLOUD.parents[2]
        sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
        for suffix in ('0'*32, 'f'*32, '2ee66d6aedfc4b36918298ebf1cb8a47'):
            cfg = CONTROL.config(sha, sha, 'o26-sort4-c1-current-recovery', 1200,
                                 'dispatch-'+suffix, b'x'*540827, CONTROL.A1_R10_PHASE)
            self.assertLessEqual(len(cfg['substitutions']), 200)
            self.assertTrue(all(len(v.encode()) <= 4000 for v in cfg['substitutions'].values()))
            self.assertTrue(all(len(arg.encode()) <= 10000 for step in cfg['steps'] for arg in step['args']))
            submitted = copy.deepcopy(cfg)
            for key in submitted['substitutions']:
                if key.startswith('_SOURCE_'):
                    submitted['substitutions'][key] = 'placeholder'
            raw = (json.dumps(submitted, separators=(',', ':'))+'\n').encode()
            self.assertLessEqual(len(base64.b64encode(gzip.compress(raw, mtime=0))), 27800)

if __name__ == '__main__':
    unittest.main()
