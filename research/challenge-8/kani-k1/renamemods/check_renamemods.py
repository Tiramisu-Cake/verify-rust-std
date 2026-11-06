#!/usr/bin/env python3
"""Source checks only; reuse LEANHELPERS' lexer/expander and authorized rustfmt.

Reverse only explicit identifier tokens and direct assertion/cover message literals.
The inherited conservative identifier closure is not compiler name resolution.
"""
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'leanhelpers', HERE.parent / 'leanhelpers/check_leanhelpers.py')
l = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l)
s, t, o = l.s, l.t, l.o
BASE = '5c929ba094cef478efc350b3cd9d7b8fc73fe203'
TOOLING = '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd'
MODULES = dict(specfix='profiles', permtags='tag_permutation',
               scratchgeom='scratch_geometry', assembly='fixed_inputs',
               wrap='forwarding_contracts', realcontracts='helper_contracts',
               allocationcontracts='helper_contracts_wide',
               tailcontracts='insert_tail_contracts')
IDENTIFIERS = {name: name.replace('specfix_', 'profile_', 1) for name in (
    'specfix_canonical_comparator', 'specfix_full_value_checker_rejects_payload_change_u8',
    'specfix_wrong_f_swap_rejected_u8', 'specfix_wrong_f_sort4_rejected_u64',
    'specfix_wrong_f_insert_rejected_u8', 'specfix_wrong_f_merge_rejected_u8')}
RENAMES = MODULES | IDENTIFIERS
REVERSE = {v: k for k, v in RENAMES.items()}


def write(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def rename(text, mapping=RENAMES):
    return re.sub(r'\b(?:' + '|'.join(map(re.escape, mapping)) + r')\b',
                  lambda m: mapping[m[0]], text)


def path_rename(path):
    return '/'.join(rename(part) for part in path.split('/'))


def canonical(text, inverse_messages=None, inverse=False):
    """Only the three authorized call shapes expose a message substitution site."""
    ts = s.tree(s.lex(text)) if isinstance(text, str) else [s.clone(x) for x in text]
    def walk(tokens):
        for i, tok in enumerate(tokens):
            if tok.kind == 'ident' and inverse:
                tok.text = REVERSE.get(tok.text, tok.text)
            if tok.kind != 'group':
                continue
            macro = i >= 2 and s.is_i(tokens[i - 2], 'assert') and s.is_p(tokens[i - 1], '!')
            kani = (i >= 4 and s.is_i(tokens[i - 4], 'kani')
                    and s.is_p(tokens[i - 3], ':') and s.is_p(tokens[i - 2], ':')
                    and s.is_i(tokens[i - 1]) and tokens[i - 1].text in ('assert', 'cover'))
            if tok.text == '(' and (macro or kani):
                comma = next((j for j, x in enumerate(tok.children) if s.is_p(x, ',')), None)
                if comma is not None and inverse_messages:
                    for x in tok.children[comma + 1:]:
                        if x.kind == 'lit':
                            x.text = inverse_messages.get(x.text, x.text)
            walk(tok.children)
    walk(ts)
    return s.ser(ts)


def main():
    # The inverse must not conceal a changed predicate, attribute, or unrelated literal.
    inverse_probe = {'"new"': '"old"'}
    assert canonical('kani::assert(x, "new");', inverse_probe) == canonical(
        'kani::assert(x, "old");')
    for text in ('kani::assert(x == "new", "old");', '#[kani::unwind(25)] fn f() {}',
                 'other("new");', 'kani::cover(!x, "old");'):
        assert canonical(text, inverse_probe) != canonical(text.replace(
            '"new"', '"old"').replace('25', '26').replace('!x', 'x'))
    old, new = s.Source(BASE), s.Source(None)
    paths = {f: path_rename(f) for f in old.files}
    back_paths = {v: k for k, v in paths.items()}
    assert len(paths) == len(back_paths) and set(paths.values()) == set(new.files)
    assert sum(k != v for k, v in paths.items()) == 8
    assert json.loads((HERE / 'rename-map.json').read_text()) == {
        'modules': MODULES, 'identifiers': IDENTIFIERS, 'files': paths}
    expected_messages, inverses = [], {}
    for f, text in old.files.items():
        labels = t.normalized(text)[1]
        inverse = inverses[paths[f]] = {}
        for label in dict.fromkeys(labels):
            after = re.sub(r'^"(?:' + '|'.join(MODULES) + r')(?::)? ', '"', label)
            if label.startswith('"realcontracts '):
                after = label.replace('"realcontracts ', '"helper contract ', 1)
            if after != label:
                assert after not in inverse, ('message collision', f, after)
                inverse[after] = label
                expected_messages.append(dict(old_file=f, new_file=paths[f], before=label,
                                              after=after, occurrences=labels.count(label)))
        assert len(labels) == len(t.normalized(new.files[paths[f]])[1])
    assert json.loads((HERE / 'message-map.json').read_text()) == expected_messages
    assert sum(x['occurrences'] for x in expected_messages) == 64
    # Compare entire token streams, except rustfmt's alphabetic root mod declarations.
    # Comparing every expanded item below also freezes those declarations and their cfg.
    for f, text in old.files.items():
        nf = paths[f]
        if f != s.VERIFY_ROOT:
            assert canonical(text) == canonical(new.files[nf], inverses[nf], True), f
        else:
            a = [it.text() for it in old.items[f] if it.kind != 'mod']
            b = [canonical(it.tokens(), inverses[nf], True)
                 for it in new.items[nf] if it.kind != 'mod']
            assert a == b
    def key_back(key):
        f, kind, name = key
        return back_paths[f], kind, rename(name, REVERSE)
    before, after = o.items(old), o.items(new)
    mapped = {key_back(k): (k, v) for k, v in after.items()}
    assert len(mapped) == len(after) and set(before) == set(mapped)
    item_pairs, item_covers = {}, {}
    for key, it in before.items():
        nk, ni = mapped[key]
        assert it.text() == canonical(ni.tokens(), inverses[nk[0]], True), key
        assert o.cover_sites(it) == o.cover_sites(ni), (key, 'cover positions')
        item_covers[key] = o.cover_sites(it)
        labels_a = t.normalized(it.text())[1]
        labels_b = t.normalized(ni.text())[1]
        assert len(labels_a) == len(labels_b)
        item_pairs[key] = list(zip(labels_a, labels_b))
    roots_old, roots_new = old.roots(True), new.roots(True)
    off_old, off_new = old.roots(False), new.roots(False)
    assert (len(off_old), len(off_new), len(roots_old), len(roots_new)) == (233, 233, 246, 246)
    name_map = {name: rename(name) for name in roots_old}
    assert len(set(name_map.values())) == 246 and set(name_map.values()) == set(roots_new)
    assert {name_map[n] for n in off_old} == set(off_new)
    rows, closures, covers = [], {}, {}
    for name, new_name in sorted(name_map.items()):
        controls = name not in off_old
        rows.append(dict(kind='control' if controls else 'ordinary',
                         before=s.PREFIX + name, after=s.PREFIX + new_name))
        a = s.closure(old, [roots_old[name]], controls)
        b = s.closure(new, [roots_new[new_name]], controls)
        mb = {key_back(k): (k, v) for k, v in b.items()}
        assert len(mb) == len(b) and set(a) == set(mb), name
        pairs = []
        sites = {}
        for key, it in a.items():
            # Full item equality and cover/message coordinates were checked once above;
            # these closures reference exactly those same item objects and keys.
            assert it is before[key] and mb[key][1] is mapped[key][1]
            if item_covers[key]:
                sites[str(key)] = item_covers[key]
            pairs.extend(item_pairs[key])
        # Distinct old messages cannot collapse anywhere in the same root closure.
        reverse_labels = {}
        for before_label, after_label in pairs:
            reverse_labels.setdefault(after_label, set()).add(before_label)
        collisions = {k: sorted(v) for k, v in reverse_labels.items() if len(v) != 1}
        assert not collisions, ('message collision', name, collisions)
        closures[s.PREFIX + new_name] = o.digest(
            '\n'.join(str(k) + ':' + a[k].text() for k in sorted(a)))
        covers[s.PREFIX + new_name] = sites
    write('name-map.json', rows)
    (HERE / 'name-map.tsv').write_text('kind\tbefore\tafter\n' + ''.join(
        f"{r['kind']}\t{r['before']}\t{r['after']}\n" for r in rows))
    for label, roots in [('ordinary', off_new), ('cfg-on', roots_new)]:
        (HERE / (label + '-expected.txt')).write_text(
            ''.join(s.PREFIX + n + '\n' for n in sorted(roots)))
    assert subprocess.check_output(['git', 'show', BASE + ':' + s.SMALLSORT]) == Path(s.SMALLSORT).read_bytes()
    library_changed = set(o.git('diff', '--name-only', BASE, '--', 'library').splitlines())
    assert library_changed <= set(paths) | set(paths.values())
    assert not o.git('diff', '--name-only', TOOLING, '--', *t.LANES)
    legacy = re.compile(r'\b(?:' + '|'.join(MODULES) + r')\b|\bspecfix_\w*')
    for f, text in new.files.items():
        assert not t.overlong_lines(text), (f, t.overlong_lines(text))
        assert not legacy.search(text), (f, 'legacy name')
        comments = '\n'.join(x for x in text.splitlines() if x.lstrip().startswith('//'))
        assert not t.FORBIDDEN.search(comments), f
        assert not any(t.FORBIDDEN.search(m) for m in t.normalized(text)[1]), f
    small_comments = '\n'.join(x for x in Path(s.SMALLSORT).read_text().splitlines()
                               if x.lstrip().startswith('//'))
    assert not legacy.search(small_comments)
    # Bare substring grep also finds ordinary Rust wrapping APIs and English wrapper terms.
    # Preserve these explicitly: none denotes the renamed module.
    substring = re.compile('|'.join(MODULES))
    mentions = []
    scan_files = dict(new.files)
    scan_files[s.SMALLSORT] = Path(s.SMALLSORT).read_text()
    for f, text in scan_files.items():
        for line_no, line in enumerate(text.splitlines(), 1):
            if f == s.SMALLSORT and not line.lstrip().startswith('//'):
                continue
            if substring.search(line):
                assert all(m[0] == 'wrap' for m in substring.finditer(line)), (f, line_no)
                assert re.search(r'wrapping_|wrapped_|wrappers?\b', line), (f, line_no)
                mentions.append(dict(file=f, line=line_no, text=line.strip(),
                    reason='Rust wrapping API, descriptive wrapper/newtype term, or existing '
                           'wrapped-value helper; not a module codename.'))
    write('remaining-name-mentions.json', mentions)
    subprocess.run(['git', 'diff', '--check'], check=True)
    format_paths = [s.SMALLSORT, *sorted(new.files)]
    format_before = {f: Path(f).read_bytes() for f in format_paths}
    command = [l.RUSTFMT, '--check', '--edition', '2024', '--config-path',
               l.RUSTFMT_CONFIG, s.SMALLSORT]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    assert not result.stdout
    assert format_before == {f: Path(f).read_bytes() for f in format_paths}
    (HERE / 'rustfmt-check.txt').write_text('command: ' + ' '.join(command) +
        '\nexit_code: 0\nstdout: <empty>\nstderr: ' + (result.stderr or '<empty>') +
        '\nsource_bytes_unchanged: true\n')
    request_path = HERE / 'RUN-REQUEST.json'
    request = json.loads(request_path.read_text())
    assert request_path.read_bytes() == (HERE.parent / 'RUN-REQUEST.json').read_bytes()
    assert request['request_id'] == 'renamemods-g1-20261106-01'
    assert request['kind'] == 'inventory' and request['agent'] == 'k1-merge'
    assert request['runner'] == 'gcb-e2-standard-4' and request['harnesses'] == []
    assert request['inventory'] is True and request['controls'] is False
    assert request['harness_timeout_minutes'] == 44
    write('cover-sites.json', covers)
    report = dict(status='PASS', base_sha=BASE, tooling_base=TOOLING,
                  library_commit=o.git('log', '-1', '--format=%H', '--', 'library'),
                  library_tree=o.git('rev-parse', 'HEAD:library'), ordinary=233,
                  controls=13, cfg_on=246, moved_files=8, renamed_identifiers=6,
                  message_sites_changed=64, distinct_message_literals_changed=len(expected_messages),
                  root_name_bijection=True, all_expanded_items_inverse_token_identical=True,
                  root_and_closure_inverse_token_identical=246,
                  closure_sha256=closures, cover_positions_and_arguments_preserved=True,
                  distinct_messages_preserved_in_each_root_closure=True,
                  smallsort_bytes_identical=True, tooling_unchanged=True,
                  overlong_lines=[], forbidden_comments_and_messages=[], legacy_name_exceptions=[],
                  substring_false_positive_lines=len(mentions),
                  substring_false_positive_details='remaining-name-mentions.json',
                  rustfmt_check='PASS', source_sha256={f: o.digest(v) for f, v in new.files.items()},
                  names_sha256={label: o.digest((HERE / (label + '-expected.txt')).read_text())
                                for label in ('ordinary', 'cfg-on')},
                  request_sha256=o.digest(request_path.read_text()),
                  compiler_inventory='NOT_RUN', new_proof_credit=False,
                  scope='Source tokens and inherited conservative identifier closures; '
                        'not compiler resolution or formal proof.')
    write('check-report.json', report)
    print(json.dumps({k: report[k] for k in ('status', 'ordinary', 'controls', 'cfg_on',
                     'moved_files', 'message_sites_changed', 'root_and_closure_inverse_token_identical')}))


if __name__ == '__main__':
    main()
