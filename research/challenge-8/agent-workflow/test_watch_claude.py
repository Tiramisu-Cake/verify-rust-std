"""Isolated Claude foreground watcher tests; bindings, /proc, session and time are synthetic."""
import contextlib
import datetime as dt
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_watch as bw  # noqa: E402
import watch_claude as wc  # noqa: E402

NOW = dt.datetime(2026, 10, 21, 12, 0, tzinfo=dt.timezone.utc)
SESSION = "11111111-2222-4333-8444-555555555555"
SELF, SHELL, CLAUDE = 300, 200, 100


def stamp(seconds):
    return (NOW + dt.timedelta(seconds=seconds)).isoformat(timespec="seconds").replace("+00:00", "Z")


class Bindings:
    BindingError = type("BindingError", (ValueError,), {})

    def __init__(self):
        self.statuses = [{"terminal": True, "status": "FAILURE", "accounted": True}]
        self.poll_calls = 0
        self.stale = False

    def capture(self, spec):
        return {"schema": "smallsort-watch-binding-v1", "owner": "select-sort4", "task_id": "select-task",
                "phase": "R17", "worktree": spec["worktree"], "branch": "topic",
                "ledger_path": str(Path(spec["worktree"]) / spec["ledger_path"]),
                "thread_id": spec["thread_id"], "build_id": spec["build_id"],
                "dispatch_token": "dispatch-opaque", "lane": "proof-lane", "infra_sha": "a" * 40,
                "proof_sha": "b" * 40, "config_sha256": "c" * 64, "assignment_sha256": "d" * 64,
                "checkpoint_sha256": "e" * 64, "ledger_authority_sha256": "f" * 64,
                "client_sha256": "1" * 64, "coordination_sha256": "2" * 64, "t0": stamp(-3600),
                "main_deadline_utc": stamp(600), "deadline_utc": stamp(1200), "budget_seconds": 3600}

    def validate(self, binding):
        if self.stale:
            raise self.BindingError("checkpoint changed")
        return {"terminal": False, "status": "WORKING", "accounted": False}

    def poll(self, binding, client_state_dir, *, timeout_seconds=55):
        self.poll_calls += 1
        status = self.statuses[min(self.poll_calls, len(self.statuses)) - 1]
        if isinstance(status, Exception):
            raise status
        return status


class BrokenStream(io.StringIO):
    def write(self, text):
        raise BrokenPipeError("session output closed")


class ClaudeWaitTests(unittest.TestCase):
    def setUp(self):
        old_thread = os.environ.pop("CODEX_THREAD_ID", None)
        if old_thread is not None:
            self.addCleanup(os.environ.__setitem__, "CODEX_THREAD_ID", old_thread)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.work = self.root / "work"
        self.work.mkdir()
        self.proc = self.root / "proc"
        for pid, parent, comm in ((SELF, SHELL, "python3"), (SHELL, CLAUDE, "bash"), (CLAUDE, 1, "claude")):
            (self.proc / str(pid)).mkdir(parents=True)
            (self.proc / str(pid) / "stat").write_text(f"{pid} ({comm} x) S {parent} 0 0\n")
            (self.proc / str(pid) / "comm").write_text(comm + "\n")
        (self.proc / str(CLAUDE) / "cwd").symlink_to(self.work)
        # Main-session shells also carry CLAUDE_CODE_CHILD_SESSION=1; it must not cause a refusal.
        self.env = {"CLAUDE_CODE_SESSION_ID": SESSION, "CLAUDE_PID": str(CLAUDE), "CLAUDE_CODE_CHILD_SESSION": "1"}
        self.out = io.StringIO()
        self.adapter = wc.Adapter(self.env, self.proc, pid=SELF, stdout=self.out)
        self.bindings = Bindings()
        self.store = bw.Store(self.root / "store")
        self.spec = self.root / "spec.json"
        self.spec.write_text(json.dumps({"schema": "smallsort-watch-spec-v1", "worktree": str(self.work),
            "ledger_path": "research/challenge-8/cloud-build/ledger.json", "thread_id": SESSION,
            "build_id": "27e8bfac-eb5f-4cf4-ae89-18bacd16eb90", "poll_seconds": 15}))
        self.sleeps = []

    def arm(self):
        return wc.arm(self.store, self.spec, bindings=self.bindings, adapter=self.adapter, now=NOW)

    def wait(self, job=None, seconds=0, max_cycles=5):
        job = job or self.arm()
        return wc.wait(self.store, job["job_id"], bindings=self.bindings, adapter=self.adapter,
                       now_fn=lambda: NOW + dt.timedelta(seconds=seconds), sleep=self.sleeps.append,
                       max_cycles=max_cycles)

    def run_cli(self, seconds=0, max_cycles=5, **kw):
        out = io.StringIO()
        self.adapter.stdout = out
        code = wc.run(self.store, bindings=self.bindings, adapter=self.adapter, out=out,
                      now_fn=lambda: NOW + dt.timedelta(seconds=seconds), sleep=self.sleeps.append,
                      max_cycles=max_cycles, **kw)
        return code, [json.loads(line) for line in out.getvalue().splitlines()]

    def ack(self, job, seconds=0, event=None):
        return wc.ack(self.store, job["job_id"], event or job["event_id"], bindings=self.bindings,
                      adapter=self.adapter, now=NOW + dt.timedelta(seconds=seconds))

    def events(self):
        return [json.loads(line) for line in self.out.getvalue().splitlines()]

    def test_terminal_accounted_build_is_printed_before_delivered(self):
        job = self.wait()
        self.assertEqual((job["state"], job["delivery"], job["attempts"]), ("DELIVERED", wc.DELIVERY, 1))
        [line] = self.events()
        self.assertEqual(line["event"]["event_id"], job["event_id"])
        self.assertEqual((line["event"]["event_name"], line["event"]["status"], line["event"]["mode"]),
                         ("build_terminal", "FAILURE", "CONTINUE_EXISTING_WINDOW"))
        self.assertIn("wait ack --job", line["next"])

    def test_cli_exit_codes_and_json_lines(self):
        code, lines = self.run_cli(spec=self.spec)
        self.assertEqual(code, 0)
        self.assertEqual([sorted(line) for line in lines], [["armed_job"], ["event", "next"], ["job"]])
        self.assertEqual(lines[2]["job"]["state"], "DELIVERED")
        self.setUp()
        with self.assertRaisesRegex(bw.WatchError, "deadline has already passed"):
            self.run_cli(spec=self.spec, seconds=1300)
        code, lines = self.run_cli(job_id=self.arm()["job_id"], seconds=1300)
        self.assertEqual((code, lines[-1]["job"]["state"]), (wc.EXIT_NOT_DELIVERED, "EXPIRED"))
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wc.main(["run", "--job", "not-a-job", "--store", str(self.root / "store")]), 2)
        self.assertIn("wait:", err.getvalue())
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            wc.main(["run", "--spec", "a", "--job", "b"])

    def test_failed_print_is_delivery_unknown_and_not_ackable(self):
        self.adapter.stdout = BrokenStream()
        job = self.wait()
        self.assertEqual(job["state"], "DELIVERY_UNKNOWN")
        with self.assertRaisesRegex(bw.WatchError, "acknowledgeable"):
            self.ack(job)

    def test_running_build_is_polled_without_delivery_until_terminal(self):
        self.bindings.statuses = [{"terminal": False, "status": "WORKING", "accounted": False}] * 2 + [
            {"terminal": True, "status": "SUCCESS", "accounted": True}]
        self.assertEqual(self.wait()["state"], "DELIVERED")
        self.assertEqual((self.bindings.poll_calls, sum(self.sleeps)), (3, 30))

    def test_unaccounted_terminal_and_status_errors_end_as_monitor_error(self):
        for statuses in ([{"terminal": True, "status": "FAILURE", "accounted": False}],
                         [OSError("status unavailable")], [{"terminal": True}]):
            with self.subTest(statuses=statuses):
                self.setUp()
                self.bindings.statuses = statuses
                job = self.wait()
                self.assertEqual(json.loads(job["payload_text"])["event_name"], "monitor_error")
                self.assertEqual(self.bindings.poll_calls, 3)

    def test_after_main_deadline_event_is_closeout_only(self):
        job = self.wait(seconds=700)
        self.assertEqual(json.loads(job["payload_text"])["mode"], "CLOSEOUT_ONLY")
        self.assertEqual(self.ack(job, seconds=700)["ack_mode"], "CLOSEOUT_ONLY")

    def test_absolute_deadline_and_stale_binding_end_without_delivery(self):
        expired = self.wait(seconds=1300, max_cycles=2)
        self.assertEqual((expired["state"], expired["event_id"]), ("EXPIRED", None))
        self.setUp()
        self.bindings.stale = True
        self.bindings.statuses = [{"terminal": False, "status": "WORKING", "accounted": False}]
        self.assertEqual(self.wait(max_cycles=2)["state"], "STALE")
        self.assertEqual((self.bindings.poll_calls, self.out.getvalue()), (0, ""))

    def test_stop_ends_wait_without_delivery(self):
        job = self.arm()
        bw.stop(self.store, job["job_id"])
        self.assertEqual(self.wait(job)["state"], "STOPPED")
        self.assertEqual((self.bindings.poll_calls, self.out.getvalue()), (0, ""))

    def test_resume_replays_delivered_event_and_refuses_foreign_jobs(self):
        delivered = self.wait()
        code, lines = self.run_cli(job_id=delivered["job_id"])
        self.assertEqual(code, 0)
        self.assertEqual((lines[0]["replay"], lines[0]["event"]["event_id"]), (True, delivered["event_id"]))
        self.assertEqual(self.store.read_job(delivered["job_id"])["attempts"], 1)
        self.ack(delivered)
        code, lines = self.run_cli(job_id=delivered["job_id"])
        self.assertEqual((code, [sorted(line) for line in lines]), (wc.EXIT_NOT_DELIVERED, [["job"]]))
        self.setUp()
        codex_job = bw.arm(self.spec, self.store, bindings=self.bindings, codex=self.adapter, now=NOW)
        with self.assertRaisesRegex(bw.WatchError, "not armed for Claude"):
            self.wait(codex_job)
        with self.assertRaisesRegex(bw.WatchError, "delivery mode"):
            bw.run_loop(self.store, codex_job["job_id"], bindings=self.bindings, codex=self.adapter,
                        now_fn=lambda: NOW, sleep=self.sleeps.append, max_cycles=1, delivery=wc.DELIVERY)

    def test_codex_runner_start_and_ack_refuse_claude_jobs(self):
        self.bindings.statuses = [{"terminal": False, "status": "WORKING", "accounted": False}]
        job = self.arm()
        with self.assertRaisesRegex(bw.WatchError, "delivery mode"):
            bw.start(self.store, job["job_id"], popen=lambda *a, **k: self.fail("runner launched"))
        with self.assertRaisesRegex(bw.WatchError, "delivery mode"):
            bw.run_loop(self.store, job["job_id"], bindings=self.bindings, codex=self.adapter,
                        now_fn=lambda: NOW, sleep=self.sleeps.append, max_cycles=1)
        self.bindings.statuses = [{"terminal": True, "status": "SUCCESS", "accounted": True}]
        delivered = self.wait(job)
        self.assertEqual(delivered["state"], "DELIVERED")
        with self.assertRaisesRegex(bw.WatchError, "delivery mode"):
            bw.ack(self.store, delivered["job_id"], delivered["event_id"], bindings=self.bindings,
                   codex=self.adapter, now=NOW)

    def test_session_identity_and_process_tree_are_required(self):
        def env(key, value):
            def change():
                if value is None:
                    self.env.pop(key)
                else:
                    self.env[key] = value
            return change

        def unrelated_pid():
            (self.proc / str(SHELL) / "stat").write_text(f"{SHELL} (bash) S 1 0 0\n")

        def not_claude():
            (self.proc / str(CLAUDE) / "comm").write_text("bash\n")

        def cwd_not_link():
            (self.proc / str(CLAUDE) / "cwd").unlink()
            (self.proc / str(CLAUDE) / "cwd").mkdir()

        def other_cwd():
            (self.proc / str(CLAUDE) / "cwd").unlink()
            (self.proc / str(CLAUDE) / "cwd").symlink_to(self.root)

        cases = [(env("CLAUDE_CODE_SESSION_ID", "other"), "target session"),
                 (env("CLAUDE_CODE_SESSION_ID", None), "target session"),
                 (env("CLAUDE_PID", None), "CLAUDE_PID is missing"),
                 (env("CLAUDE_PID", str(SHELL)), "not a Claude Code process"),
                 (unrelated_pid, "not an ancestor"), (not_claude, "not a Claude Code process"),
                 (cwd_not_link, "cwd is unavailable"), (other_cwd, "cwd does not match")]
        for change, message in cases:
            with self.subTest(case=message):
                self.setUp()
                change()
                with self.assertRaisesRegex(bw.WatchError, message):
                    self.arm()

    def test_session_change_during_monitoring_does_not_deliver(self):
        self.bindings.statuses = [{"terminal": False, "status": "WORKING", "accounted": False},
                                  {"terminal": True, "status": "SUCCESS", "accounted": True}]
        job = self.wait(max_cycles=1)
        self.env["CLAUDE_CODE_SESSION_ID"] = "other"
        with self.assertRaisesRegex(bw.WatchError, "target session"):
            self.wait(job)
        self.env["CLAUDE_CODE_SESSION_ID"] = SESSION
        (self.proc / str(CLAUDE) / "cwd").unlink()
        (self.proc / str(CLAUDE) / "cwd").symlink_to(self.root)
        with self.assertRaisesRegex(bw.WatchError, "cwd does not match"):
            self.wait(job)
        self.assertEqual((self.store.read_job(job["job_id"])["state"], self.out.getvalue()), ("MONITORING", ""))

    def test_duplicate_runner_and_second_job_are_refused(self):
        self.bindings.statuses = [{"terminal": False, "status": "WORKING", "accounted": False}]
        job = self.arm()
        with self.store.lock(job["job_id"] + ".runner.lock"):
            with self.assertRaisesRegex(bw.WatchError, "already running"):
                self.wait(job)
        with self.assertRaisesRegex(bw.WatchError, "active watcher already exists"):
            self.arm()

    def test_ack_accepts_exact_event_once(self):
        job = self.wait()
        result = self.ack(job)
        self.assertEqual((result["state"], result["ack_mode"]), ("ACKED", "CONTINUE_EXISTING_WINDOW"))
        with self.assertRaisesRegex(bw.WatchError, "acknowledgeable"):
            self.ack(job)

    def test_ack_refusals(self):
        def wrong_event(job):
            return self.ack(job, event="00000000-0000-0000-0000-000000000000")

        def runner_alive(job):
            with self.store.lock(job["job_id"] + ".runner.lock"):
                return self.ack(job)

        def other_session(job):
            self.env["CLAUDE_CODE_SESSION_ID"] = "other"
            return self.ack(job)

        def moved_cwd(job):
            (self.proc / str(CLAUDE) / "cwd").unlink()
            (self.proc / str(CLAUDE) / "cwd").symlink_to(self.root)
            return self.ack(job)

        def stopped(job):
            bw.stop(self.store, job["job_id"])
            return self.ack(job)

        def stale(job):
            self.bindings.stale = True
            return self.ack(job)

        def expired(job):
            return self.ack(job, seconds=1300)

        cases = [(wrong_event, "acknowledgeable"), (runner_alive, "already running"),
                 (other_session, "target session"), (moved_cwd, "cwd does not match"),
                 (stopped, "stopped"), (stale, "checkpoint changed"), (expired, "expired")]
        for action, message in cases:
            with self.subTest(action=action.__name__):
                self.setUp()
                job = self.wait()
                with self.assertRaisesRegex(Exception, message):
                    action(job)
                self.assertEqual(self.store.read_job(job["job_id"])["state"], "DELIVERED")
        self.setUp()
        self.bindings.statuses = [{"terminal": False, "status": "WORKING", "accounted": False}]
        job = self.wait(max_cycles=1)
        with self.assertRaisesRegex(bw.WatchError, "acknowledgeable"):
            self.ack(job, event="00000000-0000-0000-0000-000000000000")
        with self.assertRaisesRegex(bw.WatchError, "invalid event"):
            self.ack(job, event="not-a-uuid")

    def test_stop_after_delivery_exits_not_delivered_without_replay(self):
        job = self.wait()
        bw.stop(self.store, job["job_id"])
        code, lines = self.run_cli(job_id=job["job_id"])
        self.assertEqual((code, [sorted(line) for line in lines]), (wc.EXIT_NOT_DELIVERED, [["job"]]))
        self.assertTrue(lines[0]["job"]["stop_requested"])


if __name__ == "__main__":
    unittest.main()
