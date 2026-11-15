#!/usr/bin/env python3
"""Offline, standard-library-only comparison of untrusted B3 T1b text dumps.
Run with python3 -I. Never executes artifact contents or CBMC/Kani.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

ALLOC = re.compile(r"AllocId\(([0-9]+), ThreadLocalIndex\)")
START = re.compile(r"(?=^Symbol\.\.\.\.\.\.: )", re.M)
LABEL = re.compile(r"^([A-Za-z ]+\.+): ", re.M)
VTABLE = re.compile(r"/\* Kani-internal sanity check: Correct CBMC vtable size for [^\n]*\nhttps://github.com/model-checking/kani/issues/new\?template=bug_report\.md \*/")
TOKEN = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")


SOURCE_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def parse(text):
    pieces = START.split(text)
    prefix = pieces.pop(0)
    blocks = {}
    for block in pieces:
        name = block.split('\n', 1)[0].removeprefix('Symbol......: ')
        if name in blocks:
            raise ValueError('duplicate symbol: ' + name)
        blocks[name] = block
    if not blocks or prefix != '\nSymbols:\n\n':
        raise ValueError('unrecognized symbol dump prefix')
    return prefix, blocks


def field_span(block, label):
    key = label + ': '
    start = 0 if block.startswith(key) else block.find('\n' + key) + 1
    if start < 0 or not block.startswith(key, start):
        raise ValueError('missing field: ' + label)
    start += len(key)
    following = LABEL.search(block, start)
    end = following.start() if following else len(block)
    return start, end


def field(block, label):
    start, end = field_span(block, label)
    return block[start:end].rstrip('\n')


def setfield(block, label, value):
    start, end = field_span(block, label)
    old = block[start:end]
    trailing = old[len(old.rstrip('\n')):]
    return block[:start] + value + trailing + block[end:]


def outside_literals(text, transform):
    # Preserve literal/comment text; only code tokens may be alpha-renamed.
    pattern = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*)', re.S)
    parts = pattern.split(text)
    return ''.join(transform(p) if i % 2 == 0 else p for i, p in enumerate(parts))


def allocation_ids(text):
    if 'AllocId(' not in text:
        return []
    found = []
    def collect(code):
        found.extend(ALLOC.findall(code))
        return code
    outside_literals(text, collect)
    return found


def rename_allocations(text, mapping):
    if 'AllocId(' not in text:
        return text
    return outside_literals(text, lambda code: ALLOC.sub(
        lambda m: f'AllocId({mapping[m[1]]}, ThreadLocalIndex)', code))


def legacy_normalize(text):
    mapping = {}
    def rename(m):
        mapping.setdefault(m[1], len(mapping))
        return f'AllocId({mapping[m[1]]}, ThreadLocalIndex)'
    return ALLOC.sub(rename, text)


def metadata_noise(block, enabled, stats):
    if 'builtin_location' in enabled:
        loc = field(block, 'Location....')
        # Only the two observed shared builtins, exact known source coordinates.
        name = field(block, 'Symbol......')
        allowed = {
            '__CPROVER_malloc_is_new_array': {'file <builtin-library-malloc> line 6', 'file <builtin-library-calloc> line 8', 'file <builtin-library-free> line 11'},
            '__VERIFIER_nondet___CPROVER_bool': {'file <builtin-library-malloc> line 4', 'file <builtin-library-calloc> line 4'},
        }
        if (name in allowed and loc in allowed[name]
                and field(block, 'Module......') == '<built-in-library>'):
            block = setfield(block, 'Location....', 'file <builtin-library-shared-allocation>')
            stats['builtin_location'] += 1
    if 'vtable_comment' in enabled:
        def sub_comment(m):
            old = m.group()
            # Keep hashed tags, MIR shape, type names and ALL non-ID numbers.
            new = re.sub(r'((?:DefId|Ty) \{ id: )[0-9]+', r'\1<ID>', old)
            stats['vtable_comment'] += old != new
            return new
        block = VTABLE.sub(sub_comment, block)
    return block


def local_names(block, locals_by_owner, stats):
    value = field(block, 'Value.......')
    if not value.startswith('{\n'):
        return block
    owner = field(block, 'Symbol......')
    # A C printer may give one local its base name, reserving it from others.
    # Require explicit distinct symbol identities and declaration bindings.
    local_symbols = {}
    for name, entry in locals_by_owner.get(owner, []):
        if 'thread_local' in field(entry, 'Flags.......').split():
            base = field(entry, 'Base name...')
            if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', base):
                local_symbols.setdefault(base, []).append((name, field(entry, 'Type........')))
    decls = value.split('\n\nbb', 1)[0]
    mapping = {}
    for base, candidates in local_symbols.items():
        if len(candidates) < 2:
            continue
        found = []
        for name, typ in candidates:
            printed = name.replace('::', '$$')
            if re.search(r'^  ' + re.escape(typ + ' ' + printed) + r';$', decls, re.M):
                found.append((name, printed))
        missing = [(name, typ) for name, typ in candidates if name not in {n for n,_ in found}]
        if len(missing) != 1 or len(found) != len(candidates)-1:
            continue
        short_name, short_type = missing[0]
        if not re.search(r'^  ' + re.escape(short_type + ' ' + base) + r';$', decls, re.M):
            continue
        # Preserve full qualified identity, including scope and var_N.
        mapping[base] = short_name.replace('::', '$$')
        for name, printed in found:
            mapping[printed] = printed
    if mapping:
        # C tags/labels have separate namespaces; a lexical collision prevents
        # binding this display without a full parser, so leave it unchanged.
        for base in mapping:
            if '$$' in base:
                continue
            collision = [False]
            def check_context(code):
                if (re.search(r'\b(?:struct|union|enum|goto)\s+' + re.escape(base) + r'\b', code)
                        or re.search(r'\b' + re.escape(base) + r'\s*:(?!:)', code)):
                    collision[0] = True
                return code
            outside_literals(value, check_context)
            if collision[0]:
                return block
        def replace(code):
            # A member name (.input) or component designator is not this local.
            return TOKEN.sub(lambda m: mapping.get(m.group(), m.group())
                if not (m.start() and code[m.start()-1] == '.' or code[max(0,m.start()-2):m.start()] == '->') else m.group(), code)
        new_value = outside_literals(value, replace)
        stats['local_names'] += value != new_value
        return setfield(block, 'Value.......', new_value)
    return block


def allocation_map(blocks):
    # Stable use sites anchor identities BEFORE inspecting sorted allocation
    # records/initialize, whose order depends on rustc's transient numbers.
    mapping = {}
    def visit(text):
        for number in allocation_ids(text):
            if number not in mapping:
                mapping[number] = len(mapping)
    definitions = collections.defaultdict(list)
    for name, block in sorted(blocks.items()):
        if m := ALLOC.search(name):
            definitions[m.group(1)].append(block)
        elif name != '__CPROVER_initialize':
            visit(block)
    # Follow initializer/type edges of already anchored nodes in stable order.
    done = set()
    while set(mapping) - done:
        number = next(n for n in mapping if n not in done)
        done.add(number)
        for block in sorted(definitions[number], key=lambda b: ALLOC.sub('AllocId(SELF, ThreadLocalIndex)', b)):
            visit(block)
    remaining = {n for b in blocks.values() for n in allocation_ids(b)} - set(mapping)
    # Unreferenced objects are ordered by complete content, never deduplicated.
    # Ambiguous duplicate content fails closed rather than merging identities.
    while remaining:
        signatures = collections.defaultdict(list)
        for number in remaining:
            def encode(m):
                n = m.group(1)
                return 'AllocId(' + ('SELF' if n == number else 'C'+str(mapping[n]) if n in mapping else 'UNBOUND') + ', ThreadLocalIndex)'
            signatures[''.join(sorted(ALLOC.sub(encode, b) for b in definitions[number]))].append(number)
        signature = min(signatures)
        if len(signatures[signature]) != 1:
            raise ValueError('ambiguous unanchored allocation identities')
        visit('AllocId(' + signatures[signature][0] + ', ThreadLocalIndex)')
        # Dependencies acquire stable identities from this content anchor.
        while set(mapping) - done:
            number = next(n for n in mapping if n not in done)
            done.add(number)
            for block in sorted(definitions[number], key=lambda b: ALLOC.sub('AllocId(SELF, ThreadLocalIndex)', b)):
                visit(block)
        remaining -= set(mapping)
    if len(set(mapping.values())) != len(mapping):
        raise ValueError('non-injective allocation map')
    return mapping


def initialize_order(block, blocks, stats):
    value = field(block, 'Value.......')
    if not value:
        return block
    lines = value.splitlines(keepends=True)
    # Sort only maximal runs of direct static allocation assignments with a
    # restricted side-effect-free address/constant RHS. Never reorder reads,
    # calls, indirect writes, guards, labels or arbitrary initialization.
    allocation_symbols = {}
    for name, entry in blocks.items():
        if ALLOC.search(name) and not name.startswith('tag-') and 'static_lifetime' in field(entry, 'Flags.......').split():
            allocation_symbols[name.replace('.', '_').replace('::', '$$')] = entry
    def assignment(line):
        match = re.fullmatch(r'  ([^\n]+) = (.+);\n', line, re.S)
        if not match or match[1] not in allocation_symbols:
            return None
        lhs, rhs = match.groups()
        # Check exact initializer binding and immutable-allocation type.
        entry = allocation_symbols[lhs]
        if rhs != field(entry, 'Value.......') or not field(entry, 'Type........').startswith('const '):
            return None
        # The first operand of byte_extract is the POINTER VALUE (&object),
        # never *pointer or an object's stored bytes. Both offsets are zero.
        # Taking the address of existing static storage does not read its value.
        scrub = rhs
        for ident in sorted(allocation_symbols, key=len, reverse=True):
            scrub = scrub.replace('&'+ident, 'ADDRESS')
        byte_array = r"\{[ 0-9,]*\}"
        address_value = (r"byte_extract_little_endian\(\((?:un)?signed char \*\)"
            r"\(\(unsigned char \*\)ADDRESS \+ 0\), 0, (?:un)?signed char \*\)")
        item = r"(?:" + byte_array + '|' + address_value + ')'
        aggregate = r"\{\s*\.[0-9]+=" + item + r"(?:,\s*\.[0-9]+=" + item + r")*\s*\}"
        if re.fullmatch(aggregate, scrub) is None:
            return None
        return lhs
    # Treat a multiline allocation aggregate as one statement. Its entire RHS
    # must still pass the pure grammar and exact symbol-Value binding above.
    units = []
    i = 0
    while i < len(lines):
        match = re.match(r'  ([^\n]+) = ', lines[i])
        if match and match[1] in allocation_symbols:
            end = i+1
            while not lines[end-1].endswith(';\n') and end < len(lines):
                end += 1
            units.append(''.join(lines[i:end]))
            i = end
        else:
            units.append(lines[i])
            i += 1
    lines = units
    i = 0
    while i < len(lines):
        if assignment(lines[i]) is None:
            i += 1
            continue
        end = i+1
        while end < len(lines) and assignment(lines[end]) is not None:
            end += 1
        run = lines[i:end]
        targets = [assignment(line) for line in run]
        if len(set(targets)) != len(targets):
            raise ValueError('duplicate allocation initialization target')
        ordered = sorted(run, key=assignment)
        if ordered != run:
            stats['initialize_order'] += 1
        lines[i:end] = ordered
        i = end
    return setfield(block, 'Value.......', ''.join(lines).rstrip('\n'))


POLICIES = ('builtin_location', 'vtable_comment', 'allocations', 'initialize_order', 'local_names')


def normalize(text, enabled=POLICIES):
    prefix, blocks = parse(text)
    stats = collections.Counter()
    blocks = {n:metadata_noise(b, enabled, stats) for n,b in blocks.items()}
    if 'local_names' in enabled:
        locals_by_owner = collections.defaultdict(list)
        for n,b in blocks.items():
            if n.startswith('_R') and '::' in n:
                locals_by_owner[n.split('::',1)[0]].append((n,b))
        blocks = {n:local_names(b, locals_by_owner, stats) for n,b in blocks.items()}
    mapping = allocation_map(blocks) if 'allocations' in enabled else {}
    if mapping:
        rename = lambda s: rename_allocations(s, mapping)
        blocks = {rename(n):rename(b) for n,b in blocks.items()}
        stats['allocations'] = len(mapping)
    if 'initialize_order' in enabled and '__CPROVER_initialize' in blocks:
        blocks['__CPROVER_initialize'] = initialize_order(blocks['__CPROVER_initialize'], blocks, stats)
    return prefix + ''.join(b for n,b in sorted(blocks.items())), dict(stats)


def stages(text):
    # Legacy baseline is measured independently: never feed its unrestricted
    # substitutions into the new normalizer (literals are semantic data).
    prefix, blocks = parse(text)
    snapshots = {'legacy_first_occurrence': sha(legacy_normalize(text))}
    stats = collections.Counter()
    def snapshot(name):
        rendered = prefix + ''.join(blocks.values())
        snapshots[name] = sha(legacy_normalize(rendered) if name in ('builtin_location','vtable_comment') else rendered)
        return rendered
    for policy in ('builtin_location', 'vtable_comment'):
        blocks = {n:metadata_noise(b, (policy,), stats) for n,b in blocks.items()}
        snapshot(policy)
    mapping = allocation_map(blocks)
    rename = lambda s: rename_allocations(s, mapping)
    blocks = dict(sorted((rename(n),rename(b)) for n,b in blocks.items()))
    stats['allocations'] = len(mapping)
    snapshot('allocations')
    if '__CPROVER_initialize' in blocks:
        blocks['__CPROVER_initialize'] = initialize_order(blocks['__CPROVER_initialize'], blocks, stats)
    snapshot('initialize_order')
    locals_by_owner = collections.defaultdict(list)
    for n,b in blocks.items():
        if n.startswith('_R') and '::' in n:
            locals_by_owner[n.split('::',1)[0]].append((n,b))
    blocks = {n:local_names(b, locals_by_owner, stats) for n,b in blocks.items()}
    rendered = snapshot('local_names')
    return rendered, snapshots, dict(stats)


def check_control(a, b):
    pa, ba = parse(a)
    pb, bb = parse(b)
    if pa != pb or set(ba) != set(bb):
        return {'valid': False, 'reason': 'control inventory changed'}
    changed = [n for n in ba if ba[n] != bb[n]]
    if len(changed) != 1:
        return {'valid': False, 'reason': 'control must change exactly one wrapper symbol', 'changed': changed}
    wrapper = changed[0]
    if not wrapper.startswith('tag-') or not wrapper.endswith('::zst_array'):
        return {'valid': False, 'reason': 'unexpected wrapper name'}
    tag = wrapper.removeprefix('tag-')
    parent = 'tag-' + tag.removesuffix('::zst_array')
    expected_union = 'union ' + parent.removeprefix('tag-') + ' { unsigned char bytes[8]; struct ' + tag + ' zst_array; }'
    # Resolve the actual tagged union -> component -> wrapper edge in the dump.
    # No external kani metadata or wrapper Pretty/Base-name requirement.
    if parent not in ba or ba[parent] != bb[parent] or field(ba[parent], 'Type........') != expected_union:
        return {'valid': False, 'reason': 'missing union-to-wrapper type edge'}
    if field(ba[parent], 'Pretty name.') != 'ArrayUnion' or 'type' not in field(ba[parent], 'Flags.......').split():
        return {'valid': False, 'reason': 'parent is not the ArrayUnion type'}
    if 'tag-Unit' not in ba or ba['tag-Unit'] != bb['tag-Unit'] or field(ba['tag-Unit'], 'Type........') != 'struct Unit { }':
        return {'valid': False, 'reason': 'Unit is not an unchanged empty struct'}
    old = 'struct ' + tag + ' { struct Unit zst_array[2]; unsigned long int zst_array_padding; }'
    new = 'struct ' + tag + ' { struct Unit zst_array; unsigned long int zst_array_padding; }'
    if field(ba[wrapper], 'Type........') != old or field(bb[wrapper], 'Type........') != new:
        return {'valid': False, 'reason': 'payload transition or padding differs from [(); 2] -> Unit'}
    if 'type' not in field(ba[wrapper], 'Flags.......').split() or setfield(ba[wrapper], 'Type........', new) != bb[wrapper]:
        return {'valid': False, 'reason': 'off-type wrapper text changed'}
    return {'valid': True, 'parent_symbol': parent, 'wrapper_symbol': wrapper,
            'union_type': expected_union, 'old_type': old, 'new_type': new,
            'unit_type': 'struct Unit { }', 'padding_type': 'unsigned long int',
            'binding': 'unchanged tagged union Type contains the exact wrapper component; Unit empty in dump',
            'scope': 'symbol dumps; goto-functions unavailable'}


def safe_read(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError('invalid artifact-relative path')
    path = (root / relative).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError('artifact path escapes root')
    return path.read_bytes()


def run(root, output):
    root = root.resolve(strict=True)
    output = output.resolve()
    if output.is_relative_to(root):
        raise ValueError('output must be outside untrusted artifact')
    index_bytes = safe_read(root, 'INDEX.json')
    result_bytes = safe_read(root, 'RESULT.json')
    index = json.loads(index_bytes)
    original = json.loads(result_bytes)
    if original['run_id'] != '43708572925' and original['run_id'] != 43708572925:
        raise ValueError('wrong run id')
    if len(index) != 393 or collections.Counter(e['kind'] for e in index.values()) != {'final':131,'linked':131,'symtab':131}:
        raise ValueError('incomplete model inventory')
    source_indexes = {}
    source_records = {}
    for arm in ('A1','A2','B1'):
        data = safe_read(root, f'input/{arm}/index.json')
        if sha(data) != original['input_indexes'][arm]:
            raise ValueError('source index digest mismatch')
        source_indexes[arm] = sha(data)
        source_index = json.loads(data)
        if source_index.get('complete') is not True:
            raise ValueError('source index incomplete')
        source_records[arm] = source_index['records']
        if set(index) != {k for k,v in source_records[arm].items() if v['kind'] in ('final','linked','symtab')}:
            raise ValueError('source/model inventory mismatch')
    output.mkdir(parents=True, exist_ok=True)
    cache = {}
    records = []
    aa = collections.defaultdict(collections.Counter)
    pair_counts = collections.defaultdict(collections.Counter)
    control = []
    residual = []
    unknown = []
    verified = 0
    total_bytes = 0
    empty_functions = 0
    commands_by_stdout = collections.defaultdict(list)
    for path in sorted((root/'commands').glob('*.json')):
        command = json.loads(path.read_bytes())
        if command.get('stdout'):
            commands_by_stdout[command['stdout']].append(command)
    dump_commands = 0
    def get_dump(mode, mode_name, arm, key):
        nonlocal verified, total_bytes, empty_functions, dump_commands
        data = safe_read(root, mode['raw'])
        if sha(data) != mode['raw_sha256']:
            raise ValueError('dump digest mismatch: ' + mode['raw'])
        entries = commands_by_stdout.get(mode['raw'], [])
        if len(entries) != 1 or entries[0].get('state') != 'EXIT' or entries[0].get('exit') != 0:
            raise ValueError('missing or failed dump command: ' + mode['raw'])
        command = entries[0]
        source_record = source_records[arm][key]
        if source_record['sha256'] != index[key]['arms'][arm]['input_sha256']:
            raise ValueError('input model hash/source index mismatch')
        expected_suffix = '/' + arm + '/' + source_record['path']
        if not any(arg.endswith(expected_suffix) for arg in command['argv'] if isinstance(arg,str)):
            raise ValueError('dump command input/source model path mismatch')
        if '--show-' + mode_name not in command['argv']:

            raise ValueError('dump mode/command mismatch')
        stderr = safe_read(root, command['stderr'])
        if stderr:
            raise ValueError('nonempty stderr: ' + command['stderr'])
        dump_commands += 1
        verified += 1
        total_bytes += len(data)
        empty_functions += mode_name == 'goto-functions' and not data
        return data
    for pos, (key, entry) in enumerate(sorted(index.items()), 1):
        if set(entry['arms']) != {'A1','A2','B1'}:
            raise ValueError('arm inventory mismatch')
        row = {'key':key, 'kind':entry['kind'], 'is_control':'/control/' in key, 'arms':{}}
        texts = {}
        for arm in ('A1','A2','B1'):
            modes = entry['arms'][arm]['modes']
            if set(modes) != {'symbol-table','goto-functions'}:
                raise ValueError('mode inventory mismatch')
            raw = get_dump(modes['symbol-table'], 'symbol-table', arm, key)
            functions = get_dump(modes['goto-functions'], 'goto-functions', arm, key)
            digest = sha(raw)
            text = raw.decode('utf-8', errors='strict')
            if digest not in cache:
                try:
                    normalized, hashes, stats = stages(text)
                    cache[digest] = {'hashes':hashes,'stats':stats}
                except ValueError as error:
                    cache[digest] = {'error':str(error)}
            cached = cache[digest]
            if 'error' in cached:
                unknown.append({'key':key,'arm':arm,'error':cached['error']})
                normalized, hashes, stats = text, {'local_names':digest}, {}
            else:
                hashes, stats = cached['hashes'], cached['stats']
                if hashes['legacy_first_occurrence'] != modes['symbol-table']['normalized_sha256']:
                    raise ValueError('legacy normalization digest mismatch')
                # Only render again when comparing a genuine residual/control.
                normalized = None
            row['arms'][arm] = {'raw_symbol_sha256':digest,'raw_functions_sha256':sha(functions),
                'functions_bytes':len(functions),'input_sha256':entry['arms'][arm]['input_sha256'],
                'stage_sha256':hashes,'normalizations':stats}
            texts[arm] = (text, normalized)
        arms = row['arms']
        for stage in next(iter(arms.values()))['stage_sha256']:
            eq = arms['A1']['stage_sha256'][stage] == arms['A2']['stage_sha256'][stage]
            aa[stage][entry['kind']] += eq
        for left,right in [('A1','A2'),('A1','B1'),('A2','B1')]:
            eq = arms[left]['stage_sha256']['local_names'] == arms[right]['stage_sha256']['local_names']
            row[left+'_'+right+'_symbols_equal'] = eq
            pair_counts[left+'_'+right][entry['kind']] += eq
        if not row['A1_A2_symbols_equal'] or not row['A1_B1_symbols_equal'] or not row['A2_B1_symbols_equal']:
            import difflib
            rendered = {arm:stages(texts[arm][0])[0] for arm in texts}
            for left,right in [('A1','A2'),('A1','B1'),('A2','B1')]:
                if rendered[left] != rendered[right]:
                    name = sha(key)[:24] + '.'+left+'-'+right+'.diff'
                    diff = ''.join(difflib.unified_diff(rendered[left].splitlines(True),rendered[right].splitlines(True),fromfile=left+'/'+key,tofile=right+'/'+key))
                    (output/name).write_text(diff)
                    residual.append({'key':key,'pair':left+'-'+right,'control':row['is_control'],'diff':name,'diff_sha256':sha(diff)})
            if row['is_control']:
                gate = check_control(rendered['A1'], rendered['B1'])
                gate2 = check_control(rendered['A2'], rendered['B1'])
                gate.update(key=key, aa_equal=row['A1_A2_symbols_equal'], a2b_valid=gate2['valid'])
                control.append(gate)
        records.append(row)
        if pos%25 == 0:
            print(json.dumps({'processed':pos,'unique_dumps':len(cache),'normalization_errors':len(unknown)}),flush=True)
    noncontrol_residual = [e for e in residual if not e['control']]
    valid_control = len(control)==3 and all(c['valid'] and c['a2b_valid'] and c['aa_equal'] for c in control)
    display_status = 'INCONCLUSIVE_AA' if unknown or pair_counts['A1_A2'] != {'final':131,'linked':131,'symtab':131} else 'OTHER_CHANGES' if noncontrol_residual else 'MODELS_EQUAL'
    gaps = []
    if empty_functions:
        gaps.append({'code':'EMPTY_GOTO_FUNCTION_DUMPS','count':empty_functions,'expected':1179,
            'reason':'exit 0 and empty bytes do not expose compiled GOTO bodies; symbol tables contain compiled markers'})
    if not valid_control:
        gaps.append({'code':'INVALID_CONTROL_SYMBOL_GATE'})
    result = {'normalizer_sha256':SOURCE_SHA256,'schema':'b3-t1b-offline-v1','run_id':43708572925,'base_t0':'21d68cc4c0a93f36c64ccfafe3a0bb79f171ebf1',
        'status':'INCONCLUSIVE_AA' if gaps or unknown else display_status,
        'symbol_dump_perf_status':display_status,'artifact_index_sha256':sha(index_bytes),'original_result_sha256':sha(result_bytes),
        'artifact_root':str(root),'source_indexes_sha256':source_indexes,'source_reported_tool':original['tool'],
        'hash_checked_raw_dump_files':verified,'hash_checked_raw_dump_bytes':total_bytes,'checked_dump_commands':dump_commands,
        'model_counts':dict(collections.Counter(e['kind'] for e in index.values())),
        'AA_EQUAL_BY_CUMULATIVE_POLICY':{k:dict(v) for k,v in aa.items()},'PAIR_SYMBOL_EQUAL':{k:dict(v) for k,v in pair_counts.items()},
        'control':control,'control_symbol_gate_valid':valid_control,'residual_differences':residual,
        'noncontrol_residual_differences':noncontrol_residual,'normalization_errors':unknown,'evidence_gaps':gaps,
        'normalization_policies':list(POLICIES),'unique_symbol_dump_contents':len(cache),
        'original_result_preserved':True,'no_sat_or_formal_proof_or_harmlessness_credit':True,'records':records}
    (output/'RESULT-OFFLINE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ['status','symbol_dump_perf_status','AA_EQUAL_BY_CUMULATIVE_POLICY','PAIR_SYMBOL_EQUAL','evidence_gaps','control_symbol_gate_valid','unique_symbol_dump_contents']},indent=2),flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('artifact',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args = parser.parse_args()
    run(args.artifact,args.output)
