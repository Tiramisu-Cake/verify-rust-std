#!/usr/bin/env python3
"""Targeted origin/consumption mutations, no compiler, CI or source writes."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('composite_under_test',HERE/'replay.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def main():
    start=time.monotonic();b=m.load(False);report,omap,compat=m.compose(b);receipts=[]
    def record(name,fn,expected):
        before=time.monotonic()
        try:
            result=fn()
            if expected=='REJECT':raise AssertionError('mutation accepted')
            assert result, 'mutation did not close the targeted gate'
            verdict='DISCRIMINATED'
            reason=expected
        except (ValueError,KeyError,TypeError,IndexError) as exc:
            assert expected=='REJECT',(name,str(exc))
            verdict='REJECTED';reason=str(exc)
        receipts.append({'mutation':name,'verdict':verdict,'gate':reason})
        print(name+': '+verdict,flush=True)
    def partition(name,edit):
        def run():
            v=copy.deepcopy(b);edit(v);m.validate_partition(v)
        record(name,run,'REJECT')
    def component(name,edit):
        def run():
            v=copy.deepcopy(report);edit(v);m.validate_components(v,b)
        record(name,run,'REJECT')
    def row(v,rid):return next(x for x in v['rows'] if x['id']==rid)
    def obs(v,rid):return next(x for x in v['origins']['retry']['collected']['rows'] if x['id']==rid)
    retry=lambda v:v['origins']['retry']
    partition('foreign_run',lambda v:retry(v)['identity'].__setitem__('id',44095954742))
    partition('foreign_attempt',lambda v:retry(v)['identity'].__setitem__('run_attempt',2))
    partition('foreign_head',lambda v:retry(v)['identity'].__setitem__('head_sha',m.HEADS['original']))
    partition('foreign_request',lambda v:retry(v)['groups']['cell-u34']['receipt.json'].__setitem__('request_sha256',m.REQUESTS['original']))
    partition('changed_semantic_input',lambda v:retry(v)['request']['flags'].__setitem__('cfg',[]))
    partition('changed_type',lambda v:retry(v)['request']['rows'][0].__setitem__('type','u8'))
    partition('wrong_cell_timeout',lambda v:retry(v)['request']['rows'][0].__setitem__('timeout_seconds',600))
    partition('duplicate_row',lambda v:retry(v)['collected']['rows'].append(copy.deepcopy(retry(v)['collected']['rows'][0])))
    partition('foreign_row',lambda v:retry(v)['collected']['rows'].append({'id':'foreign'}))
    partition('half_group',lambda v:retry(v)['groups']['cell-u34']['properties.json']['harnesses'].pop())
    partition('failed_group_healthy_root',lambda v:retry(v)['groups']['cell-u34']['receipt.json'].__setitem__('state','FAILED'))
    old=m.read(m.runpath('original')/'collected.json')
    def splice(v):
        oldrow=next(r for r in old['rows'] if r['id']=='unstable_default_cell')
        retry(v)['collected']['rows']=[copy.deepcopy(oldrow) if r['id']=='unstable_default_cell' else r for r in retry(v)['collected']['rows']]
    partition('old_unknown_cell_splice',splice)
    def binaries():
        v=copy.deepcopy(b);g=retry(v)['groups']['cell-u34']
        for field in ('tool_fingerprints_before','tool_fingerprints_after'):g['receipt.json'][field]['binaries']['cbmc']['sha256']='f'*64
        return not m.compatibility(v)['gates']['protected_binary_digest_version_all_origins']
    record('changed_protected_binary_across_origins',binaries,'COMPATIBILITY_PENDING')
    def drift():
        v=copy.deepcopy(b);retry(v)['groups']['cell-u34']['receipt.json']['tool_fingerprints_after']['binaries']['cbmc']['sha256']='f'*64
        m.group_identity(v,'retry','cell-u34')
    record('changed_protected_binary_after',drift,'REJECT')
    def solver():
        v=copy.deepcopy(b);retry(v)['groups']['cell-u34']['export.json']['configuration']['cbmc_args']=['--object-bits','13']
        return not m.compatibility(v)['gates']['actual_configuration_solver_checks_equal']
    record('changed_solver_checks',solver,'COMPATIBILITY_PENDING')
    def root_mutation(kind):
        v=copy.deepcopy(b);g=retry(v)['groups']['cell-u34'];props=next(h['properties'] for h in g['properties.json']['harnesses'] if h['name'].endswith('::stable_default_cell'))
        p=next(p for p in props if p['description']=='stable_default_cell::model_enabled')
        if kind=='missing':p['description']='REMOVED'
        if kind=='duplicate':
            p2=copy.deepcopy(p);p2['id']=p2['id'].rsplit('.',1)[0]+'.999999';p2['display_id']=p2['id'];props.append(p2)
        if kind=='wrong_source':p['file']=m.helpers()[0].EXPORT_PREFIX+'library/core/src/cell.rs'
        if kind=='wrong_root':p['id']=p['id'].replace('::stable_default_cell.','::foreign.');p['display_id']=p['id']
        if kind=='wrong_status':p['status']='UNREACHABLE'
        r=row(report,'stable_default_cell');role=next(r for r in m.read(m.runpath('original')/'ROLE-MAP.json')['required_success_bindings'] if r['row_id']=='stable_default_cell' and r['role']=='model_enabled')
        return m.role_binding(r,role,props)['binding']=='PENDING'
    for kind in ('missing','duplicate','wrong_source','wrong_root','wrong_status'):
        record('role_'+kind,lambda kind=kind:root_mutation(kind),'REQUIRED_ROLE_PENDING')
    component('dropped_exact_role',lambda v:row(v,'stable_default_cell')['required_success'].pop())
    component('dropped_semantic_set',lambda v:row(v,'inactive_pairs_read_free')['required_success'].pop(0))
    component('foreign_component_origin',lambda v:row(v,'stable_default_cell').__setitem__('origin_key','44095954742/1'))
    component('dropped_U',lambda v:v['U_records'].pop())
    component('changed_U_source_hash',lambda v:v['U_records'][0].__setitem__('source_sha256','f'*64))
    component('changed_U_origin',lambda v:v['U_records'][0].__setitem__('origin_key','44128268928/1'))
    component('dropped_pending_gate',lambda v:row(v,'stable_default_cell')['required_success'][0].__setitem__('binding','PENDING'))
    component('dropped_PFC',lambda v:v['PFC_bindings'].pop())
    component('changed_PFC_concrete_type',lambda v:v['PFC_bindings'][0].__setitem__('type','foreign'))
    component('dropped_cover',lambda v:row(v,'stable_default_cell')['required_covers'].pop())
    component('dropped_negative',lambda v:row(v,'activation-default').__setitem__('negative_oracle',None))
    component('stale_oracle_span95',lambda v:row(v,'activation_descending_rejected')['negative_oracle']['property'].__setitem__('id',row(v,'activation_descending_rejected')['negative_oracle']['property']['id'].replace(':95:32: 95:48',':100:32: 100:48')))
    component('stale_oracle_span101',lambda v:row(v,'activation_effectful_rejected')['negative_oracle']['property'].__setitem__('id',row(v,'activation_effectful_rejected')['negative_oracle']['property']['id'].replace(':101:21: 101:37',':106:21: 106:37')))
    component('broken_companion',lambda v:v['companions'].pop(next(iter(v['companions']))))
    component('broken_union',lambda v:v['replacement_unions'].pop())
    component('union_unqualified_member',lambda v:row(v,'freeze_copy_u8_n1')['local_pending_gates'].append('SYNTHETIC_LOCAL_FAILURE'))
    def transitive():
        v=copy.deepcopy(report);rs=m.helpers()[6].index(v['rows'],'id','test rows');q=b['origins']['original']['request'];specs=m.helpers()[6].index(q['rows'],'id','test specs')
        for r in rs.values():r['spec']=specs[r['id']]
        rs['stable_default_activation-legal']['local_pending_gates'].append('SYNTHETIC_LOCAL_FAILURE')
        edges,unions=m.dependencies(rs,specs,q)
        return rs['activation-default']['qualification']=='PENDING' and edges['activation-default']['qualification']=='PENDING'
    record('transitive_companion_pending',transitive,'COMPANION_QUALIFICATION_PENDING')
    def cross_origin():
        rs=copy.deepcopy({r['id']:r for r in report['rows']});q=b['origins']['original']['request'];specs=m.helpers()[6].index(q['rows'],'id','test specs')
        for r in rs.values():r['spec']=specs[r['id']]
        rs['stable_default_activation-legal']['origin_key']='44128268928/1'
        edges,_=m.dependencies(rs,specs,q)
        return not edges['activation-default']['valid_same_run_pins'] and rs['activation-default']['qualification']=='PENDING'
    record('unexpected_cross_origin_companion',cross_origin,'SAME_RUN_PINS_PENDING')
    def cycle():
        rs=copy.deepcopy({r['id']:r for r in report['rows']});q=copy.deepcopy(b['origins']['original']['request']);specs=m.helpers()[6].index(q['rows'],'id','test specs')
        specs['corruption_companion']['companion']='snapshot_guards_companion';specs['snapshot_guards_companion']['companion']='corruption_companion'
        for r in rs.values():r['spec']=specs[r['id']]
        m.dependencies(rs,specs,q)
        return all(rs[r]['qualification']=='PENDING' for r in ('corruption_companion','snapshot_guards_companion','count_corruption_rejected'))
    record('least_fixed_point_cycle_no_seed',cycle,'TRANSITIVE_PENDING')
    need=report['totals'];assert need['rows_qualified']==need['rows']==len(b['origins']['original']['request']['rows'])
    assert (need['required_roles'],need['exact_role_labels'],need['semantic_bindings'],need['required_SAT_covers'],need['negative_oracles'],need['PFC_bound'])==(127,111,16,113,8,22)
    assert all(compat['gates'].values())
    result={'schema':'s108-composite-targeted-mutations-v1','status':'PASS','tests':len(receipts),'receipts':receipts,
        'reuse':'Reviewed inventory/U premises/PFC source-native-contract/oracle/least-fixed-point rules; targeted adapter deltas only',
        'baseline_totals':need,'duration_seconds':round(time.monotonic()-start,3),'assurance':'STATIC_STRUCTURED_SYNTHETIC_ONLY','independent_review':'PENDING'}
    (HERE/'MUTATIONS.json').write_bytes(m.encoded(result))
    print(json.dumps({'status':'PASS','tests':len(receipts),'duration_seconds':result['duration_seconds']},sort_keys=True))

if __name__=='__main__':main()
