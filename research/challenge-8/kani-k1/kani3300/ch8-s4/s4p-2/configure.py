"""Bind new profile, exact role inventory and minimal shared dispatch additions."""
from implement import SOURCE,CONTROL,HERE,OLD,OUT,BASE,TASK,put,digest,git,leaf,verify,oldleaf
import json,re,sys
sys.path.insert(0,str(HERE))
import cfg_pfc as c
old=json.loads((OLD/'CI-REQUEST.json').read_text())
order=tuple([x['id'] for x in old['rows'][:4]]+['s4p2_network_b01_n02_fullbyte','s4p2_network_b01_n03_fullbyte','s4p2_network_b01_n04_fullbyte','s4p2_network_b01_n00_01_fullbyte'])
contract=json.loads((BASE/'kani3300/ch8-s4/s4p-2-inputs/ROLE-SAT-CONTRACT.json').read_text())
bydesign={x['design_id']:x for x in contract['rows']}
designs={rid:'PLAN_N'+n+'_V34_B01_FULLU8' for rid,n in zip(order[4:],('02','03','04','01'))}
domains={rid:{'length_interval':[min(bydesign[designs[rid]]['lengths']),max(bydesign[designs[rid]]['lengths'])],
    'allocation':34,'base':1,'logical_values':'ALL_34_INDEPENDENT_U8_0_255','initialized':True,
    'type':'u8','comparator':'KeyLess<u8>','summary_edges':[]} for rid in order[4:]}
inputs={'plan':'7253272c427eb9b564c79350ef73b231fa124298','plan_review':'e287943e116a102d5950295b2629d80a62d1f922',
 'intake':'842984040e87b8b8594653634b72df7d800ca198','intake_review':'3c7bd65cf0bb758cb82dc56ef71a8b8e23efd5c0',
 'exact_admission':'9bb6e2b7a18e338f532ec817f8acfd7515fc2fc9','source_reference':'985062ebad90cee1e2846b1648cd6a8624d146f6',
 'control_reference':'2db5d2c08804036d283cb36450647cd584ee9e10',
 'role_contract_sha256':'c90950843f17903b0271a0cf349e4afd5e9189924119aacb252904f0a0b7ef1d',
 'implementation_gates_sha256':'b9d81c6dcff93f42828e604e147073317c882390af9fd4f18f2f66da747455af'}
profile=(HERE/'s4p2_profile.py').read_text()
start=profile.index('ORDER=');end=profile.index('CANDIDATES=')
profile=profile[:start]+'ORDER='+repr(order)+'\n'+profile[end:]
start=profile.index('PLAN=');end=profile.index('ACCOUNTING=')
profile=profile[:start]+''.join(k+'='+repr(v)+'\n' for k,v in [('PLAN',inputs['plan']),('INTAKE',inputs['intake']),('BOUNDARY',inputs['exact_admission']),('IMPLEMENTATION_TASK',TASK),('INPUTS',inputs)])+profile[end:]
start=profile.index('CALLEES=');end=profile.index('def enabled')
profile=profile[:start]+'CALLEES={rid:"small_sort_network" for rid in CANDIDATES}\nDOMAINS='+repr(domains)+'\nDESIGNS='+repr(designs)+'\nTERMINAL_SCHEMA="ch8-s4p-2-campaign-v1"\nSEAL_SCHEMA="ch8-s4p-2-portable-seal-v1"\n'+profile[end:]
profile=profile.replace('ch8-s4p-2-fullbyte-length-blocks-v1','ch8-s4p-2-network-fullbyte-singletons-v1').replace('S4_FULLBYTE_LENGTH_BLOCK_ACTUAL_BODY_CANDIDATE','S4P2_FULLBYTE_NETWORK_EXACT_PARTITION_ACTUAL_BODY_CANDIDATE')
(HERE/'s4p2_profile.py').write_text(profile)
(HERE/'s4p2_pins.py').write_text("STD_SHA="+repr(git(SOURCE,'rev-parse','HEAD'))+'\nSTD_TREE='+repr(git(SOURCE,'rev-parse','HEAD^{tree}'))+'\n')
import s4p2_profile as p
request=json.loads(json.dumps(old));request.update(schema=p.SCHEMA,profile=p.PROFILE,entry_g0=TASK,
    std_sha=git(SOURCE,'rev-parse','HEAD'),std_tree=git(SOURCE,'rev-parse','HEAD^{tree}'),domains=domains,
    s4p2_inputs=inputs,accounting_reference=p.ACCOUNTING,qualification_inventory=list(p.CANDIDATES))
del request['s4p_inputs']
request['s3'].update(selected=list(order),deferred=list(p.DEFERRED),plan_commit=p.PLAN,intake_commit=p.INTAKE,boundary_commit=p.BOUNDARY)
request['execution_groups']=p.groups(request)
request['changed_file_sha256'].update({rel:digest((SOURCE/rel).read_bytes()) for rel in (leaf,verify)})
request['rows']=request['rows'][:4];request['source_bindings']={k:v for k,v in request['source_bindings'].items() if k in order[:4]}
for rid in order[4:]:
    model=bydesign[designs[rid]];lo,hi=domains[rid]['length_interval']
    prefix='S4P2_N_'+(f'{lo:02}' if lo==hi else '00_01')
    selector='slice::sort::shared::smallsort::verify::sorting_s4_network_partition::'+rid
    data=(SOURCE/leaf).read_bytes();lines=data.decode().splitlines();start=lines.index('fn '+rid+'() {');attr=start-2
    end=next(i for i in range(start+1,len(lines)) if lines[i]=='}')
    binding=json.loads(json.dumps(old['source_bindings'][old['rows'][6]['id']]))
    binding.update(file=leaf,sha256=digest(data),selector=selector,mode='Original',target=None,
        locations=[{'line':attr+1,'source':lines[attr]},{'line':start+1,'source':lines[start]}])
    roles=[]
    for i in range(start+1,end):
        m=re.search(r'kani::(assert|cover)\((.*), "([A-Z0-9_]+)"\)',lines[i])
        if m:
            kind,expr,label=m.groups();semantic=label[len(prefix)+1:]
            roles.append({'description':label,'class':'cover' if kind=='cover' else 'assertion','status':'SATISFIED' if kind=='cover' else 'SUCCESS',
                'file':leaf,'line':i+1,'source_sha256':digest(data),'source_line':lines[i],
                'producer_id':'UNKNOWN_UNTIL_SAME_INVOCATION_INVENTORY','semantic_role':semantic,'predicate_tokens':c.spelling(c.tokens(expr))})
    row=json.loads(json.dumps(old['rows'][6]));row.update(id=rid,selector=selector,source_qualified_selector='core::'+selector,
        roles=roles,required_cover_count=model['cover_count'],required_cover_messages=[prefix+'_'+x for x in model['cover_roles']],
        required_success_messages=[prefix+'_'+x for x in model['assertion_roles']],scope_classification=p.classification(rid),
        design_id=designs[rid],structurally_not_applicable_roles=model['structurally_not_applicable_roles'],
        structural_na_binding=({'profile':p.PROFILE,'design_id':designs[rid],'std_sha':request['std_sha'],
            'source_sha256':digest(data),'domain':domains[rid]} if hi==1 else None))
    request['rows'].append(row);request['source_bindings'][rid]=binding
snapshot=json.loads((OLD/'S4P-SOURCE.json').read_text())
snapshot.update({rel:(SOURCE/rel).read_text() for rel in (leaf,verify)})
put(HERE/'S4P2-SOURCE.json',snapshot)
inventory={k:request[k] for k in ('rows','source_bindings','domains','s4p2_inputs')}
put(HERE/'S4P2-INVENTORY.json',inventory)
policy=(HERE/'s4p2_policy.py').read_text()
policy=policy.replace("LEAF=c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_partition.rs'", "OLD_LEAF=c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_partition.rs'\nLEAF=c.BASE+'slice/sort/shared/smallsort/verify/sorting_s4_network_partition.rs'")
policy=policy.replace("file=LEAF if rid in p.ORDER[3:] else BATCH", "file=LEAF if positive else OLD_LEAF if rid==p.ORDER[3] else BATCH")
start=policy.index('            index=p.CANDIDATES.index');end=policy.index('        elif rid==p.ORDER[3]:',start)
policy=policy[:start]+'''            model=next(x for x in CONTRACT['rows'] if x['design_id']==p.DESIGNS[rid])
            lo,hi=p.DOMAINS[rid]['length_interval']
            prefix='S4P2_N_'+(f'{lo:02}' if lo==hi else '00_01')
            assert row['required_success_messages']==[prefix+'_'+x for x in model['assertion_roles']]
            assert row['required_cover_messages']==[prefix+'_'+x for x in model['cover_roles']]
            assert row['required_cover_count']==model['cover_count']
'''+policy[end:]
needle='    assert r[\'schema\']=='
at=policy.index(needle,policy.index('def validate_request'))
policy=policy[:at]+'''    raw=(HERE/'S4P2-INVENTORY.json').read_bytes()
    assert digest(raw)==INVENTORY_SHA256, 'exact S4P2 inventory drift'
    expected=json.loads(raw)
    assert json.dumps({k:r[k] for k in expected},sort_keys=True)==json.dumps(expected,sort_keys=True), 'exact role/domain/source inventory mismatch'
'''+policy[at:]
policy=policy.replace("assert r['s4p_inputs']==p.INPUTS","assert r['s4p2_inputs']==p.INPUTS")
policy+="\nINVENTORY_SHA256="+repr(digest((HERE/'S4P2-INVENTORY.json').read_bytes()))+'\nCONTRACT='+repr(contract)+'\n'
# Rich counts must be real integers; same-site loop instances remain fully retained.
policy=policy.replace("h=parsed['harness'];records=properties['properties']", "h=parsed['harness'];records=properties['properties']\n        if any(type(h.get(k)) is not int for k in ('n_properties','n_failed')):return False\n        if h['n_properties']!=len(records):return False\n        if any(type(h.get(kind,{}).get(key)) is not int for kind,keys in [('checks',('total','success')),('covers',('total',))] for key in keys):return False")
policy=policy.replace("target_failure=row['expected']=='DETECTED'", "target_failure=row['expected']=='DETECTED'\n        if h['n_failed']!=len(failures):return False")
(HERE/'s4p2_policy.py').write_text(policy)
# Copy only the request/workflow routing branches. Old branch bytes/conditions persist.
for filename in ('runner.py','check_package.py','collect.py'):
    data=(OLD/filename).read_text()
    data=data.replace('"ch8-s4p-1-v1")','"ch8-s4p-1-v1", "ch8-s4p-2-v1")').replace("'ch8-s4p-1-v1'):","'ch8-s4p-1-v1','ch8-s4p-2-v1'):")
    lines=data.splitlines(True);new=[];i=0
    while i<len(lines):
        line=lines[i]
        if filename=='runner.py' and line.strip()=="if request.get('profile')=='ch8-s4p-1-fullbyte-length-blocks-v1':":
            new.extend([line.replace('ch8-s4p-1-fullbyte-length-blocks-v1',p.PROFILE),lines[i+1].replace('s4p_', 's4p2_')])
        if 'if request.get("schema")=="ch8-s4p-1-v1":import' in line:
            new.append(line.replace('ch8-s4p-1-v1','ch8-s4p-2-v1').replace('s4p_', 's4p2_'))
        if line.strip()=='if request.get("schema")=="ch8-s4p-1-v1":':
            new.extend([line.replace('ch8-s4p-1-v1','ch8-s4p-2-v1'),lines[i+1].replace('s4p_', 's4p2_'),lines[i+2].replace('s4p_', 's4p2_')])
        if filename=='check_package.py' and '=="ch8-s4p-1-fullbyte-length-blocks-v1"' in line:
            new.append(line.replace('ch8-s4p-1-fullbyte-length-blocks-v1',p.PROFILE).replace('s4p_', 's4p2_'))
        if filename=='check_package.py' and line.strip()=="if request.get('schema')=='ch8-s4p-1-v1':":
            new.extend([line.replace('ch8-s4p-1-v1','ch8-s4p-2-v1'),lines[i+1].replace('s4p_', 's4p2_'),lines[i+2].replace('s4p_', 's4p2_')])
        if filename=='collect.py' and line.strip()=='import s4p_profile':
            new.extend(['    import s4p2_profile\n','    if s4p2_profile.enabled(request):\n','        import s4p2_campaign\n','        return s4p2_campaign.collect(roots,request)\n'])
        if filename=='check_package.py':line=line.replace("if r.get('schema')=='ch8-s4p-1-v1'", "if r.get('schema') in ('ch8-s4p-1-v1','ch8-s4p-2-v1')")
        new.append(line);i+=1
    (HERE/filename).write_text(''.join(new))
# Explicit Original/null is carried on real new-profile rows only, without changing old _row_base.
data=(HERE/'s4p2_campaign.py').read_text()
data=data.replace("'ch8-s4p-2-campaign-v1'",'p.TERMINAL_SCHEMA').replace("'ch8-s4p-2-portable-seal-v1'",'p.SEAL_SCHEMA')
data=data.replace("    rows=[]\n", "    rows=[]\n")
data=data.replace("        rows.append(result)", "        if result.get('mode')!='Original' or result.get('target') is not None:raise GlobalFailure('Original/null row mismatch')\n        result['target']=None\n        if rid not in done:atomic(out/rid/'receipt.json',result)\n        rows.append(result)")
data=data.replace("    atomic(out/rid/'worker-receipt.json',result)", "    if result.get('mode')!='Original' or result.get('target') is not None:raise GlobalFailure('worker Original/null mismatch')\n    result['target']=None\n    atomic(out/rid/'worker-receipt.json',result)")
data=data.replace("        meta=terminal.get('s3_campaign')", "        rows=terminal.get('rows')\n        if not isinstance(rows,list) or len(rows)!=8 or [x.get('id') for x in rows]!=list(p.ORDER):raise GlobalFailure('terminal row inventory mismatch')\n        if any(x.get('mode')!='Original' or 'target' not in x or x['target'] is not None for x in rows):raise GlobalFailure('terminal Original/null mismatch')\n        meta=terminal.get('s3_campaign')")
data=data.replace("            row=c.read(root/rid/'receipt.json')", "            row=c.read(root/rid/'receipt.json')\n            if row.get('mode')!='Original' or 'target' not in row or row['target'] is not None:raise GlobalFailure('replay Original/null mismatch')")
(HERE/'s4p2_campaign.py').write_text(data)
workflow=(OLD.parent/'.github/workflows/ch8-s2.yml').read_text().replace('CH8 S4 full-byte length blocks','CH8 S4P2 exact network N0..4 partitions').replace('ch8-s4p-1-fullbyte-length-blocks-v1',p.PROFILE).replace('s4p_validate.py','s4p2_validate.py').replace('s4p_campaign.py','s4p2_campaign.py')
(CONTROL/'.github/workflows/ch8-s2.yml').write_text(workflow)
put(HERE/'CI-REQUEST.json',request)
print('S4P2 bindings configured',request['std_sha'])
