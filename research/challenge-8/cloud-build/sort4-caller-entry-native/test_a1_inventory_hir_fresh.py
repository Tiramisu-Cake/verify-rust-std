"""Synthetic validation/projection controls for Body HIR Fresh lifetimes."""
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

fixture = load("a1_hir_fresh_fixture", "test_a1_compiler_inventory.py")
m = load("a1_hir_fresh_inventory", "a1-compiler-inventory.py")


def body_marker(body_id):
    path = ("crate::default16::small_sort" if body_id == 12 else
            "crate::freeze32::small_sort")
    return f'(defIndex = {body_id}, defPath = "{path}"'


def alter_body(stream, body_id, transform):
    start = stream.index(body_marker(body_id))
    depth, quoted, escaped, end = 0, False, False, None
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
    body = stream[start:end]
    return stream[:start] + transform(body) + stream[end:]


def hir_param(kind, name=None, *, h=0, l=None, pure="false", bounds="void"):
    if kind == "type":
        name = "F" if name is None else name
        named = f'plain = (name = (name = "{name}"))'
    else:
        if l is None:
            l = name
        named = f'fresh = (h = {h}, l = {l})'
    return (f'(kind = ({kind} = void), name = ({named}), '
            f'pureWrtDrop = {pure}, bounds = {bounds})')


def hir_text(ids, *, f_name="F", f_kind="type", params_override=None):
    if params_override is None:
        params = [hir_param(f_kind, f_name)] + [hir_param("lifetime", l=x) for x in ids]
    else:
        params = params_override
    return 'hirGenerics = (params = [' + ', '.join(params) + '])'


def with_hir(stream, body_id, ids, *, input_ids=None, f_name="F", f_kind="type", params_override=None):
    names = ["'__" + str(x) for x in (ids if input_ids is None else input_ids)]
    input_aliases = ("ia", "ib", "ic")

    def transform(body):
        for old, new in zip(input_aliases, names):
            body = body.replace(f'"{old}"', f'"{new}"', 1)
        hir = hir_text(ids, f_name=f_name, f_kind=f_kind, params_override=params_override)
        return body[:-1] + ", " + hir + ")"
    return alter_body(stream, body_id, transform)


def observe(normal, readonly=None, certificate=None):
    source = fixture.valid_source()
    return m.observe("P0a", normal, normal if readonly is None else readonly,
                     fixture.certificate(source) if certificate is None else certificate,
                     source)


class HirFreshInventoryTests(unittest.TestCase):
    def test_fresh_alpha_projection_accepts_bijective_shift_and_preserves_raw(self):
        normal, readonly = fixture.stream(), fixture.stream()
        normal = with_hir(normal, 12, (53, 54, 55))
        normal = with_hir(normal, 22, (63, 64, 65))
        readonly = with_hir(readonly, 12, (48, 49, 50))
        readonly = with_hir(readonly, 22, (58, 59, 60))

        normal_shape = m._parse_inventory_input(normal, "normal")
        readonly_shape = m._parse_inventory_input(readonly, "readonly")
        normal_record = normal_shape["impls"][0]["items"][1]["body"]["record"]
        readonly_record = readonly_shape["impls"][0]["items"][1]["body"]["record"]
        normal_raw_fields, readonly_raw_fields = normal_record.fields, readonly_record.fields
        projected = m._inventory_comparison(normal_shape)
        m._inventory_comparison(readonly_shape)
        self.assertEqual(normal_record.fields, normal_raw_fields)
        self.assertEqual(readonly_record.fields, readonly_raw_fields)
        self.assertEqual(m._uint(normal_record, "defIndex"), 12)
        self.assertEqual(m._uint(readonly_record, "defIndex"), 12)

        result = observe(normal, readonly)
        raw = result["inventory"]["impls"][0]["items"][1]["body"]["record"]
        params = m._list(m._member(m._one(raw, "hirGenerics"), "params"), "params")
        self.assertIn("fresh = (h = 0, l = 53)", m._parser.render_value(params[1]))
        projected_record = projected["impls"][0]["items"][1]["body"]["record"]
        projected_params = m._list(m._member(m._one(projected_record, "hirGenerics"), "params"), "params")
        self.assertIn("fresh = (h = 0, l = 1)", m._parser.render_value(projected_params[1]))

    def test_absent_optional_hir_keeps_legacy_synthetic_records_valid(self):
        result = observe(fixture.stream())
        self.assertFalse(result["proof_credit"])
        body = result["inventory"]["impls"][0]["items"][1]["body"]["record"]
        self.assertIsNone(m._one(body, "hirGenerics", required=False))

    def test_wrong_stale_reordered_and_collapsed_fresh_bindings_fail(self):
        base = fixture.stream()
        wrong_input_name = with_hir(base, 12, (53, 54, 55), input_ids=(52, 54, 55))
        stale = with_hir(base, 12, (52, 54, 55), input_ids=(53, 54, 55))
        reordered = with_hir(base, 12, (54, 53, 55), input_ids=(53, 54, 55))
        collapsed = with_hir(base, 12, (53, 53, 55), input_ids=(53, 54, 55))
        for bad in (wrong_input_name, stale, reordered, collapsed):
            with self.subTest(bad=bad[-160:]), self.assertRaises(m.InventoryError):
                observe(with_hir(base, 12, (53, 54, 55)), bad)

    def test_fresh_ids_must_be_unique_across_selected_bodies(self):
        base = fixture.stream()
        normal = with_hir(with_hir(base, 12, (53, 54, 55)), 22, (63, 64, 65))
        duplicate = with_hir(with_hir(base, 12, (53, 54, 55)), 22, (53, 54, 55))
        with self.assertRaisesRegex(m.InventoryError, "Fresh compiler identity is reused"):
            observe(normal, duplicate)

    def test_duplicate_within_hir_fresh_records_is_rejected(self):
        # Directly isolate the HIR identity check; end-to-end input-region
        # validation rejects the corresponding duplicate input name earlier.
        text = with_hir(fixture.stream(), 12, (53, 53, 55), input_ids=(53, 54, 55))
        root = m._find_vfmir(text)
        record = next(body for body in m._records(root, "bodies")
                      if m._uint(body, "defIndex") == 12)
        with self.assertRaisesRegex(m.InventoryError, "Fresh compiler identity is reused"):
            m._hir_fresh_projection(record, ("'__53", "'__53", "'__55"), set())

    def test_hir_shape_type_flags_and_fresh_integer_are_strict(self):
        base = fixture.stream()
        valid = [hir_param("type", "F"), *(hir_param("lifetime", l=x) for x in (53, 54, 55))]
        invalid = (
            hir_text((53, 54)),
            hir_text((53, 54, 55, 56)),
            "hirGenerics = null",
            'hirGenerics = (params = null)',
            hir_text((), params_override=[valid[0], valid[1], valid[2],
                                          '(kind = (lifetime = void), name = (fresh = (h = 0, l = 55)))']),
            hir_text((), params_override=[valid[0], valid[1], valid[2],
                                          hir_param("lifetime", l=55, pure="true")]),
            hir_text((), params_override=[valid[0], valid[1], valid[2],
                                          hir_param("lifetime", l=55, bounds="[]")]),
            hir_text((), params_override=[valid[0], valid[1], valid[2],
                                          hir_param("lifetime", l=55, h=1)]),
            hir_text((), params_override=[valid[0], valid[1], valid[2],
                                          hir_param("lifetime", l=(1 << 64))]),
            hir_text((), params_override=[valid[0], valid[1], valid[2],
                                          hir_param("lifetime", l=0)]),
            'hirGenerics = (params = [(kind = (type = void), name = (plain = (name = (name = "G"))), pureWrtDrop = false, bounds = void), '
            + ', '.join(valid[1:]) + '])',
            'hirGenerics = (params = [(kind = (type = void), name = (plain = (name = (name = null))), pureWrtDrop = false, bounds = void), '
            + ', '.join(valid[1:]) + '])',
        )
        for bad_hir in invalid:
            text = alter_body(with_hir(base, 12, (53, 54, 55)), 12,
                lambda body, h=bad_hir: body[:body.index('hirGenerics =')] + h + ')')
            with self.subTest(hir=bad_hir[-90:]), self.assertRaises(m.InventoryError):
                observe(text)

    def test_zero_fresh_identity_is_invalid_even_if_input_name_matches(self):
        zero = with_hir(fixture.stream(), 12, (0, 54, 55))
        with self.assertRaisesRegex(m.InventoryError, "l must be nonzero"):
            observe(zero)

    def test_non_numeric_fresh_and_wrong_parameter_kind_fail(self):
        base = with_hir(fixture.stream(), 12, (53, 54, 55))
        text_as_id = alter_body(base, 12,
            lambda body: body.replace('h = 0, l = 54', 'h = 0, l = "54"', 1))
        wrong_kind = alter_body(base, 12,
            lambda body: body.replace('kind = (lifetime = void)', 'kind = (const = void)', 1))
        for bad in (text_as_id, wrong_kind):
            with self.assertRaises(m.InventoryError):
                observe(base, bad)

    def test_unknown_fresh_lookalike_metadata_is_not_projected(self):
        normal = with_hir(fixture.stream(), 12, (53, 54, 55))
        readonly = with_hir(fixture.stream(), 12, (48, 49, 50))
        normal = alter_body(normal, 12, lambda body: body[:-1] +
            ', opaque = (name = (fresh = (h = 0, l = 53))))')
        readonly = alter_body(readonly, 12, lambda body: body[:-1] +
            ', opaque = (name = (fresh = (h = 0, l = 99))))')
        with self.assertRaisesRegex(m.InventoryError, r"differ at .*opaque"):
            observe(normal, readonly)


if __name__ == "__main__":
    unittest.main()
