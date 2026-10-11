#!/usr/bin/env python3
"""Saved AST contract-admission controls; inert imports, no proof execution."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

runner = load('post_service_runner', HERE / 'onecell-selected-drop.py')
ast = load('post_service_ast', HERE.parents[1] / 'merge/overnight/stack-proof-ast-admission.py')
case = Path(sys.argv[1])
receipt = json.loads((case / 'classification.json').read_text())
evidence = receipt['caller_ast_evidence']['body_glue_evidence']
row = {name:evidence[name] for name in ('selected_method_safety_proof_sha256', 'selected_method_contract_sha256')}
tree = ast.OcamlAstText((case / 'proof-ast.ml').read_text()).parse()
for mode in ('valid', 'missing_contract', 'missing_normal', 'missing_unwind', 'malformed_false'):
    mutated = copy.deepcopy(tree)
    glue = next(n for n in ast.nodes(mutated, 'Func') if len(n.args) == 13 and runner._is_generated_glue_name(n.args[4]))
    if mode == 'missing_contract':
        glue.args[8] = ast.Sym('None')
    elif mode != 'valid':
        post = glue.args[8].args[0][1][1]
        switch = next(n for n in ast.nodes(post, 'SwitchExpr'))
        arms = switch.args[2]
        if mode == 'missing_normal':
            arms[:] = [a for a in arms if a.args[1] != 'returning']
        elif mode == 'missing_unwind':
            arms[:] = [a for a in arms if a.args[1] != 'unwinding']
        else:
            false = next(a.args[3] for a in arms if a.args[1] == 'unwinding')
            false.args[:] = []
    proxy = types.SimpleNamespace(**vars(ast))
    proxy.OcamlAstText = lambda text: types.SimpleNamespace(parse=lambda: mutated)
    result = runner._body_glue_ast_evidence(case, proxy, evidence['selected_method'], receipt['mir_gate'], row)
    assert result['admitted'] == (mode == 'valid'), (mode, result)
print('saved AST valid/missing-normal/missing-unwind/malformed-False controls: PASS; service only')
