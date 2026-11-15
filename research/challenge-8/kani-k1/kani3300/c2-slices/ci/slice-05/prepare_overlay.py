#!/usr/bin/env python3
"""Prepare stage5 exact-source CI-only overlay; never run native tools or CI."""
import hashlib
import json
from pathlib import Path
import subprocess
HERE = Path(__file__).resolve().parent
PACKET = HERE.parent.parent
ROOT = PACKET.parent
WORKTREE = Path('/root/kani-fix-3300-c2-slices-w15')
SOURCE = '96f5d5dc8dedd369c6986a4f1dd5e698b6167f0f'
RECIPE = '4f00e47d81da1e8849551e748ed378edbf868be1'
G0_INPUT = '7551f71dc20e3b2c464bbb5818df5ee29eb51d1c'


def git(*args):
    return subprocess.check_output(['git', '-C', str(WORKTREE), *args])


def main():
    assert git('rev-parse','HEAD').decode().strip() == SOURCE
    assert not git('status','--porcelain=v1')
    manifest = (PACKET/'slice-05/TEST-MANIFEST.json').read_bytes()
    source = json.loads((PACKET/'slice-05/SLICE.json').read_text())
    config = json.loads(git('show',RECIPE+':.github/c2-slices/inputs.json'))
    config.update(source_sha=SOURCE,source_tree=source['source_tree'],source_parent=source['base_sha'],g0_input=G0_INPUT,
        test_manifest_sha256=hashlib.sha256(manifest).hexdigest(),qualification_kind=source['qualification_kind'],
        integration_status='PENDING_NATIVE_EXACT_HEAD5',integration_heads=[5],accepted_parent_run='43710024495',
        accepted_recipe_overlay=RECIPE,effective_targeted_unit_count=20,
        packet_unit_expected_count_note='All four relevant inherited groups9+9+1+1=20; no F7 units before stage7.',
        sensitivity={'status':'REQUIRED_4_OF_4','manifest':'sensitivity-manifest.json','clean_expected_suite_required':True,
            'acceptance':'All four independent --force-rerun intended golden mismatches with completed native verdict/N; no compile/timeout/Unsupported detection.'})
    config['additional_units']['compiler-all-units'] = json.loads((HERE/'COMPILER-UNITS.json').read_text())
    config['effective_all_compiler_unit_count'] = 68
    ci = WORKTREE/'.github/c2-slices'
    ci.mkdir(parents=True,exist_ok=True)
    (ci/'inputs.json').write_text(json.dumps(config,indent=2)+'\n')
    (ci/'test-manifest.json').write_bytes(manifest)
    mutations=json.loads((ROOT/'c2-s5/SENSITIVITY-MANIFEST.json').read_text())
    mutations.update(source_candidate=SOURCE,source_tree=source['source_tree'],base=source['base_sha'],execution='NOT_RUN')
    for row in mutations['variants']:
        data=(ROOT/'c2-s5'/row['patch']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==row['patch_sha256']
        target=ci/row['patch'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        assert hashlib.sha256(git('show',SOURCE+':'+row['mutated_path'])).hexdigest()==row['input_sha256']
    (ci/'sensitivity-manifest.json').write_text(json.dumps(mutations,indent=2)+'\n')
    config['sensitivity']['manifest_sha256'] = hashlib.sha256((ci/'sensitivity-manifest.json').read_bytes()).hexdigest()
    (ci/'inputs.json').write_text(json.dumps(config,indent=2)+'\n')
    (ci/'sensitivity.py').write_bytes((HERE/'sensitivity.py').read_bytes())
    runner=git('show',RECIPE+':.github/c2-slices/slice04_ci.py').decode()
    runner=runner.replace('COMMANDS = {', 'COMMANDS = {\n    \"compiler-all-units\": [\"cargo\", \"test\", \"-p\", \"kani-compiler\", \"--\", \"--color\", \"never\"],')
    runner=runner.replace('import time\n','import time\nimport sensitivity\n')
    runner=runner.replace('for name in [*COMMANDS, *("suite-" + s for s, _ in suites(manifest))]:',
        'for name in [*COMMANDS, *("suite-" + s for s, _ in suites(manifest)), "sensitivity", *("sensitivity-" + r["id"] for r in json.loads((HERE / "sensitivity-manifest.json").read_text())["variants"])]:')
    runner=runner.replace('    else:\n        raise ValueError("unknown action: " + action)',
        '    elif action == "sensitivity":\n        good = sensitivity.run_sensitivity(sys.modules[__name__], out)\n    else:\n        raise ValueError("unknown action: " + action)')
    (ci/'slice05_ci.py').write_text(runner)
    workflow=git('show',RECIPE+':.github/workflows/uninit-quick.yml').decode()
    workflow=workflow.replace('C2 slices 04 STORAGE protocol and F6 qualification','C2 slices 05 CLOSURE and deferred integration qualification')
    workflow=workflow.replace('slice04_ci.py','slice05_ci.py').replace('c2-slices-04','c2-slices-05')
    workflow=workflow.replace('stage 4 manifest (413 unique selectors)','stage 5 manifest (460 unique selectors)')
    workflow=workflow.replace('      - name: Cumulative Quick and stage 5 manifest', "      - name: All compiler units (exactly 68, includes relevant20)\n        if: ${{ !cancelled() && steps.source_guard.outcome == 'success' }}\n        run: python3 .github/c2-slices/slice05_ci.py compiler-all-units\n        env:\n          C2_EVIDENCE_DIR: ${{ runner.temp }}/c2-slices-05-evidence\n\n      - name: Cumulative Quick and stage 5 manifest")
    workflow=workflow.replace('      - name: Source identities after\n',
        '      - name: S5 sensitivity mutations (4 independent intended golden failures)\n'
        '        if: ${{ !cancelled() && steps.source_guard.outcome == \'success\' }}\n'
        '        run: python3 .github/c2-slices/slice05_ci.py sensitivity\n'
        '        env:\n'
        '          C2_EVIDENCE_DIR: ${{ runner.temp }}/c2-slices-05-evidence\n\n'
        '      - name: Source identities after\n')
    for name in git('ls-tree','-r','--name-only',SOURCE,'--','.github/workflows').decode().splitlines():
        (WORKTREE/name).unlink()
    (WORKTREE/'.github/workflows/uninit-quick.yml').write_text(workflow)
    print('Prepared stage5 CI overlay; native builds/push/dispatch NOT_RUN.')


if __name__=='__main__':
    main()
