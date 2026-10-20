"""Synthetic action boundary; no runner, extraction, or tool invocation."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
SOURCE = Path(__file__).with_name('a1-runner.py')
TREE = ast.parse(SOURCE.read_text())
RUN = next(n for n in TREE.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
ACTION = next(n for n in RUN.body if isinstance(n, ast.FunctionDef) and n.name == 'action')
CODE = compile(ast.Module(body=[ACTION], type_ignores=[]), str(SOURCE), 'exec')

class ActionResultTests(unittest.TestCase):
    def setUp(self):
        self.rows, self.events, self.snapshots = {}, [], []
        self.args = SimpleNamespace(deadline_epoch=1000)
        self.ns = dict(a=self.args, time=SimpleNamespace(time=lambda: 0),
                       SOURCE_CASE={}, observations=self.rows, execution_events=self.events,
                       persist_progress=lambda: self.snapshots.append(dict(self.rows)))
        exec(CODE, self.ns)
        self.action = self.ns['action']

    def test_exception_retained_but_not_consumed_as_prepared_inputs(self):
        for exception in (RuntimeError('prepare failed'), KeyError('messages'), TypeError('null inputs')):
            def fail():
                raise exception
            self.assertIsNone(self.action('prepare-synthetic-inputs', fail))
            row = self.rows['prepare-synthetic-inputs']
            self.assertIn(type(exception).__name__, row['adapter_error'])
            self.assertFalse(row['proof_credit'])
            self.assertTrue(row['execution_started'])
            self.assertEqual(self.events[-1]['event'], 'adapter_error')
            self.assertIn('prepare-synthetic-inputs', self.snapshots[-1])

    def test_success_partial_null_and_absent_paths_remain_exact(self):
        for value in ({'messages': []}, {'classification': 'PARTIAL', 'artifacts': {}},
                      {'not_run': True, 'proof_credit': False, 'artifact': None},
                      {'artifacts': {'normal': {'path': None}}}, None):
            self.assertIs(self.action('synthetic-case', lambda: value), value)
            self.assertIs(self.rows['synthetic-case'], value)
            self.assertEqual(self.events[-1]['event'], 'completed')

    def test_deadline_not_run_preserved_without_execution_or_fake_inputs(self):
        self.args.deadline_epoch = 0
        self.assertIsNone(self.action('prepare-synthetic-inputs', lambda: self.fail('executed')))
        row = self.rows['prepare-synthetic-inputs']
        self.assertTrue(row['not_run'])
        self.assertFalse(row['execution_started'])
        self.assertFalse(row['proof_credit'])
        self.assertNotIn('messages', row)
        self.assertNotIn('path', row)

if __name__ == '__main__':
    unittest.main()
