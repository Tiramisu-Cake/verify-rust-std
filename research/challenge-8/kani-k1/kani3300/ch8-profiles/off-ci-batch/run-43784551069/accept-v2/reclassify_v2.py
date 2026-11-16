# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Replay the pinned JSON artifact and classify it with separately frozen v2 reviews."""
import argparse
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

from classifier_v2 import classify, consumers_after_leaves

HERE = Path(__file__).resolve().parent
BASE = '7a416079bbf17cdd8b64d5e01c2f10171e1baac6'
CONTROL = '112fcc9ada67ee2bb8e1712d47983d6717487b78'
SOURCE = '9fa2f7f97760584f38738909625c064006d8a936'
ZIP_SHA = '6b1f8ed210d93aae32b3e512565df7d6726d43660c19cb3c614f612f6b1a15e9'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def read(path):
    return json.loads(path.read_bytes())


def replay(args):
    require(digest(args.zip.read_bytes()) == ZIP_SHA, 'ZIP digest mismatch')
    require(git(args.control, 'rev-parse', 'HEAD').decode().strip() == CONTROL, 'control HEAD mismatch')
    require(not git(args.control, 'status', '--porcelain'), 'dirty control')
    root = Path(git(HERE, 'rev-parse', '--show-toplevel').decode().strip())
    for name in ('RECLASSIFY.json', 'reclassify.py'):
        path = HERE.parent / name
        require(path.read_bytes() == git(root, 'show', BASE + ':' + str(path.relative_to(root))),
                'historical intake changed: ' + name)
    # This trusted, unchanged Python replay validates source/binary before/after,
    # group execution/selection, request and every historical row snapshot.
    # No command or path taken from evidence is executed.
    with tempfile.TemporaryDirectory(prefix='prof-off-v2-') as temp:
        output = Path(temp) / 'intake.json'
        subprocess.run([sys.executable, str(HERE.parent / 'reclassify.py'), '--zip', str(args.zip),
                        '--control', str(args.control), '--output', str(output)],
                       stdout=subprocess.PIPE, check=True)
        intake = read(output)
    require(intake == read(HERE.parent / 'RECLASSIFY.json'), 'intake replay changed')
    tool_sources = read(HERE / 'TOOL-SOURCES.json')
    for name, sha in tool_sources['files'].items():
        require(digest(git(args.control, 'show', tool_sources['tool_commit'] + ':' + name)) == sha,
                'tool source hash mismatch: ' + name)
    source_map = read(HERE / 'SOURCE-MAP.json')
    require(source_map['source_commit'] == SOURCE, 'source map commit mismatch')
    source_text = {}
    for name, sha in source_map['source_files_sha256'].items():
        data = git(args.source, 'show', SOURCE + ':' + name)
        require(digest(data) == sha, 'source hash mismatch: ' + name)
        source_text[name] = data.decode().splitlines()
    for review in source_map['rows'].values():
        for cover in review['covers']:
            start = cover['source_line'] - 1
            require(type(start) is int and start >= 0, 'invalid cover source line')
            window = '\n'.join(source_text[cover['source_file']][start:start + 12])
            require(' '.join(window.split()).startswith(' '.join(cover['source_expression'].split())),
                    'cover source expression/line mismatch: ' + cover['id'])
    spec = importlib.util.spec_from_file_location('pinned_runner', args.control / 'ch8-prof-off-control/runner.py')
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    rows = runner.load_request(args.control / 'ch8-prof-off-control/CI-REQUEST.json')['rows']
    require(set(source_map['rows']) == {r['id'] for r in rows}, 'incomplete source mapping')
    mappings = {rid: {'binding': r['binding'], 'coverage': r['coverage']}
                for rid, r in source_map['rows'].items()}
    links, roles = read(HERE / 'UNSUPPORTED-LINKS.json'), read(HERE / 'UNREACHABLE-REVIEWS.json')
    previous = {r['id']: r for r in intake['rows']}
    results = {}
    with zipfile.ZipFile(args.zip) as archive:
        exports = {g: json.loads(archive.read(f'groups/group-{g:02d}/export.json')) for g in (0, 1)}
        for row in rows:
            prior = previous[row['id']]
            group = int(prior['group'].split('-')[-1])
            h = exports[group]['harnesses'][prior['harness_index']]
            result = classify(row, h, mappings[row['id']], links, roles.get(row['id'], {}),
                              prior['fixed_classifier']['state'])
            result.update(expected=row['expected'], evidence={
                'export_member': prior['export_member'], 'export_sha256': prior['export_sha256'],
                'harness_index': prior['harness_index'], 'harness_selector': row['selector'],
                'historical_receipt_preserved': True}, checks=h['checks'], covers=h['covers'],
                named_failures=h['failed_properties'], oracle=prior['oracle'],
                preflight_state=prior['fixed_classifier']['state'])
            results[row['id']] = result
    consumers_after_leaves(rows, results)
    values = [results[r['id']] for r in rows]
    result = {
        'schema': 'ch8-prof-off-policy-acceptance-v2', 'g0_input': BASE,
        'source_commit': SOURCE, 'control_commit': CONTROL, 'run': 43784551069,
        'artifact_zip_sha256': ZIP_SHA, 'assurance': 'STATIC_SOURCE_REVIEW_AND_SOURCE_REPORTED_JSON',
        'scope': 'Bounded closed instances; no independent compiler execution or B2/full-domain proof.',
        'proof_credit': 'NONE', 'historical_receipts_modified': False,
        'policy_sha256': digest((HERE.parents[4] / 'ACCEPTANCE-POLICY-BATCH.md').read_bytes()),
        'inputs_sha256': {name: digest((HERE / name).read_bytes()) for name in
                           ('classifier_v2.py', 'reclassify_v2.py', 'SOURCE-MAP.json',
                            'UNSUPPORTED-LINKS.json', 'UNREACHABLE-REVIEWS.json', 'TOOL-SOURCES.json')},
        'summary': {'rows': len(values), 'statuses': {s: sum(r['status'] == s for r in values)
                                                   for s in ('ACCEPTED', 'PENDING', 'UNKNOWN')},
                    'positive_statuses': dict(collections.Counter(r['status'] for r in values if r['expected'] == 'SUCCESS')),
                    'negative_statuses': dict(collections.Counter(r['status'] for r in values if r['expected'] != 'SUCCESS')),
                    'unsupported_decisions': dict(collections.Counter(u['decision'] for r in values for u in r['unsupported'])),
                    'unreachable_decisions': dict(collections.Counter(u['decision'] for r in values for u in r['unreachable'])),
                    'consumers': {r['id']: r.get('consumer_leaf') for r in values if 'consumer_leaf' in r},
                    'all_62_historical_snapshots_reproduced': True},
        'rows': values,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result['summary'], indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', required=True, type=Path)
    parser.add_argument('--control', required=True, type=Path)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    replay(parser.parse_args())


if __name__ == '__main__':
    main()
