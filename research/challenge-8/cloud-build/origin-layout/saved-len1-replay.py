#!/usr/bin/env python3
"""Read-only classifier replay on saved bytes; never prepares or runs proofs."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('--campaign', choices=('len1', 'caller'), default='len1')
    parser.add_argument('--build-id', required=True)
    parser.add_argument('--proof-sha', required=True)
    parser.add_argument('--archive-sha256', required=True)
    args = parser.parse_args()
    # These modules have inert imports; only parsing/classification routines run.
    target = load('saved_len1_classifier', HERE / 'onecell-drop-interface.py')
    drop = load('saved_len1_drop', HERE / 'concrete-drop-body.py')
    consumer = load('saved_len1_consumer', HERE / 'concrete-consumer.py')
    base = load('saved_len1_parsers', ROOT /
                'research/challenge-8/merge/overnight/copy-on-drop-prove.py')
    extraction = json.loads((args.evidence / 'extraction.json').read_text())
    caller = (load('saved_caller_classifier', HERE / 'onecell-caller-composition.py')
              if args.campaign == 'caller' else None)
    results = {}
    for name, row in extraction['cases'].items():
        case = args.evidence / 'cases' / name
        stages = {s: int((case / (s + '-exit-code.txt')).read_text())
                  for s in ('exporter', 'decode', 'refinement', 'verifast')}
        hashes = consumer._hashes(case)
        receipts = consumer._stage_receipts(case, stages, hashes)
        execution = {'stages': stages,
                     'source_files_unchanged': receipts['admitted'],
                     'source_unchanged_at_every_stage': receipts['admitted']}
        results[name] = (caller._classify(case, row, execution, base.mir_helper,
                                         base.ast_helper, target) if caller else
                         target._classify(name, case, row, execution, drop, base, consumer))
    print(json.dumps({'schema': 'onecell-saved-replay-v2', 'campaign': args.campaign,
                      'identity_note': 'caller supplied IDs; archive integrity must be verified independently',
                      'build_id': args.build_id, 'proof_sha': args.proof_sha,
                      'archive_sha256': args.archive_sha256,
                      'classifier_sha256': hashlib.sha256(
                          (HERE / ('onecell-caller-composition.py' if caller else
                                   'onecell-drop-interface.py')).read_bytes()).hexdigest(),
                      'fresh_proof': False, 'replay_is_new_proof': False,
                      'cases': results}, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
