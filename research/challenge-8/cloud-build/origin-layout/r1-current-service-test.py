#!/usr/bin/env python3
"""Pure synthetic annotation/control tests. No source extraction or proof tools."""
import ast
import importlib.util
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


campaign = load('current_marker_assembly', HERE/'first-callback.py')
admission = load('current_admission_synthetic', HERE/'first-callback-admission-controls.py')
module_ast = ast.parse((HERE/'actual-insert-tail-b2.py').read_bytes())
RECOVER = next(ast.literal_eval(node.value) for node in module_ast.body
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and
       t.id == 'B2_COMPARE_RECOVER' for t in node.targets))
OLD = SimpleNamespace(B2_COMPARE_RECOVER=RECOVER)


def source():
    return b'synthetic-runtime\n'+admission.CALL_ANNOTATION+b'\n'+campaign._markers(OLD)


def outcome(log, code):
    return dict(log=log, exit_code=code, log_sha256='synthetic', verifast_sha256='synthetic',
        exporter_wrapper_sha256='synthetic', captured_export_sha256='synthetic', source_sha256={})


class CurrentTests(unittest.TestCase):
    def test_singleton_facts_are_pure_unique_and_outside_lifetime(self):
        anchor = b"    //@ let cmp_k = begin_lifetime();\n"
        synthetic = b"fn synthetic() {\n"+anchor+b"    /*@ let_lft 'cmp = cmp_k; @*/\n}\n"
        changed = campaign._add_singleton_facts(synthetic)
        self.assertEqual(changed.replace(campaign.SINGLETON_FACTS, b'', 1), synthetic)
        self.assertEqual(campaign.SINGLETON_FACTS.count(b'//@ '), 6)
        self.assertLess(changed.index(b'length_drop'), changed.index(b'begin_lifetime'))
        self.assertLess(changed.index(b'length_take'), changed.index(b'let_lft'))
        self.assertNotIn(b'own', campaign.SINGLETON_FACTS)
        self.assertNotIn(b'assume', campaign.SINGLETON_FACTS)
        self.assertNotIn(b'leak', campaign.SINGLETON_FACTS)
        for bad in (b'no anchor', synthetic+anchor):
            with self.assertRaises(ValueError): campaign._add_singleton_facts(bad)

    def test_current_recovery_uses_returned_values_and_keeps_close_protocol(self):
        lines = campaign._markers(OLD).splitlines()
        self.assertEqual(len(lines), 3)
        close, end, recover = lines
        self.assertEqual(close.count(b';'), 7)  # marker + unchanged six proof commands
        self.assertEqual(recover.count(b';'), 19)  # marker +18checkedcommands
        self.assertIn(b'first_callback_scope_end', end)
        self.assertIn(b'assert *tail |-> ?current_tail;', recover)
        self.assertIn(b'assert *sift |-> ?current_sift;', recover)
        self.assertNotIn(b'head(', recover)
        self.assertNotIn(b'foreach_join', recover)
        self.assertNotIn(b'assume', recover)
        self.assertNotIn(b'leak', recover)
        self.assertEqual(recover.count(b'array_join::<u64>'), 2)
        self.assertEqual(recover.count(b'foreach_append('), 2)
        self.assertLess(recover.index(b'assert *tail'), recover.index(b'close own'))
        self.assertLess(recover.index(b'assert *sift'), recover.index(b'close own'))

    def test_existing_resource_mutations_do_not_replace_current_owner_recovery(self):
        positive = campaign._markers(OLD).splitlines()
        for name in ('lost_reference_fraction', 'lost_reference_token'):
            mutated = campaign._markers(OLD, name).splitlines()
            self.assertNotEqual(mutated[0], positive[0])
            self.assertEqual(mutated[1:], positive[1:])

    def test_annotation_replacement_refuses_stale_or_ambiguous_base(self):
        for value in (RECOVER.replace(b'head(', b'heae(', 1), RECOVER+RECOVER,
                      RECOVER.replace(b'open_full_borrow_content::<u64>(t, tail)', b'open_full_borrow_content::<u64>(t, other)', 1)):
            with self.assertRaises(ValueError):
                campaign._markers(SimpleNamespace(B2_COMPARE_RECOVER=value))

    def test_new_admission_mutations_are_single_unique_ghost_changes(self):
        pristine = source()
        for name in admission.CURRENT_RECOVERY_MUTATIONS:
            changed = admission._current_recovery_mutant(pristine, name)
            self.assertNotEqual(changed, pristine)
            self.assertEqual(changed.count(b'\n'), pristine.count(b'\n'))
            self.assertEqual(changed.count(admission.CALL_ANNOTATION), 1)
            self.assertTrue(changed.startswith(b'synthetic-runtime\n'))
            with self.assertRaises(ValueError):
                admission._current_recovery_mutant(pristine+pristine, name)
        with self.assertRaises(ValueError): admission._current_recovery_mutant(pristine, 'unknown')

    def test_refusal_requires_exact_guard_location_and_no_earlier_failure(self):
        message = f'verified/lib.rs(5,13-30): error: {admission.EXPECTED_CURRENT_RECOVERY_ERROR}'
        self.assertTrue(admission._intended_current_recovery_refusal(outcome(message, 1), 5))
        for log, code in ((message, 0), (message, 2), (message, 124), (message, 125), (message, 126), (message, 127), (message, 143), (message, None),
                          (message.replace('(5,', '(6,'), 1), ('error: compiler failed', 1),
                          (message+'\nerror: unrelated', 1), (message+'\nFatal error: exception', 1), (message+'\nfatal error: exception', 1),
                          (message+'\n0 errors found', 1)):
            self.assertFalse(admission._intended_current_recovery_refusal(outcome(log, code), 5))

    def test_positive_gate_blocks_mutants_and_strict_refusals_are_counted(self):
        pair = (b'synthetic-original', source())
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(admission, '_run_verifast', return_value=outcome('error: earlier', 1)), \
                 patch.object(admission, '_current_recovery_mutant', side_effect=AssertionError('must not run')):
                rows = admission._current_recovery_controls(Path(temp)/'blocked', None, {}, None, pair)
                self.assertTrue(all(not r['matched'] and r['status']=='POSITIVE_BASELINE_FAILED_MUTANT_NOT_RUN' for r in rows.values()))
            scope_line = pair[1][:pair[1].index(b'first_callback_scope_end::')].count(b'\n')+1
            positive = 'MERGE_HRTB_CALL registered=1 F=F T=u64 call=synthetic\nMERGE_FIRST_CALLBACK_LOCAL_CONTINUE\n0 errors found'
            def fake_run(label, *args, **kwargs):
                if label.endswith('positive-baseline'): return outcome(positive, 0)
                return outcome(f'verified/lib.rs({scope_line},13): error: {admission.EXPECTED_CURRENT_RECOVERY_ERROR}', 1)
            with patch.object(admission, '_run_verifast', side_effect=fake_run):
                rows = admission._current_recovery_controls(Path(temp)/'accepted', None, {}, None, pair)
                self.assertEqual(set(rows), set(admission.CURRENT_RECOVERY_MUTATIONS))
                self.assertTrue(all(r['matched'] for r in rows.values()))


if __name__ == '__main__': unittest.main(verbosity=2)
