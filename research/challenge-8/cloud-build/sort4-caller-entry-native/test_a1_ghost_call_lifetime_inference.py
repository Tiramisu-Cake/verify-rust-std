"""Static and synthetic checks for the R13 Rust call lifetime overlay.

These checks deliberately do not compile or execute VeriFast/OCaml.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path('/root/verify-rust-std-select-night')
VERIFAST = pathlib.Path('/root/verifast')
IDENTITY = REPO / 'research/challenge-8/cloud-build/sort4-native-c1-bound/native-dead-code-identity-diagnostic.patch'
FOCUS = REPO / 'research/challenge-8/cloud-build/sort4-native-c1-bound/native-rust-focus-dead-code-scope.patch'
PATCH = HERE / 'ghost-call-lifetime-inference-r13.patch'
MANIFEST = HERE / 'GHOST-CALL-LIFETIME-INFERENCE-R13-MANIFEST.json'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_after_overlay() -> bytes:
    manifest = json.loads(MANIFEST.read_text())
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        for rel in ('src/verify_expr.ml', 'src/vfconsole/vfconsole.ml'):
            out = root / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(subprocess.check_output([
                'git', '-C', str(VERIFAST), 'show', f"{manifest['tool_head']}:{rel}"
            ]))
        for patch in (IDENTITY, FOCUS):
            subprocess.run(['patch', '-p1', '-i', str(patch)], cwd=root,
                           check=True, capture_output=True)
        base = root / manifest['source']
        assert sha(base.read_bytes()) == manifest['base_sha256']
        subprocess.run(['patch', '-p1', '-i', str(PATCH)], cwd=root,
                       check=True, capture_output=True)
        result = base.read_bytes()
        assert sha(result) == manifest['result_sha256']
        return result


# Small immutable type-tree model for the accepted/rejected shape cases.
# ('ref', lifetime, mutable, pointee), ('ind', name, args), ('scalar', name),
# ('cell', identity), ('life', name), ('static',).
def preflight(formal, actual, proposals):
    if formal[0] == 'cell':
        if actual[0] in ('life', 'static'):
            previous = proposals.get(formal[1])
            if previous is not None:
                return previous == actual
            proposals[formal[1]] = actual
            return True
        return formal == actual
    if formal[0] == actual[0] == 'ref':
        return (formal[2] == actual[2]
                and preflight(formal[1], actual[1], proposals)
                and preflight(formal[3], actual[3], proposals))
    if formal[0] == actual[0] == 'ind':
        return (formal[1] == actual[1] and len(formal[2]) == len(actual[2])
                and all(preflight(f, a, proposals) for f, a in zip(formal[2], actual[2])))
    return formal == actual


class OverlayTests(unittest.TestCase):
    def test_manifest_and_exact_patch_replay(self):
        manifest = json.loads(MANIFEST.read_text())
        self.assertEqual(manifest['source'], 'src/verify_expr.ml')
        self.assertEqual(manifest['base_sha256'], '2d17c36005d6727cb5ff6d831bf905f513065bb591d5d9768ee70778872a6d20')
        self.assertEqual(manifest['patch_sha256'], sha(PATCH.read_bytes()))
        self.assertFalse(manifest['new_axiom_or_assumed_lemma'])
        self.assertEqual(sha(source_after_overlay()), manifest['result_sha256'])
        result = source_after_overlay()
        self.assertIn(b'is_lifetime (unfold_inferred_type tp) || unify tp StaticLifetime', result)
        self.assertIn(b'if is_lifetime (unfold_inferred_type tp) then', result)

    def test_only_unresolved_lifetime_leaf_is_proposed(self):
        formal = ('ind', 'Option', [('ref', ('cell', 'life-x'), 'shared', ('scalar', 'T'))])
        actual = ('ind', 'Option', [('ref', ('life', "'caller"), 'shared', ('scalar', 'T'))])
        proposals = {}
        self.assertTrue(preflight(formal, actual, proposals))
        self.assertEqual(proposals, {'life-x': ('life', "'caller")})

    def test_fixed_lifetime_and_static_are_rigid(self):
        self.assertTrue(preflight(('ref', ('life', "'fixed"), 'shared', ('scalar', 'T')),
                                  ('ref', ('life', "'fixed"), 'shared', ('scalar', 'T')), {}))
        proposals = {}
        self.assertTrue(preflight(('ref', ('cell', 'life-x'), 'shared', ('scalar', 'T')),
                                  ('ref', ('static',), 'shared', ('scalar', 'T')), proposals))
        self.assertEqual(proposals, {'life-x': ('static',)})

    def test_nominal_mutability_and_non_lifetime_mismatches_reject(self):
        formal = ('ind', 'Option', [('ref', ('cell', 'life-x'), 'shared', ('scalar', 'T'))])
        for actual in (
            ('ind', 'Result', [('ref', ('life', "'caller"), 'shared', ('scalar', 'T'))]),
            ('ind', 'Option', [('ref', ('life', "'caller"), 'mutable', ('scalar', 'T'))]),
            ('ind', 'Option', [('ref', ('life', "'caller"), 'shared', ('scalar', 'U'))]),
        ):
            proposals = {}
            self.assertFalse(preflight(formal, actual, proposals))

    def test_repeated_lifetime_cell_conflict_rejects_whole_preflight(self):
        formal = ('ind', 'Pair', [
            ('ref', ('cell', 'same-cell'), 'shared', ('scalar', 'T')),
            ('ref', ('cell', 'same-cell'), 'shared', ('scalar', 'T')),
        ])
        actual = ('ind', 'Pair', [
            ('ref', ('life', "'left"), 'shared', ('scalar', 'T')),
            ('ref', ('life', "'right"), 'shared', ('scalar', 'T')),
        ])
        proposals = {}
        self.assertFalse(preflight(formal, actual, proposals))
        # Production code applies proposals only after the full preflight returns true.
        self.assertEqual(proposals, {'same-cell': ('life', "'left")})

    def test_source_guards_and_apply_after_full_preflight(self):
        source = source_after_overlay().decode()
        start = source.index('let infer_rust_call_lifetimes_from_typed_variables')
        end = source.index('let ys: string list', start)
        block = source[start:end]
        self.assertIn('dialect <> Some Rust || not pure', block)
        self.assertIn('List.assoc_opt name tenv', block)
        self.assertIn('if preflight pats ps then', block)
        self.assertIn('unify_strict cell actual', block)
        self.assertNotIn('unify formal', block)
        self.assertNotIn('unify_strict formal', block)
        self.assertIn('name <> "\'_"', block)


if __name__ == '__main__':
    unittest.main()
