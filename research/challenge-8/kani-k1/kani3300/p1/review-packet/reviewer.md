# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`
- Candidate: `c39cc1121cdb287d9d77c38b87cff6c84c2c8046`
- Candidate tree: `582c123d68fb1f585ffb3e40b0d5c96c1d7d4ca3`
- Diff SHA256: `b30758e575bb0bfabab186d615e8b28871543efb0703028aa721a8622ef28c40`

## Defect

Kani #3300: MaybeUninit storage must carry byte initialization state through pointers, transmute, flat slot arrays/slices and ordinary MIR argument/return transfers. Review the entire production v2, not merely the last repair.

## Applicability

Part 1 only, final source 0ab9cc703aed799f6f73d826b60281a4632ab585 production equals 81dd85bfce67226e283fdd9a156932e32ece080b. Baseline f046..main has no changes in check_uninit or mem_init.rs. No builds, no publication.

## Invariants
- Single-byte nondeterministic shadow witness must detect any initializedness violation; data/padding masks preserved; copies must invalidate overwritten destination and preserve source witness.
- Flat bool/usize buffer is inside marked MEM_INIT_STATE. Non-deterministic argument selection, deterministic return index zero, nested calls and consuming active state must preserve witnesses.
- copy_by_id must not inspect dead return pointers or fabricate object/provenance ownership. Snapshot IDs while source live.
- DFCC may exempt verifier-private MEM_INIT_STATE only; actual writes outside modifies must remain checked. No assumptions or user-check weakening.

## Required controls
- 15 historical native PASS fixtures selected. Inspect all new sources/goldens, positive and negative pair strength; five adversarial argument/overlap/overwrite/repeat/reset tests are required. Current packaged form NOT_RUN.
- Frame negative must stay bound to actual user write at main.rs:22. Goldens for failures inside core use Failed Checks.
- No local cargo/rustc/Kani/CBMC; static review only.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0001.bin` (mode 100644, SHA256 47b1063398159a376fd4edcecee4d28ac24f54b2e86a930d836b354023cd8ed0)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0002.bin` (mode 100644, SHA256 503b2c0f60762313b6f61b4308f154a90c459b3a4370aeb4ba2aa4e4a7aef6ba)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 6a4d519b9261a2a3e479b6b143a8f6702273ddcaeee734fa513187fc4df92723)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0004.bin` (mode 100644, SHA256 db408ef3264acfad8245ac52d7f3aa2e658578edce611552ef29d19b8729f28e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0005.bin` (mode 100644, SHA256 ce16fba0d46cae786b1a85672a67e2460ff1df4c5c91d76d2c4883eed0153253)
- `library/kani_core/src/mem_init.rs` → `dependencies/0006.bin` (mode 100644, SHA256 d565a600e34ef6199f4c6e0a799a5eb9a224ec0ed9a563ef47da2cbbe908cc06)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/contract.rs` → `dependencies/0007.bin` (mode 100644, SHA256 df0b9b50b8d035aa9b447ec0af648b7466cdc74a30ed34c85a08dc9cffec5789)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0008.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/kani_middle/kani_functions.rs` → `dependencies/0009.bin` (mode 100644, SHA256 4fc4ef480440d05432e1f5b2245be83bd7c70b3cd547c57442c901457feb3ab4)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- PFC MU-roundtrip v2 reports OOM; clean positive timed out, U1 comparison INCONSISTENT/UNVALIDATED. No upstream-existing-OOM or regression claim established.
- Nested/arbitrary unions, compound storage, typed_swap, select_unpredictable, function-pointer transfers outside supported domain. CMP1/CMP2 excluded.
- Bounded finite native controls, not general proof credit; current main candidate not executed.

Do not execute source or evidence from this packet. Do not claim new proof credit.
