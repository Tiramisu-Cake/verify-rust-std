# Outer insertion loop: bounded safety experiment

This experiment checks memory safety of the actual generic
`insertion_sort_shift_left` instantiated with `[i32; 4]` backing storage. The
proof-only module makes no sortedness, comparator-ordering, or comparator
consistency assumptions. It chooses `len` from 1 through 4 and `offset` from 1
through `len`, then supplies a `FnMut` comparator whose result is a fresh
unconstrained Boolean on each call. Kani's default safety checks remain enabled;
there are no functional postconditions or replacement implementations.

`inject-outer-invariant.py` accepts the path of a disposable copy of
`smallsort.rs`. It requires the unique exact declaration/loop anchor in
`insertion_sort_shift_left`, rejects a second application, and inserts a
proof-only loop invariant: `tail` stays in the allocation of `v_base`, does
not precede the initial tail at `v_base.add(offset)`, and does not pass
`v_end`. The three obligations form one conjunction in one attribute, so the
experiment does not depend on stacking loop-invariant attributes. It fails
closed if the source no longer matches. The Kani pin is commit
`152c6a8c875d9886a67e229247b4826d6105ccfd` (Kani 0.67.0), recorded in
`tool_config/kani-version.toml`. The pinned implementation is
`library/kani_macros/src/sysroot/loop_contracts/mod.rs`; core exposes Kani
through `kani_core::kani_lib!(core)` in `library/core/src/lib.rs`. The same-allocation predicate available
to core proofs is `crate::ub_checks::same_allocation`, defined in
`library/core/src/ub_checks.rs`. No frame condition is included.

The seven covers witness lengths 1 through 4, both endpoint offsets, and the
maximum span. These are reachability checks, not assertions about sortedness or
callback outcomes.

This is a bounded safety experiment only. It does not prove arbitrary slice
lengths, functional sorting, generic ownership behavior, or all Challenge 8
obligations. The inner shift loop remains subject to the finite unwind bound;
this experiment does not prove generic comparator unwinding,
uninitialized-read absence, or generic type behavior. The injected annotations are experiment evidence and must not be
committed into the standard-library implementation. The Kani version remains
the repository pin in `tool_config/kani-version.toml`.
