"""Real watcher/adapters, temporary Git/account, fake Codex RPC/queue executable.

No network service, existing Codex thread, GCP or model is contacted.
"""
import datetime as dt
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

import build_watch as watch
import watch_bindings as bindings
import watch_codex as codex
from test_watch_bindings import BindingFixture, BUILD, THREAD


NOW = dt.datetime(2026, 10, 21, 10, 0, tzinfo=dt.timezone.utc)
ARM_TURN = "12345678-1234-4234-8234-123456789aaa"
WAKE_TURN = "12345678-1234-4234-8234-123456789bbb"
QUEUE = "12345678-1234-4234-8234-123456789ccc"


class WatchIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.f = BindingFixture(self.base)
        for mock in self.f.patches():
            mock.start()
            self.addCleanup(mock.stop)
        mock = patch.dict(os.environ, CODEX_THREAD_ID=THREAD)
        mock.start()
        self.addCleanup(mock.stop)
        self.store = watch.Store(self.base / "store")
        self.spec = self.base / "spec.json"
        self.f.write(self.spec, dict(self.f.spec, schema="smallsort-watch-spec-v1"))
        self.turn = ARM_TURN
        self.turn_status = "inProgress"
        self.runtime = "active"
        self.payload = None
        self.calls = []
        fixture = self

        class FakeRPC:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def request(self, method, params):
                fixture.calls.append((method, params))
                if method == "thread/read":
                    return {"thread": {"id": THREAD, "cwd": str(fixture.f.root),
                                       "path": str(Path.home() / ".codex/sessions/synthetic.jsonl"),
                                       "status": {"type": fixture.runtime, "activeFlags": []}}}
                if method == "thread/turns/list":
                    return {"data": [{"id": fixture.turn, "status": fixture.turn_status}]}
                if method == "thread/goal/get":
                    return {"goal": None}
                if method == "thread/items/list":
                    return {"nextCursor": None, "data": [{"turnId": fixture.turn,
                            "item": {"id": "synthetic-message", "type": "userMessage", "content": [
                                {"type": "text", "text": fixture.payload, "text_elements": []}]}}]}
                raise AssertionError("unexpected RPC: " + method)
        mock = patch.object(codex, "_WebSocketRpc", FakeRPC)
        mock.start()
        self.addCleanup(mock.stop)

        # The actual queue subprocess gets a fake executable and unused private
        # Unix endpoint. No daemon or Codex binary is involved.
        self.sock = socket.socket(socket.AF_UNIX)
        self.addCleanup(self.sock.close)
        endpoint_dir = self.base / "private"
        endpoint_dir.mkdir(mode=0o700)
        self.endpoint = endpoint_dir / "control.sock"
        self.sock.bind(str(self.endpoint))
        self.queue_file = self.base / "queued.json"
        self.fake_cli = self.base / "fake-codex"
        self.fake_cli.write_text("#!/usr/bin/env python3\nimport json,sys\nfrom pathlib import Path\n"
                                 + "Path(" + repr(str(self.queue_file)) + ").write_text(json.dumps(sys.argv[1:]))\n"
                                 + "print('Queued message " + QUEUE + " for thread " + THREAD + ".')\n")
        self.fake_cli.chmod(0o700)
        for mock in (patch.object(codex, "SOCKET_LINK", self.endpoint),
                     patch.object(codex.shutil, "which", return_value=str(self.fake_cli))):
            mock.start()
            self.addCleanup(mock.stop)

    def arm(self):
        return watch.arm(self.spec, self.store, bindings=bindings, codex=codex, now=NOW)

    def tick(self, job):
        return watch.tick(self.store, job["job_id"], bindings=bindings, codex=codex, now_fn=lambda: NOW)

    def test_real_adapter_contract_terminal_wake_and_ack(self):
        # The status process is tiny synthetic code, committed before arm. It
        # models the existing client's ordinary own-account reconciliation.
        client = self.f.root / bindings.CLIENT
        client.write_text("import json,sys\nfrom pathlib import Path\n"
                          "p=Path(sys.argv[sys.argv.index('--ledger')+1])\n"
                          "d=json.loads(p.read_text())\n"
                          "d['builds'][0].update(status='SUCCESS',accounted=True)\n"
                          "d.update(active_build=None,used_build_seconds=123,remaining_build_seconds=3477)\n"
                          "p.write_text(json.dumps(d))\n"
                          + "print(json.dumps({'id':" + repr(BUILD) + ",'status':'SUCCESS'}))\n")
        self.f.git("add", bindings.CLIENT)
        self.f.git("commit", "-qm", "synthetic status accounting")
        checkpoint_before = (self.f.root / bindings.CHECKPOINT).read_bytes()
        job = self.arm()
        self.assertEqual(self.tick(job)["state"], "READY")
        self.assertFalse(self.queue_file.exists())
        self.runtime, self.turn_status = "idle", "completed"
        delivered = self.tick(job)
        self.assertEqual(delivered["state"], "DELIVERED")
        argv = json.loads(self.queue_file.read_text())
        self.assertEqual(argv[:3], ["queue", "--remote", "unix://" + str(self.endpoint)])
        self.assertEqual(argv[3:5], ["--thread", THREAD])
        self.payload = argv[6]
        self.assertEqual(self.payload, self.store.read_job(job["job_id"])["payload_text"])
        payload = json.loads(self.payload)
        self.assertEqual(payload["kind"], "technical_data")
        self.assertEqual(payload["proof_credit"], 0)
        self.assertEqual(payload["build_id"], BUILD)
        self.turn, self.turn_status, self.runtime = WAKE_TURN, "inProgress", "active"
        ack = watch.ack(self.store, job["job_id"], delivered["event_id"], bindings=bindings, codex=codex, now=NOW)
        self.assertEqual(ack["state"], "ACKED")
        self.assertEqual(ack["ack_mode"], "CONTINUE_EXISTING_WINDOW")
        self.assertEqual(checkpoint_before, (self.f.root / bindings.CHECKPOINT).read_bytes())
        self.assertEqual({call[0] for call in self.calls}, {"thread/read", "thread/turns/list", "thread/goal/get", "thread/items/list"})

    def test_changed_real_handoff_prevents_delivery(self):
        job = self.arm()
        self.f.terminal()
        checkpoint_path = self.f.root / bindings.CHECKPOINT
        checkpoint_path.write_bytes(checkpoint_path.read_bytes() + b"\n")
        self.runtime, self.turn_status = "idle", "completed"
        self.assertEqual(self.tick(job)["state"], "STALE")
        self.assertFalse(self.queue_file.exists())


if __name__ == "__main__":
    unittest.main()
