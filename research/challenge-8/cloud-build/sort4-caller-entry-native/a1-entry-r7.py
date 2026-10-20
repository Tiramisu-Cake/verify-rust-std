#!/usr/bin/env python3
"""Cloud-only adapter for the existing recovery lane's A1 continuation."""
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
AUTHORIZATION_PHASE = 'SORT4-PACKAGING-NATIVE-PROOF-2026-10-20-R7'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path, name: str, expected: str):
    if not path.is_file() or sha(path) != expected:
        raise RuntimeError('A1 entry helper pin differs: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('A1 entry helper cannot load: ' + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    if sha(path) != expected:
        raise RuntimeError('A1 entry helper changed during import')
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('production-source', 'production-applied-patch', 'stock-home',
                'compiler-sysroot', 'evidence', 'proof-root', 'work-root', 'cloud-dir'):
        parser.add_argument('--' + key, type=Path, required=True)
    parser.add_argument('--deadline-epoch', type=int, required=True)
    a = parser.parse_args()
    if (os.environ.get('SMALLSORT_EXECUTION_PROVIDER') != 'cloud-build' or
            os.environ.get('SORT4_A1_PHASE_ID') != PHASE or
            os.environ.get('SORT4_A1_AUTHORIZATION_PHASE_ID') != AUTHORIZATION_PHASE or
            os.environ.get('SORT4_A1_CHECKED_TRAIT_CONTRACT') != '1' or
            os.environ.get('LANE') != 'o26-sort4-c1-current-recovery' or
            not os.environ.get('CLOUD_BUILD_ID') or os.environ.get('GITHUB_ACTIONS')):
        raise RuntimeError('A1 entry requires authorized Cloud lane')
    for key in ('production_source', 'production_applied_patch', 'stock_home',
                'evidence', 'proof_root', 'work_root', 'cloud_dir'):
        if not str(getattr(a, key).resolve()).startswith('/workspace/'):
            raise RuntimeError('A1 entry path outside workspace: ' + key)
    for checkout, key in ((a.proof_root, 'PROOF_SHA'), (a.cloud_dir.parents[2], 'INFRA_SHA')):
        head = subprocess.check_output(['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
        if head != os.environ.get(key):
            raise RuntimeError('A1 entry published checkout pin differs: ' + key)
    profile_path = a.proof_root / HERE / 'A1-PACKAGING-R7-PROFILE-2026-10-20.json'
    if sha(profile_path) != os.environ.get('SORT4_A1_PROFILE_SHA256'):
        raise RuntimeError('A1 entry profile pin differs')
    profile = json.loads(profile_path.read_text())
    if (profile.get('authorization_phase_id') != AUTHORIZATION_PHASE or
            profile.get('experiment_protocol_phase_id') != PHASE):
        raise RuntimeError('A1 entry authorization/protocol binding differs')
    manifest_path = a.proof_root / HERE / 'CALLER-ENTRY-MANIFEST.json'
    if sha(manifest_path) != profile['caller_manifest_sha256']:
        raise RuntimeError('A1 entry legacy manifest pin differs')
    manifest = json.loads(manifest_path.read_text())
    c4 = load(a.cloud_dir / 'sort4-caller-entry-native/selected-runtime.py',
              'a1_entry_runtime', manifest['runtime_helpers_sha256']['selected-runtime.py'])
    audit = load(a.cloud_dir / 'sort4-first-scope-audit.py', 'a1_entry_audit',
                 manifest['runtime_helpers_sha256']['sort4-first-scope-audit.py'])
    ghost = load(a.cloud_dir / 'sort4-native-c1-bound/ghost-strip.py',
                 'a1_entry_ghost', manifest['ghost_strip_sha256'])
    driver = load(a.cloud_dir / 'sort4-caller-entry-native/driver.py',
                  'a1_entry_driver', profile['caller_driver_sha256'])
    runner = load(a.cloud_dir / 'sort4-caller-entry-native/a1-runner-r7.py',
                  'a1_entry_runner_r7', profile['a1_runner_sha256'])
    result = runner.run(a, c4=c4, audit=audit, driver=driver,
                        manifest=manifest, ghost=ghost)
    a.evidence.mkdir(parents=True, exist_ok=True)
    target = a.evidence / 'diagnostic-audit.json'
    # The runner owns per-row observations; this adapter preserves them whole.
    if not target.exists():
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
