#!/usr/bin/env python3
"""Build the exact-head static writer handoff. No native tools, overlay or dispatch."""
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
spec = importlib.util.spec_from_file_location('extract5', HERE/'extract_slice.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
G0_ENTRY = '045e1925914af2664e6ba5b613de9ed0594e5629'


def dump(name, data):
    (HERE/name).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n')


def load(path):
    return json.loads(path.read_text())


def identity(ref, path):
    row = e.git('ls-tree', ref, '--', path).decode().strip()
    if not row:
        return None
    mode, _, blob = row.split('\t')[0].split()
    return dict(mode=mode, blob=blob, sha256=e.digest(e.git('cat-file', 'blob', blob)))


def main():
    head = e.git('rev-parse', 'HEAD').decode().strip()
    assert e.git('show', '-s', '--format=%P', head).decode().strip() == e.BASE
    assert not e.git('status', '--porcelain')
    tree = e.git('rev-parse', head+'^{tree}').decode().strip()
    static = load(HERE/'STATIC-VALIDATION.json')
    audit = load(HERE/'SEAM-AUDIT-05.json')
    assert static['source_sha'] == audit['head'] == head
    assert static['status'] == 'PASS_STATIC_ONLY' and audit['status'] == 'PASS_BOUNDED_STATIC_SEAM_AUDIT'
    maps = {p:e.digest((HERE.parent/p).read_bytes()) for p in [
        'source-map/B1--F.json', 'source-map/DEPENDENCIES.json', 'source-map/PRE-F7.json',
        'source-map/SEAMS.md', 'oracle-map/ORACLE-MAP.json', 'oracle-map/DOCS-MAP.json',
        'slice-03/SOURCE-MAP-CORRECTION.json', 'slice-03/ORACLE-MAP-CORRECTION.json',
        'slice-04/SLICE.json', 'slice-04/ci-43710024495/ACCEPTANCE.md']}
    rows = copy.deepcopy(e.fixtures())
    for r in rows:
        r.update(candidate_source=identity(head,r['input']), candidate_golden=identity(head,r['golden']),
                 runtime='NOT_RUN', integration_status='PENDING', closure_receipt=None)
        assert r['candidate_source'] == identity(e.F,r['input'])
        assert r['candidate_golden'] == identity(e.F,r['golden'])
    dump('ORACLE-DELTA.json',dict(source_sha=head,canonical_map='../oracle-map/ORACLE-MAP.json',
        canonical_map_sha256=maps['oracle-map/ORACLE-MAP.json'],inherited_correction='../slice-03/ORACLE-MAP-CORRECTION.json',
        selected_complete_fixtures=rows,first_executable_head5=len(rows),new_corrections=[],worker15_area='UNMODIFIED'))
    dump('SOURCE-PARTS.json',dict(source_sha=head,canonical_map='../source-map/B1--F.json',
        canonical_map_sha256=maps['source-map/B1--F.json'],parts=e.parts(),
        earlier_owners_unchanged=[1,2,3,4],source_attribution_only=True))
    dump('SOURCE-MAP-DELTA.json',dict(source_sha=head,consumed_owner=5,consumed_parts=e.parts(),
        earlier_owners_unchanged=[1,2,3,4],remaining_owners=[6,7],owner6_production_residual=False,
        production_file_matches_F=identity(head,e.LAYOUT),borrowed_imports_owner=2,
        pre_F7_adaptation='Inherited unchanged from accepted4; import/writers replaced only7.',source_map_area='UNMODIFIED'))
    d1 = load(HERE.parent/'slice-01/DEFERRED-OBLIGATIONS.json')
    d4 = load(HERE.parent/'slice-04/SLICE.json')
    ids = {r['id'] for r in rows}
    assert ids == set(d4['stage5_deferred_fixture_ids']) == {r['id'] for r in d1['obligations'] if r['integration_head']==5}
    dump('CLOSURE-OBLIGATIONS.json',dict(source_sha=head,source_tree=tree,status='PENDING_EXACT_HEAD5_RUNTIME',
        owner1=dict(historical_head=d1['source_sha'],historical_receipt='../slice-01/SLICE.json',
                    source_parts='../slice-01/SOURCE-PARTS.json',source_parts_sha256=e.digest((HERE.parent/'slice-01/SOURCE-PARTS.json').read_bytes()),
                    integration_head5_fixture_ids=sorted(ids),result='NOT_RUN'),
        owner4=dict(historical_head=e.BASE,historical_acceptance='../slice-04/ci-43710024495/ACCEPTANCE.md',
                    source_parts='../slice-04/SOURCE-PARTS.json',source_parts_sha256=e.digest((HERE.parent/'slice-04/SOURCE-PARTS.json').read_bytes()),
                    pending5_fixture_ids=sorted(ids),result='NOT_RUN'),
        accepted_head4_obligations='Remain accepted exactly as run43710024495; historical records unchanged.',
        closure_requires='Per-fixture exact source/tree/selector/native argv/exits and intended checks, useful SUCCESS, exact negatives. Aggregate exit0, fixture presence and static review do not close obligations.',
        sensitivity='S5-MUTATIONS-READINESS.json; 4/4 execution PENDING',historical_records_rewritten=False))
    # Keep the full accepted cumulative manifest. Add only the 47 complete final pairs.
    manifest = load(HERE.parent/'slice-04/TEST-MANIFEST.json')
    manifest.update(source_sha=head,runtime='NOT_RUN',unit_expected_count=20,inherited_from=dict(head=e.BASE,accepted_run='43710024495',
        manifest_sha256=e.digest((HERE.parent/'slice-04/TEST-MANIFEST.json').read_bytes())))
    manifest['relevant_units'] = load(HERE.parent/'slice-04/CI-REQUEST.json')['units']
    manifest['unit_metadata_correction'] = 'Parent manifest retained18 from owner2; accepted4 CI request/receipt runs20 (9+9+1+1). No new unit on5.'
    for g in manifest['groups']:
        if g['name']=='common_expected':
            existing = {r['input'] for r in g['selectors']}
            for r in rows:
                assert r['input'] not in existing
                files = []
                for p in [r['input'],r['golden']]:
                    flags = [s for s in e.git('show',head+':'+p).decode().splitlines() if re.match(r'\s*//\s*(kani-flags|compile-flags|ignore|xfail)',s)]
                    files.append(dict(path=p,identity=identity(head,p),original_directives=flags))
                g['selectors'].append(dict(selector='[expected] '+r['input'].removeprefix('tests/'),input=r['input'],
                    files=files,existing_path_ignore=False,result='NOT_RUN'))
            g['selectors'].sort(key=lambda r:r['selector'])
            g['static_discovery_count'] = len(g['selectors'])
            assert len(g['selectors']) == 236
        for r in g['selectors']:
            for f in r['files']:
                assert f['identity'] == identity(head,f['path']),f['path']
    unique = {(g['suite'],g['mode'],r['selector']):r for g in manifest['groups'] for r in g['selectors']}
    counts = Counter(k[0] for k in unique)
    ignores = Counter(k[0] for k,r in unique.items() if r['existing_path_ignore'])
    manifest['deduplicated_suite_counts'] = {s:dict(selectors=n,existing_path_ignored=ignores[s],
        expected_passed_if_all_succeed=n-ignores[s]) for s,n in sorted(counts.items())}
    manifest['deduplicated_selector_count'] = len(unique)
    assert len(unique)==460 and sum(ignores.values())==9
    dump('TEST-MANIFEST.json',manifest)
    # Check every old S5 semantic root is represented by unchanged input/golden at cumulative5.
    s5root = HERE.parent.parent/'c2-s5'
    strong = load(s5root/'ORACLE-MAP.json')
    strong_rows = []
    for r in strong['rows']:
        oracles = []
        for b in r['portable_blocks']:
            p = b['input']
            assert identity(head,p) == identity(e.F,p),p
            golden = next(x['golden'] for x in e.prior.prior.effective_oracle()['fixtures'] if x['input']==p)
            assert identity(head,golden) == identity(e.F,golden),golden
            oracles.append(dict(input=p,golden=golden,source=identity(head,p),golden_identity=identity(head,golden),oracle=b))
        strong_rows.append(dict(old_file=r['old_file'],old_pointer=r['old_pointer'],root=r['root'],role=r.get('role',r['root']),
            operation_contract_mode=r['operation_contract_mode'],portable_oracles=oracles,runtime='NOT_RUN'))
    assert len(strong_rows)==21
    dump('S5-ORACLE-COVERAGE.json',dict(source_sha=head,reference_manifest_sha256=e.digest((s5root/'ORACLE-MAP.json').read_bytes()),
        previous_semantic_roots=21,rows=strong_rows,status='PRESENT_EXACT_F_NOT_RUNTIME_QUALIFIED',
        note='8 strong cases + 6 old mode roots represented by7 fixtures +7 composition roots. Replace companion presence is not execution.'))
    sensitivity = load(s5root/'SENSITIVITY-MANIFEST.json')
    mutants = []
    for v in sensitivity['variants']:
        patchpath = s5root/v['patch']
        assert e.digest(patchpath.read_bytes()) == v['patch_sha256']
        assert identity(head,v['mutated_path'])['sha256'] == v['input_sha256']
        with tempfile.TemporaryDirectory(prefix='slice05-mutant-index-') as tmp:
            env = dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
            def run(*args):
                return subprocess.check_output(['git','-C',str(e.REPO),*args],env=env)
            run('read-tree',head)
            subprocess.run(['git','-C',str(e.REPO),'apply','--cached','--check',str(patchpath)],env=env,check=True)
            run('apply','--cached',str(patchpath))
            paths = run('diff','--cached','--name-only',head).decode().splitlines()
            assert paths == [v['mutated_path']]
            mutant_tree = run('write-tree').decode().strip()
        mutants.append(dict(id=v['id'],selector=v['selector'],mutated_path=v['mutated_path'],
            input_sha256=v['input_sha256'],patch='../../c2-s5/'+v['patch'],patch_sha256=v['patch_sha256'],
            alternate_index_tree=mutant_tree,git_apply_check='PASS',predicted_native_verdict=v['predicted_native_verdict'],
            predicted_native_N=v['predicted_native_N'],normal_native_N=v['normal_native_N'],
            expected_mismatch_reason=v['expected_mismatch_reason'],predicted_compiletest_exit=1,
            native_verdict='NOT_RUN',native_N=None,detected='PENDING'))
    assert len(mutants)==4
    dump('S5-MUTATIONS-READINESS.json',dict(source_sha=head,source_tree=tree,status='READY_STATIC_4_OF_4_RUNTIME_PENDING',
        reference_manifest='../../c2-s5/SENSITIVITY-MANIFEST.json',reference_manifest_sha256=e.digest((s5root/'SENSITIVITY-MANIFEST.json').read_bytes()),
        variants=mutants,native_compiletest_argv_template=sensitivity['native_compiletest_argv_template'],
        acceptance=sensitivity['acceptance'],apply='Each fresh alternate source snapshot independently; never cumulative. Actual export is unchanged. Clean native cases must pass first; --force-rerun with unique output dir; completed native verdict/N and intended failure retention required.',
        export_contains_mutations=False,native_execution='NOT_RUN',build_push_CI='NOT_RUN'))
    changes = [dict(path=p,parent=identity(e.BASE,p),source=identity(head,p),F=identity(e.F,p)) for p in sorted(e.extract())]
    patches = {k:static[k] for k in ['source.patch','residual-to-F.patch']}
    dump('INPUTS.json',dict(g0_entry=G0_ENTRY,base=e.BASE,source_sha=head,source_tree=tree,B1=e.B1,F=e.F,maps=maps,
        parent_acceptance='../slice-04/ci-43710024495/ACCEPTANCE.md',authority='Stage5 worker14 writer; local Git/Python/source and research commits only. No local builds, push, CI or publication.',
        upstream_status='Pinned U+B1 retained; no live upstream status claim or rebase.'))
    dump('DOCS-PARTS.json',dict(source_sha=head,canonical_map='../oracle-map/DOCS-MAP.json',
        canonical_map_sha256=maps['oracle-map/DOCS-MAP.json'],owner5_export_segments=[],
        export_docs_changed=[],closure_source_comments=dict(path=e.LAYOUT,F_lines=[481,482,487,488,498,499]),
        research_docs='CLOSURE-SCOPE.md',reason='F docs inventory has zero owner5 prose segments. No new temporary export prose or owner6 modes/cycle/Scope A prose introduced. Exact-F closure comments carry algorithm documentation; closure scope recorded in research.'))
    dump('SLICE.json',dict(slice=5,name='CLOSURE',status='READY_FOR_WORKER15_REVIEW_AND_COORDINATOR_CI',
        source_sha=head,source_tree=tree,base_sha=e.BASE,parents=[e.BASE],B1_dependency=e.B1,reference_F=e.F,
        reference_F_tree='9829702c1aa0ecb73c860fc0ad5451757917d6cb',g0_input=G0_ENTRY,maps=maps,changed_files=changes,
        source_parts=dict(file='SOURCE-PARTS.json',count=2),borrowed_prerequisite=['owner2 rustc_internal/TyCtxt imports and owner4 complete storage/protocol context'],
        inherited_adaptations='Exact accepted4 pre-F7 writer/import unchanged; no new adaptation.',adaptations=[],
        E1_imported=False,F7_imported=False,selected_complete_fixture_ids=sorted(ids),selected_fixture_count=47,
        deferred_obligations='CLOSURE-OBLIGATIONS.json',integration_status='PENDING',qualification_kind='TARGETED_INTEGRATION_PLUS_NO_REGRESSION',
        qualification_status='NOT_RUN',compile_seam_audit=dict(status=audit['status'],report='SEAM-AUDIT-05.json',contracts='CALL-CONTRACTS-05.json',
            manual_review='COMPILE-SEAMS.md',synthetic_tests='10 PASS',native_compile='NOT_RUN'),
        fixture_dependency_audit='FIXTURE-DEPENDENCY-AUDIT.json',bounded_independent_review='INDEPENDENT-SEAM-REVIEW.json',
        worker15_review='PENDING',S5_mutations_readiness='S5-MUTATIONS-READINESS.json',docs='DOCS-PARTS.json',
        local_builds_push_CI='NOT_RUN',cloud_spend=0,formal_proof_credit='NOT_ESTABLISHED',patches=patches,dependents=[6,7]))
    req = load(HERE.parent/'slice-04/CI-REQUEST.json')
    req.update(source_sha=head,source_tree=tree,parent=e.BASE,status='PREPARED_NOT_DISPATCHED',static_counts=manifest['deduplicated_suite_counts'],
        selector_count=len(unique),targeted_oracles='ORACLE-DELTA.json:selected_complete_fixtures',integration_closure='CLOSURE-OBLIGATIONS.json',
        S5_sensitivity='S5-MUTATIONS-READINESS.json; 4/4 required via --force-rerun after clean suite',native_results='NOT_RUN')
    dump('CI-REQUEST.json',req)
    print(json.dumps(dict(source_sha=head,source_tree=tree,files=len(changes),fixtures=len(rows),selectors=len(unique),mutations_apply=4)))


if __name__=='__main__':
    main()
