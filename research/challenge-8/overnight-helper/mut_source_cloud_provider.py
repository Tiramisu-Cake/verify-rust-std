#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Strict identified-Cloud gate shared by the inactive mutable source route."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import sys


PROVIDER_SHA256 = "771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616"


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("MUTABLE-SOURCE-CLOUD: " + why)


def validate_provider_record(record: dict, env: dict[str, str]) -> dict:
    """Pure gate for tests; input env/record are data, never process identity."""
    need(not env.get("GITHUB_ACTIONS"),
         "GitHub identity is forbidden for actual mutable source preparation")
    need(env.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         bool(env.get("CLOUD_BUILD_ID")) and
         env.get("CLOUD_BUILD_PROJECT_ID") == "smallsort-ci" and
         env.get("CLOUD_BUILD_REGION") == "global",
         "required Cloud Build environment identity is missing or wrong")
    need(record.get("provider") == "cloud-build",
         "identified Cloud Build provider required")
    need(record.get("project") == "smallsort-ci" and
         record.get("region") == "global" and
         record.get("os") == "ubuntu-22.04" and
         record.get("arch") == "x86_64" and
         bool(record.get("build_id")),
         "Cloud provider identity record is incomplete or wrong")
    return record


def require_cloud_provider(env: dict[str, str] | None = None,
                           provider_loader=None) -> dict:
    """Require the pinned provider module and its genuine Cloud identity."""
    env = os.environ if env is None else env
    need(not env.get("GITHUB_ACTIONS"),
         "GitHub identity is forbidden for actual mutable source preparation")
    # The repository's accepted Cloud entrypoint already pins this provider;
    # resolve it from the checked-out worktree instead of requiring a new
    # runner/recipe environment variable.
    path = Path(__file__).resolve().parents[1] / "cloud-build/provider.py"
    need(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() ==
         PROVIDER_SHA256, "pinned Cloud provider.py is missing or changed")
    if provider_loader is None:
        spec = importlib.util.spec_from_file_location(
            "smallsort_mutable_cloud_provider", path)
        need(spec is not None and spec.loader is not None,
             "cannot load pinned Cloud provider.py")
        provider = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = provider
        spec.loader.exec_module(provider)
        provider_loader = provider.require_supported_provider
    record = provider_loader()
    return validate_provider_record(record, env)
