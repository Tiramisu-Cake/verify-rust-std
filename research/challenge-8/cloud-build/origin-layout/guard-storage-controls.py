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


def run(root, args, env, execute_case, concrete_root):
    layout_admission = _layout_admission()
    evidence = root / 'guard-storage-controls'; evidence.mkdir()
    original = (concrete_root / 'cases/positive/original/lib.rs').read_bytes()
    baseline = (concrete_root / 'cases/positive/verified/lib.rs').read_bytes()
    manifest = json.loads((concrete_root / 'metadata.json').read_text())['positive']
    guard = b'        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n'
    ladder = b'        //@ assert gap_guard.src == held_ref; // LADDER: FBC pointer identity\n'
    signature = b'unsafe fn insertion_onecell('
    rows = {}
    for name, extra, expected in [('qualified_live_guard', b'', 'PASS'),
                                  ('guard_source_overlap_false', FALSE, 'EXPECTED_REJECTION'),
                                  ('guard_zero_extent_false', ZERO, 'EXPECTED_REJECTION')]:
        verified = baseline.replace(signature, ALIGN + signature, 1)
        assert baseline.count(guard) == baseline.count(ladder) == baseline.count(signature) == 1
        verified = verified.replace(guard, guard + FACTS + extra, 1)
        verified = verified.replace(ladder, ladder + POST, 1)
        ghosts = [item.encode() for item in manifest['ghost_fragments']] + [ALIGN, FACTS, POST]
        if extra: ghosts.append(extra)
        stripped = verified
        for ghost in ghosts:
            assert stripped.count(ghost) == 1
            stripped = stripped.replace(ghost, b'', 1)
        assert stripped == original
        case = evidence / name
        for tree, data in [('original', original), ('verified', verified)]:
            (case / tree).mkdir(parents=True); (case / tree / 'lib.rs').write_bytes(data)
        lines = {label: verified[:verified.index(token)].count(b'\n') + 1
                 for label, token in [('extent', FACTS.splitlines(keepends=True)[0]),
                     ('storage_alignment', FACTS.splitlines(keepends=True)[3]),
                     ('separation', FACTS.splitlines(keepends=True)[4]),
                     ('post_fbc', POST)]}
        if extra: lines['target'] = verified[:verified.index(extra)].count(b'\n') + 1
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
               'runtime_exact_after_ghost_strip': stripped == original,'source_baseline_sha256':sha(baseline),
               'lines':lines,'reached':reached,'errors':errors,
               'qualified_layout_source_mir_ast':layout_gate,**execution}
        (case/'classification.json').write_text(json.dumps(row,indent=2)+'\n'); rows[name]=row
    # Construct full mutable canonical FBC from the actual constructor resources.
    # This targeted negative ends at entry, before the old readonly half-frame
    # opening; it gives no mutable callee/post or CURRENT recovery credit.
    half_close=b'        //@ close [1/2]CopyOnDrop_full_borrow_content(t, &gap_guard)();\n'
    full_close=half_close.replace(b'[1/2]',b'')
    entry_false=b'        //@ assert false; // TARGET: full mutable canonical FBC entry\n'
    assert baseline.count(half_close)==1
    verified=baseline.replace(half_close,full_close+entry_false,1)
    ghosts=[item.encode().replace(half_close,full_close) for item in manifest['ghost_fragments']]+[entry_false]
    stripped=verified
    for ghost in ghosts:
        assert stripped.count(ghost)==1
        stripped=stripped.replace(ghost,b'',1)
    assert stripped==original
    name='full_mutable_canonical_fbc_entry_false';case=evidence/name
    for tree,data in [('original',original),('verified',verified)]:
        (case/tree).mkdir(parents=True);(case/tree/'lib.rs').write_bytes(data)
    close_line=verified[:verified.index(full_close)].count(b'\n')+1
    target_line=verified[:verified.index(entry_false)].count(b'\n')+1
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
                'runtime_exact_after_ghost_strip':stripped==original,
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
