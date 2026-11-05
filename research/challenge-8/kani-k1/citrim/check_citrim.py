#!/usr/bin/env python3
"""Source-only domain/identity checks, using the existing TRIMPART lexer/expander.

No compiler or verifier is invoked. Finite selectors are enumerated; input data,
comparators, assertions, stubs and shared helpers are checked by token equality.
This is neither a compiler inventory nor a formal verification result.
"""
import hashlib
import importlib.util
import itertools
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('trimpart', HERE.parent / 'codefix/trimpart_static.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
BASE = '4fa6151b6a'
TOOLING = '59893bff1f'
PREFIX = s.PREFIX


def tokens(text):
    return s.ser(s.tree(s.lex(text)))


def expand(src, file, macro, args):
    items = s.split_items(src.lookup_macro(file, macro).expand(s.tree(s.lex(args))))
    assert len(items) == 1
    return items[0].text()


def main():
    old, new = s.Source(BASE), s.Source(None)
    before, after = old.roots(False), new.roots(False)
    merge = s.VERIFY_DIR + 'merge.rs'
    network = s.VERIFY_DIR + 'network.rs'
    mappings, domains, covers, expected = {}, {}, {}, {}

    def record(original, parts, original_atoms):
        assert original in before
        mappings[original] = list(parts)
        flat = [atom for atoms in parts.values() for atom in atoms]
        assert sorted(flat) == sorted(original_atoms), (original, 'gap/overlap')
        domains[original] = {'original_atoms': original_atoms, 'parts': parts,
                             'exact_disjoint_union': True}

    # Each arbitrary [u64;9] belongs to exactly one of four truth-value pairs.
    # >= includes equality: no ordering or distinctness assumption is introduced.
    for route in ('general', 'stable'):
        original = f'merge::{route}_direct_u64_n9'
        parts = {}
        for label, first, nxt in [('swap0_swap4', 'true', 'true'),
                                  ('swap0_keep4', 'true', 'false'),
                                  ('keep0_swap4', 'false', 'true'),
                                  ('keep0_keep4', 'false', 'false')]:
            name = f'{route}_direct_u64_n9_{label}'
            key = f'merge::{name}'
            parts[key] = [f'{first},{nxt}']
            covers[key] = 1
            expected[key] = tokens(f'''#[kani::proof] #[kani::solver(kissat)]
                #[kani::unwind(10)] fn {name}() {{
                    {route}_direct_u64_partition::<9, {first}, {nxt}>();
                }}''')
        record(original, parts, [f'{a},{b}' for a, b in itertools.product(
            ('true', 'false'), repeat=2)])
        old_helper = next(it for it in old.items[merge]
                          if it.kind == 'fn' and it.name == f'{route}_direct_u64_properties')
        new_helper = next(it for it in new.items[merge]
                          if it.kind == 'fn' and it.name == f'{route}_direct_u64_partition')
        # Construct the only permitted helper change independently from the old tokens.
        want = old_helper.text().replace(f'{route}_direct_u64_properties',
                                         f'{route}_direct_u64_partition')
        want = want.replace('const N : usize >',
                            'const N : usize , const FIRST_LESS : bool , const NEXT_LESS : bool >')
        want = want.replace('let orig = v ;', 'let orig = v ; ' + tokens('''
            kani::assume(lt_u64(&v[1], &v[0]) == FIRST_LESS);
            kani::assume(lt_u64(&v[5], &v[4]) == NEXT_LESS);'''))
        assert new_helper.text() == want, (route, 'changed helper semantics')

    for width in (16, 17):
        original = f'network::dispatch_safety_stable_unstable_bytes{width}_n15_16_17'
        parts = {}
        for n in (15, 16, 17):
            name = f'dispatch_safety_stable_unstable_bytes{width}_n{n}'
            key = f'network::{name}'
            parts[key] = [f'{n},{stable}' for stable in ('true', 'false')]
            expected[key] = expand(old, network, 'dispatch_pair_safety_cases',
                                   f'{name}, [u8; {width}], [{n}]')
            covers[key] = 3
        record(original, parts, [f'{n},{stable}' for n in (15, 16, 17)
                                 for stable in ('true', 'false')])

    parts = {}
    for route, stable in [('stable', 'true'), ('unstable', 'false')]:
        name = f'dispatch_safety_{route}_bytes16_n32'
        key = f'network::{name}'
        parts[key] = [stable]
        expected[key] = tokens(f'''#[kani::proof]
            #[kani::stub(super::super::panic_on_ord_violation, assume_order_violation)]
            #[kani::unwind(65)] fn {name}() {{
                dispatch_safety_fixed::<[u8; 16], 32, {stable}>();
                kani::cover(true, "{route} route normal return at 32");
                kani::cover(true, "dispatch family reached the end");
            }}''')
        if route == 'unstable':
            expected[key] = expected[key].replace(
                tokens('#[kani::unwind(65)]'),
                tokens('#[kani::solver(kissat)] #[kani::unwind(33)]'))
        covers[key] = 2
    record('network::dispatch_safety_stable_unstable_bytes16_n32', parts, ['true', 'false'])
    # Same original pair macro/stub/unwind/helper; substitute len=32 and stable=true/false.
    # The other route's cover is infeasible in that part and lives in the complementary part.

    for lo, hi, ranges in [(2, 8, [(2, 5), (6, 8)]),
                            (9, 12, [(9, 10), (11, 12)]),
                            (13, 14, [(13, 13), (14, 14)])]:
        parts = {}
        for low, high in ranges:
            suffix = f'{low}_to{high}' if low != high else str(low)
            name = f'insert_tail_contract_u64_start1_tail{suffix}'
            key = f'network::{name}'
            parts[key] = list(range(low, high + 1))
            ends = ', '.join(map(str, parts[key]))
            expected[key] = expand(old, network, 'insert_tail_start1_group_case',
                                   f'{name}, {low}, {high}, [{ends}]')
            expected[key] = expected[key].replace(
                tokens('#[kani::unwind(25)]'),
                tokens('#[kani::solver(kissat)] #[kani::unwind(18)]'))
            expected[key] = expected[key].replace(
                'insert_tail_group_value', 'insert_tail_group_value_modifies_frame')
            covers[key] = high - low + 3
        record(f'network::insert_tail_contract_u64_start1_tail{lo}_to{hi}',
               parts, list(range(lo, hi + 1)))

    original_tail_helper = next(it for it in old.items[network]
                                if it.kind == 'fn' and it.name == 'insert_tail_group_value')
    tuned_tail_helper = next(it for it in new.items[network]
                             if it.kind == 'fn'
                             and it.name == 'insert_tail_group_value_modifies_frame')
    expected_tail_helper = original_tail_helper.text().replace(
        'insert_tail_group_value', 'insert_tail_group_value_modifies_frame').replace(
            tokens('insert_tail_start1_frame::<START>(&v, &pre, tail);') + ' ', '')
    assert tuned_tail_helper.text() == expected_tail_helper, 'only authorized frame call omitted'
    # Integer element coordinates: modifies(begin=base+1,len=tail) is [1,tail].
    # The prior frame is {0} union [tail+1,16], exactly its complement in backing17.
    # The PFC target's contract (including modifies) is checked unchanged below.
    for tail in range(2, 15):
        modifies = set(range(1, tail + 1))
        explicit_frame = {0} | set(range(tail + 1, 17))
        assert explicit_frame == set(range(17)) - modifies

    parts = {}
    for n in (30, 31, 32):
        name = f'network_safety_unstable_u64_n{n}'
        key = f'network::{name}'
        parts[key] = [n]
        expected[key] = expand(old, network, 'unstable_dispatch_network_cases', f'{name}, [{n}]')
        covers[key] = 3  # panic stub, selected length normal return, family end
    record('network::network_safety_unstable_u64_n30_to32', parts, [30, 31, 32])

    removed, added = set(before) - set(after), set(after) - set(before)
    assert removed == set(mappings), removed
    assert added == set(expected), added
    for name in added:
        assert after[name][1].text() == expected[name], (name, 'unexpected root tokens')
    assert len(before) == 219 and len(after) == 235 and len(added) == 25
    retained = set(before) & set(after)
    assert all(before[name][1].text() == after[name][1].text() for name in retained)
    old_on, new_on = old.roots(True), new.roots(True)
    opt_in = set(old_on) - set(before)
    assert len(opt_in) == 34 and set(new_on) - set(after) == opt_in
    assert all(old_on[name][1].text() == new_on[name][1].text() for name in opt_in)

    # Every old non-root expanded item (including the actual comparator/contract bodies)
    # must survive verbatim. New helper/macro allowlist is exact. Changed module files
    # may differ only in the specified old/new macro invocations and new item definitions.
    extras = {merge: {('fn', 'general_direct_u64_partition'),
                      ('fn', 'stable_direct_u64_partition'),
                      ('macro_rules', 'define_direct_u64_partition_harness')},
              network: {('macro_rules', 'dispatch_pair_route_safety_case'),
                        ('macro_rules', 'insert_tail_start1_tuned_case'),
                        ('fn', 'insert_tail_group_value_modifies_frame')}}
    for file, text in old.files.items():
        if file not in extras:
            assert new.files[file] == text, file
            continue
        old_items = {(it.kind, it.name): it.text() for it in old.expanded[file]
                     if it.kind not in ('inner_doc',) and not s.proof_kind(it.all_attrs)}
        new_items = {(it.kind, it.name): it.text() for it in new.expanded[file]
                     if it.kind not in ('inner_doc',) and not s.proof_kind(it.all_attrs)}
        assert set(new_items) - set(old_items) == extras[file]
        assert all(new_items.get(k) == v for k, v in old_items.items()), file
    changed = subprocess.check_output(['git', 'diff', '--name-only', BASE, '--', 'library'],
                                      text=True).splitlines()
    assert set(changed) == {merge, network}, changed
    lanes = ['.circleci', '.github/workflows', str(HERE.parent.relative_to(s.REPO) / 'tools'),
             str(HERE.parent.relative_to(s.REPO) / 'gcb'), 'scripts/run-kani.sh',
             'tool_config/kani-version.toml', 'rust-toolchain.toml', '.gitmodules', '.cargo',
             'library/.cargo', 'library/Cargo.toml', 'library/Cargo.lock']
    subprocess.run(['git', 'diff', '--exit-code', TOOLING, '--', *lanes], check=True)
    request = json.loads((HERE.parent / 'RUN-REQUEST.json').read_text())
    g1 = s.Source('bc4b5c7ec7b41a317548c21bc8dabeebfb062e5a').roots(False)
    g1_report = json.loads((HERE / 'g1-evidence/verification-report.json').read_text())
    carry = {row['name'].removeprefix(PREFIX) for row in g1_report['rows']
             if row['status'] == 'SUCCESS' and row['seconds'] <= 120}
    assert len(carry) == 10
    assert all(after[n][1].text() == g1[n][1].text() for n in carry)
    requested = added - carry
    assert len(request['harnesses']) == len(requested) == 15
    assert {r['name'] for r in request['harnesses']} == {PREFIX + n for n in requested}
    assert all(r['expect'] == 'SUCCESS' for r in request['harnesses'])
    previous_g2 = s.Source('7e382c4a1c7075245b3202939c0d931e199e4025')
    previous_roots = previous_g2.roots(False)
    tail_parts = {n for n in requested if n.startswith(
        'network::insert_tail_contract_u64_start1_')}
    assert len(tail_parts) == 6
    assert set(previous_roots) == set(after)
    assert all(previous_roots[n][1].text() == after[n][1].text()
               for n in set(after) - tail_parts), 'only six root expansions may change'
    assert previous_g2.files[merge] == new.files[merge], 'other nine G2 parts unchanged'
    request_names = {r['name'] for r in request['harnesses']}
    previous_request = json.loads(subprocess.check_output([
        'git', 'show', '7e382c4a1c7075245b3202939c0d931e199e4025:'
        'research/challenge-8/kani-k1/RUN-REQUEST.json'], text=True))
    assert {r['name'] for r in previous_request['harnesses']} == request_names
    (HERE / 'carried-g1.txt').write_text(''.join(PREFIX + n + '\n' for n in sorted(carry)))
    (HERE / 'expected-g2-covers.json').write_text(json.dumps(
        {PREFIX + k: covers[k] for k in sorted(requested)}, indent=2) + '\n')
    assert request['controls'] is False and request['kani_jobs'] == 1
    assert request['harness_timeout_minutes'] == 5 and request['kind'] == 'diagnostic'
    assert request['runner'] == 'gcb-e2-standard-4' and request['inventory'] is False
    for name, names in [('ordinary-expected.txt', after), ('cfg-on-expected.txt', new_on),
                        ('new-ordinary.txt', added), ('opt-in-expected.txt', opt_in)]:
        (HERE / name).write_text(''.join(PREFIX + n + '\n' for n in sorted(names)))
    (HERE / 'expected-covers.json').write_text(json.dumps(
        {PREFIX + k: v for k, v in sorted(covers.items())}, indent=2) + '\n')
    report = {'status': 'PASS_SOURCE_ONLY', 'base': subprocess.check_output(
        ['git', 'rev-parse', BASE], text=True).strip(),
        'ordinary_before': len(before), 'ordinary_after': len(after),
        'removed': sorted(removed), 'added': sorted(added),
        'retained_roots_token_identical': len(retained), 'opt_in_unchanged': len(opt_in),
        'domains': domains, 'expected_new_covers': sum(covers.values()),
        'carried_g1_success_within_120s': sorted(carry),
        'g2_requested': sorted(requested), 'expected_g2_covers': sum(covers[n] for n in requested),
        'merge_partition_predicates': ['lt_u64(&v[1], &v[0])', 'lt_u64(&v[5], &v[4])'],
        'stage': 'citrim-g2',
        'authorized_frame_change': {
            'roots': sorted(tail_parts), 'tails_checked': list(range(2, 15)),
            'modifies_indices': '[1,tail]',
            'prior_explicit_frame_indices': '{0} union [tail+1,16]',
            'frame_equals_complement': True, 'pfc_contract_unchanged': True,
            'helper_projection_only_omits_frame_call': True,
            'other_nine_g2_parts_unchanged': True,
            'coordinator_authorization': '2026-11-05: use checked profile modifies for frame',
            'performance_source_claim': 'Coordinator: TAILDIAG 59ada14d0a, 183 -> 31s (~5.85x); not independently inspected or CITRIM measured'},
        'request_sha256': hashlib.sha256((HERE.parent / 'RUN-REQUEST.json').read_bytes()).hexdigest(),
        'limitations': 'Finite selectors/source tokens only; no compiler inventory or proof; times unmeasured.'}
    (HERE / 'check-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'PASS source-only: 9 -> 25 roots; 219 -> 235 ordinary; 34 opt-in unchanged; '
          f'{sum(covers.values())} expected covers; all domain unions exact.')


if __name__ == '__main__':
    main()
