#!/usr/bin/env python3
"""Synthetic route and terminal-audit tests; no toolchain or Cloud calls."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('body_route_r21', HERE / 'body-route-r21.py')
route = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(route)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class BodyRouteR21Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'proof'
        self.infra_root = Path(self.tmp.name) / 'infra'
        self.root.mkdir()
        self.infra_root.mkdir()
        self.env = {
            'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
            'SORT4_R21_BODY_PHASE_ID': route.EXECUTION_PHASE,
            'LANE': route.EXECUTION_LANE,
            'CLOUD_BUILD_ID': 'synthetic-build',
            'SORT4_A1_PHASE_ID': route.BACKEND_PHASE,
            'SORT4_A1_AUTHORIZATION_PHASE_ID': route.BACKEND_AUTHORIZATION,
            'SORT4_A1_CHECKED_TRAIT_CONTRACT': '1',
        }
        self.profile = {
            'execution_authority_phase_id': route.EXECUTION_PHASE,
            'execution_lane': route.EXECUTION_LANE,
            'phase': route.EXECUTION_PHASE,
            'authorization_phase_id': route.BACKEND_AUTHORIZATION,
            'experiment_protocol_phase_id': route.BACKEND_PHASE,
            'phase_id': route.BACKEND_PHASE,
            'execution_mode': 'actual-sort4-body-v1',
            'body_action': 'full-body-c1-recovery',
            'cloud_build_enabled': True,
            'accepted': False, 'admitted': False, 'proof_credit': False,
            'independent_credit': False, 'profile_accepted': False,
            'formal_verification_passed': False, 'admission_record_created': False,
        }
        rel = route.PROFILE
        for field, relpath in route.PROOF_SCALAR_FILE_PINS.items():
            self.pin(field, relpath, ('proof synthetic ' + field).encode())
        for field, relpath in route.INFRA_SCALAR_FILE_PINS.items():
            self.pin(field, relpath, ('infra synthetic ' + field).encode(),
                     root=self.infra_root)
        helpers = {}
        for name in ('a1-ast-gates.py', 'a1-fixtures.py', 'a1-tool-r21.py'):
            helpers[name] = self.write(route.HERE / name, ('helper ' + name).encode())
        self.profile['a1_helper_sha256'] = helpers
        self.profile['a1_tool_sha256'] = helpers['a1-tool-r21.py']
        for field in ('a1_checked_cleanup_helper_sha256',
                      'a1_checked_cleanup_import_sha256',
                      'reference_own_probe_sha256'):
            if field == 'reference_own_probe_sha256':
                self.pin(field, route.HERE / 'a1-reference-own-probe-r17.py', b'reference own probe')
            else:
                self.profile[field] = digest(field.encode())
        std = {}
        for name in sorted(route.STD_FILES):
            std[name] = self.write(Path(name), ('std ' + name).encode())
        self.profile['std_source_sha256'] = std
        deps = {}
        for name in ('a1-actual-body-c1.py', 'a1-actual-recover-pair.rs', 'capture.py'):
            relpath = route.BODY_DEPENDENCY_PATHS.get(name, route.HERE / name)
            deps[name] = self.write(relpath, ('fixture ' + name).encode())
        self.profile['actual_body_dependencies_sha256'] = deps
        self.profile['a1_focus_semantics_sha256'] = {'src/verify_expr.ml': digest(b'focus')}
        profile_path = self.root / route.PROFILE
        profile_path.parent.mkdir(parents=True, exist_ok=True)
        profile_path.write_text(json.dumps(self.profile, sort_keys=True))
        self.profile_sha = digest(profile_path.read_bytes())
        self.env['SORT4_A1_PROFILE_SHA256'] = self.profile_sha

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, relpath: Path, raw: bytes, root: Path | None = None) -> str:
        path = (root or self.root) / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return digest(raw)

    def pin(self, field: str, relpath: Path, raw: bytes,
            root: Path | None = None) -> None:
        self.profile[field] = self.write(relpath, raw, root)

    def rewrite_profile(self):
        path = self.root / route.PROFILE
        path.write_text(json.dumps(self.profile, sort_keys=True))
        self.profile_sha = digest(path.read_bytes())
        self.env['SORT4_A1_PROFILE_SHA256'] = self.profile_sha

    def test_profile_route_source_and_helper_pins(self):
        result = route.preflight(self.root, self.infra_root, self.profile_sha, self.env)
        self.assertEqual(result['classification'], 'R21_BODY_SOURCE_PREFLIGHT')
        self.assertFalse(result['proof_credit'])

    def test_profile_sha_mismatch_refused(self):
        with self.assertRaisesRegex(ValueError, 'profile file SHA256'):
            route.preflight(self.root, self.infra_root, digest(b'other'), self.env)

    def test_source_pin_mismatch_refused(self):
        (self.infra_root / route.INFRA_SCALAR_FILE_PINS['a1_entry_sha256']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'infra-pinned source differs'):
            route.preflight(self.root, self.infra_root, self.profile_sha, self.env)

    def test_missing_infra_is_not_satisfied_by_proof_tree_copy(self):
        relpath = route.INFRA_SCALAR_FILE_PINS['a1_entry_sha256']
        proof_copy = self.root / relpath
        proof_copy.parent.mkdir(parents=True, exist_ok=True)
        proof_copy.write_bytes(b'proof-tree copy of infra entry')
        empty_infra = self.root / 'empty-infra'
        empty_infra.mkdir()
        with self.assertRaisesRegex(ValueError, 'infra-pinned source differs: a1_entry_sha256'):
            route.preflight(self.root, empty_infra, self.profile_sha, self.env)

    def test_different_infra_tree_refused_even_when_proof_tree_has_matching_file(self):
        relpath = route.INFRA_SCALAR_FILE_PINS['a1_runner_sha256']
        proof_copy = self.root / relpath
        proof_copy.parent.mkdir(parents=True, exist_ok=True)
        proof_copy.write_bytes(b'infra synthetic a1_runner_sha256')
        different_infra = self.root / 'different-infra'
        different_infra.mkdir()
        entry_relpath = route.INFRA_SCALAR_FILE_PINS['a1_entry_sha256']
        entry_target = different_infra / entry_relpath
        entry_target.parent.mkdir(parents=True, exist_ok=True)
        entry_target.write_bytes((self.infra_root / entry_relpath).read_bytes())
        with self.assertRaisesRegex(ValueError, 'infra-pinned source differs: a1_runner_sha256'):
            route.preflight(self.root, different_infra, self.profile_sha, self.env)

    def test_proof_role_helper_tamper_refused(self):
        helper = self.root / route.HERE / 'a1-ast-gates.py'
        helper.write_bytes(b'tampered proof helper')
        with self.assertRaisesRegex(ValueError, 'required A1 helper differs: a1-ast-gates.py'):
            route.preflight(self.root, self.infra_root, self.profile_sha, self.env)

    def test_route_and_profile_mismatch_refused(self):
        self.env['LANE'] = 'o26-select-callee-r20'
        with self.assertRaisesRegex(ValueError, 'fresh Cloud execution route'):
            route.preflight(self.root, self.infra_root, self.profile_sha, self.env)

    def test_profile_route_identity_mismatch_refused(self):
        self.profile['execution_lane'] = 'o26-select-callee-r20'
        self.rewrite_profile()
        with self.assertRaisesRegex(ValueError, 'profile route/backend'):
            route.preflight(self.root, self.infra_root, self.profile_sha, self.env)

    def test_success_exit_never_grants_acceptance(self):
        raw = json.dumps({'schema': 'a1-actual-sort4-body-v1',
                          'classification': 'R21_ACTUAL_BODY_ATTEMPT',
                          'proof_credit': False, 'accepted': False,
                          'verification_accepted': False, 'profile_accepted': False,
                          'body_target': {'status': 'COMPLETE_UNVERIFIED'}}).encode()
        result = route.summarize_diagnostic(raw, 0, 'complete')
        self.assertEqual(result['process_status'], 'SUCCESS_EXIT')
        self.assertEqual(result['body_diagnostic_state'], 'BODY_DIAGNOSTIC_PRESENT')
        self.assertEqual(result['body_status'], 'COMPLETE_UNVERIFIED')
        self.assertIs(result['accepted'], False)
        self.assertIs(result['proof_credit'], False)
        self.assertEqual(result['body_diagnostic']['classification'], 'R21_ACTUAL_BODY_ATTEMPT')

    def test_error_exit_preserves_diagnostic_and_original_stage(self):
        raw = json.dumps({'body_target': {'status': 'INCONCLUSIVE'},
                          'classification': 'R21_ACTUAL_BODY_ATTEMPT'}).encode()
        result = route.summarize_diagnostic(raw, 7, 'actual-body-entry')
        self.assertEqual(result['runner_exit'], 7)
        self.assertEqual(result['failed_stage'], 'actual-body-entry')
        self.assertEqual(result['process_status'], 'ERROR_EXIT')
        self.assertEqual(result['body_diagnostic']['body_target']['status'], 'INCONCLUSIVE')

    def test_timeout_exit_is_kept_distinct(self):
        result = route.summarize_diagnostic(None, 124, 'actual-body-entry')
        self.assertEqual(result['process_status'], 'TIMEOUT')
        self.assertEqual(result['runner_exit'], 124)

    def test_missing_null_wrong_type_and_partial(self):
        self.assertEqual(route.summarize_diagnostic(None, 1, 'entry')['body_diagnostic_state'], 'MISSING')
        self.assertEqual(route.summarize_diagnostic(b'null', 0, 'done')['body_diagnostic_state'], 'NULL')
        wrong = route.summarize_diagnostic(b'[]', 0, 'done')
        self.assertEqual(wrong['body_diagnostic_state'], 'WRONG_TYPE')
        self.assertEqual(wrong['body_diagnostic_raw'], '[]')
        partial = route.summarize_diagnostic(b'{"body_target":{"status":"UNKNOWN"}}', 0, 'done')
        self.assertEqual(partial['body_diagnostic_state'], 'PARTIAL')

    def test_explicit_not_run_is_preserved(self):
        raw = b'{"body_target":{"status":"NOT_RUN","reason":"prerequisite"}}'
        result = route.summarize_diagnostic(raw, 0, 'complete')
        self.assertEqual(result['body_diagnostic_state'], 'NOT_RUN')
        self.assertEqual(result['body_status'], 'NOT_RUN')
        self.assertIs(result['accepted'], False)

    def test_audit_writes_diagnostic_and_original_runner_outcome(self):
        evidence = self.root / 'evidence'
        evidence.mkdir()
        diagnostic = {'schema': 'a1-actual-sort4-body-v1',
                      'classification': 'R21_ACTUAL_BODY_ATTEMPT',
                      'proof_credit': False, 'accepted': False,
                      'verification_accepted': False, 'profile_accepted': False,
                      'body_target': {'status': 'NOT_RUN'}}
        (evidence / 'diagnostic-audit.json').write_text(json.dumps(diagnostic))
        output = self.root / 'proof-audit.json'
        result = route.audit(evidence, output, 124, 'actual-body-entry',
                             self.root, self.infra_root, self.profile_sha, self.env)
        saved = json.loads(output.read_text())
        self.assertEqual(result['runner_exit'], 124)
        self.assertEqual(saved['failed_stage'], 'actual-body-entry')
        self.assertEqual(saved['body_diagnostic'], diagnostic)
        self.assertEqual(saved['profile_preflight']['classification'], 'PREFLIGHT_MATCH')
        self.assertIs(saved['accepted'], False)
        self.assertIs(saved['proof_credit'], False)

    def test_audit_preserves_failure_when_profile_route_is_wrong(self):
        evidence = self.root / 'evidence'
        evidence.mkdir()
        output = self.root / 'proof-audit.json'
        self.env['LANE'] = 'o26-select-callee-r20'
        result = route.audit(evidence, output, 2, 'preflight',
                             self.root, self.infra_root, self.profile_sha, self.env)
        self.assertEqual(result['runner_exit'], 2)
        self.assertEqual(result['failed_stage'], 'preflight')
        self.assertEqual(result['profile_preflight']['classification'], 'PREFLIGHT_MISMATCH')
        self.assertEqual(result['body_diagnostic_state'], 'MISSING')


if __name__ == '__main__':
    unittest.main()
