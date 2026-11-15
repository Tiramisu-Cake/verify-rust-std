#!/usr/bin/env python3
"""Static extraction/fixture/patch audit. Does not execute a compiler or verifier."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extract4', HERE/'extract_slice.py')
e = importlib.util.module_from_spec(spec); spec.loader.exec_module(e)
git, digest = e.git, e.digest


def main():
    e.check_parent()
    expected = e.extract()
    for p, data in expected.items():
        assert (e.REPO/p).read_bytes() == data, p
    intended = {p for p,d in expected.items() if not git('ls-tree',e.BASE,'--',p) or git('show',e.BASE+':'+p)!=d}
    changed = set(git('diff','--name-only',e.BASE).decode().splitlines())
    changed.update(git('ls-files','--others','--exclude-standard').decode().splitlines())
    assert changed == intended, (changed-intended,intended-changed)
    parts = e.prior.parts_for('4')
    for file in e.prior.effective_inventory()['files']:
        for h in file['hunks']:
            for part in h['parts']:
                ref = e.F if part['side']=='+' else e.B1
                lines = git('show',ref+':'+file['path']).splitlines(keepends=True)
                assert digest(b''.join(lines[part['start']-1:part['start']-1+part['count']])) == part['sha256']
    # Own earlier part identities are unchanged; only canonical UintTy import ownership was corrected3.
    for owner in ['1','2','3']:
        prior_parts=json.loads((HERE.parent/f'slice-0{owner}/SOURCE-PARTS.json').read_text())['parts']
        assert e.prior.parts_for(owner)==prior_parts, owner
    prod = {r['path'] for r in parts}
    assert len(prod)==8
    assert {p for p in intended if p.startswith(('kani-compiler/','library/'))}==prod
    prefix='kani-compiler/src/kani_middle/transform/check_uninit/'
    for p in prod-{prefix+'ty_layout.rs',prefix+'delayed_ub/mod.rs'}:
        assert expected[p]==git('show',e.F+':'+p), p
    layout=expected[prefix+'ty_layout.rs']
    for t in [b'for_typed_storage',b'for_deinit',b'argument_size',b'maybe_uninit_storage',b'for_storage']:
        assert t in layout
    assert b'upvar_tys' not in layout and b'| RigidTy::Closure(_, _)' in layout
    visitor=expected[prefix+'ptr_uninit/uninit_visitor.rs']
    protocol=visitor.split(b'fn has_transfer_protocol(instance: Instance) -> bool {')[1]
    assert protocol==b'\n    instance.kind == InstanceKind::Item\n        && !instance.is_foreign_item()\n        && instance.has_body()\n        && !matches!(KaniFunction::try_from(instance), Ok(KaniFunction::Hook(_)))\n}\n'
    assert b'\n        && !matches!(KaniFunction::try_from(instance), Ok(KaniFunction::Model' not in visitor
    # Exact F equality above covers ALL caller/callee/return, Move/Copy/F6 branches and enum builders/runtime.
    # Check both public call sites accompany UninitInstrumenter's tcx argument.
    for suffix in ['ptr_uninit/mod.rs','delayed_ub/mod.rs']:
        assert b'UninitInstrumenter::run(' in expected[prefix+suffix]
    selected,deferred=e.fixture_sets()
    ids={r['id'] for r in selected}
    d1=json.loads((HERE.parent/'slice-01/DEFERRED-OBLIGATIONS.json').read_text())
    d3=json.loads((HERE.parent/'slice-03/DEFERRED-OBLIGATIONS.json').read_text())
    moved={r['id'] for r in json.loads((HERE/'ORACLE-MAP-CORRECTION.json').read_text())['changes']} if (HERE/'ORACLE-MAP-CORRECTION.json').exists() else set()
    required={r['id'] for r in d1['obligations'] if r['integration_head']==4}
    required.update(r['id'] for r in d3['reassigned_fixtures']+d3['layout_raw_obligations'])
    assert required-moved <= ids
    assert {'marker-hook-calls/marked-model-hole','marker-hook-calls/marked-model-initialized'} <= ids
    assert 'marker-hook-calls/generated-modifies-no-shadow' not in ids
    for row in selected:
        for p in [row['input'],row['golden']]: assert (e.REPO/p).read_bytes()==git('show',e.F+':'+p),p
    for row in deferred:
        for p in [row['input'],row['golden']]:
            assert not (e.REPO/p).exists(),p
    # Only four existing B1 entry source fixtures change; no existing golden/check is weakened.
    modified=git('diff','--name-only','--diff-filter=CDMRTUXB',e.BASE,'--','tests').decode().splitlines()
    assert sorted(modified)==sorted('tests/expected/uninit/unresolved-calls/entry-'+s+'-'+m+'.rs' for s in ['initialized','partial'] for m in ['plain','seeded'])
    protected=['.github','scripts','Cargo.toml','Cargo.lock','rust-toolchain.toml','kani-compiler/src/codegen_aeneas_llbc','kani-compiler/src/codegen_cprover_gotoc','kani-compiler/src/kani_middle/transform/mod.rs','kani-compiler/src/kani_middle/transform/delayed_cache.rs']
    assert not git('diff','--name-only',e.BASE,'--',*protected)
    subprocess.run(['git','-C',str(e.REPO),'diff','--check',e.BASE],check=True)
    head=git('rev-parse','HEAD').decode().strip()
    report={'status':'PASS_STATIC_ONLY','base_sha':e.BASE,'validator_sha256':digest(Path(__file__).read_bytes()),
        'owner4_part_hashes_checked':len(parts),'all_canonical_part_hashes_checked':True,
        'changed_paths':sorted(intended),'selected_whole_fixtures':len(selected),'stage5_fixture_ids':[r['id'] for r in deferred],
        'earlier_obligations_targeted4':sorted(required-moved),'newly_deferred_to5':sorted(moved),
        'production_files_exact_F':sorted(prod-{prefix+'ty_layout.rs',prefix+'delayed_ub/mod.rs'}),
        'limits':'Git/source-token/manual review only; no Rust AST/MIR/name resolution/typechecking; no integration/proof acceptance.',
        'native_fmt_build_clippy_units_tests_verifier_CI_push':'NOT_RUN','worker15_review':'PENDING','formal_proof_credit':'NOT_ESTABLISHED'}
    if head!=e.BASE:
        assert git('show','-s','--format=%P',head).decode().strip()==e.BASE
        assert not git('status','--porcelain')
        report.update(source_sha=head,source_tree=git('rev-parse',head+'^{tree}').decode().strip())
        audit=json.loads((HERE/'SEAM-AUDIT-04.json').read_text())
        assert audit['head']==head and audit['base']==e.BASE and not audit['errors']
        assert audit['status']=='PASS_BOUNDED_STATIC_SEAM_AUDIT'
        report['compile_seam_audit']={'status':audit['status'],'report':'SEAM-AUDIT-04.json','native_compile':'NOT_RUN'}
        for name,start,end in [('source.patch',e.BASE,head),('residual-to-F.patch',head,e.F)]:
            patch=git('diff','--binary','--full-index',start,end);(HERE/name).write_bytes(patch)
            with tempfile.TemporaryDirectory(prefix='slice04-index-') as tmp:
                env=dict(os.environ,GIT_INDEX_FILE=str(Path(tmp)/'index'))
                def run(*args): return subprocess.check_output(['git','-C',str(e.REPO),*args],env=env)
                run('read-tree',start)
                subprocess.run(['git','-C',str(e.REPO),'apply','--cached',str(HERE/name)],env=env,check=True)
                actual=run('write-tree').decode().strip()
                assert actual==git('rev-parse',end+'^{tree}').decode().strip()
            report[name]={'sha256':digest(patch),'alternate_index_target_tree':actual}
    (HERE/'STATIC-VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['changed_paths','stage5_fixture_ids','earlier_obligations_targeted4','production_files_exact_F']},indent=2))

if __name__=='__main__': main()
