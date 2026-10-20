# R9 normal Continue debt (static investigation)

This is a source/translator sketch for the next likely complete-body frontier.
It is not Build evidence, a verified invariant, or proof credit. The static
sources do not establish the exact heap at the normal loop backedge; choose a
concrete invariant only after the actual verifier frontier supplies those
bindings and coefficients.

## Verified static control-flow facts

The actual body is `library/core/src/slice/sort/shared/smallsort.rs:536–574`.
Before `loop`, it sets `sift = tail - 1`, reads `tail` into `tmp`, then creates
`gap_guard { src: &*tmp, dst: tail, len: 1 }`. Each pass copies the current
`sift` cell into `gap_guard.dst`, updates `gap_guard.dst = sift`, and either
breaks at `sift == begin`, decrements `sift`, and calls `is_less(&tmp, &*sift)`;
when that callback returns true, the `if !is_less(...)` body is skipped and
control reaches the next loop head.

The source setup in `first-callback.py` puts `FIRST_SHIFT_PREP` immediately
before the loop. Its `sift == begin + 1`, split/open of `array(begin, 3, ...)`,
and cell/alignment assertions describe only that initial state. They cannot
be replayed on the backedge, where both `sift` and `gap_guard.dst` have moved.
The late callback setup begins its semantic lifetime in reached per-comparison
preparation; each existing normal/cleanup recovery closes the callback scope.
The original tmp readonly token/fraction established before the guard has a
longer lifetime and remains an obligation until the guard Drop path retires it.

In `vf_mir_translator.ml`, `find_blocks` recognizes MIR loop heads and
`translate_to_vf_basic_block` emits a `WhileStmt` only when the head carries a
translated `LoopInv`/`LoopSpec`. Otherwise it emits labeled CFG blocks. The
VeriFast `goto_block` backedge check rejects a revisited block without an
invariant (`Loop invariant required`). A Rust `//@ inv ...;` at the loop head
is translated through a compiler `LoopSpecBlock` into that checked invariant;
ordinary statements inserted before `loop {` are preheader work, not the
invariant. This points to an annotation at the existing source loop head,
without a MIR/CFG rewrite.

The translator’s `first_callback_cleanup` selects the typed `FnMut::call_mut`
normal/unwind arms only at the marked call; its normal `Continue` path closes
the callback resources and then follows the original MIR successor. The late
callback path similarly closes/reopens the scoped references on each outcome.
Neither hook establishes a loop invariant for the body’s mutable gap state.

## Required invariant shape at the ordinary loop head

The invariant must be shared by the initial entry and every normal backedge.
It needs to state, using only resources present at both points:

* stable `begin`/`tail` geometry and the original tmp/guard source relation;
* the retained original tmp reference-end token and its exact remaining
  fraction, plus the current `<F>.own`/callback receiver resources after the
  prior call has returned;
* the moving `sift` and `gap_guard.dst` relation after the completed copy and
  decrement, including which interval is an initialized current array and
  which address is the live uninitialized gap;
* any current-value list/owner resources for array segments, with values bound
  by opening those actual cells. The invariant must not equate current values
  with entry `xs` or assert a complete `array(begin, 3, ...)` while a cell is
  still the live gap;
* no per-iteration callback lifetime token/reference: the prior iteration’s
  end/recovery markers must have consumed them. The next late lifetime begins
  only at the next reached comparator preparation.

This is a resource inventory, not a claim that each item is currently
available at the backedge. In particular, static source alone does not show
which physical fraction or owner chunks the pointer copy and generated MIR
leave for the backedge. Do not manufacture them from the initial array or
from pointer arithmetic.

## Source-level annotation plan (schematic, not paste-ready)

Put one checked loop invariant at the actual `loop {` head. Its precondition
must be established by the current pre-loop split/initialization sequence; its
postcondition must be re-established after a normal `Continue` iteration.
Keep the existing initial-only `FIRST_SHIFT_PREP` before the loop. The
invariant should be assembled from existing `array::<u64>`, `points_to`,
`ref_readonly_end_token`, `lifetime_token`, and `F.own` resources with the
actual symbolic bounds and fractions observed at the frontier. Do not add a
new predicate or lemma until its definition/body and source/MIR bindings are
independently justified.

At the successful comparator return, first let the existing callback recovery
finish and close the per-call late scope. At the backedge, assert/rebind the
new `sift` and `gap_guard.dst` values from their actual locals, split or join
only the physical array segments evidenced there, and prove the invariant
from those resources. On the terminating false-comparator or `sift == begin`
arms, preserve the distinct break-state needed by the existing Drop/return
recovery; do not force them through the next-iteration invariant if their
resource state differs.

The useful implementation gate is the first exact normal backedge receipt:
record its current guard destination, sift value, tmp token/fraction, `F`
resource, and each physical/current owner chunk. If the entry and backedge
cannot establish one common invariant without losing the moving gap or the
original tmp debt, leave the loop body unmodified and return that specific
missing resource/transition as the blocker. The unchanged normal and unwind
posts, current three-cell recovery, and R8/R9 profile boundaries remain in
force.

## Actual R9 Build6 frontier

Build `776ec45f-d114-4914-bd12-792311b57ae1`, exact source `a1de980d`,
tool `706e7c89`, profile `055374de`, reaches `Loop invariant required` at
`verified/lib.rs(271,13-44)` (actual log1792) after prior cleanup leakcheck1742
passes. See R9-BUILD6-RESULT for exact archive/index/file/request identities.
This confirms the invariant blocker; the source sketch above still does not
establish the normal backedge heap or a verified invariant. Main window ended;
no implementation or new Build follows in R9.
