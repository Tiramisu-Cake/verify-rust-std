"""Synthetic service-only tests; no compiler, extractor, dependency or Cloud imports."""
import json
from pathlib import Path
import tempfile
import unittest
from evidence import inventory, seal, verify_inventory
from service import classify, check_identity, normal_completion, negative_unknown_procedure, negative_source_certificate, positive_unit_definition

IDS = dict(build_id='synthetic', source_sha='a'*40, tool_sha='b'*40,
           compiler_sha='c'*40, proof_sha='d'*40, infra_sha='e'*40,
           image_digest='synthetic.invalid/rr@sha256:'+'f'*64, profile='synthetic-only')


class Services(unittest.TestCase):
    def test_positive_control_definition(self):
        self.assertFalse(positive_unit_definition('(* Program Definition g1_p0 *)'))
        self.assertFalse(positive_unit_definition('Program Definition g1_p0_def : function := garbage'))
        self.assertFalse(positive_unit_definition('Program Definition g1_p0_def : function :=\n {| f_code := [x]; f_init := "_bb0"\nFinal Obligation.'))
        self.assertFalse(positive_unit_definition('Program Definition g1_p0_def : function :=\n {| f_code := [x]; f_init := "_bb0"\nProgram Definition other : function := {| f_code := []; f_init := "_bb0" |}.\nFinal Obligation.'))
        self.assertTrue(positive_unit_definition('Program Definition g1_p0_def : function :=\n {| f_code := [x]; f_init := "_bb0" |}.\nFinal Obligation.'))

    def test_identity_negative(self):
        check_identity(IDS, IDS)
        for key in IDS:
            with self.subTest(key=key), self.assertRaises(ValueError):
                check_identity(dict(IDS, **{key: 'wrong'}), IDS)
        with self.assertRaises(ValueError):
            check_identity(IDS, {'source_sha': IDS['source_sha']})

    def test_intended_n1_only(self):
        intended = 'error: Unknown procedure: DefId(0:9 ~ rr_g1_n1[abc]::g1_unregistered)'
        self.assertTrue(negative_unknown_procedure(1, intended))
        for code, text in [(0, intended), (None, intended), (-9, intended), (-15, intended),
                           (137, intended), (143, intended),
                           (1, 'Unknown procedure: other'),
                           (1, intended+'\nerror[E0425]: compiler setup failed'),
                           (1, intended+'\nerror: unrelated translation failed')]:
            self.assertFalse(negative_unknown_procedure(code, text))
        self.assertFalse(negative_unknown_procedure(1, intended, timed_out=True))
        self.assertFalse(negative_unknown_procedure(1, intended, signaled=True))

    def test_source_certificate_negative(self):
        expected = {'smallsort': 'a'*64}
        fixture = {'source_commit': 'b'*40, 'sources': {'smallsort': {'original_sha256': '0'*64}}}
        self.assertTrue(negative_source_certificate(fixture, 'b'*40, expected))
        self.assertFalse(negative_source_certificate(fixture, 'c'*40, expected))
        self.assertFalse(negative_source_certificate({'source_commit':'b'*40,'sources':{}}, 'b'*40, expected))

    def test_verdict_boundaries(self):
        stages = {'inputs': {'ok': True}, 'compiler': {'ok': True},
                  'native': {'returncode': 0, 'timed_out': False, 'signaled': False},
                  'p1': {'returncode': 0, 'timed_out': False, 'signaled': False}}
        controls = {'P0': True, 'N1': True, 'N2': True}
        self.assertEqual(classify(stages, controls, {})['verdict'], 'INCONCLUSIVE')
        self.assertEqual(classify(stages, controls, {'verdict': 'OBSERVED'})['verdict'], 'INCONCLUSIVE')
        self.assertEqual(classify(stages, controls, {'verdict': 'STOP'})['verdict'], 'STOP')
        self.assertFalse(classify(stages, controls, {'verdict': 'PASS'})['verification_accepted'])
        for failure in ({'returncode': 1, 'timed_out': False, 'signaled': False},
                        {'returncode': -9, 'timed_out': False, 'signaled': True},
                        {'returncode': 0, 'timed_out': True, 'signaled': False},
                        {'returncode': 1, 'timed_out': True, 'signaled': False}):
            self.assertEqual(classify(dict(stages, native=failure), controls, {})['verdict'], 'INCONCLUSIVE')
        self.assertEqual(classify(dict(stages, native={'returncode': 1, 'timed_out': False, 'signaled': False, 'compiler_rejection': True}), controls, {})['verdict'], 'STOP')
        for code in (0, 1, -9, -15):
            for timed_out in (False, True):
                p1 = {'returncode': code, 'timed_out': timed_out, 'signaled': code < 0}
                got = classify(dict(stages, p1=p1), controls, {'verdict': 'PASS'})
                self.assertEqual(got['verdict'] == 'PASS', code == 0 and not timed_out)
        self.assertFalse(normal_completion({'returncode': 0, 'timed_out': True}))
        self.assertEqual(classify(stages, dict(controls, N1=False), {'verdict': 'PASS'})['verdict'], 'INCONCLUSIVE')
        self.assertEqual(classify(dict(stages, compiler={'ok': False, 'interrupted': True}),
                                  controls, {'verdict': 'PASS'})['verdict'], 'INCONCLUSIVE')

    def test_inventory_detects_tamper_and_extra(self):
        with tempfile.TemporaryDirectory(prefix='rr-g1-service-') as d:
            root = Path(d)
            for f in ('identity.json', 'execution.json', 'source-receipt.json', 'summary.json'):
                (root/f).write_text('{}\n')
            for f in ('inputs.json', 'image-receipt.json', 'cargo-config.toml'):
                (root/f).write_text('{}\n')
            seal(root)
            verify_inventory(root)
            (root/'summary.json').write_text('{"verdict":"PASS"}')
            with self.assertRaises(ValueError):
                verify_inventory(root)
            seal(root)
            (root/'unexpected').write_text('not inventoried')
            with self.assertRaises(ValueError):
                verify_inventory(root)

    def test_inventory_rejects_links(self):
        with tempfile.TemporaryDirectory(prefix='rr-g1-service-') as d:
            root = Path(d)
            (root/'link').symlink_to('/tmp')
            with self.assertRaises(ValueError):
                inventory(root)


if __name__ == '__main__':
    unittest.main()
