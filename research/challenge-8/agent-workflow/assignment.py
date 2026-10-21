#!/usr/bin/env python3
"""Create compact SmallSort assignment drafts and install them on closed branches.

Installation is a local handoff only. It does not create a ledger/profile,
register coordinator state, set T0, submit work, commit, or push.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import subprocess
import sys
import tempfile
from typing import Any

import checkpoint as cp


SCHEMA = "smallsort-assignment-v1"
CORE_DIR = Path(__file__).resolve().parent
MAX_TASK_BYTES = 6144
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
TASK_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,100}$")
PHASE_ID = re.compile(r"^[A-Z][A-Z0-9-]{0,100}$")
LANE_ID = re.compile(r"^[a-z][a-z0-9-]{0,63}$")
SPEC_KEYS = {
    "schema", "task_id", "previous_task_id", "title", "owner", "worktree", "branch",
    "baseline_sha", "source_sha", "tool_sha", "tool_worktree", "tool_branch",
    "profile_path", "profile_sha256", "phase", "lane", "ledger_path",
    "previous_ledger_path", "goal", "steps", "special_bounds", "references", "handoff",
}
COORDINATION_DIR = Path("/root/smallsort-ci-coordination")
OWNER_LABELS = {"merge": "Merge", "select-sort4": "Select/sort4"}


class AssignmentError(ValueError):
    pass


def _err(message: str) -> None:
    raise AssignmentError(message)


def _string(value: Any, field: str, limit: int = 1000) -> str:
    if not isinstance(value, str) or not value.strip():
        _err(f"{field} must be non-empty text")
    if len(value) > limit:
        _err(f"{field} exceeds {limit} characters")
    return value


def _repo_path(value: Any, field: str) -> str:
    value = _string(value, field, 500)
    if "\\" in value or "\x00" in value:
        _err(f"{field} must be a safe repository-relative path")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in ("", ".", "..") for part in p.parts) or ":" in p.parts[0]:
        _err(f"{field} must be a safe repository-relative path")
    if not p.as_posix().startswith("research/challenge-8/"):
        _err(f"{field} must stay under research/challenge-8/")
    return p.as_posix()


def validate_spec(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        _err("spec must be a JSON object")
    missing, extra = sorted(SPEC_KEYS - value.keys()), sorted(value.keys() - SPEC_KEYS)
    if missing:
        _err("missing spec fields: " + ", ".join(missing))
    if extra:
        _err("unknown spec fields: " + ", ".join(extra))
    spec = dict(value)
    if spec["schema"] != SCHEMA:
        _err(f"schema must be {SCHEMA}")
    for key in ("task_id", "previous_task_id"):
        _string(spec[key], key, 101)
        if not TASK_ID.fullmatch(spec[key]):
            _err(f"{key} contains unsafe characters")
    for key in ("title", "worktree", "branch", "tool_worktree", "tool_branch", "phase", "lane", "goal"):
        _string(spec[key], key)
    if not PHASE_ID.fullmatch(spec["phase"]):
        _err("phase must be an uppercase protocol phase identifier")
    if not LANE_ID.fullmatch(spec["lane"]):
        _err("lane must be a lowercase protocol lane identifier")
    if spec["owner"] not in OWNER_LABELS:
        _err("owner must be merge or select-sort4")
    if not Path(spec["worktree"]).is_absolute() or not Path(spec["tool_worktree"]).is_absolute():
        _err("worktree and tool_worktree must be absolute paths")
    for key in ("baseline_sha", "source_sha", "tool_sha"):
        if not isinstance(spec[key], str) or not SHA40.fullmatch(spec[key]):
            _err(f"{key} must be a lowercase full Git SHA")
    if not isinstance(spec["profile_sha256"], str) or not SHA256.fullmatch(spec["profile_sha256"]):
        _err("profile_sha256 must be lowercase SHA-256")
    for key in ("profile_path", "ledger_path", "previous_ledger_path"):
        spec[key] = _repo_path(spec[key], key)
    if spec["ledger_path"] == spec["previous_ledger_path"]:
        _err("ledger_path must be a new path distinct from previous_ledger_path")
    for key, cap in (("steps", 3), ("special_bounds", 3)):
        items = spec[key]
        if not isinstance(items, list) or len(items) > cap:
            _err(f"{key} must contain at most {cap} entries")
        for i, item in enumerate(items):
            _string(item, f"{key}[{i}]", 700)
    refs = spec["references"]
    if not isinstance(refs, list) or len(refs) > 5:
        _err("references must contain at most 5 entries")
    for i, ref in enumerate(refs):
        if not isinstance(ref, dict) or set(ref) != {"title", "path"}:
            _err(f"references[{i}] must contain title and path")
        _string(ref["title"], f"references[{i}].title", 160)
        ref["path"] = _repo_path(ref["path"], f"references[{i}].path")
    handoff = spec["handoff"]
    if not isinstance(handoff, dict):
        _err("handoff must be an object")
    required_handoff = {"confirmed", "open", "blocker", "rejected", "next_step", "artifacts"}
    if set(handoff) != required_handoff:
        _err("handoff must contain confirmed/open/blocker/rejected/next_step/artifacts")
    # Reuse the checkpoint schema validator with a synthetic NOT_STARTED envelope.
    synthetic = {
        "schema": cp.SCHEMA, "task_id": spec["task_id"], "owner": spec["owner"],
        "phase": spec["phase"], "state": "NOT_STARTED", "updated_utc": "2000-01-01T00:00:00Z",
        "assignment_sha256": "0" * 64,
        "baseline": {"source_sha": spec["source_sha"], "tool_sha": spec["tool_sha"], "profile_sha256": spec["profile_sha256"]},
        "session": {"t0": None, "main_deadline_utc": None, "deadline_utc": None,
                    "budget_seconds": 3600, "spent_seconds": 0, "retired_seconds": 0,
                    "remaining_seconds": 3600, "active_build_ids": [], "unresolved_ids": []},
        **handoff,
    }
    try:
        cp.validate(synthetic)
    except cp.CheckpointError as exc:
        _err(f"invalid handoff: {exc}")
    return spec


def _bullet(label: str, items: list[str], fallback: str = "none recorded") -> str:
    return "\n".join(f"- {item}" for item in items) if items else f"- {fallback}"


def _task_link(path: str) -> str:
    prefix = "research/challenge-8/"
    if path.startswith(prefix):
        return path[len(prefix):]
    return posixpath.relpath(path, "research/challenge-8")


def render_task(spec: dict[str, Any]) -> tuple[bytes, dict[str, Any]]:
    spec = validate_spec(spec)
    h = spec["handoff"]
    lines = [
        f"# {spec['title']}", "", f"Task ID: `{spec['task_id']}`; previous task: `{spec['previous_task_id']}`.",
        f"Owner: **{OWNER_LABELS[spec['owner']]}**. Phase: `{spec['phase']}`. Lane: `{spec['lane']}`.",
        "", "## Mission", "",
        "This is a bounded continuation of the previous task under a newly authorized window.",
        "", f"This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance.",
        "The owner may proceed within this task and its bounds. Start with T0 NOT_SET; prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, then obtain the required independent review and register the exact phase through the assigned branch client before proof work.",
        "No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.",
        "", "## Baseline and controls", "",
        f"Worktree `{spec['worktree']}` on branch `{spec['branch']}`; baseline `{spec['baseline_sha']}`; source `{spec['source_sha']}`.",
        f"Tool worktree `{spec['tool_worktree']}` on `{spec['tool_branch']}` at `{spec['tool_sha']}`.",
        f"Profile `{spec['profile_path']}` SHA-256 `{spec['profile_sha256']}`. New ledger path: `{spec['ledger_path']}`; previous closed ledger: `{spec['previous_ledger_path']}`.",
        f"Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥{420 if spec['owner'] == 'merge' else 240} seconds. T0 remains NOT_SET until the owner registers.",
        "", "## Goal and steps", "", spec["goal"], "",
    ]
    lines.extend(f"{i}. {item}" for i, item in enumerate(spec["steps"], 1))
    lines.extend(["", "## Special bounds", ""])
    lines.extend(f"- {item}" for item in spec["special_bounds"])
    if not spec["special_bounds"]:
        lines.append("- Follow CORE.md and the explicit mission above.")
    lines.extend(["", "## Starting checkpoint", "", "Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN."])
    blocker = h["blocker"]
    blocker_detail = blocker["summary"]
    if blocker.get("location"):
        blocker_detail += f" ({blocker['location']})"
    if blocker.get("build_id"):
        blocker_detail += f" [Build {blocker['build_id']}]"
    lines.extend(["", f"Blocker: {blocker_detail}"])
    lines.append(f"Next: {h['next_step']}")
    lines.extend(["", "## References", ""])
    for ref in spec["references"]:
        lines.append(f"- [{ref['title']}]({_task_link(ref['path'])})")
    if not spec["references"]:
        lines.append("- [Permanent policy](agent-workflow/CORE.md)")
    prefix = ("\n".join(lines).rstrip() + "\n\n").encode("utf-8")
    checkpoint_data = {
        "schema": cp.SCHEMA, "task_id": spec["task_id"], "owner": spec["owner"], "phase": spec["phase"],
        "state": "NOT_STARTED", "updated_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "assignment_sha256": hashlib.sha256(prefix).hexdigest(),
        "baseline": {"source_sha": spec["source_sha"], "tool_sha": spec["tool_sha"], "profile_sha256": spec["profile_sha256"]},
        "session": {"t0": None, "main_deadline_utc": None, "deadline_utc": None,
                    "budget_seconds": 3600, "spent_seconds": 0, "retired_seconds": 0,
                    "remaining_seconds": 3600, "active_build_ids": [], "unresolved_ids": []},
        "confirmed": h["confirmed"], "open": h["open"], "blocker": h["blocker"],
        "rejected": h["rejected"], "next_step": h["next_step"], "artifacts": h["artifacts"],
    }
    cp.validate(checkpoint_data)
    report = cp.render(checkpoint_data, "report").encode("utf-8")
    task = prefix + report
    if task.count(cp.REPORT_MARKER.encode("utf-8")) != 1:
        _err("assignment content must contain exactly one generated report marker")
    if len(task) > MAX_TASK_BYTES:
        _err(f"rendered task is {len(task)} bytes; limit is {MAX_TASK_BYTES}, shorten the spec")
    return task, checkpoint_data


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _read_spec(path: Path) -> dict[str, Any]:
    try:
        return validate_spec(json.loads(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _err(f"cannot read spec: {exc}")


def _git(root: Path, *args: str) -> str:
    try:
        result = subprocess.run(["git", "-C", str(root), *args], check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        stderr = getattr(exc, "stderr", "")
        _err(f"git {' '.join(args)} failed: {str(stderr).strip()}")
    return result.stdout.strip()


def _root(worktree: Path) -> Path:
    try:
        root = Path(_git(worktree, "rev-parse", "--show-toplevel")).resolve(strict=True)
        wanted = worktree.resolve(strict=True)
    except OSError as exc:
        _err(f"worktree unavailable: {exc}")
    if root != wanted:
        _err("worktree must be the exact Git repository root")
    return root


def _assert_origin(root: Path) -> None:
    origin = _git(root, "remote", "get-url", "origin")
    normalized = origin.lower().removesuffix(".git")
    if not (normalized.endswith("/tiramisu-cake/verify-rust-std") or normalized.endswith(":tiramisu-cake/verify-rust-std")):
        _err("origin must point to Tiramisu-Cake/verify-rust-std")


def _safe_path(root: Path, relative: str, label: str, *, must_exist: bool = True) -> Path:
    target = root / relative
    cursor = root
    for part in PurePosixPath(relative).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            _err(f"{label}: symlink path is rejected")
    if must_exist:
        try:
            resolved = target.resolve(strict=True)
        except OSError as exc:
            _err(f"{label}: {exc}")
        if not resolved.is_relative_to(root) or not resolved.is_file():
            _err(f"{label}: expected regular file inside worktree")
        return resolved
    if target.exists():
        _err(f"{label}: path already exists")
    if not target.parent.is_dir() or not target.parent.resolve().is_relative_to(root):
        _err(f"{label}: parent directory missing or outside worktree")
    return target


def _git_file_sha(root: Path, sha: str) -> None:
    _git(root, "cat-file", "-e", f"{sha}^{{commit}}")


def _git_file_bytes(root: Path, refpath: str) -> bytes:
    try:
        result = subprocess.run(["git", "-C", str(root), "show", f"HEAD:{refpath}"], check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError):
        _err(f"profile is missing from assigned branch: {refpath}")
    return result.stdout


def _validate_repo_state(spec: dict[str, Any]) -> Path:
    root = _root(Path(spec["worktree"]))
    _assert_origin(root)
    branch = _git(root, "branch", "--show-current")
    if branch != spec["branch"]:
        _err(f"assigned branch mismatch: expected {spec['branch']}, found {branch or 'detached HEAD'}")
    _git_file_sha(root, spec["baseline_sha"])
    _git_file_sha(root, spec["source_sha"])
    try:
        subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", spec["baseline_sha"], "HEAD"], check=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        _err("baseline_sha is not an ancestor of the assigned branch HEAD")

    toolroot = Path(_git(Path(spec["tool_worktree"]), "rev-parse", "--show-toplevel")).resolve(strict=True)
    if toolroot != Path(spec["tool_worktree"]).resolve(strict=True):
        _err("tool_worktree must be the exact Git repository root")
    if _git(toolroot, "branch", "--show-current") != spec["tool_branch"]:
        _err("tool branch mismatch")
    if _git(toolroot, "rev-parse", "HEAD") != spec["tool_sha"]:
        _err("tool SHA does not match tool worktree HEAD")
    profile = _safe_path(root, spec["profile_path"], "profile")
    profile_bytes = profile.read_bytes()
    if hashlib.sha256(profile_bytes).hexdigest() != spec["profile_sha256"]:
        _err("profile SHA-256 mismatch")
    if _git_file_bytes(root, spec["profile_path"]) != profile_bytes:
        _err("profile worktree bytes differ from the assigned branch")
    _safe_path(root, spec["previous_ledger_path"], "previous ledger")
    _safe_path(root, spec["ledger_path"], "new ledger", must_exist=False)
    return root


@contextlib.contextmanager
def _coordination_guard(owner: str, coordination_dir: Path):
    lock_path = coordination_dir / "lock"
    active_path = coordination_dir / "active.json"
    if not lock_path.is_file() or not active_path.is_file() or lock_path.is_symlink() or active_path.is_symlink():
        _err("coordinator state or shared lock is missing/unsafe")
    try:
        lock = lock_path.open("rb")
    except OSError as exc:
        _err(f"cannot open coordinator lock: {exc}")
    locked = False
    try:
        fcntl.flock(lock.fileno(), fcntl.LOCK_SH)
        locked = True
        try:
            envelope = json.loads(active_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            _err(f"cannot read coordinator state under shared lock: {exc}")
        if not isinstance(envelope, dict):
            _err("coordinator state must be an object")
        if "schema_version" in envelope:
            version, capacity = envelope.get("schema_version"), envelope.get("max_active")
            if type(version) is not int or version not in (2, 3) or capacity != {2: 2, 3: 3}[version]:
                _err("unsupported coordinator envelope")
            records = envelope.get("reservations")
        else:
            capacity = 1
            records = [envelope]
        if not isinstance(records, list) or len(records) > capacity:
            _err("invalid coordinator reservations")
        tokens, owners, ledgers = set(), set(), set()
        for record in records:
            if not isinstance(record, dict) or not isinstance(record.get("owner"), str) or not record["owner"]:
                _err("invalid coordinator reservation")
            token, ledger = record.get("dispatch_token"), record.get("ledger")
            if not isinstance(token, str) or not token or not isinstance(ledger, str) or not Path(ledger).is_absolute():
                _err("coordinator reservation lacks a valid token or absolute ledger path")
            resolved_ledger = str(Path(ledger).resolve())
            if token in tokens or record["owner"] in owners or resolved_ledger in ledgers:
                _err("coordinator reservation has duplicate token, owner, or ledger")
            tokens.add(token); owners.add(record["owner"]); ledgers.add(resolved_ledger)
            if record["owner"] == owner:
                _err(f"owner {owner} has an occupied or unresolved coordinator reservation")
        yield
    finally:
        if locked:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


def _ledger_closed(root: Path, spec: dict[str, Any]) -> str:
    ledger_path = _safe_path(root, spec["previous_ledger_path"], "previous ledger")
    try:
        ledger_bytes = ledger_path.read_bytes()
        ledger = json.loads(ledger_bytes.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _err(f"previous ledger is unreadable: {exc}")
    if _git_file_bytes(root, spec["previous_ledger_path"]) != ledger_bytes:
        _err("previous ledger worktree bytes differ from the assigned branch HEAD")
    if not isinstance(ledger, dict) or ledger.get("owner") != spec["owner"]:
        _err("previous ledger owner does not match assignment owner")
    phase = ledger.get("phase") or ledger.get("phase_id")
    if not isinstance(phase, str) or not phase:
        _err("previous ledger lacks a phase identifier")
    status = ledger.get("status") or ledger.get("state")
    if status != "CLOSED":
        _err("previous owner ledger is not CLOSED")
    remaining = ledger.get("remaining_seconds", ledger.get("remaining_build_seconds", ledger.get("remaining")))
    if type(remaining) is not int or remaining < 0:
        _err("previous ledger remaining budget is invalid")
    if ledger.get("active_build") not in (None, "") or ledger.get("active_build_id") not in (None, ""):
        _err("previous ledger still has an active Build")
    unresolved = ledger.get("unresolved", ledger.get("unresolved_ids", []))
    if unresolved not in ([], None):
        _err("previous ledger has unresolved items")
    total = ledger.get("budget_seconds", ledger.get("ceiling_build_seconds", ledger.get("authorized_seconds")))
    spent = ledger.get("spent_seconds", ledger.get("spent_build_seconds", ledger.get("used_seconds", ledger.get("used_build_seconds", ledger.get("used")))))
    remaining = ledger.get("remaining_seconds", ledger.get("remaining_build_seconds", ledger.get("remaining")))
    retired = ledger.get("retired_seconds", ledger.get("retired_build_seconds", ledger.get("closed_seconds")))
    unused_retired = ledger.get("unused_retired_seconds")
    carry = ledger.get("carry_forward_seconds", ledger.get("carry_seconds", 0))
    builds = ledger.get("builds")
    terminal = {"SUCCESS", "FAILURE", "INTERNAL_ERROR", "TIMEOUT", "CANCELLED", "EXPIRED", "REJECTED"}
    if not isinstance(builds, list) or any(not isinstance(build, dict) or build.get("accounted") is not True or (build.get("status") or build.get("state") or build.get("result")) not in terminal for build in builds):
        _err("previous ledger builds are missing terminal accounting")
    if any(type(x) is not int or x < 0 for x in (total, spent, remaining, carry)):
        _err("previous ledger time is not fully accounted")
    if unused_retired is not None:
        if type(unused_retired) is not int or unused_retired < 0:
            _err("previous ledger unused-retired accounting is invalid")
        if spent + unused_retired != total or remaining != unused_retired or carry != 0:
            _err("closed ledger retirement/remaining values are inconsistent")
    elif retired is not None:
        if type(retired) is not int or retired < 0 or spent + retired + remaining != total or remaining != 0:
            _err("previous ledger time is not fully accounted")
    else:
        _err("previous ledger lacks retired or unused-retired accounting")
    return phase


def _check_previous_task(root: Path, spec: dict[str, Any], old_phase: str) -> dict[str, bytes]:
    base = root / "research/challenge-8"
    task = _safe_path(root, "research/challenge-8/CURRENT-TASK.md", "current task")
    task_bytes = task.read_bytes()
    task_text = task_bytes.decode("utf-8", "strict")
    for needle in (spec["previous_task_id"], old_phase):
        if needle not in task_text:
            _err(f"CURRENT-TASK does not identify prior task/phase: {needle}")
    ledger_paths = (spec["previous_ledger_path"],
                    PurePosixPath(spec["previous_ledger_path"]).relative_to("research/challenge-8").as_posix())
    if not any(path in task_text for path in ledger_paths):
        _err("CURRENT-TASK does not identify the exact prior ledger path")
    if not any(owner in task_text for owner in (spec["owner"], OWNER_LABELS[spec["owner"]])):
        _err("CURRENT-TASK does not identify the prior owner")
    preserved: dict[str, bytes] = {"CURRENT-TASK.md": task_bytes}
    for name in ("STATUS.md", "AGENTS-COMPACT.md", "CORE.md", "CHECKPOINT.json"):
        path = base / name
        if path.exists() or path.is_symlink():
            safe = _safe_path(root, f"research/challenge-8/{name}", name)
            preserved[name] = safe.read_bytes()
    root_agents = root / "AGENTS.md"
    if root_agents.exists() or root_agents.is_symlink():
        safe = _safe_path(root, "AGENTS.md", "root AGENTS")
        preserved["ROOT-AGENTS.md"] = safe.read_bytes()
    nested_core = base / "agent-workflow" / "CORE.md"
    if nested_core.exists() or nested_core.is_symlink():
        safe = _safe_path(root, "research/challenge-8/agent-workflow/CORE.md", "agent-workflow/CORE.md")
        preserved["agent-workflow-CORE.md"] = safe.read_bytes()
    if "STATUS.md" not in preserved or "ROOT-AGENTS.md" not in preserved:
        _err("closed installation requires prior STATUS and root AGENTS files to archive")
    if "CHECKPOINT.json" in preserved:
        try:
            old_checkpoint = cp.validate(json.loads(preserved["CHECKPOINT.json"].decode("utf-8")))
        except (UnicodeError, json.JSONDecodeError, cp.CheckpointError) as exc:
            _err(f"existing checkpoint is invalid: {exc}")
        if old_checkpoint["owner"] != spec["owner"] or old_checkpoint["state"] != "CLOSED":
            _err("existing checkpoint must be CLOSED and match owner")
        session = old_checkpoint["session"]
        if session["remaining_seconds"] != 0 or session["active_build_ids"] or session["unresolved_ids"]:
            _err("existing checkpoint is not fully closed")
        marker = cp.REPORT_MARKER.encode("utf-8")
        if task_bytes.count(marker) != 1:
            _err("existing checkpoint requires exactly one report marker in CURRENT-TASK")
        prior_prefix, _prior_report = task_bytes.split(marker, 1)
        if hashlib.sha256(prior_prefix).hexdigest() != old_checkpoint["assignment_sha256"]:
            _err("existing checkpoint assignment digest does not match prior CURRENT-TASK")
    return preserved


def _write_atomic_new(path: Path, content: bytes) -> None:
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists() or path.is_symlink():
            _err(f"refusing to overwrite existing path: {path}")
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _archive_and_install(root: Path, spec: dict[str, Any], preserved: dict[str, bytes], task: bytes, checkpoint_data: dict[str, Any]) -> None:
    base = root / "research/challenge-8"
    history = base / "task-history" / spec["previous_task_id"]
    history_parent = base / "task-history"
    cursor = root
    for part in PurePosixPath("research/challenge-8/task-history").parts:
        cursor /= part
        if cursor.is_symlink():
            _err("task-history parent contains a symlink")
        if cursor.exists():
            resolved = cursor.resolve(strict=True)
            if not resolved.is_relative_to(root) or not resolved.is_dir():
                _err("task-history parent is outside the worktree or not a directory")
    if history.exists() or history.is_symlink():
        _err("history target already exists; refusing to overwrite archived task")
    canonical: dict[str, bytes] = {}
    for name in ("CORE.md", "AGENTS-COMPACT.md"):
        source = CORE_DIR / name
        if source.is_symlink() or not source.is_file():
            _err(f"canonical {name} is missing or unsafe")
        canonical[name] = source.read_bytes()
    checkpoint_bytes = _json_bytes(checkpoint_data)
    cp.validate(checkpoint_data)
    status_bytes = cp.render(checkpoint_data, "status").encode("utf-8")
    core_path = base / "agent-workflow" / "CORE.md"
    installs = {
        core_path: (canonical["CORE.md"], "agent-workflow-CORE.md"),
        root / "AGENTS.md": (canonical["AGENTS-COMPACT.md"], "ROOT-AGENTS.md"),
        base / "CURRENT-TASK.md": (task, "CURRENT-TASK.md"),
        base / "CHECKPOINT.json": (checkpoint_bytes, "CHECKPOINT.json"),
        base / "STATUS.md": (status_bytes, "STATUS.md"),
    }
    core_parent = core_path.parent
    cursor = base
    for part in PurePosixPath("agent-workflow").parts:
        cursor /= part
        if cursor.is_symlink():
            _err("CORE.md destination contains symlink")
    if core_parent.exists() and not core_parent.is_dir():
        _err("CORE.md destination parent is not a directory")
    for path, (_content, archive_name) in installs.items():
        if path.exists() and archive_name not in preserved:
            _err(f"refusing to overwrite unarchived existing file: {path}")
        if path.is_symlink():
            _err(f"refusing symlink destination: {path}")
    manifest = {name: hashlib.sha256(content).hexdigest() for name, content in preserved.items()}
    archive_files = {history / f"{name}.{digest}": preserved[name] for name, digest in manifest.items()}
    archive_files[history / "manifest.json"] = _json_bytes({"task_id": spec["previous_task_id"], "files": manifest})
    # All validation and generated content checks are complete before creating history.
    history.mkdir(parents=True)
    for path, content in archive_files.items():
        _write_atomic_new(path, content)
    core_parent.mkdir(parents=True, exist_ok=True)
    for path, (content, _archive_name) in installs.items():
        temp_fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
        try:
            os.fchmod(temp_fd, path.stat().st_mode & 0o777 if path.exists() else 0o644)
            with os.fdopen(temp_fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, path)
        finally:
            Path(temp_name).unlink(missing_ok=True)


def create(spec_path: Path, out_path: Path) -> None:
    spec = _read_spec(spec_path)
    task, _checkpoint = render_task(spec)
    out = out_path.absolute()
    for parent in (out.parent, *out.parent.parents):
        if parent.is_symlink():
            _err("output path contains a symlink")
    if out.exists() or out.is_symlink() or not out.parent.is_dir():
        _err("output must be a fresh file in an existing directory")
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "wb") as stream:
        stream.write(task)
        stream.flush()
        os.fsync(stream.fileno())


def install(spec_path: Path, coordination_dir: Path | None = None) -> None:
    spec = _read_spec(spec_path)
    with _coordination_guard(spec["owner"], coordination_dir or COORDINATION_DIR):
        root = _validate_repo_state(spec)
        old_phase = _ledger_closed(root, spec)
        preserved = _check_previous_task(root, spec, old_phase)
        task, checkpoint_data = render_task(spec)
        # All input checks and generated bytes are complete before the first write.
        _archive_and_install(root, spec, preserved, task, checkpoint_data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create or install a compact SmallSort assignment")
    subs = parser.add_subparsers(dest="command", required=True)
    pcreate = subs.add_parser("create")
    pcreate.add_argument("--spec", required=True, type=Path)
    pcreate.add_argument("--out", required=True, type=Path)
    pins = subs.add_parser("install")
    pins.add_argument("--spec", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            create(args.spec, args.out)
            print(f"DRAFT_WRITTEN {args.out}")
        else:
            install(args.spec)
            print("INSTALLED; AUTHORIZATION_NOT_STARTED; COORDINATOR_REGISTRATION_REQUIRED")
    except (AssignmentError, OSError, UnicodeError, cp.CheckpointError) as exc:
        print(f"assignment: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
