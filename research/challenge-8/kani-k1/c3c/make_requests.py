"""Prepare the explicit C3c paired diagnostic and full-job requests; never dispatch."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
PREFIX = 'slice::sort::shared::smallsort::verify::'
rows = [line.split('\t') for line in (BASE.parent/'c3c-inputs/mac-times.tsv').read_text().splitlines()]
heavy = [name for name, seconds, status in rows if name.startswith(PREFIX) and float(seconds) >= 400]
timeouts = [PREFIX+name for name in (
    'merge::merge_contract_u64_n16',
    'network::insertion_permutation_u64_n12',
    'network::insert_tail_contract_u64_start1',
)]
calibration = [PREFIX+'assembly::'+name for name in (
    'safety_stable_unit_n31', 'safety_stable_unit_n32',
    'safety_stable_unit_n17', 'safety_stable_unit_n16',
    'safety_stable_unit_n8', 'permutation_merge_u8_n4',
    'sorted_network_prefix_u8_n10', 'advancement_merge_up_u8_n2',
)]
assert all(any(row[0] == name for row in rows) for name in calibration)
family_calibration = [PREFIX+name for name in (
    "correct::sorted_permutation_general_stable_u8_n14",
    "correct::sorted_permutation_fallback_u64_n8",
)]
old = heavy + timeouts + family_calibration
successors = {}
for name in old:
    if name.endswith('::sorted_permutation_general_stable_u8_n14'):
        new = [name.replace('general_stable', route) for route in ('general','stable')]
    elif name.endswith('::insert_tail_contract_u64_start1'):
        new = [name+'_tail'+str(i) for i in range(2, 17)]
    elif name.endswith('::insert_tail_contract_u64_start6'):
        new = [name+'_tail'+str(i) for i in range(7, 17)]
    elif '::route_safety_all_routes_n' in name:
        new = [name.replace('all_routes', route) for route in ('general_u64','noncopy_u64','stable_u64')]
    else:
        new = [name]
    successors[name] = new
new = [item for names in successors.values() for item in names]
assert len(old) == 14 and len(new) == 42
for label, names in [('baseline',old+calibration),('candidate',new+calibration)]:
    req = dict(schema='kani-k1-run-request-v1',request_id='c3c-matched-'+label,
               agent='k1-network',kind='diagnostic',runner='gcb-e2-standard-4',
               purpose='C3c matched jobs3: 3 Mac TIMEOUT600 + all 9 Mac >=400s domains, correct family and unchanged assembly calibration; cutoff180s is censored evidence',
               harness_timeout_minutes=3,kani_jobs=3,
               harnesses=[dict(name=name,expect='SUCCESS') for name in names])
    if label=='candidate': req['inventory']=True
    (BASE/(label+'-request.json')).write_text(json.dumps(req,indent=2)+'\n')
(BASE/'paired-domain-map.json').write_text(json.dumps(dict(old_domains=successors,calibration=calibration,
     ubuntu_inflight='Not identifiable from supplied terminal-only TSV; no guessed names added'),indent=2)+'\n')
full = dict(schema='kani-k1-run-request-v1',request_id='c3c-full-autoharness',agent='k1-network',
            kind='autoharness',runner='gcb-e2-standard-4',
            purpose='C3c one literal organizer autoharness job on candidate, jobs3 timeout10m unwind1000 from bound workflow; GCB 16GB no swap',
            harness_timeout_minutes=240,inventory=True,harnesses=[])
(BASE/'autoharness-request.json').write_text(json.dumps(full,indent=2)+'\n')
print('baseline',len(old+calibration),'candidate',len(new+calibration),'full wall budget240+overhead30min')
