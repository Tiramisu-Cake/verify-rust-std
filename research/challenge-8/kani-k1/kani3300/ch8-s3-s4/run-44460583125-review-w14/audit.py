#!/usr/bin/env python3
"""Bounded independent review of committed structured evidence; no native tools."""
import base64
import collections
import copy
import gzip
import hashlib
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
G0 = Path('/root/verify-rust-std-kani3300-g0')
INTAKE = '97eaff96cd28267e36af69fe98077dd08737eea6'
TASK = '7c2c6af9f538d43e5cce51d548bdd73633358241'
REL = 'research/challenge-8/kani-k1/kani3300/ch8-s3-s4/run-44460583125/'
SOURCE = Path('/root/verify-rust-std-ch8-s3s4-bridge1-w13')
CONTROL = Path('/root/kani-ch8-s3s4-bridge1-r1-control-w13')
SRC = 'f1bdf11902252ad1178f42403c253ae710fecbaf'
CTRL = 'd675ef70dc1ada13330efc0990c2e1d6b0d21a5a'
TRIGGER = 'c2bbdb972cfe0e6f7472cf8bd93f1fa7c5e87acd'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
checks = []
def need(v, label):
    if not v:
        raise AssertionError(label)
    checks.append(label)
def sha(b): return hashlib.sha256(b).hexdigest()
def git(repo, *args): return subprocess.check_output(['git', '-C', str(repo), *args])
def blob(repo, rev, path): return git(repo, 'show', rev + ':' + path)
def read(n): return blob(G0, INTAKE, REL + n)
def obj(n): return json.loads(read(n + '.json'))
def write(n, v): (HERE / n).write_text(json.dumps(v, indent=2, ensure_ascii=False) + '\n')

def main():
    manifest = obj('MANIFEST')
    names = git(G0, 'ls-tree', '-r', '--name-only', INTAKE, REL).decode().splitlines()
    need(len(names) == 30 and len(manifest['files']) == 29, 'exact30 files/29 manifest entries')
    for n, meta in manifest['files'].items():
        b = read(n)
        need(len(b) == meta['bytes'] and sha(b) == meta['sha256'], 'committed intake size/hash ' + n)
        need((G0 / REL / n).read_bytes() == b, 'current intake bytes immutable ' + n)
    taskpath = 'research/challenge-8/kani-k1/TASK-CH8-S3S4-BRIDGE1-R1-INTAKE-REVIEW-W14.md'
    taskhash = sha(blob(G0, TASK, taskpath))
    prov = obj('PROVENANCE'); roots = obj('ROOTS'); qual = obj('QUALIFICATION')
    reqbytes = blob(CONTROL, CTRL, 'ch8-s1-control/CI-REQUEST.json'); req = json.loads(reqbytes)
    need(req == roots['request'], 'exact request source for all review comparisons')
    need(sha(reqbytes) == prov['request_sha256'] == '23c137a331acb92610b3f0cf2192a0e16081dbf0815a35fc3c8d88742c0a1fa3', 'exact request hash')
    need(req['std_sha'] == SRC and req['tool_sha'] == TOOL, 'exact source/tool pins')
    need(blob(CONTROL, TRIGGER, 'ch8-s1-control/CI-REQUEST.json') == reqbytes, 'trigger same request')
    need(git(CONTROL, 'rev-parse', CTRL+'^{tree}') == git(CONTROL, 'rev-parse', TRIGGER+'^{tree}'), 'trigger/control same tree')
    need(sha(blob(CONTROL, TRIGGER, '.github/workflows/ch8-s2.yml')) == prov['workflow_sha256'] == '317f92181bee9470ddf65471def7154fcacbf1e6fb7913220ca1f154ca915a55', 'exact workflow pin')
    for n, h in roots['source_files'].items(): need(sha(blob(SOURCE, SRC, n)) == h, 'source hash ' + n)
    for n, h in req['ci_payload_sha256'].items(): need(sha(blob(CONTROL, TRIGGER, n)) == h, 'control hash ' + n)
    gz = read('group-evidence.json.gz'); raw = gzip.decompress(gz)
    need(sha(gz) == '32fdc7741046b1dfd4d944ddf4881bffef993e87d949a91deddaf46f97b3d865' == prov['payload_sha256'], 'compact payload pin')
    need(sha(raw) == prov['uncompressed_sha256'], 'uncompressed compact hash')
    packet = json.loads(raw); members = {}; data = {}
    for n, e in packet['files'].items():
        b = e['text'].encode() if e.get('encoding', 'utf-8') == 'utf-8' else base64.b64decode(e['text'], validate=True)
        need(sha(b) == e['sha256'] and len(b) == e['bytes'], 'sealed compact member ' + n)
        members[n] = b; data[n] = json.loads(b)
    need(len(members) == 105, 'exact105 structured members')
    order = [x['id'] for x in req['rows']]
    need(type(data['receipt.json']['s3_campaign']['selected_roots']) is int and data['receipt.json']['s3_campaign']['selected_roots'] == 7, 'portable genuine int7')
    need(data['receipt.json']['s3_campaign']['completed'] == order, 'all7 portable completion order')
    need(data['receipt.json']['state'] == 'SELECTED_PARTIAL' and data['receipt.json']['stop_reason'] is None, 'partial observations without global stop')
    rows = []; ureview = []; guards = []; adverse = []
    props_projection = obj('NATIVE-PROPERTIES')
    previous_end = None
    with tempfile.TemporaryDirectory(prefix='w14-bounded-readers-') as td:
        reader = Path(td)
        for n in git(CONTROL, 'ls-tree', '-r', '--name-only', CTRL, 'ch8-s1-control').decode().splitlines():
            b = blob(CONTROL, CTRL, n); rel = str(Path(n).relative_to('ch8-s1-control'))
            need(sha(b) == prov['frozen_reader_files'][rel]['sha256'], 'frozen dependency ' + rel)
            p = reader / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b)
        sys.path.insert(0, str(reader))
        rich = importlib.import_module('rich_evidence')
        policy = importlib.import_module('s34_policy')
        ev = importlib.import_module('s3_evidence')
        runner = importlib.import_module('runner')
        for rank, row in enumerate(req['rows'], 1):
            rid = row['id']; gp = 'groups/s3-' + rid + '/'
            q = qual['rows'][rank-1]; g = data[gp+'receipt.json']; stock = data[gp+'export.json']
            pr = data[gp+'properties.json']; bm = data[gp+'binding-metadata.json']
            sup = data['workers/'+rid+'-supervision.json']; life = data['workers/'+rid+'-lifecycle.json']
            launch = data['workers/'+rid+'-launch.json']; seal = data['completed/'+rid+'.json']
            need(q['id'] == rid and q['rank'] == rank, rid+' exact qualification identity/order')
            need(g['native_start_verified'] and len(g['native_start_events']) == 1 and g['native_start_events'][0]['selector'] == row['selector'], rid+' actual singleton start')
            need(g['effective_cfg'] == req['flags']['RUSTFLAGS'] and g['selectors'] == [row['selector']], rid+' cfg/selector')
            need(g['argv'] == runner.build_argv(Path('/home/runner/work/kani/kani/export'), Path('/home/runner/work/kani/kani/tool'), [row['selector']], row['unwind'], Path('/home/runner/work/_temp/ch8-s1-receipts')/(gp+'export.json')), rid+' exact argv')
            need(bm['invocation_id'] == g['invocation_id'] and bm['request_sha256'] == prov['request_sha256'] and bm['std_sha'] == SRC and bm['tool_sha'] == TOOL and bm['argv'] == g['argv'], rid+' metadata invocation binding')
            for a in bm['artifacts']: need(sha(members[gp+a['path']]) == a['sha256'], rid+' export binding '+a['path'])
            need(ev.provenance(g, data[gp+'compile/receipt.json'], req, rid, prov['request_sha256']), rid+' source provenance')
            need(not ev.protected(g,req,data['baseline.json'],sup,prov['request_sha256'])['observed_errors_ignored'], rid+' protected epochs')
            for stage in [life['pre']['binaries'],g['tool_fingerprints_before'],g['tool_fingerprints_after'],life['post']['binaries']]:
                need(runner.fingerprints_match(data['baseline.json']['binaries'],stage),rid+' E0/pre/worker-before/worker-after/post equality')
            need(launch['monotonic'] <= sup['monotonic_start'] <= g['native_start_events'][0]['monotonic'] <= sup['monotonic_end'] and (previous_end is None or previous_end <= launch['monotonic']), rid+' serial cleanup/start order')
            previous_end = sup['monotonic_end']
            need(sup['containment']['verified'] and sup['worker_exit'] == 0 and not sup['cutoff'] and not sup['orphan_survivors_at_worker_exit'] and g['execution']['child_shutdown_verified'],rid+' containment/reap/worker exit')
            binding=req['source_bindings'][rid]; reg=q['native_registration']
            need(reg['attributes']['kind'] == ({'ProofForContract':{'target_fn':'insert_tail'}} if row['mode']=='PFC' else 'Proof') and row['target'] == ('insert_tail' if row['mode']=='PFC' else None),rid+' actual PFC/Original null target')
            need(reg['attributes']['unwind_value'] == row['unwind'] == g['unwind'] and stock['configuration']['checks']['unwinding'] is True,rid+' actual unwind obligations enabled')
            hs=stock.get('harnesses',[]); records=pr.get('harnesses',[{'properties':[]}])[0]['properties']
            failures=[p for p in records if p['status']=='FAILURE']; us=[p for p in records if p['status']=='UNREACHABLE']; gs=[p for p in records if p['class']=='unsupported_construct']
            if hs:
                h=hs[0]
                need(props_projection[rid]['properties'] == records,rid+' exact full native ID/status/metadata projection')
                need(len(records)==h['n_properties']==q['native_property_count'] and len({p['id'] for p in records})==len(records),rid+' property count/uniqueness')
                need(all(isinstance(p.get('file'),str) and p['file'] and isinstance(p.get('line'),str) and re.fullmatch('[1-9][0-9]*',p['line']) for p in records),rid+' every completed property positively located')
                dec=rich.RegularEvidence([row['selector']],Path('/home/runner/work/kani/kani/export'));dec.finished=True;dec.closed={row['selector']};dec.records={row['selector']:copy.deepcopy(records)};dec.validate(stock)
                need(dec.complete,rid+' frozen rich reader accepts exact inventory')
                need(us == [x['property'] for x in qual['U_instances'] if x['root']==rid] and gs == q['unsupported_guards'],rid+' exact U/guard retention')
                need(h['outcome']['verdict'] == ('FAILURE' if rank<=3 else 'SUCCESS') and len(failures)==(1 if rank<=3 else 0),rid+' exact native verdict')
                covers=[p for p in records if p['class']=='cover']
                need(len(covers)==row['required_cover_count'] and {p['description'] for p in covers}==set(row['required_cover_messages']) and all(p['status']=='SATISFIED' for p in covers),rid+' exact SAT cover set')
                for role in row['roles']:
                    found=[p for p in records if p['description']==role['description']]
                    need(bool(found) and all(p['status']==role['status'] and p['class']==role['class'] and p['file']=='/home/runner/work/kani/kani/export/'+role['file'] and p['line']==str(role['line']) for p in found),rid+' source role '+role['description'])
                need(all(p['status']=='SUCCESS' for p in records if p['class']=='unwind'),rid+' observed native unwind checks')
                # Remove metadata on a SUCCESS system record (outside old exact cases).
                victim=next(p for p in records if p['status']=='SUCCESS' and p['class']=='unreachable') if rank>3 else next(p for p in records if p['status']=='SUCCESS')
                for field,value in [('file',None),('line',None),('line',0),('line','0'),('file',False)]:
                    changed=copy.deepcopy(records);next(p for p in changed if p['id']==victim['id'])[field]=value
                    dec.records={row['selector']:changed}
                    try: dec.validate(stock)
                    except ValueError: adverse.append({'root':rid,'property_id':victim['id'],'mutation':{field:value},'result':'REJECT'})
                    else: raise AssertionError('missing/wrong-type location accepted')
            else:
                need(stock['run_state']=='INCOMPLETE' and not records and q['U_count']=='UNKNOWN' and q['unsupported_guards']=='UNKNOWN' and q['native_property_count']=='UNKNOWN_NO_COMPLETED_NATIVE_INVENTORY',rid+' incomplete never normalized to zero')
                ex=g['execution'];co=data[gp+'compile/receipt.json'];mem=g['memory']
                need(co['state']=='COMPLETE' and co['elapsed_upper_bound_seconds']<180 and ex['termination_reason']=='timeout' and ex['timed_out'] and ex['original_exit_code']==-15 and ex['signal']==15 and ex['elapsed_seconds']>=600,rid+' wholechild600 not compile cutoff')
                need(ex['rss_peak_kib']<mem['group_cap_kib']==min(6291456,12582912,mem['available_kib']-2097152) and sup['outer_sampled_peak_kib']<12582912,rid+' sampled RSS below unchanged caps')
            need(q['strict_expected_match'] is False and data[rid+'/receipt.json']['s3_expected_match'] is False and seal['expected_match'] is False and q['qualification_admitted'] is False,rid+' strict0 original and sealed/no admission')
            rows.append({'id':rid,'selector':row['selector'],'invocation_id':g['invocation_id'],'mode':row['mode'],'target':row['target'],'unwind':row['unwind'],'domain':q['domain'],'native_verdict':q['native_verdict'],'property_count':q['native_property_count'],'class_status_counts':q['class_status_counts'],'exact_role_records':q['literal_roles'],'PFC':q['PFC'],'strict_expected_match':False,'admitted':False})
            guards.extend({'root':rid,'invocation_id':g['invocation_id'],'property':p,'assessment':'Retained SUCCESS guard; strict rejection unchanged; no independent unsupported-path theorem or waiver'} for p in gs)
    for u in qual['U_instances']:
        b=blob(SOURCE,SRC,u['source_file']);lines=b.decode().splitlines();n=u['source_line']
        need(sha(b)==u['source_sha256'] and lines[n-1] in u['source_context'] and u['source_local_argument'],u['root']+' independent U source site '+u['property']['id'])
        ureview.append({'root':u['root'],'invocation_id':u['invocation_id'],'property':u['property'],'source_sha256':sha(b),'source_context':u['source_context'],'reviewed_source_argument':u['source_local_argument'],'assessment':'SOURCE_LOCAL_DEFINEDNESS_ARGUMENT_ACCEPTED_AS_SOURCE_REPORTED_ONLY','independent_AST_MIR_origin':'UNKNOWN','strict_policy':'REJECT_ALL; proposal DISABLED; no admission'})
    need(len(ureview)==28 and len(guards)==7 and sum(isinstance(x['property_count'],int) and x['property_count'] or 0 for x in rows)==602,'all28 U/all7 guards/exact602 completed properties')
    need(collections.Counter(x['native_verdict'] for x in rows)=={'FAILURE':3,'SUCCESS':2,'UNKNOWN_INCOMPLETE_EXPORT':2},'2SUCCESS3intendedFAIL2unknown')
    need(qual['strict_policy']=={'mode':'REJECT_ALL','proposal':'S3-U-SITE-REVIEW-v1','enabled':False,'unknown':'REJECT','role_unreachable':'REJECT'},'strict policy unchanged')
    body=blob(SOURCE,SRC,'library/core/src/slice/sort/shared/smallsort.rs').decode();s9=body.split('fn sort9_optimal',1)[1].split('fn sort13_optimal',1)[0]
    need(len(re.findall(r'\bswap_if_less\(',s9))==25,'actual sort9 exact25 real swap calls')
    need(all(x['native_verdict']!='SUCCESS' or (x['mode']=='PFC' and x['PFC'] or x['mode']=='Original' and x['PFC'] is None) for x in rows),'positive PFC/Original distinction')
    write('ROWS.json',rows);write('U-REVIEW.json',ureview);write('GUARDS.json',guards)
    write('CHECKS.json',{'status':'PASS','checks_count':len(checks),'checks':checks,'metadata_adverse_controls':adverse,'intake_replay':{'status':'PASS','checks':1000,'adverse_controls':45,'regenerated_file_deltas':[],'scope':'Previously executed once in disposable intake copy; all29 manifest-covered files byte identical; no acquire.py execution'},'proof_credit':'NONE'})
    write('INPUTS.json',{'task_commit':TASK,'task_path':taskpath,'task_sha256':taskhash,'intake_commit':INTAKE,'intake_path':REL,'intake_manifest_sha256':sha(read('MANIFEST.json')),'intake_handoff_sha256':sha(read('HANDOFF.md')),'source':SRC,'tool':TOOL,'control':CTRL,'trigger':TRIGGER,'request_sha256':prov['request_sha256'],'workflow_sha256':prov['workflow_sha256'],'payload_sha256':sha(gz),'scope':'Independent terminal intake review only; current high/FastOFF; no subagents/model changes'})
    print(json.dumps({'status':'PASS','checks':len(checks),'metadata_adverse_controls':len(adverse),'roots':len(rows),'U':len(ureview),'guards':len(guards)}))

if __name__=='__main__': main()
