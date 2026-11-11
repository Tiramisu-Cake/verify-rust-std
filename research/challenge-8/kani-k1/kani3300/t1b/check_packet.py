"""Static Git/request checks only. Never starts a compiler, verifier or Cloud tool."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LANE = ROOT / "research/challenge-8/kani-k1"
KANI = Path("/root/kani-fix-3300-t1")
BASE = "3a780c05130440340197e98eda602ee705e80d8e"
KT2 = "3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c"
CMP2 = "b1f0105c0390fb55081e3d186fa286d23867b585"
PIN = "f046b70644e113be0df9c22c2e6ea44a65a57566"
LIBRARY = "919cc3e2dc5fb19ea6e7f7be761914b949160a41"
PRODUCTION_TREE = "d356238999ab436ddc1dd7ffa845b0db214aa53e"
PRODUCTION_SHA = "46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(tree, *args, data=None, env=None):
    return subprocess.check_output(["git", "-C", str(tree), *args], input=data, env=env)


def read(path):
    return json.loads(path.read_text())


def main():
    checks = {}

    def require(name, value):
        checks[name] = bool(value)
        if not value:
            raise AssertionError(name)

    binding = read(HERE / "PATCH-BINDING.json")
    production = LANE / "kani3300/u4/kani-uninit.patch"
    diag = (HERE / "kani-diagnostic.patch").read_bytes()
    combined = (HERE / "kani-combined.patch").read_bytes()
    require("production_patch_unchanged", sha(production.read_bytes()) == PRODUCTION_SHA
            and production.read_bytes() == git(ROOT, "show", f"{BASE}:{production.relative_to(ROOT)}"))
    require("library_unchanged", git(ROOT, "rev-parse", "HEAD:library").decode().strip() == LIBRARY
            and not git(ROOT, "diff", "HEAD", "--", "library"))
    require("fixture_sha256", sha((ROOT / "library/core/src/slice/sort/shared/smallsort/verify/uninit_probe.rs").read_bytes())
            == "bd6d51c7ad634644d5e8fc16b539cd84b2eedb6101d52692c4d7d0fb3545e8a6")
    require("recipe_and_pins_unchanged", not git(ROOT, "diff", KT2, "--", "scripts/run-kani.sh",
            "tool_config/kani-version.toml", "rust-toolchain.toml", "research/challenge-8/kani-k1/gcb"))
    require("kani_branch_and_clean", git(KANI, "branch", "--show-current").decode().strip() == "diag/kani-3300-t1"
            and not git(KANI, "status", "--porcelain"))
    require("diagnostic_parent_cmp2", git(KANI, "rev-parse", binding["diagnostic_commit"] + "^").decode().strip() == CMP2)
    require("diagnostic_patch_exact_commit", diag == git(KANI, "diff", "--binary", CMP2, binding["diagnostic_commit"]))
    require("patch_hashes", sha(diag) == binding["diagnostic_patch_sha256"]
            and sha(combined) == binding["combined_patch_sha256"])
    # Private Git index only: no checkout preparation, extraction, compilation or verifier.
    with tempfile.TemporaryDirectory(prefix="kani3300-t1b-index-") as tmp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / "index"))
        git(KANI, "read-tree", PIN, env=env)
        git(KANI, "apply", "--cached", "-", data=production.read_bytes(), env=env)
        require("production_applied_tree", git(KANI, "write-tree", env=env).decode().strip() == PRODUCTION_TREE)
        git(KANI, "apply", "--cached", "-", data=diag, env=env)
        applied = git(KANI, "write-tree", env=env).decode().strip()
        require("combined_applied_tree", applied == binding["expected_applied_tree"])
        require("combined_patch_exact_static_tree", combined == git(KANI, "diff", "--cached", "--binary", PIN, env=env))
        git(KANI, "apply", "--cached", "--reverse", "-", data=diag, env=env)
        require("reversing_diagnostic_restores_cmp2_tree", git(KANI, "write-tree", env=env).decode().strip() == PRODUCTION_TREE)
    module_spec = importlib.util.spec_from_file_location("kani_k1", LANE / "tools/kani_k1.py")
    k = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(k)
    a = read(HERE / "RUN-REQUEST.json")
    b = read(HERE / "RUN-REQUEST-B.json")
    original_a = read(LANE / "kani3300/cmp3/RUN-REQUEST.json")
    original_b = read(LANE / "kani3300/cmp4/cmp2/RUN-REQUEST.json")
    for label, request, original in [("A", a, original_a), ("B", b, original_b)]:
        k.validate_request(request, max_total_minutes=720)
        require(label + "_roots_expectations_unchanged", request["harnesses"] == original["harnesses"])
        require(label + "_recipe_unchanged", all(request.get(key) == original.get(key) for key in
                ["schema", "kind", "runner", "harness_timeout_minutes", "kani_jobs", "controls", "uninit_checks", "inventory"]))
        args = "\n".join(k.kani_args(request)) + "\n"
        require(label + "_argv_unchanged", args == "\n".join(k.kani_args(original)) + "\n")
        require(label + "_no_runtime_trace_flags", not any(flag in args for flag in
                ["--cbmc-args", "--trace", "--no-slice-formula", "--keep-temps"]))
        require(label + "_combined_patch_bound", request["kani_patch"]["sha256"] == sha(combined)
                and (ROOT / request["kani_patch"]["path"]).read_bytes() == combined)
        (HERE / ("kani-" + label + ".args")).write_text(args)
    require("same_diagnostic_recipe_A_B", a["diagnostic_trace"] == b["diagnostic_trace"])
    require("request_IDs", a["request_id"].startswith("kani3300-t1b-a-") and b["request_id"].startswith("kani3300-t1b-b-"))
    require("9_and_4_roots", len(a["harnesses"]) == 9 and len(b["harnesses"]) == 4)
    tooling = read(HERE / "TOOLING-BINDING.json")
    files = read(HERE / "TOOLING-FILES.json")
    require("tooling_files_exact", all(sha((ROOT / name).read_bytes()) == digest for name, digest in files.items()))
    require("tooling_tree_exact", git(ROOT, "rev-parse", tooling["commit"] + ":research/challenge-8/kani-k1/tools").decode().strip() == tooling["tree"]
            and not git(ROOT, "diff", tooling["commit"], "--", "research/challenge-8/kani-k1/tools"))
    require("tooling_extension_exact", (HERE / "tooling-extension.patch").read_bytes() == git(ROOT, "diff", "--binary", KT2, tooling["commit"], "--", "research/challenge-8/kani-k1/tools")
            and sha((HERE / "tooling-extension.patch").read_bytes()) == tooling["extension_patch_sha256"])
    require("recipe_hashes_exact", all(sha((ROOT / name).read_bytes()) == digest for name, digest in tooling["recipe_files"].items()))
    report = {"status": "PASS", "checks": checks, "library_tree": LIBRARY,
              "diagnostic_commit": binding["diagnostic_commit"], "expected_applied_tree": applied,
              "request_A_sha256": sha((HERE / "RUN-REQUEST.json").read_bytes()),
              "request_B_sha256": sha((HERE / "RUN-REQUEST-B.json").read_bytes()),
              "A_envelope_minutes": 57, "A_planned_reserve_usd": "0.7695", "A_cap_usd": "0.80",
              "B_envelope_minutes": 42, "B_planned_reserve_usd": "0.5670", "B_separate_GO_required": True,
              "cloud": "NOT_RUN", "compilation": "NOT_RUN", "proof_credit": "NONE"}
    (HERE / "STATIC-CHECK.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(checks)} static checks; no compiler or Cloud operation")


if __name__ == "__main__":
    main()
