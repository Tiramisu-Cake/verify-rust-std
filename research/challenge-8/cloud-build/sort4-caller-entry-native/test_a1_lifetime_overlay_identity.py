"""Isolated source identity error paths; no tool or proof execution."""
import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('s4_overlay_identity', HERE / 'a1-focus-backend.py')
FOCUS = importlib.util.module_from_spec(spec)
spec.loader.exec_module(FOCUS)

class OverlayIdentity(unittest.TestCase):
    def test_exact_overlay_and_wrong_source_identities(self):
        with tempfile.TemporaryDirectory() as folder:
            tool = Path(folder)
            hashes = {}
            for name in (FOCUS.TR, FOCUS.SCHEMA, FOCUS.EXPORTER, 'bin/verifast',
                         'bin/vf-rust-mir-exporter', 'src/verify_expr.ml'):
                path = tool / name
                path.parent.mkdir(exist_ok=True, parents=True)
                path.write_bytes(name.encode())
                hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
            overlay = dict(source='src/verify_expr.ml',
                           result_sha256=hashes['src/verify_expr.ml'],
                           new_axiom_or_assumed_lemma=False)
            receipt = dict(final_translator_sha256=hashes[FOCUS.TR],
                           final_schema_sha256=hashes[FOCUS.SCHEMA],
                           final_exporter_sha256=hashes[FOCUS.EXPORTER],
                           console_binary_sha256=hashes['bin/verifast'],
                           exporter_binary_sha256=hashes['bin/vf-rust-mir-exporter'],
                           ghost_call_lifetime_inference=overlay)
            FOCUS._tool_identity(tool, receipt)
            for bad in ({}, dict(overlay, source='wrong'),
                        dict(overlay, result_sha256='0' * 64),
                        dict(overlay, new_axiom_or_assumed_lemma=True)):
                with self.subTest(bad=bad), self.assertRaises(RuntimeError):
                    FOCUS._tool_identity(tool, dict(receipt, ghost_call_lifetime_inference=bad))
            (tool / 'src/verify_expr.ml').write_bytes(b'changed after reconstruction')
            with self.assertRaises(RuntimeError):
                FOCUS._tool_identity(tool, receipt)

class BoundedHeaderDiagnostic(unittest.TestCase):
    def test_nested_difference_and_bounded_output(self):
        spec = importlib.util.spec_from_file_location('s4_header_diag', HERE / 'a1-ast-gates.py')
        gates = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gates)
        self.assertEqual(gates._bounded_header_difference((1, 2), (1, 2)), '')
        message = gates._bounded_header_difference(
            ((1, 'actual'), 'x' * 10000, 3, 4), ((1, 'expected'), 'y' * 10000, 5, 6))
        self.assertIn("header/0/1: actual='actual'; expected='expected'", message)
        self.assertEqual(message.count('actual='), 3)
        self.assertNotIn('header/3', message)
        self.assertLess(len(message), 1100)

if __name__ == '__main__':
    unittest.main()
