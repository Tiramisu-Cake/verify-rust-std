#!/usr/bin/env python3
"""Cloud-only exact C3 projection proof gates; inert on import."""
from pathlib import Path
import json
import os
import re
import shutil

HERE = Path('research/challenge-8/cloud-build/sort4-c3-bound-prefix')
TRANSLATOR = Path('src/rust_frontend/vf_mir_translator/vf_mir_translator.ml')
CONTROLS = ('c3-normal-missing-close', 'c3-unwind-missing-close',
            'c3-normal-omit-join', 'c3-unwind-omit-join', 'normal-false-post',
            'c1-unwind-false-assert', 'c2-unwind-false-assert', 'c3-unwind-false-assert')
HELPERS = ('recover_pair','join_four_owned_cells','selected_four_limits',
           'split_selected_four','join_selected_four')

def entries(log, name):
    return [m.start() for m in re.finditer(
        r"(?m)^\s*\d+(?:\.\d+)?s: .*: Verifying function '" + re.escape(name) + "'", log)]

def run(a, tool, active, capture, snapshot_fn, service):
    need, sha, record, stage = service.need, service.sha, service.record, service.stage
    profile_path = a.proof_root / HERE / 'profile.json'
    profile = json.loads(profile_path.read_text())
    need(profile['classification'] == 'EXPERIMENTAL_C1_C2_C3_BOUND_PREFIX' and
         profile['profile_accepted'] is False and profile['cloud_enabled'] is True,
         'C3 bound profile identity/enablement differs')
    fixture = a.evidence / 'c3-fixture'
    need(capture['classification'] == 'FRESH_C3_SOURCE_MIR_PREAST_CAPTURED_REFUSED_NOT_PROOF' and
         sha(fixture / 'verified/lib.rs') == profile['source_sha256'] and
         capture['pre_ast_sha256'] == profile['pre_ast_sha256'] and
         sha(a.evidence / 'c3-normal-sort4-full-mir.txt') == profile['normal_full_mir_sha256'] and
         sha(a.evidence / 'c3-readonly-sort4-full-mir.txt') == profile['readonly_full_mir_sha256'],
         'C3 fresh source/MIR/preAST pins differ')
    patch = a.proof_root / HERE / 'verifast-c3-bound-prefix-TEST.patch'
    need(sha(patch) == profile['patch_sha256'] and
         sha(tool / TRANSLATOR) == profile['base_translator_sha256'],
         'C3 bound delta/base mismatch')
    before = snapshot_fn(a,tool)
    for mode,args in [('check',['--check']),('apply',[])]:
        code,_ = stage(a,'bound-patch-'+mode,
                       ['git','-C',str(tool),'apply',*args,str(patch)],tool,active,60)
        need(code == 0,'C3 bound patch '+mode+' failed')
    need(sha(tool / TRANSLATOR) == profile['patched_translator_sha256'], 'C3 bound translator mismatch')
    code,_=stage(a,'bound-console-build',['make','-C',str(tool/'src'),'../bin/verifast',
                    'WITHOUT_LABLGTK=yes','VERBOSE=yes'],tool,active,900)
    need(code == 0,'C3 bound console build failed')
    after = snapshot_fn(a,tool)
    need(after['head']==before['head'] and after['effective_rsspec']==before['effective_rsspec'] and
         after['proof_std']==before['proof_std'] and
         all(after['critical'][k]==v for k,v in before['critical'].items() if k!=str(TRANSLATOR)) and
         all(after['binaries'][k]==v for k,v in before['binaries'].items() if k!='bin/verifast'),
         'C3 bound changed frozen inputs')
    record(a.evidence/'c3-bound-tool-snapshot.json',after)
    env=active.copy()
    env.update({'SORT4_ACTUAL_AST_SCOPE_TEST':'1','SORT4_ACTUAL_C1_PREFIX_TEST':'0',
        'SORT4_C1_PREFIX_CONTROL':'none','SORT4_C1_OUTPUT_EQ':'0','SORT4_STRICT_LFT_CUT':'1',
        'SORT4_ACTUAL_C2_DISCOVERY_TEST':'0','SORT4_ACTUAL_C2_BOUND_PREFIX_TEST':'0',
        'SORT4_C2_BOUND_CONTROL':'none','SORT4_ACTUAL_C3_CAPTURE_TEST':'0',
        'SORT4_ACTUAL_C3_BOUND_PREFIX_TEST':'0','SORT4_C3_BOUND_CONTROL':'none'})
    command=[str(tool/'bin/verifast'),'-rustc_args','--edition 2021','-verbose','2','verified/lib.rs']
    old = a.evidence/'c2-discovery-fixture'
    env['SORT4_ACTUAL_C2_BOUND_PREFIX_TEST']='1'
    code,raw=stage(a,'bound-default-off-c2',command,old,env)
    need(code==0 and '0 errors found (' in raw and 'Leak check.' in raw,'C3 bound altered C2 default-off')
    env.update({'SORT4_ACTUAL_C2_BOUND_PREFIX_TEST':'0','SORT4_ACTUAL_C2_DISCOVERY_TEST':'1'})
    code,raw=stage(a,'bound-unbound-c2',command,old,env)
    need(code in (1,2) and 'UNBOUND_C2_LIFETIME_NOT_PROOF' in raw,'C3 bound lost C2 refusal')
    env.update({'SORT4_ACTUAL_C2_DISCOVERY_TEST':'0','SORT4_ACTUAL_C3_CAPTURE_TEST':'1',
                'SORT4_C3_CAPTURE_SOURCE_SHA256':profile['source_sha256']})
    code,raw=stage(a,'bound-unbound-c3',command,fixture,env)
    need(code in (1,2) and 'FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF' in raw and
         not entries(raw,'sort4_stable'),'C3 mandatory capture refusal lost')
    env.update({'SORT4_ACTUAL_C3_CAPTURE_TEST':'0','SORT4_ACTUAL_C3_BOUND_PREFIX_TEST':'1'})
    positive=a.evidence/'c3-bound-positive-fixture'
    need(not positive.exists(),'C3 positive fixture exists')
    shutil.copytree(fixture,positive,symlinks=True)
    pre=positive/'actual-c3-bound-pre-ast.ml';post=positive/'actual-c3-bound-post-ast.ml'
    pre.unlink(missing_ok=True);post.unlink(missing_ok=True)
    code,raw=stage(a,'bound-positive',command,positive,env,600)
    errors=[line for line in raw.splitlines() if ': error:' in line or line.startswith('Fatal error:')]
    dead=[line for line in raw.splitlines() if re.search(r'\): dead code$',line)]
    target=entries(raw,'sort4_stable')
    helpers={name:entries(raw,name) for name in HELPERS}
    text=post.read_text() if post.exists() else ''
    result={'classification':'C3_FIRST_BLOCKER_DIAGNOSTIC','accepted':False,'positive_exit':code,
        'positive_errors':errors,'dead_code':dead,'target_entries':len(target),
        'helper_before_target':{k:len(v)==1 and len(target)==1 and v[0]<target[0] for k,v in helpers.items()},
        'pre_ast_sha256':sha(pre) if pre.exists() else None,'post_ast_sha256':sha(post) if post.exists() else None,
        'tool_translator_sha256':sha(tool/TRANSLATOR),'controls':{},
        'full_sort4_callable_summary':False,'allocation_review':'PENDING_INDEPENDENT_RAW_REVIEW'}
    positive_ok=(code==0 and not errors and not dead and len(target)==1 and
        all(result['helper_before_target'].values()) and '0 errors found (' in raw and
        'Leak check.' in raw[target[0]:] and 'Executing return statement' in raw[target[0]:] and
        pre.exists() and sha(pre)==profile['pre_ast_sha256'] and post.exists() and
        text.count('"std::ops::FnMut::call_mut"')==3 and
        text.count('"#register_type_projection_equality"')==3 and
        'UNBOUND_LIFETIME_DECL_PLACEHOLDER' not in text and
        'SORT4-C3-BOUND admitted ' in raw)
    result['positive_ok']=positive_ok
    if positive_ok:result['classification']='C1_C2_C3_BOUND_PREFIX_VF0_CANDIDATE'
    record(a.evidence/'c3-bound-result.json',result)
    if not positive_ok:return result
    for control in CONTROLS:
        case=a.evidence/('c3-bound-control-'+control)
        shutil.copytree(fixture,case,symlinks=True)
        env['SORT4_C3_BOUND_CONTROL']=control
        code,raw=stage(a,'bound-control-'+control,command,case,env)
        errs=[line for line in raw.splitlines() if ': error:' in line or line.startswith('Fatal error:')]
        reached=entries(raw,'sort4_stable')
        first_after=(len(errs)==1 and len(reached)==1 and reached[0]<raw.index(errs[0]))
        result['controls'][control]={'exit':code,'first_errors':errs,
            'target_entry_before_first_error':first_after,
            'intended_negative':'PENDING_FIRST_VC_RAW_REVIEW',
            'log_sha256':sha(a.evidence/('c3-bound-control-'+control+'.log'))}
        record(a.evidence/'c3-bound-result.json',result)
    # A changed source must refuse admission, before target or transformed AST.
    case=a.evidence/'c3-bound-source-mutant';shutil.copytree(fixture,case,symlinks=True)
    p=case/'verified/lib.rs';data=p.read_bytes();needle=b'(&*c, &*a);'
    need(data.count(needle)==1,'C3 source mutant operand anchor changed')
    p.write_bytes(data.replace(needle,b'(&*a, &*c);',1));env['SORT4_C3_BOUND_CONTROL']='none'
    code,raw=stage(a,'bound-source-mutant',command,case,env)
    result['source_mutant']={'exit':code,'target_proof_entries':len(entries(raw,'sort4_stable')),
        'first_errors':[line for line in raw.splitlines() if ': error:' in line or line.startswith('Fatal error:')],
        'intended_refusal':'PENDING_RAW_REVIEW','mutated_source_sha256':sha(p)}
    record(a.evidence/'c3-bound-result.json',result)
    return result
