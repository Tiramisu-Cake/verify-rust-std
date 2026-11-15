#!/usr/bin/env python3
"""Prepare an exact-head review/CI handoff without executing any CI command."""
import copy
import importlib.util
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extract2', HERE / 'extract_slice.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
git, digest = e.git, e.digest
G0_INPUT = 'e84a43a9b26b0190485b751c64e9b5ccae34b27e'


def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def identity(ref, path):
    row = git('ls-tree', ref, '--', path).decode().strip()
    if not row:
        return None
    mode, _, blob = row.split('\t')[0].split()
    return {'mode': mode, 'blob': blob, 'sha256': digest(git('cat-file', 'blob', blob))}


def main():
    head = git('rev-parse', 'HEAD').decode().strip()
    assert head != e.BASE and git('show', '-s', '--format=%P', head).decode().strip() == e.BASE
    assert not git('status', '--porcelain')
    tree = git('rev-parse', 'HEAD^{tree}').decode().strip()
    static = json.loads((HERE / 'STATIC-VALIDATION.json').read_text())
    assert static['source_sha'] == head
    maps = {name: digest((HERE.parent / name).read_bytes()) for name in [
        'source-map/B1--F.json', 'source-map/DEPENDENCIES.json', 'source-map/PRE-F7.json',
        'oracle-map/ORACLE-MAP.json', 'oracle-map/DOCS-MAP.json', 'oracle-map/DEPENDENCY-REVIEW.md']}
    dependencies = json.loads((e.MAP / 'DEPENDENCIES.json').read_text())['slices']['2']
    parts = dependencies['source_parts']
    assert len(parts) == static['owner2_part_hashes_checked'] == 52
    dump('SOURCE-PARTS.json', {'source_sha': head, 'canonical_map': '../source-map/B1--F.json',
        'canonical_map_sha256': maps['source-map/B1--F.json'], 'parts': parts,
        'semantics': 'All and only owner2 parts; complete shared seams and interim adaptations in REVIEW.md. Static source attribution, not AST/MIR binding.'})
    oracle = json.loads((HERE.parent / 'oracle-map/ORACLE-MAP.json').read_text())
    selected = [r for r in oracle['fixtures'] if r['owner_slice'] == 2 and r['earliest_runnable_head'] == 2]
    deferred = [r for r in oracle['fixtures'] if r['owner_slice'] == 2 and r['earliest_runnable_head'] > 2]
    consumers = [r for r in oracle['fixtures'] if r['id'].startswith(('mixed-promoted-allocations/', 'contract-immutable-masks/'))]
    def fixture(row, is_deferred=False):
        result = copy.deepcopy(row)
        result.update(source={'path': row['input'], **identity(e.F, row['input'])},
                      golden_identity={'path': row['golden'], **identity(e.F, row['golden'])},
                      result='NOT_RUN', integration_status='PENDING', closure_receipt=None,
                      owner2_parts={'file': 'SOURCE-PARTS.json', 'sha256': digest((HERE / 'SOURCE-PARTS.json').read_bytes())})
        for p in (row['input'], row['golden']):
            if is_deferred:
                assert not (e.REPO / p).exists(), p
            else:
                assert identity(head, p) == identity(e.F, p), p
        return result
    pending = [fixture(r, True) for r in deferred]
    pending_consumers = [fixture(r, True) for r in consumers]
    dump('ORACLE-DELTA.json', {'canonical_map': '../oracle-map/ORACLE-MAP.json', 'canonical_map_sha256': maps['oracle-map/ORACLE-MAP.json'],
        'selected_complete_fixtures': [fixture(r) for r in selected],
        'deferred_owner2_fixtures': pending, 'later_owner_immutable_consumers': pending_consumers,
        'map_changes_required': [], 'status': 'EXTRACTION_MATCHES_ACCEPTED_MAP; native NOT_RUN',
        'worker15_area': 'UNMODIFIED'})
    docs = json.loads((HERE.parent / 'oracle-map/DOCS-MAP.json').read_text())
    doc_parts = [{**d, 'added_segments': [r for r in d['added_segments'] if r['owner_slice'] == 2]}
                 for d in docs['documents'] if any(r['owner_slice'] == 2 for r in d['added_segments'])]
    for d in doc_parts:
        d.pop('removed_U_lines', None)
    adaptations = [
        {'path': 'kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs',
         'change': 'Remove the single leading empty line inside impl PointeeInfo after omitting adjacent owner4 methods.',
         'kind': 'WHITESPACE_ONLY', 'final_resolution': 'No residual semantic adaptation; head4 inserts its methods at the same seam.'},
        {'path': 'docs/src/rust-feature-support.md', 'change': 'Insert exact owner2 immutable paragraphs before retained baseline issue link, with paragraph separation.',
         'kind': 'INTERIM_PLACEMENT', 'final_resolution': 'Head6 composes all owned segments and removes baseline issue sentence exactly as F.'},
        {'path': 'docs/src/reference/experimental/contracts.md', 'change': 'Join Whole/immutable line break and replace described there with explicit uninitialized-memory support link; insert before existing conclusion without future Limitations header.',
         'kind': 'INTERIM_LINK_AND_REFLOW', 'final_resolution': 'Head6 restores exact F wording/placement after owner4/6 header and general link exist.'},
    ]
    dump('DOCS-PARTS.json', {'canonical_map_sha256': maps['oracle-map/DOCS-MAP.json'], 'documents': doc_parts,
                            'adaptations': adaptations[1:], 'final_exact_F_required_on_head': 6})
    # Retain all accepted head1 regression selectors and their original flags/goldens.
    manifest = json.loads((HERE.parent / 'slice-01/TEST-MANIFEST.json').read_text())
    manifest.update(source_sha=head, qualification_kind='TARGETED_IMMUTABLE_AND_CUMULATIVE_REGRESSION', runtime='NOT_RUN',
                    immutable_unit_names=static['immutable_unit_names'], immutable_unit_expected_count=9,
                    unit_expected_count=18, inherited_from={'head': e.BASE, 'accepted_run': '43696666260',
                    'manifest_sha256': digest((HERE.parent / 'slice-01/TEST-MANIFEST.json').read_bytes())})
    for group in manifest['groups']:
        if group['name'] == 'common_expected':
            for row in selected:
                records = []
                for p in (row['input'], row['golden']):
                    directives = [x for x in git('show', head + ':' + p).decode().splitlines()
                                  if re.match(r'\s*//\s*(kani-flags|compile-flags|ignore|xfail)', x)]
                    records.append({'path': p, 'identity': identity(head, p), 'original_directives': directives})
                group['selectors'].append({'selector': '[expected] ' + row['input'].removeprefix('tests/'),
                    'input': row['input'], 'files': records, 'existing_path_ignore': False, 'result': 'NOT_RUN'})
            group['selectors'].sort(key=lambda r: r['selector'])
            group['static_discovery_count'] = len(group['selectors'])
        # Exact before/after file hashes for inherited selectors stay identical.
        for row in group['selectors']:
            for record in row['files']:
                assert identity(head, record['path']) == record['identity'], record['path']
    unique = {(g['suite'], g['mode'], r['selector']): r for g in manifest['groups'] for r in g['selectors']}
    counts = Counter(k[0] for k in unique)
    ignored = Counter(k[0] for k,r in unique.items() if r['existing_path_ignore'])
    manifest['deduplicated_suite_counts'] = {s: {'selectors': n, 'existing_path_ignored': ignored[s], 'expected_passed_if_all_succeed': n - ignored[s]} for s,n in sorted(counts.items())}
    manifest['deduplicated_selector_count'] = len(unique)
    dump('TEST-MANIFEST.json', manifest)
    changed = git('diff', '--name-only', e.BASE, head).decode().splitlines()
    changed_records = [{'path': p, 'parent': identity(e.BASE, p), 'source': identity(head, p), 'F': identity(e.F, p)} for p in changed]
    dump('SLICE.json', {
        'slice': 2, 'name': 'IMMUTABLE M1/E2+F5', 'status': 'READY_FOR_WORKER15_REVIEW_AND_COORDINATOR_CI',
        'source_sha': head, 'source_tree': tree, 'base_sha': e.BASE, 'parents': [e.BASE],
        'B1_dependency': e.B1, 'reference_F': e.F, 'reference_F_tree': '9829702c1aa0ecb73c860fc0ad5451757917d6cb',
        'g0_input': G0_INPUT, 'maps': maps,
        'parent_acceptance': {'kind': 'NO_REGRESSION', 'run': '43696666260', 'path': '../slice-01/ci-43696666260/ACCEPTANCE.md',
            'integration_status': 'PENDING', 'integration_heads': [4, 5], 'deferred_obligations': '../slice-01/DEFERRED-OBLIGATIONS.json'},
        'changed_files': changed_records, 'source_parts': {'file': 'SOURCE-PARTS.json', 'count': len(parts)},
        'borrowed_prerequisite': {'owner': 2, 'accepted_decision': 'post-stage0 variant C',
            'helpers': ['immutable_origin_type_supported + export', 'wrapper_inner', 'maybe_uninit_storage', 'PointeeInfo::for_storage', 'required imports'],
            'later_consumers': [4, 5], 'typed_deinit_argument_protocol_helpers_imported': False},
        'adaptations': adaptations, 'F7_imported': False, 'pre_F7_parent_writers_preserved': True,
        'selected_complete_fixture_ids': [r['id'] for r in selected], 'immutable_unit_count': 9,
        'deferred_owner2_fixtures': pending, 'later_owner_immutable_consumers': pending_consumers,
        'qualification_kind': 'TARGETED_IMMUTABLE_AND_CUMULATIVE_REGRESSION', 'qualification_status': 'NOT_RUN',
        'integration_status': 'PENDING', 'deferred_integration_heads': [3, 4, 5],
        'no_native_execution': True, 'local_builds_push_CI': 'NOT_RUN', 'cloud_spend': 0,
        'worker15_review': 'PENDING', 'formal_proof_credit': 'NOT_ESTABLISHED',
        'closure_requires': 'Exact-head Quick with units9 + reached useful SUCCESS and intended negative oracles. Later owner2 fixtures close individually on heads3/4; contract consumers on5. No aggregate exit0 or historical F gate substitutes.',
        'patches': {k: static[k] for k in ['source.patch', 'residual-to-F.patch']},
        'dependents': [3, 4, 5, 6, 7],
    })
    dump('SOURCE-MAP-DELTA.json', {'canonical_map': '../source-map/B1--F.json', 'sha256': maps['source-map/B1--F.json'],
         'source_sha': head, 'consumed_owner': '2', 'consumed_parts': parts, 'remaining_owners': ['3','4','5','6','7'],
         'ownership_changes': [], 'adaptations': adaptations, 'full_logical_stack_recomposition': 'NOT_RUN',
         'residual_patch_endpoint_only': static['residual-to-F.patch']})
    req = {
        'source_sha': head, 'source_tree': tree, 'parent': e.BASE, 'status': 'PREPARED_NOT_DISPATCHED',
        'recipe': '0998b98867:.github/workflows/uninit-quick.yml', 'runner': 'ubuntu-24.04',
        'env': {'RUST_TEST_THREADS': '2'}, 'job_timeout_minutes': 120, 'test_timeout_seconds': 2400,
        'auto_retries': False, 'test_manifest': 'TEST-MANIFEST.json', 'static_counts': manifest['deduplicated_suite_counts'],
        'units': [{'filter': 'active_call_tests', 'expected': 9}, {'filter': 'immutable_allocations::tests', 'expected': 9}],
        'native_results': 'NOT_RUN', 'no_authorization_to_dispatch': True,
    }
    dump('CI-REQUEST.json', req)
    dump('MANIFEST.json', {'source_sha': head, 'source_tree': tree, 'base_sha': e.BASE,
        'files': [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())} for p in sorted(HERE.iterdir()) if p.is_file() and p.name != 'MANIFEST.json']})
    print(json.dumps({'source_sha': head, 'source_tree': tree, 'changed_paths': len(changed), 'parts': len(parts),
          'selected_fixtures': len(selected), 'deferred_owner2': len(pending), 'later_immutable_consumers': len(consumers),
          'suite_counts': manifest['deduplicated_suite_counts'], 'selectors': len(unique)}, indent=2))

if __name__ == '__main__':
    main()
