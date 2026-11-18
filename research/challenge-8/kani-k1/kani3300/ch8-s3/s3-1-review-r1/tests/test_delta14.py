"""Independent bounded synthetic delta regressions; no native tool invocation."""
import copy,gzip,hashlib,json,tempfile,unittest
from pathlib import Path
from unittest import mock
import runner as r
import s3_campaign as c
import s3_evidence as ev
import test_s3 as f
import pack_evidence

MISSING=object()
def encode(value):return json.dumps(value,indent=2,sort_keys=True).encode()+b'\n'
def get(packet,name):return json.loads(packet['files'][name]['text'])
def put(packet,name,value):
    data=encode(value);packet['files'][name]={'text':data.decode(),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'encoding':'utf-8'}
def reseal(packet,rid):
    name='completed/'+rid+'.json';seal=get(packet,name)
    for member in seal['files']:seal['files'][member]=packet['files'][member]['sha256']
    put(packet,name,seal)
def mutate(target,key,value):
    if value is MISSING:target.pop(key)
    else:target[key]=value

class Delta14(unittest.TestCase):
    def test_state_status_independent_error_stop_and_prefix_preservation(self):
        for state in ('COMPLETE','FAILED','IN_PROGRESS','INTERRUPTED'):
            for status in ('COMPLETE','FAILED','UNKNOWN'):
                for kind in ('drift','unreadable'):
                    case=f.CampaignTests();case.setUp();launches=[]
                    def invoke(std,tool,out,req,rid,limits,slot):
                        launches.append(rid);sup=case.emit(out,rid)
                        if rid==c.p.ORDER[2]:
                            path=out/'groups'/('s3-'+rid)/'receipt.json';doc=c.read(path)
                            doc.update(state=state,status=status,reason='independent original failure',original_exception={'message':'retained original'})
                            doc['execution'].update(original_exit_code=-9,signal=9)
                            if kind=='drift':doc['source_after']['std_sha']='f'*40
                            else:doc['snapshot_errors']=[{'stage':'after','binary':'cbmc','error':'EACCES original'}];doc['binary_identity']='UNKNOWN'
                            c.atomic(path,doc)
                        return sup
                    with self.subTest(state=state,status=status,kind=kind),tempfile.TemporaryDirectory() as d:
                        out=Path(d)
                        with mock.patch.object(c.snapshots,'capture',side_effect=f.synthetic_capture):
                            self.assertEqual(c.run_campaign(Path('/std'),Path('/tool'),out,case.req,invoker=invoke),1)
                        self.assertEqual(launches,list(c.p.ORDER[:3]));terminal=c.read(out/'receipt.json')
                        self.assertEqual(terminal['state'],'STOPPED');self.assertTrue(terminal['stop_reason'])
                        self.assertEqual(list(c.sealed(out)),list(c.p.ORDER[:2]))
                        self.assertTrue(all(row['status']=='NOT_RUN' for row in terminal['rows'][3:]))
                        self.assertEqual(c.read(out/'workers'/(c.p.ORDER[2]+'-lifecycle.json'))['post']['state'],'COMPLETE')
                        path=out/'groups'/('s3-'+c.p.ORDER[2])/'receipt.json';original=path.read_bytes()
                        prefix={n:r.sha256(out/n) for seal in c.sealed(out).values() for n in seal['files']}
                        c.fallback(out,case.req)
                        self.assertEqual(path.read_bytes(),original)
                        self.assertEqual(prefix,{n:r.sha256(out/n) for n in prefix})
                        self.assertEqual(c.read(path)['execution']['original_exit_code'],-9)

    def test_resealed_portable_all_source_tool_identity_fields(self):
        checks=[]
        def hook(out,upload,req):
            archive=upload/pack_evidence.NAME;original=archive.read_bytes();raw=json.loads(gzip.decompress(original));rid=c.p.ORDER[0];gid='s3-'+rid
            for location in ('compile','source_under_test','group'):
                for key in ev.IDENTITIES:
                    for value in (MISSING,None,[],17,'f'*40):
                        packet=copy.deepcopy(raw);gpname='groups/'+gid+'/receipt.json';metaname='groups/'+gid+'/binding-metadata.json';compname='groups/'+gid+'/compile/receipt.json'
                        gp=get(packet,gpname);meta=get(packet,metaname);comp=get(packet,compname)
                        target=comp if location=='compile' else gp['source_under_test'] if location=='source_under_test' else gp
                        mutate(target,key,value)
                        if location=='compile':
                            put(packet,compname,comp)
                            for item in meta['artifacts']:
                                if item['path']=='compile/receipt.json':item.update(bytes=packet['files'][compname]['bytes'],sha256=packet['files'][compname]['sha256'])
                        elif location=='source_under_test':meta['source_under_test']=copy.deepcopy(gp['source_under_test'])
                        put(packet,metaname,meta);gp['binding_metadata'].update(bytes=packet['files'][metaname]['bytes'],sha256=packet['files'][metaname]['sha256']);put(packet,gpname,gp);reseal(packet,rid)
                        archive.write_bytes(gzip.compress(json.dumps(packet).encode(),mtime=0))
                        with self.subTest(location=location,key=key,value=str(value)),self.assertRaisesRegex(c.GlobalFailure,'replay protected/provenance'):
                            c.collect([upload],req)
                        checks.append((location,key))
            archive.write_bytes(original)
        f.PortableReplayTests().exercise(replay_hook=hook)
        self.assertEqual(len(checks),60)

    def test_resealed_portable_protected_errors_all_worker_states(self):
        def hook(out,upload,req):
            archive=upload/pack_evidence.NAME;original=archive.read_bytes();raw=json.loads(gzip.decompress(original));rid=c.p.ORDER[0];name='groups/s3-'+rid+'/receipt.json'
            for state in ('COMPLETE','FAILED','IN_PROGRESS','INTERRUPTED'):
                for key,value in [('source_after_error',{'message':'recorded drift'}),('snapshot_errors',[{'error':'recorded EIO'}]),('source_after',None),('binary_identity','UNKNOWN')]:
                    packet=copy.deepcopy(raw);doc=get(packet,name);doc.update(state=state);doc[key]=value;put(packet,name,doc);reseal(packet,rid)
                    archive.write_bytes(gzip.compress(json.dumps(packet).encode(),mtime=0))
                    with self.subTest(state=state,key=key),self.assertRaisesRegex(c.GlobalFailure,'replay protected/provenance'):
                        c.collect([upload],req)
            archive.write_bytes(original)
        f.PortableReplayTests().exercise(replay_hook=hook)

    def test_original_error_exit_and_later_notrun_retained_in_stopped_replays(self):
        for state,kind in [('FAILED','source'),('COMPLETE','source'),('FAILED','binary'),('COMPLETE','binary')]:
            def fault(out,rid):
                if rid!=c.p.ORDER[2]:return
                path=out/'groups'/('s3-'+rid)/'receipt.json';doc=c.read(path)
                doc.update(state=state,reason='original failure',original_exception={'message':'original exception'})
                doc['execution'].update(original_exit_code=-15,signal=15)
                if kind=='source':doc.pop('source_after');doc['source_after_error']={'message':'original protected drift','errno':5}
                else:doc['snapshot_errors']=[{'stage':'after','binary':'cbmc','error':'original read failure'}];doc['binary_identity']='UNKNOWN'
                c.atomic(path,doc)
            with self.subTest(state=state,kind=kind):
                result=f.PortableReplayTests().exercise(fault=fault)
                self.assertEqual(result['state'],'GLOBAL_STOPPED_PENDING_REVIEW');self.assertTrue(result['global_stop'])
                worker=result['global_stops'][0]['worker_evidence'][0]
                self.assertEqual(worker['state'],state);self.assertEqual(worker['original_exit_code'],-15);self.assertEqual(worker['signal'],15)
                self.assertEqual(worker['original_exception']['message'],'original exception')
                self.assertIn('source_after_error' if kind=='source' else 'snapshot_errors',worker)

if __name__=='__main__':unittest.main(verbosity=2)
