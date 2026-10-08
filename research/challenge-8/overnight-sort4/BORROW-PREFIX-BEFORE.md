# First actual `sort4_stable` comparator: borrow-prefix diagnostic

## Obligation and hypothesis before implementation

O13 (`37711416854`, pinned std source SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`)
proved the checked first `v_base.add(1)` bounds lemma, then stopped at the
unchanged first comparison with no
`ref_precreated_token<T>(ptr_add_(v_base, 1, T_typeid), _)`. The actual call is
`is_less(&*v_base.add(1), &*v_base)`. This fixture tests whether four owned
source values can be decomposed into four real cells, with the first two
closed into full borrows,
shared through a fresh lifetime, and converted by the stock `precreate_ref`,
`init_ref_share`, `close_ref_own`, and tuple ownership protocol into the two
references required by the first callback. A checked split lemma must carry
the two untouched cells and their owners; no cell, owner, reference token, or
borrow debt may appear without a source resource or a named stock lemma.

The diagnostic retains the memory-pre contract: arbitrary sized `T` with
`0 < size_of::<T>()`, `F: FnMut(&T, &T) -> bool`, four initialized source cells
and exactly one `<T>.own` per cell, four optional destination cells, current
comparator ownership, type interpretation and thread token. It assumes no
`Copy`, `Freeze`, purity, SWO, or infallible comparator. ZST and the full
generic contract remain open. The intended normal post is the current source
array and owners, **initialized** destination array, current comparator and
thread/type resources. The intended unwind post is the current source array
and owners, **unchanged optional** destination storage, and current comparator
and thread/type resources. Active diagnostic posts retain the memory-pre
partial normal optional-destination post and the full current-source/owner,
optional-destination, comparator/thread/type unwind target. Neither post
claims ordering.

This is deliberately a prefix test. The stock `FnMut::call_mut` unwind clause
does not return `Args.own`; the two borrowed source cells require explicit
recovery on direct unwind. The separate callback-unwind component owns any
frontend hook for that edge. Until that component is independently reviewed
and active, a full verifier failure at the first call's unwind resource debt
is expected, not a sort4 proof. A setup, source, export, decode, refinement,
or split-lemma failure is inconclusive and must be repaired or reclassified;
it is not evidence of the callback obligation. A successful transition past
reference creation must be observed in the full trace, not inferred from a
missing error string.

## Semantic and trust boundary

No trusted primitive or verifier patch is added here. The array and `foreach`
split is a checked ghost lemma over the pinned stock predicates. Every
reference token is returned by stock `precreate_ref` and initialized from the
actual full-borrow share. All inserted text is ghost-only; removing it must
reproduce the exact actual runtime signature/body. The existing source SHA,
blob, first-call inventory, full NORMAL/readonly typed MIR, refinement, tool
hash, and source-alter control remain mandatory. The old `--memory-pre` path
stays byte-for-byte the same. This new mode is always diagnostic, even if the
whole verifier happens to exit zero; any acceptance would need a separate
full contract and unwind review.

The primary positive control is arrival at the first real `FnMut::call_mut`
after both reference creations, with no missing `ref_precreated_token` at
either argument. The source-alter negative must reject before MIR. The
split lemma itself must verify to return/leak check. The stock callback
microfixture already exercises the same two-reference construction and its
false-post negative, but it cannot replace the actual sort4 call. If the
first failure remains in the new setup, inspect the exact resource and
change this hypothesis before adding more annotations. If it reaches direct
unwind recovery, integrate the independently reviewed callback hook, then
recover the source array and advance to the remaining comparisons.

## Self-review

The split lemma opens an existing four-element array and existing `foreach`
ownership four times, returns four initialized cells with one owner each,
and creates no additional ownership. The first two cells
are borrowed only after that split. The positive-size premise prevents this
fixture from treating equal-address ZST elements as disjoint. The partial
normal destination post is not silently upgraded to initialized output, and
the direct-unwind owner restoration is not discharged by this prefix.
