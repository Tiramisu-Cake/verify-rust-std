"""Read committed sources only; no compiler, verifier, build or source mutation."""
from pathlib import Path
import difflib
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / 'DIAGNOSTIC-MANIFEST.json').read_text())
K = Path(MANIFEST['clone'])
P = 'library/kani_core/src/mem_init.rs'
U = 'bf9c58e662fd65c64381ef2ac97a6397ffc0693a'
R = MANIFEST['base_sha']
V02 = '48d10f9ff2a78ab0ee35e9b9c58cc28bc304ae7d'


def git(*args):
    return subprocess.check_output(['git', '-C', str(K), *args])


def blob(commit, path=P):
    return git('show', commit + ':' + path)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def declarations(source):
    found = {}
    for match in re.finditer(r'(?m)^\s*(?:pub )?(?:const )?fn (\w+)[^{]+\{', source):
        header = match.group().strip()[:-1].strip()
        found[match[1]] = re.sub(r'\s+', '', header)
    return found


def markers(source):
    result = {}
    decl = declarations(source)
    for match in re.finditer(r'#\[kanitool::fn_marker = "([^"]+)"\]', source):
        tail = source[match.end():]
        if tail.lstrip().startswith('static '):
            result[match[1]] = re.sub(r'\s+', '', tail.split(';', 1)[0])
        else:
            name = re.search(r'fn (\w+)', tail)[1]
            result[match[1]] = decl[name]
    return result


def hbuf(source, base):
    anchor = '            /// Return currently tracked memory initialization state if `ptr` points to the currently\n'
    source = base[:base.index(anchor)] + source[source.index(anchor):]
    reset = '                MEM_INIT_STATE.argument_buffer_active = false;\n'
    if reset in base:
        if reset not in source:
            source = source.replace('                MEM_INIT_STATE.value = false;\n',
                                    '                MEM_INIT_STATE.value = false;\n' + reset)
    else:
        source = source.replace(reset, '')
    arg = '        /// Information about currently tracked argument, used for passing union initialization\n'
    store = '        /// Non-deterministically store information about currently tracked argument in the argument\n'
    return source[:source.index(arg if arg in source else store)] + base[base.index(arg if arg in base else store):]


def copy_span(source):
    start = source.index('            /// Copy memory initialization state by non-deterministically switching the tracked object and\n')
    end = source.index('            /// Return currently tracked memory initialization state if `ptr` points to the currently\n', start)
    return start, end


def hcopy(source, base):
    a, b = copy_span(source)
    x, y = copy_span(base)
    return source[:a] + base[x:y] + source[b:]


def arities(source):
    expected = {'copy': 3, 'copy_by_id': 5, 'bless': 2, 'bless_by_id': 3,
                'get': 2, 'set': 3, 'get_slice': 3, 'set_slice': 4}
    result = []
    pattern = r'\.(copy_by_id|bless_by_id|copy|bless|get_slice|set_slice|get|set)::<[^>]+>\('
    for match in re.finditer(pattern, source):
        depth = 1
        end = match.end()
        while depth:
            depth += (source[end] == '(') - (source[end] == ')')
            end += 1
        args = source[match.end():end - 1].strip().rstrip(',')
        # These actual model calls have no nested comma-bearing expressions.
        count = len(args.split(',')) if args else 0
        assert count == expected[match[1]], (match[1], args)
        result.append({'method': match[1], 'line': source.count('\n', 0, match.start()) + 1,
                       'arguments': count, 'args': args})
    return result


u, r = blob(U).decode(), blob(R).decode()
assert blob(V02) == u.encode()
assert len(markers(u)) == len(markers(r)) == 14
assert markers(u) == markers(r)
assert len([x for x in markers(r) if x != 'KaniMemoryInitializationState']) == 13
rows = []
for variant in MANIFEST['variants']:
    commit = variant['sha']
    s = blob(commit).decode()
    assert markers(s) == markers(r)
    assert git('diff', '--name-only', R, commit).decode().splitlines() == [P]
    assert git('rev-parse', commit + '^').decode().strip() == R
    assert git('rev-parse', commit + '^{tree}').decode().strip() == variant['tree']
    assert sha(s.encode()) == variant['runtime_sha256']
    assert sha((HERE / variant['patch']).read_bytes()) == variant['patch_sha256']
    assert git('diff', '--full-index', '--binary', R, commit, '--', P) == (HERE / variant['patch']).read_bytes()
    subprocess.run(['git', '-C', str(K), 'diff', '--check', R, commit], check=True)
    # Entire trees equal outside the only allowed file, hence compiler/tests/driver/toolchain are frozen.
    names = git('grep', '-l', '-E', r'copy_by_id|bless_by_id|argument_buffer_(active|saved|selected|layout)|ARGUMENT_BUFFER|ArgumentBuffer', commit, '--', '*.rs').decode().splitlines()
    assert names and all(line.split(':', 1)[1] == P for line in names)
    for name in ('copy', 'copy_by_id', 'bless', 'bless_by_id'):
        assert declarations(s)[name] == declarations(r)[name]
    fields = set(re.findall(r'pub (\w+):', s[s.index('struct MemoryInitializationState'):s.index('impl MemoryInitializationState')]))
    constructor = s[s.index('pub const fn new()'):s.index('            /// Return currently tracked')]
    assert set(re.findall(r'(\w+):', constructor)) == fields
    refs = set(re.findall(r'MEM_INIT_STATE\.(argument_buffer_\w+)', s))
    assert refs <= fields
    if variant['id'] == 'R5-01':
        assert hbuf(r, u) == s and hcopy(s, r) == s
        assert 'argument_buffer_' not in s
        assert '#[derive(Clone, Copy)]\n        struct ArgumentBuffer' in s
        assert 'static mut ARGUMENT_BUFFER: Option<ArgumentBuffer> = None;' in s
        assert 'copy_init_state_single::<LAYOUT_SIZE, ()>(buffer.saved_address, to_ptr);' in s
    else:
        assert hbuf(s, r) == s and hcopy(s, r) == r
        assert 'ARGUMENT_BUFFER' not in s and 'saved_address' not in s
        assert 'self.tracked_offset += to_offset - from_offset;' in s
        assert 'self.bless_by_id::<LAYOUT_SIZE>(to_obj, to_offset, 1);' in s
        core = s[s.index('                if self.tracked_object_id == from_obj', s.index('pub fn copy_by_id')):s.index('\n            }', s.index('                if self.tracked_object_id == from_obj', s.index('pub fn copy_by_id')))]
        legacy = u[u.index('                if self.tracked_object_id == from_obj', u.index('pub fn copy')):u.index('\n            }', u.index('                if self.tracked_object_id == from_obj', u.index('pub fn copy')))]
        assert core == legacy.replace('self.bless::<LAYOUT_SIZE>(to_ptr, 1);', 'self.bless_by_id::<LAYOUT_SIZE>(to_obj, to_offset, 1);')
    rows.append({'id': variant['id'], 'markers': len(markers(s)), 'model_functions': 13,
                 'normalized_signatures_match': True, 'constructor_fields': sorted(fields),
                 'external_helper_references': 0, 'method_calls': arities(s)})
assert hbuf(hcopy(r, r), r) == r
assert hcopy(hbuf(r, u), u) == u
assert hbuf(hcopy(r, u), u) == u
second = blob(MANIFEST['variants'][1]['sha']).decode()
with_glue = hbuf(second, u)
assert hcopy(with_glue, u) == u
diff = git('diff', '--numstat', U, R, '--', P).decode().strip()
assert diff == '77\t33\t' + P
print(json.dumps({'source_audit': rows, 'markers_and_signatures': markers(r),
                  'reconstruction': {'R1_R1': sha(r.encode()), 'U_U_without_GLUE': sha(u.encode()),
                                     'V02': sha(blob(V02)), 'U_U_with_GLUE': sha(with_glue.encode()),
                                     'GLUE_removed': sha(hcopy(with_glue, u).encode())},
                  'delta_numstat': diff, 'compilation': 'NOT_RUN', 'proof_credit': 0}, indent=2))
