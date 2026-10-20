"""Synthetic decoded-MIR controls for A1 source call binding."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

m = load("a1_call_binding_test", "a1-call-binding.py")


def generic(name, index):
    return {"name": name, "index": index, "defIndex": 100 + index,
            "kind": {"type": "void"}}


def type_arg(name):
    return {"kind": {"type": {"kind": {"param": name}}}}


def sized(name):
    return {"trait": {"defId": "std::marker::Sized", "args": [type_arg(name)], "boundRegions": []}}


def ref_arg(region, param="T"):
    return {"kind": {"type": {"kind": {"ref": {
        "region": {"id": region}, "ty": {"kind": {"param": param}},
        "mutability": {"not": "void"}}}}}}


def caller_clauses(extra=False, collapse=False):
    pair_regions = ["br1", "br1" if collapse else "br2"]
    def ty_ref(region):
        return {"kind": {"ref": {"region": {"id": region}, "ty": {"kind": {"param": "T"}},
                                 "mutability": {"not": "void"}}}}
    pair_arg = {"kind": {"type": {"kind": {"tuple": [ty_ref(pair_regions[0]), ty_ref(pair_regions[1])]}}}}
    fn_args = [type_arg("F"), pair_arg]
    clauses = [sized("T"), sized("F"),
               {"trait": {"defId": "std::ops::FnMut", "args": fn_args,
                          "boundRegions": pair_regions}},
               {"projection": {"projectionTerm": {"defId": "std::ops::FnOnce::Output",
                              "args": fn_args}, "boundRegions": pair_regions,
                              "term": {"ty": {"kind": {"bool": "void"}}}}}]
    if extra:
        clauses.append({"trait": {"defId": "FreezeMarker", "args": [type_arg("T")], "boundRegions": []}})
    return clauses


def input_types(collapse=False):
    mut = {"mut": "void"}
    def ref(region, ty):
        return {"kind": {"ref": {"region": {"id": region}, "mutability": mut, "ty": ty}}}
    t = {"kind": {"param": "T"}}
    maybe = {"kind": {"adt": {"id": {"name": "std::mem::MaybeUninit"},
                                "kind": {"unionKind": "void"}, "substs": [type_arg("T")]}}}
    option = {"kind": {"adt": {"id": {"name": "std::option::Option"},
                                 "kind": {"enumKind": "void"},
                                 "substs": [{"kind": {"type": {"kind": {"ref": {"region": {"id": "p"}, "mutability": {"not": "void"}, "ty": t}}}}}]}}}
    return [ref("a", {"kind": {"slice": {"kind": {"param": "T"}}}}),
            ref("a" if collapse else "b", {"kind": {"slice": maybe}}),
            {"kind": {"uInt": {"u32": "void"}}}, option,
            ref("c", {"kind": {"param": "F"}})]


def local(name):
    return {"name": name}


def place(name, projection=None):
    return {"local": local(name), "projection": projection or []}


def input_debug(mapping):
    return [{"name": {"name": name}, "value": {"place": place(local_name)}}
            for name, local_name in mapping.items()]


def source_location(line, column):
    return {"file": {"name": {"real": {"localPath": "verified/lib.rs"}}},
            "line": line, "col": {"pos": column}}


def body_span():
    return {"regular": {"lo": source_location(1, 0),
                         "hi": source_location(20, 1)}}


def fn_def(name, substs, late):
    return {"constant": {"const": {"val": {"ty": {"kind": {"fnDef": {
        "id": {"name": name}, "substs": [type_arg(x) for x in substs],
        "lateBoundGenericParamCount": late}}}}}}}


def call(name, substs, late, line, args):
    return {"func": fn_def(name, substs, late), "args": args,
            "callSpan": {"regular": {"lo": {"line": line}}},
            "destination": {"local": local("_result" + str(line)), "projection": []},
            "target": "bb1"}


def call_operand(name):
    return {"move": {"local": local(name), "projection": [],
                     "localIsMutable": True, "kind": {"other": "void"}}}


def reborrow_assignment(temp, input_local):
    return {"kind": {"assign": {
        "lhsPlace": place(temp),
        "rhsRvalue": {"ref": {"borKind": {"mut": "void"},
                                "place": place(input_local, [{"deref": "void"}])}}}}}


def body(name, line_map, mapping, *, wrong_callee=False, wrong_args=False,
         wrong_lifetimes=False, extra_clause=False, collapse_regions=False,
         named_temp=False, wrong_move_projection=False, locals_tag="normal"):
    caller_is_observer = name == "a1_guard_observer"
    threshold_name = "StableSmallSortTypeImpl::small_sort_threshold"
    small_name = "StableSmallSortTypeImpl::small_sort"
    if wrong_callee:
        threshold_name = "OtherTrait::small_sort_threshold"
    threshold_line = line_map[threshold_name if not wrong_callee else "StableSmallSortTypeImpl::small_sort_threshold"]
    calls = [call(threshold_name, ["T"], 0, threshold_line, [])]
    blocks = []
    if not caller_is_observer:
        small_line = line_map[small_name]
        temp_ids = ["_temp_v_" + locals_tag, "_temp_s_" + locals_tag, "_temp_f_" + locals_tag]
        input_names = [mapping["v"], mapping["scratch"], mapping["is_less"]]
        statements = [reborrow_assignment(t, root) for t, root in zip(temp_ids, input_names)]
        args = [call_operand(t) for t in temp_ids]
        if wrong_move_projection:
            args[0]["move"]["projection"] = [{"deref": "void"}]
        if wrong_args:
            args[0] = call_operand(temp_ids[1])
        lifetime_count = 2 if wrong_lifetimes else 3
        calls.append(call(small_name, ["T", "F"], lifetime_count, small_line, args))
        blocks.extend({"statements": statements[i:i+1], "terminator": {"kind": {"goto": {"target": "bb1"}}}}
                      for i in range(len(statements)))
    blocks.extend({"statements": [], "terminator": {"kind": {"call": item}}} for item in calls)
    debug_rows = input_debug(mapping)
    if named_temp and not caller_is_observer:
        debug_rows.append({"name": {"name": "named-temp"}, "value": {"place": place(temp_ids[0])}})
    return {"defKind": {"fn": "void"}, "defPath": name,
            "fnSigSpan": {"regular": {"lo": {"line": 1}}},
            "span": body_span(),
            "inputs": input_types(collapse_regions), "generics": [generic("T", 0), generic("F", 1)],
            "clauses": caller_clauses(extra_clause, collapse_regions), "varDebugInfo": debug_rows,
            "localDecls": [], "basicBlocks": blocks}


def capnp(value):
    if isinstance(value, dict):
        return "(" + ", ".join(f"{k} = {capnp(v)}" for k, v in value.items()) + ")"
    if isinstance(value, list):
        return "[" + ", ".join(capnp(v) for v in value) + "]"
    if isinstance(value, str):
        if value == "void":
            return "void"
        return json.dumps(value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def function_source(name, expressions):
    calls = "\n".join("    " + expr for expr in expressions)
    return f"fn {name}<T, F: FnMut(&T, &T) -> bool>(v: &mut [T], scratch: &mut [MaybeUninit<T>], len: u32, pivot: Option<&mut T>, is_less: &mut F) {{\n{calls}\n}}\n"


ORIGINAL_SIG = "pub fn quicksort<T, F: FnMut(&T, &T) -> bool>(v: &mut [T], scratch: &mut [MaybeUninit<T>], len: u32, pivot: Option<&mut T>, is_less: &mut F) {\n"
OBSERVER_SIG = ORIGINAL_SIG.replace("pub fn quicksort<", "fn a1_guard_observer<", 1)
SOURCE = (OBSERVER_SIG + "    let _ = T::small_sort_threshold();\n}\n" +
          ORIGINAL_SIG + "    let _ = T::small_sort_threshold();\n"
          "    T::small_sort(v, scratch, is_less);\n}\n")


def certificate():
    signature = ORIGINAL_SIG
    raw = signature.encode()
    digest = hashlib.sha256(SOURCE.encode()).hexdigest()
    return {"source_inventory": {"items": {"quicksort_signature": {
                "exact_bytes_base64": __import__("base64").b64encode(raw).decode(),
                "sha256": hashlib.sha256(raw).hexdigest()}}},
            "cases": {case: {"generated_source_sha256": digest,
                             "source_pair_id": digest,
                             "diagnostic_rename": "quicksort -> a1_guard_observer (diagnostic item-name-only rename)"}
                      for case in ("P0c", "N-false31", "P1")}}


def decoded(caller_name, *, wrong_callee=False, wrong_args=False,
            wrong_lifetimes=False, extra_clause=False, collapse_regions=False,
            named_temp=False, wrong_move_projection=False, tag="normal"):
    if caller_name == "a1_guard_observer":
        mapping = {"v": "_20" + tag, "scratch": "_21" + tag, "is_less": "_22" + tag}
        lines = {"StableSmallSortTypeImpl::small_sort_threshold": 2}
    else:
        mapping = {"v": "_30" + tag, "scratch": "_31" + tag, "is_less": "_32" + tag}
        lines = {"StableSmallSortTypeImpl::small_sort_threshold": 5,
                 "StableSmallSortTypeImpl::small_sort": 6}
    record = body(caller_name, lines, mapping, wrong_callee=wrong_callee,
                  wrong_args=wrong_args, wrong_lifetimes=wrong_lifetimes,
                  extra_clause=extra_clause, collapse_regions=collapse_regions,
                  named_temp=named_temp, wrong_move_projection=wrong_move_projection,
                  locals_tag=tag)
    return "    " + capnp(record).replace("(defKind =", "( defKind =", 1) + "\n"


def rename_region_ids(decoded_text, mapping):
    functions = m._selected.decoded_mir_functions(decoded_text)
    def visit(value):
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key == "region" and isinstance(item, dict):
                    region = dict(item)
                    region["id"] = mapping.get(region.get("id"), region.get("id"))
                    result[key] = visit(region)
                elif key == "boundRegions" and isinstance(item, list):
                    result[key] = [mapping.get(region, region) for region in item]
                else:
                    result[key] = visit(item)
            return result
        if isinstance(value, list):
            return [visit(item) for item in value]
        return value
    return "".join("    " + capnp(visit(row)).replace("(defKind =", "( defKind =", 1) + "\n"
                   for row in functions)


class CallBindingTests(unittest.TestCase):
    def test_observer_threshold_only_and_quicksort_pair(self):
        result = m.observe("P0c", decoded("a1_guard_observer") + decoded("quicksort"),
                           decoded("a1_guard_observer", tag="ro") + decoded("quicksort", tag="ro"),
                           certificate(), SOURCE)
        self.assertFalse(result["proof_credit"])
        caller = result["binding"]
        self.assertEqual(caller["caller"], "a1_guard_observer")
        self.assertEqual([row["callee"] for row in caller["calls"]],
                         ["StableSmallSortTypeImpl::small_sort_threshold"])

    def test_alpha_renamed_input_and_hrtb_regions_remain_equivalent(self):
        normal = decoded("a1_guard_observer")
        readonly = decoded("a1_guard_observer", tag="ro")
        normal = rename_region_ids(normal, {
            "a": "'__72", "b": "'__73", "p": "'__74", "c": "'__75",
            "br1": "'__70", "br2": "'__71"})
        readonly = rename_region_ids(readonly, {
            "a": "'__67", "b": "'__68", "p": "'__69", "c": "'__70",
            "br1": "'__65", "br2": "'__66"})
        result = m.observe("P0c", normal, readonly, certificate(), SOURCE)
        self.assertTrue(result["semantic_normal_readonly_equal"])

    def test_semantic_mismatch_diagnostic_names_exact_field_and_path(self):
        normal = {"caller": "quicksort", "calls": [{"call_line": 5}]}
        readonly = {"caller": "quicksort", "calls": [{"call_line": 6}]}
        normal_text = "normal decoded MIR private body"
        readonly_text = "readonly decoded MIR private body"
        message = m._semantic_mismatch_message(
            "P1", normal, readonly, normal_text, readonly_text)
        self.assertTrue(message.startswith(
            "normal and readonly caller MIR semantic call bindings differ; diagnostic="))
        diagnostic = json.loads(message.split("diagnostic=", 1)[1])
        self.assertEqual(diagnostic["case_id"], "P1")
        self.assertEqual(diagnostic["caller"], "quicksort")
        self.assertEqual(diagnostic["differing_fields"], ["calls"])
        self.assertEqual(diagnostic["first_differences"], [{
            "path": "/calls/0/call_line", "normal": "5", "readonly": "6"}])
        self.assertEqual(diagnostic["normal_decoded_sha256"],
                         hashlib.sha256(normal_text.encode()).hexdigest())
        self.assertEqual(diagnostic["readonly_decoded_sha256"],
                         hashlib.sha256(readonly_text.encode()).hexdigest())
        self.assertNotIn(normal_text, message)
        self.assertNotIn(readonly_text, message)

    def test_semantic_diagnostic_handles_missing_null_and_wrong_types(self):
        message = m._semantic_mismatch_message(
            "P1", {"caller": "quicksort", "nullable": None},
            {"caller": "quicksort"}, "n", "r")
        diagnostic = json.loads(message.split("diagnostic=", 1)[1])
        self.assertEqual(diagnostic["differing_fields"], ["nullable"])
        self.assertEqual(diagnostic["first_differences"], [{
            "path": "/nullable", "normal": "None", "readonly": "<missing>"}])
        wrong = m._semantic_mismatch_message("P1", None, [], "n", "r")
        wrong_diagnostic = json.loads(wrong.split("diagnostic=", 1)[1])
        self.assertEqual(wrong_diagnostic["differing_fields"], ["$"])
        self.assertEqual(wrong_diagnostic["first_differences"][0]["normal"], "None")

    def test_semantic_diagnostic_bounds_long_values_and_total_message(self):
        long_value = "distinct-private-value-" * 4000
        message = m._semantic_mismatch_message(
            "P1", {"caller": "quicksort", "clauses": [long_value]},
            {"caller": "quicksort", "clauses": ["readonly"]},
            "n" * 5000, "r" * 5000)
        self.assertLess(len(message), 3000)
        self.assertNotIn(long_value[:100], message)
        diagnostic = json.loads(message.split("diagnostic=", 1)[1])
        self.assertEqual(diagnostic["differing_fields"], ["clauses"])
        self.assertIn("sha256=", diagnostic["first_differences"][0]["normal"])
        self.assertEqual(len(diagnostic["normal_decoded_sha256"]), 64)

    def test_semantic_diagnostic_bounds_unicode_keys_and_deep_paths(self):
        field = "界" * 12000
        nested_normal, nested_readonly = {"leaf": 0}, {"leaf": 1}
        for index in range(80):
            nested_normal = {"層" * 80 + str(index): nested_normal}
            nested_readonly = {"層" * 80 + str(index): nested_readonly}
        message = m._semantic_mismatch_message(
            "P1", {"caller": "quicksort", field: nested_normal},
            {"caller": "quicksort", field: nested_readonly}, "normal", "readonly")
        self.assertLessEqual(len(message.encode("utf-8")), 3000)
        diagnostic = json.loads(message.split("diagnostic=", 1)[1])
        self.assertEqual(len(diagnostic["normal_decoded_sha256"]), 64)
        self.assertEqual(diagnostic["first_differences"][0]["note"], "bounded traversal")
        self.assertIn("sha256=", diagnostic["first_differences"][0]["path"])

    def test_observe_semantic_mismatch_reports_diagnostic_and_still_fails(self):
        normal = decoded("quicksort")
        row = body("quicksort", {"StableSmallSortTypeImpl::small_sort_threshold": 5,
                                  "StableSmallSortTypeImpl::small_sort": 6},
                   {"v": "_30ro", "scratch": "_31ro", "is_less": "_32ro"},
                   locals_tag="ro")
        row["clauses"][0], row["clauses"][1] = row["clauses"][1], row["clauses"][0]
        readonly = "    " + capnp(row).replace("(defKind =", "( defKind =", 1) + "\n"
        with self.assertRaises(m.CallBindingError) as caught:
            m.observe("P1", normal, readonly, certificate(), SOURCE)
        message = str(caught.exception)
        self.assertIn("normal and readonly caller MIR semantic call bindings differ", message)
        diagnostic = json.loads(message.split("diagnostic=", 1)[1])
        self.assertEqual(diagnostic["differing_fields"], ["clauses"])
        self.assertTrue(diagnostic["first_differences"][0]["path"].startswith("/clauses"))

    def test_p1_binds_both_original_quicksort_calls(self):
        result = m.observe("P1", decoded("quicksort"), decoded("quicksort", tag="ro"),
                           certificate(), SOURCE)
        self.assertEqual({row["callee"] for row in result["binding"]["calls"]},
                         {"StableSmallSortTypeImpl::small_sort_threshold",
                          "StableSmallSortTypeImpl::small_sort"})
        normal = next(row for row in result["binding_by_mode"]["normal"]["calls"]
                      if row["callee"].endswith("::small_sort"))
        readonly = next(row for row in result["binding_by_mode"]["readonly"]["calls"]
                        if row["callee"].endswith("::small_sort"))
        self.assertEqual(normal["expected_ast_arguments"],
                         ("$_temp_v_normal", "$_temp_s_normal", "$_temp_f_normal"))
        self.assertEqual(readonly["expected_ast_arguments"],
                         ("$_temp_v_ro", "$_temp_s_ro", "$_temp_f_ro"))
        self.assertEqual(result["binding_by_mode"]["normal"]["mir_body_span"],
                         result["binding_by_mode"]["readonly"]["mir_body_span"])
        self.assertEqual(result["binding"]["mir_body_span"]["lo"],
                         {"source_path": "verified/lib.rs", "line": 1, "column": 0})

    def test_common_binding_claim_accepts_exact_trait_item_identity(self):
        result = m.observe("P1", decoded("quicksort"), decoded("quicksort", tag="ro"),
                           certificate(), SOURCE)
        inventory = {"schema": "a1-compiler-inventory-observation-v1",
                     "provenance": "source-reported-compiler-inventory-only",
                     "proof_credit": False,
                     "case_binding": {"case_id": "P1",
                                      "source_pair_id": hashlib.sha256(SOURCE.encode()).hexdigest()},
                     "inventory": {"trait_def_id": "StableSmallSortTypeImpl",
                                   "required_method_ids": ((70, "small_sort_threshold"),
                                                           (71, "small_sort"))}}
        claim = m.construct_common_binding_claim(result, inventory)
        self.assertEqual(claim["argument_region_roles"], [
            ["v", "input_region_0", "a"],
            ["scratch", "input_region_1", "b"],
            ["is_less", "input_region_2", "c"],
        ])
        admitted = m.validate_common_binding_claim(result, inventory, claim)
        self.assertFalse(admitted["proof_credit"])
        self.assertFalse(admitted["native_contract_credit"])
        self.assertEqual(admitted["required_method_ids"],
                         ((70, "small_sort_threshold"), (71, "small_sort")))

    def test_common_binding_claim_rejects_swapped_input_region_roles(self):
        result = m.observe("P1", decoded("quicksort"), decoded("quicksort", tag="ro"),
                           certificate(), SOURCE)
        inventory = {"schema": "a1-compiler-inventory-observation-v1",
                     "provenance": "source-reported-compiler-inventory-only",
                     "proof_credit": False,
                     "case_binding": {"case_id": "P1",
                                      "source_pair_id": hashlib.sha256(SOURCE.encode()).hexdigest()},
                     "inventory": {"trait_def_id": "StableSmallSortTypeImpl",
                                   "required_method_ids": ((70, "small_sort_threshold"),
                                                           (71, "small_sort"))}}
        claim = m.construct_common_binding_claim(result, inventory)
        swapped = m.mutate_region_binding_claim(claim)
        with self.assertRaisesRegex(
                m.CallBindingError,
                "claim input-region role map differs from compiler-derived call/input region map"):
            m.validate_common_binding_claim(result, inventory, swapped)

    def test_common_binding_claim_rejects_redirect_or_wrong_item(self):
        result = m.observe("P1", decoded("quicksort"), decoded("quicksort", tag="ro"),
                           certificate(), SOURCE)
        inventory = {"schema": "a1-compiler-inventory-observation-v1",
                     "provenance": "source-reported-compiler-inventory-only", "proof_credit": False,
                     "case_binding": {"case_id": "P1",
                                      "source_pair_id": hashlib.sha256(SOURCE.encode()).hexdigest()},
                     "inventory": {"trait_def_id": "crate::StableSmallSortTypeImpl",
                                   "required_method_ids": ((70, "small_sort_threshold"),
                                                           (71, "small_sort"))}}
        base = {"schema": "a1-common-binding-claim-v1", "caller": "quicksort",
                "method": "small_sort", "call_line": 6,
                "callee": "StableSmallSortTypeImpl::small_sort",
                "substs": ["T", "F"], "late_bound_lifetime_count": 3,
                "argument_roots": ["v", "scratch", "is_less"],
                "compiler_trait_item_id": 71}
        redirected = dict(base, selected_impl_id=999)
        with self.assertRaises(m.CallBindingError):
            m.validate_common_binding_claim(result, inventory, redirected)
        wrong_item = dict(base, compiler_trait_item_id=999)
        with self.assertRaises(m.CallBindingError):
            m.validate_common_binding_claim(result, inventory, wrong_item)
        mismatched_pair = dict(inventory)
        mismatched_pair["case_binding"] = {"case_id": "P1", "source_pair_id": "0" * 64}
        with self.assertRaises(m.CallBindingError):
            m.validate_common_binding_claim(result, mismatched_pair, base)

    def test_common_binding_claim_rejects_dropped_f_and_wrong_line(self):
        result = m.observe("P1", decoded("quicksort"), decoded("quicksort", tag="ro"),
                           certificate(), SOURCE)
        inventory = {"schema": "a1-compiler-inventory-observation-v1",
                     "provenance": "source-reported-compiler-inventory-only", "proof_credit": False,
                     "case_binding": {"case_id": "P1",
                                      "source_pair_id": hashlib.sha256(SOURCE.encode()).hexdigest()},
                     "inventory": {"trait_def_id": "crate::StableSmallSortTypeImpl",
                                   "required_method_ids": ((70, "small_sort_threshold"),
                                                           (71, "small_sort"))}}
        base = {"schema": "a1-common-binding-claim-v1", "caller": "quicksort",
                "method": "small_sort", "call_line": 6,
                "callee": "StableSmallSortTypeImpl::small_sort",
                "substs": ["T", "F"], "late_bound_lifetime_count": 3,
                "argument_roots": ["v", "scratch", "is_less"],
                "compiler_trait_item_id": 71}
        for bad in (dict(base, substs=["T"]), dict(base, call_line=99)):
            with self.subTest(bad=bad):
                with self.assertRaises(m.CallBindingError):
                    m.validate_common_binding_claim(result, inventory, bad)

    def test_normal_readonly_body_span_mismatch_rejected(self):
        # Rebuild a valid Capnp record with only the readonly Body.span changed.
        row = body("quicksort", {"StableSmallSortTypeImpl::small_sort_threshold": 5,
                                  "StableSmallSortTypeImpl::small_sort": 6},
                   {"v": "_30ro", "scratch": "_31ro", "is_less": "_32ro"}, locals_tag="ro")
        row["span"]["regular"]["hi"] = source_location(21, 1)
        changed = "    " + capnp(row).replace("(defKind =", "( defKind =", 1) + "\n"
        with self.assertRaises(m.CallBindingError):
            m.observe("P1", decoded("quicksort"), changed, certificate(), SOURCE)

    def test_wrong_callee_rejected(self):
        with self.assertRaises(m.CallBindingError):
            m.observe("P0c", decoded("a1_guard_observer", wrong_callee=True),
                      decoded("a1_guard_observer", wrong_callee=True, tag="ro"),
                      certificate(), SOURCE)

    def test_wrong_argument_origin_rejected(self):
        with self.assertRaises(m.CallBindingError):
            m.observe("P1", decoded("quicksort", wrong_args=True),
                      decoded("quicksort", wrong_args=True, tag="ro"),
                      certificate(), SOURCE)

    def test_wrong_lifetime_count_rejected(self):
        with self.assertRaises(m.CallBindingError):
            m.observe("P1", decoded("quicksort", wrong_lifetimes=True),
                      decoded("quicksort", wrong_lifetimes=True, tag="ro"),
                      certificate(), SOURCE)

    def test_added_caller_clause_rejected(self):
        with self.assertRaises(m.CallBindingError):
            m.observe("P1", decoded("quicksort", extra_clause=True),
                      decoded("quicksort", extra_clause=True, tag="ro"),
                      certificate(), SOURCE)

    def test_collapsed_input_or_hrtb_regions_rejected(self):
        with self.assertRaises(m.CallBindingError):
            m.observe("P1", decoded("quicksort", collapse_regions=True),
                      decoded("quicksort", collapse_regions=True, tag="ro"),
                      certificate(), SOURCE)

    def test_wrong_move_projection_rejected(self):
        with self.assertRaises(m.CallBindingError):
            m.observe("P1", decoded("quicksort", wrong_move_projection=True),
                      decoded("quicksort", wrong_move_projection=True, tag="ro"),
                      certificate(), SOURCE)

    def test_debug_renamed_temporary_rejected(self):
        with self.assertRaises(m.CallBindingError):
            m.observe("P1", decoded("quicksort", named_temp=True),
                      decoded("quicksort", named_temp=True, tag="ro"),
                      certificate(), SOURCE)

    def test_normal_readonly_mismatch_rejected(self):
        with self.assertRaises(m.CallBindingError):
            m.observe("P1", decoded("quicksort"),
                      decoded("quicksort", wrong_lifetimes=True, tag="ro"),
                      certificate(), SOURCE)

class DebugSymbolControls(unittest.TestCase):
    def test_debug_name_malformed_shapes_fail_closed(self):
        for invalid in (None, "v", {}, {"name": 1}, {"name": ""},
                        {"name": {"name": "v"}}, {"name": "v", "extra": "v"}):
            rows = input_debug({"v": "_1", "scratch": "_2", "is_less": "_3"})
            rows[0]["name"] = invalid
            with self.subTest(invalid=invalid), self.assertRaises(m.CallBindingError):
                m._debug_input_roots({"varDebugInfo": rows})


if __name__ == "__main__":
    unittest.main()
