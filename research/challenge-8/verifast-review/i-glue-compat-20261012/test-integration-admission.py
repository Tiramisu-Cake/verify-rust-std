#!/usr/bin/env python3
"""Saved/synthetic F1 tests through the real file-reading admission entrypoint.
Only inert classifier/parser imports; no prepare/run/proof callback is called.
"""
import argparse
import ast as py_ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    args = argparse.ArgumentParser()
    args.add_argument('--runner', type=Path, required=True)
    args.add_argument('--parser', type=Path, required=True)
    args.add_argument('--case', type=Path, required=True)
    args.add_argument('--mode', choices=('old', 'fixed'), required=True)
    args.add_argument('--extraction', type=Path, required=True)
    a = args.parse_args()
    runner = load('f1_test_runner', a.runner)
    ast = load('f1_test_parser', a.parser)
    raw = json.loads((a.case / 'classification.json').read_text())
    mir = raw['mir_gate']
    selected = mir['selected_normal_drop']['selected_path']
    row = json.loads(a.extraction.read_text())['cases']['positive']
    text = (a.case / 'proof-ast.ml').read_text()
    tree = ast.OcamlAstText(text).parse()

    def dump(value):
        if isinstance(value, ast.Node):
            return value.name + '(' + ','.join(map(dump, value.args)) + ')'
        if isinstance(value, ast.Sym):
            return value.name
        if isinstance(value, str):
            return json.dumps(value)
        if isinstance(value, list):
            return '[' + ';'.join(map(dump, value)) + ']'
        if isinstance(value, tuple):
            return '(' + ','.join(map(dump, value)) + ')'
        if type(value) is int:
            return str(value)
        raise TypeError(type(value))

    assert ast.OcamlAstText(dump(tree)).parse() == tree
    result = {'kind': 'ISOLATED_SERVICE_ONLY_NO_NEW_PROOF', 'mode': a.mode,
              'runner_sha256': hashlib.sha256(a.runner.read_bytes()).hexdigest(),
              'parser_sha256': hashlib.sha256(a.parser.read_bytes()).hexdigest(),
              'saved_ast_sha256': hashlib.sha256(text.encode()).hexdigest(),
              'extraction_sha256': hashlib.sha256(a.extraction.read_bytes()).hexdigest(),
              'saved_build_id': 'a9613c24-8f42-4008-981b-4df6b1e9206d',
              'scope': 'F1 service admission only; no v8 proof or qualification review',
              'entrypoint': '_body_glue_ast_evidence (real parser and temporary proof-ast.ml)',
              'cases': {}, 'literal_false': {}}
    names = ['valid_saved', 'duplicate_returning', 'duplicate_unwinding']
    if a.mode == 'fixed':
        names += ['missing_returning', 'missing_unwinding', 'extra_known_arm',
                  'unknown_arm', 'malformed_arm', 'malformed_arm_arity',
                  'extra_malformed_clause', 'default', 'wrong_returning_binders',
                  'wrong_unwinding_binders', 'malformed_unwind_post', 'wrapped_switch']
        # Reuse the eight exact cases from the published v6 parser test.
        previous = Path(__file__).resolve().parent.parent / 'drop-glue-v6-20261012/parser-check.py'
        literal_tests = next(py_ast.literal_eval(n.value) for n in
                             py_ast.parse(previous.read_text()).body
                             if isinstance(n, py_ast.Assign) and
                             any(isinstance(t, py_ast.Name) and t.id == 'literal_tests'
                                 for t in n.targets))
        for name, (literal, expected) in literal_tests.items():
            actual = runner._literal_false_with_loc(ast.OcamlAstText(literal).parse(), ast)
            assert actual == expected, name
            result['literal_false'][name] = actual

    saved = runner._body_glue_ast_evidence(a.case, ast, selected, mir, row)
    assert saved['admitted'] and saved['glue_contract_present']
    result['unmodified_saved_positive'] = saved['admitted']
    with tempfile.TemporaryDirectory(prefix='c8-f1-tests-') as temporary:
        case = Path(temporary)
        for name in names:
            mutated = copy.deepcopy(tree)
            funcs = [n for n in ast.nodes(mutated, 'Func') if n.args[4] in
                     [runner.GENERATED_GLUE_NAME, selected] and
                     isinstance(n.args[10], ast.Node) and n.args[10].name == 'Some']
            assert len(funcs) == 2
            for f in funcs:
                post = f.args[8].args[0][1][1]
                assert post.name == 'SwitchExpr' and len(post.args) == 4
                arms = post.args[2]
                returning = next(x for x in arms if x.args[1] == 'returning')
                unwinding = next(x for x in arms if x.args[1] == 'unwinding')
                if name in ('duplicate_returning', 'extra_known_arm'):
                    arms.append(copy.deepcopy(returning))
                elif name == 'duplicate_unwinding':
                    arms.append(copy.deepcopy(unwinding))
                elif name == 'missing_returning':
                    arms.remove(returning)
                elif name == 'missing_unwinding':
                    arms.remove(unwinding)
                elif name == 'unknown_arm':
                    unwinding.args[1] = 'unknown'
                elif name == 'malformed_arm':
                    unwinding.name = 'MalformedClause'
                elif name == 'malformed_arm_arity':
                    unwinding.args.pop()
                elif name == 'extra_malformed_clause':
                    arms.append(ast.Sym('MalformedClause'))
                elif name == 'default':
                    post.args[3] = ast.Node('Some', [copy.deepcopy(unwinding.args[3])])
                elif name == 'wrong_returning_binders':
                    returning.args[2] = []
                elif name == 'wrong_unwinding_binders':
                    unwinding.args[2] = ['result']
                elif name == 'malformed_unwind_post':
                    unwinding.args[3] = ast.Sym('False')
                elif name == 'wrapped_switch':
                    pair = f.args[8].args[0]
                    f.args[8].args[0] = (pair[0], (pair[1][0], ast.Node('Sep',
                        [copy.deepcopy(post.args[0]), post, ast.Node('True', [copy.deepcopy(post.args[0])])])))
            # Both complete contracts remain equal, so rejection cannot be
            # attributed to an unequal glue/selected post.
            assert funcs[0].args[8] == funcs[1].args[8], name
            mutated_text = text if name == 'valid_saved' else dump(mutated)
            (case / 'proof-ast.ml').write_text(mutated_text)
            verdict = runner._body_glue_ast_evidence(case, ast, selected, mir, row)
            expected = name == 'valid_saved' or a.mode == 'old'
            assert verdict['glue_contract_present'], (name, verdict)
            assert verdict['admitted'] == expected, (name, verdict)
            result['cases'][name] = {'admitted': verdict['admitted'],
                'contracts_match': verdict['glue_contract_present'],
                'literal_unwind_false': verdict['glue_literal_unwind_false'],
                'synthetic': name != 'valid_saved',
                'ast_sha256': hashlib.sha256(mutated_text.encode()).hexdigest()}
    assert hashlib.sha256((a.case / 'proof-ast.ml').read_bytes()).hexdigest() == result['saved_ast_sha256']
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
