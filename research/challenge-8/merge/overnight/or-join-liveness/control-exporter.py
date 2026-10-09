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
MODES = {"roundtrip", "storage-live-34", "goto-38-34"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha(path: Path) -> str:
    return sha(path.read_bytes())


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


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


def target_block_text(decoded: str, block_id: int) -> tuple[int, int]:
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
    return opening, balanced_end(decoded, opening)


def target_tree(parsed: dict, guard: int) -> tuple[dict, dict]:
    need(isinstance(parsed, dict) and isinstance(parsed.get("bodies"), list),
         "normal message has no body list")
    bodies = [body for body in parsed["bodies"]
              if isinstance(body, dict) and body.get("defPath") == "bidirectional_merge"]
    need(len(bodies) == 1, "normal message target body count is not one")
    blocks = bodies[0].get("basicBlocks")
    need(isinstance(blocks, list), "target has no basic blocks")
    found = {block.get("id", {}).get("index"): block for block in blocks
             if isinstance(block, dict) and isinstance(block.get("id"), dict)}
    for number in (33, 34, 35, 36, 37, 38):
        need(sum(block.get("id", {}).get("index") == number for block in blocks) == 1,
             f"target basic block {number} is not unique")
    for number in (34, 36):
        stmts = found[number].get("statements")
        need(isinstance(stmts, list) and len(stmts) == 2 and
             all(isinstance(stmt, dict) and
                 set(stmt.get("kind", {})) == {"storageDead"} for stmt in stmts),
             f"target block {number} is not a two-StorageDead edge")
        need(found[number].get("terminator", {}).get("kind", {}).get("goto", {}).get("index") == 37,
             f"target block {number} does not enter 37")
    first = found[34]["statements"][0]
    need(re.fullmatch(r"_[0-9]+", first["kind"]["storageDead"].get("name", "")) is not None,
         "storage local in block 34 is malformed")
    span = first.get("sourceInfo", {}).get("span", {}).get("regular", {})
    need(span.get("lo", {}).get("line") == guard,
         "block 34 is not at the admitted guard")
    return bodies[0], found[34]


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
        _, block = target_tree(original, guard)
        expected = copy.deepcopy(original)
        _, expected_block = target_tree(expected, guard)
        output_text = decoded.stdout.decode("utf-8")
        start, end = target_block_text(output_text, 34)
        block_text = output_text[start:end]
        change = "none"
        if mode == "storage-live-34":
            local = block["statements"][0]["kind"]["storageDead"]["name"]
            old = re.compile(r'\bstorageDead\s*=\s*\(name\s*=\s*"' +
                             re.escape(local) + r'"\s*\)')
            block_text, count = old.subn(f'storageLive = (name = "{local}")',
                                         block_text, count=1)
            need(count == 1, "block 34 StorageDead mutation did not match")
            value = expected_block["statements"][0]["kind"].pop("storageDead")
            expected_block["statements"][0]["kind"]["storageLive"] = value
            change = f"body.bidirectional_merge.block34.statements[0].kind.storageDead->storageLive({local})"
        elif mode == "goto-38-34":
            block_text, count = re.subn(r'\bgoto\s*=\s*\(index\s*=\s*37\)',
                                        'goto = (index = 38)', block_text,
                                        count=1)
            need(count == 1, "block 34 Goto37 mutation did not match")
            expected_block["terminator"]["kind"]["goto"]["index"] = 38
            change = "body.bidirectional_merge.block34.terminator.goto.index:37->38"
        changed = output_text[:start] + block_text + output_text[end:]
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
