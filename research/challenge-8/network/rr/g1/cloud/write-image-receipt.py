#!/usr/bin/env python3
"""Write the N7 cold-image receipt inside the authorized Cloud image build."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


BINARIES = {
    'rustc': Path('/opt/rust/bin/rustc'),
    'cargo': Path('/opt/rust/bin/cargo'),
    'cargo-refinedrust': Path('/opt/rr-bin/cargo-refinedrust'),
    'refinedrust-rustc': Path('/opt/rr-bin/refinedrust-rustc'),
}
ARCHIVES = {
    'rustc': 'rustc-nightly-x86_64-unknown-linux-gnu.tar.xz',
    'cargo': 'cargo-nightly-x86_64-unknown-linux-gnu.tar.xz',
    'rustc-dev': 'rustc-dev-nightly-x86_64-unknown-linux-gnu.tar.xz',
    'llvm-tools-preview': 'llvm-tools-nightly-x86_64-unknown-linux-gnu.tar.xz',
    'rust-src': 'rust-src-nightly.tar.xz',
    'rust-std': 'rust-std-nightly-x86_64-unknown-linux-gnu.tar.xz',
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def output(*argv):
    return subprocess.check_output(argv, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--dist', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    pins = json.loads(args.inputs.read_text())
    if pins.get('schema') != 'refinedrust-g1-cold-image-inputs-v1':
        raise ValueError('unexpected image-input schema')
    rr = Path('/opt/refinedrust')
    commit = output('git', '-C', str(rr), 'rev-parse', 'HEAD')
    tree = output('git', '-C', str(rr), 'rev-parse', 'HEAD^{tree}')
    dirty = output('git', '-C', str(rr), 'status', '--porcelain')
    if commit != pins['rr_commit'] or tree != pins['rr_tree'] or dirty:
        raise ValueError('RR checkout commit/tree mismatch or dirty tree')
    rustc_vv = output(str(BINARIES['rustc']), '-Vv') + '\n'
    if not rustc_vv.startswith(pins['rustc_expected'] + '\n'):
        raise ValueError('compiler version mismatch')
    if 'commit-hash: ' + pins['rustc_source_commit'] not in rustc_vv:
        raise ValueError('compiler source commit mismatch')
    lock_hash = sha256(rr / 'rr_frontend/Cargo.lock')
    if lock_hash != pins['rr_frontend_lock_sha256']:
        raise ValueError('RR Cargo.lock mismatch')
    for name, path in BINARIES.items():
        if not path.is_file() or not os.access(path, os.X_OK):
            raise ValueError('missing/non-executable binary: ' + name)
    archive_hashes = {name: sha256(args.dist / filename) for name, filename in ARCHIVES.items()}
    if archive_hashes != pins['archive_sha256_x86_64_unknown_linux_gnu']:
        raise ValueError('Rust distribution archive mismatch')
    packages = output('dpkg-query', '-W', '-f=${binary:Package}\t${Version}\n').splitlines()
    cargo_config = Path('/opt/g1-cargo/config.toml')
    receipt = {
        'schema': 'refinedrust-g1-image-receipt-v1',
        'image_digest': None,
        'image_digest_binding': 'cold Build registry receipt',
        'base_image_digest': pins['base_os_digest'],
        'rr_commit': commit,
        'rr_tree': tree,
        'rr_checkout_clean': True,
        'rr_frontend_lock_sha256': lock_hash,
        'compiler_source_commit': pins['rustc_source_commit'],
        'rustc_version_verbose': rustc_vv,
        'rust_distribution_archives_sha256': archive_hashes,
        'os_package_inventory': packages,
        'cargo_home': str(Path('/opt/g1-cargo')),
        'cargo_home_config': {
            'path': str(cargo_config),
            'present': cargo_config.is_file(),
            'sha256': sha256(cargo_config) if cargo_config.is_file() else None,
        },
        'cargo_dependency_mode': 'registry-online-locked',
        'binaries': {name: {'path': str(path), 'sha256': sha256(path)}
                     for name, path in BINARIES.items()},
        'ld_library_path': os.environ.get('LD_LIBRARY_PATH', ''),
        'receipt_generator_sha256': sha256(Path(__file__)),
    }
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
