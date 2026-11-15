#!/usr/bin/env python3
"""Bounded source-only checks; no Rust/compiler/verifier invocation."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

STD=Path('/root/verify-rust-std-ch8-s1-pprime-w13')
BASE='c5ff36ff433692140605891f646043f991db05de'
ROOT='library/core/src/slice/sort/shared/smallsort'
ALLOWED={ROOT+'.rs',ROOT+'/verify.rs',ROOT+'/verify/sorting_model.rs',
 ROOT+'/verify/sorting_model_controls.rs',ROOT+'/verify/sorting_entry_smoke.rs',
 ROOT+'/verify/sorting_entry_controls.rs','library/core/src/lib.rs',
 'library/core/Cargo.toml','tool_config/kani-version.toml'}

def git(*a):return subprocess.check_output(['git','-C',str(STD),*a],text=True).strip()

def main():
    changed=set(git('diff','--name-only',BASE,'HEAD').splitlines())
    assert changed==ALLOWED,(changed^ALLOWED)
    text=(STD/(ROOT+'.rs')).read_text()
    stripped=re.sub(r'^    #\[cfg_attr\(all\(kani, kani_smallsort_sorting\), .*\)\]\n','',text,flags=re.M)
    original=subprocess.check_output(['git','-C',str(STD),'show',BASE+':'+ROOT+'.rs'],text=True)
    assert stripped==original,'runtime source/body/signature/threshold drift'
    methods=list(re.finditer(r'impl<[^\n]+> (StableSmallSortTypeImpl|UnstableSmallSortTypeImpl|UnstableSmallSortFreezeTypeImpl) for T \{(.*?)\n\}',text,re.S))
    assert len(methods)==6
    for m in methods:
        trait=m.group(1);body=m.group(2)
        assert body.count('kani::requires(v.len() <= <T as '+trait+'>::small_sort_threshold())')==1
        assert body.count('kani::ensures(')==1 and body.count('old(verify::sorting_model::snapshot::<T, F>(v))')==1
        assert body.count('kani::modifies(')==1
        assert ('kani::requires(v.len() < 2 || scratch.len() >= v.len() + 16)' in body)==(trait=='StableSmallSortTypeImpl' and 'FreezeMarker' in m.group(0).split('{',1)[0])
    fixture=(STD/(ROOT+'/verify/sorting_entry_smoke.rs')).read_text()
    assert len(re.findall(r'^smoke!\(',fixture,re.M))==6
    assert len(re.findall(r'kani::cover\(',fixture))==11
    assert 'proof_for_contract(<$ty as $trait>::small_sort)' in fixture
    assert 'let input: [u8; 3] = kani::any();' in fixture and 'kani::assume(n <= 3)' in fixture
    assert '[const { MaybeUninit::uninit() }; 19]' in fixture
    assert 'if $n < 2 { 0 } else { $n + 16 }' in fixture
    assert not re.search(r'kani::(?:stub|stub_verified|should_panic)|assume\(false\)',fixture)
    controls=(STD/(ROOT+'/verify/sorting_entry_controls.rs')).read_text()
    assert controls.count('#[kani::proof_for_contract(')==2
    assert 'post::<u8, KeyLess<u8>>>(before, &v)' not in controls
    assert 'post::<u8, KeyLess<u8>>(before, &v)' in controls
    model=(STD/(ROOT+'/verify/sorting_model.rs')).read_text()
    assert model.count('active_model!(')==3
    assert 'default fn snapshot(_values: &[T]) -> Snapshot { Snapshot::invalid() }' in model
    assert 'default fn post(_before: Snapshot, _values: &[T]) -> bool { true }' in model
    # Exact model files must equal accepted worker11 committed content.
    for name in ['sorting_model.rs','sorting_model_controls.rs']:
        path=ROOT+'/verify/'+name
        accepted=subprocess.check_output(['git','-C',str(STD),'show','3f469d3ba2e94d7129e66e53ea76df883ff9c946:'+path])
        assert (STD/path).read_bytes()==accepted
    subprocess.run(['git','-C',str(STD),'diff','--check',BASE,'HEAD'],check=True)
    result={'state':'PASS_STATIC_ONLY','source_sha':git('rev-parse','HEAD'),
        'source_tree':git('rev-parse','HEAD^{tree}'),'changed_paths':sorted(changed),
        'runtime_body_comparison':'BYTE_IDENTICAL_AFTER_REMOVING_19_VERIFICATION_ATTRS',
        'methods':6,'pfc_smoke_roots':6,'activation_companions':2,
        'model_files':'EXACT_W11','Rust':'NOT_RUN','Kani':'NOT_RUN','Cloud_dollars':0}
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
