#!/usr/bin/env python3
"""Guard-only Cloud adaptation of disposable capture-relocate.py."""

import argparse
import difflib
import hashlib
import json
from pathlib import Path

BASE_SHA = "31fc83eea22c92ee73b1fc17a79f24ca057c343fbca2699673b4a6bc5c93bb10"
PROVIDER_SHA = "771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616"
OLD = (b'    cut.need(os.getenv("GITHUB_ACTIONS") == "true" and\n'
       b'             os.getenv("RUNNER_ENVIRONMENT") == "github-hosted" and\n'
       b'             os.getenv("RUNNER_OS") == "Linux", "hosted GitHub Linux required")')
NEW = (b'    provider_path = Path(os.environ["SMALLSORT_CLOUD_PROVIDER_PATH"])\n'
       b'    spec = importlib.util.spec_from_file_location("smallsort_provider", provider_path)\n'
       b'    provider = importlib.util.module_from_spec(spec)\n'
       b'    spec.loader.exec_module(provider)\n'
       b'    cut.need(provider.require_supported_provider()["provider"] == "cloud-build",\n'
       b'             "identified Cloud Build required")')


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--proof-root", type=Path, required=True)
    p.add_argument("--cloud-dir", type=Path, required=True)
    p.add_argument("--evidence", type=Path, required=True)
    a = p.parse_args()
    target = a.proof_root / "research/challenge-8/overnight-lifetime/capture-relocate.py"
    provider = a.cloud_dir / "provider.py"
    before = target.read_bytes()
    if sha(before) != BASE_SHA or sha(provider.read_bytes()) != PROVIDER_SHA:
        raise SystemExit("frozen relocation capture/provider bytes differ")
    if before.count(OLD) != 1:
        raise SystemExit("relocation capture provider guard is not unique")
    after = before.replace(OLD, NEW, 1)
    if after.replace(NEW, OLD, 1) != before:
        raise SystemExit("relocation provider overlay is not guard-only")
    target.write_bytes(after)
    (a.evidence / "provider-overlay-manifest.json").write_text(json.dumps({
        "path": str(target.relative_to(a.proof_root)), "base_sha256": sha(before),
        "overlay_sha256": sha(after), "provider_sha256": sha(provider.read_bytes()),
        "guard_only": True,
        "diff": "".join(difflib.unified_diff(
            before.decode().splitlines(True), after.decode().splitlines(True),
            fromfile="capture-relocate.py.base", tofile="capture-relocate.py.cloud-build")),
    }, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
