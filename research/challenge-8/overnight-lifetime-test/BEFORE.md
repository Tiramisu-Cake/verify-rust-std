# TEST-only strict-cut metadata controls: design before implementation

## Problem and positive baseline

The proposed 26.10 strict lifetime cut freezes inferred type references at
block entry and rejects unresolved inference, scoped type escape in an outer
variable, and live scoped type arguments (including nested bounds) at an
early block exit. O22 proved four local CUT examples, but none reached these
specific rejection branches. A source ghost `_` is not a usable inference
fixture: this Rust ghost parser maps it to a void-pointer manifest type,
whereas `InferredType` is introduced by translator/typechecking paths.
Declaring an outer variable *after* `let_lft 'cmp` would not test escape from
the outer environment. A new source-only negative is therefore not yet
known to reach the checks without an unrelated parse/type failure.

Use one dedicated lawful generic Rust fixture with an outer ghost integer
`probe`, `begin_lifetime`, exactly one `let_lft 'cmp`, a generic ghost
`live<T>()` chunk closed before the cut and opened after it, then the full
`end_lifetime`. The unmodified source must have exact ghost-strip identity,
complete NORMAL/readonly MIR and refinement, and full proof/leak exit 0 on
the already reviewed CUT console. This source has no runtime memory access
or user-defined executable callee. Pin its full bytes, line/column,
selected DefPath/body hashes, and positive graph before any test mutation.

## Test-only semantics and trust boundary

Build a *second* disposable console by applying a separate TEST patch after
the unchanged CUT patch. Its only production-file edit is a narrowly gated
branch in `src/verifast.ml` for the dedicated fixture's single strict block.
The branch requires a test environment variable naming one variant, the
exact `verified/lib.rs` source location of the block, and local lifetime
name `'cmp`; the hosted harness independently pins full fixture SHA-256 and
unmodified exporter/schema/refiner/spec hashes. All test variants leave
predicate symbol, coefficient, heap terms, chunk count, memory permissions,
target contracts, proof assertions, and CUT rejection code unchanged. They
alter **only type metadata** of an existing outer ghost variable or existing
`live<T>()` chunk before the already present strict check. The variant
cannot run in the production CUT console. The TEST console must have a
different source diff and binary hash, never populate production caches,
and must never verify actual helper/sort4 or be described as an accepted
proof profile. Results show that the checker rejects constructed bad states;
they do not establish that a real Rust source can construct those states.

## Intended variants and exact first obligations

1. `entry_unresolved`: replace the *type metadata* of the existing unused
   outer `probe` in the verifier environment with a fresh
   `InferredType(_, ref Unconstrained)` immediately before the strict block
   takes its entry snapshot. Its first error must be
   `Strict lifetime binding has unresolved inference in entry outer type`
   at the strict block, before executing its body. A missing `probe`, wrong
   source location or any parse/export failure is inconclusive.
2. `exit_unresolved`: give `probe` an inference alias initially resolved to
   its actual integer type via `EqConstraint`; the frozen entry copy is an
   ordinary integer type. Just before the first strict continuation, change
   only that alias state to `Unconstrained`. The current exit environment
   must fail `Strict lifetime binding has unresolved inference in exit outer
   type`. This checks that entry and exit are examined separately.
3. `late_local_alias`: use the same initially resolved alias and change only
   its state, after entry freeze and before first strict continuation, to
   `EqConstraint (GhostTypeParam "'cmp")`. The frozen entry copy must remain
   the original integer, while the current exit outer variable fails
   `A lifetime-scoped local type escapes the binding`. This directly probes
   mutable-alias escape; it does not assume such a resolution is emitted by
   the current frontend for actual Rust.
4. `exit_heap_unresolved`: select the sole existing `live<T>()` chunk by its
   exact predicate symbol and one generic argument; replace only that type
   argument with fresh unresolved inference immediately before the strict
   exit heap scan. The first error must be
   `Strict lifetime binding has unresolved inference in exit heap type`.
5. `nested_bound_heap`: on the same selected chunk, replace only its type
   argument with a `BoundedGhostTypeParam` whose *non-outer* test parameter
   has one equality bound ending in `GhostTypeParam "'cmp"`. The count,
   symbol, coefficient and terms are unchanged. The first error must be
   `A lifetime-scoped heap chunk is still live at the binding end` with
   `(bound metadata only)` in the diagnostic. The ordinary outer-`T`
   bound-rebase positive remains a separate CUT-console control.

Every variant must uniquely match its intended existing target before
mutation and fail setup if it does not. The harness records entry/exit
mutation event, exact source/profile hashes, first error and verifier exit;
only the intended one-error, no-leak-suppression rejection counts. Run the
unmodified positive again on the TEST console with the test variable absent
to establish default byte-equivalent behavior. No mutation is applied to the
real exporter, MIR, runtime source, `vf_mir_translator.ml`, `rsspec`, or
refinement checker.

## Review issue before code

The `live<T>()` chunk symbol and the callback order at `continue_outside_scope`
must be pinned from the *hosted lawful positive*; no existing 26.10 trace
currently establishes them. If the fixture fails its own proof or the chunk
is absent at the cut, revise this test plan rather than injecting a new
chunk/right. A test-only hook may need to identify the chunk through its
typed predicate symbol, not a string rendered from the heap. Root review is
required before this distinct test console is implemented or dispatched.

## Lawful source capture prepared for the next CUT checkpoint

`positive.rs` is the exact one-function generic source for this positive
baseline. Its SHA-256 is
`f4f2c6e75f35dc25bf2d8021669624ceb20caa0286417acf86bf28e1d540364d`.
The standalone hosted-only `capture-positive.py` accepts:

```
python3 research/challenge-8/overnight-lifetime-test/capture-positive.py \
  --tool-home "$CUT_TOOL_HOME" \
  --out "$FRESH_TEST_POSITIVE_EVIDENCE" \
  --deadline-epoch "$DEADLINE_EPOCH"
```

`CUT_TOOL_HOME` is the already built isolated CUT console, not a new TEST
overlay. It runs full NORMAL and readonly exports/decodes, refinement and
verbose-2 full verification on the ghost-stripped source pair. The summary
records exact source/tool/graph hashes, target body inventory, proof entry,
error/dead-code lines and all stage codes; full logs and binary/text MIR are
retained. `LAWFUL_TEST_SOURCE_CANDIDATE` requires all stages 0, target-body
inventory, one target proof entry, zero errors and a leak check. It remains
diagnostic until root reviews the complete graph and trace. No TEST injection
code has been written or activated.
