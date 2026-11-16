#!/usr/bin/env python3
"""Offline handoff/source identity checks. No compiler or network calls."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
request = json.loads((HERE / 'CI-REQUEST.json').read_text())
ci = Path(request['control_worktree'])


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


head = request['control_sha']
assert git(ci, 'rev-parse', 'HEAD').decode().strip() == head
assert git(ci, 'rev-parse', head + '^{tree}').decode().strip() == request['control_tree']
assert git(ci, 'rev-parse', head + '^').decode().strip() == request['control_parent']
assert not git(ci, 'status', '--porcelain')
assert '[skip ci]' in git(ci, 'show', '-s', '--format=%B', head).decode()
pin = request['std']['sha']
assert git(REPO, 'rev-parse', pin + '^{tree}').decode().strip() == request['std']['tree']
manifest = git(ci, 'show', head + ':scripts/ch8-b-census/roots.json')
assert manifest == (HERE / 'roots.json').read_bytes() == (HERE.parent / 'roots.json').read_bytes()
assert sha(manifest) == request['manifest_sha256']
control_request = git(ci, 'show', head + ':scripts/ch8-b-census/CI-REQUEST.json')
assert sha(control_request) == request['control_request_sha256']
payload = json.loads(control_request)
assert payload['std'] == request['std'] and payload['kani'] == request['tool']
assert payload['root_seconds'] == 600 and payload['root_rss_bytes'] == 6 * 1024**3
assert payload['inventory']['count'] == 235
assert payload['inventory']['shards'] == {'1': 0, '2': 183, '3': 0, '4': 52}
audit = json.loads((HERE / 'SOURCE-AUDIT.json').read_text())
assert audit['pprime_std'] == pin and audit['manifest_sha256'] == sha(manifest)
assert sha((HERE / 'root-audit.tsv').read_bytes()) == audit['root_table_sha256']
assert audit['roots'] == 235 and audit['renamed_roots'] == audit['changed_modules'] == 0
for item in audit['files']:
    old = git(REPO, 'show', audit['old_std'] + ':' + item['path'])
    new = git(REPO, 'show', pin + ':' + item['path'])
    assert old == new and sha(new) == item['old_sha256'] == item['pprime_sha256']
rows = list(csv.DictReader((HERE / 'root-audit.tsv').read_text().splitlines(), delimiter='\t'))
assert len(rows) == 235 and {r['pprime_root'] for r in rows} == {r['root'] for r in json.loads(manifest)}
for row in rows:
    assert row['old_root'] == row['pprime_root'] and row['old_source'] == row['pprime_source']
    path, line = row['pprime_source'].rsplit(':', 1)
    text = git(REPO, 'show', pin + ':' + path).decode().splitlines()[int(line) - 1]
    assert re.search(r'\b' + re.escape(row['pprime_root'].split('::')[-1]) + r'\b', text)
changed = git(ci, 'diff', '--name-only', request['control_parent'], head).decode().splitlines()
assert changed and all(p.startswith(('.github/workflows/', 'scripts/ch8-b-census/')) for p in changed)
assert git(ci, 'ls-tree', '-r', '--name-only', head, '.github/workflows').decode().splitlines() == ['.github/workflows/ch8-b-census.yml']
assert (HERE / 'control.patch').read_bytes() == git(ci, 'diff', '--binary', request['control_parent'], head)
assert request['accounting'] == {'dispatches': 0, 'pushes': 0, 'local_builds': 0, 'ledger_writes': 0}
assert request['runtime'] == 'ALL_235_NOT_RUN' and request['proof_credit'] == 'NONE'
print(json.dumps({'status': 'PASS_STATIC_ONLY', 'candidate': head, 'roots': 235,
                  'source_files': len(audit['files']), 'manifest_sha256': sha(manifest),
                  'global_inventory': 'NONE', 'proof_credit': 'NONE'}))
