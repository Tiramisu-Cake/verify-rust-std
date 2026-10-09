#!/usr/bin/env python3
"""Hosted-only staged exact-source direct Drop body diagnostic."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load checked helper {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


preparation = load_module("copy_on_drop_prepare", HERE / "copy-on-drop-prepare.py")
mir_helper = load_module("drop_capnp_admission", HERE / "stack-address-admission.py")
ast_helper = load_module("drop_ast_admission", HERE / "stack-proof-ast-admission.py")
TARGET = preparation.TARGET
MIR_COPY_CALLEE = "core::ptr::copy_nonoverlapping"
AST_COPY_CALLEE = "std::ptr::copy_nonoverlapping"
TIMEOUT_SECONDS = 240

STOCK_PINS = {
    "bin/verifast": "9b7650ad3ab0dad3b8974ae9ba1c662ab2cd897ce1dd07215dedcbe460249ee1",
    "bin/vf-rust-mir-exporter": "b00c75f43ab4d89bf85f5e62a5114a238b89b720d4598d90423347b9d97ac796",
    "bin/refinement-checker": "b049c8d1b0bb350f77664e1c75c5a95966c5839984abc25c7cb629c0cba04d28",
}
STOCK_SCHEMA_SHA = "f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469"
STOCK_SPECS_SHA = "4a0911303bbb087f1f50ce85524197edbb541f31c72e8133dfbcc9cf528e03a0"
STOCK_SPEC_CHECKS_SHA = "2adb5f85e2077a96e2db6b97da9af17d9324ad3c586187292854970e63078da4"
STOCK_PRELUDE_SHA = "d7058d43557a2b5147eb1377e85bb67d04b94c83594b6c1c27650c9c571841b5"
EXPERIMENTAL_PROFILE = "experimental-merge-wrapping-callback-copy-cleanup-usize-stack-v1"
EXPERIMENTAL_PATCH_PINS = {
    "wrapping_patch": "c7c776ff5aef2b8668aa2ed3d59b47109fce1d67a9dc2f2043fc2744dc0ed31e",
    "callback_patch": "0a006df94f04d6425d70280967d6652bdd33ccb88ead4a44f02a2e36775aaa5e",
    "copy_patch": "da167ee095e9fb5f425e2d604dd46a973a8c1e3a5121b2c87cc3546b0ec8e9a5",
    "cleanup_patch": "94fe2cd69edc9da6907553961ca32f0557c338266d9e9472e577860a95887604",
    "usize_patch": "ecdd1fd6fcc8d811f02fa308ddc533386e0031193d527ea6950a099f8ccccaa1",
    "stack_address_patch": "f1444866322bf06b40e078a381a69acea7ccd92b613f7dc903d289044d8cba64",
    "release_console": STOCK_PINS["bin/verifast"],
    "release_exporter": STOCK_PINS["bin/vf-rust-mir-exporter"],
    "release_refiner": STOCK_PINS["bin/refinement-checker"],
}
EXPERIMENTAL_OUTPUT_PINS = {
    "kernel_patched": "100eebae92c770a0b8cd57e2639588761f881316dd522fc3b9a9b1ec6fd91cd6",
    "translator_patched": "ffd6fe925364b8274d61f094d43211f9463e0dc3e98ae545d3f528f2da0cf6c0",
    "parser_patched": "8ed673086183323058aac5e0e21399e4532d1e74b97c5d41105827e8643107bd",
    "prelude_patched": "d1079bc94ceafe6595c7ce216f9c93e3436d22d849bd31bcb0cf442dd183e751",
    "stdlib_patched": "d92e5044bbb2692e7b006fc649df361fe80bf878b69b5a2bb80635a27330f227",
    "z3_runtime": "1837668dc531d14b3a4fffc0b690b77929d29c41868f98a89686f5ff64da95ea",
    "applied_patch": "b163d3e36b695304cbc6c84d025af7bd5d679a5fb553356baa8b8362dea1b927",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def validate_profile(args) -> dict:
    pins = {}
    if not args.profile_evidence.is_dir():
        raise RuntimeError("--profile-evidence must name the exact tool setup/build evidence directory")
    if args.profile == "stock-26.10":
        for relative, expected in STOCK_PINS.items():
            actual = file_sha(args.tool_home / relative)
            if actual != expected:
                raise RuntimeError(f"stock profile binary pin mismatch for {relative}: {actual}")
            pins[relative] = actual
        specs = ROOT / "research/challenge-8/merge/stock-26.10/vf-stock-specs.json"
        checks = ROOT / "research/challenge-8/merge/stock-26.10/vf-stock-specs.sha256"
        if file_sha(specs) != STOCK_SPECS_SHA or file_sha(checks) != STOCK_SPEC_CHECKS_SHA:
            raise RuntimeError("stock verifier spec profile manifest pin mismatch")
        prelude = args.tool_home / "bin/rust/prelude.rsspec"
        if not prelude.is_file() or file_sha(prelude) != STOCK_PRELUDE_SHA:
            raise RuntimeError("stock VeriFast prelude pin mismatch")
        entries = []
        for row in checks.read_text().splitlines():
            match = re.fullmatch(r"([0-9a-f]{64})  (.+)", row)
            if not match:
                raise RuntimeError("malformed stock spec hash manifest")
            expected, relative = match.groups()
            candidate = args.tool_home / relative
            if not candidate.is_file() or file_sha(candidate) != expected:
                raise RuntimeError(f"stock specification resource mismatch: {relative}")
            entries.append(relative)
        if len(entries) != 58 or len(set(entries)) != 58:
            raise RuntimeError("stock specification resource count differs from pinned profile")
        environment = args.profile_evidence / "environment.txt"
        if not environment.is_file():
            raise RuntimeError("stock profile evidence lacks the setup environment record")
        environment_text = environment.read_text(errors="replace")
        for required in ("official-stock-VeriFast-26.10", "f76012fb518703b1d98e243ac4f487f16877cfcb",
                         STOCK_SCHEMA_SHA, STOCK_SPECS_SHA, STOCK_SPEC_CHECKS_SHA):
            if required not in environment_text:
                raise RuntimeError("stock setup record does not bind the frozen release/schema/spec profile")
        pins.update({"spec_manifest_sha256": file_sha(specs),
                     "spec_checks_sha256": file_sha(checks),
                     "prelude_sha256": file_sha(prelude),
                     "prelude_path": "bin/rust/prelude.rsspec",
                     "spec_resource_count": len(entries)})
        return pins

    if args.profile != EXPERIMENTAL_PROFILE:
        raise RuntimeError("experimental profile needs its immutable build evidence directory")
    evidence = args.profile_evidence
    profile_file = evidence / "console-cache-profile.txt"
    runtime_file = evidence / "source-build-runtime.txt"
    applied_patch = evidence / "applied-profile.patch"
    commit_file = evidence / "verifast-source-commit.txt"
    build_exit = evidence / "source-build-exit-code.txt"
    if not all(path.is_file() for path in (profile_file, runtime_file, applied_patch,
                                            commit_file, build_exit)):
        raise RuntimeError("experimental profile evidence is incomplete")
    if commit_file.read_text().strip() != "f76012fb518703b1d98e243ac4f487f16877cfcb" or build_exit.read_text().strip() != "0":
        raise RuntimeError("experimental source build did not finish at the pinned VeriFast commit")
    fields = {}
    for line in profile_file.read_text().splitlines():
        if "=" not in line:
            raise RuntimeError("malformed experimental profile manifest")
        key, value = line.split("=", 1)
        if key in fields:
            raise RuntimeError(f"duplicate experimental profile field {key}")
        fields[key] = value
    if (fields.get("profile_id") != "vf26.10-w1-m2-c1-cleanup-usize-stack-ubuntu22.04-v1" or
            fields.get("source_commit") != "f76012fb518703b1d98e243ac4f487f16877cfcb" or
            fields.get("runner_version") != "22.04"):
        raise RuntimeError("experimental profile manifest identity mismatch")
    for key, expected in EXPERIMENTAL_PATCH_PINS.items():
        if fields.get(key) != expected:
            raise RuntimeError(f"experimental profile pin mismatch for {key}")
    for key, expected in EXPERIMENTAL_OUTPUT_PINS.items():
        if fields.get(key) != expected:
            raise RuntimeError(f"experimental semantic output pin mismatch for {key}")
    if fields.get("applied_patch") != file_sha(applied_patch):
        raise RuntimeError("experimental applied patch hash differs from build manifest")
    if fields.get("build_script") != file_sha(HERE / "build.sh"):
        raise RuntimeError("experimental build profile was produced by a different build script")
    runtime_lines = runtime_file.read_text().splitlines()
    runtime_hashes = [row.split()[0] for row in runtime_lines
                      if re.fullmatch(r"[0-9a-f]{64}  .+", row)]
    if file_sha(args.tool_home / "bin/verifast") not in runtime_hashes:
        raise RuntimeError("experimental console is not linked to recorded build runtime")
    for rel in ("bin/vf-rust-mir-exporter", "bin/refinement-checker"):
        if file_sha(args.tool_home / rel) != STOCK_PINS[rel]:
            raise RuntimeError(f"experimental profile changed release helper {rel}")
        pins[rel] = file_sha(args.tool_home / rel)
    source_resources = {
        "kernel_patched": "src/verifast.ml",
        "translator_patched": "src/rust_frontend/vf_mir_translator/vf_mir_translator.ml",
        "parser_patched": "src/rust_frontend/vf_mir_translator/rust_parser.ml",
        "prelude_patched": "bin/rust/prelude_core.rsspec",
        "stdlib_patched": "bin/rust/std/lib.rsspec",
        "z3_runtime": "bin/libz3.so",
    }
    for key, relative in source_resources.items():
        candidate = args.tool_home / relative
        if not candidate.is_file() or fields.get(key) != file_sha(candidate):
            raise RuntimeError(f"experimental tool-home source differs from build profile resource {key}")
    prelude_candidates = [args.tool_home / "bin/rust/prelude_core.rsspec",
                          args.tool_home / "bin/rust/prelude.rsspec"]
    prelude = next((path for path in prelude_candidates if path.is_file()), None)
    if prelude is None or file_sha(prelude) != fields.get("prelude_patched"):
        raise RuntimeError("experimental prelude differs from immutable build profile")
    pins.update({"profile_manifest_sha256": file_sha(profile_file),
                 "build_runtime_sha256": file_sha(runtime_file),
                 "applied_patch_sha256": file_sha(applied_patch),
                 "prelude_sha256": file_sha(prelude),
                 "prelude_path": str(prelude.relative_to(args.tool_home)),
                 "experimental_console_sha256": file_sha(args.tool_home / "bin/verifast")})
    pins.update({key: fields[key] for key in EXPERIMENTAL_OUTPUT_PINS
                 if key != "applied_patch"})
    return pins


def require_hosted_cloud() -> tuple[dict, str]:
    if os.environ.get("SMALLSORT_EXECUTION_PROVIDER") != "cloud-build":
        raise RuntimeError("SMALLSORT_EXECUTION_PROVIDER must be cloud-build")
    provider_file = os.environ.get("SMALLSORT_PROVIDER_FILE")
    if not provider_file or not Path(provider_file).is_file():
        raise RuntimeError("SMALLSORT_PROVIDER_FILE must name the reviewed Cloud Build provider helper")
    provider = __import__("runpy").run_path(provider_file)["require_supported_provider"]()
    build_id = os.environ.get("CLOUD_BUILD_ID", "")
    if (provider.get("provider") != "cloud-build" or provider.get("build_id") != build_id or
            provider.get("project") != os.environ.get("CLOUD_BUILD_PROJECT_ID") or
            provider.get("region") != os.environ.get("CLOUD_BUILD_REGION")):
        raise RuntimeError("Cloud Build provider identity differs from the checked provider helper")
    proof_sha = os.environ.get("PROOF_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", proof_sha):
        raise RuntimeError("PROOF_SHA is missing or malformed")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True, check=True).stdout.strip()
    if head != proof_sha:
        raise RuntimeError("Cloud proof checkout HEAD differs from PROOF_SHA")
    return provider, proof_sha


def hashes(case_dir: Path) -> dict[str, str]:
    return {**{name: file_sha(case_dir / name) for name in
               ("original/lib.rs", "verified/lib.rs")},
            "small_sort_source": file_sha(
                ROOT / "library/core/src/slice/sort/shared/smallsort.rs")}


def run_stage(case_dir: Path, stage: str, argv: list[str], env: dict[str, str],
              timeout_seconds: int = TIMEOUT_SECONDS, stdin: Path | None = None,
              stdout_name: str | None = None, combine: bool = False) -> int:
    before = hashes(case_dir)
    stdout_path = case_dir / (stdout_name or f"{stage}.out")
    stderr_path = case_dir / f"{stage}.log"
    resources_path = case_dir / f"{stage}-resources.txt"
    bounded = ["timeout", "--signal=TERM", "--kill-after=5s",
               f"{timeout_seconds}s", *argv]
    command = ["/usr/bin/time", "-v", "-o", str(resources_path), *bounded]
    started = time.monotonic()
    status = 127
    try:
        with stdout_path.open("wb") as stdout_file, stderr_path.open("wb") as stderr_file:
            output = stderr_file if combine else stdout_file
            error_output = subprocess.STDOUT if combine else stderr_file
            input_stream = stdin.open("rb") if stdin is not None else subprocess.DEVNULL
            with input_stream if hasattr(input_stream, "close") else _null_context(input_stream):
                result = subprocess.run(command, cwd=case_dir, env=env,
                    stdin=input_stream, stdout=output, stderr=error_output,
                    timeout=timeout_seconds + 10, check=False)
            status = result.returncode
    except subprocess.TimeoutExpired as error:
        status = 124
        with stderr_path.open("ab") as log:
            log.write(f"\nSTAGE_TIMEOUT after {timeout_seconds}s: {error}\n".encode())
    except OSError as error:
        status = 127
        stderr_path.write_text(f"could not start stage: {error}\n")
        stdout_path.touch(exist_ok=True)
    after = hashes(case_dir)
    row = {"stage": stage, "argv": command, "exit_code": status,
           "elapsed_seconds": round(time.monotonic() - started, 3),
           "source_before": before, "source_after": after,
           "source_unchanged": before == after}
    (case_dir / f"{stage}-stage.json").write_text(json.dumps(row, indent=2) + "\n")
    (case_dir / f"{stage}-exit-code.txt").write_text(f"{status}\n")
    return status


class _null_context:
    def __init__(self, value):
        self.value = value
    def __enter__(self):
        return self.value
    def __exit__(self, *args):
        return False


def not_run(case_dir: Path, stage: str, reason: str) -> None:
    (case_dir / f"{stage}.out").write_bytes(b"")
    (case_dir / f"{stage}.log").write_text(reason + "\n")
    (case_dir / f"{stage}-resources.txt").write_text("stage not run\n")
    (case_dir / f"{stage}-exit-code.txt").write_text("125\n")
    (case_dir / f"{stage}-stage.json").write_text(json.dumps({
        "stage": stage, "exit_code": 125, "status": "NOT_RUN", "reason": reason,
    }, indent=2) + "\n")


def local_name(place) -> str:
    name = mir_helper.path(place, "local", "name")
    if not isinstance(name, str) or not re.fullmatch(r"_[0-9]+", name):
        raise RuntimeError("MIR place is not a concrete local")
    return name


def field_origin(identifier: str, writes: dict[str, list], input_self: str,
                 before_index: int, visited: set[str] | None = None) -> tuple[int, int] | None:
    visited = set() if visited is None else visited
    if identifier in visited:
        return None
    visited.add(identifier)
    candidates = [(position, assign) for position, assign in writes.get(identifier, [])
                  if position < before_index]
    if len(candidates) != 1:
        return None
    write_index, assignment = candidates[0]
    rhs = mir_helper.path(assignment, "rhsRvalue")
    if "use" not in rhs or len(rhs["use"]) != 1:
        return None
    kind, place = next(iter(rhs["use"].items()))
    if kind not in ("copy", "move"):
        return None
    root = local_name(place)
    projection = mir_helper.path(place, "projection")
    if root == input_self:
        derefs = sum(1 for item in projection if "deref" in item)
        fields = [mir_helper.path(item, "field", "index") for item in projection
                  if isinstance(item, dict) and "field" in item]
        if derefs == 1 and len(fields) == 1 and len(projection) == 2:
            value = fields[0]
            return (value, write_index) if isinstance(value, int) else None
        return None
    if projection:
        return None
    return field_origin(root, writes, input_self, write_index, visited)


def contains_key(tree, key: str) -> bool:
    if isinstance(tree, dict):
        return key in tree or any(contains_key(value, key) for value in tree.values())
    if isinstance(tree, list):
        return any(contains_key(value, key) for value in tree)
    return False


def mir_admission(case_dir: Path) -> dict:
    decoded = (case_dir / "decode.out").read_text(errors="replace")
    # capnp's enum printer emits this one unquoted ADT-variance value. The
    # retained generic parser intentionally refuses unknown bare scalars;
    # normalize only the exact pinned CopyOnDrop metadata field, then parse
    # the entire decoded MIR normally. Any other enum or shape still refuses.
    variance_field = "variances = [invariant]"
    if decoded.count(variance_field) != 1 or len(re.findall(r"\bvariances\s*=", decoded)) != 1:
        raise RuntimeError("Drop MIR must have exactly one invariant T variance field")
    normalized = decoded.replace(variance_field, 'variances = ["invariant"]', 1)
    tree = mir_helper.CapnpText(normalized).parse()
    adt = mir_helper.path(tree, "adtDefs", "cons", "h")
    variants = mir_helper.path(adt, "variants")
    if (mir_helper.path(adt, "id", "name") != "CopyOnDrop" or
            mir_helper.path(adt, "variances") != ["invariant"] or
            mir_helper.path(adt, "kind") != {"structKind": None} or
            mir_helper.path(tree, "adtDefs", "cons", "t") != {"nil": None} or
            not isinstance(variants, list) or len(variants) != 1 or
            mir_helper.path(variants[0], "name") != "CopyOnDrop" or
            [mir_helper.path(field, "name", "name") for field in
             mir_helper.path(variants[0], "fields")] != ["src", "dst", "len"]):
        raise RuntimeError("normalized variance is not the exact CopyOnDrop<T> ADT field")
    bodies = mir_helper.path(tree, "bodies")
    matches = [body for body in bodies if mir_helper.path(body, "defPath") == TARGET]
    if len(matches) != 1:
        return {"target_count": len(matches), "admitted": False,
                "reason": "named actual Drop MIR body is missing or ambiguous"}
    body = matches[0]
    lines = (case_dir / "verified/lib.rs").read_text().splitlines()
    blocks = mir_helper.path(body, "basicBlocks")
    if not blocks or mir_helper.path(blocks[0], "id", "index") != 0:
        return {"target_count": 1, "admitted": False,
                "reason": "MIR body has no canonical entry basic block 0"}
    calls = []
    all_call_count = 0
    for block_index, block in enumerate(blocks):
        terminator = mir_helper.path(block, "terminator", "kind")
        if isinstance(terminator, dict) and "call" in terminator:
            all_call_count += 1
            call = terminator["call"]
            try:
                name = mir_helper.call_name(call)
            except mir_helper.AdmissionError:
                name = "<unrecognized>"
            if name == MIR_COPY_CALLEE:
                args = mir_helper.path(call, "args")
                snippet, line = mir_helper.span_text(mir_helper.path(call, "callSpan"), lines)
                calls.append((block_index, block, call, args, snippet, line))
    if len(calls) != 1 or all_call_count != 1:
        return {"target_count": 1, "copy_call_count": len(calls),
                "body_call_count": all_call_count, "admitted": False,
                "reason": "target must contain one structured std::ptr::copy_nonoverlapping call"}
    block_index, copy_block, call, args, snippet, line = calls[0]
    if block_index != 0:
        return {"target_count": 1, "copy_call_count": 1, "body_call_count": 1,
                "admitted": False, "reason": "copy call is not in the MIR entry basic block"}
    statements = mir_helper.path(copy_block, "statements")
    writes: dict[str, list] = {}
    projected_self_writes = []
    unsupported_ops = []
    for position, statement in enumerate(statements):
        kind = mir_helper.path(statement, "kind")
        if contains_key(kind, "deinit") or contains_key(kind, "storageDead"):
            unsupported_ops.append({"statement_index": position,
                                    "kind": "deinit_or_storage_dead"})
        assign = mir_helper.assignment(statement)
        if assign is None:
            continue
        lhs = mir_helper.path(assign, "lhsPlace")
        projection = mir_helper.path(lhs, "projection")
        if local_name(lhs) == "_1" and projection:
            projected_self_writes.append(position)
        if not projection:
            writes.setdefault(local_name(lhs), []).append((position, assign))
    if projected_self_writes or unsupported_ops:
        return {"target_count": 1, "copy_call_count": 1, "body_call_count": 1,
                "projected_self_writes": projected_self_writes,
                "unsupported_pre_copy_ops": unsupported_ops, "admitted": False,
                "reason": "entry block has projected self writes, deinit, or storage kill"}
    operands = []
    origins = []
    for operand in args:
        place = next(iter(operand.values())) if (
            isinstance(operand, dict) and len(operand) == 1 and
            next(iter(operand)) in ("copy", "move")) else None
        name = local_name(place) if place is not None and not mir_helper.path(place, "projection") else None
        operands.append(name)
        origins.append(field_origin(name, writes, "_1", len(statements)) if name else None)
    expected_line = preparation.COPY_CALL.decode().strip()
    source_line = lines[line - 1].strip() if 1 <= line <= len(lines) else ""
    origins_valid = len(origins) == 3 and all(isinstance(origin, tuple) for origin in origins)
    field_origins = [field for field, _ in origins] if origins_valid else []
    origin_indices = [index for _, index in origins] if origins_valid else []
    admitted = (len(args) == 3 and all(operand is not None for operand in operands) and
                origins_valid and field_origins == [0, 1, 2] and
                all(index < len(statements) for index in origin_indices) and
                snippet.strip() == expected_line and
                source_line == expected_line)
    return {"target_count": 1, "copy_call_count": len(calls),
            "copy_call_name": MIR_COPY_CALLEE,
            "decoded_variance_admission": variance_field,
            "body_call_count": all_call_count, "unexpected_call_count": all_call_count - 1,
            "copy_block_index": block_index,
            "copy_preceding_statement_count": len(statements),
            "projected_self_writes": projected_self_writes,
            "unsupported_pre_copy_ops": unsupported_ops,
            "copy_call_source_line": line, "copy_call_snippet": snippet,
            "copy_call_operands": operands,
            "argument_field_origins": field_origins,
            "argument_field_read_statement_indices": origin_indices,
            "dynamic_count_from_self_len": origins_valid and origins[2][0] == 2,
            "target_body_sha256": sha(repr(body).encode()), "admitted": admitted,
            "reason": None if admitted else "MIR call operands are not linked to self.src/self.dst/self.len"}


def actual_drop_log_segment(log: str) -> tuple[str, list[str]]:
    lines = log.splitlines()
    headers = []
    header_re = re.compile(r"Verifying function '([^']+)'$")
    for index, line in enumerate(lines):
        match = header_re.search(line)
        if match:
            headers.append((index, match.group(1)))
    names = {TARGET, TARGET.replace("core::ops::Drop", "std::ops::Drop")}
    target_segments = []
    compatibility = []
    for position, (start, name) in enumerate(headers):
        end = headers[position + 1][0] if position + 1 < len(headers) else len(lines)
        segment = "\n".join(lines[start:end])
        if name in names:
            target_segments.append(segment)
        if "CopyOnDrop" in name and ("own" in name or "full_borrow" in name):
            compatibility.append(name)
    return (target_segments[0] if len(target_segments) == 1 else ""), compatibility


def ast_drop_call(ast_text: str, copy_line: int) -> dict:
    if not ast_text:
        return {"admitted": False, "reason": "proof AST missing"}
    tree = ast_helper.OcamlAstText(ast_text).parse()
    drop_funcs = [node for node in ast_helper.nodes(tree, "Func")
                  if len(node.args) > 8 and isinstance(node.args[4], str) and
                  node.args[4] in {TARGET,
                      TARGET.replace("core::ops::Drop", "std::ops::Drop")} and
                  "verified/lib.rs(" in repr(node.args[0])]
    # The canonical dump has one declaration and one body with the same name.
    # Func arg 7 is (ghost_body, runtime_body); arg 8 is the contract. Reading
    # arg 8 would wrongly search the pre/postcondition instead of Drop's body.
    declarations = []
    bodies = []
    for function in drop_funcs:
        shape = function.args[7]
        if not isinstance(shape, tuple) or len(shape) != 2 or \
                shape[0] != ast_helper.Sym("None"):
            return {"admitted": False, "actual_drop_function_count": len(drop_funcs),
                    "reason": "Drop Func has noncanonical ghost/runtime body pair"}
        if shape[1] == ast_helper.Sym("None"):
            declarations.append(function)
            continue
        if not isinstance(shape[1], ast_helper.Node) or shape[1].name != "Some" or \
                len(shape[1].args) != 1:
            return {"admitted": False, "actual_drop_function_count": len(drop_funcs),
                    "reason": "Drop Func has noncanonical runtime body option"}
        body_tuple = shape[1].args[0]
        if not isinstance(body_tuple, tuple) or len(body_tuple) != 3 or \
                not isinstance(body_tuple[1], list):
            return {"admitted": False, "actual_drop_function_count": len(drop_funcs),
                    "reason": "Drop Func body is not a source-located statement list"}
        bodies.append((function, body_tuple))
    if len(drop_funcs) != 2 or len(declarations) != 1 or len(bodies) != 1:
        return {"admitted": False, "actual_drop_function_count": len(drop_funcs),
                "declaration_count": len(declarations), "body_count": len(bodies),
                "reason": "actual Drop needs exactly one declaration and one runtime body"}
    # The AST's source location and exact function body must both identify the
    # extracted Drop. Do not let a support/helper function satisfy the call gate.
    candidates = []
    function, body_tuple = bodies[0]
    body_start, statements, body_end = body_tuple
    try:
        function_loc = ast_helper.loc(function.args[0])
        location_match = re.fullmatch(
            r"verified/lib\.rs\(([1-9][0-9]*),[0-9]+-([1-9][0-9]*),[0-9]+\)",
            function_loc)
        source_bounds = (location_match is not None and
                         int(location_match.group(1)) < copy_line <
                         int(location_match.group(2)) and
                         ast_helper.location_line(body_start) < copy_line and
                         ast_helper.location_line(body_end) > copy_line)
    except (ValueError, TypeError, ast_helper.AdmissionError):
        source_bounds = False
    copy_calls = [call for call in ast_helper.nodes(statements, "CallExpr")
                  if len(call.args) == 6 and call.args[1] == AST_COPY_CALLEE]
    switches = [switch for switch in ast_helper.nodes(statements, "SwitchStmt")
                if len(switch.args) == 3 and switch.args[1] in copy_calls]
    if source_bounds and len(copy_calls) == 1 and len(switches) == 1:
        call = copy_calls[0]
        switch = switches[0]
        arguments = call.args[4]
        argument_vars = []
        if isinstance(arguments, list) and len(arguments) == 3:
            for argument in arguments:
                try:
                    argument_vars.append(ast_helper.var(
                        ast_helper.narg(argument, "LitPat", 1)[0]))
                except ast_helper.AdmissionError:
                    argument_vars.append(None)
        clauses = switch.args[2]
        outcomes = []
        if isinstance(clauses, list) and len(clauses) == 2:
            for clause in clauses:
                if isinstance(clause, ast_helper.Node) and clause.name == "SwitchStmtClause" and \
                        len(clause.args) == 3 and isinstance(clause.args[2], list):
                    outcome = clause.args[1]
                    outcomes.append(outcome.args[1] if isinstance(outcome, ast_helper.Node)
                                    and outcome.name == "CallExpr" and len(outcome.args) == 6
                                    else None)
                else:
                    outcomes.append(None)
        dynamic = (argument_vars == ["$_3", "$_4", "$_5"] and
                   outcomes == ["returning", "unwinding"] and
                   any(isinstance(stmt, ast_helper.Node) and stmt.name == "ReturnStmt"
                       for stmt in statements) and
                   len(ast_helper.nodes(clauses[1].args[2], "ReturnStmt")) == 1 and
                   ast_helper.location_line(call.args[0]) == copy_line and
                   ast_helper.location_line(switch.args[0]) == copy_line)
        candidates.append({"function": function.args[4], "line": copy_line,
                           "callee": call.args[1], "argument_vars": argument_vars,
                           "normal_unwind_clauses": outcomes,
                           "dynamic_count": dynamic})
    admitted = len(candidates) == 1 and candidates[0]["dynamic_count"]
    return {"admitted": admitted, "actual_drop_function_count": len(drop_funcs),
            "declaration_count": len(declarations), "body_count": len(bodies),
            "source_bounds_match": source_bounds,
            "body_copy_call_count": len(copy_calls),
            "copy_call_candidates": candidates,
            "reason": None if admitted else "actual Drop AST lacks one dynamic count-n copy call"}


def verifier_admission(case_dir: Path, case_name: str, metadata: dict,
                       stage_status: int) -> dict:
    log = (case_dir / "verifast.log").read_text(errors="replace")
    segment, compatibility = actual_drop_log_segment(log)
    target_log_count = int(bool(segment))
    copy_line = metadata["copy_call_line"]
    call = re.compile(rf"verified/lib\.rs\({copy_line},[0-9]+(?:-[0-9]+(?:,[0-9]+)?)?\): Verifying call$")
    statement = re.compile(rf"verified/lib\.rs\({copy_line},[0-9]+(?:-[0-9]+(?:,[0-9]+)?)?\): (?:note: )?Executing statement$")
    target_execution = [line for line in segment.splitlines()
                        if "verified/lib.rs(" in line and "Executing statement" in line]
    body_exec = any(re.search(rf"verified/lib\.rs\({copy_line},[0-9]+(?:-[0-9]+(?:,[0-9]+)?)?\): (?:note: )?Executing statement$", line)
                    for line in target_execution)
    return_records = len(re.findall(r"Executing return statement", segment))
    leak_records = len(re.findall(r"Leak check\.", segment))
    errors = [line for line in segment.splitlines() if re.search(r"\berror:", line, re.I)]
    global_errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    dead = [line for line in segment.splitlines() if re.search(r"dead code", line, re.I)]
    copy_call_executed = sum(1 for line in segment.splitlines() if call.search(line))
    copy_statement_executed = sum(1 for line in segment.splitlines() if statement.search(line))
    ast_path = case_dir / "proof-ast.ml"
    ast = ast_path.read_text(errors="replace") if ast_path.is_file() else ""
    ast_call = ast_drop_call(ast, copy_line)
    target_line = metadata.get("negative_target_line")
    exact_false = False
    if case_name == "first_body_false" and target_line:
        expected_column_start = preparation.FALSE_LINE.index(b"false") + 1
        expected_column_end = expected_column_start + len(b"false")
        if (metadata.get("negative_predicate") != "false" or
                metadata.get("negative_column_start") != expected_column_start or
                metadata.get("negative_column_end") != expected_column_end):
            raise RuntimeError("first-body false control oracle differs from predeclared TARGET columns")
        exact_false = bool(re.search(
            rf"verified/lib\.rs\({target_line},{metadata['negative_column_start']}-{metadata['negative_column_end']}\): error: Assertion might not hold\. \(Cannot prove false\.\)",
            segment))
    successful = (case_name == "positive" and target_log_count == 1 and body_exec and
        copy_call_executed == 1 and copy_statement_executed >= 1 and
        return_records >= 1 and leak_records >= 1 and not global_errors and not dead and
        stage_status == 0 and "0 errors found" in log and ast_call["admitted"])
    expected_negative = (case_name == "first_body_false" and target_log_count == 1 and
        exact_false and len(errors) == 1 and len(global_errors) == 1 and
        not dead and ast_call["admitted"] and stage_status == 1 and
        return_records == 0 and leak_records == 0 and
        copy_call_executed == 0 and copy_statement_executed == 0)
    return {"target_body_count": target_log_count, "body_statement_seen": body_exec,
            "copy_call_verifying_records": copy_call_executed,
            "copy_call_execution_records": copy_statement_executed,
            "return_records": return_records, "leak_checks": leak_records,
            "errors": errors, "global_error_lines": global_errors,
            "dead_code_records": dead,
            "ast_sha256": sha(ast.encode()) if ast else None,
            "ast_nonempty": bool(ast), "ast_drop_call": ast_call,
            "compatibility_functions_observed": compatibility,
            "compatibility_path_status": "CANDIDATE_FUNCTIONS_ONLY_NOT_ESTABLISHED" if compatibility else "NOT_ESTABLISHED",
            "exact_false_control": exact_false,
            "positive_gate": successful, "matched_negative_gate": expected_negative}


def run_case(case_name: str, metadata: dict, args, env: dict[str, str]) -> dict:
    case_dir = args.evidence / "cases" / case_name
    initial = hashes(case_dir)
    if (initial["original/lib.rs"] != metadata.get("original_sha256") or
            initial["verified/lib.rs"] != metadata.get("verified_sha256") or
            initial["small_sort_source"] != preparation.SOURCE_SHA256):
        raise RuntimeError(f"{case_name}: extracted source hashes differ from pinned case/source metadata")
    (case_dir / "source-before.json").write_text(json.dumps(initial, indent=2) + "\n")
    exporter = run_stage(case_dir, "exporter", [
        str(args.tool_home / "bin/vf-rust-mir-exporter"), "verified/lib.rs",
        f"--sysroot={args.compiler_sysroot}", "--edition", "2021", "--crate-type", "lib",
        "--vf-rust-mir-exporter:preprocess-readonly"], env,
        timeout_seconds=args.stage_seconds, stdout_name="compiler-mir.bin")
    if exporter == 0:
        include_dirs = list(dict.fromkeys([args.schema.parent, *args.capnp_include]))
        capnp_args = ["capnp", "decode"]
        for directory in include_dirs:
            capnp_args.extend(["-I", str(directory)])
        capnp_args.extend([str(args.schema), "VfMir"])
        decoder = run_stage(case_dir, "decode", capnp_args, env,
                            timeout_seconds=args.stage_seconds,
                            stdin=case_dir / "compiler-mir.bin")
    else:
        decoder = 125
        not_run(case_dir, "decode", "not run because readonly MIR exporter failed")
    (case_dir / "compiler-mir-sha256.txt").write_text(file_sha(case_dir / "compiler-mir.bin") + "\n")
    vf_status = run_stage(case_dir, "verifast", [
        str(args.tool_home / "bin/verifast"), "-rustc_args", "--edition 2021",
        "-verbose", "1", "-dump_ast_with_locs", "proof-ast.ml", "verified/lib.rs"],
        env, combine=True, timeout_seconds=args.verifier_seconds)
    refinement = run_stage(case_dir, "refinement", [
        str(args.tool_home / "bin/refinement-checker"), "--rustc-args", "--edition 2021",
        "original/lib.rs", "verified/lib.rs"], env,
        timeout_seconds=args.stage_seconds)
    after = hashes(case_dir)
    unchanged = initial == after and all(
        json.loads(path.read_text()).get("source_unchanged") is True
        for path in case_dir.glob("*-stage.json")
        if json.loads(path.read_text()).get("stage") not in {"decode"} or
           json.loads(path.read_text()).get("status") != "NOT_RUN")
    try:
        mir = mir_admission(case_dir) if decoder == 0 else {
        "target_count": 0, "copy_nonoverlapping_lines": [],
        "copy_call_operands": [],
        "dynamic_third_operand_recognized": False, "admitted": False}
    except Exception as error:
        mir = {"admitted": False, "reason": f"structured MIR admission failed closed: {error}"}
    try:
        proof = verifier_admission(case_dir, case_name, metadata, vf_status)
    except Exception as error:
        proof = {"positive_gate": False, "matched_negative_gate": False,
                 "reason": f"AST/log admission failed closed: {error}"}
    stages = {"exporter": exporter, "decode": decoder,
              "verifast": vf_status, "refinement": refinement}
    passed = (all(code == 0 for code in stages.values()) and unchanged and
              mir["admitted"] and proof["positive_gate"])
    matched = (exporter == 0 and decoder == 0 and vf_status == 1 and
               refinement == 0 and unchanged and
               mir["admitted"] and proof["matched_negative_gate"])
    row = {"case": case_name, "stages": stages, "source_unchanged_at_every_stage": unchanged,
           "initial_source_hashes": initial, "final_source_hashes": after,
           "mir_admission": mir, "verifier_admission": proof,
           "classification": "PASS_COMPONENT_ONLY" if passed else
               "EXPECTED_FALSE_ASSERTION" if matched else "INCONCLUSIVE",
           "accepted": False,
           "scope": "direct generic CopyOnDrop body diagnostic; not caller cleanup or whole sort proof"}
    (case_dir / "classification.json").write_text(json.dumps(row, indent=2) + "\n")
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool-home", type=Path, required=True)
    parser.add_argument("--compiler-sysroot", type=Path, required=True)
    parser.add_argument("--schema", type=Path, required=True)
    parser.add_argument("--capnp-include", type=Path, action="append", default=[])
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--profile-evidence", type=Path, required=True)
    parser.add_argument("--stage-seconds", type=int, default=90)
    parser.add_argument("--verifier-seconds", type=int, default=TIMEOUT_SECONDS)
    args = parser.parse_args()
    if not 1 <= args.stage_seconds <= 600 or not 1 <= args.verifier_seconds <= 600:
        raise RuntimeError("per-stage limits must be between 1 and 600 seconds")
    if args.profile not in {"stock-26.10", EXPERIMENTAL_PROFILE}:
        raise RuntimeError("profile must name the pinned stock-26.10 or current six-patch experimental profile")
    provider, proof_sha = require_hosted_cloud()
    if args.evidence.exists():
        raise RuntimeError("refusing to reuse Drop evidence directory")
    if not args.tool_home.is_dir() or not args.schema.is_file() or not args.compiler_sysroot.is_dir():
        raise RuntimeError("tool-home, schema, and compiler sysroot must exist")
    if any(not directory.is_dir() for directory in args.capnp_include):
        raise RuntimeError("every --capnp-include path must be an existing directory")
    for path in ("bin/verifast", "bin/vf-rust-mir-exporter", "bin/refinement-checker"):
        if not (args.tool_home / path).is_file():
            raise RuntimeError(f"missing pinned tool: {args.tool_home / path}")
    if not args.profile_evidence.is_dir():
        raise RuntimeError("--profile-evidence must name the exact build evidence directory")
    profile_pins = validate_profile(args)
    if file_sha(args.schema) != STOCK_SCHEMA_SHA:
        raise RuntimeError("MIR schema SHA differs from the frozen profile")
    args.evidence.mkdir(parents=True)
    source = ROOT / "library/core/src/slice/sort/shared/smallsort.rs"
    extraction = preparation.extract(source, args.evidence / "cases", args.evidence / "extraction.json")
    if (extraction.get("source_sha256") != preparation.SOURCE_SHA256 or
            extraction.get("source_git_blob") != preparation.SOURCE_GIT_BLOB or
            extraction.get("contract_sha256") != sha(preparation.CONTRACT)):
        raise RuntimeError("exact-source extraction report does not match the pinned preparation contract")
    libdir = args.compiler_sysroot / "lib"
    env = dict(os.environ)
    env["LD_LIBRARY_PATH"] = ":".join(filter(None, [str(libdir),
        str(args.tool_home / "bin"), env.get("LD_LIBRARY_PATH", "")]))
    tool_hashes = {}
    for rel in ("bin/verifast", "bin/vf-rust-mir-exporter", "bin/refinement-checker",
                profile_pins["prelude_path"]):
        tool_hashes[rel] = file_sha(args.tool_home / rel)
    rustc = shutil.which("rustc")
    if rustc is None:
        raise RuntimeError("pinned hosted rustc is not available on PATH")
    capnp = shutil.which("capnp")
    if capnp is None:
        raise RuntimeError("hosted Cap'n Proto decoder is not available on PATH")
    compiler_version = subprocess.run([rustc, "--version", "--verbose"],
        capture_output=True, text=True, check=True).stdout
    if (os.environ.get("RUSTUP_TOOLCHAIN") != "nightly-2026-09-25" or
            "commit-hash: f7575a9da8e4a4fca3b5668d5a2ea7476db44b3f" not in compiler_version or
            "host: x86_64-unknown-linux-gnu" not in compiler_version or
            platform.machine().lower() not in {"x86_64", "amd64"}):
        raise RuntimeError("compiler is not pinned nightly-2026-09-25 x86_64-unknown-linux-gnu")
    rustc_sysroot = subprocess.run([rustc, "--print", "sysroot"],
        capture_output=True, text=True, check=True).stdout.strip()
    if Path(rustc_sysroot).resolve() != args.compiler_sysroot.resolve():
        raise RuntimeError("PATH rustc sysroot differs from --compiler-sysroot")
    compiler_driver_hashes = {}
    for driver in sorted((args.compiler_sysroot / "lib").glob("librustc_driver-*.so")):
        compiler_driver_hashes[str(driver)] = file_sha(driver)
    if not compiler_driver_hashes:
        raise RuntimeError("compiler sysroot has no librustc_driver shared object")
    header = {"profile": args.profile, "profile_evidence": str(args.profile_evidence),
              "profile_pins": profile_pins, "cloud_build_id": provider["build_id"],
              "cloud_project": provider["project"], "cloud_region": provider["region"],
              "proof_sha": proof_sha, "provider": "cloud-build",
              "small_sort_source_sha256": file_sha(source),
              "small_sort_source_git_blob": preparation.SOURCE_GIT_BLOB,
              "tool_hashes": tool_hashes,
              "compiler_rustc_path": rustc,
              "compiler_rustc_sha256": file_sha(Path(rustc)),
              "capnp_path": capnp,
              "capnp_sha256": file_sha(Path(capnp)),
              "compiler_version_verbose": compiler_version,
              "compiler_rustc_sysroot": rustc_sysroot,
              "compiler_driver_hashes": compiler_driver_hashes,
              "compiler_sysroot": str(args.compiler_sysroot),
              "schema_sha256": file_sha(args.schema),
              "capnp_include_dirs": [str(path) for path in
                  dict.fromkeys([args.schema.parent, *args.capnp_include])],
              "stage_timeout_seconds": args.verifier_seconds,
              "semantic_profile_accepted": False}
    (args.evidence / "environment.json").write_text(json.dumps(header, indent=2) + "\n")
    rows = {}
    for name in ("positive", "first_body_false"):
        rows[name] = run_case(name, json.loads((args.evidence / "extraction.json").read_text())
                              ["cases"][name], args, env)
        (args.evidence / "results.json").write_text(json.dumps({
            "profile": args.profile, "accepted": False, "cases": rows}, indent=2) + "\n")
    positive = rows["positive"]["classification"] == "PASS_COMPONENT_ONLY"
    control = rows["first_body_false"]["classification"] == "EXPECTED_FALSE_ASSERTION"
    aggregate = {"stages_collected": True,
                 "classification": "PARTIAL_DIAGNOSTIC" if positive and control else "INCONCLUSIVE",
                 "accepted": False, "positive_component_pass": positive,
                 "matched_false_control": control,
                 "compatibility_note": "historically observed private own=false compatibility remains pending current AST/log confirmation; explicit Drop body req is checked independently",
                 "trusted_dependency_note": "stock count-n copy_nonoverlapping specification remains a trusted dependency; this does not prove caller cleanup admission",
                 "cases": {name: row["classification"] for name, row in rows.items()}}
    (args.evidence / "aggregate.json").write_text(json.dumps(aggregate, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"CopyOnDrop hosted proof preparation failed: {error}", file=sys.stderr)
        raise SystemExit(2)
