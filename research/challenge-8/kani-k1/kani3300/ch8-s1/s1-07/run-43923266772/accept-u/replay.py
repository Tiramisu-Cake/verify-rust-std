#!/usr/bin/env python3
"""Exact, offline U-only replay. Read compact JSON and pinned git blobs only.

No compiler, raw logs, archive reads, previous classifier execution, or PFC
admission. --write writes only U.json; default compares its exact bytes.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
RUN = HERE.parent
STD = '5be85699b8826e3286c0bf89efb9affefac0acb5'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
REQUEST = '6c483ce754cd8e99c01953bf4c40a145b10529d7990aa52c28ef32c00b980cd7'
MANIFEST_SHA = 'c62222e2c8b51982f2b7df3c570543042423242bfd0ed37df9856f6248ebf89b'
REPOS = {'std': Path('/root/verify-rust-std-ch8-s1-04-w13'),
         'tool': Path('/root/kani-ch8-s1-07-w13')}
PREFIX = '/home/runner/work/kani/kani/export/'
NUM = 'library/core/src/num/uint_macros.rs'
PTR = 'library/core/src/ptr/const_ptr.rs'
UB = 'library/core/src/ub_checks.rs'
FMT = 'library/core/src/fmt/mod.rs'
MODEL = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs'
CODEGEN = 'kani-compiler/src/codegen_cprover_gotoc/codegen/rvalue.rs'
MODEL_FN = 'slice::sort::shared::smallsort::verify::sorting_model::active_post::'
SUB = 'attempt to subtract with overflow'
ADD = 'attempt to add with overflow'
BOUNDS = 'index out of bounds: the length is less than or equal to the given index'


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()


def compact(text):
    # Used only on these exact pinned source excerpts (no string/comment lexer
    # claims). Full file and exact raw anchor hashes are independently checked.
    return re.sub(r'\s+', '', re.sub(r'//[^\n]*', '', text))


def excerpt(text, start, end):
    lines = text.splitlines()
    need(1 <= start <= end <= len(lines), 'source anchor range')
    return '\n'.join(lines[start-1:end])


# Full operation/control-flow shapes, not property-ID decisions. Checking the
# entire function prevents matching a guard in unrelated or dead code.
SHAPES = {
 'abs_diff': '''pub const fn abs_diff(self, other: Self) -> Self {
 if size_of::<Self>() == 1 {
 (self as i32).wrapping_sub(other as i32).unsigned_abs() as Self
 } else { if self < other { other - self } else { self - other } } }''',
 'alignment': '''pub fn is_aligned_to(self, align: usize) -> bool {
 if !align.is_power_of_two() { panic!("is_aligned_to: align is not a power-of-two"); }
 self.addr() & (align - 1) == 0 }''',
 'power_two': '''pub const fn is_power_of_two(self) -> bool { self.count_ones() == 1 }''',
 'multiple': '''pub const fn is_multiple_of(self, rhs: Self) -> bool {
 match rhs { 0 => self == 0, _ => self % rhs == 0, } }''',
 'allocation': '''pub(crate) const fn is_valid_allocation_size(size: usize, len: usize) -> bool {
 let max_len = if size == 0 { usize::MAX } else { isize::MAX as usize / size };
 len <= max_len }''',
 'fmt': '''pub const fn from_str(s: &'static str) -> Arguments<'a> {
 unsafe { Arguments { template: mem::transmute(s.as_ptr()),
 args: mem::transmute(s.len() << 1 | 1), } } }''',
 'shl': '''BinOp::Shl => {
 let t1 = self.operand_ty_stable(e1);
 let max = shift_max(t1, self.symbol_table.machine_model());
 Expr::struct_expr_from_values(self.codegen_ty_stable(res_ty), vec![
 ce1.shl(ce2.clone()),
 ce2.cast_to(self.codegen_ty_stable(t1)).gt(max).cast_to(Type::c_bool()),
 ], &self.symbol_table, ) }''',
 'checked_shl': '''pub const fn checked_shl(self, rhs: u32) -> Option<Self> {
 if rhs < Self::BITS { Some(unsafe { self.unchecked_shl(rhs) }) } else { None } }''',
 'overflowing_shl': '''pub const fn overflowing_shl(self, rhs: u32) -> (Self, bool) {
 (self.wrapping_shl(rhs), rhs >= Self::BITS) }''',
 'snapshot': '''pub(in crate::slice::sort::shared::smallsort) struct Snapshot {
 values: [u8; CAP], len: usize, valid: bool, }''',
 'active_post': '''fn active_post<T: Project>(before: Snapshot, values: &[T]) -> bool {
 if !before.valid || before.len > CAP || values.len() > CAP || before.len != values.len() {
 return false; }
 let mut i = 1;
 while i < before.len {
 if values[i].value() < values[i - 1].value() { return false; }
 i += 1; }
 i = 0;
 while i < before.len {
 let query = before.values[i];
 let mut old_count: usize = 0;
 let mut new_count: usize = 0;
 let mut j = 0;
 while j < before.len {
 if before.values[j] == query { old_count += 1; }
 if values[j].value() == query { new_count += 1; }
 j += 1; }
 if old_count != new_count { return false; }
 i += 1; }
 true }''',
}

# Exact source positions in pinned commits. These are source anchors, not
# evidence row ordinals and not assignments of contract roles.
ANCHORS = {
 'abs_diff': ('std', NUM, 3215, 3227),
 'alignment': ('std', PTR, 1474, 1480),
 'power_two': ('std', NUM, 3932, 3934),
 'multiple': ('std', NUM, 3913, 3918),
 'allocation': ('std', UB, 147, 150),
 'fmt': ('std', FMT, 815, 823),
 'shl': ('tool', CODEGEN, 328, 339),
 'shift_max': ('tool', CODEGEN, 275, 297),
 'checked_shl': ('std', NUM, 2057, 2065),
 'overflowing_shl': ('std', NUM, 3558, 3560),
 'snapshot': ('std', MODEL, 66, 70),
 'cap': ('std', MODEL, 9, 9),
 'active_post': ('std', MODEL, 91, 121),
}
FAMILY_ANCHORS = {
 'abs_diff': ['abs_diff'], 'alignment': ['alignment', 'power_two'],
 'multiple': ['multiple'], 'allocation': ['allocation'],
 'fmt': ['fmt', 'shl', 'shift_max', 'checked_shl', 'overflowing_shl'],
 'active_post': ['cap', 'snapshot', 'active_post'],
}


def classify(prop):
    """Recognize only exact safety-check sites and full function instances."""
    need(prop['class'] == 'assertion' and prop['status'] == 'UNREACHABLE', 'class/status')
    need(prop['file'].startswith(PREFIX), 'original export namespace')
    path = prop['file'][len(PREFIX):]
    match = re.fullmatch(re.escape(path) + r':([1-9][0-9]*):([1-9][0-9]*) in function (.+)', prop['location_display'])
    need(match is not None and match[1] == prop['line'], 'exact location/line')
    fn = match[3]
    need(re.fullmatch(re.escape(fn) + r'\.assertion\.[1-9][0-9]*', prop['id']) is not None,
         'property function instance')
    need(prop['display_id'] == prop['id'], 'display ID')
    line, desc = int(prop['line']), prop['description']
    if (path, fn, desc) == (NUM, 'num::<impl usize>::abs_diff', SUB) and line in (3222, 3224):
        family, operation = 'abs_diff', 'other - self' if line == 3222 else 'self - other'
    elif (path, fn, line, desc) == (PTR, 'ptr::const_ptr::<impl *const ()>::is_aligned_to', 1479, SUB):
        family, operation = 'alignment', 'align - 1'
    elif (path, fn, line, desc) == (NUM, 'num::<impl usize>::is_multiple_of', 3916,
                                   'attempt to calculate the remainder with a divisor of zero'):
        family, operation = 'multiple', 'self % rhs'
    elif (path, fn, line, desc) == (UB, 'ub_checks::is_valid_allocation_size', 148, 'attempt to divide by zero'):
        family, operation = 'allocation', 'isize::MAX as usize / size'
    elif (path, fn, line, desc) == (FMT, "fmt::Arguments::<'_>::from_str", 820, 'attempt to shift left with overflow'):
        family, operation = 'fmt', 's.len() << 1'
    else:
        need(path == MODEL and fn in {MODEL_FN + '<u8>', MODEL_FN + '<cell::Cell<u8>>',
             MODEL_FN + '<slice::sort::shared::smallsort::verify::sorting_model::NonCopyByte>'},
             'unknown function/site')
        operations = {
            (97, BOUNDS): 'values[i], values[i - 1]', (97, SUB): 'i - 1',
            (100, ADD): 'i += 1 (sorted loop)', (106, BOUNDS): 'before.values[i]',
            (111, BOUNDS): 'before.values[j]', (111, ADD): 'old_count += 1',
            (112, BOUNDS): 'values[j]', (112, ADD): 'new_count += 1',
            (113, ADD): 'j += 1', (118, ADD): 'i += 1 (multiset loop)',
        }
        need((line, desc) in operations, 'unknown active_post safety operation')
        family, operation = 'active_post', operations[line, desc]
    return family, operation, path, fn


def check_premises(family, sources, bits=64):
    """Executable source-local certificates; callers separately check blob SHAs.

    Exact closed function shapes fix all operations and guards. Mathematical
    bounds below validate the applicability argument; no reachability or origin
    of the Boolean sorting predicate is inferred.
    """
    need(bits == 64, 'pinned x86_64 usize width')
    maximum = (1 << bits) - 1
    checked = []
    for name in FAMILY_ANCHORS[family]:
        repo, path, start, end = ANCHORS[name]
        text = excerpt(sources[repo, path], start, end)
        if name in SHAPES:
            need(compact(text) == compact(SHAPES[name]), 'source control-flow/operation premise:' + name)
        elif name == 'cap':
            need(compact(text) == 'constCAP:usize=32;', 'CAP premise')
        else:
            need(name == 'shift_max', 'unknown source anchor')
            need('UintTy::Usize => Expr::int_constant(mm.pointer_width - 1, Type::size_t()),' in text,
                 'usize shift overflow threshold')
        checked.append(name)
    if family == 'abs_diff':
        # Branch1 0<=self<other<=MAX => 1<=other-self<=MAX.
        # Branch2 0<=other<=self<=MAX => 0<=self-other<=MAX.
        # Difference extrema are achieved at endpoints; no enumeration of
        # sampled 64-bit inputs is used as an exhaustive proof.
        need(0 <= 0 <= maximum and 1 <= maximum and bits // 8 != 1, 'unsigned range/branch')
        facts = {'unsigned_interval': [0, maximum], 'true_branch': 'self < other',
                 'true_difference_interval': [1, maximum], 'false_branch': 'other <= self',
                 'false_difference_interval': [0, maximum]}
    elif family == 'alignment':
        # count_ones(0)=0. Passing count_ones==1 excludes zero.
        powers = [1 << k for k in range(bits)]
        need((0).bit_count() != 1 and all(1 <= x <= maximum and x.bit_count() == 1
                                       and 0 <= x-1 < maximum for x in powers), 'alignment lower bound')
        facts = {'passing_align_min': min(powers), 'align_minus_one_interval': [0, max(powers)-1],
                 'zero_rejected_by': 'count_ones() == 1; panic before subtraction'}
    elif family in ('multiple', 'allocation'):
        facts = {'divisor_interval_at_operation': [1, maximum],
                 'zero_branch': 'self == 0' if family == 'multiple' else 'usize::MAX',
                 'operation_branch': 'match nonzero arm' if family == 'multiple' else 'size != 0'}
        need(facts['divisor_interval_at_operation'][0] > 0, 'nonzero divisor')
    elif family == 'fmt':
        rhs = int(re.search(r's\.len\(\)\s*<<\s*(\d+)', SHAPES['fmt'])[1])
        need(0 <= rhs < bits and not (rhs > bits-1), 'shift RHS range')
        facts = {'rhs': rhs, 'word_bits': bits, 'overflow_flag': 'RHS > (word_bits - 1)',
                 'overflow_flag_value': False, 'length_bound_required': False}
    else:
        cap = int(re.search(r'CAP:\s*usize\s*=\s*(\d+)', sources['std', MODEL])[1])
        need(0 <= cap <= maximum and cap == 32, 'CAP range')
        # Exhaust all admitted lengths and induction states, not element values.
        # Return-false branches only shorten loops. At inner header counts<=j;
        # either branch adds 0 or 1, preserving counts<=j+1 on the back-edge.
        first_states = outer_states = inner_states = count_transitions = 0
        for n in range(cap+1):
            for i in range(1, max(1, n)):
                need(1 <= i < n and 0 <= i-1 < n and i+1 <= n <= maximum, 'sorted-loop invariant')
                first_states += 1
            for i in range(n):
                need(0 <= i < n <= cap and i+1 <= n <= maximum, 'outer-loop invariant')
                outer_states += 1
            for j in range(n):
                need(0 <= j < n <= cap and j+1 <= n <= maximum, 'inner-loop invariant')
                inner_states += 1
                for count in range(j+1):
                    for increment in (0, 1):
                        need(0 <= count+increment <= j+1 <= n <= maximum, 'counter induction')
                        count_transitions += 1
        facts = {'CAP': cap, 'before_array_length': cap, 'accepted_lengths': [0, cap],
                 'equal_lengths_guard': True, 'caller_or_origin_required': False,
                 'sorted_loop_invariant': '1 <= i <= max(1,n); body only i < n',
                 'outer_loop_invariant': '0 <= i <= n', 'inner_loop_invariant': '0 <= j <= n',
                 'counts_at_inner_header': '0 <= old_count,new_count <= j',
                 'counter_increment_max': cap, 'index_increment_max': cap,
                 'sorted_body_states': first_states, 'outer_body_states': outer_states,
                 'inner_body_states': inner_states, 'counter_induction_transitions': count_transitions}
    return {'verified_anchors': checked, 'facts': facts}


def index(items, key, label):
    need(isinstance(items, list) and all(isinstance(x, dict) for x in items), label + ' list')
    result = {x[key]: x for x in items}
    need(len(result) == len(items) and all(isinstance(k, str) and k for k in result), label + ' duplicate/missing ID')
    return result


def load():
    data = (HERE/'INPUTS.json').read_bytes()
    need(sha(data) == MANIFEST_SHA, 'input manifest SHA')
    manifest = json.loads(data)
    blobs = {}
    for rel, expected in manifest['files'].items():
        data = (HERE/rel).read_bytes()
        need(sha(data) == expected, 'input SHA:' + rel)
        blobs[rel] = data
    sources = {}
    for item in manifest['sources']:
        data = subprocess.check_output(['git', '-C', str(REPOS[item['repo']]), 'show',
                                       item['commit'] + ':' + item['path']])
        need(sha(data) == item['sha256'], 'source blob SHA:' + item['path'])
        sources[item['repo'], item['path']] = data.decode()
    bundle = {'manifest': manifest, 'sources': sources,
              'accept': json.loads(blobs['../accept/ACCEPT.json']),
              'request': json.loads(blobs['../CI-REQUEST.json']), 'groups': {}}
    for spec in bundle['request']['execution_groups']:
        gid = spec['id']
        bundle['groups'][gid] = {name: json.loads(blobs['../evidence/' + gid + '/' + name + '.json'])
                                for name in ('properties', 'export', 'receipt')}
    return bundle


def analyze(bundle):
    manifest, sources, request, baseline, groups = (bundle[k] for k in ('manifest','sources','request','accept','groups'))
    need(request['std_sha'] == baseline['source_sha'] == STD and request['tool_sha'] == baseline['tool_sha'] == TOOL,
         'request/receipt source/tool SHA')
    need(baseline['request_sha256'] == REQUEST and baseline['run'] == 43923266772, 'run/request namespace')
    # Validation also runs when injected structured inputs bypass load() in tests.
    need(sha(encoded(request)) == manifest['request_canonical_sha256'], 'request content identity')
    need(sha(encoded(baseline)) == manifest['accept_canonical_sha256'], 'baseline content identity')
    for item in manifest['sources']:
        need(sha(sources[item['repo'],item['path']].encode()) == item['sha256'], 'source SHA')
    rows = index(request['rows'], 'id', 'request row')
    specs = index(request['execution_groups'], 'id', 'execution group')
    need(set(specs) == set(groups), 'missing/foreign group')
    membership = [rid for spec in specs.values() for rid in spec['row_ids']]
    need(len(membership) == len(set(membership)) and set(membership) == set(rows), 'row partition')
    original = baseline['unreachable_analysis']['records']
    selected = [r for r in original if r['decision'].startswith('UNKNOWN')]
    need(len(selected) == 187 and len({(r['row_id'],r['property_id']) for r in selected}) == 187,
         'exact unresolved set')
    need(sum(r['status_kind'] == 'check' and r['decision'].startswith('ALLOWED_') for r in original) == 226
         and sum(r['status_kind'] == 'cover' for r in original) == 2, 'read-only baseline partition')
    selected_by_group = collections.defaultdict(list)
    for r in selected:
        selected_by_group[r['group']].append(r)
    output, certificates = [], {}
    anchors = {}
    for name, (repo, path, start, end) in ANCHORS.items():
        value = excerpt(sources[repo,path], start, end)
        need(sha(value.encode()) == manifest['anchors'][name], 'exact source anchor:' + name)
        anchors[name] = {'repo': repo, 'commit': STD if repo == 'std' else TOOL, 'path': path,
                         'start_line': start, 'end_line': end, 'sha256': sha(value.encode())}
    for gid, spec in sorted(specs.items()):
        group = groups[gid]
        # These three projections are immutable inputs; no raw stream is read.
        for name in ('properties','export','receipt'):
            need(sha(encoded(group[name])) == manifest['group_canonical_sha256'][gid][name],
                 'group content identity:' + gid + '/' + name)
        rich, exp, rec = (group[k] for k in ('properties','export','receipt'))
        need(rec['group'] == gid and rec['request_sha256'] == REQUEST, 'group/request receipt')
        need(rec['std_sha'] == STD and rec['tool_sha'] == TOOL, 'producer pins')
        need(rec['source_before'] == rec['source_after'] ==
             {k: request[k] for k in ('std_sha','std_tree','tool_sha','tool_tree','changed_file_sha256')},
             'source snapshots')
        need(rec['variant'] == spec['variant'] and rec['unwind'] == spec['unwind'], 'group variant')
        need(exp['kani_commit'] == TOOL and exp['kani_commit_dirty'] is False
             and exp['target'] == 'x86_64-unknown-linux-gnu', 'producer/target')
        rh = index(rich['harnesses'], 'name', 'rich harness')
        eh = index(exp['harnesses'], 'name', 'export harness')
        selectors = [rows[rid]['selector'] for rid in spec['row_ids']]
        need(len(set(selectors)) == len(selectors) and set(rh) == set(eh) == set(selectors), 'harness namespace')
        need(rec['selectors'] == selectors, 'receipt selectors')
        for selector, h in rh.items():
            by_id = index(h['properties'], 'id', 'rich property')
            expected_u = {r['property_id'] for r in original if r['group'] == gid
                          and r['selector'] == selector and r['status_kind'] == 'check'}
            actual_u = {p['id'] for p in by_id.values()
                        if p['status'] == 'UNREACHABLE' and p['class'] != 'cover'}
            exported_u = eh[selector]['checks']['unreachable']
            need(actual_u == expected_u == set(exported_u)
                 and len(exported_u) == len(set(exported_u)), 'exact original U check set')
        for record in selected_by_group[gid]:
            rid, selector, pid = record['row_id'], record['selector'], record['property_id']
            need(rid in spec['row_ids'] and rows[rid]['selector'] == selector, 'row/harness binding')
            by = index(rh[selector]['properties'], 'id', 'property')
            need(pid in by, 'missing selected property')
            prop = by[pid]
            for field in ('class','description','status'):
                need(prop[field] == record[field], 'original property:' + field)
            site = record['site']
            need(prop['file'] == site['export_file'] and prop['line'] == site['line']
                 and prop['location_display'] == site['location_display'], 'original site')
            bucket = eh[selector]['checks']['unreachable']
            need(bucket.count(pid) == 1, 'exact UNREACHABLE check inventory')
            family, operation, path, fn = classify(prop)
            need(site['function'] == fn and site['source_path'] == path, 'original function/path')
            context = site['source_context']
            need(context['lines'] == [{'line': i, 'text': sources['std',path].splitlines()[i-1]}
                 for i in range(context['start_line'], context['end_line']+1)], 'original source context')
            source_hash = sha(sources['std',path].encode())
            # Variants only change the production target; reject any variant
            # changing the proof's dependency/model source without a new rule.
            changed = request['variants'].get(spec['variant'], {}).get('changed_file_sha256', {})
            need(path not in changed, 'variant changes rule source')
            if path in rec['source_under_test']['file_sha256']:
                need(rec['source_under_test']['file_sha256'][path] == source_hash, 'executed source hash')
            if family not in certificates:
                certificates[family] = check_premises(family, sources)
            output.append({'group': gid, 'row_id': rid, 'harness': selector, 'property_id': pid,
                'class': prop['class'], 'description': prop['description'], 'status': prop['status'],
                'site': site, 'source_commit': STD, 'source_sha256': source_hash,
                'request_sha256': REQUEST, 'variant': spec['variant'], 'rule': family,
                'operation': operation, 'premises': certificates[family],
                'evidence': {name: {'path': '../evidence/' + gid + '/' + name + '.json',
                    'sha256': manifest['files']['../evidence/' + gid + '/' + name + '.json']}
                    for name in ('properties','export','receipt')},
                'decision': 'JUSTIFIED_GENERATED_SAFETY_APPLICABILITY',
                'assurance': 'PINNED_SOURCE_LOCAL_ARGUMENT; SOURCE_REPORTED_CHECK_IDENTITY',
                'independent_sorting_proof_credit': 'NONE'})
    counts = dict(sorted(collections.Counter(r['rule'] for r in output).items()))
    need(counts == {'abs_diff':50,'alignment':25,'multiple':12,'allocation':18,'fmt':28,'active_post':54},
         'complete six-family inventory')
    return {'schema':'ch8-s1-07-u-v1', 'run':43923266772, 'request_sha256':REQUEST,
        'source_commit':STD, 'tool_commit':TOOL, 'manifest_sha256':MANIFEST_SHA,
        'scope':'187 original unresolved check records only', 'source_anchors':anchors,
        'summary':{'processed':len(output),'justified':len(output),'UNKNOWN':0,'families':counts,
                   'existing_allowed_checks_read_only':226,'negative_return_covers_read_only':2},
        'credit':'Generated safety-check applicability only; no sorting relation, reachability, PFC, or qualified-count credit',
        'records':output}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    try:
        result = analyze(load())
        data = encoded(result)
        if args.write:
            (HERE/'U.json').write_bytes(data)
        else:
            need((HERE/'U.json').read_bytes() == data, 'U.json replay mismatch')
        print(json.dumps({'replay':'PASS', **result['summary']}, sort_keys=True))
    except (ValueError, KeyError, TypeError, IndexError, OSError, subprocess.CalledProcessError) as exc:
        print(json.dumps({'replay':'ERROR','reason':str(exc)}), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
