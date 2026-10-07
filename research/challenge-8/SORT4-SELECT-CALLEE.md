# `select_unpredictable` actual-callee diagnostic

**Result: inconclusive at the first call in the real helper body.** Hosted run
[37549040942](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37549040942),
repository source `aed1d97`, used the accepted experimental layout profile for
other jobs but this stock VeriFast 26.09 pointer-callee diagnostic. Export,
decode, refinement and source-integrity stages passed. The fixture contains
one actual-callee body; original and verified runtime body hashes are
`0d4233fe67c243c9d46201603fb143182ba2f5caa35f5d63907a3d5c50ed9613` and
`bd332fbb6a4cbc9fc935b6bc5a0dcc99f691af9182535a1b64ae40ad516bb8fd` after
ghost annotations are stripped. The source identity is
`library/core/src/hint.rs`, blob `fe59166363b9cc049c0d48f4349f4dc9c0e458b8`,
SHA-256 `d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8`.
The full hosted evidence is under `/tmp/sort4-night-37549040942-artifacts/`;
the per-run log is `/tmp/sort4-night-37549040942.log`.

The fixture targets `T = *const Element`, without `Element: Copy`, and keeps
the runtime body byte-identical. It records a non-const proof adapter for the
pinned compiler, because this is a pointer instantiation diagnostic, not a
proof of the original generic `[const] Destruct` API. Its requested normal post
is full pointer-model equality with the argument selected by `condition`,
preserving provenance through pointer equality, plus the thread token/frame;
the requested unwind post is false for this pointer instantiation. None of
these posts was proved.

The first VeriFast error is at the first body statement:
`No such function: std::mem::MaybeUninit::<T>::new` (`verified/lib.rs:21`). The
prior hypothesis that an intrinsic would be the first unsupported operation
is superseded. The exporter emitted all three intrinsic calls, the local
`DropOnPanic` declaration/body and the later `as_mut_ptr`, `drop_in_place`,
`forget`, and `assume_init` operations; the verifier did not reach their
proof obligations. This is a function-resolution/frontend blocker, not an
intended negative and not evidence about intrinsic semantics, pointer result,
provenance, frame, or normal/unwind correctness.

The target implementation is visible in
`library/core/src/mem/maybe_uninit.rs:345–348,374–398`: `MaybeUninit<T>` is a
transparent union with `uninit: ()` and `value: ManuallyDrop<T>`, and `new`
returns `MaybeUninit { value: ManuallyDrop::new(val) }`. In the pinned
`bin/rust/std/lib.rsspec:429–486`, VeriFast models it as `struct MaybeUninit<T>`
and supplies a ghost fixpoint `MaybeUninit::new(v)` via
`new_maybe_uninit(some(v))`. That algebraic model does not register or prove the
runtime MIR function call emitted for `MaybeUninit::new`; the existing
`MaybeUninit::write` contract at lines 488–493 is a different operation and
cannot stand in for this call while retaining the body.

No checked actual-constructor route was found in the frozen profile. It would
need a checked correspondence from the runtime constructor body to the
`MaybeUninit` ownership model, including initialization of the union's
`ManuallyDrop<T>` field. Adding an opaque constructor summary, aliasing the
runtime call directly to the ghost fixpoint, or introducing a trusted union
ownership bridge would assume the missing step and is outside authorization.
The smallest future capability to assess is a source-linked, checked lowering
or body-verification route for this constructor and its union field ownership;
only after that succeeds can this unchanged helper reach the three intrinsics
and `DropOnPanic` proof obligations.

No source/script was changed for this diagnostic; no local executable checks
were run. No verifier rerun or patch is proposed in this note.
