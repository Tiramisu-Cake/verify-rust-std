"""Synthetic profile-gate checks: AST extraction, no full runner/backend import."""
import ast
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

HERE = Path(__file__).parent
PROFILE = 'A1-SCOPE-S2-PROFILE-2026-10-20.json'
PATH = Path('research/challenge-8/cloud-build/sort4-caller-entry-native')
TREE = ast.parse((HERE / 'a1-focus-backend.py').read_text())
FUNCTION = next(n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name == '_cloud_gate')
START = next(i for i, n in enumerate(FUNCTION.body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'profile_path' for t in n.targets))
GATE = compile(ast.Module(body=FUNCTION.body[START:START+2], type_ignores=[]), str(HERE / 'a1-focus-backend.py'), 'exec')


def need(ok, reason):
    if not ok:
        raise RuntimeError(reason)


class ProfileGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / PATH / PROFILE
        self.path.parent.mkdir(parents=True)
        self.profile = dict(phase_id='protocol-test', authorization_phase_id='authorization-test', profile_pin_source='coordinator-environment', proof_sha=None, infra_sha=None, cloud_build_enabled=True, profile_accepted=False)
        self.write(self.profile)

    def write(self, value):
        self.path.write_text(json.dumps(value))
        self.digest = hashlib.sha256(self.path.read_bytes()).hexdigest()

    def check(self, profile=None, digest=None, authorization_env='authorization-test'):
        ns = dict(Path=Path, a=SimpleNamespace(proof_root=self.root), HERE=PATH,
                  sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest(), json=json,
                  profile_hash=digest or self.digest, profile=self.profile if profile is None else profile,
                  PHASE='protocol-test', AUTHORIZATION_PHASE='authorization-test',
                  os=SimpleNamespace(environ={'SORT4_A1_AUTHORIZATION_PHASE_ID':authorization_env}), need=need)
        exec(GATE, ns)

    def test_exact_profile(self):
        self.check()

    def test_r5_old_path_only_is_not_accepted(self):
        self.path.rename(self.path.with_name('A1-PARSER-D2-PROFILE-2026-10-19.json'))
        with self.assertRaisesRegex(RuntimeError, 'published A1 profile identity'):
            self.check()

    def test_wrong_authorization_binding(self):
        changed = dict(self.profile, authorization_phase_id='stale-r5')
        with self.assertRaisesRegex(RuntimeError, 'published A1 profile identity'):
            self.check(profile=changed)
        with self.assertRaisesRegex(RuntimeError, 'published A1 profile identity'):
            self.check(authorization_env='stale-r5')

    def test_wrong_hash_and_changed_content(self):
        with self.assertRaisesRegex(RuntimeError, 'published A1 profile identity'):
            self.check(digest='0'*64)
        changed = dict(self.profile, profile_accepted=True)
        self.write(changed)
        with self.assertRaisesRegex(RuntimeError, 'published A1 profile identity'):
            self.check()

    def test_partial_null_missing_wrong_type(self):
        for key in self.profile:
            with self.subTest(key=key):
                changed = deepcopy(self.profile)
                del changed[key]
                # proof/infra absent are explicitly accepted by this existing gate;
                # other missing fields must fail unchanged.
                if key in ('proof_sha', 'infra_sha'):
                    continue
                self.write(changed)
                with self.assertRaisesRegex(RuntimeError, 'published A1 profile identity'):
                    self.check(profile=changed)
        for value in (None, [], 'not-a-profile'):
            with self.subTest(value=value):
                self.write(value)
                with self.assertRaises((RuntimeError, AttributeError)):
                    self.check()
        self.path.write_text('{')
        self.digest = hashlib.sha256(self.path.read_bytes()).hexdigest()
        with self.assertRaises(json.JSONDecodeError):
            self.check()

    def test_all_active_profile_consumers_and_recipe(self):
        for name in ('a1-entry.py', 'a1-runner.py', 'a1-focus-backend.py'):
            tree = ast.parse((HERE / name).read_text())
            constants = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and 'PROFILE-' in n.value]
            self.assertEqual(constants, [PROFILE], name)
        cloud = HERE.parent
        text = (cloud / 'control.py').read_text()
        self.assertIn("A1_SCOPE_PROFILE='" + str(PATH / PROFILE) + "'", text)
        recipe = json.loads((cloud / 'recipes/o26-sort4-c1-current-recovery.json').read_text())
        self.assertIn(str(PATH / PROFILE), recipe['proof_paths'])
        self.assertEqual(recipe['proof_paths'], sorted(recipe['proof_paths']))
        old_profile = HERE / 'A1-AUTO-S5-PROFILE-2026-10-20.json'
        self.assertTrue(old_profile.is_file())
        self.assertEqual(json.loads(old_profile.read_text())['authorization_phase_id'],
                         'SORT4-NATIVE-INTERFACE-AUTONOMOUS-2026-10-20-R5')
        active = json.loads((HERE / PROFILE).read_text())
        self.assertEqual(active['authorization_phase_id'],
                         'SORT4-PACKAGE-SCOPE-NATIVE-PROOF-2026-10-20-R6')
        self.assertEqual(active['experiment_protocol_phase_id'],
                         'SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17')
        self.assertEqual(active['r_patch_sha256'],
                         '9cdca995bc926efe3275319dec345f4d70a2fec7fdc95781decb4e4c2df7c9c8')
        self.assertEqual(active['c_patch_sha256'],
                         'e7cdc8a8504338ccaab760975c1a3f1a739211d7f8d531dd214babc2005d894e')
        self.assertEqual(active['execution_mode'], 'full-matrix')
        self.assertEqual(active['first_matrix_status'], 'NOT_RUN')
        self.assertFalse(active['profile_accepted'])
        self.assertFalse(active['proof_credit'])
        self.assertEqual(active['status'], 'PACKAGE_SCOPE_S2_UNRUN')


if __name__ == '__main__':
    unittest.main()
