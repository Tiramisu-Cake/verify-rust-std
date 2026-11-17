#!/usr/bin/env python3
"""Static Git/source/payload checks for the complete local S1-08 candidate.
No actual compiler/exporter/decoder/verifier/full runner, no external evidence.
"""
import argparse
import copy
import datetime
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import prepare_package as prep

HERE = Path(__file__).resolve().parent


def need(condition, label):
    if not condition:
        raise AssertionError(label)


def check(control, std_repo):
    h=control/'ch8-s1-control'
    sys.path.insert(0,str(h))
    import s108_package as s
    import runner
    import check_package
    git=prep.git
    def old(path): return git(control,'show',prep.CONTROL_BASE+':'+path)
    def current_source(path): return git(std_repo,'show',prep.STD+':'+path)
    def prior_source(path): return git(std_repo,'show',prep.STD_BASE+':'+path)
    request_bytes=(h/'CI-REQUEST.json').read_bytes()
    r=json.loads(request_bytes);base=json.loads(old('ch8-s1-control/CI-REQUEST.json'))
    m=json.loads((h/'ROLE-MAP.json').read_bytes())
    source_map={}
    for name,macros in prep.FILES.items():
        rel=prep.PREFIX+name
        s.equivalent(prior_source(rel),current_source(rel),macros)
        source_map[rel]=prep.line_map(prior_source(rel),current_source(rel))
        need((std_repo/rel).read_text()==current_source(rel),'mutable source checkout drift')
    need(not git(std_repo,'status','--porcelain'),'source checkout clean')
    need(git(std_repo,'rev-parse','HEAD').strip()==prep.STD,'source commit')
    need(git(std_repo,'rev-parse','HEAD^').strip()==prep.STD_BASE,'source parent')
    need(set(git(std_repo,'diff','--name-only',prep.STD_BASE,prep.STD).splitlines())==set(source_map),'source scope')
    maps=s.validate_map(m,r)
    all_expanded_labels=[]; all_expanded_roots=[]
    for name,macros in prep.FILES.items():
        src=current_source(prep.PREFIX+name)
        for macro in macros:
            roles=s.labelled_sites(src,macro)
            for inv in re.finditer(r'(?m)^'+macro+r'!\(([a-z0-9_]+),',src):
                root=inv[1];all_expanded_roots.append(root)
                all_expanded_labels.extend(root+'::'+role for role in roles)
    need(len(all_expanded_roots)==len(set(all_expanded_roots))==25,'all source expansion roots')
    need(len(all_expanded_labels)==len(set(all_expanded_labels))==197,'all source label uniqueness')
    need(r['role_map']['sha256']==s.sha((h/'ROLE-MAP.json').read_bytes()),'manifest hash')
    def relocated(rel, line):
        return source_map[rel][line] if rel in source_map else line
    for rel,digest in r['changed_file_sha256'].items():
        need(s.sha(current_source(rel).encode())==digest,'source file '+rel)
    for rel,digest in r['ci_payload_sha256'].items():
        need(s.sha((control/rel).read_bytes())==digest,'payload '+rel)
    need(r['std_sha']==runner.STD_SHA==prep.STD,'std pin')
    need(r['std_tree']==runner.STD_TREE==git(std_repo,'rev-parse',prep.STD+'^{tree}').strip(),'std tree')
    need(r['tool_sha']==runner.TOOL_SHA==prep.TOOL,'tool pin')
    need(r['tool_tree']==runner.TOOL_TREE==git(control,'rev-parse',prep.TOOL+'^{tree}').strip(),'tool tree')
    need(r['control_parent']==prep.CONTROL_BASE,'control parent')
    changed={'schema','std_sha','std_tree','changed_file_sha256','rows','ci_payload_sha256','reservations',
             'ci_changed_paths','source_bindings','control_parent','replacement_unions','legacy_symbolic_rows','role_map'}
    need(set(r)==set(base)|{'role_map'},'request fields')
    for key in base.keys()-changed:
        need(r[key]==base[key],'unchanged request '+key)
    need(len(r['rows'])==35 and len(r['execution_groups'])==14,'roots and groups')
    negative_details=[]
    for oldrow,row in zip(base['rows'],r['rows'],strict=True):
        expected=copy.deepcopy(oldrow)
        labels=[e for e in m['required_success_bindings'] if e['row_id']==row['id']]
        expected['required_success_messages']=[e['expected_message'] for e in labels]
        need([e['legacy_message'] for e in labels]==oldrow['required_success_messages'],'role obligation inventory')
        if oldrow.get('oracle') and row['variant']=='production':
            o=expected['oracle'];rel=o['file']
            o['line']=relocated(rel,o['line']);o['source_sha256']=s.sha(current_source(rel).encode())
        need(row==expected,'row/oracle/cover/config drift '+row['id'])
        if row.get('oracle'):
            o=row['oracle']
            negative_details.append({'id':row['id'],'property_id':o['property_id'],
                                     'source_sha256':o['source_sha256'],'line':o['line'],
                                     'oracle_identity':'UNCHANGED_PREDECLARED','coordinates':'RELOCATED_ONLY'})
        b=r['source_bindings'][row['id']];ob=base['source_bindings'][row['id']]
        expected_b=copy.deepcopy(ob);rel=b['file'];src=current_source(rel)
        expected_b['sha256']=s.sha(src.encode())
        for loc in expected_b['locations']:
            loc['line']=relocated(rel,loc['line'])
            need(src.splitlines()[loc['line']-1]==loc['source'],'source binding anchor')
        need(b==expected_b,'binding drift '+row['id'])
    # Runner and evidence pipeline semantics are frozen, except the two pins.
    old_runner=old('ch8-s1-control/runner.py').replace(base['std_sha'],r['std_sha']).replace(base['std_tree'],r['std_tree'])
    need(old_runner==(h/'runner.py').read_text(),'runner semantic drift')
    for name in ('collect.py','negative_oracle.py','rich_evidence.py','pack_evidence.py','binding_metadata.py',
                 'test_runner.py','test_s104.py','test_s105.py','test_s107.py','activation-default.patch','activation-override.patch'):
        need(old('ch8-s1-control/'+name)==(h/name).read_text(),'frozen pipeline '+name)
    expected_yaml=old('.github/workflows/ch8-s1.yml').replace('name: CH8 S1-05 rich evidence','name: CH8 S1-08 role labels').replace(
        'fetch-depth: 4','fetch-depth: 5').replace('test_s105.py test_s107.py','test_s105.py test_s107.py test_s108.py')
    need((control/'.github/workflows/ch8-s1.yml').read_text()==expected_yaml,'workflow semantic scope')
    yaml=check_package.check_yaml(control/'.github/workflows/ch8-s1.yml')
    # Recompute every required role site from frozen source, no ordinal inference.
    receipt_path=HERE.parent/'s1-07/run-43923266772/accept/ACCEPT.json'
    need(s.sha(receipt_path.read_bytes())==m['legacy_receipt']['sha256'],'legacy receipt identity')
    historical=json.loads(receipt_path.read_bytes())
    legacy={(row['id'],e['message']):e for row in historical['rows'] for e in row.get('required_success',[])}
    supplemental_expected=[]
    for e in m['required_success_bindings']:
        src=current_source(e['source']['file'])
        need(e['source']['commit']==prep.STD,'role source commit')
        need(e['expected_description'] == (e['expected_message'] if e['binding_kind']=='EXACT_ROLE_LABEL' else s.PLACEHOLDER),'constant expected description')
        for site in e['source']['sites']:
            text='\n'.join(src.splitlines()[site['line']-1:site.get('end_line',site['line'])])
            need(text.strip()==site['text'].strip(),'site text '+e['expected_message'])
            need(s.sha(site['text'].encode())==site['sha256'],'site hash')
        if e['binding_kind']=='EXACT_ROLE_LABEL':
            role=s.ROLE_SUFFIX[e['legacy_message']]
            need(e['role']==role,'role suffix')
            sites=s.labelled_sites(src,e['source']['macro'])
            need(e['source']['sites'][0]['text']==sites[role]['text'],'macro role binding')
            invocation=e['source']['invocation']
            need(src.splitlines()[invocation['line']-1].startswith(e['source']['macro']+'!('+e['root']+','),'selected root expansion')
            need(src[src.index(invocation['text']):].startswith(invocation['text']),'invocation source')
        else:
            previous=legacy[e['row_id'],e['legacy_message']]
            need(e['legacy_s107']==previous,'preserve historical exact semantic binding/set')
            need([x['line'] for x in e['source']['sites']]==[
                relocated(e['source']['file'],n) for n in previous['source']['source_role_sites']], 'legacy source relocation')
    for row in r['rows']:
        if row['id'] not in {e['row_id'] for e in m['required_success_bindings'] if e['binding_kind']=='EXACT_ROLE_LABEL'}:
            continue
        b=r['source_bindings'][row['id']]
        if b['file'].endswith('sorting_entry_smoke.rs'):
            supplemental_expected.extend((row['id'],role) for role in ('type_layout','n0_empty_unchanged','n1_value_unchanged'))
    need([(e['row_id'],e['role']) for e in m['supplemental_label_sites']]==supplemental_expected,'supplemental complete applicability')
    for e in m['supplemental_label_sites']:
        src=current_source(e['source']['file'])
        need(e['source']['sha256']==s.sha(src.encode()),'supplemental source')
        need(src.splitlines()[e['source']['line']-1].strip().startswith('kani::assert('),'supplemental site')
    # Apply the exact unchanged negative overlays to a temporary Git index at
    # the NEW base. This does not checkout a tree or execute a compiler/runner.
    variants=[]
    with tempfile.TemporaryDirectory() as tmp:
        for name,v in r['variants'].items():
            need(v==base['variants'][name],'variant oracle/payload drift')
            patch=h/v['patch'];need(s.sha(patch.read_bytes())==v['sha256'],'patch hash')
            env={**os.environ,'GIT_INDEX_FILE':str(Path(tmp)/(name+'.index'))}
            def index(*args):
                return subprocess.check_output(['git','-C',str(std_repo),*args],env=env)
            index('read-tree',prep.STD)
            index('apply','--cached','--check',str(patch))
            index('apply','--cached',str(patch))
            need(index('diff','--cached','--name-only',prep.STD).decode().splitlines()==list(v['changed_file_sha256']),'variant changed path')
            source_under_test={**r['changed_file_sha256'],**v['changed_file_sha256']}
            for rel,digest in source_under_test.items():
                need(s.sha(index('show',':'+rel))==digest,'variant source-under-test '+rel)
            variants.append({'id':name,'new_base':prep.STD,'apply_cached':'PASS','patch_sha256':v['sha256'],
                             'source_under_test_sha256':source_under_test})
    runner.load_request(h/'CI-REQUEST.json')
    paths=set(git(control,'diff','--name-only',prep.TOOL).splitlines())
    paths.update(git(control,'ls-files','--others','--exclude-standard').splitlines())
    need(sorted(paths)==r['ci_changed_paths'],'control changed path inventory')
    return {'status':'PASS','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'std_sha':prep.STD,'std_tree':r['std_tree'],'control_parent':prep.CONTROL_BASE,
            'request_sha256':s.sha(request_bytes),'role_map_sha256':r['role_map']['sha256'],
            'source_equivalence':'PASS_ALL_NON_DIAGNOSTIC_TOKENS_IN_ORDER',
            'scope':'23 macro assertion sites; negative functions/operands/control flow/covers/types/domain preserved',
            'role_map':maps,'all_source_expansion_roots':len(all_expanded_roots),
            'all_source_labels':len(all_expanded_labels),'supplemental_applicability_sites':len(supplemental_expected),
            'required_covers':sum(len(x['required_cover_messages']) for x in r['rows']),
            'negatives':negative_details,'variants':variants,'yaml_preflight':yaml,
            'runner_export_decoder_native_capture_snapshot_location_semantics':'UNCHANGED',
            'group_order_flags_checks_caps_unwind_preflight':'UNCHANGED_EXCEPT_REQUIRED_CONTROL_DEPTH_5',
            'compiler_rustfmt_runtime_verifier':'NOT_RUN','admission':'OFFLINE_PENDING','independent_review':'NOT_RUN_W14_NEXT',
            'ci_push_publication_ledger':'NOT_RUN','proof_credit':'NONE'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--control',type=Path,default=Path('/root/kani-ch8-s1-08-w13'))
    p.add_argument('--std',type=Path,default=Path('/root/verify-rust-std-ch8-s1-08-w13'))
    a=p.parse_args();result=check(a.control,a.std);prep.write(HERE/'STATIC-VALIDATION.json',result)
    print(json.dumps({k:result[k] for k in ('status','request_sha256','role_map','required_covers','compiler_rustfmt_runtime_verifier')}))
