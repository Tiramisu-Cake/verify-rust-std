#!/usr/bin/env python3
"""OPTINMOVE source checks; invokes Python and git only, never a Rust toolchain.

Reuse the TIDYDOCS lexer/expander. Compare exact tokens, including every literal and
attribute; no message normalization. The inherited closure overapproximates unqualified
names across modules. Its sole removed false edge is checked separately below using
module-local reachability and explicit cross-module path/import checks.
"""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('tidydocs', HERE.parent / 'tidydocs/check_tidydocs.py')
t = importlib.util.module_from_spec(spec)
spec.loader.exec_module(t)
s = t.s
BASE = '6443b4d99da9ff7d9bf33dee92bb035dbe66e838'
START = '01c090dc1d'
PUBLIC = '44b972435aeff6ea88cd01e64ccea3727a98294e'
CONTROLS = {
    'assembly::reject_mutant_swap_u8_n2',
    'merge::specfix::specfix_full_value_checker_rejects_payload_change_u8',
    'merge::specfix::specfix_wrong_f_insert_rejected_u8',
    'merge::specfix::specfix_wrong_f_merge_rejected_u8',
    'merge::specfix::specfix_wrong_f_sort4_rejected_u64',
    'merge::specfix::specfix_wrong_f_swap_rejected_u8',
    'permtags::reject_duplicate_network_u8_n9',
    'realcontracts::rejects_insert_tail_equal_begin_u64',
    'realcontracts::rejects_merge_overlapping_dst_u64',
    'realcontracts::rejects_swap_comparator_writing_outside_frame_u8',
    'realcontracts::rejects_swap_outside_backing_u8',
    'wrap::rejects_always_true', 'wrap::rejects_payload_corruption',
}
EXCLUSIVE = {
    'realcontracts.rs': {'exercise_insertion_fixed'},
    'permtags.rs': {'arbitrary_u64_order', 'arbitrary_cell_order', 'general_body', 'fallback_body'},
    'scratchgeom.rs': {'shared_allocation'},
}
REMOVED_MACROS = {'define_general_direct_harness', 'define_merge_scratch48_contract_harness',
                  'dispatch_pair_route_safety_case', 'permutation_case'}
REMOVED_USES = {'use super : : super : : insertion_sort_shift_left ;',
                'use crate : : mem : : MaybeUninit ;', 'use crate : : slice ;'}
FALSE_EDGE = (s.VERIFY_DIR + 'permtags.rs', 'fn', 'arbitrary_u64_order')


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def digest(data):
    return hashlib.sha256(data.encode()).hexdigest()


def write_json(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def items(src):
    out = {}
    for f, it in src.all_items():
        key = (f, it.kind, it.name)
        assert key not in out, ('duplicate item', key)
        out[key] = it
    return out


def cover_sites(it):
    """Lexical token positions, independent of line shifts and macro spelling."""
    toks = [(x.kind, x.text) for x in s.lex(it.text())]
    needle = [('ident', 'kani'), ('punct', ':'), ('punct', ':'),
              ('ident', 'cover'), ('punct', '(')]
    return [i for i in range(len(toks)) if toks[i:i + len(needle)] == needle]


def local_reachable(src, f, roots):
    """Conservative unqualified identifier graph within a single Rust module."""
    idx = {it.name: it for it in src.expanded[f] if it.kind in ('fn', 'macro_rules')}
    seen, work = set(), list(roots)
    while work:
        name = work.pop()
        if name in seen or name not in idx:
            continue
        seen.add(name)
        work.extend(s.idents(idx[name].tokens()) - seen)
    return seen


def main():
    old, new, public = s.Source(BASE), s.Source(None), s.Source(PUBLIC)
    assert set(old.files) == set(new.files), 'files must not move or disappear'
    off_old, on_old = old.roots(False), old.roots(True)
    off_new, on_new = new.roots(False), new.roots(True)
    expected = {n.removeprefix(s.PREFIX) for n in
                (HERE.parent / 'tidydocs/ordinary-expected.txt').read_text().splitlines()}
    expected_on = {n.removeprefix(s.PREFIX) for n in
                   (HERE.parent / 'tidydocs/cfg-on-expected.txt').read_text().splitlines()}
    assert len(expected) == 233 and set(off_old) == set(off_new) == expected
    assert len(on_old) == 268 and set(on_old) == expected_on
    assert len(CONTROLS) == 13 and set(on_new) == expected | CONTROLS
    moved = expected_on - expected - CONTROLS
    assert len(moved) == 22 and set(on_old) - set(on_new) == moved
    assert Counter(n.split('::')[0] for n in moved) == {
        'realcontracts': 8, 'permtags': 10, 'scratchgeom': 4}
    assert all(on_old[n][1].text() == on_new[n][1].text() for n in on_new)

    # Every surviving expanded non-macro item is unchanged, including imports and types.
    # Removed imports are a precise allowlist; removed helpers have no kept local caller.
    before, after = items(old), items(new)
    assert not set(after) - set(before)
    removed = set(before) - set(after)
    for key in set(before) & set(after):
        assert before[key].text() == after[key].text(), ('changed expanded item', key)
    removed_helpers = []
    for f, kind, name in sorted(removed):
        if kind == 'macro_rules':
            assert name in REMOVED_MACROS, (f, kind, name)
        elif kind == 'use':
            assert name in REMOVED_USES, (f, kind, name)
        else:
            mp = old.module_path(f) + '::' + name
            assert mp in moved or name in EXCLUSIVE.get(Path(f).name, set()), (f, kind, name)
            if mp not in moved:
                removed_helpers.append((f, name))
    assert {name for _, kind, name in removed if kind == 'macro_rules'} == REMOVED_MACROS
    assert len(removed_helpers) == 6
    for f, name in removed_helpers:
        local_roots = [it.name for root_f, it in on_new.values() if root_f == f]
        assert name not in local_reachable(old, f, local_roots), ('kept local path', f, name)
        # A private sibling helper can only be named via a path/import from other files.
        # Reject any such reference, including through a glob import or module alias.
        module = old.module_path(f).split('::')[-1]
        for other_f, text in old.files.items():
            if other_f == f:
                continue
            tokens = s.ser(s.tree(s.lex(text)))
            assert not re.search(r'\b' + module + r'\s*:\s*:', tokens), (other_f, module)
            for it in old.items[other_f]:
                if it.kind == 'use':
                    assert module not in s.idents(it.tokens()), ('module alias/import', other_f)
    # Explicitly check why the pre-existing global resolver invents this one false edge.
    # merge.rs has its own function with this name, used by its retained roots.
    merge_file = s.VERIFY_DIR + 'merge.rs'
    assert any(it.name == 'arbitrary_u64_order' for it in new.expanded[merge_file])
    assert FALSE_EDGE in removed

    closures, covers = {}, {}
    for controls, roots in ((False, off_new), (True, {n: on_new[n] for n in CONTROLS})):
        for name in sorted(roots):
            a = s.closure(old, [on_old[name]], controls)
            b = s.closure(new, [on_new[name]], controls)
            missing = set(a) - set(b)
            assert missing <= {FALSE_EDGE}, (name, 'missing closure', missing)
            assert not set(b) - set(a), (name, 'new closure')
            if FALSE_EDGE in missing:
                assert on_new[name][0] != FALSE_EDGE[0]
                del a[FALSE_EDGE]
            assert set(a) == set(b)
            for key in a:
                assert a[key].text() == b[key].text(), (name, key)
                assert cover_sites(a[key]) == cover_sites(b[key]), (name, key, 'cover sites')
            closures[name] = digest('\n'.join(str(k) + ':' + a[k].text() for k in sorted(a)))
            covers[name] = sum(len(cover_sites(it)) for it in a.values())

    # Preserve SmallSort byte-for-byte and freeze every path outside verify in library.
    small_old = subprocess.check_output(['git', 'show', BASE + ':' + s.SMALLSORT])
    assert small_old == Path(s.SMALLSORT).read_bytes()
    assert set(git('diff', '--name-only', START, '--', 'library').splitlines()) <= set(new.files)
    assert not git('diff', '--name-only', t.TOOLING, '--', *t.LANES)
    for f, text in new.files.items():
        assert not t.overlong_lines(text), (f, t.overlong_lines(text))
        comments = '\n'.join(x for x in text.splitlines() if x.lstrip().startswith('//'))
        assert not t.FORBIDDEN.search(comments), f
        assert not any(t.FORBIDDEN.search(label) for label in t.normalized(text)[1]), f
    subprocess.run(['git', 'diff', '--check'], check=True)

    manifest = json.loads((HERE / 'moved-statuses.json').read_text())
    assert {r['name'].removeprefix(s.PREFIX) for r in manifest} == moved
    assert len(manifest) == 22
    moved_doc = (HERE / 'MOVED-OPTIN.md').read_text()
    public_roots = public.roots(True)
    for row in manifest:
        short = row['name'].removeprefix(s.PREFIX)
        f, it = public_roots[short]
        assert row['file'] == f and row['line'] == it.first_line
        assert row['name'] in moved_doc and f'{PUBLIC}/{f}#L{it.first_line}' in moved_doc
        result = subprocess.check_output(['git', 'show', row['result_sha'] + ':' + row['result_path']],
                                         text=True)
        assert row['source_excerpt'] in result, short
        assert row['status'] in ('SUCCESS', 'TIMEOUT', 'NOT_RUN')
        if row['status'] == 'SUCCESS':
            assert str(row['seconds']) in row['source_excerpt']
        assert row['source_name'] in row['source_excerpt'], short
    for label, roots in [('ordinary', off_new), ('cfg-on', on_new),
                         ('removed', {n: on_old[n] for n in moved})]:
        (HERE / (label + '-expected.txt')).write_text(
            ''.join(s.PREFIX + n + '\n' for n in sorted(roots)))

    request = json.loads((HERE / 'RUN-REQUEST.json').read_text())
    assert (HERE.parent / 'RUN-REQUEST.json').read_bytes() == (HERE / 'RUN-REQUEST.json').read_bytes()
    for stage, controls in [('g1', False), ('g2', True)]:
        path = HERE / ('RUN-REQUEST.json' if stage == 'g1' else 'G2-RUN-REQUEST.json')
        r = json.loads(path.read_text())
        assert r['request_id'] == f'optinmove-{stage}-20261106-01'
        assert r['agent'] == 'k1-merge' and r['kind'] == 'inventory'
        assert r['inventory'] is True and r['controls'] is controls and r['harnesses'] == []
        assert r['runner'] == 'gcb-e2-standard-4' and r['harness_timeout_minutes'] == 44
    counts = git('diff', '--numstat', START, '--', s.VERIFY_ROOT, s.VERIFY_DIR)
    (HERE / 'line-delta.tsv').write_text('added\tdeleted\tfile\n' + counts + '\n')
    write_json('check-report.json', {
        'status': 'PASS', 'base_sha': BASE, 'public_source_sha': PUBLIC,
        'library_commit': git('log', '-1', '--format=%H', '--', 'library'),
        'library_tree': git('rev-parse', 'HEAD:library'),
        'ordinary': len(off_new), 'controls': len(CONTROLS), 'cfg_on': len(on_new),
        'removed': len(moved), 'removed_by_module': dict(Counter(n.split('::')[0] for n in moved)),
        'all_246_expanded_items_exact': True, 'closure_and_cover_sites_equal_roots': len(closures),
        'closure_sha256': closures, 'closure_cover_sites': covers,
        'inherited_resolver_false_edge_removed': list(FALSE_EDGE),
        'false_edge_exclusion': 'Private helper unreachable from kept local roots; no sibling path/import.',
        'all_surviving_expanded_items_exact': True, 'removed_helpers': removed_helpers,
        'removed_macros': sorted(REMOVED_MACROS), 'smallsort_bytes_identical': True,
        'overlong_lines': [], 'forbidden_comments_and_messages': [], 'tooling_unchanged': True,
        'source_sha256': {f: digest(text) for f, text in sorted(new.files.items())},
        'names_sha256': {label: digest((HERE / (label + '-expected.txt')).read_text())
                         for label in ('ordinary', 'cfg-on', 'removed')},
        'request_sha256': digest((HERE / 'RUN-REQUEST.json').read_text()),
        'g2_request_sha256': digest((HERE / 'G2-RUN-REQUEST.json').read_text()),
        'compiler_inventory_cfg_off': 'NOT_RUN', 'compiler_inventory_cfg_on': 'NOT_RUN',
        'new_unused_warnings': 'NOT_RUN: requires both compiler builds',
        'scope': 'Source token and dependency checks, not compiler inventory or new proof credit.',
    })
    print(json.dumps({'status': 'PASS', 'ordinary': len(off_new), 'controls': len(CONTROLS),
                      'cfg_on': len(on_new), 'moved': len(moved), 'exact_roots': len(closures)}))


if __name__ == '__main__':
    main()
