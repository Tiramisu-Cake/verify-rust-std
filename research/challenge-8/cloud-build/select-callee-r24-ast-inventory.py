#!/usr/bin/env python3
"""Run a source-bound, positive-only R24 AST diagnostic through the pinned stage."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

SCHEMA = "select-callee-r24-positive-ast-inventory-v1"
PHASE_ENV = "SORT4_R24_SESSION_PHASE_ID"
PHASE = "SORT4-ACTUAL-SELECT-2026-10-24-R24"
ROUTE_ENV = "SORT4_R20_CALLEE_PHASE_ID"
ROUTE_PHASE = "SORT4-ACTUAL-SELECT-2026-10-23-R21"
PROVIDER_ENV = "SMALLSORT_EXECUTION_PROVIDER"
STAGE_NAME = "r24-positive-ast"
AST_FILENAME = "r24-positive.ast.ml"
RECORD_FILENAME = "r24-positive-ast-diagnostic.json"
CONTROL_ENV = {
    "SORT4_ACTUAL_OWNER_REPO_ROOT": None,
    "SORT4_ACTUAL_OWNER_ADMISSION": "1",
    "SORT4_ACTUAL_OWNER_NINE_ADMISSION": "1",
    "SORT4_ACTUAL_NESTED_H2_REPO_ROOT": None,
    "SORT4_ACTUAL_FORGET_OWN_REPO_ROOT": None,
    "SORT4_A1_NINE_REPO_ROOT": None,
}
SNAPSHOT_NAMES = ("unit", *(f"body-{index}" for index in range(9)))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError("R24-AST-INVENTORY: " + message)


def _safe_regular_file(root: Path, path: Path, label: str) -> bytes | None:
    current = path
    while current != root and current != current.parent:
        if current.is_symlink():
            raise RuntimeError(f"R24-AST-INVENTORY: {label} traverses a symlink: {current}")
        current = current.parent
    try:
        path.resolve(strict=False).relative_to(root.resolve())
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"R24-AST-INVENTORY: {label} escapes its case directory") from exc
    if not path.exists():
        return None
    if not path.is_file():
        raise RuntimeError(f"R24-AST-INVENTORY: {label} is not a regular file: {path}")
    return path.read_bytes()


def _source_observation(case: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in ("original/lib.rs", "verified/lib.rs"):
        try:
            data = _safe_regular_file(case, case / name, "source target " + name)
            result[name] = ({"sha256": sha(data), "bytes": len(data)}
                            if data is not None else None)
        except RuntimeError as exc:
            result[name] = {"invalid": str(exc)}
    return result


def _snapshot_observation(case: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name in SNAPSHOT_NAMES:
        filename = f"actual-nested-9-{name}.marshal"
        try:
            data = _safe_regular_file(case, case / filename, "snapshot " + name)
            result[name] = ({"file": filename, "bytes": len(data), "sha256": sha(data)}
                            if data is not None else None)
        except RuntimeError as exc:
            result[name] = {"invalid": str(exc)}
    return result


def _matches_expected(observed: object, expected: object) -> bool:
    if not isinstance(expected, dict) or set(expected) != set(SNAPSHOT_NAMES):
        return False
    if not isinstance(observed, dict) or set(observed) != set(SNAPSHOT_NAMES):
        return False
    for name in SNAPSHOT_NAMES:
        row = expected[name]
        if not isinstance(row, dict) or set(row) != {"file", "bytes", "sha256"}:
            return False
        if observed.get(name) != row:
            return False
    return True


def _structural_ast_envelope(data: bytes) -> dict[str, Any]:
    """Check only the formatter's UTF-8 list/PackageDecl delimiter envelope."""
    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        return {"valid": False, "level": "STRUCTURAL_ENVELOPE_ONLY",
                "error": f"invalid UTF-8 at byte {exc.start}"}
    start = len(text) - len(text.lstrip())
    if start == len(text) or text[start] != "[":
        return {"valid": False, "level": "STRUCTURAL_ENVELOPE_ONLY",
                "error": "outer list opener missing"}
    item = start + 1
    while item < len(text) and text[item].isspace():
        item += 1
    if not text.startswith("PackageDecl", item):
        return {"valid": False, "level": "STRUCTURAL_ENVELOPE_ONLY",
                "error": "nonempty PackageDecl list opener missing"}
    end_item = item + len("PackageDecl")
    if end_item < len(text) and (text[end_item].isalnum() or text[end_item] == "_"):
        return {"valid": False, "level": "STRUCTURAL_ENVELOPE_ONLY",
                "error": "PackageDecl token is not delimited"}

    pairs = {")": "(", "]": "["}
    stack: list[str] = []
    in_string = False
    escaped = False
    outer_closed_at: int | None = None
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "([":
            stack.append(char)
        elif char in ")]":
            if not stack or stack[-1] != pairs[char]:
                return {"valid": False, "level": "STRUCTURAL_ENVELOPE_ONLY",
                        "error": f"mismatched delimiter at character {index}"}
            stack.pop()
            if not stack:
                outer_closed_at = index
                if text[index + 1:].strip():
                    return {"valid": False, "level": "STRUCTURAL_ENVELOPE_ONLY",
                            "error": "trailing text follows outer list"}
                break
    if in_string or escaped:
        return {"valid": False, "level": "STRUCTURAL_ENVELOPE_ONLY",
                "error": "unterminated quoted string"}
    if stack or outer_closed_at is None:
        return {"valid": False, "level": "STRUCTURAL_ENVELOPE_ONLY",
                "error": "truncated or unclosed outer list"}
    return {"valid": True, "level": "STRUCTURAL_ENVELOPE_ONLY",
            "package_decl_token": True}


def _write_record(case: Path, record: dict[str, Any]) -> None:
    target = case / RECORD_FILENAME
    if target.is_symlink():
        return
    try:
        target.resolve(strict=False).relative_to(case.resolve())
    except (OSError, ValueError):
        return
    temporary = case / ("." + RECORD_FILENAME + ".tmp")
    if temporary.is_symlink():
        return
    try:
        temporary.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        os.replace(temporary, target)
    except OSError:
        try:
            temporary.unlink()
        except OSError:
            pass


def run_positive_ast_inventory(*, cap, repo: Path, case: Path, tool_home: Path,
                               schema: Path, compiler_sysroot: str | Path,
                               deadline_epoch: int, variant: str,
                               expected_sources: dict[str, str],
                               expected_snapshots: dict[str, Any],
                               env: dict[str, str] | None = None) -> dict[str, Any]:
    """Run and record one AST diagnostic; malformed output is incomplete data."""
    live_env = dict(os.environ)
    selected_env = dict(live_env if env is None else env)
    need(selected_env == live_env,
         "diagnostic route environment must match the live process environment")
    need(variant == "positive", "only the positive variant may be inventoried")
    need(selected_env.get(PROVIDER_ENV) == "cloud-build" and
         selected_env.get(ROUTE_ENV) == ROUTE_PHASE and
         selected_env.get(PHASE_ENV) == PHASE and
         not selected_env.get("GITHUB_ACTIONS"),
         "exact R24 Cloud session and existing R21 callee route required")
    need(case.is_dir() and not case.is_symlink(), "case directory is missing or symlinked")
    case_real = case.resolve()
    need(set(expected_sources) == {"original/lib.rs", "verified/lib.rs"},
         "source pin inventory differs")
    need(isinstance(expected_snapshots, dict) and
         set(expected_snapshots) == set(SNAPSHOT_NAMES) and
         all(isinstance(row, dict) for row in expected_snapshots.values()),
         "expected unit/body snapshot pin inventory is malformed")
    record_path = case / RECORD_FILENAME
    need(not record_path.exists() and not record_path.is_symlink(),
         "diagnostic record already exists")
    ast_path = case / AST_FILENAME
    need(not ast_path.exists() and not ast_path.is_symlink(),
         "AST output already exists")

    sources_before = _source_observation(case)
    snapshots_before = _snapshot_observation(case)
    source_before_hashes = {name: (item.get("sha256") if isinstance(item, dict) else None)
                            for name, item in sources_before.items()}
    source_pins_valid_before = source_before_hashes == expected_sources
    snapshots_valid_before = _matches_expected(snapshots_before, expected_snapshots)
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "PENDING",
        "complete": False,
        "accepted": False,
        "proof_credit": 0,
        "body_proof_run": "UNKNOWN",
        "verifier_execution": "REQUESTED_NOT_QUALIFIED",
        "variant": variant,
        "stage_name": STAGE_NAME,
        "ast_filename": AST_FILENAME,
        "source_before": sources_before,
        "source_after": None,
        "source_pins_valid_before": source_pins_valid_before,
        "source_pins_valid_after": False,
        "snapshots_before": snapshots_before,
        "snapshots_after": None,
        "snapshots_match_pins_before": snapshots_valid_before,
        "snapshots_match_pins_after": False,
        "stage": None,
        "ast_artifact": None,
        "errors": [],
    }
    if not source_pins_valid_before:
        record["status"] = "INCOMPLETE"
        record["errors"].append("source pair differs from current proof pins before AST stage")
        record["source_after"] = _source_observation(case)
        record["snapshots_after"] = _snapshot_observation(case)
        _write_record(case, record)
        return record
    if not snapshots_valid_before:
        record["status"] = "INCOMPLETE"
        record["errors"].append("preflight snapshots differ from current positive pins")
        record["source_after"] = _source_observation(case)
        record["snapshots_after"] = _snapshot_observation(case)
        _write_record(case, record)
        return record

    argv = [
        str(tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
        "-verbose", "1", "-dump_ast_with_locs", AST_FILENAME, "verified/lib.rs",
    ]
    args = type("AstStageArgs", (), {
        "tool_home": tool_home,
        "schema": schema,
        "compiler_sysroot": str(compiler_sysroot),
        "deadline_epoch": deadline_epoch,
    })()
    link = getattr(cap, "LINK", None)
    stage_fn = getattr(link, "stage", None)
    need(callable(stage_fn), "pinned capture LINK.stage is unavailable")

    env_before = dict(os.environ)
    try:
        cap.clear_semantic_opt_ins()
        controls = {key: (str(repo) if value is None else value)
                    for key, value in CONTROL_ENV.items()}
        os.environ.update(controls)
        stage = stage_fn(case, STAGE_NAME, argv, args,
                         gates=True, pointer_drop=True, cap_seconds=110)
        record["stage"] = stage
        record["status"] = "RAN"
    except BaseException as exc:
        record["status"] = "EXCEPTION"
        record["exception"] = {"type": type(exc).__name__, "message": str(exc)}
        record["errors"].append("AST diagnostic stage raised")
        try:
            record["source_after"] = _source_observation(case)
            record["snapshots_after"] = _snapshot_observation(case)
            record["source_pins_valid_after"] = (
                {name: (item.get("sha256") if isinstance(item, dict) else None)
                 for name, item in record["source_after"].items()} == expected_sources)
            record["snapshots_match_pins_after"] = _matches_expected(
                record["snapshots_after"], expected_snapshots)
        except BaseException as observation_error:
            record["observation_error"] = {
                "type": type(observation_error).__name__,
                "message": str(observation_error),
            }
        _write_record(case, record)
        raise
    finally:
        os.environ.clear()
        os.environ.update(env_before)

    sources_after = _source_observation(case)
    snapshots_after = _snapshot_observation(case)
    record["source_after"] = sources_after
    record["snapshots_after"] = snapshots_after
    record["source_pins_valid_after"] = (
        {name: (item.get("sha256") if isinstance(item, dict) else None)
         for name, item in sources_after.items()} == expected_sources)
    record["snapshots_match_pins_after"] = _matches_expected(
        snapshots_after, expected_snapshots)

    stage = record["stage"]
    if not isinstance(stage, dict):
        record["errors"].append("stage result is missing or has the wrong type")
    else:
        if stage.get("status") != "RAN" or type(stage.get("exit")) is not int:
            record["errors"].append("stage did not return a typed RAN result")
        elif stage.get("exit") not in (0, 1):
            record["errors"].append("stage exit is neither success nor expected positive failure 1")
        if stage.get("argv") != argv:
            record["errors"].append("stage argv differs from the requested diagnostic")
        if (stage.get("stdout") != STAGE_NAME + ".log" or
                stage.get("stderr") != STAGE_NAME + ".log"):
            record["errors"].append("stage log targets differ from the R24 diagnostic name")
        if stage.get("source_before") != {
                name: digest for name, digest in expected_sources.items()}:
            record["errors"].append("stage source-before binding differs")
        if stage.get("source_after") != {
                name: digest for name, digest in expected_sources.items()}:
            record["errors"].append("stage source-after binding differs")
        if stage.get("source_unchanged") is not True:
            record["errors"].append("stage source-unchanged check did not pass")
        if stage.get("intrinsic_gate_active") is not True or \
                stage.get("pointer_drop_gate_active") is not True:
            record["errors"].append("both established verifier gates were not active")

    try:
        ast_bytes = _safe_regular_file(case_real, ast_path, "AST artifact")
    except RuntimeError as exc:
        ast_bytes = None
        record["errors"].append(str(exc))
    if ast_bytes is None or len(ast_bytes) == 0:
        record["errors"].append("AST artifact is missing or empty")
    else:
        record["ast_artifact"] = {
            "filename": AST_FILENAME,
            "bytes": len(ast_bytes),
            "sha256": sha(ast_bytes),
        }
        envelope = _structural_ast_envelope(ast_bytes)
        record["ast_artifact"]["structural_validation"] = envelope
        if envelope.get("valid") is not True:
            record["errors"].append("AST structural envelope is invalid")
    if not record["source_pins_valid_after"]:
        record["errors"].append("source pair drifted during AST diagnostic")
    if not record["snapshots_match_pins_after"]:
        record["errors"].append("unit/body snapshots drifted during AST diagnostic")
    record["status"] = "COMPLETE" if not record["errors"] else "INCOMPLETE"
    record["complete"] = not record["errors"]
    _write_record(case, record)
    return record
