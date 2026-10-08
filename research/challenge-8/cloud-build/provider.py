#!/usr/bin/env python3
"""Provider identity checks for the narrowly scoped cloud proof runner."""

from __future__ import annotations

import json
import os
from pathlib import Path
import platform
import sys
import uuid


def provider_record() -> dict[str, str]:
    """Accept a genuine GitHub host or an explicitly identified cloud build."""
    cloud = os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build"
    build_id = os.environ.get("CLOUD_BUILD_ID", "").strip()
    project = os.environ.get("CLOUD_BUILD_PROJECT_ID", "").strip()
    region = os.environ.get("CLOUD_BUILD_REGION", "").strip()
    valid_id = False
    try:
        valid_id = str(uuid.UUID(build_id)) == build_id.lower()
    except (ValueError, AttributeError):
        pass
    os_release = Path("/etc/os-release")
    release = {}
    if os_release.is_file():
        for line in os_release.read_text().splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                release[key] = value.strip('"')
    if (cloud and valid_id and project == "smallsort-ci" and region == "global" and
            platform.system() == "Linux" and platform.machine().lower() in ("x86_64", "amd64") and
            release.get("ID") == "ubuntu" and release.get("VERSION_ID") == "22.04"):
        return {
            "provider": "cloud-build",
            "build_id": build_id,
            "project": project,
            "region": region,
            "os": "ubuntu-22.04",
            "arch": "x86_64",
        }
    if (not cloud and os.environ.get("GITHUB_ACTIONS") == "true" and
            os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted" and
            os.environ.get("RUNNER_OS") == "Linux"):
        return {"provider": "github-hosted", "os": "Linux"}
    raise SystemExit("proof requires genuine GitHub-hosted Linux or identified Ubuntu 22.04 Cloud Build")


def require_supported_provider() -> dict[str, str]:
    return provider_record()


if __name__ == "__main__":
    print(json.dumps(require_supported_provider(), sort_keys=True))
