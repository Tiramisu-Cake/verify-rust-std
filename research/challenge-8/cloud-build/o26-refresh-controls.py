#!/usr/bin/env python3
"""Cloud-only component-17 negatives on the exact refreshed nine-body source.

The canonical positive case is the already captured/proved O26 refresh case.
The four negatives use separate source pairs and unmodified production exporter,
except for a TEST-only shadow exporter wrapper in the two typed-MIR mutants.
No component-20 A1 negative or proof acceptance is inferred from an owner refusal.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace
import sys

SOURCE='1798132ff7a1585db7367779365c88e5ef5f417adcff0bf82779bf6a674945e6'
ORIGINAL='466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5'
ADMISSION='SORT4-ACTUAL-OWNER-NINE: exact source and complete decoded MIR admission only'
A1_ADMISSION='SORT4-A1-NINE: exact source, typed local pair and outer cleanup call admitted'
VARIANTS=('source_owner','source_outcome','forget_move_to_copy','forget_cleanup_to_bb23')
FATAL_PREFIX='Fatal error: exception Failure("SORT4-SELECT-INTRINSIC: certificate mismatch: '

def load(path:Path,name:str):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise ValueError(f'missing module {path}')
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def digest(path:Path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path:Path,data:dict):path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')

def canonical(ev:Path):
    root=ev/'cases/candidate'
    cap=json.loads((root/'capture/summary.json').read_text())
    compare=json.loads((root/'capture-compare.json').read_text())
    proof=json.loads((root/'proof-stage.json').read_text())
    case=root/'capture/nine-body-a1-owned-forget'
    stage=proof['stage']
    source_ok=(compare['capture_complete'] is True and
       cap['frontend_refinement_and_full_body_capture'] is True and
       cap['source']['verified_sha256']==SOURCE and
       cap['source']['original_sha256']==ORIGINAL and
       digest(case/'verified/lib.rs')==SOURCE and digest(case/'original/lib.rs')==ORIGINAL)
    log=case/'refreshed-proof.log'
    text=log.read_text(errors='replace') if log.is_file() else ''
    admitted=ADMISSION in text and A1_ADMISSION in text
    proof_ran=(stage.get('status')=='RAN' and stage.get('exit') not in (None,124,137) and
       stage.get('source_unchanged') is True and
       stage.get('source_before')==stage.get('source_after') and
       stage.get('intrinsic_gate_active') is True and
       stage.get('pointer_drop_gate_active') is True and log.is_file())
    positive=source_ok and proof_ran and admitted
    return {'classification':'POSITIVE_ADMISSION_PROOF_DIAGNOSTIC' if positive else 'INCONCLUSIVE',
      'canonical_source_pair_and_refinement':source_ok,'full_six_gate_stage_ran':proof_ran,
      'owner_and_a1_admission_visible':admitted,'proof_exit':stage.get('exit'),
      'positive_verifier_exit_zero':positive and stage.get('exit')==0,
      'whole_helper_proved':False,
      'test_tool_mutation_profile':False,'a1_negative':False}

def mutate_actual_mir(decoded:str,mutation:str)->str:
    # Called by the disposable exporter wrapper. The historical mutator itself
    # is unchanged; its typed field assertions still reject shape drift.
    global CHECK
    if 'CHECK' not in globals():
        root=os.environ.get('SORT4_ACTUAL_OWNER_REPO_ROOT')
        if not root: raise ValueError('missing exact owner root for TEST wrapper')
        CHECK=load(Path(root)/'research/challenge-8/overnight-assume-actual/check-owner-nine.py',
                   'o26_refresh_wrapper_owner_controls')
    return CHECK.mutate_actual_mir(decoded,mutation)

def mutation_exact(case:Path,variant:str):
    paths={n:case/n for n in ('mutation-record.json','mutation-profile.json',
      'canonical-mir.txt','mutated-mir.txt','canonical-mir.bin','mutated-mir.bin',
      'mir-exporter-wrapper.py','normal-mir.bin')}
    paths['active-wrapper']=case/'mutation-profile/bin/vf-rust-mir-exporter'
    if not all(p.is_file() for p in paths.values()):return False,None
    record=json.loads(paths['mutation-record.json'].read_text())
    profile=json.loads(paths['mutation-profile.json'].read_text())
    try: changed=mutate_actual_mir(paths['canonical-mir.txt'].read_text(),variant)
    except (ValueError,IndexError):return False,record
    exact=(changed==paths['mutated-mir.txt'].read_text() and
       record.get('matched') is True and record.get('mutation')==variant and
       all(record.get(k)==0 for k in ('exporter_exit','decode_exit','encode_exit')) and
       record.get('selected_source_sha256')==SOURCE and
       record.get('canonical_sha256')==digest(paths['canonical-mir.bin']) and
       record.get('canonical_sha256')==digest(paths['normal-mir.bin']) and
       record.get('mutated_sha256')==digest(paths['mutated-mir.bin']) and
       paths['canonical-mir.bin'].read_bytes()!=paths['mutated-mir.bin'].read_bytes() and
       record.get('real_exporter_sha256')==profile.get('real_exporter_sha256') and
       profile.get('base_console_sha256')==profile.get('shadow_console_sha256') and
       profile.get('wrapper_sha256')==digest(paths['mir-exporter-wrapper.py']) and
       digest(paths['active-wrapper'])==profile.get('wrapper_sha256'))
    return exact,record

def case_run(repo:Path,ev:Path,variant:str,args,cap,mut,recipe):
    out=ev/'cases/owner17-controls'/variant
    source=cap.PREP.write_case(repo,out)
    case=out/cap.PREP.CASE_NAME
    verified=case/'verified/lib.rs'; original=case/'original/lib.rs'
    cap.PREP.require(source['verified_sha256']==SOURCE and
       source['original_sha256']==ORIGINAL and
       digest(verified)==SOURCE and digest(original)==ORIGINAL,
       f'{variant}: canonical fresh source pair differs')
    if variant.startswith('source_'):
        before,after={
          'source_owner':(b'*g.inner |-> ?payload &*& <T>.own(t, payload);',
                          b'*g.inner |-> ?payload &*& <T>.own(t, payload) &*& true;'),
          'source_outcome':(b'fn_outcome_result(outcome)',
                            b'fn_outcome_result( outcome)'),
        }[variant]
        data=verified.read_bytes()
        cap.PREP.require(data.count(before)==1,f'{variant}: source mutation anchor')
        verified.write_bytes(data.replace(before,after,1))
        cap.PREP.require(cap.PREP.SEVEN.OWNER.OWNER.strip_ghost(verified.read_bytes())==
                         original.read_bytes(),f'{variant}: runtime source changed')
        source['verified_sha256']=digest(verified)
    args.first_barrier=False;args.fingerprint_probe=False
    cap.clear_semantic_opt_ins()
    captures=cap.GUARD.capture_case(case,source,args)
    stages=captures.get('stages',{})
    paired=(captures.get('frontend_refinement') is True and
       captures.get('source_unchanged') is True and
       all(stages.get(n,{}).get('exit')==0 for n in (
          'normal-export','normal-decode','readonly-export','readonly-decode','refinement')) and
       all(stages.get(n,{}).get('source_unchanged') is True for n in stages) and
       digest(original)==ORIGINAL and digest(verified)==source['verified_sha256'])
    tool=args.tool_home;shadow=False
    if not variant.startswith('source_') and paired:
        tool=mut.make_shadow(tool,args.schema,case,variant,SOURCE)
        wrapper=tool/'bin/vf-rust-mir-exporter'
        prior=repr(str(mut.HERE/'capture-actual-owner-mir-mutation.py'))
        data=wrapper.read_text()
        cap.PREP.require(data.count(prior)==1,'shadow wrapper importer anchor')
        data=data.replace(prior,repr(str(Path(__file__).resolve())),1)
        wrapper.write_text(data)
        (case/'mir-exporter-wrapper.py').write_text(data)
        profile=json.loads((case/'mutation-profile.json').read_text())
        profile['wrapper_sha256']=digest(wrapper)
        write(case/'mutation-profile.json',profile)
        shadow=True
    stage=recipe.proof_stage(repo,case,tool,args.schema,Path(args.compiler_sysroot),
                 args.deadline_epoch,'full-verification',variant) if paired else {}
    log=case/'full-verification.log'
    text=log.read_text(errors='replace') if log.is_file() else ''
    errors=cap.LINK.LINK.ERR.findall(text)
    fatal=[x for x in text.splitlines() if x.startswith('Fatal error:')]
    reason=('owner exact verified source SHA256' if variant.startswith('source_')
            else 'owner complete decoded unit SHA256')
    exact,record=(True,None) if not shadow else mutation_exact(case,variant)
    expected=FATAL_PREFIX+reason+'")'
    intended=(paired and exact and stage.get('status')=='RAN' and
       stage.get('source_unchanged') is True and
       stage.get('source_before')==stage.get('source_after') and
       stage.get('intrinsic_gate_active') is True and
       stage.get('pointer_drop_gate_active') is True and
       stage.get('exit')==2 and fatal==[expected] and not errors and
       ADMISSION not in text and A1_ADMISSION not in text and
       "Verifying function '" not in text and
       (not shadow or record.get('selected_source_sha256')==SOURCE))
    result={'variant':variant,'classification':'EXACT_COMPONENT17_NEGATIVE' if intended else 'INCONCLUSIVE',
       'intended_component17_refusal':intended,'a1_negative':False,
       'source_pair_normal_readonly_refinement_complete':paired,
       'test_tool_mutation_profile':shadow,'exact_mutation':exact if shadow else None,
       'source_sha256':source['verified_sha256'],'original_sha256':ORIGINAL,
       'expected_reason':reason,'fatal':fatal,'first_error':errors[0] if errors else None,
       'proof_exit':stage.get('exit'),'proof_stage':stage,'mutation_record':record}
    write(case/'owner17-control-summary.json',result)
    print(json.dumps({'variant':variant,'classification':result['classification'],
                      'proof_exit':stage.get('exit')}),flush=True)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('repo','tool-home','schema','evidence','cloud-dir'):
        p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--compiler-sysroot',required=True)
    p.add_argument('--deadline-epoch',type=int,required=True)
    a=p.parse_args();ev=a.evidence
    if os.environ.get('SMALLSORT_EXECUTION_PROVIDER')!='cloud-build' or os.environ.get('GITHUB_ACTIONS'):
        raise SystemExit('Cloud provider required; GitHub identity impersonation forbidden')
    root=a.repo/'research/challenge-8'
    check=load(root/'overnight-assume-actual/check-owner-nine.py','o26_refresh_historical_owner_controls')
    global CHECK
    CHECK=check
    cap=check.CAP;mut=check.MUT
    recipe=load(a.cloud_dir/'o26-recipe.py','o26_refresh_six_gate_proof')
    controls=ev/'cases/owner17-controls'
    controls.mkdir(parents=True,exist_ok=False)
    positive=canonical(ev)
    rows=[case_run(a.repo,ev,v,a,cap,mut,recipe) for v in VARIANTS]
    complete=(positive['classification']!='INCONCLUSIVE' and
              all(r['intended_component17_refusal'] for r in rows))
    result={'classification':'COMPONENT17_CONTROLS_COMPLETE' if complete else 'INCONCLUSIVE',
      'diagnostic_complete':complete,'verification_accepted':False,
      'a1_isolated_negative':False,'a1_gate_status':'OPEN',
      'positive':positive,'negative_cases':rows,
      'source_sha256':SOURCE,'original_sha256':ORIGINAL,
      'test_only_mir_wrapper_cases':['forget_move_to_copy','forget_cleanup_to_bb23']}
    write(controls/'summary.json',result)
    print(json.dumps({'classification':result['classification'],
                      'diagnostic_complete':complete}),flush=True)
    if not complete:raise SystemExit(1)
if __name__=='__main__':main()
