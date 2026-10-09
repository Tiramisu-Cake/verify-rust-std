#!/usr/bin/env python3
"""Independent component-20 A1 Move/Copy negative on the rebase source."""
from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

ROOT=Path('research/challenge-8')
TRANSLATOR=Path('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml')
MUTATION='outer_assume_init_move_to_copy'
OWNER_FATAL='Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: owner complete decoded unit SHA256")'
A1_FATAL='Fatal error: exception Failure("SORT4-A1-NINE: certificate mismatch: outer assume_init must move selected wrapper")'

def need(ok,why):
    if not ok:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,obj):Path(path).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def read(path):return json.loads(Path(path).read_text())
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    need(spec is not None and spec.loader is not None,f'missing {path}')
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def tool_snapshot(root,proof):
    tracked=('src/verifast.ml',str(TRANSLATOR),
             'src/rust_frontend/vf_mir_translator/rust_parser.ml',
             'src/rust_frontend/vf_mir/vf_mir.capnp')
    binaries=('bin/verifast','bin/vf-rust-mir-exporter','bin/refinement-checker',
              'bin/vf-cxx-ast-exporter','bin/libz3.so')
    std=('library/core/src/hint.rs','library/core/src/intrinsics/mod.rs',
         'library/core/src/mem/manually_drop.rs','library/core/src/mem/maybe_dangling.rs',
         'library/core/src/mem/maybe_uninit.rs','library/core/src/mem/mod.rs',
         'library/core/src/ptr/mod.rs','library/core/src/ptr/mut_ptr.rs')
    diff=subprocess.check_output(('git','-C',str(root),'diff','--binary','HEAD'))
    return {'diff_sha256':hashlib.sha256(diff).hexdigest(),
            'tracked':{name:sha(root/name) for name in tracked},
            'binaries':{name:sha(root/name) for name in binaries},
            'specs':{str(p.relative_to(root)):sha(p)
                     for p in sorted((root/'bin/rust').rglob('*.rsspec'))},
            'proof_std':{name:sha(proof/name) for name in std}}

def input_modules(args):
    profile=load(args.cloud_dir/'o26-wrapper-profile.py','o26_wrapper_a1_profile')
    cap=load(args.proof_root/ROOT/'overnight-assume-actual/capture.py','o26_wrapper_a1_capture')
    prep=load(args.proof_root/ROOT/'overnight-assume-actual/prepare-wrapper-rebase.py',
              'o26_wrapper_a1_prepare')
    mut=load(args.proof_root/ROOT/'overnight-helper/capture-actual-owner-mir-mutation.py',
             'o26_wrapper_a1_shadow')
    return profile,cap,prep,mut

def mutate_actual_mir(decoded,mutation):
    need(mutation==MUTATION,'unknown A1 wrapper mutation')
    proof=os.environ.get('A1_TEST_PROOF_ROOT')
    need(proof is not None,'A1 TEST proof root missing')
    profile=load(Path(os.environ['A1_TEST_CLOUD_DIR'])/'o26-wrapper-profile.py',
                 'o26_wrapper_a1_mutator_loaded')
    return profile.mutate_outer_mir(decoded,mutation,Path(proof))

def shadow(tool,schema,case,args,mut,source):
    selected=mut.make_shadow(tool,schema,case,MUTATION,source)
    wrapper=selected/'bin/vf-rust-mir-exporter'
    prior=repr(str(mut.HERE/'capture-actual-owner-mir-mutation.py'))
    text=wrapper.read_text()
    need(text.count(prior)==1,'A1 wrapper import anchor differs')
    text=text.replace(prior,repr(str(Path(__file__).resolve())),1)
    wrapper.write_text(text)
    (case/'mir-exporter-wrapper.py').write_text(text)
    identity=read(case/'mutation-profile.json')
    identity.update({'wrapper_sha256':sha(wrapper),'test_only':True,'mutation':MUTATION})
    write(case/'mutation-profile.json',identity)
    return selected

def mutation_record(case,profile,proof,source,normal):
    names=('mutation-record.json','mutation-profile.json','canonical-mir.txt',
           'mutated-mir.txt','canonical-mir.bin','mutated-mir.bin',
           'mir-exporter-wrapper.py')
    need(all((case/n).is_file() for n in names),'A1 mutation evidence missing')
    record=read(case/'mutation-record.json');p=read(case/'mutation-profile.json')
    need(record['matched'] is True and record['mutation']==MUTATION and
         record['selected_source_sha256']==source and
         all(record[k]==0 for k in ('exporter_exit','decode_exit','encode_exit')) and
         record['canonical_sha256']==sha(case/'canonical-mir.bin')==normal and
         record['mutated_sha256']==sha(case/'mutated-mir.bin') and
         profile.mutate_outer_mir((case/'canonical-mir.txt').read_text(),MUTATION,proof)==
             (case/'mutated-mir.txt').read_text() and
         p['wrapper_sha256']==sha(case/'mir-exporter-wrapper.py')==
             sha(case/'mutation-profile/bin/vf-rust-mir-exporter') and
         p['base_console_sha256']==p['shadow_console_sha256'],
         'A1 mutation changed more than exact Move/Copy or wrapper identity differs')
    return {'source_sha256':source,'canonical_mir_sha256':normal,
            'mutated_mir_sha256':record['mutated_sha256'],
            'wrapper_sha256':p['wrapper_sha256'],
            'real_exporter_sha256':record['real_exporter_sha256']}

def capture(args,m):
    profile,cap,prep,mut=input_modules(args)
    source=m['source']['verified_sha256']
    positive=args.evidence.parent/'capture/nine-body-wrapper-rebase'
    need(read(args.evidence.parent/'capture-check.json')['classification']=='WRAPPER_REBASE_CAPTURE_PINNED',
         'new positive source capture unavailable')
    positive_stage=read(args.evidence.parent/'profile-proof-stage.json')
    positive_log=(positive/'profile-proof.log').read_text(errors='replace')
    need(positive_stage.get('status')=='RAN' and
         positive_stage.get('exit') not in (None,124,137) and
         positive_stage.get('source_unchanged') is True and
         'SORT4-ACTUAL-OWNER-NINE:' in positive_log and
         'SORT4-A1-NINE:' in positive_log,
         'new positive owner/A1 proof unavailable for independent negative')
    baseline=tool_snapshot(args.profile_source,args.proof_root)
    out=args.evidence/'production'
    s=prep.write_case(args.proof_root,out)
    case=out/prep.CASE_NAME
    need(sha(case/'verified/lib.rs')==source==s['verified_sha256'] and
         sha(case/'original/lib.rs')==m['source']['original_sha256'],
         'A1 source pair differs')
    stage_args=SimpleNamespace(tool_home=args.profile_source,schema=args.schema,
         compiler_sysroot=str(args.compiler_sysroot),deadline_epoch=args.deadline_epoch,
         first_barrier=False,fingerprint_probe=False)
    cap.clear_semantic_opt_ins()
    support=cap.GUARD.capture_case(case,s,stage_args)
    stages=support['stages']
    need(support['frontend_refinement'] is True and
         all(stages[k]['exit']==0 for k in ('normal-export','normal-decode',
             'readonly-export','readonly-decode','refinement')) and
         sha(case/'normal-mir.bin')==sha(positive/'normal-mir.bin') and
         sha(case/'readonly-mir.bin')==sha(positive/'readonly-mir.bin'),
         'A1 rebase paired MIR/refinement changed')
    selected=shadow(args.profile_source,args.schema,case,args,mut,source)
    owner=profile.proof_stage(args,case,selected,'production-owner-refusal',
                              'rebase_a1_owner',True)
    write(args.evidence/'production-owner-stage.json',owner)
    probe_args=SimpleNamespace(**vars(stage_args));probe_args.tool_home=selected
    fingerprint=cap.refusal_fingerprint(case,s,probe_args)
    write(args.evidence/'synthetic-fingerprint.json',fingerprint)
    identity=mutation_record(case,profile,args.proof_root,source,sha(case/'normal-mir.bin'))
    log=(case/'production-owner-refusal.log').read_text(errors='replace')
    fatal=[x for x in log.splitlines() if x.startswith('Fatal error:')]
    owner_refusal=(owner.get('status')=='RAN' and owner.get('exit')==2 and
                   owner.get('source_unchanged') is True and
                   owner.get('source_before')==owner.get('source_after') and
                   fatal==[OWNER_FATAL] and not cap.LINK.LINK.ERR.findall(log) and
                   "Verifying function '" not in log)
    need(owner_refusal,'A1 synthetic owner refusal occurred at wrong predicate')
    write(args.evidence/'capture-summary.json',
          {'source_sha256':source,'normal_readonly_refinement_complete':True,
           'owner_hash_only_refusal':owner_refusal,'synthetic_fingerprint':fingerprint,
           'mutation_identity':identity,'production_tool_snapshot':baseline,
           'verification_accepted':False})

def delta(args,m):
    row=read(args.evidence/'capture-summary.json')
    fp=row['synthetic_fingerprint']
    source=m['source']['verified_sha256'];s=m['source']
    case=args.evidence/'production/nine-body-wrapper-rebase'
    snaps=fp['snapshots']
    need(fp['classification']=='INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE' and
         fp['all_ten_snapshots'] is True and set(snaps)=={'unit',*(f'body-{i}' for i in range(9))},
         'A1 synthetic fingerprint incomplete')
    for label,record in snaps.items():
        p=case/record['file']
        need(record['bytes']>0 and p.stat().st_size==record['bytes'] and
             sha(p)==record['sha256'],'A1 synthetic snapshot differs')
        expected=s['unit_sha256'] if label=='unit' else s['body_sha256'][int(label[5:])]
        need((record['sha256']!=expected) if label in ('unit','body-7') else
             (record['sha256']==expected),f'A1 mutation changed wrong body: {label}')
    before=(args.profile_source/TRANSLATOR).read_text()
    old_unit=s['unit_sha256'];old_body=s['body_sha256'][7]
    new_unit=snaps['unit']['sha256'];new_body=snaps['body-7']['sha256']
    need(before.count(old_unit)==before.count(old_body)==1,
         'A1 component-23 pins not unique')
    after=before.replace(old_unit,new_unit,1).replace(old_body,new_body,1)
    need(after.replace(new_unit,old_unit,1).replace(new_body,old_body,1)==before,
         'A1 TEST delta not reversible')
    patch=''.join(difflib.unified_diff(before.splitlines(keepends=True),
          after.splitlines(keepends=True),fromfile='a/'+str(TRANSLATOR),
          tofile='b/'+str(TRANSLATOR)))
    need(patch.count('@@')==4,'A1 TEST delta needs exactly two hunks')
    (args.evidence/'test-owner17-delta.patch').write_text(patch)
    write(args.evidence/'test-delta-profile.json',
          {'classification':'TEST_ONLY_REBASE_OWNER_HASH_DELTA',
           'production_translator_sha256':sha(args.profile_source/TRANSLATOR),
           'test_translator_sha256':hashlib.sha256(after.encode()).hexdigest(),
           'synthetic_unit_sha256':new_unit,'synthetic_body7_sha256':new_body,
           'patch_sha256':sha(args.evidence/'test-owner17-delta.patch'),
           'component20_unchanged':True,'verification_accepted':False})

def test(args,m):
    profile,cap,prep,mut=input_modules(args)
    delta_record=read(args.evidence/'test-delta-profile.json')
    before=(args.profile_source/TRANSLATOR).read_text()
    after=(args.test_source/TRANSLATOR).read_text()
    baseline=read(args.evidence/'capture-summary.json')['production_tool_snapshot']
    need(tool_snapshot(args.profile_source,args.proof_root)==baseline,
         'A1 production profile tool/proof source changed during TEST')
    new_unit=delta_record['synthetic_unit_sha256']
    new_body=delta_record['synthetic_body7_sha256']
    old_unit=m['source']['unit_sha256'];old_body=m['source']['body_sha256'][7]
    need(sha(args.test_source/TRANSLATOR)==delta_record['test_translator_sha256'] and
         after.replace(new_unit,old_unit,1).replace(new_body,old_body,1)==before,
         'A1 TEST console differs beyond owner hashes')
    for rel in ('src/verifast.ml','src/rust_frontend/vf_mir_translator/rust_parser.ml',
                'src/rust_frontend/vf_mir/vf_mir.capnp'):
        need(sha(args.profile_source/rel)==sha(args.test_source/rel),
             f'A1 TEST changed {rel}')
    for rel in ('bin/vf-rust-mir-exporter','bin/refinement-checker',
                'bin/vf-cxx-ast-exporter','bin/libz3.so'):
        need(sha(args.profile_source/rel)==sha(args.test_source/rel),
             f'A1 TEST changed stock binary {rel}')
    test_identity=tool_snapshot(args.test_source,args.proof_root)
    modified=lambda root:subprocess.check_output((
        'git','-C',str(root),'diff','--name-only','HEAD')).decode().splitlines()
    production_modified=modified(args.profile_source)
    need(production_modified==modified(args.test_source) and
         all(sha(args.profile_source/name)==sha(args.test_source/name)
             for name in production_modified if name!=str(TRANSLATOR)),
         'A1 TEST changed additional tracked tool source')
    need(test_identity['specs']==baseline['specs'] and
         test_identity['proof_std']==baseline['proof_std'] and
         all(value==baseline['tracked'][name]
             for name,value in test_identity['tracked'].items()
             if name!=str(TRANSLATOR)) and
         all(value==baseline['binaries'][name]
             for name,value in test_identity['binaries'].items()
             if name!='bin/verifast') and
         test_identity['tracked'][str(TRANSLATOR)]==
             delta_record['test_translator_sha256'] and
         test_identity['binaries']['bin/verifast']!=
             baseline['binaries']['bin/verifast'],
         'A1 TEST changed frozen specs/kernel/source/binaries')
    case=args.evidence/'test-case';case.mkdir()
    prod=args.evidence/'production/nine-body-wrapper-rebase'
    for kind in ('verified','original'):
        (case/kind).mkdir()
        (case/kind/'lib.rs').write_bytes((prod/kind/'lib.rs').read_bytes())
    source=m['source']['verified_sha256']
    need(sha(case/'verified/lib.rs')==source and
         sha(case/'original/lib.rs')==m['source']['original_sha256'],
         'A1 TEST source pair changed')
    selected=shadow(args.test_source,args.schema,case,args,mut,source)
    raw=profile.proof_stage(args,case,selected,'test-a1-refusal','rebase_a1_test',True)
    need(tool_snapshot(args.profile_source,args.proof_root)==baseline,
         'A1 production profile tool/proof source changed after TEST proof')
    write(args.evidence/'test-a1-stage.json',raw)
    identity=mutation_record(case,profile,args.proof_root,source,sha(prod/'normal-mir.bin'))
    log=(case/'test-a1-refusal.log').read_text(errors='replace')
    fatal=[x for x in log.splitlines() if x.startswith('Fatal error:')]
    accepted=(raw.get('status')=='RAN' and raw.get('exit')==2 and
              raw.get('source_unchanged') is True and
              raw.get('source_before')==raw.get('source_after') and
              raw.get('intrinsic_gate_active') is True and
              raw.get('pointer_drop_gate_active') is True and
              fatal==[A1_FATAL] and not cap.LINK.LINK.ERR.findall(log) and
              'SORT4-ACTUAL-OWNER-NINE:' in log and
              "Verifying function '" not in log)
    write(args.evidence/'test-result.json',
          {'classification':'REBASE_A1_MOVE_COPY_NEGATIVE' if accepted else 'INCONCLUSIVE',
           'intended_a1_refusal':accepted,'proof_stage':raw,'fatal':fatal,
           'mutation_identity':identity,'test_tool_snapshot':test_identity,
           'verification_accepted':False})
    need(accepted,'A1 TEST wrong refusal')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('capture','delta','test'))
    for key in ('proof-root','cloud-dir','profile-source','test-source',
                'compiler-sysroot','evidence'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--deadline-epoch',type=int,required=True)
    args=p.parse_args()
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER')=='cloud-build' and
         not os.environ.get('GITHUB_ACTIONS'),'Cloud Build required')
    args.schema=args.profile_source/'src/rust_frontend/vf_mir/vf_mir.capnp'
    os.environ['A1_TEST_PROOF_ROOT']=str(args.proof_root)
    os.environ['A1_TEST_CLOUD_DIR']=str(args.cloud_dir)
    profile=load(args.cloud_dir/'o26-wrapper-profile.py','o26_wrapper_a1_manifest')
    m=profile.profile(args.proof_root)
    {'capture':capture,'delta':delta,'test':test}[args.mode](args,m)

if __name__=='__main__':main()
