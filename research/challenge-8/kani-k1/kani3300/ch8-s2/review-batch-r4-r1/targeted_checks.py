#!/usr/bin/env python3
"""Same14 exact discriminator and bounded byte-delta checks; no compiler."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent / 'batch-r4-r1'
PINS = json.loads((PACKAGE / 'PINS.json').read_text())
Q = Path(PINS['control']['worktree']) / 'ch8-s1-control'
sys.dont_write_bytecode = True
sys.path.insert(0, str(Q))
import cfg_pfc as c
import ordinary_contracts as o
import lexical_bindings as l


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def run(gate, root, request):
    try:
        result = gate(root, request)
        uses = result.get('checked_active_ordinary_uses', [])
        records = [x for x in uses if x['harness'].endswith('::sort13_weak')]
        return {'status': result['status'], 'ordinary_count': len(uses),
                'sort13_weak_records': records, 'function_count': len(result.get('functions', []))}
    except c.GateError as exc:
        return {'status': 'REJECT', 'diagnostic': str(exc)}


def main():
    source = Path(PINS['source']['worktree'])
    control = Q.parent
    old_source = PINS['source']['derivation_source']
    old_control = PINS['control']['derivation_control']
    old_batch = git(source, 'show', old_source + ':' + l.BATCH)
    final_batch = (source / l.BATCH).read_bytes()
    assert final_batch == old_batch.replace(b'swap_if_less, sort8_stable, insert_tail,',
                                           b'swap_if_less, sort8_stable, sort4_stable, insert_tail,', 1)
    assert git(source, 'diff', '--name-only', old_source, PINS['source']['sha']).decode().splitlines() == [l.BATCH]
    paths = git(control, 'diff', '--name-only', old_control, PINS['control']['sha']).decode().splitlines()
    allowed = ['CI-REQUEST.json', 'S2-SOURCE.json', 'cfg_pfc.py', 'fixtures/s2-r4-batch.rs.txt',
               'lexical_bindings.py', 'ordinary_contracts.py', 'runner.py', 's2_correspondence.py',
               's2_policy.py', 'test_cfg_pfc.py']
    assert paths == sorted('ch8-s1-control/' + x for x in allowed)
    old_runner = git(control, 'show', old_control + ':ch8-s1-control/runner.py').decode()
    for old, new in [(old_source, PINS['source']['sha']),
                     ('135f4549d1e8d6f69f1935c817f4c42bb917b756', PINS['source']['tree'])]:
        assert old_runner.count(old) == 1
        old_runner = old_runner.replace(old, new)
    assert old_runner == (Q / 'runner.py').read_text()
    assert git(control, 'show', old_control + ':.github/workflows/ch8-s2.yml') == (control / '.github/workflows/ch8-s2.yml').read_bytes()
    r = json.loads((Q / 'CI-REQUEST.json').read_text())
    old_r = json.loads(git(control, 'show', old_control + ':ch8-s1-control/CI-REQUEST.json'))
    def normalize(obj):
        if isinstance(obj, dict): return {k: normalize(v) for k,v in obj.items() if k != 'source_sha256'}
        if isinstance(obj, list): return [normalize(v) for v in obj]
        return obj
    assert normalize(r['rows']) == normalize(old_r['rows'])
    for key in ('budgets','flags','execution_groups','variants','replacement_unions',
                'formal_expected_inventory','diagnostic_assumed_inventory','qualification_inventory'):
        assert r[key] == old_r[key], key
    sources = json.loads((Q / 'S2-SOURCE.json').read_text())
    for rel, text in sources.items():
        assert text.encode() == (source / rel).read_bytes(), rel
    alias_cases, lexical_cases = [], []
    with tempfile.TemporaryDirectory(prefix='same14-targeted-') as temp:
        root = Path(temp)
        for rel, text in sources.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        batch = root / l.BATCH
        original = sources[l.BATCH]
        old = '#[kani::stub(s2_swap_seam,weak_swap)]'
        req = copy.deepcopy(r)
        removed = ['ordinary_contract_source_sha256', 'cfg_pfc_source_sha256']
        for key in removed: req.pop(key)
        variants = [
            ('exact_review', 'use crate::kani::stub as ordinary1;\nuse self::ordinary1 as ordinary2;\n', 'ordinary2'),
            ('three_level', 'use crate::kani::stub as ordinary1;\nuse self::ordinary1 as ordinary2;\nuse self::ordinary2 as ordinary3;\n', 'ordinary3'),
            ('module_chain', 'use crate::kani as k1;\nuse self::k1 as k2;\n', 'k2::stub'),
        ]
        for label, imports, attr in variants:
            for target, status in [('s2_swap_seam', 'STATIC_PASS'), ('swap_if_less', 'REJECT')]:
                # Keep every original function attribute attached to its function.
                text = imports + original.replace(old, '#[' + attr + '(' + target + ',weak_swap)]')
                batch.write_text(text)
                outcomes = {name: run(gate, root, req) for name,gate in [('ordinary',o.check),('combined',c.check)]}
                assert all(v['status'] == status for v in outcomes.values()), outcomes
                for outcome in outcomes.values():
                    if status == 'STATIC_PASS':
                        assert len(outcome['sort13_weak_records']) == 1
                        assert outcome['sort13_weak_records'][0]['target'] == '::'.join(l.MOD + (target,))
                    else:
                        assert 'swap_if_less has active contract attrs' in outcome['diagnostic']
                alias_cases.append({'case':label + '_' + target, 'imports':imports, 'attribute':attr,
                                    'only_removed_hash_maps':removed, 'outcomes':outcomes})
        for label, imports, expected in [
            ('cycle','use self::a2 as a1;\nuse self::a1 as a2;\n','cyclic alias'),
            ('ambiguous','use crate::kani::stub as a2;\nuse crate::kani::stub_verified as a2;\n','ambiguous'),
            ('unresolved','use self::missing as a1;\nuse self::a1 as a2;\n','unresolved alias'),
        ]:
            batch.write_text(imports + original.replace(old,'#[a2(s2_swap_seam,weak_swap)]'))
            outcomes = {name: run(gate, root, req) for name,gate in [('ordinary',o.check),('combined',c.check)]}
            assert all(v['status'] == 'REJECT' and expected in v['diagnostic'] for v in outcomes.values())
            alias_cases.append({'case':label,'imports':imports,'only_removed_hash_maps':removed,'outcomes':outcomes})
        req = copy.deepcopy(r)
        req.pop('lexical_source_sha256')
        mutations = [
            ('final', original, 'STATIC_PASS'),
            ('frozen_r4', old_batch.decode(), 'REJECT'),
            ('removed_import', original.replace('sort4_stable, ', ''), 'REJECT'),
            ('renamed_import', original.replace('sort4_stable, ', 'sort4_stable as renamed4, '), 'REJECT'),
            ('wrong_target', original.replace('sort4_stable, ', 'insert_tail as sort4_stable, '), 'REJECT'),
            ('disabled_import', '#[cfg(not(kani))]\nuse super::super::sort4_stable;\n' + original.replace('sort4_stable, ', ''), 'REJECT'),
            ('qualified', original.replace('sort4_stable, ', '').replace('sort4_stable(', 'super::super::sort4_stable('), 'STATIC_PASS'),
            ('alias', original.replace('sort4_stable, ', 'sort4_stable as four, ').replace('sort4_stable(', 'four('), 'STATIC_PASS'),
        ]
        for label, text, status in mutations:
            batch.write_text(text)
            outcome = run(l.check, root, req)
            assert outcome['status'] == status, (label, outcome)
            if status == 'REJECT':
                assert ('sort4_stable' in outcome['diagnostic'] or 'relocated binding differs' in outcome['diagnostic'])
            lexical_cases.append({'case':label, 'only_removed_hash_maps':['lexical_source_sha256'], 'outcome':outcome})
        batch.write_text(original)
        doc = l.check(root, r)
        assert doc == json.loads((PACKAGE / 'NAME-RESOLUTION-MAP.json').read_text())
        counts = {f['function']:len(f['static_calls']) for f in doc['functions']}
        assert counts == {'sort13_weak':4, 'general32_weak':4, 'sort8_registration_only':5,
                          's2_swap_seam':1, 's2_merge_seam':1, 'sort13_fault_network':46,
                          'general_fault_copy':3, 'general_fault_scratch':13}
        assert len(doc['contexts']) == 11 and sum(counts.values()) == 77
        scratch = next(f for f in doc['functions'] if f['function'] == 'general_fault_scratch')
        calls = [x for x in scratch['static_calls'] if x['path'] == 'sort4_stable']
        assert [x['line'] for x in calls] == [300,301]
        assert all(x['identity'] == '::'.join(c.SM + ('sort4_stable',)) for x in calls)
    result = {'status':'STATIC_PASS', 'source':PINS['source'], 'control':PINS['control'],
              'source_delta':'EXACT_ONE_IMPORT_LINE; all other source bytes identical to frozen r4',
              'control_changed_paths':paths, 'runner':'TWO_SOURCE_IDENTITY_LITERALS_ONLY',
              'workflow':'BYTE_IDENTICAL', 'row_semantics_caps_cfg_model':'UNCHANGED_BY_BOUNDED_BYTE_DELTA',
              'alias_cases':alias_cases, 'lexical_cases':lexical_cases,
              'inventory_static_call_counts':counts, 'static_call_occurrences':77, 'contexts':11,
              'R14-01':'CLOSED_STATIC', 'R14-02':'CLOSED_STATIC',
              'limits':'No expansion/type/method/MIR/native compile/causal repair; no proof credit'}
    (OUT / 'TARGETED-CHECKS.json').write_text(json.dumps(result,indent=2)+'\n')
    print('TARGETED_CHECKS_COMPLETE: exact aliases reject contracted/retain safe; lexical frozen reject/final pass; bounded invariants')


if __name__ == '__main__':
    main()
