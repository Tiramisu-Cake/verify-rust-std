#!/usr/bin/env python3
"""Prepare reviewable cfg-only fallback patches without applying them."""
import difflib
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'scope'))
from source_inventory import ROOT, MODULES, records, source
from source_items import CFG, items


def name(i):
    return i['name'].split('(', 1)[1].split(',', 1)[0] if i['kind'] == 'call' else i['name']


def main():
    plans = {
        'aggregate-stable-n6-to8': dict(module='merge',
            gate=[f'stable_direct_u64_n{n}' for n in (6, 7, 8)],
            ungate=['stable_direct_aggregate_u64_properties'] +
                   [f'stable_direct_aggregate_u64_n{n}' for n in (6, 7, 8)], p1_delta=0,
            p2_delta=0, reason='Select the preserved aggregate fixture for stable N6..8'),
        'u8-n9-not-admitted': dict(module='merge',
            gate=['general_direct_u8_n9', 'stable_direct_nonconst_u8_n9'],
            ungate=['general_stable_sorted_permutation_u8_n9'], p1_delta=-1, p2_delta=1,
            reason='P1 restores C u8 N9; P2 must retain C and both new fixed-route proofs'),
        'm9-not-admitted': dict(module='merge',
            gate=['general_direct_u64_n9', 'stable_direct_u64_n9'], ungate=[],
            p1_delta=-2, p2_delta=0,
            reason='Move the complete M9 pair to P2; C u64 N9 stays retired'),
        'start1-not-admitted': dict(module='network',
            gate=[f'insert_tail_contract_u64_start1_tail{a}_to{b}'
                  for a, b in ((2, 8), (9, 12), (13, 16))], ungate=[],
            p1_delta=-3, p2_delta=0,
            reason='Move all three PFC groups to P2; START1 baseline stays diagnostic'),
    }
    for n in range(2, 6):
        plans[f'nonconst-b-u64-n{n}'] = dict(module='merge',
            gate=[f'general_stable_direct_u64_n{n}'],
            ungate=[f'general_stable_direct_nonconst_u64_n{n}'], p1_delta=0, p2_delta=0,
            reason='Select the preserved generic helper without changing either body')
    out = HERE / 'fallbacks'
    out.mkdir(exist_ok=True)
    for label, plan in plans.items():
        module = plan['module']
        before = source(module)
        edits, seen = [], set()
        for i in items(before):
            symbol = name(i)
            if symbol in plan['gate']:
                assert not i['gated'], symbol
                edits.append((i['start'], i['start'], CFG + '\n'))
                seen.add(symbol)
            elif symbol in plan['ungate']:
                assert i['gated'], symbol
                pos = before.index(CFG, i['start'], i['content'])
                edits.append((pos, pos + len(CFG) + 1, ''))
                seen.add(symbol)
        assert seen == set(plan['gate'] + plan['ungate']), (label, seen)
        after = before
        for start, end, replacement in sorted(edits, reverse=True):
            after = after[:start] + replacement + after[end:]
        # Removing all cfg attributes restores identical body/literal tokens.
        assert before.replace(CFG + '\n', '') == after.replace(CFG + '\n', '')
        count = sum(not r['opt_in'] for m in MODULES for r in records(
            m, text=after if m == module else source(m)))
        assert count == 197 + plan['p1_delta'], (label, count)
        path = str(ROOT / (module + '.rs'))
        patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                        fromfile='a/' + path, tofile='b/' + path, n=2))
        (out / (label + '.patch')).write_text(patch)
        plan.update(patch=str((out / (label + '.patch')).relative_to(HERE)),
                    patch_sha256=hashlib.sha256(patch.encode()).hexdigest(),
                    static_p1_after=count, body_changes=False, applied=False)
    report = dict(status='CFG_ONLY_FALLBACK_PATCHES_NOT_APPLIED', plans=plans,
                  formulas=dict(p1='191+u+2*m+3*s (r=0)', p2='344-u'),
                  p2_rule='Regenerate selected P2 manifest/patch after cfg selection; '
                          'for u=0 C u8 N9 and both new u8 proofs are in P2',
                  exclusions='No baseline START1, C u64 N9, aggregate N9 or const u8 N9 restored',
                  controls_note='Shared const corruption control remains unchanged during cfg selection')
    (HERE / 'cfg-fallbacks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(dict(status=report['status'], plans=len(plans)), indent=2))


if __name__ == '__main__':
    main()
