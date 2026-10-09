#!/usr/bin/env python3
"""Build and restore a small, credential-free archive of committed inputs.

Only Git objects reachable from the explicit commits and selected committed
paths enter the payload. The index and working tree are never read.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys


SCHEMA = "smallsort-git-source-input-v1"
SHARED_SCHEMA = "smallsort-git-source-input-v2-shared-objects"
OBJECT_ID = re.compile(r"^[0-9a-f]{40}$")
WORKSPACE = Path("/workspace")
STD_PATHS = (
    "library/core/src/mem/mod.rs",
    "library/core/src/mem/manually_drop.rs",
    "library/core/src/mem/maybe_uninit.rs",
    "library/core/src/mem/maybe_dangling.rs",
    "library/core/src/ptr/mod.rs",
    "library/core/src/hint.rs",
    "library/core/src/slice/sort/shared/smallsort.rs",
)
STOCK_PATHS = (
    "research/challenge-8/check-stock-2610.py",
    "research/challenge-8/check-forget-generic.py",
    "research/challenge-8/forget-evidence-classifier.py",
    *STD_PATHS,
)
CONSTRUCTOR_PATHS = (
    *STOCK_PATHS,
    "research/challenge-8/overnight-s6/check-maybeuninit-new-pointer.py",
    "research/challenge-8/overnight-s6/prepare-and-check-sort4-select.py",
    "research/challenge-8/overnight-s6/verifast-s6-26.10-candidate.patch",
    "research/challenge-8/verifast-manuallydrop-new-cfg-2610.patch",
    "research/challenge-8/rust-fieldless-layout-controls/positive_c_nonempty.c",
    "research/challenge-8/rust-fieldless-layout-controls/positive_cpp_empty.cpp",
)
INFRA_EXACT_PATHS = (
    "research/challenge-8/cloud-build/run-proof.sh",
)
EXACT_INFRA_TRANSPORT = "exact-recipe-v1"
EXACT_INFRA_CORE = (
    *INFRA_EXACT_PATHS,
    "research/challenge-8/cloud-build/control.py",
    "research/challenge-8/cloud-build/coordination.py",
    "research/challenge-8/cloud-build/exact-infra-transport-controls.py",
    "research/challenge-8/cloud-build/package-evidence.py",
    "research/challenge-8/cloud-build/provider.py",
    "research/challenge-8/cloud-build/source-input.py",
    "research/challenge-8/cloud-build/verify-evidence.py",
)
RECIPE_PREFIX = "research/challenge-8/cloud-build/recipes/"
INFRA_PYTHON_PREFIXES = (
    "research/challenge-8/cloud-build/",
    "research/challenge-8/cloud-build/overlays/",
)


def stop(message: str) -> "NoReturn":
    raise SystemExit(message)


def valid_path(value: str) -> str:
    path = PurePosixPath(value)
    if (not value or path.is_absolute() or "\\" in value or
            str(path) != value or any(part in ("", ".", "..") for part in path.parts)):
        stop(f"invalid repository path: {value!r}")
    return value


def git(repo: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    result = subprocess.run(["git", "-C", str(repo), *args], input=input_bytes,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            check=False)
    if result.returncode:
        stop(f"git {' '.join(args)} failed: {result.stderr.decode(errors='replace').strip()}")
    return result.stdout


def git_oid(kind: str, data: bytes) -> str:
    return hashlib.sha1(f"{kind} {len(data)}\0".encode() + data).hexdigest()


def read_object(repo: Path, kind: str, oid: str) -> bytes:
    if git(repo, "cat-file", "-t", oid).decode().strip() != kind:
        stop(f"unexpected object type for {oid}; expected {kind}")
    data = git(repo, "cat-file", kind, oid)
    if git_oid(kind, data) != oid:
        stop(f"Git object identity check failed: {oid}")
    return data


def tree_entries(data: bytes) -> list[tuple[str, str, str]]:
    entries = []
    offset = 0
    valid_modes = {b"40000", b"100644", b"100755", b"120000", b"160000"}
    while offset < len(data):
        space = data.find(b" ", offset)
        if space < 0:
            stop("truncated Git tree mode")
        mode = data[offset:space]
        if mode not in valid_modes:
            stop(f"invalid Git tree mode: {mode!r}")
        nul = data.find(b"\0", space + 1)
        if nul < 0:
            stop("truncated Git tree entry name")
        name_bytes = data[space + 1:nul]
        if not name_bytes or b"/" in name_bytes or name_bytes in (b".", b".."):
            stop("invalid Git tree entry name")
        oid_start = nul + 1
        oid_end = oid_start + 20
        if oid_end > len(data):
            stop("truncated Git tree object ID")
        try:
            name = name_bytes.decode("utf-8")
            mode_text = mode.decode("ascii")
        except UnicodeDecodeError:
            stop("non-UTF-8 path or non-ASCII mode in Git tree")
        entries.append((mode_text, name, data[oid_start:oid_end].hex()))
        offset = oid_end
    return entries


def child(repo: Path, tree_oid: str, name: str) -> tuple[str, str, str]:
    rows = [row for row in tree_entries(read_object(repo, "tree", tree_oid))
            if row[1] == name]
    if len(rows) != 1:
        stop(f"missing or duplicated committed tree entry: {name}")
    return rows[0]


def root_tree_of(repo: Path, commit: str) -> str:
    data = read_object(repo, "commit", commit)
    line = next((row for row in data.split(b"\n") if row.startswith(b"tree ")), None)
    if line is None:
        stop(f"commit has no root tree: {commit}")
    return line[5:].decode("ascii")


def committed_path(repo: Path, root_tree: str, path: str,
                   objects: dict[str, tuple[str, bytes]]) -> dict:
    parts = valid_path(path).split("/")
    tree_oid = root_tree
    for name in parts[:-1]:
        mode, _, tree_oid = child(repo, tree_oid, name)
        if mode != "40000":
            stop(f"selected path ancestor is not a tree: {path}")
        objects[tree_oid] = ("tree", read_object(repo, "tree", tree_oid))
    mode, _, blob_oid = child(repo, tree_oid, parts[-1])
    if mode not in ("100644", "100755"):
        stop(f"selected path is not a regular committed file: {path} ({mode})")
    blob = read_object(repo, "blob", blob_oid)
    objects[blob_oid] = ("blob", blob)
    return {"path": path, "mode": mode, "oid": blob_oid,
            "sha256": hashlib.sha256(blob).hexdigest(), "size": len(blob)}


def list_committed_tree(repo: Path, root_tree: str, prefix: str,
                        objects: dict[str, tuple[str, bytes]]) -> list[str]:
    tree_oid = root_tree
    for name in prefix.rstrip("/").split("/"):
        mode, _, tree_oid = child(repo, tree_oid, name)
        if mode != "40000":
            stop(f"expected directory in committed tree: {prefix}")
        objects[tree_oid] = ("tree", read_object(repo, "tree", tree_oid))
    result = []
    for mode, name, oid in tree_entries(read_object(repo, "tree", tree_oid)):
        if mode in ("100644", "100755") and name.endswith(".py"):
            result.append(prefix.rstrip("/") + "/" + name)
            objects[oid] = ("blob", read_object(repo, "blob", oid))
    return result


def infra_paths(repo: Path, commit: str) -> list[str]:
    root = root_tree_of(repo, commit)
    objects: dict[str, tuple[str, bytes]] = {}
    paths = list(INFRA_EXACT_PATHS)
    for prefix in INFRA_PYTHON_PREFIXES:
        paths.extend(list_committed_tree(repo, root, prefix, objects))
    return sorted(set(valid_path(path) for path in paths))


def validate_recipe(recipe: dict, lane: str) -> dict:
    if recipe.get("schema") != "smallsort-cloud-recipe-v1" or recipe.get("lane") != lane:
        stop("recipe schema/lane mismatch")
    transport = recipe.get("infra_transport")
    if transport is not None and transport != EXACT_INFRA_TRANSPORT:
        stop("unknown recipe infrastructure transport policy")
    for key in ("proof_paths", "infra_paths"):
        paths = recipe.get(key)
        if not isinstance(paths, list) or not paths or paths != sorted(set(paths)):
            stop(f"recipe {key} must be a nonempty sorted exact path list")
        for path in paths:
            valid_path(path)
            if not path.startswith(("research/challenge-8/", "library/core/")):
                stop("recipe input outside research/std scope")
    entrypoint = valid_path(recipe.get("entrypoint", ""))
    if entrypoint not in recipe["infra_paths"] or not entrypoint.startswith("research/challenge-8/cloud-build/") or not entrypoint.endswith(".sh"):
        stop("recipe entrypoint must be an explicit infrastructure shell input")
    if transport == EXACT_INFRA_TRANSPORT and not all(
            path.startswith("research/challenge-8/cloud-build/")
            for path in recipe["infra_paths"]):
        stop("exact recipe infrastructure input outside Cloud module tree")
    if "baseline_sha" in recipe:
        if not OBJECT_ID.fullmatch(recipe["baseline_sha"]):
            stop("recipe baseline SHA must be full")
        paths = recipe.get("baseline_paths")
        if not isinstance(paths, list) or not paths or paths != sorted(set(paths)):
            stop("recipe baseline_paths must be exact sorted paths")
        for path in paths:
            valid_path(path)
            if not path.startswith(("research/challenge-8/", "library/core/")):
                stop("baseline input outside research/std scope")
    elif "baseline_paths" in recipe:
        stop("baseline paths without original SHA")
    return recipe


def committed_recipe(repo: Path, infra_sha: str, lane: str) -> dict:
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", lane):
        stop("invalid recipe lane")
    raw = git(repo, "show", infra_sha + ":" + RECIPE_PREFIX + lane + ".json")
    return validate_recipe(json.loads(raw), lane)


def repo_record(repo: Path, commit: str, paths: list[str]) -> tuple[dict, dict[str, tuple[str, bytes]]]:
    if not OBJECT_ID.fullmatch(commit):
        stop(f"commit must be a full 40-digit SHA-1: {commit}")
    commit_data = read_object(repo, "commit", commit)
    root_tree = root_tree_of(repo, commit)
    objects: dict[str, tuple[str, bytes]] = {
        commit: ("commit", commit_data),
        root_tree: ("tree", read_object(repo, "tree", root_tree)),
    }
    selected = [committed_path(repo, root_tree, path, objects)
                for path in sorted(set(paths))]
    record = {"commit": commit, "root_tree": root_tree, "paths": selected,
              "objects": [
                  {"oid": oid, "type": kind, "size": len(data),
                   "data_base64": base64.b64encode(data).decode("ascii")}
                  for oid, (kind, data) in sorted(objects.items())
              ]}
    return record, objects


def make_payload(repo: Path, infra_sha: str, proof_sha: str, lane: str) -> bytes:
    """Return deterministic gzip JSON for the requested source commits."""
    repo = repo.resolve()
    recipe = None if lane in ("stock", "constructor") else committed_recipe(repo, infra_sha, lane)
    if recipe and recipe.get("infra_transport") == EXACT_INFRA_TRANSPORT:
        selected_infra = sorted(set(EXACT_INFRA_CORE + tuple(recipe["infra_paths"]) +
                                    (RECIPE_PREFIX + lane + ".json",)))
    else:
        selected_infra = infra_paths(repo, infra_sha)
    if recipe and recipe.get("infra_transport") != EXACT_INFRA_TRANSPORT:
        selected_infra = sorted(set(selected_infra + recipe["infra_paths"] + [RECIPE_PREFIX + lane + ".json"]))
    infra, _ = repo_record(repo, infra_sha, selected_infra)
    proof_paths = recipe["proof_paths"] if recipe else STOCK_PATHS if lane == "stock" else CONSTRUCTOR_PATHS
    proof, _ = repo_record(repo, proof_sha, list(proof_paths))
    payload = {"schema": SCHEMA, "lane": lane,
               "infra": infra, "proof": proof}
    if recipe:
        payload["recipe"] = recipe
        if "baseline_sha" in recipe:
            payload["baseline"], _ = repo_record(repo, recipe["baseline_sha"], recipe["baseline_paths"])
        # Transfer each original object once; every original repo keeps its closure.
        # Recipes without a historical baseline use the same bounded encoding.
        pool = {}
        for name in ("infra", "proof", "baseline"):
            if name not in payload:
                continue
            record = payload[name]
            for item in record["objects"]:
                oid = item["oid"]
                if oid in pool and pool[oid] != item:
                    stop("same object ID has inconsistent source records")
                pool[oid] = item
            record["objects"] = [{"oid": item["oid"]} for item in record["objects"]]
        payload["schema"] = SHARED_SCHEMA
        payload["shared_objects"] = []
        for oid in sorted(pool):
            item = dict(pool[oid])
            raw_object = base64.b64decode(item["data_base64"], validate=True)
            item["data_base64"] = base64.b64encode(gzip.compress(raw_object, mtime=0)).decode("ascii")
            item["compression"] = "gzip"
            payload["shared_objects"].append(item)
    raw = (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode="wb", filename="",
                       compresslevel=9, mtime=0) as stream:
        stream.write(raw)
    return buffer.getvalue()


def expected_infra_paths(repo_record_data: dict, recipe: dict | None = None) -> list[str]:
    # Validate the exact narrow path policy without consulting a worktree.
    paths = [item.get("path") for item in repo_record_data.get("paths", [])]
    if recipe and recipe.get("infra_transport") == EXACT_INFRA_TRANSPORT:
        expected = sorted(set(EXACT_INFRA_CORE + tuple(recipe["infra_paths"]) +
                              (RECIPE_PREFIX + recipe["lane"] + ".json",)))
        if paths != expected:
            stop("exact recipe infrastructure path set differs")
        if any(item.get("mode") not in ("100644", "100755")
               for item in repo_record_data.get("paths", [])):
            stop("exact recipe infrastructure input is not a regular file")
        return expected
    def allowed_python(path: str) -> bool:
        for prefix in INFRA_PYTHON_PREFIXES:
            remainder = path.removeprefix(prefix)
            if path.startswith(prefix) and remainder.endswith(".py") and "/" not in remainder:
                return True
        return False

    recipe_paths = set(recipe["infra_paths"] + [RECIPE_PREFIX + recipe["lane"] + ".json"]) if recipe else set()
    expected = [path for path in paths if path in INFRA_EXACT_PATHS or allowed_python(path) or path in recipe_paths]
    if sorted(set(expected)) != sorted(paths):
        stop("bundle contains an unapproved infra path")
    if not set(INFRA_EXACT_PATHS).issubset(expected):
        stop("bundle is missing an infra runner path")
    if not recipe_paths.issubset(expected):
        stop("bundle is missing recipe infrastructure inputs")
    return sorted(expected)


def expected_proof_paths(lane: str) -> list[str]:
    if lane == "stock":
        return sorted(STOCK_PATHS)
    if lane == "constructor":
        return sorted(CONSTRUCTOR_PATHS)
    stop(f"unsupported archive lane: {lane}")


def ensure_workspace(path: Path) -> None:
    resolved = path.resolve()
    if resolved != WORKSPACE and WORKSPACE not in resolved.parents:
        stop(f"restore path must be within {WORKSPACE}: {resolved}")


def restore_repo(record: dict, destination: Path, allowed_paths: list[str]) -> list[dict]:
    commit = record.get("commit")
    if not isinstance(commit, str) or not OBJECT_ID.fullmatch(commit):
        stop("invalid commit in source archive")
    selected = record.get("paths")
    if not isinstance(selected, list) or [item.get("path") for item in selected] != allowed_paths:
        stop("archive paths do not match lane allowlist")
    if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
        stop(f"restore destination must be a real directory: {destination}")
    if destination.exists() and any(destination.iterdir()):
        stop(f"restore destination must be empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "--quiet", "--object-format=sha1", str(destination)], check=True)
    object_ids = set()
    for item in record.get("objects", []):
        oid, kind = item.get("oid"), item.get("type")
        if not isinstance(oid, str) or not OBJECT_ID.fullmatch(oid) or kind not in ("commit", "tree", "blob"):
            stop("invalid Git object record")
        if oid in object_ids:
            stop(f"duplicate Git object record: {oid}")
        object_ids.add(oid)
        try:
            data = base64.b64decode(item.get("data_base64", ""), validate=True)
            if item.get("compression") == "gzip":
                data = gzip.decompress(data)
            elif item.get("compression") is not None:
                stop(f"unsupported Git object compression: {oid}")
        except (ValueError, TypeError, OSError, EOFError):
            stop(f"invalid base64 for Git object {oid}")
        if len(data) != item.get("size") or git_oid(kind, data) != oid:
            stop(f"Git object identity check failed: {oid}")
        stored = subprocess.run(
            ["git", "-C", str(destination), "hash-object", "-w", "-t", kind, "--stdin"],
            input=data, stdout=subprocess.PIPE, check=True).stdout.decode().strip()
        if stored != oid:
            stop(f"Git stored unexpected object ID: {oid}")
    commit_tree = root_tree_of(destination, commit)
    if commit_tree != record.get("root_tree"):
        stop(f"commit root tree mismatch in {destination}")
    required_oids = {commit, commit_tree}
    git(destination, "update-ref", "refs/heads/source-input", commit)
    git(destination, "symbolic-ref", "HEAD", "refs/heads/source-input")
    restored = []
    for item in selected:
        path = valid_path(item["path"])
        tree_oid = commit_tree
        parts = path.split("/")
        for component in parts[:-1]:
            mode, _, tree_oid = child(destination, tree_oid, component)
            if mode != "40000":
                stop(f"restored ancestor is not a tree: {path}")
            required_oids.add(tree_oid)
        mode, _, oid = child(destination, tree_oid, parts[-1])
        required_oids.add(oid)
        if mode != item.get("mode") or oid != item.get("oid"):
            stop(f"committed path mode/OID differs: {path}")
        content = git(destination, "show", f"{commit}:{path}")
        if (git_oid("blob", content) != oid or
                hashlib.sha256(content).hexdigest() != item.get("sha256") or
                len(content) != item.get("size")):
            stop(f"committed path bytes differ: {path}")
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(0o755 if mode == "100755" else 0o644)
        restored.append({"path": path, "mode": mode, "oid": oid,
                         "sha256": item["sha256"], "size": len(content)})
    if object_ids != required_oids:
        stop(f"Git object closure differs from selected inputs in {destination}")
    return restored


def restore_archive(archive: Path, evidence: Path) -> dict:
    ensure_workspace(archive)
    ensure_workspace(evidence)
    compressed = archive.read_bytes()
    try:
        raw = gzip.decompress(compressed)
        payload = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        stop(f"source archive is unreadable: {error}")
    if payload.get("schema") not in (SCHEMA, SHARED_SCHEMA):
        stop("unsupported source archive schema")
    if payload["schema"] == SHARED_SCHEMA:
        pool = {}
        for item in payload.get("shared_objects", []):
            oid = item.get("oid")
            if not isinstance(oid, str) or not OBJECT_ID.fullmatch(oid) or oid in pool:
                stop("invalid or duplicated shared Git object")
            pool[oid] = item
        referenced = set()
        for name in ("infra", "proof", *(("baseline",) if "baseline" in payload else ())):
            record = payload.get(name)
            if not isinstance(record, dict):
                stop("shared schema requires both original input repositories")
            expanded = []
            for ref in record.get("objects", []):
                if set(ref) != {"oid"} or ref["oid"] not in pool:
                    stop("invalid shared-object reference")
                referenced.add(ref["oid"])
                expanded.append(pool[ref["oid"]])
            record["objects"] = expanded
        if referenced != set(pool):
            stop("shared Git object pool differs from repository closure union")
    elif "shared_objects" in payload:
        stop("unexpected shared Git object pool")
    lane = payload.get("lane")
    infra_record = payload.get("infra", {})
    proof_record_data = payload.get("proof", {})
    if os.environ.get("LANE") != lane:
        stop("archive lane differs from explicit LANE environment")
    if os.environ.get("INFRA_SHA") != infra_record.get("commit"):
        stop("infra commit differs from explicit INFRA_SHA environment")
    if os.environ.get("PROOF_SHA") != proof_record_data.get("commit"):
        stop("proof commit differs from explicit PROOF_SHA environment")
    recipe = None if lane in ("stock", "constructor") else validate_recipe(payload.get("recipe", {}), lane)
    infra_paths_allowed = expected_infra_paths(infra_record, recipe)
    proof_paths_allowed = recipe["proof_paths"] if recipe else expected_proof_paths(lane)
    if [item.get("path") for item in proof_record_data.get("paths", [])] != proof_paths_allowed:
        stop("proof archive paths do not match lane allowlist")
    infra_dir, proof_dir = WORKSPACE / "infra", WORKSPACE / "proof"
    infra_restored = restore_repo(infra_record, infra_dir, infra_paths_allowed)
    if recipe:
        restored_recipe = json.loads((infra_dir / (RECIPE_PREFIX + lane + ".json")).read_bytes())
        if restored_recipe != recipe:
            stop("recipe differs from original infrastructure Git object")
    proof_restored = restore_repo(proof_record_data, proof_dir, proof_paths_allowed)
    baseline_restored = None
    if recipe and "baseline_sha" in recipe:
        baseline_record = payload.get("baseline", {})
        if baseline_record.get("commit") != recipe["baseline_sha"]:
            stop("baseline commit differs from recipe")
        baseline_restored = restore_repo(baseline_record, WORKSPACE / "baseline", recipe["baseline_paths"])
    elif "baseline" in payload:
        stop("unexpected baseline repository")
    evidence.mkdir(parents=True, exist_ok=True)
    saved_archive = evidence / "source-input.gz"
    saved_archive.write_bytes(compressed)
    record = {
        "schema": payload["schema"], "lane": lane,
        "archive_sha256": hashlib.sha256(compressed).hexdigest(),
        "archive_size": len(compressed),
        "payload_sha256": hashlib.sha256(raw).hexdigest(),
        "infra": {"commit": infra_record["commit"],
                  "root_tree": infra_record["root_tree"],
                  "restored_paths": infra_restored,
                  "head": git(infra_dir, "rev-parse", "HEAD").decode().strip()},
        "proof": {"commit": proof_record_data["commit"],
                  "root_tree": proof_record_data["root_tree"],
                  "restored_paths": proof_restored,
                  "head": git(proof_dir, "rev-parse", "HEAD").decode().strip()},
        "archive_copy": str(saved_archive),
    }
    if recipe:
        record["recipe"] = recipe
    if baseline_restored is not None:
        record["baseline"] = {"commit": recipe["baseline_sha"], "root_tree": payload["baseline"]["root_tree"], "restored_paths": baseline_restored,
                              "head": git(WORKSPACE / "baseline", "rev-parse", "HEAD").decode().strip()}
    (evidence / "source-input-certificate.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"lane": lane, "archive_sha256": record["archive_sha256"],
                      "infra_head": record["infra"]["head"],
                      "proof_head": record["proof"]["head"]}, sort_keys=True))
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    restore = subparsers.add_parser("restore")
    restore.add_argument("--archive", type=Path, required=True)
    restore.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    restore_archive(args.archive.resolve(), args.evidence.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
