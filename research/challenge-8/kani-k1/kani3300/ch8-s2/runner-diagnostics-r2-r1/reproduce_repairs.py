"""Bounded author repair fixtures, adapted from the exact reviewer reproductions.

No compiler, full runner or production evidence. All data are synthetic; temp
files are deleted. Native service behavior is exercised by the separate 29 tests.
"""
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import types

CONTROL = Path('/root/kani-ch8-s2-diagnostics-r2-r1-w11')
sys.path.insert(0, str(CONTROL/'ch8-s1-control'))
import check_package
import pack_evidence
import runner
import rustc_diagnostics as diagnostics

BASE = '2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8'
CANDIDATE = '472be8c3794d7a4530760ab7d5eae4ce950aa01c'


def unpack(root):
    pack_evidence.pack(root)
    return json.loads(gzip.decompress((root/pack_evidence.NAME).read_bytes()))


def missing_group():
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for stream in ('stdout', 'stderr'):
            cap = diagnostics.Capture(stream, 8192, root/'setup'/('rustc-'+stream+'-receipt.json'))
            cap.finish()
        # The exact selected production group; simulate interruption before its
        # execute() call, after a successful setup. No main runner is invoked.
        check_package.fallback(root, ['s2-batch3probes-u34'])
        artifact = unpack(root)
        group = json.loads(artifact['files']['groups/s2-batch3probes-u34/receipt.json']['text'])
        assert group['state'] == 'NOT_RUN_OR_INTERRUPTED'
        assert group['rustc_diagnostics']['complete'] is False
        assert artifact['diagnostic_retention']['complete'] is False
        assert list(artifact['rustc_diagnostics']) == ['groups/s2-batch3probes-u34', 'setup']
        return {'finding': 'B-01', 'result': 'AUTHOR_REPAIR_PASS_PENDING_REVIEW14',
                'group_state': group['state'], 'group_diagnostics': group['rustc_diagnostics'],
                'artifact_directories': list(artifact['rustc_diagnostics']),
                'artifact_diagnostic_retention': artifact['diagnostic_retention']}


def suggestion_context():
    text = (b'error[E0308]: mismatched types\n --> src/a.rs:1:1\n  |\n'
            b'1 | let n = 42;\n  |         ^^ expected &str\nhelp: replace the value\n  |\n'
            b'1 - let n = 42;\n1 + let n = "42";\n  |\n\n')
    results = []
    for stream in ('stdout', 'stderr'):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ('stdout', 'stderr'):
                cap = diagnostics.Capture(name, 8192, root/('rustc-'+name+'-receipt.json'))
                if name == stream:
                    # Single-byte feeds also check this is not a chunk artifact.
                    for byte in text:
                        cap.feed(bytes([byte]))
                cap.finish()
            value = json.loads((root/('rustc-'+stream+'-receipt.json')).read_text())
            retained = ''.join(b['text'] for b in value['blocks'])
            artifact = unpack(root)
            assert value['complete'] is True and value['dropped_bytes'] == 0
            assert retained == text.decode()
            assert value['retained_input_bytes'] == len(text)
            assert value['blocks'][0]['start_byte'] == 0 and value['blocks'][0]['end_byte'] == len(text)
            assert artifact['diagnostic_retention']['complete'] is True
            results.append({'stream': stream, 'input_bytes': len(text),
                'input_sha256': hashlib.sha256(text).hexdigest(), 'input_text': text.decode(),
                'retained_input_bytes': value['retained_input_bytes'],
                'complete': value['complete'], 'dropped_bytes': value['dropped_bytes'],
                'incomplete_reasons': value['incomplete_reasons'], 'blocks': value['blocks'],
                'artifact_complete': artifact['diagnostic_retention']['complete']})
    return {'finding': 'B-02', 'result': 'AUTHOR_REPAIR_PASS_PENDING_REVIEW14', 'cases': results,
            'fixture_provenance': 'Constructed rustc-style suggestion diff; not observed compiler output'}


def actual_baseline_middle():
    # Load exact old runner bytes, without invoking its main entry point.
    old_code = subprocess.check_output(['git', '-C', str(CONTROL), 'show',
                                       BASE+':ch8-s1-control/runner.py'])
    old = types.ModuleType('w14_baseline_runner')
    old.__file__ = str(CONTROL/'ch8-s1-control/runner.py')
    sys.modules[old.__name__] = old
    exec(compile(old_code, '<pinned-baseline-runner>', 'exec'), old.__dict__)
    block = b'error[E9999]: UNIQUE_MIDDLE_REVIEW14\n --> a.rs:1:1\n  = note: preserved context\n\n'
    payload = b'head\n' + b'noise\n'*14000 + block + b'noise\n'*14000 + b'tail\n'
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        class NoopRich:
            def feed(self, data): pass
            def finish(self): pass
        def state(): return {'stdout_kept': 0, 'stdout_bytes': 0, 'stdout_cap': False}
        old_state, new_state = state(), state()
        old._read_pipe(io.BytesIO(payload), root/'old.log', old.STDOUT_CAP_BYTES,
                       old_state, threading.Lock(), 'stdout', True, NoopRich())
        cap = diagnostics.Capture('stdout', runner.STDOUT_CAP_BYTES, root/'rustc-stdout-receipt.json')
        runner._read_pipe(io.BytesIO(payload), root/'new.log', runner.STDOUT_CAP_BYTES,
                          new_state, threading.Lock(), 'stdout', True, NoopRich(), cap)
        cap.finish()
        assert b'UNIQUE_MIDDLE_REVIEW14' not in (root/'old.log').read_bytes()
        assert b'UNIQUE_MIDDLE_REVIEW14' not in (root/'new.log').read_bytes()
        assert cap.document()['blocks'][0]['text'] == block.decode()
        assert old_state['stdout_bytes'] == new_state['stdout_bytes'] == len(payload)
        assert (root/'old.log').read_bytes() == (root/'new.log').read_bytes()
        return {'check': 'actual-baseline-vs-candidate-long-middle', 'result': 'PASS',
                'baseline_runner_sha256': hashlib.sha256(old_code).hexdigest(),
                'input_bytes': len(payload), 'input_sha256': hashlib.sha256(payload).hexdigest(),
                'baseline_and_candidate_preview_equal': True, 'baseline_missing_error': True,
                'candidate_retained_exact_block': True, 'block': cap.document()['blocks'][0]}


def main():
    actual = subprocess.check_output(['git', '-C', str(CONTROL), 'rev-parse', 'HEAD']).decode().strip()
    assert actual == CANDIDATE
    print(json.dumps({'candidate': CANDIDATE, 'assurance': 'BOUNDED_OFFLINE_SYNTHETIC',
        'checks': [actual_baseline_middle(), missing_group(), suggestion_context()],
        'production_retention': 'NOT_RUN', 'historical_cause': 'UNKNOWN', 'proof_credit': 'NONE'}, indent=2))


if __name__ == '__main__':
    main()
