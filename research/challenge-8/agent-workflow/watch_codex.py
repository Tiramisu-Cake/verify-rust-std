"""Bounded read-only Codex inspection and explicit queue delivery adapter.

This module never starts or configures the managed app server.  Its RPC surface
is intentionally limited to thread metadata reads; queue delivery is a
separate, explicit subprocess operation for a caller that has already checked
all admission bindings.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import socket
import stat
import struct
import subprocess
import time
import uuid

SOCKET_LINK = Path("/root/.codex/app-server-control/app-server-control.sock")
MAX_FRAME = 1024 * 1024
MAX_MESSAGE = 1024 * 1024
MAX_JSON = 1024 * 1024
MAX_PAYLOAD = 3072
MAX_CAPTURE = 64 * 1024
RPC_TIMEOUT = 8.0
QUEUE_TIMEOUT = 20.0
ALLOWED_RPC = frozenset({"initialize", "thread/read", "thread/turns/list", "thread/items/list", "thread/goal/get"})
_IGNORED_NOTIFICATIONS = frozenset({
    "configWarning", "remoteControl/status/changed", "account/updated",
})
_UUID = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


class AdapterError(RuntimeError):
    """The adapter could not establish a bounded, well-typed result."""


class DeliveryUnknown(AdapterError):
    """Queue submission may have arrived; automatic retry is unsafe."""


def _json_object(data: bytes) -> dict:
    if len(data) > MAX_JSON:
        raise AdapterError("oversize JSON message")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=pairs)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise AdapterError("invalid bounded JSON message") from exc
    if not isinstance(value, dict):
        raise AdapterError("JSON-RPC message must be an object")
    return value


class _WebSocketRpc:
    """Minimal client WebSocket with bounded frames and strict JSON-RPC."""

    def __init__(self, socket_path: Path = SOCKET_LINK, socket_factory=socket.socket):
        self.sock = None
        self.buf = bytearray()
        self.serial = 0
        self.closed = False
        try:
            endpoint = Path(socket_path).resolve(strict=True)
            endpoint_info = endpoint.stat()
            parent_info = endpoint.parent.stat()
            if (not stat.S_ISSOCK(endpoint_info.st_mode)
                    or endpoint_info.st_uid != os.getuid()
                    or parent_info.st_uid != os.getuid()
                    or parent_info.st_mode & 0o077):
                raise AdapterError("control endpoint is not an owned private Unix socket")
            self.sock = socket_factory(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(RPC_TIMEOUT)
            self.sock.connect(str(endpoint))
            self._handshake()
            self.request("initialize", {
                "clientInfo": {"name": "smallsort_codex_watcher", "version": "1.0"},
                "capabilities": {"experimentalApi": False},
            })
            self._send_json({"method": "initialized", "params": {}})
        except Exception:
            self.close()
            raise

    def close(self):
        if self.sock is not None and not self.closed:
            self.closed = True
            try:
                self.sock.close()
            except OSError:
                pass

    def __enter__(self):
        return self

    def __exit__(self, *_exc):
        self.close()

    def _recv(self, count: int, deadline: float | None = None) -> bytes:
        while len(self.buf) < count:
            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise AdapterError("RPC deadline expired")
                self.sock.settimeout(remaining)
            try:
                part = self.sock.recv(min(65536, max(1, count - len(self.buf))))
            except socket.timeout as exc:
                raise AdapterError("control socket timed out") from exc
            except OSError as exc:
                raise AdapterError("control socket read failed") from exc
            if not part:
                raise AdapterError("control socket reached EOF")
            self.buf.extend(part)
            if len(self.buf) > MAX_MESSAGE + 8192:
                raise AdapterError("buffer cap exceeded")
        value = bytes(self.buf[:count])
        del self.buf[:count]
        return value

    def _handshake(self):
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = ("GET / HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\n"
                   "Connection: Upgrade\r\nSec-WebSocket-Key: " + key +
                   "\r\nSec-WebSocket-Version: 13\r\n\r\n").encode("ascii")
        self.sock.sendall(request)
        response = bytearray()
        while b"\r\n\r\n" not in response:
            response.extend(self._recv(1))
            if len(response) > 8192:
                raise AdapterError("oversize WebSocket handshake")
        header, remainder = bytes(response).split(b"\r\n\r\n", 1)
        self.buf[:0] = remainder
        try:
            lines = header.decode("latin1").split("\r\n")
            fields = {}
            for line in lines[1:]:
                if ":" not in line:
                    raise ValueError("malformed header")
                name, value = line.split(":", 1)
                name = name.strip().lower()
                if name in fields:
                    raise ValueError("duplicate header")
                fields[name] = value.strip()
        except ValueError as exc:
            raise AdapterError("malformed WebSocket handshake") from exc
        expected = base64.b64encode(hashlib.sha1(
            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")
        ).digest()).decode("ascii")
        if (not lines[0].startswith("HTTP/1.1 101 ")
                or fields.get("upgrade", "").lower() != "websocket"
                or "upgrade" not in [part.strip() for part in fields.get("connection", "").lower().split(",")]
                or fields.get("sec-websocket-accept") != expected):
            raise AdapterError("WebSocket accept handshake mismatch")

    def _send_frame(self, opcode: int, payload: bytes):
        if len(payload) > MAX_FRAME:
            raise AdapterError("oversize outgoing WebSocket frame")
        n = len(payload)
        if n < 126:
            head = bytes((0x80 | opcode, 0x80 | n))
        elif n <= 0xFFFF:
            head = bytes((0x80 | opcode, 0x80 | 126)) + struct.pack("!H", n)
        else:
            head = bytes((0x80 | opcode, 0x80 | 127)) + struct.pack("!Q", n)
        mask = os.urandom(4)
        masked = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
        try:
            self.sock.sendall(head + mask + masked)
        except (OSError, socket.timeout) as exc:
            raise AdapterError("control socket write failed") from exc

    def _send_json(self, message: dict):
        payload = json.dumps(message, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if len(payload) > MAX_JSON:
            raise AdapterError("oversize outgoing JSON")
        self._send_frame(1, payload)

    def _frame(self, deadline: float) -> tuple[int, bool, bytes]:
        first, second = self._recv(2, deadline)
        if second & 0x80:
            raise AdapterError("masked server WebSocket frame")
        opcode = first & 0x0F
        fin = bool(first & 0x80)
        size = second & 0x7F
        if size == 126:
            size = struct.unpack("!H", self._recv(2, deadline))[0]
            if size < 126:
                raise AdapterError("noncanonical WebSocket frame length")
        elif size == 127:
            raw = self._recv(8, deadline)
            if raw[0] & 0x80:
                raise AdapterError("invalid WebSocket frame length")
            size = struct.unpack("!Q", raw)[0]
            if size <= 0xFFFF:
                raise AdapterError("noncanonical WebSocket frame length")
        if size > MAX_FRAME:
            raise AdapterError("oversize WebSocket frame")
        if opcode >= 8 and (not fin or size > 125):
            raise AdapterError("invalid WebSocket control frame")
        return opcode, fin, self._recv(size, deadline)

    def _receive_json(self, deadline: float) -> dict:
        fragments = bytearray()
        fragmenting = False
        while True:
            opcode, fin, data = self._frame(deadline)
            if opcode == 9:
                self._send_frame(10, data)
                continue
            if opcode == 10:
                continue
            if opcode == 8:
                raise AdapterError("server closed WebSocket")
            if opcode == 1:
                if fragmenting:
                    raise AdapterError("nested fragmented WebSocket message")
                fragments.extend(data)
                fragmenting = not fin
            elif opcode == 0:
                if not fragmenting:
                    raise AdapterError("unexpected WebSocket continuation")
                fragments.extend(data)
                fragmenting = not fin
            else:
                raise AdapterError("unsupported WebSocket opcode")
            if len(fragments) > MAX_MESSAGE:
                raise AdapterError("oversize WebSocket message")
            if not fragmenting:
                return _json_object(bytes(fragments))

    def request(self, method: str, params: dict, timeout: float = RPC_TIMEOUT) -> dict:
        if method not in ALLOWED_RPC:
            raise AdapterError("RPC method is outside the read-only allowlist")
        deadline = time.monotonic() + min(max(timeout, 0.01), RPC_TIMEOUT)
        self.serial += 1
        ident = self.serial
        self.sock.settimeout(max(0.001, deadline - time.monotonic()))
        self._send_json({"id": ident, "method": method, "params": params})
        while True:
            message = self._receive_json(deadline)
            if message.get("method") is not None:
                if message.get("method") in _IGNORED_NOTIFICATIONS:
                    continue
                raise AdapterError("unexpected server RPC notification")
            if message.get("id") != ident:
                raise AdapterError("unexpected JSON-RPC response id")
            if "error" in message:
                raise AdapterError("Codex RPC returned an error")
            result = message.get("result")
            if not isinstance(result, dict):
                raise AdapterError("Codex RPC result has an unknown shape")
            return result


def inspect_thread(thread_id: str) -> dict:
    """Read thread, latest turn, and goal metadata from the managed daemon."""
    if not isinstance(thread_id, str) or not _UUID.fullmatch(thread_id):
        raise AdapterError("thread id must be a UUID")
    with _WebSocketRpc() as rpc:
        read = rpc.request("thread/read", {"threadId": thread_id, "includeTurns": False})
        thread = read.get("thread")
        if not isinstance(thread, dict) or thread.get("id") != thread_id:
            raise AdapterError("thread is absent or response identity mismatched")
        cwd = thread.get("cwd")
        rollout_path = thread.get("path")
        status_obj = thread.get("status")
        if not isinstance(cwd, str) or not os.path.isabs(cwd):
            raise AdapterError("thread cwd is missing or malformed")
        if not isinstance(rollout_path, str) or not os.path.isabs(rollout_path):
            raise AdapterError("thread rollout path is unavailable; archive state is unknown")
        if not isinstance(status_obj, dict) or status_obj.get("type") not in {"active", "idle", "notLoaded", "systemError"}:
            raise AdapterError("thread runtime status is unknown")
        if status_obj["type"] == "active" and not isinstance(status_obj.get("activeFlags"), list):
            raise AdapterError("active thread status is malformed")
        runtime_status = "unloaded" if status_obj["type"] == "notLoaded" else status_obj["type"]
        archived = _archive_state(rollout_path)
        turns = rpc.request("thread/turns/list", {
            "threadId": thread_id, "limit": 1, "sortDirection": "desc", "itemsView": "notLoaded",
        }).get("data")
        if not isinstance(turns, list) or len(turns) > 1:
            raise AdapterError("latest-turn response has unknown shape")
        if turns:
            turn = turns[0]
            if not isinstance(turn, dict) or not isinstance(turn.get("id"), str):
                raise AdapterError("latest turn is malformed")
            turn_id = turn["id"]
            turn_status = turn.get("status")
            if turn_status not in {"completed", "interrupted", "failed", "inProgress"}:
                raise AdapterError("latest turn status is unknown")
        else:
            turn_id = None
            turn_status = None
        goal_result = rpc.request("thread/goal/get", {"threadId": thread_id})
        if "goal" not in goal_result:
            raise AdapterError("goal response is missing its required goal field")
        goal = goal_result.get("goal")
        if goal is None:
            goal_active = False
        elif isinstance(goal, dict) and goal.get("threadId") == thread_id and goal.get("status") in {
            "active", "paused", "blocked", "usageLimited", "budgetLimited", "complete",
        }:
            goal_active = goal["status"] != "complete"
        else:
            raise AdapterError("goal response has unknown shape")
        return {
            "thread_id": thread_id,
            "cwd": cwd,
            "status": runtime_status,
            "latest_turn_id": turn_id,
            "latest_turn_status": turn_status,
            "goal_active": goal_active,
            "archived": archived,
        }


def _archive_state(rollout_path: str) -> bool:
    """Classify only known Codex rollout directories; unknown paths fail closed."""
    codex_home = Path.home() / ".codex"
    try:
        relative = Path(rollout_path).relative_to(codex_home)
    except ValueError as exc:
        raise AdapterError("thread rollout path is outside the managed Codex home") from exc
    if not relative.parts or len(relative.parts) < 2 or ".." in relative.parts:
        raise AdapterError("thread rollout path does not identify a known session store")
    if relative.parts[0] == "archived_sessions":
        return True
    if relative.parts[0] in {"sessions", "threads"}:
        return False
    raise AdapterError("thread rollout path uses an unknown session store")


def _validate_payload(payload_text: str) -> None:
    if not isinstance(payload_text, str):
        raise AdapterError("payload must be text")
    payload_bytes = payload_text.encode("utf-8")
    if len(payload_bytes) > MAX_PAYLOAD:
        raise AdapterError("payload exceeds 3072 bytes")
    payload = _json_object(payload_bytes)
    if payload.get("kind") != "technical_data":
        raise AdapterError("payload kind must be technical_data")


def confirm_delivery(thread_id: str, latest_turn_id: str, payload_text: str) -> bool:
    """Confirm a queued payload was persisted as the sole user steer in its turn.

    A receipt mismatch returns False. Transport or unknown-schema failures raise
    AdapterError so the caller cannot mistake an unreadable result for a match.
    """
    if not isinstance(thread_id, str) or not _UUID.fullmatch(thread_id):
        raise AdapterError("thread id must be a UUID")
    if not isinstance(latest_turn_id, str) or not _UUID.fullmatch(latest_turn_id):
        raise AdapterError("latest turn id must be a UUID")
    _validate_payload(payload_text)
    with _WebSocketRpc() as rpc:
        result = rpc.request("thread/items/list", {
            "threadId": thread_id,
            "turnId": latest_turn_id,
            "limit": 20,
        })
    data = result.get("data")
    if not isinstance(data, list):
        raise AdapterError("item-history response has unknown shape")
    if len(data) > 20:
        return False
    # Missing cursor is also unknown: only an explicit null proves one page is
    # complete, and a non-null cursor means the bounded page was incomplete.
    if "nextCursor" not in result or result["nextCursor"] is not None:
        return False
    items = []
    for entry in data:
        if not isinstance(entry, dict) or entry.get("turnId") != latest_turn_id:
            return False
        item = entry.get("item")
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(item.get("type"), str):
            return False
        items.append(item)
    user_messages = [item for item in items if item["type"] == "userMessage"]
    if len(user_messages) != 1:
        return False
    content = user_messages[0].get("content")
    if not isinstance(content, list) or len(content) != 1:
        return False
    text_input = content[0]
    return (isinstance(text_input, dict)
            and text_input.get("type") == "text"
            and text_input.get("text") == payload_text)


def _drain_bounded(pipe, output: bytearray) -> bool:
    """Drain one ready pipe chunk; retain only a bounded diagnostic prefix."""
    try:
        part = os.read(pipe.fileno(), 8192)
    except BlockingIOError:
        return True
    if not part:
        return False
    if len(output) < MAX_CAPTURE:
        output.extend(part[:MAX_CAPTURE - len(output)])
    return True


def _digest(data: bytearray) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def deliver(thread_id: str, payload_text: str) -> dict:
    """Queue one typed technical-data JSON message; never retries ambiguity."""
    if not isinstance(thread_id, str) or not _UUID.fullmatch(thread_id):
        raise AdapterError("thread id must be a UUID")
    _validate_payload(payload_text)
    executable = shutil.which("codex")
    if not executable or not os.path.isabs(executable):
        raise DeliveryUnknown("codex executable unavailable; delivery state unknown")
    try:
        endpoint = SOCKET_LINK.resolve(strict=True)
        st = endpoint.stat()
        parent = endpoint.parent.stat()
        if (not stat.S_ISSOCK(st.st_mode) or st.st_uid != os.getuid()
                or parent.st_uid != os.getuid() or parent.st_mode & 0o077):
            raise AdapterError("control endpoint is not an owned private Unix socket")
    except AdapterError:
        raise
    except OSError as exc:
        raise DeliveryUnknown("control endpoint unavailable; delivery state unknown") from exc
    argv = [executable, "queue", "--remote", "unix://" + str(endpoint),
            "--thread", thread_id, "--message", payload_text]
    proc = None
    stdout, stderr = bytearray(), bytearray()
    try:
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, close_fds=True, start_new_session=True)
        for stream in (proc.stdout, proc.stderr):
            os.set_blocking(stream.fileno(), False)
        selector = selectors.DefaultSelector()
        selector.register(proc.stdout, selectors.EVENT_READ, stdout)
        selector.register(proc.stderr, selectors.EVENT_READ, stderr)
        deadline = time.monotonic() + QUEUE_TIMEOUT
        open_streams = 2
        while open_streams or proc.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError
            for key, _ in selector.select(min(remaining, 0.25)):
                if not _drain_bounded(key.fileobj, key.data):
                    selector.unregister(key.fileobj)
                    open_streams -= 1
            if proc.poll() is not None and not selector.get_map():
                break
        rc = proc.wait(timeout=0.2)
        selector.close()
    except Exception as exc:
        if proc is not None and proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except OSError:
                pass
        if proc is not None:
            try:
                proc.wait(timeout=1)
            except Exception:
                pass
            for stream in (proc.stdout, proc.stderr):
                try:
                    stream.close()
                except Exception:
                    pass
        raise DeliveryUnknown(
            "queue delivery outcome unknown (" + type(exc).__name__ +
            "; stdout sha256 " + _digest(stdout) + "; stderr sha256 " + _digest(stderr) + ")"
        ) from None
    for stream in (proc.stdout, proc.stderr):
        stream.close()
    if rc != 0:
        raise DeliveryUnknown("queue delivery outcome unknown (exit " + str(rc) +
                              "; stdout sha256 " + _digest(stdout) +
                              "; stderr sha256 " + _digest(stderr) + ")")
    try:
        ack = stdout.decode("utf-8").strip()
    except UnicodeDecodeError:
        ack = ""
    match = re.fullmatch(r"Queued message ([0-9a-fA-F-]{36}) for thread ([0-9a-fA-F-]{36})\.", ack)
    if (not match or not _UUID.fullmatch(match.group(1))
            or not _UUID.fullmatch(match.group(2)) or match.group(2).lower() != thread_id.lower()):
        raise DeliveryUnknown("queue acknowledgement malformed or mismatched (stdout sha256 " +
                              _digest(stdout) + "; stderr sha256 " + _digest(stderr) + ")")
    return {"queue_id": match.group(1)}
