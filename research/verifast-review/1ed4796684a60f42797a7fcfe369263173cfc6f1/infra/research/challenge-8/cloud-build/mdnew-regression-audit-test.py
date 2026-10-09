"""Synthetic controls for the regression evidence classifier; no verifier/compiler."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

MODULE = Path(__file__).with_name("mdnew-regression-audit.py")
spec = importlib.util.spec_from_file_location("mdnew_regression_audit", MODULE)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


with tempfile.TemporaryDirectory(prefix="mdnew-regression-audit-") as temp:
    root = Path(temp)
    tool = root / "candidate"
    all_logs = root / "evidence/allprooflogs"
    tool.mkdir(parents=True)
    subprocess.run(["git", "init", "--quiet", str(tool)], check=True)
    subprocess.run(["git", "-C", str(tool), "config", "user.name", "Fixture"], check=True)
    subprocess.run(["git", "-C", str(tool), "config", "user.email", "fixture@example.invalid"], check=True)

    local_cases = {}
    for name, (relative, _, _, options) in m.CASES.items():
        content = f"// synthetic source for {name}\n".encode()
        source = tool / "tests/rust" / relative
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(content)
        local_cases[name] = (relative, hashlib.sha256(content).hexdigest(), options)
    subprocess.run(["git", "-C", str(tool), "add", "tests/rust"], check=True)
    subprocess.run(["git", "-C", str(tool), "commit", "--quiet", "-m", "fixture"], check=True)
    m.CANDIDATE = subprocess.check_output(["git", "-C", str(tool), "rev-parse", "HEAD"], text=True).strip()
    m.TREE = subprocess.check_output(["git", "-C", str(tool), "rev-parse", "HEAD^{tree}"], text=True).strip()
    m.CASES = {
        name: (relative,
               subprocess.check_output(["git", "-C", str(tool), "rev-parse",
                                        f"{m.CANDIDATE}:tests/rust/{relative}"], text=True).strip(),
               source_sha, options)
        for name, (relative, source_sha, options) in local_cases.items()
    }
    m.BASE = "b" * 40
    bundle = b"synthetic committed input bundle"
    m.BUNDLE = hashlib.sha256(bundle).hexdigest()
    m.STOCK_ARCHIVE = "1" * 64
    m.DEPS_ARCHIVE = "2" * 64
    m.RUSTC = "3" * 40
    manifest_bytes = json.dumps({"candidate_commit": m.CANDIDATE, "candidate_tree": m.TREE,
                                 "candidate_ref": m.REF, "bundle_sha256": m.BUNDLE}).encode() + b"\n"
    manifest_path = all_logs / "tool-input/manifest"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(manifest_bytes)
    (manifest_path.parent / "bundle").write_bytes(bundle)

    infra_sha = "a" * 40
    proof_sha = infra_sha
    proof_tree = "4" * 40
    infra_tree = "5" * 40
    cert = {"lane": "verifast-mdnew-regressions", "archive_sha256": "6" * 64,
            "proof": {"commit": proof_sha, "head": proof_sha, "root_tree": proof_tree,
                      "restored_paths": [
                          {"path": f"research/challenge-8/verifast-input/{m.CANDIDATE}/bundle",
                           "sha256": m.BUNDLE},
                          {"path": f"research/challenge-8/verifast-input/{m.CANDIDATE}/manifest",
                           "sha256": hashlib.sha256(manifest_bytes).hexdigest()}]},
            "infra": {"commit": infra_sha, "head": infra_sha, "root_tree": infra_tree,
                      "restored_paths": []}}
    infra_root = Path(__file__).resolve().parents[3]
    for relative, path in (
        ("research/challenge-8/cloud-build/run-verifast-mdnew-cfg.sh",
         infra_root / "research/challenge-8/cloud-build/run-verifast-mdnew-cfg.sh"),
        ("research/challenge-8/cloud-build/mdnew-regression-audit.py", MODULE),
        ("research/challenge-8/cloud-build/recipes/verifast-mdnew-regressions.json",
         infra_root / "research/challenge-8/cloud-build/recipes/verifast-mdnew-regressions.json"),
    ):
        cert["infra"]["restored_paths"].append(
            {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    write_json(all_logs.parent / "source-input-certificate.json", cert)
    write_json(all_logs / "identities.json", {"infra_sha": infra_sha, "proof_sha": proof_sha,
                                                "infra_tree": infra_tree, "proof_tree": proof_tree,
                                                "source_input_archive_sha256": cert["archive_sha256"]})
    write_json(all_logs / "restore-receipt.json", {
        "classification": "RESTORED_GIT_INPUT", "base_commit": m.BASE,
        "candidate_commit": m.CANDIDATE, "candidate_ref": m.REF, "candidate_tree": m.TREE,
        "bundle_sha256": m.BUNDLE,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "proof_sha": proof_sha, "infra_sha": infra_sha,
        "git_identity_preserved": True})
    hashes = {"baseline": "7" * 64, "candidate": "8" * 64}
    runtime = {"baseline_source_sha": m.BASE, "candidate_source_sha": m.CANDIDATE,
               "candidate_tree": m.TREE, "stock_distribution_sha256": m.STOCK_ARCHIVE,
               "vfdeps_archive_sha256": m.DEPS_ARCHIVE,
               "rustc_verbose": f"commit-hash: {m.RUSTC}",
               "console_binary_sha256": hashes,
               "components": {name: {"source_file_count": 1,
                                      "source_files_sha256": "a" * 64}
                              for name in ("src/rust_frontend/vf_mir_exporter",
                                           "src/rust_frontend/vf_mir_decoder",
                                           "src/refinement_checker")},
               "specification_inventory": {"baseline": {"rust/std/lib.rsspec": "b" * 64},
                                           "candidate": {"rust/std/lib.rsspec": "b" * 64}},
               "stock_specification_inventory": {"rust/std/lib.rsspec": "b" * 64},
               "pinned_stock_binaries": {name: {"sha256": "9" * 64,
                                                   "baseline_equal": True,
                                                   "candidate_equal": True}
                                           for name in ("vf-rust-mir-exporter", "refinement-checker",
                                                        "vf-cxx-ast-exporter", "libz3.so",
                                                        "rust/std/lib.rsspec")}}
    write_json(all_logs / "runtime-components.json", runtime)

    results = []
    for name, (relative, source_sha, options) in local_cases.items():
        source = tool / "tests/rust" / relative
        blob = subprocess.check_output(["git", "-C", str(tool), "rev-parse",
                                        f"{m.CANDIDATE}:tests/rust/{relative}"], text=True).strip()
        stdout = all_logs / "regressions" / f"{name}.stdout.log"
        stdout.parent.mkdir(parents=True, exist_ok=True)
        stdout.write_text("0 errors found (3 statements verified)\n")
        files = {
            "stdout": stdout,
            "stderr": all_logs / f"mdnew-regression-{name}-stderr.log",
            "resources": all_logs / f"mdnew-regression-{name}-resources.txt",
            "exit_status_file": all_logs / f"mdnew-regression-{name}-exit-code.txt",
        }
        files["stderr"].write_text("")
        files["resources"].write_text("Elapsed time: 1s\nExit status: 0\n")
        files["exit_status_file"].write_text("0\n")
        results.append({"name": name, "path": relative, "source_sha256": source_sha,
                        "git_blob": blob, "options": options, "exit_status": 0,
                        **{key: {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                           for key, path in files.items()}})
    write_json(all_logs / "regressions/manifest.json", {
        "schema": "verifast-mdnew-regressions-v1", "infra_sha": infra_sha,
        "proof_sha": proof_sha, "candidate_commit": m.CANDIDATE,
        "candidate_tree": m.TREE, "results": results})
    result = m.audit(tool, all_logs)
    assert result["classification"] == "UPSTREAM_TARGETED_REGRESSIONS_PASS"
    assert len(result["completed_regressions"]) == 5

    results[0]["exit_status"] = 124
    (all_logs / "mdnew-regression-generic_pair-exit-code.txt").write_text("124\n")
    results[0]["exit_status_file"]["sha256"] = hashlib.sha256(
        (all_logs / "mdnew-regression-generic_pair-exit-code.txt").read_bytes()).hexdigest()
    write_json(all_logs / "regressions/manifest.json", {
        "schema": "verifast-mdnew-regressions-v1", "infra_sha": infra_sha,
        "proof_sha": proof_sha, "candidate_commit": m.CANDIDATE,
        "candidate_tree": m.TREE, "results": results})
    try:
        m.audit(tool, all_logs)
    except m.AuditFailure as ex:
        assert ex.kind == "TIMEOUT"
    else:
        raise AssertionError("timeout control unexpectedly passed")

    results[0]["exit_status"] = 0
    (all_logs / "mdnew-regression-generic_pair-exit-code.txt").write_text("0\n")
    results[0]["exit_status_file"]["sha256"] = hashlib.sha256(
        (all_logs / "mdnew-regression-generic_pair-exit-code.txt").read_bytes()).hexdigest()
    stdout = all_logs / "regressions/generic_pair.stdout.log"
    stdout.write_text("started but no terminal summary\n")
    results[0]["stdout"]["sha256"] = hashlib.sha256(stdout.read_bytes()).hexdigest()
    write_json(all_logs / "regressions/manifest.json", {
        "schema": "verifast-mdnew-regressions-v1", "infra_sha": infra_sha,
        "proof_sha": proof_sha, "candidate_commit": m.CANDIDATE,
        "candidate_tree": m.TREE, "results": results})
    try:
        m.audit(tool, all_logs)
    except m.AuditFailure as ex:
        assert ex.kind == "INCOMPLETE_EVIDENCE"
    else:
        raise AssertionError("incomplete run control unexpectedly passed")

    results[0]["stdout"]["sha256"] = "0" * 64
    write_json(all_logs / "regressions/manifest.json", {
        "schema": "verifast-mdnew-regressions-v1", "infra_sha": infra_sha,
        "proof_sha": proof_sha, "candidate_commit": m.CANDIDATE,
        "candidate_tree": m.TREE, "results": results})
    try:
        m.audit(tool, all_logs)
    except m.AuditFailure as ex:
        assert ex.kind == "INCOMPLETE_EVIDENCE"
    else:
        raise AssertionError("tampered log control unexpectedly passed")

    results[0]["exit_status"] = 1
    (all_logs / "mdnew-regression-generic_pair-exit-code.txt").write_text("1\n")
    results[0]["exit_status_file"]["sha256"] = hashlib.sha256(
        (all_logs / "mdnew-regression-generic_pair-exit-code.txt").read_bytes()).hexdigest()
    stdout.write_text("generic_pair.rs(4,3): error: Cannot prove condition.\n")
    results[0]["stdout"]["sha256"] = hashlib.sha256(stdout.read_bytes()).hexdigest()
    write_json(all_logs / "regressions/manifest.json", {
        "schema": "verifast-mdnew-regressions-v1", "infra_sha": infra_sha,
        "proof_sha": proof_sha, "candidate_commit": m.CANDIDATE,
        "candidate_tree": m.TREE, "results": results})
    try:
        m.audit(tool, all_logs)
    except m.AuditFailure as ex:
        assert ex.kind == "EARLY_OR_WRONG_DIAGNOSTIC"
    else:
        raise AssertionError("unexpected verifier failure control unexpectedly passed")

print(json.dumps({"synthetic_regression_controls": 5, "compiler_or_verifier_execution": False,
                  "passed": True}))
