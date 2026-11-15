"""Synthetic r2 capture/classification; no network, tool install or backend."""
import copy
import importlib.util
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parent
KANI = Path('/root/kani-b3-t1/.github/b3-t1b')
sys.path.insert(0, str(KANI))
spec = importlib.util.spec_from_file_location('runner_r2', KANI/'run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
offline = runpy.run_path(str(BASE/'offline.py'))
r2 = runpy.run_path(str(BASE/'offline_r2.py'))['run_r2']
fixtures = runpy.run_path(str(BASE/'test_offline.py'))
sha = offline['sha']


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def function_body(value=1):
    return (m.extract_functions.__globals__['SEPARATOR'] + b'f /* f */\n'
            + b'        // 0 no location\n        ASSIGN x := ' + str(value).encode()
            + b'\n        // 1 no location\n        END_FUNCTION\n\n')


class Framing(unittest.TestCase):
    def test_exact_prefix_only_and_content_preserved(self):
        banner = b"Reading GOTO program from '/x/A1/files/f'\n"
        body = function_body().replace(b'ASSIGN x := 1', b'ASSIGN x := "Reading GOTO program from other"')
        actual, status, counts = m.extract_functions(banner+body, '/x/A1/files/f')
        self.assertEqual((actual, status), (body, banner))
        self.assertEqual(counts, {'function_count': 1, 'instruction_count': 2})
        self.assertEqual((BASE/'function_dump_r2.py').read_bytes(), (KANI/'function_dump.py').read_bytes())

    def test_empty_status_only_wrong_path_list_partial_and_duplicates(self):
        banner = b"Reading GOTO program from '/model'\n"
        good = banner + function_body()
        for raw in (b'', banner, good.replace(b'/model', b'/other'),
                    banner+b'f /* f */\n', good.replace(b'END_FUNCTION', b'SKIP'),
                    good+function_body(), b'unknown status\n'+good,
                    good.replace(b'        // 0 no location\n', b'').replace(b'        // 1 no location\n', b'')):
            with self.subTest(raw=raw[:90]), self.assertRaises(ValueError):
                m.extract_functions(raw, '/model')


class Capture(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name)
        cls.root, cls.out = cls.base/'input', cls.base/'capture'
        cls.out.mkdir()
        cls.keys = [f'{kind}/control/array_typed_copy' for kind in ('final','linked','symtab')]
        cls.keys += [f'{kind}/perf/{n}' for kind in ('final','linked','symtab') for n in range(130)]
        cls.arms = {}
        for arm in m.ARMS:
            records = {key: {'kind':key.split('/')[0], 'path':f'files/{i}', 'sha256':'b'*64}
                       for i,key in enumerate(cls.keys)}
            cls.arms[arm] = {'records':records, 'tools':{'goto-instrument':'a'*64}, 'complete':True}
            save(cls.root/arm/'index.json', cls.arms[arm])
            save(cls.root/arm/'tools.json', {'goto-instrument':{'sha256':'a'*64}})
        cls.calls = []
        def command(runner, argv, stem, timeout=60):
            argv = list(map(str, argv))
            cls.calls.append(argv)
            p = cls.out/(stem+'.txt')
            err = cls.out/(stem+'.stderr.txt')
            p.parent.mkdir(parents=True, exist_ok=True)
            data = b''
            if stem == 'setup/download':
                (cls.out/m.DEB).write_bytes(b'synthetic package')
            elif stem == 'setup/version':
                data = b'6.11.0\n'
            elif argv[1].startswith('--show-'):
                arm = Path(argv[2]).parts[-3]
                key = cls.keys[int(Path(argv[2]).name)]
                if argv[1] == '--show-symbol-table':
                    instance = fixtures['OfflineTests']()
                    data = instance.control_model(arm == 'B1').encode() if '/control/' in key else fixtures['dump'](fixtures['block']('f','void (void)')).encode()
                else:
                    data = ("Reading GOTO program from '"+argv[2]+"'\n").encode()+function_body()
            p.write_bytes(data)
            err.write_bytes(b'')
            save(cls.out/'commands'/f'{len(cls.calls):05d}.json', {'argv':argv, 'exit':0, 'state':'EXIT',
                 'stdout':str(p.relative_to(cls.out)), 'stderr':str(err.relative_to(cls.out))})
            return p
        real_sha = m.sha256
        env = {'GITHUB_ACTIONS':'true', 'RUNNER_OS':'Linux', 'GITHUB_RUN_ATTEMPT':'1',
               'GITHUB_WORKSPACE':str(cls.base/'checkout')}
        cls.result = {'schema':'b3-t1b-r2-capture-v1', 'run_id':'synthetic-r2', 'run_attempt':'1',
                      'source_run':m.RUN_ID, 'source_artifact':m.ARTIFACT,
                      'task_base':'43b065bb9d0fc78cb66aef81584a8241a85f461d',
                      'ci_parent':'1a8faa3b60ee9a19534cdb57315e8887f5666301',
                      'source_ci_sha':'cfa4b0c5296b1f7735b0d4a138d339431dfbf93d', 'ci_sha':'c'*40}
        with patch.dict(m.os.environ, env), patch.object(m, 'validate', return_value=cls.arms), \
             patch.object(m.Runner, 'command', command), patch.object(m.shutil, 'which', return_value='/fake/goto-instrument'), \
             patch.object(m, 'sha256', side_effect=lambda p:'a'*64 if str(p)=='/fake/goto-instrument' else real_sha(p)):
            m.execute(cls.root, cls.out, cls.result)
        cls.original = (cls.out/'RESULT.json').read_bytes()
        cls.index = json.loads((cls.out/'INDEX.json').read_bytes())

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def classify(self):
        return r2(self.out, self.base/'classified', offline)

    def test_capture_and_full_offline(self):
        self.assertEqual(self.result['status'], 'CAPTURE_COMPLETE_OFFLINE_REQUIRED')
        self.assertEqual(self.result['function_dumps'],1179)
        for argv in self.calls:
            if len(argv)>1 and argv[1].startswith('--show-'):
                self.assertEqual(argv[-1], '6' if argv[1]=='--show-goto-functions' else '4')
        result = self.classify()
        self.assertEqual(result['status'],'MODELS_EQUAL')
        self.assertEqual(result['AA_EQUAL'], {'final':131,'linked':131,'symtab':131})
        self.assertEqual(len(result['B_DIFF']),3)
        self.assertTrue(result['control_valid'])
        self.assertEqual((self.out/'RESULT.json').read_bytes(),self.original)

    def test_function_mutation_is_not_normalized_or_given_b_credit(self):
        key='final/perf/99'
        mode=copy.deepcopy(self.index[key]['arms']['A2']['modes']['goto-functions'])
        paths=[self.out/mode[name] for name in ('raw','content')]
        old=[p.read_bytes() for p in paths]
        try:
            for path in paths:
                path.write_bytes(path.read_bytes().replace(b'ASSIGN x := 1',b'ASSIGN x := 2'))
            data=copy.deepcopy(self.index)
            for name,path in zip(('raw','content'),paths):
                data[key]['arms']['A2']['modes']['goto-functions'][name+'_sha256']=sha(path.read_bytes())
            save(self.out/'INDEX.json',data)
            result=self.classify()
            self.assertEqual(result['status'],'INCONCLUSIVE_AA')
            self.assertEqual(result['AA_DIFF'][0]['class'],'FUNCTION_CHANGES')
            self.assertFalse(any(r['key']==key for r in result['B_DIFF']))
        finally:
            for path,value in zip(paths,old):path.write_bytes(value)
            save(self.out/'INDEX.json',self.index)

    def test_partial_missing_null_wrong_type_not_run_and_source_mismatch(self):
        for replacement in ({'status':'NOT_RUN'}, {'stage':'DUMPS'}, {'input_indexes':None},
                            {'tool':[]}, {'source_run':'other'}, {'task_base':'other'},
                            {'ci_parent':'other'}, {'source_ci_sha':'other'}, {'ci_sha':None}):
            try:
                data=copy.deepcopy(self.result);data.update(replacement)
                save(self.out/'RESULT.json',data)
                with self.assertRaises((ValueError,TypeError,KeyError)):
                    self.classify()
                sentinel=json.loads((self.base/'classified/RESULT-OFFLINE-r2.json').read_bytes())
                self.assertEqual(sentinel['status'],'INVALID')
            finally:
                (self.out/'RESULT.json').write_bytes(self.original)
        path=self.out/self.index['final/perf/0']['arms']['A1']['modes']['goto-functions']['raw']
        old=path.read_bytes()
        try:
            path.unlink()
            with self.assertRaises(FileNotFoundError):self.classify()
            path.write_bytes(b'')
            with self.assertRaises(ValueError):self.classify()
        finally:path.write_bytes(old)

    def test_command_failure_timeout_and_wrong_verbosity(self):
        mode=self.index['final/perf/0']['arms']['A1']['modes']['goto-functions']
        path=next(p for p in (self.out/'commands').glob('*.json') if json.loads(p.read_bytes())['stdout']==mode['raw'])
        old=path.read_bytes()
        for update in ({'exit':17}, {'state':'TIMEOUT','exit':None}, {'argv':['fake','--show-goto-functions','/other','--verbosity','4']}):
            try:
                data=json.loads(old);data.update(update);save(path,data)
                with self.assertRaises(ValueError):self.classify()
            finally:path.write_bytes(old)

    def test_controls_reject_off_wrapper_and_body_change(self):
        for key in ('final/control/array_typed_copy',):
            mode=copy.deepcopy(self.index[key]['arms']['B1']['modes']['goto-functions'])
            paths=[self.out/mode[name] for name in ('raw','content')]
            old=[p.read_bytes() for p in paths]
            try:
                data=copy.deepcopy(self.index)
                for name,path in zip(('raw','content'),paths):
                    path.write_bytes(path.read_bytes().replace(b'ASSIGN x := 1',b'ASSIGN x := 2'))
                    data[key]['arms']['B1']['modes']['goto-functions'][name+'_sha256']=sha(path.read_bytes())
                save(self.out/'INDEX.json',data)
                result=self.classify()
                self.assertEqual(result['status'],'INVALID_CONTROL')
            finally:
                for path,value in zip(paths,old):path.write_bytes(value)
                save(self.out/'INDEX.json',self.index)


if __name__=='__main__':unittest.main()
