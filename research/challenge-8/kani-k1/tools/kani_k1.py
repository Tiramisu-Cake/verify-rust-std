#!/usr/bin/env python3
"""Run-request validation and bounded result summary for the Kani K-1 experiment lane.

Subcommands
  validate REQUEST --args-out FILE      check the request, write one Kani argument per line
  summarize --request R --log L ...      parse terse Kani output into summary.json/summary.md
  gate SUMMARY                           exit 0 iff the run completed and met every expectation

Standard library only. No network, no proof tools. The summary is the agent-facing evidence:
statuses, times, failed checks and compile errors are bounded and every truncation is explicit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA = "kani-k1-run-request-v1"
SUMMARY_SCHEMA = "kani-k1-run-summary-v1"
AGENTS = {"k1-merge", "k1-network", "coordinator"}
KINDS = {"measurement", "diagnostic"}
EXPECT = {"SUCCESS", "FAILED"}
HARNESS_PREFIX = "slice::sort::shared::smallsort::kani_k1::"
HARNESS_RE = re.compile(r"^slice::sort::shared::smallsort::kani_k1::[A-Za-z0-9_]+(::[A-Za-z0-9_]+)*$")
REQUEST_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
REQUEST_KEYS = {"schema", "request_id", "agent", "kind", "purpose", "runner", "harness_timeout_minutes", "harnesses"}
RUNNERS = {"ubuntu-latest", "macos-latest"}
HARNESS_KEYS = {"name", "expect"}
MAX_HARNESSES = 20
MAX_TIMEOUT_MINUTES = 30
MEASUREMENT_TIMEOUT_MINUTES = 10
MAX_TOTAL_MINUTES = 150
MEASUREMENT_LIMIT_SECONDS = 600.0

MAX_FAILED_CHECKS = 20
MAX_LINE_CHARS = 400
MAX_COMPILE_LINES = 80
MAX_MD_BYTES = 12000

CHECKING_RE = re.compile(r"^(?:Thread \d+: )?Checking harness (\S+?)\.\.\.\s*$")
STATUS_RE = re.compile(r"^VERIFICATION:-\s*(SUCCESSFUL|FAILED)\b(.*)$")
TIME_RE = re.compile(r"^Verification Time:\s*([0-9]+(?:\.[0-9]+)?)s\s*$")
CHECKS_RE = re.compile(r"^\s*\*\*\s*(\d+) of (\d+) failed(?:\s*\((\d+) unreachable\))?")
COVER_RE = re.compile(r"^\s*\*\*\s*(\d+) of (\d+) cover properties satisfied")
FAILED_CHECK_RE = re.compile(r"^Failed Checks:\s*(.*)$")
COMPLETE_RE = re.compile(r"^Complete - (\d+) successfully verified harness(?:es)?, (\d+) failures?, (\d+) total\.")
TIMEOUT_MARK = "timed out"
COMPILE_ERROR_RE = re.compile(r"^error(\[E\d{4}\])?:")
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


def validate_request(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise RequestError("request must be a JSON object")
    extra = set(data) - REQUEST_KEYS
    missing = REQUEST_KEYS - set(data)
    if extra:
        raise RequestError(f"unknown request keys: {sorted(extra)}")
    if missing:
        raise RequestError(f"missing request keys: {sorted(missing)}")
    if data["schema"] != SCHEMA:
        raise RequestError(f"schema must be {SCHEMA}")
    if not isinstance(data["request_id"], str) or not REQUEST_ID_RE.match(data["request_id"]):
        raise RequestError("request_id must match [a-z0-9][a-z0-9._-]{0,63}")
    if data["agent"] not in AGENTS:
        raise RequestError(f"agent must be one of {sorted(AGENTS)}")
    if data["kind"] not in KINDS:
        raise RequestError(f"kind must be one of {sorted(KINDS)}")
    purpose = data["purpose"]
    if not isinstance(purpose, str) or not purpose.strip() or len(purpose) > 300 or "\n" in purpose:
        raise RequestError("purpose must be one non-empty line of at most 300 characters")
    if data["runner"] not in RUNNERS:
        raise RequestError(f"runner must be one of {sorted(RUNNERS)}")
    timeout = data["harness_timeout_minutes"]
    if type(timeout) is not int or not 1 <= timeout <= MAX_TIMEOUT_MINUTES:
        raise RequestError(f"harness_timeout_minutes must be an integer 1..{MAX_TIMEOUT_MINUTES}")
    if data["kind"] == "measurement" and timeout != MEASUREMENT_TIMEOUT_MINUTES:
        raise RequestError("a measurement run must use harness_timeout_minutes = 10")
    harnesses = data["harnesses"]
    if not isinstance(harnesses, list) or not 1 <= len(harnesses) <= MAX_HARNESSES:
        raise RequestError(f"harnesses must be a list of 1..{MAX_HARNESSES} entries")
    names: list[str] = []
    for entry in harnesses:
        if not isinstance(entry, dict) or set(entry) != HARNESS_KEYS:
            raise RequestError("each harness entry must be exactly {name, expect}")
        name, expect = entry["name"], entry["expect"]
        if not isinstance(name, str) or not HARNESS_RE.match(name):
            raise RequestError(f"harness name must be a full path under {HARNESS_PREFIX}: {name!r}")
        if expect not in EXPECT:
            raise RequestError(f"expect must be SUCCESS or FAILED: {name}")
        names.append(name)
    if len(set(names)) != len(names):
        raise RequestError("duplicate harness names")
    if len(names) * timeout > MAX_TOTAL_MINUTES:
        raise RequestError(f"harness count × timeout exceeds {MAX_TOTAL_MINUTES} minutes")
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
            "failed_checks_truncated": False, "timed_out": False}


def parse_log(text: str) -> dict[str, Any]:
    blocks: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    compile_lines: list[str] = []
    compile_truncated = False
    complete = None
    in_error = 0
    for raw in text.splitlines():
        line = raw.rstrip("\r")
        m = CHECKING_RE.match(line)
        if m:
            current = _new_block(m.group(1))
            blocks.append(current)
            in_error = 0
            continue
        if COMPILE_ERROR_RE.match(line):
            in_error = 8
        if in_error:
            if len(compile_lines) < MAX_COMPILE_LINES:
                compile_lines.append(_clip(line))
            else:
                compile_truncated = True
            in_error -= 1
        m = COMPLETE_RE.match(line)
        if m:
            complete = {"success": int(m.group(1)), "failures": int(m.group(2)), "total": int(m.group(3))}
            continue
        if current is None:
            continue
        if TIMEOUT_MARK in line:
            current["timed_out"] = True
        m = STATUS_RE.match(line)
        if m:
            current["status_line"] = m.group(1)
            continue
        m = TIME_RE.match(line)
        if m:
            current["time_s"] = float(m.group(1))
            continue
        m = CHECKS_RE.match(line)
        if m:
            current["checks_failed"], current["checks_total"] = int(m.group(1)), int(m.group(2))
            current["unreachable"] = int(m.group(3)) if m.group(3) is not None else 0
            continue
        m = COVER_RE.match(line)
        if m:
            current["covers_satisfied"], current["covers_total"] = int(m.group(1)), int(m.group(2))
            continue
        m = FAILED_CHECK_RE.match(line)
        if m:
            if len(current["failed_checks"]) < MAX_FAILED_CHECKS:
                current["failed_checks"].append(_clip(m.group(1)))
            else:
                current["failed_checks_truncated"] = True
            continue
        if line.startswith(" File: ") and current["failed_checks"] and not current["failed_checks_truncated"]:
            current["failed_checks"][-1] = _clip(current["failed_checks"][-1] + " @" + line[len(" File:"):])
    return {"blocks": blocks, "compile_errors": compile_lines, "compile_errors_truncated": compile_truncated,
            "complete_line": complete}


def _block_status(block: dict[str, Any]) -> str:
    if block["timed_out"]:
        return "TIMEOUT"
    if block["status_line"] == "SUCCESSFUL":
        return "SUCCESS"
    if block["status_line"] == "FAILED":
        return "FAILED"
    return "UNKNOWN"


def parse_time_file(text: str | None) -> dict[str, Any]:
    if text is None:
        return {"max_rss_kb": None, "wall": None, "time_file": "MISSING"}
    rss, wall = RSS_RE.search(text), WALL_RE.search(text)
    if rss or wall:
        return {"max_rss_kb": int(rss.group(1)) if rss else None, "wall": wall.group(1) if wall else None,
                "time_file": "PARSED"}
    rss, real = MAC_RSS_RE.search(text), MAC_REAL_RE.search(text)
    if rss or real:
        return {"max_rss_kb": int(rss.group(1)) // 1024 if rss else None, "wall": f"{real.group(1)}s" if real else None,
                "time_file": "PARSED"}
    return {"max_rss_kb": None, "wall": None, "time_file": "UNPARSED"}


def summarize(request_text: str | None, log_text: str | None, time_text: str | None, exit_code: int | None,
              head_sha: str | None, kani_commit: str | None, request_error: str | None = None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "schema": SUMMARY_SCHEMA, "head_sha": head_sha, "kani_commit": kani_commit,
        "request_sha256": hashlib.sha256(request_text.encode()).hexdigest() if request_text is not None else None,
        "kani_exit_code": exit_code, "request": None, "status": None, "expectation_met": False,
        "measurement_ok": None, "harnesses": [], "unrequested_blocks": [], "compile_errors": [],
        "compile_errors_truncated": False, "complete_line": None, "resources": parse_time_file(time_text),
        "notes": [],
    }
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
    if log_text is None:
        summary["status"] = "RUNNER_ERROR"
        summary["notes"].append("Kani log missing: setup or runner failed before verification output")
        summary["harnesses"] = [{"name": e["name"], "expect": e["expect"], "status": "NOT_RUN"} for e in request["harnesses"]]
        return summary
    parsed = parse_log(log_text)
    summary["compile_errors"] = parsed["compile_errors"]
    summary["compile_errors_truncated"] = parsed["compile_errors_truncated"]
    summary["complete_line"] = parsed["complete_line"]
    by_name: dict[str, dict[str, Any]] = {}
    for block in parsed["blocks"]:
        if block["name"] in by_name:
            summary["notes"].append(f"harness reported more than once, last block kept: {block['name']}")
        by_name[block["name"]] = block
    requested = {e["name"] for e in request["harnesses"]}
    summary["unrequested_blocks"] = sorted(n for n in by_name if n not in requested)
    rows = []
    for entry in request["harnesses"]:
        block = by_name.get(entry["name"])
        if block is None:
            rows.append({"name": entry["name"], "expect": entry["expect"], "status": "NOT_RUN"})
            continue
        status = _block_status(block)
        row = {"name": entry["name"], "expect": entry["expect"], "status": status, "time_s": block["time_s"],
               "checks_failed": block["checks_failed"], "checks_total": block["checks_total"],
               "unreachable": block["unreachable"], "covers_satisfied": block["covers_satisfied"],
               "covers_total": block["covers_total"], "failed_checks": block["failed_checks"],
               "failed_checks_truncated": block["failed_checks_truncated"]}
        row["covers_all_satisfied"] = (None if block["covers_total"] is None
                                       else block["covers_satisfied"] == block["covers_total"])
        rows.append(row)
    summary["harnesses"] = rows
    statuses = [r["status"] for r in rows]
    if not parsed["blocks"] and parsed["compile_errors"]:
        summary["status"] = "COMPILE_ERROR"
    elif any(s in ("NOT_RUN", "UNKNOWN") for s in statuses):
        summary["status"] = "PARTIAL"
    else:
        summary["status"] = "COMPLETE"
    summary["expectation_met"] = summary["status"] == "COMPLETE" and all(r["status"] == r["expect"] for r in rows)
    if request["kind"] == "measurement":
        summary["measurement_ok"] = summary["expectation_met"] and all(
            r["status"] != "SUCCESS" or (r["time_s"] is not None and r["time_s"] <= MEASUREMENT_LIMIT_SECONDS
                                         and r.get("covers_all_satisfied") is not False)
            for r in rows)
    if exit_code not in (None, 0) and summary["status"] == "COMPLETE" and all(s == "SUCCESS" for s in statuses):
        summary["notes"].append(f"Kani exited {exit_code} although every requested harness succeeded")
    return summary


def render_md(summary: dict[str, Any]) -> str:
    req = summary["request"] or {}
    res = summary["resources"]
    lines = [
        f"# K-1 run `{req.get('request_id', '?')}`: {summary['status']}",
        "",
        f"- head `{summary['head_sha']}`, Kani `{summary['kani_commit']}`, request sha256 `{summary['request_sha256']}`",
        f"- agent `{req.get('agent')}`, kind `{req.get('kind')}`, runner `{req.get('runner')}`, per-harness timeout {req.get('harness_timeout_minutes')} min",
        f"- expectation met: {summary['expectation_met']}; measurement ok: {summary['measurement_ok']}; Kani exit {summary['kani_exit_code']}",
        f"- max RSS {res['max_rss_kb']} KiB, wall {res['wall']} ({res['time_file']})",
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
            lines += [f"- {c}" for c in r["failed_checks"]]
    if summary["compile_errors"]:
        lines += ["", "Compile errors" + (" (truncated)" if summary["compile_errors_truncated"] else "") + ":", "```"]
        lines += summary["compile_errors"] + ["```"]
    if summary["unrequested_blocks"]:
        lines += ["", "Unrequested harness blocks: " + ", ".join(summary["unrequested_blocks"])]
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
    s = sub.add_parser("summarize")
    s.add_argument("--request", required=True)
    s.add_argument("--log")
    s.add_argument("--time")
    s.add_argument("--exit-code")
    s.add_argument("--head-sha")
    s.add_argument("--kani-commit")
    s.add_argument("--request-error")
    s.add_argument("--out-dir", required=True)
    g = sub.add_parser("gate")
    g.add_argument("summary")
    a = ap.parse_args(argv)
    if a.cmd == "validate":
        try:
            request = validate_request(json.loads(Path(a.request).read_text()))
        except (OSError, json.JSONDecodeError, RequestError) as exc:
            print(f"REQUEST_INVALID: {exc}", file=sys.stderr)
            return 2
        Path(a.args_out).write_text("\n".join(kani_args(request)) + "\n")
        if a.runner_out:
            Path(a.runner_out).write_text(request["runner"] + "\n")
        print(f"request {request['request_id']}: {len(request['harnesses'])} harness(es) accepted")
        return 0
    if a.cmd == "summarize":
        exit_code = None
        if a.exit_code not in (None, ""):
            try:
                exit_code = int(a.exit_code)
            except ValueError:
                exit_code = None
        summary = summarize(_read_optional(a.request), _read_optional(a.log), _read_optional(a.time), exit_code,
                            a.head_sha, a.kani_commit, a.request_error or None)
        out = Path(a.out_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        (out / "summary.md").write_text(render_md(summary))
        print(render_md(summary))
        return 0
    try:
        summary = json.loads(Path(a.summary).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        print(f"gate: unreadable summary: {exc}", file=sys.stderr)
        return 3
    ok = summary.get("status") == "COMPLETE" and summary.get("expectation_met") is True
    print(f"gate: status={summary.get('status')} expectation_met={summary.get('expectation_met')}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
