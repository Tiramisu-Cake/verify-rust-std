"""Execute targeted candidate service tests and frozen distinguishing control once."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

OUT = Path(__file__).resolve().parent
CONTROL = Path('/root/kani-ch8-s3-1-r2-control-w13')
FROZEN = 'fc29b93b1e333b73e55e2872701c80d9927f3b02'


def git(*args):
    return subprocess.check_output(['git', '-C', str(CONTROL), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def run(label, argv, cwd, env, timeout):
    record_path = OUT / (label + '-execution.json')
    assert not record_path.exists()
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start = time.monotonic()
    with (OUT / (label + '.stdout.txt')).open('xb') as stdout, (OUT / (label + '.stderr.txt')).open('xb') as stderr:
        result = subprocess.run(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr, timeout=timeout)
    record = dict(argv=argv, cwd=str(cwd), started_utc=started,
                  ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  exit_code=result.returncode, elapsed_seconds=time.monotonic() - start,
                  native='NOT_RUN', proof_credit='NONE')
    for stream in ('stdout', 'stderr'):
        record[stream + '_sha256'] = sha((OUT / (label + '.' + stream + '.txt')).read_bytes())
    record_path.write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    assert git('rev-parse', 'HEAD').decode().strip() == 'cb63033ffcde918f4341146e56373476b8eeb569'
    assert not git('status', '--porcelain=v1')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(CONTROL / 'ch8-s1-control'))
    rec = run('candidate', ['python3', '-m', 'unittest', '-v', 'test_s3_paths', 'test_s3_repair',
                             'test_path_delta14'], OUT, env, 240)
    assert rec['exit_code'] == 0
    closure = {}
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        names = git('ls-tree', '-r', '--name-only', FROZEN, '--', 'ch8-s1-control',
                    '.github/workflows/ch8-s2.yml').decode().splitlines()
        for name in names:
            data = git('show', FROZEN + ':' + name)
            dest = root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            closure[name] = sha(data)
        test_data = (CONTROL / 'ch8-s1-control/test_s3_paths.py').read_bytes()
        (root / 'ch8-s1-control/test_s3_paths.py').write_bytes(test_data)
        frozen_env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(root / 'ch8-s1-control'))
        rec = run('frozen', ['python3', '-m', 'unittest', '-v',
                            'test_s3_paths.RealPathWriterTests.test_workflow_relative_entry_real_writer_and_portable_replay'],
                  root / 'ch8-s1-control', frozen_env, 60)
        assert rec['exit_code'] == 1
        assert 'recorded worker binary drift: before' in (OUT / 'frozen.stderr.txt').read_text()
    (OUT / 'frozen-closure.json').write_text(json.dumps(dict(control=FROZEN, files=closure,
        added_fixture_sha256=sha(test_data), result='EXPECTED_REJECTION',
        historical_artifact_transformed=False), indent=2) + '\n')
    assert not git('status', '--porcelain=v1')
    print('23 targeted tests PASS; exact frozen workflow control rejects as expected')


if __name__ == '__main__':
    main()
