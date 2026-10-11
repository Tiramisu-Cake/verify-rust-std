# Public stable-sort guard prefix — conditional Cloud diagnostic

The actual public entry is `library/core/src/slice/sort/stable/mod.rs:29`:
`sort<T, F: FnMut(&T, &T) -> bool, BufT: BufGuard<T>>(v: &mut [T],
is_less: &mut F)`. The pinned source SHA-256 is
`3f2b2d8543a1cb91c9352e041bed49949a31cbd4b1030ec1a82cca1304cb22d3`.
It first returns if `T::IS_ZST`, then computes `len = v.len()` and returns
when `intrinsics::likely(len < 2)`. This experiment cuts immediately after
the first guard, before computing `len` or translating `likely`. The actual `SizedTypeProperties::IS_ZST`
definition is `Self::SIZE == 0` in `library/core/src/mem/mod.rs` (SHA-256
`b86a596a58dcb21a45e8b29b33327ca8c7bde708aa6fca158d4366e51403daf2`).
The pinned translator already lowers the exact associated constant to
`std::mem::IS_ZST::<T>()`, whose existing rsspec says its result equals
`size_of::<T>() == 0`. This diagnostic changes no tool rule or spec.

The proof-only fixture retains the generic `T/F/BufT` signature, native
`v: &mut [T]` and `is_less: &mut F` resources, and the exact first guard.
It asserts only that this guard's continuation has `size_of::<T>() > 0`.
The ZST early return must satisfy its full generated normal, unwind, local
free and leak posts. The no-panic guard path must retain native source cells,
F ownership, thread/lifetime/type resources and refinement. A false
`size_of::<T>() == 0` assertion on the continuation and a false assertion
inside the reachable ZST branch are independent negative controls, each
creditable only at its exact assertion after paired MIR/refinement. The
later `len` and `intrinsics::likely` operations receive no proof credit.

This is a deliberately partial public-entry diagnostic. It cannot transfer
this continuation fact to `small_sort_general_with_scratch`: the intervening
cfg selection, insertion/driftsort, scratch construction and calls remain
unproved. In particular, it supplies no non-ZST precondition to the separate
native helper fixture and cannot resolve its `len + 16` obligation by fiat.
Any VF0 result remains a candidate under the experimental, unaccepted
ZST/C1/C4 tool profile and needs fresh full source/MIR/AST/log review.
