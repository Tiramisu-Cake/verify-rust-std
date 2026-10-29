#!/usr/bin/env python3
"""Run-request validation and bounded result summary for the Kani K-1 experiment lane.

Subcommands
  validate REQUEST --args-out FILE [--runner-out FILE]   check the request, write one Kani argument per line
  summarize --request R --log L ...                      parse terse Kani output into summary.json/summary.md
  gate SUMMARY                                           exit 0 iff the run is COMPLETE, consistent and met
                                                         every expectation (and, for measurement, every bound)
  sample-mem --out FILE                                  record per-command peak RSS until SIGTERM (resource lane)
  ledger [--price POOL=USD ...]                          Cloud Build list JSON on stdin -> "builds used reserved"
                                                         minutes, or USD at the given per-minute pool prices

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
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA = "kani-k1-run-request-v1"
SUMMARY_SCHEMA = "kani-k1-run-summary-v2"
AGENTS = {"k1-merge", "k1-network", "coordinator"}
KINDS = {"measurement", "diagnostic", "resource", "partition", "autoharness", "inventory"}
# kind partition: one worker of the organizers' CI layout (kani.yml): scripts/run-kani.sh with WORKER_INDEX /
# WORKER_TOTAL over the whole std harness list (kani list order, ceiling-sized contiguous chunks), no harness
# list and no per-harness timeout, exactly as their CI. harness_timeout_minutes is the wall budget of the
# whole partition. kani_jobs: 2 = their ubuntu (KANI_JOBS=2); absent = run-kani.sh default -j (their macOS).
PARTITION_MAX_MINUTES = 300
EXPECT = {"SUCCESS", "FAILED"}
# circleci-linux-large: CircleCI Linux VM large, 4 CPU / 15 GB; the two GitHub runners are kept for the
# dormant GitHub Actions lane. gcb-e2-highmem-4: Cloud Build private pool, 4 vCPU / 32 GB, twice the
# organizers' runner memory, so it takes only kind "resource", which never counts for PASS.
# gcb-e2-standard-4: Cloud Build private pool, 4 vCPU / 16 GB, the resources of the organizers' ubuntu
# runner (R7 review 2026-10-27); measurement and diagnostic, no memory cap below the machine's own.
RESOURCE_RUNNER = "gcb-e2-highmem-4"
STANDARD_RUNNER = "gcb-e2-standard-4"
GCB_RUNNERS = {RESOURCE_RUNNER, STANDARD_RUNNER}
RUNNERS = {"circleci-linux-large", "ubuntu-latest", "macos-latest", RESOURCE_RUNNER, STANDARD_RUNNER}
PARTITION_RUNNERS = {STANDARD_RUNNER, "ubuntu-latest", "macos-latest"}
HARNESS_PREFIX = "slice::sort::shared::smallsort::verify::"
HARNESS_RE = re.compile(r"slice::sort::shared::smallsort::verify::[A-Za-z0-9_]+(::[A-Za-z0-9_]+)*")
REQUEST_ID_RE = re.compile(r"[a-z0-9][a-z0-9._-]{0,63}")
REQUEST_KEYS = {"schema", "request_id", "agent", "kind", "purpose", "runner", "harness_timeout_minutes", "harnesses"}
# kani_jobs: harnesses verified concurrently (Kani --jobs), as the organizers' ubuntu partitions do with
# KANI_JOBS=2. Only kind diagnostic on the 16 GB pool: concurrent runs share memory and CPU, so their times
# are not single-harness measurements.
# uninit_checks: adds Kani's `-Z uninit-checks` (not in the organizers' CI flags, run-kani.sh:87), so its
# results are evidence outside CI; diagnostic on the 16 GB pool only (plan R8 §4, U-1).
# controls: compiles the opt-in control/mutant harnesses (`#[cfg(kani_smallsort_controls)]`) by passing
# RUSTFLAGS="--cfg kani_smallsort_controls" to Kani; the organizers' CI never sets it, so controls stay out of
# the submitted set (plan R8, L1-6/L1-9). 16 GB pool only.
CONTROLS_CFG = "kani_smallsort_controls"
OPTIONAL_REQUEST_KEYS = {"kani_jobs", "uninit_checks", "controls", "worker_index", "worker_total", "inventory"}
KANI_JOBS = {1, 2, 3}
PARTITION_KANI_JOBS = {1, 2}
STANDARD_DIAGNOSTIC_MAX_HARNESSES = 80
HARNESS_REQUIRED = {"name", "expect"}
HARNESS_OPTIONAL = {"expect_check"}
MAX_HARNESSES = 20
MAX_TIMEOUT_MINUTES = 30
RESOURCE_MAX_TIMEOUT_MINUTES = 720
AUTOHARNESS_MAX_MINUTES = 270  # whole build work budget, including the supported full std inventory
INVENTORY_MAX_MINUTES = 60
MEASUREMENT_TIMEOUT_MINUTES = 10
MAX_TOTAL_MINUTES = 150
MEASUREMENT_LIMIT_SECONDS = 600.0

MAX_FAILED_CHECKS = 20
MAX_LINE_CHARS = 400
MAX_ERROR_LINES = 80
MAX_MD_BYTES = 12000
MAX_METADATA_FILES_PER_DIR = 2048
MAX_METADATA_FILE_BYTES = 16 * 1024 * 1024
METADATA_REFRESH_SECONDS = 2.0

CHECKING_RE = re.compile(r"^(?:Thread \d+: )?Checking harness (\S+?)\.\.\.\s*$")
# Under --jobs > 1 Kani prefixes every line of a harness's output with its worker, `Thread N: ` (seen in
# Cloud Build run 22e18888, 2026-10-27); blocks of different workers interleave, a worker's own do not.
THREAD_RE = re.compile(r"^Thread (\d+): ?(.*)$")
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
    extra, missing = set(data) - REQUEST_KEYS - OPTIONAL_REQUEST_KEYS, REQUEST_KEYS - set(data)
    if extra:
        raise RequestError(f"unknown request keys: {sorted(extra)}")
    if missing:
        raise RequestError(f"missing request keys: {sorted(missing)}")
    if data["schema"] != SCHEMA:
        raise RequestError(f"schema must be {SCHEMA}")
    if not _one_line(data["purpose"], 300):
        raise RequestError("purpose must be one non-empty line of at most 300 characters")
    if not isinstance(data["request_id"], str) or not REQUEST_ID_RE.fullmatch(data["request_id"]):
        raise RequestError("request_id must match [a-z0-9][a-z0-9._-]{0,63}")
    for key, allowed in (("agent", AGENTS), ("kind", KINDS), ("runner", RUNNERS)):
        if not isinstance(data[key], str) or data[key] not in allowed:
            raise RequestError(f"{key} must be one of {sorted(allowed)}")
    if "inventory" in data:
        if type(data["inventory"]) is not bool:
            raise RequestError("inventory must be true or false")
    inventory = data["kind"] == "inventory"
    if inventory:
        if data["runner"] != STANDARD_RUNNER:
            raise RequestError(f"kind inventory runs only on runner {STANDARD_RUNNER}")
        if data.get("inventory") is not True:
            raise RequestError("kind inventory requires inventory: true")
        if data["harnesses"] != []:
            raise RequestError("kind inventory takes harnesses: []")
        if set(data) & {"uninit_checks", "worker_index", "worker_total", "kani_jobs"}:
            raise RequestError("kind inventory does not accept uninit_checks, worker_index, worker_total, or kani_jobs")
        timeout = data["harness_timeout_minutes"]
        if type(timeout) is not int or not 1 <= timeout <= INVENTORY_MAX_MINUTES:
            raise RequestError(f"harness_timeout_minutes (whole-job wall budget) must be an integer 1..{INVENTORY_MAX_MINUTES}")
        if "controls" in data and type(data["controls"]) is not bool:
            raise RequestError("controls must be true or false")
        return data
    if data.get("inventory") and (data["runner"] != STANDARD_RUNNER or data["kind"] not in ("diagnostic", "autoharness")):
        raise RequestError(f"inventory is only for kind diagnostic, autoharness, or inventory on runner {STANDARD_RUNNER}")
    partition = data["kind"] == "partition"
    autoharness = data["kind"] == "autoharness"
    if autoharness:
        unsupported = set(data) & {"uninit_checks", "controls", "worker_index", "worker_total", "kani_jobs"}
        if unsupported:
            raise RequestError(f"kind autoharness uses literal workflow flags; unsupported request keys: {sorted(unsupported)}")
        if data["runner"] != STANDARD_RUNNER:
            raise RequestError(f"kind autoharness runs only on runner {STANDARD_RUNNER}")
        if data["harnesses"] != []:
            raise RequestError("kind autoharness takes harnesses: [] (command is extracted from kani.yml)")
        timeout = data["harness_timeout_minutes"]
        if type(timeout) is not int or not 1 <= timeout <= AUTOHARNESS_MAX_MINUTES:
            raise RequestError(f"harness_timeout_minutes (whole-job wall budget) must be an integer 1..{AUTOHARNESS_MAX_MINUTES}")
        return data
    if partition:
        if data["runner"] not in PARTITION_RUNNERS:
            raise RequestError(f"kind partition runs only on {sorted(PARTITION_RUNNERS)}")
        wi, wt = data.get("worker_index"), data.get("worker_total")
        if type(wi) is not int or type(wt) is not int or not 1 <= wi <= wt <= 16:
            raise RequestError("kind partition needs integers 1 <= worker_index <= worker_total <= 16")
        if data["harnesses"] != []:
            raise RequestError("kind partition takes harnesses: [] (the whole std harness list is partitioned)")
        if data.get("uninit_checks") or data.get("controls"):
            raise RequestError("kind partition replicates the organizers' CI: no uninit_checks, no controls")
        t = data["harness_timeout_minutes"]
        cap = PARTITION_MAX_MINUTES if max_total_minutes is None else min(max_total_minutes, PARTITION_MAX_MINUTES)
        if type(t) is not int or not 1 <= t <= cap:
            raise RequestError(f"harness_timeout_minutes (partition wall budget) must be an integer 1..{cap}")
        if "kani_jobs" in data and (type(data["kani_jobs"]) is not int or data["kani_jobs"] not in PARTITION_KANI_JOBS):
            raise RequestError(f"kani_jobs must be one of {sorted(PARTITION_KANI_JOBS)} for kind partition")
        return data
    if "worker_index" in data or "worker_total" in data:
        raise RequestError("worker_index/worker_total are only for kind partition")
    if (data["runner"] == RESOURCE_RUNNER) != (data["kind"] == "resource"):
        raise RequestError(f"kind resource runs exactly on runner {RESOURCE_RUNNER}, and that runner takes only kind resource")
    if "kani_jobs" in data:
        if type(data["kani_jobs"]) is not int or data["kani_jobs"] not in KANI_JOBS:
            raise RequestError(f"kani_jobs must be one of {sorted(KANI_JOBS)}")
        if data["kani_jobs"] != 1 and (data["runner"] != STANDARD_RUNNER or data["kind"] != "diagnostic"):
            raise RequestError(f"kani_jobs > 1 is only for kind diagnostic on runner {STANDARD_RUNNER}")
    if "uninit_checks" in data:
        if type(data["uninit_checks"]) is not bool:
            raise RequestError("uninit_checks must be true or false")
        if data["uninit_checks"] and (data["runner"] != STANDARD_RUNNER or data["kind"] != "diagnostic"):
            raise RequestError(f"uninit_checks is only for kind diagnostic on runner {STANDARD_RUNNER}")
    if "controls" in data:
        if type(data["controls"]) is not bool:
            raise RequestError("controls must be true or false")
        if data["controls"] and data["runner"] != STANDARD_RUNNER:
            raise RequestError(f"controls is only for runner {STANDARD_RUNNER}")
    timeout = data["harness_timeout_minutes"]
    limit = RESOURCE_MAX_TIMEOUT_MINUTES if data["kind"] == "resource" else MAX_TIMEOUT_MINUTES
    if type(timeout) is not int or not 1 <= timeout <= limit:
        raise RequestError(f"harness_timeout_minutes must be an integer 1..{limit} for kind {data['kind']}")
    if data["kind"] == "measurement" and timeout != MEASUREMENT_TIMEOUT_MINUTES:
        raise RequestError("a measurement run must use harness_timeout_minutes = 10")
    harnesses = data["harnesses"]
    harness_limit = (STANDARD_DIAGNOSTIC_MAX_HARNESSES
                     if data["runner"] == STANDARD_RUNNER and data["kind"] == "diagnostic" else MAX_HARNESSES)
    if not isinstance(harnesses, list) or not 1 <= len(harnesses) <= harness_limit:
        raise RequestError(f"harnesses must be a list of 1..{harness_limit} entries")
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
    # The kind's own cap always applies; a lane may only lower it (CircleCI 40). The Cloud Build dispatcher
    # sizes the paid build timeout from this total (k1g.sh), so it must never exceed the cap.
    cap = RESOURCE_MAX_TIMEOUT_MINUTES if data["kind"] == "resource" else MAX_TOTAL_MINUTES
    max_total_minutes = cap if max_total_minutes is None else min(max_total_minutes, cap)
    if len(names) * timeout > max_total_minutes:
        raise RequestError(f"harness count × timeout exceeds {max_total_minutes} minutes for this lane")
    return data


def partition_env(request: dict[str, Any]) -> list[str]:
    """Environment of one organizers'-CI worker (kind partition), one VAR=value per line; [] otherwise."""
    if request["kind"] != "partition":
        return []
    env = [f"WORKER_INDEX={request['worker_index']}", f"WORKER_TOTAL={request['worker_total']}"]
    if "kani_jobs" in request:
        env.append(f"KANI_JOBS={request['kani_jobs']}")
    return env


PARTITION_TOP = 15
PARTITION_FAILURES = 20


def worker_list(log_text: str) -> list[str] | None:
    """Harness names run-kani.sh hands to this worker: the lines after "Running verification for harnesses:"
    (one name per line, no whitespace), up to the first other line. None if the header is missing."""
    lines = log_text.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "Running verification for harnesses:":
            names = []
            for nxt in lines[i + 1:]:
                if not nxt or any(c.isspace() for c in nxt) or "::" not in nxt:
                    break
                names.append(nxt)
            return names
    return None


def summarize_partition(summary: dict[str, Any], request: dict[str, Any], parsed: dict[str, Any],
                        exit_code: int | None, log_text: str = "") -> dict[str, Any]:
    """Kind partition: no expectations per harness; every harness of the worker must verify."""
    blocks = parsed["blocks"]
    inconsistencies = summary["inconsistencies"]
    assigned = worker_list(log_text)
    if assigned is None:
        inconsistencies.append("run-kani.sh worker harness list missing: completeness cannot be checked")
    elif sorted(assigned) != sorted(b["name"] for b in blocks):
        missing = sorted(set(assigned) - {b["name"] for b in blocks})
        inconsistencies.append(f"worker was assigned {len(assigned)} harnesses but {len(blocks)} were reported"
                               + (f"; first missing: {missing[0]}" if missing else ""))
    if "kani_jobs" not in request or request["kani_jobs"] > 1:
        if parsed["overlaps"]:
            inconsistencies.append(f"{parsed['overlaps']} harness block(s) started on a worker before its previous block ended")
        if parsed["orphans"]:
            inconsistencies.append(f"{parsed['orphans']} result line(s) without a worker prefix under concurrent verification")
    names = [b["name"] for b in blocks]
    if len(set(names)) != len(names):
        inconsistencies.append("harness reported more than once")
    statuses = [_block_status(b) for b in blocks]
    counts: dict[str, int] = {}
    for st in statuses:
        counts[st] = counts.get(st, 0) + 1
    complete = parsed["complete_line"]
    if complete is None:
        inconsistencies.append("final 'Complete - …' line missing")
    else:
        if complete["total"] != len(blocks):
            inconsistencies.append(f"Kani total {complete['total']} differs from {len(blocks)} parsed harness blocks")
        if complete["success"] != counts.get("SUCCESS", 0):
            inconsistencies.append(f"Kani success count {complete['success']} differs from parsed {counts.get('SUCCESS', 0)}")
    all_success = bool(blocks) and all(st == "SUCCESS" for st in statuses)
    if exit_code is not None and (exit_code == 0) != all_success:
        inconsistencies.append(f"Kani exit {exit_code} does not match the parsed statuses")
    if not blocks:
        summary["status"] = "RUNNER_ERROR" if not parsed["errors"] else "TOOL_ERROR"
    elif any(st == "UNKNOWN" for st in statuses) or complete is None:
        summary["status"] = "PARTIAL"
    elif inconsistencies:
        summary["status"] = "INCONSISTENT"
    else:
        summary["status"] = "COMPLETE"
    summary["expectation_met"] = summary["status"] == "COMPLETE" and all_success
    timed = sorted(((b["time_s"] or 0.0, b["name"], st) for b, st in zip(blocks, statuses)), reverse=True)
    failures = [{"name": b["name"], "status": st,
                 "first_failed_check": (b["failed_checks"][0]["description"] if b["failed_checks"] else None)}
                for b, st in zip(blocks, statuses) if st != "SUCCESS"]
    summary["partition"] = {
        "worker_index": request["worker_index"], "worker_total": request["worker_total"],
        "kani_jobs": request.get("kani_jobs"), "harness_count": len(blocks), "counts": counts,
        "smallsort_kani_k1_count": sum(n.startswith(HARNESS_PREFIX) for n in names),
        "sum_verification_time_s": round(sum(t for t, _, _ in timed), 3),
        "slowest": [{"name": n, "time_s": t, "status": st} for t, n, st in timed[:PARTITION_TOP]],
        "failures": failures[:PARTITION_FAILURES], "failures_truncated": len(failures) > PARTITION_FAILURES,
    }
    return summary


def kani_args(request: dict[str, Any]) -> list[str]:
    if request["kind"] == "inventory":
        return []
    args: list[str] = []
    for entry in request["harnesses"]:
        args += ["--harness", entry["name"]]
    if request.get("uninit_checks"):
        args += ["-Z", "uninit-checks"]
    args += ["--exact", "--harness-timeout", f"{request['harness_timeout_minutes']}m",
             f"--jobs={request.get('kani_jobs', 1)}", "--output-format=terse"]
    return args


def extract_autoharness_command(workflow: str) -> str:
    """Return the literal `run: |` body for kani_autoharness / Run Kani Verification."""
    lines = workflow.splitlines()
    job = next((i for i, line in enumerate(lines) if line == "  kani_autoharness:"), None)
    if job is None:
        raise ValueError("workflow has no kani_autoharness job")
    job_end = next((i for i in range(job + 1, len(lines)) if re.match(r"^  [A-Za-z0-9_-]+:", lines[i])), len(lines))
    step = next((i for i in range(job, job_end) if lines[i].strip() == "- name: Run Kani Verification"), None)
    if step is None:
        raise ValueError("kani_autoharness has no Run Kani Verification step")
    run = next((i for i in range(step + 1, job_end) if lines[i].strip() == "run: |"), None)
    if run is None:
        raise ValueError("Run Kani Verification step must use a literal run: | block")
    body: list[str] = []
    for line in lines[run + 1:job_end]:
        if line.strip() and not line.startswith("          "):
            break
        body.append(line[10:] if line.startswith("          ") else "")
    while body and not body[-1]:
        body.pop()
    if not body or not any(line.startswith("scripts/run-kani.sh --run autoharness") for line in body):
        raise ValueError("autoharness command block is empty or does not invoke run-kani.sh")
    return "\n".join(body) + "\n"


def verification_mode(kind: str) -> str:
    """Map a validated request kind to the gcb-k1 verify-stage route."""
    return {"inventory": "inventory", "autoharness": "autoharness", "partition": "partition", "measurement": "selected",
            "diagnostic": "selected"}.get(kind, "invalid")


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
    overlaps = 0  # a harness started on a worker whose previous block had not ended
    orphans = 0   # an unprefixed result line while only prefixed (worker) blocks were open
    result_res = (STATUS_RE, TIME_RE, CHECKS_RE, COVER_RE, FAILED_CHECK_RE, FILE_RE, TIMEOUT_RE, OOM_RE)
    open_blocks: dict[str | None, dict[str, Any] | None] = {}   # worker -> its open block; None = unprefixed
    for raw in text.splitlines():
        line = raw.rstrip("\r")
        worker = None
        m = THREAD_RE.match(line)
        if m:
            worker, line = m.group(1), m.group(2)
        current = open_blocks.get(worker)
        m = CHECKING_RE.match(line)
        if m:
            overlaps += current is not None
            current = open_blocks[worker] = _new_block(m.group(1))
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
            open_blocks.clear()
            continue
        if SUMMARY_HEADER_RE.match(line):
            open_blocks.clear()
            continue
        if current is None:
            if worker is None and any(open_blocks.values()) and any(r.match(line) for r in result_res):
                orphans += 1
            continue
        if TIMEOUT_RE.match(line):
            current["timed_out"] = True
            # Kani may report FAILED and then its timeout marker, with no Verification Time.
            # This marker is terminal for the worker and must close the block before its next start.
            open_blocks[worker] = None
            continue
        if OOM_RE.match(line):
            current["out_of_memory"] = True
            open_blocks[worker] = None
            continue
        m = STATUS_RE.match(line)
        if m:
            current["status_line"] = m.group(1)
            if m.group(1) == "TIMEOUT":
                # Some Kani versions print no Verification Time for a timeout.
                # Close this worker's block here so the next Thread N start is attributed cleanly.
                open_blocks[worker] = None
            continue
        m = TIME_RE.match(line)
        if m:
            current["time_s"] = float(m.group(1))
            open_blocks[worker] = None  # a harness block ends with its verification time
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
    return {"blocks": blocks, "errors": errors, "errors_truncated": errors_truncated, "complete_line": complete,
            "overlaps": overlaps, "orphans": orphans}


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
    """k1-out/memcap.txt of the verify step: key=value lines written by circleci-k1.sh (state ENFORCED or
    UNAVAILABLE: a cgroup cap) or gcb-k1.sh (state MACHINE: no cgroup cap, the machine's memory is the limit)."""
    if text is None:
        return {"state": "MISSING", "max_bytes": None, "peak_bytes": None, "oom_kill": None, "swap": None, "reason": None}
    fields = dict(line.split("=", 1) for line in text.splitlines() if "=" in line)

    def num(key: str) -> int | None:
        value = fields.get(key, "").strip()
        return int(value) if value.isdigit() else None
    state = fields.get("state", "").strip()
    return {"state": state if state in ("ENFORCED", "UNAVAILABLE", "MACHINE") else "UNPARSED", "max_bytes": num("max_bytes"),
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
    processes: list[dict[str, str]] = []
    roles: list[dict[str, str]] = []
    for line in text.splitlines():
        if line.startswith("cmd="):
            f = dict(part.split("=", 1) for part in line.split() if "=" in part)
            if all(f.get(k, "").isdigit() for k in ("peak_kb", "first_s", "last_s")):
                command = {"cmd": _clip(f["cmd"])[:40], "peak_kb": int(f["peak_kb"]),
                           "first_s": int(f["first_s"]), "last_s": int(f["last_s"])}
                if f.get("peak_s", "").isdigit():
                    command["peak_s"] = int(f["peak_s"])
                commands.append(command)
        elif line.startswith(("cbmc_pid=", "solver_pid=")):
            processes.append(dict(part.split("=", 1) for part in line.split() if "=" in part))
        elif line.startswith("role="):
            roles.append(dict(part.split("=", 1) for part in line.split() if "=" in part))
        elif "=" in line:
            key, value = line.split("=", 1)
            head[key.strip()] = value.strip()

    def num(key: str) -> int | None:
        return int(head[key]) if head.get(key, "").isdigit() else None
    commands.sort(key=lambda c: -c["peak_kb"])
    samples = num("samples")
    return {"state": "PARSED" if samples else "UNPARSED", "interval_ms": num("interval_ms"), "samples": samples,
            "total_rss_peak_kb": num("total_rss_peak_kb"), "total_peak_s": num("total_peak_s"),
            "commands": commands[:PEAKS_TOP],
            "commands_truncated": len(commands) > PEAKS_TOP, "processes": processes[-12:], "roles": roles[-3:],
            "cgroup_events": {k: v for k, v in head.items() if k.startswith("cgroup_")},
            "dmesg_oom": head.get("dmesg_oom"), "records_truncated": head.get("sampler_records_truncated") == "true"}


def _proc_status(path: Path) -> dict[str, str] | None:
    try:
        text = path.read_text()
    except OSError:
        return None
    return dict(line.split(":", 1) for line in text.splitlines() if ":" in line)


def _kb(value: str | None) -> int:
    parts = (value or "").split()
    return int(parts[0]) if parts and parts[0].isdigit() else 0


def _proc_ppid(path: Path) -> str | None:
    try:
        fields = path.read_text().rsplit(")", 1)[1].split()
        return fields[1] if len(fields) > 1 and fields[1].isdigit() else None
    except (OSError, IndexError):
        return None


def _proc_cwd(path: Path) -> Path | None:
    try:
        return Path(os.readlink(path / "cwd")).resolve(strict=False)
    except (OSError, RuntimeError):
        return None


def _cgroup_events() -> dict[str, int]:
    try:
        rows = (Path("/sys/fs/cgroup/memory.events")).read_text().splitlines()
    except OSError:
        return {}
    return {p[0]: int(p[1]) for line in rows if len(p := line.split()) == 2 and p[1].isdigit()}


_METADATA_INDEX_CACHE: dict[str, dict[str, Any]] = {}


def _canonical_path(value: str | Path, base: Path) -> Path | None:
    try:
        path = Path(value)
        return (path if path.is_absolute() else base / path).resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return None


def _model_paths_from_argv(argv: list[str], cwd: Path) -> list[Path]:
    # Pinned Kani appends custom CBMC args, the model, then verbosity/json-ui flags.
    # Scan all path-like .out tokens; metadata must identify exactly one candidate.
    candidates = []
    seen: set[str] = set()
    for token in argv:
        if token.startswith("-") or not token.endswith(".out") or token.endswith(".symtab.out"):
            continue
        path = _canonical_path(token, cwd)
        if path is not None and str(path) not in seen:
            candidates.append(path)
            seen.add(str(path))
    return candidates


def _goto_model_path(value: str, process_cwd: Path) -> Path | None:
    if not value.endswith(".symtab.out"):
        return None
    goto = Path(value)
    model = goto.with_name(goto.name[:-len(".symtab.out")] + ".out")
    return _canonical_path(model, process_cwd)


def metadata_index(metadata_dir: Path, process_cwd: Path) -> dict[str, Any]:
    """Read one output directory's compiler metadata, resolving goto_file from CBMC's cwd."""
    try:
        directory = metadata_dir.resolve(strict=False)
        all_files = sorted(directory.glob("*.kani-metadata.json"))
        overflow = len(all_files) > MAX_METADATA_FILES_PER_DIR
        files = all_files[:MAX_METADATA_FILES_PER_DIR]
        signature = []
        for path in files:
            try:
                stat = path.stat()
                signature.append((str(path), stat.st_mtime_ns, stat.st_size))
            except OSError:
                signature.append((str(path), -1, -1))
    except OSError:
        directory, signature, overflow = metadata_dir, [], False
    cwd = process_cwd.resolve(strict=False)
    key = f"{directory}|cwd={cwd}"
    now = time.monotonic()
    cached = _METADATA_INDEX_CACHE.get(key)
    if cached and now - cached["checked_s"] < METADATA_REFRESH_SECONDS:
        return cached
    if cached and cached["signature"] == signature:
        cached["checked_s"] = now
        return cached

    index: dict[str, list[dict[str, Any]]] = {}
    complete = not overflow
    for raw_path, mtime_ns, size in signature:
        if size < 0 or size > MAX_METADATA_FILE_BYTES:
            complete = False
            continue
        path = Path(raw_path)
        try:
            raw = path.read_bytes()
            after = path.stat()
            if after.st_mtime_ns != mtime_ns or after.st_size != size:
                complete = False
                continue
            digest = hashlib.sha256(raw).hexdigest()
            payload = json.loads(raw)
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            complete = False
            continue
        if not isinstance(payload, dict):
            complete = False
            continue
        for key_name in ("proof_harnesses", "test_harnesses"):
            entries = payload.get(key_name)
            if not isinstance(entries, list):
                complete = False
                continue
            for row in entries:
                if not isinstance(row, dict):
                    complete = False
                    continue
                pretty, mangled, goto = row.get("pretty_name"), row.get("mangled_name"), row.get("goto_file")
                # `goto_file` is optional in Kani metadata; null rows cannot name this model.
                if goto is None:
                    continue
                if not all(isinstance(v, str) and v for v in (pretty, mangled, goto)):
                    complete = False
                    continue
                model = _goto_model_path(goto, cwd)
                if model is None:
                    continue
                index.setdefault(str(model), []).append({
                    "pretty_name": pretty, "mangled_name": mangled, "metadata_path": raw_path,
                    "metadata_sha256": digest, "metadata_group": key_name,
                })
    cached = {"signature": signature, "checked_s": now, "index": index, "metadata_file_count": len(signature),
              "complete": complete}
    if len(_METADATA_INDEX_CACHE) >= 16 and key not in _METADATA_INDEX_CACHE:
        oldest = min(_METADATA_INDEX_CACHE, key=lambda k: _METADATA_INDEX_CACHE[k]["checked_s"])
        _METADATA_INDEX_CACHE.pop(oldest, None)
    _METADATA_INDEX_CACHE[key] = cached
    return cached


def resolve_cbmc_metadata(argv: list[str], cwd: Path, *, head_sha: str | None = None,
                          kani_commit: str | None = None, build_id: str | None = None) -> dict[str, Any]:
    """Join a CBMC argv model candidate to exactly one same-directory Kani metadata row."""
    models = _model_paths_from_argv(argv, cwd)
    identity = {"head_sha": head_sha, "kani_commit": kani_commit, "build_id": build_id}
    if not models:
        return {"attribution": "unresolved-model-path", **identity}
    matches = []
    incomplete = []
    for model in models:
        index = metadata_index(model.parent, cwd)
        rows = index["index"].get(str(model), [])
        if len(rows) > 1:
            return {"attribution": "metadata-ambiguous", "model_path": str(model),
                    "metadata_dir": str(model.parent), "metadata_file_count": index["metadata_file_count"],
                    "metadata_match_count": len(rows), **identity}
        if not index["complete"]:
            incomplete.append((model, index))
        elif len(rows) == 1:
            matches.append((model, index, rows[0]))
    if len(matches) > 1:
        return {"attribution": "metadata-ambiguous", "model_candidates": [str(p) for p in models], **identity}
    if incomplete:
        model, index = incomplete[0]
        return {"attribution": "metadata-incomplete", "model_path": str(model),
                "metadata_dir": str(model.parent), "metadata_file_count": index["metadata_file_count"], **identity}
    if not matches:
        model = models[0]
        index = metadata_index(model.parent, cwd)
        return {"attribution": "metadata-not-found", "model_path": str(model),
                "metadata_dir": str(model.parent), "metadata_file_count": index["metadata_file_count"],
                "metadata_match_count": 0, **identity}
    model, index, row = matches[0]
    result: dict[str, Any] = {"model_path": str(model), "metadata_dir": str(model.parent), **identity}
    result["metadata_file_count"] = index["metadata_file_count"]
    result["metadata_match_count"] = 1
    result.update(attribution="direct", direct_harness=row["pretty_name"], **row)
    return result


def finalize_process_records(process_records: dict[str, dict[str, Any]]) -> None:
    """Propagate only exact CBMC metadata matches to direct child solvers; keep active sets ambiguous."""
    for record in process_records.values():
        record.setdefault("metadata_resolution", record.get("attribution", "unresolved"))
    cbmc_records = {str(record["pid"]): record for record in process_records.values() if record.get("cmd") == "cbmc"}
    cbmc_harnesses = {pid: record for pid, record in cbmc_records.items() if record.get("metadata_resolution") == "direct"}
    for record in process_records.values():
        parent = cbmc_records.get(record.get("ppid")) if record.get("cmd") != "cbmc" else None
        if parent is not None:
            record["metadata_parent_pid"] = parent["pid"]
            record["metadata_resolution"] = parent.get("metadata_resolution", parent.get("attribution"))
        exact_parent = cbmc_harnesses.get(record.get("ppid")) if record.get("cmd") != "cbmc" else None
        if exact_parent is not None:
            record.update({key: exact_parent[key] for key in ("attribution", "direct_harness", "harness", "mangled_name",
                                                         "metadata_path", "metadata_sha256", "metadata_group",
                                                         "metadata_match_count", "metadata_file_count", "metadata_dir",
                                                         "model_path", "head_sha",
                                                         "kani_commit", "build_id") if key in exact_parent})
            record["parent_cbmc_pid"] = exact_parent["pid"]
        if record.get("metadata_resolution") != "direct":
            record["attribution"] = "active-set-ambiguous" if record.get("active_at_peak") else "unattributed"
        else:
            record["attribution"] = "direct"
        if record.get("direct_harness"):
            record["harness"] = record["direct_harness"]
        if record.get("cmd") != "cbmc" and parent is None:
            record.setdefault("metadata_resolution", "no-cbmc-parent")
        record["active_harnesses"] = [f"Thread {worker}: {name}"
                                       for worker, name in sorted(record.pop("active_at_peak", {}).items())]


def sample_memory(out: Path, interval: float, max_seconds: float | None = None, proc: Path = Path("/proc"),
                  log: Path | None = None, harness_out: Path | None = None, head_sha: str | None = None,
                  kani_commit: str | None = None, build_id: str | None = None) -> None:
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
    cbmc: dict[str, dict[str, Any]] = {}
    solver: dict[str, dict[str, Any]] = {}
    driver_series: list[tuple[int, int]] = []
    harness_observations: list[tuple[int, str]] = []
    active_by_worker: dict[str, str] = {}
    role_peaks: dict[str, tuple[int, int]] = {}
    process_records: dict[str, dict[str, Any]] = {}
    cgroup_events_start = _cgroup_events()
    total_peak = total_peak_s = samples = 0
    last_driver_s = -30  # Include the baseline point at elapsed 0; subsequent points are about 30 s apart.
    log_offset = 0
    me = str(os.getpid())
    while True:
        now = int(time.monotonic() - t0)
        total = 0
        role_now = {"driver": 0, "cbmc": 0, "solver": 0}
        for status_path in proc.glob("[0-9]*/status"):
            if status_path.parent.name == me:
                continue
            st = _proc_status(status_path)
            if not st or "VmRSS" not in st:
                continue  # kernel thread or gone
            total += _kb(st.get("VmRSS"))
            name = re.sub(r"[^A-Za-z0-9._+-]", "_", st.get("Name", "?").strip())[:40] or "?"
            rss_now = _kb(st.get("VmRSS"))
            if name == "kani-driver":
                role_now["driver"] += rss_now
            elif name == "cbmc":
                role_now["cbmc"] += rss_now
            elif re.search(r"(?i)(kissat|cadical|cryptominisat|minisat|lingeling|boolector|bitwuzla|yices|cvc5|z3)", name):
                role_now["solver"] += rss_now
            rss_peak = max(_kb(st.get("VmHWM")), _kb(st.get("VmRSS")))
            entry = peaks.setdefault(name, {"peak_kb": 0, "first_s": now, "last_s": now, "peak_s": now})
            if rss_peak > entry["peak_kb"]:
                entry["peak_kb"], entry["peak_s"] = rss_peak, now
            entry["last_s"] = now
            if name == "cbmc":
                pid = status_path.parent.name
                try:
                    argv = [arg.decode("utf-8", "replace") for arg in (status_path.parent / "cmdline").read_bytes().split(b"\0") if arg]
                except OSError:
                    argv = []
                cwd = _proc_cwd(status_path.parent) or Path.cwd()
                resolved = resolve_cbmc_metadata(argv, cwd, head_sha=head_sha, kani_commit=kani_commit, build_id=build_id)
                direct = resolved.get("direct_harness")
                model_hint = resolved.get("model_path") or (argv[-1] if argv else "")
                per_pid = cbmc.setdefault(pid, {"peak_kb": 0, "first_s": now, "last_s": now,
                                                 "peak_s": now, "hint": direct or model_hint[-100:]})
                for field in ("direct_harness", "harness", "mangled_name", "metadata_path", "metadata_sha256",
                              "metadata_group", "metadata_match_count", "metadata_file_count", "metadata_dir", "model_path"):
                    per_pid.pop(field, None)
                per_pid.update({k: v for k, v in resolved.items() if k != "attribution"})
                per_pid["attribution"] = resolved["attribution"]
                per_pid["metadata_resolution"] = resolved["attribution"]
                if rss_peak > per_pid["peak_kb"]:
                    per_pid["peak_kb"], per_pid["peak_s"] = rss_peak, now
                    per_pid["active_at_peak"] = dict(active_by_worker)
                per_pid["last_s"] = now
                per_pid["active"] = ",".join(f"T{worker}:{h}" for worker, h in sorted(active_by_worker.items()))[:180]
                record = process_records.setdefault(pid, {"pid": pid, "cmd": name, "first_s": now, "last_s": now,
                                                          "head_sha": head_sha, "kani_commit": kani_commit,
                                                          "build_id": build_id})
                for field in ("direct_harness", "harness", "mangled_name", "metadata_path", "metadata_sha256",
                              "metadata_group", "metadata_match_count", "metadata_file_count", "metadata_dir", "model_path"):
                    record.pop(field, None)
                record.update({k: v for k, v in resolved.items() if k != "attribution"})
                record["attribution"] = resolved["attribution"]
                record["metadata_resolution"] = resolved["attribution"]
                if rss_peak > record.get("peak_kb", 0):
                    record.update(peak_kb=rss_peak, peak_s=now,
                                  active_at_peak=dict(active_by_worker), ppid=_proc_ppid(status_path.parent / "stat"))
                record["last_s"] = now
                if len(cbmc) > 12:
                    keep = sorted(cbmc, key=lambda p: cbmc[p]["peak_kb"], reverse=True)[:6]
                    cbmc = {p: cbmc[p] for p in keep}
            elif re.search(r"(?i)(kissat|cadical|cryptominisat|minisat|lingeling|boolector|bitwuzla|yices|cvc5|z3)", name):
                pid = status_path.parent.name
                entry = solver.setdefault(pid, {"name": name, "peak_kb": 0, "first_s": now, "last_s": now,
                                                "peak_s": now, "active": ""})
                if rss_peak > entry["peak_kb"]:
                    entry["peak_kb"], entry["peak_s"] = rss_peak, now
                    entry["direct_harness"] = None
                    entry["active_at_peak"] = dict(active_by_worker)
                entry["last_s"] = now
                entry["active"] = ",".join(f"T{worker}:{h}" for worker, h in sorted(active_by_worker.items()))[:180]
                record = process_records.setdefault(pid, {"pid": pid, "cmd": name, "first_s": now, "last_s": now,
                                                          "head_sha": head_sha, "kani_commit": kani_commit,
                                                          "build_id": build_id})
                if rss_peak > record.get("peak_kb", 0):
                    record.update(peak_kb=rss_peak, peak_s=now,
                                  active_at_peak=dict(active_by_worker), ppid=_proc_ppid(status_path.parent / "stat"))
                record["last_s"] = now
                if len(solver) > 12:
                    keep = sorted(solver, key=lambda p: solver[p]["peak_kb"], reverse=True)[:6]
                    solver = {p: solver[p] for p in keep}
        if now - last_driver_s >= 30:
            driver_rss = 0
            for status_path in proc.glob("[0-9]*/status"):
                st = _proc_status(status_path)
                if st and re.sub(r"[^A-Za-z0-9._+-]", "_", st.get("Name", "").strip())[:40] == "kani-driver":
                    driver_rss += _kb(st.get("VmRSS"))
            if len(driver_series) >= 50:
                driver_series = driver_series[::2]
            driver_series.append((now, driver_rss))
            last_driver_s = now
        if log is not None:
            try:
                with log.open("rb") as stream:
                    stream.seek(log_offset)
                    fresh = stream.read(65536)
                    log_offset = stream.tell()
                for line in fresh.decode("utf-8", "replace").splitlines():
                    worker, body = "0", line
                    thread = THREAD_RE.match(line)
                    if thread:
                        worker, body = thread.group(1), thread.group(2)
                    match = CHECKING_RE.match(body)
                    if match:
                        harness_name = match.group(1)
                        if harness_name.startswith(HARNESS_PREFIX):
                            harness_name = harness_name[len(HARNESS_PREFIX):]
                        active_by_worker[worker] = harness_name[:80]
                        if len(harness_observations) < 50:
                            harness_observations.append((now, f"T{worker}:{harness_name[:70]}"))
                    else:
                        status = STATUS_RE.match(body)
                        if ((status and status.group(1) == "TIMEOUT") or TIMEOUT_RE.match(body)
                                or OOM_RE.match(body) or TIME_RE.match(body)):
                            active_by_worker.pop(worker, None)
            except OSError:
                pass
        if total > total_peak:
            total_peak, total_peak_s = total, now
        for role, rss in role_now.items():
            if rss > role_peaks.get(role, (0, now))[0]:
                role_peaks[role] = (rss, now)
        samples += 1
        lines = [f"interval_ms={round(interval * 1000)}", f"samples={samples}", f"elapsed_s={now}",
                 f"total_rss_peak_kb={total_peak}", f"total_peak_s={total_peak_s}"]
        lines += [f"cmd={n} peak_kb={e['peak_kb']} first_s={e['first_s']} last_s={e['last_s']} peak_s={e['peak_s']}"
                  for n, e in sorted(peaks.items())]
        lines += [f"role={role} simultaneous_rss_peak_kb={rss} peak_s={at}"
                  for role, (rss, at) in sorted(role_peaks.items())]
        extra = [f"cbmc_pid={pid} peak_kb={e['peak_kb']} first_s={e['first_s']} last_s={e['last_s']} "
                 f"peak_s={e['peak_s']} active={re.sub(r'[^A-Za-z0-9_:.,-]', '_', e.get('active', ''))} "
                 f"hint={'_'.join(e['hint'].split())[:60]}"
                 for pid, e in sorted(cbmc.items(), key=lambda pair: -pair[1]["peak_kb"])[:6]]
        extra += [f"solver_pid={pid} cmd={e['name']} peak_kb={e['peak_kb']} first_s={e['first_s']} last_s={e['last_s']} "
                  f"peak_s={e['peak_s']} active={re.sub(r'[^A-Za-z0-9_:.,-]', '_', e.get('active', ''))}"
                  for pid, e in sorted(solver.items(), key=lambda pair: -pair[1]["peak_kb"])[:6]]
        drivers = [f"driver_s={elapsed} rss_kb={rss}" for elapsed, rss in driver_series]
        harnesses = [f"harness_s={elapsed} name={re.sub(r'[^A-Za-z0-9_:.-]', '_', name)}"
                     for elapsed, name in harness_observations]
        # k1g.sh prints at most 8000 bytes. Keep this artifact below that bound so the useful tail records
        # cannot be silently clipped by the reader; preserve complete lines and all legacy command rows.
        size = sum(len(line.encode()) + 1 for line in lines)
        for line in extra:
            if size + len(line.encode()) + 1 <= 6500:
                lines.append(line)
                size += len(line.encode()) + 1
        for i in range(max(len(drivers), len(harnesses))):
            for records in (drivers, harnesses):
                if i < len(records):
                    line = records[i]
                    if size + len(line.encode()) + 1 <= 6500:
                        lines.append(line)
                        size += len(line.encode()) + 1
        tmp = out.with_name(out.name + ".tmp")
        tmp.write_text("\n".join(lines) + "\n")
        tmp.replace(out)
        if stop or (max_seconds is not None and time.monotonic() - t0 >= max_seconds):
            cgroup = Path("/sys/fs/cgroup")
            cgroup_events_end = _cgroup_events()
            for filename in ("memory.current", "memory.peak", "memory.events"):
                try:
                    if filename == "memory.events":
                        for key, value in cgroup_events_end.items():
                            lines.append(f"cgroup_event_{key}={value}")
                            lines.append(f"cgroup_event_delta_{key}={value - cgroup_events_start.get(key, value)}")
                        continue
                    content = (cgroup / filename).read_text().strip()
                    if content.isdigit():
                        lines.append(f"cgroup_{filename.replace('.', '_')}={content}")
                except OSError:
                    pass
            try:
                dmesg = subprocess.run(["dmesg", "--ctime"], capture_output=True, text=True, timeout=3, check=False)
                oom_lines = [line.strip() for line in dmesg.stdout.splitlines()
                             if re.search(r"(?i)(oom-kill|out of memory|killed process)", line)]
                lines.append("dmesg_oom=" + (" | ".join(oom_lines[-3:])[:700] if oom_lines else
                                               ("unreadable" if dmesg.returncode else "none_seen")))
            except (OSError, subprocess.TimeoutExpired):
                lines.append("dmesg_oom=unavailable")
            trailer = [line for line in lines if line.startswith(("cgroup_", "dmesg_oom="))]
            body = [line for line in lines if not line.startswith(("cgroup_", "dmesg_oom="))]
            clipped = False
            while len(("\n".join(body + trailer) + "\n").encode()) > 7800 and len(body) > 5:
                body.pop()
                clipped = True
            if clipped:
                body.append("sampler_records_truncated=true")
            lines = body + trailer
            out.write_text("\n".join(lines) + "\n")
            if harness_out is not None:
                finalize_process_records(process_records)
                harness_out.write_text("".join(json.dumps(record, sort_keys=True) + "\n"
                                                    for record in sorted(process_records.values(), key=lambda r: (-r.get("peak_kb", 0), int(r["pid"])))))
            return
        deadline = time.monotonic() + interval
        while not stop and time.monotonic() < deadline:
            time.sleep(min(0.2, interval))


def ledger(builds: Any, prices: dict[str, float] | None = None) -> tuple[int, float, float]:
    """Pool minutes of a `gcloud builds list --format=json` result: (builds, used, reserved). A finished build
    counts start..finish rounded up (none if it never started); an unfinished one, queued or running, reserves
    its full timeout. With `prices` (pool resource name -> USD per minute) each build's minutes are priced by
    the pool it ran in, and a build in any other pool raises. Anything unreadable raises, so that dispatch
    fails closed."""
    def ts(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(builds, list):
        raise ValueError("build list must be a JSON array")
    used = reserved = 0
    for b in builds:
        rate = 1
        if prices is not None:
            pool = ((b.get("options") or {}).get("pool") or {}).get("name")
            if pool not in prices:
                raise ValueError(f"build {b.get('id')} ran in pool {pool!r}, which has no price")
            rate = prices[pool]
        if b.get("finishTime"):
            if b.get("startTime"):
                used += math.ceil((ts(b["finishTime"]) - ts(b["startTime"])).total_seconds() / 60) * rate
            continue
        timeout = b.get("timeout")
        if not isinstance(timeout, str) or not re.fullmatch(r"\d+(\.\d+)?s", timeout):
            raise ValueError(f"unfinished build {b.get('id')} has unreadable timeout {timeout!r}")
        reserved += math.ceil(float(timeout[:-1]) / 60) * rate
    return len(builds), used, reserved


def ledger_selected(builds: Any, ids: list[str], prices: dict[str, float]) -> tuple[int, float, float]:
    """Price exactly the requested builds; reject duplicate inputs or ambiguous/missing build records."""
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("selected build IDs must be non-empty and unique")
    if not prices:
        raise ValueError("selected build budget requires explicit pool prices")
    if not isinstance(builds, list):
        raise ValueError("build list must be a JSON array")
    if len(builds) >= 1000:
        raise ValueError("1000 or more builds listed; selected budget may undercount")
    selected = []
    for build_id in ids:
        matches = [b for b in builds if isinstance(b, dict) and b.get("id") == build_id]
        if len(matches) != 1:
            raise ValueError(f"build ID {build_id} found {len(matches)} times in ledger; expected exactly once")
        selected.append(matches[0])
    return ledger(selected, prices)


INVENTORY_SCHEMA = "kani-k1-ordinary-inventory-v1"


def extract_inventory(listing: Any) -> list[str]:
    """Match scripts/run-kani.sh get_harnesses extraction, then retain names in the verify module."""
    if not isinstance(listing, dict) or listing.get("file-version") != "0.1":
        raise ValueError("kani list JSON file-version must be 0.1")
    names: list[str] = []
    for section in ("standard-harnesses", "contract-harnesses"):
        groups = listing.get(section)
        if not isinstance(groups, dict):
            raise ValueError(f"kani list JSON missing {section} object")
        for values in groups.values():
            if not isinstance(values, list) or any(not isinstance(name, str) for name in values):
                raise ValueError(f"kani list JSON {section} entries must be arrays of names")
            names.extend(name for name in values if name.startswith(HARNESS_PREFIX))
    if any(not HARNESS_RE.fullmatch(name) for name in names):
        raise ValueError("kani list returned a verify harness name outside the accepted full-name format")
    if len(names) != len(set(names)):
        raise ValueError("kani list returned duplicate verify harness names")
    if not names:
        raise ValueError("kani list returned no ordinary verify harnesses")
    return names


def write_inventory(listing: Any, request_text: str, head_sha: str, kani_commit: str, build_id: str,
                    out: Path) -> None:
    request = validate_request(json.loads(request_text))
    if request.get("inventory") is not True:
        raise ValueError("inventory artifact requires request inventory=true")
    names = extract_inventory(listing)
    name_text = "\n".join(names) + "\n"
    fields = [f"schema={INVENTORY_SCHEMA}", f"request_id={request['request_id']}",
              f"request_sha256={hashlib.sha256(request_text.encode()).hexdigest()}", f"build_id={build_id}",
              f"head_sha={head_sha}", f"kani_commit={kani_commit}", f"count={len(names)}",
              f"names_sha256={hashlib.sha256(name_text.encode()).hexdigest()}"]
    out.write_text("\n".join(fields) + "\n\n" + name_text)


def _page_bounds(total: int, offset: int, count: int) -> None:
    if type(offset) is not int or type(count) is not int or offset < 0 or not 1 <= count <= 80:
        raise ValueError("offset must be non-negative and count must be 1..80")
    if offset > total:
        raise ValueError(f"offset {offset} exceeds total {total}")


def summary_page(summary: dict[str, Any], offset: int, count: int) -> str:
    rows = summary.get("harnesses")
    if not isinstance(rows, list):
        raise ValueError("summary has no harnesses array")
    _page_bounds(len(rows), offset, count)
    end = min(offset + count, len(rows))
    lines = [f"request_id={((summary.get('request') or {}).get('request_id', '?'))}",
             f"request_sha256={summary.get('request_sha256')}", f"build_id={(summary.get('run') or {}).get('id', '')}",
             f"head_sha={summary.get('head_sha')}", f"total={len(rows)}", f"offset={offset}", f"count={end - offset}",
             f"next_offset={end if end < len(rows) else 'done'}", "name\tstatus\ttime_s\tchecks\tcovers"]
    for row in rows[offset:end]:
        checks = "" if row.get("checks_total") is None else f"{row.get('checks_failed')}/{row['checks_total']}"
        covers = "" if row.get("covers_total") is None else f"{row.get('covers_satisfied')}/{row['covers_total']}"
        lines.append(f"{row.get('name', '')}\t{row.get('status', '')}\t{row.get('time_s', '')}\t{checks}\t{covers}")
    return "\n".join(lines) + "\n"


def inventory_page(inventory_text: str, summary: dict[str, Any], offset: int, count: int) -> str:
    header, sep, body = inventory_text.partition("\n\n")
    if not sep:
        raise ValueError("inventory file has no names section")
    fields = dict(line.split("=", 1) for line in header.splitlines() if "=" in line)
    names = body.splitlines()
    try:
        total = int(fields["count"])
    except (KeyError, ValueError) as exc:
        raise ValueError("inventory count missing or invalid") from exc
    canonical = "\n".join(names) + ("\n" if names else "")
    if fields.get("schema") != INVENTORY_SCHEMA or total != len(names) \
            or hashlib.sha256(canonical.encode()).hexdigest() != fields.get("names_sha256"):
        raise ValueError("inventory schema/count/names SHA-256 mismatch")
    request = summary.get("request") or {}
    run = summary.get("run") or {}
    if request.get("inventory") is not True:
        raise ValueError("summary is not bound to an inventory=true request")
    bindings = {"request_id": request.get("request_id"), "request_sha256": summary.get("request_sha256"),
                "build_id": run.get("id"), "head_sha": summary.get("head_sha"),
                "kani_commit": summary.get("kani_commit")}
    for key, expected in bindings.items():
        if fields.get(key) != str(expected or ""):
            raise ValueError(f"inventory {key} does not match summary")
    _page_bounds(total, offset, count)
    end = min(offset + count, total)
    lines = [f"request_id={fields['request_id']}", f"request_sha256={fields['request_sha256']}",
             f"build_id={fields['build_id']}", f"head_sha={fields['head_sha']}",
             f"kani_commit={fields['kani_commit']}", f"inventory_sha256={hashlib.sha256(inventory_text.encode()).hexdigest()}",
             f"names_sha256={fields['names_sha256']}",
             f"total={total}", f"offset={offset}", f"count={end - offset}",
             f"next_offset={end if end < total else 'done'}", *names[offset:end]]
    return "\n".join(lines) + "\n"


def parse_inventory_artifact(inventory_text: str, summary: dict[str, Any]) -> dict[str, Any]:
    """Validate a completed inventory artifact against its run summary and return bounded metadata."""
    header, sep, body = inventory_text.partition("\n\n")
    if not sep:
        raise ValueError("inventory artifact has no names section")
    fields = dict(line.split("=", 1) for line in header.splitlines() if "=" in line)
    names = body.splitlines()
    name_text = "\n".join(names) + ("\n" if names else "")
    if (fields.get("schema") != INVENTORY_SCHEMA or fields.get("count") != str(len(names))
            or not names or hashlib.sha256(name_text.encode()).hexdigest() != fields.get("names_sha256")):
        raise ValueError("inventory schema/count/names SHA-256 mismatch")
    request = summary.get("request") or {}
    run = summary.get("run") or {}
    bindings = {"request_id": request.get("request_id"), "request_sha256": summary.get("request_sha256"),
                "build_id": run.get("id"), "head_sha": summary.get("head_sha"),
                "kani_commit": summary.get("kani_commit")}
    for key, expected in bindings.items():
        if fields.get(key) != str(expected or ""):
            raise ValueError(f"inventory {key} does not match run")
    return {"count": len(names), "names_sha256": fields["names_sha256"],
            "artifact_sha256": hashlib.sha256(inventory_text.encode()).hexdigest()}


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
              peaks_tracked: bool = False, inventory_text: str | None = None) -> dict[str, Any]:
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
    if peaks is not None and peaks.get("records_truncated"):
        summary["notes"].append("memory sampler detail rows truncated to preserve cgroup/OOM tail records")
    if peaks is not None and peaks["commands"] and summary["resources"]["max_rss_kb_whole_run"]:
        top, exact = peaks["commands"][0]["peak_kb"], summary["resources"]["max_rss_kb_whole_run"]
        if exact > top:
            # The sampler misses growth in a process's last interval; time -v sees the largest child exactly.
            summary["notes"].append(f"time -v max RSS {exact} KiB exceeds the largest sampled command peak {top} KiB: "
                                    "a process grew between samples; use the time -v value as the true single-process peak")
    if memcap is not None:
        if memcap["state"] not in ("ENFORCED", "MACHINE"):
            summary["notes"].append(f"verify memory cap {memcap['state']}: {memcap['reason'] or 'no reason recorded'}")
        if memcap["oom_kill"]:
            summary["notes"].append(f"verify cgroup OOM killer fired {memcap['oom_kill']} time(s)")
        if memcap["state"] in ("ENFORCED", "MACHINE") and memcap["swap"] != "off":
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
    summary["request"]["kani_jobs"] = request.get("kani_jobs", 1)
    if request["kind"] == "autoharness":
        summary["request"]["kani_jobs"] = 3
    summary["request"]["uninit_checks"] = request.get("uninit_checks", False)
    summary["request"]["controls"] = request.get("controls", False)
    summary["request"]["inventory"] = request.get("inventory", False)
    if request.get("controls"):
        summary["notes"].append(f"--cfg {CONTROLS_CFG} on: opt-in control/mutant harnesses compiled, outside the CI set")
    if request.get("uninit_checks"):
        summary["notes"].append("-Z uninit-checks on: not in the organizers' CI flags, evidence outside CI")
    if request["kind"] == "resource":
        summary["notes"].append("kind resource on 32 GB: memory/time data only, never a PASS or measurement result")
    if request["kind"] != "partition" and request.get("kani_jobs", 1) > 1:
        summary["notes"].append(f"{request['kani_jobs']} harnesses verified concurrently: times and memory are of the "
                                "shared run, not single-harness measurements")
    if request["kind"] == "partition":
        summary["request"]["worker_index"] = request["worker_index"]
        summary["request"]["worker_total"] = request["worker_total"]
        summary["request"]["kani_jobs"] = request.get("kani_jobs")
        if log_text is None:
            summary["status"] = "RUNNER_ERROR"
            summary["notes"].append(f"Kani log missing (build {build_outcome})")
            return summary
        parsed = parse_log(log_text)
        summary["errors"], summary["errors_truncated"] = parsed["errors"], parsed["errors_truncated"]
        summary["complete_line"] = parsed["complete_line"]
        return summarize_partition(summary, request, parsed, exit_code, log_text)
    if request["kind"] == "inventory":
        parsed_log = parse_log(log_text or "")
        summary["errors"], summary["errors_truncated"] = parsed_log["errors"], parsed_log["errors_truncated"]
        if exit_code != 0:
            summary["status"] = "TOOL_ERROR" if log_text else "RUNNER_ERROR"
            summary["notes"].append(f"Kani list did not complete successfully (exit {exit_code})")
            return summary
        if inventory_text is None:
            summary["status"] = "PARTIAL"
            summary["notes"].append("Kani list exited successfully but the inventory artifact is missing")
            return summary
        try:
            summary["inventory_result"] = parse_inventory_artifact(inventory_text, summary)
        except ValueError as exc:
            summary["status"] = "INCONSISTENT"
            summary["inconsistencies"].append(str(exc))
            return summary
        summary["status"] = "COMPLETE"
        summary["expectation_met"] = True
        summary["measurement_ok"] = None
        return summary
    if request["kind"] == "autoharness":
        if log_text is None:
            summary["status"] = "RUNNER_ERROR"
            summary["notes"].append(f"autoharness log missing (build {build_outcome})")
            return summary
        parsed = parse_log(log_text)
        summary["errors"], summary["errors_truncated"] = parsed["errors"], parsed["errors_truncated"]
        summary["complete_line"] = parsed["complete_line"]
        rows = []
        for block in parsed["blocks"]:
            status = _block_status(block)
            missing = status == "UNKNOWN" or (status in ("SUCCESS", "FAILED") and block["time_s"] is None)
            rows.append({"name": block["name"], "expect": "workflow", "status":
                         "MISSING_RESULT" if missing else status, "reported_status": status if missing else None,
                         "time_s": block["time_s"], "checks_failed": block["checks_failed"],
                         "checks_total": block["checks_total"], "unreachable": block["unreachable"],
                         "covers_satisfied": block["covers_satisfied"], "covers_total": block["covers_total"],
                         "failed_checks": block["failed_checks"], "failed_located": block["failed_located"],
                         "failed_checks_truncated": block["failed_checks_truncated"]})
        summary["harnesses"] = rows
        summary["started_count"] = len(rows)
        summary["counts"] = {status: sum(row["status"] == status for row in rows)
                              for status in ("SUCCESS", "FAILED", "TIMEOUT", "OUT_OF_MEMORY", "MISSING_RESULT")}
        statuses = [row["status"] for row in rows]
        inconsistencies = summary["inconsistencies"]
        if request.get("kani_jobs", 3) > 1 and parsed["overlaps"]:
            inconsistencies.append(f"{parsed['overlaps']} overlapping worker block(s) under jobs=3")
        if request.get("kani_jobs", 3) > 1 and parsed["orphans"]:
            inconsistencies.append(f"{parsed['orphans']} unprefixed result line(s) under jobs=3")
        complete = parsed["complete_line"]
        if complete is None:
            inconsistencies.append("final 'Complete - …' line missing")
        else:
            if complete["total"] != len(rows):
                inconsistencies.append(f"Kani total {complete['total']} differs from {len(rows)} started harnesses")
            if complete["success"] != sum(s == "SUCCESS" for s in statuses):
                inconsistencies.append(f"Kani success count {complete['success']} differs from parsed successes")
            if complete["failures"] != sum(s in ("FAILED", "TIMEOUT", "OUT_OF_MEMORY") for s in statuses):
                inconsistencies.append(f"Kani failure count {complete['failures']} differs from parsed non-success results")
        if exit_code is None:
            inconsistencies.append("Kani exit code unknown")
        elif complete is not None and (exit_code == 0) != (complete["failures"] == 0):
            inconsistencies.append(f"Kani exit {exit_code} does not match final failure count {complete['failures']}")
        if not rows:
            summary["status"] = "RUNNER_ERROR"
        elif "MISSING_RESULT" in statuses or complete is None:
            summary["status"] = "PARTIAL"
        elif inconsistencies:
            summary["status"] = "INCONSISTENT"
        else:
            summary["status"] = "COMPLETE"
        summary["expectation_met"] = summary["status"] == "COMPLETE" and all(s == "SUCCESS" for s in statuses)
        summary["measurement_ok"] = summary["expectation_met"]
        timed = [row for row in rows if row["time_s"] is not None]
        summary["autoharness"] = {"started_count": len(rows), "counts": summary["counts"],
                                  "sum_verification_time_s": round(sum(row["time_s"] for row in timed), 3),
                                  "timed_count": len(timed),
                                  "slowest": sorted(timed, key=lambda row: (-row["time_s"], row["name"]))[:15]}
        return summary
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
    if request.get("kani_jobs", 1) > 1 and parsed["overlaps"]:
        # Lines are attributed per worker prefix; a worker starting a harness inside its open block would mean
        # the attribution failed.
        inconsistencies.append(f"{parsed['overlaps']} harness block(s) started on a worker before its previous "
                               "block ended under kani_jobs > 1: output may be interleaved")
    if request.get("kani_jobs", 1) > 1 and parsed["orphans"]:
        inconsistencies.append(f"{parsed['orphans']} result line(s) without a worker prefix under kani_jobs > 1: "
                               "they cannot be attributed to a harness")
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
        # MACHINE (Cloud Build 16 GB): no cgroup to count OOM kills; an OOM-killed CBMC is an OUT_OF_MEMORY row
        # and any other killed tool leaves no COMPLETE status, so swap is what remains to check.
        memcap_ok = memcap is None or (memcap["state"] == "ENFORCED" and memcap["oom_kill"] == 0
                                       and memcap["swap"] == "off") or (memcap["state"] == "MACHINE"
                                                                       and memcap["swap"] == "off")
        summary["measurement_ok"] = summary["expectation_met"] and memcap_ok and all(
            r["status"] != "SUCCESS" or (r["time_s"] is not None and r["time_s"] <= MEASUREMENT_LIMIT_SECONDS
                                         and (not request.get("controls") or
                                              ((r["covers_total"] or 0) >= 1 and
                                               r["covers_satisfied"] == r["covers_total"])))
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
    if memcap["state"] == "MACHINE":
        return (f"MACHINE (no cgroup cap; the machine's memory {memcap['max_bytes'] / 2**30 if memcap['max_bytes'] else 0:.2f} GiB "
                f"is the limit), swap {memcap['swap']}")
    gib = lambda b: "?" if b is None else f"{b / 2**30:.2f} GiB"  # noqa: E731
    return (f"{memcap['state']}, limit {gib(memcap['max_bytes'])}, cgroup peak incl. page cache "
            f"{gib(memcap['peak_bytes'])}, OOM kills {memcap['oom_kill']}, swap {memcap['swap']}")


def _peaks_lines(peaks: dict[str, Any] | None) -> list[str]:
    if peaks is None:
        return []
    gib = lambda kb: "?" if kb is None else f"{kb / 2**20:.2f} GiB"  # noqa: E731
    every = "?" if peaks["interval_ms"] is None else f"{peaks['interval_ms'] / 1000:g}"
    peak_time = "?" if peaks.get("total_peak_s") is None else f"{peaks['total_peak_s']} s"
    out = [f"- memory peaks {peaks['state']}: sampled every {every} s, {peaks['samples']} samples, "
           f"largest sampled sum of RSS {gib(peaks['total_rss_peak_kb'])} at {peak_time}; per command (kernel VmHWM; 13 GiB = CircleCI cap, "
           "16 GB = organizers' runner). RSS is process resident memory, not physical RAM use:"]
    for c in peaks["commands"]:
        fit = "≤13 GiB" if c["peak_kb"] <= 13 * 2**20 else ("≤16 GB" if c["peak_kb"] * 1024 <= 16 * 10**9 else ">16 GB")
        peak_at = f", peak sample {c['peak_s']} s" if c.get("peak_s") is not None else ""
        out.append(f"  - `{c['cmd']}` {gib(c['peak_kb'])} ({fit}), seen {c['first_s']}–{c['last_s']} s{peak_at}")
    if peaks.get("commands_truncated"):
        out.append(f"  - …only the {PEAKS_TOP} largest commands listed")
    for role in peaks.get("roles", []):
        role_kb = role.get("simultaneous_rss_peak_kb", "0")
        out.append(f"  - simultaneous {role.get('role', '?')} RSS {gib(int(role_kb))} at {role.get('peak_s', '?')} s")
    for proc in peaks.get("processes", []):
        pid = proc.get("cbmc_pid", proc.get("solver_pid", "?"))
        out.append(f"  - {proc.get('cmd', 'cbmc')} PID {pid}: {gib(int(proc.get('peak_kb', '0')))} peak at {proc.get('peak_s', '?')} s; active `{proc.get('active', '')}`")
    if peaks.get("cgroup_events"):
        out.append("  - cgroup counters: " + ", ".join(f"{k}={v}" for k, v in sorted(peaks["cgroup_events"].items())))
    if peaks.get("dmesg_oom"):
        out.append(f"  - dmesg OOM scan: `{peaks['dmesg_oom']}`")
    return out


def render_md(summary: dict[str, Any]) -> str:
    req = summary["request"] or {}
    res = summary["resources"]
    run = summary.get("run") or {}
    timeout_label = ("whole-job work budget" if req.get("kind") in ("autoharness", "partition", "inventory")
                     else "per-harness timeout")
    timeout_note = ("; per-harness settings from the checked-out workflow"
                    if req.get("kind") == "autoharness" else "")
    lines = [
        f"# K-1 run `{req.get('request_id', '?')}`: {summary['status']}",
        "",
        f"- head `{summary['head_sha']}`, Kani `{summary['kani_commit']}`, request sha256 `{summary['request_sha256']}`",
        f"- run {run.get('id')} attempt {run.get('attempt')}, image {run.get('image_os')} {run.get('image_version')}, build {summary.get('build_outcome')}",
        f"- agent `{req.get('agent')}`, kind `{req.get('kind')}`, runner `{req.get('runner')}`, {timeout_label} {req.get('harness_timeout_minutes')} min{timeout_note}, "
        f"harnesses in parallel {req.get('kani_jobs', 1)}, uninit checks {'on' if req.get('uninit_checks') else 'off'}, "
        f"controls cfg {'on' if req.get('controls') else 'off'}",
        f"- gate: {gate_ok(summary)}; expectation met: {summary['expectation_met']}; measurement ok: {summary['measurement_ok']}; Kani exit {summary['kani_exit_code']}",
        f"- whole run, including compilation: max RSS {res['max_rss_kb_whole_run']} KiB, wall {res['wall_whole_run']} ({res['time_file']})",
        f"- verify memory cap: {_memcap_line(res.get('memcap'))}",
        *_peaks_lines(res.get("peaks")),
        "",
        "| harness | expect | status | time s | failed/total checks | unreachable | covers |",
        "|---|---|---|---|---|---|---|",
    ]
    inventory = summary.get("inventory_result")
    if inventory is not None:
        lines[8:8] = [f"- ordinary verify inventory: {inventory['count']} names; names SHA-256 `{inventory['names_sha256']}`",
                       f"- inventory artifact SHA-256: `{inventory['artifact_sha256']}`", ""]
    auto = summary.get("autoharness")
    if auto is not None:
        lines[8:8] = [f"- autoharness started: {auto['started_count']}; results: {auto['counts']}; "
                      f"sum Verification Time: {auto['sum_verification_time_s']} s over {auto['timed_count']} timed harnesses",
                      ""]
    part = summary.get("partition")
    if part is not None:
        lines[-2:] = [
            f"Partition {part['worker_index']}/{part['worker_total']} (organizers' layout), KANI_JOBS "
            f"{part['kani_jobs'] if part['kani_jobs'] is not None else 'unset (-j)'}: {part['harness_count']} harnesses, "
            f"{part['smallsort_kani_k1_count']} of them smallsort kani_k1; statuses {part['counts']}; "
            f"sum of Verification Time {part['sum_verification_time_s']} s (concurrent runs overlap; wall is above)",
            "", f"Slowest {len(part['slowest'])}:", "", "| harness | status | time s |", "|---|---|---|",
            *[f"| {r['name']} | {r['status']} | {r['time_s']} |" for r in part["slowest"]],
        ]
        if part["failures"]:
            lines += ["", "Not SUCCESS" + (" (truncated)" if part["failures_truncated"] else "") + ":"]
            lines += [f"- {f['name']}: {f['status']}; {f['first_failed_check'] or 'no failed check'}" for f in part["failures"]]
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
    v.add_argument("--autoharness-script-out", help="extract the literal workflow command for kind autoharness")
    v.add_argument("--runner-out")
    v.add_argument("--rustflags-out", help="write the RUSTFLAGS value the request needs (empty line if none)")
    v.add_argument("--partition-out", help="write the worker environment of kind partition (empty if none)")
    v.add_argument("--max-total-minutes", type=int, default=None)
    v.add_argument("--require-runner", action="append", default=[],
                   help="accepted runner value of this lane (repeatable); any other is rejected")
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
    s.add_argument("--inventory", help="completed inventory artifact, required to gate kind inventory")
    s.add_argument("--bind", action="append", default=[], help="file whose SHA-256 is recorded (repeatable)")
    s.add_argument("--out-dir", required=True)
    g = sub.add_parser("gate")
    g.add_argument("summary")
    led = sub.add_parser("ledger")
    led.add_argument("--price", action="append", default=[], metavar="POOL=USD",
                     help="per-minute price of a worker pool (repeatable); prices the ledger in USD")
    led.add_argument("--id", action="append", default=[], help="price only this build UUID (repeatable)")
    inv = sub.add_parser("write-inventory")
    inv.add_argument("--listing", required=True)
    inv.add_argument("--request", required=True)
    inv.add_argument("--head-sha", required=True)
    inv.add_argument("--kani-commit", required=True)
    inv.add_argument("--build-id", required=True)
    inv.add_argument("--out", required=True)
    ps = sub.add_parser("page-summary")
    ps.add_argument("summary")
    ps.add_argument("offset", type=int)
    ps.add_argument("count", type=int)
    pi = sub.add_parser("page-inventory")
    pi.add_argument("inventory")
    pi.add_argument("summary")
    pi.add_argument("offset", type=int)
    pi.add_argument("count", type=int)
    m = sub.add_parser("sample-mem")
    m.add_argument("--out", required=True)
    m.add_argument("--interval", type=float, default=2.0)
    m.add_argument("--max-seconds", type=float)
    m.add_argument("--log", help="Kani output file; record up to 50 Checking harness lines with sampler elapsed time")
    m.add_argument("--harness-out", help="write per-PID CBMC/solver RSS attribution JSONL")
    m.add_argument("--head-sha")
    m.add_argument("--kani-commit")
    m.add_argument("--build-id")
    a = ap.parse_args(argv)
    if a.cmd == "ledger":
        try:
            prices = None
            if a.price:
                prices = {}
                for item in a.price:
                    pool, _, usd = item.rpartition("=")
                    if not pool or not math.isfinite(float(usd)) or float(usd) <= 0:
                        raise ValueError(f"bad --price {item!r}")
                    prices[pool] = float(usd)
            builds = json.load(sys.stdin)
            count, used, reserved = ledger_selected(builds, a.id, prices) if a.id else ledger(builds, prices)
            print(count, *((f"{used:.4f}", f"{reserved:.4f}") if prices else (used, reserved)))
        except (ValueError, TypeError, AttributeError) as exc:
            print(f"ledger: {exc}", file=sys.stderr)
            return 2
        return 0
    if a.cmd == "write-inventory":
        try:
            write_inventory(json.loads(Path(a.listing).read_text()), Path(a.request).read_text(), a.head_sha,
                            a.kani_commit, a.build_id, Path(a.out))
        except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
            print(f"write-inventory: {exc}", file=sys.stderr)
            return 2
        return 0
    if a.cmd == "page-summary":
        try:
            print(summary_page(json.loads(Path(a.summary).read_text()), a.offset, a.count), end="")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"page-summary: {exc}", file=sys.stderr)
            return 2
        return 0
    if a.cmd == "page-inventory":
        try:
            output = inventory_page(Path(a.inventory).read_text(), json.loads(Path(a.summary).read_text()),
                                    a.offset, a.count)
            print(output, end="")
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"page-inventory: {exc}", file=sys.stderr)
            return 2
        return 0
    if a.cmd == "sample-mem":
        sample_memory(Path(a.out), a.interval, a.max_seconds, log=Path(a.log) if a.log else None,
                      harness_out=Path(a.harness_out) if a.harness_out else None,
                      head_sha=a.head_sha, kani_commit=a.kani_commit, build_id=a.build_id)
        return 0
    if a.cmd == "validate":
        try:
            request = validate_request(json.loads(Path(a.request).read_text()), a.max_total_minutes)
            if a.require_runner and request["runner"] not in a.require_runner:
                raise RequestError(f"this lane runs only runner(s) {sorted(a.require_runner)}, request asks {request['runner']}")
        except (OSError, json.JSONDecodeError, RequestError) as exc:
            print(f"REQUEST_INVALID: {exc}", file=sys.stderr)
            return 2
        Path(a.args_out).write_text("\n".join(kani_args(request)) + "\n")
        if request["kind"] == "autoharness" and a.autoharness_script_out:
            Path(a.autoharness_script_out).write_text(extract_autoharness_command(Path(".github/workflows/kani.yml").read_text()))
        elif a.autoharness_script_out:
            Path(a.autoharness_script_out).write_text("")
        if a.runner_out:
            Path(a.runner_out).write_text(request["runner"] + "\n")
        if a.partition_out:
            Path(a.partition_out).write_text("".join(line + "\n" for line in partition_env(request)))
        if a.rustflags_out:
            Path(a.rustflags_out).write_text((f"--cfg {CONTROLS_CFG}" if request.get("controls") else "") + "\n")
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
                            _read_optional(a.peaks), a.peaks is not None, _read_optional(a.inventory))
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
