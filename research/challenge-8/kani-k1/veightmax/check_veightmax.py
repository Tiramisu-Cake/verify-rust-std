#!/usr/bin/env python3
"""Source-only exact relocation/inventory checks. No compiler or proof tools.

Reuses the existing Rust token lexer and ordinary macro expander. This establishes
source equality and an expected list, not compiler inventory or verification credit.
Run from the VEIGHTMAX worktree root; generated files stay in veightmax/.
"""
import hashlib
import importlib.util
import json
import subprocess
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('trimpart', HERE.parent / 'codefix/trimpart_static.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
BASE = '6ef2158d9df1e194bbcd2bf7a46e8feafc3e8cab'
TOOLING = '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd'
RUSTFMT = ('/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/'
           'scratchpad/rustfmt.sh')
EXPECTED = {
    'widedomains': ('30b4a0796a', 'allocationcontracts', {
        'swap_safety_u8_backing32': 'swap_safety_u8_backing32',
        'swap_safety_u64_backing32': 'swap_safety_u64_backing32',
        'unstable_network_safety_u8_n32_stubbed': 'unstable_network_safety_u8_n32_stubbed',
        'merge_safety_u64_len8_scratch48_src32_dst0': 'merge_safety_u64_len8_scratch48_src32_dst0',
        'sort8_safety_u64_scratch48_src32_dst0_merge_stubbed':
            'sort8_safety_u64_scratch48_src32_dst0_merge_stubbed',
    }, {'arbitrary_less', 'exercise_swap', 'cut_order_violation', 'tail_less_u64',
        'tail_comparison_covers', 'cut_merge_order_violation'}),
    'taildiag': ('59ada14d0a', 'tailcontracts', {
        'u64_backing17_tail1_to7_no_explicit_frame': 'insert_tail_safety_u64_backing17_tail1_to7',
        'u64_backing17_tail8_to15_no_explicit_frame': 'insert_tail_safety_u64_backing17_tail8_to15',
    }, {'read_arguments', 'comparison_covers', 'arbitrary_less', 'exercise'}),
}
LANES = ['.circleci', '.github/workflows', 'research/challenge-8/kani-k1/tools',
         'research/challenge-8/kani-k1/gcb', 'scripts/run-kani.sh',
         'tool_config/kani-version.toml', 'rust-toolchain.toml', '.gitmodules', '.cargo',
         'library/.cargo', 'library/Cargo.toml', 'library/Cargo.lock']


def git(*args):
    return subprocess.check_output(['git', *args], text=True)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def functions(text):
    return {it.name: it for it in s.split_items(s.tree(s.lex(text))) if it.kind == 'fn'}


def main():
    old, new = s.Source(BASE), s.Source(None)
    before, after = old.roots(False), new.roots(False)
    baseline = (HERE.parent / 'citrim/final-ordinary-expected.txt').read_text().splitlines()
    assert baseline == git('show', BASE + ':research/challenge-8/kani-k1/citrim/final-ordinary-expected.txt').splitlines()
    assert len(baseline) == 226 and set(baseline) == {s.PREFIX + n for n in before}
    assert all(after[n][1].text() == it.text() for n, (_, it) in before.items())
    # The only change to existing library files is two ordinary module declarations.
    expected_parent = old.files[s.VERIFY_ROOT].replace(
        'mod assembly;', 'mod allocationcontracts;\nmod assembly;').replace(
        'mod smoke;', 'mod smoke;\nmod tailcontracts;')
    assert new.files[s.VERIFY_ROOT] == expected_parent
    assert all(new.files[p] == t for p, t in old.files.items() if p != s.VERIFY_ROOT)
    assert Path(s.SMALLSORT).read_text() == git('show', f'{BASE}:{s.SMALLSORT}')
    assert '#[cfg(kani)]\n#[unstable(feature = "kani", issue = "none")]\nmod verify;' in Path(s.SMALLSORT).read_text()
    subprocess.run(['git', 'diff', '--exit-code', TOOLING, '--', *LANES], check=True)

    mappings = json.loads((HERE / 'mapping.json').read_text())
    assert len(mappings) == 2 and {g['source_module'] for g in mappings} == set(EXPECTED)
    added, covers, checked, prior = set(), {}, [], []
    for g in mappings:
        revision, target, roots, helpers = EXPECTED[g['source_module']]
        assert g['source_revision'] == git('rev-parse', revision).strip()
        assert g['target_module'] == target
        assert g['source_file'] == s.VERIFY_DIR + g['source_module'] + '.rs'
        assert g['target_file'] == s.VERIFY_DIR + target + '.rs'
        original = functions(git('show', g['source_revision'] + ':' + g['source_file']))
        current = functions(Path(g['target_file']).read_text())
        assert set(current) == set(roots.values()) | helpers
        wanted_items = {(a, b, 'root') for a, b in roots.items()} | {
            (h, h, 'helper') for h in helpers}
        assert len(g['items']) == len(wanted_items)
        assert {(i['source_name'], i['target_name'], i['kind']) for i in g['items']} == wanted_items
        for a, b, kind in sorted(wanted_items):
            want = original[a].text().replace('fn ' + a + ' ', 'fn ' + b + ' ', 1)
            assert current[b].text() == want, (a, b, 'tokens changed')
            assert not s.gated(current[b].all_attrs)
            assert bool(s.proof_kind(current[b].all_attrs)) == (kind == 'root')
            checked.append({'source': g['source_module'] + '::' + a, 'target': target + '::' + b,
                            'kind': kind, 'tokens_equal_except_name': True,
                            'attributes_equal': s.ser(original[a].all_attrs) == s.ser(current[b].all_attrs),
                            'normalized_tokens_sha256': digest(want.encode())})
        # Exact imported names/paths are retained from the source; no new helper is substituted.
        items = s.split_items(s.tree(s.lex(Path(g['target_file']).read_text())))
        assert all(i.kind in ('fn', 'use', 'inner_doc') for i in items)
        imports = ('''use super::super::{UnstableSmallSortTypeImpl, bidirectional_merge,
                       sort8_stable, swap_if_less};
                       use crate::mem::{ManuallyDrop, MaybeUninit}; use crate::{kani, ptr};'''
                   if target == 'allocationcontracts' else
                   'use super::super::insert_tail; use crate::kani;')
        assert [i.text() for i in items if i.kind == 'use'] == [
            i.text() for i in s.split_items(s.tree(s.lex(imports)))]
        assert not any(t.kind == 'ident' and t.text in ('widedomains', 'taildiag')
                       for t in s.lex(Path(g['target_file']).read_text()))
        assert len(g['roots']) == len(roots)
        assert {r['source_name']: r['target_name'] for r in g['roots']} == roots
        for r in g['roots']:
            name = s.PREFIX + target + '::' + r['target_name']
            added.add(target + '::' + r['target_name'])
            report = json.loads(git('show', g['source_revision'] + ':' + r['report_path']))
            assert report['source_sha'] == r['proved_source_sha']
            assert report['build_id'] == r['build_id']
            row = next(x for x in report['rows'] if x['name'] ==
                       s.PREFIX + g['source_module'] + '::' + r['source_name'])
            assert row == r['prior_row'] and row['status'] == 'SUCCESS'
            # Check the selected source really matches the commit that ran successfully.
            proved = functions(git('show', r['proved_source_sha'] + ':' + g['source_file']))
            dependencies, work = set(), [r['source_name']]
            while work:
                source_name = work.pop()
                if source_name in dependencies:
                    continue
                dependencies.add(source_name)
                work.extend((s.idents(original[source_name].tokens()) & helpers) - dependencies)
            for source_name in dependencies:
                assert proved[source_name].text() == original[source_name].text()
            assert git('show', r['proved_source_sha'] + ':' + s.SMALLSORT) == Path(s.SMALLSORT).read_text()
            if 'checks_failed' in row:
                failed, total = row['checks_failed'], row['checks_total']
                reached, count = row['covers_satisfied'], row['covers_total']
                seconds = str(row['seconds'])
            else:
                failed, total = map(int, row['checks'].split('/'))
                reached, count = map(int, row['covers'].split('/'))
                seconds = str(row['time_s'])
            assert failed == 0 and total > 0
            assert reached == count == r['expected_covers']
            covers[name] = count
            prior.append({'source': row['name'], 'target': name, 'build_id': r['build_id'],
                          'source_sha': r['proved_source_sha'], 'status': row['status'],
                          'seconds': seconds, 'checks_failed': failed, 'checks_total': total,
                          'covers_satisfied': reached, 'covers_total': count})
    assert len(added) == 7 and set(after) == set(before) | added and len(after) == 233
    opt = set(old.roots(True)) - set(before)
    assert set(new.roots(True)) - set(after) == opt and len(opt) == 34
    assert all(new.roots(True)[n][1].text() == old.roots(True)[n][1].text() for n in opt)
    assert set(new.files) - set(old.files) == {g['target_file'] for g in mappings}
    changed = set(git('diff', '--name-only', BASE, '--', 'library').splitlines())
    assert changed <= {s.VERIFY_ROOT, *(g['target_file'] for g in mappings)}
    for p in [s.VERIFY_ROOT, *(g['target_file'] for g in mappings)]:
        subprocess.run([RUSTFMT, '--check', '--edition', '2024', '--config-path',
                        str(HERE.parent / 'codefix/rustfmt.toml'), '--config', 'skip_children=true', p], check=True)
    subprocess.run(['git', 'diff', '--check'], check=True)
    for file, names in [('ordinary-expected.txt', after), ('new-ordinary.txt', added),
                        ('opt-in-expected.txt', opt), ('cfg-on-expected.txt', new.roots(True))]:
        (HERE / file).write_text(''.join(s.PREFIX + n + '\n' for n in sorted(names)))
    (HERE / 'expected-covers.json').write_text(json.dumps(covers, indent=2, sort_keys=True) + '\n')
    request = json.loads((HERE.parent / 'RUN-REQUEST.json').read_text())
    assert request == json.loads((HERE / 'RUN-REQUEST.json').read_text())
    assert request['agent'] == 'k1-merge' and request['kind'] == 'diagnostic'
    assert request['controls'] is False and request['inventory'] is True
    assert request['kani_jobs'] == 1 and request['harness_timeout_minutes'] == 4
    assert request['runner'] == 'gcb-e2-standard-4' and request['request_id'].startswith('veightmax-')
    assert len(request['harnesses']) == 7 and {r['name'] for r in request['harnesses']} == set(covers)
    assert all(r['expect'] == 'SUCCESS' for r in request['harnesses'])
    seconds = sum(Decimal(r['seconds']) for r in prior)
    assert seconds == Decimal('392.653726') and sum(covers.values()) == 42
    report = {'source_check': 'PASS', 'base_sha': BASE, 'tooling_base': TOOLING,
              'library_commit': git('log', '-1', '--format=%H', '--', 'library').strip(),
              'source_files_sha256': {p: digest(Path(p).read_bytes()) for p in
                                      [s.SMALLSORT, s.VERIFY_ROOT,
                                       *(g['target_file'] for g in mappings)]},
              'ordinary_before': 226, 'ordinary_after': 233, 'cfg_on_after': 267,
              'base_library_files_unchanged_except_module_declarations': True,
              'base_ordinary_roots_token_identical': 226, 'opt_in_unchanged': 34,
              'normalized_item_comparisons': checked, 'prior_source_reported_rows': prior,
              'prior_seconds_sum': str(seconds), 'expected_covers': 42,
              'ordinary_names_sha256': digest((HERE / 'ordinary-expected.txt').read_bytes()),
              'request_sha256': digest((HERE / 'RUN-REQUEST.json').read_bytes()),
              'compiler_inventory': 'PENDING_GO_AND_BUILD',
              'integrated_verification': 'PENDING_GO_AND_BUILD',
              'scope': 'Source token equality and source-reported bounded prior results only. '
                       'No new proof, compiler inventory or universal T/F theorem.'}
    (HERE / 'check-report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('source_check', 'ordinary_after', 'cfg_on_after',
          'expected_covers', 'prior_seconds_sum', 'ordinary_names_sha256', 'request_sha256')}, indent=2))


if __name__ == '__main__':
    main()
