#!/usr/bin/env python3
"""Exact final-object distinguishing replay, source scanners only."""
import copy,hashlib,json,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
P=json.loads((HERE/'PINS.json').read_text());Q=Path(P['control']['worktree'])/'ch8-s1-control'
sys.dont_write_bytecode=True;sys.path.insert(0,str(Q))
import cfg_pfc as c,ordinary_contracts as o,lexical_bindings as l
r=json.loads((Q/'CI-REQUEST.json').read_text())
sources=json.loads((Q/'S2-SOURCE.json').read_text())
B=l.BATCH

def result(fun,root,request):
    try:
        d=fun(root,request)
        return {'status':d['status'],'records':len(d.get('checked_active_ordinary_uses',d.get('functions',[])))}
    except c.GateError as e:return {'status':'REJECT','diagnostic':str(e)}

def main():
    rows=[]
    with tempfile.TemporaryDirectory(prefix='s2-r4-r1-replay-') as tmp:
        root=Path(tmp)
        for rel,text in sources.items():
            p=root/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
        request=copy.deepcopy(r)
        removed={key:request.pop(key) for key in ('ordinary_contract_source_sha256','cfg_pfc_source_sha256')}
        old='#[kani::stub(s2_swap_seam,weak_swap)]'
        for target in ('s2_swap_seam','swap_if_less'):
            replacement='use crate::kani::stub as ordinary1;\nuse self::ordinary1 as ordinary2;\n#[ordinary2('+target+',weak_swap)]'
            (root/B).write_text(sources[B].replace(old,replacement))
            outcomes={gate.__name__:result(gate.check,root,request) for gate in (o,c)}
            expected='STATIC_PASS' if target=='s2_swap_seam' else 'REJECT'
            assert all(x['status']==expected for x in outcomes.values())
            if expected=='REJECT':assert all('swap_if_less has active contract attrs' in x['diagnostic'] for x in outcomes.values())
            rows.append({'case':'EXACT_REVIEW_DISCRIMINATOR_'+target,'replacement':replacement,'only_removed_hash_maps':list(removed),'gates':outcomes})
        request=copy.deepcopy(r);request.pop('lexical_source_sha256')
        final=sources[B];frozen=(Q/'fixtures/s2-r4-batch.rs.txt').read_text()
        assert hashlib.sha256(frozen.encode()).hexdigest()=='794fb18e5f6aa5a79f79b6e200b9cf5a4074442ddf51bdba9df4ea5f32567ef7'
        for name,text,expected in [('frozen_r4',frozen,'REJECT'),('fixed_r4_r1',final,'STATIC_PASS'),
          ('removed_import',final.replace('sort4_stable, ',''),'REJECT'),
          ('renamed_import',final.replace('sort4_stable, ','sort4_stable as renamed4, '),'REJECT'),
          ('wrong_target_import',final.replace('sort4_stable, ','insert_tail as sort4_stable, '),'REJECT'),
          ('cfg_disabled_import',final.replace('sort4_stable, ','')+'\n#[cfg(not(kani))]\nuse super::super::sort4_stable;\n','REJECT'),
          ('qualified_legitimate',final.replace('sort4_stable, ','').replace('sort4_stable(','super::super::sort4_stable('),'STATIC_PASS')]:
            (root/B).write_text(text);out=result(l.check,root,request);assert out['status']==expected,(name,out)
            rows.append({'case':name,'only_removed_hash_maps':['lexical_source_sha256'],'name_gate':out})
    doc={'status':'STATIC_PASS','source':P['source'],'control':P['control'],'frozen_review':'f5dd71722f82ac59e37152927a5f4dd9eee6ea1a',
      'cases':rows,'R14-01':'REPAIRED_SOURCE_BINDING; frozen rejection/fixed acceptance; no observed compiler diagnostic',
      'R14-02':'EXACT_CHAIN_REJECTED_BY_BOTH_GATES_ON_CONTRACTED_TARGET; safe chain retained',
      'limits':'Lexical scanner only; native compile/causal repair NOT_RUN; actual R3 failing unit/body UNKNOWN; independent review pending; proof credit NONE'}
    (HERE/'FINDING-CLOSURE.json').write_text(json.dumps(doc,indent=2)+'\n')
    print('STATIC_PASS: exact review alias discriminator in both gates; frozen r4 reject/fixed pass and import mutations')
if __name__=='__main__':main()
