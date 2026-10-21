#!/usr/bin/env python3
"""Isolated service checks for R12 source-freeze preflight helpers."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile


MODULE_PATH = Path(__file__).with_name("r12-source-preflight.py")
SPEC = importlib.util.spec_from_file_location("r12_source_preflight", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def check(label, action, expected_error=None):
    try:
        action()
    except (ValueError, OSError) as error:
        if expected_error is None or expected_error not in str(error):
            raise AssertionError(f"{label}: unexpected error: {error}") from error
    else:
        if expected_error is not None:
            raise AssertionError(f"{label}: expected refusal containing {expected_error!r}")


def test_aggregate_order_and_refusal():
    files = {"a": b"alpha", "b": b"beta"}
    def read(path):
        if path not in files:
            raise FileNotFoundError(path)
        return files[path]
    first, missing = MODULE.aggregate(["a", "b"], read)
    second, _ = MODULE.aggregate(["b", "a"], read)
    assert first != second and not missing
    digest, missing = MODULE.aggregate(["a", "absent"], read)
    assert digest != first and missing == ["absent"]


def test_mode_cards():
    with tempfile.TemporaryDirectory(prefix="r12-source-mode-test-") as temp:
        root = Path(temp)
        mode = root / "mode.json"
        original_root, original_path = MODULE.ROOT, MODULE.MODE_PATH
        try:
            MODULE.ROOT, MODULE.MODE_PATH = root, "mode.json"
            synthetic = {
                "schema": "merge-r12-upload-mode-v1", "mode": "synthetic-upload",
                "payload_bytes": 536870912, "threshold_bytes": 157286400,
                "threshold_source": "https://docs.cloud.google.com/storage/docs/parallel-composite-uploads",
                "proof_attempted": False,
            }
            mode.write_text(json.dumps(synthetic))
            MODULE.validate_mode()
            for field, bad_value in (("payload_bytes", 536870912.0),
                                     ("threshold_bytes", True),
                                     ("proof_attempted", 0)):
                malformed = dict(synthetic, **{field: bad_value})
                mode.write_text(json.dumps(malformed))
                check(f"wrong {field} type", MODULE.validate_mode,
                      "fixed contract")
            proof = {"schema": "merge-r12-upload-mode-v1", "mode": "proof-r11"}
            mode.write_text(json.dumps(proof))
            MODULE.validate_mode()
            proof["proof_attempted"] = False
            mode.write_text(json.dumps(proof))
            check("extra proof field", MODULE.validate_mode, "only its exact mode identity")
            mode.unlink()
            mode.symlink_to(root / "missing-target")
            check("mode symlink", MODULE.validate_mode, "not a regular file")
        finally:
            MODULE.ROOT, MODULE.MODE_PATH = original_root, original_path


def test_recipe_allowlist():
    with tempfile.TemporaryDirectory(prefix="r12-source-recipe-test-") as temp:
        root = Path(temp)
        original_root, original_git = MODULE.ROOT, MODULE.git
        baseline = {
            "proof_paths": ["frozen.py"],
            "entrypoint": "research/challenge-8/cloud-build/run-merge.sh",
            "infra_paths": ["research/challenge-8/cloud-build/run-merge.sh"],
        }
        try:
            MODULE.ROOT = root
            recipe_path = root / "research/challenge-8/cloud-build/recipes/merge.json"
            recipe_path.parent.mkdir(parents=True)
            for relative in ["frozen.py", *MODULE.REQUIRED_R12]:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture\n")
            fake_git = lambda *args: json.dumps(baseline).encode()
            MODULE.git = fake_git
            current = {
                "proof_paths": sorted(["frozen.py", *MODULE.REQUIRED_R12]),
                "entrypoint": baseline["entrypoint"],
                "infra_paths": list(baseline["infra_paths"]),
            }
            recipe_path.write_text(json.dumps(current))
            MODULE.validate_recipe(["frozen.py"])
            current["infra_paths"].append("unexpected-infra.sh")
            recipe_path.write_text(json.dumps(current))
            check("extra infra path", lambda: MODULE.validate_recipe(["frozen.py"]),
                  "entrypoint or infra path set")
            current["infra_paths"].pop()
            current["entrypoint"] = "unexpected-entrypoint.sh"
            recipe_path.write_text(json.dumps(current))
            check("changed entrypoint", lambda: MODULE.validate_recipe(["frozen.py"]),
                  "entrypoint or infra path set")
            current["entrypoint"] = baseline["entrypoint"]
            current["proof_paths"].append("unexpected.py")
            current["proof_paths"].sort()
            recipe_path.write_text(json.dumps(current))
            check("unknown recipe addition", lambda: MODULE.validate_recipe(["frozen.py"]),
                  "bounded allowlist")
            current["proof_paths"].remove("frozen.py")
            recipe_path.write_text(json.dumps(current))
            check("removed frozen source", lambda: MODULE.validate_recipe(["frozen.py"]),
                  "removed frozen R11")
        finally:
            MODULE.ROOT, MODULE.git = original_root, original_git


def main():
    test_aggregate_order_and_refusal()
    test_mode_cards()
    test_recipe_allowlist()
    print("R12 source-preflight synthetic service checks PASS (3 groups)")


if __name__ == "__main__":
    main()
