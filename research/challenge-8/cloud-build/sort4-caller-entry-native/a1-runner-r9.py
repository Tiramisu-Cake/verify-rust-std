#!/usr/bin/env python3
"""R9 authorization adapter for the byte-pinned S3 A1 runner."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path("research/challenge-8/cloud-build/sort4-caller-entry-native")
PROFILE = HERE / "A1-NATIVE-INTERFACE-R9-PROFILE-2026-10-20.json"
PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
AUTHORIZATION_PHASE = "SORT4-NATIVE-INTERFACE-PROOF-2026-10-20-R9"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(a, *, c4, audit, driver, manifest, ghost):
    profile_path = Path(a.proof_root) / PROFILE
    profile_sha = os.environ.get("SORT4_A1_PROFILE_SHA256")
    if (not profile_path.is_file() or not profile_sha or
            _sha(profile_path) != profile_sha):
        raise RuntimeError("A1 R9 runner profile pin differs")
    profile = json.loads(profile_path.read_text())
    if not isinstance(profile, dict):
        raise RuntimeError("A1 R9 runner profile must be an object")
    if (profile.get("authorization_phase_id") != AUTHORIZATION_PHASE or
            profile.get("experiment_protocol_phase_id") != PHASE):
        raise RuntimeError("A1 R9 runner authorization/protocol binding differs")
    core = Path(a.proof_root) / HERE / "a1-runner.py"
    if _sha(core) != profile.get("a1_source_runner_sha256"):
        raise RuntimeError("A1 R9 pinned S3 runner source differs")
    spec = importlib.util.spec_from_file_location("a1_r9_pinned_s3_runner", core)
    if spec is None or spec.loader is None:
        raise RuntimeError("A1 R9 pinned S3 runner cannot load")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if _sha(core) != profile.get("a1_source_runner_sha256"):
        raise RuntimeError("A1 R9 pinned S3 runner changed during import")
    module.AUTHORIZATION_PHASE = AUTHORIZATION_PHASE
    module.PROFILE = PROFILE
    return module.run(a, c4=c4, audit=audit, driver=driver,
                      manifest=manifest, ghost=ghost)
