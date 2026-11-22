# #752. Draft for owner review

Use the replacement below after the bounded checks and regression matrix pass on the candidate. Keep the other entries in **Limitations**.

## Replacement for “Contracts on the trait methods”

> **Scope of the trait-method contracts.** The three `small_sort` trait methods carry direct sorting contracts on their implementations, including the specialization defaults. The contract checks establish nondecreasing order and preservation of the full logical-value multiset on normal return for the covered fixtures. These fixtures use `u64` with a fixed read-only comparator at lengths 2 and 3, `Cell<u8>` at length 2 for the stable and unstable defaults, and a non-`Copy` byte key that implements `Freeze` at length 2 for the Freeze default. The claims are limited to the tested comparators, types, lengths, and slice and scratch layouts. Stability for distinguishable equal-key elements, unwinding, and coverage for arbitrary types, comparators, and lengths remain open.

## Addition to the PR description

> Adds direct sorting contracts and bounded `proof_for_contract` checks for `StableSmallSortTypeImpl::small_sort`, `UnstableSmallSortTypeImpl::small_sort`, and `UnstableSmallSortFreezeTypeImpl::small_sort`, including their specialization defaults. The checks use the repository’s pinned Kani and preserve the existing SmallSort harnesses.
