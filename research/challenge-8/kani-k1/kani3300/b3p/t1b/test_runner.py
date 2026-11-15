"""Python-only fixtures; no backend, package installation, network or builds."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path('/root/kani-b3-t1/.github/b3-t1b/run.py')
sys.path.insert(0, str(MODULE.parent))
spec = importlib.util.spec_from_file_location('t1b_runner', MODULE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
import compare


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


class Validation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.data = {}
        rows = ['control', *compare.PERF_ROWS]
        for arm in m.ARMS:
            records = {}
            row_info = {}
            total = 0
            for n, row in enumerate(rows):
                count = 1 if n == 0 else (9 if n <= 10 else 8)
                names = ['array_typed_copy'] if n == 0 else [f'h{n}_{i}' for i in range(count)]
                row_info[row] = {'expected_harnesses': names, 'captured_harnesses': names, 'exit': 1}
                for name in names:
                    key = f'final/{row}/{name}'
                    records[key] = {'kind': 'final', 'row': row, 'harness': name,
                                    'argv': ['/source/test.out', '--json-ui'], 'cwd': '/source'}
                    total += 1
                for kind in ('linked', 'symtab', 'metadata'):
                    records[f'{kind}/{row}/source-{n}'] = {'kind': kind, 'row': row}
            assert total == 131
            for i in range(409 - len(records)):
                records[f'metadata/control/extra-{i}'] = {'kind': 'metadata', 'row': 'control'}
            for key, rec in records.items():
                rel = 'files/' + hashlib.sha256(key.encode()).hexdigest()
                payload = key.encode()
                rec.update(path=rel, sha256=hashlib.sha256(payload).hexdigest())
                p = cls.root / arm / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(payload)
                save(cls.root / arm / 'records' / (Path(rel).name + '.json'), {'key': key, 'record': rec})
            tools = {k: 'a' * 64 for k in compare.REQUIRED_TOOLS}
            if arm == 'B1':
                tools.update({k: 'b' * 64 for k in compare.EXCLUDED_AB_TOOLS})
            data = {'complete': True, 'records': records, 'rows': row_info, 'tools': tools,
                    'locks': {k: 'e' * 64 for k in compare.REQUIRED_LOCKS}}
            cls.data[arm] = data
            save(cls.root / arm / 'index.json', data)
            save(cls.root / arm / 'tools.json', {k: {'path': '/bin/' + k, 'sha256': v} for k, v in tools.items()})

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_complete_409_131_and_all_hashes(self):
        result = m.validate(self.root)
        self.assertEqual(len(result['A1']['records']), 409)

    def test_index_missing_null_wrong_type_partial_and_not_run(self):
        path = self.root / 'A2/index.json'
        for update in ({'complete': False}, {'records': None}, {'rows': []}, {'complete': 'NOT_RUN'}):
            with self.subTest(update=update):
                data = copy.deepcopy(self.data['A2'])
                data.update(update)
                save(path, data)
                try:
                    with self.assertRaises(m.Invalid):
                        m.validate(self.root)
                finally:
                    save(path, self.data['A2'])

    def test_record_and_index_disagreement(self):
        p = next((self.root / 'A2/records').glob('*.json'))
        old = p.read_text()
        data = json.loads(old)
        data['record']['row'] = 'unknown'
        save(p, data)
        try:
            with self.assertRaisesRegex(m.Invalid, 'records/index mismatch'):
                m.validate(self.root)
        finally:
            p.write_text(old)

    def test_missing_record_and_duplicate_json_key(self):
        p = next((self.root / 'A2/records').glob('*.json'))
        old = p.read_text()
        p.unlink()
        try:
            with self.assertRaisesRegex(m.Invalid, 'records/index mismatch'):
                m.validate(self.root)
        finally:
            p.write_text(old)
        p.write_text('{"key":"first","key":"second","record":null}')
        try:
            with self.assertRaisesRegex(m.Invalid, 'duplicate JSON key'):
                m.validate(self.root)
        finally:
            p.write_text(old)

    def test_unrecorded_file(self):
        path = self.root / 'A2/files/unrecorded'
        path.write_bytes(b'unbound payload')
        try:
            with self.assertRaisesRegex(m.Invalid, 'unrecorded'):
                m.validate(self.root)
        finally:
            path.unlink()

    def test_wrong_tool_hash(self):
        p = self.root / 'B1/tools.json'
        old = p.read_text()
        data = json.loads(old)
        data['goto-instrument']['sha256'] = 'f' * 64
        save(p, data)
        try:
            with self.assertRaisesRegex(m.Invalid, 'hash mismatch'):
                m.validate(self.root)
        finally:
            p.write_text(old)

    def test_changed_model_hash(self):
        rec = next(iter(self.data['A2']['records'].values()))
        p = self.root / 'A2' / rec['path']
        old = p.read_bytes()
        p.write_bytes(b'corruption')
        try:
            with self.assertRaisesRegex(m.Invalid, 'sha256 mismatch'):
                m.validate(self.root)
        finally:
            p.write_bytes(old)

    def test_source_target_argv_mismatch(self):
        p = self.root / 'B1/index.json'
        old = p.read_text()
        data = json.loads(old)
        key = next(k for k in data['records'] if k.startswith('final/'))
        data['records'][key]['argv'][0] = '/other/target.out'
        save(p, data)
        rp = self.root / 'B1/records' / (Path(data['records'][key]['path']).name + '.json')
        rold = rp.read_text()
        save(rp, {'key': key, 'record': data['records'][key]})
        try:
            with self.assertRaisesRegex(m.Invalid, 'provenance/argv drift'):
                m.validate(self.root)
        finally:
            p.write_text(old)
            rp.write_text(rold)


class Commands(unittest.TestCase):
    def test_success_exit_error_timeout_exception_and_partial(self):
        for outcome in (0, 17, subprocess.TimeoutExpired(['fake'], 3), OSError('no tool')):
            with self.subTest(outcome=outcome), tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp)
                runner = m.Runner(out)
                def fake(argv, **kwargs):
                    kwargs['stdout'].write(b'partial\n')
                    if isinstance(outcome, Exception):
                        raise outcome
                    return subprocess.CompletedProcess(argv, outcome)
                with patch.object(m.subprocess, 'run', side_effect=fake):
                    if outcome == 0:
                        runner.command(['fake', '--show-symbol-table'], 'dump')
                    else:
                        with self.assertRaises(Exception):
                            runner.command(['fake', '--show-symbol-table'], 'dump')
                event = m.read(next((out / 'commands').glob('*.json')))
                self.assertEqual(event['exit'], outcome if isinstance(outcome, int) else None)
                self.assertEqual((out / 'dump.txt').read_bytes(), b'partial\n')
                self.assertNotEqual(event['state'], 'STARTED')

    def test_short_names_and_no_normalization_in_diff(self):
        key = 'final/' + 'long::name' * 1000
        self.assertEqual(len(m.ident(key)), 32)
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            path = m.diff(out, key, 'A1-B1', 'symbol-table', 'x\r\n', 'x\n')
            self.assertLess(len(Path(path).name), 100)
            self.assertGreater((out / path).stat().st_size, 0)

    def test_total_deadline_records_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            runner = m.Runner(out, seconds=-1)
            with patch.object(m.subprocess, 'run') as call:
                with self.assertRaises(m.Invalid):
                    runner.command(['fake'], 'dump')
                call.assert_not_called()
            self.assertEqual(m.read(next((out / 'commands').glob('*.json')))['state'], 'EXCEPTION')


class Orchestration(unittest.TestCase):
    def run_fixture(self, *, aa_drift=False, bad_repeat=False, bad_control=False, bad_tool=False):
        import test_analysis as fixture
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root, out = base / 'input', base / 'out'
            out.mkdir()
            keys = ('final/control/array_typed_copy', 'final/perf/one', 'final/perf/two', 'linked/perf/source')
            arms = {a: {'records': {k: {'kind': k.split('/')[0], 'path': f'files/{i}', 'sha256': 'a' * 64}
                                    for i, k in enumerate(keys)},
                        'tools': {'goto-instrument': 'a' * 64}} for a in m.ARMS}
            for a in m.ARMS:
                save(root / a / 'index.json', {'synthetic': True})
                save(root / a / 'tools.json', {'synthetic': True})
            env = {'GITHUB_ACTIONS': 'true', 'RUNNER_OS': 'Linux', 'GITHUB_RUN_ATTEMPT': '1',
                   'GITHUB_WORKSPACE': str(base / 'checkout')}
            calls = []
            def command(runner, argv, stem, timeout=60):
                argv = list(map(str, argv))
                calls.append(argv)
                p = out / (stem + '.txt')
                p.parent.mkdir(parents=True, exist_ok=True)
                text = ''
                if stem == 'setup/download':
                    (out / m.DEB).write_bytes(b'synthetic package')
                elif stem == 'setup/version':
                    text = '6.11.0\n'
                elif '--show-' in argv[1]:
                    mode = argv[1].removeprefix('--show-')
                    arm = Path(argv[2]).parts[-3]
                    number = int(Path(argv[2]).name)
                    if mode == 'symbol-table':
                        changed = number == 0 and arm == 'B1' and not bad_control
                        text = fixture.symbol_dump(fixture.NEW if changed else fixture.OLD)
                        if aa_drift and number == 1 and arm == 'A2':
                            text += 'unexpected A/A drift\n'
                    else:
                        text = 'function body\n'
                    if bad_repeat and stem.endswith('.repeat'):
                        text += 'nondeterministic\n'
                p.write_bytes(text.encode())
                return p
            result = {}
            real_sha = m.sha256
            def hashed(path):
                return ('f' if bad_tool else 'a') * 64 if str(path) == '/fake/goto-instrument' else real_sha(path)
            with patch.dict(m.os.environ, env), patch.object(m, 'validate', return_value=arms), \
                 patch.object(m.Runner, 'command', command), patch.object(m.shutil, 'which', return_value='/fake/goto-instrument'), \
                 patch.object(m, 'sha256', side_effect=hashed):
                if bad_repeat or bad_tool:
                    with self.assertRaises(m.Invalid):
                        m.execute(root, out, result)
                else:
                    m.execute(root, out, result)
            if not bad_tool:
                self.assertTrue(any('--show-symbol-table' in c for c in calls))
            else:
                self.assertFalse(any('--show-symbol-table' in c for c in calls))
            return result, calls

    def test_stable_equal_perf_with_sensitive_control_and_three_repeat_models(self):
        result, calls = self.run_fixture()
        self.assertEqual(result['status'], 'MODELS_EQUAL')
        self.assertEqual(len(result['determinism']), 6)
        self.assertEqual(len({r['key'] for r in result['determinism']}), 3)
        self.assertEqual(len(result['B_DIFF']), 1)
        self.assertEqual(len(result['B_PAIR_DIFFS']), 2)
        self.assertEqual(sum(c[1] == '--show-goto-functions' for c in calls if len(c) > 1), 15)

    def test_aa_drift_keeps_ab_tentative(self):
        result, _ = self.run_fixture(aa_drift=True)
        self.assertEqual(result['status'], 'INCONCLUSIVE_AA')
        self.assertEqual(len(result['AA_DIFF']), 1)
        self.assertTrue(any(not r['aa_equal'] for r in result['B_PAIR_DIFFS']))
        self.assertFalse(any(r['key'] == 'final/perf/one' for r in result['B_DIFF']))

    def test_invalid_control(self):
        result, _ = self.run_fixture(bad_control=True)
        self.assertEqual((result['status'], result['error']), ('INVALID', 'INVALID_CONTROL'))

    def test_repeat_failure_and_tool_mismatch_stop(self):
        self.run_fixture(bad_repeat=True)
        self.run_fixture(bad_tool=True)


if __name__ == '__main__':
    unittest.main()
