# c451ed14 source-linked Drop saved replay

This is local classifier/parser replay of **saved Cloud artifacts**, not a new
verification run. The archive identified by SHA-256
`f1fffedddde12c4b62533d9e3e0d65855324cff4614a9f08e18f96215357da3d`
contains Build `c451ed14-505f-49c3-8e88-82664b9aafa3` and its original six
concrete Drop cases under proof/infra source
`3a3a70e7803bc275b381ba4af1133c6cae1d7662`. The
source SHA-256 is `85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`,
Git blob `40939f922bcb6fdc7ee0d30427fa861827043827`, and extracted block
SHA-256 `caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a`.
The saved `extraction.json` SHA-256 is
`aea6987ceb5900faf53d6a2fccab48da48d30cbdbcdea77577ebb25308fcbb0b`.

The corrected classifier at SHA-256
`9f6811321b275ee2824b413f417376bf54398393e29e83840191cc287c0b69f8`
replays the saved stage receipts and obtains:

| Case | Saved replay status | First frontier |
| --- | --- | --- |
| `direct_positive` | `CONDITIONAL_STRONG_PRE_BODY_PASS` | body copy, return and leak, zero verifier errors |
| `direct_first_body_false` | `EXPECTED_REJECTION` | first body statement |
| `canonical_dst_pre` | `INCONCLUSIVE` | maybe-uninitialized singleton-to-`array_` shape, prelude line 256 |
| `canonical_positive` | `INCONCLUSIVE` | root alignment |
| `prototype_false` | `EXPECTED_REJECTION` | canonical prototype entry |
| `first_body_false` | `INCONCLUSIVE` | root alignment before body |

For every row, source, MIR, AST, exporter/decode/refinement stage and
unchanged-source receipt gates are admitted. The body pass is conditional on
the historical strong precondition; it does not prove the one-cell canonical
caller or a compiler-generated callee. The two newly added cases,
`canonical_alignment_probe` and `canonical_dst_shape_probe`, have **NOT_RUN**
status until a fresh Cloud Build under the same validated parent receipt.

Reproduce this replay in the assigned project checkout with the saved archive
unpacked at `/tmp/c8-current-unpacked-c451ed14`; it imports only the pinned
Python admission parsers and reads saved text:

```sh
python3 - <<'PY'
import importlib.util, json, pathlib, sys
root = pathlib.Path('/root/verify-rust-std-merge-origin')
path = root / 'research/challenge-8/cloud-build/origin-layout/concrete-drop-body.py'
spec = importlib.util.spec_from_file_location('drop_replay', path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
base = module._load('drop_saved_parser', root / 'research/challenge-8/merge/overnight/copy-on-drop-prove.py')
saved = pathlib.Path('/tmp/c8-current-unpacked-c451ed14/allprooflogs/cases/insertion-onecell-guard-diagnostic/concrete-drop-body')
rows = json.loads((saved / 'extraction.json').read_text())['cases']
for name in sorted(rows):
    row = rows[name]
    case = saved / 'cases' / name
    old = json.loads((case / 'classification.json').read_text())
    contract = row['ghost_fragments'][1 if row['canonical'] else 0].encode()
    header = contract.split(b'safety_proof {\n', 1)[0]
    result = module._classify(name, case, row, old['parent_execution'], header, base, None)
    assert result['source_gate']['admitted'] and result['mir_gate']['admitted'] and result['ast_gate']['admitted']
    print(name, result['classification'], result['first_frontier'])
PY
```

An isolated saved-text mutation check copied only `proof-ast.ml` and
`decode.out` into a temporary directory. Replacing the unique runtime
`self.src` select at the copy operand's source span with `self.dst` made AST
admission refuse: `copy operand 0 is not the ordered self.src read`. Replacing
the source-located MIR `core::ptr::copy_nonoverlapping` callee with
`core::ptr::copy` made MIR admission refuse: `unrecognized Drop MIR call`.
The baseline files admitted both gates. No compiler, extractor, proof runner
or verifier was run locally.
