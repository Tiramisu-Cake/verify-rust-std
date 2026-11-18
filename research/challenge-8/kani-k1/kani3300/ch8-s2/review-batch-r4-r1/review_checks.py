#!/usr/bin/env python3
"""Same14 bounded delta validation. Offline/static/synthetic only."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent / 'batch-r4-r1'
G0 = Path('/root/verify-rust-std-kani3300-g0')
PACKAGE_SHA = '474e0b4209554bdd69c4303410192d2d472af4a2'
FROZEN_REVIEW = 'f5dd71722f82ac59e37152927a5f4dd9eee6ea1a'
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def verify_manifest(directory, commit):
    records = []
    for line in (directory / 'MANIFEST.sha256').read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        name = name.lstrip('*')
        data = (directory / name).read_bytes()
        assert sha(data) == digest, name
        rel = str((directory / name).relative_to(G0))
        assert data == git(G0, 'show', commit + ':' + rel), rel
        records.append({'path': name, 'sha256': digest})
    assert set(r['path'] for r in records) | {'MANIFEST.sha256'} == {p.name for p in directory.iterdir()}
    manifest_rel = str((directory / 'MANIFEST.sha256').relative_to(G0))
    assert (directory / 'MANIFEST.sha256').read_bytes() == git(G0, 'show', commit + ':' + manifest_rel)
    return records


def main():
    package_records = verify_manifest(PACKAGE, PACKAGE_SHA)
    assert len(package_records) == 59
    frozen_records = verify_manifest(OUT.parent / 'review-batch-r4', FROZEN_REVIEW)
    pins = json.loads((PACKAGE / 'PINS.json').read_text())
    assert pins['source']['sha'] == 'bd62e54df1b4749154790aa3db3cc7978f547f75'
    assert pins['control']['sha'] == '0e8c836857344866564e1423ad5d8d28bbc4106b'
    assert pins['control']['request_sha256'] == '9d165365933b6bc117311d7d52568f834bc2f083c2272800803a84883f286717'
    inputs = {'task_id': 'taskcf40e805eb47a5f11efdf27a62b06caf2bc2adff',
              'issued': 'owner17:29; explicit /new supersedes task reuse-context instruction',
              'package_commit': PACKAGE_SHA, 'frozen_review': FROZEN_REVIEW, 'pins': pins,
              'package_files': 60, 'package_hashes': package_records,
              'frozen_review_hashes': frozen_records}
    dump('INPUTS.json', inputs)
    q = Path(pins['control']['worktree']) / 'ch8-s1-control'
    sys.path.insert(0, str(q))
    # Run the exact final committed-object suite independently of author evidence.
    argv = [sys.executable, '-m', 'unittest', '-v', 'test_runner.py',
            'test_s107.FinalizationTests', 'test_s2.py', 'test_cfg_pfc.py',
            'test_rustc_diagnostics.py', 'test_contract_stacks.py']
    start = time.monotonic()
    with (OUT / 'FINAL-TESTS.txt').open('w') as stream:
        test = subprocess.run(argv, cwd=q, env=os.environ.copy(), stdout=stream, stderr=subprocess.STDOUT)
    transcript = (OUT / 'FINAL-TESTS.txt').read_text()
    assert test.returncode == 0 and 'Ran 96 tests in ' in transcript and transcript.endswith('\nOK\n')
    test_result = {'count': 96, 'exit': test.returncode, 'argv': argv, 'workdir': str(q),
                   'elapsed_seconds': round(time.monotonic() - start, 3),
                   'transcript_sha256': sha(transcript.encode()),
                   'scope': 'actual final committed objects; Python/static/synthetic only'}
    dump('TEST-PROVENANCE.json', dict(test_result, source=pins['source'], control=pins['control']))
    print('96 final-object offline tests PASS', flush=True)
    # Only redirect the validator's output writes; keep immutable package inputs.
    script = (PACKAGE / 'validate_package.py').read_text()
    assert script.count('(HERE / name).write_text') == 1
    assert script.count("(HERE/'PREBUILD-SOURCE-PREFLIGHT.txt').write_text") == 1
    script = script.replace('(HERE / name).write_text', '(REVIEW_OUT / name).write_text')
    script = script.replace("(HERE/'PREBUILD-SOURCE-PREFLIGHT.txt').write_text",
                            "(REVIEW_OUT/'PREBUILD-SOURCE-PREFLIGHT.txt').write_text")
    scope = {'__file__': str(PACKAGE / 'validate_package.py'), '__name__': 'review_validator', 'REVIEW_OUT': OUT}
    exec(compile(script, str(PACKAGE / 'validate_package.py'), 'exec'), scope)
    scope['main']()
    assert package_records == verify_manifest(PACKAGE, PACKAGE_SHA)
    assert frozen_records == verify_manifest(OUT.parent / 'review-batch-r4', FROZEN_REVIEW)
    dump('CHECKS.json', {'package_manifest': '60_FILES_59_HASHES_COMMITTED_MATCH',
                        'frozen_review_manifest': 'COMMITTED_MATCH_UNCHANGED',
                        'final_object_tests': test_result,
                        'static_validator': 'PASS_OUTPUT_WRITES_REDIRECTED_ONLY',
                        'native_compile': 'NOT_RUN', 'causal_repair': 'NOT_RUN',
                        'actual_r3_failing_unit_body': 'UNKNOWN', 'proof_credit': 'NONE'})
    print('REVIEW_CHECKS_COMPLETE', flush=True)


if __name__ == '__main__':
    main()
