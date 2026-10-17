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


class AstGateError(ValueError):
    pass


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise AstGateError(reason)


def digest(value: Any) -> str:
    return hashlib.sha256(repr(value).encode()).hexdigest()


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


def _segments(source: str, ctor: str) -> list[str]:
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
        out.append(source[match.start():end + 1].strip())
    return out


def functions(source: str) -> list[dict[str, Any]]:
    result = []
    for segment in _segments(source, "Func"):
        value = tree(segment)
        fs = node(value, "Func", 13)
        name = atom(fs[4])
        body = fs[10]
        need(body == ("atom", "None") or
             isinstance(body, tuple) and body[0] == "Some" and
             len(node(body, "Some", 1)) == 1 and
             len(node(node(body, "Some", 1)[0], "tuple", 2)) == 2,
             "Func body option")
        result.append({"name": name, "fields": fs, "raw": segment,
                       "kind": "prototype" if body == ("atom", "None")
                       else "definition"})
    need(bool(result), "no Func records in AST")
    return result


def _source_line(location: Any) -> int:
    need(isinstance(location, tuple) and location[0] == "loc",
         "Func source location")
    match = re.search(r"(?:^|/)verified/lib\.rs\(([1-9][0-9]*),", location[1])
    need(match is not None, "Func not bound to verified/lib.rs line")
    return int(match.group(1))


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
                       "type_args_sha256": digest(call["type_args"]),
                       "argument_count": len(call["args"])} for call in calls],
            "compiler_mir_binding_checked": False,
            "proof_credit": False}
