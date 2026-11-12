"""Bounded committed-source/hash audit only; no compiler/verifier/build."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
M = json.loads((HERE / 'DIAGNOSTIC-MANIFEST.json').read_text())
I = json.loads((HERE / 'INPUTS.json').read_text())
K = M['clone']
P = 'library/kani_core/src/mem_init.rs'
R = M['base_sha']


def git(*args, **kwargs):
    return subprocess.check_output(['git', '-C', K, *args], **kwargs)


def blob(c, p=P):
    return git('show', c + ':' + p)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def declarations(s):
    return {m[1]: re.sub(r'\s+', '', m[0].strip()[:-1]) for m in
            re.finditer(r'(?m)^\s*(?:pub )?(?:const )?fn (\w+)[^{]+\{', s)}


def markers(s):
    result = {}
    ds = declarations(s)
    for m in re.finditer(r'#\[kanitool::fn_marker = "([^"]+)"\]', s):
        tail = s[m.end():]
        result[m[1]] = (re.sub(r'\s+', '', tail.split(';', 1)[0])
                        if tail.lstrip().startswith('static ')
                        else ds[re.search(r'fn (\w+)', tail)[1]])
    return result


def span(s, start, end):
    return s[s.index(start):s.index(end, s.index(start))]


def functions(s):
    result = {}
    for m in re.finditer(r'(?m)^\s*(?:pub )?(?:const )?fn (\w+)[^{]+\{', s):
        depth, pos = 1, m.end()
        while depth:
            depth += (s[pos] == '{') - (s[pos] == '}')
            pos += 1
        result[m[1]] = s[m.start():pos]
    return result


def arities(s):
    expected = {'copy': 3, 'copy_by_id': 5, 'bless': 2, 'bless_by_id': 3,
                'get': 2, 'set': 3, 'get_slice': 3, 'set_slice': 4}
    rows = []
    for m in re.finditer(r'\.(copy_by_id|bless_by_id|copy|bless|get_slice|set_slice|get|set)::<[^>]+>\(', s):
        depth, pos = 1, m.end()
        while depth:
            depth += (s[pos] == '(') - (s[pos] == ')')
            pos += 1
        args = s[m.end():pos-1].strip().rstrip(',')
        # These actual expressions contain no nested comma-bearing subexpressions.
        count = len(args.split(',')) if args else 0
        assert count == expected[m[1]], (m[1], args)
        rows.append(dict(method=m[1], arguments=count, args=args))
    return rows


r = blob(R).decode()
u = blob(M['U']).decode()
t = blob(M['R5_01_template']).decode()
reset_r = '                MEM_INIT_STATE.argument_buffer_active = false;\n'
reset_u = '                ARGUMENT_BUFFER = None;\n'
anchor = '                MEM_INIT_STATE.value = false;\n'
mandatory = 'if selected_argument == 0 || super::any() {'
local = '            let should_store: bool = super::any();\n            if should_store {'
assert len(markers(r)) == 14 and markers(r) == markers(u) == markers(t)
assert len(markers(r)) - 1 == 13
copy_start = '            /// Copy memory initialization state by non-deterministically switching the tracked object and\n'
copy_end = '            /// Return currently tracked memory initialization state if `ptr` points to the currently\n'
hc = span(r, copy_start, copy_end)
assert hc == span(t, copy_start, copy_end)
rows = []
for pin in I['pins']:
    for f in pin['files']:
        assert sha(blob(pin['sha'], f['path'])) == f['sha256']
for ref in I['references']:
    root = HERE.parents[4]
    b = subprocess.check_output(['git', '-C', str(root), 'show', ref['revision'] + ':' + ref['path']])
    assert sha(b) == ref['sha256']
assert sha((HERE.parents[4] / I['P1']['path']).read_bytes()) == I['P1']['sha256']
for tool in I['formatting']['tool_files']:
    assert sha(Path(tool['path']).read_bytes()) == tool['sha256']
assert sha(blob(R, 'rustfmt.toml')) == I['formatting']['config_sha256']

for v in M['variants']:
    c = v['sha']
    s = blob(c).decode()
    assert git('rev-parse', c + '^').decode().strip() == R
    assert git('diff', '--name-only', R, c).decode().splitlines() == [P]
    assert git('rev-parse', c + '^{tree}').decode().strip() == v['tree']
    assert git('rev-parse', c + ':' + P).decode().strip() == v['runtime_blob']
    assert sha(s.encode()) == v['runtime_sha256']
    patch = (HERE / v['patch']).read_bytes()
    assert sha(patch) == v['patch_sha256']
    assert patch == git('diff', '--full-index', '--binary', R, c, '--', P)
    git('diff', '--check', R, c)
    identity = git('show', '-s', '--format=%an <%ae>%n%cn <%ce>%n%s', c).decode().splitlines()
    assert identity[:2] == ['Tiramisu-Cake <igkharin@gmail.com>'] * 2
    assert '[skip ci]' not in identity[2]
    # Reconstruct exact candidate tree from its patch in a disposable index.
    with tempfile.TemporaryDirectory(prefix='kani3300-r6-index-') as d:
        env = dict(os.environ, GIT_INDEX_FILE=d + '/index')
        git('read-tree', R, env=env)
        git('apply', '--cached', '--check', str(HERE / v['patch']), env=env)
        git('apply', '--cached', str(HERE / v['patch']), env=env)
        assert git('write-tree', env=env).decode().strip() == v['tree']
    assert markers(s) == markers(r)
    assert declarations(s) == declarations(r)
    assert span(s, copy_start, copy_end) == hc
    assert all(functions(s)[n] == functions(r)[n] for n in
               functions(r) if n not in ('new', 'initialize_memory_initialization_state',
                                         'store_argument', 'load_argument'))
    fields = set(re.findall(r'pub (\w+):', span(s, 'struct MemoryInitializationState', 'impl MemoryInitializationState')))
    ctor = functions(s)['new']
    assert set(re.findall(r'(\w+):', ctor)) == fields
    assert set(re.findall(r'MEM_INIT_STATE\.(argument_buffer_\w+)', s)) <= fields
    names = git('grep', '-l', '-E', r'copy_by_id|bless_by_id|argument_buffer_(active|saved|selected|layout)|ARGUMENT_BUFFER|ArgumentBuffer', c, '--', '*.rs').decode().splitlines()
    assert names and all(n.split(':', 1)[1] == P for n in names)
    if v['id'] == 'R6-01':
        init = r.index('fn initialize_memory_initialization_state()')
        expected = (r[:init] + r[init:].replace(reset_r, '', 1)).replace(mandatory, 'if super::any() {')
        assert expected == s
        inverse = s.replace('if super::any() {', mandatory).replace(anchor, anchor + reset_r)
        assert inverse == r
        assert functions(s)['new'] == functions(r)['new']
        assert functions(s)['load_argument'] == functions(r)['load_argument']
        assert s.count(reset_r) == 1 and 'ARGUMENT_BUFFER' not in s
        reconstructed = R
    else:
        assert t.count(local) == 1
        expected = t.replace(local, '            ' + mandatory).replace(anchor, anchor + reset_u)
        assert expected == s
        inverse = s.replace('            ' + mandatory, local).replace(anchor + reset_u, anchor)
        assert inverse == t
        assert functions(s)['new'] == functions(u)['new']
        assert functions(s)['load_argument'] == functions(u)['load_argument']
        assert '#[derive(Clone, Copy)]\n        struct ArgumentBuffer' in s
        assert 'static mut ARGUMENT_BUFFER: Option<ArgumentBuffer> = None;' in s
        assert 'argument_buffer_' not in s and s.count(reset_u) == 2
        assert 'copy_init_state_single::<LAYOUT_SIZE, ()>(buffer.saved_address, to_ptr);' in s
        reconstructed = M['R5_01_template']
    site_rows = []
    for number, line in enumerate(s.splitlines(), 1):
        if ('ARGUMENT_BUFFER' in line or 'argument_buffer_' in line or
                'if selected_argument == 0' in line or 'if super::any()' in line):
            site_rows.append(dict(line=number, source=line.strip()))
    rows.append(dict(id=v['id'], sha=c, tree=v['tree'], markers=14, model_functions=13,
                     normalized_all_signatures_match=True, exact_R1_Hcopy_GLUE_sha256=sha(hc.encode()),
                     inverse_Hepoch_restores_commit=reconstructed, inverse_runtime_sha256=sha(inverse.encode()),
                     constructor_fields=sorted(fields), external_helper_references=0,
                     method_calls=arities(s), source_sites=site_rows,
                     exact_patch_tree_reconstruction=True, diff_check='PASSED'))
print(json.dumps(dict(schema='kani3300-m2br6-static-v1', candidates=rows,
                      markers_and_signatures=markers(r), internal_and_model_signatures=declarations(r),
                      endpoints=dict(R1_R1=sha(r.encode()), U_U_Hcopy_GLUE_R1=sha(t.encode())),
                      input_and_dependency_hashes='PASSED', compilation='NOT_RUN',
                      pinned_rustfmt=I['formatting'],
                      actual_retained_binding='UNKNOWN', proof_credit=0), indent=2))
