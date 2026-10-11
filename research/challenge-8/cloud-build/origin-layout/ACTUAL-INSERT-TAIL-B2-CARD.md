# B2: actual `insert_tail` three-cell causal diagnostic

**Status: PREPARED, NOT RUN, NO PROOF CREDIT.** Policy revision read:
`6e1a8e59c56669abe5e6ec2013478e45ed2cc267`. Authorized session №2
starts 2026-10-11 21:36:26 UTC, main cutoff 23:36:26 UTC and finish-only cutoff
2026-10-12 00:06:26 UTC. B1 qualification and transport repair precede B2. This
card does not dispatch a Build or transfer a B1 result to B2.

The actual obligation is SmallSort's `insert_tail` at lines 536–570; its
consumer is the insertion loop in `insertion_sort_shift_left` at line 596 and
the two scratch-half loops in `small_sort_general_with_scratch` at line 274.
The Cloud fixture pins full original `insert_tail` and `CopyOnDrop` blocks from
SmallSort blob `40939f922bcb6fdc7ee0d30427fa861827043827` and source SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.
Static read/hash of the current assigned source confirms the exact Drop block
SHA-256 `caff1edbfa3a8d9fd29459e49c43abd0f8f987f9061c75e7bf6ecedbbba26a6a`
(364 bytes, lines 295–310) and full insertion block SHA-256
`9bc00f3913373e5879769b9970d66b1a56ada05a10205d51cafdf6533ecc2f29`
(1380 bytes, lines 536–571). The hosted preparation rejects a hash, byte
count or ordered runtime-anchor mismatch before executing any proof stage.
It mechanically substitutes `T=u64` in every runtime statement and the guard
type while retaining generic `F`, `FnMut` calls, `self.len`, and both normal and
cleanup Drop edges. Paired original/verified inputs differ by checked proof
annotations only; ghost stripping must reproduce every runtime byte. This is a
concrete specialization diagnostic, not generic `insert_tail` verification.

`b2_three_from_local` creates `[10_u64, 20, 5]` in its own stack allocation,
derives `begin` and `tail=begin+2`, and passes its genuine `&mut F`. Its sole
external resource precondition is the canonical `&mut F` comparator state
`*is_less |-> f0 &*& <F>.own(t,f0)`, with thread/type resources. This is the
caller's legitimate input obligation, not a guard/receiver premise; a later
actual outer caller must establish this `F` borrow and get its current state
back on both outcomes. The actual callee's precondition is its three initialized cells,
one current `<u64>.own` for each, and the comparator state; the wrapper must
establish it from the local initializer. No receiver, guard FBC, origin,
borrow-end token, current-gap premise, or source/destination permission is
supplied to either function. The complete target normal **and** unwind posts
restore all three initialized cells with one owner per current value, current
`F` state, thread/type resources and caller frame. They do not claim that a
callback preserves entry values. The wrapper's normal/unwind F post and leak
check must also pass; a final proof requires checking the array at its call
boundary and local cleanup, not merely a green callee.

For the intended witness, the first callback may return true. `tail.read()`
moves the sole logical owner of `5` into `tmp`, leaving a logical gap at index
2. `copy_nonoverlapping(sift, gap_guard.dst, 1)` copies `20` into that gap;
the actual assignment `gap_guard.dst=sift` moves the logical gap to index 1.
The late `is_less(&tmp,&*sift)` can then unwind. Before the real cleanup
`Drop`, both callback reference loans and current `F` state must be recovered;
the checked generated glue/selected method copies the **current** held value
into the updated gap. The normal second-false path fills index 1; second-true
shifts `10` and fills index 0. The first comparison's early false return and
direct panic must also satisfy the full posts, without a guard. No sorting or
snapshot/permutation claim is made from arbitrary callback answers/effects.

## Falsifiable first experiment

The new `actual-insert-tail-b2.py` is an inert hosted `execute_case` hook. On
the exact experimental profile `experimental-merge-actual-glue-body-v8`, which
is **not accepted for integration**, a
single case prepares the full bodies and posts, runs exporter/decode/official
refinement/VeriFast through the existing merge lane, stores source and stage
receipts, and records the first exact error. It never classifies an early
setup, frontend, resource, dead-code, or refinement failure as an intended
negative or proof success. The first predicted causal refusal is the actual
`tail.sub(1)` at SmallSort line 540: a three-cell array resource may still
need an explicit checked interior `pointer_within_limits` derivation. This
matches an older generic-source observation and is a hypothesis for the new
concrete profile, not transferred proof evidence. If that bound is discharged,
the next expected refusal is the first comparator's genuine reference loans
at line 541; later refusals would identify moving-gap or cleanup resources. A late-Call refusal would identify the next
needed lowering rule. The current script deliberately adds **no** callback
marker: the existing marker protocol is inapplicable to this exact CFG. A
full positive needs reached first/late calls, two shifts or justified loop
invariant, normal and late-panic cleanup, actual selected Drop/glue body,
all full posts, return/free/leak/dead-code, and an exact paired MIR/AST and
source-refinement certificate.

Prior MIR evidence in `INSERTION-RESOURCE-LEDGER.md` is dated and must be
re-observed for this input. It maps first callback `bb1` to direct Continue;
late callback `bb13` to cleanup `bb20`, which Drops the guard and reaches
`bb21` UnwindResume. The existing cleanup translator admits only a single
generic-`T` two-source `FnMut` call with `UnwindAction::Continue` and a strict
ghost marker sequence. Its global synthetic unwind epilogue would skip the
real guard Drop if applied to the late Call. Thus the fixture currently can
provide a causal failure, **not** a logically complete proof annotation.
The required next semantic card must qualify this exact late Cleanup edge,
return both temporary reference loans and current `F` before guard Drop,
preserve the real cleanup successor and original UnwindResume, and prove
normal/cleanup current resources without creating a second owner. The first
comparison needs its separate full-return recovery. This is within the
owner's narrow exporter/lowering/refiner/receiver-Drop authority only after
its own before-implementation card and regression design; kernel, memory,
alias, generic `T`, ZST and source runtime changes remain outside scope.

The official refinement checker currently follows only normal targets of
`Call` and `Drop` (`refinement_checker.ml` near 2595 and 2607, both TODOs).
Before any B2 panic proof claim, the qualified actual caller must compare
original and verified unwind action and cleanup graph, with mutations that
remove or redirect the late Call cleanup and guard Drop rejected at the exact
refinement obligation. Ordinary normal/unwind smoke does not close this.

Expected controls after the first causal result: a reached false assertion
after the first `dst` update; missing callback loan fraction/token at its
real close/end predicate; missing moving-gap destination permission at the
actual selected Drop precondition; and late cleanup-edge mutants at official
refinement. Each needs its own exact stage, predicate and location oracle
calibrated from raw Cloud evidence. Until then every control is NOT_RUN and
the v8/B2 profile remains NOT_ACCEPTED/NOT_FOR_INTEGRATION. A full source,
proof, or tool change requires a fresh exact-SHA Build; saved replay changes
only classification of unchanged artifacts.
