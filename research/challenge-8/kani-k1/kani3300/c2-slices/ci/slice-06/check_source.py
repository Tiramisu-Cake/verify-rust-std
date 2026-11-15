#!/usr/bin/env python3
"""Independent worker15 exact source/residual/manifest checks. Git/Python only."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
HERE=Path(__file__).resolve().parent
PACKET=HERE.parent.parent
REPO=Path('/root/kani-fix-3300-c2-slices-w15')
SOURCE='3f5242bb1539fb88196d7e503b722f0905f2b46c'
BASE='96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f'
F='ad499e41dd2db9ccd432f89721638a1f3a0bbd44'
F_TREE='9829702c1aa0ecb73c860fc0ad5451757917d6cb'
B1='6fe484b30043b3696b5f1ccc4bea0e42891ad012'


def git(*args,**kwargs):
    return subprocess.check_output(['git','-C',str(REPO),*args],**kwargs)


def load(name):
    return json.loads((PACKET/name).read_text())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def grouped(manifest):
    result={}
    for group in manifest['groups']:
        rows=result.setdefault((group['suite'],group['mode']),{})
        for row in group['selectors']:
            assert rows.setdefault(row['selector'],row)==row
    return result


def main():
    source=load('slice-06/SLICE.json')
    assert source['source_sha']==SOURCE and source['base_sha']==BASE
    assert git('show','-s','--format=%P',SOURCE).decode().strip()==BASE
    assert git('rev-parse',SOURCE+'^{tree}').decode().strip()==source['source_tree']
    assert git('merge-base',B1,SOURCE).decode().strip()==B1
    assert git('rev-parse',F+'^{tree}').decode().strip()==F_TREE
    rows=load('slice-06/ORACLE-DELTA.json')['selected_complete_fixtures']
    assert len(rows)==11 and all(r['owner_slice']==6 for r in rows)
    paths={r[k] for r in rows for k in ['input','golden']}
    docs={'docs/src/reference/experimental/contracts.md','docs/src/rust-feature-support.md','tests/expected/uninit/part1-edges/README.md'}
    delta=dict(line.split('\t',1)[::-1] for line in git('diff','--name-status',BASE,SOURCE).decode().splitlines())
    assert len(delta)==25 and set(delta)==paths|docs
    assert all(delta[p]=='A' for p in paths)
    identities=[]
    for p in delta:
        assert git('ls-tree',SOURCE,'--',p)==git('ls-tree',F,'--',p),p
        identities.append({'path':p,'sha256':sha(git('show',SOURCE+':'+p))})
    assert not git('diff',SOURCE,F,'--','tests','docs')
    assert not git('diff',BASE,SOURCE,'--','kani-compiler','library','.github','Cargo.lock','Cargo.toml','rust-toolchain.toml')
    canonical=load('f7/F7-RESIDUAL.json')
    residual=set(git('diff','--name-only',SOURCE,F).decode().splitlines())
    assert residual=={r['path'] for r in canonical['files']}
    patches=[]
    for row in canonical['files']:
        actual=git('diff','--no-ext-diff','--unified=0',SOURCE,F,'--',row['path'])
        historical=git('diff','--no-ext-diff','--unified=0',row['historical_delta_base'],row['historical_delta_target'],'--',row['path'])
        assert actual==historical and sha(actual)==row['historical_patch_sha256'],row['path']
        hunks=[s for s in actual.decode().splitlines() if s.startswith('@@')]
        assert hunks==row['hunks']
        patches.append(dict(path=row['path'],patch_sha256=sha(actual),hunks=hunks,exact_historical_bytes=True))
    assert sum(len(p['hunks']) for p in patches)==14
    residual_patch=git('diff','--binary','--full-index',SOURCE,F)
    assert residual_patch==(PACKET/'slice-06/residual-to-F.patch').read_bytes()
    with tempfile.TemporaryDirectory() as directory:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(directory)/'index'))
        git('read-tree',SOURCE,env=env)
        subprocess.run(['git','-C',str(REPO),'apply','--cached','-'],input=residual_patch,env=env,check=True)
        assert git('write-tree',env=env).decode().strip()==F_TREE
    previous=grouped(load('slice-05/TEST-MANIFEST.json'))
    manifest=load('slice-06/TEST-MANIFEST.json');current=grouped(manifest)
    assert manifest['source_sha']==SOURCE and set(current)==set(previous)
    assert all(current[key][sel]==row for key,entries in previous.items() for sel,row in entries.items())
    additions={s for key,entries in current.items() for s in entries if s not in previous[key]}
    assert additions=={'[expected] '+r['input'].removeprefix('tests/') for r in rows}
    tracked=git('ls-tree','-r','--name-only',SOURCE,'--','tests/expected/uninit').decode().splitlines()
    discovered={'[expected] '+p.removeprefix('tests/') for p in tracked if p.endswith('.rs') and '/auxiliary/' not in p}
    assert discovered=={s for s in current[('expected','expected')] if s.startswith('[expected] expected/uninit/')}
    files={f['path']:f['identity'] for entries in current.values() for row in entries.values() for f in row['files']}
    for p,identity in files.items():
        assert sha(git('show',SOURCE+':'+p))==identity['sha256'],p
        entry=git('ls-tree',SOURCE,'--',p).decode().split('\t')[0].split()
        assert entry[0]==identity['mode'] and entry[2]==identity['blob'],p
    counts={key[0]:[len(entries),sum(r['existing_path_ignore'] for r in entries.values())] for key,entries in current.items()}
    assert counts=={'kani':[53,3],'expected':[379,6],'ui':[17,0],'script-based-pre':[3,0],'json-handler':[17,0],'std-checks':[2,0]}
    assert len(discovered)==212
    # Every production/fixture prerequisite is inherited unchanged; F7 stays absent.
    assert not git('diff',BASE,SOURCE,'--','kani-compiler','library')
    assert git('show',SOURCE+':kani-compiler/src/kani_middle/transform/mod.rs').count(b'replace_delayed_body')==0
    contracts=(PACKET/'slice-06/CALL-CONTRACTS-06.json').read_bytes()
    assert contracts==(PACKET/'ci/slice-05/CALL-CONTRACTS.json').read_bytes()
    (HERE/'CALL-CONTRACTS.json').write_bytes(contracts)
    subprocess.run(['git','-C',str(REPO),'diff','--check',BASE,SOURCE],check=True)
    report=dict(status='PASS_STATIC_ONLY',source_sha=SOURCE,source_tree=source['source_tree'],base_sha=BASE,
                changed_paths=identities,production_delta=0,exact_F_new_pairs=11,tests_docs_equal_F=True,
                canonical_F7_sha256=sha((PACKET/'f7/F7-RESIDUAL.json').read_bytes()),exact_residual=patches,
                residual_patch_sha256=sha(residual_patch),alternate_index_recomposed_tree=F_TREE,F7_applied_to_source=False,
                inherited_selectors_unchanged=460,cumulative_selectors=471,existing_ignores=9,
                suite_counts=counts,manifest_file_identities=len(files),present_uninit_selectors=len(discovered),
                native_checks='NOT_RUN',formal_proof_credit='NOT_ESTABLISHED')
    (HERE/'SOURCE-VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['changed_paths','exact_residual']}))


if __name__=='__main__':
    main()
