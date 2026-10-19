#!/usr/bin/env python3
"""Synthetic service checks for r4 addressability receipt classification."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "r4-addressability-controls.py"
spec = importlib.util.spec_from_file_location("r4_addressability_controls_service", MODULE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("addressability controls module is unavailable")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def write_stage_receipts(case: Path, codes: dict[str, int], omit=()) -> None:
    for stage in omit:
        (case / f"{stage}-stage.json").unlink(missing_ok=True)
    for stage, code in codes.items():
        if stage in omit:
            continue
        source_hashes = {
            "original/lib.rs": runner._sha((case / "original/lib.rs").read_bytes()),
            "verified/lib.rs": runner._sha((case / "verified/lib.rs").read_bytes()),
        }
        (case / f"{stage}-stage.json").write_text(json.dumps({
            "stage": stage, "exit_code": code, "source_unchanged": True,
            "source_before": source_hashes, "source_after": source_hashes,
        }))


def execution(codes: dict[str, int]) -> dict:
    return {"stages": codes, "source_unchanged_at_every_stage": True}


with tempfile.TemporaryDirectory(prefix="r4-addressability-service-") as temp:
    root = Path(temp)
    metadata = runner.prepare(root / "suite")

    # Positive: final Rocq output from the actual verifier reports the target
    # local as address-taken, and the target statement, return, leak, and all
    # stage receipts are present. This test uses synthetic data only.
    positive = root / "suite/address_after_merge"
    positive_meta = metadata["address_after_merge"]
    (positive / "verified/lib.v").write_text(
        'LocalAddrTaken "local" true;;\n')
    positive_log = "".join(
        f"verified/lib.rs({line},1-2): Executing statement\n"
        for line in positive_meta["target_lines"])
    (positive / "verifast.log").write_text(
        positive_log + "Executing return statement\nLeak check.\n0 errors found\n")
    positive_codes = positive_meta["expected_stages"]
    write_stage_receipts(positive, positive_codes)
    positive_result = runner.classify("address_after_merge", positive,
                                      positive_meta, execution(positive_codes))
    assert positive_result["classification"] == "PASS_CONTROL"
    assert positive_result["rocq_final_local_flags"]["flags"] == {"local": [True]}

    # Intended negative: setup/refinement complete, the unique error is at the
    # declared assertion line and names the missing physical chunk.
    negative = root / "suite/missing_physical_owner"
    negative_meta = metadata["missing_physical_owner"]
    line = negative_meta["target_lines"][0]
    negative_codes = negative_meta["expected_stages"]
    write_stage_receipts(negative, negative_codes)
    (negative / "verifast.log").write_text(
        f"verified/lib.rs({line},5-8): error: No matching heap chunks: *anchor |-> _\n")
    negative_result = runner.classify("missing_physical_owner", negative,
                                      negative_meta, execution(negative_codes))
    assert negative_result["classification"] == "EXPECTED_REJECTION"

    # Setup errors, incomplete receipts, and absent artifacts stay inconclusive.
    failed_setup = dict(positive_codes, exporter=1)
    write_stage_receipts(positive, failed_setup)
    assert runner.classify("address_after_merge", positive, positive_meta,
                           execution(failed_setup))["classification"] == "INCONCLUSIVE"

    write_stage_receipts(positive, positive_codes, omit=("decode",))
    assert runner.classify("address_after_merge", positive, positive_meta,
                           execution(positive_codes))["classification"] == "INCONCLUSIVE"
    assert runner.classify("address_after_merge", positive, positive_meta,
                           {"stages": None})["classification"] == "INCONCLUSIVE"
    assert runner.classify("address_after_merge", positive, positive_meta,
                           None)["classification"] == "INCONCLUSIVE"

    absent = root / "suite/address_in_merge_assertion"
    absent_meta = metadata["address_in_merge_assertion"]
    absent_codes = absent_meta["expected_stages"]
    write_stage_receipts(absent, absent_codes)
    (absent / "verifast.log").write_text("Executing return statement\nLeak check.\n0 errors found\n")
    assert runner.classify("address_in_merge_assertion", absent, absent_meta,
                           execution(absent_codes))["classification"] == "INCONCLUSIVE"
    valid_receipt = {"profile": runner.PROFILE, "build_id": "build-r4",
                     "proof_sha": "a" * 40, "profile_sha256": "b" * 64,
                     "tool_commit": "c" * 40, "verify_expr_sha256": "d" * 64,
                     "accepted": False}
    assert runner._receipt_gate(SimpleNamespace(profile=runner.PROFILE),
                                valid_receipt)["build_id"] == "build-r4"
    for invalid in (None, [], {}, {**valid_receipt, "profile": "wrong"},
                    {**valid_receipt, "profile_sha256": "bad"},
                    {key: value for key, value in valid_receipt.items() if key != "tool_commit"},
                    {key: value for key, value in valid_receipt.items() if key != "accepted"},
                    {**valid_receipt, "accepted": True}):
        try:
            runner._receipt_gate(SimpleNamespace(profile=runner.PROFILE), invalid)
        except (TypeError, RuntimeError):
            pass
        else:
            raise AssertionError(f"invalid profile receipt was accepted: {invalid!r}")

    before_live = metadata["before_storage_live"]
    assert before_live["expected_class"] == "negative"
    before_live_source = (root / "suite/before_storage_live/verified/lib.rs").read_text()
    assert before_live_source.index("TARGET: ghost address precedes local StorageLive") < \
        before_live_source.index("let local = 31u64;")

    # A single case callback exception becomes a row and does not abort the
    # remaining isolated cases. The fake callback executes no tools.
    def synthetic_callback(case, args, env):
        if case.name == "address_before_merge":
            raise RuntimeError("synthetic callback failure")
        return None

    run_root = root / "run"
    run_args = SimpleNamespace(profile=runner.PROFILE)
    aggregate = runner.run(run_root, run_args, {}, synthetic_callback, valid_receipt)
    assert len(aggregate["cases"]) == len(runner.CASES)
    assert aggregate["cases"]["address_before_merge"] == "INCONCLUSIVE"
    assert aggregate["all_matched"] is False
    assert (run_root / "aggregate.json").is_file()

print("r4 addressability synthetic service checks: PASS")
