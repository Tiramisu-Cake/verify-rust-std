"""Existing control gate against local Git, with synthetic CI environment only."""
from pathlib import Path
import json,os,subprocess,sys
from unittest import mock
OUT=Path(__file__).resolve().parent;C=Path('/root/kani-ch8-s4-next-control-w15');H=C/'ch8-s1-control'
sys.path.insert(0,str(H));import check_package
sha=subprocess.check_output(['git','-C',str(C),'rev-parse','HEAD'],text=True).strip()
with mock.patch.dict(os.environ,{'GITHUB_REPOSITORY':'Tiramisu-Cake/kani','GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/heads/uninit-ci/ch8-s4p-network-r2-offline-synthetic','GITHUB_RUN_ATTEMPT':'1','GITHUB_SHA':sha}):report=check_package.control(C)
record={'status':'STATIC_PASS','report':report,'method':'Existing check_package.control against exact committed local tree, synthetic environment; no push/event/CI/dispatch actually occurred','native_CI':'NOT_RUN'}
(OUT/'CONTROL-GATE.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
