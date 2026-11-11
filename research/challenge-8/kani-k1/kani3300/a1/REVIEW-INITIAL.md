# KANI3300 A1 static review

- Baseline: `1cd96e354ec45346b61c245554a50a8af8cb5ce7`
- Candidate: `5fd713a200aea3ba85edcc341f48a0a20331fce2` (tree `a98ce921792aeebf873acd57a586e92321816e05`)
- Packet diff SHA-256: `6e4345ecea0a2832248e4601f3d88ff0c11b052752de246e3450ee5c425e2343`; spec SHA-256: `2eb2317402a9841b2f39177ecca9d83077d1851aa36f97f721cd6b93b0f80552`.

## Finding

- **P2 — zero-sized typed assignment now queries pointer identity.** `copy_init_state_single` previously delegated to `copy_init_state`, which returns before pointer decomposition when `LAYOUT_SIZE == 0`. It now calls `to_raw_parts` and `MEM_INIT_STATE.copy` unconditionally ([mem_init.rs:389](/root/kani-fix-3300-a1/library/kani_core/src/mem_init.rs:389)); `copy` obtains object/offset identities before `copy_by_id` reaches its zero-size guard. For `MaybeUninit<()>` this changes a zero-byte no-op into pointer-object queries. Add an early zero-size return before raw pointer handling, matching the old path and the other model helpers. This is a static concern; no runtime failure was measured.

## Review notes

The transfer split is otherwise coherent by inspection: `for_typed_storage` derives D(T), repeats it at array stride, and leaves raw `Copy`/`SetSliceChunk` on full storage masks. `SetStorage` intersects its initialized mask with D(T), so false data bytes remain false and padding is discarded. Generated `CopyInitStateSingleModel` and `LoadArgumentModel` calls match the changed model parameters; `StoreArgumentModel` remains the two-argument identity capture. Existing pinned `rustc_public` layout/array APIs used here match the staged nightly-2026-10-23 source snapshots. No new import or plainly unused binding was found.

The fixtures distinguish raw copy, typed assignment, bodyful argument/return, data preservation, partial data, and N=2 array stride. Their `.expected` files are expectations, not measured outcomes. Existing A2 layout, A3 pairing, and B1 resolver concerns remain outside this review.

## Verdict and limits

**NEEDS_FIX (zero-size guard), then coordinator CI review.** `git diff --check` is clean. No cargo/rustc/Kani/CBMC/Miri, compilation, MIR inspection, or CI was run; unused/`-D warnings` could not be compiler-verified. No proof credit or CI claim is made.
