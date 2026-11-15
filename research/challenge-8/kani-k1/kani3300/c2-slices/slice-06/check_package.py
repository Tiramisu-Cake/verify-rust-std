#!/usr/bin/env python3
"""Validate the writer handoff identities and coverage; no native tools."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('validation6', HERE/'validate_slice.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def main():
    s = v.e.load(HERE/'SLICE.json')
    assert s['source_sha']==v.HEAD and s['base_sha']==v.e.BASE and s['parents']==[v.e.BASE]
    assert not v.e.git('status','--porcelain')
    assert v.e.git('rev-parse','HEAD').decode().strip()==v.HEAD
    assert v.e.git('rev-parse','HEAD^{tree}').decode().strip()==s['source_tree']
    assert s['production_delta']==0 and not s['F7_imported'] and s['selected_fixture_count']==11
    assert s['qualification_status']=='NOT_RUN' and s['worker15_review']=='PENDING'
    assert s['local_builds_push_CI']=='NOT_RUN'
    for p,sha in s['maps'].items():
        assert v.e.digest((v.ROOT/p).read_bytes())==sha,p
    for c in s['changed_files']:
        for key,ref in [('parent',v.e.BASE),('source',v.HEAD),('F',v.e.F)]:
            assert c[key]==v.identity(ref,c['path']),c['path']
    for name,expected_base,expected_files in [('SEAM-AUDIT-06.json',v.e.BASE,11),
            ('SEAM-AUDIT-06-CUMULATIVE.json',v.e.B1,190)]:
        a=v.e.load(HERE/name)
        assert a['head']==v.HEAD and a['base']==expected_base
        assert a['changed_rust_file_count']==expected_files and not a['errors']
        assert a['status']=='PASS_BOUNDED_STATIC_SEAM_AUDIT'
        assert a['contracts_sha256']==v.e.digest((HERE/'CALL-CONTRACTS-06.json').read_bytes())
        assert a['tool_sha256']==v.e.digest((v.ROOT/'seam-audit/check_seams.py').read_bytes())
    assert (HERE/'CALL-CONTRACTS-06.json').read_bytes()==(v.ROOT/'slice-05/CALL-CONTRACTS-05.json').read_bytes()
    assert v.e.load(HERE/'SEAM-CHECKER-TESTS.json')['tests']==10
    independent=v.e.load(HERE/'INDEPENDENT-SEAM-REVIEW.json')
    assert independent['source_sha']==v.HEAD and not independent['findings']
    assert independent['package_followup']=='PASS_BOUNDED_STATIC_PACKAGE_REVIEW'
    assert not independent['package_findings']
    rows=v.e.load(HERE/'ORACLE-DELTA.json')['selected_complete_fixtures']
    assert {r['id'] for r in rows}==set(s['selected_complete_fixture_ids'])
    deps=v.e.load(HERE/'FIXTURE-DEPENDENCY-AUDIT.json')
    assert {r['id'] for r in deps['fixtures']}==set(s['selected_complete_fixture_ids'])
    assert all(not r['F7_required'] and r['prerequisite_owner']==4 for r in deps['fixtures'])
    for r in deps['fixtures']:
        link=r['source_link']
        text=v.e.git('show',v.HEAD+':'+link['path']).decode()
        for symbol in link['symbols']:
            assert 'fn '+symbol+'(' in text,symbol
    coverage=v.e.load(HERE/'ORACLE-COVERAGE.json')
    assert coverage['mapped_fixtures']==182 and coverage['mapped_test_paths']==364
    assert not v.e.git('diff',v.HEAD,v.e.F,'--','tests','docs')
    residual=v.e.load(HERE/'F7-RESIDUAL.json')
    assert residual['status']=='PASS_EXACT_PINNED_F7_HUNKS_ONLY'
    assert sum(len(r['hunks']) for r in residual['files'])==14
    assert all(r['exact_bytes_equal'] and r['patch_sha256']==r['historical_patch_sha256'] for r in residual['files'])
    assert residual['patch']['alternate_index_target_tree']==v.F_TREE
    for name,row in s['patches'].items():
        assert v.e.digest((HERE/name).read_bytes())==row['sha256']
    m=v.e.load(HERE/'TEST-MANIFEST.json');req=v.e.load(HERE/'CI-REQUEST.json')
    assert m['source_sha']==req['source_sha']==v.HEAD
    assert m['deduplicated_selector_count']==req['selector_count']==471
    assert m['deduplicated_suite_counts']==req['static_counts']
    assert sum(r['expected_passed_if_all_succeed'] for r in req['static_counts'].values())==462
    assert sum(u['expected'] for u in req['units'])==m['unit_expected_count']==20
    assert req['native_results']=='NOT_RUN' and req['no_authorization_to_dispatch']
    # No foreign writer's state is absorbed into this research commit.
    dirty=subprocess.check_output(['git','-C',str(v.G0),'status','--porcelain','--untracked-files=all']).decode().splitlines()
    prefix=str(HERE.relative_to(v.G0))+'/'
    assert all(row[3:].startswith(prefix) for row in dirty),dirty
    # Unified patch context encodes blank source lines as a single space. Keep
    # exact patch bytes (already hash/replay checked); lint non-patch research.
    for staged in [[],['--cached']]:
        subprocess.run(['git','-C',str(v.G0),'diff',*staged,'--check','--',prefix,
            ':(exclude)'+prefix+'*.patch'],check=True)
    v.dump('PACKAGE-VALIDATION.json',dict(status='PASS_STATIC_PACKAGE',source_sha=v.HEAD,
        source_tree=s['source_tree'],changed_paths=25,new_fixture_pairs=11,all_mapped_pairs=182,
        exact_F7_hunks=14,exact_F7_files=5,recomposed_F_tree=v.F_TREE,
        compile_seam_check='PASS_BOUNDED_STATIC',independent_bounded_review='PASS',
        native_tests_builds_push_CI='NOT_RUN',worker15_review='PENDING',proof_credit='NOT_ESTABLISHED',
        whitespace_check='Source PASS; research non-patch PASS. Exact unified patches retain required single-space blank context lines.'))
    files={p.name:v.e.digest(p.read_bytes()) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='MANIFEST.json'}
    v.dump('MANIFEST.json',dict(source_sha=v.HEAD,source_tree=s['source_tree'],files_sha256=files))
    print(json.dumps(dict(status='PASS_STATIC_PACKAGE',files=len(files),source_sha=v.HEAD)))


if __name__=='__main__':
    main()
