"""Independent regressions against exact1dfc. Synthetic Python only."""
import copy, json, sys, unittest
from pathlib import Path
from unittest import mock
CONTROL=Path('/root/kani-ch8-s3-1-final-control-w13/ch8-s1-control')
sys.path.insert(0,str(CONTROL))
import runner as r
import collect as collector
import s3_campaign as campaign
import test_s3

class ProvenanceFindings(unittest.TestCase):
    def test_reproduce_stale_source_in_actual_singleton_writer(self):
        writes=[];original=r._write_json
        def record(path,value):
            writes.append((str(path),copy.deepcopy(value)))
            return original(path,value)
        case=test_s3.SingletonRunnerTests()
        try:
            with mock.patch.object(r,'_write_json',side_effect=record):
                result,fatal,gp,_=case.exercise()
            self.assertIsNone(fatal)
            wanted=r.load_request()['std_sha']
            compiles=[v for path,v in writes if path.endswith('/compile/receipt.json')]
            self.assertTrue(compiles)
            self.assertEqual(gp['std_sha'],wanted)
            self.assertEqual(gp['source_before']['std_sha'],wanted)
            self.assertEqual(compiles[-1]['state'],'COMPLETE')
            self.assertEqual(compiles[-1]['std_sha'],r.STD_SHA)
            self.assertNotEqual(compiles[-1]['std_sha'],wanted)
            self.assertEqual(gp['source_under_test']['base_std_sha'],r.STD_SHA)
            self.assertNotEqual(gp['source_under_test']['base_std_sha'],wanted)
            print(json.dumps({'finding':'R14-01','new_std':wanted,'compile_std':compiles[-1]['std_sha'],
                'source_under_test_base':gp['source_under_test']['base_std_sha'],
                'group_state':gp['state'],'scope':'synthetic execution; actual writer and source binding code'}))
        finally:case.doCleanups()

    def test_portable_collector_accepts_those_stale_compile_identities(self):
        seen=[];original=collector.read
        def read(path):
            value=original(path)
            if str(path).endswith('/compile/receipt.json'):seen.append(copy.deepcopy(value))
            return value
        case=test_s3.PortableReplayTests('test_same_invocation_stock_rich_metadata_and_upload_only_replay')
        try:
            with mock.patch.object(collector,'read',side_effect=read):
                case.test_same_invocation_stock_rich_metadata_and_upload_only_replay()
            wanted=r.load_request()['std_sha']
            self.assertGreaterEqual(len(seen),18)
            self.assertTrue(all(v['state']=='COMPLETE' and v['std_sha']==r.STD_SHA!=wanted for v in seen))
            print(json.dumps({'finding':'R14-01','accepted_compile_receipts':len(seen),
                'accepted_stale_std':r.STD_SHA,'expected_std':wanted,'local_and_upload_replay':'ACCEPTED',
                'scope':'complete synthetic stock/rich/native-metadata campaign; no native execution'}))
        finally:case.doCleanups()

class SnapshotFindings(unittest.TestCase):
    def test_recorded_failed_worker_protected_capture_does_not_stop_later_roots(self):
        for failure in ('source_drift','binary_unreadable'):
            fixture=test_s3.CampaignTests();fixture.setUp()
            launches=[]
            def invoke(std,tool,out,request,rid,limits,slot):
                launches.append(rid)
                sup=fixture.emit(out,rid)
                if rid==test_s3.p.ORDER[2]:
                    gp=out/'groups'/('s3-'+rid)/'receipt.json'
                    doc=campaign.read(gp);doc['state']='FAILED'
                    if failure=='source_drift':
                        doc.pop('source_after')
                        doc['source_after_error']={'type':'RunnerError','operation':'snapshot.source_after',
                            'epoch':'WORKER_POST','message':'std HEAD drift'}
                    else:
                        doc['binary_identity']='UNKNOWN'
                        doc['snapshot_errors']=[{'stage':'after','binary':'cbmc','error':'PermissionError: unreadable'}]
                        doc['tool_fingerprints_after']['required_hashes_present']=False
                    campaign.atomic(gp,doc)
                    row=out/rid/'receipt.json';result=campaign.read(row)
                    result.update(outcome='UNKNOWN',reason='recorded protected capture failure')
                    campaign.atomic(row,result)
                return sup
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                with mock.patch.object(campaign.snapshots,'capture',side_effect=test_s3.synthetic_capture):
                    code=campaign.run_campaign(Path('/std'),Path('/tool'),Path(d),fixture.req,invoker=invoke)
                terminal=campaign.read(Path(d)/'receipt.json')
                self.assertEqual(code,1)
                self.assertEqual(launches,list(test_s3.p.ORDER))
                self.assertIsNone(terminal['stop_reason'])
                self.assertEqual(len(campaign.sealed(Path(d))),9)
                print(json.dumps({'finding':'R14-02','recorded_error':failure,'later_roots_launched':launches[3:],
                    'terminal_state':terminal['state'],'global_stop_reason':terminal['stop_reason'],
                    'scope':'synthetic worker failure plus recovered controller snapshot; actual root_outcome/run_campaign'}))

if __name__=='__main__':unittest.main(verbosity=2)
