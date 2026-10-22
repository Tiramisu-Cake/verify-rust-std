#!/usr/bin/env python3
"""Synthetic service tests for network-run.py: fake verifast, no proof tool, no Cloud."""
import importlib.util
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('network_run', HERE / 'network-run.py')
nr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nr)
git = lambda *a: subprocess.check_output(['git', '-C', str(HERE)] + list(a))
CLOUD = {'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build', 'CLOUD_BUILD_ID': 'synthetic', 'PATH': os.environ['PATH']}
FAKE = '''#!/usr/bin/env python3
import os, sys, time, pathlib
src = pathlib.Path('verified/lib.rs').read_bytes()
print('ARGS', sys.argv[1:]); print('ENV', os.environ.get('NETWORK_SWAP_IF_LESS_CALL_LINE'),
      os.environ.get('NETWORK_SWAP_IF_LESS_SOURCE_SHA256'), os.environ.get('SORT4_ACTUAL_BODY_C1_RECOVERY'))
mode = os.environ.get('FAKE_MODE', 'ok')
if mode == 'sleep': time.sleep(60)
sys.exit({'ok': 0, 'fail': 1}.get(mode, 3))
'''


class NetworkRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d = Path(self.tmp.name)
        std = self.d / 'smallsort.rs'; std.write_bytes(git('cat-file', '-p', '40939f922bcb6fdc7ee0d30427fa861827043827'))
        pair = self.d / 'pair.rs'; pair.write_bytes(git('cat-file', '-p', 'a29ad2542a4eb4c70686786c3426ab742672e761'))
        self.controls = self.d / 'r4'
        subprocess.run(['python3', '-B', str(HERE.parent / 'r4' / 'swap-if-less-body.py'), str(std), str(pair),
                        str(self.controls)], check=True, capture_output=True)
        self.w7 = self.d / 'w7'
        subprocess.run(['python3', '-B', str(HERE.parent / 'w7' / 'network-body.py'), str(std), str(pair),
                        str(self.w7)], check=True, capture_output=True)
        self.tool = self.d / 'tool'
        (self.tool / 'bin').mkdir(parents=True)
        fake = self.tool / 'bin' / 'verifast'
        fake.write_text(FAKE)
        fake.chmod(fake.stat().st_mode | stat.S_IEXEC)

    def run_main(self, controls, env=None, timeout='30', tag='a'):
        args = ['--tool', str(self.tool), '--controls', str(controls), '--work', str(self.d / ('work' + tag)),
                '--evidence', str(self.d / ('ev' + tag)), '--timeout', timeout]
        return nr.main(args, dict(CLOUD, **(env or {})))

    def summary(self, tag='a'):
        return json.loads((self.d / ('ev' + tag) / 'summary.json').read_text())

    def test_success_records_raw_observations_and_optin(self):
        self.assertEqual(self.run_main(self.controls, {'SORT4_ACTUAL_BODY_C1_RECOVERY': '1'}), 0)
        s = self.summary()
        meta = json.loads((self.controls / 'meta.json').read_text())
        self.assertEqual({r['control'] for r in s['controls']}, set(meta['controls']))
        for r in s['controls']:
            self.assertEqual((r['classification'], r['exit']), ('OBSERVED_UNCLASSIFIED', 0))
            out = (self.d / 'eva' / (r['control'] + '.stdout')).read_text()
            self.assertIn(f"ENV {meta['controls'][r['control']]['crate_call_line']} {meta['controls'][r['control']]['crate_sha256']} None", out)
        self.assertFalse(s['proof_credit'])
        self.assertNotIn('PASS', json.dumps(s))

    def test_error_exit_preserved(self):
        self.assertEqual(self.run_main(self.controls, {'FAKE_MODE': 'fail'}), 0)
        self.assertTrue(all(r['exit'] == 1 for r in self.summary()['controls']))

    def test_timeout(self):
        meta = json.loads((self.controls / 'meta.json').read_text())
        meta['controls'] = {'positive': meta['controls']['positive']}
        (self.controls / 'meta.json').write_text(json.dumps(meta))
        self.assertEqual(self.run_main(self.controls, {'FAKE_MODE': 'sleep'}, timeout='30'), 0)
        r = self.summary()['controls'][0]
        self.assertEqual((r['timed_out'], r['exit'], r['classification']), (True, None, 'OBSERVED_UNCLASSIFIED'))

    def test_missing_and_wrong_sha_are_explicit_not_run(self):
        (self.controls / 'own-drop.rs').unlink()
        (self.controls / 'copy-offset.rs').write_bytes(b'tampered')
        self.assertEqual(self.run_main(self.controls), 2)
        rows = {r['control']: r for r in self.summary()['controls']}
        self.assertEqual((rows['own-drop']['classification'], rows['own-drop']['reason']), ('NOT_RUN', 'control crate missing'))
        self.assertEqual(rows['copy-offset']['classification'], 'NOT_RUN')
        self.assertFalse(self.summary()['complete'])

    def test_missing_tool_is_error(self):
        (self.tool / 'bin' / 'verifast').unlink()
        self.assertEqual(self.run_main(self.controls), 2)
        self.assertTrue(all(r['classification'] == 'ERROR' for r in self.summary()['controls']))

    def test_w7_meta_groups(self):
        self.assertEqual(self.run_main(self.w7), 0)
        names = {r['control'] for r in self.summary()['controls']}
        self.assertIn('sort9-positive', names)
        self.assertIn('sort13-reach-after-last', names)

    def test_refusals(self):
        with self.assertRaisesRegex(SystemExit, 'Cloud Build provider'):
            nr.main(['--tool', 'x', '--controls', str(self.controls), '--work', 'w', '--evidence', 'e'], {})
        meta_path = self.controls / 'meta.json'
        for bad in ([], {'controls': {}}, {'controls': {'positive': {'crate_sha256': 'x'}}},
                    {'controls': {'positive': {'crate_sha256': '0' * 64, 'crate_call_line': '9'}}}):
            meta_path.write_text(json.dumps(bad))
            with self.assertRaises(SystemExit):
                self.run_main(self.controls, tag=str(len(json.dumps(bad))))
        with self.assertRaisesRegex(SystemExit, 'timeout'):
            self.run_main(self.controls, timeout='5', tag='t')

    def test_existing_output_refused(self):
        (self.d / 'eva').mkdir()
        with self.assertRaisesRegex(SystemExit, 'must not exist'):
            self.run_main(self.controls)


if __name__ == '__main__':
    unittest.main()
