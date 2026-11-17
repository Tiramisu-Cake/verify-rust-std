#!/usr/bin/env python3
"""Read-only origin-partitioned S1-08 candidate replay. --write writes only HERE.

No compiler, verifier, network, raw logs or full evidence archives. The two
unchanged collectors replay separately over their retained bounded JSON-only
compact artifacts. No synthetic request and no mixed collector roots.
"""
import argparse
import collections
import copy
import hashlib
import functools
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[7]
BASE = HERE.parents[2]
S108 = HERE.parents[1]
MANIFEST_SHA = '3191ea3ad753f2c5057413aae775aceb36db3895277829772d3443d5e7ed517e'
TASK = 'dad394c5948af7dde9f6195b5e7d461f6b040a8d'
SOURCE = '99e8456d200fff1299ee5756279cddb23921dc65'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
PREFIX = '/home/runner/work/kani/kani/export/'
STD = Path('/root/verify-rust-std-ch8-s1-08-w13')
CONTROL = Path('/root/kani-ch8-s1-08-cell-retry-fix-w13')
S107 = BASE / 's1-07/run-43923266772'
RUNS = {'original': 44095954742, 'retry': 44128268928}
INTAKES = {'original': '6d300f3ab9801c808612b562588af06e0f7b4ff9', 'retry': '0beb690dfa99e4524de71b2ffc311fe7d7556cc1'}
HEADS = {'original': '21592884db439389364b416dea1515bfa9d8018e', 'retry': '4336dfed5af21660b9ac82907107be839ce13977'}
REQUESTS = {'original': '77ae11136368b592f044da3f881408c87453d9bf5f28c3fd1a5eb0fcc1431c7e', 'retry': '3e61b78c0f527ea5966ca33ff5d05ad354c1846ae995ce320f361ae795f6f2d8'}


def clean(x):
    if isinstance(x,dict):
        return {k:clean(v) for k,v in x.items() if k not in ('stdout','stderr')}
    return [clean(v) for v in x] if isinstance(x,list) else x


def index(items,key):
    need(isinstance(items,list) and all(isinstance(x,dict) for x in items),'index list')
    result={x[key]:x for x in items}
    need(len(result)==len(items) and all(result),'duplicate/missing '+key)
    return result


def runpath(origin):
    return S108 / ('run-'+str(RUNS[origin]))


def groupdir(origin,gid):
    return runpath(origin)/'evidence'/('groups' if origin=='retry' else '')/gid


def file_ref(path, commit=None):
    return {'path':str(path.relative_to(ROOT)), 'sha256':sha(path.read_bytes()),
            **({'commit':commit} if commit else {})}


def verify_inputs():
    m = read(HERE/'INPUTS.json')
    need(sha((HERE/'INPUTS.json').read_bytes())==MANIFEST_SHA and m['task_commit']==TASK and m['intakes']==INTAKES and m['source']==SOURCE and m['tool']==TOOL,
         'manifest identity')
    for rel,x in m['files'].items():
        p=ROOT/rel
        need(p.is_file() and not p.is_symlink() and sha(p.read_bytes())==x['sha256'], 'input SHA:'+rel)
        need(p.read_bytes()==blob(ROOT,x['commit'],rel), 'committed bytes:'+rel)
    return m


def origin_replay(origin):
    """Process-isolated unchanged collector; never runs intake.main/runner.main."""
    run=runpath(origin); q=read(run/'CI-REQUEST.json')
    need(sha((run/'CI-REQUEST.json').read_bytes())==REQUESTS[origin], 'origin request')
    need((run/'CI-REQUEST.json').read_bytes()==blob(CONTROL,HEADS[origin],'ch8-s1-control/CI-REQUEST.json'), 'executed request')
    for path,pin in q['ci_payload_sha256'].items():
        need(sha(blob(CONTROL,HEADS[origin],path))==pin, 'producer payload:'+path)
    for p in sorted((run/'replay-control').rglob('*')):
        if p.is_file():
            need(p.read_bytes()==blob(CONTROL,HEADS[origin],'ch8-s1-control/'+str(p.relative_to(run/'replay-control'))), 'executed collector tree')
    sys.path.insert(0,str(run/'replay-control'))
    import runner
    import collect
    need(runner.load_request()==q, 'request loader')
    roots=sorted((run/'artifacts').iterdir())
    actual=clean(collect.collect(roots,q))
    expected=read(run/('runner-collected.json' if origin=='original' else 'collector-exact.json'))
    need(actual==clean(expected), 'exact collector replay:'+origin)
    selected=[r for r in actual['rows'] if r.get('status')=='OBSERVED' and r.get('outcome')=='RECORDED']
    plan=read(BASE/'s1-08-composition-plan/INPUTS.json')[origin]
    need({r['id'] for r in selected}==set(plan['selected_row_ids']), 'fixed origin partition')
    need(actual['missing_groups']==(['cell-u34'] if origin=='original' else
         [g['id'] for g in q['execution_groups'] if g['id']!='cell-u34']), 'origin missing groups retained')
    return {'origin':origin, 'run_id':RUNS[origin], 'attempt':1, 'request_sha256':REQUESTS[origin],
            'collector':'EXACT_READ_ONLY_MATCH', 'selected_rows':len(selected),
            'missing_groups':actual['missing_groups'], 'collector_receipt_sha256':sha(encoded(actual)),
            'immutable_receipt':file_ref(run/('runner-collected.json' if origin=='original' else 'collector-exact.json'),INTAKES[origin])}


def load(replay_origins=True):
    m=verify_inputs(); plan=read(BASE/'s1-08-composition-plan/INPUTS.json')
    b={'plan':plan,'manifest':m,'origins':{},'replays':{}}
    for origin in RUNS:
        if replay_origins:
            p=subprocess.run([sys.executable,'-I','-B',str(HERE/'replay.py'),'--origin',origin],
                             capture_output=True,text=True,timeout=180)
            need(p.returncode==0,'origin replay:'+origin+':'+p.stderr[-2000:])
            b['replays'][origin]=json.loads(p.stdout)
        run=runpath(origin);q=read(run/'CI-REQUEST.json')
        groups={g['id']:{n:read(groupdir(origin,g['id'])/n) for n in
                ('receipt.json','compile/receipt.json','export.json','properties.json','binding-metadata.json')}
                for g in q['execution_groups'] if g['id'] in plan[origin]['selected_groups']}
        b['origins'][origin]={'request':q,'groups':groups,
            'collected':clean(read(run/('runner-collected.json' if origin=='original' else 'collector-exact.json'))),
            'identity':read(run/'run-identity.json'), 'artifacts':read(run/'artifacts-metadata.json'),
            'jobs':read(run/'jobs-metadata.json'), 'provenance':read(run/'PROVENANCE.json')}
    verify_inputs()
    return b


@functools.lru_cache(None)
def helpers():
    inv=module('s108_reviewed_inventory',S107/'accept/replay.py')
    native=module('s108_reviewed_native',S107/'accept/native.py')
    source=module('s108_reviewed_source',S107/'accept/pfc.py')
    u=module('s108_reviewed_U',S107/'accept-u/replay.py')
    sem=module('s108_reviewed_semantic',S107/'accept/semantic.py')
    un=module('s108_reviewed_unreachable',BASE/'s1-06/run-43889560779/accept-v2/unreachable.py')
    v3=module('s108_reviewed_qualify',S107/'accept-v3/replay.py')
    return inv,native,source,u,sem,un,v3


@functools.lru_cache(None)
def source_text(path):
    return blob(STD,SOURCE,path).decode()


def compatibility(b):
    old,new=(b['origins'][o]['request'] for o in RUNS)
    allowed={'schema','rows','ci_payload_sha256','budgets','reservations','batch_policy','ci_changed_paths',
             'workflow_stages','artifact_policy','execution_scope'}
    delta={k for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
    gates={'only_reviewed_delta_fields':delta==allowed}
    a,c=(index(q['rows'],'id') for q in (old,new))
    gates['full_rows_equal_except_cell_timeout']=set(a)==set(c) and all(
        {k:v for k,v in a[r].items() if k!='timeout_seconds'}=={k:v for k,v in c[r].items() if k!='timeout_seconds'}
        and a[r]['timeout_seconds']==600 and c[r]['timeout_seconds']==(1200 if r in b['plan']['retry']['selected_row_ids'] else 600) for r in a)
    gates['all_other_semantic_request_fields_equal']=all(old.get(k)==new.get(k) for k in old.keys()|new.keys() if k not in allowed)
    gates['role_map_equal']=(runpath('original')/'ROLE-MAP.json').read_bytes()==(runpath('retry')/'ROLE-MAP.json').read_bytes()
    transfer=read(runpath('retry')/'COMPATIBILITY.json')
    actual_changes=[]
    for path in sorted(set(git(CONTROL,'ls-tree','-r','--name-only',HEADS['retry'],'ch8-s1-control','.github/workflows').decode().splitlines()) |
                       set(git(CONTROL,'ls-tree','-r','--name-only',HEADS['original'],'ch8-s1-control','.github/workflows').decode().splitlines())):
        def get(rev):
            exists=git(CONTROL,'ls-tree',rev,'--',path)
            return blob(CONTROL,rev,path) if exists else None
        x,y=get(HEADS['original']),get(HEADS['retry'])
        if x!=y:actual_changes.append({'path':path,'old_sha256':sha(x) if x is not None else None,'retry_sha256':sha(y) if y is not None else None})
    gates['exact_reviewed_control_delta']=actual_changes==transfer['control_changed_paths'] and all(transfer['gates'].values())
    # Complete values are pinned, rather than a wildcard approval of these keys.
    gates['exact_reviewed_request_delta']=transfer['request_delta']=={k:{'old':old.get(k),'retry':new.get(k)} for k in sorted(delta)}
    cfg=[];binary=[]
    for origin,ob in b['origins'].items():
        for gid,g in ob['groups'].items():
            rec,exp=g['receipt.json'],g['export.json']
            binary.append({'origin':origin,'group':gid,'before':{k:v['sha256'] for k,v in rec['tool_fingerprints_before']['binaries'].items()},
                'after':{k:v['sha256'] for k,v in rec['tool_fingerprints_after']['binaries'].items()},'versions':exp['tools']})
            cfg.append({'origin':origin,'group':gid,'configuration':exp['configuration'],'target':exp['target'],
                        'features':exp['enabled_unstable_features'],'tool':exp['kani_commit'],'dirty':exp['kani_commit_dirty']})
    gates['protected_binary_digest_version_all_origins']=bool(binary) and all(
        x['before']==x['after']==binary[0]['before'] and x['versions']==binary[0]['versions'] for x in binary)
    gates['actual_configuration_solver_checks_equal']=bool(cfg) and all(
        {k:v for k,v in x.items() if k not in ('origin','group')}==
        {k:v for k,v in cfg[0].items() if k not in ('origin','group')} for x in cfg)
    gates['cell_actual_semantics_reviewed_equal']=all(x['equal'] for x in transfer['actual_semantic_configuration'].values())
    return {'schema':'s108-composite-compatibility-v1','gates':gates,'status':'PASS' if all(gates.values()) else 'PENDING',
        'immutable_intake_compatibility':file_ref(runpath('retry')/'COMPATIBILITY.json',INTAKES['retry']),
        'request_delta':transfer['request_delta'],'control_delta':actual_changes,'protected_binaries':binary,
        'assurance':'Exact reviewed deltas and unchanged pinned producer rules; no new broad compiler audit',
        'unknowns':transfer['unknown_fields'],'independent_proof_credit':'NONE'}


def validate_partition(b):
    plan=b['plan'];keys=[]
    need(plan==read(BASE/'s1-08-composition-plan/INPUTS.json'),'composition decision identity')
    for origin,ob in b['origins'].items():
        q=ob['request'];p=plan[origin];i=ob['identity']
        need(sha(encoded(q))==b['manifest']['canonical_requests'][origin], 'request canonical identity:'+origin)
        need(i['id']==RUNS[origin] and i['run_attempt']==1 and i['head_sha']==HEADS[origin]
             and i['head_commit']['tree_id']==p['tree'] and i['status']=='completed'
             and i['conclusion']==('failure' if origin=='original' else 'success'), 'terminal origin identity:'+origin)
        need(git(CONTROL,'rev-parse',HEADS[origin]+'^{tree}').decode().strip()==p['tree'],'control tree')
        control=p['control_sha'] if origin=='original' else p['reviewed_control_sha']
        need(git(CONTROL,'rev-parse',control+'^{tree}').decode().strip()==p['tree'],'reviewed tree')
        need(git(CONTROL,'rev-parse',HEADS[origin]+'^')==git(CONTROL,'rev-parse',control+'^'),'trigger/reviewed parent')
        need(q['std_sha']==SOURCE and q['tool_sha']==TOOL,'source/tool origin')
        need(set(ob['groups'])==set(p['selected_groups']), 'atomic predetermined groups:'+origin)
        jobs=ob['jobs']['jobs']
        need(len(jobs)==(14 if origin=='original' else 1) and sum(j['conclusion']=='success' for j in jobs)==(13 if origin=='original' else 1),'terminal job partition')
        for gid in ob['groups']:
            job,=[j for j in jobs if j['name'].endswith('('+gid+')')]
            need(job['run_id']==RUNS[origin] and job['status']=='completed' and job['conclusion']=='success' and all(s['conclusion']=='success' for s in job['steps']),'complete selected job')
        rows=index(q['rows'],'id');observed=index(ob['collected']['rows'],'id')
        need(set(observed)==set(rows),'collector declared rows')
        for gid,g in ob['groups'].items():
            gs=next(x for x in q['execution_groups'] if x['id']==gid)
            need(g['receipt.json']['state']=='COMPLETE','incomplete group:'+origin+':'+gid)
            need(g['receipt.json']['request_sha256']==REQUESTS[origin], 'foreign group request')
            selectors=[rows[r]['selector'] for r in gs['row_ids']]
            need(len(selectors)==len(set(selectors)) and g['receipt.json']['selectors']==selectors,'group selectors')
            need(set(index(g['export.json']['harnesses'],'name'))==set(index(g['properties.json']['harnesses'],'name'))==set(selectors),'whole group inventory')
            need(set(index(g['binding-metadata.json']['rows'],'row_id'))==set(gs['row_ids']),'whole native group')
            for rid in gs['row_ids']:
                r=observed[rid]
                need(r['status']=='OBSERVED' and r['outcome']=='RECORDED' and r['group']==gid
                     and r['selector']==rows[rid]['selector'] and r['variant']==rows[rid]['variant'],'foreign/unknown row:'+rid)
                keys.append(rid)
        need(set(r for gid in ob['groups'] for r in next(g['row_ids'] for g in q['execution_groups'] if g['id']==gid))==set(p['selected_row_ids']), 'fixed selected rows')
    need(len(keys)==len(set(keys)) and set(keys)==set(index(b['origins']['original']['request']['rows'],'id')), '35 unique declared row partition')
    return keys


def group_identity(b,origin,gid):
    """Narrow replacement of old fixed-run/600s group plumbing; rules unchanged."""
    inv,native,_,_,_,_,_=helpers()
    ob=b['origins'][origin];q=ob['request'];g=ob['groups'][gid]
    spec=next(s for s in q['execution_groups'] if s['id']==gid)
    rec,m,exp,comp=[g[k] for k in ('receipt.json','binding-metadata.json','export.json','compile/receipt.json')]
    timeout=1200 if origin=='retry' else 600
    source={k:q[k] for k in ('std_sha','std_tree','tool_sha','tool_tree','changed_file_sha256')}
    need(m['group_id']==rec['group']==gid and m['request_sha256']==rec['request_sha256']==comp['request_sha256']==REQUESTS[origin], 'group native/request')
    need(m['std_sha']==rec['std_sha']==comp['std_sha']==SOURCE and m['tool_sha']==rec['tool_sha']==comp['tool_sha']==TOOL,'group source/tool')
    need(m['source_before']==m['source_after']==rec['source_before']==rec['source_after']==source,'source snapshots')
    need(m['state']=='CAPTURED_AVAILABLE_FIELDS' and m['native_metadata_state']=='CAPTURED' and m['errors']==[], 'native capture')
    need(m['compiler_identity_status']=='UNKNOWN_NOT_EXPORTED_BY_PINNED_PRODUCER' and m['compilation_id'] is None,'retained native limits')
    need(m['requirements_sha256']==q['binding_metadata_requirements_sha256'] and m['expected_flags_and_checks']==q['flags'],'native flags/requirements')
    need(m['invocation_id']==rec['invocation_id'] and re.fullmatch('[0-9a-f]{32}',m['invocation_id']),'native invocation')
    need(m['variant']==rec['variant']==spec['variant'] and m['unwind']==rec['unwind']==spec['unwind'],'variant/unwind')
    expected_hashes=dict(q['changed_file_sha256']);patch=q['variants'].get(spec['variant'])
    if patch:expected_hashes.update(patch['changed_file_sha256'])
    need(m['source_under_test']==rec['source_under_test']=={'base_std_sha':SOURCE,'variant':spec['variant'],'file_sha256':expected_hashes,'patch_sha256':patch['sha256'] if patch else None},'effective source/variant')
    selectors=[next(r['selector'] for r in q['rows'] if r['id']==rid) for rid in spec['row_ids']]
    argv=[PREFIX.replace('/export/','/tool/')+'scripts/kani','verify-std']
    for f in q['flags']['unstable']:
        if f!='export-json':argv+=['-Z',f]
    argv+=['--no-assert-contracts','--jobs=1','--harness-timeout',str(timeout)+'s']
    for s in selectors:argv+=['--harness',s]
    argv+=['--exact','--default-unwind',str(spec['unwind']),'-Z','export-json','--export-json',
           '/home/runner/work/_temp/ch8-s1-receipts/groups/'+gid+'/export.json','--output-format=regular',PREFIX+'library','--cbmc-args','--object-bits','12']
    need(rec['argv']==m['argv']==argv and comp['selectors']==rec['selectors']==selectors,'exact argv')
    need(m['effective_cfg']==rec['effective_cfg']==' '.join('--cfg='+x for x in q['flags']['cfg']),'effective cfg')
    need(m['configuration_sha256']==sha(json.dumps({'flags':q['flags'],'cfg':rec['effective_cfg'],'argv':argv},sort_keys=True).encode()),'configuration SHA')
    need(inv.snapshot_gate(rec)=='MATCH' and m['binaries_before']==rec['tool_fingerprints_before'] and m['binaries_after']==rec['tool_fingerprints_after'],'snapshot/shutdown')
    ex=rec['execution'];need(m['execution']==ex and not rec['phase_limited'] and ex['signal'] is None
        and all(ex[k] is False for k in ('timed_out','stdout_truncated','stderr_truncated','output_truncated'))
        and not ex.get('termination_reason') and all(not x.get(k) for x in (m,rec) for k in ('original_exception','execution_exception')), 'execution exceptions/exits')
    need(ex['original_exit_code']==(1 if any(r['expected']=='DETECTED' for r in q['rows'] if r['id'] in spec['row_ids']) else 0),'original exit')
    need(comp['state']=='COMPLETE' and comp['boundary']=='STOCK_INITIAL_EXPORT_OBSERVED','compile boundary')
    need(exp['run_state']=='COMPLETE' and exp['outcome']=={'kind':'COMPLETED'} and exp['harness_timeout_s']==timeout
         and exp['kani_commit']==TOOL and exp['kani_commit_dirty'] is False and exp['target']=='x86_64-unknown-linux-gnu','stock completion')
    need(exp['harness_selection']=={'requested_filters':selectors,'exact':True,'unmatched_filters':[],'matched_count':len(selectors)},'exact selection')
    need(g['properties.json']['state']=='COMPLETE' and g['properties.json']['error'] is None,'rich completeness')
    need(exp['configuration']['checks']=={'memory_safety':True,'overflow':True,'unwinding':True,'undefined_function':True,
         'assertion_reach_checks':True,'ignore_global_asm':False,'extra_pointer_checks':False,'assert_contracts':False,'prove_safety_only':False}
         and exp['configuration']['cbmc_args']==['--object-bits','12'] and exp['configuration']['coverage_enabled'] is False
         and set(exp['enabled_unstable_features'])==set(q['flags']['unstable']), 'checks/solver features')
    for e in m['native_metadata']:
        _,checks=native._records(e)
        need(e['state']=='CAPTURED' and checks['sha256_valid'] and checks['bytes_valid'] and checks['json_valid'],'native content')
    return g


def pfc_bundle(b,origin):
    inv,native,src,_,_,_,_=helpers()
    p=module('s108_PFC_'+origin,S107/'accept-pfc/replay.py')
    p.SOURCE=SOURCE;p.CONTROL_SHA=HEADS[origin];p.REQUEST_SHA=REQUESTS[origin];p.STD=STD;p.CONTROL=CONTROL
    p.helpers=lambda:(inv,native,src)
    ob=b['origins'][origin];q=ob['request']
    sources={path:source_text(path) for path in set(q['changed_file_sha256'])|{p.SHARED,'library/core/src/cell.rs','library/core/src/marker.rs'}}
    producer={}
    for role,(path,start,end) in p.PRODUCER_SPECS.items():
        raw=blob(CONTROL,TOOL,path)
        need(raw==blob(CONTROL,HEADS[origin],path),'unchanged PFC producer:'+path)
        producer[role]={'commit':TOOL,'path':path,'sha256':sha(raw),'start_line':start,'end_line':end,'lines':raw.decode().splitlines()[start-1:end]}
    symbols=[h['contract']['contracted_function_name'] for g in ob['groups'].values() for h in g['export.json']['harnesses'] if isinstance(h['attributes']['kind'],dict) and 'ProofForContract' in h['attributes']['kind']]
    dictionary,demangler=p.demangle(symbols)
    bundle={**ob,'sources':sources,'patches':{k:blob(CONTROL,HEADS[origin],'ch8-s1-control/'+v['patch']).decode() for k,v in q['variants'].items()},
            'producer':producer,'dictionary':dictionary,'demangler':demangler}
    # The earlier intake supplied this navigation field after collector replay.
    # Derive it from this origin's exact native row; never use historical evidence.
    bundle['collected']=copy.deepcopy(ob['collected'])
    for gs in q['execution_groups']:
        if gs['id'] not in ob['groups']:continue
        meta=ob['groups'][gs['id']]['binding-metadata.json']
        for mr in meta['rows']:
            cr=next(r for r in bundle['collected']['rows'] if r['id']==mr['row_id'])
            cr['evidence']={'invocation_id':meta['invocation_id'],'native_harness_records':mr['native_harness_records']}
    p.source_identity(bundle)
    def group_adapter(bundle,gs):
        group_identity(b,origin,gs['id'])
        return p.effective_source(bundle,gs['variant'])
    p.group_identity=group_adapter
    return p,bundle


def source_certificate(spec):
    src=spec['source'];text=source_text(src['file']);lines=text.splitlines()
    need(sha(text.encode())==src['sha256'] and src.get('commit',SOURCE)==SOURCE,'role source hash')
    for s in src.get('sites',[]):
        need('\n'.join(lines[s['line']-1:s.get('end_line',s['line'])]).strip()==s['text'].strip() and sha(s['text'].encode())==s['sha256'],'role source site')
    call=src.get('invocation')
    if call:need('\n'.join(lines[call['line']-1:call['line']-1+len(call['text'].splitlines())])==call['text'],'root macro invocation')
    return text


def property_ref(row,p):
    return {'id':p['id'],'class':p['class'],'status':p['status'],'description':p['description'],
            'file':p['file'],'line':p['line'],'location_display':p['location_display'],
            'sha256':sha(encoded(p)),'origin_key':row['origin_key']}


def exact_property_site(prop,file,lines):
    stem=prop['id'].rsplit('.',2)[0]
    return (prop.get('display_id')==prop['id'] and prop['file']==helpers()[0].EXPORT_PREFIX+file
        and str(prop['line']).isdigit() and int(prop['line']) in lines
        and re.fullmatch(re.escape(file)+':'+str(prop['line'])+r':[1-9][0-9]* in function '+re.escape(stem),prop['location_display']) is not None)


def role_binding(row,role,props):
    text=source_certificate(role);src=role['source'];stem=lambda p:p['id'].rsplit('.',2)[0]
    candidates=[p for p in props if p['class']=='assertion' and p['description']==role['expected_description']
                and p['file']==helpers()[0].EXPORT_PREFIX+src['file'] and int(p['line']) in src['allowed_property_lines']]
    if role['binding_kind']=='EXACT_SUCCESS_SEMANTIC_SET':
        fn=row['selector'].rsplit('::',1)[0]+'::inactive::<'
        candidates=[p for p in candidates if stem(p).startswith(fn)]
        calls=src['helper_callsites'];lines=text.splitlines()
        need(len(calls)==3 and all(re.search(r'\binactive\s*\(',lines[n-1]) for n in calls),'inactive source calls')
        instances={stem(p) for p in candidates}
        # Exact full fresh instance set: two closures tied to fresh source coordinates,
        # plus the explicit MaybeUninit/KeyLess monomorphization. No historical IDs.
        prefix=helpers()[0].EXPORT_PREFIX+src['file']
        closure_lines=[calls[0],calls[1]-1]
        need('let effectful = |a: &u8, b: &u8|' in lines[calls[1]-2], 'effectful comparator source')
        need(all(any('{closure@'+prefix+':'+str(n)+':' in inst for inst in instances) for n in closure_lines)
             and sum('mem::maybe_uninit::MaybeUninit<u8>' in inst and 'sorting_model::KeyLess<' in inst for inst in instances)==1,
             'fresh inactive concrete instances')
        valid=len(candidates)==len(instances)==len(calls) and all(p['status']=='SUCCESS' and exact_property_site(p,src['file'],src['allowed_property_lines']) for p in candidates)
    else:
        candidates=[p for p in candidates if stem(p)==row['selector']]
        valid=len(candidates)==1 and candidates[0]['status']=='SUCCESS' and exact_property_site(candidates[0],src['file'],src['allowed_property_lines'])
    return {'role':role['role'],'message':role['expected_message'],'expected_description':role['expected_description'],
        'binding':role['binding_kind'] if valid else 'PENDING','properties':[property_ref(row,p) for p in candidates],
        'source':{k:v for k,v in src.items() if k!='legacy_s107'},'origin_key':row['origin_key'],
        'native_root':row['native_root'],'reason':None if valid else 'missing/duplicate/wrong-root/status/source role'}


def supplemental(row,entry,props):
    s=entry['source'];lines=source_text(s['file']).splitlines()
    need(sha(source_text(s['file']).encode())==s['sha256'] and '\n'.join(lines[s['line']-1:s.get('end_line',s['line'])]).strip()==s['text'].strip(),'supplemental source')
    root=row['selector'].rsplit('::',1)[-1]
    need(entry['expected_description']==root+'::'+entry['role'],'supplemental root label')
    guard=entry['guard']
    need(guard in {'true','n == 0','n == 1'},'supplemental known guard')
    applies=guard=='true' or not isinstance(row['domain_N'],int) or row['domain_N']==int(guard[-1])
    need(entry['applies']==applies,'supplemental guard vs row domain')
    matches=[p for p in props if p['description']==entry['expected_description']]
    valid=all(p['class']=='assertion' and p['file']==helpers()[0].EXPORT_PREFIX+s['file']
              and p['id'].rsplit('.',2)[0]==row['selector'] and p['status']==('SUCCESS' if entry['applies'] else 'UNREACHABLE')
              and exact_property_site(p,s['file'],{s['line']}|{x['line'] for x in row['source_binding']['locations']}) for p in matches)
    # A statically false branch may be absent, or retained as UNREACHABLE.
    valid=valid and (len(matches)==1 if entry['applies'] else len(matches)<=1)
    return {'role':entry['role'],'guard':entry['guard'],'applies':entry['applies'],'required_in_127':False,
        'decision':'BOUND_GUARD_APPLICABILITY' if valid else 'PENDING', 'source':s,
        'properties':[property_ref(row,p) for p in matches],'origin_key':row['origin_key']}


def cover_binding(row,message,props):
    sem=helpers()[4];pfcsrc=row['source_binding'];text=source_text(pfcsrc['file'])
    found=[p for p in props if p['class']=='cover' and p['description']==message]
    valid=len(found)==1 and found[0]['status']=='SATISFIED'
    p=found[0] if len(found)==1 else None
    ctx=sem._source_context(text,row['selector'].rsplit('::',1)[-1],message,'cover',int(p['line']) if p else None)
    # positive! changed assert! to constant kani::assert. Reuse the reviewed
    # source-case rule with its actual fresh operation lines (no stale anchors).
    if ctx['source_case']=='MODEL_CONTROLS_POSITIVE' and ctx['root_macro']=='positive':
        lo,hi=sem._macro_regions(text.splitlines())['positive']
        ops=[i+1 for i in range(lo,hi+1) if 'kani::assert(' in text.splitlines()[i] or 'sorted_prefix(' in text.splitlines()[i]]
        ctx['operation_source_lines']=ops
        ctx['source_role_order_after_assumptions_and_call']=bool(ops and ctx['assumption_source_lines'] and ctx['cover_source_lines'] and
            max(ctx['assumption_source_lines'])<min(ops) and max(ops)<min(ctx['cover_source_lines']))
    valid=bool(valid and ctx['active_source_role_sites'] and ctx['source_role_order_after_assumptions_and_call']
               and p['file']==helpers()[0].EXPORT_PREFIX+pfcsrc['file'] and p['id'].rsplit('.',2)[0]==row['selector']
               and exact_property_site(p,pfcsrc['file'],set(ctx['active_source_role_sites'])|{x['line'] for x in pfcsrc['locations']}))
    return {'message':message,'binding':'EXACT_SAT_COVER_SEMANTIC' if valid else 'PENDING',
            'property':property_ref(row,p) if p else None,'source':ctx,'source_sha256':pfcsrc['sha256'],'origin_key':row['origin_key']}


def native_root(row,g):
    native=helpers()[1];m=g['binding-metadata.json'];h=next(h for h in g['export.json']['harnesses'] if h['name']==row['selector'])
    mr=next(r for r in m['rows'] if r['row_id']==row['id'])
    need((mr['group_id'],mr['harness'],mr['crate'],mr['mode'],mr['variant'])==(row['group'],row['selector'],'core',row['mode'],row['variant']),'native row namespace')
    ref,=mr['native_harness_records'];entry,=[e for e in m['native_metadata'] if e['path']==ref['metadata_path']]
    actual=native._pointer(json.loads(entry['text']),ref['pointer'])
    source=row['source_binding']
    need(actual['pretty_name']==ref['name']==row['selector'] and actual['crate_name']==ref['crate']==h['crate_name']=='core'
         and actual['attributes']==h['attributes'] and actual['contract']==h['contract'],'native root attributes')
    need(actual['original_file']==helpers()[0].EXPORT_PREFIX+source['file'] and actual['original_start_line']==h['line']
         and actual['original_end_line']>=actual['original_start_line'],'native root source span')
    need(h['file']==source['file'] and source['selector']==row['selector'] and source['mode']==row['mode'],'source root context')
    lines=source_text(source['file']).splitlines();need(sha(source_text(source['file']).encode())==source['sha256'],'root source hash')
    for loc in source['locations']:need(lines[loc['line']-1]==loc['source'],'root source site')
    need(h['warnings']==[] and h['warnings_truncated']==0 and not h['attributes']['stubs'] and not h['attributes']['verified_stubs']
         and h['attributes']['should_panic'] is False and h['is_automatically_generated'] is False and h['has_loop_contracts'] is False
         and h['resolved_unwind']==row['spec']['unwind'] and h['attributes']['unwind_value'] in (None,row['spec']['unwind']),'root modes/stubs/warnings')
    return {**ref,'sha256':entry['sha256'],'record_sha256':sha(encoded(actual)),
            'source_span':[actual['original_start_line'],actual['original_end_line']]}


def unreachable(b,origin,rows):
    _,_,_,u,_,un,_=helpers();ob=b['origins'][origin];q=ob['request']
    source=lambda path:source_text(path)
    result=un.analyze_groups(q,{gid:{'properties':g['properties.json'],'export':g['export.json'],'receipt':g['receipt.json']}
                                  for gid,g in ob['groups'].items()},source)
    need(not result['unknown'],'U input gaps')
    sources={(repo,path):blob(STD if repo=='std' else CONTROL,SOURCE if repo=='std' else u.TOOL,path).decode()
             for repo,path,_,_ in u.ANCHORS.values()}
    out=[]
    for r in result['records']:
        row=rows[r['row_id']];g=ob['groups'][r['group']]
        props=next(h['properties'] for h in g['properties.json']['harnesses'] if h['name']==r['selector'])
        prop=next(p for p in props if p['id']==r['property_id']);r['origin_key']=row['origin_key']
        r['source_sha256']=sha(source(r['site']['source_path']).encode()) if r['site']['source_path'] else None
        r['evidence_sha256']=row['evidence_hashes'];r['native_root']=row['native_root']
        required=[s for s in row['required_success'] if any(p['id']==r['property_id'] for p in s['properties'])]
        supp=[s for s in row['supplemental'] if any(p['id']==r['property_id'] for p in s['properties'])]
        if required or prop['class'] in {'assigns','frees','postcondition'}:
            r['decision']='BLOCK_MANDATORY_POST_FRAME_RELATION_UNREACHABLE'
        elif supp:
            s,=supp
            r['decision']='ALLOWED_EXPECTED_BRANCH_UNREACHABLE' if not s['applies'] and s['decision']=='BOUND_GUARD_APPLICABILITY' else 'BLOCK_MANDATORY_POST_FRAME_RELATION_UNREACHABLE'
            r['decision_basis']={'guard':s['guard'],'source':s['source'],'N':row['domain_N']}
        elif (r['site']['source_path'].endswith('/sorting_entry_smoke.rs') and prop['class']=='assertion'
              and prop['description']==u.BOUNDS and int(prop['line'])==128 and row['domain_N'] in (0,2,3)
              and prop['id'].rsplit('.',2)[0]==row['selector']):
            snippet=source(r['site']['source_path']).splitlines()[126:130]
            need(snippet==['            if $exact_n == 1 {','                let expected = [$new(input[0])];',
                '                kani::assert(post::<$type, KeyLess<$type>>(',
                '                    snapshot::<$type, KeyLess<$type>>(&expected), &backing[1..2]), concat!(stringify!($name), "::n1_value_unchanged"));'], 'fresh N1 safety guard source')
            r['decision']='ALLOWED_EXPECTED_BRANCH_UNREACHABLE'
            r['decision_basis']={'guard':'$exact_n == 1','N':row['domain_N'],'source_lines':[127,128,129,130],
                'premise':'Exact N substitution excludes input[0] construction in this branch; same reviewed rule at fresh site128 (old137)'}
        elif r['status_kind']=='cover':
            companion=row['spec'].get('companion')
            allowed=row['id'] in {'activation-default','activation-override'} and row['negative_oracle'] and companion in rows
            allowed=allowed and rows[companion]['source_reported_verdict']=='SUCCESS' and rows[companion]['origin_key']==row['origin_key']
            allowed=allowed and r['description'] not in row['spec']['required_cover_messages'] and r['site']['source_path'].endswith('/sorting_entry_controls.rs') and int(r['site']['line'])==(20 if row['id']=='activation-default' else 33)
            r['decision']='ALLOWED_EXPECTED_NEGATIVE_POST_FAILURE_RETURN_COVER' if allowed else 'PENDING_NEGATIVE_COVER'
            r['decision_basis']={'companion':companion,'same_origin':allowed,'positive_reachability_credit':'NONE'}
        elif r['decision'].startswith('ALLOWED_'):
            # Old smoke line137 ceased being an assertion; never reuse that exception.
            if r['site']['source_path'].endswith('/sorting_entry_smoke.rs') and int(r['site']['line'])!=23:
                r['decision']='UNKNOWN_CHANGED_HARNESS_SITE'
        if r['decision'].startswith('UNKNOWN'):
            try:
                family,operation,path,fn=u.classify(prop)
                premises=u.check_premises(family,sources)
                need(path not in q['variants'].get(row['variant'],{}).get('changed_file_sha256',{}),'variant changes U rule source')
                context=r['site']['source_context']
                need(context and context['lines']==[{'line':i,'text':source(path).splitlines()[i-1]} for i in range(context['start_line'],context['end_line']+1)],'exact U source context')
                r.update(decision='ALLOWED_GENERATED_SAFETY_APPLICABILITY',rule=family,operation=operation,premises=premises,
                         assurance='PINNED_SOURCE_LOCAL_ARGUMENT; SOURCE_REPORTED_CHECK_IDENTITY')
            except (ValueError,KeyError,TypeError) as exc:
                r['unresolved_reason']=str(exc)
        r['independent_proof_credit']='NONE';out.append(r)
    return out


def origin_map(b):
    result={'schema':'s108-composite-origin-map-v1','origins':{},'rows':{}}
    for origin,ob in b['origins'].items():
        p=b['plan'][origin];artifacts=index(ob['artifacts']['artifacts'],'name')
        provs=ob['provenance']['success_artifacts'] if origin=='original' else None
        origin_tuple={'repository':p['repository'],'run_id':RUNS[origin],'attempt':1,'trigger_sha':HEADS[origin],
            'control_sha':p['control_sha'] if origin=='original' else p['reviewed_control_sha'],'control_tree':p['tree'],
            'request_sha256':REQUESTS[origin],'source_sha':SOURCE,'tool_sha':b['plan']['common']['tool_sha'],'intake_commit':INTAKES[origin]}
        result['origins'][origin]={'identity':origin_tuple,'collector':b['replays'].get(origin),'groups':{}}
        for gid,g in ob['groups'].items():
            name='ch8-s1-05-'+str(RUNS[origin])+'-1-'+gid;art=artifacts[name]
            need(art['workflow_run']['id']==RUNS[origin] and art['workflow_run']['head_sha']==HEADS[origin] and not art['expired'],'artifact origin')
            zipinfo=read(runpath(origin)/'artifacts'/name/'zip-integrity.json')
            need(zipinfo['github_digest_match'] is True and art['digest']=='sha256:'+zipinfo['sha256'] and art['size_in_bytes']==zipinfo['bytes'],'historical ZIP attestation identity')
            payload=runpath(origin)/'artifacts'/name/'group-evidence.json.gz'
            need(sha(payload.read_bytes())==zipinfo['payload_sha256'],'exact compact payload digest')
            prov=next((x for x in provs if x['artifact']==name),None) if provs else None
            if prov:
                need(prov['github_id']==art['id'] and prov['github_zip_digest']==art['digest'] and prov['payload_sha256']==zipinfo['payload_sha256'],'original provenance identity')
                for rel,digest in prov['projections'].items():need(sha((runpath(origin)/rel).read_bytes())==digest,'original projection digest')
            entries=prov['entries'] if prov else ob['provenance']['embedded_members']
            for filename in ('properties.json','export.json','binding-metadata.json'):
                need(sha((groupdir(origin,gid)/filename).read_bytes())==entries['groups/'+gid+'/'+filename]['sha256'],'exact structured member projection')
            base=groupdir(origin,gid)
            group={**origin_tuple,'group':gid,'invocation_id':g['receipt.json']['invocation_id'],
                   'artifact':{k:art[k] for k in ('id','name','digest')},'original_member_hashes':entries,
                   'projection_hashes':{n:sha((base/n).read_bytes()) for n in g},
                   'projection_root':str(base.relative_to(ROOT)),'state':g['receipt.json']['state']}
            result['origins'][origin]['groups'][gid]=group
            spec=next(s for s in ob['request']['execution_groups'] if s['id']==gid)
            for rid in spec['row_ids']:
                need(rid not in result['rows'],'duplicate origin row')
                result['rows'][rid]={'origin':origin,'origin_key':str(RUNS[origin])+'/1','group':gid,'group_pointer':'/origins/'+origin+'/groups/'+gid,
                                      'group_origin_sha256':sha(encoded(group))}
    return result


def dependencies(rows,specs,request):
    v3=helpers()[6]
    for rid,row in rows.items():
        cid=specs[rid].get('companion')
        if cid:
            c=rows.get(cid);same=bool(c and row['origin_key']==c['origin_key']=='44095954742/1')
            row['same_run_companion']={'id':cid,'group':c['group'] if c else None,'run':44095954742 if same else None,
                'source_verdict':c['source_reported_verdict'] if c else None,'source_tool_request_pins':'MATCH' if same else 'MISMATCH',
                'binary_after':c['binary_after'] if c else 'UNKNOWN'}
    edges=v3.qualify(rows,specs,44095954742)
    unions=[]
    for spec in request['replacement_unions']:
        members=[rows[r] for r in spec['member_row_ids'] if r in rows]
        exact=len(members)==len(set(spec['member_row_ids']))==4
        exact=exact and {m['domain_N'] for m in members}=={0,1,2,3} and all(m['origin_key']=='44095954742/1' for m in members)
        covered=set(spec['required_cover_messages'])<={c['message'] for m in members for c in m['required_covers'] if c['binding']=='EXACT_SAT_COVER_SEMANTIC'}
        # Union roles are root-qualified in S1-08; the request supplies the shared
        # role vocabulary separately rather than pretending messages are identical.
        required_roles=set(spec['required_success_roles'])
        success=all(required_roles<={s['role'] for s in m['required_success'] if s['binding'] in {'EXACT_ROLE_LABEL','EXACT_SUCCESS_SEMANTIC','EXACT_SUCCESS_SEMANTIC_SET'}} for m in members)
        good=exact and covered and success and all(m['qualification']=='QUALIFIED' for m in members)
        unions.append({'id':spec['id'],'members':spec['member_row_ids'],'member_qualification':{m['id']:m['qualification'] for m in members},
            'exact_origin_domain_members':'BOUND' if exact else 'PENDING','required_cover_union':'BOUND' if covered else 'PENDING',
            'required_success_members':'BOUND' if success else 'PENDING','qualification':'QUALIFIED_BOUNDED_UNION' if good else 'PENDING',
            'origin_key':'44095954742/1','proof_credit':'NONE'})
    return edges,unions


def compose(b):
    keys=validate_partition(b);compat=compatibility(b);omap=origin_map(b);inv=helpers()[0]
    roles=read(runpath('original')/'ROLE-MAP.json');rows={};pfc_records=[];u_records=[];unsupported=[];exceptions=[]
    pmodules={o:pfc_bundle(b,o) for o in RUNS}
    for origin,ob in b['origins'].items():
        q=ob['request'];specs=index(q['rows'],'id');groups={r:g for g in q['execution_groups'] for r in g['row_ids']}
        for gid,g in ob['groups'].items():
            group_identity(b,origin,gid)
            for rid in next(s['row_ids'] for s in q['execution_groups'] if s['id']==gid):
                s=specs[rid];h=next(h for h in g['export.json']['harnesses'] if h['name']==s['selector'])
                props=next(h['properties'] for h in g['properties.json']['harnesses'] if h['name']==s['selector']);by=inv.inventory(h,props)
                row={'id':rid,'group':gid,'selector':s['selector'],'expected':s['expected'],'variant':s['variant'],'mode':s['mode'],
                    'domain_N':s.get('N'),'type':s.get('type'),'threshold':s.get('threshold'),'unwind':s['unwind'],'source_reported_verdict':h['outcome']['verdict'],'properties':len(props),'binary_after':'MATCH',
                    'origin_key':omap['rows'][rid]['origin_key'],'origin':omap['rows'][rid], 'evidence_hashes':omap['origins'][origin]['groups'][gid]['projection_hashes'],
                    'spec':s,'source_binding':q['source_bindings'][rid],'local_pending_gates':[],'proof_credit':'NONE'}
                rows[rid]=row;row['native_root']=native_root(row,g)
                inv.STD=STD;inv.CONTROL=CONTROL;inv.SOURCE_SHA=SOURCE;inv.CONTROL_SHA=HEADS[origin]
                row['negative_oracle']=inv.negative_oracle(s,h,by,q)
                if rid in {'activation_descending_rejected','activation_effectful_rejected'}:
                    line,span,statement=(95,'95:32: 95:48','require_active(&[0u8, 1], &|a: &u8, b: &u8| a > b);') if rid=='activation_descending_rejected' else (101,'101:21: 101:37','let effectful = |a: &u8, b: &u8| { touched = true; a < b };')
                    oracle=row['negative_oracle'];file=s['oracle']['file']
                    need('closure@'+PREFIX+file+':'+span in oracle['property']['id']
                         and source_text(file).splitlines()[line-1].strip()==statement,'fresh repaired closure source span')
                    oracle['fresh_closure_source_binding']={'line':line,'span':span,'statement':statement,
                        'source_sha256':s['oracle']['source_sha256'],'native_root':row['native_root'],
                        'assurance':'SOURCE_REPORTED_EXACT_ID_SITE_SOURCE; NO_INDEPENDENT_MIR_ORIGIN_CREDIT'}
                row['required_success']=[role_binding(row,r,props) for r in roles['required_success_bindings'] if r['row_id']==rid]
                row['supplemental']=[supplemental(row,r,props) for r in roles['supplemental_label_sites'] if r['row_id']==rid]
                row['required_covers']=[cover_binding(row,msg,props) for msg in s['required_cover_messages']]
                need([x['message'] for x in row['required_success']]==s['required_success_messages'],'required role namespace:'+rid)
                gates=row['local_pending_gates']
                if compat['status']!='PASS':gates.append('COMPOSITION_COMPATIBILITY_PENDING')
                if any(r['binding']=='PENDING' for r in row['required_success']):gates.append('REQUIRED_ROLE_OR_SEMANTIC_BINDING')
                if any(c['binding']!='EXACT_SAT_COVER_SEMANTIC' for c in row['required_covers']):gates.append('REQUIRED_SAT_COVER_BINDING')
                if any(c['decision']=='PENDING' for c in row['supplemental']):gates.append('SUPPLEMENTAL_GUARD_APPLICABILITY')
                if s['mode']=='PFC':
                    p,pb=pmodules[origin]
                    try:
                        binding=p.analyze_row(pb,s,groups[rid]);binding['origin_key']=row['origin_key']
                        pfc_records.append(binding);row['PFC']={'status':binding['status'],'sha256':sha(encoded(binding)),'origin_key':row['origin_key']}
                    except (ValueError,KeyError,TypeError,IndexError) as exc:
                        row['PFC']={'status':'PENDING','reason':str(exc),'origin_key':row['origin_key']};gates.append('FULL_PROFILES_V4_PFC_BINDING')
                for prop in props:
                    located=isinstance(prop.get('file'),str) and prop['file'].startswith(inv.EXPORT_PREFIX) and str(prop.get('line','')).isdigit() and int(prop['line'])>0
                    if not located:
                        entry=dict(prop,group=gid,selector=s['selector'],row_id=rid)
                        policy=read(BASE/'s1-06/run-43889560779/accept-v2/LOCATION-POLICY.json')
                        need(inv.location_exception(entry,policy),'unapproved location:'+rid+':'+prop['id'])
                        exceptions.append({'row_id':rid,'property':property_ref(row,prop),'decision':'ALLOWED_LOCATION_ONLY_NO_REPAIR'})
                    if prop['class']=='unsupported_construct':
                        need(prop['status']=='SUCCESS' and prop['id'] not in h['checks']['unreachable'],'unsupported exact successful guard')
                        unsupported.append({'row_id':rid,'property':property_ref(row,prop),'decision':'ALLOWED_EXACT_SUCCESSFUL_UNSUPPORTED_GUARD','semantics':'assert(false); assume(false)'})
    for origin in RUNS:u_records.extend(unreachable(b,origin,rows))
    for row in rows.values():
        records=[r for r in u_records if r['row_id']==row['id']]
        row['U']={'records':len(records),'allowed':sum(r['decision'].startswith('ALLOWED_') for r in records),
            'pending':[{'property_id':r['property_id'],'decision':r['decision'],'reason':r.get('unresolved_reason',r['decision_basis'])} for r in records if not r['decision'].startswith('ALLOWED_')],
            'origin_key':row['origin_key'],'records_sha256':sha(encoded(records))}
        if row['U']['pending']:row['local_pending_gates'].append('UNREACHABLE_APPLICABILITY_OR_MANDATORY_OBLIGATION')
    # Preserve original PFC negative companion full concrete target-instance gate.
    byp=index(pfc_records,'id')
    for row in rows.values():
        if row['mode']=='PFC' and row['expected']=='DETECTED' and row['id'] in byp:
            binding=byp[row['id']];c=byp.get(row['spec'].get('companion'),{})
            good=c.get('status')=='SOURCE_REPORTED_BOUND' and c['origin_key']==binding['origin_key'] and c['variant']=='production'
            good=good and c['harness']==binding['harness'] and c['contract']['target_instance']==binding['contract']['target_instance'] and all(e['property']['status']=='SUCCESS' for e in c['contract']['ensures'])
            if good:binding['negative_oracle']['legal_companion_binding']=c['id']
            else:row['local_pending_gates'].append('PFC_LEGAL_COMPANION_FULL_TARGET')
            row['PFC']['sha256']=sha(encoded(binding))
    req=b['origins']['original']['request'];specs=index(req['rows'],'id')
    edges,unions=dependencies(rows,specs,req)
    for row in rows.values():row.pop('spec')
    totals={'rows':len(rows),'rows_qualified':sum(r['qualification']=='QUALIFIED' for r in rows.values()),
        'original_rows':sum(r['origin_key']=='44095954742/1' for r in rows.values()),'retry_rows':sum(r['origin_key']=='44128268928/1' for r in rows.values()),
        'properties_reconciled':sum(r['properties'] for r in rows.values()),'required_roles':sum(len(r['required_success']) for r in rows.values()),
        'exact_role_labels':sum(s['binding']=='EXACT_ROLE_LABEL' for r in rows.values() for s in r['required_success']),
        'semantic_bindings':sum(s['binding'] in {'EXACT_SUCCESS_SEMANTIC','EXACT_SUCCESS_SEMANTIC_SET'} for r in rows.values() for s in r['required_success']),
        'required_SAT_covers':sum(c['binding']=='EXACT_SAT_COVER_SEMANTIC' for r in rows.values() for c in r['required_covers']),
        'supplemental_sites':sum(len(r['supplemental']) for r in rows.values()),'U_records':len(u_records),
        'U_allowed':sum(r['decision'].startswith('ALLOWED_') for r in u_records),'U_decisions':dict(sorted(collections.Counter(r['decision'] for r in u_records).items())),
        'PFC_bound':len(pfc_records),'negative_oracles':sum(bool(r['negative_oracle']) for r in rows.values()),
        'companions':len(edges),'companions_qualified':sum(e['qualification']=='QUALIFIED' for e in edges.values()),
        'unions':len(unions),'unions_qualified':sum(u['qualification']=='QUALIFIED_BOUNDED_UNION' for u in unions),
        'location_exceptions':len(exceptions),'unsupported_success_guards':len(unsupported)}
    report={'schema':'ch8-s1-08-origin-partitioned-composite-acceptance-v1','stage':'READY_FOR_INDEPENDENT_REVIEW',
        'task_commit':TASK,'intakes':INTAKES,'source_sha':SOURCE,'tool_sha':b['plan']['common']['tool_sha'],
        'qualified_acceptance':'QUALIFIED_BOUNDED_SOURCE_REPORTED_COMPOSITE_CANDIDATE' if all(r['qualification']=='QUALIFIED' for r in rows.values()) and all(u['qualification']=='QUALIFIED_BOUNDED_UNION' for u in unions) else 'PENDING',
        'totals':totals,'rows':list(rows.values()),'U_records':u_records,'PFC_bindings':pfc_records,'companions':edges,'replacement_unions':unions,
        'location_exceptions':exceptions,'unsupported_records':unsupported,'compatibility':'PASS' if compat['status']=='PASS' else 'PENDING',
        'origin_replays':b['replays'],'independent_review':'PENDING_NEW_ADAPTER_AND_RECEIPT','final_admission':'PENDING_INDEPENDENT_REVIEW',
        'independent_proof_credit':'NONE','B1_credit':'NONE','B2_credit':'NONE','general_theorem_credit':'NONE',
        'assurance':'BOUNDED_SOURCE_REPORTED_PROFILES_V4_U_PER_SITE_FRESH_ROLES; TRUST_PINNED_STOCK_COMPILER',
        'lost_claims':b['plan']['lost_claims'],'original_run_status':'FAILED_IMMUTABLE',
        'cell_profile':{'harness_timeout_seconds':1200,'child_timeout_seconds':3300,'stable_verification_seconds':round(next(h['resources']['verification_time_s'] for h in b['origins']['retry']['groups']['cell-u34']['export.json']['harnesses'] if h['name'].endswith('::stable_default_cell')),3),'unstable_verification_seconds':round(next(h['resources']['verification_time_s'] for h in b['origins']['retry']['groups']['cell-u34']['export.json']['harnesses'] if h['name'].endswith('::unstable_default_cell')),3),'fit600':'NOT_ESTABLISHED','causality':'NOT_ESTABLISHED'},
        'domain':'S1 smoke N0..3 exact initialized fixture geometry; no threshold16/32 or general theorem',
        'execution':{'offline':True,'compiler_verifier_CI_rerun_push_ledger_budget':'NOT_RUN_NOT_MODIFIED','subagents':'NONE','raw_logs_read':False}}
    validate_components(report,b)
    return report,omap,compat


def validate_components(report,b):
    """Exact component coverage/namespace and transitive consumption validation."""
    rows=index(report['rows'],'id');req=b['origins']['original']['request'];specs=index(req['rows'],'id')
    need(set(rows)==set(specs),'component row coverage')
    roles=read(runpath('original')/'ROLE-MAP.json')['required_success_bindings']
    expected={(r['row_id'],r['role']) for r in roles}
    actual=[(rid,s['role']) for rid,row in rows.items() for s in row['required_success']]
    need(len(actual)==len(set(actual)) and set(actual)==expected,'component role coverage')
    required_u={(origin,rid,p['id']) for origin,ob in b['origins'].items() for g in ob['groups'].values() for h in g['properties.json']['harnesses']
                for rid in [next(r['id'] for r in ob['request']['rows'] if r['selector']==h['name'] and r['variant']==g['receipt.json']['variant'])]
                for p in h['properties'] if p['status']=='UNREACHABLE'}
    got=[('original' if r['origin_key']=='44095954742/1' else 'retry',r['row_id'],r['property_id']) for r in report['U_records']]
    need(len(got)==len(set(got)) and set(got)==required_u,'component U coverage')
    for rid,row in rows.items():
        origin='retry' if rid in b['plan']['retry']['selected_row_ids'] else 'original'
        need(row['origin_key']==str(RUNS[origin])+'/1','component origin namespace')
        gs=next(g for g in req['execution_groups'] if rid in g['row_ids']);g=b['origins'][origin]['groups'][gs['id']]
        need(row['group']==gs['id'] and row['selector']==specs[rid]['selector'] and row['variant']==specs[rid]['variant'],'component row namespace')
        records=[r for r in report['U_records'] if r['row_id']==rid]
        need(row['U']['origin_key']==row['origin_key'] and row['U']['records']==len(records)
             and row['U']['records_sha256']==sha(encoded(records)), 'component U consumption hash')
        expected_gates=set()
        if report['compatibility']!='PASS':expected_gates.add('COMPOSITION_COMPATIBILITY_PENDING')
        if any(r['binding']=='PENDING' for r in row['required_success']):expected_gates.add('REQUIRED_ROLE_OR_SEMANTIC_BINDING')
        if any(c['binding']!='EXACT_SAT_COVER_SEMANTIC' for c in row['required_covers']):expected_gates.add('REQUIRED_SAT_COVER_BINDING')
        if any(c['decision']=='PENDING' for c in row['supplemental']):expected_gates.add('SUPPLEMENTAL_GUARD_APPLICABILITY')
        if row['mode']=='PFC' and row.get('PFC',{}).get('status')!='SOURCE_REPORTED_BOUND':expected_gates.add('FULL_PROFILES_V4_PFC_BINDING')
        if any(not r['decision'].startswith('ALLOWED_') for r in records):expected_gates.add('UNREACHABLE_APPLICABILITY_OR_MANDATORY_OBLIGATION')
        need(expected_gates<=set(row['local_pending_gates']), 'component pending gate consumption')
        props=next(h['properties'] for h in g['properties.json']['harnesses'] if h['name']==row['selector'])
        by=index(props,'id')
        for s in row['required_success']:
            for p in s['properties']:
                need(p['origin_key']==row['origin_key'] and p['id'] in by and p==property_ref(row,by[p['id']]),'component role actual property')
        need([c['message'] for c in row['required_covers']]==specs[rid]['required_cover_messages'],'component cover coverage')
        for c in row['required_covers']:
            if c['property']:need(c['property']==property_ref(row,by[c['property']['id']]),'component cover property')
        need(bool(row['negative_oracle'])==(specs[rid]['expected']=='DETECTED'),'component negative coverage')
        if row['negative_oracle']:
            p=row['negative_oracle']['property'];need(p==by[specs[rid]['oracle']['property_id']] and p['status']=='FAILURE','component stale oracle')
        if row['mode']=='PFC' and row.get('PFC',{}).get('status')=='SOURCE_REPORTED_BOUND':
            chain=next((p for p in report['PFC_bindings'] if p['id']==rid),None)
            need(chain is not None and chain['origin_key']==row['origin_key'] and sha(encoded(chain))==row['PFC']['sha256'],'component PFC coverage/hash')
    edges={(r['id'],r['companion']) for r in req['rows'] if r.get('companion')}
    need(set(report['companions'])=={r for r,c in edges} and all(report['companions'][r]['id']==c for r,c in edges),'companion coverage')
    # Recompute least fixed point, preventing caller-only or transitive promotion.
    recomputed=copy.deepcopy(rows)
    for r in recomputed.values():r['spec']=specs[r['id']]
    e,unions=dependencies(recomputed,specs,req)
    need(e==report['companions'] and unions==report['replacement_unions'],'companion/union gate consumption')
    need(all(recomputed[r]['qualification']==rows[r]['qualification'] for r in rows),'transitive qualification')
    return True


def encoded(value):
    return (json.dumps(value,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode()


def sha(data):return hashlib.sha256(data).hexdigest()


def read(path):return json.loads(path.read_bytes())


def need(ok,reason):
    if not ok:raise ValueError(reason)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


@functools.lru_cache(None)
def git(repo,*args):return subprocess.check_output(['git','-C',str(repo),*args])


def blob(repo,commit,path):return git(repo,'show',commit+':'+path)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');parser.add_argument('--origin',choices=RUNS);args=parser.parse_args()
    try:
        if args.origin:
            verify_inputs();print(json.dumps(origin_replay(args.origin),sort_keys=True));return 0
        b=load();report,omap,compat=compose(b)
        for name,value in [('ACCEPT.json',report),('ORIGIN-MAP.json',omap),('COMPATIBILITY.json',compat)]:
            data=encoded(value)
            if args.write:(HERE/name).write_bytes(data)
            else:need((HERE/name).read_bytes()==data,name+' replay mismatch')
        print(json.dumps({'replay':'WRITTEN' if args.write else 'MATCH','verdict':report['qualified_acceptance'],'sha256':sha(encoded(report)),'totals':report['totals']},sort_keys=True));return 0
    except (ValueError,KeyError,TypeError,IndexError,OSError,subprocess.SubprocessError) as exc:
        print(json.dumps({'replay':'ERROR','reason':str(exc)}),file=sys.stderr);return 1


if __name__=='__main__':raise SystemExit(main())
