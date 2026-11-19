"""Independent offline exact-package checks. No compiler, native or CI entry."""
from pathlib import Path
import ast, hashlib, json, os, re, subprocess, tempfile

OUT = Path(__file__).resolve().parent
G = OUT.parents[5]
P = OUT.with_name('s4-next-impl')
PACKAGE = 'f485968493d3512f3e719825ef4490866808d120'
def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env)
def read(p): return json.loads(p.read_bytes())
def sha(b): return hashlib.sha256(b).hexdigest()
def save(name, obj): (OUT/name).write_text(json.dumps(obj, indent=2)+'\n')
pins = read(P/'PINS.json')
S, C, T = [Path(pins[k]['repo']) for k in ('source','control','tool')]
H = C/'ch8-s1-control'
R = read(P/'CI-REQUEST.json')
def tree(repo, commit):
    return {line.split(b'\t',1)[1].decode():line.split(b'\t',1)[0].decode()
            for line in git(repo,'ls-tree','-r','-z',commit).split(b'\0') if line}
manifest = read(P/'MANIFEST.json')['files']
package_files = tree(G, PACKAGE+':'+str(P.relative_to(G)))
assert set(package_files) == set(manifest)|{'MANIFEST.json'}
assert {str(p.relative_to(P)) for p in P.rglob('*') if p.is_file()} == set(package_files)
for rel in package_files:
    data = git(G,'show',PACKAGE+':'+str((P/rel).relative_to(G)))
    assert data == (P/rel).read_bytes(), rel
    if rel in manifest:
        assert {'sha256':sha(data),'bytes':len(data)} == manifest[rel], rel
identities = {}
for key, repo in [('source',S),('control',C),('tool',T)]:
    pin=pins[key]
    assert git(repo,'rev-parse','HEAD').decode().strip()==pin['sha']
    assert git(repo,'rev-parse','HEAD^{tree}').decode().strip()==pin['tree']
    assert git(repo,'show','-s','--format=%P','HEAD').decode().strip()==pin['sole_parent']
    assert not git(repo,'status','--porcelain')
    identities[key]={k:pin[k] for k in ('sha','tree','sole_parent')}
    available=set(git(repo,'rev-list','--max-count='+str(pin['checkout_depth']),pin['sha']).decode().splitlines())
    assert set(pin['required_commits_available']) <= available
for key, repo in [('source',S),('control',C)]:
    before,after=tree(repo,pins[key]['sole_parent']),tree(repo,pins[key]['sha'])
    changed=sorted(p for p in before.keys()|after.keys() if before.get(p)!=after.get(p))
    identities[key]['changed_paths']=changed
    if key=='source':
        assert changed==['library/core/src/slice/sort/shared/smallsort/verify.rs',
                         'library/core/src/slice/sort/shared/smallsort/verify/sorting_s4_full_lengths_next.rs']
    else:
        old_changed=[p for p in changed if p in before]
        assert old_changed==['.github/workflows/ch8-s2.yml','ch8-s1-control/CI-REQUEST.json',
                            'ch8-s1-control/check_package.py','ch8-s1-control/collect.py','ch8-s1-control/runner.py']
        assert not (before.keys()-after.keys())
old=json.loads(git(C,'show',pins['control']['sole_parent']+':ch8-s1-control/CI-REQUEST.json'))
assert R['rows'][:4]==old['rows'][:4]
assert R['flags']==old['flags'] and R['budgets']==old['budgets']
for row in R['rows'][:4]:
    rid=row['id']; b=R['source_bindings'][rid]
    assert b==old['source_bindings'][rid]
    assert (S/b['file']).read_bytes()==git(S,'show',pins['source']['sole_parent']+':'+b['file'])
for fixture,path in [('s4p2r2-request.json','ch8-s1-control/CI-REQUEST.json'),('s4p2r2-workflow.yml','.github/workflows/ch8-s2.yml')]:
    assert (H/'fixtures'/fixture).read_bytes()==git(C,'show',pins['control']['sole_parent']+':'+path)
assert (H/'CI-REQUEST.json').read_bytes()==(P/'CI-REQUEST.json').read_bytes()
assert (C/'.github/workflows/ch8-s2.yml').read_bytes()==(P/'WORKFLOW.yml').read_bytes()
assert sha((P/'CI-REQUEST.json').read_bytes())==pins['request_sha256']
assert sha((P/'WORKFLOW.yml').read_bytes())==pins['workflow_sha256']
assert git(C,'diff','--name-only',pins['tool']['sha'],'HEAD').decode().splitlines()==R['ci_changed_paths']
assert git(C,'diff','--diff-filter=D','--name-only',pins['tool']['sha'],'HEAD').decode().splitlines()==R['ci_deleted_paths']
assert set(R['ci_payload_sha256'])==set(R['ci_changed_paths'])-set(R['ci_deleted_paths'])-{'ch8-s1-control/CI-REQUEST.json'}
for rel,digest in R['ci_payload_sha256'].items(): assert sha((C/rel).read_bytes())==digest
tables=('changed_file_sha256','cfg_pfc_source_sha256','ordinary_contract_source_sha256','contract_stack_source_sha256','lexical_source_sha256')
for key in tables:
    for rel,digest in R[key].items(): assert sha((S/rel).read_bytes())==digest
for dep in read(P/'DEPENDENCIES.json'):
    data=git(G,'show',dep['commit']+':'+dep['path'])
    assert sha(data)==dep['sha256'] and len(data)==dep['bytes']
    assert git(G,'rev-parse',dep['commit']+':'+dep['path']).decode().strip()==dep['git_blob']
replays=[]
for patch in read(P/'PATCHES.json'):
    repo=S if patch['file'].startswith('SOURCE') else C
    with tempfile.TemporaryDirectory() as d:
        env={**os.environ,'GIT_INDEX_FILE':d+'/index'}
        # Never touch a candidate index/worktree.
        git(repo,'read-tree',patch['base'],env=env)
        git(repo,'apply','--cached',str(P/patch['file']),env=env)
        actual=git(repo,'write-tree',env=env).decode().strip()
        assert actual==patch['expected_tree']==patch['replayed_tree']
        replays.append({'file':patch['file'],'tree':actual})
def normalize(t):
    return t.replace('s4p2r2','s4p3').replace('S4P2R2','S4P3').replace('s4p-2r2','s4p-3').replace('sorting_s4_network_r2','sorting_s4_full_lengths_next')
assert normalize((H/'s4p2r2_campaign.py').read_text())==(H/'s4p3_campaign.py').read_text()
functions=['expected_observation','validate_roles']
for func in functions:
    nodes=[]
    for prefix in ('s4p2r2','s4p3'):
        nodes.append(next(x for x in ast.parse((H/(prefix+'_policy.py')).read_text()).body if isinstance(x,ast.FunctionDef) and x.name==func))
    assert ast.dump(nodes[0])==ast.dump(nodes[1])
for rel in ('runner.py','check_package.py','collect.py'):
    before=git(C,'show',pins['control']['sole_parent']+':ch8-s1-control/'+rel).decode()
    after=(H/rel).read_text()
    lines=after.splitlines(True)
    result=[];i=0
    while i<len(lines):
        if 's4p3' in lines[i] or 'ch8-s4p-3-' in lines[i]:
            line=lines[i]
            # New standalone dispatch blocks; remove their complete suite.
            if (line.lstrip().startswith(('if ','import '))) and not (' in (' in line):
                indent=len(line)-len(line.lstrip());i+=1
                if line.rstrip().endswith(':'):
                    while i<len(lines) and len(lines[i])-len(lines[i].lstrip())>indent:i+=1
                continue
            line=line.replace(', "ch8-s4p-3-v1"','').replace(",'ch8-s4p-3-v1'",'')
            result.append(line);i+=1
        else: result.append(lines[i]);i+=1
    assert ''.join(result)==before,rel
save('STATIC-CHECKS.json',{'status':'PASS','package':PACKAGE,'manifest_entries':len(manifest),
     'identities':identities,'payload_hashes':len(R['ci_payload_sha256']),'source_hash_tables':len(tables),
     'dependency_records':len(read(P/'DEPENDENCIES.json')),'negative_rows_and_bindings':'PARENT_IDENTICAL_FIRST_FOUR',
     'flags_budgets':'PARENT_IDENTICAL','parent_and_stock_patch_replays':replays,
     'campaign':'EXACT_NAMESPACE_COPY','acceptance_and_role_ASTs':'IDENTICAL',
     'shared_runtime_inverse_dispatch':'PARENT_BYTE_IDENTICAL','required_ancestry_within_depth':True,
     'native_CI':'NOT_RUN','proof_credit':'NONE'})
print('Independent static checks PASS',flush=True)
