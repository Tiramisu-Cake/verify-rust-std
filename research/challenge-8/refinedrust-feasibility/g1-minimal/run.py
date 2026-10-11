#!/usr/bin/env python3
"""Cloud-only diagnostic candidate. Never run/import this driver on the VPS.

Uses existing byte verifier/injector; no Radium parser or proof execution.
The existing dispatcher owns authorization, source transport, upload and accounting.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
from service import audit, first_diagnostic
sys.path.insert(0, str(HERE.parent / 'g1'))
from annotate import prepare
from verify_inputs import verify_checkout


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main():
    # Misuse guard, not authentication: only reviewed dispatcher can grant a run.
    if (os.environ.get('SMALLSORT_EXECUTION_PROVIDER') != 'cloud-build' or
            not os.environ.get('CLOUD_BUILD_ID') or not Path('/workspace').is_dir()):
        raise SystemExit('Cloud-only candidate; no local invocation, including --help')
    parser = argparse.ArgumentParser()
    for name in ('source', 'rr', 'freeze', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    source = args.source.resolve()
    rr = args.rr.resolve()
    if (not out.is_relative_to('/workspace/evidence') or out.exists() or
            not source.is_relative_to('/workspace') or source.exists()):
        raise SystemExit('fresh evidence and disposable source paths required')
    out.mkdir(parents=True)
    outer = out.parent
    pins = json.loads((HERE / 'inputs.json').read_text())
    commands = {}
    failed_stage = 'freeze'
    inventory_ok = False
    base = {}
    deadline = float(os.environ['SMALLSORT_DEADLINE_EPOCH']) - 15
    build_id = os.environ['CLOUD_BUILD_ID']

    def command(name, argv, cwd, env, cap):
        nonlocal failed_stage
        failed_stage = name
        directory = out / name
        directory.mkdir()
        log = directory / 'command.log'
        allowance = min(cap, int(deadline - time.time()))
        if allowance <= 0:
            raise ValueError('dispatcher work deadline exhausted')
        rec = {'argv': argv, 'cwd': str(cwd), 'started_epoch': time.time(), 'timeout_seconds': allowance}
        write(directory / 'environment.json', env)
        if 'RR_CONFIG' in env:
            shutil.copyfile(env['RR_CONFIG'], directory / 'RefinedRust.toml')
            rec['rr_config_sha256'] = sha(directory / 'RefinedRust.toml')
        write(directory / 'command.json', rec)
        timed_out = False
        with log.open('wb') as stream:
            proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = proc.wait(timeout=allowance)
            except subprocess.TimeoutExpired:
                timed_out = True
                for sig in (signal.SIGTERM, signal.SIGKILL):
                    try:
                        os.killpg(proc.pid, sig)
                    except ProcessLookupError:
                        pass
                    if sig == signal.SIGTERM:
                        try:
                            proc.wait(timeout=2)
                        except subprocess.TimeoutExpired:
                            pass
                code = proc.wait(timeout=2)
        rec.update(returncode=code, timed_out=timed_out, finished_epoch=time.time(),
                   log_sha256=sha(log), child_peak_rss_kib_cumulative=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                   first_diagnostic=first_diagnostic(log.read_text(errors='replace')))
        commands[name] = rec
        write(directory / 'command.json', rec)
        # Standard existing packager stage files; raw originals stay in g1/.
        shutil.copyfile(log, outer / 'allprooflogs' / (name + '.log'))
        (outer / 'allprooflogs' / (name + '-exit-code.txt')).write_text(str(code) + '\n')
        if timed_out or code < 0:
            raise ValueError('timeout/signal at ' + name)
        return code

    try:
        (outer / 'allprooflogs/cases/g1-minimal').mkdir(parents=True, exist_ok=True)
        freeze = json.loads(args.freeze.read_text())
        shutil.copyfile(args.freeze, out / 'freeze.json')
        if (freeze.get('schema') != 'rr-g1-minimal-freeze-v1' or
                not re.fullmatch(r'[^\s]+@sha256:[0-9a-f]{64}', freeze.get('image_digest') or '') or
                freeze['image_digest'] != os.environ.get('PROOF_IMAGE')):
            raise ValueError('reviewed image freeze absent or submitted image mismatch')
        bins = freeze['binaries']
        for name in ('rustc', 'cargo', 'cargo-refinedrust', 'refinedrust-rustc'):
            spec = bins[name]
            path = Path(spec['path'])
            if (not path.is_absolute() or not re.fullmatch(r'[0-9a-f]{64}', spec.get('sha256') or '') or
                    sha(path) != spec['sha256']):
                raise ValueError('unfrozen/mismatching binary: ' + name)
        if Path(bins['cargo-refinedrust']['path']).parent != Path(bins['refinedrust-rustc']['path']).parent:
            raise ValueError('stock RR binaries must be siblings')
        cargo_home = Path(freeze['cargo_home'])
        cargo_config = cargo_home / 'config.toml'
        if (not cargo_home.is_absolute() or not re.fullmatch(r'[0-9a-f]{64}', freeze.get('cargo_config_sha256') or '') or
                sha(cargo_config) != freeze['cargo_config_sha256'] or (cargo_home / 'config').exists()):
            raise ValueError('locked Cargo dependency/vendor configuration missing')
        paths = freeze.get('lib_load_paths')
        if not isinstance(paths, list) or not paths:
            raise ValueError('official pinned stdlib export paths not frozen')
        for raw in paths:
            path = Path(raw).resolve(strict=True)
            if not path.is_dir() or not path.is_relative_to(rr) or not any(path.rglob('*.rrlib')):
                raise ValueError('missing pinned stdlib exports: ' + raw)
        # Existing verifier checks committed bytes of complete RR/source closure.
        failed_stage = 'tool-inputs'
        write(out / 'tool-receipt.json', verify_checkout(rr, pins['rr']))
        write(out / 'inputs.json', {k: pins[k] for k in ('source', 'rr', 'compiler', 'profile')})
        base = {'PATH': ':'.join((str(Path(bins['cargo-refinedrust']['path']).parent),
                    str(Path(bins['cargo']['path']).parent), '/usr/bin', '/bin')),
                'HOME': '/workspace/g1-home', 'CARGO_HOME': str(cargo_home),
                'CARGO_NET_OFFLINE': 'true', 'CARGO_BUILD_JOBS': '1',
                'RUSTUP_TOOLCHAIN': pins['compiler']['channel'], 'RUSTC_BOOTSTRAP': '1',
                'RUSTFLAGS': '-Cpanic=unwind -Coverflow-checks=on',
                'RUST_LOG': 'info',
                'LD_LIBRARY_PATH': '/opt/rust/lib:/opt/rust/lib/rustlib/x86_64-unknown-linux-gnu/lib',
                'BUILD_ID': build_id, 'CLOUD_BUILD_ID': build_id,
                'SMALLSORT_EXECUTION_PROVIDER': 'cloud-build', 'GIT_TERMINAL_PROMPT': '0',
                'GIT_CONFIG_NOSYSTEM': '1'}
        Path(base['HOME']).mkdir()
        if command('rustc-version', [bins['rustc']['path'], '-Vv'], rr, base, 15) != 0:
            raise ValueError('rustc version failed')
        version = (out / 'rustc-version/command.log').read_text()
        if ('commit-hash: ' + pins['compiler']['commit']) not in version or ('host: ' + pins['compiler']['host']) not in version:
            raise ValueError('compiler identity mismatch')
        if command('cargo-version', [bins['cargo']['path'], '-V'], rr, base, 15) != 0:
            raise ValueError('cargo version failed')
        if command('rr-version', [bins['cargo-refinedrust']['path'], '--version'], rr, base, 15) != 0:
            raise ValueError('stock RR version report failed')
        rr_version = (out / 'rr-version/command.log').read_text()
        if ((' (' + bins['cargo']['path'] + ')') not in rr_version or
                (' (' + bins['rustc']['path'] + ')') not in rr_version):
            raise ValueError('RR compile-time Cargo/rustc paths differ from frozen binaries')
        if command('source-restore', ['bash', str(HERE / 'restore-source.sh'), str(source)], rr, base, 180) != 0:
            raise ValueError('exact source transfer failed')
        failed_stage = 'source-inputs'
        write(out / 'source-receipt.json', verify_checkout(source, pins['source']))
        failed_stage = 'annotations'
        # Reuse only inert byte injector, with new minimal manifest (no unit/True).
        os.environ['BUILD_ID'] = build_id
        prepare(source, out / 'ghost-receipt.json', HERE / 'annotations.json')
        work = Path('/workspace/g1-cargo-targets')
        if work.exists():
            raise ValueError('fresh Cargo target directory required')
        env = dict(base, CARGO_TARGET_DIR=str(work))
        config = out / 'RefinedRust.toml'
        config.write_text('run_check = false\nno_verify = false\nadmit_proofs = false\ntrust_debug = false\n'
                          'skip_unsupported_features = false\nregister_all_adts = false\n'
                          'dump_debug_info = true\ndump_borrowck_info = true\ngenerate_linking_requirements = true\n'
                          'find_stdlib = false\npanic_abort_mode = "conservative"\ncheck_overflows = true\n' +
                          'lib_load_paths = ' + json.dumps(paths) + '\n' +
                          'output_dir = ' + json.dumps(str(out / 'output')) + '\n' +
                          'log_dir = ' + json.dumps(str(out / 'frontend-log')) + '\n')
        env['RR_CONFIG'] = str(config)
        control = out / 'control-crate'
        shutil.copytree(HERE.parent / 'g1/controls/p0', control)
        common = ['--locked', '--offline', '--target', pins['compiler']['host']]
        argv = [bins['cargo-refinedrust']['path'], '--', '--manifest-path', str(control / 'Cargo.toml'), *common]
        if command('control', argv, control, env, 90) != 0:
            raise ValueError('baseline frontend control failed; target NOT_RUN')
        if not any((out / 'output').rglob('generated_code_*.v')):
            raise ValueError('control generated code absent; target NOT_RUN')
        # Separate output dirs avoid mistaking the tiny control for target output.
        config.write_text(config.read_text().replace(str(out / 'output'), str(out / 'target-output'))
                          .replace(str(out / 'frontend-log'), str(out / 'target-frontend-log')))
        argv = [bins['cargo-refinedrust']['path'], '--', '--manifest-path', str(source / 'library/Cargo.toml'), '-p', 'core', *common]
        target_code = command('target', argv, source, env, 720)
        write(out / 'first-blocker.json', {
            'stage': 'target' if target_code else 'unproved-obligations',
            'returncode': target_code,
            'diagnostic': commands['target']['first_diagnostic'],
            'reason': ('Inspect original frontend log for compiler/admission/feature/binding cause'
                       if target_code else 'Resource/linking obligations and actual source mapping require review/proof'),
            'target_attribution': 'UNREVIEWED'})
        failed_stage = None
        # All generated files in configured output/log paths are retained, even on error.
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        write(out / 'first-blocker.json', {'stage': failed_stage, 'reason': str(exc), 'target_attribution': 'UNREVIEWED'})
    finally:
        write(out / 'execution.json', commands)
        try:
            files = {}
            for path in sorted(out.rglob('*')):
                if path.is_symlink():
                    raise ValueError('evidence symlink: ' + str(path))
                if path.is_file():
                    files[str(path.relative_to(out))] = {'sha256': sha(path), 'bytes': path.stat().st_size}
            write(out / 'inventory.json', files)
            inventory_ok = True
        except (OSError, ValueError) as exc:
            failed_stage = 'inventory'
            write(out / 'inventory-error.json', {'error': str(exc)})
        result = audit(commands, failed_stage, inventory_ok)
        write(outer / 'allprooflogs/cases/g1-minimal/result.json', result)
        write(outer / 'allprooflogs/proof-audit.json', result)
    return 0 if result['diagnostic_complete'] else 2


if __name__ == '__main__':
    sys.exit(main())
