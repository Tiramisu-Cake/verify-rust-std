#!/usr/bin/env python3
"""Generate the exact-head worker14 handoff. Does not prepare or dispatch an overlay."""
import copy
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extract3', HERE / 'extract_slice.py')
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)
git, digest = e.git, e.digest
G0_INPUT = '76ff7005a20b84d6b063994094091766b5963c2d'


def dump(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def identity(ref, path):
    row = git('ls-tree', ref, '--', path).decode().strip()
    if not row:
        return None
    mode, _, blob = row.split('\t')[0].split()
    return {'mode': mode, 'blob': blob, 'sha256': digest(git('cat-file', 'blob', blob))}


def main():
    head = git('rev-parse', 'HEAD').decode().strip()
    assert git('show', '-s', '--format=%P', head).decode().strip() == e.BASE
    assert not git('status', '--porcelain')
    tree = git('rev-parse', head + '^{tree}').decode().strip()
    static = json.loads((HERE / 'STATIC-VALIDATION.json').read_text())
    assert static['source_sha'] == head and static['status'] == 'PASS_STATIC_ONLY'
    assert static['validator_sha256'] == digest((HERE / 'validate_slice.py').read_bytes())
    maps = {name: digest((HERE.parent / name).read_bytes()) for name in [
        'source-map/B1--F.json', 'source-map/DEPENDENCIES.json', 'source-map/PRE-F7.json',
        'source-map/SEAMS.md', 'oracle-map/ORACLE-MAP.json', 'oracle-map/DOCS-MAP.json',
        'oracle-map/DEPENDENCY-REVIEW.md', 'ci/QUICK-PLAN.json']}
    parts = e.parts_for('3')
    dump('SOURCE-PARTS.json', {'source_sha': head, 'canonical_map': '../source-map/B1--F.json',
        'canonical_map_sha256': maps['source-map/B1--F.json'], 'parts': parts,
        'ownership_correction': 'SOURCE-MAP-CORRECTION.json',
        'semantics': 'Canonical20 owner3 parts plus exactly two import parts moved4 to3; inherited owners1/2 unchanged. Token/source attribution, not AST/MIR binding.'})
    selected, deferred, moved = e.fixture_sets()
    correction = json.loads((HERE / 'ORACLE-MAP-CORRECTION.json').read_text())

    def fixture(row, pending=False):
        result = copy.deepcopy(row)
        result.update(source={'path': row['input'], **identity(e.F, row['input'])},
            golden_identity={'path': row['golden'], **identity(e.F, row['golden'])},
            result='NOT_RUN', integration_status='PENDING', closure_receipt=None,
            owner3_parts={'file': 'SOURCE-PARTS.json', 'sha256': digest((HERE / 'SOURCE-PARTS.json').read_bytes())})
        for p in [row['input'], row['golden']]:
            assert identity(head, p) is None if pending else identity(head, p) == identity(e.F, p), p
        return result

    selected_records = [fixture(r) for r in selected]
    pending_records = [fixture(r, True) for r in deferred]
    moved_records = [fixture(r, True) for r in moved]
    dump('DEFERRED-OBLIGATIONS.json', {'source_sha': head, 'integration_status': 'PENDING',
        'integration_heads': [4], 'qualification_kind_on3': 'NO_REGRESSION',
        'reassigned_fixture_owner': 4, 'first_executable_head': 4,
        'reassigned_fixtures': moved_records, 'layout_raw_obligations': pending_records,
        'inherited_owner1': {'status': 'PENDING', 'heads': [4, 5],
            'receipt': '../slice-01/DEFERRED-OBLIGATIONS.json'},
        'closure_requires': 'Exact cumulative head4 receipts per complete F fixture/golden with useful successes and intended failures; no Unsupported substitution, no closure via aggregate exit0.',
        'historical_run': correction['historical_run'],
        'historical_assurance': correction['historical_result_assurance']})
    dump('ORACLE-DELTA.json', {'canonical_map': '../oracle-map/ORACLE-MAP.json',
        'canonical_map_sha256': maps['oracle-map/ORACLE-MAP.json'],
        'selected_complete_fixtures': selected_records, 'deferred_owner3_fixtures': pending_records,
        'closes_owner2_fixture_presence_only': [r['id'] for r in selected if r['owner_slice'] == 2],
        'historical_owner2_receipts': '../slice-02/SLICE.json (unchanged; later-head runtime closure still PENDING)',
        'effective_map_correction': 'ORACLE-MAP-CORRECTION.json',
        'reassigned_owner4_fixtures': moved_records,
        'map_changes_required': correction['changes'], 'status': 'EXTRACTION_MATCHES_COORDINATOR_CORRECTED_MAP; native NOT_RUN',
        'worker15_area': 'UNMODIFIED'})
    docs = json.loads((HERE.parent / 'oracle-map/DOCS-MAP.json').read_text())
    doc_parts = [{'path': d['path'], 'added_segments': [r for r in d['added_segments'] if r['owner_slice'] == 3]}
        for d in docs['documents'] if any(r['owner_slice'] == 3 for r in d['added_segments'])]
    dump('DOCS-PARTS.json', {'canonical_map_sha256': maps['oracle-map/DOCS-MAP.json'],
        'documents': doc_parts, 'adaptations': [], 'intrinsics_exact_F': True,
        'general_scope_docs': 'Inherited owner2 paragraphs only; remaining scope belongs4/5/6.'})
    manifest = json.loads((HERE.parent / 'slice-02/TEST-MANIFEST.json').read_text())
    manifest.update(source_sha=head, qualification_kind='NO_REGRESSION',
        runtime='NOT_RUN', inherited_from={'head': e.BASE, 'accepted_run': '43701587141',
            'manifest_sha256': digest((HERE.parent / 'slice-02/TEST-MANIFEST.json').read_bytes())})
    for group in manifest['groups']:
        if group['name'] == 'common_expected':
            for row in selected:
                records = []
                for p in [row['input'], row['golden']]:
                    directives = [x for x in git('show', head + ':' + p).decode().splitlines()
                        if re.match(r'\s*//\s*(kani-flags|compile-flags|ignore|xfail)', x)]
                    records.append({'path': p, 'identity': identity(head, p), 'original_directives': directives})
                group['selectors'].append({'selector': '[expected] ' + row['input'].removeprefix('tests/'),
                    'input': row['input'], 'files': records, 'existing_path_ignore': False, 'result': 'NOT_RUN'})
            group['selectors'].sort(key=lambda r: r['selector'])
            assert len(group['selectors']) == 94
            group['static_discovery_count'] = len(group['selectors'])
        for row in group['selectors']:
            for record in row['files']:
                assert identity(head, record['path']) == record['identity'], record['path']
    unique = {(g['suite'], g['mode'], r['selector']): r for g in manifest['groups'] for r in g['selectors']}
    counts = Counter(k[0] for k in unique)
    ignored = Counter(k[0] for k, r in unique.items() if r['existing_path_ignore'])
    manifest['deduplicated_suite_counts'] = {s: {'selectors': n, 'existing_path_ignored': ignored[s],
        'expected_passed_if_all_succeed': n - ignored[s]} for s, n in sorted(counts.items())}
    manifest['deduplicated_selector_count'] = len(unique)
    assert len(unique) == 318
    dump('TEST-MANIFEST.json', manifest)
    changed = git('diff', '--name-only', e.BASE, head).decode().splitlines()
    changed_records = [{'path': p, 'parent': identity(e.BASE, p), 'source': identity(head, p),
        'F': identity(e.F, p)} for p in changed]
    patches = {k: static[k] for k in ['source.patch', 'residual-to-F.patch']}
    dump('INPUTS.json', {'g0_entry': G0_INPUT, 'base': e.BASE, 'B1': e.B1, 'F': e.F,
        'source_sha': head, 'source_tree': tree, 'maps': maps,
        'parent_acceptance': '../slice-02/ci-43701587141/ACCEPTANCE.md',
        'task': '../../../TASK-KANI3300-C2-SLICES.md', 'assigned_worktree': str(e.REPO),
        'authority': 'worker14 writer, stage3 rework only; coordinator variant C analogue; local Git/Python/static checks; no local native builds/push/CI',
        'rework_decision': {'path': 'ci-43704461635/RESULT.md', 'g0_sha': 'ddcc17f20e01c3073606d632a27e5fc9f5aea71b',
            'assurance': 'SOURCE_REPORTED_COORDINATOR_RECORD', 'source_sha': correction['historical_source']},
        'upstream_status': 'Pinned U+B1 stack; historical snapshot not refreshed in this extraction session.'})
    dump('SLICE.json', {'slice': 3, 'name': 'LAYOUT-RAW A1/A2',
        'status': 'READY_FOR_WORKER15_REVIEW_AND_COORDINATOR_CI', 'source_sha': head, 'source_tree': tree,
        'base_sha': e.BASE, 'parents': [e.BASE], 'B1_dependency': e.B1, 'reference_F': e.F,
        'reference_F_tree': '9829702c1aa0ecb73c860fc0ad5451757917d6cb', 'g0_input': G0_INPUT, 'maps': maps,
        'parent_acceptance': {'run': '43701587141', 'path': '../slice-02/ci-43701587141/ACCEPTANCE.md',
            'owner1_integration': 'PENDING on4/5; inherited unchanged'},
        'changed_files': changed_records, 'source_parts': {'file': 'SOURCE-PARTS.json', 'count': len(parts)},
        'borrowed_prerequisite': [{'kind': 'NEUTRAL_IMPORT', 'symbol': 'rustc_public::ty::UintTy',
            'from_owner': 4, 'to_owner': 3, 'record': 'SOURCE-MAP-CORRECTION.json',
            'authority': 'TASK neutral import with first consumer; no semantic ownership transfer'}], 'adaptations': [],
        'inherited_adaptations': '../slice-02/SLICE.json; exact pre-F7 writers/import + owner2 doc placement/reflow unchanged',
        'F7_imported': False, 'closure5_imported': False, 'storage4_imported': False,
        'selected_complete_fixture_ids': [r['id'] for r in selected],
        'selected_owner3_fixture_ids': [r['id'] for r in selected if r['owner_slice'] == 3],
        'owner2_consumers_introduced': [r['id'] for r in selected if r['owner_slice'] == 2],
        'deferred_owner3_fixtures': pending_records, 'deferred_integration_heads': [4],
        'integration_status': 'PENDING', 'integration_heads': [4],
        'deferred_obligations': 'DEFERRED-OBLIGATIONS.json',
        'reassigned_owner4_fixture_ids': [r['id'] for r in moved],
        'oracle_map_correction': 'ORACLE-MAP-CORRECTION.json',
        'oracle_map_correction_sha256': digest((HERE / 'ORACLE-MAP-CORRECTION.json').read_bytes()),
        'fixture_dependency_audit': 'FIXTURE-DEPENDENCY-AUDIT.json',
        'supersedes': {'source_sha': correction['historical_source'],
            'overlay_sha_prefix': correction['historical_overlay'], 'run': correction['historical_run'],
            'result': correction['historical_result'], 'assurance': correction['historical_result_assurance']},
        'qualification_kind': manifest['qualification_kind'], 'qualification_status': 'NOT_RUN',
        'nested_offset_integration_status': 'PENDING', 'raw_eq_runtime_status': 'NOT_RUN',
        'seam_audit': {'tool': '../seam-audit/check_seams.py', 'report': 'SEAM-AUDIT-03.json',
            'contracts': 'CALL-CONTRACTS-03.json', 'manual_review': 'COMPILE-SEAMS.md',
            'status': 'PASS_BOUNDED_STATIC_SEAM_AUDIT', 'synthetic_tests': '10 PASS', 'native_compile': 'NOT_RUN'},
        'closure_requires': 'Exact-head Quick NO_REGRESSION only on3; all18 reassigned fixtures plus nine nested Pat/enum/raw-eq-uninit/raw-MU obligations remain PENDING on4. Exact complete F fixture receipts with unchanged source parts/goldens required; no aggregate exit0 closes integration.',
        'no_native_execution': True, 'local_builds_push_CI': 'NOT_RUN', 'cloud_spend': 0,
        'worker15_review': 'PENDING', 'formal_proof_credit': 'NOT_ESTABLISHED',
        'patches': patches, 'dependents': [4, 5, 6, 7]})
    dump('SOURCE-MAP-DELTA.json', {'canonical_map': '../source-map/B1--F.json',
        'sha256': maps['source-map/B1--F.json'], 'source_sha': head, 'consumed_owner': '3',
        'consumed_parts': parts, 'remaining_owners': ['4', '5', '6', '7'],
        'ownership_changes': json.loads((HERE / 'SOURCE-MAP-CORRECTION.json').read_text())['owner_changes'],
        'source_map_area': 'UNMODIFIED; effective corrected inventory in this package', 'adaptations': [],
        'full_logical_stack_recomposition': 'NOT_RUN', 'residual_patch_endpoint_only': patches['residual-to-F.patch']})
    dump('CI-REQUEST.json', {'source_sha': head, 'source_tree': tree, 'parent': e.BASE,
        'status': 'PREPARED_NOT_DISPATCHED', 'qualification_kind': 'NO_REGRESSION', 'recipe': '0998b98867:.github/workflows/uninit-quick.yml',
        'runner': 'ubuntu-24.04', 'env': {'RUST_TEST_THREADS': '2'}, 'job_timeout_minutes': 120,
        'test_timeout_seconds': 2400, 'auto_retries': False, 'test_manifest': 'TEST-MANIFEST.json',
        'static_counts': manifest['deduplicated_suite_counts'], 'selector_count': len(unique),
        'units': [{'filter': 'active_call_tests', 'expected': 9}, {'filter': 'immutable_allocations::tests', 'expected': 9}],
        'targeted_oracles': 'ORACLE-DELTA.json:selected_complete_fixtures',
        'native_results': 'NOT_RUN', 'worker15_overlay': 'NOT_PREPARED_BY_WORKER14', 'no_authorization_to_dispatch': True})
    dump('MANIFEST.json', {'source_sha': head, 'source_tree': tree, 'base_sha': e.BASE,
        'files': [{'path': p.name, 'bytes': p.stat().st_size, 'sha256': digest(p.read_bytes())}
            for p in sorted(HERE.iterdir()) if p.is_file() and p.name != 'MANIFEST.json']})
    print(json.dumps({'source_sha': head, 'source_tree': tree, 'changed_paths': len(changed),
        'parts': len(parts), 'selected_fixtures': len(selected), 'deferred_owner3': len(deferred),
        'suite_counts': manifest['deduplicated_suite_counts'], 'selectors': len(unique)}, indent=2))


if __name__ == '__main__':
    main()
