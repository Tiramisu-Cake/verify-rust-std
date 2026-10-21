#!/usr/bin/env python3
"""Opt-in synthetic Codex queue wakeup experiment; never monitors real CI.

Creates one new Luna HIGH thread, two short turns, and archives only that thread.
No proof tools, Cloud calls, existing-thread messages, or coordinator mutations.
Uses the already-running local daemon; never starts/restarts it. No dependencies.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import socket
import stat
import struct
import subprocess
import time
import uuid

MODEL = "gpt-6-luna"
MAX_FRAME = 1024 * 1024
SOCKET = Path("/root/.codex/app-server-control/app-server-control.sock")


class ProbeError(RuntimeError):
    pass


class Rpc:
    def __init__(self):
        # The managed daemon publishes this stable path as a symlink to its
        # private /tmp/codex-daemon-UID socket. Resolve once; do not replace it.
        endpoint = SOCKET.resolve(strict=True)
        info, parent = endpoint.stat(), endpoint.parent.stat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid() or parent.st_uid != os.getuid() or parent.st_mode & 0o022:
            raise ProbeError("expected an existing private Unix control socket owned by this user")
        self.sock = socket.socket(socket.AF_UNIX)
        self.sock.settimeout(10)
        self.sock.connect(str(endpoint))
        key = base64.b64encode(os.urandom(16)).decode()
        request = ("GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\n"
                   "Connection: Upgrade\r\nSec-WebSocket-Key: " + key +
                   "\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(request.encode())
        header = bytearray()
        while not header.endswith(b"\r\n\r\n"):
            header.extend(self.exact(1))
            if len(header) > 8192:
                raise ProbeError("oversize WebSocket handshake")
        expected = base64.b64encode(hashlib.sha1((key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()).digest())
        if not header.startswith(b"HTTP/1.1 101 ") or b"sec-websocket-accept: " + expected.lower() not in bytes(header).lower():
            raise ProbeError("WebSocket handshake not accepted")
        self.serial = 0
        self.thread = None
        self.started = []
        self.completed = []
        self.answers = []
        self.usage = []
        self.request("initialize", {"clientInfo": {"name": "smallsort_queue_synthetic_probe", "version": "0.1.0"}, "capabilities": {"experimentalApi": True}})
        self.send({"method": "initialized", "params": {}})

    def exact(self, size):
        value = bytearray()
        while len(value) < size:
            part = self.sock.recv(size - len(value))
            if not part:
                raise ProbeError("control socket closed")
            value.extend(part)
        return bytes(value)

    def frame(self, opcode, value):
        size = len(value)
        if size > MAX_FRAME:
            raise ProbeError("oversize outgoing frame")
        prefix = bytes([0x80 | opcode, 0x80 | size]) if size < 126 else bytes([0x80 | opcode, 0xFE]) + struct.pack("!H", size) if size < 65536 else bytes([0x80 | opcode, 0xFF]) + struct.pack("!Q", size)
        mask = os.urandom(4)
        self.sock.sendall(prefix + mask + bytes(x ^ mask[i % 4] for i, x in enumerate(value)))

    def send(self, message):
        self.frame(1, json.dumps(message).encode())

    def receive(self, timeout=10):
        self.sock.settimeout(timeout)
        while True:
            first, second = self.exact(2)
            opcode, size = first & 15, second & 127
            if size == 126:
                size = struct.unpack("!H", self.exact(2))[0]
            elif size == 127:
                size = struct.unpack("!Q", self.exact(8))[0]
            if size > MAX_FRAME or second & 128:
                raise ProbeError("oversize or unexpectedly masked server frame")
            value = self.exact(size)
            if opcode == 9:
                self.frame(10, value)
                continue
            if opcode == 8:
                raise ProbeError("server closed WebSocket")
            if opcode == 10:
                continue
            if opcode != 1 or not first & 128:
                raise ProbeError("fragmented/nontext frames are outside this bounded probe")
            message = json.loads(value)
            self.observe(message)
            return message

    def observe(self, message):
        params = message.get("params", {})
        if not self.thread or params.get("threadId") != self.thread:
            return
        method = message.get("method")
        if method == "turn/started":
            self.started.append(params["turn"]["id"])
        elif method == "turn/completed":
            self.completed.append({"id": params["turn"]["id"], "status": params["turn"]["status"]})
        elif method == "thread/tokenUsage/updated":
            self.usage.append(params["tokenUsage"])
        elif method == "item/completed" and params.get("item", {}).get("type") == "agentMessage":
            self.answers.append(params["item"].get("text", "")[:1000])

    def request(self, method, params, timeout=20):
        self.serial += 1
        ident = self.serial
        self.send({"id": ident, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            message = self.receive(max(.05, deadline - time.monotonic()))
            if message.get("id") == ident:
                if "error" in message:
                    raise ProbeError(method + ": " + str(message["error"])[:500])
                return message["result"]
        raise ProbeError(method + " timed out")

    def drain(self, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                self.receive(min(1, max(.05, deadline - time.monotonic())))
            except socket.timeout:
                pass

    def wait_completed(self, count, seconds=120):
        deadline = time.monotonic() + seconds
        while len(self.completed) < count and time.monotonic() < deadline:
            try:
                self.receive(min(10, max(.05, deadline - time.monotonic())))
            except socket.timeout:
                pass
        if len(self.completed) != count or self.completed[-1]["status"] != "completed":
            raise ProbeError("synthetic turn failed or did not complete")


def event_guard(event, expected, seen, now):
    """Synthetic routing check only; NOT production authorization/admission."""
    if any(event.get(key) != expected[key] for key in ("thread_id", "phase", "build_id")):
        return "STALE_IDENTITY"
    if event["event_id"] in seen:
        return "DUPLICATE"
    if now >= expected["absolute"]:
        return "EXPIRED"
    return "CLOSEOUT_ONLY" if now >= expected["main"] else "CONTINUE_EXISTING_WINDOW"


def run(out, idle_seconds):
    if out.exists() or out.is_symlink() or not out.parent.is_dir():
        raise ProbeError("output must be a new directory under an existing parent")
    if any(p.is_symlink() for p in [out, *out.parents]):
        raise ProbeError("symlink output ancestors refused")
    out.mkdir()
    (out / "workspace").mkdir()
    report = {"schema": "smallsort-synthetic-queue-probe-v1", "synthetic": True, "model": MODEL, "effort": "high", "cloud_calls": 0, "proof_credit": 0, "production_watcher_deployed": False}
    rpc = None
    thread = None
    try:
        rpc = Rpc()
        models = rpc.request("model/list", {})
        if not any(x.get("model") == MODEL and any(r.get("reasoningEffort") == "high" for r in x.get("supportedReasoningEfforts", [])) for x in models.get("data", [])):
            raise ProbeError("explicit Luna HIGH unavailable; no model fallback")
        params = {"model": MODEL, "cwd": str(out / "workspace"), "approvalPolicy": "never", "sandbox": "read-only", "config": {"model_reasoning_effort": "high"}, "developerInstructions": "This is only a synthetic queue wakeup test. Do not use tools, inspect files, delegate, or perform actions. Initial answer exactly ARMED_FOR_SYNTHETIC_EVENT; after a SYNTHETIC_EVENT answer exactly SYNTHETIC_EVENT_RECEIVED. No CI authorization is granted."}
        created = rpc.request("thread/start", params)
        thread = created["thread"]["id"]
        if created["model"] != MODEL or created.get("reasoningEffort") != "high":
            raise ProbeError("server did not preserve explicit Luna HIGH")
        rpc.thread = thread
        report["thread_id"] = thread
        rpc.request("thread/name/set", {"threadId": thread, "name": "SmallSort SYNTHETIC queue wakeup probe"})
        rpc.request("turn/start", {"threadId": thread, "model": MODEL, "effort": "high", "input": [{"type": "text", "text": "Synthetic probe: answer ARMED_FOR_SYNTHETIC_EVENT and end this turn. No tools or further work."}]})
        print("ARMING_TEST_THREAD", flush=True)
        rpc.wait_completed(1)
        report["initial_reply"] = rpc.answers[-1] if rpc.answers else None
        before = rpc.request("thread/read", {"threadId": thread, "includeTurns": False})["thread"]["status"]
        count_before = len(rpc.started)
        usage_before = list(rpc.usage)
        start = time.monotonic()
        rpc.drain(idle_seconds)
        after = rpc.request("thread/read", {"threadId": thread, "includeTurns": False})["thread"]["status"]
        report["idle"] = {"observed_seconds": round(time.monotonic() - start, 3), "status_before": before, "status_after": after, "extra_turns_started": len(rpc.started) - count_before, "usage_changed": rpc.usage != usage_before}
        print("IDLE_OBSERVATION " + json.dumps(report["idle"]), flush=True)
        now = time.time()
        expected = {"thread_id": thread, "phase": "SYNTHETIC-NOT-CI", "build_id": "SYNTHETIC-NOT-A-CLOUD-BUILD", "main": now + 7200, "absolute": now + 9000}
        event = {key: expected[key] for key in ("thread_id", "phase", "build_id")}
        event["event_id"] = uuid.uuid4().hex
        state = event_guard(event, expected, set(), now)
        payload = "SYNTHETIC_EVENT " + json.dumps({**event, "kind": "BUILD_TERMINAL", "status": "SUCCESS", "authority": state, "budget_changed": False, "synthetic": True}, sort_keys=True)
        queued = subprocess.run(["codex", "queue", "--remote", "unix://" + str(SOCKET), "--thread", thread, "--message", payload, "-m", MODEL, "-c", 'model_reasoning_effort="high"'], capture_output=True, text=True, timeout=30)
        report["queue_exit"] = queued.returncode
        report["queue_output"] = queued.stdout.strip()[:1000]
        if queued.returncode:
            raise ProbeError("codex queue failed: " + queued.stderr[:500])
        print("QUEUE_ACCEPTED", flush=True)
        rpc.drain(15)
        report["queue_alone_started_turn"] = len(rpc.started) > count_before
        if not report["queue_alone_started_turn"]:
            report["pending_queue"] = rpc.request("thread/queue/list", {"threadId": thread, "limit": 5})
            rpc.request("thread/queue/start", {"threadId": thread})
            report["explicit_queue_start_required"] = True
        else:
            report["explicit_queue_start_required"] = False
        rpc.wait_completed(2)
        report["wake_reply"] = rpc.answers[-1] if rpc.answers else None
        cases = [(event, {event["event_id"]}, now, "DUPLICATE"), ({**event, "phase": "OLD-PHASE"}, set(), now, "STALE_IDENTITY"), ({**event, "build_id": "OTHER-BUILD"}, set(), now, "STALE_IDENTITY"), ({**event, "thread_id": "OTHER-THREAD"}, set(), now, "STALE_IDENTITY"), (event, set(), expected["main"], "CLOSEOUT_ONLY"), (event, set(), expected["absolute"], "EXPIRED")]
        report["routing_guards"] = []
        for ev, seen, when, answer in cases:
            actual = event_guard(ev, expected, seen, when)
            if actual != answer:
                raise ProbeError("synthetic routing guard failed")
            report["routing_guards"].append(actual)
        rpc.drain(1)
        report["turns_started"] = len(rpc.started)
        report["turns_completed"] = rpc.completed
        report["usage"] = rpc.usage
        report["result"] = "PASS" if (report["initial_reply"] == "ARMED_FOR_SYNTHETIC_EVENT" and report["wake_reply"] == "SYNTHETIC_EVENT_RECEIVED" and report["idle"]["extra_turns_started"] == 0 and not report["idle"]["usage_changed"] and len(rpc.started) == 2) else "INCONCLUSIVE"
    except Exception as exc:
        report["result"] = "ERROR"
        report["error"] = str(exc)[:1000]
    finally:
        if thread and rpc:
            active = [ident for ident in rpc.started if ident not in {x["id"] for x in rpc.completed}]
            for ident in active:
                try:
                    rpc.request("turn/interrupt", {"threadId": thread, "turnId": ident})
                except Exception:
                    pass
            try:
                rpc.request("thread/archive", {"threadId": thread})
                report["only_created_test_thread_archived"] = True
            except Exception as exc:
                report["archive_error"] = str(exc)[:500]
        if rpc:
            rpc.sock.close()
        (out / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("PROBE_RESULT " + json.dumps({key: report.get(key) for key in ("result", "thread_id", "queue_alone_started_turn", "explicit_queue_start_required", "turns_started", "error")}), flush=True)
    return 0 if report["result"] == "PASS" else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-real-probe", action="store_true", required=True, help="explicitly allow two synthetic Luna HIGH turns")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--idle-seconds", type=int, default=30, choices=range(10, 61))
    args = parser.parse_args()
    return run(args.out.absolute(), args.idle_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
