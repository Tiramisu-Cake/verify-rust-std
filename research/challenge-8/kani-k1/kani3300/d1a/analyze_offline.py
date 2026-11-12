#!/usr/bin/env python3
"""D1-A offline text census; no tool invocation or converter-cost claim.

Input is the coordinator-provided bounded program-only projection, at most 8 MiB.
Coordinates are 1-based physical lines and 0-based byte offsets. Preserve SSA
suffixes/constants; join multiline renderings for whitespace-only fingerprints.
This does not decode IREP, recover DAGs, or prove printed numeric steps execute.
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT = Path('/root/kani3300-d1p-ci')
OUT = Path(__file__).with_name('SSA-SUMMARY.json')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def census(base):
    path = base / 'invocations/cbmc-001/process/stdout.bin'
    raw = path.read_bytes()
    assert len(raw) <= 8 * 1024**2
    rows, unknown, active = [], [], False
    pc, location, current, offset = None, None, None, 0
    for line, chunk in enumerate(raw.splitlines(keepends=True), 1):
        text = chunk.decode('utf-8', 'strict').rstrip('\n')
        if text == 'Program constraints:':
            active = True
        elif active:
            match = re.fullmatch(r'// (\d+) (.*)', text)
            start = re.fullmatch(r'\((sliced|\d+)\) (.*)', text)
            guard = re.fullmatch(r'\s+guard: (.*)', text)
            if match:
                pc, location = int(match[1]), match[2]
                current = None
            elif start:
                current = dict(line=line, byte_offset=offset, byte_length=len(chunk),
                               pc=pc, source_location=location, term=start[2],
                               retained=start[1] != 'sliced', printed_id=start[1],
                               guard=None)
                rows.append(current)
            elif guard and current:
                current['guard'] = guard[1]
                current = None
            elif text == ',':
                # End of show_program, before the final JSON status object.
                active = False
                current = None
            elif current and text.startswith('    .'):
                current['term'] += '\n' + text
                current['byte_length'] += len(chunk)
            elif text.strip():
                unknown.append(dict(line=line, byte_offset=offset, text=text[:160]))
        offset += len(chunk)
    groups = defaultdict(list)
    categories = {'all': Counter(), 'retained': Counter(), 'ignored': Counter()}
    operators = {'all': Counter(), 'retained': Counter(), 'ignored': Counter()}
    indices = {'all': Counter(), 'retained': Counter(), 'ignored': Counter()}
    candidates = defaultdict(list)
    for row in rows:
        term = row['term']
        row['text_sha256'] = sha(term.encode())
        normalized = re.sub(r'\s+', ' ', term).strip()
        row['fingerprint'] = sha(normalized.encode())
        row['category'] = next((x for x in ('ASSERT', 'ASSUME', 'CONSTRAINT',
                                           'SHARED_READ', 'SHARED_WRITE')
                                if term.startswith(x + '(')), 'assignment_or_UNKNOWN')
        row['root_width_bits'] = (1 if row['category'] in ('ASSERT', 'ASSUME', 'CONSTRAINT')
                                  or ' == ' in term else None)
        groups[row['fingerprint']].append(row)
        for bucket in ('all', 'retained' if row['retained'] else 'ignored'):
            categories[bucket][row['category']] += 1
            for op in re.findall(r'byte_(?:extract|update)\w*|__CPROVER_POINTER_OBJECT|'
                                 r'__CPROVER_POINTER_OFFSET|\bWITH\b|\bARRAY_OF\b|\birep\(', term):
                operators[bucket][op] += 1
            for index in re.findall(r'\[([^\]\n]{1,256})\]', term):
                indices[bucket]['constant_text' if re.fullmatch(r'\d+', index)
                                else 'symbolic_or_UNKNOWN_text'] += 1
        for name, pattern in {
            'byte_ops': r'byte_(?:extract|update)',
            'finite_array_update': r'\bWITH\b',
            'state_value': r'MEM_INIT_STATE#\d+\.\.value ==',
            'state_offset': r'MEM_INIT_STATE#\d+\.\.tracked_offset ==',
            'saved_object': r'MEM_INIT_STATE#\d+\.\.argument_buffer_saved_object_id ==',
            'store_frame': r'ASSERT\(.*__check_lhs_assignment',
        }.items():
            if re.search(pattern, term):
                candidates[name].append(row)

    def brief(row):
        result = {k: v for k, v in row.items() if k != 'term'}
        result['excerpt'] = row['term'][:480]
        result['excerpt_truncated'] = len(row['term']) > 480
        return result

    def ranking(retained, width_filter=None):
        entries = []
        for key, group in groups.items():
            chosen = [r for r in group if (retained is None or r['retained'] == retained)
                      and (width_filter is None or
                           (r['root_width_bits'] is not None) == width_filter)]
            if chosen:
                entries.append(dict(fingerprint=key, occurrences=len(chosen),
                                    first=brief(chosen[0])))
        return sorted(entries, key=lambda r: (-r['occurrences'], r['fingerprint']))[:30]

    legacy = json.loads((base / 'ssa-summary.json').read_text())
    selected = {}
    for key, group in candidates.items():
        # Keep full coordinates for all byte operations and retained updates;
        # representative first/last state/frame terms, with total counts.
        kept = group if key == 'byte_ops' else [r for r in group if r['retained']]
        selected[key] = dict(all_occurrences=len(group),
                             retained_occurrences=sum(r['retained'] for r in group),
                             records=[brief(r) for r in (kept if len(kept) <= 16 else kept[:8]+kept[-8:])])
    return dict(input=str(path), input_sha256=sha(raw), input_bytes=len(raw),
                model_sha256=json.loads((base/'invocations/cbmc-001/actual-cbmc.goto.json').read_text())['sha256'],
                physical_lines=len(raw.splitlines()), textual_census_complete=not unknown,
                unknown_lines=unknown, counts={k: dict(v) for k,v in categories.items()},
                printed_all=len(rows), printed_retained=sum(r['retained'] for r in rows),
                printed_ignored=sum(not r['retained'] for r in rows),
                guard_lines=sum(r['guard'] is not None for r in rows),
                guard_operator_occurrences=dict(Counter(op for r in rows if r['guard']
                    for op in re.findall(r'__CPROVER_POINTER_OBJECT|__CPROVER_POINTER_OFFSET|'
                                         r'byte_(?:extract|update)\w*|\bWITH\b', r['guard']))),
                operator_occurrences={k: dict(v) for k,v in operators.items()},
                index_text_occurrences={k: dict(v) for k,v in indices.items()},
                legacy_prefix_counts=legacy['counts'], legacy_parser_complete=legacy['parser_complete'],
                top30_all_by_occurrences=ranking(None), top30_retained_by_occurrences=ranking(True),
                top30_retained_by_known_logical_root_width_then_occurrences=ranking(True, True),
                top30_retained_unknown_root_width_by_occurrences=ranking(True, False),
                top30_by_exact_operand_width='UNKNOWN: no complete typed expression tree',
                boolean_root_width_note='Equality/ASSERT/ASSUME root is Boolean (1 logical bit); '
                                        'this does not bound operands, storage, or conversion cost.',
                selected_candidates=selected)


if __name__ == '__main__':
    data = dict(schema='kani3300-d1a-offline-text-census-v1',
                coverage='Entire coordinator-provided bounded program-only projection; '
                         'no VCC prefix expansion, no DAG/cache/allocation/conversion measurements.',
                normalization='Whitespace only; preserve SSA suffixes and constants',
                verification='NOT_RUN', offender='NOT_ESTABLISHED',
                widths='Boolean root widths grammar-derived; operand widths remain UNKNOWN '
                       'unless separately type/source-derived in MODEL-MAP/ATTRIBUTION.',
                cases={base.parts[3]: census(base) for base in sorted(ROOT.glob('*/*/P1/*'))})
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    for key, case in data['cases'].items():
        print(key, {k: case[k] for k in ('printed_all','printed_retained','printed_ignored',
                                      'guard_lines','textual_census_complete')})
