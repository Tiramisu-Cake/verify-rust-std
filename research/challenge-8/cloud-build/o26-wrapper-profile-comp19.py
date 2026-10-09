#!/usr/bin/env python3
"""Cloud-only independent SAFE-forget Move(_33) to Copy(_33) negative."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from types import SimpleNamespace

ROOT=Path('research/challenge-8')
TRANSLATOR=Path('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml')
MUTATION='forget_move_to_copy'
OWNER_FATAL='Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: owner complete decoded unit SHA256")'
FORGET_FATAL='Fatal error: exception Failure("SORT4-ACTUAL-FORGET-OWN: certificate mismatch: forget argument plain Move")'
OWNER_MARK='SORT4-ACTUAL-OWNER-NINE: exact source and complete decoded MIR admission only'
FORGET_MARK='SORT4-ACTUAL-FORGET-OWN: exact nine-body SAFE call/owner callee admitted'
A1_MARK='SORT4-A1-NINE: exact source, typed local pair and outer cleanup call admitted'
VERIFIER_ERROR=re.compile(r'^.+\(\d+,[^)]*\): error: ',re.MULTILINE)


def common(args):
    a1=load(args.cloud_dir/'o26-wrapper-profile-a1.py','o26_comp19_common_a1')
    profile,cap,prep,mut=a1.input_modules(args)
    m=profile.profile(args.proof_root)
    return a1,profile,cap,prep,mut,m


def load(path,name):
    import importlib.util,sys
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None:raise ValueError(f'missing {path}')
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def mutate_actual_mir(decoded,mutation):
    if mutation!=MUTATION:raise ValueError('unexpected component-19 MIR mutation')
    proof=os.environ.get('COMP19_TEST_PROOF_ROOT')
    cloud=os.environ.get('COMP19_TEST_CLOUD_DIR')
    if not proof or not cloud:raise ValueError('component-19 TEST roots absent')
    profile=load(Path(cloud)/'o26-wrapper-profile.py','o26_comp19_wrapper_profile')
    return profile.mutate_outer_mir(decoded,MUTATION,Path(proof))


def shadow(a1,tool,schema,case,mut,source):
    selected=mut.make_shadow(tool,schema,case,MUTATION,source)
    wrapper=selected/'bin/vf-rust-mir-exporter'
    prior=repr(str(mut.HERE/'capture-actual-owner-mir-mutation.py'))
    text=wrapper.read_text()
    a1.need(text.count(prior)==1,'component-19 shadow import anchor differs')
    text=text.replace(prior,repr(str(Path(__file__).resolve())),1)
    wrapper.write_text(text)
    (case/'mir-exporter-wrapper.py').write_text(text)
    identity=a1.read(case/'mutation-profile.json')
    identity.update({'wrapper_sha256':a1.sha(wrapper),'test_only':True,
                     'mutation':MUTATION})
    a1.write(case/'mutation-profile.json',identity)
    return selected


def mutation_record(a1,profile,proof,case,source,normal):
    names=('mutation-record.json','mutation-profile.json','canonical-mir.txt',
           'mutated-mir.txt','canonical-mir.bin','mutated-mir.bin',
           'mir-exporter-wrapper.py')
    a1.need(all((case/n).is_file() for n in names),
            'component-19 mutation evidence missing')
    record=a1.read(case/'mutation-record.json')
    identity=a1.read(case/'mutation-profile.json')
    a1.need(record['matched'] is True and record['mutation']==MUTATION and
            record['selected_source_sha256']==source and
            all(record[k]==0 for k in ('exporter_exit','decode_exit','encode_exit')) and
            record['canonical_sha256']==a1.sha(case/'canonical-mir.bin')==normal and
            record['mutated_sha256']==a1.sha(case/'mutated-mir.bin') and
            profile.mutate_outer_mir((case/'canonical-mir.txt').read_text(),MUTATION,proof)==
                (case/'mutated-mir.txt').read_text() and
            identity['wrapper_sha256']==a1.sha(case/'mir-exporter-wrapper.py')==
                a1.sha(case/'mutation-profile/bin/vf-rust-mir-exporter') and
            identity['base_console_sha256']==identity['shadow_console_sha256'] and
            identity['real_exporter_sha256']==record['real_exporter_sha256'],
            'component-19 MIR/wrapper delta differs')
    return {'mutation':MUTATION,'canonical_mir_sha256':normal,
            'mutated_mir_sha256':record['mutated_sha256'],
            'wrapper_sha256':identity['wrapper_sha256'],
            'real_exporter_sha256':record['real_exporter_sha256']}


def capture(args):
    a1,profile,cap,prep,mut,m=common(args)
    a1.need(m['typed_outer_mir']['forget']['block']==15 and
            m['typed_outer_mir']['forget']['move_argument_local']=='_33' and
            m['typed_outer_mir']['forget']['cleanup_block']==26,
            'component-19 typed target differs')
    parent=args.evidence.parent
    positive=parent/'capture/nine-body-wrapper-rebase'
    a1.need(a1.read(parent/'capture-check.json')['classification']=='WRAPPER_REBASE_CAPTURE_PINNED',
            'fresh positive wrapper capture missing')
    positive_stage=a1.read(parent/'profile-proof-stage.json')
    positive_log=(positive/'profile-proof.log').read_text(errors='replace')
    a1.need(positive_stage.get('status')=='RAN' and
            positive_stage.get('exit') not in (None,124,137) and
            positive_stage.get('source_unchanged') is True and
            OWNER_MARK in positive_log and FORGET_MARK in positive_log,
            'same-version production owner/forget proof stage unavailable')
    baseline=a1.tool_snapshot(args.profile_source,args.proof_root)
    source=m['source']['verified_sha256']
    out=args.evidence/'production'
    prepared=prep.write_case(args.proof_root,out)
    case=out/prep.CASE_NAME
    a1.need(prepared['verified_sha256']==source==a1.sha(case/'verified/lib.rs') and
            prepared['original_sha256']==m['source']['original_sha256']==
                a1.sha(case/'original/lib.rs'),
            'component-19 source pair differs')
    stage_args=SimpleNamespace(tool_home=args.profile_source,schema=args.schema,
        compiler_sysroot=str(args.compiler_sysroot),deadline_epoch=args.deadline_epoch,
        first_barrier=False,fingerprint_probe=False)
    cap.clear_semantic_opt_ins()
    support=cap.GUARD.capture_case(case,prepared,stage_args)
    stages=support['stages']
    a1.need(support['frontend_refinement'] is True and
            support['source_unchanged'] is True and
            all(stages[k]['exit']==0 and stages[k]['source_unchanged'] is True
                for k in ('normal-export','normal-decode','readonly-export',
                          'readonly-decode','refinement')) and
            a1.sha(case/'normal-mir.bin')==a1.sha(positive/'normal-mir.bin') and
            a1.sha(case/'readonly-mir.bin')==a1.sha(positive/'readonly-mir.bin'),
            'component-19 fresh NORMAL/READONLY/refinement differs')
    selected=shadow(a1,args.profile_source,args.schema,case,mut,source)
    owner=profile.proof_stage(args,case,selected,'production-owner-refusal',
                              'rebase_comp19_owner',True)
    a1.write(args.evidence/'production-owner-stage.json',owner)
    probe_args=SimpleNamespace(**vars(stage_args));probe_args.tool_home=selected
    fingerprint=cap.refusal_fingerprint(case,prepared,probe_args)
    a1.write(args.evidence/'synthetic-fingerprint.json',fingerprint)
    identity=mutation_record(a1,profile,args.proof_root,case,source,
                             a1.sha(case/'normal-mir.bin'))
    log=(case/'production-owner-refusal.log').read_text(errors='replace')
    fatal=[x for x in log.splitlines() if x.startswith('Fatal error:')]
    owner_refusal=(owner.get('status')=='RAN' and owner.get('exit')==2 and
                   owner.get('source_unchanged') is True and
                   owner.get('source_before')==owner.get('source_after') and
                   owner.get('source_before',{}).get('verified/lib.rs')==source and
                   owner.get('intrinsic_gate_active') is True and
                   owner.get('pointer_drop_gate_active') is True and
                   fatal==[OWNER_FATAL] and VERIFIER_ERROR.search(log) is None and
                   "Verifying function '" not in log and
                   FORGET_MARK not in log and A1_MARK not in log)
    a1.need(owner_refusal,'component-19 synthetic owner refusal wrong')
    a1.write(args.evidence/'capture-summary.json',
             {'classification':'COMP19_OWNER_HASH_ONLY_CAPTURE',
              'source_sha256':source,'normal_readonly_refinement_complete':True,
              'owner_hash_only_refusal':True,'synthetic_fingerprint':fingerprint,
              'mutation_identity':identity,'production_tool_snapshot':baseline,
              'verification_accepted':False})


def delta(args):
    a1,profile,cap,prep,mut,m=common(args)
    a1.delta(args,m)
    row=a1.read(args.evidence/'test-delta-profile.json')
    a1.need(row['classification']=='TEST_ONLY_REBASE_OWNER_HASH_DELTA' and
            row['component20_unchanged'] is True and
            row['production_translator_sha256']==a1.sha(args.profile_source/TRANSLATOR),
            'component-19 TEST owner hash-only delta differs')
    row.update({'classification':'TEST_ONLY_COMP19_OWNER_HASH_DELTA',
                'target':MUTATION,'component19_unchanged':True,
                'verification_accepted':False})
    a1.write(args.evidence/'test-delta-profile.json',row)


def test(args):
    a1,profile,cap,prep,mut,m=common(args)
    row=a1.read(args.evidence/'test-delta-profile.json')
    baseline=a1.read(args.evidence/'capture-summary.json')['production_tool_snapshot']
    a1.need(row['classification']=='TEST_ONLY_COMP19_OWNER_HASH_DELTA' and
            row['target']==MUTATION and row['component19_unchanged'] is True and
            a1.tool_snapshot(args.profile_source,args.proof_root)==baseline,
            'component-19 production snapshot changed')
    before=(args.profile_source/TRANSLATOR).read_text()
    after=(args.test_source/TRANSLATOR).read_text()
    old_unit=m['source']['unit_sha256'];old_body=m['source']['body_sha256'][7]
    new_unit=row['synthetic_unit_sha256'];new_body=row['synthetic_body7_sha256']
    a1.need(a1.sha(args.test_source/TRANSLATOR)==row['test_translator_sha256'] and
            after.replace(new_unit,old_unit,1).replace(new_body,old_body,1)==before,
            'component-19 TEST changed more than two owner pins')
    test_identity=a1.tool_snapshot(args.test_source,args.proof_root)
    a1.need(test_identity['specs']==baseline['specs'] and
            test_identity['proof_std']==baseline['proof_std'] and
            all(v==baseline['tracked'][k] for k,v in test_identity['tracked'].items()
                if k!=str(TRANSLATOR)) and
            all(v==baseline['binaries'][k] for k,v in test_identity['binaries'].items()
                if k!='bin/verifast') and
            test_identity['binaries']['bin/verifast']!=baseline['binaries']['bin/verifast'],
            'component-19 TEST changed frozen source/specs/binaries')
    modified=lambda root:subprocess.check_output((
        'git','-C',str(root),'diff','--name-only','HEAD')).decode().splitlines()
    names=modified(args.profile_source)
    a1.need(names==modified(args.test_source) and
            all(a1.sha(args.profile_source/n)==a1.sha(args.test_source/n)
                for n in names if n!=str(TRANSLATOR)),
            'component-19 TEST changed additional tracked source')
    case=args.evidence/'test-case';case.mkdir()
    prod=args.evidence/'production/nine-body-wrapper-rebase'
    for kind in ('verified','original'):
        (case/kind).mkdir()
        (case/kind/'lib.rs').write_bytes((prod/kind/'lib.rs').read_bytes())
    source=m['source']['verified_sha256']
    a1.need(a1.sha(case/'verified/lib.rs')==source and
            a1.sha(case/'original/lib.rs')==m['source']['original_sha256'],
            'component-19 TEST source pair changed')
    selected=shadow(a1,args.test_source,args.schema,case,mut,source)
    raw=profile.proof_stage(args,case,selected,'test-forget-refusal',
                            'rebase_comp19_test',True)
    a1.need(a1.tool_snapshot(args.profile_source,args.proof_root)==baseline,
            'component-19 production tool/proof source changed after TEST')
    a1.write(args.evidence/'test-forget-stage.json',raw)
    identity=mutation_record(a1,profile,args.proof_root,case,source,
                             a1.sha(prod/'normal-mir.bin'))
    log=(case/'test-forget-refusal.log').read_text(errors='replace')
    fatal=[x for x in log.splitlines() if x.startswith('Fatal error:')]
    intended=(raw.get('status')=='RAN' and raw.get('exit')==2 and
              raw.get('source_unchanged') is True and
              raw.get('source_before')==raw.get('source_after') and
              raw.get('source_before',{}).get('verified/lib.rs')==source and
              raw.get('source_before',{}).get('original/lib.rs')==
                  m['source']['original_sha256'] and
              raw.get('intrinsic_gate_active') is True and
              raw.get('pointer_drop_gate_active') is True and
              fatal==[FORGET_FATAL] and VERIFIER_ERROR.search(log) is None and
              OWNER_MARK in log and A1_MARK not in log and
              "Verifying function '" not in log)
    result={'classification':'REBASE_COMP19_MOVE_COPY_NEGATIVE' if intended else 'INCONCLUSIVE',
            'diagnostic_complete':intended,'verification_accepted':False,
            'intended_component19_refusal':intended,'owner_hash_only_test':True,
            'proof_stage':raw,'fatal':fatal,'mutation_identity':identity,
            'test_tool_snapshot':test_identity,'production_unchanged':True}
    a1.write(args.evidence/'test-result.json',result)
    a1.need(intended,'component-19 wrong refusal')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('capture','delta','test'))
    for key in ('proof-root','cloud-dir','profile-source','test-source',
                'compiler-sysroot','evidence'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--deadline-epoch',type=int,required=True)
    args=p.parse_args()
    a1=load(args.cloud_dir/'o26-wrapper-profile-a1.py','o26_comp19_bootstrap')
    a1.need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER')=='cloud-build' and
            not os.environ.get('GITHUB_ACTIONS'),'Cloud Build required')
    args.schema=args.profile_source/'src/rust_frontend/vf_mir/vf_mir.capnp'
    os.environ['COMP19_TEST_PROOF_ROOT']=str(args.proof_root)
    os.environ['COMP19_TEST_CLOUD_DIR']=str(args.cloud_dir)
    {'capture':capture,'delta':delta,'test':test}[args.mode](args)


if __name__=='__main__':main()
