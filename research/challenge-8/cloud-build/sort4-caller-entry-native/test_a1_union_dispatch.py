"""Pure authorization/profile transport checks; no API/build/tool execution."""
import datetime
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch

CLOUD=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(CLOUD))
SPEC=importlib.util.spec_from_file_location('a1_fix_dispatch_control',CLOUD/'control.py')
CONTROL=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(CONTROL)

class Clock(datetime.datetime):
    @classmethod
    def now(cls,tz=None):
        return cls.fromisoformat(CONTROL.A1_UNION_START.replace('Z','+00:00')).astimezone(tz)

class ExactNewAuthorization(unittest.TestCase):
    def setUp(self):
        self.clock=patch.object(CONTROL.datetime,'datetime',Clock);self.clock.start();self.addCleanup(self.clock.stop)
        self.ledger=dict(phase=CONTROL.A1_UNION_PHASE,status='AUTHORIZED',authorization='synthetic test only',owner='select-sort4',ceiling_build_seconds=3600,remaining_build_seconds=3600,allowed_lanes=list(CONTROL.A1_LANES),start_utc=CONTROL.A1_UNION_START,main_deadline_utc=CONTROL.A1_UNION_MAIN_DEADLINE,deadline_utc=CONTROL.A1_UNION_DEADLINE,maximum_builds=None,maximum_build_timeout_seconds=900,builds=[],active_build=None)
        self.args=SimpleNamespace(phase_id=CONTROL.A1_UNION_PHASE,owner='select-sort4',command='submit',lane='o26-sort4-c1-current-recovery',source_mode='pinned-objects',timeout=900)

    def test_exact_account(self):
        CONTROL.authorized_phase(self.args,self.ledger)

    def test_wrong_account_refused(self):
        for key,bad in [('owner','other'),('ceiling_build_seconds',7200),('maximum_builds',1),('maximum_build_timeout_seconds',901),('start_utc',CONTROL.A1_START),('deadline_utc',CONTROL.A1_UNION_MAIN_DEADLINE),('main_deadline_utc',CONTROL.A1_MAIN_DEADLINE),('allowed_lanes',['smoke-success']),('status','CLOSED')]:
            with self.subTest(key=key),self.assertRaises(SystemExit):CONTROL.authorized_phase(self.args,dict(self.ledger,**{key:bad}))

    def test_wrong_timeout_before_request(self):
        with patch.object(CONTROL.coordination,'request',side_effect=AssertionError('must not request')):
            for seconds in (89,901):
                with self.subTest(seconds=seconds),self.assertRaises(SystemExit):
                    self.args.timeout=seconds
                    CONTROL.run_command(self.args,Path('/unused'),self.ledger,Path('/unused/ledger'))

    def test_main_and_absolute_deadlines(self):
        for key in ('A1_UNION_MAIN_DEADLINE', 'A1_UNION_DEADLINE'):
            class EndClock(Clock):
                @classmethod
                def now(cls,tz=None):
                    return cls.fromisoformat(getattr(CONTROL,key).replace('Z','+00:00')).astimezone(tz)
            with patch.object(CONTROL.datetime,'datetime',EndClock), patch.object(CONTROL.coordination,'request',side_effect=AssertionError('must not request')), self.assertRaises(SystemExit):
                CONTROL.run_command(self.args,Path('/unused'),self.ledger,Path('/unused/ledger'))

    def test_partial_null_missing_profile_remain_errors(self):
        for payload in ({}, {'authorization_phase_id':CONTROL.A1_UNION_PHASE}, None, [], {'authorization_phase_id':CONTROL.A1_UNION_PHASE,'experiment_protocol_phase_id':None}):
            with self.subTest(payload=payload), patch.object(CONTROL.subprocess,'check_output',return_value=json.dumps(payload).encode()), self.assertRaises((SystemExit,AttributeError)):
                CONTROL.envs('a'*40,'b'*40,self.args.lane,CONTROL.A1_UNION_PHASE)

    def test_preserved_protocol_and_new_authorization_profile(self):
        payload=json.dumps(dict(authorization_phase_id=CONTROL.A1_UNION_PHASE,experiment_protocol_phase_id=CONTROL.A1_PHASE)).encode()
        with patch.object(CONTROL.subprocess,'check_output',return_value=payload) as git:
            env=CONTROL.envs('a'*40,'b'*40,self.args.lane,CONTROL.A1_UNION_PHASE)
        self.assertEqual(git.call_args.args[0][-1],'b'*40+':'+CONTROL.A1_UNION_PROFILE)
        for value in ['SORT4_A1_PHASE_ID='+CONTROL.A1_PHASE,'SORT4_A1_AUTHORIZATION_PHASE_ID='+CONTROL.A1_UNION_PHASE,'SORT4_A1_PROFILE_SHA256='+CONTROL.digest(payload)]:self.assertIn(value,env)
        self.assertFalse(any(value.startswith('SORT4_ACTUAL_CALLER_ENTRY_PHASE=') for value in env))

    def test_wrong_profile_binding_refused(self):
        for auth,protocol in [(CONTROL.A1_PHASE,CONTROL.A1_PHASE),(CONTROL.A1_UNION_PHASE,CONTROL.A1_UNION_PHASE)]:
            with self.subTest(auth=auth,protocol=protocol),patch.object(CONTROL.subprocess,'check_output',return_value=json.dumps(dict(authorization_phase_id=auth,experiment_protocol_phase_id=protocol)).encode()),self.assertRaises(SystemExit):
                CONTROL.envs('a'*40,'b'*40,self.args.lane,CONTROL.A1_UNION_PHASE)

if __name__=='__main__':unittest.main()
