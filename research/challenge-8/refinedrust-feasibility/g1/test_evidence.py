"""Synthetic collector tests; imports only evidence/service, never the Cloud runner."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from evidence import RR_PROFILE, collect, digest, seal
from test_service import IDS as TEST_IDS


HERE = Path(__file__).parent
PINS = json.loads((HERE / 'inputs.json').read_text())
IDS = dict(TEST_IDS, source_sha=PINS['source']['commit'], tool_sha=PINS['rr']['commit'],
           compiler_sha=PINS['compiler']['commit'], profile=PINS['profile'])
P0 = 'Program Definition g1_p0_def : function :=\n {| f_code := [x]; f_init := "_bb0" |}.\nFinal Obligation.\n'
N1 = 'error: Unknown procedure: DefId(0:9 ~ rr_g1_n1[abc]::g1_unregistered)\n'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def make_archive(root, with_p1=False):
    pins = json.loads((HERE / 'inputs.json').read_text())
    shutil.copyfile(HERE / 'inputs.json', root / 'inputs.json')
    shutil.copyfile(HERE / 'controls/n2-source-certificate.json', root / 'n2-source-certificate.json')
    (root / 'cargo-config.toml').write_text('[net]\noffline = true\n')
    lock = next(r['sha256'] for r in pins['rr']['files'] if r['path'] == 'rr_frontend/Cargo.lock')
    image_pins = json.loads((HERE / 'cloud/IMAGE-INPUTS.json').read_text())
    write_json(root / 'image-receipt.json', {
        'schema': 'refinedrust-g1-image-receipt-v1', 'rr_commit': pins['rr']['commit'],
        'rr_checkout_clean': True,
        'compiler_source_commit': pins['compiler']['commit'], 'rr_frontend_lock_sha256': lock,
        'rust_distribution_archives_sha256': image_pins['archive_sha256_x86_64_unknown_linux_gnu'],
        'cargo_config': {'path': '/opt/g1-cargo/config.toml',
                         'sha256': digest(root / 'cargo-config.toml')},
        'ld_library_path': '/opt/rust/lib:/opt/rust/lib/rustlib/x86_64-unknown-linux-gnu/lib',
        'binaries': {'rustc': {'path': '/opt/rust/bin/rustc', 'sha256': 'a'*64},
                     'cargo': {'path': '/opt/rust/bin/cargo', 'sha256': 'b'*64},
                     'cargo_refinedrust': {'path': '/opt/rr-bin/cargo-refinedrust', 'sha256': 'c'*64},
                     'refinedrust_rustc': {'path': '/opt/rr-bin/refinedrust-rustc', 'sha256': 'd'*64}}})
    write_json(root / 'identity.json', IDS)
    write_json(root / 'source-receipt.json', {
        'source_commit': IDS['source_sha'], 'build_id': IDS['build_id'], 'sources': {},
        'manifest_sha256': digest(HERE / 'annotations.json') if with_p1 else None})
    write_json(root / 'summary.json', {'verdict': 'INCONCLUSIVE'})
    stages = {'inputs': {'ok': True}, 'compiler': {'ok': True}}
    command_names = ('versions', 'p0', 'n1', 'native', 'p1') if with_p1 else ('versions', 'p0', 'n1', 'native')
    for name in command_names:
        directory = root / name
        directory.mkdir()
        env = {'BUILD_ID': IDS['build_id'], 'CARGO_HOME': '/opt/g1-cargo',
               'HOME': '/workspace/archive/home',
               'PATH': '/opt/rr-bin:/opt/rust/bin:/usr/bin:/bin',
               'RUSTUP_TOOLCHAIN': pins['compiler']['channel'], 'RUSTC_BOOTSTRAP': '1',
               'RUSTFLAGS': '-Cpanic=unwind -Coverflow-checks=on',
               'CARGO_NET_OFFLINE': 'true', 'CARGO_BUILD_JOBS': '2',
               'LD_LIBRARY_PATH': '/opt/rust/lib:/opt/rust/lib/rustlib/x86_64-unknown-linux-gnu/lib'}
        if name in ('p0', 'n1', 'p1'):
            config = ''.join(key + ' = ' + json.dumps(value) + '\n'
                             for key, value in RR_PROFILE.items())
            config += 'log_dir = ' + json.dumps('/workspace/archive/' + name + '/log') + '\n'
            config += 'output_dir = ' + json.dumps('/workspace/archive/' + name + '/output') + '\n'
            (directory / 'RefinedRust.toml').write_text(config)
            env.update(RR_CONFIG='/workspace/archive/' + name + '/RefinedRust.toml',
                       CARGO_TARGET_DIR='/workspace/archive/' + name + '/target')
        if name == 'native':
            env['CARGO_TARGET_DIR'] = '/workspace/archive/native-target'
        write_json(directory / 'environment.json', env)
        version_text = ('rustc synthetic\ncommit-hash: ' + pins['compiler']['commit'] +
                        '\nhost: ' + pins['compiler']['host'] + '\n')
        (directory / 'command.log').write_text(
            N1 if name == 'n1' else version_text if name == 'versions' else 'normal\n')
        binary = {'versions': '/opt/rust/bin/rustc', 'native': '/opt/rust/bin/cargo'}.get(
            name, '/opt/rr-bin/cargo-refinedrust')
        original_dir = '/workspace/archive/' + name
        cwd = original_dir + '/fixture' if name in ('p0', 'n1') else '/workspace/source'
        if name == 'versions':
            argv = [binary, '-Vv']
        elif name in ('p0', 'n1'):
            argv = [binary, '--', '--manifest-path', cwd + '/Cargo.toml',
                    '--locked', '--offline', '--target', pins['compiler']['host']]
        elif name == 'native':
            argv = [binary, 'check', '--manifest-path', cwd + '/library/Cargo.toml',
                    '-p', 'core', '--locked', '--offline', '--target', pins['compiler']['host']]
        else:
            argv = [binary, '--', '--manifest-path', cwd + '/library/Cargo.toml',
                    '-p', 'core', '--locked', '--offline', '--target', pins['compiler']['host']]
        record = {'argv': argv, 'cwd': cwd, 'evidence_dir': original_dir,
                  'returncode': 1 if name == 'n1' else 0, 'timed_out': False,
                  'signaled': False, 'log_sha256': digest(directory / 'command.log'),
                  'log_bytes': (directory / 'command.log').stat().st_size,
                  'environment_sha256': digest(directory / 'environment.json')}
        if name in ('p0', 'n1', 'p1'):
            record['rr_config_sha256'] = digest(directory / 'RefinedRust.toml')
        write_json(directory / 'command.json', record)
        stages[name] = record
    (root / 'p0/output').mkdir()
    (root / 'p0/output/positive.v').write_text(P0)
    write_json(root / 'execution.json', {
        'stages': stages, 'controls': {'P0': True, 'N1': True, 'N2': True}})
    seal(root)


class Evidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='rr-g1-evidence-')
        self.root = Path(self.tmp.name)
        make_archive(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_labels_and_recomputed_controls(self):
        result = collect(self.root, IDS)
        self.assertEqual(result['controls'], {'P0': True, 'N1': True, 'N2': True})
        self.assertTrue(result['local_inventory_valid'])
        self.assertFalse(result['diagnostic_complete'])  # no source correspondence
        self.assertFalse(result['evidence_complete'])  # external package verification absent
        self.assertFalse(result['verification_accepted'])
        self.assertEqual(result['proof_status'], 'NOT_RUN')
        execution = json.loads((self.root / 'execution.json').read_text())
        execution['controls'] = {'P0': False, 'N1': False, 'N2': False}
        write_json(self.root / 'execution.json', execution)
        seal(self.root)
        self.assertEqual(collect(self.root, IDS)['controls'], {'P0': True, 'N1': True, 'N2': True})

    def test_required_artifact_deletion_even_after_reseal(self):
        for rel in ('image-receipt.json', 'cargo-config.toml', 'n2-source-certificate.json',
                    'p0/command.json', 'p0/command.log', 'p0/environment.json',
                    'p0/RefinedRust.toml', 'native/command.json', 'n1/RefinedRust.toml'):
            with self.subTest(rel=rel):
                original = (self.root / rel).read_bytes()
                (self.root / rel).unlink()
                seal(self.root)
                with self.assertRaises(ValueError):
                    collect(self.root, IDS)
                (self.root / rel).write_bytes(original)
                seal(self.root)

    def test_substitution_and_cross_record_mismatch(self):
        paths = ('n2-source-certificate.json', 'p0/command.log',
                 'p0/environment.json', 'p0/RefinedRust.toml', 'cargo-config.toml')
        for rel in paths:
            with self.subTest(rel=rel):
                path = self.root / rel
                original = path.read_bytes()
                path.write_bytes(original + b'changed\n')
                seal(self.root)
                with self.assertRaises(ValueError):
                    collect(self.root, IDS)
                path.write_bytes(original)
                seal(self.root)
        execution = json.loads((self.root / 'execution.json').read_text())
        execution['stages']['native']['returncode'] = 1
        write_json(self.root / 'execution.json', execution)
        seal(self.root)
        with self.assertRaisesRegex(ValueError, 'record mismatch'):
            collect(self.root, IDS)
        make_archive_reset(self.root)
        config = self.root / 'p0/RefinedRust.toml'
        config.write_text(config.read_text().replace('run_check = false', 'run_check = 0'))
        record = json.loads((self.root / 'p0/command.json').read_text())
        record['rr_config_sha256'] = digest(config)
        write_json(self.root / 'p0/command.json', record)
        execution = json.loads((self.root / 'execution.json').read_text())
        execution['stages']['p0'] = record
        write_json(self.root / 'execution.json', execution)
        seal(self.root)
        with self.assertRaisesRegex(ValueError, 'RR profile mismatch'):
            collect(self.root, IDS)

    def test_interrupted_controls_and_native_p1(self):
        def alter(name, code, timeout):
            original = json.loads((self.root / 'execution.json').read_text())
            record = copy.deepcopy(original['stages'][name])
            record.update(returncode=code, timed_out=timeout, signaled=code < 0)
            write_json(self.root / name / 'command.json', record)
            original['stages'][name] = record
            write_json(self.root / 'execution.json', original)
            seal(self.root)
            return collect(self.root, IDS)

        for name, code, timeout in (('p0', 0, True), ('n1', -9, False),
                                    ('n1', 1, True), ('native', 0, True),
                                    ('native', -15, False)):
            with self.subTest(name=name, code=code, timeout=timeout):
                make_archive_reset(self.root)
                result = alter(name, code, timeout)
                self.assertNotEqual(result['verdict'], 'PASS')
                if name == 'p0':
                    self.assertFalse(result['controls']['P0'])
                if name == 'n1':
                    self.assertFalse(result['controls']['N1'])

    def test_not_run_stages_have_causal_status(self):
        execution = json.loads((self.root / 'execution.json').read_text())
        del execution['stages']['native']
        shutil.rmtree(self.root / 'native')
        write_json(self.root / 'execution.json', execution)
        seal(self.root)
        result = collect(self.root, IDS)
        self.assertEqual(result['stage_status']['native']['status'], 'NOT_RUN')
        self.assertEqual(result['stage_status']['p1']['status'], 'NOT_RUN')

    def test_p1_requires_all_source_archives(self):
        make_archive_reset(self.root, with_p1=True)
        with self.assertRaisesRegex(ValueError, 'P1 requires all four'):
            collect(self.root, IDS)


def make_archive_reset(root, with_p1=False):
    for child in root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    make_archive(root, with_p1=with_p1)


if __name__ == '__main__':
    unittest.main()
