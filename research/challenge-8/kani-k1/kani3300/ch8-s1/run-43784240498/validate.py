"""Offline package/structured-evidence validation; never invokes proof tools."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
SOURCE = Path('/root/verify-rust-std-ch8-s1-pprime-w13')
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    provenance = read(HERE/'PROVENANCE.json')
    assert subprocess.check_output(['git', '-C', str(SOURCE), 'rev-parse', 'HEAD'],text=True).strip() == provenance['std_sha']
    request = read(HERE/'S1-04/CI-REQUEST.json')
    spec = importlib.util.spec_from_file_location('oracle',HERE/'S1-04/negative_oracle.py')
    module = importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    rows = read(HERE/'ROWS.json'); assert len(rows) == len({r['id'] for r in rows}) == 23
    grouped = [rid for g in request['execution_groups'] for rid in g['row_ids']]
    assert len(grouped) == len(set(grouped)) == 23 and set(grouped) == {r['id'] for r in rows}
    for rel, digest in request['changed_file_sha256'].items():
        assert sha(SOURCE/rel) == digest
    for binding in request['source_bindings'].values():
        path=SOURCE/binding['file'];assert sha(path)==binding['sha256']
        lines=path.read_text().splitlines()
        for loc in binding['locations']:
            assert lines[loc['line']-1]==loc['source']
    groups=read(HERE/'evidence/groups.json')
    for group in groups.values():
        if 'execution' not in group: continue
        assert group['source_before']==group['source_after']
        assert group['tool_fingerprints_before']['required_hashes_present'] is True
        assert group['tool_fingerprints_after']['required_hashes_present'] is True
        assert group['tool_fingerprints_before']['binaries']==group['tool_fingerprints_after']['binaries']
    observed = {}; totals = {'SUCCESS':0,'FAILURE':0,'TIMEOUT':0};sat = 0
    for export, digest in provenance['exports'].items():
        path = HERE/'evidence'/export.split('/')[1];path = path.with_suffix('.json')
        assert sha(path) == digest
        d = read(path)
        assert d['kani_commit'] == provenance['tool_sha'] and d['kani_commit_dirty'] is False
        assert d['run_state']=='COMPLETE' and d['harness_timeout_s']==600
        assert d['harness_selection']['exact'] and d['harness_selection']['unmatched_filters']==[]
        selectors=d['harness_selection']['requested_filters'];assert len(selectors)==len(set(selectors))==len(d['harnesses'])==d['harness_selection']['matched_count']
        assert set(selectors)=={h['name'] for h in d['harnesses']}
        checks=d['configuration']['checks']
        assert all(checks[x] is True for x in ('memory_safety','overflow','unwinding','undefined_function','assertion_reach_checks'))
        assert checks['assert_contracts'] is False and checks['prove_safety_only'] is False
        assert d['configuration']['cbmc_args']==['--object-bits','12']
        for h in d['harnesses']:
            assert h['name'] not in observed; observed[h['name']]=h
            candidates=[r for r in request['rows'] if r['selector']==h['name'] and r['variant']=='production']
            assert len(candidates)==1
            row=candidates[0]; binding=request['source_bindings'][row['id']]
            assert h['resolved_unwind']==row['unwind']
            assert h['file']==binding['file'] and h['line'] in [loc['line'] for loc in binding['locations']]
            assert h['crate_name']==binding['crate'] and h['is_automatically_generated'] is False
            if row['mode']=='PFC':
                import re
                target=h['attributes']['kind']['ProofForContract']['target_fn']
                tokens=lambda x:re.findall(r'::|[A-Za-z_][A-Za-z_0-9]*|[<>,&()]',x)
                assert tokens(target)==tokens(binding['target'])
                assert h['contract']['contracted_function_name']
            else:
                assert h['attributes']['kind']=='Proof' and h['contract'] is None
            outcome=h['outcome'];key=outcome.get('verdict',outcome['kind']);totals[key]+=1
            if key=='TIMEOUT':
                assert h['checks']['total'] is None and h['covers']['total'] is None
                continue
            c,v=h['checks'],h['covers']
            assert all(c[x]==[] for x in ('undetermined','error','unknown','other'))
            assert all(v[x]==[] for x in ('unsatisfiable','unreachable','undetermined','error','unknown','other'))
            assert c['total']==c['success']+len(c['failure'])+len(c['unreachable'])
            assert h['n_failed']==len(c['failure'])==len(h['failed_properties'])
            assert {p['id'] for p in h['failed_properties']}==set(c['failure'])
            assert h['n_properties']==c['total']+v['total']
            assert v['total']==len(v['satisfied']);sat+=v['total']
            assert all(p['status']=='SUCCESS' and p['class']=='unsupported_construct' for p in h['unsupported_constructs'])
    cover_map=read(HERE/'COVER-MAP.json')
    assert len(cover_map)==101 and sum(c['status']=='SATISFIED' for c in cover_map)==57
    for c in cover_map:
        row=next(r for r in request['rows'] if r['id']==c['row'])
        harness=observed[row['selector']]
        assert (c['property_id'] in harness['covers']['satisfied'])==(c['status']=='SATISFIED')
    assert totals=={'SUCCESS':11,'FAILURE':6,'TIMEOUT':4} and len(observed)==21 and sat==57
    negative=read(HERE/'S1-04/negative-oracles.json');assert len(negative)==6
    mutations=0
    for rid,o in negative.items():
        p=SOURCE/o['file']; assert sha(p)==o['source_sha256']
        lines=p.read_text().splitlines();assert lines[o['line']-1]==o['source_line']
        assert o['intended_message'] in '\n'.join(lines[o['line']-1:o['line']+2])
        h=observed[o['selector']];assert module.matches(h,o)
        for key,value in [('selector',None),('property_id',None),('export_file',''),('line',True),('line',None),('class',None)]:
            bad=copy.deepcopy(o);bad[key]=value;assert not module.matches(h,bad);mutations+=1
        for key,value in [('id','wrong.assertion.1'),('file','wrong.rs'),('line','1'),('class','unwinding_assertion'),('status','SUCCESS')]:
            bad=copy.deepcopy(h);bad['failed_properties'][0][key]=value
            assert not module.matches(bad,o);mutations+=1
        for bad in [None,[],{},dict(h,outcome={'kind':'TIMEOUT'}),dict(h,outcome={'kind':'COMPLETED','verdict':'SUCCESS'}),dict(h,checks=None),dict(h,covers=None),dict(h,failed_properties=[]),dict(h,n_failed=2),dict(h,failed_properties=h['failed_properties']*2)]:
            assert not module.matches(bad,o);mutations+=1
        for key in ('error','unknown','undetermined','other'):
            bad=copy.deepcopy(h);bad['checks'][key]=['unexpected'];assert not module.matches(bad,o);mutations+=1
        bad=copy.deepcopy(h);bad['checks']['failure'].append('unrelated.assertion.1');assert not module.matches(bad,o);mutations+=1
        bad=copy.deepcopy(h);bad['failed_properties'][0]['description']='arbitrary reformatted message'
        assert module.matches(bad,o)
    # Pure parser reproduction: preserves space and NUL, unlike .strip().
    raw=' M library/core/src/slice/sort/shared/smallsort.rs\0'
    old={x[3:] for x in raw.strip().split('\0') if x}
    fixed={x[3:] for x in raw.split('\0') if x}
    assert old != {'library/core/src/slice/sort/shared/smallsort.rs'} == fixed
    report={'validation':'PASS_OFFLINE_ONLY','rows':23,'exported_roots':21,'observed':totals,'proof_not_run':2,'satisfied_covers':sat,'required_cover_candidates':len(read(HERE/'COVER-MAP.json')),'exact_negative_assert_bindings':6,'rejected_oracle_mutations':mutations,'porcelain_reproduction':'CONFIRMED','runner_modified':False,'new_control':None,'future_proof':'NOT_RUN','proof_credit':'NONE','limitations':['Named successful assertion and cover-message IDs not exported; qualified acceptance remains pending.','Activation wrapper oracles unobserved/unbound; proposal is deliberately not dispatchable.','Formula variables/clauses, solver-stage times, per-root RSS absent.']}
    (HERE/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__': main()
