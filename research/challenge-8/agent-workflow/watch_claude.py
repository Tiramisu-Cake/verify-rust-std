"""Claude Code foreground delivery for the existing Build watcher.

The agent runs `smallsort-session wait run` as its own background Bash task and
ends the turn. Monitoring, authority checks, deadlines and the single delivery
attempt stay in build_watch; delivery writes the technical_data event to this
process's stdout (flushed before the job becomes DELIVERED) and the process
exits, so Claude Code returns the output to the same session. No Codex queue,
Claude CLI, network or model call is made here.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time

import build_watch as bw

DELIVERY = "claude-foreground"
TURN = "claude-foreground"
EXIT_NOT_DELIVERED = 3
MAX_ANCESTORS = 64


class Adapter:
    """Delivery adapter bound to the calling top-level Claude Code session.

    CLAUDE_CODE_SESSION_ID must equal the job thread_id, CLAUDE_PID must be a
    `claude` ancestor of this process, and that process cwd must be the assigned
    worktree (as for Codex thread cwd). Subagents share all of these (including
    CLAUDE_CODE_CHILD_SESSION, which the main session's shells also carry), so
    "main session only" is a procedural rule in WATCH-CLAUDE.md. Turn ordering is
    Claude Code's own background-task notification, so the reported turn is
    constant and never blocks delivery.
    """
    def __init__(self, environ=None, proc=Path("/proc"), pid=None, stdout=None):
        self.environ = os.environ if environ is None else environ
        self.proc = proc
        self.pid = os.getpid() if pid is None else pid
        self.stdout = stdout

    def _session(self, thread_id):
        session = self.environ.get("CLAUDE_CODE_SESSION_ID")
        if not session or session != thread_id:
            raise bw.WatchError("CLAUDE_CODE_SESSION_ID does not match target session")

    def _parent(self, pid):
        try:
            stat = (self.proc / str(pid) / "stat").read_text()
        except OSError:
            return None
        fields = stat[stat.rfind(")") + 1:].split()
        return int(fields[1]) if len(fields) > 1 and fields[1].isdigit() else None

    def _cwd(self):
        raw = self.environ.get("CLAUDE_PID", "")
        if not raw.isdigit():
            raise bw.WatchError("CLAUDE_PID is missing")
        pid, seen = self.pid, 0
        while pid and pid != int(raw) and seen < MAX_ANCESTORS:
            pid, seen = self._parent(pid), seen + 1
        if pid != int(raw):
            raise bw.WatchError("CLAUDE_PID is not an ancestor of this process")
        try:
            comm = (self.proc / raw / "comm").read_text().strip()
        except OSError:
            comm = ""
        if comm != "claude":
            raise bw.WatchError("CLAUDE_PID is not a Claude Code process")
        link = self.proc / raw / "cwd"
        if not link.is_symlink():
            raise bw.WatchError("Claude Code process cwd is unavailable")
        return str(link.resolve())

    def inspect_thread(self, thread_id):
        self._session(thread_id)
        return {"thread_id": thread_id, "cwd": self._cwd(), "status": "idle", "latest_turn_id": TURN,
                "latest_turn_status": "completed", "goal_active": False, "archived": False}

    def deliver(self, thread_id, payload_text):
        self._session(thread_id)
        _emit(self.stdout or sys.stdout, json.loads(payload_text))
        return {"queue_id": f"{DELIVERY}:{os.getpid()}"}


def _emit(stream, event, replay=False):
    line = {"event": event, "next": (f"smallsort-session wait ack --job {event['job_id']} "
                                     f"--event {event['event_id']} before changing CHECKPOINT")}
    if replay:
        line["replay"] = True
    stream.write(json.dumps(line, ensure_ascii=False, sort_keys=True) + "\n")
    stream.flush()


def _bound_session(adapter, job):
    if job.get("delivery") != DELIVERY:
        raise bw.WatchError("job was not armed for Claude foreground delivery")
    thread = adapter.inspect_thread(job["thread_id"])
    if Path(thread["cwd"]).resolve() != Path(job["binding"]["worktree"]).resolve():
        raise bw.WatchError("session cwd does not match bound worktree")


def arm(store: bw.Store, spec, *, bindings=None, adapter=None, now=None):
    return bw.arm(spec, store, bindings=bindings or bw._adapter("watch_bindings"), codex=adapter or Adapter(),
                  now=now, delivery=DELIVERY)


def wait(store: bw.Store, job_id: str, *, bindings=None, adapter=None, now_fn=bw._utcnow, sleep=time.sleep,
         max_cycles=None):
    """Monitor an armed or interrupted Claude job in the foreground until it leaves the active states."""
    bindings = bindings or bw._adapter("watch_bindings")
    adapter = adapter or Adapter()
    job = store.read_job(job_id)
    _bound_session(adapter, job)
    if job["state"] in bw.TERMINAL_JOB_STATES:
        return job
    return bw.run_loop(store, job_id, bindings=bindings, codex=adapter, now_fn=now_fn, sleep=sleep,
                       max_cycles=max_cycles, delivery=DELIVERY)


def ack(store: bw.Store, job_id: str, event_id: str, *, bindings=None, adapter=None, now=None):
    """Acknowledge a delivered event from the same session after the wait process exited."""
    if not bw.JOB_ID_RE.fullmatch(event_id):
        raise bw.WatchError("invalid event ID")
    bindings = bindings or bw._adapter("watch_bindings")
    adapter = adapter or Adapter()
    now_fn = bw._utcnow if now is None else (lambda: now)
    # A still-running foreground runner means the event has not reached the session.
    with store.lock(job_id + ".runner.lock", nonblocking=True):
        pass
    with store.lock(job_id + ".lock"):
        job = store.read_job(job_id)
        _bound_session(adapter, job)
        if job["event_id"] != event_id or job["state"] != "DELIVERED":
            raise bw.WatchError("event does not match an acknowledgeable delivery")
        if bw._stop_requested(store, job_id):
            raise bw.WatchError("watcher was stopped; event cannot be acknowledged")
        bw._validate_job(store, job, bindings)
        now = now_fn()
        if now >= bw._parse_stamp(job["binding"]["deadline_utc"]):
            raise bw.WatchError("absolute authorization window has expired")
        if not isinstance(job.get("payload_text"), str) or len(job["payload_text"].encode()) > 3072:
            raise bw.WatchError("persisted event payload is missing or invalid")
        job["ack_mode"] = ("CLOSEOUT_ONLY" if now >= bw._parse_stamp(job["binding"]["main_deadline_utc"])
                           else "CONTINUE_EXISTING_WINDOW")
        bw._mark(store, job, "ACKED", status="acknowledged; no new authorization granted", now=now)
        if bw._stop_requested(store, job_id):
            job["state"] = "DELIVERED"
            job.pop("ack_mode", None)
            job["updated_utc"] = bw._stamp(now_fn())
            job["last_status"] = "stop requested during acknowledgement"
            store.save_job(job)
            raise bw.WatchError("watcher was stopped during acknowledgement")
        return bw.status(store, job_id)


def run(store: bw.Store, *, spec=None, job_id=None, bindings=None, adapter=None, out=None, now_fn=bw._utcnow, **kw):
    """CLI body of `wait run`: returns the exit code and writes JSON lines to out."""
    out = out or sys.stdout
    adapter = adapter or Adapter(stdout=out)
    if spec is not None:
        job_id = arm(store, spec, bindings=bindings, adapter=adapter, now=now_fn())["job_id"]
        out.write(json.dumps({"armed_job": job_id}) + "\n")
        out.flush()
    elif store.read_job(job_id)["state"] == "DELIVERED" and not bw._stop_requested(store, job_id):
        job = store.read_job(job_id)
        _bound_session(adapter, job)
        _emit(out, json.loads(job["payload_text"]), replay=True)
    try:
        job = wait(store, job_id, bindings=bindings, adapter=adapter, now_fn=now_fn, **kw)
    except Exception as exc:
        raise bw.WatchError(f"{exc}; job {job_id} may still be active, check "
                            f"`smallsort-session watch status --job {job_id}`") from exc
    out.write(json.dumps({"job": bw.status(store, job_id)}, ensure_ascii=False, sort_keys=True) + "\n")
    out.flush()
    delivered = job["state"] == "DELIVERED" and not bw._stop_requested(store, job_id)
    return 0 if delivered else EXIT_NOT_DELIVERED


def main(argv=None):
    parser = argparse.ArgumentParser(prog="smallsort-session wait")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("run")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--spec"); group.add_argument("--job")
    p.add_argument("--store", default=str(bw.DEFAULT_STORE))
    p = sub.add_parser("ack"); p.add_argument("--job", required=True); p.add_argument("--event", required=True)
    p.add_argument("--store", default=str(bw.DEFAULT_STORE))
    args = parser.parse_args(argv)
    try:
        store = bw.Store(args.store)
        if args.command == "run":
            return run(store, spec=args.spec, job_id=args.job)
        print(json.dumps(ack(store, args.job, args.event), ensure_ascii=False, sort_keys=True))
        return 0
    except (bw.WatchError, OSError, ValueError, RuntimeError) as exc:
        print(f"wait: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
