#!/usr/bin/env python3
"""Bounded source checks only. Does not execute Rust or any verifier."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1])
base = '8e01eb2aff5183c53403e1d1e73e573ce28d3095'
runtime = 'library/kani_core/src/mem_init.rs'
contract = 'kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs'

def git(*args):
    return subprocess.check_output(['git', '-C', str(repo), *args])

def old(path):
    return git('show', f'{base}:{path}').decode()

def block(text, anchor):
    start = text.index(anchor)
    opening = text.index('{', start)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == '{') - (text[end] == '}')
        if depth == 0:
            return text[start:end + 1]
    raise AssertionError(anchor)

def tokens(text):
    pat = r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/|[A-Za-z_][A-Za-z_0-9]*|[0-9]+|[^\s]'
    return [t for t in re.findall(pat, text) if not t.startswith(('//', '/*'))]

before, after = old(runtime), (repo / runtime).read_text()
fields = dict(re.findall(r'pub (\w+): ([^,\n]+),', block(after, 'struct ArgumentBuffer')))
expected = dict(re.findall(r'pub (\w+): ([^,\n]+),', block(before, 'struct ArgumentBuffer')))
del expected['relative_offset']
expected.update(saved_base='*const u8', saved_byte='*const u8')
assert fields == expected and len(fields) == 13
assert list(fields.values()).count('usize') == 8
assert list(fields.values()).count('bool') == 3
assert list(fields.values()).count('*const u8') == 2
assert 'ARGUMENT_BUFFER.relative_offset' not in after
assert before.count('fn_marker = "KaniMemoryInitializationState"') == after.count('fn_marker = "KaniMemoryInitializationState"') == 1
assert before.count('fn_marker = "KaniMemoryInitializationArgumentBuffer"') == after.count('fn_marker = "KaniMemoryInitializationArgumentBuffer"') == 1
assert block(before, 'impl MemoryInitializationState') == block(after, 'impl MemoryInitializationState')
for name in re.findall(r'\bfn (\w+)', before):
    if name not in ('new', 'store_argument', 'load_argument'):
        assert block(before, f'fn {name}') == block(after, f'fn {name}'), name
constructor = block(block(after, 'impl ArgumentBuffer'), 'pub const fn new')
assert constructor.count('kani_mem_init_core::ptr::null()') == 2
for name in fields:
    assert re.search(r'\b' + name + r':', constructor), name
for name in ['store_argument', 'load_argument']:
    assert before[before.index('fn '+name):before.index('{', before.index('fn '+name))] == after[after.index('fn '+name):after.index('{', after.index('fn '+name))]
store_before, store_after = [block(t, 'fn store_argument') for t in (before, after)]
start_before = store_before.index('ARGUMENT_BUFFER.has_witness =')
end_before = store_before.index('ARGUMENT_BUFFER.value = MEM_INIT_STATE.value;') + len('ARGUMENT_BUFFER.value = MEM_INIT_STATE.value;')
start_after = store_after.index('let has_witness =')
end_after = store_after.index('ARGUMENT_BUFFER.value = captured_value;') + len('ARGUMENT_BUFFER.value = captured_value;')
assert tokens(store_before[:start_before]+store_before[end_before:]) == tokens(store_after[:start_after]+store_after[end_after:])
assert tokens(store_before[start_before:store_before.index(';', start_before)].split(' = ', 1)[1]) == tokens(store_after[start_after:store_after.index(';', start_after)].split(' = ', 1)[1])
assert store_after.index('let captured_value = MEM_INIT_STATE.value;') < store_after.index('let (saved_base, saved_byte)')
assert store_after.index('if has_witness') < store_after.index('wrapping_add(relative_offset)')
assert store_after.count('wrapping_add(') == 1
load_before, load_after = [block(t, 'fn load_argument') for t in (before, after)]
a = load_before.index('let relative_offset = ARGUMENT_BUFFER.relative_offset;')
b = a + len('let relative_offset = ARGUMENT_BUFFER.relative_offset;')
c = load_after.index('let saved_base = ARGUMENT_BUFFER.saved_base;')
d = load_after.index('MEM_INIT_STATE.tracked_object_id =')
assert tokens(load_before[:a]+load_before[b:]) == tokens(load_after[:c]+load_after[d:])
assert load_after.index('if selected && ARGUMENT_BUFFER.has_witness && super::any()') < c
assert 'MEM_INIT_STATE.value = ARGUMENT_BUFFER.value && layout[relative_offset];' in load_after
for forbidden in ['.read(', '.as_ref(', '.offset_from(', 'is_allocated(', 'object_size(', 'assume(', 'copy_init_state_single(']:
    assert forbidden not in store_after + load_after, forbidden
assert after.count('shadow carrier store ') == 5 and after.count('shadow carrier load ') == 3
for target in ('saved_base', 'saved_byte'):
    assert after.count('ARGUMENT_BUFFER.'+target) == 2  # one store, one guarded load
compiler_before, compiler_after = old(contract), (repo / contract).read_text()
replacement = '("saved_base", Type::unsigned_int(8).to_pointer()),\n                    ("saved_byte", Type::unsigned_int(8).to_pointer()),'
assert compiler_before.replace('("relative_offset", Type::size_t()),', replacement) == compiler_after
field_list = compiler_after[compiler_after.index('for (field, expected_type) in ['):compiler_after.index('] {', compiler_after.index('for (field, expected_type) in ['))]
assert set(re.findall(r'\("(\w+)"', field_list)) == set(fields)
assert 'let target = buffer.to_expr().member(field, &self.symbol_table);' in compiler_after
assert 'assigns.push(Lambda::as_contract_for(&goto_annotated_fn_typ, None, target));' in compiler_after
changed = set(git('diff', '--name-only', base).decode().splitlines())
test_delta = git('diff', '--name-status', base, '--', 'tests').decode().splitlines()
assert len(test_delta) == 4 and all(line.startswith('A\ttests/expected/uninit/private-transfer-pointer/') for line in test_delta)
new_tests = {line.split('\t')[1] for line in test_delta}
assert changed == {runtime, contract} | new_tests, changed
control_manifest = json.loads((Path(__file__).parent.parent / 'm2br8c/TEST-MANIFEST.json').read_text())
control_patch = git('diff', '--binary', '--full-index', base, '--', 'tests/expected/uninit/private-transfer-pointer/')
assert hashlib.sha256(control_patch).hexdigest() == control_manifest['patch']['sha256']
subprocess.run(['git', '-C', str(repo), 'diff', '--check', base], check=True)
# Finite arithmetic sanity, not proof credit or backend execution.
cases = 0
for width in range(2, 9):
    for offset_width in range(1, width):
        modulus, word = 1 << offset_width, 1 << width
        for base_offset in range(modulus):
            for relative in range(modulus-base_offset):
                encoded = (base_offset + relative) % modulus
                assert (encoded-base_offset) % word == relative
                cases += 1
assert ((250+10) % 256 - 250) % 65536 != 10
assert ((0+256) % 256 - 0) % 65536 != 256
print(json.dumps({'status':'PASS_SOURCE_ONLY_NOT_COMPILATION', 'base':base,
                  'changed_files':sorted(changed), 'fields':fields,
                  'base_tests_tree':git('rev-parse', f'{base}:tests').decode().strip(),
                  'composed_tests_tree':git('rev-parse', 'HEAD:tests').decode().strip(),
                  'new_controls_patch_sha256':hashlib.sha256(control_patch).hexdigest(),
                  'arithmetic_sanity_cases':cases, 'proof_credit':0}, indent=2))
