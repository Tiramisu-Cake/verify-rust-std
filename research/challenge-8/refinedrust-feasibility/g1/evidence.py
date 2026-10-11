"""Evidence integrity/collector CLI. Service-only: no subprocess/network/toolchain."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from service import check_identity, classify, normal_completion, negative_unknown_procedure, validate_source_metadata, negative_source_certificate, positive_unit_definition


SCHEMA = 'rr-g1-evidence-v1'
COMMAND_STAGES = ('versions', 'p0', 'n1', 'native', 'p1')
RR_STAGES = ('p0', 'n1', 'p1')
RR_PROFILE = {'skip_unsupported_features': False, 'register_all_adts': False,
              'dump_debug_info': True, 'dump_borrowck_info': True,
              'generate_linking_requirements': True, 'run_check': False,
              'no_verify': False, 'admit_proofs': False, 'trust_debug': False,
              'find_stdlib': False, 'panic_abort_mode': 'conservative',
              'check_overflows': True, 'lib_load_paths': []}


def parse_generated_rr_config(text):
    """Parse only the simple `key = JSON-literal` lines emitted by rr_env."""
    settings = {}
    for line in text.splitlines():
        match = re.fullmatch(r'([a-z_]+) = (.+)', line)
        if not match or match[1] in settings:
            raise ValueError('unexpected/duplicate generated RR config line')
        settings[match[1]] = json.loads(match[2])
    return settings


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
    files = manifest['files']
    required = {'identity.json', 'execution.json', 'source-receipt.json',
                'summary.json', 'inputs.json', 'image-receipt.json', 'cargo-config.toml'}
    if not required.issubset(files):
        raise ValueError('incomplete required evidence: ' + ', '.join(sorted(required - files.keys())))
    execution = json.loads((root / 'execution.json').read_text())
    stages = execution.get('stages', {})
    if not isinstance(stages, dict) or set(stages) - set(COMMAND_STAGES) - {'inputs', 'compiler'}:
        raise ValueError('unknown execution stage')
    for name in COMMAND_STAGES:
        stage_dir = name + '/'
        present = {p for p in files if p.startswith(stage_dir)}
        if name not in stages and present:
            raise ValueError('unrecorded attempted stage: ' + name)
        if name in stages:
            needed = {stage_dir + 'command.json', stage_dir + 'command.log',
                      stage_dir + 'environment.json'}
            if name in RR_STAGES:
                needed.add(stage_dir + 'RefinedRust.toml')
            if not needed.issubset(files):
                raise ValueError('incomplete ' + name + ' evidence: ' + ', '.join(sorted(needed - files.keys())))
    if ('N2' in execution.get('controls', {}) or
            any(name in stages for name in ('native', 'p1'))):
        if 'n2-source-certificate.json' not in files:
            raise ValueError('missing archived N2 certificate')
    return manifest


def verify_commands(root, stages):
    original_root = None
    for name in COMMAND_STAGES:
        if name not in stages:
            continue
        directory = root / name
        record = json.loads((directory / 'command.json').read_text())
        stage = dict(stages[name])
        if name == 'native':
            stage.pop('compiler_rejection', None)
        if record != stage:
            raise ValueError('execution/command record mismatch: ' + name)
        original_dir = Path(record.get('evidence_dir', ''))
        if (not original_dir.is_absolute() or original_dir.name != name or
                not original_dir.parent.is_relative_to('/workspace') or
                (original_root is not None and original_dir.parent != original_root)):
            raise ValueError('invalid original evidence directory: ' + name)
        original_root = original_dir.parent
        code = record.get('returncode')
        if (type(record.get('timed_out')) is not bool or
                type(record.get('signaled')) is not bool or
                record['signaled'] != (type(code) is int and code < 0)):
            raise ValueError('invalid termination record: ' + name)
        if (record.get('log_sha256') != digest(directory / 'command.log') or
                record.get('log_bytes') != (directory / 'command.log').stat().st_size or
                record.get('environment_sha256') != digest(directory / 'environment.json')):
            raise ValueError('command log/environment mismatch: ' + name)
        environment = json.loads((directory / 'environment.json').read_text())
        if name in RR_STAGES:
            config = directory / 'RefinedRust.toml'
            if (record.get('rr_config_sha256') != digest(config) or
                    environment.get('RR_CONFIG') != str(original_dir / 'RefinedRust.toml') or
                    environment.get('CARGO_TARGET_DIR') != str(original_dir / 'target')):
                raise ValueError('effective RR config/environment mismatch: ' + name)
            settings = parse_generated_rr_config(config.read_text())
            if (set(settings) != set(RR_PROFILE) | {'log_dir', 'output_dir'} or
                    any(type(settings.get(key)) is not type(value) or settings[key] != value
                        for key, value in RR_PROFILE.items()) or
                    settings.get('log_dir') != str(original_dir / 'log') or
                    settings.get('output_dir') != str(original_dir / 'output')):
                raise ValueError('effective RR profile mismatch: ' + name)
        elif 'rr_config_sha256' in record or 'RR_CONFIG' in environment:
            raise ValueError('unexpected RR config: ' + name)


def verify_effective_environment(root, stages, actual, pins, image):
    binaries = image.get('binaries', {})
    required = {'rustc', 'cargo', 'cargo_refinedrust'}
    if not required.issubset(binaries):
        raise ValueError('image receipt omits command binaries')
    cargo_home = str(Path(image.get('cargo_config', {}).get('path', '')).parent)
    for name in COMMAND_STAGES:
        if name not in stages:
            continue
        environment = json.loads((root / name / 'environment.json').read_text())
        expected = {'BUILD_ID': actual['build_id'],
                    'CARGO_HOME': cargo_home,
                    'RUSTUP_TOOLCHAIN': pins['compiler']['channel'],
                    'RUSTC_BOOTSTRAP': '1',
                    'RUSTFLAGS': '-Cpanic=unwind -Coverflow-checks=on',
                    'CARGO_NET_OFFLINE': 'true', 'CARGO_BUILD_JOBS': '2',
                    'LD_LIBRARY_PATH': image.get('ld_library_path')}
        expected['PATH'] = ':'.join((
            str(Path(binaries['cargo_refinedrust']['path']).parent),
            str(Path(binaries['cargo']['path']).parent), '/usr/bin', '/bin'))
        if any(environment.get(key) != value for key, value in expected.items()):
            raise ValueError('effective command environment mismatch: ' + name)
        binary = {'versions': 'rustc', 'p0': 'cargo_refinedrust',
                  'n1': 'cargo_refinedrust', 'native': 'cargo',
                  'p1': 'cargo_refinedrust'}[name]
        if stages[name].get('argv', [None])[0] != binaries[binary].get('path'):
            raise ValueError('command binary/image receipt mismatch: ' + name)
        original_dir = Path(stages[name]['evidence_dir'])
        cwd = Path(stages[name].get('cwd', ''))
        if name == 'versions':
            argv = [binaries[binary]['path'], '-Vv']
        elif name in ('p0', 'n1'):
            if cwd != original_dir / 'fixture':
                raise ValueError('fixture command cwd mismatch: ' + name)
            argv = [binaries[binary]['path'], '--', '--manifest-path',
                    str(cwd / 'Cargo.toml'), '--locked', '--offline', '--target',
                    pins['compiler']['host']]
        elif name == 'native':
            argv = [binaries[binary]['path'], 'check', '--manifest-path',
                    str(cwd / 'library/Cargo.toml'), '-p', 'core', '--locked',
                    '--offline', '--target', pins['compiler']['host']]
        else:
            argv = [binaries[binary]['path'], '--', '--manifest-path',
                    str(cwd / 'library/Cargo.toml'), '-p', 'core', '--locked',
                    '--offline', '--target', pins['compiler']['host']]
        if stages[name]['argv'] != argv:
            raise ValueError('command arguments mismatch: ' + name)
        if environment.get('HOME') != str(original_dir.parent / 'home'):
            raise ValueError('command HOME mismatch: ' + name)
        if name == 'native' and environment.get('CARGO_TARGET_DIR') != str(original_dir.parent / 'native-target'):
            raise ValueError('native target directory mismatch')


def verify_source_archives(root, receipt, source_names, originals):
    sources = receipt.get('sources')
    if not isinstance(sources, dict) or set(sources) != set(source_names):
        raise ValueError('P1 requires all four annotated source archives')
    file_records = receipt.get('files')
    if not isinstance(file_records, list) or {rec.get('path') for rec in file_records} != set(source_names.values()):
        raise ValueError('P1 source certificate file set mismatch')
    for name, source_path in source_names.items():
        spec = sources[name]
        expected_paths = {'original_path': f'sources/{name}.original.rs',
                          'annotated_path': f'sources/{name}.annotated.rs',
                          'stripped_path': f'sources/{name}.stripped.rs'}
        if any(spec.get(key) != value for key, value in expected_paths.items()):
            raise ValueError('P1 source archive path mismatch: ' + name)
        payloads = {key: (root / rel).read_bytes() for key, rel in expected_paths.items()}
        hashes = {key: hashlib.sha256(data).hexdigest() for key, data in payloads.items()}
        if (hashes['original_path'] != originals[source_path] or
                hashes['original_path'] != spec.get('original_sha256') or
                hashes['annotated_path'] != spec.get('annotated_sha256') or
                hashes['stripped_path'] != spec.get('stripped_sha256') or
                payloads['original_path'] != payloads['stripped_path'] or
                spec.get('strip_equals_original') is not True):
            raise ValueError('P1 source archive bytes/hash mismatch: ' + name)
        record = next(rec for rec in file_records if rec['path'] == source_path)
        if (record.get('original_sha256') != hashes['original_path'] or
                record.get('annotated_sha256') != hashes['annotated_path'] or
                record.get('strip_equals_original') is not True):
            raise ValueError('P1 source certificate record mismatch: ' + name)


def stage_status(stages, controls, n2_attempted):
    result = {}
    for name in ('inputs', 'compiler', 'p0', 'n1', 'n2', 'native', 'p1'):
        if name == 'n2':
            status = 'COMPLETE' if controls['N2'] else 'FAILED' if n2_attempted else 'NOT_RUN'
            result[name] = {'status': status,
                            'reason': 'archived metadata negative' if controls['N2'] else
                                      'archived N2 failed' if n2_attempted else 'N2 not reached'}
        elif name in ('inputs', 'compiler'):
            ok = stages.get(name, {}).get('ok') is True
            attempted = name in stages or (name == 'compiler' and 'versions' in stages)
            result[name] = {'status': 'COMPLETE' if ok else 'FAILED' if attempted else 'NOT_RUN',
                            'reason': '' if ok else name + ' not established'}
        elif name not in stages:
            cause = {'p0': 'compiler preflight did not reach P0',
                     'n1': 'P0/control sequence stopped before N1',
                     'native': 'admission controls did not reach native core',
                     'p1': 'native core/annotation did not reach P1'}[name]
            result[name] = {'status': 'NOT_RUN', 'reason': cause}
        else:
            normal = normal_completion(stages[name])
            result[name] = {'status': 'COMPLETE' if normal else 'INTERRUPTED',
                            'reason': '' if normal else 'timeout/signal/incomplete command'}
    return result


def collect(root, expected, reviewed_map=None):
    verify_inventory(root)
    actual = json.loads((root / 'identity.json').read_text())
    check_identity(actual, expected)
    execution = json.loads((root / 'execution.json').read_text())
    stages = execution.get('stages', {})
    verify_commands(root, stages)
    pins_path = Path(__file__).with_name('inputs.json')
    if (root / 'inputs.json').read_bytes() != pins_path.read_bytes():
        raise ValueError('pinned input manifest differs from reviewed collector version')
    pins = json.loads(pins_path.read_text())
    pinned_ids = {'source_sha': pins['source']['commit'], 'tool_sha': pins['rr']['commit'],
                  'compiler_sha': pins['compiler']['commit'], 'profile': pins['profile']}
    if any(actual.get(key) != value for key, value in pinned_ids.items()):
        raise ValueError('archive identity/pinned input mismatch')
    image = json.loads((root / 'image-receipt.json').read_text())
    expected_image = {'schema': 'refinedrust-g1-image-receipt-v1',
                      'rr_commit': pins['rr']['commit'],
                      'rr_checkout_clean': True,
                      'compiler_source_commit': pins['compiler']['commit'],
                      'rr_frontend_lock_sha256': next(r['sha256'] for r in pins['rr']['files']
                                                     if r['path'] == 'rr_frontend/Cargo.lock')}
    if any(image.get(key) != value for key, value in expected_image.items()):
        raise ValueError('image receipt/pins mismatch')
    image_pins = json.loads((Path(__file__).parent / 'cloud/IMAGE-INPUTS.json').read_text())
    if image.get('rust_distribution_archives_sha256') != image_pins['archive_sha256_x86_64_unknown_linux_gnu']:
        raise ValueError('image receipt distribution closure mismatch')
    if (not Path(image.get('cargo_config', {}).get('path', '')).is_absolute() or
            set(image.get('binaries', {})) != {'rustc', 'cargo', 'cargo_refinedrust', 'refinedrust_rustc'} or
            any(not Path(spec.get('path', '')).is_absolute() or
                    not re.fullmatch(r'[0-9a-f]{64}', str(spec.get('sha256', '')))
                    for spec in image['binaries'].values())):
        raise ValueError('incomplete image receipt binary/Cargo provenance')
    if image.get('cargo_config', {}).get('sha256') != digest(root / 'cargo-config.toml'):
        raise ValueError('image receipt/Cargo config mismatch')
    verify_effective_environment(root, stages, actual, pins, image)
    version = stages.get('versions', {})
    version_log = (root / 'versions' / 'command.log')
    version_text = version_log.read_text(errors='replace') if version_log.is_file() else ''
    compiler_ok = (normal_completion(version) and version.get('returncode') == 0 and
                   ('commit-hash: ' + pins['compiler']['commit']) in version_text and
                   ('host: ' + pins['compiler']['host']) in version_text)
    if 'compiler' in stages and 'versions' not in stages:
        raise ValueError('compiler status without versions command')
    if stages.get('compiler', {}).get('ok') is True and not compiler_ok:
        raise ValueError('compiler status contradicts rustc version evidence')
    stages = dict(stages)
    if 'versions' in stages:
        stages['compiler'] = {'ok': compiler_ok, 'interrupted': not normal_completion(version)}
    if 'native' in stages and 'compiler_rejection' in stages['native']:
        native_log = (root / 'native' / 'command.log').read_text(errors='replace')
        native = dict(stages['native'])
        rejection = bool(re.search(r'error\[E\d+\]', native_log))
        if native['compiler_rejection'] != rejection:
            raise ValueError('native rejection flag contradicts raw log')
        native['compiler_rejection'] = rejection
        stages['native'] = native
    receipt = json.loads((root / 'source-receipt.json').read_text())
    if receipt.get('source_commit') != actual['source_sha']:
        raise ValueError('annotation source identity mismatch')
    if receipt.get('build_id') != actual['build_id']:
        raise ValueError('annotation Build identity mismatch')
    controls = {}
    n1 = stages.get('n1', {})
    log = root / 'n1' / 'command.log'
    controls['N1'] = log.is_file() and negative_unknown_procedure(
        n1.get('returncode'), log.read_text(errors='replace'),
        timed_out=n1.get('timed_out', True), signaled=n1.get('signaled', True))
    # P0 must contain its generated actual Program Definition and a successful stage.
    p0 = stages.get('p0', {})
    p0_files = list((root / 'p0' / 'output').rglob('*.v'))
    controls['P0'] = normal_completion(p0) and p0.get('returncode') == 0 and any(
        positive_unit_definition(p.read_text(errors='replace')) for p in p0_files)
    # Receipt paths must stay within this downloaded archive, not original Cloud paths.
    originals = {rec['path']: rec['sha256'] for rec in pins['source']['files']}
    source_names = {'smallsort': 'library/core/src/slice/sort/shared/smallsort.rs',
                    'core_lib': 'library/core/src/lib.rs',
                    'manually_drop': 'library/core/src/mem/manually_drop.rs',
                    'maybe_dangling': 'library/core/src/mem/maybe_dangling.rs'}
    source_hashes = {name: originals[path] for name, path in source_names.items()}
    validate_source_metadata(receipt, pins['source']['commit'], source_hashes)
    if 'p1' in stages:
        if receipt.get('manifest_sha256') != digest(Path(__file__).parent / 'annotations.json'):
            raise ValueError('P1 annotation manifest mismatch')
        verify_source_archives(root, receipt, source_names, originals)
    reviewed_n2 = Path(__file__).parent / 'controls/n2-source-certificate.json'
    archived_n2 = root / 'n2-source-certificate.json'
    if archived_n2.is_file() and archived_n2.read_bytes() != reviewed_n2.read_bytes():
        raise ValueError('archived N2 differs from reviewed bytes')
    controls['N2'] = (archived_n2.is_file() and negative_source_certificate(
        json.loads(archived_n2.read_text()), pins['source']['commit'], source_hashes))
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
    verdict = classify(stages, controls, corr)
    statuses = stage_status(stages, controls, archived_n2.is_file())
    diagnostic_complete = bool(all(controls.values()) and receipt.get('sources') and
                           corr.get('verdict') in ('PASS', 'STOP') and
                           all(statuses[name]['status'] == 'COMPLETE' for name in statuses))
    return dict(verdict, controls=controls, correspondence=corr, stage_status=statuses,
                local_inventory_valid=True, diagnostic_complete=diagnostic_complete,
                evidence_complete=False)


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
