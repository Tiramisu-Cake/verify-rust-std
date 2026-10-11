#!/usr/bin/env python3
"""Isolated saved/synthetic AST admission checks; no prepare/run/tool invocation."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

pinned = Path(sys.argv[1])
raw_case = Path(sys.argv[2])
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
runner = load('review_v6_selected', pinned / 'research/challenge-8/cloud-build/origin-layout/onecell-selected-drop.py')
ast = load('review_v6_ast', pinned / 'research/challenge-8/merge/overnight/stack-proof-ast-admission.py')
parser = ast.OcamlAstText
literal_tests = {
    'valid': ('False(loc "verified/lib.rs(42,17-22)")', True),
    'symbol': ('False', False),
    'empty': ('False()', False),
    'extra_argument': ('False(loc "verified/lib.rs(42,17-22)", True)', False),
    'non_location': ('False(Var(loc "verified/lib.rs(42,17-22)", "x"))', False),
    'foreign_location': ('False(loc "other.rs(42,17-22)")', False),
    'true': ('True(loc "verified/lib.rs(42,17-22)")', False),
    'wrapper': ('assume(loc "verified/lib.rs(42,17-22)", False)', False),
}
result = {'kind': 'SERVICE_ONLY_NO_NEW_PROOF', 'literal': {}, 'whole_post': {}}
for name, (text, expected) in literal_tests.items():
    actual = runner._literal_false_with_loc(parser(text).parse(), ast)
    assert actual == expected, name
    result['literal'][name] = actual
raw = json.loads((raw_case / 'classification.json').read_text())
mir = raw['mir_gate']
selected = mir['selected_normal_drop']['selected_path']
tree = parser((raw_case / 'proof-ast.ml').read_text()).parse()

for name in ['valid_saved', 'missing_glue_contract', 'missing_unwind_arm', 'malformed_unwind_post', 'missing_normal_arm', 'duplicate_unwind_arm']:
    mutation = copy.deepcopy(tree)
    funcs = [n for n in ast.nodes(mutation, 'Func') if n.args[4] in [runner.GENERATED_GLUE_NAME, selected] and isinstance(n.args[10], ast.Node) and n.args[10].name == 'Some']
    assert len(funcs) == 2
    if name == 'missing_glue_contract':
        [f for f in funcs if f.args[4] == runner.GENERATED_GLUE_NAME][0].args[8] = ast.Sym('None')
    elif name != 'valid_saved':
        for f in funcs:
            switches = ast.nodes(f.args[8], 'SwitchExpr')
            assert len(switches) == 1
            arms = switches[0].args[2]
            if name == 'missing_unwind_arm':
                arms[:] = [a for a in arms if a.args[1] != 'unwinding']
            elif name == 'missing_normal_arm':
                arms[:] = [a for a in arms if a.args[1] != 'returning']
            elif name == 'malformed_unwind_post':
                [a for a in arms if a.args[1] == 'unwinding'][0].args[3] = ast.Sym('False')
            elif name == 'duplicate_unwind_arm':
                arms.append(copy.deepcopy([a for a in arms if a.args[1] == 'unwinding'][0]))
    # Inject only parser return value; saved file is never changed.
    class SavedMutation:
        def __init__(self, text): pass
        def parse(self): return mutation
    ast.OcamlAstText = SavedMutation
    verdict = runner._body_glue_ast_evidence(raw_case, ast, selected, mir)
    result['whole_post'][name] = verdict['admitted']
    expected = name in ['valid_saved', 'duplicate_unwind_arm']
    assert verdict['admitted'] == expected, (name, verdict)
ast.OcamlAstText = parser
result['finding'] = 'Duplicate identical unwind arms accepted by dict collapse; saved real AST has exactly two arms. Classifier hardening gate, no invalidation of authentic bounded proof.'
print(json.dumps(result, indent=2))
