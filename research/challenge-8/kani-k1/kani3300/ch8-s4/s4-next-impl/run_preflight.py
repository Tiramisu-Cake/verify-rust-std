"""Existing source preflight, uncached. No compiler, verifier or CI."""
from pathlib import Path
import json,sys,time
from unittest import mock
OUT=Path(__file__).resolve().parent;C=Path('/root/kani-ch8-s4-next-control-w15');H=C/'ch8-s1-control'
sys.path.insert(0,str(H))
import runner,check_package,s4p3_policy as policy
request=runner.load_request();saved=[];start=time.monotonic();original=policy.validate_source
def observe(std,req):
    result=original(std,req);saved.append(result);return result
with mock.patch.object(policy,'validate_source',side_effect=observe):source=runner.verify_source(Path('/root/verify-rust-std-ch8-s4-next-w15'),Path('/root/kani-upstream-ch8-s1'),request,prebuild=True)
assert len(saved)==1 and saved[0]['status']=='STATIC_PASS'
for name,report in saved[0]['reports'].items():
    assert json.loads((OUT/('MAP-'+name.upper()+'.json')).read_text())==json.loads(json.dumps(report))
rows=saved[0]['reports']['contract_stacks']['cfg_projection_invariance'];keys={'kani'}|{x[6:] for x in request['flags']['RUSTFLAGS'].split()}
assert len(rows)==len({tuple(x['effective_cfg']) for x in rows})==1<<len(keys)==64
from s4p3_contract_stacks import ACTIVE
assert sum(set(x['effective_cfg'])<=keys-{'kani_smallsort_controls'} for x in rows)==32
assert sum(ACTIVE<=set(x['effective_cfg']) for x in rows)==8
result={'status':'STATIC_PASS','source':source,'domain_correspondence':saved[0]['domain_correspondence'],
    'request_sha256':runner.sha256(H/'CI-REQUEST.json'),'workflow':check_package.check_yaml(C/'.github/workflows/ch8-s2.yml'),
    'seconds':time.monotonic()-start,'method':'runner.verify_source(prebuild=True); actual validate_source observed exactly once; no token/gate cache',
    'cfg_projections':64,'legacy_contexts':32,'ACTIVE_contexts':8,'native_compile_CI':'NOT_RUN','proof_credit':'NONE'}
(OUT/'PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'seconds':result['seconds'],'request_sha256':result['request_sha256']}),flush=True)
