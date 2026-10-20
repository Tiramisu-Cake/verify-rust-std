"""Small synthetic controls for lossless audit numbers and scalar types."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
HERE = Path(__file__).resolve().parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

P = load("numeric_packager", "package-evidence.py")
V = load("numeric_verifier", "verify-evidence.py")

class AuditNumericTests(unittest.TestCase):
    def test_invalid_json_and_audit_shapes_fail_without_mutation(self):
        for text in ('{', 'null', '[]', '{}', '{"accepted":null}',
                     '{"accepted":0}', '{"accepted":false,"x":NaN}'):
            raw = text.encode() + b' ' * 2048
            payload = {"proof-audit.json": raw}
            with self.subTest(text=text), patch.object(P, "METADATA_MAX_BYTES", 1000):
                with self.assertRaises(ValueError):
                    P.canonicalize_oversized_proof_audits(payload)
                self.assertEqual(payload, {"proof-audit.json": raw})

    def test_companion_file_and_directory_collisions_fail_without_mutation(self):
        source = "allprooflogs/proof-audit.json"
        raw = b'{"accepted":false}' + b' ' * 2048
        for collision in (source + ".original-bytes", source + ".original-bytes/child.txt",
                          "allprooflogs"):
            payload = {source: raw, collision: b"existing"}
            before = dict(payload)
            with self.subTest(collision=collision), patch.object(P, "METADATA_MAX_BYTES", 1000):
                with self.assertRaisesRegex(ValueError, "companion path collision"):
                    P.canonicalize_oversized_proof_audits(payload)
                self.assertEqual(payload, before)

    def test_numeric_loss_rejected_without_mutating_inputs(self):
        for token in ("1e9999", "1e-9999", "1.2345678901234567890123456789"):
            raw = ('{"accepted":false,"x":' + token + '}' + ' ' * 2048).encode()
            payload = {"proof-audit.json": raw}
            with self.subTest(token=token), patch.object(P, "METADATA_MAX_BYTES", 1000):
                with self.assertRaises(ValueError):
                    P.canonicalize_oversized_proof_audits(payload)
                self.assertEqual(payload, {"proof-audit.json": raw})
    def test_original_preservation_limit_is_explicit(self):
        payload = {"proof-audit.json": b'{"accepted":false}' + b' ' * 2048}
        with patch.object(P, "METADATA_MAX_BYTES", 1000), patch.object(P, "ORIGINAL_AUDIT_MAX_BYTES", 1500):
            with self.assertRaises(ValueError) as error:
                P.canonicalize_oversized_proof_audits(payload)
            self.assertIn("original_limit_bytes=1500", str(error.exception))
            self.assertEqual(len(payload), 1)
    def test_bool_number_tamper_and_precision_loss_fail_content_check(self):
        self.assertTrue(V.audit_canonicalization_matches(b'{ "accepted": false, "x": true }', b'{"accepted":false,"x":true}\n'))
        self.assertFalse(V.audit_canonicalization_matches(b'{"accepted":false,"x":true}', b'{"accepted":false,"x":1}\n'))
        self.assertFalse(V.audit_canonicalization_matches(b'{"accepted":false,"x":1e9999}', b'{"accepted":false,"x":Infinity}\n'))
        self.assertFalse(V.audit_canonicalization_matches(b'{"accepted":false,"x":1e-9999}', b'{"accepted":false,"x":0.0}\n'))

if __name__ == "__main__":
    unittest.main()
