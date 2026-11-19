#!/usr/bin/env python3
"""R14-02: mutate only terminal schema on an authentic synthetic writer prefix."""
import json
from pathlib import Path
import sys
from unittest import mock

HERE = Path(__file__).resolve().parent
CONTROL = Path('/root/kani-ch8-s4p-1-control-w13/ch8-s1-control')
sys.path.insert(0, str(CONTROL))
import test_s4p_paths as fixtures
import s4p_campaign as campaign
import collect as public
import pack_evidence

def main():
    records = []
    for state in ('FULL', 'STOPPED0', 'PARTIAL0'):
        case = fixtures.RealPathWriterTests()
        with case.fixture() as fix:
            if state == 'FULL':
                code, terminal = case.run_fixture(fix)
                assert code == 0 and len(terminal['s3_campaign']['completed']) == 8
            else:
                with mock.patch.object(campaign, 'check_usage', side_effect=campaign.GlobalFailure('review prelaunch stop')):
                    code, terminal = case.run_fixture(fix)
                assert code == 1 and terminal['s3_campaign']['completed'] == []
                if state == 'PARTIAL0': terminal = campaign.finalize(fix[3], fix[4])
            path = fix[3] / 'receipt.json'; original = path.read_bytes()
            upload = fix[0] / 'schema-upload'; upload.mkdir()
            for variant in ('missing', 'null', 'old-schema', 'wrong-type'):
                doc = json.loads(original)
                if variant == 'missing': doc.pop('schema')
                else: doc['schema'] = {'null': None, 'old-schema': 'ch8-s3s4-bridge1-campaign-v1', 'wrong-type': 123}[variant]
                campaign.atomic(path, doc)
                pack_evidence.pack(fix[3])
                (upload / pack_evidence.NAME).write_bytes((fix[3] / pack_evidence.NAME).read_bytes())
                for route in (fix[3], upload):
                    observed = public.collect([route], fix[4])
                    records.append({'writer_state': terminal['state'], 'variant': variant,
                        'route': 'LOCAL' if route == fix[3] else 'UPLOAD_ONLY', 'accepted': True,
                        'recorded_observations': sum(x.get('outcome') == 'RECORDED' for x in observed['rows']),
                        'proof_credit': observed['proof_credit'], 'reader_state': observed['state']})
            path.write_bytes(original)
    result = {'finding': 'R14-02', 'records': records, 'all_malformed_schemas_accepted': True,
              'scope': 'Synthetic native data; real writers, readers, hashes and portable packing. No native/CI/full Validate.'}
    (HERE / 'TERMINAL-SCHEMA-MATRIX.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'finding': 'R14-02', 'malformed_acceptances': len(records),
                      'full_inventory_acceptances': sum(x['recorded_observations'] == 8 for x in records)}))

if __name__ == '__main__': main()
