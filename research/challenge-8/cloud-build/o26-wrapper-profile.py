#!/usr/bin/env python3
"""Cloud-only, fail-closed component-23 wrapper-rebase profile diagnostic."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path('research/challenge-8')
MANIFEST = ROOT/'overnight-assume-actual/O26-WRAPPER-REBASE-PROFILE.json'
TRANSLATOR = Path('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml')
ORIGINAL = '466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5'
PRODUCTION_TRANSLATOR = '0862e635075edd06a827c567710a3e1125ac03aa122e95149db755a1fddce48a'
OLD_SOURCE = '1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6'
PAIR = ('SORT4_WRAPPER_REBASE_REPO_ROOT', 'SORT4_WRAPPER_REBASE_ADMISSION')
OWNER = 'SORT4-ACTUAL-OWNER-NINE: exact source and complete decoded MIR admission only'
A1 = 'SORT4-A1-NINE: exact source, typed local pair and outer cleanup call admitted'
PREFIX = (
    'sort4_certified_maybeuninit::sort4_checked_maybeuninit_new',
    'sort4_checked_as_mut_ptr', 'sort4_checked_pointer_drop',
    'sort4_checked_generic_drop', 'checked_transmute_neo_pointer',
    'checked_assume_init_pointer', 'checked_forget_owned',
)
VARIANTS = ('source_owner', 'source_outcome', 'forget_move_to_copy',
            'forget_cleanup_to_wrong_block')
TYPED_OUTER = {
    'indexing':'zero-based decoded MIR block indexes; exporter local names',
    'local_count':52,'block_count':35,
    'save_old_ghost_calls':[
        {'block':4,'destination_local':'_12','normal_block':5,'unwind':'Continue'},
        {'block':5,'destination_local':'_13','normal_block':6,'unwind':'Continue'},
    ],
    'rebase_both_ghost_calls':[
        {'block':21,'destination_local':'_39','normal_block':22,'cleanup_block':34},
        {'block':22,'destination_local':'_40','normal_block':23,'cleanup_block':34},
        {'block':23,'destination_local':'_41','normal_block':24,'cleanup_block':34},
        {'block':24,'destination_local':'_42','normal_block':25,'cleanup_block':34},
        {'block':25,'destination_local':'_43','normal_block':26,'cleanup_block':34},
        {'block':26,'destination_local':'_44','normal_block':27,'cleanup_block':34},
        {'block':27,'destination_local':'_45','normal_block':28,'cleanup_block':34},
        {'block':28,'destination_local':'_46','normal_block':29,'cleanup_block':34},
    ],
    'pointer_drop_receiver_local':'_30',
    'forget':{'block':16,'guard_source_local':'_26','move_argument_local':'_34',
              'destination_local':'_33','normal_block':17,'cleanup_block':34,
              'negative_cleanup_block':33},
    'assume_init':{'block':30,'move_argument_local':'_47',
                   'destination_local':'_0','normal_block':31,'cleanup_block':34},
    'unwind_chain':{'resume_block':32,'drop_block':33,'switch_block':34,
                    'switch_local':'_51','switch_targets':[32,33]},
    'shared_cleanup_predecessor_count':18,
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def read(path):
    return json.loads(Path(path).read_text())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, f'missing module: {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def profile(proof):
    m = read(proof/MANIFEST)
    s = m['source']
    h = re.compile(r'[0-9a-f]{64}\Z')
    need(m['classification']=='EXPERIMENTAL_O26_WRAPPER_REBASE_COMPONENT23_R2_NOT_ACCEPTED',
         'component-23 manifest classification differs')
    need(m['component23_patch']=='overnight-assume-actual/verifast-o26-wrapper-rebase-profile-26.10.patch',
         'component-23 patch path differs')
    need(m['production_translator_sha256']==PRODUCTION_TRANSLATOR and
         m['kernel_modified'] is False and m['verification_accepted'] is False,
         'component-23 production identity differs')
    need(m['opt_in']=={PAIR[0]:'exact proof root', PAIR[1]:'1'},
         'component-23 opt-in contract differs')
    need(m['typed_outer_mir']==TYPED_OUTER,
         'component-23 observed typed MIR graph differs')
    need(s['original_sha256']==ORIGINAL and
         isinstance(s['body_sha256'], list) and len(s['body_sha256'])==9,
         'component-23 source shape differs')
    for value in (m['component23_patch_sha256'], m['new_translator_sha256'],
                  s['verified_sha256'], s['unit_sha256'], *s['body_sha256']):
        need(isinstance(value,str) and h.fullmatch(value) is not None,
             'component-23 observed SHA missing; draft cannot run')
    need(s['verified_sha256']!=OLD_SOURCE and
         s['unit_sha256']!='10cf6e4d2a462082d456135078a77ea6670358f1ad15e0d81901104e8a102b43',
         'component-23 source/unit must be distinct from canonical')
    patch=proof/ROOT/m['component23_patch']
    need(sha(patch)==m['component23_patch_sha256'], 'component-23 patch SHA differs')
    return m


def tool_snapshot(root,proof):
    """HEAD plus complete tracked diff identifies every tracked source byte."""
    head=subprocess.check_output(('git','-C',str(root),'rev-parse','HEAD')).decode().strip()
    diff=subprocess.check_output(('git','-C',str(root),'diff','--binary','HEAD'))
    names=subprocess.check_output(('git','-C',str(root),'diff','--name-only','HEAD')).decode().splitlines()
    tracked=('src/verifast.ml',str(TRANSLATOR),
             'src/rust_frontend/vf_mir_translator/rust_parser.ml',
             'src/rust_frontend/vf_mir/vf_mir.capnp')
    bins=('bin/verifast','bin/vf-rust-mir-exporter','bin/refinement-checker',
          'bin/vf-cxx-ast-exporter','bin/libz3.so')
    std=('library/core/src/hint.rs','library/core/src/intrinsics/mod.rs',
         'library/core/src/mem/manually_drop.rs','library/core/src/mem/maybe_dangling.rs',
         'library/core/src/mem/maybe_uninit.rs','library/core/src/mem/mod.rs',
         'library/core/src/ptr/mod.rs','library/core/src/ptr/mut_ptr.rs')
    return {'head':head,'tracked_diff_sha256':hashlib.sha256(diff).hexdigest(),
            'modified_tracked_source_sha256':{name:sha(root/name) for name in names},
            'critical_source_sha256':{name:sha(root/name) for name in tracked},
            'effective_rsspec_sha256':{str(p.relative_to(root)):sha(p)
                for p in sorted((root/'bin/rust').rglob('*.rsspec'))},
            'binary_sha256':{name:sha(root/name) for name in bins},
            'proof_std_sha256':{name:sha(proof/name) for name in std}}


def tool_identity(args, m):
    prod=args.production_source
    new=args.profile_source
    baseline=read(args.evidence/'production-tool-baseline.json')
    production=tool_snapshot(prod,args.proof_root)
    profile_now=tool_snapshot(new,args.proof_root)
    need(production==baseline,'production tool/proof source changed since pre-copy snapshot')
    need(sha(prod/TRANSLATOR)==PRODUCTION_TRANSLATOR and
         sha(new/TRANSLATOR)==m['new_translator_sha256'],
         'component-23 translator identity differs')
    before=subprocess.check_output(('git','-C',str(prod),'diff','--binary','HEAD'))
    after=subprocess.check_output(('git','-C',str(new),'diff','--binary','HEAD'))
    need(before==args.production_patch.read_bytes(), 'production patch differs')
    old_names=subprocess.check_output(('git','-C',str(prod),'diff','--name-only','HEAD')).decode().splitlines()
    new_names=subprocess.check_output(('git','-C',str(new),'diff','--name-only','HEAD')).decode().splitlines()
    need(after!=before and old_names==new_names and str(TRANSLATOR) in old_names and
         production['head']==profile_now['head']=='f76012fb518703b1d98e243ac4f487f16877cfcb',
         'component-23 touched new files or had no effect')
    for name in old_names:
        if name!=str(TRANSLATOR):
            need(sha(prod/name)==sha(new/name),f'component-23 altered tracked source {name}')
    patch_text=(args.proof_root/ROOT/m['component23_patch']).read_text()
    need([x for x in patch_text.splitlines() if x.startswith(('--- ','+++ '))]==
         ['--- a/'+str(TRANSLATOR),'+++ b/'+str(TRANSLATOR)],
         'component-23 patch scope differs from translator only')
    for name in ('src/verifast.ml','src/rust_frontend/vf_mir_translator/rust_parser.ml',
                 'src/rust_frontend/vf_mir/vf_mir.capnp'):
        need(sha(prod/name)==sha(new/name), f'component-23 changed {name}')
    for name in ('bin/vf-rust-mir-exporter','bin/refinement-checker',
                 'bin/vf-cxx-ast-exporter','bin/libz3.so'):
        need(sha(prod/name)==sha(new/name)==sha(args.stock_home/name),
             f'component-23 changed stock binary {name}')
    need(sha(prod/'bin/verifast')!=sha(new/'bin/verifast'),
         'component-23 console did not change')
    old_specs=production['effective_rsspec_sha256']
    new_specs=profile_now['effective_rsspec_sha256']
    need(old_specs and old_specs==new_specs and
         'bin/rust/std/lib.rsspec' in old_specs,
         'component-23 changed effective Rust specifications')
    frozen=read(args.evidence.parents[1]/'frozen-profile.json')
    need(old_specs['bin/rust/std/lib.rsspec']==
         frozen['hosted_profile_hashes']['bin/rust/std/lib.rsspec'],
         'component-23 effective std lib.rsspec differs from frozen profile')
    need(production['proof_std_sha256']==profile_now['proof_std_sha256'] and
         all(value==production['critical_source_sha256'][name]
             for name,value in profile_now['critical_source_sha256'].items()
             if name!=str(TRANSLATOR)) and
         all(value==production['modified_tracked_source_sha256'][name]
             for name,value in profile_now['modified_tracked_source_sha256'].items()
             if name!=str(TRANSLATOR)) and
         all(value==production['binary_sha256'][name]
             for name,value in profile_now['binary_sha256'].items()
             if name!='bin/verifast'),
         'component-23 changed additional tracked source, binary, or proof std')
    return {'production_diff_sha256':hashlib.sha256(before).hexdigest(),
            'profile_diff_sha256':hashlib.sha256(after).hexdigest(),
            'production_console_sha256':sha(prod/'bin/verifast'),
            'profile_console_sha256':sha(new/'bin/verifast'),
            'production_translator_sha256':sha(prod/TRANSLATOR),
            'profile_translator_sha256':sha(new/TRANSLATOR),
            'modified_tracked_source_sha256':{name:sha(prod/name) for name in old_names
                                              if name!=str(TRANSLATOR)},
            'effective_rsspec_sha256':old_specs,
            'production_snapshot':production,
            'profile_snapshot':profile_now,
            'stock_binaries_unchanged':True,'kernel_schema_parser_unchanged':True,
            'all_other_tracked_sources_and_rsspec_unchanged':True}


def check_capture(args, m):
    root=args.evidence.parents[1]
    canonical=read(root/'cases/candidate/capture/summary.json')
    current=read(args.evidence/'capture/summary.json')
    s=current['source']; expected=m['source']
    case=args.evidence/'capture/nine-body-wrapper-rebase'
    need(current['frontend_refinement_and_full_body_capture'] is True and
         current['source_mode']=='wrapper-rebase-source-only' and
         s['verified_sha256']==expected['verified_sha256']==sha(case/'verified/lib.rs') and
         s['original_sha256']==expected['original_sha256']==sha(case/'original/lib.rs') and
         s['ghost_strip_identity'] is True and s['actual_runtime_unchanged'] is True and
         s['verified_source_reversible_two_insertions'] is True,
         'wrapper rebase source/MIR/refinement pair differs')
    guard=current['guard_capture']
    stages=guard['stages']
    need(guard['frontend_refinement'] is True and
         all(stages[k]['exit']==0 and stages[k]['source_unchanged'] is True
             for k in ('normal-export','normal-decode','readonly-export',
                       'readonly-decode','refinement')),
         'wrapper rebase normal/readonly/refinement incomplete')
    expected_hashes={'unit':expected['unit_sha256'],
                     **{f'body-{i}':v for i,v in enumerate(expected['body_sha256'])}}
    old=canonical['fingerprint']['snapshots']
    now=current['fingerprint']['snapshots']
    need(current['fingerprint']['classification']=='INTENDED_DIAGNOSTIC_REFUSAL_NO_PROOF_RULE' and
         current['fingerprint']['all_ten_snapshots'] is True and
         set(now)==set(expected_hashes)==set(old), 'ten source snapshots missing')
    for label,digest in expected_hashes.items():
        row=now[label]
        p=case/row['file']
        need(row['file']==f'actual-nested-9-{label}.marshal' and
             row['bytes']>0 and p.stat().st_size==row['bytes'] and
             sha(p)==row['sha256']==digest, f'{label} snapshot differs')
        need((digest!=old[label]['sha256']) if label in ('unit','body-7') else
             (digest==old[label]['sha256']), f'{label} same-build delta differs')
    normal=(case/'normal-mir.txt').read_text()
    normal_shape=outer_shape(normal,args.proof_root)
    need(normal_shape==TYPED_OUTER,
         'wrapper rebase NORMAL typed outer MIR graph differs')
    return {'classification':'WRAPPER_REBASE_CAPTURE_PINNED',
            'source_sha256':s['verified_sha256'], 'original_sha256':s['original_sha256'],
            'unit_sha256':expected_hashes['unit'],
            'body7_sha256':expected_hashes['body-7'],
            'ten_snapshots_independently_hashed':True,
            'eight_canonical_bodies_unchanged':True,
            'normal_readonly_refinement_complete':True,
            'typed_outer_mir_exact':True,
            'verification_accepted':False}


def outer_parts(decoded,proof):
    mut=load(proof/ROOT/'overnight-helper/capture-actual-owner-mir-mutation.py',
             'o26_wrapper_outer_shape')
    start,end,body=mut.selected_body(decoded,'select_unpredictable')
    loc_start=body.index('localDecls = [')
    blocks_start=body.index('basicBlocks = [',loc_start)
    blocks_end=body.index('\n      span = (',blocks_start)
    locals_section=body[loc_start:blocks_start]
    blocks=body[blocks_start:blocks_end]
    names=set(re.findall(r'name = "(_\d+)"',locals_section))
    ids=[int(v) for v in re.findall(r'\( id = \(index = (\d+)\),',blocks)]
    need(names=={f'_{n}' for n in range(TYPED_OUTER['local_count'])} and
         ids==list(range(TYPED_OUTER['block_count'])),
         'outer local/block count or ordering differs')
    return mut,start,end,body,blocks_start,blocks_end,blocks


def selected_call(decoded,proof,kind):
    mut,start,end,body,lo,hi,blocks=outer_parts(decoded,proof)
    site=TYPED_OUTER[kind]
    marker=f'( id = (index = {site["block"]}),'
    need(blocks.count(marker)==1,f'{kind} block index differs')
    at=blocks.index(marker)
    block=mut.PREP.LINK.CONSTRUCTOR.mir_balanced_item(blocks,blocks.index('(',at))
    callee=('std::mem::forget' if kind=='forget' else
            'std::mem::MaybeUninit::<T>::assume_init')
    marker=f'name = "{callee}"'
    need(block.count(marker)==1,f'{kind} callee differs')
    callee_at=block.index(marker)
    call_at=block.rfind('call = (',0,callee_at)
    need(call_at>=0,f'{kind} call missing')
    call_at+=len('call = ')
    call=mut.PREP.LINK.CONSTRUCTOR.mir_balanced_item(block,call_at)
    arg_lo=call.index('args = [')
    arg_hi=call.index('destination = (',arg_lo)
    args=call[arg_lo:arg_hi]
    dest=call[arg_hi:]
    need(args.count('move = (')==1 and args.count('copy = (')==0 and
         args.count(f'local = (name = "{site["move_argument_local"]}")')==1 and
         f'local = (name = "{site["destination_local"]}")' in dest and
         f'target = (something = (index = {site["normal_block"]}))' in call and
         f'unwindAction = (cleanup = (index = {site["cleanup_block"]}))' in call,
         f'{kind} exact Move/destination/normal/unwind differs')
    return mut,start,end,body,lo,hi,blocks,at,block,call_at,call,arg_lo,arg_hi


def outer_shape(decoded,proof):
    mut,start,end,body,lo,hi,blocks=outer_parts(decoded,proof)
    save=TYPED_OUTER['save_old_ghost_calls']
    rebase=TYPED_OUTER['rebase_both_ghost_calls']
    need(len(save)==2 and len(rebase)==8 and
         [site['block'] for site in save]==[4,5] and
         [site['block'] for site in rebase]==list(range(21,29)) and
         save[-1]['normal_block']<TYPED_OUTER['forget']['block']<rebase[0]['block'] and
         rebase[-1]['normal_block']<TYPED_OUTER['assume_init']['block'],
         'R2 ghost-call cardinality or order differs')
    for group,sites in (('SAVE_OLD',save),('REBASE_BOTH',rebase)):
        for site in sites:
            marker=f'( id = (index = {site["block"]}),'
            need(blocks.count(marker)==1,f'{group} block index not unique')
            at=blocks.index(marker)
            block=mut.PREP.LINK.CONSTRUCTOR.mir_balanced_item(blocks,blocks.index('(',at))
            need(block.count('name = "VeriFast_ghost_command"')==1 and
                 'args = []' in block and
                 f'local = (name = "{site["destination_local"]}")' in block and
                 f'target = (something = (index = {site["normal_block"]}))' in block,
                 f'{group} ghost call/destination/normal edge differs')
            if group=='REBASE_BOTH':
                need(f'unwindAction = (cleanup = (index = {site["cleanup_block"]}))' in block,
                     'REBASE_BOTH cleanup edge differs')
            else:
                need(site['unwind']=='Continue' and
                     'unwindAction = (continue = void)' in block,
                     'SAVE_OLD continue edge differs')
    need(blocks.count('unwindAction = (cleanup = (index = 34))')==
         TYPED_OUTER['shared_cleanup_predecessor_count'],
         'R2 shared cleanup predecessor count differs')
    for kind in ('forget','assume_init'):
        selected_call(decoded,proof,kind)
    need(f'local = (name = "{TYPED_OUTER["pointer_drop_receiver_local"]}")' in body,
         'pointer-drop receiver local absent')
    chain=TYPED_OUTER['unwind_chain']
    records={}
    for key in ('resume_block','drop_block','switch_block'):
        marker=f'( id = (index = {chain[key]}),'
        need(blocks.count(marker)==1,f'unwind {key} absent')
        at=blocks.index(marker)
        records[key]=mut.PREP.LINK.CONSTRUCTOR.mir_balanced_item(blocks,blocks.index('(',at))
    need('unwindResume = void' in records['resume_block'] and
         f'local = (name = "{TYPED_OUTER["forget"]["guard_source_local"]}")' in records['drop_block'] and
         f'target = (index = {chain["resume_block"]})' in records['drop_block'] and
         f'local = (name = "{chain["switch_local"]}")' in records['switch_block'] and
         f'targets = [(index = {chain["switch_targets"][0]}), (index = {chain["switch_targets"][1]})]' in records['switch_block'],
         'typed unwind switch/drop/resume chain differs')
    return TYPED_OUTER


def mutate_outer_mir(decoded,mutation,proof):
    kind='assume_init' if mutation=='outer_assume_init_move_to_copy' else 'forget'
    need(mutation in ('outer_assume_init_move_to_copy','forget_move_to_copy',
                      'forget_cleanup_to_wrong_block'),'unknown wrapper MIR mutation')
    (mut,start,end,body,lo,hi,blocks,at,block,call_at,call,
     arg_lo,arg_hi)=selected_call(decoded,proof,kind)
    if mutation.endswith('move_to_copy'):
        prior=call[arg_lo:arg_hi]
        changed=prior.replace('move = (','copy = (',1)
        need(changed.replace('copy = (','move = (',1)==prior,
             'Move/Copy delta not exactly reversible')
        next_call=call[:arg_lo]+changed+call[arg_hi:]
    else:
        old=f'unwindAction = (cleanup = (index = {TYPED_OUTER["forget"]["cleanup_block"]}))'
        new=f'unwindAction = (cleanup = (index = {TYPED_OUTER["forget"]["negative_cleanup_block"]}))'
        need(call.count(old)==1,'forget cleanup edge not unique')
        next_call=call.replace(old,new,1)
        need(next_call.replace(new,old,1)==call,'forget cleanup delta not reversible')
    next_block=block[:call_at]+next_call+block[call_at+len(call):]
    next_blocks=blocks[:at]+next_block+blocks[at+len(block):]
    next_body=body[:lo]+next_blocks+body[hi:]
    result=decoded[:start]+next_body+decoded[end:]
    need(result!=decoded,'wrapper MIR mutation had no effect')
    return result


def proof_stage(args, case, tool, name, label, admitted):
    recipe=load(args.cloud_dir/'o26-recipe.py',f'o26_wrapper_profile_{label}')
    need(not any(os.environ.get(k) for k in PAIR),
         'inherited component-23 opt-in forbidden')
    if admitted:
        os.environ[PAIR[0]]=str(args.proof_root)
        os.environ[PAIR[1]]='1'
    try:
        return recipe.proof_stage(args.proof_root,case,tool,args.schema,
                                  args.compiler_sysroot,args.deadline_epoch,name,label)
    finally:
        for key in PAIR: os.environ.pop(key,None)


def run_proofs(args, m):
    case=args.evidence/'capture/nine-body-wrapper-rebase'
    need(read(args.evidence/'capture-check.json')['classification']=='WRAPPER_REBASE_CAPTURE_PINNED',
         'pinned capture required before proof')
    positive=proof_stage(args,case,args.profile_source,'profile-proof','profile_positive',True)
    write(args.evidence/'profile-proof-stage.json',positive)
    canonical=args.evidence.parents[1]/'cases/candidate/capture/nine-body-a1-owned-forget'
    off_canonical=proof_stage(args,canonical,args.profile_source,
                              'profile-off-canonical','profile_off_canonical',False)
    write(args.evidence/'profile-off-canonical-stage.json',off_canonical)
    off_rebase=proof_stage(args,case,args.profile_source,
                           'profile-off-rebase','profile_off_rebase',False)
    write(args.evidence/'profile-off-rebase-stage.json',off_rebase)
    return {'profile':positive,'profile_off_canonical':off_canonical,
            'profile_off_rebase':off_rebase}


def owner_controls(args,m):
    source=m['source']['verified_sha256']
    root=args.evidence/'owner17-controls'
    need(not root.exists(),'owner controls evidence exists')
    root.mkdir()
    cap=load(args.proof_root/ROOT/'overnight-assume-actual/capture.py','o26_wrapper_owner_capture')
    prep=load(args.proof_root/ROOT/'overnight-assume-actual/prepare-wrapper-rebase.py','o26_wrapper_owner_prepare')
    mut=load(args.proof_root/ROOT/'overnight-helper/capture-actual-owner-mir-mutation.py',
             'o26_wrapper_owner_shadow')
    rows=[]
    for variant in VARIANTS:
        out=root/variant
        selected=prep.write_case(args.proof_root,out)
        case=out/prep.CASE_NAME
        verified=case/'verified/lib.rs';original=case/'original/lib.rs'
        need(selected['verified_sha256']==source==sha(verified) and
             selected['original_sha256']==ORIGINAL==sha(original),
             f'{variant} fresh source differs')
        if variant.startswith('source_'):
            before,after={
              'source_owner':(b'*g.inner |-> ?payload &*& <T>.own(t, payload);',
                              b'*g.inner |-> ?payload &*& <T>.own(t, payload) &*& true;'),
              'source_outcome':(b'fn_outcome_result(outcome)',
                                b'fn_outcome_result( outcome)'),
            }[variant]
            data=verified.read_bytes()
            need(data.count(before)==1,f'{variant} mutation anchor differs')
            verified.write_bytes(data.replace(before,after,1))
            need(prep.BASE.SEVEN.OWNER.OWNER.strip_ghost(verified.read_bytes())==
                 original.read_bytes(),f'{variant} runtime source changed')
            selected['verified_sha256']=sha(verified)
        stage_args=SimpleNamespace(tool_home=args.profile_source,schema=args.schema,
            compiler_sysroot=str(args.compiler_sysroot),deadline_epoch=args.deadline_epoch,
            first_barrier=False,fingerprint_probe=False)
        cap.clear_semantic_opt_ins()
        support=cap.GUARD.capture_case(case,selected,stage_args)
        stages=support['stages']
        paired=(support['frontend_refinement'] is True and support['source_unchanged'] is True and
                all(stages[k]['exit']==0 and stages[k]['source_unchanged'] is True
                    for k in ('normal-export','normal-decode','readonly-export',
                              'readonly-decode','refinement')))
        need(paired,f'{variant} source pair/refinement incomplete')
        tool=args.profile_source
        if not variant.startswith('source_'):
            tool=mut.make_shadow(tool,args.schema,case,variant,source)
            wrapper=tool/'bin/vf-rust-mir-exporter'
            previous=repr(str(mut.HERE/'capture-actual-owner-mir-mutation.py'))
            text=wrapper.read_text()
            need(text.count(previous)==1,f'{variant} shadow import anchor differs')
            text=text.replace(previous,repr(str(Path(__file__).resolve())),1)
            wrapper.write_text(text)
            (case/'mir-exporter-wrapper.py').write_text(text)
            p=read(case/'mutation-profile.json')
            p['wrapper_sha256']=sha(wrapper)
            write(case/'mutation-profile.json',p)
        result=proof_stage(args,case,tool,'owner-control',variant,True)
        log=(case/'owner-control.log').read_text(errors='replace')
        fatal=[x for x in log.splitlines() if x.startswith('Fatal error:')]
        expected=('owner exact verified source SHA256' if variant.startswith('source_')
                  else 'owner complete decoded unit SHA256')
        wrapper_record=None
        if not variant.startswith('source_'):
            wrapper_record=read(case/'mutation-record.json')
            profile_record=read(case/'mutation-profile.json')
            need(wrapper_record['matched'] is True and
                 wrapper_record['selected_source_sha256']==source and
                 wrapper_record['mutation']==variant and
                 all(wrapper_record[k]==0 for k in ('exporter_exit','decode_exit','encode_exit')) and
                 wrapper_record['canonical_sha256']==sha(case/'canonical-mir.bin')==sha(case/'normal-mir.bin') and
                 wrapper_record['mutated_sha256']==sha(case/'mutated-mir.bin') and
                 profile_record['wrapper_sha256']==sha(case/'mir-exporter-wrapper.py')==sha(tool/'bin/vf-rust-mir-exporter') and
                 profile_record['base_console_sha256']==profile_record['shadow_console_sha256'] and
                 mutate_outer_mir((case/'canonical-mir.txt').read_text(),variant,args.proof_root)==
                     (case/'mutated-mir.txt').read_text(),
                 f'{variant} shadow identity or MIR delta differs')
        exact=(result.get('status')=='RAN' and result.get('exit')==2 and
               result.get('source_unchanged') is True and
               result.get('source_before')==result.get('source_after') and
               result.get('intrinsic_gate_active') is True and
               result.get('pointer_drop_gate_active') is True and
               fatal==['Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: '+expected+'")'] and
               not cap.LINK.LINK.ERR.findall(log) and OWNER not in log and A1 not in log and
               "Verifying function '" not in log)
        row={'variant':variant,'intended_component17_refusal':exact,
             'proof_stage':result,'fatal':fatal,'mutation_record':wrapper_record,
             'source_sha256':selected['verified_sha256'],'verification_accepted':False}
        write(case/'control-summary.json',row)
        rows.append(row)
    complete=all(row['intended_component17_refusal'] for row in rows)
    report={'classification':'COMPONENT17_REBASE_CONTROLS_COMPLETE' if complete else 'INCONCLUSIVE',
            'diagnostic_complete':complete,'verification_accepted':False,
            'negative_cases':rows,'source_sha256':source}
    write(root/'summary.json',report)
    need(complete,'component-17 rebase controls incomplete')
    return report


def mutate_actual_mir(decoded,mutation):
    root=os.environ.get('SORT4_ACTUAL_OWNER_REPO_ROOT')
    need(root is not None,'owner mutation proof root absent')
    return mutate_outer_mir(decoded,mutation,Path(root))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=('preflight','production-snapshot','tool-identity','capture-check',
                                   'proofs','owner-controls','final-identity'))
    for key in ('proof-root','cloud-dir','production-source','profile-source',
                'production-patch','stock-home','compiler-sysroot','evidence'):
        p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--deadline-epoch',type=int,required=True)
    a=p.parse_args()
    need(os.environ.get('SMALLSORT_EXECUTION_PROVIDER')=='cloud-build' and
         not os.environ.get('GITHUB_ACTIONS'),'Cloud Build required')
    m=profile(a.proof_root)
    a.schema=a.profile_source/'src/rust_frontend/vf_mir/vf_mir.capnp'
    if a.mode=='preflight':
        write(a.evidence/'profile-manifest.json',m)
    elif a.mode=='production-snapshot':
        need(sha(a.production_source/TRANSLATOR)==PRODUCTION_TRANSLATOR,
             'pre-copy production translator differs')
        diff=subprocess.check_output(('git','-C',str(a.production_source),
                                      'diff','--binary','HEAD'))
        need(diff==a.production_patch.read_bytes(),
             'pre-copy production applied patch differs')
        baseline=tool_snapshot(a.production_source,a.proof_root)
        need(baseline['head']=='f76012fb518703b1d98e243ac4f487f16877cfcb' and
             'bin/rust/std/lib.rsspec' in baseline['effective_rsspec_sha256'],
             'pre-copy frozen profile missing')
        write(a.evidence/'production-tool-baseline.json',baseline)
    elif a.mode=='tool-identity':
        write(a.evidence/'tool-identity.json',tool_identity(a,m))
    elif a.mode=='final-identity':
        current=tool_identity(a,m)
        need(current==read(a.evidence/'tool-identity.json'),
             'production/profile tools or specs changed during proof/controls')
        write(a.evidence/'tool-identity-after.json',current)
    elif a.mode=='capture-check':
        write(a.evidence/'capture-check.json',check_capture(a,m))
    elif a.mode=='proofs':
        run_proofs(a,m)
    else:
        owner_controls(a,m)


if __name__=='__main__':
    main()
