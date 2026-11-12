"""Read-only source/package checks; never invokes a compiler or verifier."""
import hashlib
import json
from pathlib import Path
import re
import subprocess


D = Path(__file__).resolve().parent
G = D.parents[4]
M = json.loads((D / "TEST-MANIFEST.json").read_text())
I = json.loads((D / "INPUTS.json").read_text())
K = Path(M["clone"])


def git(*args, cwd=K):
    return subprocess.check_output(["git", *args], cwd=cwd)


def check_file(record, root):
    data = (root / record["path"]).read_bytes()
    assert len(data) == record["bytes"], record["path"]
    assert hashlib.sha256(data).hexdigest() == record["sha256"], record["path"]


assert git("rev-parse", "HEAD").decode().strip() == M["candidate_commit"]
assert git("rev-parse", "HEAD^").decode().strip() == M["base_commit"] == M["parent"]
assert git("rev-parse", "HEAD^{tree}").decode().strip() == M["candidate_tree"]
assert git("rev-parse", M["base_commit"] + "^{tree}").decode().strip() == M["base_tree"]
assert not git("status", "--porcelain=v1", "--untracked-files=all").strip()
names = git("diff", "--name-only", M["base_commit"], "HEAD").decode().splitlines()
assert sorted(names) == sorted(x["path"] for x in M["changed_files"])
assert len(names) == 4
assert all(x.startswith("tests/expected/uninit/private-transfer-frame/") for x in names)
assert all(x.startswith("A\t") for x in git("diff", "--name-status", M["base_commit"], "HEAD").decode().splitlines())
patch = git("diff", "--binary", "--full-index", M["base_commit"], "HEAD", "--", "tests/expected/uninit/private-transfer-frame/")
assert patch == (D / "TEST-DELTA.patch").read_bytes()
check_file(M["patch"], D)
git("diff", "--check", M["base_commit"], "HEAD")
git("apply", "--check", str(D / "TEST-DELTA.patch"), cwd=Path(I["seed_read_only"]))
assert git("rev-parse", "HEAD", cwd=Path(I["seed_read_only"])).decode().strip() == M["base_commit"]
assert not git("status", "--porcelain=v1", cwd=Path(I["seed_read_only"])).strip()

for item in M["changed_files"] + I["unchanged_kani_dependencies"]:
    check_file(item, K)
for item in I["references"]:
    check_file(item, G)
check_file(I["std_api_reference"], Path(I["std_api_reference"]["repository"]))
for item in I["formatting"]:
    check_file(item, Path("/"))

for c in M["new_controls"] + M["reused_controls"]:
    check_file(c["source"], K)
    check_file(c["golden"], K)
    source = (K / c["source"]["path"]).read_text()
    assert re.search(r"fn " + re.escape(c["source_root"]) + r"\(", source)
    assert c["outcome"] == "NOT_RUN" and c["actual_emitted_root"] == "UNKNOWN"
    if "expected_failure_site" in c:
        site = c["expected_failure_site"]
        assert source.splitlines()[site["line"] - 1].strip() == site["expression"]
        assert not c["extra_failures_allowed"]
for c in M["new_controls"]:
    source = (K / c["source"]["path"]).read_text()
    assert source.count("#[kani::proof_for_contract(") == 1
    assert "--edition 2021 -D warnings" in source
    assert "-Z uninit-checks -Z function-contracts --output-format=regular" in source
    assert "Copyright Kani Contributors" in source and "SPDX-License-Identifier: Apache-2.0 OR MIT" in source
    assert "#[kani::requires" not in source and "kani::assume(" not in source
    assert "0 failures, 1 total." in (K / c["golden"]["path"]).read_text()
assert M["new_selector_count"] == len(M["new_controls"]) == 2
assert M["new_controls"][0]["source"]["sha256"] == "fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b"
p2 = next(c for c in M["reused_controls"] if c["source_root"] == "postcondition_reads_returned_hole")
assert p2["source"]["sha256"] == "61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759"

mixed = M["mixed_composition"]
repo = Path(mixed["source_repo"])
assert git("rev-parse", mixed["commit"] + "^{tree}", cwd=repo).decode().strip() == mixed["tree"]
assert not (K / "tests/expected/uninit/mixed-promoted-allocations").exists()
paths = git("ls-tree", "-r", "--name-only", mixed["commit"], "--", "tests/expected/uninit/mixed-promoted-allocations", cwd=repo).decode().splitlines()
assert sorted(paths) == sorted(x["path"] for x in mixed["files"])
assert len(paths) == 16
for item in mixed["files"]:
    data = git("show", mixed["commit"] + ":" + item["path"], cwd=repo)
    assert len(data) == item["bytes"] and hashlib.sha256(data).hexdigest() == item["sha256"]
    if "source_root" in item:
        assert "fn " + item["source_root"] + "(" in data.decode()

check_file(M["unit5"]["source"], K)
assert len(M["unit5"]["names"]) == 5
for name in M["unit5"]["names"]:
    assert "fn " + name + "(" in (K / M["unit5"]["source"]["path"]).read_text()
result = dict(candidate=M["candidate_commit"], parent=M["parent"], tree=M["candidate_tree"],
              files=len(names), new_selectors=2, reused_roots=len(M["reused_controls"]),
              external_mixed_files=16, external_mixed_materialized=False,
              exact_patch_and_hashes="PASS", source_root_and_site_checks="PASS",
              existing_source_and_goldens_unchanged="PASS", seed_unchanged="PASS",
              pinned_rustfmt="PASS_PREVIOUS_CHECK_NO_SOURCE_CHANGE",
              compilation="NOT_RUN", macro_expansion="NOT_RUN", solver="NOT_RUN",
              emitted_bindings="UNKNOWN", cloud_usd=0, dispatches=0, proof_credit=0)
print(json.dumps(result, indent=2))
