"""Read-only static audit of the issued exact package; outputs only here."""
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path('/root/verify-rust-std-kani3300-g0')
BASE = Path('research/challenge-8/kani-k1/kani3300/ch8-s2')
OUT = Path(__file__).resolve().parent
PACKAGE = ROOT / BASE / 'batch-r5'
REV = '53008fd4de6bb5719fd232b1ddb7e875b5112012'

def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2) + '\n')

paths = git(ROOT, 'ls-tree', '-r', '--name-only', REV, '--', str(BASE / 'batch-r5')).decode().splitlines()
for name in paths:
    assert (ROOT / name).read_bytes() == git(ROOT, 'show', REV + ':' + name), name
entries = []
for line in (PACKAGE / 'MANIFEST.sha256').read_text().splitlines():
    digest, name = line.split('  ', 1)
    assert sha((PACKAGE / name).read_bytes()) == digest, name
    entries.append({'path': name, 'sha256': digest})
assert len(paths) == 75 and len(entries) == 74
assert set(x['path'] for x in entries) == {str(Path(x).relative_to(BASE / 'batch-r5')) for x in paths} - {'MANIFEST.sha256'}
save('PACKAGE-HASHES.json', {'package_commit': REV, 'tracked_files': len(paths), 'manifest_hashes': len(entries), 'all_committed_bytes_match': True, 'files': entries})
pins = json.loads((PACKAGE / 'PINS.json').read_text())
save('INPUTS.json', {'package_commit': REV, 'task_commit': 'cd5da9a56e145dfef0e14a78a5379659d1c77cd6', 'addendum_commit': 'e333995f0089a629e0ccbaf1a477248ff5fc31e2', 'pins': pins})
ns = {'__file__': str(PACKAGE / 'validate_package.py'), '__name__': 'review14_reexecuted_package_validator'}
source = (PACKAGE / 'validate_package.py').read_text()
exec(compile(source, ns['__file__'], 'exec'), ns)
# The reviewed validator performs static hashes/Git-index replay/shallow probes;
# its only persistent output is dump(). Redirect that to reviewer-owned evidence.
ns['dump'] = lambda name, value: save('REEXECUTED-' + name, value)
ns['main']()
control = Path(pins['control']['worktree'])
frozen = pins['frozen_control']
invariance = json.loads((PACKAGE / 'RUNNER-INVARIANCE.json').read_text())
ast_checks = []
for item in invariance['legacy_functions']:
    def function(text, name):
        node = next(n for n in ast.parse(text).body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)
        node.name = 'normalized_name'
        return ast.dump(node, include_attributes=False)
    old = git(control, 'show', frozen + ':ch8-s1-control/' + item['file']).decode()
    new = (control / 'ch8-s1-control' / item['file']).read_text()
    assert function(old, item['legacy_function']) == function(new, item['new_name']), item
    ast_checks.append(item)
save('LEGACY-AST-CHECKS.json', {'status': 'PASS', 'checks': ast_checks})
timing = json.loads((PACKAGE / 'RELEASE-FINAL-VALIDATE-TIMING.json').read_text())
elapsed = timing['elapsed_seconds']
save('VALIDATE-MARGIN.json', {'control_sha': pins['control']['sha'], 'recorded_tests': 130, 'elapsed_seconds': elapsed, 'elapsed_scope': 'author-recorded final object host execution, provenance and transcript hashes rechecked; suite not rerun by reviewer', 'original_cap_seconds': 600, 'required_margin': 1.5, 'minimum_cap_seconds': elapsed * 1.5, 'original_margin': 600 / elapsed, 'original_acceptable': 600 >= elapsed * 1.5, 'proposed_660_margin': 660 / elapsed, 'repair_review': 'requires exact issued committed pins; no final-object execution inferred', 'future_GitHub_duration': 'UNKNOWN'})
assert not (600 >= elapsed * 1.5)
print('REVIEW14: immutable package hashes, redirected static validator, independent legacy AST and margin checks complete')
