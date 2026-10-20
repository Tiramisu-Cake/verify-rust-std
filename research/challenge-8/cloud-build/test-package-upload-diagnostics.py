"""Isolated generated packaging/verdict stages, with synthetic packager and no cloud calls."""
import base64
import gzip
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location('packaging_diagnostic_control', HERE / 'control.py')
CONTROL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTROL)


class PackagingDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='packaging-diagnostics-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        with patch.object(CONTROL, 'SDK_PYTHON', sys.executable):
            self.config = CONTROL.config('a' * 40, 'b' * 40, 'smoke-error', 900,
                                         'synthetic-packaging-only')
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        stub = self.bin / 'gcloud'
        stub.write_text('#!/bin/sh\nprintf "unexpected gcloud invocation\\n" >&2\nexit 99\n')
        stub.chmod(0o755)

    def verdict(self):
        code = self.config['steps'][2]['args'][1].replace('/workspace', str(self.root))
        return subprocess.run([sys.executable, '-c', code], text=True, capture_output=True)

    def test_primary_packaging_error_survives_missing_and_stale_summary(self):
        primary = 'evidence packaging failed: external manifest exceeds 8 MiB\n'
        source = 'import sys\nsys.stderr.write(' + repr(primary) + ')\nsys.exit(17)\n'
        self.config['steps'][1]['env'] = []
        script = self.config['steps'][1]['args'][1].replace('$$', '$').replace('/workspace', str(self.root))
        # A failed fresh packaging attempt must override stale acceptance markers.
        out = self.root / 'out'
        out.mkdir()
        (out / 'summary.json').write_text(json.dumps({'verification_accepted': True}))
        (self.root / 'upload.ok').touch()
        env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ['PATH'],
                   PACKAGER_BYTES=base64.b64encode(gzip.compress(source.encode())).decode())
        result = subprocess.run(['bash', '-ceu', script], text=True, capture_output=True, env=env)
        self.assertEqual(result.returncode, 17, result.stderr)
        record = json.loads((self.root / 'package-upload-error.json').read_text())
        self.assertEqual(record['primary_error'], primary)
        self.assertEqual(record['exit_code'], 17)
        self.assertEqual(record['failure_class'], 'packaging-failed')
        self.assertEqual(record['proof_status'], 'UNCHANGED')
        self.assertFalse((self.root / 'upload.ok').exists())
        for stale in (True, False):
            if not stale:
                (out / 'summary.json').unlink()
            final = self.verdict()
            self.assertEqual(final.returncode, 2)
            self.assertIn('external manifest exceeds 8 MiB', final.stdout)
            self.assertNotIn('FileNotFoundError', final.stdout)
            self.assertNotIn('SMALLSORT_FINAL_VERDICT', final.stdout)

    def test_missing_output_has_explicit_infrastructure_diagnostic(self):
        result = self.verdict()
        self.assertEqual(result.returncode, 2)
        self.assertIn('missing-packaging-output', result.stdout)
        self.assertNotIn('FileNotFoundError', result.stdout)

    def test_malformed_or_null_failure_record_never_falls_through_to_acceptance(self):
        out = self.root / 'out'
        out.mkdir()
        (out / 'summary.json').write_text(json.dumps({'verification_accepted': True}))
        (self.root / 'upload.ok').touch()
        for value in ('{', 'null', '[]'):
            (self.root / 'package-upload-error.json').write_text(value)
            result = self.verdict()
            self.assertEqual(result.returncode, 2)
            self.assertIn('packaging-failed', result.stdout)
            self.assertNotIn('SMALLSORT_FINAL_VERDICT', result.stdout)

    def test_existing_failure_success_and_missing_upload_semantics_remain(self):
        out = self.root / 'out'
        out.mkdir()
        summary = out / 'summary.json'
        summary.write_text(json.dumps({'verification_accepted': False, 'smoke_success': False,
                                       'diagnostic_complete': False}))
        (self.root / 'upload.ok').touch()
        self.assertEqual(self.verdict().returncode, 1)
        summary.write_text(json.dumps({'verification_accepted': False, 'smoke_success': True,
                                       'diagnostic_complete': False}))
        self.assertEqual(self.verdict().returncode, 0)
        (self.root / 'upload.ok').unlink()
        self.assertEqual(self.verdict().returncode, 1)

    def test_config_arguments_remain_bounded(self):
        self.assertTrue(all(len(arg.encode()) <= 10000 for step in self.config['steps']
                            for arg in step.get('args', [])))


if __name__ == '__main__':
    unittest.main()
