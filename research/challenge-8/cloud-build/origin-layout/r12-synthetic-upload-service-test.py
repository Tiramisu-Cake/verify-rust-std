#!/usr/bin/env python3
"""Isolated R12 synthetic-mode and payload-generator tests; no Cloud or proof tools."""
from __future__ import annotations

import hashlib
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUN_MERGE = ROOT / "cloud-build" / "run-merge.sh"
GENERATOR_PATH = HERE / "r12-synthetic-upload.py"
spec = importlib.util.spec_from_file_location("r12_synthetic_upload_test", GENERATOR_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("R12 synthetic upload generator unavailable")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)
package_spec = importlib.util.spec_from_file_location("r12_package_evidence_test", ROOT / "cloud-build" / "package-evidence.py")
if package_spec is None or package_spec.loader is None:
    raise RuntimeError("Cloud evidence packager unavailable")
package = importlib.util.module_from_spec(package_spec)
package_spec.loader.exec_module(package)


def mode_card(path: Path, mode="synthetic-upload"):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"schema": generator.MODE_SCHEMA, "mode": mode}
    if mode == "synthetic-upload":
        data.update({"payload_bytes": generator.SYNTHETIC_PAYLOAD_BYTES,
                     "threshold_bytes": generator.COMPOSITE_THRESHOLD_BYTES,
                     "threshold_source": generator.THRESHOLD_SOURCE,
                     "proof_attempted": False})
    path.write_text(json.dumps(data) + "\n")
    return path


def source_certificate(evidence: Path, infra_sha="1" * 40, proof_sha="2" * 40):
    evidence.mkdir(parents=True, exist_ok=True)
    source_bytes = b"synthetic pinned source-input archive for package-service test\n"
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    (evidence / "source-input.gz").write_bytes(source_bytes)
    (evidence / "source-input-certificate.json").write_text(json.dumps({
        "lane": "merge", "archive_sha256": source_sha,
        "proof": {"commit": proof_sha, "head": proof_sha},
        "infra": {"commit": infra_sha, "head": infra_sha},
    }))
    return {"LANE": "merge", "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
            "SOURCE_MODE": "pinned-objects", "CLOUD_BUILD_ID": "build-r12-synthetic-test",
            "INFRA_SHA": infra_sha, "PROOF_SHA": proof_sha, "SOURCE_INPUT_SHA256": source_sha}


class R12SyntheticUploadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_mode_card_is_explicit_and_fails_closed(self):
        card = mode_card(self.root / "mode.json")
        self.assertEqual(generator.read_mode_card(card)[0], "synthetic-upload")
        card = mode_card(self.root / "proof.json", "proof-r11")
        self.assertEqual(generator.read_mode_card(card)[0], "proof-r11")
        for content in (
            "{bad json", json.dumps({"schema": generator.MODE_SCHEMA, "mode": "unknown"}),
            json.dumps({"schema": generator.MODE_SCHEMA, "mode": "synthetic-upload", "extra": 1}),
            json.dumps({"schema": "wrong", "mode": "proof-r11"}),
        ):
            path = self.root / "invalid.json"
            path.write_text(content)
            with self.subTest(content=content), self.assertRaises(ValueError):
                generator.read_mode_card(path)
        symlink = self.root / "linked.json"
        symlink.symlink_to(card)
        with self.assertRaises(ValueError):
            generator.read_mode_card(symlink)

    def test_random_payload_helper_streams_exact_bytes_and_refuses_reuse(self):
        path = self.root / "payload.bin"
        size, digest = generator.write_random_payload(path, 8193, chunk_bytes=1024,
                                                       random_bytes=lambda count: bytes([count % 251]) * count)
        expected = b"".join(bytes([min(1024, remaining) % 251]) * min(1024, remaining)
                            for remaining in (8193, 7169, 6145, 5121, 4097, 3073, 2049, 1025, 1))
        self.assertEqual(size, 8193)
        self.assertEqual(path.stat().st_size, 8193)
        self.assertEqual(path.read_bytes(), expected)
        self.assertEqual(digest, hashlib.sha256(expected).hexdigest())
        with self.assertRaises(FileExistsError):
            generator.write_random_payload(path, 1)

    def test_internal_small_generation_records_identity_without_proof_credit(self):
        evidence = self.root / "evidence"
        env = source_certificate(evidence)
        card = mode_card(self.root / "mode.json")
        fixed_times = iter(("2026-10-21T10:00:00Z", "2026-10-21T10:00:01Z"))
        record = generator._generate_synthetic(evidence, card, env, payload_size_bytes=4096,
                                                random_bytes=lambda n: os.urandom(n),
                                                clock=lambda: next(fixed_times))
        case = evidence / "allprooflogs/cases/synthetic-upload"
        payload = case / "payload.bin"
        manifest = json.loads((case / "manifest.json").read_text())
        audit = json.loads((evidence / "allprooflogs/proof-audit.json").read_text())
        self.assertEqual(record, manifest)
        self.assertEqual(manifest["status"], "COMPLETE")
        self.assertEqual(manifest["payload"]["size_bytes"], 4096)
        self.assertEqual(manifest["payload"]["sha256"], hashlib.sha256(payload.read_bytes()).hexdigest())
        self.assertEqual(manifest["build_id"], env["CLOUD_BUILD_ID"])
        self.assertEqual(manifest["source"]["proof_sha"], env["PROOF_SHA"])
        self.assertEqual(manifest["mode"], "synthetic-upload")
        self.assertEqual(manifest["mode_card"]["payload_bytes"], 512 * 1024 * 1024)
        self.assertEqual(manifest["upload_size_contract"]["threshold_bytes"], 150 * 1024 * 1024)
        self.assertEqual(manifest["started_at_utc"], "2026-10-21T10:00:00Z")
        self.assertEqual(manifest["completed_at_utc"], "2026-10-21T10:00:01Z")
        self.assertTrue(audit["diagnostic_complete"])
        self.assertFalse(audit["proof_attempted"])
        self.assertFalse(audit["accepted"])
        self.assertEqual(audit["independent_credit"], 0)
        self.assertEqual((evidence / "allprooflogs/r12-synthetic-upload-exit-code.txt").read_text(), "0\n")

    def test_generation_failure_keeps_diagnostic_incomplete(self):
        evidence = self.root / "evidence"
        env = source_certificate(evidence)
        card = mode_card(self.root / "mode.json")
        with patch.object(generator, "write_random_payload", side_effect=OSError("synthetic injected failure")):
            with self.assertRaises(OSError):
                generator._generate_synthetic(evidence, card, env, payload_size_bytes=16,
                                               clock=lambda: "2026-10-21T10:00:00Z")
        audit = json.loads((evidence / "allprooflogs/proof-audit.json").read_text())
        self.assertFalse(audit["diagnostic_complete"])
        self.assertFalse(audit["accepted"])
        self.assertFalse(audit["proof_attempted"])
        self.assertEqual(audit["classification"], "SYNTHETIC_UPLOAD_GENERATION_FAILED")
        self.assertEqual((evidence / "allprooflogs/r12-synthetic-upload-exit-code.txt").read_text(), "1\n")
        self.assertFalse((evidence / "allprooflogs/cases/synthetic-upload/manifest.json").exists())

    def test_packager_reports_diagnostic_completion_without_proof_acceptance(self):
        evidence = self.root / "evidence"
        env = source_certificate(evidence)
        card = mode_card(self.root / "mode.json")
        generator._generate_synthetic(evidence, card, env, payload_size_bytes=4096)
        config = {"steps": [{"id": "execute", "env": [
            "LANE=merge", f"INFRA_SHA={env['INFRA_SHA']}", f"PROOF_SHA={env['PROOF_SHA']}",
            "SOURCE_MODE=pinned-objects", f"SOURCE_INPUT_SHA256={env['SOURCE_INPUT_SHA256']}"]}]}
        config_bytes = (json.dumps(config, sort_keys=True) + "\n").encode()
        (evidence / "submitted-config.json").write_bytes(config_bytes)
        (evidence / "environment.txt").write_text("synthetic package test environment\n")
        (evidence / "full-stdout.log").write_text("synthetic generator completed\n")
        (evidence / "full-stderr.log").write_text("")
        (evidence / "run-exit.txt").write_text("0\n")
        out = self.root / "out"
        package_env = {
            "CLOUD_BUILD_ID": env["CLOUD_BUILD_ID"], "INFRA_SHA": env["INFRA_SHA"],
            "PROOF_SHA": env["PROOF_SHA"], "LANE": "merge",
            "SUBMITTED_CONFIG_SHA": hashlib.sha256(config_bytes).hexdigest(),
        }
        with patch.dict(os.environ, package_env), patch.object(
                sys, "argv", [str(ROOT / "cloud-build/package-evidence.py"),
                              "--evidence", str(evidence), "--out", str(out)]):
            self.assertEqual(package.main(), 0)
        summary = json.loads((out / "summary.json").read_text())
        self.assertTrue(summary["evidence_complete"])
        self.assertTrue(summary["diagnostic_complete"])
        self.assertFalse(summary["verification_accepted"])
        self.assertEqual(summary["run_exit_code"], 0)

    def test_cli_keeps_fixed_512_mib_runtime_floor(self):
        self.assertEqual(generator.MIN_PAYLOAD_BYTES, 512 * 1024 * 1024)
        self.assertEqual(generator.SYNTHETIC_PAYLOAD_BYTES, 512 * 1024 * 1024)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                generator.main(["generate", str(self.root / "missing-card.json"),
                                str(self.root / "evidence"), "--size-bytes", "16"])

    def test_run_merge_dispatches_only_explicit_card_and_ignores_environment_mode(self):
        workspace = Path("/workspace")
        created_workspace = not workspace.exists()
        workspace.mkdir(parents=True, exist_ok=True)
        temp = tempfile.TemporaryDirectory(prefix="r12-dispatch-", dir=workspace)
        root = Path(temp.name)
        try:
            proof = root / "proof"
            evidence = root / "evidence"
            card = proof / "research/challenge-8/cloud-build/origin-layout/R12-UPLOAD-MODE-20261021.json"
            generator_path = card.parent / "r12-synthetic-upload.py"
            normal = proof / "research/challenge-8/merge/cloud-build/merge.sh"
            generator_path.parent.mkdir(parents=True, exist_ok=True)
            normal.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(GENERATOR_PATH, generator_path)
            marker = root / "normal-called"
            normal.write_text("#!/usr/bin/env bash\nprintf normal > \"$R12_MARKER\"\n")
            normal.chmod(0o755)
            synthetic_marker = root / "synthetic-called"
            python_wrapper_dir = root / "bin"
            python_wrapper_dir.mkdir()
            wrapper = python_wrapper_dir / "python3"
            real_python = Path(sys.executable)
            wrapper.write_text(f'''#!/usr/bin/env bash
if [[ "${{1:-}}" == "{generator_path}" && "${{2:-}}" == generate ]]; then
  printf synthetic > "$R12_SYNTHETIC_MARKER"
  exit 0
fi
exec "{real_python}" "$@"
''')
            wrapper.chmod(0o755)
            env = os.environ.copy()
            env.update({"PROOF_ROOT": str(proof), "EVIDENCE_ROOT": str(evidence),
                        "R12_MARKER": str(marker), "R12_SYNTHETIC_MARKER": str(synthetic_marker),
                        "PATH": str(python_wrapper_dir) + os.pathsep + env.get("PATH", ""),
                        "SMALLSORT_R12_MODE": "synthetic-upload"})

            def run():
                return subprocess.run(["bash", str(RUN_MERGE), "merge"], env=env,
                                      text=True, capture_output=True, check=False)

            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(marker.is_file(), "absent card must preserve normal legacy route")
            self.assertFalse(synthetic_marker.exists(), "environment alone must not select synthetic mode")
            marker.unlink()

            mode_card(card, "proof-r11")
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(marker.is_file())
            self.assertFalse(synthetic_marker.exists())
            marker.unlink()

            mode_card(card, "synthetic-upload")
            result = run()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(synthetic_marker.is_file())
            self.assertFalse(marker.exists(), "synthetic mode must not invoke normal proof merge")
            synthetic_marker.unlink()

            card.write_text('{invalid')
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())
            self.assertFalse(synthetic_marker.exists())

            card.unlink()
            card.symlink_to(root / "dangling-target")
            result = run()
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())
            self.assertFalse(synthetic_marker.exists())
        finally:
            temp.cleanup()
            if created_workspace:
                try:
                    workspace.rmdir()
                except OSError:
                    pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
