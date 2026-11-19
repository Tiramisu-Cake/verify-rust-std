"""Offline construction only; run once from the clean pinned control parent."""
from pathlib import Path
import copy,hashlib,json,re,subprocess
OUT=Path(__file__).resolve().parent
CONTROL=Path('/root/kani-ch8-s4p-2-r1-control-w13');H=CONTROL/'ch8-s1-control'
SOURCE=Path('/root/verify-rust-std-ch8-s4p-2-w13')
PARENT='4059c900e50ba179d824a1e6f6bd7798cf343e36'
SOURCE_PARENT='c12867b1e651a3927cbd9f169fe2c3d3728a44c3'
PLAN='cdedf547df37aec4c442727a902a784f4d1b5155'
REVIEW='2b7872e84c'
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()
def D(b):return hashlib.sha256(b).hexdigest()
def put(path,v):path.write_text(json.dumps(v,indent=2)+'\n')
def transform(s):return s.replace('s4p2_','s4p2r2_').replace('ch8-s4p-2','ch8-s4p-2r2').replace('S4P2-','S4P2R2-').replace('S4P2_N_','S4P2R2_N_')
assert git(CONTROL,'rev-parse','HEAD')==PARENT and not git(CONTROL,'status','--porcelain')
old=json.loads((H/'CI-REQUEST.json').read_text());put(H/'fixtures/s4p2-request.json',old)
(H/'fixtures/s4p2-workflow.yml').write_bytes((CONTROL/'.github/workflows/ch8-s2.yml').read_bytes())
for suffix in ('cfg_pfc','contract_stacks','ordinary_contracts','lexical_bindings','policy','profile','campaign','package'):
    (H/f's4p2r2_{suffix}.py').write_text(transform((H/f's4p2_{suffix}.py').read_text()))
# Audit both old and new compiled modules, retaining every old provider.
p=H/'s4p2r2_cfg_pfc.py';s=p.read_text().replace("'sorting_s4_network_partition')","'sorting_s4_network_partition', 'sorting_s4_network_r2')");p.write_text(s)
p=H/'s4p2r2_lexical_bindings.py';s=p.read_text().replace("(c.VERIFY, 'sorting_s4_network_partition'),","(c.VERIFY, 'sorting_s4_network_partition'), (c.VERIFY, 'sorting_s4_network_r2'),").replace("'sorting_s4_network_partition'):","'sorting_s4_network_partition','sorting_s4_network_r2'):")
s=s.replace("    byname = {r['function']:r for r in records}","    network_r2 = c.SM+('verify','sorting_s4_network_r2')\n    records += [audit(n,i,network_r2) for n,i in functions(read(BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_r2.rs')).items()]\n    byname = {r['function']:r for r in records}")
p.write_text(s)
p=H/'s4p2r2_ordinary_contracts.py';s=p.read_text().replace("rel != c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_partition.rs'", "rel not in (c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_partition.rs', c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_r2.rs')");p.write_text(s)
review=git(Path('/root/verify-rust-std-kani3300-g0'),'rev-parse',REVIEW)
authority=git(Path('/root/verify-rust-std-kani3300-g0'),'rev-parse','HEAD')
inputs={'plan':PLAN,'plan_review':review,'source_reference':SOURCE_PARENT,'control_reference':PARENT,'authority':authority,'intake':'00efb1f5440627362af5c470ad434b89c5e27cca','role_contract_sha256':old['s4p2_inputs']['role_contract_sha256']}
p=H/'s4p2r2_profile.py';s=p.read_text()
s=re.sub(r'^PLAN=.*$', 'PLAN='+repr(PLAN),s,flags=re.M)
s=re.sub(r'^INTAKE=.*$', 'INTAKE='+repr(inputs['intake']),s,flags=re.M)
s=re.sub(r'^IMPLEMENTATION_TASK=.*$', 'IMPLEMENTATION_TASK='+repr(authority),s,flags=re.M)
s=re.sub(r'^INPUTS=.*$', 'INPUTS='+repr(inputs),s,flags=re.M)
s=s.replace('network-fullbyte-singletons-v1','network-fullbyte-concrete-calls-v1')
p.write_text(s)
(H/'s4p2r2_pins.py').write_text('# Copyright Kani Contributors\n# SPDX-License-Identifier: Apache-2.0 OR MIT\nSTD_SHA='+repr(git(SOURCE,'rev-parse','HEAD'))+'\nSTD_TREE='+repr(git(SOURCE,'rev-parse','HEAD^{tree}'))+'\n')
# Shared runtime additions are mechanical dispatch only. Existing branches retained.
for filename in ('runner.py','check_package.py','collect.py'):
    original=(H/filename).read_text();s=original
    s=s.replace('"ch8-s4p-2-v1")','"ch8-s4p-2-v1", "ch8-s4p-2r2-v1")').replace("'ch8-s4p-2-v1')", "'ch8-s4p-2-v1','ch8-s4p-2r2-v1')")
    lines=s.splitlines(True);new=[]
    for i,line in enumerate(lines):
        if filename=='runner.py' and line.strip()=="if request.get('profile')=='ch8-s4p-2-network-fullbyte-singletons-v1':":
            new.extend([transform(line).replace('network-fullbyte-singletons-v1','network-fullbyte-concrete-calls-v1'),transform(lines[i+1])])
        if 'if request.get("schema")=="ch8-s4p-2-v1":import' in line:
            new.append(transform(line))
        if line.strip()=='if request.get("schema")=="ch8-s4p-2-v1":':
            count=3 if 'import s4p2_profile' in lines[i+1] else 2
            new.extend(transform(x) for x in lines[i:i+count])
        if filename=='check_package.py' and '=="ch8-s4p-2-network-fullbyte-singletons-v1"' in line:
            new.append(transform(line).replace('network-fullbyte-singletons-v1','network-fullbyte-concrete-calls-v1'))
        if filename=='check_package.py' and line.strip()=="if request.get('schema')=='ch8-s4p-2-v1':":new.extend(transform(x) for x in lines[i:i+3])
        if filename=='collect.py' and line.strip()=='import s4p2_profile':new.extend(transform(x) for x in lines[i:i+4])
        new.append(line)
    (H/filename).write_text(''.join(new))
# Request: preserve the complete four negative row and binding objects.
r=json.loads(transform(json.dumps(old)))
r.update(std_sha=git(SOURCE,'rev-parse','HEAD'),std_tree=git(SOURCE,'rev-parse','HEAD^{tree}'),source_parent=SOURCE_PARENT,control_parent=PARENT,control_reference=PARENT,entry_g0=authority,s4p2r2_inputs=inputs)
r['profile']='ch8-s4p-2r2-network-fullbyte-concrete-calls-v1'
r['authorization']='OFFLINE_IMPLEMENTATION_ONLY; exact-package review, publication and coordinator GO separately; no launch'
r['s3'].update(plan_commit=PLAN,intake_commit=inputs['intake'])
leaf='library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_network_r2.rs'
verify='library/core/src/slice/sort/shared/smallsort/verify.rs'
r['changed_file_sha256'].update({rel:D((SOURCE/rel).read_bytes()) for rel in (leaf,verify)})
snapshot=json.loads((H/'S4P2-SOURCE.json').read_text());snapshot.update({rel:(SOURCE/rel).read_text() for rel in (leaf,verify)});put(H/'S4P2R2-SOURCE.json',snapshot)
# Keep old role contract exactly; new IDs map to the same four designs.
(H/'S4P2R2-ROLE-CONTRACT.json').write_bytes((H/'S4P2-ROLE-CONTRACT.json').read_bytes())
import sys
sys.path.insert(0,str(H));import cfg_pfc as c
for row in r['rows'][4:]:
    rid=row['id'];selector='slice::sort::shared::smallsort::verify::sorting_s4_network_r2::'+rid
    row.update(selector=selector,source_qualified_selector='core::'+selector)
    data=(SOURCE/leaf).read_bytes();lines=data.decode().splitlines();start=lines.index('fn '+rid+'() {');end=next(i for i in range(start+1,len(lines)) if lines[i]=='}')
    binding=r['source_bindings'][rid];binding.update(file=leaf,sha256=D(data),selector=selector,locations=[{'line':start-1,'source':lines[start-2]},{'line':start+1,'source':lines[start]}])
    roles=[]
    bydesc={x['description']:x for x in row['roles']}
    for i in range(start+1,end):
        m=re.search(r'kani::(assert|cover)\((.*), "([A-Z0-9_]+)"\)',lines[i])
        if not m:continue
        kind,expr,label=m.groups();role=copy.deepcopy(bydesc[label]);role.update(file=leaf,line=i+1,source_sha256=D(data),source_line=lines[i],predicate_tokens=c.spelling(c.tokens(expr)));roles.append(role)
    row['roles']=roles
    if row['structural_na_binding']:row['structural_na_binding'].update(profile=r['profile'],std_sha=r['std_sha'],source_sha256=D(data))
assert r['rows'][:4]==old['rows'][:4]
assert {k:v for k,v in r['source_bindings'].items() if k in [x['id'] for x in old['rows'][:4]]}=={k:v for k,v in old['source_bindings'].items() if k in [x['id'] for x in old['rows'][:4]]}
p=H/'s4p2r2_policy.py';s=p.read_text().replace("LEAF=c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_partition.rs'", "LEAF=c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_r2.rs'").replace("r['control_parent']=='9e14e033f9ee31522b571c127609dcdff76d230b'","r['control_parent']=="+repr(PARENT)).replace("r['source_parent']=='97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a'","r['source_parent']=="+repr(SOURCE_PARENT))
p.write_text(s)
workflow=transform((CONTROL/'.github/workflows/ch8-s2.yml').read_text()).replace('network-fullbyte-singletons-v1','network-fullbyte-concrete-calls-v1')
(CONTROL/'.github/workflows/ch8-s2.yml').write_text(workflow.replace('fetch-depth: 7','fetch-depth: 8').replace('fetch-depth: 5','fetch-depth: 6'))
p=H/'s4p2r2_package.py';p.write_text(p.read_text().replace('    from check_package import CHECKOUT_DEPTHS',"    from check_package import CHECKOUT_DEPTHS as LEGACY_CHECKOUT_DEPTHS\n    CHECKOUT_DEPTHS={**LEGACY_CHECKOUT_DEPTHS,'control':8,'export':6}"))
put(H/'CI-REQUEST.json',r)
print(json.dumps({'source':r['std_sha'],'control_parent':PARENT,'profile':r['profile'],'negative_rows_unchanged':True}))
