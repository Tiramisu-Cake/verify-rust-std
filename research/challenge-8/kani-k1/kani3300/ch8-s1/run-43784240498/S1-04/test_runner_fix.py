"""Synthetic patch regressions. Run against a scratch patched runner.py only."""
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import runner

class FixTests(unittest.TestCase):
    def test_porcelain_variant_applies_and_bad_hash_restores(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);repo=root/'source';repo.mkdir()
            subprocess.run(['git','init','-q',str(repo)],check=True)
            rel='library/core/file with spaces.rs';p=repo/rel;p.parent.mkdir(parents=True);p.write_text('original\n')
            subprocess.run(['git','-C',str(repo),'add','.'],check=True)
            subprocess.run(['git','-C',str(repo),'-c','user.name=Synthetic','-c','user.email=synthetic@invalid','commit','-qm','fixture'],check=True)
            patch=root/'overlay.patch';patch.write_text(''.join(difflib.unified_diff(['original\n'],['changed\n'],fromfile='a/'+rel,tofile='b/'+rel)))
            digest=hashlib.sha256(b'changed\n').hexdigest()
            with mock.patch.object(runner,'_variant_info',return_value=(patch,'synthetic',{rel:digest})):
                result,_=runner._run_variant(repo,'activation-default',{})
            self.assertEqual(result,patch);self.assertEqual(p.read_text(),'changed\n')
            subprocess.run(['git','-C',str(repo),'apply','--reverse',str(patch)],check=True)
            with mock.patch.object(runner,'_variant_info',return_value=(patch,'synthetic',{rel:'wrong'})):
                with self.assertRaisesRegex(runner.RunnerError,'changed-file SHA mismatch'):
                    runner._run_variant(repo,'activation-default',{})
            self.assertEqual(p.read_text(),'original\n')
            self.assertEqual(subprocess.check_output(['git','-C',str(repo),'status','--porcelain=v1']),b'')

    def group_fixture(self,out):
        row={'id':'fixture','selector':'fixture::root','mode':'PFC','variant':'activation-default','unwind':34,'timeout_seconds':600}
        group={'id':'activation-default-u34','variant':'activation-default','unwind':34,'rows':[row]}
        return {'changed_file_sha256':{},'source_bindings':{}},group

    def test_variant_error_retained_without_fabricated_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);request,group=self.group_fixture(out);source={'std_sha':runner.STD_SHA}
            with mock.patch.object(runner,'verify_source',return_value=source),mock.patch.object(runner,'binary_fingerprints',return_value={'required_hashes_present':True}),mock.patch.object(runner,'group_memory_budget',return_value={}),mock.patch.object(runner,'_run_variant',side_effect=runner.RunnerError('original variant defect')):
                rows,fatal=runner._run_group(out/'source',out/'tool',out,request,group,10**12)
            self.assertEqual(fatal,'RunnerError: original variant defect')
            receipt=json.loads((out/'groups/activation-default-u34/receipt.json').read_text())
            self.assertEqual(receipt['source_before'],receipt['source_after'])
            self.assertEqual(rows[0]['status'],'UNKNOWN');self.assertEqual(rows[0]['outcome'],'UNKNOWN')

    def test_original_exception_kept_if_cleanup_source_check_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);request,group=self.group_fixture(out)
            with mock.patch.object(runner,'verify_source',side_effect=[{'std_sha':runner.STD_SHA},runner.RunnerError('actual later drift')]),mock.patch.object(runner,'binary_fingerprints',return_value={'required_hashes_present':True}),mock.patch.object(runner,'group_memory_budget',return_value={}),mock.patch.object(runner,'_run_variant',side_effect=runner.RunnerError('original variant defect')):
                _,fatal=runner._run_group(out/'source',out/'tool',out,request,group,10**12)
            self.assertIn('original variant defect',fatal);self.assertIn('actual later drift',fatal)

if __name__=='__main__': unittest.main()
