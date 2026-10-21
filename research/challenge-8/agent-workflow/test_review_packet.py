"""Synthetic Git tests for review_packet; no network, Cloud, or proof tools."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("review_packet", HERE / "review_packet.py")
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


class ReviewPacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.root = self.parent / "repo"
        self.root.mkdir()
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "test@example.invalid")
        git(self.root, "config", "user.name", "Review Packet Test")
        (self.root / "src").mkdir()
        (self.root / "src/main.rs").write_text("fn old() {}\n")
        (self.root / "src/dep.rs").write_bytes(b"dependency v1\x00\n")
        (self.root / "mode.sh").write_text("#!/bin/sh\necho old\n")
        (self.root / "mode.sh").chmod(0o644)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "baseline")
        self.baseline = git(self.root, "rev-parse", "HEAD")
        (self.root / "src/main.rs").write_text("fn fixed() {}\n")
        (self.root / "src/new.rs").write_text("new file\n")
        (self.root / "mode.sh").chmod(0o755)
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "candidate")
        self.candidate = git(self.root, "rev-parse", "HEAD")
        self.spec = {
            "schema": module.SCHEMA, "worktree": str(self.root),
            "baseline_commit": self.baseline, "candidate_commit": self.candidate,
            "defect": "A parser accepted the invalid input.",
            "applicability": "Only applies to the committed parser path.",
            "invariants": ["Reject malformed input without changing state."],
            "controls": ["Valid input remains accepted.", "Malformed input is rejected."],
            "dependencies": ["src/dep.rs"], "prior_reviews": [],
            "known_limitations": ["This review packet does not prove runtime behavior."],
        }
        self.spec_path = self.parent / "spec.json"
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")
        self.out = self.parent / "packet"

    def create(self):
        self.created = module.create(self.spec_path, self.out)

    def check(self):
        return module.check(self.out, self.created["candidate_commit"], self.created["spec_sha256"])

    def test_committed_bytes_only_and_complete_changed_inventory(self):
        (self.root / "src/main.rs").write_text("dirty local replacement\n")
        (self.root / "untracked-secret.txt").write_text("must not enter packet")
        self.create()
        self.assertEqual(self.check()["state"], "PACKET_VALID_NOT_REVIEWED")
        meta = json.loads((self.out / "metadata.json").read_text())
        by_path = {entry["path"]: entry for entry in meta["changed_files"]}
        self.assertEqual(set(by_path), {"mode.sh", "src/main.rs", "src/new.rs"})
        self.assertEqual(by_path["mode.sh"]["candidate"]["mode"], "100755")
        self.assertEqual(by_path["src/main.rs"]["candidate"]["sha256"], module._sha(b"fn fixed() {}\n"))
        self.assertNotIn("dirty local replacement", (self.out / "diff.patch").read_text(errors="replace"))
        self.assertNotIn("untracked-secret", " ".join(p.name for p in self.out.rglob("*")))
        deps = meta["dependencies"][0]
        self.assertEqual((self.out / deps["member"]).read_bytes(), b"dependency v1\x00\n")
        reviewer = (self.out / "reviewer.md").read_text()
        self.assertIn("grants no proof credit", reviewer)
        self.assertIn("NOT_REVIEWED", json.loads((self.out / "metadata.json").read_text())["review_state"])

    def test_check_detects_dependency_diff_metadata_and_inventory_tampering(self):
        self.create()
        dep_file = self.out / "dependencies" / "0000.bin"
        dep_file.write_bytes(b"forged dependency")
        self.refresh_inventory()
        with self.assertRaises(module.ReviewPacketError):
            self.check()
        self.create_again()
        metadata = json.loads((self.out / "metadata.json").read_text())
        metadata["changed_files"] = []
        (self.out / "metadata.json").write_text(json.dumps(metadata) + "\n")
        self.refresh_inventory()
        with self.assertRaises(module.ReviewPacketError):
            self.check()

    def create_again(self):
        import shutil
        shutil.rmtree(self.out)
        self.create()

    def refresh_inventory(self):
        files = {p.relative_to(self.out).as_posix(): module._sha(p.read_bytes())
                 for p in self.out.rglob("*") if p.is_file() and p.name != "inventory.json"}
        (self.out / "inventory.json").write_bytes(module._json({"schema": "smallsort-review-inventory-v1", "files": files}))

    def test_rejects_non_ancestor_and_output_inside_worktree_before_writing(self):
        other = self.parent / "other"
        git(self.root, "checkout", "-qb", "other-branch", self.baseline)
        nonancestor = git(self.root, "rev-parse", "HEAD")
        git(self.root, "checkout", "-q", "main")
        spec = dict(self.spec, baseline_commit=self.candidate, candidate_commit=nonancestor)
        self.spec_path.write_text(json.dumps(spec))
        with self.assertRaises(module.ReviewPacketError):
            module.create(self.spec_path, self.out)
        self.spec_path.write_text(json.dumps(self.spec))
        inside = self.root / "packet"
        with self.assertRaises(module.ReviewPacketError):
            module.create(self.spec_path, inside)
        self.assertFalse(inside.exists())
        self.assertFalse(other.exists())

    def test_rejects_symlinked_output_ancestor(self):
        target = self.parent / "real"
        target.mkdir()
        link = self.parent / "alias"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaises(module.ReviewPacketError):
            module.create(self.spec_path, link / "packet")
        self.assertEqual(list(target.iterdir()), [])

    def test_unrelated_committed_symlink_is_accepted_but_selected_or_changed_is_rejected(self):
        link = self.root / "untouched-link"
        link.symlink_to("src/dep.rs")
        git(self.root, "add", "untouched-link")
        git(self.root, "commit", "-qm", "symlink baseline")
        baseline_with_link = git(self.root, "rev-parse", "HEAD")
        (self.root / "src/main.rs").write_text("fn final() {}\n")
        git(self.root, "add", "src/main.rs")
        git(self.root, "commit", "-qm", "candidate with unrelated symlink")
        candidate_with_link = git(self.root, "rev-parse", "HEAD")
        self.spec.update(baseline_commit=baseline_with_link, candidate_commit=candidate_with_link)
        self.spec_path.write_text(json.dumps(self.spec))
        self.create()
        self.assertEqual(self.check()["state"], "PACKET_VALID_NOT_REVIEWED")

        self.create_again()
        self.spec["dependencies"] = ["untouched-link"]
        self.spec_path.write_text(json.dumps(self.spec))
        with self.assertRaisesRegex(module.ReviewPacketError, "dependency is not a regular"):
            module.create(self.spec_path, self.parent / "selected-link-packet")

        self.spec["dependencies"] = ["src/dep.rs"]
        self.spec_path.write_text(json.dumps(self.spec))
        self.create_again()
        (self.root / "untouched-link").unlink()
        git(self.root, "add", "-u", "untouched-link")
        git(self.root, "commit", "-qm", "delete symlink")
        deleted_link_candidate = git(self.root, "rev-parse", "HEAD")
        self.spec.update(candidate_commit=deleted_link_candidate, dependencies=["src/dep.rs"])
        self.spec_path.write_text(json.dumps(self.spec))
        with self.assertRaisesRegex(module.ReviewPacketError, "changed baseline path is not a regular"):
            module.create(self.spec_path, self.parent / "deleted-link-packet")

    def test_check_requires_external_candidate_and_spec_identity_even_after_inventory_refresh(self):
        self.create()
        old_spec_sha = self.created["spec_sha256"]
        spec = json.loads((self.out / "spec.json").read_text())
        spec["defect"] = "A different defect scope."
        (self.out / "spec.json").write_bytes(module._json(spec))
        self.refresh_inventory()
        with self.assertRaisesRegex(module.ReviewPacketError, "expect-spec-sha256"):
            module.check(self.out, self.candidate, old_spec_sha)
        with self.assertRaisesRegex(module.ReviewPacketError, "expect-candidate"):
            module.check(self.out, "0" * 40, old_spec_sha)

    def test_spec_prior_and_bundle_reads_reject_symlink_ancestors_and_large_prior(self):
        target = self.parent / "real-files"
        target.mkdir()
        (target / "spec.json").write_text(json.dumps(self.spec))
        link = self.parent / "spec-alias"
        link.symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(module.ReviewPacketError, "spec has symlink ancestor"):
            module.create(link / "spec.json", self.out)

        large_prior = target / "prior.md"
        large_prior.write_bytes(b"x" * (module.MAX_PRIOR + 1))
        self.spec["prior_reviews"] = [{"path": str(large_prior), "sha256": module._sha(large_prior.read_bytes())}]
        self.spec_path.write_text(json.dumps(self.spec))
        with self.assertRaisesRegex(module.ReviewPacketError, "prior review must be a regular file"):
            self.create()
        prior_alias = self.parent / "prior-alias"
        prior_alias.symlink_to(target, target_is_directory=True)
        self.spec["prior_reviews"] = [{"path": str(prior_alias / "prior.md"), "sha256": module._sha(large_prior.read_bytes())}]
        self.spec_path.write_text(json.dumps(self.spec))
        with self.assertRaisesRegex(module.ReviewPacketError, "prior review has symlink ancestor"):
            self.create()

        self.spec["prior_reviews"] = []
        self.spec_path.write_text(json.dumps(self.spec))
        self.create()
        bundle_alias = self.parent / "bundle-alias"
        bundle_alias.symlink_to(self.parent, target_is_directory=True)
        with self.assertRaisesRegex(module.ReviewPacketError, "bundle has symlink ancestor"):
            module.check(bundle_alias / "packet", self.created["candidate_commit"], self.created["spec_sha256"])

    def test_rendered_reviewer_limit_is_enforced(self):
        self.spec["controls"] = ["Control: " + ("x" * 7600)]
        self.spec_path.write_text(json.dumps(self.spec))
        with self.assertRaisesRegex(module.ReviewPacketError, "rendered reviewer instructions exceed 8 KiB"):
            self.create()
        self.assertFalse(self.out.exists())

    def test_git_stdout_and_tree_and_changed_name_limits(self):
        with self.assertRaisesRegex(module.ReviewPacketError, "git output exceeds 1 byte limit"):
            module._git(self.root, "diff", "--no-ext-diff", self.baseline, self.candidate, "--", binary=True, limit=1)
        with patch.object(module, "MAX_TREE_ENTRIES", 1):
            with self.assertRaisesRegex(module.ReviewPacketError, "Git tree exceeds 1 entry limit"):
                module._expected(module._validate(self.spec))
        with patch.object(module, "MAX_CHANGED_NAME_BYTES", 1):
            with self.assertRaisesRegex(module.ReviewPacketError, "git output exceeds 1 byte limit"):
                module._expected(module._validate(self.spec))

    def test_git_stderr_is_bounded_and_timeout_kills_child(self):
        fakebin = self.parent / "fakebin"
        fakebin.mkdir()
        fake_git = fakebin / "git"
        fake_git.write_text("#!/usr/bin/python3\nimport sys\nsys.stderr.write('e' * 100000)\nsys.exit(1)\n")
        fake_git.chmod(0o755)
        with patch.dict(os.environ, {"PATH": str(fakebin)}):
            with self.assertRaises(module.ReviewPacketError) as caught:
                module._git(self.root, "failing-command")
        self.assertIn("stderr truncated at 8192 bytes", str(caught.exception))
        self.assertLess(len(str(caught.exception)), 8400)

        fake_git.write_text("#!/usr/bin/python3\nimport time\ntime.sleep(5)\n")
        fake_git.chmod(0o755)
        with patch.dict(os.environ, {"PATH": str(fakebin)}), patch.object(module, "MAX_GIT_SECONDS", 0.1):
            with self.assertRaisesRegex(module.ReviewPacketError, "exceeded 0.1s timeout"):
                module._git(self.root, "slow-command")

    def test_prior_review_reference_requires_exact_hash_and_is_not_go(self):
        prior = self.parent / "prior.md"
        prior.write_text("review decision: GO")
        self.spec["prior_reviews"] = [{"path": str(prior), "sha256": module._sha(prior.read_bytes())}]
        self.spec_path.write_text(json.dumps(self.spec))
        self.create()
        self.assertEqual(self.check()["proof_credit"], "NONE")
        prior.write_text("changed decision")
        with self.assertRaises(module.ReviewPacketError):
            self.check()

    def test_rejects_dependency_caps_and_invalid_path(self):
        huge = self.root / "src/huge.bin"
        huge.write_bytes(b"x" * (module.MAX_DEP + 1))
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "large dependency")
        candidate = git(self.root, "rev-parse", "HEAD")
        self.spec.update(candidate_commit=candidate, dependencies=["src/huge.bin"])
        self.spec_path.write_text(json.dumps(self.spec))
        with self.assertRaises(module.ReviewPacketError):
            self.create()
        self.spec["dependencies"] = ["../escape"]
        self.spec_path.write_text(json.dumps(self.spec))
        with self.assertRaises(module.ReviewPacketError):
            self.create()
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
