"""Small synthetic tests for md_classifier; no verifier or runner imports."""
import unittest

from md_classifier import classify_log


SHA = "a" * 64
BASE = {
    "source_sha256": SHA,
    "read_line": 13,
    "target_line": 12,
    "spec_init_line": 88,
}
EXEC = {
    "source_unchanged_at_every_stage": True,
    "source_before": {"original/lib.rs": SHA, "verified/lib.rs": SHA},
    "source_after": {"original/lib.rs": SHA, "verified/lib.rs": SHA},
    "stages": {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 0},
}
HEADER = "1.0s: verified/lib.rs(1,1-2): Verifying function '{}'\n"


class ClassifierTests(unittest.TestCase):
    def test_positive_requires_all_markers_inside_named_body(self):
        log = HEADER.format("positive_manually_drop_after_merge") + (
            "verified/lib.rs(13,5): Executing statement\n"
            "Executing return statement\nLeak check.\n0 errors found\n")
        got = classify_log("positive_manually_drop_after_merge", log, BASE, EXEC)
        self.assertEqual(got["classification"], "REGRESSION_MATCHED")
        helper = HEADER.format("helper") + "Executing return statement\nLeak check.\n"
        got = classify_log("positive_manually_drop_after_merge", helper, BASE, EXEC)
        self.assertEqual(got["classification"], "INCONCLUSIVE")

    def test_positive_rejects_duplicate_body_dead_code_and_modified_source(self):
        body = ("verified/lib.rs(13,5): Executing statement\n"
                "Executing return statement\nLeak check.\n0 errors found\n")
        log = HEADER.format("positive_manually_drop_after_merge") + body
        for suffix in ("verified/lib.rs(40,1): dead code\n",
                       HEADER.format("positive_manually_drop_after_merge") + body):
            self.assertEqual(classify_log("positive_manually_drop_after_merge",
                                          log + suffix, BASE, EXEC)["classification"],
                             "INCONCLUSIVE")
        changed = {**EXEC, "source_before": {"original/lib.rs": SHA,
                                               "verified/lib.rs": SHA},
                   "source_after": {"original/lib.rs": SHA,
                                              "verified/lib.rs": "b" * 64}}
        self.assertEqual(classify_log("positive_manually_drop_after_merge", log,
                                      BASE, changed)["classification"], "INCONCLUSIVE")

    def test_missing_initialization_requires_exact_predicate_location_and_target(self):
        meta = {**BASE, "target_line": 19}
        log = (HEADER.format("negative_missing_reference_initialization") +
               "verified/lib.rs(19,5): Executing statement\n"
               "aliasing.rsspec(88,2): error: No matching heap chunks: "
               "ref_initialized<i32>\n")
        result = classify_log("negative_missing_reference_initialization", log,
                              meta, {**EXEC, "stages": {**EXEC["stages"], "verifast": 1}})
        self.assertEqual(result["classification"], "REGRESSION_MATCHED")
        wrong = log.replace("ref_initialized<i32>", "points_to<i32>")
        self.assertEqual(classify_log("negative_missing_reference_initialization", wrong,
                                      meta, {**EXEC, "stages": {**EXEC["stages"], "verifast": 1}})
                         ["classification"], "INCONCLUSIVE")
        wrong_path = log.replace("aliasing.rsspec(88,2)", "helper.rsspec(88,2)")
        self.assertEqual(classify_log("negative_missing_reference_initialization", wrong_path,
                                      meta, {**EXEC, "stages": {**EXEC["stages"], "verifast": 1}})
                         ["classification"], "INCONCLUSIVE")
        wrong_source_line = log.replace("aliasing.rsspec(88,2)", "aliasing.rsspec(89,2)")
        self.assertEqual(classify_log("negative_missing_reference_initialization", wrong_source_line,
                                      meta, {**EXEC, "stages": {**EXEC["stages"], "verifast": 1}})
                         ["classification"], "INCONCLUSIVE")
        # The source call must be reached even when the intended spec error is elsewhere.
        no_call = log.replace("verified/lib.rs(19,5): Executing statement\n", "")
        self.assertEqual(classify_log("negative_missing_reference_initialization", no_call,
                                      meta, {**EXEC, "stages": {**EXEC["stages"], "verifast": 1}})
                         ["classification"], "INCONCLUSIVE")
        exact_source_error = (HEADER.format("negative_missing_reference_initialization") +
                              "verified/lib.rs(19,5): error: No matching heap chunks: "
                              "ref_initialized<i32>\n")
        self.assertEqual(classify_log("negative_missing_reference_initialization",
                                      exact_source_error, meta,
                                      {**EXEC, "stages": {**EXEC["stages"], "verifast": 1}})
                         ["classification"], "REGRESSION_MATCHED")

    def test_missing_precreation_is_admission_only_at_target(self):
        meta = {**BASE, "target_line": 22}
        log = ("verified/lib.rs(22,5): error: "
               "Taking the address of this expression is not supported\n")
        result = classify_log("negative_missing_precreated_reference", log, meta,
                              {**EXEC, "stages": {**EXEC["stages"], "verifast": 1}})
        self.assertEqual(result["classification"], "REGRESSION_MATCHED")
        self.assertEqual(result["gate_kind"], "ADMISSION_ONLY")
        wrong_path = log.replace("verified/lib.rs", "helper.rs")
        self.assertEqual(classify_log("negative_missing_precreated_reference", wrong_path,
                                      meta, {**EXEC, "stages": {**EXEC["stages"], "verifast": 1}})
                         ["classification"], "INCONCLUSIVE")

    def test_read_permission_requires_actual_read_not_prep_leak(self):
        meta = {**BASE, "target_line": 24, "read_line": 24}
        stages = {**EXEC["stages"], "verifast": 1}
        log = (HEADER.format("negative_read_without_permission") +
               "verified/lib.rs(24,5): Executing statement\n"
               "verified/lib.rs(24,5): error: No matching heap chunks: points_to<i32>\n")
        self.assertEqual(classify_log("negative_read_without_permission", log, meta,
                                      {**EXEC, "stages": stages})["classification"],
                         "REGRESSION_MATCHED")
        prep = log.replace("(24,5): error:", "(20,5): error:").replace(
            "Executing statement\n", "Executing statement\nLeak check.\n")
        self.assertEqual(classify_log("negative_read_without_permission", prep, meta,
                                      {**EXEC, "stages": stages})["classification"],
                         "INCONCLUSIVE")
        wrong_path = log.replace("verified/lib.rs(24,5): error:", "helper.rs(24,5): error:")
        self.assertEqual(classify_log("negative_read_without_permission", wrong_path, meta,
                                      {**EXEC, "stages": stages})["classification"],
                         "INCONCLUSIVE")


if __name__ == "__main__":
    unittest.main()
