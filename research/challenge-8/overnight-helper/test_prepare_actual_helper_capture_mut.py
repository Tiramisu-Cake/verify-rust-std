"""Synthetic checks for the P2 `*mut Element` fixture writer; no tool runs."""
from __future__ import annotations

import hashlib
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
spec = importlib.util.spec_from_file_location("p2_mut_capture",
                                              HERE / "prepare-actual-helper-capture-mut.py")
TARGET = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = TARGET
spec.loader.exec_module(TARGET)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class MutableFixture(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)

    def test_pair_differs_from_const_only_in_signature_types(self):
        record = TARGET.write_fixture(REPO, self.tmp / "mut")
        const = TARGET.load_const()
        const_record = const.write_fixture(REPO, self.tmp / "const")
        mut_v = (self.tmp / "mut/verified/lib.rs").read_bytes()
        mut_o = (self.tmp / "mut/original/lib.rs").read_bytes()
        const_v = (self.tmp / "const/verified/lib.rs").read_bytes()
        const_o = (self.tmp / "const/original/lib.rs").read_bytes()
        self.assertEqual(sha(const_v), record["const_verified_sha256"])
        self.assertEqual(sha(const_v), const_record["verified_sha256"])
        self.assertEqual(mut_v.replace(TARGET.MUT_SIGNATURE, TARGET.CONST_SIGNATURE, 1), const_v)
        self.assertEqual(mut_o.replace(TARGET.MUT_SIGNATURE, TARGET.CONST_SIGNATURE, 1), const_o)
        self.assertEqual(const.strip_ghost(mut_v), mut_o)
        self.assertEqual((sha(mut_o), sha(mut_v)),
                         (record["original_sha256"], record["verified_sha256"]))
        self.assertNotIn(b"*const", mut_o)
        self.assertEqual(mut_o.count(b"*mut Element"), 3)
        self.assertEqual(record["source_certificate"]["target_specialization"],
                         "T = *mut Element; Element unrestricted")
        self.assertIs(record["const_pair_identity_modulo_signature"], True)
        self.assertEqual(record["fixture_signature"].encode(), TARGET.MUT_SIGNATURE)
        self.assertEqual(record["translator_admission"], "NOT_IMPLEMENTED")
        self.assertEqual(record["helper_proof_status"], "NOT_RUN")

    def test_contract_text_is_the_published_p2_interface_text(self):
        record = TARGET.write_fixture(REPO, self.tmp / "mut")
        self.assertEqual(record["contract_text_sha256"],
                         "dc985de2e2a0e1a95e6c12c4b9cb78c4042d9d45f949d78904a999e82262b870")

    def test_refuses_overwrite_and_changed_std_source(self):
        TARGET.write_fixture(REPO, self.tmp / "mut")
        with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
            TARGET.write_fixture(REPO, self.tmp / "mut")
        fake = self.tmp / "repo"
        for rel in ("library/core/src/hint.rs", "library/core/src/mem/maybe_uninit.rs"):
            (fake / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / rel, fake / rel)
        hint = fake / "library/core/src/hint.rs"
        hint.write_bytes(hint.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "std source pin changed"):
            TARGET.write_fixture(fake, self.tmp / "other")

    def test_refuses_changed_const_preparer(self):
        original = TARGET.CONST_PREPARER_SHA256
        TARGET.CONST_PREPARER_SHA256 = "0" * 64
        try:
            with self.assertRaisesRegex(ValueError, "pinned const helper preparer differs"):
                TARGET.write_fixture(REPO, self.tmp / "mut")
        finally:
            TARGET.CONST_PREPARER_SHA256 = original


if __name__ == "__main__":
    unittest.main()
