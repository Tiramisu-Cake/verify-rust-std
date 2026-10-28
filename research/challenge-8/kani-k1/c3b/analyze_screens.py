"""Check every final ordinary name against bounded k1g summary pages and Git-bound requests."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

BASE = Path(__file__).resolve().parent


def read_rows(path, entry):
    text = path.read_text()
    lines = text.splitlines()
    header = "name\tstatus\ttime_s\tchecks\tcovers"
    split = lines.index(header)
    fields = dict(line.split("=", 1) for line in lines[:split])
    if fields["build_id"] != entry["build_id"] or fields["head_sha"] != entry["sha"]:
        raise ValueError(f"{path.name}: build or source identity mismatch")
    request_bytes = subprocess.check_output(
        ["git", "show", entry["sha"] + ":research/challenge-8/kani-k1/RUN-REQUEST.json"],
        cwd=BASE.parents[3])
    if hashlib.sha256(request_bytes).hexdigest() != fields["request_sha256"]:
        raise ValueError(f"{path.name}: request SHA mismatch")
    request = json.loads(request_bytes)
    if request["request_id"] != fields["request_id"] or request.get("kani_jobs", 1) != 1:
        raise ValueError(f"{path.name}: wrong request or concurrency")
    if fields["offset"] != "0" or fields["next_offset"] != "done":
        raise ValueError(f"{path.name}: incomplete page")
    rows = []
    for line in lines[split + 1:]:
        name, status, time, checks, covers = line.split("\t")
        seconds = None if time in ("", "None") else float(time)
        if seconds is not None and (not math.isfinite(seconds) or seconds < 0):
            raise ValueError(f"{path.name}: invalid verification time")
        failed = None if not checks else int(checks.split("/")[0])
        satisfied = None if not covers else int(covers.split("/")[0])
        total_covers = None if not covers else int(covers.split("/")[1])
        rows.append(dict(name=name, status=status, time_s=seconds, checks=checks,
                         checks_failed=failed, covers=covers, covers_satisfied=satisfied,
                         covers_total=total_covers, build_id=entry["build_id"],
                         source_sha=entry["sha"], request_sha256=fields["request_sha256"]))
    requested = [item["name"] for item in request["harnesses"]]
    if (len(rows) != int(fields["count"]) or len(rows) != int(fields["total"])
            or sorted(row["name"] for row in rows) != sorted(requested)
            or len(requested) != len(set(requested))):
        raise ValueError(f"{path.name}: request/rows completeness failure")
    summary = path.with_name(path.name.replace(".rows.tsv", ".summary.md")).read_text()
    if not re.search(r"^# K-1 run `[^`]+`: COMPLETE$", summary, re.M):
        raise ValueError(f"{path.name}: run is not COMPLETE; cannot accept individual rows")
    return rows


def analyze(inventory, labels, limit):
    expected = inventory.read_text().splitlines()
    if not expected or len(expected) != len(set(expected)):
        raise ValueError("empty/duplicated ordinary inventory")
    registry = {entry["label"]: entry for entry in json.loads((BASE / "builds.json").read_text())}
    latest, pending, errors, superseded = {}, [], [], []
    for label in labels:
        if not re.fullmatch(r"(?:screen|repair)-[a-z0-9-]+", label):
            raise ValueError("only explicit final screen/repair labels may supply acceptance evidence")
        path = BASE / (label + ".rows.tsv")
        if not path.exists() or not path.stat().st_size:
            pending.append(label)
            continue
        try:
            rows = read_rows(path, registry[label])
        except (ValueError, KeyError) as error:
            errors.append(str(error))
            continue
        for row in rows:
            name = row["name"]
            if name in latest:
                superseded.append(dict(name=name, old_build=latest[name]["build_id"],
                                       new_build=row["build_id"]))
            latest[name] = row
    missing = sorted(set(expected) - set(latest))
    obsolete = sorted(set(latest) - set(expected))
    selected = [latest[name] for name in expected if name in latest]
    not_proved, over_budget = [], []
    for row in selected:
        passed = (row["status"] == "SUCCESS" and row["checks_failed"] == 0
                  and row["time_s"] is not None)
        if row["name"].endswith("::mutating_comparator_changes_both_keys"):
            passed = passed and row["covers_satisfied"] == row["covers_total"] == 1
        if not passed:
            not_proved.append(row)
        elif row["time_s"] > limit:
            over_budget.append(row)
    timed = [row for row in selected if row["time_s"] is not None]
    result = dict(inventory=str(inventory), inventory_count=len(expected), target_gcb_s=limit,
                  evidence_labels=labels, observed_names=len(selected), missing=missing,
                  obsolete=obsolete, pending=pending, binding_errors=errors,
                  not_proved=not_proved, over_budget=over_budget, superseded=superseded,
                  max_observed_s=max((row["time_s"] for row in timed), default=None),
                  sum_observed_s=sum(row["time_s"] for row in timed),
                  complete=not (missing or pending or errors or not_proved or over_budget), rows=selected)
    (BASE / "screen-analysis.json").write_text(json.dumps(result, indent=2) + "\n")
    with (BASE / "ordinary-timings.tsv").open("w") as stream:
        stream.write("name\tstatus\ttime_s\tchecks\tcovers\tbuild_id\tsource_sha\n")
        for row in selected:
            stream.write("\t".join(str(row[key]) for key in
                         ("name", "status", "time_s", "checks", "covers", "build_id", "source_sha")) + "\n")
    concise = {key: result[key] for key in
               ("inventory_count", "target_gcb_s", "observed_names", "pending", "binding_errors",
                "max_observed_s", "sum_observed_s", "complete")}
    concise.update(missing_count=len(missing), not_proved_count=len(not_proved),
                   over_budget_count=len(over_budget))
    print(json.dumps(concise, indent=2))
    for row in sorted(not_proved + over_budget,
                      key=lambda item: item["time_s"] or math.inf, reverse=True)[:20]:
        print(row["name"], row["status"], row["time_s"])
    return result["complete"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--limit", type=float, default=90)
    parser.add_argument("--labels", nargs="+", default=[f"screen-{i}of6" for i in range(1, 7)])
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    complete = analyze(args.inventory, args.labels, args.limit)
    if args.require_complete and not complete:
        raise SystemExit(1)
