#!/usr/bin/env python3
"""Run and audit the refusal-only W4 external-contract input diagnostic.

The driver builds a separate copy of the qualified bootstrap tool, performs a
fresh source/MIR capture, then runs six closed contract header cases. The
patched native route always refuses before body proof; no result admits a
caller body or receives proof credit.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid
from typing import Any, Callable


SCHEMA = 'select-r24-w4-contract-inputs-v1'
SUMMARY_REL = Path('cases/r24-w4-contract-inputs/W4-CONTRACT-INPUTS.json')
AUDIT_REL = Path('cases/r24-w4-contract-inputs/W4-CONTRACT-INPUTS-AUDIT.json')
ROOT_REL = SUMMARY_REL.parent
MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONTRACT-INPUTS-MODE.json')
MODE_SHA256 = '383a53b7f58571a1c439970e654cb08599091af17ae4ed93dd142ff3a9380204'
MANIFEST_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONTRACT-INPUT-MANIFEST.json')
MANIFEST_SHA256 = 'c1bb294644c2befbb9b511266106ba547ab4bfc6a83781d12a511a93e3698498'
GENERATOR_REL = Path('research/challenge-8/task-history/select-callee-r24/w4-contract-input-diagnostic.py')
GENERATOR_SHA256 = 'cc54516f98979a89b3dc922604e810b5c09f9daf40eb371cf2f1f0159cee1339'
PATCH_REL = Path('research/challenge-8/cloud-build/sort4-caller-entry-native/w4-contract-input-r24.patch')
PATCH_SHA256 = '6c8cb345ebc11945f5624f6468732d9f0feb38294c7c73d48b0c748d2b4e03dc'
HEADER_VARIANTS_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONTRACT-HEADER-VARIANTS.json')
HEADER_VARIANTS_SHA256 = '5d0ef2f5dabee2d1a3056855154327cd2b57d26919cb9cf068be34f2d8764a56'
REFERENCE_HEADER_REL = Path('research/challenge-8/cloud-build/sort4-caller-entry-native/w4-select-callee-r24.rsspec')
REFERENCE_HEADER_SHA256 = 'a699492f945c544cb525f7ec1cc54b461f6472b25f7b085d2325811179a93c82'
QUALIFIED_PROFILE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CONST-NATIVE-QUALIFICATION.json')
QUALIFIED_PROFILE_SHA256 = 'a826753d75bbc154d64216e8de6e90ddc10c4b78f8e34b475cca37325d1cf24d'
BOOTSTRAP_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-BOOTSTRAP-QUALIFIED-MODE.json')
BOOTSTRAP_MODE_SHA256 = 'b633c38b1d91d3e016b96dee2833d1bd9823f919526635feb67f2ac0ea920b12'
CAPTURE_MODE_REL = Path('research/challenge-8/task-history/select-callee-r24/W4-CAPTURE-MODE.json')
CAPTURE_MODE_SHA256 = '1d251b0d1a48ec1c3310e9ae179f7a750b8608ec57c31a4da3b46ce6e12fe0a3'
CAPTURE_REL = Path('research/challenge-8/cloud-build/select-callee-r24-w4-capture.py')
CAPTURE_SHA256 = '8f3c8bddd385754aeaa4b784f3273a56e6af2f5356658c4df3d50f7c519f812d'
STAGE_RUNNER_REL = Path('research/challenge-8/overnight-sort4/capture.py')
STAGE_RUNNER_SHA256 = '0d993e8c36cb7684eb509e8efcfb9553b07e92e87885f4ae430269c4cb2a6060'
MIR_CALLS_REL = Path('research/challenge-8/cloud-build/select-callee-r24-w4-mir-calls.py')
MIR_CALLS_SHA256 = '024004290c45a4fa53e20db0f6f1e0eb7227c7eb0a433dce77b1e81407172928'
QUALIFICATION_SUMMARY_NAME = 'W4-CONST-QUALIFICATION.json'
QUALIFICATION_AUDIT_NAME = 'W4-CONST-QUALIFICATION-AUDIT.json'
MATRIX_SUMMARY_REL = Path('cases/r21-fractional-proof/r21-fractional-proof.json')
MATRIX_AUDIT_REL = Path('const-regression-audit.json')
CONSEQUENCE_SUMMARY_REL = Path('cases/r24-w4-const-consequence/W4-CONST-CONSEQUENCE.json')
CONSEQUENCE_AUDIT_REL = Path('cases/r24-w4-const-consequence/W4-CONST-CONSEQUENCE-AUDIT.json')
MATRIX_VARIANTS = (
    'positive', 'omit-selected-own', 'omit-unselected-own', 'no-retained-half',
    'callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss',
    'callee-thread-duplicate',
)
CONST_MATRIX_ORIGINAL_SHA256 = '466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5'
CONST_MATRIX_BASE_VERIFIED_SHA256 = '1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6'
CASES = ('positive', 'false-normal', 'false-unwind', 'duplicate-thread',
         'mut-pointer', 'extra-declaration')
EXPECTED_CASE_CLASS = {
    'positive': 'INPUTS_MATCH',
    'false-normal': 'EXPECTED_INPUT_REFUSAL',
    'false-unwind': 'EXPECTED_INPUT_REFUSAL',
    'duplicate-thread': 'EXPECTED_INPUT_REFUSAL',
    'mut-pointer': 'EXPECTED_INPUT_REFUSAL',
    'extra-declaration': 'EXPECTED_INPUT_REFUSAL',
}
CASE_REFUSAL = {
    'positive': 'contract inputs matched; no proof rule admitted',
    **{name: 'pinned control contract refused; no proof rule admitted'
       for name in CASES if name != 'positive'},
}
NATIVE_PREFIX = 'SORT4-R24-W4-CONTRACT-INPUTS:'
NATIVE_REFUSAL_PREFIX = NATIVE_PREFIX + ' diagnostic refusal: '
NATIVE_ENV_PREFIX = 'SORT4_R24_W4_CONTRACT_'
NATIVE_HOME = Path('/workspace/smallsort-work/r24-w4-contract-input-tool')
WORKSPACE_ROOT = Path('/workspace')
R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
R24_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R21_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
LANE = 'o26-select-callee-r20'
PROFILE = 'experimental-s6-26.10-v1'
BOOTSTRAP_SOURCE_SHA256 = '5170c56386f092d55a42251594eb4b080073f58828cbe1dcf44053b5bdc99942'
PATCHED_SOURCE_SHA256 = 'f83bd98b5d466314782e47ddc2d80356a0d0736b6cfc03ade59409eb01313806'
SOURCE_SHA256 = 'e3fb9d257609d07b8a54afd135d219e6f531fa274364b9671f87e07e93d0d663'
ORIGINAL_SHA256 = 'b4b0070e224cc60eba58a2116c0009fdda2e3ae599c67344194a709215a374db'
CALLEE_SOURCE_SHA256 = '687327ca06d076d9bf3528859109ff5fc93b21b9cbbab7834d64edac93fbeaff'
CALLEE_UNIT_SHA256 = 'cc6292e0683b62b8457267f2963bfb29901d0a5492fa10933c0be9cb2f674925'
CALLEE_BODY_SHA256 = 'd370bf5eeeaf553ba450d3add562b85f46673bbac21c249b439ef126443bbb08'
CALLER_UNIT_SHA256 = 'b711429f889c6e36393272c29fcc9c4e50fe75beb2ffe2d048ffc424b4325c83'
CALLER_BODY_SHA256 = '067c11f2b290d462d5a203678d069abe53ceffed6362a6ba4cd47035fa81a67e'
TYPED_CALL_NAVIGATION_SHA256 = '8d797805c256370660d23b3d725bfefec2ece548a4ca766c2d0ede4b25d9a375'
TOOL_HASHES = {
    'bin/refinement-checker': 'b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28',
    'bin/rust/std/lib.rsspec': 'd33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf',
    'bin/rust/rust_belt/general.rsspec': 'ef2ff16dffd472bbc5fd7fa17e7f13a03d83919520da5ce7e2d7095194790d1d',
    'bin/verifast': '33b693fa92790864db503fa69657e572fd2699350e6c7e1b4b2ffc3998108fe0',
    'bin/vf-rust-mir-exporter': 'b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796',
    'src/frontend/ocaml_expr_of_ast.ml': 'f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94',
    'src/rust_frontend/vf_mir/vf_mir.capnp': 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469',
    'src/rust_frontend/vf_mir_translator/rust_parser.ml': '6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246',
    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': BOOTSTRAP_SOURCE_SHA256,
}
FROZEN_TOOL_HASHES_8A = {
    'bin/refinement-checker': 'b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28',
    'bin/rust/std/lib.rsspec': 'd33b2a7a284557002b4f7afe3d5e63f813e51f818c588712d743b4b46f9bedaf',
    'bin/verifast': '01eaa29335277643e2c16dd35b561e2aecee867fbdd64cf13b8eb1d082602cd6',
    'bin/vf-rust-mir-exporter': 'b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796',
    'src/frontend/ocaml_expr_of_ast.ml': 'f32f1a9abd3f31c211b3ac633eca130e3298ab6e8fe39e5b489c69401efc1f94',
    'src/rust_frontend/vf_mir/vf_mir.capnp': 'f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469',
    'src/rust_frontend/vf_mir_translator/rust_parser.ml': '6a866aa5d469a1677ae1ac1bcdd675e4c059dcde449872b9cd1700d4b2e51246',
    'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml': '8a0260169bd2345070755e268edb640eaa4f02c261bef3330d7b33698e4ce007',
}
PATCHED_TOOL_HASHES = dict(TOOL_HASHES)
PATCHED_TOOL_HASHES['src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'] = PATCHED_SOURCE_SHA256
SOURCE_TOOL_HASHES = {k: v for k, v in PATCHED_TOOL_HASHES.items() if k != 'bin/verifast'}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError('R24-W4-CONTRACT-INPUTS: ' + message)


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def _json(path: Path) -> object:
    try:
        if path.is_symlink() or not path.is_file():
            return None
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None


def _safe_root(root: Path, *, create: bool = False) -> Path:
    absolute = Path(os.path.abspath(root))
    if root.exists() or root.is_symlink():
        need(root.resolve() == absolute and root.is_dir() and not root.is_symlink(),
             'evidence root missing/unsafe or aliases another directory')
    elif create:
        _safe_create_tree(root)
    else:
        raise RuntimeError('R24-W4-CONTRACT-INPUTS: evidence root is missing')
    need(root.resolve() == absolute, 'evidence root resolved outside expected path')
    return absolute


def _safe_create_tree(path: Path) -> None:
    absolute=Path(os.path.abspath(path))
    missing=[]; cursor=path
    while not cursor.exists() and not cursor.is_symlink():
        missing.append(cursor); cursor=cursor.parent
    need(cursor.exists() and cursor.is_dir() and not cursor.is_symlink() and
         cursor.resolve()==Path(os.path.abspath(cursor)),
         'nearest existing directory is missing/unsafe')
    for directory in reversed(missing):
        parent=directory.parent
        need(parent.resolve()==Path(os.path.abspath(parent)) and parent.is_dir() and not parent.is_symlink(),
             'directory ancestor is symlinked or aliased')
        directory.mkdir(exist_ok=False)
        need(directory.is_dir() and not directory.is_symlink() and
             directory.resolve()==Path(os.path.abspath(directory)),
             'directory creation escaped or aliased')
    need(path.resolve()==absolute and path.is_dir() and not path.is_symlink(),
         'created directory is unsafe')


def _contained_file(root: Path, relative: str | Path) -> tuple[bytes, Path]:
    rel = Path(relative)
    need(not rel.is_absolute() and '..' not in rel.parts,
         'artifact path is absolute or escapes evidence root')
    path = root / rel
    absolute_root = Path(os.path.abspath(root))
    need(path.resolve() == absolute_root / rel and path.resolve().is_relative_to(absolute_root) and
         not path.is_symlink() and path.is_file(),
         'artifact missing, symlinked, or outside evidence root: ' + str(rel))
    return path.read_bytes(), path


def _write_json(path: Path, value: dict[str, Any], *, overwrite: bool = False) -> None:
    parent = path.parent
    absolute_parent=Path(os.path.abspath(parent))
    missing=[]; cursor=parent
    while not cursor.exists() and not cursor.is_symlink():
        missing.append(cursor); cursor=cursor.parent
    need(cursor.exists() and cursor.is_dir() and not cursor.is_symlink() and
         cursor.resolve()==Path(os.path.abspath(cursor)),
         'nearest existing JSON parent is missing/unsafe')
    for directory in reversed(missing):
        need(directory.parent.resolve()==Path(os.path.abspath(directory.parent)),
             'JSON parent chain is symlinked or aliased')
        directory.mkdir(exist_ok=False)
        need(directory.is_dir() and not directory.is_symlink() and
             directory.resolve()==Path(os.path.abspath(directory)),
             'JSON parent creation escaped or aliased')
    need(parent.resolve() == absolute_parent,
         'JSON output parent is symlinked or aliased')
    need(path.resolve()==Path(os.path.abspath(path)),
         'JSON output path is symlinked or aliased')
    if path.exists() or path.is_symlink():
        need(overwrite and path.is_file() and not path.is_symlink(),
             'JSON output already exists or is unsafe')
    temp = path.with_name(path.name + '.tmp')
    need(not temp.exists() and not temp.is_symlink(), 'JSON temp output already exists')
    raw = _canonical(value)
    fd=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
    with os.fdopen(fd,'wb') as f:
        f.write(raw); f.flush(); os.fsync(f.fileno())
    os.replace(temp, path)


def _load_pinned_json(repo: Path, rel: Path, expected: str) -> dict[str, Any]:
    path = repo / rel
    need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == expected,
         'pinned JSON missing or changed: ' + rel.as_posix())
    value = _json(path)
    need(type(value) is dict, 'pinned JSON has wrong type: ' + rel.as_posix())
    return value


def _load(repo: Path, rel: Path, module_name: str, expected: str):
    path = repo / rel
    need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == expected,
         'pinned module missing or changed: ' + rel.as_posix())
    spec = importlib.util.spec_from_file_location(module_name, path)
    need(spec is not None and spec.loader is not None, 'cannot load pinned module: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    need(sha(path.read_bytes()) == expected, 'pinned module changed during import')
    return module


def expected_mode(repository: Path | None = None) -> dict[str, Any]:
    """Return the canonical closed driver mode; its physical SHA is pinned separately."""
    repository=repository or Path(__file__).resolve().parents[3]
    generator=_load(repository,GENERATOR_REL,'r24_contract_mode_generator',GENERATOR_SHA256)
    generator_mode=generator.expected_mode()
    return {
        'schema': 'select-r24-w4-contract-inputs-driver-mode-v1',
        'native_mode': generator_mode,
        'native_mode_generator_path': GENERATOR_REL.as_posix(),
        'native_mode_generator_sha256': GENERATOR_SHA256,
        'native_manifest_path': MANIFEST_REL.as_posix(),
        'native_manifest_sha256': MANIFEST_SHA256,
        'native_patch_path': PATCH_REL.as_posix(), 'native_patch_sha256': PATCH_SHA256,
        'native_result_translator_sha256': PATCHED_SOURCE_SHA256,
        'bootstrap_mode_path': BOOTSTRAP_MODE_REL.as_posix(),
        'bootstrap_mode_sha256': BOOTSTRAP_MODE_SHA256,
        'qualified_profile_path': QUALIFIED_PROFILE_REL.as_posix(),
        'qualified_profile_sha256': QUALIFIED_PROFILE_SHA256,
        'capture_mode_path': CAPTURE_MODE_REL.as_posix(),
        'capture_mode_sha256': CAPTURE_MODE_SHA256,
        'capture_helper_path': CAPTURE_REL.as_posix(), 'capture_helper_sha256': CAPTURE_SHA256,
        'capture_stage_runner_path': STAGE_RUNNER_REL.as_posix(),
        'capture_stage_runner_sha256': STAGE_RUNNER_SHA256,
        'mir_calls_path': MIR_CALLS_REL.as_posix(), 'mir_calls_sha256': MIR_CALLS_SHA256,
        'header_variants_path': HEADER_VARIANTS_REL.as_posix(),
        'header_variants_sha256': HEADER_VARIANTS_SHA256,
        'reference_header_path': REFERENCE_HEADER_REL.as_posix(),
        'reference_header_sha256': REFERENCE_HEADER_SHA256,
        'bootstrap_tool_hashes': TOOL_HASHES,
        'frozen_capture_tool_hashes': FROZEN_TOOL_HASHES_8A,
        'tool_copy_path': str(NATIVE_HOME),
        'typed_call_linkage': 'UNKNOWN', 'caller_body_proof_admission': False,
        'accepted': False, 'publication_allowed': False, 'proof_credit': 0,
    }


def _route(args: argparse.Namespace, env: dict[str, str], *, live_deadline: bool) -> None:
    for name in ('repo','cloud_dir','evidence','tool_home','native_tool_home','schema',
                 'compiler_sysroot','mode_file','capture_mode_file','const_mode_file'):
        value = getattr(args, name, None)
        need(value is not None, 'required path argument missing: ' + name)
        setattr(args, name, Path(value).resolve())
    need(args.tool_home != args.native_tool_home and args.deadline_epoch > 0 and
         (not live_deadline or args.deadline_epoch > int(time.time())),
         'frozen/bootstrap tool homes or shared deadline invalid')
    need(args.repo.resolve().is_relative_to(WORKSPACE_ROOT) and
         args.cloud_dir.resolve().is_relative_to(WORKSPACE_ROOT) and
         args.evidence.resolve().is_relative_to(WORKSPACE_ROOT) and
         args.tool_home.resolve().is_relative_to(WORKSPACE_ROOT) and
         args.native_tool_home.resolve().is_relative_to(WORKSPACE_ROOT) and
         args.compiler_sysroot.resolve().is_relative_to(WORKSPACE_ROOT),
         'all Cloud driver paths must be within /workspace')
    need(re.fullmatch(r'[0-9a-f]{40}', str(args.candidate)) is not None,
         'candidate must be full current commit SHA')
    try:
        canonical_build = str(uuid.UUID(env.get('CLOUD_BUILD_ID', '')))
    except (ValueError, AttributeError, TypeError):
        raise RuntimeError('R24-W4-CONTRACT-INPUTS: current Cloud Build UUID missing/invalid')
    need(canonical_build == env.get('CLOUD_BUILD_ID') and
         env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         env.get(R24_ENV) == R24_PHASE and env.get(R21_ENV) == R21_PHASE and
         env.get('SORT4_SELECT_PROFILE') == PROFILE and env.get('LANE') == LANE and
         not env.get('GITHUB_ACTIONS'), 'exact R24/R21 Cloud route required')
    allowed = {R24_ENV, R21_ENV, 'SORT4_SELECT_PROFILE'}
    need(not any(k.startswith('SORT4_') and k not in allowed for k in env),
         'ambient SORT4 opt-in is forbidden')


def _mode(args: argparse.Namespace) -> dict[str, Any]:
    path = args.mode_file
    need(path == (args.repo / MODE_REL).resolve() and path.is_file() and
         not path.is_symlink() and MODE_SHA256 != 'PENDING' and
         sha(path.read_bytes()) == MODE_SHA256,
         'exact contract-input driver mode path/hash differs')
    try:
        mode = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError('R24-W4-CONTRACT-INPUTS: mode JSON invalid') from exc
    need(type(mode) is dict and mode == expected_mode(args.repo), 'contract-input mode contract differs')
    return mode


def _tool_hashes(home: Path, expected: dict[str, str], *, binary_any: bool = False) -> dict[str, Any]:
    result = {}
    for rel, expected_sha in expected.items():
        path = home / rel
        if path.is_symlink() or not path.is_file():
            result[rel] = {'regular': False, 'sha256': None, 'bytes': None}
            continue
        raw = path.read_bytes(); digest = sha(raw)
        result[rel] = {'regular': True, 'sha256': digest, 'bytes': len(raw),
                       'expected_sha256': expected_sha,
                       'matches': bool(len(raw)) and (binary_any and rel == 'bin/verifast' or digest == expected_sha)}
    return result


def _tool_identity_errors(value: object, expected: dict[str, str], *, binary_any: bool = False) -> list[str]:
    if type(value) is not dict or set(value) != set(expected):
        return ['tool identity inventory missing or has wrong shape']
    errors=[]
    for rel, digest in expected.items():
        row=value.get(rel)
        if type(row) is not dict or row.get('regular') is not True or row.get('bytes',0) <= 0:
            errors.append('tool file missing/unsafe: '+rel); continue
        if not (binary_any and rel=='bin/verifast') and row.get('sha256') != digest:
            errors.append('tool file SHA differs: '+rel)
        if row.get('matches') is not True:
            errors.append('tool file expected identity differs: '+rel)
    return errors


def _load_prerequisites(args: argparse.Namespace, mode: dict[str, Any],
                         matrix_summary: object, matrix_audit: object,
                         consequence_summary: object, consequence_audit: object,
                         env: dict[str, str]) -> dict[str, Any]:
    work = args.evidence
    physical_matrix = _json(work / MATRIX_SUMMARY_REL)
    physical_matrix_audit = _json(work / MATRIX_AUDIT_REL)
    physical_consequence = _json(work / CONSEQUENCE_SUMMARY_REL)
    physical_consequence_audit = _json(work / CONSEQUENCE_AUDIT_REL)
    need(type(physical_matrix) is dict and physical_matrix == matrix_summary,
         'passed matrix summary differs from physical R21 summary')
    need(type(physical_matrix_audit) is dict and physical_matrix_audit == matrix_audit,
         'passed matrix audit differs from physical R21 audit')
    need(type(physical_consequence) is dict and physical_consequence == consequence_summary,
         'passed consequence summary differs from physical summary')
    need(type(physical_consequence_audit) is dict and physical_consequence_audit == consequence_audit,
         'passed consequence audit differs from physical audit')
    build_id=env.get('CLOUD_BUILD_ID')
    need(physical_matrix.get('schema')=='r21-fractional-classified-proof-v1' and
         physical_matrix.get('complete') is True and
         physical_matrix.get('variant_order') == list(MATRIX_VARIANTS) and
         physical_matrix.get('current_build_id') == build_id and
         physical_matrix.get('r24_session_phase_id') == R24_PHASE and
         physical_matrix.get('tool_home') == str(args.native_tool_home) and
         physical_matrix.get('body_proof_run') is True and
         physical_matrix.get('checked_pointer_outcomes_requested') is True,
         'current same-Build full-eight matrix summary is incomplete or mismatched')
    pins=physical_matrix.get('pins')
    need(type(pins) is dict and pins.get('base_original_sha256')==CONST_MATRIX_ORIGINAL_SHA256 and
         pins.get('base_verified_sha256')==CONST_MATRIX_BASE_VERIFIED_SHA256,
         'R21 matrix frozen base source pair differs')
    rows=physical_matrix.get('rows')
    need(type(rows) is dict and set(rows)==set(MATRIX_VARIANTS), 'R21 matrix row inventory differs')
    for variant in MATRIX_VARIANTS:
        row=rows[variant]
        observation=row.get('current_stage_observation') if type(row) is dict else None
        expected_exit=0 if variant=='positive' else 1
        expected_class=('POSITIVE_VERIFIED_SOURCE_REPORTED' if variant=='positive' else
                        'EXPECTED_SAME_SITE_TYPED_FAILURE' if variant in
                        {'omit-selected-own','omit-unselected-own','no-retained-half'} else
                        'EXPECTED_CALLEE_CONTRACT_REJECTION')
        expected_argv=[str(args.native_tool_home/'bin/verifast'),'-rustc_args','--edition 2021',
                       '-verbose','1','verified/lib.rs']
        need(type(row) is dict and row.get('variant')==variant and row.get('status')=='COMPLETE' and
             row.get('classification')==expected_class and
             row.get('normal_unwind_nested_drop_gates') is True and
             type(observation) is dict and observation.get('status')=='RAN' and
             observation.get('argv')==expected_argv and
             observation.get('exit')==expected_exit and observation.get('source_unchanged') is True,
             'same-Build R21 matrix row incomplete/mismatched: '+variant)
    need(physical_matrix.get('accepted') is False and physical_matrix.get('proof_credit') is False,
         'R21 matrix claims acceptance/credit outside source-reported boundary')
    need(type(physical_matrix_audit) is dict and
         physical_matrix_audit.get('schema')=='r21-fractional-proof-audit-v1' and
         physical_matrix_audit.get('evidence_complete') is True and
         physical_matrix_audit.get('fractional_proof_status')=='object' and
         physical_matrix_audit.get('fractional_proof')==physical_matrix and
         physical_matrix_audit.get('accepted') is False and
         physical_matrix_audit.get('verification_accepted') is False and
         physical_matrix_audit.get('proof_credit') is False,
         'physical R21 matrix audit is incomplete or has unsafe boundary')
    need(physical_consequence.get('schema')=='select-r24-w4-const-consequence-v1' and
         physical_consequence.get('complete') is True and
         physical_consequence.get('candidate')==args.candidate and
         physical_consequence.get('native_build_id')==build_id and
         physical_consequence.get('body_proof_run') is True and
         physical_consequence.get('call_linkage')=='UNKNOWN' and
         physical_consequence.get('accepted') is False and
         physical_consequence.get('publication_allowed') is False and
         physical_consequence.get('proof_credit')==0,
         'same-Build ordinary consequence summary incomplete or boundary differs')
    matrix_ref=physical_consequence.get('const_matrix')
    need(type(matrix_ref) is dict and
         matrix_ref.get('summary_sha256')==sha((work/MATRIX_SUMMARY_REL).read_bytes()) and
         matrix_ref.get('audit_sha256')==sha((work/MATRIX_AUDIT_REL).read_bytes()) and
         matrix_ref.get('native_build_id')==build_id and
         matrix_ref.get('all_eight_rows_complete') is True,
         'ordinary consequence does not bind this exact fresh eight-row matrix')
    need(physical_consequence_audit.get('schema')=='select-r24-w4-const-consequence-audit-v1' and
         physical_consequence_audit.get('complete') is True and
         physical_consequence_audit.get('evidence_complete') is True and
         type(physical_consequence_audit.get('summary')) is dict and
         physical_consequence_audit['summary'].get('candidate')==args.candidate and
         physical_consequence_audit['summary'].get('native_build_id')==build_id and
         physical_consequence_audit.get('accepted') is False and
         physical_consequence_audit.get('proof_credit')==0,
         'same-Build consequence audit incomplete or boundary differs')
    qualification_path=work.parent/QUALIFICATION_SUMMARY_NAME
    qualification=_json(qualification_path)
    need(type(qualification) is dict and
         qualification.get('candidate')==args.candidate and qualification.get('build_id')==build_id and
         qualification.get('phase_id')==R24_PHASE and qualification.get('route_phase_id')==R21_PHASE and
         qualification.get('lane')==LANE and qualification.get('profile')==PROFILE and
         qualification.get('accepted') is False and
         qualification.get('publication_allowed') is False and
         qualification.get('proof_credit')==0 and not qualification.get('errors'),
         'outer current-Build qualification context/boundary differs')
    bootstrap_mode=_load_pinned_json(args.repo, BOOTSTRAP_MODE_REL, BOOTSTRAP_MODE_SHA256)
    need(bootstrap_mode.get('schema')=='select-r24-w4-const-qualification-mode-v1' and
         bootstrap_mode.get('accepted') is False and bootstrap_mode.get('independent_proof_credit')==0,
         'frozen bootstrap-qualified mode boundary differs')
    profile=_load_pinned_json(args.repo, QUALIFIED_PROFILE_REL, QUALIFIED_PROFILE_SHA256)
    need(profile.get('schema')=='select-r24-current-native-const-qualified-profile-v1' and
         profile.get('build_id')=='9984b5ac-b202-4f3a-995b-5e183e76c3d3' and
         profile.get('accepted') is True and profile.get('proof_credit')==0,
         'qualified bootstrap profile receipt differs')
    manifest=_load_pinned_json(args.repo, MANIFEST_REL, MANIFEST_SHA256)
    header_manifest=_load_pinned_json(args.repo, HEADER_VARIANTS_REL, HEADER_VARIANTS_SHA256)
    need(manifest.get('schema')=='select-r24-w4-contract-input-manifest-v1' and
         manifest.get('mode')==mode.get('native_mode') and
         manifest.get('result_translator_sha256')==PATCHED_SOURCE_SHA256 and
         manifest.get('patch',{}).get('sha256')==PATCH_SHA256 and
         manifest.get('native_inputs',{}).get('source_sha256')==SOURCE_SHA256 and
         manifest.get('native_inputs',{}).get('callee_unit_sha256')==CALLEE_UNIT_SHA256 and
         manifest.get('native_inputs',{}).get('callee_body_sha256')==CALLEE_BODY_SHA256,
         'native diagnostic manifest differs from mode/pins')
    patch=args.repo/PATCH_REL
    need(patch.is_file() and not patch.is_symlink() and sha(patch.read_bytes())==PATCH_SHA256,
         'native diagnostic patch missing or changed')
    header= args.repo/REFERENCE_HEADER_REL
    need(header.is_file() and not header.is_symlink() and sha(header.read_bytes())==REFERENCE_HEADER_SHA256,
         'positive external header missing or changed')
    return {'matrix_summary':physical_matrix,'matrix_audit':physical_matrix_audit,
            'consequence_summary':physical_consequence,'consequence_audit':physical_consequence_audit,
            'qualification_summary':qualification,'bootstrap_mode':bootstrap_mode,
            'qualified_profile':profile,'manifest':manifest,'header_manifest':header_manifest}


def _source_path(args: argparse.Namespace, relative: str, expected: str) -> tuple[Path, bytes]:
    path=args.evidence/relative
    need(not path.is_symlink() and path.is_file() and
         path.resolve().is_relative_to(args.evidence.resolve()),
         'required current matrix input missing/unsafe: '+relative)
    raw=path.read_bytes(); need(sha(raw)==expected,'required current matrix input hash differs: '+relative)
    return path.resolve(),raw


def _write_case_header(args: argparse.Namespace, case_root: Path, case: str,
                       header_manifest: dict[str, Any]) -> dict[str, Any]:
    result=_case_header_bytes(args,case,header_manifest)
    row=header_manifest['cases'][case]
    _safe_create_tree(case_root)
    path=case_root/'r24-select.rsspec'
    path.write_bytes(result)
    return {'path':str(path.resolve()),'relative_path':str(path.relative_to(args.evidence)),
            'bytes':len(result),'sha256':sha(result)}


def _case_header_bytes(args: argparse.Namespace, case: str,
                       header_manifest: dict[str, Any]) -> bytes:
    base_path=args.repo/REFERENCE_HEADER_REL
    need(base_path.is_file() and not base_path.is_symlink() and sha(base_path.read_bytes())==REFERENCE_HEADER_SHA256,
         'reference header changed while deriving case bytes')
    base=base_path.read_bytes()
    row=header_manifest.get('cases',{}).get(case)
    need(type(row) is dict,'closed header case missing: '+case)
    if case=='positive':
        result=base
    else:
        replacement=row.get('replacement')
        need(type(replacement) is dict and set(replacement)=={'from','to'},
             'header replacement missing/wrong type: '+case)
        old=replacement['from'].encode(); new=replacement['to'].encode()
        need(base.count(old)==1,'header replacement anchor is absent/ambiguous: '+case)
        result=base.replace(old,new,1)
    expected=row.get('sha256'); expected_bytes=row.get('bytes')
    need(type(expected) is str and type(expected_bytes) is int and
         sha(result)==expected and len(result)==expected_bytes,
         'generated header bytes differ from closed pin: '+case)
    return result


def _capture_fresh(args: argparse.Namespace, root: Path, stage_runner,
                   capture_module=None) -> dict[str, Any]:
    capture = capture_module or _load(args.cloud_dir,Path(CAPTURE_REL.name),'r24_w4_contract_capture',CAPTURE_SHA256)
    capture_root=root/'capture'
    capture_args=argparse.Namespace(**vars(args))
    capture_args.evidence=capture_root
    capture_args.tool_home=args.tool_home
    capture_args.schema=args.tool_home/'src/rust_frontend/vf_mir/vf_mir.capnp'
    capture_args.mode_file=args.repo/CAPTURE_MODE_REL
    capture_args.output=capture_root/'W4-CAPTURE-AUDIT.json'
    capture_args.runner_exit=0; capture_args.failed_stage='complete'
    def capture_stage(name, argv, fixture, stage_env, hashes, deadline, cap, stdin=None, stdout=None):
        return stage_runner(name, argv, fixture, stage_env, hashes, deadline, cap,
                            stdin_name=stdin, stdout_name=stdout)
    report=capture.collect(capture_args,stage_runner=capture_stage)
    need(type(report) is dict and report.get('complete') is True and
         report.get('candidate')==args.candidate and
         report.get('proof_credit')==0 and report.get('call_linkage_status')=='UNKNOWN',
         'fresh frozen W4 capture incomplete or boundary differs')
    audit=capture.audit(capture_args)
    need(type(audit) is dict and audit.get('evidence_complete') is True and
         audit.get('accepted') is False and audit.get('proof_credit')==0,
         'fresh W4 capture physical audit incomplete')
    return {'report':report,'audit':audit,'module':capture,'root':capture_root}


def _check_mir_calls(args: argparse.Namespace, capture_report: dict[str, Any], mir_module=None) -> dict[str, Any]:
    module=mir_module or _load(args.cloud_dir,Path(MIR_CALLS_REL.name),'r24_w4_contract_mir_calls',MIR_CALLS_SHA256)
    mir=capture_report.get('mir')
    need(type(mir) is dict and set(mir)=={'normal','readonly'},'fresh normal/readonly MIR inventory missing')
    texts={}
    for kind in ('normal','readonly'):
        row=mir.get(kind)
        need(type(row) is dict and type(row.get('full_function_record')) is str,
             'fresh full-function MIR record missing: '+kind)
        raw,_=_contained_file(capture_report['_evidence_root'],row['full_function_record'])
        need(sha(raw)==row.get('full_function_record_sha256'),'fresh MIR record digest differs: '+kind)
        texts[kind]=raw.decode('utf-8',errors='strict')
    result=module.analyze_pair(texts['normal'],texts['readonly'])
    need(type(result) is dict and result.get('complete') is True and
         result.get('status')=='COMPLETE_TYPED_MIR_OBSERVATION' and
         result.get('typed_call_linkage')=='UNKNOWN' and
         result.get('typed_callee_family_observation')=='OBSERVED_STRUCTURAL_MIR_CALLS',
         'fresh MIR analyzer incomplete or claims linkage')
    for kind in ('normal','readonly'):
        calls=result.get(kind,{}).get('calls') if type(result.get(kind)) is dict else None
        need(type(calls) is list and len(calls)==8,'fresh typed MIR selector count differs: '+kind)
    return result


def _stage_runner(repo: Path, injection=None):
    if injection is not None:
        return injection
    module=_load(repo,STAGE_RUNNER_REL,'r24_w4_contract_stage_runner',STAGE_RUNNER_SHA256)
    return module.run_stage


def _run_stage(runner, name: str, argv: list[str], root: Path, env: dict[str,str],
               fixture_hashes: dict[str,str], deadline: int, *, cap=1200,
               stdout_name: str | None=None, stdin_name: str | None=None) -> dict[str,Any]:
    result=runner(name,argv,root,env,fixture_hashes,deadline,cap,
                  stdin_name=stdin_name,stdout_name=stdout_name)
    if type(result) is not dict:
        return {'status':'WRONG_TYPE','exit':None,'argv':argv,'errors':['stage result wrong type']}
    row=dict(result); code=row.get('exit')
    if 'status' not in row:
        row['status']='TIMEOUT' if code==124 else 'NOT_RUN' if row.get('skipped') is True or type(code) is not int else 'RAN'
    elif row.get('status') not in ('RAN','TIMEOUT','NOT_RUN'):
        row['errors']=list(row.get('errors',[]))+['explicit stage status is malformed']
    row['argv']=argv
    row['closed_environment']={k:v for k,v in env.items()
        if k.startswith('SORT4_') or k == 'LANE'}
    if type(code) is not int:
        row.setdefault('errors',[]); row['errors'].append('stage exit missing/wrong type or NOT_RUN')
    return row


def _stage_logs(root: Path, stage: object) -> dict[str,Any]:
    result={'stdout':None,'stderr':None}; errors=[]
    if type(stage) is not dict: return result,['stage record missing/wrong type']
    for channel in ('stdout','stderr'):
        name=stage.get(channel)
        if type(name) is not str:
            errors.append(channel+' stage log path missing/wrong type'); continue
        try:
            raw,path=_contained_file(root,name)
            raw.decode('utf-8',errors='strict')
            result[channel]={'path':str(path.relative_to(root)),'bytes':len(raw),'sha256':sha(raw)}
        except BaseException as exc:
            errors.append(channel+' stage log missing/unsafe/invalid UTF-8: '+type(exc).__name__)
    return result,errors


def _header_variants(header_manifest: dict[str,Any]) -> list[str]:
    cases=header_manifest.get('cases')
    need(type(cases) is dict and set(cases)==set(CASES),
         'header manifest case order/inventory differs')
    return list(CASES)


def _case_env(args: argparse.Namespace, case: str, native_dir: Path, header: Path,
              callee_unit: Path, callee_body: Path, callee_source: Path,
              profile_path: Path, base: dict[str,str] | None=None) -> dict[str,str]:
    env=dict(os.environ) if base is None else dict(base)
    env['PATH']=str(NATIVE_HOME/'bin')+os.pathsep+env.get('PATH',os.defpath)
    env.update({R24_ENV:R24_PHASE,R21_ENV:R21_PHASE,'SORT4_SELECT_PROFILE':PROFILE,
                NATIVE_ENV_PREFIX+'MODE':'1',NATIVE_ENV_PREFIX+'CASE':case,
                NATIVE_ENV_PREFIX+'EVIDENCE_DIR':str(native_dir.resolve()),
                NATIVE_ENV_PREFIX+'SOURCE_SHA256':SOURCE_SHA256,
                NATIVE_ENV_PREFIX+'CALLEE_UNIT':str(callee_unit),
                NATIVE_ENV_PREFIX+'CALLEE_BODY':str(callee_body),
                NATIVE_ENV_PREFIX+'CALLEE_SOURCE':str(callee_source),
                NATIVE_ENV_PREFIX+'REFERENCE_HEADER':str(args.repo/REFERENCE_HEADER_REL),
                NATIVE_ENV_PREFIX+'QUALIFIED_PROFILE':str(profile_path)})
    return env


def _validate_native_facts(case: str, case_root: Path, header: dict[str,Any],
                           native_stage: object, native_before: object,
                           native_after: object, expected_inputs: dict[str,tuple[str,int]],
                           build_id: str, *, require_binary_stable: str | None=None,
                           expected_environment: dict[str,str] | None=None,
                           expected_paths: dict[str,Path] | None=None,
                           expected_argv: list[str] | None=None) -> tuple[dict[str,Any],list[str]]:
    errors=[]
    if type(native_stage) is not dict or native_stage.get('status')!='RAN' or native_stage.get('exit')!=1:
        errors.append('native diagnostic stage was not RAN with the expected refusal exit')
    if expected_environment is not None and type(native_stage) is dict and \
       native_stage.get('closed_environment') != expected_environment:
        errors.append('native closed SORT4 environment differs')
    if type(native_stage) is dict and expected_argv is not None and native_stage.get('argv')!=expected_argv:
        errors.append('native verifier argv differs from the closed command')
    if type(native_stage) is dict and (native_stage.get('fixture_before')!={'verified/lib.rs':SOURCE_SHA256} or
       native_stage.get('fixture_after')!={'verified/lib.rs':SOURCE_SHA256} or
       native_stage.get('fixture_integrity') is not True):
        errors.append('native source fixture changed or stage inventory is incomplete')
    native_tool_set={**SOURCE_TOOL_HASHES,'bin/verifast':'DIAGNOSTIC_BUILD_OUTPUT_RECORDED'}
    if _tool_identity_errors(native_before,native_tool_set,binary_any=True) or \
       _tool_identity_errors(native_after,native_tool_set,binary_any=True):
        errors.append('diagnostic tool source identity changed during case '+case)
    before=native_before.get('bin/verifast') if type(native_before) is dict else None
    after=native_after.get('bin/verifast') if type(native_after) is dict else None
    if type(before) is not dict or type(after) is not dict or before!=after or \
       after.get('regular') is not True or after.get('bytes',0)<=0:
        errors.append('diagnostic verifier binary changed during case '+case)
    if require_binary_stable is not None and type(after) is dict and after.get('sha256')!=require_binary_stable:
        errors.append('diagnostic verifier binary differs from built identity')
    logs,log_errors=_stage_logs(case_root,native_stage); errors.extend(log_errors)
    stdout=''; stderr=''
    try:
        stdout=(case_root/native_stage['stdout']).read_text(encoding='utf-8')
        stderr=(case_root/native_stage['stderr']).read_text(encoding='utf-8')
    except BaseException as exc:
        errors.append('native diagnostic log unreadable: '+type(exc).__name__)
    out_lines=stdout.splitlines(); err_lines=stderr.splitlines()
    marker_rows=[line for line in out_lines if line.startswith(NATIVE_PREFIX)]
    expected_marker=re.compile(r'^SORT4-R24-W4-CONTRACT-INPUTS: case='+re.escape(case)+
        r' actual_spec_sha256=[0-9a-f]{64} imported_spec_sha256=[0-9a-f]{64} '
        r'caller_body_sha256='+CALLER_BODY_SHA256+r' typed_call_linkage=UNKNOWN$')
    if len(marker_rows)!=1 or not expected_marker.fullmatch(marker_rows[0]):
        errors.append('native stdout contract-input marker missing/duplicated/malformed')
    reason=CASE_REFUSAL[case]
    expected_stderr='Fatal error: exception Failure("'+NATIVE_REFUSAL_PREFIX+reason+'")'
    if err_lines.count(expected_stderr)!=1 or sum(line.count(NATIVE_PREFIX) for line in out_lines+err_lines)!=2:
        errors.append('native stderr refusal marker missing, duplicated, or changed')
    facts_path=case_root/'native'/'contract-inputs.json'
    facts=_json(facts_path)
    if type(facts) is not dict or facts.get('schema')!=SCHEMA or facts.get('case')!=case or \
       facts.get('complete') is not True or facts.get('classification')!=EXPECTED_CASE_CLASS[case] or \
       facts.get('expected_refusal')!=('contract inputs matched; no proof rule admitted' if case=='positive' else 'exact pinned control contract rejected'):
        errors.append('native contract-input facts missing/incomplete or classification differs')
        facts={} if type(facts) is not dict else facts
    expected_input_keys={'caller_source','caller_unit','caller_body','callee_source',
                         'callee_source_in_mir','callee_unit','callee_body','reference_header',
                         'variant_header','qualified_profile'}
    inputs=facts.get('inputs') if type(facts) is dict else None
    if type(inputs) is not dict or set(inputs)!=expected_input_keys:
        errors.append('native input fact inventory differs')
    else:
        for key,(digest,size) in expected_inputs.items():
            item=inputs.get(key)
            if type(item) is not dict or item.get('sha256')!=digest or type(item.get('bytes')) is not int or item.get('bytes')!=size:
                errors.append('native input fact differs: '+key)
            elif key in ('caller_unit','caller_body'):
                if item.get('origin')!='native_input' or set(item)!={'origin','bytes','sha256'}:
                    errors.append('native memory input shape differs: '+key)
            elif type(item.get('path')) is not str or set(item)!={'path','bytes','sha256'}:
                errors.append('native file input shape differs: '+key)
            else:
                try:
                    path=Path(item['path'])
                    expected_path=(expected_paths or {}).get(key)
                    if path.is_symlink() or not path.is_file() or sha(path.read_bytes())!=digest or \
                       (expected_path is not None and path.resolve()!=expected_path.resolve()) or \
                       (expected_path is not None and Path(os.path.abspath(expected_path))!=expected_path.resolve()):
                        errors.append('native input physical target differs: '+key)
                except OSError:
                    errors.append('native input physical target missing: '+key)
        if type(inputs.get('variant_header')) is dict and inputs['variant_header'].get('sha256')!=header.get('sha256'):
            errors.append('native variant header fact differs')
    if facts.get('typed_call_navigation_sha256')!=TYPED_CALL_NAVIGATION_SHA256 or \
       facts.get('typed_call_site_count_source_reported')!=8 or \
       facts.get('typed_call_linkage')!='UNKNOWN' or facts.get('caller_body_proof_admission') is not False or \
       facts.get('accepted') is not False or facts.get('publication_allowed') is not False or \
       facts.get('proof_credit')!=0:
        errors.append('native report linkage/admission boundary differs')
    for basename,key in (('actual-contract.ml','actual_contract'),('imported-contract.ml','imported_contract')):
        try:
            raw,path=_contained_file(case_root/'native',basename)
            value=facts.get(key)
            if type(value) is not dict or value.get('path')!=basename or value.get('bytes')!=len(raw) or value.get('sha256')!=sha(raw):
                errors.append('physical '+basename+' differs from native report')
        except BaseException as exc:
            errors.append('physical '+basename+' missing/unsafe: '+type(exc).__name__)
    actual=facts.get('actual_contract'); imported=facts.get('imported_contract')
    if type(actual) is dict and type(imported) is dict:
        equal=actual.get('sha256')==imported.get('sha256')
        if (case=='positive') != equal:
            errors.append('actual/imported contract equality differs from case')
    expected_files={'contract-inputs.json','actual-contract.ml','imported-contract.ml'}
    native_dir=case_root/'native'
    try:
        names={p.name for p in native_dir.iterdir()}
        if names!=expected_files:
            errors.append('native evidence file inventory differs')
    except OSError:
        errors.append('native evidence directory missing/unsafe')
    facts['native_logs']=logs
    facts['build_id']=build_id
    facts['stage']={'status':native_stage.get('status') if type(native_stage) is dict else None,
                    'exit':native_stage.get('exit') if type(native_stage) is dict else None,
                    'argv':native_stage.get('argv') if type(native_stage) is dict else None,
                    'fixture_before':native_stage.get('fixture_before') if type(native_stage) is dict else None,
                    'fixture_after':native_stage.get('fixture_after') if type(native_stage) is dict else None,
                    'fixture_integrity':native_stage.get('fixture_integrity') if type(native_stage) is dict else None}
    facts['diagnostic_only']=True
    facts['errors']=errors
    facts.update(accepted=False,publication_allowed=False,proof_credit=0,
                 typed_call_linkage='UNKNOWN',caller_body_proof_admission=False)
    return facts,errors


def _context_prerequisite(args: argparse.Namespace, env: dict[str,str], *, live_deadline: bool):
    mode=_mode(args)
    prereq=_load_prerequisites(args,mode,
        getattr(args,'_const_matrix_summary',None),getattr(args,'_const_matrix_audit',None),
        getattr(args,'_consequence_summary',None),getattr(args,'_consequence_audit',None),env)
    return mode,prereq


def _partial_record(args: argparse.Namespace, env: dict[str,str]) -> dict[str,Any]:
    return {'schema':SCHEMA,'complete':False,'classification':'INCOMPLETE_CONTRACT_INPUT_DIAGNOSTIC',
        'assurance':'SOURCE_REPORTED_DIAGNOSTIC_ONLY','candidate':getattr(args,'candidate',None),
        'build_id':env.get('CLOUD_BUILD_ID'),'phase_id':R24_PHASE,'route_phase_id':R21_PHASE,
        'owner':'select-sort4','lane':LANE,'profile':PROFILE,'mode_path':MODE_REL.as_posix(),
        'mode_sha256':MODE_SHA256,'cases':[],'stages':[],'capture':None,
        'native_tool_home':str(getattr(args,'native_tool_home','')),
        'tool_copy_path':str(NATIVE_HOME),'errors':[],
        'typed_call_linkage':'UNKNOWN','call_linkage':'UNKNOWN',
        'caller_body_proof_admission':False,'caller_body_proof_status':'UNKNOWN',
        'accepted':False,'publication_allowed':False,'proof_credit':0}


def _check_capture_and_input_files(args: argparse.Namespace, root: Path,
                                   capture_report: dict[str,Any], analyzer_result: dict[str,Any],
                                   prereq: dict[str,Any]) -> tuple[dict[str,Any],list[str]]:
    errors=[]
    source=capture_report.get('source')
    fixture_paths=source.get('fixture_paths') if type(source) is dict else None
    need(type(fixture_paths) is dict and set(fixture_paths)=={'original','verified'},
         'fresh capture source fixture paths missing')
    current_sources={}
    for label,expected in (('original',ORIGINAL_SHA256),('verified',SOURCE_SHA256)):
        raw,path=_contained_file(root/'capture',fixture_paths[label])
        if sha(raw)!=expected: errors.append('fresh captured '+label+' source hash differs')
        current_sources[label]={'path':str(path.relative_to(args.evidence)),
                                'bytes':len(raw),'sha256':sha(raw),'expected_sha256':expected}
    need(type(analyzer_result) is dict and analyzer_result.get('complete') is True,
         'typed MIR analyzer result missing/incomplete')
    positive=prereq['matrix_summary']['rows']['positive']
    if positive.get('current_stage_observation',{}).get('source_unchanged') is not True:
        errors.append('positive const matrix source-stage binding is not intact')
    positive_case=args.evidence/'cases/r21-fractional-proof/variants/positive/nine-body-a1-owned-forget'
    unit_path=positive_case/'actual-nested-9-unit.marshal'
    body_path=positive_case/'actual-nested-9-body-7.marshal'
    source_path=positive_case/'verified/lib.rs'
    current={}
    for key,path,expected in (('callee_unit',unit_path,CALLEE_UNIT_SHA256),
                              ('callee_body',body_path,CALLEE_BODY_SHA256),
                              ('callee_source',source_path,CALLEE_SOURCE_SHA256)):
        need(not path.is_symlink() and path.is_file() and path.resolve().is_relative_to(args.evidence.resolve()),
             'same-Build current positive const input missing/unsafe: '+key)
        raw=path.read_bytes(); need(sha(raw)==expected,'same-Build current positive const input hash differs: '+key)
        current[key]={'path':str(path.resolve()),'bytes':len(raw),'sha256':sha(raw)}
    mir_inputs=analyzer_result
    result={'fresh_caller_source':current_sources,'fresh_typed_mir_observation':mir_inputs,
            'same_build_current_callee_inputs':current}
    return result,errors


def _stage_env(args: argparse.Namespace, base: dict[str,str] | None=None) -> dict[str,str]:
    env=dict(os.environ) if base is None else dict(base); env['PATH']=str(NATIVE_HOME/'bin')+os.pathsep+env.get('PATH',os.defpath)
    env.update({R24_ENV:R24_PHASE,R21_ENV:R21_PHASE,'SORT4_SELECT_PROFILE':PROFILE})
    return env


def _run_driver(args: argparse.Namespace, *, stage_runner=None, capture_module=None,
                mir_module=None, prerequisites: dict[str,Any], env: dict[str,str] | None=None) -> dict[str,Any]:
    root=args.evidence/ROOT_REL
    need(not root.exists() and not root.is_symlink(),'fresh contract-input subtree already exists')
    _safe_create_tree(root)
    run_env=dict(os.environ) if env is None else dict(env)
    record=_partial_record(args,run_env)
    record['evidence_root']=str(root.resolve())
    record['const_matrix_summary_path']=MATRIX_SUMMARY_REL.as_posix()
    record['const_matrix_audit_path']=MATRIX_AUDIT_REL.as_posix()
    record['consequence_summary_path']=CONSEQUENCE_SUMMARY_REL.as_posix()
    record['consequence_audit_path']=CONSEQUENCE_AUDIT_REL.as_posix()
    record['errors']=[]
    summary_path=args.evidence/SUMMARY_REL
    _write_json(summary_path,record)
    try:
        runner=_stage_runner(args.repo,stage_runner)
        capture=_capture_fresh(args,root,runner,capture_module)
        capreport=dict(capture['report']); capreport['_evidence_root']=capture['root']
        mir=_check_mir_calls(args,capreport,mir_module)
        inputs,source_errors=_check_capture_and_input_files(args,root,capreport,mir,prerequisites)
        record['capture']={'summary_path':str((capture['root']/capture['module'].SUMMARY_REL).relative_to(args.evidence)),
                           'audit_path':str((capture['root']/'W4-CAPTURE-AUDIT.json').relative_to(args.evidence)),
                           'summary':capture['report'],'audit':capture['audit']}
        record['input_observation']=inputs
        record['errors'].extend(source_errors)
        if source_errors: raise RuntimeError('fresh capture/source input validation failed')
        bootstrap_before=_tool_hashes(args.native_tool_home,TOOL_HASHES)
        need(not _tool_identity_errors(bootstrap_before,TOOL_HASHES),
             'qualified bootstrap tool files do not match all nine pins')
        frozen_before=_tool_hashes(args.tool_home,FROZEN_TOOL_HASHES_8A)
        need(not _tool_identity_errors(frozen_before,FROZEN_TOOL_HASHES_8A),'frozen 8a tool home changed')
        record['bootstrap_tool_hashes_before']=bootstrap_before
        record['frozen_tool_hashes_before']=frozen_before
        need(not NATIVE_HOME.exists() and not NATIVE_HOME.is_symlink(),
             'diagnostic tool-copy path already exists')
        stage_root=root/'tool-stages'; _safe_create_tree(stage_root)
        stage_hashes={}
        for label,src_label in (('original','original'),('verified','verified')):
            source_path=capture['root']/capture['report']['source']['fixture_paths'][src_label]
            raw=source_path.read_bytes(); destination=stage_root/label/'lib.rs'
            destination.parent.mkdir(); destination.write_bytes(raw)
            stage_hashes[f'{label}/lib.rs']=sha(raw)
        base_env=_stage_env(args,run_env)
        def runone(name,argv,cap=1200):
            stage=_run_stage(runner,name,argv,stage_root,base_env,stage_hashes,
                             args.deadline_epoch,cap=cap,stdout_name=name+'.stdout.log')
            stage['name']=name
            logs,log_errors=_stage_logs(stage_root,stage)
            stage['physical_logs']=logs; stage['errors']=list(stage.get('errors',[]))+log_errors
            record['stages'].append(stage); _write_json(summary_path,record,overwrite=True)
            return stage
        copy=runone('contract-tool-copy',['/bin/cp','-a',str(args.native_tool_home),str(NATIVE_HOME)])
        if copy.get('status')!='RAN' or copy.get('exit')!=0: raise RuntimeError('diagnostic tool copy failed')
        copied_before=_tool_hashes(NATIVE_HOME,TOOL_HASHES)
        need(not _tool_identity_errors(copied_before,TOOL_HASHES),'copied bootstrap tool identity differs')
        translator=NATIVE_HOME/'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
        need(translator.is_file() and not translator.is_symlink() and sha(translator.read_bytes())==BOOTSTRAP_SOURCE_SHA256,
             'bootstrap translator is not exact 5170 source')
        patch=args.repo/PATCH_REL
        check=runone('contract-tool-patch-check',['git','-C',str(NATIVE_HOME),'apply','--check',str(patch)])
        if check.get('status')!='RAN' or check.get('exit')!=0: raise RuntimeError('native diagnostic patch check failed')
        apply=runone('contract-tool-patch-apply',['git','-C',str(NATIVE_HOME),'apply',str(patch)])
        if apply.get('status')!='RAN' or apply.get('exit')!=0: raise RuntimeError('native diagnostic patch apply failed')
        need(sha(translator.read_bytes())==PATCHED_SOURCE_SHA256,'patched translator bytes differ')
        build=runone('contract-tool-build',['make','-C',str(NATIVE_HOME/'src'),'../bin/verifast',
                                           'WITHOUT_LABLGTK=yes','VERBOSE=yes'])
        if build.get('status')!='RAN' or build.get('exit')!=0: raise RuntimeError('diagnostic tool build failed')
        native_built=_tool_hashes(NATIVE_HOME,SOURCE_TOOL_HASHES)
        need(not _tool_identity_errors(native_built,SOURCE_TOOL_HASHES),
             'diagnostic tool source identity changed during build')
        binary=_tool_hashes(NATIVE_HOME,{'bin/verifast':'DIAGNOSTIC_BUILD_OUTPUT_RECORDED'},binary_any=True)
        need(type(binary.get('bin/verifast')) is dict and binary['bin/verifast'].get('regular') is True and
             binary['bin/verifast'].get('bytes',0)>0,'built diagnostic verifier binary missing/empty')
        record['diagnostic_tool_hashes_after_build']={**native_built,**binary}
        _write_json(summary_path,record,overwrite=True)
        capsource=capture['report']['source']; fixture_root=capture['root']
        case_source=fixture_root/capsource['fixture_paths']['verified']
        case_source_sha=sha(case_source.read_bytes())
        need(case_source_sha==SOURCE_SHA256,'fresh captured W4 verified source changed before native case')
        callee_unit,_=_source_path(args,'cases/r21-fractional-proof/variants/positive/nine-body-a1-owned-forget/actual-nested-9-unit.marshal',CALLEE_UNIT_SHA256)
        callee_body,_=_source_path(args,'cases/r21-fractional-proof/variants/positive/nine-body-a1-owned-forget/actual-nested-9-body-7.marshal',CALLEE_BODY_SHA256)
        callee_source,_=_source_path(args,'cases/r21-fractional-proof/variants/positive/nine-body-a1-owned-forget/verified/lib.rs',CALLEE_SOURCE_SHA256)
        profile_path=args.repo/QUALIFIED_PROFILE_REL
        header_manifest=prerequisites['header_manifest']
        for case in _header_variants(header_manifest):
            case_root=root/'variants'/case
            header=_write_case_header(args,case_root,case,header_manifest)
            _safe_create_tree(case_root/'verified')
            shutil.copyfile(case_source,case_root/'verified/lib.rs')
            need(sha((case_root/'verified/lib.rs').read_bytes())==SOURCE_SHA256,
                 'case source bytes differ before diagnostic: '+case)
            native_dir=case_root/'native'; native_dir.mkdir()
            env=_case_env(args,case,native_dir,Path(header['path']),callee_unit,callee_body,callee_source,profile_path,run_env)
            expected_prefix={
                'SORT4_R24_W4_CONTRACT_MODE','SORT4_R24_W4_CONTRACT_CASE','SORT4_R24_W4_CONTRACT_EVIDENCE_DIR',
                'SORT4_R24_W4_CONTRACT_SOURCE_SHA256','SORT4_R24_W4_CONTRACT_CALLEE_UNIT',
                'SORT4_R24_W4_CONTRACT_CALLEE_BODY','SORT4_R24_W4_CONTRACT_CALLEE_SOURCE',
                'SORT4_R24_W4_CONTRACT_REFERENCE_HEADER','SORT4_R24_W4_CONTRACT_QUALIFIED_PROFILE'}
            need({k for k in env if k.startswith(NATIVE_ENV_PREFIX)}==expected_prefix,
                 'native contract env inventory differs')
            case_hashes={'verified/lib.rs':SOURCE_SHA256}
            argv=[str(NATIVE_HOME/'bin/verifast'),'-rustc_args','--edition 2021','-verbose','1',
                  '-extern_spec','r24_select='+header['path'],'verified/lib.rs']
            native_before=_tool_hashes(NATIVE_HOME,{**SOURCE_TOOL_HASHES,'bin/verifast':'DIAGNOSTIC_BUILD_OUTPUT_RECORDED'},binary_any=True)
            stage=_run_stage(runner,'contract-input-'+case,argv,case_root,env,case_hashes,
                             args.deadline_epoch,cap=1200,stdout_name='contract-inputs.stdout.log')
            stage_logs,stage_log_errors=_stage_logs(case_root,stage)
            stage['physical_logs']=stage_logs
            native_after=_tool_hashes(NATIVE_HOME,{**SOURCE_TOOL_HASHES,'bin/verifast':'DIAGNOSTIC_BUILD_OUTPUT_RECORDED'},binary_any=True)
            expected_inputs=_expected_input_hashes(case,header,case_source,capreport,callee_source,callee_unit,callee_body,profile_path)
            expected_paths={'caller_source':case_root/'verified/lib.rs','callee_source':callee_source,
                'callee_source_in_mir':callee_source,'callee_unit':callee_unit,'callee_body':callee_body,
                'reference_header':args.repo/REFERENCE_HEADER_REL,'variant_header':Path(header['path']),
                'qualified_profile':profile_path}
            expected_argv=[str(NATIVE_HOME/'bin/verifast'),'-rustc_args','--edition 2021','-verbose','1',
                           '-extern_spec','r24_select='+header['path'],'verified/lib.rs']
            facts,case_errors=_validate_native_facts(case,case_root,header,stage,native_before,native_after,
                expected_inputs,run_env['CLOUD_BUILD_ID'],require_binary_stable=binary['bin/verifast']['sha256'],
                expected_environment={k:v for k,v in env.items() if k.startswith('SORT4_') or k=='LANE'},
                expected_paths=expected_paths,expected_argv=expected_argv)
            case_errors.extend(stage_log_errors)
            case_row={'case':case,'expected_classification':EXPECTED_CASE_CLASS[case],
                      'header':header,'stage':stage,'facts':facts,'errors':case_errors,
                      'source_after_sha256':sha((case_root/'verified/lib.rs').read_bytes()),
                      'tool_hashes_before':native_before,'tool_hashes_after':native_after,
                      'expected_refusal':CASE_REFUSAL[case]}
            record['cases'].append(case_row)
            if case_errors: record['errors'].extend(case+': '+e for e in case_errors)
            _write_json(summary_path,record,overwrite=True)
            if case_errors: break
        source_after={}
        for label,expected in (('original',ORIGINAL_SHA256),('verified',SOURCE_SHA256)):
            rel=capsource['fixture_paths'][label]
            raw,path=_contained_file(fixture_root,rel)
            source_after[label]={'path':str(path.relative_to(args.evidence)),
                                 'bytes':len(raw),'sha256':sha(raw)}
            if sha(raw)!=expected:
                record['errors'].append('captured '+label+' source changed during contract cases')
        current_positive=args.evidence/'cases/r21-fractional-proof/variants/positive/nine-body-a1-owned-forget'
        for rel,expected in (('actual-nested-9-unit.marshal',CALLEE_UNIT_SHA256),
                             ('actual-nested-9-body-7.marshal',CALLEE_BODY_SHA256),
                             ('verified/lib.rs',CALLEE_SOURCE_SHA256)):
            raw,path=_contained_file(current_positive,rel)
            if sha(raw)!=expected:
                record['errors'].append('same-Build callee input changed during cases: '+rel)
        record['complete_source_observation_after']=source_after
        capture_args=argparse.Namespace(**vars(args)); capture_args.evidence=capture['root']
        capture_args.tool_home=args.tool_home
        capture_args.schema=args.tool_home/'src/rust_frontend/vf_mir/vf_mir.capnp'
        capture_args.mode_file=args.repo/CAPTURE_MODE_REL
        capture_args.output=capture['root']/'W4-CAPTURE-AUDIT.json'
        capture_args.runner_exit=0; capture_args.failed_stage='complete'
        audit_after=capture['module'].audit(capture_args)
        if type(audit_after) is not dict or audit_after.get('evidence_complete') is not True or \
           audit_after.get('accepted') is not False or audit_after.get('proof_credit')!=0:
            record['errors'].append('fresh source capture changed or failed post-case audit')
        record['capture']['audit_after']=audit_after
        record['bootstrap_tool_hashes_after']=_tool_hashes(args.native_tool_home,TOOL_HASHES)
        record['frozen_tool_hashes_after']=_tool_hashes(args.tool_home,FROZEN_TOOL_HASHES_8A)
        record['errors'].extend(_tool_identity_errors(record['bootstrap_tool_hashes_after'],TOOL_HASHES))
        record['errors'].extend(_tool_identity_errors(record['frozen_tool_hashes_after'],FROZEN_TOOL_HASHES_8A))
        record['errors'].extend(_tool_identity_errors(record['diagnostic_tool_hashes_after_build'],
            {**SOURCE_TOOL_HASHES,'bin/verifast':'DIAGNOSTIC_BUILD_OUTPUT_RECORDED'},binary_any=True))
        record['complete']=not record['errors'] and len(record['cases'])==len(CASES)
        record['classification']='ALL_CASES_DIAGNOSTIC_ONLY_COMPLETE' if record['complete'] else 'INCOMPLETE_CONTRACT_INPUT_DIAGNOSTIC'
        record.update(typed_call_linkage='UNKNOWN',call_linkage='UNKNOWN',caller_body_proof_admission=False,
                      caller_body_proof_status='UNKNOWN',accepted=False,publication_allowed=False,proof_credit=0)
        _write_json(summary_path,record,overwrite=True)
        return record
    except BaseException as exc:
        record['errors'].append('exception: '+type(exc).__name__+': '+str(exc))
        record['complete']=False; record['classification']='INCOMPLETE_CONTRACT_INPUT_DIAGNOSTIC'
        record.update(typed_call_linkage='UNKNOWN',call_linkage='UNKNOWN',caller_body_proof_admission=False,
                      caller_body_proof_status='UNKNOWN',accepted=False,publication_allowed=False,proof_credit=0)
        try: _write_json(summary_path,record,overwrite=True)
        except BaseException as write_error:
            try: exc.add_note('partial contract-input summary write failed: '+repr(write_error))
            except Exception: pass
        raise


def _expected_input_hashes(case: str, header: dict[str,Any], source: Path,
                           capture_report: dict[str,Any], callee_source: Path,
                           callee_unit: Path, callee_body: Path, profile_path: Path) -> dict[str,tuple[str,int]]:
    capture_root=Path(capture_report['_evidence_root'])
    src=capture_report['source']; paths=src['fixture_paths']
    caller_source_raw=(capture_root/paths['verified']).read_bytes()
    header_path=Path(header['path']); header_raw=header_path.read_bytes()
    profile_raw=profile_path.read_bytes()
    source_raw=source.read_bytes(); callee_raw=callee_source.read_bytes()
    unit_raw=callee_unit.read_bytes(); body_raw=callee_body.read_bytes()
    hashes={
        'caller_source':(sha(caller_source_raw),len(caller_source_raw)),
        'caller_unit':(CALLER_UNIT_SHA256,271019), 'caller_body':(CALLER_BODY_SHA256,262129),
        'callee_source':(sha(callee_raw),len(callee_raw)),
        'callee_source_in_mir':(sha(callee_raw),len(callee_raw)),
        'callee_unit':(sha(unit_raw),len(unit_raw)), 'callee_body':(sha(body_raw),len(body_raw)),
        'reference_header':(REFERENCE_HEADER_SHA256,384),
        'variant_header':(header['sha256'],header['bytes']),
        'qualified_profile':(QUALIFIED_PROFILE_SHA256,len(profile_raw)),
    }
    return hashes


def _audit_core(args: argparse.Namespace, source: object, *, stage_runner=None,
                capture_module=None, mir_module=None, prerequisites: dict[str,Any] | None=None,
                env: dict[str,str]) -> list[str]:
    errors=[]
    root=args.evidence/ROOT_REL
    if type(source) is not dict:
        return ['contract-input summary missing/wrong type']
    if source.get('schema')!=SCHEMA or source.get('candidate')!=args.candidate or \
       source.get('build_id')!=env.get('CLOUD_BUILD_ID'):
        errors.append('driver summary context differs')
    if source.get('complete') is not True or source.get('classification')!='ALL_CASES_DIAGNOSTIC_ONLY_COMPLETE' or \
       source.get('errors')!=[]:
        errors.append('driver summary does not report a clean complete diagnostic collection')
    if source.get('mode_sha256')!=MODE_SHA256 or source.get('mode_path')!=MODE_REL.as_posix():
        errors.append('driver mode identity differs')
    if source.get('typed_call_linkage')!='UNKNOWN' or source.get('call_linkage')!='UNKNOWN' or \
       source.get('caller_body_proof_admission') is not False or source.get('accepted') is not False or \
       source.get('publication_allowed') is not False or source.get('proof_credit')!=0:
        errors.append('driver diagnostic boundary differs')
    if source.get('evidence_root')!=str(root.resolve()): errors.append('driver evidence root differs')
    tool_stages=source.get('stages')
    expected_tool_commands={
        'contract-tool-copy':['/bin/cp','-a',str(args.native_tool_home),str(NATIVE_HOME)],
        'contract-tool-patch-check':['git','-C',str(NATIVE_HOME),'apply','--check',str(args.repo/PATCH_REL)],
        'contract-tool-patch-apply':['git','-C',str(NATIVE_HOME),'apply',str(args.repo/PATCH_REL)],
        'contract-tool-build':['make','-C',str(NATIVE_HOME/'src'),'../bin/verifast','WITHOUT_LABLGTK=yes','VERBOSE=yes'],
    }
    if type(tool_stages) is not list or [x.get('name') for x in tool_stages if type(x) is dict] != list(expected_tool_commands):
        errors.append('diagnostic tool build stage inventory/order differs')
        tool_stages=[] if type(tool_stages) is not list else tool_stages
    tool_stage_root=root/'tool-stages'
    capture_summary=source.get('capture',{}).get('summary',{}) if type(source.get('capture')) is dict else {}
    fixture_map={}
    if type(capture_summary) is dict and type(capture_summary.get('source')) is dict:
        for label,rel in capture_summary['source'].get('fixture_paths',{}).items():
            try:
                raw,_=_contained_file(root/'capture',rel)
                fixture_map[label+'/lib.rs']=sha(raw)
            except BaseException:
                errors.append('captured source unavailable for tool-stage audit: '+str(label))
    for stage in tool_stages:
        name=stage.get('name') if type(stage) is dict else None
        if name not in expected_tool_commands: errors.append('unknown tool-build stage'); continue
        if stage.get('argv')!=expected_tool_commands[name] or stage.get('status')!='RAN' or stage.get('exit')!=0:
            errors.append('diagnostic tool build command/result differs: '+name)
        if stage.get('fixture_before')!=fixture_map or stage.get('fixture_after')!=fixture_map or \
           stage.get('fixture_integrity') is not True:
            errors.append('diagnostic tool build fixture changed: '+name)
        for channel,meta in stage.get('physical_logs',{}).items() if type(stage.get('physical_logs')) is dict else ():
            try:
                raw,_=_contained_file(tool_stage_root,meta.get('path',''))
                if type(meta) is not dict or len(raw)!=meta.get('bytes') or sha(raw)!=meta.get('sha256'):
                    errors.append('diagnostic tool stage log changed: '+name+'/'+channel)
            except BaseException:
                errors.append('diagnostic tool stage log missing/unsafe: '+name+'/'+channel)
    capreport=None
    try:
        runner=_stage_runner(args.repo,stage_runner)
        capture=_load_capture_for_audit(args,root,capture_module,runner)
        capreport=dict(capture['report']); capreport['_evidence_root']=capture['root']
        mir=_check_mir_calls(args,capreport,mir_module)
        if source.get('capture',{}).get('summary')!=capture['report']:
            errors.append('fresh capture summary changed')
        if source.get('capture',{}).get('audit')!=capture['audit']:
            errors.append('fresh capture audit changed')
        if source.get('capture',{}).get('audit_after')!=capture['audit']:
            errors.append('fresh capture post-case audit changed')
        if source.get('input_observation',{}).get('fresh_typed_mir_observation')!=mir:
            errors.append('typed MIR observation changed')
        source_after={}
        for label,expected in (('original',ORIGINAL_SHA256),('verified',SOURCE_SHA256)):
            rel=capture['report']['source']['fixture_paths'][label]
            raw,path=_contained_file(capture['root'],rel)
            source_after[label]={'path':str(path.relative_to(args.evidence)),
                                 'bytes':len(raw),'sha256':sha(raw)}
            if sha(raw)!=expected:
                errors.append('post-case captured source changed: '+label)
        if source.get('complete_source_observation_after')!=source_after:
            errors.append('post-case source observation differs from physical capture')
    except BaseException as exc:
        errors.append('fresh capture/MIR audit failed: '+type(exc).__name__+': '+str(exc))
    cases=source.get('cases')
    if type(cases) is not list or [x.get('case') for x in cases if type(x) is dict]!=list(CASES):
        errors.append('case inventory/order incomplete')
        cases=[] if type(cases) is not list else cases
    for row in cases:
        case=row.get('case') if type(row) is dict else None
        if case not in CASES: errors.append('unknown case row'); continue
        try:
            case_root=root/'variants'/case
            if row.get('errors')!=[] or row.get('expected_classification')!=EXPECTED_CASE_CLASS[case]:
                errors.append('case row has errors or unexpected classification: '+case)
            header=row.get('header')
            if type(header) is not dict: raise RuntimeError('header record missing')
            expected_header=_case_header_bytes(args,case,prerequisites['header_manifest'])
            header_path=case_root/'r24-select.rsspec'
            if header.get('path')!=str(header_path.resolve()) or header_path.is_symlink() or \
               not header_path.is_file() or header_path.read_bytes()!=expected_header or \
               header.get('sha256')!=sha(expected_header) or header.get('bytes')!=len(expected_header):
                errors.append('case header path/content differs from generated closed variant: '+case)
            case_source=case_root/'verified/lib.rs'
            if case_source.is_symlink() or not case_source.is_file() or sha(case_source.read_bytes())!=SOURCE_SHA256 or \
               row.get('source_after_sha256')!=SOURCE_SHA256:
                errors.append('case source changed or is unsafe: '+case)
            native_dir=case_root/'native'
            stage=row.get('stage')
            if type(stage) is not dict: raise RuntimeError('stage record missing')
            expected_argv=[str(NATIVE_HOME/'bin/verifast'),'-rustc_args','--edition 2021','-verbose','1',
                           '-extern_spec','r24_select='+str(header_path.resolve()),'verified/lib.rs']
            if stage.get('argv')!=expected_argv or stage.get('status')!='RAN' or stage.get('exit')!=1 or \
               stage.get('fixture_integrity') is not True or stage.get('fixture_before')!={'verified/lib.rs':SOURCE_SHA256} or \
               stage.get('fixture_after')!={'verified/lib.rs':SOURCE_SHA256}:
                errors.append('case native stage command/result/source binding differs: '+case)
            for channel,meta in (stage.get('physical_logs',{}) if type(stage) is dict else {}).items():
                if type(meta) is not dict: errors.append('case stage log metadata wrong type: '+case); continue
                raw,_=_contained_file(case_root,meta.get('path',''))
                if len(raw)!=meta.get('bytes') or sha(raw)!=meta.get('sha256'):
                    errors.append('case stage physical log changed: '+case+':'+channel)
            if type(prerequisites) is dict and type(capreport) is dict:
                positive=args.evidence/'cases/r21-fractional-proof/variants/positive/nine-body-a1-owned-forget'
                callee_source=positive/'verified/lib.rs'
                callee_unit=positive/'actual-nested-9-unit.marshal'
                callee_body=positive/'actual-nested-9-body-7.marshal'
                profile_path=args.repo/QUALIFIED_PROFILE_REL
                expected_inputs=_expected_input_hashes(case,header,case_source,capreport,callee_source,callee_unit,callee_body,profile_path)
                expected_paths={'caller_source':case_root/'verified/lib.rs','callee_source':callee_source,
                    'callee_source_in_mir':callee_source,'callee_unit':callee_unit,'callee_body':callee_body,
                    'reference_header':args.repo/REFERENCE_HEADER_REL,'variant_header':header_path,
                    'qualified_profile':profile_path}
                expected_environment=_case_env(args,case,case_root/'native',header_path,
                    callee_unit,callee_body,callee_source,profile_path,env)
                expected_environment={k:v for k,v in expected_environment.items()
                    if k.startswith('SORT4_') or k=='LANE'}
                expected_argv=[str(NATIVE_HOME/'bin/verifast'),'-rustc_args','--edition 2021','-verbose','1',
                               '-extern_spec','r24_select='+str(header_path.resolve()),'verified/lib.rs']
                before=row.get('tool_hashes_before'); after=row.get('tool_hashes_after')
                facts,case_errors=_validate_native_facts(case,case_root,header,stage,before,after,
                    expected_inputs,env.get('CLOUD_BUILD_ID',''),
                    require_binary_stable=source.get('diagnostic_tool_hashes_after_build',{}).get('bin/verifast',{}).get('sha256'),
                    expected_environment=expected_environment,expected_paths=expected_paths,
                    expected_argv=expected_argv)
                errors.extend(case+': '+message for message in case_errors)
                if row.get('facts')!=facts:
                    errors.append('case native fact audit differs from saved row: '+case)
        except BaseException as exc:
            errors.append('case physical audit failed: '+case+':'+type(exc).__name__)
    try:
        original=_tool_hashes(args.native_tool_home,TOOL_HASHES)
        errors.extend(_tool_identity_errors(original,TOOL_HASHES))
        frozen=_tool_hashes(args.tool_home,FROZEN_TOOL_HASHES_8A)
        errors.extend(_tool_identity_errors(frozen,FROZEN_TOOL_HASHES_8A))
        built=_tool_hashes(NATIVE_HOME,SOURCE_TOOL_HASHES)
        errors.extend(_tool_identity_errors(built,SOURCE_TOOL_HASHES))
        binary=_tool_hashes(NATIVE_HOME,{'bin/verifast':'DIAGNOSTIC_BUILD_OUTPUT_RECORDED'},binary_any=True)
        if source.get('diagnostic_tool_hashes_after_build',{}).get('bin/verifast')!=binary.get('bin/verifast'):
            errors.append('diagnostic build binary changed after run')
        if source.get('bootstrap_tool_hashes_after')!=original or source.get('frozen_tool_hashes_after')!=frozen:
            errors.append('frozen/bootstrap input tool hashes differ from run summary')
    except BaseException as exc:
        errors.append('physical tool identity audit failed: '+type(exc).__name__)
    return errors


def _load_capture_for_audit(args: argparse.Namespace, root: Path, capture_module, stage_runner):
    capture=capture_module or _load(args.cloud_dir,Path(CAPTURE_REL.name),'r24_w4_contract_capture_audit',CAPTURE_SHA256)
    capture_root=root/'capture'
    capture_args=argparse.Namespace(**vars(args)); capture_args.evidence=capture_root
    capture_args.tool_home=args.tool_home
    capture_args.schema=args.tool_home/'src/rust_frontend/vf_mir/vf_mir.capnp'
    capture_args.mode_file=args.repo/CAPTURE_MODE_REL
    capture_args.output=capture_root/'W4-CAPTURE-AUDIT.json'
    capture_args.runner_exit=getattr(args,'runner_exit',0)
    capture_args.failed_stage=getattr(args,'failed_stage','complete')
    report=_json(capture_root/capture.SUMMARY_REL)
    audit=capture.audit(capture_args)
    need(type(report) is dict and type(audit) is dict,'capture summary/audit missing or wrong type')
    return {'report':report,'audit':audit,'module':capture,'root':capture_root}


def run(args: argparse.Namespace, *, const_matrix_summary=None, const_matrix_audit=None,
        consequence_summary=None, consequence_audit=None, stage_runner=None,
        capture_module=None, mir_module=None, env: dict[str,str] | None=None) -> dict[str,Any]:
    selected_env=dict(os.environ) if env is None else dict(env)
    _route(args,selected_env,live_deadline=True)
    need(selected_env==dict(os.environ) if env is None else True,
         'run requires current process route environment unless an isolated test injection is supplied')
    args._const_matrix_summary=const_matrix_summary; args._const_matrix_audit=const_matrix_audit
    args._consequence_summary=consequence_summary; args._consequence_audit=consequence_audit
    mode=_mode(args)
    prereq=_load_prerequisites(args,mode,const_matrix_summary,const_matrix_audit,
                               consequence_summary,consequence_audit,selected_env)
    return _run_driver(args,stage_runner=stage_runner,capture_module=capture_module,
                       mir_module=mir_module,prerequisites=prereq,env=selected_env)


def audit(args: argparse.Namespace, *, const_matrix_summary=None, const_matrix_audit=None,
          consequence_summary=None, consequence_audit=None, stage_runner=None,
          capture_module=None, mir_module=None, env: dict[str,str] | None=None) -> dict[str,Any]:
    selected_env=dict(os.environ) if env is None else dict(env)
    args.evidence=Path(args.evidence).resolve()
    root=args.evidence/ROOT_REL
    raw_output=Path(getattr(args,'output',root/AUDIT_REL.relative_to(ROOT_REL)))
    expected=root/AUDIT_REL.relative_to(ROOT_REL)
    safe=True
    try:
        need(not raw_output.is_symlink() and raw_output.resolve()==expected.resolve() and
             expected.resolve().is_relative_to(root.resolve()),'audit output must be exact internal path')
        if root.exists(): _safe_root(root)
        else: _safe_root(root,create=True)
    except BaseException:
        safe=False
    report={'schema':SCHEMA+'-audit','complete':False,'evidence_complete':False,
            'candidate':getattr(args,'candidate',None),'build_id':selected_env.get('CLOUD_BUILD_ID'),
            'runner_exit':getattr(args,'runner_exit',None),'failed_stage':getattr(args,'failed_stage',None),
            'mode_path':MODE_REL.as_posix(),'mode_sha256':MODE_SHA256,'errors':[],
            'typed_call_linkage':'UNKNOWN','caller_body_proof_admission':False,
            'accepted':False,'publication_allowed':False,'proof_credit':0}
    if not safe:
        report['errors']=['audit output/root is unsafe; no write performed']
        return report
    try:
        _route(args,selected_env,live_deadline=False); _mode(args)
        prerequisites=_load_prerequisites(args,_mode(args),const_matrix_summary,const_matrix_audit,
                                           consequence_summary,consequence_audit,selected_env)
    except BaseException as exc:
        prerequisites=None
        report['errors'].append('audit prerequisite validation failed: '+type(exc).__name__+': '+str(exc))
    summary=_json(root/SUMMARY_REL.relative_to(ROOT_REL))
    if prerequisites is not None:
        report['errors'].extend(_audit_core(args,summary,stage_runner=stage_runner,
            capture_module=capture_module,mir_module=mir_module,prerequisites=prerequisites,env=selected_env))
    else:
        report['errors'].append('audit summary was not fully revalidated')
    report['complete']=not report['errors'] and type(summary) is dict and summary.get('complete') is True
    report['evidence_complete']=report['complete']
    report['summary_path']=(root/SUMMARY_REL.relative_to(ROOT_REL)).relative_to(args.evidence).as_posix()
    report['summary_sha256']=sha((root/SUMMARY_REL.relative_to(ROOT_REL)).read_bytes()) if \
        (root/SUMMARY_REL.relative_to(ROOT_REL)).is_file() and not (root/SUMMARY_REL.relative_to(ROOT_REL)).is_symlink() else None
    _write_json(expected,report,overwrite=expected.exists())
    return report

