#!/usr/bin/env python3
"""Independent14 read-only Git/hash/transcript audit; no native tools."""
import hashlib, json, os, re, subprocess, tempfile
from pathlib import Path

G0 = Path('/root/verify-rust-std-kani3300-g0')
PACK = G0/'research/challenge-8/kani-k1/kani3300/ch8-s3/s3-1'
PIN = 'e8a8e5328a941af8a07b778122604b0c9bf4579b'
def git(repo, *args, env=None, binary=False):
    return subprocess.check_output(['git','-C',str(repo),*args],env=env, text=not binary).strip() if not binary else subprocess.check_output(['git','-C',str(repo),*args],env=env)
def sha(data): return hashlib.sha256(data).hexdigest()
def main():
    out={'schema':'independent14-input-audit-v1','package':PIN,'checks':[]}
    def check(name, value):
        assert value, name
        out['checks'].append(name)
    pins=json.loads((PACK/'PINS.json').read_text())
    files=git(G0,'ls-tree','-r','--name-only',PIN,'--',str(PACK.relative_to(G0))).splitlines()
    check('package55_committed_files',len(files)==55)
    for rel in files:check('committed_bytes:'+rel,git(G0,'show',PIN+':'+rel,binary=True)==(G0/rel).read_bytes())
    manifest=(PACK/'MANIFEST.sha256').read_text().splitlines()
    check('package54_manifest_records',len(manifest)==54)
    for line in manifest:
        h,rel=line.split(maxsplit=1);rel=rel.lstrip('*')
        check('manifest:'+rel,sha((PACK/rel).read_bytes())==h)
    for name in ('source','control','tool'):
        p=pins[name];repo=Path(p['worktree'])
        for key,suffix in [('sha',''),('tree','^{tree}'),('parent','^')]:
            check(name+':'+key,git(repo,'rev-parse','HEAD'+suffix)==p[key])
        check(name+':clean',not git(repo,'status','--porcelain=v1'))
    ctl=Path(pins['control']['worktree']); src=Path(pins['source']['worktree'])
    check('request_bytes', (PACK/'CI-REQUEST.json').read_bytes()==(ctl/'ch8-s1-control/CI-REQUEST.json').read_bytes())
    check('workflow_bytes',(PACK/'WORKFLOW.yml').read_bytes()==(ctl/'.github/workflows/ch8-s2.yml').read_bytes())
    for file,key in [('CI-REQUEST.json','request_sha256'),('WORKFLOW.yml','workflow_sha256')]:check(key,sha((PACK/file).read_bytes())==pins[key])
    request=json.loads((PACK/'CI-REQUEST.json').read_text())
    bindings=json.loads((PACK/'ROOT-BINDINGS.json').read_text())
    roles=json.loads((PACK/'ROLE-COVER-MAP.json').read_text())
    check('root_bindings',bindings['source_bindings']==request['source_bindings'])
    check('role_map_request',roles['selected']==[{'id':r['id'],'roles':r['roles']} for r in request['rows']])
    check('nine_roots',len(request['rows'])==9 and [r['id'] for r in request['rows']]==pins['roots'])
    all_roles=[role for row in request['rows'] for role in row['roles']]
    check('selected71_role_sites',len(all_roles)==71)
    check('selected44_cover_sites',sum(role['class']=='cover' for role in all_roles)==44)
    check('six_pfc_three_controls',sum(r['mode']=='PFC' for r in request['rows'])==6)
    for row in request['rows']:
        b=request['source_bindings'][row['id']];text=(src/b['file']).read_text();lines=text.splitlines()
        start=next(i for i,line in enumerate(lines) if line=='fn '+row['id']+'() {')
        end=next(i for i in range(start+1,len(lines)) if lines[i]=='}')
        actual=[(kind,label,i+1) for i in range(start+1,end) for kind,label in re.findall(r'kani::(assert|cover)\(.*?, "([A-Z0-9_]+)"\)',lines[i])]
        check('literal_roles:'+row['id'],actual==[('cover' if x['class']=='cover' else 'assert',x['description'],x['line']) for x in row['roles']])
        for role in row['roles']:check('role:'+role['description'],lines[role['line']-1]==role['source_line'] and sha((src/b['file']).read_bytes())==role['source_sha256'])
        if row['mode']=='PFC':
            attributes='\n'.join(lines[start-3:start])
            check('actual_pfc:'+row['id'],'proof_for_contract('+b['target']+')' in attributes and 'stub' not in attributes)
    batch='library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs'
    old=git(src,'show','bd62e54df1b4749154790aa3db3cc7978f547f75:'+batch,binary=True).decode()
    normalized,count=re.subn(r'assert!\((.*), "(S2_[A-Z0-9_]+)"\)',r'kani::assert(\1, "\2")',old)
    check('exact22_legacy_literal_only',count==22 and normalized==(src/batch).read_text())
    check('all22_map_source',len(roles['all22_legacy_literal_sites'])==22 and all(normalized.splitlines()[x['line']-1]==x['source_line'] and '"'+x['literal']+'"' in x['source_line'] for x in roles['all22_legacy_literal_sites']))
    check('legacy_fixture_exact_bd62',old==(ctl/'ch8-s1-control/fixtures/s3-parent-bd62-batch.rs.txt').read_text())
    for site in json.loads((PACK/'U-SITE-PROPOSAL.json').read_text())['sites']:
        data=(src/site['file']).read_bytes()
        check('disabled_U_site:'+site['file']+':'+str(site['line']),sha(data)==site['sha256'] and data.decode().splitlines()[site['line']-1]==site['source_line'])
    for rel,h in request['changed_file_sha256'].items():check('source_hash:'+rel,sha((src/rel).read_bytes())==h)
    for rel,h in request['ci_payload_sha256'].items():check('control_hash:'+rel,sha((ctl/rel).read_bytes())==h)
    for dep in json.loads((PACK/'INPUTS.json').read_text())['dependencies']:
        check('dependency:'+dep['path'],sha(git(G0,'show',dep['commit']+':'+dep['path'],binary=True))==dep['sha256'])
    patches=json.loads((PACK/'PATCHES.json').read_text())
    if isinstance(patches,dict):patches=patches.get('patches',patches.get('replays',[]))
    check('eight_patch_records',len(patches)==8)
    for item in patches:
        repo=Path(item['repository']); patch=PACK/item['patch']
        check('patch_hash:'+patch.name,sha(patch.read_bytes())==item['sha256'])
        with tempfile.TemporaryDirectory() as d:
            env=dict(os.environ,GIT_INDEX_FILE=d+'/index')
            subprocess.run(['git','-C',str(repo),'read-tree',item['base']],env=env,check=True)
            subprocess.run(['git','-C',str(repo),'apply','--cached',str(patch)],env=env,check=True)
            check('patch_tree:'+patch.name,git(repo,'write-tree',env=env)==git(repo,'rev-parse',item['head']+'^{tree}'))
    ancestry=json.loads((PACK/'ANCESTRY.json').read_text())
    if isinstance(ancestry,dict):ancestry=ancestry.get('checkouts',ancestry.get('checkout_ancestry',[]))
    for item in ancestry:
        check('ancestry:'+item['worktree'],git(Path(item['worktree']),'rev-list','--first-parent','--max-count='+str(item['fetch_depth']),'HEAD').splitlines()==item['chain'])
    for folder,expected,seconds in [('validation-final/',172,601.497913089),('',171,619.748906721)]:
        p=PACK/folder;doc=json.loads((p/'FINAL-VALIDATE.json').read_text())
        for stream in ('stdout','stderr'):check(folder+stream+':hash',sha((p/('FINAL-VALIDATE.'+stream+'.txt')).read_bytes())==doc[stream+'_sha256'])
        check(folder+'elapsed_ns',(doc['monotonic_end_ns']-doc['monotonic_start_ns'])/1e9==seconds==doc['elapsed_seconds'])
        stderr=(p/'FINAL-VALIDATE.stderr.txt').read_text()
        check(folder+'test_count',sum(int(x.split()[1]) for x in stderr.splitlines() if x.startswith('Ran '))==expected)
        check(folder+'PASS',doc['state']=='PASS' and 'FAILED (' not in stderr)
        check(folder+'script',sha((PACK/('run_validate_final_candidate.py' if folder else 'run_final_validate.py')).read_bytes())==doc['script_sha256'])
    final=json.loads((PACK/'validation-final/FINAL-VALIDATE.json').read_text())
    check('final_control_sha',final['control_sha']==pins['control']['sha'])
    check('final_margin',final['margin']==1080/final['elapsed_seconds'] and final['margin']>=1.5)
    out.update(state='PASS',count=len(out['checks']),native='NOT_RUN',proof_credit='NONE')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
