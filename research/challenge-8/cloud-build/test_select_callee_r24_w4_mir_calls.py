from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest


HELPER = Path(__file__).with_name('select-callee-r24-w4-mir-calls.py')
SPEC = importlib.util.spec_from_file_location('r24_w4_mir_calls_tested', HELPER)
MIR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MIR)


def _raw_ptr(mutability='not', depth=1):
    ty = {'kind': {'param': 'T'}}
    for _ in range(depth):
        ty = {'kind': {'rawPtr': {'ty': ty, 'mutability': {mutability: 'void'}}}}
    return ty


def _span(line, lo, hi, path='verified/lib.rs'):
    def point(pos):
        return {'file': {'name': {'real': {'localPath': path}}},
                'line': line, 'col': {'pos': pos}}
    return {'regular': {'lo': point(lo), 'hi': point(hi)}}


def _source_info(line, lo=1, hi=2):
    return {'span': _span(line, lo, hi)}


def _fn(callee=MIR.CALLEE, mutability='not', depth=1, subst_count=1,
        late_bound=0):
    subst = {'kind': {'type': _raw_ptr(mutability, depth)}}
    return {'constant': {'const': {
        'constValue': {'zeroSized': 'void'},
        'ty': {'kind': {'fnDef': {
            'id': {'name': callee},
            'substs': [subst for _ in range(subst_count)],
            'lateBoundGenericParamCount': late_bound,
        }}},
    }}}


def _local(name, ty, line, lo=1, hi=2):
    return {'mutability': {'mut': 'void'}, 'id': {'name': name}, 'ty': ty,
            'sourceInfo': _source_info(line, lo, hi)}


def _operand(name):
    return {'move': {'local': {'name': name}, 'projection': [],
                     'localIsMutable': True, 'kind': {'other': 'void'}}}


def _body(mode='normal'):
    body = {
        'defKind': {'fn': 'void'},
        'defPath': MIR.EXPECTED_DEF_PATH,
        'localDecls': [],
        'basicBlocks': [],
    }
    for i in range(8):
        line = 372 + i
        names = [f'_{mode}_{i}_{n}' for n in ('bool', 'left', 'right', 'dst')]
        body['localDecls'].extend([
            _local(names[0], {'kind': {'bool': 'void'}}, line),
            _local(names[1], _raw_ptr(), line, 3, 4),
            _local(names[2], _raw_ptr(), line, 5, 6),
            _local(names[3], _raw_ptr(), line, 7, 8),
        ])
        call = {
            'func': _fn(),
            'args': [_operand(name) for name in names[:3]],
            'destination': {'local': {'name': names[3]}, 'projection': [],
                            'localIsMutable': False, 'kind': {'other': 'void'}},
            'callSpan': _span(line, 9, 31),
            'target': {'something': {'index': i + 1}},
            'unwindAction': {'continue': 'void'},
        }
        body['basicBlocks'].append({
            'id': {'index': i},
            'statements': [],
            'terminator': {'sourceInfo': _source_info(line, 9, 31),
                           'kind': {'call': call}},
            'isCleanup': False,
        })
    return body


def _emit(value):
    if isinstance(value, dict):
        return '( ' + ', '.join(f'{key} = {_emit(child)}' for key, child in value.items()) + ' )'
    if isinstance(value, list):
        return '[ ' + ', '.join(_emit(child) for child in value) + ' ]'
    if isinstance(value, str):
        if value == 'void':
            return value
        return json.dumps(value)
    if value is True:
        return 'true'
    if value is False:
        return 'false'
    return str(value)


def _analyze(normal=None, readonly=None):
    return MIR.analyze_pair(_emit(normal or _body('normal')),
                            _emit(readonly or _body('readonly')))


class W4MirCallTests(unittest.TestCase):
    def test_extracts_eight_typed_const_pointer_calls_and_preserves_metadata(self):
        report = _analyze()
        self.assertTrue(report['complete'], report['errors'])
        self.assertEqual(report['status'], 'COMPLETE_TYPED_MIR_OBSERVATION')
        self.assertEqual(report['schema'], 'select-r24-w4-mir-calls-v1')
        self.assertEqual(report['scope'], 'TYPED_MIR_OBSERVATION_ONLY')
        self.assertEqual(report['typed_call_linkage'], 'UNKNOWN')
        self.assertEqual(report['typed_callee_family_observation'],
                         'OBSERVED_STRUCTURAL_MIR_CALLS')
        self.assertEqual(report['source_site_mapping'], 'EQUAL_EMITTED_COORDINATES_ONLY')
        self.assertEqual(len(report['normal']['calls']), 8)
        row = report['normal']['calls'][0]
        self.assertEqual(row['callee'], MIR.CALLEE)
        self.assertEqual(row['operand_local_ids'], ['_normal_0_bool',
                                                     '_normal_0_left',
                                                     '_normal_0_right'])
        self.assertEqual(row['destination_local_id'], '_normal_0_dst')
        self.assertEqual(row['call_span']['lo'], {
            'path': 'verified/lib.rs', 'line': 372, 'column_pos': 9})
        self.assertEqual(row['block_index'], 0)
        self.assertEqual(row['fn_def']['lateBoundGenericParamCount'], 0)
        self.assertEqual(row['raw_callee']['constant']['const']['ty']['kind']
                         ['fnDef']['lateBoundGenericParamCount'], 0)
        self.assertFalse(report['proof_claim'])
        self.assertFalse(report['accepted'])
        self.assertEqual(report['proof_credit'], 0)

    def test_nonselector_calls_are_retained_by_not_counted_as_selectors(self):
        normal = _body('normal')
        normal['basicBlocks'][0]['terminator']['kind'] = {'call': {
            'func': _fn('core::ptr::copy'), 'args': [],
            'destination': {'local': {'name': '_normal_0_dst'}, 'projection': [],
                            'localIsMutable': False, 'kind': {'other': 'void'}},
            'callSpan': _span(372, 9, 31),
            'target': {'something': {'index': 1}},
            'unwindAction': {'continue': 'void'},
        }}
        report = _analyze(normal=normal)
        self.assertFalse(report['complete'])
        self.assertIn('count', report['errors'][0])

    def test_const_pointer_mutability_depth_and_generic_arity_are_closed(self):
        mutations = [
            lambda b: b['basicBlocks'][0]['terminator']['kind']['call']['func'].__setitem__(
                'x', _fn(mutability='mut')),
            lambda b: b['basicBlocks'][0]['terminator']['kind']['call']['func'].__setitem__(
                'x', _fn(depth=2)),
            lambda b: b['basicBlocks'][0]['terminator']['kind']['call']['func'].__setitem__(
                'x', _fn(subst_count=2)),
            lambda b: b['basicBlocks'][0]['terminator']['kind']['call']['func'].__setitem__(
                'x', _fn(late_bound=1)),
        ]
        for mutate in mutations:
            normal = _body('normal'); mutate(normal)
            # Keep target counting structural so the malformed original call
            # is still visible as an attempted selector call.
            call = normal['basicBlocks'][0]['terminator']['kind']['call']
            call['func'] = call['func'].pop('x')
            report = _analyze(normal=normal)
            self.assertFalse(report['complete'], report)
            self.assertEqual(report['typed_call_linkage'], 'UNKNOWN')

    def test_wrong_target_mutated_operand_arity_and_operand_form_refuse(self):
        cases = []
        b = _body('normal')
        b['basicBlocks'][0]['terminator']['kind']['call']['func'] = _fn('other::callee')
        cases.append(b)
        b = _body('normal')
        b['basicBlocks'][0]['terminator']['kind']['call']['args'].pop()
        cases.append(b)
        b = _body('normal')
        b['basicBlocks'][0]['terminator']['kind']['call']['args'][0] = {
            'copy': {'local': {'name': '_normal_0_bool'}, 'projection': [],
                     'localIsMutable': True, 'kind': {'other': 'void'}}}
        cases.append(b)
        b = _body('normal')
        b['basicBlocks'][0]['terminator']['kind']['call']['args'][1]['move']['projection'] = [
            {'deref': 'void'}]
        cases.append(b)
        for normal in cases:
            report = _analyze(normal=normal)
            self.assertFalse(report['complete'], report)

    def test_operand_and_destination_local_types_are_resolved_exactly(self):
        cases = []
        b = _body('normal')
        b['localDecls'][1]['ty'] = _raw_ptr(mutability='mut')
        cases.append(b)
        b = _body('normal')
        b['localDecls'][2]['ty'] = _raw_ptr(depth=2)
        cases.append(b)
        b = _body('normal')
        b['localDecls'][3]['ty'] = {'kind': {'bool': 'void'}}
        cases.append(b)
        b = _body('normal')
        b['localDecls'].pop(1)
        cases.append(b)
        for normal in cases:
            report = _analyze(normal=normal)
            self.assertFalse(report['complete'], report)
            self.assertEqual(report['proof_credit'], 0)

    def test_destination_shape_and_call_source_target_pair_must_match(self):
        normal = _body('normal')
        normal['basicBlocks'][0]['terminator']['kind']['call']['destination']['projection'] = [
            {'deref': 'void'}]
        self.assertFalse(_analyze(normal=normal)['complete'])
        normal = _body('normal')
        normal['basicBlocks'][0]['terminator']['kind']['call']['target'] = None
        self.assertFalse(_analyze(normal=normal)['complete'])
        normal = _body('normal')
        normal['basicBlocks'][0]['terminator']['kind']['call']['callSpan'] = _span(999, 9, 31)
        report = _analyze(normal=normal)
        self.assertFalse(report['complete'])
        self.assertIn('spans differ', report['errors'][0])

    def test_malformed_truncated_duplicate_and_escaped_strings_are_safe(self):
        valid = _emit(_body('normal'))
        escaped = valid.replace('verified/lib.rs', 'verified/lib.rs with \\"quote\\" and )],')
        parsed = MIR._parse_record(escaped)
        self.assertEqual(parsed['localDecls'][0]['sourceInfo']['span']['regular']['lo']
                         ['file']['name']['real']['localPath'],
                         'verified/lib.rs with "quote" and )],')
        for text in (valid[:-1], valid + ' garbage', valid.replace('defPath =', 'defPath = "dup", defPath ='),
                     valid.replace('"verified/lib.rs"', r'"broken\q"', 1)):
            report = MIR.analyze_pair(text, _emit(_body('readonly')))
            self.assertFalse(report['complete'], text[:100])
            self.assertEqual(report['status'], 'INCOMPLETE_UNKNOWN')
            self.assertEqual(report['typed_call_linkage'], 'UNKNOWN')

    def test_wrong_source_path_shape_and_body_target_are_incomplete(self):
        normal = _body('normal')
        normal['basicBlocks'][0]['terminator']['kind']['call']['callSpan'] = _span(
            372, 9, 31, path='somewhere-else.rs')
        self.assertFalse(_analyze(normal=normal)['complete'])
        readonly = _body('readonly')
        readonly['defPath'] = 'other::body'
        self.assertFalse(_analyze(readonly=readonly)['complete'])

    def test_both_records_with_same_wrong_function_defpath_refuse(self):
        normal = _body('normal'); normal['defPath'] = 'other::function'
        readonly = _body('readonly'); readonly['defPath'] = 'other::function'
        report = _analyze(normal=normal, readonly=readonly)
        self.assertFalse(report['complete'])
        self.assertEqual(report['status'], 'INCOMPLETE_UNKNOWN')
        self.assertIn('exact sort4_stable', report['errors'][0])

    def test_null_wrong_types_and_budget_limits_return_unknown(self):
        for normal in (None, 4, '', 'x' * (MIR.MAX_TEXT_CHARS + 1)):
            report = MIR.analyze_pair(normal, _emit(_body('readonly')))
            self.assertFalse(report['complete'])
            self.assertEqual(report['typed_call_linkage'], 'UNKNOWN')
        normal = _body('normal')
        normal['basicBlocks'][0]['terminator']['sourceInfo'] = None
        self.assertFalse(_analyze(normal=normal)['complete'])


if __name__ == '__main__':
    unittest.main()
