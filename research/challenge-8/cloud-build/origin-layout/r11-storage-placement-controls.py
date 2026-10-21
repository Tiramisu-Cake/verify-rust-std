#!/usr/bin/env python3
"""Hosted source-bound R11 placement controls for the invariant unit temporary.

Importing this module is inert.  The runner only replays the already captured
compiler MIR through copied hosted tools; it does not extract MIR or award proof
credit.  Every result remains diagnostic, including a matching placement cut.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import sys
import uuid

HERE = Path(__file__).resolve().parent
PROFILE = "experimental-merge-label-storage-r11-v1"
CAMPAIGN = "r11-storage-placement-controls-v1"
STAGES = ("exporter", "decode", "refinement", "verifast")
TOOLS = ("vf-rust-mir-exporter", "verifast", "refinement-checker")
MUTANTS = ("missing_live", "missing_dead", "wrong_dead_local", "duplicate_live",
           "target_span_mismatch", "ordinary_non_unit_destination",
           "extra_address_taken_use")
DIAGNOSTIC = "R11 invariant placement binding refused"
CUT_PREFIX = "R11_INVARIANT_CUT "
EXEC_PREFIX = "R11_EXEC "
INVARIANT = b"inv thread_token(t)"
SETUP_CODES = {124, 125, 126, 127, 134, 137, 139}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_sha(path: Path) -> str:
    return _sha(path.read_bytes())


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"required hosted helper unavailable: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _not_run(name: str, reason: str, **extra) -> dict:
    return {"case": name, "classification": "NOT_RUN", "matched": False,
            "accepted": False, "proof_credit": False, "reason": reason, **extra}


def _inconclusive(name: str, reason: str, **extra) -> dict:
    return {"case": name, "classification": "INCONCLUSIVE", "matched": False,
            "accepted": False, "proof_credit": False, "reason": reason, **extra}


def _hosted_identity_matches(provider, proof_sha, run_identity: dict) -> bool:
    """Compare the required hosted identity, allowing unrelated metadata."""
    expected = run_identity.get("provider") if type(run_identity) is dict else None
    keys = ("provider", "build_id", "project", "region")
    if type(provider) is not dict or type(expected) is not dict:
        return False
    for key in keys:
        actual_value = provider.get(key)
        expected_value = expected.get(key)
        if (type(actual_value) is not str or not actual_value or
                type(expected_value) is not str or not expected_value or
                actual_value != expected_value):
            return False
    return type(proof_sha) is str and proof_sha == run_identity.get("proof_sha")


def _source_pair(case: Path, record: dict) -> tuple[bytes, bytes]:
    if type(record) is not dict or record.get("profile") != PROFILE or \
            record.get("prefix") is not False or record.get("mutation") is not None:
        raise ValueError("source_record is not the unmutated R11 fullbody case")
    original = (case / "original/lib.rs").read_bytes()
    verified = (case / "verified/lib.rs").read_bytes()
    if (_sha(original) != record.get("original_sha256") or
            _sha(verified) != record.get("verified_sha256")):
        raise ValueError("R11 source pair differs from source_record hashes")
    if verified.count(INVARIANT) != 1:
        raise ValueError("expected exactly one source-bound thread_token invariant")
    if record.get("verified_sha256") is None:
        raise ValueError("source_record is missing verified source identity")
    return original, verified


def _run_identity(validated_run, args, env: dict, profile_binding: dict) -> dict:
    if type(validated_run) is not dict:
        raise ValueError("parent-validated current R11 run tuple is required")
    profile = getattr(args, "profile", None)
    if profile != PROFILE or validated_run.get("profile") != PROFILE:
        raise ValueError("selected and parent-validated profiles must both be R11")
    if validated_run.get("accepted") is not False:
        raise ValueError("parent profile receipt must remain explicitly unaccepted")
    # The first-callback API passes the original parent-validated profile
    # receipt. Normalize its provider fields only after checking the selected
    # active profile and exact binary hashes below.
    provider = validated_run.get("provider")
    if type(provider) is not dict:
        raise ValueError("parent-validated provider receipt is absent")
    build_id = validated_run.get("cloud_build_id", provider.get("build_id"))
    try:
        if type(build_id) is not str or str(uuid.UUID(build_id)) != build_id:
            raise ValueError
    except (ValueError, AttributeError):
        raise ValueError("parent-validated Cloud Build UUID is malformed") from None
    if (type(provider) is not dict or provider.get("provider") != "cloud-build" or
            provider.get("build_id") != build_id or
            provider.get("project") != env.get("CLOUD_BUILD_PROJECT_ID") or
            provider.get("region") != env.get("CLOUD_BUILD_REGION") or
            env.get("CLOUD_BUILD_ID") != build_id or
            env.get("PROOF_SHA") != validated_run.get("proof_sha")):
        raise ValueError("parent Build/proof/provider identity differs from hosted environment")
    proof_sha = validated_run.get("proof_sha")
    source_sha = validated_run.get("source_sha256")
    profile_sha = validated_run.get("profile_sha256", profile_binding["profile_sha256"])
    tool_commit = validated_run.get(
        "tool_commit", validated_run.get("effective_tool_commit",
                                          profile_binding.get("effective_tool_commit")))
    hashes = validated_run.get("tool_sha256", validated_run.get("executable_hashes"))
    if type(proof_sha) is not str or not re.fullmatch(r"[0-9a-f]{40}", proof_sha):
        raise ValueError("current proof SHA is malformed")
    if type(source_sha) is not str or not re.fullmatch(r"[0-9a-f]{64}", source_sha):
        raise ValueError("current source SHA is malformed")
    if profile_sha != profile_binding["profile_sha256"]:
        raise ValueError("current profile SHA differs from parent-validated tuple")
    if type(tool_commit) is not str or not re.fullmatch(r"[0-9a-f]{40}", tool_commit):
        raise ValueError("current effective tool commit is malformed")
    if type(hashes) is not dict or set(hashes) != set(TOOLS) or any(
            type(hashes.get(key)) is not str or
            not re.fullmatch(r"[0-9a-f]{64}", hashes[key]) for key in TOOLS):
        raise ValueError("parent tool binary SHA map is malformed")
    tool_home = getattr(args, "tool_home", None)
    if tool_home is None:
        raise ValueError("current tool-home path is unavailable")
    actual = {name: _file_sha(Path(tool_home) / "bin" / name) for name in TOOLS}
    if actual != hashes:
        raise ValueError("current tool binaries differ from parent-validated SHA map")
    if profile_binding.get("effective_tool_commit") != tool_commit:
        raise ValueError("active R11 profile tool commit differs from validated tuple")
    return {"cloud_build_id": build_id, "proof_sha": proof_sha,
            "source_sha256": source_sha, "profile": PROFILE,
            "profile_sha256": profile_sha, "tool_commit": tool_commit,
            "tool_sha256": dict(hashes),
            "provider": {key: provider[key] for key in ("provider", "build_id", "project", "region")}}


def _profile_binding(args, env: dict) -> dict:
    selected = getattr(args, "profile", None)
    path_value = env.get("SMALLSORT_MERGE_PROFILE") if type(env) is dict else None
    if selected != PROFILE or not path_value:
        raise ValueError("R11 profile path and selected profile are required")
    path = Path(path_value)
    raw = path.read_bytes()
    data = json.loads(raw)
    if type(data) is not dict or data.get("profile") != PROFILE or data.get("accepted") is not False:
        raise ValueError("active profile is not the exact unaccepted R11 profile")
    return {"profile": PROFILE, "profile_sha256": _sha(raw),
            "profile_path": str(path.resolve()),
            "effective_tool_commit": data.get("effective_tool_commit")}


def _target_line(verified: bytes) -> tuple[int, bytes]:
    lines = verified.splitlines()
    found = [(i + 1, line) for i, line in enumerate(lines) if INVARIANT in line]
    if len(found) != 1:
        raise ValueError("source invariant line is absent or ambiguous")
    return found[0]


def _mutation_plan(decoded: str, verified: bytes) -> dict:
    """Bind a safe structural MIR edit to the invariant's exact source line.

    This intentionally requires the reviewed exporter text spelling.  Unknown
    schemas or non-unique destinations are setup failures, never controls.
    """
    helper = _load("r11_capnp_text_helpers", HERE / "first-callback-admission-controls.py")
    source_line, source_text = _target_line(verified)
    _, _, body, blocks = _body_parts(decoded, helper)
    candidates = []
    for bstart, bend, block in blocks:
        if "VeriFast_ghost_command" not in block:
            continue
        terminator = helper._field_text(block, "terminator")
        locations = re.findall(
            r"\bsourceInfo\s*=\s*\(\s*span\s*=.*?\bline\s*=\s*(\d+)",
            terminator, re.S)
        if len(locations) == 1 and int(locations[0]) == source_line:
            candidates.append((bstart, bend, block, terminator))
    if len(candidates) != 1:
        raise ValueError("cannot uniquely bind ghost-call terminator to invariant source line")
    call_block_start, call_block_end, call_block, call = candidates[0]
    if "VeriFast_ghost_command" not in call:
        raise ValueError("source line does not select the ghost-command terminator")
    start = body.find(call)
    if start < 0:
        raise ValueError("bound ghost-call terminator was lost in selected Body")
    destination = re.findall(
        r"\bdestination\s*=\s*\(\s*local\s*=\s*\(\s*name\s*=\s*\"([^\"]+)\"",
        call)
    if len(destination) != 1:
        raise ValueError("ghost-command destination is not a unique bare local")
    temp = destination[0]
    live_rows = [(lo, hi, stmt) for lo, hi, stmt in _statement_records(call_block, helper)
                 if re.search(rf"\bstorageLive\s*=\s*\(\s*name\s*=\s*\"{re.escape(temp)}\"", stmt)]
    if len(live_rows) != 1 or call_block.find(live_rows[0][2]) >= call_block.find(call):
        raise ValueError("unit destination has no unique preceding StorageLive in call block")
    target_id = _option_block_index(call, helper)
    successor = [row for row in blocks if _block_index(row[2], helper) == target_id]
    if len(successor) != 1:
        raise ValueError("ghost-call successor basic block is not unique")
    dead_rows = [(lo, hi, stmt) for lo, hi, stmt in _statement_records(successor[0][2], helper)
                 if re.search(rf"\bstorageDead\s*=\s*\(\s*name\s*=\s*\"{re.escape(temp)}\"", stmt)]
    if len(dead_rows) != 1:
        raise ValueError("ghost-call successor lacks one exact destination StorageDead")
    if source_text.count(b"inv thread_token(t)") != 1:
        raise ValueError("source invariant text is not unique on its line")
    edges = _edge_signature(decoded, helper, temp)
    return {"source_line": source_line, "source_line_text": source_text.decode("utf-8", "replace"),
            "temp_local": temp, "body_start": decoded.find(body),
            "call_start": decoded.find(body) + start, "call_end": decoded.find(body) + start + len(call),
            "call_text": call, "body_text": body,
            "successor_id": target_id, "native_edges": edges}


def _body_parts(decoded: str, helper):
    body_start, body_end, body = helper._unique_function_body(decoded)
    list_start, list_end, block_items = helper._field_list(body, "basicBlocks")
    list_text = body[list_start + 1:list_end - 1]
    blocks = []
    for lo, hi in helper._item_spans(list_text):
        blocks.append((body_start + list_start + 1 + lo,
                       body_start + list_start + 1 + hi,
                       list_text[lo:hi]))
    return body_start, body_end, body, blocks


def _edge_signature(decoded: str, helper, temp_local: str) -> dict:
    _, _, _, blocks = _body_parts(decoded, helper)
    terms = []
    for _, _, block in blocks:
        term = helper._field_text(block, "terminator")
        if "VeriFast_ghost_command" in term:
            if _destination_local(term, helper) == temp_local:
                terms.append(term)
    if len(terms) != 1:
        raise ValueError("selected temp destination must bind exactly one ghost-command terminator")
    return {"target": helper._field_text(terms[0], "target"),
            "unwindAction": helper._field_text(terms[0], "unwindAction")}


def _destination_local(terminator: str, helper) -> str | None:
    destination = helper._field_text(terminator, "destination")
    names = re.findall(r"\bname\s*=\s*\"([^\"]+)\"", destination)
    return names[0] if len(names) == 1 else None


def _terminator_source_line(terminator: str) -> int | None:
    lines = re.findall(
        r"\bsourceInfo\s*=\s*\(\s*span\s*=.*?\bline\s*=\s*(\d+)",
        terminator, re.S)
    return int(lines[0]) if len(lines) == 1 else None


def _preserve_edges(before: str, after: str, helper, temp_local: str) -> str:
    if (_edge_signature(before, helper, temp_local) !=
            _edge_signature(after, helper, temp_local)):
        raise ValueError("MIR mutation changed the native call target or unwind cleanup edge")
    return after


def _statement_records(block: str, helper):
    start, end, values = helper._field_list(block, "statements")
    text = block[start + 1:end - 1]
    return [(start + 1 + lo, start + 1 + hi, text[lo:hi])
            for lo, hi in helper._item_spans(text)]


def _option_block_index(terminator: str, helper) -> str:
    option = helper._field_text(terminator, "target")
    target = helper._field_text(option, "something")
    indices = re.findall(r"\bindex\s*=\s*(\d+)\b", target)
    if len(indices) != 1:
        raise ValueError("call successor has no unique BasicBlockId.index")
    return indices[0]


def _block_index(block: str, helper) -> str:
    record = block.strip()
    if (not record.startswith("(") or
            helper._matching_end(record, 0, "(", ")") != len(record)):
        raise ValueError("BasicBlock is not one balanced outer record")
    fields = helper._split_items(record[1:-1])
    id_fields = [item for item in fields if re.match(r"^\s*id\s*=", item)]
    if len(id_fields) != 1:
        raise ValueError("BasicBlock must have exactly one top-level id field")
    ident = helper._field_text(id_fields[0], "id")
    indices = re.findall(r"\bindex\s*=\s*(\d+)\b", ident)
    if len(indices) != 1:
        raise ValueError("BasicBlock id has no unique BasicBlockId.index")
    return indices[0]


def _remove_statement(block: str, start: int, end: int, helper) -> str:
    list_start, list_end, _ = helper._field_list(block, "statements")
    list_text = block[list_start + 1:list_end - 1]
    # Statement offsets are relative to the block; list offsets are relative to
    # that same block. Remove exactly one item and one adjacent separator.
    a, b = start - (list_start + 1), end - (list_start + 1)
    if a < 0 or b > len(list_text) or a >= b:
        raise ValueError("statement span escaped selected statements list")
    if b < len(list_text) and list_text[b:].lstrip().startswith(","):
        comma = list_text.find(",", b)
        list_text = list_text[:a] + list_text[comma + 1:]
    elif a > 0 and "," in list_text[:a]:
        comma = list_text.rfind(",", 0, a)
        list_text = list_text[:comma] + list_text[b:]
    else:
        list_text = list_text[:a] + list_text[b:]
    return block[:list_start + 1] + list_text + block[list_end - 1:]


def _locate_nodes(decoded: str, plan: dict, helper) -> dict:
    body_start, body_end, body, blocks = _body_parts(decoded, helper)
    local_name = plan["temp_local"]
    candidates = []
    for block_start, block_end, block in blocks:
        if "VeriFast_ghost_command" not in block:
            continue
        term = helper._field_text(block, "terminator")
        if ("VeriFast_ghost_command" in term and
                _terminator_source_line(term) == plan["source_line"] and
                _destination_local(term, helper) == local_name):
            candidates.append((block_start, block_end, block, term))
    if len(candidates) != 1:
        raise ValueError("invariant ghost call does not select one MIR basic block")
    bstart, bend, block, term = candidates[0]
    statement_rows = _statement_records(block, helper)
    live_rows, dead_rows = [], []
    for lo, hi, statement in statement_rows:
        if re.search(rf"\bstorageLive\s*=\s*\(\s*name\s*=\s*\"{re.escape(local_name)}\"", statement):
            live_rows.append((lo, hi, statement))
        if re.search(rf"\bstorageDead\s*=\s*\(\s*name\s*=\s*\"{re.escape(local_name)}\"", statement):
            dead_rows.append((lo, hi, statement))
    target_id = _option_block_index(term, helper)
    successors = [row for row in blocks if _block_index(row[2], helper) == target_id]
    if len(successors) != 1:
        raise ValueError("ghost-call successor basic block is not unique")
    sstart, send, successor = successors[0]
    dead_rows = [(lo, hi, statement) for lo, hi, statement in _statement_records(successor, helper)
                 if re.search(rf"\bstorageDead\s*=\s*\(\s*name\s*=\s*\"{re.escape(local_name)}\"", statement)]
    if len(live_rows) != 1 or len(dead_rows) != 1:
        raise ValueError("selected MIR path lacks unique destination Live and successor Dead")
    term_rel = block.find(term)
    if not live_rows[0][1] <= term_rel:
        raise ValueError("MIR invariant call is not between the selected Live/Dead statements")
    return {"body_start": body_start, "body_end": body_end, "body": body,
            "block_start": bstart, "block_end": bend, "block": block,
            "successor_start": sstart, "successor_end": send, "successor": successor,
            "live": live_rows[0], "dead": dead_rows[0], "term": term,
            "temp_local": local_name, "helper": helper}


def _replace_item(text: str, start: int, end: int, replacement: str) -> str:
    return text[:start] + replacement + text[end:]


def _mutate_decoded(decoded: str, name: str, plan: dict) -> str:
    helper = _load("r11_capnp_text_helpers_mut", HERE / "first-callback-admission-controls.py")
    original_decoded = decoded
    nodes = _locate_nodes(decoded, plan, helper)
    block, live = nodes["block"], nodes["live"]
    successor, dead = nodes["successor"], nodes["dead"]
    if name == "missing_live":
        block = _remove_statement(block, live[0], live[1], helper)
    elif name == "missing_dead":
        successor = _remove_statement(successor, dead[0], dead[1], helper)
        changed = (decoded[:nodes["successor_start"]] + successor +
                   decoded[nodes["successor_end"]:])
        return _preserve_edges(original_decoded, changed, helper, nodes["temp_local"])
    elif name == "wrong_dead_local":
        if dead[2].count(nodes["temp_local"]) != 1:
            raise ValueError("dead local identifier is not uniquely writable")
        _, _, decls = helper._field_list(nodes["body"], "localDecls")
        declared = [match.group(1) for item in decls for match in re.finditer(
            r"\bid\s*=\s*\(\s*name\s*=\s*\"([^\"]+)\"", item)]
        alternatives = [name for name in declared if name == "_0" and
                        name != nodes["temp_local"]]
        if len(alternatives) != 1:
            raise ValueError("canonical _0 alternate local is not uniquely declared for wrong-dead binding control")
        successor = successor[:dead[0]] + dead[2].replace(nodes["temp_local"],
                     alternatives[0], 1) + successor[dead[1]:]
        changed = (decoded[:nodes["successor_start"]] + successor +
                   decoded[nodes["successor_end"]:])
        return _preserve_edges(original_decoded, changed, helper, nodes["temp_local"])
    elif name == "duplicate_live":
        block = block[:live[1]] + ", " + live[2] + block[live[1]:]
    elif name == "target_span_mismatch":
        term = nodes["term"]
        pattern = re.compile(r"(\bline\s*=\s*)" + str(plan["source_line"]) + r"\b")
        changed, count = pattern.subn(lambda m: m.group(1) + str(plan["source_line"] + 1), term, count=1)
        if count != 1:
            raise ValueError("ghost-call source span did not have one exact target line")
        block = block.replace(term, changed, 1)
    elif name == "ordinary_non_unit_destination":
        body = nodes["body"]
        _, _, declarations = helper._field_list(body, "localDecls")
        unit_decl = [item for item in declarations if re.search(
            rf"\bid\s*=\s*\(\s*name\s*=\s*\"{re.escape(nodes['temp_local'])}\"", item)]
        if len(unit_decl) != 1:
            raise ValueError("destination local declaration is not unique")
        ty = helper._field_text(unit_decl[0], "ty")
        if not ty or "tuple = []" not in ty:
            raise ValueError("destination local is not encoded as the empty tuple unit type")
        other_ty = "(kind = (uInt = (u64 = void)))"
        old_record = unit_decl[0]
        new_record = old_record.replace(ty, other_ty, 1)
        if body.count(old_record) != 1:
            raise ValueError("destination LocalDecl record is not unique in Body")
        body = body.replace(old_record, new_record, 1)
        decoded = decoded.replace(nodes["body"], body, 1)
        return _preserve_edges(original_decoded, decoded, helper, nodes["temp_local"])
    elif name == "extra_address_taken_use":
        # No second typed use is injected unless the exporter exposes an exact,
        # unique address-taking MIR place. This source currently has no reviewed
        # mutation template, so setup remains explicitly unsupported.
        raise ValueError("no reviewed unique typed address-taking insertion point")
    else:
        raise ValueError(f"unsupported R11 mutation {name}")
    changed = decoded[:nodes["block_start"]] + block + decoded[nodes["block_end"]:]
    return _preserve_edges(original_decoded, changed, helper, nodes["temp_local"])


def _stage_gate(case: Path, stage_result: dict, expected_sources: dict,
                run_identity: dict, case_identity: dict) -> dict:
    path = case / "verifast-stage.json"
    if not path.is_file():
        return {"admitted": False, "reason": "genuine verifier stage receipt is absent"}
    try:
        receipt = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        return {"admitted": False, "reason": f"invalid verifier receipt: {error}"}
    if type(receipt) is not dict or type(stage_result) is not dict:
        return {"admitted": False, "reason": "verifier receipt or stage result has wrong type"}
    before, after = receipt.get("source_before"), receipt.get("source_after")
    source_ok = (type(before) is dict and before == expected_sources and after == expected_sources and
                 receipt.get("source_unchanged") is True)
    identity_ok = receipt.get("r11_run_identity") == case_identity
    code = receipt.get("exit_code")
    code_ok = (type(code) is int and type(stage_result.get("exit_code")) is int and
               stage_result.get("exit_code") == code)
    status = receipt.get("status")
    status_ok = status is None or (type(status) is str and
                                    status in {"SUCCESS", "SUCCEEDED", "COMPLETED"})
    sha = _file_sha(path)
    claimed_sha = stage_result.get("stage_receipt_sha256")
    sha_ok = claimed_sha == sha
    admitted = (receipt.get("stage") == "verifast" and source_ok and identity_ok and
                code_ok and status_ok and sha_ok and
                receipt.get("r11_run_identity", {}).get("cloud_build_id") ==
                run_identity["cloud_build_id"])
    return {"admitted": admitted, "receipt_sha256": sha,
            "source_identity_matches": source_ok, "run_identity_matches": identity_ok,
            "exit_code_matches": code_ok, "status_matches": status_ok,
            "receipt_sha_matches": sha_ok}


def _current_native_input_gate(case: Path, raw: bytes, decoded: bytes,
                               source_pair: tuple[bytes, bytes], run_identity: dict) -> dict:
    """Require current fullbody exporter/decode receipts and their output bytes.

    The parent callback must stamp the already genuine stage receipts with the
    validated current-run tuple. This reader never retrofits an old receipt.
    """
    expected_sources = {"original/lib.rs": _sha(source_pair[0]),
                        "verified/lib.rs": _sha(source_pair[1]),
                        "small_sort_source": run_identity["source_sha256"]}
    rows = {}
    artifacts = {
        "exporter": ("compiler-mir.bin", raw),
        "decode": ("decode.out", decoded),
    }
    for stage, (expected_output, data) in artifacts.items():
        path = case / f"{stage}-stage.json"
        if not path.is_file():
            return {"admitted": False, "reason": f"current {stage} stage receipt is missing"}
        try:
            receipt = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as error:
            return {"admitted": False, "reason": f"current {stage} receipt is invalid: {error}"}
        if type(receipt) is not dict:
            return {"admitted": False, "reason": f"current {stage} receipt has wrong type"}
        before, after = receipt.get("source_before"), receipt.get("source_after")
        source_ok = (before == expected_sources and after == expected_sources and
                     receipt.get("source_unchanged") is True)
        code_ok = type(receipt.get("exit_code")) is int and receipt.get("exit_code") == 0
        status = receipt.get("status")
        status_ok = status is None or (type(status) is str and
                                       status in {"SUCCESS", "SUCCEEDED", "COMPLETED"})
        identity_ok = receipt.get("r11_run_identity") == run_identity
        output_ok = (receipt.get("output_path") == expected_output and
                     receipt.get("output_sha256") == _sha(data) and
                     type(receipt.get("output_size")) is int and
                     receipt.get("output_size") == len(data))
        input_ok = True
        if stage == "decode":
            input_ok = (receipt.get("input_path") == "compiler-mir.bin" and
                        receipt.get("input_sha256") == _sha(raw))
        ok = (receipt.get("stage") == stage and source_ok and code_ok and
              status_ok and identity_ok and output_ok and input_ok)
        rows[stage] = {"admitted": ok, "receipt_sha256": _file_sha(path),
                       "source_identity_matches": source_ok,
                       "run_identity_matches": identity_ok,
                       "exit_code_matches": code_ok, "status_matches": status_ok,
                       "output_identity_matches": output_ok,
                       "input_identity_matches": input_ok}
        if not ok:
            return {"admitted": False, "stages": rows,
                    "reason": f"current {stage} stage/artifact receipt did not match"}
    return {"admitted": True, "stages": rows,
            "compiler_mir_sha256": _sha(raw), "decode_sha256": _sha(decoded),
            "source_sha256": expected_sources}


def _parse_cut(log: str, target_line: int) -> list[dict]:
    rows = []
    for line in log.splitlines():
        if line.startswith(CUT_PREFIX):
            pairs = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)",
                               line[len(CUT_PREFIX):])
            fields = dict(pairs)
            if len(fields) != len(pairs):
                continue
            if "inv_at" in fields:
                matches_target = bool(re.fullmatch(
                    rf"verified/lib\.rs\({target_line},\d+(?:-\d+(?:,\d+)?)?\)",
                    fields["inv_at"]))
            else:
                at = fields.get("at", "")
                line_field = fields.get("line")
                matches_target = bool(
                    (line_field is not None and line_field.isdigit() and
                     int(line_field) == target_line) or
                    re.search(rf"verified/lib\.rs\({target_line},", at))
            if matches_target:
                rows.append(fields)
    return rows


def _parse_exec(log: str, target_line: int) -> list[dict]:
    rows = []
    for line in log.splitlines():
        if not line.startswith(EXEC_PREFIX):
            continue
        fields = dict(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s]+)", line[len(EXEC_PREFIX):]))
        location = fields.get("at", "")
        if (fields.get("kind") == "label_invariant" and fields.get("phase") == "body" and
                fields.get("gate") == "produced" and
                re.search(rf"verified/lib\.rs\({target_line},", location)):
            rows.append(fields)
    return rows


def _case_identity(run_identity: dict, name: str, mutation: str,
                   source_hashes: dict, target: dict) -> dict:
    identity = {**run_identity, "case": name, "mutation": mutation,
                "case_source_sha256": dict(source_hashes), "target": dict(target)}
    identity["identity_sha256"] = _sha(json.dumps(
        identity, sort_keys=True, separators=(",", ":")).encode())
    return identity


def _run_replay(case: Path, name: str, mutation: str, raw: Path,
                source_pair: tuple[bytes, bytes], args, env: dict, base,
                run_identity: dict, target: dict, expected_source_sha: str) -> dict:
    case.mkdir(parents=True, exist_ok=False)
    source_dir = case / "sources"
    (source_dir / "original").mkdir(parents=True)
    (source_dir / "verified").mkdir()
    (source_dir / "original/lib.rs").write_bytes(source_pair[0])
    (source_dir / "verified/lib.rs").write_bytes(source_pair[1])
    source_hashes = {"original/lib.rs": _sha(source_pair[0]),
                     "verified/lib.rs": _sha(source_pair[1]),
                     "small_sort_source": expected_source_sha}
    identity = _case_identity(run_identity, name, mutation, source_hashes, target)
    bin_dir, child_env = _load("r11_capnp_text_helpers_tools", HERE /
        "first-callback-admission-controls.py")._tool_tree(Path(args.tool_home), case, env)
    real_verifast = Path(args.tool_home) / "bin/verifast"
    local_verifast = bin_dir / "verifast"
    shutil.copy2(real_verifast, local_verifast)
    local_verifast.chmod(local_verifast.stat().st_mode | 0o111)
    if _file_sha(local_verifast) != run_identity["tool_sha256"]["verifast"]:
        raise ValueError("copied verifier differs from current validated binary")
    helper = _load("r11_capnp_text_helpers_wrapper", HERE / "first-callback-admission-controls.py")
    wrapper, wrapper_sha = helper._exporter_wrapper(
        bin_dir, Path(args.tool_home) / "bin/vf-rust-mir-exporter", replay=raw)
    command = [str(local_verifast), "-rustc_args", "--edition 2021",
               "-rust_owned_array_allocation_r8", "-verbose", "1",
               "-dump_ast_with_locs", "proof-ast.ml", "verified/lib.rs"]
    status = base.run_stage(source_dir, "verifast", command, child_env,
                            timeout_seconds=getattr(args, "verifier_seconds", 1200),
                            combine=True)
    receipt_path = source_dir / "verifast-stage.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.is_file() else None
    # Preserve the genuine run_stage receipt fields. Add only the case identity
    # after a genuine non-setup completion. A timeout/could-not-start receipt is
    # retained untouched and cannot be admitted as an executed native control.
    receipt_complete = (type(receipt) is dict and type(status) is int and
                        status not in SETUP_CODES and receipt.get("stage") == "verifast" and
                        receipt.get("exit_code") == status and
                        receipt.get("source_unchanged") is True and
                        type(receipt.get("source_before")) is dict and
                        receipt.get("source_before") == receipt.get("source_after"))
    if receipt_complete:
        receipt["r11_run_identity"] = identity
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    log_path = source_dir / "verifast.log"
    log = log_path.read_text(errors="replace") if log_path.is_file() else ""
    receipt_sha = _file_sha(receipt_path) if receipt_path.is_file() else None
    outcome = {"exit_code": status, "log": log,
               "log_sha256": _file_sha(log_path) if log_path.is_file() else None,
               "stage_receipt_sha256": receipt_sha,
               "verifast_sha256": _file_sha(local_verifast),
               "pinned_verifast_sha256": run_identity["tool_sha256"]["verifast"],
               "exporter_wrapper_sha256": wrapper_sha,
               "exporter_binary_sha256": run_identity["tool_sha256"]["vf-rust-mir-exporter"],
               "refinement_binary_sha256": run_identity["tool_sha256"]["refinement-checker"],
               "replay_export_sha256": _file_sha(raw),
               "r11_run_identity": identity,
               "stage_receipt": receipt}
    expected = {**source_hashes}
    gate = _stage_gate(source_dir, outcome, expected, run_identity, identity)
    outcome["stage_receipt_gate"] = gate
    return outcome


def _classify(name: str, outcome: dict, target_line: int, *, positive: bool,
              stage_gate: dict | None = None) -> dict:
    if type(outcome) is not dict:
        return _inconclusive(name, "verifier outcome is not an object")
    code = outcome.get("exit_code")
    log = outcome.get("log") if type(outcome.get("log")) is str else ""
    cuts = _parse_cut(log, target_line)
    produced = _parse_exec(log, target_line)
    errors = [line for line in log.splitlines() if re.search(r"\berror:", line, re.I)]
    locations = [int(n) for n in re.findall(
        r"verified/lib\.rs\((\d+),\d+(?:-\d+(?:,\d+)?)?\): "
        r"(?:note: )?Executing statement", log)]
    target_seen = target_line in locations or any(f"verified/lib.rs({target_line}," in e for e in errors)
    refusal = (not positive and type(code) is int and code == 1 and
               len(errors) == 1 and DIAGNOSTIC in errors[0] and
               f"verified/lib.rs({target_line}," in errors[0] and
               not cuts and not produced and target_seen and
               stage_gate is not None and stage_gate.get("admitted") is True)
    positive_match = (positive and type(code) is int and code not in SETUP_CODES and
                      len(cuts) == 1 and len(produced) == 1 and target_seen and
                      stage_gate is not None and stage_gate.get("admitted") is True)
    classification = "MATCHED_DIAGNOSTIC_ONLY" if (positive_match or refusal) else "INCONCLUSIVE"
    return {"case": name, "classification": classification,
            "matched": bool(positive_match or refusal), "accepted": False,
            "proof_credit": False, "target_line": target_line,
            "target_seen": target_seen, "exit_code": code,
            "intended_refusal": refusal, "placement_cut_receipts": cuts,
            "body_produced_receipts": produced, "errors": errors,
            "stage_receipt_gate": stage_gate,
            "evidence_class": "R11 placement diagnostic only; no proof credit"}


def run(evidence, args, env, positive_case, source_record, *, validated_run):
    """Run hosted R11 placement mutants against one saved fullbody MIR export."""
    evidence = Path(evidence)
    if evidence.exists():
        return {"schema": CAMPAIGN, "profile": PROFILE, "accepted": False,
                "proof_credit": False, "classification": "INCONCLUSIVE",
                "all_matched": False, "cases": {},
                "error": f"FileExistsError: refusing to reuse R11 placement evidence: {evidence}"}
    result = {"schema": CAMPAIGN, "profile": PROFILE, "accepted": False,
              "proof_credit": False, "classification": "INCONCLUSIVE",
              "all_matched": False, "cases": {}}
    try:
        binding = _profile_binding(args, env)
        run_identity = _run_identity(validated_run, args, env, binding)
        proof = _load("r11_storage_hosted_gate", HERE.parents[1] /
                      "merge/overnight/copy-on-drop-prove.py")
        provider, proof_sha = proof.require_hosted_cloud()
        if not _hosted_identity_matches(provider, proof_sha, run_identity):
            raise ValueError("hosted provider or proof identity differs from validated current run")
        positive_case = Path(positive_case)
        original, verified = _source_pair(positive_case, source_record)
        raw = positive_case / "compiler-mir.bin"
        decoded_path = positive_case / "decode.out"
        if not raw.is_file() or not decoded_path.is_file():
            raise ValueError("saved compiler-mir.bin and decode.out are required")
        raw_bytes = raw.read_bytes()
        decoded_bytes = decoded_path.read_bytes()
        decoded = decoded_bytes.decode("utf-8")
        if not raw_bytes or not decoded_bytes:
            raise ValueError("saved native MIR export is empty")
        input_gate = _current_native_input_gate(positive_case, raw_bytes, decoded_bytes,
                                                (original, verified), run_identity)
        if input_gate.get("admitted") is not True:
            raise ValueError("saved native MIR is not bound to current exporter/decode stages: " +
                             str(input_gate.get("reason")))
        plan = _mutation_plan(decoded, verified)
        result.update(binding)
        result["r11_run_identity"] = run_identity
        result["native_input"] = {"compiler_mir_sha256": _sha(raw_bytes),
                                  "decode_sha256": _sha(decoded.encode()),
                                  "source_pair_sha256": {"original/lib.rs": _sha(original),
                                                         "verified/lib.rs": _sha(verified)},
                                  "target": {"line": plan["source_line"],
                                             "text": plan["source_line_text"],
                                             "destination_local": plan["temp_local"],
                                             "successor_block_index": plan["successor_id"]},
                                  "native_ghost_call_edges": plan["native_edges"]}
        result["current_native_input_gate"] = input_gate
        evidence.mkdir(parents=True)
        (evidence / "manifest.json").write_text(json.dumps(
            {"schema": CAMPAIGN, "profile": PROFILE, "accepted": False,
             "proof_credit": False, "run_identity": run_identity,
             "native_input": result["native_input"],
             "current_native_input_gate": input_gate,
             "mutants": list(MUTANTS)},
            indent=2, sort_keys=True) + "\n")
        helper = _load("r11_capnp_text_helpers_encode", HERE / "first-callback-admission-controls.py")
        include_dirs = list(dict.fromkeys([Path(args.schema).parent,
                                           *getattr(args, "capnp_include", ())]))
        pristine_copy = evidence / "pristine.bin"
        pristine_copy.write_bytes(raw_bytes)
        specs = [("positive_replay", "positive", decoded, pristine_copy)]
        for name in MUTANTS:
            try:
                changed = _mutate_decoded(decoded, name, plan)
                changed_path = evidence / f"{name}.bin"
                helper._encode(changed, Path(args.schema), include_dirs, evidence, env, changed_path)
                specs.append((name, name, changed, changed_path))
            except Exception as error:
                result["cases"][name] = _not_run(name,
                    f"unique source-bound Cap'n Proto mutation setup failed: {type(error).__name__}: {error}")
        expected_source_sha = run_identity["source_sha256"]
        target = {"line": plan["source_line"], "text": plan["source_line_text"],
                  "destination_local": plan["temp_local"]}
        # The host proof helper rechecks provider identity at this point; no
        # local fallback is permitted.
        for case_name, mutation, _mutated_text, replay_path in specs:
            case_dir = evidence / case_name
            try:
                outcome = _run_replay(case_dir, case_name, mutation, replay_path,
                                      (original, verified), args, env, proof,
                                      run_identity, target, expected_source_sha)
                gate = outcome.get("stage_receipt_gate")
                is_positive = case_name == "positive_replay"
                classified = _classify(case_name, outcome, plan["source_line"],
                                       positive=is_positive, stage_gate=gate)
                classified.update({key: value for key, value in outcome.items()
                                   if key not in classified})
                classified["mutated_export_sha256"] = _file_sha(replay_path)
                classified["native_decode_sha256"] = _sha(decoded.encode())
                result["cases"][case_name] = classified
            except Exception as error:
                result["cases"][case_name] = _inconclusive(
                    case_name, f"hosted verifier replay failed: {type(error).__name__}: {error}")
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
        result["cases"] = {name: _not_run(name, "R11 placement setup failed") for name in MUTANTS}
    required_cases = {"positive_replay", *MUTANTS[:-1]}
    result["all_matched"] = (required_cases.issubset(result["cases"]) and
                              all(result["cases"][name].get("matched") is True
                                  for name in required_cases))
    result["optional_extra_address_taken_control_matched"] = (
        result["cases"].get("extra_address_taken_use", {}).get("matched") is True)
    result["classification"] = "DIAGNOSTIC_CONTROLS_MATCHED" if result["all_matched"] else "INCONCLUSIVE"
    result["accepted"] = False
    result["proof_credit"] = False
    try:
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "aggregate.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    except OSError:
        pass
    return result
