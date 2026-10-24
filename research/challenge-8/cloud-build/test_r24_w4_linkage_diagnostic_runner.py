"""Isolated Bash boundary tests for the W4 linkage diagnostic route.

The tests run extracted gate, audit, and branch fragments from the production
shell runner. Python and stage calls are local fakes; the Cloud runner and
toolchain are never invoked.
"""
from __future__ import annotations

import hashlib
import contextlib
import importlib.util
import io
import json
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
LINK_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-LINKAGE-DIAGNOSTIC-MODE.json')
CAPTURE_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-MODE.json')
INTERFACE_REL = Path('research/challenge-8/task-history/select-callee-r23/P2-INTERFACE.json')
QUALIFICATION_REL = Path('research/challenge-8/task-history/select-callee-r24/CONST-CALLEE-QUALIFICATION.json')
PINS_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-PINS.json')
NATIVE_PATCH_REL = Path('research/challenge-8/cloud-build/sort4-caller-entry-native/w4-native-fingerprint-r24.patch')
HELPER = 'select-callee-r24-w4-linkage-diagnostic.py'
ANALYZER = 'select-callee-r24-w4-mir-calls.py'
CAPTURE_HELPER = 'select-callee-r24-w4-capture.py'
DIAGNOSTIC_SCRIPT = CLOUD / HELPER
DIAGNOSTIC_SPEC = importlib.util.spec_from_file_location('w4_cli_parser_under_test', DIAGNOSTIC_SCRIPT)
DIAGNOSTIC = importlib.util.module_from_spec(DIAGNOSTIC_SPEC)
assert DIAGNOSTIC_SPEC.loader is not None
DIAGNOSTIC_SPEC.loader.exec_module(DIAGNOSTIC)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def shell_source() -> str:
    return RUNNER.read_text(encoding='utf-8')


def gate_block() -> str:
    source = shell_source()
    start = source.index('# This separate W4 step captures the unchanged body;')
    end = source.index('positive_ast_args=()', start)
    return source[start:end]


def linkage_branch() -> str:
    source = shell_source()
    start = source.index('if (( r24_w4_linkage_diagnostic == 1 )); then',
                         source.index('ldd "$source_home/bin/verifast"'))
    end = source.index('\nif (( r24_w4_capture_only == 1 )); then', start)
    return source[start:end]


def audit_function() -> str:
    source = shell_source()
    start = source.index('audit_result() {')
    end = source.index('\n  if (( ${r24_w4_capture_only:-0} == 1 )); then', start)
    return source[start:end] + '\n}'


class W4LinkageShellBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.proof = self.root / 'proof'
        self.cloud = self.root / 'cloud'
        self.proof.mkdir()
        self.cloud.mkdir()
        self.capture_mode = self.proof / CAPTURE_MODE_REL
        self.link_mode = self.proof / LINK_MODE_REL
        self.interface = self.proof / INTERFACE_REL
        self.qualification = self.proof / QUALIFICATION_REL
        self.pins = self.proof / PINS_REL
        self.native_patch = self.proof / NATIVE_PATCH_REL
        for path in (self.capture_mode, self.link_mode, self.interface,
                     self.qualification, self.pins, self.native_patch):
            path.parent.mkdir(parents=True, exist_ok=True)
        self.capture_helper = self.cloud / CAPTURE_HELPER
        self.helper = self.cloud / HELPER
        self.analyzer = self.cloud / ANALYZER
        for source, target in (
            (REPO / CAPTURE_MODE_REL, self.capture_mode),
            (REPO / LINK_MODE_REL, self.link_mode),
            (REPO / INTERFACE_REL, self.interface),
            (REPO / QUALIFICATION_REL, self.qualification),
            (REPO / PINS_REL, self.pins),
            (CLOUD / 'sort4-caller-entry-native/w4-native-fingerprint-r24.patch', self.native_patch),
            (CLOUD / CAPTURE_HELPER, self.capture_helper),
            (CLOUD / HELPER, self.helper),
            (CLOUD / ANALYZER, self.analyzer),
        ):
            shutil.copyfile(source, target)
        self.hashes = {key: sha(path.read_bytes()) for key, path in {
            'r24_w4_mode_file': self.capture_mode,
            'r24_w4_helper': self.capture_helper,
            'r24_w4_linkage_mode_file': self.link_mode,
            'r24_w4_linkage_helper': self.helper,
            'r24_w4_linkage_analyzer': self.analyzer,
            'r24_w4_capture_pins': self.pins,
        }.items()}

    def tearDown(self):
        self.temp.cleanup()

    def env(self, **overrides):
        env = {key: value for key, value in os.environ.items()
               if not key.startswith('SORT4_') and key not in ('CLOUD_BUILD_ID', 'PROOF_SHA', 'LANE')}
        env.update({'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
                    'r24_mut_proof_enabled': '1',
                    'SORT4_R24_SESSION_PHASE_ID': PHASE,
                    'proof_root': str(self.proof), 'cloud_dir': str(self.cloud)})
        env.update(overrides)
        return env

    def bound_gate(self):
        text = gate_block()
        substitutions = {
            '$r24_w4_mode_file': self.hashes['r24_w4_mode_file'],
            '$r24_w4_helper': self.hashes['r24_w4_helper'],
            '$r24_w4_linkage_mode_file': self.hashes['r24_w4_linkage_mode_file'],
            '$r24_w4_linkage_helper': self.hashes['r24_w4_linkage_helper'],
            '$cloud_dir/select-callee-r24-w4-mir-calls.py': self.hashes['r24_w4_linkage_analyzer'],
            '$proof_root/research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-PINS.json':
                self.hashes['r24_w4_capture_pins'],
        }
        lines = []
        for line in text.splitlines():
            for needle, digest in substitutions.items():
                if f'sha256sum "{needle}"' in line:
                    before, marker, after = line.partition('==')
                    self.assertTrue(marker, f'hash guard absent for {needle}')
                    suffix = after[after.index(']]'):]
                    line = before + '== ' + digest + ' ' + suffix
            lines.append(line)
        return '\n'.join(lines)

    def run_gate(self, *, absent_linkage_mode=False, absent_capture_mode=False,
                 changed=None, env_extra=None):
        if absent_linkage_mode:
            self.link_mode.unlink(missing_ok=True)
        if absent_capture_mode:
            self.capture_mode.unlink(missing_ok=True)
        changed_paths = {
            'mode': self.link_mode, 'helper': self.helper, 'analyzer': self.analyzer,
            'pins': self.pins, 'capture-mode': self.capture_mode,
            'capture-helper': self.capture_helper,
        }
        if changed:
            changed_paths[changed].write_bytes(changed_paths[changed].read_bytes() + b'changed')
        setup = ('set -euo pipefail\n'
                 f'proof_root={self.proof}\ncloud_dir={self.cloud}\n'
                 'r24_mut_proof_enabled="${TEST_MUT_ENABLED:-1}"\n')
        script = setup + self.bound_gate() + '\nprintf "%s %s\\n" "$r24_w4_capture_only" "$r24_w4_linkage_diagnostic"\n'
        return subprocess.run(['bash', '-c', script], env=self.env(**(env_extra or {})),
                              capture_output=True, text=True)

    def test_new_mode_absent_retains_capture_only_default_and_no_diagnostic_branch(self):
        result = self.run_gate(absent_linkage_mode=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '1 0')
        old_default = self.run_gate(absent_capture_mode=True, absent_linkage_mode=True)
        self.assertEqual(old_default.returncode, 2 if self.capture_mode.is_file() else 0)

    def test_exact_closed_dependencies_enable_linkage_and_mutated_or_missing_pin_refuses(self):
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '1 1')
        for changed in ('mode', 'helper', 'analyzer', 'pins'):
            with self.subTest(changed=changed):
                target = {'mode': self.link_mode, 'helper': self.helper,
                          'analyzer': self.analyzer, 'pins': self.pins}[changed]
                source = {'mode': REPO / LINK_MODE_REL, 'helper': CLOUD / HELPER,
                          'analyzer': CLOUD / ANALYZER, 'pins': REPO / PINS_REL}[changed]
                shutil.copyfile(source, target)
                bad = self.run_gate(changed=changed)
                self.assertEqual(bad.returncode, 2)
                shutil.copyfile(source, target)
        # A missing mode disables this opt-in. Missing dependencies with an
        # exact mode present are refusal conditions.
        result_without_mode = self.run_gate(absent_linkage_mode=True)
        self.assertEqual(result_without_mode.returncode, 0)
        self.assertEqual(result_without_mode.stdout.strip(), '1 0')
        for target in (self.helper, self.analyzer, self.pins):
            with self.subTest(missing=target.name):
                shutil.copyfile(REPO / LINK_MODE_REL, self.link_mode)
                target.unlink()
                bad = self.run_gate()
                self.assertEqual(bad.returncode, 2)
                # Restore exact test fixture before testing the next path.
                source = {self.link_mode: REPO / LINK_MODE_REL,
                          self.helper: CLOUD / HELPER,
                          self.analyzer: CLOUD / ANALYZER,
                          self.pins: REPO / PINS_REL}[target]
                shutil.copyfile(source, target)

    def test_linkage_mode_requires_capture_prerequisite_and_exact_route(self):
        for env_extra in ({'TEST_MUT_ENABLED': '0'},
                          {'SORT4_R24_SESSION_PHASE_ID': 'wrong'},
                          {'SORT4_R24_SESSION_PHASE_ID': ''},
                          {'SORT4_R21_BODY_PHASE_ID': ROUTE}):
            with self.subTest(env=env_extra):
                result = self.run_gate(env_extra=env_extra)
                self.assertEqual(result.returncode, 2)
        missing_capture = self.run_gate(absent_capture_mode=True)
        self.assertEqual(missing_capture.returncode, 2)

    def audit_harness(self, audit_exit=0, missing_tools=False, report_state='valid'):
        calls = self.root / 'audit-call.bin'
        marker = self.root / 'proof-audit.json'
        ev = self.root / 'allprooflogs'
        ev.mkdir(parents=True, exist_ok=True)
        tool_setup = ('' if missing_tools else
                      'source_home=/synthetic/tool-home\nw4_native_home=/synthetic/native-tool-home\nschema=/synthetic/schema\n'
                      'compiler_sysroot=/synthetic/sysroot\n')
        script = ('set -u\n'
                  f'proof_root={self.proof}\ncloud_dir={self.cloud}\nev={self.root / "allprooflogs"}\n'
                  f'evidence_root={self.root}\n'
                  + tool_setup +
                  'deadline=9999999999\ncurrent_sha=0123456789abcdef0123456789abcdef01234567\n'
                  'r24_w4_linkage_diagnostic=1\nr24_w4_capture_only=1\n'
                  f'r24_w4_helper={self.capture_helper}\nr24_w4_mode_file={self.capture_mode}\n'
                  f'r24_w4_linkage_helper={self.helper}\nr24_w4_linkage_mode_file={self.link_mode}\n'
                  f'python3() {{ if [[ "$1" == -c ]]; then command python3 "$@"; return $?; fi; '
                  f'printf "%s\\0" "$@" > {calls}; local out= runner= stage=; '
                  'while (($#)); do case "$1" in --output) out="$2"; shift 2;; '
                  '--runner-exit) runner="$2"; shift 2;; --failed-stage) stage="$2"; shift 2;; *) shift;; esac; done; '
                  + ('if [[ "' + report_state + '" == missing ]]; then return ' + str(audit_exit) + '; fi; '
                     'mkdir -p "$(dirname "$out")"; '
                     'if [[ "' + report_state + '" == unsafe ]]; then ln -s /dev/null "$out"; '
                     'else printf \'{"schema":"select-r24-w4-linkage-diagnostic-v1-audit","evidence_complete":false,"runner_exit":%s,"failed_stage":"%s","accepted":false,"publication_allowed":false,"proof_credit":0}\\n\' "$runner" "$stage" > "$out"; fi; '
                     'return ' + str(audit_exit) + '; }\n')
                  + audit_function() + '\n'
                  'audit_result 9 setup-failure\n')
        return subprocess.run(['bash', '-c', script], env=self.env(), capture_output=True, text=True), calls

    def test_audit_prefix_uses_linkage_audit_and_preserves_original_runner_context(self):
        result, calls = self.audit_harness(audit_exit=7)
        self.assertEqual(result.returncode, 7)
        args = calls.read_bytes().split(b'\0')[:-1]
        self.assertEqual(args[:2], [str(self.helper).encode(), b'audit'])
        values = {args[i]: args[i + 1] for i in range(len(args) - 1) if args[i].startswith(b'--')}
        for flag in (b'--repo', b'--cloud-dir', b'--evidence', b'--tool-home', b'--schema',
                     b'--compiler-sysroot', b'--deadline-epoch', b'--candidate',
                     b'--capture-mode-file', b'--mode-file', b'--output',
                     b'--runner-exit', b'--failed-stage'):
            self.assertIn(flag, args)
        self.assertEqual(values[b'--compiler-sysroot'], b'/synthetic/sysroot')
        self.assertTrue(values[b'--candidate'])
        self.assertEqual(values[b'--capture-mode-file'], str(self.capture_mode).encode())
        self.assertEqual(values[b'--mode-file'], str(self.link_mode).encode())
        self.assertEqual(values[b'--runner-exit'], b'9')
        self.assertEqual(values[b'--failed-stage'], b'setup-failure')
        self.assertEqual(values[b'--output'],
                         str(self.root / 'allprooflogs/cases/r24-w4-linkage-diagnostic/W4-LINKAGE-DIAGNOSTIC-AUDIT.json').encode())
        self.assertEqual(json.loads((self.root / 'proof-audit.json').read_text())['runner_exit'], 9)
        parsed_audit = DIAGNOSTIC.parser().parse_args([arg.decode() for arg in args[1:]])
        self.assertEqual(parsed_audit.command, 'audit')
        self.assertEqual(parsed_audit.deadline_epoch, 9999999999)
        self.assertEqual(parsed_audit.runner_exit, 9)
        self.assertEqual(parsed_audit.failed_stage, 'setup-failure')
        self.assertEqual(args.count(str(self.capture_helper).encode()), 0)
        self.assertNotIn(b'select-callee-r24-mut-classified-proof.py', b'\0'.join(args))
        self.assertNotIn(b'select-callee-r24-p2-entailment.py', b'\0'.join(args))
        self.temp.cleanup()
        self.setUp()
        result, calls = self.audit_harness(missing_tools=True)
        self.assertEqual(result.returncode, 0)
        args = calls.read_bytes().split(b'\0')[:-1]
        values = {args[i]: args[i + 1] for i in range(len(args) - 1) if args[i].startswith(b'--')}
        self.assertEqual(values[b'--tool-home'], b'/workspace/missing-native-tool')
        self.assertEqual(values[b'--native-tool-home'], b'/workspace/missing-w4-fingerprint-tool')
        self.assertEqual(values[b'--schema'], b'/workspace/missing-schema')
        self.assertEqual(values[b'--compiler-sysroot'], b'/workspace/missing-sysroot')

    def test_audit_mirrors_partial_helper_report_and_preserves_helper_exit(self):
        result, calls = self.audit_harness(audit_exit=4)
        self.assertEqual(result.returncode, 4)
        args = calls.read_bytes().split(b'\0')[:-1]
        values = {args[i]: args[i + 1] for i in range(len(args) - 1) if args[i].startswith(b'--')}
        report = Path(values[b'--output'].decode())
        mirror = self.root / 'proof-audit.json'
        self.assertTrue(report.is_file())
        self.assertTrue(mirror.is_file())
        self.assertEqual(report.read_bytes(), mirror.read_bytes())
        self.assertEqual(json.loads(mirror.read_text())['failed_stage'], 'setup-failure')

    def test_missing_or_unsafe_helper_audit_report_refuses_mirror(self):
        for state in ('missing', 'unsafe'):
            with self.subTest(state=state):
                self.temp.cleanup()
                self.setUp()
                result, _calls = self.audit_harness(audit_exit=4, report_state=state)
                self.assertEqual(result.returncode, 4)
                self.assertFalse((self.root / 'proof-audit.json').exists())

    def test_run_cli_still_requires_deadline_and_unknown_arguments_remain_rejected(self):
        run_args = ['run', '--repo', '/synthetic/proof', '--cloud-dir', '/synthetic/cloud',
                    '--evidence', '/synthetic/evidence', '--tool-home', '/synthetic/tool-home',
                    '--native-tool-home', '/synthetic/native-tool-home',
                    '--schema', '/synthetic/schema', '--compiler-sysroot', '/synthetic/sysroot',
                    '--capture-mode-file', '/synthetic/proof/W4-CAPTURE-MODE.json',
                    '--mode-file', '/synthetic/proof/W4-LINKAGE-DIAGNOSTIC-MODE.json',
                    '--candidate', '0123456789abcdef0123456789abcdef01234567',
                    '--deadline-epoch', '9999999999']
        parsed_run = DIAGNOSTIC.parser().parse_args(run_args)
        self.assertEqual(parsed_run.command, 'run')
        self.assertEqual(parsed_run.deadline_epoch, 9999999999)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                DIAGNOSTIC.parser().parse_args(run_args + ['--unrecognized-diagnostic-flag'])

    def branch_harness(self, stage_exit=0, audit_exit=0):
        stage_calls = self.root / 'linkage-stage-call.bin'
        audit_calls = self.root / 'linkage-branch-audit.bin'
        python_calls = self.root / 'linkage-python-call.bin'
        marker = self.root / 'proof-audit.json'
        branch = linkage_branch()
        script = ('set -euo pipefail\n'
                  f'r24_w4_linkage_helper={self.helper}\nr24_w4_mode_file={self.capture_mode}\n'
                  f'r24_w4_linkage_mode_file={self.link_mode}\n'
                  f'proof_root={self.proof}\ncloud_dir={self.cloud}\nev={self.root / "allprooflogs"}\n'
                  f'evidence_root={self.root}\n'
                  f'work_root={self.root / "work"}\nsource_home={self.root / "source-tool"}\n'
                  'schema=/synthetic/schema\n'
                  'compiler_sysroot=/synthetic/sysroot\ndeadline=9999999999\n'
                  'mkdir -p "$source_home/src/rust_frontend/vf_mir_translator"\n'
                  'printf synthetic > "$source_home/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml"\n'
                  'current_sha=0123456789abcdef0123456789abcdef01234567\n'
                  'r24_w4_linkage_diagnostic=1\nr24_w4_capture_only=1\n'
                  'current_stage=provider\n'
                  f'stage() {{ current_stage="$1"; printf "%s\\0" "$@" >> {stage_calls}; '
                  'if [[ "$1" == r24-w4-native-copy ]]; then mkdir -p "$w4_native_home"; fi; '
                  'if [[ "$1" == r24-w4-linkage-diagnostic ]]; then return ' + str(stage_exit) + '; fi; return 0; }\n'
                  'sha256sum() { local path="${@: -1}"; '
                  'if [[ "$path" == "$w4_native_patch" ]]; then '
                  'printf "e720c48a5daf9e402ceb0dfddb0b5fcbc9405bedd0f9cf7eff061e5a672dcd90  %s\\n" "$path"; '
                  'elif [[ "$path" == *vf_mir_translator.ml ]]; then '
                  'if [[ "$path" == *r24-w4-native-fingerprint-tool* ]]; then '
                  'printf "5170c56386f092d55a42251594eb4b080073f58828cbe1dcf44053b5bdc99942  %s\\n" "$path"; '
                  'else printf "8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007  %s\\n" "$path"; fi; '
                  'else command sha256sum "$@"; fi; }\n'
                  f'python3() {{ if [[ "$1" == -c ]]; then command python3 "$@"; return $?; fi; '
                  f'printf "%s\\0" "$@" > {python_calls}; local out= runner= failed=; '
                  'while (($#)); do case "$1" in --output) out="$2"; shift 2;; '
                  '--runner-exit) runner="$2"; shift 2;; --failed-stage) failed="$2"; shift 2;; *) shift;; esac; done; '
                  'mkdir -p "$(dirname "$out")"; '
                  'printf \'{"schema":"select-r24-w4-linkage-diagnostic-v1-audit","evidence_complete":false,"runner_exit":%s,"failed_stage":"%s","accepted":false,"publication_allowed":false,"proof_credit":0}\\n\' "$runner" "$failed" > "$out"; '
                  f'return {audit_exit}; }}\n'
                  + audit_function() + '\n'
                  f"trap 'status=$?; if [[ ! -f {marker} ]]; then audit_result \"$status\" \"$current_stage\" || true; fi' EXIT\n"
                  + branch + '\nprintf "LINKAGE_FALLTHROUGH\\n"\n')
        result = subprocess.run(['bash', '-c', script], env=self.env(), capture_output=True, text=True)
        return result, stage_calls, audit_calls, python_calls

    def test_new_branch_stages_linkage_then_audits_and_exits_before_old_capture(self):
        result, stage_calls, audit_calls, python_calls = self.branch_harness()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('LINKAGE_FALLTHROUGH', result.stdout)
        stage = stage_calls.read_bytes().split(b'\0')[:-1]
        self.assertEqual(stage[:2], [b'r24-w4-native-copy', b'cp'])
        self.assertIn(b'r24-w4-linkage-diagnostic', stage)
        self.assertIn(str(self.helper).encode(), stage)
        for flag in (b'--repo', b'--cloud-dir', b'--evidence', b'--tool-home', b'--schema',
                     b'--native-tool-home',
                     b'--compiler-sysroot', b'--deadline-epoch', b'--candidate',
                     b'--capture-mode-file', b'--mode-file'):
            self.assertIn(flag, stage)
        audit = python_calls.read_bytes().split(b'\0')[:-1]
        self.assertEqual(audit[:2], [str(self.helper).encode(), b'audit'])
        values = {audit[i]: audit[i + 1] for i in range(len(audit) - 1) if audit[i].startswith(b'--')}
        self.assertEqual(values[b'--compiler-sysroot'], b'/synthetic/sysroot')
        self.assertEqual(values[b'--native-tool-home'], str(self.root / 'work/r24-w4-native-fingerprint-tool').encode())
        self.assertEqual(values[b'--runner-exit'], b'0')
        self.assertEqual(values[b'--failed-stage'], b'complete')

    def test_stage_failure_or_timeout_audits_original_exit_without_fallback(self):
        for code in (1, 124):
            with self.subTest(exit=code):
                # Use independent output files to preserve the exact injected process result.
                self.temp.cleanup()
                self.setUp()
                result, stage_calls, audit_calls, python_calls = self.branch_harness(stage_exit=code)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertNotIn('LINKAGE_FALLTHROUGH', result.stdout)
                self.assertTrue(stage_calls.is_file())
                audit = python_calls.read_bytes().split(b'\0')[:-1]
                values = {audit[i]: audit[i + 1] for i in range(len(audit) - 1)
                          if audit[i].startswith(b'--')}
                self.assertEqual(values[b'--runner-exit'], str(code).encode())
                self.assertEqual(values[b'--failed-stage'], b'r24-w4-linkage-diagnostic')

    def test_linkage_audit_failure_propagates_without_old_capture_fallback(self):
        result, _stage_calls, _audit_calls, python_calls = self.branch_harness(audit_exit=7)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertNotIn('LINKAGE_FALLTHROUGH', result.stdout)
        audit = python_calls.read_bytes().split(b'\0')[:-1]
        values = {audit[i]: audit[i + 1] for i in range(len(audit) - 1)
                  if audit[i].startswith(b'--')}
        self.assertEqual(values[b'--runner-exit'], b'0')
        self.assertEqual(values[b'--failed-stage'], b'complete')


if __name__ == '__main__':
    unittest.main()
