#!/usr/bin/env python3
"""Pinned Cloud adapter for the inactive R21 fractional proof runner.

This entry point consumes the completed fingerprint JSON and captured
candidate source. It does not prepare or extract source and grants no proof
acceptance or proof credit.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import time
from typing import Any

CASE = 'nine-body-a1-owned-forget'
FINGERPRINT_HELPER_SHA256 = '9cb4dee13b134f1ba328b35c23e667c4ef73961cf980147fdda8f9cb56d16c71'
PROOF_HELPER_SHA256 = 'b37f38ec991e10ecf474cc1dec5e2a0fd59232ac70ac5399e66e9775a3d9ed7b'
R20_HELPER_SHA256 = '83d2d0940fcb255a58b97db8d6161ec3b39660a62905f89a33f926a96d3099ba'
O26_RECIPE_SHA256 = '464eef45b08b8724eba949289eff9cd745f48d65d0031ffae5675738856d562c'
O26_REFRESH_SHA256 = '2cd963cc3d28c69370260cd2154e7284e189fea953928c3fc829f2fd53766af3'
TRANSFORM_SHA256 = '8a23499c9852dfdc9973cca186daa83dcc2f7836642c40627ab1def6dd763772'
REPAIR_SHA256 = '3646b05602b7dce35cd4b2ab8f74d8cfe280d65df2637ac4f6cc0a128dd7e2a3'
CONTROLS_SHA256 = '533c3d9be5249a40b2f0ad701cfaff6e95e688ecfb5b9c024c5dd2a56dc5124d'
CAPTURE_SHA256 = 'ffc3653263e86c5afa4f82440f10a2207e75ad8083bdad5f784597fe0dbaa84f'
PROVIDER_SHA256 = '771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616'
TARGET_HELPER_SHA256 = '5c51ae49766ec7f8dda5ac548555773bce34398462376a4ff56653d6bef91e93'
AST_INVENTORY_SHA256 = '100bd96f885dccba31d0848e9c69d586b902e11c4630b869be04094e0203b2de'
OPT_IN_KEY = 'SORT4_R21_FRACTIONAL_FORGET'
VARIANT_KEY = 'SORT4_R21_FRACTIONAL_VARIANT'
R20_OPT_IN_KEY = 'SORT4_R20_FINAL_SELECT_REPAIR'
SNAPSHOT_NAMES = ('unit', *(f'body-{index}' for index in range(9)))
CAPTURE_LOG = 'nine-body-fingerprint-refusal.log'
PHASE_ENV = 'SORT4_R20_CALLEE_PHASE_ID'
PHASE = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
R24_SESSION_ENV = 'SORT4_R24_SESSION_PHASE_ID'
R24_SESSION_PHASE = 'SORT4-ACTUAL-SELECT-2026-10-24-R24'
CHECKED_OUTCOMES_KEY = 'SORT4_R24_CHECKED_POINTER_OUTCOMES'


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError('R21-FRACTIONAL-PROOF-ENTRY: ' + why)


def load(path: Path, name: str, expected_sha256: str):
    need(path.is_file() and sha(path.read_bytes()) == expected_sha256,
         'pinned module differs: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None,
         'module spec unavailable: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    need(sha(path.read_bytes()) == expected_sha256,
         'module changed during import: ' + str(path))
    return module


def load_runtime(repo: Path, cloud_dir: Path, evidence: Path):
    """Load the exact fingerprint/proof adapters and their pinned O26 base."""
    provider = load(cloud_dir / 'provider.py', 'r21_fractional_proof_entry_provider',
                    PROVIDER_SHA256)
    need(callable(getattr(provider, 'require_supported_provider', None)),
         'pinned provider module lacks its Cloud check')
    fractional = load(cloud_dir / 'select-callee-r21-fractional.py',
                      'r21_fractional_proof_entry_fingerprint',
                      FINGERPRINT_HELPER_SHA256)
    proof = load(cloud_dir / 'select-callee-r21-fractional-proof.py',
                 'r21_fractional_proof_entry_classifier', PROOF_HELPER_SHA256)
    target_helper = load(cloud_dir / 'select-callee-r22-control-targets.py',
                         'r21_fractional_proof_entry_targets', TARGET_HELPER_SHA256)
    ast_inventory = load(cloud_dir / 'select-callee-r24-ast-inventory.py',
                         'r24_positive_ast_inventory', AST_INVENTORY_SHA256)
    transform, r20, o26, refresh = fractional.pinned_dependencies(
        repo, cloud_dir, evidence)
    need(sha((repo / fractional.TRANSFORM_REL).read_bytes()) == TRANSFORM_SHA256 and
         fractional.TRANSFORM_REPAIR_SHA256 == REPAIR_SHA256 and
         fractional.TRANSFORM_CONTROLS_SHA256 == CONTROLS_SHA256 and
         fractional.R20_HELPER_SHA256 == R20_HELPER_SHA256 and
         fractional.O26_RECIPE_SHA256 == O26_RECIPE_SHA256 and
         fractional.O26_REFRESH_SHA256 == O26_REFRESH_SHA256 and
         fractional.CAPTURE_SHA256 == CAPTURE_SHA256,
         'fractional dependency closure differs')
    capture = o26.load_capture(repo, 'r21_fractional_proof_entry')
    need(callable(getattr(capture, 'refusal_fingerprint', None)) and
         callable(getattr(capture, 'clear_semantic_opt_ins', None)),
         'pinned capture lacks mode-9 interface')
    need(callable(getattr(r20, 'classify_bound_row', None)) and
         callable(getattr(o26, 'proof_stage', None)) and
         callable(getattr(ast_inventory, 'run_positive_ast_inventory', None)) and
         callable(getattr(transform, 'transform', None)),
         'pinned proof services are incomplete')
    return {'provider': provider, 'fractional': fractional, 'proof': proof,
            'target_helper': target_helper, 'transform': transform,
            'r20': r20, 'o26': o26, 'refresh': refresh, 'capture': capture,
            'ast_inventory': ast_inventory}


def run_proof_stage(*, runtime, repo: Path, case: Path, name: str,
                    tool_home: Path, schema: Path, compiler_sysroot: Path,
                    deadline_epoch: int, variant: str,
                    positive_ast_inventory: bool,
                    expected_sources: dict[str, str],
                    expected_snapshots: dict[str, Any],
                    checked_pointer_outcomes: bool = False) -> dict[str, Any]:
    """Inventory baseline AST, then opt in only around the ordinary proof."""
    need(name == 'r20-merged-optin' and variant in runtime['proof'].VARIANTS,
         'unexpected proof-stage identity or fractional variant')
    need(os.environ.get(OPT_IN_KEY) == '1' and
         R20_OPT_IN_KEY not in os.environ and VARIANT_KEY not in os.environ and
         CHECKED_OUTCOMES_KEY not in os.environ,
         'proof-stage opt-ins are not isolated to the callback')
    need(type(checked_pointer_outcomes) is bool, 'checked outcomes option must be boolean')
    if checked_pointer_outcomes:
        need(os.environ.get(R24_SESSION_ENV) == R24_SESSION_PHASE and
             os.environ.get(PHASE_ENV) == PHASE and
             os.environ.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
             not os.environ.get('GITHUB_ACTIONS'),
             'checked outcomes require exact R24 Cloud session on the R21 route')
    os.environ[R20_OPT_IN_KEY] = '1'
    os.environ[VARIANT_KEY] = variant
    try:
        diagnostic = None
        if positive_ast_inventory and variant == 'positive':
            diagnostic = runtime['ast_inventory'].run_positive_ast_inventory(
                cap=runtime['capture'], repo=repo, case=case,
                tool_home=tool_home, schema=schema,
                compiler_sysroot=compiler_sysroot,
                deadline_epoch=deadline_epoch, variant=variant,
                expected_sources=expected_sources,
                expected_snapshots=expected_snapshots)
        if checked_pointer_outcomes:
            os.environ[CHECKED_OUTCOMES_KEY] = '1'
        stage = runtime['o26'].proof_stage(repo, case, tool_home, schema,
            compiler_sysroot, deadline_epoch, name, 'r21_fractional_' + variant)
        if diagnostic is not None and isinstance(stage, dict):
            stage = dict(stage)
            stage['r24_positive_ast_inventory'] = diagnostic
        if checked_pointer_outcomes and isinstance(stage, dict):
            stage = dict(stage)
            stage['r24_checked_pointer_outcomes_requested'] = True
        return stage
    finally:
        os.environ.pop(CHECKED_OUTCOMES_KEY, None)
        os.environ.pop(R20_OPT_IN_KEY, None)
        os.environ.pop(VARIANT_KEY, None)


def _snapshot_path(case: Path, label: str) -> Path:
    return case / f'actual-nested-9-{label}.marshal'


def _archive_capture(case: Path, archive: Path, label: str,
                     result: object, evidence: Path) -> dict[str, Any]:
    """Preserve this call's existing exact mode-9 output names and hashes."""
    archive.mkdir(parents=True, exist_ok=False)
    files: dict[str, Any] = {}
    for name in (*SNAPSHOT_NAMES, CAPTURE_LOG):
        source = case / (CAPTURE_LOG if name == CAPTURE_LOG else
                         f'actual-nested-9-{name}.marshal')
        need(not source.is_symlink(),
             'capture output unexpectedly became a symlink: ' + str(source))
        need(not source.exists() or source.is_file(),
             'capture output unexpectedly became a non-file: ' + str(source))
        if source.is_file():
            target = archive / source.name
            shutil.copyfile(source, target)
            data = target.read_bytes()
            files[name] = {'file': str(target.relative_to(case)),
                           'bytes': len(data), 'sha256': sha(data)}
        else:
            files[name] = {'file': None, 'bytes': None, 'sha256': None}
    return {'call': label, 'case': str(case.relative_to(evidence)),
            'directory': str(archive.relative_to(case)),
            'files': files, 'returned_type': type(result).__name__}


def _clear_capture_outputs(case: Path) -> None:
    """Remove only the known ten snapshots and their mode-9 log."""
    for path in [*(_snapshot_path(case, label) for label in SNAPSHOT_NAMES),
                 case / CAPTURE_LOG]:
        if path.is_symlink() or path.is_file():
            path.unlink()
        elif path.exists():
            raise RuntimeError('R21-FRACTIONAL-PROOF-ENTRY: known capture output is not a file: ' +
                               str(path))


def run(args, *, runtime_loader=load_runtime,
        env: dict[str, str] | None = None) -> dict[str, Any]:
    live_env = dict(os.environ)
    selected_env = dict(live_env if env is None else env)
    need(selected_env == live_env,
         'entry route environment must be the live Cloud process environment')
    need(selected_env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
         selected_env.get(PHASE_ENV) == PHASE and
         not selected_env.get('GITHUB_ACTIONS'),
         'fresh R21 Cloud proof phase required')
    need(OPT_IN_KEY not in selected_env and R20_OPT_IN_KEY not in selected_env and
         VARIANT_KEY not in selected_env and CHECKED_OUTCOMES_KEY not in selected_env and
         not any(key.startswith('SORT4_R21_FRACTIONAL_') for key in selected_env),
         'proof opt-ins and variant must not be ambient')
    positive_ast_inventory = bool(getattr(args, 'positive_ast_inventory', False))
    checked_pointer_outcomes = getattr(args, 'checked_pointer_outcomes', False)
    need(type(checked_pointer_outcomes) is bool, 'checked outcomes option must be boolean')
    if positive_ast_inventory or checked_pointer_outcomes:
        need(selected_env.get(PHASE_ENV) == PHASE and
             selected_env.get(R24_SESSION_ENV) == R24_SESSION_PHASE and
             selected_env.get('SMALLSORT_EXECUTION_PROVIDER') == 'cloud-build' and
             not selected_env.get('GITHUB_ACTIONS'),
             'R24 diagnostics/checked outcomes require exact R24 Cloud session on the R21 route')
    runtime = runtime_loader(args.repo, args.cloud_dir, args.evidence)
    provider = runtime.get('provider')
    need(callable(getattr(provider, 'require_supported_provider', None)),
         'pinned provider checker is required')
    provider_record = provider.require_supported_provider()
    need(isinstance(provider_record, dict) and
         provider_record.get('provider') == 'cloud-build',
         'actual supported Cloud Build provider required')
    fractional = runtime['fractional']
    proof = runtime['proof']
    capture = runtime['capture']
    fractional.require_cloud(selected_env)
    proof.require_route(selected_env, fractional.PHASE_ENV, fractional.PHASE,
                        OPT_IN_KEY)
    need(fractional.PHASE_ENV == PHASE_ENV and fractional.PHASE == PHASE,
         'pinned fingerprint helper uses a different R21 route identity')

    pins_path = args.pins_json
    need(pins_path.is_file() and not pins_path.is_symlink(),
         'completed fingerprint JSON is missing or symlinked')
    pin_bytes = pins_path.read_bytes()
    fingerprint_record = json.loads(pin_bytes)
    pins = proof.fingerprint_to_pins(fingerprint_record)
    need(proof.validate_pins(pins) is pins,
         'completed fingerprint pin manifest failed validation')
    refresh = runtime['refresh']
    default_snapshots = {'unit': refresh.UNIT,
        **{f'body-{index}': value
           for index, value in enumerate(refresh.BODIES)}}
    need(pins.get('snapshot_pins') == default_snapshots,
         'fingerprint location-control pins differ from the pinned O26 defaults')

    base = args.evidence / 'cases/candidate/capture' / CASE
    original_path = base / 'original/lib.rs'
    verified_path = base / 'verified/lib.rs'
    need(original_path.is_file() and verified_path.is_file() and
         not original_path.is_symlink() and not verified_path.is_symlink(),
         'captured candidate source pair is missing or symlinked')
    evidence_real = args.evidence.resolve()
    need(original_path.resolve().is_relative_to(evidence_real) and
         verified_path.resolve().is_relative_to(evidence_real),
         'captured candidate source escapes the evidence root')
    original = original_path.read_bytes()
    base_verified = verified_path.read_bytes()
    need(sha(original) == pins['base_original_sha256'] and
         sha(base_verified) == pins['base_verified_sha256'],
         'captured candidate source differs from pinned fingerprint input')
    need(sha(pins_path.read_bytes()) == sha(pin_bytes),
         'fingerprint pins changed while loading')

    target_map = None
    target_map_bytes = None
    target_helper = runtime['target_helper']
    tool_spec = None
    tool_spec_file = None
    tool_spec_path = args.tool_home / target_helper.TOOL_SPEC_FILE
    if args.target_map is not None:
        need(args.target_map.is_file() and not args.target_map.is_symlink(),
             'caller-supplied diagnostic target map is missing or symlinked')
        target_map_bytes = args.target_map.read_bytes()
        target_map = json.loads(target_map_bytes)
        need(tool_spec_path.is_file() and not tool_spec_path.is_symlink(),
             'pinned tool lib.rsspec file is missing or symlinked')
        tool_spec = tool_spec_path.read_bytes()
        relative_spec = target_helper.TOOL_SPEC_FILE
        absolute_spec = str(tool_spec_path.resolve())
        spec_records = target_map.get('targets') if isinstance(target_map, dict) else None
        spec_files = {spec_records.get(name, {}).get('file')
                      for name in target_helper.SPEC_PRECONDITION_LINE
                      if isinstance(spec_records, dict) and
                         isinstance(spec_records.get(name), dict)}
        tool_spec_file = (relative_spec if spec_files == {relative_spec}
                          else absolute_spec)

    dependencies = {
        'fingerprint_helper_sha256': FINGERPRINT_HELPER_SHA256,
        'proof_helper_sha256': PROOF_HELPER_SHA256,
        'transform_sha256': TRANSFORM_SHA256,
        'transform_repair_sha256': REPAIR_SHA256,
        'transform_controls_sha256': CONTROLS_SHA256,
        'r20_helper_sha256': R20_HELPER_SHA256,
        'o26_recipe_sha256': O26_RECIPE_SHA256,
        'o26_refresh_sha256': O26_REFRESH_SHA256,
        'capture_sha256': CAPTURE_SHA256,
        'provider_sha256': PROVIDER_SHA256,
        'target_helper_sha256': TARGET_HELPER_SHA256,
        'provider_record': provider_record,
        'pins_json_sha256': sha(pin_bytes),
    }
    if target_map_bytes is not None:
        dependencies.update(target_map_sha256=sha(target_map_bytes),
                            tool_spec_sha256=sha(tool_spec))

    capture_call_counts: dict[Path, int] = {}
    capture_history: list[dict[str, Any]] = []

    def refusal_fingerprint(case: Path, source: dict, capture_args):
        resolved_case = case.resolve()
        count = capture_call_counts.get(resolved_case, 0) + 1
        capture_call_counts[resolved_case] = count
        need(count <= 2, 'unexpected third fingerprint capture for one proof case')
        # This removes stale outputs before each stage. Previous call outputs
        # were copied into the case-local archive and their hashes are stored
        # separately in this return value and the proof row.
        _clear_capture_outputs(case)
        capture.clear_semantic_opt_ins()
        try:
            result = capture.refusal_fingerprint(case, source, capture_args)
        except BaseException:
            try:
                archive = case / 'r21-fractional-capture-history' / f'call-{count:02d}'
                archived = _archive_capture(case, archive, f'call-{count:02d}',
                                             {'status': 'EXCEPTION'}, args.evidence)
                capture_history.append(archived)
            except BaseException:
                pass
            raise
        finally:
            capture.clear_semantic_opt_ins()
        archive = case / 'r21-fractional-capture-history' / f'call-{count:02d}'
        archived = _archive_capture(case, archive, f'call-{count:02d}', result,
                                     args.evidence)
        capture_history.append(archived)
        if isinstance(result, dict):
            result = dict(result)
            result['capture_archive'] = archived
        return result

    def proof_stage(*, case: Path, name: str, tool_home: Path,
                    schema: Path, compiler_sysroot: Path,
                    deadline_epoch: int, variant: str):
        expected_sources = {}
        expected_snapshots = {}
        if positive_ast_inventory and variant == 'positive':
            expected_sources = {
                'original/lib.rs': sha(original),
                'verified/lib.rs': pins['cases'][variant]['verified_sha256'],
            }
            expected_snapshots = pins['cases'][variant]['snapshots']
        return run_proof_stage(runtime=runtime, repo=args.repo, case=case,
            name=name, tool_home=tool_home, schema=schema,
            compiler_sysroot=compiler_sysroot, deadline_epoch=deadline_epoch,
            variant=variant, positive_ast_inventory=positive_ast_inventory,
            expected_sources=expected_sources,
            expected_snapshots=expected_snapshots,
            checked_pointer_outcomes=checked_pointer_outcomes)

    record_path = args.evidence / 'cases/r21-fractional-proof/r21-fractional-proof.json'
    try:
        record = proof.proof_batch(evidence=args.evidence, original=original,
            base_verified=base_verified, fingerprint_record=fingerprint_record,
            transform=runtime['transform'].transform, r20=runtime['r20'],
            proof_stage=proof_stage, refusal_fingerprint=refusal_fingerprint,
            tool_home=args.tool_home, schema=args.schema,
            compiler_sysroot=args.compiler_sysroot,
            deadline_epoch=args.deadline_epoch,
            phase_key=fractional.PHASE_ENV, phase_value=fractional.PHASE,
            opt_in_key=OPT_IN_KEY, env=selected_env,
            target_map=target_map, target_helper=target_helper,
            tool_spec=tool_spec, tool_spec_file=tool_spec_file)
    except BaseException:
        try:
            if record_path.is_file():
                record = json.loads(record_path.read_text())
                record['capture_archive_records'] = capture_history
                record['entry_dependencies'] = dependencies
                record['complete'] = False
                record['accepted'] = False
                record['proof_credit'] = False
                record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
        except BaseException:
            pass
        raise
    if target_map is not None:
        dependencies['target_map_canonical_sha256'] = record.get(
            'diagnostic_target_map_sha256')
    source_unchanged = (original_path.is_file() and verified_path.is_file() and
        sha(original_path.read_bytes()) == sha(original) and
        sha(verified_path.read_bytes()) == sha(base_verified))
    pins_unchanged = pins_path.is_file() and sha(pins_path.read_bytes()) == sha(pin_bytes)
    target_map_unchanged = (target_map_bytes is None or
        (args.target_map.is_file() and not args.target_map.is_symlink() and
         sha(args.target_map.read_bytes()) == sha(target_map_bytes)))
    tool_spec_unchanged = (tool_spec is None or
        (tool_spec_path.is_file() and not tool_spec_path.is_symlink() and
         sha(tool_spec_path.read_bytes()) == sha(tool_spec)))
    if (not source_unchanged or not pins_unchanged or not target_map_unchanged or
            not tool_spec_unchanged):
        record['complete'] = False
        record['classification'] = 'R21_FRACTIONAL_CLASSIFIED_PROOF_INCOMPLETE'
        record['entry_integrity_error'] = {
            'source_unchanged': source_unchanged,
            'pins_unchanged': pins_unchanged,
            'target_map_unchanged': target_map_unchanged,
            'tool_spec_unchanged': tool_spec_unchanged,
        }
    record['target_map_unchanged'] = target_map_unchanged
    record['tool_spec_unchanged'] = tool_spec_unchanged
    record['capture_archive_records'] = capture_history
    record['entry_dependencies'] = dependencies
    record['accepted'] = False
    record['proof_credit'] = False
    record_path.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('repo', 'cloud-dir', 'evidence', 'tool-home', 'schema',
                 'compiler-sysroot', 'pins-json'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--target-map', type=Path, default=None)
    parser.add_argument('--deadline-epoch', type=int, required=True)
    parser.add_argument('--positive-ast-inventory', action='store_true',
                        help='add one R24-only positive AST diagnostic before the proof stage')
    parser.add_argument('--checked-pointer-outcomes', action='store_true',
                        help='request exact R24 checked pointer call result projection for all proof variants')
    args = parser.parse_args(argv)
    need(args.deadline_epoch > int(time.time()), 'shared deadline has elapsed')
    record = run(args)
    print(json.dumps({'classification': record.get('classification'),
                      'complete': record.get('complete'),
                      'accepted': False, 'proof_credit': False}))
    return 0 if record.get('complete') is True else 4


if __name__ == '__main__':
    raise SystemExit(main())
