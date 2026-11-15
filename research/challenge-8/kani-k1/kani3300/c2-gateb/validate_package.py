#!/usr/bin/env python3
"""Static preparation validation only: Python, Git identities, no builds."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
KANI = Path('/root/kani-fix-3300-c2-gateb-w15')
STD = Path('/root/verify-rust-std-kani3300-gateb-prime')
OLD = Path('/root/kani-fix-3300-sel1-replay-w15')
C2 = 'ad499e41dd2db9ccd432f89721638a1f3a0bbd44'
C1_CI = '0c1cc8a7d05184044d496b01f5ed41cebfde0cac'
PREFIX = 'scripts/kani3300-replay/'
WORKFLOW = '.github/workflows/kani3300-replay.yml'

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args], text=True).strip()

def blob(repo, sha, path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', f'{sha}:{path}'])

def digest(data): return hashlib.sha256(data).hexdigest()

def main():
    package = json.loads((HERE / 'PACKAGE.json').read_text())
    for rel, expected in package['files_sha256'].items():
        assert digest((HERE / rel).read_bytes()) == expected, rel
    overlay = package['kani_ci_overlay_commit']
    assert git(KANI, 'rev-parse', overlay + '^') == C2
    assert git(KANI, 'rev-list', '--count', C2 + '..' + overlay) == '1'
    changed = git(KANI, 'diff', '--name-only', C2, overlay).splitlines()
    assert all(p == WORKFLOW or p.startswith(PREFIX) for p in changed)
    assert not git(KANI, 'status', '--porcelain')
    for p in sorted((HERE / 'ci/full-export').rglob('*')):
        if not p.is_file(): continue
        rel = p.relative_to(HERE / 'ci/full-export').as_posix()
        assert blob(KANI, overlay, rel) == p.read_bytes() == (KANI / rel).read_bytes(), rel
    manifest = json.loads((HERE / 'ci/REPLAY-CI-OVERLAY.json').read_text())
    for rel, expected in manifest['full_export_file_sha256'].items():
        assert digest(blob(KANI, overlay, rel)) == expected, rel
    assert manifest['source']['source_binding_sha256'] == digest((HERE / 'ci/c2-source-binding.json').read_bytes())
    assert manifest['request']['sha256'] == digest((HERE / 'CI-REQUEST.json').read_bytes())
    assert (HERE / 'CI-REQUEST.json').read_bytes() == (HERE / 'ci/CI-REQUEST.json').read_bytes()
    for p in (HERE / 'ci').iterdir():
        if p.name in ('CI-REQUEST.json', 'REPLAY-CI-OVERLAY.json', 'c2-source-binding.json',
                      'gateb-prime-test-only.patch', 'replay.py', 'test_replay.py'):
            assert p.read_bytes() == (KANI / PREFIX / p.name).read_bytes(), p.name
    spec = importlib.util.spec_from_file_location('replay', HERE / 'ci/replay.py')
    replay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay)
    identity = replay.verify_source(Path('/root/kani-fix-3300-c2-s6'))
    req = replay.load_request()
    old_request = json.loads(blob(OLD, C1_CI, PREFIX + 'CI-REQUEST.json'))
    for old, new in zip(old_request['roots'], req['roots']):
        new['argv'][0] = '<EXACT_C1_KANI_BINARY>'
        assert old == new
    for key in ('flags', 'patched_file_sha256', 'test_only_library_tree', 'test_overlay_commit', 'test_patch_sha256', 'selected_library_tree', 'nightly'):
        assert req[key] == old_request[key], key
    assert git(STD, 'rev-parse', 'HEAD') == '01d75b8e839c751e7ab679fdaaa5fba6384983b6'
    assert not git(STD, 'status', '--porcelain')
    assert git(STD, 'rev-parse', replay.STD_SHA + ':library') == replay.STD_TREE
    assert git(STD, 'rev-parse', req['test_overlay_commit'] + ':library') == req['test_only_library_tree']
    for rel, expected in replay.PATCHED_FILE_HASHES.items():
        assert digest((STD / rel).read_bytes()) == expected, rel
    patch = (HERE / 'test-only.patch').read_bytes()
    assert patch == blob(OLD, C1_CI, PREFIX + 'gateb-prime-test-only.patch')
    assert patch == (HERE / 'ci/gateb-prime-test-only.patch').read_bytes()
    library_diff = git(STD, 'diff', '--name-only', replay.STD_SHA, req['test_overlay_commit'], '--', 'library').splitlines()
    assert sorted(library_diff) == sorted(replay.PATCHED_FILE_HASHES)
    subprocess.run(['git', '-C', str(KANI), 'diff', '--check', C2, overlay], check=True)
    print(json.dumps({'status': 'PASS', 'kani_overlay': overlay, 'ci_only_paths': changed,
                      'source': identity, 'std_patch_byte_identical_to_c1': True,
                      'rows_profile_targets_harnesses_unchanged': True,
                      'package_files_verified': len(package['files_sha256']),
                      'proof_status': 'NOT_RUN', 'review': 'COORDINATOR_PENDING'}, indent=2))

if __name__ == '__main__':
    sys.dont_write_bytecode = True
    main()
