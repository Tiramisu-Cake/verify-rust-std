#!/usr/bin/env python3
"""Run generated R13 package-upload shell with a real packager and fake gcloud."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CONTROL = ROOT / "control.py"
LAYOUT = ROOT / "origin-layout"
sys.path.insert(0, str(ROOT))
import control  # noqa: E402

INFRA = "1" * 40
PROOF = "2" * 40
BUILD_ID = "68d2fe9c-bb4b-494e-844d-1a779d8d9f41"
LIMIT = 536_870_912
THRESHOLD = 157_286_400
SYNTHETIC_PAYLOAD = 268_435_456
THRESHOLD_SOURCE = "https://docs.cloud.google.com/storage/docs/parallel-composite-uploads"
OMIT = object()


def mode_card(mode):
    if mode == "proof-r11":
        return {"schema": "merge-r13-upload-mode-v1", "mode": "proof-r11",
                "archive_limit_bytes": LIMIT}
    return {"schema": "merge-r13-upload-mode-v1", "mode": "synthetic-upload",
            "payload_bytes": SYNTHETIC_PAYLOAD, "threshold_bytes": THRESHOLD,
            "archive_limit_bytes": LIMIT, "threshold_source": THRESHOLD_SOURCE,
            "proof_attempted": False}


def fake_gcloud(bin_dir):
    path = bin_dir / "gcloud"
    path.write_text("""#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
with open(os.environ['FAKE_GCLOUD_LOG'], 'a') as stream:
    stream.write(json.dumps({'argv': args, 'composite': os.environ.get('CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED')}) + '\\n')
if args[-3:] == ['config', 'get-value', 'storage/parallel_composite_upload_threshold']:
    if os.environ.get('FAKE_FAIL_STAGE') == 'config-query': sys.exit(23)
    value = os.environ.get('FAKE_THRESHOLD', '150M')
    if value != '__EMPTY__': print(value)
    sys.exit(0)
if args[-3:] == ['config', 'get-value', 'storage/parallel_composite_upload_enabled']:
    print(os.environ.get('FAKE_EFFECTIVE_COMPOSITE', 'False')); sys.exit(0)
source = next((x for x in args if x.startswith(os.environ['TEST_WORKSPACE'])), '')
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
    path.chmod(0o755)


def run_case(card=OMIT, threshold="150M", effective="False", failure=None, r13_required=True):
    with tempfile.TemporaryDirectory(prefix="r13-upload-") as temporary:
        root = Path(temporary)
        workspace = root / "workspace"
        evidence = workspace / "evidence"
        out = workspace / "out"
        proof = workspace / "proof/research/challenge-8/cloud-build/origin-layout"
        evidence.mkdir(parents=True)
        proof.mkdir(parents=True)
        (evidence / "run-exit.txt").write_text("0\n")
        (evidence / "full-stdout.log").write_text("tiny local packaging service run\n")
        (evidence / "full-stderr.log").write_text("")
        (evidence / "environment.txt").write_text("synthetic service environment\n")
        cfg = control.config(INFRA, PROOF, "merge", 600, "r13-service", r13_required=r13_required)
        config_bytes = json.dumps(cfg, sort_keys=True).encode() + b"\n"
        (evidence / "submitted-config.json").write_bytes(config_bytes)
        (evidence / "allprooflogs").mkdir()
        if card is not OMIT:
            card_path = proof / "R13-UPLOAD-MODE-20261021.json"
            card_path.write_text(card if isinstance(card, str) else json.dumps(card))
        shutil.copy2(LAYOUT / "r13-archive-size-guard.py", proof / "r13-archive-size-guard.py")

        bin_dir = root / "bin"
        bin_dir.mkdir()
        fake_gcloud(bin_dir)
        log = root / "gcloud.jsonl"
        shell = cfg["steps"][1]["args"][1].replace("/workspace", str(workspace)).replace(
            "SDK_PYTHON", sys.executable).replace("$$", "$")
        env = dict(os.environ)
        env.update({
            "PATH": str(bin_dir) + os.pathsep + env.get("PATH", ""),
            "FAKE_GCLOUD_LOG": str(log), "TEST_WORKSPACE": str(workspace),
            "FAKE_FAIL_STAGE": failure or "", "FAKE_THRESHOLD": threshold,
            "FAKE_EFFECTIVE_COMPOSITE": effective,
            "R13_UPLOAD_REQUIRED": "true" if r13_required else "false",
            "CLOUD_BUILD_ID": BUILD_ID, "PROJECT_ID": "smallsort-ci",
            "INFRA_SHA": INFRA, "PROOF_SHA": PROOF, "LANE": "merge",
            "PROOF_IMAGE": control.UBUNTU, "SUBMITTED_CONFIG_SHA": hashlib.sha256(config_bytes).hexdigest(),
            "CLOUD_BUILD_PROJECT_ID": "smallsort-ci", "CLOUD_BUILD_REGION": "global",
            "SMALLSORT_EXECUTION_PROVIDER": "cloud-build",
            "PACKAGER_BYTES": cfg["steps"][1]["env"][-1].split("=", 1)[1],
            "CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED": "True",
        })
        result = subprocess.run(["bash", "-ceu", shell], env=env, text=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        records = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
        archive = out / "evidence.tar.gz"
        diagnostic_path = out / "archive-size-check.json"
        marker_path = out / "upload-complete.json"
        uploaded = [Path(next((x for x in row["argv"] if x.startswith(str(workspace / "out"))), "")).name
                    for row in records if "storage" in row["argv"] and "cp" in row["argv"]]
        snapshot = {
            "archive_exists": archive.is_file(),
            "archive_bytes": archive.stat().st_size if archive.is_file() else None,
            "diagnostic_exists": diagnostic_path.is_file(),
            "diagnostic": json.loads(diagnostic_path.read_text()) if diagnostic_path.is_file() else None,
            "marker_exists": marker_path.is_file(),
            "marker": json.loads(marker_path.read_text()) if marker_path.is_file() else None,
            "upload_ok": (workspace / "upload.ok").is_file(),
            "uploaded": uploaded,
            "calls": records,
        }
        return result, snapshot


def main():
    cfg = control.config(INFRA, PROOF, "merge", 600, "r13-service", r13_required=True)
    shell = cfg["steps"][1]["args"][1]
    assert shell.startswith("set -euo pipefail\nexport CLOUDSDK_STORAGE_PARALLEL_COMPOSITE_UPLOAD_ENABLED=False\n")
    guard_call = "r13-archive-size-guard.py --archive /workspace/out/evidence.tar.gz"
    assert guard_call in shell
    assert shell.index("r13-archive-size-guard.py") < shell.index('gcloud --configuration=smallsort-ci --account=' + control.ACCOUNT + ' --project=smallsort-ci storage cp')
    assert "publication_files+=(archive-size-check.json)" in shell
    assert "archive_size_guard_sha256" in shell and "archive_size_guard':guard" in shell
    assert cfg["steps"][1]["name"] == control.SDK and cfg["serviceAccount"].endswith(control.ACCOUNT)
    assert "R13_UPLOAD_REQUIRED=true" in cfg["steps"][0]["env"]
    assert "R13_UPLOAD_REQUIRED=true" in cfg["steps"][1]["env"]

    # Ordinary proof mode allows a tiny local archive while retaining the shared upper cap.
    success, ok = run_case(card=mode_card("proof-r11"))
    assert success.returncode == 0, (success.returncode, success.stderr)
    assert ok["archive_exists"] and ok["diagnostic_exists"] and ok["diagnostic"]["accepted"] is True
    assert ok["diagnostic"]["mode"] == "proof-r11"
    assert ok["diagnostic"]["actual_archive_bytes"] == ok["archive_bytes"]
    assert ok["diagnostic"]["archive_limit_bytes"] == LIMIT
    assert ok["diagnostic"]["effective_threshold_bytes"] == THRESHOLD
    assert ok["upload_ok"] and ok["marker_exists"]
    assert all(row["composite"] == "False" for row in ok["calls"])
    uploads = [row["argv"] for row in ok["calls"] if "storage" in row["argv"] and "cp" in row["argv"]]
    names = [Path(next(x for x in row if x.startswith("/tmp/r13-upload-") and x != "--recursive")).name for row in uploads[:8]]
    expected = ["evidence.tar.gz", "archive.sha256", "summary.json", "manifest.json", "files-sha256.json",
                "submitted-config.json", "text-logs-index.json", "archive-size-check.json"]
    assert names == expected, names
    recursive = next(i for i, row in enumerate(uploads) if "--recursive" in row)
    marker = next(i for i, row in enumerate(uploads) if any("upload-complete.json" in x for x in row))
    assert recursive == 8 and marker == 9 and marker == len(uploads) - 1
    assert all("--if-generation-match=0" in row for row in uploads)
    assert all(row[-1].startswith(control.BUCKET + "/" + BUILD_ID + "/") or
               row[-1] == control.BUCKET + "/" + BUILD_ID + "/" for row in uploads)
    assert all(row[:3] == ["--configuration=smallsort-ci", "--account=" + control.ACCOUNT,
                           "--project=smallsort-ci"] for row in [r["argv"] for r in ok["calls"]])
    receipt = ok["marker"]
    diagnostic_bytes = json.dumps(ok["diagnostic"], sort_keys=True, indent=2) + "\n"
    assert receipt["archive_size_guard"] == ok["diagnostic"]
    assert receipt["archive_size_guard_sha256"] == hashlib.sha256(diagnostic_bytes.encode()).hexdigest()
    assert receipt["archive_size_bytes"] == ok["archive_bytes"]

    # Synthetic mode is refused based on the actual tiny compressed archive before any cp.
    refused, small = run_case(card=mode_card("synthetic-upload"))
    assert refused.returncode != 0
    assert small["archive_exists"] and small["diagnostic_exists"]
    assert small["diagnostic"]["accepted"] is False
    assert small["diagnostic"]["mode"] == "synthetic-upload"
    assert small["diagnostic"]["actual_archive_bytes"] == small["archive_bytes"]
    assert small["diagnostic"]["archive_limit_bytes"] == LIMIT
    assert small["diagnostic"]["effective_threshold_bytes"] == THRESHOLD
    assert small["diagnostic"]["source"] == {"infra_sha": INFRA, "proof_sha": PROOF}
    assert small["diagnostic"]["build_id"] == BUILD_ID
    assert not small["uploaded"] and not small["marker_exists"] and not small["upload_ok"]
    assert len(small["calls"]) == 2 and all(row["composite"] == "False" for row in small["calls"])

    missing_card, missing = run_case(card=OMIT, r13_required=True)
    assert missing_card.returncode != 0
    assert not missing["archive_exists"] and not missing["uploaded"]
    assert not missing["marker_exists"] and not missing["upload_ok"]
    assert missing["calls"] == [], "required card must be checked before gcloud or packager"

    legacy_cfg = control.config(INFRA, PROOF, "merge", 600, "r13-service", r13_required=False)
    assert "R13_UPLOAD_REQUIRED=false" in legacy_cfg["steps"][0]["env"]
    assert "R13_UPLOAD_REQUIRED=false" in legacy_cfg["steps"][1]["env"]
    legacy_result, legacy = run_case(card=OMIT, r13_required=False)
    assert legacy_result.returncode == 0 and legacy["upload_ok"] and legacy["marker_exists"]
    assert not legacy["diagnostic_exists"], "legacy config keeps its absent-card fallback"

    # Malformed/missing/null mode and policy values fail before the first storage cp.
    malformed = [
        '{"schema":"wrong","mode":"proof-r11","archive_limit_bytes":536870912}',
        json.dumps({**mode_card("proof-r11"), "archive_limit_bytes": None}),
        json.dumps({**mode_card("proof-r11"), "unexpected": 1}),
        "{bad json",
    ]
    for raw in malformed:
        result, state = run_case(card=raw)
        assert result.returncode != 0 and state["diagnostic_exists"]
        assert not state["uploaded"] and not state["marker_exists"] and not state["upload_ok"], raw
    for threshold in ("__EMPTY__", "null", "bad-threshold"):
        result, state = run_case(card=mode_card("proof-r11"), threshold=threshold)
        assert result.returncode != 0 and state["diagnostic_exists"]
        assert not state["uploaded"] and not state["marker_exists"] and not state["upload_ok"], threshold
    result, state = run_case(card=mode_card("proof-r11"), effective="True")
    assert result.returncode != 0 and not state["uploaded"] and not state["marker_exists"]

    # Preserve original upload failures and withhold marker/upload.ok for partial publication.
    failures = {"archive": 17, "chunks": 17, "marker": 17}
    for stage, code in failures.items():
        result, state = run_case(card=mode_card("proof-r11"), failure=stage)
        assert result.returncode == code, (stage, result.returncode, result.stderr)
        assert all(row["composite"] == "False" for row in state["calls"])
        assert not state["upload_ok"]
        if stage in ("archive", "chunks"):
            assert not state["marker_exists"] and "upload-complete.json" not in state["uploaded"]
        else:
            assert state["marker_exists"] and state["uploaded"][-1] == "upload-complete.json"
    print(json.dumps({"classification": "PASS_R13_GENERATED_UPLOAD_SERVICE", "proof_mode": "tiny archive accepted",
                      "synthetic_mode": "tiny archive refused before storage cp",
                      "metadata_refusals": len(malformed) + 4,
                      "upload_failures": {k: v for k, v in failures.items()},
                      "proof_attempted": False, "proof_credit": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
