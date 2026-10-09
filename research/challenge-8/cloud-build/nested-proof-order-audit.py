#!/usr/bin/env python3
"""Audit the isolated O26 proof-order TEST; no TEST result is proof acceptance."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

SOURCE='1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6'
ORIGINAL='466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5'
TRANSLATOR='0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a'
TEST_PATCH='da3c79529a1b78fc6f9c22eb7695b908646b8acb4c6eafde1daf3e059ee3a482'
VF_HEAD='f76012fb518703b1d98e243ac4f487f16877cfcb'
TRANSLATOR_PATH='src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
BINARIES=('bin/verifast','bin/vf-rust-mir-exporter','bin/refinement-checker',
          'bin/vf-cxx-ast-exporter','bin/libz3.so')
NAMES=(
 'sort4_certified_maybeuninit::sort4_checked_maybeuninit_new',
 'sort4_checked_as_mut_ptr','sort4_checked_pointer_drop',
 'sort4_checked_generic_drop','checked_transmute_neo_pointer',
 'checked_assume_init_pointer','checked_forget_owned',
 'select_unpredictable',
 '<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop',
)
ROW=re.compile(r'SORT4-NESTED-PROOF-ORDER-TEST: (before|after)\[(\d+)\] '
               r'body_name=(.*?) module=(.*?) fn=(.*?) type=FuncBody '
               r'loc=(\S+) ast_sha256=([0-9a-f]{64})')

def read(path:Path):
    try:return json.loads(path.read_text())
    except (OSError,ValueError):return {}

def digest(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()

def git(root:Path,*args:str)->bytes:
    return subprocess.check_output(('git','-C',str(root),*args))

def snapshot(root:Path)->dict:
    paths=[p.decode() for p in git(root,'ls-files','-z').split(b'\0') if p]
    if len(paths)!=len(set(paths)) or not paths:raise ValueError('tracked inventory empty/duplicate')
    def tracked_hash(rel:str)->str:
        path=root/rel
        if path.is_symlink():return hashlib.sha256(os.readlink(path).encode()).hexdigest()
        return digest(path)
    tracked={p:tracked_hash(p) for p in paths}
    specs={str(p.relative_to(root)):digest(p) for p in sorted((root/'bin/rust').rglob('*.rsspec'))}
    binaries={p:digest(root/p) for p in BINARIES}
    if 'src/verifast.ml' not in tracked or TRANSLATOR_PATH not in tracked or not specs:
        raise ValueError('kernel/translator/spec inventory incomplete')
    return {'head':git(root,'rev-parse','HEAD').decode().strip(),
            'tracked':tracked,'effective_rsspec':specs,'binaries':binaries,
            'applied_diff_sha256':hashlib.sha256(git(root,'diff')).hexdigest()}

def equal_except(a:dict,b:dict,allowed:set[str])->bool:
    return (set(a)==set(b) and
            all(a[k]==b[k] for k in a if k not in allowed) and
            all(a[k]!=b[k] for k in allowed))

def save(path:Path,data:dict):path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')

def snapshot_main():
    p=argparse.ArgumentParser()
    p.add_argument('snapshot',choices=('snapshot',))
    p.add_argument('--phase',choices=('production-before','test-delta','final'),required=True)
    p.add_argument('--production-source',type=Path,required=True)
    p.add_argument('--test-source',type=Path,required=True)
    p.add_argument('--stock-home',type=Path,required=True)
    p.add_argument('--production-applied-patch',type=Path,required=True)
    p.add_argument('--evidence',type=Path,required=True)
    a=p.parse_args();ev=a.evidence
    prod=snapshot(a.production_source)
    if (prod['head']!=VF_HEAD or prod['tracked'][TRANSLATOR_PATH]!=TRANSLATOR or
        git(a.production_source,'diff')!=a.production_applied_patch.read_bytes()):
        raise ValueError('production source/profile changed')
    if any(prod['binaries'][p]!=digest(a.stock_home/p) for p in BINARIES[1:]):
        raise ValueError('production exporter/refiner/other binary differs from stock')
    if a.phase=='production-before':
        save(ev/'production-before-snapshot.json',prod)
        return
    before=read(ev/'production-before-snapshot.json')
    if before!=prod:raise ValueError('production tracked source/kernel/spec/binary changed')
    test=snapshot(a.test_source)
    if (test['head']!=VF_HEAD or test['effective_rsspec']!=prod['effective_rsspec'] or
        not equal_except(prod['tracked'],test['tracked'],{TRANSLATOR_PATH})):
        raise ValueError('TEST tracked source differs beyond translator')
    if a.phase=='test-delta':
        if test['binaries']!=prod['binaries']:
            raise ValueError('TEST binaries changed before console rebuild')
        save(ev/'test-before-build-snapshot.json',test)
        return
    delta=read(ev/'test-before-build-snapshot.json')
    if (test['tracked']!=delta.get('tracked') or
        test['effective_rsspec']!=delta.get('effective_rsspec') or
        not equal_except(prod['binaries'],test['binaries'],{'bin/verifast'})):
        raise ValueError('TEST source/spec/other binaries changed during build/proof')
    save(ev/'production-after-snapshot.json',prod)
    save(ev/'test-after-snapshot.json',test)
    save(ev/'source-integrity.json',{'production_unchanged':True,
         'test_only_translator_changed':True,'test_only_console_changed':True,
         'all_effective_rsspec_unchanged':True,'kernel_unchanged':True,
         'all_other_tracked_source_and_binaries_unchanged':True,
         'tracked_file_count':len(prod['tracked']),
         'effective_rsspec_count':len(prod['effective_rsspec'])})

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--runner-exit',type=int,required=True)
    p.add_argument('--failed-stage',required=True)
    a=p.parse_args();ev=a.evidence
    inputs=read(ev/'input-identity.json')
    delta=read(ev/'test-delta.json')
    integrity=read(ev/'source-integrity.json')
    prod_before=read(ev/'production-before-snapshot.json')
    prod_after=read(ev/'production-after-snapshot.json')
    test_before=read(ev/'test-before-build-snapshot.json')
    test_after=read(ev/'test-after-snapshot.json')
    pair=read(ev/'cases/candidate/capture-compare.json')
    cap=read(ev/'cases/candidate/capture/summary.json')
    stage=read(ev/'cases/candidate/proof-stage.json').get('stage',{})
    log=ev/'cases/candidate/capture/nine-body-a1-owned-forget/refreshed-proof.log'
    text=log.read_text(errors='replace') if log.is_file() else ''
    rows={'before':{},'after':{}}
    for phase,number,body_name,module,name,loc,sha in ROW.findall(text):
        index=int(number)
        if index not in rows[phase]:rows[phase][index]=(body_name,module,name,loc,sha)
        else:rows[phase][index]=None
    inventory=(all(set(rows[k])==set(range(9)) and None not in rows[k].values()
                   for k in rows) and
       [rows['before'][i][0] for i in range(9)]==list(NAMES) and
       [rows['after'][i][0] for i in range(9)]==list(NAMES[:7])+[NAMES[8],NAMES[7]] and
       sorted(rows['before'].values())==sorted(rows['after'].values()) and
       'SORT4-NESTED-PROOF-ORDER-TEST: exact nine-body one-item permutation' in text)
    headers=[text.find("Verifying function '"+name+"'") for name in NAMES]
    prefix=(all(n>=0 for n in headers[:7]) and headers[:7]==sorted(headers[:7]))
    nested_index=headers[8];outer_index=headers[7]
    nested_before_outer=(prefix and nested_index>headers[6] and outer_index>nested_index)
    errors_before_outer=(outer_index>=0 and
       (re.search(r'(^|\n)(Error|Fatal error):',text[:outer_index]) is not None))
    proof_ran=(stage.get('status')=='RAN' and stage.get('exit') is not None and
       stage.get('exit') not in (124,137) and stage.get('source_unchanged') is True and
       stage.get('source_before')==stage.get('source_after') and
       stage.get('source_before',{}).get('verified/lib.rs')==SOURCE and
       stage.get('source_before',{}).get('original/lib.rs')==ORIGINAL and
       stage.get('intrinsic_gate_active') is True and
       stage.get('pointer_drop_gate_active') is True and log.is_file())
    source=cap.get('source',{})
    source_pair=(source.get('verified_sha256')==SOURCE and
       source.get('original_sha256')==ORIGINAL and pair.get('capture_complete') is True and
       pair.get('source_pair_match') is True and
       pair.get('full_normal_readonly_mir_match') is True and
       (ev/'cases/candidate/capture/nine-body-a1-owned-forget/verified/lib.rs').is_file() and
       (ev/'cases/candidate/capture/nine-body-a1-owned-forget/original/lib.rs').is_file() and
       digest(ev/'cases/candidate/capture/nine-body-a1-owned-forget/verified/lib.rs')==SOURCE and
       digest(ev/'cases/candidate/capture/nine-body-a1-owned-forget/original/lib.rs')==ORIGINAL)
    patch=ev/'test-applied.patch'
    profile=(inputs.get('classification')=='O26_NESTED_PROOF_ORDER_TEST_ONLY' and
       inputs.get('production_translator_sha256')==TRANSLATOR and
       delta.get('production_translator_sha256')==TRANSLATOR and
       delta.get('changed_paths')==[
         'bin/rust/std/lib.rsspec',
         'src/rust_frontend/vf_mir_translator/rust_parser.ml',
         'src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'] and
       inputs.get('test_patch_sha256')==delta.get('test_patch_sha256')==TEST_PATCH and
       (ev/'test-order.patch').is_file() and digest(ev/'test-order.patch')==TEST_PATCH and
       patch.is_file() and (ev/'production-translator.ml').is_file() and
       (ev/'test-translator.ml').is_file() and
       digest(ev/'production-translator.ml')==TRANSLATOR and
       digest(ev/'test-translator.ml')==delta.get('test_translator_sha256'))
    stable=(integrity.get('production_unchanged') is True and
       integrity.get('test_only_translator_changed') is True and
       integrity.get('test_only_console_changed') is True and
       integrity.get('all_effective_rsspec_unchanged') is True and
       integrity.get('kernel_unchanged') is True and
       integrity.get('all_other_tracked_source_and_binaries_unchanged') is True and
       prod_before==prod_after and prod_before.get('head')==VF_HEAD and
       prod_before.get('tracked',{}).get(TRANSLATOR_PATH)==TRANSLATOR and
       test_before.get('tracked')==test_after.get('tracked') and
       test_before.get('effective_rsspec')==test_after.get('effective_rsspec')==
         prod_before.get('effective_rsspec') and
       equal_except(prod_before.get('tracked',{}),test_after.get('tracked',{}),
                    {TRANSLATOR_PATH}) and
       equal_except(prod_before.get('binaries',{}),test_after.get('binaries',{}),
                    {'bin/verifast'}))
    nested_prefix_complete=proof_ran and inventory and nested_before_outer and not errors_before_outer
    diagnostic_complete=(a.runner_exit==0 and profile and stable and source_pair and proof_ran and
                         inventory and nested_before_outer and not errors_before_outer)
    result={'classification':('NESTED_PROOF_ORDER_TEST_DIAGNOSTIC_COMPLETE' if diagnostic_complete
        else 'INCONCLUSIVE_OR_NESTED_BLOCKER'),
      'test_profile_only':True,'diagnostic_complete':diagnostic_complete,
      'verification_accepted':False,'accepted':False,'actual_helper_proved':False,
      'nested_prefix_complete_diagnostic':nested_prefix_complete,
      'full_proof_exit':stage.get('exit'),'full_proof_zero':proof_ran and stage.get('exit')==0,
      'source_mir_refinement_complete':source_pair,'test_profile_pins_complete':profile,
      'production_and_test_source_integrity':stable,
      'exact_ast_one_item_permutation':inventory,
      'seven_prefix_headers_then_nested_then_outer':nested_before_outer,
      'error_before_outer':errors_before_outer,'inventory':rows,
      'runner_exit':a.runner_exit,'failed_stage':a.failed_stage,
      'pending_gates':['separate production admissibility review',
        'component17 source/MIR controls','component20 A1 controls',
        'proof-order declaration corruption negatives','whole target proof and resource review']}
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in
          ('classification','diagnostic_complete','verification_accepted')}),flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='snapshot':snapshot_main()
    else:main()
