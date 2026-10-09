#!/usr/bin/env python3
"""Cloud-only exact Build 673 controls reuse; never runs the historical matrix."""

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
from urllib.parse import quote
from urllib.request import Request, urlopen


BUILD = "673526ac-6556-40bc-9ebe-7792e257bfcd"
ARCHIVE_SHA = "11ebebd82f74b42b4fd1a66cfa9959dc58bc4793629569545d35a2447c20e861"
INFRA = "9f22416ac13ac006f505605b57b50f37629caef1"
PROOF = "d253128ac42f5788cc322201bdfcc6c1e2e36f76"
CONFIG = "0d3bdf60f461b0fb6eff7c55664ccd7ab094ac179f59be611c66294989e28e25"
LANE = "o26-strict-cut-false-posts"
BUCKET = "smallsort-ci-evidence-504462351565"
OBJECTS = ("evidence.tar.gz", "archive.sha256", "summary.json", "manifest.json",
           "files-sha256.json", "submitted-config.json", "upload-complete.json",
           "text-logs-index.json")
CONTROLS = "allprooflogs/cases/strict-cut-controls/"
RELOCATION = "allprooflogs/cases/cut-relocate/"


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    need(path.is_file() and not path.is_symlink(), f"missing regular file: {path.name}")
    return json.loads(path.read_text())


def cloud_token():
    request = Request("http://metadata.google.internal/computeMetadata/v1/instance/"
                      "service-accounts/default/token", headers={"Metadata-Flavor": "Google"})
    with urlopen(request, timeout=15) as response:
        token = json.load(response).get("access_token")
    need(isinstance(token, str) and bool(token), "Cloud metadata token missing")
    return token


def download(directory, token):
    for name in OBJECTS:
        object_name = f"cloud-build/{BUILD}/{name}"
        url = (f"https://storage.googleapis.com/storage/v1/b/{BUCKET}/o/"
               f"{quote(object_name, safe='')}?alt=media")
        request = Request(url, headers={"Authorization": f"Bearer {token}"})
        target = directory / name
        limit = 128 * 1024 * 1024 if name == "evidence.tar.gz" else 8 * 1024 * 1024
        with urlopen(request, timeout=45) as response, target.open("xb") as output:
            size = 0
            while block := response.read(1024 * 1024):
                size += len(block)
                need(size <= limit, f"historical object oversized: {name}")
                output.write(block)


def extract_selected(archive, evidence, historical, inventory):
    names = set()
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar:
            name = member.name
            path = PurePosixPath(name)
            need(not path.is_absolute() and path.as_posix() == name and
                 all(part not in ("", ".", "..") for part in path.parts) and
                 member.isfile() and name not in names,
                 "historical archive contains unsafe member")
            names.add(name)
            if name.startswith(CONTROLS):
                relative = name.removeprefix(CONTROLS)
                need(relative, "empty historical controls path")
                destination = evidence / relative
            elif name.startswith(RELOCATION) and name.removeprefix(RELOCATION) in (
                    "production-snapshot.json", "source-audit.json"):
                destination = historical / name.removeprefix(RELOCATION)
            elif name == "allprooflogs/refreshed-applied.patch":
                destination = historical / "refreshed-applied.patch"
            else:
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            need(not destination.exists(), "duplicate selected historical member")
            stream = tar.extractfile(member)
            need(stream is not None, "unreadable historical member")
            with destination.open("xb") as output:
                shutil.copyfileobj(stream, output)
            need(digest(destination) == inventory.get(name),
                 "selected historical member differs from verified inventory")
    need((evidence / "cases").is_dir() and
         (evidence / "capture-exits.json").is_file() and
         (evidence / "diagnostic-audit.json").is_file(),
         "historical controls incomplete")
    for name in ("production-snapshot.json", "source-audit.json", "refreshed-applied.patch"):
        need((historical / name).is_file(), f"historical identity missing: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("production-source", "production-applied-patch", "stock-home",
                 "compiler-sysroot", "evidence", "deadline-epoch", "proof-root",
                 "work-root", "cloud-dir", "relocation-evidence"):
        parser.add_argument("--" + flag, required=True)
    a = parser.parse_args()
    paths = [Path(getattr(a, key.replace("-", "_"))) for key in (
        "production-source", "production-applied-patch", "stock-home",
        "compiler-sysroot", "evidence", "proof-root", "work-root", "cloud-dir",
        "relocation-evidence")]
    need(all(str(path).startswith("/workspace/") and ".." not in path.parts and
             "." not in path.parts for path in paths), "Cloud workspace path required")
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         not os.environ.get("GITHUB_ACTIONS") and
         os.environ.get("LANE") == "o26-strict-cut-reuse-false-posts",
         "Cloud reuse lane identity required")
    evidence = Path(a.evidence)
    need(not evidence.exists(), "reuse evidence already exists")
    evidence.mkdir(parents=True)
    report = {"classification": "INCONCLUSIVE", "accepted": False,
              "historical_build_id": BUILD, "historical_cases_executed_in_this_build": 0,
              "historical_case_count": 17, "new_false_post_cases_executed_here": 0}
    try:
        need(a.deadline_epoch.isdecimal() and int(a.deadline_epoch) > 0,
             "invalid deadline")
        cloud = Path(a.cloud_dir)
        relocation = Path(a.relocation_evidence)
        historical = Path(a.work_root) / "strict-cut-historical-673"
        need(not historical.exists(), "historical scratch already exists")
        historical.mkdir()
        download(historical, cloud_token())
        need(digest(historical / "evidence.tar.gz") == ARCHIVE_SHA,
             "pinned historical archive digest differs")
        verify = subprocess.run((sys.executable, str(cloud / "verify-evidence.py"),
            "--directory", str(historical), "--expected-build-id", BUILD,
            "--expected-infra-sha", INFRA, "--expected-proof-sha", PROOF,
            "--expected-config-sha", CONFIG, "--expected-lane", LANE,
            "--require-text-logs"), capture_output=True, text=True, check=False)
        need(verify.returncode == 0, "historical archive/receipt inventory verification failed")
        integrity = json.loads(verify.stdout)
        need(integrity.get("integrity_verified") is True and
             integrity.get("archive_sha256") == ARCHIVE_SHA and
             integrity.get("verification_accepted") is False,
             "historical evidence status differs")
        extract_selected(historical / "evidence.tar.gz", evidence, historical,
                         load(historical / "files-sha256.json"))
        old_audit = load(evidence / "diagnostic-audit.json")
        need(old_audit.get("classification") == "INCONCLUSIVE" and
             old_audit.get("accepted") is False and
             old_audit.get("reason") ==
             "negative_end_lifetime_twice: first error has no source location",
             "historical failed-audit identity differs")
        shutil.copyfile(evidence / "diagnostic-audit.json",
                        evidence / "historical-diagnostic-audit.json")
        shutil.copyfile(historical / "upload-complete.json",
                        evidence / "historical-upload-complete.json")
        archived_overlay = load(evidence / "provider-overlay-manifest.json")
        shutil.copyfile(evidence / "provider-overlay-manifest.json",
                        evidence / "historical-provider-overlay-manifest.json")
        for name in ("production-snapshot.json", "source-audit.json"):
            need(load(historical / name) == load(relocation / name),
                 f"fresh production/relocation identity differs: {name}")
        need((historical / "refreshed-applied.patch").read_bytes() ==
             Path(a.production_applied_patch).read_bytes(),
             "fresh production patch differs from Build 673")
        overlay = subprocess.run((sys.executable,
            str(cloud / "cut-trace-provider-overlay.py"),
            "--proof-root", a.proof_root, "--cloud-dir", a.cloud_dir,
            "--evidence", a.evidence), capture_output=True, text=True,
            check=False)
        need(overlay.returncode == 0,
             "fresh frozen capture/provider guard-only overlay failed")
        need(load(evidence / "provider-overlay-manifest.json") == archived_overlay,
             "fresh guard-only overlay differs from verified Build 673 manifest")
        relocation_source = Path(a.work_root) / "cut-relocation-isolated-source"
        output = evidence / "diagnostic-audit.json"
        audit = subprocess.run((sys.executable, str(cloud / "strict-cut-controls-audit.py"),
            "final", "--production-source", a.production_source,
            "--production-applied-patch", a.production_applied_patch,
            "--stock-home", a.stock_home, "--relocation-source", str(relocation_source),
            "--relocation-evidence", a.relocation_evidence,
            "--proof-root", a.proof_root, "--cloud-dir", a.cloud_dir,
            "--evidence", a.evidence, "--output", str(output)),
            capture_output=True, text=True, check=False)
        need(audit.returncode == 0, "historical matrix re-audit failed")
        fresh = load(output)
        need(fresh.get("classification") == "CONTROLS_DISCOVERY_REVIEW_REQUIRED" and
             fresh.get("accepted") is False and len(fresh.get("cases", [])) == 17,
             "historical matrix re-audit incomplete")
        report.update({"classification": "HISTORICAL_STRICT_CUT_MATRIX_REAUDITED",
                       "archive_sha256": ARCHIVE_SHA, "infra_sha": INFRA,
                       "proof_sha": PROOF, "config_sha256": CONFIG,
                       "verified_inventory": True, "fresh_tool_identity_equal": True,
                       "historical_case_count": len(fresh["cases"]),
                       "historical_audit_sha256": digest(evidence / "historical-diagnostic-audit.json"),
                       "current_audit_sha256": digest(output)})
    except Exception as exc:
        report["reason"] = str(exc)
    (evidence / "reuse-provenance.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    if report["classification"] == "INCONCLUSIVE":
        raise SystemExit("strictCUT historical reuse inconclusive: " + report["reason"])


if __name__ == "__main__":
    main()
