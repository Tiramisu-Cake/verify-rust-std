#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Reclassify immutable hosted H_align artifacts into a separate output tree."""

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path


RUNS = {
    "37529855468": {
        "source": "17ad1f48b1eb97f806e03a97b7bf64b24f8ac50b",
        "zip_sha256": "f1ca30c7bc50125c09a901e9442ef2af8e596bc06e3dbd6c50bebb4e00ef663f",
        "expected": "parse-error-inconclusive",
    },
    "37532204465": {
        "source": "9474453f231eb600e1ec35d571c8ac4f70fa7138",
        "zip_sha256": "7ef6d71628a06b3c853cd165a3984669b1b4e1d4e1e282f87ec7998ce87411cd",
        "expected": "negative-detection",
    },
}
CASES = (
    "positive_generic_const", "positive_generic_mut", "positive_zst_layout",
    "positive_zst_add", "negative_source_byte_offset",
    "negative_destination_byte_offset",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_manifest(root):
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"unexpected symlink in archived evidence: {path}")
        if path.is_file():
            result[str(path.relative_to(root))] = digest(path)
    return result


def load_classifier(path):
    spec = importlib.util.spec_from_file_location("sort4_alignment_classifier", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def verify_case_integrity(case_dir):
    required = ("exporter", "decoder", "verifast", "refinement")
    before = json.loads((case_dir / "source-before-sha256.json").read_text())
    after = json.loads((case_dir / "source-after-sha256.json").read_text())
    if before != after or (case_dir / "source-unchanged.txt").read_text().strip() != "true":
        return False
    for stage in required:
        record = json.loads((case_dir / f"source-integrity-{stage}.json").read_text())
        if record.get("unchanged") is not True:
            return False
        if "before" in record and record.get("before") != record.get("after"):
            return False
    return True


def verify_archived_sources(case_dir, metadata):
    """Hash archived source files and bind them to extraction/stage manifests."""
    actual = {
        "original/lib.rs": digest(case_dir / "original/lib.rs"),
        "verified/lib.rs": digest(case_dir / "verified/lib.rs"),
    }
    expected = {
        "original/lib.rs": metadata.get("original_sha256"),
        "verified/lib.rs": metadata.get("verified_sha256"),
    }
    before = json.loads((case_dir / "source-before-sha256.json").read_text())
    after = json.loads((case_dir / "source-after-sha256.json").read_text())
    return actual == expected and before == actual and after == actual


def replay_one(classifier, evidence, run_id, spec):
    root = evidence / "verifast-sort4-alignment"
    environment = (root / "environment.txt").read_text(errors="replace")
    source_match = re.search(r"^Source commit: ([0-9a-f]{40})$", environment, re.M)
    if not source_match or source_match.group(1) != spec["source"]:
        raise ValueError(f"run {run_id}: artifact source SHA does not match pinned run SHA")
    extraction = json.loads((root / "cases/extraction.json").read_text())
    if tuple(extraction.get("case_order", ())) != CASES:
        raise ValueError(f"run {run_id}: archived extraction case order changed")
    original_aggregate = json.loads((root / "aggregate.json").read_text())
    per_case = {}
    for name in CASES:
        if name not in extraction.get("cases", {}):
            raise ValueError(f"run {run_id}: missing extraction metadata for {name}")
        case_dir = root / "cases" / name
        integrity = verify_case_integrity(case_dir) and verify_archived_sources(
            case_dir, extraction["cases"][name]
        )
        stages = {
            stage: int((case_dir / filename).read_text().strip())
            for stage, filename in (
                ("exporter", "exporter-exit-code.txt"),
                ("decode", "decode-exit-code.txt"),
                ("verifast", "verifast-exit-code.txt"),
                ("refinement", "refinement-exit-code.txt"),
            )
        }
        log = (case_dir / "verifast.log").read_text(errors="replace")
        unchanged = integrity
        result = classifier.classify_evidence(
            name, extraction["cases"][name], stages, log, unchanged
        )
        result["archived_classification"] = json.loads(
            (case_dir / "classification.json").read_text()
        ).get("classification")
        per_case[name] = result

    if spec["expected"] == "parse-error-inconclusive":
        if any(item["classification"] != "INCONCLUSIVE" for item in per_case.values()):
            raise ValueError(f"run {run_id}: original parse failures must remain INCONCLUSIVE")
    else:
        expected = {
            "positive_generic_const": "INCONCLUSIVE",
            "positive_generic_mut": "INCONCLUSIVE",
            "positive_zst_layout": "INCONCLUSIVE",
            "positive_zst_add": "INCONCLUSIVE",
            "negative_source_byte_offset": "EXPECTED_FALSE_POST_FAILURE",
            "negative_destination_byte_offset": "EXPECTED_FALSE_POST_FAILURE",
        }
        actual = {name: item["classification"] for name, item in per_case.items()}
        if actual != expected:
            raise ValueError(f"run {run_id}: reclassification mismatch: {actual}")
    # The old aggregate is read only and recorded by hash as a tamper check.
    aggregate_path = root / "aggregate.json"
    if not original_aggregate:
        raise ValueError(f"run {run_id}: archived original aggregate is empty")
    return {
        "run_id": run_id,
        "source_sha": spec["source"],
        "original_aggregate_sha256": digest(aggregate_path),
        "cases": per_case,
    }


def mutation_checks(classifier, evidence):
    """Exercise fail-closed name, reachability, location, text, stage and hash gates."""
    root = evidence / "verifast-sort4-alignment"
    extraction = json.loads((root / "cases/extraction.json").read_text())
    checked = []
    for name in ("negative_source_byte_offset", "negative_destination_byte_offset"):
        meta = extraction["cases"][name]
        case = root / "cases" / name
        stages = {key: int((case / file).read_text().strip()) for key, file in (
            ("exporter", "exporter-exit-code.txt"), ("decode", "decode-exit-code.txt"),
            ("verifast", "verifast-exit-code.txt"), ("refinement", "refinement-exit-code.txt"),
        )}
        log = (case / "verifast.log").read_text(errors="replace")
        if classifier.classify_evidence(name, meta, stages, log, True)["classification"] != "EXPECTED_FALSE_POST_FAILURE":
            raise ValueError(f"mutation baseline for {name} is not the intended negative")
        variants = []
        variants.append(("wrong-name", name + "_other", meta, stages, log, True))
        no_operation_records = "\n".join(
            line for line in log.splitlines()
            if not ((match := classifier.EXECUTION_RECORD.search(line)) and
                    int(match.group(1)) == meta["pointer_operation_line"])
        ) + "\n"
        variants.append(("missing-operation", name, meta, stages, no_operation_records, True))
        wrong_line = dict(meta, alignment_assertion_line=meta["alignment_assertion_line"] + 1)
        variants.append(("wrong-assertion-line", name, wrong_line, stages, log, True))
        variants.append(("wrong-assertion-text", name, dict(meta, alignment_assertion="//@ assert false;"), stages, log, True))
        variants.append(("wrong-error-expression", name, meta, stages, log.replace("Cannot prove %(", "Cannot prove forged%(", 1), True))
        failed_stages = dict(stages, refinement=1)
        variants.append(("failed-refinement", name, meta, failed_stages, log, True))
        variants.append(("source-integrity-failure", name, meta, stages, log, False))

        def mutate_header(transform):
            changed = []
            for entry in log.splitlines():
                match = classifier.TIMESTAMP_HEADER.search(entry)
                if match and match.group(2) == name:
                    changed.append(transform(entry))
                else:
                    changed.append(entry)
            return "\n".join(changed) + "\n"

        variants.append(("missing-target-header", name, meta, stages,
                          mutate_header(lambda _: ""), True))
        variants.append(("wrong-target-header-name", name, meta, stages,
                          mutate_header(lambda entry: entry.replace(name, "other_function")), True))
        target_headers = [entry for entry in log.splitlines()
                          if (match := classifier.TIMESTAMP_HEADER.search(entry)) and match.group(2) == name]
        if len(target_headers) != 1:
            raise ValueError(f"expected one authentic target header for mutation checks: {name}")
        variants.append(("duplicate-target-header", name, meta, stages,
                          log.replace(target_headers[0], target_headers[0] + "\n" + target_headers[0], 1), True))
        variants.append(("exporter-failure", name, meta, dict(stages, exporter=1), log, True))
        variants.append(("decoder-failure", name, meta, dict(stages, decode=1), log, True))
        parse_error = f"verified/lib.rs({meta['alignment_assertion_line']},1-2): error: Parse error."
        variants.append(("parse-error-before-assertion", name, meta, stages, parse_error, True))
        unrelated_error = "verified/lib.rs(1,1-2): error: unrelated assertion failure"
        variants.append(("unrelated-error", name, meta, stages,
                          log + "\n" + unrelated_error + "\n", True))
        variants.append(("earlier-error", name, meta, stages,
                          unrelated_error + "\n" + log, True))
        for label, case_name, case_meta, case_stages, case_log, intact in variants:
            classified = classifier.classify_evidence(
                case_name, case_meta, case_stages, case_log, intact
            )["classification"]
            if classified != "INCONCLUSIVE":
                raise ValueError(f"{name} fail-closed mutation {label} classified as {classified}")
            checked.append(f"{name}:{label}")
    return checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--classifier", type=Path, required=True)
    parser.add_argument("--run-metadata", action="append", required=True,
                        help="RUN_ID=path/to/GitHub run API JSON")
    parser.add_argument("--artifact-metadata", action="append", required=True,
                        help="ARTIFACT_ID=path/to/GitHub artifact API JSON")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    classifier = load_classifier(args.classifier)
    runs = {}
    artifacts = {}
    before = {}
    for item in args.run_metadata:
        run_id, path_text = item.split("=", 1)
        if run_id not in RUNS or run_id in runs:
            raise ValueError(f"unexpected or duplicate run id {run_id}")
        metadata = json.loads(Path(path_text).read_text())
        if metadata.get("id") != int(run_id) or metadata.get("head_sha") != RUNS[run_id]["source"]:
            raise ValueError(f"GitHub run metadata mismatch for {run_id}")
        runs[run_id] = metadata
    if set(runs) != set(RUNS):
        raise ValueError("both pinned historical runs must be supplied")
    expected_artifacts = {"11443817617": "37529855468", "11445280961": "37532204465"}
    for item in args.artifact_metadata:
        artifact_id, path_text = item.split("=", 1)
        if artifact_id not in expected_artifacts or artifact_id in artifacts:
            raise ValueError(f"unexpected or duplicate artifact id {artifact_id}")
        metadata = json.loads(Path(path_text).read_text())
        if metadata.get("id") != int(artifact_id) or metadata.get("expired") is not False:
            raise ValueError(f"artifact metadata mismatch/expired for {artifact_id}")
        workflow_run = metadata.get("workflow_run") or {}
        run_id = expected_artifacts[artifact_id]
        if workflow_run.get("id") != int(run_id) or workflow_run.get("head_sha") != RUNS[run_id]["source"]:
            raise ValueError(f"artifact-to-run metadata mismatch for {artifact_id}")
        artifacts[artifact_id] = metadata
    if set(artifacts) != set(expected_artifacts):
        raise ValueError("both pinned GitHub artifact metadata records must be supplied")

    output = {"runs": {}, "mutation_checks": []}
    for run_id in sorted(RUNS):
        evidence = args.evidence_root / run_id
        before[run_id] = tree_manifest(evidence)
        output["runs"][run_id] = replay_one(classifier, evidence, run_id, RUNS[run_id])
    output["mutation_checks"] = mutation_checks(
        classifier, args.evidence_root / "37532204465"
    )
    after = {run_id: tree_manifest(args.evidence_root / run_id) for run_id in sorted(RUNS)}
    if before != after:
        raise ValueError("archived input evidence changed during reclassification")
    output["input_tree_manifests_unchanged"] = True
    output["input_tree_manifests"] = {"before": before, "after": after}
    output["run_metadata_sha256"] = {
        run_id: digest(Path(path_text))
        for run_id, path_text in (item.split("=", 1) for item in args.run_metadata)
    }
    output["artifact_metadata_sha256"] = {
        artifact_id: digest(Path(path_text))
        for artifact_id, path_text in (item.split("=", 1) for item in args.artifact_metadata)
    }
    output["processor_sha256"] = {
        str(path): digest(path)
        for path in (
            args.classifier, Path(__file__),
            Path(__file__).with_name("test-sort4-alignment-classifier.py"),
            Path(__file__).with_name("run-sort4-alignment-replay.sh"),
        )
    }
    output["archive_sha256"] = {run_id: RUNS[run_id]["zip_sha256"] for run_id in sorted(RUNS)}
    output_path = args.output / "reclassification.json"
    output_path.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Saved separate replay result: {output_path}")
    for run_id, result in output["runs"].items():
        classes = {name: case["classification"] for name, case in result["cases"].items()}
        print(f"run {run_id}: {classes}")
    print(f"Fail-closed mutation checks: {len(output['mutation_checks'])} passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"replay failed closed: {exc}", file=sys.stderr)
        raise SystemExit(1)
