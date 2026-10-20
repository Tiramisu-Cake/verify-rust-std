"""Synthetic facade archival controls; AST-only helpers, no runner/tool invocation."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

SOURCE = Path(__file__).with_name("a1-synthetic-backend.py")
TREE = ast.parse(SOURCE.read_text())
NAMES = {"_archive_synthetic_tool_facade", "_invoke_with_facade_cleanup"}
FUNCTIONS = [node for node in TREE.body
             if isinstance(node, ast.FunctionDef) and node.name in NAMES]
CODE = compile(ast.Module(body=FUNCTIONS, type_ignores=[]), str(SOURCE), "exec")


def need(ok, why):
    if not ok:
        raise RuntimeError("A1-SYNTHETIC-BACKEND: " + why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


NS = {"Path": Path, "os": os, "json": json, "_need": need, "_sha": sha}
exec(CODE, NS)
archive = NS["_archive_synthetic_tool_facade"]
invoke_with_cleanup = NS["_invoke_with_facade_cleanup"]
PACKAGE_FIXTURE_PATH = SOURCE.parent.parent / "test-package-evidence-manifest.py"
PACKAGE_FIXTURE_SPEC = importlib.util.spec_from_file_location(
    "synthetic_backend_package_fixture", PACKAGE_FIXTURE_PATH)
PACKAGE_FIXTURE = importlib.util.module_from_spec(PACKAGE_FIXTURE_SPEC)
PACKAGE_FIXTURE_SPEC.loader.exec_module(PACKAGE_FIXTURE)


class SyntheticFacadeArchiveTests(unittest.TestCase):
    def make_facade(self, root):
        facade = root / "synthetic-tool"
        facade.mkdir()
        target_dir = root.parent / (root.name + "-support-dir")
        target_dir.mkdir()
        (target_dir / "data.txt").write_text("support target remains external")
        target_file = root.parent / (root.name + "-support-file")
        target_file.write_text("driver target remains external")
        (facade / ".devcontainer").symlink_to(target_dir, target_is_directory=True)
        (facade / "support-file").symlink_to(target_file)
        bin_dir = facade / "bin"
        bin_dir.mkdir()
        (bin_dir / "support-driver").symlink_to(target_file)
        console = bin_dir / "verifast"
        console.write_bytes(b"console bytes")
        wrapper = bin_dir / "vf-rust-mir-exporter"
        wrapper.write_bytes(b"wrapper bytes")
        return facade, target_dir, target_file, console, wrapper

    def test_records_targets_then_unlinks_only_links_and_retains_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "evidence"
            root.mkdir()
            facade, target_dir, target_file, console, wrapper = self.make_facade(root)
            console_hash, wrapper_hash = sha(console), sha(wrapper)
            target_hashes = {target_dir / "data.txt": sha(target_dir / "data.txt"),
                             target_file: sha(target_file)}
            manifest_path = archive(root, facade, console_hash, wrapper_hash)
            manifest = json.loads(manifest_path.read_text())
            self.assertEqual(manifest["schema"], "a1-synthetic-tool-facade-archive-v1")
            self.assertTrue(manifest["facade_retained"])
            self.assertTrue(manifest["symlinks_removed_after_recording"])
            self.assertFalse(manifest["targets_dereferenced_for_archive"])
            self.assertFalse(manifest["proof_credit"])
            self.assertEqual(manifest["console"]["sha256"], console_hash)
            self.assertEqual(manifest["transport_wrapper"]["sha256"], wrapper_hash)
            self.assertEqual({(row["path"], row["target"], row["kind"])
                              for row in manifest["symlinks"]}, {
                (".devcontainer", str(target_dir), "symlink"),
                ("support-file", str(target_file), "symlink"),
                ("bin/support-driver", str(target_file), "symlink"),
            })
            self.assertFalse((facade / ".devcontainer").is_symlink())
            self.assertFalse((facade / "support-file").is_symlink())
            self.assertFalse((facade / "bin/support-driver").is_symlink())
            self.assertTrue(console.is_file() and wrapper.is_file())
            self.assertEqual(sha(console), console_hash)
            self.assertEqual(sha(wrapper), wrapper_hash)
            for path, digest in target_hashes.items():
                self.assertTrue(path.exists())
                self.assertEqual(sha(path), digest)

    def test_partial_facade_is_archived_without_following_or_requiring_bin(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "evidence"
            root.mkdir()
            facade = root / "synthetic-tool"
            facade.mkdir()
            outside = Path(temporary) / "outside"
            outside.write_text("untouched")
            (facade / ".devcontainer").symlink_to(outside)
            manifest_path = archive(root, facade, None, None)
            manifest = json.loads(manifest_path.read_text())
            self.assertTrue(manifest["symlinks_removed_after_recording"])
            self.assertIsNone(manifest["console"]["sha256"])
            self.assertIsNone(manifest["transport_wrapper"]["sha256"])
            self.assertFalse((facade / ".devcontainer").is_symlink())
            self.assertEqual(outside.read_text(), "untouched")
            self.assertTrue(facade.is_dir())

    def test_cleanup_runs_after_translator_error_and_preserves_primary_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "evidence"
            root.mkdir()
            facade, _, _, console, wrapper = self.make_facade(root)
            hashes = sha(console), sha(wrapper)
            manifest = []
            primary = RuntimeError("synthetic translator failed")

            def fail():
                raise primary

            with self.assertRaises(RuntimeError) as caught:
                invoke_with_cleanup(
                    fail, lambda: manifest.append(archive(root, facade, *hashes)))
            self.assertIs(caught.exception, primary)
            self.assertEqual(len(manifest), 1)
            self.assertTrue(json.loads(manifest[0].read_text())[
                "symlinks_removed_after_recording"])
            self.assertEqual(sha(console), hashes[0])
            self.assertEqual(sha(wrapper), hashes[1])

    def test_finalizer_archives_a_facade_when_creation_fails_partway(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "evidence"
            root.mkdir()
            facade = root / "synthetic-tool"
            target = Path(temporary) / "support-target"
            target.write_text("still present")
            manifest = []
            primary = RuntimeError("wrapper creation failed")

            def partial_setup():
                facade.mkdir()
                (facade / ".devcontainer").symlink_to(target)
                raise primary

            def cleanup():
                manifest.append(archive(root, facade, None, None))

            with self.assertRaises(RuntimeError) as caught:
                invoke_with_cleanup(partial_setup, cleanup)
            self.assertIs(caught.exception, primary)
            self.assertFalse((facade / ".devcontainer").is_symlink())
            self.assertEqual(target.read_text(), "still present")
            self.assertEqual(json.loads(manifest[0].read_text())["symlinks"], [{
                "path": ".devcontainer", "target": str(target), "kind": "symlink"}])

    def test_cleanup_error_is_added_without_masking_translator_error(self):
        primary = RuntimeError("translator primary")

        def fail():
            raise primary

        def cleanup_fail():
            raise OSError("manifest write failed")

        with self.assertRaises(RuntimeError) as caught:
            invoke_with_cleanup(fail, cleanup_fail)
        self.assertIs(caught.exception, primary)
        self.assertIn("manifest write failed", "\n".join(primary.__notes__))

    def test_cleanup_error_propagates_when_invocation_succeeded(self):
        with self.assertRaisesRegex(OSError, "manifest write failed"):
            invoke_with_cleanup(lambda: "result",
                                lambda: (_ for _ in ()).throw(OSError("manifest write failed")))

    def test_packager_rejects_before_and_accepts_after_facade_link_accounting(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            evidence, output = root / "evidence", root / "package"
            PACKAGE_FIXTURE.make_input(evidence, large_audit=False)
            facade = evidence / "synthetic-tool"
            facade.mkdir()
            target = root / "unchanged-support-target"
            target.write_text("the facade link points here")
            (facade / ".devcontainer").symlink_to(target)
            bin_dir = facade / "bin"
            bin_dir.mkdir()
            console = bin_dir / "verifast"
            wrapper = bin_dir / "vf-rust-mir-exporter"
            console.write_bytes(b"console")
            wrapper.write_bytes(b"wrapper")

            rejected = PACKAGE_FIXTURE.package(evidence, output)
            self.assertEqual(rejected.returncode, 1)
            self.assertIn("symlink in evidence: synthetic-tool/.devcontainer",
                          rejected.stderr)

            manifest_path = archive(evidence, facade, sha(console), sha(wrapper))
            manifest = json.loads(manifest_path.read_text())
            self.assertEqual(manifest["symlinks"], [{
                "path": ".devcontainer", "target": str(target), "kind": "symlink"}])
            self.assertFalse(any(path.is_symlink() for path in facade.rglob("*")))
            self.assertEqual(target.read_text(), "the facade link points here")
            accepted = PACKAGE_FIXTURE.package(evidence, output)
            self.assertEqual(accepted.returncode, 0, accepted.stderr)


if __name__ == "__main__":
    unittest.main()
