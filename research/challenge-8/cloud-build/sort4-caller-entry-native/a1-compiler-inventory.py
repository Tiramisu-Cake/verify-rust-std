"""Fail-closed A1 compiler inventory observations from decoded VfMir text.

This module records compiler-reported identities and spans only. It does not
establish native contract semantics, verifier acceptance, or proof credit.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
import re
from pathlib import Path
import sys
from types import MappingProxyType
from typing import Any

_PARSER_PATH = Path(__file__).with_name("a1-synthetic-inputs.py")
_spec = importlib.util.spec_from_file_location("a1_synthetic_inputs_inventory", _PARSER_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load bounded A1 Cap'n Proto parser")
_parser = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _parser
_spec.loader.exec_module(_parser)

class InventoryError(ValueError):
    """Input cannot be bound unambiguously to the source certificate."""


def _one(r, key, required=True):
    return _parser._one(r, key, required=required)


def _text(r, key):
    value = _one(r, key)
    if not isinstance(value, _parser.Text):
        raise InventoryError(f"{key} must be quoted text")
    return value.value


def _uint(r, key):
    value = _one(r, key)
    if not isinstance(value, _parser.Number):
        raise InventoryError(f"{key} must be a numeric compiler identity")
    try:
        number = int(value.value, 0)
    except ValueError as exc:
        raise InventoryError(f"invalid numeric identity {key}") from exc
    if number <= 0:
        raise InventoryError(f"{key} must be nonzero")
    return number


def _index(r, key):
    value = _one(r, key)
    if not isinstance(value, _parser.Number):
        raise InventoryError(f"{key} must be numeric")
    try:
        number = int(value.value, 0)
    except ValueError as exc:
        raise InventoryError(f"invalid numeric index {key}") from exc
    if number < 0:
        raise InventoryError(f"{key} must be nonnegative")
    return number


def _exact_fields(record, names, label):
    if not isinstance(record, _parser.Record) or tuple(key for key, _ in record.fields) != tuple(names):
        raise InventoryError(f"{label} has an unknown, missing, or reordered union shape")


def _records(r, key):
    try:
        return _parser._records(_one(r, key), key)
    except _parser.ShapeError as exc:
        raise InventoryError(str(exc)) from exc


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    return value


def _span_loc(span, endpoint):
    """Decode regular span endpoint (file path, line, column), rejecting dummy."""
    if not isinstance(span, _parser.Record):
        raise InventoryError("source span must be a record")
    regular = _one(span, "regular", required=False)
    if not isinstance(regular, _parser.Record):
        raise InventoryError("dummy or unrecognized span cannot bind source")
    loc = _one(regular, endpoint)
    if not isinstance(loc, _parser.Record):
        raise InventoryError("span endpoint must be a location")
    line = _uint(loc, "line")
    col = _one(loc, "col")
    if not isinstance(col, _parser.Record):
        raise InventoryError("location column must be CharPos record")
    pos = _one(col, "pos")
    if not isinstance(pos, _parser.Number):
        raise InventoryError("location column must be numeric")
    filename = _one(loc, "file")
    if not isinstance(filename, _parser.Record):
        raise InventoryError("location file must be a record")
    name = _one(filename, "name")
    if not isinstance(name, _parser.Record):
        raise InventoryError("source file name must be a record")
    real = _one(name, "real", required=False)
    if not isinstance(real, _parser.Record):
        raise InventoryError("non-real source path cannot bind fixture")
    path = _one(real, "localPath", required=False)
    if isinstance(path, _parser.Record):
        path = _one(path, "text")
    if not isinstance(path, _parser.Text):
        remapped = _one(real, "remapped", required=False)
        if isinstance(remapped, _parser.Record):
            path = _one(remapped, "virtualName")
    if not isinstance(path, _parser.Text):
        raise InventoryError("source path is missing or non-text")
    try:
        column = int(pos.value, 0)
    except ValueError as exc:
        raise InventoryError("invalid span column") from exc
    if column < 0:
        raise InventoryError("negative span column")
    return path.value, line, column


def _span(span):
    lo = _span_loc(span, "lo")
    hi = _span_loc(span, "hi")
    if lo[0] != hi[0] or (hi[1], hi[2]) < (lo[1], lo[2]):
        raise InventoryError("malformed or cross-file span")
    return lo, hi


def _find_vfmir(source):
    try:
        records = _parser.parse_records(source)
    except (_parser.ParseError, _parser.ShapeError) as exc:
        raise InventoryError(f"decoded VfMir parse failed: {exc}") from exc
    roots = [r for r in records if _one(r, "traitImpls", required=False) is not None
             and _one(r, "traits", required=False) is not None
             and _one(r, "bodies", required=False) is not None]
    if len(roots) != 1:
        raise InventoryError("expected exactly one VfMir root record")
    return roots[0]


def _unique_by(rows, key_fn, label):
    output = {}
    for row in rows:
        key = key_fn(row)
        if key in output:
            raise InventoryError(f"duplicate {label} identity {key!r}")
        output[key] = row
    return output


def _trait(root):
    try:
        traits = _records(root, "traits")
    except InventoryError:
        raise
    found = [t for t in traits if _text(t, "name") == "StableSmallSortTypeImpl"]
    if len(found) != 1:
        raise InventoryError("expected exactly one root StableSmallSortTypeImpl trait")
    trait = found[0]
    required = _records(trait, "requiredFns")
    names = [_text(f, "name") for f in required]
    if len(names) != 2 or set(names) != {"small_sort_threshold", "small_sort"}:
        raise InventoryError("root trait must contain exactly the two expected required methods")
    _unique_by(required, lambda f: _text(f, "name"), "required method name")
    # Patched required-item encoding carries stable compiler indices and parent.
    parent_paths = {_text(fn, "parentDefId") for fn in required}
    if parent_paths != {"StableSmallSortTypeImpl"}:
        raise InventoryError("required methods do not identify the exact root trait compiler path")
    for fn in required:
        if _text(fn, "parentDefId") not in parent_paths:
            raise InventoryError("required method has wrong parent compiler path")
        _uint(fn, "defIndex")
        _uint(fn, "parentDefIndex")
        if _one(fn, "scopedRepresentation") != _parser.Atom("true"):
            raise InventoryError("required method lacks scoped representation")
        _span(_one(fn, "nameSpan"))
        if _text(fn, "defId") != "StableSmallSortTypeImpl::" + _text(fn, "name"):
            raise InventoryError("required method has an unexpected compiler DefId")
    if len({_uint(fn, "parentDefIndex") for fn in required}) != 1:
        raise InventoryError("required methods disagree on root trait compiler identity")
    if len({_uint(fn, "defIndex") for fn in required}) != 2:
        raise InventoryError("required methods reuse a compiler identity")
    return trait, required


def _impls(root, expected_trait_path):
    rows = _records(root, "traitImpls")
    selected = [i for i in rows if _text(i, "ofTrait") == "StableSmallSortTypeImpl"]
    if len(selected) != 2:
        raise InventoryError("expected exactly two source impls of root trait")
    by_id = _unique_by(selected, lambda i: _uint(i, "defIndex"), "impl defIndex")
    result = {}
    trait_paths = {_text(i, "ofTrait") for i in selected}
    if trait_paths != {expected_trait_path}:
        raise InventoryError("source impls disagree on the root trait compiler path")
    for impl in by_id.values():
        items = _records(impl, "items")
        wanted = [item for item in items if _text(item, "name") in
                  ("small_sort_threshold", "small_sort")]
        if len(wanted) != 2 or len(items) != 2:
            raise InventoryError("each impl must inventory threshold and small_sort items")
        mapping = _unique_by(wanted, lambda x: _text(x, "name"), "impl item name")
        item_ids = [_uint(x, "defIndex") for x in wanted]
        if len(set(item_ids)) != 2:
            raise InventoryError("impl item compiler identities must be distinct")
        for item in wanted:
            _text(item, "defId")
        unsafe = _one(impl, "isUnsafe")
        negative = _one(impl, "isNegative")
        if unsafe != _parser.Atom("false") or negative != _parser.Atom("false"):
            raise InventoryError("A1 source impls must be positive and safe")
        if _text(impl, "selfTy") != "T":
            raise InventoryError("A1 source impl self type must be compiler-reported T")
        gen_args = _records(impl, "genArgs")
        if len(gen_args) != 1 or _generic_arg_type_param(gen_args[0]) != "T":
            raise InventoryError("A1 trait impl genArgs must contain exactly self type T")
        generics = _records(impl, "generics")
        clauses = _records(impl, "clauses")
        generic_names = tuple(_text(g, "name") for g in generics)
        if generic_names != ("T",):
            raise InventoryError("A1 impl compiler generics must contain exactly the source type parameter T")
        generic = generics[0]
        if _index(generic, "index") != 0:
            raise InventoryError("A1 impl type parameter T must have compiler generic index zero")
        _uint(generic, "defIndex")
        kind = _one(generic, "kind")
        if not isinstance(kind, _parser.Record):
            raise InventoryError("A1 impl generic kind must be a record")
        _exact_fields(kind, ("type",), "A1 impl generic kind")
        if _one(kind, "type", required=False) != _parser.Atom("void"):
            raise InventoryError("A1 impl generic T must have compiler type kind")
        # Keep full generic/clauses records as canonical rendered observations;
        # the per-declaration native contract remains outside this parser.
        result[_uint(impl, "defIndex")] = {
            "impl": impl, "items": mapping, "generics": generics,
            "clauses": clauses, "generic_names": generic_names,
            "self_ty": _text(impl, "selfTy"),
            "span": _span(_one(impl, "span")),
        }
    return result


def _body_map(root):
    bodies = _records(root, "bodies")
    indexed = _unique_by(bodies, lambda b: _uint(b, "defIndex"), "body defIndex")
    output = {}
    for ident, body in indexed.items():
        path = _text(body, "defPath")
        output[ident] = {
            "def_path": path,
            "fn_sig_span": _span(_one(body, "fnSigSpan")),
            "mir_span": _span(_one(body, "span")),
            "imp_span": _span(_one(body, "impSpan")),
            "record": body,
        }
    return output


def _scope_body_callable(clause, body_id, ordinal, input_regions):
    """Resolve this compiler Clause's references against its own Binder slots.

    Printed names identify slots only inside this boundRegions list. Scope
    ownership comes from the selected compiler Body and the Clause occurrence,
    not from the spelling or proximity of another clause's names.
    """
    names = clause[3]
    if len(names) != 2 or len(set(names)) != 2:
        raise InventoryError("impl small_sort Body clause must have two distinct local binders")
    if set(input_regions) & set(names):
        raise InventoryError("impl small_sort Body clause captures an input region")
    keys = tuple(("body-clause", body_id, ordinal, i) for i in range(2))
    bindings = dict(zip(names, keys))

    def resolve(value):
        if isinstance(value, tuple):
            if len(value) == 4 and value[0] == "ref":
                if value[1] not in bindings:
                    raise InventoryError("impl small_sort Body clause reference is free or outside its scope")
                return ("ref", bindings[value[1]], value[2], resolve(value[3]))
            return tuple(resolve(x) for x in value)
        return value

    # Generic type parameters inhabit a separate namespace; only typed ref
    # region positions are rewritten. Raw compiler records stay untouched.
    return (clause[0], clause[1], resolve(clause[2]), keys, *clause[4:])


def _impl_body_small_sort(body, impl_name, expected_impl_generic_id):
    record = body["record"]
    impl_generics = _records(record, "implBlockGenerics")
    generics = _records(record, "generics")
    impl_names = tuple(_text(x, "name") for x in impl_generics)
    generic_names = tuple(_text(x, "name") for x in generics)
    if impl_names != ("T",) or tuple(_index(x, "index") for x in impl_generics) != (0,) or \
            generic_names != ("F",) or tuple(_index(x, "index") for x in generics) != (1,):
        raise InventoryError("impl small_sort Body must retain impl T and method F in their schema tables")
    impl_ids = tuple(_uint(x, "defIndex") for x in impl_generics)
    generic_ids = tuple(_uint(x, "defIndex") for x in generics)
    if impl_ids != (expected_impl_generic_id,):
        raise InventoryError("impl small_sort Body T identity differs from its compiler TraitImpl")
    if len(set(impl_ids + generic_ids)) != 2:
        raise InventoryError("impl small_sort Body generic compiler identities collide")
    input_types = tuple(_ty(x) for x in _list(_member(record, "inputs"), "impl small_sort Body inputs"))
    output = _ty(_member(record, "output"))
    if len(input_types) != 3 or output != ("tuple", ()):
        raise InventoryError("impl small_sort Body signature must have three inputs and unit output")
    regions = tuple(x[1] for x in input_types if isinstance(x, tuple) and len(x) == 4 and x[0] == "ref")
    if len(regions) != 3 or len(set(regions)) != 3:
        raise InventoryError("impl small_sort Body input regions must remain distinct")
    alias = {"T": "@Self", "F": "@F", **{region: f"@input_{i}" for i, region in enumerate(regions)}}

    def normalized(value):
        if isinstance(value, str):
            return alias.get(value, value)
        if isinstance(value, tuple):
            return tuple(normalized(x) for x in value)
        return value
    normalized_inputs = tuple(normalized(x) for x in input_types)
    expected_inputs = (
        ("ref", "@input_0", True, ("slice", ("param", "@Self"))),
        ("ref", "@input_1", True, ("slice", ("adt", "MaybeUninit", (("type", ("param", "@Self")),)))),
        ("ref", "@input_2", True, ("param", "@F")))
    if normalized_inputs != expected_inputs:
        raise InventoryError("impl small_sort Body signature differs from Self/F positional input types")

    clauses = tuple(normalized(_canonical_small_sort_clause(_trait_clause_shape(x)))
                    for x in _records(record, "clauses"))
    sized = [x for x in clauses if x == ("trait", "Sized", (("type", ("param", "@F")),), ())]
    fnmut = [x for x in clauses if x[0] == "trait" and x[1] == "FnMut"]
    output_rows = [x for x in clauses if x[0] == "projection" and x[1] == "Output"]
    if len(clauses) != 3 or len(sized) != 1 or len(fnmut) != 1 or len(output_rows) != 1:
        raise InventoryError("impl small_sort Body must retain exact Sized(F)/FnMut/Output clauses")
    try:
        body_id = _uint(record, "defIndex")
    except _parser.ShapeError as exc:
        raise InventoryError(str(exc)) from exc
    scoped_input_regions = tuple(alias[r] for r in regions)
    clauses = tuple(_scope_body_callable(clause, body_id, ordinal, scoped_input_regions)
                    if clause is fnmut[0] or clause is output_rows[0] else clause
                    for ordinal, clause in enumerate(clauses))
    fnmut = [x for x in clauses if x[0] == "trait" and x[1] == "FnMut"]
    output_rows = [x for x in clauses if x[0] == "projection" and x[1] == "Output"]
    _, _, fn_args, fn_regions = fnmut[0]
    _, _, out_args, out_regions, out_ty = output_rows[0]
    def callable_args(regions_):
        if len(regions_) != 2 or len(set(regions_)) != 2:
            return None
        return (("type", ("param", "@F")), ("type", ("tuple", (
            ("ref", regions_[0], False, ("param", "@Self")),
            ("ref", regions_[1], False, ("param", "@Self"))))))
    if fn_args != callable_args(fn_regions) or out_args != callable_args(out_regions) or \
            out_ty != ("bool",) or set(fn_regions) & set(out_regions):
        raise InventoryError("impl small_sort Body FnMut/Output binders are merged or malformed")
    canonical = {"impl_generic_names": impl_names,
                 "impl_generic_ids": impl_ids,
                 "generic_names": generic_names,
                 "generic_ids": generic_ids,
                 "input_regions": tuple(alias[r] for r in regions),
                 "inputs": normalized_inputs,
                 "clauses": clauses,
                 "impl": impl_name,
                 "def_path": body["def_path"],
                 "fn_sig_span": body["fn_sig_span"],
                 "mir_span": body["mir_span"]}
    canonical["digest"] = hashlib.sha256(json.dumps(canonical, sort_keys=True, default=str).encode()).hexdigest()
    return canonical


def _generic_arg_type_param(arg):
    _exact_fields(arg, ("kind",), "generic argument")
    kind = _one(arg, "kind")
    if not isinstance(kind, _parser.Record):
        raise InventoryError("generic argument kind must be a record")
    _exact_fields(kind, ("type",), "generic argument kind")
    ty = _one(kind, "type", required=False)
    if not isinstance(ty, _parser.Record):
        raise InventoryError("generic argument must be a type argument")
    _exact_fields(ty, ("kind",), "generic argument type")
    ty_kind = _one(ty, "kind")
    if not isinstance(ty_kind, _parser.Record):
        raise InventoryError("generic argument type kind must be a record")
    _exact_fields(ty_kind, ("param",), "generic argument type kind")
    param = _one(ty_kind, "param", required=False)
    if not isinstance(param, _parser.Text):
        raise InventoryError("generic argument must name a type parameter")
    return param.value


def _member(record, key):
    try:
        return _one(record, key)
    except _parser.ShapeError as exc:
        raise InventoryError(str(exc)) from exc


def _text_atom(value, label):
    if not isinstance(value, _parser.Text):
        raise InventoryError(f"{label} must be quoted text")
    return value.value


def _list(value, label):
    if not isinstance(value, _parser.ListValue):
        raise InventoryError(f"{label} must be a list")
    return value.values


def _union(record, label, choices):
    if not isinstance(record, _parser.Record):
        raise InventoryError(f"{label} must be a union record")
    keys = tuple(key for key, _ in record.fields)
    if len(keys) != 1 or keys[0] not in choices:
        raise InventoryError(f"{label} has an unknown union shape")
    return keys[0], _member(record, keys[0])


def _ty(value):
    """Decode just the closed compiler type subset used by small_sort."""
    kind, payload = _union(_member(value, "kind"), "small_sort type kind",
                           ("ref", "slice", "param", "adt", "tuple", "bool"))
    if kind == "param":
        return ("param", _text_atom(payload, "type parameter"))
    if kind == "ref":
        region = _member(payload, "region")
        region_id = _text_atom(_member(region, "id"), "reference region id")
        referent = _ty(_member(payload, "ty"))
        mutability, mut_payload = _union(_member(payload, "mutability"), "reference mutability",
                                         ("mut", "not"))
        if mut_payload != _parser.Atom("void"):
            raise InventoryError("reference mutability payload must be void")
        return ("ref", region_id, mutability == "mut", referent)
    if kind == "slice":
        return ("slice", _ty(payload))
    if kind == "tuple":
        return ("tuple", tuple(_ty(x) for x in _list(payload, "tuple type")))
    if kind == "bool":
        if payload != _parser.Atom("void"):
            raise InventoryError("bool type payload must be void")
        return ("bool",)
    if kind == "adt":
        adt_id = _member(payload, "id")
        name = _text(adt_id, "name")
        adt_kind, adt_payload = _union(_member(payload, "kind"), "ADT kind",
                                       ("structKind", "enumKind", "unionKind"))
        if adt_kind != "unionKind" or adt_payload != _parser.Atom("void"):
            raise InventoryError("MaybeUninit must retain its compiler union ADT kind")
        if name not in ("core::mem::MaybeUninit", "std::mem::MaybeUninit"):
            raise InventoryError("unsupported ADT identity in small_sort interface")
        name = "MaybeUninit"
        args = _list(_member(payload, "substs"), "ADT substitutions")
        return ("adt", name, tuple(_generic_arg_shape(x) for x in args))
    raise InventoryError("unsupported small_sort compiler type")


def _generic_arg_shape(value):
    kind, payload = _union(_member(value, "kind"), "generic argument kind",
                           ("type", "lifetime"))
    if kind == "type":
        return ("type", _ty(payload))
    return ("lifetime", _text_atom(_member(payload, "id"), "generic lifetime id"))


def _trait_clause_shape(value):
    union, clause = _union(value, "small_sort clause", ("trait", "projection"))
    if union == "trait":
        name = _text_atom(_member(clause, "defId"), "trait clause DefId")
        args = tuple(_generic_arg_shape(x) for x in
                     _list(_member(clause, "args"), "trait clause args"))
        regions = tuple(_text_atom(x, "trait bound region") for x in
                        _list(_member(clause, "boundRegions"), "trait bound regions"))
        return ("trait", name, args, regions)
    term = _member(clause, "projectionTerm")
    name = _text_atom(_member(term, "defId"), "projection DefId")
    args = tuple(_generic_arg_shape(x) for x in
                 _list(_member(term, "args"), "projection args"))
    regions = tuple(_text_atom(x, "projection bound region") for x in
                    _list(_member(clause, "boundRegions"), "projection bound regions"))
    rhs = _member(clause, "term")
    rhs_kind, rhs_value = _union(rhs, "projection result", ("ty",))
    return ("projection", name, args, regions, _ty(rhs_value))


def _canonical_small_sort_clause(shape, *, parent_trait=None):
    """Accept only the pinned standard-library identities used by this API."""
    kind, name, *rest = shape
    if kind == "trait" and name in ("core::marker::Sized", "std::marker::Sized"):
        return (kind, "Sized", *rest)
    if kind == "trait" and name in ("core::ops::FnMut", "std::ops::FnMut"):
        return (kind, "FnMut", *rest)
    if kind == "projection" and name in (
            "core::ops::FnOnce::Output", "std::ops::FnOnce::Output"):
        return (kind, "Output", *rest)
    if kind == "trait" and parent_trait is not None and name == parent_trait:
        return (kind, "StableSmallSortTypeImpl", *rest)
    raise InventoryError("small_sort clause has an unexpected compiler DefId")


def _required_hir_partition(method, early_type_names, fresh_lifetime_count):
    """Validate optional HIR generic metadata without joining it to scoped lifetimes."""
    fields = [value for key, value in method.fields if key == "hirGenerics"]
    if not fields:
        return
    if len(fields) != 1 or not isinstance(fields[0], _parser.Record):
        raise InventoryError("required method HIR generics must be one explicit record")
    params = _list(_member(fields[0], "params"), "required method HIR parameters")
    expected_count = len(early_type_names) + fresh_lifetime_count
    if len(params) != expected_count:
        raise InventoryError("required method HIR early types/Fresh lifetime partition has wrong length")
    fresh_ids = set()
    for position, param in enumerate(params):
        if not isinstance(param, _parser.Record):
            raise InventoryError("required method HIR parameter must be a record")
        _span(_member(param, "span"))
        if _member(param, "pureWrtDrop") != _parser.Atom("false") or \
                _member(param, "bounds") != _parser.Atom("void"):
            raise InventoryError("required method HIR parameter drop/bounds flags differ from source")
        kind, kind_payload = _union(_member(param, "kind"),
                                    "required method HIR parameter kind",
                                    ("type", "lifetime", "const"))
        if kind_payload != _parser.Atom("void"):
            raise InventoryError("required method HIR parameter kind payload must be void")
        name_tag, name_payload = _union(_member(param, "name"),
                                        "required method HIR parameter name",
                                        ("plain", "fresh"))
        if position < len(early_type_names):
            expected_name = early_type_names[position]
            if kind != "type" or name_tag != "plain" or not isinstance(name_payload, _parser.Record):
                raise InventoryError("required method HIR early parameter must be a plain type generic")
            symbol = _member(name_payload, "name")
            if not isinstance(symbol, _parser.Record) or \
                    _text_atom(_member(symbol, "name"), "required method HIR type name") != expected_name:
                raise InventoryError("required method HIR early type name differs from compiler generic")
            continue
        if kind != "lifetime" or name_tag != "fresh":
            raise InventoryError("required method HIR late parameter must be a Fresh lifetime")
        _exact_fields(name_payload, ("h", "l"), "required method HIR Fresh UInt128 identity")
        high, low = _index(name_payload, "h"), _uint(name_payload, "l")
        if high != 0 or low >= (1 << 64):
            raise InventoryError("required method HIR Fresh identity is outside compiler index range")
        if low in fresh_ids:
            raise InventoryError("required method HIR Fresh identity is duplicated")
        fresh_ids.add(low)


def _required_small_sort(required):
    methods = [fn for fn in required if _text(fn, "name") == "small_sort"]
    if len(methods) != 1:
        raise InventoryError("expected one compiler required small_sort method")
    method = methods[0]
    if _one(method, "scopedRepresentation") != _parser.Atom("true"):
        raise InventoryError("small_sort required method lacks scoped representation")
    method_id = _uint(method, "defIndex")
    parent_id = _uint(method, "parentDefIndex")
    if _text(method, "defId") != "StableSmallSortTypeImpl::small_sort" or \
            _text(method, "parentDefId") != "StableSmallSortTypeImpl":
        raise InventoryError("required small_sort compiler DefId does not match its owner")

    type_params = _records(method, "typeParams")
    if len(type_params) != 2:
        raise InventoryError("small_sort must retain exactly Self and method F type bindings")
    names = tuple(_text(x, "name") for x in type_params)
    indices = tuple(_index(x, "index") for x in type_params)
    type_ids = tuple(_uint(x, "defIndex") for x in type_params)
    if names != ("Self", "F") or indices != (0, 1) or len(set(type_ids)) != 2:
        raise InventoryError("small_sort Self/F compiler type identities are incomplete or reordered")
    aliases = tuple(_text(x, "alias") for x in type_params)
    if len(set(aliases)) != 2:
        raise InventoryError("small_sort Self/F wire aliases collide")
    generic_rows = _records(method, "generics")
    if len(generic_rows) != 1 or _text(generic_rows[0], "name") != "F" or \
            _index(generic_rows[0], "index") != 1 or \
            _uint(generic_rows[0], "defIndex") != type_ids[1]:
        raise InventoryError("small_sort method generic table does not identify F")
    _required_hir_partition(method, tuple(_text(row, "name") for row in generic_rows), 3)

    lifetime_params = tuple(_text_atom(x, "small_sort signature lifetime") for x in
                            _list(_member(method, "lifetimeParams"), "small_sort lifetimeParams"))
    scoped = _records(method, "scopedRegions")
    scoped_rows = []
    semantic_ids, wire_aliases = set(), set()
    for row in scoped:
        alias = _text(row, "alias")
        scope = _text(row, "scope")
        depth, index = _index(row, "depth"), _index(row, "index")
        kind = _text(row, "kind")
        elided = _member(row, "elidedRole")
        if elided not in (_parser.Atom("true"), _parser.Atom("false")):
            raise InventoryError("small_sort scoped region elidedRole must be boolean")
        semantic = (scope, depth, index, kind)
        if alias in wire_aliases or semantic in semantic_ids or depth != 0 or kind not in ("anon", "named", "printing"):
            raise InventoryError("small_sort scoped region identity is duplicate or malformed")
        wire_aliases.add(alias)
        semantic_ids.add(semantic)
        scoped_rows.append((alias, scope, depth, index, kind, elided == _parser.Atom("true")))
    by_scope = {scope: [row for row in scoped_rows if row[1] == scope]
                for scope in {row[1] for row in scoped_rows}}
    sig_rows = by_scope.get("sig", [])
    if len(lifetime_params) != 3 or len(set(lifetime_params)) != 3 or \
            len(sig_rows) != 3 or tuple(row[0] for row in sorted(sig_rows, key=lambda x: x[3])) != lifetime_params or \
            tuple(row[3] for row in sorted(sig_rows, key=lambda x: x[3])) != (0, 1, 2) or \
            not all(row[5] for row in sig_rows):
        raise InventoryError("small_sort must preserve three ordered distinct scoped input regions")

    def normalize_shape(value, names):
        if isinstance(value, str):
            return names.get(value, value)
        if isinstance(value, tuple):
            if len(value) == 2 and value[0] == "param" and value[1] in names:
                return ("param", names[value[1]])
            if len(value) == 4 and value[0] == "ref" and value[1] in names:
                return (value[0], names[value[1]], value[2], normalize_shape(value[3], names))
            return tuple(normalize_shape(x, names) for x in value)
        return value
    type_names = {aliases[0]: "Self", aliases[1]: "F"}
    region_names = {region: f"@input_{i}" for i, region in enumerate(lifetime_params)}
    inputs = tuple(normalize_shape(_ty(x), type_names | region_names)
                   for x in _list(_member(method, "inputs"), "small_sort inputs"))
    output = normalize_shape(_ty(_member(method, "output")), type_names | region_names)
    if len(inputs) != 3 or output != ("tuple", ()):
        raise InventoryError("small_sort compiler signature must have three inputs and unit output")
    if inputs != tuple(("ref", f"@input_{i}", True, inner) for i, inner in enumerate((
            ("slice", ("param", "Self")),
            ("slice", ("adt", "MaybeUninit", (("type", ("param", "Self")),))),
            ("param", "F")))):
        raise InventoryError("small_sort compiler signature lost Self, F, mutability, or positional input regions")

    clauses = tuple(normalize_shape(_canonical_small_sort_clause(_trait_clause_shape(x)),
                                    type_names | region_names)
                    for x in _records(method, "clauses"))
    if len(clauses) != 3:
        raise InventoryError("small_sort required item must retain exactly three method-owned clauses")
    expected_fixed = {
        ("trait", "Sized", (("type", ("param", "F")),), ()),
    }
    if not expected_fixed.issubset(set(clauses)):
        raise InventoryError("small_sort full clauses lost Sized(Self) or Sized(F)")
    fnmut = [x for x in clauses if x[0] == "trait" and x[1] == "FnMut"]
    output_clause = [x for x in clauses if x[0] == "projection" and x[1] == "Output"]
    if len(fnmut) != 1 or len(output_clause) != 1:
        raise InventoryError("small_sort full FnMut/Output clause pair is missing")
    _, _, fn_args, fn_regions = fnmut[0]
    _, _, out_args, out_regions, out_ty = output_clause[0]
    fn_regions = tuple(fnmut[0][3])
    out_binders = tuple(output_clause[0][3])
    expected_fn_args = (("type", ("param", "F")), ("type", ("tuple", (
        ("ref", fn_regions[0], False, ("param", "Self")),
        ("ref", fn_regions[1], False, ("param", "Self")))))) if len(fn_regions) == 2 else ()
    expected_out_args = (("type", ("param", "F")), ("type", ("tuple", (
        ("ref", out_binders[0], False, ("param", "Self")),
        ("ref", out_binders[1], False, ("param", "Self")))))) if len(out_binders) == 2 else ()
    if len(fn_regions) != 2 or len(set(fn_regions)) != 2 or fn_args != expected_fn_args or \
            len(out_binders) != 2 or len(set(out_binders)) != 2 or out_args != expected_out_args or out_ty != ("bool",):
        raise InventoryError("small_sort HRTB FnMut/Output clauses differ or lose bound regions")
    fnmut_ordinal = next(i for i, clause in enumerate(clauses)
                         if clause[0] == "trait" and clause[1] == "FnMut")
    output_ordinal = next(i for i, clause in enumerate(clauses)
                          if clause[0] == "projection" and clause[1] == "Output")
    hrtb_scopes = [scope for scope in by_scope if scope.startswith("clause_")]
    if len(hrtb_scopes) != 2:
        raise InventoryError("small_sort FnMut and Output must have distinct scoped binders")
    for scope in hrtb_scopes:
        rows = sorted(by_scope[scope], key=lambda x: x[3])
        expected_binders = (fn_regions if scope == f"clause_{fnmut_ordinal}" else
                            out_binders if scope == f"clause_{output_ordinal}" else ())
        if len(rows) != 2 or tuple(x[3] for x in rows) != (0, 1) or \
                tuple(x[0] for x in rows) != expected_binders:
            raise InventoryError("small_sort HRTB clause binder identity is incomplete")
    if set(lifetime_params) & (set(fn_regions) | set(out_binders)) or \
            len(hrtb_scopes) != 2 or set(by_scope) != {
                "sig", f"clause_{fnmut_ordinal}", f"clause_{output_ordinal}"}:
        raise InventoryError("small_sort input and HRTB regions must remain disjoint")
    parent_trait = _text(method, "parentDefId")
    parent_clauses = tuple(normalize_shape(
        _canonical_small_sort_clause(_trait_clause_shape(x), parent_trait=parent_trait),
        type_names | region_names) for x in _records(method, "parentClauses"))
    expected_parent = {
        ("trait", "Sized", (("type", ("param", "Self")),), ()),
        ("trait", "StableSmallSortTypeImpl", (("type", ("param", "Self")),), ()),
    }
    if set(parent_clauses) != expected_parent:
        raise InventoryError("small_sort parent trait clauses are incomplete or unexpected")

    # Canonicalize aliases by positional binder role; compiler numeric identity
    # remains separately exposed and never derives from rendered names.
    alpha = {aliases[0]: "@Self", aliases[1]: "@F"}
    alpha.update({region: f"@input_{i}" for i, region in enumerate(lifetime_params)})
    for scope, rows in by_scope.items():
        if scope.startswith("clause_"):
            for i, row in enumerate(sorted(rows, key=lambda x: x[3])):
                alpha[row[0]] = f"@hrtb_{i}"
    def canon(value):
        if isinstance(value, _parser.Text):
            return alpha.get(value.value, value.value)
        if isinstance(value, _parser.Record):
            return tuple((k, canon(v)) for k, v in value.fields)
        if isinstance(value, _parser.ListValue):
            return tuple(canon(x) for x in value.values)
        if isinstance(value, _parser.Number):
            return int(value.value, 0)
        if isinstance(value, _parser.Atom):
            return value.value
        raise InventoryError("unknown compiler small_sort interface value")
    identity = {
        "required_def_id": _text(method, "defId"), "required_def_index": method_id,
        "parent_def_id": _text(method, "parentDefId"), "parent_def_index": parent_id,
        "source_span": _span(_member(method, "nameSpan")),
        "type_params": tuple((names[i], indices[i], type_ids[i]) for i in range(2)),
        "signature_regions": tuple(alpha[x] for x in lifetime_params),
        "hrtb_regions": tuple(alpha[x] for x in fn_regions),
        "scoped_regions": tuple((alpha.get(a, a), scope, depth, index, kind, elided)
                                 for a, scope, depth, index, kind, elided in scoped_rows),
        "inputs": inputs, "output": output,
        "clauses": tuple(canon(x) for x in _records(method, "clauses")),
        "parent_clauses": tuple(canon(x) for x in _records(method, "parentClauses")),
        "ast_type_param_names": ("Self", "F"),
        "alpha_roles": ("Self", "F", "input_0", "input_1", "input_2", "hrtb_0", "hrtb_1"),
    }
    identity["interface_digest"] = hashlib.sha256(json.dumps(identity, sort_keys=True, default=str).encode()).hexdigest()
    return identity


def tuple_shape(value):
    return value


def _trait_clause(clause):
    _exact_fields(clause, ("trait",), "impl clause")
    trait = _one(clause, "trait", required=False)
    if not isinstance(trait, _parser.Record):
        raise InventoryError("impl clause must be a positive trait clause")
    _exact_fields(trait, ("defId", "args", "boundRegions"), "impl trait clause")
    name = _text(trait, "defId")
    # The schema requires explicit self type; absence must not degrade to a
    # path-only trait match.
    args = _records(trait, "args")
    if len(args) != 1 or _generic_arg_type_param(args[0]) != "T":
        raise InventoryError("impl trait clause must bind exactly compiler type parameter T")
    regions = _one(trait, "boundRegions")
    if not isinstance(regions, _parser.ListValue) or regions.values:
        raise InventoryError("impl applicability clauses must have no bound regions")
    return name


def _freeze_shape(root):
    trait, required = _trait(root)
    required_small_sort = _required_small_sort(required)
    impls = _impls(root, _text(required[0], "parentDefId"))
    bodies = _body_map(root)
    global_item_ids = set()
    observations = []
    for impl_id, info in impls.items():
        clause_names = tuple(_trait_clause(c) for c in info["clauses"])
        freeze_clause = "FreezeMarker" in " ".join(clause_names)
        name = "freeze32" if freeze_clause else "default16"
        if name in {x["impl"] for x in observations}:
            raise InventoryError("ambiguous default/Freeze impl applicability")
        observed_items = []
        for method in ("small_sort_threshold", "small_sort"):
            item = info["items"][method]
            item_id = _uint(item, "defIndex")
            if item_id in global_item_ids:
                raise InventoryError("compiler item identity reused across impls")
            global_item_ids.add(item_id)
            body = bodies.get(item_id)
            if body is None:
                raise InventoryError(f"impl item {method} has no body matched by compiler defIndex")
            if _text(item, "defId") != body["def_path"]:
                raise InventoryError("impl item defId does not match body's defPath")
            observed_items.append({"name": method, "def_index": item_id,
                                   "def_id": _text(item, "defId"), "body": body,
                                   "small_sort_signature": (_impl_body_small_sort(
                                       body, name, _uint(info["generics"][0], "defIndex"))
                                       if method == "small_sort" else None)})
        observations.append({"impl": name, "impl_def_index": impl_id,
                             "self_ty": info["self_ty"], "generic_names": info["generic_names"],
                             "generics": tuple(_parser.render_value(x) for x in info["generics"]),
                             "clauses": tuple(_parser.render_value(x) for x in info["clauses"]),
            "clause_names": clause_names,
                             "span": info["span"], "items": tuple(observed_items)})
    if {x["impl"] for x in observations} != {"default16", "freeze32"}:
        raise InventoryError("could not distinguish default and Freeze impl applicability")
    by_kind = {x["impl"]: x for x in observations}
    for kind, required_clause_names in (("default16", ("Sized",)),
                                        ("freeze32", ("Sized", "FreezeMarker"))):
        names = by_kind[kind]["clause_names"]
        suffixes = tuple(name.split("::")[-1] for name in names)
        if len(suffixes) != len(required_clause_names) or set(suffixes) != set(required_clause_names):
            raise InventoryError(f"{kind} impl clauses are not exact Sized/Freeze applicability")
        sized = [name for name in names if name.split("::")[-1] == "Sized"]
        if any(name not in ("core::marker::Sized", "std::marker::Sized") for name in sized):
            raise InventoryError("impl Sized clause is not the canonical marker trait")
        if kind == "freeze32" and not any(name.endswith("::FreezeMarker") or name == "FreezeMarker"
                                          for name in names):
            raise InventoryError("Freeze clause does not name the source-local FreezeMarker")
        if kind == "freeze32":
            if "FreezeMarker" not in names:
                raise InventoryError("Freeze applicability does not resolve to this fixture's FreezeMarker")
    if not set(bodies).issuperset(global_item_ids):
        raise InventoryError("one or more impl item bodies are unbound")
    impl_ids = set(impls)
    if impl_ids.intersection(global_item_ids) or impl_ids.intersection(bodies):
        raise InventoryError("impl/body/item compiler identities collide across entity kinds")
    required_ids = {_uint(x, "defIndex") for x in required}
    if required_ids.intersection(impl_ids) or required_ids.intersection(bodies):
        raise InventoryError("trait method and impl/body compiler identities collide")
    small_sort_required_id = required_small_sort["required_def_index"]
    impl_small_sort_identities = tuple(sorted(
        ({"impl": row["impl"], "impl_def_index": row["impl_def_index"],
          "item_def_index": next(item["def_index"] for item in row["items"]
                                  if item["name"] == "small_sort"),
          "item_def_id": next(item["def_id"] for item in row["items"]
                               if item["name"] == "small_sort"),
          "ast_body_line": next(item["body"]["mir_span"][0][1] for item in row["items"]
                                if item["name"] == "small_sort"),
          "source_body_span": next(item["body"]["mir_span"] for item in row["items"]
                                   if item["name"] == "small_sort"),
          "compiler_signature_digest": next(item["small_sort_signature"]["digest"]
                                             for item in row["items"]
                                             if item["name"] == "small_sort"),
          "compiler_signature": next(item["small_sort_signature"]
                                      for item in row["items"]
                                      if item["name"] == "small_sort"),
          "source_fn_sig_span": next(item["body"]["fn_sig_span"] for item in row["items"]
                                      if item["name"] == "small_sort"),
          "alias": "__a1_impl_{}_item_{}_small_sort".format(
              row["impl_def_index"], next(item["def_index"] for item in row["items"]
                                            if item["name"] == "small_sort"))}
         for row in observations), key=lambda row: row["impl"]))
    return {"trait_def_id": _text(required[0], "parentDefId"),
            "trait_methods": tuple(sorted(_text(x, "name") for x in required)),
            "required_method_ids": tuple(sorted((_uint(x, "defIndex"), _text(x, "name")) for x in required)),
            "required_method_spans": tuple(sorted(
                ((_text(x, "name"), _span(_one(x, "nameSpan"))) for x in required),
                key=lambda x: x[0])),
            "required_small_sort": required_small_sort,
            "impl_small_sort_identities": impl_small_sort_identities,
            "impls": tuple(sorted(observations, key=lambda x: x["impl"])),
            "body_count": len(bodies)}


def _source_binding(case_id, cert, source_text, shape):
    """Verify generated source bytes and compiler spans are in that fixture file.

    This binds compiler identities/spans to the exact generated source file. It
    does not independently establish that source bytes equal rustc's input.
    """
    cases = cert.get("cases") if isinstance(cert, dict) else None
    inventory = cert.get("source_inventory") if isinstance(cert, dict) else None
    if not isinstance(cases, dict) or case_id not in cases or not isinstance(inventory, dict):
        raise InventoryError("fixture certificate lacks selected case/source inventory")
    case = cases[case_id]
    if not isinstance(case, dict) or not isinstance(source_text, str):
        raise InventoryError("fixture case/source text has invalid shape")
    raw = source_text.encode("utf-8")
    digest = hashlib.sha256(raw).hexdigest()
    if digest != case.get("generated_source_sha256") or digest != case.get("source_pair_id"):
        raise InventoryError("source bytes do not match certificate generated-source/source-pair hashes")
    expected_source_id = hashlib.sha256(json.dumps(
        {"source_commit": inventory.get("source_commit"),
         "source_pins": {k: v.get("sha256") for k, v in inventory.get("files", {}).items()}},
        sort_keys=True).encode()).hexdigest()
    if case.get("source_id") != expected_source_id:
        raise InventoryError("source_id does not match pinned source inventory")
    fixture_filename = case.get("source_file")
    if not isinstance(fixture_filename, str) or not fixture_filename:
        raise InventoryError("fixture certificate has no generated source filename")
    source_lines = source_text.splitlines()
    if not source_lines:
        raise InventoryError("empty fixture source")
    # Each observed span must refer to this generated unit, with valid coordinates.
    def span_slice(pair):
        lo, hi = pair
        start = lo[2]
        end = hi[2]
        if lo[1] == hi[1]:
            return source_lines[lo[1] - 1][start:end]
        return "\n".join([source_lines[lo[1] - 1][start:]] +
                          source_lines[lo[1]:hi[1] - 1] +
                          [source_lines[hi[1] - 1][:end]])

    spans = [pair for _, pair in shape["required_method_spans"]]
    for impl in shape["impls"]:
        spans.append(impl["span"])
        for item in impl["items"]:
            spans.extend((item["body"]["fn_sig_span"], item["body"]["mir_span"],
                          item["body"]["imp_span"]))
    for pair in spans:
        for path, line, col in pair:
            if line < 1 or line > len(source_lines) or col < 0 or col > len(source_lines[line - 1]):
                raise InventoryError("compiler span is outside certified generated source file bounds")
            if path != "verified/lib.rs":
                raise InventoryError("compiler input path is not canonical verified/lib.rs")
    # All spans must bind to the same compiler input path, independent of the
    # package filename recorded by the fixture constructor.
    span_paths = {point[0] for pair in spans for point in pair}
    if len(span_paths) != 1:
        raise InventoryError("compiler spans disagree on input source path")
    for method, span_pair in shape["required_method_spans"]:
        if method not in span_slice(span_pair):
            raise InventoryError("trait required-method nameSpan does not select its source method")
    for impl in shape["impls"]:
        impl_text = span_slice(impl["span"])
        if not impl_text.lstrip().startswith("impl"):
            raise InventoryError("TraitImpl.span does not begin at an impl declaration")
        marker = "FreezeMarker" if impl["impl"] == "freeze32" else "StableSmallSortTypeImpl"
        if marker not in impl_text:
            raise InventoryError("TraitImpl.span does not contain its source-certified applicability marker")
        item_cert_name = "freeze_impl" if impl["impl"] == "freeze32" else "default_impl"
        item_cert = inventory.get("items", {}).get(item_cert_name)
        if not isinstance(item_cert, dict):
            raise InventoryError("source inventory lacks exact impl bytes")
        encoded = item_cert.get("exact_bytes_base64")
        expected_item_sha = item_cert.get("sha256")
        mutation = case.get("mutation_certificate")
        if isinstance(mutation, dict) and mutation.get("mutated_impl") == impl["impl"]:
            expected_item_sha = mutation.get("mutated_item_sha256")
            exact = impl_text.encode("utf-8")
            if hashlib.sha256(exact).hexdigest() != expected_item_sha and \
                    hashlib.sha256((exact + b"\n")).hexdigest() != expected_item_sha:
                raise InventoryError("mutated impl span does not match its mutation certificate")
        else:
            import base64
            if not isinstance(encoded, str):
                raise InventoryError("source inventory impl bytes are missing")
            expected_bytes = base64.b64decode(encoded, validate=True)
            if hashlib.sha256(expected_bytes).hexdigest() != item_cert.get("sha256"):
                raise InventoryError("source certificate impl bytes do not match their recorded hash")
            expected = expected_bytes.decode("utf-8").rstrip("\n")
            if impl_text.rstrip("\n") != expected:
                raise InventoryError("compiler impl span does not equal exact source-certified impl bytes")
        for item in impl["items"]:
            il, ih = item["body"]["imp_span"]
            sl, sh = item["body"]["fn_sig_span"]
            lo, hi = impl["span"]
            if (il[0] != lo[0] or (il[1], il[2]) < (lo[1], lo[2]) or
                    (ih[1], ih[2]) > (hi[1], hi[2]) or sl[0] != lo[0] or
                    (sl[1], sl[2]) < (lo[1], lo[2]) or (sh[1], sh[2]) > (hi[1], hi[2])):
                raise InventoryError("impl item signature/impSpan is not nested in its owning impl span")
            sig = span_slice(item["body"]["fn_sig_span"])
            body = span_slice(item["body"]["imp_span"]).strip()
            if item["name"] not in sig:
                raise InventoryError("body signature span does not select the matched source item")
            if not (body.startswith("{") and body.endswith("}")):
                raise InventoryError("Body.impSpan does not select a complete source implementation block")
    return {"case_id": case_id, "source_id": case["source_id"],
            "source_pair_id": digest, "generated_source_sha256": digest,
            "fixture_source_file": fixture_filename,
            "compiler_input_path": next(iter(span_paths))}


def _parse_inventory_input(source: str, label: str):
    try:
        return _freeze_shape(_find_vfmir(source))
    except InventoryError as exc:
        match = re.search(r"at byte ([0-9]+)", str(exc))
        if match is not None:
            position = int(match.group(1))
            if 0 <= position <= len(source):
                decoder = exc.__cause__.__cause__ if exc.__cause__ else None
                local = getattr(decoder, "source_unicode_position", decoder.pos) if isinstance(decoder, json.JSONDecodeError) else None
                error_position = min(len(source), position + local) if local is not None else position
                lo, hi = max(0, error_position - 96), min(len(source), error_position + 96)
                window = source[lo:hi]
                exc.parser_diagnostic = {
                    "schema": "a1-parser-input-diagnostic-v1", "call": label,
                    "proof_credit": False, "parser_input_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                    "input_unicode_length": len(source), "input_utf8_length": len(source.encode("utf-8")),
                    "reported_position_label": "byte", "reported_position_unit": "unicode-codepoint",
                    "literal_unicode_start": position,
                    "literal_utf8_start": len(source[:position].encode("utf-8")),
                    "decoder_error": str(decoder)[:256] if decoder is not None else None,
                    "decoder_local_unicode_position": local,
                    "decoder_json_unicode_position": decoder.pos if isinstance(decoder, json.JSONDecodeError) else None,
                    "decoder_error_coordinate_unit": "normalized-json-unicode-codepoint",
                    "error_unicode_position": error_position,
                    "error_utf8_position": len(source[:error_position].encode("utf-8")),
                    "window_unicode_start": lo, "window_unicode_end": hi,
                    "window_utf8_start": len(source[:lo].encode("utf-8")),
                    "window_utf8_end": len(source[:hi].encode("utf-8")),
                    "window_json": json.dumps(window, ensure_ascii=True),
                    "window_utf8_hex": window.encode("utf-8").hex(),
                    "exception": str(exc)[:256]}
        raise


# These lists describe preprocessing-dependent execution/debug data, not the
# interface inventory. All other Body fields (including unknown fields) remain
# in the comparison. Both complete raw records remain untouched.
_OPERATIONAL_BODY_FIELDS = frozenset(("localDecls", "basicBlocks", "varDebugInfo"))


def _replace_field(record, key, value):
    if not isinstance(record, _parser.Record) or sum(k == key for k, _ in record.fields) != 1:
        raise InventoryError("cannot identify unique compiler field: " + key)
    return _parser.Record(tuple((k, value if k == key else v) for k, v in record.fields))


def _region_id_projection(region, bindings):
    name = _text_atom(_member(region, "id"), "typed region id")
    if name not in bindings:
        raise InventoryError("typed region reference is outside its validated scope")
    return _replace_field(region, "id", _parser.Text(bindings[name]))


def _type_region_projection(ty, bindings):
    # Follow only schema-owned type paths. Unknown fields are kept verbatim.
    kind = _member(ty, "kind")
    tag, payload = _union(kind, "projected type", ("ref", "slice", "tuple", "adt", "param", "bool"))
    if tag == "ref":
        projected = _replace_field(payload, "region", _region_id_projection(_member(payload, "region"), bindings))
        projected = _replace_field(projected, "ty", _type_region_projection(_member(payload, "ty"), bindings))
    elif tag == "slice":
        projected = _type_region_projection(payload, bindings)
    elif tag == "tuple":
        projected = _parser.ListValue(tuple(_type_region_projection(x, bindings)
                                            for x in _list(payload, "projected tuple")))
    elif tag == "adt":
        args = _member(payload, "substs")
        projected = _replace_field(payload, "substs", _parser.ListValue(tuple(
            _argument_region_projection(x, bindings) for x in _list(args, "projected substitutions"))))
    else:
        return ty
    return _replace_field(ty, "kind", _replace_field(kind, tag, projected))


def _argument_region_projection(arg, bindings):
    kind = _member(arg, "kind")
    tag, payload = _union(kind, "projected generic argument", ("type", "lifetime"))
    projected = (_type_region_projection(payload, bindings) if tag == "type"
                 else _region_id_projection(payload, bindings))
    return _replace_field(arg, "kind", _replace_field(kind, tag, projected))


def _hir_fresh_projection(record, input_names, seen_fresh):
    fields = [value for key, value in record.fields if key == "hirGenerics"]
    if not fields:
        # Minimal synthetic records historically omit HIR. Field presence is
        # still retained in cross-mode comparison; real exports carry it.
        return record
    if len(fields) != 1 or not isinstance(fields[0], _parser.Record):
        raise InventoryError("Body HIR generics must be one explicit record")
    hir = fields[0]
    params = _list(_member(hir, "params"), "Body HIR generic parameters")
    if len(params) != 4:
        raise InventoryError("Body HIR must contain F and three elided input lifetimes")
    projected = []
    fresh_names = []
    fresh_ids = []
    for position, param in enumerate(params):
        if not isinstance(param, _parser.Record):
            raise InventoryError("Body HIR parameter must be a record")
        if _member(param, "pureWrtDrop") != _parser.Atom("false") or \
                _member(param, "bounds") != _parser.Atom("void"):
            raise InventoryError("Body HIR parameter drop/bounds flags differ from source")
        tag, kind_payload = _union(_member(param, "kind"), "Body HIR parameter kind",
                                  ("type", "lifetime", "const"))
        name = _member(param, "name")
        name_tag, payload = _union(name, "Body HIR parameter name", ("plain", "fresh"))
        if kind_payload != _parser.Atom("void"):
            raise InventoryError("Body HIR parameter kind payload must be void")
        if position == 0:
            if tag != "type" or name_tag != "plain" or not isinstance(payload, _parser.Record):
                raise InventoryError("Body HIR first parameter must be plain type F")
            symbol = _member(payload, "name")
            if not isinstance(symbol, _parser.Record) or _text_atom(_member(symbol, "name"), "Body HIR type name") != "F":
                raise InventoryError("Body HIR type parameter must match method F")
            projected.append(param)
            continue
        if tag != "lifetime" or name_tag != "fresh":
            raise InventoryError("Body HIR input lifetime must have a Fresh compiler identity")
        _exact_fields(payload, ("h", "l"), "Body HIR Fresh UInt128 identity")
        high, low = _index(payload, "h"), _uint(payload, "l")
        if high != 0 or low >= (1 << 64):
            raise InventoryError("Body HIR Fresh identity is outside compiler index range")
        if low in seen_fresh or low in fresh_ids:
            raise InventoryError("Body HIR Fresh compiler identity is reused")
        fresh_ids.append(low)
        fresh_names.append("'__" + str(low))
        # The containing Body ID and input position are the comparison scope.
        # Only after the exact binding check below is this projected record used.
        fresh = _replace_field(payload, "l", _parser.Number(str(position)))
        projected.append(_replace_field(param, "name", _replace_field(name, "fresh", fresh)))
    if tuple(fresh_names) != input_names:
        raise InventoryError("Body HIR Fresh lifetimes do not bind ordered input regions")
    seen_fresh.update(fresh_ids)
    return _replace_field(record, "hirGenerics", _replace_field(hir, "params", _parser.ListValue(tuple(projected))))


def _body_region_projection(record, seen_fresh):
    # Caller invokes this only after _impl_body_small_sort has checked the full
    # signature, distinctness, local references, positional types and capture.
    body_id = _uint(record, "defIndex")
    inputs = _list(_member(record, "inputs"), "Body inputs")
    input_names = tuple(_ty(x)[1] for x in inputs)
    input_bindings = {name: f"@body:{body_id}:input:{slot}" for slot, name in enumerate(input_names)}
    projected = _hir_fresh_projection(record, input_names, seen_fresh)
    projected = _replace_field(projected, "inputs", _parser.ListValue(tuple(
        _type_region_projection(x, input_bindings) for x in inputs)))
    clauses = []
    for ordinal, clause in enumerate(_records(record, "clauses")):
        tag, payload = _union(clause, "Body clause", ("trait", "projection"))
        names = tuple(_text_atom(x, "Body bound region") for x in
                      _list(_member(payload, "boundRegions"), "Body clause binders"))
        bindings = {name: f"@body:{body_id}:clause:{ordinal}:region:{slot}"
                    for slot, name in enumerate(names)}
        row = _replace_field(payload, "boundRegions", _parser.ListValue(tuple(
            _parser.Text(bindings[name]) for name in names)))
        args_owner = payload if tag == "trait" else _member(payload, "projectionTerm")
        args = _parser.ListValue(tuple(_argument_region_projection(x, bindings)
                    for x in _list(_member(args_owner, "args"), "Body clause arguments")))
        if tag == "trait":
            row = _replace_field(row, "args", args)
        else:
            row = _replace_field(row, "projectionTerm", _replace_field(args_owner, "args", args))
            term = _member(payload, "term")
            row = _replace_field(row, "term", _replace_field(term, "ty",
                _type_region_projection(_member(term, "ty"), bindings)))
        clauses.append(_replace_field(clause, tag, row))
    return _replace_field(projected, "clauses", _parser.ListValue(tuple(clauses)))


def _inventory_comparison(shape):
    result = dict(shape)
    impls = []
    seen_fresh = set()
    for impl in shape["impls"]:
        row = dict(impl)
        items = []
        for item in impl["items"]:
            projected = dict(item)
            body = dict(item["body"])
            record = body["record"]
            if item["small_sort_signature"] is not None:
                record = _body_region_projection(record, seen_fresh)
            fields = []
            seen = set()
            for key, value in record.fields:
                if key in _OPERATIONAL_BODY_FIELDS:
                    if key in seen or not isinstance(value, _parser.ListValue):
                        raise InventoryError("operational Body field must be one explicit list: " + key)
                    seen.add(key)
                    # Preserve field presence/order: a missing list on one side
                    # still mismatches. Values are retained in the raw record.
                    value = _parser.ListValue(())
                fields.append((key, value))
            body["record"] = _parser.Record(tuple(fields))
            projected["body"] = body
            items.append(projected)
        row["items"] = tuple(items)
        impls.append(row)
    result["impls"] = tuple(impls)
    return result


def _first_difference(left, right, path="inventory"):
    """Bounded diagnostic coordinates only; never relaxes comparison."""
    path = path[:220]
    if left == right:
        return None
    if isinstance(left, dict) and isinstance(right, dict):
        if left.keys() != right.keys():
            return path + ".keys"
        for key in left:
            if left[key] != right[key]:
                return _first_difference(left[key], right[key], path + "." + str(key))
    if isinstance(left, _parser.Record) and isinstance(right, _parser.Record):
        if tuple(k for k, _ in left.fields) != tuple(k for k, _ in right.fields):
            return path + ".fields"
        for (key, value), (_, other) in zip(left.fields, right.fields):
            if value != other:
                return _first_difference(value, other, path + "." + key)
    if isinstance(left, _parser.ListValue) and isinstance(right, _parser.ListValue):
        return _first_difference(left.values, right.values, path)
    if isinstance(left, (tuple, list)) and isinstance(right, (tuple, list)):
        if len(left) != len(right):
            return path + ".length"
        for index, (value, other) in enumerate(zip(left, right)):
            if value != other:
                return _first_difference(value, other, path + "[" + str(index) + "]")
    return path[:240]


def observe(case_id: str, normal_text: str, readonly_text: str,
            source_certificate: dict[str, Any], generated_source: str):
    """Return immutable source-reported inventory only; proof_credit is always false."""
    normal = _parse_inventory_input(normal_text, "normal")
    readonly = _parse_inventory_input(readonly_text, "readonly")
    normal_comparison = _inventory_comparison(normal)
    readonly_comparison = _inventory_comparison(readonly)
    if normal_comparison != readonly_comparison:
        raise InventoryError("normal and readonly VfMir compiler inventories differ at " +
                             _first_difference(normal_comparison, readonly_comparison))
    binding = _source_binding(case_id, source_certificate, generated_source, normal)
    return _freeze({"schema": "a1-compiler-inventory-observation-v1",
                    "provenance": "source-reported-compiler-inventory-only",
                    "proof_credit": False, "native_contract_credit": False,
                    "case_binding": binding, "inventory": normal})
