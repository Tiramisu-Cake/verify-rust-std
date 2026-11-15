#!/usr/bin/env python3
"""Build a static exact-head handoff; no overlay, native tests, network or dispatch."""
import copy
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('extract4',HERE/'extract_slice.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
git,digest=e.git,e.digest
G0_ENTRY='3458504407790eb2fd87e1b9f6e6693b42c57db2'


def dump(name,data): (HERE/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def read(name): return json.loads((HERE/name).read_text())
def identity(ref,path):
    row=git('ls-tree',ref,'--',path).decode().strip()
    if not row:return None
    mode,_,blob=row.split('\t')[0].split()
    return dict(mode=mode,blob=blob,sha256=digest(git('cat-file','blob',blob)))
def directives(ref,path):
    return [x for x in git('show',ref+':'+path).decode().splitlines() if re.match(r'\s*//\s*(kani-flags|compile-flags|ignore|xfail)',x)]


def main():
    head=git('rev-parse','HEAD').decode().strip()
    assert git('show','-s','--format=%P',head).decode().strip()==e.BASE and not git('status','--porcelain')
    tree=git('rev-parse',head+'^{tree}').decode().strip()
    static=read('STATIC-VALIDATION.json');assert static['source_sha']==head and static['status']=='PASS_STATIC_ONLY'
    audit=read('SEAM-AUDIT-04.json');assert audit['head']==head and not audit['errors']
    maps={n:digest((HERE.parent/n).read_bytes()) for n in ['source-map/B1--F.json','source-map/DEPENDENCIES.json','source-map/PRE-F7.json','source-map/SEAMS.md','oracle-map/ORACLE-MAP.json','oracle-map/DOCS-MAP.json','oracle-map/DEPENDENCY-REVIEW.md','ci/QUICK-PLAN.json','slice-03/SOURCE-MAP-CORRECTION.json','slice-03/ORACLE-MAP-CORRECTION.json']}
    parts=e.prior.parts_for('4')
    dump('SOURCE-PARTS.json',dict(source_sha=head,canonical_map='../source-map/B1--F.json',canonical_map_sha256=maps['source-map/B1--F.json'],parts=parts,
        effective_import_correction='../slice-03/SOURCE-MAP-CORRECTION.json',semantics='180 owner4 line parts; neutral UintTy import pair consumed3. All owners1/2/3 parts unchanged. Source attribution, not AST/MIR binding.'))
    selected,deferred=e.fixture_sets()
    def fixture(row,pending=False):
        r=copy.deepcopy(row)
        r.update(source={'path':row['input'],**identity(e.F,row['input'])},golden_identity={'path':row['golden'],**identity(e.F,row['golden'])},
            result='NOT_RUN',integration_status='PENDING',closure_receipt=None)
        for p in [row['input'],row['golden']]:
            assert identity(head,p) is None if pending else identity(head,p)==identity(e.F,p),p
        return r
    selected_records=[fixture(r) for r in selected]
    deferred_records=[fixture(r,True) for r in deferred]
    d1=json.loads((HERE.parent/'slice-01/DEFERRED-OBLIGATIONS.json').read_text())
    d3=json.loads((HERE.parent/'slice-03/DEFERRED-OBLIGATIONS.json').read_text())
    byid={r['id']:r for r in selected_records}
    required1=[r['id'] for r in d1['obligations'] if r['integration_head']==4]
    required3=[r['id'] for r in d3['layout_raw_obligations']]
    reassigned=[r['id'] for r in d3['reassigned_fixtures']]
    assert len(selected)==99 and len(required1)==7 and len(required3)==9 and len(reassigned)==18
    assert set(required1+required3+reassigned)<=set(byid)
    pending=dict(source_sha=head,integration_status='PENDING',integration_heads=[4,5],
        head4_targeted_owner1=[dict(id=id,source_parts='../slice-01/SOURCE-PARTS.json',source_parts_sha256=digest((HERE.parent/'slice-01/SOURCE-PARTS.json').read_bytes()),fixture=byid[id]) for id in required1],
        head4_targeted_owner3=[dict(id=id,source_parts='../slice-03/SOURCE-PARTS.json',source_parts_sha256=digest((HERE.parent/'slice-03/SOURCE-PARTS.json').read_bytes()),fixture=byid[id]) for id in required3],
        head4_reassigned_18=[byid[id] for id in reassigned],
        head5_fixtures=deferred_records,newly_deferred_from4_to5=[],
        historical_receipts_unchanged=['../slice-01/SLICE.json','../slice-02/SLICE.json','../slice-03/ci-43704461635/RESULT.md','../slice-03/ci-43706759714/ACCEPTANCE.md'],
        closure_requires='Exact cumulative head4/5 runtime receipts per unchanged complete fixture/golden; useful SUCCESS and exact intended negatives. Fixture presence, source-token checks and aggregate exit0 do not close obligations.')
    dump('DEFERRED-OBLIGATIONS.json',pending)
    dump('ORACLE-DELTA.json',dict(source_sha=head,canonical_map='../oracle-map/ORACLE-MAP.json',canonical_map_sha256=maps['oracle-map/ORACLE-MAP.json'],
        inherited_correction='../slice-03/ORACLE-MAP-CORRECTION.json',selected_complete_fixtures=selected_records,
        first_executable_head4=99,stage5_deferred=deferred_records,new_corrections=[],
        all_earlier_head4_obligations_present=True,dependency_audit='FIXTURE-DEPENDENCY-AUDIT.json',runtime='NOT_RUN',worker15_area='UNMODIFIED'))
    # Bind external bounded fixture review to actual candidate objects, retaining the original source-path analysis.
    dep=read('FIXTURE-DEPENDENCY-AUDIT.json')
    assert set(dep['stage4_pairs'])==set(byid)
    for id,r in dep['stage4_pairs'].items():
        assert r['input_identity_F']['sha256']==identity(head,r['input'])['sha256']
        assert r['golden_identity_F']['sha256']==identity(head,r['golden'])['sha256']
        r['candidate_source_identity']=identity(head,r['input']);r['candidate_golden_identity']=identity(head,r['golden'])
        # Fill the optional historical map field from the independently read object, not a null placeholder.
        r['pair_identity_F']['golden']=identity(e.F,r['golden'])
    dep.update(source_sha=head,source_tree=tree,base_sha=e.BASE,status='PASS_BOUNDED_STATIC_FIXTURE_DEPENDENCY_AUDIT',
        newly_added_fixtures_requiring5=[],newly_deferred_to5=[],native_compile_and_runtime='NOT_RUN')
    dump('FIXTURE-DEPENDENCY-AUDIT.json',dep)
    docs=json.loads((HERE.parent/'oracle-map/DOCS-MAP.json').read_text())
    dump('DOCS-PARTS.json',dict(canonical_map_sha256=maps['oracle-map/DOCS-MAP.json'],documents=[{'path':d['path'],'added_segments':[r for r in d['added_segments'] if r['owner_slice']==4]} for d in docs['documents'] if any(r['owner_slice']==4 for r in d['added_segments'])],
        adaptations=['rust-feature-support: owner4 prefix placed before inherited owner2 immutable paragraph, shared line184 split; later6 contract modes/link omitted by complete interim sentence By-value aggregates containing.',
            'contracts: complete interim The limitations of + existing uninit link before owner4 apply-to sentence; inherited owner2 Whole immutable paragraph reflowed. Owner6 final link/modes remain absent.'],
        future_scope='Closure5 and general/mode/edge6 prose remains deferred; no whole-file restore.'))
    manifest=json.loads((HERE.parent/'slice-03/TEST-MANIFEST.json').read_text())
    manifest.update(source_sha=head,qualification_kind='TARGETED_INTEGRATION_PLUS_NO_REGRESSION',runtime='NOT_RUN',inherited_from=dict(head=e.BASE,accepted_run='43706759714',manifest_sha256=digest((HERE.parent/'slice-03/TEST-MANIFEST.json').read_bytes())))
    for g in manifest['groups']:
        if g['name']=='common_expected':
            existing={r['input'] for r in g['selectors']}
            for r in selected:
                if r['input'] not in existing:
                    g['selectors'].append(dict(selector='[expected] '+r['input'].removeprefix('tests/'),input=r['input'],files=[dict(path=p,identity=identity(head,p),original_directives=directives(head,p)) for p in [r['input'],r['golden']]],existing_path_ignore=False,result='NOT_RUN'))
            g['selectors'].sort(key=lambda r:r['selector']);g['static_discovery_count']=len(g['selectors'])
            assert len(g['selectors'])==189
        for r in g['selectors']:
            for f in r['files']:
                # Four inherited entry sources intentionally become exact F; every other baseline record is preserved.
                new=identity(head,f['path'])
                if new!=f['identity']:
                    assert f['path'] in {x['input'] for x in selected}
                    assert new==identity(e.F,f['path'])
                f.update(identity=new,original_directives=directives(head,f['path']))
    unique={(g['suite'],g['mode'],r['selector']):r for g in manifest['groups'] for r in g['selectors']}
    counts=Counter(k[0] for k in unique);ignored=Counter(k[0] for k,r in unique.items() if r['existing_path_ignore'])
    manifest['deduplicated_suite_counts']={s:dict(selectors=n,existing_path_ignored=ignored[s],expected_passed_if_all_succeed=n-ignored[s]) for s,n in sorted(counts.items())}
    manifest['deduplicated_selector_count']=len(unique)
    assert len(unique)==413 and sum(ignored.values())==9
    dump('TEST-MANIFEST.json',manifest)
    changed=git('diff','--name-only',e.BASE,head).decode().splitlines()
    changes=[dict(path=p,parent=identity(e.BASE,p),source=identity(head,p),F=identity(e.F,p)) for p in changed]
    patches={k:static[k] for k in ['source.patch','residual-to-F.patch']}
    authority='User stage4 worker14 writer; Git/Python/static review only; local source+g0 commits authorized; no native builds, push, CI or overlay dispatch.'
    dump('INPUTS.json',dict(g0_entry=G0_ENTRY,base=e.BASE,B1=e.B1,F=e.F,source_sha=head,source_tree=tree,maps=maps,
        parent_acceptance='../slice-03/ci-43706759714/ACCEPTANCE.md',assigned_worktree=str(e.REPO),authority=authority,
        task='../../../TASK-KANI3300-C2-SLICES.md',upstream_status='Pinned U+B1; historical snapshot not refreshed or asserted current.'))
    dump('SOURCE-MAP-DELTA.json',dict(canonical_map='../source-map/B1--F.json',sha256=maps['source-map/B1--F.json'],source_sha=head,consumed_owner='4',consumed_parts=parts,
        earlier_owners_unchanged=['1','2','3'],remaining_owners=['5','6','7'],owner6_production_residual=False,
        inherited_import_correction='../slice-03/SOURCE-MAP-CORRECTION.json',source_map_area='UNMODIFIED',adaptations='Exact existing pre-F7 import/writer remains; owner4 resolver/helper shared hunk fully assembled to F.',
        full_logical_stack_recomposition='NOT_RUN',residual_patch_endpoint_only=patches['residual-to-F.patch']))
    dump('SLICE.json',dict(slice=4,name='STORAGE/protocol+F6+Hook',status='READY_FOR_WORKER15_REVIEW_AND_COORDINATOR_CI',
        source_sha=head,source_tree=tree,base_sha=e.BASE,parents=[e.BASE],B1_dependency=e.B1,reference_F=e.F,reference_F_tree='9829702c1aa0ecb73c860fc0ad5451757917d6cb',g0_input=G0_ENTRY,maps=maps,
        changed_files=changes,source_parts=dict(file='SOURCE-PARTS.json',count=len(parts)),borrowed_prerequisite=['Accepted2 wrapper_inner/maybe_uninit_storage/for_storage and imports; accepted3 UintTy neutral import and layout/raw_eq'],
        inherited_adaptations='../slice-03/SLICE.json; exact pre-F7 writer/import retained',adaptations=['Shared resolver hunk no longer needs early-head relocation; complete owner4 body equals F.','Docs interim placement/reflow: DOCS-PARTS.json'],
        F7_imported=False,closure5_imported=False,storage4_imported=True,selected_complete_fixture_ids=[r['id'] for r in selected],
        selected_fixture_count=99,stage5_deferred_fixture_ids=[r['id'] for r in deferred],newly_deferred_to5=[],
        deferred_obligations='DEFERRED-OBLIGATIONS.json',integration_status='PENDING',qualification_kind=manifest['qualification_kind'],qualification_status='NOT_RUN',
        fixture_dependency_audit='FIXTURE-DEPENDENCY-AUDIT.json',compile_seam_audit=dict(tool='../seam-audit/check_seams.py',report='SEAM-AUDIT-04.json',contracts='CALL-CONTRACTS-04.json',manual_review='COMPILE-SEAMS.md',status=audit['status'],synthetic_tests='10 PASS',native_compile='NOT_RUN'),
        bounded_independent_seam_review='INDEPENDENT-SEAM-REVIEW.json',worker15_review='PENDING',local_builds_push_CI='NOT_RUN',cloud_spend=0,formal_proof_credit='NOT_ESTABLISHED',patches=patches,dependents=[5,6,7]))
    units=[dict(filter=n,expected=c,result='NOT_RUN') for n,c in [('active_call_tests',9),('immutable_allocations::tests',9),('argument_size_tests',1),('marker_category_tests',1)]]
    dump('CI-REQUEST.json',dict(source_sha=head,source_tree=tree,parent=e.BASE,status='PREPARED_NOT_DISPATCHED',qualification_kind=manifest['qualification_kind'],recipe='0998b98867:.github/workflows/uninit-quick.yml',runner='ubuntu-24.04',env={'RUST_TEST_THREADS':'2'},job_timeout_minutes=120,test_timeout_seconds=2400,auto_retries=False,test_manifest='TEST-MANIFEST.json',static_counts=manifest['deduplicated_suite_counts'],selector_count=len(unique),units=units,
        targeted_oracles='ORACLE-DELTA.json:selected_complete_fixtures',integration_closure='DEFERRED-OBLIGATIONS.json',native_results='NOT_RUN',worker15_overlay='NOT_PREPARED_BY_WORKER14',no_authorization_to_dispatch=True))
    print(json.dumps(dict(source_sha=head,source_tree=tree,parts=len(parts),changed_paths=len(changed),fixtures=len(selected),selectors=len(unique),suite_counts=manifest['deduplicated_suite_counts']),indent=2))

if __name__=='__main__':main()
