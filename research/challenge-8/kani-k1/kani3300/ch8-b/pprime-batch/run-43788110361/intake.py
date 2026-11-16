"""Static intake of the authorized curated B-02 ZIP; no compiler or CI calls.

Usage: python3 intake.py ARTIFACT.zip CONTROL_REPOSITORY > TABLE.json
CONTROL_REPOSITORY is read only; package objects are read with git show.
Only named curated JSON members are parsed; no workflow logs are opened.
"""
import collections
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

PACKAGE = '99dbb2157bdb4f0322bcb3677f4ee51991de2f28'
TRIGGER = 'f601ca74cab11954fbc4deaca853513d28f254a1'
ZIP_SHA = 'd67f61fbd18549741490e0b96843fd63f21a42eb37c7ba23d33087f6542b61f5'
PASS_REASONS = {
    3: 'N=1: stable general path returns at smallsort.rs:228 before any copy; fixed_inputs.rs:157-175.',
    28: 'N=13: verified swap stub replaces real copying body; insertion offset==len; no merge (helper_contracts.rs:78-100; smallsort.rs:332-354,667).',
    29: 'N=9: verified swap stub replaces real copying body; insertion offset==len; no merge (helper_contracts.rs:78-100; smallsort.rs:332-354,667).',
    50: 'N=0: both u8/u64 fallback branches skip insertion (merge.rs:398-413,537-546; smallsort.rs:201-204).',
    51: 'N=1: both u8/u64 fallback branches skip insertion (merge.rs:398-413,537-546; smallsort.rs:201-204).',
    73: 'u64 N=0: stable/general branches return at len<2 (merge.rs:357-424; smallsort.rs:228).',
    74: 'u64 N=1: stable/general branches return at len<2 (merge.rs:357-424; smallsort.rs:228).',
    75: 'u8 N=0: stable/general branches return at len<2 (merge.rs:357-424; smallsort.rs:228).',
    76: 'u8 N=1: stable/general branches return at len<2 (merge.rs:357-424; smallsort.rs:228).',
    226: 'Only evaluates has_efficient_in_place_swap type predicates, no sorting/copy (smoke.rs:15-34).',
    229: 'Only evaluates type sizes, traits and route thresholds, no sorting/copy (tag_permutation.rs:71-101).',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    archive, repo = map(Path, sys.argv[1:])
    assert sha(archive.read_bytes()) == ZIP_SHA, 'GitHub artifact digest mismatch'

    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])

    def source(path):
        return git('show', PACKAGE + ':' + path)

    prefix = 'scripts/ch8-b-census/'
    manifest_bytes = source(prefix + 'roots.json')
    request_bytes = source(prefix + 'CI-REQUEST.json')
    manifest, req = json.loads(manifest_bytes), json.loads(request_bytes)
    assert git('rev-parse', TRIGGER + '^').decode().strip() == PACKAGE
    tree = git('rev-parse', PACKAGE + '^{tree}').decode().strip()
    assert git('rev-parse', TRIGGER + '^{tree}').decode().strip() == tree
    assert sha(manifest_bytes) == req['inventory']['manifest_sha256']
    assert len(manifest) == 235 and len({r['selector'] for r in manifest}) == 235
    assert all(r['intended_invalid_value'] is False for r in manifest)
    hashes = {}
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist()) == len(set(z.namelist())), 'duplicate ZIP member'

        def read(name):
            data = z.read(name)
            hashes[name] = sha(data)
            return json.loads(data)

        summary, binding, post = map(read, ['summary.json', 'binding.json', 'post-source.json'])
        before_binary, after_binary = map(read, ['binary-hashes.json', 'post-binary-hashes.json'])
        assert before_binary and before_binary == after_binary
        assert post['binary_hashes_unchanged'] is True
        assert binding['inventory_sha256'] == sha(manifest_bytes)
        assert binding['request_sha256'] == sha(request_bytes)
        for name in ['kani', 'std']:
            expected = dict(sha=req[name]['sha'], tree=req[name]['tree'], tracked_clean=True)
            assert binding[name] == post[name] == expected
        group = read('group.json')
        compile_receipt = read('std-compile.json')
        assert group['compile'] == compile_receipt
        assert group['exit'] == 1 and group['stop'] is None
        assert group['exception'] is None and group['signal'] is None
        assert compile_receipt['status'] == 'MARKER_OBSERVED'
        selectors = [r['selector'] for r in manifest]
        assert group['selectors'] == selectors
        argv = group['argv']
        assert [argv[i+1] for i, a in enumerate(argv) if a == '--harness'] == selectors
        assert argv.count('--exact') == 1 and argv.count('--jobs=1') == 1
        assert argv[argv.index('--harness-timeout')+1] == '600s'
        assert '--no-assert-contracts' in argv
        assert [argv[i+1] for i, a in enumerate(argv) if a == '-Z'] == [
            'unstable-options', *req['organizer_features'], 'valid-value-checks', 'export-json']
        expected_config = dict(cbmc_args=['--object-bits', '12'], coverage_enabled=False,
            checks=dict(assert_contracts=False, assertion_reach_checks=True,
                extra_pointer_checks=False, ignore_global_asm=False, memory_safety=True,
                overflow=True, prove_safety_only=False, undefined_function=True, unwinding=True))
        out = []
        identity = None
        export_sha = None
        for expected in manifest:
            member = 'root-%03d.json' % expected['id']
            row = read(member)
            assert all(row[k] == v for k, v in expected.items())
            assert row['schema'] == 'ch8-b-root-v1' and row['complete'] is True
            assert row['runtime_proof_status'] == 'ATTEMPTED'
            assert row['group_receipt'] == 'group.json'
            assert row['per_root_rss_bytes'] == 'UNKNOWN'
            if identity is None:
                identity, export_sha = row['export_identity'], row['export_sha256']
            assert row['export_identity'] == identity and row['export_sha256'] == export_sha
            h = row['harness']
            assert h['name'] == row['selector'] and h['crate_name'] == 'core'
            assert h['is_automatically_generated'] is False
            assert h['outcome']['kind'] == 'COMPLETED'
            checks, covers, failed = h['checks'], h['covers'], h['failed_properties']
            for buckets in [checks, covers]:
                assert all(buckets[k] == [] for k in ['error','other','undetermined','unknown'])
            assert h['n_failed'] == len(failed) == len(checks['failure'])
            assert set(checks['failure']) == {p['id'] for p in failed}
            assert checks['total'] == checks['success'] + len(failed) + len(checks['unreachable'])
            assert covers['total'] == sum(len(covers[k]) for k in ['satisfied','unsatisfiable','unreachable'])
            assert h['n_properties'] == checks['total'] + covers['total']
            assert {p['id'] for p in h['unsupported_constructs'] if p['status']=='FAILURE'} == set(checks['failure'])
            assert all(p['class']=='unsupported_construct' and p['status']=='FAILURE'
                and 'checking validity of `copy_nonoverlapping`' in p['description'] for p in failed)
            classification = 'copy Unsupported' if failed else 'PASS'
            assert row['classification'] == classification
            assert row['observed_classes'] == [classification]
            assert h['outcome']['verdict'] == ('FAILURE' if failed else 'SUCCESS')
            assert (row['id'] in PASS_REASONS) == (classification == 'PASS')
            out.append(dict(id=row['id'], root=row['root'], selector=row['selector'],
                historical_shard=row['shard'], classification=classification,
                intended_invalid_value=False, complete=True, receipt=member,
                receipt_sha256=hashes[member], failed_count=len(failed),
                exactly_one_failure=len(failed)==1,
                failures_only_copy_unsupported=bool(failed), other_failures=[],
                pass_source_explanation=PASS_REASONS.get(row['id']),
                harness=h))
        assert identity['kani_commit'] == req['kani']['sha']
        assert identity['kani_commit_dirty'] is False and identity['target'] == req['target']
        assert identity['run_state'] == 'COMPLETE' and identity['configuration'] == expected_config
        assert identity['enabled_unstable_features'] == sorted([
            *req['organizer_features'], 'unstable-options','valid-value-checks','export-json'])
        assert identity['harness_selection'] == dict(exact=True, matched_count=235,
            requested_filters=selectors, unmatched_filters=[])
        counts = dict(collections.Counter(r['classification'] for r in out))
        failure_counts = dict(collections.Counter(r['failed_count'] for r in out))
        assert counts == summary['counts'] == {'copy Unsupported':224, 'PASS':11}
        assert failure_counts == {0:11, 1:211, 2:13}
        assert summary['status'] == 'COMPLETE' and summary['completed'] == summary['expected'] == 235
        assert summary['job_status'] == 'success'
        result = dict(schema='ch8-b02-intake-v1', g0_input='4c8ad23a1b50293f4f7b42464ee6c0714431b520',
            assurance='STATIC_RECONCILIATION_OF_SOURCE_REPORTED_DIAGNOSTICS',
            proof_credit='NONE; neither B1 nor B2 newly established',
            provenance=dict(run=43788110361, artifact=14192030971, artifact_size_bytes=archive.stat().st_size,
                artifact_sha256=ZIP_SHA, github_digest_matched=True, trigger=TRIGGER,
                package=PACKAGE, package_tree=tree, binding=binding,
                export_sha256_source_reported=export_sha,
                raw_export_not_available=True, curated_member_sha256=hashes),
            summary=summary, failed_properties_per_root_histogram=failure_counts,
            failure_property_count=sum(r['failed_count'] for r in out),
            failing_copy_property_frequencies=dict(collections.Counter(
                p['id'] for r in out for p in r['harness']['failed_properties'])),
            group=dict(argv=argv, cwd=group['cwd'], exit=group['exit'],
                wall_s=group['wall_s'], peak_rss_bytes=group['peak_rss_bytes'],
                per_root_rss_bytes='UNKNOWN', compile={k:compile_receipt[k] for k in [
                    'status','boundary','wall_s','limit_s']}),
            export_identity=identity, rows=out)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
