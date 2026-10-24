import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
DRIVER_PATH = HERE / 'select-callee-r24-w4-contract-inputs.py'
REPO = HERE.parents[2]
spec = importlib.util.spec_from_file_location('contract_inputs_driver_test', DRIVER_PATH)
driver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def tool_rows(expected, *, binary_any=False):
    result = {}
    for rel, expected_sha in expected.items():
        actual = expected_sha if not (binary_any and rel == 'bin/verifast') else 'b' * 64
        result[rel] = {'regular': True, 'sha256': actual, 'bytes': 9,
                       'expected_sha256': expected_sha,
                       'matches': True}
    return result


class ContractInputsTests(unittest.TestCase):
    def test_expected_mode_uses_the_frozen_native_generator_api(self):
        generator = driver._load(REPO, driver.GENERATOR_REL, 'test_contract_generator', driver.GENERATOR_SHA256)
        self.assertEqual(driver.expected_mode(REPO)['native_mode'], generator.expected_mode())
        self.assertEqual(driver.expected_mode(REPO)['native_mode']['schema'], 'select-r24-w4-contract-inputs-mode-v1')
        self.assertFalse(driver.expected_mode(REPO)['accepted'])
        self.assertEqual(driver.expected_mode(REPO)['proof_credit'], 0)
        self.assertTrue(all(row['exit_code'] == driver.NATIVE_REFUSAL_EXIT == 2
                            for row in generator.expected_mode()['expected_results'].values()))

    def test_production_helper_api_and_sorted_header_manifest_shape(self):
        capture = driver._load(HERE, Path(driver.CAPTURE_REL.name), 'test_real_w4_capture', driver.CAPTURE_SHA256)
        stage = driver._load(REPO, driver.STAGE_RUNNER_REL, 'test_real_w4_stage', driver.STAGE_RUNNER_SHA256)
        manifest = driver._load_pinned_json(REPO, driver.HEADER_VARIANTS_REL, driver.HEADER_VARIANTS_SHA256)
        self.assertIn('stage_runner', __import__('inspect').signature(capture.collect).parameters)
        self.assertIn('stdout_name', __import__('inspect').signature(stage.run_stage).parameters)
        self.assertEqual(driver._header_variants(manifest), list(driver.CASES))

    def test_prerequisite_loader_with_real_pins_and_frozen_record_shapes(self):
        from types import SimpleNamespace
        import uuid

        def fixture():
            temp=tempfile.TemporaryDirectory(); root=Path(temp.name)
            repo=root/'proof-root'; work=root/'evidence'/'qualification-work'; native=root/'native-home'
            repo.mkdir(parents=True); work.mkdir(parents=True); native.mkdir()
            pinned=(driver.BOOTSTRAP_MODE_REL,driver.QUALIFIED_PROFILE_REL,driver.MANIFEST_REL,
                    driver.HEADER_VARIANTS_REL,driver.REFERENCE_HEADER_REL,driver.PATCH_REL,
                    driver.MODE_REL,driver.GENERATOR_REL)
            for rel in pinned:
                target=repo/rel; target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((REPO/rel).read_bytes())
            build=str(uuid.uuid4()); candidate='b'*40
            args=SimpleNamespace(repo=repo,evidence=work,native_tool_home=native,candidate=candidate,mode_file=repo/driver.MODE_REL)
            mode=driver._mode(args)
            matrix_rows={}
            for variant in driver.MATRIX_VARIANTS:
                classification=('POSITIVE_VERIFIED_SOURCE_REPORTED' if variant=='positive' else
                    'EXPECTED_SAME_SITE_TYPED_FAILURE' if variant in {'omit-selected-own','omit-unselected-own','no-retained-half'}
                    else 'EXPECTED_CALLEE_CONTRACT_REJECTION')
                matrix_rows[variant]={'variant':variant,'status':'COMPLETE','classification':classification,
                    'normal_unwind_nested_drop_gates':True,
                    'current_stage_observation':{'status':'RAN','argv':[str(native/'bin/verifast'),'-rustc_args',
                        '--edition 2021','-verbose','1','verified/lib.rs'],
                        'exit':0 if variant=='positive' else 1,'source_unchanged':True}}
            matrix={'schema':'r21-fractional-classified-proof-v1','complete':True,
                'variant_order':list(driver.MATRIX_VARIANTS),'current_build_id':build,
                'r24_session_phase_id':driver.R24_PHASE,'tool_home':str(native),'body_proof_run':True,
                'checked_pointer_outcomes_requested':True,'accepted':False,'proof_credit':False,
                'pins':{'base_original_sha256':driver.CONST_MATRIX_ORIGINAL_SHA256,
                        'base_verified_sha256':driver.CONST_MATRIX_BASE_VERIFIED_SHA256},'rows':matrix_rows}
            matrix_audit={'schema':'r21-fractional-proof-audit-v1','evidence_complete':True,
                'fractional_proof_status':'object','fractional_proof':matrix,'accepted':False,
                'verification_accepted':False,'proof_credit':False}
            work.mkdir(parents=True,exist_ok=True)
            (work/driver.MATRIX_SUMMARY_REL).parent.mkdir(parents=True,exist_ok=True)
            (work/driver.MATRIX_SUMMARY_REL).write_text(json.dumps(matrix))
            (work/driver.MATRIX_AUDIT_REL).write_text(json.dumps(matrix_audit))
            matrix_ref={'summary_path':driver.MATRIX_SUMMARY_REL.as_posix(),
                'summary_sha256':digest((work/driver.MATRIX_SUMMARY_REL).read_bytes()),
                'audit_path':driver.MATRIX_AUDIT_REL.as_posix(),
                'audit_sha256':digest((work/driver.MATRIX_AUDIT_REL).read_bytes()),
                'schema':matrix['schema'],'audit_schema':matrix_audit['schema'],
                'native_build_id':build,'native_tool_home':str(native),
                'variant_order':list(driver.MATRIX_VARIANTS),'all_eight_rows_complete':True}
            consequence={'schema':'select-r24-w4-const-consequence-v1','complete':True,
                'candidate':candidate,'native_build_id':build,'body_proof_run':True,
                'call_linkage':'UNKNOWN','accepted':False,'publication_allowed':False,
                'proof_credit':0,'const_matrix':matrix_ref}
            consequence_audit={'schema':'select-r24-w4-const-consequence-audit-v1',
                'complete':True,'evidence_complete':True,'summary':consequence,
                'accepted':False,'proof_credit':0}
            (work/driver.CONSEQUENCE_SUMMARY_REL).parent.mkdir(parents=True,exist_ok=True)
            (work/driver.CONSEQUENCE_SUMMARY_REL).write_text(json.dumps(consequence))
            (work/driver.CONSEQUENCE_AUDIT_REL).write_text(json.dumps(consequence_audit))
            qualification={'candidate':candidate,'build_id':build,'phase_id':driver.R24_PHASE,
                'route_phase_id':driver.R21_PHASE,'lane':driver.LANE,'profile':driver.PROFILE,
                'accepted':False,'publication_allowed':False,'proof_credit':0,'errors':[]}
            (work.parent/driver.QUALIFICATION_SUMMARY_NAME).write_text(json.dumps(qualification))
            env={'CLOUD_BUILD_ID':build}
            return temp,args,mode,matrix,matrix_audit,consequence,consequence_audit,env

        temp,args,mode,matrix,matrix_audit,consequence,consequence_audit,env=fixture()
        with temp:
            result=driver._load_prerequisites(args,mode,matrix,matrix_audit,consequence,consequence_audit,env)
            self.assertEqual(result['matrix_summary'],matrix)
            self.assertEqual(result['consequence_audit'],consequence_audit)
            with self.assertRaisesRegex(RuntimeError,'same-Build'):
                driver._load_prerequisites(args,mode,matrix,matrix_audit,consequence,consequence_audit,
                    {'CLOUD_BUILD_ID':str(uuid.uuid4())})
            with self.assertRaisesRegex(RuntimeError,'passed matrix summary'):
                driver._load_prerequisites(args,mode,None,matrix_audit,consequence,consequence_audit,env)
            (args.evidence/driver.MATRIX_SUMMARY_REL).write_text('null')
            with self.assertRaisesRegex(RuntimeError,'passed matrix summary'):
                driver._load_prerequisites(args,mode,matrix,matrix_audit,consequence,consequence_audit,env)

    def test_stage_status_preserves_explicit_failure_and_timeout_states(self):
        root = Path('/tmp')
        runner = lambda *a, **kw: {'exit': 0, 'status': 'NOT_RUN', 'skipped': 'not attempted'}
        result = driver._run_stage(runner, 'x', ['tool'], root, {}, {}, 1)
        self.assertEqual(result['status'], 'NOT_RUN')
        self.assertEqual(result['skipped'], 'not attempted')
        timed = driver._run_stage(lambda *a, **kw: {'exit': 124, 'status': 'TIMEOUT'}, 'x', ['tool'], root, {}, {}, 1)
        self.assertEqual(timed['status'], 'TIMEOUT')
        malformed = driver._run_stage(lambda *a, **kw: {'exit': 0, 'status': 'SUCCESS'}, 'x', ['tool'], root, {}, {}, 1)
        self.assertEqual(malformed['status'], 'SUCCESS')
        self.assertIn('malformed', malformed['errors'][0])

    def test_safe_json_writer_rejects_symlink_parent_before_creating_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            outside = root / 'outside'; outside.mkdir()
            link = root / 'link'; link.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(RuntimeError):
                driver._write_json(link / 'nested' / 'report.json', {'complete': False})
            self.assertFalse((outside / 'nested').exists())

    def _native_case(self, case='positive', *, marker=True, duplicate=False, status='RAN', exit_code=2):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        native = root / 'native'; native.mkdir()
        actual = b'let contract = actual\n'
        imported = actual if case == 'positive' else b'let contract = control\n'
        (native / 'actual-contract.ml').write_bytes(actual)
        (native / 'imported-contract.ml').write_bytes(imported)
        values = {
            'caller_source': (b'caller source', str(root / 'verified/lib.rs')),
            'callee_source': (b'callee source', str(root / 'callee/lib.rs')),
            'callee_source_in_mir': (b'callee source', str(root / 'callee/lib.rs')),
            'callee_unit': (b'unit', str(root / 'callee/unit.marshal')),
            'callee_body': (b'body', str(root / 'callee/body.marshal')),
            'reference_header': (b'reference header', str(root / 'reference.rsspec')),
            'variant_header': (b'variant header', str(root / 'variant.rsspec')),
            'qualified_profile': (b'profile', str(root / 'profile.json')),
        }
        expected = {}
        facts_inputs = {}
        for key, (raw, path) in values.items():
            expected[key] = (digest(raw), len(raw))
            facts_inputs[key] = {'path': path, 'bytes': len(raw), 'sha256': digest(raw)}
        expected['caller_unit'] = (driver.CALLER_UNIT_SHA256, 271019)
        expected['caller_body'] = (driver.CALLER_BODY_SHA256, 262129)
        facts_inputs['caller_unit'] = {'origin': 'native_input', 'bytes': 271019, 'sha256': driver.CALLER_UNIT_SHA256}
        facts_inputs['caller_body'] = {'origin': 'native_input', 'bytes': 262129, 'sha256': driver.CALLER_BODY_SHA256}
        # Physical records need not point at fixture paths for this validator-level synthetic.
        for key in ('caller_source', 'callee_source', 'callee_source_in_mir', 'callee_unit', 'callee_body',
                    'reference_header', 'variant_header', 'qualified_profile'):
            path = Path(facts_inputs[key]['path'])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(values[key][0])
        out = ('SORT4-R24-W4-CONTRACT-INPUTS: case=positive actual_spec_sha256=' + digest(actual) +
               ' imported_spec_sha256=' + digest(imported) + ' caller_body_sha256=' + driver.CALLER_BODY_SHA256 +
               ' typed_call_linkage=UNKNOWN\n') if marker else 'unrecognized output\n'
        if duplicate: out += out
        err = 'Fatal error: exception Failure("' + driver.NATIVE_REFUSAL_PREFIX + driver.CASE_REFUSAL[case] + '")\n'
        (root / 'out.log').write_text(out)
        (root / 'err.log').write_text(err)
        stage = {'status': status, 'exit': exit_code, 'stdout': 'out.log', 'stderr': 'err.log',
                 'argv': ['verifast'], 'fixture_integrity': True,
                 'fixture_before': {'verified/lib.rs':driver.SOURCE_SHA256},
                 'fixture_after': {'verified/lib.rs':driver.SOURCE_SHA256}}
        facts = {'schema': driver.SCHEMA, 'case': case, 'complete': True,
                 'classification': driver.EXPECTED_CASE_CLASS[case],
                 'expected_refusal': 'contract inputs matched; no proof rule admitted' if case == 'positive' else 'exact pinned control contract rejected',
                 'inputs': facts_inputs,
                 'actual_contract': {'path': 'actual-contract.ml', 'bytes': len(actual), 'sha256': digest(actual)},
                 'imported_contract': {'path': 'imported-contract.ml', 'bytes': len(imported), 'sha256': digest(imported)},
                 'typed_call_navigation_sha256': driver.TYPED_CALL_NAVIGATION_SHA256,
                 'typed_call_site_count_source_reported': 8, 'typed_call_linkage': 'UNKNOWN',
                 'caller_body_proof_admission': False, 'accepted': False, 'publication_allowed': False, 'proof_credit': 0}
        (native / 'contract-inputs.json').write_text(json.dumps(facts))
        before = tool_rows(driver.SOURCE_TOOL_HASHES)
        after = tool_rows(driver.SOURCE_TOOL_HASHES)
        before['bin/verifast'] = after['bin/verifast'] = {'regular': True, 'sha256': 'a'*64, 'bytes': 99,
            'expected_sha256': 'DIAGNOSTIC_BUILD_OUTPUT_RECORDED', 'matches': True}
        return temp, root, {'path': str(root / 'variant.rsspec'), 'bytes': 15, 'sha256': digest(b'variant header')}, stage, before, after, expected

    def test_positive_native_payload_matches_exact_source_reported_boundary(self):
        temp, root, header, stage, before, after, expected = self._native_case()
        with temp:
            facts, errors = driver._validate_native_facts('positive', root, header, stage, before, after,
                                                         expected, '00000000-0000-4000-8000-000000000001',
                                                         require_binary_stable='a'*64)
        self.assertEqual(errors, [])
        self.assertFalse(facts['accepted'])
        self.assertEqual(facts['proof_credit'], 0)

    def test_native_wrong_marker_duplicate_marker_and_not_run_fail_closed(self):
        for kwargs in ({'marker': False}, {'duplicate': True}, {'status': 'NOT_RUN'}):
            temp, root, header, stage, before, after, expected = self._native_case(**kwargs)
            with temp:
                _, errors = driver._validate_native_facts('positive', root, header, stage, before, after,
                                                          expected, '00000000-0000-4000-8000-000000000001',
                                                          require_binary_stable='a'*64)
            self.assertTrue(errors)

    def test_only_integer_refusal_exit2_accepts_otherwise_valid_native_facts(self):
        temp, root, header, stage, before, after, expected = self._native_case()
        with temp:
            for exit_code in (1, 0, 124, 137, None, False, 2.0, '2'):
                stage['exit'] = exit_code
                _, errors = driver._validate_native_facts(
                    'positive', root, header, stage, before, after, expected,
                    '00000000-0000-4000-8000-000000000001', require_binary_stable='a'*64)
                self.assertEqual(errors, [
                    'native diagnostic stage was not RAN with the expected refusal exit'],
                    repr(exit_code))

    def test_wrong_facts_type_and_missing_native_outputs_fail_closed(self):
        temp, root, header, stage, before, after, expected = self._native_case()
        with temp:
            (root / 'native' / 'contract-inputs.json').write_text('null')
            _, errors = driver._validate_native_facts('positive', root, header, stage, before, after,
                                                      expected, '00000000-0000-4000-8000-000000000001')
        self.assertTrue(errors)

    def test_full_run_then_read_only_audit_with_fake_stages_and_partial_failure(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        import shutil
        import uuid

        def execute(native_exit=2):
            temp = tempfile.TemporaryDirectory()
            base = Path(temp.name)
            repo, cloud, evidence, frozen, bootstrap, sysroot = [base / n for n in
                ('repo', 'cloud', 'evidence', 'frozen', 'bootstrap', 'sysroot')]
            for p in (repo, cloud, evidence, sysroot): p.mkdir()
            rels = sorted(set(driver.TOOL_HASHES) | set(driver.FROZEN_TOOL_HASHES_8A))
            base_hashes = {}; frozen_hashes = {}
            base_translator = b'bootstrap translator'
            patched_translator = b'patched diagnostic translator'
            frozen_translator = b'frozen 8a translator'
            for rel in rels:
                if rel == 'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':
                    raw = base_translator
                    frozen_raw = frozen_translator
                elif rel == 'bin/verifast':
                    raw = b'bootstrap verifier'
                    frozen_raw = b'frozen verifier'
                else:
                    raw = frozen_raw = ('tool:' + rel).encode()
                for home, value in ((bootstrap, raw), (frozen, frozen_raw)):
                    path = home / rel; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(value)
                if rel in driver.TOOL_HASHES: base_hashes[rel] = digest(raw)
                if rel in driver.FROZEN_TOOL_HASHES_8A: frozen_hashes[rel] = digest(frozen_raw)
            source_hashes = dict(base_hashes)
            source_hashes['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'] = digest(patched_translator)
            source_hashes.pop('bin/verifast')
            frozen_source = dict(frozen_hashes)
            patchfile = repo / driver.PATCH_REL; patchfile.parent.mkdir(parents=True, exist_ok=True); patchfile.write_bytes(b'patch')
            ref_bytes = b'R' * 384
            ref = repo / driver.REFERENCE_HEADER_REL; ref.parent.mkdir(parents=True, exist_ok=True); ref.write_bytes(ref_bytes)
            profile_bytes = b'profile-record'
            profile = repo / driver.QUALIFIED_PROFILE_REL; profile.parent.mkdir(parents=True, exist_ok=True); profile.write_bytes(profile_bytes)
            (repo / driver.MODE_REL).parent.mkdir(parents=True, exist_ok=True)
            (repo / driver.MODE_REL).write_text('{}')
            (repo / driver.CAPTURE_MODE_REL).parent.mkdir(parents=True, exist_ok=True)
            (repo / driver.CAPTURE_MODE_REL).write_text('{}')
            (repo / driver.BOOTSTRAP_MODE_REL).parent.mkdir(parents=True, exist_ok=True)
            (repo / driver.BOOTSTRAP_MODE_REL).write_text('{}')
            callee_dir=evidence/'cases/r21-fractional-proof/variants/positive/nine-body-a1-owned-forget'
            callee_dir.mkdir(parents=True, exist_ok=True)
            original=b'original'; verified=b'verified'; callee_source_raw=b'callee source'
            callee_unit_raw=b'callee unit'; callee_body_raw=b'callee body'
            (callee_dir/'verified').mkdir(); (callee_dir/'verified/lib.rs').write_bytes(callee_source_raw)
            (callee_dir/'actual-nested-9-unit.marshal').write_bytes(callee_unit_raw)
            (callee_dir/'actual-nested-9-body-7.marshal').write_bytes(callee_body_raw)
            test_constants={
                'SOURCE_SHA256':digest(verified), 'ORIGINAL_SHA256':digest(original),
                'CALLEE_SOURCE_SHA256':digest(callee_source_raw), 'CALLEE_UNIT_SHA256':digest(callee_unit_raw),
                'CALLEE_BODY_SHA256':digest(callee_body_raw), 'BOOTSTRAP_SOURCE_SHA256':digest(base_translator),
                'PATCHED_SOURCE_SHA256':digest(patched_translator), 'REFERENCE_HEADER_SHA256':digest(ref_bytes),
                'QUALIFIED_PROFILE_SHA256':digest(profile_bytes), 'CALLER_UNIT_SHA256':'1'*64,
                'CALLER_BODY_SHA256':'2'*64,
            }
            modes = driver.CASES
            header_manifest={'cases':{k:{'sha256':digest(('header:'+k).encode()),'bytes':len(('header:'+k).encode())} for k in modes}}
            matrix={'rows':{'positive':{'current_stage_observation':{'source_unchanged':True}}}}
            prereq={'matrix_summary':matrix,'header_manifest':header_manifest}
            class Capture:
                SUMMARY_REL=Path('W4-CAPTURE.json')
                def collect(self, a, *, stage_runner):
                    (a.evidence/'fixture/original').mkdir(parents=True, exist_ok=True)
                    (a.evidence/'fixture/verified').mkdir(parents=True, exist_ok=True)
                    (a.evidence/'fixture/original/lib.rs').write_bytes(original)
                    (a.evidence/'fixture/verified/lib.rs').write_bytes(verified)
                    report={'complete':True,'candidate':a.candidate,'proof_credit':0,
                            'call_linkage_status':'UNKNOWN','source':{'fixture_paths':
                                {'original':'fixture/original/lib.rs','verified':'fixture/verified/lib.rs'}},
                            'mir':{'normal':{},'readonly':{}}}
                    (a.evidence/self.SUMMARY_REL).write_text(json.dumps(report))
                    self.report=report
                    return report
                def audit(self,a):
                    return {'evidence_complete':True,'accepted':False,'proof_credit':0}
            capture=Capture()
            def fake_header(args, case, manifest): return ('header:'+case).encode()
            def write_header(args, case_root, case, manifest):
                raw=fake_header(args,case,manifest); driver._safe_create_tree(case_root)
                path=case_root/'r24-select.rsspec'; path.write_bytes(raw)
                return {'path':str(path.resolve()),'relative_path':str(path.relative_to(args.evidence)),
                        'bytes':len(raw),'sha256':digest(raw)}
            mir_result={'complete':True,'status':'COMPLETE_TYPED_MIR_OBSERVATION',
                        'typed_call_linkage':'UNKNOWN','typed_callee_family_observation':'OBSERVED_STRUCTURAL_MIR_CALLS'}
            def check_capture(*a, **k): return ({'fresh_typed_mir_observation':mir_result},[])
            def fake_mir(*a, **k): return mir_result
            def fake_runner(name, argv, root, env, hashes, deadline, cap, *, stdin_name=None, stdout_name=None):
                if name=='contract-tool-copy': shutil.copytree(Path(argv[-2]),Path(argv[-1]))
                if name=='contract-tool-patch-apply':
                    (Path(driver.NATIVE_HOME)/'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml').write_bytes(patched_translator)
                if name.startswith('contract-input-'):
                    case=name.removeprefix('contract-input-'); nd=Path(env[driver.NATIVE_ENV_PREFIX+'EVIDENCE_DIR'])
                    header_path=Path(env[driver.NATIVE_ENV_PREFIX+'REFERENCE_HEADER'])
                    ref_header=Path(env[driver.NATIVE_ENV_PREFIX+'REFERENCE_HEADER'])
                    variant_header=Path(env[driver.NATIVE_ENV_PREFIX+'EVIDENCE_DIR']).parent/'r24-select.rsspec'
                    # header path is passed in argv; it is one directory above native/.
                    variant_header=Path(argv[argv.index('-extern_spec')+1].split('=',1)[1])
                    actual=b'contract '+case.encode(); imported=actual if case=='positive' else b'different contract'
                    (nd/'actual-contract.ml').write_bytes(actual); (nd/'imported-contract.ml').write_bytes(imported)
                    inputs={}
                    def file_record(key,path,raw): inputs[key]={'path':str(path.resolve()),'bytes':len(raw),'sha256':digest(raw)}
                    caller=(root/'verified/lib.rs').read_bytes(); file_record('caller_source',root/'verified/lib.rs',caller)
                    file_record('callee_source',callee_dir/'verified/lib.rs',callee_source_raw)
                    file_record('callee_source_in_mir',callee_dir/'verified/lib.rs',callee_source_raw)
                    file_record('callee_unit',callee_dir/'actual-nested-9-unit.marshal',callee_unit_raw)
                    file_record('callee_body',callee_dir/'actual-nested-9-body-7.marshal',callee_body_raw)
                    file_record('reference_header',ref,ref_bytes)
                    vraw=variant_header.read_bytes(); file_record('variant_header',variant_header,vraw)
                    file_record('qualified_profile',profile,profile_bytes)
                    inputs['caller_unit']={'origin':'native_input','bytes':271019,'sha256':test_constants['CALLER_UNIT_SHA256']}
                    inputs['caller_body']={'origin':'native_input','bytes':262129,'sha256':test_constants['CALLER_BODY_SHA256']}
                    facts={'schema':driver.SCHEMA,'case':case,'complete':True,
                           'classification':driver.EXPECTED_CASE_CLASS[case],
                           'expected_refusal':'contract inputs matched; no proof rule admitted' if case=='positive' else 'exact pinned control contract rejected',
                           'inputs':inputs,'actual_contract':{'path':'actual-contract.ml','bytes':len(actual),'sha256':digest(actual)},
                           'imported_contract':{'path':'imported-contract.ml','bytes':len(imported),'sha256':digest(imported)},
                           'typed_call_navigation_sha256':driver.TYPED_CALL_NAVIGATION_SHA256,
                           'typed_call_site_count_source_reported':8,'typed_call_linkage':'UNKNOWN',
                           'caller_body_proof_admission':False,'accepted':False,'publication_allowed':False,'proof_credit':0}
                    (nd/'contract-inputs.json').write_text(json.dumps(facts))
                    marker=(f"SORT4-R24-W4-CONTRACT-INPUTS: case={case} actual_spec_sha256={digest(actual)} "
                            f"imported_spec_sha256={digest(imported)} caller_body_sha256={test_constants['CALLER_BODY_SHA256']} typed_call_linkage=UNKNOWN\n")
                    refusal=driver.CASE_REFUSAL[case]
                    stderr=f'Fatal error: exception Failure("{driver.NATIVE_REFUSAL_PREFIX}{refusal}")\n'
                    (root/'native.stdout.log').write_text(marker)
                    (root/'native.stderr.log').write_text(stderr)
                    out_name='native.stdout.log'; err_name='native.stderr.log'; code=native_exit
                else:
                    out_name=(stdout_name or name+'.stdout.log'); err_name=name+'-stderr.log'; code=0
                    (root/out_name).write_text('ok\n'); (root/err_name).write_text('')
                before={rel:digest((root/rel).read_bytes()) for rel in hashes}
                after=dict(before)
                return {'exit':code,'argv':argv,'fixture_before':before,'fixture_after':after,
                        'fixture_integrity':before==hashes==after,'stdout':out_name,'stderr':err_name}
            args=SimpleNamespace(repo=repo,cloud_dir=cloud,evidence=evidence,tool_home=frozen,
                native_tool_home=bootstrap,schema=frozen/'src/rust_frontend/vf_mir/vf_mir.capnp',
                compiler_sysroot=sysroot,mode_file=repo/driver.MODE_REL,capture_mode_file=repo/driver.CAPTURE_MODE_REL,
                const_mode_file=repo/'const-mode.json',deadline_epoch=4102444800,candidate='a'*40,
                output=None,runner_exit=0,failed_stage='complete')
            env={'CLOUD_BUILD_ID':str(uuid.uuid4()),'SMALLSORT_EXECUTION_PROVIDER':'cloud-build',
                 driver.R24_ENV:driver.R24_PHASE,driver.R21_ENV:driver.R21_PHASE,
                 'SORT4_SELECT_PROFILE':driver.PROFILE,'LANE':driver.LANE}
            patches={}
            patches.update(test_constants)
            patches.update({'TOOL_HASHES':base_hashes,'FROZEN_TOOL_HASHES_8A':frozen_hashes,
                            'SOURCE_TOOL_HASHES':source_hashes,'PATCHED_TOOL_HASHES':{**base_hashes,**{'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml':digest(patched_translator)}},
                            'MODE_SHA256':'1'*64,'NATIVE_HOME':base/'diagnostic-home','WORKSPACE_ROOT':base})
            with patch.multiple(driver, **patches), \
                 patch.object(driver,'_mode',return_value={}), \
                 patch.object(driver,'_load_prerequisites',return_value=prereq), \
                 patch.object(driver,'_check_capture_and_input_files',side_effect=check_capture), \
                 patch.object(driver,'_check_mir_calls',side_effect=fake_mir), \
                 patch.object(driver,'_write_case_header',side_effect=write_header), \
                 patch.object(driver,'_case_header_bytes',side_effect=fake_header), \
                 patch.object(driver,'_source_path',side_effect=lambda a, rel, expected: (a.evidence/rel,(a.evidence/rel).read_bytes())):
                result=driver.run(args,const_matrix_summary={},const_matrix_audit={},
                    consequence_summary={},consequence_audit={},stage_runner=fake_runner,
                    capture_module=capture,mir_module=object(),env=env)
                self.assertEqual(result['complete'],native_exit==2, (result['errors'], result.get('bootstrap_tool_hashes_after',{}).get('bin/verifast')))
                args.output=result['evidence_root'] and (evidence/driver.AUDIT_REL)
                audit=driver.audit(args,const_matrix_summary={},const_matrix_audit={},
                    consequence_summary={},consequence_audit={},stage_runner=fake_runner,
                    capture_module=capture,mir_module=object(),env=env)
                self.assertEqual(audit['evidence_complete'],native_exit==2, audit['errors'])
                self.assertFalse(audit['accepted'])
                self.assertEqual(audit['proof_credit'],0)
            temp.cleanup()

        execute(native_exit=2)
        execute(native_exit=124)


if __name__ == '__main__':
    unittest.main()
