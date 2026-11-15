import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

MODULE_PATH = Path(__file__).resolve().parent / "sensitivity.py"
spec = importlib.util.spec_from_file_location("sensitivity_ci", MODULE_PATH)
sc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sc)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def patch_for(path, old, new):
    # A deterministic one-line patch with git-compatible a/ and b/ paths.
    return (f"--- a/{path}\n+++ b/{path}\n@@ -1 +1 @@\n-{old.decode().rstrip()}\n+{new.decode().rstrip()}\n").encode()


class FakeCI:
    def __init__(self, root, outcome="ok"):
        self.ROOT = root
        self.outcome = outcome
        self.snapshot_labels = []

    def inputs(self):
        return ({"source_sha": sc.SOURCE_SHA,
                 "sensitivity": {"manifest_sha256": sha(sc.MANIFEST_PATH.read_bytes())}}, {})

    @staticmethod
    def save(path, data):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n")

    def snapshot(self, label, out):
        status = subprocess.check_output(
            ["git", "status", "--porcelain=v1", "--untracked-files=normal"],
            cwd=self.ROOT, text=True,
        )
        if status:
            raise ValueError("synthetic source tree not clean")
        self.snapshot_labels.append(label)

    def execute(self, name, argv, out, expected=None, timeout=None):
        out = Path(out)
        variant_id = name.removeprefix("sensitivity-")
        variant = next(v for v in load_test_manifest()["variants"] if v["id"] == variant_id)
        run_dir = out / name
        run_dir.mkdir(parents=True, exist_ok=True)
        selector = variant["selector"]
        if self.outcome == "missing" and variant_id == "positive-remove-useful-assertion":
            stdout = stderr = ""
            native = None
        elif self.outcome == "partial" and variant_id == "positive-remove-useful-assertion":
            stdout = f"test {selector} ... FAILED\ntest result: FAILED. 0 passed; 1 failed; 0 ignored;\n"
            stderr = ""
            native = "SUMMARY:\n ** 0 of 3 failed\n"
        elif self.outcome == "unsupported" and variant_id == "positive-remove-useful-assertion":
            stdout = f"test {selector} ... FAILED\ntest result: FAILED. 0 passed; 1 failed; 0 ignored;\nUnsupported target\n"
            stderr = ""
            native = native_for(variant_id)
        elif self.outcome == "compile" and variant_id == "positive-remove-useful-assertion":
            stdout = f"test {selector} ... FAILED\ntest result: FAILED. 0 passed; 1 failed; 0 ignored;\nerror: could not compile test\n"
            stderr = ""
            native = native_for(variant_id)
        else:
            diagnostic = {
                "positive-remove-useful-assertion": "lawful_modifies_preserves_outside.assertion.3",
                "negative-extra-reached-failure": "** 1 of",
                "negative-repair-user-write": "Check that *var_7 is assignable / Status: FAILURE",
                "golden-invert-required-count": "** 1 of",
            }[variant_id]
            stdout = (f"test {selector} ... FAILED\ntest result: FAILED. 0 passed; 1 failed; 0 ignored;\n"
                      f"error: test failed: expected output to contain the line(s):\n{diagnostic}\n")
            stderr = ""
            native = native_for(variant_id)
        (run_dir / "stdout.txt").write_text(stdout)
        (run_dir / "stderr.txt").write_text(stderr)
        # Derive compiletest's expected-mode .out path, matching the helper.
        build_base = Path(argv[argv.index("--build-base") + 1])
        native_path = sc._native_output_path(build_base, variant)
        if native is not None:
            native_path.parent.mkdir(parents=True, exist_ok=True)
            native_path.write_text(native)
        exit_code, termination = (1, "EXIT")
        if self.outcome == "timeout" and variant_id == "positive-remove-useful-assertion":
            exit_code, termination = (-9, "TIMEOUT")
        if self.outcome == "launch" and variant_id == "positive-remove-useful-assertion":
            exit_code, termination = (None, "LAUNCH_ERROR")
        record = {"name": name, "argv": argv, "exit": exit_code,
                  "termination_reason": termination, "result": "FAIL_OR_UNKNOWN",
                  "problems": []}
        self.save(run_dir / "result.json", record)
        return False


def native_for(variant_id):
    head = "Checking harness synthetic...\n"
    if variant_id == "positive-remove-useful-assertion":
        middle = ("Check 0: lawful_modifies_preserves_outside.assertion.2\n"
                  "\t - Status: SUCCESS\n\t - Description: \"assertion failed: out == 29\"\n")
        n, verification, complete = 0, "SUCCESSFUL", "Complete - 1 successfully verified harnesses, 0 failures, 1 total."
        summary = "** 0 of 3 failed"
    elif variant_id == "negative-extra-reached-failure":
        middle = ("Check 0: frame_target::\n\t - Status: FAILURE\n"
                  "\t - Description: \"Check that *var_7 is assignable\"\n"
                  "Check 1: frame_negative::assertion.1\n\t - Status: FAILURE\n"
                  "\t - Description: \"\"s5 independent reached failure\"\"\n")
        n, verification, complete = 2, "FAILED", "Complete - 0 successfully verified harnesses, 1 failures, 1 total."
        summary = "** 2 of 3 failed"
    elif variant_id == "negative-repair-user-write":
        middle = ("Check 0: frame_target::\n\t - Status: SUCCESS\n"
                  "\t - Description: \"Check that *var_7 is assignable\"\n")
        n, verification, complete = 0, "SUCCESSFUL", "Complete - 1 successfully verified harnesses, 0 failures, 1 total."
        summary = "** 0 of 2 failed (2 unreachable)"
    else:
        middle = ("Check 0: lawful_modifies_preserves_outside.assertion.2\n"
                  "\t - Status: SUCCESS\n\t - Description: \"assertion failed: out == 29\"\n")
        n, verification, complete = 0, "SUCCESSFUL", "Complete - 1 successfully verified harnesses, 0 failures, 1 total."
        summary = "** 0 of 3 failed"
    return f"{head}{middle}SUMMARY:\n {summary}\nVERIFICATION:- {verification}\n{complete}\n"


def setup_fixture(testcase):
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name) / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Synthetic"], cwd=root, check=True)
    paths = {
        "tests/expected/uninit/private-transfer-frame/lawful-modifies.rs": b"original-lawful\n",
        "tests/expected/uninit/maybe-uninit-contract-frame/main.rs": b"original-frame\n",
        "tests/expected/uninit/private-transfer-frame/lawful-modifies.expected": b"golden-count-zero\n",
    }
    for rel, payload in paths.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    patch_dir = Path(temp.name) / "patches"
    patch_dir.mkdir()
    variants = []
    specs = [
        ("positive-remove-useful-assertion", "lawful-modifies.rs", paths["tests/expected/uninit/private-transfer-frame/lawful-modifies.rs"], b"mutant-lawful\n", "SUCCESS", 0, "assertion.3 removed"),
        ("negative-extra-reached-failure", "main.rs", paths["tests/expected/uninit/maybe-uninit-contract-frame/main.rs"], b"mutant-extra\n", "FAILURE", 2, "extra reached failure"),
        ("negative-repair-user-write", "main.rs", paths["tests/expected/uninit/maybe-uninit-contract-frame/main.rs"], b"mutant-repair\n", "SUCCESS", 0, "repair user write"),
        ("golden-invert-required-count", "lawful-modifies.expected", paths["tests/expected/uninit/private-transfer-frame/lawful-modifies.expected"], b"golden-count-one\n", "SUCCESS", 0, "count inversion"),
    ]
    paths_by_id = [
        "tests/expected/uninit/private-transfer-frame/lawful-modifies.rs",
        "tests/expected/uninit/maybe-uninit-contract-frame/main.rs",
        "tests/expected/uninit/maybe-uninit-contract-frame/main.rs",
        "tests/expected/uninit/private-transfer-frame/lawful-modifies.expected",
    ]
    selectors = [
        "[expected] expected/uninit/private-transfer-frame/lawful-modifies.rs",
        "[expected] expected/uninit/maybe-uninit-contract-frame/main.rs",
        "[expected] expected/uninit/maybe-uninit-contract-frame/main.rs",
        "[expected] expected/uninit/private-transfer-frame/lawful-modifies.rs",
    ]
    for spec_row, rel, selector in zip(specs, paths_by_id, selectors):
        ident, _, old, new, verdict, n, reason = spec_row
        patch = patch_for(rel, old, new)
        patch_path = patch_dir / (ident + ".patch")
        patch_path.write_bytes(patch)
        variants.append({"id": ident, "selector": selector, "input": rel,
                         "mutated_path": rel, "input_sha256": sha(old),
                         "patch": str(patch_path), "patch_sha256": sha(patch),
                         "predicted_native_verdict": verdict, "predicted_native_N": n,
                         "expected_mismatch_reason": reason})
    subprocess.run(["git", "add", "tests"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "synthetic base"], cwd=root, check=True)
    manifest_path = Path(temp.name) / "manifest.json"
    manifest_path.write_text(json.dumps({"execution": "NOT_RUN", "variants": variants}))
    testcase._temp = temp
    testcase.root = root
    testcase.manifest = manifest_path
    testcase.variants = variants


def load_test_manifest():
    return json.loads(sc.MANIFEST_PATH.read_text())


class SensitivityRunnerTests(unittest.TestCase):
    def setUp(self):
        setup_fixture(self)
        self.original_manifest_path = sc.MANIFEST_PATH
        sc.MANIFEST_PATH = self.manifest
        # FakeCI needs access to synthetic variants during execute.
        globals()["load_test_manifest"] = lambda: {"variants": self.variants}
        self.out = self.root.parent / "evidence"
        FakeCI.save(self.out / "suite-expected" / "result.json", {
            "exit": 0, "termination_reason": "EXIT",
            "result": "EXIT_ZERO_COUNTS_MATCH_REQUIRES_REVIEW", "problems": [],
        })

    def tearDown(self):
        sc.MANIFEST_PATH = self.original_manifest_path
        self._temp.cleanup()

    def test_all_four_complete_expected_mismatches_restore_original_sources(self):
        ci = FakeCI(self.root)
        self.assertTrue(sc.run_sensitivity(ci, self.out))
        self.assertEqual(ci.snapshot_labels, [
            label for v in self.variants for label in
            ("sensitivity-" + v["id"] + "-before", "sensitivity-" + v["id"] + "-after")
        ])
        self.assertEqual(subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root, text=True), "")
        report = json.loads((self.out / "sensitivity" / "result.json").read_text())
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(len(report["variants"]), 4)
        for variant in self.variants:
            evidence_dir = self.out / ("sensitivity-" + variant["id"])
            self.assertTrue((evidence_dir / "mutation.patch").is_file())
            self.assertTrue((evidence_dir / "mutated-input.bin").is_file())

    def test_repaired_write_detection_tolerates_local_renumbering(self):
        variant = self.variants[2]
        native = native_for(variant["id"])
        self.assertFalse(sc._variant_expectation(variant, native))
        for local in ("var_8", "var_42"):
            self.assertFalse(sc._variant_expectation(variant, native.replace("var_7", local)))
        wrong = native.replace("Status: SUCCESS", "Status: FAILURE", 1)
        self.assertTrue(sc._variant_expectation(variant, wrong))
        missing = native.replace("Check that *var_7 is assignable", "unrelated successful check")
        self.assertTrue(sc._variant_expectation(variant, missing))

    def test_repaired_write_requires_intended_failure_mismatch(self):
        variant = self.variants[2]
        stdout = (f"test {variant['selector']} ... FAILED\n"
                  "test result: FAILED. 0 passed; 1 failed; 0 ignored;\n"
                  "test failed: expected output to contain the line(s):\nStatus: FAILURE\n")
        record = {"exit": 1, "termination_reason": "EXIT"}
        self.assertTrue(sc._validate_compiletest(record, variant["selector"], stdout, "",
                                               native_for(variant["id"]), "", variant))
        stdout += "Check that *var_7 is assignable\n"
        self.assertFalse(sc._validate_compiletest(record, variant["selector"], stdout, "",
                                                native_for(variant["id"]), "", variant))

    def test_bad_or_incomplete_compiletest_evidence_fails_and_restores(self):
        for outcome in ("missing", "partial", "unsupported", "compile", "timeout", "launch"):
            with self.subTest(outcome=outcome):
                ci = FakeCI(self.root, outcome)
                self.assertFalse(sc.run_sensitivity(ci, self.out))
                self.assertEqual(subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root, text=True), "")
                report = json.loads((self.out / "sensitivity" / "result.json").read_text())
                self.assertEqual(report["result"], "FAIL_OR_UNKNOWN")

    def test_false_nonzero_native_verdict_is_rejected(self):
        variant = self.variants[1]
        bad_native = native_for("negative-extra-reached-failure").replace("** 2 of 3", "** 1 of 3")
        bad = sc._variant_expectation(variant, bad_native)
        self.assertTrue(any("SUMMARY count" in problem for problem in bad))

    def test_summary_requires_adjacent_numeric_renderer_line_and_rejects_undetermined(self):
        variant = self.variants[2]
        native = native_for(variant["id"])
        self.assertFalse(any("SUMMARY count" in p for p in sc._variant_expectation(variant, native)))
        nonadjacent = native.replace("SUMMARY:\n **", "SUMMARY:\n ignored header\n **")
        self.assertTrue(any("SUMMARY count" in p for p in sc._variant_expectation(variant, nonadjacent)))
        undetermined = native.replace("VERIFICATION:- SUCCESSFUL", "VERIFICATION:- UNDETERMINED")
        self.assertTrue(any("undetermined" in p for p in sc._variant_expectation(variant, undetermined)))

    def test_wrong_status_and_missing_intended_mismatch_diagnostic_fail(self):
        variant = self.variants[1]
        wrong_status = native_for("negative-extra-reached-failure").replace("Status: FAILURE", "Status: SUCCESS", 1)
        self.assertTrue(any("outside-assigns check" in p for p in sc._variant_expectation(variant, wrong_status)))
        good_native = native_for("positive-remove-useful-assertion")
        variant = self.variants[0]
        bad = sc._validate_compiletest(
            {"exit": 1, "termination_reason": "EXIT"}, variant["selector"],
            f"test {variant['selector']} ... FAILED\ntest result: FAILED. 0 passed; 1 failed; 0 ignored;\n",
            "", good_native, "", variant)
        self.assertTrue(any("intended expected-output mismatch" in p for p in bad))

    def test_extra_reached_assertion_must_be_failure_itself(self):
        variant = self.variants[1]
        native = native_for("negative-extra-reached-failure")
        native = native.replace(
            'Check 1: frame_negative::assertion.1\n\t - Status: FAILURE',
            'Check 1: frame_negative::assertion.1\n\t - Status: SUCCESS',
        )
        native += ('Check 2: unrelated::assertion.2\n\t - Status: FAILURE\n'
                   '\t - Description: "unrelated failure"\n')
        self.assertTrue(any("added reached failure is not recorded" in p
                            for p in sc._variant_expectation(variant, native)))

    def test_missing_or_duplicate_completion_is_rejected(self):
        native = native_for("positive-remove-useful-assertion")
        variant = self.variants[0]
        self.assertTrue(any("completion record" in p for p in
                            sc._variant_expectation(variant, native.replace("Complete -", "Done -"))))
        self.assertTrue(any("completion record" in p for p in
                            sc._variant_expectation(variant, native + "Complete - 1 successfully verified harnesses, 0 failures, 1 total.\n")))

    def test_wrong_patch_hash_or_path_fails_without_leaving_source_dirty(self):
        variant = self.variants[0]
        Path(variant["patch"]).write_text("wrong bytes\n")
        ci = FakeCI(self.root)
        self.assertFalse(sc.run_sensitivity(ci, self.out))
        self.assertEqual(subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root, text=True), "")

    def test_wrong_patch_path_fails_without_mutating_source(self):
        self.variants[0]["patch"] = str(self.manifest.parent / "missing.patch")
        self.manifest.write_text(json.dumps({"execution": "NOT_RUN", "variants": self.variants}))
        ci = FakeCI(self.root)
        self.assertFalse(sc.run_sensitivity(ci, self.out))
        self.assertEqual(subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root, text=True), "")

    def test_wrong_manifest_and_duplicate_variant_ids_fail_before_mutation(self):
        ci = FakeCI(self.root)
        self.manifest.write_text("{}\n")
        self.assertFalse(sc.run_sensitivity(ci, self.out))
        self.assertEqual(subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root, text=True), "")
        duplicate = [*self.variants[:-1], dict(self.variants[0])]
        self.manifest.write_text(json.dumps({"execution": "NOT_RUN", "variants": duplicate}))
        self.assertFalse(sc.run_sensitivity(ci, self.out))
        self.assertEqual(subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root, text=True), "")

    def test_missing_clean_suite_gate_prevents_mutations(self):
        (self.out / "suite-expected" / "result.json").unlink()
        ci = FakeCI(self.root)
        self.assertFalse(sc.run_sensitivity(ci, self.out))
        self.assertEqual(ci.snapshot_labels, [])
        self.assertEqual(subprocess.check_output(["git", "status", "--porcelain"], cwd=self.root, text=True), "")


if __name__ == "__main__":
    unittest.main()
