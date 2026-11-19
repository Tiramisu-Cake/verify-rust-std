#!/usr/bin/env python3
"""Reproduce W14-B1-01 with real Python writers and synthetic native exports."""
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
CONTROL = Path('/root/kani-ch8-s3s4-bridge1-control-w13')
EXPECTED = 'b9e57f09775ed9db249e0b1b6f8e7e53bde5e60f'
assert subprocess.check_output(['git', '-C', str(CONTROL), 'rev-parse', 'HEAD'], text=True).strip() == EXPECTED
sys.path.insert(0, str(CONTROL / 'ch8-s1-control'))
import test_s34_paths as fixtures
import s34_campaign as campaign
import pack_evidence

test = fixtures.RealPathWriterTests('test_workflow_relative_entry_real_writer_and_portable_replay')
observed = []
with test.fixture() as fix:
    code, terminal = test.run_fixture(fix)
    assert code == 0
    out, request = fix[3], fix[4]
    path = out / 'receipt.json'
    authentic = path.read_bytes()
    assert len(terminal['rows']) == len(fix[6]) == len(terminal['s3_campaign']['completed']) == 7
    assert terminal['s3_campaign']['selected_roots'] == 8
    upload = fix[0] / 'upload-reproducer'
    upload.mkdir()
    for name, value in [('consistent_seven', 7), ('writer_wrong_eight', 8), ('missing', 'DELETE'),
                        ('null', None), ('bool', True), ('string', '7'), ('float', 7.0),
                        ('zero', 0), ('wrong_count_six', 6)]:
        doc = json.loads(authentic)
        if value == 'DELETE':
            del doc['s3_campaign']['selected_roots']
        else:
            doc['s3_campaign']['selected_roots'] = value
        campaign.atomic(path, doc)
        local = campaign.collect([out], request)
        pack_evidence.pack(out)
        (upload / pack_evidence.NAME).write_bytes((out / pack_evidence.NAME).read_bytes())
        portable = campaign.collect([upload], request)
        assert local == portable
        observed.append({'case': name, 'value': value, 'actual_local': 'ACCEPT',
                         'actual_upload_only': 'ACCEPT',
                         'expected': 'ACCEPT' if name == 'consistent_seven' else 'REJECT'})
    path.write_bytes(authentic)
print(json.dumps({'candidate': 'bcc103354d1418feeda043c6b955b38bb4393598',
                  'writer_declares': 8, 'actual_completed': 7,
                  'native_execution': 'SYNTHETIC_ONLY', 'observed': observed}, indent=2))
