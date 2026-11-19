"""W14 independent offline identities, patch trees and fallback differential.

No compiler, native runner, CI, source writes, publication, or ledger access.
All temporary indices and generated Git objects live outside input repositories.
"""
from pathlib import Path
import hashlib, json, os, subprocess, sys, tempfile, types, time

OUT = Path(__file__).resolve().parent
PACK = OUT.parent / 's4p-2'
G0 = PACK.parents[5]
AUTHOR = '90d861e59f996d35b23a5cb843e311b29efdabf7'
TASK = 'bf3aba53618b759a11d3ff277e88ba66530ec708'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
read = lambda name: json.loads((PACK / name).read_text())
def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env).decode().strip()
def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def identities():
    pins = read('PINS.json')
    manifest = read('MANIFEST.json')['files']
    actual = {str(p.relative_to(PACK)) for p in PACK.rglob('*') if p.is_file()}
    assert actual == set(manifest) | {'MANIFEST.json'}
    for rel, item in manifest.items():
        path = PACK / rel
        assert not path.is_symlink()
        raw = path.read_bytes()
        assert len(raw) == item['bytes'] and sha(raw) == item['sha256'], rel
        assert raw == subprocess.check_output(['git', '-C', str(G0), 'show', AUTHOR + ':' + str(path.relative_to(G0))])
    result = {'author': AUTHOR, 'task': TASK, 'author_packet_files': len(actual),
              'manifest_hashes': len(manifest), 'manifest_sha256': sha((PACK/'MANIFEST.json').read_bytes()), 'pins': {}}
    assert git(G0, 'rev-parse', 'HEAD') == AUTHOR
    for role in ('source', 'control', 'tool'):
        item = pins[role]; repo = Path(item['repo'])
        assert git(repo, 'rev-parse', 'HEAD') == item['sha']
        assert git(repo, 'rev-parse', 'HEAD^{tree}') == item['tree']
        assert git(repo, 'show', '-s', '--format=%P', 'HEAD') == item['sole_parent']
        assert not git(repo, 'status', '--porcelain=v1')
        result['pins'][role] = item
    req = read('CI-REQUEST.json'); control = Path(pins['control']['repo'])
    assert sha((PACK/'CI-REQUEST.json').read_bytes()) == pins['request']['sha256']
    assert (PACK/'CI-REQUEST.json').read_bytes() == (control/'ch8-s1-control/CI-REQUEST.json').read_bytes()
    assert sha((PACK/'WORKFLOW.yml').read_bytes()) == pins['request']['workflow_sha256']
    assert (PACK/'WORKFLOW.yml').read_bytes() == (control/'.github/workflows/ch8-s2.yml').read_bytes()
    paths = git(control, 'diff', '--name-only', req['tool_sha'], 'HEAD').splitlines()
    assert paths == req['ci_changed_paths']
    assert set(req['ci_payload_sha256']) == set(paths)-set(req['ci_deleted_paths'])-{'ch8-s1-control/CI-REQUEST.json'}
    for rel, h in req['ci_payload_sha256'].items(): assert sha((control/rel).read_bytes()) == h, rel
    result.update(payload_files=len(req['ci_payload_sha256']), request_sha256=pins['request']['sha256'], workflow_sha256=pins['request']['workflow_sha256'])
    preservation = {}
    for role, baseline in [('source','985062ebad90cee1e2846b1648cd6a8624d146f6'), ('control','2db5d2c08804036d283cb36450647cd584ee9e10')]:
        repo = pins[role]['repo']; changed=git(repo,'diff','--name-only',baseline,'HEAD').splitlines()
        preservation[role]={'reference':baseline,'changed_paths':changed}
        if role=='source':
            assert changed == ['library/core/src/slice/sort/shared/smallsort/verify.rs', 'library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_network_partition.rs']
            rel=changed[0]; old=subprocess.check_output(['git','-C',repo,'show',baseline+':'+rel])
            assert (Path(repo)/rel).read_bytes().startswith(old)
        else:
            assert all(p.startswith(('ch8-s1-control/s4p2_', 'ch8-s1-control/S4P2-', 'ch8-s1-control/test_s4p2', 'ch8-s1-control/fixtures/s4p-')) or p in ['.github/workflows/ch8-s2.yml','ch8-s1-control/CI-REQUEST.json','ch8-s1-control/check_package.py','ch8-s1-control/collect.py','ch8-s1-control/runner.py'] for p in changed)
    result['preservation']=preservation
    result['status']='PASS'; save('IDENTITIES.json',result)

def replays():
    pins=read('PINS.json'); results=[]
    for row in read('PATCHES.json'):
        repo=Path(pins['source' if row['file'].startswith('SOURCE') else 'control']['repo'])
        assert sha((PACK/row['file']).read_bytes())==row['sha256']
        objects=git(repo,'rev-parse','--path-format=absolute','--git-common-dir')+'/objects'
        with tempfile.TemporaryDirectory() as tmp:
            obj=Path(tmp)/'objects';obj.mkdir()
            env=dict(os.environ,GIT_INDEX_FILE=tmp+'/index',GIT_OBJECT_DIRECTORY=str(obj),GIT_ALTERNATE_OBJECT_DIRECTORIES=objects)
            git(repo,'read-tree',row['base'],env=env)
            git(repo,'apply','--cached','--binary',str(PACK/row['file']),env=env)
            tree=git(repo,'write-tree',env=env)
            assert tree==row['expected_tree']==row['replayed_tree']
            results.append({'patch':row['file'],'base':row['base'],'tree':tree,'status':'INDEPENDENT_EXACT_TREE_PASS'})
    save('PATCH-REPLAYS.json',results)

def fallback_differential():
    pins=read('PINS.json'); control=Path(pins['control']['repo'])
    sys.path.insert(0,str(control/'ch8-s1-control'))
    import runner, s4p2_campaign as final
    old=types.ModuleType('w14_precursor')
    precursor='321c266daf58309ae3eadc6d5c3f358766938ac0'
    raw=subprocess.check_output(['git','-C',str(control),'show',precursor+':ch8-s1-control/s4p2_campaign.py'])
    exec(compile(raw,'precursor:s4p2_campaign.py','exec'),old.__dict__)
    req=runner.load_request(); results=[]
    for label,module in [('precursor',old),('final',final)]:
        for terminal in ({}, {'schema':None}, {'schema':True}, {'schema':8.0}, {'schema':[]}, {'schema':{}}, None):
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                if terminal is not None:module.atomic(root/'receipt.json',terminal)
                original=(root/'receipt.json').read_bytes() if terminal is not None else None
                try:module.fallback(root,req); outcome='ACCEPTED'
                except Exception as exc:outcome=type(exc).__name__+': '+str(exc)
                after=(root/'receipt.json').read_bytes()
                preserved=after==original if original is not None else None
                if terminal is None:assert outcome=='ACCEPTED' and json.loads(after)['s3_campaign']['selected_roots']==8
                elif label=='final':assert outcome.startswith('GlobalFailure:') and preserved
                elif terminal=={}:assert outcome=='ACCEPTED' and not preserved
                results.append({'object':label,'terminal':terminal,'outcome':outcome,'existing_bytes_preserved':preserved})
    changed=git(control,'diff','--name-only',precursor,pins['control']['sha']).splitlines()
    assert changed==['ch8-s1-control/CI-REQUEST.json','ch8-s1-control/s4p2_campaign.py','ch8-s1-control/test_s4p2_boundary.py']
    save('FALLBACK-DIFFERENTIAL.json',{'finding':'AUTHOR-FALLBACK-EMPTY-OBJECT','closure':'INDEPENDENTLY_CLOSED_ON_EXACT_FINAL_OBJECT','precursor':precursor,'final':pins['control']['sha'],'changed_paths':changed,'cases':results})

if __name__=='__main__':
    start=time.monotonic()
    identities(); replays(); fallback_differential()
    print(json.dumps({'status':'PASS','checks':['identities','six isolated index/tree replays','precursor/final fallback differential'],'elapsed_seconds':time.monotonic()-start,'native':'NOT_RUN','proof_credit':'NONE'}))
