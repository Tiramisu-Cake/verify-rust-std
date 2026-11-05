#!/usr/bin/env python3
"""Final CITRIM source reconciliation and bounded-evidence selection. No proof tools.

Failed/slow replacement families return to their exact original roots. Successful
families keep only source-identical measured parts. Counts here are source inventories;
separate source-bound compiler inventory remains a coordinator closeout item.
"""
import hashlib
import importlib.util
import json
import subprocess
from collections import Counter
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('trimpart', HERE.parent / 'codefix/trimpart_static.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
BASE = '4fa6151b6a9d0ae63261ab03eb86b65cec0a899e'
G1 = 'bc4b5c7ec7b41a317548c21bc8dabeebfb062e5a'
G2 = '9cc449ccce74c6b3b8f96554b86308ff39a2b71f'
TOOLING = '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd'
PREFIX = s.PREFIX


def main():
    base, g1, g2, final = [s.Source(rev) for rev in (BASE, G1, G2, None)]
    old, built1, built2, roots = [src.roots(False) for src in (base, g1, g2, final)]
    one = json.loads((HERE / 'g1-evidence/verification-report.json').read_text())
    two = json.loads((HERE / 'g2-evidence/verification-report.json').read_text())
    assert one['evidence_consistency'] == two['evidence_consistency'] == 'PASS'
    assert one['source_sha'] == G1 and two['source_sha'] == G2
    proposal = json.loads((HERE / 'g2-evidence/check-report.json').read_text())
    expected_covers = json.loads((HERE / 'g2-evidence/expected-covers.json').read_text())
    carry = (HERE / 'g2-evidence/carried-g1.txt').read_text().splitlines()
    rows1 = {r['name']: r for r in one['rows']}
    rows = {n: dict(rows1[n], source_sha=G1) for n in carry}
    rows.update({r['name']: dict(r, source_sha=G2) for r in two['rows']})
    assert set(rows) == {PREFIX + n for n in set(built2) - set(old)}

    def acceptable(row):
        return (row['status'] == 'SUCCESS' and row['checks_failed'] == 0
                and row['seconds'] is not None and row['seconds'] <= 120
                and row['covers_satisfied'] == row['covers_total'] == expected_covers[row['name']])

    kept, restored, decisions, kept_parts = [], [], {}, set()
    for original, domain in proposal['domains'].items():
        parts = list(domain['parts'])
        retain_split = all(acceptable(rows[PREFIX + p]) for p in parts)
        if retain_split:
            kept.append(original)
            kept_parts.update(parts)
            # Equality of finite selectors and their exact original macro expansions was
            # checked in the archived pre-build report; all kept bodies/helpers match below.
            flat = [x for atoms in domain['parts'].values() for x in atoms]
            assert sorted(flat) == sorted(domain['original_atoms'])
            final_domain = domain
        else:
            restored.append(original)
            final_domain = {'original_atoms': domain['original_atoms'],
                            'parts': {original: domain['original_atoms']},
                            'exact_disjoint_union': True}
        decisions[original] = {'decision': 'KEEP_VERIFIED_SPLIT' if retain_split else 'RESTORE_ORIGINAL',
                               'final_domain': final_domain,
                               'experimental_rows': [rows[PREFIX + p] for p in parts]}
    assert len(kept) == 4 and len(restored) == 5 and len(kept_parts) == 11
    assert set(roots) == (set(old) - set(kept)) | kept_parts
    assert len(old) == 219 and len(roots) == 226
    assert all(roots[n][1].text() == old[n][1].text() for n in set(roots) & set(old))
    assert all(roots[n][1].text() == (built1 if rows[PREFIX+n]['source_sha'] == G1
                                    else built2)[n][1].text() for n in kept_parts)
    opt_old = set(base.roots(True)) - set(old)
    opt_final = set(final.roots(True)) - set(roots)
    assert len(opt_old) == 34 and opt_old == opt_final
    assert all(base.roots(True)[n][1].text() == final.roots(True)[n][1].text() for n in opt_old)

    # Every base non-root is retained verbatim. Only the measured N32 stable-route macro
    # remains extra; rejected merge/tail helpers/macros are removed, avoiding unused items.
    def nonroots(src):
        return Counter((path, it.kind, it.name, it.text()) for path, it in src.all_items()
                       if not (it.kind == 'fn' and s.proof_kind(it.all_attrs)))
    previous, current = nonroots(base), nonroots(final)
    assert not previous - current, 'old shared item changed/removed'
    extra = current - previous
    network = s.VERIFY_DIR + 'network.rs'
    macro = next(it for it in g2.items[network]
                 if it.kind == 'macro_rules' and it.name == 'dispatch_pair_route_safety_case')
    assert extra == Counter({(network, macro.kind, macro.name, macro.text()): 1})
    assert final.files[s.VERIFY_DIR + 'merge.rs'] == base.files[s.VERIFY_DIR + 'merge.rs']
    for path in base.files:
        if path != network:
            assert base.files[path] == final.files[path], path
    changes = subprocess.check_output(['git', 'diff', '--name-only', BASE, '--', 'library'],
                                      text=True).splitlines()
    assert changes == [network], changes
    lanes = ['.circleci', '.github/workflows', 'research/challenge-8/kani-k1/tools',
             'research/challenge-8/kani-k1/gcb', 'scripts/run-kani.sh',
             'tool_config/kani-version.toml', 'rust-toolchain.toml', '.gitmodules', '.cargo',
             'library/.cargo', 'library/Cargo.toml', 'library/Cargo.lock']
    subprocess.run(['git', 'diff', '--exit-code', TOOLING, '--', *lanes], check=True)
    final_rows = [rows[PREFIX+n] for n in sorted(kept_parts)]
    seconds = sum(Decimal(r['seconds_decimal']) for r in final_rows)
    covers = sum(r['covers_total'] for r in final_rows)
    assert covers == 31 and all(acceptable(r) for r in final_rows)
    for name, names in [('final-ordinary-expected.txt', roots),
                        ('final-cfg-on-expected.txt', final.roots(True)),
                        ('final-retained-parts.txt', kept_parts),
                        ('final-restored-roots.txt', restored)]:
        (HERE / name).write_text(''.join(PREFIX + n + '\n' for n in sorted(names)))
    names_hash = hashlib.sha256((HERE / 'final-ordinary-expected.txt').read_bytes()).hexdigest()
    (HERE / 'final-expected-covers.json').write_text(json.dumps(
        {r['name']: r['covers_total'] for r in final_rows}, indent=2) + '\n')
    subprocess.run(['git', 'diff', '--exit-code', 'HEAD', '--', 'library'], check=True)
    library_sha = subprocess.check_output(
        ['git', 'log', '-1', '--format=%H', '--', 'library'], text=True).strip()
    assert Decimal(one['cost_usd']) + Decimal(two['cost_usd']) == Decimal('2.2815')
    report = {'source_check': 'PASS', 'final_library_sha': library_sha,
              'final_network_sha256': hashlib.sha256(Path(network).read_bytes()).hexdigest(), 'task_runtime_goal': 'PARTIAL_4_OF_9',
              'base_sha': BASE, 'g1_source': G1, 'g2_source': G2,
              'ordinary_before': 219, 'ordinary_after': 226, 'delta': 7,
              'base_ordinary_roots_token_identical': 215, 'opt_in_unchanged': 34,
              'cfg_on_after': len(final.roots(True)),
              'names_sha256': names_hash, 'kept_split_families': sorted(kept),
              'restored_original_families': sorted(restored),
              'decisions': decisions, 'retained_part_rows': final_rows,
              'retained_part_seconds_sum': str(seconds), 'retained_covers': covers,
              'max_retained_seconds': max(r['seconds'] for r in final_rows),
              'full_suite_seconds_before': None, 'full_suite_seconds_after': None,
              'compiler_inventory': 'PENDING_COORDINATOR_SEPARATE_BUILD',
              'cost_usd': '2.2815', 'reserved_usd': '0.0000',
              'proof_scope': '11 retained parts have SUCCESS, 0 failed checks, 31/31 reachable '
                  'covers and <=120s at their own bound G1/G2 sources. Token-identical roots '
                  'and unchanged shared dependencies support carrying this bounded evidence '
                  'to the reconciled source. No new final-source build or full-suite proof; '
                  'restored roots have no new proof/time credit. Source inventory is not compiler inventory.',
              'runtime_limit': 'Target <=120s achieved for four original families only; five '
                  'unresolved >200s Actions families restored unchanged. Small GCB margin remains; '
                  'no measured GCB/Actions scaling or Actions <=200s guarantee.'}
    (HERE / 'final-check-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('source_check', 'task_runtime_goal', 'ordinary_after',
        'delta', 'retained_part_seconds_sum', 'retained_covers', 'max_retained_seconds')}, indent=2))


if __name__ == '__main__':
    main()
