"""Allowed static/synthetic checks; no Rust compiler or verifier execution."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / 'tools'))
import test_diagnostic_trace as fixtures
from check_semantics import check, normalize
from estimate_capacity import estimate


class CompactTests(unittest.TestCase):
    def test_semantic_tokens_preserved(self):
        self.assertEqual(len(check()), 5)

    def test_semantic_comparator_detects_real_change(self):
        a = 'let body = self.transformer.body(self.tcx, instance);'
        self.assertNotEqual(normalize(a), normalize(a.replace('self.transformer.body', 'instance.body')))
        a = 'for instruction in instructions.into_iter().rev() { self.build_check_for_instruction(&mut body, instruction, source); }'
        self.assertNotEqual(normalize(a), normalize(a.replace('.rev()', '')))

    def test_capacity_estimate_fits_fixed_caps(self):
        result = estimate()
        self.assertLessEqual(result['projected_total_records'], 510)
        self.assertLessEqual(result['projected_total_bytes'], 256000)

    def test_compact_consumer_survives_reader_with_null_or_known_writer(self):
        name = 'core::ops::index_range::IndexRange::len'
        root = 'core::slice::sort::shared::smallsort::verify::uninit_probe::cmp3_index_range_len'
        ctx = {'root': root, 'stage': 'codegen', 'unit': 0}
        records = [
            {'kind': 'codegen_order', 'data': {'ordinal': 1}},
            {'kind': 'goto_function_presence', 'data': {'root': root, 'function': 'IndexRange::len',
             'phase': 'final_reachable_items_before_emission', 'instances': [{'instance': name}], 'absent': False}},
            {'kind': 'memory_init_ops_summary', 'data': {'instance': name, 'instructions': 8, 'zero_ops': 6, 'nonzero_ops': 2}},
            {'kind': 'goto_body_consumed', 'data': {'instance': name, 'mangled_symbol': 's' * 100,
             'body_hash': 'a' * 16, 'body_hash_algorithm': 'std-default-hasher-64', 'dump_bytes': 1000,
             'dump_ok': True, 'phase': 'before_goto_blocks', 'last_writer': None}},
        ]
        for writer in (None, {'writer': 'DelayedUbPass', 'body_hash': 'a' * 16, 'dump_ok': True,
                              'context': {**ctx, 'root': root.replace('cmp3_index_range_len', 'cmp3_into_iter_next')}}):
            rows = copy.deepcopy(records); rows[-1]['data']['last_writer'] = writer
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp)
                fixtures.sidecar(path, json.dumps(fixtures.REQUEST, separators=(',', ':')), records=rows, context=ctx)
                encoded = (path / 'kani3300-trace-1-0.jsonl').read_bytes().splitlines()
                self.assertLessEqual(max(map(len, encoded)) + 1, 2048)
                result = fixtures.collect(path)
                self.assertEqual(result['state'], 'COMPLETE', result['errors'])
                self.assertEqual(result['records'][-1]['data']['last_writer'], writer)


if __name__ == '__main__':
    unittest.main()
