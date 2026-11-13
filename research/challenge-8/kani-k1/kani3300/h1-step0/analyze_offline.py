#!/usr/bin/env python3
"""Narrow extension of ../d1a/analyze_offline.py's bounded text parser.
No compiler, subprocess, network, exporter, binary GOTO decoder or solver.
Coordinates: physical 1-based lines, 0-based UTF-8 byte offsets/lengths.
Run: python3 research/challenge-8/kani-k1/kani3300/h1-step0/analyze_offline.py
"""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import resource
import signal
import time

HERE = Path(__file__).resolve().parent
D1A = HERE.parent / 'd1a'
ROOT = Path('/root/kani3300-d1p-ci')
PINS = {'r1-skip': '56cbc5c4a479bc3fb25310b14fcf279d90581a02',
        'r6b': '405c1f059264d8f7cedeeaa01c6d4ad6867a419e'}
AUTH_SHA = '2a457ede0d8ff712719580a8b0227719972c77e61c872695dc4de69249c7396a'
CAP = 8 * 1024**2
DYNAMIC = r'dynamic_object(?:\$\d+)?'
VERSION = DYNAMIC + r'#\d+'
STARTED = time.monotonic()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked(path, expected, cap=CAP):
    if not path.is_file():
        raise ValueError(f'STOP missing file: {path}')
    if path.stat().st_size > cap:
        raise ValueError(f'INCOMPLETE file cap: {path}')
    data = path.read_bytes()
    if sha(data) != expected['sha256'] or len(data) != expected['bytes']:
        raise ValueError(f'STOP identity sha256/bytes: {path}')
    return data


def norm(text):
    # Whitespace only. Do not erase SSA/call suffixes, casts, fields or offsets.
    return re.sub(r'\s+', ' ', text).strip()


def validate_identity(identity, pin, key):
    for field, expected in [('source_sha', PINS[key]), ('source_tree', pin['source_tree']),
                            ('ci_sha', pin['ci_commit']), ('ci_tree', pin['ci_tree']),
                            ('run_id', '43314208878'), ('run_attempt', '1'), ('job', key)]:
        if identity.get(field) != expected:
            raise ValueError(f'STOP wrong pin {key}/{field}')


def validate_receipt(receipt, raw, executable_sha):
    s = receipt.get('streams', {}).get('stdout', {})
    if (receipt.get('collector_status') != 'COMPLETE' or receipt.get('stream_complete') is not True
            or s.get('truncated') is not False or s.get('dropped_bytes') != 0
            or s.get('emitted_bytes') != len(raw) or s.get('total_bytes') != len(raw)
            or receipt.get('limiter_reason') is not None or receipt.get('original_rc') != 0):
        raise ValueError('INCOMPLETE stdout receipt/coverage')
    if receipt.get('executable_sha256') != executable_sha:
        raise ValueError('STOP wrong receipt executable_sha256')


def coord(row):
    return {k: row[k] for k in ('line', 'byte_offset', 'byte_length', 'pc',
                                'source_location', 'function', 'printed_id', 'ignore', 'kind')}


def parse(raw, cap=CAP):
    if len(raw) > cap:
        return [], ['INCOMPLETE byte cap']
    rows, issues = [], []
    active, current, prefixes, ended = False, None, 0, False
    pc, location, offset = None, None, 0
    for line, chunk in enumerate(raw.splitlines(keepends=True), 1):
        text = chunk.decode('utf-8', 'strict').rstrip('\r\n')
        if text == 'Program constraints:':
            prefixes += 1
            active, current = True, None
        elif active:
            match = re.fullmatch(r'// (\d+) (.*)', text)
            start = re.fullmatch(r'\((sliced|\d+)\) (.*)', text)
            guard = re.fullmatch(r'\s+guard: (.*)', text)
            if match:
                pc, location, current = int(match[1]), match[2], None
            elif start:
                current = dict(line=line, byte_offset=offset, byte_length=len(chunk),
                               pc=pc, source_location=location, term=start[2],
                               ignore=start[1] == 'sliced', printed_id=start[1], guard=None)
                rows.append(current)
            elif guard and current:
                current['guard'] = guard[1]
                current['guard_line'] = line
                current['guard_byte_offset'] = offset
                current = None
            elif text == ',':
                active, current, ended = False, None, True
            elif current and text.startswith('    '):
                current['term'] += '\n' + text
                current['byte_length'] += len(chunk)
            elif text.strip():
                issues.append(f'UNKNOWN line {line}: {text[:120]}')
        offset += len(chunk)
    if prefixes != 1 or not ended or active:
        issues.append(f'INCOMPLETE framing prefixes={prefixes} ended={ended} active={active}')
    for r in rows:
        term = r['term']
        call = re.match(r'([A-Z_]+)\(', term)
        if call:
            r['kind'] = call[1] if call[1] in ('ASSERT', 'ASSUME', 'CONSTRAINT', 'SHARED_READ', 'SHARED_WRITE') else 'UNKNOWN_KIND'
        elif ' == ' in term:
            r['kind'] = 'guard_assignment' if re.match(r'\\guard#\d+ == ', term) else 'assignment'
        else:
            r['kind'] = 'UNKNOWN_KIND'
        if r['kind'] == 'UNKNOWN_KIND':
            issues.append(f'UNKNOWN_KIND line {r["line"]}')
        r['function'] = (r['source_location'] or '').partition(' function ')[2] or None
    return rows, issues


def indexed(text):
    """Only adjacent version[index] reads/stores, balanced [] including nested indices.
    WITH [index:=value], byte_extract/update and array literals are not index reads.
    Returns (version, index, start, end); ambiguous/unclosed index fails closed.
    """
    out, issues = [], []
    for m in re.finditer(r'(' + VERSION + r')\[', text):
        depth, end = 1, m.end()
        while end < len(text) and depth:
            depth += (text[end] == '[') - (text[end] == ']')
            end += 1
        if depth:
            issues.append('INCOMPLETE ambiguous/unclosed index')
        else:
            out.append((m[1], text[m.end():end-1], m.start(), end))
    return out, issues


def definition_class(definition):
    if definition is None:
        return 'UNKNOWN_MISSING_DEFINITION'
    if definition['ignore']:
        return 'SLICED_FREE_VERSION_CANDIDATE'
    if definition['rhs'] == 'ARRAY_OF(NULL)' and not definition['guard']:
        return 'RETAINED_NULL_CONSTANT'
    return 'RETAINED_INITIALIZED_WITH_OR_SYMBOLIC_NOT_PROVEN_CONSTANT'


def goto_records(text):
    out, pc, loc = [], None, None
    for line, t in enumerate(text.splitlines(), 1):
        m = re.fullmatch(r'\s*// (\d+) (.*)', t)
        if m:
            pc, loc = int(m[1]), m[2]
        elif t.strip() and not t.strip().startswith('//') and pc is not None:
            out.append(dict(line=line, pc=pc, source_location=loc, text=t.strip()))
            pc = None
    return out


def summarize(rows, issues, gtext, stext):
    assertions = [i for i, r in enumerate(rows) if r['kind'] == 'ASSERT']
    last = assertions[-1] if assertions else -1
    if last < 0:
        issues.append('INCOMPLETE no visible ASSERT')
    tables, definitions, others = {}, {}, []
    for r in rows:
        t = r['term']
        m = re.fullmatch(r'(.+)\.\.(contract_frees|allocated|deallocated)\.\.elems == (' + DYNAMIC + r')', t)
        if m:
            root = m[3]
            binding = dict(owner_ssa=m[1], field=m[2], binding=coord(r), expression=t)
            tables.setdefault(root, dict(root=root, aliases=[], definitions=[]))['aliases'].append(binding)
        d = re.fullmatch(r'(' + VERSION + r') == (.*)', t, re.S)
        if d:
            if d[1] in definitions:
                issues.append('INCOMPLETE duplicate definition ' + d[1])
            rhs = d[2]
            definitions[d[1]] = dict(version=d[1], rhs=rhs, guard=r['guard'],
                ignore=r['ignore'], definition=coord(r), dependencies=sorted(set(re.findall(VERSION, rhs))),
                form='WITH' if ' WITH ' in rhs else 'ARRAY_OF' if rhs.startswith('ARRAY_OF(') else 'OTHER')
    g = goto_records(gtext)
    mirrors = [x for x in g if 'IF ' in x['text'] and 'set.allocated.elems' in x['text']]
    type_lines = [dict(line=i, text=t) for i,t in enumerate(stext.splitlines(), 1)
                  if t.startswith('Type') and 'nof_elems;' in t and 'void **elems' in t]
    allocation = [x for x in g if 'statement="allocate"' in x['text'] and 'nof_objects * 8' in x['text']]
    architecture = {}
    symbol_lines = stext.splitlines()
    for field in ('pointer_width','char_width'):
        head = next((i for i,t in enumerate(symbol_lines)
                     if t=='Symbol......: __CPROVER_architecture_'+field), None)
        values = [(i,t) for i,t in enumerate(symbol_lines[head:head+10],head)
                  if t.startswith('Value.......: ')] if head is not None else []
        if values:
            i,t = values[0]
            match = re.fullmatch(r'Value.......: \(__CPROVER_integer\)(\d+)',t)
            architecture[field] = dict(line=i+1,text=t,value=int(match[1]) if match else None)
    for root, table in tables.items():
        for v, d in definitions.items():
            if v.rsplit('#', 1)[0] == root:
                table['definitions'].append(d | {'classification': definition_class(d),
                    'source_value_shape': 'INITIALIZED_NULL' if d['rhs']=='ARRAY_OF(NULL)' else
                        'INITIALIZED_WITH_ADDRESS_OR_NULL_UPDATES' if d['form']=='WITH' else 'UNKNOWN',
                    'constant_bitvector': 'YES' if definition_class(d)=='RETAINED_NULL_CONSTANT' else 'UNKNOWN'})
        table['shared_events'] = [coord(r) | {'term': r['term']} for r in rows
                                  if r['kind'] in ('SHARED_READ','SHARED_WRITE') and
                                  re.search(r'\('+re.escape(root)+r'#\d+\)',r['term'])]
        table['pointer_aliases'] = [coord(r) | {'term':r['term']} for r in rows
                                   if r['kind']=='assignment' and not r['term'].startswith(root+'#')
                                   and re.search(r' == (?:\(const void \*\))?'+re.escape(root)+r'$',r['term'])]
        # Independently bind each root to its indexed-set invocation using the
        # nearest creation-function object_bits/nof_objects assignments, not $12 reuse.
        first = next((r for r in rows if r['term'].startswith(root+'#1 == ')), None)
        creation = [r for r in rows if first and r['line'] < first['line'] and
                    r['function'] == '__CPROVER_contracts_obj_set_create_indexed_by_object_id']
        sizes = [r for r in creation if re.match(r'nof_objects!.* == \d+$', r['term'])]
        bits = [r for r in creation if re.match(r'object_bits!.* == \d+$', r['term'])]
        n, b = (int(sizes[-1]['term'].split(' == ')[1]) if sizes else None,
                int(bits[-1]['term'].split(' == ')[1]) if bits else None)
        width_known = bool(type_lines and allocation and
                           architecture.get('pointer_width',{}).get('value')==64 and
                           architecture.get('char_width',{}).get('value')==8)
        table.update(element_type='const void * (source/type-derived)', element_width_bits=64 if width_known else None,
            extent_elements=n, extent_bytes=n*8 if n and width_known else None,
            capacity_bits=n*64 if n and width_known else None, object_bits=b,
            architecture=architecture,
            width_assurance='TYPE_DERIVED: architecture pointer_width64/char_width8, void **elems and allocate(nof_objects * 8); not converter measurement',
            creation_context=bits[-1]['term'].split(' == ')[0] if bits else 'UNKNOWN',
            size_coordinates=coord(sizes[-1]) if sizes else None,
            bit_coordinates=coord(bits[-1]) if bits else None,
            goto_allocation_candidates=allocation, symbol_type=type_lines,
            write_set_scope='requires/ensures/contract owner from exact aliases; dynamic call extent UNKNOWN beyond captured SSA',
            actual_flattened_width_bits='UNKNOWN (converter not run/captured)',
            free_bits_transition='PROVISIONAL: sliced definition does not prove fresh full-width converter allocation')
    groups = defaultdict(list)
    counts, ops = Counter(), Counter()
    for i, r in enumerate(rows):
        period = 'through_last_ASSERT' if i <= last else 'after_last_ASSERT'
        counts[(period, 'ignored' if r['ignore'] else 'retained', r['kind'])] += 1
        for field in ('term', 'guard'):
            text = r[field] or ''
            for op in re.findall(r'byte_(?:extract|update)\w*|\bWITH\b', text):
                ops[(period, 'ignored' if r['ignore'] else 'retained', field, op)] += 1
            matches, errors = indexed(text)
            issues.extend(f'{x} line {r["line"]}' for x in errors)
            for v, idx, start, end in matches:
                root = v.rsplit('#', 1)[0]
                if root not in tables:
                    others.append(dict(version=v, index=idx, location=coord(r), reason='UNBOUND_DYNAMIC_OBJECT'))
                    continue
                is_store = field == 'term' and r['kind'] in ('assignment', 'guard_assignment') and ' == ' in text and end <= text.index(' == ')
                kind = 'lhs_store' if is_store else 'index_read'
                width = tables[root]['element_width_bits']
                key = (v, idx, f'const void * (rendered); {width if width else "UNKNOWN"} bits (TYPE_DERIVED)')
                candidate = (not is_store and i <= last and
                             (r['kind'] == 'guard_assignment' or not r['ignore']))
                groups[key].append(dict(**coord(r), field=field, period=period,
                    use_kind=kind, candidate=candidate,
                    inclusion_reason=('GOTO_MIRROR_PROXY' if r['kind']=='guard_assignment' else
                                      'RETAINED_PRINTED_EXPRESSION' if not r['ignore'] else 'IGNORED_NON_GUARD_EXCLUDED'),
                    guard=r['guard']))
    entries = []
    for (v, idx, typ), occurrences in groups.items():
        d = definitions.get(v)
        if d is None:
            issues.append('UNKNOWN_MISSING_DEFINITION ' + v)
        mirror = [x for x in mirrors if any(
            x['source_location'] == p['source_location'] for p in occurrences)]
        entries.append(dict(table_version=v, index_expression=idx, canonical_index=norm(idx),
            result_type=typ, owner=tables[v.rsplit('#',1)[0]]['aliases'],
            definition_class=definition_class(d),
            definition=coord_from_def(d), occurrences=occurrences,
            candidate_occurrences=sum(p['candidate'] for p in occurrences),
            mirror_candidates=mirror,
            mirror_assurance='POSSIBLE_SOURCE_RULE_MATCH; source/function match, instruction PC renumbered; no per-invocation GOTO/L2 binding',
            index_class='POINTER_OBJECT_WITH_64_BIT_CAST' if re.match(r'\((?:signed )?long int\)__CPROVER_POINTER_OBJECT\(', idx) else 'UNKNOWN',
            converted_index_constant='UNKNOWN: object encoding and converter simplification not captured'))
    entries.sort(key=lambda e:(e['table_version'], e['index_expression']))
    selected = [e for e in entries if e['candidate_occurrences']]
    free = [e for e in selected if e['definition_class']=='SLICED_FREE_VERSION_CANDIDATE']
    retained = [e for e in selected if e['definition_class'].startswith('RETAINED_')]
    canonical_keys = {(e['table_version'],e['canonical_index'],e['result_type']) for e in selected}
    canonical_free = {(e['table_version'],e['canonical_index'],e['result_type']) for e in free}
    canonical_retained = {(e['table_version'],e['canonical_index'],e['result_type']) for e in retained}
    free_versions = {e['table_version'] for e in free}
    aggregate = dict(candidate_distinct_raw=len(selected), candidate_distinct_canonical=len(canonical_keys),
        candidate_occurrences=sum(e['candidate_occurrences'] for e in selected),
        canonical_D_free_version_read_candidates=len(canonical_free),
        canonical_C_retained_version_candidates=len(canonical_retained),
        C_retained_version_candidates=len(retained), C_constant_confirmed=sum(e['definition_class']=='RETAINED_NULL_CONSTANT' for e in retained),
        C_constant_actual='UNKNOWN; retained WITH/addresses are not automatically constant bitvectors',
        D_free_version_read_candidates=len(free), S_free_table_version_candidates=len(free_versions),
        free_first_read_per_version=len(free_versions), free_extra_distinct_reads_same_version=len(free)-len(free_versions),
        free_repeated_occurrences_same_read=sum(e['candidate_occurrences']-1 for e in free),
        retained_first_read_per_version=len({e['table_version'] for e in retained}),
        retained_extra_distinct_reads_same_version=len(retained)-len({e['table_version'] for e in retained}),
        retained_repeated_occurrences_same_read=sum(e['candidate_occurrences']-1 for e in retained),
        actual_C_D_S='UNKNOWN; printed proxy membership exact, converter membership/cache misses not captured',
        actual_ranges='No finite upper bound from program-only coverage; zero misses not excluded by text alone')
    use_counts = Counter((p['period'], p['field'], p['use_kind'], p['kind'],
                          'ignored' if p['ignore'] else 'retained', p['candidate'])
                         for e in entries for p in e['occurrences'])
    guard_counts = Counter(('through_last_ASSERT' if i <= last else 'after_last_ASSERT',
                           'ignored' if r['ignore'] else 'retained')
                          for i,r in enumerate(rows) if r['guard'] is not None)
    return dict(status='COMPLETE_TEXT_ONLY' if not issues else 'INCOMPLETE', issues=issues[:40],
        issue_count=len(issues), printed_all=len(rows), printed_retained=sum(not r['ignore'] for r in rows),
        printed_ignored=sum(r['ignore'] for r in rows), guard_lines=sum(r['guard'] is not None for r in rows),
        last_visible_ASSERT=coord(rows[last]) if last >= 0 else None,
        category_counts=[dict(period=p, status=s, kind=k, count=n) for (p,s,k),n in sorted(counts.items())],
        guard_line_counts=[dict(period=p,status=s,count=n) for (p,s),n in sorted(guard_counts.items())],
        other_operators=[dict(period=p,status=s,field=f,operator=o,count=n) for (p,s,f,o),n in sorted(ops.items())],
        table_use_counts=[dict(period=p,field=f,use_kind=u,record_kind=k,status=s,candidate=c,count=n)
                          for (p,f,u,k,s,c),n in sorted(use_counts.items())],
        aggregate=aggregate, reads=entries, unbound_indexed_dynamic_objects=others,
        tables=list(tables.values()), mirror_static_candidates=mirrors,
        coverage='Entire bounded printed stream; UNKNOWN_GOTO_COVERAGE. No GOTO conversion count or cache-miss claim.' )


def coord_from_def(d):
    return d['definition'] if d else None


def cpu_cap(*_):
    raise ValueError('INCOMPLETE CPU cap')


def warning_binding(stream, gtext, stext):
    g = goto_records(gtext)
    data = []
    for op in ('add', 'sub'):
        symbol = '_RNvMs9_NtCseOU9pHvofFg_4core3numj14saturating_' + op
        lines = gtext.splitlines()
        head = next((i for i,t in enumerate(lines) if t.endswith('/* '+symbol+' */')), None)
        end = next((i for i in range(head+1,len(lines)) if 'END_FUNCTION' in lines[i]), None) if head is not None else None
        body = lines[head:end+1] if end is not None else []
        st = stext.splitlines()
        sym = next((i for i,t in enumerate(st) if t == 'Symbol......: '+symbol), None)
        signature = next((t for t in st[sym:sym+10] if t.startswith('Type')), None) if sym is not None else None
        calls = [x for x in g if 'CALL ' in x['text'] and symbol+'(' in x['text']]
        warnings = [dict(line=i,text=t.strip()) for i,t in enumerate(stream.splitlines(),1)
                    if symbol in t and 'not enough arguments' in t]
        data.append(dict(symbol=symbol, warnings=warnings, callsites=calls,
            actual_signature=signature, signature_line=sym+6 if sym is not None else None,
            body_lines=[head+1,end+1] if body else None,
            extra_parameter_referenced_in_body=any('__write_set_to_check' in t for t in body) if body else 'UNKNOWN',
            body_sha256=sha(('\n'.join(body)+'\n').encode()) if body else None,
            assurance='STATIC exact saved body/signature/calls; extra write-set parameter unused in this body only; no general fidelity/harmlessness claim'))
    return data


def arithmetic():
    qv,qc=65600,4259841
    source=[('upstream/43253856019',284883,17072414),('V02/43258921276',844029,51222776),
            ('R5-01/43268005490',846480,51218835),('R6b/43276309576',829958,51173785)]
    return dict(assurance='Exact arithmetic on R3 source-reported counters; not newly measured evidence',
        model='64-bit constant-converted indices, has_set_to path, assumed cache behavior only',
        rows=[dict(run=r,V=v,C=c,kV=v//qv,kC=c//qc,
             residualV_using_kV=v%qv,residualC_using_kC=c%qc,
             residualV_percent=100*(v%qv)/v,residualC_percent=100*(c%qc)/c) for r,v,c in source],
        formulas=dict(constant_read_vars='N+64',constant_read_clauses='65N+1',
            free_first_version_vars='129N+64',free_read_clauses='321N+1',
            free_extra_same_version_vars='65N+64',slopesV='64S+65D+C',slopesC='321D+65C'),
        proxy_scenarios=[dict(case='R1 proxy D=S=6,C=0', V=6*(129*65536+64), C=6*(321*65536+1)),
                        dict(case='R6 proxy C=12 IF constant, D=S=0', V=12*qv, C=12*qc),
                        dict(case='R6 alternate all 12 free, sharing S=6 (illustration only)',
                             V=(64*6+65*12)*65536+64*12,C=321*12*65536+12)],
        caveat='No read count inferred from floor; symbolic indices, widths/caching/mixed classes may invalidate model. No gates=>RSS inference.')


def main():
    resource.setrlimit(resource.RLIMIT_AS, (512*1024**2,512*1024**2))
    signal.signal(signal.SIGXCPU, cpu_cap)
    resource.setrlimit(resource.RLIMIT_CPU, (60,61))
    auth_bytes = checked(D1A/'INPUTS.json',dict(sha256=AUTH_SHA,bytes=(D1A/'INPUTS.json').stat().st_size))
    auth=json.loads(auth_bytes)
    support = {
        HERE.parent.parent/'TASK-KANI3300-H1-STEP0.md': '637cd6f5d34a44305a48ba2d2e696ccbc0dfe78069331b53172aeded0ff15790',
        HERE.parent.parent/'AUDIT-REPORT-KANI3300-PART1-R3-RU.md': 'a7051b671564642dc517d4468100723888c9a429003446827778ca2add175059',
        HERE.parent.parent/'PLANNER-R3-H1-REVIEW.md': 'f0959adf705bc23d4de9b4aae04aa49cbcba67f93780b847f5bc6ebaf1cfcffc',
        D1A/'DATA-ACCEPTANCE.md': 'b9be3b4df23f841354b622c703e530a3df71bac616db40e41edc5f3394af0f11',
        D1A/'analyze_offline.py': 'b96bb772690eba527bbfca01beb0d45d270b3614f90b7d349ab8020a42a34421',
        D1A/'SSA-SUMMARY.json': 'f9f994382f49f1d98d519e56896842ce4b93b5b3bcd5ec4a641a8471ccb281d9'}
    support_files = []
    for path, expected in support.items():
        spec = dict(sha256=expected,bytes=path.stat().st_size)
        checked(path,spec)
        support_files.append(dict(path=str(path),**spec))
    inputs=dict(schema='kani3300-h1-step0-inputs-v1', authority='TASK-KANI3300-H1-STEP0.md; worker14',
        support_files=support_files,
        source_research_base='ea38ff43a21e634af02eecf70b3f18b9e0ae9f71',
        d1a_authority=dict(commit='15276d57238f4a70b2ea5fca9141ef047cce120c',sha256=AUTH_SHA),
        budget=dict(cpu_seconds=60,address_space_MiB=512,file_cap_bytes=CAP,
                    on_cap='INCOMPLETE; no prefix treated as complete'),
        coverage='Only explicit two D1 roots. No historical raw logs, binary GOTO reads, new runs or downloads.',cases={})
    census, tables = {}, {}
    legacy=json.loads((D1A/'SSA-SUMMARY.json').read_text())
    for key, source in PINS.items():
        pin=auth['pins'][key]
        if pin['source'] != source:
            raise ValueError(f'STOP wrong source pin: {key}')
        root=ROOT/('d1p-'+key+'-43314208878-1')
        files=[]
        def control(name):
            p=root/name;spec=pin['control_files'][name];raw=checked(p,spec)
            files.append(dict(path=str(p),**spec));return json.loads(raw)
        identity=control('identity.json');manifest=control('ARTIFACT-MANIFEST.json')
        validate_identity(identity, pin, key)
        entries={e['path']:e for e in manifest['files']}
        base=root/source/'P1/postcondition_reads_initialized_return'
        def read(name):
            p=base/name;spec=entries.get(str(p.relative_to(root)))
            if spec is None:
                raise ValueError(f'STOP missing manifest entry: {p}')
            raw=checked(p,spec);files.append(dict(path=str(p),sha256=spec['sha256'],bytes=spec['bytes']))
            return raw
        # Confirm manifest identity before reading bounded contents.
        metadata=json.loads(read('invocations/cbmc-001/actual-cbmc.goto.json'))
        expected_model=pin['snapshots']['invocations/cbmc-001/actual-cbmc.goto']['sha256']
        if (metadata['sha256']!=expected_model or metadata.get('complete') is not True or
                metadata['bytes'] != pin['snapshots']['invocations/cbmc-001/actual-cbmc.goto']['bytes']):
            raise ValueError(f'STOP wrong actual-model sha256: {key}')
        raw=read('invocations/cbmc-001/process/stdout.bin')
        receipt=json.loads(read('invocations/cbmc-001/process/receipt.json'))
        graw=read('actual-cbmc-show-goto-functions/stdout.bin')
        sraw=read('actual-cbmc-show-symbol-table/stdout.bin')
        gtext,stext=graw.decode(),sraw.decode()
        view_receipts={name:json.loads(read(name+'/receipt.json')) for name in
                       ('actual-cbmc-show-goto-functions','actual-cbmc-show-symbol-table')}
        validate_receipt(receipt, raw, pin['tools']['cbmc']['sha256'])
        for name, content in [('actual-cbmc-show-goto-functions',graw),('actual-cbmc-show-symbol-table',sraw)]:
            validate_receipt(view_receipts[name], content, pin['tools']['goto-instrument']['sha256'])
        rows,issues=parse(raw)
        result=summarize(rows,issues,gtext,stext)
        expected=legacy['cases'][root.name]
        result['D1A_sanity']={f:dict(expected=expected[f],observed=result[f],equal=expected[f]==result[f])
                              for f in ('printed_all','printed_retained','printed_ignored','guard_lines')}
        result['saturating_warnings']=warning_binding(raw.decode(),gtext,stext)
        tables[key]=result.pop('tables');census[key]=result
        inputs['cases'][key]=dict(root=str(base),source=source,actual_model_sha256=expected_model,
             actual_model_metadata=metadata,files=files,stream_receipt=receipt,view_receipts=view_receipts,
             D1A_coverage=pin['ssa_visible_summary'],tools=pin['tools'],model_binary_read=False)
        if time.monotonic()-STARTED > 60:
            raise ValueError('INCOMPLETE wall time cap')
    for name, data in [('INPUTS.json',inputs),('TABLES.json',dict(schema='kani3300-h1-tables-v1',
        model_scope={k:v['actual_model_sha256'] for k,v in inputs['cases'].items()},cases=tables)),
        ('READ-CENSUS.json',dict(schema='kani3300-h1-read-census-v1',canonical_rule='Whitespace only; no PO(field) collapse without source proof',
              assurance='Text proxy exact if COMPLETE_TEXT_ONLY; converter causality PROVISIONAL; proof_credit=0',
              cases=census,arithmetic=arithmetic()))]:
        (HERE/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    for k,c in census.items():
        print(k,c['status'],json.dumps(c['aggregate'],sort_keys=True))
    (HERE/'INCOMPLETE.json').unlink(missing_ok=True)


if __name__=='__main__':
    try:
        main()
    except (ValueError, MemoryError, OSError) as e:
        for name in ('INPUTS.json','TABLES.json','READ-CENSUS.json'):
            (HERE/name).unlink(missing_ok=True)
        (HERE/'INCOMPLETE.json').write_text(json.dumps(dict(status='INCOMPLETE',reason=str(e)))+'\n')
        raise
