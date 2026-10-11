#!/usr/bin/env python3
"""Small isolated tests for package-evidence tool-profile classification."""

import hashlib
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "package-evidence.py"
spec = importlib.util.spec_from_file_location("package_evidence", SCRIPT)
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


def encoded(value):
    return json.dumps(value, sort_keys=True).encode()


profile = {
    "schema": "smallsort-tracked-md-profile-v1",
    "profile": "synthetic-candidate-profile",
    "verifast_commit": "f" * 40,
    "proof_sha": "2" * 40,
    "ordered_patch_chain": [{"path": "candidate.patch", "sha256": "a" * 64}],
    "exporter_sha256": "b" * 64,
    "console_sha256": "c" * 64,
    "selected_drop_tool_commit": "d" * 40,
    "effective_tool_commit": "9" * 40,
    "integration_status": "NOT_FOR_INTEGRATION",
}
profile_raw = encoded(profile)
preflight_raw = encoded({
    "schema": "smallsort-compile-preflight-v1",
    "profile": profile["profile"],
    "profile_sha256": "e" * 64,
    "proof_attempted": False,
})
receipt = {
    "profile_build_sha256": hashlib.sha256(profile_raw).hexdigest(),
    "profile_evidence": "/workspace/evidence/allprooflogs/tracked-md-build",
    "actual_tool_sha256": {
        "vf-rust-mir-exporter": profile["exporter_sha256"],
        "verifast": profile["console_sha256"],
    },
    "receipt_sha256": "1" * 64,
    "receipt": {
        "proof_sha": "2" * 40,
        "profile": profile["profile"],
        "cloud_build_id": "build-id",
        "provider": {"build_id": "build-id"},
        "rustc_toolchain": "nightly-pinned",
        "rustc_version": "rustc test\ncommit-hash: 8f7575a9da8e4a4fca3b5668d5a2ea7476db44b3\n",
    },
}
payload = {
    "allprooflogs/tracked-md-build/profile-build.json": profile_raw,
    "allprooflogs/tracked-md-build/compile-preflight.json": preflight_raw,
    "allprooflogs/checked-minimal-bridge/onecell-selected-drop/receipt.json": encoded(receipt),
}

metadata = package.manifest_tool_profile("merge", payload, "2" * 40, "build-id")
assert metadata["baseline"]["patches_in_application_order"] == []
assert metadata["executed"]["profile"] == profile["profile"]
assert metadata["executed"]["patches_in_application_order"] == profile["ordered_patch_chain"]
assert metadata["executed"]["accepted"] is False
assert metadata["executed"]["tool_commit"] == profile["effective_tool_commit"]
assert metadata["executed"]["compiler_commit"] == "8f7575a9da8e4a4fca3b5668d5a2ea7476db44b3"
assert package.manifest_tool_profile("merge", {}, "2" * 40, "build-id")["executed"]["status"] == "unknown"
assert package.manifest_tool_profile("stock", {}, "2" * 40, "build-id")["executed"]["patches_in_application_order"] == []
assert len(package.manifest_tool_profile("constructor", {}, "2" * 40, "build-id")["executed"]["patches_in_application_order"]) == 2

bad = dict(payload)
bad_receipt = dict(receipt)
bad_receipt["profile_build_sha256"] = "0" * 64
bad["allprooflogs/checked-minimal-bridge/onecell-selected-drop/receipt.json"] = encoded(bad_receipt)
assert package.manifest_tool_profile("merge", bad, "2" * 40, "build-id")["executed"]["status"] == "inconsistent"

partial = package.manifest_tool_profile("merge", {next(iter(payload)): payload[next(iter(payload))]}, "2" * 40, "build-id")
assert partial["executed"]["status"] == "inconsistent"

cross_build = package.manifest_tool_profile("merge", payload, "2" * 40, "other-build")
assert cross_build["executed"]["status"] == "inconsistent"

print("package-evidence profile service checks passed")
