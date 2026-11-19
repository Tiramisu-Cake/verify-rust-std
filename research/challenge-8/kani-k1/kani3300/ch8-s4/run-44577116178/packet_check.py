#!/usr/bin/env python3
"""Final post-edit consistency and immutable-history check, no acquisition/native work."""
import collections,gzip,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
import replay as r
H=r.HERE
def read(n):return json.loads((H/n).read_text())
def main():
 checks=[]
 def need(ok,label):
  if not ok:raise AssertionError(label)
  checks.append(label)
 a=read('artifact-integrity.json');gz=(H/'group-evidence.json.gz').read_bytes();raw=gzip.decompress(gz);need(r.sha(gz)==a['payload_sha256'] and r.sha(raw)==a['uncompressed_sha256'],'original acquired member/payload byte identities preserved')
 packet=json.loads(raw);data={}
 for n,e in packet['files'].items():
  b=r.decode(e);need(len(b)==e['bytes'] and r.sha(b)==e['sha256'],'authentic structured member '+n);data[n]=json.loads(b)
 qs=read('QUALIFICATION.json')['rows'];ps=read('NATIVE-PROPERTIES.json');us=read('U-DOMAIN-ARGUMENTS.json');gs=read('GUARD-ARGUMENTS.json');ls=read('LOCATION-ARGUMENTS.json');ns=read('NON-VACUITY.json')['cases'];counts=collections.Counter();expectedU=set();expectedG=set()
 for q,nv in zip(qs,ns):
  rid=q['id'];pr=data['groups/s3-'+rid+'/properties.json'];native=pr['harnesses'][0]['properties']
  if q['n_properties'] is None:
   need(pr['state']=='INCOMPLETE' and ps[rid]['properties'] is None and not native and nv['candidate_status']=='BLOCKER' and nv['native_covers'] is None and nv['all_exported_unwind_properties'] is None,rid+' incomplete inventories remain UNKNOWN/BLOCKER')
   continue
  need(pr['state']=='COMPLETE' and ps[rid]['properties']==native and q['n_properties']==len(native),rid+' complete native dictionaries preserved')
  need(q['status_counts']==dict(collections.Counter(p['status'] for p in native)),rid+' exact complete status counts')
  for p in native:
   counts[p['status']]+=1
   if p['status']=='UNREACHABLE':expectedU.add((rid,p['id']))
   if p['class']=='unsupported_construct':expectedG.add((rid,p['id']))
  if rid in data['campaign-start.json']['request_data']['domains']:
   roles=nv['required_assertion_roles'];need(len(roles)==4 and all(x['native_matches'] and all(p['status']=='SUCCESS' for p in x['native_matches']) for x in roles),rid+' all four SUCCESS roles')
   need(len(nv['native_covers'])==6 and all(p['status']=='SATISFIED' for p in nv['native_covers']) and nv['all_exported_unwind_properties']==[],rid+' six SAT covers and complete empty residual unwind inventory')
 need(us['count']==len(us['instances'])==len(expectedU)==40 and {(u['root'],u['property']['id']) for u in us['instances']}==expectedU,'all40 U exact bijection and reported cardinality')
 need(not us['blockers'] and all(u['domain_unreachability_argument'] and u['property']['status']=='UNREACHABLE' for u in us['instances']),'all observed U arguments present and native U statuses preserved')
 need(us['argument_kinds']==dict(collections.Counter(u['argument_kind'] for u in us['instances'])),'domain argument-kind totals agree with instances')
 need(gs['count']==len(gs['instances'])==7 and {(g['root'],g['property']['id']) for g in gs['instances']}==expectedG,'all7 SUCCESS unsupported guards exact inventory')
 need(ls['count']==len(ls['non_std_location_cases'])==7 and not ls['blockers'],'all7 nonstd locations exact candidate count')
 need(dict(counts)=={'SUCCESS':599,'UNREACHABLE':40,'FAILURE':4,'SATISFIED':12},'655 observed records across6 complete inventories;2 unknown excluded')
 con=read('CONNECTED-JOBS.json')['jobs'];jobs=read('JOBS-METADATA.json')['jobs'];need(len(con)==len(jobs)==1 and all(con[0][k]==jobs[0][k] for k in ['id','name','status','conclusion','run_id']),'connector and exact-attempt REST job metadata agree')
 need(read('CONNECTED-ARTIFACTS.json')==read('CONNECTED-METADATA.json')['artifacts'],'connector metadata retained without projection drift')
 need(data['receipt.json']['state']=='SELECTED_PARTIAL' and read('RUN-METADATA.json')['conclusion']=='failure' and all(q['canonical']['s3_expected_match'] is False for q in qs),'workflow failure/campaign partial/strict0 history preserved')
 cost=read('COST-INTERPRETATION.json');need(all(c['native_verification_time_s'] is None and c['native_verification_cost_status']=='UNKNOWN_CENSORED' for c in cost['censored_cases']) and cost['exact_speedup_factor'] is None,'N13/N17 completed verification costs and speedup remain unknown')
 prefix='research/challenge-8/kani-k1/';ledger=prefix+'CH8-DISPATCH-LEDGER.md';need((r.G0/ledger).read_bytes()==r.blob(r.G0,'HEAD',ledger),'ledger byte-identical to prior HEAD; no mutation')
 need(not r.git(r.G0,'diff','HEAD','--',r.BASE+'ch8-s4/run-44548842328/').strip(),'S4P2-r2 history unchanged')
 for n in ['VALIDATION.json','AUDIT-VALIDATION.json','ADDENDUM-VALIDATION.json','COST-VALIDATION.json']:
  v=read(n);need(v['status']=='PASS' and v['checks_count']==len(v['checks']),'validation count/status consistent '+n)
 for n,ident in read('ADDENDUM-VALIDATION.json')['preserved_original_files'].items():
  b=(H/n).read_bytes();need(len(b)==ident['bytes'] and r.sha(b)==ident['sha256'],'addendum immutable input/projection identity '+n)
 need(read('CHECKPOINT.json')['status']=='HANDOFF' and read('RESULT.json')['admission'] is False,'one-stage HANDOFF/no admission')
 r.write('PACKET-CHECK.json',{'status':'PASS','checks_count':len(checks),'checks':checks,'scope':'Final post-edit compact-member consistency, metadata and immutable history; no native or policy change','admission':False});print(json.dumps({'status':'PASS','checks':len(checks)}))
if __name__=='__main__':main()
