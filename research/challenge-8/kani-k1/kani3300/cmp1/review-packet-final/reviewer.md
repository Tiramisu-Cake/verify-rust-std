# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `81dd85bfce67226e283fdd9a156932e32ece080b`
- Candidate: `bb767b96ed5d39c57c5a790c4098d0367c7400ed`
- Candidate tree: `8efbe6822044d7964c7bcddf25b99719c0930334`
- Diff SHA256: `8f170c7221c6bad8c6a0c0e895a73110b52818f05a63180f5233dee828c9413b`

## Defect

Compound struct layouts containing MaybeUninit storage currently fail layout computation. Review the CMP1 production delta and the existing argument/copy shadow protocol it relies upon.

## Applicability

Sized struct products with ordinary fields and MU or flat array leaves; nested structs and ManuallyDrop. Unsupported shapes must fail closed. No whole DST transfer.

## Invariants
- Target R/S/P byte ranges are pairwise disjoint, in bounds and cover size; internal and tail padding plus zero extents are explicit.
- Product typed reads require R. Storage transfer preserves every live uninitialized destination byte on an abstract witness path; no generic Set can bless S.
- Aggregate operands are materialized and destination disjoint from all source allocations throughout fieldwise updates; guard precedes first shadow mutation.
- Whole product copies, return and multiple arguments retain witness coverage, including nonreturned arguments and callee/caller reads.
- Typed source reads retain delayed UB checks before static mask can hide them. Padding updates touch only P. One unchanged flat ghost-state and argument buffer.

## Required controls
- Read required task/design/planner documents from paths provided in reviewer assignment. Fixtures prepared separately, native NOT_RUN.
- Check both source and destination copy witnesses; overwrite with empty slots; ordinary R poisoning with full S; raw/ref projections and real unsize; late Drop SetRef.
- Check all unsupported union/storage-enum/nested MU guards independently; bodyless calls fail before unpaired Store.

## Declared dependencies
- `library/kani_core/src/mem_init.rs` → `dependencies/0000.bin` (mode 100644, SHA256 d565a600e34ef6199f4c6e0a799a5eb9a224ec0ed9a563ef47da2cbbe908cc06)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs` → `dependencies/0001.bin` (mode 100644, SHA256 0f32763a6981ae6269d4b938302ac106ff6ebaa19df9fa413765a982f1390277)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs` → `dependencies/0002.bin` (mode 100644, SHA256 354079ebb24304c7f8dc6516ba2e50dad70f0e30466f9660d17ecece01bc7277)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0003.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0004.bin` (mode 100644, SHA256 503b2c0f60762313b6f61b4308f154a90c459b3a4370aeb4ba2aa4e4a7aef6ba)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0005.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No local compiler/Kani/CBMC runs permitted; only static and rustfmt checks.
- U3B result currently PRE_BUILD native NOT_RUN; production equals v2, PFC acceptance pending.
- Only disjoint direct-local aggregates and direct whole-product assignment destinations supported; any destination Deref explicitly Unsupported before transfer. Ordinary/MU field projections retain existing path.

Do not execute source or evidence from this packet. Do not claim new proof credit.
