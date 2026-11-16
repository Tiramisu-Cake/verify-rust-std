# Copyright Kani Contributors
# SPDX-License-Identifier: Apache-2.0 OR MIT
import copy
import json
from pathlib import Path
import sys
import unittest

from classifier_v3 import EvidenceError, bind_stdout, role

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'accept-v2'))
import classifier_v2 as policy
import test_classifier_v2 as prior_tests


RULES = json.loads((Path(__file__).parent / 'ROLE-RULES.json').read_text())['rules']
FN = "fmt::Arguments::<'_>::from_str"
PID = FN + '.assertion.1'


def block(number, pid, status, description, file='library/core/src/fmt/mod.rs',
          line=820, fn=FN):
    return (f'Check {number}: {pid}\n\t - Status: {status}\n'
            f'\t - Description: "{description}"\n'
            f'\t - Location: {file}:{line}:38 in function {fn}\n\n')


def fixture():
    text = ('Checking harness target::h...\nRESULTS:\n' +
            block(1, PID, 'UNREACHABLE', 'attempt to shift left with overflow') +
            block(2, 'ok', 'SUCCESS', 'ordinary check') +
            block(3, 'cover', 'SATISFIED', 'after target') +
            '\nSUMMARY:\nVERIFICATION:- SUCCESSFUL\nVerification Time: 1.0s\n')
    data = text.encode()
    row = {'id': 'h', 'selector': 'target::h'}
    h = {'name': row['selector'], 'outcome': {'verdict': 'SUCCESS'}, 'n_properties': 3,
         'checks': {'success': 1, 'unreachable': [PID], 'failure': []},
         'covers': {'satisfied': ['cover']}}
    receipt = dict(row, group='group-00', group_receipt='groups/group-00/receipt.json',
                   group_export_sha256='sha', stdout_cap_bytes=1048576)
    compilation = {'state': 'PRE_HARNESS_COMPLETE', 'harness_marker_order': ['h'],
                   'row_output_bytes': {'h': {'stdout': len(data)}}}
    group = {'id': 'group-00', 'rows': ['h'], 'state': 'OBSERVED', 'export_sha256': 'sha',
             'execution': {'stdout_truncated': False, 'stderr_truncated': False,
                           'output_truncated': False, 'timed_out': False,
                           'signal': None, 'compilation': copy.deepcopy(compilation)}}
    return [data, row, h, receipt, group, compilation]


def set_text(args, data):
    args[0] = data
    args[5]['row_output_bytes']['h']['stdout'] = len(data)
    args[4]['execution']['compilation'] = copy.deepcopy(args[5])


def record(fn=FN, file='library/core/src/fmt/mod.rs', line=820,
           description='attempt to shift left with overflow'):
    return dict(id=fn + '.assertion.1', status='UNREACHABLE', function=fn,
                file=file, line=line, column=38, description=description)


class BindingTests(unittest.TestCase):
    def rejected(self, args):
        with self.assertRaises((EvidenceError, KeyError, TypeError, UnicodeError)):
            bind_stdout(*args)

    def test_success(self):
        records, evidence = bind_stdout(*fixture())
        self.assertEqual(records[PID]['line'], 820)
        self.assertEqual(evidence['state'], 'BOUND_COMPLETE')

    def test_truncation_and_interruption_flags(self):
        for field in ('stdout_truncated', 'stderr_truncated', 'output_truncated', 'timed_out'):
            for value in (True, None, 0, 'false'):
                with self.subTest(field=field, value=value):
                    a = fixture(); a[4]['execution'][field] = value; self.rejected(a)
        for field, value in (('signal', 9), ('termination_reason', 'row_stdout_cap')):
            a = fixture(); a[4]['execution'][field] = value; self.rejected(a)

    def test_wrong_count_cap_and_missing(self):
        for change in ('short', 'equal_cap', 'small_cap', 'null_cap', 'bool_cap', 'missing'):
            with self.subTest(change=change):
                a = fixture()
                if change == 'short': a[0] = a[0][:-1]
                elif change == 'missing': a[0] = None
                else:
                    a[3]['stdout_cap_bytes'] = {'equal_cap': len(a[0]), 'small_cap': 1,
                                                'null_cap': None, 'bool_cap': True}[change]
                self.rejected(a)

    def test_receipt_binding(self):
        for field in ('id', 'selector', 'group', 'group_receipt', 'group_export_sha256'):
            a = fixture(); a[3][field] = 'wrong'; self.rejected(a)

    def test_missing_null_wrong_type_receipt(self):
        for value in ({}, None, []):
            a = fixture(); a[3] = value; self.rejected(a)

    def test_split_receipt_disagreement(self):
        a = fixture(); a[5]['state'] = 'UNKNOWN'; self.rejected(a)

    def test_duplicate_missing_foreign_marker_order(self):
        for order in ([], ['h', 'h'], ['other']):
            a = fixture(); a[5]['harness_marker_order'] = order
            a[4]['execution']['compilation'] = copy.deepcopy(a[5]); self.rejected(a)

    def test_wrong_foreign_or_duplicate_marker(self):
        for data in (fixture()[0].replace(b'target::h...', b'other::h...'),
                     fixture()[0] + b'Checking harness target::h...\n'):
            a = fixture(); set_text(a, data); self.rejected(a)

    def test_duplicate_id(self):
        a = fixture(); set_text(a, a[0].replace(b'Check 2: ok', ('Check 2: ' + PID).encode()))
        self.rejected(a)

    def test_exact_id_not_suffix(self):
        a = fixture(); a[2]['checks']['unreachable'] = ['other.' + PID]; self.rejected(a)

    def test_unreachable_status_mismatch(self):
        a = fixture(); set_text(a, a[0].replace(b'Status: UNREACHABLE', b'Status: SUCCESS'))
        self.rejected(a)

    def test_missing_block_or_location(self):
        for old, new in ((b'Check 2:', b'Partial 2:'), (b' - Location:', b' - Missing:')):
            a = fixture(); set_text(a, a[0].replace(old, new)); self.rejected(a)

    def test_wrong_property_count_sequence_success_cover(self):
        a = fixture(); a[2]['n_properties'] += 1; self.rejected(a)
        a = fixture(); set_text(a, a[0].replace(b'Check 2:', b'Check 4:')); self.rejected(a)
        a = fixture(); a[2]['checks']['success'] += 1; self.rejected(a)
        a = fixture(); a[2]['covers']['satisfied'] = ['foreign']; self.rejected(a)

    def test_missing_terminal_or_results_and_wrong_verdict(self):
        for old, new in ((b'RESULTS:', b'PARTIAL:'), (b'Verification Time:', b'Partial Time:'),
                         (b'SUCCESSFUL', b'FAILED')):
            a = fixture(); set_text(a, a[0].replace(old, new)); self.rejected(a)

    def test_raw_quotes_multiline_and_builtin_line_without_column(self):
        a = fixture()
        set_text(a, a[0].replace(b'ordinary check', b'raw "quote"\nand newline').replace(
            b'fmt/mod.rs:820:38', b'fmt/mod.rs:820'))
        checks, _ = bind_stdout(*a)
        self.assertEqual(checks['ok']['description'], 'raw "quote"\nand newline')
        self.assertIsNone(checks[PID]['column'])

    def test_check_outside_results(self):
        a = fixture(); set_text(a, a[0].replace(b'RESULTS:\n', b'').replace(
            b'SUMMARY:', b'RESULTS:\nSUMMARY:')); self.rejected(a)

    def test_no_unreachable_still_requires_complete_stdout(self):
        a = fixture(); a[2]['checks']['unreachable'] = []
        a[2]['checks']['success'] = 2
        set_text(a, a[0].replace(b'UNREACHABLE', b'SUCCESS'))
        bind_stdout(*a)
        a[4]['execution']['stdout_truncated'] = True; self.rejected(a)


class RoleTests(unittest.TestCase):
    def test_exact_defensive_rule(self):
        self.assertEqual(role(record(), RULES)['role'], 'defensive_branch')

    def test_unknown_file_function_site_description_or_class(self):
        for key, value in (('file', 'other.rs'), ('function', 'other'), ('line', 821),
                           ('description', 'required assertion'), ('id', 'fmt.postcondition.1')):
            r = record(); r[key] = value
            self.assertEqual(role(r, RULES)['role'], 'UNKNOWN')

    def test_required_target_roles_precede_exemptions(self):
        for name in ('postcondition', 'frame', 'relation', 'required_section'):
            r = record('slice::sort::shared::smallsort::target',
                       'library/core/src/slice/sort/shared/smallsort.rs', 715,
                       {'postcondition': 'postcondition', 'frame': 'modifies frame',
                        'relation': 'relation assertion', 'required_section': 'required section'}[name])
            self.assertEqual(role(r, RULES)['role'], name)

    def test_target_arithmetic_not_blanket_exempt(self):
        fn = 'slice::sort::shared::smallsort::sort4_stable::<u8, F>'
        r = record(fn, 'library/core/src/slice/sort/shared/smallsort.rs', 715,
                   'attempt to add with overflow')
        self.assertEqual(role(r, RULES)['role'], 'defensive_branch')
        r['description'] = 'assertion failed: sorted(v)'
        self.assertEqual(role(r, RULES)['role'], 'UNKNOWN')


class IntegrationTests(unittest.TestCase):
    def fixture(self, r):
        f = prior_tests.PolicyTests(); f.setUp()
        f.h['checks']['unreachable'] = [r['id']]
        f.h['checks']['success'] = 1
        f.roles[r['id']] = role(r, RULES)
        return f

    def test_defensive_to_policy_accepted_unknown_to_unknown(self):
        f = self.fixture(record())
        self.assertEqual(f.run_policy()['status'], 'ACCEPTED')
        f = self.fixture(record(description='unmapped custom condition'))
        self.assertEqual(f.run_policy()['status'], 'UNKNOWN')

    def test_required_postcondition_to_policy_block(self):
        r = record('slice::sort::shared::smallsort::target',
                   'library/core/src/slice/sort/shared/smallsort.rs', 715, 'postcondition')
        f = self.fixture(r)
        result = f.run_policy()
        self.assertEqual(result['status'], 'PENDING')
        self.assertEqual(result['unreachable'][0]['decision'], 'BLOCK')

    def test_wrapper_pending_and_consumer_leaf_gate_survive(self):
        f = self.fixture(record())
        f.mapping['binding']['wrapper_status'] = 'PENDING'
        leaf = f.run_policy()
        consumer = dict(f.row, id='consumer', mode='Replace:P', leaf_companion='leaf')
        result = {'id': 'consumer', 'status': 'ACCEPTED', 'unknown_reasons': [], 'pending_reasons': []}
        results = {'leaf': leaf, 'consumer': result}
        policy.consumers_after_leaves([consumer, f.row], results)
        self.assertEqual(results['leaf']['status'], 'PENDING')
        self.assertEqual(results['consumer']['status'], 'PENDING')
        self.assertIn('MATCHING_LEAF_NOT_ACCEPTED', results['consumer']['pending_reasons'])

    def test_offset_nonzst_and_zst_are_distinct(self):
        for ty, rule_id in (('u8', 'offset-nonzst'), ('()', 'offset-zst-forbidden-call-entry')):
            r = record('kani::rustc_intrinsics::ptr_offset_from::<' + ty + '>',
                       'library/core/src/lib.rs', 357, 'Cannot compute offset of a ZST')
            self.assertEqual(role(r, RULES)['rule'], rule_id)
        r['function'] = 'kani::rustc_intrinsics::ptr_offset_from::<UnknownType>'
        self.assertEqual(role(r, RULES)['role'], 'UNKNOWN')


if __name__ == '__main__':
    unittest.main()
