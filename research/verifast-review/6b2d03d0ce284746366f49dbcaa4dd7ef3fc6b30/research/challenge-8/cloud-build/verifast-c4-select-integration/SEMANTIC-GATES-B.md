# Composition regression gates B — design for independent review

2026-10-10. This is a preimplementation design only. No translator, verifier,
fixture, runner, or toolchain was changed or run. The target is the same pinned
composition artifact and exact C4 source/MIR/pre-AST described in
`COMPOSITION-SEMANTIC-CARD.md`; all test hooks are default-off and yield no
proof credit.

## Same-post thread and owner sensitivity controls

The composition positive already retains the source contract verbatim:
normal post at `verified/lib.rs:315-320` and unwind post at `:322-327`. The
first-select transformer adds a result relation at source line 487. Add two
mutually exclusive test controls immediately after that relation in the
generated normal-path AST. They change only verifier ghost state; they do not
change the C4 contract, selector export, call target, normal/unwind CFG, or
runtime source.

For `leak-thread-token`, insert
`Ast.Leak(loc, Ast.CallExpr(loc, "thread_token", [], [],
  [Ast.LitPat (Ast.Var (loc, "t"))], Ast.Static))`.
The source contract's input `thread_token(?t)` binds `t`, and the original
normal/unwind posts each require `thread_token(t)`. The test must show the
post-call leak consumes that exact chunk and the unchanged normal post fails
at its thread-token clause. The selector and C1–C4 unwind paths remain intact.

There is no named `four_owned_cells` predicate in the pinned C4 fixture. The
actual joined four-cell frame produced by `join_four_owned_cells` /
`join_selected_four` is exactly `v_base[..4] |-> ?xs &*&
foreach(xs, own::<T>(t))`, as in the source post. For
`leak-current-four-cell-frame`, insert one `Ast.Leak` consuming that exact
separating conjunction, using a fresh assertion binder for `xs`:

```ocaml
let xs = Ast.VarPat (loc, "#c4_select_frame_xs") in
let cells = Ast.PointsTo (loc,
  Ast.ReadArray (loc, Ast.Var (loc, "v_base"),
    Ast.SliceExpr (loc, None, Some (Ast.LitPat
      (Ast.IntLit (loc, big_int_of_string "4", true, false, NoLSuffix))))),
  Ast.RegularPointsTo, xs) in
let own = Ast.CallExpr (loc, "own",
  [Ast.IdentTypeExpr (loc, None, "T")], [],
  [Ast.LitPat (Ast.Var (loc, "t"))], Ast.Static) in
let each = Ast.CallExpr (loc, "foreach", [], [],
  [Ast.LitPat (Ast.Var (loc, "#c4_select_frame_xs")); Ast.LitPat own],
  Ast.Static) in
Ast.Leak (loc, Ast.Sep (loc, cells, each))
```

The exact constructor inventory is from `src/frontend/ast.ml` (`Leak`,
`PointsTo`, `ReadArray`, `SliceExpr`, `CallExpr`, `Sep`) and the saved C4 AST
for `v_base[..4]` and `foreach(source_after, own::<T>(t))`. This deliberately
leaks both the four cell contents and their `T` owners after the real call;
the untouched normal post must then fail at its original array/foreach clause.
The test is a sensitivity check for the retained frame, not a model of a
possible source implementation.

Accept each negative only if the exact nine imported definitions verify
before `sort4_stable`, the importer marker/hash and actual source-487 call are
present, the injected `Leak` is consumed at that call location, and the sole
failure is at the unchanged target normal post (`thread_token(t)` for the
token control; the source array/`foreach` clause for the frame control).
Failure at import, an earlier body, Leak's own consumption, C1–C4 unwind, or
unrelated setup is inconclusive. Require a fresh positive on the same profile
with all original posts and no test control. Do not append either hook to the
checked selector AST blob.

## Admission-mutation matrix

Keep `SOURCE` and `CONTRACT` mutations at fixture preparation, before fresh
capture. The runtime-source case changes one executable byte in a disposable
copy while preserving the old expected source digest. The contract-only case
changes one SAFE clause (remove `thread_token(t)` from the copied normal
post), verifies that ghost stripping still equals the pinned original, and
leaves the annotated source digest stale. Each must fail at the driver's
source-certificate preflight with its explicit `source SHA256 differs` marker;
no compiler/extractor/verifier stage or function header is allowed. Record the
mutated and expected digests, and distinguish the contract-only control by
its unchanged ghost-stripped source hash. This tests the pinned-source
admission boundary; it is not a postcondition VC.

For `TYPE`, `MOVE`, and consumer `EDGE`, begin from the already admitted C4
source/MIR and exact pre-AST digest, then inject exactly one in-memory AST
mutation immediately before the first-select shape matcher. Keep the original
AST and selector-export digests in the evidence. The hook must report the
mutation name and old/new node fingerprints, then run the ordinary named
shape check; it may not short-circuit with a generic forced refusal.

* `TYPE`: change only the call's type argument from `*const T` to
  `*const u8`; expect the exact type/DefPath/call-shape refusal before proof.
* `MOVE`: change only operand setup block 173 from `$_173 = a` to
  `$_173 = d` (same pointer type); expect the exact source-operand setup
  refusal before proof.
* `EDGE`: change only the switch's unwinding outcome continuation from the
  source-derived `return unwinding()` to a different target/continuation;
  add an explicit normal/unwind successor matcher and expect its named edge
  refusal before proof. Keep the returning branch, call type, operands, and
  both original posts unchanged.

For all three, require no `Verifying function` header and the corresponding
specific refusal marker. A generic pre-AST hash failure, verifier error,
compile/extraction failure, or a mutated selector AST is inconclusive.

`REACHABLE_UNWIND` is a decoded typed-CFG mutation in the selector unit, not a
post-hoc rejection and not the consumer edge case. After the exact normal and
readonly MIR hashes and source/body hashes are checked, mutate the in-memory
body-7 (`select_unpredictable`) call at source line 194 from
`UnwindAction.Unreachable` to `UnwindAction.Cleanup` targeting its existing
shared cleanup block 38. This turns the actual source call's previously
unreachable cleanup edge into an additional reachable predecessor without
changing source bytes or the existing target block. Then run the unchanged
owner/cleanup CFG admission. Require its exact cleanup-predecessor inventory
refusal before any function header. Record the original and mutated edge
fingerprints; do not rewrite the result into a synthetic rejection marker.
The archived full MIR confirms this call has `unwindAction = unreachable`,
while body 7's real `DropOnPanic` paths use `Cleanup(index=38)` and that block
is marked cleanup. This is the concrete reachable-unwind mutant.

## Outer-F Bool positive locality and closure (owner-approved correction 2026-10-11)

The required cut106 rejection was withdrawn after the read-only semantic review
`a0bd98275be52760dcb30f9a6c8d07ef6d7dcd36`. Keep the exact source, contracts,
`negative_outer_bound_escape` historical name, tool/profile and all semantic
inputs unchanged. That name does not make the example a valid negative.

Expected positive: paired source/MIR/refinement and exact admissions pass; one
FnOnce Output=Bool registration for outer F with tuple `(&'cmp T, &'cmp T)`
immediately precedes the actual FnMut callback103; six service locals are inside
the strict block. Require the actual call verification, normal and unwind scope
closure at106, both recover_pair calls, original post consumption, lifetime-token
consumption, return/leak checks, no errors/dead code and terminal95 statements.
Repeated same-coordinate statement events are not proof of an exact unique
registration event: use the pinned final AST plus contextual call trace.

The pure `outer_bool_auditor.py` audits these observations on saved evidence.
Its replay does not invoke proof, change old summaries or create fresh proof
credit. Historical expected-VC and Cloud FAILURE remain in the immutable D
archive/review. A missing event or incomplete log is INCONCLUSIVE even with exit0.
The Cloud runner uses the same auditor for observation; its changed classifier
has not itself been executed in Cloud.

General metadata escape negative and O23 soundness remain OPEN. The sketch of
an HRTB callback returning a reference is NOT_RUN, outside the exact Bool
matcher. It does not automatically become a requirement to widen this profile.
The distinct live-heap/debt/token negatives retain their intended semantic VCs.

## Implementation boundaries and review checklist

Use one explicit enum for first-select semantic controls and a separate enum
for preparation/shape/CFG admission mutants. Each mode is default-off,
rejects unknown values, is limited to the exact source/body/profile and a fresh
evidence directory, and emits a named stage marker. Every negative row must
store stage exit, exact target header order, exact first diagnostic/refusal,
mutant fingerprint, and raw log hash. Set composition completion false unless
the positive, wrong-result, both Leak controls, all admission cases, reachable
unwind, outer-F Bool positive closure and existing strict owner/debt/token controls
all reach their specified predicates. All controls remain diagnostic-only;
none widens source scope or grants proof credit.

Independent review must specifically confirm the two `Ast.Leak` formulas
resolve to the pinned C4 chunks and fail at the unchanged posts; the exact
line-194 MIR call/block-38 mutation reaches the owner CFG guard; the edge hook
tests compiler-derived successor identity rather than only a spelling; and
the new strict fixture really registers the current outer projection bound.
No implementation or dispatch before that review.

Cloud compile correction (0a21b11d): final unit observation hook is outside
State module scope. Replace invalid State.body_name expression with exact-one
actual MIR body-name count from bodies_cpn, using existing translated def path.
Domain remains only pinned negative_outer_bound_escape source/strict/HRTB
target and unused absolute output; required helper bodies allowed. This changes
no emitted statement/type/contract/kernel/post or default-off production path.
Independent targeted review required before edit; fresh Cloud compile/proof gate.

Final delivery repair, UNRUN: full30 original canonical module pack restored.
Only two hardcoded large tracked files (tool-c4.patch, source-modules.json) are
XZ-compressed in recipe transport. Cloud preflight must bound decompression to
manifest raw_size, reject extra stream bytes, and compare compressed SHA256,
raw SHA256, exact proof HEAD tree Git blob and mode100644 before materialization
and existing preflight. All original source/patch/module bytes stay unchanged.
No coordinator/protocol limit or semantic rule change, no new Cloud dispatch.
