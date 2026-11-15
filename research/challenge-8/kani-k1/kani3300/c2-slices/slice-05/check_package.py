#!/usr/bin/env python3
"""Check handoff identities/coverage without executing Rust or changing source."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('package5', HERE/'build_package.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def main():
    s = b.load(HERE/'SLICE.json')
    head, tree = s['source_sha'], s['source_tree']
    assert b.e.git('rev-parse','HEAD').decode().strip() == head
    assert not b.e.git('status','--porcelain')
    assert b.e.git('rev-parse',head+'^{tree}').decode().strip() == tree
    assert s['parents'] == [b.e.BASE] and s['selected_fixture_count'] == 47
    assert not s['E1_imported'] and not s['F7_imported']
    assert s['integration_status']=='PENDING' and s['qualification_status']=='NOT_RUN'
    for p, sha in s['maps'].items():
        assert b.e.digest((HERE.parent/p).read_bytes()) == sha,p
    for c in s['changed_files']:
        for key, ref in [('source',head),('parent',b.e.BASE),('F',b.e.F)]:
            assert c[key] == b.identity(ref,c['path']),c['path']
    rows = b.load(HERE/'ORACLE-DELTA.json')['selected_complete_fixtures']
    ids = {r['id'] for r in rows}
    assert len(rows)==47 and ids==set(s['selected_complete_fixture_ids'])
    dep = b.load(HERE/'FIXTURE-DEPENDENCY-AUDIT.json')
    assert {r['id'] for r in dep['fixtures']} == ids
    for r in dep['fixtures']:
        assert not r['E1_required'] and not r['F7_required']
        assert r['source_sha256'] == b.identity(head,r['input'])['sha256']
        assert r['golden_sha256'] == b.identity(head,r['golden'])['sha256']
    obligations = b.load(HERE/'CLOSURE-OBLIGATIONS.json')
    assert set(obligations['owner1']['integration_head5_fixture_ids']) == ids
    assert set(obligations['owner4']['pending5_fixture_ids']) == ids
    for key in ['owner1','owner4']:
        assert obligations[key]['result']=='NOT_RUN'
    audit = b.load(HERE/'SEAM-AUDIT-05.json')
    assert audit['head']==head and audit['status']=='PASS_BOUNDED_STATIC_SEAM_AUDIT' and not audit['errors']
    assert audit['contracts_sha256'] == b.e.digest((HERE/'CALL-CONTRACTS-05.json').read_bytes())
    for name, suffix in [('DRAFT','DRAFT-CONTRACT'),('INTERIM','INTERIM-CONTRACT')]:
        a = b.load(HERE/f'SEAM-AUDIT-05-{suffix}.json')
        assert a['status']=='FAIL' and a['head']==head
        assert a['contracts_sha256']==b.e.digest((HERE/f'CALL-CONTRACTS-05-{name}.json').read_bytes())
    review = b.load(HERE/'INDEPENDENT-SEAM-REVIEW.json')
    assert review['source_sha']==head and not review['findings']
    assert review['production']['candidate_blob'] == b.identity(head,b.e.LAYOUT)['blob']
    assert s['worker15_review']=='PENDING'
    m = b.load(HERE/'TEST-MANIFEST.json')
    req = b.load(HERE/'CI-REQUEST.json')
    assert m['source_sha']==req['source_sha']==head
    assert m['deduplicated_selector_count']==req['selector_count']==460
    assert m['deduplicated_suite_counts']==req['static_counts']
    assert m['unit_expected_count']==sum(u['expected'] for u in req['units'])==20
    assert m['relevant_units']==req['units']
    assert req['native_results']=='NOT_RUN' and req['no_authorization_to_dispatch']
    mutants = b.load(HERE/'S5-MUTATIONS-READINESS.json')
    assert mutants['source_sha']==head and len(mutants['variants'])==4
    for v in mutants['variants']:
        assert b.e.digest((HERE/v['patch']).read_bytes())==v['patch_sha256']
        assert b.identity(head,v['mutated_path'])['sha256']==v['input_sha256']
        assert v['git_apply_check']=='PASS' and v['native_verdict']=='NOT_RUN' and v['detected']=='PENDING'
    coverage = b.load(HERE/'S5-ORACLE-COVERAGE.json')
    assert coverage['source_sha']==head and len(coverage['rows'])==21
    assert sum(len(r['portable_oracles']) for r in coverage['rows'])==22
    assert b.load(HERE/'DOCS-PARTS.json')['owner5_export_segments']==[]
    for p, v in s['patches'].items():
        assert b.e.digest((HERE/p).read_bytes())==v['sha256']
    # Only owned research directory may be dirty in g0; do not absorb another writer's work.
    import subprocess
    repo = HERE.parents[5]
    assert (repo/'.git').exists(),repo
    g0_dirty = subprocess.check_output(['git','-C',str(repo),'status','--porcelain','--untracked-files=all']).decode().splitlines()
    allowed = str(HERE.relative_to(repo))+'/'
    assert all(row[3:].startswith(allowed) for row in g0_dirty),g0_dirty
    b.dump('PACKAGE-VALIDATION.json',dict(status='PASS_STATIC_PACKAGE',source_sha=head,source_tree=tree,
        exact_fixture_pairs=47,previous_S5_roots=21,portable_oracles=22,mutation_patches_apply=4,
        native_results='NOT_RUN',worker15_review='PENDING',proof_credit='NOT_ESTABLISHED'))
    files = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='MANIFEST.json'}
    b.dump('MANIFEST.json',dict(source_sha=head,source_tree=tree,files_sha256=files))
    print(json.dumps(dict(status='PASS_STATIC_PACKAGE',files=len(files),source_sha=head)))


if __name__=='__main__':
    main()
