#!/usr/bin/env python3
"""Cloud-only R21 transport adapter for the separately authorized body lane."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import subprocess

HERE = Path('research/challenge-8/cloud-build/sort4-caller-entry-native')
PHASE = 'SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17'
AUTHORIZATION_PHASE = 'SORT4-ACTUAL-C2-2026-10-21-R17'
EXECUTION_PHASE_ID = 'SORT4-ACTUAL-SELECT-2026-10-23-R21'
EXECUTION_LANE = 'o26-sort4-body-r21'
ROUTED_PROFILE = 'A1-ACTUAL-BODY-R21-TRANSPORT-PROFILE.json'


def require_execution_route(env, profile=None):
    """Separate fresh R21 execution identity from the legacy backend protocol."""
    if (env.get('SMALLSORT_EXECUTION_PROVIDER') != 'cloud-build' or
            env.get('SORT4_R21_BODY_PHASE_ID') != EXECUTION_PHASE_ID or
            env.get('LANE') != EXECUTION_LANE or
            not env.get('CLOUD_BUILD_ID') or env.get('GITHUB_ACTIONS')):
        raise RuntimeError('A1 R21 entry requires fresh authorized Cloud lane')
    if profile is not None and (
            profile.get('execution_authority_phase_id') != EXECUTION_PHASE_ID or
            profile.get('execution_lane') != EXECUTION_LANE or
            profile.get('authorization_phase_id') != AUTHORIZATION_PHASE or
            profile.get('phase_id') != PHASE or
            profile.get('experiment_protocol_phase_id') != PHASE or
            profile.get('execution_mode') != 'actual-sort4-body-v1' or
            profile.get('body_action') != 'full-body-c1-recovery' or
            profile.get('cloud_build_enabled') is not True):
        raise RuntimeError('A1 R21 profile route/backend protocol binding differs')


def require_workspace_paths(paths):
    for key, value in paths.items():
        if not str(Path(value).resolve()).startswith('/workspace/'):
            raise RuntimeError('A1 R21 entry path outside workspace: ' + key)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path, name: str, expected: str):
    if not path.is_file() or sha(path) != expected:
        raise RuntimeError('A1 R21 entry helper pin differs: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('A1 R21 entry helper cannot load: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    if sha(path) != expected:
        raise RuntimeError('A1 R21 entry helper changed during import')
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('production-source', 'production-applied-patch', 'stock-home',
                'compiler-sysroot', 'evidence', 'proof-root', 'work-root', 'cloud-dir'):
        parser.add_argument('--' + key, type=Path, required=True)
    parser.add_argument('--deadline-epoch', type=int, required=True)
    a = parser.parse_args()
    require_execution_route(os.environ)
    require_workspace_paths({key: getattr(a, key) for key in
        ('production_source', 'production_applied_patch', 'stock_home',
         'evidence', 'proof_root', 'work_root', 'cloud_dir')})
    for checkout, key in ((a.proof_root, 'PROOF_SHA'), (a.cloud_dir.parents[2], 'INFRA_SHA')):
        head = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        if head != os.environ.get(key):
            raise RuntimeError('A1 R21 entry published checkout pin differs: ' + key)
    expected_profile = os.environ.get('SORT4_A1_PROFILE_SHA256')
    profile_candidate = a.proof_root / HERE / ROUTED_PROFILE
    matches = [profile_candidate] if (profile_candidate.is_file() and
        sha(profile_candidate) == expected_profile) else []
    if len(matches) != 1:
        raise RuntimeError('A1 R21 entry profile pin differs')
    profile_path = matches[0]
    profile = json.loads(profile_path.read_text())
    require_execution_route(os.environ, profile)
    # The fresh R21 marker/lane above gates execution. Only then install the
    # legacy A1/R17 identifiers as backend protocol values for pinned helpers.
    os.environ['SORT4_A1_PHASE_ID'] = PHASE
    os.environ['SORT4_A1_AUTHORIZATION_PHASE_ID'] = AUTHORIZATION_PHASE
    os.environ['SORT4_A1_CHECKED_TRAIT_CONTRACT'] = '1'
    manifest_path = a.proof_root / HERE / 'CALLER-ENTRY-MANIFEST.json'
    if sha(manifest_path) != profile['caller_manifest_sha256']:
        raise RuntimeError('A1 R21 entry legacy manifest pin differs')
    manifest = json.loads(manifest_path.read_text())
    c4 = load(a.cloud_dir / 'sort4-caller-entry-native/selected-runtime.py',
              'a1_entry_runtime_r21', manifest['runtime_helpers_sha256']['selected-runtime.py'])
    audit = load(a.cloud_dir / 'sort4-first-scope-audit.py', 'a1_entry_audit_r21',
                 manifest['runtime_helpers_sha256']['sort4-first-scope-audit.py'])
    ghost = load(a.cloud_dir / 'sort4-native-c1-bound/ghost-strip.py',
                 'a1_entry_ghost_r21', manifest['ghost_strip_sha256'])
    driver = load(a.cloud_dir / 'sort4-caller-entry-native/driver.py',
                  'a1_entry_driver_r21', profile['caller_driver_sha256'])
    runner = load(a.cloud_dir / 'sort4-caller-entry-native/a1-runner-r21.py',
                  'a1_entry_runner_r21', profile['a1_runner_sha256'])
    result = runner.run(a, c4=c4, audit=audit, driver=driver,
                        manifest=manifest, ghost=ghost)
    a.evidence.mkdir(parents=True, exist_ok=True)
    target = a.evidence / 'diagnostic-audit.json'
    if not target.exists():
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
