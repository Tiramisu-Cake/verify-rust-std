#!/usr/bin/env python3
"""Source-only TIDYDOCS checks. Run at the worktree root; no compiler is invoked.

Reuse the existing lexer and macro expander without changing tooling. Only direct string
message arguments of assert!, kani::assert, and kani::cover may be normalized. The single
new control must match an exact token template. Runtime cover counts remain CI evidence.
"""
import difflib
from functools import lru_cache
import hashlib
import importlib.util
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('source_checks', HERE.parent / 'codefix/trimpart_static.py')
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)
BASE = '44b972435a'
TOOLING = '59893bff1fbb2af1a0c08862afd7e3bb87c19cdd'
CONTROL = 'realcontracts::rejects_swap_comparator_writing_outside_frame_u8'
CONTROL_FILE = s.VERIFY_DIR + 'realcontracts.rs'
LINE_LIMIT = 100
CONTROL_SOURCE = '''#[cfg(kani_smallsort_controls)]
#[kani::proof_for_contract(swap_if_less)]
fn rejects_swap_comparator_writing_outside_frame_u8() {
    let mut v: [u8; 4] = kani::any();
    let mut comparisons = 0u8;
    let mut is_less = |a: &u8, b: &u8| {
        comparisons = comparisons.wrapping_add(1);
        *a < *b
    };
    unsafe { swap_if_less(v.as_mut_ptr(), 0, 1, &mut is_less) };
}'''
LANES = ['.circleci', '.github/workflows', 'research/challenge-8/kani-k1/tools',
         'research/challenge-8/kani-k1/gcb', 'scripts/run-kani.sh',
         'tool_config/kani-version.toml', 'rust-toolchain.toml', '.gitmodules', '.cargo',
         'library/.cargo', 'library/Cargo.toml', 'library/Cargo.lock']
FORBIDDEN = re.compile(r'\b(?:GCB|G1|G2|lane|REALCONTRACTSTWO|realcontractstwo|original|historical)\b'
                       r'|Part [12]|research roots|prior .*SUCCESS', re.I)


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()


def flat_tokens(text):
    return [(t.kind, t.text) for t in s.lex(text) if t.kind != 'doc']


@lru_cache(maxsize=None)
def normalized(text):
    """Leave predicates and all other literals unchanged, including numeric messages."""
    tokens = s.tree(s.lex(text))
    messages = []

    def walk(ts):
        for i, t in enumerate(ts):
            if t.kind != 'group':
                continue
            macro = i >= 2 and s.is_i(ts[i - 2], 'assert') and s.is_p(ts[i - 1], '!')
            kani_call = (i >= 4 and s.is_i(ts[i - 4], 'kani')
                         and s.is_p(ts[i - 3], ':') and s.is_p(ts[i - 2], ':')
                         and s.is_i(ts[i - 1]) and ts[i - 1].text in ('assert', 'cover'))
            if t.text == '(' and (macro or kani_call):
                # Only literal message arguments after the predicate. Nested predicate groups
                # are never interpreted as argument separators.
                comma = next((j for j, x in enumerate(t.children) if s.is_p(x, ',')), None)
                if comma is not None:
                    for j in range(comma + 1, len(t.children)):
                        x = t.children[j]
                        if x.kind == 'lit' and x.text.startswith('"'):
                            messages.append(x.text)
                            x.text = '"<message>"'
            walk(t.children)
    walk(tokens)
    return s.ser(tokens), messages


def comment_lines(text):
    return sum(line.lstrip().startswith('//') for line in text.splitlines())


def count_covers(text):
    return len(re.findall(r'\bkani : : cover \(', normalized(text)[0]))


def overlong_lines(text):
    return [{'line': n, 'length': len(line)}
            for n, line in enumerate(text.splitlines(), 1) if len(line) > LINE_LIMIT]


def main():
    assert not overlong_lines('x' * LINE_LIMIT)
    assert overlong_lines('x' * (LINE_LIMIT + 1)) == [{'line': 1, 'length': 101}]
    # The message allowance must not hide literals in a predicate, attribute, or other call.
    assert normalized('kani::assert(x == "p", "a");')[0] == normalized('kani::assert(x == "p", "b");')[0]
    assert normalized('assert!(x, "a");')[0] == normalized('assert!(x, "b");')[0]
    for a, b in [('kani::assert(x == "p", "m");', 'kani::assert(x == "q", "m");'),
                 ('#[kani::unwind(25)] fn f() {}', '#[kani::unwind(26)] fn f() {}'),
                 ('other("a");', 'other("b");'),
                 ('kani::cover(x, "m");', 'kani::cover(!x, "m");')]:
        assert normalized(a)[0] != normalized(b)[0]
    old, new = s.Source(BASE), s.Source(None)
    assert set(old.files) == set(new.files)
    verify_overlong = {path: overlong_lines(text) for path, text in new.files.items()
                       if overlong_lines(text)}
    assert not verify_overlong, ('verify lines exceed 100 characters', verify_overlong)
    real = new.files[CONTROL_FILE]
    # The exact new item is last; remove its attributes and body using the source splitter.
    added = [it for it in s.split_items(s.tree(s.lex(real)))
             if it.kind == 'fn' and it.name == CONTROL.split('::')[-1]]
    assert len(added) == 1
    assert normalized(added[0].text())[0] == normalized(CONTROL_SOURCE)[0]
    # No messages exist in the new control; its other literals must match too.
    assert flat_tokens(added[0].text()) == flat_tokens(CONTROL_SOURCE)
    begin = real.index('#[cfg(kani_smallsort_controls)]', real.index('// The order is lawful;'))
    without_control = real[:begin]
    assert normalized(real[begin:])[0] == normalized(CONTROL_SOURCE)[0]

    messages_changed = []
    counts = {}
    for path, before in old.files.items():
        after = without_control if path == CONTROL_FILE else new.files[path]
        a, labels_a = normalized(before)
        b, labels_b = normalized(after)
        assert a == b, ('non-message code changed', path)
        assert len(labels_a) == len(labels_b)
        for x, y in zip(labels_a, labels_b):
            if x != y:
                assert path == CONTROL_FILE
                assert x.startswith('"realcontractstwo ') and y == x.replace('realcontractstwo ', 'realcontracts ', 1)
                messages_changed.append({'file': path, 'before': x, 'after': y})
        counts[path] = {'before': comment_lines(before), 'after': comment_lines(new.files[path])}
        # Search human comments and messages, never immutable identifiers.
        comments = '\n'.join(l for l in new.files[path].splitlines() if l.lstrip().startswith('//'))
        assert not FORBIDDEN.search(comments), (path, 'forbidden comment', FORBIDDEN.search(comments))
        assert all(not FORBIDDEN.search(label) for label in normalized(new.files[path])[1])
    assert messages_changed

    small_before = subprocess.check_output(['git', 'show', BASE + ':' + s.SMALLSORT], text=True)
    small_after = Path(s.SMALLSORT).read_text()
    strip = lambda t: ''.join(l for l in t.splitlines(keepends=True) if not l.lstrip().startswith('//'))
    assert strip(small_before) == strip(small_after), 'non-comment lines differ bytewise'
    changes = []
    for op, a, b, c, d in difflib.SequenceMatcher(None, small_before.splitlines(), small_after.splitlines()).get_opcodes():
        if op == 'equal':
            continue
        assert op == 'insert', ('smallsort.rs must only add comments', op)
        lines = small_after.splitlines()[c:d]
        assert all(l.lstrip().startswith('//') for l in lines)
        changes.extend(lines)
    assert len(changes) == 9
    smallsort_new_overlong = overlong_lines('\n'.join(changes))
    assert not smallsort_new_overlong, ('new smallsort.rs lines exceed 100 characters',
                                       smallsort_new_overlong)
    counts[s.SMALLSORT] = {'before': comment_lines(small_before), 'after': comment_lines(small_after)}

    before, after = old.roots(False), new.roots(False)
    on_before, on_after = old.roots(True), new.roots(True)
    assert len(before) == len(after) == 233 and set(before) == set(after)
    assert len(on_before) == 267 and len(on_after) == 268
    assert set(on_after) == set(on_before) | {CONTROL} and CONTROL not in after
    assert sum('reject' in n for n in set(on_before) - set(before)) == 12
    assert len(set(on_before) - set(before)) - 12 == 22
    # Cover call locations, predicates, and message argument counts are preserved in every
    # ordinary expanded root and its conservatively resolved dependency closure.
    cover_checks = {}
    for name in sorted(before):
        a = s.closure(old, [before[name]], False)
        b = s.closure(new, [after[name]], False)
        assert set(a) == set(b), (name, 'dependencies changed')
        for key in a:
            assert normalized(a[key].text())[0] == normalized(b[key].text())[0], (name, key)
            assert count_covers(a[key].text()) == count_covers(b[key].text())
        cover_checks[name] = sum(count_covers(it.text()) for it in a.values())
    assert all(normalized(on_before[n][1].text())[0] == normalized(on_after[n][1].text())[0]
               for n in on_before)
    # No library files outside the permitted set changed, and lane/tooling stays frozen.
    permitted = set(new.files) | {s.SMALLSORT}
    assert set(git('diff', '--name-only', BASE, '--', 'library').splitlines()) <= permitted
    assert not git('diff', '--name-only', TOOLING, '--', *LANES)
    subprocess.run(['git', 'diff', '--check'], check=True)
    for name, roots in [('ordinary-expected.txt', after), ('cfg-on-expected.txt', on_after)]:
        (HERE / name).write_text(''.join(s.PREFIX + n + '\n' for n in sorted(roots)))
    request = json.loads((HERE.parent / 'RUN-REQUEST.json').read_text())
    assert request == json.loads((HERE / 'RUN-REQUEST.json').read_text())
    assert request['request_id'] == 'tidydocs-g1-20261106-01'
    assert request['agent'] == 'k1-merge' and request['kind'] == 'diagnostic'
    assert request['controls'] is True and request['inventory'] is False
    assert request['runner'] == 'gcb-e2-standard-4' and request['kani_jobs'] == 1
    assert request['harness_timeout_minutes'] == 5
    wanted = [
        {'name': s.PREFIX + CONTROL, 'expect': 'FAILED', 'expect_check': 'assignable'},
        *({'name': s.PREFIX + 'realcontracts::' + n, 'expect': 'SUCCESS'} for n in
          ['swap_safety_u8_backing9', 'unstable_network_safety_u8_n9_stubbed', 'sort4_safety_u64'])
    ]
    assert request['harnesses'] == wanted
    covers = {s.PREFIX + 'realcontracts::' + n: count for n, count in
              [('swap_safety_u8_backing9', 6), ('unstable_network_safety_u8_n9_stubbed', 1),
               ('sort4_safety_u64', 3)]}
    (HERE / 'expected-covers.json').write_text(json.dumps(covers, indent=2) + '\n')
    report = {
        'status': 'PASS',
        'request_sha256': sha((HERE / 'RUN-REQUEST.json').read_text()),
        'request_validation': 'PASS', 'positive_g1_expected_covers': 10, 'base_sha': git('rev-parse', BASE), 'tooling_base': TOOLING,
        'library_commit': git('log', '-1', '--format=%H', '--', 'library'),
        'library_tree': git('rev-parse', 'HEAD:library'),
        'line_length_limit': LINE_LIMIT,
        'verify_lines_over_limit': verify_overlong,
        'smallsort_new_lines_over_limit': smallsort_new_overlong,
        'smallsort_existing_lines_over_limit': len(overlong_lines(small_before)),
        'non_comment_smallsort_bytes_equal': True, 'smallsort_added_comment_lines': len(changes),
        'verify_code_equal_except_message_literals_and_exact_new_control': True,
        'ordinary_before': len(before), 'ordinary_after': len(after), 'ordinary_names_equal': True,
        'existing_negative_controls': 12, 'other_opt_in': 22, 'new_negative_controls': 1,
        'cfg_on_after': len(on_after), 'new_control': CONTROL,
        'ordinary_cover_structure_equal_roots': len(cover_checks),
        'ordinary_cover_dependency_source_sites': cover_checks,
        'v8c_runtime_covers_source_reported': 966,
        'runtime_covers_remeasured': False, 'compiler_inventory': 'NOT_RUN',
        'negative_control_calibration': 'PENDING_COORDINATOR_GO_AND_G1',
        'forbidden_comments_and_messages': [],
        'message_changes': messages_changed, 'comment_line_counts': counts,
        'source_sha256': {p: sha(Path(p).read_text()) for p in sorted(permitted)},
        'ordinary_names_sha256': sha((HERE / 'ordinary-expected.txt').read_text()),
        'scope': 'Source equality and macro-expanded expected names, not compiler inventory or new proof credit.'
    }
    (HERE / 'check-report.json').write_text(json.dumps(report, indent=2) + '\n')
    (HERE / 'comment-lines.tsv').write_text('file\tbefore\tafter\n' + ''.join(
        f'{p}\t{c["before"]}\t{c["after"]}\n' for p, c in sorted(counts.items())))
    print(json.dumps({k: report[k] for k in ['status', 'ordinary_after', 'cfg_on_after',
          'ordinary_cover_structure_equal_roots', 'smallsort_added_comment_lines']}))
    print('message literals changed:', len(messages_changed))


if __name__ == '__main__':
    main()
