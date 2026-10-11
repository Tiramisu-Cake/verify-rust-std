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
drop_module = load('receiver_service_drop_module', HERE / 'onecell-selected-drop.py')
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

# Saved Build 53b4's diagnostics report the failed contract location first,
# then attach the generated caller call as a note. Exercise both locations and
# reject the same predicate at an unrelated source/call site.
drop_loc = 'verified/lib.rs(194,9-10)'
def diagnostic(error, call=drop_loc):
    return (error + '\n194 |         }\n    |         ^\n' +
            call + ': note: Verifying call\n')

omit_log = ('  0.273924s: ' + drop_loc + ': Consuming points_to chunk\n' +
    diagnostic(drop_loc + ': error: No matching heap chunks: '
               '[_]points_to<CopyOnDrop>(gap_guard_addr, _)', call=drop_loc).replace(
                   drop_loc + ': note: Verifying call', drop_loc + ': note: Consuming points_to chunk'))
wrong_log = diagnostic('/workspace/tool/bin/rust/aliasing.rsspec(68,9-26): error: '
    'No matching heap chunks: ref_mut_end_token<CopyOnDrop>(gap_guard_addr, _)')
duplicate_log = diagnostic('/workspace/tool/bin/rust/aliasing.rsspec(68,9-26): error: '
    'No matching heap chunks: ref_mut_end_token<CopyOnDrop>(fn_outcome_result(outcome1), _)')
retire_log = diagnostic('verified/lib.rs(53,17-20): error: No matching heap chunks: '
    'CopyOnDrop_src(fn_outcome_result(outcome1), _)')
for mode, log in (('omit_end', omit_log), ('wrong_end', wrong_log),
                  ('duplicate_end', duplicate_log), ('post_retirement_drop', retire_log)):
    result = runner._target_error_and_call_trace(log, mode, drop_loc)
    assert result['matched'], (mode, result)
    assert result['caller_drop_loc'] == drop_loc
for mode, log in (
    ('omit_end', wrong_log),
    ('wrong_end', duplicate_log),
    ('duplicate_end', wrong_log),
    ('post_retirement_drop', diagnostic('verified/lib.rs(53,17-20): error: '
        'No matching heap chunks: CopyOnDrop_len(fn_outcome_result(outcome1), _)')),
    ('omit_end', diagnostic('/workspace/tool/bin/rust/aliasing.rsspec(68,9-26): error: '
        'No matching heap chunks: ref_mut_end_token<CopyOnDrop>(fn_outcome_result(outcome1), _)',
        'verified/lib.rs(193,9-10)')),
    ('omit_end', omit_log + 'verified/lib.rs(17,1-2): error: unrelated failure\n'),
):
    assert not runner._target_error_and_call_trace(log, mode, drop_loc)['matched'], mode

# The call span also labels several generated statements and a later prototype
# check. Bind the completed glue lifetime to its final source-end Leak check,
# allowing unrelated inner checks while rejecting a missing, moved, or duplicate
# final check.
source_span = '/workspace/toolchain/lib/rust/core/ptr.rs(848,1-850,25)'
copy_loc = '/workspace/toolchain/lib/rust/core/ptr.rs(848,1)'
end_loc = '/workspace/toolchain/lib/rust/core/ptr.rs(850,24-25)'
glue_gate = {'receiver_copy_loc': copy_loc, 'selected_method_call_loc': source_span}
glue_log = (f"{source_span}: Verifying function '__vf_generated_drop_glue'\n"
            f"{copy_loc}: Executing statement\n"
            f"{source_span}: Verifying call\n"
            "verified/lib.rs(55,1-56,2): Leak check.\n"
            f"{source_span}: Executing return statement\n"
            f"{end_loc}: Leak check.\n"
            f"{drop_loc}: Verifying function 'natural_onecell'\n"
            f"{drop_loc}: error: expected caller failure\n")
assert runner._glue_markers_precede_error(glue_log, glue_gate,
    f'{drop_loc}: error: expected caller failure', drop_module)
assert not runner._glue_markers_precede_error(
    glue_log.replace(f'{end_loc}: Leak check.\n', ''), glue_gate,
    f'{drop_loc}: error: expected caller failure', drop_module)
assert not runner._glue_markers_precede_error(
    glue_log.replace(end_loc, '/workspace/toolchain/lib/rust/core/ptr.rs(849,24-25)'),
    glue_gate, f'{drop_loc}: error: expected caller failure', drop_module)
assert not runner._glue_markers_precede_error(
    glue_log.replace(f'{end_loc}: Leak check.\n', f'{end_loc}: Leak check.\n{end_loc}: Leak check.\n'),
    glue_gate, f'{drop_loc}: error: expected caller failure', drop_module)

# Optional exact Build replay: run the complete classifier on preserved case
# logs, proof AST, MIR, and original execution/source-hash receipts. This is
# parser/classifier replay only; no exporter, refiner, or proof subprocesses.
if len(sys.argv) > 3:
    saved_root = Path(sys.argv[3])
    positive_case = saved_root / 'cases' / 'positive'
    positive_receipt = json.loads((positive_case / 'classification.json').read_text())
    positive_ast = positive_receipt['caller_ast_evidence']
    positive_glue = positive_ast['body_glue_evidence']
    positive_drop_loc = next(row['loc'] for row in positive_ast['call_nodes']
                             if row['callee'] == runner.GLUE_NAME)
    positive_inspection = runner._inspect_ast(positive_case / 'proof-ast.ml', ast,
                                              positive_drop_loc)
    assert positive_inspection['admitted']
    base_path = HERE.parents[1] / 'merge' / 'overnight' / 'copy-on-drop-prove.py'
    base = load('receiver_saved_replay_base', base_path)
    expected = {
        'omit_end': 'EXPECTED_RECEIVER_END_REJECTION',
        'wrong_end': 'EXPECTED_RECEIVER_END_REJECTION',
        'duplicate_end': 'EXPECTED_RECEIVER_END_REJECTION',
        'post_retirement_drop': 'EXPECTED_POST_RETIREMENT_DROP_REJECTION',
    }
    for mode, expected_classification in expected.items():
        case = saved_root / 'receiver-controls' / 'cases' / mode
        receipt = json.loads((case / 'classification.json').read_text())
        replay = runner._classify(
            case, mode, receipt['execution_receipt'],
            receipt['source_sha256_before'], receipt['source_sha256_after'],
            positive_drop_loc, tuple(positive_inspection['receiver_argument']),
            positive_glue, ast, drop_module, base.mir_helper)
        assert replay['classification'] == expected_classification, (mode, replay)
        assert replay['target_error_and_caller_trace']['matched'], mode
        assert replay['generated_glue_markers_precede_caller_error'], mode
        if mode == 'post_retirement_drop':
            assert replay['retirement_log_order_admitted']

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
