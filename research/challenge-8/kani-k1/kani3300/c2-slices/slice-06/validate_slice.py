#!/usr/bin/env python3
"""Exact-head extraction/residual/coverage handoff. No native tools or dispatch."""
import copy
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extract6', HERE/'extract_slice.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
ROOT = HERE.parent
G0 = HERE.parents[5]
ENTRY = '3d494fa76ab4cce73f00065f6076f0f2c5bd34be'
HEAD = '3f5242bb1539fb88196d7e503b722f0905f2b46c'
F_TREE = '9829702c1aa0ecb73c860fc0ad5451757917d6cb'
U = '0aac16ef62da9e9d5645782d458593e5d78143ba'


def dump(name, obj):
    (HERE/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')


def identity(ref, path):
    entry = e.git('ls-tree', ref, '--', path).decode().strip()
    if not entry:
        return None
    mode, kind, blob = entry.split('\t')[0].split()
    return dict(mode=mode, blob=blob, sha256=e.digest(e.git('cat-file', kind, blob)))


def replay(start, patch, target):
    with tempfile.TemporaryDirectory(prefix='slice06-index-') as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp)/'index'))
        cmd = ['git', '-C', str(e.REPO)]
        subprocess.run(cmd+['read-tree', start], env=env, check=True)
        subprocess.run(cmd+['apply', '--cached', '--check', str(patch)], env=env, check=True)
        subprocess.run(cmd+['apply', '--cached', str(patch)], env=env, check=True)
        result = subprocess.check_output(cmd+['write-tree'], env=env).decode().strip()
        assert result == e.git('rev-parse', target+'^{tree}').decode().strip()
        return result


def main():
    assert e.git('rev-parse', 'HEAD').decode().strip() == HEAD
    assert not e.git('status', '--porcelain')
    assert e.git('show', '-s', '--format=%P', HEAD).decode().strip() == e.BASE
    assert e.git('merge-base', e.B1, HEAD).decode().strip() == e.B1
    tree = e.git('rev-parse', HEAD+'^{tree}').decode().strip()
    assert e.git('rev-parse', e.F+'^{tree}').decode().strip() == F_TREE
    changed = e.git('diff', '--name-only', e.BASE, HEAD).decode().splitlines()
    assert set(changed) == set(e.paths()) and len(changed) == 25
    assert not e.git('diff', e.BASE, HEAD, '--', 'kani-compiler', 'library', '.github', 'Cargo.lock')
    changes = []
    for path in changed:
        source, final = identity(HEAD, path), identity(e.F, path)
        assert source == final, path
        changes.append(dict(path=path, parent=identity(e.BASE, path), source=source, F=final))
    subprocess.run(['git', '-C', str(e.REPO), 'diff', '--check', e.BASE, HEAD], check=True)

    # Pin inputs without modifying source-map/oracle-map or historical evidence.
    inputs = ['source-map/B1--F.json', 'source-map/DEPENDENCIES.json', 'source-map/PRE-F7.json',
              'source-map/SEAMS.md', 'oracle-map/ORACLE-MAP.json', 'oracle-map/DOCS-MAP.json',
              'slice-03/SOURCE-MAP-CORRECTION.json', 'slice-03/ORACLE-MAP-CORRECTION.json',
              'f7/F7-RESIDUAL.json', 'f7/EXTRACTION-PLAN.md', 'slice-05/SLICE.json',
              'slice-05/TEST-MANIFEST.json', 'slice-05/ci-43715788377/ACCEPTANCE.md']
    maps = {p:e.digest((ROOT/p).read_bytes()) for p in inputs}
    reading = ['../../TASK-KANI3300-C2-SLICES.md', '../../PLAN-KANI3300-C2.md',
               '../../AUDIT-REPORT-KANI3300-PART1-R4-RU.md', '../c2-s5/ORACLE-MAP.md',
               '../c2-s5/ORACLE-MAP.json', '../c2-s5/MODE-COVER-MAP.md',
               '../c2-s5/DISCOVERY-DELETION-MAP.md', '../c2-s5/SENSITIVITY-MANIFEST.json',
               '../c2-s6/CONTROL-MAP.md', '../c2-s6/DOCS-SCOPE-MAP.md',
               '../c2-s6/ci-43656920767/ACCEPTANCE.md', '../c2-gatea/ACCEPTANCE.md',
               '../c2-gateb/RESULT.md']
    dump('READ-INPUTS.json', dict(g0_input=ENTRY, files=[dict(path=p,
        sha256=e.digest((ROOT/p).read_bytes())) for p in reading], maps=maps,
        evidence_assurance='Existing coordinator/source-reported acceptance; no new runtime or proof credit.'))

    # Stronger than a path allowlist: every complete zero-context patch must equal
    # its pinned historical F7 patch byte for byte, including metadata and headers.
    plan = e.load(ROOT/'f7/F7-RESIDUAL.json')
    residual_paths = set(e.git('diff', '--name-only', HEAD, e.F).decode().splitlines())
    assert residual_paths == {r['path'] for r in plan['files']}
    residual_rows = []
    for r in plan['files']:
        path = r['path']
        historical = e.git('diff', '--no-ext-diff', '--unified=0',
                           r['historical_delta_base'], r['historical_delta_target'], '--', path)
        actual = e.git('diff', '--no-ext-diff', '--unified=0', HEAD, e.F, '--', path)
        assert e.digest(historical) == r['historical_patch_sha256'], path
        assert actual == historical, path
        assert [s for s in actual.decode().splitlines() if s.startswith('@@')] == r['hunks']
        assert identity(e.F, path)['blob'] == r['F_blob']
        residual_rows.append(dict(path=path, hunks=r['hunks'], patch_sha256=e.digest(actual),
            historical_patch_sha256=r['historical_patch_sha256'], exact_bytes_equal=True,
            head6=identity(HEAD,path), F=identity(e.F,path)))
    patch_records = {}
    for name, start, end in [('source.patch', e.BASE, HEAD), ('residual-to-F.patch', HEAD, e.F)]:
        patch = e.git('diff', '--binary', '--full-index', start, end)
        (HERE/name).write_bytes(patch)
        patch_records[name] = dict(sha256=e.digest(patch), alternate_index_target_tree=replay(start,HERE/name,end))
    dump('F7-RESIDUAL.json', dict(status='PASS_EXACT_PINNED_F7_HUNKS_ONLY', source_sha=HEAD,
        source_tree=tree, F=e.F, F_tree=F_TREE, canonical='../f7/F7-RESIDUAL.json',
        canonical_sha256=maps['f7/F7-RESIDUAL.json'], files=residual_rows,
        patch=patch_records['residual-to-F.patch'], production_applied=False,
        structural_isolation_credit='NOT_ESTABLISHED_BEFORE_F7'))
    dump('RECOMPOSE.json', dict(source_sha=HEAD,source_tree=tree,reference_F=e.F,
        reference_F_tree=F_TREE, residual='F7-RESIDUAL.json',
        alternate_index_recomposition='EXACT_F_TREE', patches=patch_records,
        native_execution='NOT_RUN', stage7_commit_created=False))

    oracle = e.load(ROOT/'oracle-map/ORACLE-MAP.json')
    selected = copy.deepcopy(e.fixtures())
    for r in selected:
        assert identity(e.BASE,r['input']) is None and identity(e.BASE,r['golden']) is None
        r.update(candidate_source=identity(HEAD,r['input']), candidate_golden=identity(HEAD,r['golden']),
                 native_result='NOT_RUN', qualification='PENDING_COORDINATOR_EXACT_HEAD6_CI')
        assert e.git('show', HEAD+':'+r['golden']).decode().splitlines() == r['oracle']['literal_golden']
    dump('ORACLE-DELTA.json', dict(source_sha=HEAD,canonical_map='../oracle-map/ORACLE-MAP.json',
        canonical_map_sha256=maps['oracle-map/ORACLE-MAP.json'], selected_complete_fixtures=selected,
        selected_pairs=11, semantic_oracles_or_directives_changed=False,
        golden_precision='Preserve F literal-only edge oracles; no new exact property-count claim.',
        runtime='NOT_RUN', worker15_area='UNMODIFIED'))
    # Every final mapped fixture, including prior composition/modes/semantic cases.
    coverage = []
    for r in oracle['fixtures']:
        assert identity(HEAD,r['input']) == identity(e.F,r['input']),r['input']
        assert identity(HEAD,r['golden']) == identity(e.F,r['golden']),r['golden']
        coverage.append(dict(id=r['id'], input=r['input'], golden=r['golden'], exact_F=True,
            parent_present=identity(e.BASE,r['input']) is not None))
    for r in oracle['paths']:
        assert identity(HEAD,r['path']) == r['identities']['F'],r['path']
    assert not e.git('diff', HEAD, e.F, '--', 'tests', 'docs')
    composition = [r for r in coverage if r['id'].startswith(('part1-composition/', 'root-composition/', 'contract-modes/'))]
    assert all(r['parent_present'] for r in composition)
    dump('ORACLE-COVERAGE.json', dict(source_sha=HEAD, mapped_fixtures=len(coverage),
        mapped_test_paths=len(oracle['paths']), all_tests_and_docs_equal_F=True,
        fixtures=coverage, composition_and_modes_inherited=composition,
        additional_composition_residual=[], historical_correction_preserved='../slice-03/ORACLE-MAP-CORRECTION.json',
        note='Exact tree identities, not new execution. Canonical early-head attributions retain the accepted slice03 correction.'))
    # Resolve links from current source map, rather than stale embedded navigation hashes.
    source = e.load(ROOT/'source-map/B1--F.json')
    visitor = 'kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs'
    links = [dict(path=f['path'], hunk_id=h['id'], parts=h['parts'])
        for f in source['files'] if f['path']==visitor for h in f['hunks']
        if h['id']=='B1--F:19:009']
    const = next(p for p in links[0]['parts'] if p['start']==420)
    assert const['count']==5 and const['owner']=='4'
    assert identity(HEAD,visitor)==identity(e.BASE,visitor)==identity(e.F,visitor)
    assert not e.load(ROOT/'source-map/DEPENDENCIES.json')['slices']['6']['source_parts']
    dump('SOURCE-MAP-DELTA.json', dict(source_sha=HEAD, consumed_owner=6,production_parts=[],
        production_changed_paths=[], production_prerequisites_owner=4, ordinary_union_constant=links,
        projected_raw_and_unsized='Inherited owner4 unchanged; visitor/layout/operation/runtime blobs equal accepted5.',
        canonical_map_sha256=maps['source-map/B1--F.json'], earlier_owners_unchanged=[1,2,3,4,5],
        remaining_owner=7, pre_F7_adaptations='Exact PRE-F7 import and both cache writers inherited unchanged.',
        navigation_note='oracle source_features embedded hunk hashes are historical; this delta binds the current canonical source map.'))
    docs = e.load(ROOT/'oracle-map/DOCS-MAP.json')
    doc_rows = []
    for d in docs['documents']:
        assert identity(HEAD,d['path'])==identity(e.F,d['path'])
        lines = e.git('show',HEAD+':'+d['path']).decode().splitlines()
        for s in d['added_segments']:
            assert lines[s['F_line']-1][s['start_column_0']:s['end_column_0']]==s['text']
        doc_rows.append(dict(path=d['path'], candidate=identity(HEAD,d['path']),
            final_F=identity(e.F,d['path']), owner6_segments=[s for s in d['added_segments'] if s['owner_slice']==6],
            owner6_removed_U_lines=[s for s in d['removed_U_lines'] if s['owner_slice']==6],
            earlier_owner_segments_verified=True))
    dump('DOCS-PARTS.json',dict(source_sha=HEAD,canonical_map_sha256=maps['oracle-map/DOCS-MAP.json'],
        documents=doc_rows, changed_paths=e.DOCS, shared_file_delta='docs-remainder.patch',
        reflow_owner=6, new_prose=False, final_docs_equal_F=True))

    # Inherit every selector from accepted5; add exactly the eleven new edge cases.
    manifest = copy.deepcopy(e.load(ROOT/'slice-05/TEST-MANIFEST.json'))
    manifest.update(source_sha=HEAD,runtime='NOT_RUN',inherited_from=dict(head=e.BASE,
        accepted_run='43715788377', manifest_sha256=maps['slice-05/TEST-MANIFEST.json']))
    for g in manifest['groups']:
        if g['name']=='common_expected':
            for r in selected:
                assert r['input'] not in {x['input'] for x in g['selectors']}
                files=[]
                for p in [r['input'],r['golden']]:
                    directives=[s for s in e.git('show',HEAD+':'+p).decode().splitlines()
                        if re.match(r'\s*//\s*(kani-flags|compile-flags|ignore|xfail)',s)]
                    files.append(dict(path=p,identity=identity(HEAD,p),original_directives=directives))
                g['selectors'].append(dict(selector='[expected] '+r['input'].removeprefix('tests/'),
                    input=r['input'],files=files,existing_path_ignore=False,result='NOT_RUN'))
            g['selectors'].sort(key=lambda r:r['selector'])
            g['static_discovery_count']=len(g['selectors'])
            assert len(g['selectors'])==247
        for r in g['selectors']:
            r['result']='NOT_RUN'
            for f in r['files']:
                assert f['identity']==identity(HEAD,f['path']),f['path']
    unique={(g['suite'],g['mode'],r['selector']):r for g in manifest['groups'] for r in g['selectors']}
    counts=Counter(k[0] for k in unique)
    ignores=Counter(k[0] for k,r in unique.items() if r['existing_path_ignore'])
    manifest['deduplicated_suite_counts']={s:dict(selectors=n,existing_path_ignored=ignores[s],
        expected_passed_if_all_succeed=n-ignores[s]) for s,n in sorted(counts.items())}
    manifest['deduplicated_selector_count']=len(unique)
    assert len(unique)==471 and sum(ignores.values())==9
    dump('TEST-MANIFEST.json',manifest)
    sensitivity=e.load(ROOT/'slice-05/S5-MUTATIONS-READINESS.json')
    for v in sensitivity['variants']:
        assert identity(HEAD,v['mutated_path'])==identity(e.BASE,v['mutated_path'])
        assert identity(HEAD,v['mutated_path'])['sha256']==v['input_sha256']
    dump('S5-INHERITED-ACCEPTANCE.json',dict(source_sha=HEAD, accepted_head=e.BASE,
        accepted_run='43715788377', acceptance='../slice-05/ci-43715788377/ACCEPTANCE.md',
        acceptance_sha256=maps['slice-05/ci-43715788377/ACCEPTANCE.md'],
        all_mutated_paths_parent_identical=True, all_previous_oracles_parent_identical=True,
        source_reported_mutation_acceptance='4/4; fourth accepted by coordinator manual review, as recorded',
        new_mutation_execution='NOT_RUN', proof_credit='NOT_ESTABLISHED'))
    req=copy.deepcopy(e.load(ROOT/'slice-05/CI-REQUEST.json'))
    req.update(source_sha=HEAD, source_tree=tree, parent=e.BASE, status='PREPARED_NOT_DISPATCHED',
        static_counts=manifest['deduplicated_suite_counts'],selector_count=len(unique),
        targeted_oracles='ORACLE-DELTA.json:selected_complete_fixtures',
        integration_closure='All11 E1 fixture selectors; legal SUCCESS and exact intended read/unsized boundary failures.',
        S5_sensitivity='Inherited accepted4/4 at unchanged head5 production/oracles; S5-INHERITED-ACCEPTANCE.json',
        native_results='NOT_RUN', compile_seams=['SEAM-AUDIT-06.json','SEAM-AUDIT-06-CUMULATIVE.json'])
    dump('CI-REQUEST.json',req)
    audits=[]
    for name in ['SEAM-AUDIT-06.json','SEAM-AUDIT-06-CUMULATIVE.json']:
        a=e.load(HERE/name)
        assert a['head']==HEAD and a['status']=='PASS_BOUNDED_STATIC_SEAM_AUDIT' and not a['errors']
        assert a['contracts_sha256']==e.digest((HERE/'CALL-CONTRACTS-06.json').read_bytes())
        audits.append(dict(path=name,sha256=e.digest((HERE/name).read_bytes()),
            base=a['base'],changed_rust_files=a['changed_rust_file_count'],bound_calls=len(a['bound_api_calls'])))
    dump('INPUTS.json',dict(g0_input=ENTRY,U=U,B1=e.B1,base=e.BASE,source_sha=HEAD,source_tree=tree,
        F=e.F,F_tree=F_TREE,maps=maps,authority='worker14 stage6 writer; local Git/Python and commits only; Cloud $0',
        upstream_status='Pinned U+B1 retained; no rebase or new live upstream claim.'))
    dump('SLICE.json',dict(slice=6,name='E1_AND_REMAINING_SCOPE_A_DOCS',
        status='READY_FOR_WORKER15_REVIEW_AND_COORDINATOR_CI',source_sha=HEAD,source_tree=tree,
        base_sha=e.BASE,parents=[e.BASE],B1_dependency=e.B1,reference_F=e.F,reference_F_tree=F_TREE,
        g0_input=ENTRY,maps=maps,changed_files=changes,production_delta=0,
        selected_fixture_count=11,selected_complete_fixture_ids=[r['id'] for r in selected],
        source_map='SOURCE-MAP-DELTA.json',oracle_map='ORACLE-DELTA.json',full_coverage='ORACLE-COVERAGE.json',
        docs='DOCS-PARTS.json',borrowed_prerequisite=['owner4 ordinary-union constant V420-424, projected raw/address and unsized guards'],
        inherited_adaptations='PRE-F7 import and both cache writers, unchanged from accepted5; removed only7',
        adaptations=[],F7_imported=False,F7_residual='F7-RESIDUAL.json',patches=patch_records,
        compile_seam_audits=audits,synthetic_seam_checker_tests='10 PASS',
        native_compile='NOT_RUN',qualification_status='NOT_RUN',integration_status='PENDING',
        qualification_kind='TARGETED_EDGE_INTEGRATION_PLUS_CUMULATIVE_NO_REGRESSION',
        worker15_review='PENDING',bounded_independent_review='INDEPENDENT-SEAM-REVIEW.json',
        local_builds_push_CI='NOT_RUN',cloud_spend=0,formal_proof_credit='NOT_ESTABLISHED',dependents=[7]))
    dump('STATIC-VALIDATION.json',dict(status='PASS_STATIC_ONLY',source_sha=HEAD,source_tree=tree,
        parent=e.BASE,changed_paths=25,production_delta=0,exact_F_new_fixture_pairs=11,
        full_mapped_fixture_pairs=len(coverage),complete_tests_docs_equal_F=True,
        exact_historical_F7_patches=5,residual_hunks=sum(len(r['hunks']) for r in residual_rows),
        alternate_index_F_tree=F_TREE,compile_seam_audits=audits,selector_count=len(unique),
        native_builds_verifier_CI_push='NOT_RUN',proof_credit='NOT_ESTABLISHED'))
    print(json.dumps(dict(status='PASS_STATIC_ONLY',source_sha=HEAD,source_tree=tree,
        fixtures=11,all_mapped_fixtures=len(coverage),selectors=len(unique),exact_F7_files=5,
        exact_F7_hunks=sum(len(r['hunks']) for r in residual_rows))))


if __name__ == '__main__':
    main()
