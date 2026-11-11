"""Capacity estimate from previously saved bounded A3 trace-field responses, never raw evidence.
Omitted records are not reconstructed. Extrapolation is an explicit planning assumption.
"""
import collections
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILTERS = ['IndexRange::len', 'cmp3_index_range_len', 'cmp3_manually_drop_unsized_len']


def estimate():
    records, inputs = {}, {}
    for path in sorted((HERE.parent / 't1b-a3/evidence/35308c57').glob('records-*.stdout.txt')):
        raw = path.read_bytes()
        inputs[path.name] = hashlib.sha256(raw).hexdigest()
        for row in json.loads(raw).get('records', []):
            key = row['invocation'], row['seq']
            if key in records:
                assert records[key] == row
            records[key] = row
    assert len(records) == 374
    kept, zeros = [], 0
    for row in sorted(records.values(), key=lambda r: r['seq']):
        data = row['data']; name = data.get('instance', '')
        if name and not any(f in name for f in FILTERS) and row['kind'] not in ('initial_target', 'body_cache', 'body_cache_writer'):
            continue
        if 'pincheck_calibration_' in name or 'kani_cmp3::manually_drop_unsized_len' in name:
            continue
        if data.get('decision') == 'zero_ops_selected':
            zeros += 1
            continue
        if row['kind'] == 'mir_snapshot':
            if data['stage'] != 'local_before_passes':
                continue
            row = {**row, 'data': {k: v for k, v in data.items() if k in
                   ('instance', 'stage', 'body_hash', 'body_hash_algorithm', 'dump_bytes', 'dump_ok')}}
        kept.append(row)
    compact_bytes = sum(len(json.dumps(r, separators=(',', ':'), ensure_ascii=False).encode()) + 1 for r in kept)
    projected_records = math.ceil(len(kept) * 929 / 374)
    projected_bytes = math.ceil(compact_bytes * 929 / 374)
    # 40 extra records: <=18 per-body zero summaries, <=7 GOTO consumers, 2 final-presence,
    # 5 actual-order events, 8 slack. Five-root planning model; changed reachability is unknown.
    extras = 40
    # Existing writers need new hash/context fields: allow 20 writers * 512 bytes.
    total_bytes = projected_bytes + extras * 2048 + 20 * 512 + 4096
    result = {'assurance': 'ESTIMATE ONLY; assumes retained A3 event density; omitted555 and changed root context UNKNOWN',
              'A3_seen': 929, 'A3_emitted': 374, 'A3_omitted': 555, 'A3_sidecar_bytes': 254788,
              'retained_kinds': dict(collections.Counter(r['kind'] for r in records.values())),
              'compact_retained_records': len(kept), 'compact_retained_bytes': compact_bytes,
              'selected_zero_records_removed': zeros,
              'projected_records_before_extras': projected_records,
              'projected_bytes_before_extras': projected_bytes,
              'extra_record_allowance': extras, 'projected_total_records': projected_records + extras,
              'writer_extra_bytes': 20 * 512, 'header_footer_allowance_bytes': 4096,
              'projected_total_bytes': total_bytes, 'record_limit_payload': 510, 'byte_limit': 256000,
              'assumed_new_record_bytes_max': 2048, 'input_sha256': inputs}
    assert result['projected_total_records'] <= 510 and total_bytes <= 256000
    return result


if __name__ == '__main__':
    print(json.dumps(estimate(), indent=2))
