# KANI3300 part 1 — complete static comparison

Source: `0ab9cc703aed799f6f73d826b60281a4632ab585`, production `81dd85bfce67226e283fdd9a156932e32ece080b`.
Historical baseline: `f046b70644e113be0df9c22c2e6ea44a65a57566`.
Official `origin/main`, fetched 2026-11-11: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`.
Packaged commit: `c39cc1121cdb287d9d77c38b87cff6c84c2c8046`, parent is that main, exactly one commit.

`V2-FULL-DIFF.patch` retains the complete original baseline-to-v2 diff: 73 files, +1765/-178.
`V2-VS-MAIN.patch` retains the direct main-to-original-v2 comparison, including reversals of intervening main changes;
it is comparison data, not the patch to apply. Only `kani3300-part1-build.patch` is a candidate/gate input.
Production is seven files, +675/-178; the original 33 fixtures/goldens are 66 files, +1090.
`v2-production-original.patch` isolates all production changes, without dropping dependencies.
`kani3300-part1-build.patch` contains the complete packaged delta: seven production files and 15 fixtures/goldens,
37 files, +1267/-178 (tests: 30 files, +592). Production is byte-identical to final v2.
No CMP1/CMP2 code was imported. The read-only v2 clone and full historical test set were not modified.

| File under `kani-compiler/src/kani_middle/transform/check_uninit/`, unless stated | Entire semantic change |
|---|---|
| `delayed_ub/mod.rs`, `ptr_uninit/mod.rs` | Pass `TyCtxt` into the instrumenter so standard wrappers are recognized by language item. |
| `ty_layout.rs` | Recognize exactly `MaybeUninit<T>` and flat arrays/slices of slots. Storage transfer masks cover its bytes; inner layouts still reject nested unions/compound storage. |
| `relevant_instruction.rs` | Add destination-type transmute checks, constant allocation masks and explicit before/after positions for storage/argument transfers. Return buffer index is zero. |
| `mod.rs` | Materialize constant arguments with their byte mask; permit reading storage without claiming initialized payload; suppress generic storage blessing; preserve typed transmute checks and mask-based writes. Clear a reset's entire slot even for an empty union field. |
| `ptr_uninit/uninit_visitor.rs` | Preserve state when forming raw addresses; distinguish reads of payload from storage; handle exact T-to-MU/MU-to-T and ManuallyDrop conversions. Transfer masks before assignments that can overwrite sources, support nonoverlapping static aggregate/repeat operands and flat slots. Instrument ordinary MIR arguments and normal returns; reject shadow-carrying no-MIR/function-pointer paths and typed_swap of storage. |
| `library/kani_core/src/mem_init.rs` | Flatten transfer metadata into marked `MEM_INIT_STATE`; snapshot live object IDs/offsets, transfer via `copy_by_id`, force return selection at index zero, clear consumed active state. Copy maps a tracked source byte or blesses the overwritten destination range for all copied elements. |

The single-byte witness model, ordinary data/padding masks, validity pass and user DFCC frame checks remain required.
`codegen/contract.rs` is unchanged: its existing `KaniMemoryInitializationState` marker lookup admits the private static
to DFCC assigns. Moving buffer fields inside that static uses this existing exemption; no user object is added.
Independent analysis of these invariants is in `REVIEW-INVARIANTS.md`; static review is not formal acceptance.

There are three intervening main commits, listed with all changed paths in `MAIN-DRIFT.txt`:
quantifier capture/safety checks, concrete playback in workspace members, and Z3 dependency/setup automation.
Neither `check_uninit/` nor `library/kani_core/src/mem_init.rs` changed between f046 and main.
The production patch applied cleanly; every resulting production file equals v2, so no semantic rebase repair was needed.
Quantifier codegen, driver/playback and dependency changes are retained from main, not reversed or included as our delta.
Compatibility of the combined main tree remains NOT_RUN. The prepared K-1 gate uses f046 and cannot establish main CI acceptance.

Every selected source has prior native PASS; `TEST-MANIFEST.json` binds each to build IDs and observations.
Six negative goldens replace a property-description match with `Failed Checks:` while retaining failure/count checks.
The frame golden retains the actual assigns failure and the outside-modifies user write at line 22.
No harness, assertion or compile/kani flag was removed. All new Rust files were run through the requested rustfmt/config.
Adapted goldens, the packaged test context and the main rebase have NOT_RUN status until a separately authorized gate.
Nonselected fixtures, including PFC OOM, UNKNOWN positive and unsupported compound controls, remain in original v2.
