"""Isolated synthetic capture/runner tests. No real toolchain executable is used."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

BUNDLE = Path('/root/kani-b3-t1/.github/b3-t1')
sys.path.insert(0, str(BUNDLE))
import common
import shim
spec = importlib.util.spec_from_file_location('t1_runner', BUNDLE / 'run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.target = self.source / 'target'
        self.target.mkdir(parents=True)
        self.arm = self.root / 'A1'
        self.env = patch.dict(os.environ, T1_SOURCE=str(self.source), T1_ARM_DIR=str(self.arm),
                              T1_ROW='control', T1_TARGET=str(self.target),
                              T1_REAL_CARGO='/fake/cargo', T1_REAL_GOTO_CC='/fake/goto-cc',
                              T1_LOCKED='1')
        self.env.start()
        self.md = self.target / 'main.kani-metadata.json'
        self.symtab = self.target / 'main.symtab.out'
        self.model = self.target / 'main.out'
        self.symtab.write_bytes(b'codegen')
        self.model.write_bytes(b'final instrumented model')
        self.metadata()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def metadata(self, **changes):
        h = dict(pretty_name='array_typed_copy', goto_file=str(self.symtab))
        h.update(changes)
        self.md.write_text(json.dumps(dict(proof_harnesses=[h], test_harnesses=[])))

    def test_cbmc_captures_final_bound_model_without_execution(self):
        with patch.object(shim, 'execute', side_effect=AssertionError('must never delegate CBMC')), patch('builtins.print'):
            code = shim.cbmc(['--json-ui', str(self.model), '--verbosity', '9'])
        self.assertEqual(code, 86)
        records = list((self.arm / 'records').glob('*.json'))
        self.assertEqual(len(records), 1)
        record = json.loads(records[0].read_text())
        self.assertEqual(record['key'], 'final/control/array_typed_copy')
        self.assertEqual((self.arm / record['record']['path']).read_bytes(), self.model.read_bytes())
        shim.finish_row('control', self.target, 1)

    def test_missing_null_wrong_type_unbound_metadata_rejected(self):
        for changes in [dict(goto_file=None), dict(goto_file=42), dict(pretty_name=None), dict(goto_file=str(self.target/'wrong.symtab.out'))]:
            with self.subTest(changes=changes):
                self.metadata(**changes)
                with self.assertRaises(ValueError):
                    common.bind_harness(self.model)
        self.md.unlink()
        with self.assertRaises(ValueError):
            common.bind_harness(self.model)

    def test_duplicate_capture_and_wrong_invocation_rejected(self):
        with patch('builtins.print'):
            shim.cbmc(['--json-ui', str(self.model)])
            with self.assertRaises(FileExistsError):
                shim.cbmc(['--json-ui', str(self.model)])
        with self.assertRaises(ValueError):
            shim.cbmc(['--version'])

    def test_partial_census_and_wrong_exit_rejected(self):
        with self.assertRaises(ValueError):
            shim.finish_row('control', self.target, 1)
        with self.assertRaises(ValueError):
            shim.finish_row('control', self.target, 0)

    def test_link_capture_before_specialization_and_original_error_exit(self):
        with patch.object(shim, 'execute', return_value=subprocess.CompletedProcess([], 0)):
            self.assertEqual(shim.goto_cc([str(self.symtab), '-o', str(self.model)]), 0)
        kinds = {json.loads(p.read_text())['record']['kind'] for p in (self.arm/'records').glob('*.json')}
        self.assertEqual(kinds, {'symtab', 'linked'})
        with patch.object(shim, 'execute', return_value=subprocess.CompletedProcess([], 7)):
            self.assertEqual(shim.goto_cc([str(self.symtab), '-o', str(self.model)]), 7)

    def test_cargo_alias_locks_and_toolchain_prefix(self):
        with patch.object(shim, 'execute', return_value=subprocess.CompletedProcess([], 0)) as execute:
            self.assertEqual(shim.cargo(['+nightly-2026-10-23', 'build-dev', '--', '--release']), 0)
        self.assertEqual(execute.call_args.args[0], ['/fake/cargo', '+nightly-2026-10-23', 'run', '--locked',
            '--target-dir', 'target/tools', '-p', 'build-kani', '--', 'build-dev', '--', '--release'])

    def test_exceptions_and_original_exits_retained(self):
        with patch.object(common.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['fake'], 1)):
            with self.assertRaises(subprocess.TimeoutExpired):
                common.execute(['fake'], timeout=1)
        events = [json.loads(p.read_text()) for p in (self.arm/'events').glob('*.json')]
        self.assertTrue(any(e['event'] == 'exception' and 'TimeoutExpired' in e['error'] for e in events))
        with patch.object(common.subprocess, 'run', return_value=subprocess.CompletedProcess(['fake'], 9)):
            self.assertEqual(common.execute(['fake']).returncode, 9)
        with patch.object(runner, 'execute', return_value=subprocess.CompletedProcess(['fake'], 9)):
            with self.assertRaises(RuntimeError):
                runner.run(['fake'], self.arm/'failure.log', self.source)

    def test_local_runner_is_guarded(self):
        with patch.dict(os.environ, GITHUB_ACTIONS='false'):
            with self.assertRaisesRegex(RuntimeError, 'CI-only'):
                runner.main(self.source, self.root/'artifacts')

    def test_symlink_path_dispatches_python_capture_only(self):
        bindir = self.root / 'shim-bin'
        bindir.mkdir()
        (bindir / 'cbmc').symlink_to(BUNDLE / 'shim.py')
        # This is the Python mock executable, not CBMC. It must import common via
        # its resolved script location and never delegate to a toolchain.
        result = subprocess.run([str(bindir/'cbmc'), '--json-ui', str(self.model)],
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 86, result.stderr)
        self.assertIn('SAT NOT_RUN', result.stdout)


if __name__ == '__main__':
    unittest.main()
