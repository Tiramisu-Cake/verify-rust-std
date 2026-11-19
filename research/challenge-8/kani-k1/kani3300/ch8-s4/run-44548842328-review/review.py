#!/usr/bin/env python3
"""Independent compact-evidence/source review. Offline; writes only REVIEW.json.

No intake modules are imported. Semantic arguments below were checked against
the pinned Rust source; these consistency checks do not prove compiler lowering.
"""
import base64
import collections
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
G0 = HERE.parents[5]
INTAKE = HERE.with_name('run-44548842328')
BASE = '7c66fb85b99f77801ff10e99ccc5d37761ba5442'
SOURCE = Path('/root/verify-rust-std-ch8-s4p-2-w13')
STD = '8faf8e62af8f82b5c46af020086f8df591b6757e'
TOOL = Path('/root/kani-upstream-ch8-s1')
TOOL_SHA = '0aac16ef62da9e9d5645782d458593e5d78143ba'
EXPORT = '/home/runner/work/kani/kani/export/'
CHECKS = []

def sha(b):
    return hashlib.sha256(b).hexdigest()

def need(value, label):
    if not value:
        raise AssertionError(label)
    CHECKS.append(label)

def blob(repo, rev, path):
    return subprocess.check_output(['git', '-C', str(repo), 'show', rev + ':' + path])

def read(name):
    return json.loads((INTAKE / name).read_bytes())

def decode(entry):
    return entry['text'].encode() if entry.get('encoding', 'utf-8') == 'utf-8' else base64.b64decode(entry['text'], validate=True)

def main():
    manifest = read('MANIFEST.json')['files']
    prefix = str(INTAKE.relative_to(G0)) + '/'
    for name, identity in manifest.items():
        b = (INTAKE / name).read_bytes()
        need(b == blob(G0, BASE, prefix + name), 'pinned intake bytes ' + name)
        need(len(b) == identity['bytes'] and sha(b) == identity['sha256'], 'manifest ' + name)
    need((INTAKE / 'MANIFEST.json').read_bytes() == blob(G0, BASE, prefix + 'MANIFEST.json'), 'pinned manifest')
    gz = (INTAKE / 'group-evidence.json.gz').read_bytes()
    raw = gzip.decompress(gz)
    integrity = read('artifact-integrity.json')
    need(sha(gz) == integrity['payload_sha256'] and sha(raw) == integrity['uncompressed_sha256'], 'compact compressed/uncompressed digests')
    packet = json.loads(raw)
    members = {}
    for name, entry in packet['files'].items():
        b = decode(entry)
        need(len(b) == entry['bytes'] and sha(b) == entry['sha256'], 'compact member ' + name)
        members[name] = json.loads(b)
    need(len(members) == 119, '119 structured members')
    request = members['campaign-start.json']['request_data']
    need(request['std_sha'] == STD and request['tool_sha'] == TOOL_SHA, 'exact std/tool')
    need(request == read('ROOTS.json')['request'], 'request projection')
    need(request['unreachable_admission'] == {'mode':'REJECT_ALL', 'proposal':'S3-U-SITE-REVIEW-v1', 'enabled':False, 'unknown':'REJECT', 'role_unreachable':'REJECT'}, 'unchanged strict U policy')
    need(read('RUN-METADATA.json')['conclusion'] == 'failure' and members['receipt.json']['state'] == 'SELECTED_PARTIAL', 'failure/partial history')
    source_cache = {}
    def source(path):
        if path not in source_cache:
            source_cache[path] = blob(SOURCE, STD, path)
        return source_cache[path]
    for field in ('changed_file_sha256', 'cfg_pfc_source_sha256', 'contract_stack_source_sha256', 'lexical_source_sha256', 'ordinary_contract_source_sha256'):
        for path, digest in request[field].items():
            need(sha(source(path)) == digest, 'request source dependency ' + path)
    helper_path = 'library/core/src/slice/sort/shared/smallsort.rs'
    helper = source(helper_path).decode().splitlines()
    anchors = {340:'if len < 2 {', 341:'return;', 351:'let no_merge = len < 18;',
               354:'let initial_region_len = if no_merge { len } else { len_div_2 };',
               370:'insertion_sort_shift_left(region, presorted_len, is_less);',
               372:'if no_merge {', 373:'return;',
               389:'bidirectional_merge(slice::from_raw_parts_mut(v_base, len), scratch_base, is_less);'}
    for line, text in anchors.items():
        need(helper[line-1].strip() == text, 'independent helper anchor ' + str(line))
    projections = read('NATIVE-PROPERTIES.json')
    qualifications = read('QUALIFICATION.json')['rows']
    arguments = read('U-DOMAIN-ARGUMENTS.json')['instances']
    argmap = {(x['root'], x['property']['id']): x for x in arguments}
    need(len(argmap) == len(arguments) == 67, '67 unique per-invocation U records')
    location_records = read('LOCATION-ARGUMENTS.json')['non_std_location_cases']
    locmap = {(x['root'], x['property']['id']): x for x in location_records}
    need(len(locmap) == len(location_records) == 13, '13 unique location records')
    totals = collections.Counter()
    seen_u, seen_loc, u_decisions, cases = set(), set(), [], []
    arithmetic = {
        ('num::<impl usize>::abs_diff.assertion.1', 3222): ('num/uint_macros.rs', 'other - self', 'self<other makes other-self nonnegative; usize order prevents underflow.'),
        ('num::<impl usize>::abs_diff.assertion.2', 3224): ('num/uint_macros.rs', 'self - other', 'The else branch has self>=other; self-other cannot underflow.'),
        ('num::<impl usize>::is_multiple_of.assertion.1', 3916): ('num/uint_macros.rs', '_ => self % rhs == 0,', 'The separate zero match arm excludes rhs=0 at the remainder operation; no condition on self is needed.'),
        ('ub_checks::is_valid_allocation_size.assertion.1', 148): ('ub_checks.rs', 'if size == 0', 'The division arm is entered only for size!=0; u8 size is also 1. No ownership conclusion follows.'),
        ('ptr::const_ptr::<impl *const ()>::is_aligned_to.assertion.1', 1479): ('ptr/const_ptr.rs', 'align - 1', 'Continuation past the non-power-of-two panic requires a nonzero power of two, hence align>=1 and subtraction is defined.'),
        ("fmt::Arguments::<'_>::from_str.assertion.1", 820): ('fmt/mod.rs', 's.len() << 1 | 1', 'Literal shift count 1 is below the x86_64 usize width 64; this is shift-count definedness, not preservation of high bits or transmute validity.')}
    for q, row in zip(qualifications, request['rows']):
        rid = row['id']
        need(q['id'] == rid, 'row order ' + rid)
        gp = 'groups/s3-' + rid + '/'
        ps = members[gp+'properties.json']['harnesses'][0]['properties']
        h = members[gp+'export.json']['harnesses'][0]
        receipt = members[gp+'receipt.json']
        bm = members[gp+'binding-metadata.json']
        need(ps == projections[rid]['properties'], 'full property projection ' + rid)
        need(len({p['id'] for p in ps}) == len(ps) == h['n_properties'] == q['n_properties'], 'unique complete inventory ' + rid)
        need(receipt['invocation_id'] == q['invocation_id'] == bm['invocation_id'], 'same invocation ' + rid)
        need(receipt['cargo_target_dir'] == q['namespace'] and q['invocation_id'] in q['namespace'], 'namespace ' + rid)
        need(bm['std_sha'] == STD and bm['tool_sha'] == TOOL_SHA, 'binding pins ' + rid)
        need(members[rid+'/receipt.json']['s3_expected_match'] is False and q['strict_expected_match'] is False, 'historical strict rejection ' + rid)
        need(q['checks'] == h['checks'] and q['covers_summary'] == h['covers'], 'native summaries ' + rid)
        totals.update(p['status'] for p in ps)
        covers = [p for p in ps if p['class'] == 'cover']
        checks = [p for p in ps if p['class'] != 'cover']
        need(len(checks) == h['checks']['total'] and len(covers) == h['covers']['total'], 'check/cover partition ' + rid)
        need({p['id'] for p in checks if p['status']=='UNREACHABLE'} == set(h['checks']['unreachable']), 'U summary ' + rid)
        positive = rid in request['domains']
        regs = []
        for entry in bm['native_metadata']:
            if entry['state'] == 'CAPTURED':
                b = decode(entry)
                need(sha(b) == entry['sha256'] and len(b) == entry['bytes'], 'native metadata digest ' + rid)
                regs.extend(x for x in json.loads(b).get('proof_harnesses', []) if x['pretty_name'] == row['selector'])
        need(len(regs) == 1 and regs[0]['attributes']['kind'] == 'Proof', 'actual native proof registration ' + rid)
        if positive:
            domain = request['domains'][rid]
            need(domain['type']=='u8' and domain['comparator']=='KeyLess<u8>' and domain['allocation']==34 and domain['base']==1 and domain['initialized'] and domain['logical_values']=='ALL_34_INDEPENDENT_U8_0_255' and not domain['summary_edges'], 'finite full-byte domain ' + rid)
            need(row['mode']=='Original' and row['target'] is None and not regs[0]['attributes']['stubs'] and not regs[0]['attributes']['verified_stubs'] and not q['providers'], 'Original no replacement ' + rid)
            f = request['source_bindings'][rid]['file']
            lines = source(f).decode().splitlines()
            body = lines[regs[0]['original_start_line']-1:regs[0]['original_end_line']]
            lo, hi = domain['length_interval']
            calls = [l.strip() for l in body if 'small_sort_network(' in l]
            slices = ['[1..2]', '[1..1]'] if hi==1 else [f'[1..{hi+1}]']
            need(len(calls)==len(slices) and all(s in c for s,c in zip(slices,calls)), 'literal helper calls ' + rid)
            need('let mut v: [u8; 34] = kani::any();' in '\n'.join(body) and 'for i in 0..34 {' in '\n'.join(body), 'full initialization/frame loop ' + rid)
            roles = [p for p in ps if p['class']=='assertion' and p['description'].startswith('S4P2R2_')]
            need(len(roles)==4 and all(p['status']=='SUCCESS' for p in roles), 'four required SUCCESS roles ' + rid)
            for role in row['roles']:
                matches = [p for p in ps if p['description']==role['description']]
                need(len(matches)==1 and matches[0]['class']==role['class'] and matches[0]['status']==role['status'] and matches[0]['line']==str(role['line']) and matches[0]['file']==EXPORT+f and lines[role['line']-1]==role['source_line'] and sha(source(f))==role['source_sha256'], 'exact source-bound role/cover ' + role['description'])
            need({p['description'] for p in covers}==set(row['required_cover_messages']) and len(covers)==row['required_cover_count'] and all(p['status']=='SATISFIED' for p in covers), 'all declared covers SAT ' + rid)
            need(max(int(p['line']) for p in roles)<min(int(p['line']) for p in covers), 'post-role continuing witnesses ' + rid)
            need(all(p['status'] in ('SUCCESS','UNREACHABLE') for p in checks), 'no missing/error/failed safety status ' + rid)
            unwinds = [p for p in checks if p['class']=='unwind']
            need(all(p['status']=='SUCCESS' for p in unwinds) and q['resolved_unwind']==row['unwind']==36, 'complete exported unwind inventory ' + rid)
            cases.append({'root':rid, 'verdict':'APPROVE', 'invocation_id':q['invocation_id'], 'properties':len(ps), 'SUCCESS':sum(p['status']=='SUCCESS' for p in checks), 'U':sum(p['status']=='UNREACHABLE' for p in checks), 'SAT':len(covers), 'roles':roles, 'covers':covers, 'unwind':unwinds, 'findings':[]})
        for p in ps:
            key = (rid,p['id'])
            if p['status']=='UNREACHABLE':
                seen_u.add(key)
                a = argmap[key]
                f = p['file'].removeprefix(EXPORT)
                line = int(p['line'])
                text = source(f).decode().splitlines()[line-1]
                need(a['property']==p and a['invocation_id']==q['invocation_id'] and a['namespace']==q['namespace'], 'U exact native identity '+rid+'/'+p['id'])
                need(a['source_sha']==STD and a['source_file']==f and a['source_sha256']==sha(source(f)) and a['source_line']==line and a['exact_source_line']==text, 'U exact source binding '+rid+'/'+p['id'])
                if (p['id'],line) in arithmetic:
                    suffix, token, reason = arithmetic[p['id'],line]
                    need(f.endswith(suffix) and token in text, 'arithmetic operation '+rid+'/'+p['id'])
                    kind = 'GENERATED_FAILURE_EDGE_EXCLUDED'
                elif '::bidirectional_merge::<' in p['id'] or '::small_sort_network::<' in p['id']:
                    need(positive and f==helper_path, 'network/merge actual instance '+rid+'/'+p['id'])
                    hi = request['domains'][rid]['length_interval'][1]
                    if hi <= 1:
                        reason = 'Both literal lengths 0/1 return at 340-341 before all reported network/merge sites.'
                    else:
                        reason = f'Literal N={hi}; initial region length={hi}<9, presorted_len=1. Immutable no_merge=true forces return at 372-373 on first iteration after insertion_sort_shift_left. No normal continuation reaches 381 or merge call389; nonreturn also cannot reach them.'
                    need(line in ((974,990,991,992) if '::bidirectional_merge::<' in p['id'] else (350,381)), 'exact excluded helper site '+rid+'/'+p['id'])
                    kind = 'SOURCE_SITE_EXCLUDED'
                else:
                    need(f.endswith('/sorting_model.rs') and '::active_post::<' in p['id'], 'known model U '+rid+'/'+p['id'])
                    if rid in ('checker_order_corrupt','sort13_weak'):
                        reason = 'Fixed descending output makes i=1 order comparison return false at98, before increment100 and count sites106-118. sort13 weak seam is an empty replacement on every comparator, so its descending fixture is unchanged.'
                        need(line in (100,106,111,112,113,118), 'negative early-order site '+rid+'/'+p['id'])
                    elif rid in ('checker_count_corrupt','s4p_cell_count_corrupt'):
                        reason = 'First query has unequal multiplicities (32 vs31 ones, or1 vs2 zeroes respectively); return116 occurs before outer increment118.'
                        need(line==118, 'negative early-count site '+rid+'/'+p['id'])
                    else:
                        need(rid.endswith('n00_01_fullbyte') and line in (97,100), 'N01 excluded order sites '+p['id'])
                        reason = 'active_post i starts1; matching snapshot/output length is0 or1, so i<L is false and the order body97/increment100 cannot execute. Count/post roles remain independently required.'
                    kind = 'SOURCE_SITE_EXCLUDED'
                need(kind==a['argument_kind'] and bool(a['domain_unreachability_argument']), 'reviewed U category '+rid+'/'+p['id'])
                u_decisions.append({'root':rid,'invocation_id':q['invocation_id'],'property':p,'source_sha':STD,'source_file':f,'source_sha256':sha(source(f)),'source_line':line,'kind':kind,'reviewer_argument':reason,'verdict':'ACCEPT_SOURCE_REPORTED_SITE_ARGUMENT'})
            if '/library/kani_core/' in p['file'] or '<builtin-library-memcpy>' in p['file']:
                seen_loc.add(key)
                a = locmap[key]
                need(a['property']==p and a['invocation_id']==q['invocation_id'] and a['namespace']==q['namespace'] and p['status']=='SUCCESS', 'exact location record '+rid+'/'+p['id'])
                if '/library/kani_core/' in p['file']:
                    b = blob(TOOL, TOOL_SHA, 'library/kani_core/src/models.rs')
                    need(a['source_sha']==TOOL_SHA and a['source_sha256']==sha(b) and p['line']=='203' and p['class']=='unreachable', 'stock-model source '+rid)
                    need(any(x['id']=='<usize as kani::rustc_intrinsics::ToISize>::to_isize.safety_check.1' and x['status']=='SUCCESS' and x['description']=='Offset value overflows isize' for x in ps), 'retained conversion safety sibling '+rid)
                else:
                    need((p['id'],p['line']) in (('memcpy.pointer.1','33'),('memcpy.pointer.2','34')) and p['class']=='pointer' and a['backend_builtin_source_identity'].startswith('UNKNOWN_NOT_EXPORTED'), 'builtin pseudo-coordinate/source UNKNOWN '+rid+'/'+p['id'])
    need(seen_u==set(argmap) and seen_loc==set(locmap), 'exact U/location bijections')
    need(dict(totals)=={'SUCCESS':1051,'UNREACHABLE':67,'FAILURE':4,'SATISFIED':21}, 'all 1143 original statuses')
    need([c['SAT'] for c in cases]==[6,6,6,3], '6/6/6/3 SAT')
    need({p['description'] for p in cases[-1]['covers']}=={'S4P2R2_N_00_01_N00','S4P2R2_N_00_01_N01','S4P2R2_N_00_01_USEFUL_RETURN'}, 'both N0 and N1 post-role witnesses')
    cost = read('COST-INTERPRETATION.json')
    need(cost['exact_speedup_factor'] is None and 'UNKNOWN_CENSORED' in cost['old_r1_positives'], 'honest censored old costs')
    result = {'status':'PASS','input_commit':BASE,'source':STD,'tool':TOOL_SHA,'compact_sha256':sha(gz),'checks_count':len(CHECKS),'checks':CHECKS,'cases':cases,'U_instances':u_decisions,'U_kind_counts':dict(collections.Counter(x['kind'] for x in u_decisions)),'non_std_records_reviewed':len(seen_loc),'status_counts':dict(totals),'findings':[],'assurance':'Independent review of bounded SOURCE_REPORTED S1 candidates; no compiler/emitter/MIR proof or admission. Generated failure-edge exclusion does not explain UNREACHABLE check-site classification.'}
    (HERE/'REVIEW.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','checks_count','U_kind_counts','non_std_records_reviewed','status_counts','findings')}))

if __name__ == '__main__':
    main()
