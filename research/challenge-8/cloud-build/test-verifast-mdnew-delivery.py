#!/usr/bin/env python3
"""Small Git-only delivery tests; does not compile or execute VeriFast."""
from __future__ import annotations
import hashlib, importlib.util, json, shutil, subprocess, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESTORE = HERE / "restore-verifast-input.py"
SPEC = importlib.util.spec_from_file_location("mdnew_restore", RESTORE)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args])


class DeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument("--source-repository", type=Path, required=True)
        p.add_argument("--bundle", type=Path, required=True)
        p.add_argument("--manifest", type=Path, required=True)
        cls.args = p.parse_args()
        cls.source = cls.args.source_repository.resolve()
        cls.bundle_source = cls.args.bundle.resolve()
        cls.manifest_source = cls.args.manifest.resolve()

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="mdnew-delivery-test-")
        self.root = Path(self.tmp.name)
        self.repo = self.root / "tool"
        subprocess.run(["git", "clone", "--quiet", "--shared", str(self.source), str(self.repo)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "checkout", "--quiet", "--detach", MODULE.BASE], check=True)
        self.bundle = self.root / "bundle"
        self.manifest = self.root / "manifest"
        shutil.copyfile(self.bundle_src, self.bundle)
        shutil.copyfile(self.manifest_src, self.manifest)

    @property
    def bundle_src(self) -> Path:
        return self.bundle_source

    @property
    def manifest_src(self) -> Path:
        return self.manifest_source

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def altered(self, mutate) -> dict:
        data=json.loads(self.manifest.read_text())
        mutate(data)
        self.manifest.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
        return data

    def reject(self, expected: str) -> None:
        with self.assertRaisesRegex(MODULE.DeliveryError, expected):
            MODULE.validate(self.repo, self.bundle, self.manifest)

    def test_exact_git_identity_restore(self) -> None:
        receipt=self.root/"receipt.json"; dest=self.root/"candidate"
        proc=subprocess.run(["python3",str(RESTORE),"--repository",str(self.repo),"--bundle",str(self.bundle),
            "--manifest",str(self.manifest),"--destination",str(dest),"--receipt",str(receipt),
            "--infra-sha","4058e8bf45eb567e4656d953274c96bf8488a7a3","--proof-sha","4058e8bf45eb567e4656d953274c96bf8488a7a3"],capture_output=True,text=True)
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(git("-C",str(dest),"rev-parse","HEAD").decode().strip(),MODULE.CANDIDATE)
        self.assertEqual(git("-C",str(dest),"rev-parse","HEAD^{tree}").decode().strip(),MODULE.TREE)
        data=json.loads(receipt.read_text())
        self.assertTrue(data["git_identity_preserved"])
        self.assertEqual(data["candidate_commit"],MODULE.CANDIDATE)
        self.assertEqual(data["bundle_sha256"],hashlib.sha256(self.bundle.read_bytes()).hexdigest())

    def test_wrong_bundle_digest_rejected(self) -> None:
        self.altered(lambda m:m.update(bundle_sha256="0"*64))
        self.reject("bundle digest mismatch")

    def test_wrong_prerequisite_header_rejected(self) -> None:
        raw=self.bundle.read_bytes(); old=b"-"+MODULE.BASE.encode()
        self.assertEqual(raw.count(old),1)
        self.bundle.write_bytes(raw.replace(old,b"-"+b"1"*40,1))
        self.altered(lambda m:m.update(bundle_sha256=hashlib.sha256(self.bundle.read_bytes()).hexdigest()))
        self.reject("prerequisite header")

    def test_wrong_ref_rejected(self) -> None:
        self.altered(lambda m:m.update(candidate_ref="refs/heads/other"))
        self.reject("Git identities mismatch")

    def test_wrong_tree_rejected(self) -> None:
        self.altered(lambda m:m.update(candidate_tree="0"*40))
        self.reject("Git identities mismatch")

    def test_wrong_fixture_blob_rejected(self) -> None:
        rel=MODULE.FIXTURES[0]
        self.altered(lambda m:m["fixtures"][rel].update(sha256="0"*64))
        self.reject("fixture manifest mismatch")

    def test_unsafe_selected_path_rejected(self) -> None:
        def mutate(m):
            item=m["selected_files"].pop(MODULE.SELECTED[0])
            m["selected_files"]["../.git/config"]=item
        self.altered(mutate)
        self.reject("selected source inventory")

    def test_wrong_base_checkout_rejected(self) -> None:
        subprocess.run(["git","-C",str(self.repo),"checkout","--quiet","--detach",MODULE.CANDIDATE],check=True)
        self.reject("not the exact prerequisite base")


def main() -> int:
    unittest.main(argv=[__file__], verbosity=2)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
