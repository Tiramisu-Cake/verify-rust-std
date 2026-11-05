#!/usr/bin/env python3
"""Check captured bounded K-1 responses; no raw evidence or proof-tool invocation."""
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

PACKET = Path(__file__).resolve().parent
EVIDENCE = PACKET / "evidence"
BUILD = "f645e709-de9a-4b7a-a61f-69aab36f4f75"
SOURCE = "2ed6e9c7da48d61fd362a9f90401486ef25421bc"
KANI = "cd355b0bccd32300713bc2ce4f765dafa1510607"
PREFIX = "slice::sort::shared::smallsort::verify::looppin::"


def main():
    request_bytes = (PACKET / "request.json").read_bytes()
    request = json.loads(request_bytes)
    request_hash = hashlib.sha256(request_bytes).hexdigest()
    summary = (EVIDENCE / "summary.md").read_text()
    rows_text = (EVIDENCE / "rows.txt").read_text()
    status = json.loads((EVIDENCE / "status.json").read_text())
    assert status["id"] == BUILD and status["source_sha"] == SOURCE
    assert status["status"] == "SUCCESS" and status["timeout"] == "2520s"
    assert status["pool"].endswith("/workerPools/k1-standard4")
    assert all(value in summary for value in (BUILD, SOURCE, KANI, request_hash, request["request_id"]))
    assert "gate: True; expectation met: True" in summary
    assert "Kani exit 1" in summary and ": COMPLETE" in summary
    expected_headers = {
        "request_id": request["request_id"], "request_sha256": request_hash,
        "build_id": BUILD, "head_sha": SOURCE, "total": "4", "offset": "0",
        "count": "4", "next_offset": "done",
    }
    headers = dict(line.split("=", 1) for line in rows_text.splitlines()[:8])
    assert headers == expected_headers
    rows = {}
    for line in rows_text.splitlines()[9:]:
        name, outcome, seconds, checks, covers = line.split("\t")
        rows[name] = {"status": outcome, "time_s": seconds, "failed_total_checks": checks, "covers": covers}
    assert set(rows) == {h["name"] for h in request["harnesses"]}
    assert len(rows) == 4
    expected_covers = {"calibration_true": "3/3", "insert_tail_u64_tail1_to4_backing5": "4/4",
                       "outer_loop_u64_symbolic_len_backing5": "3/3"}
    for entry in request["harnesses"]:
        row = rows[entry["name"]]
        assert row["status"] == entry["expect"]
        assert Decimal(row["time_s"]) < 180
        short = entry["name"].removeprefix(PREFIX)
        if entry["expect"] == "SUCCESS":
            assert row["failed_total_checks"].startswith("0/")
            assert row["covers"] == expected_covers[short]
        else:
            assert row["failed_total_checks"] == "1/88"
    description = "Check invariant after step for loop " + PREFIX + "calibration_false_control.0"
    location = "/workspace/src/library/core/src/slice/sort/shared/smallsort/verify/looppin.rs:38"
    assert description + " @ " + location in summary
    assert len(re.findall(r"(?m)^- Check invariant after step", summary)) == 1
    tooling = (EVIDENCE / "tooling.txt").read_text().splitlines()
    assert len(tooling) == 8 and all(line.startswith("ok ") for line in tooling)
    assert "59893bff1fbb2af1a0c08862afd7e3bb87c19cdd" in tooling[1]
    peaks_text = (EVIDENCE / "peaks0.txt").read_text()
    assert "process_records=2 offset=0 count=2 next_offset=done" in peaks_text
    processes = [json.loads(line) for line in peaks_text.splitlines() if line.startswith("{")]
    assert len(processes) == 2
    for process in processes:
        assert process["build_id"] == BUILD and process["head_sha"] == SOURCE
        assert process["kani_commit"] == KANI
        assert process["attribution"] == process["metadata_resolution"] == "direct"
        assert process["harness"] == process["direct_harness"] == process["pretty_name"]
        assert process["harness"] in rows and process["cmd"] == "cbmc"
        rows[process["harness"]]["cbmc_peak_rss_kib"] = process["peak_kb"]
    for row in rows.values():
        row.setdefault("cbmc_peak_rss_kib", None)
    count, spent, reserved = (EVIDENCE / "cost.txt").read_text().split()
    assert count == "1" and Decimal(spent) == Decimal("0.1620") and Decimal(reserved) == 0
    report = {
        "verdict": "PASS_BOUNDED_DIAGNOSTIC", "build_id": BUILD, "source_sha": SOURCE,
        "kani_commit": KANI, "request_sha256": request_hash, "request_id": request["request_id"],
        "rows": rows, "negative_check": {"description": description, "location": location},
        "covers_satisfied": 10, "covers_total": 10, "unreachable_covers": 0,
        "tooling_bindings": "PASS", "cloud_status": "SUCCESS", "kani_exit": 1,
        "spent_usd": spent, "reserved_usd": reserved,
        "verification_time_sum_s": str(sum(Decimal(row["time_s"]) for row in rows.values())),
        "memory_limit": "15.63 GiB machine memory, swap off; samples every 2 seconds",
        "memory_limitations": "Calibration roots finished below the sampling interval; no per-root RSS record, not zero RSS.",
        "scope": "Fixed backing only; copied outer loop and matched local helper PFC. No arbitrary-length or generic proof credit.",
        "evidence_kind": "Validation of bounded K-1 responses, not an independent verifier execution.",
    }
    (EVIDENCE / "verification-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
