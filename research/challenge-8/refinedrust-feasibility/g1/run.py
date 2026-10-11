#!/usr/bin/env python3
"""Cloud-only G1 frontend admission runner. Never invoke on the VPS, even --help.

No dispatch, coordinator, dependency installation or Rocq invocation. The
external execution authorization is supplied only after independent review.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import time

from annotate import prepare
from evidence import collect, digest, seal
from service import check_identity, normal_completion, negative_unknown_procedure, negative_source_certificate, positive_unit_definition
from verify_inputs import verify_checkout

HERE = Path(__file__).resolve().parent


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def authorization(path, pins):
    if (not os.environ.get('BUILD_ID') or not Path('/workspace').is_dir() or
        os.environ.get('SMALLSORT_EXECUTION_PROVIDER') != 'cloud-build'):
        raise ValueError('Cloud-only runner: BUILD_ID and /workspace required')
    auth = json.loads(path.read_text())
    if auth.get('schema') != 'rr-g1-execution-authorization-v1' or auth.get('authorized') is not True:
        raise ValueError('execution is not authorized')
    if auth.get('owner') != pins['dispatch']['owner'] or auth.get('project') != pins['dispatch']['project']:
        raise ValueError('wrong execution owner/project')
    if datetime.fromisoformat(auth['expires_at'].replace('Z', '+00:00')) <= datetime.now(timezone.utc):
        raise ValueError('execution window expired')
    ids = auth['identities']
    check_identity(ids, ids)
    required = {'build_id': os.environ['BUILD_ID'], 'source_sha': pins['source']['commit'],
                'tool_sha': pins['rr']['commit'], 'compiler_sha': pins['compiler']['commit'],
                'profile': pins['profile']}
    if any(ids.get(k) != v for k, v in required.items()):
        raise ValueError('authorization does not match pinned G1 inputs')
    # This is a misuse guard, not a substitute for dispatcher/IAM authorization.
    closure = auth['harness_sha256']
    needed = {'run.py', 'service.py', 'evidence.py', 'verify_inputs.py', 'annotate.py',
              'annotations.json', 'inputs.json', 'correspondence.py', 'cloud/IMAGE-INPUTS.json'}
    needed.update(str(p.relative_to(HERE)) for p in (HERE / 'controls').rglob('*') if p.is_file())
    if not needed.issubset(closure):
        raise ValueError('authorization omits executable harness/control closure')
    for name, sha in closure.items():
        rel = Path(name)
        p = HERE / rel
        if rel.is_absolute() or '..' in rel.parts or not p.resolve().is_relative_to(HERE) or p.is_symlink():
            raise ValueError('unsafe harness closure path')
        if digest(p) != sha:
            raise ValueError('harness byte mismatch: ' + name)
    for name in ('rustc', 'cargo', 'cargo_refinedrust', 'refinedrust_rustc'):
        spec = auth['binaries'][name]
        p = Path(spec['path'])
        if not p.is_absolute() or digest(p) != spec['sha256']:
            raise ValueError('image binary mismatch: ' + name)
    if Path(auth['binaries']['cargo_refinedrust']['path']).parent != Path(auth['binaries']['refinedrust_rustc']['path']).parent:
        raise ValueError('RR binaries must be siblings (stock get_rustc_path)')
    receipt = Path(auth['image_receipt'])
    if digest(receipt) != auth['image_receipt_sha256']:
        raise ValueError('image dependency receipt mismatch')
    image = json.loads(receipt.read_text())
    expected_image = {'schema': 'refinedrust-g1-image-receipt-v1',
                      'rr_commit': pins['rr']['commit'], 'rr_checkout_clean': True,
                      'compiler_source_commit': pins['compiler']['commit'],
                      'rr_frontend_lock_sha256': next(r['sha256'] for r in pins['rr']['files']
                                                     if r['path']=='rr_frontend/Cargo.lock')}
    if any(image.get(k) != v for k, v in expected_image.items()):
        raise ValueError('cold receipt tool/compiler provenance mismatch')
    if image.get('binaries') != auth['binaries'] or image.get('cargo_config', {}).get('sha256') != auth['cargo_config_sha256']:
        raise ValueError('binary/vendor configuration does not match cold receipt')
    image_pins = json.loads((HERE/'cloud/IMAGE-INPUTS.json').read_text())
    if image.get('rust_distribution_archives_sha256') != image_pins['archive_sha256_x86_64_unknown_linux_gnu']:
        raise ValueError('cold receipt compiler component closure mismatch')
    binding = auth.get('registry_binding') or {}
    if (binding.get('image_digest') != ids['image_digest'] or
        binding.get('image_receipt_sha256') != auth['image_receipt_sha256'] or
        not binding.get('cold_build_id') or
        not re.fullmatch('[0-9a-f]{64}', str(binding.get('registry_receipt_sha256', '')))):
        raise ValueError('independently reviewed registry/image/receipt binding absent')
    # The executing step digest still needs independent submitted-config/API
    # validation by dispatcher; an image cannot contain its own final digest.
    cargo_home = Path(auth['cargo_home'])
    if not cargo_home.is_absolute() or digest(cargo_home / 'config.toml') != auth['cargo_config_sha256']:
        raise ValueError('frozen Cargo source/vendor config missing/mismatch')
    if (cargo_home / 'config').exists():
        raise ValueError('second ambient Cargo config forbidden')
    return auth


def command(argv, cwd, env, directory, timeout):
    directory.mkdir(parents=True, exist_ok=True)
    write_json(directory / 'environment.json', env)
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    timed_out = False
    with (directory / 'command.log').open('wb') as log:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            code = proc.wait(timeout=max(1, timeout))
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                code = proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                code = None
            # The parent may have exited on TERM while its children still run.
            # Always kill the remaining process group before leaving the log.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            if code is None:
                try:
                    code = proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    code = None
    rec = {'argv': argv, 'cwd': str(cwd), 'evidence_dir': str(directory), 'started': started,
           'finished': datetime.now(timezone.utc).isoformat(), 'seconds': time.monotonic()-begin,
           'returncode': code, 'timed_out': timed_out, 'signaled': code is not None and code < 0,
           'environment_sha256': digest(directory / 'environment.json'),
           'log_sha256': digest(directory / 'command.log'),
           'log_bytes': (directory / 'command.log').stat().st_size,
           'child_peak_rss_kib_cumulative': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}
    if 'RR_CONFIG' in env:
        rec['rr_config_sha256'] = digest(Path(env['RR_CONFIG']))
    write_json(directory / 'command.json', rec)
    return rec


def rr_env(base, rr, directory):
    directory.mkdir(parents=True, exist_ok=True)
    config = directory / 'RefinedRust.toml'
    # Import no stdlib summaries into actual core: ordinary selected callees must
    # be translated. Missing bindings produce a diagnostic, not assumed safety.
    config.write_text('''skip_unsupported_features = false
register_all_adts = false
dump_debug_info = true
dump_borrowck_info = true
generate_linking_requirements = true
run_check = false
no_verify = false
admit_proofs = false
trust_debug = false
find_stdlib = false
panic_abort_mode = "conservative"
check_overflows = true
post_generation_hook = []
lib_load_paths = []
'''.replace('post_generation_hook = []\n', '') +
                      'log_dir = ' + json.dumps(str(directory / 'log')) + '\n' +
                      'output_dir = ' + json.dumps(str(directory / 'output')) + '\n')
    # No unrecorded RR overrides; stock wrapper sets only RUSTC/RR_OUTPUT_DIR.
    env = dict(base, RR_CONFIG=str(config), CARGO_TARGET_DIR=str(directory / 'target'))
    write_json(directory / 'environment.json', env)
    return env


def execute(repo, rr, out, auth):
    pins = json.loads((HERE / 'inputs.json').read_text())
    ids = auth['identities']
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / 'identity.json', ids)
    shutil.copyfile(HERE / 'inputs.json', out / 'inputs.json')
    shutil.copyfile(auth['image_receipt'], out / 'image-receipt.json')
    shutil.copyfile(Path(auth['cargo_home']) / 'config.toml', out / 'cargo-config.toml')
    stages, controls = {}, {}
    execution = {'stages': stages, 'controls': controls}
    source = {'source_commit': pins['source']['commit'], 'build_id': ids['build_id'],
              'sources': {}, 'correspondence': {}, 'annotation_status': 'NOT_RUN'}
    write_json(out / 'source-receipt.json', source)
    write_json(out / 'execution.json', execution)
    binaries = auth['binaries']
    base = {'PATH': ':'.join((str(Path(binaries['cargo_refinedrust']['path']).parent),
                             str(Path(binaries['cargo']['path']).parent), '/usr/bin', '/bin')),
            'HOME': str(out / 'home'), 'CARGO_HOME': auth['cargo_home'],
            'RUSTUP_TOOLCHAIN': pins['compiler']['channel'], 'RUSTC_BOOTSTRAP': '1',
            'RUSTFLAGS': '-Cpanic=unwind -Coverflow-checks=on', 'CARGO_BUILD_JOBS': '2',
            'CARGO_NET_OFFLINE': 'true', 'BUILD_ID': ids['build_id'],
            'LD_LIBRARY_PATH': '/opt/rust/lib:/opt/rust/lib/rustlib/x86_64-unknown-linux-gnu/lib'}
    Path(base['HOME']).mkdir()
    deadline = time.monotonic()  # replaced by reviewed wrapper preflight below
    def invoke(name, argv, cwd, env, limit):
        remain = int(deadline - time.monotonic())
        if remain <= 0:
            raise TimeoutError('G1 work deadline exhausted')
        rec = command(argv, cwd, env, out / name, min(limit, remain))
        stages[name] = rec
        write_json(out / 'execution.json', execution)
        return rec
    try:
        # Respect time already consumed by source transport/restore in the outer
        # reviewed dispatcher. Leave 90 s for correspondence/inventory before its
        # independent 70 s archive/upload reserve; do not invent a new Build clock.
        wrapper_remaining = float(os.environ['SMALLSORT_DEADLINE_EPOCH']) - time.time()
        if wrapper_remaining <= 90:
            raise ValueError('insufficient reviewed wrapper work window')
        deadline = time.monotonic() + min(1050, wrapper_remaining) - 90
        src = verify_checkout(repo, pins['source'])
        tool = verify_checkout(rr, pins['rr'])
        stages['inputs'] = {'ok': True, 'source': src, 'tool': tool,
                            'free_disk_bytes': shutil.disk_usage(out).free}
        if stages['inputs']['free_disk_bytes'] < 40 * 1024 ** 3:
            raise ValueError('less than 40 GiB free workspace')
        rec = invoke('versions', [binaries['rustc']['path'], '-Vv'], repo, base, 15)
        version = (out / 'versions/command.log').read_text()
        stages['compiler'] = {'ok': normal_completion(rec) and rec['returncode'] == 0 and
                             ('commit-hash: ' + pins['compiler']['commit']) in version and
                             ('host: ' + pins['compiler']['host']) in version,
                             'version_log': 'versions/command.log'}
        if not stages['compiler']['ok']:
            raise ValueError('compiler version mismatch')
        controls_started = time.monotonic()
        for name in ('p0', 'n1'):
            work = out / name / 'fixture'
            shutil.copytree(HERE / 'controls' / name, work)
            env = rr_env(base, rr, out / name)
            budget = max(1, int(90 - (time.monotonic() - controls_started)))
            result = invoke(name, [binaries['cargo_refinedrust']['path'], '--', '--manifest-path',
                                   str(work / 'Cargo.toml'), '--locked', '--offline', '--target',
                                   pins['compiler']['host']], work, env, budget)
            if name == 'p0':
                controls['P0'] = normal_completion(result) and result['returncode'] == 0 and any(
                    positive_unit_definition(f.read_text(errors='replace'))
                    for f in (out / name / 'output').rglob('*.v'))
            else:
                controls['N1'] = negative_unknown_procedure(
                    result['returncode'], (out / name / 'command.log').read_text(errors='replace'),
                    timed_out=result['timed_out'], signaled=result['signaled'])
        annotation_manifest = json.loads((HERE/'annotations.json').read_text())
        hashes = {rec['source_key']: rec['sha256'] for rec in annotation_manifest['files']}
        fixture = json.loads((HERE/'controls/n2-source-certificate.json').read_text())
        controls['N2'] = negative_source_certificate(fixture, pins['source']['commit'], hashes)
        shutil.copyfile(HERE/'controls/n2-source-certificate.json', out/'n2-source-certificate.json')
        if not all(controls.values()):
            raise ValueError('diagnostic control failed')
        native_env = dict(base, CARGO_TARGET_DIR=str(out / 'native-target'))
        result = invoke('native', [binaries['cargo']['path'], 'check', '--manifest-path',
                                  str(repo / 'library/Cargo.toml'), '-p', 'core', '--locked',
                                  '--offline', '--target', pins['compiler']['host']], repo, native_env, 240)
        if not normal_completion(result) or result['returncode'] != 0:
            result['compiler_rejection'] = bool(re.search(r'error\[E\d+\]', (out/'native/command.log').read_text(errors='replace')))
            raise ValueError('native core admission failed')
        certificate = prepare(repo, out / 'source-receipt.json.pending')
        source = dict(certificate, sources=certificate['source_receipt']['sources'])
        # prepare archive parent is evidence root; replace initial NOT_RUN receipt.
        (out / 'source-receipt.json.pending').replace(out / 'source-receipt.json')
        source['source_base_dir'] = str(out)
        source['correspondence'] = {}
        write_json(out / 'source-receipt.json', source)
        env = rr_env(base, rr, out / 'p1')
        invoke('p1', [binaries['cargo_refinedrust']['path'], '--', '--manifest-path',
                      str(repo/'library/Cargo.toml'), '-p', 'core', '--locked', '--offline',
                      '--target', pins['compiler']['host']], repo, env, 540)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError, TimeoutError) as exc:
        execution['runner_error'] = {'type': type(exc).__name__, 'message': str(exc)}
        stages.setdefault('inputs', {'ok': False})
    finally:
        # CARGO_TARGET_DIR contains huge compiler artifacts, not evidence. MIR and
        # Radium logs/output are outside it; preserve every diagnostic before removal.
        for name in ('p0', 'n1', 'p1'):
            shutil.rmtree(out / name / 'target', ignore_errors=True)
        shutil.rmtree(out / 'native-target', ignore_errors=True)
        write_json(out / 'execution.json', execution)
        write_json(out / 'summary.json', {'verdict': 'INCONCLUSIVE', 'proof_status': 'NOT_RUN',
                                         'verification_accepted': False,
                                         'local_inventory_valid': False,
                                         'diagnostic_complete': False,
                                         'evidence_complete': False,
                                         'status': 'classification pending'})
        seal(out)
        try:
            summary = collect(out, ids)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            summary = {'verdict': 'INCONCLUSIVE', 'blocker': 'collector: ' + str(exc),
                       'verification_accepted': False, 'proof_status': 'NOT_RUN',
                       'local_inventory_valid': False, 'diagnostic_complete': False,
                       'evidence_complete': False}
        write_json(out / 'summary.json', summary)
        seal(out)
    return 0 if summary['verdict'] == 'PASS' else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--rr', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--authorization', type=Path, required=True)
    args = parser.parse_args()
    pins = json.loads((HERE/'inputs.json').read_text())
    auth = authorization(args.authorization, pins)
    repo, rr, out = args.repo.resolve(), args.rr.resolve(), args.out.resolve()
    if not out.is_relative_to(Path('/workspace')) or out.exists():
        raise ValueError('fresh Cloud evidence path required')
    if repo == rr or out.is_relative_to(repo) or out.is_relative_to(rr):
        raise ValueError('source/tool/evidence paths must be disjoint')
    return execute(repo, rr, out, auth)


if __name__ == '__main__':
    raise SystemExit(main())
