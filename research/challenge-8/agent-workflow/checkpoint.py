#!/usr/bin/env python3
"""SmallSort agent checkpoint v1, with bounded validation and generated views.

Schema (JSON): schema="smallsort-checkpoint-v1"; task_id; owner in
{merge,select-sort4,network}; phase; state in {NOT_STARTED,ACTIVE,CLOSED,HANDOFF};
updated_utc; assignment_sha256 (SHA-256 of CURRENT-TASK text before its single
"## Отчёт агента" marker); baseline={source_sha,tool_sha (40 hex or null),
profile_sha256 (64 hex or null)}; session={t0,main_deadline_utc,deadline_utc,
budget_seconds,spent_seconds,retired_seconds,remaining_seconds,
active_build_ids,unresolved_ids}; confirmed=[{claim,assurance,evidence}],
open=[strings], blocker={summary,location?,build_id?,evidence},
rejected=[{approach,reason,evidence}], next_step, artifacts=[{path,sha256}].
Evidence entries have path, sha256, and optional build_id. UNKNOWN/null remains
unknown. The remaining budget includes any active-build reservations.

The CLI is standalone and uses only the Python standard library. write-views
requires the checkpoint and both targets to be regular, non-symlink files in
the same Git worktree; each target is replaced atomically after all checks.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import posixpath
import re
import sys
import tempfile
from typing import Any


SCHEMA = "smallsort-checkpoint-v1"
REPORT_MARKER = "## Отчёт агента"
MAX_OUTPUT = 6 * 1024
MAX_NARRATIVE = 1200
MAX_LIST = 8
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
SHA256 = re.compile(r"^[0-9a-fA-F]{64}$")
BUILD_UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
STATES = {"NOT_STARTED", "ACTIVE", "CLOSED", "HANDOFF"}
OWNERS = {"merge", "select-sort4", "network"}
ASSURANCES = {"SOURCE_REPORTED", "INDEPENDENTLY_ESTABLISHED"}


class CheckpointError(ValueError):
    pass


def _fail(msg: str) -> None:
    raise CheckpointError(msg)


def _text(value: Any, label: str, *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str) or not value.strip():
        _fail(f"{label}: expected non-empty text" + (" or null" if optional else ""))
    if len(value) > MAX_NARRATIVE:
        _fail(f"{label}: exceeds {MAX_NARRATIVE} characters")


def _sha(value: Any, label: str, pattern: re.Pattern[str], *, optional: bool = False) -> None:
    if optional and value is None:
        return
    if not isinstance(value, str) or not pattern.fullmatch(value):
        _fail(f"{label}: invalid {'SHA-256' if pattern is SHA256 else 'SHA-1'} identity" + (" or null" if optional else ""))


def _uuid(value: Any, label: str) -> None:
    if not isinstance(value, str) or not BUILD_UUID.fullmatch(value):
        _fail(f"{label}: invalid Build UUID")


def _utc(value: Any, label: str, *, optional: bool = False) -> dt.datetime | None:
    if optional and value is None:
        return None
    if not isinstance(value, str):
        _fail(f"{label}: expected timezone-aware ISO-8601 timestamp" + (" or null" if optional else ""))
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _fail(f"{label}: invalid ISO-8601 timestamp")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail(f"{label}: timezone is required")
    return parsed.astimezone(dt.timezone.utc)


def _entries(value: Any, label: str, cap: int = MAX_LIST) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > cap:
        _fail(f"{label}: expected list of at most {cap} entries")
    for i, entry in enumerate(value):
        if not isinstance(entry, dict):
            _fail(f"{label}[{i}]: expected object")
        _text(entry.get("path"), f"{label}[{i}].path")
        _sha(entry.get("sha256"), f"{label}[{i}].sha256", SHA256)
        if "build_id" in entry and entry["build_id"] is not None:
            _uuid(entry["build_id"], f"{label}[{i}].build_id")
    return value


def validate(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        _fail("checkpoint: expected JSON object")
    if data.get("schema") != SCHEMA:
        _fail(f"schema: expected {SCHEMA}")
    for key in ("task_id", "phase", "updated_utc", "next_step"):
        _text(data.get(key), key)
    if data.get("owner") not in OWNERS:
        _fail("owner: expected merge, select-sort4 or network")
    if data.get("state") not in STATES:
        _fail("state: invalid checkpoint state")
    _utc(data["updated_utc"], "updated_utc")
    _sha(data.get("assignment_sha256"), "assignment_sha256", SHA256)

    baseline = data.get("baseline")
    if not isinstance(baseline, dict):
        _fail("baseline: expected object")
    for key in ("source_sha", "tool_sha"):
        _sha(baseline.get(key), f"baseline.{key}", SHA40, optional=True)
    _sha(baseline.get("profile_sha256"), "baseline.profile_sha256", SHA256, optional=True)

    session = data.get("session")
    if not isinstance(session, dict):
        _fail("session: expected object")
    dates = {key: _utc(session.get(key), f"session.{key}", optional=True) for key in ("t0", "main_deadline_utc", "deadline_utc")}
    numeric = ("budget_seconds", "spent_seconds", "retired_seconds", "remaining_seconds")
    for key in numeric:
        value = session.get(key)
        if type(value) is not int or value < 0:
            _fail(f"session.{key}: expected non-negative integer")
    if session["spent_seconds"] + session["retired_seconds"] + session["remaining_seconds"] != session["budget_seconds"]:
        _fail("session budget arithmetic must satisfy spent + retired + remaining = budget")
    for key in ("active_build_ids", "unresolved_ids"):
        value = session.get(key)
        if not isinstance(value, list) or len(value) > 32:
            _fail(f"session.{key}: expected list of at most 32 IDs")
        for i, item in enumerate(value):
            _text(item, f"session.{key}[{i}]")
            if key == "active_build_ids":
                _uuid(item, f"session.{key}[{i}]")
    if data["state"] == "NOT_STARTED":
        if any(x is not None for x in dates.values()):
            _fail("NOT_STARTED requires null session dates")
        if session["active_build_ids"] or session["unresolved_ids"] or session["spent_seconds"] or session["retired_seconds"]:
            _fail("NOT_STARTED requires no builds/unresolved IDs and zero spent/retired time")
    else:
        t0, main, deadline = (dates[k] for k in ("t0", "main_deadline_utc", "deadline_utc"))
        if None in (t0, main, deadline):
            _fail(f"{data['state']} requires all session dates")
        assert t0 is not None and main is not None and deadline is not None
        if main != t0 + dt.timedelta(minutes=120) or deadline != main + dt.timedelta(minutes=30):
            _fail("session dates must use t0 + 120 minutes main window and +30 minutes closeout")
    if data["state"] == "CLOSED" and (session["remaining_seconds"] != 0 or session["active_build_ids"] or session["unresolved_ids"]):
        _fail("CLOSED requires zero remaining time and no active builds or unresolved IDs")

    confirmed = data.get("confirmed")
    if not isinstance(confirmed, list) or len(confirmed) > MAX_LIST:
        _fail(f"confirmed: expected list of at most {MAX_LIST} claims")
    for i, claim in enumerate(confirmed):
        if not isinstance(claim, dict):
            _fail(f"confirmed[{i}]: expected object")
        _text(claim.get("claim"), f"confirmed[{i}].claim")
        if claim.get("assurance") not in ASSURANCES:
            _fail(f"confirmed[{i}].assurance: invalid assurance")
        evidence = claim.get("evidence")
        if not isinstance(evidence, list) or not evidence or len(evidence) > 8:
            _fail(f"confirmed[{i}].evidence: each confirmed claim requires 1 to 8 evidence entries")
        _entries(evidence, f"confirmed[{i}].evidence", cap=8)
    opened = data.get("open")
    if not isinstance(opened, list) or len(opened) > 32:
        _fail("open: expected list of at most 32 strings")
    for i, item in enumerate(opened):
        _text(item, f"open[{i}]")
    blocker = data.get("blocker")
    if not isinstance(blocker, dict):
        _fail("blocker: expected object")
    _text(blocker.get("summary"), "blocker.summary")
    _text(blocker.get("location"), "blocker.location", optional=True)
    if blocker.get("build_id") is not None:
        _uuid(blocker["build_id"], "blocker.build_id")
    _entries(blocker.get("evidence"), "blocker.evidence")
    rejected = data.get("rejected")
    if not isinstance(rejected, list) or len(rejected) > MAX_LIST:
        _fail(f"rejected: expected list of at most {MAX_LIST} entries")
    for i, item in enumerate(rejected):
        if not isinstance(item, dict):
            _fail(f"rejected[{i}]: expected object")
        _text(item.get("approach"), f"rejected[{i}].approach")
        _text(item.get("reason"), f"rejected[{i}].reason")
        _entries(item.get("evidence"), f"rejected[{i}].evidence")
    _entries(data.get("artifacts"), "artifacts", cap=32)
    return data


def load_checkpoint(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _fail(f"cannot read checkpoint: {exc}")
    return validate(data)


def _bounded(text: str) -> str:
    if len(text.encode("utf-8")) > MAX_OUTPUT:
        _fail(f"rendered output exceeds {MAX_OUTPUT} bytes; shorten checkpoint fields")
    return text


def _link(path: str) -> str:
    prefix = "research/challenge-8/"
    if path.startswith(prefix):
        return path[len(prefix):]
    return posixpath.relpath(path, "research/challenge-8")


def render(data: dict[str, Any], fmt: str) -> str:
    validate(data)
    session = data["session"]
    t0 = session["t0"] or "NOT_SET"
    main_deadline = session["main_deadline_utc"] or "NOT_SET"
    absolute_deadline = session["deadline_utc"] or "NOT_SET"
    if fmt == "status":
        lines = [f"# Agent checkpoint: {data['task_id']}", "", f"- Owner: {data['owner']} | phase: {data['phase']} | state: {data['state']}", f"- Updated: {data['updated_utc']}", f"- Baseline: source `{data['baseline']['source_sha'] or 'UNKNOWN'}`, tool `{data['baseline']['tool_sha'] or 'UNKNOWN'}`, profile `{data['baseline']['profile_sha256'] or 'UNKNOWN'}`", f"- Session dates: T0 `{t0}`; main deadline `{main_deadline}`; absolute deadline `{absolute_deadline}`", f"- Budget: {session['budget_seconds']}s total; {session['spent_seconds']}s spent; {session['retired_seconds']}s retired; {session['remaining_seconds']}s remaining including active reservations", f"- Active Build IDs: {', '.join(session['active_build_ids']) or 'none recorded'}", f"- Unresolved IDs: {', '.join(session['unresolved_ids']) or 'none recorded'}", "", "## Confirmed claims"]
        for item in data["confirmed"]:
            evidence = "; ".join(f"[{e['path']}]({_link(e['path'])}) SHA `{e['sha256']}`" + (f" Build `{e['build_id']}`" if e.get("build_id") else "") for e in item["evidence"])
            lines.append(f"- [{item['assurance']}] {item['claim']} — {evidence}")
        if not data["confirmed"]:
            lines.append("- None recorded; UNKNOWN remains UNKNOWN.")
        lines.extend(["", "## Open"])
        lines.extend(f"- {item}" for item in data["open"])
        if not data["open"]:
            lines.append("- None recorded.")
        lines.extend(["", "## Rejected approaches"])
        for item in data["rejected"]:
            evidence = "; ".join(f"[{e['path']}]({_link(e['path'])}) SHA `{e['sha256']}`" for e in item["evidence"])
            lines.append(f"- {item['approach']} — {item['reason']}" + (f"; {evidence}" if evidence else ""))
        if not data["rejected"]:
            lines.append("- None recorded.")
        blocker = data["blocker"]
        blocker_text = blocker["summary"]
        if blocker.get("location"):
            blocker_text += f" ({blocker['location']})"
        if blocker.get("build_id"):
            blocker_text += f" [Build `{blocker['build_id']}`]"
        lines.extend(["", "## Blocker", blocker_text])
        for evidence in blocker["evidence"]:
            lines.append(f"- [{evidence['path']}]({_link(evidence['path'])}) SHA `{evidence['sha256']}`" + (f" Build `{evidence['build_id']}`" if evidence.get("build_id") else ""))
        lines.extend(["", "## Next", data["next_step"]])
        if data["artifacts"]:
            lines.extend(["", "## Artifacts"])
            lines.extend(f"- [{x['path']}]({_link(x['path'])}) — `{x['sha256']}`" for x in data["artifacts"])
        return _bounded("\n".join(lines) + "\n")
    if fmt != "report":
        _fail("format must be status or report")
    lines = [f"{REPORT_MARKER}", "", f"**{data['task_id']} · {data['owner']} · {data['phase']} · {data['state']}**", f"Updated: {data['updated_utc']}. Baseline source/tool/profile: `{data['baseline']['source_sha'] or 'UNKNOWN'}` / `{data['baseline']['tool_sha'] or 'UNKNOWN'}` / `{data['baseline']['profile_sha256'] or 'UNKNOWN'}`.", f"Dates: T0 `{t0}`; main `{main_deadline}`; absolute `{absolute_deadline}`. Budget {session['budget_seconds']}s: {session['spent_seconds']}s spent, {session['retired_seconds']}s retired, {session['remaining_seconds']}s remaining including reservations.", f"Active Build IDs: {', '.join(session['active_build_ids']) or 'none recorded'}; unresolved: {', '.join(session['unresolved_ids']) or 'none recorded'}.", f"Blocker: {data['blocker']['summary']}" + (f" [Build `{data['blocker']['build_id']}`]" if data['blocker'].get("build_id") else ""), f"Next: {data['next_step']}", "See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities."]
    return _bounded("\n".join(lines) + "\n")


def _project_root(path: Path) -> Path:
    resolved = path.resolve(strict=True)
    for parent in (resolved.parent, *resolved.parent.parents):
        if (parent / ".git").exists():
            return parent
    _fail("cannot determine Git worktree root for write-views")


def _safe_regular(path: Path, root: Path, label: str) -> Path:
    absolute = path.absolute()
    for component in (absolute, *absolute.parents):
        if component.is_symlink():
            _fail(f"{label}: symlink paths are rejected")
    try:
        resolved = absolute.resolve(strict=True)
    except OSError as exc:
        _fail(f"{label}: {exc}")
    if not resolved.is_relative_to(root):
        _fail(f"{label}: target is outside the checkpoint Git worktree")
    if not resolved.is_file():
        _fail(f"{label}: expected existing regular file")
    return resolved


def write_views(checkpoint_path: Path, status_path: Path, task_path: Path) -> None:
    if checkpoint_path.name != "CHECKPOINT.json" or checkpoint_path.parent.name != "challenge-8" or checkpoint_path.parent.parent.name != "research":
        _fail("checkpoint must be research/challenge-8/CHECKPOINT.json")
    if status_path.name != "STATUS.md" or status_path.parent != checkpoint_path.parent:
        _fail("status target must be alongside checkpoint as STATUS.md")
    if task_path.name != "CURRENT-TASK.md" or task_path.parent != checkpoint_path.parent:
        _fail("task target must be alongside checkpoint as CURRENT-TASK.md")
    data = load_checkpoint(checkpoint_path)
    root = _project_root(checkpoint_path)
    cp = _safe_regular(checkpoint_path, root, "checkpoint")
    status = _safe_regular(status_path, root, "status target")
    task = _safe_regular(task_path, root, "task target")
    if len({cp, status, task}) != 3:
        _fail("checkpoint, status, and task paths must be distinct")
    try:
        task_bytes = task.read_bytes()
        task_bytes.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        _fail(f"task target: cannot read UTF-8 content: {exc}")
    marker = REPORT_MARKER.encode("utf-8")
    if task_bytes.count(marker) != 1:
        _fail(f"task target must contain exactly one {REPORT_MARKER} marker")
    prefix, _old_report = task_bytes.split(marker, 1)
    digest = hashlib.sha256(prefix).hexdigest()
    if digest.lower() != data["assignment_sha256"].lower():
        _fail("assignment_sha256 does not match CURRENT-TASK prefix")
    status_new = render(data, "status").encode("utf-8")
    task_new = prefix + render(data, "report").encode("utf-8")
    if len(task_new) > MAX_OUTPUT:
        _fail(f"CURRENT-TASK output exceeds {MAX_OUTPUT} bytes; shorten assignment/checkpoint fields")
    _safe_regular(status, root, "status target")
    _safe_regular(task, root, "task target")
    _atomic_replace(status, status_new)
    _atomic_replace(task, task_new)


def _atomic_replace(path: Path, content: bytes) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(tmp_name)
    try:
        os.fchmod(fd, path.stat().st_mode & 0o777)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate and render a SmallSort agent checkpoint")
    sub = parser.add_subparsers(dest="command", required=True)
    pval = sub.add_parser("validate")
    pval.add_argument("checkpoint", type=Path)
    pr = sub.add_parser("render")
    pr.add_argument("checkpoint", type=Path)
    pr.add_argument("--format", choices=("status", "report"), default="status")
    pw = sub.add_parser("write-views")
    pw.add_argument("checkpoint", type=Path)
    pw.add_argument("--status", required=True, type=Path)
    pw.add_argument("--task", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "validate":
            load_checkpoint(args.checkpoint)
            print("VALID")
        elif args.command == "render":
            sys.stdout.write(render(load_checkpoint(args.checkpoint), args.format))
        else:
            write_views(args.checkpoint, args.status, args.task)
            print("VIEWS_WRITTEN")
    except (CheckpointError, OSError, UnicodeError) as exc:
        print(f"checkpoint: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
