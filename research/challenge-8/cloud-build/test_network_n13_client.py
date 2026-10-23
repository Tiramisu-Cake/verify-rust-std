"""Synthetic client checks for the bounded Network N13 Cloud phase."""
import datetime
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock


CLOUD_BUILD = Path(__file__).resolve().parent
sys.path.insert(0, str(CLOUD_BUILD))
import control


CANDIDATE = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=CLOUD_BUILD).decode().strip()
PHASE = control.NETWORK_N4_PHASE


class NetworkN13ClientTests(unittest.TestCase):
    def setUp(self):
        class FrozenDatetime(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return cls(2026, 10, 23, 7, 54, tzinfo=datetime.timezone.utc)
        self.clock = mock.patch.object(control.datetime, "datetime", FrozenDatetime)
        self.clock.start()
        self.addCleanup(self.clock.stop)

    def test_main_envelope_refuses_a_build_that_only_fits_absolute(self):
        record = dict(control.NETWORK_PHASES[PHASE])
        record["main_deadline_utc"] = "2026-10-23T08:10:00Z"
        with mock.patch.dict(control.NETWORK_PHASES, {PHASE: record}):
            with self.assertRaisesRegex(SystemExit, "queue reserve exceeds main"):
                control.network_submit_gate(self.args(timeout=975))

    def args(self, *, stage="exact", timeout=975, infra_sha=CANDIDATE):
        values = {"phase_id": PHASE, "timeout": timeout, "infra_sha": infra_sha}
        if stage is not None:
            values["stage"] = stage
        return SimpleNamespace(**values)

    def test_registered_stage_and_exact_build_timeouts_are_required(self):
        expected = {
            "preflight": 735,
            "exact": 975,
            "controls": 1155,
            "controls-order": 975,
            "regressions": 915,
            "regressions-n13": 735,
            "regressions-n9": 555,
        }
        for stage, timeout in expected.items():
            with self.subTest(stage=stage):
                control.network_submit_gate(self.args(stage=stage, timeout=timeout))
        for bad in (
            self.args(stage=None),
            self.args(stage="unregistered"),
            self.args(timeout=794),
            self.args(stage="controls-order", timeout=794),
        ):
            with self.subTest(args=vars(bad)), self.assertRaises(SystemExit):
                control.network_submit_gate(bad)

    def test_profile_stage_limits_must_match_client_envelope(self):
        profile_path = CLOUD_BUILD / "network-n13" / "N13-EXECUTION-PROFILE-20261023-N4.json"
        profile = json.loads(profile_path.read_text())
        control.network_profile_stage_gate(profile, "controls-order", 975, 600)
        control.network_profile_stage_gate(profile, "regressions-n13", 735, 360)
        for changed in ("timeout_seconds", "build_timeout_seconds"):
            bad = json.loads(json.dumps(profile))
            bad["stages"]["controls-order"][changed] -= 1
            with self.subTest(changed=changed), self.assertRaises(SystemExit):
                control.network_profile_stage_gate(bad, "controls-order", 975, 600)
            bad = json.loads(json.dumps(profile))
            bad["stages"]["regressions-n13"][changed] -= 1
            with self.subTest(stage="regressions-n13", changed=changed), self.assertRaises(SystemExit):
                control.network_profile_stage_gate(bad, "regressions-n13", 735, 360)

    def test_selected_recipe_must_bind_network_stages(self):
        profile_path = CLOUD_BUILD / "network-n13" / "N13-EXECUTION-PROFILE-20261023-N4.json"
        old_recipe = subprocess.check_output([
            "git", "show", "010127f1a6fb125097dcbec4ef84818b8f7adb8f:research/challenge-8/cloud-build/recipes/network-n13.json"
        ])
        with mock.patch.object(
            control.subprocess, "check_output",
            side_effect=[profile_path.read_bytes(), old_recipe],
        ), self.assertRaises(SystemExit):
            control.network_submit_gate(self.args(stage="controls-order"))

    def test_profile_bytes_must_match_registration_pin(self):
        self.assertEqual(
            control.network_env(CANDIDATE, PHASE),
            ["NETWORK_PHASE_ID=" + PHASE,
             "NETWORK_PROFILE_SHA256=" + control.NETWORK_N4_PROFILE_SHA256],
        )
        with mock.patch.object(control.subprocess, "check_output", return_value=b"wrong profile"):
            with self.assertRaises(SystemExit):
                control.network_env(CANDIDATE, PHASE)

    def test_generated_config_carries_the_admitted_stage(self):
        with mock.patch.object(control, "network_env", return_value=[]):
            config = control.config(
                CANDIDATE, CANDIDATE, "network-n13", 795, "synthetic-token",
                phase_id=PHASE, stage="controls-order",
            )
        self.assertIn("NETWORK_STAGE=controls-order", config["steps"][0]["env"])
        self.assertEqual(config["timeout"], "795s")
        self.assertEqual(config["queueTtl"], "60s")

    def test_generated_network_config_has_one_bounded_bootstrap_deadline(self):
        with mock.patch.object(control, "network_env", return_value=[]):
            config = control.config(
                CANDIDATE, CANDIDATE, "network-n13", 795, "synthetic-token",
                source_payload=b"synthetic-pinned-archive", phase_id=PHASE,
                stage="exact",
            )
        work = config["steps"][0]["args"][1]
        self.assertEqual(work.count("NETWORK_SETUP_DEADLINE_EPOCH=$$(( $$(date +%s) + 120 ))"), 1)
        self.assertIn("Acquire::http::Timeout=25", work)
        self.assertIn("Acquire::https::Timeout=25", work)
        self.assertIn("Acquire::Retries=1", work)
        self.assertIn("network_setup_run pinned-source-restore", work)

    def test_generated_work_runs_restore_after_apt_as_a_separate_command(self):
        source_payload = b"synthetic-pinned-archive"
        with mock.patch.object(control, "network_env", return_value=[]):
            config = control.config(
                CANDIDATE, CANDIDATE, "network-n13", 795, "synthetic-token",
                source_payload=source_payload, phase_id=PHASE, stage="exact",
            )
        body = config["steps"][0]["args"][1]
        timeout_start = body.index("timeout --signal=TERM --kill-after=10s")
        quote_start = body.index(" bash -ceu ", timeout_start) + len(" bash -ceu ")
        quote_end = body.index(" > /workspace/evidence/full-stdout.log", quote_start)
        generated_work = shlex.split(body[quote_start:quote_end])[0].replace("$$", "$")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bindir = root / "bin"
            bindir.mkdir()
            evidence = root / "evidence"
            evidence.mkdir()
            apt_trace = root / "apt-args"
            restore_trace = root / "restore-ran"
            run_proof_trace = root / "run-proof-ran"
            (bindir / "apt-get").write_text(
                "#!/bin/sh\nprintf '%s\\n' \"$*\" >> \"$APT_TRACE\"\n"
            )
            (bindir / "timeout").write_text(
                "#!/bin/sh\n"
                "while [ \"$1\" != \"\" ]; do case \"$1\" in --*) shift;; *s) shift; break;; *) break;; esac; done\n"
                "exec \"$@\"\n"
            )
            (bindir / "python3").write_text(
                "#!/bin/sh\n"
                f"if [ \"${{1:-}}\" = \"{root}/source-input.py\" ] && [ \"${{2:-}}\" = restore ]; then echo restored > \"$RESTORE_TRACE\"; exit 0; fi\n"
                "exec /usr/bin/python3 \"$@\"\n"
            )
            (bindir / "bash").write_text(
                "#!/bin/sh\n"
                f"if [ \"${{1:-}}\" = \"{root}/infra/research/challenge-8/cloud-build/run-proof.sh\" ]; then echo invoked > \"$RUN_PROOF_TRACE\"; exit 0; fi\n"
                "exec /bin/bash \"$@\"\n"
            )
            for executable in (bindir / "apt-get", bindir / "timeout", bindir / "python3", bindir / "bash"):
                executable.chmod(0o755)

            restore_bytes, _ = control.source_restore_transport(
                (control.DIR / "source-input.py").read_bytes(), PHASE,
            )
            env = os.environ.copy()
            env.update({
                "PATH": str(bindir) + os.pathsep + env["PATH"],
                "APT_TRACE": str(apt_trace),
                "RESTORE_TRACE": str(restore_trace),
                "RUN_PROOF_TRACE": str(run_proof_trace),
                "NETWORK_STAGE": "exact",
                "NETWORK_BOOTSTRAP_RECORD": str(evidence / "network-n13-bootstrap.json"),
                "EVIDENCE_ROOT": str(evidence),
                "SOURCE_GROUP_0": config["substitutions"]["_SOURCE_0"],
                "SOURCE_RESTORE_BYTES": restore_bytes,
                "LANE": "network-n13",
            })
            script = generated_work.replace("/workspace", str(root))
            result = subprocess.run(
                ["/bin/bash", "-ceu", script], env=env, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            apt_calls = apt_trace.read_text().splitlines()
            self.assertEqual(len(apt_calls), 2)
            self.assertIn("Acquire::Retries=1", " ".join(apt_calls))
            self.assertNotIn("network_setup_run", " ".join(apt_calls))
            self.assertNotIn("pinned-source-restore", " ".join(apt_calls))
            self.assertTrue(restore_trace.is_file())
            self.assertTrue(run_proof_trace.is_file())
            bootstrap = json.loads((evidence / "network-n13-bootstrap.json").read_text())
            self.assertEqual(bootstrap["operation"], "pinned-source-restore")
            self.assertEqual(bootstrap["runner_state"], "NOT_REACHED")

    def test_bootstrap_helper_records_success_original_error_and_timeout(self):
        helper = control.network_bootstrap_script()
        for mode, expected in (("success", 0), ("error", 100), ("timeout", 124)):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                bindir = root / "bin"
                bindir.mkdir()
                trace = root / "apt-args"
                (bindir / "apt-get").write_text(
                    "#!/bin/sh\n"
                    "test -f \"$BOOT_RECORD\" || exit 97\n"
                    "grep -q '\"state\":\"RUNNING\"' \"$BOOT_RECORD\" || exit 98\n"
                    "printf '%s\\n' \"$*\" >> \"$APT_TRACE\"\n"
                    "exit \"${APT_FAKE_EXIT:-0}\"\n"
                )
                (bindir / "timeout").write_text(
                    "#!/bin/sh\n"
                    "while [ \"$1\" != \"\" ]; do case \"$1\" in --*) shift;; *s) shift; break;; *) break;; esac; done\n"
                    + ("\"$@\"; exit 124\n" if mode == "timeout" else "exec \"$@\"\n")
                )
                for executable in (bindir / "apt-get", bindir / "timeout"):
                    executable.chmod(0o755)
                record = root / "bootstrap.json"
                env = os.environ.copy()
                env.update({
                    "PATH": str(bindir) + os.pathsep + env["PATH"],
                    "APT_TRACE": str(trace),
                    "BOOT_RECORD": str(record),
                    "NETWORK_BOOTSTRAP_RECORD": str(record),
                    "NETWORK_STAGE": "exact",
                })
                if mode == "error":
                    env["APT_FAKE_EXIT"] = "100"
                result = subprocess.run(
                    ["bash", "-ceu", helper], env=env, text=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                self.assertEqual(result.returncode, expected)
                saved = json.loads(record.read_text())
                self.assertEqual(saved["state"], "SUCCEEDED" if expected == 0 else "FAILED")
                self.assertEqual(saved["exit_code"], expected)
                self.assertEqual(saved["runner_state"], "NOT_REACHED")
                if mode != "timeout":
                    self.assertIn("Acquire::http::Timeout=25", trace.read_text())
                    self.assertIn("Acquire::Retries=1", trace.read_text())

    def test_run_wrapper_rejects_missing_stage_before_setup(self):
        result = subprocess.run(
            ["bash", str(CLOUD_BUILD / "network-n13" / "run.sh")],
            env={key: value for key, value in os.environ.items() if key != "NETWORK_STAGE"},
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("NETWORK_STAGE is required", result.stderr)

    def test_network_build_reservation_keeps_setup_and_report_margins(self):
        budget = control.network_time_budget(735)
        self.assertEqual(budget, {
            "package_reserve": 240, "work_seconds": 495, "soft_margin": 15,
        })


if __name__ == "__main__":
    unittest.main()
