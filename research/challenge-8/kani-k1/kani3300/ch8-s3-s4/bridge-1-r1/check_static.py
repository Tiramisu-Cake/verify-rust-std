#!/usr/bin/env python3
"""Read-only package/pin/source-map consistency; never native compile or dispatch."""
import hashlib,json,subprocess,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])
def main():
    pins=read('PINS.json');request=read('CI-REQUEST.json');ancestry=read('ANCESTRY.json');deps=read('DEPENDENCIES.json')
    manifest={}
    for line in (HERE/'MANIFEST.sha256').read_text().splitlines():
        digest,rel=line.split('  ',1);assert rel not in manifest;assert sha((HERE/rel).read_bytes())==digest,rel;manifest[rel]=digest
    actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256' and '__pycache__' not in p.parts}
    assert set(manifest)==actual
    assert sha((HERE/'CI-REQUEST.json').read_bytes())==pins['request']['sha256']
    assert sha((HERE/'WORKFLOW.yml').read_bytes())==pins['request']['workflow_sha256']
    assert request['std_sha']==pins['source']['sha'] and request['std_tree']==pins['source']['tree']
    assert [r['id'] for r in request['rows']]==pins['ordered_rows'] and len(request['rows'])==7
    assert [r['mode'] for r in request['rows']]==['Original']*3+['PFC']+['Original']*3
    assert [r['target'] for r in request['rows']]==[None]*3+['insert_tail']+[None]*3
    for name in ('source','control','tool'):
        item=pins[name];repo=Path(item['worktree']);assert git(repo,'rev-parse','HEAD').decode().strip()==item['sha']
        assert git(repo,'rev-parse','HEAD^{tree}').decode().strip()==item['tree']
        assert not git(repo,'status','--porcelain=v1').strip()
        assert ancestry[name]['sha']==item['sha'] and ancestry[name]['tree']==item['tree']
        if name!='tool':assert git(repo,'rev-list','--parents','-n','1','HEAD').decode().split()[1:]==[item['sole_parent']]
    source=Path(pins['source']['worktree']);control=Path(pins['control']['worktree'])
    assert (control/'ch8-s1-control/CI-REQUEST.json').read_bytes()==(HERE/'CI-REQUEST.json').read_bytes()
    assert (control/'.github/workflows/ch8-s2.yml').read_bytes()==(HERE/'WORKFLOW.yml').read_bytes()
    for rel,record in deps['source'].items():assert sha((source/rel).read_bytes())==record['sha256'],rel
    for rel,digest in request['ci_payload_sha256'].items():assert sha((control/rel).read_bytes())==digest,rel
    for cite in read('SOURCE-CITATIONS.json')['ranges']:
        data=(source/cite['file']).read_bytes();lines=data.decode().splitlines();assert sha(data)==cite['file_sha256']
        assert sha(('\n'.join(lines[cite['start_line']-1:cite['end_line']])+'\n').encode())==cite['range_sha256']
    roles=read('ROLE-ORACLE-COVER.json')['rows']
    for row in roles:
        for role in row['roles']:
            data=(source/role['file']).read_bytes();assert sha(data)==role['source_sha256']
            assert data.decode().splitlines()[role['line']-1]==role['source_line']
    patches=read('PATCHES.json');assert len(patches)==6
    for patch in patches:assert sha((HERE/patch['file']).read_bytes())==patch['sha256'] and patch['replayed_tree']==patch['expected_tree']
    final=read('validation/final-validate.json');summary=read('VALIDATION.json')
    assert final['control_sha']==pins['control']['sha'] and final['control_tree']==pins['control']['tree']
    assert final['exit_code']==0 and final['tracked_clean'] and final['tracked_clean_after']
    assert summary['actual_final_validate_execution_count']==1 and summary['result']['success']
    assert summary['result']['control_sha']==pins['control']['sha'] and summary['result']['request_sha256']==pins['request']['sha256']
    assert summary['margin_at_18_minutes']>=1.5
    repair=read('PRESERVATION.json')['count_repair']
    assert git(control,'diff','--name-only',repair['baseline_control'],pins['control']['sha']).decode().splitlines()==repair['changed_paths_exact']
    baseline=json.loads(git(control,'show',repair['baseline_control']+':ch8-s1-control/CI-REQUEST.json'))
    assert [key for key in request if request[key]!=baseline[key]]==['ci_payload_sha256']
    assert [key for key in request['ci_payload_sha256'] if request['ci_payload_sha256'][key]!=baseline['ci_payload_sha256'][key]]==repair['payload_changed_entries_exact']
    assert git(control,'show',repair['baseline_control']+':.github/workflows/ch8-s2.yml')==(HERE/'WORKFLOW.yml').read_bytes()
    assert sha((HERE/'COUNT-REPAIR.patch').read_bytes())==repair['patch_sha256']
    original=HERE.with_name('bridge-1')
    for name,digest in repair['unchanged_package_maps'].items():
        assert sha((HERE/name).read_bytes())==digest and (HERE/name).read_bytes()==(original/name).read_bytes()
    main_repo=next(path for path in HERE.parents if (path/'.git').exists())
    for item in read('PRECURSORS.json')['historical_immutable']:
        assert sha(git(main_repo,'show',item['commit']+':'+item['path']))==item['sha256']
    baseline_result=read('validation/baseline-count.stdout')
    assert baseline_result['writer_declares']==8 and baseline_result['actual_completed']==7
    assert len(baseline_result['observed'])==9
    assert all(row['actual_local']==row['actual_upload_only']=='ACCEPT' for row in baseline_result['observed'])
    assert read('validation/baseline-count.json')['exit_code']==0
    standalone=read('validation/standalone-portable.json')
    assert standalone['control_sha']==pins['control']['sha'] and standalone['exit_code']==0
    assert 'Ran 1 test' in (HERE/'validation/standalone-portable.stderr').read_text()
    assert (HERE/'validation/standalone-portable.stderr').read_text().rstrip().endswith('OK')
    assert read('validation/targeted-count.json')['exit_code']==0
    tests=read('TEST-LIST.json');assert tests['control_sha']==pins['control']['sha']
    expected=[test for suite in tests['suites'].values() for test in suite['expanded_ids']]
    stderr=(HERE/'validation/final-validate.stderr').read_text()
    observed=re.findall(r'^\w+ \(([^)]+)\) \.\.\. ok$',stderr,re.M)
    assert observed==expected,(len(observed),len(expected))
    assert len(observed)==tests['expected_total']==267
    for name in ('test_selected_count_real_writer_and_both_readers',
                 'test_selected_count_stopped_and_partial_prefix',
                 'test_selected_count_without_completions',
                 'test_selected_count_requires_validated_request_inventory'):
        assert 'test_s34_paths.RealPathWriterTests.'+name in tests['suites']['bridge1']['selection']
    for binding in read('STATIC-GATE-BINDING.json')['code_bindings']:
        data=(control/binding['file']).read_bytes();assert sha(data)==binding['sha256']
        lines=data.decode().splitlines()
        assert sha(('\n'.join(lines[binding['start_line']-1:binding['end_line']])+'\n').encode())==binding['range_sha256']
    closures=read('FINDING-CLOSURES.json')
    assert closures['repaired_control']==pins['control']['sha']
    assert [f['id'] for f in closures['findings']]==['W14-B1-01','W14-B1-02']
    assert not closures['approval_or_GO']
    assert final['head_after']==pins['control']['sha'] and final['control_parents']==[pins['control']['sole_parent']]
    assert summary['source_preflight']['exit_code']==summary['control_preflight']['exit_code']==0
    assert summary['source_preflight']['control_sha']==summary['control_preflight']['control_sha']==pins['control']['sha']
    print(json.dumps({'status':'STATIC_PACKAGE_PASS','files_hashed':len(manifest),'dependency_source_files':len(deps['source']),
                      'source_ranges':len(read('SOURCE-CITATIONS.json')['ranges']),'native_compile_proof_cost_fit':'NOT_RUN','proof_credit':'NONE'},sort_keys=True))
if __name__=='__main__':main()
