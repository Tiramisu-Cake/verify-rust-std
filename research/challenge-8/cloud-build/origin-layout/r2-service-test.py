#!/usr/bin/env python3
"""Small synthetic annotation/phase guard tests; no proof/extraction or live state."""
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

campaign = load('r2_synthetic_campaign', HERE/'first-callback.py')
control = load('r2_synthetic_control', HERE.parent/'control.py')

class Tests(unittest.TestCase):
    def test_unique_tail_annotation_is_ghost_only_and_preserves_runtime(self):
        source = b'synthetic-runtime\n        let tmp = ManuallyDrop::new(tail.read());\n'
        changed = campaign._open_tail_read(source)
        self.assertEqual(changed.replace(campaign.TAIL_READ_OPEN, b'', 1), source)
        self.assertEqual(campaign.TAIL_READ_OPEN.count(b'//@ '), 3)
        self.assertIn(b'?read_current', changed)
        self.assertNotIn(b'xs', campaign.TAIL_READ_OPEN)
        for bad in (b'absent', source+source):
            with self.assertRaises(ValueError): campaign._open_tail_read(bad)

    def test_phase_exact_identity_and_timeout_fail_closed(self):
        path = HERE/'FIRST-COMPARATOR-R2-BUDGET-20261019.json'
        ledger = json.loads(path.read_text())
        args = SimpleNamespace(phase_id=ledger['phase'], ledger=path,
            owner='merge', command='submit', timeout=900, lane='merge', source_mode='pinned-objects')
        control.authorized_phase(args, ledger)
        for key, value in [('owner','other'), ('start_utc','2026-10-19T11:58:00Z'),
                           ('main_deadline_utc','2026-10-19T14:57:00Z'),
                           ('deadline_utc','2026-10-19T15:27:00Z'),
                           ('ceiling_build_seconds',20000), ('allowed_lanes',['stock'])]:
            bad = copy.deepcopy(ledger); bad[key] = value
            with self.assertRaises(SystemExit): control.authorized_phase(args, bad)
        for key, value in [('timeout',901), ('lane','stock'), ('source_mode','public-git'), ('owner','other')]:
            bad = copy.copy(args); setattr(bad,key,value)
            with self.assertRaises(SystemExit): control.authorized_phase(bad, ledger)

if __name__ == '__main__': unittest.main(verbosity=2)
