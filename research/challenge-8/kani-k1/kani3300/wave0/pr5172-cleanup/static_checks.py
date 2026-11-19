"""Read-only source/byte checks; never invokes a Rust toolchain or verifier."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path('/root/kani-pr5172-cleanup-w11')
OUT = Path(__file__).resolve().parent
PARENT = '80e5d6fabc0103b0b3117440007ad2d9475f9a9c'
PREFIX = 'tests/expected/uninit/unresolved-calls/'
LICENSE = '// Copyright Kani Contributors\n// SPDX-License-Identifier: Apache-2.0 OR MIT\n'
MODULE = '#[path = "auxiliary/analysis_target.rs"]\nmod analysis_target;\n\n'


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def old(path):
    return git('show', PARENT + ':' + path)


def digest(data):
    return hashlib.sha256(data).hexdigest()


step = json.loads((OUT / 'STEP1.json').read_text())
roots = sorted(p for p in git('ls-tree', '-r', '--name-only', PARENT, PREFIX).decode().splitlines()
               if p.endswith('.rs'))
assert len(roots) == 22
helper_pattern = r'// The copy intrinsic[^\n]*\n#\[inline\(never\)\]\nfn seed\(\) \{.*?\n\}\n\n'
helper = re.search(helper_pattern, old(PREFIX + 'direct-seeded.rs').decode(), re.S).group()
assert digest(helper.encode()) == step['helper_sha256']
aux_path = PREFIX + 'auxiliary/analysis_target.rs'
aux = (ROOT / aux_path).read_text()
assert aux == LICENSE + '\n' + helper.replace('fn seed()', 'pub fn check_byte_copy()').rstrip() + '\n'
assert '#[kani::proof]' not in aux
matrix = []
for path in roots:
    before = old(path).decode()
    after = (ROOT / path).read_text()
    if path.endswith('-seeded.rs'):
        assert before.count(helper) == 1
        restored = after.replace(MODULE, helper).replace('analysis_target::check_byte_copy();', 'seed();')
        assert restored == before, path
    else:
        assert after == before and 'analysis_target' not in after, path
    named = (ROOT / path).with_suffix('.expected')
    oracle = named if named.exists() else named.parent / 'expected'
    oracle_bytes = oracle.read_bytes()
    assert oracle_bytes == old(path[:-3] + '.expected'), path
    assert 'VERIFICATION:- ' in oracle_bytes.decode() and 'Complete - ' in oracle_bytes.decode()
    assert after.startswith(LICENSE)
    matrix.append({'source': path, 'harnesses': re.findall(r'#\[kani::proof\]\s*fn (\w+)\(', after),
                   'flags': re.findall(r'^// (?:kani|compile)-flags: (.+)$', after, re.M),
                   'oracle': str(oracle.relative_to(ROOT)), 'oracle_sha256': digest(oracle_bytes),
                   'copy_calls': after.count('analysis_target::check_byte_copy();')})
assert sum(len(row['harnesses']) for row in matrix) == 24
assert sum(row['copy_calls'] for row in matrix) == 12
assert len(list((ROOT / PREFIX).glob('*.expected'))) == 14
assert all(not (ROOT / PREFIX / name).exists() for name in step['shared_expected_names'])
assert digest((ROOT / PREFIX / 'expected').read_bytes()) == step['shared_expected_sha256']

# Mirror the inspected collector's .rs/prefix filter and auxiliary exclusion.
def discovered(directory):
    result = []
    for path in sorted(directory.iterdir()):
        if path.name.endswith('.rs') and not path.name.startswith(('.', '#', '~')):
            result.append(str(path.relative_to(ROOT)))
        elif path.is_dir() and path.name != 'auxiliary':
            result.extend(discovered(path))
    return result


assert sorted(discovered(ROOT / PREFIX)) == roots
main = (ROOT / 'tools/compiletest/src/main.rs').read_text()
runner = (ROOT / 'tools/compiletest/src/runtest.rs').read_text()
assert 'if &file_name != "auxiliary"' in main
assert 'let expected_path = if dot_expected_path.exists()' in runner
assert 'self.testpaths.file.parent().unwrap().join("expected")' in runner
assert git('diff', '--name-only', PARENT, '--', 'tools', 'kani-driver', 'library') == b''
compiler_changes = git('diff', '--name-only', PARENT, '--', 'kani-compiler').decode().splitlines()
comment_path = 'kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs'
old_comment = (b'                        // The resolver accepts MIR bodies and foreign items. Foreign items use\n'
               b'                        // the models below; other calls transfer union argument and return state.\n')
new_comment = (b'                        // Foreign allocation calls use the models below; other calls store\n'
               b'                        // initialization state for union arguments.\n')
assert compiler_changes == [comment_path], compiler_changes
current_compiler = (ROOT / comment_path).read_bytes()
assert current_compiler.count(new_comment) == old(comment_path).count(old_comment) == 1
assert current_compiler.replace(new_comment, old_comment) == old(comment_path)
compiler = {path: {'parent_git_blob': git('rev-parse', PARENT + ':' + path).decode().strip(),
                   'parent_sha256': digest(old(path)),
                   'candidate_git_blob': git('hash-object', '--no-filters', path).decode().strip(),
                   'candidate_sha256': digest((ROOT / path).read_bytes()),
                   'disposition': 'EXACT_COMMENT_ONLY_CHANGE' if path == comment_path else 'BYTE_IDENTICAL'}
            for path in step['compiler_paths']}
assert all((ROOT / path).read_bytes() == old(path) for path in compiler if path != comment_path)
allowed = {p for p in roots if p.endswith('-seeded.rs')}
allowed.update(PREFIX + name for name in step['shared_expected_names'])
allowed.update((aux_path, PREFIX + 'expected'))
allowed.add(comment_path)
changed = set(git('diff', '--no-renames', '--name-only', PARENT).decode().splitlines())
untracked = set(git('ls-files', '--others', '--exclude-standard').decode().splitlines())
assert changed | untracked == allowed, (changed | untracked) ^ allowed
snapshot = OUT.parent / 'open-pr-slop-inputs-20261119/pr-5172/PR-BODY.snapshot.md'
body = snapshot.read_text()
draft = (OUT / 'PROPOSED-PR.md').read_text()
for line in body.splitlines():
    if line.startswith(('By submitting this pull request,', '*Disclosure:')):
        assert line in draft.splitlines()
assert digest(snapshot.read_bytes()) == '09eb0ccd45ce870ea58eccb5c2038e353e5d680bf77722267795eded30531c56'
git('diff', '--check', PARENT)
head = git('rev-parse', 'HEAD').decode().strip()
commit_identity = None
if head != PARENT:
    assert git('show', '-s', '--format=%P', head).decode().strip() == PARENT
    assert git('rev-list', '--count', PARENT + '..' + head).decode().strip() == '1'
    assert git('status', '--porcelain=v1') == b''
    author = git('show', '-s', '--format=%an <%ae>', head).decode().strip()
    committer = git('show', '-s', '--format=%cn <%ce>', head).decode().strip()
    message = git('show', '-s', '--format=%B', head).decode().strip()
    assert author == committer == 'Tiramisu-Cake <igkharin@gmail.com>'
    assert not any(tag in message.lower() for tag in ('[skip ci]', '[ci skip]', 'skip-ci', 'co-authored-by:'))
    for path in allowed:
        if (ROOT / path).exists():
            assert git('show', head + ':' + path) == (ROOT / path).read_bytes()
    commit_identity = {'author': author, 'committer': committer, 'message': message,
                       'exactly_one_commit': True, 'worktree_clean': True,
                       'committed_bytes_checked': True}
receipt = {'status': 'STATIC_CHECKS_PASS', 'parent': PARENT,
           'candidate_head': head, 'commit_identity': commit_identity,
           'candidate_tree': git('rev-parse', 'HEAD^{tree}').decode().strip(),
           'discovered_roots': 22, 'retained_harnesses': 24, 'copy_calls': 12,
           'shared_helper_sources': 11, 'named_oracles': 14, 'fallback_oracles': 8,
           'compiler_paths': compiler, 'compiler_code_bytes_identical_except_exact_comment': True,
           'adapter': {'disposition': 'DEFERRED', 'reason': 'avoid code churn in a PR under review'},
           'matrix': matrix,
           'validation': 'Source reversal, exact effective oracle bytes, discovery port, flags and scope checks; git diff --check',
           'native_compiler_Kani_CBMC_CI': 'NOT_RUN', 'independent_review': 'NOT_RUN', 'proof_credit': 'NONE'}
(OUT / 'STATIC-CHECKS.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k: receipt[k] for k in ('status', 'candidate_head', 'retained_harnesses', 'discovered_roots', 'native_compiler_Kani_CBMC_CI')}))
