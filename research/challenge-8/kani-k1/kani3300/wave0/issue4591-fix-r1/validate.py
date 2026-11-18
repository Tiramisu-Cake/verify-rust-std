#!/usr/bin/env python3
"""Validate the static package and synthetic publication metadata without a compiler."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import yaml


PKG = Path(__file__).resolve().parent
PINS = json.loads((PKG / "SOURCE-PINS.json").read_text())
SRC = Path(PINS["source_worktree"])
BASE = PINS["main"]["sha"]
HEAD = PINS["candidate"]["sha"]
TREE = PINS["candidate"]["tree"]
CHECKS = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    CHECKS.append(name)


def git(*args, env=None):
    return subprocess.check_output(["git", "-C", str(SRC), *args], env=env).decode().strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replay(patches):
    with tempfile.TemporaryDirectory(prefix="issue4591-index-") as temp:
        env = dict(os.environ, GIT_INDEX_FILE=str(Path(temp) / "index"))
        git("read-tree", BASE, env=env)
        for name in patches:
            git("apply", "--cached", "--check", str(PKG / name), env=env)
            git("apply", "--cached", str(PKG / name), env=env)
        return git("write-tree", env=env)


def harnesses(path):
    return [(name, attrs) for attrs, name in re.findall(
        r"((?:#\[kani::[^\n]+\]\n)+)fn (\w+)\(", path.read_text())
        if "#[kani::proof]" in attrs or "#[kani::proof_for_contract(" in attrs]


def main():
    check("source_head", git("rev-parse", "HEAD") == HEAD)
    check("source_clean", git("status", "--porcelain") == "")
    check("source_branch", git("branch", "--show-current") == PINS["source_branch"])
    check("candidate_tree", git("rev-parse", f"{HEAD}^{{tree}}") == TREE)
    check("single_stock_main_parent", git("show", "-s", "--format=%P", HEAD) == BASE)
    check("one_commit_from_stock_main", git("rev-list", f"{BASE}..{HEAD}").split() == [HEAD])
    check("main_tree_parent", git("rev-parse", f"{BASE}^{{tree}}") == PINS["main"]["tree"]
          and git("rev-parse", f"{BASE}^") == PINS["main"]["parent"])
    check("local_skipped_candidate", "[skip ci]" in git("show", "-s", "--format=%B", HEAD))
    check("author", git("show", "-s", "--format=%an <%ae>", HEAD) == "Tiramisu-Cake <igkharin@gmail.com>")
    changed = git("diff", "--name-only", BASE, HEAD).splitlines()
    check("exact_source_and_test_scope", changed == PINS["changed_paths"]
          and len(PINS["source_paths"]) == 3 and len(PINS["test_paths"]) == 8)
    frozen = PINS["frozen_inputs"]
    check("repair_sibling_of_frozen_candidate", frozen["parent"] == BASE
          and git("show", "-s", "--format=%P", frozen["source"]) == BASE
          and git("rev-parse", frozen["source"] + "^{tree}") == frozen["tree"]
          and frozen["source"] != HEAD)
    delta = git("diff", "--name-only", frozen["source"], HEAD).splitlines()
    check("repair_only_three_fixture_oracle_paths", delta == PINS["repair_delta_paths"]
          == ["tests/expected/function-contract/ordinary_stub_fail.expected",
              "tests/expected/function-contract/ordinary_stub_fail.rs",
              "tests/kani/FunctionContracts/ordinary_stub.rs"])
    for path in PINS["source_paths"]:
        check("reviewed_compiler_bytes:" + path,
              git("rev-parse", f"{frozen['source']}:{path}")
              == git("rev-parse", f"{HEAD}:{path}"))
    check("entire_compiler_tree_reviewed_unchanged",
          git("rev-parse", frozen["source"] + ":kani-compiler")
          == git("rev-parse", HEAD + ":kani-compiler"))
    check("frozen_compiler_patch_bytes", hashlib.sha256(subprocess.check_output(
          ["git", "-C", str(PKG), "show", frozen["g0"]
           + ":research/challenge-8/kani-k1/kani3300/wave0/issue4591-fix/fix.patch"])).hexdigest()
          == digest(PKG / "fix.patch"))

    check("whitespace", git("diff", "--check", BASE, HEAD) == "")
    for path, pin in PINS["changed_files"].items():
        check(f"file:{path}", digest(SRC / path) == pin["sha256"]
              and git("rev-parse", f"{HEAD}:{path}") == pin["blob"])
    for path, tree in PINS["protected_git_trees"].items():
        check(f"protected_tree:{path}", git("rev-parse", f"{BASE}:{path}") == tree
              and git("rev-parse", f"{HEAD}:{path}") == tree)
    for path, sha in PINS["protected_files_sha256"].items():
        check(f"protected_file:{path}", digest(SRC / path) == sha
              and git("diff", BASE, HEAD, "--", path) == "")
    workflow_paths = sorted(str(p.relative_to(SRC)) for p in (SRC / ".github/workflows").glob("*.yml"))
    check("exact_workflow_set", workflow_paths == sorted(PINS["all_workflows_sha256"]))
    inventory = json.loads((PKG / "WORKFLOW-INVENTORY.json").read_text())
    ci = json.loads((PKG / "CI-REQUEST.json").read_text())
    for path, sha in PINS["all_workflows_sha256"].items():
        check(f"workflow_bytes:{path}", digest(SRC / path) == sha)
        workflow = yaml.load((SRC / path).read_text(), Loader=yaml.BaseLoader)
        recorded = inventory["workflows"][Path(path).name]
        check(f"workflow_inventory:{path}", all(recorded[field] == workflow.get(field)
              for field in ("on", "jobs", "concurrency", "name")))
    check("all_push_jobs_exact", all(ci["native_jobs"][name] == inventory["workflows"][name]["jobs"]
          for name in ci["workflow_files"]))
    check("native_push_workflows", ci["workflow_files"] == ["kani.yml", "format-check.yml", "deny.yml"])
    check("five_regression_os_entries", ci["native_jobs"]["kani.yml"]["regression"]["strategy"]["matrix"]["os"]
          == ["macos-15-intel", "ubuntu-22.04", "ubuntu-24.04", "macos-15", "ubuntu-24.04-arm"])
    check("no_dispatch_or_publication", not ci["authorization"]["dispatch"]
          and not ci["authorization"]["publication"] and not any(ci["actions"].values())
          and ci["launch_owner"] == "USERCOORDINATOR_ONLY" and ci["pr_publication_owner"] == "OWNER_ONLY"
          and "SEPARATE_USERCOORDINATOR_FULL_STANDARD_PUSH_CI_COMMAND" in ci["authorization"]["gates"])
    check("future_head_not_created", PINS["future_final_head"]["sha"] == "NOT_CREATED"
          and ci["future_final_head"] == PINS["future_final_head"])
    for name, sha in PINS["patches"].items():
        check(f"patch_digest:{name}", digest(PKG / name) == sha)
    check("split_patch_replay_exact_tree", replay(["regression-main.patch", "fix.patch"]) == TREE)
    check("whole_patch_replay_exact_tree", replay(["full-main.patch"]) == TREE)

    snapshot = json.loads((PKG / "ISSUE-4591.json").read_text())
    issue_code = snapshot["issue"]["issue"]["body"].split("```rust\n", 1)[1].split("```", 1)[0].strip()
    issue_test = (SRC / "tests/expected/function-contract/ordinary_stub_issue_4591.rs").read_text()
    check("verbatim_issue_rust_code", issue_test[issue_test.index("#[kani::ensures"):].strip() == issue_code)
    check("issue_and_maintainer_input", snapshot["issue"]["issue"]["issue_number"] == 4591
          and any(c["id"] == 4946988101 for c in snapshot["comments"]["comments"]))
    for path in PINS["test_paths"]:
        if path.endswith(".rs"):
            check(f"license:{path}", (SRC / path).read_text().startswith(
                "// Copyright Kani Contributors\n// SPDX-License-Identifier: Apache-2.0 OR MIT\n"))
    positive = harnesses(SRC / "tests/kani/FunctionContracts/ordinary_stub.rs")
    negative = harnesses(SRC / "tests/expected/function-contract/ordinary_stub_fail.rs")
    no_assert = harnesses(SRC / "tests/kani/FunctionContracts/ordinary_stub_no_assert.rs")
    check("explicit_harness_inventory", len(positive) == 19 and len(negative) == 13 and len(no_assert) == 4)
    oracle = json.loads((PKG / "REGRESSION-ORACLE.json").read_text())
    expected_harnesses = {(path, name) for path in PINS["test_paths"] if path.endswith(".rs")
                          for name, _ in harnesses(SRC / path)}
    check("oracle_complete_and_not_run", oracle["source_head"] == HEAD
          and oracle["source_tree"] == TREE and oracle["expected_only"] is True
          and {(row["path"], row["harness"]) for row in oracle["harnesses"]} == expected_harnesses
          and all(row["main_new_native"] == row["fixed_new_native"] == "NOT_RUN"
                  for row in oracle["harnesses"]))
    intake = oracle["original_intake"]
    intake_dir = PKG.parent / "stub-contract-confirm-intake/run-44380273557"
    check("historical_classification_retained", intake["retained_producer_classification"]
          == intake["retained_owner_policy_classification"] == "INCONCLUSIVE"
          and intake["new_candidate_credit"] is False)
    for path, sha in intake["immutable_read_inputs"].items():
        check(f"historical_input_unchanged:{path}", digest(intake_dir / path) == sha)
    checkpoint = json.loads((PKG / "CHECKPOINT.json").read_text())
    check("ready_review_gate_and_ci_binding", checkpoint["status"] == "READY_FOR_SAME11_DELTA_REVIEW"
          and checkpoint["source_head"] == HEAD and checkpoint["source_tree"] == TREE
          and checkpoint["source_parent"] == BASE
          and checkpoint["ci_request_sha256"] == digest(PKG / "CI-REQUEST.json")
          and checkpoint["independent11"] == "PENDING_SAME11_DELTA_NOT_AUTHORED_BY_W15"
          and checkpoint["root_go"] == "BLOCKED_UPSTREAM_MAIN_DRIFT_PENDING_SAME11_DELTA_AND_ROOT_DECISION")
    check("only_expected_panic_in_no_assert", [name for name, attrs in no_assert if "#[kani::should_panic]" in attrs]
          == ["replacement_provider"])
    expected = (SRC / "tests/expected/function-contract/ordinary_stub_fail.expected").read_text()
    failed = set(re.findall(r"^Verification failed for - (\w+)$", expected, re.MULTILINE))
    check("negative_named_semantic_results", failed == {name for name, _ in negative}
          - {"provider", "requires_only_provider"}
          and "Complete - 2 successfully verified harnesses, 11 failures, 13 total." in expected)
    check("oracle_attributes_match_every_harness", all(
          row["attributes"] == next(attrs.splitlines() for name, attrs
                                    in harnesses(SRC / row["path"]) if name == row["harness"])
          for row in oracle["harnesses"]))
    helper_spec = importlib.util.spec_from_file_location("pfc_fixture_check", PKG / "pfc_fixture_check.py")
    helper = importlib.util.module_from_spec(helper_spec)
    helper_spec.loader.exec_module(helper)
    texts = {path: (SRC / path).read_text() for path in PINS["test_paths"] if path.endswith(".rs")}
    frozen_texts = {path: subprocess.check_output(
        ["git", "-C", str(SRC), "show", f"{frozen['source']}:{path}"], text=True) for path in texts}
    pfc_report = helper.regression_checks(texts, frozen_texts)
    for name in pfc_report["checks"]:
        check("pfc_regression:" + name, True)
    check("unique_discriminating_property_oracle",
          expected.count('- Description: "|result| *result == 0"') == 1
          and sum(text.count("#[kani::ensures(|result| *result == 0)]") for text in texts.values()) == 1)
    frozen_expected = subprocess.check_output(["git", "-C", str(SRC), "show",
        f"{frozen['source']}:tests/expected/function-contract/ordinary_stub_fail.expected"], text=True)
    addition = 'assertion\\\n- Status: FAILURE\\\n- Description: "|result| *result == 0"\n\n'
    check("all_old_negative_oracles_preserved", expected.replace(addition, "") == frozen_expected)
    ci_pins = json.loads((PKG / "CI-REQUEST.json").read_text())
    prov = json.loads((PKG / "PROVENANCE.json").read_text())
    inventory = json.loads((PKG / "WORKFLOW-INVENTORY.json").read_text())
    check("rebound_source_ci_provenance_inventory",
          ci_pins["candidate"] == PINS["candidate"] == prov["source"]
          and ci_pins["main"] == PINS["main"] == prov["base"]
          and inventory["candidate_sha"] == HEAD and checkpoint["patches"] == PINS["patches"]
          and prov["task_g0"] == PINS["task"]["g0_sha"] == checkpoint["g0_task_commit"])

    issue_expected = (SRC / "tests/expected/function-contract/ordinary_stub_issue_4591.expected").read_text()
    check("issue_overflow_oracle", 'caller.assertion\\\n- Status: FAILURE\\\n- Description: "attempt to add with overflow"'
          in issue_expected and "VERIFICATION:- FAILED" in issue_expected)
    check("bounded_arithmetic_oracle", all(x + 2 <= 255 and x + 2 != x + 1 for x in range(8))
          and 8 + 2 == 10 and not 8 < 8 and (2**31 - 1) + 1 > 2**31 - 1)

    module = (SRC / "kani-compiler/src/kani_middle/transform/mod.rs").read_text()
    stubs = (SRC / "kani-compiler/src/kani_middle/transform/stubs.rs").read_text()
    contracts = (SRC / "kani-compiler/src/kani_middle/transform/contracts.rs").read_text()
    check("source_report_after_validation", "if let Some(body) = FnStubValidator::validate" in stubs
          and re.search(r"if let Some\(body\) = FnStubValidator::validate[^\n]+\{\n"
                        r"\s+self.body_source = Some\(new_instance\);\n\s+return \(true, body\);", stubs) is not None)
    check("state_reset_and_consumed", "self.body_source = None;" in stubs
          and "self.body_source.take()" in stubs and "let mut body_source = instance;" in module)
    check("passes_retained", "self.stub_passes.iter_mut().chain(self.inst_passes.iter_mut())" in module
          and "let transform_instance = pass.transform_instance(instance, body_source);" in module)
    check("explicit_original_contract_modes_retained", "self.check_fn == Some(*def) || self.replace_fns.contains(def)"
          in contracts and "body_source\n        }" in contracts)
    original_contracts = subprocess.check_output(["git", "-C", str(SRC), "show", f"{BASE}:kani-compiler/src/kani_middle/transform/contracts.rs"]).decode()
    check("closure_search_and_modes_byte_unchanged", contracts[contracts.index("    /// Select any unused closure"):]
          == original_contracts[original_contracts.index("    /// Select any unused closure"):]
          and contracts[contracts.index("    fn contract_mode("):contracts.index("    /// Detect the `stub_verified`")]
          == original_contracts[original_contracts.index("    fn contract_mode("):original_contracts.index("    /// Detect the `stub_verified`")])

    spec = importlib.util.spec_from_file_location("publication_gate", PKG / "check_push_head.py")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    final = "1" * 40
    commits = [{"sha": final, "message": "Support ordinary stubs of contracted functions"}]
    check("mock_final_sibling_accepted", not gate.check_metadata(PINS, final, TREE, [BASE], commits))
    for label, head, tree, parents, entries in [
        ("candidate", HEAD, TREE, [BASE], [{"sha": HEAD, "message": "[skip ci]"}]),
        ("main", BASE, TREE, [BASE], [{"sha": BASE, "message": "main"}]),
        ("short_sha", final[:12], TREE, [BASE], commits),
        ("tree_drift", final, "2" * 40, [BASE], commits),
        ("merge_parent", final, TREE, [BASE, HEAD], commits),
        ("candidate_parent", final, TREE, [HEAD], commits),
        ("empty_range", final, TREE, [BASE], []),
        ("skipped_ancestor", final, TREE, [BASE], commits + [{"sha": HEAD, "message": "[skip ci]"}]),
    ]:
        check(f"mock_reject:{label}", bool(gate.check_metadata(PINS, head, tree, parents, entries)))
    for directive in ("[skip ci]", "[ci skip]", "[no ci]", "[skip actions]", "[actions skip]", "skip-checks: true"):
        check(f"mock_reject:{directive}", bool(gate.check_metadata(PINS, final, TREE, [BASE],
              [{"sha": final, "message": "Support ordinary stubs\n\n" + directive}])))
    for sha, expected_code in ((HEAD, 1), (BASE, 1), (HEAD[:12], 2)):
        result = subprocess.run([sys.executable, "-B", str(PKG / "check_push_head.py"), str(SRC), sha],
                                capture_output=True, text=True)
        check(f"gate_cli_reject:{sha}", result.returncode == expected_code)

    main_check = json.loads((PKG / "MAIN-CHECK.json").read_text())
    check("upstream_recheck_binding_and_explicit_drift_gate",
          main_check["expected_main"] == BASE and main_check["drift"] is True
          and main_check["observed_main"] == ci["main_drift"]["observed"]
          == checkpoint["open"][0]["observed"]
          and main_check["raw_reference_line"] == main_check["observed_main"] + "\trefs/heads/main"
          and ci["main_drift"]["resolution"] == "PENDING_ROOT_COORDINATOR"
          and "ROOT_COORDINATOR_UPSTREAM_MAIN_DRIFT_DECISION" in ci["authorization"]["gates"])
    for commit, directory in ((frozen["g0"], "issue4591-fix"),
                              (frozen["review"], "issue4591-fix-review-w11")):
        prefix = "research/challenge-8/kani-k1/kani3300/wave0/" + directory
        repo = Path(subprocess.check_output(["git", "-C", str(PKG), "rev-parse", "--show-toplevel"], text=True).strip())
        listing = subprocess.check_output(["git", "-C", str(repo), "ls-tree", "-r", "--name-only",
                                           commit, "--", prefix], text=True).splitlines()
        check("immutable_input_package:" + directory, bool(listing) and all(
            (repo / path).read_bytes() == subprocess.check_output(
                ["git", "-C", str(PKG), "show", commit + ":" + path]) for path in listing))

    manifest = PKG / "MANIFEST.json"
    if manifest.exists():
        records = json.loads(manifest.read_text())["files"]
        check("manifest_file_set", sorted(records) == sorted(p.name for p in PKG.iterdir()
              if p.is_file() and p.name != "MANIFEST.json"))
        for name, record in records.items():
            check(f"manifest:{name}", digest(PKG / name) == record["sha256"]
                  and (PKG / name).stat().st_size == record["bytes"])
    print(json.dumps({"status": "STATIC_AND_MOCK_PASS", "checks": CHECKS,
                      "source_head": HEAD, "source_tree": TREE,
                      "native_main": "NOT_RUN", "native_fixed": "NOT_RUN",
                      "compiler": "NOT_RUN", "fullrunner": "NOT_RUN", "ci": "NOT_RUN",
                      "independent_review": "PENDING_SAME11_DELTA",
                      "pfc_regression": pfc_report,
                      "scope": "Git/hash/patch/fixture checks and synthetic gate metadata; no typechecking or formal proof"},
                     indent=2))


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    main()
