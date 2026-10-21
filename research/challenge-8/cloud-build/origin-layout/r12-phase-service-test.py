#!/usr/bin/env python3
"""Isolated R12 phase and prerequisite tests; never invokes Cloud or proof tools."""
from pathlib import Path
from types import SimpleNamespace
import datetime
import importlib.util
import json
import sys
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
spec=importlib.util.spec_from_file_location('r12_control',HERE.parent/'control.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
PHASE='MERGE-UPLOAD-NONCOMPOSITE-R12-2026-10-21'
LEDGER=HERE/'CURRENT-RECOVERY-R12-UPLOAD-BUDGET-20261021.json'


def account():
 return dict(phase=PHASE,owner='merge',authorization_model='bounded-cloud-budget',status='AUTHORIZED',
  authorization='explicit synthetic test authorization',allowed_lanes=['merge'],ceiling_build_seconds=3600,
  max_builds=None,max_timeout_seconds=1200,carryover_allowed=False,start_utc='2026-10-21T10:53:30Z',
  main_deadline_utc='2026-10-21T12:53:30Z',deadline_utc='2026-10-21T13:23:30Z',
  builds=[],active_build=None,used_build_seconds=0,remaining_build_seconds=3600,synthetic_upload_gate=None)


def args(**changes):
 result=dict(phase_id=PHASE,ledger=LEDGER,owner='merge',command='submit',timeout=1200,
             lane='merge',source_mode='pinned-objects',infra_sha='a'*40,proof_sha='a'*40)
 result.update(changes);return SimpleNamespace(**result)


def authorize(a=None,d=None,*,now='2026-10-21T11:00:00+00:00',mode='synthetic-upload'):
 real=m.datetime.datetime
 class Frozen(real):
  @classmethod
  def now(cls,tz=None):
   value=real.fromisoformat(now)
   return value if tz is None else value.astimezone(tz)
 with patch.object(m.datetime,'datetime',Frozen),patch.object(m,'r12_upload_mode',return_value=mode):
  return m.authorized_phase(a or args(),d or account())


def valid_proof_account():
 d=account();d['builds']=[dict(build_id='probe-id',accounted=True,status='SUCCESS',proof_sha='b'*40,submitted_config_sha256='c'*64)]
 d['synthetic_upload_gate']=dict(status='VERIFIED_SYNTHETIC_PUBLICATION',upload_complete=True,
  archive_inventory_verified=True,proof_attempted=False,verification_accepted=False,
  parallel_composite_upload_enabled=False,archive_size_bytes=536900000,threshold_bytes=157286400,
  brief_request_id='request-id',archive_sha256='d'*64,build_id='probe-id',proof_source_sha='b'*40,
  submitted_config_sha256='c'*64)
 return d


class Tests(unittest.TestCase):
 def test_exact_bounds_and_request_without_submit_fields(self):
  for timeout in (90,1200):authorize(args(timeout=timeout))
  authorize(SimpleNamespace(phase_id=PHASE,ledger=LEDGER,owner='merge',command='request'))
  for change in ({'timeout':89},{'timeout':1201},{'lane':'stock'},{'source_mode':'public-git'},{'infra_sha':'b'*40}):
   with self.subTest(change=change),self.assertRaises(SystemExit):authorize(args(**change))

 def test_time_start_main_absolute_and_envelope(self):
  for now in ('2026-10-21T10:53:29+00:00','2026-10-21T12:53:30+00:00','2026-10-21T13:23:30+00:00'):
   with self.subTest(now=now),self.assertRaises(SystemExit):authorize(now=now)
  authorize(args(command='status'),now='2026-10-21T13:20:00+00:00')
  with self.assertRaises(SystemExit):authorize(args(command='status'),now='2026-10-21T13:23:30+00:00')
  # Use a still-open main for an independent envelope boundary check.
  source=(HERE.parent/'control.py').read_text()
  self.assertIn('now+datetime.timedelta(seconds=a.timeout+60)>cutoff',source)
  self.assertIn("'MERGE-UPLOAD-NONCOMPOSITE-R12-2026-10-21'):authorized_phase",source)

 def test_missing_null_wrong_authorization_and_no_old_account(self):
  for field in ('owner','authorization_model','ceiling_build_seconds','allowed_lanes','start_utc','main_deadline_utc','deadline_utc','max_builds','max_timeout_seconds','carryover_allowed','synthetic_upload_gate'):
   for missing in (False,True):
    d=account()
    if missing:d.pop(field)
    else:d[field]=None if field!='max_builds' else 1
    if field=='synthetic_upload_gate' and not missing:continue
    with self.subTest(field=field,missing=missing),self.assertRaises(SystemExit):authorize(d=d)
  with self.assertRaises(SystemExit):authorize(args(ledger=HERE/'R11-RETRY-BUDGET-20261021.json'))
  d=account();d['status']='CLOSED'
  with self.assertRaises(SystemExit):authorize(d=d)

 def test_proof_denied_without_matching_synthetic_gate(self):
  with self.assertRaises(SystemExit):authorize(mode='proof-r11')
  fields=('upload_complete','archive_inventory_verified','proof_attempted','verification_accepted','parallel_composite_upload_enabled','brief_request_id','archive_sha256','build_id','proof_source_sha','submitted_config_sha256','archive_size_bytes','threshold_bytes')
  for field in fields:
   d=valid_proof_account();d['synthetic_upload_gate'][field]=None
   with self.subTest(field=field),self.assertRaises(SystemExit):authorize(d=d,mode='proof-r11')
  d=valid_proof_account();d['builds'][0]['status']='FAILURE'
  with self.assertRaises(SystemExit):authorize(d=d,mode='proof-r11')

 def test_proof_gate_matches_accounted_probe_and_source_mode(self):
  d=valid_proof_account()
  real=m.datetime.datetime
  class Frozen(real):
   @classmethod
   def now(cls,tz=None):return real.fromisoformat('2026-10-21T11:10:00+00:00')
  def mode(sha):return 'synthetic-upload' if sha=='b'*40 else 'proof-r11'
  with patch.object(m.datetime,'datetime',Frozen),patch.object(m,'r12_upload_mode',side_effect=mode),patch.object(m,'r12_validate_retry_sources') as binding:
   m.authorized_phase(args(),d)
   binding.assert_called_once_with('b'*40,'a'*40)
  for field,value in (('accounted',False),('proof_sha','e'*40),('submitted_config_sha256','e'*64)):
   bad=valid_proof_account();bad['builds'][0][field]=value
   with patch.object(m.datetime,'datetime',Frozen),patch.object(m,'r12_upload_mode',side_effect=mode),self.assertRaises(SystemExit):m.authorized_phase(args(),bad)

 def test_mode_flip_allows_only_identical_runtime_and_publication_objects(self):
  original={'proof.py':('100644','blob','a'*40),'control.py':('100644','blob','b'*40)}
  def run(after,recipe=b'recipe'):
   with patch.object(m,'r12_runtime_inventory',side_effect=[(b'recipe',original),(recipe,after)]):
    m.r12_validate_retry_sources('b'*40,'a'*40)
  run(dict(original))
  for path in original:
   for changed in (('100644','blob','c'*40),('100755','blob',original[path][2])):
    after=dict(original);after[path]=changed
    with self.subTest(path=path,changed=changed),self.assertRaises(SystemExit):run(after)
  with self.assertRaises(SystemExit):run({'control.py':original['control.py']})
  with self.assertRaises(SystemExit):run(dict(original),b'changed-recipe')

 def test_budget_and_pending_shapes_fail_closed(self):
  for field,value in (('used_build_seconds',True),('used_build_seconds',-1),('used_build_seconds',3601),('remaining_build_seconds',True),('remaining_build_seconds',3601),('remaining_build_seconds',3599),('builds',None),('builds',[None]),('active_build',False),('active_build','')):
   d=account();d[field]=value
   with self.subTest(field=field,value=value),self.assertRaises(SystemExit):authorize(d=d)
  for field in ('used_build_seconds','remaining_build_seconds','builds','active_build'):
   d=account();d.pop(field)
   with self.subTest(missing=field),self.assertRaises(SystemExit):authorize(d=d)
  d=account();d['used_build_seconds']=600;d['remaining_build_seconds']=3000
  authorize(d=d)

 def test_selected_commit_card_is_required_and_strict(self):
  card={'schema':'merge-r12-upload-mode-v1','mode':'synthetic-upload','payload_bytes':536870912,'threshold_bytes':157286400,'threshold_source':'https://docs.cloud.google.com/storage/docs/parallel-composite-uploads','proof_attempted':False}
  with patch.object(m.subprocess,'check_output',return_value=json.dumps(card).encode()):
   self.assertEqual(m.r12_upload_mode('a'*40),'synthetic-upload')
  for bad in (None,{},dict(schema='merge-r12-upload-mode-v1',mode='synthetic-upload'),dict(card,payload_bytes=1),dict(card,proof_attempted=True),dict(card,proof_attempted=0),dict(card,payload_bytes=536870912.0)):
   with patch.object(m.subprocess,'check_output',return_value=json.dumps(bad).encode()),self.assertRaises(SystemExit):m.r12_upload_mode('a'*40)
  with self.assertRaises(SystemExit):m.r12_upload_mode('HEAD')

if __name__=='__main__':unittest.main()
