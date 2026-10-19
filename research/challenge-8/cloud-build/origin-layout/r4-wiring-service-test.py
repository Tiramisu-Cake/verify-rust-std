#!/usr/bin/env python3
"""Inert synthetic R4 authorization/wiring checks; no proof or live state."""
import ast
import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
spec=importlib.util.spec_from_file_location('r4_control',HERE.parent/'control.py');control=importlib.util.module_from_spec(spec);spec.loader.exec_module(control)
class Tests(unittest.TestCase):
 def test_exact_phase_account_refuses_malformed_or_changed_authorization(self):
  path=HERE/'GUARD-ADDRESSABILITY-R4-BUDGET-20261020.json'; good=json.loads(path.read_text())
  args=SimpleNamespace(phase_id=good['phase'],ledger=path,owner='merge',command='submit',timeout=900,lane='merge',source_mode='pinned-objects')
  control.authorized_phase(args,good)
  for key in ['owner','authorization_model','allowed_lanes','ceiling_build_seconds','start_utc','main_deadline_utc','deadline_utc','status']:
   for value in [None,{},'wrong']:
    bad=copy.deepcopy(good);bad[key]=value
    with self.subTest(key=key,value=value),self.assertRaises(SystemExit):control.authorized_phase(args,bad)
   bad=copy.deepcopy(good);bad.pop(key)
   with self.subTest(key=key,missing=True),self.assertRaises(SystemExit):control.authorized_phase(args,bad)
  for key,value in [('timeout',89),('timeout',901),('lane','stock'),('source_mode','public-git'),('owner','other')]:
   bad=copy.copy(args);setattr(bad,key,value)
   with self.subTest(key=key,value=value),self.assertRaises(SystemExit):control.authorized_phase(bad,good)
 def test_main_deadline_rechecked_for_submit_and_request(self):
  path=HERE/'GUARD-ADDRESSABILITY-R4-BUDGET-20261020.json';good=json.loads(path.read_text())
  real=control.datetime.datetime
  class AtMain(real):
   @classmethod
   def now(cls,tz=None):return real.fromisoformat('2026-10-19T23:24:56+00:00')
  with patch.object(control.datetime,'datetime',AtMain):
   for command in ['request','submit']:
    args=SimpleNamespace(phase_id=good['phase'],ledger=path,owner='merge',command=command,timeout=900,lane='merge',source_mode='pinned-objects')
    with self.subTest(command=command),self.assertRaises(SystemExit):control.authorized_phase(args,good)
 def test_executor_trace_is_opt_in_real_console_flag(self):
  root=HERE.parents[3]; path=root/'research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py'
  tree=ast.parse(path.read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='execute_case')
  text=ast.get_source_segment(path.read_text(),fn)
  self.assertIn('getattr(args, "r4_addressability_rocq", False) is True',text)
  self.assertIn('vf_arguments.append("-emit_rocq")',text)
  self.assertIn('source_unchanged_at_every_stage',text)
 def test_parent_environment_satisfies_actual_control_receipt_gate(self):
  import hashlib
  root=HERE.parents[3]; path=root/'research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py'
  tree=ast.parse(path.read_bytes());main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
  block=next(n for n in main.body if isinstance(n,ast.If) and any(isinstance(x,ast.Attribute) and x.attr=='update' for x in ast.walk(n)) and 'profile_sha256' in ast.unparse(n))
  profile=HERE/'GLUE-PROFILE.json';card=json.loads(profile.read_text())
  args=SimpleNamespace(profile=card['profile'])
  environment={'profile':card['profile'],'proof_sha':'a'*40,'provider':{'build_id':'synthetic-build'},'accepted':False}
  context={'args':args,'environment':environment,'profile_card':card,'Path':Path,'os':SimpleNamespace(environ={'SMALLSORT_MERGE_PROFILE':str(profile)}),'base':SimpleNamespace(file_sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest())}
  exec(compile(ast.fix_missing_locations(ast.Module(body=[block],type_ignores=[])),str(path),'exec'),context)
  spec=importlib.util.spec_from_file_location('r4_inert_receipt_gate',HERE/'r4-addressability-controls.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  binding=m._receipt_gate(args,environment)
  self.assertEqual(binding['tool_commit'],card['effective_tool_commit'])
  self.assertEqual(binding['profile_sha256'],hashlib.sha256(profile.read_bytes()).hexdigest())
  self.assertEqual(binding['verify_expr_sha256'],card['verify_expr_sha256'])
if __name__=='__main__':unittest.main(verbosity=2)
