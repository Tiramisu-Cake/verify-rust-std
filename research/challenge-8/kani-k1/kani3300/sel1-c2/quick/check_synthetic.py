#!/usr/bin/env python3
"""Synthetic service checks only. No Cargo/rustc/Kani/setup invocation."""
from pathlib import Path
import importlib.util,json,sys,tempfile,unittest,os
from unittest import mock
HERE=Path(__file__).resolve().parent
SRC=HERE/'full-export/.github/c2-slices'
os.environ['SEL1_C2_SOURCE_DIR']='/root/kani-fix-3300-sel1-c2-w14'
sys.path.insert(0,str(SRC))
import slice07_ci as ci
import structural

class QuickPreparationTests(unittest.TestCase):
    def test_reviewed_candidate_binding(self):
        config, manifest = ci.inputs()
        self.assertEqual(config['source_sha'], '14bc57fdb99960240c4944845a3d985c8af4dcf7')
        self.assertEqual(config['source_sha'], manifest['source_sha'])
        self.assertEqual(config['source_tree'], manifest['source_tree'])
        self.assertEqual(manifest['deduplicated_selector_count'], 500)

    def test_inherited_inventory_and_all_29_controls_remain(self):
        data=json.loads((SRC/'test-manifest.json').read_text())
        rows=ci.suites(data)
        self.assertEqual(sum(len(v) for v in rows.values()),500)
        controls=json.loads((SRC/'sel1-controls.json').read_text())
        self.assertEqual(len(controls['selectors']),29)
        self.assertEqual(sum(r['expected_result']=='SUCCESS' for r in controls['selectors']),12)
        wanted={'[expected] '+r['file'].removeprefix('tests/') for r in controls['selectors']}
        self.assertTrue(wanted <= set(rows[('expected','expected')]))
        self.assertFalse(any(rows[('expected','expected')][s]['existing_path_ignore'] for s in wanted))
        self.assertEqual(sum(v['existing_path_ignore'] for v in rows[('expected','expected')].values()),6)

    def test_s5_and_f7_inventory_preserved(self):
        self.assertEqual(len(json.loads((SRC/'sensitivity-manifest.json').read_text())['variants']),4)
        data=json.loads((SRC/'structural-manifest.json').read_text())
        self.assertEqual(len(structural.invocations(data)),11)
        self.assertIn('18',json.dumps(json.loads((SRC/'inputs.json').read_text())['structural']))

    def test_missing_partial_wrong_counts_and_timeout_cannot_pass(self):
        for output in ['', 'test result: ok.', 'test result: ok. 1 passed; 1 failed; 0 ignored;',
                       'test result: ok. 1 passed; 0 failed; 0 ignored;\ntest wanted ... ok\nProcess timed out after 1']:
            with self.subTest(output=output):self.assertTrue(ci.check_output(output,{'wanted':False}))

    def test_original_failure_launch_error_and_timeout_retained(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            self.assertFalse(ci.execute('failure',[sys.executable,'-c','raise SystemExit(7)'],out))
            self.assertEqual(json.loads((out/'failure/result.json').read_text())['exit'],7)
            self.assertFalse(ci.execute('missing',['/nonexistent/sel1-c2-synthetic-program'],out))
            self.assertEqual(json.loads((out/'missing/result.json').read_text())['termination_reason'],'LAUNCH_ERROR')
            self.assertFalse(ci.execute('timeout',[sys.executable,'-c','import time; time.sleep(5)'],out,timeout=.03))
            self.assertEqual(json.loads((out/'timeout/result.json').read_text())['termination_reason'],'TIMEOUT')

    def test_success_needs_exact_native_inventory_and_stays_review_required(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)
            program="print('test wanted ... ok'); print('test result: ok. 1 passed; 0 failed; 0 ignored;')"
            self.assertTrue(ci.execute('success',[sys.executable,'-c',program],out,{'wanted':False}))
            self.assertEqual(json.loads((out/'success/result.json').read_text())['result'],'EXIT_ZERO_COUNTS_MATCH_REQUIRES_REVIEW')

    def test_source_stage_target_mismatch(self):
        config={'source_sha':'1'*40,'source_parent':'2'*40,'source_tree':'3'*40}
        for case in ['head','parent','tree','dirty']:
            def git(*args):
                table={('rev-parse','HEAD'): 'wrong' if case=='head' else config['source_sha'],
                       ('rev-parse','HEAD^'):'wrong' if case=='parent' else config['source_parent'],
                       ('rev-parse',config['source_sha']+'^{tree}'):'wrong' if case=='tree' else config['source_tree'],
                       ('rev-parse',config['source_sha']+'^'):config['source_parent'],
                       ('status','--porcelain=v1','--untracked-files=normal'):' M tracked' if case=='dirty' else ''}
                return table.get(args,'').encode()
            with self.subTest(case=case),tempfile.TemporaryDirectory() as td, \
                 mock.patch.object(ci,'inputs',return_value=(config,{})), \
                 mock.patch.object(ci,'git',side_effect=git), \
                 mock.patch.object(ci.subprocess,'check_output',return_value=b'overlay'):
                with self.assertRaises(ValueError):ci.snapshot('before',Path(td))

    def test_null_wrong_type_and_not_run_cannot_pass(self):
        for value in [None, {}, []]:
            with self.assertRaises(TypeError):
                ci.check_output(value, {'wanted': False})
        for value in ['NOT_RUN', 'test result: ok. 0 passed; 0 failed; 0 ignored;']:
            self.assertTrue(ci.check_output(value, {'wanted': False}))

    def test_explicit_not_run_before_any_native_stage(self):
        with tempfile.TemporaryDirectory() as td, \
             mock.patch.dict(ci.os.environ, {'C2_EVIDENCE_DIR': td}), \
             mock.patch.object(ci.sys, 'argv', ['runner', 'before']), \
             mock.patch.object(ci, 'snapshot'):
            ci.main()
            record = json.loads((Path(td)/'units/result.json').read_text())
            self.assertEqual(record['result'], 'NOT_RUN')
            self.assertIsNone(record['exit'])
            self.assertEqual(record['termination_reason'], 'NOT_STARTED')

    def test_manifest_mismatch_fails_before_execution(self):
        for kind in ['hash', 'source']:
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                config = json.loads((SRC/'inputs.json').read_text())
                manifest = json.loads((SRC/'test-manifest.json').read_text())
                if kind == 'hash':
                    config['test_manifest_sha256'] = '0'*64
                else:
                    manifest['source_sha'] = '0'*40
                    import hashlib
                    data = json.dumps(manifest).encode()
                    config['test_manifest_sha256'] = hashlib.sha256(data).hexdigest()
                (root/'test-manifest.json').write_text(json.dumps(manifest))
                (root/'inputs.json').write_text(json.dumps(config))
                with mock.patch.object(ci, 'HERE', root), self.assertRaises(ValueError):
                    ci.inputs()

if __name__=='__main__':unittest.main(verbosity=2)
