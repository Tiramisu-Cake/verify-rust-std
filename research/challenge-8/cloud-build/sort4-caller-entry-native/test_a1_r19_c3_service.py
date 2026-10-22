"""Synthetic R19 c3 routing and static constructor checks; no tools, no Cloud."""
from pathlib import Path
_r17 = Path(__file__).with_name('test_a1_r17_body_service.py')
exec(compile(_r17.read_text(), str(_r17), 'exec'))

import importlib.util as _ilu
import sys
from types import SimpleNamespace
from unittest.mock import patch

_ROOT = Path(__file__).resolve().parents[4]


def _load(path, name):
    spec = _ilu.spec_from_file_location(name, path)
    module = _ilu.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class R19IndexedCountRoute(unittest.TestCase):
    def make_case(self, **delta):
        case = R17IndexedCallbackControls().make_case()
        meta = dict(case[3], actual_indexed_calls=3, c3_comparator_line=15)
        meta.update(delta)
        return *case[:3], meta

    def run_route(self, case):
        c4 = FakeC4(support=False)
        env = {'SORT4_ACTUAL_BODY_INDEXED_CALLS': 'ambient'}
        with tempfile.TemporaryDirectory() as temp:
            row = BODY.run_case(None, c4, Path('/synthetic/tool'), env, Path(temp),
                case, FakeGates(), FakeGrammar({}), {'tool_hashes': {}})
        self.assertEqual(env['SORT4_ACTUAL_BODY_INDEXED_CALLS'], 'ambient')
        self.assertFalse(row['proof_credit'])
        return c4

    def test_c3_route_sets_explicit_count_and_c2_route_clears_it(self):
        c4 = self.run_route(self.make_case())
        self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_INDEXED_CALLS'], '3')
        self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_CALL_LINES'], '7,11,15,19,23')
        c4 = self.run_route(R17IndexedCallbackControls().make_case())
        self.assertNotIn('SORT4_ACTUAL_BODY_INDEXED_CALLS', c4.support_env)
        self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_C2_RECOVERY'], '1')

    def test_indexed_count_off_control_removes_only_the_count(self):
        c4 = self.run_route(self.make_case(frontend_control='indexed-count-off',
                                           required_lemmas=[]))
        self.assertNotIn('SORT4_ACTUAL_BODY_INDEXED_CALLS', c4.support_env)
        self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_C2_RECOVERY'], '1')
        self.assertEqual(c4.support_env['SORT4_ACTUAL_BODY_C1_RECOVERY'], '1')

    def test_bad_count_or_c3_site_refuses_before_stages(self):
        for delta in ({'actual_indexed_calls': 4}, {'actual_indexed_calls': '3'},
                      {'actual_indexed_calls': 1}, {'c3_comparator_line': 16},
                      {'c3_comparator_line': None}, {'actual_c2_recovery': False},
                      {'actual_indexed_calls': 2, 'frontend_control': 'indexed-count-off'}):
            c4 = FakeC4()
            with self.subTest(delta=delta), tempfile.TemporaryDirectory() as temp:
                with self.assertRaises(RuntimeError):
                    BODY.run_case(None, c4, Path('/synthetic/tool'), {}, Path(temp),
                        self.make_case(**delta), FakeGates(), FakeGrammar({}),
                        {'tool_hashes': {}})
                self.assertEqual(c4.stage_calls, 0)

    def test_refresh_sets_c3_site_only_for_c3(self):
        text = b'\n'.join(b'let c' + str(i).encode() + b' = is_less(fake);' for i in range(1, 6)) + b'\n'
        routed = BODY.refresh_callback_coordinates(
            ('fake', text, text, {'actual_c1_recovery': True, 'actual_indexed_calls': 3}))
        self.assertEqual(routed[3]['c3_comparator_line'], 3)
        routed = BODY.refresh_callback_coordinates(('fake', text, text, {'actual_c1_recovery': True}))
        self.assertNotIn('c3_comparator_line', routed[3])


class R19StaticConstructor(unittest.TestCase):
    """Pure source transformation on the pinned std source; no compiler/verifier."""

    @classmethod
    def setUpClass(cls):
        here = Path(__file__).resolve().parent
        cls.ghost = _load(_ROOT / 'research/challenge-8/cloud-build/sort4-native-c1-bound/ghost-strip.py', 'r19_ghost')
        capture = _load(_ROOT / 'research/challenge-8/overnight-sort4/capture.py', 'r19_capture')
        c1 = _load(here / 'a1-actual-body-c1.py', 'r19_c1')
        cls.c2 = _load(here / 'a1-actual-body-c2.py', 'r19_c2')
        cls.four = (here / 'a1-actual-recover-four.rs').read_bytes()
        source = (_ROOT / BODY.SOURCE).read_bytes()
        cls.args = (source, cls.ghost, capture, (here / 'a1-actual-recover-pair.rs').read_bytes(),
                    cls.four, c1, BODY.construct_actual, BODY.lemma_metadata)
        cls.v3, cls.o3, cls.m3 = cls.c2.construct_c3(*cls.args)

    def test_c3_layer_is_ghost_only_and_exact(self):
        v2, o2, _ = self.c2.construct(*self.args)
        self.assertEqual(self.o3, o2)
        self.assertEqual(self.ghost.strip_ghost(self.v3), self.o3)
        self.assertEqual(v2.count(self.c2.C3_CALL), 1)
        self.assertEqual(self.v3.count(self.c2.C3_CALL), 0)
        self.assertEqual(self.v3.count(self.c2.MARKER3), 1)
        self.assertEqual(self.v3.count(self.c2.MARKER), 1)
        self.assertEqual(self.v3.count(self.c2.C3_SHARES), 1)
        self.assertEqual(self.v3.count(b'__vf_callback_unwind_'), 3)
        self.assertEqual(self.v3.count(b'__vf_callback_scope3();'), 1)
        self.assertEqual(self.v3.count(self.c2.C3_HEADER_LIFETIMES), 1)
        self.assertLess(self.v3.index(self.c2.NORMAL), self.v3.index(self.c2.C3_SETUP))
        self.assertLess(self.v3.index(self.c2.MARKER3), self.v3.index(self.c2.C3_TYPED_CALL))
        self.assertEqual(self.m3['actual_indexed_calls'], 3)
        self.assertFalse(self.m3['proof_credit'])
        routed = BODY.refresh_callback_coordinates(('actual-sort4', self.v3, self.o3, self.m3))
        self.assertEqual(routed[3]['c3_comparator_line'], routed[3]['callback_call_lines'][2])

    def test_eight_c3_controls_preserve_runtime_and_differ(self):
        rows = self.c2.resource_controls_c3(self.v3, self.o3, self.ghost, self.four,
                                            self.m3, BODY.lemma_metadata)
        self.assertEqual([r[0] for r in rows], [
            'c3-missing-unselected-share-negative', 'c3-missing-unrelated-end-token-negative',
            'c3-wrong-ordered-ref-pair-negative', 'c3-wrong-ref-resource-negative',
            'c3-wrong-marker-index-negative', 'c3-missing-fourth-debt-token-negative',
            'c3-displaced-marker-negative', 'c3-index-overflow-marker-negative'])
        self.assertEqual(len({r[1] for r in rows}), 8)
        for name, candidate, original, meta in rows:
            self.assertNotEqual(candidate, self.v3, name)
            self.assertEqual(self.ghost.strip_ghost(candidate), self.o3, name)
            self.assertFalse(meta['proof_credit'])
        overflow = dict((r[0], r[1]) for r in rows)['c3-index-overflow-marker-negative']
        self.assertEqual(overflow.count(b'__vf_callback_unwind_'), 4)

    def test_c3_refuses_without_exact_c2_input(self):
        with self.assertRaises(RuntimeError):
            self.c2._layer_c3(self.v3, self.o3, self.m3, self.ghost, BODY.lemma_metadata)
        with self.assertRaises(RuntimeError):
            self.c2._layer_c3(self.v3, self.o3, dict(self.m3, actual_c2_recovery=False),
                              self.ghost, BODY.lemma_metadata)
        with self.assertRaises(RuntimeError):
            self.c2.resource_controls_c3(self.v3, self.o3, self.ghost, self.four,
                                         dict(self.m3, actual_indexed_calls=2), BODY.lemma_metadata)


class R19RoutedProfileSelection(unittest.TestCase):
    """The R17 routing key selects exactly one allowlisted profile by SHA."""

    def setUp(self):
        here = Path(__file__).resolve().parent
        self.runner = _load(here / 'a1-runner-r17.py', 'r19_routed_runner')
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.dir = self.root / 'research/challenge-8/cloud-build/sort4-caller-entry-native'
        self.dir.mkdir(parents=True)
        for name in ('A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json',
                     'A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json'):
            (self.dir / name).write_bytes((here / name).read_bytes())
        (self.dir / 'a1-actual-body-r17.py').write_bytes(b'# synthetic, unpinned\n')

    def tearDown(self):
        self.temp.cleanup()

    def run_with(self, digest):
        args = SimpleNamespace(proof_root=self.root)
        with patch.dict('os.environ', {'SORT4_A1_PROFILE_SHA256': digest}):
            return self.runner.run(args, c4=None, audit=None, driver=None,
                                   manifest=None, ghost=None)

    def test_r19_and_r17_bytes_select_their_own_profile(self):
        for name in ('A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json',
                     'A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json'):
            digest = sha((self.dir / name).read_bytes())
            # Selection passes; the next gate refuses the synthetic body bytes.
            with self.subTest(name=name), \
                    self.assertRaisesRegex(RuntimeError, 'actual body implementation pin differs'):
                self.run_with(digest)

    def test_unknown_missing_or_ambiguous_profile_refuses(self):
        r19 = self.dir / 'A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json'
        for digest in ('0' * 64, ''):
            with self.subTest(digest=digest), \
                    self.assertRaisesRegex(RuntimeError, 'runner profile pin differs'):
                self.run_with(digest)
        digest = sha(r19.read_bytes())
        (self.dir / 'A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json').write_bytes(r19.read_bytes())
        with self.assertRaisesRegex(RuntimeError, 'runner profile pin differs'):
            self.run_with(digest)
        r19.unlink()
        (self.dir / 'A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json').unlink()
        with self.assertRaisesRegex(RuntimeError, 'runner profile pin differs'):
            self.run_with(digest)

    def test_all_four_adapters_share_the_same_allowlist(self):
        here = Path(__file__).resolve().parent
        for name in ('a1-entry-r17.py', 'a1-runner-r17.py', 'a1-actual-body-r17.py', 'a1-tool-r17.py'):
            text = (here / name).read_text()
            self.assertIn('A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json', text, name)
            self.assertIn('A1-ACTUAL-C2-R17-PROFILE-2026-10-21.json', text, name)
            self.assertIn('SORT4_A1_PROFILE_SHA256', text, name)


if __name__ == '__main__':
    unittest.main()
