"""Synthetic controls for schema-scoped Body region alpha projection."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).parent

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fixture = load("a1_region_alpha_fixture", "test_a1_compiler_inventory.py")
m = load("a1_region_alpha_inventory", "a1-compiler-inventory.py")


def body_text(body_id):
    if body_id == 12:
        return fixture.body(12, "crate::default16::small_sort", 6, 7, 101, 201)
    if body_id == 22:
        return fixture.body(22, "crate::freeze32::small_sort", 12, 13, 102, 202)
    raise AssertionError("only verified small_sort bodies are in this test fixture")


def replace_body(stream, body_id, transform):
    marker = f'(defIndex = {body_id}, defPath = "'
    start = stream.index(marker)
    depth = 0
    quoted = False
    escaped = False
    end = None
    for position in range(start, len(stream)):
        char = stream[position]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                end = position + 1
                break
    assert end is not None
    before = stream[start:end]
    return stream[:start] + transform(before) + stream[end:]


def rename_regions(body, mapping):
    for old, new in mapping.items():
        body = body.replace(f'"{old}"', f'"{new}"')
    return body


def stream_with_alpha(*, same_labels=False):
    stream = fixture.stream()
    for body_id, prefix in ((12, "default"), (22, "freeze")):
        names = {"ia": f"{prefix}_i0", "ib": f"{prefix}_i1",
                 "ic": f"{prefix}_i2", "ha": f"{prefix}_h0",
                 "hb": f"{prefix}_h1", "oa": f"{prefix}_h0" if same_labels else f"{prefix}_o0",
                 "ob": f"{prefix}_h1" if same_labels else f"{prefix}_o1"}
        stream = replace_body(stream, body_id, lambda body, n=names: rename_regions(body, n))
    return stream


def body_fields(stream, body_id, fields):
    return replace_body(stream, body_id,
                        lambda body: body[:-1] + ", " + fields + ")")


def observe(normal, readonly=None, certificate=None):
    source = fixture.valid_source()
    return m.observe("P0a", normal, normal if readonly is None else readonly,
                     fixture.certificate(source) if certificate is None else certificate,
                     source)


class InventoryRegionAlphaTests(unittest.TestCase):
    def test_fnmut_and_output_alpha_rename_independently_in_both_directions(self):
        compiler_names = fixture.stream()
        independently_renamed = stream_with_alpha(same_labels=False)
        shared_clause_names = stream_with_alpha(same_labels=True)
        # The two clause binders receive unrelated names independently, and
        # both the renamed-to-original and original-to-renamed comparisons pass.
        observe(compiler_names, independently_renamed)
        observe(independently_renamed, compiler_names)
        # Also compare distinct clause labels with a stream where FnMut and
        # Output deliberately reuse the same labels.
        observe(shared_clause_names, compiler_names)
        observe(compiler_names, shared_clause_names)

    def test_consistent_input_and_independent_clause_alpha_renaming_compares(self):
        normal = stream_with_alpha(same_labels=True)
        readonly = stream_with_alpha(same_labels=True)
        # Use separate names in readonly for each Body. FnMut and Output reuse
        # spellings within each Body, while Body IDs and clause ordinals scope them.
        for body_id, prefix in ((12, "rdefault"), (22, "rfreeze")):
            mappings = {"default_i0": f"{prefix}_i0", "default_i1": f"{prefix}_i1",
                        "default_i2": f"{prefix}_i2", "default_h0": f"{prefix}_h0",
                        "default_h1": f"{prefix}_h1", "freeze_i0": f"{prefix}_i0",
                        "freeze_i1": f"{prefix}_i1", "freeze_i2": f"{prefix}_i2",
                        "freeze_h0": f"{prefix}_h0", "freeze_h1": f"{prefix}_h1"}
            readonly = replace_body(readonly, body_id,
                                    lambda body, mp=mappings: rename_regions(body, mp))
        # Keep ordinary quoted text fixed even when it resembles a region name.
        normal = body_fields(normal, 12, 'contract = (annotation = "ia")')
        readonly = body_fields(readonly, 12, 'contract = (annotation = "ia")')

        raw_before = m._parse_inventory_input(normal, "normal")
        raw_record_before = raw_before["impls"][0]["items"][1]["body"]["record"]
        fields_before = raw_record_before.fields
        readonly_before = m._parse_inventory_input(readonly, "readonly")
        readonly_record_before = readonly_before["impls"][0]["items"][1]["body"]["record"]
        readonly_fields_before = readonly_record_before.fields
        projected = m._inventory_comparison(raw_before)
        m._inventory_comparison(readonly_before)
        self.assertEqual(raw_record_before.fields, fields_before)
        self.assertEqual(readonly_record_before.fields, readonly_fields_before)
        projected_record = projected["impls"][0]["items"][1]["body"]["record"]
        self.assertEqual(m._one(projected_record, "contract"),
                         m._parser.parse_records('(contract = (annotation = "ia"))')[0].fields[0][1])

        result = observe(normal, readonly)
        self.assertFalse(result["proof_credit"])
        raw_result = result["inventory"]["impls"][0]["items"][1]["body"]["record"]
        self.assertEqual(m._one(raw_result, "contract"), m._one(raw_record_before, "contract"))
        # Raw compiler records keep the original mode-specific region spellings.
        self.assertIn('"default_i0"', m._parser.render_value(raw_record_before))
        self.assertIn('"rdefault_i0"', m._parser.render_value(readonly_record_before))

    def test_input_collapse_local_collapse_free_ref_capture_and_wrong_slot_rejected(self):
        normal = fixture.stream()
        mutations = []
        mutations.append(replace_body(normal, 12,
            lambda body: body.replace('"ib"', '"ia"', 1)))

        def local_collapse(body):
            return body.replace('"hb"', '"ha"')
        mutations.append(replace_body(normal, 12, local_collapse))

        def free_reference(body):
            start = body.index('defId = "core::ops::FnMut"')
            end = body.index('defId = "core::ops::FnOnce::Output"')
            return body[:start] + body[start:end].replace('"ha"', '"free"', 1) + body[end:]
        mutations.append(replace_body(normal, 12, free_reference))

        def input_capture(body):
            start = body.index('defId = "core::ops::FnMut"')
            end = body.index('defId = "core::ops::FnOnce::Output"')
            return body[:start] + body[start:end].replace('"ha"', '"ia"') + body[end:]
        mutations.append(replace_body(normal, 12, input_capture))

        def wrong_slot(body):
            return body.replace('boundRegions = ["ha", "hb"]',
                                 'boundRegions = ["hb", "ha"]', 1)
        mutations.append(replace_body(normal, 12, wrong_slot))

        for changed in mutations:
            with self.subTest(change=changed[-120:]), self.assertRaises(m.InventoryError):
                observe(normal, changed)

    def test_wrong_output_type_input_type_mutability_and_tuple_arity_rejected(self):
        normal = fixture.stream()
        changes = (
            lambda b: b.replace('(bool = void)', '(unit = void)', 1),
            lambda b: b.replace('param = "T"', 'param = "U"', 1),
            lambda b: b.replace('mutability = (mut = void)', 'mutability = (not = void)', 1),
        )
        tuple_item = ('(kind = (ref = (region = (id = "hb"), '
                      'ty = (kind = (param = "T")), mutability = (not = void))))')
        changes += (lambda b: b.replace(tuple_item, tuple_item + ", " + tuple_item, 1),)
        for change in changes:
            changed = replace_body(normal, 12, change)
            with self.subTest(change=change), self.assertRaises(m.InventoryError):
                observe(normal, changed)

    def test_body_identity_and_source_binding_stay_strict(self):
        normal = fixture.stream()
        changed_identity = normal.replace(
            'defIndex = 12, defPath = "crate::default16::small_sort"',
            'defIndex = 99, defPath = "crate::default16::small_sort"', 1)
        with self.assertRaises(m.InventoryError):
            observe(normal, changed_identity)
        source = fixture.valid_source()
        bad_certificate = fixture.certificate(source)
        bad_certificate["cases"]["P0a"]["generated_source_sha256"] = "0" * 64
        with self.assertRaises(m.InventoryError):
            observe(normal, normal, bad_certificate)

    def test_unknown_ref_like_metadata_is_not_alpha_projected(self):
        normal = body_fields(fixture.stream(), 12,
            'opaqueMetadata = (ref = (region = (id = "ha"), note = "same"))')
        readonly = body_fields(fixture.stream(), 12,
            'opaqueMetadata = (ref = (region = (id = "readonly-region"), note = "same"))')
        with self.assertRaisesRegex(m.InventoryError, r"differ at .*opaqueMetadata"):
            observe(normal, readonly)

    def test_unrelated_contract_text_is_not_alpha_projected(self):
        normal = body_fields(fixture.stream(), 12,
                             'contract = (annotation = "ia")')
        readonly = stream_with_alpha()
        readonly = body_fields(readonly, 12,
                              'contract = (annotation = "readonly-annotation")')
        with self.assertRaisesRegex(m.InventoryError, r"differ at .*contract"):
            observe(normal, readonly)


if __name__ == "__main__":
    unittest.main()
