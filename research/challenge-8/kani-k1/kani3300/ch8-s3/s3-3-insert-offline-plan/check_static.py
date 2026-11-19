#!/usr/bin/env python3
"""Read-only bounded source/document arithmetic check. No runtime import or native run."""
from pathlib import Path
import hashlib, json, subprocess, ast
from decimal import Decimal

HERE=Path(__file__).resolve().parent
def read(name):return json.loads((HERE/name).read_text())
def digest(raw):return hashlib.sha256(raw).hexdigest()

def main():
    inputs=read('INPUTS.json');alt=read('ALTERNATIVES.json');resource=read('RESOURCE.json')
    deps=read('DEPENDENCIES.json')['dependencies'];cites=read('SOURCE-CITATIONS.json')['citations']
    bodies={}
    for dep in deps:
        argv=['git','-C',dep['repository']]
        raw=subprocess.check_output(argv+['show',dep['commit']+':'+dep['path']])
        assert len(raw)==dep['bytes'] and digest(raw)==dep['sha256']
        assert subprocess.check_output(argv+['rev-parse',dep['commit']+':'+dep['path']],text=True).strip()==dep['blob']
        bodies[(dep['commit'],dep['path'])]=raw
    for cite in cites:
        raw=bodies[(cite['commit'],cite['path'])]
        assert digest(raw)==cite['file_sha256']
        assert digest(b''.join(raw.splitlines(keepends=True)[cite['line_start']-1:cite['line_end']]))==cite['range_sha256']
    facts=read('SOURCE-CITATIONS.json')['authored_intake_fact_rows']
    for fact in facts:
        raw=bodies[(fact['commit'],fact['path'])];line=raw.decode().splitlines()[fact['line']-1]
        assert line==fact['row_text'] and digest((line+'\n').encode())==fact['row_sha256']
        assert digest(raw)==fact['file_sha256']
        cells=line.strip('|').split('|');observed=inputs['censored_insertions'][fact['id']]
        assert Decimal(cells[1])==Decimal(str(observed['compile_observation_upper_seconds']))
        assert Decimal(cells[4])==Decimal(str(observed['whole_child_seconds']))
        assert int(cells[6])==observed['sampled_local_trigger_kib']
        assert cells[7]=='TERMINATED_UNFINISHED_RSS'
    ctl=inputs['control'];src=inputs['source']
    runner=bodies[(ctl,'ch8-s1-control/runner.py')].decode();ast.parse(runner)
    assert 'cap = min(GROUP_RSS_MAX_KIB, available-MEMORY_RESERVE_KIB)' in runner
    assert "memory['group_cap_kib']=min(memory['group_cap_kib'],RSS_CAP_KIB)" in runner
    assert 'if rss > rss_cap_kib:' in runner and 'time.sleep(0.05)' in runner
    outer=bodies[(ctl,'ch8-s1-control/s3_runtime.py')].decode()
    assert "elif peak>outer_rss_kib:cutoff='outer_sampled_rss'" in outer
    assert 'time.sleep(.02)' in outer
    assert "slot,p.CAPS['outer_rss_kib']" in bodies[(ctl,'ch8-s1-control/s32_campaign.py')].decode()
    unit=1048576;reserve=2*unit;outer_cap=12*unit
    peak=max(row['sampled_local_trigger_kib'] for row in inputs['censored_insertions'].values())
    assert peak==6361996
    for row in resource['options']:
        local=row['local_kib'];available=row['full_local_admission_A_kib']
        assert available==local+reserve and local<=outer_cap-reserve
        assert row['outer12_minus_local_kib']==outer_cap-local
        assert row['above_max_prior_trigger_kib']==local-peak>0
        assert min(local,outer_cap,available-reserve)==local
        assert min(local,outer_cap,available-1-reserve)==local-1
    assert min(6815744,outer_cap,8*unit-reserve)==6*unit
    assert 6815744+reserve==8912896 and resource['outer14_claim'] is False
    original={(base,tail) for base in range(1,17) for tail in range(1,17)}
    short={(base,1) for base in range(1,17)};long={(base,16) for base in range(1,17)}
    middle={(base,8) for base in range(1,17)}
    assert len(original)==256 and max(b+p for b,p in original)==32<34
    assert len(short)==len(long)==len(middle)==16 and short.isdisjoint(long)
    assert len(short|long)==32 and len(original-{(1,1)})==255
    assert {(1,1)}<=short and {(1,16)}<=long and len(original-middle)==240
    assert (0,1) not in original
    early={(a,x) for a in range(256) for x in range(256) if x>=a}
    sift={(a,x) for a in range(256) for x in range(256) if x<a}
    assert len(early)==32896 and len(sift)==32640 and early.isdisjoint(sift)
    assert len(early|sift)==65536
    assert not any(a<=x<a for a in range(256) for x in range(256))
    smallsort=bodies[(src,'library/core/src/slice/sort/shared/smallsort.rs')].decode().splitlines()
    assert '\n'.join(smallsort[499:541]).count('swap_if_less(')==25
    assert alt['positive_network_alternative']['domain']['outside_positions']==34-9==25
    assert alt['positive_network_alternative']['mode']=='Original'
    assert alt['preferred_workflow']['order']==['checker_order_corrupt','checker_count_corrupt','sort13_weak','i_p01_b01_fullu8','sort9_v34_b01_len09_real']
    assert alt['preferred_workflow']['envelope_seconds']==5*720+180+240==4020
    assert alt['preferred_workflow']['remaining_inside6900_seconds']==2880
    assert alt['memory_only_workflow_alternative']['envelope_seconds']==4*720+180+240==3300
    assert inputs['accounting_reference']['remaining_attempts']==17-13==4
    assert not inputs['accounting_reference']['reservation_or_mutation']
    assert [inputs['current_caps'][k] for k in ['child_seconds','compile_seconds','slot_seconds']]==[600,180,720]
    seen=set()
    for node in read('DAG.json')['nodes']:
        assert set(node['requires'])<=seen;seen.add(node['id'])
    assert len(seen)==9
    review=read('REVIEW-BINDING.json')
    assert inputs['independent_review_commit']==review['review']=='028531727fc48ef9f26f16dfb95c2b2666c96dd7'
    assert inputs['admission_commit']==review['admission_commit']=='ff193cc35690a5daabaa849d412c58d9f286d893'
    admission=json.loads(bodies[(inputs['admission_commit'],'research/challenge-8/kani-k1/kani3300/ch8-s3/admission-s3-2-r1-exact-location/ADMISSION.json')])
    assert admission['qualified_case_count']==1 and admission['exact_metadata_case_count']==3
    assert admission['qualified_case']['initialization_provider_eligible'] is False
    assert admission['qualified_case']['universal_contract_or_assumed_summary_credit']=='NONE'
    assert all(not row['qualification_as_init_leaf_provider_summary'] and row['actual_mask_dstinit']=='OPEN' for row in admission['diagnostic_rows'])
    assert admission['general_rule']['status']=='PENDING_NOT_ADMITTED'
    assert not admission['accounting']['dispatch_charge_refund_reservation_grant']
    assert inputs['status']==alt['status']=='READY_PLANONLY_INPUTS_BOUND'
    assert alt['qualification_and_credit']['new_S3_3_qualified_leaves']==0
    for file in HERE.iterdir():
        if file.is_file():
            if file.suffix=='.json':json.loads(file.read_text())
            assert all(line.rstrip()==line for line in file.read_text().splitlines()),file.name
    return {'status':'PASS_BOUNDED_STATIC_DOCUMENT_ARITHMETIC_ONLY','dependency_commit_blob_sha256_bytes_matches':len(deps),
        'exact_source_range_digest_matches':len(cites),'authored_intake_fact_row_bindings':len(facts),'synthetic_resource_boundary_checks':9,
        'original_insertion_geometry_pairs':256,'fixed_base_geometry_pairs':1,'uncovered_original_pairs':255,
        'p1_predicate_value_pairs':65536,'early_pairs':32896,'sift_pairs':32640,'predicate_arithmetic_is_algorithm_proof':False,
        'source_literal_real9_swap_calls':25,'preferred_slots_envelope':[5,4020],'resource_alternative_slots_envelope':[4,3300],
        'DAG_dependency_nodes':9,'review_and_admission_bound':True,'prior_allinit_admitted_cases':1,
        'new_S3_3_qualified_cases':0,'partial_init_provider_contexts_closed':0,
        'native_compile_solver_or_fit':'NOT_RUN_UNKNOWN','artifact_audit_repeated':False,
        'source_control_caps_flags_policy_runtime_CI_accounting_edits':False,'independent_B1_B2_init_credit':0,
        'limits':['Scalar/predicate/source checks do not prove actual body/loop/drop/frame/init/caller binding',
            'Future A, uncensored time and completion memory UNKNOWN; no cap or workflow grant',
            'Prior exact metadata and bounded case do not transfer to new IDs/runs/general rules']}

if __name__=='__main__':print(json.dumps(main(),indent=2))
