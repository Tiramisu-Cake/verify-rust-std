# C2 annotation candidate: preparation and gates

This is a source-annotation draft only. It does not alter the std source, a
runner, the translator, the kernel, or a profile. It is not a verified
fixture, a callable summary, or evidence that the current C1 Cloud proof has
passed. Do not build or dispatch C2 until the owner records the C1 result and
approves the next exact profile.

`C2-ANNOTATION-DRAFT.rs` belongs immediately after the normal C1
`join_four_owned_cells::<T>(v_base, t)` at source 194 and immediately before
the existing second comparator at source 195:

```rust
let c2 = is_less(&*v_base.add(3), &*v_base.add(2));
```

The runtime expression and its operand order stay byte-for-byte unchanged.
Ghost stripping must recover the exact pinned source and complete function.
The draft does not move, replace, or omit any normal operation.

The draft starts a distinct `cmp2_k` / `'cmp2` lifetime after C1's normal
recovery and join. It re-establishes pointer limits for indices 3 and 2,
splits the four *current* owned cells, closes and borrows the current values at
`v_base + 3` and `v_base + 2`, shares those borrows, and precreates/ref-shares
the two callback argument references in that order. The tuple passed to
`FnMut::call_mut` is exactly `(&'cmp2 T, &'cmp2 T)` with fields 0/1 mapped to
those references.

Those four source values are arbitrary current values. C1 may have changed
them, and the draft makes no equality claim with function-entry values. The
same is true of the closure: there is no assertion that `F` or `is_less` is
unchanged after C1. C2 must consume the current closure state delivered by
the first call's ordinary `FnMut` contract.

Immediately before the C2 call, the four-part direct-unwind marker closes the
C2 `comparison_debt`, recovers the pair `(v_base + 3, v_base + 2)`, and rejoins
the four current cells. On normal return, the source closes the same debt,
ends only `'cmp2`, recovers that pair, then rejoins the current four-cell
array. This matches the existing callback debt and recovery lemmas; no axiom,
assumption, ownership bridge, or new lemma is introduced.

## Frontend and source-binding constraints

- Match this exact C2 source call and retain its argument order `(3, 2)`.
- The complete normal and readonly typed MIR must retain the original whole
  function, including all five `FnMut::call_mut`, eight
  `select_unpredictable`, and four `copy_nonoverlapping` calls. The selected
  C2 call must be the second callback call, with the ordered source operands
  `[v_base + 3, v_base + 2]`, direct `Continue` unwind, and no cleanup edge.
- Bind the two `precreate_ref` results to the actual MIR borrow operands in
  the `FnMut::Args` aggregate. Do not pin temporary local numbers or infer
  correspondence from equal pointer values.
- Require the second unwind marker to be unique, immediately before the C2
  call, and consumed by that call. Reject missing, duplicate, displaced, or
  wrong-call markers. The first C1 marker and its successful Cloud evidence
  remain separately pinned.
- Keep full unwind checking, strict dead-code checking, normal and unwind
  posts, helper verification, return/leak checks, and exact source/MIR/AST
  identities enabled. No verifier/compiler semantic change is part of this
  draft.

## Required Cloud gates before any bounded C2 result

1. Preserve the C1 baseline and first C1 proof as fresh Cloud evidence; do not
   infer readiness from this draft or from a native-entry lemma.
2. Reprepare from the pinned SmallSort source. Check exact source bytes,
   ghost-strip identity, unique C1/C2 call sites, and unchanged original
   runtime call inventory.
3. Export/decode/refine complete normal and readonly MIR. Record complete
   function hashes and verify both callback operand aggregates, callback
   order, C2 direct unwind edge, and absence of cleanup.
4. Verify `recover_pair` and `join_four_owned_cells` in the same unit before
   the actual target. Require a fresh C2 positive with VF0, full normal and
   direct-unwind posts, return, leak, and dead-code checks.
5. Add isolated missing-debt, missing-join, marker, operand-order, and source
   hash controls. Until a fresh run pins each control's first stage, exact
   predicate, and source location, report the observation as inconclusive;
   a generic postcondition error is not an intended negative.
6. Label any successful result as a bounded prefix through the second
   comparator/recovery boundary. It does not establish the rest of
   `sort4_stable`, destination initialization, the later comparisons or
   copies, or a callable full-function summary.

The existing source contract's positive-size, source ownership, closure
interpretation, and destination obligations remain explicit. The separate
native-entry subset theorem may be cited only as a prerequisite if its own
proof and source binding are accepted; it does not silently discharge those
other debts or compose a whole-sort summary.
