#!/usr/bin/env python3
"""Run-request validation and bounded result summary for the Kani K-1 experiment lane.

Subcommands
  validate REQUEST --args-out FILE [--runner-out FILE]   check the request, write one Kani argument per line
  summarize --request R --log L ...                      parse terse Kani output into summary.json/summary.md
  gate SUMMARY                                           exit 0 iff the run is COMPLETE, consistent and met
                                                         every expectation (and, for measurement, every bound)
  sample-mem --out FILE                                  record per-command peak RSS until SIGTERM (resource lane)
  ledger                                                 Cloud Build list JSON on stdin -> "builds used reserved" minutes

Standard library only. No network, no proof tools. The summary is the agent-facing evidence:
statuses, times, failed checks and errors are bounded and every truncation is explicit. Anything the
parser cannot reconcile becomes an explicit non-COMPLETE status, never a silent pass.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "kani-k1-run-request-v1"
SUMMARY_SCHEMA = "kani-k1-run-summary-v2"
AGENTS = {"k1-merge", "k1-network", "coordinator"}
KINDS = {"measurement", "diagnostic", "resource"}
EXPECT = {"SUCCESS", "FAILED"}
# circleci-linux-large: CircleCI Linux VM large, 4 CPU / 15 GB (the active lane); the two GitHub runners
# are kept for the dormant GitHub Actions lane. gcb-e2-highmem-4: Cloud Build private pool, 4 vCPU / 32 GB,
# twice the organizers' runner memory, so it takes only kind "resource", which never counts for PASS.
RESOURCE_RUNNER = "gcb-e2-highmem-4"
RUNNERS = {"circleci-linux-large", "ubuntu-latest", "macos-latest", RESOURCE_RUNNER}
HARNESS_PREFIX = "slice::sort::shared::smallsort::kani_k1::"
HARNESS_RE = re.compile(r"slice::sort::shared::smallsort::kani_k1::[A-Za-z0-9_]+(::[A-Za-z0-9_]+)*")
REQUEST_ID_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
REQUEST_KEYS = {"schema", "request_id", "agent", "kind", "purpose", "runner", "harness_timeout_minutes", "harnesses"}
HARNESS_REQUIRED = {"name", "expect"}
HARNESS_OPTIONAL = {"expect_check"}
MAX_HARNESSES = 20
MAX_TIMEOUT_MINUTES = 30
RESOURCE_MAX_TIMEOUT_MINUTES = 720
MEASUREMENT_TIMEOUT_MINUTES = 10
MAX_TOTAL_MINUTES = 150
MEASUREMENT_LIMIT_SECONDS = 600.0

MAX_FAILED_CHECKS = 20
MAX_LINE_CHARS = 400
MAX_ERROR_LINES = 80
MAX_MD_BYTES = 12000

CHECKING_RE = re.compile(r"^(?:Thread \d+: )?Checking harness (\S+?)\.\.\.\s*$")
STATUS_RE = re.compile(r"^VERIFICATION:-\s*(SUCCESSFUL|FAILED|TIMEOUT)\b(.*)$")
TIME_RE = re.compile(r"^Verification Time:\s*([0-9]+(?:\.[0-9]+)?)s\s*$")
CHECKS_RE = re.compile(r"^\s*\*\*\s*(\d+) of (\d+) failed(.*)$")
UNREACHABLE_RE = re.compile(r"(\d+) unreachable")
COVER_RE = re.compile(r"^\s*\*\*\s*(\d+) of (\d+) cover properties satisfied")
FAILED_CHECK_RE = re.compile(r"^Failed Checks:\s*(.*)$")
FILE_RE = re.compile(r'^\s*File: "([^"]+)", line (\d+)')
COMPLETE_RE = re.compile(r"^Complete - (\d+) successfully verified harness(?:es)?, (\d+) failures?, (\d+) total\.")
SUMMARY_HEADER_RE = re.compile(r"^Summary:\s*$")
# Kani prints this line when CBMC exceeds --harness-timeout. A mismatch only loses TIMEOUT labelling:
# such a harness is FAILED without a located check, which never meets SUCCESS or FAILED expectations.
TIMEOUT_RE = re.compile(r"^CBMC timed out\b")
# Kani prints this line when CBMC was killed by SIGKILL, which in this lane is the verify cgroup's OOM killer.
OOM_RE = re.compile(r"^CBMC appears to have run out of memory\b")
ERROR_RE = re.compile(r"^error(\[E\d{4}\])?:")
RUSTC_ERROR_RE = re.compile(r"^error\[E\d{4}\]:|could not compile")
RSS_RE = re.compile(r"Maximum resident set size \(kbytes\):\s*(\d+)")
WALL_RE = re.compile(r"Elapsed \(wall clock\) time \(h:mm:ss or m:ss\):\s*([0-9:.]+)")
# BSD /usr/bin/time -l on macOS: RSS in bytes, wall as "<seconds> real".
MAC_RSS_RE = re.compile(r"^\s*(\d+)\s+maximum resident set size", re.M)
MAC_REAL_RE = re.compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s+real\b", re.M)


class RequestError(ValueError):
    pass


def _clip(text: str) -> str:
    text = text.rstrip("\n")
    return text if len(text) <= MAX_LINE_CHARS else text[:MAX_LINE_CHARS] + " …[clipped]"


def _one_line(value: Any, limit: int) -> bool:
    return isinstance(value, str) and bool(value.strip()) and len(value) <= limit and "\n" not in value and "\r" not in value


def validate_request(data: Any, max_total_minutes: int | None = None) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise RequestError("request must be a JSON object")
    extra, missing = set(data) - REQUEST_KEYS, REQUEST_KEYS - set(data)
    if extra:
        raise RequestError(f"unknown request keys: {sorted(extra)}")
    if missing:
        raise RequestError(f"missing request keys: {sorted(missing)}")
    if data["schema"] != SCHEMA:
        raise RequestError(f"schema must be {SCHEMA}")
    if not isinstance(data["request_id"], str) or not REQUEST_ID_RE.fullmatch(data["request_id"]):
        raise RequestError("request_id must match [a-z0-9][a-z0-9._-]{0,63}")
    for key, allowed in (("agent", AGENTS), ("kind", KINDS), ("runner", RUNNERS)):
        if not isinstance(data[key], str) or data[key] not in allowed:
            raise RequestError(f"{key} must be one of {sorted(allowed)}")
    if not _one_line(data["purpose"], 300):
        raise RequestError("purpose must be one non-empty line of at most 300 characters")
    if (data["runner"] == RESOURCE_RUNNER) != (data["kind"] == "resource"):
        raise RequestError(f"kind resource runs exactly on runner {RESOURCE_RUNNER}, and that runner takes only kind resource")
    timeout = data["harness_timeout_minutes"]
    limit = RESOURCE_MAX_TIMEOUT_MINUTES if data["kind"] == "resource" else MAX_TIMEOUT_MINUTES
    if type(timeout) is not int or not 1 <= timeout <= limit:
        raise RequestError(f"harness_timeout_minutes must be an integer 1..{limit} for kind {data['kind']}")
    if data["kind"] == "measurement" and timeout != MEASUREMENT_TIMEOUT_MINUTES:
        raise RequestError("a measurement run must use harness_timeout_minutes = 10")
    harnesses = data["harnesses"]
    if not isinstance(harnesses, list) or not 1 <= len(harnesses) <= MAX_HARNESSES:
        raise RequestError(f"harnesses must be a list of 1..{MAX_HARNESSES} entries")
    names: list[str] = []
    for entry in harnesses:
        if (not isinstance(entry, dict) or not HARNESS_REQUIRED <= set(entry)
                or set(entry) - HARNESS_REQUIRED - HARNESS_OPTIONAL):
            raise RequestError("each harness entry must be {name, expect} plus expect_check for expect FAILED")
        name, expect = entry["name"], entry["expect"]
        if not isinstance(name, str) or not HARNESS_RE.fullmatch(name):
            raise RequestError(f"harness name must be a full path under {HARNESS_PREFIX}: {name!r}")
        if not isinstance(expect, str) or expect not in EXPECT:
            raise RequestError(f"expect must be SUCCESS or FAILED: {name}")
        # A FAILED expectation must name the intended check, else an unrelated failure would count.
        if expect == "FAILED" and not _one_line(entry.get("expect_check"), 200):
            raise RequestError(f"expect FAILED requires expect_check, a one-line substring of the intended check: {name}")
        if expect == "SUCCESS" and "expect_check" in entry:
            raise RequestError(f"expect_check is only for expect FAILED: {name}")
        names.append(name)
    if len(set(names)) != len(names):
        raise RequestError("duplicate harness names")
    # The lane's own cap applies when the caller gives none (e.g. summarize). For resource runs the dispatcher
    # sizes the paid Cloud Build timeout from this total (k1g.sh), so it is capped here in any case.
    if data["kind"] == "resource":
        cap = RESOURCE_MAX_TIMEOUT_MINUTES
        max_total_minutes = cap if max_total_minutes is None else min(max_total_minutes, cap)
    elif max_total_minutes is None:
        max_total_minutes = MAX_TOTAL_MINUTES
    if len(names) * timeout > max_total_minutes:
        raise RequestError(f"harness count × timeout exceeds {max_total_minutes} minutes for this lane")
    return data


def kani_args(request: dict[str, Any]) -> list[str]:
    args: list[str] = []
    for entry in request["harnesses"]:
        args += ["--harness", entry["name"]]
    args += ["--exact", "--harness-timeout", f"{request['harness_timeout_minutes']}m",
             "--jobs=1", "--output-format=terse"]
    return args


def _new_block(name: str) -> dict[str, Any]:
    return {"name": name, "status_line": None, "time_s": None, "checks_failed": None, "checks_total": None,
            "unreachable": None, "covers_satisfied": None, "covers_total": None, "failed_checks": [],
            "failed_located": 0, "failed_checks_truncated": False, "timed_out": False, "out_of_memory": False}


def parse_log(text: str) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    errors: list[str] = []
    errors_truncated = False
    complete = None
    error_context = 0
    for raw in text.splitlines():
        line = raw.rstrip("\r")
        m = CHECKING_RE.match(line)
        if m:
            current = _new_block(m.group(1))
            blocks.append(current)
            error_context = 0
            continue
        if ERROR_RE.match(line):
            error_context = 8
        if error_context:
            if len(errors) < MAX_ERROR_LINES:
                errors.append(_clip(line))
            else:
                errors_truncated = True
            error_context -= 1
        m = COMPLETE_RE.match(line)
        if m:
            complete = {"success": int(m.group(1)), "failures": int(m.group(2)), "total": int(m.group(3))}
            current = None
            continue
        if SUMMARY_HEADER_RE.match(line):
            current = None
            continue
        if current is None:
            continue
        if TIMEOUT_RE.match(line):
            current["timed_out"] = True
            continue
        if OOM_RE.match(line):
            current["out_of_memory"] = True
            continue
        m = STATUS_RE.match(line)
        if m:
            current["status_line"] = m.group(1)
            continue
        m = TIME_RE.match(line)
        if m:
            current["time_s"] = float(m.group(1))
            current = None  # a harness block ends with its verification time
            continue
        m = CHECKS_RE.match(line)
        if m:
            current["checks_failed"], current["checks_total"] = int(m.group(1)), int(m.group(2))
            rest = m.group(3).strip()
            found = UNREACHABLE_RE.search(rest)
            # No suffix: no unreachable checks. A suffix without a readable count stays unknown (None).
            current["unreachable"] = int(found.group(1)) if found else (0 if not rest else None)
            continue
        m = COVER_RE.match(line)
        if m:
            current["covers_satisfied"], current["covers_total"] = int(m.group(1)), int(m.group(2))
            continue
        m = FAILED_CHECK_RE.match(line)
        if m:
            if len(current["failed_checks"]) < MAX_FAILED_CHECKS:
                current["failed_checks"].append({"description": _clip(m.group(1)), "location": None})
                current["_last_open"] = True
            else:
                current["failed_checks_truncated"] = True
                current["_last_open"] = False
            continue
        m = FILE_RE.match(line)
        if m and current.get("_last_open"):
            current["failed_checks"][-1]["location"] = _clip(f"{m.group(1)}:{m.group(2)}")
            current["failed_located"] += 1
            current["_last_open"] = False
    for block in blocks:
        block.pop("_last_open", None)
    return {"blocks": blocks, "errors": errors, "errors_truncated": errors_truncated, "complete_line": complete}


def _block_status(block: dict[str, Any]) -> str:
    if block["out_of_memory"]:
        return "OUT_OF_MEMORY"
    if block["timed_out"] or block["status_line"] == "TIMEOUT":
        return "TIMEOUT"
    if block["status_line"] == "SUCCESSFUL":
        return "SUCCESS"
    if block["status_line"] == "FAILED":
        return "FAILED"
    return "UNKNOWN"


def _row_meets(row: dict[str, Any], entry: dict[str, Any]) -> bool:
    if entry["expect"] == "SUCCESS":
        return row["status"] == "SUCCESS"
    if row["status"] != "FAILED" or not row.get("failed_located"):
        return False
    needle = entry["expect_check"]
    # Only descriptions of located checks count; the file path is not searched.
    return any(c["location"] is not None and needle in c["description"] for c in row.get("failed_checks", []))


def parse_time_file(text: str | None) -> dict[str, Any]:
    if text is None:
        return {"max_rss_kb_whole_run": None, "wall_whole_run": None, "time_file": "MISSING"}
    rss, wall = RSS_RE.search(text), WALL_RE.search(text)
    if rss or wall:
        return {"max_rss_kb_whole_run": int(rss.group(1)) if rss else None,
                "wall_whole_run": wall.group(1) if wall else None, "time_file": "PARSED"}
    rss, real = MAC_RSS_RE.search(text), MAC_REAL_RE.search(text)
    if rss or real:
        return {"max_rss_kb_whole_run": int(rss.group(1)) // 1024 if rss else None,
                "wall_whole_run": f"{real.group(1)}s" if real else None, "time_file": "PARSED"}
    return {"max_rss_kb_whole_run": None, "wall_whole_run": None, "time_file": "UNPARSED"}


def parse_memcap(text: str | None) -> dict[str, Any]:
    """k1-out/memcap.txt of the verify step: key=value lines written by circleci-k1.sh."""
    if text is None:
        return {"state": "MISSING", "max_bytes": None, "peak_bytes": None, "oom_kill": None, "swap": None, "reason": None}
    fields = dict(line.split("=", 1) for line in text.splitlines() if "=" in line)

    def num(key: str) -> int | None:
        value = fields.get(key, "").strip()
        return int(value) if value.isdigit() else None
    state = fields.get("state", "").strip()
    return {"state": state if state in ("ENFORCED", "UNAVAILABLE") else "UNPARSED", "max_bytes": num("max_bytes"),
            "peak_bytes": num("peak_bytes"), "oom_kill": num("oom_kill"),
            "swap": fields.get("swap", "").strip() or None,
            "reason": _clip(fields["reason"].strip()) if fields.get("reason") else None}


PEAKS_TOP = 12


def parse_peaks(text: str | None) -> dict[str, Any]:
    """k1-out/peaks.txt of sample-mem: key=value header lines and one `cmd=NAME peak_kb=… first_s=… last_s=…` per command."""
    if text is None:
        return {"state": "MISSING", "interval_ms": None, "samples": None, "total_rss_peak_kb": None, "commands": []}
    head: dict[str, str] = {}
    commands: list[dict[str, Any]] = []
    for line in text.splitlines():
        if line.startswith("cmd="):
            f = dict(part.split("=", 1) for part in line.split() if "=" in part)
            if all(f.get(k, "").isdigit() for k in ("peak_kb", "first_s", "last_s")):
                commands.append({"cmd": _clip(f["cmd"])[:40], "peak_kb": int(f["peak_kb"]),
                                 "first_s": int(f["first_s"]), "last_s": int(f["last_s"])})
        elif "=" in line:
            key, value = line.split("=", 1)
            head[key.strip()] = value.strip()

    def num(key: str) -> int | None:
        return int(head[key]) if head.get(key, "").isdigit() else None
    commands.sort(key=lambda c: -c["peak_kb"])
    samples = num("samples")
    return {"state": "PARSED" if samples else "UNPARSED", "interval_ms": num("interval_ms"), "samples": samples,
            "total_rss_peak_kb": num("total_rss_peak_kb"), "commands": commands[:PEAKS_TOP],
            "commands_truncated": len(commands) > PEAKS_TOP}


def _proc_status(path: Path) -> dict[str, str] | None:
    try:
        text = path.read_text()
    except OSError:
        return None
    return dict(line.split(":", 1) for line in text.splitlines() if ":" in line)


def _kb(value: str | None) -> int:
    parts = (value or "").split()
    return int(parts[0]) if parts and parts[0].isdigit() else 0


def sample_memory(out: Path, interval: float, max_seconds: float | None = None, proc: Path = Path("/proc")) -> None:
    """Every INTERVAL seconds read VmHWM (the kernel's per-process peak RSS) of every process and keep the
    maximum per command name, plus the largest sampled sum of VmRSS. The file is rewritten atomically after
    each sample, so a killed sampler still leaves the last state. Stops on SIGTERM/SIGINT or after MAX_SECONDS."""
    stop = False

    def on_signal(signum: int, frame: Any) -> None:
        nonlocal stop
        stop = True
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    t0 = time.monotonic()
    peaks: dict[str, dict[str, int]] = {}
    total_peak = samples = 0
    me = str(os.getpid())
    while True:
        now = int(time.monotonic() - t0)
        total = 0
        for status_path in proc.glob("[0-9]*/status"):
            if status_path.parent.name == me:
                continue
            st = _proc_status(status_path)
            if not st or "VmRSS" not in st:
                continue  # kernel thread or gone
            total += _kb(st.get("VmRSS"))
            name = re.sub(r"[^A-Za-z0-9._+-]", "_", st.get("Name", "?").strip())[:40] or "?"
            entry = peaks.setdefault(name, {"peak_kb": 0, "first_s": now, "last_s": now})
            entry["peak_kb"] = max(entry["peak_kb"], _kb(st.get("VmHWM")), _kb(st.get("VmRSS")))
            entry["last_s"] = now
        total_peak, samples = max(total_peak, total), samples + 1
        lines = [f"interval_ms={round(interval * 1000)}", f"samples={samples}", f"elapsed_s={now}", f"total_rss_peak_kb={total_peak}"]
        lines += [f"cmd={n} peak_kb={e['peak_kb']} first_s={e['first_s']} last_s={e['last_s']}" for n, e in sorted(peaks.items())]
        tmp = out.with_name(out.name + ".tmp")
        tmp.write_text("\n".join(lines) + "\n")
        tmp.replace(out)
        if stop or (max_seconds is not None and time.monotonic() - t0 >= max_seconds):
            return
        deadline = time.monotonic() + interval
        while not stop and time.monotonic() < deadline:
            time.sleep(min(0.2, interval))


def ledger(builds: Any) -> tuple[int, int, int]:
    """Pool minutes of a `gcloud builds list --format=json` result: (builds, used, reserved). A finished build
    counts start..finish rounded up (none if it never started); an unfinished one, queued or running, reserves
    its full timeout. Anything unreadable raises, so that dispatch fails closed."""
    def ts(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(builds, list):
        raise ValueError("build list must be a JSON array")
    used = reserved = 0
    for b in builds:
        if b.get("finishTime"):
            if b.get("startTime"):
                used += math.ceil((ts(b["finishTime"]) - ts(b["startTime"])).total_seconds() / 60)
            continue
        timeout = b.get("timeout")
        if not isinstance(timeout, str) or not re.fullmatch(r"\d+(\.\d+)?s", timeout):
            raise ValueError(f"unfinished build {b.get('id')} has unreadable timeout {timeout!r}")
        reserved += math.ceil(float(timeout[:-1]) / 60)
    return len(builds), used, reserved


def file_bindings(paths: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in paths:
        path = Path(p)
        out[p] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "MISSING"
    return out


def summarize(request_text: str | None, log_text: str | None, time_text: str | None, exit_code: int | None,
              head_sha: str | None, kani_commit: str | None, request_error: str | None = None,
              run: dict[str, Any] | None = None, tooling: dict[str, str] | None = None,
              build_outcome: str | None = None, memcap_text: str | None = None,
              memcap_tracked: bool = False, peaks_text: str | None = None,
              peaks_tracked: bool = False) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "schema": SUMMARY_SCHEMA, "head_sha": head_sha, "kani_commit": kani_commit, "run": run or {},
        "tooling_sha256": tooling or {}, "build_outcome": build_outcome,
        "request_sha256": hashlib.sha256(request_text.encode()).hexdigest() if request_text is not None else None,
        "kani_exit_code": exit_code, "request": None, "status": None, "expectation_met": False,
        "measurement_ok": None, "harnesses": [], "unrequested_blocks": [], "errors": [],
        "errors_truncated": False, "complete_line": None, "inconsistencies": [],
        "resources": parse_time_file(time_text), "notes": [],
    }
    # The memory cap is tracked only where the lane sets one (CircleCI); it then bounds measurement runs.
    memcap = parse_memcap(memcap_text) if memcap_tracked else None
    summary["resources"]["memcap"] = memcap
    # Per-command peaks are tracked only where the lane samples them (the 32 GB resource lane).
    peaks = parse_peaks(peaks_text) if peaks_tracked else None
    summary["resources"]["peaks"] = peaks
    if peaks is not None and peaks["state"] != "PARSED":
        summary["notes"].append(f"per-command memory peaks {peaks['state']}")
    if peaks is not None and peaks["commands"] and summary["resources"]["max_rss_kb_whole_run"]:
        top, exact = peaks["commands"][0]["peak_kb"], summary["resources"]["max_rss_kb_whole_run"]
        if exact > top:
            # The sampler misses growth in a process's last interval; time -v sees the largest child exactly.
            summary["notes"].append(f"time -v max RSS {exact} KiB exceeds the largest sampled command peak {top} KiB: "
                                    "a process grew between samples; use the time -v value as the true single-process peak")
    if memcap is not None:
        if memcap["state"] != "ENFORCED":
            summary["notes"].append(f"verify memory cap {memcap['state']}: {memcap['reason'] or 'no reason recorded'}")
        if memcap["oom_kill"]:
            summary["notes"].append(f"verify cgroup OOM killer fired {memcap['oom_kill']} time(s)")
        if memcap["state"] == "ENFORCED" and memcap["swap"] != "off":
            summary["notes"].append(f"swap not confirmed off in the verify cgroup: {memcap['swap']}")
    request = None
    if request_error is None and request_text is not None:
        try:
            request = validate_request(json.loads(request_text))
        except (RequestError, json.JSONDecodeError) as exc:
            request_error = str(exc)
    elif request_text is None and request_error is None:
        request_error = "request file missing"
    if request is None:
        summary["status"] = "REQUEST_INVALID"
        summary["notes"].append(f"request rejected before Kani ran: {_clip(request_error or 'unknown')}")
        return summary
    summary["request"] = {k: request[k] for k in ("request_id", "agent", "kind", "purpose", "runner", "harness_timeout_minutes")}
    if request["kind"] == "resource":
        summary["notes"].append("kind resource on 32 GB: memory/time data only, never a PASS or measurement result")
    not_run = [{"name": e["name"], "expect": e["expect"], "status": "NOT_RUN"} for e in request["harnesses"]]
    if log_text is None:
        summary["status"] = "RUNNER_ERROR"
        summary["harnesses"] = not_run
        reason = {"failure": "the pinned Kani build failed",
                  "deps-failure": "installing dependencies failed",
                  "not-started": "the job failed before request validation (checkout or submodules)",
                  "verify-skipped": "verification not started: too little time left before the lane's job cap"}.get(
                      build_outcome, "setup or runner failed before verification output")
        summary["notes"].append("Kani log missing: " + reason)
        return summary
    parsed = parse_log(log_text)
    summary["errors"], summary["errors_truncated"] = parsed["errors"], parsed["errors_truncated"]
    summary["complete_line"] = parsed["complete_line"]
    if not parsed["blocks"]:
        summary["harnesses"] = not_run
        if memcap is not None and memcap["oom_kill"]:
            summary["status"] = "RUNNER_ERROR"
            summary["notes"].append("OOM kill before any harness output: out of memory during compilation or goto instrumentation")
        elif any(RUSTC_ERROR_RE.search(line) for line in parsed["errors"]):
            summary["status"] = "COMPILE_ERROR"
        elif parsed["errors"]:
            summary["status"] = "TOOL_ERROR"
        else:
            summary["status"] = "RUNNER_ERROR"
            summary["notes"].append(f"no harness output and no error lines; Kani exit {exit_code}")
        return summary
    by_name: dict[str, dict[str, Any]] = {}
    inconsistencies = summary["inconsistencies"]
    for block in parsed["blocks"]:
        if block["name"] in by_name:
            inconsistencies.append(f"harness reported more than once: {block['name']}")
        by_name[block["name"]] = block
    requested = {e["name"] for e in request["harnesses"]}
    summary["unrequested_blocks"] = sorted(n for n in by_name if n not in requested)
    if summary["unrequested_blocks"]:
        inconsistencies.append("Kani verified harnesses that were not requested")
    rows = []
    for entry in request["harnesses"]:
        block = by_name.get(entry["name"])
        if block is None:
            rows.append({"name": entry["name"], "expect": entry["expect"], "status": "NOT_RUN"})
            continue
        row = {"name": entry["name"], "expect": entry["expect"], "status": _block_status(block),
               "expect_check": entry.get("expect_check"), "time_s": block["time_s"],
               "checks_failed": block["checks_failed"], "checks_total": block["checks_total"],
               "unreachable": block["unreachable"], "covers_satisfied": block["covers_satisfied"],
               "covers_total": block["covers_total"], "failed_checks": block["failed_checks"],
               "failed_located": block["failed_located"], "failed_checks_truncated": block["failed_checks_truncated"]}
        rows.append(row)
    summary["harnesses"] = rows
    statuses = [r["status"] for r in rows]
    complete = parsed["complete_line"]
    if complete is None:
        inconsistencies.append("final 'Complete - …' line missing")
    else:
        if complete["total"] != len(rows):
            inconsistencies.append(f"Kani total {complete['total']} differs from {len(rows)} requested")
        if complete["success"] != statuses.count("SUCCESS"):
            inconsistencies.append(f"Kani success count {complete['success']} differs from parsed {statuses.count('SUCCESS')}")
    all_success = all(s == "SUCCESS" for s in statuses)
    if exit_code is None:
        inconsistencies.append("Kani exit code unknown")
    elif (exit_code == 0) != all_success:
        inconsistencies.append(f"Kani exit {exit_code} does not match the parsed statuses")
    if memcap is not None and memcap["state"] == "ENFORCED" and memcap["oom_kill"] is not None \
            and memcap["oom_kill"] != statuses.count("OUT_OF_MEMORY"):
        # Kani labels any SIGKILL of CBMC as out of memory; under the cap each such row needs one cgroup OOM kill.
        inconsistencies.append(f"cgroup OOM kills {memcap['oom_kill']} differ from {statuses.count('OUT_OF_MEMORY')} "
                               "OUT_OF_MEMORY harness(es)")
    if any(s in ("NOT_RUN", "UNKNOWN") for s in statuses):
        summary["status"] = "PARTIAL"
    elif inconsistencies:
        summary["status"] = "INCONSISTENT"
    else:
        summary["status"] = "COMPLETE"
    summary["expectation_met"] = summary["status"] == "COMPLETE" and all(
        _row_meets(r, e) for r, e in zip(rows, request["harnesses"]))
    if request["kind"] == "measurement":
        memcap_ok = memcap is None or (memcap["state"] == "ENFORCED" and memcap["oom_kill"] == 0
                                       and memcap["swap"] == "off")
        summary["measurement_ok"] = summary["expectation_met"] and memcap_ok and all(
            r["status"] != "SUCCESS" or (r["time_s"] is not None and r["time_s"] <= MEASUREMENT_LIMIT_SECONDS
                                         and (r["covers_total"] or 0) >= 1
                                         and r["covers_satisfied"] == r["covers_total"])
            for r in rows)
    for r in rows:
        if r.get("unreachable"):
            summary["notes"].append(f"{r['unreachable']} unreachable check(s) in {r['name']}")
    return summary


def gate_ok(summary: dict[str, Any]) -> bool:
    if summary.get("status") != "COMPLETE" or summary.get("expectation_met") is not True:
        return False
    if (summary.get("request") or {}).get("kind") == "measurement":
        return summary.get("measurement_ok") is True
    return True


def _memcap_line(memcap: dict[str, Any] | None) -> str:
    if memcap is None:
        return "not tracked by this lane"
    gib = lambda b: "?" if b is None else f"{b / 2**30:.2f} GiB"  # noqa: E731
    return (f"{memcap['state']}, limit {gib(memcap['max_bytes'])}, cgroup peak incl. page cache "
            f"{gib(memcap['peak_bytes'])}, OOM kills {memcap['oom_kill']}, swap {memcap['swap']}")


def _peaks_lines(peaks: dict[str, Any] | None) -> list[str]:
    if peaks is None:
        return []
    gib = lambda kb: "?" if kb is None else f"{kb / 2**20:.2f} GiB"  # noqa: E731
    every = "?" if peaks["interval_ms"] is None else f"{peaks['interval_ms'] / 1000:g}"
    out = [f"- memory peaks {peaks['state']}: sampled every {every} s, {peaks['samples']} samples, "
           f"largest sampled sum of RSS {gib(peaks['total_rss_peak_kb'])}; per command (kernel VmHWM; 13 GiB = CircleCI cap, "
           "16 GB = organizers' runner):"]
    for c in peaks["commands"]:
        fit = "≤13 GiB" if c["peak_kb"] <= 13 * 2**20 else ("≤16 GB" if c["peak_kb"] * 1024 <= 16 * 10**9 else ">16 GB")
        out.append(f"  - `{c['cmd']}` {gib(c['peak_kb'])} ({fit}), seen {c['first_s']}–{c['last_s']} s")
    if peaks.get("commands_truncated"):
        out.append(f"  - …only the {PEAKS_TOP} largest commands listed")
    return out


def render_md(summary: dict[str, Any]) -> str:
    req = summary["request"] or {}
    res = summary["resources"]
    run = summary.get("run") or {}
    lines = [
        f"# K-1 run `{req.get('request_id', '?')}`: {summary['status']}",
        "",
        f"- head `{summary['head_sha']}`, Kani `{summary['kani_commit']}`, request sha256 `{summary['request_sha256']}`",
        f"- run {run.get('id')} attempt {run.get('attempt')}, image {run.get('image_os')} {run.get('image_version')}, build {summary.get('build_outcome')}",
        f"- agent `{req.get('agent')}`, kind `{req.get('kind')}`, runner `{req.get('runner')}`, per-harness timeout {req.get('harness_timeout_minutes')} min",
        f"- gate: {gate_ok(summary)}; expectation met: {summary['expectation_met']}; measurement ok: {summary['measurement_ok']}; Kani exit {summary['kani_exit_code']}",
        f"- whole run, including compilation: max RSS {res['max_rss_kb_whole_run']} KiB, wall {res['wall_whole_run']} ({res['time_file']})",
        f"- verify memory cap: {_memcap_line(res.get('memcap'))}",
        *_peaks_lines(res.get("peaks")),
        "",
        "| harness | expect | status | time s | failed/total checks | unreachable | covers |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in summary["harnesses"]:
        short = r["name"][len(HARNESS_PREFIX):] if r["name"].startswith(HARNESS_PREFIX) else r["name"]
        covers = "" if r.get("covers_total") is None else f"{r['covers_satisfied']}/{r['covers_total']}"
        checks = "" if r.get("checks_total") is None else f"{r['checks_failed']}/{r['checks_total']}"
        lines.append(f"| {short} | {r['expect']} | {r['status']} | {r.get('time_s', '')} | {checks} | {r.get('unreachable', '')} | {covers} |")
    for r in summary["harnesses"]:
        if r.get("failed_checks"):
            lines += ["", f"Failed checks of `{r['name']}`" + (" (truncated)" if r["failed_checks_truncated"] else "") + ":"]
            lines += [f"- {c['description']} @ {c['location'] or 'no location'}" for c in r["failed_checks"]]
    if summary["inconsistencies"]:
        lines += ["", "Inconsistencies:"] + [f"- {i}" for i in summary["inconsistencies"]]
    if summary["errors"]:
        lines += ["", "Error lines" + (" (truncated)" if summary["errors_truncated"] else "") + ":", "```"]
        lines += summary["errors"] + ["```"]
    if summary["tooling_sha256"]:
        lines += ["", "Tooling SHA-256 at the run commit:"] + [f"- `{p}` {h}" for p, h in sorted(summary["tooling_sha256"].items())]
    if summary["notes"]:
        lines += ["", "Notes:"] + [f"- {n}" for n in summary["notes"]]
    text = "\n".join(lines) + "\n"
    data = text.encode()
    if len(data) > MAX_MD_BYTES:
        marker = "\n…[summary.md truncated at 12000 bytes; summary.json holds the bounded full record]\n"
        text = data[:MAX_MD_BYTES - len(marker.encode())].decode(errors="ignore") + marker
    return text


def _read_optional(path: str | None) -> str | None:
    if path is None:
        return None
    p = Path(path)
    return p.read_text(errors="replace") if p.is_file() else None


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="kani_k1")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate")
    v.add_argument("request")
    v.add_argument("--args-out", required=True)
    v.add_argument("--runner-out")
    v.add_argument("--max-total-minutes", type=int, default=MAX_TOTAL_MINUTES)
    v.add_argument("--require-runner", help="reject any other runner value (lane-specific)")
    s = sub.add_parser("summarize")
    s.add_argument("--request", required=True)
    s.add_argument("--log")
    s.add_argument("--time")
    s.add_argument("--exit-code")
    s.add_argument("--head-sha")
    s.add_argument("--kani-commit")
    s.add_argument("--request-error")
    s.add_argument("--build-outcome")
    s.add_argument("--run-id")
    s.add_argument("--run-attempt")
    s.add_argument("--image-os")
    s.add_argument("--image-version")
    s.add_argument("--memcap", help="memcap.txt of the verify step; marks the memory cap as tracked")
    s.add_argument("--peaks", help="peaks.txt of sample-mem; marks per-command memory peaks as tracked")
    s.add_argument("--bind", action="append", default=[], help="file whose SHA-256 is recorded (repeatable)")
    s.add_argument("--out-dir", required=True)
    g = sub.add_parser("gate")
    g.add_argument("summary")
    sub.add_parser("ledger")
    m = sub.add_parser("sample-mem")
    m.add_argument("--out", required=True)
    m.add_argument("--interval", type=float, default=2.0)
    m.add_argument("--max-seconds", type=float)
    a = ap.parse_args(argv)
    if a.cmd == "ledger":
        try:
            print(*ledger(json.load(sys.stdin)))
        except (ValueError, TypeError, AttributeError) as exc:
            print(f"ledger: {exc}", file=sys.stderr)
            return 2
        return 0
    if a.cmd == "sample-mem":
        sample_memory(Path(a.out), a.interval, a.max_seconds)
        return 0
    if a.cmd == "validate":
        try:
            request = validate_request(json.loads(Path(a.request).read_text()), a.max_total_minutes)
            if a.require_runner and request["runner"] != a.require_runner:
                raise RequestError(f"this lane runs only runner {a.require_runner}, request asks {request['runner']}")
        except (OSError, json.JSONDecodeError, RequestError) as exc:
            print(f"REQUEST_INVALID: {exc}", file=sys.stderr)
            return 2
        Path(a.args_out).write_text("\n".join(kani_args(request)) + "\n")
        if a.runner_out:
            Path(a.runner_out).write_text(request["runner"] + "\n")
        print(f"request {request['request_id']}: {len(request['harnesses'])} harness(es) accepted")
        return 0
    if a.cmd == "summarize":
        try:
            exit_code = int(a.exit_code) if a.exit_code not in (None, "") else None
        except ValueError:
            exit_code = None
        run = {"id": a.run_id or None, "attempt": a.run_attempt or None,
               "image_os": a.image_os or None, "image_version": a.image_version or None}
        summary = summarize(_read_optional(a.request), _read_optional(a.log), _read_optional(a.time), exit_code,
                            a.head_sha, a.kani_commit, a.request_error or None, run, file_bindings(a.bind),
                            a.build_outcome or None, _read_optional(a.memcap), a.memcap is not None,
                            _read_optional(a.peaks), a.peaks is not None)
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        (out / "summary.md").write_text(render_md(summary))
        return 0
    try:
        summary = json.loads(Path(a.summary).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"gate: unreadable summary: {exc}", file=sys.stderr)
        return 3
    ok = gate_ok(summary)
    print(f"gate: {ok}; status={summary.get('status')} expectation_met={summary.get('expectation_met')} "
          f"measurement_ok={summary.get('measurement_ok')}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
