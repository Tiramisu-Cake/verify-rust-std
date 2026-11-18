#!/usr/bin/env python3
"""Bounded static identity/name checks for the exact reviewed source objects."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent / 'batch-r4'
DIAG = OUT.parent / 'r3-closure-diagnostic'
sys.dont_write_bytecode = True
sys.path.insert(0, '/root/kani-ch8-s2-r4-final-w13/ch8-s1-control')
import cfg_pfc as c
import s2_correspondence as corr


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def main():
    pins = json.loads((PACKAGE / 'PINS.json').read_text())
    refs = json.loads((PACKAGE / 'SOURCE-DIAGNOSTIC-REFERENCE.json').read_text())
    for name, expected in refs['files_sha256'].items():
        assert hashlib.sha256((DIAG / name).read_bytes()).hexdigest() == expected, name
    objects = json.loads((DIAG / 'PROVENANCE.json').read_text())['files']
    for obj in objects:
        data = git(obj['repository'], 'show', obj['commit'] + ':' + obj['path'])
        assert hashlib.sha256(data).hexdigest() == obj['sha256'], obj['path']
        if 'git_blob' in obj:
            assert git(obj['repository'], 'rev-parse', obj['commit'] + ':' + obj['path']).decode().strip() == obj['git_blob']
    repo = Path(pins['source']['worktree'])
    batch = git(repo, 'show', pins['source']['sha'] + ':' + corr.BATCH).decode()
    _, items = c.items(batch)
    aliases = {}
    functions = set()
    for item in items:
        pos = c.kind(item, 'use')
        if pos is not None:
            aliases.update(c.use_paths(item['head'][pos:]))
        pos = c.kind(item, 'fn')
        if pos is not None:
            functions.add(item['head'][pos][0])
    scratch = corr.fn(batch, 'general_fault_scratch')
    calls = [line for token, line in scratch['body'] if token == 'sort4_stable']
    assert calls == [300, 301]
    assert 'sort4_stable' not in aliases and 'sort4_stable' not in functions
    original = git(repo, 'show', pins['source']['sha'] + ':' + corr.SMALLSORT).decode()
    assert corr.fn(original, 'sort4_stable')
    # Confirm exact r3 baseline; all source paths except the batch remain identical.
    source_paths = git(repo, 'diff', '--name-only', pins['source']['derivation_source'], pins['source']['sha']).decode().splitlines()
    assert source_paths == [corr.BATCH]
    # Confirm the scoped control delta has only the two identity literals in runner.
    control = Path(pins['control']['worktree'])
    old_runner = git(control, 'show', pins['control']['derivation_control'] + ':ch8-s1-control/runner.py')
    new_runner = git(control, 'show', pins['control']['sha'] + ':ch8-s1-control/runner.py')
    normalized = new_runner.replace(pins['source']['sha'].encode(), pins['source']['derivation_source'].encode())
    normalized = normalized.replace(pins['source']['tree'].encode(), b'b5b25f4e59308df7b15340cae343f50ae9fd8a81')
    assert normalized == old_runner
    result = {
        'diagnostic_commit': pins['frozen_diagnostic'],
        'diagnostic_files_sha256_checked': len(refs['files_sha256']),
        'diagnostic_provenance_objects_checked': len(objects),
        'source_delta_paths': source_paths,
        'runner_delta': 'TWO_IDENTITY_LITERALS_ONLY',
        'source_binding_finding': {
            'file': corr.BATCH, 'calls': calls, 'name': 'sort4_stable',
            'module_import_aliases': sorted(aliases), 'module_functions': sorted(functions),
            'import_or_declaration_present': False,
            'original_parent_declaration_present': True,
            'scope': 'Static source name audit; no native compilation or observed compiler diagnostic.'
        },
        'native_compile': 'NOT_RUN', 'causal_repair': 'NOT_RUN', 'proof_credit': 'NONE'
    }
    (OUT / 'ADDITIONAL-CHECKS.json').write_text(json.dumps(result, indent=2) + '\n')
    print('ADDITIONAL_CHECKS_COMPLETE: frozen diagnostic identities; missing sort4_stable binding; exact runner delta')


if __name__ == '__main__':
    main()
