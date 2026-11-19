"""Offline construction from the exact clean network-r2 control parent."""
from pathlib import Path
import copy, hashlib, json, re, subprocess, sys
OUT=Path(__file__).resolve().parent
MAIN=OUT.parents[6]
C=Path('/root/kani-ch8-s4-next-control-w15'); H=C/'ch8-s1-control'
S=Path('/root/verify-rust-std-ch8-s4-next-w15')
SP='8faf8e62af8f82b5c46af020086f8df591b6757e'
CP='3d3fb715271e3b195c6e0eee3557d5b0a6aad00d'
PLAN='c0de8471801ac22b38e3290c7a6b75742135af6b'
REVIEW='762a2a678eb624d1ddd18f0764a365e7787392c0'
ADMISSION='8896f60ae9e0ea1c706c6b8693d00e2500190676'
MAIN=Path('/root/verify-rust-std-kani3300-g0')
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def D(b):return hashlib.sha256(b).hexdigest()
def put(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def ns(s):return s.replace('s4p2r2_','s4p3_').replace('ch8-s4p-2r2','ch8-s4p-3').replace('S4P2R2-','S4P3-').replace('S4P2R2_N_','S4P3_N_')
assert git(C,'rev-parse','HEAD')==CP and not git(C,'status','--porcelain')
old=json.loads((H/'CI-REQUEST.json').read_text())
(H/'fixtures/s4p2r2-request.json').write_bytes((H/'CI-REQUEST.json').read_bytes())
(H/'fixtures/s4p2r2-workflow.yml').write_bytes((C/'.github/workflows/ch8-s2.yml').read_bytes())
for suffix in ('cfg_pfc','contract_stacks','ordinary_contracts','lexical_bindings','policy','profile','campaign','package'):
    (H/f's4p3_{suffix}.py').write_text(ns((H/f's4p2r2_{suffix}.py').read_text()))
leaf='library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_full_lengths_next.rs'
verify='library/core/src/slice/sort/shared/smallsort/verify.rs'
p=H/'s4p3_cfg_pfc.py';p.write_text(p.read_text().replace("'sorting_s4_network_r2')", "'sorting_s4_network_r2', 'sorting_s4_full_lengths_next')"))
p=H/'s4p3_lexical_bindings.py';text=p.read_text().replace("(c.VERIFY, 'sorting_s4_network_r2'),", "(c.VERIFY, 'sorting_s4_network_r2'), (c.VERIFY, 'sorting_s4_full_lengths_next'),").replace("'sorting_s4_network_r2'):","'sorting_s4_network_r2','sorting_s4_full_lengths_next'):")
text=text.replace("    byname = {r['function']:r for r in records}","    next_module = c.SM+('verify','sorting_s4_full_lengths_next')\n    records += [audit(n,i,next_module) for n,i in functions(read(BASE+'slice/sort/shared/smallsort/verify/sorting_s4_full_lengths_next.rs')).items()]\n    byname = {r['function']:r for r in records}")
p.write_text(text)
p=H/'s4p3_ordinary_contracts.py';p.write_text(p.read_text().replace("c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_r2.rs')", "c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_r2.rs', c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_full_lengths_next.rs')"))
# Same guard, snapshot, full oracle, frame, canary and covers; only finite N differs.
oldcontract=json.loads((H/'S4P2R2-ROLE-CONTRACT.json').read_text())
contract={'schema':'s4p3-network-boundaries-role-contract-v1','status':'REQUIRED_ACCEPTANCE_CONTRACT_FOR_FUTURE_PACKAGE','rows':[]}
for n in (8,9,13,17):
    row=copy.deepcopy(next(x for x in oldcontract['rows'] if x['lengths']==[2]))
    row.update(design_id=f'PLAN_N{n:02}_V34_B01_FULLU8',lengths=[n])
    row['cover_roles']={k.replace('N02',f'N{n:02}'):v for k,v in row['cover_roles'].items()}
    row['static_assignments']=[{'role':role,'n':n,'active_input':([0]*n if role=='DUPLICATE' else list(range(n,0,-1))), 'candidate_output':([0]*n if role=='DUPLICATE' else list(range(1,n+1)))} for role in row['cover_roles']]
    contract['rows'].append(row)
put(H/'S4P3-ROLE-CONTRACT.json',contract)
authority='778418b5a6c59e9b649435fd4bbc7a61ae0cd2ec'  # observed task-containing snapshot, not an execution GO
inputs={'plan':PLAN,'plan_review':REVIEW,'source_reference':SP,'control_reference':CP,'authority':authority,'intake':PLAN,'network_admission_reference':ADMISSION,'role_contract_sha256':D((H/'S4P3-ROLE-CONTRACT.json').read_bytes())}
# Profile is the unchanged network-r2 mechanism with a new exact finite domain.
profile=ns((H/'s4p2r2_profile.py').read_text())
order=tuple(old['rows'][i]['id'] for i in range(4))+tuple(f's4p3_network_b01_n{n:02}_fullbyte' for n in (8,9,13,17))
domains={rid:{**copy.deepcopy(old['domains'][old['rows'][4]['id']]),'length_interval':[n,n]} for rid,n in zip(order[4:],(8,9,13,17))}
values={'ORDER':order,'PLAN':PLAN,'INTAKE':PLAN,'BOUNDARY':ADMISSION,'IMPLEMENTATION_TASK':authority,'INPUTS':inputs,'DOMAINS':domains,'DESIGNS':{rid:f'PLAN_N{n:02}_V34_B01_FULLU8' for rid,n in zip(order[4:],(8,9,13,17))}}
for key,value in values.items():profile,count=re.subn(r'^'+key+r'=.*$',key+'='+repr(value),profile,flags=re.M);assert count==1
profile=profile.replace('S4P2_FULLBYTE_NETWORK_EXACT_PARTITION_ACTUAL_BODY_CANDIDATE','S4P3_FULLBYTE_NETWORK_BOUNDARY_ACTUAL_BODY_CANDIDATE')
(H/'s4p3_profile.py').write_text(profile)
(H/'s4p3_pins.py').write_text('# Copyright Kani Contributors\n# SPDX-License-Identifier: Apache-2.0 OR MIT\nSTD_SHA='+repr(git(S,'rev-parse','HEAD'))+'\nSTD_TREE='+repr(git(S,'rev-parse','HEAD^{tree}'))+'\n')
# Shared runtime: add only dispatch adjacent to the retained r2 dispatch.
for filename in ('runner.py','check_package.py','collect.py'):
    text=(H/filename).read_text().replace('"ch8-s4p-2r2-v1")','"ch8-s4p-2r2-v1", "ch8-s4p-3-v1")').replace("'ch8-s4p-2r2-v1')","'ch8-s4p-2r2-v1','ch8-s4p-3-v1')")
    lines=text.splitlines(True);result=[]
    for i,line in enumerate(lines):
        if filename=='runner.py' and line.strip()=="if request.get('profile')=='ch8-s4p-2r2-network-fullbyte-concrete-calls-v1':":result.extend(ns(x) for x in lines[i:i+2])
        if 'if request.get("schema")=="ch8-s4p-2r2-v1":import' in line:result.append(ns(line))
        if line.strip()=='if request.get("schema")=="ch8-s4p-2r2-v1":':result.extend(ns(x) for x in lines[i:i+(3 if 'import s4p2r2_profile' in lines[i+1] else 2)])
        if filename=='check_package.py' and '=="ch8-s4p-2r2-network-fullbyte-concrete-calls-v1"' in line:result.append(ns(line))
        if filename=='check_package.py' and line.strip()=="if request.get('schema')=='ch8-s4p-2r2-v1':":result.extend(ns(x) for x in lines[i:i+3])
        if filename=='collect.py' and line.strip()=='import s4p2r2_profile':result.extend(ns(x) for x in lines[i:i+4])
        result.append(line)
    (H/filename).write_text(''.join(result))
# New request preserves negative objects without a textual namespace rewrite.
r=copy.deepcopy(old)
r.pop('s4p2r2_inputs')
r.update(schema='ch8-s4p-3-v1',profile='ch8-s4p-3-network-fullbyte-concrete-calls-v1',std_sha=git(S,'rev-parse','HEAD'),std_tree=git(S,'rev-parse','HEAD^{tree}'),source_parent=SP,control_parent=CP,control_reference=CP,entry_g0=authority,s4p3_inputs=inputs,domains=domains)
r['s3'].update(selected=list(order),plan_commit=PLAN,intake_commit=PLAN,boundary_commit=ADMISSION)
r['accounting_reference']['latest_admission_only']=ADMISSION
r['qualification_inventory']=list(order[4:])
r['execution_groups']=[{'id':'s3-'+rid,'variant':'production','unwind':u,'row_ids':[rid]} for rid,u in zip(order,(34,34,34,36,36,36,36,36))]
r['rows']=copy.deepcopy(old['rows'][:4]);r['source_bindings']={row['id']:copy.deepcopy(old['source_bindings'][row['id']]) for row in r['rows']}
r['changed_file_sha256'].update({rel:D((S/rel).read_bytes()) for rel in (leaf,verify)})
sys.path.insert(0,str(H));import cfg_pfc as cfg
lines=(S/leaf).read_text().splitlines();sha=D((S/leaf).read_bytes())
for rid,n in zip(order[4:],(8,9,13,17)):
    row=copy.deepcopy(old['rows'][4]);selector='slice::sort::shared::smallsort::verify::sorting_s4_full_lengths_next::'+rid
    prefix=f'S4P3_N_{n:02}_';model=next(x for x in contract['rows'] if x['lengths']==[n])
    start=lines.index('fn '+rid+'() {');end=next(i for i in range(start+1,len(lines)) if lines[i]=='}')
    row.update(id=rid,selector=selector,source_qualified_selector='core::'+selector,design_id=model['design_id'],required_success_messages=[prefix+k for k in model['assertion_roles']],required_cover_messages=[prefix+k for k in model['cover_roles']],roles=[])
    row['scope_classification']['category']='S4P3_FULLBYTE_NETWORK_BOUNDARY_ACTUAL_BODY_CANDIDATE'
    for i in range(start+1,end):
        m=re.search(r'kani::(assert|cover)\((.*), "([A-Z0-9_]+)"\)',lines[i])
        if not m:continue
        kind,expr,label=m.groups()
        row['roles'].append({'description':label,'class':'cover' if kind=='cover' else 'assertion','status':'SATISFIED' if kind=='cover' else 'SUCCESS','file':leaf,'line':i+1,'source_sha256':sha,'source_line':lines[i],'producer_id':'UNKNOWN_UNTIL_SAME_INVOCATION_INVENTORY','semantic_role':label.removeprefix(prefix),'predicate_tokens':cfg.spelling(cfg.tokens(expr))})
    r['rows'].append(row)
    r['source_bindings'][rid]={'file':leaf,'sha256':sha,'selector':selector,'mode':'Original','target':None,'crate':'core','locations':[{'line':start-1,'source':lines[start-2]},{'line':start+1,'source':lines[start]}]}
assert r['rows'][:4]==old['rows'][:4]
p=H/'s4p3_policy.py';text=p.read_text().replace('verify/sorting_s4_network_r2.rs','verify/sorting_s4_full_lengths_next.rs').replace("r['control_parent']=='4059c900e50ba179d824a1e6f6bd7798cf343e36'","r['control_parent']=="+repr(CP)).replace("r['source_parent']=='c12867b1e651a3927cbd9f169fe2c3d3728a44c3'","r['source_parent']=="+repr(SP)).replace("'c90950843f17903b0271a0cf349e4afd5e9189924119aacb252904f0a0b7ef1d'",repr(inputs['role_contract_sha256']))
p.write_text(text)
workflow=ns((C/'.github/workflows/ch8-s2.yml').read_text()).replace('fetch-depth: 8','fetch-depth: 9').replace('fetch-depth: 6','fetch-depth: 7')
(C/'.github/workflows/ch8-s2.yml').write_text(workflow)
p=H/'s4p3_package.py';p.write_text(p.read_text().replace("'control':8,'export':6","'control':9,'export':7"))
(H/'test_s4p3.py').write_text(ns((H/'test_s4p2r2.py').read_text()).replace("'control':8,'export':6","'control':9,'export':7"))
put(H/'CI-REQUEST.json',r)
print(json.dumps({'status':'CONSTRUCTED_NOT_FROZEN','source':r['std_sha'],'control_parent':CP,'negative_rows_unchanged':True}))
