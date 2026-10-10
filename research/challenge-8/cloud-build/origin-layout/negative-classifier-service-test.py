#!/usr/bin/env python3
"""Isolated saved-text admission mutations; no compiler or verifier is run."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('guard_negative_service',
                                              HERE/'guard-storage-controls.py')
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)

source = (b'#![no_std]\n' + control._layout_admission().GUARD_SOURCE +
          b'\npub unsafe fn no_storage_receipts(root: *const CopyOnDrop, src: *const u64)\n'
          b'/*@ req true; @*/ /*@ ens true; @*/ {\n'
          b'    //@ assert std::mem::size_of::<CopyOnDrop>() > 0;\n'
          b'    //@ assert root as usize != src as usize;\n}\n')


def point(line, col):
    return {'file': {'name': {'real': {'localPath': 'verified/lib.rs'}}},
            'line': line, 'col': {'pos': col}}


def span(start_line, start_col, end_line, end_col):
    return {'regular': {'lo': point(start_line, start_col),
                        'hi': point(end_line, end_col)}}


u64 = {'uInt': {'u64': None}}
ptr = lambda mut: {'rawPtr': {'ty': {'kind': u64}, 'mutability': {mut: None}}}
fields = [{'name': {'name': name}, 'ty': {'kind': kind}}
          for name, kind in (('src', ptr('not')), ('dst', ptr('mut')),
                             ('len', {'uInt': {'uSize': None}}))]
guard = {'id': {'name': 'CopyOnDrop'}, 'hasConcreteGuardLayout': True,
         'concreteGuardDefPath': 'CopyOnDrop',
         'concreteGuardDefPathHash': 'DefPathHash(abc)',
         'isLocal': True, 'kind': {'structKind': None}, 'isReprC': False,
         'implementsDrop': False, 'defSpan': span(2, 0, 6, 1),
         'variants': [{'fields': fields}], 'concreteGuardSizeBytes': 24,
         'concreteGuardAlignBytes': 8,
         'concreteGuardFieldOffsets': ['0', '8', '16'],
         'concreteGuardFieldSizes': ['8', '8', '8']}
mir = {'targetTriple': 'x86_64-unknown-linux-gnu', 'pointerWidth': 64,
       'adtDefs': {'cons': {'h': guard, 't': {'nil': None}}},
       'bodies': [{'defPath': 'no_storage_receipts'}]}


def encode(value):
    if isinstance(value, dict):
        return '(' + ', '.join(key+' = '+encode(item) for key, item in value.items()) + ')'
    if isinstance(value, list):
        return '[' + ', '.join(map(encode, value)) + ']'
    if isinstance(value, str):
        return json.dumps(value)
    if value is None:
        return 'void'
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


loc = 'loc "verified/lib.rs(10,1)"'
u64_type = f'ManifestTypeExpr({loc},Int(Unsigned,FixedWidthRank(3)))'
ptr_type = f'PtrTypeExpr({loc},{u64_type})'
len_type = f'ManifestTypeExpr({loc},Int(Unsigned,PtrRank))'
ast_fields = ';'.join(
    f'Field({loc},Real,{ty},{json.dumps(name)},None,None,false,None)'
    for name, ty in (('src', ptr_type), ('dst', ptr_type), ('len', len_type)))
attr = ('RustConcreteGuardLayout(make_rust_concrete_guard_layout('
        '"CopyOnDrop","DefPathHash(abc)","x86_64-unknown-linux-gnu",'
        '64,"24","8",["0";"8";"16"],["8";"8";"8"]))')
live = f'RustStorageLiveStmt({loc},{loc},"_1","$_1")'
dead = f'RustStorageDeadStmt({loc},{loc},"_1","$_1")'
assertion = f'PureStmt({loc},Assert({loc},true))'


def ast_text(statements, contract=None, attribute=attr):
    args = ['None']*13
    args[4] = '"no_storage_receipts"'
    args[8] = contract or f'Some((True({loc}),("outcome",True({loc}))))'
    args[10] = f'Some(([{";".join(statements)}],{loc}))'
    return (f'[Struct(loc "verified/lib.rs(2,1-6,2)","CopyOnDrop",[],Left([],[{ast_fields}],[],false),'
            f'[{attribute}]);Func({",".join(args)})]')


with tempfile.TemporaryDirectory() as temp:
    case = Path(temp)
    (case/'decode.out').write_text(encode(mir))
    (case/'proof-ast.ml').write_text(ast_text([live, assertion, dead]))
    result = control._no_storage_qualification_gate(case, source)
    assert result['admitted'] is True, result
    assert result['temporary_storage_live_count'] == 1
    (case/'proof-ast.ml').write_text(ast_text([live, assertion]))
    assert control._no_storage_qualification_gate(case, source)['admitted'] is False
    (case/'proof-ast.ml').write_text(ast_text([live.replace('$_1','root'), assertion, dead]))
    assert control._no_storage_qualification_gate(case, source)['admitted'] is False
    (case/'proof-ast.ml').write_text(ast_text([live, assertion, dead],
        contract=f'Some((PointsTo({loc}), ("outcome",True({loc}))))'))
    assert control._no_storage_qualification_gate(case, source)['admitted'] is False
    (case/'proof-ast.ml').write_text(ast_text([live, assertion, dead],
        attribute=attr.replace('DefPathHash(abc)', 'DefPathHash(other)')))
    assert control._no_storage_qualification_gate(case, source)['admitted'] is False
    (case/'proof-ast.ml').write_text(ast_text([live, assertion, dead]))
    wrong = copy.deepcopy(mir)
    wrong['adtDefs']['cons']['h']['concreteGuardFieldOffsets'] = ['0', '4', '16']
    (case/'decode.out').write_text(encode(wrong))
    assert control._no_storage_qualification_gate(case, source)['admitted'] is False
print('no-storage qualification parser: one compiler temp accepted, five mutations rejected')
