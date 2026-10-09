#!/usr/bin/env python3
"""Restore the pinned VeriFast candidate bundle into a disposable checkout."""
from __future__ import annotations
import argparse, hashlib, json, re, subprocess
from pathlib import Path, PurePosixPath

BASE = "f76012fb518703b1d98e243ac4f487f16877cfcb"
CANDIDATE = "fc03ad9e5ab3404398404f3bba9d7bcacec01c43"
TREE = "b292b2e0549db791e57245b0218c4f519e8b821e"
REF = "refs/heads/challenge8/mdnew-focused-validation"
INPUT_ROOT = "research/challenge-8/verifast-input/" + CANDIDATE + "/"
FIXTURES = (
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/forget.rs",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/shared_cleanup.rs",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/false_normal_post.rs",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/shared_false_unwind.rs",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/dead_code_pre.rs",
)
SELECTED = (
    "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/README.md",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/dead_code_pre.rs",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/false_normal_post.rs",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/forget.rs",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/shared_cleanup.rs",
    "tests/rust/purely_unsafe/manuallydrop_new_cfg/shared_false_unwind.rs",
    "tests/rust/testsuite.mysh",
)

class DeliveryError(ValueError):
    pass

def run(argv: list[str], *, cwd: Path | None = None) -> bytes:
    p = subprocess.run(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise DeliveryError(f"command failed ({p.returncode}): {' '.join(argv)}: " +
                            p.stderr.decode(errors="replace")[-2000:])
    return p.stdout

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def check(cond: bool, reason: str) -> None:
    if not cond:
        raise DeliveryError(reason)

def validate(repo: Path, bundle: Path, manifest_path: Path) -> dict:
    try:
        m = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise DeliveryError(f"cannot read manifest: {exc}") from exc
    check(m.get("schema") == "verifast-input-bundle-v1" and
          m.get("purpose") == "mdnew-cfg-cloud-delivery", "manifest schema/purpose mismatch")
    check(m.get("base_commit") == BASE and m.get("candidate_commit") == CANDIDATE and
          m.get("candidate_tree") == TREE and m.get("candidate_ref") == REF,
          "manifest pinned Git identities mismatch")
    check(m.get("bundle_relative_path") == INPUT_ROOT + "bundle", "bundle path mismatch")
    check(set(m.get("selected_files", {})) == set(SELECTED), "selected source inventory differs from audited allowlist")
    bundle_bytes = bundle.read_bytes()
    check(sha(bundle_bytes) == m.get("bundle_sha256"), "bundle digest mismatch")
    check(run(["git", "-C", str(repo), "rev-parse", "HEAD"]).decode().strip() == BASE,
          "tool checkout is not the exact prerequisite base")
    check(not run(["git", "-C", str(repo), "status", "--porcelain"]).strip(),
          "tool checkout is not clean")
    header = bundle_bytes.split(b"\n\n", 1)[0].decode("ascii", errors="strict").splitlines()
    prerequisites = [line[1:].split(" ", 1)[0] for line in header if line.startswith("-")]
    check(prerequisites == [BASE], "bundle prerequisite header must name exactly the pinned base")
    check(run(["git", "-C", str(repo), "bundle", "verify", str(bundle)]).decode().find(BASE) >= 0,
          "bundle prerequisite verification did not name base")
    heads = run(["git", "-C", str(repo), "bundle", "list-heads", str(bundle)]).decode().splitlines()
    check(heads == [CANDIDATE + " " + REF], "bundle ref set differs")
    check(set(m.get("fixtures", {})) == set(FIXTURES), "fixture inventory mismatch")
    selected = m.get("selected_files")
    check(isinstance(selected, dict) and set(FIXTURES).issubset(selected),
          "selected source inventory incomplete")
    check("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml" in selected,
          "translator source absent from selected inventory")
    for rel, record in selected.items():
        posix = PurePosixPath(rel)
        check(rel and "\\" not in rel and not rel.startswith("/") and
              posix.as_posix() == rel and all(part not in ("", ".", "..") for part in rel.split("/")) and
              not any(part in (".git", ".config", "hooks", "config") for part in posix.parts),
              f"unsafe selected path: {rel}")
        check(isinstance(record, dict) and re.fullmatch(r"[0-9a-f]{40}", record.get("git_blob", "")) is not None,
              f"invalid blob identity for {rel}")
        check(re.fullmatch(r"[0-9a-f]{64}", record.get("sha256", "")) is not None,
              f"invalid digest for {rel}")
    run(["git", "-C", str(repo), "fetch", str(bundle), REF + ":refs/verifast-delivery/candidate"])
    check(run(["git", "-C", str(repo), "rev-parse", "refs/verifast-delivery/candidate"]).decode().strip() == CANDIDATE,
          "fetched candidate commit identity differs")
    check(run(["git", "-C", str(repo), "rev-parse", CANDIDATE + "^{tree}"]).decode().strip() == TREE,
          "candidate tree identity differs")
    for rel, record in selected.items():
        oid = run(["git", "-C", str(repo), "rev-parse", CANDIDATE + ":" + rel]).decode().strip()
        raw = run(["git", "-C", str(repo), "show", CANDIDATE + ":" + rel])
        check(oid == record["git_blob"] and sha(raw) == record["sha256"] and
              len(raw) == record["bytes"], f"selected candidate bytes mismatch: {rel}")
    check(set(m["fixtures"]) == set(FIXTURES), "fixture keys differ")
    for rel in FIXTURES:
        check(m["fixtures"][rel] == selected[rel], f"fixture manifest mismatch: {rel}")
    return m

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repository", type=Path, required=True)
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    p.add_argument("--infra-sha", required=True)
    p.add_argument("--proof-sha", required=True)
    a = p.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", a.infra_sha) or not re.fullmatch(r"[0-9a-f]{40}", a.proof_sha):
        p.error("infra/proof identities must be full lowercase SHA-1 values")
    try:
        m = validate(a.repository.resolve(), a.bundle.resolve(), a.manifest.resolve())
        check(not a.destination.exists(), "candidate destination already exists")
        a.destination.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "-C", str(a.repository), "worktree", "add", "--detach",
             str(a.destination), CANDIDATE])
        check(run(["git", "-C", str(a.destination), "rev-parse", "HEAD"]).decode().strip() == CANDIDATE,
              "restored candidate checkout SHA differs")
        check(run(["git", "-C", str(a.destination), "rev-parse", "HEAD^{tree}"]).decode().strip() == TREE,
              "restored candidate checkout tree differs")
        check(not run(["git", "-C", str(a.destination), "status", "--porcelain"]).strip(),
              "restored candidate checkout is not clean")
        for rel, record in m["selected_files"].items():
            restored = (a.destination / rel).read_bytes()
            check(sha(restored) == record["sha256"] and len(restored) == record["bytes"],
                  f"restored worktree bytes differ: {rel}")
        receipt = {"classification":"RESTORED_GIT_INPUT", "infra_sha":a.infra_sha,
                   "proof_sha":a.proof_sha, "base_commit":BASE,
                   "candidate_commit":CANDIDATE, "candidate_tree":TREE,
                   "candidate_ref":REF, "bundle_sha256":m["bundle_sha256"],
                   "manifest_sha256":sha(a.manifest.read_bytes()),
                   "selected_files":{k:v["sha256"] for k,v in m["selected_files"].items()},
                   "fixture_hashes":{k:v["sha256"] for k,v in m["fixtures"].items()},
                   "destination":str(a.destination), "git_identity_preserved":True}
        a.receipt.parent.mkdir(parents=True, exist_ok=True)
        a.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
        print(json.dumps(receipt, sort_keys=True))
        return 0
    except (DeliveryError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"delivery restore rejected: {exc}", file=__import__('sys').stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
