#!/usr/bin/env python3
"""Static and synthetic checks only; never invoke Rust/Kani or dispatch CI."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

WORKTREE = Path(sys.argv.pop(1)) if len(sys.argv) > 1 else Path('/root/kani-fix-3300-c2-slices-w15')
sys.path.insert(0, str(WORKTREE / '.github/c2-slices'))
spec = importlib.util.spec_from_file_location('slice_ci', WORKTREE / '.github/c2-slices/slice06_ci.py')
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)
GOOD = 'test selector ... ok\n\ntest result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 0.01s\n'


class RunnerChecks(unittest.TestCase):
    def test_success(self):
        self.assertEqual(ci.check_output(GOOD, {'selector': False}), [])

    def test_partial(self):
        self.assertTrue(ci.check_output('test selector ... ok\n', {'selector': False}))

    def test_missing(self):
        self.assertTrue(ci.check_output('', {'selector': False}))

    def test_null_wrong_type(self):
        for value in [None, {}, []]:
            with self.assertRaises(TypeError):
                ci.check_output(value, {'selector': False})

    def test_zero_unit_selection(self):
        self.assertTrue(ci.check_output('test result: ok. 0 passed; 0 failed; 0 ignored;', {'selector': False}))

    def test_substituted_name(self):
        self.assertTrue(ci.check_output(GOOD.replace('test selector', 'test other'), {'selector': False}))

    def test_new_ignore(self):
        self.assertTrue(ci.check_output(GOOD.replace('... ok', '... ignored'), {'selector': False}))

    def test_native_timeout(self):
        self.assertTrue(ci.check_output(GOOD + 'Process timed out after 2400s', {'selector': False}))

    def test_duplicate_results(self):
        self.assertTrue(ci.check_output(GOOD + GOOD, {'selector': False}))

    def test_execute_success_and_original_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            self.assertTrue(ci.execute('success', [sys.executable, '-c', 'print(' + repr(GOOD) + ')'], out, {'selector': False}))
            self.assertFalse(ci.execute('failure', [sys.executable, '-c', 'import sys; print("original-error",file=sys.stderr); sys.exit(7)'], out))
            record = json.loads((out / 'failure/result.json').read_text())
            self.assertEqual(record['exit'], 7)
            self.assertEqual(record['termination_reason'], 'EXIT')
            self.assertEqual((out / 'failure/stderr.txt').read_text().strip(), 'original-error')

    def test_execute_timeout(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            self.assertFalse(ci.execute('timeout', [sys.executable, '-c', 'import time; time.sleep(2)'], out, timeout=0.03))
            record = json.loads((out / 'timeout/result.json').read_text())
            self.assertEqual(record['termination_reason'], 'TIMEOUT')
            self.assertLess(record['exit'], 0)

    def test_launch_error(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            self.assertFalse(ci.execute('missing-command', ['/nonexistent-c2-slices-command'], out))
            record = json.loads((out / 'missing-command/result.json').read_text())
            self.assertEqual(record['termination_reason'], 'LAUNCH_ERROR')
            self.assertIsNone(record['exit'])

    def test_not_run_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            with patch.dict(ci.os.environ, {'C2_EVIDENCE_DIR': str(out)}), patch.object(ci.sys, 'argv', ['runner', 'before']), patch.object(ci, 'snapshot'):
                ci.main()
            record = json.loads((out / 'units/result.json').read_text())
            self.assertEqual(record['result'], 'NOT_RUN')
            self.assertIsNone(record['exit'])

    def test_source_stage_target_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            original_inputs = ci.inputs
            config, manifest = original_inputs()
            config['source_tree'] = 'bad-tree'
            with patch.object(ci, 'inputs', return_value=(config, manifest)), self.assertRaises(ValueError):
                ci.snapshot('bad', out)
            record = json.loads((out / 'source-bad.json').read_text())
            self.assertIn('overlay parent/source tree mismatch', record['problems'])

    def test_untracked_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            real_git = ci.git
            def dirty_git(*args):
                return b'?? kani-compiler/src/extra.rs\n' if args[0] == 'status' else real_git(*args)
            with patch.object(ci, 'git', side_effect=dirty_git), self.assertRaises(ValueError):
                ci.snapshot('dirty', out)
            record = json.loads((out / 'source-dirty.json').read_text())
            self.assertIn('worktree is not clean (including untracked source/test paths)', record['problems'])
            self.assertEqual(record['status_porcelain'], '?? kani-compiler/src/extra.rs\n')

    def test_manifest_and_selection(self):
        config, manifest = ci.inputs()
        groups = ci.suites(manifest)
        self.assertEqual({suite: (len(items), sum(i['existing_path_ignore'] for i in items.values())) for (suite, _), items in groups.items()},
                         {'kani': (53, 3), 'expected': (379, 6), 'ui': (17, 0), 'script-based-pre': (3, 0), 'json-handler': (17, 0), 'std-checks': (2, 0)})
        self.assertEqual(len(manifest['active_call_units']), 9)
        self.assertEqual(len(manifest['immutable_unit_names']), 9)
        # Validate every input/golden/helper identity in the exact source commit.
        files = {f['path']: f['identity'] for g in manifest['groups'] for s in g['selectors'] for f in s['files']}
        for name, identity in files.items():
            data = subprocess.check_output(['git', '-C', str(WORKTREE), 'show', config['source_sha'] + ':' + name])
            self.assertEqual(hashlib.sha256(data).hexdigest(), identity['sha256'], name)
        prefix = 'kani_middle::points_to::points_to_analysis::active_call_tests::'
        source = (WORKTREE / 'kani-compiler/src/kani_middle/points_to/points_to_analysis.rs').read_text()
        for name in manifest['active_call_units']:
            self.assertIn('fn ' + name + '()', source)
            self.assertIn(prefix, (WORKTREE / '.github/c2-slices/slice06_ci.py').read_text())

    def test_immutable_selection(self):
        config, manifest = ci.inputs()
        expected = {'codegen_cprover_gotoc::context::immutable_allocations::tests::' + n: False
                    for n in manifest['immutable_unit_names']}
        self.assertEqual(len(expected), 9)
        self.assertEqual(ci.COMMANDS['immutable-units'][4], 'immutable_allocations::tests')
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(ci.os.environ, {'C2_EVIDENCE_DIR': directory}), patch.object(ci.sys, 'argv', ['runner', 'immutable-units']), patch.object(ci, 'execute', return_value=True) as execute:
                ci.main()
                self.assertEqual(execute.call_args.args[3], expected)
        text = '\n'.join('test ' + n + ' ... ok' for n in expected)
        text += '\ntest result: ok. 9 passed; 0 failed; 0 ignored;'
        self.assertEqual(ci.check_output(text, expected), [])
        self.assertTrue(ci.check_output(text.replace('9 passed', '0 passed'), expected))
        self.assertTrue(ci.check_output(text.replace('tests::zero_is_initialized_hole_is_not', 'tests::substitute'), expected))

    def test_immutable_not_run(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            with patch.dict(ci.os.environ, {'C2_EVIDENCE_DIR': directory}), patch.object(ci.sys, 'argv', ['runner', 'before']), patch.object(ci, 'snapshot'):
                ci.main()
            record = json.loads((out / 'immutable-units/result.json').read_text())
            self.assertEqual(record['result'], 'NOT_RUN')
            self.assertIsNone(record['exit'])

    def test_new_units_exact_nonzero_and_not_run(self):
        config, manifest = ci.inputs()
        self.assertEqual(config['effective_targeted_unit_count'], 20)
        self.assertEqual(set(config['additional_units']), {'argument-size-units', 'marker-category-units', 'compiler-all-units'})
        for action, spec in config['additional_units'].items():
            if action == 'compiler-all-units':
                continue
            self.assertEqual(ci.COMMANDS[action][4], spec['filter'])
            expected = {name: False for name in spec['native_names']}
            self.assertEqual(len(expected), 1)
            with tempfile.TemporaryDirectory() as directory:
                out = Path(directory)
                with patch.dict(ci.os.environ, {'C2_EVIDENCE_DIR': directory}), patch.object(ci.sys, 'argv', ['runner', action]), patch.object(ci, 'execute', return_value=True) as execute:
                    ci.main()
                    self.assertEqual(execute.call_args.args[3], expected)
                with patch.dict(ci.os.environ, {'C2_EVIDENCE_DIR': directory}), patch.object(ci.sys, 'argv', ['runner', 'before']), patch.object(ci, 'snapshot'):
                    ci.main()
                record = json.loads((out / action / 'result.json').read_text())
                self.assertEqual(record['result'], 'NOT_RUN')
                self.assertIsNone(record['exit'])
            good = '\n'.join('test ' + name + ' ... ok' for name in expected) + '\ntest result: ok. 1 passed; 0 failed; 0 ignored;'
            self.assertEqual(ci.check_output(good, expected), [])
            self.assertTrue(ci.check_output(good.replace('1 passed', '0 passed'), expected))
            self.assertTrue(ci.check_output(good.replace(next(iter(expected)), 'substitute'), expected))

    def test_cumulative_force_rerun_and_flags(self):
        config, manifest = ci.inputs()
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(ci.os.environ, {'C2_EVIDENCE_DIR': directory}), patch.object(ci.sys, 'argv', ['runner', 'suites']), patch.object(ci, 'execute', return_value=True) as execute:
                ci.main()
                self.assertEqual(execute.call_count, 6)
                for call in execute.call_args_list:
                    argv = call.args[1]
                    for flag in ['--force-rerun', '--exact', '--no-fail-fast', '--timeout', '--build-base', '--logfile']:
                        self.assertIn(flag, argv)
                    self.assertEqual(argv[argv.index('--timeout')+1], '2400')
                    self.assertNotIn('--object-bits', argv)
                    self.assertNotIn('--ignore-global-asm', argv)
        self.assertEqual(config['sensitivity']['status'], 'REQUIRED_4_OF_4')
        packet = Path(__file__).resolve().parent.parent.parent
        self.assertEqual((WORKTREE / '.github/c2-slices/test-manifest.json').read_bytes(), (packet / 'slice-06/TEST-MANIFEST.json').read_bytes())

    def test_full_compiler_units(self):
        config, _ = ci.inputs()
        spec = config['additional_units']['compiler-all-units']
        self.assertEqual(len(spec['native_names']), 68)
        expected = {n: False for n in spec['native_names']}
        with tempfile.TemporaryDirectory() as directory:
            with patch.dict(ci.os.environ, {'C2_EVIDENCE_DIR': directory}), patch.object(ci.sys, 'argv', ['runner', 'compiler-all-units']), patch.object(ci, 'execute', return_value=True) as execute:
                ci.main()
                self.assertEqual(execute.call_args.args[3], expected)
                self.assertEqual(execute.call_args.args[1], ['cargo','test','-p','kani-compiler','--','--color','never'])
        good = '\n'.join('test ' + n + ' ... ok' for n in expected)+'\ntest result: ok. 68 passed; 0 failed; 0 ignored;'
        self.assertEqual(ci.check_output(good, expected), [])
        self.assertTrue(ci.check_output(good.replace('68 passed','0 passed'), expected))

    def test_prepare_reproduces_overlay(self):
        packet = Path(__file__).resolve().parent
        spec = importlib.util.spec_from_file_location('prepare6', packet/'prepare_overlay.py')
        prepare = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prepare)
        def real_git(*args):
            return subprocess.check_output(['git','-C',str(WORKTREE),*args])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflows = real_git('ls-tree','-r','--name-only',prepare.SOURCE,'--','.github/workflows').decode().splitlines()
            for name in workflows:
                file = root/name; file.parent.mkdir(parents=True,exist_ok=True)
                file.write_bytes(real_git('show',prepare.SOURCE+':'+name))
            def pinned_git(*args):
                if args == ('rev-parse','HEAD'):
                    return (prepare.SOURCE+'\n').encode()
                if args == ('status','--porcelain=v1'):
                    return b''
                return real_git(*args)
            with patch.object(prepare,'WORKTREE',root), patch.object(prepare,'git',side_effect=pinned_git):
                prepare.main()
            for file in (root/'.github').rglob('*'):
                if file.is_file():
                    relative = file.relative_to(root)
                    self.assertEqual(file.read_bytes(),(WORKTREE/relative).read_bytes(),str(relative))

    def test_workflow(self):
        import yaml
        workflow = yaml.load((WORKTREE / '.github/workflows/uninit-quick.yml').read_text(), Loader=yaml.BaseLoader)
        job = workflow['jobs']['uninit']
        self.assertEqual(job['runs-on'], 'ubuntu-24.04')
        self.assertEqual(job['timeout-minutes'], '120')
        self.assertEqual(job['steps'][0]['with']['fetch-depth'], '3')
        self.assertEqual(workflow['env']['RUST_TEST_THREADS'], '2')
        self.assertEqual(job['steps'][-1]['if'], '${{ always() }}')
        self.assertEqual(job['steps'][-2]['if'], '${{ always() }}')
        self.assertEqual(job['steps'][-1]['with']['if-no-files-found'], 'error')
        self.assertEqual(list((WORKTREE / '.github/workflows').iterdir()), [WORKTREE / '.github/workflows/uninit-quick.yml'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
