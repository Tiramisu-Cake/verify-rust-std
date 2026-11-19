#!/usr/bin/env python3
"""Targeted independent projections and adverse reader checks; no evidence fetch."""
import collections,copy,gzip,importlib,json,sys,tempfile
from pathlib import Path
sys.dont_write_bytecode=True
import replay as r
def main():
    H=r.HERE; packet=json.loads(gzip.decompress((H/'group-evidence.json.gz').read_bytes())); bs={n:r.decode(e) for n,e in packet['files'].items()};d={n:json.loads(b) for n,b in bs.items()};req=d['campaign-start.json']['request_data'];qs=json.loads((H/'QUALIFICATION.json').read_text())['rows'];us=json.loads((H/'U-ARGUMENTS.json').read_text())['instances'];props=json.loads((H/'NATIVE-PROPERTIES.json').read_text());guards=json.loads((H/'GUARD-ARGUMENTS.json').read_text())['instances'];checks=[]
    def need(x,label):
        if not x:raise AssertionError(label)
        checks.append(label)
    source={};sites={};expectedU={};expectedG={};location_cases=[]
    source_paths=set(r.git(r.SOURCE,'ls-tree','-r','--name-only',req['std_sha']).decode().splitlines())
    tool_paths=set(r.git(r.TOOL,'ls-tree','-r','--name-only',req['tool_sha']).decode().splitlines())
    for q in qs:
        rid=q['id']; gp='groups/s3-'+rid+'/'; ps=d[gp+'properties.json']['harnesses'][0]['properties'];h=d[gp+'export.json']['harnesses'][0]
        need(props[rid]['properties']==ps and q['n_properties']==len(ps),'exact native projection '+rid)
        need(q['status_counts']==dict(collections.Counter(p['status'] for p in ps)),'status counts '+rid)
        need(q['checks']==h['checks'] and q['covers_summary']==h['covers'],'native summary preserved '+rid)
        for p in ps:
            need(r.located(p) and p['file'].startswith(str(r.STD)+'/'),'exact positive coordinate and source namespace '+rid+'/'+p['id'])
            rel=p['file'].removeprefix(str(r.STD)+'/');n=int(p['line']);key=(rel,n)
            if rel in source_paths:
                if rel not in source:source[rel]=r.blob(r.SOURCE,req['std_sha'],rel)
                ls=source[rel].decode().splitlines();need(n<=len(ls),'coordinate within pinned std source '+rid+'/'+p['id'])
                site={'file':rel,'line':n,'source_sha':req['std_sha'],'source_sha256':r.sha(source[rel]),'source_line':ls[n-1],'coordinate_kind':'STD_SOURCE'}
            elif rel=='library/kani_core/src/models.rs' and rel in tool_paths:
                b=r.blob(r.TOOL,req['tool_sha'],rel);ls=b.decode().splitlines()
                need(p['id']=='<usize as kani::rustc_intrinsics::ToISize>::to_isize.unreachable.1' and p['class']=='unreachable' and p['description']=='unreachable code' and p['status']=='SUCCESS' and n==203,'exact stock Kani model coordinate '+rid)
                site={'file':rel,'line':n,'source_sha':req['tool_sha'],'source_sha256':r.sha(b),'source_line':ls[n-1],'coordinate_kind':'STOCK_KANI_MODEL_SOURCE_REPORTED'}
                location_cases.append({'root':rid,'property':p,'invocation_id':q['invocation_id'],'namespace':q['namespace'],'members':q['members'],'source_file':rel,'source_sha':req['tool_sha'],'source_sha256':r.sha(b),'source_context':r.context(b,n),'assessment':'S1_SOURCE_REPORTED_LOCATION_CANDIDATE','argument':'The native display names the exact stock Kani ToISize model, not a std implementation. Pinned tool models.rs:203 defines usize::to_isize; a failed conversion executes its separate safety_check(false) before unreachable!. Preserve this SUCCESS system check and all sibling safety checks. Native normalization prepends the export root to the relative display; no physical std file or independent MIR source mapping is claimed. Retain the exact full dictionary and complete same-invocation inventory. No missing-location waiver or generic conversion theorem is proposed.','admitted':False})
            elif rel=='<builtin-library-memcpy>' and p['id'] in ('memcpy.pointer.1','memcpy.pointer.2'):
                need(p['class']=='pointer' and p['status']=='SUCCESS' and (p['id'],n) in [('memcpy.pointer.1',33),('memcpy.pointer.2',34)],'exact builtin memcpy coordinate '+rid+'/'+p['id'])
                site={'file':rel,'line':n,'coordinate_kind':'NATIVE_BACKEND_BUILTIN_DISPLAY','source_sha':'UNKNOWN_NOT_EXPORTED','source_sha256':None,'source_line':None}
                location_cases.append({'root':rid,'property':p,'invocation_id':q['invocation_id'],'namespace':q['namespace'],'members':q['members'],'protected_identity':'PROTECTED.json exact E0/pre/BEFORE/AFTER/post CBMC binary hashes','assessment':'S1_SOURCE_REPORTED_LOCATION_CANDIDATE','argument':'This exact SUCCESS pointer-system property reports a CBMC builtin memcpy pseudo-file at native line33 or34; it is not a missing coordinate or a Rust source site. Retain the exact id/class/description/location_display/canonical file/line, successful native check, complete counts, roles, SAT covers and all other safety properties for this invocation. The protected backend identity binds the source-reported producer observation. As with the S3-1-r2/S4P1 exact system-record method, unknown actual source/lowering origin is disclosed rather than replaced by a guessed std coordinate. This is a per-record metadata candidate at S1 source-reported level only; no new general parser waiver, backend-library-source correctness or independent AST/MIR claim.','backend_builtin_source_identity':'UNKNOWN_NOT_EXPORTED; no raw library/binary/log inspection performed','admitted':False})
            else:raise AssertionError('BLOCKER unargued location '+rid+'/'+str(p))
            entry=sites.setdefault(key,dict(site,instances=[]));entry['instances'].append({'root':rid,'id':p['id'],'status':p['status'],'class':p['class'],'location_display':p['location_display']})
            if p['status']=='UNREACHABLE':expectedU[rid,p['id']]=p
            if p['class']=='unsupported_construct':expectedG[rid,p['id']]=p
    need(len(us)==len(expectedU)==67 and len({(x['root'],x['property']['id']) for x in us})==67,'U argument coverage is exact bijection, no duplicates')
    for u in us:
        rid=u['root'];p=u['property'];need(expectedU[rid,p['id']]==p,'exact U dictionary '+rid+'/'+p['id'])
        need(u['source_sha256']==r.sha(source[u['source_file']]) and u['source_context']==r.context(source[u['source_file']],u['source_line']),'exact U source/hash/context '+rid+'/'+p['id'])
        arg,premises=r.argument(rid,p);need(arg==u['source_local_argument'] and premises==u['premises'] and arg and u['assessment']=='S1_SOURCE_LOCAL_CANDIDATE','U source-local argument '+rid+'/'+p['id'])
        q=next(q for q in qs if q['id']==rid);need(u['invocation_id']==q['invocation_id'] and u['namespace']==q['namespace'] and u['member_sha256']==r.sha(bs[u['member']]),'U invocation/member identity '+rid+'/'+p['id'])
    need(len(guards)==len(expectedG)==13 and {(g['root'],g['property']['id']) for g in guards}==set(expectedG),'all13 exact successful guards covered')
    for g in guards:need(g['property']==expectedG[g['root'],g['property']['id']] and g['source_sha256']==r.sha(source[g['source_file']]),'exact guard/source dictionary '+g['root']+'/'+g['property']['id'])
    # Exact S1-policy and precedent identities; read narrow policy files, not old evidence.
    refs=[]
    for rel in ['research/challenge-8/kani-k1/S1-ACCEPTANCE-DECISION-2026-11-17.md',r.BASE+'ch8-s3/s3-1-r2/U-SITE-PROPOSAL.json',r.BASE+'ch8-s3/admission-r2-qualified/ACCEPTANCE.md',r.BASE+'ch8-s3/admission-r2-location/ADMISSION.md',r.BASE+'ch8-s4/admission-s4p1-r1-fallback/ADMISSION.md',r.BASE+'ch8-s4/admission-s4p1-r1-fallback/ADMISSION.json',r.BASE+'ch8-s4/run-44505531344/replay.py',r.BASE+'ch8-s4/run-44505531344/acquire.py']:
        b=r.blob(r.G0,'8a1ea2ac1c2a4a06273f38784208a70ecc31d7c6',rel);refs.append({'commit':'8a1ea2ac1c2a4a06273f38784208a70ecc31d7c6','path':rel,'bytes':len(b),'sha256':r.sha(b)})
    # Pin tool semantics supporting guard interpretation, without claiming a MIR trace.
    toolsites=[]
    for f,a,b in [('library/kani_core/src/mem.rs',261,273),('library/kani_core/src/lib.rs',585,596),('kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs',129,146),('kani-compiler/src/codegen_cprover_gotoc/codegen/assert.rs',270,299),('kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs',202,225),('kani-compiler/src/codegen_cprover_gotoc/codegen/foreign_function.rs',245,262),('kani-compiler/src/intrinsics.rs',298,304)]:
        raw=r.blob(r.TOOL,req['tool_sha'],f);ls=raw.decode().splitlines();toolsites.append({'file':f,'sha':req['tool_sha'],'sha256':r.sha(raw),'lines':[a,b],'context':'\n'.join(f'{i+1}: {ls[i]}' for i in range(a-1,b))})
    adverses=[]
    with tempfile.TemporaryDirectory(prefix='network-r2-audit-') as td:
        tmp=Path(td);reader=tmp/'reader';reader.mkdir()
        for n in r.git(r.CONTROL,'ls-tree','-r','--name-only',r.HEAD,'ch8-s1-control').decode().splitlines():
            p=reader/Path(n).relative_to('ch8-s1-control');p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(r.blob(r.CONTROL,r.HEAD,n))
        sys.path.insert(0,str(reader));pub=importlib.import_module('collect');c=importlib.import_module('s4p2r2_campaign');pol=importlib.import_module('s4p2r2_policy');ev=importlib.import_module('s3_evidence')
        local=tmp/'local';upload=tmp/'upload';local.mkdir();upload.mkdir()
        for n,b in bs.items():p=local/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        gz=(H/'group-evidence.json.gz').read_bytes();(upload/'group-evidence.json.gz').write_bytes(gz);original=c.collect([local],req);need(original==pub.collect([upload],req),'authentic local/upload collector equality')
        for label,term in [('present empty object',{}),('schema missing',dict(d['receipt.json'])),('schema null',dict(d['receipt.json'],schema=None)),('schema integer',dict(d['receipt.json'],schema=1))]:
            if label=='schema missing':del term['schema']
            altered=copy.deepcopy(packet);b=r.canon(term);altered['files']['receipt.json']={'encoding':'utf-8','text':b.decode(),'bytes':len(b),'sha256':r.sha(b)};(local/'receipt.json').write_bytes(b);(upload/'group-evidence.json.gz').write_bytes(gzip.compress(r.canon(altered),mtime=0))
            for route in [local,upload]:
                try:pub.collect([route],req)
                except c.GlobalFailure as exc:need(str(exc)=='S4 terminal campaign schema mismatch','reject '+label+'/'+route.name);adverses.append({'test':label,'route':route.name,'result':'REJECT','reason':str(exc)})
                else:raise AssertionError('accepted malformed terminal '+label)
        (local/'receipt.json').write_bytes(bs['receipt.json']);(upload/'group-evidence.json.gz').write_bytes(gz)
        victim=local/qs[-1]['members']['export.json']['member'];saved=victim.read_bytes();victim.write_bytes(saved+b' ')
        try:c.sealed(local)
        except (c.GlobalFailure,ValueError,OSError):adverses.append({'test':'changed sealed positive export','result':'REJECT'})
        else:raise AssertionError('changed sealed export accepted')
        victim.write_bytes(saved)
        rid=qs[-1]['id'];gp='groups/s3-'+rid+'/';changed=copy.deepcopy(d[gp+'receipt.json']);changed['tool_fingerprints_after']['binaries']['kani_driver']['sha256']='0'*64
        try:ev.protected(changed,req,d['baseline.json'],d['workers/'+rid+'-supervision.json'],d['receipt.json']['request_sha256'])
        except ev.EvidenceError:adverses.append({'test':'changed protected driver in successful positive','result':'REJECT'})
        else:raise AssertionError('changed protected driver accepted')
        for q in qs:
            row=next(row for row in req['rows'] if row['id']==q['id']);rid=q['id'];gp='groups/s3-'+rid+'/';need(pol.expected_observation(row,d[rid+'/receipt.json']['export'],d[gp+'properties.json']['harnesses'][0]) is False,'authentic producer rejection '+rid)
        need(c.collect([local],req)==pub.collect([upload],req)==original and all((local/n).read_bytes()==b for n,b in bs.items()),'all authentic evidence restored after temporary adverse checks')
    need(len(location_cases)==13,'all5 tool-model and8 builtin location records have per-instance arguments')
    r.write('LOCATION-SITES.json',{'unique_coordinates':len(sites),'instances':sum(len(x['instances']) for x in sites.values()),'sites':list(sites.values()),'missing_coordinate_count':0,'non_std_coordinate_instances':13,'scope':'Std coordinates checked against pinned std; Kani model coordinates against pinned stock tool; backend pseudo-locations retained as native displays with actual source origin UNKNOWN. No invented coordinate or old waiver.'})
    r.write('LOCATION-ARGUMENTS.json',{'missing_location_cases':[],'non_std_location_cases':location_cases,'count':13,'blockers':[],'admitted':False,'scope':'Per-instance source-reported metadata candidates only. No native null/zero coordinate and no syntactic location waiver required. Backend builtin source/lowering identity UNKNOWN, not established by these coordinates.'})
    r.write('POLICY-REFERENCES.json',{'references':refs,'method':'S1 exact per-site arithmetic/bounds arguments and complete same-invocation role/cover/guard/status inventory, then independent review and separate admission. S3-1-r2 and S4P1 exact missing-location admissions do not transfer.','tool_guard_semantics':toolsites,'independent_compiler_proof':'UNKNOWN_NOT_CLAIMED'})
    r.write('AUDIT-VALIDATION.json',{'status':'PASS','checks_count':len(checks),'checks':checks,'adverse_tests':adverses,'scope':'Targeted offline reporting consistency and frozen reader rejection; no native or full Validate rerun','original_evidence_unchanged':True})
    print(json.dumps({'status':'PASS','checks':len(checks),'adverse_tests':len(adverses),'unique_coordinates':len(sites),'missing_locations':0,'non_std_location_arguments':13}))
if __name__=='__main__':main()
