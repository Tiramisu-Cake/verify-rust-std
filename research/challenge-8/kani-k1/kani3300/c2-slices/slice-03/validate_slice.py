#!/usr/bin/env python3
"""Check exact extraction, ownership, fixtures and patch endpoints; no native tools."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extract3', HERE / 'extract_slice.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
git, digest = e.git, e.digest


def main():
    e.check_parent()
    expected = e.extract()
    for path, data in expected.items():
        assert (e.REPO / path).read_bytes() == data, path
    changed = set(git('diff', '--name-only', e.BASE).decode().splitlines())
    changed.update(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
    intended = {p for p, data in expected.items() if not git('ls-tree', e.BASE, '--', p)
                or git('show', e.BASE + ':' + p) != data}
    assert changed == intended, (changed - intended, intended - changed)
    parts = e.parts_for('3')
    inventory = e.effective_inventory()
    canonical = []
    for file in inventory['files']:
        for hunk in file['hunks']:
            for index, part in enumerate(hunk['parts']):
                if part['owner'] != '3':
                    continue
                row = {'hunk_id': hunk['id'], 'part_index': index, 'path': file['path'], **part}
                canonical.append(row)
                ref = e.F if part['side'] == '+' else e.B1
                lines = git('show', ref + ':' + file['path']).splitlines(keepends=True)
                data = b''.join(lines[part['start'] - 1:part['start'] - 1 + part['count']])
                assert digest(data) == part['sha256'], row
    assert canonical == parts and len(parts) == 22
    # Correction changes exactly the import owner; all earlier parts stay immutable.
    dependencies = json.loads((e.MAP / 'DEPENDENCIES.json').read_text())['slices']
    for owner in ['1', '2', '5', '6', '7']:
        assert e.parts_for(owner) == dependencies[owner]['source_parts'], owner
    old4 = dependencies['4']['source_parts']
    assert len(e.parts_for('4')) == len(old4) - 2
    production = sorted({r['path'] for r in parts})
    assert sorted(p for p in intended if p.endswith('.rs') and p.startswith('kani-compiler/')) == production
    prefix = 'kani-compiler/src/kani_middle/transform/check_uninit/'
    layout = expected[prefix + 'ty_layout.rs']
    assert b'data_bytes_for_ty(machine_info, *base_ty, current_offset)' in layout
    enum_fields = layout.split(b'// Compare variant layouts relative to the enum.', 1)[1].split(b'// Compose the selected local layout exactly once.', 1)[0]
    assert b'field_offset + current_offset,' not in enum_fields
    assert b'data_bytes.offset += current_offset;' in layout
    for forbidden in [b'for_typed_storage', b'for_deinit', b'argument_size', b'upvar_tys']:
        assert forbidden not in layout
    assert b'| RigidTy::Closure(_, _)' in layout
    visitor = expected[prefix + 'ptr_uninit/uninit_visitor.rs']
    assert b'ty::{AdtKind, ConstantKind, RigidTy, Ty, TyConstKind, TyKind, UintTy}' in visitor
    raw = visitor.split(b'Intrinsic::RawEq => {', 1)[1].split(b'Intrinsic::CompareBytes', 1)[0]
    for token in [b'for operand in args', b'Ty::try_new_array(', b'UintTy::U8',
                  b'layout.shape().size.bytes()', b'MemoryInitOp::CheckAs', b'MemoryInitOp::Unsupported']:
        assert token in raw
    assert b'Intrinsic::RawEq' not in visitor.split(b'fn can_skip_intrinsic', 1)[1]
    target = expected[prefix + 'delayed_ub/initial_target_visitor.rs']
    assert b'Intrinsic::RawEq => {\n                    self.push_operand(&args[0]);\n                    self.push_operand(&args[1]);' in target
    assert target == git('show', e.F + ':' + prefix + 'delayed_ub/initial_target_visitor.rs')
    relevant = expected[prefix + 'relevant_instruction.rs']
    assert b'pointee.projection.push(ProjectionElem::Deref);' in relevant
    assert b'mk_ref(&Operand::Copy(pointee), body, statements, source)' in relevant
    for forbidden in [b'CheckRefAs', b'SetStorage', b'BeginArgumentTransfer', b'constant_init_mask']:
        assert forbidden not in relevant
    protected = ['library', '.github', 'scripts', 'Cargo.toml', 'Cargo.lock', 'rust-toolchain.toml',
        'kani-compiler/src/kani_middle/kani_functions.rs',
        'kani-compiler/src/kani_middle/transform/delayed_cache.rs',
        prefix + 'ptr_uninit/mod.rs', prefix + 'delayed_ub/mod.rs',
        prefix + 'delayed_ub/instrumentation_visitor.rs',
        'kani-compiler/src/codegen_cprover_gotoc', 'kani-compiler/src/codegen_aeneas_llbc',
        'docs/src/rust-feature-support.md', 'docs/src/reference/experimental/contracts.md']
    assert not git('diff', '--name-only', e.BASE, '--', *protected)
    oracle = json.loads((HERE.parent / 'oracle-map/ORACLE-MAP.json').read_text())
    selected = [r for r in oracle['fixtures'] if r['earliest_runnable_head'] == 3]
    deferred = [r for r in oracle['fixtures'] if r['owner_slice'] == 3 and r['earliest_runnable_head'] > 3]
    assert len(selected) == 19 and len(deferred) == 9
    assert len([r for r in selected if r['owner_slice'] == 3]) == 4
    for row in selected:
        for p in [row['input'], row['golden']]:
            assert expected[p] == git('show', e.F + ':' + p)
    for row in deferred:
        for p in [row['input'], row['golden']]:
            assert not (e.REPO / p).exists(), p
    # Previously present tests, directives and goldens cannot be changed or removed.
    assert not git('diff', '--name-only', '--diff-filter=CDMRTUXB', e.BASE, '--', 'tests')
    subprocess.run(['git', '-C', str(e.REPO), 'diff', '--check', e.BASE], check=True)
    report = {'status': 'PASS_STATIC_ONLY', 'base_sha': e.BASE,
        'owner3_part_hashes_checked': len(parts), 'changed_paths': sorted(intended),
        'selected_whole_fixtures': len(selected), 'selected_owner2': 15, 'selected_owner3': 4,
        'deferred_owner3_whole_fixtures': len(deferred), 'deferred_integration_heads': [4],
        'checks': ['accepted parent reconstructed exactly', 'deterministic owners1+2+3 composition',
            'all22 effective owner3 part hashes/bijection (20 canonical + exact neutral UintTy import pair)', 'both raw_eq operands with complete byte extent and Unsupported path',
            'both relevance seeds', 'reference CheckAs reborrow and diagnostic type agree',
            'enum local-mask and Pat offsets preserved', 'closure/storage/F7 features absent',
            'all19 complete fixture/golden pairs exact F', 'all existing tests/flags/goldens unchanged',
            'nine deferred owner3 fixtures absent', 'protected paths identical to accepted parent', 'git diff --check'],
        'native_fmt_build_clippy_units_tests_verifier_CI_push': 'NOT_RUN',
        'worker15_review': 'PENDING', 'formal_proof_credit': 'NOT_ESTABLISHED'}
    head = git('rev-parse', 'HEAD').decode().strip()
    if head != e.BASE:
        assert git('show', '-s', '--format=%P', head).decode().strip() == e.BASE
        assert not git('status', '--porcelain')
        report.update(source_sha=head, source_tree=git('rev-parse', head + '^{tree}').decode().strip())
        audit = json.loads((HERE / 'SEAM-AUDIT-03.json').read_text())
        assert audit['head'] == head and audit['base'] == e.BASE and not audit['errors']
        assert audit['status'] == 'PASS_BOUNDED_STATIC_SEAM_AUDIT'
        assert audit['tool_sha256'] == digest((HERE.parent / 'seam-audit/check_seams.py').read_bytes())
        assert audit['contracts_sha256'] == digest((HERE / 'CALL-CONTRACTS-03.json').read_bytes())
        report['compile_seam_audit'] = {'status': audit['status'], 'report': 'SEAM-AUDIT-03.json', 'native_compile': 'NOT_RUN'}
        for name, start, end in [('source.patch', e.BASE, head), ('residual-to-F.patch', head, e.F)]:
            patch = git('diff', '--binary', '--full-index', start, end)
            (HERE / name).write_bytes(patch)
            with tempfile.TemporaryDirectory(prefix='slice03-index-') as tmp:
                env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
                def run(*args):
                    return subprocess.check_output(['git', '-C', str(e.REPO), *args], env=env)
                run('read-tree', start)
                subprocess.run(['git', '-C', str(e.REPO), 'apply', '--cached', str(HERE / name)], env=env, check=True)
                actual = run('write-tree').decode().strip()
                assert actual == git('rev-parse', end + '^{tree}').decode().strip()
            report[name] = {'sha256': digest(patch), 'alternate_index_target_tree': actual}
    (HERE / 'STATIC-VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ['changed_paths', 'checks']}, indent=2))


if __name__ == '__main__':
    main()
