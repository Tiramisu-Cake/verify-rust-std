"""Read-only scope-A identity/coordinate checks; never imports or runs project tools."""
import hashlib
import json
from pathlib import Path
import subprocess


G0 = Path('/root/verify-rust-std-kani3300-g0')
SOURCE = Path('/root/verify-rust-std-ch8-s2-cfg-r1-w13')
CONTROL = Path('/root/kani-ch8-s2-cfg-r1-w13')
AUTHOR = '7de045996987af5454052c33c448eaf31e910a32'
TASK = '90b7e5bd7f7dcecc00e7009196a466a7422f179d'
S = '9fd558c9dab5ec26abdb1226eb5f2b9cd9ffbff6'
O = '97ac4d39d7f959ea70b1f57785ffd1fd66ecd22a'
K = '0aac16ef62da9e9d5645782d458593e5d78143ba'
C = '2ecf5e839f898f6bb1cd96edd6cc6bf677acb4c8'
BASE = 'research/challenge-8/kani-k1/'
PACKET = BASE + 'kani3300/ch8-s2/r1-static-diagnostic/'
BATCH = BASE + 'kani3300/ch8-s2/batch-r1/'
BATCH_SOURCE = 'library/core/src/slice/sort/shared/smallsort/verify/sorting_s2_batch.rs'


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args])


def blob(repo, commit, path):
    return git(repo, 'show', f'{commit}:{path}')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(blob(G0, AUTHOR, path))


def repo_for(commit):
    if commit == S:
        return SOURCE
    if commit in (K, C):
        return CONTROL
    return G0


def check_identity(repo, entry):
    data = blob(repo, entry['commit'], entry['path'])
    assert sha(data) == entry['sha256'], entry['path']
    assert git(repo, 'rev-parse', f"{entry['commit']}:{entry['path']}").decode().strip() == entry['blob']
    return data


def main():
    manifest = load(PACKET + 'MANIFEST.json')
    expected = set(manifest['files']) | {'MANIFEST.json'}
    assert len(expected) == 7
    actual = set(git(G0, 'ls-tree', '-r', '--name-only', AUTHOR, '--', PACKET).decode().splitlines())
    assert actual == {PACKET + name for name in expected}
    changed = set(git(G0, 'diff-tree', '--no-commit-id', '--name-only', '-r', AUTHOR).decode().splitlines())
    assert changed == actual
    for name in sorted(expected):
        data = blob(G0, AUTHOR, PACKET + name)
        assert (G0 / PACKET / name).read_bytes() == data
        if name != 'MANIFEST.json':
            assert len(data) == manifest['files'][name]['bytes']
            assert sha(data) == manifest['files'][name]['sha256']

    provenance = load(PACKET + 'PROVENANCE.json')
    identities = []
    for repo, commit, tree, parent in [
        (SOURCE, S, '64d96010b0b4b896322e26d700c253f834ba9fd6', O),
        (CONTROL, K, '9d8bc9312bf955ef126d32b819b3cd0ed105ed2b', None),
        (CONTROL, C, 'b04ce6fd7a2c937bf72fcda7a262eef65a9f45bb',
         '9e14e033f9ee31522b571c127609dcdff76d230b'),
    ]:
        assert git(repo, 'rev-parse', commit + '^{tree}').decode().strip() == tree
        if parent:
            assert git(repo, 'rev-parse', commit + '^').decode().strip() == parent
        identities.append({'commit': commit, 'tree': tree, 'parent_checked': parent})
    for repo, commit in [(SOURCE, S), (CONTROL, C)]:
        assert git(repo, 'rev-parse', 'HEAD').decode().strip() == commit
        assert git(repo, 'status', '--porcelain=v1') == b''
    for entry in provenance['inputs']:
        assert entry['commit'] == TASK
        check_identity(G0, entry)
    for path, digest in provenance['source_files_from_prior_manifest_checked'].items():
        data = blob(SOURCE, S, path)
        assert sha(data) == digest
        assert (SOURCE / path).read_bytes() == data

    cfgmap = load(PACKET + 'SOURCE-CFG-MAP.json')
    excerpt_count = 0
    file_identities = []
    for entry in cfgmap['evidence']:
        data = check_identity(repo_for(entry['commit']), entry)
        lines = data.decode().splitlines()
        for excerpt in entry['excerpts']:
            a, z = excerpt['start_line'], excerpt['end_line']
            assert 1 <= a <= z <= len(lines)
            assert '\n'.join(lines[a - 1:z]) == excerpt['text'], (entry['path'], a, z)
            excerpt_count += 1
        file_identities.append({k: entry[k] for k in ('commit', 'path', 'blob', 'sha256')})
    assert len(file_identities) == 26

    request_bytes = blob(G0, TASK, BATCH + 'CI-REQUEST.json')
    assert request_bytes == blob(CONTROL, C, 'ch8-s1-control/CI-REQUEST.json')
    request = json.loads(request_bytes)
    bindings = json.loads(blob(G0, TASK, BATCH + 'ROOT-BINDINGS.json'))
    assert len(request['rows']) == len(bindings) == len(cfgmap['rows']) == 11
    assert {r['id'] for r in request['rows']} == {r['id'] for r in cfgmap['rows']}
    binding_by_id = {r['id']: r['binding'] for r in bindings}
    request_by_id = {r['id']: r for r in request['rows']}
    cfgs = {'kani', 'kani_smallsort_sorting', 'kani_smallsort_controls', 'kani_smallsort_s2_assumed'}
    assert set(cfgmap['common_cfg']) == cfgs
    provider_references = 0
    for row in cfgmap['rows']:
        binding = binding_by_id[row['id']]
        assert row['source_binding_reused'] == binding
        assert row['root'] == request_by_id[row['id']]['source_qualified_selector']
        assert row['root_mode'] == request_by_id[row['id']]['mode'] == binding['mode']
        assert set(row['effective_cfg']) == cfgs and row['active'] is True
        data = blob(SOURCE, S, binding['file'])
        assert sha(data) == binding['sha256']
        lines = data.decode().splitlines()
        assert lines[row['line'] - 1].strip() == f"fn {row['id']}() {{"
        for anchor in binding['locations']:
            assert lines[anchor['line'] - 1].strip() == anchor['source'].strip()
        for consumer in row['stub_verified']:
            target = consumer['target'].split('::')[-1]
            assert lines[consumer['line'] - 1].strip() == f'#[kani::stub_verified({target})]'
            for provider in consumer['matching_pfc']:
                provider_lines = blob(SOURCE, S, provider['file']).decode().splitlines()
                assert provider['target'] == consumer['target']
                assert provider_lines[provider['line'] - 1].strip() == f'#[kani::proof_for_contract({target})]'
                provider_references += 1
        for ordinary in row['ordinary_stubs']:
            target = ordinary['target'].split('::')[-1]
            replacement = ordinary['replacement'].split('::')[-1]
            assert lines[ordinary['line'] - 1].strip() == f'#[kani::stub({target},{replacement})]'
    assert cfgmap['sort8_registration_selected_for_execution'] is False
    assert 'sort8_registration_only' not in request_by_id

    old = blob(SOURCE, O, BATCH_SOURCE)
    new = blob(SOURCE, S, BATCH_SOURCE)
    assert new.startswith(old)
    assert len(new.splitlines()) - len(old.splitlines()) == 13
    assert git(SOURCE, 'diff', '--numstat', O, S).decode().strip() == f'13\t0\t{BATCH_SOURCE}'
    assert git(SOURCE, 'diff', '--name-only', O, S).decode().splitlines() == [BATCH_SOURCE]

    report = load(PACKET + 'REPORT.json')
    assert report['historical_rustc_cause'] == 'UNKNOWN'
    assert report['observed_compiler_diagnostic'] is None
    assert report['successful_r1_compilation'] == 'NOT_ESTABLISHED'
    assert report['proposed_repair']['state'] == 'NOT_APPLIED'
    assert report['established_r1_static_compile_defects'] == []
    assert report['proof_credit'] == 'NONE'
    print(json.dumps({
        'schema': 'ch8-s2-r1-static-review-validation-v1',
        'result': 'PASS', 'author_commit': AUTHOR, 'scope': 'A',
        'method': 'Read-only Git blobs, SHA256, byte/line comparisons; no compiler or project imports',
        'author_packet_files': 7, 'author_manifest_entries_verified': 6,
        'author_manifest_sha256': sha(blob(G0, AUTHOR, PACKET + 'MANIFEST.json')),
        'source_tool_control': identities,
        'source_control_worktrees_clean': True,
        'provenance_inputs_verified': len(provenance['inputs']),
        'prior_source_manifest_entries_verified': len(provenance['source_files_from_prior_manifest_checked']),
        'file_identities': file_identities, 'exact_excerpts_verified': excerpt_count,
        'roots_verified': 11, 'request_sha256': sha(request_bytes),
        'provider_references_verified': provider_references,
        'request_control_bytes_equal': True,
        'delta': {'files': 1, 'added_lines': 13, 'removed_lines': 0, 'old_prefix_identical': True},
        'limits': 'Identity/coordinate checks support the accompanying manual static review; no AST, macro expansion, Rust type/borrow check, runtime input binding, or compilation result',
    }, indent=2))


if __name__ == '__main__':
    main()
