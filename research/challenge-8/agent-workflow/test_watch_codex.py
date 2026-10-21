from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import tempfile
import unittest
from unittest import mock

import watch_codex as wc


THREAD = "019a0000-0000-7000-8000-000000000001"
TURN = "019a0000-0000-7000-8000-000000000002"
GOAL = "019a0000-0000-7000-8000-000000000003"
QUEUE = "019a0000-0000-7000-8000-000000000004"
PAYLOAD = json.dumps({"kind": "technical_data", "value": "receipt"}, separators=(",", ":"))


def frame(opcode, data=b"", fin=True):
    n = len(data)
    head = bytes(((0x80 if fin else 0) | opcode, n)) if n < 126 else bytes(
        ((0x80 if fin else 0) | opcode, 126)) + struct.pack("!H", n)
    return head + data


class FakeSocket:
    """In-memory server speaking only enough WebSocket for deterministic tests."""

    def __init__(self, modes=()):
        self.incoming = bytearray()
        self.sent = bytearray()
        self.closed = False
        self.modes = set(modes)
        self.requests = []
        self.client_opcodes = []
        self.chunk = 3

    def settimeout(self, _value):
        pass

    def connect(self, _path):
        pass

    def close(self):
        self.closed = True

    def recv(self, size):
        if not self.incoming:
            raise socket.timeout()
        take = min(size, self.chunk, len(self.incoming))
        data = bytes(self.incoming[:take])
        del self.incoming[:take]
        return data

    def sendall(self, data):
        self.sent.extend(data)
        if b"\r\n\r\n" in self.sent and not getattr(self, "handshaken", False):
            request, remainder = bytes(self.sent).split(b"\r\n\r\n", 1)
            key_line = next(line for line in request.split(b"\r\n") if line.lower().startswith(b"sec-websocket-key:"))
            key = key_line.split(b":", 1)[1].strip()
            accept = base64.b64encode(hashlib.sha1(key + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
            if "bad-accept" in self.modes:
                accept = b"wrong"
            self.incoming.extend(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + accept + b"\r\n\r\n")
            self.sent.clear()
            self.handshaken = True
            if "http-extra-frame" in self.modes:
                self.incoming.extend(frame(1, b'{"id":1,"result":{}}'))
            return
        # Client frames are masked; parse complete one-frame JSON messages.
        while len(self.sent) >= 6:
            first, second = self.sent[0], self.sent[1]
            n = second & 0x7f
            prefix = 2
            if n == 126:
                if len(self.sent) < 8:
                    return
                n, prefix = struct.unpack("!H", self.sent[2:4])[0], 4
            total = prefix + 4 + n
            if len(self.sent) < total:
                return
            mask = self.sent[prefix:prefix + 4]
            body = self.sent[prefix + 4:total]
            payload = bytes(b ^ mask[i % 4] for i, b in enumerate(body))
            del self.sent[:total]
            self.client_opcodes.append(first & 0x0f)
            if first & 0x0f == 10:  # pong
                continue
            if first & 0x0f != 1:
                raise AssertionError("unexpected client frame opcode")
            msg = json.loads(payload)
            if msg.get("method") == "initialized":
                continue
            self.requests.append(msg)
            response = {"id": msg["id"], "result": self.response(msg["method"], msg.get("params", {}))}
            encoded = json.dumps(response).encode()
            if "ping" in self.modes and msg["method"] == "thread/read":
                self.incoming.extend(frame(9, b"ping"))
            if "fragmented" in self.modes and msg["method"] == "thread/read":
                mid = len(encoded) // 2
                self.incoming.extend(frame(1, encoded[:mid], fin=False))
                self.incoming.extend(frame(0, encoded[mid:], fin=True))
            else:
                self.incoming.extend(frame(1, encoded))

    def response(self, method, params):
        if "unknown-result" in self.modes and method == "thread/read":
            return {"unknown": True}
        if method == "initialize":
            return {}
        if method == "thread/read":
            path = "/root/.codex/archived_sessions/test.jsonl" if "archived-path" in self.modes else "/root/.codex/sessions/test.jsonl"
            return {"thread": {"id": THREAD, "cwd": "/tmp/work", "path": path, "status": {"type": "idle"}}}
        if method == "thread/turns/list":
            return {"data": [{"id": TURN, "status": "completed", "items": [], "itemsView": "notLoaded"}]}
        if method == "thread/goal/get":
            return {"goal": {"threadId": THREAD, "status": "active"}}
        if method == "thread/items/list":
            user = {"id": "item-is-not-queue-id", "type": "userMessage", "content": [{"type": "text", "text": PAYLOAD}]}
            entries = [{"turnId": TURN, "item": user}]
            if "multiple-steer" in self.modes:
                entries.append({"turnId": TURN, "item": {"id": "second-user", "type": "userMessage", "content": [{"type": "text", "text": "other"}]}})
            if "wrong-turn" in self.modes:
                entries[0]["turnId"] = GOAL
            result = {"data": entries, "nextCursor": None}
            if "paginated-items" in self.modes:
                result["nextCursor"] = "more"
            if "invalid-receipt" in self.modes:
                user["content"][0]["text"] = "different"
            return result
        raise AssertionError(method)


class WatchCodexTests(unittest.TestCase):
    def endpoint(self):
        temp = tempfile.TemporaryDirectory()
        path = Path(temp.name) / "socket"
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(str(path))
        os.chmod(temp.name, 0o700)
        return temp, path, listener

    def fake_rpc(self, modes=()):
        fake = FakeSocket(modes)
        temp, path, listener = self.endpoint()
        rpc = wc._WebSocketRpc(path, socket_factory=lambda *_args: fake)
        self.addCleanup(rpc.close)
        self.addCleanup(listener.close)
        self.addCleanup(temp.cleanup)
        return rpc, fake

    def test_transport_handles_partial_reads_fragmentation_ping_and_initialize(self):
        rpc, fake = self.fake_rpc({"fragmented", "ping"})
        result = rpc.request("thread/read", {"threadId": THREAD, "includeTurns": False})
        self.assertEqual(result["thread"]["id"], THREAD)
        self.assertEqual([x["method"] for x in fake.requests], ["initialize", "thread/read"])
        self.assertIn(10, fake.client_opcodes)  # pong frame was emitted

    def test_exact_accept_mismatch_closes_socket(self):
        fake = FakeSocket({"bad-accept"})
        temp, path, listener = self.endpoint()
        self.addCleanup(listener.close)
        self.addCleanup(temp.cleanup)
        with self.assertRaises(wc.AdapterError):
            wc._WebSocketRpc(path, socket_factory=lambda *_args: fake)
        self.assertTrue(fake.closed)

    def test_rpc_allowlist_and_unknown_schema_fail_closed(self):
        rpc, _fake = self.fake_rpc()
        with self.assertRaises(wc.AdapterError):
            rpc.request("thread/start", {})
        rpc2, _fake2 = self.fake_rpc({"unknown-result"})
        with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc2):
            with self.assertRaises(wc.AdapterError):
                wc.inspect_thread(THREAD)

    def test_inspection_maps_thread_latest_turn_and_goal(self):
        rpc, fake = self.fake_rpc()
        with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc):
            result = wc.inspect_thread(THREAD)
        self.assertEqual(result, {
            "thread_id": THREAD, "cwd": "/tmp/work", "status": "idle",
            "latest_turn_id": TURN, "latest_turn_status": "completed",
            "goal_active": True, "archived": False,
        })
        self.assertEqual([x["method"] for x in fake.requests], [
            "initialize", "thread/read", "thread/turns/list", "thread/goal/get",
        ])
        self.assertEqual(fake.requests[1]["params"], {"threadId": THREAD, "includeTurns": False})
        self.assertEqual(fake.requests[2]["params"], {
            "threadId": THREAD, "limit": 1, "sortDirection": "desc", "itemsView": "notLoaded",
        })

    def test_inspection_rejects_unknown_status_and_missing_thread(self):
        rpc, _fake = self.fake_rpc()
        rpc.request = mock.Mock(side_effect=[{"thread": {
            "id": THREAD, "cwd": "/tmp", "path": "/root/.codex/sessions/test.jsonl",
            "status": {"type": "future"},
        }}])
        with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc):
            with self.assertRaises(wc.AdapterError):
                wc.inspect_thread(THREAD)
        with self.assertRaises(wc.AdapterError):
            wc.inspect_thread("missing")

    def test_inspection_uses_archived_rollout_path(self):
        rpc, _fake = self.fake_rpc({"archived-path"})
        with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc):
            self.assertTrue(wc.inspect_thread(THREAD)["archived"])
        rpc2, _fake2 = self.fake_rpc()
        rpc2.request = mock.Mock(return_value={"thread": {
            "id": THREAD, "cwd": "/tmp", "path": None, "status": {"type": "notLoaded"},
        }})
        with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc2):
            with self.assertRaises(wc.AdapterError):
                wc.inspect_thread(THREAD)

    def test_inspection_requires_explicit_goal_field_but_accepts_null(self):
        thread = {"thread": {
            "id": THREAD, "cwd": "/tmp", "path": "/root/.codex/sessions/test.jsonl",
            "status": {"type": "idle"},
        }}
        turns = {"data": []}
        for goal_result in ({}, {"goal": "unknown"}):
            rpc, _fake = self.fake_rpc()
            rpc.request = mock.Mock(side_effect=[thread, turns, goal_result])
            with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc):
                with self.assertRaises(wc.AdapterError):
                    wc.inspect_thread(THREAD)
        rpc, _fake = self.fake_rpc()
        rpc.request = mock.Mock(side_effect=[thread, turns, {"goal": None}])
        with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc):
            result = wc.inspect_thread(THREAD)
        self.assertFalse(result["goal_active"])

    def test_confirm_delivery_requires_one_exact_complete_user_message(self):
        rpc, fake = self.fake_rpc()
        with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc):
            self.assertTrue(wc.confirm_delivery(THREAD, TURN, PAYLOAD))
        self.assertEqual([r["method"] for r in fake.requests], ["initialize", "thread/items/list"])
        request = fake.requests[1]
        self.assertEqual(request["params"], {"threadId": THREAD, "turnId": TURN, "limit": 20})
        for mode in ({"invalid-receipt"}, {"multiple-steer"}, {"wrong-turn"}, {"paginated-items"}):
            rpc, _fake = self.fake_rpc(mode)
            with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc):
                self.assertFalse(wc.confirm_delivery(THREAD, TURN, PAYLOAD), mode)

    def test_confirm_delivery_rejects_unknown_or_malformed_item_pages(self):
        rpc, _fake = self.fake_rpc()
        rpc.request = mock.Mock(return_value={"data": [], "nextCursor": "more"})
        with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc):
            self.assertFalse(wc.confirm_delivery(THREAD, TURN, PAYLOAD))
        rpc, _fake = self.fake_rpc()
        rpc.request = mock.Mock(return_value={"data": [{"turnId": TURN, "item": {"type": "future"}}], "nextCursor": None})
        with mock.patch.object(wc, "_WebSocketRpc", return_value=rpc):
            self.assertFalse(wc.confirm_delivery(THREAD, TURN, PAYLOAD))

    def delivery(self, ack, rc=0, timeout=False):
        temp, endpoint, listener = self.endpoint()
        self.addCleanup(listener.close)
        self.addCleanup(temp.cleanup)
        out_r, out_w = os.pipe()
        err_r, err_w = os.pipe()
        if not timeout:
            os.write(out_w, ack.encode())
        os.close(out_w)
        os.close(err_w)
        stdout = os.fdopen(out_r, "rb", buffering=0)
        stderr = os.fdopen(err_r, "rb", buffering=0)
        self.addCleanup(stdout.close)
        self.addCleanup(stderr.close)
        class Proc:
            pid = 99999999
            def __init__(self):
                self.stdout, self.stderr = stdout, stderr
            def poll(self):
                return None if timeout else rc
            def wait(self, timeout=None):
                return rc
        proc = Proc()
        args_seen = []
        def popen(args, **kwargs):
            args_seen.append((args, kwargs))
            return proc
        payload = json.dumps({"kind": "technical_data", "value": "synthetic"})
        with mock.patch.object(wc, "SOCKET_LINK", endpoint), mock.patch.object(wc.shutil, "which", return_value="/usr/bin/codex"), mock.patch.object(wc.subprocess, "Popen", side_effect=popen), mock.patch.object(wc, "QUEUE_TIMEOUT", 0.01 if timeout else 20):
            if timeout:
                with mock.patch.object(wc.selectors.DefaultSelector, "select", return_value=[]):
                    with self.assertRaises(wc.DeliveryUnknown):
                        wc.deliver(THREAD, payload)
            else:
                result = None
                error = None
                try:
                    result = wc.deliver(THREAD, payload)
                except wc.DeliveryUnknown as exc:
                    error = exc
        return result if not timeout else None, error if not timeout else None, args_seen

    def test_delivery_exact_ack_and_fixed_args_without_model_override(self):
        result, error, calls = self.delivery(f"Queued message {QUEUE} for thread {THREAD}.\n")
        self.assertIsNone(error)
        self.assertEqual(result, {"queue_id": QUEUE})
        args, kwargs = calls[0]
        self.assertEqual(args[:6], ["/usr/bin/codex", "queue", "--remote", args[3], "--thread", THREAD])
        self.assertTrue(args[3].startswith("unix://"))
        self.assertNotIn("-m", args)
        self.assertNotIn("--model", args)
        self.assertNotIn("--effort", args)
        self.assertTrue(kwargs["start_new_session"])

    def test_delivery_rejects_nonzero_timeout_malformed_and_other_thread(self):
        good = f"Queued message {QUEUE} for thread {THREAD}."
        result, error, _ = self.delivery(good, rc=1)
        self.assertIsNone(result)
        self.assertIsInstance(error, wc.DeliveryUnknown)
        result, error, _ = self.delivery("not an acknowledgement")
        self.assertIsNone(result)
        self.assertIsInstance(error, wc.DeliveryUnknown)
        other = "019a0000-0000-7000-8000-000000000099"
        result, error, _ = self.delivery(f"Queued message {QUEUE} for thread {other}.")
        self.assertIsNone(result)
        self.assertIsInstance(error, wc.DeliveryUnknown)
        self.delivery(good, timeout=True)

    def test_delivery_validates_payload_before_subprocess(self):
        with mock.patch.object(wc.shutil, "which", return_value="/usr/bin/codex"), mock.patch.object(wc.subprocess, "Popen") as popen:
            with self.assertRaises(wc.AdapterError):
                wc.deliver(THREAD, '{"kind":"evidence_command","cmd":"run"}')
            with self.assertRaises(wc.AdapterError):
                wc.deliver(THREAD, "x" * 3073)
            popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
