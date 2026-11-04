#!/usr/bin/env python3
"""Source-only VEIGHTINTEG checks; no cargo/rustc/Kani/CBMC. Run from this worktree."""
import difflib
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'codefix_checks', HERE.parent / 'codefix/check_codefix.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)
s = c.s
RUSTFMT = ('/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/'
           'scratchpad/rustfmt.sh')
V8 = '56efe5c477'
PRE_REVIEW = 'b4ad90657369b970a48921100bb01d05902372e7'
COVER_VARIANTS = {
    'realcontracts::unstable_network_safety_u8_n9_stubbed_with_callback_covers',
    'realcontracts::unstable_network_safety_u8_n13_stubbed_with_callback_covers',
    'permtags::network_u8_n9_with_panic_cover',
    'permtags::network_u8_n13_with_panic_cover',
}
REMOVED_COVERS = {
    'realcontracts::unstable_network_safety_u8_n9_stubbed':
        ['realcontracts comparator true', 'realcontracts comparator false'],
    'realcontracts::unstable_network_safety_u8_n13_stubbed':
        ['realcontracts comparator true', 'realcontracts comparator false'],
    'permtags::network_u8_n9': ['permtags: order violation panic is reachable'],
    'permtags::network_u8_n13': ['permtags: order violation panic is reachable'],
}
SOURCES = {'realcontracts': '588c002998', 'permtags': 'c59410d242',
           'scratchgeom': '151c193b63'}
NEW = {
    'realcontracts::swap_safety_u8_backing4': (19.355654, 6, 6, 'REALCONTRACTS G1r'),
    'realcontracts::swap_safety_u64_backing4': (19.362135, 6, 6, 'REALCONTRACTS G1r'),
    'realcontracts::swap_safety_bytes17_backing4': (31.84324, 6, 6, 'REALCONTRACTS G1r'),
    'realcontracts::swap_safety_u8_backing9': (17.355093, 6, 6, 'REALCONTRACTSTWO G1'),
    'realcontracts::swap_safety_u8_backing13': (17.583559, 6, 6, 'REALCONTRACTSTWO G1'),
    'realcontracts::unstable_network_safety_u8_n9_stubbed':
        (11.660206, 1, 3, 'REALCONTRACTSTWO G1'),
    'realcontracts::unstable_network_safety_u8_n13_stubbed':
        (13.978799, 1, 3, 'REALCONTRACTSTWO G1'),
    'realcontracts::insert_tail_safety_u64_tail1_to4_backing5':
        (34.020428, 7, 7, 'REALCONTRACTSTWO G1'),
    'realcontracts::sort4_safety_u64': (36.28767, 3, 3, 'REALCONTRACTSTWO G2'),
    'realcontracts::merge_safety_u64_len2': (27.213285, 4, 4, 'REALCONTRACTSTWO G2'),
    'realcontracts::merge_safety_u64_len4': (42.305798, 4, 4, 'REALCONTRACTSTWO G2'),
    'permtags::network_u8_n9': (13.415, 1, 2, 'PERMTAGS G1'),
    'permtags::network_u8_n13': (23.773, 1, 2, 'PERMTAGS G1'),
    'permtags::tag_types_preserve_source_routes': (0.064, 1, 1, 'PERMTAGS G1'),
    'scratchgeom::stable_u64_min_scratch_n2': (3.8116105, 2, 2, 'SCRATCHGEOM'),
}


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def format_source(text):
    return subprocess.check_output([
        RUSTFMT, '--edition', '2024', '--config-path', str(HERE.parent / 'codefix/rustfmt.toml'),
        '--config', 'skip_children=true', '--emit', 'stdout'], input=text, text=True)


def items_at(rev, path, formatted=False):
    text = subprocess.check_output(['git', 'show', f'{rev}:{path}'], text=True)
    return s.split_items(s.tree(s.lex(format_source(text) if formatted else text)))


def raw_items(text):
    return s.split_items(s.tree(s.lex(text)))


def main():
    old, new = s.Source(V8), s.Source(None)
    before, ordinary, cfg_on = old.roots(True), new.roots(False), new.roots(True)
    old_roots_changed = [n for n, (_, it) in before.items()
                         if n not in cfg_on or it.text() != cfg_on[n][1].text()]
    old_files_changed = [f for f, t in old.files.items()
                         if f != s.VERIFY_ROOT and new.files.get(f) != t]
    runtime = Path(s.SMALLSORT).read_text()
    runtime_items = raw_items(runtime)
    old_runtime = items_at(V8, s.SMALLSORT)

    fn_map = {it.name: it for it in runtime_items if it.kind == 'fn'}
    runtime_changed = [it.name for it in old_runtime if it.kind == 'fn'
                       and (it.name not in fn_map
                            or s.ser(it.body) != s.ser(fn_map[it.name].body))]
    # Read free-function signatures/bodies directly: the reused item splitter handles const
    # items as semicolon-terminated, whereas upstream ends with a const fn and no module item.
    def free_functions(text):
        tt = s.tree(s.lex(text))
        out = {}
        for i, t in enumerate(tt):
            if s.is_i(t, 'fn'):
                end = next(j for j in range(i + 2, len(tt)) if s.is_g(tt[j], '{'))
                out[tt[i + 1].text] = s.ser(tt[i:end + 1])
        return out
    upstream_text = subprocess.check_output(['git', 'show', f'{s.BASE}:{s.SMALLSORT}'], text=True)
    current_functions = free_functions(runtime)
    upstream_runtime_changed = [name for name, body in free_functions(upstream_text).items()
                                if current_functions.get(name) != body]
    request = json.loads((HERE.parent / 'RUN-REQUEST.json').read_text())
    expected_runtime = items_at(SOURCES['realcontracts'], s.SMALLSORT)
    runtime_exact = s.ser(s.tree(s.lex(runtime))) == s.ser(
        [t for it in expected_runtime for t in it.tokens()])
    source_body_changes = []
    extra_items = {}
    callback_cover_tokens = s.ser(s.tree(s.lex(
        'kani::cover(answer, "realcontracts comparator true");'
        'kani::cover(!answer, "realcontracts comparator false");')))
    for mod, rev in SOURCES.items():
        path = s.VERIFY_DIR + mod + '.rs'
        original = {(it.kind, it.name): it for it in items_at(rev, path, formatted=True)
                    if it.kind not in ('use', 'inner_doc')}
        current = {(it.kind, it.name): it for it in new.items[path]
                   if it.kind not in ('use', 'inner_doc')}
        for key, it in original.items():
            if mod == 'permtags' and key in (
                    ('macro_call', 'permutation_case')):
                # Macro calls share a key in this map; expanded root checks below are exact.
                continue
            actual = s.ser(current[key].body) if key in current else None
            if mod == 'realcontracts' and key == ('fn', 'arbitrary_less'):
                actual = actual.replace('comparison_covers ( answer ) ;', callback_cover_tokens)
            if actual != s.ser(it.body):
                source_body_changes.append(f'{mod}:{key}')
        extra_items[mod] = set(current) - set(original)
    expected_extra_items = {
        'realcontracts': {('fn', 'comparison_covers'), ('fn', 'omit_comparison_covers'),
            ('fn', 'unstable_network_safety_u8_n9_stubbed_with_callback_covers'),
            ('fn', 'unstable_network_safety_u8_n13_stubbed_with_callback_covers')},
        'permtags': {('fn', 'abort_without_panic_cover'), ('fn', 'network_u8_n9'),
                    ('fn', 'network_u8_n13')},
        'scratchgeom': set(),
    }
    cover_only_checks = []
    for mod in ('realcontracts', 'permtags'):
        original = s.Source(SOURCES[mod]).roots(True)
        for name in sorted(n for n in REMOVED_COVERS if n.startswith(mod + '::')):
            item = cfg_on[name][1]
            orig = original[name][1]
            actual = item.text().replace(
                '# [ kani : : stub ( comparison_covers , omit_comparison_covers ) ] ', '')
            actual = actual.replace('abort_without_panic_cover', 'abort_on_order_violation')
            cover_only_checks.append(actual == orig.text())
            suffix = '_with_callback_covers' if mod == 'realcontracts' else '_with_panic_cover'
            variant = cfg_on[name + suffix][1].text().replace(
                '# [ cfg ( kani_smallsort_controls ) ] ', '').replace(
                    name.split('::')[-1] + suffix, name.split('::')[-1])
            cover_only_checks.append(variant == orig.text())
    rc_items = {it.name: it for it in new.items[s.VERIFY_DIR + 'realcontracts.rs']}
    cover_only_checks.append(s.ser(rc_items['comparison_covers'].body[-1].children)
                             == callback_cover_tokens)
    cover_only_checks.append(not rc_items['omit_comparison_covers'].body[-1].children)
    pt_items = {it.name: it for it in new.items[s.VERIFY_DIR + 'permtags.rs']}
    panic_cut = s.ser(pt_items['abort_without_panic_cover'].body[-1].children)
    orig_panic = s.ser(pt_items['abort_on_order_violation'].body[-1].children).replace(
        'kani : : cover ( true , "permtags: order violation panic is reachable" ) ; ', '')
    cover_only_checks.append(panic_cut == orig_panic)
    packet_before = s.Source(PRE_REVIEW)
    unchanged_roots = []
    for name, (_, it) in packet_before.roots(True).items():
        if name in REMOVED_COVERS:
            continue
        if name not in cfg_on or it.text() != cfg_on[name][1].text():
            unchanged_roots.append(name)
    orphan_checks = {str(cfg): s.orphans(new, cfg) for cfg in (False, True)}
    changed_library = git('diff', '--name-only', s.BASE, '--', 'library').splitlines()
    outside = [f for f in changed_library
               if f not in (s.SMALLSORT, s.CARGO, s.VERIFY_ROOT)
               and not f.startswith(s.VERIFY_DIR)]
    # Mutations to check-cfg only are compared explicitly with the established v8 file.
    cargo_unchanged = not git('diff', V8, '--', s.CARGO)
    lane_diff = git('diff', c.TOOLING_BASE, '--name-only', '--', *c.LANES)
    old_runtime_text = subprocess.check_output(['git', 'show', f'{V8}:{s.SMALLSORT}'], text=True)
    matcher = difflib.SequenceMatcher(a=old_runtime_text.splitlines(), b=runtime.splitlines())
    added_runtime_numbers = set()
    for tag, _, _, j, end in matcher.get_opcodes():
        if tag in ('insert', 'replace'):
            added_runtime_numbers.update(range(j + 1, end + 1))
    inherited_long_lines = [f'{s.SMALLSORT}:{i}:{len(line)}'
                            for i, line in enumerate(runtime.splitlines(), 1)
                            if len(line) > 100 and i not in added_runtime_numbers]
    long_lines = [f'{f}:{i}:{len(line)}' for f, text in {**new.files, s.SMALLSORT: runtime}.items()
                  for i, line in enumerate(text.splitlines(), 1) if len(line) > 100
                  and (f != s.SMALLSORT or i in added_runtime_numbers)]
    rows = {}
    for f, text in new.files.items():
        lines = text.splitlines()
        opt = set()
        for it in new.items[f]:
            if new.file_gate[f] or s.gated(it.all_attrs):
                opt.update(range(it.first_line, it.last_line + 1))
        if new.file_gate[f]:
            opt = set(range(1, len(lines) + 1))
        rows[f] = {'total': len(lines), 'ordinary_or_shared': len(lines) - len(opt),
                   'opt_in_only': len(opt)}
    added_runtime = len(runtime.splitlines()) - len(subprocess.check_output(
        ['git', 'show', f'{V8}:{s.SMALLSORT}'], text=True).splitlines())
    checks = {
        'ordinary_204_plus_15': len(old.roots(False)) == 204
            and len(ordinary) == 219 and set(ordinary) == set(old.roots(False)) | set(NEW),
        'cfg_on_253_with_34_opt_in': len(cfg_on) == 253 and len(set(cfg_on) - set(ordinary)) == 34,
        'v8_212_roots_tokens_identical': not old_roots_changed,
        'all_existing_verify_files_except_module_doc_byte_identical': not old_files_changed,
        'all_existing_runtime_function_bodies_tokens_identical': not runtime_changed,
        'upstream_runtime_function_bodies_tokens_identical': not upstream_runtime_changed,
        'runtime_all_tokens_exactly_realcontractstwo': runtime_exact,
        'request_exactly_15_new_ordinary_success_roots':
            [r['name'] for r in request['harnesses']] == [s.PREFIX + n for n in sorted(NEW)]
            and all(r['expect'] == 'SUCCESS' for r in request['harnesses']),
        'request_prescribed_settings': request['kind'] == 'diagnostic'
            and request['inventory'] is True and request['controls'] is False
            and request['kani_jobs'] == 1 and request['harness_timeout_minutes'] == 10,
        'source_module_bodies_unchanged_after_cover_hook_expansion': not source_body_changes,
        'only_expected_cover_helpers_and_opt_in_variants_added':
            extra_items == expected_extra_items,
        'cover_only_adjustment_and_exact_original_opt_in_copies': all(cover_only_checks),
        'all_other_packet_roots_unchanged': not unchanged_roots,
        'only_four_opt_in_roots_added_to_packet':
            set(cfg_on) - set(packet_before.roots(True)) == COVER_VARIANTS,
        'cfg_off_and_on_no_static_orphans': not any(any(x) for x in orphan_checks.values()),
        'library_diff_paths_and_check_cfg_only': not outside and cargo_unchanged,
        'lane_files_equal_tooling_base': not lane_diff,
        'verify_and_new_runtime_line_width_100': not long_lines,
        'git_diff_check': all(subprocess.run(cmd, capture_output=True).returncode == 0
                              for cmd in (['git', 'diff', '--check'],
                                          ['git', 'diff', '--cached', '--check'])),
        'new_roots_prior_success_within_60s': len(NEW) == 15
            and all(v[0] <= 60 for v in NEW.values()),
    }
    total = {k: sum(v[k] for v in rows.values()) for k in next(iter(rows.values()))}
    report = {
        'status': 'PASS' if all(checks.values()) else 'FAIL', 'checks': checks,
        'v8': git('rev-parse', V8), 'tooling_base': git('rev-parse', c.TOOLING_BASE),
        'ordinary_before': 204, 'ordinary_after': len(ordinary), 'cfg_on': len(cfg_on),
        'new_roots': sorted(NEW), 'opt_in_roots': sorted(set(cfg_on) - set(ordinary)),
        'old_roots_changed': old_roots_changed, 'old_files_changed': old_files_changed,
        'runtime_changed': runtime_changed, 'upstream_runtime_changed': upstream_runtime_changed,
        'source_body_changes': source_body_changes,
        'cover_only_checks': cover_only_checks,
        'unchanged_packet_root_differences': unchanged_roots,
        'removed_ordinary_covers': REMOVED_COVERS,
        'coverage_change_base': PRE_REVIEW,
        'request_sha256': hashlib.sha256((HERE.parent / 'RUN-REQUEST.json').read_bytes())
            .hexdigest(),
        'expected_new_ordinary_covers': {'satisfied': 55, 'total': 55, 'unreachable': 0},
        'static_orphans': orphan_checks, 'outside_allowed_library': outside,
        'lane_diff': lane_diff, 'long_lines': long_lines,
        'inherited_runtime_long_lines': inherited_long_lines, 'verify_lines': rows,
        'verify_lines_total': total,
        'verify_lines_v8': sum(len(t.splitlines()) for t in old.files.values()),
        'runtime_lines': len(runtime.splitlines()), 'runtime_added_lines': added_runtime,
        'prior_ci_seconds_sum': sum(v[0] for v in NEW.values()),
        'prior_covers': {'satisfied': sum(v[1] for v in NEW.values()),
                         'total': sum(v[2] for v in NEW.values()), 'expected_unreachable': 6},
        'source_claims': {n: {'seconds': v[0], 'covers': [v[1], v[2]], 'report': v[3]}
                          for n, v in NEW.items()},
        'sha256': {f: hashlib.sha256(t.encode()).hexdigest()
                   for f, t in {**new.files, s.SMALLSORT: runtime}.items()},
        'limitations': 'Source macro expansion, cfg gates and token comparisons only; not compiler '
            'inventory or proof. Line split assigns explicit cfg-gated item spans to opt-in and '
            'remaining lines (shared helpers, blank lines and comments) to ordinary/shared. '
            'Prior times/covers are source-reported, not independently reverified here.',
    }
    expected_covers = {
        s.PREFIX + name: {'expect': 'SUCCESS', 'covers_satisfied': value[2]
                         - len(REMOVED_COVERS.get(name, [])),
                         'covers_total': value[2] - len(REMOVED_COVERS.get(name, [])),
                         'unreachable_covers': 0}
        for name, value in sorted(NEW.items())}
    HERE.joinpath('expected-covers.json').write_text(json.dumps(expected_covers, indent=2) + '\n')
    report['expected_covers_sha256'] = hashlib.sha256(
        HERE.joinpath('expected-covers.json').read_bytes()).hexdigest()
    HERE.joinpath('check-report.json').write_text(json.dumps(report, indent=2) + '\n')
    for name, roots in [('ordinary-expected', ordinary), ('cfg-on-expected', cfg_on),
                        ('opt-in-expected', set(cfg_on) - set(ordinary)), ('new-ordinary', NEW)]:
        HERE.joinpath(name + '.txt').write_text(''.join(s.PREFIX + n + '\n' for n in sorted(roots)))
    print(json.dumps({k: report[k] for k in ('status', 'checks', 'ordinary_after', 'cfg_on',
          'verify_lines_total', 'runtime_lines', 'runtime_added_lines',
          'prior_ci_seconds_sum')}, indent=2))
    return int(report['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
