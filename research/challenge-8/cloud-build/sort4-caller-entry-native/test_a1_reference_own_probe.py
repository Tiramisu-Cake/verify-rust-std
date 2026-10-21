"""Synthetic source and classifier tests; no proof pipeline execution."""
import importlib.util
import hashlib
from pathlib import Path
import unittest
HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
PROBE = load('probe_service_test', HERE / 'a1-reference-own-probe.py')
FIXTURES = load('probe_fixture_test', HERE / 'a1-fixtures.py')
GHOST = load('probe_ghost_test', HERE.parent / 'sort4-native-c1-bound/ghost-strip.py')
SELECTED = {'classification': 'ONE_SOURCE_INTERVAL_SELECTED_CHECKED_LEMMA'}

class ProbeService(unittest.TestCase):
    def setUp(self):
        self.cases = PROBE.variants(FIXTURES, GHOST)
    def stage(self, log=b'', code=0):
        return {'classification': 'TERMINAL', 'exit': code,
                'log_sha256': hashlib.sha256(log).hexdigest()}
    def test_faithful_sources(self):
        self.assertEqual(len(self.cases), 7)
        helper = self.cases['helper']['source']
        self.assertIn(FIXTURES.OPTION_CLEANUP_LEMMA, helper)
        self.assertIn(b'Option::None => {}', helper)
        self.assertIn(b'Option::Some(r) => { open shared_ref_type_own', helper)
        for row in self.cases.values():
            self.assertEqual(GHOST.strip_ghost(row['source']), row['original'])
            self.assertNotIn(b'Freeze', row['source'])
            self.assertNotIn(b'Copy', row['source'])
        self.assertIn(b"share)('a, t, r)", self.cases['some-preserve']['source'])
        self.assertIn(b'Option_own::<T>', self.cases['negative-generic-erasure']['source'])
        self.assertIn(b"Option_own::<&'a mut T>", self.cases['negative-mutable-erasure']['source'])
        self.assertIn(b"share)('static", self.cases['negative-lifetime-redirect']['source'])
    def test_positive_terminal_and_identity(self):
        row = self.cases['helper']
        self.assertTrue(PROBE.classify(self.stage(), b'', SELECTED, row)['passed'])
        for stage in (None, {}, {'classification': 'RUNNING'},
                      {'classification': 'TERMINAL', 'exit': None},
                      {'classification': 'TERMINAL', 'exit': '0'},
                      {'classification': 'TERMINAL', 'exit': False},
                      self.stage(code=124), self.stage(code=1)):
            self.assertFalse(PROBE.classify(stage, b'', SELECTED, row)['passed'])
        for log, selection in ((None, SELECTED), (b'changed', SELECTED), (b'', None), (b'', {})):
            self.assertFalse(PROBE.classify(self.stage(), log, selection, row)['passed'])
    def test_observed_persistent_lifetime_diagnostic_and_wrong_lifetime(self):
        row = self.cases['negative-lifetime-redirect']
        log = b"verified/lib.rs(5,29-30): error: No matching heap chunks: [_]share(T_typeid)(lft_of('static_typeid), t, r)\n"
        self.assertTrue(PROBE.classify(self.stage(log, 1), log, SELECTED, row)['passed'])
        for bad in (log.replace(b"'static_typeid", b"'a_typeid"),
                    log.replace(b'[_]', b'[1]'), log.replace(b'T_typeid', b'U_typeid'),
                    log.replace(b': error: No', b': error: unrelated No')):
            self.assertFalse(PROBE.classify(self.stage(bad, 1), bad, SELECTED, row)['passed'])
    def test_negative_resource_and_location(self):
        for name, row in self.cases.items():
            if row['expected_failure'] is None:
                continue
            line = row['metadata']['body_end_line']
            log = f"verified/lib.rs({line},1): error: {row['expected_failure']}(t, r)\n".encode()
            with self.subTest(name=name):
                self.assertTrue(PROBE.classify(self.stage(log, 1), log, SELECTED, row)['passed'])
                for bad in (log.replace(f'({line},'.encode(), b'(999,'),
                            log.replace(b'verified/lib.rs', b'other/lib.rs'),
                            log + b'error: unrelated failure\n', b'verified/lib.rs(4,1): Parse error\n'):
                    self.assertFalse(PROBE.classify(self.stage(bad, 1), bad, SELECTED, row)['passed'])
                for code in (0, 124):
                    self.assertFalse(PROBE.classify(self.stage(log, code), log, SELECTED, row)['passed'])
if __name__ == '__main__':
    unittest.main()
