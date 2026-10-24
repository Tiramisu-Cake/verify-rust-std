import argparse
from contextlib import ExitStack
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import subprocess
from unittest import mock


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / 'select-callee-r24-w4-const-qualification.py'
SPEC = importlib.util.spec_from_file_location('r24_w4_const_qualification_tested', SCRIPT)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class ConsequenceFake:
    SUMMARY_REL = Path('cases/r24-w4-const-consequence/W4-CONST-CONSEQUENCE.json')

    def run(self, args, *, const_matrix_summary=None, const_matrix_audit=None, **kwargs):
        return {'complete': True, 'accepted': False,
                'body_proof_run': True, 'call_linkage': 'UNKNOWN',
                'publication_allowed': False, 'proof_credit': 0,
                'matrix_summary': const_matrix_summary is not None,
                'matrix_audit': const_matrix_audit is not None}

    def audit(self, args, *, diag=None, const_matrix_summary=None, const_matrix_audit=None):
        return {'complete': args.runner_exit == 0 and args.failed_stage == 'complete',
                'evidence_complete': args.runner_exit == 0 and args.failed_stage == 'complete',
                'accepted': False, 'proof_credit': 0}


class ContractFake:
    SCHEMA = 'select-r24-w4-contract-inputs-v1'
    SUMMARY_REL = Path('cases/r24-w4-contract-inputs/W4-CONTRACT-INPUTS.json')
    AUDIT_REL = Path('cases/r24-w4-contract-inputs/W4-CONTRACT-INPUTS-AUDIT.json')

    def run(self, args, *, const_matrix_summary=None, const_matrix_audit=None,
            consequence_summary=None, consequence_audit=None):
        assert args.const_mode_file != args.mode_file
        assert args.mode_file == args.repo / MOD.CONTRACT_MODE_REL
        assert const_matrix_summary['complete'] is True
        assert const_matrix_audit['evidence_complete'] is True
        assert consequence_summary['complete'] is True
        assert consequence_audit['complete'] is True
        record = dict(complete=True, accepted=False, publication_allowed=False,
                      proof_credit=0, caller_body_proof_admission=False,
                      typed_call_linkage='UNKNOWN')
        path = args.evidence / self.SUMMARY_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record))
        return record

    def audit(self, args, *, const_matrix_summary=None, const_matrix_audit=None,
              consequence_summary=None, consequence_audit=None):
        path = args.evidence / self.SUMMARY_REL
        complete = path.is_file() and args.runner_exit == 0 and args.failed_stage == 'complete'
        record = dict(complete=complete, evidence_complete=complete, accepted=False,
                      publication_allowed=False, proof_credit=0,
                      caller_body_proof_admission=False, typed_call_linkage='UNKNOWN')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record))
        return record


class ControlFake:
    SCHEMA = 'select-r24-w4-control-capture-v1'
    SUMMARY_REL = Path('cases/r24-w4-control-capture/W4-CONTROL-CAPTURE.json')
    AUDIT_REL = Path('cases/r24-w4-control-capture/W4-CONTROL-CAPTURE-AUDIT.json')

    def run(self, args, *, prerequisite_summary=None, prerequisite_audit=None):
        assert args.mode_file == args.repo / MOD.CONTROL_MODE_REL
        assert args.native_tool_home == Path('/workspace/smallsort-work/r24-w4-contract-input-tool')
        assert prerequisite_summary['complete'] is True
        assert prerequisite_audit['evidence_complete'] is True
        record = dict(complete=True, accepted=False, publication_allowed=False,
                      proof_credit=0, caller_body_proof_admission=False,
                      typed_call_linkage='UNKNOWN', body_proof_run=False,
                      universe_complete=False)
        path = args.evidence / self.SUMMARY_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record))
        return record

    def audit(self, args, *, prerequisite_summary=None, prerequisite_audit=None):
        path = args.evidence / self.SUMMARY_REL
        complete = path.is_file() and args.runner_exit == 0 and args.failed_stage == 'complete'
        record = dict(complete=complete, evidence_complete=complete, accepted=False,
                      publication_allowed=False, proof_credit=0,
                      caller_body_proof_admission=False, typed_call_linkage='UNKNOWN',
                      body_proof_run=False, universe_complete=False)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record))
        return record


def matrix_record(native_home=None, target_receipt=None):
    variants = {}
    for variant in MOD.VARIANTS:
        same_site = variant in {'omit-selected-own', 'omit-unselected-own', 'no-retained-half'}
        variants[variant] = {
            'variant': variant, 'status': 'COMPLETE',
            'classification': ('POSITIVE_VERIFIED_SOURCE_REPORTED' if variant == 'positive' else
                               'EXPECTED_SAME_SITE_TYPED_FAILURE' if same_site else
                               'EXPECTED_CALLEE_CONTRACT_REJECTION'),
            'normal_unwind_nested_drop_gates': True,
            'current_stage_observation': {'status': 'RAN', 'exit': 0 if variant == 'positive' else 1,
                                          'source_unchanged': True,
                                          'argv': ([str(native_home / 'bin/verifast'), '-rustc_args',
                                                    '--edition 2021', '-verbose', '1', 'verified/lib.rs']
                                                   if native_home else [])},
        }
    receipt = target_receipt or {}
    return {'schema': 'r21-fractional-classified-proof-v1',
            'complete': True, 'variant_order': list(MOD.VARIANTS),
            'body_proof_run': True,
            'rows': variants, 'pins': {'base_original_sha256': MOD.CONST_ORIGINAL_SHA256,
                                       'base_verified_sha256': MOD.CONST_BASE_VERIFIED_SHA256},
            'tool_home': str(native_home) if native_home else None,
            'entry_dependencies': {
                'target_map_sha256': receipt.get('derived_map_raw_sha256'),
                'target_map_canonical_sha256': receipt.get('derived_map_canonical_sha256'),
                'tool_spec_sha256': receipt.get('new_spec_sha256')},
            'diagnostic_target_map_sha256': receipt.get('derived_map_canonical_sha256'),
            'current_build_id': 'build-uuid', 'checked_pointer_outcomes_requested': True,
            'accepted': False, 'proof_credit': False}


class FakeCommandRunner:
    def __init__(self, fail=None, result=None, throw=None, native_home=None,
                 omit_output=None, dirty_after=None):
        self.fail = fail
        self.result = result
        self.throw = throw
        self.native_home = native_home
        self.omit_output = omit_output
        self.dirty_after = dirty_after
        self.calls = []

    def __call__(self, name, argv, *, cwd, env, deadline):
        self.calls.append((name, argv))
        if name == self.throw:
            raise RuntimeError('injected stage exception')
        if name == self.omit_output:
            return {'status': 'RAN', 'exit': 0, 'stdout': '', 'stderr': ''}
        if name == self.fail:
            return self.result or {'status': 'RAN', 'exit': 1, 'stdout': 'stage out', 'stderr': 'stage err'}
        work = Path(argv[argv.index('--evidence') + 1]) if '--evidence' in argv else None
        if name == 'source-preflight':
            work.mkdir(parents=True, exist_ok=True)
            data = {'source_generation_complete': True,
                    'source': {'original_sha256': MOD.CONST_ORIGINAL_SHA256,
                               'verified_sha256': MOD.CONST_BASE_VERIFIED_SHA256,
                               'ghost_strip_identity': True}}
            (work / 'source-preflight.json').write_text(json.dumps(data))
        elif name == 'candidate-capture':
            root = work / 'nine-body-a1-owned-forget'
            source = {'original_sha256': MOD.CONST_ORIGINAL_SHA256,
                      'verified_sha256': MOD.CONST_BASE_VERIFIED_SHA256,
                      'ghost_strip_identity': True}
            for variant, content in (('original', b'orig'), ('verified', b'verified')):
                raw = content
                source[variant + '_sha256'] = sha(raw)
                p = root / variant / 'lib.rs'
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(raw)
            data = {'frontend_refinement_and_full_body_capture': True,
                    'actual_helper_proved': False, 'source': source}
            (work / 'summary.json').write_text(json.dumps(data))
        elif name == 'candidate-source-compare':
            (work / 'cases/candidate/capture-compare.json').write_text(
                json.dumps({'capture_complete': True}))
        elif name == 'candidate-proof':
            case = work / 'cases/candidate/capture/nine-body-a1-owned-forget'
            (case / 'refreshed-proof.log').write_text('baseline verifier result')
            (work / 'cases/candidate/proof-stage.json').write_text(json.dumps({
                'stage': {'status': 'RAN', 'exit': 1, 'source_unchanged': True,
                          'argv': [str(self.native_home / 'bin/verifast'), '-rustc_args',
                                   '--edition 2021', '-verbose', '1', 'verified/lib.rs'],
                          'stdout': 'refreshed-proof.log', 'stderr': 'refreshed-proof.log',
                          'source_before': {'original/lib.rs': MOD.CONST_ORIGINAL_SHA256,
                                            'verified/lib.rs': MOD.CONST_BASE_VERIFIED_SHA256},
                          'source_after': {'original/lib.rs': MOD.CONST_ORIGINAL_SHA256,
                                           'verified/lib.rs': MOD.CONST_BASE_VERIFIED_SHA256}},
                'actual_verification_accepted': False}))
            if self.dirty_after == name:
                (work / 'cases/candidate/capture/nine-body-a1-owned-forget/verified/lib.rs').write_bytes(b'dirty')
        elif name == 'r21-fractional-proof':
            path = work / MOD.CONST_MATRIX_REPORT_REL
            path.parent.mkdir(parents=True, exist_ok=True)
            receipt = json.loads((work / MOD.TARGET_INTENT_RECEIPT_REL).read_text())
            path.write_text(json.dumps(matrix_record(self.native_home, receipt)))
        elif name == 'const-regression-audit':
            path = work / MOD.CONST_MATRIX_AUDIT_REL
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({'evidence_complete': True, 'accepted': False,
                                        'verification_accepted': False, 'proof_credit': False}))
        return {'status': 'RAN', 'exit': 0, 'stdout': 'synthetic stdout', 'stderr': ''}


class FrozenAuditFake:
    def compare(self, evidence):
        return None

    def audit(self, args):
        value = json.loads((args.evidence / MOD.CONST_MATRIX_AUDIT_REL).read_text())
        args.output.write_text(json.dumps(value))
        return value


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.args = argparse.Namespace(
            repo=self.root / 'repo', cloud_dir=self.root / 'cloud',
            evidence=self.root / 'evidence', tool_home=self.root / 'tool8a',
            native_tool_home=self.root / 'tool5170',
            schema=self.root / 'tool5170/src/rust_frontend/vf_mir/vf_mir.capnp',
            compiler_sysroot=self.root / 'sysroot', deadline_epoch=4_000_000_000,
            candidate='a' * 40, capture_mode_file=self.root / 'mode-capture.json',
            mode_file=self.root / 'mode-new.json')
        self.args.evidence.mkdir(parents=True)
        self.provider_receipt = json.dumps({'synthetic': True}, sort_keys=True).encode()
        (self.args.evidence / 'candidate-provider-overlay.json').write_bytes(self.provider_receipt)
        self.args.repo.mkdir()
        self.args.cloud_dir.mkdir()
        self.args.tool_home.mkdir()
        self.args.native_tool_home.mkdir()
        self.target_spec = b'synthetic pinned lib.rsspec\n'
        for home in (self.args.tool_home, self.args.native_tool_home):
            spec = home / 'bin/rust/std/lib.rsspec'
            spec.parent.mkdir(parents=True)
            spec.write_bytes(self.target_spec)
        source_map = json.loads((HERE.parents[2] / MOD.TARGET_MAP_REL).read_text())
        old_spec = str((self.args.tool_home / 'bin/rust/std/lib.rsspec').resolve())
        for row in source_map['targets'].values():
            if row['file'].endswith('/lib.rsspec'):
                row['file'] = old_spec
                row['tool_spec_sha256'] = sha(self.target_spec)
        self.target_map_raw = (json.dumps(source_map, indent=2, sort_keys=True) + '\n').encode()
        target_path = self.args.repo / MOD.TARGET_MAP_REL
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(self.target_map_raw)
        self.env = dict(os.environ)
        self.env.update({MOD.R24_PHASE_ENV: MOD.R24_PHASE, MOD.R21_PHASE_ENV: MOD.R21_PHASE,
                         'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build',
                         'SORT4_SELECT_PROFILE': MOD.PROFILE, 'LANE': MOD.LANE,
                         'CLOUD_BUILD_ID': 'build-uuid'})
        self.original = b'orig'
        self.verified = b'verified'
        self.old_digest = {'old-tool': 'old'}
        self.native_digest = {'bin/verifast': {'regular': True, 'sha256': 'native',
                                               'bytes': 1, 'expected_sha256': 'native',
                                               'matches': True}}

    def tearDown(self):
        self.tmp.cleanup()

    def patched(self):
        patches = [
            mock.patch.object(MOD, '_context'),
            mock.patch.object(MOD, '_mode', return_value={}),
            mock.patch.object(MOD, '_validate_pins', return_value={
                'cloud_overlay': {'path': str(self.args.evidence / 'candidate-provider-overlay.json'),
                                  'sha256': sha(self.provider_receipt)}}),
            mock.patch.object(MOD, '_tool_identity', return_value=self.old_digest),
            mock.patch.object(MOD, '_read_native_files', return_value=self.native_digest),
            mock.patch.object(MOD, 'TOOL_HASHES_8A', {'old-tool': 'old'}),
            mock.patch.object(MOD, 'NATIVE_TOOL_HASHES', {'bin/verifast': 'native'}),
            mock.patch.object(MOD, 'TARGET_SPEC_SHA256', sha(self.target_spec)),
            mock.patch.object(MOD, 'TARGET_MAP_SHA256', sha(self.target_map_raw)),
            mock.patch.object(MOD, 'CONST_ORIGINAL_SHA256', sha(self.original)),
            mock.patch.object(MOD, 'CONST_BASE_VERIFIED_SHA256', sha(self.verified)),
        ]
        stack = ExitStack()
        for patcher in patches: stack.enter_context(patcher)
        return stack

    def _synthetic_target_map_for_frozen_validator(self):
        helper_path = HERE / 'select-callee-r22-control-targets.py'
        helper = MOD._load(helper_path, 'r24_test_r22_target_helper', sha(helper_path.read_bytes()))
        sources = {}
        for variant in helper.VARIANTS:
            if variant in helper.CALLEE_VARIANTS:
                sources[variant] = (helper.FORGET_SIGNATURE +
                                    helper.FORGET_CONTRACTS[variant] + b'\n' +
                                    helper.FORGET_BODY + b'\n')
            else:
                sources[variant] = (helper.SELECT_SIGNATURE + b'{\n' +
                                    helper.RETAINED_HALF_MERGE + b'\n' +
                                    helper.FULL_CELL_ASSERT + b'}\n')
        spec_lines = [b''] * 463
        spec_lines[461] = helper.SPEC_PRECONDITION_TEXT['omit-selected-own'].encode()
        spec_lines[462] = helper.SPEC_PRECONDITION_TEXT['omit-unselected-own'].encode()
        spec = b'\n'.join(spec_lines) + b'\n'
        spec_hash = sha(spec)
        for home in (self.args.tool_home, self.args.native_tool_home):
            path = home / 'bin/rust/std/lib.rsspec'
            path.write_bytes(spec)
        raw_map = json.loads((HERE.parents[2] / MOD.TARGET_MAP_REL).read_text())
        for variant, source in sources.items():
            row = raw_map['targets'][variant]
            file, line = helper._source_anchor(variant, source)
            row.update(source_sha256=sha(source), tool_spec_sha256=spec_hash,
                       file=(str((self.args.tool_home / helper.TOOL_SPEC_FILE).resolve())
                             if variant in helper.SPEC_PRECONDITION_LINE else file),
                       line=line)
        raw = (json.dumps(raw_map, indent=2, sort_keys=True) + '\n').encode()
        path = self.args.repo / MOD.TARGET_MAP_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return helper, raw_map, sources, spec, spec_hash, raw

    def test_derived_intent_relocates_only_spec_paths_and_frozen_validator_accepts(self):
        helper, original, sources, spec, spec_hash, raw = self._synthetic_target_map_for_frozen_validator()
        with mock.patch.object(MOD, 'TARGET_MAP_SHA256', sha(raw)), \
             mock.patch.object(MOD, 'TARGET_SPEC_SHA256', spec_hash):
            derived, receipt, _, _ = MOD._target_intent_material(self.args)
            self.assertEqual(receipt['semantics'], 'DERIVED_TARGET_INTENT_NOT_NEW_OBSERVATION')
            self.assertFalse(receipt['new_path_observed'])
            changed = []
            for variant in helper.VARIANTS:
                before, after = original['targets'][variant], derived['targets'][variant]
                allowed = {'file'} if variant in helper.SPEC_PRECONDITION_LINE else set()
                self.assertEqual({k: v for k, v in before.items() if k not in allowed},
                                 {k: v for k, v in after.items() if k not in allowed})
                if allowed:
                    changed.append((variant, before['file'], after['file']))
            self.assertEqual([row[0] for row in changed],
                             ['omit-selected-own', 'omit-unselected-own'])
            result = helper.validate_target_map(
                derived, sources, spec,
                tool_spec_file=str(self.args.native_tool_home / helper.TOOL_SPEC_FILE),
                tool_home=self.args.native_tool_home)
        self.assertEqual(result['status'], 'TARGET_MAP_VALIDATED_NOT_ACCEPTED')
        self.assertEqual(result['provenance_status'],
                         'CALLER_DECLARED_PRIOR_OBSERVATIONS_CONSISTENT_NOT_AUTHENTICATED')
        self.assertFalse(result['accepted'])
        self.assertFalse(result['proof_credit'])

    def test_target_intent_audit_recomputes_physical_map_and_receipt(self):
        with self.patched():
            work = self.args.evidence / MOD.WORK_REL
            work.mkdir(parents=True)
            receipt = MOD._write_target_intent(self.args, work)
            reserved_matrix_root = work / 'cases/r21-fractional-proof'
            self.assertFalse(reserved_matrix_root.exists())
            reserved_matrix_root.mkdir(parents=True, exist_ok=False)
            self.assertEqual(MOD._validate_target_intent(self.args, work, receipt), [])
            (work / MOD.TARGET_INTENT_REL).write_bytes(b'{}\n')
            self.assertTrue(any('artifact changed' in e for e in
                                MOD._validate_target_intent(self.args, work, receipt)))

    def test_target_intent_audit_rejects_symlinked_parent_escape(self):
        with self.patched():
            work = self.args.evidence / MOD.WORK_REL
            work.mkdir(parents=True)
            receipt = MOD._write_target_intent(self.args, work)
            intent_parent = work / MOD.TARGET_INTENT_REL.parent
            outside = self.root / 'escaped-target-inputs'
            intent_parent.rename(outside)
            intent_parent.symlink_to(outside, target_is_directory=True)
            errors = MOD._validate_target_intent(self.args, work, receipt)
        self.assertTrue(any('escapes or aliases' in error for error in errors))

    def test_target_intent_refuses_native_spec_drift_and_symlink(self):
        with self.patched():
            spec = self.args.native_tool_home / 'bin/rust/std/lib.rsspec'
            spec.write_bytes(b'changed')
            with self.assertRaisesRegex(RuntimeError, 'bytes differ'):
                MOD._target_intent_material(self.args)
            spec.unlink()
            external = self.root / 'outside.rsspec'
            external.write_bytes(self.target_spec)
            spec.symlink_to(external)
            with self.assertRaisesRegex(RuntimeError, 'symlinked|outside'):
                MOD._target_intent_material(self.args)

    def test_target_intent_rejects_missing_null_and_wrong_type_map(self):
        target_path = self.args.repo / MOD.TARGET_MAP_REL
        original = target_path.read_bytes()
        for content in (b'null\n', b'[]\n'):
            target_path.write_bytes(content)
            with mock.patch.object(MOD, 'TARGET_MAP_SHA256', sha(content)), \
                 mock.patch.object(MOD, 'TARGET_SPEC_SHA256', sha(self.target_spec)):
                with self.assertRaisesRegex(RuntimeError, 'schema or shape'):
                    MOD._target_intent_material(self.args)
        target_path.unlink()
        with self.patched():
            with self.assertRaisesRegex(RuntimeError, 'missing or unsafe'):
                MOD._target_intent_material(self.args)
        target_path.write_bytes(original)

    def test_unmocked_canonical_mode_and_pinned_inputs_accept_synthetic_overlay(self):
        repo = self.root / 'pinned-repo'
        evidence = self.root / 'pinned-evidence'
        repo.mkdir()
        evidence.mkdir()
        source_repo = HERE.parents[2]
        json_inputs = (MOD.CAPTURE_MODE_REL, MOD.CAPTURE_PINS_REL,
                       MOD.NATIVE_FINGERPRINT_PINS_REL, MOD.W4_INPUTS_REL,
                       MOD.CONST_QUALIFICATION_REL, MOD.P2_INTERFACE_REL,
                       MOD.FRACTIONAL_PINS_REL, MOD.TARGET_MAP_REL, MOD.MODE_REL,
                       MOD.O26_PROVIDER_REL, MOD.CONTRACT_MODE_REL, MOD.CONTROL_MODE_REL)
        for rel in json_inputs:
            destination = repo / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_repo / rel, destination)
        recipe_path = source_repo / MOD.O26_BASE_REL
        spec = importlib.util.spec_from_file_location('test_o26_base_recipe', recipe_path)
        o26 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(o26)
        overlay_rows = []
        for relative, (original_sha, overlaid_sha) in MOD.O26_OVERLAY_FILES.items():
            relative_path = Path(relative)
            raw = (source_repo / relative_path).read_text()
            self.assertEqual(sha(raw.encode()), original_sha)
            matches = [guard for guard in o26.GUARD_VARIANTS if raw.count(guard) == 1]
            self.assertEqual(len(matches), 1)
            overlaid = raw.replace(matches[0], '_o26_cloud_provider_ok()', 1)
            overlaid = overlaid.replace('from pathlib import Path\n',
                                        'from pathlib import Path\n' + o26.HELPER, 1)
            self.assertEqual(sha(overlaid.encode()), overlaid_sha)
            destination = repo / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(overlaid)
            overlay_rows.append({'path': relative, 'original_sha256': original_sha,
                                 'cloud_overlay_sha256': overlaid_sha, 'guard_only': True})
        (evidence / 'candidate-provider-overlay.json').write_text(json.dumps({
            'proof_sha': 'a' * 40, 'provider_sha256': MOD.O26_PROVIDER_SHA256,
            'files': overlay_rows}))
        args = argparse.Namespace(
            repo=repo, cloud_dir=HERE, evidence=evidence,
            tool_home=self.root / 'frozen8a', native_tool_home=self.root / 'native5170',
            schema=self.root / 'native5170/src/rust_frontend/vf_mir/vf_mir.capnp',
            compiler_sysroot=self.root / 'sysroot', deadline_epoch=4_000_000_000,
            candidate='a' * 40, capture_mode_file=repo / MOD.CAPTURE_MODE_REL,
            mode_file=repo / MOD.MODE_REL)
        self.assertEqual(MOD._mode(args), MOD.expected_mode())
        pins = MOD._validate_pins(args)
        self.assertEqual(pins['w4_inputs']['native_body_inventory'], ['sort4_stable'])
        self.assertEqual(pins['cloud_overlay']['proof_sha'], args.candidate)

    def test_frozen_pinned_dependencies_uses_byte_identical_work_receipt(self):
        source_repo = HERE.parents[2]
        repo = self.root / 'synthetic-proof-repo'
        evidence = self.root / 'outer-evidence'
        work = evidence / MOD.WORK_REL
        repo.mkdir()
        evidence.mkdir()
        work.mkdir(parents=True)
        git = lambda *items: subprocess.run(['git', '-C', str(repo), *items],
                                             check=True, capture_output=True, text=True)
        git('init', '-q')
        git('config', 'user.email', 'fixture@example.invalid')
        git('config', 'user.name', 'synthetic fixture')
        fractional = MOD._load(HERE / 'select-callee-r21-fractional.py',
                               'r24_const_qualification_frozen_fractional',
                               '9cb4dee13b134f1ba328b35c23e667c4ef73961cf980147fdda8f9cb56d16c71')
        o26_spec = importlib.util.spec_from_file_location('test_real_o26_overlay', HERE / 'o26-recipe.py')
        o26 = importlib.util.module_from_spec(o26_spec)
        o26_spec.loader.exec_module(o26)
        for relative in (*o26.OVERLAYS, fractional.TRANSFORM_REL):
            source = source_repo / relative
            target = repo / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        git('add', '--all')
        git('commit', '-q', '-m', 'synthetic provider overlay validation inputs')
        proof_sha = git('rev-parse', 'HEAD').stdout.strip()
        rows = []
        for relative in o26.OVERLAYS:
            path = repo / relative
            committed = path.read_bytes()
            before = committed.decode('utf-8')
            guards = [guard for guard in o26.GUARD_VARIANTS if before.count(guard) == 1]
            self.assertEqual(len(guards), 1)
            after = before.replace(guards[0], '_o26_cloud_provider_ok()', 1)
            after = after.replace('from pathlib import Path\n',
                                  'from pathlib import Path\n' + o26.HELPER, 1)
            overlaid = after.encode()
            path.write_bytes(overlaid)
            rows.append({'path': relative.as_posix(), 'original_sha256': sha(committed),
                         'cloud_overlay_sha256': sha(overlaid), 'guard_only': True,
                         'diff': ''.join(difflib.unified_diff(
                             before.splitlines(True), after.splitlines(True),
                             fromfile=relative.as_posix() + '.committed',
                             tofile=relative.as_posix() + '.cloud-guard'))})
        original_source, verified_source = b'synthetic original source', b'synthetic verified source'
        original_path, verified_path = work / 'preflight/original/lib.rs', work / 'preflight/verified/lib.rs'
        original_path.parent.mkdir(parents=True, exist_ok=True)
        verified_path.parent.mkdir(parents=True, exist_ok=True)
        original_path.write_bytes(original_source)
        verified_path.write_bytes(verified_source)
        (work / 'source-preflight.json').write_text(json.dumps({
            'classification': 'O26_REFRESH_SOURCE_ONLY_PREFLIGHT',
            'source_generation_complete': True, 'compiler_or_verifier_invoked': False,
            'source': {'original_sha256': sha(original_source),
                       'verified_sha256': sha(verified_source),
                       'ghost_strip_identity': True,
                       'source_order': [f'function-{i}' for i in range(9)]},
            'files': {'original': 'preflight/original/lib.rs',
                      'verified': 'preflight/verified/lib.rs'}}))
        receipt = {'proof_sha': proof_sha, 'provider_sha256': o26.PROVIDER_SHA, 'files': rows}
        raw_receipt = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
        (evidence / 'candidate-provider-overlay.json').write_bytes(raw_receipt)
        with self.assertRaisesRegex(RuntimeError, 'provider overlay receipt is missing'):
            fractional.pinned_dependencies(repo, HERE, work)
        binding = MOD._copy_provider_overlay_receipt(
            evidence, work, {'sha256': sha(raw_receipt)})
        self.assertEqual(binding['sha256'], sha(raw_receipt))
        real_validator = fractional.validate_o26_provider_overlay

        def synthetic_preflight_validator(repo_arg, cloud_arg, evidence_arg, o26_arg,
                                          *, expected_source_sha256,
                                          expected_original_sha256, committed_reader=None):
            return real_validator(repo_arg, cloud_arg, evidence_arg, o26_arg,
                                  expected_source_sha256=sha(verified_source),
                                  expected_original_sha256=sha(original_source),
                                  committed_reader=committed_reader)

        with mock.patch.object(fractional, 'validate_o26_provider_overlay',
                               side_effect=synthetic_preflight_validator):
            dependencies = fractional.pinned_dependencies(repo, HERE, work)
        self.assertEqual(len(dependencies), 4)
        self.assertEqual(MOD._validate_provider_overlay_copy(evidence, work, binding), [])

    def test_service_composition_success_records_all_routes_false(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(native_home=self.args.native_tool_home)
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake(), contract_module=ContractFake(), control_module=ControlFake())
        self.assertTrue(record['complete'])
        self.assertEqual(len(runner.calls), 6)
        self.assertEqual(record['accepted'], False)
        self.assertEqual(record['publication_allowed'], False)
        self.assertEqual(record['proof_credit'], 0)
        self.assertEqual(record['native_tool_hashes_before'], record['native_tool_hashes_after'])
        for _, argv in runner.calls:
            if 'select-callee-r21-fractional-proof-entry.py' in argv[1]:
                self.assertIn(str(self.args.native_tool_home), argv)

    def test_audit_reopens_summary_matrix_logs_source_and_tool_identity(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(native_home=self.args.native_tool_home)
            MOD.run(self.args, command_runner=runner,
                    consequence_module=ConsequenceFake(), contract_module=ContractFake(), control_module=ControlFake())
            self.args.output = self.args.evidence / MOD.AUDIT_REL
            self.args.runner_exit = 0
            self.args.failed_stage = 'complete'
            with mock.patch.object(MOD, '_load', return_value=FrozenAuditFake()):
                result = MOD.audit(self.args, consequence_module=ConsequenceFake(), contract_module=ContractFake(), control_module=ControlFake())
        self.assertTrue(result['complete'], result['errors'])
        self.assertFalse(result['accepted'])
        self.assertEqual(result['proof_credit'], 0)

    def test_contract_diagnostic_not_run_after_matrix_failure(self):
        diagnostic = ContractFake()
        diagnostic.run = mock.Mock(side_effect=AssertionError('must not run'))
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            record = MOD.run(self.args, command_runner=FakeCommandRunner(
                fail='r21-fractional-proof', native_home=self.args.native_tool_home),
                consequence_module=ConsequenceFake(), contract_module=diagnostic, control_module=ControlFake())
        self.assertFalse(record['complete'])
        diagnostic.run.assert_not_called()

    def test_contract_partial_or_boundary_escape_stays_incomplete(self):
        for value in (None, [], {'complete': False},
                      dict(complete=True, accepted=True, publication_allowed=False,
                           proof_credit=0, caller_body_proof_admission=False,
                           typed_call_linkage='UNKNOWN')):
            self.assertTrue(MOD._contract_boundary_errors(value))

    def test_source_capture_not_run_after_partial_contract_diagnostic(self):
        diagnostic = ContractFake()
        diagnostic.audit = mock.Mock(return_value=dict(
            complete=False, evidence_complete=False, accepted=False,
            publication_allowed=False, proof_credit=0,
            caller_body_proof_admission=False, typed_call_linkage='UNKNOWN'))
        captured = ControlFake()
        captured.run = mock.Mock(side_effect=AssertionError('must not run'))
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            record = MOD.run(self.args, command_runner=FakeCommandRunner(
                native_home=self.args.native_tool_home), consequence_module=ConsequenceFake(),
                contract_module=diagnostic, control_module=captured)
        self.assertFalse(record['complete'])
        captured.run.assert_not_called()

    def test_source_capture_partial_and_boundary_escape_are_incomplete(self):
        good = dict(complete=True, evidence_complete=True, accepted=False,
                    publication_allowed=False, proof_credit=0,
                    caller_body_proof_admission=False, typed_call_linkage='UNKNOWN',
                    body_proof_run=False, universe_complete=False)
        self.assertEqual(MOD._control_boundary_errors(good, audited=True), [])
        for key, value in (('complete', False), ('evidence_complete', False),
                           ('body_proof_run', True), ('universe_complete', True),
                           ('accepted', True), ('proof_credit', False)):
            self.assertTrue(MOD._control_boundary_errors(
                dict(good, **{key: value}), audited=True), key)

    def test_source_capture_exception_preserves_original_and_partial_snapshot(self):
        captured = ControlFake()
        captured.run = mock.Mock(side_effect=ValueError('injected capture failure'))
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            with self.assertRaisesRegex(ValueError, 'injected capture failure'):
                MOD.run(self.args, command_runner=FakeCommandRunner(
                    native_home=self.args.native_tool_home), consequence_module=ConsequenceFake(),
                    contract_module=ContractFake(), control_module=captured)
        partial = json.loads((self.args.evidence / MOD.SUMMARY_REL).read_text())
        self.assertFalse(partial['complete'])
        self.assertTrue(partial['postqualification_diagnostic']['complete'])
        self.assertIsNone(partial['source_control_capture'])
        self.assertTrue(any('ValueError' in e for e in partial['errors']))

    def test_contract_runner_exception_keeps_partial_and_original_exception(self):
        diagnostic = ContractFake()
        diagnostic.run = mock.Mock(side_effect=ValueError('injected diagnostic failure'))
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            with self.assertRaisesRegex(ValueError, 'injected diagnostic failure'):
                MOD.run(self.args, command_runner=FakeCommandRunner(
                    native_home=self.args.native_tool_home),
                    consequence_module=ConsequenceFake(), contract_module=diagnostic, control_module=ControlFake())
        partial = json.loads((self.args.evidence / MOD.SUMMARY_REL).read_text())
        self.assertFalse(partial['complete'])
        self.assertTrue(partial['consequence']['complete'])
        self.assertTrue(any('ValueError' in e for e in partial['errors']))

    def test_partial_matrix_audit_uses_real_consequence_signature_and_fails_closed(self):
        consequence = MOD._load(HERE / MOD.CONSEQUENCE_REL.name,
                                'r24_w4_const_consequence_signature_test',
                                MOD.CONSEQUENCE_SHA256)
        contract = MOD._load(HERE / MOD.CONTRACT_REL.name,
                            'r24_w4_contract_inputs_signature_test',
                            MOD.CONTRACT_SHA256)
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(fail='r21-fractional-proof', native_home=self.args.native_tool_home)
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake(), contract_module=ContractFake(), control_module=ControlFake())
            self.assertFalse(record['complete'])
            self.args.cloud_dir = HERE
            self.args.output = self.args.evidence / MOD.AUDIT_REL
            self.args.runner_exit = 1
            self.args.failed_stage = 'r21-fractional-proof'
            with mock.patch.object(MOD, '_load', return_value=FrozenAuditFake()):
                audit = MOD.audit(self.args, consequence_module=consequence,
                                  contract_module=contract, control_module=ControlFake())
        self.assertFalse(audit['complete'])
        self.assertFalse(audit['evidence_complete'])
        self.assertTrue(any('matrix' in item or 'command identity' in item
                            for item in audit['errors']))
        consequence_audit = json.loads(
            (self.args.evidence / MOD.WORK_REL /
             'cases/r24-w4-const-consequence/W4-CONST-CONSEQUENCE-AUDIT.json').read_text())
        self.assertFalse(consequence_audit['evidence_complete'])
        contract_audit = json.loads((self.args.evidence / MOD.WORK_REL /
                                    contract.AUDIT_REL).read_text())
        self.assertFalse(contract_audit['complete'])
        self.assertFalse(contract_audit['evidence_complete'])

    def test_error_exit_is_preserved_and_stops_following_stages(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(fail='candidate-source-compare')
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake(), contract_module=ContractFake(), control_module=ControlFake())
        self.assertFalse(record['complete'])
        self.assertEqual(record['stages'][-1]['exit'], 1)
        self.assertEqual(record['stages'][-1]['name'], 'candidate-source-compare')
        self.assertEqual(len(runner.calls), 3)

    def test_timeout_status_and_exit_are_not_recast(self):
        runner = FakeCommandRunner(fail='source-preflight', result={
            'status': 'TIMEOUT', 'exit': 124, 'stdout': 'partial', 'stderr': 'timeout'})
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake(), contract_module=ContractFake(), control_module=ControlFake())
        self.assertEqual(record['stages'][0]['status'], 'TIMEOUT')
        self.assertEqual(record['stages'][0]['exit'], 124)
        self.assertFalse(record['complete'])

    def test_missing_success_artifact_stays_incomplete(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(omit_output='candidate-capture')
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake(), contract_module=ContractFake(), control_module=ControlFake())
        self.assertFalse(record['complete'])
        self.assertEqual(record['stages'][-1]['status'], 'RAN')
        self.assertTrue(any('capture' in error for error in record['errors']))

    def test_missing_null_and_wrong_type_stage_results_fail_closed(self):
        for malformed in (None, 'not-a-stage', {'status': 'NOT_RUN', 'exit': None,
                                                'stdout': None, 'stderr': None}):
            row = MOD._stage_record('stage', ['cmd'], malformed)
            self.assertNotEqual(row['status'], 'RAN')
            self.assertTrue(row['errors'])

    def test_matrix_requires_all_exact_rows_and_source_bound_ran_stages(self):
        data = matrix_record()
        self.assertEqual(MOD._validate_matrix_rows(data), [])
        del data['rows']['omit-selected-own']
        self.assertTrue(MOD._validate_matrix_rows(data))

    def test_source_stage_target_mismatch_is_rejected(self):
        data = matrix_record()
        data['rows']['positive']['current_stage_observation']['source_unchanged'] = False
        self.assertIn('proof stage missing/partial/source-dirty: positive',
                      MOD._validate_matrix_rows(data))
        with mock.patch.object(MOD, 'CONST_ORIGINAL_SHA256', 'a' * 64):
            self.assertIn('matrix source-stage-target command differs: positive',
                          MOD._validate_matrix_rows(data, native_home=Path('/native')))

    def test_dirty_source_after_baseline_stage_is_captured(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(native_home=self.args.native_tool_home,
                                       dirty_after='candidate-proof')
            record = MOD.run(self.args, command_runner=runner,
                             consequence_module=ConsequenceFake(), contract_module=ContractFake(), control_module=ControlFake())
        self.assertFalse(record['complete'])
        self.assertTrue(any('source changed' in error for error in record['errors']))

    def test_tool_identity_drift_is_detected(self):
        before = {'bin/verifast': {'regular': True, 'sha256': 'native', 'bytes': 1}}
        after = {'bin/verifast': {'regular': True, 'sha256': 'changed', 'bytes': 1}}
        with mock.patch.object(MOD, 'NATIVE_TOOL_HASHES', {'bin/verifast': 'native'}):
            self.assertTrue(MOD._validate_native_identities(before, after))

    def test_exception_writes_partial_snapshot_then_rethrows_same_type(self):
        with self.patched(), mock.patch.dict(os.environ, self.env, clear=True):
            runner = FakeCommandRunner(throw='source-preflight')
            with self.assertRaisesRegex(RuntimeError, 'injected stage exception'):
                MOD.run(self.args, command_runner=runner,
                        consequence_module=ConsequenceFake(), contract_module=ContractFake(), control_module=ControlFake())
        partial = json.loads((self.args.evidence / MOD.SUMMARY_REL).read_text())
        self.assertFalse(partial['complete'])
        self.assertIn('exception: RuntimeError', partial['errors'][0])


if __name__ == '__main__':
    unittest.main()
