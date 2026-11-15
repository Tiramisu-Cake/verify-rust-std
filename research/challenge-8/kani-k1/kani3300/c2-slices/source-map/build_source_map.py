#!/usr/bin/env python3
"""Static Git inventory only. Does not build, apply patches, or change source refs."""
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent
REPO = Path('/root/kani-fix-3300-c2-s6')
U = '0aac16ef62da9e9d5645782d458593e5d78143ba'
B1 = '6fe484b30043b3696b5f1ccc4bea0e42891ad012'
F = 'ad499e41dd2db9ccd432f89721638a1f3a0bbd44'
M = 'kani-compiler/src/kani_middle/'
C = 'kani-compiler/src/codegen_cprover_gotoc/'
T = M + 'transform/check_uninit/'
V = T + 'ptr_uninit/uninit_visitor.rs'
L = T + 'ty_layout.rs'


def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def between(n, a, b):
    return a <= n <= b


def owner(path, side, n, anchor):
    """One owner per +/- line, in B1/F coordinates. See SEAMS for adaptations."""
    if path.startswith(C):
        if path == C + 'compiler_interface.rs':
            return '7' if (side == '+' and between(n, 92, 96)) else '2'
        return '2'
    if path == 'kani-compiler/src/codegen_aeneas_llbc/compiler_interface.rs':
        return '7'
    if path in [M + 'anonymous_allocations.rs', M + 'mod.rs', M + 'points_to/points_to_graph.rs']:
        return '2'
    if path == M + 'points_to/mod.rs':
        return '1'
    if path == M + 'points_to/points_to_analysis.rs':
        if (side == '+' and (between(n, 580, 581) or between(n, 600, 601))) or (
            side == '-' and (between(n, 405, 410) or between(n, 429, 434))
        ):
            return '2'
        return '1'
    if path == T + 'delayed_ub/initial_target_visitor.rs':
        # RawEq seeds/comment belong to3; tcx/body plumbing is first consumed by2.
        if side == '+' and (between(n, 76, 77) or between(n, 115, 117) or between(n, 123, 126)):
            return '3'
        if side == '-' and (n == 68 or between(n, 106, 108)):
            return '3'
        if (side == '+' and between(n, 145, 146)) or (side == '-' and n == 132):
            return '1'
        return '2'
    if path == T + 'delayed_ub/instrumentation_visitor.rs':
        return '1'
    if path == T + 'delayed_ub/mod.rs':
        if side == '+':
            if n == 18:
                return '7'  # TransformationResult import removal waits for both writer replacements.
            if n == 80 or n == 88 or between(n, 158, 161):
                return '2'
            if n == 180:
                return '4'
            if n == 191 or n == 212:
                return '7'
        else:
            if n == 15:
                return '7'
            if n == 76:
                return '2'
            if between(n, 143, 145):
                return '7'
        return '1'
    if path == M + 'transform/mod.rs':
        return '2' if side == '+' and n == 73 else '7'
    if path == M + 'transform/delayed_cache.rs':
        return '7'
    if path == L:
        if side == '+':
            # Minimal borrowed qualification prerequisites; no typed transfer builders.
            if between(n, 8, 10) or n == 14 or between(n, 119, 139) or between(n, 178, 192):
                return '2'
            if between(n, 345, 346) or n == 359 or between(n, 389, 392) or n == 426:
                return '3'
            if between(n, 481, 508):
                return '5'
        else:
            if n == 8 or n == 12:
                return '2'
            if n == 260 or n == 273 or between(n, 336, 338):
                return '3'
            if n == 395:
                return '5'
        return '4'
    if path == T + 'mod.rs':
        if side == '+' and between(n, 936, 950):
            return '2'
        if side == '+' and between(n, 454, 458):
            return '3'  # CheckAs on reference places, RawEq extent path.
        return '4'
    if path == T + 'relevant_instruction.rs':
        if (side == '+' and (between(n, 327, 338) or n in (318, 344))) or (
            side == '-' and n == 291
        ):
            return '3'
        # ProjectionElem import shares a wrapped line with retained names: earliest consumer3.
        if side == '+' and between(n, 12, 13):
            return '3'
        if side == '-' and between(n, 12, 13):
            return '3'
        return '4'
    if path == V:
        if side == '+':
            if between(n, 420, 424):
                return '4'  # Accepted variant C; marked-model prerequisites stay together.
            if between(n, 649, 680):
                return '3'
            if n == 544 or between(n, 1179, 1184):
                return '1'
        else:
            if n == 683:
                return '3'
            if n == 282 or between(n, 763, 765):
                return '1'
        return '4'
    if path in [T + 'ptr_uninit/mod.rs', M + 'kani_functions.rs', 'library/kani_core/src/mem_init.rs']:
        return '4'
    raise ValueError(f'Unmapped production path: {path}')


def blob_info(ref, path):
    raw = git('ls-tree', ref, '--', path).decode().strip()
    if not raw:
        return {'mode': None, 'blob': None, 'sha256': None, 'lines': 0}
    mode, typ, blob = raw.split('\t')[0].split()
    data = git('cat-file', 'blob', blob)
    return {'mode': mode, 'blob': blob, 'sha256': sha(data), 'lines': len(data.splitlines())}


def symbol(lines, n):
    candidates = []
    for i, line in enumerate(lines[:n], 1):
        match = re.match(r'\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(fn|struct|enum|trait|mod|impl)\s+(.+)', line)
        if match:
            candidates.append((i, match.group(0).strip()))
    return {'line': candidates[-1][0], 'declaration': candidates[-1][1]} if candidates else None


def parse_pair(label, base, target):
    patch = git('diff', '--no-ext-diff', '--no-renames', '--full-index', '--binary', '--unified=0', base, target, '--', 'kani-compiler', 'library')
    (OUT / (label + '.patch')).write_bytes(patch)
    rows = []
    current = None
    for line in patch.decode().splitlines(keepends=True):
        if line.startswith('diff --git '):
            path = line.rstrip().split(' b/', 1)[1]
            current = {'path': path, 'hunks': []}
            rows.append(current)
        elif line.startswith('@@ '):
            match = re.match(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)', line)
            old_start, old_count = int(match[1]), int(match[2] or 1)
            new_start, new_count = int(match[3]), int(match[4] or 1)
            h = {'header': line.rstrip(), 'old': [old_start, old_count], 'new': [new_start, new_count], 'lines': []}
            current['hunks'].append(h)
        elif current and current['hunks'] and line[0] in '+-\\':
            current['hunks'][-1]['lines'].append(line)
    checks = []
    count = 0
    for file_index, row in enumerate(rows, 1):
        path = row['path']
        row['identities'] = {name: blob_info(ref, path) for name, ref in [('U', U), ('B1', B1), ('F', F)]}
        old_data = git('show', base + ':' + path) if row['identities']['U' if base == U else 'B1']['blob'] else b''
        new_data = git('show', target + ':' + path) if row['identities']['B1' if target == B1 else 'F']['blob'] else b''
        old_lines, new_lines = old_data.splitlines(keepends=True), new_data.splitlines(keepends=True)
        rebuilt = []
        cursor = 0
        for hi, h in enumerate(row['hunks'], 1):
            count += 1
            h['id'] = f'{label}:{file_index:02}:{hi:03}'
            h['sha256'] = sha((h['header'] + '\n' + ''.join(h['lines'])).encode())
            h['symbol_old'] = symbol([x.decode() for x in old_lines], h['old'][0])
            h['symbol_new'] = symbol([x.decode() for x in new_lines], h['new'][0])
            h['parts'] = []
            old_pos, new_pos = h['old'][0], h['new'][0]
            for line in h['lines']:
                side = line[0]
                if side == '\\':
                    raise ValueError('No-newline marker requires explicit handling')
                n = old_pos if side == '-' else new_pos
                selected = 'B1' if label == 'U--B1' else owner(path, side, n, h['new'][0])
                if h['parts'] and h['parts'][-1]['side'] == side and h['parts'][-1]['owner'] == selected and h['parts'][-1]['start'] + h['parts'][-1]['count'] == n:
                    part = h['parts'][-1]
                    part['count'] += 1
                    part['_text'] += line[1:]
                else:
                    h['parts'].append({'side': side, 'start': n, 'count': 1, 'owner': selected, '_text': line[1:]})
                if side == '-':
                    old_pos += 1
                else:
                    new_pos += 1
            assert old_pos - h['old'][0] == h['old'][1]
            assert new_pos - h['new'][0] == h['new'][1]
            for part in h['parts']:
                part['sha256'] = sha(part.pop('_text').encode())
            h['owners'] = sorted({p['owner'] for p in h['parts']})
            pos = h['old'][0] - 1 if h['old'][1] else h['old'][0]
            rebuilt.extend(old_lines[cursor:pos])
            deleted = [line[1:].encode() for line in h['lines'] if line[0] == '-']
            assert deleted == old_lines[pos:pos + h['old'][1]], (label, path, h['id'])
            rebuilt.extend(line[1:].encode() for line in h['lines'] if line[0] == '+')
            cursor = pos + h['old'][1]
            del h['lines']
        rebuilt.extend(old_lines[cursor:])
        assert b''.join(rebuilt) == new_data, (label, path)
        checks.append({'path': path, 'in_memory_patch_reconstruction': 'EXACT', 'sha256': sha(new_data)})
    result = {'base': base, 'target': target, 'diff_algorithm': 'git default/myers, --no-renames -U0', 'patch_sha256': sha(patch), 'files': rows}
    dump(label + '.json', result)
    return result, checks


def main():
    a, ac = parse_pair('U--B1', U, B1)
    b, bc = parse_pair('B1--F', B1, F)
    # Direct U->F checksum is an independent endpoint, not a third ownership assignment.
    direct = git('diff', '--no-ext-diff', '--no-renames', '--full-index', '--binary', '--unified=0', U, F, '--', 'kani-compiler', 'library')
    (OUT / 'U--F.patch').write_bytes(direct)
    refs = {}
    for name, ref in [('U', U), ('B1', B1), ('F', F), ('pre_F7', 'ad324418cd')]:
        full = git('rev-parse', ref).decode().strip()
        refs[name] = {'sha': full, 'tree': git('rev-parse', full + '^{tree}').decode().strip(),
                      'parents': git('show', '-s', '--format=%P', full).decode().strip().split(),
                      'author_time': git('show', '-s', '--format=%aI', full).decode().strip(),
                      'committer_time': git('show', '-s', '--format=%cI', full).decode().strip()}
    assert refs['B1']['parents'] == [U]
    assert refs['F']['tree'] == '9829702c1aa0ecb73c860fc0ad5451757917d6cb'
    subprocess.run(['git', '-C', str(REPO), 'merge-base', '--is-ancestor', B1, F], check=True)
    all_paths = git('diff', '--name-status', '--no-renames', U, F).decode().splitlines()
    production = {r['path'] for r in b['files']} | {r['path'] for r in a['files']}
    delegated = [line for line in all_paths if line.split('\t')[-1] not in production]
    assert all(line.split('\t')[-1].startswith(('tests/', 'docs/')) for line in delegated), delegated
    dump('INPUTS.json', {'observed_at_utc': datetime.now(timezone.utc).isoformat(), 'g0_entry': '203c712c6b7ac3898f105c3ca89fe0d9a026baf6',
        'source': str(REPO), 'b1_checkout': '/root/kani-fix-b1-upstream', 'worker14_worktree': '/root/kani-fix-3300-c2-slices-w14',
        'refs': refs, 'lineage': 'U -> existing B1 -> logical slices1..6 -> separate F7; no rebase',
        'upstream_snapshot': 'UPSTREAM-SNAPSHOT.json', 'production_files': sorted(production),
        'worker15_delegated_paths': delegated, 'delegated_scope': 'No test/oracle/docs ownership decisions in worker14 inventory; embedded unit code is inventoried with its source owner, oracle mapping belongs to worker15.'})
    tally = Counter()
    for r in b['files']:
        for h in r['hunks']:
            for part in h['parts']:
                tally[part['owner'] + part['side']] += part['count']
    md = ['# FILE/HUNK-MAP — worker14, stage0', '',
          'Canonical ownership: `U--B1.json`, `B1--F.json`; full zero-context source patches alongside.',
          'Coordinates: old/new are [start,count] in the named base/target blobs, not future slice heads.',
          'Each +/- source line has exactly one owner. Multi-owner Git hunks are split by `parts`.',
          'Parts are bookkeeping ranges, not independently applicable patches. Shared imports and moved baseline code require coherent edits.',
          'Original blob IDs/modes/SHA256, symbol anchors and hunk/part SHA256 are in JSON. U--F.patch is endpoint cross-check only.', '',
          'B1 remains the existing parent; changes after B1 are never attributed back to #5172.', '']
    for label, obj in [('U--B1', a), ('B1--F', b)]:
        md += [f'## {label}', '']
        for row in obj['files']:
            md += ['### ' + row['path'], '', '| ID | old → new [start,count] | owner |', '|---|---|---|']
            for h in row['hunks']:
                md.append(f"| `{h['id']}` | {h['old']} → {h['new']} | {','.join(h['owners'])} |")
            md.append('')
    (OUT / 'FILE-HUNK-MAP.md').write_text('\n'.join(md).rstrip() + '\n')
    slices = {}
    for selected in map(str, range(1, 8)):
        parts = []
        for row in b['files']:
            for h in row['hunks']:
                for i, part in enumerate(h['parts']):
                    if part['owner'] == selected:
                        parts.append({'hunk_id': h['id'], 'part_index': i, 'path': row['path'], **part})
        slices[selected] = {
            'prerequisite_heads': ['B1'] if selected == '1' else [str(int(selected) - 1)],
            'source_parts': parts,
            'source_changed_lines': sum(p['count'] for p in parts),
            'tests_docs_map': 'worker15/oracle-map; not assigned by worker14',
            'implemented': False, 'native_qualification': 'NOT_RUN'}
    slices['1'].update(qualification_kind='NO_REGRESSION', integration_status='PENDING', integration_heads=[4, 5])
    dump('DEPENDENCIES.json', {
        'order': ['U', 'B1', '1', '2', '3', '4', '5', '6', '7'],
        'slices': slices,
        'borrowed_prerequisites': [
            {'owner': '2', 'outline_owner': '4', 'reason': 'immutable_origin_type_supported already needs recognition/for_storage',
             'symbols': ['immutable_origin_type_supported', 'wrapper_inner', 'maybe_uninit_storage', 'PointeeInfo::for_storage'],
             'consumers': ['2', '4'], 'coordinator_map_review_required_before_code': False, 'accepted_by': 'TASK variant C @4fef62ad67'},
            {'owner': '4', 'outline_owner': '6', 'reason': 'MU raw assignments and address formation require projected-place checks now',
             'symbols': ['address_of_raw_deref', 'visit_ordinary_assignment including F420-424', 'visit_rvalue F951-975'],
             'consumers': ['4', '6'], 'coordinator_map_review_required_before_code': False, 'accepted_by': 'TASK variant C @4fef62ad67'},
            {'owner': '4', 'outline_owner': '6', 'reason': 'Accepted variant C: ordinary-union constant assignment required by marked-model controls on head4',
             'symbols': ['visit_ordinary_assignment F420-424'], 'consumers': ['4', '6'],
             'coordinator_map_review_required_before_code': False, 'accepted_by': 'TASK variant C @4fef62ad67'}],
        'additional_semantic_edges': [['2', '3'], ['3', '5'], ['4', '6'], ['2', '7'], ['1', '7']],
        'U_prerequisites': ['checked_body/constructor and tail-call paths', 'atomic store post-setter and nonvolatile reads',
                            'InitializeMemoryInitializationState marker and KaniMemoryInitializationState private state fields'],
        'head6_residual': {'exact_F_parts': slices['7']['source_parts'], 'non_F_adaptations': 'PRE-F7.json'},
        'head1_captured_closure_regression': 'NOT_ESTABLISHED; coordinator Quick must decide; STOP if a new ordinary regression is reached',
        'combined_stage0_acceptance': 'VARIANT_C_ACCEPTED_BY_TASK_AT_4fef62ad67; static maps are not runtime results',
        'recomposed_tree': 'NOT_CREATED'})
    pre_path = T + 'delayed_ub/mod.rs'
    pre_lines = git('show', refs['pre_F7']['sha'] + ':' + pre_path).decode().splitlines(keepends=True)
    snippets = []
    for start, length, name in [(18, 1, 'TransformationResult import'), (191, 3, 'ordinary delayed write'), (214, 1, 'failed-root delayed write')]:
        data = ''.join(pre_lines[start - 1:start - 1 + length])
        snippets.append({'name': name, 'start': start, 'count': length, 'text': data, 'sha256': sha(data.encode()),
                         'temporary_owner': '1..6', 'replacement_owner': '7'})
    dump('PRE-F7.json', {'commit': refs['pre_F7']['sha'], 'path': pre_path,
        'blob': git('rev-parse', refs['pre_F7']['sha'] + ':' + pre_path).decode().strip(),
        'snippets': snippets, 'F_replacements': [
            {'start': 18, 'count': 1, 'role': 'remove TransformationResult import'},
            {'start': 191, 'count': 1, 'role': 'replace ordinary delayed write'},
            {'start': 212, 'count': 1, 'role': 'replace failed-root write'}],
        'no_structural_isolation_credit_before_7': True})
    # Search every F compiler/runtime Rust blob, including unchanged potential consumers.
    names = '''resolve_call AnalysisBodyOverride BodyProvenance AnalysisKey PointsToAnalysisError
        ActiveCalls CallerLocation run_points_to_analysis anonymous_origins AnonymousOrigin referent_extent
        target_matches constant_successors ImmutableAllocations Descriptor ConstantCollector seed_returns
        observe_immutable_origins register_immutable_static prepare_immutable_allocations
        bind_immutable_allocation finalize_immutable_allocations immutable_origin_type_supported
        wrapper_inner maybe_uninit_storage for_storage for_typed_storage for_deinit argument_size
        constant_init_mask SetStorage CheckRefAs BeginArgumentTransfer transfer_mask has_transfer_protocol
        transfers_shadow needs_nested_call_reset reset_nested_call enclosing_union assign_storage_operand
        unsupported_storage_assignment assign_storage typed_storage_mask maybe_uninit_transmute
        address_of_raw_deref visit_ordinary_assignment DelayedCache DelayedTransformationScope
        delayed_scope replace_delayed_body begin_argument_transfer'''.split()
    uses = {name: [] for name in names}
    pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, names)) + r')\b')
    paths = git('ls-tree', '-r', '--name-only', F, '--', 'kani-compiler', 'library').decode().splitlines()
    for path in paths:
        if not path.endswith('.rs'):
            continue
        for n, line in enumerate(git('show', F + ':' + path).decode().splitlines(), 1):
            for name in set(pattern.findall(line)):
                uses[name].append({'path': path, 'line': n, 'text': line.strip()})
    dump('SEAM-USES.json', {'source': F, 'scope': 'all tracked kani-compiler/**/*.rs and library/**/*.rs in F',
        'assurance': 'LEXICAL_ONLY: includes declarations/comments/same-spelling unrelated items; SEAMS.md identifies semantic consumers',
        'symbols': uses})
    dump('STATIC-CHECKS.json', {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
        'B1_parent_is_U': True, 'B1_ancestor_of_F': True, 'F_tree_exact': True,
        'production_paths': len(production), 'U_to_B1_source_hunks': sum(len(r['hunks']) for r in a['files']),
        'B1_to_F_source_hunks': sum(len(r['hunks']) for r in b['files']), 'owned_changed_line_counts': dict(sorted(tally.items())),
        'unassigned_changed_source_lines': 0, 'duplicate_owned_changed_source_lines': 0,
        'delegated_test_doc_paths': len(delegated), 'all_other_U_to_F_paths_are_tests_or_docs': True,
        'in_memory_reconstruction': {'U_to_B1': ac, 'B1_to_F': bc}, 'U_to_F_patch_sha256': sha(direct),
        'slice_code_written': False, 'native_builds': 'NOT_RUN', 'CI': 'NOT_RUN', 'push': 'NOT_RUN',
        'intermediate_compile_behavior': 'NOT_ESTABLISHED', 'final_recomposed_head': 'NOT_CREATED',
        'worker15_oracle_map': 'INDEPENDENT_PARALLEL_SCOPE_NOT_ACCEPTED_HERE'})
    print(json.dumps({'source_files': len(production), 'hunks': [sum(len(r['hunks']) for r in x['files']) for x in [a, b]], 'line_owners': dict(sorted(tally.items())), 'delegated_paths': len(delegated)}))


if __name__ == '__main__':
    main()
