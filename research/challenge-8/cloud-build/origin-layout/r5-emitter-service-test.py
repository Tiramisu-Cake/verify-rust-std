#!/usr/bin/env python3
"""Synthetic checks for R5 addressability diagnostics and profile identity."""
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import subprocess
import sys

HERE = Path(__file__).resolve().parent
provider_spec = importlib.util.spec_from_file_location(
    "provider_overlays_profile_test", HERE.parents[1] / "merge/cloud-build/provider-overlays.py")
if provider_spec is None or provider_spec.loader is None:
    raise RuntimeError("provider overlay module is unavailable")
provider = importlib.util.module_from_spec(provider_spec)
provider_spec.loader.exec_module(provider)
receiver_spec = importlib.util.spec_from_file_location(
    "generated_glue_receiver_r5_test", HERE / "generated-glue-receiver-controls.py")
receiver = importlib.util.module_from_spec(receiver_spec)
receiver_spec.loader.exec_module(receiver)
compat_spec = importlib.util.spec_from_file_location(
    "generated_glue_compat_r5_test", HERE / "generated-glue-compatibility-controls.py")
compat = importlib.util.module_from_spec(compat_spec)
compat_spec.loader.exec_module(compat)

spec = importlib.util.spec_from_file_location(
    "r5_addressability_controls_test", HERE / "r5-addressability-controls.py")
if spec is None or spec.loader is None:
    raise RuntimeError("R5 addressability controls module is unavailable")
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

def sha(path):
    return runner._sha(path.read_bytes())

def make_stage_receipts(case, meta):
    hashes = {"original/lib.rs": sha(case / "original/lib.rs"),
              "verified/lib.rs": sha(case / "verified/lib.rs")}
    for stage, code in meta["expected_stages"].items():
        (case / f"{stage}-stage.json").write_text(json.dumps({
            "stage": stage, "exit_code": code, "source_unchanged": True,
            "source_before": hashes, "source_after": hashes}))

def classify_flags(case, meta, flags):
    (case / "verified/lib.v").write_text(flags)
    target_lines = "".join(
        f"verified/lib.rs({line},1-2): Executing statement\n"
        for line in meta["target_lines"])
    (case / "verifast.log").write_text(
        target_lines + "Executing return statement\nLeak check.\n0 errors found\n")
    return runner.classify("address_after_merge", case, meta, {
        "stages": meta["expected_stages"], "source_unchanged_at_every_stage": True})

with tempfile.TemporaryDirectory(prefix="r5-emitter-service-") as temp:
    root = Path(temp)
    metadata = runner.prepare(root / "suite")
    case = root / "suite" / "address_after_merge"
    meta = metadata["address_after_merge"]
    make_stage_receipts(case, meta)
    assert classify_flags(case, meta, 'LocalAddrTaken "local" true;;\n')["classification"] == "PASS_CONTROL"
    for flags in ('LocalAddrTaken "local" false;;\n', "",
                  'LocalAddrTaken "local" true;;\nLocalAddrTaken "local" true;;\n'):
        assert classify_flags(case, meta, flags)["classification"] == "INCONCLUSIVE"

    assert provider.profile_identity({"profile": runner.PROFILE, "accepted": False}) == runner.PROFILE
    assert runner.PROFILE in compat.PINNED_REFINER_SOURCE_SHA256_BY_PROFILE
    assert compat.PINNED_REFINER_SOURCE_SHA256_BY_PROFILE[runner.PROFILE] == compat.PINNED_REFINER_SOURCE_SHA256_BY_PROFILE["experimental-merge-guard-addressability-v1"]
    receiver_run = receiver.run(root / "receiver-controls", SimpleNamespace(profile=runner.PROFILE),
                                {}, None, root / "positive-case", lambda *args: None)
    assert receiver_run["profile"] == runner.PROFILE and receiver_run["cases"]
    assert set(receiver_run["cases"].values()) == {"NOT_RUN"}
    assert provider.profile_identity({"profile": "experimental-merge-guard-addressability-v1", "accepted": False}) == "experimental-merge-guard-addressability-v1"
    for bad_card in (None, {}, {"profile": "unknown-profile", "accepted": False},
                     {"profile": runner.PROFILE, "accepted": True},
                     {"profile": runner.PROFILE, "accepted": None}):
        try:
            provider.profile_identity(bad_card)
        except SystemExit:
            pass
        else:
            raise AssertionError("provider profile gate admitted malformed/old/accepted identity")

    # Exercise the actual inline EMITTERPIN validation block without invoking
    # patch application, cargo, Dune, exporter, verifier, or Cloud.
    profile_script = (HERE.parents[1] / "merge/overnight/guard-ownership/insertion-onecell/build-profile.sh").read_text()
    marker = "<<'EMITTERPIN'\n"
    block = profile_script.split(marker, 1)[1].split("\nEMITTERPIN", 1)[0]
    fake_patch = b"synthetic-emitter-patch"
    patch_path = root / "synthetic.patch"
    patch_path.write_bytes(fake_patch)
    good_profile = {"profile": runner.PROFILE, "accepted": False,
        "ordered_patch_chain": [{"path": "x", "sha256": "0" * 64}] * 15 + [{
            "path": "research/challenge-8/cloud-build/origin-layout/r5-deferred-local-emitter.patch",
            "sha256": runner._sha(fake_patch)}],
        "deferred_local_emitter_patch_sha256": runner._sha(fake_patch)}
    profile_path = root / "profile.json"
    def run_inline(card):
        profile_path.write_text(json.dumps(card))
        return subprocess.run([sys.executable, "-", str(profile_path), str(patch_path)],
            input=block, text=True, capture_output=True)
    assert run_inline(good_profile).returncode == 0
    bad_profiles = [None, {}, {**good_profile, "profile": None},
        {**good_profile, "profile": "experimental-merge-guard-addressability-v1"},
        {**good_profile, "accepted": True},
        {**good_profile, "ordered_patch_chain": good_profile["ordered_patch_chain"][:-1]},
        {**good_profile, "deferred_local_emitter_patch_sha256": "f" * 64}]
    for bad_profile in bad_profiles:
        if bad_profile is None:
            profile_path.write_text("null")
            result = subprocess.run([sys.executable, "-", str(profile_path), str(patch_path)],
                input=block, text=True, capture_output=True)
        else:
            result = run_inline(bad_profile)
        assert result.returncode != 0

    receipt = {"profile": runner.PROFILE, "build_id": "build-r5",
               "proof_sha": "a" * 40, "profile_sha256": "b" * 64,
               "tool_commit": "c" * 40, "verify_expr_sha256": "d" * 64,
               "accepted": False}
    args = SimpleNamespace(profile=runner.PROFILE)
    assert runner._receipt_gate(args, receipt)["build_id"] == "build-r5"
    for bad_args, bad_receipt in (
        (args, None), (args, {**receipt, "profile": None}),
    ):
        try:
            runner._receipt_gate(bad_args, bad_receipt)
        except (TypeError, RuntimeError):
            pass
        else:
            raise AssertionError("R5 identity gate admitted an old, missing, or null profile")
print("R5 emitter synthetic service checks: PASS")

# Exercise the production dispatch expression, so import aliases cannot be
# confused with packaged module filenames. Do not execute hosted main().
import ast
ROOT = HERE.parents[3]
production = ROOT / "research/challenge-8/merge/overnight/guard-ownership/insertion-onecell/prove.py"
tree = ast.parse(production.read_bytes())
assignment = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "control_name" for t in node.targets))
recipe = json.loads((ROOT / "research/challenge-8/cloud-build/recipes/merge.json").read_text())
for active, expected in [("experimental-merge-guard-addressability-v1", "r4-addressability-controls.py"),
                         ("experimental-merge-guard-addressability-emitter-r5-v1", "r5-addressability-controls.py")]:
    namespace = {"args": SimpleNamespace(profile=active)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[assignment], type_ignores=[])), str(production), "exec"), namespace)
    module_path = HERE / namespace["control_name"]
    assert module_path.name == expected and module_path.is_file()
    assert str(module_path.relative_to(ROOT)) in recipe["proof_paths"]
print("Production R4/R5 control dispatch packaging: PASS")
