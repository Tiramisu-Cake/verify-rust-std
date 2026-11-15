#!/usr/bin/env python3
"""Exact source/CI package validator. Git/Python only, never build or dispatch."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PACKET=HERE.parent.parent
REPO=Path('/root/kani-fix-3300-c2-slices-w15')
SOURCE='8e299aa6243bc5f06a29c51e98aafa9564478220'
BASE='3f5242bb1539fb88196d7e503b722f0905f2b46c'
F='ad499e41dd2db9ccd432f89721638a1f3a0bbd44'
TREE='9829702c1aa0ecb73c860fc0ad5451757917d6cb'
RECIPE='ece902633e72af24dcd1157ee7b457d27840027c'


def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args])
def sha(data):return hashlib.sha256(data).hexdigest()
def read(path):return json.loads(path.read_text())
def save(path,value):path.write_text(json.dumps(value,indent=2)+'\n')


def main():
    sys.path.insert(0,str(REPO/'.github/c2-slices'))
    import slice07_ci as ci
    import structural
    config,manifest=ci.inputs()
    overlay=git('rev-parse','HEAD').decode().strip()
    assert not git('status','--porcelain')
    assert git('rev-parse','HEAD^').decode().strip()==SOURCE
    assert git('rev-parse',SOURCE+'^').decode().strip()==BASE
    assert git('rev-parse',SOURCE+'^{tree}').decode().strip()==TREE
    assert git('rev-parse',F+'^{tree}').decode().strip()==TREE
    assert not git('diff',F,SOURCE)
    assert not git('diff',SOURCE,overlay,'--','kani-compiler','library','tests','docs','Cargo.toml','Cargo.lock','rust-toolchain.toml')
    changed=git('diff','--name-only',SOURCE,overlay).decode().splitlines()
    assert all(ci.ci_path(p) for p in changed)
    exact=git('diff','--binary','--full-index',BASE,SOURCE)
    assert exact==(PACKET/'f7/source.patch').read_bytes()==(PACKET/'slice-06/residual-to-F.patch').read_bytes()
    residual=read(PACKET/'f7/F7-RESIDUAL.json')
    assert set(git('diff','--name-only',BASE,SOURCE).decode().splitlines())=={r['path'] for r in residual['files']}
    for row in residual['files']:
        delta=git('diff','--no-ext-diff','--unified=0',BASE,SOURCE,'--',row['path'])
        assert sha(delta)==row['historical_patch_sha256']
        assert [s for s in delta.decode().splitlines() if s.startswith('@@')]==row['hunks']
    original=read(PACKET/'slice-06/TEST-MANIFEST.json')
    assert original['groups']==manifest['groups']
    assert original['active_call_units']==manifest['active_call_units']
    assert original['immutable_unit_names']==manifest['immutable_unit_names']
    assert manifest['source_sha']==SOURCE and manifest['source_tree']==TREE
    counts={suite:dict(discovery=len(rows),passed=sum(not r['existing_path_ignore'] for r in rows.values()),ignored=sum(r['existing_path_ignore'] for r in rows.values())) for (suite,_),rows in ci.suites(manifest).items()}
    assert counts=={'kani':dict(discovery=53,passed=50,ignored=3),'expected':dict(discovery=379,passed=373,ignored=6),'ui':dict(discovery=17,passed=17,ignored=0),'script-based-pre':dict(discovery=3,passed=3,ignored=0),'json-handler':dict(discovery=17,passed=17,ignored=0),'std-checks':dict(discovery=2,passed=2,ignored=0)}
    units=config['additional_units']
    for action,expected in [('delayed-cache-units',6),('delayed-scope-units',2),('compiler-all-units',76)]:
        assert len(units[action]['native_names'])==expected
    assert config['effective_all_compiler_unit_count']==76
    assert units['compiler-all-units']['expected_passed']==76
    assert units['compiler-all-units']['includes_relevant_groups']==28
    assert units['compiler-all-units']['F7_units_absent']==0
    mapped=[r for r in read(PACKET/'oracle-map/ORACLE-MAP.json')['new_unit_tests'] if r['owner_slice']==7]
    expected={r['test'] for r in mapped};actual={n.rsplit('::',1)[1] for action in ('delayed-cache-units','delayed-scope-units') for n in units[action]['native_names']}
    assert actual==expected and len(expected)==8
    for r in mapped:
        assert ('fn '+r['test']+'(').encode() in git('show',SOURCE+':'+r['path'])
    assert ci.sensitivity.SOURCE_SHA==SOURCE
    assert (REPO/'.github/c2-slices/sensitivity.py').read_bytes()==git('show',RECIPE+':.github/c2-slices/sensitivity.py').replace(BASE.encode(),SOURCE.encode())
    sensitivity=read(HERE/'sensitivity-manifest.json')
    assert sha((HERE/'sensitivity-manifest.json').read_bytes())==config['sensitivity']['manifest_sha256']
    for row in sensitivity['variants']:
        data=(HERE/row['patch']).read_bytes()
        assert sha(data)==row['patch_sha256']
        assert sha(git('show',SOURCE+':'+row['mutated_path']))==row['input_sha256']
        subprocess.run(['git','-C',str(REPO),'apply','--check','-'],input=data,check=True)
    structural_manifest=read(HERE/'structural-manifest.json')
    mixed=(HERE/'structural-mixed.rs').read_bytes()
    assert mixed==git('show','3b382c812a:tests/json-handler/uninit-part1-composition/mixed.rs')
    assert sha(mixed)==structural_manifest['source_sha256']
    assert sha((HERE/'structural-manifest.json').read_bytes())==config['structural']['manifest_sha256']
    calls=structural.invocations(structural_manifest)
    assert len(calls)==11 and sum(len(c['selectors']) for c in calls[7:])==18
    assert not any('expected_inventory' in r for r in structural_manifest['roots'])
    assert not (REPO/'tests/json-handler/uninit-part1-composition').exists()
    assert not (REPO/'.github/c2-slices/roots.json').exists()
    paths=git('ls-tree','-r','--name-only',overlay,'--','.github/c2-slices').decode().splitlines()
    for name in paths:
        local=HERE/Path(name).relative_to('.github/c2-slices')
        if name.endswith('test-manifest.json'):local=PACKET/'f7/TEST-MANIFEST.json'
        assert local.read_bytes()==git('show',overlay+':'+name),name
    assert (HERE/'uninit-quick.yml').read_bytes()==git('show',overlay+':.github/workflows/uninit-quick.yml')
    for path in HERE.glob('*.py'):ast.parse(path.read_text(),str(path))
    # Static exact source identity snapshot (all protected entries), not native evidence.
    with tempfile.TemporaryDirectory() as temp:
        ci.snapshot('package-static',Path(temp)); snapshot=read(Path(temp)/'source-package-static.json')
    spec=importlib.util.spec_from_file_location('prepare_f7',HERE/'prepare_overlay.py')
    prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)
    real_check=subprocess.check_output
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp)
        for name in git('ls-tree','-r','--name-only',SOURCE,'--','.github/workflows').decode().splitlines():
            dest=root/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(git('show',SOURCE+':'+name))
        def pinned(argv,*args,**kw):
            tail=argv[3:]
            if tail==['rev-parse','HEAD']:return (SOURCE+'\n').encode()
            if tail==['status','--porcelain']:return b''
            return real_check(['git','-C',str(REPO),*tail],*args,**kw)
        with patch.object(prepare,'REPO',root),patch.object(prepare.subprocess,'check_output',side_effect=pinned):prepare.main()
        for path in (root/'.github').rglob('*'):
            if path.is_file():assert path.read_bytes()==(REPO/path.relative_to(root)).read_bytes()
    subprocess.run(['git','-C',str(REPO),'diff','--check',BASE,SOURCE],check=True)
    subprocess.run(['git','-C',str(REPO),'diff','--check',SOURCE,overlay,'--','.github',':(exclude).github/c2-slices/sensitivity/*.patch'],check=True)
    (HERE/'overlay.patch').write_bytes(git('diff','--binary','--full-index',SOURCE,overlay))
    report=dict(status='PASS_STATIC_AND_SYNTHETIC_ONLY',source_sha=SOURCE,source_tree=TREE,source_parent=BASE,F=F,exact_F_tree=True,diff_F_empty=True,residual_files=0,residual_hunks=0,historical_hunks_exact=14,overlay_sha=overlay,overlay_tree=git('rev-parse',overlay+'^{tree}').decode().strip(),overlay_parent=SOURCE,overlay_only_ci=True,recipe_sha=RECIPE,recipe_run='43720042056',source_entries_checked=len(snapshot['files']),source_snapshot_problems=snapshot['problems'],source_patch_sha256=sha(exact),overlay_patch_sha256=sha((HERE/'overlay.patch').read_bytes()),generator_reproduction='PASS_EXACT_BYTES',suite_counts=counts,selectors=471,targeted_units=28,compiler_units=76,F7_units=8,structural_invocations=11,structural_comparisons=18,structural_input_byte_identical_S4=True,synthetic_tests=dict(runner=24,structural=15,sensitivity=13,seam=10),source_native_checks='NOT_RUN',CI='NOT_RUN',push='NOT_RUN',proof_credit='NOT_ESTABLISHED')
    save(HERE/'STATIC-VALIDATION.json',report)
    print(json.dumps(report))


if __name__=='__main__':main()
