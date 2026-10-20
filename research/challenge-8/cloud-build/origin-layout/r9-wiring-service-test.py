#!/usr/bin/env python3
"""Synthetic R9 profile dispatch and guard-trace environment controls."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
R9 = "experimental-merge-guard-current-return-r9-v1"
R10 = "experimental-merge-moving-gap-r10-v1"
R8 = "experimental-merge-owned-array-allocation-r8-v1"
R7 = "experimental-merge-late-callback-recovery-r7-v1"
TRACE = "SMALLSORT_R9_GUARD_TRACE"
PROVE = ROOT / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    callback = load("r9_wiring_callback", HERE / "first-callback.py")
    prove = load("r9_wiring_prove", PROVE)
    callback_source = (HERE / "first-callback.py").read_text()
    run_body = callback_source[callback_source.index("def run(evidence, args, env, execute_case, validated_receipt):"):]
    env_copy_at = run_body.index("campaign_env = dict(env)")
    env_scrub_at = run_body.index("campaign_env.pop(R9_GUARD_TRACE_ENV, None)")
    first_control_at = run_body.index("share_controls.run")
    assert env_copy_at < env_scrub_at < first_control_at
    assert "evidence/'share-representation-controls', args, campaign_env" in run_body
    assert "evidence/'guard-array-controls', args, campaign_env" in run_body

    parent_env = {"KEEP": "yes", TRACE: "stale-parent-value"}
    captured = {}

    def capture(_case, _args, env):
        captured.update(env)
        return {"ok": True}

    callback._execute_case_with_r9_trace(
        capture, Path("case"), object(), parent_env, profile=R9,
        prefix=False, actual_callback_case=True)
    assert captured[TRACE] == "1"
    assert captured["KEEP"] == "yes"
    assert parent_env == {"KEEP": "yes", TRACE: "stale-parent-value"}

    for profile, prefix in ((R9, True), (R10, True), (R8, False), (R7, False), ("baseline", False)):
        captured.clear()
        callback._execute_case_with_r9_trace(
            capture, Path("case"), object(), parent_env, profile=profile,
            prefix=prefix, actual_callback_case=True)
        assert TRACE not in captured, (profile, prefix, captured)
        assert parent_env[TRACE] == "stale-parent-value"

    def raises(_case, _args, env):
        assert env is not parent_env
        env[TRACE] = "mutated-child"
        raise RuntimeError("synthetic callback failure")

    try:
        callback._execute_case_with_r9_trace(
            raises, Path("case"), object(), parent_env, profile=R9,
            prefix=False, actual_callback_case=True)
    except RuntimeError as error:
        assert str(error) == "synthetic callback failure"
    else:
        raise AssertionError("synthetic callback error was swallowed")
    assert parent_env[TRACE] == "stale-parent-value"

    with tempfile.TemporaryDirectory(prefix="r9-profile-binding-") as temp:
        profile_path = Path(temp) / "profile.json"
        profile_path.write_text(json.dumps({"profile": R9, "schema": "test-v1",
                                           "accepted": False,
                                           "effective_tool_commit": "a" * 40}))
        freshness = load("r9_wiring_freshness", HERE / "r8-freshness-controls.py")
        binding = freshness._profile_binding(SimpleNamespace(profile=R9),
                                              {"SMALLSORT_MERGE_PROFILE": str(profile_path)})
        assert binding["profile"] == R9 and binding["profile_accepted"] is False
        profile_path.write_text(json.dumps({"profile": R10, "schema": "test-v1",
                                           "accepted": False,
                                           "effective_tool_commit": "b" * 40}))
        binding = freshness._profile_binding(SimpleNamespace(profile=R10),
                                              {"SMALLSORT_MERGE_PROFILE": str(profile_path)})
        assert binding["profile"] == R10 and binding["profile_accepted"] is False

    parser_tree = ast.parse(PROVE.read_bytes())
    allocation_args = [node for node in ast.walk(parser_tree)
                        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                        and node.func.attr == "add_argument" and node.args
                        and isinstance(node.args[0], ast.Constant)
                        and node.args[0].value == "--r8-owned-array-allocation"]
    assert len(allocation_args) == 1
    keywords = {node.arg: node.value for node in allocation_args[0].keywords}
    assert isinstance(keywords.get("action"), ast.Constant) and keywords["action"].value == "store_true"
    assert isinstance(keywords.get("default"), ast.Constant) and keywords["default"].value is False
    source = ast.unparse(parser_tree)
    assert "args.profile not in (R8_PROFILE, R9_PROFILE, R10_PROFILE)" in source
    baseline_path = HERE / "R9-BASELINE-PROFILE-20261020.json"
    baseline_raw = baseline_path.read_bytes()
    assert hashlib.sha256(baseline_raw).hexdigest() == (
        "838ade9927ebba82b8df61283fdd8189e71b673ac91eadf897806d0bfaa80cc1")
    baseline = json.loads(baseline_raw)
    r9_profile = json.loads((HERE / "R10-BASELINE-PROFILE-20261021.json").read_text())
    assert r9_profile["profile"] == R9 and r9_profile["accepted"] is False
    assert r9_profile["ordered_patch_chain"][:-1] == baseline["ordered_patch_chain"]
    assert "R9-BASELINE-PROFILE-20261020.json" in (
        ROOT / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/build-profile.sh").read_text()

    with tempfile.TemporaryDirectory(prefix="r9-cli-case-") as temp:
        case = Path(temp)
        for folder in ("original", "verified"):
            (case / folder).mkdir()
            (case / folder / "lib.rs").write_text("pub fn fixture() {}\n")
        args = SimpleNamespace(profile=R9, tool_home=Path("/tool"),
            compiler_sysroot=Path("/sysroot"), schema=Path("/schema/vf_mir.capnp"),
            stage_seconds=1, verifier_seconds=1, r8_owned_array_allocation=True,
            first_fnmut_continue=False)
        stage_calls = []

        def stage(_case, name, command, _env, **_kwargs):
            stage_calls.append((name, list(command)))
            return 0

        with patch.object(prove.base, "run_stage", side_effect=stage):
            result = prove.execute_case(case, args, {})
        vf_command = next(command for name, command in stage_calls if name == "verifast")
        assert "-rust_owned_array_allocation_r8" in vf_command
        assert result["r8_owned_array_allocation"] is True

        args.profile = R10
        with patch.object(prove.base, "run_stage", side_effect=stage):
            result = prove.execute_case(case, args, {})
        vf_command = next(command for name, command in stage_calls if name == "verifast")
        assert "-rust_owned_array_allocation_r8" in vf_command
        assert result["r8_owned_array_allocation"] is True

        args.profile = R7
        with patch.object(prove.base, "run_stage", side_effect=stage):
            try:
                prove.execute_case(case, args, {})
            except ValueError as error:
                assert "exact R8 profile" in str(error)
            else:
                raise AssertionError("allocation option was not profile-gated")

    consumers = (
        HERE / "first-callback.py",
        HERE / "r8-freshness-controls.py",
        HERE / "r7-late-admission-controls.py",
        HERE / "onecell-selected-drop.py",
        HERE / "onecell-caller-composition.py",
        HERE / "concrete-consumer.py",
        HERE / "compile-preflight.sh",
        HERE.parent / "../merge/cloud-build/provider-overlays.py",
    )
    for path in consumers:
        assert R9 in path.read_text() and R10 in path.read_text(), (path, R9, R10)
    print("R9 profile/default-off allocation/trace isolation synthetic checks PASS")


if __name__ == "__main__":
    main()
