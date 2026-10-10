#!/usr/bin/env python3
"""Saved-data MIR/AST admission for the concrete one-cell guard controls.

This checks source and translation identity only. It grants no allocation,
permission, separation, or proof credit on its own.
"""
from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
OLD = HERE.parents[1] / "merge/overnight"
GUARD_SOURCE = (b"struct CopyOnDrop {\n    src: *const u64,\n"
                b"    dst: *mut u64,\n    len: usize,\n}")
TMP_SOURCE = b"        let tmp = ManuallyDrop::new(tail.read());\n"
GUARD_INIT = b"        let mut gap_guard = CopyOnDrop { src: &*tmp, dst: tail, len: 1 };\n"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"missing strict parser: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _need(ok: bool, why: str):
    if not ok:
        raise ValueError(why)


def _one(items, why: str):
    _need(len(items) == 1, f"expected one {why}, found {len(items)}")
    return items[0]


def _source_line(source: bytes, anchor: bytes) -> int:
    _need(source.count(anchor) == 1, f"source anchor is not unique: {anchor!r}")
    return source[:source.index(anchor)].count(b"\n") + 1


def _span(mir, span, source: bytes, allow_empty=False) -> tuple[int, int, bytes]:
    regular = mir.path(span, "regular")
    lo, hi = mir.path(regular, "lo"), mir.path(regular, "hi")
    for endpoint in (lo, hi):
        _need(mir.path(endpoint, "file", "name", "real", "localPath") ==
              "verified/lib.rs", "MIR span is not in checked source")
    lines = source.splitlines(keepends=True)
    first, last = mir.path(lo, "line"), mir.path(hi, "line")
    _need(isinstance(first, int) and isinstance(last, int) and
          1 <= first <= last <= len(lines), "MIR source lines are invalid")
    start, end = mir.path(lo, "col", "pos"), mir.path(hi, "col", "pos")
    _need(isinstance(start, int) and isinstance(end, int) and
          0 <= start <= len(lines[first - 1]) and 0 <= end <= len(lines[last - 1]),
          "MIR source columns are invalid")
    first_byte = sum(map(len, lines[:first - 1])) + start
    last_byte = sum(map(len, lines[:last - 1])) + end
    _need(first_byte <= last_byte if allow_empty else first_byte < last_byte,
          "empty or reversed MIR source span")
    return first, last, source[first_byte:last_byte]


def _uint(value, positive=False) -> int:
    _need(isinstance(value, str) and re.fullmatch(r"0|[1-9][0-9]*", value)
          is not None, "noncanonical compiler layout integer")
    number = int(value)
    _need(number <= (1 << 64) - 1 and (not positive or number > 0),
          "compiler layout integer outside positive u64 range")
    return number


def _ty(mir, field, kind: str, mutability: str | None = None) -> bool:
    try:
        ty_kind = mir.path(field, "ty", "kind")
        if kind == "usize":
            return ty_kind == {"uInt": {"uSize": None}}
        raw = mir.path(ty_kind, "rawPtr")
        return (mir.path(raw, "mutability") == {mutability: None} and
                mir.path(raw, "ty", "kind") == {"uInt": {"u64": None}})
    except Exception:
        return False


def _ast_type(ast, value, pointer: bool) -> bool:
    if pointer:
        if not isinstance(value, ast.Node) or value.name != "PtrTypeExpr" or len(value.args) != 2:
            return False
        value = value.args[1]
    if not isinstance(value, ast.Node) or value.name != "ManifestTypeExpr" or len(value.args) != 2:
        return False
    integer = value.args[1]
    if not isinstance(integer, ast.Node) or integer.name != "Int" or len(integer.args) != 2:
        return False
    return (integer.args[0] == ast.Sym("Unsigned") and
            integer.args[1] == (ast.Node("FixedWidthRank", [3]) if pointer
                                else ast.Sym("PtrRank")))


def _normal_successors(mir, block) -> list[int]:
    kind = mir.path(block, "terminator", "kind")
    _need(isinstance(kind, dict) and len(kind) == 1,
          "invalid MIR terminator while checking live-local path")
    tag, data = next(iter(kind.items()))
    if tag == "goto":
        targets = [data]
    elif tag == "switchInt":
        targets = mir.path(data, "targets")
    elif tag == "call":
        target = mir.path(data, "target")
        targets = [mir.path(target, "something")] if "something" in target else []
    elif tag in ("drop", "assert"):
        targets = [mir.path(data, "target")]
    elif tag in ("return", "unreachable", "unwindResume", "unwindTerminate"):
        targets = []
    else:
        raise ValueError(f"unsupported MIR normal edge while checking live locals: {tag}")
    return [mir.path(target, "index") for target in targets]


def _concurrent_live_path(mir, blocks, tmp_event, guard_event, tmp_id) -> bool:
    by_id = {mir.path(block, "id", "index"): block for block in blocks}
    _need(len(by_id) == len(blocks), "duplicate MIR block identity")
    todo = [(tmp_event[0], tmp_event[1] + 1)]
    visited = set()
    while todo:
        block_id, start = todo.pop()
        if (block_id, start) in visited:
            continue
        visited.add((block_id, start))
        block = by_id.get(block_id)
        _need(block is not None, "MIR normal edge points to absent block")
        statements = mir.path(block, "statements")
        for index in range(start, len(statements)):
            if (block_id, index) == guard_event[:2]:
                return True
            if mir.path(statements[index], "kind") == {"storageDead": {"name": tmp_id}}:
                break
        else:
            todo.extend((next_id, 0) for next_id in _normal_successors(mir, block))
    return False


def admit(case: Path) -> dict:
    """Fail closed unless compiler layout and two live locals match source and AST."""
    try:
        original = (case / "original/lib.rs").read_bytes()
        source = (case / "verified/lib.rs").read_bytes()
        decoded = (case / "decode.out").read_bytes()
        ast_bytes = (case / "proof-ast.ml").read_bytes()
        for data in (original, source):
            _source_line(data, GUARD_SOURCE)
            _source_line(data, TMP_SOURCE)
            _source_line(data, GUARD_INIT)
        guard_line = _source_line(source, GUARD_SOURCE)
        tmp_line = _source_line(source, TMP_SOURCE)
        init_line = _source_line(source, GUARD_INIT)
        _need(guard_line < tmp_line < init_line, "source guard/locals are out of order")
        mir = _load("guard_layout_strict_mir", OLD / "stack-address-admission.py")
        ast = _load("guard_layout_strict_ast", OLD / "stack-proof-ast-admission.py")
        tree = mir.CapnpText(decoded.decode("utf-8").replace(
            "variances = [invariant]", 'variances = ["invariant"]')).parse()
        ast_tree = ast.OcamlAstText(ast_bytes.decode("utf-8")).parse()
        _need(mir.path(tree, "targetTriple") == "x86_64-unknown-linux-gnu" and
              mir.path(tree, "pointerWidth") == 64,
              "MIR compiler target/pointer width differs")
        adts, cursor = [], mir.path(tree, "adtDefs")
        while isinstance(cursor, dict) and "cons" in cursor:
            adts.append(mir.path(cursor, "cons", "h"))
            cursor = mir.path(cursor, "cons", "t")
        guard = _one([item for item in adts if mir.path(item, "hasConcreteGuardLayout") is True],
                     "compiler-qualified guard ADT")
        path = mir.path(guard, "id", "name")
        _need(isinstance(path, str) and re.search(r"(?:^|::)CopyOnDrop$", path) is not None and
              mir.path(guard, "concreteGuardDefPath") == path and
              mir.path(guard, "isLocal") is True and
              mir.path(guard, "kind") == {"structKind": None} and
              mir.path(guard, "isReprC") is False and
              mir.path(guard, "implementsDrop") is False,
              "qualified guard identity/shape differs")
        path_hash = mir.path(guard, "concreteGuardDefPathHash")
        _need(isinstance(path_hash, str) and bool(path_hash.strip()),
              "compiler DefPathHash is absent")
        def_first, _, snippet = _span(mir, mir.path(guard, "defSpan"), source)
        _need(def_first == guard_line and snippet in (GUARD_SOURCE, GUARD_SOURCE + b"\n"),
              "qualified ADT def-span does not match exact source declaration")
        variants = mir.path(guard, "variants")
        _need(isinstance(variants, list) and len(variants) == 1,
              "qualified guard has non-struct variants")
        fields = mir.path(variants[0], "fields")
        names = [mir.path(field, "name", "name") for field in fields]
        _need(names == ["src", "dst", "len"] and
              _ty(mir, fields[0], "u64", "not") and
              _ty(mir, fields[1], "u64", "mut") and
              _ty(mir, fields[2], "usize"),
              "qualified MIR guard fields or mutability differ")
        size = mir.path(guard, "concreteGuardSizeBytes")
        align = mir.path(guard, "concreteGuardAlignBytes")
        _need(isinstance(size, int) and isinstance(align, int) and
              0 < size <= (1 << 64) - 1 and 0 < align <= (1 << 64) - 1,
              "compiler guard size/alignment is invalid")
        offsets = mir.path(guard, "concreteGuardFieldOffsets")
        sizes = mir.path(guard, "concreteGuardFieldSizes")
        _need(isinstance(offsets, list) and isinstance(sizes, list) and
              len(offsets) == len(sizes) == 3, "compiler field layout arity differs")
        intervals = [( _uint(off), _uint(width, positive=True))
                     for off, width in zip(offsets, sizes)]
        _need(all(off + width <= size for off, width in intervals) and
              all(a + aw <= b or b + bw <= a
                  for i, (a, aw) in enumerate(intervals)
                  for b, bw in intervals[i + 1:]),
              "compiler guard field intervals overlap or exceed extent")
        structs = [node for node in ast.nodes(ast_tree, "Struct")
                   if len(node.args) == 5 and node.args[1] == path]
        struct = _one(structs, "translated guard Struct")
        _need(ast.location_line(struct.args[0]) == guard_line and struct.args[2] == [],
              "translated guard source/type parameters differ")
        body = struct.args[3]
        _need(isinstance(body, ast.Node) and body.name == "Left" and
              len(body.args) == 4 and body.args[0] == [] and body.args[2] == [],
              "translated guard fields are not a plain struct")
        ast_fields = body.args[1]
        _need(isinstance(ast_fields, list) and len(ast_fields) == 3 and
              [f.args[3] for f in ast_fields if isinstance(f, ast.Node) and
               f.name == "Field" and len(f.args) == 8] == names and
              _ast_type(ast, ast_fields[0].args[2], True) and
              _ast_type(ast, ast_fields[1].args[2], True) and
              _ast_type(ast, ast_fields[2].args[2], False),
              "translated guard field types/names differ")
        attrs = struct.args[4]
        _need(isinstance(attrs, list) and len(attrs) == 1 and
              isinstance(attrs[0], ast.Node) and
              attrs[0].name == "RustConcreteGuardLayout" and len(attrs[0].args) == 1,
              "translated guard layout attr missing or duplicated")
        helper = attrs[0].args[0]
        _need(isinstance(helper, ast.Node) and
              helper.name == "make_rust_concrete_guard_layout" and len(helper.args) == 8,
              "translated guard layout record is not the exact helper tuple")
        expected = [path, path_hash, "x86_64-unknown-linux-gnu", 64,
                    str(size), str(align), offsets, sizes]
        _need(helper.args == expected, "MIR/AST compiler layout metadata differs")
        bodies = [body for body in mir.path(tree, "bodies")
                  if mir.path(body, "defPath") == "insertion_onecell"]
        mir_body = _one(bodies, "source insertion_onecell MIR body")
        debug = mir.vdi_map(mir_body)
        local_ids = {}
        for name in ("tmp", "gap_guard"):
            local_id = _one(debug.get(name, []), f"{name} MIR debug local")
            _one([decl for decl in mir.path(mir_body, "localDecls")
                  if mir.path(decl, "id", "name") == local_id],
                 f"{name} MIR local declaration")
            local_ids[name] = local_id
        _need(local_ids["tmp"] != local_ids["gap_guard"],
              "tmp and guard share a MIR local")
        events = {name: [] for name in local_ids}
        blocks = mir.path(mir_body, "basicBlocks")
        for block in blocks:
            block_id = mir.path(block, "id", "index")
            for position, statement in enumerate(mir.path(block, "statements")):
                kind = mir.path(statement, "kind")
                for name, local_id in local_ids.items():
                    if kind.get("storageLive") == {"name": local_id}:
                        _need(set(kind) == {"storageLive"},
                              "MIR StorageLive has extra operations")
                        line, _, _ = _span(mir, mir.path(statement, "sourceInfo", "span"),
                                           source, allow_empty=True)
                        events[name].append((block_id, position, line))
        tmp_live = _one(events["tmp"], "tmp StorageLive")
        guard_live = _one(events["gap_guard"], "guard StorageLive")
        _need(tmp_live[2] == tmp_line and guard_live[2] == init_line and
              tmp_live[2] < guard_live[2],
              "MIR tmp/guard liveness does not match source anchors")
        _need(_concurrent_live_path(mir, blocks, tmp_live, guard_live,
                                    local_ids["tmp"]),
              "MIR does not connect tmp StorageLive to guard StorageLive while tmp is live")
        functions = [node for node in ast.nodes(ast_tree, "Func")
                     if len(node.args) == 13 and node.args[4] == "insertion_onecell"]
        function = _one(functions, "translated insertion_onecell function")
        runtime = function.args[10]
        _need(runtime != ast.Sym("None"), "translated function has no body")
        ordered = list(ast.walk(runtime))
        markers = {}
        for name, (_live_block, _live_pos, source_line) in (
                ("tmp", tmp_live), ("gap_guard", guard_live)):
            local_id = local_ids[name]
            found = [(i, node) for i, node in enumerate(ordered)
                     if node.name == "RustStorageLiveStmt" and len(node.args) == 4 and
                     node.args[2] == local_id and node.args[3] == name]
            index, marker = _one(found, f"{name} translated StorageLive")
            _need(ast.location_line(marker.args[1]) == source_line,
                  f"{name} AST marker differs from MIR span")
            markers[name] = index
        _need(markers["tmp"] < markers["gap_guard"],
              "translated tmp/guard StorageLive order differs")
        return {"admitted": True, "source_guard_line": guard_line,
                "layout": {"def_path": path, "def_path_hash": path_hash,
                           "target_triple": "x86_64-unknown-linux-gnu",
                           "pointer_width": 64, "size_bytes": size,
                           "align_bytes": align, "field_offsets": offsets,
                           "field_sizes": sizes},
                "locals": {"tmp": local_ids["tmp"], "gap_guard": local_ids["gap_guard"]},
                "storage_live_lines": {"tmp": tmp_live[2], "gap_guard": guard_live[2]},
                "decode_sha256": hashlib.sha256(decoded).hexdigest(),
                "proof_ast_sha256": hashlib.sha256(ast_bytes).hexdigest(),
                "verified_source_sha256": hashlib.sha256(source).hexdigest()}
    except Exception as error:
        return {"admitted": False, "reason": f"guard layout/source/MIR/AST gate failed: {error}"}
