#!/usr/bin/env python3
"""Bounded distinguishing replays; real Python gates/writers/readers only.

Native execution/telemetry/Git in service fixtures are synthetic, as explicitly
defined by test_s4p_paths. Actual source preflight uses real pinned repositories.
"""
import copy
import datetime
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent / 's4p-1-r1'
CONTROL = Path('/root/kani-ch8-s4p-1-r1-control-w13/ch8-s1-control')
SOURCE = Path('/root/verify-rust-std-ch8-s4p-1-w13')
TOOL = Path('/root/kani-upstream-ch8-s1')
sys.path.insert(0, str(CONTROL))
import collect as public
import pack_evidence
import runner
import s4p_campaign as campaign
import s4p_contract_stacks as stacks
import s4p_policy as policy
import test_s4p_paths as fixtures
from validate_tokens import cached_tokens

def save(name, doc):
    (HERE / name).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + '\n')

def preflight():
    req = runner.load_request()
    original_policy, original_decl = policy.validate_source, stacks.declarations
    baseline = stacks.frozen()
    normalized = stacks.normalize(baseline)
    comparisons = {}
    reports = []
    def observe_decl(text, active, parent=()):
        result = list(original_decl(text, active, parent))
        if not parent and text in (baseline, normalized):
            comparisons.setdefault(frozenset(active), {})['old' if text == baseline else 'new'] = result
        return iter(result)
    def observe_policy(std, request):
        result = original_policy(std, request)
        reports.append(result)
        return result
    with mock.patch.object(policy, 'validate_source', side_effect=observe_policy), mock.patch.object(stacks, 'declarations', side_effect=observe_decl):
        result = runner.verify_source(SOURCE, TOOL, req, prebuild=True)
    assert len(reports) == 1 and reports[0]['status'] == 'STATIC_PASS'
    for name, report in reports[0]['reports'].items():
        assert report == json.loads((PACKET / ('MAP-' + name.upper() + '.json')).read_text())
    report = reports[0]['reports']['contract_stacks']
    keys = {'kani', 'kani_smallsort_sorting', 'kani_smallsort_s2_assumed', 'kani_smallsort_s3_leaf', 'kani_smallsort_s4_partition'}
    expected = {frozenset(part) for n in range(6) for part in itertools.combinations(keys, n)}
    actual = [frozenset(row['effective_cfg']) for row in report['cfg_projection_invariance']]
    assert len(actual) == len(set(actual)) == 32 and set(actual) == expected == set(comparisons)
    assert sum('kani_smallsort_sorting' in row for row in actual) == 16
    active_records = []
    for context in sorted((ctx for ctx in expected if stacks.ACTIVE <= ctx), key=lambda c: sorted(c)):
        pair = comparisons[context]
        assert set(pair) == {'old', 'new'} and len(pair['old']) == len(pair['new']) > 0
        wrappers = []
        for (old_name, _, old_attrs), (new_name, _, new_attrs) in zip(pair['old'], pair['new']):
            assert old_name == new_name
            old, new = stacks.contracts(old_attrs), stacks.contracts(new_attrs)
            assert [(x['op'], x['predicate_tokens']) for x in old] == [(x['op'], x['predicate_tokens']) for x in new]
            if any(x['family'] == 'safety_wrapper' for x in old):
                assert new and all(x['family'] == 'direct_kani' for x in new)
                wrappers.append({'function': '::'.join(old_name), 'clauses': len(new)})
        assert wrappers
        active_records.append({'cfg': sorted(context), 'compared_functions': len(pair['new']), 'normalized_wrappers': wrappers})
    assert len(active_records) == 4
    result = {'status':'PASS', 'actual_entry':'runner.verify_source(..., prebuild=True)',
              'source_result':result, 'all_four_reports_exact_match':True,
              'projections':32, 'sorting_enabled':16, 'ACTIVE':active_records,
              'source_files_sha256':report['source_files_sha256'], 'proof_credit':'NONE'}
    save('PREFLIGHT.json', result)
    print('Fresh actual source preflight and32/16/4 nonempty normalization comparisons PASS', flush=True)

def schema_matrix():
    records = []
    expected_schema = 'ch8-s4p-1-campaign-v1'
    # Independent table; expected identity comes from this trusted literal,
    # never from a mutated terminal or an old-schema bridge.
    variants = [('genuine', expected_schema), ('missing', None), ('null', None),
                ('old-bridge', 'ch8-s3s4-bridge1-campaign-v1'), ('int', 123),
                ('true', True), ('false', False), ('float', 1.0), ('list', []),
                ('object', {}), ('empty', ''), ('unknown', 'ch8-s4p-unknown-campaign-v1'),
                ('old-s3', 'ch8-s3-1-campaign-v1'), ('old-s32', 'ch8-s3-2-campaign-v1')]
    for scenario in ('FULL8', 'STOPPED0', 'PARTIAL0'):
        case = fixtures.RealPathWriterTests()
        with case.fixture() as fix:
            if scenario == 'FULL8':
                code, terminal = case.run_fixture(fix)
                assert code == 0 and len(terminal['s3_campaign']['completed']) == 8
            else:
                with mock.patch.object(campaign, 'check_usage', side_effect=campaign.GlobalFailure('independent14 prelaunch stop')):
                    code, terminal = case.run_fixture(fix)
                assert code == 1 and terminal['state'] == 'STOPPED' and terminal['s3_campaign']['completed'] == []
                if scenario == 'PARTIAL0':
                    terminal = campaign.finalize(fix[3], fix[4])
                    assert terminal['state'] == 'SELECTED_PARTIAL'
            out = fix[3]
            terminalpath = out / 'receipt.json'
            authentic = terminalpath.read_bytes()
            assert json.loads(authentic) == terminal and terminal['schema'] == expected_schema
            assert type(terminal['s3_campaign']['selected_roots']) is int and terminal['s3_campaign']['selected_roots'] == 8
            other = {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*.json') if p != terminalpath}
            upload = fix[0] / 'independent-schema-upload'
            upload.mkdir()
            try:
                for variant, value in variants:
                    mutated = json.loads(authentic)
                    if variant == 'missing':
                        del mutated['schema']
                    else:
                        mutated['schema'] = value
                    assert {k:v for k,v in mutated.items() if k != 'schema'} == {k:v for k,v in terminal.items() if k != 'schema'}
                    campaign.atomic(terminalpath, mutated)
                    pack_evidence.pack(out)
                    (upload / pack_evidence.NAME).write_bytes((out / pack_evidence.NAME).read_bytes())
                    assert [p.name for p in upload.iterdir()] == [pack_evidence.NAME]
                    accepted_results = []
                    for route_name, route in (('LOCAL', out), ('UPLOAD_ONLY', upload)):
                        original_read = public.read
                        with mock.patch.object(public, 'legacy_collect', wraps=public.legacy_collect) as collect_spy, mock.patch.object(public, 'read', wraps=original_read) as read_spy:
                            observed = None
                            error = None
                            try:
                                observed = public.collect([route], fix[4])
                            except campaign.GlobalFailure as exc:
                                error = str(exc)
                            if variant == 'genuine':
                                assert error is None and collect_spy.call_count == 1
                                assert len(observed['rows']) == 8 and observed['proof_credit'] == 'NONE'
                                assert sum(row['outcome'] == 'RECORDED' for row in observed['rows']) == len(terminal['s3_campaign']['completed'])
                                accepted_results.append(observed)
                            else:
                                assert observed is None and error == 'S4 terminal campaign schema mismatch'
                                assert collect_spy.call_count == 0
                                assert read_spy.call_args_list == [mock.call(route / 'receipt.json')]
                        records.append({'scenario':scenario, 'writer_state':terminal['state'], 'completed':len(terminal['s3_campaign']['completed']),
                                        'route':route_name, 'variant':variant, 'schema_present':'schema' in mutated, 'schema':mutated.get('schema'),
                                        'accepted':observed is not None, 'legacy_collection_calls':collect_spy.call_count,
                                        'error':error, 'only_terminal_read_before_reject':variant != 'genuine',
                                        'recorded_observations':None if observed is None else sum(row['outcome'] == 'RECORDED' for row in observed['rows'])})
                    if accepted_results:
                        assert len(accepted_results) == 2 and accepted_results[0] == accepted_results[1]
            finally:
                terminalpath.write_bytes(authentic)
            assert other == {str(p.relative_to(out)): p.read_bytes() for p in out.rglob('*.json') if p != terminalpath}
    bad = [r for r in records if not r['accepted']]
    good = [r for r in records if r['accepted']]
    original24 = [r for r in bad if r['variant'] in ('missing', 'null', 'old-bridge', 'int')]
    assert len(records) == 84 and len(bad) == 78 and len(good) == 6 and len(original24) == 24
    save('TERMINAL-SCHEMA-MATRIX.json', {'status':'PASS', 'records':records, 'malformed_rejected':len(bad), 'genuine_accepted':len(good), 'original24_rejected':len(original24), 'scope':'Authentic synthetic writer/finalizer, public collector and compact packer; no native/CI/proof credit'})
    print('Independent authentic terminal matrix:78 rejected before collection/6 accepted; original24 all reject', flush=True)

def prefixes():
    results = []
    for size in range(9):
        def fault(root, out, rid, tool, sup):
            if size < 8 and rid == campaign.p.ORDER[size]:
                raise campaign.GlobalFailure('independent14 prefix boundary')
        case = fixtures.RealPathWriterTests()
        with case.fixture(fault=fault) as fix:
            code, terminal = case.run_fixture(fix)
            assert code == (0 if size == 8 else 1)
            assert terminal['schema'] == 'ch8-s4p-1-campaign-v1'
            assert terminal['s3_campaign']['completed'] == list(campaign.p.ORDER[:size])
            assert type(terminal['s3_campaign']['selected_roots']) is int and terminal['s3_campaign']['selected_roots'] == 8
            local = public.collect([fix[3]], fix[4])
            pack_evidence.pack(fix[3])
            upload = fix[0] / 'prefix-upload'; upload.mkdir()
            (upload / pack_evidence.NAME).write_bytes((fix[3] / pack_evidence.NAME).read_bytes())
            assert public.collect([upload], fix[4]) == local
            assert len(local['rows']) == 8 and local['proof_credit'] == 'NONE'
            results.append({'prefix':size, 'schema':terminal['schema'], 'writer_state':terminal['state'], 'selected_roots':8, 'selected_roots_type':'int', 'routes':['LOCAL','UPLOAD_ONLY'], 'accepted':True})
    save('PREFIXES.json', {'status':'PASS', 'records':results, 'proof_credit':'NONE'})
    print('Genuine prefix0..8/int8 accepted on both public routes', flush=True)

def selected_tests():
    names = ['test_s4p_gate_repair',
             'test_s4p_boundary.SourceTests.test_required_path_unknown_callable_and_cell_projection_fail_closed',
             'test_s4p_boundary.SourceTests.test_missing_new_cfg_module_and_wrong_contract_target_fail_closed',
             'test_s4p_boundary.BoundaryTests.test_legacy_counts_profiles_and_runtime_caps_preserved']
    suite = unittest.defaultTestLoader.loadTestsFromNames(names)
    start = time.monotonic()
    with (HERE / 'TARGETED-TESTS.txt').open('w') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    save('TARGETED-TESTS.json', {'status':'PASS' if result.wasSuccessful() else 'FAIL', 'names':names, 'tests':result.testsRun, 'failures':len(result.failures), 'errors':len(result.errors), 'seconds':time.monotonic()-start, 'native_compile_CI':'NOT_RUN'})
    assert result.wasSuccessful()
    print('Actual CI-selected distinguishing regressions/source failure controls PASS:', result.testsRun, flush=True)

def main():
    start = time.monotonic()
    with cached_tokens():
        preflight()
        schema_matrix()
        prefixes()
        selected_tests()
    save('REPLAY.json', {'status':'PASS', 'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'seconds':time.monotonic()-start, 'request_sha256':runner.sha256(runner.REQUEST_PATH), 'control_sha':'2db5d2c08804036d283cb36450647cd584ee9e10', 'cfg_projections':32, 'sorting_enabled':16, 'ACTIVE_contexts':4, 'malformed_rejected_before_collection':78, 'genuine_accepted':6, 'original24_rejected':24, 'prefixes':list(range(9)), 'CI_selected_tests_passed':6, 'full_validate_repeated':False, 'native_compile_CI':'NOT_RUN', 'proof_credit':'NONE'})

if __name__ == '__main__':
    main()
