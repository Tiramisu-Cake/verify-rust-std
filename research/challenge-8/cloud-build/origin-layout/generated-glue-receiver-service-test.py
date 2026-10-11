#!/usr/bin/env python3
"""Isolated AST receiver classifier checks on saved data; no proof execution."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

runner = load('receiver_service_runner', HERE / 'generated-glue-receiver-controls.py')
ast = load('receiver_service_ast', HERE.parents[1] / 'merge/overnight/stack-proof-ast-admission.py')
path = Path(sys.argv[1])
loc = sys.argv[2]
positive = runner._inspect_ast(path, ast, loc)
assert positive['admitted'] and positive['end_count_at_drop_loc'] == positive['all_end_count'] == 2
assert positive['physical_reopen_arguments'] == [['address', 'gap_guard']] * 2
assert len(positive['outcome_arms']) == 2
receiver = positive['receiver_argument']
assert receiver[0] == 'receiver'
assert positive['end_arguments_at_drop_loc'] == [receiver] * 2
assert all(arm['end_arguments'] == [receiver] for arm in positive['outcome_arms'])
# The in-memory checks must have exactly the same representation as receipts.
assert json.loads(json.dumps(positive)) == positive
text = path.read_text()
end_line = next(line for line in text.splitlines(True) if '"end_ref_mut"' in line and f'loc "{loc}"' in line)
assert text.count(end_line) == 2
with tempfile.TemporaryDirectory(prefix='receiver-classifier-service-') as tmp:
    target = Path(tmp) / 'ast.ml'
    for mode in ('omit_end', 'wrong_end', 'duplicate_end'):
        replacement = '' if mode == 'omit_end' else end_line + end_line if mode == 'duplicate_end' else end_line.replace(f'Var (loc "{loc}", "{receiver[1]}")', f'AddressOf (loc "{loc}", Var (loc "{loc}", "gap_guard"))')
        target.write_text(text.replace(end_line, replacement))
        details = runner._inspect_ast(target, ast, loc)
        assert runner._expected_ast(mode, details, tuple(receiver)), (mode, details)
        details['physical_reopen_arguments'][0][1] = 'different_guard'
        assert not runner._expected_ast(mode, details, tuple(receiver))
print('receiver classifier saved/synthetic service: PASS; no proof credit')
