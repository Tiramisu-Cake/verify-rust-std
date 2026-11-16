"""Offline, fail-closed contract binding; never executes compiler/evidence commands."""
import argparse
import collections
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE / 'accept-v3'))
from classifier_v3 import bind_stdout, digest, require

G0 = '57ff2242017bf6356f78245d92d871e2534c2c7d'
SOURCE = '9fa2f7f97760584f38738909625c064006d8a936'
TOOL = '0aac16ef62da9e9d5645782d458593e5d78143ba'
CONTROL = '112fcc9ada67ee2bb8e1712d47983d6717487b78'
ROOT = 'core::slice::sort::shared::smallsort'
DIR = 'library/core/src/slice/sort/shared/smallsort'
PROFILES = ROOT + '::verify::merge::profiles'
NETWORK = ROOT + '::verify::network'
FRAME = 'rejects_swap_comparator_writing_outside_frame_u8'
# Reviewed source sites, not inferred from observed successful assertions.
SITES = {
    'swap_profile': ('/verify/merge/profiles.rs', [204], [205], [206, 207]),
    'sort4_profile': ('/verify/merge/profiles.rs', [227], [228], [229, 230]),
    'insert_tail_profile': ('/verify/merge/profiles.rs', [262], [266], [267, 268]),
    'merge_profile': ('/verify/merge/profiles.rs', [298], [299], [300, 301]),
    'stable_cell': ('/verify/forwarding_contracts.rs', [95], [96], [97, 98]),
    'unstable_byte': ('/verify/forwarding_contracts.rs', [111], [112], [113, 114]),
    'freeze_noncopy': ('/verify/forwarding_contracts.rs', [124], [125], [126, 127]),
    'swap_if_less': ('.rs', [387, 394, 401, 405, 409], [413], []),
}
TOOL_FILES = [
    'library/kani_macros/src/sysroot/contracts/' + f + '.rs'
    for f in ('mod', 'initialize', 'bootstrap', 'check', 'replace')
] + [
    'kani-compiler/src/kani_middle/attributes.rs',
    'kani-compiler/src/kani_middle/resolve.rs',
    'kani-compiler/src/kani_middle/codegen_units.rs',
    'kani-compiler/src/kani_middle/transform/contracts.rs',
    'kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs',
    'kani-driver/src/call_goto_instrument.rs',
    'kani-driver/src/cbmc_output_parser.rs',
    'kani-driver/src/frontend/schema_utils.rs',
    'kani_metadata/src/harness.rs',
]


def read(path):
    return json.loads(path.read_bytes())


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def relative(name):
    """Driver pretty names omit the local core crate; keep all path components."""
    return name.replace('core::', '')


def compact(value):
    return re.sub(r'\s+', '', value)


def clause(text, line, kind):
    tail = '\n'.join(text.splitlines()[line - 1:])
    prefix = '#[kani::' + kind + '('
    require(tail.startswith(prefix), 'SOURCE_CLAUSE_SITE_MISMATCH')
    depth, start = 1, len(prefix)
    for i in range(start, len(tail)):
        if tail[i] == '(':
            depth += 1
        elif tail[i] == ')':
            depth -= 1
            if depth == 0:
                require(tail[i + 1:i + 2] == ']', 'SOURCE_CLAUSE_END_MISMATCH')
                return tail[start:i]
    raise ValueError('SOURCE_CLAUSE_INCOMPLETE')


def expected_instance(row, mapping):
    target = mapping['binding']['source_target']['fully_qualified']
    fn = target.rsplit('::', 1)[-1]
    require(fn in SITES, 'UNREVIEWED_TARGET')
    profile = row['profile']
    if fn.endswith('_profile'):
        modules = {
            **{p: PROFILES for p in ('LtU8', 'LtI32', 'LtU64', 'Sort4ReadU64', 'Sort4ReadB16')},
            **{p: NETWORK for p in ('StrictU8', 'StrictU64', 'DropU8', 'CellI32', 'KeyB16', 'KeyB17')},
        }
        require(profile in modules, 'UNREVIEWED_PROFILE')
        return target + '::<' + modules[profile] + '::' + profile + '>'
    if fn == 'swap_if_less':
        helper = ROOT + '::verify::helper_contracts::'
        if row['id'] == FRAME:
            require(profile == 'effectful captured-counter closure', 'FRAME_PROFILE_MISMATCH')
            return target + '::<u8, ' + helper + FRAME + '::{closure#0}>'
        require(row['id'] == 'swap_safety_u8_backing4' and
                profile == 'arbitrary_less::<u8> FnDef', 'SWAP_F_INSTANCE_MISMATCH')
        return target + '::<u8, ' + helper + 'arbitrary_less<u8>>'
    require((row['id'], profile) in {
        ('stable_cell_n2', 'Cell<u8>/upper7'), ('unstable_byte_n2', 'u8/upper7'),
        ('freeze_noncopy_n2', 'NonCopyU8/upper7')}, 'CONCRETE_FORWARDER_MISMATCH')
    return target


def property_at(records, pid, function, file=None, line=None, description=None):
    p = records[pid]
    require(p['function'] == function and p['id'] == pid, 'PROPERTY_FUNCTION_MISMATCH')
    require(p['status'] == 'SUCCESS', 'REQUIRED_PROPERTY_NOT_SUCCESS')
    if file is not None:
        require(p['file'] == file and p['line'] == line, 'PROPERTY_SOURCE_SITE_MISMATCH')
    if description is not None:
        require(compact(p['description']) == compact(description), 'PROPERTY_CLAUSE_TEXT_MISMATCH')
    return p


def clause_property(records, function, file, line, description):
    # Runtime checks in clause evaluation share assertion numbering. In
    # insert_tail, subtraction at line264 is .assertion.1; ensures are .2/.3.
    found = [p for p in records.values() if p['function'] == function and
             p['file'] == file and p['line'] == line and
             compact(p['description']) == compact(description) and
             re.fullmatch(re.escape(function) + r'\.assertion\.[1-9][0-9]*', p['id'])]
    require(len(found) == 1, 'CLAUSE_PROPERTY_MISSING_OR_AMBIGUOUS')
    return property_at(records, found[0]['id'], function, file, line, description)


def bind(row, old, mapping, h, records, demangled, sources):
    instance = expected_instance(row, mapping)
    fn = mapping['binding']['source_target']['fully_qualified'].rsplit('::', 1)[-1]
    suffix, requires, modifies, ensures = SITES[fn]
    file = DIR + suffix
    source = sources[file]
    out = {'state': 'BOUND', 'expected_instance_fully_qualified': instance,
           'source_file': file, 'source_requires_lines': requires,
           'source_modifies_lines': modifies, 'source_ensures_lines': ensures,
           'assurance': 'PINNED_SOURCE_CHAIN_AND_EXACT_SAME_ROW_SOURCE_REPORTED_PROPERTIES',
           'proof_credit': 'NONE'}
    if row['mode'].startswith('PFC:'):
        symbol = old['binding']['export_contract_symbol']
        require(h['contract']['contracted_function_name'] == symbol, 'CONTRACT_SYMBOL_MISMATCH')
        name = demangled[symbol]
        # Closure ordinals are observations, not role rules. Role follows metadata
        # find_modifies + named checked_with/modifies_wrapper source chain.
        match = re.fullmatch(re.escape(instance) + r'::\{closure#([0-9]+)\}::\{closure#([0-9]+)\}', name)
        require(match is not None, 'FULL_TARGET_PROFILE_OR_WRAPPER_MISMATCH')
        check = name.rsplit('::', 1)[0]
        out.update(contract_symbol=symbol, modifies_wrapper_fully_qualified=name,
                   check_wrapper_fully_qualified=check,
                   check_local='__kani_check_' + fn, modifies_local='__kani_modifies_' + fn,
                   preconditions={'role': 'ASSUMED_BY_CHECK_WRAPPER', 'assertion_ids': []})
        props = []
        for cls, desc in (
            ('single_top_level_call', 'Only a single top-level call to function ' + symbol + ' when checking contract ' + symbol),
            ('no_recursive_call', 'No recursive call to function ' + symbol + ' when checking contract ' + symbol),
            ('no_alloc_dealloc_in_requires', 'Check that requires do not allocate or deallocate memory'),
            ('no_alloc_dealloc_in_ensures', 'Check that ensures do not allocate or deallocate memory'),
        ):
            props.append(property_at(records, name + '.' + cls + '.1', name, file,
                                     modifies[0], desc))
        out['enforced_contract_properties'] = props
        out['postconditions'] = [clause_property(
            records, relative(check), file, line, clause(source, line, 'ensures')) for line in ensures]
        out['assigns'] = {
            'enforced_contract_symbol': symbol,
            'relation': 'ONE_ENFORCED_CONTRACT_FOR_THIS_EXACT_HARNESS; IDs name write sites, not contract owner',
            'properties': [p for pid, p in records.items() if '.assigns.' in pid],
        }
        require(out['assigns']['properties'], 'ASSIGNS_INVENTORY_ABSENT')
        require(all(p['status'] == ('FAILURE' if row['id'] == FRAME and p['id'] in h['checks']['failure']
                                    else 'SUCCESS') for p in out['assigns']['properties']),
                'ASSIGNS_STATUS_MISMATCH')
    else:
        require(row['mode'] == 'Replace:profile_wrapper' and h['contract'] is None,
                'REPLACE_MODE_OR_CONTRACT_MISMATCH')
        require(h['attributes']['verified_stubs'] == [mapping['binding']['source_target']['fully_qualified']],
                'REPLACE_VERIFIED_STUB_MISMATCH')
        candidates = [p for p in records.values() if
                      re.fullmatch(re.escape(relative(instance)) + r'::\{closure#[0-9]+\}\.assertion\.[1-9][0-9]*', p['id']) and
                      p['file'] == file and p['line'] == requires[0] and
                      compact(p['description']) == compact(clause(source, requires[0], 'requires'))]
        require(len(candidates) == 1, 'REPLACE_PRECONDITION_WRAPPER_AMBIGUOUS')
        replace = candidates[0]['function']
        out['replace_wrapper_function'] = replace
        out['replace_local'] = '__kani_replace_' + fn
        out['preconditions'] = {'role': 'ASSERTED_BY_REPLACE_WRAPPER', 'properties': [clause_property(
            records, replace, file, line, clause(source, line, 'requires')) for line in requires]}
        out['postconditions'] = []
        out['replacement_postconditions'] = 'ASSUMED; matching accepted PFC leaf required separately'
        out['assigns'] = {'role': 'REPLACE_HAVOC_OF_SOURCE_MODIFIES; no enforced PFC contract here'}
    covers = []
    for c in mapping['covers']:
        prior_source_line = c['source_line']
        p = records[c['id']]
        require(p['status'] == 'SATISFIED' and p['file'] == c['source_file'], 'COVER_SITE_OR_STATUS_MISMATCH')
        macro = c.get('site_binding') == 'STATIC_MACRO_REPETITION_ORDINAL_MAPPING'
        if macro:
            # The diagnostic uses the macro invocation's first line; v2 points
            # at the row argument. Verify both from pinned source, never +/- guess.
            lines = sources[c['source_file']].splitlines()
            invocation = c['macro_callsite_line']
            if 'insert_tail_start1_group_case!(' in lines[invocation - 1]:
                expected_line = invocation
            else:
                require(lines[invocation - 2] == 'insert_tail_start1_group_case!(', 'MACRO_INVOCATION_MISMATCH')
                expected_line = invocation - 1
            require(p['line'] == expected_line, 'COVER_MACRO_LOCATION_MISMATCH')
            desc = 'insert-tail contract covers tail ' + str(c['macro_bindings']['end']) + ' with requires satisfied'
            require(p['description'] == desc, 'COVER_MACRO_DESCRIPTION_MISMATCH')
        elif c.get('site_binding') == 'STATIC_MACRO_TEMPLATE_ORDINAL_MAPPING':
            # V2's lexical ordinal is wrong for the nondeterministic 2..4
            # match: CBMC numbers arms 4,3,2. Bind literal clause + callsite.
            require(row['id'] in {'merge_contract_u64_n2_to4', 'merge_contract_u8_n2_to4'},
                    'UNREVIEWED_COVER_MACRO')
            candidates = [d for d in mapping['covers'] if
                          d.get('site_binding') == 'STATIC_MACRO_TEMPLATE_ORDINAL_MAPPING' and
                          '"' + p['description'] + '"' in d['source_expression']]
            require(len(candidates) == 1, 'MACRO_COVER_CLAUSE_AMBIGUOUS')
            c = candidates[0]
            require(p['line'] == c['macro_callsite_line'], 'MACRO_COVER_CALLSITE_MISMATCH')
            source_lines = sources[c['source_file']].splitlines()
            require(row['id'] in source_lines[c['macro_callsite_line'] - 1] and
                    c['source_expression'] in source_lines[c['source_line'] - 1],
                    'MACRO_COVER_SOURCE_MISMATCH')
        else:
            require(p['line'] == c['source_line'], 'COVER_SOURCE_LINE_MISMATCH')
        require(p['function'] == p['id'].rsplit('.cover.', 1)[0], 'COVER_FUNCTION_MISMATCH')
        covers.append({'property': p, 'source_role': c['role'],
                       'source_expression': c['source_expression'], 'source_line': c['source_line'],
                       'v3_mapping_source_line': prior_source_line,
                       'target_call_source_lines': c.get('target_call_source_lines', []),
                       'indirect_target_call_chain': c.get('indirect_target_call_chain', []),
                       'relation': 'MACRO_TEMPLATE_PLUS_EXACT_INVOCATION_AND_CLAUSE' if macro else 'EXACT_STDOUT_SOURCE_SITE'})
    out['covers'] = covers
    out['post_target_ids'] = old['cover_mapping']['post_target_ids']
    if row['expected'] == 'SUCCESS':
        require(out['post_target_ids'], 'POST_TARGET_COVER_ABSENT')
    if row['id'] == FRAME:
        pid = relative(ROOT) + '::verify::helper_contracts::' + FRAME + '::{closure#0}.assigns.1'
        p = records[pid]
        require(h['checks']['failure'] == [pid] and len(h['failed_properties']) == 1,
                'FRAME_FOREIGN_OR_MISSING_FAILURE')
        require(p['status'] == 'FAILURE' and p['function'] == pid.rsplit('.assigns.', 1)[0] and
                p['file'] == DIR + '/verify/helper_contracts.rs' and p['line'] == 276 and
                p['description'] == 'Check that *var_9 is assignable', 'FRAME_NAMED_SITE_MISMATCH')
        require(sources[p['file']].splitlines()[275].strip() == 'comparisons = comparisons.wrapping_add(1);',
                'FRAME_SOURCE_WRITE_MISMATCH')
        require(compact(sources[DIR + '.rs'].splitlines()[412]) ==
                '#[cfg_attr(kani,crate::kani::modifies(v_base.wrapping_add(a_pos),v_base.wrapping_add(b_pos)))]',
                'FRAME_SOURCE_WRITESET_MISMATCH')
        out['negative_oracle'] = {'state': 'BOUND', 'failure': p,
            'predeclared_criterion': 'Generated modifies failure for captured comparisons (unchanged manifest placeholder)',
            'relation': 'Comparator F is this exact harness closure; line276 writes the counter outside the two-element write set; sole enforced contract is the metadata symbol',
            'trace_pointer_to_var_9': 'NOT_INDEPENDENTLY_ESTABLISHED; source-reported class/site binding only'}
    return out


def replay(args):
    previous_path = BASE / 'accept-v3/ACCEPT.json'
    previous = read(previous_path)
    require(digest(previous_path.read_bytes()) == '947e1bb9c615d61007fc97ada6a732c098fd69c5d9085268fe5310999b0d4396', 'V3_CHANGED')
    require(previous['source_commit'] == SOURCE and previous['control_commit'] == CONTROL, 'INPUT_PIN_MISMATCH')
    require(digest(args.zip.read_bytes()) == previous['artifact_zip_sha256'], 'ZIP_SHA_MISMATCH')
    source_map = read(BASE / 'accept-v2/SOURCE-MAP.json')
    require(digest((BASE / 'accept-v2/SOURCE-MAP.json').read_bytes()) ==
            'de253321477ef4e6c45c7d90a0afda7bf2e4fdba3c2dbd989aa598dee08be7e7', 'SOURCE_MAP_CHANGED')
    sources = {p: git(args.source, 'show', SOURCE + ':' + p).decode()
               for p in source_map['source_files_sha256']}
    for p, sha in source_map['source_files_sha256'].items():
        require(digest(sources[p].encode()) == sha, 'SOURCE_HASH_MISMATCH:' + p)
    tool_hashes = {}
    for p in TOOL_FILES:
        data = git(args.control, 'show', TOOL + ':' + p)
        require(data == git(args.control, 'show', CONTROL + ':' + p), 'CONTROL_TOOL_DELTA:' + p)
        tool_hashes[p] = digest(data)
    request_data = git(args.control, 'show', CONTROL + ':ch8-prof-off-control/CI-REQUEST.json')
    request = json.loads(request_data)['rows']
    rows = {r['id']: r for r in request}
    symbols = sorted({r['binding']['export_contract_symbol'] for r in previous['rows']
                      if r['binding']['export_contract_symbol']})
    decoded = subprocess.check_output(['c++filt', '-i', '-s', 'rust'], input='\n'.join(symbols) + '\n', text=True).splitlines()
    require(len(decoded) == len(symbols) and all(s != d for s, d in zip(symbols, decoded)), 'DEMANGLE_INCOMPLETE')
    demangled = dict(zip(symbols, decoded))
    values = copy.deepcopy(previous['rows'])
    with zipfile.ZipFile(args.zip) as archive:
        require(len(archive.namelist()) == len(set(archive.namelist())), 'DUPLICATE_ZIP_MEMBER')
        for r in values:
            if r['binding']['wrapper_status'] != 'PENDING':
                continue
            row, mapping = rows[r['id']], source_map['rows'][r['id']]
            try:
                member = r['evidence']['export_member']
                export_data = archive.read(member)
                require(digest(export_data) == r['evidence']['export_sha256'], 'EXPORT_SHA_MISMATCH')
                h = json.loads(export_data)['harnesses'][r['evidence']['harness_index']]
                group_name = member.split('/')[1]
                group = json.loads(archive.read('groups/' + group_name + '/receipt.json'))
                compilation = json.loads(archive.read('groups/' + group_name + '/compile-receipt.json'))
                data = archive.read(r['stdout_binding']['stdout_member'])
                receipt = archive.read(row['id'] + '/receipt.json')
                require(digest(data) == r['stdout_binding']['stdout_sha256'] and
                        digest(receipt) == r['stdout_binding']['receipt_sha256'], 'STDOUT_RECEIPT_SHA_MISMATCH')
                records, _ = bind_stdout(data, row, h, json.loads(receipt), group, compilation)
                binding = bind(row, r, mapping, h, records, demangled, sources)
                r['exact_binding_v4'] = binding
                r['binding']['wrapper_status'] = 'BOUND'
                r['binding']['assurance'] = binding['assurance']
                r['pending_reasons'].remove('EXACT_CONTRACT_WRAPPER_BINDING_PENDING')
                if row['id'] == FRAME:
                    r['pending_reasons'].remove('PREDECLARED_FRAME_ORACLE_BINDING_PENDING')
            except (KeyError, TypeError, ValueError, AttributeError, UnicodeError) as exc:
                r['exact_binding_v4'] = {'state': 'UNKNOWN', 'reason': type(exc).__name__ + ': ' + str(exc)}
                r['unknown_reasons'].append('EXACT_BINDING_V4:' + str(exc))
            r['status'] = 'UNKNOWN' if r['unknown_reasons'] else 'PENDING' if r['pending_reasons'] else 'ACCEPTED'
    by_id = {r['id']: r for r in values}
    # Consumers are evaluated only after all PFC leaf results, with exact instance equality.
    for r in values:
        if 'consumer_leaf' not in r:
            continue
        leaf = by_id[r['consumer_leaf']['id']]
        if 'MATCHING_LEAF_NOT_ACCEPTED' in r['pending_reasons']:
            r['pending_reasons'].remove('MATCHING_LEAF_NOT_ACCEPTED')
        exact = r.get('exact_binding_v4', {}).get('expected_instance_fully_qualified')
        if leaf['status'] != 'ACCEPTED' or exact is None or exact != leaf.get('exact_binding_v4', {}).get('expected_instance_fully_qualified'):
            r['pending_reasons'].append('MATCHING_LEAF_NOT_ACCEPTED')
        r['consumer_leaf'] = {'id': leaf['id'], 'status': leaf['status'], 'exact_instance_match': exact is not None and exact == leaf.get('exact_binding_v4', {}).get('expected_instance_fully_qualified')}
        r['status'] = 'UNKNOWN' if r['unknown_reasons'] else 'PENDING' if r['pending_reasons'] else 'ACCEPTED'
    result = {k: v for k, v in previous.items() if k not in {'rows', 'schema', 'summary', 'g0_input', 'inputs_sha256'}}
    result.update(schema='ch8-prof-off-policy-acceptance-v4', g0_input=G0,
                  v3_assurance='19 accepted rows carried unchanged from hash-pinned reviewed v3; 43 unresolved rows rebound; prior policy decisions retained',
                  v3_input_sha256=digest(previous_path.read_bytes()), tool_commit=TOOL,
                  tool_sources_sha256=tool_hashes, source_files_sha256=source_map['source_files_sha256'],
                  request_sha256=digest(request_data),
                  demangler={'command': ['c++filt', '-i', '-s', 'rust'], 'version': subprocess.check_output(['c++filt', '--version'], text=True).splitlines()[0],
                             'executable_sha256': digest(Path('/usr/bin/c++filt').read_bytes()), 'symbols': demangled},
                  inputs_sha256={p.name: digest(p.read_bytes()) for p in (HERE / 'reclassify_v4.py', HERE / 'test_binding_v4.py')},
                  rows=values)
    result['summary'] = {
        'rows': len(values), 'statuses': dict(collections.Counter(r['status'] for r in values)),
        'positive_statuses': dict(collections.Counter(r['status'] for r in values if r['expected'] == 'SUCCESS')),
        'negative_statuses': dict(collections.Counter(r['status'] for r in values if r['expected'] != 'SUCCESS')),
        'pending_reasons': dict(collections.Counter(p for r in values for p in r['pending_reasons'])),
        'pfc_rows': sum(r['mode'].startswith('PFC:') for r in request),
        'positive_pfc_rows': sum(r['mode'].startswith('PFC:') and r['expected'] == 'SUCCESS' for r in request),
        'replace_consumers': sum(r['mode'].startswith('Replace:') for r in request),
        'bindings': dict(collections.Counter(r['exact_binding_v4']['state'] for r in values if 'exact_binding_v4' in r)),
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('zip', 'control', 'source', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    replay(parser.parse_args())
