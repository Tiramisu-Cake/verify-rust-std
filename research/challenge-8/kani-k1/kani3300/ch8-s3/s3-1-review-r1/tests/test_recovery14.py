"""Distinguish valid interrupted absence in local/upload-only readers."""
import copy,gzip,json,unittest
import test_s3 as f
import s3_campaign as c
import pack_evidence
from test_delta14 import get,put,reseal

class Recovery14(unittest.TestCase):
    def test_verified_interrupted_absence_recovers_locally_and_portably(self):
        def hook(out,upload,req):
            archive=upload/pack_evidence.NAME;original=archive.read_bytes();packet=json.loads(gzip.decompress(original));rid=c.p.ORDER[2]
            group='groups/s3-'+rid+'/receipt.json';rowname=rid+'/receipt.json';supname='workers/'+rid+'-supervision.json';lifename='workers/'+rid+'-lifecycle.json';sealname='completed/'+rid+'.json'
            doc=get(packet,group);doc['state']='IN_PROGRESS'
            for key in ('source_after','tool_fingerprints_after','binary_identity'):doc.pop(key)
            doc['execution'].update(original_exit_code=-15,signal=15);doc['execution_exception']={'message':'original interruption'}
            sup=get(packet,supname);sup.update(worker_exit=-15,cutoff='slot_wall')
            life=get(packet,lifename);life['supervision']=copy.deepcopy(sup)
            row=get(packet,rowname);row.update(status='UNKNOWN',outcome='UNKNOWN',s3_expected_match=False,invocation_original_exit=-15,invocation_signal=15,s3_supervision=sup,
                worker_protected_evidence={'inner_after_absent':['source_after','tool_fingerprints_after'],'controller_recovery_used':True,'observed_errors_ignored':False})
            terminal=get(packet,'receipt.json');terminal['state']='SELECTED_PARTIAL';terminal['rows']=[row if x['id']==rid else x for x in terminal['rows']]
            seal=get(packet,sealname);seal.update(supervision=sup,expected_match=False)
            changes={group:doc,rowname:row,supname:sup,lifename:life,sealname:seal,'receipt.json':terminal}
            for name,value in changes.items():put(packet,name,value)
            reseal(packet,rid)
            old_local={name:(out/name).read_bytes() for name in changes}
            try:
                for name in changes:(out/name).write_text(packet['files'][name]['text'])
                archive.write_bytes(gzip.compress(json.dumps(packet).encode(),mtime=0))
                local=c.collect([out],req);portable=c.collect([upload],req)
                self.assertEqual(portable,local);self.assertFalse(local['global_stop'])
                self.assertEqual(len(local['rows']),9)
                result=next(x for x in local['rows'] if x['id']==rid)
                self.assertEqual(result['outcome'],'UNKNOWN');self.assertEqual(result['invocation_original_exit'],-15)
                self.assertTrue(result['worker_protected_evidence']['controller_recovery_used'])
                self.assertTrue(all(x.get('s3_expected_match') for x in local['rows'] if x['id'] in c.p.ORDER[3:]))
            finally:
                for name,data in old_local.items():(out/name).write_bytes(data)
                archive.write_bytes(original)
        f.PortableReplayTests().exercise(replay_hook=hook)

if __name__=='__main__':unittest.main(verbosity=2)
