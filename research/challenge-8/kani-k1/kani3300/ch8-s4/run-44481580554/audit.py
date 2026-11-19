#!/usr/bin/env python3
"""Supplemental bounded source/guard/dependency audit; no native tools."""
import collections,copy,gzip,hashlib,json,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;G0=HERE.parents[5];BASE='research/challenge-8/kani-k1/'
SOURCE=Path('/root/verify-rust-std-ch8-s4p-1-w13');CONTROL=Path('/root/kani-ch8-s4p-1-r1-control-w13')
def sha(b):return hashlib.sha256(b).hexdigest()
def read(n):return json.loads((HERE/n).read_bytes())
def write(n,d):(HERE/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
def blob(repo,rev,path):return subprocess.check_output(['git','-C',str(repo),'show',rev+':'+path])
checks=[]
def need(x,label):
 if not x:raise AssertionError(label)
 checks.append(label)
def source_context(b,n):
 lines=b.decode().splitlines();return '\n'.join(f'{i+1}: {lines[i]}' for i in range(max(0,n-5),min(len(lines),n+4)))
def main():
 pins=read('INPUTS.json')['terminal_inputs'];req=read('ROOTS.json')['request'];q=read('QUALIFICATION.json');props=read('NATIVE-PROPERTIES.json');cost=read('COST.json');prov=read('PROVENANCE.json')
 # Verify full immutable author and review manifests against their recorded pins.
 manifests=[]
 for key in ['package','independent_review']:
  pin=pins[key];prefix=BASE+pin['path']+'/';b=blob(G0,pin['g0'],prefix+'MANIFEST.sha256')
  need(sha(b)==pin['manifest_sha256'],key+' exact pinned manifest digest');count=0
  for line in b.decode().splitlines():
   if not line.strip():continue
   h,n=line.split(maxsplit=1);n=n.lstrip('*');need(not Path(n).is_absolute() and '..' not in Path(n).parts,key+' manifest safe path '+n)
   need(sha(blob(G0,pin['g0'],prefix+n))==h,key+' immutable member '+n);count+=1
  manifests.append({'kind':key,'commit':pin['g0'],'manifest_sha256':sha(b),'validated_files':count})
 review_path=BASE+pins['independent_review']['path']+'/FINDINGS.json';review=json.loads(blob(G0,pins['independent_review']['g0'],review_path))
 need(review['verdict']=='APPROVE' and review['repair_author_commit']==pins['package']['g0'] and review['control_sha']==pins['package']['control']['sha'] and review['new_findings']==[] and review['blockers']==[] and {x['id']:x['status'] for x in review['findings']}=={'R14-01':'CLOSED','R14-02':'CLOSED'},'review14 exact approval and both gate closures')
 go_path=BASE+pins['root_go']['path']+'/ROOT-RECHECK.json';go=json.loads(blob(G0,pins['root_go']['g0'],go_path))
 need(go['source']['sha']==req['std_sha'] and go['control']['sha']==pins['package']['control']['sha'] and go['tool']['sha']==req['tool_sha'] and go['request_sha256']==pins['request']['sha256'] and go['workflow_sha256']==pins['request']['workflow_sha256'] and go['verdict']=='APPROVE' and go['blockers']==[],'rootGO exact dependencies/request/workflow')
 write('DEPENDENCIES.json',{'validated_manifests':manifests,'review':{'commit':pins['independent_review']['g0'],'path':review_path,'sha256':sha(blob(G0,pins['independent_review']['g0'],review_path)),'findings':review},'rootGO':{'commit':pins['root_go']['g0'],'path':go_path,'sha256':sha(blob(G0,pins['root_go']['g0'],go_path)),'status':'Exact identity tuple matches; consumed one campaign only'},'host305':'Prior source/control regression evidence only; not native proof or fit evidence'})
 # Retain all SUCCESS guards without treating unsupported operations as supported.
 guards=[]
 for row in q['rows']:
  if not isinstance(row['unsupported_guards'],list):continue
  for p in row['unsupported_guards']:
   rel=p['file'].split('/export/',1)[1];b=blob(SOURCE,req['std_sha'],rel);n=int(p['line'])
   if p['id']=='kani::mem::cbmc::same_allocation.unsupported_construct.1':
    argument='The bounded native inventory reports SUCCESS for the guard against pointers to unallocated memory. The exact harness uses a live initialized backing34 and interior slice base1; logical Cell values use new/get/set. This is source context, not ownership/provenance inferred from pointer equality.'
   elif p['id'].startswith('panic::location::'):
    argument='The bounded native inventory reports SUCCESS for the unsupported caller_location guard at Location::caller. No supported semantics for caller_location or generic panic paths are inferred; this finite normal-return harness does not supply a general panic theorem.'
   else:
    need(p['id']=='panicking::panic_nounwind_fmt::runtime.unsupported_construct.1','only exact observed guard families')
    argument='The bounded native inventory reports SUCCESS for the unsupported foreign Rust rust_begin_unwind guard in panic_nounwind_fmt::runtime. This preserves the system guard and native status; generic panic/unwind behavior and emitter reachability remain outside this source-local assessment.'
   need(p['status']=='SUCCESS','guard retained exact SUCCESS '+row['id']+'/'+p['id'])
   guards.append({'root':row['id'],'selector':row['selector'],'invocation_id':next(r['invocation_id'] for r in read('ROOTS.json')['rows'] if r['id']==row['id']),'property':p,'source_sha':req['std_sha'],'source_file':rel,'source_sha256':sha(b),'source_context':source_context(b,n),'assessment':'SOURCE_REPORTED_GUARD_SUCCESS_ONLY','source_local_context':argument,'independent_guard_reachability_or_MIR_proof':'UNKNOWN','unsupported_operation_general_support_claim':False,'producer_policy':'Unchanged; strict rejects nonempty unsupported_constructs'})
 need(len(guards)==7,'all7 observed guard instances audited')
 write('GUARD-ARGUMENTS.json',{'instances':guards,'count':7,'network_guard_counts':'UNKNOWN_CENSORED','general_support_or_admission':False})
 # Explicit positive length blocks and feasible witnesses: no impossible N0/1 claim.
 blocks=[]
 for row in q['rows'][4:]:
  planned=next(r for r in req['rows'] if r['id']==row['id']);lo,hi=row['domain']['length_interval'];lengths=[r for r in row['literal_roles'] if r['required']['class']=='cover' and r['required']['description'][-4:-2]=='_N'];witnesses=[r for r in row['literal_roles'] if r['required']['class']=='cover' and r not in lengths]
  need(len(lengths)==hi-lo+1 and len(witnesses)==5 and all(r['required']['description'].endswith(f'_N{n:02}') for r,n in zip(lengths,range(lo,hi+1))),'exact length labels and5 witnesses '+row['id'])
  observed=row['native_verdict']=='SUCCESS'
  need(all(r['exact_match']==observed for r in lengths+witnesses),'all length/witness observed or UNKNOWN '+row['id'])
  roles=[r for r in row['literal_roles'] if r['required']['class']=='assertion'];need(len(roles)==4 and all(r['exact_match']==observed for r in roles),'four concrete SUCCESS roles or UNKNOWN '+row['id'])
  blocks.append({'root':row['id'],'domain':row['domain'],'required_length_covers':hi-lo+1,'length_records':lengths,'five_feasible_witnesses':witnesses,'four_roles':roles,'state':'OBSERVED_SOURCE_REPORTED_PENDING_REVIEW_LOCATION' if observed else 'UNKNOWN_CENSORED','feasibility':'UNSORTED/DUPLICATE/NONCONSTANT are existential only for n>=2; MAX_DESCENDING uses the block maximum; USEFUL_RETURN true. No witness for an impossible N0/1 condition is claimed.','all34_values':'Independent kani::any<[u8;34]>; initialized logical Cell array via34 set calls or initialized u8 array; no inherited u8 Cell-provider credit','assumed_summary_edges':[],'admitted':False})
 need([x['required_length_covers'] for x in blocks]==[3,2,3,2],'perlength cover requirement3/2/3/2')
 write('LENGTH-ROLES-SAT.json',{'blocks':blocks,'observed_SAT':15,'network_required_but_UNKNOWN':15,'fallback_union0_4':'Potential finite union only after independent14 and separate admission; NOT_ADMITTED','summary_provider_init_MIR_credit':'NONE'})
 # Compare old original packets with the actual independent review recommendations.
 comparisons=[]
 for commit,dir in [('a9fe0055aab3279e3f5bb71bde9667925da80e65','run-44416629057-review-w14'),('028531727fc48ef9f26f16dfb95c2b2666c96dd7','run-44439462279-review-w14')]:
  prefix=BASE+'kani3300/ch8-s3/'+dir+'/';raw=blob(G0,commit,prefix+'LOCATION-DECISION.json');d=json.loads(raw);find=json.loads(blob(G0,commit,prefix+'FINDINGS.json'))
  records=[d['exact_property']] if 'exact_property' in d else [x['exact_property'] for x in d['cases']]
  need(len(records)==(1 if dir.startswith('run-444166') else 3),'old independently reviewed exactcase cardinality')
  for p in records:need(all(k in p and p[k] is None for k in ['file','line']) and p['class']=='unreachable' and p['status']=='SUCCESS' and p['description']=='unreachable code','old exact null keys class/status shape')
  comparisons.append({'review_commit':commit,'path':prefix+'LOCATION-DECISION.json','sha256':sha(raw),'recommendation':d['recommendation'],'status':d['status'],'properties':records,'findings':find,'comparison':'Same display-zero/null/class/status/description structure; new run/IDs/namespace/source/control/request/protected tuple differ. Existing old review/admission never transfers; shared emitter or source/MIR origin UNKNOWN.'})
 write('LOCATION-COMPARISON.json',{'reviews':comparisons,'old_admissions':'LOCATION-PROPOSAL.json old_packets pins f740/ff193 exact original decisions','new_cases':'Two exact fallback cases proposed NOT_APPLIED only','shared_emitter':'UNKNOWN','new_waiver_or_admission':False})
 # Check protected snapshots remain complete in UNKNOWN rows too, preserving errors.
 prot=read('PROTECTED.json');need(prot['baseline']['errors']==[],'baseline no observed errors')
 epochs=[]
 for e in prot['epochs']:
  life=e['lifecycle'];need(life['pre']['errors']==life['post']['errors']==[],'controller epochs errors preserved empty '+e['id'])
  epochs.append({'root':e['id'],'baseline_epoch':prot['baseline']['epoch'],'pre_epoch':life['pre']['epoch'],'post_epoch':life['post']['epoch'],'inner_after_absent':e['protected']['inner_after_absent'],'controller_recovery_used':e['protected']['controller_recovery_used'],'observed_errors_ignored':False,'errno_and_runtime_diagnostics':'COST.json rows/lifecycle_diagnostics; exact original structured supervision retained in compact member'})
 write('EPOCH-AUDIT.json',{'rows':epochs,'binary_path_sha_snapshots':'PROTECTED.json','canonical_path_assurance':'Exported snapshot paths/identities and exact reviewed capture code; independent physical inode/realpath causality UNKNOWN','B01_B02':'Source/reader identity and gate closures inherited from exact reviewed control, actual all-state readers replayed; interrupted missing-AFTER recovery not needed in this run','no_errors_suppressed':True})
 write('AUDIT-VALIDATION.json',{'status':'PASS','checks_count':len(checks),'checks':checks,'scope':'Targeted dependency, source-local guards, exact length/roles/SAT, historical reviews, epoch checks; no native/compiler/CI'})
 print(json.dumps({'audit':'PASS','checks':len(checks),'guards':7,'positive_blocks':4,'old_reviews':2}))
if __name__=='__main__':main()
