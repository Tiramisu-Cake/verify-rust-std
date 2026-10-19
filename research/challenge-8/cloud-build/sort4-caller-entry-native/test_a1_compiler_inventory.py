"""Synthetic-only tests for A1 compiler inventory admission."""
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

p = load("a1_inventory_test_parser", "a1-synthetic-inputs.py")
m = load("a1_compiler_inventory_test", "a1-compiler-inventory.py")


def span(path="verified/lib.rs", line=1, endline=None):
    endline = endline or line
    return f'(regular = (lo = (file = (name = (real = (localPath = "{path}"))), line = {line}, col = (pos = 0)), hi = (file = (name = (real = (localPath = "{path}"))), line = {endline}, col = (pos = 60))))'


def required(name, idx):
    base = f'name = "{name}", nameSpan = {span(line=1 if name == "small_sort_threshold" else 2)}, defId = "StableSmallSortTypeImpl::{name}", defIndex = {idx}, parentDefId = "StableSmallSortTypeImpl", parentDefIndex = 7, scopedRepresentation = true'
    if name != "small_sort":
        return f'({base})'
    def ty(kind):
        return f'(kind = {kind})'
    def param(value):
        return ty(f'(param = "{value}")')
    def ref(region, target, mut=True):
        return ty(f'(ref = (region = (id = "{region}"), ty = {target}, mutability = ({"mut" if mut else "not"} = void)))')
    def gtype(value):
        return f'(kind = (type = {value}))'
    inputs = [ref("a", ty('(slice = ' + param("tp_self") + ')')),
              ref("b", ty('(slice = (kind = (adt = (id = (name = "core::mem::MaybeUninit"), kind = (unionKind = void), substs = [' + gtype(param("tp_self")) + ']))))')),
              ref("c", param("tp_f"))]
    def fn_args(left, right):
        tuple_arg = gtype(ty('(tuple = [' + ref(left, param("tp_self"), False) + ', ' + ref(right, param("tp_self"), False) + '])'))
        return '[' + gtype(param("tp_f")) + ', ' + tuple_arg + ']'
    fnmut = f'(trait = (defId = "core::ops::FnMut", args = {fn_args("h20", "h21")}, boundRegions = ["h20", "h21"]))'
    projection = f'(projection = (projectionTerm = (defId = "core::ops::FnOnce::Output", args = {fn_args("h30", "h31")}), boundRegions = ["h30", "h31"], term = (ty = (kind = (bool = void)))))'
    clauses = [
        '(trait = (defId = "core::marker::Sized", args = [' + gtype(param("tp_f")) + '], boundRegions = []))',
        fnmut, projection]
    scoped = []
    for scope, names in (("sig", ("a", "b", "c")),
                         ("clause_1", ("h20", "h21")),
                         ("clause_2", ("h30", "h31"))):
        for position, alias in enumerate(names):
            scoped.append(f'(alias = "{alias}", scope = "{scope}", depth = 0, index = {position}, kind = "anon", elidedRole = {"true" if scope == "sig" else "false"})')
    parent = [
        '(trait = (defId = "core::marker::Sized", args = [' + gtype(param("tp_self")) + '], boundRegions = []))',
        '(trait = (defId = "StableSmallSortTypeImpl", args = [' + gtype(param("tp_self")) + '], boundRegions = []))']
    return f'({base}, typeParams = [(alias = "tp_self", name = "Self", index = 0, defIndex = 71), (alias = "tp_f", name = "F", index = 1, defIndex = 72)], generics = [(name = "F", index = 1, defIndex = 72)], lifetimeParams = ["a", "b", "c"], inputs = [{" , ".join(inputs)}], output = (kind = (tuple = [])), clauses = [{", ".join(clauses)}], parentClauses = [{", ".join(parent)}], scopedRegions = [{", ".join(scoped)}])'


def impl(identity, freeze=False, duplicate_item=False):
    def arg(name="T"):
        return f'(kind = (type = (kind = (param = "{name}"))))'
    def clause(name):
        trait_path = "FreezeMarker" if name == "FreezeMarker" else "core::marker::Sized"
        return f'(trait = (defId = "{trait_path}", args = [{arg()}], boundRegions = []))'
    gen_clause = ', clauses = [' + clause('Sized') + (', ' + clause('FreezeMarker') if freeze else '') + ']'
    threshold = identity * 10 + 1
    body_items = [
        f'(name = "small_sort_threshold", defId = "crate::{"freeze32" if freeze else "default16"}::small_sort_threshold", defIndex = {threshold})',
        f'(name = "small_sort", defId = "crate::{"freeze32" if freeze else "default16"}::small_sort", defIndex = {threshold + 1})',
    ]
    if duplicate_item:
        body_items.append(body_items[0])
    return (f'(ofTrait = "StableSmallSortTypeImpl", selfTy = "T", defIndex = {identity}, '
            f'generics = [(name = "T", kind = (type = void), index = 0, defIndex = {identity + 100})]{gen_clause}, '
            f'isUnsafe = false, isNegative = false, genArgs = [{arg()}], span = {span(line=9 if freeze else 3, endline=14 if freeze else 8)}, items = [{", ".join(body_items)}])')


def body(defindex, path, line, block_line, impl_generic_id=101, method_generic_id=201):
    extra = ""
    if path.endswith("::small_sort"):
        def ty(kind): return f'(kind = {kind})'
        def param(name): return ty(f'(param = "{name}")')
        def ref(region, inner, mut=True):
            return ty(f'(ref = (region = (id = "{region}"), ty = {inner}, mutability = ({"mut" if mut else "not"} = void)))')
        def gtype(value): return f'(kind = (type = {value}))'
        inputs = [ref("ia", ty('(slice = ' + param("T") + ')')),
                  ref("ib", ty('(slice = (kind = (adt = (id = (name = "core::mem::MaybeUninit"), kind = (unionKind = void), substs = [' + gtype(param("T")) + ']))))')),
                  ref("ic", param("F"))]
        def fn_args(a, b):
            tup = gtype(ty('(tuple = [' + ref(a, param("T"), False) + ', ' + ref(b, param("T"), False) + '])'))
            return '[' + gtype(param("F")) + ', ' + tup + ']'
        clauses = [
            '(trait = (defId = "core::marker::Sized", args = [' + gtype(param("F")) + '], boundRegions = []))',
            f'(trait = (defId = "core::ops::FnMut", args = {fn_args("ha", "hb")}, boundRegions = ["ha", "hb"]))',
            f'(projection = (projectionTerm = (defId = "core::ops::FnOnce::Output", args = {fn_args("oa", "ob")}), boundRegions = ["oa", "ob"], term = (ty = (kind = (bool = void)))))']
        extra = (', inputs = [' + ', '.join(inputs) + '], output = (kind = (tuple = [])), '
                 f'implBlockGenerics = [(name = "T", index = 0, defIndex = {impl_generic_id}, kind = (type = void))], '
                 f'generics = [(name = "F", index = 1, defIndex = {method_generic_id}, kind = (type = void))], '
                 'clauses = [' + ', '.join(clauses) + ']')
    return (f'(defIndex = {defindex}, defPath = "{path}", fnSigSpan = {span(line=line)}, span = {span(line=line)}, impSpan = {span(line=block_line)}{extra})')


def stream(freeze_marker=True, duplicate_impl_id=False, duplicate_body_id=False):
    i2 = 1 if duplicate_impl_id else 2
    id_thr1, id_small1 = 11, 12
    id_thr2, id_small2 = (11, 12) if duplicate_body_id else (21, 22)
    traits = f'(cons = (h = (name = "StableSmallSortTypeImpl", requiredFns = (cons = (h = {required("small_sort_threshold", 70)}, t = (cons = (h = {required("small_sort", 71)}, t = (nil = void)))))), t = (nil = void)))'
    impls = f'[{impl(1)}, {impl(i2, freeze=freeze_marker)}]'
    bodies = (f'[{body(id_thr1, "crate::default16::small_sort_threshold", 4, 5)}, '
              f'{body(id_small1, "crate::default16::small_sort", 6, 7, 101, 201)}, '
              f'{body(id_thr2, "crate::freeze32::small_sort_threshold", 10, 11)}, '
              f'{body(id_small2, "crate::freeze32::small_sort", 12, 13, 102, 202)}]')
    return f'(traits = {traits}, traitImpls = {impls}, bodies = {bodies})'


def valid_source():
    lines = [
        "fn small_sort_threshold() { let _pad = 0; }",
        "fn small_sort() { let _pad = 0; }",
        "impl<T> StableSmallSortTypeImpl for T {",
        "fn small_sort_threshold()",
        "{ /* threshold implementation block only */ }",
        "fn small_sort()",
        "{ /* sort implementation block only */ }",
        "}",
        "impl<T: FreezeMarker> StableSmallSortTypeImpl for T {",
        "fn small_sort_threshold()",
        "{ /* freeze threshold block only */ }",
        "fn small_sort()",
        "{ /* freeze sort block only */ }",
        "}",
    ]
    return "\n".join(line.ljust(60) for line in lines) + "\n"

def certificate(source):
    lines = source.splitlines()
    default_bytes = "\n".join(lines[2:8]).encode()
    freeze_bytes = "\n".join(lines[8:14]).encode()
    source_id = hashlib.sha256(json.dumps(
        {"source_commit": "test-commit", "source_pins": {"std.rs": "abc"}},
        sort_keys=True).encode()).hexdigest()
    digest = hashlib.sha256(source.encode()).hexdigest()
    return {"source_inventory": {"source_commit": "test-commit",
                                  "files": {"std.rs": {"sha256": "abc"}},
                                  "items": {
                                      "default_impl": {"sha256": hashlib.sha256(default_bytes).hexdigest(), "exact_bytes_base64": __import__("base64").b64encode(default_bytes).decode()},
                                      "freeze_impl": {"sha256": hashlib.sha256(freeze_bytes).hexdigest(), "exact_bytes_base64": __import__("base64").b64encode(freeze_bytes).decode()}
                                  }},
            "cases": {"P0a": {"source_id": source_id, "source_pair_id": digest,
                               "generated_source_sha256": digest, "source_file": "P0a.rs"}}}


class InventoryTests(unittest.TestCase):
    def test_observed_maybeuninit_union_record(self):
        # Minimal synthetic copy of the verified ADT structure, not actual MIR replay.
        for name in ("std::mem::MaybeUninit", "core::mem::MaybeUninit"):
            with self.subTest(name=name):
                value = f'(kind=(adt=(id=(name="{name}"),kind=(unionKind=void),substs=[(kind=(type=(kind=(param="__vf_req_t_16_0"))))])))'
                self.assertEqual(m._ty(m._parser.parse_records(value)[0]),
                    ("adt", "MaybeUninit", (("type", ("param", "__vf_req_t_16_0")),)))

    def test_maybeuninit_union_rejections_at_intended_checks(self):
        value = '(kind=(adt=(id=(name="std::mem::MaybeUninit"),kind=(unionKind=void),substs=[(kind=(type=(kind=(param="Self"))))])))'
        for old, new, message in (
            ("unionKind=void", "structKind=void", "compiler union ADT kind"),
            ("unionKind=void", "enumKind=void", "compiler union ADT kind"),
            ("unionKind=void", "unionKind=true", "compiler union ADT kind"),
            ("std::mem::MaybeUninit", "other::MaybeUninit", "unsupported ADT identity"),
            ('substs=[(kind=(type=(kind=(param="Self"))))]', 'substs=void', "ADT substitutions"),
            ('kind=(type=(kind=(param="Self")))', 'kind=(other=void)', "generic argument kind"),
        ):
            with self.subTest(new=new), self.assertRaisesRegex(m.InventoryError, message):
                m._ty(m._parser.parse_records(value.replace(old, new))[0])

    def test_required_small_sort_wrong_scratch_substitution(self):
        source = valid_source()
        text = stream().replace('param = "tp_self"', 'param = "tp_f"', 2)
        with self.assertRaisesRegex(m.InventoryError, "signature lost Self, F"):
            m.observe("P0a", text, text, certificate(source), source)

    def test_imp_span_binds_block_without_function_name(self):
        source = valid_source()
        result = m.observe("P0a", stream(), stream(), certificate(source), source)
        self.assertFalse(result["proof_credit"])
        self.assertFalse(result["native_contract_credit"])
        self.assertEqual({x["impl"] for x in result["inventory"]["impls"]}, {"default16", "freeze32"})
        required_small = result["inventory"]["required_small_sort"]
        self.assertEqual(required_small["ast_type_param_names"], ("Self", "F"))
        self.assertEqual(required_small["signature_regions"],
                         ("@input_0", "@input_1", "@input_2"))
        self.assertEqual(len(required_small["hrtb_regions"]), 2)
        self.assertEqual({x["impl"] for x in result["inventory"]["impl_small_sort_identities"]},
                         {"default16", "freeze32"})
        self.assertTrue(all(len(x["compiler_signature_digest"]) == 64
                            for x in result["inventory"]["impl_small_sort_identities"]))
        with self.assertRaises(TypeError):
            result["proof_credit"] = True

    def test_required_small_sort_lost_F_rejected(self):
        source = valid_source()
        text = stream().replace('name = "F", index = 1, defIndex = 72',
                                'name = "G", index = 1, defIndex = 72', 1)
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_required_small_sort_region_collapse_rejected(self):
        source = valid_source()
        text = stream().replace('lifetimeParams = ["a", "b", "c"]',
                                'lifetimeParams = ["a", "a", "c"]', 1)
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_required_small_sort_missing_output_clause_rejected(self):
        source = valid_source()
        text = stream()
        start = text.find(', (projection = (projectionTerm = (defId = "core::ops::FnOnce::Output"')
        self.assertGreaterEqual(start, 0)
        end = text.find('], parentClauses', start)
        self.assertGreater(end, start)
        malformed = text[:start] + text[end:]
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", malformed, malformed, certificate(source), source)

    def test_impl_small_sort_compiler_signature_substitution_rejected(self):
        source = valid_source()
        text = stream().replace('name = "T", index = 0, defIndex = 101',
                                'name = "U", index = 0, defIndex = 101', 1)
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_impl_small_sort_body_T_identity_must_match_trait_impl(self):
        source = valid_source()
        text = stream().replace('implBlockGenerics = [(name = "T", index = 0, defIndex = 102',
                                'implBlockGenerics = [(name = "T", index = 0, defIndex = 101', 1)
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_small_sort_rejects_wrong_compiler_defid_namespaces(self):
        source = valid_source()
        for needle, replacement in (
                ('name = "core::mem::MaybeUninit"', 'name = "evil::mem::MaybeUninit"'),
                ('defId = "core::ops::FnMut"', 'defId = "evil::ops::FnMut"'),
                ('defId = "StableSmallSortTypeImpl", args = [',
                 'defId = "evil::StableSmallSortTypeImpl", args = [')):
            text = stream().replace(needle, replacement, 1)
            with self.subTest(needle=needle), self.assertRaises(m.InventoryError):
                m.observe("P0a", text, text, certificate(source), source)

    def test_small_sort_rejects_qualified_root_trait_identity(self):
        source = valid_source()
        text = stream().replace('ofTrait = "StableSmallSortTypeImpl"',
                                'ofTrait = "evil::StableSmallSortTypeImpl"', 1)
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_wrong_freeze_applicability_rejected(self):
        text = stream(freeze_marker=False)
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(valid_source()), valid_source())

    def test_duplicate_impl_identity_rejected(self):
        text = stream(duplicate_impl_id=True)
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(valid_source()), valid_source())

    def test_duplicate_item_identity_rejected_by_body_binding(self):
        # The second impl reuses both item identities; inventory must fail closed.
        base = stream()
        # Replace second impl's compiler item IDs with the first impl's.
        text = base.replace('defIndex = 21', 'defIndex = 11').replace('defIndex = 22', 'defIndex = 12')
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(valid_source()), valid_source())

    def test_normal_readonly_mismatch_rejected(self):
        source = valid_source()
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", stream(), stream().replace('selfTy = "T"', 'selfTy = "U"', 1), certificate(source), source)

    def test_same_printed_path_does_not_override_numeric_identity(self):
        source = valid_source()
        text = stream().replace('defIndex = 11, defPath = "crate::default16::small_sort_threshold"',
                                'defIndex = 99, defPath = "crate::default16::small_sort_threshold"')
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_missing_body_rejected(self):
        source = valid_source()
        text = stream().replace(
            ", " + body(22, "crate::freeze32::small_sort", 12, 13, 102, 202), "")
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_source_certificate_hash_mismatch_rejected(self):
        source = valid_source()
        cert = certificate(source)
        cert["cases"]["P0a"]["generated_source_sha256"] = "0" * 64
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", stream(), stream(), cert, source)

    def test_package_filename_is_not_accepted_as_compiler_input_path(self):
        source = valid_source()
        text = stream().replace("verified/lib.rs", "P0a.rs")
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_unrelated_absolute_same_suffix_is_not_accepted(self):
        source = valid_source()
        text = stream().replace("verified/lib.rs", "/tmp/other-checkout/verified/lib.rs")
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_body_signature_from_other_impl_is_rejected(self):
        source = valid_source()
        text = stream().replace(
            f'defIndex = 11, defPath = "crate::default16::small_sort_threshold", fnSigSpan = {span(line=4)}, span = {span(line=4)}, impSpan = {span(line=5)}',
            f'defIndex = 11, defPath = "crate::default16::small_sort_threshold", fnSigSpan = {span(line=2)}, span = {span(line=2)}, impSpan = {span(line=5)}')
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_imp_span_from_other_impl_is_rejected(self):
        source = valid_source()
        text = stream().replace(
            f'defIndex = 11, defPath = "crate::default16::small_sort_threshold", fnSigSpan = {span(line=4)}, span = {span(line=4)}, impSpan = {span(line=5)}',
            f'defIndex = 11, defPath = "crate::default16::small_sort_threshold", fnSigSpan = {span(line=4)}, span = {span(line=4)}, impSpan = {span(line=11)}')
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_unexpected_impl_clause_rejected(self):
        source = valid_source()
        text = stream().replace("core::marker::Sized", "core::marker::Send", 1)
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)

    def test_unsafe_impl_rejected(self):
        source = valid_source()
        text = stream().replace("isUnsafe = false", "isUnsafe = true", 1)
        with self.assertRaises(m.InventoryError):
            m.observe("P0a", text, text, certificate(source), source)


if __name__ == "__main__":
    unittest.main()
