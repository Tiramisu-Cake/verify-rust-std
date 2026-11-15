"""Synthetic YAML/control/fallback checks; never calls build/toolchain commands."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import yaml
import check_package as c


class PackageTests(unittest.TestCase):
    def test_yaml_valid_and_sensitivity(self):
        source=Path(__file__).with_name('ch8-s1.yml')
        self.assertEqual(c.check_yaml(source)['yaml'],'PASS')
        doc=yaml.load(source.read_text(),Loader=yaml.BaseLoader)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'workflow.yml'
            for mutate in [lambda x:x['on'].update({'workflow_dispatch':{}}),
                lambda x:x['jobs']['s1'].update({'env':{'TEMP':'${{ runner.temp }}'}}),
                lambda x:x['jobs']['s1']['steps'][1]['with'].update({'fetch-depth':'1'}),
                lambda x:x['jobs']['s1'].update({'runs-on':'self-hosted'})]:
                bad=copy.deepcopy(doc);mutate(bad);p.write_text(yaml.safe_dump(bad))
                with self.assertRaises(AssertionError):c.check_yaml(p)

    def test_control_guards_and_payload_drift(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);repo=root/'control';here=repo/'scripts/ch8-s1';here.mkdir(parents=True)
            payload=here/'payload.py';payload.write_text('synthetic')
            rel='scripts/ch8-s1/payload.py'
            req={'status':'READY','std_sha':'a'*40,'ci_payload_sha256':{rel:hashlib.sha256(payload.read_bytes()).hexdigest()},'ci_changed_paths':[rel]}
            (here/'CI-REQUEST.json').write_text(json.dumps(req))
            responses={('rev-parse','HEAD'):'b'*40,('rev-parse','HEAD^'):'a'*40,
                ('rev-list','--parents','-n','1','HEAD'):'b'*40+' '+'a'*40,
                ('status','--porcelain','--untracked-files=no'):'',
                ('diff','--name-only','HEAD^','HEAD'):rel,
                ('ls-tree','-r','--name-only','HEAD','.github/workflows'):'.github/workflows/ch8-s1.yml'}
            env={'GITHUB_REPOSITORY':'Tiramisu-Cake/verify-rust-std','GITHUB_EVENT_NAME':'push',
                 'GITHUB_REF':'refs/heads/uninit-ci/ch8-s1-synthetic','GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':'b'*40}
            with patch.object(c,'HERE',here),patch.object(c,'git',side_effect=lambda repo,*args:responses[args]),patch.dict(os.environ,env,clear=True):
                self.assertEqual(c.control(repo)['status'],'PASS')
                for key,value in [('GITHUB_REPOSITORY','other/repo'),('GITHUB_EVENT_NAME','workflow_dispatch'),
                                  ('GITHUB_REF','refs/heads/main'),('GITHUB_RUN_ATTEMPT','2'),('GITHUB_SHA','c'*40)]:
                    with patch.dict(os.environ,{key:value}):
                        with self.assertRaises(AssertionError):c.control(repo)
                responses[('rev-list','--parents','-n','1','HEAD')]+=' '+'c'*40
                with self.assertRaises(AssertionError):c.control(repo)
                responses[('rev-list','--parents','-n','1','HEAD')]='b'*40+' '+'a'*40
                payload.write_text('drift')
                with self.assertRaises(AssertionError):c.control(repo)
                payload.write_text('synthetic')
                (root/'Cargo.toml').write_text('[workspace]')
                with self.assertRaises(AssertionError):c.control(repo)

    def test_fallback_preserves_receipt_materializes_tail_and_bounds(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);here=root/'control';here.mkdir();out=root/'receipts';out.mkdir()
            request={'rows':[{'id':s,'selector':'x::'+s,'mode':'Original','variant':'production'} for s in ['done','tail']],
                     'budgets':{'artifact_bytes':10000}}
            (here/'CI-REQUEST.json').write_text(json.dumps(request))
            done=out/'done';done.mkdir();(done/'receipt.json').write_text('{"original_exit_code":42}')
            with patch.object(c,'HERE',here):
                c.fallback(out)
                self.assertEqual(json.loads((done/'receipt.json').read_text())['original_exit_code'],42)
                self.assertEqual(json.loads((out/'tail/receipt.json').read_text())['status'],'NOT_RUN')
                (out/'oversize.log').write_bytes(b'x'*20000)
                c.fallback(out)
                self.assertTrue((out/'TRUNCATED.json').is_file())
                self.assertFalse((out/'oversize.log').exists())


if __name__=='__main__':unittest.main()
