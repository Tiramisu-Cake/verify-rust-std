"""Isolated shell-boundary tests for the R24 W4 capture-only route.

These execute only the W4 gate, audit function, and capture branch extracted
from the production runner. All Python and stage calls are replaced by local
callbacks; the Cloud runner and toolchain are never started.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


CLOUD = Path(__file__).resolve().parent
REPO = CLOUD.parents[2]
RUNNER = CLOUD / 'run-o26-select-callee-r20.sh'
PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
ROUTE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
BUILD = '12345678-1234-4234-8234-123456789abc'
INTERFACE_REL = Path('research/challenge-8/task-history/select-callee-r23/P2-INTERFACE.json')
QUALIFICATION_REL = Path('research/challenge-8/task-history/select-callee-r24/CONST-CALLEE-QUALIFICATION.json')


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def shell_source() -> str:
    return RUNNER.read_text()


def w4_gate_block() -> str:
    source = shell_source()
    start = source.index('# This separate W4 step captures the unchanged body;')
    end = source.index('positive_ast_args=()', start)
    return source[start:end]


def audit_function() -> str:
    source = shell_source()
    start = source.index('audit_result() {')
    end = source.index('\ntrap ', start)
    return source[start:end]


def w4_capture_branch() -> str:
    source = shell_source()
    after_ldd = source.index('ldd "$source_home/bin/verifast"')
    start = source.index('if (( r24_w4_capture_only == 1 )); then', after_ldd)
    end = source.index('\nrun_const_regression() {', start)
    return source[start:end]


class W4ShellBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.proof = self.root / 'proof'
        self.cloud = self.root / 'cloud'
        self.proof.mkdir()
        self.cloud.mkdir()
        self.mode = self.proof / 'research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-MODE.json'
        self.helper = self.cloud / 'select-callee-r24-w4-capture.py'
        self.interface = self.proof / INTERFACE_REL
        self.qualification = self.proof / QUALIFICATION_REL
        self.mode.parent.mkdir(parents=True, exist_ok=True)
        self.interface.parent.mkdir(parents=True, exist_ok=True)
        self.qualification.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO / INTERFACE_REL, self.interface)
        shutil.copyfile(REPO / QUALIFICATION_REL, self.qualification)
        # The mode/helper are being created by the sibling admission task. Use
        # their real bytes when present; otherwise use inert fixtures and bind
        # the extracted shell block to those local fixture hashes below.
        source_mode = REPO / self.mode.relative_to(self.proof)
        source_helper = CLOUD / self.helper.name
        self.mode.write_bytes(source_mode.read_bytes() if source_mode.is_file() else b'{"synthetic":"mode"}\n')
        self.helper.write_bytes(source_helper.read_bytes() if source_helper.is_file() else b'# synthetic helper fixture\n')
        self.mode_sha = sha(self.mode.read_bytes())
        self.helper_sha = sha(self.helper.read_bytes())

    def tearDown(self):
        self.temp.cleanup()

    def env(self, **overrides):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith('SORT4_') and key not in ('CLOUD_BUILD_ID', 'PROOF_SHA', 'LANE')}
        env.update({'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
                    'r24_mut_proof_enabled': '1',
                    'SORT4_R24_SESSION_PHASE_ID': PHASE,
                    'proof_root': str(self.proof), 'cloud_dir': str(self.cloud),
                    'r24_mut_proof_enabled': '1'})
        env.update(overrides)
        return env

    def bound_gate(self):
        text = w4_gate_block()
        pins = {
            'r24_w4_mode_file': self.mode_sha,
            'r24_w4_helper': self.helper_sha,
        }
        lines = []
        for line in text.splitlines():
            for name, value in pins.items():
                if f'sha256sum "${name}"' in line:
                    before, marker, after = line.partition('==')
                    self.assertTrue(marker, f'{name} hash check absent from extracted shell block')
                    suffix = after[after.index(']]'):]
                    line = before + '== ' + value + ' ' + suffix
            lines.append(line)
        return '\n'.join(lines)

    def run_gate(self, *, mode_present=True, env_extra=None, changed=None):
        if not mode_present:
            self.mode.unlink(missing_ok=True)
        elif changed == 'mode':
            self.mode.write_bytes(self.mode.read_bytes() + b'changed')
        elif changed == 'helper':
            self.helper.write_bytes(self.helper.read_bytes() + b'changed')
        elif changed == 'interface':
            self.interface.write_bytes(self.interface.read_bytes() + b'changed')
        elif changed == 'qualification':
            self.qualification.write_bytes(self.qualification.read_bytes() + b'changed')
        script = ('set -euo pipefail\n'
                  f'proof_root={self.proof}\ncloud_dir={self.cloud}\n'
                  'r24_mut_proof_enabled="${TEST_MUT_ENABLED:-1}"\n'
                  + self.bound_gate() + '\n'
                  'printf "%s\\n" "$r24_w4_capture_only"\n')
        env = self.env(**(env_extra or {}))
        return subprocess.run(['bash', '-c', script], env=env, capture_output=True, text=True)

    def test_absent_mode_keeps_capture_route_off_and_default_pipeline_available(self):
        result = self.run_gate(mode_present=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '0')

    def test_exact_pins_enable_capture_and_changed_dependencies_refuse(self):
        good = self.run_gate()
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(good.stdout.strip(), '1')
        for changed in ('mode', 'helper', 'interface', 'qualification'):
            with self.subTest(changed=changed):
                bad = self.run_gate(changed=changed)
                self.assertEqual(bad.returncode, 2)

    def test_mode_requires_mutable_route_r24_phase_and_no_old_body_route(self):
        invalid_envs = (
            {'TEST_MUT_ENABLED': '0'},
            {'SORT4_R24_SESSION_PHASE_ID': 'wrong'},
            {'SORT4_R24_SESSION_PHASE_ID': ''},
            {'SORT4_R21_BODY_PHASE_ID': 'SORT4-ACTUAL-SELECT-2026-10-23-R21'},
        )
        for overrides in invalid_envs:
            env = {'SORT4_R24_SESSION_PHASE_ID': PHASE, **overrides}
            with self.subTest(overrides=overrides):
                result = self.run_gate(env_extra=env)
                self.assertEqual(result.returncode, 2)

    def test_audit_prefix_routes_only_to_w4_and_passes_closed_audit_identity(self):
        calls = self.root / 'python-call.bin'
        script = ('set -u\n'
                  f'proof_root={self.proof}\ncloud_dir={self.cloud}\nev=/synthetic/evidence\n'
                  'evidence_root=/synthetic/evidence-root\n'
                  'r24_w4_capture_only=1\nr24_w4_helper="$cloud_dir/select-callee-r24-w4-capture.py"\n'
                  'r24_w4_mode_file="$proof_root/research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-MODE.json"\n'
                  'current_sha=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\ndeadline=9999999999\n'
                  'compiler_sysroot=/synthetic/sysroot\n'
                  f'python3() {{ printf "%s\\0" "$@" > {calls}; return "${{TEST_AUDIT_EXIT:-0}}"; }}\n'
                  + audit_function() + '\n'
                  'if audit_result 7 r24-w4-capture; then exit 0; else exit "$?"; fi\n')
        env = self.env()
        env.pop('source_home', None)
        env.pop('schema', None)
        result = subprocess.run(['bash', '-c', script], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        args = calls.read_bytes().split(b'\0')[:-1]
        self.assertEqual(args[0], str(self.helper).encode())
        self.assertEqual(args[1], b'audit')
        for flag in (b'--repo', b'--cloud-dir', b'--evidence', b'--tool-home',
                     b'--schema', b'--compiler-sysroot', b'--deadline-epoch',
                     b'--candidate', b'--mode-file', b'--output',
                     b'--runner-exit', b'--failed-stage'):
            self.assertIn(flag, args)
        values = {args[i]: args[i + 1] for i in range(len(args) - 1) if args[i].startswith(b'--')}
        self.assertEqual(values[b'--tool-home'], b'/workspace/missing-native-tool')
        self.assertEqual(values[b'--schema'], b'/workspace/missing-schema')
        self.assertTrue(values[b'--compiler-sysroot'], 'audit must receive a nonempty sysroot argument')
        self.assertEqual(values[b'--candidate'], b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        self.assertEqual(values[b'--mode-file'], str(self.mode).encode())
        self.assertEqual(values[b'--runner-exit'], b'7')
        self.assertEqual(values[b'--failed-stage'], b'r24-w4-capture')
        self.assertEqual(args.count(str(self.cloud / 'select-callee-r24-mut-classified-proof.py').encode()), 0)
        self.assertEqual(args.count(str(self.cloud / 'select-callee-r24-p2-entailment.py').encode()), 0)

    def branch_harness(self, stage_exit=0, audit_exit=0):
        stage_calls = self.root / 'stage-call.bin'
        audit_calls = self.root / 'branch-audit-call.bin'
        script = ('set -euo pipefail\n'
                  f'r24_w4_helper={self.helper}\n'
                  'proof_root=/synthetic/proof\ncloud_dir=/synthetic/cloud\nev=/synthetic/evidence\n'
                  'source_home=/synthetic/tools\nschema=/synthetic/VfMir.capnp\n'
                  'compiler_sysroot=/synthetic/sysroot\ndeadline=9999999999\n'
                  'current_sha=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n'
                  'r24_w4_capture_only=1\n'
                  f'r24_w4_mode_file={self.mode}\n'
                  f'stage() {{ printf "%s\\0" "$@" > {stage_calls}; return {stage_exit}; }}\n'
                  f'audit_result() {{ printf "%s\\0" "$@" > {audit_calls}; return {audit_exit}; }}\n'
                  + w4_capture_branch() + '\n'
                  'printf "MUT_FALLTHROUGH\\n"\n')
        result = subprocess.run(['bash', '-c', script], env=self.env(), capture_output=True, text=True)
        return result, stage_calls, audit_calls

    def test_capture_branch_runs_stage_then_audit_and_exits_before_const_route(self):
        result, stage_file, audit_file = self.branch_harness()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('MUT_FALLTHROUGH', result.stdout)
        stage_args = stage_file.read_bytes().split(b'\0')[:-1]
        self.assertEqual(stage_args[:4], [b'r24-w4-capture', b'python3', str(self.helper).encode(), b'run'])
        for flag in (b'--repo', b'--cloud-dir', b'--evidence', b'--tool-home', b'--schema',
                     b'--compiler-sysroot', b'--deadline-epoch', b'--candidate', b'--mode-file'):
            self.assertIn(flag, stage_args)
        audit_args = audit_file.read_bytes().split(b'\0')[:-1]
        self.assertEqual(audit_args, [b'0', b'complete'])

    def test_capture_stage_error_and_timeout_preserve_exit_without_audit_or_fallthrough(self):
        for code in (1, 124):
            with self.subTest(code=code):
                result, _stage_file, audit_file = self.branch_harness(stage_exit=code)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertNotIn('MUT_FALLTHROUGH', result.stdout)
                self.assertFalse(audit_file.exists())

    def test_capture_audit_failure_propagates_without_const_fallthrough(self):
        result, _stage_file, audit_file = self.branch_harness(audit_exit=7)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertNotIn('MUT_FALLTHROUGH', result.stdout)
        self.assertEqual(audit_file.read_bytes().split(b'\0')[:-1], [b'0', b'complete'])


if __name__ == '__main__':
    unittest.main()
