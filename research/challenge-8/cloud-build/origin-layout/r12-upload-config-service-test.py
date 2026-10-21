#!/usr/bin/env python3
"""Exercise the generated R12 package-upload shell with a fake local gcloud."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

CONTROL = Path(__file__).resolve().parents[1] / "control.py"
sys.path.insert(0, str(CONTROL.parent))
import control  # noqa: E402

INFRA = "1" * 40
PROOF = "2" * 40
BUILD_ID = "service-build-r12"


def fail(message):
    raise AssertionError(message)


def make_fake_gcloud(bin_dir):
    executable = bin_dir / "gcloud"
    executable.write_text("""#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ['FAKE_GCLOUD_LOG'], 'a') as stream:
    stream.write(json.dumps({'argv': args, 'composite': os.environ.get('CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED'), 'external': os.environ.get('EXTERNAL_COMPOSITE')}) + '\\n')
if args[-3:] == ['config', 'get-value', 'storage/parallel_composite_upload_threshold']:
    if os.environ.get('FAKE_FAIL_STAGE') == 'config-query': sys.exit(23)
    print('150M'); sys.exit(0)
if args[-3:] == ['config', 'get-value', 'storage/parallel_composite_upload_enabled']:
    print(os.environ.get('FAKE_EFFECTIVE_COMPOSITE', os.environ['CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED'])); sys.exit(0)
source = next((x for x in args if x.startswith('/tmp/r12-upload-') or x.startswith(os.environ['TEST_WORKSPACE'])), '')
if '--recursive' in args:
    stage = 'chunks'
elif source.endswith('evidence.tar.gz'):
    stage = 'archive'
elif source.endswith('upload-complete.json'):
    stage = 'marker'
else:
    stage = pathlib.Path(source).name
if os.environ.get('FAKE_FAIL_STAGE') == stage:
    print('controlled fake failure: ' + stage, file=sys.stderr)
    sys.exit(17)
sys.exit(0)
""")
    executable.chmod(0o755)


def calls(log):
    return [json.loads(line) for line in log.read_text().splitlines()]


def run_case(shell_template, package_b64, failure=None, external="True", effective=None):
    with tempfile.TemporaryDirectory(prefix="r12-upload-") as td:
        root = Path(td)
        workspace = root / "workspace"
        evidence = workspace / "evidence"
        out = workspace / "out"
        evidence.mkdir(parents=True)
        (evidence / "run-exit.txt").write_text("0\n")
        (evidence / "full-stdout.log").write_text("tiny synthetic run\n")
        (evidence / "full-stderr.log").write_text("")
        (evidence / "environment.txt").write_text("tiny synthetic environment\n")
        config_bytes = json.dumps(control.config(INFRA, PROOF, "merge", 600, "r12-service"), sort_keys=True).encode() + b"\n"
        (evidence / "submitted-config.json").write_bytes(config_bytes)
        (evidence / "allprooflogs").mkdir()
        # This is a local packaging exercise; the evidence intentionally makes no proof claim.
        bin_dir = root / "bin"
        bin_dir.mkdir()
        make_fake_gcloud(bin_dir)
        log = root / "gcloud.jsonl"
        shell = shell_template.replace("/workspace", str(workspace)).replace("SDK_PYTHON", sys.executable).replace("$$", "$")
        env = dict(os.environ)
        env.update({
            "PATH": str(bin_dir) + os.pathsep + env.get("PATH", ""),
            "FAKE_GCLOUD_LOG": str(log), "TEST_WORKSPACE": str(workspace),
            "FAKE_FAIL_STAGE": failure or "", "EXTERNAL_COMPOSITE": external,
            "CLOUD_BUILD_ID": BUILD_ID, "PROJECT_ID": "smallsort-ci",
            "INFRA_SHA": INFRA, "PROOF_SHA": PROOF, "LANE": "merge",
            "PROOF_IMAGE": control.UBUNTU, "SUBMITTED_CONFIG_SHA": hashlib.sha256(config_bytes).hexdigest(),
            "CLOUD_BUILD_PROJECT_ID": "smallsort-ci", "CLOUD_BUILD_REGION": "global",
            "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
            "PACKAGER_BYTES": package_b64,
            "CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED": external,
        })
        if effective is not None:
            env["FAKE_EFFECTIVE_COMPOSITE"] = effective
        proc = subprocess.run(["bash", "-ceu", shell], env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        records = calls(log) if log.exists() else []
        snapshot = {
            "upload_ok": (workspace / "upload.ok").exists(),
            "marker_exists": (out / "upload-complete.json").is_file(),
            "marker_uploaded": any("upload-complete.json" in x for row in records for x in row["argv"]),
        }
        if snapshot["marker_exists"]:
            snapshot["receipt"] = json.loads((out / "upload-complete.json").read_text())
        policy = evidence / "allprooflogs/upload-policy.json"
        if policy.is_file():
            snapshot["policy"] = json.loads(policy.read_text())
        return proc, records, snapshot


def main():
    cfg = control.config(INFRA, PROOF, "merge", 600, "r12-service")
    upload = cfg["steps"][1]["args"][1]
    package = cfg["steps"][1]["env"][-1].split("=", 1)[1]
    assert upload.startswith("set -euo pipefail\nexport CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False\n"), "export must be first package-upload action"
    assert "storage/parallel_composite_upload_threshold" in upload and "storage/parallel_composite_upload_enabled" in upload
    assert cfg["steps"][1]["name"] == control.SDK
    assert cfg["serviceAccount"].endswith(control.ACCOUNT)

    success, records, snapshot = run_case(upload, package, external="True")
    assert success.returncode == 0, (success.returncode, success.stderr)
    assert snapshot["upload_ok"]
    assert records and all(row["composite"] == "False" for row in records), "every gcloud call must see export despite hostile parent env"
    args = [row["argv"] for row in records]
    assert args[0][-3:] == ["config", "get-value", "storage/parallel_composite_upload_threshold"]
    assert args[1][-3:] == ["config", "get-value", "storage/parallel_composite_upload_enabled"]
    uploads = args[2:]
    expected = ["evidence.tar.gz", "archive.sha256", "summary.json", "manifest.json", "files-sha256.json", "submitted-config.json", "text-logs-index.json"]
    names = [Path(next(x for x in row if x.startswith("/tmp/r12-upload-") and x != "--recursive")).name for row in uploads[:7]]
    assert names == expected, names
    assert all("--if-generation-match=0" in row for row in uploads)
    assert all(row[:3] == ["--configuration=smallsort-ci", "--account=" + control.ACCOUNT, "--project=smallsort-ci"] for row in args)
    assert all(row[-1].startswith(control.BUCKET + "/" + BUILD_ID) for row in uploads)
    recursive = next(i for i, row in enumerate(uploads) if "--recursive" in row)
    marker = next(i for i, row in enumerate(uploads) if any("upload-complete.json" in x for x in row))
    assert recursive == 7 and marker == 8 and marker == len(uploads) - 1, (recursive, marker, uploads)
    archive_index = next(i for i, row in enumerate(records) if any(x.endswith("evidence.tar.gz") for x in row["argv"]))
    assert all(row["composite"] == "False" for row in records[:archive_index + 1])
    receipt = snapshot["receipt"]
    assert receipt["uploaded"] is True and receipt["parallel_composite_upload_enabled"] == "False"
    assert receipt["archive_size_bytes"] > 0 and len(receipt["archive_sha256"]) == 64
    assert all(c in "0123456789abcdef" for c in receipt["archive_sha256"])
    assert receipt["archive_upload_seconds"] >= 0 and receipt["pre_marker_upload_seconds"] >= 0
    assert receipt["archive_upload_bytes_per_second"] is None or receipt["archive_upload_bytes_per_second"] >= 0
    policy = snapshot["policy"]
    assert policy["parallel_composite_upload_enabled_env"] == "False"
    assert policy["parallel_composite_upload_enabled_effective"] == "False"
    assert policy["parallel_composite_upload_threshold"] == "150M"

    cases = {"config-query": 23, "archive": 17, "chunks": 17, "marker": 17}
    for stage, expected_exit in cases.items():
        result, failed_calls, failed = run_case(upload, package, failure=stage, external="True")
        assert result.returncode == expected_exit, (stage, result.returncode, result.stderr)
        assert not failed["upload_ok"], stage
        assert failed_calls and all(row["composite"] == "False" for row in failed_calls), stage
        if stage in ("config-query", "archive", "chunks"):
            assert not failed["marker_exists"], stage
            assert not failed["marker_uploaded"], stage
        elif stage == "marker":
            assert failed["marker_exists"]
            assert any("upload-complete.json" in x for x in failed_calls[-1]["argv"])
    mismatch, mismatch_calls, mismatch_state = run_case(upload, package, external="True", effective="True")
    assert mismatch.returncode != 0, "unexpected effective composite policy must fail closed"
    assert len(mismatch_calls) == 2 and all("config" in row["argv"] for row in mismatch_calls)
    assert all("storage" not in row["argv"] or "cp" not in row["argv"] for row in mismatch_calls)
    assert not mismatch_state["upload_ok"] and not mismatch_state["marker_exists"] and not mismatch_state["marker_uploaded"]
    print(json.dumps({"classification": "PASS_SYNTHETIC_PACKAGE_UPLOAD_SERVICE", "success_calls": len(records),
                      "failure_cases": {k: "preserved exit " + str(v) for k, v in cases.items()},
                      "wrong_effective_policy": "failed closed before uploads",
                      "proof_attempted": False, "proof_credit": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
