"""Actual existing runner prebuild gate, all four maps retained; no native tools."""
import json,sys,time
from pathlib import Path
from unittest import mock
CONTROL=Path('/root/kani-ch8-s4p-2-r1-control-w13');HERE=CONTROL/'ch8-s1-control'
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import runner,s4p2_policy as policy,check_package
request=runner.load_request();start=time.monotonic();saved=[];original=policy.validate_source
def observe(std,req):
    result=original(std,req);saved.append(result);return result
with mock.patch.object(policy,'validate_source',side_effect=observe):
    source=runner.verify_source(Path('/root/verify-rust-std-ch8-s4p-2-w13'),Path('/root/kani-upstream-ch8-s1'),request,prebuild=True)
assert len(saved)==1 and saved[0]['status']=='STATIC_PASS'
for name,report in saved[0]['reports'].items():
    (OUT/('MAP-'+name.upper()+'.json')).write_text(json.dumps(report,indent=2)+'\n')
rows=saved[0]['reports']['contract_stacks']['cfg_projection_invariance']
keys={'kani'}|{x[6:] for x in request['flags']['RUSTFLAGS'].split()}
assert len(rows)==len({tuple(x['effective_cfg']) for x in rows})==1<<len(keys)==64
legacy=keys-{'kani_smallsort_controls'}
assert sum(set(x['effective_cfg'])<=legacy for x in rows)==32
assert sum('kani_smallsort_sorting' in x['effective_cfg'] for x in rows)==32
from s4p2_contract_stacks import ACTIVE
assert sum(ACTIVE<=set(x['effective_cfg']) for x in rows)==8
result={'source':source,'workflow':check_package.check_yaml(CONTROL/'.github/workflows/ch8-s2.yml'),
    'actual_source_preflight':'runner.verify_source(...,prebuild=True), original validate_source observed exactly once; no lexer/gate/report cache',
    'request_sha256':runner.sha256(runner.REQUEST_PATH),'seconds':time.monotonic()-start,
    'cfg_keys':sorted(keys),'cfg_projections':64,'legacy_contexts_retained':32,'sorting_enabled':32,'ACTIVE_contexts':8,
    'proof_credit':'NONE','native_compile_CI':'NOT_RUN'}
(OUT/'PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'STATIC_PASS','seconds':result['seconds'],'cfg_projections':64,'ACTIVE_contexts':8}),flush=True)
