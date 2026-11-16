# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Replay v2 unchanged, then apply complete per-row stdout role binding."""
import argparse
import collections
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import zipfile

from classifier_v3 import bind_stdout, digest, require, role

HERE = Path(__file__).resolve().parent
V2 = HERE.parent / 'accept-v2'
sys.path.insert(0, str(V2))
import classifier_v2 as policy
import reclassify_v2 as prior

G0 = '28a11b9b7af6d76c951df6518323af4a72b84919'


def read(path):
    return json.loads(path.read_bytes())


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def replay(args):
    root = Path(git(HERE, 'rev-parse', '--show-toplevel').decode().strip())
    dependencies = {}
    for path in V2.iterdir():
        if path.is_file():
            rel = str(path.relative_to(root))
            require(path.read_bytes() == git(root, 'show', G0 + ':' + rel),
                    'V2 dependency modified: ' + rel)
            dependencies[rel] = digest(path.read_bytes())
    with tempfile.TemporaryDirectory(prefix='prof-off-v3-') as temp:
        output = Path(temp) / 'v2.json'
        with contextlib.redirect_stdout(io.StringIO()):
            prior.replay(SimpleNamespace(zip=args.zip, control=args.control,
                                         source=args.source, output=output))
        v2 = read(output)
    require(v2 == read(V2 / 'ACCEPT.json'), 'V2 exact replay mismatch')
    rows = read(args.control / 'ch8-prof-off-control/CI-REQUEST.json')['rows']
    mappings = read(V2 / 'SOURCE-MAP.json')['rows']
    links = read(V2 / 'UNSUPPORTED-LINKS.json')
    rules = read(HERE / 'ROLE-RULES.json')['rules']
    source_sites = {}
    for file in sorted({r['file'].replace('\\.', '.') for r in rules if r['lines'] is not None}):
        # Rule file patterns use re.escape; resolve only from an explicit allowlist.
        require(file in {
            'library/core/src/fmt/mod.rs', 'library/core/src/ptr/const_ptr.rs',
            'library/core/src/num/uint_macros.rs', 'library/core/src/ub_checks.rs',
            'library/core/src/slice/sort/shared/smallsort.rs',
            'library/core/src/slice/sort/shared/smallsort/verify/merge/profiles.rs',
            'library/core/src/slice/sort/shared/smallsort/verify/merge.rs',
            'library/core/src/lib.rs', 'library/kani_core/src/models.rs'}, 'Unknown rule file')
        tool = file.startswith('library/kani_core/')
        commit, repo = (prior.CONTROL, args.control) if tool else (prior.SOURCE, args.source)
        source_sites[file] = {'commit': commit, 'sha256': digest(git(repo, 'show', commit + ':' + file))}
    previous = {r['id']: r for r in v2['rows']}
    results, group_identity = {}, {}
    with zipfile.ZipFile(args.zip) as archive:
        require(len(archive.namelist()) == len(set(archive.namelist())), 'Duplicate ZIP member')
        for row in rows:
            old = previous[row['id']]
            export_member = old['evidence']['export_member']
            group_name = export_member.split('/')[1]
            group_member = 'groups/' + group_name + '/receipt.json'
            compilation_member = 'groups/' + group_name + '/compile-receipt.json'
            group_data = archive.read(group_member)
            group, compilation = json.loads(group_data), json.loads(archive.read(compilation_member))
            export_data = archive.read(export_member)
            require(digest(export_data) == old['evidence']['export_sha256'] == group['export_sha256'],
                    'Group export hash mismatch')
            h = json.loads(export_data)['harnesses'][old['evidence']['harness_index']]
            group_identity[group_name] = {
                'receipt_sha256': digest(group_data),
                'compile_receipt_sha256': digest(archive.read(compilation_member)),
                'export_sha256': digest(export_data)}
            role_reviews, evidence, binding_error = {}, {}, None
            try:
                receipt_data = archive.read(row['id'] + '/receipt.json')
                data = archive.read(row['id'] + '/stdout.log')
                records, evidence = bind_stdout(data, row, h, json.loads(receipt_data), group, compilation)
                evidence['receipt_sha256'] = digest(receipt_data)
                for pid in h['checks']['unreachable']:
                    role_reviews[pid] = role(records[pid], rules)
            except (KeyError, ValueError, TypeError, AttributeError, UnicodeError) as exc:
                binding_error = type(exc).__name__ + ': ' + str(exc)
                evidence = {'state': 'UNKNOWN', 'reason': binding_error}
            result = policy.classify(row, h, mappings[row['id']], links, role_reviews,
                                     old['preflight_state'])
            if binding_error:
                result['unknown_reasons'].append('STDOUT_BINDING_UNKNOWN:' + binding_error)
                policy.finish(result)
            result.update(expected=old['expected'], evidence=old['evidence'], checks=h['checks'],
                          covers=h['covers'], named_failures=h['failed_properties'], oracle=old['oracle'],
                          preflight_state=old['preflight_state'], stdout_binding=evidence)
            results[row['id']] = result
    policy.consumers_after_leaves(rows, results)
    values = [results[r['id']] for r in rows]
    result = {
        'schema': 'ch8-prof-off-policy-acceptance-v3', 'g0_input': G0,
        'source_commit': prior.SOURCE, 'control_commit': prior.CONTROL,
        'run': 43784551069, 'artifact_id': 14190662926, 'artifact_zip_sha256': prior.ZIP_SHA,
        'assurance': 'STATIC_SOURCE_REVIEW_AND_SOURCE_REPORTED_JSON_AND_REGULAR_STDOUT',
        'scope': v2['scope'], 'proof_credit': 'NONE', 'historical_receipts_modified': False,
        'v2_exact_replay_sha256': digest((V2 / 'ACCEPT.json').read_bytes()),
        'v2_dependencies_sha256': dependencies, 'source_sites': source_sites,
        'group_identities': group_identity,
        'inputs_sha256': {name: digest((HERE / name).read_bytes()) for name in
                           ('classifier_v3.py', 'reclassify_v3.py', 'ROLE-RULES.json')},
        'summary': {
            'rows': len(values), 'statuses': dict(collections.Counter(r['status'] for r in values)),
            'positive_statuses': dict(collections.Counter(r['status'] for r in values if r['expected'] == 'SUCCESS')),
            'negative_statuses': dict(collections.Counter(r['status'] for r in values if r['expected'] != 'SUCCESS')),
            'stdout_binding': dict(collections.Counter(r['stdout_binding']['state'] for r in values)),
            'unreachable_decisions': dict(collections.Counter(u['decision'] for r in values for u in r['unreachable'])),
            'role_rules': dict(collections.Counter(u.get('rule') or 'UNKNOWN' for r in values for u in r['unreachable'])),
            'pending_reasons': dict(collections.Counter(p for r in values for p in r['pending_reasons'])),
            'consumers': {r['id']: r['consumer_leaf'] for r in values if 'consumer_leaf' in r},
            'all_62_historical_snapshots_reproduced': True},
        'rows': values}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result['summary'], indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ('zip', 'control', 'source', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    replay(parser.parse_args())
