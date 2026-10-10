#!/usr/bin/env python3
"""Isolated synthetic parser test; never invokes exporter, verifier or proof."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "guard_layout_admission_service", HERE / "guard-layout-admission.py")
admission = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admission)

source = (admission.GUARD_SOURCE + b"\npub unsafe fn insertion_onecell() {\n" +
          admission.TMP_SOURCE + admission.GUARD_INIT +
          b"        //@ assert true; // GUARD: allocation separation\n" +
          b"        //@ assert true; // GUARD: post FBC separation\n}\n")
line = lambda token: source[:source.index(token)].count(b"\n") + 1
tmp_line, guard_line = line(admission.TMP_SOURCE), line(admission.GUARD_INIT)


def span(start_line, start_col=0, end_line=None, end_col=0):
    def point(number, column):
        return {"file": {"name": {"real": {"localPath": "verified/lib.rs"}}},
                "line": number, "col": {"pos": column}}
    return {"regular": {"lo": point(start_line, start_col),
                        "hi": point(end_line or start_line, end_col)}}


def local(name):
    return {"name": name}


def field(name, kind):
    return {"name": {"name": name}, "ty": {"kind": kind}}


u64 = {"uInt": {"u64": None}}
pointer = lambda mut: {"rawPtr": {"ty": {"kind": u64},
                                  "mutability": {mut: None}}}
fields = [field("src", pointer("not")), field("dst", pointer("mut")),
          field("len", {"uInt": {"uSize": None}})]
adt = {"id": {"name": "CopyOnDrop"}, "hasConcreteGuardLayout": True,
       "concreteGuardDefPath": "CopyOnDrop",
       "concreteGuardDefPathHash": "DefPathHash(abc)",
       "isLocal": True, "kind": {"structKind": None}, "isReprC": False,
       "implementsDrop": False, "defSpan": span(1, 0, 5, 1),
       "variants": [{"fields": fields}], "concreteGuardSizeBytes": 24,
       "concreteGuardAlignBytes": 8,
       "concreteGuardFieldOffsets": ["0", "8", "16"],
       "concreteGuardFieldSizes": ["8", "8", "8"]}


def debug(name, ident):
    return {"name": {"name": name},
            "value": {"place": {"local": local(ident), "projection": []}}}


def live(name, ident, source_line):
    return {"kind": {name: local(ident)},
            "sourceInfo": {"span": span(source_line)}}


constructor = {
    "kind": {"assign": {
        "lhsPlace": {"local": local("_2"), "projection": []},
        "rhsRvalue": {"aggregate": {
            "aggregateKind": {"adt": {"adtId": {"name": "CopyOnDrop"},
                                      "fields": [{"name": name} for name in
                                                 ("src", "dst", "len")]}},
            "operands": [1, 2, 3]}}}},
    "sourceInfo": {"span": span(guard_line)},
}


body = {"defPath": "insertion_onecell",
        "varDebugInfo": [debug("tmp", "_1"), debug("gap_guard", "_2")],
        "localDecls": [{"id": local("_1")}, {"id": local("_2")}],
        "basicBlocks": [{"id": {"index": 0},
                         "statements": [live("storageLive", "_1", tmp_line),
                                        live("storageLive", "_2", guard_line),
                                        constructor],
                         "terminator": {"kind": {"return": None}}}]}
mir = {"targetTriple": "x86_64-unknown-linux-gnu", "pointerWidth": 64,
       "adtDefs": {"cons": {"h": adt, "t": {"nil": None}}}, "bodies": [body]}


def encode(value):
    if isinstance(value, dict):
        return "(" + ", ".join(key + " = " + encode(item)
                                for key, item in value.items()) + ")"
    if isinstance(value, list):
        return "[" + ", ".join(map(encode, value)) + "]"
    if isinstance(value, str):
        return json.dumps(value)
    if value is None:
        return "void"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


u64_type = ('ManifestTypeExpr(loc "verified/lib.rs(2,1)",'
            'Int(Unsigned,FixedWidthRank(3)))')
ptr_type = 'PtrTypeExpr(loc "verified/lib.rs(2,1)",' + u64_type + ')'
len_type = ('ManifestTypeExpr(loc "verified/lib.rs(4,1)",'
            'Int(Unsigned,PtrRank))')
ast_fields = ";".join(
    'Field(loc "verified/lib.rs(2,1)",Real,' + ty + ',' +
    json.dumps(name) + ',None,None,false,None)'
    for name, ty in (("src", ptr_type), ("dst", ptr_type), ("len", len_type)))
attr = ('RustConcreteGuardLayout(make_rust_concrete_guard_layout('
        '"CopyOnDrop","DefPathHash(abc)","x86_64-unknown-linux-gnu",'
        '64,"24","8",["0";"8";"16"],["8";"8";"8"]))')
def marker(kind, number, ident, name):
    return (f'{kind}(loc "verified/lib.rs({number},1)",'
            f'loc "verified/lib.rs({number},1)","{ident}","{name}")')


tmp_marker = marker("RustStorageLiveStmt", tmp_line, "_1", "tmp")
guard_marker = marker("RustStorageLiveStmt", guard_line, "_2", "gap_guard")
loc = f'loc "verified/lib.rs({guard_line},1)"'
writes = [f'ExprStmt(AssignExpr({loc},Select({loc},Var({loc},"gap_guard"),'
          f'"{field}"),Mutation,Var({loc},"value")))'
          for field in ("src", "dst", "len")]
def assertion(line):
    return (f'PureStmt(loc "verified/lib.rs({line},1)",'
            f'Assert(loc "verified/lib.rs({line},1)",true))')


fact = assertion(guard_line + 1)
post_fact = assertion(guard_line + 2)
statements = [tmp_marker, guard_marker, *writes, fact, post_fact]
fn_args = ["None"] * 13
fn_args[4] = '"insertion_onecell"'


def ast_text_for(items):
    args = fn_args.copy()
    args[10] = ('Some(([' + ';'.join(items) + '],'
                f'loc "verified/lib.rs({guard_line + 3},1)"))')
    return ('[Struct(loc "verified/lib.rs(1,1-5,2)","CopyOnDrop",[],Left([],[' +
            ast_fields + '],[],false),[' + attr + ']);Func(' +
            ','.join(args) + ')]')


ast_text = ast_text_for(statements)

with tempfile.TemporaryDirectory() as temp:
    case = Path(temp)
    for variant in ("original", "verified"):
        (case / variant).mkdir()
        (case / variant / "lib.rs").write_bytes(source)
    (case / "decode.out").write_text(encode(mir))
    (case / "proof-ast.ml").write_text(ast_text)
    result = admission.admit(case)
    assert result["admitted"], result
    (case / "proof-ast.ml").write_text(
        ast_text.replace("DefPathHash(abc)", "DefPathHash(other)"))
    assert admission.admit(case)["admitted"] is False
    (case / "proof-ast.ml").write_text(
        ast_text.replace('"_2","gap_guard"', '"_9","gap_guard"'))
    assert admission.admit(case)["admitted"] is False
    bad_mir = copy.deepcopy(mir)
    bad_mir["adtDefs"]["cons"]["h"]["concreteGuardFieldOffsets"] = ["0", "4", "16"]
    (case / "decode.out").write_text(encode(bad_mir))
    (case / "proof-ast.ml").write_text(ast_text)
    assert admission.admit(case)["admitted"] is False
    (case / "decode.out").write_text(encode(mir))
    dead = marker("RustStorageDeadStmt", tmp_line, "_1", "tmp")
    (case / "proof-ast.ml").write_text(
        ast_text_for([tmp_marker, dead, guard_marker, *writes, fact, post_fact]))
    assert admission.admit(case)["admitted"] is False
    branch = f'IfStmt({loc},true,SkipStmt({loc}),SkipStmt({loc}))'
    (case / "proof-ast.ml").write_text(
        ast_text_for([tmp_marker, branch, guard_marker, *writes, fact, post_fact]))
    assert admission.admit(case)["admitted"] is False
    (case / "proof-ast.ml").write_text(
        ast_text_for([tmp_marker, branch.replace("IfStmt", "SwitchStmt"),
                      guard_marker, *writes, fact, post_fact]))
    assert admission.admit(case)["admitted"] is False
    nested_guard = f'IfStmt({loc},true,{guard_marker},SkipStmt({loc}))'
    (case / "proof-ast.ml").write_text(
        ast_text_for([tmp_marker, nested_guard, *writes, fact, post_fact]))
    assert admission.admit(case)["admitted"] is False
    (case / "proof-ast.ml").write_text(
        ast_text_for([tmp_marker, guard_marker, dead, *writes, fact, post_fact]))
    assert admission.admit(case)["admitted"] is False
    (case / "proof-ast.ml").write_text(
        ast_text_for([tmp_marker, guard_marker, *writes[:-1], fact, post_fact]))
    assert admission.admit(case)["admitted"] is False
    (case / "proof-ast.ml").write_text(
        ast_text_for([tmp_marker, guard_marker, *writes, fact, dead, post_fact]))
    assert admission.admit(case)["admitted"] is False
    (case / "proof-ast.ml").write_text(
        ast_text_for([tmp_marker, guard_marker, *writes, fact]))
    assert admission.admit(case)["admitted"] is False
    (case / "proof-ast.ml").write_text(ast_text)
    bad_mir = copy.deepcopy(mir)
    bad_mir["bodies"][0]["basicBlocks"][0]["statements"].insert(
        2, live("storageDead", "_1", guard_line))
    (case / "decode.out").write_text(encode(bad_mir))
    assert admission.admit(case)["admitted"] is False
print("guard layout saved-data parser: positive and twelve mutations passed")
