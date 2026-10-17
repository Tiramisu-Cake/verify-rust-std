"""Fail-closed A1 compiler inventory observations from decoded VfMir text.

This module records compiler-reported identities and spans only. It does not
establish native contract semantics, verifier acceptance, or proof credit.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import importlib.util
import json
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
    if len(parent_paths) != 1 or next(iter(parent_paths)).split("::")[-1] != "StableSmallSortTypeImpl":
        raise InventoryError("required methods disagree on root trait compiler path")
    for fn in required:
        if _text(fn, "parentDefId") not in parent_paths:
            raise InventoryError("required method has wrong parent compiler path")
        _uint(fn, "defIndex")
        _uint(fn, "parentDefIndex")
        if _one(fn, "scopedRepresentation") != _parser.Atom("true"):
            raise InventoryError("required method lacks scoped representation")
        _span(_one(fn, "nameSpan"))
    if len({_uint(fn, "parentDefIndex") for fn in required}) != 1:
        raise InventoryError("required methods disagree on root trait compiler identity")
    if len({_uint(fn, "defIndex") for fn in required}) != 2:
        raise InventoryError("required methods reuse a compiler identity")
    return trait, required


def _impls(root, expected_trait_path):
    rows = _records(root, "traitImpls")
    selected = [i for i in rows if _text(i, "ofTrait").split("::")[-1] == "StableSmallSortTypeImpl"]
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
        }
    return output


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
                                   "def_id": _text(item, "defId"), "body": body})
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
            crate_prefix = _text(required[0], "parentDefId").rsplit("::", 1)[0]
            if f"{crate_prefix}::FreezeMarker" not in names:
                raise InventoryError("Freeze applicability does not resolve to this fixture's FreezeMarker")
    if not set(bodies).issuperset(global_item_ids):
        raise InventoryError("one or more impl item bodies are unbound")
    impl_ids = set(impls)
    if impl_ids.intersection(global_item_ids) or impl_ids.intersection(bodies):
        raise InventoryError("impl/body/item compiler identities collide across entity kinds")
    required_ids = {_uint(x, "defIndex") for x in required}
    if required_ids.intersection(impl_ids) or required_ids.intersection(bodies):
        raise InventoryError("trait method and impl/body compiler identities collide")
    return {"trait_def_id": _text(required[0], "parentDefId"),
            "trait_methods": tuple(sorted(_text(x, "name") for x in required)),
            "required_method_ids": tuple(sorted((_uint(x, "defIndex"), _text(x, "name")) for x in required)),
            "required_method_spans": tuple(sorted(
                ((_text(x, "name"), _span(_one(x, "nameSpan"))) for x in required),
                key=lambda x: x[0])),
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


def observe(case_id: str, normal_text: str, readonly_text: str,
            source_certificate: dict[str, Any], generated_source: str):
    """Return immutable source-reported inventory only; proof_credit is always false."""
    normal = _freeze_shape(_find_vfmir(normal_text))
    readonly = _freeze_shape(_find_vfmir(readonly_text))
    if normal != readonly:
        raise InventoryError("normal and readonly VfMir compiler inventories differ")
    binding = _source_binding(case_id, source_certificate, generated_source, normal)
    return _freeze({"schema": "a1-compiler-inventory-observation-v1",
                    "provenance": "source-reported-compiler-inventory-only",
                    "proof_credit": False, "native_contract_credit": False,
                    "case_binding": binding, "inventory": normal})
