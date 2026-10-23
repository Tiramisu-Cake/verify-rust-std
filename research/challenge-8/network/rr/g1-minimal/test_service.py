"""Only synthetic saved records; never imports the Cloud runner or injector."""
import unittest
from service import audit, first_diagnostic, online_freeze


class SavedDataTests(unittest.TestCase):
    def test_first_error_is_unreviewed(self):
        self.assertEqual(first_diagnostic('warning: a\nerror[E1]: b\nunsupported c')['line'], 2)
        self.assertEqual(first_diagnostic('UnknownProcedure foo')['attribution'], 'UNREVIEWED')

    def test_success_is_not_proof(self):
        result = audit({'target': {'returncode': 0, 'timed_out': False}}, None, True)
        self.assertTrue(result['diagnostic_complete'])
        self.assertFalse(result['accepted'])
        self.assertEqual(result['proof_status'], 'NOT_RUN')
        self.assertEqual(result['classification'], 'INCONCLUSIVE')

    def test_frontend_failure_can_be_collected(self):
        result = audit({'target': {'returncode': 101, 'timed_out': False}}, None, True)
        self.assertTrue(result['diagnostic_complete'])
        self.assertFalse(result['verification_accepted'])

    def test_incomplete_or_unrun_has_no_collection_credit(self):
        for commands, stage, inventory in [({}, 'source-restore', True),
                ({'target': {'returncode': -9}}, None, True),
                ({'target': {'returncode': 124, 'timed_out': True}}, None, True),
                ({'target': {'returncode': 0}}, None, False),
                ({'target': {'returncode': 0}}, 'inventory', True)]:
            self.assertFalse(audit(commands, stage, inventory)['diagnostic_complete'])

    def test_malformed_partial_and_explicit_not_run_records_are_not_collected(self):
        for target in (None, [], 'NOT_RUN', {}, {'returncode': '0', 'timed_out': False},
                       {'returncode': True, 'timed_out': False},
                       {'returncode': 0, 'timed_out': None}, {'returncode': 0}):
            with self.subTest(target=target):
                result = audit({'target': target}, None, True)
                self.assertFalse(result['diagnostic_complete'])
                self.assertFalse(result['accepted'])

    def test_online_freeze_requires_all_exact_binary_and_image_pins(self):
        import copy
        image = 'us-central1-docker.pkg.dev/smallsort-ci/smallsort-tools/refinedrust-g1@sha256:' + 'a' * 64
        freeze = {'schema': 'rr-g1-online-freeze-v2', 'image_digest': image,
                  'cargo_home': '/opt/g1-cargo', 'image_receipt_sha256': 'b' * 64,
                  'rr_frontend_lock_sha256': 'b66b9e281478be8263eab9ba210964cdd8f1db92535b7b81305f50dea03682aa',
                  'binaries': {name: {'path': path, 'sha256': 'c' * 64} for name, path in {
                      'rustc': '/opt/rust/bin/rustc', 'cargo': '/opt/rust/bin/cargo',
                      'cargo-refinedrust': '/opt/rr-bin/cargo-refinedrust',
                      'refinedrust-rustc': '/opt/rr-bin/refinedrust-rustc'}.items()}}
        self.assertEqual(online_freeze(freeze, image), freeze['binaries'])
        for key, value in [('schema', 'old'), ('image_digest', None), ('cargo_home', '/tmp/cache'),
                           ('image_receipt_sha256', None), ('binaries', None)]:
            bad = copy.deepcopy(freeze); bad[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                online_freeze(bad, image)
        with self.assertRaises(ValueError):
            online_freeze(freeze, image + '0')
        for value in (None, 3, 'false'):
            bad = copy.deepcopy(freeze); bad['binaries']['rustc']['sha256'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                online_freeze(bad, image)


if __name__ == '__main__':
    unittest.main()
