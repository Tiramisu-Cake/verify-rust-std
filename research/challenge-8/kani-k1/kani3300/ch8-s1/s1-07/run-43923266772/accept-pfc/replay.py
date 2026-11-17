#!/usr/bin/env python3
"""Exact S1-07 PFC component, bounded source-reported Profiles v4 policy.

Only structured retained evidence, git object reads and c++filt are inputs.
This is deliberately not an admission-root classifier or a Rust parser.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RUN = HERE.parent
G0 = HERE.parents[7]
STD = Path('/root/verify-rust-std-ch8-s1-04-w13')
CONTROL = Path('/root/kani-ch8-s1-07-w13')
SOURCE = '5be85699b8826e3286c0bf89efb9affefac0acb5'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
CONTROL_SHA = 'b37f6f75c5b7b77e84297cd7104f9c0868502fd4'
ENTRY = '2f3ede5ff46ace1c2058f01f8ecda06799674b57'
REQUEST_SHA = '6c483ce754cd8e99c01953bf4c40a145b10529d7990aa52c28ef32c00b980cd7'
PREFIX = '/home/runner/work/kani/kani/export/'
SMALL = 'library/core/src/slice/sort/shared/smallsort.rs'
SHARED = 'library/core/src/slice/sort/shared/mod.rs'
MODEL = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs'
SMOKE = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_smoke.rs'
CONTROLS = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_controls.rs'
NS = 'core::slice::sort::shared::smallsort::'
TYPE_PATHS = {'u8': 'u8', 'Cell<u8>': 'core::cell::Cell<u8>',
              'NonCopyByte': NS + 'verify::sorting_model::NonCopyByte'}
PRODUCER_SPECS = {
    'pfc_attribute': ('library/kani_macros/src/sysroot/contracts/mod.rs', 572, 587),
    'resolve_target': ('kani-compiler/src/kani_middle/resolve.rs', 58, 119),
    'manual_target_definition': ('kani-compiler/src/kani_middle/metadata.rs', 81, 95),
    'check_mode': ('kani-compiler/src/kani_middle/codegen_units.rs', 275, 292),
    'names': ('library/kani_macros/src/sysroot/contracts/initialize.rs', 72, 90),
    'attributes': ('library/kani_macros/src/sysroot/contracts/bootstrap.rs', 32, 105),
    'check_semantics': ('library/kani_macros/src/sysroot/contracts/check.rs', 23, 153),
    'producer_symbol': ('kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs', 19, 124),
    'enforce_contract': ('kani-driver/src/call_goto_instrument.rs', 177, 212),
    'property_id': ('kani-driver/src/cbmc_output_parser.rs', 132, 139),
    'property_location': ('kani-driver/src/cbmc_output_parser.rs', 280, 307),
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()


def read(path):
    return json.loads(path.read_bytes())


@functools.lru_cache(None)
def git_bytes(repo, revision, path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', revision + ':' + path])


def pinned_file(path):
    """Read an input from the task's committed g0, then compare working bytes."""
    rel = str(path.relative_to(G0))
    expected = git_bytes(G0, ENTRY, rel)
    need(path.read_bytes() == expected, 'task input changed: ' + rel)
    return expected


def norm(text):
    # Only whitespace is removed from clauses/target attributes.
    return re.sub(r'\s+', '', text)


def fullpath(text):
    # Stock pretty names omit the *local* core crate prefix. Keep every module,
    # type, generic argument and closure segment; no terminal/suffix matching.
    return re.sub(r'(?<![A-Za-z0-9_:])core::', '', text)


def one(values, reason):
    need(isinstance(values, list) and len(values) == 1, reason)
    return values[0]


def import_helper(name, path):
    pinned_file(path)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@functools.lru_cache(None)
def helpers():
    return (import_helper('s107_inventory', RUN / 'accept/replay.py'),
            import_helper('s107_native', RUN / 'accept/native.py'),
            import_helper('s107_source', RUN / 'accept/pfc.py'))


def apply_patch(base, patch):
    """Apply exact unified hunks in memory; never modify the source checkout."""
    lines, out, pos = base.splitlines(keepends=True), [], 0
    diff = patch.splitlines(keepends=True)
    need(diff[:2] == ['--- a/' + SMALL + '\n', '+++ b/' + SMALL + '\n'], 'patch file scope')
    i = 2
    while i < len(diff):
        m = re.fullmatch(r'@@ -(\d+),(\d+) \+(\d+),(\d+) @@\n', diff[i])
        need(m is not None, 'patch hunk header')
        old_start, old_count, new_start, new_count = map(int, m.groups())
        need(old_start - 1 >= pos, 'patch hunk order')
        out.extend(lines[pos:old_start - 1])
        need(len(out) == new_start - 1, 'patch new coordinate')
        pos = old_start - 1
        old_n = new_n = 0
        i += 1
        while i < len(diff) and not diff[i].startswith('@@'):
            l = diff[i]
            need(l[0] in ' +-', 'patch hunk line')
            if l[0] in ' -':
                need(pos < len(lines) and lines[pos] == l[1:], 'patch exact old context')
                pos += 1
                old_n += 1
            if l[0] in ' +':
                out.append(l[1:])
                new_n += 1
            i += 1
        need((old_n, new_n) == (old_count, new_count), 'patch hunk lengths')
    out.extend(lines[pos:])
    return ''.join(out)


def demangle(symbols):
    binary = Path(shutil.which('c++filt')).resolve()
    args = [str(binary), '-i', '-s', 'rust']
    unique = sorted(set(symbols))
    decoded = subprocess.check_output(args, input='\n'.join(unique) + '\n', text=True).splitlines()
    need(len(decoded) == len(unique) and all(a != b for a, b in zip(unique, decoded)), 'Rust demangling')
    return dict(zip(unique, decoded)), {
        'path': str(binary), 'sha256': digest(binary.read_bytes()),
        'version': subprocess.check_output([str(binary), '--version'], text=True).splitlines()[0],
        'arguments': ['-i', '-s', 'rust'],
    }


def load_bundle():
    """Hash-check inputs, but never open retained archives or full raw logs."""
    request_raw = pinned_file(RUN / 'CI-REQUEST.json')
    need(digest(request_raw) == REQUEST_SHA, 'exact request SHA')
    need(request_raw == git_bytes(CONTROL, CONTROL_SHA, 'ch8-s1-control/CI-REQUEST.json'), 'control request')
    request = json.loads(request_raw)
    collected = json.loads(pinned_file(RUN / 'collected.json'))
    inputs = {'CI-REQUEST.json': digest(request_raw), 'collected.json': digest(pinned_file(RUN / 'collected.json'))}
    # Historical analysis is an input for comparison/navigation, never a verdict.
    for rel in ['accept/ACCEPT.json', 'accept/pfc.py', 'accept/native.py', 'accept/replay.py', 'PROVENANCE.json']:
        inputs[rel] = digest(pinned_file(RUN / rel))
    groups = {}
    for group in request['execution_groups']:
        if not any(r['id'] in group['row_ids'] and r['mode'] == 'PFC' for r in request['rows']):
            continue
        gid = group['id']
        groups[gid] = {}
        for fn in ['properties.json', 'export.json', 'binding-metadata.json', 'receipt.json', 'compile/receipt.json']:
            rel = 'evidence/' + gid + '/' + fn
            raw = pinned_file(RUN / rel)
            inputs[rel] = digest(raw)
            groups[gid][fn] = json.loads(raw)
    sources = {p: git_bytes(STD, SOURCE, p).decode() for p in set(request['changed_file_sha256']) | {
        SHARED, 'library/core/src/cell.rs', 'library/core/src/marker.rs'}}
    patches = {v: git_bytes(CONTROL, CONTROL_SHA, 'ch8-s1-control/' + s['patch']).decode()
               for v, s in request['variants'].items()}
    producer = {}
    for role, (path, start, end) in PRODUCER_SPECS.items():
        raw = git_bytes(CONTROL, TOOL, path)
        need(raw == git_bytes(CONTROL, CONTROL_SHA, path), 'producer source drift: ' + path)
        producer[role] = {'commit': TOOL, 'path': path, 'sha256': digest(raw), 'start_line': start,
                          'end_line': end, 'lines': raw.decode().splitlines()[start-1:end]}
    symbols = [h['contract']['contracted_function_name'] for g in groups.values()
               for h in g['export.json']['harnesses'] if isinstance(h.get('attributes', {}).get('kind'), dict)
               and 'ProofForContract' in h['attributes']['kind']]
    dictionary, identity = demangle(symbols)
    provenance = json.loads(pinned_file(RUN / 'PROVENANCE.json'))
    return dict(request=request, collected=collected, groups=groups, sources=sources, patches=patches, provenance=provenance,
                producer=producer, dictionary=dictionary, demangler=identity, inputs=inputs)


def source_identity(b):
    req = b['request']
    need((req['std_sha'], req['tool_sha']) == (SOURCE, TOOL), 'source/tool pins')
    for repo, sha, field in [(STD, SOURCE, 'std_tree'), (CONTROL, TOOL, 'tool_tree')]:
        need(subprocess.check_output(['git', '-C', str(repo), 'rev-parse', sha + '^{tree}'], text=True).strip() == req[field], 'pinned tree identity: ' + field)
    for path, sha in req['changed_file_sha256'].items():
        need(digest(b['sources'][path].encode()) == sha, 'source SHA: ' + path)
    # These type-system dependencies are outside the request's changed-file set.
    for path in [SHARED, 'library/core/src/cell.rs', 'library/core/src/marker.rs']:
        need(b['sources'][path].encode() == git_bytes(STD, SOURCE, path), 'type dependency SHA: ' + path)
    for role, (path, start, end) in PRODUCER_SPECS.items():
        raw = git_bytes(CONTROL, TOOL, path)
        anchor = b['producer'][role]
        need(anchor == dict(commit=TOOL, path=path, sha256=digest(raw), start_line=start,
                            end_line=end, lines=raw.decode().splitlines()[start-1:end]), 'producer edge: ' + role)


def effective_source(b, variant):
    req, base = b['request'], b['sources'][SMALL]
    if variant == 'production':
        return base, None
    need(variant in req['variants'], 'unknown variant')
    spec, patch = req['variants'][variant], b['patches'][variant]
    need(digest(patch.encode()) == spec['sha256'], 'variant patch SHA')
    result = apply_patch(base, patch)
    need(digest(result.encode()) == spec['changed_file_sha256'][SMALL], 'effective variant source SHA')
    need(spec['marker'] in patch, 'variant marker')
    return result, {'path': 'git:' + CONTROL_SHA + ':ch8-s1-control/' + spec['patch'],
                    'sha256': spec['sha256'], 'marker': spec['marker']}


def group_identity(b, group):
    req, gid = b['request'], group['id']
    g = b['groups'][gid]
    m, rec, exp = [g[x] for x in ['binding-metadata.json', 'receipt.json', 'export.json']]
    need(m['group_id'] == rec['group'] == gid and m['variant'] == rec['variant'] == group['variant'], 'group/variant identity')
    need(m['request_sha256'] == rec['request_sha256'] == REQUEST_SHA, 'group request identity')
    need(m['std_sha'] == rec['std_sha'] == SOURCE and m['tool_sha'] == rec['tool_sha'] == TOOL, 'group source/tool')
    need(m['state'] == 'CAPTURED_AVAILABLE_FIELDS' and m['native_metadata_state'] == 'CAPTURED'
         and m['errors'] == [], 'metadata capture state')
    need(m['invocation_id'] == rec['invocation_id'] and re.fullmatch('[0-9a-f]{32}', m['invocation_id']), 'invocation identity')
    need(m['expected_flags_and_checks'] == req['flags'], 'flags identity')
    need(m['effective_cfg'] == rec['effective_cfg'] == '--cfg=kani_smallsort_sorting --cfg=kani_smallsort_controls', 'effective cfg')
    selected = [one([r for r in req['rows'] if r['id'] == rid], 'group row')['selector'] for rid in group['row_ids']]
    argv = [PREFIX.replace('/export/', '/tool/') + 'scripts/kani', 'verify-std']
    for feature in req['flags']['unstable']:
        if feature != 'export-json':
            argv += ['-Z', feature]
    argv += ['--no-assert-contracts', '--jobs=1', '--harness-timeout', '600s']
    for selector in selected:
        argv += ['--harness', selector]
    argv += ['--exact', '--default-unwind', str(group['unwind']), '-Z', 'export-json', '--export-json',
             '/home/runner/work/_temp/ch8-s1-receipts/groups/' + gid + '/export.json',
             '--output-format=regular', PREFIX + 'library', '--cbmc-args', '--object-bits', '12']
    need(m['argv'] == rec['argv'] == argv and m['unwind'] == rec['unwind'] == group['unwind'] == 34, 'argv/unwind identity')
    need(m['configuration_sha256'] == digest(json.dumps({'flags': req['flags'], 'cfg': m['effective_cfg'],
                                                       'argv': m['argv']}, sort_keys=True).encode()), 'configuration SHA')
    need(exp['kani_commit'] == TOOL and exp['kani_commit_dirty'] is False, 'export tool identity')
    need(m['execution'] == rec['execution'] and rec['execution']['child_shutdown_verified'] is True
         and all(rec['execution'][k] is False for k in ['timed_out', 'output_truncated', 'stdout_truncated', 'stderr_truncated'])
         and rec['execution']['signal'] is None and rec['phase_limited'] is False
         and not rec.get('execution_exception') and not rec.get('original_exception')
         and not m['execution_exception'] and not m['original_exception'], 'complete execution')
    need(rec['execution']['original_exit_code'] == (1 if any(r['expected'] == 'DETECTED' for r in req['rows']
         if r['id'] in group['row_ids']) else 0), 'original group exit')
    need(m['source_before'] == m['source_after'] == rec['source_before'] == rec['source_after'], 'source snapshots')
    need(m['source_before']['std_sha'] == SOURCE and m['source_before']['tool_sha'] == TOOL
         and m['source_before']['changed_file_sha256'] == req['changed_file_sha256'], 'base source snapshot')
    need(m['source_before'] == {k: req[k] for k in ['std_sha', 'std_tree', 'tool_sha', 'tool_tree', 'changed_file_sha256']}, 'exact source/tool snapshot')
    effective, patch = effective_source(b, group['variant'])
    expected_hashes = dict(req['changed_file_sha256'])
    expected_hashes[SMALL] = digest(effective.encode())
    need(m['source_under_test'] == rec['source_under_test'] == {
        'base_std_sha': SOURCE, 'variant': group['variant'], 'file_sha256': expected_hashes,
        'patch_sha256': patch['sha256'] if patch else None}, 'effective source receipt')
    old, _, _ = helpers()
    need(old.snapshot_gate(rec) == 'MATCH' and m['binaries_before'] == rec['tool_fingerprints_before']
         and m['binaries_after'] == rec['tool_fingerprints_after'], 'same-run binary snapshots')
    comp = g['compile/receipt.json']
    need(comp['state'] == 'COMPLETE' and comp['boundary'] == 'STOCK_INITIAL_EXPORT_OBSERVED'
         and comp['std_sha'] == SOURCE and comp['tool_sha'] == TOOL and comp['request_sha256'] == REQUEST_SHA
         and comp['selectors'] == rec['selectors'] == selected, 'compile observation namespace')
    need(exp['harness_selection'] == {'requested_filters': selected, 'exact': True, 'unmatched_filters': [], 'matched_count': len(selected)}, 'exact export selection')
    need(exp['run_state'] == 'COMPLETE' and exp['outcome'] == {'kind': 'COMPLETED'} and exp['harness_timeout_s'] == 600
         and exp['target'] == 'x86_64-unknown-linux-gnu', 'complete export')
    need(exp['configuration']['checks'] == {'memory_safety': True, 'overflow': True, 'unwinding': True,
         'undefined_function': True, 'assertion_reach_checks': True, 'ignore_global_asm': False,
         'extra_pointer_checks': False, 'assert_contracts': False, 'prove_safety_only': False}
         and exp['configuration']['cbmc_args'] == ['--object-bits', '12']
         and exp['configuration']['coverage_enabled'] is False, 'export checks configuration')
    need(set(exp['enabled_unstable_features']) == set(req['flags']['unstable']), 'export feature identity')
    need(len(exp['harnesses']) == len(selected) and len(g['properties.json']['harnesses']) == len(selected)
         and {h['name'] for h in exp['harnesses']} == {h['name'] for h in g['properties.json']['harnesses']} == set(selected)
         and g['properties.json']['error'] is None, 'complete exact group harness inventories')
    need(len(m['rows']) == len(group['row_ids']) and {r['row_id'] for r in m['rows']} == set(group['row_ids']), 'metadata row inventory')
    # Compile/receipt is a reserialized intake projection: its original member
    # digest differs. Preserve the original->projection distinction explicitly.
    prov = one([p for p in b['provenance'] if p['artifact'] == 'ch8-s1-05-43923266772-1-' + gid], 'provenance group')
    for rel, sha in prov['projections'].items():
        need(b['inputs'][rel] == sha, 'retained projection digest')
    for a in m['artifacts']:
        need({k: a[k] for k in ['bytes', 'sha256']} == prov['entries']['groups/' + gid + '/' + a['path']], 'metadata original artifact digest')
        if a['path'] in ['export.json', 'properties.json']:
            need(a['sha256'] == b['inputs']['evidence/' + gid + '/' + a['path']], 'original exact export/property bytes')
    return effective, patch


def source_target(b, row, source, h):
    """Bounded macro substitution for the two pinned macros and two direct roots."""
    _, _, old = helpers()
    text = b['sources'][source['file']]
    lines = text.splitlines()
    need(digest(text.encode()) == source['sha256'], 'harness source SHA')
    need(source['mode'] == row['mode'] == 'PFC' and source['selector'] == row['selector']
         and source['crate'] == h['crate_name'] == 'core', 'source harness/crate/mode')
    need(h['file'] == source['file'], 'export source file')
    for loc in source['locations']:
        need(lines[loc['line']-1] == loc['source'], 'harness source site')
    selector_name = row['selector'].split('::')[-1]
    invocation = source['locations'][0]
    match = re.match(r'(smoke(?:_exact_n)?)!\(', invocation['source'])
    if match:
        macro = match[1]
        chunk = '\n'.join(lines[invocation['line']-1:])
        end = chunk.index(');')
        args = old._split_args(chunk[len(macro)+2:end])
        need(args[0] == selector_name and len(args) == (7 if macro == 'smoke_exact_n' else 6), 'macro invocation arguments')
        ty, trait = args[1], args[3]
        expected = '<' + ty + ' as ' + trait + '>::small_sort'
        start = next(i for i, l in enumerate(lines) if l == 'macro_rules! ' + macro + ' {')
        variable = '$type' if macro == 'smoke_exact_n' else '$ty'
        attr_line = start + (4 if macro == 'smoke_exact_n' else 3)
        need(lines[attr_line-1].strip() == '#[kani::proof_for_contract(<' + variable + ' as $trait>::small_sort)]', 'macro PFC attribute')
        need(lines[int(h['line'])-1].strip() == 'fn $name() {' and int(h['line']) == start + (6 if macro == 'smoke_exact_n' else 5), 'macro definition export site')
        # Verify call substitution, comparator and chosen route, not just the attr.
        template = '\n'.join(lines[start:invocation['line']-1])
        need('let mut less = KeyLess::<' + variable + '>::new();' in template
             and 'invoke!($route, ' + variable + ', $trait,' in template, 'macro actual call/comparator')
        route = args[5]
        need(route == ('stable_empty' if trait == 'StableSmallSortTypeImpl' and ty == 'Cell<u8>'
                       else 'stable_general' if trait == 'StableSmallSortTypeImpl' else 'unstable'), 'macro route')
        need('<$ty as $trait>::small_sort($v, &mut scratch, $less);' in text
             and '<$ty as $trait>::small_sort($v, &mut scratch[..scratch_len], $less);' in text
             and '<$ty as $trait>::small_sort($v, $less)' in text, 'invoke target call')
        need(int(args[4]) == (16 if ty == 'Cell<u8>' else 32), 'macro specialization threshold')
        if 'type' in row:
            need(row['type'] == ty, 'request type')
        if isinstance(row.get('N'), int):
            need(macro == 'smoke_exact_n' and int(args[6]) == row['N'], 'exact N substitution')
        return ty, trait, expected, {'macro': macro, 'arguments': args, 'invocation': invocation,
                                    'attribute_line': attr_line, 'call_route': route}
    need(invocation['source'] == 'fn ' + selector_name + '() {' and h['line'] == invocation['line'], 'direct harness site')
    attr = lines[invocation['line']-3].strip()
    m = re.fullmatch(r'#\[kani::proof_for_contract\((<(.+) as (\w+)>::small_sort)\)\]', attr)
    need(m is not None, 'direct PFC attr')
    target, ty, trait = m.groups()
    body = '\n'.join(lines[invocation['line']-1:]).split('\n}', 1)[0]
    need(target + '(' in body and 'KeyLess::<' + ty + '>::new()' in body, 'direct actual call/comparator')
    return ty, trait, target, {'macro': None, 'invocation': invocation, 'attribute_line': invocation['line']-2}


def selected_impl(b, ty, trait, effective):
    need(ty in TYPE_PATHS and trait in {'StableSmallSortTypeImpl', 'UnstableSmallSortTypeImpl',
                                      'UnstableSmallSortFreezeTypeImpl'}, 'supported type/trait specialization')
    # Type facts from pinned source, interpreted under the stock compiler trust.
    need('impl<T: Freeze> FreezeMarker for T {}' in b['sources'][SHARED], 'FreezeMarker blanket impl')
    need('value: UnsafeCell<T>,' in b['sources']['library/core/src/cell.rs']
         and 'impl<T: PointeeSized> !Freeze for UnsafeCell<T> {}' in b['sources']['library/core/src/marker.rs'], 'Cell non-Freeze fact')
    need('struct NonCopyByte(u8);' in b['sources'][MODEL]
         and not re.search(r'(?:impl[^\n]*Copy[^\n]*NonCopyByte|derive\([^)]*Copy[^)]*\)[\s\S]{0,80}struct NonCopyByte)', b['sources'][MODEL]), 'NonCopyByte non-Copy fact')
    need('Copy for\n        usize, u8,' in b['sources']['library/core/src/marker.rs'], 'u8 Copy fact')
    bounds = '' if ty == 'Cell<u8>' else ': FreezeMarker'
    if trait == 'UnstableSmallSortFreezeTypeImpl':
        need(ty != 'Cell<u8>', 'Freeze trait applicability')
        bounds = ': FreezeMarker + CopyMarker' if ty == 'u8' else ': FreezeMarker'
    header = 'impl<T' + bounds + '> ' + trait + ' for T {'
    need('impl<T: Copy> CopyMarker for T {}' in effective, 'CopyMarker blanket impl')
    lines = effective.splitlines()
    need(lines.count(header) == 1, 'unique applicable impl header')
    start = lines.index(header)
    end = next((i for i in range(start+1, len(lines)) if lines[i] == '}'), None)
    need(end is not None, 'impl body extent')
    body = lines[start:end+1]
    attrs = []
    for i, l in enumerate(body, start+1):
        m = re.fullmatch(r'\s*#\[cfg_attr\(all\(kani, kani_smallsort_sorting\), kani::(requires|modifies|ensures)\((.*)\)\)\]', l)
        if m:
            attrs.append({'kind': m[1], 'expression': m[2], 'line': i, 'source': l})
    need([a['kind'] for a in attrs] == (['requires', 'requires', 'modifies', 'ensures']
         if trait == 'StableSmallSortTypeImpl' and ty != 'Cell<u8>' else ['requires', 'modifies', 'ensures']), 'selected impl contract clauses')
    method = one([{'line': start+i+1, 'source': l} for i, l in enumerate(body) if re.search(r'fn small_sort<F', l)], 'selected impl method')
    threshold = 16 if ty == 'Cell<u8>' else 32
    return {'header': header, 'line': start+1, 'end_line': end+1, 'method': method,
            'attributes': attrs, 'threshold': threshold,
            'facts': {'Freeze': ty != 'Cell<u8>', 'Copy': ty == 'u8',
                      'selection': 'more-specific applicable bound wins; default otherwise'} }


def type_semantics(b):
    specs = [(SHARED, 3, 13), ('library/core/src/marker.rs', 473, 480),
             ('library/core/src/marker.rs', 905, 919), ('library/core/src/cell.rs', 311, 317),
             (MODEL, 13, 27), (MODEL, 47, 64), (MODEL, 139, 154),
             (SMALL, 153, 160), (SMALL, 195, 218)]
    return [{'path': path, 'commit': SOURCE, 'sha256': digest(b['sources'][path].encode()),
             'start_line': start, 'end_line': end, 'lines': b['sources'][path].splitlines()[start-1:end]}
            for path, start, end in specs]


def native_link(meta, row, h, trait, source):
    _, native, _ = helpers()
    mr = one([x for x in meta['rows'] if x['row_id'] == row['id']], 'native row uniqueness')
    need((mr['harness'], mr['crate'], mr['mode'], mr['variant'], mr['group_id']) ==
         (row['selector'], 'core', 'PFC', row['variant'], meta['group_id']), 'native row identity')
    ref = one(mr['native_harness_records'], 'native ref uniqueness')
    need(ref['name'] == row['selector'] and ref['crate'] == 'core'
         and re.fullmatch(r'/proof_harnesses/(0|[1-9][0-9]*)', ref['pointer']), 'native ref identity')
    entry = one([e for e in meta['native_metadata'] if e['path'] == ref['metadata_path']], 'native file reference')
    records, checks = native._records(entry)
    need(entry['state'] == 'CAPTURED' and checks['sha256_valid'] and checks['bytes_valid']
         and checks['json_valid'], 'native embedded content integrity')
    doc = json.loads(entry['text'])
    record = native._pointer(doc, ref['pointer'])
    need(isinstance(record, dict) and record['pretty_name'] == h['name'] == row['selector']
         and record['crate_name'] == h['crate_name'] == doc['crate_name'] == 'core', 'native exact harness')
    need(record['attributes'] == h['attributes'] and record['contract'] == h['contract'], 'native/export attrs and raw symbol')
    need(record['original_file'] == PREFIX + source['file'] and record['original_start_line'] == h['line'], 'native/export source site')
    need(record['has_loop_contracts'] is h['has_loop_contracts'] is False
         and record['is_automatically_generated'] is h['is_automatically_generated'] is False, 'manual PFC/no loop contract')
    target_def = one([d for d in doc['contracted_functions'] if row['selector'] in d['harnesses']], 'manual target-definition link')
    need(target_def['function'] == '<T as ' + fullpath(NS) + trait + '>::small_sort'
         and target_def['file'] == PREFIX + SMALL
         and target_def['harnesses'].count(row['selector']) == 1, 'native target definition type/trait/file')
    return {'metadata_path': ref['metadata_path'], 'sha256': entry['sha256'], 'pointer': ref['pointer'],
            'target_definition': target_def, 'source_start_line': record['original_start_line'],
            'source_end_line': record['original_end_line']}


def stem(p):
    parts = p['id'].rsplit('.', 2)
    need(len(parts) == 3 and parts[1] == p['class'], 'property ID class')
    return parts[0]


def property_site(p, function, line):
    need(p['file'] == PREFIX + SMALL and str(p['line']) == str(line), 'contract property source site')
    m = re.fullmatch(re.escape(SMALL) + r':' + str(line) + r':\d+ in function (.+)', p['location_display'])
    need(m is not None and fullpath(m[1]) == fullpath(function)
         and fullpath(stem(p)) == fullpath(function), 'property full function/location stem')


def contract_properties(b, row, h, props, impl, ty, trait):
    raw = h['contract']['contracted_function_name']
    need(h['contract']['recursion_tracker'] is None, 'nonrecursive contract mode')
    need(raw in b['dictionary'], 'raw symbol dictionary')
    decoded = b['dictionary'][raw]
    # The producer, not a closure index, assigns the modifies role. Compare the
    # entire decoded target instance then split only its structurally nested closures.
    m = re.fullmatch(r'(.+)(::\{closure#\d+\})(::\{closure#\d+\})', decoded)
    need(m is not None, 'nested modifies wrapper structure')
    target_instance, check = m[1], m[1] + m[2]
    full_ty = TYPE_PATHS[ty]
    expected_instance = '<' + full_ty + ' as ' + NS + trait + '>::small_sort::<' + NS + 'verify::sorting_model::KeyLess<' + full_ty + '>>'
    need(target_instance == expected_instance, 'decoded full target type/trait/comparator instance')
    modifies = one([a for a in impl['attributes'] if a['kind'] == 'modifies'], 'one modifies clause')
    diagnostics = []
    for cls, lead in [('single_top_level_call', 'Only a single top-level call'), ('no_recursive_call', 'No recursive call')]:
        p = one([p for p in props if p['class'] == cls], 'one exact diagnostic: ' + cls)
        need(p['status'] == 'SUCCESS' and p['description'] == lead + ' to function ' + raw + ' when checking contract ' + raw
             and p['description'].count(raw) == 2, 'diagnostic raw symbol/status: ' + cls)
        property_site(p, decoded, modifies['line'])
        diagnostics.append(p)
    ensures = []
    for a in impl['attributes']:
        if a['kind'] != 'ensures':
            continue
        p = one([p for p in props if p['class'] == 'assertion' and fullpath(stem(p)) == fullpath(check)
                 and str(p['line']) == str(a['line']) and norm(p['description']) == norm(a['expression'])], 'exact check ensures clause/site')
        property_site(p, check, a['line'])
        need(p['status'] == ('FAILURE' if row['expected'] == 'DETECTED' else 'SUCCESS'), 'ensures clause status')
        ensures.append({'source_clause': a, 'property': p})
    parent_asserts = [p for p in props if p['class'] == 'assertion' and fullpath(stem(p)) == fullpath(check)
                     and p['file'] == PREFIX + SMALL and str(p['line']) in {str(a['line']) for a in impl['attributes'] if a['kind'] == 'ensures'}]
    need(len(parent_asserts) == len(ensures), 'duplicate/unbound ensures at clause site')
    allocation_checks = []
    for cls in ['no_alloc_dealloc_in_requires', 'no_alloc_dealloc_in_ensures']:
        p = one([p for p in props if p['class'] == cls], 'clause allocation diagnostic')
        need(p['status'] == 'SUCCESS', 'clause allocation status')
        property_site(p, decoded, modifies['line'])
        allocation_checks.append(p)
    frame = [p for p in props if p['class'] in {'assigns', 'frees'}]
    need(frame and all(p['status'] == 'SUCCESS' for p in frame), 'enforced frame statuses')
    return {'raw_symbol': raw, 'decoded_modifies_wrapper': decoded, 'check_wrapper': check,
            'target_instance': target_instance, 'diagnostics': diagnostics, 'ensures': ensures,
            'requires': [{'source_clause': a, 'semantics': 'ASSUMED_BY_PFC_CHECK; NOT_ASSERTED',
                          'assertion_ids': []} for a in impl['attributes'] if a['kind'] == 'requires'],
            'modifies': {'source_clause': modifies, 'semantics': 'ENFORCED_BY_SOLE_DFCC_CONTRACT',
                         'write_site_properties': frame}, 'clause_allocation_checks': allocation_checks}


def oracle(row, h, props, contract, effective, patch):
    failures = [p for p in props if p['status'] == 'FAILURE']
    if row['expected'] == 'SUCCESS':
        need(row['variant'] == 'production' and not failures and h['outcome']['verdict'] == 'SUCCESS', 'positive oracle')
        return None
    need(row['expected'] == 'DETECTED' and patch is not None, 'activation variant expected detection')
    o = row['oracle']
    p = one(failures, 'activation sole failure')
    need(o['selector'] == row['selector'] and o['require_only_this_failure'] is True
         and o['status'] == p['status'] == 'FAILURE', 'predeclared oracle selector/status')
    need(p == contract['ensures'][0]['property'] and p['id'] == o['property_id']
         and p['class'] == o['class'] == 'assertion' and p['description'] == o['description']
         and p['file'] == o['export_file'] == PREFIX + o['file']
         and str(p['line']) == str(o['line']), 'predeclared exact sole-failure oracle')
    need(digest(effective.encode()) == o['source_sha256'] and effective.splitlines()[o['line']-1] == o['source_line'], 'oracle effective source')
    need(row['failure_description'] == patch['marker'] and patch['marker'] in p['description'], 'oracle variant marker')
    return {'status': 'EXACT_PREDECLARED_SOLE_FAILURE', 'id': p['id'], 'source_sha256': o['source_sha256'],
            'patch': patch, 'companion': row['companion']}


def analyze_row(b, row, group):
    req, gid = b['request'], group['id']
    need(row['id'] in group['row_ids'] and row['variant'] == group['variant'], 'row/group/variant')
    effective, patch = group_identity(b, group)
    g = b['groups'][gid]
    h = one([h for h in g['export.json']['harnesses'] if h['name'] == row['selector']], 'export exact harness')
    rich = one([h for h in g['properties.json']['harnesses'] if h['name'] == row['selector']], 'rich exact harness')
    props = rich['properties']
    old, _, _ = helpers()
    old.inventory(h, props)
    source = req['source_bindings'][row['id']]
    need(g['binding-metadata.json']['source_bindings'][row['id']] == source, 'metadata/request source binding')
    ty, trait, target, macro = source_target(b, row, source, h)
    attr = h['attributes']
    need(isinstance(attr['kind'], dict) and set(attr['kind']) == {'ProofForContract'}
         and norm(attr['kind']['ProofForContract']['target_fn']) == norm(source['target']) == norm(target), 'PFC source/export target')
    if 'target' in row:
        need(norm(row['target']) == norm(target), 'request row target')
    need(attr['stubs'] == attr['verified_stubs'] == [] and attr['should_panic'] is False
         and h['resolved_unwind'] == group['unwind'] and h['warnings'] == [] and h['warnings_truncated'] == 0, 'PFC attributes/unwind')
    impl = selected_impl(b, ty, trait, effective)
    if 'threshold' in row:
        need(row['threshold'] == impl['threshold'], 'specialization threshold')
    native = native_link(g['binding-metadata.json'], row, h, trait, source)
    contract = contract_properties(b, row, h, props, impl, ty, trait)
    result_oracle = oracle(row, h, props, contract, effective, patch)
    collected = one([r for r in b['collected']['rows'] if r['id'] == row['id']], 'collected row')
    need(collected['selector'] == row['selector'] and collected['variant'] == row['variant']
         and collected['group'] == gid, 'collected row group/harness')
    need(collected['export']['harness'] == h and collected['export']['source_binding'] == source
         and collected['evidence']['invocation_id'] == g['binding-metadata.json']['invocation_id'], 'collected export/source/invocation')
    need(collected['evidence']['native_harness_records'] == one([r for r in g['binding-metadata.json']['rows'] if r['row_id'] == row['id']], 'metadata row')['native_harness_records'], 'collected native references')
    return {'id': row['id'], 'status': 'SOURCE_REPORTED_BOUND', 'group': gid, 'harness': row['selector'],
            'crate': 'core', 'variant': row['variant'], 'type': ty, 'trait': trait, 'target_attribute': target,
            'source': {'file': source['file'], 'sha256': source['sha256'], 'macro': macro,
                       'effective_target_file': SMALL, 'effective_target_sha256': digest(effective.encode()), 'patch': patch},
            'selected_impl': impl, 'native': native, 'contract': contract, 'negative_oracle': result_oracle,
            'property_count': len(props), 'configuration_sha256': g['binding-metadata.json']['configuration_sha256'],
            'invocation_id': g['binding-metadata.json']['invocation_id'], 'gaps': []}


def analyze(b):
    source_identity(b)
    req = b['request']
    rows = [r for r in req['rows'] if r['mode'] == 'PFC']
    need(len(rows) == len({r['id'] for r in rows}) == 22, 'exact 22 PFC row inventory')
    bindings = []
    for row in sorted(rows, key=lambda r: r['id']):
        try:
            group = one([g for g in req['execution_groups'] if row['id'] in g['row_ids']], 'unique request group')
            bindings.append(analyze_row(b, row, group))
        except (ValueError, KeyError, TypeError, IndexError, AttributeError) as exc:
            bindings.append({'id': row['id'], 'status': 'PENDING', 'gaps': [str(exc)]})
    by = {r['id']: r for r in bindings}
    for row in rows:
        if row['expected'] != 'DETECTED' or by[row['id']]['status'] == 'PENDING':
            continue
        companion = by.get(row['companion'], {})
        try:
            need(companion.get('status') == 'SOURCE_REPORTED_BOUND' and companion['variant'] == 'production'
                 and companion['harness'] == row['selector']
                 and companion['contract']['target_instance'] == by[row['id']]['contract']['target_instance'], 'legal companion same target instance')
            need(all(e['property']['status'] == 'SUCCESS' for e in companion['contract']['ensures']), 'legal companion ensures')
            by[row['id']]['negative_oracle']['legal_companion_binding'] = row['companion']
        except (ValueError, KeyError) as exc:
            by[row['id']] = {'id': row['id'], 'status': 'PENDING', 'gaps': [str(exc)]}
    return {
        'schema': 's1-07-pfc-component-profiles-v4-v1', 'task_commit': ENTRY, 'run': '43923266772',
        'request_sha256': REQUEST_SHA, 'source_sha': SOURCE, 'tool_sha': TOOL, 'control_sha': CONTROL_SHA,
        'assurance': 'BOUNDED_SOURCE_REPORTED_PROFILES_V4_TRUST_PINNED_STOCK_COMPILER',
        'independent_proof_credit': 'NONE', 'B1_credit': 'NONE', 'B2_credit': 'NONE',
        'component_only': True, 'admission_root_recomputed': False,
        'normalization': {'clauses': 'whitespace only', 'paths': 'local core:: prefix only; full path and generic equality',
                          'roles': 'producer checked_with -> modifies_wrapper; no closure ordinal role assignment'},
        'demangler': b['demangler'], 'demangling_dictionary': b['dictionary'],
        'input_sha256': b['inputs'], 'source_file_sha256': {p: digest(s.encode()) for p, s in sorted(b['sources'].items())},
        'type_specialization_semantics': type_semantics(b),
        'producer_semantics': b['producer'],
        'bindings': [by[r['id']] for r in sorted(rows, key=lambda r: r['id'])],
        'totals': {'chains': len(rows), 'bound': sum(r['status'] == 'SOURCE_REPORTED_BOUND' for r in by.values()),
                   'pending': sum(r['status'] == 'PENDING' for r in by.values())},
        'limits': ['No independent AST/MIR/DefId/instance provenance trace or compiler correctness proof.',
                   'Native invocation ID is a runner directory identity; compilation_id remains null.',
                   'PFC requires are assumed, ensures asserted, modifies enforced; diagnostic pair is not all clauses.',
                   'Write properties are write sites under the sole enforced contract, not independent owner traces.',
                   'This component changes no overall qualified count, U/role/cover gates or historical receipt.',
                   'S1 smoke fixture N0..3 and fixed geometry; no full threshold/general sorting theorem.'],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true', help='write only accept-pfc/PFC.json')
    args = parser.parse_args()
    result = analyze(load_bundle())
    need(result['totals'] == {'chains': 22, 'bound': 22, 'pending': 0},
         'unclosed PFC edges: ' + json.dumps([r for r in result['bindings'] if r['status'] == 'PENDING']))
    data = encoded(result)
    if args.write:
        (HERE / 'PFC.json').write_bytes(data)
    else:
        need((HERE / 'PFC.json').read_bytes() == data, 'PFC.json replay differs')
    print(json.dumps({'totals': result['totals'], 'sha256': digest(data), 'replay': 'MATCH' if not args.write else 'WRITTEN'}))


if __name__ == '__main__':
    main()
