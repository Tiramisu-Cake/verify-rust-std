#!/usr/bin/env python3
"""Validate static handoff identities/coverage and write its final file manifest."""
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def sha(b):return hashlib.sha256(b).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
def dump(name,data):(HERE/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')

def main():
    spec=importlib.util.spec_from_file_location('extract4',HERE/'extract_slice.py')
    e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
    git=e.git
    source,static,audit,req,manifest=[read(n) for n in ['SLICE.json','STATIC-VALIDATION.json','SEAM-AUDIT-04.json','CI-REQUEST.json','TEST-MANIFEST.json']]
    head=git('rev-parse','HEAD').decode().strip();tree=git('rev-parse',head+'^{tree}').decode().strip()
    assert head==source['source_sha']==static['source_sha']==audit['head']==req['source_sha']==manifest['source_sha']
    assert tree==source['source_tree']==static['source_tree']==req['source_tree']
    assert git('show','-s','--format=%P',head).decode().strip()==source['base_sha']==static['base_sha']==audit['base']==req['parent']==e.BASE
    assert not git('status','--porcelain')
    assert source['worker15_review']=='PENDING' and source['qualification_status']==req['native_results']=='NOT_RUN'
    assert source['integration_status']=='PENDING' and req['no_authorization_to_dispatch']
    assert audit['status']=='PASS_BOUNDED_STATIC_SEAM_AUDIT' and not audit['errors']
    assert audit['changed_rust_file_count']==107 and len(audit['bound_api_calls'])==93
    assert audit['tool_sha256']==sha((HERE.parent/'seam-audit/check_seams.py').read_bytes())
    assert audit['contracts_sha256']==sha((HERE/'CALL-CONTRACTS-04.json').read_bytes())
    assert static['validator_sha256']==sha((HERE/'validate_slice.py').read_bytes())
    for name,h in source['maps'].items():assert sha((HERE.parent/name).read_bytes())==h,name
    for name,v in source['patches'].items():assert sha((HERE/name).read_bytes())==v['sha256'],name
    assert source['source_parts']['count']==static['owner4_part_hashes_checked']==len(read('SOURCE-PARTS.json')['parts'])==180
    assert read('SOURCE-PARTS.json')['parts']==e.prior.parts_for('4')
    oracle=read('ORACLE-DELTA.json');selected=oracle['selected_complete_fixtures']
    assert len(selected)==99 and len(oracle['stage5_deferred'])==47
    ids={r['id'] for r in selected};assert ids==set(source['selected_complete_fixture_ids'])
    assert not oracle['new_corrections'] and not source['newly_deferred_to5']
    audit5=read('FIXTURE-DEPENDENCY-AUDIT.json')
    assert audit5['source_sha']==head and audit5['source_tree']==tree
    assert audit5['status']=='PASS_BOUNDED_STATIC_FIXTURE_DEPENDENCY_AUDIT'
    assert not audit5['newly_added_fixtures_requiring5'] and not audit5['newly_deferred_to5']
    assert set(audit5['stage4_pairs'])==ids
    for row in selected:
        for key,identity_key in [('input','source'),('golden','golden_identity')]:
            data=git('show',head+':'+row[key]);assert sha(data)==row[identity_key]['sha256']
            assert data==git('show',e.F+':'+row[key])
        fixture=audit5['stage4_pairs'][row['id']]
        assert fixture['candidate_source_identity']['sha256']==row['source']['sha256']
        assert fixture['candidate_golden_identity']['sha256']==row['golden_identity']['sha256']
    obligations=read('DEFERRED-OBLIGATIONS.json')
    for k,n in [('head4_targeted_owner1',7),('head4_targeted_owner3',9),('head4_reassigned_18',18),('head5_fixtures',47)]:
        assert len(obligations[k])==n
    assert obligations['integration_status']=='PENDING' and not obligations['newly_deferred_from4_to5']
    # No future head fixture enters this source, even if a manifest forgot it.
    for row in oracle['stage5_deferred']:
        assert not git('ls-tree',head,'--',row['input']) and not git('ls-tree',head,'--',row['golden'])
    assert 'marker-hook-calls/generated-modifies-no-shadow' in {r['id'] for r in oracle['stage5_deferred']}
    assert {'marker-hook-calls/marked-model-hole','marker-hook-calls/marked-model-initialized'}<=ids
    unique={}
    all_inputs=set()
    for group in manifest['groups']:
        for row in group['selectors']:
            key=group['suite'],group['mode'],row['selector'];unique[key]=row
            all_inputs.add(row['input'])
            for f in row['files']:
                assert sha(git('show',head+':'+f['path']))==f['identity']['sha256'],f['path']
    assert len(unique)==manifest['deduplicated_selector_count']==req['selector_count']==413
    assert sum(r['existing_path_ignore'] for r in unique.values())==9
    assert req['static_counts']==manifest['deduplicated_suite_counts']
    present={p for p in git('ls-tree','-r','--name-only',head,'--','tests/expected/uninit').decode().splitlines() if p.endswith('.rs')}
    assert present<=all_inputs,(present-all_inputs)
    assert {r['input'] for r in selected}<=all_inputs
    assert req['units']==[dict(filter=n,expected=c,result='NOT_RUN') for n,c in [('active_call_tests',9),('immutable_allocations::tests',9),('argument_size_tests',1),('marker_category_tests',1)]]
    independent=read('INDEPENDENT-SEAM-REVIEW.json')
    assert independent['review_binding']['head']==head
    for row in independent['files']:
        assert git('rev-parse',head+':'+row['path']).decode().strip()==row['head_blob']==row['working_blob']
    changed=git('diff','--name-only',e.BASE,head).decode().splitlines();assert len(changed)==204
    report=dict(status='PASS_STATIC_PACKAGE_INTEGRITY',source_sha=head,source_tree=tree,base_sha=e.BASE,
        checks=['exact source/base/tree and clean source','180 owner4 source parts; earlier owners immutable','all source/residual patch hashes and Git-index endpoint trees','107-file seam inventory;44 contracts/93 bound calls;independent production blob binding','99 exact-F complete fixtures and golden identities','7 owner1 +9 owner3 +18 reassigned obligations present, runtime PENDING','47 future5 fixtures absent; no new fixture requires5 by bounded source audit','all currently present expected/uninit inputs in manifest;413 deduplicated selectors/9 pre-existing ignores','original inherited checks and four intentional exact-F entry updates','units9/9/1/1 requested with zero-test refusal'],native_builds_push_CI='NOT_RUN',worker15_review='PENDING',formal_proof_credit='NOT_ESTABLISHED')
    dump('PACKAGE-VALIDATION.json',report)
    dump('MANIFEST.json',dict(source_sha=head,source_tree=tree,base_sha=e.BASE,files=[dict(path=p.name,bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='MANIFEST.json']))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
