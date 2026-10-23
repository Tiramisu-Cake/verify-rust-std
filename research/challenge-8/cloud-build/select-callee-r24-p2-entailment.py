#!/usr/bin/env python3
"""Cloud checked consequence from the mutable callee post to the planned P2 post."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import traceback

D_SHA='f0907ded785ed659309277a497d8425f882dbd492da2d6c3e81cdc4b1088cbf8'
MODEL_REL='bin/rust/rust_belt/general.rsspec'
MODEL_SHA='ef2ff16dffd472bbc5fd7fa17e7f13a03d83919520da5ce7e2d7095194790d1d'
SUMMARY_REL=Path('cases/r24-p2-entailment/P2-ENTAILMENT.json')
CONTRACT_SHA='dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870'
LEMMA=b'''#![allow(dead_code)]

/*@
lem select_p2_post_consequence<Element>(
    t: thread_id_t, condition: bool,
    true_val: *Element, false_val: *Element, result: *Element)
    req thread_token(t) &*& (result as pointer) ==
        (if condition { true_val as pointer } else { false_val as pointer }) &*&
        raw_ptr_own::<Element>()(t, result);
    ens thread_token(t) &*& (result as pointer) ==
        (if condition { true_val as pointer } else { false_val as pointer });
{
    open raw_ptr_own::<Element>()(t, result);
}
@*/

pub fn p2_consequence_anchor()
/*@
req thread_token(?t) &*& t == currentThread;
@*/
/*@
ens thread_token(t);
@*/
/*@
on_unwind_ens false;
@*/
{}
'''
NAMES=('normal-export','readonly-export','normal-decode','readonly-decode','refinement','p2-entailment-proof')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def need(ok,why):
    if not ok:raise RuntimeError('R24-P2-ENTAILMENT: '+why)
def require_compiler_sysroot(args):
    value=getattr(args,'compiler_sysroot',None)
    need(isinstance(value,str) and bool(value.strip()),'compiler sysroot is required for stage identity')
def load_diag(cloud):
    p=cloud/'select-callee-r24-mut-matrix-proof.py';need(p.is_file() and not p.is_symlink() and sha(p.read_bytes())==D_SHA,'frozen diagnostic library changed')
    spec=importlib.util.spec_from_file_location('r24_p2_consequence_diagnostic',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def commands_for(args):
    tool=Path(args.tool_home);exporter=str(tool/'bin/vf-rust-mir-exporter')
    return {
          'normal-export':([exporter,'verified/lib.rs',f'--sysroot={args.compiler_sysroot}','--edition','2021'],None,'normal-mir.bin'),
          'readonly-export':([exporter,'verified/lib.rs',f'--sysroot={args.compiler_sysroot}','--edition','2021','--crate-type','lib','--vf-rust-mir-exporter:preprocess-readonly'],None,'readonly-mir.bin'),
          'normal-decode':(['capnp','decode',str(args.schema),'VfMir'],'normal-mir.bin','normal-mir.txt'),
          'readonly-decode':(['capnp','decode',str(args.schema),'VfMir'],'readonly-mir.bin','readonly-mir.txt'),
          'refinement':([str(tool/'bin/refinement-checker'),'--rustc-args','--edition 2021','original/lib.rs','verified/lib.rs'],None,None),
          'p2-entailment-proof':([str(tool/'bin/verifast'),'-rustc_args','--edition 2021','-verbose','1','verified/lib.rs'],None,None)}

def validate_case(case,args,diag):
    # This literal fixture contains only non-nested annotation blocks. Remove
    # those blocks exactly and bind the saved runtime bytes to the checked lemma.
    for rel in ('original/lib.rs','verified/lib.rs',*(name+'-stage.json' for name in NAMES)):
        need(diag._regular_under(case,case/rel),'source/stage missing or symlinked: '+rel)
    original=(case/'original/lib.rs').read_bytes();verified=(case/'verified/lib.rs').read_bytes()
    need(verified==LEMMA,'lemma source changed')
    need(re.sub(rb'/\*@.*?@\*/',b'',verified,flags=re.S)==original,'lemma ghost-strip identity differs')
    source={rel:sha((case/rel).read_bytes()) for rel in ('original/lib.rs','verified/lib.rs')}
    stages={name:json.loads((case/(name+'-stage.json')).read_text()) for name in NAMES}
    commands=commands_for(args)
    for name,row in stages.items():
        need(isinstance(row,dict),'stage is not an object: '+name)
        need(row.get('timeout') is not True and row.get('timed_out') is not True,'stage timed out: '+name)
        argv,inp,out=commands[name]
        expected_out=out or name+'.log';expected_err=name+'-stderr.log' if out else expected_out
        need(row.get('argv')==argv and row.get('stdout')==expected_out and row.get('stderr')==expected_err,'stage command/outputs differ: '+name)
        need(diag._regular_under(case,case/expected_out) and diag._regular_under(case,case/expected_err),'stage physical outputs missing: '+name)
        need(isinstance(row,dict) and row.get('status')=='RAN' and type(row.get('exit')) is int and row['exit']==0 and row.get('source_before')==source and row.get('source_after')==source and row.get('source_unchanged') is True and row.get('intrinsic_gate_active') is False and row.get('pointer_drop_gate_active') is False,name+' missing/failed/source drift or semantic gates')
    name=NAMES[-1];proof=stages[name]
    argv=[str(Path(args.tool_home)/'bin/verifast'),'-rustc_args','--edition 2021','-verbose','1','verified/lib.rs']
    need(proof.get('argv')==argv and proof.get('stdout')==name+'.log' and proof.get('stderr')==name+'.log','proof argv/log target differs')
    raw=(case/(name+'.log')).read_bytes();log=raw.decode('utf-8',errors='strict')
    headers=re.findall(r"(?m)^\s*\d+(?:\.\d+)?s: verified/lib\.rs\([^)]*\): Verifying function 'select_p2_post_consequence'\s*$",log)
    need(len(headers)==1,'checked consequence lemma verification header absent/ambiguous')
    need(len(re.findall(r'(?m)^0 errors found \([1-9][0-9]* statements verified\)',log))==1,'successful verifier summary missing')
    need(not re.search(r'(?im)error:|fatal error|exception|verification failed|SORT4-R24-MUTABLE-CERTIFICATES:',log),'unexpected error or mutable admission marker')
    inv=[]
    for p in sorted(case.iterdir()):
        if p.is_file() and p.name!=SUMMARY_REL.name:need(not p.is_symlink(),'symlink artifact');inv.append({'path':p.name,'sha256':sha(p.read_bytes())})
    return {'source_hashes':source,'stages':stages,'lemma_headers':1,'proof_log_sha256':sha(raw),'artifact_inventory':inv}

def run(args,*,diag=None,stage=None):
    require_compiler_sysroot(args)
    diag=diag or load_diag(Path(args.cloud_dir));lib=diag.load_library(Path(args.cloud_dir))
    build=diag._validate_context(args,dict(os.environ),lib)
    diag.validate_mode(Path(args.repo),Path(args.matrix_proof_mode_file),lib)
    evidence=Path(args.evidence);tool=Path(args.tool_home)
    positive=diag._positive_evidence(Path(args.repo));before=diag._tool_hashes(tool,evidence/diag.PROFILE_REL,positive)
    model=tool/MODEL_REL;need(model.is_file() and not model.is_symlink() and sha(model.read_bytes())==MODEL_SHA,'raw-pointer model pin differs')
    modelraw=model.read_bytes();need(modelraw.count(b'pred_ctor raw_ptr_own<T>()(t: thread_id_t, v: *T;) = true;')==1 and modelraw.count(b'type_pred_def for <T> <*T>.own = raw_ptr_own::<T>;')==1,'raw-pointer model definitions differ')
    case=evidence/SUMMARY_REL.parent;need(not case.exists(),'fresh consequence output required');(case/'original').mkdir(parents=True);(case/'verified').mkdir()
    original=re.sub(rb'/\*@.*?@\*/',b'',LEMMA,flags=re.S)
    (case/'original/lib.rs').write_bytes(original);(case/'verified/lib.rs').write_bytes(LEMMA)
    report={'schema':'select-r24-p2-checked-consequence-v1','complete':False,'candidate':args.candidate,'native_build_id':build,'contract_text_sha256':CONTRACT_SHA,'scope':'NORMAL_POST_ENTAILMENT_ONLY; NO_CALLEE_BODY_REPLACEMENT; FALSE_UNWIND_INHERITED_FROM_CALLEE','model':{'path':MODEL_REL,'sha256':MODEL_SHA},'tool_hashes':before,'accepted':False,'publication_allowed':False,'proof_credit':0,'errors':[]}
    def save():diag.write_json(evidence/SUMMARY_REL,report)
    try:
        if stage is None:
            adapter=Path(args.cloud_dir)/'select-callee-r24-mut-capture.py'
            need(adapter.is_file() and not adapter.is_symlink() and sha(adapter.read_bytes())=='96e770129d1fc08e798e4b3ce8ad3bfe5b7ba01b68dafd0e6dfa3e0c8957f756','capture adapter pin differs')
            spec=importlib.util.spec_from_file_location('r24_p2_capture_adapter',adapter);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
            stage=old.load_capture_runtime(Path(args.repo),Path(args.cloud_dir),evidence)['capture'].LINK.stage
        commands=commands_for(args)
        for name in NAMES:
            argv,inp,out=commands[name];row=stage(case,name,argv,args,input_name=inp,output_name=out,gates=False,pointer_drop=False,cap_seconds=1200)
            need(isinstance(row,dict) and row.get('status')=='RAN' and type(row.get('exit')) is int and row['exit']==0,name+' not successful')
        report['observation']=validate_case(case,args,diag)
        need(before==diag._tool_hashes(tool,evidence/diag.PROFILE_REL,positive) and sha(model.read_bytes())==MODEL_SHA,'tool/model changed during consequence proof')
        report['complete']=True;save();return report
    except BaseException as exc:
        report['errors'].append(type(exc).__name__+': '+str(exc));report['exception']={'type':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}
        try:save()
        except BaseException as other:
            if hasattr(exc,'add_note'):exc.add_note('consequence snapshot failed: '+str(other))
        raise

def audit(args,*,diag=None):
    diag=diag or load_diag(Path(args.cloud_dir));errors=[];report=None
    try:
        require_compiler_sysroot(args)
        lib=diag.load_library(Path(args.cloud_dir));build=diag._validate_context(args,dict(os.environ),lib)
        diag.validate_mode(Path(args.repo),Path(args.matrix_proof_mode_file),lib)
        evidence=Path(args.evidence);tool=Path(args.tool_home)
        need(diag._regular_under(evidence,evidence/SUMMARY_REL),'consequence summary missing/symlinked')
        report=json.loads((evidence/SUMMARY_REL).read_text())
        need(isinstance(report,dict) and report.get('schema')=='select-r24-p2-checked-consequence-v1' and report.get('complete') is True and report.get('candidate')==args.candidate and report.get('native_build_id')==build and report.get('contract_text_sha256')==CONTRACT_SHA and report.get('errors')==[] and report.get('accepted') is False and report.get('publication_allowed') is False and type(report.get('proof_credit')) is int and report['proof_credit']==0,'consequence identity/completeness/boundaries differ')
        need(report.get('observation')==validate_case(evidence/SUMMARY_REL.parent,args,diag),'consequence physical evidence changed')
        positive=diag._positive_evidence(Path(args.repo));need(report.get('tool_hashes')==diag._tool_hashes(tool,evidence/diag.PROFILE_REL,positive),'consequence tool/profile changed')
        model=tool/MODEL_REL;need(diag._regular_under(tool,model) and sha(model.read_bytes())==MODEL_SHA and report.get('model')=={'path':MODEL_REL,'sha256':MODEL_SHA},'consequence model changed')
        need(args.runner_exit==0 and args.failed_stage=='complete','consequence runner did not complete')
    except BaseException as exc:errors.append(type(exc).__name__+': '+str(exc))
    result={'schema':'select-r24-p2-consequence-audit-v1','evidence_complete':not errors,'errors':errors,'consequence_summary':report,'accepted':False,'publication_allowed':False,'proof_credit':0}
    diag.write_json(Path(args.output),result);return result

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('run','audit'))
    for name in ('repo','cloud-dir','evidence','tool-home','schema','matrix-proof-mode-file'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--compiler-sysroot');p.add_argument('--deadline-epoch',type=int);p.add_argument('--candidate',required=True)
    p.add_argument('--output',type=Path);p.add_argument('--runner-exit',type=int);p.add_argument('--failed-stage')
    args=p.parse_args()
    if args.action=='run':
        need(args.deadline_epoch is not None,'run arguments incomplete');require_compiler_sysroot(args);run(args)
    else:
        need(args.output is not None and args.runner_exit is not None and args.failed_stage is not None,'audit arguments incomplete')
        if audit(args)['evidence_complete'] is not True:raise SystemExit(4)
if __name__=='__main__':main()
