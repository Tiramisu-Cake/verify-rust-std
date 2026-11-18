#!/usr/bin/env python3
"""Independent14 offline review checks. Never build, compile or run proof roots."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent / 'batch-r4'
CONTROL = Path('/root/kani-ch8-s2-r4-final-w13')
Q = CONTROL / 'ch8-s1-control'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True
sys.path.insert(0, str(Q))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def main():
    # Verify all committed package bytes before using its audited static helper.
    entries = []
    for line in (PACKAGE / 'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.lstrip('*')
        assert sha(PACKAGE / name) == digest, name
        entries.append(name)
    assert len(entries) == 47
    assert set(entries) | {'MANIFEST.sha256'} == {p.name for p in PACKAGE.iterdir()}
    pins = json.loads((PACKAGE / 'PINS.json').read_text())
    assert pins['source']['sha'] == '16aa3557742e1b8a8b64b3b3d49da23d988027f8'
    assert pins['control']['sha'] == 'db81e62d76cfa193b1d7fe8e8ebbecead7e20ef8'
    assert pins['control']['request_sha256'] == '800fa67f8b7dcd8efdb228b72c0131f77d3676b3a1f46e1c06ba29a93cb77512'
    dump('INPUTS.json', {'package_commit': '4e2801660d89d75a1357a420c78cd435159c35b3',
                        'pins': pins, 'manifest_files_verified': len(entries),
                        'validator_sha256': sha(PACKAGE / 'validate_package.py')})
    # Re-run actual final-object offline tests, independently of author transcript.
    argv = [sys.executable, '-m', 'unittest', '-v', 'test_runner.py',
            'test_s107.FinalizationTests', 'test_s2.py', 'test_cfg_pfc.py',
            'test_rustc_diagnostics.py', 'test_contract_stacks.py']
    test = subprocess.run(argv, cwd=Q, env=os.environ.copy(), capture_output=True, text=True)
    (OUT / 'FINAL-TESTS.txt').write_text(test.stdout + test.stderr)
    assert test.returncode == 0, test.stderr
    assert 'Ran 84 tests in ' in test.stderr and test.stderr.endswith('\nOK\n')
    # Execute the reviewed package validator with its two output writes redirected.
    # Its HERE remains the immutable input package; no candidate file is written.
    script = (PACKAGE / 'validate_package.py').read_text()
    assert script.count('(HERE / name).write_text') == 1
    assert script.count("(HERE/'PREBUILD-SOURCE-PREFLIGHT.txt').write_text") == 1
    script = script.replace('(HERE / name).write_text', '(REVIEW_OUT / name).write_text')
    script = script.replace("(HERE/'PREBUILD-SOURCE-PREFLIGHT.txt').write_text",
                            "(REVIEW_OUT/'PREBUILD-SOURCE-PREFLIGHT.txt').write_text")
    scope = {'__file__': str(PACKAGE / 'validate_package.py'), '__name__': 'review_validator',
             'REVIEW_OUT': OUT}
    exec(compile(script, str(PACKAGE / 'validate_package.py'), 'exec'), scope)
    scope['main']()
    # Independent alias-chain discriminator. Reseal semantic fixtures by dropping
    # only source-hash checks, exactly as the supplied mutation tests do.
    import cfg_pfc as c
    import ordinary_contracts as ordinary
    import runner
    import s2_correspondence as corr
    sources = json.loads((Q / 'S2-SOURCE.json').read_text())
    request = copy.deepcopy(runner.load_request())
    for key in ('cfg_pfc_source_sha256', 'ordinary_contract_source_sha256'):
        request.pop(key)
    cases = []
    with tempfile.TemporaryDirectory(prefix='review14-alias-') as tmp:
        root = Path(tmp)
        for rel, text in sources.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        path = root / corr.BATCH
        old = '#[kani::stub(s2_swap_seam,weak_swap)]'
        variants = {
            'baseline_r4': old,
            'direct_contracted': '#[kani::stub(swap_if_less,weak_swap)]',
            'single_alias_contracted': 'use crate::kani::stub as ordinary1;\n#[ordinary1(swap_if_less,weak_swap)]',
            'chained_alias_contracted': 'use crate::kani::stub as ordinary1;\nuse self::ordinary1 as ordinary2;\n#[ordinary2(swap_if_less,weak_swap)]',
        }
        for label, replacement in variants.items():
            # Imports belong at module scope before all harness attributes;
            # never insert a use between #[kani::proof] and its function.
            prefix, attr = replacement.rsplit('\n', 1) if replacement.startswith('use ') else ('', replacement)
            path.write_text(prefix + '\n' + sources[corr.BATCH].replace(old, attr))
            row = {'case': label, 'old': old, 'replacement': replacement,
                   'mutation_file': corr.BATCH}
            for name, gate in [('ordinary_gate', ordinary.check), ('combined_cfg_pfc_gate', c.check)]:
                try:
                    result = gate(root, request)
                    records = result['checked_active_ordinary_uses']
                    row[name] = {'status': result['status'], 'binding_count': len(records),
                                 'sort13_weak_records': [r for r in records if r['harness'].endswith('::sort13_weak')]}
                except c.GateError as exc:
                    row[name] = {'status': 'REJECT', 'diagnostic': str(exc)}
            cases.append(row)
    assert cases[0]['ordinary_gate']['status'] == 'STATIC_PASS'
    assert all(cases[i]['ordinary_gate']['status'] == 'REJECT' for i in (1, 2))
    assert cases[3]['ordinary_gate']['status'] == 'STATIC_PASS'
    assert cases[3]['combined_cfg_pfc_gate']['status'] == 'STATIC_PASS'
    assert not cases[3]['ordinary_gate']['sort13_weak_records']
    dump('ALIAS-DISCRIMINATOR.json', {
        'source_sha': pins['source']['sha'], 'control_sha': pins['control']['sha'],
        'cases': cases,
        'limitation': 'Synthetic source-gate check only; native macro expansion/compilation NOT_RUN. Exact immutable request hashes would separately reject mutation.',
        'finding': 'Unsupported chained alias silently removes active ordinary stub from both gate inventories; neither resolves nor fails closed.'})
    # Input package was not modified by tests or helper redirection.
    for line in (PACKAGE / 'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        assert sha(PACKAGE / name.lstrip('*')) == digest
    dump('CHECKS.json', {'package_manifest': '48_FILES_47_HASHES_MATCH',
                        'final_object_tests': {'count': 84, 'exit': test.returncode, 'argv': argv,
                                               'transcript_sha256': sha(OUT / 'FINAL-TESTS.txt')},
                        'static_validator': 'PASS_OUTPUT_REDIRECTED_ONLY',
                        'alias_discriminator': 'REPRODUCED_FAIL_OPEN',
                        'native_compile': 'NOT_RUN', 'causal_repair': 'NOT_RUN',
                        'actual_failing_r3_unit_body': 'UNKNOWN', 'proof_credit': 'NONE'})
    print('REVIEW_CHECKS_COMPLETE: 84 tests pass; exact validator pass; chained-alias fail-open reproduced')


if __name__ == '__main__':
    main()
