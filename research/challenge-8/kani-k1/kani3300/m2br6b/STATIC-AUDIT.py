"""Committed source/hash/format audit only. No Rust compilation or verification."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
M = json.loads((HERE / 'DIAGNOSTIC-MANIFEST.json').read_text())
I = json.loads((HERE / 'INPUTS.json').read_text())
K = M['clone']
C = 'kani-compiler/src/kani_middle/transform/check_uninit/mod.rs'
R = 'library/kani_core/src/mem_init.rs'
N = 'KANI_INITIALIZE_MEMORY_INITIALIZATION_STATE'
DELTA = (
    '// Bootstrap only verifier-owned state without instrumenting its own reset writes.\n'
    "// The harness-entry call and the initializer's runtime assignments still execute.\n"
    'const ' + N + ': KaniFunction =\n'
    '    KaniFunction::Model(KaniModel::InitializeMemoryInitializationState);\n'
)


def git(*args, repo=K, **kwargs):
    return subprocess.check_output(['git', '-C', str(repo), *args], **kwargs)


def blob(c, p):
    return git('show', c + ':' + p)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def declarations(s):
    return {m[1]: re.sub(r'\s+', '', m[0].strip()[:-1]) for m in
            re.finditer(r'(?m)^\s*(?:pub )?(?:const )?fn (\w+)[^{;]+\{', s)}


def functions(s):
    result = {}
    for m in re.finditer(r'(?m)^\s*(?:pub )?(?:const )?fn (\w+)[^{;]+\{', s):
        depth, pos = 1, m.end()
        while depth:
            depth += (s[pos] == '{') - (s[pos] == '}')
            pos += 1
        result[m[1]] = s[m.start():pos]
    return result


def markers(s):
    return re.findall(r'#\[kanitool::fn_marker = "([^"]+)"\]', s)


for ref in I['references']:
    assert sha(git('show', ref['revision'] + ':' + ref['path'], repo=ROOT)) == ref['sha256']
for deps in I['dependencies']:
    for f in deps['files']:
        assert sha(blob(deps['parent'], f['path'])) == f['sha256']
assert sha((ROOT / I['P1']['path']).read_bytes()) == I['P1']['sha256']
assert (ROOT / I['P1']['path']).stat().st_size == I['P1']['bytes']
for f in I['formatting']['tool_files']:
    assert sha(Path(f['path']).read_bytes()) == f['sha256']
rows = []
patches = []
compiler_files = []
r1 = blob('1cd96e354ec45346b61c245554a50a8af8cb5ce7', R).decode()
for v in M['variants']:
    c, p = v['sha'], v['parent']
    assert git('rev-parse', v['branch']).decode().strip() == c
    assert git('rev-parse', c + '^').decode().strip() == p
    assert git('rev-parse', c + '^{tree}').decode().strip() == v['tree']
    assert git('rev-parse', p + '^{tree}').decode().strip() == v['parent_tree']
    assert git('diff', '--name-only', p, c).decode().splitlines() == [C]
    assert git('rev-parse', c + ':kani-compiler').decode().strip() == v['compiler_tree']
    for key in ('runtime', 'compiler'):
        f = v[key]
        assert sha(blob(c, f['path'])) == f['sha256']
        assert sha(blob(p, f['path'])) == f['parent_sha256']
        assert git('rev-parse', c + ':' + f['path']).decode().strip() == f['blob']
    assert blob(c, R) == blob(p, R)
    before = blob(p, C).decode()
    after = blob(c, C).decode()
    assert before.count('const KANI_STORE_ARGUMENT:') == 1
    anchor = 'const KANI_STORE_ARGUMENT: KaniFunction = KaniFunction::Model(KaniModel::StoreArgument);\n'
    assert after == before.replace(anchor, anchor + DELTA).replace(
        '    KANI_STORE_ARGUMENT,\n', '    KANI_STORE_ARGUMENT,\n    ' + N + ',\n')
    assert after.count(N) == 2
    old_skip = before.split('const SKIPPED_ITEMS: &[KaniFunction] = &[', 1)[1].split('];', 1)[0]
    new_skip = after.split('const SKIPPED_ITEMS: &[KaniFunction] = &[', 1)[1].split('];', 1)[0]
    assert new_skip.replace('    ' + N + ',\n', '') == old_skip
    # All function bodies/normal call sites/CFG source remain byte-identical.
    assert functions(before) == functions(after)
    assert declarations(before) == declarations(after)
    guard = 'if KaniFunction::try_from(instance).map(|f| SKIPPED_ITEMS.contains(&f)).unwrap_or(false)'
    instrument = functions(after)['instrument']
    assert instrument.index(guard) < instrument.index('target_finder.find_all(&body)')
    assert 'return (false, body);' in instrument
    identity = blob(c, 'kani-compiler/src/kani_middle/kani_functions.rs').decode()
    assert '#[strum(serialize = "InitializeMemoryInitializationStateModel")]\n    InitializeMemoryInitializationState,' in identity
    assert 'Model(KaniModel)' in identity
    assert 'attributes::fn_marker(instance.def)' in identity
    assert 'try_get_kani_function(&fn_attr).ok_or(())' in identity
    providers = []
    for rel in ('ptr_uninit/mod.rs', 'delayed_ub/mod.rs'):
        path = 'kani-compiler/src/kani_middle/transform/check_uninit/' + rel
        b = blob(c, path)
        assert b == blob(p, path)
        assert 'UninitInstrumenter::run(' in b.decode()
        providers.append(dict(path=path, sha256=sha(b), unchanged=True))
    runtime = blob(c, R).decode()
    assert declarations(runtime) == declarations(r1)
    assert markers(runtime) == markers(r1) and len(markers(runtime)) == 14
    init = functions(runtime)['initialize_memory_initialization_state']
    reset = 'ARGUMENT_BUFFER = None;' if v['id'] == 'R6-02b' else 'MEM_INIT_STATE.argument_buffer_active = false;'
    assert init.count('super::any()') == 2 and reset in init
    assert 'MEM_INIT_STATE.value = false;' in init
    assert 'if selected_argument == 0 || super::any()' in functions(runtime)['store_argument']
    if v['id'] == 'R6-02b':
        assert 'static mut ARGUMENT_BUFFER: Option<ArgumentBuffer> = None;' in runtime
        assert '#[derive(Clone, Copy)]\n        struct ArgumentBuffer' in runtime
    for name in ('copy', 'copy_by_id', 'bless', 'bless_by_id', 'copy_init_state', 'copy_init_state_single'):
        assert functions(runtime)[name] == functions(r1)[name]
    patch = (HERE / v['patch']).read_bytes()
    assert patch == git('diff', '--full-index', '--binary', p, c)
    assert sha(patch) == v['patch_sha256']
    git('diff', '--check', p, c)
    identity_rows = git('show', '-s', '--format=%an <%ae>%n%cn <%ce>%n%s', c).decode().splitlines()
    assert identity_rows[:2] == ['Tiramisu-Cake <igkharin@gmail.com>'] * 2
    assert '[skip ci]' not in identity_rows[2]
    with tempfile.TemporaryDirectory(prefix='kani3300-r6b-index-') as d:
        env = dict(os.environ, GIT_INDEX_FILE=d + '/index')
        git('read-tree', p, env=env)
        git('apply', '--cached', '--check', str(HERE / v['patch']), env=env)
        git('apply', '--cached', str(HERE / v['patch']), env=env)
        assert git('write-tree', env=env).decode().strip() == v['tree']
    config = blob(c, 'rustfmt.toml')
    assert sha(config) == I['formatting']['config_sha256']
    # Format exactly committed bytes, with no worktree mutation or toolchain lookup.
    with tempfile.TemporaryDirectory(prefix='kani3300-r6b-fmt-') as d:
        temp = Path(d)
        (temp / 'rustfmt.toml').write_bytes(config)
        for path in (C, R):
            target = Path(K) / path if path == C else temp / Path(path).name
            if path == C:
                assert target.read_bytes() == blob(c, path)
            else:
                target.write_bytes(blob(c, path))
            subprocess.run([I['formatting']['tool_files'][0]['path'], '--check',
                            '--config-path', str(temp / 'rustfmt.toml'),
                            str(target)], check=True, capture_output=True)
    patches.append(patch)
    compiler_files.append(after)
    rows.append(dict(id=v['id'], sha=c, tree=v['tree'], exact_parent_runtime=True,
                     only_changed_file=C, identical_function_bodies=True,
                     added_skip_identities=['KaniModel::InitializeMemoryInitializationState'],
                     markers=len(markers(runtime)), normalized_runtime_signatures=declarations(runtime),
                     initializer_source=init.strip(), provider_bindings=providers,
                     patch_tree_reconstruction='PASSED', identity='PASSED',
                     diff_check='PASSED', pinned_rustfmt='PASSED_NOT_COMPILATION'))
assert patches[0] == patches[1] and compiler_files[0] == compiler_files[1]
assert M['variants'][0]['compiler_tree'] == M['variants'][1]['compiler_tree']
assert git('status', '--porcelain=v1') == b''
print(json.dumps(dict(schema='kani3300-m2br6b-static-v1', candidates=rows,
                     exact_compiler_delta_and_tree_match=True, historical_inputs_unchanged=True,
                     P1_hash='PASSED', frozen_dependencies='PASSED',
                     compilation='NOT_RUN', emitted_path_bindings='UNKNOWN', proof_credit=0), indent=2))
