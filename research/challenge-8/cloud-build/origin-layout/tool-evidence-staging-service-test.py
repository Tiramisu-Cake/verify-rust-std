#!/usr/bin/env python3
"""Synthetic tool staging/package service tests; no proof tools or Cloud calls."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PACKAGE_PATH = Path(os.environ.get("SMALLSORT_TEST_PACKAGER",
                                   str(HERE.parent / "package-evidence.py")))
HELPER_PATH = HERE / "first-callback-admission-controls.py"
CALLER_MANAGED = ("bin/verifast", "bin/refinement-checker", "bin/vf-rust-mir-exporter")
STAGING_SCHEMA = "smallsort-tool-evidence-staging-v1"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


package = load("tool_stage_test_package", PACKAGE_PATH)
controls = load("tool_stage_test_controls", HELPER_PATH)


class ToolEvidenceStagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def make_tool_home(self, path):
        home = Path(path)
        (home / "bin/rust/specs").mkdir(parents=True)
        (home / "bin/rust/specs/core.rsspec").write_bytes(b"spec bytes\n")
        (home / "bin/rustc").write_bytes(b"rustc helper bytes\n")
        for name in CALLER_MANAGED:
            entry = home / name
            entry.parent.mkdir(parents=True, exist_ok=True)
            entry.write_bytes(("caller-managed:" + name).encode())
        (home / "share/private-ish.txt").parent.mkdir(parents=True)
        (home / "share/private-ish.txt").write_bytes(b"root subtree excluded\n")
        return home

    @staticmethod
    def manifest(case):
        path = Path(case) / "tool-staging.json"
        if not path.is_file() or path.is_symlink():
            raise AssertionError("tool staging manifest is missing or not a regular file")
        value = json.loads(path.read_text())
        if value.get("schema") != STAGING_SCHEMA:
            raise AssertionError("unexpected tool staging manifest schema")
        return value

    @staticmethod
    def excluded_by_path(manifest):
        return {entry.get("path"): entry for entry in manifest.get("excluded", [])}

    def assert_no_links(self, root):
        root = Path(root)
        self.assertTrue(root.is_dir())
        self.assertFalse(any(path.is_symlink() for path in root.rglob("*")))

    @staticmethod
    def tree_snapshot(root):
        root = Path(root)
        snapshot = {}
        for directory, dirnames, filenames in os.walk(root, followlinks=False):
            base = Path(directory)
            for name in list(dirnames) + filenames:
                path = base / name
                rel = path.relative_to(root).as_posix()
                mode = path.lstat().st_mode
                if stat.S_ISLNK(mode):
                    snapshot[rel] = ("symlink", os.readlink(path))
                elif stat.S_ISDIR(mode):
                    snapshot[rel] = ("directory", stat.S_IMODE(mode))
                elif stat.S_ISREG(mode):
                    snapshot[rel] = ("file", hashlib.sha256(path.read_bytes()).hexdigest(),
                                     path.stat().st_size, stat.S_IMODE(mode))
                else:
                    snapshot[rel] = ("special", stat.S_IFMT(mode))
        return snapshot

    def test_regular_assets_stage_with_manifest_and_real_tooltree_at_both_paths(self):
        for relative_case in (
                Path("synthetic-tool"),
                Path("allprooflogs/cases/r11-storage-placement-controls/duplicate_live")):
            with self.subTest(relative_case=relative_case):
                evidence = self.root / ("evidence-" + relative_case.parts[0])
                case = evidence.joinpath(*relative_case.parts[1:])
                case.mkdir(parents=True)
                (case / "verified.rs").write_bytes(b"case source\n")
                (case / "compiler-mir.bin").write_bytes(b"case MIR bytes")
                (case / "verifast.log").write_bytes(b"saved case log\n")
                home_path = (self.root / "synthetic-tool" if relative_case.parts[0] == "synthetic-tool"
                             else self.root / ("tool-home-" + relative_case.parts[0]))
                home = self.make_tool_home(home_path)
                # Reproduce the historical synthetic-tool/.devcontainer link
                # without requiring or inspecting a real developer config.
                external_config = self.root / ("external-config-" + relative_case.parts[0])
                external_config.mkdir()
                (external_config / "config.json").write_bytes(b"synthetic config")
                (home / ".devcontainer").symlink_to(external_config, target_is_directory=True)

                source_before = self.tree_snapshot(home)
                bin_dir, child_env = controls._tool_tree(home, case, {"PATH": "/usr/bin"})
                self.assertEqual(self.tree_snapshot(home), source_before)
                tool_root = case / "tool"
                self.assertEqual(bin_dir, tool_root / "bin")
                self.assertTrue(child_env["PATH"].startswith(str(bin_dir) + os.pathsep))
                self.assertTrue(child_env["LD_LIBRARY_PATH"].startswith(str(home / "bin")))
                self.assert_no_links(tool_root)
                self.assertEqual((bin_dir / "rust/specs/core.rsspec").read_bytes(),
                                 b"spec bytes\n")
                self.assertEqual((bin_dir / "rustc").read_bytes(), b"rustc helper bytes\n")
                for entry in CALLER_MANAGED:
                    self.assertFalse((tool_root / entry).exists(), entry)
                self.assertFalse((tool_root / "share").exists())
                self.assertFalse((tool_root / ".devcontainer").exists())

                record = self.manifest(case)
                self.assertEqual(record["status"], "COMPLETE")
                self.assertEqual(record["caller_managed"], list(CALLER_MANAGED))
                included = {row["path"]: row for row in record["included"]}
                self.assertEqual(included["bin/rust/specs/core.rsspec"], {
                    "path": "bin/rust/specs/core.rsspec",
                    "sha256": hashlib.sha256(b"spec bytes\n").hexdigest(),
                    "size_bytes": len(b"spec bytes\n")})
                excluded = self.excluded_by_path(record)
                self.assertIn("share", excluded)
                self.assertIn(".devcontainer", excluded)
                self.assertEqual(excluded[".devcontainer"]["kind"], "symlink")
                self.assertEqual(excluded[".devcontainer"]["target"], str(external_config))

    def test_symlinks_are_recorded_without_following_or_leaking_filesystem_links(self):
        home = self.make_tool_home(self.root / "synthetic-tool")
        case = self.root / "evidence/allprooflogs/cases/synthetic"
        case.mkdir(parents=True)
        sentinel = self.root / "sentinel"
        sentinel.mkdir()
        (sentinel / "secret.txt").write_bytes(b"never copy through a link")
        (home / ".devcontainer").symlink_to(sentinel, target_is_directory=True)
        (home / "bin/link-file").symlink_to(sentinel / "secret.txt")
        (home / "bin/link-dir").symlink_to(sentinel, target_is_directory=True)
        (home / "bin/dangling").symlink_to("missing-target")
        (home / "bin/cycle-a").symlink_to("cycle-b")
        (home / "bin/cycle-b").symlink_to("cycle-a")
        (home / "bin/absolute").symlink_to((sentinel / "secret.txt").resolve())

        source_before = self.tree_snapshot(home)
        controls._tool_tree(home, case, {})
        self.assertEqual(self.tree_snapshot(home), source_before)
        tool_root = case / "tool"
        self.assert_no_links(tool_root)
        copied = [path.relative_to(tool_root).as_posix() for path in tool_root.rglob("*")]
        for rel in ("bin/link-file", "bin/link-dir", "bin/dangling",
                    "bin/cycle-a", "bin/cycle-b", "bin/absolute"):
            self.assertNotIn(rel, copied)
        self.assertEqual((sentinel / "secret.txt").read_bytes(), b"never copy through a link")

        record = self.manifest(case)
        self.assertEqual(record["status"], "COMPLETE")
        excluded = self.excluded_by_path(record)
        for rel, target in {
                ".devcontainer": str(sentinel),
                "bin/link-file": str(sentinel / "secret.txt"),
                "bin/link-dir": str(sentinel),
                "bin/dangling": "missing-target",
                "bin/cycle-a": "cycle-b", "bin/cycle-b": "cycle-a",
                "bin/absolute": str((sentinel / "secret.txt").resolve())}.items():
            self.assertEqual(excluded[rel]["kind"], "symlink", rel)
            self.assertEqual(excluded[rel].get("target"), target, rel)
            self.assertTrue(excluded[rel].get("reason"), rel)

    def test_invalid_roots_and_special_files_fail_without_complete_manifest(self):
        for mode in ("missing_bin", "symlink_bin", "symlink_home", "fifo"):
            with self.subTest(mode=mode):
                home = self.root / ("home-" + mode)
                case = self.root / ("case-" + mode)
                case.mkdir()
                if mode == "symlink_home":
                    real = self.make_tool_home(self.root / "real-home")
                    home.symlink_to(real, target_is_directory=True)
                elif mode == "missing_bin":
                    home.mkdir()
                elif mode == "symlink_bin":
                    home.mkdir()
                    actual_bin = self.root / "actual-bin"
                    actual_bin.mkdir()
                    home.joinpath("bin").symlink_to(actual_bin, target_is_directory=True)
                else:
                    home = self.make_tool_home(home)
                    os.mkfifo(home / "bin/z-fifo")
                with self.assertRaises(Exception):
                    controls._tool_tree(home, case, {})
                record = self.manifest(case)
                self.assertEqual(record["status"], "FAILED")
                self.assertNotEqual(record["status"], "COMPLETE")
                if mode == "fifo":
                    self.assertTrue(record["included"], "failure must retain partial staging receipt")
                    self.assertTrue((case / "tool/bin/rust/specs/core.rsspec").is_file())
                    self.assertIn("error", record)

    def test_preexisting_destination_refuses_without_overwriting_existing_files(self):
        home = self.make_tool_home(self.root / "preexisting-home")
        case = self.root / "preexisting-case"
        (case / "tool/bin").mkdir(parents=True)
        marker = case / "tool/bin/keep.txt"
        marker.write_bytes(b"preserve existing destination")
        with self.assertRaises(Exception):
            controls._tool_tree(home, case, {})
        self.assertEqual(marker.read_bytes(), b"preserve existing destination")

    def test_copy_tool_file_refuses_source_links_and_destination_links_or_files(self):
        sentinel = self.root / "copy-sentinel"
        sentinel.write_bytes(b"unchanged sentinel")
        source_link = self.root / "source-link"
        source_link.symlink_to(sentinel)
        with self.assertRaises(OSError):
            controls._copy_tool_file(source_link, self.root / "copied-source-link")
        self.assertFalse((self.root / "copied-source-link").exists())
        self.assertEqual(sentinel.read_bytes(), b"unchanged sentinel")

        source = self.root / "regular-source"
        source.write_bytes(b"copy exactly")
        destination_target = self.root / "destination-target"
        destination_target.write_bytes(b"preserve destination target")
        destination_link = self.root / "destination-link"
        destination_link.symlink_to(destination_target)
        with self.assertRaises(FileExistsError):
            controls._copy_tool_file(source, destination_link)
        self.assertTrue(destination_link.is_symlink())
        self.assertEqual(destination_target.read_bytes(), b"preserve destination target")

        existing = self.root / "existing-file"
        existing.write_bytes(b"preserve existing file")
        with self.assertRaises(FileExistsError):
            controls._copy_tool_file(source, existing)
        self.assertEqual(existing.read_bytes(), b"preserve existing file")

    def test_package_cli_archives_staged_case_as_regular_files_with_matching_inventory(self):
        evidence = self.root / "package-evidence"
        cases = {
            "synthetic-tool": evidence / "allprooflogs/cases/synthetic-tool",
            "r11-storage-placement-controls/duplicate_live":
                evidence / "allprooflogs/cases/r11-storage-placement-controls/duplicate_live",
        }
        for case in cases.values():
            case.mkdir(parents=True)
        (evidence / "run-exit.txt").write_text("0\n")
        (evidence / "full-stdout.log").write_text("synthetic stdout\n")
        (evidence / "full-stderr.log").write_text("")
        (evidence / "environment.txt").write_text("synthetic environment\n")
        (evidence / "submitted-config.json").write_text("{}\n")
        (evidence / "allprooflogs/case.log").write_text("synthetic outer log\n")
        retained = {
            "verified/lib.rs": b"synthetic source\n",
            "compiler-mir.bin": b"synthetic MIR bytes",
            "verifast.log": b"synthetic case log\n",
            "mir-exporter-wrapper.py": b"#!/usr/bin/env python3\npass\n",
        }
        external_config = self.root / "package-external-config"
        external_config.mkdir()
        (external_config / "config.json").write_text("sentinel that must not enter evidence")
        home = self.make_tool_home(self.root / "synthetic-tool")
        (home / ".devcontainer").symlink_to(external_config, target_is_directory=True)
        source_before = self.tree_snapshot(home)
        for case in cases.values():
            for rel, data in retained.items():
                target = case / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            controls._tool_tree(home, case, {})
            # Model assets installed by the caller after the shared staging helper
            # returns; these must remain packageable regular evidence files.
            for rel in CALLER_MANAGED:
                target = case / "tool" / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(("caller-output:" + rel).encode())
        self.assertEqual(self.tree_snapshot(home), source_before)

        out = self.root / "package-out"
        env = os.environ.copy()
        for key in ("CLOUD_BUILD_ID", "INFRA_SHA", "PROOF_SHA", "LANE",
                    "SUBMITTED_CONFIG_SHA", "PROOF_IMAGE"):
            env.pop(key, None)
        command = [sys.executable, str(PACKAGE_PATH), "--evidence", str(evidence),
                   "--out", str(out)]
        completed = subprocess.run(command, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        archive = out / "evidence.tar.gz"
        self.assertTrue(archive.is_file())
        with tarfile.open(archive, "r:gz") as tar:
            members = tar.getmembers()
            self.assertTrue(all(member.isfile() for member in members))
            contents = {member.name: tar.extractfile(member).read()
                        for member in members if member.isfile()}
        inventory = json.loads(contents["files-sha256.json"])
        for name, expected_sha in inventory.items():
            self.assertIn(name, contents)
            self.assertEqual(hashlib.sha256(contents[name]).hexdigest(), expected_sha, name)
        self.assertEqual(set(inventory), set(contents) - {"files-sha256.json", "manifest.json"})
        for case_name in ("synthetic-tool", "r11-storage-placement-controls/duplicate_live"):
            prefix = "allprooflogs/cases/" + case_name + "/"
            for rel, data in retained.items():
                self.assertEqual(contents[prefix + rel], data)
            self.assertIn(prefix + "tool-staging.json", contents)
            staging = json.loads(contents[prefix + "tool-staging.json"])
            self.assertEqual(staging["status"], "COMPLETE")
            self.assertIn(prefix + "tool/bin/rust/specs/core.rsspec", contents)
            self.assertIn(prefix + "tool/bin/verifast", contents)
            self.assertNotIn(prefix + "tool/.devcontainer/config.json", contents)
        self.assertNotIn(b"sentinel that must not enter evidence",
                         b"".join(contents.values()))

    def test_unrelated_evidence_symlink_still_fails_packager(self):
        evidence = self.root / "unrelated-symlink-evidence"
        evidence.mkdir()
        target = self.root / "external.txt"
        target.write_text("external")
        (evidence / "unrelated-link").symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink in evidence"):
            package.collect(evidence)


if __name__ == "__main__":
    unittest.main()
