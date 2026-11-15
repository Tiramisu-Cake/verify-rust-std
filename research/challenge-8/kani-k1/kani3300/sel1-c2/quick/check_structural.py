#!/usr/bin/env python3
"""Synthetic adapter/error-path checks only. No native invocation."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent / 'full-export/.github/c2-slices'))
import structural as runner
import structural_observation as CHECKER
from structural_observation import observation
from structural_compare import compare_root

def observation_fixture():
    source_rel = ".github/c2-slices/structural-mixed.rs"
    case = {"name": "immutable_hole_negative", "root_line": 22,
            "mode": "Assert", "target": None, "expected_verdict": "FAILURE"}
    data = CHECKER.load_export(
        CHECKER.ROOT / "tests/json-handler/schema-validation/fixture-completed-failure.json")
    data = copy.deepcopy(data)
    stamp = datetime.now(timezone.utc).replace(microsecond=0)
    data["started_at"] = stamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    data["enabled_unstable_features"] = sorted(
        ["uninit-checks", "function-contracts", "export-json", "unstable-options"])
    data["configuration"]["cbmc_args"] = ["--object-bits", "12"]
    data["configuration"]["coverage_enabled"] = False
    for key in ("memory_safety", "overflow", "unwinding", "undefined_function",
                "assertion_reach_checks", "assert_contracts"):
        data["configuration"]["checks"][key] = True
    for key in ("ignore_global_asm", "prove_safety_only"):
        data["configuration"]["checks"][key] = False
    data["harness_selection"] = {"requested_filters": [case["name"]], "exact": True,
                                 "unmatched_filters": [], "matched_count": 1}
    harness = data["harnesses"][0]
    harness.update(name=case["name"], file=source_rel, line=case["root_line"],
                   outcome={"kind": "COMPLETED", "verdict": "FAILURE"},
                   failure_kind="OTHER", n_properties=4, n_failed=2)
    harness["attributes"].update(kind="Proof", should_panic=False, stubs=[], verified_stubs=[])
    success = {"id": "root.assertion.1", "status": "SUCCESS", "description": "legal assertion",
               "location": f"{source_rel}:18:1 in function immutable_hole_negative"}
    failed = {"id": "root.read.1", "description": "bad read", "class": "safety_check",
              "file": source_rel, "line": "24", "trace_available": True, "status": "FAILURE"}
    unsupported = {"id": "root.unsupported.1", "description": "cycle boundary",
                   "class": "unsupported_construct", "file": source_rel, "line": "25",
                   "trace_available": False, "status": "FAILURE"}
    unreachable = {"id": "root.unreachable.1", "status": "UNREACHABLE",
                   "description": "unreachable assertion",
                   "location": f"{source_rel}:26:1 in function immutable_hole_negative"}
    harness["failed_properties"] = [failed, unsupported]
    harness["unsupported_constructs"] = [unsupported]
    harness["checks"] = {"total": 4, "success": 1, "failure": [failed["id"], unsupported["id"]],
                         "unreachable": [unreachable["id"]], "undetermined": [], "error": [],
                         "unknown": [], "other": []}
    harness["covers"] = {"total": 0, "satisfied": [], "unsatisfiable": [], "unreachable": [],
                         "undetermined": [], "error": [], "unknown": [], "other": []}
    data["summary"] = {"total": 1, "successful": 0, "failed": 1, "checks_total": 4,
                       "checks_success": 1, "covers_total": 0, "covers_satisfied": 0}
    regular_rows = [success,
                    {"id": failed["id"], "status": "FAILURE", "description": failed["description"],
                     "location": f"{source_rel}:24:1 in function immutable_hole_negative"},
                    {"id": unsupported["id"], "status": "FAILURE", "description": unsupported["description"],
                     "location": f"{source_rel}:25:1 in function immutable_hole_negative"},
                    unreachable]
    log = f"Checking harness {case['name']}...\n\nRESULTS:\n"
    for index, prop in enumerate(regular_rows, 1):
        log += (f"Check {index}: {prop['id']}\n\t - Status: {prop['status']}\n"
                f"\t - Description: \"{prop['description']}\"\n"
                f"\t - Location: {prop['location']}\n\n")
    log += "\nSUMMARY:\nVERIFICATION:- FAILED\n"
    receipt = {"build_prefix": str(CHECKER.ROOT), "started_epoch": stamp.timestamp() - 0.5,
               "finished_epoch": stamp.timestamp() + 2}
    return data, log, [case["name"]], {case["name"]: case}, receipt


class ObservationInvariantTests(unittest.TestCase):
    def observe(self, mutation=None):
        data, regular, selectors, cases, receipt = observation_fixture()
        if mutation:
            mutation(data, regular, receipt)
        return observation(data, regular, selectors, cases, receipt)

    def test_complete_synthetic_export_passes_and_retains_metadata(self):
        result = self.observe()
        root_observation = result["roots"][0]
        self.assertEqual(root_observation["failure_kind"], "OTHER")
        self.assertEqual(root_observation["n_failed"], 2)
        self.assertEqual(len(root_observation["unsupported_constructs"]), 1)
        self.assertEqual(root_observation["failed_properties"][0]["class"], "safety_check")
        expected = {"binding": "REGRESSION_BOUND", "expected_verdict": "FAILURE",
                    "checks": root_observation["checks"],
                    "failure_kind": root_observation["failure_kind"],
                    "failed_properties": root_observation["failed_properties"],
                    "unsupported_constructs": root_observation["unsupported_constructs"]}
        self.assertTrue(compare_root(root_observation, root_observation)['accepted'])

    def test_reached_cover_is_retained_with_exact_identity_and_location(self):
        data, regular, selectors, cases, receipt = observation_fixture()
        harness = data["harnesses"][0]
        harness["covers"].update(total=1, satisfied=["root.cover.1"])
        harness["n_properties"] += 1
        data["summary"].update(covers_total=1, covers_satisfied=1)
        regular = regular.replace("\nSUMMARY:", 'Check 5: root.cover.1\n'
                                  '\t - Status: SATISFIED\n'
                                  '\t - Description: "useful path reached"\n'
                                  '\t - Location: fixture.rs:1 in function root\n\nSUMMARY:')
        result = observation(data, regular, selectors, cases, receipt)
        self.assertEqual(result["roots"][0]["covers"], [
            {"id": "root.cover.1", "status": "SATISFIED", "description": "useful path reached",
             "location": "fixture.rs:1 in function root"}])
        harness["covers"]["satisfied"] = ["wrong.cover.1"]
        with self.assertRaisesRegex(ValueError, "cover inventory mismatch"):
            observation(data, regular, selectors, cases, receipt)

    def test_pfc_target_accepts_bare_and_qualified_names_but_rejects_other_targets(self):
        for target in ("pfc_contract", "mixed::pfc_contract", "other_contract",
                       "not_pfc_contract", "mixed::not_pfc_contract"):
            with self.subTest(target=target):
                data, regular, selectors, cases, receipt = observation_fixture()
                case = cases[selectors[0]]
                case.update(mode="PFC", target="pfc_contract")
                data["harnesses"][0]["attributes"]["kind"] = {
                    "ProofForContract": {"target_fn": target}}
                if target in ("pfc_contract", "mixed::pfc_contract"):
                    observation(data, regular, selectors, cases, receipt)
                else:
                    with self.assertRaisesRegex(ValueError, "wrong PFC target.*actual="):
                        observation(data, regular, selectors, cases, receipt)

    def test_failed_trace_availability_is_retained_and_compared(self):
        baseline = self.observe()
        changed = self.observe(lambda d, _r, _p:
                               d["harnesses"][0]["failed_properties"][0].update(trace_available=False))
        self.assertTrue(baseline["roots"][0]["failed_properties"][0]["trace_available"])
        self.assertFalse(changed["roots"][0]["failed_properties"][0]["trace_available"])
        self.assertFalse(compare_root(baseline['roots'][0], changed['roots'][0])['accepted'])

    def test_swapped_success_and_unreachable_ids_rejected(self):
        def swap(data, _regular, _receipt):
            checks = data["harnesses"][0]["checks"]
            checks["unreachable"] = ["root.assertion.1"]
        with self.assertRaisesRegex(ValueError, "unreachable ID mismatch"):
            self.observe(swap)

    def test_failure_counter_and_duplicate_failure_rejected(self):
        with self.assertRaisesRegex(ValueError, "failed-property counter"):
            self.observe(lambda d, _r, _p: d["harnesses"][0].update(n_failed=1))

        def duplicate(data, _regular, _receipt):
            h = data["harnesses"][0]
            h["failed_properties"].append(copy.deepcopy(h["failed_properties"][0]))
            h["n_failed"] += 1
        with self.assertRaisesRegex(ValueError, "duplicate failed-properties"):
            self.observe(duplicate)

    def test_unsupported_inventory_must_match_regular_and_failure_rows(self):
        def drift(data, _regular, _receipt):
            data["harnesses"][0]["unsupported_constructs"][0]["status"] = "SUCCESS"
        with self.assertRaisesRegex(ValueError, "Unsupported inventory mismatch"):
            self.observe(drift)

    def test_stale_export_timestamp_rejected(self):
        with self.assertRaisesRegex(ValueError, "stale export timestamp"):
            self.observe(lambda data, _regular, _receipt: data.update(started_at="2020-01-01T00:00:00Z"))

    def test_null_wrong_type_incomplete_and_wrong_root_rejected(self):
        mutations = [
            (lambda d, _r, _p: d.update(harnesses=None), "schema/presence"),
            (lambda d, _r, _p: d["harnesses"][0].update(unsupported_constructs=None), "schema/presence"),
            (lambda d, _r, _p: d["harnesses"][0].update(n_failed="2"), "schema/presence"),
            (lambda d, _r, _p: d.update(run_state="INCOMPLETE"), "schema/presence"),
            (lambda d, _r, _p: d["harnesses"][0].update(name="wrong_root"), "wrong selected root"),
        ]
        for mutation, message in mutations:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.observe(mutation)



class StructuralDriverTests(unittest.TestCase):
    def manifest(self):
        return json.loads((runner.HERE/'structural-manifest.json').read_text())

    def test_11_exact_calls_and_limits(self):
        manifest = self.manifest()
        calls = runner.invocations(manifest)
        self.assertEqual(len(calls), 11)
        self.assertEqual([c['expected_exit'] for c in calls], [0,1,0,0,1,1,0,1,1,1,1])
        self.assertEqual(calls[8]['selectors'], list(reversed(calls[7]['selectors'])))
        for c in calls:
            argv = runner.command(Path('/source'),manifest,c,Path('/output')/c['id'])
            self.assertEqual(argv.count('--harness'),len(c['selectors']))
            self.assertEqual(argv[-3:],['--cbmc-args','--object-bits','12'])
            self.assertIn('--exact',argv)
            self.assertEqual(argv[argv.index('--jobs')+1],'1')

    def test_original_exit_and_termination_gate(self):
        for expected in (0,1):
            runner.validate_result(dict(termination_reason='EXIT',exit=expected,problems=[]),expected)
        for record in [None, {}, dict(termination_reason='EXIT',exit=None),
                       dict(termination_reason='EXIT',exit=True),dict(termination_reason='EXIT',exit=2),
                       dict(termination_reason='TIMEOUT',exit=-9),dict(termination_reason='LAUNCH_ERROR',exit=None),
                       dict(termination_reason='NOT_STARTED',exit=None),
                       dict(termination_reason='EXIT',exit=0,problems=['partial']),
                       dict(termination_reason='EXIT',exit=0,exception='original error')]:
            with self.assertRaises((ValueError,AttributeError)):
                runner.validate_result(record,0)

    def invoke(self, mode):
        import slice07_ci as ci
        manifest=self.manifest(); calls=runner.invocations(manifest)
        class FakeCI:
            def __init__(self,root):self.ROOT=root;self.count=0
            save=staticmethod(ci.save)
            def inputs(self):return ci.inputs()
            def snapshot(self,*_args):pass
            def execute(self,action,argv,out,timeout=None):
                self.count+=1; base=out/action; row=next(c for c in calls if action=='structural-'+c['id'])
                code=row['expected_exit']; reason='EXIT'
                if mode=='timeout':code=-9;reason='TIMEOUT'
                if mode=='launch':code=None;reason='LAUNCH_ERROR'
                if mode=='wrong-exit':code=7
                self.save(base/'result.json',dict(exit=code,termination_reason=reason,argv=argv,environment={'RUSTFLAGS':os.environ.get('RUSTFLAGS')},problems=[]))
                (base/'stdout.txt').write_text('mock');(base/'stderr.txt').write_text('')
                if mode!='missing':(base/'export.json').write_text('{' if mode=='malformed' else '{}')
                return code==0
        import os
        def synthetic(_data,_regular,selectors,_cases,_receipt):
            roots=[]
            for name in selectors:
                checks=[dict(id=name+'.assertion.1',status='SUCCESS',description='useful check',location='fixture.rs:1')]
                if mode=='drift' and len(selectors)>1:checks.append(dict(id='extra',status='SUCCESS',description='extra',location='fixture.rs:2'))
                roots.append(dict(expected_root=name,actual_root=name,inventory_complete=True,checks=checks,covers=[],failed_properties=[],unsupported_constructs=[],verdict='SUCCESS',failure_kind='NONE',n_failed=0))
            return dict(run_state='COMPLETE',requested_roots=selectors,roots=roots)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); source=root/manifest['source'];source.parent.mkdir(parents=True)
            source.write_bytes((runner.HERE/'structural-mixed.rs').read_bytes())
            (root/'rust-toolchain.toml').write_text('synthetic only')
            fake=FakeCI(root); out=root/'output'
            with patch.object(runner,'tools',return_value={}),patch.object(runner.observer,'observation',side_effect=synthetic):
                good=runner.run(fake,out)
            summary=json.loads((out/'structural/summary.json').read_text())
            for row in summary['runs']:
                self.assertEqual(row['original_exit'], next(c['expected_exit'] for c in calls if c['id']==row['id']) if mode not in ('timeout','launch','wrong-exit') else {'timeout':-9,'launch':None,'wrong-exit':7}[mode])
            return good,summary,fake.count

    def test_completed_exact_capture_all_18(self):
        good,summary,count=self.invoke('good')
        self.assertTrue(good);self.assertEqual(count,11);self.assertEqual(len(summary['comparisons']),18)
        self.assertEqual(summary['binding_status'],'NOT_CHECKED_CAPTURE')
        self.assertEqual(summary['order_credit'],'NOT_ESTABLISHED')

    def test_additions_fail_after_all_18_compared(self):
        good,summary,count=self.invoke('drift')
        self.assertFalse(good);self.assertEqual(count,11);self.assertEqual(len(summary['comparisons']),18)
        self.assertTrue(all(not r['accepted'] for r in summary['comparisons']))

    def test_process_and_output_errors_preserve_original_exit(self):
        for mode in ('missing','malformed','timeout','launch','wrong-exit'):
            with self.subTest(mode=mode):
                good,summary,count=self.invoke(mode)
                self.assertFalse(good);self.assertEqual(count,1);self.assertEqual(summary['status'],'FAIL_OR_UNKNOWN')
                self.assertIn('error',summary)

    def test_manifest_tamper_stops_before_tools(self):
        import slice07_ci as ci
        config,manifest=ci.inputs();config['structural']['manifest_sha256']='wrong'
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(ci,'inputs',return_value=(config,manifest)),patch.object(runner,'tools') as tool:
                self.assertFalse(runner.run(ci,Path(temp)))
                tool.assert_not_called()

if __name__ == '__main__':
    unittest.main(verbosity=2)
