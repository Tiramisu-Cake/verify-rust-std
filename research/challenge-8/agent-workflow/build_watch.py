#!/usr/bin/env python3
"""Bounded, sidecar-only watcher for an already authorized SmallSort job.

The adapters are intentionally imported only at the point of use.  The watcher
never interprets coordinator data as commands and never starts a Build.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
from pathlib import PurePosixPath
import re
import subprocess
import sys
import time
import uuid

DEFAULT_STORE = Path("/root/.local/state/smallsort-watch")
MAX_FILE = 256 * 1024
MAX_JOBS = 64
MAX_EVENTS = 128
MAX_DELIVERY_SECONDS = 20
TERMINAL_JOB_STATES = {"DELIVERED", "DELIVERY_UNKNOWN", "ACKED", "STOPPED", "STALE", "EXPIRED"}
ACTIVE_JOB_STATES = {"ARMED", "MONITORING", "READY", "DELIVERING"}
JOB_ID_RE = re.compile(r"[0-9a-f-]{36}\Z")


class WatchError(ValueError):
    pass


class DeliveryUnknown(RuntimeError):
    """An enqueue may have happened, so it must never be retried blindly."""


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _stamp(value: dt.datetime | None = None) -> str:
    return (value or _utcnow()).isoformat(timespec="seconds").replace("+00:00", "Z")


def _parse_stamp(value: str) -> dt.datetime:
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        raise WatchError("binding has invalid UTC deadline") from None
    if parsed.tzinfo is None:
        raise WatchError("binding deadline must include UTC timezone")
    return parsed.astimezone(dt.timezone.utc)


def _json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _digest(value) -> str:
    return hashlib.sha256(_json_bytes(value)).hexdigest()


def _load_json(path: Path):
    st = path.lstat()
    if not path.is_file() or path.is_symlink() or st.st_size > MAX_FILE:
        raise WatchError(f"unsafe or oversized file: {path.name}")
    with path.open("rb") as stream:
        raw = stream.read(MAX_FILE + 1)
    if len(raw) > MAX_FILE:
        raise WatchError(f"oversized file: {path.name}")
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise WatchError(f"invalid JSON: {path.name}") from None


class Store:
    """Private, bounded regular-file store. All writes are fsync + replace."""
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._ensure_dir(self.root)

    @staticmethod
    def _ensure_dir(path: Path):
        absolute = path.absolute()
        for component in (absolute, *absolute.parents):
            if component.exists() or component.is_symlink():
                if component.is_symlink() or not component.is_dir():
                    raise WatchError("store path components must be real directories")
        if path.exists() or path.is_symlink():
            if path.is_symlink() or not path.is_dir():
                raise WatchError("store path must be a real directory")
        else:
            path.mkdir(mode=0o700, parents=True)
        os.chmod(path, 0o700)

    def file(self, name: str) -> Path:
        if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,100}", name):
            raise WatchError("invalid store filename")
        result = self.root / name
        if result.is_symlink():
            raise WatchError(f"refusing symlink: {name}")
        return result

    @contextlib.contextmanager
    def lock(self, name: str, *, nonblocking=False):
        path = self.file(name)
        fd = os.open(path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | (fcntl.LOCK_NB if nonblocking else 0))
            except BlockingIOError:
                raise WatchError("watcher is already running") from None
            yield
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)

    def write(self, name: str, value):
        data = _json_bytes(value)
        if len(data) > MAX_FILE:
            raise WatchError("state exceeds storage bound")
        path = self.file(name)
        temp = self.file(".tmp-" + uuid.uuid4().hex)
        fd = os.open(temp, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600)
        try:
            with os.fdopen(fd, "wb", closefd=True) as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp, path)
            dfd = os.open(self.root, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        finally:
            with contextlib.suppress(FileNotFoundError):
                temp.unlink()

    def read_job(self, job_id: str):
        if not JOB_ID_RE.fullmatch(job_id):
            raise WatchError("invalid job ID")
        job = _load_json(self.file(job_id + ".json"))
        if not isinstance(job, dict) or job.get("job_id") != job_id:
            raise WatchError("job state identity mismatch")
        if job.get("integrity") != _digest({k: v for k, v in job.items() if k != "integrity"}):
            raise WatchError("job state integrity check failed")
        return job

    def save_job(self, job):
        value = dict(job)
        value.pop("integrity", None)
        value["integrity"] = _digest(value)
        self.write(value["job_id"] + ".json", value)

    def list_jobs(self):
        jobs = []
        for path in self.root.glob("*.json"):
            if path.is_symlink() or not path.is_file():
                raise WatchError("unsafe state entry")
            if path.stat().st_size > MAX_FILE:
                raise WatchError("oversized state entry")
            jobs.append(self.read_job(path.stem))
            if len(jobs) > MAX_JOBS:
                raise WatchError("job store capacity exceeded")
        return jobs


def _adapter(name):
    __import__(name)
    return sys.modules[name]


def _inspect(codex, thread_id):
    result = codex.inspect_thread(thread_id)
    needed = {"thread_id", "cwd", "status", "latest_turn_id", "latest_turn_status", "goal_active", "archived"}
    if not isinstance(result, dict) or not needed.issubset(result) or result["thread_id"] != thread_id:
        raise WatchError("thread inspection returned incomplete or mismatched metadata")
    return result


def _normalize_binding(binding):
    required = {"schema", "owner", "task_id", "phase", "worktree", "branch", "ledger_path", "thread_id",
                "build_id", "dispatch_token", "lane", "infra_sha", "proof_sha", "config_sha256",
                "assignment_sha256", "checkpoint_sha256", "ledger_authority_sha256", "client_sha256",
                "coordination_sha256", "t0", "main_deadline_utc", "deadline_utc", "budget_seconds"}
    if not isinstance(binding, dict) or not required.issubset(binding):
        raise WatchError("binding adapter returned incomplete binding")
    if binding["schema"] != "smallsort-watch-binding-v1":
        raise WatchError("binding schema must be smallsort-watch-binding-v1")
    for key in required - {"schema", "budget_seconds"}:
        if not isinstance(binding[key], str) or not binding[key]:
            raise WatchError(f"binding {key} must be a non-empty string")
    if type(binding["budget_seconds"]) is not int or binding["budget_seconds"] <= 0:
        raise WatchError("binding budget_seconds must be positive")
    _parse_stamp(binding["main_deadline_utc"])
    _parse_stamp(binding["deadline_utc"])
    return json.loads(_json_bytes(binding))


def arm(spec_path: str | Path, store: Store, *, bindings=None, codex=None, now=None, delivery=None):
    path = Path(spec_path)
    spec = _load_json(path)
    keys = {"schema", "worktree", "ledger_path", "thread_id", "build_id", "poll_seconds", "deadline_margin_seconds"}
    optional = {"poll_seconds", "deadline_margin_seconds"}
    if not isinstance(spec, dict) or spec.get("schema") != "smallsort-watch-spec-v1":
        raise WatchError("spec schema must be smallsort-watch-spec-v1")
    if set(spec) - keys or keys - optional - set(spec):
        raise WatchError("spec has missing or unknown keys")
    poll = spec.get("poll_seconds", 30)
    margin = spec.get("deadline_margin_seconds", 180)
    if type(poll) is not int or not 15 <= poll <= 60:
        raise WatchError("poll_seconds must be 15..60")
    if type(margin) is not int or not 30 <= margin <= 600:
        raise WatchError("deadline_margin_seconds must be 30..600")
    for k in ("worktree", "ledger_path", "thread_id", "build_id"):
        if not isinstance(spec[k], str) or not spec[k].strip():
            raise WatchError(f"{k} must be non-empty")
    ledger_rel = PurePosixPath(spec["ledger_path"])
    if (ledger_rel.is_absolute() or ledger_rel.as_posix() != spec["ledger_path"]
            or "\\" in spec["ledger_path"] or "\x00" in spec["ledger_path"]
            or any(part in ("", ".", "..") for part in ledger_rel.parts)):
        raise WatchError("ledger_path must be a safe worktree-relative POSIX path")
    if os.environ.get("CODEX_THREAD_ID") and os.environ["CODEX_THREAD_ID"] != spec["thread_id"]:
        raise WatchError("CODEX_THREAD_ID does not match target thread")
    bindings = bindings or _adapter("watch_bindings")
    codex = codex or _adapter("watch_codex")
    binding = _normalize_binding(bindings.capture(spec))
    expected_ledger = str((Path(binding["worktree"]) / Path(*ledger_rel.parts)).absolute())
    if (binding["thread_id"] != spec["thread_id"]
            or Path(binding["worktree"]).resolve() != Path(spec["worktree"]).resolve()
            or Path(binding["ledger_path"]).absolute() != Path(expected_ledger)
            or binding["build_id"] != spec["build_id"]):
        raise WatchError("spec does not match captured authorization binding")
    thread = _inspect(codex, spec["thread_id"])
    if Path(thread["cwd"]).resolve() != Path(binding["worktree"]).resolve():
        raise WatchError("thread cwd does not match bound worktree")
    if thread["goal_active"] or thread["archived"] or thread["latest_turn_status"] not in ("inProgress", "active", "completed"):
        raise WatchError("thread must be unarchived, goal-free, and idle or completing a turn")
    current = now or _utcnow()
    if _parse_stamp(binding["deadline_utc"]) <= current:
        raise WatchError("binding deadline has already passed")
    with store.lock("store.lock"):
        jobs = store.list_jobs()
        same_scope = [j for j in jobs if
                      (j.get("binding", {}).get("owner"), j.get("binding", {}).get("ledger_path"), j.get("thread_id")) ==
                      (binding["owner"], binding["ledger_path"], spec["thread_id"])]
        if any((j.get("state") in ACTIVE_JOB_STATES | {"DELIVERED", "DELIVERY_UNKNOWN"}
                and not _stop_requested(store, j["job_id"]))
               for j in same_scope):
            raise WatchError("an active watcher already exists for owner/ledger/thread")
        job_id = str(uuid.uuid4())
        job = {"job_id": job_id, "event_id": None, "state": "ARMED", "thread_id": spec["thread_id"],
               "armed_turn_id": thread["latest_turn_id"], "binding": binding,
               "binding_sha256": _digest(binding), "poll_seconds": poll, "deadline_margin_seconds": margin,
               "created_utc": _stamp(current), "updated_utc": _stamp(current), "poll_failures": 0,
               "last_status": None, "attempts": 0, "runner_pid": None, "heartbeat_utc": None}
        if delivery is not None:
            # Non-Codex delivery adapters own their runner and ack; see _require_delivery.
            job["delivery"] = delivery
        state_dir = store.file(job_id + ".state")
        state_dir.mkdir(mode=0o700)
        dfd = os.open(store.root, os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
        store.save_job(job)
    return job


def _require_delivery(job, delivery):
    """Refuse a runner/ack whose delivery adapter differs from the one the job was armed for."""
    if job.get("delivery") != delivery:
        raise WatchError("job delivery mode does not match this command")


def _load_adapters():
    return _adapter("watch_bindings"), _adapter("watch_codex")


def _validate_job(store, job, bindings):
    if _digest(job["binding"]) != job.get("binding_sha256"):
        raise WatchError("frozen authorization binding changed")
    result = bindings.validate(job["binding"])
    if not isinstance(result, dict) or not {"terminal", "status", "accounted"}.issubset(result):
        raise WatchError("binding validation returned incomplete status")
    return result


def _payload(job, status, mode, event_name):
    b = job["binding"]
    payload = {"kind": "technical_data", "event_name": event_name,
               "event_id": job["event_id"], "job_id": job["job_id"], "thread_id": job["thread_id"],
               "owner": b["owner"], "task_id": b["task_id"], "phase": b["phase"], "build_id": b["build_id"],
               "dispatch_token": b["dispatch_token"], "source_sha": b["infra_sha"], "proof_sha": b["proof_sha"],
               "config_sha256": b["config_sha256"], "unchanged_t0": b["t0"],
               "main_deadline_utc": b["main_deadline_utc"], "absolute_deadline_utc": b["deadline_utc"],
               "mode": mode, "status": str(status)[:200], "authority": "UNCHANGED_EXISTING_TASK_ONLY",
               "proof_credit": 0, "ack_required": True,
               "instructions": "Acknowledge this event. Continue only within the existing branch admission and use the Evidence Brief after terminal status."}
    text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(text.encode()) > 3072:
        raise WatchError("notification exceeds 3 KiB")
    return text


def _mark(store, job, state, *, status=None, event_id=None, now=None):
    job["state"] = state
    job["updated_utc"] = _stamp(now)
    if status is not None:
        job["last_status"] = str(status)[:200]
    if event_id is not None:
        job["event_id"] = event_id
    store.save_job(job)


def _stop_requested(store, job_id):
    marker = store.file(job_id + ".stop")
    return marker.exists()


def _attempt_delivery(store, job, bindings, codex, status, mode, event_name, now_fn):
    now = now_fn()
    if now >= _parse_stamp(job["binding"]["deadline_utc"]):
        _mark(store, job, "EXPIRED", status="absolute deadline passed", now=now)
        return
    thread = _inspect(codex, job["thread_id"])
    if Path(thread["cwd"]).resolve() != Path(job["binding"]["worktree"]).resolve():
        _mark(store, job, "STALE", status="thread cwd changed before delivery", now=now_fn())
        return
    if (thread["archived"] or thread["goal_active"]
            or thread["latest_turn_status"] in ("interrupted", "failed")):
        _mark(store, job, "STALE", status="thread state changed before delivery", now=now)
        return
    if thread["latest_turn_id"] != job["armed_turn_id"]:
        _mark(store, job, "STALE", status="thread has a newer turn", now=now)
        return
    if thread["latest_turn_status"] in ("active", "inProgress") or thread["status"] == "active":
        job["pending_terminal_status"] = str(status)[:200]
        job["pending_event_name"] = event_name
        _mark(store, job, "READY", status="waiting for armed turn to finish", now=now)
        return
    if thread["status"] not in ("idle", "unloaded"):
        _mark(store, job, "STALE", status="thread is not safely idle", now=now)
        return
    if thread["latest_turn_status"] != "completed":
        _mark(store, job, "STALE", status="thread is not safely idle", now=now)
        return
    if _stop_requested(store, job["job_id"]):
        _mark(store, job, "STOPPED", status="stopped by operator", now=now_fn())
        return
    try:
        _validate_job(store, job, bindings)
    except Exception as exc:
        binding_error = getattr(bindings, "BindingError", ())
        if binding_error and isinstance(exc, binding_error):
            _mark(store, job, "STALE", status="authorization binding stale before delivery", now=now_fn())
        else:
            job["pending_terminal_status"] = str(status)[:200]
            job["pending_event_name"] = event_name
            _mark(store, job, "READY", status="authority refresh failed; delivery deferred", now=now_fn())
        return
    # Serialize final stop/deadline checks with stop() and keep DELIVERING
    # durable across the bounded queue operation. A crash after this write is
    # always interpreted as DELIVERY_UNKNOWN on restart.
    with store.lock(job["job_id"] + ".lock"):
        current = store.read_job(job["job_id"])
        if current["state"] in TERMINAL_JOB_STATES:
            return
        job.update(current)
        if _stop_requested(store, job["job_id"]) or job.get("stop_requested"):
            _mark(store, job, "STOPPED", status="stopped by operator", now=now_fn())
            return
        now = now_fn()
        remaining = (_parse_stamp(job["binding"]["deadline_utc"]) - now).total_seconds()
        if remaining < MAX_DELIVERY_SECONDS:
            _mark(store, job, "EXPIRED", status="insufficient time for bounded queue delivery", now=now)
            return
        mode = "CLOSEOUT_ONLY" if now >= _parse_stamp(job["binding"]["main_deadline_utc"]) else "CONTINUE_EXISTING_WINDOW"
        if job["attempts"] >= 1:
            _mark(store, job, "DELIVERY_UNKNOWN", status="delivery attempt limit reached", now=now)
            return
        job["event_id"] = str(uuid.uuid4())
        job["attempts"] += 1
        payload = _payload(job, status, mode, event_name)
        job["payload_text"] = payload
        job.pop("pending_terminal_status", None)
        job.pop("pending_event_name", None)
        _mark(store, job, "DELIVERING", status=status, now=now)
        try:
            # Recheck immediately before enqueue while stop() is serialized on
            # this state lock. The adapter itself has a hard 20-second bound.
            if _stop_requested(store, job["job_id"]):
                _mark(store, job, "STOPPED", status="stopped by operator", now=now_fn())
                return
            now = now_fn()
            if (_parse_stamp(job["binding"]["deadline_utc"]) - now).total_seconds() < MAX_DELIVERY_SECONDS:
                _mark(store, job, "EXPIRED", status="insufficient time before enqueue", now=now)
                return
            mode_now = "CLOSEOUT_ONLY" if now >= _parse_stamp(job["binding"]["main_deadline_utc"]) else "CONTINUE_EXISTING_WINDOW"
            if mode_now != mode:
                mode = mode_now
                payload = _payload(job, status, mode, event_name)
                job["payload_text"] = payload
                job["updated_utc"] = _stamp(now)
                store.save_job(job)
            result = codex.deliver(job["thread_id"], payload)
            if not isinstance(result, dict) or not isinstance(result.get("queue_id"), str):
                raise DeliveryUnknown("delivery adapter returned no queue identity")
            job["queue_id"] = result["queue_id"][:200]
            _mark(store, job, "DELIVERED", status=status, now=now_fn())
        except Exception as exc:
            job["delivery_error"] = type(exc).__name__[:100]
            _mark(store, job, "DELIVERY_UNKNOWN", status="enqueue outcome unknown", now=now_fn())


def tick(store: Store, job_id: str, *, bindings=None, codex=None, now_fn=_utcnow):
    bindings = bindings or _adapter("watch_bindings")
    codex = codex or _adapter("watch_codex")
    # Serialize watcher ticks without holding the short state lock across
    # binding validation or coordinator/status IO. stop() uses its own marker.
    with store.lock(job_id + ".tick.lock"):
        job = store.read_job(job_id)
        if job["state"] in TERMINAL_JOB_STATES:
            return job
        if job["state"] == "DELIVERING":
            _mark(store, job, "DELIVERY_UNKNOWN", status="runner restarted during enqueue", now=now_fn())
            return job
        if job.get("stop_requested") or _stop_requested(store, job_id):
            _mark(store, job, "STOPPED", status="stopped by operator", now=now_fn())
            return job
        now = now_fn()
        if now >= _parse_stamp(job["binding"]["deadline_utc"]):
            _mark(store, job, "EXPIRED", status="absolute deadline passed", now=now)
            return job
        try:
            result = _validate_job(store, job, bindings)
        except Exception as exc:
            binding_error = getattr(bindings, "BindingError", ())
            if binding_error and isinstance(exc, binding_error):
                _mark(store, job, "STALE", status="authorization binding stale", now=now)
                return job
            job["poll_failures"] += 1
            if job["poll_failures"] >= 3:
                mode = "CLOSEOUT_ONLY" if now >= _parse_stamp(job["binding"]["main_deadline_utc"]) else "CONTINUE_EXISTING_WINDOW"
                _attempt_delivery(store, job, bindings, codex, "watch status unavailable after three failures",
                                  mode, "monitor_error", now_fn)
            else:
                _mark(store, job, "MONITORING", status="status query failed", now=now)
            return job
        now = now_fn()
        if job.get("stop_requested") or _stop_requested(store, job_id):
            _mark(store, job, "STOPPED", status="stopped by operator", now=now)
            return job
        if now >= _parse_stamp(job["binding"]["deadline_utc"]):
            _mark(store, job, "EXPIRED", status="absolute deadline passed", now=now)
            return job
        if job["state"] == "READY" and job.get("pending_terminal_status") is not None:
            _attempt_delivery(store, job, bindings, codex, job["pending_terminal_status"],
                              "CONTINUE_EXISTING_WINDOW", job.get("pending_event_name", "build_terminal"), now_fn)
            return job
        main_deadline = _parse_stamp(job["binding"]["main_deadline_utc"])
        absolute_deadline = _parse_stamp(job["binding"]["deadline_utc"])
        armed_at = _parse_stamp(job["created_utc"])
        margin = dt.timedelta(seconds=job["deadline_margin_seconds"])
        main_alert = armed_at < main_deadline - margin and now >= main_deadline - margin
        absolute_alert = armed_at >= main_deadline - margin and now >= absolute_deadline - margin
        if main_alert or absolute_alert:
            mode = "CLOSEOUT_ONLY" if now >= main_deadline else "CONTINUE_EXISTING_WINDOW"
            _attempt_delivery(store, job, bindings, codex, "authorization window nearing deadline",
                              mode, "deadline_near", now_fn)
            return job
        if result["terminal"] and result["accounted"]:
            mode = "CLOSEOUT_ONLY" if now >= _parse_stamp(job["binding"]["main_deadline_utc"]) else "CONTINUE_EXISTING_WINDOW"
            _attempt_delivery(store, job, bindings, codex, result["status"], mode, "build_terminal", now_fn)
            return job
        try:
            if _stop_requested(store, job_id):
                _mark(store, job, "STOPPED", status="stopped by operator", now=now_fn())
                return job
            now = now_fn()
            if now >= _parse_stamp(job["binding"]["deadline_utc"]):
                _mark(store, job, "EXPIRED", status="absolute deadline passed before poll", now=now)
                return job
            client_state_dir = store.file(job_id + ".state")
            if client_state_dir.is_symlink() or not client_state_dir.is_dir():
                raise WatchError("private client state directory is missing or unsafe")
            observed = bindings.poll(job["binding"], str(client_state_dir))
            if not isinstance(observed, dict) or not {"terminal", "status", "accounted"}.issubset(observed):
                raise WatchError("poll returned incomplete status")
            if observed["terminal"] and observed["accounted"]:
                job["poll_failures"] = 0
                mode = "CLOSEOUT_ONLY" if now >= _parse_stamp(job["binding"]["main_deadline_utc"]) else "CONTINUE_EXISTING_WINDOW"
                _attempt_delivery(store, job, bindings, codex, observed["status"], mode, "build_terminal", now_fn)
            elif observed["terminal"] and not observed["accounted"]:
                job["poll_failures"] += 1
                if job["poll_failures"] >= 3:
                    mode = "CLOSEOUT_ONLY" if now >= _parse_stamp(job["binding"]["main_deadline_utc"]) else "CONTINUE_EXISTING_WINDOW"
                    _attempt_delivery(store, job, bindings, codex, "terminal status is not yet accounted",
                                      mode, "monitor_error", now_fn)
                else:
                    _mark(store, job, "MONITORING", status="terminal status is not yet accounted", now=now)
            else:
                job["poll_failures"] = 0
                _mark(store, job, "MONITORING", status=observed["status"], now=now)
        except Exception as exc:
            binding_error = getattr(bindings, "BindingError", ())
            if binding_error and isinstance(exc, binding_error):
                _mark(store, job, "STALE", status="authorization binding stale during poll", now=now_fn())
                return job
            job["poll_failures"] += 1
            if job["poll_failures"] >= 3:
                _attempt_delivery(store, job, bindings, codex, "watch status unavailable after three failures",
                                  "CLOSEOUT_ONLY" if now >= _parse_stamp(job["binding"]["main_deadline_utc"]) else "CONTINUE_EXISTING_WINDOW",
                                  "monitor_error", now_fn)
            else:
                _mark(store, job, "MONITORING", status="status query failed", now=now)
        return job


def run_loop(store: Store, job_id: str, *, nonce=None, bindings=None, codex=None, now_fn=_utcnow, sleep=time.sleep, max_cycles=None,
             delivery=None):
    bindings = bindings or _adapter("watch_bindings")
    codex = codex or _adapter("watch_codex")
    cycles = 0
    with store.lock(job_id + ".runner.lock", nonblocking=True):
        with store.lock(job_id + ".lock"):
            job = store.read_job(job_id)
            _require_delivery(job, delivery)
            if nonce is not None and job.get("launch_nonce") != nonce:
                raise WatchError("runner launch nonce is stale")
            job["runner_nonce"] = nonce
            job["runner_pid"] = os.getpid()
            job["heartbeat_utc"] = _stamp(now_fn())
            job["updated_utc"] = job["heartbeat_utc"]
            store.save_job(job)
        while max_cycles is None or cycles < max_cycles:
            job = store.read_job(job_id)
            if job["state"] in TERMINAL_JOB_STATES:
                return job
            # State lock remains short; heartbeat and state updates never wrap I/O.
            with store.lock(job_id + ".lock"):
                job = store.read_job(job_id)
                job["state"] = "MONITORING" if job["state"] == "ARMED" else job["state"]
                job["heartbeat_utc"] = _stamp(now_fn())
                job["updated_utc"] = job["heartbeat_utc"]
                store.save_job(job)
            tick(store, job_id, bindings=bindings, codex=codex, now_fn=now_fn)
            cycles += 1
            job = store.read_job(job_id)
            if job["state"] in TERMINAL_JOB_STATES:
                return job
            remaining = job["poll_seconds"]
            while remaining > 0:
                if store.read_job(job_id).get("stop_requested") or _stop_requested(store, job_id):
                    break
                portion = min(1, remaining)
                sleep(portion)
                remaining -= portion
        return store.read_job(job_id)


def start(store: Store, job_id: str, *, popen=subprocess.Popen, sleep=time.sleep, now_fn=_utcnow):
    with store.lock(job_id + ".start.lock", nonblocking=True):
        # Refuse an already-running child before issuing a new launch token.
        with store.lock(job_id + ".runner.lock", nonblocking=True):
            pass
        with store.lock(job_id + ".lock"):
            job = store.read_job(job_id)
            _require_delivery(job, None)
            if job["state"] not in ("ARMED", "MONITORING", "READY", "DELIVERING"):
                raise WatchError("job is not startable")
            nonce = str(uuid.uuid4())
            job["launch_nonce"] = nonce
            job["runner_nonce"] = None
            job["heartbeat_utc"] = None
            job["runner_pid"] = None
            job["updated_utc"] = _stamp(now_fn())
            store.save_job(job)
        command = [sys.executable, str(Path(__file__).resolve()), "run", "--job", job_id,
                   "--store", str(store.root), "--nonce", nonce]
        proc = popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     close_fds=True, start_new_session=True)
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            current = store.read_job(job_id)
            if current.get("runner_nonce") == nonce and current.get("heartbeat_utc"):
                return {"job_id": job_id, "pid": proc.pid, "state": current["state"]}
            if proc.poll() is not None:
                raise WatchError("watcher runner exited before heartbeat")
            sleep(0.05)
        # Only terminate the exact child returned by this launch.
        with contextlib.suppress(Exception):
            proc.terminate()
        raise WatchError("watcher runner heartbeat not observed within 3 seconds")


def status(store: Store, job_id: str):
    job = store.read_job(job_id)
    result = {k: job.get(k) for k in ("job_id", "state", "event_id", "thread_id", "created_utc", "updated_utc",
                                      "heartbeat_utc", "last_status", "attempts", "queue_id", "delivery_error", "ack_mode")}
    result["stop_requested"] = bool((job.get("stop_requested") or _stop_requested(store, job_id))
                                      and job.get("state") != "ACKED")
    return result


def stop(store: Store, job_id: str, *, now=None):
    job = store.read_job(job_id)
    if job["state"] not in ("ACKED", "STOPPED", "STALE", "EXPIRED"):
        marker = store.file(job_id + ".stop")
        try:
            fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600)
        except FileExistsError:
            fd = None
        if fd is not None:
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
            dfd = os.open(store.root, os.O_RDONLY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        # Do not wait behind an in-flight enqueue/confirmation. The marker is
        # already durable and is checked before ACK; current work can finish.
        try:
            with store.lock(job_id + ".lock", nonblocking=True):
                current = store.read_job(job_id)
                if current["state"] == "ACKED":
                    with contextlib.suppress(FileNotFoundError):
                        marker.unlink()
        except WatchError:
            pass
    return status(store, job_id)


def ack(store: Store, job_id: str, event_id: str, *, bindings=None, codex=None, now=None):
    if not JOB_ID_RE.fullmatch(event_id):
        raise WatchError("invalid event ID")
    bindings = bindings or _adapter("watch_bindings")
    codex = codex or _adapter("watch_codex")
    now_fn = _utcnow if now is None else (lambda: now)
    if os.environ.get("CODEX_THREAD_ID"):
        target = store.read_job(job_id)["thread_id"]
        if os.environ["CODEX_THREAD_ID"] != target:
            raise WatchError("CODEX_THREAD_ID does not match target thread")
    with store.lock(job_id + ".lock"):
        job = store.read_job(job_id)
        _require_delivery(job, None)
        if job["event_id"] != event_id or job["state"] not in ("DELIVERED", "DELIVERY_UNKNOWN"):
            raise WatchError("event does not match an acknowledgeable delivery")
        now = now_fn()
        if _stop_requested(store, job_id):
            raise WatchError("watcher was stopped; queued event cannot be acknowledged")
        _validate_job(store, job, bindings)
        if now >= _parse_stamp(job["binding"]["deadline_utc"]):
            raise WatchError("absolute authorization window has expired")
        if not isinstance(job.get("payload_text"), str) or len(job["payload_text"].encode()) > 3072:
            raise WatchError("persisted event payload is missing or invalid")

        def verify_thread(thread, expected_turn=None):
            if (thread["thread_id"] != job["thread_id"]
                    or Path(thread["cwd"]).resolve() != Path(job["binding"]["worktree"]).resolve()
                    or thread["archived"] or thread["goal_active"]
                    or thread["latest_turn_id"] == job["armed_turn_id"]
                    or thread["latest_turn_status"] not in ("completed", "inProgress")
                    or thread["status"] not in ("idle", "unloaded", "active")):
                raise WatchError("thread does not contain a safe resumed turn for this event")
            if expected_turn is not None and thread["latest_turn_id"] != expected_turn:
                raise WatchError("thread changed during delivery confirmation")

        thread = _inspect(codex, job["thread_id"])
        verify_thread(thread)
        latest_turn_id = thread["latest_turn_id"]
        confirm = getattr(codex, "confirm_delivery", None)
        if not callable(confirm) or confirm(job["thread_id"], latest_turn_id, job["payload_text"]) is not True:
            raise WatchError("latest turn does not confirm the exact queued event")
        thread = _inspect(codex, job["thread_id"])
        verify_thread(thread, latest_turn_id)
        _validate_job(store, job, bindings)
        now = now_fn()
        if _stop_requested(store, job_id):
            raise WatchError("watcher was stopped during acknowledgement")
        if now >= _parse_stamp(job["binding"]["deadline_utc"]):
            raise WatchError("absolute authorization window expired during acknowledgement")
        job["ack_mode"] = ("CLOSEOUT_ONLY" if now >= _parse_stamp(job["binding"]["main_deadline_utc"])
                            else "CONTINUE_EXISTING_WINDOW")
        prior_state = job["state"]
        _mark(store, job, "ACKED", status="acknowledged; no new authorization granted", now=now)
        if _stop_requested(store, job_id):
            job["state"] = prior_state
            job.pop("ack_mode", None)
            job["updated_utc"] = _stamp(now_fn())
            job["last_status"] = "stop requested during acknowledgement"
            store.save_job(job)
            raise WatchError("watcher was stopped during acknowledgement")
        return status(store, job_id)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="smallsort-session watch")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("arm"); p.add_argument("--spec", required=True); p.add_argument("--store", default=str(DEFAULT_STORE))
    for name in ("start", "status", "stop"):
        p = sub.add_parser(name); p.add_argument("--job", required=True); p.add_argument("--store", default=str(DEFAULT_STORE))
    p = sub.add_parser("run"); p.add_argument("--job", required=True); p.add_argument("--store", default=str(DEFAULT_STORE)); p.add_argument("--nonce", required=True)
    p = sub.add_parser("ack"); p.add_argument("--job", required=True); p.add_argument("--event", required=True); p.add_argument("--store", default=str(DEFAULT_STORE))
    args = parser.parse_args(argv)
    try:
        store = Store(args.store)
        if args.command == "arm": result = arm(args.spec, store)
        elif args.command == "start": result = start(store, args.job)
        elif args.command == "run": result = run_loop(store, args.job, nonce=args.nonce)
        elif args.command == "status": result = status(store, args.job)
        elif args.command == "stop": result = stop(store, args.job)
        else: result = ack(store, args.job, args.event)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (WatchError, OSError, ValueError, RuntimeError) as exc:
        print(f"watch: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
