#!/usr/bin/env python3
"""Cloud-only selected Freeze branch diagnostic; inert on import."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re

HERE = Path("research/challenge-8/cloud-build/sort4-caller-entry-native")
REL = Path("research/challenge-8")
TR = Path("src/rust_frontend/vf_mir_translator/vf_mir_translator.ml")
PHASE = "SORT4-COMPILER-BINDING-PREFIX-CLOUD-2026-10-11"
SELECTED = {
    "selected-branch-positive": "selected_freeze_basecase",
    "selected-branch-false-bound-31": "selected_freeze_basecase_false_31",
    "selected-branch-missing-source-array": "selected_freeze_basecase_missing_source_array",
}
CONTROLS = ("canonical-generic", "canonical-mu", "consumer-positive",
            "consumer-wrong-pointer", "consumer-missing-raw-rights",
            "consumer-mu-cast-no-initialized-T", "threshold-body-positive")
SELECTED_LOCAL_MAPS = {
    "selected_freeze_basecase": {
        "normal": {
            "root": [
                "_17",
                "_18",
                "_19"
            ],
            "helper": [
                "_5",
                "_6",
                "_7"
            ]
        },
        "readonly": {
            "root": [
                "_16",
                "_17",
                "_18"
            ],
            "helper": [
                "_5",
                "_6",
                "_7"
            ]
        }
    },
    "selected_freeze_basecase_false_31": {
        "normal": {
            "root": [
                "_17",
                "_18",
                "_19"
            ],
            "helper": [
                "_5",
                "_6",
                "_7"
            ]
        },
        "readonly": {
            "root": [
                "_16",
                "_17",
                "_18"
            ],
            "helper": [
                "_5",
                "_6",
                "_7"
            ]
        }
    },
    "selected_freeze_basecase_missing_source_array": {
        "normal": {
            "root": [
                "_21",
                "_22",
                "_23"
            ],
            "helper": [
                "_5",
                "_6",
                "_7"
            ]
        },
        "readonly": {
            "root": [
                "_16",
                "_17",
                "_18"
            ],
            "helper": [
                "_5",
                "_6",
                "_7"
            ]
        }
    },
    "binding_selected_freeze": {
        "normal": {
            "root": [
                "_16",
                "_17",
                "_18"
            ],
            "helper": [
                "_5",
                "_6",
                "_7"
            ]
        },
        "readonly": {
            "root": [
                "_16",
                "_17",
                "_18"
            ],
            "helper": [
                "_5",
                "_6",
                "_7"
            ]
        }
    }
}


def need(ok: bool, why: str) -> None:
    if not ok:
        raise RuntimeError("SELECTED-PROOF: " + why)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def digest_or_none(path: Path) -> str | None:
    return sha(path) if path.is_file() else None


def validate_identity(expected: dict, observed: dict) -> None:
    need(set(observed) == set(expected), "complete evidence identity fields")
    for label, value in expected.items():
        need(observed[label] == value, "evidence identity: " + label)


def parse_capnp_record(source: str) -> dict:
    """Parse one bounded Cap'n Proto text function record, rejecting ambiguity."""
    import ast

    token = re.compile(r'\s*("(?:\\.|[^"\\])*"|[()\[\],=]|[^\s()\[\],=]+)')
    values = []
    at = 0
    while at < len(source):
        match = token.match(source, at)
        need(match is not None, "undecodable MIR text at byte " + str(at))
        values.append(match.group(1))
        at = match.end()
    index = 0

    def value():
        nonlocal index
        need(index < len(values), "truncated MIR text value")
        head = values[index]
        index += 1
        if head == "(":
            fields = {}
            while True:
                need(index < len(values), "unterminated MIR record")
                if values[index] == ")":
                    index += 1
                    return fields
                key = values[index]
                index += 1
                need(re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", key) is not None and
                     index < len(values) and values[index] == "=",
                     "invalid MIR field")
                index += 1
                need(key not in fields, "duplicate MIR field " + key)
                fields[key] = value()
                need(index < len(values), "unterminated MIR field " + key)
                if values[index] == ",":
                    index += 1
                else:
                    need(values[index] == ")", "invalid MIR field separator")
        if head == "[":
            items = []
            while True:
                need(index < len(values), "unterminated MIR list")
                if values[index] == "]":
                    index += 1
                    return items
                items.append(value())
                need(index < len(values), "unterminated MIR list item")
                if values[index] == ",":
                    index += 1
                else:
                    need(values[index] == "]", "invalid MIR list separator")
        need(head not in (")", "]", ",", "="), "unexpected MIR delimiter")
        if head.startswith('"'):
            decoded = ast.literal_eval(head)
            need(isinstance(decoded, str), "MIR string atom")
            return decoded
        if head in ("true", "false"):
            return head == "true"
        if re.fullmatch(r"-?[0-9]+", head):
            return int(head)
        return head

    result = value()
    need(index == len(values) and isinstance(result, dict),
         "complete single MIR function record")
    return result


def decoded_mir_functions(decoded: str) -> list[dict]:
    """Extract every complete function; this deliberately has no fuzzy match."""
    starts = list(re.finditer(r"(?m)^    \( defKind =", decoded))
    need(starts, "no complete MIR function records")
    records = []
    for start in starts:
        begin = decoded.index("(", start.start())
        depth = 0
        quoted = False
        escape = False
        end = None
        for offset in range(begin, len(decoded)):
            char = decoded[offset]
            if quoted:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    end = offset + 1
                    break
        need(end is not None, "unterminated MIR function")
        record = parse_capnp_record(decoded[begin:end])
        need(isinstance(record.get("defPath"), str) and
             isinstance(record.get("basicBlocks"), list) and
             isinstance(record.get("inputs"), list) and
             isinstance(record.get("localDecls"), list),
             "complete typed MIR function")
        records.append(record)
    return records


def _mir_param_arg(argument: dict, name: str) -> bool:
    return argument == {"kind": {"type": {"kind": {"param": name}}}}


def _mir_fnmut_pair(arguments: list, regions: list) -> bool:
    if len(arguments) != 2 or len(regions) != 2 or regions[0] == regions[1] or \
            not _mir_param_arg(arguments[0], "F"):
        return False
    try:
        pair = arguments[1]["kind"]["type"]["kind"]["tuple"]
        return len(pair) == 2 and all(
            item["kind"]["ref"] == {
                "region": {"id": region}, "ty": {"kind": {"param": "T"}},
                "mutability": {"not": "void"}}
            for item, region in zip(pair, regions))
    except (KeyError, TypeError):
        return False


def _mir_full_freeze_clauses(clauses: list) -> bool:
    """Mirror the selected translator's exact five-clause domain."""
    if not isinstance(clauses, list) or len(clauses) != 5:
        return False
    sized_t = {"trait": {"defId": "std::marker::Sized",
                         "args": [{"kind": {"type": {"kind": {"param": "T"}}}}],
                         "boundRegions": []}}
    sized_f = {"trait": {"defId": "std::marker::Sized",
                         "args": [{"kind": {"type": {"kind": {"param": "F"}}}}],
                         "boundRegions": []}}
    freeze_t = {"trait": {"defId": "FreezeMarker",
                          "args": [{"kind": {"type": {"kind": {"param": "T"}}}}],
                          "boundRegions": []}}
    front = clauses[:3]
    if front not in ([sized_t, sized_f, freeze_t],
                     [sized_t, freeze_t, sized_f]):
        return False
    fnmut, output = clauses[3:]
    try:
        trait = fnmut["trait"]
        projection = output["projection"]
        return (trait["defId"] == "std::ops::FnMut" and
                _mir_fnmut_pair(trait["args"], trait["boundRegions"]) and
                projection["projectionTerm"]["defId"] ==
                "std::ops::FnOnce::Output" and
                projection["boundRegions"] == trait["boundRegions"] and
                _mir_fnmut_pair(projection["projectionTerm"]["args"],
                                projection["boundRegions"]) and
                projection["term"] == {"ty": {"kind": {"bool": "void"}}})
    except (KeyError, TypeError):
        return False


def _mir_selected_impl_clauses(clauses: list) -> bool:
    return clauses == [
        {"trait": {"defId": "std::marker::Sized",
                   "args": [{"kind": {"type": {"kind": {"param": "T"}}}}],
                   "boundRegions": []}},
        {"trait": {"defId": "FreezeMarker",
                   "args": [{"kind": {"type": {"kind": {"param": "T"}}}}],
                   "boundRegions": []}}]


def _mir_method_clauses(clauses: list) -> bool:
    return _mir_full_freeze_clauses([
        {"trait": {"defId": "std::marker::Sized",
                   "args": [{"kind": {"type": {"kind": {"param": "T"}}}}],
                   "boundRegions": []}},
        {"trait": {"defId": "FreezeMarker",
                   "args": [{"kind": {"type": {"kind": {"param": "T"}}}}],
                   "boundRegions": []}}, *clauses])


def _mir_input_shape(body: dict, count: int) -> bool:
    inputs = body["inputs"]
    if len(inputs) != count:
        return False
    try:
        refs = [inputs[i]["kind"]["ref"] for i in
                ((0, 1, 4) if count == 5 else (0, 1, 2))]
        if not all(ref["mutability"] == {"mut": "void"} and
                   isinstance(ref["region"]["id"], str) for ref in refs):
            return False
        first = refs[0]["ty"] == {"kind": {"slice": {"kind": {"param": "T"}}}}
        scratch = refs[1]["ty"]["kind"]["slice"]["kind"]["adt"]
        second = (scratch["id"] == {"name": "std::mem::MaybeUninit"} and
                  scratch["kind"] == {"unionKind": "void"} and
                  scratch["substs"] ==
                  [{"kind": {"type": {"kind": {"param": "T"}}}}])
        comparator = refs[2]["ty"] == {"kind": {"param": "F"}}
        if count == 3:
            return first and second and comparator
        pivot = inputs[3]["kind"]["adt"]
        return (first and second and comparator and
                inputs[2] == {"kind": {"uInt": {"u32": "void"}}} and
                pivot["id"] == {"name": "std::option::Option"} and
                pivot["kind"] == {"enumKind": "void"} and
                len(pivot["substs"]) == 1 and
                pivot["substs"][0]["kind"]["type"]["kind"]["ref"]["ty"] ==
                {"kind": {"param": "T"}} and
                pivot["substs"][0]["kind"]["type"]["kind"]["ref"]["mutability"] ==
                {"not": "void"})
    except (KeyError, TypeError):
        return False


def _mir_source_line(text: str, needle: str, *, after: str = "") -> int:
    start = text.index(after) + len(after) if after else 0
    first = text.find(needle, start)
    need(first >= 0 and text.find(needle, first + 1) < 0,
         "unique MIR source anchor " + needle)
    return text[:first].count("\n") + 1


def _mir_call_shape(call: dict, name: str, argument_names: list[str],
                    source_line: int, body: dict, roots: dict[str, str],
                    expected_temporaries: list[str] | None = None) -> dict:
    fn_def = _mir_callee(call)
    need(fn_def["id"]["name"] == name and _mir_call_line(call) == source_line,
         "exact MIR callee and call source line " + name)
    expected = ([_mir_type_arg("T")] if not argument_names else
                [_mir_type_arg("T"), _mir_type_arg("F")])
    need(fn_def["substs"] == expected and
         fn_def["lateBoundGenericParamCount"] == (0 if not argument_names else 3) and
         len(call["args"]) == len(argument_names),
         "MIR FnDef T/F substitutions, three late-bound lifetimes and arity " + name)
    if argument_names:
        need(_mir_arg_source_roots(body, call, roots) == argument_names,
             "MIR operands derive from v, scratch, is_less in order " + name)
        need(expected_temporaries is not None and
             len(set(expected_temporaries)) == len(expected_temporaries),
             "selected call temporaries are unique " + name)
        need(expected_temporaries is not None and
             _mir_exact_reborrow_temporaries(
                 body, call, roots, expected_temporaries, argument_names),
             "exact direct MIR reborrow temporaries for translated AST " + name)
    source_locals = {source: local for local, source in roots.items()}
    return {"callee": name, "call_line": source_line,
            "fn_def_substs": ["T"] if not argument_names else ["T", "F"],
            "late_bound_generic_param_count": fn_def["lateBoundGenericParamCount"],
            "argument_source_roots": argument_names,
            "source_mir_locals": [source_locals[item] for item in argument_names],
            "argument_mir_locals": expected_temporaries or [],
            "argument_operand_shapes": [
                {"kind": next(iter(operand)),
                 "projection": next(iter(operand.values())).get("projection")}
                for operand in call["args"]]}


def _mir_type_arg(name: str) -> dict:
    return {"kind": {"type": {"kind": {"param": name}}}}


def _mir_selected_graph(functions: list[dict], source: str,
                        caller_name: str, *, query_fixture: bool,
                        expected_root_temporaries: list[str] | None = None,
                        expected_helper_temporaries: list[str] | None = None) -> dict:
    """Admit only the source-pinned selected caller, impl, and helper graph."""
    need(len(functions) == (9 if query_fixture else 4),
         "closed compiler binding MIR function inventory")
    by_path: dict[str, list[dict]] = {}
    for body in functions:
        by_path.setdefault(body["defPath"], []).append(body)
    caller = by_path.get(caller_name, [])
    helper = by_path.get("small_sort_general_with_scratch", [])
    methods = {method: by_path.get("<T as StableSmallSortTypeImpl>::" + method, [])
               for method in ("small_sort_threshold", "small_sort")}
    need(len(caller) == 1 and len(helper) == 1 and
         all(len(methods[name]) == (2 if query_fixture else 1) for name in methods),
         "selected MIR body inventory and both query impls")
    caller, helper = caller[0], helper[0]
    impl_start = "impl<T: FreezeMarker> StableSmallSortTypeImpl for T {"
    method_lines = {
        "small_sort_threshold": _mir_source_line(
            source, "fn small_sort_threshold() -> usize", after=impl_start),
        "small_sort": _mir_source_line(source, "fn small_sort<F:", after=impl_start)}
    selected = {}
    for method, candidates in methods.items():
        chosen = [body for body in candidates
                  if _mir_signature_line(body) == method_lines[method]]
        need(len(chosen) == 1 and
             _mir_selected_impl_clauses(chosen[0].get("implBlockClauses")) and
             (chosen[0]["clauses"] == [] if method == "small_sort_threshold" else
              _mir_method_clauses(chosen[0]["clauses"])),
             "exact selected impl body source line and clauses " + method)
        selected[method] = chosen[0]
    need(_mir_signature_line(caller) == _mir_source_line(
             source, "fn " + caller_name + "<") and
         _mir_full_freeze_clauses(caller["clauses"]) and
         _mir_input_shape(caller, 5),
         "exact selected caller source, full clauses and five typed inputs")
    need(_mir_signature_line(helper) == _mir_source_line(
             source, "fn small_sort_general_with_scratch<") and
         _mir_full_freeze_clauses(helper["clauses"]) and
         _mir_input_shape(helper, 3) and
         _mir_input_shape(selected["small_sort"], 3),
         "exact helper and selected method full typed signatures")
    root_expr = braced(source, "fn " + caller_name + "<")
    caller_start = source.index("fn " + caller_name + "<")
    def caller_call_line(expression: str) -> int:
        need(root_expr.count(expression) == 1, "unique selected source call " + expression)
        return source[:caller_start + root_expr.index(expression)].count("\n") + 1
    expected_calls = {
        "StableSmallSortTypeImpl::small_sort_threshold":
            caller_call_line("T::small_sort_threshold()"),
        "StableSmallSortTypeImpl::small_sort":
            caller_call_line("T::small_sort(v, scratch, is_less);")}
    need(root_expr.count("T::small_sort_threshold()") == 1 and
         root_expr.count("T::small_sort(v, scratch, is_less);") == 1,
         "one exact selected source call of each method")
    root_calls = [call for call in _mir_calls(caller)
                  if _mir_callee(call)["id"]["name"].startswith(
                      "StableSmallSortTypeImpl::")]
    need(len(root_calls) == 2 and
         {_mir_callee(call)["id"]["name"] for call in root_calls} ==
         set(expected_calls), "exact selected MIR trait call pair")
    need(expected_root_temporaries is not None and
         expected_helper_temporaries is not None,
         "case/mode exact MIR local map is required")
    root_records = []
    for call in root_calls:
        name = _mir_callee(call)["id"]["name"]
        args = [] if name.endswith("small_sort_threshold") else [
            "v", "scratch", "is_less"]
        root_records.append(_mir_call_shape(
            call, name, args, expected_calls[name], caller,
            {"_1": "v", "_2": "scratch", "_5": "is_less"},
            expected_root_temporaries if args else []))
    helper_name = "small_sort_general_with_scratch"
    helper_calls = [call for call in _mir_calls(selected["small_sort"])
                    if _mir_callee(call)["id"]["name"] == helper_name]
    need(len(helper_calls) == 1, "one selected method forwarding call")
    helper_call = _mir_call_shape(
        helper_calls[0], helper_name, ["v", "scratch", "is_less"],
        _mir_source_line(source, helper_name + "(v, scratch, is_less);"),
        selected["small_sort"], {"_1": "v", "_2": "scratch", "_3": "is_less"},
        expected_helper_temporaries)
    return {"caller": caller_name, "caller_line": _mir_signature_line(caller),
            "selected_method_lines": method_lines,
            "helper_line": _mir_signature_line(helper),
            "full_selected_caller_and_helper_clauses": True,
            "selected_impl_clauses": True,
            "input_shapes": "v:&mut[T],scratch:&mut[MaybeUninit<T>],is_less:&mut F",
            "calls": sorted(root_records, key=lambda item: item["callee"]) + [helper_call],
            "proof_credit": False}


def _mir_calls(body: dict) -> list[dict]:
    calls = []
    for block in body["basicBlocks"]:
        terminator = block.get("terminator", {}).get("kind", {})
        if "call" not in terminator:
            continue
        call = terminator["call"]
        need(isinstance(call, dict), "MIR call terminator shape")
        calls.append(call)
    return calls


def _mir_callee(call: dict) -> dict:
    try:
        fn_def = call["func"]["constant"]["const"]["val"]["ty"]["kind"]["fnDef"]
        need(set(fn_def) == {"id", "substs", "lateBoundGenericParamCount"} and
             isinstance(fn_def["id"]["name"], str) and
             isinstance(fn_def["substs"], list), "MIR FnDef shape")
        return fn_def
    except (KeyError, TypeError) as exc:
        raise RuntimeError("SELECTED-PROOF: unrecognized MIR call callee") from exc


def _mir_signature_line(body: dict) -> int:
    try:
        return body["fnSigSpan"]["regular"]["lo"]["line"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError("SELECTED-PROOF: MIR signature source line missing") from exc


def _mir_call_line(call: dict) -> int:
    try:
        return call["callSpan"]["regular"]["lo"]["line"]
    except (KeyError, TypeError) as exc:
        raise RuntimeError("SELECTED-PROOF: MIR call source line missing") from exc


def _mir_arg_source_roots(body: dict, call: dict,
                          input_roots: dict[str, str]) -> list[str]:
    """Admit only single-origin reference reborrows/copies of exact inputs."""
    assignments: dict[str, list[dict | None]] = {}
    for block in body["basicBlocks"]:
        for statement in block["statements"]:
            assignment = statement.get("kind", {}).get("assign")
            if assignment is None:
                continue
            lhs = assignment["lhsPlace"]
            need(lhs.get("projection") == [], "MIR assignment projection")
            local = lhs["local"]["name"]
            assignments.setdefault(local, []).append(assignment["rhsRvalue"])
        terminator_call = block.get("terminator", {}).get("kind", {}).get("call")
        if terminator_call is not None:
            destination = terminator_call["destination"]
            if destination.get("projection") == []:
                assignments.setdefault(destination["local"]["name"], []).append(None)
    need(not any(assignments.get(local) for local in input_roots),
         "MIR input reassigned before selected call")

    def place_root(place: dict, seen: set[str]) -> str:
        need(place.get("projection") in ([], [{"deref": "void"}]),
             "MIR operand projection outside direct reborrow")
        return local_root(place["local"]["name"], seen)

    def local_root(local: str, seen: set[str]) -> str:
        if local in input_roots:
            return input_roots[local]
        need(local not in seen, "cyclic MIR operand provenance")
        definitions = assignments.get(local, [])
        need(definitions and all(item is not None for item in definitions),
             "MIR operand has no direct source-input definition")
        origins = set()
        for definition in definitions:
            if "ref" in definition:
                reference = definition["ref"]
                need(reference.get("borKind") == {"mut": "void"} or
                     reference.get("borKind") == {"shared": "void"},
                     "MIR reborrow kind")
                origins.add(place_root(reference["place"], seen | {local}))
            elif "use" in definition:
                operand = definition["use"]
                need(set(operand) in ({"move"}, {"copy"}),
                     "MIR copy/move source")
                origins.add(place_root(next(iter(operand.values())), seen | {local}))
            else:
                need(False, "MIR operand derived by unsupported rvalue")
        need(len(origins) == 1, "ambiguous MIR operand source")
        return next(iter(origins))

    roots = []
    for operand in call["args"]:
        need(set(operand) in ({"move"}, {"copy"}),
             "MIR selected call argument is not a source place")
        roots.append(place_root(next(iter(operand.values())), set()))
    return roots


def _mir_exact_reborrow_temporaries(body: dict, call: dict,
                                    input_roots: dict[str, str],
                                    temporaries: list[str],
                                    expected_sources: list[str]) -> bool:
    """Match each moved call argument to exactly one `&mut *input` MIR write."""
    if len(call["args"]) != len(temporaries) or \
            len(temporaries) != len(expected_sources):
        return False
    source_locals = {name: local for local, name in input_roots.items()}
    for operand, temporary, source_name in zip(
            call["args"], temporaries, expected_sources):
        if operand != {"move": {"local": {"name": temporary},
                               "projection": [], "localIsMutable": True,
                               "kind": {"other": "void"}}}:
            # localIsMutable/kind are exporter metadata; direct move and
            # empty projection are the causal fields checked below.
            if set(operand) != {"move"} or \
                    operand["move"].get("local") != {"name": temporary} or \
                    operand["move"].get("projection") != []:
                return False
        assignments = [statement["kind"]["assign"]
                       for block in body["basicBlocks"]
                       for statement in block["statements"]
                       if "assign" in statement.get("kind", {}) and
                       statement["kind"]["assign"]["lhsPlace"].get("local") ==
                       {"name": temporary}]
        if len(assignments) != 1 or assignments[0]["lhsPlace"].get("projection") != []:
            return False
        reference = assignments[0]["rhsRvalue"].get("ref")
        if not isinstance(reference, dict) or \
                reference.get("borKind") != {"mut": "void"} or \
                reference.get("place", {}).get("local") != \
                {"name": source_locals[source_name]} or \
                reference["place"].get("projection") != [{"deref": "void"}]:
            return False
    return True


def full_mir_admission(mir_paths: dict[str, Path], source: str,
                       caller_name: str, *, query_fixture: bool,
                       expected_call_lines: dict[str, int] | None = None,
                       local_maps: dict[str, dict[str, list[str]]] | None = None) -> dict:
    """Admit the two complete, source-pinned MIR graphs before binding."""
    summaries = {}
    hashes = {}
    parsed = {}
    for mode in ("normal", "readonly"):
        path = mir_paths[mode]
        need(path.is_file() and path.stat().st_size > 0,
             mode + " complete decoded MIR missing")
        hashes[mode] = sha(path)
        functions = decoded_mir_functions(path.read_text(errors="strict"))
        parsed[mode] = functions
        need(local_maps is not None and mode in local_maps,
             mode + " exact selected MIR local map missing")
        maps = local_maps[mode]
        summaries[mode] = _mir_selected_graph(
            functions, source, caller_name, query_fixture=query_fixture,
            expected_root_temporaries=maps["root"],
            expected_helper_temporaries=maps["helper"])
        if expected_call_lines is not None:
            observed = {row["callee"].removeprefix("StableSmallSortTypeImpl::"):
                        row["call_line"] for row in summaries[mode]["calls"]
                        if row["callee"].startswith("StableSmallSortTypeImpl::")}
            need(observed == expected_call_lines,
                 mode + " MIR calls equal compiler-observed original callsites")
    def semantic_summary(summary: dict) -> dict:
        import copy
        normalized = copy.deepcopy(summary)
        for row in normalized["calls"]:
            # Numeric compiler locals are omitted only after the per-mode exact
            # local map and provenance checks above have succeeded.
            row.pop("argument_mir_locals")
        return normalized
    need(semantic_summary(summaries["normal"]) ==
         semantic_summary(summaries["readonly"]),
         "normal/readonly full MIR semantic clauses, substitutions and provenance")
    # The same admission predicate must reject changes to its causal fields.
    import copy
    baseline = parsed["normal"]
    controls = {}
    for name in ("missing-MIR-body", "missing-Freeze-clause",
                 "wrong-MIR-operand", "wrong-late-bound-lifetimes",
                 "wrong-original-argument-source", "wrong-move-projection",
                 "wrong-temporary-id", "missing-binder"):
        modified = list(baseline)
        if name == "missing-MIR-body":
            modified.pop()
        else:
            index = next(i for i, body in enumerate(modified)
                         if body["defPath"] == caller_name)
            modified[index] = copy.deepcopy(modified[index])
            caller = modified[index]
            if name == "missing-Freeze-clause":
                caller["clauses"] = [clause for clause in caller["clauses"]
                                     if clause.get("trait", {}).get("defId") !=
                                     "FreezeMarker"]
            elif name == "missing-binder":
                small_call = next(call for call in _mir_calls(caller)
                                  if _mir_callee(call)["id"]["name"] ==
                                  "StableSmallSortTypeImpl::small_sort")
                del _mir_callee(small_call)["lateBoundGenericParamCount"]
            else:
                small_call = next(call for call in _mir_calls(caller)
                                  if _mir_callee(call)["id"]["name"] ==
                                  "StableSmallSortTypeImpl::small_sort")
                if name == "wrong-MIR-operand":
                    next(iter(small_call["args"][2].values()))["local"]["name"] = "_2"
                elif name == "wrong-original-argument-source":
                    first_temp = local_maps["normal"]["root"][0]
                    first_assign = next(statement["kind"]["assign"]
                        for block in caller["basicBlocks"]
                        for statement in block["statements"]
                        if statement.get("kind", {}).get("assign", {})
                        .get("lhsPlace", {}).get("local", {}).get("name") == first_temp)
                    first_assign["rhsRvalue"]["ref"]["place"]["local"]["name"] = "_2"
                elif name == "wrong-move-projection":
                    small_call["args"][0]["move"]["projection"] = [{"deref": "void"}]
                elif name == "wrong-temporary-id":
                    small_call["args"][0]["move"]["local"]["name"] = "_999"
                else:
                    _mir_callee(small_call)["lateBoundGenericParamCount"] = 2
        try:
            _mir_selected_graph(modified, source, caller_name,
                                query_fixture=query_fixture,
                                expected_root_temporaries=local_maps["normal"]["root"],
                                expected_helper_temporaries=local_maps["normal"]["helper"])
            refused, reason = False, "structural MIR predicate unexpectedly accepted"
        except Exception as exc:
            refused, reason = True, str(exc)
        controls[name] = {"refused_before_verifier": refused,
                          "stage": "full_mir_structural_admission",
                          "reason": reason, "synthetic": True,
                          "proof_credit": False}
    need(all(row["refused_before_verifier"] for row in controls.values()),
         "full MIR structural negative controls")
    return {"mir_sha256": hashes, "structural_summary": summaries["normal"],
            "raw_per_mode_maps": local_maps,
            "per_mode_structural_summaries": summaries,
            "normal_readonly_semantic_equality": True,
            "negative_controls": controls,
            "complete_source_typed_graph": True, "proof_credit": False}


def semantic_mir_calls(graph: dict) -> list[dict]:
    """Normalize numeric locals after full per-case/per-mode map admission."""
    return [{key: row[key] for key in
             ("callee", "fn_def_substs", "late_bound_generic_param_count",
              "argument_source_roots", "source_mir_locals",
              "argument_operand_shapes")}
            for row in graph["calls"]]


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "module " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def braced(source: str, needle: str) -> str:
    need(source.count(needle) == 1, "unique source block " + needle)
    start = source.index(needle)
    open_brace = source.index("{", start)
    depth = 0
    for index in range(open_brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise RuntimeError("SELECTED-PROOF: unclosed source block " + needle)


def parenthesized(source: str, marker: str, before: int) -> str:
    start = source.rfind(marker, 0, before)
    need(start >= 0, "AST clause marker " + marker)
    opening = source.index("(", start + len(marker))
    depth = 0
    quoted = False
    escaped = False
    for index in range(opening, len(source)):
        char = source[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise RuntimeError("SELECTED-PROOF: unclosed AST clause " + marker)


def tokens(source: str, *, caller: bool = False) -> tuple[str, ...]:
    source = re.sub(r"/\*@.*?@\*/", "", source, flags=re.S)
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    source = re.sub(r"//[^\n]*", "", source)
    source = source.replace("#[inline(always)]", "")
    if caller:
        source = re.sub(r"\bfn\s+\w+", "fn CALLER", source, count=1)
    return tuple(re.findall(r"[A-Za-z_][A-Za-z_0-9]*|\d+|::|->|&&|<=|>=|\S", source))


def source_correspondence(a, manifest: dict, caller_driver, ghost) -> dict:
    template_path = a.proof_root / HERE / "selected-branch-cases.rs"
    query_path = a.proof_root / HERE / "compiler-binding-cases.rs"
    small_path = a.proof_root / "library/core/src/slice/sort/shared/smallsort.rs"
    quick_path = a.proof_root / "library/core/src/slice/sort/stable/quicksort.rs"
    need(sha(small_path) == manifest["actual_smallsort_source_sha256"] and
         sha(quick_path) == manifest["actual_quicksort_source_sha256"],
         "same-version std source")
    query_pins = json.loads((a.proof_root / HERE /
                             "COMPILER-SELECTED-INSTANCE-PINS.json").read_text())
    need(sha(query_path) == query_pins["fixture_sha256"], "same query fixture")
    template = template_path.read_text()
    query = query_path.read_text()
    small = small_path.read_text()
    need(set(re.findall(r"(?m)^// CASE_BEGIN ([^\s]+)$", template)) == set(SELECTED) and
         set(re.findall(r"(?m)^// CASE_END ([^\s]+)$", template)) == set(SELECTED),
         "closed selected case inventory")
    case_hashes = {}
    trait = braced(query, "pub(crate) trait StableSmallSortTypeImpl: Sized {")
    impl = braced(query, "impl<T: FreezeMarker> StableSmallSortTypeImpl for T {")
    caller = braced(query, "fn binding_selected_freeze<")
    marker_start = "#[unsafe(rustc_allow_lifetime_dependent_specialization)]"
    marker_end = "impl<T: Freeze> FreezeMarker for T {}"
    need(query.count(marker_start) == 1 and query.count(marker_end) == 1,
         "unique query FreezeMarker header")
    query_marker = query[query.index(marker_start):
                         query.index(marker_end) + len(marker_end)]
    helper = braced(small, "fn small_sort_general_with_scratch<")
    branch = "let presorted_len = if const { size_of::<T>() <= 16 } && len >= 16 {"
    need(helper.count(branch) == 1 and
         helper.count("} else if len >= 8 {") == 1 and
         helper.count("sort4_stable(v_base, scratch_base, is_less);") == 1,
         "actual helper branch order and first sort4 boundary")
    helper_prefix = helper[:helper.index(branch) + len(branch)]
    for case, target in SELECTED.items():
        source = caller_driver.case_source(template, case)
        original = ghost.strip_ghost(source.encode()).decode()
        case_hashes[case] = hashlib.md5(source.encode()).hexdigest()
        need(source.count(marker_start) == 1 and source.count(marker_end) == 1 and
             tokens(source[source.index(marker_start):
                           source.index(marker_end) + len(marker_end)]) ==
             tokens(query_marker), case + " exact FreezeMarker header")
        need(tokens(braced(source, "pub(crate) trait StableSmallSortTypeImpl: Sized {")) ==
             tokens(trait),
             case + " exact trait source correspondence")
        need(tokens(braced(source, "impl<T: FreezeMarker> StableSmallSortTypeImpl for T {")) ==
             tokens(impl), case + " selected method bodies source correspondence")
        need(tokens(braced(source, "fn " + target + "<"), caller=True) ==
             tokens(caller, caller=True), case + " caller signature/guard/operands correspondence")
        selected_helper = braced(source, "fn small_sort_general_with_scratch<")
        need(selected_helper.count(branch) == 1 and
             tokens(selected_helper[:selected_helper.index(branch) + len(branch)]) ==
             tokens(helper_prefix), case + " exact helper entry prefix")
        need(selected_helper.count("} else if len >= 8 {") == 1 and
             "sort4_stable(" not in original and
             "return;" in selected_helper,
             case + " diagnostic first-call cut")
        need(original.count("T::small_sort(v, scratch, is_less);") == 1 and
             original.count("T::small_sort_threshold()") == 1,
             case + " same original call operands")
    selected_pins = json.loads((a.proof_root / HERE /
                                "SELECTED-BRANCH-BINDING-PINS.json").read_text())
    need(case_hashes == selected_pins["case_verified_lib_md5"],
         "exact selected translator case MD5 inventory")
    cert = {"std_source_sha256": {"smallsort": sha(small_path),
                                  "quicksort": sha(quick_path)},
            "query_fixture_sha256": sha(query_path),
            "selected_template_sha256": sha(template_path),
            "case_verified_lib_md5": case_hashes,
            "FreezeMarker_header_matches_query_fixture": True,
            "trait_impl_and_caller_tokens_match_query_fixture": True,
            "helper_entry_prefix_matches_actual_std": True,
            "first_sort4_call_cut_explicit": True,
            "proof_credit": False}
    save(a.evidence / "selected-source-correspondence.json", cert)
    return cert


def exact_call_mapping(rows: list[dict], fixture_text: str, cert: dict) -> dict:
    names = ("binding_selected_freeze", "binding_fallback_cell",
             "binding_unconstrained_generic")
    methods = ("small_sort_threshold", "small_sort")
    expected_lines = {}
    for name in names:
        start = fixture_text.index("fn " + name + "<")
        body = braced(fixture_text, "fn " + name + "<")
        expected_lines[name] = {}
        for method, expression in ((methods[0], "T::small_sort_threshold()"),
                                   (methods[1], "T::small_sort(v, scratch, is_less)")):
            need(body.count(expression) == 1, "exact query callsite " + name + " " + method)
            expected_lines[name][method] = \
                fixture_text[:start + body.index(expression)].count("\n") + 1
    pairs = {}
    for row in rows:
        caller = next((name for name in names
                       if row["caller"] in (name, "lib::" + name)), None)
        method = next((name for name in methods
                       if row["callee"] in ("StableSmallSortTypeImpl::" + name,
                                           "lib::StableSmallSortTypeImpl::" + name)), None)
        need(caller is not None and method is not None,
             "exact original caller and trait callee DefPath")
        pair = (caller, method)
        need(pair not in pairs and
             row["caller_line"] == cert["caller_lines"][caller] and
             row["call_line"] == expected_lines[caller][method] and
             "verified/lib.rs" in row["caller_source_file"] and
             "verified/lib.rs" in row["call_source_file"],
             "exact original callsite line and source file")
        pairs[pair] = row
    need(set(pairs) == {(caller, method) for caller in names for method in methods},
         "six exact original callsites")
    original_ids = {}
    resolved_ids = {}
    for method in methods:
        ids = {pairs[name, method]["callee_def_id"] for name in names}
        need(len(ids) == 1 and next(iter(ids)), "one original trait DefId " + method)
        original_ids[method] = next(iter(ids))
        selected = pairs[names[0], method]["resolved_def_id"]
        fallback = pairs[names[1], method]["resolved_def_id"]
        need(selected and fallback and selected != fallback,
             "distinct selected/fallback compiler DefIds " + method)
        resolved_ids[method] = {"selected": selected, "fallback": fallback}
    return {"expected_call_lines": expected_lines,
            "original_trait_def_ids": original_ids,
            "resolved_method_def_ids": resolved_ids}


def compiler_gate(a, manifest: dict, query_result: dict) -> dict:
    need(os.environ.get("SMALLSORT_EXECUTION_PROVIDER") == "cloud-build" and
         os.environ.get("LANE") == "o26-sort4-c1-current-recovery" and
         os.environ.get("SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID") == PHASE and
         manifest["phase_id"] == PHASE and not os.environ.get("GITHUB_ACTIONS"),
         "exact Cloud phase/lane")
    need(query_result.get("selection_observation_complete") is True and
         query_result.get("binding_gate_open") is False and
         query_result.get("compiler_binding", {}).get("selected_pair_observed") is True and
         query_result["compiler_binding"].get("fallback_pair_observed") is True and
         query_result["compiler_binding"].get("unconstrained_not_selected") is True and
         query_result.get("proof_credit") is False,
         "fresh query selected/default/unconstrained observation")
    pins_path = a.proof_root / HERE / "COMPILER-SELECTED-INSTANCE-PINS.json"
    pins = json.loads(pins_path.read_text())
    query_module = a.cloud_dir / "sort4-caller-entry-native/compiler-query.py"
    audit_path = a.evidence / "diagnostic-audit.json"
    cert_path = a.evidence / "compiler-binding-source-certificate.json"
    version_path = a.evidence / "compiler-binding/compiler-version.log"
    tool_path = a.evidence / "compiler-binding-tool-identity.json"
    tool = json.loads(tool_path.read_text()) if tool_path.is_file() else {}
    log_paths = {mode: a.evidence / "compiler-binding" /
                 (mode + "-instance-query.log") for mode in ("normal", "readonly")}
    fixture_paths = {mode: a.evidence / "compiler-binding" /
                     (mode + "-fixture") for mode in ("normal", "readonly")}
    expected_identity = {
        "same_build_query_audit": query_result,
        "query_pins_sha256": manifest["compiler_query_pins_sha256"],
        "query_module_sha256": pins["query_module_sha256"],
        "source_certificate_sha256": query_result["source_certificate_sha256"],
        "compiler_commit_present": True,
        "production_head": pins["source_commit"],
        "production_exporter_sha256": pins["source_file_sha256"],
        "patched_exporter_sha256": pins["patched_file_sha256"],
        "exporter_patch_sha256": pins["patch_sha256"],
        "built_exporter_sha256": query_result["built_exporter_sha256"],
        "query_fixture_sha256": pins["fixture_sha256"],
    }
    observed_identity = {
        "same_build_query_audit": json.loads(audit_path.read_text())
        if audit_path.is_file() else None,
        "query_pins_sha256": digest_or_none(pins_path),
        "query_module_sha256": digest_or_none(query_module),
        "source_certificate_sha256": digest_or_none(cert_path),
        "compiler_commit_present": (pins["rustc_commit"] in
                                    version_path.read_text(errors="replace"))
        if version_path.is_file() else False,
        "production_head": tool.get("production_head"),
        "production_exporter_sha256": tool.get("production_exporter_sha256"),
        "patched_exporter_sha256": tool.get("patched_exporter_sha256"),
        "exporter_patch_sha256": tool.get("patch_sha256"),
        "built_exporter_sha256": digest_or_none(a.work_root /
            "sort4-compiler-binding-query-isolated-source/bin/vf-rust-mir-exporter"),
        "query_fixture_sha256": digest_or_none(a.proof_root / HERE / pins["fixture_file"]),
    }
    for mode in ("normal", "readonly"):
        expected_identity[mode + "_raw_log_sha256"] = \
            query_result["raw_exporter_log_sha256"][mode]
        observed_identity[mode + "_raw_log_sha256"] = digest_or_none(log_paths[mode])
        for side in ("verified", "original"):
            key = mode + "_" + side + "_fixture_sha256"
            expected_identity[key] = pins["fixture_sha256"]
            observed_identity[key] = digest_or_none(fixture_paths[mode] / side / "lib.rs")
    validate_identity(expected_identity, observed_identity)
    identity_controls = {}
    for name, key, value in (
        ("missing-entire-query-evidence", "same_build_query_audit", None),
        ("mismatched-raw-log-hash", "normal_raw_log_sha256", "0" * 64),
        ("mutated-source", "query_fixture_sha256", "0" * 64),
        ("wrong-exporter-source", "patched_exporter_sha256", "0" * 64),
        ("wrong-compiler-identity", "compiler_commit_present", False),
    ):
        changed = ({field: None for field in observed_identity}
                   if name == "missing-entire-query-evidence" else dict(observed_identity))
        if name != "missing-entire-query-evidence":
            changed[key] = value
        try:
            validate_identity(expected_identity, changed)
            refused, reason = False, "identity predicate unexpectedly accepted"
        except Exception as exc:
            refused, reason = True, str(exc)
        identity_controls[name] = {
            "refused_before_verifier": refused, "stage": "identity_admission",
            "predicate": key, "reason": reason, "synthetic": True,
            "proof_credit": False}
    need(all(row["refused_before_verifier"] for row in identity_controls.values()),
         "same identity predicate refuses synthetic evidence changes")
    query = load(query_module, "selected_proof_query_parser")
    _, cert = query.source_certificate(a, manifest, pins)
    need(json.loads(cert_path.read_text()) == cert,
         "fresh exact source certificate")
    record_path = a.evidence / "compiler-binding-records.json"
    saved = json.loads(record_path.read_text())
    fixture_text = (a.proof_root / HERE / pins["fixture_file"]).read_text()
    observations = {}
    exact_maps = {}
    for mode in ("normal", "readonly"):
        log = log_paths[mode]
        rows, finding = query.parse_records(log.read_text(errors="replace"), cert)
        need(rows == saved[mode] and
             rows == json.loads((a.evidence / "compiler-binding" /
                                 (mode + "-raw-records.json")).read_text()) and
             finding == query_result["compiler_binding"] and
             finding["selection_observation_complete"] is True,
             mode + " exact six source/impl/argument records")
        observations[mode] = rows
        exact_maps[mode] = exact_call_mapping(rows, fixture_text, cert)
    key_fields = ("caller_def_id", "caller_clauses", "typing_env", "callee_def_id",
                  "original_args", "argument_count", "resolution", "instance_kind",
                  "resolved_def_id", "resolved_args", "resolved_impl_id",
                  "resolved_line", "resolved_impl_line")
    def indexed(rows: list[dict]) -> dict:
        return {(row["caller"], row["callee"]):
                tuple(query.normalize_compiler_debug(row[field])
                      if field in ("caller_clauses", "typing_env") else row[field]
                      for field in key_fields) for row in rows}
    need(indexed(observations["normal"]) == indexed(observations["readonly"]),
         "normal/readonly compiler identities")
    need(exact_maps["normal"] == exact_maps["readonly"],
         "normal/readonly exact source-call and DefId mapping")
    mir_paths = {mode: a.evidence / "compiler-binding" / (mode + "-mir.txt")
                 for mode in ("normal", "readonly")}
    for mode in mir_paths:
        binary = a.evidence / "compiler-binding" / (mode + "-mir.bin")
        export_stage = json.loads((a.evidence / "compiler-binding" /
                                   (mode + "-instance-query-stage.json")).read_text())
        decode_stage = json.loads((a.evidence / "compiler-binding" /
                                   (mode + "-mir-decode-stage.json")).read_text())
        need(binary.is_file() and mir_paths[mode].is_file() and
             export_stage.get("exit") == 0 and
             export_stage.get("stdout_sha256") == sha(binary) and
             decode_stage.get("exit") == 0 and
             decode_stage.get("stdout_sha256") == sha(mir_paths[mode]) and
             decode_stage.get("argv", [])[:2] == ["capnp", "decode"],
             mode + " same-build exporter binary and full MIR decode identity")
    full_mir = full_mir_admission(
        mir_paths, fixture_text, "binding_selected_freeze", query_fixture=True,
        expected_call_lines=exact_maps["normal"]["expected_call_lines"][
            "binding_selected_freeze"],
        local_maps={mode: {"root": ["_16", "_17", "_18"],
                           "helper": ["_5", "_6", "_7"]}
                    for mode in ("normal", "readonly")})
    save(a.evidence / "compiler-binding-full-mir-admission.json", full_mir)
    baseline = observations["normal"]
    def synthetic_refusal(mutated: list[dict]) -> tuple[bool, str]:
        synthetic = "\n".join(query.MARKER + json.dumps(row) for row in mutated)
        try:
            _, finding = query.parse_records(synthetic, cert)
            if finding["selection_observation_complete"] is False:
                return True, "selection observation incomplete"
            exact_call_mapping(mutated, fixture_text, cert)
            return False, "exact mapping unexpectedly admitted"
        except Exception as exc:
            return True, str(exc)
    missing = [dict(row) for row in baseline[:-1]]
    wrong_impl = [dict(row) for row in baseline]
    selected_threshold = next(row for row in wrong_impl
                              if row["caller"].endswith("binding_selected_freeze") and
                              row["callee"].endswith("::small_sort_threshold"))
    selected_threshold["resolved_impl_line"] = cert["impl_line_regions"]["fallback"][0]
    wrong_callsite = [dict(row) for row in baseline]
    wrong_callsite[0]["call_line"] += 1
    wrong_callee = [dict(row) for row in baseline]
    wrong_callee[0]["callee"] = "Other::" + wrong_callee[0]["callee"]
    controls = {}
    for name, changed, predicate in (
        ("missing-record", missing, "six exact caller/method records"),
        ("wrong-impl", wrong_impl, "selected impl source line"),
        ("wrong-callsite", wrong_callsite, "exact original call line"),
        ("wrong-callee", wrong_callee, "exact original trait DefPath"),
    ):
        refused, reason = synthetic_refusal(changed)
        controls[name] = {"refused_before_verifier": refused,
                          "stage": "record_admission", "predicate": predicate,
                          "reason": reason, "synthetic": True,
                          "proof_credit": False}
    need(all(row["refused_before_verifier"] for row in controls.values()),
         "missing/wrong-impl/wrong-callsite/wrong-callee record controls")
    controls.update(identity_controls)
    save(a.evidence / "selected-admission-controls.json", controls)
    gate = {"same_build_query_audit_sha256": sha(a.evidence / "diagnostic-audit.json"),
            "query_pins_sha256": sha(pins_path),
            "source_certificate_sha256": sha(cert_path),
            "records_sha256": sha(record_path),
            "raw_log_sha256": query_result["raw_exporter_log_sha256"],
            "selected_pair_observed": True, "fallback_pair_observed": True,
            "unconstrained_not_selected": True,
            "exact_call_mapping": exact_maps["normal"],
            "full_mir_admission_sha256": sha(
                a.evidence / "compiler-binding-full-mir-admission.json"),
            "full_mir_sha256": full_mir["mir_sha256"],
            "full_mir_structural_summary": full_mir["structural_summary"],
            "admission_controls": controls,
            "full_structural_clause_and_operand_gate": True,
            "proof_credit": False}
    save(a.evidence / "selected-compiler-admission.json", gate)
    return gate


def selected_fixture_mir_gate(a, c4, tool: Path, env: dict,
                              fixture: Path, target: str,
                              query_graph: dict,
                              precomputed_support: tuple[dict, dict] | None = None) -> dict:
    """Check the actual selected consumer graph before its binding opt-in."""
    root = fixture.parent / "pre-binding"
    prior = {side: sha(fixture / side / "lib.rs")
             for side in ("verified", "original")}
    rows, support = (precomputed_support if precomputed_support is not None else
                     c4.source_support(a, tool, fixture, root, env, target=target))
    need(support.get("paired_support_passed") is True and
         all(rows[key].get("exit") == 0 for key in
             ("normal-export", "normal-decode", "readonly-export",
              "readonly-decode", "refinement")) and
         prior == {side: sha(fixture / side / "lib.rs")
                   for side in ("verified", "original")},
         target + " paired pre-binding exporter/refinement/source support")
    mir_paths = {mode: root / (mode + "-mir.txt")
                 for mode in ("normal", "readonly")}
    for mode in mir_paths:
        need(rows[mode + "-export"].get("stdout_sha256") ==
             sha(root / (mode + "-mir.bin")) and
             rows[mode + "-decode"].get("stdout_sha256") == sha(mir_paths[mode]),
             target + " exact pre-binding MIR binary/decode")
    source = (fixture / "verified/lib.rs").read_text()
    need(target in SELECTED_LOCAL_MAPS,
         target + " has no observed normal/readonly local map; admission remains closed")
    observed = full_mir_admission(
        mir_paths, source, target, query_fixture=False,
        local_maps=SELECTED_LOCAL_MAPS[target])
    need(semantic_mir_calls(observed["structural_summary"]) ==
         semantic_mir_calls(query_graph) and
         observed["structural_summary"]["full_selected_caller_and_helper_clauses"] and
         observed["structural_summary"]["selected_impl_clauses"] and
         observed["structural_summary"]["input_shapes"] ==
         query_graph["input_shapes"],
         target + " same source-selected method/helper clause, FnDef and operand graph")
    observed.update(source_pair_sha256=prior, query_graph_sha256=hashlib.sha256(
        json.dumps(query_graph, sort_keys=True).encode()).hexdigest(),
        paired_source_support=True, binding_gate_open=True)
    save(root / "selected-pre-binding-mir-admission.json", observed)
    return observed


def make_selected_fixture(a, caller_driver, ghost, template: str,
                          name: str, expected_md5: str) -> Path:
    source = caller_driver.case_source(template, name).encode()
    need(hashlib.md5(source).hexdigest() == expected_md5, name + " source MD5")
    original = ghost.strip_ghost(source)
    fixture = a.evidence / "cases" / name / "fixture"
    (fixture / "verified").mkdir(parents=True, exist_ok=False)
    (fixture / "original").mkdir()
    (fixture / "verified/lib.rs").write_bytes(source)
    (fixture / "original/lib.rs").write_bytes(original)
    save(fixture.parent / "source-certificate.json", {
        "case": name, "verified_sha256": sha(fixture / "verified/lib.rs"),
        "original_sha256": sha(fixture / "original/lib.rs"),
        "ghost_stripped_byte_identical": original == ghost.strip_ghost(source),
        "full_generated_posts_required": True, "proof_credit": False})
    return fixture


def _balanced_end(source: str, opening: int) -> int:
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack: list[str] = []
    quoted = False
    escaped = False
    for index in range(opening, len(source)):
        char = source[index]
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
            stack.append(pairs[char])
        elif char in ")]}":
            need(stack and stack[-1] == char, "balanced proof AST delimiters")
            stack.pop()
            if not stack:
                return index
    raise RuntimeError("SELECTED-PROOF: unclosed proof AST expression")


def _split_ast_fields(source: str, delimiter: str = ",") -> list[str]:
    fields: list[str] = []
    start = 0
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    quoted = False
    escaped = False
    for index, char in enumerate(source):
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
            stack.append(pairs[char])
        elif char in ")]}":
            need(stack and stack[-1] == char, "balanced proof AST fields")
            stack.pop()
        elif char == delimiter and not stack:
            fields.append(source[start:index].strip())
            start = index + 1
    fields.append(source[start:].strip())
    return fields


def _ast_list_items(value: str) -> list[str]:
    value = value.strip()
    need(value.startswith("[") and value.endswith("]"), "AST call argument list")
    contents = value[1:-1].strip()
    return [] if not contents else _split_ast_fields(contents, ";")


def _call_records(source: str) -> list[tuple[str, list[str]]]:
    records: list[tuple[str, list[str]]] = []
    for match in re.finditer(r"\bCallExpr\s*\(", source):
        opening = source.index("(", match.start())
        end = _balanced_end(source, opening)
        fields = _split_ast_fields(source[opening + 1:end])
        need(len(fields) == 6, "CallExpr field count")
        callee = fields[1]
        if callee.startswith('"') and callee.endswith('"'):
            records.append((callee[1:-1], _ast_list_items(fields[4])))
    return records


def _arg_source_name(argument: str) -> str | None:
    match = re.fullmatch(
        r'LitPat\s*\(\s*Var\s*\(\s*loc\s+"(?:[^"\\]|\\.)*"\s*,\s*"([A-Za-z_$][A-Za-z_0-9$]*)"\s*\)\s*\)',
        argument.strip())
    return match.group(1) if match else None


def audit_selected_callgraph(functions: dict[str, str],
                             operand_map: dict,
                             all_function_segments: list[str] | None = None) -> dict:
    expected_names = {"selected_freeze_basecase",
                      "sort4_selected_branch_threshold",
                      "sort4_selected_branch_small_sort",
                      "sort4_selected_branch_helper"}
    need(set(functions) == expected_names, "closed selected generated function set")
    need(isinstance(operand_map, dict) and
         set(operand_map) in ({"root", "helper"}, {"root", "helper", "fixture"}) and
         isinstance(operand_map["root"], list) and
         isinstance(operand_map["helper"], list) and
         ("fixture" not in operand_map or
          operand_map["fixture"] == "synthetic-callgraph-v1"),
         "explicit selected AST operand map; synthetic marker only for controls")
    need(len(operand_map["root"]) == 3 and len(set(operand_map["root"])) == 3 and
         all(re.fullmatch(r"\$[A-Za-z_][A-Za-z_0-9]*", name)
             for name in operand_map["root"]) and
         len(operand_map["helper"]) == 3 and len(set(operand_map["helper"])) == 3 and
         all(re.fullmatch(r"\$[A-Za-z_][A-Za-z_0-9]*", name)
             for name in operand_map["helper"]),
         "three explicit exact AST variable operands per selected edge")
    selected = "sort4_selected_branch_small_sort"
    helper = "sort4_selected_branch_helper"
    threshold = "sort4_selected_branch_threshold"
    expected = {
        "selected_freeze_basecase": {threshold: ([], 1), selected: (operand_map["root"], 1)},
        "sort4_selected_branch_threshold": {},
        selected: {helper: (operand_map["helper"], 1)},
        "sort4_selected_branch_helper": {},
    }
    all_selected_edges: list[tuple[str, str, list[str]]] = []
    per_owner: dict[str, dict[str, int]] = {}
    selected_targets = {threshold, selected, helper}
    unrenamed_targets = {
        "StableSmallSortTypeImpl::small_sort_threshold",
        "StableSmallSortTypeImpl::small_sort",
        "<T as StableSmallSortTypeImpl>::small_sort",
        "small_sort_general_with_scratch",
    }
    for owner, segment in functions.items():
        counts: dict[str, int] = {}
        for callee, arguments in _call_records(segment):
            need(callee not in unrenamed_targets,
                 "unrenamed selected call escaped binding: " + owner + " -> " + callee)
            if callee not in selected_targets:
                continue
            names = [_arg_source_name(argument) for argument in arguments]
            need(all(name is not None for name in names),
                 "selected call arguments must be direct exact AST vars")
            source_names = [name for name in names if name is not None]
            counts[callee] = counts.get(callee, 0) + 1
            all_selected_edges.append((owner, callee, source_names))
            expected_args, cardinality = expected[owner].get(callee, (None, 0))
            need(expected_args is not None and source_names == expected_args,
                 "selected call owner/operand provenance: " + owner + " -> " + callee)
            need(cardinality == 1, "selected call edge cardinality: " + owner + " -> " + callee)
        if owner in expected:
            expected_counts = {callee: edge[1]
                               for callee, edge in expected[owner].items()}
            need(counts == expected_counts,
                 "exact selected call graph cardinality for " + owner)
        per_owner[owner] = counts
    if all_function_segments is not None:
        selected_segments = set(functions.values())
        for segment in all_function_segments:
            if segment in selected_segments:
                continue
            for callee, _ in _call_records(segment):
                need(callee not in selected_targets | unrenamed_targets,
                     "selected edge escaped its exact owner function: " + callee)
    expected_edges = {
        ("selected_freeze_basecase", threshold, ()),
        ("selected_freeze_basecase", selected, tuple(operand_map["root"])),
        (selected, helper, tuple(operand_map["helper"])),
    }
    observed_edges = {(owner, callee, tuple(args))
                      for owner, callee, args in all_selected_edges}
    need(observed_edges == expected_edges and len(all_selected_edges) == 3,
         "no missing, duplicate, or unexpected selected call edges")
    return {"expected_edges": [
                {"owner": owner, "callee": callee, "args": list(args)}
                for owner, callee, args in sorted(expected_edges)],
            "observed_edges": [
                {"owner": owner, "callee": callee, "args": args}
                for owner, callee, args in sorted(all_selected_edges)],
            "per_owner_counts": per_owner,
            "operand_identity_level": "exact AST temporary IDs checked against admitted per-mode MIR source map",
            "complete": True,
            "proof_credit": False}


def _synthetic_callgraph_controls() -> dict:
    def call(name: str, args: tuple[str, ...]) -> str:
        rendered = "; ".join(
            f'LitPat (Var (loc "synthetic", "{arg}"))' for arg in args)
        return f'CallExpr (loc "synthetic", "{name}", [], [], [{rendered}], Static)'

    threshold = "sort4_selected_branch_threshold"
    selected = "sort4_selected_branch_small_sort"
    helper = "sort4_selected_branch_helper"
    baseline = {
        "selected_freeze_basecase": call(threshold, ()) + call(selected, ("$_16", "$_17", "$_18")),
        threshold: "",
        selected: call(helper, ("$_5", "$_6", "$_7")),
        helper: "",
    }
    mutations = {
        "missing-small-sort-edge": dict(baseline, selected_freeze_basecase=call(threshold, ())),
        "duplicate-helper-edge": dict(baseline, **{selected: baseline[selected] + baseline[selected]}),
        "wrong-helper-owner": dict(baseline, **{helper: call(helper, ("$_5", "$_6", "$_7"))}),
        "wrong-operand": dict(baseline, selected_freeze_basecase=
                               call(threshold, ()) + call(selected, ("$_9", "$_17", "$_18"))),
        "wrong-helper-local": dict(baseline, **{selected: call(helper, ("$_5", "$_99", "$_7"))}),
        "wrong-projection": dict(baseline, **{selected:
            f'CallExpr (loc "synthetic", "{helper}", [], [], '
            '[DerefExpr (LitPat (Var (loc "synthetic", "$_5"))); '
            'LitPat (Var (loc "synthetic", "$_6")); '
            'LitPat (Var (loc "synthetic", "$_7"))], Static)'}),
        "unrenamed-generic-fallback": dict(baseline, selected_freeze_basecase=
                               call("StableSmallSortTypeImpl::small_sort", ("$_16", "$_17", "$_18"))),
    }
    operand_map = {"root": ["$_16", "$_17", "$_18"],
                   "helper": ["$_5", "$_6", "$_7"],
                   "fixture": "synthetic-callgraph-v1"}
    audit_selected_callgraph(baseline, operand_map, list(baseline.values()))
    controls = {"baseline-shape-accepted": {
        "refused": False, "reason": "expected synthetic selected graph accepted",
        "synthetic": True, "proof_credit": False}}
    for name, mutated in mutations.items():
        try:
            audit_selected_callgraph(mutated, operand_map, list(mutated.values()))
            refused, reason = False, "synthetic call graph unexpectedly accepted"
        except Exception as exc:
            refused, reason = True, str(exc)
        controls[name] = {"refused": refused, "reason": reason,
                          "synthetic": True, "proof_credit": False}
    try:
        audit_selected_callgraph(
            baseline, operand_map,
            [*baseline.values(), call(selected, ("$_16", "$_17", "$_18"))])
        refused, reason = False, "synthetic out-of-owner edge unexpectedly accepted"
    except Exception as exc:
        refused, reason = True, str(exc)
    controls["edge-outside-owner-inventory"] = {
        "refused": refused, "reason": reason, "synthetic": True,
        "proof_credit": False}
    try:
        audit_selected_callgraph(baseline)
        refused, reason = False, "missing explicit operand map unexpectedly accepted"
    except Exception as exc:
        refused, reason = True, str(exc)
    controls["missing-explicit-operand-map"] = {
        "refused": refused, "reason": reason, "synthetic": True,
        "proof_credit": False}
    try:
        wrong_map = {**operand_map, "root": ["$_16", "$_16", "$_18"]}
        audit_selected_callgraph(baseline, wrong_map)
        refused, reason = False, "duplicate operand-map local unexpectedly accepted"
    except Exception as exc:
        refused, reason = True, str(exc)
    controls["duplicate-operand-map-local"] = {
        "refused": refused, "reason": reason, "synthetic": True,
        "proof_credit": False}
    def admitted(mode: str) -> dict:
        maps = SELECTED_LOCAL_MAPS["selected_freeze_basecase"]
        def row(callee: str, locals_: list[str], source_locals: list[str]) -> dict:
            return {"callee": callee, "argument_mir_locals": locals_,
                    "argument_source_roots": ["v", "scratch", "is_less"],
                    "source_mir_locals": source_locals,
                    "argument_operand_shapes": [{"kind": "move", "projection": []}] * 3}
        return {"binding_gate_open": True, "paired_source_support": True,
                "structural_summary": {"caller": "selected_freeze_basecase"},
                "raw_per_mode_maps": maps,
                "per_mode_structural_summaries": {
                    item: {"caller": "selected_freeze_basecase", "calls": [
                        row("StableSmallSortTypeImpl::small_sort",
                            maps[item]["root"], ["_1", "_2", "_5"]),
                        row("small_sort_general_with_scratch",
                            maps[item]["helper"], ["_1", "_2", "_3"])]}
                    for item in ("normal", "readonly")}}
    for mode in ("normal", "readonly"):
        mapped = _consumer_operand_map(admitted(mode), "selected-branch-positive",
                                       "selected_freeze_basecase", mode)
        expected_map = {"root": ["$" + item for item in
                                  SELECTED_LOCAL_MAPS["selected_freeze_basecase"][mode]["root"]],
                        "helper": ["$" + item for item in
                                    SELECTED_LOCAL_MAPS["selected_freeze_basecase"][mode]["helper"]]}
        need(mapped == expected_map, "synthetic explicit mode-to-AST operand mapping")
    bad_admission = admitted("normal")
    bad_admission["per_mode_structural_summaries"]["normal"]["calls"][0][
        "source_mir_locals"] = ["_2", "_1", "_5"]
    for label, selected_case, selected_target, selected_mode, certificate in (
        ("unobserved-translation-mode", "selected-branch-positive",
         "selected_freeze_basecase", "", admitted("normal")),
        ("wrong-case-certificate", "selected-branch-false-bound-31",
         "selected_freeze_basecase", "normal", admitted("normal")),
        ("wrong-MIR-source-map", "selected-branch-positive",
         "selected_freeze_basecase", "normal", bad_admission),
    ):
        try:
            _consumer_operand_map(certificate, selected_case, selected_target,
                                  selected_mode)
            refused, reason = False, "synthetic consumer map unexpectedly accepted"
        except Exception as exc:
            refused, reason = True, str(exc)
        controls[label] = {"refused": refused, "reason": reason,
                           "synthetic": True, "proof_credit": False}
    need(all(control["refused"] for name, control in controls.items()
             if name != "baseline-shape-accepted"),
         "synthetic selected-callgraph negative controls")
    return controls


def _consumer_operand_map(admission: dict, case: str, target: str,
                          observed_mode: str) -> dict:
    need(observed_mode in ("normal", "readonly"),
         "observed selected AST translation mode is explicitly pinned")
    need(case in SELECTED and SELECTED[case] == target and
         target in SELECTED_LOCAL_MAPS and
         admission.get("binding_gate_open") is True and
         admission.get("paired_source_support") is True and
         admission.get("structural_summary", {}).get("caller") == target,
         "selected consumer MIR admission certificate matches exact case/target")
    need(admission.get("raw_per_mode_maps") == SELECTED_LOCAL_MAPS[target],
         "consumer admission retains exact observed normal/readonly local maps")
    modes = admission.get("per_mode_structural_summaries")
    need(isinstance(modes, dict) and set(modes) == {"normal", "readonly"},
         "consumer admission includes both mode-specific structural summaries")
    for mode in ("normal", "readonly"):
        summary = modes[mode]
        need(summary.get("caller") == target,
             mode + " MIR structural summary caller identity")
        root_rows = [row for row in summary.get("calls", [])
                     if row.get("callee") == "StableSmallSortTypeImpl::small_sort"]
        helper_rows = [row for row in summary.get("calls", [])
                       if row.get("callee") == "small_sort_general_with_scratch"]
        need(len(root_rows) == 1 and len(helper_rows) == 1,
             mode + " MIR selected root/helper call uniqueness")
        root, helper = root_rows[0], helper_rows[0]
        need(root.get("argument_mir_locals") == SELECTED_LOCAL_MAPS[target][mode]["root"] and
             root.get("argument_source_roots") == ["v", "scratch", "is_less"] and
             root.get("source_mir_locals") == ["_1", "_2", "_5"] and
             root.get("argument_operand_shapes") == [
                 {"kind": "move", "projection": []}] * 3 and
             helper.get("argument_mir_locals") == SELECTED_LOCAL_MAPS[target][mode]["helper"] and
             helper.get("argument_source_roots") == ["v", "scratch", "is_less"] and
             helper.get("source_mir_locals") == ["_1", "_2", "_3"] and
             helper.get("argument_operand_shapes") == [
                 {"kind": "move", "projection": []}] * 3,
             mode + " MIR map/source roots/move operands agree with admission")
    expected = SELECTED_LOCAL_MAPS[target][observed_mode]
    return {"root": ["$" + local for local in expected["root"]],
            "helper": ["$" + local for local in expected["helper"]]}


def post_ast_audit(root: Path, result: dict, target: str, case: str,
                   observed_mode: str, consumer_admission: dict) -> dict:
    path = root / "proof-ast.ml"
    need(path.is_file() and sha(path) == result.get("proof_ast_sha256"),
         "captured exact selected proof AST")
    ast = path.read_text(errors="replace")
    starts = [match.start() for match in re.finditer(r"(?m)^\s*Func \(", ast)]
    need(starts, "proof AST function inventory")
    starts.append(len(ast))
    functions = [ast[starts[index]:starts[index + 1]]
                 for index in range(len(starts) - 1)]
    names = ("selected_freeze_basecase", "sort4_selected_branch_threshold",
             "sort4_selected_branch_small_sort", "sort4_selected_branch_helper")
    rows = {}
    function_segments = {}
    for name in names:
        matches = [segment for segment in functions
                   if re.search(r',\s*"' + re.escape(name) + r'"\s*,\s*\[',
                                segment.split("Some ((", 1)[0])]
        need(len(matches) == 1, "one selected generated function/post " + name)
        segment = matches[0]
        function_segments[name] = segment
        normal = 'SwitchExprClause' in segment and '"returning"' in segment
        unwind = 'SwitchExprClause' in segment and '"unwinding"' in segment
        need("fn_outcome" in segment and normal and unwind,
             "generated normal and unwind post retained: " + name)
        returning_clause = parenthesized(segment, "SwitchExprClause",
                                         segment.index('"returning"'))
        unwinding_clause = parenthesized(segment, "SwitchExprClause",
                                         segment.index('"unwinding"'))
        resources = ("thread_token",) if name == "sort4_selected_branch_threshold" else \
                    ("thread_token", "lifetime_token", "array", "own", "is_less")
        clause_counts = {kind: {resource: clause.count('"' + resource + '"')
                                for resource in resources}
                         for kind, clause in (("normal", returning_clause),
                                              ("unwind", unwinding_clause))}
        need(all(count >= 1 for row in clause_counts.values()
                 for count in row.values()),
             "native resource retained in each normal/unwind post: " + name)
        if name != "sort4_selected_branch_threshold":
            need("MaybeUninit" in returning_clause and
                 "MaybeUninit" in unwinding_clause,
                 "source/scratch/F/lifetime resources retained: " + name)
        rows[name] = {"function_ast_sha256": hashlib.sha256(segment.encode()).hexdigest(),
                      "normal_post_present": normal, "unwind_post_present": unwind,
                      "normal_post_sha256": hashlib.sha256(returning_clause.encode()).hexdigest(),
                      "unwind_post_sha256": hashlib.sha256(unwinding_clause.encode()).hexdigest(),
                      "post_resource_counts": clause_counts}
    operand_map = _consumer_operand_map(consumer_admission, case, target,
                                       observed_mode)
    callgraph = audit_selected_callgraph(function_segments, operand_map, functions)
    audit = {"proof_ast_sha256": sha(path), "functions": rows,
             "source_caller_target": target,
             "case": case, "observed_translation_mode": observed_mode,
             "admitted_operand_map": operand_map,
             "generated_caller_name": "selected_freeze_basecase",
             "callgraph": callgraph,
             "synthetic_callgraph_controls": _synthetic_callgraph_controls(),
             "normal_and_unwind_posts_present": True,
             "exact_post_equality_to_prepatch": "RAW_REVIEW_REQUIRED",
             "proof_credit": False}
    save(root / "selected-post-ast-audit.json", audit)
    return audit


def classify_selected(name: str, result: dict, fixture: Path) -> dict:
    source = (fixture / "verified/lib.rs").read_text()
    first = result.get("first_error") or ""
    lines = [int(value) for value in re.findall(r"verified/lib\.rs\((\d+),", first)]
    paired = result.get("support", {}).get("paired_support_passed") is True
    common = (paired and result.get("source_pair_immutable") is True and
              result.get("proof_ast_sha256") is not None and
              result.get("stages", {}).get("proof-ast-diagnostic") == 0)
    stage = result.get("first_causal_stage")
    exit_code = result.get("stages", {}).get("verification")
    if name == "selected-branch-positive":
        log = fixture.parent / "verification.log"
        verbose = log.read_text(errors="replace") if log.is_file() else ""
        passed = (common and stage == "NONE_OBSERVED" and exit_code == 0 and
                  "Leak check." in verbose and "0 errors found (" in verbose)
        label = "SELECTED_PREFIX_VF0_CANDIDATE_RAW_REVIEW_REQUIRED" if passed else \
                "SELECTED_PREFIX_FIRST_OBLIGATION_INCONCLUSIVE"
    elif name == "selected-branch-false-bound-31":
        intended = [i for i, line in enumerate(source.splitlines(), 1)
                    if "//@ assert len <= 31;" in line]
        passed = (common and stage == "verification" and exit_code not in (None, 0) and
                  len(intended) == 1 and intended[0] in lines and "Cannot prove" in first)
        label = "INTENDED_FALSE31_NEGATIVE_RAW_REVIEW_REQUIRED" if passed else \
                "FALSE31_FIRST_OBLIGATION_WRONG_OR_INCONCLUSIVE"
    else:
        intended = [i for i, line in enumerate(source.splitlines(), 1)
                    if "T::small_sort(v, scratch, is_less);" in line]
        passed = (common and stage == "verification" and exit_code not in (None, 0) and
                  len(intended) == 1 and intended[0] in lines and
                  "No matching heap chunks" in first and "array" in first)
        label = "INTENDED_SOURCE_ARRAY_NEGATIVE_RAW_REVIEW_REQUIRED" if passed else \
                "SOURCE_ARRAY_FIRST_OBLIGATION_WRONG_OR_INCONCLUSIVE"
    return {"classification": label, "gate_passed": passed,
            "first_causal_stage": stage, "first_error": first or None,
            "verifier_exit": exit_code, "paired_support_passed": paired,
            "intended_stage": ("verification" if name != "selected-branch-positive"
                               else "NONE_OBSERVED"),
            "intended_predicate": ({"selected-branch-positive":
                                    "full normal/unwind/free/leak/dead-code obligations",
                                    "selected-branch-false-bound-31": "len <= 31 assertion",
                                    "selected-branch-missing-source-array":
                                    "selected source array precondition"}[name]),
            "full_log_sha256": sha(fixture.parent / "verification.log")
            if (fixture.parent / "verification.log").is_file() else None,
            "proof_credit": False}


def run(a, c4, audit, manifest: dict, ghost, caller_driver, query_result: dict) -> dict:
    result = {"classification": "SELECTED_PROOF_NOT_RUN_OR_INCONCLUSIVE",
              "accepted": False, "verification_accepted": False,
              "diagnostic_complete": False, "binding_gate_open": False,
              "profile_accepted": False, "actual_caller_proved": False,
              "caller_bound_transfer_proved": False, "actual_sort4_proved": False,
              "proof_credit": False}
    try:
        gate = compiler_gate(a, manifest, query_result)
        cert = source_correspondence(a, manifest, caller_driver, ghost)
        selected_pins = json.loads((a.proof_root / HERE /
                                    "SELECTED-BRANCH-BINDING-PINS.json").read_text())
        threshold_pins = json.loads((a.proof_root / HERE /
                                     "STABLE-THRESHOLD-BINDING-PINS.json").read_text())
        need(selected_pins["phase_id"] == PHASE and
             selected_pins["profile_accepted"] is False and
             threshold_pins["profile_accepted"] is False and
             selected_pins["base_translator_sha256"] ==
             threshold_pins["result_translator_sha256"] and
             threshold_pins["base_translator_sha256"] ==
             manifest["as_mut_ptr_translator_sha256"],
             "exact selected/threshold/slice chain")
        tool, expected, production = caller_driver.reconstruct(
            a, c4, audit, manifest, os.environ.copy())
        env = c4.clean_env(a, tool)
        caller_driver.apply(a, c4, tool, env, "selected-slice-as-mut-ptr",
                            a.proof_root / REL / "caller-entry/verifast-slice-as-mut-ptr.patch",
                            manifest["as_mut_ptr_patch_sha256"], {str(TR)},
                            before={str(TR): manifest["c4_base_translator_sha256"]},
                            after={str(TR): manifest["as_mut_ptr_translator_sha256"]})
        caller_driver.apply(a, c4, tool, env, "selected-threshold-binding",
                            a.proof_root / HERE / "stable-threshold-binding.patch",
                            threshold_pins["patch_sha256"], {str(TR)},
                            before={str(TR): threshold_pins["base_translator_sha256"]},
                            after={str(TR): threshold_pins["result_translator_sha256"]})
        caller_driver.apply(a, c4, tool, env, "selected-branch-binding",
                            a.proof_root / HERE / "selected-branch-binding.patch",
                            selected_pins["patch_sha256"], {str(TR)},
                            before={str(TR): selected_pins["base_translator_sha256"]},
                            after={str(TR): selected_pins["result_translator_sha256"]})
        (tool / "bin/verifast").unlink(missing_ok=True)
        row = c4.stage(a, a.evidence / "selected-tool", "selected-console-build",
                       ["make", "-C", str(tool / "src"), "../bin/verifast",
                        "WITHOUT_LABLGTK=yes", "VERBOSE=yes"],
                       c4.clean_env(a, tool), 900, cwd=tool)
        need(row.get("exit") == 0, "selected final console build")
        final = audit.snapshot(tool, a.proof_root)
        need(final["critical"][str(TR)] == selected_pins["result_translator_sha256"] and
             all(final["critical"][key] == value for key, value in
                 expected["critical"].items() if key != str(TR)) and
             all(final["binaries"][key] == value for key, value in
                 expected["binaries"].items() if key != "bin/verifast") and
             final["modified_names"] == expected["modified_names"] and
             all(final["modified_hashes"][key] == value for key, value in
                 expected["modified_hashes"].items() if key != str(TR)) and
             final["effective_rsspec"] == expected["effective_rsspec"] and
             final["proof_std"] == expected["proof_std"] and
             final["head"] == expected["head"],
             "final profile differs beyond selected translator/console")
        save(a.evidence / "selected-effective-profile.json", final)
        base_env = c4.clean_env(a, tool)
        template = (a.proof_root / HERE / "selected-branch-cases.rs").read_text()
        if manifest.get("selected_capture_only") is True:
            captures = {}
            capture_names = manifest.get("selected_capture_cases")
            need(isinstance(capture_names, list) and capture_names and
                 len(capture_names) == len(set(capture_names)) and
                 set(capture_names) <= set(SELECTED),
                 "explicit distinct selected capture cases")
            for name in capture_names:
                target = SELECTED[name]
                fixture = make_selected_fixture(
                    a, caller_driver, ghost, template, name,
                    selected_pins["case_verified_lib_md5"][name])
                root = fixture.parent
                rows, support = c4.source_support(
                    a, tool, fixture, root / "pre-binding", base_env,
                    target=target)
                row = {"paired_support_passed": support.get("paired_support_passed") is True,
                       "source_support_sha256": sha(root / "pre-binding/source-support.json"),
                       "raw_mir_sha256": {mode: support.get("full_mir", {}).get(
                           mode, {}).get("sha256") for mode in ("normal", "readonly")},
                       "proof_credit": False}
                if support.get("paired_support_passed") is True:
                    try:
                        admission = selected_fixture_mir_gate(
                            a, c4, tool, base_env, fixture, target,
                            gate["full_mir_structural_summary"],
                            precomputed_support=(rows, support))
                        row.update(mir_admitted=True,
                                   admission_sha256=sha(root /
                                       "pre-binding/selected-pre-binding-mir-admission.json"))
                        need(selected_pins["patch_sha256"] == sha(
                                 a.proof_root / HERE / "selected-branch-binding.patch"),
                             "AST diagnostic requires the exact capture-stop translator")
                        selected_env = dict(base_env)
                        selected_env.update(SORT4_SELECTED_BRANCH_INTERFACE="1",
                                            SORT4_SELECTED_COMPILER_BINDING_VERIFIED="1",
                                            SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID=PHASE)
                        selected_env["SORT4_SELECTED_OPERAND_CAPTURE_ONLY"] = "1"
                        # The translator explicitly stops after operand observation,
                        # before binding/verification, independent of local numbers.
                        ast_stage = c4.stage(
                            a, root / "pre-binding", "proof-ast-diagnostic",
                            [str(tool / "bin/verifast"), "-dump_ast_with_locs",
                             "proof-ast.ml", "-rustc_args", "--edition 2021",
                             "verified/lib.rs"], selected_env, 90, cwd=fixture)
                        ast_log = root / "pre-binding/proof-ast-diagnostic.log"
                        ast_text = ast_log.read_text(errors="replace") if ast_log.is_file() else ""
                        marker = re.search(
                            r"SORT4-SELECTED-OPERAND-OBSERVATION: source=([0-9a-f]+) "
                            r"owner=([^ ]+) callee=([^ ]+) vars=([^\s]+)", ast_text)
                        observed_vars = marker.group(4).split(",") if marker else []
                        matching_modes = [mode for mode in ("normal", "readonly")
                            if observed_vars == ["$" + local for local in
                                SELECTED_LOCAL_MAPS[target][mode]["root"]]]
                        observed_mode = matching_modes[0] if len(matching_modes) == 1 else None
                        need(ast_stage.get("exit") not in (None, 0) and marker is not None and
                             marker.group(1) == selected_pins["case_verified_lib_md5"][name] and
                             marker.group(2) == target and
                             marker.group(3) == "StableSmallSortTypeImpl::small_sort" and
                             observed_mode is not None and
                             "capture-only stop before selected-call binding and verification"
                             in ast_text,
                             "pinned selected translator did not stop at expected operand refusal")
                        ast_path = fixture / "proof-ast.ml"
                        if ast_path.is_file():
                            import shutil
                            shutil.copy2(ast_path, root / "pre-binding/proof-ast.ml")
                        row["ast_diagnostic"] = {
                            "exit": ast_stage.get("exit"),
                            "expected_operand_refusal_observed": True,
                            "operand_observation": marker.group(0),
                            "observed_mode": observed_mode,
                            "raw_per_mode_local_maps": SELECTED_LOCAL_MAPS[target],
                            "log_sha256": digest_or_none(ast_log),
                            "ast_sha256": digest_or_none(root / "pre-binding/proof-ast.ml"),
                            "verification_invoked": False, "proof_credit": False}
                    except Exception as exc:
                        row.update(mir_admitted=False, admission_reason=str(exc),
                                   ast_diagnostic={"invoked": False,
                                                   "verification_invoked": False,
                                                   "proof_credit": False})
                else:
                    row.update(mir_admitted=False,
                               admission_reason="paired source support failed",
                               ast_diagnostic={"invoked": False,
                                               "verification_invoked": False,
                                               "proof_credit": False})
                captures[name] = row
            need(all(not item.get("ast_diagnostic", {}).get("verification_invoked", True)
                     for item in captures.values()),
                 "capture-only mode must not invoke verification")
            result.update(classification="SELECTED_MIR_CAPTURE_ONLY",
                          capture_only=True, selected_consumer_captures=captures,
                          diagnostic_complete=False, binding_gate_open=False,
                          verification_invoked=False, proof_credit=False)
            save(a.evidence / "selected-proof-audit.json", result)
            return result
        controls = {}
        for name in CONTROLS:
            fixture, _ = caller_driver.make_fixture(a, c4, ghost, manifest, name)
            controls[name] = caller_driver.verify_one(a, c4, tool, base_env, fixture, name)
        need(all(controls[name].get("gate_passed") is True for name in CONTROLS),
             "final-profile canonical T/MU, pointer and threshold body controls")
        cases = {}
        consumer_mir = {}
        for name, target in SELECTED.items():
            fixture = make_selected_fixture(a, caller_driver, ghost, template,
                                            name, selected_pins["case_verified_lib_md5"][name])
            root = fixture.parent
            consumer = selected_fixture_mir_gate(
                a, c4, tool, base_env, fixture, target,
                gate["full_mir_structural_summary"])
            consumer_mir[name] = {
                "admission_sha256": sha(root / "pre-binding/selected-pre-binding-mir-admission.json"),
                "normal_readonly_mir_sha256": consumer["mir_sha256"],
                "paired_source_support": True, "binding_gate_open": True}
            selected_env = dict(base_env)
            selected_env.update(SORT4_SELECTED_BRANCH_INTERFACE="1",
                                SORT4_SELECTED_COMPILER_BINDING_VERIFIED="1",
                                SORT4_ACTUAL_CALLER_ENTRY_PHASE_ID=PHASE)
            raw = c4.verify_case(a, tool, fixture, root, selected_env,
                                 target=target, ast=True,
                                 require_paired_support=False, verbosity=6)
            observed_mode = selected_pins.get("observed_translation_modes", {}).get(name)
            admission_path = root / "pre-binding/selected-pre-binding-mir-admission.json"
            consumer_admission = json.loads(admission_path.read_text())
            need(consumer_admission == consumer,
                 name + " on-disk consumer MIR admission certificate is unchanged")
            posts = post_ast_audit(root, raw, target, name, observed_mode,
                                   consumer_admission)
            row = classify_selected(name, raw, fixture)
            row["post_ast_sha256"] = posts["proof_ast_sha256"]
            row["normal_and_unwind_posts_present"] = posts[
                "normal_and_unwind_posts_present"]
            raw.update(row)
            save(root / "case-result.json", raw)
            cases[name] = row
        result.update(classification=("SELECTED_PREFIX_CANDIDATE_RAW_REVIEW_REQUIRED"
                                      if all(row["gate_passed"] for row in cases.values()) else
                                      "SELECTED_PREFIX_FIRST_OBLIGATION_OPEN"),
                      diagnostic_complete=True,
                      binding_gate_open=False,
                      compiler_gate=gate,
                      source_correspondence_sha256=sha(a.evidence / "selected-source-correspondence.json"),
                      final_translator_sha256=final["critical"][str(TR)],
                      final_console_sha256=final["binaries"]["bin/verifast"],
                      controls={name: {"classification": row.get("classification"),
                                      "gate_passed": row.get("gate_passed"),
                                      "first_error": row.get("first_error")}
                                for name, row in controls.items()},
                      selected_consumer_mir_admission=consumer_mir,
                      cases=cases)
        need(audit.snapshot(a.production_source, a.proof_root) == production,
             "production source unchanged")
    except Exception as exc:
        result["reason"] = str(exc)
    save(a.evidence / "selected-proof-audit.json", result)
    return result
