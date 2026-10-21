"""Isolated watcher tests; adapters and time are synthetic, with no services."""
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
import uuid

MODULE = Path(__file__).with_name("build_watch.py")
spec = importlib.util.spec_from_file_location("build_watch", MODULE)
watch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watch)


NOW = dt.datetime(2026, 10, 21, 12, 0, tzinfo=dt.timezone.utc)


def stamp(seconds):
    return (NOW + dt.timedelta(seconds=seconds)).isoformat(timespec="seconds").replace("+00:00", "Z")


class Bindings:
    def __init__(self, status=None, poll_error=False):
        self.status = status or {"terminal": False, "status": "WORKING", "accounted": False}
        self.poll_error = poll_error
        self.validated = 0
        self.poll_calls = 0

    def capture(self, spec):
        return {"schema": "smallsort-watch-binding-v1", "owner": "merge", "task_id": "merge-task",
                "phase": "W2", "worktree": spec["worktree"], "branch": "topic",
                "ledger_path": str(Path(spec["worktree"]) / spec["ledger_path"]),
                "thread_id": spec["thread_id"],
                "build_id": spec["build_id"], "dispatch_token": "dispatch-opaque", "lane": "proof-lane",
                "infra_sha": "a" * 40, "proof_sha": "b" * 40, "config_sha256": "c" * 64,
                "assignment_sha256": "d" * 64, "checkpoint_sha256": "e" * 64,
                "ledger_authority_sha256": "f" * 64, "client_sha256": "1" * 64,
                "coordination_sha256": "2" * 64, "t0": stamp(-3600),
                "main_deadline_utc": stamp(600), "deadline_utc": stamp(1200), "budget_seconds": 7200}

    def validate(self, binding):
        self.validated += 1
        return {"terminal": False, "status": "WORKING", "accounted": False}

    def poll(self, binding, client_state_dir):
        self.poll_calls += 1
        if self.poll_error:
            raise OSError("synthetic status error")
        return self.status


class Codex:
    def __init__(self):
        self.thread = {"thread_id": "thread-1", "cwd": "/work", "status": "idle",
                       "latest_turn_id": "turn-1", "latest_turn_status": "completed",
                       "goal_active": False, "archived": False}
        self.deliveries = []
        self.raise_delivery = False
        self.confirm_result = True
        self.confirm_payloads = []

    def inspect_thread(self, thread_id):
        return dict(self.thread)

    def deliver(self, thread_id, payload_text):
        if self.raise_delivery:
            raise OSError("enqueue outcome unknown")
        self.deliveries.append((thread_id, json.loads(payload_text)))
        return {"queue_id": "queue-1"}

    def confirm_delivery(self, thread_id, latest_turn_id, payload_text):
        self.confirm_payloads.append((thread_id, latest_turn_id, payload_text))
        return (self.confirm_result and thread_id == self.thread["thread_id"]
                and latest_turn_id == self.thread["latest_turn_id"]
                and self.thread.get("user_message") == payload_text
                and not self.thread.get("steers"))


class WatchTests(unittest.TestCase):
    def setUp(self):
        self.old_thread_env = os.environ.pop("CODEX_THREAD_ID", None)
        self.addCleanup(self._restore_thread_env)
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = watch.Store(self.root / "store")
        self.bindings = Bindings()
        self.codex = Codex()
        (self.root / "work").mkdir()
        self.codex.thread["cwd"] = str(self.root / "work")
        self.spec_path = self.root / "spec.json"
        self.spec_path.write_text(json.dumps({"schema": "smallsort-watch-spec-v1", "worktree": str(self.root / "work"),
            "ledger_path": "research/challenge-8/cloud-build/ledger.json", "thread_id": "thread-1", "build_id": "build-1"}))
        self.job = watch.arm(self.spec_path, self.store, bindings=self.bindings, codex=self.codex, now=NOW)

    def _restore_thread_env(self):
        if self.old_thread_env is not None:
            os.environ["CODEX_THREAD_ID"] = self.old_thread_env

    def tearDown(self):
        self.temp.cleanup()

    def tick(self, seconds=0):
        return watch.tick(self.store, self.job["job_id"], bindings=self.bindings, codex=self.codex,
                          now_fn=lambda: NOW + dt.timedelta(seconds=seconds))

    def resume_with_exact_event(self, job_id):
        job = self.store.read_job(job_id)
        self.codex.thread.update({"latest_turn_id": "turn-2", "latest_turn_status": "completed",
                                  "status": "idle", "user_message": job.get("payload_text"), "steers": []})

    def test_restart_persists_monitoring_and_delivers_once_after_accounting(self):
        self.assertEqual(self.tick()["state"], "MONITORING")
        reopened = watch.Store(self.store.root)
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": False}
        self.assertEqual(watch.tick(reopened, self.job["job_id"], bindings=self.bindings, codex=self.codex,
                                    now_fn=lambda: NOW)["state"], "MONITORING")
        self.assertEqual(self.codex.deliveries, [])
        self.bindings.status["accounted"] = True
        result = watch.tick(reopened, self.job["job_id"], bindings=self.bindings, codex=self.codex, now_fn=lambda: NOW)
        self.assertEqual(result["state"], "DELIVERED")
        self.assertEqual(len(self.codex.deliveries), 1)
        self.assertEqual(self.codex.deliveries[0][1]["kind"], "technical_data")
        self.assertEqual(self.codex.deliveries[0][1]["event_name"], "build_terminal")
        self.assertEqual(watch.tick(reopened, self.job["job_id"], bindings=self.bindings, codex=self.codex,
                                    now_fn=lambda: NOW)["state"], "DELIVERED")
        self.assertEqual(len(self.codex.deliveries), 1)
        self.resume_with_exact_event(self.job["job_id"])
        ack = watch.ack(reopened, self.job["job_id"], result["event_id"], bindings=self.bindings,
                        codex=self.codex, now=NOW)
        self.assertEqual(ack["state"], "ACKED")
        self.assertEqual(self.codex.confirm_payloads[0][2], reopened.read_job(self.job["job_id"])["payload_text"])

    def test_ambiguous_delivery_is_never_retried(self):
        self.bindings.status = {"terminal": True, "status": "FAILURE", "accounted": True}
        self.codex.raise_delivery = True
        result = self.tick()
        self.assertEqual(result["state"], "DELIVERY_UNKNOWN")
        event_id = result["event_id"]
        self.codex.raise_delivery = False
        self.assertEqual(self.tick()["state"], "DELIVERY_UNKNOWN")
        self.assertEqual(len(self.codex.deliveries), 0)
        self.resume_with_exact_event(result["job_id"])
        self.assertEqual(watch.ack(self.store, result["job_id"], event_id, bindings=self.bindings,
                                   codex=self.codex, now=NOW)["state"], "ACKED")

    def test_unknown_delivery_blocks_rearm_until_stopped(self):
        self.bindings.status = {"terminal": True, "status": "FAILURE", "accounted": True}
        self.codex.raise_delivery = True
        self.tick()
        with self.assertRaises(watch.WatchError):
            watch.arm(self.spec_path, self.store, bindings=self.bindings, codex=self.codex, now=NOW)
        watch.stop(self.store, self.job["job_id"])
        resumed = watch.arm(self.spec_path, self.store, bindings=self.bindings, codex=self.codex, now=NOW)
        self.assertEqual(resumed["state"], "ARMED")

    def test_crash_after_delivering_state_has_no_automatic_resend(self):
        job = self.store.read_job(self.job["job_id"])
        job["state"] = "DELIVERING"
        job["event_id"] = str(uuid.uuid4())
        job["attempts"] = 1
        self.store.save_job(job)
        # A restarted runner does not interpret an in-flight enqueue as safe to retry.
        result = watch.tick(self.store, job["job_id"], bindings=self.bindings, codex=self.codex, now_fn=lambda: NOW)
        self.assertEqual(result["state"], "DELIVERY_UNKNOWN")
        self.assertEqual(self.codex.deliveries, [])

    def test_start_can_recover_delivering_job_without_resending(self):
        job = self.store.read_job(self.job["job_id"])
        job["state"] = "DELIVERING"
        job["event_id"] = str(uuid.uuid4())
        job["attempts"] = 1
        job["payload_text"] = '{"kind":"technical_data"}'
        self.store.save_job(job)
        class Proc:
            pid = 991
            def poll(self): return None
            def terminate(self): pass
        def launch(command, **kwargs):
            nonce = command[command.index("--nonce") + 1]
            current = self.store.read_job(self.job["job_id"])
            current["runner_nonce"] = nonce
            current["heartbeat_utc"] = stamp(0)
            self.store.save_job(current)
            return Proc()
        watch.start(self.store, job["job_id"], popen=launch, now_fn=lambda: NOW)
        nonce = self.store.read_job(job["job_id"])["launch_nonce"]
        result = watch.run_loop(self.store, job["job_id"], nonce=nonce, bindings=self.bindings,
                                codex=self.codex, now_fn=lambda: NOW, sleep=lambda _n: None, max_cycles=2)
        self.assertEqual(result["state"], "DELIVERY_UNKNOWN")
        self.assertEqual(self.codex.deliveries, [])

    def test_binding_stale_and_thread_changes_stop_without_notification(self):
        class Stale(Bindings):
            BindingError = watch.WatchError
            def validate(self, binding):
                raise watch.WatchError("wrong owner/phase/ledger")
        result = watch.tick(self.store, self.job["job_id"], bindings=Stale(), codex=self.codex, now_fn=lambda: NOW)
        self.assertEqual(result["state"], "STALE")
        self.assertEqual(self.codex.deliveries, [])

    def test_new_turn_or_active_goal_blocks_unsolicited_wakeup(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        self.codex.thread["latest_turn_id"] = "turn-2"
        self.assertEqual(self.tick()["state"], "STALE")
        self.assertEqual(self.codex.deliveries, [])

    def test_same_turn_active_waits_then_can_resume(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        self.codex.thread["status"] = "active"
        self.codex.thread["latest_turn_status"] = "inProgress"
        self.assertEqual(self.tick()["state"], "READY")
        polls = self.bindings.poll_calls
        self.assertEqual(self.codex.deliveries, [])
        self.codex.thread["status"] = "unloaded"
        self.codex.thread["latest_turn_status"] = "completed"
        self.assertEqual(self.tick()["state"], "DELIVERED")
        self.assertEqual(self.bindings.poll_calls, polls)

    def test_active_goal_and_duplicate_arm_are_rejected(self):
        with self.assertRaises(watch.WatchError):
            watch.arm(self.spec_path, self.store, bindings=self.bindings, codex=self.codex, now=NOW)
        self.codex.thread["goal_active"] = True
        with self.assertRaises(watch.WatchError):
            watch.arm(self.spec_path, watch.Store(self.root / "bad-goal"), bindings=self.bindings,
                      codex=self.codex, now=NOW)

    def test_codex_thread_environment_must_match_on_acknowledgement(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        delivered = self.tick()
        os.environ["CODEX_THREAD_ID"] = "another-thread"
        self.resume_with_exact_event(self.job["job_id"])
        with self.assertRaises(watch.WatchError):
            watch.ack(self.store, self.job["job_id"], delivered["event_id"], bindings=self.bindings,
                      codex=self.codex, now=NOW)

    def test_ack_rejects_invalid_receipt_and_steered_user_message(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        delivered = self.tick()
        self.resume_with_exact_event(self.job["job_id"])
        self.codex.confirm_result = False
        with self.assertRaises(watch.WatchError):
            watch.ack(self.store, self.job["job_id"], delivered["event_id"], bindings=self.bindings,
                      codex=self.codex, now=NOW)
        self.codex.confirm_result = True
        self.codex.thread["steers"] = ["extra user message"]
        with self.assertRaises(watch.WatchError):
            watch.ack(self.store, self.job["job_id"], delivered["event_id"], bindings=self.bindings,
                      codex=self.codex, now=NOW)

    def test_ack_reinspection_rejects_turn_race(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        delivered = self.tick()
        self.resume_with_exact_event(self.job["job_id"])
        original_confirm = self.codex.confirm_delivery
        def racing_confirm(thread_id, turn_id, payload):
            result = original_confirm(thread_id, turn_id, payload)
            self.codex.thread["latest_turn_id"] = "turn-3"
            return result
        self.codex.confirm_delivery = racing_confirm
        with self.assertRaises(watch.WatchError):
            watch.ack(self.store, self.job["job_id"], delivered["event_id"], bindings=self.bindings,
                      codex=self.codex, now=NOW)

    def test_stop_after_queue_blocks_acknowledgement(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        delivered = self.tick()
        self.resume_with_exact_event(self.job["job_id"])
        watch.stop(self.store, self.job["job_id"])
        with self.assertRaises(watch.WatchError):
            watch.ack(self.store, self.job["job_id"], delivered["event_id"], bindings=self.bindings,
                      codex=self.codex, now=NOW)

    def test_stop_during_confirmation_is_durable_and_blocks_ack_without_deadlock(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        delivered = self.tick()
        self.resume_with_exact_event(self.job["job_id"])
        original_confirm = self.codex.confirm_delivery
        def stop_then_confirm(thread_id, turn_id, payload):
            watch.stop(self.store, self.job["job_id"])
            return original_confirm(thread_id, turn_id, payload)
        self.codex.confirm_delivery = stop_then_confirm
        with self.assertRaises(watch.WatchError):
            watch.ack(self.store, self.job["job_id"], delivered["event_id"], bindings=self.bindings,
                      codex=self.codex, now=NOW)
        self.assertEqual(self.store.read_job(self.job["job_id"])["state"], "DELIVERED")
        self.assertTrue(watch.status(self.store, self.job["job_id"])["stop_requested"])

    def test_stop_after_enqueue_started_allows_delivery_but_blocks_ack(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        original_deliver = self.codex.deliver
        def stop_during_enqueue(thread_id, payload):
            watch.stop(self.store, self.job["job_id"])
            return original_deliver(thread_id, payload)
        self.codex.deliver = stop_during_enqueue
        delivered = self.tick()
        self.assertEqual(delivered["state"], "DELIVERED")
        self.assertTrue(watch.status(self.store, self.job["job_id"])["stop_requested"])
        self.resume_with_exact_event(self.job["job_id"])
        with self.assertRaises(watch.WatchError):
            watch.ack(self.store, self.job["job_id"], delivered["event_id"], bindings=self.bindings,
                      codex=self.codex, now=NOW)

    def test_deadline_crossing_during_thread_inspection_prevents_enqueue(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        ticks = iter([NOW, NOW + dt.timedelta(seconds=1185), NOW + dt.timedelta(seconds=1185),
                      NOW + dt.timedelta(seconds=1185)])
        self.codex.inspect_thread = lambda _thread: {
            "thread_id": "thread-1", "cwd": str(self.root / "work"), "status": "idle",
            "latest_turn_id": "turn-1", "latest_turn_status": "completed", "goal_active": False, "archived": False}
        result = watch.tick(self.store, self.job["job_id"], bindings=self.bindings, codex=self.codex,
                            now_fn=lambda: next(ticks))
        self.assertEqual(result["state"], "EXPIRED")
        self.assertEqual(self.codex.deliveries, [])

    def test_changed_binding_after_poll_prevents_enqueue(self):
        class Changed(Bindings):
            BindingError = watch.WatchError
            def poll(self, binding, client_state_dir):
                return {"terminal": True, "status": "SUCCESS", "accounted": True}
            def validate(self, binding):
                self.validated += 1
                if self.validated > 1:
                    raise watch.WatchError("binding changed after poll")
                return {"terminal": False, "status": "WORKING", "accounted": False}
        changed = Changed()
        result = watch.tick(self.store, self.job["job_id"], bindings=changed, codex=self.codex, now_fn=lambda: NOW)
        self.assertEqual(result["state"], "STALE")
        self.assertEqual(self.codex.deliveries, [])

    def test_terminal_unaccounted_status_still_runs_reconciliation_poll(self):
        class Reconciles(Bindings):
            def validate(self, binding):
                self.validated += 1
                return {"terminal": True, "status": "SUCCESS", "accounted": False}
            def poll(self, binding, client_state_dir):
                self.poll_calls += 1
                return {"terminal": True, "status": "SUCCESS", "accounted": True}
        recon = Reconciles()
        result = watch.tick(self.store, self.job["job_id"], bindings=recon, codex=self.codex, now_fn=lambda: NOW)
        self.assertEqual(recon.poll_calls, 1)
        self.assertEqual(result["state"], "DELIVERED")

    def test_repeated_unaccounted_terminal_reconciliation_notifies_as_monitor_error(self):
        class Unaccounted(Bindings):
            def validate(self, binding):
                self.validated += 1
                return {"terminal": True, "status": "SUCCESS", "accounted": False}
            def poll(self, binding, client_state_dir):
                self.poll_calls += 1
                return {"terminal": True, "status": "SUCCESS", "accounted": False}
        stalled = Unaccounted()
        for _ in range(3):
            result = watch.tick(self.store, self.job["job_id"], bindings=stalled, codex=self.codex,
                                now_fn=lambda: NOW)
        self.assertEqual(result["state"], "DELIVERED")
        self.assertEqual(self.codex.deliveries[0][1]["event_name"], "monitor_error")

    def test_predelivery_cwd_must_match_frozen_worktree(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        self.codex.thread["cwd"] = "/different-worktree"
        result = self.tick()
        self.assertEqual(result["state"], "STALE")
        self.assertEqual(self.codex.deliveries, [])

    def test_stopped_pending_delivery_cannot_rearm_or_queue(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        self.codex.thread["status"] = "active"
        self.codex.thread["latest_turn_status"] = "inProgress"
        self.assertEqual(self.tick()["state"], "READY")
        watch.stop(self.store, self.job["job_id"])
        self.codex.thread["status"] = "unloaded"
        self.codex.thread["latest_turn_status"] = "completed"
        self.assertEqual(self.tick()["state"], "STOPPED")
        self.assertEqual(self.codex.deliveries, [])

    def test_deadline_and_main_window_modes(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        result = self.tick(700)
        self.assertEqual(result["state"], "DELIVERED")
        self.assertEqual(self.codex.deliveries[0][1]["mode"], "CLOSEOUT_ONLY")
        second = watch.Store(self.root / "other")
        late_binding = self.bindings.capture(json.loads(self.spec_path.read_text()))
        late_binding["main_deadline_utc"] = stamp(-600)
        late_binding["deadline_utc"] = stamp(600)
        self.bindings.capture = lambda _spec: late_binding
        late_job = watch.arm(self.spec_path, second, bindings=self.bindings, codex=self.codex, now=NOW)
        result = watch.tick(second, late_job["job_id"], bindings=self.bindings, codex=self.codex, now_fn=lambda: NOW)
        self.assertEqual(result["state"], "DELIVERED")
        self.assertEqual(self.codex.deliveries[-1][1]["mode"], "CLOSEOUT_ONLY")

    def test_no_enqueue_after_absolute_deadline(self):
        self.bindings.status = {"terminal": True, "status": "SUCCESS", "accounted": True}
        self.assertEqual(self.tick(1201)["state"], "EXPIRED")
        self.assertEqual(self.codex.deliveries, [])

    def test_stop_and_ack_validate_thread_context_and_window(self):
        self.assertTrue(watch.stop(self.store, self.job["job_id"])["state"] == "ARMED")
        self.assertEqual(self.tick()["state"], "STOPPED")
        with self.assertRaises(watch.WatchError):
            watch.ack(self.store, self.job["job_id"], str(uuid.uuid4()), bindings=self.bindings,
                      codex=self.codex, now=NOW)

    def test_store_rejects_symlink_and_tampered_state(self):
        link = self.store.root / "evil.json"
        link.symlink_to(self.spec_path)
        with self.assertRaises(watch.WatchError):
            self.store.list_jobs()
        link.unlink()
        state_path = self.store.root / (self.job["job_id"] + ".json")
        data = json.loads(state_path.read_text())
        data["state"] = "DELIVERED"
        state_path.write_text(json.dumps(data))
        with self.assertRaises(watch.WatchError):
            self.store.read_job(self.job["job_id"])

    def test_start_observes_runner_heartbeat_and_refuses_runner_lease_race(self):
        class Proc:
            pid = 987
            def poll(self): return None
            def terminate(self): pass
        def launch(command, **kwargs):
            self.assertIn("run", command)
            nonce = command[command.index("--nonce") + 1]
            job = self.store.read_job(self.job["job_id"])
            job["heartbeat_utc"] = stamp(0)
            job["runner_nonce"] = nonce
            self.store.save_job(job)
            return Proc()
        old = self.store.read_job(self.job["job_id"])
        old["heartbeat_utc"] = stamp(-100)
        old["runner_nonce"] = "stale-runner"
        self.store.save_job(old)
        result = watch.start(self.store, self.job["job_id"], popen=launch, now_fn=lambda: NOW)
        self.assertEqual(result["pid"], 987)
        with self.store.lock(self.job["job_id"] + ".runner.lock"):
            with self.assertRaises(watch.WatchError):
                watch.start(self.store, self.job["job_id"], popen=launch, now_fn=lambda: NOW)
            with self.assertRaises(watch.WatchError):
                watch.run_loop(self.store, self.job["job_id"], bindings=self.bindings, codex=self.codex,
                               now_fn=lambda: NOW, sleep=lambda _n: None, max_cycles=0)

    def test_thread_cwd_and_active_goal_rejected_at_arm(self):
        self.codex.thread["cwd"] = "/elsewhere"
        with self.assertRaises(watch.WatchError):
            watch.arm(self.spec_path, watch.Store(self.root / "bad"), bindings=self.bindings, codex=self.codex, now=NOW)

    def test_failed_polls_alert_after_three_attempts(self):
        self.bindings.poll_error = True
        for _ in range(2):
            self.tick()
        result = self.tick()
        self.assertEqual(result["state"], "DELIVERED")
        self.assertEqual(self.codex.deliveries[0][1]["status"], "watch status unavailable after three failures")


if __name__ == "__main__":
    unittest.main()
