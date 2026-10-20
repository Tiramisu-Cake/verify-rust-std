"""Source-reported A1 caller-to-trait MIR binding; no proof credit."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

_SELECTED_PATH = Path(__file__).with_name("selected-proof.py")
_spec = importlib.util.spec_from_file_location("a1_selected_proof_mir_helpers", _SELECTED_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError("cannot load selected-proof decoded MIR helpers")
_selected = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _selected
_spec.loader.exec_module(_selected)

class CallBindingError(ValueError):
    """Caller MIR cannot be bound to the certified source callsites."""


CALL_BINDING_REGION_MAP_REFUSAL = "INPUT_REGION_ROLE_REFUSAL_OBSERVED"


def construct_common_binding_claim(call_binding, compiler_inventory):
    """Build the valid structure-only common-call claim from paired observations."""
    _need(isinstance(call_binding, Mapping) and isinstance(compiler_inventory, Mapping),
          "paired caller binding and compiler inventory observations are required")
    caller_binding = call_binding.get("binding")
    _need(isinstance(caller_binding, Mapping) and caller_binding.get("caller") == "quicksort",
          "common binding claim requires the original unrestricted quicksort caller")
    calls = [row for row in caller_binding.get("calls", ())
             if isinstance(row, Mapping) and row.get("callee") ==
             "StableSmallSortTypeImpl::small_sort"]
    _need(len(calls) == 1, "caller must have exactly one bound common small_sort call")
    inv = compiler_inventory.get("inventory")
    _need(isinstance(inv, Mapping) and inv.get("trait_def_id") == "StableSmallSortTypeImpl",
          "inventory does not identify the expected common trait")
    ids = inv.get("required_method_ids")
    _need(isinstance(ids, (tuple, list)), "inventory required-method identities are missing")
    matches = [identity for identity, name in ids
               if isinstance(identity, int) and name == "small_sort"]
    _need(len(matches) == 1, "inventory common required-method identity is ambiguous")
    row = calls[0]
    return {"schema": "a1-common-binding-claim-v1", "caller": "quicksort",
            "method": "small_sort", "call_line": row.get("call_line"),
            "callee": row.get("callee"), "substs": list(row.get("substs", ())),
            "late_bound_lifetime_count": row.get("late_bound_lifetime_count"),
            "argument_roots": list(row.get("argument_roots", ())),
            "argument_region_roles": [list(entry) for entry in
                                      row.get("argument_region_roles", ())],
            "compiler_trait_item_id": matches[0]}


def mutate_region_binding_claim(claim):
    """Return the N-region-swap admission control with v/scratch roles swapped."""
    _need(isinstance(claim, dict) and isinstance(claim.get("argument_region_roles"), list),
          "common binding claim has no positional input-region role map")
    result = dict(claim)
    result["argument_region_roles"] = [list(entry)
                                       for entry in claim["argument_region_roles"]]
    roles = result["argument_region_roles"]
    _need(len(roles) == 3 and all(isinstance(entry, list) and len(entry) == 3
                                  for entry in roles),
          "common binding claim input-region role map has unknown shape")
    roles[0][1:], roles[1][1:] = roles[1][1:], roles[0][1:]
    return result


def validate_common_binding_claim(call_binding, compiler_inventory, claim):
    """Admit an exact claim connecting an unrestricted caller to the common trait item.

    This is a source-reported representation gate. It grants no proof or native
    contract credit and deliberately accepts no impl selection or redirect.
    """
    expected_keys = {"schema", "caller", "method", "call_line", "callee",
                     "substs", "late_bound_lifetime_count", "argument_roots",
                     "argument_region_roles", "compiler_trait_item_id"}
    _need(isinstance(claim, dict) and set(claim) == expected_keys,
          "common binding claim must use the closed exact schema")
    _need(claim.get("schema") == "a1-common-binding-claim-v1",
          "common binding claim schema is unknown")
    _need(isinstance(call_binding, Mapping) and isinstance(compiler_inventory, Mapping),
          "paired caller binding and compiler inventory observations are required")
    _need(call_binding.get("schema") == "a1-call-binding-observation-v1" and
          call_binding.get("provenance") == "source-reported-MIR-call-binding-only" and
          call_binding.get("semantic_normal_readonly_equal") is True and
          call_binding.get("proof_credit") is False,
          "caller binding observation is not a paired source-reported observation")
    _need(compiler_inventory.get("schema") == "a1-compiler-inventory-observation-v1" and
          compiler_inventory.get("provenance") == "source-reported-compiler-inventory-only" and
          compiler_inventory.get("proof_credit") is False,
          "compiler inventory is not a source-reported inventory observation")
    call_pair = call_binding.get("case_binding")
    inventory_pair = compiler_inventory.get("case_binding")
    _need(isinstance(call_pair, Mapping) and isinstance(inventory_pair, Mapping) and
          call_pair.get("case_id") == inventory_pair.get("case_id") == "P1" and
          isinstance(call_pair.get("source_pair_id"), str) and
          call_pair.get("source_pair_id") == inventory_pair.get("source_pair_id"),
          "caller and compiler inventory are not bound to the same P1 source pair")
    caller_binding = call_binding.get("binding")
    _need(isinstance(caller_binding, Mapping) and caller_binding.get("caller") == "quicksort" and
          caller_binding.get("input_shape") == "unrestricted-original-T-F-FnMut-Output",
          "common binding claim requires the original unrestricted quicksort caller")
    calls = [row for row in caller_binding.get("calls", ())
             if isinstance(row, Mapping) and row.get("callee") ==
             "StableSmallSortTypeImpl::small_sort"]
    _need(len(calls) == 1, "caller must have exactly one bound common small_sort call")
    observed = calls[0]
    expected_claim = {
        "schema": "a1-common-binding-claim-v1",
        "caller": "quicksort",
        "method": "small_sort",
        "call_line": observed.get("call_line"),
        "callee": "StableSmallSortTypeImpl::small_sort",
        "substs": ["T", "F"],
        "late_bound_lifetime_count": 3,
        "argument_roots": ["v", "scratch", "is_less"],
    }
    _need(all(claim.get(key) == value for key, value in expected_claim.items()),
          "claim differs from the paired compiler caller MIR binding")
    expected_region_roles = [list(entry) for entry in observed.get("argument_region_roles", ())]
    _need(claim.get("argument_region_roles") == expected_region_roles,
          "claim input-region role map differs from compiler-derived call/input region map")
    inv = compiler_inventory.get("inventory")
    _need(isinstance(inv, Mapping) and inv.get("trait_def_id") == "StableSmallSortTypeImpl",
          "inventory does not identify the expected common trait")
    required_ids = inv.get("required_method_ids")
    _need(isinstance(required_ids, (tuple, list)), "inventory required-method identities are missing")
    named = {}
    for row in required_ids:
        _need(isinstance(row, (tuple, list)) and len(row) == 2 and
              isinstance(row[0], int) and row[0] > 0 and isinstance(row[1], str),
              "inventory required-method identity has an invalid shape")
        _need(row[1] not in named, "inventory required-method names are ambiguous")
        named[row[1]] = row[0]
    _need(set(named) == {"small_sort_threshold", "small_sort"} and
          claim["compiler_trait_item_id"] == named["small_sort"],
          "claim compiler item identity does not match the common required method")
    return _freeze({"schema": "a1-common-binding-observation-v1",
                    "provenance": "source-reported-common-call-and-item-binding-only",
                    "caller": "quicksort", "method": "small_sort",
                    "call_line": observed["call_line"],
                    "callee": observed["callee"], "substs": ("T", "F"),
                    "late_bound_lifetime_count": 3,
                    "argument_roots": ("v", "scratch", "is_less"),
                    "argument_region_roles": tuple(tuple(entry) for entry in
                                                    observed["argument_region_roles"]),
                    "required_method_ids": tuple(sorted((identity, name)
                                                         for name, identity in named.items())),
                    "compiler_trait_item_id": named["small_sort"],
                    "selected_impl_id": None, "proof_credit": False,
                    "native_contract_credit": False})


def _need(ok, why):
    if not ok:
        raise CallBindingError(why)


def _freeze(value):
    if isinstance(value, dict):
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(v) for v in value)
    return value


def _one_function(functions, path):
    matches = [row for row in functions if row.get("defPath") == path]
    _need(len(matches) == 1, f"expected one compiler MIR body for {path}")
    return matches[0]


def _debug_input_roots(body):
    wanted = ("v", "scratch", "is_less")
    found: dict[str, list[str]] = {name: [] for name in wanted}
    debug_names_by_local: dict[str, list[str]] = {}
    debug = body.get("varDebugInfo")
    _need(isinstance(debug, list), "MIR varDebugInfo list is required for input binding")
    for row in debug:
        _need(isinstance(row, dict), "MIR varDebugInfo entry must be a record")
        symbol = row.get("name")
        _need(isinstance(symbol, dict) and set(symbol) == {"name"} and
              isinstance(symbol["name"], str) and bool(symbol["name"]),
              "MIR varDebugInfo name must be a Symbol with nonempty Text name")
        name = symbol["name"]
        try:
            value = row["value"]
            if "const" in value:
                _need(set(value) == {"const"}, "unknown constant debug-value shape")
                continue
            _need(set(value) == {"place"}, "unknown debug-value union arm")
            place = value["place"]
            _need(place.get("projection") == [], "input debug place must be an unprojected local")
            local = place["local"]["name"]
        except (KeyError, TypeError) as exc:
            raise CallBindingError("source input debug entry is not a direct MIR local") from exc
        _need(isinstance(local, str) and local, "debug input local name is empty")
        debug_names_by_local.setdefault(local, []).append(name)
        if name in found:
            found[name].append(local)
    if any(len(found[name]) != 1 for name in wanted):
        raise CallBindingError("v, scratch, and is_less must each map to one debug local")
    locals_ = [found[name][0] for name in wanted]
    _need(len(set(locals_)) == 3, "source input names alias the same MIR local")
    roots = {local: name for name, local in ((n, found[n][0]) for n in wanted)}
    return roots, debug_names_by_local


def _input_region_ids(body):
    """Retain distinct source-input and FnMut binder regions, not just names."""
    inputs = body.get("inputs")
    _need(isinstance(inputs, list) and len(inputs) == 5,
          "caller input list is required for region binding")
    try:
        regions = [inputs[index]["kind"]["ref"]["region"]["id"] for index in (0, 1, 4)]
        pivot_ref = inputs[3]["kind"]["adt"]["substs"][0]["kind"]["type"]["kind"]["ref"]
        regions.append(pivot_ref["region"]["id"])
    except (KeyError, IndexError, TypeError) as exc:
        raise CallBindingError("caller reference input regions have unknown shape") from exc
    _need(all(isinstance(region, str) and region for region in regions) and
          len(set(regions)) == 4,
          "v, scratch, pivot, and is_less input regions must remain distinct")
    return tuple(regions)


def _argument_region_roles(call, input_regions):
    """Bind roots to observed caller-input region identities by signature position.

    These are caller formal-input regions only. MIR reborrow temporaries are
    erased in the exporter and no temporary lifetime is inferred here.
    """
    roots = call.get("argument_roots")
    _need(roots == ["v", "scratch", "is_less"] and len(input_regions) == 4,
          "small_sort roots cannot be bound to the caller input-region signature")
    return tuple((root, f"input_region_{position}", input_regions[position])
                 for position, root in enumerate(roots))


def _generic_names(body):
    rows = body.get("generics")
    _need(isinstance(rows, list), "caller compiler generic list is missing")
    names = []
    indexes = []
    defids = []
    for row in rows:
        _need(isinstance(row, dict) and row.get("kind") == {"type": "void"},
              "caller generic must be a compiler type parameter")
        name, index, def_index = row.get("name"), row.get("index"), row.get("defIndex")
        _need(isinstance(name, str) and isinstance(index, int) and isinstance(def_index, int)
              and index >= 0 and def_index > 0, "caller generic compiler identity is incomplete")
        names.append(name)
        indexes.append(index)
        defids.append(def_index)
    _need(names == ["T", "F"] and len(set(indexes)) == 2 and len(set(defids)) == 2,
          "caller compiler generics must be exactly distinct T and F")
    return tuple(names)


def _mir_body_span(body):
    try:
        span = body["span"]["regular"]
        points = {}
        for endpoint in ("lo", "hi"):
            loc = span[endpoint]
            filename = loc["file"]["name"]["real"]
            path = filename.get("localPath")
            if not isinstance(path, str):
                path = filename["remapped"]["virtualName"]
            line = loc["line"]
            column = loc["col"]["pos"]
            _need(isinstance(path, str) and isinstance(line, int) and line > 0 and
                  isinstance(column, int) and column >= 0,
                  "caller Body.span source location values are invalid")
            points[endpoint] = {"source_path": path, "line": line, "column": column}
        lo, hi = points["lo"], points["hi"]
        _need(lo["source_path"] == hi["source_path"] and
              (hi["line"], hi["column"]) >= (lo["line"], lo["column"]),
              "caller Body.span must be a regular ordered source span")
        return {"lo": lo, "hi": hi}
    except (KeyError, TypeError) as exc:
        raise CallBindingError("caller Body.span bounds are missing or unrecognized") from exc


def _caller_clauses(body, input_regions):
    clauses = body.get("clauses")
    _need(isinstance(clauses, list) and len(clauses) == 4,
          "caller must retain only T/F Sized and FnMut/Output source clauses")
    sized = []
    for clause in clauses[:2]:
        try:
            trait = clause["trait"]
            _need(trait["defId"] in ("std::marker::Sized", "core::marker::Sized") and
                  trait["boundRegions"] == [] and len(trait["args"]) == 1,
                  "caller has an unexpected type-bound clause")
            arg = trait["args"][0]
            _need(arg.get("kind", {}).get("type", {}).get("kind", {}).get("param") in ("T", "F"),
                  "caller Sized clause is not for T or F")
            sized.append(arg["kind"]["type"]["kind"]["param"])
        except (KeyError, TypeError, IndexError) as exc:
            raise CallBindingError("caller Sized clause has unknown shape") from exc
    _need(set(sized) == {"T", "F"} and len(sized) == 2,
          "caller must retain Sized for both original type parameters")
    fnmut, output = clauses[2:]
    try:
        fn = fnmut["trait"]
        _need(fn["defId"] == "std::ops::FnMut" and
              _selected._mir_fnmut_pair(fn["args"], fn["boundRegions"]),
              "caller FnMut clause differs from source signature")
        hrtb_regions = fn["boundRegions"]
        _need(isinstance(hrtb_regions, list) and len(hrtb_regions) == 2 and
              len(set(hrtb_regions)) == 2 and
              set(hrtb_regions).isdisjoint(input_regions),
              "FnMut HRTB regions must not merge with source input regions")
        projection = output["projection"]
        _need(projection["projectionTerm"]["defId"] == "std::ops::FnOnce::Output" and
              projection["boundRegions"] == fn["boundRegions"] and
              _selected._mir_fnmut_pair(projection["projectionTerm"]["args"],
                                        projection["boundRegions"]) and
              projection["term"] == {"ty": {"kind": {"bool": "void"}}},
              "caller FnOnce::Output clause differs from source signature")
    except (KeyError, TypeError) as exc:
        raise CallBindingError("caller FnMut/Output clause has unknown shape") from exc
    return clauses, tuple(hrtb_regions)


def _source_functions(case_id, certificate, source):
    if not isinstance(certificate, dict) or not isinstance(source, str):
        raise CallBindingError("source certificate and generated source are required")
    cases = certificate.get("cases")
    inventory = certificate.get("source_inventory")
    _need(isinstance(cases, dict) and case_id in cases and isinstance(inventory, dict),
          "source certificate lacks selected case or inventory")
    case = cases[case_id]
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    _need(case.get("generated_source_sha256") == digest and case.get("source_pair_id") == digest,
          "generated Rust source does not match case source hashes")
    items = inventory.get("items")
    _need(isinstance(items, dict) and isinstance(items.get("quicksort_signature"), dict),
          "source certificate lacks exact quicksort signature bytes")
    import base64
    try:
        original_signature = base64.b64decode(
            items["quicksort_signature"]["exact_bytes_base64"], validate=True).decode("utf-8")
    except (KeyError, ValueError, UnicodeError, TypeError) as exc:
        raise CallBindingError("source quicksort signature certificate is invalid") from exc
    _need(hashlib.sha256(original_signature.encode()).hexdigest() ==
          items["quicksort_signature"].get("sha256"),
          "source quicksort signature bytes/hash mismatch")
    observer_signature = original_signature.replace("pub fn quicksort<", "fn a1_guard_observer<", 1)
    _need(observer_signature != original_signature and
          source.count(observer_signature) == 1 and source.count(original_signature) == 1,
          "generated source must retain exact original quicksort plus item-name-only observer")
    expected_rename = "quicksort -> a1_guard_observer (diagnostic item-name-only rename)"
    _need(case.get("diagnostic_rename") == expected_rename,
          "source certificate does not record the expected observer rename")
    if case_id in ("P0c", "N-false31"):
        selected_caller = "a1_guard_observer"
    elif case_id == "P1":
        selected_caller = "quicksort"
    else:
        raise CallBindingError("call-binding gate only admits P0c, N-false31, and P1")
    return case, selected_caller


def _source_calls(source, caller_name):
    marker = f"fn {caller_name}<"
    _need(source.count(marker) == 1, f"expected one source function {caller_name}")
    try:
        block = _selected.braced(source, marker)
        start = source.index(marker)
    except Exception as exc:
        raise CallBindingError(f"cannot isolate source body {caller_name}") from exc
    threshold = "T::small_sort_threshold()"
    _need(block.count(threshold) == 1, "source caller must contain one threshold trait call")
    expressions = [("StableSmallSortTypeImpl::small_sort_threshold", threshold)]
    if caller_name == "quicksort":
        small = "T::small_sort(v, scratch, is_less);"
        _need(block.count(small) == 1, "original quicksort must retain one unrestricted small_sort call")
        expressions.append(("StableSmallSortTypeImpl::small_sort", small))
    else:
        _need("T::small_sort(" not in block,
              "P0 observer must stop before the small_sort call")
    return {name: source[:start + block.index(expr)].count("\n") + 1
            for name, expr in expressions}


def _calls_for(body, caller_name, expected_lines, roots, debug_names_by_local):
    calls = _selected._mir_calls(body)
    trait_calls = []
    for call in calls:
        name = _selected._mir_callee(call)["id"]["name"]
        if name.startswith("StableSmallSortTypeImpl::"):
            trait_calls.append((name, call))
    _need({name for name, _ in trait_calls} == set(expected_lines) and
          len(trait_calls) == len(expected_lines),
          f"{caller_name} MIR must have exactly its source-derived trait call set")
    observed = []
    for name, call in trait_calls:
        callee = _selected._mir_callee(call)
        expected_substs = [_selected._mir_type_arg("T")]
        expected_args = []
        expected_lifetimes = 0
        if name.endswith("::small_sort"):
            expected_substs.append(_selected._mir_type_arg("F"))
            expected_args = ["v", "scratch", "is_less"]
            expected_lifetimes = 3
        _need(callee["substs"] == expected_substs and
              callee["lateBoundGenericParamCount"] == expected_lifetimes,
              "MIR FnDef substitutions/late-bound lifetime count changed")
        _need(_selected._mir_call_line(call) == expected_lines[name],
              "MIR call source line differs from its function-scoped source expression")
        if expected_args:
            actual_roots = _selected._mir_arg_source_roots(body, call, roots)
            _need(actual_roots == expected_args,
                  "MIR small_sort arguments do not derive from v, scratch, is_less in order")
            temporaries = []
            for operand in call["args"]:
                _need(set(operand) == {"move"}, "MIR small_sort arguments must be direct moved locals")
                moved = operand["move"]
                _need(moved.get("projection") == [] and
                      isinstance(moved.get("local", {}).get("name"), str),
                      "MIR small_sort argument move must have an empty local projection")
                temporaries.append(moved["local"]["name"])
            _need(len(set(temporaries)) == 3 and
                  not any(debug_names_by_local.get(temp) for temp in temporaries),
                  "small_sort reborrow temporaries must be unique and unnamed in varDebugInfo")
            _need(_selected._mir_exact_reborrow_temporaries(
                      body, call, roots, temporaries, expected_args),
                  "MIR arguments must be exact direct reborrows from named source inputs")
        else:
            _need(call.get("args") == [], "threshold trait call unexpectedly has arguments")
        observed.append({"callee": name, "substs": ["T"] if not expected_args else ["T", "F"],
                         "late_bound_lifetime_count": expected_lifetimes,
                         "call_line": expected_lines[name], "argument_roots": expected_args,
                         "argument_mir_locals": temporaries if expected_args else [],
                         "expected_ast_arguments": ["$" + local for local in temporaries]
                         if expected_args else []})
    return tuple(sorted(observed, key=lambda row: row["callee"]))


def _analyze_functions(case_id, functions, certificate, source):
    case, caller_name = _source_functions(case_id, certificate, source)
    caller = _one_function(functions, caller_name)
    _need(_selected._mir_input_shape(caller, 5),
          "source caller must retain the original unrestricted five-input signature")
    generics = _generic_names(caller)
    input_regions = _input_region_ids(caller)
    clauses, hrtb_regions = _caller_clauses(caller, input_regions)
    expected_lines = _source_calls(source, caller_name)
    roots, debug_names_by_local = _debug_input_roots(caller)
    calls = _calls_for(caller, caller_name, expected_lines, roots, debug_names_by_local)
    for call in calls:
        if call["callee"] == "StableSmallSortTypeImpl::small_sort":
            call["argument_region_roles"] = _argument_region_roles(call, input_regions)
    return {"caller": caller_name, "compiler_generics": generics,
            "case_binding": {"case_id": case_id,
                             "source_pair_id": case["source_pair_id"],
                             "generated_source_sha256": case["generated_source_sha256"]},
            "mir_body_span": _mir_body_span(caller),
            "source_call_lines": tuple(sorted(expected_lines.items())),
            "input_regions": input_regions,
            "hrtb_regions": hrtb_regions,
            "calls": calls, "clauses": tuple(json.dumps(c, sort_keys=True) for c in clauses),
            "input_shape": "unrestricted-original-T-F-FnMut-Output", "proof_credit": False}


def observe(case_id: str, normal_decoded: str, readonly_decoded: str,
            source_certificate: dict[str, Any], generated_source: str):
    """Bind paired decoded caller MIRs to exact fixture source callsites."""
    try:
        normal_functions = _selected.decoded_mir_functions(normal_decoded)
        readonly_functions = _selected.decoded_mir_functions(readonly_decoded)
    except Exception as exc:
        raise CallBindingError(f"decoded MIR function parse failed: {exc}") from exc
    normal = _analyze_functions(case_id, normal_functions, source_certificate, generated_source)
    readonly = _analyze_functions(case_id, readonly_functions, source_certificate, generated_source)
    _need(normal["mir_body_span"] == readonly["mir_body_span"],
          "normal and readonly caller MIR Body.span bounds differ")
    def semantic(row):
        region_aliases = {region: f"input_region_{i}"
                          for i, region in enumerate(row["input_regions"])}
        region_aliases.update({region: f"hrtb_region_{i}"
                               for i, region in enumerate(row["hrtb_regions"])})
        def normalize(value):
            if isinstance(value, str):
                return region_aliases.get(value, value)
            if isinstance(value, list):
                return [normalize(item) for item in value]
            if isinstance(value, dict):
                return {key: normalize(item) for key, item in value.items()}
            return value
        calls = tuple(normalize({key: value for key, value in call.items()
                                 if key not in ("argument_mir_locals", "expected_ast_arguments")})
                      for call in row["calls"])
        normalized = {key: value for key, value in row.items()
                      if key not in ("calls", "input_regions", "hrtb_regions", "clauses")}
        normalized["calls"] = calls
        normalized["input_region_partition"] = tuple(region_aliases[x]
                                                       for x in row["input_regions"])
        normalized["hrtb_region_partition"] = tuple(region_aliases[x]
                                                      for x in row["hrtb_regions"])
        normalized["clauses"] = tuple(json.dumps(normalize(json.loads(clause)), sort_keys=True)
                                      for clause in row["clauses"])
        return normalized
    _need(semantic(normal) == semantic(readonly),
          "normal and readonly caller MIR semantic call bindings differ")
    return _freeze({"schema": "a1-call-binding-observation-v1",
                    "provenance": "source-reported-MIR-call-binding-only",
                    "proof_credit": False, "native_contract_credit": False,
                    "semantic_normal_readonly_equal": True,
                    "case_binding": normal["case_binding"],
                    "binding_by_mode": {"normal": normal, "readonly": readonly},
                    "binding": normal})
