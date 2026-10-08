#!/usr/bin/env python3
"""Hosted diagnostic of the five S6 projection ghosts in actual 26.10 helper.

This reuses the source-certified constructor/as_mut_ptr/intrinsic/drop fixture
and frozen S6 projection admission. It never classifies the helper as proved.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LINK = load(REPO / "research/challenge-8/overnight-linkage/"
            "check-intrinsic-drop-linkage.py", "overnight_projection_link")
PREP = load(REPO / "research/challenge-8/prepare-select-pointer-actual.py",
            "overnight_projection_preparer")


def insert_exact_projection(source: bytes) -> bytes:
    insertions = (
        (b"    let false_ptr = false_val.as_mut_ptr();\n",
         PREP.PROJECTION_OPEN_GHOSTS),
        (b"        let guard = DropOnPanic { inner: guard };\n",
         PREP.PROJECTION_SPLIT_GHOST),
        (b"        drop.drop_in_place();\n",
         PREP.PROJECTION_CLOSE_GHOSTS),
    )
    for anchor, ghost in insertions:
        LINK.LINK.require(source.count(anchor) == 1,
                          "actual projection insertion anchor changed")
        source = source.replace(anchor, anchor + ghost, 1)
    return source


def main() -> None:
    LINK.LINK.require((os.environ.get("GITHUB_ACTIONS"),
                       os.environ.get("RUNNER_ENVIRONMENT"),
                       os.environ.get("RUNNER_OS")) ==
                      ("true", "github-hosted", "Linux"),
                      "actual projection diagnostic requires hosted Actions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--deadline-epoch", type=int, required=True)
    args = parser.parse_args()
    evidence = args.evidence.resolve()
    LINK.LINK.require(not evidence.exists(), "refusing to overwrite evidence")
    evidence.mkdir(parents=True)

    baseline_dir = evidence / "baseline-source"
    LINK.LINK.ACTUAL.write_fixture(REPO, baseline_dir)
    body, body_certificate = LINK.LINK.ACTUAL.source_certificate(REPO)
    constructor_certificate = LINK.CONSTRUCTOR.certify_repository_sources(REPO)
    asptr_adapter, asptr_certificate, _ = LINK.ASPTR_LINK.adapter_source(
        evidence, "positive", LINK.CONSTRUCTOR)
    drop_body, drop_certificate = LINK.DROP_SOURCE.source_certificate(
        REPO, LINK.CONSTRUCTOR)
    intrinsic_certificate = LINK.INTRINSIC.source_certificate(
        REPO, LINK.CONSTRUCTOR)
    baseline_verified = LINK.canonical_actual_contract(
        (baseline_dir / "verified/lib.rs").read_bytes())
    case = evidence / "projected-actual"
    fixture = LINK.make_case(baseline_verified, body,
                             constructor_certificate, asptr_adapter,
                             drop_body, case, "pointer_drop")
    verified_path = case / "verified/lib.rs"
    original_path = case / "original/lib.rs"
    unprojected = verified_path.read_bytes()
    verified = insert_exact_projection(unprojected)
    original = original_path.read_bytes()
    LINK.LINK.require(LINK.CONSTRUCTOR.strip_ghost_annotations(verified) == original,
                      "projected ghosts changed Rust runtime source")
    LINK.LINK.require(verified.count(PREP.PROJECTION_OPEN_GHOSTS) == 1 and
                      verified.count(PREP.PROJECTION_SPLIT_GHOST) == 1 and
                      verified.count(PREP.PROJECTION_CLOSE_GHOSTS) == 1,
                      "projection ghost sequence changed")
    verified_path.write_bytes(verified)
    fixture.update({
        "variant": "actual_select_pointer_drop_projection_26_10",
        "actual_body_byte_identical": False,
        "actual_runtime_body_ghost_stripped_identical": True,
        "original_sha256": LINK.LINK.sha(original),
        "verified_sha256": LINK.LINK.sha(verified),
        "unprojected_verified_sha256": LINK.LINK.sha(unprojected),
        "ghost_strip_identity": True,
        "exact_five_s6_projection_ghosts": True,
        "scope": "diagnostic prefix, not actual helper proof",
    })
    LINK.LINK.write_json(case / "fixture.json", fixture)
    stages = LINK.run_case(case, args, pointer_drop=True)
    result = LINK.classify(case, "pointer_drop", stages)
    log_path = case / "full-verification.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    record = {
        "classification": "DIAGNOSTIC_ONLY",
        "actual_helper_proved": False,
        "fixture": fixture,
        "std_source_certificates": {
            "actual": body_certificate, "constructor": constructor_certificate,
            "as_mut_ptr": asptr_certificate, "intrinsic": intrinsic_certificate,
            "pointer_drop": drop_certificate,
        },
        "stages": stages,
        "linkage_diagnostic": result,
        "full_projected_actual_mir_admitted":
            "SORT4-SELECT-INTRINSIC: full typed actual MIR graph accepted" in log,
        "pointer_drop_redirect_seen":
            "SORT4-POINTER-DROP: redirected typed external method 1" in log,
        "first_error": result.get("first_error"),
        "fatal": result.get("fatal"),
    }
    LINK.LINK.write_json(evidence / "summary.json", record)
    print(json.dumps({key: record[key] for key in
                      ("classification", "full_projected_actual_mir_admitted",
                       "pointer_drop_redirect_seen", "first_error", "fatal")},
                     sort_keys=True))


if __name__ == "__main__":
    main()
