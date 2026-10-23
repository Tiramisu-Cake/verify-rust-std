#!/usr/bin/env python3
"""Exact positive-only R24 mutable proof transport and conservative source audit."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import uuid

MODE_REL=Path('research/challenge-8/task-history/select-callee-r24/P2-MUT-PROOF-MODE.json')
MODE_SHA='bcbe8f080fd29cc3fc2c9282a92d6e54202c526de7d187d57ab47f822489046e'
LIB_SHA='8a481421396de618e50f8a6b7a408ffd9f048fd94397e647c3002e1489723d0c'
R24='SORT4-ACTUAL-SELECT-2026-10-24-R24'
R21='SORT4-ACTUAL-SELECT-2026-10-23-R21'

def need(ok, why):
    if not ok:raise RuntimeError('R24-MUT-PROOF-ENTRY: '+why)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def load_library(cloud):
    path=cloud/'select-callee-r24-mut-proof.py'
    need(path.is_file() and not path.is_symlink() and digest(path)==LIB_SHA,'proof library hash')
    spec=importlib.util.spec_from_file_location('r24_mut_proof_library',path)
    need(spec is not None and spec.loader is not None,'proof library loader')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    need(digest(path)==LIB_SHA,'proof library changed during import')
    return module

def mode(repo, file, lib):
    need(file.resolve()==(repo/MODE_REL).resolve() and file.is_file() and not file.is_symlink() and
         digest(file)==MODE_SHA,'exact positive-proof mode path/hash')
    value=json.loads(file.read_text())
    need(isinstance(value,dict) and value.get('schema')=='select-r24-mut-proof-mode-v1' and
         value.get('enabled') is True and value.get('proof_mode')=='positive' and
         value.get('proof_variants')==['positive'] and value.get('const_regression')=='FULL8_REQUIRED_SAME_TOOL' and
         value.get('phase_id')==os.environ.get(lib.R24_PHASE_ENV)==R24 and
         value.get('route_phase_id')==os.environ.get(lib.R21_PHASE_ENV)==R21 and
         value.get('owner')=='select-sort4' and value.get('lane')==lib.LANE and
         value.get('profile')==lib.PROFILE and value.get('pins_file')==lib.PINS_REL.as_posix() and
         value.get('pins_sha256')==lib.PINS_SHA256 and value.get('accepted') is False and
         value.get('publication_allowed') is False and type(value.get('independent_proof_credit')) is int and
         value['independent_proof_credit']==0,'positive-proof mode bounds')
    return value

def audit_record(summary, const_audit, exit_code, failed, env, lib, pins):
    errors=[]
    try:
        native=str(uuid.UUID(env.get('CLOUD_BUILD_ID','')))
    except (ValueError,TypeError,AttributeError):native=None
    if native is None or native!=env.get('CLOUD_BUILD_ID'):errors.append('current native UUID missing')
    try:lib._validate_route(env,native,Path('/workspace/proof'))
    except (ValueError,RuntimeError):errors.append('audit route context differs')
    if exit_code!=0:errors.append('runner failed')
    if not isinstance(const_audit,dict) or const_audit.get('evidence_complete') is not True:
        errors.append('same-tool full const regression audit incomplete')
    if not isinstance(summary,dict):errors.append('mutable proof summary missing/wrong type')
    else:
        if (summary.get('schema')!=lib.SCHEMA or summary.get('complete') is not True or
            summary.get('proof_mode')!='positive' or summary.get('proof_variants')!=['positive'] or
            summary.get('native_build_id')!=native or summary.get('candidate')!=env.get('PROOF_SHA') or
            not isinstance(env.get('PROOF_SHA'),str) or re.fullmatch('[0-9a-f]{40}',env['PROOF_SHA']) is None or
            summary.get('body_proof_run') is not True or summary.get('provider')!='cloud-build' or
            summary.get('lane')!=lib.LANE or summary.get('profile')!=lib.PROFILE or
            summary.get('r24_session_phase_id')!=R24 or summary.get('r21_route_phase_id')!=R21 or
            summary.get('pins')!={'path':lib.PINS_REL.as_posix(),'sha256':lib.PINS_SHA256}):
            errors.append('mutable proof summary identity/completeness differs')
        if any(summary.get(k) is not False for k in ('accepted','publication_allowed')) or type(summary.get('proof_credit')) is not int or summary.get('proof_credit')!=0:
            errors.append('unearned acceptance/publication/credit')
        captured=summary.get('complete_source_observation')
        errors+=lib._validate_capture(captured,pins,native)
        provider=captured.get('provider_record') if isinstance(captured,dict) else None
        if (not isinstance(provider,dict) or provider.get('provider')!='cloud-build' or
            provider.get('build_id')!=native or provider.get('project')!='smallsort-ci' or
            provider.get('region')!='global' or provider.get('os')!='ubuntu-22.04' or
            provider.get('arch')!='x86_64'):
            errors.append('capture native provider binding differs')
        rows=summary.get('rows')
        if not isinstance(rows,dict) or set(rows)!={'positive'}:errors.append('positive row inventory differs')
        else:
            row=rows['positive'];stage=row.get('proof_stage') if isinstance(row,dict) else None
            pair={'original/lib.rs':pins['source']['original_sha256'],
                  'verified/lib.rs':pins['source']['verified_sha256']}
            if (not isinstance(row,dict) or row.get('variant')!='positive' or
                row.get('stage_name')!='r24-mut-proof-positive' or
                row.get('classification')!='POSITIVE_PROOF_STAGE_RAN_SOURCE_INTACT' or
                row.get('source_intact') is not True or row.get('source_before')!=pair or
                row.get('source_after')!=pair or row.get('errors')!=[] or row.get('native_marker_seen')!=1 or
                not isinstance(stage,dict) or stage.get('status')!='RAN' or
                type(stage.get('exit')) is not int or stage['exit']!=0 or stage.get('source_unchanged') is not True or
                stage.get('source_before')!=pair or stage.get('source_after')!=pair or
                stage.get('intrinsic_gate_active') is not False or stage.get('pointer_drop_gate_active') is not False):
                errors.append('positive ordinary stage/source/native marker differs')
    return {'schema':'select-r24-mut-proof-audit-v1','scope':'POSITIVE_PROOF_STAGE_SOURCE_REPORTED_NO_ACCEPTANCE',
            'runner_exit':exit_code,'failed_stage':failed,'evidence_complete':not errors,
            'errors':errors,'mutable_proof_summary':summary,'const_regression_audit':const_audit,
            'verification_accepted':False,'accepted':False,'publication_allowed':False,'proof_credit':0}

def read_optional(path):
    try:return json.loads(path.read_text())
    except (OSError,ValueError):return None

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['run','audit'])
    for name in ['repo','cloud-dir','evidence','proof-mode-file']:parser.add_argument('--'+name,type=Path,required=True)
    for name in ['tool-home','schema','compiler-sysroot','mode-file','matrix-mode-file','output']:parser.add_argument('--'+name,type=Path)
    for name in ['mode-sha256','matrix-mode-sha256','candidate','failed-stage']:parser.add_argument('--'+name)
    for name in ['deadline-epoch','runner-exit']:parser.add_argument('--'+name,type=int)
    args=parser.parse_args();lib=load_library(args.cloud_dir);mode(args.repo,args.proof_mode_file,lib)
    if args.action=='run':
        need(all(getattr(args,n) is not None for n in ['tool_home','schema','compiler_sysroot','mode_file','matrix_mode_file','deadline_epoch','mode_sha256','matrix_mode_sha256','candidate']),'complete run arguments')
        need(args.candidate==os.environ.get('PROOF_SHA') and
             re.fullmatch('[0-9a-f]{40}',args.candidate) is not None,'exact committed proof candidate')
        args.proof_mode='positive';args.proof_variants=['positive']
        result=lib.run(args)
        print(json.dumps({'complete':result['complete'],'classification':result['classification'],'accepted':False,'proof_credit':0}))
        if result['complete'] is not True:raise SystemExit(4)
    else:
        need(args.output is not None and args.runner_exit is not None,'complete audit arguments')
        result=audit_record(read_optional(args.evidence/lib.SUMMARY_REL),read_optional(args.evidence/'const-regression-audit.json'),args.runner_exit,args.failed_stage,dict(os.environ),lib,lib._load_pins(args.repo))
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
