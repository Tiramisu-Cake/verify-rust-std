# Slice01 author review notes

Candidate: `d82752c8bc878398e672bffaa631ca6a28430acc`, tree `c7024fb95c9cbb8ca2b1091056b9d5aa9c8cea9b`.
One commit, exact parent existing B1 `6fe484b30043b3696b5f1ccc4bea0e42891ad012`.
TASK @`4fef62ad67`, variant C is the extraction contract. These are author/static notes;
independent worker15 review and all native results remain pending. READY means ready for that review/CI preparation.

The extracted change analyzes selected registration/discarded bodies with their provenance,
uses one root-local active-call stack with latched error and Result propagation, and adds ordinary
scalar/reference storage entry setters without initializing referents or union storage.
The resolver's tcx/checked_body signature and both consumers move together. Error/no-body paths,
the single operand walk/common target flush, upstream checked_body/tail-call/atomic changes and
all22 submitted B1 fixture code/golden pairs are retained. A failed root exports no partial graph;
ordinary instrumentation precedes its explicit Unsupported insertion. Other roots continue.

There are six changed production files. `points_to_graph.rs` has no owner1 delta and remains B1.
Nine ActiveCalls unit bodies and the complete changed delayed instrumentation visitor are exact F.
Four final-source B1 fixture edits change comments only; their code, flags and goldens are unchanged.
There are no new expected integration fixtures or docs on this head, no new non-MU substitute tests,
no scaffolding/future APIs, and no immutable/layout/raw_eq/storage/runtime/closure/F7 feature hunks.

## Extraction seams and map corrections

- The baseline combined `TransformationResult, body::CheckType` import is split into the exact historical
  pre-F7 import and owner1's expanded body import. It would otherwise import CheckType twice.
- The zero-context resolver hunk also removes two baseline helpers. The resolver signature/body is
  replaced at its original position, preserving its existing closing brace and both entire helpers.
  An independent static comparison checks that this file differs from B1 only in the resolver and call.
- Ordinary writes keep the existing cache `entry(...).and_modify(...)`; the new failed-root loop uses
  the real historical cache `insert(... TransformationResult(...))` from PRE-F7.json. F7 API is absent.
- The stage0 F7 failed-root writer coordinate was off by one: F212 is `replace_delayed_body`, F213 is
  `modified = true`. Canonical parts, PRE-F7.json and the generator now assign212 to7 and213 to1.
  The F source and its hunk hashes are unchanged. This corrects bookkeeping, not feature ownership.
- Accepted variant C moves exact F420–424 ordinary-union constant branch6→4. This change updates the
  canonical source map/dependencies only; it imports none of those lines into head1. E1 production
  residual can be zero. Recognition helpers2/projected-raw guards4 stay as accepted.

All full hunk/part identities are in SOURCE-PARTS.json and the updated canonical source map.
The two syntax seams preserve baseline material; the only temporary semantic API adaptation is the
explicitly authorized pre-F7 cache writer form, reversed in7. There is no structural F7 isolation credit.

## Qualification and remaining obligations

`qualification_kind=NO_REGRESSION`, `qualification_status=NOT_RUN`,
`integration_status=PENDING`, `integration_heads=[4,5]`.
ActiveCalls9 is generic key/stack testing, not reached MIR/entry-setter evidence.
Stock FunctionContracts/function-contract tests keep their original flags and cannot supply that evidence.

TEST-MANIFEST.json specifies the complete common Quick plus full FunctionContracts25 and
function-contract138 selectors, retaining existing ignores. The latter replaces the old12-selector
smoke plan. The upstream uninit/delayed-UB manifest also includes the existing verify_std_cmd and
two std-checks/std goldens that use uninit settings outside the common filters. No native discovery
or test execution is claimed. CI-REQUEST.md is a prepared exact-head request, not a dispatch.

Seven head4 obligations preserve the final DAG/cycle/root-order and ordinary payload/padding pairs.
Head5 obligations include complete ordinary positive/capture-free, contract-immutable, strong,
mode/root and captured-environment consumers from the oracle map. SLICE.json and
DEFERRED-OBLIGATIONS.json pin every fixture/golden and link immutable owner1 hunk parts.
They require explicit exact-cumulative-head receipts with useful SUCCESS and intended negatives.
No aggregate exit0 or synthetic unit PASS closes them. History of head1 must remain no-regression;
later provenance is integration-tested on head4/5. Known accepted recursive cycle boundaries stay intact.

Worker15's research area is untouched. ORACLE-DELTA.json records its required map/Quick refresh
under the accepted decision and the corrected F7 coordinate. Stage0 dependency findings were static,
not failed runtime observations; the user has separately authorized this stage1 extraction.

## Static validation and limits

`validate_slice.py` checks deterministic owner-only extraction, lexical delimiter balance (not Rust
parsing), the independent exact resolver delta, exact F unit/visitor bodies, real pre-F7 writer forms,
all22 B1 controls, unchanged protected paths, and `git diff --check`. Its zero-context source patch
reconstructs every changed blob in memory. Temporary alternate indexes apply source.patch from B1
to the candidate tree and residual-to-F.patch from the candidate to the exact F tree. These establish
patch endpoint integrity; they are not a seven-slice recomposition or compiler/proof qualification.

NOT_RUN: Rust parsing/typecheck, rustfmt, build, clippy, native units/compiletest/verifier, CI, push,
independent review, logical full-stack recomposition. Cloud spend0, no dispatch/publication.
Any new ordinary regression, false SUCCESS, extra Unsupported or lost check remains STOP.
