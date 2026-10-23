"""Read-only watcher authority checks; status/accounting uses the existing client.

This adapter never submits/cancels Builds or writes checkpoints/ledgers itself.
Its sole subprocess action is the pinned branch client's ordinary status path.
"""
from __future__ import annotations

import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import signal
import stat
import subprocess
import sys
import time

import checkpoint as cp

SCHEMA = "smallsort-watch-binding-v1"
COORDINATION = Path("/root/smallsort-ci-coordination")
OWNER_REPOS = {
    "merge": (Path("/root/verify-rust-std-merge-origin"), "merge/incoming-origin-20261009"),
    "select-sort4": (Path("/root/verify-rust-std-select-night"), "research/night-select-sort4-cloud-2026-10-09"),
    "network": (Path("/root/verify-rust-std-networks"), "challenge-8/networks"),
}
# Shared envelope versions this watcher reads; both have three project slots.
ENVELOPES = {(3, 3), (4, 3)}
CLIENT = "research/challenge-8/cloud-build/control.py"
COORD = "research/challenge-8/cloud-build/coordination.py"
CHECKPOINT = "research/challenge-8/CHECKPOINT.json"
TASK = "research/challenge-8/CURRENT-TASK.md"
TERMINAL = {"SUCCESS", "FAILURE", "INTERNAL_ERROR", "TIMEOUT", "CANCELLED", "EXPIRED"}
LIVE = {"QUEUED", "WORKING", "PENDING"}
SHA40 = re.compile(r"[a-f0-9]{40}\Z")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")
UUID = re.compile(r"[a-fA-F0-9]{8}(?:-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}\Z")
MUTABLE_LEDGER = {
    "builds", "active_build", "active_build_id", "used_build_seconds",
    "spent_build_seconds", "spent_seconds", "used_seconds", "remaining_build_seconds",
    "remaining_seconds", "retired_seconds", "retired_build_seconds", "unused_retired_seconds",
}
BUILD_FIELDS = ("build_id", "dispatch_token", "owner", "phase_id", "infra_sha", "proof_sha", "lane", "submitted_config_sha256", "source_mode", "source_input_sha256", "timeout_seconds", "reserved_seconds")


class BindingError(ValueError):
    """Authority was lost or input is stale; do not send a wakeup."""


class PollError(RuntimeError):
    """Bounded diagnostics without subprocess output or command text."""
    def __init__(self, message, *, kind="status_error", returncode=None, stderr_sha256=None):
        super().__init__(message)
        self.kind = kind
        self.returncode = returncode
        self.stderr_sha256 = stderr_sha256


class PollBusy(PollError):
    """Coordinator contention deferred a poll; no metadata request failed."""
    def __init__(self):
        super().__init__("coordinator read lock busy", kind="coordinator_busy")


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _json_hash(value):
    return _hash(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode())


def _safe(path, directory=False):
    p = Path(path).absolute()
    if any(part in {".", ".."} for part in p.parts) or any(x.is_symlink() for x in [p, *p.parents]):
        raise BindingError("symlink or traversal in authority path")
    mode = p.stat().st_mode
    if not (stat.S_ISDIR(mode) if directory else stat.S_ISREG(mode)):
        raise BindingError("authority path has wrong type")
    return p


def _read(path, cap=128 * 1024):
    p = _safe(path)
    fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > cap:
            raise BindingError("oversized/nonregular authority file")
        value = bytearray()
        while True:
            part = os.read(fd, min(8192, cap + 1 - len(value)))
            if not part:
                return bytes(value)
            value.extend(part)
            if len(value) > cap:
                raise BindingError("authority file grew beyond cap")
    finally:
        os.close(fd)


def _load(path):
    try:
        value = json.loads(_read(path))
        if not isinstance(value, dict):
            raise ValueError("object required")
        return value
    except (OSError, ValueError, RecursionError) as exc:
        raise BindingError("unavailable/invalid authority JSON") from exc


def _run(argv, cwd=None, cap=256 * 1024, timeout=20):
    """Bound both streams before accumulation; kill/reap own child group."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    result = {"stdout": bytearray(), "stderr": bytearray()}
    selector = selectors.DefaultSelector()
    try:
        for stream, key in ((proc.stdout, "stdout"), (proc.stderr, "stderr")):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, key)
        deadline = time.monotonic() + timeout
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise PollError("status subprocess timeout", kind="subprocess_timeout")
            for item, _ in selector.select(min(.2, remaining)):
                part = os.read(item.fd, 8192)
                if not part:
                    selector.unregister(item.fileobj)
                    continue
                target = result[item.data]
                if len(target) + len(part) > (cap if item.data == "stdout" else 8192):
                    raise PollError("metadata subprocess output cap", kind="output_cap")
                target.extend(part)
        code = proc.wait(timeout=max(.01, deadline - time.monotonic()))
        if code:
            raise PollError(f"metadata subprocess exit={code}", kind="subprocess_exit",
                            returncode=code, stderr_sha256=_hash(result["stderr"]))
        return bytes(result["stdout"])
    finally:
        selector.close()
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        proc.wait()
        proc.stdout.close()
        proc.stderr.close()


def _git(root, *args):
    try:
        return _run(["git", "-C", str(root), "-c", "core.hooksPath=/dev/null", *args], cap=256 * 1024)
    except (OSError, PollError, subprocess.TimeoutExpired) as exc:
        raise BindingError("Git identity check failed") from exc


def _repo_file(value):
    if not isinstance(value, str) or not value.startswith("research/challenge-8/cloud-build/") or "\\" in value or ":" in value or "\x00" in value:
        raise BindingError("ledger must be an exact relative Cloud Build path")
    p = PurePosixPath(value)
    if p.as_posix() != value or any(x in {"", ".", ".."} for x in value.split("/")):
        raise BindingError("unsafe ledger path")
    return value


def _identity(item):
    return {key: item.get(key) for key in BUILD_FIELDS}


def _reservation(owner, ledger_path, item, must_have):
    envelope = _load(COORDINATION / "active.json")
    records = envelope.get("reservations")
    version, capacity = envelope.get("schema_version"), envelope.get("max_active")
    if type(version) is not int or type(capacity) is not int or (version, capacity) not in ENVELOPES or not isinstance(records, list) or len(records) > 3:
        raise BindingError("unsupported coordinator envelope")
    matches = [r for r in records if isinstance(r, dict) and r.get("owner") == owner]
    expected = {"owner": owner, "ledger": str(ledger_path), "dispatch_token": item["dispatch_token"], "phase_id": item["phase_id"], "build_id": item["build_id"]}
    if matches:
        if len(matches) != 1 or any(matches[0].get(k) != v for k, v in expected.items()):
            raise BindingError("own coordinator reservation identity mismatch")
        return
    if must_have:
        # A crash after a normal global receipt was written but before own
        # ledger reconciliation may legitimately leave only this receipt.
        receipt = _load(COORDINATION / "receipts" / (item["dispatch_token"] + ".json"))
        if any(receipt.get(k) != v for k, v in expected.items()) or receipt.get("status") not in TERMINAL:
            raise BindingError("registered owner reservation/receipt absent")


def _snapshot(spec):
    try:
        root = _safe(Path(spec["worktree"]), directory=True)
        checkpoint_bytes = _read(root / CHECKPOINT)
        checkpoint = cp.validate(json.loads(checkpoint_bytes))
        owner = checkpoint["owner"]
        wanted_root, wanted_branch = OWNER_REPOS[owner]
        if root != wanted_root or _git(root, "rev-parse", "--show-toplevel").decode().strip() != str(root):
            raise BindingError("worktree is not assigned to this owner")
        branch = _git(root, "branch", "--show-current").decode().strip()
        if branch != wanted_branch:
            raise BindingError("assigned branch changed")
        origin = _git(root, "remote", "get-url", "origin").decode().strip()
        if origin not in {"https://github.com/Tiramisu-Cake/verify-rust-std.git", "git@github.com:Tiramisu-Cake/verify-rust-std.git"}:
            raise BindingError("origin is not the assigned fork")
        if checkpoint["state"] != "HANDOFF" or checkpoint["session"]["active_build_ids"] != [spec["build_id"]] or checkpoint["session"]["unresolved_ids"]:
            raise BindingError("exact single-Build HANDOFF checkpoint required")
        task = _read(root / TASK, 6144)
        marker = cp.REPORT_MARKER.encode()
        if task.count(marker) != 1 or _hash(task.split(marker)[0]) != checkpoint["assignment_sha256"]:
            raise BindingError("assignment digest mismatch")
        ledger_path = root / _repo_file(spec["ledger_path"])
        lock = _safe(COORDINATION / "lock")
        with lock.open("rb") as stream:
            end = time.monotonic() + 5
            while True:
                try:
                    fcntl.flock(stream, fcntl.LOCK_SH | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() >= end:
                        raise PollBusy()
                    time.sleep(.05)
            ledger = _load(ledger_path)
            if ledger.get("status") != "AUTHORIZED" or ledger.get("owner") != owner or ledger.get("phase") != checkpoint["phase"]:
                raise BindingError("phase account is closed/replaced or owner changed")
            if ledger.get("phase_id", checkpoint["phase"]) != checkpoint["phase"] or ledger.get("task_id", checkpoint["task_id"]) != checkpoint["task_id"]:
                raise BindingError("phase/task aliases disagree")
            dates = {"t0": "start_utc", "main_deadline_utc": "main_deadline_utc", "deadline_utc": "deadline_utc"}
            for field, key in dates.items():
                if cp._utc(ledger.get(key), key) != cp._utc(checkpoint["session"][field], field):
                    raise BindingError("ledger/checkpoint window mismatch")
            ceiling = ledger.get("ceiling_build_seconds")
            used, remaining = ledger.get("used_build_seconds"), ledger.get("remaining_build_seconds")
            retired = ledger.get("retired_seconds", ledger.get("retired_build_seconds", 0))
            if any(type(v) is not int or v < 0 for v in (ceiling, used, remaining, retired)) or ceiling != checkpoint["session"]["budget_seconds"] or used + remaining + retired != ceiling:
                raise BindingError("phase budget changed/incoherent")
            builds = ledger.get("builds")
            if not isinstance(builds, list) or any(not isinstance(b, dict) for b in builds):
                raise BindingError("invalid Build accounting")
            selected = [b for b in builds if b.get("build_id") == spec["build_id"]]
            if len(selected) != 1:
                raise BindingError("Build is not uniquely recorded")
            item = selected[0]
            if item.get("owner") != owner or item.get("phase_id") != checkpoint["phase"] or item.get("lane") not in ledger.get("allowed_lanes", []):
                raise BindingError("Build owner/phase/lane mismatch")
            token = item.get("dispatch_token")
            if not isinstance(token, str) or not re.fullmatch(r"dispatch-[a-f0-9]{32}", token):
                raise BindingError("invalid dispatch token")
            for field, pattern in (("infra_sha", SHA40), ("proof_sha", SHA40), ("submitted_config_sha256", SHA256)):
                if not isinstance(item.get(field), str) or not pattern.fullmatch(item[field]):
                    raise BindingError("missing exact source/config identity")
            accounted = item.get("accounted", False)
            status = item.get("status")
            if type(accounted) is not bool or status not in LIVE | TERMINAL or (accounted and status not in TERMINAL):
                raise BindingError("invalid Build status/accounting")
            pending = [b for b in builds if not b.get("accounted")]
            if not accounted and (len(pending) != 1 or pending[0] is not item or ledger.get("active_build") != spec["build_id"]):
                raise BindingError("another/unknown submission occupies this account")
            if accounted and (pending or ledger.get("active_build") not in (None, "")):
                raise BindingError("account has moved to another Build")
            _reservation(owner, ledger_path, item, must_have=not accounted)
        code = {}
        for path in (CLIENT, COORD):
            value = _read(root / path, 256 * 1024)
            if value != _git(root, "show", "HEAD:" + path):
                raise BindingError("status client differs from committed bytes")
            code[path] = _hash(value)
        binding = {
            "schema": SCHEMA, "owner": owner, "task_id": checkpoint["task_id"], "phase": checkpoint["phase"],
            "worktree": str(root), "branch": branch, "ledger_path": str(ledger_path), "thread_id": spec["thread_id"],
            "build_id": item["build_id"], "dispatch_token": token, "lane": item["lane"],
            "infra_sha": item["infra_sha"], "proof_sha": item["proof_sha"], "config_sha256": item["submitted_config_sha256"],
            "assignment_sha256": checkpoint["assignment_sha256"], "checkpoint_sha256": _hash(checkpoint_bytes),
            "ledger_authority_sha256": _json_hash({k: v for k, v in ledger.items() if k not in MUTABLE_LEDGER}),
            "build_identity_sha256": _json_hash(_identity(item)), "client_sha256": code[CLIENT], "coordination_sha256": code[COORD],
            "t0": checkpoint["session"]["t0"], "main_deadline_utc": checkpoint["session"]["main_deadline_utc"],
            "deadline_utc": checkpoint["session"]["deadline_utc"], "budget_seconds": ceiling,
        }
        return binding, {"terminal": status in TERMINAL, "status": status, "accounted": accounted}
    except (cp.CheckpointError, KeyError, TypeError, OSError, UnicodeError, ValueError) as exc:
        if isinstance(exc, BindingError):
            raise
        raise BindingError("authority binding unavailable/invalid") from exc


def capture(spec):
    if not UUID.fullmatch(str(spec.get("build_id", ""))) or not UUID.fullmatch(str(spec.get("thread_id", ""))):
        raise BindingError("exact Build/thread UUID required")
    return _snapshot(spec)[0]


def validate(binding):
    if not isinstance(binding, dict) or binding.get("schema") != SCHEMA:
        raise BindingError("invalid binding envelope")
    root = Path(binding["worktree"])
    try:
        relative = Path(binding["ledger_path"]).relative_to(root).as_posix()
    except ValueError as exc:
        raise BindingError("ledger escaped worktree") from exc
    spec = {"worktree": str(root), "ledger_path": relative, "thread_id": binding["thread_id"], "build_id": binding["build_id"]}
    current, status = _snapshot(spec)
    if current != binding:
        raise BindingError("watcher handoff/authority/source identity is stale")
    return status


def poll(binding, client_state_dir, *, timeout_seconds=55):
    # A status invocation reconciles all occupied owners under the existing
    # coordinator lock. Allow a bounded envelope, rather than the Git helper's
    # 20s default. The caller further limits this by the absolute deadline.
    if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not 0 < timeout_seconds <= 55:
        raise ValueError("status timeout must be positive and at most55 seconds")
    end = time.monotonic() + timeout_seconds
    validate(binding)
    target = Path(client_state_dir).absolute()
    if target.exists():
        _safe(target, directory=True)
    else:
        _safe(target.parent, directory=True)
        target.mkdir(mode=0o700)
    argv = [sys.executable, str(Path(binding["worktree"]) / CLIENT), "--owner", binding["owner"], "--phase-id", binding["phase"], "--ledger", binding["ledger_path"], "--state-dir", str(target), "status", binding["build_id"]]
    try:
        remaining = end - time.monotonic()
        if remaining <= 0:
            raise PollError("status validation exhausted poll budget", kind="subprocess_timeout")
        response = json.loads(_run(argv, cwd=binding["worktree"], timeout=remaining))
    except (OSError, ValueError, PollError, subprocess.TimeoutExpired) as exc:
        raise PollError("existing status client failed; no verification inference") from exc
    if not isinstance(response, dict) or response.get("id") != binding["build_id"] or not isinstance(response.get("status"), str) or response["status"] not in LIVE | TERMINAL:
        raise PollError("status metadata missing/mismatched", kind="metadata_mismatch")
    result = validate(binding)
    if result["status"] != response["status"]:
        raise PollError("Build status and reconciled account differ", kind="account_mismatch")
    return result
