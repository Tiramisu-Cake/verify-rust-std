# Independent review: first-select pointer-value cut

**Verdict: GO for the exact normal-path ghost open described below.** This is
static review of the proposed annotation only. It does not approve a tool or
profile, and it adds no proof credit to Build `1492d638`.

## Reviewed boundary

The review target is the prepared C4 → first actual select composition at proof
HEAD `9ff47c3d26429f431b79ac3fd172f5bee67a1802`, tool HEAD
`09389e2c0a4d6d2ed4e1146df0ad6321832c12cb`, and the existing experimental C1
profile. The saved `composition-positive` log records the full imported
nine-body sequence before `sort4_stable`, the real `select_unpredictable(c3,
c, a)` call at source line 487, and the original-pointer assertion. Its only
reported consumer error is the function-exit leak of
`raw_ptr_own(T_typeid)(t, result27)` at line 502. The saved run is diagnostic
evidence: `proof_credit=false`.

The approved source-level annotation is exactly:

```rust
//@ open raw_ptr_own::<T>()(t, min);
```

Place it on the normal continuation immediately after the selected-pointer
identity assertion, following the actual first select. Keep the assertion and
all existing function posts intact.

## Resource and path reasoning

The pinned `bin/rust/rust_belt/general.rsspec:109` defines
`raw_ptr_own<T>()(t, v)` as `true`; line 153 uses it as the type predicate for
`*T`. The selected `min` has type `*const T`, and the selector contract and its
existing safety proof use this same predicate form for the result. VeriFast's
ordinary `open` syntax is already used for this predicate in the pinned
translator/spec sources. Opening it consumes the returned pointer-value chunk
and exposes only `true`. It creates no `T.own`, cell, slice, borrow, or other
pointee permission. The pinned `copy_nonoverlapping` contract in
`bin/rust/std/lib.rsspec:642` relies on source/destination slice resources;
those resources remain separate from this value predicate.

The annotation follows the selector and therefore executes only on its normal
continuation. It does not edit C1–C4 direct-unwind branches or any selector,
C4, or `sort4_stable` contract. The existing thread token, four CURRENT cell
owners, `F` resources, destination frame, and lifetime obligations remain
available and must still be discharged by the unchanged posts and checks.
This establishes a justified ghost-resource cut for the reported pointer-value
chunk; it does not establish that the remainder of the actual sort4 body or its
full theorem verifies.

## Required gates after the edit

Run a fresh Cloud result on the exact edited proof/tool/profile identities. The
result must retain the producer AST seal and typed location-only certificate,
reverify all nine imported bodies before the consumer, and verify the composed
positive through its original posts, return, leak, dead-code, and lifetime
checks. The already defined six same-post composition controls must still reach
their intended consumer VCs: wrong selected original, false normal post,
omitted C4 normal join, missing C4 unwind close, lost thread token, and lost
CURRENT four-cell frame. Review their raw locations; setup/admission refusals
do not count as semantic negatives.

Also rerun the selector and C4 positive gates and the affected cleanup/unwind
regressions under the same effective profile. Confirm the selector's existing
pointer-value positive and no-pointee-rights negative, and preserve the full
unwind/dead-code/leak checks. In particular, the cut must not make any
CURRENT-owner or pointee-rights negative pass. A clean composition positive
without these gates is insufficient for accepting this edit.

## Scope and assumptions

This review assumes the exact imported producer and source/MIR/type/Move/edge
admission gates from the reviewed run remain unchanged, and that the new open is
inserted only for the first actual select's `min` on its normal path. Do not
generalize the cut to other selectors or functions, close a replacement
predicate, add an ownership bridge, alter posts, or use it to suppress cleanup
or leak checks. The producer, `raw_ptr_own` definition, caller source, C4
contracts, kernel, and all admission controls stay fixed.

This is a scoped semantic review of a ghost annotation, not independent review
of a resulting implementation or fresh run. The exact post-edit diff and Cloud
evidence still require their normal review before any profile or consumer
acceptance.

## Post-implementation static review — tool commit `2e95eec0`

**Verdict: GO for the reviewed translator insertion; fresh Cloud validation is
mandatory.** I reviewed the translator hunk from
`09389e2c0a4d6d2ed4e1146df0ad6321832c12cb` to
`2e95eec0c0a08c071f896fd9d00a606f572d5352`. At
`src/rust_frontend/vf_mir_translator/vf_mir_translator.ml:8838`, it constructs
the expected `Ast.PureStmt` wrapping `Ast.Open` for `raw_ptr_own<T>()(t,min)`.
The insertion is in the exact already-admitted source-line-487 first-select
case, after `result_assertion` and before the existing optional leak controls.
The assertion is therefore still checked before the cut, and the thread-token
and CURRENT-frame leak controls still execute after it.

The normal wrapper contains this transformed first-select sequence. The
selector's unwind arm returns from its switch, so it cannot fall through to the
open; the separately retained C1–C4 unwind joins and posts are untouched. The
translator's existing edge walk accepts `Open` as a statement, and this hunk
does not change the imported producer, call admission, predicate definition,
or any postcondition. The reviewed translator diff is limited to this
insertion. Commit `2e95eec0` also changes
`src/frontend/ocaml_expr_of_ast.ml`; that separate formatter change was outside
this review and was assigned to another independent reviewer.

No compiler, verifier, extraction, or Cloud run was performed. This verdict
approves only the exact translator edit for a fresh Cloud run. The required
selector/C4 positives, composed positive, six same-post semantic controls,
producer certificate and imported-body order, and cleanup/unwind/leak and
no-pointee-rights regressions remain mandatory. Build `1492d638` remains
pre-edit diagnostic evidence and cannot validate commit `2e95eec0`.
