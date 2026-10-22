#!/usr/bin/env python3
"""R17 adapter for the separately pinned complete actual sort4 body runner."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path("research/challenge-8/cloud-build/sort4-caller-entry-native")
ROUTED_PROFILES = (HERE / "A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json",
                   HERE / "A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json")
PHASE = "SORT4-A1-CHECKED-TRAIT-CONTRACT-CLOUD-2026-10-17"
AUTHORIZATION_PHASE = "SORT4-ACTUAL-C2-2026-10-21-R17"
ACTUAL_BODY = HERE / "a1-actual-body-r17.py"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(a, *, c4, audit, driver, manifest, ghost):
    profile_sha = os.environ.get("SORT4_A1_PROFILE_SHA256")
    matches = [Path(a.proof_root) / rel for rel in ROUTED_PROFILES
               if (Path(a.proof_root) / rel).is_file() and profile_sha and
               _sha(Path(a.proof_root) / rel) == profile_sha]
    if len(matches) != 1:
        raise RuntimeError("A1 R17 runner profile pin differs")
    profile_path = matches[0]
    profile = json.loads(profile_path.read_text())
    if not isinstance(profile, dict):
        raise RuntimeError("A1 R17 runner profile must be an object")
    if (profile.get("authorization_phase_id") != AUTHORIZATION_PHASE or
            profile.get("experiment_protocol_phase_id") != PHASE or
            profile.get("execution_mode") != "actual-sort4-body-v1" or
            profile.get("body_action") != "full-body-c1-recovery"):
        raise RuntimeError("A1 R17 runner authorization/protocol/body binding differs")
    body = Path(a.proof_root) / ACTUAL_BODY
    expected = profile.get("a1_actual_body_sha256")
    if not isinstance(expected, str) or len(expected) != 64 or _sha(body) != expected:
        raise RuntimeError("A1 R17 actual body implementation pin differs")
    spec = importlib.util.spec_from_file_location("a1_r17_actual_body", body)
    if spec is None or spec.loader is None:
        raise RuntimeError("A1 R17 actual body implementation cannot load")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if _sha(body) != expected:
        raise RuntimeError("A1 R17 actual body implementation changed during import")
    return module.run(a, c4=c4, audit=audit, driver=driver,
                      manifest=manifest, ghost=ghost)
