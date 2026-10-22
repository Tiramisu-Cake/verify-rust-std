"""Isolated synthetic admission tests; never generates an actual proof unit."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[2] / "networks" / "prove.py"
spec = importlib.util.spec_from_file_location("prove_admission_test", PATH)
prove = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prove)


class AdmissionTests(unittest.TestCase):
    def test_synthetic_source_schedule_and_executable_gates(self):
        # Small synthetic service input, never the actual source extractor.
        text = ("fn sort9_optimal<T, F>(v: &mut [T], is_less: &mut F)\n"
                "where\n    F: FnMut(&T, &T) -> bool,\n{\n"
                "    if v.len() < 9 {\n        intrinsics::abort();\n    }\n"
                "    let v_base = v.as_mut_ptr();\n    unsafe {\n"
                "        swap_if_less(v_base, 0, 1, is_less);\n    }\n}\n")
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "synthetic.rs"
            source.write_text(text)
            schedule = prove.digest(b"[[0,1]]")
            with patch.object(prove, "SOURCE", source), patch.object(prove, "CALL_COUNTS", {9: 1}), patch.object(prove, "SCHEDULE_SHA256", {9: schedule}):
                with patch.object(prove, "SOURCE_SHA256", prove.digest(text.encode())):
                    self.assertEqual(prove.extract(9)[0], [(0, 1)])
                    source.write_text(text + "// changed\n")
                    with self.assertRaisesRegex(RuntimeError, "SHA256"):
                        prove.extract(9)
                for changed, error in ((text.replace("0, 1,", "0, 2,"), "schedule"),
                                       (text.replace("    unsafe {", "    extra();\n    unsafe {"), "executable")):
                    source.write_text(changed)
                    with patch.object(prove, "SOURCE_SHA256", prove.digest(changed.encode())):
                        with self.assertRaisesRegex(RuntimeError, error):
                            prove.extract(9)

    def test_multibody_negative_requires_checked_dependencies(self):
        source = ("lemma void dependency()\n{}\nlemma void target()\n{\n"
                  "    assert false;\n}\n")
        log = ("0s: test.c(1,1-2): Verifying function 'dependency'\n"
               "0s: test.c(2,1-2): Executing return statement\nLeak check.\n"
               "0s: test.c(3,1-2): Verifying function 'target'\n"
               "0s: test.c(5,5-17): Executing statement\n"
               "test.c(5,5-17): error: Assertion might not hold. (Cannot prove false.)\n")
        metadata = {"target_line": 5, "expected_predicate": "false",
                    "expected_bodies": ["dependency", "target"]}
        gate = lambda output=log, status=1, unchanged=True, meta=metadata: prove.negative_gate(
            Path("test.c"), source, output, status, meta, unchanged)
        self.assertTrue(gate())
        for original, replacement in (("Leak check.", ""), ("Executing return statement", ""),
                                       ("Verifying function 'dependency'", ""),
                                       ("(5,5-17): error:", "(4,5-17): error:"),
                                       ("Cannot prove false.", "Cannot prove other."),
                                       ("(5,5-17): Executing statement", "")):
            self.assertFalse(gate(log.replace(original, replacement)))
        self.assertFalse(gate(status=124))
        self.assertFalse(gate(unchanged=False))
        self.assertFalse(gate(meta={"target_line": 5, "expected_predicate": "false"}))


if __name__ == "__main__":
    unittest.main()
