"""Summarize saved, bounded K-1 interface output; never read raw evidence caches."""
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
kind = sys.argv[1]
assert kind in ("measurement", "diagnostic")
request_bytes = (ROOT / f"{kind}.request.json").read_bytes()
request = json.loads(request_bytes)
ledger = json.loads((ROOT / "builds.json").read_text())
build = next(b for b in ledger["submitted_builds"] if b["kind"] == kind)
page = (ROOT / f"{kind}.rows.txt").read_text()
header, tsv = page.split("name\tstatus\ttime_s\tchecks\tcovers\n", 1)
fields = dict(line.split("=", 1) for line in header.splitlines())
assert fields["request_id"] == request["request_id"]
assert fields["request_sha256"] == hashlib.sha256(request_bytes).hexdigest()
assert fields["build_id"] == build["build_uuid"]
assert fields["head_sha"] == build["source_sha"]
assert fields["offset"] == "0" and fields["next_offset"] == "done"
rows = list(csv.DictReader(io.StringIO(tsv), fieldnames=(
    "name", "status", "time_s", "checks", "covers"
), delimiter="\t"))
assert len(rows) == int(fields["total"]) == int(fields["count"]) == len(request["harnesses"])
assert [r["name"] for r in rows] == [h["name"] for h in request["harnesses"]]
peaks = (ROOT / f"{kind}.peaks.txt").read_text()
processes = [json.loads(line) for line in peaks.splitlines() if line.startswith("{")]
match = re.search(r"process_records=(\d+) offset=0 count=(\d+) next_offset=done", peaks)
assert match and int(match[1]) == int(match[2]) == len(processes)
for process in processes:
    assert process["build_id"] == build["build_uuid"]
    assert process["head_sha"] == build["source_sha"]
    assert process["kani_commit"] == "9461e07af7ec929f050aa4192f29363c9be07779"
    assert process["cmd"] == "cbmc" and process["attribution"] == "direct"
    assert process["direct_harness"] == process["harness"]
for row in rows:
    row["time_s"] = float(row["time_s"]) if row["time_s"] not in ("", "None") else None
    matches = [p for p in processes if p["harness"] == row["name"]]
    assert len(matches) <= 1
    process = matches[0] if matches else {}
    row["cbmc_peak_kib"] = process.get("peak_kb")
    row["cbmc_peak_gib"] = process["peak_kb"] / 1048576 if process else None
    row["pid"] = process.get("pid")
    row["first_s"], row["last_s"] = process.get("first_s"), process.get("last_s")
summary = (ROOT / f"{kind}.summary.md").read_text()
assert f"head `{build['source_sha']}`" in summary
assert f"run {build['build_uuid']} " in summary
assert "uninit checks off, controls cfg on" in summary
assert f"harnesses in parallel {request['kani_jobs']}" in summary
tooling = (ROOT / f"{kind}.tooling.txt").read_text()
assert "DIFF" not in tooling and "k1-standard4" in tooling
assert f"build commit {build['source_sha']} equal BASE {ledger['base_sha']}" in tooling
assert sum(line.startswith("ok ") for line in tooling.splitlines()) == 8
cost = (ROOT / f"{kind}.cost.txt").read_text().split()
assert cost[0] == "1" and float(cost[2]) == 0
gate = all(
    r["status"] == "SUCCESS" and r["checks"].startswith("0/") and r["covers"] == "1/1"
    and r["time_s"] is not None and r["time_s"] <= 600 and r["cbmc_peak_kib"]
    for r in rows
) and "gate: True; expectation met: True" in summary
overlap = max((sum(p["first_s"] <= t <= p["last_s"] for p in processes)
               for t in {p["first_s"] for p in processes}), default=0)


def number(pattern):
    match = re.search(pattern, peaks, re.M)
    return int(match[1]) if match else None


result = dict(
    build_uuid=build["build_uuid"], source_sha=build["source_sha"],
    request_id=request["request_id"], request_sha256=fields["request_sha256"],
    kind=kind, kani_jobs=request["kani_jobs"], gate=bool(gate),
    complete="`: COMPLETE" in summary, actual_cost_usd=cost[1], rows=rows,
    sum_verification_time_s=sum(r["time_s"] or 0 for r in rows),
    driver_peak_kib=number(r"^cmd=kani-driver peak_kb=(\d+)"),
    sampled_simultaneous_all_rss_peak_kib=number(r"^total_rss_peak_kb=(\d+)"),
    sampled_simultaneous_cbmc_rss_peak_kib=number(
        r"^role=cbmc simultaneous_rss_peak_kb=(\d+)"
    ),
    max_cbmc_overlap_from_observed_lifetimes=overlap,
    oom_scan=re.search(r"^dmesg_oom=(.*)$", peaks, re.M)[1],
    missing_names=[r["name"] for r in rows if r["status"] == "MISSING"],
    method="Kernel VmHWM, 2-second sampling; overlapping first_s/last_s lifetimes.",
    tooling_verified=True, macos="UNKNOWN",
)
(ROOT / f"{kind}.results.json").write_text(json.dumps(result, indent=2) + "\n")
print(f"{kind}: gate={bool(gate)}, overlap={overlap}, cost=${cost[1]}")
for row in rows:
    print(row["name"].split("::merge::")[1], row["status"], row["time_s"],
          row["cbmc_peak_gib"], row["covers"], row["checks"])
