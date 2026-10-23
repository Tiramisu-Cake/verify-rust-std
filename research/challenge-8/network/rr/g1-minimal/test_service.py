"""Only synthetic saved records; never imports the Cloud runner or injector."""
import unittest
from service import audit, first_diagnostic


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


if __name__ == '__main__':
    unittest.main()
