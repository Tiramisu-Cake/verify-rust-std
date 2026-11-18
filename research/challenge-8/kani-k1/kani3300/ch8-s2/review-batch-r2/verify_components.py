"""W14 immutable Git-object checks; no compiler, full runner, or dispatch."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
G = HERE.parents[5]
PACK = HERE.parent
S = Path('/root/verify-rust-std-ch8-s2-r2-final-w13')
C = Path('/root/kani-ch8-s2-diagnostics-r2-r1-w11')
SOURCE = 'efb1aba7fc6445cba6cd75154713b598c9e2579d'
CONTROL = '472be8c3794d7a4530760ab7d5eae4ce950aa01c'
OLD_SOURCE = '9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6'
OLD_CONTROL = 'b678fb6cdd5edf69a4e952167422f36a45a3d6cb'
BATCH = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs'

def git(repo, *args, env=None):
    return subprocess.check_output(['git', '-C', str(repo), *args], env=env)

def sha(data):
    return hashlib.sha256(data).hexdigest()

def packet(name, commit, count):
    path = PACK/name
    rel = path.relative_to(G).as_posix()
    files = git(G, 'ls-tree', '-r', '--name-only', commit, '--', rel).decode().splitlines()
    assert len(files) == count
    result = []
    for file in files:
        data = git(G, 'show', commit+':'+file)
        assert data == (G/file).read_bytes(), file
        result.append({'path': str(Path(file).relative_to(rel)), 'sha256': sha(data)})
    manifest = []
    for line in (path/'MANIFEST.sha256').read_text().splitlines():
        digest, file = line.split('  ', 1)
        assert sha((path/file).read_bytes()) == digest, file
        manifest.append(file)
    assert set(manifest) == {r['path'] for r in result} - {'MANIFEST.sha256'}
    return {'commit': commit, 'files': result, 'manifest_count': len(manifest)}

def replay(repo, package, patch, target):
    data = (package/patch['path']).read_bytes()
    assert sha(data) == patch['sha256']
    assert data == git(repo, 'diff', '--binary', patch['base'], target)
    with tempfile.TemporaryDirectory(prefix='w14-index-') as tmp:
        env = {**os.environ, 'GIT_INDEX_FILE': str(Path(tmp)/'index')}
        git(repo, 'read-tree', patch['base'], env=env)
        git(repo, 'apply', '--cached', str(package/patch['path']), env=env)
        tree = git(repo, 'write-tree', env=env).decode().strip()
    assert tree == patch['target_tree']
    return {**patch, 'replayed_tree': tree, 'exact_git_diff': True}

def main():
    packets = {name: packet(name, commit, count) for name, commit, count in [
        ('batch-r2', '714c1ca56dd7cf352ae6feebe5e252178cdb63b2', 40),
        ('runner-diagnostics-r2-r1', 'a8e3cb30c617a6dee07fa847f1f23470d59783e3', 28)]}
    sp, rp = PACK/'batch-r2', PACK/'runner-diagnostics-r2-r1'
    sid = json.loads((sp/'IDENTITIES.json').read_text())
    rid = json.loads((rp/'IDENTITIES.json').read_text())
    for repo, pin, tree, parent in [
        (S, SOURCE, '4563e06722871ae5eafdf6d288afa21a406b6ba8', '97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a'),
        (C, CONTROL, '4835c615d20e6606ddcdc64bbb8314973cec141b', '9e14e033f9ee31522b571c127609dcdff76d230b')]:
        assert git(repo, 'rev-parse', 'HEAD').decode().strip() == pin
        assert git(repo, 'rev-parse', pin+'^{tree}').decode().strip() == tree
        assert git(repo, 'rev-parse', pin+'^').decode().strip() == parent
        assert not git(repo, 'status', '--porcelain=v1').strip()
    assert sid['source']['sha'] == SOURCE and rid['control']['sha'] == CONTROL
    for rel, digest in sid['source']['files'].items():
        assert sha(git(S, 'show', SOURCE+':'+rel)) == digest
    patches = []
    for patch in json.loads((sp/'PATCHES.json').read_text()):
        # Old composed control is explicitly not a combined GO candidate.
        repo, pin = (S, SOURCE) if patch['path'].startswith('SOURCE-') else (C, sid['control']['sha'])
        patches.append(replay(repo, sp, patch, pin))
    for patch in json.loads((rp/'PATCHES.json').read_text()):
        patches.append(replay(C, rp, patch, CONTROL))
    for rel, digest in rid['source']['files'].items():
        repo = Path(rid['source']['worktree'])
        assert sha(git(repo, 'show', OLD_SOURCE+':'+rel)) == digest
    old = json.loads(git(C, 'show', OLD_CONTROL+':ch8-s1-control/CI-REQUEST.json'))
    new = json.loads(git(C, 'show', CONTROL+':ch8-s1-control/CI-REQUEST.json'))
    assert new.keys() == old.keys()
    assert [k for k in old if old[k] != new[k]] == ['ci_payload_sha256']
    delta = git(C, 'diff', '--name-only', OLD_CONTROL, CONTROL).decode().splitlines()
    assert delta == ['ch8-s1-control/CI-REQUEST.json', 'ch8-s1-control/pack_evidence.py',
                     'ch8-s1-control/rustc_diagnostics.py', 'ch8-s1-control/test_rustc_diagnostics.py']
    for rel, digest in new['ci_payload_sha256'].items():
        assert sha(git(C, 'show', CONTROL+':'+rel)) == digest
    for rel in ('ch8-s1-control/runner.py', 'ch8-s1-control/check_package.py',
                'ch8-s1-control/test_runner.py', '.github/workflows/ch8-s2.yml'):
        assert git(C, 'show', CONTROL+':'+rel) == git(C, 'show', OLD_CONTROL+':'+rel)
    assert len(new['rows']) == 11
    assert sum(r['required_cover_count'] for r in new['rows']) == 20
    assert sum(r['expected'] == 'DETECTED' for r in new['rows']) == 6
    # Use published source-component policies plus exact unchanged dependencies.
    sys.path[:0] = [str(sp), str(C/'ch8-s1-control')]
    import cfg_pfc
    request = json.loads((sp/'CI-REQUEST.json').read_text())
    matrix = cfg_pfc.check(S, request)
    assert matrix == json.loads((sp/'CFG-PFC-MAP.json').read_text())
    # The packet copies the policy but not its sibling fixture. Provide the
    # exact committed baseline fixture in a disposable module location.
    with tempfile.TemporaryDirectory(prefix='w14-policy-fixture-') as tmp:
        location = Path(tmp)/'s2_policy.py'
        location.write_bytes((sp/'s2_policy.py').read_bytes())
        fixture = location.parent/'fixtures/s2-r1-batch.rs.txt'
        fixture.parent.mkdir()
        fixture.write_bytes(git(S, 'show', OLD_SOURCE+':'+BATCH))
        assert fixture.read_bytes() == git(C, 'show', sid['control']['sha']+':ch8-s1-control/fixtures/s2-r1-batch.rs.txt')
        policy = types.ModuleType('w14_source_policy')
        policy.__file__ = str(location)
        exec(compile(location.read_bytes(), str(location), 'exec'), policy.__dict__)
        assert policy.validate_source(S, request)
    assert git(S, 'diff', '--name-only', OLD_SOURCE, SOURCE).decode().strip() == BATCH
    before = git(S, 'show', OLD_SOURCE+':'+BATCH).decode()
    after = git(S, 'show', SOURCE+':'+BATCH).decode()
    def functions(text):
        return {i['head'][cfg_pfc.kind(i, 'fn')][0]: i for i in cfg_pfc.items(text)[1] if cfg_pfc.kind(i, 'fn') is not None}
    a, b = functions(before), functions(after)
    for root in request['rows']:
        name = root['id']
        assert a[name]['body'] == b[name]['body'] and a[name]['head'] == b[name]['head']
    for name in ('general32_assumed', 'general32_weak'):
        row = next(r for r in matrix['rows'] if r['id'] == name)
        assert any(x['target'].endswith('::sort8_stable') for x in row['ordinary_stubs_no_pfc_required'])
    compiled = json.loads((sp/'COMPILED-ITEMS-MAP.json').read_text())
    verified_files = []
    base = S/'library/core/src/slice/sort/shared/smallsort/verify'
    for path in sorted(base.rglob('*.rs')):
        rel = str(path.relative_to(S))
        assert sha(path.read_bytes()) == compiled['source_sha256'][rel]
        tokens = cfg_pfc.tokens(path.read_text())
        assert 'stub_verified(sort8_stable)' not in cfg_pfc.spelling(tokens)
        if any(t == 'stub_verified' for t, _ in tokens): verified_files.append(rel)
        if rel != BATCH: assert path.read_bytes() == git(S, 'show', OLD_SOURCE+':'+rel)
    assert verified_files == compiled['all_verified_use_files']
    assert len(compiled['outside_primary_gate']) == 6
    # Keep full supplemental map for human review of macro registrations/cfgs.
    for item in compiled['outside_primary_gate']:
        pfc = item['matching_pfc']
        assert 'proof_for_contract' in (S/pfc['file']).read_text().splitlines()[pfc['attribute_line']-1]
    return {'state': 'PASS', 'packets': packets, 'source': sid['source'], 'runner': rid['control'],
            'patches': patches, 'repair_delta_paths': delta, 'unchanged_request_fields': 'ALL_EXCEPT_PAYLOAD_HASHES',
            'roots': 11, 'covers': 20, 'exact_negatives': 6, 'cfg_map': matrix,
            'source_root_bodies_signatures_assertions_covers': 'EXACT_RETAINED',
            'supplemental_compiled_map': compiled, 'old_composed_control': 'REPLAY_CHECKED_NOT_APPROVED',
            'integration_gate': 'PENDING_EXACT_FINAL_PACKAGE', 'native': 'NOT_RUN',
            'historical_cause': 'UNKNOWN', 'proof_credit': 'NONE'}

if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
