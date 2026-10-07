#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only immutable replay; no compiler/verifier/exporter invocation."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import zipfile
import importlib.util

RUN = 37684590509
ARTIFACT = 11510757595
SOURCE = '6b63670c21bfa57d2531c4be57ac098df6111c5f'
ROOT = 'current/select-pointer/cfg-acceptance/'

def need(ok, why):
    if not ok: raise ValueError(why)

def main():
    need(os.environ.get('GITHUB_ACTIONS') == 'true' and
         os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted', 'hosted only')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--outer', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    run = json.loads((a.output/'original-run.json').read_text())
    artifact = json.loads((a.output/'original-artifact.json').read_text())
    need(run['id'] == RUN and run['head_sha'] == SOURCE and
         run['repository']['full_name'] == 'Tiramisu-Cake/verify-rust-std' and
         artifact['id'] == ARTIFACT and artifact['workflow_run']['id'] == RUN and
         artifact['workflow_run']['head_sha'] == SOURCE, 'immutable source pin differs')
    with zipfile.ZipFile(a.outer) as outer:
        names = [n for n in outer.namelist() if n.endswith('sort4-select-compact-evidence.zip')]
        need(len(names) == 1, 'compact archive missing or ambiguous')
        raw = outer.read(names[0])
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        manifest = json.loads(z.read('COMPACT-EVIDENCE-MANIFEST.json'))
        for entry in manifest['entries']:
            if entry['included']:
                data = z.read(entry['compact_entry'])
                need(hashlib.sha256(data).hexdigest() == entry['sha256'] and
                     len(data) == entry['file_size'], 'manifest bytes differ')
        def read(name): return z.read(ROOT+name)
        summary_bytes = read('summary.json')
        summary = json.loads(summary_bytes)
        old_bytes = read('false_unwind/summary.json')
        old = json.loads(old_bytes)
        stages = old['stages']
        source = read('false_unwind/verified/lib.rs')
        original = read('false_unwind/original/lib.rs')
        need(re.sub(rb'/\*@.*?@\*/', b'', source, flags=re.S) == original,
             'runtime source differs')
        hashes = {'original/lib.rs': hashlib.sha256(original).hexdigest(),
                  'verified/lib.rs': hashlib.sha256(source).hexdigest()}
        need(all(r['source_before'] == r['source_after'] == hashes and r['source_exact']
                 for r in stages.values()), 'stage source identity differs')
        need(stages['full-verification']['exit'] == 1 and
             all(stages[n]['exit'] == 0 for n in ('readonly-export', 'readonly-decode',
                 'normal-export', 'normal-decode', 'refinement')), 'wrong stage')
        log = read('false_unwind/full-verification.log').decode()
        ast = read('false_unwind/verified-ast.txt').decode()
        name = 'checked_unwind_call'
        location = 'verified/lib.rs(23,15-20)'
        need(source.splitlines()[22] == b'on_unwind_ens false;', 'contract coordinate differs')
        path = Path(__file__).with_name('forget-evidence-classifier.py')
        spec = importlib.util.spec_from_file_location('cfg_replay_strict', path)
        classifier = importlib.util.module_from_spec(spec)
        import sys
        sys.modules[spec.name] = classifier
        spec.loader.exec_module(classifier)
        expected = ['u32_sync', 'u32_share_mono', 'init_ref_readonly_points_to_shared',
                    'std::mem::close_MaybeUninit_pointer_own',
                    'std::mem::select_MaybeUninit_pointer_own',
                    'std::ptr::pointer_drop_glue_identity', 'potentially_panicking', name]
        predicate = {'file': 'verified/lib.rs', 'line': 23,
                     'message': 'Cannot prove condition. (Cannot prove false.)',
                     'function': name}
        actual = classifier.classify_unit(log, 1, expected, positive=False,
                                          expected_error=predicate)
        need(actual['accepted'] and actual['classification'] == 'INTENDED_NEGATIVE',
             'wrong proof obligation')
        need('ReturnStmt' in ast and '"unwinding"' in ast and
             'verified/lib.rs(26,14-38): Executing return statement' in log,
             'caller unwind return did not execute')
        controls = {
            'correct_obligation': actual['accepted'],
            'wrong_line_rejected': not classifier.classify_unit(log, 1, expected,
                positive=False, expected_error={**predicate, 'line': 20})['accepted'],
            'wrong_predicate_rejected': not classifier.classify_unit(log, 1, expected,
                positive=False, expected_error={**predicate, 'message': 'Parse error.'})['accepted'],
            'setup_failure_rejected': not classifier.classify_unit(
                location+': error: Parse error.\n', 1, expected,
                positive=False, expected_error=predicate)['accepted'],
            'exit_zero_rejected': not classifier.classify_unit(log, 0, expected,
                positive=False, expected_error=predicate)['accepted'],
            'unknown_function_rejected': not classifier.classify_unit(log, 1,
                expected[:-1]+['wrong_function'], positive=False,
                expected_error=predicate)['accepted'],
        }
        need(all(controls.values()), 'classifier controls failed')
        result = {'source_run': RUN, 'source_artifact': ARTIFACT, 'source_sha': SOURCE,
                  'archive_sha256': hashlib.sha256(raw).hexdigest(),
                  'original_summary_sha256': hashlib.sha256(summary_bytes).hexdigest(),
                  'original_false_unwind_summary_sha256': hashlib.sha256(old_bytes).hexdigest(),
                  'original_classification': old['classification'],
                  'new_separate_classification': 'INTENDED_PROOF_REJECTION',
                  'strict_replayed_result': actual, 'classifier_controls': controls,
                  'profile_status': 'UNACCEPTED', 'proof_rerun': False,
                  'remaining_gate': 'pointer-drop MIR cfg_unwind/extra_operation/contract and two pin controls',
                  'actual_linkage': 'NOT_RUN'}
        (a.output/'replay-result.json').write_text(json.dumps(result, indent=2)+'\n')
        (a.output/'original-summary.json').write_bytes(summary_bytes)
        (a.output/'original-false-unwind-summary.json').write_bytes(old_bytes)
        print(json.dumps({'new_separate_classification': result['new_separate_classification'],
                          'classifier_controls_pass': True, 'profile_status': 'UNACCEPTED'}))

if __name__ == '__main__': main()
