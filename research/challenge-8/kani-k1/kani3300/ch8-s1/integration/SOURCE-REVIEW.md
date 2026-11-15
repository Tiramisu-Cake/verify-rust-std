# S1 source review (static; Rust/Kani NOT_RUN)

Candidate reviewed: std `75a4d1ea6eb60c63c27c1b18e662740d93bafb08`, tree
`6d1b90bc11440762c9b65889fc538ba3071b0d9d`, against baseline
`872d5a43380752786415bc00d2a12ce0e930cb37`; Kani source is exact stock
`0aac16ef62da9e9d5645782d458593e5d78143ba`. This is a source review only and
confers no proof credit.

## Decision: GO for the bounded static review, with frame scope caveat

The six body contracts have `kani::modifies(v)` (and stable Freeze also
`scratch`) on generic methods whose comparator parameter is
`F: FnMut(&T, &T) -> bool`: [smallsort.rs:39-41, 60-63, 90-92, 108-110,
138-140, 174-176](/root/verify-rust-std-ch8-s1-w13/library/core/src/slice/sort/shared/smallsort.rs:39).
Kani's `modifies` is unconditional within a checked function instance: it is a
pointer set, not a conditional clause ([contracts.rs:156-162](/root/kani-upstream-ch8-s1/library/kani/src/contracts.rs:156),
[check.rs:56-70](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/check.rs:56)).
An effectful `FnMut` can write through captured mutable references outside
`v`/`scratch`, so this frame is not valid as a generic theorem. But stock Kani
docs state a `proof_for_contract` harness with type parameters may check only
one instantiation ([contracts.rs:187-192](/root/kani-upstream-ch8-s1/library/kani/src/contracts.rs:187));
these PFCs instantiate the exact pure `KeyLess` ZSTs. S1 also explicitly does
not use the new contracts as `stub_verified` summaries or claim an arbitrary
`FnMut` frame. Under that task scope, the frame clause is an instance-specific
claim the bounded PFC can check, not proof that the generic method has that
frame for every `F`.

The effectful-closure control tests inactive model activation only; it does not
call `small_sort` with that closure ([sorting_model_controls.rs:103-108](/root/verify-rust-std-ch8-s1-w13/library/core/src/slice/sort/shared/smallsort/verify/sorting_model_controls.rs:103)).
Therefore, any later use of these contracts with arbitrary `F`, or any
`stub_verified` consumer, must be rejected absent a separately justified frame.
This is a scope restriction, not a demonstrated blocker for the assigned S1
PFC instances. Exact target resolution and the actual instance-specific frame
checks remain unverified until CI.

## Static checks that pass

- All six attrs are attached directly to the intended implementation bodies;
  each requires uses the fully qualified threshold of that body's trait. The
  Stable Freeze scratch clause is `len < 2 || scratch.len() >= len + 16`.
- Each ensures uses an owned `old(snapshot::<T,F>(v))` and guards the pure
  checker with `!enabled`. The model snapshots initialized full-value bytes,
  bounds active snapshots at 32, checks length/order/all old-value counts, and
  does not call `FnMut` ([sorting_model.rs:78-120](/root/verify-rust-std-ch8-s1-w13/library/core/src/slice/sort/shared/smallsort/verify/sorting_model.rs:78)).
- The three active selectors are closed concrete `KeyLess` pairs; FnOnce/FnMut
  implementations have independent argument lifetimes and pure projections.
  The blanket model fallback is read-free and inactive for other `T,F`.
- Six separate PFC roots name the requested concrete trait targets. They assert
  activation and exact 16/32 thresholds, use symbolic N0..3, stable MU scratch
  separated from values, independently check the result and adjacent spans,
  and include N/order/duplicate/ascending covers
  ([sorting_entry_smoke.rs:32-90](/root/verify-rust-std-ch8-s1-w13/library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_smoke.rs:32)).
  The model-control source contains the expected inactive, invalid-token,
  order-corruption/count-corruption controls and legal companions.
- In stock Kani 0aac macro source, `build_ensures` lifts each `old(expr)` into
  a pre-body `let ... = (expr).clone()` ([shared.rs:138-158, 235-253](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/shared.rs:138));
  the check path runs the postcondition after the wrapped function body
  ([check.rs:33-54](/root/kani-upstream-ch8-s1/library/kani_macros/src/sysroot/contracts/check.rs:33)).
  This supports the owned-snapshot approach by source inspection only. It does
  not establish Rust compilation, target resolution, contract activation, or
  verifier success.

No Rust/Kani/CBMC qualification was run. Exact PFC body resolution, Fn lowering,
postcondition attachment/reachability, all covers, and CI behavior remain
NOT_RUN. No runtime correctness or proof claim is made.
