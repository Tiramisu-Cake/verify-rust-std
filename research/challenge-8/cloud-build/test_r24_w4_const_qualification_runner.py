"""Extracted Bash routing/exit tests; all command services are synthetic."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

CLOUD = Path(__file__).resolve().parent
REPO = CLOUD.parents[2]
RUNNER = CLOUD / 'run-o26-select-callee-r20.sh'
MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONST-QUALIFICATION-MODE.json')
INPUTS_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-INPUTS-QUALIFICATION.json')
HELPER = CLOUD / 'select-callee-r24-w4-const-qualification.py'

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def gate():
    s = RUNNER.read_text()
    return s[s.index('# Current-tool const matrix'):s.index('positive_ast_args=()')]

def audit():
    s = RUNNER.read_text()
    a = s.index('audit_result() {')
    b = s.index('  if (( ${r24_w4_linkage_diagnostic:-0}', a)
    return s[a:b] + '}\n'

def branch():
    s = RUNNER.read_text()
    a = s.index('  if (( ${r24_w4_const_qualification:-0} == 1 )); then',
                s.index('stage r24-w4-native-console-build'))
    b = s.index('  stage r24-w4-linkage-diagnostic', a)
    return s[a:b]

class ConstRoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.proof = self.root / 'proof'
        self.cloud = self.root / 'infra/cloud-build'
        self.cloud.mkdir(parents=True)
        self.mode = self.proof / MODE_REL
        self.inputs = self.proof / INPUTS_REL
        self.helper = self.cloud / HELPER.name
        self.consequence = self.cloud / 'select-callee-r24-w4-const-consequence.py'
        for p in (self.mode, self.inputs, self.helper, self.consequence):
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(('synthetic ' + p.name).encode())
        self.ev = self.root / 'evidence/allprooflogs'
        self.ev.mkdir(parents=True)
        self.report = self.ev / 'cases/r24-w4-const-qualification/W4-CONST-QUALIFICATION-AUDIT.json'
        self.mirror = self.ev.parent / 'proof-audit.json'
        self.calls = self.root / 'args.json'
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('SORT4_')}

    def tearDown(self):
        self.tmp.cleanup()

    def setup(self):
        return ('set -euo pipefail\n'
                f'proof_root={self.proof}\ncloud_dir={self.cloud}\n'
                f'ev={self.ev}\nevidence_root={self.ev.parent}\n'
                f'r24_w4_const_helper={self.helper}\n'
                f'r24_w4_const_mode_file={self.mode}\n'
                'r24_w4_mode_file=/synthetic/capture-mode.json\n'
                'source_home=/synthetic/frozen-tool\nw4_native_home=/synthetic/native-tool\n'
                'compiler_sysroot=/synthetic/sysroot\ndeadline=9999999999\n'
                'current_sha=0123456789abcdef0123456789abcdef01234567\n')

    def shell(self, code):
        return subprocess.run(['bash', '-c', code], env=self.env, capture_output=True, text=True)

    def bound_gate(self):
        s = gate()
        pins = {'$r24_w4_const_mode_file': self.mode,
                '$r24_w4_const_helper': self.helper,
                '$cloud_dir/select-callee-r24-w4-const-consequence.py': self.consequence,
                '$proof_root/' + INPUTS_REL.as_posix(): self.inputs}
        result = []
        for line in s.splitlines():
            for variable, path in pins.items():
                if f'sha256sum "{variable}"' in line:
                    left, _, right = line.partition('==')
                    line = left + '== ' + digest(path.read_bytes()) + ' ' + right[right.index(']]'):]
            result.append(line)
        return '\n'.join(result)

    def test_closed_gate_absent_mode_prerequisite_and_dependency_drift(self):
        bound = self.bound_gate()
        good = self.shell(self.setup() + 'r24_w4_linkage_diagnostic=1\n' + bound + '\necho "$r24_w4_const_qualification"')
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(good.stdout.strip(), '1')
        bad_parent = self.shell(self.setup() + 'r24_w4_linkage_diagnostic=0\n' + bound)
        self.assertEqual(bad_parent.returncode, 2)
        for p in (self.helper, self.consequence, self.inputs):
            before = p.read_bytes()
            p.write_bytes(before + b' changed')
            result = self.shell(self.setup() + 'r24_w4_linkage_diagnostic=1\n' + bound)
            self.assertEqual(result.returncode, 2)
            p.write_bytes(before)
        self.mode.unlink()
        off = self.shell(self.setup() + 'r24_w4_linkage_diagnostic=0\n' + bound + '\necho "$r24_w4_const_qualification"')
        self.assertEqual(off.returncode, 0, off.stderr)
        self.assertEqual(off.stdout.strip(), '0')

    def audit_harness(self, helper_exit=0, kind='valid'):
        writer = self.root / 'fake-helper.py'
        writer.write_text('''import json,pathlib,sys
args=sys.argv[1:]
path=pathlib.Path(args[args.index('--output')+1]); path.parent.mkdir(parents=True,exist_ok=True)
json.dump(args,open(sys.argv[0]+'.args','w'))
kind=''' + repr(kind) + '''
if kind!='missing':
 d={'schema':'select-r24-w4-const-qualification-v1-audit','evidence_complete':''' + repr(helper_exit == 0) + ''','runner_exit':int(args[args.index('--runner-exit')+1]),'failed_stage':args[args.index('--failed-stage')+1],'accepted':False,'publication_allowed':False,'proof_credit':0,'errors':[]}
 if kind=='wrong-context': d['runner_exit']=0
 if kind=='wrong-credit': d['proof_credit']=False
 path.write_text(json.dumps(d))
 if kind=='symlink':
  other=path.with_suffix('.outside');other.write_bytes(path.read_bytes());path.unlink();path.symlink_to(other)
sys.exit(''' + str(helper_exit) + ''')
''')
        code = self.setup() + 'r24_w4_const_qualification=1\n'
        code += f'''python3() {{ if [[ "$1" == "$r24_w4_const_helper" ]]; then shift; {sys.executable} {writer} "$@"; else {sys.executable} "$@"; fi; }}
'''
        result = self.shell(code + audit() + '\naudit_result 9 native-source-stage\n')
        args = json.loads(Path(str(writer) + '.args').read_text())
        return result, args

    def test_audit_is_contained_and_mirrors_with_original_context(self):
        result, args = self.audit_harness()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(args[args.index('--output') + 1]), self.report)
        self.assertTrue(self.report.is_relative_to(self.ev))
        self.assertEqual(self.mirror.read_bytes(), self.report.read_bytes())
        d = json.loads(self.mirror.read_text())
        self.assertEqual((d['runner_exit'], d['failed_stage']), (9, 'native-source-stage'))
        self.assertEqual(args[args.index('--schema') + 1], '/synthetic/native-tool/src/rust_frontend/vf_mir/vf_mir.capnp')

    def test_partial_audit_still_mirrors_and_preserves_helper_failure(self):
        result, _ = self.audit_harness(helper_exit=7)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertEqual(self.mirror.read_bytes(), self.report.read_bytes())
        self.assertIs(json.loads(self.mirror.read_text())['evidence_complete'], False)

    def test_missing_unsafe_or_wrong_context_audits_refuse(self):
        for kind in ('missing', 'symlink', 'wrong-context', 'wrong-credit'):
            with self.subTest(kind=kind):
                self.report.unlink(missing_ok=True)
                self.mirror.unlink(missing_ok=True)
                result, _ = self.audit_harness(kind=kind)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(self.mirror.exists())

    def test_branch_uses_new_qualification_before_old_diagnostic(self):
        argsfile = self.root / 'stage.args'
        code = self.setup() + 'r24_w4_const_qualification=1\n'
        code += f'''stage() {{ printf '%s\\0' "$@" > {argsfile}; }}
audit_result() {{ [[ "$1" == 0 && "$2" == complete ]]; }}
'''
        result = self.shell(code + branch())
        self.assertEqual(result.returncode, 0, result.stderr)
        args = argsfile.read_bytes().split(b'\0')[:-1]
        self.assertEqual(args[:4], [b'r24-w4-const-qualification', b'python3', str(self.helper).encode(), b'run'])
        self.assertIn(b'--native-tool-home', args)
        self.assertNotIn(b'r24-w4-linkage-diagnostic', args)

    def test_original_stage_failure_is_not_replaced_by_later_success(self):
        code = self.setup() + 'r24_w4_const_qualification=1\nstage() { return 4; }\naudit_result() { exit 99; }\n'
        result = self.shell(code + branch())
        self.assertEqual(result.returncode, 4, result.stderr)

    def test_w4_transport_keeps_active_route_and_omits_only_mutable_executables(self):
        recipe = json.loads((CLOUD / 'recipes/o26-select-callee-r20.json').read_text())
        selected = set(recipe['proof_paths']) | set(recipe['infra_paths'])
        self.assertIn(MODE_REL.as_posix(), selected)
        self.assertIn(HELPER.relative_to(REPO).as_posix(), selected)
        self.assertIn('research/challenge-8/task-history/select-callee-r24/P2-MUT-QUALIFIED-PROFILE.json', selected)
        design = json.loads((REPO / 'research/challenge-8/task-history/select-callee-r24/W4-CHECKED-CALLER-ADMISSION-DESIGN.json').read_text())
        omitted = design['runtime_transport_closure']['omitted_mutable_only_helpers']
        self.assertEqual(len(omitted), 10)
        reached = [CLOUD / name for name in (
            'select-callee-r24-w4-const-qualification.py',
            'select-callee-r24-w4-const-consequence.py',
            'select-callee-r24-w4-contract-inputs.py',
            'select-callee-r24-w4-control-capture.py',
            'select-callee-r24-w4-linkage-diagnostic.py',
            'select-callee-r24-w4-capture.py',
            'select-callee-r24-w4-mir-calls.py',
            'select-callee-r21-fractional-proof-entry.py',
            'select-callee-r21-fractional-proof.py',
            'select-callee-r21-fractional.py',
            'select-callee-r21-proof-audit.py',
        )]
        for rel in omitted:
            self.assertNotIn(rel, selected)
            for path in reached:
                self.assertNotIn(Path(rel).name, path.read_text(), (rel, path))
        # A reached success branch exits before any omitted mutable stage.
        result = self.shell(self.setup() +
            'r24_w4_const_qualification=1\nstage() { return 0; }\n'
            'audit_result() { return 0; }\n' + branch() + '\nexit 99\n')
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
