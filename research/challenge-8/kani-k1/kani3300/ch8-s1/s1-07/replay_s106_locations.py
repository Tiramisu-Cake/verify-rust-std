#!/usr/bin/env python3
"""Read-only structured S1-06 replay through the S1-07 decoder; no verifier/logs."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--control',type=Path,default=Path('/root/kani-ch8-s1-07-w13'))
    args=parser.parse_args()
    sys.path.insert(0,str(args.control/'ch8-s1-control'))
    import rich_evidence as rich
    source=Path(__file__).resolve().parent.parent/'s1-06/run-43889560779'
    groups=[];count=0;exceptions=[]
    for dest in sorted((source/'evidence').iterdir()):
        inventory_path=dest/'properties.json';stock_path=dest/'export.json'
        inventory=json.loads(inventory_path.read_text());stock=json.loads(stock_path.read_text())
        records={h['name']:h['properties'] for h in inventory['harnesses']}
        original=copy.deepcopy(records)
        decoder=rich.RegularEvidence(list(records),Path('/'))
        decoder.records=records;decoder.finished=True;decoder.validate(stock)
        assert decoder.records==original,'historical property mutated'
        kept=decoder.location_exceptions()
        exceptions.extend({'group':dest.name,**x} for x in kept)
        n=sum(len(p) for p in records.values());count+=n
        groups.append({'group':dest.name,'properties':n,'location_exceptions':len(kept),
                       'inventory_sha256':hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
                       'stock_sha256':hashlib.sha256(stock_path.read_bytes()).hexdigest(),
                       'decoder_inventory_state':decoder.document()['state']})
    expected=json.loads((source/'missing-sites.json').read_text())['records']
    actual={(x['group'],x['harness'],x['property']['id']) for x in exceptions}
    assert actual=={(x['group'],x['selector'],x['id']) for x in expected}
    assert len(groups)==14 and count==9986 and len(exceptions)==18
    print(json.dumps({'state':'STRUCTURED_REPLAY_PASS','groups':groups,'total_properties':count,
                      'location_exception_records':len(exceptions),'exact_ids':2,
                      'historical_files_changed':False,'qualified_acceptance':'PENDING_OFFLINE_W11',
                      'after_binary_measurements_recovered':False,'proof_credit':'NONE'},indent=2))


if __name__=='__main__':main()
