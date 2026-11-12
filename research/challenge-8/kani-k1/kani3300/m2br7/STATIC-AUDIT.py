#!/usr/bin/env python3
"""Bounded source equivalence/coverage checks; never executes Rust or a verifier."""
import hashlib
import json
import re
import subprocess
import sys

repo, base, b0, candidate = sys.argv[1:]


def git(*args):
    return subprocess.check_output(['git', '-C', repo, *args])


def source(rev, path):
    return git('show', f'{rev}:{path}').decode()


def tokens(text):
    # Preserve strings/operators; discard only whitespace and comments.
    pattern = r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/|[A-Za-z_][A-Za-z_0-9]*|[0-9]+|[^\s]'
    return [t for t in re.findall(pattern, text) if not t.startswith(('//', '/*'))]


def block(text, anchor):
    start = text.index(anchor)
    opening = text.index('{', start)
    # These audited definitions have no brace-bearing strings/comments.
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == '{') - (text[end] == '}')
        if depth == 0:
            return text[start:end + 1]
    raise AssertionError(anchor)


runtime = 'library/kani_core/src/mem_init.rs'
contract = 'kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs'
skip = 'kani-compiler/src/kani_middle/transform/check_uninit/mod.rs'
old, new = source(base, runtime), source(candidate, runtime)
assert source(b0, runtime) == old
assert git('diff', '--name-only', base, b0).decode().splitlines() == [skip]
old_skip, new_skip = source(base, skip), source(b0, skip)
added = '''// Bootstrap only verifier-owned state without instrumenting its own reset writes.
// The harness-entry call and the initializer's runtime assignments still execute.
const KANI_INITIALIZE_MEMORY_INITIALIZATION_STATE: KaniFunction =
    KaniFunction::Model(KaniModel::InitializeMemoryInitializationState);
'''
assert new_skip.replace(added, '').replace('    KANI_INITIALIZE_MEMORY_INITIALIZATION_STATE,\n', '') == old_skip
assert source(candidate, skip) == new_skip
assert git('diff', '--name-only', b0, candidate).decode().splitlines() == [contract, runtime]

old_fields = dict(re.findall(r'pub (argument_buffer_\w+): (usize|bool)', old))
buffer = block(new, 'struct ArgumentBuffer')
fields = dict(re.findall(r'pub (\w+): (usize|bool)', buffer))
assert {'argument_buffer_' + k: v for k, v in fields.items()} == old_fields
assert len(fields) == 12 and list(fields.values()).count('usize') == 9
assert dict(re.findall(r'pub (\w+): (usize|bool)', block(new, 'struct MemoryInitializationState'))) == {
    'tracked_object_id': 'usize', 'tracked_offset': 'usize', 'value': 'bool'}
old_init = block(old, 'pub const fn new')
new_main_init = block(block(new, 'impl MemoryInitializationState'), 'pub const fn new')
new_buffer_init = block(block(new, 'impl ArgumentBuffer'), 'pub const fn new')
initial_values = dict(re.findall(r'\b(\w+): (false|0)\b', old_init))
combined = dict(re.findall(r'\b(\w+): (false|0)\b', new_main_init))
combined.update({'argument_buffer_' + k: v for k, v in re.findall(r'\b(\w+): (false|0)\b', new_buffer_init)})
assert combined == initial_values and len(combined) == 15

names = re.findall(r'\bfn (\w+)', old)
assert len(names) == len(set(names))
normalized = {}
for name in names:
    if name == 'new':
        continue
    before = block(old, 'fn ' + name)
    after = block(new, 'fn ' + name).replace('ARGUMENT_BUFFER.', 'MEM_INIT_STATE.argument_buffer_')
    assert tokens(before) == tokens(after), name
    normalized[name] = hashlib.sha256(json.dumps(tokens(before)).encode()).hexdigest()
old_markers = re.findall(r'fn_marker = "([^"]+)"', old)
new_markers = re.findall(r'fn_marker = "([^"]+)"', new)
assert new_markers.count('KaniMemoryInitializationState') == 1
new_markers.remove('KaniMemoryInitializationArgumentBuffer')
assert new_markers == old_markers
assert not re.search(r'\bARGUMENT_BUFFER\s*=', new)
assert 'argument_buffer_' not in new
reset = block(new, 'fn initialize_memory_initialization_state')
assert re.findall(r'ARGUMENT_BUFFER\.(\w+)\s*=(?!=)', reset) == ['active', 'selected_argument', 'has_witness']

c = source(candidate, contract)
target_fields = dict(re.findall(r'\("(\w+)", Type::(c_bool|size_t)\(\)\)', c))
assert target_fields == {k: 'c_bool' if v == 'bool' else 'size_t' for k, v in fields.items()}
assert len(re.findall(r'\("\w+", Type::(?:c_bool|size_t)\(\)\)', c)) == 12
assert 'buffer.to_expr().member(field, &self.symbol_table)' in c
assert 'None, main.to_expr()' in c
assert 'None, buffer.to_expr()' not in c
old_c = source(base, contract)
boundary = '        // The last argument is a tuple with addresses that can be modified.'
assert old_c[old_c.index(boundary):] == c[c.index(boundary):]
assert git('rev-parse', base + ':tests') == git('rev-parse', candidate + ':tests')
unchanged = [
    'kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs',
    'kani-compiler/src/kani_middle/anonymous_allocations.rs',
    'kani-compiler/src/kani_middle/kani_functions.rs',
    'kani-compiler/src/codegen_cprover_gotoc/compiler_interface.rs',
    'kani-compiler/src/codegen_cprover_gotoc/codegen/static_var.rs',
]
unchanged_hashes = {}
for path in unchanged:
    assert git('show', base + ':' + path) == git('show', candidate + ':' + path)
    unchanged_hashes[path] = hashlib.sha256(git('show', candidate + ':' + path)).hexdigest()

operations = {}
for field in fields:
    operations[field] = {}
    for name in ['initialize_memory_initialization_state', 'begin_argument_transfer', 'store_argument', 'load_argument']:
        body = block(new, 'fn ' + name)
        uses = re.findall(r'ARGUMENT_BUFFER\.' + field + r'\b\s*(\+=|-=|=(?!=))?', body)
        if uses:
            operations[field][name] = {'writes': sum(bool(x) for x in uses), 'non_lhs_uses': sum(not x for x in uses)}

print(json.dumps({'status': 'STATIC_PASS_NOT_COMPILATION', 'base': base, 'B0': b0,
                  'B1': candidate, 'normalized_function_sha256': normalized,
                  'fields': fields, 'operations': operations, 'unchanged_sha256': unchanged_hashes,
                  'compilation': 'NOT_RUN', 'G1': 'NOT_RUN', 'G2': 'NOT_RUN'}, indent=2))
