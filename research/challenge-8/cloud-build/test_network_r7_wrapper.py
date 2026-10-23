"""Isolated synthetic wrapper tests; never install or run Rust/proof tools."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class R7WrapperTests(unittest.TestCase):
    def run_fixture(self, mode="success", setup=0, runner=0):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            infra, proof, work, evidence = (root / name for name in ("infra", "proof", "work", "evidence"))
            for path in (infra, proof, work, evidence):
                path.mkdir()
            provider = infra / "research/challenge-8/cloud-build/provider.py"
            provider.parent.mkdir(parents=True)
            provider.write_text("print('{\"provider\":\"cloud-build\"}')\n")
            fake_runner = proof / "research/challenge-8/network/r7/run-cloud.py"
            fake_runner.parent.mkdir(parents=True)
            fake_runner.write_text('''import json,os,pathlib,sys
out=pathlib.Path(sys.argv[sys.argv.index('--evidence')+1]);out.mkdir(parents=True)
mode=os.environ['FAKE_AUDIT_MODE']
x={'accepted':False,'proof_credit':False,'lane':'network-n13','stage':'swap-size',
   'component_accepted':True,'diagnostic_complete':True,'classification':'NETWORK_R7_COMPONENT_CHECKED'}
if mode=='partial':x['component_accepted']=False
if mode=='wrong-stage':x['stage']='exact'
if mode=='wrong-lane':x['lane']='other'
if mode=='null':x['component_accepted']=None
if mode=='wrong-type':x['diagnostic_complete']='true'
if mode=='NOT_RUN':x['classification']='NOT_RUN'
if mode=='missing':x.pop('proof_credit')
if mode=='credit':x['accepted']=True
if mode!='missing-file':(out/'proof-audit.json').write_text('{broken' if mode=='malformed' else json.dumps(x))
sys.exit(int(os.environ['FAKE_RUNNER_EXIT']))
''')
            bindir = root / "bin"
            bindir.mkdir()
            timeout = bindir / "timeout"
            timeout.write_text('#!/bin/sh\nprintf "synthetic setup observation\\n"\nexit "$FAKE_SETUP_EXIT"\n')
            timeout.chmod(0o755)
            script = root / "wrapper.sh"
            script.write_text((HERE / "network-n13/run-r7.sh").read_text().replace('/workspace', str(root)))
            env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ['PATH'],
                       NETWORK_STAGE='swap-size', INFRA_ROOT=str(infra), PROOF_ROOT=str(proof),
                       WORK_ROOT=str(work), EVIDENCE_ROOT=str(evidence), FAKE_AUDIT_MODE=mode,
                       FAKE_SETUP_EXIT=str(setup), FAKE_RUNNER_EXIT=str(runner))
            observed = subprocess.run(['bash', str(script), str(work/'tool'), str(evidence/'allprooflogs/cases')],
                                      env=env, capture_output=True, text=True)
            audit = json.loads((evidence/'allprooflogs/proof-audit.json').read_text())
            saved_setup = int((evidence/'allprooflogs/r7-compiler-setup-exit-code.txt').read_text())
            saved_runner = int((evidence/'allprooflogs/r7-runner-exit-code.txt').read_text())
            log = (evidence/'allprooflogs/r7-compiler-setup.log').read_text()
            return observed, audit, saved_setup, saved_runner, log

    def test_success_preserves_component_receipt_without_credit(self):
        observed, audit, setup, runner, log = self.run_fixture()
        self.assertEqual(observed.returncode, 0, observed.stderr)
        self.assertTrue(audit['component_accepted'])
        self.assertTrue(audit['diagnostic_complete'])
        self.assertFalse(audit['accepted'])
        self.assertFalse(audit['proof_credit'])
        self.assertEqual((setup, runner), (0, 0))
        self.assertIn('synthetic setup observation', log)
        self.assertEqual(len(audit['runner_audit_sha256']), 64)

    def test_setup_error_and_timeout_preserve_original_exit(self):
        for code in (17, 124):
            with self.subTest(code=code):
                observed, audit, setup, runner, log = self.run_fixture(setup=code)
                self.assertEqual(observed.returncode, code)
                self.assertEqual(setup, code)
                self.assertFalse(audit['component_accepted'])
                self.assertEqual(audit['compiler_setup_exit_status'], code)
                self.assertIn('synthetic setup observation', log)

    def test_runner_error_and_timeout_cannot_admit_a_success_audit(self):
        for code in (1, 124):
            with self.subTest(code=code):
                observed, audit, setup, runner, _ = self.run_fixture(runner=code)
                self.assertEqual(observed.returncode, code)
                self.assertEqual(runner, code)
                self.assertFalse(audit['component_accepted'])
                self.assertEqual(audit['stage_exit_status'], code)

    def test_partial_missing_malformed_wrong_type_and_mismatched_audits_fail_closed(self):
        for mode in ('partial', 'wrong-stage', 'wrong-lane', 'null', 'wrong-type',
                     'NOT_RUN', 'missing', 'missing-file', 'malformed', 'credit'):
            with self.subTest(mode=mode):
                _, audit, _, _, _ = self.run_fixture(mode)
                self.assertFalse(audit['component_accepted'])
                self.assertFalse(audit['accepted'])
                self.assertFalse(audit['proof_credit'])
                self.assertFalse(audit['diagnostic_complete'])
                self.assertEqual(audit['classification'], 'INCONCLUSIVE')


if __name__ == '__main__':
    unittest.main()
