#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted regression checks against the two immutable saved H_align runs."""

import argparse
import importlib.util
import json
import unittest
from pathlib import Path
import sys


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class SavedEvidenceClassifierTests(unittest.TestCase):
    def read_run(self, run_id):
        root = self.evidence_root / run_id / "verifast-sort4-alignment"
        extraction = json.loads((root / "cases/extraction.json").read_text())
        outcomes = {}
        for name in self.replay.CASES:
            case = root / "cases" / name
            stage_names = (
                ("exporter", "exporter-exit-code.txt"),
                ("decode", "decode-exit-code.txt"),
                ("verifast", "verifast-exit-code.txt"),
                ("refinement", "refinement-exit-code.txt"),
            )
            stages = {key: int((case / filename).read_text().strip())
                      for key, filename in stage_names}
            outcomes[name] = self.classifier.classify_evidence(
                name, extraction["cases"][name], stages,
                (case / "verifast.log").read_text(errors="replace"),
                self.replay.verify_case_integrity(case) and
                self.replay.verify_archived_sources(case, extraction["cases"][name]),
            )["classification"]
        return outcomes

    def test_original_parse_errors_remain_inconclusive(self):
        self.assertEqual(set(self.read_run("37529855468").values()), {"INCONCLUSIVE"})

    def test_new_intended_alignment_assertions_are_detected(self):
        result = self.read_run("37532204465")
        self.assertEqual(result["positive_generic_const"], "INCONCLUSIVE")
        self.assertEqual(result["positive_generic_mut"], "INCONCLUSIVE")
        self.assertEqual(result["positive_zst_layout"], "INCONCLUSIVE")
        self.assertEqual(result["positive_zst_add"], "INCONCLUSIVE")
        self.assertEqual(result["negative_source_byte_offset"], "EXPECTED_FALSE_POST_FAILURE")
        self.assertEqual(result["negative_destination_byte_offset"], "EXPECTED_FALSE_POST_FAILURE")

    def test_fail_closed_mutations(self):
        checks = self.replay.mutation_checks(
            self.classifier, self.evidence_root / "37532204465"
        )
        self.assertEqual(len(checks), 30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--classifier", type=Path, required=True)
    parser.add_argument("--replay", type=Path, required=True)
    arguments = parser.parse_args()
    SavedEvidenceClassifierTests.evidence_root = arguments.evidence_root
    SavedEvidenceClassifierTests.classifier = load_module(
        "sort4_alignment_classifier", arguments.classifier
    )
    SavedEvidenceClassifierTests.replay = load_module("sort4_alignment_replay", arguments.replay)
    unittest.main(argv=[sys.argv[0]])
