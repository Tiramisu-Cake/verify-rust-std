#!/usr/bin/env python3
"""Synthetic, isolated admission tests for the len1 interface classifier.

No source preparation, MIR export, compiler, verifier, proof, or live evidence
is invoked or modified by this service test.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"missing test module: {path}")
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


target = load("onecell_interface_under_test", HERE / "onecell-drop-interface.py")
ast = load("onecell_interface_ast", HERE.parents[3] /
           "research/challenge-8/merge/overnight/stack-proof-ast-admission.py")


def loc(line: int):
    return ast.Node("loc", [f"verified/lib.rs({line},1)"])


def u64():
    return ast.Node("ManifestTypeExpr", [loc(1),
        ast.Node("Int", [ast.Sym("Unsigned"), ast.Node("FixedWidthRank", [3])])])


def ptr_u64():
    return ast.Node("PtrTypeExpr", [loc(1), u64()])


def usize():
    return ast.Node("ManifestTypeExpr", [loc(1),
        ast.Node("Int", [ast.Sym("Unsigned"), ast.Sym("PtrRank")])])


def effect_fixture():
    source = b"struct CopyOnDrop {\n" + target.EFFECT_DEF + b"\n"
    with tempfile.TemporaryDirectory(prefix="onecell-interface-service-") as root:
        case = Path(root)
        (case / "verified").mkdir()
        (case / "verified/lib.rs").write_bytes(source)
        declaration = ast.Node("PredFamilyDecl", [
            loc(2), target.EFFECT_NAME.decode(), [], 0,
            [ast.Node("IdentTypeExpr", [loc(2), ast.Sym("None"), "thread_id_t"]),
             ptr_u64(), ptr_u64(), usize()],
            ast.Node("Some", [4]), ast.Sym("Inductiveness_Inductive")])
        params = [(ast.Node("IdentTypeExpr", [loc(2), ast.Sym("None"), "thread_id_t"]), "t"),
                  (ptr_u64(), "src"), (ptr_u64(), "dst"), (usize(), "len")]
        # Deliberately use only a generic nonempty assertion node.  The real
        # parsed array/pattern/coefficient AST is not in saved c766 evidence;
        # this test confirms the classifier refuses to infer it from source.
        body = ast.Node("Sep", [loc(2), ast.Node("EmpAsn", [loc(2)]),
                                 ast.Node("EmpAsn", [loc(2)])])
        definition = ast.Node("PredFamilyInstanceDecl", [
            loc(2), target.EFFECT_NAME.decode(), [], [], params, body])
        tree = [declaration, definition]
        passed = target._effect_definition_gate(case, tree, ast)
        assert not passed["admitted"]
        assert passed["reason"] == ("effect definition AST gate failed: "
                                    "effect declaration/definition location differs from checked source name span")
        # Matching the source name span alone must still reject the arbitrary
        # emp/emp body: the gate requires exact CURRENT payload resources.
        exact_loc = ast.Node("loc", [f"verified/lib.rs(2,6-{6 + len(target.EFFECT_NAME)})"])
        for node in tree:
            node.args[0] = exact_loc
        rejected_body = target._effect_definition_gate(case, tree, ast)
        assert not rejected_body["admitted"]
        assert "not exactly the len1/source-quarter/destination-singleton/current-owner assertion" in rejected_body["reason"]

        wrong_binder = copy.deepcopy(tree)
        wrong_binder[1].args[4][2] = (wrong_binder[1].args[4][2][0], "other")
        assert not target._effect_definition_gate(case, wrong_binder, ast)["admitted"]

        arbitrary_body = copy.deepcopy(tree)
        arbitrary_body[1].args[5] = ast.Node("EmpAsn", [loc(2)])
        assert not target._effect_definition_gate(case, arbitrary_body, ast)["admitted"]

        duplicate = tree + [copy.deepcopy(definition)]
        assert not target._effect_definition_gate(case, duplicate, ast)["admitted"]

        assert not target._effect_definition_gate(case, [declaration], ast)["admitted"]


class FakeMir:
    @staticmethod
    def path(value, *keys):
        for key in keys:
            if isinstance(value, dict):
                value = value[key]
            else:
                raise KeyError(key)
        return value


def test_layout_gate():
    source = (b"struct CopyOnDrop {\n    src: *const u64,\n"
              b"    dst: *mut u64,\n    len: usize,\n}\n")
    names = ["src", "dst", "len"]
    fields = [{"name": {"name": "src"}, "ty": {"kind": {"rawPtr": {
                   "ty": {"kind": {"uInt": {"u64": None}}}, "mutability": {"not": None}}}}},
              {"name": {"name": "dst"}, "ty": {"kind": {"rawPtr": {
                   "ty": {"kind": {"uInt": {"u64": None}}}, "mutability": {"mut": None}}}}},
              {"name": {"name": "len"}, "ty": {"kind": {"uInt": {"uSize": None}}}}]
    def point(line, col):
        return {"file": {"name": {"real": {"localPath": "verified/lib.rs"}}},
                "line": line, "col": {"pos": col}}
    adt = {"id": {"name": "CopyOnDrop"}, "hasConcreteGuardLayout": True,
           "concreteGuardDefPath": "CopyOnDrop", "concreteGuardDefPathHash": "opaque-hash",
           "isLocal": True, "kind": {"structKind": None}, "isReprC": False,
           "implementsDrop": True,
           "defSpan": {"regular": {"lo": point(1, 0), "hi": point(5, 1)}},
           "variants": [{"fields": fields}], "concreteGuardSizeBytes": 24,
           "concreteGuardAlignBytes": 8, "concreteGuardFieldOffsets": ["0", "8", "16"],
           "concreteGuardFieldSizes": ["8", "8", "8"]}
    tree = {"targetTriple": "x86_64-unknown-linux-gnu", "pointerWidth": 64,
            "adtDefs": {"cons": {"h": adt, "t": {"nil": None}}}}
    ast_fields = [ast.Node("Field", [loc(1), ast.Sym("Real"), ptr_u64(), "src",
                                      ast.Sym("None"), ast.Sym("None"), False, ast.Sym("None")]),
                  ast.Node("Field", [loc(1), ast.Sym("Real"), ptr_u64(), "dst",
                                      ast.Sym("None"), ast.Sym("None"), False, ast.Sym("None")]),
                  ast.Node("Field", [loc(1), ast.Sym("Real"), usize(), "len",
                                      ast.Sym("None"), ast.Sym("None"), False, ast.Sym("None")])]
    attrs = [ast.Node("RustConcreteGuardLayout", [ast.Node(
        "make_rust_concrete_guard_layout", ["CopyOnDrop", "opaque-hash",
            "x86_64-unknown-linux-gnu", 64, "24", "8", ["0", "8", "16"],
            ["8", "8", "8"]])])]
    struct_loc = ast.Node("loc", ["verified/lib.rs(1,1-5,2)"])
    struct = ast.Node("Struct", [struct_loc, "CopyOnDrop", [],
        ast.Node("Left", [[], ast_fields, [], ast.Sym("None")]), attrs])
    ast_tree = [struct]
    good = target._guard_layout_gate(FakeMir, tree, ast, ast_tree, source)
    assert good["admitted"], good

    wrong_hash = copy.deepcopy(ast_tree)
    wrong_hash[0].args[4][0].args[0].args[1] = "other-hash"
    assert not target._guard_layout_gate(FakeMir, tree, ast, wrong_hash, source)["admitted"]

    wrong_span = copy.deepcopy(tree)
    wrong_span["adtDefs"]["cons"]["h"]["defSpan"]["regular"]["hi"]["line"] = 4
    assert not target._guard_layout_gate(FakeMir, wrong_span, ast, ast_tree, source)["admitted"]


def test_stage_classifiers():
    row = {"expected_qualification_failure": "wrong_effect_signature"}
    source = {"admitted": True}
    execution = {"source_files_unchanged": True}
    stages = {"exporter": 0, "decode": 0, "refinement": 0, "verifast": 1}
    diagnostic = "error: Malformed CopyOnDrop_drop_effect opt-in predicate"
    assert target._qualification_failure_matched(row, source, execution,
                                                   stages, [diagnostic], diagnostic)
    for bad_stages in (dict(stages, decode=1), dict(stages, refinement=1),
                       dict(stages, verifast=0)):
        assert not target._qualification_failure_matched(
            row, source, execution, bad_stages, [diagnostic], diagnostic)
    assert not target._qualification_failure_matched(
        row, source, execution, stages, [diagnostic, diagnostic], diagnostic)
    assert not target._no_effect_refusal_matched(
        Path("/nonexistent-synthetic-case"), {"case": "canonical_no_effect"},
        {}, {}, ["error"], "error: arbitrary failure after leak", {}, {}, {})
    assert target._all_cases_matched(target.EXPECTED_CLASSIFICATIONS.copy())
    incomplete = target.EXPECTED_CLASSIFICATIONS.copy()
    incomplete.pop("canonical_no_effect")
    assert not target._all_cases_matched(incomplete)
    wrong_class = target.EXPECTED_CLASSIFICATIONS.copy()
    wrong_class["canonical_no_effect"] = "INCONCLUSIVE"
    assert not target._all_cases_matched(wrong_class)


effect_fixture()
test_layout_gate()
test_stage_classifiers()
print("onecell interface synthetic admission service tests PASS")
