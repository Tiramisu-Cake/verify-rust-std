#!/usr/bin/env python3
"""Cloud-only isolated unit/scalar layout controls; classifier reads saved data.

run() is called only by the hosted proof driver. No subprocess/compiler/dispatch
entrypoint here; executor is supplied by the checked Cloud driver.
"""
from pathlib import Path
import hashlib
import json
import re

HEADER = '#![no_std]\n#![allow(dead_code)]\nuse core::mem::ManuallyDrop;\n\n'
CASES = {
    'unit_ghost_size': ('', '    //@ assert std::mem::size_of::<()>() == 0; // TARGET\n', 'PASS'),
    'unit_ghost_alignment': ('', '    //@ assert std::mem::align_of::<()>() == 1; // TARGET\n', 'PASS'),
    'unit_runtime_size': ('', '    let n = core::mem::size_of::<()>();\n    //@ assert n == 0; // TARGET\n', 'PASS'),
    'unit_runtime_alignment': ('', '    let n = core::mem::align_of::<()>();\n    //@ assert n == 1; // TARGET\n', 'PASS'),
    'unit_wrapper_runtime_size': ('', '    let n = core::mem::size_of::<ManuallyDrop<()>>();\n    //@ assert n == 0; // TARGET\n', 'PASS'),
    'scalar_wrapper_runtime_size': ('', '    let n = core::mem::size_of::<ManuallyDrop<u64>>();\n    //@ assert n == 8; // TARGET\n', 'PASS'),
    'unit_positive_extent_false': ('', '    //@ assert std::mem::size_of::<()>() > 0; // TARGET\n', 'EXPECTED_REJECTION'),
    'unit_wrong_alignment_false': ('', '    //@ assert std::mem::align_of::<()>() != 1; // TARGET\n', 'EXPECTED_REJECTION'),
    'unit_generic_instantiation': ('fn layout_generic_size<T>() -> usize\n/*@ req true; @*/ /*@ ens result == std::mem::size_of::<T>(); @*/ {\n    core::mem::size_of::<T>()\n}\n\n', '    let n = layout_generic_size::<()>();\n    //@ assert n == 0; // TARGET\n', 'PASS'),
    'scalar_generic_instantiation': ('fn layout_generic_size<T>() -> usize\n/*@ req true; @*/ /*@ ens result == std::mem::size_of::<T>(); @*/ {\n    core::mem::size_of::<T>()\n}\n\n', '    let n = layout_generic_size::<u64>();\n    //@ assert n == 8; // TARGET\n', 'PASS'),
    'unknown_struct_no_positivity': ('struct LayoutUnknown {}\n\n', '    //@ assert std::mem::size_of::<LayoutUnknown>() > 0; // TARGET\n', 'EXPECTED_REJECTION'),
    'unit_pointer_zero_step': ('', '    let p = 1_usize as *const ();\n    let q = p.wrapping_add(1);\n    //@ assert q as usize == p as usize; // TARGET\n', 'PASS'),
    'unit_pointer_unequal_false': ('', '    let p = 1_usize as *const ();\n    let q = p.wrapping_add(1);\n    //@ assert q as usize != p as usize; // TARGET\n', 'EXPECTED_REJECTION'),
    'unit_local_storage': ('', '    let tmp = ManuallyDrop::new(());\n    let n = core::mem::size_of::<ManuallyDrop<()>>();\n    //@ assert n == 0; // TARGET\n', 'PASS'),
}


def prepare(evidence: Path):
    rows = {}
    for name, (helper, statements, expected) in CASES.items():
        unit = (HEADER + helper + f'pub unsafe fn {name}()\n/*@ req true; @*/ /*@ ens true; @*/ {{\n' + statements + '}\n').encode()
        target = [i+1 for i, s in enumerate(unit.decode().splitlines()) if '// TARGET' in s]
        assert len(target) == 1
        case = evidence / name
        for tree in ('original', 'verified'):
            (case/tree).mkdir(parents=True)
            (case/tree/'lib.rs').write_bytes(unit)
        rows[name] = {'name': name, 'target_line': target[0], 'expectation': expected,
                      'source_sha256': hashlib.sha256(unit).hexdigest()}
    (evidence/'manifest.json').write_text(json.dumps(rows, indent=2)+'\n')
    return rows


def classify(case: Path, meta: dict, execution: dict):
    log = (case/'verifast.log').read_text(errors='replace')
    errors = re.findall(r'^.*\berror:.*$', log, re.M|re.I)
    at = rf"verified/lib\.rs\({meta['target_line']},\d+(?:-\d+(?:,\d+)?)?\): "
    reached = re.search(at+r'(?:note: )?Executing statement', log) is not None
    headers = list(re.finditer(r"Verifying function '([^']+)'", log))
    segment = ''
    for i, match in enumerate(headers):
        if match.group(1) == meta['name']:
            segment = log[match.start(): headers[i+1].start() if i+1<len(headers) else len(log)]
    s = execution['stages']
    source_ok = (execution.get('source_unchanged_at_every_stage') is True and
                 all(hashlib.sha256((case/tree/'lib.rs').read_bytes()).hexdigest()==meta['source_sha256']
                     for tree in ('original','verified')))
    base_ok = source_ok and all(s.get(k)==0 for k in ('exporter','decode','refinement')) and reached and bool(segment) and not re.search('dead code',log,re.I)
    normal = 'Executing return statement' in segment and 'Leak check.' in segment
    if meta['expectation']=='PASS':
        matched = base_ok and s.get('verifast')==0 and not errors and normal and '0 errors found' in log
        verdict = 'PASS_CONTROL' if matched else 'INCONCLUSIVE'
    else:
        matched = (base_ok and s.get('verifast')==1 and len(errors)==1 and
                   re.search(at+'error:', errors[0]) is not None and
                   'Cannot prove' in errors[0] and 'Leak check.' not in segment)
        verdict = 'EXPECTED_REJECTION' if matched else 'INCONCLUSIVE'
    return {**meta, **execution, 'classification': verdict, 'target_reached': reached,
            'normal_return_leak_seen': normal, 'errors': errors, 'accepted': False,
            'domain': 'canonical unit / u64 / layout-erased ManuallyDrop thereof; generic helper specialization only'}


def run(root, args, env, execute_case):
    evidence = root/'layout-controls'; evidence.mkdir()
    rows = prepare(evidence)
    results = {}
    for name, meta in rows.items():
        case = evidence/name
        results[name] = classify(case, meta, execute_case(case,args,env))
        (case/'classification.json').write_text(json.dumps(results[name],indent=2)+'\n')
    summary = {'schema':'merge-unit-layout-controls-v1','accepted':False,'cases':results,
               'all_matched':all(v['classification'] in {'PASS_CONTROL','EXPECTED_REJECTION'} for v in results.values()),
               'generic_runtime_extent':'OPEN', 'zst_address_separation':'NOT_CLAIMED'}
    (evidence/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


def classify_compiler_facts(evidence: Path, source: Path):
    """Read a saved Cloud compiler observation; no compiler/proof execution."""
    expected = {"unit": [0, 1], "manually_drop_unit": [0, 1],
                "u64": [8, 8], "manually_drop_u64": [8, 8],
                "unit_array_stride": 0, "u64_array_stride": 8,
                "classification": "COMPILER_FACT_DIAGNOSTIC_NOT_PROOF"}
    observed = json.loads((evidence / "compiler-layout.json").read_text())
    valid = (observed == expected and
             hashlib.sha256((evidence / "compiler-layout.rs").read_bytes()).digest() ==
             hashlib.sha256(source.read_bytes()).digest() and
             (evidence / "compiler-layout-compile-exit-code.txt").read_text().strip() == "0" and
             (evidence / "compiler-layout-run-exit-code.txt").read_text().strip() == "0" and
             not re.search(r"\berror:", (evidence / "compiler-layout-compile.log").read_text(), re.I) and
             not (evidence / "compiler-layout-run.log").read_text().strip())
    return {"valid": bool(valid), "observed": observed, "accepted": False,
            "classification": "COMPILER_FACT_DIAGNOSTIC_NOT_PROOF"}
