#!/usr/bin/env python3
"""Small synthetic phase guard tests; no proof/extraction or live state."""
import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

control = load('r3_synthetic_control', HERE.parent/'control.py')

class Tests(unittest.TestCase):
    def test_phase_exact_identity_and_timeout_fail_closed(self):
        path = HERE/'FIRST-COMPARATOR-R3-BUDGET-20261019.json'
        ledger = json.loads(path.read_text())
        args = SimpleNamespace(phase_id=ledger['phase'], ledger=path,
            owner='merge', command='submit', timeout=900, lane='merge', source_mode='pinned-objects')
        control.authorized_phase(args, ledger)
        for key, value in [('owner','other'), ('owner',None), ('authorization_model',None), ('start_utc','2026-10-19T16:10:27Z'),
                           ('main_deadline_utc','2026-10-19T20:39:27Z'),
                           ('deadline_utc','2026-10-19T21:09:27Z'),
                           ('ceiling_build_seconds',4000), ('status','CLOSED'), ('allowed_lanes',['stock'])]:
            bad = copy.deepcopy(ledger); bad[key] = value
            with self.assertRaises(SystemExit): control.authorized_phase(args, bad)
        for key, value in [('timeout',89), ('timeout',901), ('lane','stock'), ('source_mode','public-git'), ('owner','other')]:
            bad = copy.copy(args); setattr(bad,key,value)
            with self.assertRaises(SystemExit): control.authorized_phase(bad, ledger)

if __name__ == '__main__': unittest.main(verbosity=2)
