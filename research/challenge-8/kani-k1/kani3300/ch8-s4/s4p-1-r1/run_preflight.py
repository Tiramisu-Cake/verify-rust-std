import datetime, hashlib, json, os, sys, time
from pathlib import Path
from unittest import mock
CONTROL=Path('/root/kani-ch8-s4p-1-r1-control-w13');HERE=CONTROL/'ch8-s1-control'
OUT=Path('/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s4/s4p-1-r1')
sys.path.insert(0,str(HERE))
import runner, s4p_policy as policy, check_package
request=runner.load_request();start=time.monotonic();saved=[]
original=policy.validate_source
def observe(std,req):
    result=original(std,req);saved.append(result);return result
with mock.patch.object(policy,'validate_source',side_effect=observe):
    source=runner.verify_source(Path('/root/verify-rust-std-ch8-s4p-1-w13'),Path('/root/kani-upstream-ch8-s1'),request,prebuild=True)
assert len(saved)==1 and saved[0]['status']=='STATIC_PASS'
for name,report in saved[0]['reports'].items():
    (OUT/('MAP-'+name.upper()+'.json')).write_text(json.dumps(report,indent=2)+'\n')
rows=saved[0]['reports']['contract_stacks']['cfg_projection_invariance']
assert len(rows)==len({tuple(x['effective_cfg']) for x in rows})==32
from s4p_contract_stacks import ACTIVE
assert sum('kani_smallsort_sorting' in x['effective_cfg'] for x in rows)==16
assert sum(ACTIVE<=set(x['effective_cfg']) for x in rows)==4
result={'source':source,'workflow':check_package.check_yaml(CONTROL/'.github/workflows/ch8-s2.yml'),
    'actual_source_preflight':'runner.verify_source(...,prebuild=True); spy calls original validate_source exactly once and retains returned reports',
    'request_sha256':runner.sha256(runner.REQUEST_PATH),'seconds':time.monotonic()-start,
    'cfg_projections':32,'sorting_enabled':16,'ACTIVE_contexts':4,'proof_credit':'NONE','native_compile_CI':'NOT_RUN'}
(OUT/'PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'STATIC_PASS','seconds':result['seconds'],'cfg_projections':32,'ACTIVE_contexts':4}),flush=True)
