"""Evidence integrity/collector CLI. Service-only: no subprocess/network/toolchain."""
import argparse
import hashlib
import json
from pathlib import Path
from service import check_identity, classify, negative_unknown_procedure, validate_source_metadata, negative_source_certificate, positive_unit_definition


SCHEMA = 'rr-g1-evidence-v1'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def inventory(root):
    result = {}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():
            raise ValueError('symlink forbidden in evidence: ' + str(p))
        if p.is_file() and p != root / 'evidence-manifest.json':
            result[p.relative_to(root).as_posix()] = {'sha256': digest(p), 'bytes': p.stat().st_size}
    return result


def seal(root):
    # Caller must seal after all logging/config/source/output files have closed.
    manifest = {'schema': SCHEMA, 'files': inventory(root)}
    (root / 'evidence-manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def verify_inventory(root):
    manifest = json.loads((root / 'evidence-manifest.json').read_text())
    if manifest.get('schema') != SCHEMA or manifest.get('files') != inventory(root):
        raise ValueError('evidence file inventory/bytes/hash mismatch')
    required = ('identity.json', 'execution.json', 'source-receipt.json', 'summary.json')
    if any(p not in manifest['files'] for p in required):
        raise ValueError('incomplete required evidence')
    return manifest


def collect(root, expected, reviewed_map=None):
    verify_inventory(root)
    actual = json.loads((root / 'identity.json').read_text())
    check_identity(actual, expected)
    execution = json.loads((root / 'execution.json').read_text())
    receipt = json.loads((root / 'source-receipt.json').read_text())
    if receipt.get('source_commit') != actual['source_sha']:
        raise ValueError('annotation source identity mismatch')
    if receipt.get('build_id') != actual['build_id']:
        raise ValueError('annotation Build identity mismatch')
    controls = dict(execution.get('controls', {}))
    n1 = execution.get('stages', {}).get('n1', {})
    log = root / 'n1' / 'command.log'
    controls['N1'] = log.is_file() and negative_unknown_procedure(n1.get('returncode'), log.read_text(errors='replace'))
    # P0 must contain its generated actual Program Definition and a successful stage.
    p0 = execution.get('stages', {}).get('p0', {})
    p0_files = list((root / 'p0' / 'output').rglob('*.v'))
    controls['P0'] = p0.get('returncode') == 0 and any(
        positive_unit_definition(p.read_text(errors='replace')) for p in p0_files)
    # Receipt paths must stay within this downloaded archive, not original Cloud paths.
    pins = json.loads(Path(__file__).with_name('inputs.json').read_text())
    if (root / 'inputs.json').read_bytes() != Path(__file__).with_name('inputs.json').read_bytes():
        raise ValueError('pinned input manifest differs from reviewed collector version')
    originals = {rec['path']: rec['sha256'] for rec in pins['source']['files']}
    source_names = {'smallsort': 'library/core/src/slice/sort/shared/smallsort.rs',
                    'core_lib': 'library/core/src/lib.rs',
                    'manually_drop': 'library/core/src/mem/manually_drop.rs',
                    'maybe_dangling': 'library/core/src/mem/maybe_dangling.rs'}
    source_hashes = {name: originals[path] for name, path in source_names.items()}
    validate_source_metadata(receipt, pins['source']['commit'], source_hashes)
    fixture = json.loads(Path(__file__).parent.joinpath('controls/n2-source-certificate.json').read_text())
    controls['N2'] = negative_source_certificate(fixture, pins['source']['commit'], source_hashes)
    receipt['insertions'] = {name: rec['insertions'] for name, path in source_names.items()
                             for rec in receipt.get('files', []) if rec['path'] == path}
    for name, spec in receipt.get('sources', {}).items():
        if name not in source_names or spec.get('original_sha256') != originals[source_names[name]]:
            raise ValueError('original source hash is not pinned: ' + name)
        for key in ('original_path', 'annotated_path', 'stripped_path'):
            rel = Path(spec[key])
            if rel.is_absolute() or '..' in rel.parts or not (root / rel).resolve().is_relative_to(root.resolve()):
                raise ValueError('external source evidence path')
    receipt['source_base_dir'] = str(root.resolve())
    from correspondence import inspect_outputs
    if reviewed_map is not None:
        if reviewed_map.get('schema') != 'g1-reviewed-correspondence-v1':
            raise ValueError('unsupported independently reviewed correspondence schema')
        receipt['reviewed_map_schema'] = reviewed_map['schema']
        for key in ('correspondence', 'body_map', 'locals', 'callee_inventory', 'resource_inventory'):
            receipt[key] = reviewed_map[key]
    corr = inspect_outputs(root / 'p1', receipt) if receipt.get('sources') else {
        'verdict': 'INCONCLUSIVE', 'blocker': 'annotations/correspondence NOT_RUN', 'checks': []}
    verdict = classify(execution.get('stages', {}), controls, corr)
    return dict(verdict, controls=controls, correspondence=corr, evidence_complete=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--expected-identities', type=Path, required=True,
                        help='independently verified dispatcher/config identities, never copied from archive')
    parser.add_argument('--reviewed-map', type=Path)
    parser.add_argument('--reviewed-map-sha256', help='externally reviewed mapping hash')
    args = parser.parse_args()
    mapping = None
    if args.reviewed_map:
        if digest(args.reviewed_map) != args.reviewed_map_sha256:
            raise ValueError('reviewed correspondence mapping hash mismatch')
        mapping = json.loads(args.reviewed_map.read_text())
    result = collect(args.evidence, json.loads(args.expected_identities.read_text()), mapping)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result['verdict'] == 'PASS' else 2


if __name__ == '__main__':
    raise SystemExit(main())
