"""Bounded, structural A1 OCaml AST dump gates; no proof verdicts.

The parser accepts only the constructor/list/tuple syntax emitted by the
pinned OCaml AST printer. Unknown syntax, shape, identity, or post structure
is inconclusive and raises AstGateError. Caller/MIR identity is a separate gate.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Mapping


MAX_TEXT = 16 * 1024 * 1024
MAX_SEGMENTS = 20000
MAX_DEPTH = 128
COMMON = "StableSmallSortTypeImpl::small_sort_threshold"
SMALL_SORT = "StableSmallSortTypeImpl::small_sort"
ROOT_QUALIFIED_FUNC_NAMES = frozenset((
    "<T as StableSmallSortTypeImpl>::small_sort_threshold",
    "<T as StableSmallSortTypeImpl>::small_sort",
))


class AstGateError(ValueError):
    pass


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise AstGateError(reason)


def digest(value: Any) -> str:
    return hashlib.sha256(repr(value).encode()).hexdigest()


def _valid_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _receipt_sha256(receipt: Mapping[str, Any]) -> str:
    return hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(",", ":"),
                                      ensure_ascii=False).encode("utf-8")).hexdigest()


def _receipt_pair_sha256(receipt: Mapping[str, Any]) -> str | None:
    parts = receipt.get("source_pair_sha256")
    if not isinstance(parts, Mapping) or not all(
            _valid_sha256(parts.get(key)) for key in ("verified", "original")):
        return None
    return hashlib.sha256((parts["verified"] + ":" + parts["original"]).encode("ascii")).hexdigest()


def _guard_r_only_reference_receipt(receipt: Mapping[str, Any], ast_sha256: str,
                                    source_pair_id: str,
                                    reference_source_text: str | None = None) -> None:
    """Validate versioned R-only capture provenance and source-anchored status."""
    need(isinstance(receipt, Mapping) and
         receipt.get("schema") == "a1-r-only-native-reference-receipt-v2" and
         receipt.get("mode") == "r-only-native-reference" and
         receipt.get("source_pair_id") == source_pair_id and
         receipt.get("stage_classification") == "TERMINAL" and
         type(receipt.get("observed_exit")) is int and
         all(_valid_sha256(receipt.get(key)) for key in (
             "reference_binary_sha256", "reference_translator_sha256",
             "profile_sha256", "ast_sha256", "actual_source_pair_sha256",
             "stage_log_sha256")) and
         _receipt_pair_sha256(receipt) == receipt.get("actual_source_pair_sha256") and
         isinstance(receipt.get("build_id"), str) and bool(receipt["build_id"]) and
         receipt.get("proof_credit") is False and
         receipt.get("ast_sha256") == ast_sha256,
         "R-only v2 capture receipt identity/hash/status is invalid")
    exit_code = receipt["observed_exit"]
    diagnostic = receipt.get("diagnostic")
    if exit_code == 0:
        need(receipt.get("capture_status") == "COMPLETE_NO_ERROR_EXIT0" and
             diagnostic is None,
             "R-only exit 0 capture status/diagnostic mismatch")
    elif exit_code == 1:
        need(receipt.get("capture_status") ==
             "COMPLETE_EXPECTED_DUPLICATE_PROTOTYPE_EXIT1" and
             isinstance(diagnostic, Mapping) and
             diagnostic.get("kind") == "duplicate-function-prototype" and
             diagnostic.get("source") == "verified/lib.rs" and
             type(diagnostic.get("line")) is int and diagnostic["line"] > 0 and
             type(diagnostic.get("start_column")) is int and diagnostic["start_column"] > 0 and
             type(diagnostic.get("end_column")) is int and
             diagnostic["end_column"] - diagnostic["start_column"] ==
             len("small_sort_threshold") and
             isinstance(diagnostic.get("declaration_text"), str) and
             diagnostic["declaration_text"].strip() ==
             "fn small_sort_threshold() -> usize;" and
             _valid_sha256(diagnostic.get("declaration_sha256")) and
             hashlib.sha256(diagnostic["declaration_text"].encode("utf-8")).hexdigest() ==
             diagnostic["declaration_sha256"] and
             diagnostic.get("count") == 1 and type(diagnostic.get("count")) is int,
             "R-only exit 1 lacks the unique source-anchored duplicate-prototype receipt")
        if reference_source_text is not None:
            matching_lines = [(number, line) for number, line in
                              enumerate(reference_source_text.splitlines(), 1)
                              if line.strip() == "fn small_sort_threshold() -> usize;"]
            need(len(matching_lines) == 1 and
                 matching_lines[0][0] == diagnostic["line"] and
                 matching_lines[0][1] == diagnostic["declaration_text"] and
                 matching_lines[0][1].index("small_sort_threshold") + 1 ==
                 diagnostic["start_column"] and
                 diagnostic["end_column"] == diagnostic["start_column"] +
                 len("small_sort_threshold"),
                 "R-only diagnostic is not anchored to the unique source threshold declaration")
    else:
        need(False, "R-only capture receipt exit is not admitted")


def balanced_end(source: str, opening: int) -> int:
    pairs = {"(": ")", "[": "]", "{": "}"}
    need(opening < len(source) and source[opening] in pairs, "opening delimiter")
    stack: list[str] = []
    quoted = escaped = False
    for pos in range(opening, len(source)):
        char = source[pos]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in pairs:
            need(len(stack) < MAX_DEPTH, "AST nesting bound")
            stack.append(pairs[char])
        elif char in ")]}":
            need(bool(stack) and stack[-1] == char, "AST delimiter mismatch")
            stack.pop()
            if not stack:
                return pos
    raise AstGateError("unclosed AST delimiter or string")


def fields(source: str, delimiter: str = ",") -> list[str]:
    source = source.strip()
    if not source:
        return []
    out: list[str] = []
    start = 0
    stack: list[str] = []
    quoted = escaped = False
    pairs = {"(": ")", "[": "]", "{": "}"}
    for pos, char in enumerate(source):
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char in pairs:
            need(len(stack) < MAX_DEPTH, "AST field nesting bound")
            stack.append(pairs[char])
        elif char in ")]}":
            need(bool(stack) and stack[-1] == char, "AST field delimiter mismatch")
            stack.pop()
        elif char == delimiter and not stack:
            out.append(source[start:pos].strip())
            start = pos + 1
    need(not stack and not quoted, "unbalanced AST fields")
    out.append(source[start:].strip())
    need(all(out), "empty AST field")
    return out


def _string(source: str) -> str:
    need(source.startswith('"') and source.endswith('"'), "quoted AST string")
    try:
        value = json.loads(source)
    except (ValueError, json.JSONDecodeError) as exc:
        raise AstGateError("unsupported OCaml string escape") from exc
    need(isinstance(value, str), "AST string type")
    return value


def tree(source: str, depth: int = 0) -> Any:
    """Parse a bounded OCaml constructor expression, not arbitrary OCaml."""
    need(depth < MAX_DEPTH, "AST expression depth")
    source = source.strip()
    need(bool(source), "empty AST expression")
    if source.startswith('"'):
        return ("str", _string(source))
    for prefix, tag in (("loc ", "loc"),
                        ("big_int_of_string ", "bigint"),
                        ("num_of_string ", "num")):
        if source.startswith(prefix):
            return (tag, _string(source[len(prefix):].strip()))
    if source[0] == "[":
        need(balanced_end(source, 0) == len(source) - 1, "AST list suffix")
        return ("list", tuple(tree(x, depth + 1) for x in
                              fields(source[1:-1], ";")))
    if source[0] == "(":
        need(balanced_end(source, 0) == len(source) - 1, "AST tuple suffix")
        members = fields(source[1:-1])
        return ("tuple", tuple(tree(x, depth + 1) for x in members))
    match = re.fullmatch(r"([A-Za-z_][A-Za-z_0-9]*)\s*\(", source[:source.find("(") + 1])
    if match:
        opening = source.find("(")
        need(balanced_end(source, opening) == len(source) - 1,
             "AST constructor suffix")
        return (match.group(1), tuple(tree(x, depth + 1) for x in
                                      fields(source[opening + 1:-1])))
    need(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*|[+-]?[0-9]+", source) is not None,
         "unsupported AST atom")
    return ("atom", source)


def node(value: Any, kind: str, arity: int | None = None) -> tuple[Any, ...]:
    need(isinstance(value, tuple) and len(value) == 2 and value[0] == kind and
         isinstance(value[1], tuple), "expected AST node " + kind)
    if arity is not None:
        need(len(value[1]) == arity, kind + " arity")
    return value[1]


def atom(value: Any, expected: str | None = None) -> str:
    need(isinstance(value, tuple) and len(value) == 2 and
         value[0] in ("atom", "str") and isinstance(value[1], str),
         "AST atom/string")
    if expected is not None:
        need(value[1] == expected, "expected AST atom " + expected)
    return value[1]


def items(value: Any) -> tuple[Any, ...]:
    return node(value, "list")


def normalize(value: Any, alpha: Mapping[str, str] | None = None) -> Any:
    """Erase source positions and rename only explicitly supplied binders."""
    alpha = alpha or {}
    if not isinstance(value, tuple) or len(value) != 2:
        raise AstGateError("malformed AST normalization node")
    kind, data = value
    if kind == "loc":
        return ("loc", "<source-location>")
    if kind == "str":
        return ("str", alpha.get(data, data))
    if isinstance(data, tuple):
        return (kind, tuple(normalize(x, alpha) for x in data))
    return value


def _segment_ranges(source: str, ctor: str) -> list[tuple[int, int, str]]:
    need(len(source) <= MAX_TEXT, "AST dump size bound")
    # A quoted source fragment may contain a line beginning with `Func (`.
    # Keep offsets, but blank all quoted characters before searching records.
    masked = list(source)
    quoted = escaped = False
    for pos, char in enumerate(source):
        if quoted:
            if char != "\n":
                masked[pos] = " "
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            masked[pos] = " "
            quoted = True
    need(not quoted, "unclosed quoted AST string")
    matches = list(re.finditer(r"(?m)^\s*" + re.escape(ctor) + r"\s*\(",
                               "".join(masked)))
    need(len(matches) <= MAX_SEGMENTS, "AST segment count bound")
    out = []
    for match in matches:
        begin = source.index("(", match.start())
        end = balanced_end(source, begin)
        start = match.start()
        out.append((start, end + 1, source[start:end + 1].strip()))
    return out


def _segments(source: str, ctor: str) -> list[str]:
    return [segment for _, _, segment in _segment_ranges(source, ctor)]


def _bounded_field_diagnostic(value: Any, *, preview_chars: int = 160) -> str:
    """Describe an unexpected AST field without echoing an unbounded value."""
    rendered = repr(value)
    encoded = rendered.encode("utf-8", errors="backslashreplace")
    preview = rendered[:preview_chars]
    return (f"repr={preview!r} repr_complete={len(rendered) <= preview_chars} "
            f"repr_chars={len(rendered)} repr_utf8_bytes={len(encoded)} "
            f"repr_sha256={hashlib.sha256(encoded).hexdigest()}")


def _package_func_local_error(owner: str, package_location: Any,
                              func_location: Any, local: Any) -> AstGateError:
    if isinstance(local, tuple) and len(local) == 2 and local[0] == "str":
        leaf = local[1]
        if isinstance(leaf, str):
            leaf_bytes = leaf.encode("utf-8")
            leaf_summary = (f"leaf={leaf[:160]!r} "
                            f"leaf_complete={len(leaf) <= 160} "
                            f"leaf_chars={len(leaf)} leaf_utf8_bytes={len(leaf_bytes)} "
                            f"leaf_sha256={hashlib.sha256(leaf_bytes).hexdigest()}")
        else:
            leaf_summary = "leaf=non-string " + _bounded_field_diagnostic(leaf)
    else:
        leaf_summary = "leaf=unavailable"
    return AstGateError(
        "package Func local name: "
        f"owner={_bounded_field_diagnostic(owner)} "
        f"package_location={_bounded_field_diagnostic(package_location)} "
        f"func_location={_bounded_field_diagnostic(func_location)} "
        f"local={_bounded_field_diagnostic(local)} {leaf_summary}")


def functions(source: str) -> list[dict[str, Any]]:
    def row(fs: tuple[Any, ...], name: str, raw: str) -> dict[str, Any]:
        body = fs[10]
        need(body == ("atom", "None") or
             isinstance(body, tuple) and body[0] == "Some" and
             len(node(body, "Some", 1)) == 1 and
             len(node(node(body, "Some", 1)[0], "tuple", 2)) == 2,
             "Func body option")
        return {"name": name, "fields": fs, "raw": raw,
                "kind": "prototype" if body == ("atom", "None") else "definition"}

    need(len(source) <= MAX_TEXT, "AST dump size bound")
    result = []
    # The final frontend dump is a list of PackageDecl chunks, after module
    # flattening. A package name is already cumulative; repeated chunks are legal.
    if source.lstrip().startswith("["):
        text = source.strip()
        need(balanced_end(text, 0) == len(text) - 1, "package list suffix")
        packages = fields(text[1:-1], ";")
        need(len(packages) <= MAX_SEGMENTS, "AST package count bound")
        for package in packages:
            match = re.match(r"PackageDecl\s*\(", package)
            need(match is not None, "final AST requires PackageDecl")
            opening = package.index("(")
            need(balanced_end(package, opening) == len(package) - 1,
                 "PackageDecl suffix")
            parts = fields(package[opening + 1:-1])
            need(len(parts) == 4, "PackageDecl arity")
            location = tree(parts[0])
            need(location[0] == "loc", "PackageDecl source location")
            name_value = tree(parts[1])
            need(name_value[0] == "str", "PackageDecl name string")
            owner = name_value[1]
            need(owner == "" or owner == "<T as StableSmallSortTypeImpl>" or
                 re.fullmatch(
                     r"[A-Za-z_][A-Za-z_0-9]*(?:::[A-Za-z_][A-Za-z_0-9]*)*",
                     owner) is not None, "noncanonical PackageDecl path")
            items(tree(parts[2]))
            declarations = parts[3]
            need(declarations.startswith("[") and
                 balanced_end(declarations, 0) == len(declarations) - 1,
                 "PackageDecl declaration list")
            decls = fields(declarations[1:-1], ";")
            need(len(decls) <= MAX_SEGMENTS, "AST declaration count bound")
            for declaration in decls:
                need(re.match(r"(?:PackageDecl|ModuleDecl)\b", declaration) is None,
                     "unexpected nested scope in final package")
                if re.match(r"Func\b", declaration):
                    fs = node(tree(declaration), "Func", 13)
                    local = fs[4]
                    if not (isinstance(local, tuple) and len(local) == 2 and
                            local[0] == "str" and isinstance(local[1], str) and
                            local[1]):
                        raise _package_func_local_error(owner, location, fs[0], local)
                    if "::" in local[1]:
                        if owner != "" or local[1] not in ROOT_QUALIFIED_FUNC_NAMES:
                            raise _package_func_local_error(owner, location,
                                                            fs[0], local)
                        # These two method names are already complete canonical
                        # identities in the root PackageDecl emitted by this
                        # translator path. Keep the exact string intact.
                        name = local[1]
                    else:
                        name = (owner + "::" if owner else "") + local[1]
                    record = row(fs, name, declaration)
                    record.update(package_name=owner, package_location=location)
                    result.append(record)
    else:
        # Legacy isolated service fixtures contain bare Func records. Never use
        # this compatibility path to recover a malformed actual package dump.
        masked = re.sub(r'"(?:[^"\\]|\\.)*"', '""', source, flags=re.S)
        need(re.search(r"\b(?:PackageDecl|ModuleDecl)\b", masked) is None,
             "scope requires complete final package list")
        for _, _, segment in _segment_ranges(source, "Func"):
            fs = node(tree(segment), "Func", 13)
            result.append(row(fs, atom(fs[4]), segment))
    need(bool(result), "no Func records in AST")
    return result


def _source_line(location: Any) -> int:
    need(isinstance(location, tuple) and location[0] == "loc",
         "Func source location")
    match = re.search(r"(?:^|/)verified/lib\.rs\(([1-9][0-9]*),", location[1])
    need(match is not None, "Func not bound to verified/lib.rs line")
    return int(match.group(1))


def _source_span(location: Any) -> tuple[tuple[str, int, int], tuple[str, int, int]]:
    """Decode the complete regular Lexed Func span in the canonical source."""
    need(isinstance(location, tuple) and len(location) == 2 and
         location[0] == "loc" and isinstance(location[1], str),
         "Func source span")
    match = re.fullmatch(
        r"(verified/lib\.rs)\(([1-9][0-9]*),([0-9]+)-"
        r"(?:([1-9][0-9]*),)?([0-9]+)\)", location[1])
    need(match is not None, "Func must have a full regular verified/lib.rs span")
    path, lo_line, lo_col, hi_line, hi_col = match.groups()
    if hi_line is None:
        hi_line = lo_line
    lo = (path, int(lo_line), int(lo_col))
    hi = (path, int(hi_line), int(hi_col))
    need((hi[1], hi[2]) >= (lo[1], lo[2]),
         "Func source span must be ordered")
    return lo, hi


def _compiler_source_span(value: Any) -> tuple[tuple[str, int, int], tuple[str, int, int]]:
    """Require a complete regular MIR body span from the source inventory."""
    need(isinstance(value, (tuple, list)) and len(value) == 2,
         "compiler original impl Body.span missing")
    points = []
    for point in value:
        need(isinstance(point, (tuple, list)) and len(point) == 3 and
             point[0] == "verified/lib.rs" and type(point[1]) is int and
             point[1] > 0 and type(point[2]) is int and point[2] >= 0,
             "compiler original impl Body.span must be regular verified/lib.rs")
        points.append((point[0], point[1], point[2]))
    need((points[1][1], points[1][2]) >= (points[0][1], points[0][2]),
         "compiler original impl Body.span must be ordered")
    return points[0], points[1]


def _compiler_source_span_as_ast(value: Any) -> tuple[tuple[str, int, int], tuple[str, int, int]]:
    """Translate raw MIR CharPos columns to the AST's explicitly 1-based columns."""
    span = _compiler_source_span(value)
    return tuple((path, line, column + 1) for path, line, column in span)


def _threshold_header(record: Mapping[str, Any], type_parameter: str) -> None:
    """Exact safe, zero-argument, usize function envelope of the pinned AST."""
    fs = record["fields"]
    parameters = items(fs[2])
    need(len(parameters) == 1, "threshold must have one type parameter")
    name, bounds = node(parameters[0], "tuple", 2)
    atom(name, type_parameter)
    sized, = node(bounds, "tuple", 1)
    atom(sized, "true")
    rt, = node(fs[3], "Some", 1)
    _, outcome_name, outcome_args = node(rt, "ConstructedTypeExpr", 3)
    atom(outcome_name, "fn_outcome")
    outcome_types = items(outcome_args)
    need(len(outcome_types) == 1, "one threshold normal-result type")
    _, manifest = node(outcome_types[0], "ManifestTypeExpr", 2)
    signed, rank = node(manifest, "Int", 2)
    atom(signed, "Unsigned")
    atom(rank, "PtrRank")
    need(fs[1] == ("atom", "Regular") and
         fs[5] == ("list", ()) and fs[6] == ("atom", "false") and
         fs[7] == ("tuple", (("atom", "None"), ("atom", "None"))) and
         fs[9] == ("atom", "false") and fs[11] == ("atom", "false") and
         fs[12] == ("list", ()), "safe zero-arg threshold header")


def _range(value: Any, binder: str) -> None:
    loc, op, args = node(value, "Operation", 3)
    atom(op, "And")
    parts = items(args)
    need(len(parts) == 2, "two checked range conjuncts")
    lower, upper = parts
    def integer(value: Any, expected: str) -> None:
        fields_ = node(value, "IntLit", 5)
        need(fields_[1] == ("bigint", expected) and
             fields_[2:] == (("atom", "true"), ("atom", "false"),
                            ("atom", "NoLSuffix")),
             "checked range integer literal")
    def variable(value: Any) -> None:
        _, name = node(value, "Var", 2)
        atom(name, binder)
    _, lop, larg = node(lower, "Operation", 3)
    _, uop, uarg = node(upper, "Operation", 3)
    atom(lop, "Le")
    atom(uop, "Le")
    need(len(items(larg)) == len(items(uarg)) == 2,
         "binary checked range comparisons")
    left, middle = items(larg)
    right, top = items(uarg)
    integer(left, "16")
    variable(middle)
    variable(right)
    integer(top, "32")
    need(isinstance(loc, tuple) and loc[0] == "loc", "range location")


def contract(record: Mapping[str, Any], checked: bool) -> dict[str, Any]:
    spec, = node(record["fields"][8], "Some", 1)
    pre, outcome_post = node(spec, "tuple", 2)
    outcome, post = node(outcome_post, "tuple", 2)
    outcome_name = atom(outcome)
    _, discrim, arms, default = node(post, "SwitchExpr", 4)
    need(default == ("atom", "None"), "unexpected threshold outcome default")
    _, discriminant = node(discrim, "Var", 2)
    atom(discriminant, outcome_name)
    need(len(items(arms)) == 2, "exact returning and unwind arms")
    returning, unwinding = items(arms)
    _, return_name, result_args, normal = node(returning, "SwitchExprClause", 4)
    _, unwind_name, unwind_args, unwind = node(unwinding, "SwitchExprClause", 4)
    atom(return_name, "returning")
    atom(unwind_name, "unwinding")
    need(len(items(result_args)) == 1, "one returning result binder")
    result, = items(result_args)
    result_name = atom(result)
    need(len(items(unwind_args)) == 0 and result_name != outcome_name,
         "threshold outcome binders")
    if checked:
        _, native, range_post = node(normal, "Sep", 3)
        _range(range_post, result_name)
    else:
        native = normal
        need(not _contains_range(native), "unchecked common threshold has range")
    need(not _contains_range(unwind), "unwind arm contains checked range")
    alpha = {outcome_name: "@outcome", result_name: "@result"}
    return {"pre": normalize(pre, alpha),
            "native_returning": normalize(native, alpha),
            "unwinding": normalize(unwind, alpha),
            "checked_range": checked,
            "source_line": _source_line(record["fields"][0])}


def _contains_range(value: Any) -> bool:
    if not isinstance(value, tuple) or len(value) != 2:
        return False
    if value[0] == "Operation":
        try:
            _, _, arguments = node(value, "Operation", 3)
            lower = items(arguments)[0]
            _, _, comparisons = node(lower, "Operation", 3)
            _, variable = node(items(comparisons)[1], "Var", 2)
            _range(value, atom(variable))
        except (AstGateError, IndexError):
            pass
        else:
            return True
    return isinstance(value[1], tuple) and any(_contains_range(x) for x in value[1])


def _impl_identity(inventory: Mapping[str, Mapping[str, Any]]) -> dict[str, dict]:
    need(set(inventory) == {"default16", "freeze32"}, "two compiler impls required")
    result = {}
    ids = []
    for impl, row in inventory.items():
        impl_id = str(row.get("compiler_impl_id", ""))
        item_id = str(row.get("compiler_item_id", ""))
        need(re.fullmatch(r"[1-9][0-9]*", impl_id) is not None and
             re.fullmatch(r"[1-9][0-9]*", item_id) is not None and
             isinstance(row.get("source_line"), int) and row["source_line"] > 0,
             "numeric compiler item/span identity")
        diagnostic = row.get("diagnostic_post_line")
        need(isinstance(diagnostic, int) and diagnostic > 0,
             "compiler fnSigSpan diagnostic post line")
        ids.extend((impl_id, item_id))
        result[impl] = {"alias": f"__a1_impl_{impl_id}_item_{item_id}_small_sort_threshold",
                        "source_line": row["source_line"],
                        "diagnostic_post_line": diagnostic,
                        "compiler_impl_id": impl_id, "compiler_item_id": item_id}
    need(len(set(ids)) == 4, "duplicate compiler impl/item identity")
    return result


def threshold_posts(ast: str, inventory: Mapping[str, Mapping[str, Any]],
                    *, stage: str, baseline: Mapping[str, Any] | None = None,
                    common_line: int | None = None) -> dict[str, Any]:
    """Check exact source-bound common/prototype/body post structure only."""
    need(stage in {"bodies", "interface", "caller"}, "A1 AST stage")
    identities = _impl_identity(inventory)
    fs = functions(ast)
    common = [row for row in fs if row["name"] == COMMON]
    need(len(common) == 1 and common[0]["kind"] == "prototype",
         "one common threshold prototype")
    _threshold_header(common[0], "Self")
    need(common_line is not None and common_line > 0 and
         _source_line(common[0]["fields"][0]) == common_line,
         "common threshold source span")
    checked_common = stage == "caller"
    common_post = contract(common[0], checked_common)
    native = {key: common_post[key] for key in
              ("pre", "native_returning", "unwinding")}
    if checked_common:
        need(baseline is not None and all(native[key] == baseline.get(key)
             for key in native), "published common post differs from native baseline")
    else:
        need(baseline is None or all(native[key] == baseline.get(key)
             for key in native), "common post native baseline drift")
    checked_rows = {}
    aliases = set()
    for impl, identity in identities.items():
        alias = identity["alias"]
        aliases.add(alias)
        found = [row for row in fs if row["name"] == alias]
        proto = [row for row in found if row["kind"] == "prototype"]
        body = [row for row in found if row["kind"] == "definition"]
        need(len(found) == 2 and len(proto) == len(body) == 1,
             "one impl prototype and one actual definition: " + impl)
        need(all(normalize(row["fields"][3]) ==
                 normalize(common[0]["fields"][3]) for row in found),
             "impl threshold zero-arg safe usize signature")
        for row in found:
            _threshold_header(row, "T")
        for row in found:
            need(_source_line(row["fields"][0]) == identity["source_line"],
                 "impl AST source span differs from compiler item")
        need(all(normalize(proto[0]["fields"][index]) ==
                 normalize(body[0]["fields"][index])
                 for index in (*range(0, 8), 9, 11, 12)),
             "impl prototype/body header mismatch")
        posts = [contract(row, True) for row in (proto[0], body[0])]
        need(all(all(post[key] == native[key] for key in native)
                 for post in posts),
             "impl native pre/returning/unwind post changed: " + impl)
        checked_rows[impl] = {"alias": alias, "source_line": identity["source_line"],
                              "diagnostic_post_line": identity["diagnostic_post_line"],
                              "prototype_contract_sha256": digest(posts[0]),
                              "body_contract_sha256": digest(posts[1]),
                              "compiler_impl_id": identity["compiler_impl_id"],
                              "compiler_item_id": identity["compiler_item_id"]}
    need(not any(row["name"].startswith("__a1_impl_") and
                 row["name"].endswith("_small_sort_threshold") and
                 row["name"] not in aliases for row in fs),
         "unexpected generated implementation alias")
    return {"classification": "STRUCTURE_ONLY_UNRUN_PROOF",
            "stage": stage, "common_checked": checked_common,
            "native": native,
            "native_sha256": {key: digest(value) for key, value in native.items()},
            "impls": checked_rows, "proof_credit": False,
            "body_conformance_proved": False}


def _small_sort_native(record: Mapping[str, Any], alpha: Mapping[str, str]) -> dict[str, Any]:
    spec, = node(record["fields"][8], "Some", 1)
    pre, outcome_post = node(spec, "tuple", 2)
    outcome, post = node(outcome_post, "tuple", 2)
    outcome_name = atom(outcome)
    _, discrim, arms, default = node(post, "SwitchExpr", 4)
    need(default == ("atom", "None"), "small_sort outcome default")
    _, discriminant = node(discrim, "Var", 2)
    atom(discriminant, outcome_name)
    clauses = items(arms)
    returning = [x for x in clauses if node(x, "SwitchExprClause", 4)[1] == ("str", "returning")]
    unwinding = [x for x in clauses if node(x, "SwitchExprClause", 4)[1] == ("str", "unwinding")]
    need(len(clauses) == 2 and len(returning) == len(unwinding) == 1,
         "small_sort must retain exactly returning and unwind outcomes")
    _, _, result_args, normal = node(returning[0], "SwitchExprClause", 4)
    _, _, unwind_args, unwind = node(unwinding[0], "SwitchExprClause", 4)
    need(len(items(result_args)) == 1 and len(items(unwind_args)) == 0,
         "small_sort outcome binder shape")
    result_name = atom(items(result_args)[0])
    scoped = {**alpha, outcome_name: "@outcome", result_name: "@result"}
    return {"pre": normalize(pre, scoped),
            "returning": normalize(normal, scoped),
            "unwind": normalize(unwind, scoped)}


def _small_sort_generic_names(record: Mapping[str, Any]) -> tuple[str, ...]:
    rows = items(record["fields"][2])
    names = []
    for row in rows:
        name, _bounds = node(row, "tuple", 2)
        names.append(atom(name))
    return tuple(names)


def _small_sort_alpha(record: Mapping[str, Any], *, self_name: str) -> dict[str, str]:
    names = _small_sort_generic_names(record)
    need(len(names) == 5 and names[:2] == (self_name, "F") and
         all(name.startswith("'") and name not in ("'static", "'_<erased>")
             for name in names[2:]) and len(set(names[2:])) == 3,
         "small_sort AST must declare Self/F and three distinct positional input regions")
    alpha = {self_name: "@Self", "Self": "@Self", "T": "@Self", "F": "@F"}
    for i, name in enumerate(names[2:]):
        # AST type identifiers keep the apostrophe; gen_contract uses the
        # internal ghost lifetime spelling without it. Both are bound by the
        # same compiler-derived positional region identity.
        alpha[name] = f"@input_{i}"
        alpha[name[1:]] = f"@input_{i}"
        alpha["_q_" + name[1:]] = f"@input_{i}_fraction"
    return alpha


def _ast_region_expr(value: Any) -> str:
    if isinstance(value, tuple) and value[0] == "Var":
        _, name = node(value, "Var", 2)
        return atom(name)
    if isinstance(value, tuple) and value[0] == "IdentTypeExpr":
        _, package, name = node(value, "IdentTypeExpr", 3)
        need(package == ("atom", "None"), "small_sort AST lifetime package")
        return atom(name)
    raise AstGateError("small_sort AST lifetime expression")


def _ast_ty(value: Any) -> Any:
    if not isinstance(value, tuple) or len(value) != 2:
        raise AstGateError("small_sort AST type expression")
    kind, _ = value
    if kind == "RustRefTypeExpr":
        loc, region, mutability, referent = node(value, kind, 4)
        need(isinstance(loc, tuple) and loc[0] == "loc", "reference type location")
        need(mutability in (("atom", "Mutable"), ("atom", "Shared")),
             "reference mutability tag")
        return ("ref", _ast_region_expr(region), mutability[1] == "Mutable", _ast_ty(referent))
    if kind == "SliceTypeExpr":
        loc, elem = node(value, kind, 2)
        need(isinstance(loc, tuple) and loc[0] == "loc", "slice type location")
        return ("slice", _ast_ty(elem))
    if kind == "IdentTypeExpr":
        _, package, name = node(value, kind, 3)
        need(package in (("atom", "None"), ("Some", (("str", "core"),)),
                         ("Some", (("str", "std"),))), "type identifier package")
        return ("param", atom(name))
    if kind == "StructTypeExpr":
        loc, name, _fields, _attrs, args = node(value, kind, 5)
        need(isinstance(loc, tuple) and loc[0] == "loc", "struct type location")
        name_option = node(name, "Some", 1)
        struct_name = atom(name_option[0])
        need(struct_name == "std::mem::MaybeUninit",
             "small_sort AST ADT identifier is not translator-canonical std::mem::MaybeUninit")
        type_args = tuple(_ast_ty(x) for x in items(args))
        return ("adt", struct_name.split("::")[-1], type_args)
    if kind == "ManifestTypeExpr":
        _loc, manifest = node(value, kind, 2)
        return ("manifest", normalize(manifest))
    raise AstGateError("unsupported small_sort AST signature type " + str(kind))


def _small_sort_ast_signature(record: Mapping[str, Any], self_name: str,
                              alpha: Mapping[str, str]) -> tuple[Any, ...]:
    rows = items(record["fields"][5])
    need(len(rows) == 3, "small_sort AST must retain exactly three typed parameters")
    names, types = [], []
    for row in rows:
        typ, name = node(row, "tuple", 2)
        # Some translator paths preserve immutable parameter bindings as one
        # outer ConstTypeExpr; others emit the bare type. Normalize that
        # binding marker only here. Do not unwrap constness inside references
        # or other nested type constructors.
        if isinstance(typ, tuple) and typ and typ[0] == "ConstTypeExpr":
            _const_loc, typ = node(typ, "ConstTypeExpr", 2)
            need(isinstance(_const_loc, tuple) and len(_const_loc) == 2 and
                 _const_loc[0] == "loc" and isinstance(_const_loc[1], str),
                 "small_sort AST parameter ConstTypeExpr location")
        types.append(_ast_ty(typ))
        names.append(atom(name))
    need(tuple(names) in (("v", "scratch", "is_less"),
                          ("v", "_scratch", "is_less")),
         "small_sort AST parameter order/name binding")
    normalized = []
    for typ in types:
        def rename(value):
            if isinstance(value, tuple):
                if len(value) == 2 and value[0] == "param":
                    return ("param", alpha.get(value[1], value[1]))
                if len(value) == 3 and value[0] == "ref":
                    return (value[0], alpha.get(value[1], value[1]), value[2], rename(value[2]))
                return tuple(rename(x) for x in value)
            return alpha.get(value, value) if isinstance(value, str) else value
        normalized.append(rename(typ))
    expected = (("ref", "@input_0", True, ("slice", ("param", "@Self"))),
                ("ref", "@input_1", True, ("slice", ("adt", "MaybeUninit", (("param", "@Self"),)))),
                ("ref", "@input_2", True, ("param", "@F")))
    need(tuple(normalized) == expected,
         "small_sort AST typed parameters differ from compiler Self/F/input-region signature")
    return tuple(normalized)


def _small_sort_ast_scratch_name(record: Mapping[str, Any]) -> str:
    rows = items(record["fields"][5])
    need(len(rows) == 3, "small_sort AST must retain exactly three typed parameters")
    _typ, name = node(rows[1], "tuple", 2)
    scratch_name = atom(name)
    need(scratch_name in ("scratch", "_scratch"),
         "small_sort AST scratch parameter name")
    return scratch_name


def _compiler_small_sort_type_to_ast(value: Any) -> Any:
    """Convert compiler canonical types to the AST gate's matching shape."""
    if not isinstance(value, tuple):
        return value
    if len(value) == 2 and value[0] == "param":
        return ("param", {"Self": "@Self", "F": "@F"}.get(value[1], value[1]))
    if value and value[0] == "adt":
        args = tuple(_compiler_small_sort_type_to_ast(arg[1])
                     if isinstance(arg, tuple) and len(arg) == 2 and arg[0] == "type"
                     else arg for arg in value[2])
        return ("adt", value[1].split("::")[-1], args)
    return tuple(_compiler_small_sort_type_to_ast(x) for x in value)


def _small_sort_ast_return(record: Mapping[str, Any]) -> str:
    wrapped, = node(record["fields"][3], "Some", 1)
    _, outcome_name, args = node(wrapped, "ConstructedTypeExpr", 3)
    atom(outcome_name, "fn_outcome")
    returns = items(args)
    need(len(returns) == 1, "small_sort must retain one normal return type")
    _, unit = node(returns[0], "ManifestTypeExpr", 2)
    struct_name, struct_args = node(unit, "StructType", 2)
    atom(struct_name, "std_tuple_0_")
    need(items(struct_args) == (), "small_sort normal return type must be unit")
    return "unit"


def _small_sort_ast_header(record: Mapping[str, Any], alpha: Mapping[str, str]) -> tuple[Any, ...]:
    """Normalize complete regular/safe header fields retained by Func."""
    return tuple(normalize(record["fields"][index], alpha)
                 for index in (1, 2, 3, 5, 6, 7, 9, 11, 12))


def _small_sort_ast_header_for_common_comparison(header: tuple[Any, ...]) -> tuple[Any, ...]:
    """Project outer binding markers and the second label for common comparison.

    Keep original parameter names in stored headers and same-body comparisons.
    The blanket impl spells the unused second binding `_scratch`; its trait
    prototype and Freeze impl spell it `scratch`.
    """
    need(isinstance(header, tuple) and len(header) == 9,
         "small_sort AST normalized header shape")
    parameters = list(items(header[3]))
    need(len(parameters) == 3, "small_sort AST normalized parameter count")
    parameter_types = [node(row, "tuple", 2)[0] for row in parameters]
    parameter_names = [node(row, "tuple", 2)[1] for row in parameters]
    need(parameter_names == [("str", "v"), ("str", "scratch"), ("str", "is_less")] or
         parameter_names == [("str", "v"), ("str", "_scratch"), ("str", "is_less")],
         "small_sort AST normalized parameter names")
    for index, typ in enumerate(parameter_types):
        if isinstance(typ, tuple) and typ and typ[0] == "ConstTypeExpr":
            binding_loc, typ = node(typ, "ConstTypeExpr", 2)
            need(isinstance(binding_loc, tuple) and len(binding_loc) == 2 and
                 binding_loc[0] == "loc" and isinstance(binding_loc[1], str),
                 "small_sort AST header parameter binding marker location")
            # Only an outer immutable binding marker is a representation choice.
            # Nested constness and the reference's own mutability stay exact.
            node(typ, "RustRefTypeExpr", 4)
        parameters[index] = ("tuple", (typ, parameter_names[index]))
    parameters[1] = ("tuple", (node(parameters[1], "tuple", 2)[0],
                                ("str", "@scratch-binding")))
    projected = list(header)
    projected[3] = ("list", tuple(parameters))
    return tuple(projected)


def _bounded_header_difference(actual: Any, expected: Any) -> str:
    """Report at most three differing leaves without serializing AST bodies."""
    rows = []

    def visit(left, right, path):
        if len(rows) >= 3 or left == right:
            return
        if (type(left) is type(right) and isinstance(left, (tuple, list)) and
                len(left) == len(right)):
            for index, (a, b) in enumerate(zip(left, right)):
                visit(a, b, path + "/" + str(index))
                if len(rows) >= 3:
                    break
        else:
            rows.append(path + ": actual=" + repr(left)[:160] +
                        "; expected=" + repr(right)[:160])

    visit(actual, expected, "header")
    return " | ".join(rows)


def _small_sort_scratch_name_from_header(header: tuple[Any, ...]) -> str:
    need(isinstance(header, tuple) and len(header) == 9,
         "small_sort AST normalized header shape")
    parameters = items(header[3])
    need(len(parameters) == 3, "small_sort AST normalized parameter count")
    _typ, name = node(parameters[1], "tuple", 2)
    name = atom(name)
    need(name in ("scratch", "_scratch"),
         "small_sort AST normalized scratch parameter name")
    return name


def _small_sort_native_for_common_comparison(native: Mapping[str, Any],
                                              scratch_name: str) -> dict[str, Any]:
    """Alpha-rename only scratch Vars and its translator-generated fold binders.

    Stored native trees and same-body comparisons remain raw. This view is only
    for comparing trait and impl contracts whose source binding names differ.
    """
    need(scratch_name in ("scratch", "_scratch"),
         "small_sort native comparison scratch parameter name")
    need(isinstance(native, Mapping) and set(native) == {"pre", "returning", "unwind"},
         "small_sort native comparison shape")
    source_folds = {f"_v{index}_{scratch_name}": index for index in (0, 1)}
    counts: dict[tuple[str, str], int] = {}
    strings: set[str] = set()

    def inspect(value: Any) -> None:
        if isinstance(value, tuple) and len(value) == 2:
            kind, data = value
            if kind in ("Var", "VarPat"):
                need(isinstance(data, tuple) and len(data) == 2 and
                     isinstance(data[1], tuple) and len(data[1]) == 2 and
                     data[1][0] == "str" and isinstance(data[1][1], str),
                     "small_sort native variable node")
                name = data[1][1]
                strings.add(name)
                if kind == "Var" and name == scratch_name:
                    counts[(kind, name)] = counts.get((kind, name), 0) + 1
                fold_match = re.fullmatch(r"_v([0-9]+)_" + re.escape(scratch_name), name)
                if fold_match is not None:
                    need(fold_match.group(1) in ("0", "1"),
                         "unrecognized small_sort generated scratch fold binder")
                    counts[(kind, name)] = counts.get((kind, name), 0) + 1
            if kind == "str" and isinstance(data, str):
                strings.add(data)
            if isinstance(data, tuple):
                for item in data:
                    inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)
        elif isinstance(value, dict):
            for item in value.values():
                inspect(item)

    inspect(native)
    generated = {name for _kind, name in counts if name in source_folds}
    for name in generated:
        need(counts.get(("VarPat", name), 0) > 0 and
             counts.get(("Var", name), 0) > 0,
             "small_sort generated scratch fold binder is unbound or unused")

    def fresh(label: str) -> str:
        stem = f"\x00a1-native-{label}"
        candidate = stem + "\x00"
        suffix = 0
        while candidate in strings:
            suffix += 1
            candidate = f"{stem}-{suffix}\x00"
        strings.add(candidate)
        return candidate

    replacements = {scratch_name: fresh("param-scratch")}
    for name in generated:
        replacements[name] = fresh(f"fold-{source_folds[name]}")

    def rewrite(value: Any) -> Any:
        if isinstance(value, tuple) and len(value) == 2:
            kind, data = value
            if kind in ("Var", "VarPat") and isinstance(data, tuple) and len(data) == 2:
                name_node = data[1]
                if (isinstance(name_node, tuple) and len(name_node) == 2 and
                        name_node[0] == "str" and
                        ((kind == "Var" and name_node[1] in replacements) or
                         (kind == "VarPat" and name_node[1] in generated))):
                    return (kind, (rewrite(data[0]), ("str", replacements[name_node[1]])))
            return (kind, tuple(rewrite(item) for item in data)) \
                if isinstance(data, tuple) else value
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if isinstance(value, dict):
            return {key: rewrite(item) for key, item in value.items()}
        return value

    return rewrite(dict(native))


def _small_sort_ast_bounds(record: Mapping[str, Any]) -> tuple[bool, ...]:
    rows = items(record["fields"][2])
    bounds = []
    for row in rows:
        _, payload = node(row, "tuple", 2)
        (value,) = node(payload, "tuple", 1)
        need(value in (("atom", "true"), ("atom", "false")),
             "small_sort AST generic bound marker")
        bounds.append(value == ("atom", "true"))
    need(len(bounds) == 5 and tuple(bounds[:2]) == (True, True) and
         tuple(bounds[2:]) == (False, False, False),
         "small_sort AST Self/F sized markers and signature lifetimes differ from compiler interface")
    return tuple(bounds)


def _small_sort_impl_surface(record: Mapping[str, Any], identity: Mapping[str, Any], *,
                             label: str) -> dict[str, Any]:
    """Bind an original/candidate impl definition to its compiler item identity."""
    item_path = identity.get("item_def_id")
    need(isinstance(item_path, str) and item_path and record.get("name") == item_path and
         record.get("kind") == "definition",
         label + " AST definition does not match its compiler item DefPath")
    source_body_span = _compiler_source_span(identity.get("source_body_span"))
    need(_source_line(record["fields"][0]) == identity.get("ast_body_line") and
         _source_span(record["fields"][0]) ==
         _compiler_source_span_as_ast(source_body_span),
         label + " AST definition span differs from compiler Body.span")
    signature = identity.get("compiler_signature")
    need(isinstance(signature, Mapping) and
         signature.get("digest") == identity.get("compiler_signature_digest"),
         label + " compiler Body signature identity missing")
    alpha = _small_sort_alpha(record, self_name="T")
    ast_signature = _small_sort_ast_signature(record, "T", alpha)
    expected_signature = tuple(_compiler_small_sort_type_to_ast(x)
                               for x in signature.get("inputs", ()))
    need(ast_signature == expected_signature,
         label + " AST parameter types differ from compiler Body signature")
    compiler_regions = signature.get("input_regions")
    ast_regions = _small_sort_generic_names(record)[2:]
    need(compiler_regions == ("@input_0", "@input_1", "@input_2") and
         tuple(alpha.get(region) for region in ast_regions) == compiler_regions,
         label + " AST lifetime alpha map differs from compiler positional input-region map")
    need(_small_sort_ast_return(record) == "unit",
         label + " AST return type differs from compiler unit output")
    _small_sort_ast_bounds(record)
    native = _small_sort_native(record, alpha)
    header = _small_sort_ast_header(record, alpha)
    return {"item_def_id": item_path, "compiler_impl_id": identity.get("impl_def_index"),
            "compiler_item_id": identity.get("item_def_index"),
            "compiler_signature_digest": signature["digest"],
            "positional_alpha_map": tuple(sorted(alpha.items())),
            "compiler_positional_region_map": tuple(zip(ast_regions, compiler_regions)),
            "normalized_header": header, "normalized_native": native,
            "native_sha256": {key: digest(value) for key, value in native.items()},
            "ast_body_line": identity["ast_body_line"],
            "source_body_span": source_body_span}


def small_sort_native_baseline(ast: str, inventory: Mapping[str, Any], *,
                               source_pair_id: str,
                               reference_receipt: Mapping[str, Any],
                               reference_source_text: str) -> dict[str, Any]:
    """Extract native small_sort structure from the independently run R-only AST.

    The caller must label this result only after collecting the AST from a
    separate R-only native-reference invocation. This routine grants no
    proof/conformance credit. `source_pair_id` is the compiler inventory's
    certified verified-source ID; the receipt separately binds the actual
    verified+original pair by its two file hashes and their combined digest.
    """
    observed = _inventory_payload(inventory)
    interface = observed.get("required_small_sort")
    need(isinstance(interface, Mapping), "compiler required small_sort interface missing")
    case = inventory.get("case_binding", {})
    need(isinstance(case, Mapping) and case.get("source_pair_id") == source_pair_id,
         "R-only baseline source pair does not match compiler inventory")
    _guard_r_only_reference_receipt(
        reference_receipt, hashlib.sha256(ast.encode("utf-8")).hexdigest(),
        source_pair_id, reference_source_text)
    fs = functions(ast)
    required_id = interface.get("required_def_id")
    common = [row for row in fs if row["name"] == required_id]
    need(len(common) == 1 and common[0]["kind"] == "prototype",
         "R-only AST must contain the compiler-bound required small_sort prototype")
    alpha = _small_sort_alpha(common[0], self_name="Self")
    signature = _small_sort_ast_signature(common[0], "Self", alpha)
    need(interface.get("ast_type_param_names") == ("Self", "F") and
         signature == tuple(_compiler_small_sort_type_to_ast(x)
                            for x in interface.get("inputs", ())) and
         interface.get("output") == ("tuple", ()) and
         _small_sort_ast_return(common[0]) == "unit",
         "R-only required AST signature differs from compiler-derived interface")
    _small_sort_ast_bounds(common[0])
    need(_source_line(common[0]["fields"][0]) == interface["source_span"][0][1],
         "R-only required small_sort AST location differs from compiler nameSpan")
    native = _small_sort_native(common[0], alpha)
    common_native_projection = _small_sort_native_for_common_comparison(
        native, _small_sort_ast_scratch_name(common[0]))
    common_header = _small_sort_ast_header(common[0], alpha)
    impl_identities = observed.get("impl_small_sort_identities")
    need(isinstance(impl_identities, (tuple, list)) and len(impl_identities) == 2,
         "compiler-bound original small_sort impl identities missing from R-only baseline")
    original_impls = {}
    identity_keys = set()
    impl_ids = set()
    item_ids = set()
    source_spans = set()
    by_item_path: dict[str, list[Mapping[str, Any]]] = {}
    for identity in impl_identities:
        need(isinstance(identity, Mapping) and
             identity.get("impl") in ("default16", "freeze32") and
             identity["impl"] not in original_impls,
             "compiler original impl identity row is malformed or duplicated")
        item_path = identity.get("item_def_id")
        impl_id, item_id = identity.get("impl_def_index"), identity.get("item_def_index")
        source_body_span = _compiler_source_span(identity.get("source_body_span"))
        identity_key = (impl_id, item_id)
        need(isinstance(item_path, str) and bool(item_path) and
             type(impl_id) is int and impl_id > 0 and
             type(item_id) is int and item_id > 0 and
             identity_key not in identity_keys and impl_id not in impl_ids and
             item_id not in item_ids,
             "compiler original impl numeric identity is missing or duplicated")
        need(source_body_span not in source_spans,
             "compiler original impl Body.span is missing or duplicated")
        identity_keys.add(identity_key)
        impl_ids.add(impl_id)
        item_ids.add(item_id)
        source_spans.add(source_body_span)
        by_item_path.setdefault(item_path, []).append(identity)
        matches = [row for row in fs if row["name"] == item_path and
                   row["kind"] == "definition" and
                   _source_span(row["fields"][0]) ==
                   _compiler_source_span_as_ast(source_body_span)]
        need(len(matches) == 1,
             "R-only AST must contain one original impl definition by compiler DefPath and full Body.span: " +
             identity["impl"])
        surface = _small_sort_impl_surface(matches[0], identity,
                                           label="R-only " + identity["impl"])
        impl_native_projection = _small_sort_native_for_common_comparison(
            surface["normalized_native"], _small_sort_ast_scratch_name(matches[0]))
        need(impl_native_projection == common_native_projection,
             "unmodified R-only impl native contract differs from required common baseline: " +
             identity["impl"])
        compared_header = _small_sort_ast_header_for_common_comparison(
            surface["normalized_header"])
        expected_header = _small_sort_ast_header_for_common_comparison(common_header)
        need(compared_header == expected_header,
             "unmodified R-only impl typed header differs from required common baseline: " +
             identity["impl"] + "; " +
             _bounded_header_difference(compared_header, expected_header))
        original_impls[identity["impl"]] = surface
    for item_path, identities in by_item_path.items():
        path_definitions = [row for row in fs if row["name"] == item_path and
                            row["kind"] == "definition"]
        need(len(path_definitions) == len(identities),
             "R-only AST DefPath has unbound or ambiguous original impl definitions: " +
             item_path)
        for row in path_definitions:
            row_span = _source_span(row["fields"][0])
            need(sum(_compiler_source_span_as_ast(identity["source_body_span"]) == row_span
                     for identity in identities) == 1,
                 "R-only AST original impl definition does not bind uniquely back to compiler Body.span: " +
                 item_path)
    need(set(original_impls) == {"default16", "freeze32"},
         "R-only baseline must bind both original small_sort impl definitions")
    return {"schema": "a1-small-sort-native-baseline-v1",
            "provenance": "r-only-native-translation",
            "source_pair_id": source_pair_id,
            "actual_source_pair_sha256": reference_receipt["actual_source_pair_sha256"],
            "compiler_interface_digest": interface["interface_digest"],
            "reference_receipt": dict(reference_receipt),
            "reference_receipt_sha256": _receipt_sha256(reference_receipt),
            "ast_sha256": hashlib.sha256(ast.encode("utf-8")).hexdigest(),
            "normalized_header": common_header,
            "normalized_native": native,
            "native_sha256": {key: digest(value) for key, value in native.items()},
            "normalized_impls": original_impls,
            "proof_credit": False, "conformance_credit": False}


def _inventory_payload(inventory: Mapping[str, Any]) -> Mapping[str, Any]:
    need(isinstance(inventory, Mapping) and
         inventory.get("schema") == "a1-compiler-inventory-observation-v1" and
         inventory.get("provenance") == "source-reported-compiler-inventory-only" and
         inventory.get("proof_credit") is False,
         "full source-reported compiler inventory observation required")
    payload = inventory.get("inventory")
    need(isinstance(payload, Mapping), "compiler inventory payload missing")
    return payload


def small_sort_interface(ast: str, inventory: Mapping[str, Any], *,
                         baseline: Mapping[str, Any] | None,
                         actual_source_pair_sha256: str) -> dict[str, Any]:
    """Bind compiler-required and both impl small_sort ASTs; interface only.

    The baseline must come from a separate R-only native-reference AST dump.
    `actual_source_pair_sha256` is recomputed from the exact pair hashes in its
    receipt and compared independently of the inventory's source ID.
    Every compared contract is complete native pre/returning/unwind structure;
    only explicit positional binder alpha-renaming is permitted.
    """
    payload = _inventory_payload(inventory)
    case = inventory.get("case_binding")
    need(isinstance(case, Mapping) and isinstance(case.get("source_pair_id"), str),
         "compiler inventory source-pair identity missing")
    interface = payload.get("required_small_sort")
    identities = payload.get("impl_small_sort_identities")
    need(isinstance(interface, Mapping) and isinstance(identities, (tuple, list)) and
         len(identities) == 2,
         "complete compiler required/impl small_sort identities missing")
    need(isinstance(baseline, Mapping) and
         baseline.get("schema") == "a1-small-sort-native-baseline-v1" and
         baseline.get("provenance") == "r-only-native-translation" and
         baseline.get("source_pair_id") == case["source_pair_id"] and
         baseline.get("actual_source_pair_sha256") == actual_source_pair_sha256 and
         baseline.get("compiler_interface_digest") == interface.get("interface_digest") and
         baseline.get("proof_credit") is False and baseline.get("conformance_credit") is False,
         "independent R-only native baseline missing or bound to another source/interface")
    receipt = baseline.get("reference_receipt")
    need(isinstance(receipt, Mapping) and
         baseline.get("reference_receipt_sha256") == _receipt_sha256(receipt),
         "R-only capture receipt changed after baseline extraction")
    _guard_r_only_reference_receipt(
        receipt, baseline.get("ast_sha256"), case["source_pair_id"])
    need(receipt.get("actual_source_pair_sha256") == actual_source_pair_sha256 and
         receipt.get("ast_sha256") == baseline.get("ast_sha256") and
         hashlib.sha256(ast.encode("utf-8")).hexdigest() != baseline.get("ast_sha256"),
         "P1 baseline is candidate-self or lacks an independent R-only invocation identity")
    baseline_native = baseline.get("normalized_native")
    baseline_header = baseline.get("normalized_header")
    baseline_hashes = baseline.get("native_sha256")
    baseline_impls = baseline.get("normalized_impls")
    need(isinstance(baseline_header, (tuple, list)) and
         isinstance(baseline_native, Mapping) and set(baseline_native) ==
         {"pre", "returning", "unwind"} and isinstance(baseline_hashes, Mapping) and
         all(baseline_hashes.get(key) == digest(baseline_native[key])
             for key in ("pre", "returning", "unwind")) and
         isinstance(baseline_impls, Mapping) and set(baseline_impls) ==
         {"default16", "freeze32"},
         "R-only baseline common/original-impl native receipts are incomplete")
    for impl_name, original in baseline_impls.items():
        original_header = original.get("normalized_header")
        original_native = original.get("normalized_native")
        need(isinstance(original, Mapping) and
             isinstance(original_native, Mapping) and
             set(original_native) == {"pre", "returning", "unwind"} and
             isinstance(original.get("native_sha256"), Mapping) and
             all(original["native_sha256"].get(key) == digest(original_native[key])
                 for key in ("pre", "returning", "unwind")) and
             _small_sort_native_for_common_comparison(
                 original_native, _small_sort_scratch_name_from_header(original_header)) ==
             _small_sort_native_for_common_comparison(
                 baseline_native, _small_sort_scratch_name_from_header(tuple(baseline_header))) and
             _small_sort_ast_header_for_common_comparison(original_header) ==
             _small_sort_ast_header_for_common_comparison(tuple(baseline_header)),
             "R-only original impl baseline is incomplete or differs from required common: " +
             impl_name)

    fs = functions(ast)
    common_name = interface.get("required_def_id")
    common = [row for row in fs if row["name"] == common_name]
    need(len(common) == 1 and common[0]["kind"] == "prototype",
         "AST must bind the unique required small_sort prototype and Self/F order")
    alpha_common = _small_sort_alpha(common[0], self_name="Self")
    common_signature = _small_sort_ast_signature(common[0], "Self", alpha_common)
    required_signature = tuple(_compiler_small_sort_type_to_ast(x)
                               for x in interface.get("inputs", ()))
    need(interface.get("ast_type_param_names") == ("Self", "F") and
         common_signature == required_signature,
         "required AST signature differs from compiler-derived Self/F/scoped inputs")
    need(_small_sort_ast_return(common[0]) == "unit" and
         interface.get("output") == ("tuple", ()),
         "required AST return differs from compiler-derived unit output")
    _small_sort_ast_bounds(common[0])
    need(_source_line(common[0]["fields"][0]) == interface["source_span"][0][1],
         "required small_sort AST source location differs from compiler nameSpan")
    common_native = _small_sort_native(common[0], alpha_common)
    need(_small_sort_ast_header(common[0], alpha_common) == tuple(baseline_header),
         "candidate common full typed/native header differs from independent R-only baseline")
    need(common_native == baseline_native,
         "candidate common small_sort native contract differs from independent R-only baseline")

    # The native baseline AST carries the unchanged method's full header. Impl
    # Self is compiler T; F remains the method parameter. Lifetimes are compared
    # by their positional roles after the compiler interface has established
    # distinct signature and HRTB binders.
    checked = {}
    aliases = set()
    for row in identities:
        need(isinstance(row, Mapping) and row.get("impl") in ("default16", "freeze32"),
             "compiler small_sort impl identity row")
        original = baseline_impls.get(row["impl"])
        need(isinstance(original, Mapping) and
             original.get("item_def_id") == row.get("item_def_id") and
             original.get("compiler_impl_id") == row.get("impl_def_index") and
             original.get("compiler_item_id") == row.get("item_def_index") and
             original.get("compiler_signature_digest") == row.get("compiler_signature_digest") and
             _compiler_source_span(original.get("source_body_span")) ==
             _compiler_source_span(row.get("source_body_span")),
             "R-only original impl baseline is bound to another compiler item: " + row["impl"])
        alias = row.get("alias")
        need(isinstance(alias, str) and alias not in aliases and
             re.fullmatch(r"__a1_impl_[1-9][0-9]*_item_[1-9][0-9]*_small_sort", alias),
             "compiler-derived numeric small_sort impl alias")
        aliases.add(alias)
        found = [fn for fn in fs if fn["name"] == alias]
        body = [fn for fn in found if fn["kind"] == "definition"]
        need(len(found) == len(body) == 1,
             "one compiler-bound actual small_sort impl definition: " + row["impl"])
        fn = body[0]
        alpha_impl = _small_sort_alpha(fn, self_name="T")
        ast_signature = _small_sort_ast_signature(fn, "T", alpha_impl)
        compiler_signature = row.get("compiler_signature")
        need(isinstance(compiler_signature, Mapping) and
             compiler_signature.get("digest") == row.get("compiler_signature_digest"),
             "numeric impl Body compiler signature identity missing")
        expected_signature = tuple(_compiler_small_sort_type_to_ast(x)
                                   for x in compiler_signature.get("inputs", ()))
        need(ast_signature == expected_signature,
             "actual impl AST parameter types differ from its numeric compiler Body signature")
        compiler_regions = compiler_signature.get("input_regions")
        ast_regions = _small_sort_generic_names(fn)[2:]
        need(compiler_regions == ("@input_0", "@input_1", "@input_2") and
             tuple(alpha_impl.get(region) for region in ast_regions) == compiler_regions and
             original.get("compiler_positional_region_map") ==
             tuple(zip(ast_regions, compiler_regions)),
             "actual impl AST lifetime alpha map differs from compiler positional input-region map")
        need(_small_sort_ast_return(fn) == "unit",
             "actual impl AST return type differs from compiler unit output")
        _small_sort_ast_bounds(fn)
        need(_source_line(fn["fields"][0]) == row.get("ast_body_line") and
             _source_span(fn["fields"][0]) ==
             _compiler_source_span_as_ast(row.get("source_body_span")),
             "small_sort implementation AST span differs from compiler Body.span")
        native = _small_sort_native(fn, alpha_impl)
        need(native == original["normalized_native"],
             "impl small_sort native pre/returning/unwind differs from its original R-only body: " + row["impl"])
        need(_small_sort_native_for_common_comparison(
                 native, _small_sort_ast_scratch_name(fn)) ==
             _small_sort_native_for_common_comparison(
                 baseline_native, _small_sort_scratch_name_from_header(tuple(baseline_header))),
             "impl small_sort native contract differs from common under parameter binding alpha map: " +
             row["impl"])
        impl_header = _small_sort_ast_header(fn, alpha_impl)
        need(impl_header == original["normalized_header"],
             "impl small_sort full typed/native header differs from its original R-only body: " +
             row["impl"])
        need(_small_sort_ast_header_for_common_comparison(
                 _small_sort_ast_header(common[0], alpha_common)) ==
             _small_sort_ast_header_for_common_comparison(impl_header),
             "common and impl small_sort AST typed headers differ under positional alpha map")
        need(ast_signature == common_signature,
             "common and impl AST parameter signature differs under compiler positional map")
        checked[row["impl"]] = {
            "alias": alias, "compiler_impl_id": str(row["impl_def_index"]),
            "compiler_item_id": str(row["item_def_index"]),
            "compiler_signature_digest": compiler_signature["digest"],
            "positional_alpha_map": tuple(sorted(alpha_impl.items())),
            "compiler_positional_region_map": tuple(zip(ast_regions, compiler_regions)),
            "native_sha256": {key: digest(common_native[key]) for key in common_native},
            "actual_definition_bound_to_compiler_item": True,
            "native_matches_r_only_original_impl": True,
        }
    need({row.get("impl") for row in identities} == {"default16", "freeze32"},
         "both actual small_sort implementations are required")
    return {"schema": "a1-small-sort-interface-observation-v1",
            "classification": "INTERFACE_STRUCTURE_ONLY_UNRUN_PROOF",
            "source_pair_id": case["source_pair_id"],
            "actual_source_pair_sha256": actual_source_pair_sha256,
            "compiler_interface_digest": interface["interface_digest"],
            "normalized_native": common_native,
            "native_sha256": {key: digest(common_native[key]) for key in common_native},
            "impls": checked, "structural_pass": True,
            "compiler_clauses_source_bound": True,
            "ast_clause_representation": "none; compiler-required interface is separately validated",
            "compiler_clause_digest": digest(interface["clauses"]),
            "positional_alpha_roles": interface["alpha_roles"],
            "body_count": 0, "proof_credit": False,
            "conformance_credit": False, "native_contract_credit": False}


def _calls(body: Any) -> list[dict[str, Any]]:
    result = []
    def visit(value: Any) -> None:
        if not isinstance(value, tuple) or len(value) != 2:
            raise AstGateError("malformed caller AST node")
        kind, children = value
        if kind == "CallExpr":
            loc, callee, targs, indices, args, binding = node(value, "CallExpr", 6)
            result.append({"callee": atom(callee), "type_args": items(targs),
                           "predicate_indices": items(indices),
                           "args": items(args), "binding": binding,
                           "location": loc})
        if isinstance(children, tuple):
            for child in children:
                visit(child)
    visit(body)
    return result


def caller_calls(ast: str, *, owner: str, expected: tuple[str, ...],
                 source_line: int,
                 call_lines: Mapping[str, int],
                 expected_arguments: Mapping[str, tuple[str, ...]]) -> dict[str, Any]:
    """Bound the final call AST; compiler MIR binding remains independent."""
    need(owner in {"a1_guard_observer", "quicksort"}, "certified caller owner")
    need(expected in ((COMMON,), (COMMON, SMALL_SORT)), "supported call inventory")
    fs = functions(ast)
    owners = [row for row in fs if row["name"] == owner]
    need(len(owners) == 1 and owners[0]["kind"] == "definition" and
         _source_line(owners[0]["fields"][0]) == source_line,
         "one exact source caller body")
    need(set(call_lines) == set(expected) and
         all(isinstance(line, int) and line > source_line
             for line in call_lines.values()),
         "exact source-certified trait call lines")
    need(set(expected_arguments) == set(expected),
         "each source call needs compiler-bound AST operand inventory")
    body = owners[0]["fields"][10]
    all_calls = _calls(body)
    need(not any(call["callee"].startswith("__a1_impl_") or
                 call["callee"].startswith("sort4_selected_branch_")
                 for call in all_calls), "implementation alias in caller body")
    calls = [call for call in all_calls if
             "small_sort" in call["callee"]]
    need(tuple(call["callee"] for call in calls) == expected,
         "original common trait call inventory/order")
    for call in calls:
        need(call["callee"] in (COMMON, SMALL_SORT) and
             _source_line(call["location"]) == call_lines[call["callee"]] and
             len(call["type_args"]) == (1 if call["callee"] == COMMON else 5) and
             len(call["args"]) == (0 if call["callee"] == COMMON else 3) and
             len(call["predicate_indices"]) == 0 and
             call["binding"] == ("atom", "Static"),
             "common call type/value arity or binding differs")
        def type_name(value: Any, expected_name: str) -> None:
            _, package, name = node(value, "IdentTypeExpr", 3)
            need(package == ("atom", "None"), "call type package")
            atom(name, expected_name)
        type_name(call["type_args"][0], "T")
        if call["callee"] == SMALL_SORT:
            type_name(call["type_args"][1], "F")
        bound_arguments = expected_arguments[call["callee"]]
        need(isinstance(bound_arguments, tuple) and
             len(bound_arguments) == len(call["args"]),
             "compiler-bound AST argument count")
        for argument, bound_name in zip(call["args"], bound_arguments):
            expression, = node(argument, "LitPat", 1)
            _, argument_name = node(expression, "Var", 2)
            atom(argument_name, bound_name)
    return {"classification": "CALL_AST_STRUCTURE_ONLY",
            "owner": owner, "source_line": source_line,
            "calls": [{"callee": call["callee"],
                       "ast_call_span": call["location"][1],
                       "ast_call_span_bounds": _source_span(call["location"]),
                       "type_args_sha256": digest(call["type_args"]),
                       "argument_count": len(call["args"])} for call in calls],
            "compiler_mir_binding_checked": False,
            "proof_credit": False}
