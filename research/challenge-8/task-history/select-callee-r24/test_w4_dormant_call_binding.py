"""Static authoring checks only: no actual source preparation or native tools."""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

BIND = load('r24_dormant_binding_authoring', 'w4-dormant-call-binding-r24.py')
CERT = load('r24_dormant_input_cert_authoring', 'w4-caller-input-certificates-r24.py')

class DormantBindingTests(unittest.TestCase):
    def test_closed_data_table_exact_37_and_changed_bytes_refused(self):
        raw = (HERE / 'W4-CONTROL-DATA-ALL37-INPUTS.json').read_bytes()
        rows = CERT.rows(raw)
        self.assertEqual(len(rows), 37)
        self.assertEqual(rows[0][0], 'positive')
        self.assertEqual(rows[-1][0], 'c5-cross-scope-read-negative')
        for changed in (b'', raw + b'\n', raw.replace(b'"proof_credit": 0', b'"proof_credit": 1')):
            with self.subTest(changed_size=len(changed)), self.assertRaises(ValueError):
                CERT.rows(changed)
        self.assertIn('let source_only = true', CERT.ocaml_module(raw))
        self.assertNotIn('active := true', CERT.ocaml_module(raw))

    def test_malformed_structures_refuse_even_with_test_digest_rebound(self):
        import copy
        import hashlib
        import json
        from unittest.mock import patch
        original = json.loads((HERE / 'W4-CONTROL-DATA-ALL37-INPUTS.json').read_bytes())
        variants = []
        for key, value in (('accepted', True), ('proof_credit', False),
                           ('universe_count', True), ('callee_qualification', True)):
            changed = copy.deepcopy(original)
            changed[key] = value
            variants.append(changed)
        for change in ('duplicate', 'index-bool', 'bytes-bool', 'wrong-unit-path', 'wrong-tool'):
            changed = copy.deepcopy(original)
            if change == 'duplicate': changed['rows'][1]['variant'] = changed['rows'][0]['variant']
            elif change == 'index-bool': changed['rows'][0]['index'] = False
            elif change == 'bytes-bool': changed['rows'][0]['unit']['bytes'] = True
            elif change == 'wrong-unit-path': changed['rows'][0]['unit']['path'] = '../caller-native-unit.marshal'
            else: changed['tool_hashes']['bin/verifast'] = '0' * 64
            variants.append(changed)
        for changed in variants:
            raw = json.dumps(changed).encode()
            with self.subTest(keys=list(changed)), patch.object(CERT, 'INPUTS_SHA256', hashlib.sha256(raw).hexdigest()):
                with self.assertRaises(ValueError): CERT.rows(raw)

    def test_missing_or_duplicate_authoring_anchor_refused(self):
        with self.assertRaises(AssertionError):
            BIND.generate('')
        with self.assertRaises(AssertionError):
            BIND.once('XX', 'X', 'Y')
        with self.assertRaises(AssertionError):
            BIND.once('', 'X', 'Y')

if __name__ == '__main__':
    unittest.main()
