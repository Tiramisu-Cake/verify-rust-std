"""Static packet/identity checks only; never invokes a compiler or Cloud service."""
import hashlib
import importlib.util
import json
import subprocess
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
LANE = ROOT / "research/challenge-8/kani-k1"
B_HEAD = "c8967c5a44e8f95b19f31761e55313d8488faea5"
LIBRARY = "919cc3e2dc5fb19ea6e7f7be761914b949160a41"
KT2 = "3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c"
PIN = "f046b70644e113be0df9c22c2e6ea44a65a57566"
PATCH = "46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4"
TREE = "d356238999ab436ddc1dd7ffa845b0db214aa53e"
PROTECTED = [".circleci", ".github/workflows", "research/challenge-8/kani-k1/tools",
             "research/challenge-8/kani-k1/gcb", "scripts/run-kani.sh",
             "tool_config/kani-version.toml", "rust-toolchain.toml", ".gitmodules",
             ".cargo", "library/.cargo", "library/Cargo.toml", "library/Cargo.lock"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def read(path):
    return json.loads(path.read_text())


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    checks = {}

    def require(name, condition):
        checks[name] = bool(condition)
        if not condition:
            raise AssertionError(name)

    a_blob = (HERE / "RUN-REQUEST.json").read_bytes()
    a = json.loads(a_blob)
    c = read(LANE / "kani3300/cmp3/RUN-REQUEST.json")
    b_blob = git("show", f"{B_HEAD}:research/challenge-8/kani-k1/RUN-REQUEST.json")
    b = json.loads(b_blob)
    b_dir = LANE / "kani3300/cmp4"
    obs = read(b_dir / "CMP2-OBSERVATIONS.json")
    binding = read(LANE / "kani3300/u4/PATCH-BINDING.json")
    require("root_request_equals_snapshot", (LANE / "RUN-REQUEST.json").read_bytes() == a_blob)
    require("A_equals_original_CMP3_except_request_metadata", {k: v for k, v in a.items() if k not in {"request_id", "purpose"}} == {k: v for k, v in c.items() if k not in {"request_id", "purpose"}})
    require("exact_nine_roots_and_U1_U2", len(a["harnesses"]) == 9 and a["harnesses"][7]["expect"] == "FAILED" and a["harnesses"][7]["expect_check"] == "Reading from an uninitialized" and a["harnesses"][8]["expect"] == "SUCCESS")
    require("B_published_request_equals_preserved_snapshot", b_blob == (b_dir / "cmp2/RUN-REQUEST.json").read_bytes())
    require("A_B_recipe_fields_equal", {k: v for k, v in a.items() if k not in {"request_id", "purpose", "harnesses"}} == {k: v for k, v in b.items() if k not in {"request_id", "purpose", "harnesses"}})
    require("request_kind_and_flags", a["kind"] == "diagnostic" and a["agent"] == "k1-merge" and a["runner"] == "gcb-e2-standard-4" and a["kani_jobs"] == 1 and a["harness_timeout_minutes"] == 3 and a["uninit_checks"] is True and a["controls"] is True and a["inventory"] is False and a["request_id"].startswith("kani3300-t1a-"))
    require("same_library_tree_A_B_planner_reference", all(git("rev-parse", f"{rev}:library").decode().strip() == LIBRARY for rev in ["HEAD", B_HEAD, "2121ff2d08d50d412c834760af925b202a1d8c01"]))
    require("no_working_library_or_lane_diff", git("diff", "HEAD", "--", "library", *PROTECTED) == b"")
    require("KT2_protected_paths_equal_A_and_B", all(git("diff", KT2, rev, "--", *PROTECTED) == b"" for rev in ["HEAD", B_HEAD]))
    require("patch_same_as_B_and_expected", a["kani_patch"] == b["kani_patch"] and sha((ROOT / a["kani_patch"]["path"]).read_bytes()) == PATCH == a["kani_patch"]["sha256"] and (ROOT / a["kani_patch"]["path"]).read_bytes() == git("show", f"{B_HEAD}:{a['kani_patch']['path']}"))
    require("applied_tree_binding_matches_B_report", binding["expected_production_applied_tree"] == TREE == obs["applied_tree_reported"])
    require("pin_and_toolchain", PIN in (ROOT / "tool_config/kani-version.toml").read_text() and 'channel = "nightly-2026-10-23"' in (ROOT / "rust-toolchain.toml").read_text() and obs["kani_pin"] == PIN)
    require("B_observation_request_and_head_bindings", obs["head_sha"] == B_HEAD and obs["request_sha256"] == sha(b_blob) and obs["request_id"] == b["request_id"] and obs["kani_patch_sha256"] == PATCH)

    receipts = []
    index = read(b_dir / "CMP2-EVIDENCE-INDEX.json")
    for entry in index["files"]:
        path = b_dir / entry["path"]
        blob = path.read_bytes()
        require("B_receipt_" + entry["path"], sha(blob) == entry["sha256"] and len(blob) == entry["bytes"] and blob == git("show", f"HEAD:{path.relative_to(ROOT)}"))
        receipts.append({"path": str(path.relative_to(ROOT)), "sha256": sha(blob), "bytes": len(blob)})
    status = read(b_dir / "evidence/d137507f/status.json")
    require("B_cloud_source_binding", status["id"] == obs["build_id"] == index["build_id"] and status["source_sha"] == B_HEAD and status["status"] == obs["cloud_status"] == "SUCCESS" and status["pool"].endswith("/k1-standard4"))
    require("B_three_positives_and_expected_U1", len(obs["roots"]) == 4 and [r["name"] for r in obs["roots"]] == [r["name"] for r in b["harnesses"]] and all(r["status"] == "SUCCESS" and r["checks_failed"] == 0 for r in obs["roots"][:3]) and obs["roots"][3]["status"] == "FAILED" and obs["roots"][3]["checks_failed"] == 1 and obs["roots"][3]["failed_checks"][0]["description"] == "Undefined Behavior: Reading from an uninitialized pointer of type `u8`" and obs["summary_status"] == "COMPLETE" and obs["gate"] is True)
    summary = (b_dir / "evidence/d137507f/summary.md").read_text()
    tooling = (b_dir / "evidence/d137507f/check-tooling.txt").read_text()
    require("B_summary_pin_patch_tree_recipe", all(s in summary for s in [B_HEAD, PIN, sha(b_blob), TREE, PATCH, "per-harness timeout 3 min", "harnesses in parallel 1", "uninit checks on", "controls cfg on"]) and KT2 in tooling and TREE in tooling and "DIFF" not in tooling)

    spec = importlib.util.spec_from_file_location("kani_k1", LANE / "tools/kani_k1.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.validate_request(a, max_total_minutes=720)
    args = "\n".join(module.kani_args(a)) + "\n"
    require("generated_args_equal_original_CMP3_bytes", args == (HERE / "kani.args").read_text() == (LANE / "kani3300/cmp3/kani.args").read_text())
    require("no_trace_emit_or_slice_delta", not any(flag in args for flag in ["--emit", "--trace", "--no-slice-formula"]))
    require("same_runner_and_RUSTFLAGS_as_CMP3_and_B", all((HERE / name).read_bytes() == (LANE / "kani3300/cmp3" / name).read_bytes() == (b_dir / "cmp2" / name).read_bytes() for name in ["runner.txt", "rustflags.txt"]) and (HERE / "rustflags.txt").read_text() == "--cfg kani_smallsort_controls\n")
    reserve = Decimal(9 * 3 + 30) * Decimal("0.0135")
    require("reserve_57_minutes_within_cap", reserve == Decimal("0.7695") and reserve <= Decimal("0.80"))
    comparison = {
        "baseline_usable": "YES, as source-reported bounded diagnostic only",
        "B_build_id": obs["build_id"], "B_head": B_HEAD,
        "library_tree_A_and_B": LIBRARY, "kani_pin": PIN,
        "toolchain": "nightly-2026-10-23", "tooling_base": KT2,
        "patch_sha256": PATCH, "applied_tree_B_reported_and_A_expected": TREE,
        "B_request_sha256": sha(b_blob), "A_request_sha256": sha(a_blob),
        "recipe": "diagnostic, uninit/controls on, inventory off, standard4/jobs1, 3m; unchanged KT2 runner and RUSTFLAGS",
        "differences": ["Original nine CMP3 selectors/expectations instead of four CMP4 selectors; request_id and purpose"],
        "B_roots": obs["roots"], "receipts": receipts,
        "limitations": ["Preserved bounded receipts, checked against committed bytes and recorded hashes; no new Cloud query performed.", "B native report unavailable; Brief HTTP404. Actual argv and MIR remain UNKNOWN.", "A actual applied tree/argv/results NOT_RUN; verify terminal bindings before classification.", "No same-library observation yet; selected root order does not establish codegen order.", "No independent B1/B2 proof credit; no mechanism or deterministic root-set-only causality established."],
        "proof_credit": "NONE",
    }
    (HERE / "BASELINE-COMPARISON.json").write_text(json.dumps(comparison, indent=2) + "\n")
    (HERE / "static-check.json").write_text(json.dumps({"status": "PASS", "assurance": "static packet/identity check only", "checks": checks, "request_sha256": sha(a_blob), "library_tree": LIBRARY, "planned_reserve_usd": str(reserve), "cap_usd": "0.80", "attempts_allowed": 1, "attempts_used": 0, "cloud": "NOT_RUN", "proof_credit": "NONE"}, indent=2) + "\n")
    print(f"PASS: {len(checks)} static checks; B usable as source-reported baseline; A NOT_RUN")


if __name__ == "__main__":
    main()
