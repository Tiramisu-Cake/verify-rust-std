#!/usr/bin/env python3
"""Hosted-run safety checks for the compact evidence packager."""

import importlib.util
import pathlib
import unittest
import zipfile


SCRIPT = pathlib.Path(__file__).with_name("package-sort4-evidence.py")
SPEC = importlib.util.spec_from_file_location("sort4_evidence_packager", SCRIPT)
PACKAGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGER)


class EvidencePackagerTests(unittest.TestCase):
    def test_rejects_traversal_and_windows_paths(self):
        for path in ("../escape", "/absolute", "C:\\escape", "a\\..\\b"):
            with self.subTest(path=path), self.assertRaises(RuntimeError):
                PACKAGER.safe_member_name(path)

    def test_omits_symlink_entries_without_following_them(self):
        shadow = zipfile.ZipInfo("maybeuninit-new-pointer/mutation-profile/bin/tool")
        shadow.external_attr = 0o120777 << 16
        include, reason = PACKAGER.classify(shadow, pathlib.PurePosixPath(shadow.filename))
        self.assertFalse(include)
        self.assertIn("shadow tool profile", reason)

        link = zipfile.ZipInfo("maybeuninit-new-pointer/evidence/link")
        link.external_attr = 0o120777 << 16
        include, reason = PACKAGER.classify(link, pathlib.PurePosixPath(link.filename))
        self.assertFalse(include)
        self.assertIn("symbolic link", reason)

    def test_excludes_binary_and_tool_payloads_but_keeps_mir_binary(self):
        include, reason = PACKAGER.current_file_decision(
            pathlib.PurePosixPath("select-pointer/lib/libverifast.so"), False, False
        )
        self.assertFalse(include)
        self.assertIn("subtree", reason)
        include, reason = PACKAGER.current_file_decision(
            pathlib.PurePosixPath("select-pointer/libverifast.so"), False, False
        )
        self.assertFalse(include)
        self.assertIn("binary", reason)
        include, _ = PACKAGER.current_file_decision(
            pathlib.PurePosixPath("select-pointer/compiler-mir.bin"), False, False
        )
        self.assertTrue(include)
        include, reason = PACKAGER.current_file_decision(
            pathlib.PurePosixPath("select-pointer/verifast"), False, False, True
        )
        self.assertFalse(include)
        self.assertIn("executable tool payload", reason)

    def test_enforces_compact_archive_size_limit(self):
        with self.assertRaises(RuntimeError):
            PACKAGER.checked_size(pathlib.Path(__file__), 1)

    def test_manifest_rejects_duplicates_and_hashless_inclusions(self):
        valid = {
            "source_set": "current", "source_entry": "research-results/a.log",
            "included": True, "sha256": "a" * 64, "compact_entry": "current/a.log",
            "file_size": 12, "crc32": "1234abcd",
        }
        PACKAGER.validate_manifest_entries([valid])
        with self.assertRaises(RuntimeError):
            PACKAGER.validate_manifest_entries([valid, valid])
        broken = dict(valid, sha256=None)
        with self.assertRaises(RuntimeError):
            PACKAGER.validate_manifest_entries([broken])
        escaped = dict(valid, compact_entry="current/../outside.log")
        with self.assertRaises(RuntimeError):
            PACKAGER.validate_manifest_entries([escaped])


if __name__ == "__main__":
    unittest.main(verbosity=2)
