"""Bounded offline review checks: identities, fixtures, discovery and output matching."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,subprocess
OUT=Path(__file__).resolve().parent
MAIN=Path('/root/verify-rust-std-kani3300-g0')
BASE=MAIN/'research/challenge-8/kani-k1'
INPUT=BASE/'kani3300/wave0/open-pr-slop-inputs-20261119/pr-5172'
SOURCE=Path('/root/kani-pr5172-slop-readonly-20261119')
D=lambda data:hashlib.sha256(data).hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(SOURCE),*args])
def same(values):return len(set(values))==1
r=json.loads((INPUT/'INPUTS.json').read_text())
for path in [INPUT/'INPUTS.json',INPUT/'CONNECTED-PR.json',INPUT/'SOURCE.patch',INPUT/'PR-BODY.snapshot.md',INPUT.parent/'STYLE-UPSTREAM-RULES.snapshot.md']:
    committed=subprocess.check_output(['git','-C',str(MAIN),'show','3dfa44344bd9c91a7307236d3bd9e5c9f6a848cc:'+str(path.relative_to(MAIN))])
    assert committed==path.read_bytes()
assert git('rev-parse','HEAD').decode().strip()==r['head']
assert git('rev-parse','HEAD^{tree}').decode().strip()==r['head_tree']
assert not git('status','--porcelain=v1')
assert git('merge-base',r['head'],r['base_snapshot']).decode().strip()==r['merge_base']
assert set(git('diff','--name-only',r['merge_base'],r['head']).decode().splitlines())==set(r['changed_files'])
for name,item in r['changed_files'].items():
    data=(SOURCE/name).read_bytes()
    assert D(data)==item['sha256'] and len(data)==item['bytes']
    assert git('rev-parse',r['head']+':'+name).decode().strip()==item['git_blob']
assert git('diff','--binary','--full-index',r['merge_base'],r['head'])==(INPUT/'SOURCE.patch').read_bytes()
assert D((INPUT/'SOURCE.patch').read_bytes())==r['diff_sha256']
assert D((INPUT/'PR-BODY.snapshot.md').read_bytes())==r['PR_body_sha256']
assert D((INPUT.parent/'STYLE-UPSTREAM-RULES.snapshot.md').read_bytes())==r['style_sha256']
connected=json.loads((INPUT/'CONNECTED-PR.json').read_text())
assert connected['body']==(INPUT/'PR-BODY.snapshot.md').read_text()
assert connected['head']['sha']==r['head'] and len(connected['files'])==50
directory=SOURCE/'tests/expected/uninit/unresolved-calls'
rs=sorted(directory.glob('*.rs'));expected=sorted(directory.glob('*.expected'))
assert len(rs)==len(expected)==22
assert sum(p.read_text().count('#[kani::proof]') for p in rs)==24
seed_functions=[];flags={};oracles=defaultdict(list)
for path in rs:
    source=path.read_text();flags[path.name]=re.findall(r'^// (?:kani|compile)-flags: (.+)$',source,re.M)
    assert '#[kani::proof]' in source and source.startswith('// Copyright Kani Contributors\n// SPDX-License-Identifier: Apache-2.0 OR MIT\n')
    if path.stem.endswith('-seeded'):
        seed_functions.append(re.search(r'#\[inline\(never\)\]\nfn seed\(\) \{.*?\n\}',source,re.S).group())
    oracle=path.with_suffix('.expected').read_text()
    assert 'VERIFICATION:- ' in oracle and 'Complete - ' in oracle
    assert not any(x in oracle.lower() for x in ('internal compiler error','panicked at','unimplemented!'))
    oracles[oracle].append(path.with_suffix('.expected').name)
assert len(seed_functions)==11 and same(seed_functions)
default_names=[f'{family}-{mode}.expected' for family in ('erased-pointer','fn-pointer','global-escaped','wrapped-pointer') for mode in ('plain','seeded')]
default=(directory/default_names[0]).read_bytes()
assert all((directory/name).read_bytes()==default for name in default_names)
assert 'file_name != "auxiliary"' in (SOURCE/'tools/compiletest/src/main.rs').read_text()
# A direct port of TestCx::contains_lines/contains; execute no upstream driver.
def contains(output,parts):
    return any(all(part.strip() in line for part,line in zip(parts,output[start:])) for start in range(len(output)-len(parts)+1))
def accepts(output,expected):
    lines=output.split('\n');pending=[]
    for line in expected.split('\n'):
        if line.endswith('\\'):pending.append(line[:-1])
        else:
            pending.append(line)
            if not contains(lines,pending):return False
            pending=[]
    return not pending or contains(lines,pending)
assert accepts(default.decode(),default.decode())
assert not accepts('error: compiler failed\npanicked at codegen',default.decode())
assert not accepts(default.decode().replace('calls through function pointers','unrelated error'),default.decode())
# A naive merged initialized/partial oracle can accept swapped safety results.
unsupported=' - Status: FAILURE\n - Description: "Kani does not support memory initialization checks across calls through function pointers. For more information about planned support, see https://github.com/model-checking/kani/issues/3300."'
description=' - Description: "Undefined Behavior: Reading from an uninitialized pointer of type `u32`"'
swapped='\n'.join(['Checking harness initialized...', 'initialized::indirect.safety_check.1',' - Status: FAILURE',description,unsupported,'VERIFICATION:- FAILED','Checking harness partial...','partial::indirect.safety_check.1',' - Status: SUCCESS',description,unsupported,'VERIFICATION:- FAILED','Complete - 0 successfully verified harnesses, 2 failures, 2 total.'])
projections=[]
for family,harness in [('entry-initialized','initialized'),('entry-partial','partial')]:
    text=(directory/(family+'-plain.expected')).read_text().replace('Checking harness check...',f'Checking harness {harness}...')
    text=text.replace('Complete - 0 successfully verified harnesses, 1 failures, 1 total.','Complete - 0 successfully verified harnesses, 2 failures, 2 total.')
    projections.append(accepts(swapped,text))
assert projections==[True,True]
receipt={'status':'STATIC_CHECKS_PASS','task':'3dfa44344bd9c91a7307236d3bd9e5c9f6a848cc','head':r['head'],'tree':r['head_tree'],'base':r['base_snapshot'],
    'changed_files_verified':50,'changed_code_files':6,'test_source_files':22,'test_expected_files':22,'proof_harnesses':24,
    'identical_copy_helpers':11,'shared_default_oracle_candidate_files':default_names,'distinct_expected_contents':len(oracles),
    'flags_by_file':flags,'checks':['all50 published blobs/bytes/SHA256 and exact diff match','body and STYLE snapshot hashes match; connected body equal',
    '22 independently discovered .rs files,24 explicit proof harnesses','all11 copy helpers identical; auxiliary is excluded by actual discovery',
    '8 expected files identical and eligible for existing directory fallback','all expected files require verification + completed inventory; no golden ICE',
    'ported existing substring matcher rejects setup-only output','naive merged initialized/partial expected outputs accept swapped safety statuses; retain separate or bind fully qualified property identities'],
    'native_compiler_CI':'NOT_RUN','source_changed':False,'proof_credit':'NONE'}
(OUT/'STATIC-CHECKS.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('status','changed_files_verified','proof_harnesses','identical_copy_helpers','distinct_expected_contents','native_compiler_CI')}))
