#!/usr/bin/env python3
"""Isolated service tests for cold-image.sh; every Docker call is stubbed."""

import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[4]
SCRIPT = Path(__file__).with_name('cold-image.sh')
AUDIT = Path(__file__).with_name('cold-image-audit.py')
LOCK = Path('/root/refinedrust-feasibility-sources/refinedrust-332d945fafa14bf55c0c8390cb35ec4b0c012cff/rr_frontend/Cargo.lock')
BUILD_ID = '01234567-89ab-cdef-0123-456789abcdef'
REGISTRY = 'us-central1-docker.pkg.dev/smallsort-ci/smallsort-tools/refinedrust-g1'
DIGEST = REGISTRY + '@sha256:' + 'a' * 64

DOCKER_STUB = r'''#!/usr/bin/env python3
import json, os, pathlib, shutil, sys
argv=sys.argv[1:]
mode=os.environ.get('DOCKER_MOCK_MODE','success')
trace=pathlib.Path(os.environ['DOCKER_TRACE'])
with trace.open('a') as f:
    f.write(json.dumps({'argv':argv,'api':os.environ.get('DOCKER_API_VERSION'),
                        'config':os.environ.get('DOCKER_CONFIG')})+'\n')
cmd=argv[0] if argv else ''
if cmd=='version':
    versions={
      'success': {'Client':{'ApiVersion':'1.41'},'Server':{'ApiVersion':'1.44','MinAPIVersion':'1.24'}},
      'version-missing': {'Client':{'ApiVersion':'1.41'}},
      'version-null': None,
      'version-wrong-type': ['not','an','object'],
    }
    print(json.dumps(versions.get(mode,versions['success'])))
elif cmd=='build':
    print('synthetic build '+mode)
    if mode=='build-error': sys.exit(37)
    if mode=='build-timeout': sys.exit(124)
elif cmd=='create':
    print('mock-container')
elif cmd=='cp':
    src,dest=argv[1:]
    target=pathlib.Path(dest); target.parent.mkdir(parents=True,exist_ok=True)
    if src.endswith('/opt/g1-image-receipt.json'):
        target.write_text('{"synthetic":"inert image receipt"}\n')
    elif src.endswith('/opt/refinedrust/rr_frontend/Cargo.lock'):
        shutil.copyfile(os.environ['LOCK_FIXTURE'],target)
    elif src.endswith('/opt/g1-executables.sha256'):
        target.write_text('synthetic executable hashes; no binary executed\n')
    else: sys.exit(41)
elif cmd=='rm':
    pass
elif cmd=='push':
    print('synthetic push')
elif cmd=='inspect':
    if mode=='foreign-repository': print(json.dumps(['unrelated.example/image@sha256:'+'b'*64]))
    else: print(json.dumps([os.environ['SYNTHETIC_DIGEST']]))
else:
    print('unexpected docker command: '+repr(argv),file=sys.stderr)
    sys.exit(89)
'''


class ColdScriptServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cold-script-service-')
        self.base = Path(self.temp.name)
        self.root = self.base / 'workspace'
        self.evidence = self.root / 'evidence'
        self.bin = self.base / 'bin'
        self.bin.mkdir(parents=True)
        self.trace = self.base / 'docker-trace.jsonl'
        self.docker_config = self.base / 'docker-config'
        self.docker_config.mkdir()
        (self.docker_config / 'config.json').write_text('{"auths":{"synthetic":"unchanged"}}\n')
        self.config_bytes = (self.docker_config / 'config.json').read_bytes()
        (self.bin / 'docker').write_text(DOCKER_STUB)
        (self.bin / 'docker').chmod(0o755)
        self.script = self.base / 'cold-image.sh'
        source = SCRIPT.read_text()
        source = source.replace('ROOT=/workspace', f'ROOT={self.root}')
        source = source.replace('[[ "$EVIDENCE_ROOT" == /workspace/* ]]', '[[ "$EVIDENCE_ROOT" == "$ROOT"/* ]]')
        source = source.replace('[[ -S /var/run/docker.sock ]]', '[[ -S "$ROOT/docker.sock" ]]')
        self.script.write_text(source)
        proof = self.root / 'proof/research/challenge-8/network/rr/g1/cloud'
        proof.mkdir(parents=True)
        for name in ('Dockerfile.candidate', 'IMAGE-INPUTS.json', 'write-image-receipt.py'):
            (proof / name).write_text('synthetic pinned package fixture\n')
        infra = self.root / 'infra/research/challenge-8/cloud-build/network-rr'
        infra.mkdir(parents=True)
        shutil.copyfile(AUDIT, infra / 'cold-image-audit.py')
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(str(self.root / 'docker.sock'))
        sock.close()
        self.env = os.environ.copy()
        self.env.update({
            'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
            'CLOUD_BUILD_ID': BUILD_ID,
            'COLD_IMAGE_TAG': 'n8-' + BUILD_ID,
            'EVIDENCE_ROOT': str(self.evidence),
            'DOCKER_CONFIG': str(self.docker_config),
            'DOCKER_TRACE': str(self.trace),
            'DOCKER_MOCK_MODE': 'success',
            'SYNTHETIC_DIGEST': DIGEST,
            'LOCK_FIXTURE': str(LOCK),
            'PATH': str(self.bin) + os.pathsep + '/usr/bin:/bin',
        })

    def tearDown(self):
        self.temp.cleanup()

    def run_script(self, mode='success'):
        env = self.env.copy()
        env['DOCKER_MOCK_MODE'] = mode
        return subprocess.run(['/bin/bash', str(self.script)], cwd=self.base, env=env,
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def read_json(self, path):
        return json.loads(path.read_text())

    def calls(self):
        return [json.loads(line) for line in self.trace.read_text().splitlines()]

    def test_success_push_digest_audit_and_credentials(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = self.read_json(self.evidence / 'cold-image/registry-receipt.json')
        self.assertEqual(receipt['image_digest'], DIGEST)
        self.assertEqual(receipt['stage'], 'cold-image')
        audit = self.read_json(self.evidence / 'allprooflogs/proof-audit.json')
        self.assertTrue(audit['diagnostic_complete'])
        self.assertFalse(audit['accepted'])
        self.assertFalse(audit['proof_credit'])
        calls = self.calls()
        self.assertEqual(calls[0]['argv'][0], 'version')
        self.assertTrue(all(call['api'] == '1.41' for call in calls))
        self.assertTrue(all(call['config'] == str(self.docker_config) for call in calls))
        self.assertEqual((self.docker_config / 'config.json').read_bytes(), self.config_bytes)

    def test_original_build_error_and_timeout_are_preserved(self):
        for mode, code, failure in (('build-error', 37, 'stage-error'),
                                    ('build-timeout', 124, 'timeout')):
            with self.subTest(mode=mode):
                self.trace.unlink(missing_ok=True)
                result = self.run_script(mode)
                self.assertEqual(result.returncode, code, result.stderr)
                status = self.read_json(self.evidence / 'cold-image/build-status.json')
                self.assertEqual(status['exit_code'], code)
                audit = self.read_json(self.evidence / 'allprooflogs/proof-audit.json')
                self.assertEqual(audit['failure_class'], failure)
                commands = [call['argv'][0] for call in self.calls()]
                self.assertIn('build', commands)
                self.assertNotIn('create', commands)

    def test_invalid_docker_version_stops_before_build_and_preserves_snapshot(self):
        for mode in ('version-missing', 'version-null', 'version-wrong-type'):
            with self.subTest(mode=mode):
                self.trace.unlink(missing_ok=True)
                result = self.run_script(mode)
                self.assertEqual(result.returncode, 2, result.stderr)
                snapshot_path = self.evidence / 'cold-image/docker-version.json'
                self.assertTrue(snapshot_path.is_file())
                snapshot = self.read_json(snapshot_path)
                if mode == 'version-null':
                    self.assertIsNone(snapshot)
                preflight = self.read_json(self.evidence / 'cold-image/docker-api-preflight.json')
                self.assertEqual(preflight['state'], 'FAILED')
                self.assertEqual(self.calls()[0]['argv'][0], 'version')
                self.assertNotIn('build', [call['argv'][0] for call in self.calls()])

    def test_foreign_registry_receipt_fails_closed(self):
        result = self.run_script('foreign-repository')
        self.assertNotEqual(result.returncode, 0)
        audit = self.read_json(self.evidence / 'allprooflogs/proof-audit.json')
        self.assertFalse(audit['diagnostic_complete'])
        self.assertFalse(audit['proof_credit'])
        self.assertFalse((self.evidence / 'cold-image/registry-receipt.json').exists())


if __name__ == '__main__':
    unittest.main()
