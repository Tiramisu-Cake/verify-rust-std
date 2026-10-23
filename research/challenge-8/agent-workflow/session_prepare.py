#!/usr/bin/env python3
"""Prepare a review bundle for a future SmallSort proof-agent session.

This tool prepares data and checks source closure. It does not register an
authorization with a branch client, reserve a coordinator slot, or dispatch a
Cloud Build. All Git inspection is read-only.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from typing import Any

import checkpoint as cp


SPEC_KEYS = {
    "schema", "task_id", "phase", "owner", "worktree", "branch",
    "baseline_sha", "lane", "t0", "main_minutes", "finish_minutes",
    "cloud_seconds", "max_timeout_seconds", "report_reserve_seconds",
    "profile_path", "recipe_path", "old_ledger_path", "new_ledger_path",
    "new_profile_path", "profile_updates",
}
PHASE_RE = re.compile(r"[A-Z][A-Z0-9-]{0,100}\Z")
NAME_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,100}\Z")
SHA_RE = re.compile(r"[0-9a-f]{40}\Z")
LANE_RE = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
PROTECTED_PROFILE_KEYS = {
    "profile_accepted", "accepted", "proof_credit", "independent_credit",
    "admitted", "admission_record_created", "formal_verification_passed",
    "cloud_build_enabled",
}
# Owners whose first Cloud session may be prepared without an old ledger/profile.
FIRST_SESSION_OWNERS = {"network"}
# Bounds for an explicit task window/budget; defaults remain 120 + 30 minutes and 3600 s.
MAX_MAIN_MINUTES = 10080
MAX_FINISH_MINUTES = 240
MAX_CLOUD_SECONDS = 86400
MAX_BUILD_TIMEOUT = 1740
TERMINAL_STATES = {"SUCCESS", "FAILURE", "INTERNAL_ERROR", "TIMEOUT", "CANCELLED", "EXPIRED"}


class PrepareError(ValueError):
    """Invalid specification, source tree, or prepared bundle."""


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_git(root: Path, *args: str, binary: bool = False) -> bytes | str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"")
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", "replace")
        raise PrepareError(f"git {' '.join(args)} failed: {str(detail).strip()}") from None
    return result.stdout if binary else result.stdout.decode("utf-8", "strict").strip()


def _safe_repo_path(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise PrepareError(f"{field} must be a non-empty repository-relative POSIX path")
    p = PurePosixPath(value)
    if p.is_absolute() or any(part in ("", ".", "..") for part in p.parts) or ":" in p.parts[0]:
        raise PrepareError(f"unsafe repository path for {field}: {value!r}")
    if any(char in value for char in "*?[]"):
        raise PrepareError(f"Git pathspec metacharacters are not allowed in {field}: {value!r}")
    return p.as_posix()


def _validate_spec(spec: Any) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise PrepareError("spec must be a JSON object")
    if spec.get("schema") != "smallsort-session-spec-v1":
        raise PrepareError("schema must be smallsort-session-spec-v1")
    missing = sorted(SPEC_KEYS - set(spec))
    extra = sorted(set(spec) - SPEC_KEYS)
    if missing:
        raise PrepareError("missing spec fields: " + ", ".join(missing))
    if extra:
        raise PrepareError("unknown spec fields: " + ", ".join(extra))
    s = copy.deepcopy(spec)
    for key in ("task_id", "phase", "branch"):
        if not isinstance(s[key], str) or not s[key].strip():
            raise PrepareError(f"{key} must be a non-empty string")
    if not NAME_RE.fullmatch(s["task_id"]):
        raise PrepareError("task_id contains unsafe characters")
    if not PHASE_RE.fullmatch(s["phase"]):
        raise PrepareError("phase must be an uppercase phase identifier")
    if s["owner"] not in ("merge", "select-sort4", "network"):
        raise PrepareError("owner must be merge, select-sort4 or network")
    if not LANE_RE.fullmatch(s["lane"]):
        raise PrepareError("lane contains unsafe characters")
    if not isinstance(s["worktree"], str) or not s["worktree"]:
        raise PrepareError("worktree must be an absolute path")
    if not Path(s["worktree"]).is_absolute():
        raise PrepareError("worktree must be an absolute path")
    if not SHA_RE.fullmatch(str(s["baseline_sha"])):
        raise PrepareError("baseline_sha must be a lowercase 40-character Git SHA")
    # The window and budget come from the installed assignment text (CORE default
    # 120 + 30 minutes and 3600 s, or the explicit window/budget it states).
    for key, low, high in (("main_minutes", 1, MAX_MAIN_MINUTES), ("finish_minutes", 1, MAX_FINISH_MINUTES)):
        if type(s[key]) is not int or s[key] < low or s[key] > high:
            raise PrepareError(f"{key} must be an integer in {low}..{high}")
    for key in ("cloud_seconds", "max_timeout_seconds", "report_reserve_seconds"):
        if type(s[key]) is not int or s[key] <= 0:
            raise PrepareError(f"{key} must be a positive integer")
    if s["cloud_seconds"] > MAX_CLOUD_SECONDS:
        raise PrepareError(f"cloud_seconds must be at most {MAX_CLOUD_SECONDS}")
    if s["max_timeout_seconds"] > MAX_BUILD_TIMEOUT:
        raise PrepareError(f"max_timeout_seconds must be at most {MAX_BUILD_TIMEOUT} (coordinator envelope timeout + 60 s queue <= 1800)")
    minimum_reserve = 420 if s["owner"] == "merge" else 240
    if s["report_reserve_seconds"] < minimum_reserve:
        raise PrepareError(f"report_reserve_seconds must be at least {minimum_reserve} for {s['owner']}")
    if s["report_reserve_seconds"] >= s["cloud_seconds"]:
        raise PrepareError("report_reserve_seconds must be below cloud_seconds")
    if s["report_reserve_seconds"] >= s["max_timeout_seconds"]:
        raise PrepareError("report_reserve_seconds must be below max_timeout_seconds")
    t0 = _parse_utc(s["t0"], "t0")
    s["_t0"] = t0
    keys = ["profile_path", "recipe_path", "old_ledger_path", "new_ledger_path"]
    # First Cloud session of an owner without Cloud history: no old ledger, and optionally
    # no source profile (the draft profile then starts from an empty object plus updates).
    if s["owner"] in FIRST_SESSION_OWNERS and s["old_ledger_path"] is None:
        keys.remove("old_ledger_path")
        if s["profile_path"] is None:
            if s["new_profile_path"] is None:
                raise PrepareError("a first session without a source profile requires new_profile_path")
            keys.remove("profile_path")
    # new_profile_path null reuses the pinned profile_path unchanged: no draft profile, no updates.
    if s["new_profile_path"] is not None:
        keys.append("new_profile_path")
    elif s["profile_updates"] != {}:
        raise PrepareError("profile_updates require new_profile_path; reuse of a pinned profile allows no updates")
    for key in keys:
        s[key] = _safe_repo_path(s[key], key)
    path_set = [s[key] for key in ("old_ledger_path", "new_ledger_path", "profile_path", "new_profile_path")
                if s[key] is not None]
    if len(set(path_set)) != len(path_set):
        raise PrepareError("old/new ledger and profile paths must be distinct")
    if any(a.startswith(b + "/") or b.startswith(a + "/")
           for index, a in enumerate(path_set) for b in path_set[index + 1:]):
        raise PrepareError("ledger/profile paths cannot be ancestors of one another")
    if not isinstance(s["profile_updates"], dict):
        raise PrepareError("profile_updates must be an explicit JSON object")
    _validate_profile_updates(s["profile_updates"])
    return s


def _parse_utc(value: Any, field: str) -> dt.datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise PrepareError(f"{field} must be UTC in YYYY-MM-DDTHH:MM:SSZ form")
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        raise PrepareError(f"{field} is not a valid UTC timestamp") from None
    if parsed.utcoffset() != dt.timedelta(0) or parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise PrepareError(f"{field} must be canonical UTC in YYYY-MM-DDTHH:MM:SSZ form")
    return parsed


def _validate_profile_updates(updates: dict[str, Any]) -> None:
    for pointer, value in updates.items():
        if not isinstance(pointer, str) or not pointer.startswith("/") or pointer == "/":
            raise PrepareError("profile_updates keys must be non-root JSON pointers")
        decoded = pointer.split("/")[1:]
        if any(re.search(r"~(?![01])", part) for part in decoded):
            raise PrepareError(f"invalid JSON pointer: {pointer}")
        key = decoded[-1].replace("~1", "/").replace("~0", "~").lower()
        if key in PROTECTED_PROFILE_KEYS and value is not False:
            raise PrepareError(f"profile update cannot enable protected field {pointer}")


def _apply_pointer(obj: dict[str, Any], pointer: str, value: Any) -> None:
    parts = [part.replace("~1", "/").replace("~0", "~") for part in pointer.split("/")[1:]]
    current: Any = obj
    for part in parts[:-1]:
        if not isinstance(current, dict) or part not in current or not isinstance(current[part], dict):
            raise PrepareError(f"profile update parent does not exist as an object: {pointer}")
        current = current[part]
    if not isinstance(current, dict):
        raise PrepareError(f"profile update parent is not an object: {pointer}")
    current[parts[-1]] = value


def _git_blob(root: Path, commit: str, path: str) -> tuple[str, str, bytes] | None:
    raw = _run_git(root, "ls-tree", "-z", commit, "--", path, binary=True)
    assert isinstance(raw, bytes)
    found: list[tuple[str, str, str]] = []
    for record in raw.split(b"\x00"):
        if not record:
            continue
        meta, _name = record.split(b"\t", 1)
        mode, kind, oid = meta.decode("ascii").split(" ")
        found.append((mode, kind, oid))
    if not found:
        return None
    if len(found) != 1:
        raise PrepareError(f"path is ambiguous in Git tree: {path}")
    mode, kind, oid = found[0]
    if kind != "blob" or mode not in ("100644", "100755"):
        raise PrepareError(f"path must be a regular committed file: {path}")
    content = _run_git(root, "cat-file", "blob", oid, binary=True)
    assert isinstance(content, bytes)
    return mode, oid, content


def _committed_file(root: Path, commit: str, path: str, *, check_worktree: bool = True) -> tuple[str, str, bytes]:
    item = _git_blob(root, commit, path)
    if item is None:
        raise PrepareError(f"committed input is missing: {path}")
    mode, oid, content = item
    target = root / path
    if check_worktree:
        if target.is_symlink() or not target.is_file():
            raise PrepareError(f"worktree input missing or symlinked: {path}")
        if target.read_bytes() != content:
            raise PrepareError(f"worktree input differs from committed bytes: {path}")
        st_mode = target.stat().st_mode
        work_mode = "100755" if st_mode & 0o111 else "100644"
        if work_mode != mode:
            raise PrepareError(f"worktree mode differs from committed mode: {path}")
    return mode, oid, content


def _tree_entries(root: Path, commit: str, paths: list[str]) -> dict[str, tuple[str, str]]:
    if not paths:
        return {}
    raw = _run_git(root, "ls-tree", "-r", "-z", commit, "--", *paths, binary=True)
    assert isinstance(raw, bytes)
    result: dict[str, tuple[str, str]] = {}
    for record in raw.split(b"\x00"):
        if not record:
            continue
        meta, raw_path = record.split(b"\t", 1)
        mode, kind, oid = meta.decode("ascii").split(" ")
        path = raw_path.decode("utf-8", "strict")
        if kind != "blob" or mode not in ("100644", "100755"):
            raise PrepareError(f"recipe closure contains non-regular Git object: {path} ({mode} {kind})")
        result[path] = (mode, oid)
    return result


def _recipe_paths(recipe: Any) -> tuple[list[str], list[str]]:
    if not isinstance(recipe, dict):
        raise PrepareError("recipe must be a JSON object")
    groups: list[list[str]] = []
    for key in ("infra_paths", "proof_paths"):
        value = recipe.get(key)
        if not isinstance(value, list) or any(not isinstance(p, str) for p in value):
            raise PrepareError(f"recipe.{key} must be a string array")
        paths = [_safe_repo_path(path, f"recipe.{key}") for path in value]
        if len(paths) != len(set(paths)):
            raise PrepareError(f"recipe.{key} contains duplicate paths")
        groups.append(paths)
    return groups[0], groups[1]


def _closure(root: Path, commit: str, recipe: dict[str, Any], pending: dict[str, bytes] | None = None) -> dict[str, Any]:
    infra, proof = _recipe_paths(recipe)
    declared = [(path, "infra") for path in infra] + [(path, "proof") for path in proof]
    pending = pending or {}
    expanded: dict[str, set[str]] = {}
    pending_expanded: dict[str, set[str]] = {}
    for path, group in declared:
        matching_pending = [p for p in pending if p == path or p.startswith(path.rstrip("/") + "/")]
        for pending_path in matching_pending:
            pending_expanded.setdefault(pending_path, set()).add(group)
        if path in pending:
            continue
        selected = _tree_entries(root, commit, [path])
        if not selected:
            if matching_pending:
                continue
            raise PrepareError(f"recipe path is absent from selected commit: {path}")
        for selected_path in selected:
            # A recipe directory can cover an old input that was replaced by a
            # generated file. Reject this implicit broadening instead of
            # silently including both generations.
            if selected_path in (pending or {}):
                pending_expanded.setdefault(selected_path, set()).add(group)
                continue
            expanded.setdefault(selected_path, set()).add(group)
    records: list[dict[str, Any]] = []
    for path, groups in sorted(pending_expanded.items()):
        data = pending[path]
        records.append({"path": path, "groups": sorted(groups), "mode": "100644", "blob": None,
                        "sha256": _sha256(data), "bytes": len(data), "state": "generated_pending_commit"})
    for path, groups in sorted(expanded.items()):
        item = _git_blob(root, commit, path)
        if item is None:
            raise PrepareError(f"selected commit blob disappeared: {path}")
        mode, oid, data = item
        target = root / path
        if target.is_symlink() or not target.is_file() or target.read_bytes() != data:
            raise PrepareError(f"selected closure worktree bytes differ or are unavailable: {path}")
        work_mode = "100755" if target.stat().st_mode & 0o111 else "100644"
        if work_mode != mode:
            raise PrepareError(f"selected closure worktree mode differs: {path}")
        records.append({"path": path, "groups": sorted(groups), "mode": mode, "blob": oid,
                        "sha256": _sha256(data), "bytes": len(data), "state": "committed"})
    records.sort(key=lambda item: (item["path"], item["groups"]))
    return {"schema": "smallsort-session-closure-v1", "commit": commit,
            "entry_count": len(records), "entries": records}


def closure_command(root: Path, commit: str, recipe_path: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    if not SHA_RE.fullmatch(commit):
        raise PrepareError("commit must be a lowercase 40-character Git SHA")
    actual = _run_git(root, "rev-parse", "--verify", f"{commit}^{{commit}}")
    if actual != commit:
        raise PrepareError("commit is not the exact selected Git commit")
    if recipe_path.is_absolute():
        try:
            relative = recipe_path.resolve(strict=True).relative_to(root).as_posix()
        except (ValueError, FileNotFoundError):
            raise PrepareError("recipe path must be inside the selected worktree") from None
    else:
        relative = _safe_repo_path(recipe_path.as_posix(), "recipe path")
    _, _, raw = _committed_file(root, commit, relative)
    try:
        recipe = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PrepareError(f"recipe JSON invalid: {exc}") from None
    return _closure(root, commit, recipe)


def _load_old_ledger(raw: bytes, phase: str, owner: str) -> dict[str, Any]:
    try:
        ledger = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PrepareError(f"old ledger JSON invalid: {exc}") from None
    if not isinstance(ledger, dict):
        raise PrepareError("old ledger must be a JSON object")
    if ledger.get("owner") != owner:
        raise PrepareError("old ledger owner does not match the session owner")
    status = str(ledger.get("status", "")).upper()
    if status in {"ACTIVE", "AUTHORIZED", "OPEN", "IN_PROGRESS"}:
        raise PrepareError("refusing to replace an active legacy ledger")
    if ledger.get("active_build") not in (None, ""):
        raise PrepareError("old ledger still has an active_build")
    builds = ledger.get("builds", [])
    if not isinstance(builds, list):
        raise PrepareError("old ledger builds must be an array")
    for build in builds:
        if not isinstance(build, dict):
            raise PrepareError("old ledger contains a malformed build record")
        state = str(build.get("status", build.get("state", ""))).upper()
        if state not in TERMINAL_STATES:
            raise PrepareError("old ledger still has a non-terminal or unresolved build")
    all_accounted = True
    for build in builds:
        if not isinstance(build, dict):
            all_accounted = False
            break
        state = str(build.get("status", build.get("state", ""))).upper()
        accounted = build.get("accounted") is True
        if state not in TERMINAL_STATES or not accounted:
            all_accounted = False
            break
    closed = status in {"CLOSED", "RETIRED", "COMPLETE", "COMPLETED"}
    explicit_retirement = bool(ledger.get("retired_closure") or ledger.get("retirement_record") or ledger.get("closed_by"))
    if not all_accounted:
        raise PrepareError("every old ledger build must be terminal and accounted=true")
    if not closed and not explicit_retirement:
        raise PrepareError("old ledger must be CLOSED, or fully accounted with an explicit retired closure")
    if ledger.get("phase") == phase:
        raise PrepareError("new phase must not reuse the old ledger phase")
    return ledger


def _fresh_ledger(s: dict[str, Any]) -> dict[str, Any]:
    t0 = s["_t0"]
    main = t0 + dt.timedelta(minutes=s["main_minutes"])
    absolute = main + dt.timedelta(minutes=s["finish_minutes"])
    iso = lambda value: value.strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "schema": "smallsort-prepared-session-ledger-v1",
        "phase": s["phase"], "phase_id": s["phase"], "task_id": s["task_id"],
        "owner": s["owner"], "status": "PREPARED_NOT_REGISTERED",
        "authorization": "DRAFT ONLY: generated from explicit session spec; branch-client registration and owner review remain required",
        "authorization_model": "bounded-cloud-budget",
        "allowed_lanes": [s["lane"]], "ceiling_build_seconds": s["cloud_seconds"],
        "used_build_seconds": 0, "spent_build_seconds": 0,
        "remaining_build_seconds": s["cloud_seconds"], "max_builds": None,
        "maximum_builds": None, "max_timeout_seconds": s["max_timeout_seconds"],
        "maximum_build_timeout_seconds": s["max_timeout_seconds"],
        "start_utc": iso(t0), "main_deadline_utc": iso(main), "deadline_utc": iso(absolute),
        "report_reserve_seconds": s["report_reserve_seconds"],
        "carryover_allowed": False, "carry_seconds": 0, "retired_seconds": 0,
        "builds": [], "active_build": None,
        "baseline_sha": s["baseline_sha"],
    }


def _generated_paths(s: dict[str, Any]) -> list[str]:
    return [s["new_ledger_path"]] + ([s["new_profile_path"]] if s["new_profile_path"] is not None else [])


def _replaced_paths(s: dict[str, Any]) -> set[str]:
    replaced = {s["old_ledger_path"]} | ({s["profile_path"]} if s["new_profile_path"] is not None else set())
    return replaced - {None}


def _pending(s: dict[str, Any], ledger: dict[str, Any], profile: dict[str, Any] | None) -> dict[str, bytes]:
    pending = {s["new_ledger_path"]: _json_bytes(ledger)}
    if s["new_profile_path"] is not None:
        pending[s["new_profile_path"]] = _json_bytes(profile)
    return pending


def _substitute_recipe(recipe: dict[str, Any], s: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(recipe)
    replacements = {s["old_ledger_path"]: s["new_ledger_path"]} if s["old_ledger_path"] is not None else {}
    if s["new_profile_path"] is not None and s["profile_path"] is not None:
        replacements[s["profile_path"]] = s["new_profile_path"]
    found = set()
    for key in ("infra_paths", "proof_paths"):
        if not isinstance(result.get(key), list):
            continue
        next_paths = []
        for value in result[key]:
            if value in replacements:
                found.add(value)
                next_paths.append(replacements[value])
            else:
                next_paths.append(value)
        result[key] = sorted(next_paths)
    result["proof_paths"] = sorted(result["proof_paths"])
    result["infra_paths"] = sorted(result["infra_paths"])
    return result


def _require_first_session_references(recipe: dict[str, Any], s: dict[str, Any]) -> None:
    """Without an old ledger nothing is substituted: the recipe must name the generated files."""
    if s["old_ledger_path"] is not None:
        return
    infra, proof = _recipe_paths(recipe)
    missing = [path for path in _generated_paths(s) if path not in infra + proof]
    if missing:
        raise PrepareError("first-session recipe must reference the generated file(s): " + ", ".join(missing))


def _profile_object(profile_raw: bytes) -> dict[str, Any]:
    try:
        profile = json.loads(profile_raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PrepareError(f"profile JSON invalid: {exc}") from None
    if not isinstance(profile, dict):
        raise PrepareError("profile must be a JSON object")
    return profile


def _assert_history_unchanged(root: Path, s: dict[str, Any], head: str) -> None:
    # Compare committed blobs only, so this fires before any worktree comparison.
    for path in (s["profile_path"], s["old_ledger_path"]):
        if path is None:
            continue
        if _committed_file(root, s["baseline_sha"], path, check_worktree=False)[2] != _committed_file(root, head, path, check_worktree=False)[2]:
            raise PrepareError("historical ledger/profile bytes changed after the closed-session baseline")


def _check_reused_profile(profile: dict[str, Any], recipe: dict[str, Any], s: dict[str, Any]) -> None:
    """A reused pinned profile keeps its own phase binding and cloud flag, never acceptance/credit flags."""
    def credit_flags(value: Any, path: str = "") -> list[str]:
        if isinstance(value, dict):
            found = []
            for key, child in value.items():
                if key.lower() in PROTECTED_PROFILE_KEYS - {"cloud_build_enabled"} and child is not False:
                    found.append(f"{path}/{key}")
                found.extend(credit_flags(child, f"{path}/{key}"))
            return found
        if isinstance(value, list):
            return [hit for index, child in enumerate(value) for hit in credit_flags(child, f"{path}/{index}")]
        return []
    flags = credit_flags(profile)
    if flags:
        raise PrepareError("reused profile carries acceptance/admission/credit flags: " + ", ".join(sorted(flags)))
    infra, proof = _recipe_paths(recipe)
    if s["profile_path"] not in infra + proof:
        raise PrepareError("reused profile is not referenced by the recipe")


def _profile(profile_raw: bytes, s: dict[str, Any]) -> dict[str, Any]:
    profile = _profile_object(profile_raw)
    for pointer, value in s["profile_updates"].items():
        _apply_pointer(profile, pointer, value)
    profile["session_preparation"] = {
        "schema": "smallsort-session-preparation-v1", "task_id": s["task_id"],
        "phase": s["phase"], "owner": s["owner"], "status": "DRAFT",
        "cloud_build_enabled": False,
    }
    profile["status"] = "DRAFT"
    def clear_protected(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in list(value.items()):
                if key.lower() in PROTECTED_PROFILE_KEYS:
                    value[key] = False
                else:
                    clear_protected(child)
        elif isinstance(value, list):
            for child in value:
                clear_protected(child)
    clear_protected(profile)
    for key in PROTECTED_PROFILE_KEYS:
        profile[key] = False
    return profile


def _write_new_file(root: Path, relative: str, data: bytes) -> None:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() or target.is_symlink():
        raise PrepareError(f"generated path collision: {relative}")
    target.write_bytes(data)


def _outside_output(worktree: Path, out: Path) -> Path:
    if out.exists() or out.is_symlink():
        raise PrepareError("output directory already exists or is a symlink")
    if ".." in out.parts:
        raise PrepareError("output path cannot contain '..' components")
    absolute = out.absolute()
    probe = absolute.parent
    while probe != probe.parent:
        if probe.is_symlink():
            raise PrepareError("output parent path contains a symlink")
        probe = probe.parent
    if not absolute.parent.exists() or not absolute.parent.is_dir():
        raise PrepareError("output parent directory must already exist")
    resolved_output = absolute.parent.resolve(strict=True) / absolute.name
    resolved_worktree = worktree.resolve(strict=True)
    if resolved_output == resolved_worktree or resolved_worktree in resolved_output.parents:
        raise PrepareError("output directory must be outside the source worktree")
    return absolute


def _client_hooks(root: Path, commit: str, control_path: str, phase: str) -> tuple[dict[str, int], bool]:
    control = _git_blob(root, commit, control_path)
    if control is None:
        raise PrepareError(f"branch client not found: {control_path}")
    control_text = control[2].decode("utf-8", "replace")
    hooks: dict[str, int] = {}
    for name in ("authorized_phase", "envs", "config", "run_command"):
        match = re.search(rf"^def {name}\(", control_text, re.MULTILINE)
        if match:
            hooks[name] = control_text.count("\n", 0, match.start()) + 1
    if "authorized_phase" not in hooks:
        raise PrepareError("cannot identify branch-client authorization hook")
    return hooks, phase in control_text


def _registration_plan(s: dict[str, Any], control_path: str, hooks: dict[str, int], phase_literal: bool) -> str:
    main = (s["_t0"] + dt.timedelta(minutes=s["main_minutes"])).strftime("%Y-%m-%dT%H:%M:%SZ")
    absolute = (s["_t0"] + dt.timedelta(minutes=s["main_minutes"] + s["finish_minutes"])).strftime("%Y-%m-%dT%H:%M:%SZ")
    literal_status = "already appears in the client source; its gates still require review" if phase_literal else "is absent from the selected client source"
    hook_lines = ", ".join(f"`{name}()` line {line}" for name, line in hooks.items())
    profile_line = (f"new draft `{s['new_profile_path']}` from an empty object (first Cloud session; no source profile)" if s["profile_path"] is None
                    else f"new draft `{s['new_profile_path']}` from `{s['profile_path']}`" if s["new_profile_path"] is not None
                    else f"reuse pinned `{s['profile_path']}` unchanged (no draft profile; bytes must equal the baseline commit; it keeps its own phase/authorization fields and cloud flag, so the client registration must bind its exact SHA-256)")
    consumed = "prepared ledger, the prepared profile and recipe" if s["new_profile_path"] is not None else "prepared ledger and recipe and the pinned profile"
    first_session_line = ("- Previous ledger: none (first Cloud session of this owner)\n" if s["old_ledger_path"] is None else "")
    transport_note = "The shared closure inventory proves committed file identities and bytes, but cannot establish that the final encoded payload/configuration fits transport caps. The existing committed-source client preflight must check those final caps.\n\n"
    return transport_note + f"""# Registration plan — {s['phase']}\n\nThis bundle is **PREPARED_NOT_REGISTERED**. It does not authorize or dispatch a Cloud Build.\n\n- Owner/task: `{s['owner']}` / `{s['task_id']}`\n- Branch and selected HEAD: `{s['branch']}` / see `bundle.json`\n- Baseline checkpoint: `{s['baseline_sha']}`\n- Window: T0 `{s['_t0'].strftime('%Y-%m-%dT%H:%M:%SZ')}`, main deadline `{main}`, absolute deadline `{absolute}`\n- Budget: `{s['cloud_seconds']}` Cloud seconds, max timeout `{s['max_timeout_seconds']}`, report reserve `{s['report_reserve_seconds']}`\n- Lane: `{s['lane']}`\n- Profile: {profile_line}\n{first_session_line}\n## Required branch-client registration\n\nThe selected client remains authoritative at `{control_path}`. The phase ID `{s['phase']}` {literal_status}. Existing client hooks found by static source inspection: {hook_lines}. Review/add exact phase-specific checks in `authorized_phase` (account/owner/lane/window/deadline and timeout), profile/environment binding in `envs`, source/recipe checks in `config` or source preparation, and final authorization before reservation in `run_command`. The branch lane entrypoint must consume the {consumed}. Add matching synthetic registration and service error-path tests.\n\nThe generated ledger's draft status intentionally fails current submission gates. The session preparer does not create permissive client hooks, alter the live coordinator, or decide trusted proof/profile semantics. Commit the reviewed generated files and client registration on the assigned branch, then run the branch's static preflight and synthetic service tests before any separately authorized use.\n"""


ASSIGNMENT_PHASE = re.compile(r"Phase: `([A-Z][A-Z0-9-]{0,100})`")
ASSIGNMENT_TIMEOUT = re.compile(r"Per-Build timeout \u2264(\d+) seconds")


def _check_installed_assignment(root: Path, head: str, s: dict[str, Any]) -> None:
    """Bind the session spec to the committed CURRENT-TASK of the same phase, if installed."""
    show = subprocess.run(["git", "-C", str(root), "show", f"{head}:research/challenge-8/CURRENT-TASK.md"],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if show.returncode != 0:
        return  # no installed assignment on this branch (legacy or fixture worktree)
    try:
        text = show.stdout.decode("utf-8", "strict")
    except UnicodeDecodeError:
        raise PrepareError("installed CURRENT-TASK is not UTF-8") from None
    prefix = text.split(cp.REPORT_MARKER, 1)[0]
    phases = ASSIGNMENT_PHASE.findall(prefix)
    if phases and phases[0] != s["phase"]:
        raise PrepareError(f"spec phase {s['phase']} differs from the installed assignment phase {phases[0]}")
    try:
        terms = cp.assignment_terms(prefix)
    except cp.CheckpointError as exc:
        raise PrepareError(f"installed CURRENT-TASK: {exc}") from None
    if terms is None:
        return
    if (s["main_minutes"], s["finish_minutes"]) != (terms["main_minutes"], terms["finish_minutes"]):
        raise PrepareError(f"spec window {s['main_minutes']}+{s['finish_minutes']} differs from the assignment's {terms['main_minutes']}+{terms['finish_minutes']} minutes")
    if s["cloud_seconds"] != terms["budget_seconds"]:
        raise PrepareError(f"spec cloud_seconds {s['cloud_seconds']} differs from the assignment's {terms['budget_seconds']} seconds")
    timeouts = ASSIGNMENT_TIMEOUT.findall(prefix)
    if timeouts and s["max_timeout_seconds"] > int(timeouts[0]):
        raise PrepareError(f"spec max_timeout_seconds {s['max_timeout_seconds']} exceeds the assignment's {timeouts[0]} seconds")


def prepare(spec_path: Path, out_path: Path) -> dict[str, Any]:
    try:
        raw_spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PrepareError(f"cannot read JSON spec: {exc}") from None
    s = _validate_spec(raw_spec)
    root = Path(s["worktree"]).resolve(strict=True)
    if not root.is_dir():
        raise PrepareError("worktree must be a directory")
    actual_branch = _run_git(root, "branch", "--show-current")
    if actual_branch != s["branch"]:
        raise PrepareError(f"selected branch mismatch: expected {s['branch']}, found {actual_branch or '(detached)'}")
    head = _run_git(root, "rev-parse", "--verify", "HEAD^{commit}")
    baseline = _run_git(root, "rev-parse", "--verify", f"{s['baseline_sha']}^{{commit}}")
    if baseline != s["baseline_sha"]:
        raise PrepareError("baseline_sha does not resolve to the exact Git commit")
    ancestor = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", s["baseline_sha"], head],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ancestor.returncode != 0:
        raise PrepareError("baseline_sha is not an ancestor of the selected HEAD")
    for path in (s["profile_path"], s["recipe_path"], s["old_ledger_path"]):
        if path is not None:
            _committed_file(root, head, path)
    _check_installed_assignment(root, head, s)
    old_raw = None
    if s["old_ledger_path"] is not None:
        _, _, old_raw = _committed_file(root, head, s["old_ledger_path"])
        _load_old_ledger(old_raw, s["phase"], s["owner"])
    for path in _generated_paths(s):
        if _git_blob(root, head, path) is not None or (root / path).exists() or (root / path).is_symlink():
            raise PrepareError(f"new target path already exists: {path}")
    profile_raw = _committed_file(root, head, s["profile_path"])[2] if s["profile_path"] is not None else None
    _, _, recipe_raw = _committed_file(root, head, s["recipe_path"])
    try:
        old_recipe = json.loads(recipe_raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PrepareError(f"recipe JSON invalid: {exc}") from None
    if not isinstance(old_recipe, dict) or old_recipe.get("lane") != s["lane"]:
        raise PrepareError("recipe lane must exactly match spec lane")
    _assert_history_unchanged(root, s, head)
    source_profile = _profile_object(profile_raw if profile_raw is not None else b"{}")
    ledger = _fresh_ledger(s)
    profile = _profile(_json_bytes(source_profile) if profile_raw is None else profile_raw, s) if s["new_profile_path"] is not None else None
    recipe = _substitute_recipe(old_recipe, s)
    _require_first_session_references(recipe, s)
    if profile is None:
        _check_reused_profile(source_profile, recipe, s)
    pending = _pending(s, ledger, profile)
    closure = _closure(root, head, recipe, pending)
    implicit_old_paths = _replaced_paths(s) & {item["path"] for item in closure["entries"]}
    if implicit_old_paths:
        raise PrepareError("recipe directory implicitly includes replaced old file(s); use exact paths: " + ", ".join(sorted(implicit_old_paths)))
    control_path = "research/challenge-8/cloud-build/control.py"
    hooks, phase_literal = _client_hooks(root, head, control_path, s["phase"])
    bundle = _outside_output(root, out_path)
    bundle.mkdir(mode=0o700)
    generated = {
        "spec.json": {k: v for k, v in s.items() if not k.startswith("_")},
        "ledger.json": ledger,
        **({"profile.json": profile} if profile is not None else {}),
        "source_profile.json": source_profile,
        "recipe.json": recipe,
        "source_recipe.json": old_recipe,
        "closure.json": closure,
    }
    for name, value in generated.items():
        (bundle / name).write_bytes(_json_bytes(value))
    if profile_raw is not None:
        (bundle / "source_profile.raw.json").write_bytes(profile_raw)
    if old_raw is not None:
        (bundle / "old_ledger.raw.json").write_bytes(old_raw)
    plan = _registration_plan(s, control_path, hooks, phase_literal)
    (bundle / "registration-plan.md").write_text(plan, encoding="utf-8")
    bundle_meta = {
        "schema": "smallsort-session-bundle-v1", "state": "PREPARED_NOT_REGISTERED",
        "task_id": s["task_id"], "phase": s["phase"], "owner": s["owner"],
        "worktree": str(root), "branch": actual_branch, "selected_head": head,
        "baseline_sha": s["baseline_sha"], "client": control_path,
        "client_hooks": hooks, "client_phase_literal_present": phase_literal,
        "limitations": ["no client registration", "no coordinator authorization", "no slot request", "no Cloud dispatch"],
    }
    (bundle / "bundle.json").write_bytes(_json_bytes(bundle_meta))
    files = sorted(p for p in bundle.rglob("*") if p.is_file())
    inventory = {p.relative_to(bundle).as_posix(): _sha256(p.read_bytes()) for p in files}
    (bundle / "inventory.json").write_bytes(_json_bytes({"schema": "smallsort-session-inventory-v1", "files": inventory}))
    return {"state": "PREPARED_NOT_REGISTERED", "bundle": str(bundle), "phase": s["phase"],
            "owner": s["owner"], "selected_head": head, "closure_entries": len(closure["entries"]),
            "client_hooks": hooks}


def _validate_bundle_contract(bundle: Path) -> dict[str, Any]:
    try:
        spec = _validate_spec(json.loads((bundle / "spec.json").read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as exc:
        raise PrepareError(f"bundle JSON invalid: {exc}") from None
    reuse_profile = spec["new_profile_path"] is None
    expected_files = {"spec.json", "ledger.json", "profile.json", "source_profile.json", "source_profile.raw.json",
                      "old_ledger.raw.json", "recipe.json", "source_recipe.json", "closure.json",
                      "bundle.json", "registration-plan.md", "inventory.json"} - ({"profile.json"} if reuse_profile else set())
    if spec["profile_path"] is None:
        expected_files.discard("source_profile.raw.json")
    if spec["old_ledger_path"] is None:
        expected_files.discard("old_ledger.raw.json")
    found_files = {p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file()}
    if found_files != expected_files:
        raise PrepareError("bundle file set differs from prepared format")
    json_names = ["ledger.json", "source_profile.json", "recipe.json", "source_recipe.json", "closure.json", "bundle.json", "inventory.json"]
    if not reuse_profile:
        json_names.append("profile.json")
    try:
        values = {name: json.loads((bundle / name).read_text(encoding="utf-8")) for name in json_names}
    except (OSError, json.JSONDecodeError) as exc:
        raise PrepareError(f"bundle JSON invalid: {exc}") from None
    ledger, recipe = values["ledger.json"], values["recipe.json"]
    # Reuse mode checks the pinned source profile instead of a generated draft.
    profile = values["source_profile.json"] if reuse_profile else values["profile.json"]
    source_recipe = values["source_recipe.json"]
    source_profile = values["source_profile.json"]
    meta, closure = values["bundle.json"], values["closure.json"]
    if not all(isinstance(v, dict) for v in (ledger, profile, recipe, meta, closure)):
        raise PrepareError("bundle documents must be JSON objects")
    try:
        raw_source_profile = (json.loads((bundle / "source_profile.raw.json").read_text(encoding="utf-8"))
                              if spec["profile_path"] is not None else {})
        old_ledger_raw = (bundle / "old_ledger.raw.json").read_bytes() if spec["old_ledger_path"] is not None else None
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PrepareError(f"historical source snapshots invalid: {exc}") from None
    if raw_source_profile != source_profile:
        raise PrepareError("source profile parsed snapshot differs from preserved original bytes")
    if old_ledger_raw is not None:
        _load_old_ledger(old_ledger_raw, spec["phase"], spec["owner"])
    if meta.get("schema") != "smallsort-session-bundle-v1" or meta.get("state") != "PREPARED_NOT_REGISTERED" or ledger.get("status") != "PREPARED_NOT_REGISTERED":
        raise PrepareError("bundle must remain PREPARED_NOT_REGISTERED")
    if (meta.get("phase") != spec["phase"] or meta.get("owner") != spec["owner"] or
            meta.get("branch") != spec["branch"] or meta.get("task_id") != spec["task_id"]):
        raise PrepareError("bundle metadata does not match spec")
    if ledger != _fresh_ledger(spec):
        raise PrepareError("prepared ledger differs from the complete spec-derived fresh ledger")
    if ledger.get("phase") != spec["phase"] or ledger.get("owner") != spec["owner"] or ledger.get("allowed_lanes") != [spec["lane"]]:
        raise PrepareError("ledger identity/lane differs from spec")
    if ledger.get("baseline_sha") != spec["baseline_sha"] or ledger.get("builds") != [] or ledger.get("active_build") is not None:
        raise PrepareError("ledger baseline or fresh-account fields invalid")
    start = _parse_utc(spec["t0"], "t0")
    expected_main = (start + dt.timedelta(minutes=spec["main_minutes"])).strftime("%Y-%m-%dT%H:%M:%SZ")
    expected_absolute = (start + dt.timedelta(minutes=spec["main_minutes"] + spec["finish_minutes"])).strftime("%Y-%m-%dT%H:%M:%SZ")
    if ledger.get("start_utc") != spec["t0"] or ledger.get("main_deadline_utc") != expected_main or ledger.get("deadline_utc") != expected_absolute:
        raise PrepareError("ledger deadline fields do not match spec")
    if reuse_profile:
        _check_reused_profile(source_profile, recipe, spec)
    else:
        _check_draft_profile(profile, source_profile, spec)
    if recipe.get("lane") != spec["lane"]:
        raise PrepareError("recipe lane differs from spec")
    if recipe != _substitute_recipe(source_recipe, spec):
        raise PrepareError("prepared recipe is not the exact allowed ledger/profile substitution")
    infra, proof = _recipe_paths(recipe)
    if _replaced_paths(spec) & set(infra + proof):
        raise PrepareError("old ledger/profile references were not substituted")
    _require_first_session_references(recipe, spec)
    return _check_closure_and_sources(bundle, spec, meta, closure, ledger, None if reuse_profile else profile,
                                      recipe, source_profile, source_recipe, values, infra, proof)


def _check_draft_profile(profile: dict[str, Any], source_profile: dict[str, Any], spec: dict[str, Any]) -> None:
    if profile.get("status") != "DRAFT" or profile.get("cloud_build_enabled") is not False:
        raise PrepareError("profile must be DRAFT and cloud_build_enabled=false")
    if profile != _profile(_json_bytes(source_profile), spec):
        raise PrepareError("prepared profile differs from explicit source profile plus spec updates")
    def protected_flags_false(value: Any) -> bool:
        if isinstance(value, dict):
            return all((child is False if key.lower() in PROTECTED_PROFILE_KEYS else protected_flags_false(child))
                       for key, child in value.items())
        if isinstance(value, list):
            return all(protected_flags_false(child) for child in value)
        return True
    if not protected_flags_false(profile):
        raise PrepareError("profile acceptance/admission/credit flags must be false")
    prep = profile.get("session_preparation")
    if not isinstance(prep, dict) or prep.get("phase") != spec["phase"] or prep.get("owner") != spec["owner"] or prep.get("status") != "DRAFT":
        raise PrepareError("profile session preparation metadata mismatch")


def _check_closure_and_sources(bundle: Path, spec: dict[str, Any], meta: dict[str, Any], closure: dict[str, Any],
                               ledger: dict[str, Any], profile: dict[str, Any] | None, recipe: dict[str, Any],
                               source_profile: dict[str, Any], source_recipe: dict[str, Any],
                               values: dict[str, Any], infra: list[str], proof: list[str]) -> dict[str, Any]:
    if (closure.get("schema") != "smallsort-session-closure-v1" or
            closure.get("commit") != meta.get("selected_head") or
            not isinstance(closure.get("entries"), list) or
            closure.get("entry_count") != len(closure.get("entries", []))):
        raise PrepareError("closure commit/entries mismatch")
    for path, data in _pending(spec, ledger, profile).items():
        was_referenced = path in infra + proof
        records = [x for x in closure["entries"] if isinstance(x, dict) and x.get("path") == path]
        if was_referenced and (len(records) != 1 or records[0].get("state") != "generated_pending_commit" or records[0].get("sha256") != _sha256(data)):
            raise PrepareError(f"generated closure entry mismatch: {path}")
        if not was_referenced and records:
            raise PrepareError(f"unreferenced generated path appears in closure: {path}")
    root = Path(meta.get("worktree", ""))
    selected_head = meta.get("selected_head")
    if not root.is_absolute() or not isinstance(selected_head, str) or not SHA_RE.fullmatch(selected_head):
        raise PrepareError("bundle selected source identity is malformed")
    root = root.resolve(strict=True)
    if Path(spec["worktree"]).resolve(strict=True) != root:
        raise PrepareError("bundle worktree identity differs from spec")
    selected_commit = _run_git(root, "rev-parse", "--verify", f"{selected_head}^{{commit}}")
    if selected_commit != selected_head:
        raise PrepareError("bundle selected HEAD is not a commit")
    if _run_git(root, "branch", "--show-current") != spec["branch"]:
        raise PrepareError("bundle worktree is no longer on the selected branch")
    ancestry = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", spec["baseline_sha"], selected_head],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ancestry.returncode != 0:
        raise PrepareError("bundle baseline is not an ancestor of selected HEAD")
    _assert_history_unchanged(root, spec, selected_head)
    head_profile_raw = (_committed_file(root, selected_head, spec["profile_path"])[2]
                        if spec["profile_path"] is not None else None)
    head_ledger_raw = (_committed_file(root, selected_head, spec["old_ledger_path"])[2]
                       if spec["old_ledger_path"] is not None else None)
    _, _, head_recipe_raw = _committed_file(root, selected_head, spec["recipe_path"])
    if ((head_profile_raw is not None and head_profile_raw != (bundle / "source_profile.raw.json").read_bytes()) or
            (head_ledger_raw is not None and head_ledger_raw != (bundle / "old_ledger.raw.json").read_bytes())):
        raise PrepareError("preserved historical input bytes differ from selected Git files")
    try:
        head_profile = json.loads(head_profile_raw) if head_profile_raw is not None else {}
        if head_profile != source_profile or json.loads(head_recipe_raw) != source_recipe:
            raise PrepareError("source profile/recipe snapshots differ from selected Git files")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise PrepareError(f"selected source profile/recipe JSON invalid: {exc}") from None
    if head_ledger_raw is not None:
        _load_old_ledger(head_ledger_raw, spec["phase"], spec["owner"])
    control_path = "research/challenge-8/cloud-build/control.py"
    hooks, phase_literal = _client_hooks(root, selected_head, control_path, spec["phase"])
    expected_meta = {
        "schema": "smallsort-session-bundle-v1", "state": "PREPARED_NOT_REGISTERED",
        "task_id": spec["task_id"], "phase": spec["phase"], "owner": spec["owner"],
        "worktree": str(root), "branch": spec["branch"], "selected_head": selected_head,
        "baseline_sha": spec["baseline_sha"], "client": control_path,
        "client_hooks": hooks, "client_phase_literal_present": phase_literal,
        "limitations": ["no client registration", "no coordinator authorization", "no slot request", "no Cloud dispatch"],
    }
    if meta != expected_meta:
        raise PrepareError("bundle metadata differs from selected source/client inspection")
    if (bundle / "registration-plan.md").read_text(encoding="utf-8") != _registration_plan(spec, control_path, hooks, phase_literal):
        raise PrepareError("registration plan differs from selected source/client inspection")
    pending = _pending(spec, ledger, profile)
    rebuilt_closure = _closure(root.resolve(strict=True), selected_head, recipe, pending)
    if closure != rebuilt_closure:
        raise PrepareError("closure inventory differs from selected Git/worktree inputs")
    inventory = values["inventory.json"]
    if inventory.get("schema") != "smallsort-session-inventory-v1" or not isinstance(inventory.get("files"), dict):
        raise PrepareError("inventory schema invalid")
    actual_inventory = {p.relative_to(bundle).as_posix(): _sha256(p.read_bytes())
                        for p in bundle.rglob("*") if p.is_file() and p.name != "inventory.json"}
    if inventory["files"] != actual_inventory:
        raise PrepareError("bundle byte inventory mismatch")
    return {"state": "PREPARED_NOT_REGISTERED", "phase": spec["phase"], "owner": spec["owner"],
            "files": len(actual_inventory), "closure_entries": len(closure["entries"])}


def check(bundle_path: Path) -> dict[str, Any]:
    if bundle_path.is_symlink() or not bundle_path.is_dir():
        raise PrepareError("bundle must be an existing non-symlink directory")
    return _validate_bundle_contract(bundle_path.resolve(strict=True))


def _write_inventory_exclusive(path: Path, data: bytes) -> Path:
    absolute = path.absolute()
    if absolute.exists() or absolute.is_symlink():
        raise PrepareError("inventory output already exists or is a symlink")
    if not absolute.parent.exists() or not absolute.parent.is_dir():
        raise PrepareError("inventory output parent directory must already exist")
    probe = absolute.parent
    while probe != probe.parent:
        if probe.is_symlink():
            raise PrepareError("inventory output parent path contains a symlink")
        probe = probe.parent
    try:
        with absolute.open("xb") as stream:
            stream.write(data)
    except FileExistsError:
        raise PrepareError("inventory output already exists") from None
    return absolute


def _closure_summary(root: Path, recipe: Path, result: dict[str, Any], inventory_path: Path | None) -> dict[str, Any]:
    entries = result["entries"]
    summary: dict[str, Any] = {
        "schema": "smallsort-session-closure-summary-v1",
        "status": "STATIC_ONLY_NOT_PROOF",
        "worktree": str(root.resolve(strict=True)),
        "commit": result["commit"],
        "recipe": str(recipe),
        "entry_count": len(entries),
        "total_bytes": sum(item["bytes"] for item in entries),
        "inventory_sha256": _sha256(_json_bytes(result)),
    }
    if inventory_path is not None:
        written = _write_inventory_exclusive(inventory_path, _json_bytes(result))
        summary["inventory_path"] = str(written)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    p = commands.add_parser("prepare")
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    c = commands.add_parser("check")
    c.add_argument("--bundle", type=Path, required=True)
    cl = commands.add_parser("closure")
    cl.add_argument("--worktree", type=Path, required=True)
    cl.add_argument("--commit", required=True)
    cl.add_argument("--recipe", type=Path, required=True)
    cl.add_argument("--inventory-out", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "prepare":
            result = prepare(args.spec, args.out)
        elif args.command == "check":
            result = check(args.bundle)
        else:
            result = closure_command(args.worktree, args.commit, args.recipe)
            result = _closure_summary(args.worktree, args.recipe, result, args.inventory_out)
        sys.stdout.buffer.write(_json_bytes(result))
        return 0
    except (PrepareError, OSError, UnicodeError) as exc:
        sys.stderr.write(f"session_prepare: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
