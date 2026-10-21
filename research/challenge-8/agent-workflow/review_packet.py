#!/usr/bin/env python3
"""Create and verify bounded, committed-source review packets (no proof credit)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import selectors
import subprocess
import sys
import time
from typing import Any


SCHEMA = "smallsort-review-spec-v1"
MAX_SPEC = 8192
MAX_REVIEWER = 8192
MAX_PRIOR = 64 * 1024
MAX_PRIORS = 32
MAX_PRIOR_TOTAL = 256 * 1024
MAX_GIT_STDOUT = 4 * 1024 * 1024
MAX_GIT_STDERR = 8 * 1024
MAX_GIT_SECONDS = 30
MAX_TREE_ENTRIES = 100_000
MAX_CHANGED_NAME_BYTES = 1024 * 1024
MAX_CHANGED_PATHS = 10_000
MAX_DIFF = 512 * 1024
MAX_DEP = 1024 * 1024
MAX_DEPS = 4 * 1024 * 1024
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
SPEC_KEYS = {"schema", "worktree", "baseline_commit", "candidate_commit", "defect",
             "applicability", "invariants", "controls", "dependencies", "prior_reviews",
             "known_limitations"}


class ReviewPacketError(ValueError):
    pass


def _json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git(root: Path, *args: str, binary: bool = False, limit: int = MAX_GIT_STDOUT) -> bytes | str:
    env = dict(os.environ)
    env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                "GIT_OPTIONAL_LOCKS": "0", "GIT_PAGER": "cat"})
    command = ["git", "-C", str(root), "-c", "core.hooksPath=/dev/null",
               "-c", "diff.renames=false", *args]
    try:
        proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    except OSError as e:
        raise ReviewPacketError(f"cannot run git: {e}") from None
    assert proc.stdout is not None and proc.stderr is not None
    selector = selectors.DefaultSelector()
    stdout_data = bytearray()
    stderr_data = bytearray()
    stderr_truncated = False
    stdout_open = stderr_open = True
    deadline = time.monotonic() + MAX_GIT_SECONDS
    try:
        for stream, label in ((proc.stdout, "stdout"), (proc.stderr, "stderr")):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, label)
        while stdout_open or stderr_open:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ReviewPacketError(f"git {' '.join(args)} exceeded {MAX_GIT_SECONDS}s timeout")
            events = selector.select(min(remaining, 1.0))
            if not events and proc.poll() is not None:
                # Pipe EOF is still reported by selector; keep selecting until both drain.
                continue
            for key, _ in events:
                stream = key.fileobj
                label = key.data
                chunk = os.read(stream.fileno(), 65536)
                if not chunk:
                    selector.unregister(stream)
                    if label == "stdout":
                        stdout_open = False
                    else:
                        stderr_open = False
                    continue
                if label == "stdout":
                    stdout_data.extend(chunk)
                    if len(stdout_data) > limit:
                        raise ReviewPacketError(f"git output exceeds {limit} byte limit")
                else:
                    room = MAX_GIT_STDERR - len(stderr_data)
                    if room > 0:
                        stderr_data.extend(chunk[:room])
                    if len(chunk) > room:
                        stderr_truncated = True
        try:
            returncode = proc.wait(timeout=max(0.01, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            raise ReviewPacketError(f"git {' '.join(args)} exceeded {MAX_GIT_SECONDS}s timeout") from None
    except Exception:
        if proc.poll() is None:
            proc.kill()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        raise
    finally:
        selector.close()
        proc.stdout.close()
        proc.stderr.close()
    if returncode:
        detail = stderr_data.decode("utf-8", "replace").strip()
        if stderr_truncated:
            detail += " [stderr truncated at 8192 bytes]"
        raise ReviewPacketError(f"git {' '.join(args)} failed: {detail}")
    output = bytes(stdout_data)
    if binary:
        return output
    try:
        return output.decode("utf-8", "strict").strip()
    except UnicodeDecodeError as e:
        raise ReviewPacketError(f"git {' '.join(args)} returned invalid UTF-8 at byte {e.start}") from None


def _no_symlink_ancestors(path: Path, field: str) -> None:
    path = Path(os.path.abspath(path))
    cur = Path(path.anchor)
    for part in path.parts[1:]:
        cur = cur / part
        try:
            if cur.is_symlink():
                raise ReviewPacketError(f"{field} has symlink ancestor: {cur}")
        except OSError as e:
            raise ReviewPacketError(f"cannot inspect {field} path {cur}: {e}") from None


def _read_regular(path: Path, limit: int, field: str) -> bytes:
    _no_symlink_ancestors(path, field)
    try:
        st = path.stat(follow_symlinks=False)
        if not path.is_file() or st.st_size > limit:
            raise ReviewPacketError(f"{field} must be a regular file no larger than {limit} bytes: {path}")
        with path.open("rb") as stream:
            data = stream.read(limit + 1)
    except OSError as e:
        raise ReviewPacketError(f"cannot read {field} {path}: {e}") from None
    if len(data) > limit:
        raise ReviewPacketError(f"{field} exceeds {limit} byte limit: {path}")
    return data


def _path(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise ReviewPacketError(f"{where} must be a repository-relative POSIX path")
    p = PurePosixPath(value)
    raw_parts = value.split("/")
    if (p.is_absolute() or not p.parts or any(x in ("", ".", "..") for x in raw_parts)
            or ":" in p.parts[0] or any(c in value for c in "*?[]")):
        raise ReviewPacketError(f"unsafe {where}: {value!r}")
    return p.as_posix()


def _narrative(value: Any, field: str, *, list_ok: bool = False) -> Any:
    if list_ok:
        if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
            raise ReviewPacketError(f"{field} must be a non-empty list of non-empty strings")
        return [x.strip() for x in value]
    if not isinstance(value, str) or not value.strip():
        raise ReviewPacketError(f"{field} must be a non-empty string")
    return value.strip()


def _validate(spec: Any) -> dict[str, Any]:
    if not isinstance(spec, dict) or set(spec) != SPEC_KEYS:
        if not isinstance(spec, dict):
            raise ReviewPacketError("spec must be a JSON object")
        raise ReviewPacketError(f"spec keys mismatch; missing={sorted(SPEC_KEYS-set(spec))}, extra={sorted(set(spec)-SPEC_KEYS)}")
    s = dict(spec)
    if s["schema"] != SCHEMA:
        raise ReviewPacketError(f"schema must be {SCHEMA}")
    if not isinstance(s["worktree"], str) or not Path(s["worktree"]).is_absolute():
        raise ReviewPacketError("worktree must be an absolute path")
    for k in ("baseline_commit", "candidate_commit"):
        if not isinstance(s[k], str) or not SHA_RE.fullmatch(s[k]):
            raise ReviewPacketError(f"{k} must be a full lowercase commit SHA")
    for k in ("defect", "applicability"):
        s[k] = _narrative(s[k], k)
    for k in ("invariants", "controls", "known_limitations"):
        s[k] = _narrative(s[k], k, list_ok=True)
    if sum(len(x.encode("utf-8")) for x in [s["defect"], s["applicability"], *s["invariants"], *s["controls"], *s["known_limitations"]]) > MAX_SPEC:
        raise ReviewPacketError("reviewer narrative exceeds 8 KiB")
    if not isinstance(s["dependencies"], list):
        raise ReviewPacketError("dependencies must be a list of exact candidate Git paths")
    deps = [_path(p, "dependency") for p in s["dependencies"]]
    if len(set(deps)) != len(deps):
        raise ReviewPacketError("dependencies contain duplicate paths")
    s["dependencies"] = deps
    if not isinstance(s["prior_reviews"], list) or len(s["prior_reviews"]) > MAX_PRIORS:
        raise ReviewPacketError("prior_reviews must be a list")
    refs = []
    for ref in s["prior_reviews"]:
        if not isinstance(ref, dict) or set(ref) != {"path", "sha256"}:
            raise ReviewPacketError("each prior review must contain exactly path and sha256")
        if not isinstance(ref["path"], str):
            raise ReviewPacketError("prior review path must be absolute")
        p = Path(ref["path"])
        if not p.is_absolute() or not HASH_RE.fullmatch(str(ref["sha256"])):
            raise ReviewPacketError("prior review path must be absolute and sha256 must be full lowercase hex")
        refs.append({"path": str(p), "sha256": ref["sha256"]})
    s["prior_reviews"] = refs
    return s


def _commit(root: Path, sha: str) -> None:
    found = _git(root, "rev-parse", "--verify", f"{sha}^{{commit}}")
    if found != sha:
        raise ReviewPacketError(f"commit does not resolve exactly: {sha}")


def _tree(root: Path, commit: str) -> dict[str, tuple[str, str, str]]:
    raw = _git(root, "ls-tree", "-r", "-z", "--full-tree", commit, binary=True)
    assert isinstance(raw, bytes)
    out: dict[str, tuple[str, str, str]] = {}
    for record in raw.split(b"\0"):
        if not record:
            continue
        meta, pathraw = record.split(b"\t", 1)
        mode, kind, oid = meta.decode("ascii").split(" ")
        try:
            path = pathraw.decode("utf-8", "strict")
        except UnicodeDecodeError:
            raise ReviewPacketError("committed Git path is not UTF-8") from None
        _path(path, "committed path")
        out[path] = mode, kind, oid
        if len(out) > MAX_TREE_ENTRIES:
            raise ReviewPacketError(f"Git tree exceeds {MAX_TREE_ENTRIES} entry limit")
    return out


def _prior(spec: dict[str, Any]) -> list[dict[str, str]]:
    out = []
    total = 0
    for item in spec["prior_reviews"]:
        p = Path(item["path"])
        content = _read_regular(p, MAX_PRIOR, "prior review")
        total += len(content)
        if total > MAX_PRIOR_TOTAL:
            raise ReviewPacketError("prior review references exceed 256 KiB total")
        if _sha(content) != item["sha256"]:
            raise ReviewPacketError(f"prior review reference missing, symlinked, or SHA256 mismatch: {p}")
        out.append(item)
    return out


def _expected(spec: dict[str, Any]) -> dict[str, bytes]:
    worktree = Path(spec["worktree"])
    _no_symlink_ancestors(worktree, "worktree")
    root = worktree.resolve(strict=True)
    if not root.is_dir() or not (root / ".git").exists():
        raise ReviewPacketError("worktree must be a Git worktree")
    base, cand = spec["baseline_commit"], spec["candidate_commit"]
    _commit(root, base); _commit(root, cand)
    if _git(root, "merge-base", "--is-ancestor", base, cand, binary=True) != b"":
        raise ReviewPacketError("baseline_commit must be an ancestor of candidate_commit")
    before, after = _tree(root, base), _tree(root, cand)
    diff = _git(root, "diff", "--binary", "--full-index", "--no-ext-diff", "--no-textconv", "--no-renames",
                "--no-color", base, cand, "--", binary=True, limit=MAX_DIFF)
    assert isinstance(diff, bytes)
    name_raw = _git(root, "diff", "--name-only", "--no-renames", "-z", base, cand, "--",
                    binary=True, limit=MAX_CHANGED_NAME_BYTES)
    assert isinstance(name_raw, bytes)
    try:
        paths = [x.decode("utf-8", "strict") for x in name_raw.split(b"\0") if x]
    except UnicodeDecodeError as e:
        raise ReviewPacketError(f"changed Git path is not UTF-8 at byte {e.start}") from None
    if len(paths) > MAX_CHANGED_PATHS:
        raise ReviewPacketError(f"changed path count exceeds {MAX_CHANGED_PATHS}")
    numstat_raw = _git(root, "diff", "--numstat", "--no-renames", "-z", base, cand, "--", binary=True, limit=MAX_DIFF)
    assert isinstance(numstat_raw, bytes)
    binary_paths = set()
    for row in numstat_raw.split(b"\0"):
        if not row:
            continue
        fields = row.split(b"\t", 2)
        if len(fields) != 3:
            raise ReviewPacketError("git returned malformed diff numstat")
        if fields[0] == b"-" and fields[1] == b"-":
            try:
                binary_paths.add(fields[2].decode("utf-8", "strict"))
            except UnicodeDecodeError:
                raise ReviewPacketError("binary changed path is not UTF-8") from None
    changed = []
    for path in paths:
        _path(path, "changed path")
        old, new = before.get(path), after.get(path)
        entry = {"path": path, "status": "deleted" if new is None else ("added" if old is None else "modified"),
                 "binary": path in binary_paths, "baseline": _tree_entry_sha(root, path, old, "baseline"),
                 "candidate": _tree_entry_sha(root, path, new, "candidate")}
        changed.append(entry)
    total = 0
    deps_meta = []
    files: dict[str, bytes] = {"diff.patch": diff}
    for i, path in enumerate(spec["dependencies"]):
        item = after.get(path)
        if item is None:
            raise ReviewPacketError(f"dependency is absent from candidate commit: {path}")
        mode, kind, oid = item
        if kind != "blob" or mode not in ("100644", "100755"):
            raise ReviewPacketError(f"dependency is not a regular committed file: {path} ({mode} {kind})")
        content = _git(root, "cat-file", "blob", oid, binary=True, limit=MAX_DEP)
        assert isinstance(content, bytes)
        total += len(content)
        if total > MAX_DEPS:
            raise ReviewPacketError("candidate dependency bytes exceed 4 MiB")
        member = f"dependencies/{i:04d}.bin"
        files[member] = content
        deps_meta.append({"path": path, "member": member, "mode": mode, "blob": oid, "size": len(content), "sha256": _sha(content)})
    refs = _prior(spec)
    metadata = {"schema": "smallsort-review-packet-v1", "worktree": str(root),
                "baseline_commit": base, "candidate_commit": cand, "candidate_tree": _git(root, "rev-parse", f"{cand}^{{tree}}"),
                "diff_sha256": _sha(diff), "changed_files": changed, "dependencies": deps_meta,
                "prior_reviews": refs, "proof_credit": "NONE", "review_state": "NOT_REVIEWED"}
    files["metadata.json"] = _json(metadata)
    files["spec.json"] = _json(spec)
    metadata["spec_sha256"] = _sha(files["spec.json"])
    files["metadata.json"] = _json(metadata)
    reviewer = _reviewer(metadata, spec).encode("utf-8")
    if len(reviewer) > MAX_REVIEWER:
        raise ReviewPacketError("rendered reviewer instructions exceed 8 KiB")
    files["reviewer.md"] = reviewer
    inventory = {name: _sha(data) for name, data in sorted(files.items())}
    files["inventory.json"] = _json({"schema": "smallsort-review-inventory-v1", "files": inventory})
    return files


def _tree_entry_sha(root: Path, path: str, item: tuple[str, str, str] | None, side: str) -> dict[str, str] | None:
    if item is None:
        return None
    mode, kind, oid = item
    if kind != "blob" or mode not in ("100644", "100755"):
        raise ReviewPacketError(f"changed {side} path is not a regular committed file: {path} ({mode} {kind})")
    content = _git(root, "cat-file", "blob", oid, binary=True, limit=MAX_DEP)
    assert isinstance(content, bytes)
    return {"mode": mode, "blob": oid, "sha256": _sha(content)}


def _reviewer(meta: dict[str, Any], spec: dict[str, Any]) -> str:
    lines = ["# Bounded candidate review packet", "", "Review the exact committed candidate named below.",
             "This packet is a review handoff only: it grants no proof credit, admission, or authorization.", "",
             f"- Baseline: `{meta['baseline_commit']}`", f"- Candidate: `{meta['candidate_commit']}`",
             f"- Candidate tree: `{meta['candidate_tree']}`", f"- Diff SHA256: `{meta['diff_sha256']}`", "",
             "## Defect", "", spec["defect"], "", "## Applicability", "", spec["applicability"], "",
             "## Invariants", *[f"- {x}" for x in spec["invariants"]], "", "## Required controls",
             *[f"- {x}" for x in spec["controls"]], "", "## Declared dependencies",
             *[f"- `{d['path']}` → `{d['member']}` (mode {d['mode']}, SHA256 {d['sha256']})" for d in meta["dependencies"]],
             "", "## Scope and limitations", "", "The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.",
             "Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.",
             "A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.",
             "Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.", "",
             *[f"- {x}" for x in spec["known_limitations"]], "", "Do not execute source or evidence from this packet. Do not claim new proof credit.", ""]
    return "\n".join(lines)


def _safe_out(out: Path, root: Path) -> Path:
    out = Path(os.path.abspath(out))
    _no_symlink_ancestors(out, "output")
    if out == root or root in out.parents or out in root.parents:
        raise ReviewPacketError("output must be outside the worktree")
    if out.exists():
        raise ReviewPacketError("output directory must be new")
    if not out.parent.is_dir():
        raise ReviewPacketError("output parent must already exist as a directory")
    return out


def create(spec_file: Path, out: Path) -> dict[str, Any]:
    raw = _read_regular(Path(spec_file), MAX_SPEC, "spec")
    try:
        spec = _validate(json.loads(raw.decode("utf-8")))
    except (UnicodeError, json.JSONDecodeError) as e:
        raise ReviewPacketError(f"invalid JSON spec: {e}") from None
    worktree = Path(spec["worktree"])
    _no_symlink_ancestors(worktree, "worktree")
    root = worktree.resolve(strict=True)
    dest = _safe_out(out, root)
    files = _expected(spec)
    dest.mkdir()
    try:
        for name, data in files.items():
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    except Exception:
        # Never replace or modify user data; this directory was created by this call.
        import shutil
        shutil.rmtree(dest)
        raise
    return {"state": "PACKET_CREATED_NOT_REVIEWED", "directory": str(dest), "files": len(files),
            "candidate_commit": spec["candidate_commit"], "spec_sha256": _sha(files["spec.json"]),
            "packet_sha256": _sha(files["inventory.json"]), "proof_credit": "NONE"}


def check(bundle: Path, expect_candidate: str, expect_spec_sha256: str) -> dict[str, Any]:
    bundle = Path(bundle)
    _no_symlink_ancestors(bundle, "bundle")
    if bundle.is_symlink() or not bundle.is_dir():
        raise ReviewPacketError("bundle must be a regular directory")
    if not isinstance(expect_candidate, str) or not SHA_RE.fullmatch(expect_candidate):
        raise ReviewPacketError("expect_candidate must be a full lowercase commit SHA")
    if not isinstance(expect_spec_sha256, str) or not HASH_RE.fullmatch(expect_spec_sha256):
        raise ReviewPacketError("expect_spec_sha256 must be a full lowercase SHA256")
    for p in bundle.rglob("*"):
        if p.is_symlink():
            raise ReviewPacketError(f"bundle contains symlink: {p}")
        if not p.is_dir() and not p.is_file():
            raise ReviewPacketError(f"bundle contains unsupported entry: {p}")
    raw = _read_regular(bundle / "spec.json", MAX_SPEC, "bundled spec")
    try:
        spec = _validate(json.loads(raw.decode("utf-8")))
    except (UnicodeError, json.JSONDecodeError) as e:
        raise ReviewPacketError(f"invalid bundled spec: {e}") from None
    spec_sha256 = _sha(_json(spec))
    if spec["candidate_commit"] != expect_candidate:
        raise ReviewPacketError("bundled candidate does not match --expect-candidate")
    if spec_sha256 != expect_spec_sha256:
        raise ReviewPacketError("bundled spec does not match --expect-spec-sha256")
    expected = _expected(spec)
    actual_names = {p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file()}
    if actual_names != set(expected):
        raise ReviewPacketError(f"bundle file set differs; extra={sorted(actual_names-set(expected))}, missing={sorted(set(expected)-actual_names)}")
    for name, data in expected.items():
        actual = _read_regular(bundle / name, len(data), f"bundle member {name}")
        if actual != data:
            raise ReviewPacketError(f"bundle content does not match committed source/spec: {name}")
    return {"state": "PACKET_VALID_NOT_REVIEWED", "candidate_commit": spec["candidate_commit"],
            "spec_sha256": spec_sha256, "packet_sha256": _sha(expected["inventory.json"]),
            "proof_credit": "NONE", "files": len(expected)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="smallsort-session review")
    sub = parser.add_subparsers(dest="command", required=True)
    p_create = sub.add_parser("create")
    p_create.add_argument("--spec", required=True, type=Path)
    p_create.add_argument("--out", required=True, type=Path)
    p_check = sub.add_parser("check")
    p_check.add_argument("--bundle", required=True, type=Path)
    p_check.add_argument("--expect-candidate", required=True)
    p_check.add_argument("--expect-spec-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        result = create(args.spec, args.out) if args.command == "create" else check(args.bundle, args.expect_candidate, args.expect_spec_sha256)
    except (ReviewPacketError, OSError) as e:
        print(f"review packet error: {e}", file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
