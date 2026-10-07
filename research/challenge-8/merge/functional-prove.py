#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hosted-only functional occurrence-ID proof for the pinned merge bodies."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GEOMETRY = HERE / "geometry.c"
GEOMETRY_SHA256 = "4594f159400bcfeeea87e3086e5765472d121dced7385bd2ef216a83bf24dea8"
FUNCTIONAL = HERE / "functional-ids.c"
GEOMETRY_HARNESS = HERE / "prove.py"
GEOMETRY_HARNESS_SHA256 = "32d009716b6b3dacc7f300ced0a1950a90ff0d8872253d7d63efe627a221774f"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def admitted_harness():
    if sha(GEOMETRY_HARNESS.read_bytes()) != GEOMETRY_HARNESS_SHA256:
        raise RuntimeError("accepted exact-source merge geometry harness changed")
    spec = importlib.util.spec_from_file_location("admitted_merge_geometry", GEOMETRY_HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load accepted merge geometry admission")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def negative_case(geometry: str, functional: str) -> tuple[str, dict]:
    geometry_definitions = geometry.split("lemma void mg_merge_up_access", 1)[0]
    functional_definitions = functional.split("lemma void fa_threshold_step", 1)[0]
    if geometry_definitions == geometry or functional_definitions == functional:
        raise RuntimeError("negative definitions boundary missing")
    source = geometry_definitions + "@*/\n" + functional_definitions + "@*/\n"
    source += """/*@
lemma void fa_negative_duplicate_without_guard()
    requires true;
    ensures true;
{
    list<pair<bool, bool> > decisions = cons(pair(true, false), nil);
    assert length(decisions) == 1;
    assert mg_guard_pass(1, 0, mg_end_a(decisions, 0),
                         mg_end_d(decisions, 0), false) == false;
    assert fa_output(1, 0, 0, 0, 0, decisions, false) == cons(0, cons(0, nil));
    assert fa_count(fa_output(1, 0, 0, 0, 0, decisions, false), 0) == 2;
    assert fa_count(fa_output(1, 0, 0, 0, 0, decisions, false), 1) == 0;
    assert fa_count(fa_output(1, 0, 0, 0, 0, decisions, false), 0) == 1; // TARGET_NEGATIVE_DUPLICATE
}
@*/
"""
    target = next(i for i, line in enumerate(source.splitlines(), 1)
                  if "TARGET_NEGATIVE_DUPLICATE" in line)
    return source, {
        "target_line": target,
        "expected_predicate": "fa_count(fa_output(1, 0, 0, 0, 0, cons(pair(boxed_bool(true), boxed_bool(false)), nil), false), 0) = 1",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()

    admitted = admitted_harness()
    frozen = admitted.frozen_classifier()
    frozen.require_hosted()
    certificate = admitted.admit_source()
    tool = (args.tool_home / "bin/verifast").resolve(strict=True)
    if not tool.is_file():
        raise RuntimeError("stock VeriFast console not found")
    geometry_bytes = GEOMETRY.read_bytes()
    if sha(geometry_bytes) != GEOMETRY_SHA256:
        raise RuntimeError("accepted G2 geometry proof changed")
    geometry = geometry_bytes.decode("utf-8")
    functional_bytes = FUNCTIONAL.read_bytes()
    functional = functional_bytes.decode("utf-8")
    if geometry.count("lemma void mg_entry(") != 1 or functional.count("lemma void fa_entry(") != 1:
        raise RuntimeError("required exported proof body missing or ambiguous")

    evidence = args.evidence.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    certificate_path = evidence / "source-admission.json"
    certificate_path.write_text(json.dumps(certificate, indent=2) + "\n")
    negative_source, negative_metadata = negative_case(geometry, functional)
    cases = [
        ("merge_functional_ids_full", geometry + "\n" + functional, None),
        ("merge_functional_ids_negative_duplicate", negative_source, negative_metadata),
    ]
    manifest = {
        "scope": "pure exact occurrence-ID merge schedule, conditional on only the final scalar guard; Rust transfer remains open",
        "domain": "n>=2, arbitrary independent pair decisions of length n/2, arbitrary odd residual choice",
        "posts": "full G2 access trace; natural output and chronological writes of length n; exactly one write at every destination; trace/output correspondence; arbitrary-ID multiplicity one in [0,n), zero outside",
        "tool_profile": "official-stock-VeriFast-26.09",
        "actual_source": str(admitted.SOURCE.relative_to(ROOT)),
        "source_admission_sha256": sha(certificate_path.read_bytes()),
        "source_admission": certificate,
        "geometry_sha256": GEOMETRY_SHA256,
        "functional_proof_sha256": sha(functional_bytes),
        "geometry_harness_sha256": GEOMETRY_HARNESS_SHA256,
        "frozen_classifier_sha256": admitted.FROZEN_SHA256,
        "verifast_binary_sha256": sha(tool.read_bytes()),
        "cases": [],
    }
    passed = True
    for name, source, expected in cases:
        result = frozen.run_case(tool, evidence, name, source, expected)
        result["boundary"] = (
            "checked pure exact occurrence-ID theorem with final scalar guard; "
            "Rust pointer/resources/FnMut/unwind and scalar-to-pointer guard transfer open"
        )
        manifest["cases"].append(result)
        (evidence / "results.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(f"{name}: {'PASS' if result['accepted'] else 'INCONCLUSIVE'}", flush=True)
        passed &= result["accepted"]
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"merge functional proof preparation failed: {error}", file=sys.stderr)
        sys.exit(2)
