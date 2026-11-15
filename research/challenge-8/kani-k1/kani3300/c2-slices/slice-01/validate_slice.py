#!/usr/bin/env python3
"""Static extraction and preservation checks. Does not execute Rust or tests."""
import importlib.util
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extract', HERE / 'extract_slice.py')
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)
git, digest = extract.git, extract.digest


def delimiters(data):
    """Small lexical delimiter check only; explicitly not a Rust parser/typecheck."""
    text = data.decode()
    i, stack = 0, []
    while i < len(text):
        if text.startswith('//', i):
            end = text.find('\n', i)
            i = len(text) if end < 0 else end + 1
            continue
        if text.startswith('/*', i):
            i, depth = i + 2, 1
            while depth:
                assert i < len(text), 'unclosed block comment'
                if text.startswith('/*', i):
                    depth += 1
                    i += 2
                elif text.startswith('*/', i):
                    depth -= 1
                    i += 2
                else:
                    i += 1
            continue
        raw = re.match(r'(?:br|cr|r)(#*)"', text[i:])
        if raw:
            end = text.find('"' + raw[1], i + len(raw[0]))
            assert end >= 0, 'unclosed raw string'
            i = end + 1 + len(raw[1])
            continue
        char = re.match(r"'(?:\\(?:u\{[0-9a-fA-F_]+\}|x[0-9a-fA-F]{2}|.)|[^'\\\n])'", text[i:])
        if char:
            i += len(char[0])
            continue
        if text[i] == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == '\\' else 1
            assert i < len(text), 'unclosed string'
        elif text[i] in '([{':
            stack.append(text[i])
        elif text[i] in ')]}':
            assert stack and stack.pop() == {')': '(', ']': '[', '}': '{'}[text[i]], ('delimiter mismatch', i)
        i += 1
    assert not stack, stack


def reconstruct(patch, base, target):
    """Independently reconstruct zero-context Git patches from immutable blobs."""
    chunks = re.split(rb'(?=^diff --git )', patch, flags=re.M)[1:]
    for chunk in chunks:
        path = chunk.splitlines()[0].decode().split(' b/', 1)[1]
        old = git('show', base + ':' + path).splitlines(keepends=True)
        new = git('show', target + ':' + path).splitlines(keepends=True)
        result, cursor = [], 0
        for block in re.split(rb'(?=^@@ )', chunk, flags=re.M)[1:]:
            lines = block.splitlines(keepends=True)
            m = re.match(rb'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', lines[0])
            start, count = int(m[1]), int(m[2] or b'1')
            pos = start - 1 if count else start
            result.extend(old[cursor:pos])
            deleted = [x[1:] for x in lines[1:] if x.startswith(b'-')]
            assert deleted == old[pos:pos + count], path
            result.extend(x[1:] for x in lines[1:] if x.startswith(b'+'))
            cursor = pos + count
        result.extend(old[cursor:])
        assert b''.join(result) == b''.join(new), path
    return len(chunks)


def main():
    expected = extract.extract()
    for path, data in expected.items():
        assert (extract.REPO / path).read_bytes() == data, path
        delimiters(data)
    changed = set(git('diff', '--name-only', extract.B1).decode().splitlines())
    assert changed == set(expected), (changed, set(expected))
    v = 'kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs'
    original = git('show', extract.B1 + ':' + v)
    final = git('show', extract.F + ':' + v).splitlines(keepends=True)
    independent = original.replace(b'try_resolve_instance(&self.locals, func)', b'try_resolve_instance(self.tcx, &self.locals, func)')
    independent = independent.replace(
        b'fn try_resolve_instance(locals: &[LocalDecl], func: &Operand) -> Result<Instance, String> {\n    resolve_call(func.ty(locals).unwrap())\n}',
        b''.join(final[1178:1185]).rstrip(b'\n'),
    )
    assert independent == expected[v], 'baseline visitor changes exceed exact resolver plumbing'
    t = 'kani-compiler/src/kani_middle/transform/check_uninit/'
    assert expected[t + 'delayed_ub/instrumentation_visitor.rs'] == git('show', extract.F + ':' + t + 'delayed_ub/instrumentation_visitor.rs')
    delayed = expected[t + 'delayed_ub/mod.rs']
    pre = json.loads((extract.MAP / 'PRE-F7.json').read_text())
    for item in pre['snippets']:
        assert delayed.count(item['text'].encode()) == 1
    assert b'replace_delayed_body' not in delayed
    assert b'Anonymous' not in delayed and b'UninitInstrumenter::run(\n                    tcx,' not in delayed
    a = 'kani-compiler/src/kani_middle/points_to/points_to_analysis.rs'
    module = b'#[cfg(test)]\nmod active_call_tests {'
    assert expected[a].split(module)[1] == git('show', extract.F + ':' + a).split(module)[1]
    unit_names = re.findall(rb'#\[test\]\s+fn (\w+)', expected[a].split(module)[1])
    assert len(unit_names) == 9
    controls = git('ls-tree', '-r', '--name-only', extract.B1, '--', 'tests/expected/uninit/unresolved-calls').decode().splitlines()
    comment_changes = set(p for p in expected if p.startswith('tests/'))
    for path in controls:
        before = git('show', extract.B1 + ':' + path)
        now = (extract.REPO / path).read_bytes()
        if path in comment_changes:
            code = lambda b: b'\n'.join(x for x in b.splitlines() if not x.lstrip().startswith(b'//'))
            assert code(before) == code(now)
        else:
            assert before == now, path
    assert len([p for p in controls if p.endswith('.expected')]) == 22
    protected = ['library', 'docs', '.github', 'kani-compiler/src/kani_middle/points_to/points_to_graph.rs', t + 'ty_layout.rs']
    assert not git('diff', '--name-only', extract.B1, '--', *protected)
    subprocess.run(['git', '-C', str(extract.REPO), 'diff', '--check', extract.B1], check=True)
    report = {
        'status': 'PASS_STATIC_ONLY', 'files': len(expected),
        'active_call_unit_names': [n.decode() for n in unit_names],
        'active_call_unit_count': 9, 'unit_execution': 'NOT_RUN',
        'checks': ['deterministic owner1 extraction including explicit syntax seams', 'lexical balanced delimiters (not Rust parsing)',
                   'independent exact resolver-only change over baseline visitor', 'entire instrumentation visitor and nine unit bodies exact F',
                   'both real pre-F7 cache writers; no future API', 'all 22 B1 fixture code/golden pairs retained',
                   'no runtime/layout/graph/docs/workflow/pin changes', 'git diff --check'],
        'compilation_fmt_clippy_CI_push': 'NOT_RUN', 'integration_status': 'PENDING',
        'integration_heads': [4, 5], 'independent_review': 'PENDING_WORKER15',
    }
    head = git('rev-parse', 'HEAD').decode().strip()
    if head != extract.B1:
        assert git('show', '-s', '--format=%P', head).decode().strip() == extract.B1
        assert not git('status', '--porcelain')
        report['source_sha'] = head
        report['source_tree'] = git('rev-parse', 'HEAD^{tree}').decode().strip()
        for name, base, target in [('source.patch', extract.B1, head), ('residual-to-F.patch', head, extract.F)]:
            patch = git('diff', '--no-ext-diff', '--no-renames', '--full-index', '--binary', '--unified=0', base, target)
            (HERE / name).write_bytes(patch)
            if name == 'source.patch':
                report['patch_reconstruction_files'] = reconstruct(patch, base, target)
            report[name + '_sha256'] = digest(patch)
            # Alternate temporary indexes do not change any worktree or ref.
            # This checks patch endpoints, not the future logical slice stack.
            with tempfile.TemporaryDirectory(prefix='c2-slice01-index-') as tmp:
                env = dict(os.environ, GIT_INDEX_FILE=str(Path(tmp) / 'index'))
                def index_git(*args):
                    return subprocess.check_output(['git', '-C', str(extract.REPO), *args], env=env)
                index_git('read-tree', base)
                index_git('apply', '--cached', '--unidiff-zero', '--whitespace=nowarn', str(HERE / name))
                tree = index_git('write-tree').decode().strip()
                assert tree == git('rev-parse', target + '^{tree}').decode().strip()
                report[name + '_alternate_index_target_tree'] = tree
    (HERE / 'STATIC-VALIDATION.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
