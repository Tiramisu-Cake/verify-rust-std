#!/usr/bin/env python3
"""Cloud-only qualified guard storage controls on the saved source-linked fixture.

Only run() writes/runs fixtures using the supplied hosted stage executor.
Classification and source stripping are isolated saved-data service operations.
"""
from pathlib import Path
import hashlib
import json
import re
import copy
import importlib.util
import sys

ALIGN = b'''/*@
lem guard_storage_alignment(p: *CopyOnDrop)
    req [?f](*p |-> ?v);
    ens [f](*p |-> v) &*& p as usize % std::mem::align_of::<CopyOnDrop>() == 0;
{
    open [f]points_to::<CopyOnDrop>(p, v);
    to_u8s_::<CopyOnDrop>(p);
    from_u8s_::<CopyOnDrop>(p);
    close [f]points_to::<CopyOnDrop>(p, v);
}
@*/

'''
FACTS = b'''        //@ assert std::mem::size_of::<CopyOnDrop>() > 0; // GUARD: extent
        //@ assert std::mem::align_of::<CopyOnDrop>() > 0; // GUARD: layout alignment
        //@ guard_storage_alignment(&gap_guard as *mut CopyOnDrop);
        //@ assert (&gap_guard as *mut CopyOnDrop) as usize % std::mem::align_of::<CopyOnDrop>() == 0; // GUARD: actual storage alignment
        //@ assert ((&gap_guard as *mut CopyOnDrop) as usize + std::mem::size_of::<CopyOnDrop>() <= gap_guard.src as usize || gap_guard.src as usize + std::mem::size_of::<u64>() <= (&gap_guard as *mut CopyOnDrop) as usize); // GUARD: allocation separation
'''
POST = b'''        //@ assert ((&gap_guard as *mut CopyOnDrop) as usize + std::mem::size_of::<CopyOnDrop>() <= gap_guard.src as usize || gap_guard.src as usize + std::mem::size_of::<u64>() <= (&gap_guard as *mut CopyOnDrop) as usize); // GUARD: post FBC separation
'''
FALSE = b'''        //@ assert (&gap_guard as *mut CopyOnDrop) as usize == gap_guard.src as usize; // TARGET
'''
ZERO = b'''        //@ assert std::mem::size_of::<CopyOnDrop>() == 0; // TARGET
'''


def sha(data): return hashlib.sha256(data).hexdigest()


def _layout_admission():
    path = Path(__file__).with_name('guard-layout-admission.py')
    spec = importlib.util.spec_from_file_location('qualified_guard_layout_admission', path)
    if spec is None or spec.loader is None:
        raise RuntimeError('qualified guard layout admission helper missing')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _no_storage_qualification_gate(case, source):
    """Bind the synthetic negative's qualified ADT and resource-free body."""
    try:
        admission = _layout_admission()
        mir = admission._load('guard_no_storage_mir', admission.OLD / 'stack-address-admission.py')
        ast = admission._load('guard_no_storage_ast', admission.OLD / 'stack-proof-ast-admission.py')
        decoded = (case/'decode.out').read_text()
        ast_text = (case/'proof-ast.ml').read_text()
        tree = mir.CapnpText(decoded.replace(
            'variances = [invariant]', 'variances = ["invariant"]')).parse()
        ast_tree = ast.OcamlAstText(ast_text).parse()
        admission._need(mir.path(tree, 'targetTriple') == 'x86_64-unknown-linux-gnu' and
                        mir.path(tree, 'pointerWidth') == 64,
                        'negative compiler target/pointer width differs')
        cursor = mir.path(tree, 'adtDefs')
        adts = []
        while isinstance(cursor, dict) and 'cons' in cursor:
            adts.append(mir.path(cursor, 'cons', 'h'))
            cursor = mir.path(cursor, 'cons', 't')
        guard = admission._one([item for item in adts if
                                mir.path(item, 'id', 'name') == 'CopyOnDrop'],
                               'negative CopyOnDrop ADT')
        path = mir.path(guard, 'id', 'name')
        admission._need(mir.path(guard, 'hasConcreteGuardLayout') is True and
                        mir.path(guard, 'concreteGuardDefPath') == path and
                        mir.path(guard, 'isLocal') is True and
                        mir.path(guard, 'kind') == {'structKind': None} and
                        mir.path(guard, 'isReprC') is False and
                        mir.path(guard, 'implementsDrop') is False,
                        'negative ADT is not the source-qualified guard')
        path_hash = mir.path(guard, 'concreteGuardDefPathHash')
        admission._need(isinstance(path_hash, str) and bool(path_hash.strip()),
                        'negative compiler DefPathHash absent')
        guard_line = admission._source_line(source, admission.GUARD_SOURCE)
        def_line, _, snippet = admission._span(mir, mir.path(guard, 'defSpan'), source)
        admission._need(def_line == guard_line and
                        snippet in (admission.GUARD_SOURCE, admission.GUARD_SOURCE+b'\n'),
                        'negative guard def-span differs from exact source')
        variants = mir.path(guard, 'variants')
        admission._need(isinstance(variants, list) and len(variants) == 1,
                        'negative guard variant shape differs')
        fields = mir.path(variants[0], 'fields')
        names = [mir.path(field, 'name', 'name') for field in fields]
        admission._need(names == ['src', 'dst', 'len'] and
                        admission._ty(mir, fields[0], 'u64', 'not') and
                        admission._ty(mir, fields[1], 'u64', 'mut') and
                        admission._ty(mir, fields[2], 'usize'),
                        'negative guard field types differ')
        size = mir.path(guard, 'concreteGuardSizeBytes')
        align = mir.path(guard, 'concreteGuardAlignBytes')
        admission._need(isinstance(size, int) and isinstance(align, int) and
                        0 < size <= (1 << 64)-1 and 0 < align <= (1 << 64)-1,
                        'negative guard extent/alignment differs')
        offsets = mir.path(guard, 'concreteGuardFieldOffsets')
        sizes = mir.path(guard, 'concreteGuardFieldSizes')
        admission._need(isinstance(offsets, list) and isinstance(sizes, list) and
                        len(offsets) == len(sizes) == 3,
                        'negative guard layout arity differs')
        intervals = [(admission._uint(off), admission._uint(width, positive=True))
                     for off, width in zip(offsets, sizes)]
        admission._need(all(off+width <= size for off, width in intervals) and
                        all(a+aw <= b or b+bw <= a
                            for i, (a, aw) in enumerate(intervals)
                            for b, bw in intervals[i+1:]),
                        'negative guard layout fields overlap')
        structs = [node for node in ast.nodes(ast_tree, 'Struct') if
                   len(node.args) == 5 and node.args[1] == path]
        struct = admission._one(structs, 'negative translated guard Struct')
        admission._need(ast.location_line(struct.args[0]) == guard_line and
                        struct.args[2] == [], 'negative translated Struct identity differs')
        body = struct.args[3]
        admission._need(isinstance(body, ast.Node) and body.name == 'Left' and
                        len(body.args) == 4 and body.args[0] == [] and body.args[2] == [],
                        'negative translated Struct shape differs')
        ast_fields = body.args[1]
        admission._need(isinstance(ast_fields, list) and len(ast_fields) == 3 and
                        [field.args[3] for field in ast_fields if
                         isinstance(field, ast.Node) and field.name == 'Field' and
                         len(field.args) == 8] == names and
                        admission._ast_type(ast, ast_fields[0].args[2], True) and
                        admission._ast_type(ast, ast_fields[1].args[2], True) and
                        admission._ast_type(ast, ast_fields[2].args[2], False),
                        'negative translated guard field types differ')
        attrs = struct.args[4]
        admission._need(isinstance(attrs, list) and len(attrs) == 1 and
                        isinstance(attrs[0], ast.Node) and
                        attrs[0].name == 'RustConcreteGuardLayout' and
                        len(attrs[0].args) == 1,
                        'negative translated layout attribute differs')
        helper = attrs[0].args[0]
        admission._need(isinstance(helper, ast.Node) and
                        helper.name == 'make_rust_concrete_guard_layout' and
                        helper.args == [path, path_hash, 'x86_64-unknown-linux-gnu', 64,
                                        str(size), str(align), offsets, sizes],
                        'negative MIR/AST qualified layout differs')
        bodies = [body for body in mir.path(tree, 'bodies') if
                  mir.path(body, 'defPath') == 'no_storage_receipts']
        admission._one(bodies, 'negative MIR function')
        funcs = [node for node in ast.nodes(ast_tree, 'Func') if
                 len(node.args) == 13 and node.args[4] == 'no_storage_receipts']
        function = admission._one(funcs, 'negative AST function')
        contract = function.args[8]
        admission._need(isinstance(contract, ast.Node) and contract.name == 'Some' and
                        len(contract.args) == 1 and isinstance(contract.args[0], tuple) and
                        len(contract.args[0]) == 2 and
                        isinstance(contract.args[0][0], ast.Node) and
                        contract.args[0][0].name == 'True',
                        'negative function requires physical resources')
        runtime = function.args[10]
        admission._need(isinstance(runtime, ast.Node) and runtime.name == 'Some' and
                        len(runtime.args) == 1 and isinstance(runtime.args[0], tuple) and
                        len(runtime.args[0]) == 2 and isinstance(runtime.args[0][0], list),
                        'negative function has no flat checked body')
        for forbidden in ('Assume', 'Close', 'Open', 'Leak'):
            admission._need(not ast.nodes(runtime, forbidden),
                            'negative body contains resource-producing ghost operation')
        markers = [node for node in ast.nodes(runtime, 'RustStorageLiveStmt') if
                   len(node.args) == 4]
        dead = [node for node in ast.nodes(runtime, 'RustStorageDeadStmt') if
                len(node.args) == 4]
        admission._need(len(markers) == len(ast.nodes(runtime, 'RustStorageLiveStmt')) and
                        len(dead) == len(ast.nodes(runtime, 'RustStorageDeadStmt')),
                        'malformed negative temporary storage marker')
        live_ids = [node.args[2] for node in markers]
        dead_ids = [node.args[2] for node in dead]
        flat = runtime.args[0][0]
        positions = {id(statement): index for index, statement in enumerate(flat)}
        dead_by_id = {node.args[2]: node for node in dead}
        admission._need(all(isinstance(node.args[3], str) and
                            re.fullmatch(r'\$_[0-9]+', node.args[3]) and
                            node.args[2] not in ('root', 'src') for node in markers) and
                        len(live_ids) == len(set(live_ids)) and
                        sorted(live_ids) == sorted(dead_ids) and
                        all(id(node) in positions for node in markers+dead) and
                        all(dead_by_id[live.args[2]].args[3] == live.args[3] and
                            positions[id(live)] < positions[id(dead_by_id[live.args[2]])]
                            for live in markers),
                        'negative function has a relevant or unpaired StorageLive')
        return {'admitted': True, 'layout_def_path': path,
                'layout_def_path_hash': path_hash,
                'temporary_storage_live_count': len(markers),
                'relevant_storage_receipts_absent': True,
                'physical_precondition_absent': True}
    except Exception as error:
        return {'admitted': False, 'reason': f'qualified no-storage gate failed: {error}'}



GUARD_INIT = b'        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n'
FBC_LADDER = b'        //@ assert gap_guard.src == held_ref; // LADDER: FBC pointer identity\n'
SIGNATURE = b'unsafe fn insertion_onecell('
HALF_CLOSE = b'        //@ close [1/2]CopyOnDrop_full_borrow_content(t, &gap_guard)();\n'
ENTRY_FALSE = b'        //@ assert false; // TARGET: full mutable canonical FBC entry\n'


def _once(data, token, label):
    count = data.count(token)
    if count != 1:
        raise ValueError(f'guard preparation {label}: expected one occurrence, found {count}')


def _replace_manifest_fragment(fragments, anchor, replacement, label):
    # An insertion inside an existing fragment changes that fragment's exact
    # expected bytes. Update its sole carrier, never widen accepted hashes.
    carriers = [i for i, fragment in enumerate(fragments) if anchor in fragment]
    if len(carriers) != 1:
        raise ValueError(f'guard preparation {label}: expected one manifest carrier, found {len(carriers)}')
    index = carriers[0]
    _once(fragments[index], anchor, label+' manifest anchor')
    result = list(fragments)
    result[index] = result[index].replace(anchor, replacement, 1)
    return result


def _check_prepared(name, original, verified, fragments):
    stripped = verified
    receipt = []
    for index, fragment in enumerate(fragments):
        _once(stripped, fragment, f'{name} ghost fragment {index}')
        receipt.append({'index': index, 'sha256': sha(fragment), 'bytes': len(fragment)})
        stripped = stripped.replace(fragment, b'', 1)
    if stripped != original:
        raise ValueError(f'guard preparation {name}: runtime bytes differ after exact ghost removal')
    return {'schema': 'guard-fixture-preparation-v1', 'case': name,
            'original_sha256': sha(original), 'verified_sha256': sha(verified),
            'runtime_exact_after_ghost_strip': True,
            'ghost_fragments': [fragment.decode() for fragment in fragments],
            'fragment_receipts': receipt, 'accepted': False, 'proof_attempted': False}


def prepare_qualified(name, original, baseline, manifest, extra=b''):
    # Pure byte preparation shared by Cloud and saved replay. No tool execution.
    for label, token in [('constructor', GUARD_INIT), ('post-FBC ladder', FBC_LADDER),
                         ('signature', SIGNATURE)]:
        _once(baseline, token, label)
    verified = baseline.replace(SIGNATURE, ALIGN+SIGNATURE, 1)
    verified = verified.replace(GUARD_INIT, GUARD_INIT+FACTS+extra, 1)
    verified = verified.replace(FBC_LADDER, FBC_LADDER+POST, 1)
    fragments = _replace_manifest_fragment([item.encode() for item in manifest['ghost_fragments']],
                                           FBC_LADDER, FBC_LADDER+POST, 'post-FBC')
    fragments += [ALIGN, FACTS] + ([extra] if extra else [])
    receipt = _check_prepared(name, original, verified, fragments)
    lines = {label: verified[:verified.index(token)].count(b'\n')+1
             for label, token in [('extent', FACTS.splitlines(keepends=True)[0]),
                 ('storage_alignment', FACTS.splitlines(keepends=True)[3]),
                 ('separation', FACTS.splitlines(keepends=True)[4]), ('post_fbc', POST)]}
    if extra:
        _once(verified, extra, 'negative target')
        lines['target'] = verified[:verified.index(extra)].count(b'\n')+1
    if not lines['separation'] < verified[:verified.index(FBC_LADDER)].count(b'\n')+1 < lines['post_fbc']:
        raise ValueError('guard preparation: separation/post-FBC insertion order changed')
    receipt['lines'] = lines
    return verified, lines, receipt


def prepare_full_fbc(original, baseline, manifest):
    _once(baseline, HALF_CLOSE, 'half FBC close')
    full_close = HALF_CLOSE.replace(b'[1/2]', b'')
    replacement = full_close+ENTRY_FALSE
    verified = baseline.replace(HALF_CLOSE, replacement, 1)
    fragments = _replace_manifest_fragment([item.encode() for item in manifest['ghost_fragments']],
                                           HALF_CLOSE, replacement, 'full FBC entry')
    receipt = _check_prepared('full_mutable_canonical_fbc_entry_false', original, verified, fragments)
    close_line = verified[:verified.index(full_close)].count(b'\n')+1
    target_line = verified[:verified.index(ENTRY_FALSE)].count(b'\n')+1
    receipt['lines'] = {'close': close_line, 'target': target_line}
    return verified, close_line, target_line, receipt


def run(root, args, env, execute_case, concrete_root):
    layout_admission = _layout_admission()
    evidence = root / 'guard-storage-controls'; evidence.mkdir()
    original = (concrete_root / 'cases/positive/original/lib.rs').read_bytes()
    baseline = (concrete_root / 'cases/positive/verified/lib.rs').read_bytes()
    manifest = json.loads((concrete_root / 'metadata.json').read_text())['positive']
    rows = {}
    for name, extra, expected in [('qualified_live_guard', b'', 'PASS'),
                                  ('guard_source_overlap_false', FALSE, 'EXPECTED_REJECTION'),
                                  ('guard_zero_extent_false', ZERO, 'EXPECTED_REJECTION')]:
        verified, lines, preparation = prepare_qualified(name, original, baseline, manifest, extra)
        case = evidence / name
        for tree, data in [('original', original), ('verified', verified)]:
            (case / tree).mkdir(parents=True); (case / tree / 'lib.rs').write_bytes(data)
        (case/'preparation.json').write_text(json.dumps(preparation, indent=2)+'\n')
        execution = execute_case(case, args, env)
        layout_gate = layout_admission.admit(case)
        log = (case / 'verifast.log').read_text(errors='replace')
        stages = execution['stages']
        errors = re.findall(r'^.*\berror:.*$', log, re.M | re.I)
        reached = {label: bool(re.search(rf'verified/lib\.rs\({line},\d+.*\): (?:note: )?Executing statement', log))
                   for label, line in lines.items()}
        intact = execution.get('source_unchanged_at_every_stage') is True and sha((case/'original/lib.rs').read_bytes()) == sha(original) and sha((case/'verified/lib.rs').read_bytes()) == sha(verified)
        admitted = (intact and layout_gate['admitted'] is True and
                    all(stages.get(stage) == 0 for stage in ('exporter','decode','refinement')) and
                    'dead code' not in log.lower())
        if expected == 'PASS':
            matched = admitted and stages['verifast'] == 0 and not errors and all(reached.values()) and 'Executing return statement' in log and 'Leak check.' in log and '0 errors found' in log
        else:
            matched = admitted and stages['verifast'] == 1 and len(errors) == 1 and reached.get('target') and re.search(rf'verified/lib\.rs\({lines["target"]},\d+.*\): error: (?:Assertion might not hold\. \()?Cannot prove',errors[0]) is not None
        row = {'classification': ('PASS_CONTROL' if expected == 'PASS' else 'EXPECTED_REJECTION') if matched else 'INCONCLUSIVE',
               'expectation':expected,'accepted':False,'original_sha256':sha(original),'verified_sha256':sha(verified),
               'runtime_exact_after_ghost_strip': preparation['runtime_exact_after_ghost_strip'],'source_baseline_sha256':sha(baseline),
               'lines':lines,'reached':reached,'errors':errors,
               'qualified_layout_source_mir_ast':layout_gate,**execution}
        (case/'classification.json').write_text(json.dumps(row,indent=2)+'\n'); rows[name]=row
    # Construct full mutable canonical FBC from the actual constructor resources.
    # This targeted negative ends at entry, before the old readonly half-frame
    # opening; it gives no mutable callee/post or CURRENT recovery credit.
    verified, close_line, target_line, preparation = prepare_full_fbc(original, baseline, manifest)
    name='full_mutable_canonical_fbc_entry_false';case=evidence/name
    for tree,data in [('original',original),('verified',verified)]:
        (case/tree).mkdir(parents=True);(case/tree/'lib.rs').write_bytes(data)
    (case/'preparation.json').write_text(json.dumps(preparation,indent=2)+'\n')
    execution=execute_case(case,args,env)
    log=(case/'verifast.log').read_text(errors='replace')
    errors=re.findall(r'^.*\berror:.*$',log,re.M|re.I)
    reached=lambda line:bool(re.search(rf'verified/lib\.rs\({line},\d+.*\): (?:note: )?Executing statement',log))
    matched=(execution.get('source_unchanged_at_every_stage') is True and
             all(execution['stages'].get(k)==0 for k in ('exporter','decode','refinement')) and
             execution['stages'].get('verifast')==1 and len(errors)==1 and
             reached(close_line) and reached(target_line) and
             re.search(rf'verified/lib\.rs\({target_line},\d+.*\): error: Assertion might not hold\. \(Cannot prove false\.\)',errors[0]) is not None)
    rows[name]={'classification':'EXPECTED_REJECTION' if matched else 'INCONCLUSIVE',
                'expectation':'EXPECTED_REJECTION','accepted':False,
                'runtime_exact_after_ghost_strip':preparation['runtime_exact_after_ghost_strip'],
                'full_physical_fbc_constructed':matched,'canonical_ref_origin_not_claimed':True,
                'callee_call_or_mutable_post_credit':False,'close_line':close_line,'target_line':target_line,
                'original_sha256':sha(original),'verified_sha256':sha(verified),'errors':errors,**execution}
    (case/'classification.json').write_text(json.dumps(rows[name],indent=2)+'\n')
    # Source/type qualification is refused before any layout equality is added.
    for name, declaration, ty, params in [
            ('wrong_constness_unqualified', 'struct CopyOnDrop {\n    src: *mut u64,\n    dst: *mut u64,\n    len: usize,\n}\n', 'CopyOnDrop', ''),
            ('renamed_guard_unqualified', 'struct DifferentGuard {\n    src: *const u64,\n    dst: *mut u64,\n    len: usize,\n}\n', 'DifferentGuard', ''),
            ('generic_guard_unqualified', 'struct CopyOnDrop<T> {\n    src: *const T,\n    dst: *mut T,\n    len: usize,\n}\n', 'CopyOnDrop<T>', '<T>'),
            ('zst_guard_unqualified', 'struct CopyOnDrop {}\n', 'CopyOnDrop', '')]:
        data = ('#![no_std]\n' + declaration + f'pub unsafe fn {name}{params}()\n/*@ req true; @*/ /*@ ens true; @*/ {{\n    //@ assert std::mem::size_of::<{ty}>() > 0; // TARGET\n}}\n').encode()
        case = evidence/name
        for tree in ('original','verified'):
            (case/tree).mkdir(parents=True);(case/tree/'lib.rs').write_bytes(data)
        target = next(i+1 for i,line in enumerate(data.splitlines()) if b'// TARGET' in line)
        execution = execute_case(case,args,env)
        log = (case/'verifast.log').read_text(errors='replace')
        decoded = (case/'decode.out').read_text(errors='replace') if (case/'decode.out').exists() else ''
        errors = re.findall(r'^.*\berror:.*$',log,re.M|re.I)
        at=rf'verified/lib\.rs\({target},\d+.*\): '
        qualified_absent = 'hasConcreteGuardLayout = true' not in decoded and bool(decoded)
        matched = (execution.get('source_unchanged_at_every_stage') is True and
                   all(execution['stages'].get(k)==0 for k in ('exporter','decode','refinement')) and
                   execution['stages'].get('verifast')==1 and qualified_absent and len(errors)==1 and
                   re.search(at+'(?:note: )?Executing statement',log) is not None and
                   re.search(at+r'error: (?:Assertion might not hold\. \()?Cannot prove',errors[0]) is not None and 'dead code' not in log.lower())
        rows[name]={'classification':'EXPECTED_REJECTION' if matched else 'INCONCLUSIVE',
                    'expectation':'EXPECTED_REJECTION','accepted':False,'qualified_layout_absent':qualified_absent,
                    'source_sha256':sha(data),'target_line':target,'errors':errors,**execution}
        (case/'classification.json').write_text(json.dumps(rows[name],indent=2)+'\n')
    # Layout alone does not separate arbitrary incoming pointers. There are
    # neither physical chunks nor StorageLive receipts in this control.
    name = 'qualified_layout_without_storage_resources'
    data = (b'#![no_std]\nstruct CopyOnDrop {\n    src: *const u64,\n    dst: *mut u64,\n    len: usize,\n}\n'
            b'pub unsafe fn no_storage_receipts(root: *const CopyOnDrop, src: *const u64)\n'
            b'/*@ req true; @*/ /*@ ens true; @*/ {\n'
            b'    //@ assert std::mem::size_of::<CopyOnDrop>() > 0; // LAYOUT_REACHED\n'
            b'    //@ assert root as usize + std::mem::size_of::<CopyOnDrop>() <= src as usize || src as usize + std::mem::size_of::<u64>() <= root as usize; // TARGET\n}\n')
    case = evidence/name
    for tree in ('original', 'verified'):
        (case/tree).mkdir(parents=True); (case/tree/'lib.rs').write_bytes(data)
    target = next(i+1 for i,line in enumerate(data.splitlines()) if b'// TARGET' in line)
    execution = execute_case(case,args,env)
    log = (case/'verifast.log').read_text(errors='replace')
    errors = re.findall(r'^.*\berror:.*$',log,re.M|re.I)
    at = rf'verified/lib\.rs\({target},\d+.*\): '
    extent = next(i+1 for i,line in enumerate(data.splitlines()) if b'// LAYOUT_REACHED' in line)
    extent_at = rf'verified/lib\.rs\({extent},\d+.*\): '
    qualification = _no_storage_qualification_gate(case, data)
    matched = (execution.get('source_unchanged_at_every_stage') is True and
               all(execution['stages'].get(k)==0 for k in ('exporter','decode','refinement')) and
               execution['stages'].get('verifast')==1 and
               qualification['admitted'] is True and len(errors)==1 and
               re.search(extent_at+'(?:note: )?Executing statement',log) is not None and
               re.search(at+'(?:note: )?Executing statement',log) is not None and
               re.search(at+r'error: (?:Assertion might not hold\. \()?Cannot prove',errors[0]) is not None and
               'dead code' not in log.lower())
    rows[name] = {'classification':'EXPECTED_REJECTION' if matched else 'INCONCLUSIVE',
                  'expectation':'EXPECTED_REJECTION','accepted':False,
                  'qualified_layout_source_mir_ast':qualification,
                  'physical_resources_supplied':False,
                  'relevant_storage_receipts_absent':qualification.get('relevant_storage_receipts_absent',False),
                  'source_sha256':sha(data),'extent_line':extent,
                  'target_line':target,'errors':errors,**execution}
    (case/'classification.json').write_text(json.dumps(rows[name],indent=2)+'\n')
    # The exporter still supplies its actual x86_64 layout.  A verifier using
    # a 32-bit pointer model must refuse it before any layout fact/body step.
    name = 'mismatched_verifier_pointer_model'
    data = b'''#![no_std]
struct CopyOnDrop {
    src: *const u64,
    dst: *mut u64,
    len: usize,
}
pub unsafe fn target_control()
/*@ req true; @*/ /*@ ens true; @*/ {
    //@ assert std::mem::size_of::<CopyOnDrop>() > 0; // UNREACHED
}
'''
    case=evidence/name
    for tree in ('original','verified'):
        (case/tree).mkdir(parents=True);(case/tree/'lib.rs').write_bytes(data)
    control_args=copy.copy(args);control_args.qualification_target='ILP32'
    execution=execute_case(case,control_args,env)
    log=(case/'verifast.log').read_text(errors='replace')
    decoded=(case/'decode.out').read_text(errors='replace')
    errors=re.findall(r'^.*\berror:.*$',log,re.M|re.I)
    matched=(execution.get('source_unchanged_at_every_stage') is True and
             all(execution['stages'].get(k)==0 for k in ('exporter','decode','refinement')) and
             execution['stages'].get('verifast')==1 and
             'hasConcreteGuardLayout = true' in decoded and len(errors)==1 and
             'Invalid compiler-qualified concrete Rust guard layout metadata.' in errors[0])
    rows[name]={'classification':'EXPECTED_QUALIFICATION_REJECTION' if matched else 'INCONCLUSIVE',
                'expectation':'EXPECTED_QUALIFICATION_REJECTION','accepted':False,
                'exporter_target':'x86_64-unknown-linux-gnu','verifier_target':'ILP32',
                'source_sha256':sha(data),'errors':errors,**execution}
    (case/'classification.json').write_text(json.dumps(rows[name],indent=2)+'\n')
    summary={'schema':'qualified-guard-storage-controls-v1','cases':rows,'accepted':False,
             'domain':'source-linked concrete-u64 actual tmp/guard constructor and half-FBC precise frame',
             'all_matched':all(row['classification'] in {'PASS_CONTROL','EXPECTED_REJECTION','EXPECTED_QUALIFICATION_REJECTION'} for row in rows.values()),
             'actual_glue_credit':False}
    (evidence/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
