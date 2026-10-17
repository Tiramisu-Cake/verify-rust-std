"""Fail-closed bounded Cap'n Proto text subset parser and synthetic controls.

This module operates only on caller-supplied decoded text. Mutation results are
synthetic test inputs and carry no compiler, translator, refinement, or proof
provenance. The accepted grammar is records, lists, quoted strings, bare enum/
boolean/void atoms, and decimal or hexadecimal integers; unsupported text is
rejected. No complete decoded VfMir stream has been used to claim compatibility.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Iterable, Union


class ParseError(ValueError):
    pass


class ShapeError(ValueError):
    pass


@dataclass(frozen=True)
class Text:
    value: str


@dataclass(frozen=True)
class Atom:
    value: str


@dataclass(frozen=True)
class Number:
    value: str


@dataclass(frozen=True)
class Record:
    fields: tuple[tuple[str, "Value"], ...]


@dataclass(frozen=True)
class ListValue:
    values: tuple["Value", ...]


Value = Union[Text, Atom, Number, Record, ListValue]

_TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_./:$-]*|[+-]?(?:0[xX][0-9A-Fa-f]+|[0-9]+)")
MAX_SOURCE_CHARS = 4 * 1024 * 1024
MAX_NODES = 300_000
MAX_DEPTH = 64
MAX_TOP_LEVEL_RECORDS = 10_000


class _Parser:
    def __init__(self, source: str):
        if len(source) > MAX_SOURCE_CHARS:
            raise ParseError("Cap'n Proto text exceeds size limit")
        self.source = source
        self.i = 0
        self.depth = 0
        self.nodes = 0

    def _space(self) -> None:
        while self.i < len(self.source) and self.source[self.i].isspace():
            self.i += 1

    def _peek(self) -> str:
        self._space()
        return self.source[self.i:self.i + 1]

    def _take(self, expected: str) -> None:
        self._space()
        if not self.source.startswith(expected, self.i):
            raise ParseError(f"expected {expected!r} at byte {self.i}")
        self.i += len(expected)

    def _word(self) -> str:
        self._space()
        match = _TOKEN.match(self.source, self.i)
        if match is None:
            raise ParseError(f"expected field name or scalar at byte {self.i}")
        self.i = match.end()
        return match.group(0)

    def _string(self) -> Text:
        start = self.i
        self._take('"')
        escaped = False
        while self.i < len(self.source):
            ch = self.source[self.i]
            self.i += 1
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                raw = self.source[start:self.i]
                try:
                    value = json.loads(raw)
                except (ValueError, json.JSONDecodeError) as exc:
                    raise ParseError(f"invalid quoted string at byte {start}") from exc
                if not isinstance(value, str):
                    raise ParseError("quoted scalar did not decode to text")
                return Text(value)
        raise ParseError(f"unterminated quoted string at byte {start}")

    def value(self) -> Value:
        self.nodes += 1
        if self.nodes > MAX_NODES:
            raise ParseError("Cap'n Proto text exceeds node limit")
        ch = self._peek()
        if ch == "(":
            return self.record()
        if ch == "[":
            return self.list_value()
        if ch == '"':
            return self._string()
        word = self._word()
        if re.fullmatch(r"[+-]?(?:0[xX][0-9A-Fa-f]+|[0-9]+)", word):
            return Number(word)
        return Atom(word)

    def record(self) -> Record:
        self._enter()
        self._take("(")
        fields: list[tuple[str, Value]] = []
        while self._peek() != ")":
            if not self._peek():
                raise ParseError("unterminated record")
            key = self._word()
            self._take("=")
            fields.append((key, self.value()))
            ch = self._peek()
            if ch == ",":
                self._take(",")
            elif ch not in ("", ")"):
                raise ParseError(f"expected comma or record close at byte {self.i}")
        self._take(")")
        result = Record(tuple(fields))
        self.depth -= 1
        return result

    def list_value(self) -> ListValue:
        self._enter()
        self._take("[")
        values: list[Value] = []
        while self._peek() != "]":
            if not self._peek():
                raise ParseError("unterminated list")
            values.append(self.value())
            ch = self._peek()
            if ch == ",":
                self._take(",")
            elif ch not in ("", "]"):
                raise ParseError(f"expected comma or list close at byte {self.i}")
        self._take("]")
        result = ListValue(tuple(values))
        self.depth -= 1
        return result

    def _enter(self) -> None:
        if self.depth >= MAX_DEPTH:
            raise ParseError("Cap'n Proto text exceeds nesting limit")
        self.depth += 1

    def all_records(self) -> tuple[Record, ...]:
        rows: list[Record] = []
        while self._peek():
            value = self.value()
            if not isinstance(value, Record):
                raise ParseError("top-level value is not a record")
            rows.append(value)
            if len(rows) > MAX_TOP_LEVEL_RECORDS:
                raise ParseError("Cap'n Proto text exceeds top-level record limit")
        if not rows:
            raise ParseError("empty top-level record sequence")
        return tuple(rows)


def parse_records(source: str) -> tuple[Record, ...]:
    """Parse all top-level structs in the bounded grammar without data loss."""
    if not isinstance(source, str):
        raise TypeError("Cap'n Proto text must be str")
    return _Parser(source).all_records()


def render_value(value: Value) -> str:
    if isinstance(value, Text):
        return json.dumps(value.value, ensure_ascii=False)
    if isinstance(value, Atom):
        return value.value
    if isinstance(value, Number):
        return value.value
    if isinstance(value, ListValue):
        return "[" + ", ".join(render_value(v) for v in value.values) + "]"
    if isinstance(value, Record):
        return "(" + ", ".join(f"{k} = {render_value(v)}" for k, v in value.fields) + ")"
    raise TypeError(f"unsupported parsed value {type(value).__name__}")


def render_records(records: Iterable[Record]) -> str:
    rows = tuple(records)
    if not rows:
        raise ValueError("cannot render empty record sequence")
    return "\n".join(render_value(row) for row in rows) + "\n"


def _one(record: Record, key: str, *, required: bool = True) -> Value | None:
    found = [value for name, value in record.fields if name == key]
    if len(found) > 1:
        raise ShapeError(f"duplicate field {key!r}")
    if not found:
        if required:
            raise ShapeError(f"missing field {key!r}")
        return None
    return found[0]


def _text(record: Record, key: str) -> str:
    value = _one(record, key)
    if not isinstance(value, Text):
        raise ShapeError(f"field {key!r} must be a quoted string")
    return value.value


def _indlist_entries(value: Value, field: str) -> tuple[tuple[Record, tuple[int, ...]], ...]:
    """Decode schema IndList(T) cons(h,t)/nil while retaining direct paths."""
    entries = []
    current = value
    prefix: tuple[int, ...] = ()
    while True:
        if not isinstance(current, Record):
            raise ShapeError(f"IndList field {field!r} must be a union record")
        nil = _one(current, "nil", required=False)
        cons = _one(current, "cons", required=False)
        if (nil is None) == (cons is None):
            raise ShapeError(f"IndList field {field!r} must have exactly one union arm")
        if nil is not None:
            if not isinstance(nil, Atom) or nil.value != "void":
                raise ShapeError(f"IndList field {field!r} nil arm must be void")
            return tuple(entries)
        if not isinstance(cons, Record):
            raise ShapeError(f"IndList field {field!r} cons arm must be a record")
        h = _one(cons, "h")
        t = _one(cons, "t")
        if not isinstance(h, Record):
            raise ShapeError(f"IndList field {field!r} head must be a record")
        cons_field = next(i for i, (key, _) in enumerate(current.fields) if key == "cons")
        h_field = next(i for i, (key, _) in enumerate(cons.fields) if key == "h")
        t_field = next(i for i, (key, _) in enumerate(cons.fields) if key == "t")
        entries.append((h, prefix + (cons_field, -1, h_field, -1)))
        prefix = prefix + (cons_field, -1, t_field, -1)
        current = t
        if len(entries) > MAX_NODES:
            raise ShapeError(f"IndList field {field!r} exceeds node limit")


def _records(value: Value | None, field: str) -> tuple[Record, ...]:
    if isinstance(value, ListValue) and all(isinstance(x, Record) for x in value.values):
        return tuple(value.values)  # type: ignore[return-value]
    if isinstance(value, Record):
        return tuple(row for row, _ in _indlist_entries(value, field))
    raise ShapeError(f"field {field!r} must be a record list or IndList")


def _render_indlist(rows: Iterable[Record]) -> Record:
    result = Record((("nil", Atom("void")),))
    for row in reversed(tuple(rows)):
        result = Record((("cons", Record((("h", row), ("t", result)))),))
    return result


def _map_value(value: Value, fn) -> Value:
    if isinstance(value, Text):
        return fn(value)
    if isinstance(value, Record):
        return Record(tuple((k, _map_value(v, fn)) for k, v in value.fields))
    if isinstance(value, ListValue):
        return ListValue(tuple(_map_value(v, fn) for v in value.values))
    return value


def _replace_field(record: Record, key: str, replacement: Value | None) -> Record:
    count = sum(name == key for name, _ in record.fields)
    if count != 1:
        raise ShapeError(f"expected exactly one {key!r} field")
    fields = tuple((name, replacement if name == key else value)
                   for name, value in record.fields if replacement is not None or name != key)
    return Record(fields)


def _update_record_at(root: Record, path: tuple[int, ...], replacement: Record) -> Record:
    if not path:
        return replacement
    field_index, child_index = path[0], path[1]
    fields = list(root.fields)
    key, value = fields[field_index]
    if child_index == -1:
        if not isinstance(value, Record):
            raise ShapeError("internal path no longer points through a direct record")
        fields[field_index] = (key, _update_record_at(value, path[2:], replacement))
        return Record(tuple(fields))
    if not isinstance(value, ListValue):
        raise ShapeError("internal path no longer points through a list")
    rows = list(value.values)
    child = rows[child_index]
    if not isinstance(child, Record):
        raise ShapeError("internal path no longer points to a record")
    rows[child_index] = _update_record_at(child, path[2:], replacement)
    fields[field_index] = (key, ListValue(tuple(rows)))
    return Record(tuple(fields))


def _walk(value: Value, path: tuple[int, ...] = ()):
    if isinstance(value, Record):
        yield value, path
        for fi, (key, child) in enumerate(value.fields):
            if isinstance(child, ListValue):
                for ci, row in enumerate(child.values):
                    if isinstance(row, Record):
                        yield from _walk(row, path + (fi, ci))
            elif isinstance(child, Record):
                # Direct record fields use a sentinel child slot in paths.
                yield from _walk(child, path + (fi, -1))
    elif isinstance(value, ListValue):
        for ci, child in enumerate(value.values):
            yield from _walk(child, path + (-1, ci)) if isinstance(child, Record) else ()


def _find_target(records: tuple[Record, ...], root_trait: str, target_fn: str):
    if root_trait != "StableSmallSortTypeImpl" or target_fn != "small_sort":
        raise ShapeError("mutation target is pinned to root StableSmallSortTypeImpl::small_sort")
    roots = []
    for ri, record in enumerate(records):
        for node, path in _walk(record):
            if _one(node, "requiredFns", required=False) is not None:
                nm = _one(node, "name", required=False)
                if isinstance(nm, Text) and nm.value == root_trait:
                    roots.append((ri, node, path))
    if len(roots) != 1:
        raise ShapeError(f"expected one root trait record, found {len(roots)}")
    ri, root, root_path = roots[0]
    required_value = _one(root, "requiredFns")
    required = _records(required_value, "requiredFns")
    if not isinstance(required_value, Record):
        raise ShapeError("Trait.requiredFns must use the schema IndList representation")
    required_paths = _indlist_entries(required_value, "requiredFns")
    named = [(i, row) for i, row in enumerate(required)
             if _text(row, "name") == target_fn]
    if len(named) != 1:
        raise ShapeError(f"expected exactly one required method {target_fn!r}")
    fi, method = named[0]
    scoped = _one(method, "scopedRepresentation")
    if not isinstance(scoped, Atom) or scoped.value != "true":
        raise ShapeError("target required method lacks scopedRepresentation = true")
    _validate_method_shape(method, root_trait)
    if len(root_path) % 2 != 0:
        raise ShapeError("root trait must be addressable through record lists")
    # Root path terminates at the trait record. Add the requiredFns list edge.
    required_field = next(i for i, (key, _) in enumerate(root.fields) if key == "requiredFns")
    method_path = root_path + (required_field, -1) + required_paths[fi][1]
    return ri, root, root_path, required, fi, method, method_path


def _validate_method_shape(method: Record, root_trait: str) -> None:
    for field in ("defId", "parentDefId"):
        if not isinstance(_one(method, field), Text):
            raise ShapeError(f"required-item {field} must be quoted text")
    for field in ("defIndex", "parentDefIndex"):
        identity = _one(method, field)
        if not isinstance(identity, Number) or int(identity.value, 16) == 0:
            raise ShapeError(f"required-item {field} must be numeric")
    if _text(method, "parentDefId") != root_trait:
        raise ShapeError("required-item parentDefId does not match selected root trait")
    for field in ("hirGenerics", "output"):
        if not isinstance(_one(method, field), Record):
            raise ShapeError(f"required-item {field} must be a record")
    if not isinstance(_one(method, "inputs"), ListValue):
        raise ShapeError("required-item inputs must be a list")
    for field in ("clauses", "parentClauses", "generics", "typeParams", "scopedRegions"):
        value = _one(method, field)
        if not isinstance(value, ListValue) or any(not isinstance(row, Record) for row in value.values):
            raise ShapeError(f"required-item {field} must be a record list")
    for row in _records(_one(method, "typeParams"), "typeParams"):
        if not isinstance(_one(row, "alias"), Text) or not isinstance(_one(row, "name"), Text):
            raise ShapeError("typeParams alias/name must be quoted text")
        if not isinstance(_one(row, "index"), Number) or not isinstance(_one(row, "defIndex"), Number):
            raise ShapeError("typeParams index/defIndex must be numeric")
    for row in _records(_one(method, "generics"), "generics"):
        if not isinstance(_one(row, "name"), Text) or not isinstance(_one(row, "index"), Number) or \
                not isinstance(_one(row, "defIndex"), Number):
            raise ShapeError("generics name/index/defIndex have invalid types")
    _alias_rows(method)


def _replace_at_path(records: tuple[Record, ...], ri: int, path: tuple[int, ...], replacement: Record) -> tuple[Record, ...]:
    rows = list(records)
    rows[ri] = _update_record_at(rows[ri], path, replacement)
    return tuple(rows)


def _alias_rows(method: Record) -> tuple[tuple[str, str, int, int], ...]:
    raw = _records(_one(method, "scopedRegions"), "scopedRegions")
    rows = []
    seen = set()
    for row in raw:
        alias = _text(row, "alias")
        scope = _text(row, "scope")
        depth = _one(row, "depth")
        index = _one(row, "index")
        kind = _one(row, "kind")
        elided = _one(row, "elidedRole")
        if not isinstance(depth, Number) or not isinstance(index, Number):
            raise ShapeError("scoped region depth/index must be numeric atoms")
        if not isinstance(kind, Text) or kind.value not in ("anon", "named", "printing"):
            raise ShapeError("scoped region kind must be a recognized quoted tag")
        if not isinstance(elided, Atom) or elided.value not in ("true", "false"):
            raise ShapeError("scoped region elidedRole must be boolean atom")
        if alias in seen:
            raise ShapeError("duplicate scoped region alias")
        seen.add(alias)
        rows.append((alias, scope, int(depth.value, 0), int(index.value, 0)))
    return tuple(rows)


def _set_list(record: Record, field: str, rows: Iterable[Value]) -> Record:
    return _replace_field(record, field, ListValue(tuple(rows)))


def _set_text_aliases(value: Value, aliases: dict[str, str]) -> Value:
    return _map_value(value, lambda item: Text(aliases[item.value])
                      if item.value in aliases else item)


def _alpha_rename_method(method: Record, aliases: dict[str, str]) -> Record:
    reference_fields = {"inputs", "output", "clauses", "parentClauses",
                        "hirGenerics", "generics", "typeParams", "scopedRegions",
                        "lifetimeParams", "contract"}
    return Record(tuple((key, _set_text_aliases(value, aliases)
                         if key in reference_fields else value)
                        for key, value in method.fields))


def _update_method_field(method: Record, field: str, transform) -> Record:
    value = _one(method, field)
    if value is None:
        raise ShapeError(f"missing {field}")
    return _replace_field(method, field, transform(value))


def _region_refs(value: Value, aliases: set[str]) -> list[str]:
    found = []
    def visit(v: Value) -> None:
        if isinstance(v, Text) and v.value in aliases:
            found.append(v.value)
        elif isinstance(v, Record):
            for _, child in v.fields:
                visit(child)
        elif isinstance(v, ListValue):
            for child in v.values:
                visit(child)
    visit(value)
    return found


def _replace_text(value: Value, old: str, new: str) -> Value:
    return _map_value(value, lambda item: Text(new) if item.value == old else item)


def _clause_kind(row: Record) -> tuple[str, str] | None:
    """Find the exact active union arm and its compiler trait/projection ID."""
    arms = [(key, value) for key, value in row.fields
            if key in ("trait", "projection")]
    if len(arms) > 1:
        raise ShapeError("ambiguous tagged clause identity")
    if not arms:
        return None
    arm, value = arms[0]
    if not isinstance(value, Record):
        raise ShapeError("clause union arm must be a record")
    identity = value if arm == "trait" else _one(value, "projectionTerm")
    if not isinstance(identity, Record):
        raise ShapeError("clause identity record is missing")
    def_id = _one(identity, "defId")
    if not isinstance(def_id, Text):
        raise ShapeError("clause defId must be quoted text")
    return arm, def_id.value


def _change_clause(rows: tuple[Record, ...], target: str) -> tuple[Record, ...]:
    matches = []
    for i, row in enumerate(rows):
        ident = _clause_kind(row)
        if ident and ident[1].endswith(target):
            matches.append((i, row, ident))
    if len(matches) != 1:
        raise ShapeError(f"expected one {target} clause, found {len(matches)}")
    i, row, _ = matches[0]
    changed = _map_value(row, lambda item: Text(item.value + "::A1SyntheticChanged")
                         if item.value.endswith(target) else item)
    if not isinstance(changed, Record):
        raise ShapeError("internal clause mutation failed")
    out = list(rows)
    out[i] = changed
    return tuple(out)


def _remove_clause_and_reindex(method: Record, clauses: tuple[Record, ...], target: str):
    matches = [(i, row) for i, row in enumerate(clauses)
               if (identity := _clause_kind(row)) and identity[1].endswith(target)]
    if len(matches) != 1:
        raise ShapeError(f"expected exactly one {target} clause")
    removed_index, removed = matches[0]
    old_scope = f"clause_{removed_index}"
    scoped = _records(_one(method, "scopedRegions"), "scopedRegions")
    owned = [row for row in scoped if _text(row, "scope") == old_scope]
    if not owned:
        raise ShapeError(f"removed {target} clause has no scoped binder rows")
    removed_aliases = {_text(row, "alias") for row in owned}
    _need_alias_refs = _region_refs(removed, removed_aliases)
    if not _need_alias_refs:
        raise ShapeError(f"removed {target} clause does not reference its scoped binders")
    new_scoped = []
    for row in scoped:
        scope = _text(row, "scope")
        if scope == old_scope:
            continue
        match = re.fullmatch(r"clause_([0-9]+)", scope)
        if match and int(match.group(1)) > removed_index:
            row = _replace_field(row, "scope", Text(f"clause_{int(match.group(1)) - 1}"))
        new_scoped.append(row)
    new_clauses = tuple(row for i, row in enumerate(clauses) if i != removed_index)
    updated = _set_list(method, "clauses", new_clauses)
    updated = _set_list(updated, "scopedRegions", new_scoped)
    return updated, tuple(sorted(removed_aliases)), len(owned)


def mutate_required_fn(decoded_text: str, mutation: str, *,
                       root_trait: str = "StableSmallSortTypeImpl",
                       target_fn: str = "small_sort",
                       impl_def_index: int | None = None) -> tuple[str, dict]:
    """Apply one exact-shape mutation to root required small_sort only.

    Returned metadata explicitly labels all outputs synthetic and without
    compiler/exporter/refinement/proof provenance.
    """
    records = parse_records(decoded_text)
    ri, root, root_path, required, fi, method, method_path = _find_target(
        records, root_trait, target_fn)
    original = render_value(method)
    aliases = _alias_rows(method)
    scoped_aliases = {row[0] for row in aliases}
    if not scoped_aliases:
        raise ShapeError("target method has no scoped region rows")
    new_method = method
    mutation_extra: dict = {}

    if mutation == "binder_collapse":
        groups: dict[tuple[str, int], list[tuple[str, int]]] = {}
        for alias, scope, depth, index in aliases:
            groups.setdefault((scope, depth), []).append((alias, index))
        pair = next((rows for rows in groups.values()
                     if len(rows) >= 2 and len({index for _, index in rows}) >= 2), None)
        if pair is None:
            raise ShapeError("no scoped binder indices available to collapse")
        first, second = pair[0], pair[1]
        scoped = _records(_one(method, "scopedRegions"), "scopedRegions")
        out = list(scoped)
        found = False
        for i, row in enumerate(out):
            if _text(row, "alias") == second[0]:
                out[i] = _replace_field(row, "index", Number(str(first[1])))
                found = True
                break
        if not found:
            raise ShapeError("binder row disappeared")
        new_method = _set_list(method, "scopedRegions", out)
    elif mutation == "alpha_valid":
        # Translator scoped-region aliases are wire lifetime names and must
        # retain the leading apostrophe expected by the Rust lifetime syntax.
        mapping = {alias: f"'__a1_alpha_{i}" for i, (alias, _, _, _) in enumerate(aliases)}
        if len(set(mapping.values())) != len(mapping) or scoped_aliases.intersection(mapping.values()):
            raise ShapeError("alpha alias mapping is not bijective")
        new_method = _alpha_rename_method(method, mapping)
        inverse = {new: old for old, new in mapping.items()}
        mutation_extra = {
            "alpha_alias_bijection": mapping,
            "semantic_metadata_unchanged": _alpha_rename_method(new_method, inverse) == method,
        }
        if not mutation_extra["semantic_metadata_unchanged"]:
            raise ShapeError("alpha rename changed non-alias semantic metadata")
    elif mutation == "free_region_input":
        inputs = _one(method, "inputs")
        refs = _region_refs(inputs, scoped_aliases) if inputs is not None else []
        if not refs:
            raise ShapeError("no bound region reference in target inputs")
        new_method = _update_method_field(method, "inputs",
                                          lambda value: _replace_text(value, refs[0], "__a1_free_region"))
    elif mutation == "input_region_swap":
        inputs = _one(method, "inputs")
        refs = _region_refs(inputs, scoped_aliases) if inputs is not None else []
        distinct = []
        for ref in refs:
            if ref not in distinct:
                distinct.append(ref)
        if len(distinct) < 2:
            raise ShapeError("two distinct bound input regions are required")
        left, right = distinct[:2]
        value = _one(method, "inputs")
        assert value is not None
        def swap(v: Value) -> Value:
            if isinstance(v, Text):
                return Text(right if v.value == left else left if v.value == right else v.value)
            if isinstance(v, Record):
                return Record(tuple((k, swap(x)) for k, x in v.fields))
            if isinstance(v, ListValue):
                return ListValue(tuple(swap(x) for x in v.values))
            return v
        new_method = _update_method_field(method, "inputs", swap)
    elif mutation == "no_F":
        tparams = _records(_one(method, "typeParams"), "typeParams")
        if not any(_text(row, "name") == "F" for row in tparams):
            raise ShapeError("target method has no F type parameter to remove")
        generics = _records(_one(method, "generics"), "generics")
        hir = _one(method, "hirGenerics")
        if not isinstance(hir, Record):
            raise ShapeError("target hirGenerics must be a record")
        hir_params = _records(_one(hir, "params"), "hirGenerics.params")
        generic_rows = [row for row in generics if _text(row, "name") == "F"]
        hir_rows = [row for row in hir_params if _text(row, "name") == "F"]
        if len(generic_rows) != 1 or len(hir_rows) != 1:
            raise ShapeError("expected exactly one compiler and HIR generic F declaration")
        changed_hir = _replace_field(hir, "params", ListValue(
            tuple(row for row in hir_params if row is not hir_rows[0])))
        new_method = _replace_field(method, "generics", ListValue(
            tuple(row for row in generics if row is not generic_rows[0])))
        new_method = _replace_field(new_method, "hirGenerics", changed_hir)
        updated = _replace_at_path(records, ri, method_path, new_method)
        return render_records(updated), _metadata(
            mutation, original, render_value(new_method),
            extra={"removed_generic": "F", "required_method_retained": True,
                   "typeParams_and_uses_retained": True})
    elif mutation in ("remove_fnmut", "remove_output", "change_fnmut", "change_output"):
        clauses = _records(_one(method, "clauses"), "clauses")
        suffix = "std::ops::FnMut" if mutation.endswith("fnmut") else "std::ops::FnOnce::Output"
        if mutation.startswith("remove_"):
            new_method, removed_aliases, removed_binder_count = _remove_clause_and_reindex(
                method, clauses, suffix)
            mutation_extra = {"removed_clause_scoped_aliases": removed_aliases,
                              "removed_clause_binder_count": removed_binder_count,
                              "remaining_clause_scope_reindexed": True}
        else:
            new_clauses = _change_clause(clauses, suffix)
            new_method = _set_list(method, "clauses", new_clauses)
    elif mutation == "duplicate_impl_method":
        impl_candidates = []
        for tr, top in enumerate(records):
            for node, path in _walk(top):
                of_trait = _one(node, "ofTrait", required=False)
                items_value = _one(node, "items", required=False)
                if isinstance(of_trait, Text) and of_trait.value.endswith(root_trait) and isinstance(items_value, ListValue):
                    impl_candidates.append((tr, node, path, items_value))
        if len(impl_candidates) != 2:
            raise ShapeError(f"expected both target TraitImpl records, found {len(impl_candidates)}")
        ids = []
        for _, candidate, _, _ in impl_candidates:
            value = _one(candidate, "defIndex")
            if not isinstance(value, Number):
                raise ShapeError("TraitImpl compiler defIndex must be numeric")
            ids.append(int(value.value, 16) if value.value.lower().startswith("0x") else int(value.value))
        if len(set(ids)) != 2:
            raise ShapeError("both TraitImpl records need distinct compiler indices")
        if impl_def_index is None or impl_def_index not in ids:
            raise ShapeError("duplicate mutation requires an explicit inventory impl defIndex")
        tr, impl, impl_path, items_value = impl_candidates[ids.index(impl_def_index)]
        impl_items = _records(items_value, "items")
        methods = [row for row in impl_items if _text(row, "name") == "small_sort"]
        if len(methods) != 1:
            raise ShapeError(f"expected one impl small_sort item, found {len(methods)}")
        updated_impl = _replace_field(impl, "items", ListValue(tuple(impl_items) + (methods[0],)))
        updated = _replace_at_path(records, tr, impl_path, updated_impl)
        return render_records(updated), _metadata(mutation, original, original,
                                                    extra={"duplicate_method_record": "small_sort",
                                                           "selected_impl_def_index": impl_def_index,
                                                           "both_impls_present": True})
    else:
        raise ShapeError(f"unsupported mutation {mutation!r}")

    updated = _replace_at_path(records, ri, method_path, new_method)
    rendered = render_records(updated)
    reparsed = parse_records(rendered)
    _find_target(reparsed, root_trait, target_fn)
    return rendered, _metadata(mutation, original, render_value(new_method),
                               extra={"scoped_region_rows_before": len(aliases),
                                      "semantic_provenance": "synthetic-only",
                                      **mutation_extra})


def _metadata(mutation: str, before: str, after: str | None, *, extra: dict | None = None) -> dict:
    intended = {
        "binder_collapse": "required-item binder scope/index validation",
        "alpha_valid": "valid alpha-invariance control",
        "free_region_input": "required-item input region binding validation",
        "input_region_swap": "required-item distinct input borrow relation",
        "no_F": "required-item HIR/compiler generic scope consistency",
        "remove_fnmut": "required-item FnMut clause validation",
        "remove_output": "required-item FnOnce::Output clause validation",
        "change_fnmut": "required-item FnMut clause identity validation",
        "change_output": "required-item FnOnce::Output clause identity validation",
        "duplicate_impl_method": "source impl item inventory duplicate detection",
    }
    return {"mutation": mutation, "synthetic": True, "provenance": "none",
            "compiler_derived": False, "translator_derived": False,
            "refinement_derived": False, "proof_credit": False,
            "intended_stage": intended[mutation],
            "target_location": "root Trait.requiredFns::small_sort",
            "before_required_fn": before, "after_required_fn": after,
            **(extra or {})}
