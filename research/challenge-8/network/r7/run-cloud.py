#!/usr/bin/env python3
"""Cloud-only isolated transfer runner for has_efficient_in_place_swap<T>."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import traceback
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
INFRA_DEFAULT = Path("/workspace/infra")
PROOF_DEFAULT = Path("/workspace/proof")
PROVIDER_REL = Path("research/challenge-8/cloud-build/provider.py")
EXTRACTOR_REL = Path("research/challenge-8/extract-verifast-swap-size.py")
EXTRACTOR_SHA256 = "ffa6fe5fa3f35533fafba3bc035e0da08d1624f093f2c47fceeb861a35a44140"
SOURCE_REL = Path("library/core/src/slice/sort/shared/smallsort.rs")
PROFILE_REL = Path("research/challenge-8/cloud-build/network-n13/R7-EXECUTION-PROFILE-20261024-N5.json")
SOURCE_COMMIT = "cd371e035c7e573760c43bf934d53e8118ee3e7d"
SOURCE_BLOB = "40939f922bcb6fdc7ee0d30427fa861827043827"
SOURCE_SHA256 = "85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1"
ARCHIVE_SHA256 = "da1b619fa63ba73c12ce591638ced90fd2471add6f181d0e3310657fe4df98aa"
CONSOLE_SHA256 = "dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc"
TOOL_COMMIT = "809de4596839b739dd999f9e462242c835e3af46"
COMPILER_COMMIT = "db3e99bbab28c6ca778b13222becdea54533d908"
TOOLCHAIN = "nightly-2026-02-05"
FUNCTION = "smallsort::has_efficient_in_place_swap"
CONTRACT = "req true; ens result == (std::mem::size_of::<T>() <= 8); generic T unrestricted"
SPEC = "/*@ req true; @*/ /*@ ens result == (std::mem::size_of::<T>() <= 8); @*/ "
TIMEOUT_SECONDS = 180
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def provider_identity(infra_root: Path) -> dict[str, Any]:
    """Use the infrastructure's provider check before reading proof inputs."""
    provider = load_module("r7_cloud_provider", infra_root / PROVIDER_REL)
    record = provider.require_supported_provider()
    require(isinstance(record, dict) and record.get("provider") == "cloud-build",
            "runner requires the identified Cloud Build provider")
    require(record.get("project") == "smallsort-ci" and record.get("region") == "global",
            "Cloud Build identity is outside the authorized provider")
    return record


def load_profile(infra_root: Path, environ: dict[str, str]) -> tuple[dict[str, Any], dict[str, str]]:
    path = infra_root / PROFILE_REL
    raw = path.read_bytes()
    actual = sha(raw)
    expected = environ.get("NETWORK_R7_PROFILE_SHA256", "")
    require(SHA_RE.fullmatch(expected) is not None, "NETWORK_R7_PROFILE_SHA256 must be a SHA256")
    require(actual == expected, "R7 execution profile SHA256 mismatch")
    profile = json.loads(raw)
    require(isinstance(profile, dict) and
            profile.get("schema") == "smallsort-network-r7-execution-profile-v1",
            "unexpected R7 execution profile schema")
    require(profile.get("status") == "EXECUTION_CANDIDATE_PINNED" and
            profile.get("accepted") is False and profile.get("proof_credit") is False and
            profile.get("lane") == "network-n13" and profile.get("stage") == "swap-size",
            "R7 profile lane/stage mismatch")
    source = profile.get("source")
    require(isinstance(source, dict) and source.get("commit") == SOURCE_COMMIT and
            source.get("git_blob") == SOURCE_BLOB and source.get("sha256") == SOURCE_SHA256 and
            source.get("path") == str(SOURCE_REL), "R7 profile source pin mismatch")
    tool = profile.get("tool")
    require(isinstance(tool, dict) and tool.get("source_commit") == TOOL_COMMIT and
            tool.get("archive_sha256") == ARCHIVE_SHA256 and
            tool.get("console_sha256") == CONSOLE_SHA256 and tool.get("patches") == [],
            "R7 profile stock-tool pin mismatch")
    require(tool.get("refiner") == "bin/refinement-checker",
            "R7 profile refinement-checker path mismatch")
    require(tool.get("refiner_pin") ==
            "All refiner/exporter/prelude/spec bytes from the hash-verified stock archive; per-file hashes recorded before use.",
            "R7 profile stock-tool inventory rule mismatch")
    compiler = profile.get("compiler")
    require(isinstance(compiler, dict) and compiler.get("toolchain") == TOOLCHAIN and
            compiler.get("target") == "x86_64-unknown-linux-gnu" and
            compiler.get("data_model") == "LP64" and
            compiler.get("commit") == COMPILER_COMMIT,
            "R7 profile compiler pin mismatch")
    verifier = profile.get("verifier")
    refiner = profile.get("refiner")
    target = profile.get("target")
    require(isinstance(verifier, dict) and verifier.get("args") == [
                "-rustc_args", "--edition 2021", "-skip_specless_fns", "-verbose", "1", "verified/lib.rs"] and
            verifier.get("timeout_seconds") == TIMEOUT_SECONDS and
            isinstance(refiner, dict) and refiner.get("args") == [
                "--rustc-args", "--edition 2021", "original/lib.rs", "verified/lib.rs"] and
            refiner.get("timeout_seconds") == TIMEOUT_SECONDS and
            isinstance(target, dict) and target.get("symbol") == FUNCTION and
            target.get("contract") == "req true; ens result == (std::mem::size_of::<T>() <= 8);" and
            type(target.get("expected_named_bodies")) is int and target.get("expected_named_bodies") == 1 and
            type(target.get("minimum_statement_records")) is int and target.get("minimum_statement_records") == 1,
            "R7 profile command/target bounds mismatch")
    return profile, {"path": str(path), "sha256": actual}


def extractor_identity(path: Path) -> dict[str, str]:
    raw = path.read_bytes()
    actual = sha(raw)
    require(actual == EXTRACTOR_SHA256, "source extractor SHA256 mismatch")
    return {"path": str(path), "sha256": actual}


def extract(proof_root: Path, evidence: Path) -> None:
    """Call the unchanged extractor with only its documented cwd and argv."""
    path = proof_root / EXTRACTOR_REL
    module = load_module("r7_swap_size_extractor", path)
    old_cwd, old_argv = Path.cwd(), sys.argv[:]
    try:
        os.chdir(proof_root)
        sys.argv = [str(path), str(evidence)]
        module.main()
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)


def snapshot(directory: Path) -> list[dict[str, Any]]:
    result = []
    for path in sorted(directory.rglob("*")):
        if path.is_file() and not path.is_symlink():
            raw = path.read_bytes()
            result.append({"path": path.relative_to(directory).as_posix(),
                           "size_bytes": len(raw), "sha256": sha(raw)})
    return result


def input_snapshot(evidence: Path, proof_root: Path, tools: dict[str, Any],
                   profile_identity: dict[str, str]) -> list[dict[str, Any]]:
    """Hash all proof inputs and pinned tools immediately before/after execution."""
    relative = ["original/lib.rs", "original/smallsort.rs", "verified/lib.rs",
                "verified/smallsort.rs", "extraction.json",
                "source-spans/has_efficient_in_place_swap.rs", "tool-inventory.json"]
    paths: dict[str, Path] = {f"evidence/{name}": evidence / name for name in relative}
    paths["source/live"] = proof_root / SOURCE_REL
    paths["profile"] = Path(profile_identity["path"])
    for key in ("verifier", "refiner", "exporter", "source_extractor"):
        item = tools.get(key)
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            paths[f"tool/{key}"] = Path(item["path"])
    inventory = json.loads((evidence / "tool-inventory.json").read_text(encoding="utf-8"))
    for item in inventory.get("files", []):
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            paths[f"stock/{item['path']}"] = Path(tools["tool_home"]) / item["path"]
    rows = []
    for label, path in sorted(paths.items()):
        if path.is_file() and not path.is_symlink():
            raw = path.read_bytes()
            rows.append({"input": label, "path": str(path), "size_bytes": len(raw), "sha256": sha(raw)})
        else:
            rows.append({"input": label, "path": str(path), "missing_or_nonregular": True})
    return rows


def snapshots_match(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> bool:
    return (not any(row.get("missing_or_nonregular") is True for row in before + after) and
            before == after)


def validate_command(record: Any, label: str, argv: list[str], cwd: Path, timeout: int,
                     log_path: Path) -> tuple[bool, dict[str, Any]]:
    """Validate a command receipt while retaining the raw observation."""
    observed = record if isinstance(record, dict) else {"raw_observation": record}
    reasons = []
    if not isinstance(record, dict):
        reasons.append("command result must be an object")
    else:
        if type(record.get("label")) is not str or record.get("label") != label:
            reasons.append("command label mismatch")
        if (type(record.get("argv")) is not list or
                any(type(arg) is not str for arg in record.get("argv", [])) or record.get("argv") != argv):
            reasons.append("command argv mismatch")
        if type(record.get("cwd")) is not str or record.get("cwd") != str(cwd):
            reasons.append("command cwd mismatch")
        if type(record.get("timeout_seconds")) is not int or record.get("timeout_seconds") != timeout:
            reasons.append("command timeout mismatch")
        if type(record.get("state")) is not str or record.get("state") != "EXITED":
            reasons.append("command did not exit normally")
        if type(record.get("exit")) is not int or record.get("exit") != 0:
            reasons.append("command exit is not integer zero")
        if type(record.get("log")) is not str or record.get("log") != str(log_path):
            reasons.append("command log path mismatch")
        log_sha = record.get("log_sha256")
        if not isinstance(log_sha, str) or SHA_RE.fullmatch(log_sha) is None:
            reasons.append("command log SHA256 missing or malformed")
        if not log_path.is_file() or log_path.is_symlink():
            reasons.append("expected command log is missing or nonregular")
        elif isinstance(log_sha, str) and log_sha != sha(log_path.read_bytes()):
            reasons.append("command log hash mismatch")
    if reasons:
        observed["validation_errors"] = reasons
    return not reasons, observed


def invoke_command(command_runner: Callable[..., Any], label: str, argv: list[str], cwd: Path,
                   log_path: Path, timeout: int) -> Any:
    try:
        return command_runner(label, argv, cwd, log_path, timeout)
    except Exception as exc:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if not log_path.exists():
            log_path.write_text("", encoding="utf-8")
        return {"label": label, "argv": argv, "cwd": str(cwd), "timeout_seconds": timeout,
                "state": "EXCEPTION", "exit": None, "log": str(log_path),
                "log_sha256": sha(log_path.read_bytes()),
                "exception": {"type": type(exc).__name__, "message": str(exc),
                              "traceback": traceback.format_exc()}}


def source_unchanged(proof_root: Path) -> bool:
    return sha((proof_root / SOURCE_REL).read_bytes()) == SOURCE_SHA256


def diagnostic_status(result: dict[str, Any], evidence: Path) -> bool:
    required_files = [evidence / "verified/lib.rs", evidence / "verified/smallsort.rs",
                      evidence / "original/lib.rs", evidence / "original/smallsort.rs",
                      evidence / "extraction.json", evidence / "source-spans/has_efficient_in_place_swap.rs",
                      evidence / "tool-inventory.json"]
    commands = result.get("commands")
    if not all(path.is_file() and not path.is_symlink() for path in required_files):
        return False
    if type(commands) is not list or len(commands) != 2:
        return False
    for row in commands:
        if (not isinstance(row, dict) or row.get("state") not in ("EXITED", "TIMEOUT", "EXCEPTION") or
                not isinstance(row.get("log"), str) or not Path(row["log"]).is_file()):
            return False
    return True


def validate_extraction(proof_root: Path, evidence: Path) -> dict[str, Any]:
    source_path = proof_root / SOURCE_REL
    raw_source = source_path.read_bytes()
    require(sha(raw_source) == SOURCE_SHA256, "live source SHA256 mismatch")
    blob = subprocess.run(["git", "hash-object", str(source_path)], cwd=proof_root,
                          text=True, capture_output=True, check=True, timeout=TIMEOUT_SECONDS).stdout.strip()
    require(blob == SOURCE_BLOB, "live source Git blob mismatch")

    metadata_path = evidence / "extraction.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    require(isinstance(metadata, dict), "extractor metadata must be an object")
    required = {
        "source": str(SOURCE_REL), "source_sha256": SOURCE_SHA256,
        "specified_function": "has_efficient_in_place_swap<T>",
        "expected_specified_target_bodies": 1, "ghost_contract": SPEC,
        "ghost_comment_only": True, "contract": CONTRACT,
    }
    for key, expected in required.items():
        require(metadata.get(key) == expected, f"extraction source-stage-target mismatch: {key}")
    require(type(metadata.get("expected_specified_target_bodies")) is int,
            "extraction target-body count has the wrong type")
    targets = metadata.get("target_statement_lines")
    require(targets == [6, 7] and type(targets) is list and
            all(type(line) is int and line > 0 for line in targets),
            "extraction source-stage-target statement lines mismatch")

    original = (evidence / "original/smallsort.rs").read_bytes()
    verified = (evidence / "verified/smallsort.rs").read_bytes()
    span = (evidence / "source-spans/has_efficient_in_place_swap.rs").read_bytes()
    require(sha(original) == metadata.get("original_sha256") and
            sha(verified) == metadata.get("verified_sha256") and
            sha(span) == metadata.get("source_span_sha256"),
            "extraction artifact hash mismatch")
    require(verified.count(SPEC.encode()) == 1 and verified.replace(SPEC.encode(), b"", 1) == original,
            "ghost stripping does not recover original bytes exactly")
    require(span in original and original.count(b"has_efficient_in_place_swap<T>() -> bool") == 1,
            "extracted target signature/span mismatch")
    workspace_commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=proof_root,
                                       text=True, capture_output=True, check=True,
                                       timeout=TIMEOUT_SECONDS).stdout.strip()
    return {"commit": SOURCE_COMMIT, "workspace_commit": workspace_commit,
            "git_blob": blob, "path": str(SOURCE_REL),
            "sha256": sha(raw_source), "extraction": metadata,
            "original_sha256": sha(original), "verified_sha256": sha(verified),
            "source_span_sha256": sha(span), "target_statement_lines": targets}


def tool_identities(tool_home: Path, proof_root: Path, evidence: Path) -> dict[str, Any]:
    tool_home = tool_home.resolve(strict=True)
    verifier = (tool_home / "bin/verifast").resolve(strict=True)
    refiner = (tool_home / "bin/refinement-checker").resolve(strict=True)
    require(verifier.is_file() and refiner.is_file(), "verifier/refiner must be regular files")
    verifier_sha = sha(verifier.read_bytes())
    require(verifier_sha == CONSOLE_SHA256, "stock VeriFast console SHA256 mismatch")
    exporter = (tool_home / "bin/vf-rust-mir-exporter").resolve(strict=True)
    required_stock_files = [
        refiner, exporter,
        (tool_home / "bin/rust/prelude.rsspec").resolve(strict=True),
        (tool_home / "bin/rust/std/lib.rsspec").resolve(strict=True),
    ]
    optional_roots = [tool_home / "prelude.h", tool_home / "prelude.gh",
                      tool_home / "prelude_core.gh"]
    optional_stock_paths = []
    for root in optional_roots:
        if root.is_dir():
            optional_stock_paths.extend(path for path in root.rglob("*")
                                        if path.is_file() and not path.is_symlink())
        elif root.is_file() and not root.is_symlink():
            optional_stock_paths.append(root)
    optional_stock_paths.extend([tool_home / "prelude.h/prelude_core.gh",
                                 tool_home / "prelude.gh/prelude_core.gh",
                                 tool_home / "bin/rust/prelude_core.rsspec",
                                 tool_home / "bin/rust/prelude_core_core.rsspec"])
    stock_files = {path.relative_to(tool_home).as_posix(): path
                   for path in tool_home.joinpath("bin/rust").rglob("*")
                   if path.is_file() and not path.is_symlink()}
    for path in optional_stock_paths:
        if path.is_file() and not path.is_symlink():
            stock_files[path.relative_to(tool_home).as_posix()] = path
    for path in required_stock_files:
        require(path.is_file() and not path.is_symlink(),
                f"required stock VeriFast file missing or not regular: {path}")
        stock_files[path.relative_to(tool_home).as_posix()] = path
    inventory = [{"path": relative, "size_bytes": path.stat().st_size,
                  "sha256": sha(path.read_bytes())}
                 for relative, path in sorted(stock_files.items())]
    inventory_sha = sha(json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode())
    inventory_record = {"archive_sha256": ARCHIVE_SHA256, "file_count": len(inventory),
                        "inventory_sha256": inventory_sha, "files": inventory}
    (evidence / "tool-inventory.json").write_text(
        json.dumps(inventory_record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    extractor = proof_root / EXTRACTOR_REL
    spec_path = evidence / "verified/smallsort.rs"
    return {
        "tool_home": str(tool_home),
        "archive_sha256": ARCHIVE_SHA256,
        "verifier": {"path": str(verifier), "sha256": verifier_sha},
        "refiner": {"path": str(refiner), "sha256": sha(refiner.read_bytes())},
        "exporter": {"path": str(exporter), "sha256": sha(exporter.read_bytes())},
        "source_extractor": extractor_identity(extractor),
        "tool_inventory": {"path": str(evidence / "tool-inventory.json"),
                           "file_count": len(inventory), "sha256": inventory_sha},
        "spec_file": {"path": str(spec_path), "sha256": sha(spec_path.read_bytes())},
        "tool_commit": TOOL_COMMIT,
        "toolchain": TOOLCHAIN,
        "target": "x86_64-unknown-linux-gnu",
        "abi": "LP64",
    }


def run_command(label: str, argv: list[str], cwd: Path, log_path: Path,
                timeout: int = TIMEOUT_SECONDS) -> dict[str, Any]:
    """Run a bounded command while preserving timeout, exception and partial log."""
    record: dict[str, Any] = {"label": label, "argv": argv, "cwd": str(cwd),
                              "timeout_seconds": timeout, "state": "NOT_RUN"}
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run(argv, cwd=cwd, text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, timeout=timeout, check=False)
        output = completed.stdout or ""
        log_path.write_text(output, encoding="utf-8", errors="replace")
        record.update({"state": "EXITED", "exit": completed.returncode,
                       "log": str(log_path), "log_sha256": sha(log_path.read_bytes())})
    except subprocess.TimeoutExpired as exc:
        raw = exc.stdout or b""
        if isinstance(raw, bytes):
            output = raw.decode("utf-8", "replace")
        else:
            output = raw
        log_path.write_text(output, encoding="utf-8", errors="replace")
        record.update({"state": "TIMEOUT", "exit": None, "log": str(log_path),
                       "log_sha256": sha(log_path.read_bytes()),
                       "exception": {"type": type(exc).__name__, "message": str(exc)}})
    except Exception as exc:  # retain unexpected execution failures as evidence
        if not log_path.exists():
            log_path.write_text("", encoding="utf-8")
        record.update({"state": "EXCEPTION", "exit": None, "log": str(log_path),
                       "log_sha256": sha(log_path.read_bytes()),
                       "exception": {"type": type(exc).__name__, "message": str(exc),
                                     "traceback": traceback.format_exc()}})
    return record


def compiler_identity(profile: dict[str, Any], evidence: Path) -> dict[str, Any]:
    command = ["rustc", "--version", "--verbose"]
    log_path = evidence / "logs/compiler-version.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    base = {"command": command, "toolchain": TOOLCHAIN,
            "expected_commit": profile["compiler"]["commit"],
            "expected_target": profile["compiler"]["target"],
            "data_model": profile["compiler"]["data_model"], "timeout_seconds": TIMEOUT_SECONDS,
            "log": str(log_path)}
    try:
        completed = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, timeout=TIMEOUT_SECONDS, check=False)
        output = completed.stdout or ""
        log_path.write_text(output, encoding="utf-8", errors="replace")
        commit_match = re.search(r"(?m)^commit-hash: ([0-9a-f]{40})$", output)
        host_match = re.search(r"(?m)^host: ([^\r\n]+)$", output)
        host = host_match.group(1) if host_match else None
        commit = commit_match.group(1) if commit_match else None
        accepted = (type(completed.returncode) is int and completed.returncode == 0 and
                    host == profile["compiler"]["target"] and commit == profile["compiler"]["commit"])
        return {**base, "state": "EXITED", "exit": completed.returncode,
                "version": output.strip(), "raw_output": output, "commit": commit, "host": host,
                "target": host, "abi": "LP64" if host == "x86_64-unknown-linux-gnu" else None,
                "accepted": accepted, "log_sha256": sha(log_path.read_bytes())}
    except subprocess.TimeoutExpired as exc:
        raw = exc.stdout or b""
        output = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
        log_path.write_text(output, encoding="utf-8", errors="replace")
        return {**base, "state": "TIMEOUT", "exit": None, "version": output.strip(),
                "raw_output": output, "commit": None, "host": None, "target": None,
                "abi": None, "accepted": False, "log_sha256": sha(log_path.read_bytes()),
                "exception": {"type": type(exc).__name__, "message": str(exc),
                              "timeout_seconds": exc.timeout}}
    except Exception as exc:
        if not log_path.exists():
            log_path.write_text("", encoding="utf-8")
        return {**base, "state": "EXCEPTION", "exit": None, "version": "",
                "raw_output": "", "commit": None, "host": None, "target": None,
                "abi": None, "accepted": False, "log_sha256": sha(log_path.read_bytes()),
                "exception": {"type": type(exc).__name__, "message": str(exc),
                              "traceback": traceback.format_exc()}}


def function_trace(log: str, lines: list[int]) -> dict[str, Any]:
    target_records = [line for line in log.splitlines()
                      if f"Verifying function '{FUNCTION}'" in line]
    # Historical runner's exact source path and statement-line classifier.
    statement = re.compile(
        r"^.*verified/smallsort[.]rs\((\d+),[0-9]+(?:-[0-9]+(?:,[0-9]+)?)?\): "
        r"(?:note: )?Executing (?:statement|return statement)$")
    body_records = []
    for line in log.splitlines():
        match = statement.match(line)
        if match and int(match.group(1)) in lines:
            body_records.append(line)
    errors = [line for line in log.splitlines() if re.search(r"\berror(?:\[|:)", line)]
    return {"named_function_records": target_records, "named_function_count": len(target_records),
            "body_statement_records": body_records, "body_statement_count": len(body_records),
            "error_records": errors, "error_count": len(errors)}


def empty_evidence(path: Path) -> None:
    require(path.exists() and path.is_dir(), "--evidence must be an existing empty directory")
    require(not any(path.iterdir()), "--evidence directory must be empty")
    require(not path.is_symlink(), "--evidence directory cannot be a symlink")


def audit_record(result: dict[str, Any]) -> dict[str, Any]:
    return {"accepted": False, "component_accepted": result.get("accepted") is True,
            "classification": ("NETWORK_R7_COMPONENT_CHECKED" if result.get("accepted") is True
                               else "INCONCLUSIVE"),
            "diagnostic_complete": result.get("diagnostic_complete") is True,
            "proof_credit": False, "lane": "network-n13", "stage": "swap-size"}


def execute(args: argparse.Namespace, environ: dict[str, str],
            provider_check: Callable[[Path], dict[str, Any]] = provider_identity,
            profile_loader: Callable[[Path, dict[str, str]], tuple[dict[str, Any], dict[str, str]]] = load_profile,
            extractor: Callable[[Path, Path], None] = extract,
            command_runner: Callable[..., dict[str, Any]] = run_command) -> tuple[int, dict[str, Any]]:
    evidence = Path(args.evidence).resolve()
    empty_evidence(evidence)
    infra_root = Path(environ.get("INFRA_ROOT", str(INFRA_DEFAULT))).resolve(strict=True)
    proof_root = Path(environ.get("PROOF_ROOT", str(PROOF_DEFAULT))).resolve(strict=True)
    result: dict[str, Any] = {
        "schema": "smallsort-r7-swap-size-cloud-result-v1", "lane": "network-n13",
        "stage": "swap-size", "accepted": False, "classification": "INCONCLUSIVE",
        "diagnostic_complete": False, "proof_credit": False,
        "provider": None, "profile": None, "source": None, "tools": None, "compiler": None,
        "commands": [
            {"label": "verifier", "state": "NOT_RUN", "exit": None,
             "argv": [str(Path(args.tool_home).resolve() / "bin/verifast"), "<profile verifier args>"],
             "timeout_seconds": TIMEOUT_SECONDS},
            {"label": "refiner", "state": "NOT_RUN", "exit": None,
             "argv": [str(Path(args.tool_home).resolve() / "bin/refinement-checker"), "<profile refiner args>"],
             "timeout_seconds": TIMEOUT_SECONDS},
        ], "trace": None, "error": None,
    }
    try:
        # This must precede source reads, extraction imports and tool invocation.
        result["provider"] = provider_check(infra_root)
        profile, profile_identity = profile_loader(infra_root, environ)
        result["profile"] = profile_identity
        result["target"] = profile["target"]
        result["commands"][0].update({"argv": [str(Path(args.tool_home).resolve() / "bin/verifast"),
                                                     *profile["verifier"]["args"]],
                                      "timeout_seconds": profile["verifier"]["timeout_seconds"]})
        result["commands"][1].update({"argv": [str(Path(args.tool_home).resolve() / "bin/refinement-checker"),
                                                     *profile["refiner"]["args"]],
                                      "timeout_seconds": profile["refiner"]["timeout_seconds"]})
        source_extractor = proof_root / EXTRACTOR_REL
        result["source_extractor"] = extractor_identity(source_extractor)
        extractor(proof_root, evidence)
        source = validate_extraction(proof_root, evidence)
        result["source"] = source
        tool_home = Path(args.tool_home).resolve(strict=True)
        tools = tool_identities(tool_home, proof_root, evidence)
        result["tools"] = tools
        tools["tool_home"] = str(tool_home)
        result["compiler"] = compiler_identity(profile, evidence)
        require(result["compiler"].get("accepted") is True,
                "rustc version/target/compiler commit does not match the R7 profile")
        verified = evidence / "verified/lib.rs"
        original = evidence / "original/lib.rs"
        verified_lib = evidence / "verified/smallsort.rs"
        original_lib = evidence / "original/smallsort.rs"
        verifier_argv = [str(tool_home / "bin/verifast"), *profile["verifier"]["args"]]
        verifier_log_path = evidence / "logs/verifier.log"
        refiner_argv = [str(tool_home / "bin/refinement-checker"), *profile["refiner"]["args"]]
        refiner_log_path = evidence / "logs/refiner.log"
        input_before = input_snapshot(evidence, proof_root, tools, profile_identity)
        result["input_snapshot_before"] = input_before
        require(not any(row.get("missing_or_nonregular") is True for row in input_before),
                "proof input snapshot contains missing or nonregular files")
        verifier_raw = invoke_command(command_runner, "verifier", verifier_argv, evidence,
                                      verifier_log_path, profile["verifier"]["timeout_seconds"])
        result["commands"][0] = verifier_raw if isinstance(verifier_raw, dict) else {
            "raw_observation": verifier_raw}
        # Always invoke the refinement checker, even if VeriFast fails.
        refiner_raw = invoke_command(command_runner, "refiner", refiner_argv, evidence,
                                     refiner_log_path, profile["refiner"]["timeout_seconds"])
        result["commands"][1] = refiner_raw if isinstance(refiner_raw, dict) else {
            "raw_observation": refiner_raw}
        # Validate both receipts only after the complete tool sequence, so a
        # later tool cannot alter an earlier command's saved log unnoticed.
        verifier_ok, verifier = validate_command(verifier_raw, "verifier", verifier_argv, evidence,
                                                 TIMEOUT_SECONDS, verifier_log_path)
        refiner_ok, refiner = validate_command(refiner_raw, "refiner", refiner_argv, evidence,
                                               TIMEOUT_SECONDS, refiner_log_path)
        result["commands"][0] = verifier
        result["commands"][1] = refiner
        verifier_log = verifier_log_path.read_text(encoding="utf-8", errors="replace") \
            if verifier_log_path.is_file() else ""
        trace = function_trace(verifier_log, source["target_statement_lines"])
        result["trace"] = trace
        result["command_validations"] = {"verifier": verifier_ok, "refiner": refiner_ok}
        input_after = input_snapshot(evidence, proof_root, tools, profile_identity)
        result["input_snapshot_after"] = input_after
        inputs_unchanged = snapshots_match(input_before, input_after)
        result["proof_inputs_unchanged"] = inputs_unchanged
        expected_paths = [verified, original, verified_lib, original_lib,
                          evidence / "extraction.json", evidence / "source-spans/has_efficient_in_place_swap.rs",
                          evidence / "tool-inventory.json"]
        files_present = all(path.is_file() and not path.is_symlink() for path in expected_paths)
        unchanged = source_unchanged(proof_root)
        stage_ok = (verifier_ok and refiner_ok and verifier.get("state") == "EXITED" and
                    type(verifier.get("exit")) is int and verifier.get("exit") == 0 and
                    refiner.get("state") == "EXITED" and type(refiner.get("exit")) is int and
                    refiner.get("exit") == 0 and
                    trace["named_function_count"] == 1 and trace["body_statement_count"] >= 1 and
                    trace["error_count"] == 0 and files_present and unchanged and inputs_unchanged)
        result["diagnostic_complete"] = diagnostic_status(result, evidence)
        result["accepted"] = bool(stage_ok and result["diagnostic_complete"] and
                                  source.get("commit") == SOURCE_COMMIT and source.get("git_blob") == SOURCE_BLOB and
                                  tools.get("verifier", {}).get("sha256") == CONSOLE_SHA256 and
                                  tools.get("archive_sha256") == ARCHIVE_SHA256 and
                                  result["compiler"].get("toolchain") == TOOLCHAIN and
                                  result["compiler"].get("commit") == profile["compiler"].get("commit") and
                                  result["compiler"].get("target") == "x86_64-unknown-linux-gnu" and
                                  result["compiler"].get("abi") == "LP64")
        result["classification"] = "ACCEPTED_COMPONENT" if result["accepted"] else "INCONCLUSIVE"
        result["source_unchanged"] = unchanged
        result["source_tool_target_match"] = bool(
            source.get("commit") == SOURCE_COMMIT and source.get("git_blob") == SOURCE_BLOB and
            tools.get("tool_commit") == TOOL_COMMIT and result["compiler"].get("toolchain") == TOOLCHAIN and
            result["compiler"].get("target") == "x86_64-unknown-linux-gnu" and
            result["compiler"].get("abi") == "LP64")
        result["audit"] = audit_record(result)
        result["evidence_snapshot"] = snapshot(evidence)
        return (0 if result["accepted"] else 2), result
    except Exception as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc),
                            "traceback": traceback.format_exc()}
        result["diagnostic_complete"] = diagnostic_status(result, evidence)
        result["audit"] = audit_record(result)
        result["evidence_snapshot"] = snapshot(evidence)
        return 2, result


def main(argv: list[str] | None = None, environ: dict[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool-home", required=True)
    parser.add_argument("--evidence", required=True)
    args = parser.parse_args(argv)
    evidence = Path(args.evidence).resolve()
    try:
        if evidence.exists():
            if evidence.is_symlink() or not evidence.is_dir() or any(evidence.iterdir()):
                print("--evidence must be an existing empty directory or a new path", file=sys.stderr)
                return 2
        else:
            evidence.mkdir(parents=True)
    except OSError as exc:
        print(f"cannot prepare --evidence directory: {exc}", file=sys.stderr)
        return 2
    try:
        code, result = execute(args, os.environ if environ is None else environ)
    except Exception as exc:
        code = 2
        result = {"schema": "smallsort-r7-swap-size-cloud-result-v1", "lane": "network-n13",
                  "stage": "swap-size", "accepted": False, "classification": "INCONCLUSIVE",
                  "diagnostic_complete": False, "proof_credit": False,
                  "error": {"type": type(exc).__name__, "message": str(exc),
                            "traceback": traceback.format_exc()}}
    result["audit"] = audit_record(result)
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "proof-audit.json").write_text(json.dumps(result["audit"], indent=2, sort_keys=True) + "\n",
                                                encoding="utf-8")
    command_by_label = {row.get("label"): row for row in result.get("commands", [])
                        if isinstance(row, dict)}
    for label in ("verifier", "refiner"):
        row = command_by_label.get(label, {})
        value = row.get("exit") if type(row.get("exit")) is int else row.get("state", "NOT_RUN")
        (evidence / f"{label}-exit-code.txt").write_text(f"{value}\n", encoding="utf-8")
    (evidence / "stages-exit-code.txt").write_text(f"{code}\n", encoding="utf-8")
    (evidence / "exit-code.txt").write_text(f"{code}\n", encoding="utf-8")
    result["evidence_snapshot"] = snapshot(evidence)
    (evidence / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                                            encoding="utf-8")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
