#!/usr/bin/env python3
"""Isolated, diagnostic-only normal MIR exporter wrapper.

The production exporter is copied beside this file as
vf-rust-mir-exporter.official. Every invocation publishes its raw output and
its one deliberately encoded Capnp message. Nothing here is a proof summary.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys


SCHEMA_SHA = "f48fcf29b99717c2e0cb37d4708b47eccaa3270b999e4a84093e37fbd51b7469"
PARSER_SHA = "9ecce61ca3886f2b9e21bb03d35ce6312da5eb405ff35a0bb37211eb2c49e974"
REFUSAL = "MIR-OR-JOIN-LIVENESS: exact source/MIR/AST join admission failed"
MODES = {
    "roundtrip",
    "storage-live-34", "storage-live-36",
    "goto-38-34", "goto-38-36",
    "statement-count-34", "statement-count-36",
    "real-statement-34", "predecessor-32",
    "comparison-eq-33", "comparison-eq-35",
    "branch-order-33", "branch-order-35",
    "span-column-34", "span-column-36",
    "panic-callee", "panic-unwind",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def path(value: object, *keys: str):
    for key in keys:
        need(isinstance(value, dict) and key in value,
             f"normal MIR field is missing: {key}")
        value = value[key]
    return value


def run(argv: list[str], stdin: bytes | None, seconds: int) -> subprocess.CompletedProcess:
    return subprocess.run(argv, input=stdin, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, timeout=seconds, check=False)


def balanced_end(text: str, opening: int) -> int:
    need(text[opening] == "(", "record opening is absent")
    depth = 0
    quoted = False
    escaped = False
    for at in range(opening, len(text)):
        ch = text[at]
        if quoted:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return at + 1
    raise ValueError("unbalanced decoded Capnp record")


def target_block_text(decoded: str, block_id: int) -> tuple[int, int, str]:
    paths = list(re.finditer(r'\bdefPath\s*=\s*"bidirectional_merge"', decoded))
    need(len(paths) == 1, "decoded target body count is not one")
    body_start = decoded.rfind("( defKind =", 0, paths[0].start())
    need(body_start >= 0, "target body record opening absent")
    body_end = balanced_end(decoded, body_start)
    need(paths[0].end() < body_end, "target path escaped its body")
    segment = decoded[body_start:body_end]
    starts = list(re.finditer(r'\(\s*id\s*=\s*\(index\s*=\s*' +
                              str(block_id) + r'\)\s*,', segment))
    need(len(starts) == 1, f"target basic block {block_id} is not unique")
    opening = body_start + starts[0].start()
    end = balanced_end(decoded, opening)
    return opening, end, decoded[opening:end]


def need_keys(value: object, keys: set[str], label: str) -> dict:
    need(isinstance(value, dict) and set(value) == keys,
         f"{label} has missing or unexpected fields")
    return value


def target_tree(parsed: dict, guard: int) -> tuple[dict, dict[int, dict]]:
    need(isinstance(parsed, dict) and isinstance(parsed.get("bodies"), list),
         "normal message has no body list")
    bodies = [body for body in parsed["bodies"]
              if isinstance(body, dict) and body.get("defPath") == "bidirectional_merge"]
    need(len(bodies) == 1, "normal message target body count is not one")
    blocks = bodies[0].get("basicBlocks")
    need(isinstance(blocks, list), "target has no basic blocks")
    found = {block.get("id", {}).get("index"): block for block in blocks
             if isinstance(block, dict) and isinstance(block.get("id"), dict)}
    for number in (32, 33, 34, 35, 36, 37, 38):
        need(sum(block.get("id", {}).get("index") == number for block in blocks) == 1,
             f"target basic block {number} is not unique")
    need_keys(path(found[32], "terminator", "kind"), {"goto"},
              "block 32 terminator kind")
    need(path(found[32], "terminator", "kind", "goto", "index") == 33,
         "target block 32 is not the expected odd-tail predecessor Goto33")
    for number in (34, 36):
        stmts = found[number].get("statements")
        need(isinstance(stmts, list) and len(stmts) == 2 and
             all(isinstance(stmt, dict) and
                 set(stmt.get("kind", {})) == {"storageDead"} for stmt in stmts),
             f"target block {number} is not a two-StorageDead edge")
        for stmt in stmts:
            storage = need_keys(path(stmt, "kind"), {"storageDead"},
                                f"block {number} statement kind")["storageDead"]
            need_keys(storage, {"name"}, f"block {number} StorageDead")
        need(found[number].get("terminator", {}).get("kind", {}).get("goto", {}).get("index") == 37,
             f"target block {number} does not enter 37")
        term = path(found[number], "terminator")
        need_keys(path(term, "kind"), {"goto"}, f"block {number} terminator kind")
        span = path(term, "sourceInfo", "span", "regular")
        need(path(span, "lo", "file", "name", "real", "localPath") == "verified/lib.rs" and
             path(span, "hi", "file", "name", "real", "localPath") == "verified/lib.rs" and
             path(span, "lo", "line") == guard and
             path(span, "lo", "col", "pos") == 50 and
             path(span, "hi", "line") == guard + 2 and
             path(span, "hi", "col", "pos") == 9,
             f"block {number} Goto source span differs from the frozen normal form")
    first = found[34]["statements"][0]
    need(re.fullmatch(r"_[0-9]+", first["kind"]["storageDead"].get("name", "")) is not None,
         "storage local in block 34 is malformed")
    span = first.get("sourceInfo", {}).get("span", {}).get("regular", {})
    need(span.get("lo", {}).get("line") == guard,
         "block 34 is not at the admitted guard")
    for number, expected_targets in ((33, [35, 34]), (35, [38, 36])):
        stmts = found[number].get("statements")
        need(isinstance(stmts, list) and bool(stmts),
             f"block {number} has no comparison statements")
        last = need_keys(stmts[-1], {"sourceInfo", "kind"},
                         f"block {number} final statement")
        assign = need_keys(path(last, "kind"), {"assign"},
                           f"block {number} final statement kind")["assign"]
        assign = need_keys(assign, {"lhsPlace", "rhsRvalue"},
                           f"block {number} comparison assignment")
        lhs = need_keys(assign["lhsPlace"],
                        {"local", "projection", "localIsMutable", "kind"},
                        f"block {number} comparison destination")
        need(lhs["projection"] == [] and lhs["kind"] == {"other": None},
             f"block {number} comparison destination is projected/typed unexpectedly")
        result_local = path(lhs, "local", "name")
        need(re.fullmatch(r"_[0-9]+", result_local or "") is not None,
             f"block {number} comparison result local is malformed")
        result_decls = [decl for decl in path(bodies[0], "localDecls")
                        if path(decl, "id", "name") == result_local]
        need(len(result_decls) == 1 and
             path(result_decls[0], "ty", "kind") == {"bool": None},
             f"block {number} comparison result is not its unique bool local")
        rhs = need_keys(assign["rhsRvalue"], {"binaryOp"},
                        f"block {number} comparison rvalue")["binaryOp"]
        rhs = need_keys(rhs, {"operator", "operandl", "operandr"},
                        f"block {number} binary comparison")
        need(rhs["operator"] == {"ne": None},
             f"block {number} comparison is not the expected ne")
        switch = need_keys(path(found[number], "terminator", "kind"), {"switchInt"},
                           f"block {number} terminator kind")["switchInt"]
        switch = need_keys(switch, {"discr", "discrTy", "values", "targets"},
                           f"block {number} switchInt")
        need(path(switch, "discr", "move", "local", "name") == result_local and
             switch["discrTy"] == {"kind": {"bool": None}} and
             switch["values"] == [{"h": 0, "l": 0}] and
             [path(target, "index") for target in switch["targets"]] == expected_targets,
             f"block {number} switch type/value/branch pair differs from the frozen form")
    block37 = found[37]
    call = need_keys(path(block37, "terminator", "kind"), {"call"},
                     "block 37 terminator kind")["call"]
    call = need_keys(call, {"func", "args", "destination", "callSpan", "unwindAction"},
                     "block 37 panic call")
    need(path(call, "func", "constant", "const", "val", "ty", "kind", "fnDef", "id", "name") ==
         "panic_on_ord_violation" and call["args"] == [] and
         call["unwindAction"] == {"continue": None},
         "block 37 panic callee, arguments, or unwind action differs from the frozen form")
    need(block37.get("isCleanup") is False and
         len(path(block37, "statements")) == 1 and
         set(path(block37, "statements")[0].get("kind", {})) == {"storageLive"},
         "block 37 cleanup flag or setup statements differ from the frozen form")
    panic_span = path(call, "callSpan", "regular")
    need(path(panic_span, "lo", "file", "name", "real", "localPath") == "verified/lib.rs" and
         path(panic_span, "hi", "file", "name", "real", "localPath") == "verified/lib.rs" and
         path(panic_span, "lo", "line") == guard + 1 and
         path(panic_span, "hi", "line") == guard + 1,
         "block 37 panic source span differs from the admitted source call")
    return bodies[0], found


def direct_list_records(text: str, field: str) -> tuple[int, int, list[tuple[int, int]]]:
    markers = list(re.finditer(r"\b" + re.escape(field) + r"\s*=\s*\[", text))
    need(len(markers) == 1, f"record list {field} is absent or ambiguous")
    opening = text.index("[", markers[0].start(), markers[0].end())
    records = []
    at = opening + 1
    while at < len(text):
        while at < len(text) and (text[at].isspace() or text[at] == ","):
            at += 1
        if at < len(text) and text[at] == "]":
            return opening, at, records
        need(at < len(text) and text[at] == "(",
             f"{field} contains an unsupported non-record list item")
        end = balanced_end(text, at)
        records.append((at, end))
        at = end
    raise ValueError(f"unterminated {field} list")


def main() -> int:
    mode = os.environ.get("OR_JOIN_CONTROL_MODE", "")
    role = os.environ.get("OR_JOIN_CONTROL_ROLE", "")
    need(mode in MODES and role in {"manual", "frontend"},
         "missing diagnostic mode/role")
    evidence = Path(os.environ["OR_JOIN_CONTROL_EVIDENCE"])
    directory = evidence / mode / role
    directory.mkdir(parents=True, exist_ok=False)
    record = {"mode": mode, "role": role, "accepted": False,
              "classification": "INCONCLUSIVE", "argv": sys.argv[1:]}
    try:
        official = Path(__file__).with_name("vf-rust-mir-exporter.official")
        schema = Path(os.environ["OR_JOIN_CONTROL_SCHEMA"])
        parser_file = Path(os.environ["OR_JOIN_CONTROL_PARSER"])
        source = Path("verified/lib.rs")
        expected_source = os.environ["OR_JOIN_CONTROL_SOURCE_SHA"]
        expected_mir = os.environ["OR_JOIN_CONTROL_NORMAL_MIR_SHA"]
        expected_exporter = os.environ["OR_JOIN_CONTROL_OFFICIAL_SHA"]
        sysroot = os.environ["OR_JOIN_CONTROL_SYSROOT"]
        guard = int(os.environ["OR_JOIN_CONTROL_GUARD_LINE"])
        need(sys.argv[1:] == ["verified/lib.rs", "--sysroot=" + sysroot,
                              "--edition", "2021"],
             "exporter invocation is not the exact normal-preprocess command")
        need(file_sha(source) == expected_source and
             file_sha(schema) == SCHEMA_SHA and
             file_sha(parser_file) == PARSER_SHA and
             file_sha(official) == expected_exporter,
             "source/schema/parser/official exporter hash mismatch")
        lines = source.read_text().splitlines()
        need(lines[guard - 1] == "        if left != left_end || right != right_end {" and
             lines[guard] == "            panic_on_ord_violation();",
             "admitted source guard/panic changed")
        record.update({"source_sha256": file_sha(source),
                       "schema_sha256": file_sha(schema),
                       "parser_sha256": file_sha(parser_file),
                       "official_exporter_sha256": file_sha(official)})
        exported = run([str(official), *sys.argv[1:]], None, 45)
        (directory / "official.stdout.bin").write_bytes(exported.stdout)
        (directory / "official.stderr").write_bytes(exported.stderr)
        record.update({"official_exit": exported.returncode,
                       "official_stdout_sha256": sha(exported.stdout),
                       "official_stderr_sha256": sha(exported.stderr)})
        sys.stderr.buffer.write(exported.stderr)
        if exported.returncode:
            sys.stdout.buffer.write(exported.stdout)
            return exported.returncode
        need(sha(exported.stdout) == expected_mir,
             "normal message is not the exact production message")
        inc = ["-I", str(schema.parent)]
        decoded = run(["capnp", "decode", *inc, str(schema), "VfMir"],
                      exported.stdout, 15)
        (directory / "normal-decode.txt").write_bytes(decoded.stdout)
        (directory / "normal-decode.stderr").write_bytes(decoded.stderr)
        need(decoded.returncode == 0, "normal Capnp decode failed")
        spec = importlib.util.spec_from_file_location("or_join_capnp_text", parser_file)
        need(spec is not None and spec.loader is not None, "Capnp parser loader failed")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        original = module.CapnpText(decoded.stdout.decode("utf-8")).parse()
        _, original_blocks = target_tree(original, guard)
        expected = copy.deepcopy(original)
        _, expected_blocks = target_tree(expected, guard)
        output_text = decoded.stdout.decode("utf-8")
        changed = output_text
        change = "none"
        if mode.startswith("storage-live-"):
            block_id = int(mode.rsplit("-", 1)[1])
            block_text = target_block_text(output_text, block_id)
            storage = original_blocks[block_id]["statements"][0]["kind"]["storageDead"]
            local = storage["name"]
            old = re.compile(r'\bstorageDead\s*=\s*\(name\s*=\s*"' +
                             re.escape(local) + r'"\s*\)')
            mutated, count = old.subn(f'storageLive = (name = "{local}")',
                                      block_text[2], count=1)
            need(count == 1, f"block {block_id} StorageDead mutation did not match")
            expected_blocks[block_id]["statements"][0]["kind"]["storageLive"] = \
                expected_blocks[block_id]["statements"][0]["kind"].pop("storageDead")
            change = f"body.bidirectional_merge.block{block_id}.statements[0].kind.storageDead->storageLive({local})"
            changed = output_text[:block_text[0]] + mutated + output_text[block_text[1]:]
        elif mode.startswith("goto-38-"):
            block_id = int(mode.rsplit("-", 1)[1])
            block_text = target_block_text(output_text, block_id)
            mutated, count = re.subn(r'\bgoto\s*=\s*\(index\s*=\s*37\)',
                                     'goto = (index = 38)', block_text[2], count=1)
            need(count == 1, f"block {block_id} Goto37 mutation did not match")
            expected_blocks[block_id]["terminator"]["kind"]["goto"]["index"] = 38
            change = f"body.bidirectional_merge.block{block_id}.terminator.goto.index:37->38"
            changed = output_text[:block_text[0]] + mutated + output_text[block_text[1]:]
        elif mode.startswith("statement-count-"):
            block_id = int(mode.rsplit("-", 1)[1])
            block_text = target_block_text(output_text, block_id)
            _, _, records = direct_list_records(block_text[2], "statements")
            need(len(records) == 2, f"block {block_id} statement-count source changed")
            first_end, second_start = records[0][1], records[1][0]
            separators = list(re.finditer(r",", block_text[2][first_end:second_start]))
            need(len(separators) == 1,
                 f"block {block_id} statements do not have one separator")
            comma = first_end + separators[0].start()
            second_end = records[1][1]
            mutated = block_text[2][:comma] + block_text[2][second_end:]
            expected_blocks[block_id]["statements"].pop(1)
            change = f"body.bidirectional_merge.block{block_id}.statements.remove(index=1)"
            changed = output_text[:block_text[0]] + mutated + output_text[block_text[1]:]
        elif mode == "real-statement-34":
            source_block = target_block_text(output_text, 33)
            target_block = target_block_text(output_text, 34)
            _, _, source_records = direct_list_records(source_block[2], "statements")
            _, target_close, target_records = direct_list_records(target_block[2], "statements")
            need(source_records and len(target_records) == 2,
                 "real-statement source/target statement count changed")
            statement = source_block[2][source_records[-1][0]:source_records[-1][1]]
            mutated_target = (target_block[2][:target_records[-1][1]] + ",\n" +
                              statement + target_block[2][target_records[-1][1]:])
            # The expected tree changes only by appending the existing typed
            # comparison record from block 33; all operands and local types
            # remain those of the official normal MIR.
            expected_blocks[34]["statements"].append(
                copy.deepcopy(original_blocks[33]["statements"][-1]))
            change = "body.bidirectional_merge.block34.statements.append(block33.final_typed_ne_assignment)"
            changed = (output_text[:target_block[0]] + mutated_target +
                       output_text[target_block[1]:])
        elif mode == "predecessor-32":
            block_text = target_block_text(output_text, 32)
            mutated, count = re.subn(r'\bgoto\s*=\s*\(index\s*=\s*33\)',
                                     'goto = (index = 37)', block_text[2], count=1)
            need(count == 1, "block 32 Goto33 mutation did not match")
            expected_blocks[32]["terminator"]["kind"]["goto"]["index"] = 37
            change = "body.bidirectional_merge.block32.terminator.goto.index:33->37"
            changed = output_text[:block_text[0]] + mutated + output_text[block_text[1]:]
        elif mode.startswith("comparison-eq-"):
            block_id = int(mode.rsplit("-", 1)[1])
            block_text = target_block_text(output_text, block_id)
            mutated, count = re.subn(r'\boperator\s*=\s*\(ne\s*=\s*void\)',
                                     'operator = (eq = void)', block_text[2], count=1)
            need(count == 1, f"block {block_id} ne operator mutation did not match")
            rhs = expected_blocks[block_id]["statements"][-1]["kind"]["assign"]["rhsRvalue"]["binaryOp"]
            rhs["operator"] = {"eq": None}
            change = f"body.bidirectional_merge.block{block_id}.comparison.operator:ne->eq"
            changed = output_text[:block_text[0]] + mutated + output_text[block_text[1]:]
        elif mode.startswith("branch-order-"):
            block_id = int(mode.rsplit("-", 1)[1])
            block_text = target_block_text(output_text, block_id)
            targets_start, targets_end, target_records = direct_list_records(
                block_text[2], "targets")
            need(len(target_records) == 2,
                 f"block {block_id} target pair is not exactly two entries")
            first = block_text[2][target_records[0][0]:target_records[0][1]]
            second = block_text[2][target_records[1][0]:target_records[1][1]]
            mutated = (block_text[2][:target_records[0][0]] + second + ", " + first +
                       block_text[2][target_records[1][1]:])
            expected_blocks[block_id]["terminator"]["kind"]["switchInt"]["targets"].reverse()
            change = f"body.bidirectional_merge.block{block_id}.switchInt.targets:swap"
            changed = output_text[:block_text[0]] + mutated + output_text[block_text[1]:]
        elif mode.startswith("span-column-"):
            block_id = int(mode.rsplit("-", 1)[1])
            block_text = target_block_text(output_text, block_id)
            term_start = block_text[2].find("terminator = (")
            need(term_start >= 0, f"block {block_id} terminator text absent")
            term_text = block_text[2][term_start:]
            low_col = re.compile(r'(\blo\s*=\s*\(.*?\bcol\s*=\s*\(pos\s*=\s*)50(\s*\)\s*\))', re.S)
            mutated_term, count = low_col.subn(r'\g<1>49\2', term_text, count=1)
            need(count == 1, f"block {block_id} low-column span mutation did not match")
            term_span = path(expected_blocks[block_id], "terminator", "sourceInfo", "span", "regular", "lo", "col")
            term_span["pos"] = 49
            mutated = block_text[2][:term_start] + mutated_term
            change = f"body.bidirectional_merge.block{block_id}.terminator.span.lo.col.pos:50->49"
            changed = output_text[:block_text[0]] + mutated + output_text[block_text[1]:]
        elif mode == "panic-callee":
            block_text = target_block_text(output_text, 37)
            mutated, count = re.subn(r'name\s*=\s*"panic_on_ord_violation"',
                                     'name = "std::process::abort"',
                                     block_text[2], count=1)
            need(count == 1, "block 37 panic callee mutation did not match")
            expected_blocks[37]["terminator"]["kind"]["call"]["func"]["constant"]["const"]["val"]["ty"]["kind"]["fnDef"]["id"]["name"] = "std::process::abort"
            change = "body.bidirectional_merge.block37.call.func.fnDef.id.name:panic_on_ord_violation->std::process::abort"
            changed = output_text[:block_text[0]] + mutated + output_text[block_text[1]:]
        elif mode == "panic-unwind":
            block_text = target_block_text(output_text, 37)
            mutated, count = re.subn(r'unwindAction\s*=\s*\(continue\s*=\s*void\)',
                                     'unwindAction = (unreachable = void)',
                                     block_text[2], count=1)
            need(count == 1, "block 37 unwind-action mutation did not match")
            expected_blocks[37]["terminator"]["kind"]["call"]["unwindAction"] = {"unreachable": None}
            change = "body.bidirectional_merge.block37.call.unwindAction:continue->unreachable"
            changed = output_text[:block_text[0]] + mutated + output_text[block_text[1]:]
        (directory / "encoded-input.txt").write_text(changed)
        check_tree = module.CapnpText(changed).parse()
        need(check_tree == expected, "decoded text changed beyond the declared field")
        encoded = run(["capnp", "encode", *inc, str(schema), "VfMir"],
                      changed.encode("utf-8"), 15)
        (directory / "encode.stderr").write_bytes(encoded.stderr)
        (directory / "encoded-message.bin").write_bytes(encoded.stdout)
        need(encoded.returncode == 0, "Capnp encode failed")
        checked = run(["capnp", "decode", *inc, str(schema), "VfMir"],
                      encoded.stdout, 15)
        (directory / "redecode.txt").write_bytes(checked.stdout)
        (directory / "redecode.stderr").write_bytes(checked.stderr)
        need(checked.returncode == 0 and
             module.CapnpText(checked.stdout.decode("utf-8")).parse() == expected,
             "encoded Capnp message did not preserve exactly the declared tree")
        if mode == "roundtrip":
            need(checked.stdout == decoded.stdout,
                 "positive normal Capnp decode text changed on roundtrip")
        record.update({"classification": "MESSAGE_CERTIFIED", "change": change,
                       "normal_decoded_sha256": sha(decoded.stdout),
                       "encoded_input_sha256": sha(changed.encode()),
                       "encoded_message_sha256": sha(encoded.stdout),
                       "redecoded_sha256": sha(checked.stdout),
                       "positive_decoded_text_byte_equal":
                           checked.stdout == decoded.stdout if mode == "roundtrip" else None,
                       "exact_semantic_tree_match": True,
                       "normal_mode_only": True})
        sys.stdout.buffer.write(encoded.stdout)
        return 0
    except (OSError, KeyError, ValueError, RuntimeError,
            UnicodeError, subprocess.TimeoutExpired) as exc:
        record["refusal"] = str(exc)
        print(f"MIR-OR-JOIN diagnostic wrapper refusal: {exc}", file=sys.stderr)
        return 2
    finally:
        (directory / "certificate.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, KeyError, ValueError) as exc:
        print(f"MIR-OR-JOIN diagnostic wrapper setup refusal: {exc}",
              file=sys.stderr)
        raise SystemExit(2)
