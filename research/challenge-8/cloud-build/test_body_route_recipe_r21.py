"""Static closure and tiny Git source-input tests for the inactive R21 route."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


CLOUD = Path(__file__).resolve().parent
REPO = CLOUD.parents[2]
CHALLENGE = REPO / "research/challenge-8"
RECIPE_PATH = CLOUD / "recipes/o26-sort4-body-r21.json"
CLOSURE_PATH = CHALLENGE / "task-history/select-callee-r21/BODY-ROUTE-CLOSURE.json"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load isolated module: {path}")
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SOURCE_INPUT = load("r21_recipe_source_input", CLOUD / "source-input.py")


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def commit(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=synthetic", "-c", "user.email=synthetic@example.invalid",
        "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def write(repo: Path, relative: str, raw: bytes = b"synthetic input\n") -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)


def tiny_repo(root: Path, *, infra_helper: bool) -> tuple[Path, str, str, dict]:
    repo = root / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True,
                   stdout=subprocess.DEVNULL)
    git(repo, "config", "user.name", "synthetic")
    git(repo, "config", "user.email", "synthetic@example.invalid")
    lane = "o26-sort4-body-r21"
    entry = "research/challenge-8/cloud-build/run-o26-sort4-body-r21.sh"
    helper = "research/challenge-8/cloud-build/sort4-caller-entry-native/a1-entry-r21.py"
    proof = "research/challenge-8/synthetic-profile.json"
    recipe = {
        "schema": "smallsort-cloud-recipe-v1", "lane": lane,
        "source_transport_codec": "utf8-xz-envelope-v1",
        "entrypoint": entry, "proof_paths": [proof],
        "infra_paths": sorted([entry, helper]),
        "infra_transport": "exact-recipe-v1",
    }
    for relative in SOURCE_INPUT.EXACT_INFRA_CORE:
        write(repo, relative)
    write(repo, entry, b"#!/bin/bash\n")
    if infra_helper:
        write(repo, helper, b"infra role\n")
    write(repo, SOURCE_INPUT.RECIPE_PREFIX + lane + ".json",
          (json.dumps(recipe, sort_keys=True) + "\n").encode())
    infra_sha = commit(repo, "synthetic infra inputs")
    write(repo, proof, b"synthetic proof profile\n")
    if not infra_helper:
        # The same path exists only in the proof commit. It must not satisfy
        # the recipe's infra-role selection from the earlier infra commit.
        write(repo, helper, b"proof role copy\n")
    proof_sha = commit(repo, "synthetic proof inputs")
    return repo, infra_sha, proof_sha, recipe


class BodyRouteRecipeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.recipe = json.loads(RECIPE_PATH.read_text())
        cls.closure = json.loads(CLOSURE_PATH.read_text())
        cls.profile = json.loads((CLOUD / "sort4-caller-entry-native" /
                                  "A1-ACTUAL-BODY-R21-TRANSPORT-PROFILE.json").read_text())

    def test_inactive_recipe_and_closure_roles_are_exact(self):
        recipe = self.recipe
        SOURCE_INPUT.validate_recipe(recipe, recipe["lane"])
        self.assertEqual(recipe["lane"], "o26-sort4-body-r21")
        self.assertEqual(recipe["source_transport_codec"], "utf8-xz-envelope-v1")
        self.assertEqual(recipe["infra_transport"], "exact-recipe-v1")
        self.assertEqual(recipe["proof_paths"], sorted(set(recipe["proof_paths"])))
        self.assertEqual(recipe["infra_paths"], sorted(set(recipe["infra_paths"])))
        self.assertIs(self.profile["cloud_build_enabled"], False)
        self.assertIs(self.profile["profile_accepted"], False)
        self.assertEqual(self.closure["status"], "WORKTREE_STATIC_CLOSURE_UNCOMMITTED")
        self.assertIsNone(self.closure["measured_payload_bytes"])
        self.assertEqual(self.closure["proof_paths"], recipe["proof_paths"])
        self.assertEqual(self.closure["infra_recipe_paths"], recipe["infra_paths"])
        self.assertEqual(self.closure["automatic_exact_infra_core"],
                         list(SOURCE_INPUT.EXACT_INFRA_CORE))
        entry = recipe["entrypoint"]
        self.assertIn(entry, recipe["infra_paths"])
        self.assertIn("research/challenge-8/cloud-build/body-route-r21.py",
                      recipe["infra_paths"])
        self.assertIn("research/challenge-8/cloud-build/sort4-caller-entry-native/a1-runner-r21.py",
                      recipe["infra_paths"])
        self.assertIn("research/challenge-8/cloud-build/sort4-caller-entry-native/driver.py",
                      recipe["infra_paths"])
        self.assertIn("research/challenge-8/cloud-build/sort4-caller-entry-native/a1-entry-r21.py",
                      recipe["infra_paths"])
        self.assertNotIn("research/challenge-8/cloud-build/sort4-caller-entry-native/a1-entry-r21.py",
                         recipe["proof_paths"])
        self.assertIn("research/challenge-8/cloud-build/o26-refresh-recipe.py",
                      recipe["infra_paths"])
        shell = (REPO / recipe["entrypoint"]).read_text()
        self.assertIn('python3 "$cloud_dir/sort4-caller-entry-native/a1-entry-r21.py"', shell)
        self.assertNotIn('python3 "$proof_root/research/challenge-8/cloud-build/sort4-caller-entry-native/a1-entry-r21.py"', shell)
        self.assertEqual(self.closure["runner_script_sha256"],
                         hashlib.sha256(shell.encode()).hexdigest())

    def test_every_selected_working_tree_path_exists(self):
        for relative in (*self.recipe["proof_paths"], *self.recipe["infra_paths"]):
            self.assertTrue((REPO / relative).is_file(), relative)

    def test_all_profile_body_and_standard_source_pins_are_selected(self):
        proof = set(self.recipe["proof_paths"])
        body_dir = "research/challenge-8/cloud-build/sort4-caller-entry-native/"
        self.assertIn(body_dir + "A1-ACTUAL-BODY-R21-TRANSPORT-PROFILE.json", proof)
        for name in self.profile["actual_body_dependencies_sha256"]:
            relative = ("research/challenge-8/overnight-sort4/capture.py" if name == "capture.py"
                        else body_dir + name)
            self.assertIn(relative, proof, name)
        for relative in self.profile["std_source_sha256"]:
            self.assertIn(relative, proof, relative)
        for name in ("a1-actual-body-r21.py", "a1-tool-r21.py",
                     "a1-cleanup-helper.py", "a1-ghost-grammar.py",
                     "a1-fixtures.py", "a1-ast-gates.py",
                     "a1-reference-own-probe-r17.py"):
            self.assertIn(body_dir + name, proof, name)

    def test_manifest_and_selected_runtime_patch_closures_are_complete(self):
        proof = set(self.recipe["proof_paths"])
        manifest = json.loads((CHALLENGE / "overnight-linkage/O26-PROFILE-MANIFEST.json").read_text())
        refresh = json.loads((CHALLENGE / "overnight-assume-actual/O26-REFRESH-PROFILE.json").read_text())
        for row in manifest["patches_in_application_order"]:
            self.assertIn("research/challenge-8/" + row["path"], proof, row["path"])
        for row in refresh["refresh_patches"]:
            self.assertIn("research/challenge-8/" + row["path"], proof, row["path"])

        runtime_path = CLOUD / "sort4-caller-entry-native/selected-runtime.py"
        tree = ast.parse(runtime_path.read_text())
        rows = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                    isinstance(target, ast.Name) and target.id == "PATCHES"
                    for target in node.targets):
                rows = ast.literal_eval(node.value)
        self.assertIsNotNone(rows)
        for profile_rel, _field, patch_rel, _base, _result in rows:
            def repo_path(relative: str) -> str:
                return "research/challenge-8/" + relative
            self.assertIn(repo_path(profile_rel), proof)
            self.assertIn(repo_path(patch_rel), proof)

    def test_dead_generic_and_selected_prefix_paths_are_excluded(self):
        paths = set(self.recipe["proof_paths"]) | set(self.recipe["infra_paths"])
        for name in ("a1-runner.py", "selected-proof.py", "a1-tool.py",
                     "a1-tool-r17.py", "a1-actual-body-r17.py",
                     "A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json"):
            self.assertFalse(any(Path(path).name == name for path in paths), name)
        excluded = {row["path"] for row in self.closure["excluded"]}
        for name in ("a1-runner.py", "selected-proof.py", "a1-tool.py",
                     "a1-tool-r17.py", "a1-actual-body-r17.py"):
            self.assertTrue(any(Path(path).name == name for path in excluded), name)
        loaded = {"a1-ast-gates.py", "a1-fixtures.py", "a1-tool-r21.py"}
        for name in self.profile["a1_helper_sha256"]:
            relative = "research/challenge-8/cloud-build/sort4-caller-entry-native/" + name
            if name in loaded:
                self.assertIn(relative, paths, name)
            else:
                self.assertNotIn(relative, paths, name)

    def test_source_input_selects_the_committed_recipe_and_refuses_wrong_role(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, infra_sha, proof_sha, recipe = tiny_repo(root, infra_helper=True)
            payload_bytes = SOURCE_INPUT.make_payload(repo, infra_sha, proof_sha,
                                                      recipe["lane"])
            payload, _ = SOURCE_INPUT.decode_payload(payload_bytes)
            infra_paths = [row["path"] for row in payload["infra"]["paths"]]
            proof_paths = [row["path"] for row in payload["proof"]["paths"]]
            expected_infra = sorted(set(SOURCE_INPUT.EXACT_INFRA_CORE +
                                        tuple(recipe["infra_paths"]) +
                                        (SOURCE_INPUT.RECIPE_PREFIX + recipe["lane"] + ".json",)))
            self.assertEqual(infra_paths, expected_infra)
            self.assertEqual(proof_paths, recipe["proof_paths"])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo, infra_sha, proof_sha, recipe = tiny_repo(root, infra_helper=False)
            with self.assertRaisesRegex(SystemExit, "missing or duplicated committed tree entry"):
                SOURCE_INPUT.make_payload(repo, infra_sha, proof_sha, recipe["lane"])


if __name__ == "__main__":
    unittest.main()
