"""Independent bounded regression fixtures, not native compiler evidence."""
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

C = Path('/root/kani-ch8-s2-diagnostics-r2-r1-w11')
sys.path.insert(0, str(C/'ch8-s1-control'))
import check_package
import pack_evidence
import runner
import rustc_diagnostics as d

GROUP = 's2-batch3probes-u34'

def unpack(root):
    pack_evidence.pack(root)
    return json.loads(gzip.decompress((root/pack_evidence.NAME).read_bytes()))

def complete(root):
    for stream in ('stdout', 'stderr'):
        d.Capture(stream, 8192, root/('rustc-'+stream+'-receipt.json')).finish()

def b01():
    cases = []
    for kind in ('exact-fallback', 'both-streams-removed', 'selected-group-absent',
                 'row-group-absent', 'NOT_RUN', 'NOT_RUN_OR_INTERRUPTED', 'IN_PROGRESS', 'INTERRUPTED'):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            complete(root/'setup')
            group = root/'groups'/GROUP
            if kind == 'exact-fallback':
                check_package.fallback(root, [GROUP])
            elif kind == 'row-group-absent':
                (root/'receipt.json').write_text(json.dumps({'rows': [{'group': GROUP, 'status': 'PENDING'}]}))
            else:
                (root/'receipt.json').write_text(json.dumps({'selected_groups': [GROUP], 'rows': []}))
                if kind != 'selected-group-absent':
                    complete(group)
                    (group/'receipt.json').write_text(json.dumps({'state': 'FAILED' if kind == 'both-streams-removed' else kind,
                        'execution': {'original_exit_code': 42}, 'rustc_diagnostics': d.summary(group),
                        'outcome': 'UNKNOWN', 'proof_credit': 'NONE'}))
                    if kind == 'both-streams-removed':
                        assert unpack(root)['diagnostic_retention']['complete']
                        for stream in ('stdout', 'stderr'):
                            (group/('rustc-'+stream+'-receipt.json')).unlink()
            snapshots = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*.json')}
            artifact = unpack(root)
            assert artifact['rustc_diagnostics']['setup']['complete']
            assert not artifact['diagnostic_retention']['complete']
            summary = artifact['rustc_diagnostics']['groups/'+GROUP]
            assert not summary['complete'] and summary['unobserved_bytes'] is None
            assert 'groups/'+GROUP in artifact['diagnostic_retention']['expected_directories']
            for rel, data in snapshots.items():
                assert (root/rel).read_bytes() == data
                assert artifact['files'][rel]['text'].encode() == data
            cases.append({'case': kind, 'state': summary['execution_state'], 'reasons': summary['incomplete_reasons'],
                          'global_complete': artifact['diagnostic_retention']['complete'], 'source_receipts_unchanged': True})
    return {'finding': 'B-01', 'status': 'CLOSED', 'cases': cases}

def b02():
    fixture = (b'error[E0308]: mismatched types\n --> src/a.rs:1:1\n  |\n'
               b'1 | let n = 42;\n  |         ^^ expected &str\nhelp: replace the value\n  |\n'
               b'1 - let n = 42;\n1 + let n = "42";\n  |\n\n')
    assert len(fixture) == 165
    cases = []
    for stream in ('stdout', 'stderr'):
        for chunk in (1, 7, 4096):
            for ansi in (False, True):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    prefix = b'ordinary non-diagnostic prefix\n'
                    text = fixture + '  = note: café\nhelp: following context\n'.encode()
                    wire = text.replace(b'error[E0308]', b'\x1b[31merror[E0308]\x1b[0m').replace(b'1 +', b'\x1b[32m1 +\x1b[0m') if ansi else text
                    for name in ('stdout', 'stderr'):
                        cap = d.Capture(name, 8192, root/('rustc-'+name+'-receipt.json'))
                        if name == stream:
                            data = prefix+wire
                            for offset in range(0, len(data), chunk): cap.feed(data[offset:offset+chunk])
                        cap.finish()
                    doc = json.loads((root/('rustc-'+stream+'-receipt.json')).read_text())
                    assert doc['complete'] and doc['dropped_bytes'] == 0
                    assert len(doc['blocks']) == 1
                    block = doc['blocks'][0]
                    assert block['text'] == text.decode() and block['complete']
                    assert (block['start_byte'], block['end_byte']) == (len(prefix), len(prefix)+len(wire))
                    assert doc['retained_input_bytes'] == len(wire)
                    artifact = unpack(root)
                    assert artifact['diagnostic_retention']['complete']
                    assert json.loads(artifact['files']['rustc-'+stream+'-receipt.json']['text']) == doc
                    cases.append({'stream': stream, 'chunk': chunk, 'ansi': ansi, 'original_start': block['start_byte'],
                                  'original_end': block['end_byte'], 'text_sha256': hashlib.sha256(text).hexdigest(), 'packed_exact': True})
    return {'finding': 'B-02', 'status': 'CLOSED', 'original_fixture_bytes': 165, 'cases': cases}

def long_middle():
    # Reuse only the prior review's bounded baseline reader fixture, binding it
    # explicitly to the repaired implementation; do not re-audit unchanged code.
    source = Path('/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/ch8-s2/runner-diagnostics-r2-review/reproduce.py')
    module = types.ModuleType('prior_review_fixture')
    module.__file__ = str(source)
    exec(compile(source.read_bytes(), str(source), 'exec'), module.__dict__)
    module.CONTROL = C
    return module.actual_baseline_middle()

if __name__ == '__main__':
    assert subprocess.check_output(['git', '-C', str(C), 'rev-parse', 'HEAD']).decode().strip() == '472be8c3794d7a4530760ab7d5eae4ce950aa01c'
    print(json.dumps({'state': 'PASS', 'checks': [b01(), b02(), long_middle()],
                      'assurance': 'BOUNDED_OFFLINE_SYNTHETIC', 'native': 'NOT_RUN',
                      'historical_cause': 'UNKNOWN', 'proof_credit': 'NONE'}, indent=2))
