#!/usr/bin/env python3
"""R21 adapter for the separately pinned complete actual sort4 body runner."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path("research/challenge-8/cloud-build/sort4-caller-entry-native")
ROUTED_PROFILE = HERE / "A1-ACTUAL-BODY-R21-TRANSPORT-PROFILE.json"
PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
AUTHORIZATION_PHASE = "SORT4-ACTUAL-C2-2026-10-21-R17"
EXECUTION_PHASE_ID = "SORT4-ACTUAL-SELECT-2026-10-23-R21"
EXECUTION_LANE = "o26-sort4-body-r21"
ACTUAL_BODY = HERE / "a1-actual-body-r21.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_runner_route(env, profile):
    """Require R21 execution authority and separately pinned R17 protocol identity."""
    if (env.get("SMALLSORT_EXECUTION_PROVIDER") != "cloud-build" or
            env.get("SORT4_R21_BODY_PHASE_ID") != EXECUTION_PHASE_ID or
            env.get("LANE") != EXECUTION_LANE or not env.get("CLOUD_BUILD_ID") or
            env.get("GITHUB_ACTIONS")):
        raise RuntimeError("A1 R21 runner requires fresh authorized Cloud lane")
    if (profile.get("execution_authority_phase_id") != EXECUTION_PHASE_ID or
            profile.get("execution_lane") != EXECUTION_LANE or
            profile.get("authorization_phase_id") != AUTHORIZATION_PHASE or
            profile.get("phase_id") != PHASE or
            profile.get("experiment_protocol_phase_id") != PHASE or
            profile.get("execution_mode") != "actual-sort4-body-v1" or
            profile.get("body_action") != "full-body-c1-recovery" or
            profile.get("cloud_build_enabled") is not True):
        raise RuntimeError("A1 R21 runner profile route/backend binding differs")


def run(a, *, c4, audit, driver, manifest, ghost):
    profile_sha = os.environ.get("SORT4_A1_PROFILE_SHA256")
    profile_path = Path(a.proof_root) / ROUTED_PROFILE
    matches = [profile_path] if (profile_path.is_file() and profile_sha and
                                 _sha(profile_path) == profile_sha) else []
    if len(matches) != 1:
        raise RuntimeError("A1 R21 runner profile pin differs")
    profile_path = matches[0]
    profile = json.loads(profile_path.read_text())
    if not isinstance(profile, dict):
        raise RuntimeError("A1 R21 runner profile must be an object")
    require_runner_route(os.environ, profile)
    body = Path(a.proof_root) / ACTUAL_BODY
    expected = profile.get("a1_actual_body_sha256")
    if not isinstance(expected, str) or len(expected) != 64 or _sha(body) != expected:
        raise RuntimeError("A1 R17 actual body implementation pin differs")
    spec = importlib.util.spec_from_file_location("a1_r21_actual_body", body)
    if spec is None or spec.loader is None:
        raise RuntimeError("A1 R17 actual body implementation cannot load")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if _sha(body) != expected:
        raise RuntimeError("A1 R17 actual body implementation changed during import")
    return module.run(a, c4=c4, audit=audit, driver=driver,
                      manifest=manifest, ghost=ghost)
