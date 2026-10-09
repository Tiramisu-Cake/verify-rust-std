#!/usr/bin/env python3
"""Small isolated committed-object transport controls; Git/JSON only."""
import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch
import control

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('source_input',HERE/'source-input.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def main():
 p=argparse.ArgumentParser();p.add_argument('--sha',required=True);a=p.parse_args()
 repo=HERE.parents[2]
 payload=m.make_payload(repo,a.sha,a.sha,'verifast-mdnew-cfg')
 cfg=control.config(a.sha,a.sha,'verifast-mdnew-cfg',1740,'dispatch-isolated-preflight',payload)
 parts=[v for k,v in cfg['substitutions'].items() if k.startswith('_SOURCE_')]
 assert len(parts)<=191 and all(len(v)<=3990 for v in parts)
 assert all(len(arg.encode())<=10000 for step in cfg['steps'] for arg in step.get('args',[]))
 try:control.config(a.sha,a.sha,'verifast-mdnew-cfg',1740,'dispatch-isolated-preflight',b'x'*572000)
 except SystemExit:pass
 else:raise AssertionError('Oversize payload did not reject')
 raw=json.loads(gzip.decompress(payload))
 with tempfile.TemporaryDirectory(prefix='mdnew-transport-') as directory:
  root=Path(directory);workspace=root/'workspace';workspace.mkdir()
  archive=workspace/'archive.gz';archive.write_bytes(payload)
  with patch.object(m,'WORKSPACE',workspace),patch.dict(os.environ,{'LANE':'verifast-mdnew-cfg','INFRA_SHA':a.sha,'PROOF_SHA':a.sha}):
   receipt=m.restore_archive(archive,workspace/'evidence')
   for role in ('infra','proof'):
    assert receipt[role]['head']==a.sha
    assert subprocess.check_output(['git','-C',str(workspace/role),'rev-parse','HEAD'],text=True).strip()==a.sha
   candidate='fc03ad9e5ab3404398404f3bba9d7bcacec01c43'
   inputs=workspace/'proof/research/challenge-8/verifast-input'/candidate
   manifest=json.loads((inputs/'manifest').read_text())
   assert hashlib.sha256((inputs/'bundle').read_bytes()).hexdigest()==manifest['bundle_sha256']
   assert receipt['archive_sha256']==hashlib.sha256(payload).hexdigest()
  with patch.object(m,'WORKSPACE',workspace),patch.dict(os.environ,{'LANE':'verifast-mdnew-cfg','INFRA_SHA':a.sha,'PROOF_SHA':'0'*40}):
   try:m.restore_archive(archive,workspace/'mismatch-evidence')
   except SystemExit:pass
   else:raise AssertionError('Wrong source identity did not reject')
 print(json.dumps({'classification':'LOCAL_GIT_SERVICE_PASS','infra_sha':a.sha,'proof_sha':a.sha,'payload_bytes':len(payload),'source_parts':len(parts),'payload_sha256':hashlib.sha256(payload).hexdigest(),'controls':['exact recipe Git restoration','bundle bytes bound to committed manifest','archive receipt identity','191-part bound','10000-byte command bound','oversize rejection','wrong proof identity rejection'],'proof_execution':False},indent=2))

if __name__=='__main__':main()
