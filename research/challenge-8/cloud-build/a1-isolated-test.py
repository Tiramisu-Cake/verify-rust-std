#!/usr/bin/env python3
"""O26 A1 isolated negative: Cloud evidence only, never a production proof."""
from __future__ import annotations
import argparse
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace

VF_HEAD='f76012fb518703b1d98e243ac4f487f16877cfcb'
SOURCE='1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6'
ORIGINAL='466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5'
UNIT='10cf6e4d2a462082d456135078a77ea6670358f1ad15e0d81901104e8a102b43'
BODY7='9577c64905c4a45eecc4aab506f6276fea076f8a7a18d2f7ca0304cf70205b86'
TRANSLATOR='src/rust_frontend/vf_mir_translator/vf_mir_translator.ml'
SCHEMA='src/rust_frontend/vf_mir/vf_mir.capnp'
BINARIES=('bin/verifast','bin/vf-rust-mir-exporter','bin/refinement-checker',
          'bin/vf-cxx-ast-exporter','bin/libz3.so')
TRACKED=('src/verifast.ml',TRANSLATOR,'src/rust_frontend/vf_mir_translator/rust_parser.ml',SCHEMA)
STD=('library/core/src/hint.rs','library/core/src/intrinsics/mod.rs',
     'library/core/src/mem/manually_drop.rs','library/core/src/mem/maybe_dangling.rs',
     'library/core/src/mem/maybe_uninit.rs','library/core/src/mem/mod.rs',
     'library/core/src/ptr/mod.rs','library/core/src/ptr/mut_ptr.rs')
OWNER_MARK='SORT4-ACTUAL-OWNER-NINE: exact source and complete decoded MIR admission only'
A1_MARK='SORT4-A1-NINE: exact source, typed local pair and outer cleanup call admitted'
OWNER_FATAL='Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: owner complete decoded unit SHA256")'
A1_FATAL='Fatal error: exception Failure("SORT4-A1-NINE: certificate mismatch: outer assume_init must move selected wrapper")'
MUTATION='outer_assume_init_move_to_copy'
PROD_CASE='production/nine-body-a1-owned-forget'


def need(ok:bool,why:str):
    if not ok:raise ValueError(why)

def sha(path:Path)->str:return hashlib.sha256(path.read_bytes()).hexdigest()
def safe_sha(path:Path):
    try:return sha(path)
    except OSError:return None
def write(path:Path,data:dict):path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
def read(path:Path):
    try:return json.loads(path.read_text())
    except (OSError,ValueError):return None

def git(root:Path,*args:str)->bytes:
    return subprocess.check_output(('git','-C',str(root),*args))

def load(path:Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    need(spec is not None and spec.loader is not None,f'module missing {path}')
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module

def mutator():
    global MUT
    if 'MUT' not in globals():
        root=os.environ.get('A1_TEST_PROOF_ROOT')
        need(root is not None,'A1_TEST_PROOF_ROOT missing for exact shadow mutation')
        MUT=load(Path(root)/'research/challenge-8/overnight-helper/capture-actual-owner-mir-mutation.py',
                 'o26_a1_test_mutator')
    return MUT

def mutate_actual_mir(decoded:str,mutation:str)->str:
    """Called by the disposable exporter wrapper on the canonical normal unit."""
    need(mutation==MUTATION,'unexpected A1 TEST mutation')
    m=mutator()
    start,end,body=m.selected_body(decoded,'select_unpredictable')
    name='name = "std::mem::MaybeUninit::<T>::assume_init"'
    need(body.count(name)==1,'outer assume_init call not unique')
    at=body.index(name)
    call_anchor=body.rfind('call = (',0,at)
    need(call_anchor>=0,'outer assume_init call record missing')
    call_at=call_anchor+len('call = ')
    call=m.PREP.LINK.CONSTRUCTOR.mir_balanced_item(body,call_at)
    need(call.count(name)==1,'selected call is not assume_init')
    lo=call.index('args = [');hi=call.index('destination = (',lo)
    args=call[lo:hi]
    need(args.count('move = (')==1 and args.count('copy = (')==0 and
         args.count('local = (name = "_37")')==1 and
         args.count('projection = []')==1 and
         args.count('localIsMutable = true')==1 and
         args.count('kind = (other = void)')==1,
         'outer assume_init argument is not exact Move(_37)')
    changed=args.replace('move = (','copy = (',1)
    need(changed.replace('copy = (','move = (',1)==args,
         'A1 TEST argument changed more than the operand variant')
    new_call=call[:lo]+changed+call[hi:]
    new_body=body[:call_at]+new_call+body[call_at+len(call):]
    result=decoded[:start]+new_body+decoded[end:]
    need(result!=decoded,'A1 TEST mutation had no effect')
    return result

def specs(root:Path)->dict:
    base=root/'bin/rust'
    return {str(p.relative_to(root)):sha(p) for p in sorted(base.rglob('*.rsspec'))}

def snapshot(root:Path,proof:Path,production_patch:Path,stock:Path)->dict:
    need(git(root,'rev-parse','HEAD').decode().strip()==VF_HEAD,'VeriFast source HEAD differs')
    diff=git(root,'diff','--binary','HEAD')
    need(diff==production_patch.read_bytes(),'production applied diff differs')
    need(all((root/p).is_file() for p in TRACKED+BINARIES),'production tool files absent')
    for p in BINARIES[1:]:
        need((root/p).read_bytes()==(stock/p).read_bytes(),f'production stock binary differs: {p}')
    proof_std={p:sha(proof/p) for p in STD}
    return {'verifast_head':VF_HEAD,'proof_sha':git(proof,'rev-parse','HEAD').decode().strip(),
      'production_diff_sha256':hashlib.sha256(diff).hexdigest(),
      'production_modified_files':git(root,'diff','--name-only','HEAD').decode().splitlines(),
      'tracked':{p:sha(root/p) for p in TRACKED},
      'binaries':{p:sha(root/p) for p in BINARIES},
      'specs':specs(root),'proof_std':proof_std}

def setup_shadow(tool:Path,schema:Path,case:Path,proof:Path):
    m=mutator()
    shadow=m.make_shadow(tool,schema,case,MUTATION,SOURCE)
    wrapper=shadow/'bin/vf-rust-mir-exporter'
    source=wrapper.read_text()
    anchor=repr(str(m.HERE/'capture-actual-owner-mir-mutation.py'))
    need(source.count(anchor)==1,'TEST wrapper import anchor differs')
    source=source.replace(anchor,repr(str(Path(__file__).resolve())),1)
    wrapper.write_text(source)
    (case/'mir-exporter-wrapper.py').write_text(source)
    profile=read(case/'mutation-profile.json')
    need(profile is not None,'TEST wrapper profile missing')
    profile['wrapper_sha256']=sha(wrapper)
    profile['test_only']=True
    profile['mutation']=MUTATION
    write(case/'mutation-profile.json',profile)
    return shadow

def exact_wrapper_record(case:Path)->dict:
    names=('mutation-record.json','mutation-profile.json','normal-mir.bin',
      'canonical-mir.bin','mutated-mir.bin','canonical-mir.txt','mutated-mir.txt',
      'mir-exporter-wrapper.py')
    paths={n:case/n for n in names}
    paths['active-wrapper']=case/'mutation-profile/bin/vf-rust-mir-exporter'
    need(all(p.is_file() for p in paths.values()),'TEST mutation evidence missing')
    record=read(paths['mutation-record.json']);profile=read(paths['mutation-profile.json'])
    need(record is not None and profile is not None,'TEST mutation record unavailable')
    canonical=paths['canonical-mir.txt'].read_text()
    changed=paths['mutated-mir.txt'].read_text()
    need(mutate_actual_mir(canonical,MUTATION)==changed,
         'TEST mutation changed more than selected Move(_37)')
    need(record.get('matched') is True and record.get('mutation')==MUTATION and
      all(record.get(k)==0 for k in ('exporter_exit','decode_exit','encode_exit')) and
      record.get('selected_source_sha256')==SOURCE and
      record.get('canonical_sha256')==sha(paths['canonical-mir.bin'])==sha(paths['normal-mir.bin']) and
      record.get('mutated_sha256')==sha(paths['mutated-mir.bin']) and
      paths['canonical-mir.bin'].read_bytes()!=paths['mutated-mir.bin'].read_bytes() and
      profile.get('base_console_sha256')==profile.get('shadow_console_sha256') and
      profile.get('wrapper_sha256')==sha(paths['active-wrapper'])==sha(paths['mir-exporter-wrapper.py']),
      'TEST wrapper record differs from canonical normal export')
    return {'mutation':MUTATION,'exact_one_field_diff':True,
      'canonical_mir_bin_sha256':sha(paths['canonical-mir.bin']),
      'mutated_mir_bin_sha256':sha(paths['mutated-mir.bin']),
      'canonical_mir_text_sha256':sha(paths['canonical-mir.txt']),
      'mutated_mir_text_sha256':sha(paths['mutated-mir.txt']),
      'wrapper_sha256':sha(paths['active-wrapper']),
      'real_exporter_sha256':record['real_exporter_sha256']}

def positive(evidence:Path)->dict:
    ev=evidence.parents[1]
    candidate=ev/'cases/candidate'
    summary=read(candidate/'capture/summary.json') or {}
    compare=read(candidate/'capture-compare.json') or {}
    proof=read(candidate/'proof-stage.json') or {}
    case=candidate/'capture/nine-body-a1-owned-forget'
    stage=proof.get('stage',{})
    log=case/'refreshed-proof.log'
    text=log.read_text(errors='replace') if log.is_file() else ''
    admitted=(OWNER_MARK in text and A1_MARK in text)
    complete=(summary.get('frontend_refinement_and_full_body_capture') is True and
      compare.get('capture_complete') is True and
      summary.get('source',{}).get('verified_sha256')==SOURCE and
      summary.get('source',{}).get('original_sha256')==ORIGINAL and
      sha(case/'verified/lib.rs')==SOURCE and sha(case/'original/lib.rs')==ORIGINAL and
      stage.get('status')=='RAN' and stage.get('source_unchanged') is True and
      stage.get('source_before')==stage.get('source_after') and
      stage.get('intrinsic_gate_active') is True and
      stage.get('pointer_drop_gate_active') is True and
      stage.get('exit') not in (None,124,137) and admitted)
    return {'support_complete':complete,'owner_and_a1_admission_visible':admitted,
      'proof_exit':stage.get('exit'),'actual_helper_proved':False,
      'canonical_case':str(case),'canonical_normal_sha256':sha(case/'normal-mir.bin'),
      'canonical_readonly_sha256':sha(case/'readonly-mir.bin')}

def capture(args):
    ev=args.evidence
    proof=args.proof_root
    cap=load(proof/'research/challenge-8/overnight-assume-actual/capture.py','o26_a1_capture')
    recipe=load(args.cloud_dir/'o26-recipe.py','o26_a1_six_gates')
    prep=positive(ev)
    need(prep['support_complete'],'canonical production owner/A1 admission unavailable')
    out=ev/'production'
    source=cap.PREP.write_case(proof,out)
    case=out/cap.PREP.CASE_NAME
    need(case==ev/PROD_CASE,'A1 TEST prepared case path differs')
    need(source['verified_sha256']==SOURCE and source['original_sha256']==ORIGINAL and
      source['ghost_strip_identity'] is True and
      sha(case/'verified/lib.rs')==SOURCE and sha(case/'original/lib.rs')==ORIGINAL,
      'A1 TEST source pair differs')
    earlier=read(ev.parents[1]/'cases/candidate/capture/summary.json')
    need(source['source_order']==earlier['source']['source_order'] and len(source['source_order'])==9,
      'A1 TEST source order differs')
    stage_args=SimpleNamespace(tool_home=args.production_source,schema=args.schema,
        compiler_sysroot=str(args.compiler_sysroot),deadline_epoch=args.deadline_epoch,
        first_barrier=False,fingerprint_probe=False)
    cap.clear_semantic_opt_ins()
    support=cap.GUARD.capture_case(case,source,stage_args)
    stages=support.get('stages',{})
    need(support.get('frontend_refinement') is True and support.get('source_unchanged') is True and
      all(stages.get(k,{}).get('exit')==0 for k in ('normal-export','normal-decode',
        'readonly-export','readonly-decode','refinement')),
      'A1 TEST paired normal/readonly/refinement failed')
    need(sha(case/'normal-mir.bin')==prep['canonical_normal_sha256'] and
      sha(case/'readonly-mir.bin')==prep['canonical_readonly_sha256'],
      'A1 TEST paired MIR differs from canonical production capture')
    shadow=setup_shadow(args.production_source,args.schema,case,proof)
    raw=recipe.proof_stage(proof,case,shadow,args.schema,args.compiler_sysroot,
                           args.deadline_epoch,'production-owner-refusal','a1_owner17')
    write(ev/'production-owner-refusal-stage.json',raw)
    probe_args=SimpleNamespace(**vars(stage_args));probe_args.tool_home=shadow
    probe=cap.refusal_fingerprint(case,source,probe_args)
    write(ev/'synthetic-fingerprint.json',probe)
    wrapper=exact_wrapper_record(case)
    write(ev/'capture-summary.json',{'canonical_positive':prep,'source':source,
      'paired_support':support,'production_owner_refusal':raw,
      'synthetic_probe':probe,'mutation':wrapper,
      'classification':'A1_TEST_SYNTHETIC_CAPTURE_ONLY','accepted':False})
    print(json.dumps({'production_owner_exit':raw.get('exit'),
      'fingerprint':probe.get('classification')}),flush=True)

def delta(args):
    ev=args.evidence
    report=read(ev/'capture-summary.json')
    need(report is not None,'A1 synthetic capture missing')
    probe=report['synthetic_probe'];snaps=probe['snapshots']
    canonical=read(ev.parents[1]/'cases/candidate/capture/summary.json')
    old=canonical['fingerprint']['snapshots']
    need(old['unit']['sha256']==UNIT and old['body-7']['sha256']==BODY7,
         'canonical owner17 unit/body-7 certificate differs')
    need(probe.get('classification')=='INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE' and
      probe.get('all_ten_snapshots') is True and set(snaps)==set(old),
      'synthetic refusal-only fingerprint incomplete')
    case=ev/PROD_CASE
    for key,row in snaps.items():
        need(sha(case/row['file'])==row['sha256'] and
             (case/row['file']).stat().st_size==row['bytes'] and row['bytes']>0,
             f'synthetic fingerprint file differs: {key}')
        need((row['sha256']!=old[key]['sha256']) if key in ('unit','body-7') else
             (row['sha256']==old[key]['sha256']),
             f'synthetic fingerprint affected wrong body: {key}')
    before=(args.production_source/TRANSLATOR).read_text()
    need(before.count(UNIT)==1 and before.count(BODY7)==1,
         'production owner17 certificate pins not unique')
    need(sha(args.production_source/TRANSLATOR)==
      read(args.proof_root/'research/challenge-8/overnight-assume-actual/O26-REFRESH-PROFILE.json')['refreshed_translator_sha256'],
      'production translator profile SHA differs')
    new_unit=snaps['unit']['sha256'];new_body7=snaps['body-7']['sha256']
    after=before.replace(UNIT,new_unit,1).replace(BODY7,new_body7,1)
    need(after.replace(new_unit,UNIT,1).replace(new_body7,BODY7,1)==before,
         'TEST delta changes more than two owner17 pins')
    patch=''.join(difflib.unified_diff(before.splitlines(keepends=True),
      after.splitlines(keepends=True),fromfile='a/'+TRANSLATOR,tofile='b/'+TRANSLATOR))
    need(patch.count('@@')==4,'TEST delta must have exactly two hunks')
    (ev/'test-owner17-delta.patch').write_text(patch)
    write(ev/'test-delta-profile.json',{'classification':'TEST_ONLY_OWNER17_SYNTHETIC_CERTIFICATE',
      'accepted':False,'production_translator_sha256':hashlib.sha256(before.encode()).hexdigest(),
      'expected_test_translator_sha256':hashlib.sha256(after.encode()).hexdigest(),
      'synthetic_unit_sha256':new_unit,'synthetic_body_7_sha256':new_body7,
      'unchanged_body_snapshots':{k:snaps[k]['sha256'] for k in snaps if k not in ('unit','body-7')},
      'test_delta_sha256':sha(ev/'test-owner17-delta.patch'),
      'byte_inverse_exact':True,'a1_component20_unchanged':True,
      'source22_unchanged':True,'normal_cleanup_24_unchanged':True})

def verify_delta(args):
    ev=args.evidence;record=read(ev/'test-delta-profile.json')
    prod=(args.production_source/TRANSLATOR).read_text()
    test=(args.test_source/TRANSLATOR).read_text()
    need(record is not None and sha(args.test_source/TRANSLATOR)==record['expected_test_translator_sha256'],
      'TEST translator SHA differs')
    saved=ev/'test-translator.ml'
    if saved.exists():
        need(saved.read_bytes()==(args.test_source/TRANSLATOR).read_bytes(),
             'saved TEST translator differs')
    need(test.replace(record['synthetic_unit_sha256'],UNIT,1).replace(
      record['synthetic_body_7_sha256'],BODY7,1)==prod,
      'TEST translator contains non-owner17 changes')
    need(git(args.test_source,'diff','--name-only','HEAD').decode().splitlines()==
         git(args.production_source,'diff','--name-only','HEAD').decode().splitlines(),
         'TEST source modified-file inventory differs')
    need((args.test_source/'src/verifast.ml').read_bytes()==
         (args.production_source/'src/verifast.ml').read_bytes(),
         'TEST kernel differs')
    for rel in TRACKED[2:]:
        need((args.test_source/rel).read_bytes()==(args.production_source/rel).read_bytes(),
             f'TEST source differs: {rel}')
    need(specs(args.test_source)==specs(args.production_source),'TEST effective specs differ')
    print('TEST-only two-pin source delta verified',flush=True)

def test(args):
    ev=args.evidence;source=read(ev/'capture-summary.json')['source']
    prod=ev/PROD_CASE;case=ev/'test-case'
    case.mkdir(exist_ok=False)
    for kind in ('verified','original'):
        (case/kind).mkdir()
        (case/kind/'lib.rs').write_bytes((prod/kind/'lib.rs').read_bytes())
    need(sha(case/'verified/lib.rs')==SOURCE and sha(case/'original/lib.rs')==ORIGINAL,
      'TEST case source pair changed')
    recipe=load(args.cloud_dir/'o26-recipe.py','o26_a1_test_six_gates')
    shadow=setup_shadow(args.test_source,args.schema,case,args.proof_root)
    raw=recipe.proof_stage(args.proof_root,case,shadow,args.schema,args.compiler_sysroot,
                           args.deadline_epoch,'test-a1-refusal','a1_isolated')
    write(ev/'test-a1-refusal-stage.json',raw)
    wrapper=exact_wrapper_record_test(case,prod)
    write(ev/'test-stage-summary.json',{'stage':raw,'source_sha256':SOURCE,
      'original_sha256':ORIGINAL,'test_wrapper':wrapper,'accepted':False})
    print(json.dumps({'test_a1_exit':raw.get('exit')}),flush=True)

def exact_wrapper_record_test(case:Path,prod:Path)->dict:
    record=read(case/'mutation-record.json');profile=read(case/'mutation-profile.json')
    need(record is not None and profile is not None,'TEST console mutation missing')
    need(mutate_actual_mir((case/'canonical-mir.txt').read_text(),MUTATION)==
         (case/'mutated-mir.txt').read_text(),'TEST console mutation differs')
    need(record.get('matched') is True and record.get('selected_source_sha256')==SOURCE and
         record.get('canonical_sha256')==sha(case/'canonical-mir.bin')==sha(prod/'normal-mir.bin') and
         record.get('mutated_sha256')==sha(case/'mutated-mir.bin') and
         record.get('mutated_sha256')==
           (read(prod/'mutation-record.json') or {}).get('mutated_sha256') and
         all(record.get(k)==0 for k in ('exporter_exit','decode_exit','encode_exit')) and
         profile.get('wrapper_sha256')==sha(case/'mutation-profile/bin/vf-rust-mir-exporter') and
         profile.get('base_console_sha256')==profile.get('shadow_console_sha256'),
         'TEST console wrapper/canonical bytes differ')
    return {'exact_one_field_diff':True,
      'canonical_mir_bin_sha256':sha(case/'canonical-mir.bin'),
      'mutated_mir_bin_sha256':sha(case/'mutated-mir.bin'),
      'test_console_sha256':profile['base_console_sha256'],
      'real_exporter_sha256':record['real_exporter_sha256']}

def audit(args):
    ev=args.evidence
    baseline=read(ev/'production-snapshot.json') or {}
    current=None
    try:current=snapshot(args.production_source,args.proof_root,
                         args.production_patch,args.stock_home)
    except (OSError,ValueError,subprocess.CalledProcessError):pass
    capture_report=read(ev/'capture-summary.json') or {}
    delta_report=read(ev/'test-delta-profile.json') or {}
    test_report=read(ev/'test-stage-summary.json') or {}
    owner=read(ev/'production-owner-refusal-stage.json') or {}
    a1=read(ev/'test-a1-refusal-stage.json') or {}
    prod_log=ev/PROD_CASE/'production-owner-refusal.log'
    test_log=ev/'test-case/test-a1-refusal.log'
    ptext=prod_log.read_text(errors='replace') if prod_log.is_file() else ''
    ttext=test_log.read_text(errors='replace') if test_log.is_file() else ''
    errors=re.compile(r'^.*: error:.*$',re.M)
    prod_fatals=[x for x in ptext.splitlines() if x.startswith('Fatal error:')]
    test_fatals=[x for x in ttext.splitlines() if x.startswith('Fatal error:')]
    source_support=(capture_report.get('canonical_positive',{}).get('support_complete') is True and
      capture_report.get('paired_support',{}).get('frontend_refinement') is True and
      all(capture_report.get('paired_support',{}).get('stages',{}).get(k,{}).get('exit')==0
          for k in ('normal-export','normal-decode','readonly-export','readonly-decode','refinement')) and
      capture_report.get('source',{}).get('verified_sha256')==SOURCE and
      capture_report.get('source',{}).get('original_sha256')==ORIGINAL and
      safe_sha(ev/PROD_CASE/'verified/lib.rs')==SOURCE and
      safe_sha(ev/PROD_CASE/'original/lib.rs')==ORIGINAL and
      safe_sha(ev/'test-case/verified/lib.rs')==SOURCE and
      safe_sha(ev/'test-case/original/lib.rs')==ORIGINAL)
    mutation_exact=False
    if source_support:
      try:mutation_exact=exact_wrapper_record(ev/PROD_CASE)==capture_report.get('mutation')
      except (OSError,ValueError,KeyError,subprocess.CalledProcessError):pass
    source_support=source_support and mutation_exact
    owner_rejected=(owner.get('status')=='RAN' and owner.get('exit')==2 and
      owner.get('source_unchanged') is True and
      owner.get('source_before')==owner.get('source_after') and
      owner.get('source_before',{}).get('verified/lib.rs')==SOURCE and
      owner.get('source_before',{}).get('original/lib.rs')==ORIGINAL and
      owner.get('intrinsic_gate_active') is True and
      owner.get('pointer_drop_gate_active') is True and
      prod_fatals==[OWNER_FATAL] and not errors.findall(ptext) and
      OWNER_MARK not in ptext and A1_MARK not in ptext and
      "Verifying function '" not in ptext)
    probe=capture_report.get('synthetic_probe',{})
    canonical_summary=read(ev.parents[1]/'cases/candidate/capture/summary.json') or {}
    old_snaps=canonical_summary.get('fingerprint',{}).get('snapshots',{})
    snaps=probe.get('snapshots',{})
    snapshot_files=(set(snaps)==set(old_snaps)=={'unit',*(f'body-{i}' for i in range(9))} and
      all(safe_sha(ev/PROD_CASE/(row.get('file') or 'missing'))==row.get('sha256') and
          (row.get('bytes') or 0)>0 for row in snaps.values()))
    eight_same=(snapshot_files and
      all(snaps[k]['sha256']==old_snaps[k]['sha256'] for k in snaps
          if k not in ('unit','body-7')) and
      snaps['unit']['sha256']!=old_snaps['unit']['sha256'] and
      snaps['body-7']['sha256']!=old_snaps['body-7']['sha256'])
    fingerprint=(probe.get('classification')=='INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE' and
      probe.get('all_ten_snapshots') is True and snapshot_files and eight_same and
      delta_report.get('byte_inverse_exact') is True and
      delta_report.get('synthetic_unit_sha256')==snaps.get('unit',{}).get('sha256') and
      delta_report.get('synthetic_body_7_sha256')==snaps.get('body-7',{}).get('sha256'))
    a1_rejected=(a1.get('status')=='RAN' and a1.get('exit')==2 and
      a1.get('source_unchanged') is True and
      a1.get('source_before')==a1.get('source_after') and
      a1.get('source_before',{}).get('verified/lib.rs')==SOURCE and
      a1.get('source_before',{}).get('original/lib.rs')==ORIGINAL and
      a1.get('intrinsic_gate_active') is True and
      a1.get('pointer_drop_gate_active') is True and
      test_fatals==[A1_FATAL] and not errors.findall(ttext) and
      OWNER_MARK in ttext and A1_MARK not in ttext and
      "Verifying function '" not in ttext)
    tool_ok=False
    if test_report and delta_report:
      try:
        verify_delta(args)
        tool_ok=(sha(args.test_source/TRANSLATOR)==delta_report['expected_test_translator_sha256'] and
          safe_sha(ev/'test-translator.ml')==delta_report['expected_test_translator_sha256'] and
          (ev/'test-applied.patch').read_bytes()==git(args.test_source,'diff','--binary','HEAD') and
          exact_wrapper_record_test(ev/'test-case',ev/PROD_CASE)==test_report['test_wrapper'] and
          test_report['test_wrapper']['test_console_sha256']==sha(args.test_source/'bin/verifast') and
          test_report['test_wrapper']['real_exporter_sha256']==sha(args.production_source/'bin/vf-rust-mir-exporter') and
          sha(args.test_source/'bin/vf-rust-mir-exporter')==sha(args.production_source/'bin/vf-rust-mir-exporter') and
          sha(args.test_source/'bin/refinement-checker')==sha(args.production_source/'bin/refinement-checker'))
      except (OSError,ValueError,KeyError,subprocess.CalledProcessError):pass
    production_unchanged=bool(baseline) and current==baseline
    complete=(source_support and owner_rejected and fingerprint and a1_rejected and
      tool_ok and production_unchanged)
    report={'classification':'ISOLATED_A1_MOVE_NEGATIVE_MATCH' if complete else 'INCONCLUSIVE',
      'diagnostic_complete':complete,'verification_accepted':False,'accepted':False,
      'actual_helper_proved':False,'test_profile_only':True,
      'production_unchanged':production_unchanged,'source_pair_and_refinement':source_support,
      'production_owner17_refusal':owner_rejected,'synthetic_fingerprint_complete':fingerprint,
      'test_tool_isolated':tool_ok,'test_a1_exact_refusal':a1_rejected,
      'a1_negative_obligation':'outer assume_init must move selected wrapper',
      'production_fatals':prod_fatals,'test_fatals':test_fatals,
      'production_exit':owner.get('exit'),'test_exit':a1.get('exit'),
      'synthetic_unit_sha256':delta_report.get('synthetic_unit_sha256'),
      'synthetic_body_7_sha256':delta_report.get('synthetic_body_7_sha256'),
      'test_delta_sha256':delta_report.get('test_delta_sha256'),
      'production_snapshot':baseline,'test_profile':delta_report,
      'pending':['full positive helper proof','production A1 root mismatch negative',
                 'normal/unwind ownership acceptance']}
    write(ev/'diagnostic-audit.json',report)
    print(json.dumps({k:report[k] for k in ('classification','diagnostic_complete','verification_accepted')}),flush=True)
    if not complete:raise SystemExit(1)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('snapshot','capture','delta','verify-delta','test','audit'))
    for n in ('production-source','production-patch','stock-home','compiler-sysroot',
              'evidence','proof-root','work-root','cloud-dir'):
        p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--deadline-epoch',type=int,required=True)
    p.add_argument('--test-source',type=Path)
    a=p.parse_args()
    if a.mode in ('verify-delta','test','audit'):
        need(a.test_source is not None,'TEST source path required')
    a.schema=a.production_source/SCHEMA
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER')=='cloud-build' and
         not os.environ.get('GITHUB_ACTIONS'),'Cloud provider required; fake GitHub identity forbidden')
    if a.mode=='snapshot':write(a.evidence/'production-snapshot.json',
      snapshot(a.production_source,a.proof_root,a.production_patch,a.stock_home))
    elif a.mode=='capture':capture(a)
    elif a.mode=='delta':delta(a)
    elif a.mode=='verify-delta':verify_delta(a)
    elif a.mode=='test':test(a)
    else:audit(a)
if __name__=='__main__':main()
