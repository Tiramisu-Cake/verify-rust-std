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
    return f'(name = "{name}", nameSpan = {span(line=1 if name == "small_sort_threshold" else 2)}, defId = "crate::StableSmallSortTypeImpl::{name}", defIndex = {idx}, parentDefId = "crate::StableSmallSortTypeImpl", parentDefIndex = 7, scopedRepresentation = true)'


def impl(identity, freeze=False, duplicate_item=False):
    def arg(name="T"):
        return f'(kind = (type = (kind = (param = "{name}"))))'
    def clause(name):
        trait_path = "crate::FreezeMarker" if name == "FreezeMarker" else "core::marker::Sized"
        return f'(trait = (defId = "{trait_path}", args = [{arg()}], boundRegions = []))'
    gen_clause = ', clauses = [' + clause('Sized') + (', ' + clause('FreezeMarker') if freeze else '') + ']'
    threshold = identity * 10 + 1
    body_items = [
        f'(name = "small_sort_threshold", defId = "crate::{"freeze32" if freeze else "default16"}::small_sort_threshold", defIndex = {threshold})',
        f'(name = "small_sort", defId = "crate::{"freeze32" if freeze else "default16"}::small_sort", defIndex = {threshold + 1})',
    ]
    if duplicate_item:
        body_items.append(body_items[0])
    return (f'(ofTrait = "crate::StableSmallSortTypeImpl", selfTy = "T", defIndex = {identity}, '
            f'generics = [(name = "T", kind = (type = void), index = 0, defIndex = {identity + 100})]{gen_clause}, '
            f'isUnsafe = false, isNegative = false, genArgs = [{arg()}], span = {span(line=9 if freeze else 3, endline=14 if freeze else 8)}, items = [{", ".join(body_items)}])')


def body(defindex, path, line, block_line):
    return (f'(defIndex = {defindex}, defPath = "{path}", fnSigSpan = {span(line=line)}, span = {span(line=line)}, impSpan = {span(line=block_line)})')


def stream(freeze_marker=True, duplicate_impl_id=False, duplicate_body_id=False):
    i2 = 1 if duplicate_impl_id else 2
    id_thr1, id_small1 = 11, 12
    id_thr2, id_small2 = (11, 12) if duplicate_body_id else (21, 22)
    traits = f'(cons = (h = (name = "StableSmallSortTypeImpl", requiredFns = (cons = (h = {required("small_sort_threshold", 70)}, t = (cons = (h = {required("small_sort", 71)}, t = (nil = void)))))), t = (nil = void)))'
    impls = f'[{impl(1)}, {impl(i2, freeze=freeze_marker)}]'
    bodies = (f'[{body(id_thr1, "crate::default16::small_sort_threshold", 4, 5)}, '
              f'{body(id_small1, "crate::default16::small_sort", 6, 7)}, '
              f'{body(id_thr2, "crate::freeze32::small_sort_threshold", 10, 11)}, '
              f'{body(id_small2, "crate::freeze32::small_sort", 12, 13)}]')
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
    def test_imp_span_binds_block_without_function_name(self):
        source = valid_source()
        result = m.observe("P0a", stream(), stream(), certificate(source), source)
        self.assertFalse(result["proof_credit"])
        self.assertFalse(result["native_contract_credit"])
        self.assertEqual({x["impl"] for x in result["inventory"]["impls"]}, {"default16", "freeze32"})
        with self.assertRaises(TypeError):
            result["proof_credit"] = True

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
            ", " + body(22, "crate::freeze32::small_sort", 12, 13), "")
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
