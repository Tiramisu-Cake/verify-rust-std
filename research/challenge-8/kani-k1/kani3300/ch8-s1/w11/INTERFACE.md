# W11 → W13 interface, S1 v1

Status: v1 accepted for preparation by worker13 via thread message on 2026-11-16.
Core/Kani qualification remains NOT_RUN; integration acceptance belongs to worker13.
Module path: `crate::slice::sort::shared::smallsort::verify::sorting_model`.
All facade items use `pub(in crate::slice::sort::shared::smallsort)`.
Worker13 registers `pub(super) mod sorting_model;` inside verify; the actual
smallsort attrs can then use `verify::sorting_model::*`. Private fields stay private.
This visibility correction was proposed to13 before source freeze.

```rust
KeyLess<T>::new() -> KeyLess<T>
NonCopyByte::new(value: u8) -> NonCopyByte
enabled::<T, F>() -> bool
snapshot::<T, F>(values: &[T]) -> Snapshot
post::<T, F>(before: Snapshot, values: &[T]) -> bool
```

No caller bounds, including no T:Copy/Ord/Freeze or F bound. Private `Model<T,F>` on
`()` has blanket default methods and three concrete specializations, compatible in
intent with baseline `min_specialization`; actual core/Kani qualification NOT_RUN.
Pairs: u8/KeyLess<u8>, Cell<u8>/KeyLess<Cell<u8>>, NonCopyByte/KeyLess<NonCopyByte>.
Named KeyLess has a private PhantomData field; manual concrete FnOnce/FnMut impls
with independent argument lifetimes use `extern "rust-call"`; no FnPtr/address guard.
Requires `fn_traits` under `cfg(all(kani,kani_smallsort_sorting))` in core lib;
`unboxed_closures` and `min_specialization` already present in std872d.

`Snapshot: Copy` owns `[u8;32]`, input len and valid flag, private fields. Full-value
projection equals the order key for these three types. Only active initialized
prefix is read; inactive snapshot returns invalid without even querying input len.
Inactive post returns true without reading input; attrs MUST explicitly guard
`!enabled::<T,F>() || post::<T,F>(old(snapshot::<T,F>(v)), v)`.
Active len>32 returns invalid / post=false; never truncate or panic.
Active post requires valid snapshot, equal len<=32, adjacent sortedness, and equal
counts of every input value. With equal lengths these counts exhaust the output:
no novel value can replace an input value. No FnMut call/allocation/assumed sortedness.

NonCopyByte: repr(transparent) u8, Freeze, size1/align1, !Copy, no Drop.
Cell<u8>: size1/align1, !Freeze; projection only get(). u8: Freeze+Copy, size1/align1.
KeyLess is ZST, no capture/writes. Model activation depends on exact T/F only, not N.
Snapshot pairing is caller's responsibility: snapshot and post use the same T/F
and the pre-call input. This is not an arbitrary-token authentication API.

W11 modules: sorting_model.rs and sorting_model_controls.rs only. W13 registers
model under cfg(all(kani,kani_smallsort_sorting)), controls additionally under
kani_smallsort_controls. Controls are opt-in proof roots, never ordinary inventory.
No raw adapter is part of v1. API changes require communication before freeze.
