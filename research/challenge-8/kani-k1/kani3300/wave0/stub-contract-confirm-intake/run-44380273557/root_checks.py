#!/usr/bin/env python3
"""Check packet bytes, pinned Git objects and the proofreading copy."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args, root=ROOT):
    return subprocess.check_output(['git', '-C', str(root), *args])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--committed', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((HERE / 'MANIFEST.json').read_text())
    files = sorted(p.name for p in HERE.iterdir() if p.is_file())
    assert files == sorted([*manifest['files'], 'MANIFEST.json'])
    for name, entry in manifest['files'].items():
        data = (HERE / name).read_bytes()
        assert sha(data) == entry['sha256'] and len(data) == entry['bytes'], name
    profile = json.loads((HERE / 'frozen-profile.json').read_text())
    inputs = json.loads((HERE / 'INPUTS.json').read_text())
    control = Path('/root/kani-stub-contract-push-control-w15')
    stock = Path('/root/kani-stub-contract-source-w15')
    pin_checks = 0
    for scope, repo, commit in [('source_sha256', stock, inputs['parent']), ('control_sha256', control, inputs['head'])]:
        for path, expected in profile[scope].items():
            assert sha(git('show', commit + ':' + path, root=repo)) == expected, path
            pin_checks += 1
    assert git('rev-parse', inputs['head']+'^{tree}', root=control).decode().strip() == inputs['tree']
    assert git('show','-s','--format=%P', inputs['head'],root=control).decode().strip() == inputs['parent']
    rel = str(HERE.relative_to(ROOT))
    for commit in [inputs['package_g0'], inputs['review_updated_GO_g0'], '545c33e27a282104cafe5f51837d5226dd1961e0', '96642d9188c1900224c154c97a9f5e6ec6531dc0']:
        assert git('cat-file', '-t', commit).strip() == b'commit'
    draft = (HERE/'ISSUE-DRAFT.md').read_bytes()
    assert Path('/root/smallsort-pr-drafts/ISSUE-STUB-CONTRACT-DRAFT.md').read_bytes() == draft
    text = draft.decode()
    assert '*Disclosure: this issue and reproducer were prepared with the help of AI assistants.*' in text
    for forbidden in ['/root/', 'research/', 'INCONCLUSIVE', 'B1', 'B2', 'ledger', 'oracle', 'e9f0e9a', 'faffcee', '5bb7ec', '615f027']:
        assert forbidden not in text, forbidden
    # The issue reproducer has exactly the authored fixture, apart from copyright.
    source = git('show', inputs['head']+':tests/script-based-pre/stub-contract-confirm/src/lib.rs', root=control).decode()
    source = '\n'.join(source.splitlines()[2:])+'\n'
    assert text.split('```rust\n',1)[1].split('```',1)[0] == source
    subprocess.run([sys.executable, str(HERE/'replay.py')], check=True, stdout=subprocess.PIPE)
    # Replay must be deterministic and must preserve the artifact and manifest.
    for name, entry in manifest['files'].items():
        assert sha((HERE/name).read_bytes()) == entry['sha256'], name
    committed = 0
    if args.committed:
        for name in files:
            assert git('show','HEAD:'+rel+'/'+name) == (HERE/name).read_bytes(), name
            committed += 1
        changed = git('diff-tree','--no-commit-id','--name-only','-r','HEAD').decode().splitlines()
        assert changed and all(p.startswith(rel+'/') for p in changed)
        assert '[skip ci]' in git('show','-s','--format=%B','HEAD').decode()
        assert git('show','-s','--format=%an <%ae>','HEAD').decode().strip() == 'Tiramisu-Cake <igkharin@gmail.com>'
    print(json.dumps({'status':'PASS','g0_head':git('rev-parse','HEAD').decode().strip(),'manifest_entries':len(manifest['files']),'pinned_source_files':pin_checks,'committed_files_checked':committed,'draft_identical':True,'replay_pass':True,'ownpaths_only':True if args.committed else 'pending commit'}))


if __name__ == '__main__':
    main()
