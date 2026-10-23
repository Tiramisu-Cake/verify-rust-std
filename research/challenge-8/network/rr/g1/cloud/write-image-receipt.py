#!/usr/bin/env python3
"""Cold-image receipt generator. Run only inside an authorized Cloud image build."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


BINARIES = {
    'rustc': Path('/opt/rust/bin/rustc'),
    'cargo': Path('/opt/rust/bin/cargo'),
    'cargo_refinedrust': Path('/opt/rr-bin/cargo-refinedrust'),
    'refinedrust_rustc': Path('/opt/rr-bin/refinedrust-rustc'),
}


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def output(*argv):
    return subprocess.check_output(argv, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True)
    parser.add_argument('--context', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    pins = json.loads(args.inputs.read_text())
    if pins['schema'] != 'refinedrust-g1-cold-image-inputs-v1':
        raise ValueError('unexpected image-input schema')
    rr = Path('/opt/refinedrust')
    commit = output('git', '-C', str(rr), 'rev-parse', 'HEAD')
    if commit != pins['rr_commit'] or output('git', '-C', str(rr), 'status', '--porcelain'):
        raise ValueError('RR checkout mismatch or dirty tree')
    rustc_vv = output(str(BINARIES['rustc']), '-Vv') + '\n'
    if rustc_vv != (args.context / 'rustc-vv-expected.txt').read_text():
        raise ValueError('compiler verbose version mismatch')
    cargo_config = Path('/opt/g1-cargo/config.toml')
    if sha256(cargo_config) != sha256(args.context / 'cargo-config.toml'):
        raise ValueError('installed Cargo config differs')
    archives = {
        'rustc': 'rustc-nightly-x86_64-unknown-linux-gnu.tar.xz',
        'cargo': 'cargo-nightly-x86_64-unknown-linux-gnu.tar.xz',
        'rustc-dev': 'rustc-dev-nightly-x86_64-unknown-linux-gnu.tar.xz',
        'llvm-tools-preview': 'llvm-tools-nightly-x86_64-unknown-linux-gnu.tar.xz',
        'rust-src': 'rust-src-nightly.tar.xz',
        'rust-std': 'rust-std-nightly-x86_64-unknown-linux-gnu.tar.xz',
    }
    for component, filename in archives.items():
        if sha256(args.context / filename) != pins['archive_sha256_x86_64_unknown_linux_gnu'][component]:
            raise ValueError('Rust distribution archive mismatch: ' + component)
    packages = output('dpkg-query', '-W', '-f=${binary:Package}\t${Version}\n').splitlines()
    receipt = {
        'schema': 'refinedrust-g1-image-receipt-v1',
        'image_digest': None,  # Registry digest is bound externally after push; no circular image hash.
        'image_digest_binding': 'cold Build registry receipt',
        'base_image_digest': pins['base_os_digest'],
        'rr_commit': commit,
        'rr_checkout_clean': True,
        'compiler_source_commit': pins['rustc_source_commit'],
        'rustc_version_verbose': rustc_vv,
        'rr_frontend_lock_sha256': sha256(rr / 'rr_frontend/Cargo.lock'),
        'rust_distribution_archives_sha256': {key: sha256(args.context / name)
                                                for key, name in archives.items()},
        'os_package_inventory': packages,
        'os_package_bundle_sha256': sha256(args.context / 'debs.tar'),
        'cargo_vendor_archive_sha256': sha256(args.context / 'vendor.tar'),
        'cargo_config': {'path': str(cargo_config), 'sha256': sha256(cargo_config)},
        'binaries': {name: {'path': str(path), 'sha256': sha256(path)}
                     for name, path in BINARIES.items()},
        'ld_library_path': os.environ.get('LD_LIBRARY_PATH', ''),
        'receipt_generator_sha256': sha256(Path(__file__)),
    }
    if receipt['rr_frontend_lock_sha256'] != pins['rr_frontend_lock_sha256']:
        raise ValueError('RR Cargo.lock mismatch')
    args.out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
