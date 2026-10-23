#!/usr/bin/env python3
"""Closed R24 mutable proof runner composed over the frozen capture producer."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import traceback
from typing import Any

SCHEMA = 'select-r24-mut-proof-v1'
PINS_REL = Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-MATRIX-PINS.json')
PINS_SHA256 = '5aee793196c2e0ab5960f1c0ea4aab8880ca68e61d74876363e2ccf3febadbed'
ENGINE_REL = Path('research/challenge-8/cloud-build/select-callee-r24-mut-matrix-fingerprint.py')
ENGINE_SHA256 = '0abc95eaebf7593746e6ff9703b75c37df24041587aaafaafb7761eb2302c9ca'
R24_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
R24_PHASE_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R21_PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
PROFILE = 'experimental-s6-26.10-v1'
LANE = 'o26-select-callee-r20'
VARIANTS = (
    'positive', 'omit-selected-own', 'omit-unselected-own', 'no-retained-half',
    'callee-false-normal', 'callee-owner-duplicate', 'callee-owner-loss',
    'callee-thread-duplicate',
)
SNAPSHOTS = ('unit', *(f'body-{i}' for i in range(9)))
CASE_ENV = 'SORT4_R24_MUTABLE_CASE'
ROOT_ENV = 'SORT4_R24_MUTABLE_REPO_ROOT'
MARKER_PREFIX = 'SORT4-R24-MUTABLE-CERTIFICATES: case='
MARKER_SUFFIX = ' bodies=9 pointer_drop=1 assume_init=1; raw MIR cleanup retained'
SUMMARY_REL = Path('cases/r24-mut-proof/MUT-PROOF.json')
ALLOWED_AMBIENT_SORT4 = {R24_PHASE_ENV, R21_PHASE_ENV, 'SORT4_SELECT_PROFILE'}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError('R24-MUT-PROOF: ' + why)


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name('.' + path.name + '.tmp')
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    os.replace(temp, path)


def _load_pins(repo: Path) -> dict[str, Any]:
    path = repo / PINS_REL
    need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == PINS_SHA256,
         'exact mutable matrix pin file required')
    pins = json.loads(path.read_text(encoding='utf-8'))
    need(isinstance(pins, dict) and pins.get('schema') == 'select-r24-mut-matrix-pins-v1' and
         pins.get('variant_order') == list(VARIANTS) and
         pins.get('accepted') is False and pins.get('proof_credit') == 0 and
         pins.get('publication_allowed') is False and pins.get('typed_admission') is False and
         pins.get('body_proof_run') is False,
         'matrix pins schema, order, or proof boundary differs')
    need(isinstance(pins.get('cases'), dict) and set(pins['cases']) == set(VARIANTS),
         'matrix pin cases differ')
    src = pins.get('source')
    need(isinstance(src, dict) and src.get('specialization') == 'T = *mut Element; Element unrestricted' and
         src.get('original_sha256') == '3bf0bf792c8135bf964f19b3aaadef38b8ca5ee9ec95107029ad99d28a807aaa' and
         src.get('verified_sha256') == '74b20681c4c34cdc9ecd0fbb7fb3d44c51941e5d9640ede5705c5d6b6fa25165',
         'mutable source identity pins differ')
    for variant in VARIANTS:
        row = pins['cases'][variant]
        need(isinstance(row, dict) and isinstance(row.get('snapshots'), dict) and
             set(row['snapshots']) == set(SNAPSHOTS), 'ten snapshot pins missing: ' + variant)
        for name, item in row['snapshots'].items():
            need(isinstance(item, dict) and item.get('file') == f'actual-nested-9-{name}.marshal' and
                 type(item.get('bytes')) is int and item['bytes'] > 0 and
                 isinstance(item.get('sha256'), str) and re.fullmatch(r'[0-9a-f]{64}', item['sha256']),
                 'snapshot pin malformed: ' + variant + '/' + name)
    return pins


def _validate_route(env: dict[str, str], build_id: object, repo: Path) -> None:
    need(env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         env.get(R24_PHASE_ENV) == R24_PHASE and env.get(R21_PHASE_ENV) == R21_PHASE and
         env.get('LANE') == LANE and env.get('SORT4_SELECT_PROFILE') == PROFILE and
         not env.get('GITHUB_ACTIONS'), 'exact R24/R21 Cloud route and runner profile required')
    bad = sorted(key for key in env if key.startswith('SORT4_') and key not in ALLOWED_AMBIENT_SORT4)
    need(not bad, 'ambient SORT4 proof opt-ins refused: ' + ', '.join(bad))
    need(isinstance(build_id, str) and build_id == env.get('CLOUD_BUILD_ID') and
         re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', build_id),
         'canonical current Cloud build UUID required')
    need(repo.is_absolute(), 'exact proof repo must be absolute')


def _expected_variants(args) -> list[str]:
    mode = getattr(args, 'proof_mode', 'positive')
    requested = getattr(args, 'proof_variants', None)
    expected = ['positive'] if mode == 'positive' else list(VARIANTS) if mode == 'all8' else None
    need(expected is not None, 'proof_mode must be exactly positive or all8')
    if requested is None:
        requested = expected
    need(type(requested) is list and requested == expected,
         'proof_variants must exactly match the reviewable proof_mode order')
    return expected


def _source_pair(case: Path, expected: dict[str, Any], owner) -> tuple[dict[str, str], list[str]]:
    pair: dict[str, str] = {}
    errors = []
    for rel, key in (('original/lib.rs', 'original_sha256'), ('verified/lib.rs', 'verified_sha256')):
        path = case / rel
        if path.is_symlink() or not path.is_file():
            errors.append('source target missing or symlinked: ' + rel)
            continue
        digest = sha(path.read_bytes())
        pair[rel] = digest
        if digest != expected.get(key):
            errors.append('source target hash differs: ' + rel)
    try:
        if len(pair) == 2 and owner.strip_ghost((case / 'verified/lib.rs').read_bytes()) != \
                (case / 'original/lib.rs').read_bytes():
            errors.append('ghost-strip identity differs')
    except BaseException as exc:
        errors.append('ghost-strip check failed: ' + type(exc).__name__)
    return pair, errors


def _validate_capture(engine_record: object, pins: dict[str, Any], build_id: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(engine_record, dict):
        return ['fingerprint producer result is not an object']
    if engine_record.get('complete') is not True:
        errors.append('fingerprint producer is incomplete')
    if engine_record.get('native_build_id') != build_id:
        errors.append('fingerprint producer build differs from current build')
    if engine_record.get('variant_order') != list(VARIANTS):
        errors.append('fingerprint producer variant order differs')
    rows = engine_record.get('rows')
    if not isinstance(rows, dict) or set(rows) != set(VARIANTS):
        errors.append('fingerprint producer does not contain exactly all eight rows')
        return errors
    for variant in VARIANTS:
        row = rows.get(variant)
        if not isinstance(row, dict):
            errors.append('fingerprint row missing or wrong type: ' + variant)
            continue
        if (row.get('complete') is not True or
                row.get('status') != 'COMPLETE_SOURCE_REPORTED_FINGERPRINT' or
                row.get('native_build_id') != build_id or
                row.get('source_unchanged') is not True or
                row.get('ghost_strip_identity') is not True):
            errors.append('fingerprint row incomplete/current/source mismatch: ' + variant)
        if row.get('original_sha256') != pins['source']['original_sha256']:
            errors.append('original source pin differs: ' + variant)
        expected_case = pins['cases'][variant]
        if row.get('verified_sha256') != expected_case['source']['verified_sha256']:
            errors.append('verified source pin differs: ' + variant)
        fp = row.get('fingerprint')
        snaprows = fp.get('snapshots') if isinstance(fp, dict) else None
        if not isinstance(snaprows, dict) or set(snaprows) != set(SNAPSHOTS):
            errors.append('fingerprint ten-snapshot inventory differs: ' + variant)
            continue
        for name in SNAPSHOTS:
            observed, pin = snaprows.get(name), expected_case['snapshots'][name]
            if (not isinstance(observed, dict) or observed.get('file') != pin['file'] or
                    observed.get('bytes') != pin['bytes'] or observed.get('sha256') != pin['sha256']):
                errors.append(f'fingerprint snapshot pin differs: {variant}/{name}')
    location = engine_record.get('location_control')
    if not isinstance(location, dict) or location.get('complete') is not True or \
            location.get('native_build_id') != build_id or location.get('reproduces_positive_pins') is not True:
        errors.append('positive location control incomplete/current/pin mismatch')
    else:
        fp = location.get('fingerprint')
        snaprows = fp.get('snapshots') if isinstance(fp, dict) else None
        positive = pins['cases']['positive']['snapshots']
        if not isinstance(snaprows, dict) or set(snaprows) != set(SNAPSHOTS):
            errors.append('location control ten-snapshot inventory differs')
        else:
            for name in SNAPSHOTS:
                observed, pin = snaprows.get(name), positive[name]
                if not isinstance(observed, dict) or any(observed.get(k) != pin[k] for k in ('file','bytes','sha256')):
                    errors.append('location control snapshot pin differs: ' + name)
    return errors


def _proof_callback(runtime, args):
    cap = runtime['capture']
    link = getattr(cap, 'LINK', None)
    stage_obj = link
    need(callable(getattr(stage_obj, 'stage', None)), 'frozen capture LINK.stage interface unavailable')
    def invoke(*, case: Path, variant: str, name: str, build_id: str):
        need(name == 'r24-mut-proof-' + variant, 'unexpected fixed proof stage name')
        args_ns = type('ProofArgs', (), {})()
        args_ns.tool_home = Path(args.tool_home)
        args_ns.schema = Path(args.schema)
        args_ns.compiler_sysroot = str(args.compiler_sysroot)
        args_ns.deadline_epoch = int(args.deadline_epoch)
        argv = [str(Path(args.tool_home) / 'bin/verifast'), '-rustc_args',
                '--edition 2021', '-verbose', '1', 'verified/lib.rs']
        return stage_obj.stage(case, name, argv, args_ns, gates=False,
                               pointer_drop=False, cap_seconds=1200)
    return invoke


def _stage_errors(stage: object, case: Path, name: str, before: dict[str, str],
                  after: dict[str, str], variant: str) -> tuple[list[str], str]:
    errors: list[str] = []
    if not isinstance(stage, dict):
        return ['proof stage result is not an object'], ''
    if stage.get('status') != 'RAN': errors.append('proof stage status is not RAN')
    if type(stage.get('exit')) is not int: errors.append('proof stage exit is missing or wrong type')
    if stage.get('timeout') is True or stage.get('timed_out') is True or stage.get('status') in ('TIMEOUT','TIMED_OUT') or stage.get('exit') in (124,137):
        errors.append('proof stage timed out')
    if stage.get('source_before') != before or stage.get('source_after') != after or before != after:
        errors.append('proof stage source target mismatch or drift')
    if stage.get('name') not in (None, name): errors.append('proof stage name identity differs')
    if stage.get('build_id') is not None and stage.get('build_id') != os.environ.get('CLOUD_BUILD_ID'):
        errors.append('proof stage build identity differs')
    log = ''
    log_value = stage.get('log_text')
    if isinstance(log_value, str):
        log = log_value
    else:
        out = stage.get('stdout')
        if isinstance(out, str) and out and not Path(out).is_absolute() and '..' not in Path(out).parts:
            path = case / out
            if path.is_file() and not path.is_symlink():
                try: log = path.read_text(encoding='utf-8')
                except (OSError, UnicodeDecodeError): errors.append('proof log unreadable')
    if variant == 'positive':
        marker = MARKER_PREFIX + variant + MARKER_SUFFIX
        if log.splitlines().count(marker) != 1 or log.count(MARKER_PREFIX) != 1: errors.append('positive native certificate marker missing/duplicated/wrong-case')
        if re.search(r'(?m)^.*(?:Fatal error:|error:|Cannot prove|Assertion might not hold).*$', log):
            errors.append('positive proof log contains diagnostic error')
        if stage.get('exit') != 0: errors.append('positive proof did not exit 0')
        if stage.get('error_count') not in (None, 0): errors.append('positive proof reported errors')
        if stage.get('additional_fatal') is True or stage.get('located_errors') not in (None, [], 0):
            errors.append('positive proof reported fatal or located errors')
    return errors, log


def run(args, *, engine=None, pins_loader=_load_pins, proof_runner=None,
        runtime_loader=None, env=None) -> dict[str, Any]:
    """Run fresh capture first, then only the exact requested mutable proof cases."""
    env = dict(os.environ if env is None else env)
    repo, evidence = Path(args.repo), Path(args.evidence)
    variants = _expected_variants(args)
    build_id = env.get('CLOUD_BUILD_ID')
    _validate_route(env, build_id, repo)
    pins = pins_loader(repo)
    if engine is None:
        import importlib.util
        path = Path(args.cloud_dir) / ENGINE_REL.name
        need(path.is_file() and not path.is_symlink() and sha(path.read_bytes()) == ENGINE_SHA256,
             'frozen fingerprint producer hash differs')
        spec = importlib.util.spec_from_file_location('r24_mut_proof_frozen_engine', path)
        need(spec is not None and spec.loader is not None, 'frozen fingerprint producer unavailable')
        engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(engine)
    need(repo.is_dir() and evidence.is_dir() and not evidence.is_symlink(),
         'proof repo and fresh evidence root must exist')
    summary_path = evidence / SUMMARY_REL
    need(not summary_path.exists() and not summary_path.is_symlink(), 'fresh mutable proof summary required')
    summary: dict[str, Any] = {
        'schema': SCHEMA, 'classification': 'INCOMPLETE_MUTABLE_PROOF', 'complete': False,
        'candidate': getattr(args, 'candidate', None), 'proof_mode': getattr(args, 'proof_mode', 'positive'),
        'proof_variants': variants, 'native_build_id': build_id,
        'r24_session_phase_id': env.get(R24_PHASE_ENV), 'r21_route_phase_id': env.get(R21_PHASE_ENV),
        'provider': env.get('SMALLSORT_EXECUTION_PROVIDER'), 'lane': env.get('LANE'),
        'profile': env.get('SORT4_SELECT_PROFILE'),
        'pins': {'path': PINS_REL.as_posix(), 'sha256': PINS_SHA256},
        'complete_source_observation': None, 'rows': {}, 'artifact_inventory': [],
        'accepted': False, 'proof_credit': 0, 'publication_allowed': False,
        'body_proof_run': False, 'typed_admission': False,
    }

    def save(error: BaseException | None = None):
        if error is not None:
            summary['exception'] = {'type': type(error).__name__, 'message': str(error),
                                    'traceback': traceback.format_exc()}
        inventory=[]
        for row in summary['rows'].values():
            case=evidence / row['case_path']
            for path in sorted(case.glob('r24-mut-proof-*')):
                if path.is_file() and not path.is_symlink():
                    raw=path.read_bytes()
                    inventory.append({'path':path.relative_to(evidence).as_posix(),
                                      'bytes':len(raw),'sha256':sha(raw)})
        summary['artifact_inventory']=inventory
        _write(summary_path, summary)

    try:
        # This call is intentionally first: it regenerates and validates the full source-only matrix.
        captured = engine.run(args)
        summary['complete_source_observation'] = captured
        capture_errors = _validate_capture(captured, pins, build_id)
        if capture_errors:
            summary['incomplete_reasons'] = capture_errors
            save()
            return summary
        if runtime_loader is not None:
            runtime = runtime_loader(args)
        else:
            old_path = Path(args.cloud_dir) / 'select-callee-r24-mut-capture.py'
            old_loader = getattr(engine, 'load_old_adapter', None)
            need(callable(old_loader), 'frozen engine old adapter loader unavailable')
            old = old_loader(Path(args.cloud_dir))
            runtime = old.load_capture_runtime(repo, Path(args.cloud_dir), evidence)
        if proof_runner is None:
            proof_runner = _proof_callback(runtime, args)
        source_repo = evidence / 'cases/r24-mut-capture/source-repository'
        writers = engine.load_old_adapter(Path(args.cloud_dir)).load_source_writers(source_repo)
        owner = writers['owner']
        for variant in variants:
            source_row = captured['rows'][variant]
            case_rel = source_row.get('case_path')
            need(isinstance(case_rel, str) and not Path(case_rel).is_absolute() and '..' not in Path(case_rel).parts,
                 'fingerprint case path is not evidence-relative: ' + variant)
            case = evidence / case_rel
            expected = {'original_sha256': source_row['original_sha256'],
                        'verified_sha256': source_row['verified_sha256']}
            before, errors = _source_pair(case, expected, owner)
            row = {'variant': variant, 'case_path': case_rel, 'stage_name': 'r24-mut-proof-' + variant,
                   'classification': 'UNKNOWN_UNCLASSIFIED', 'proof_stage': None,
                   'source_before': before, 'source_after': None, 'source_intact': False,
                   'errors': errors, 'accepted': False, 'proof_credit': 0,
                   'publication_allowed': False}
            summary['rows'][variant] = row
            if errors:
                continue
            # Per-case opt-ins exist only around the actual native LINK.stage call.
            stage_env = {CASE_ENV: variant, ROOT_ENV: str(repo)}
            need(not any(key in env for key in stage_env), 'mutable proof opt-in already ambient')
            try:
                os.environ.update(stage_env)
                stage = proof_runner(case=case, variant=variant,
                                     name='r24-mut-proof-' + variant, build_id=build_id)
            except BaseException as exc:
                row['proof_stage_exception'] = {'type': type(exc).__name__, 'message': str(exc)}
                row['errors'].append('proof stage raised: ' + type(exc).__name__)
                row['proof_stage'] = {'status': 'EXCEPTION', 'exception_type': type(exc).__name__}
                after, after_errors = _source_pair(case, expected, owner)
                row['source_after'] = after
                row['source_intact'] = before == after and not after_errors
                row['errors'].extend(after_errors)
                raise
            finally:
                os.environ.pop(CASE_ENV, None)
                os.environ.pop(ROOT_ENV, None)
            row['proof_stage'] = stage
            after, after_errors = _source_pair(case, expected, owner)
            row['source_after'] = after
            row['source_intact'] = before == after and not after_errors
            stage_errors, log = _stage_errors(stage, case, row['stage_name'], before, after, variant)
            row['native_marker_seen'] = log.count(MARKER_PREFIX + variant + MARKER_SUFFIX) if variant == 'positive' else None
            row['errors'].extend(after_errors + stage_errors)
            if variant == 'positive' and not row['errors']:
                row['classification'] = 'POSITIVE_PROOF_STAGE_RAN_SOURCE_INTACT'
            elif variant != 'positive':
                # A negative result is never promoted without reviewed, case-specific refusal pins.
                row['classification'] = 'UNKNOWN_UNCLASSIFIED'
                row['errors'].append('negative diagnostic acceptance is not pinned')
        summary['complete'] = all(row.get('proof_stage') is not None and not row['errors']
                                  for row in summary['rows'].values())
        summary['classification'] = ('COMPLETE_MUTABLE_PROOF_STAGES_SOURCE_REPORTED'
                                     if summary['complete'] else 'INCOMPLETE_MUTABLE_PROOF')
        summary['accepted'] = False
        summary['proof_credit'] = 0
        summary['publication_allowed'] = False
        summary['body_proof_run'] = bool(summary['rows'])
        save()
        return summary
    except BaseException as exc:
        summary['complete'] = False
        summary['classification'] = 'INCOMPLETE_MUTABLE_PROOF'
        summary.setdefault('incomplete_reasons', []).append(type(exc).__name__ + ': ' + str(exc))
        save(exc)
        raise
