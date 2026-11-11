# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `6ef9fd72066443f7f113440ba32f77f310520a93`
- Candidate: `b1f0105c0390fb55081e3d186fa286d23867b585`
- Candidate tree: `45511935c1ce911ea6c85eee5f6850095cbf966e`
- Diff SHA256: `50dd4a6ef02274d642f0d326a4f9c0b41b39d131134cbf5b389e2ef3ec050b03`

## Defect

CMP1 native positives fail with uninitialized usize reads in std IndexRange::len; padding-negative has required diagnostic absent. Assess only CMP2 minus CMP1 for soundness and applicable source checks. Do not treat the author implementation or diagnosis as established evidence.

## Applicability

The existing CMP0/CMP1 product R/S/P and ordinary typed-memory model; no new layout support, ghost state, or argument-buffer protocol permitted.

## Invariants
- Typed ordinary source reads remain checked before any parameter initialization can hide a false byte.
- Empty MaybeUninit storage including nested product and ManuallyDrop S must retain every existing witness; pointer argument values must not initialize pointees.
- R receives only the applicable typed ordinary mask after source checks, P=false; no blanket whole-product blessing.
- Instrumentation source locations and ordering must remain valid at function entry, empty blocks, ordinary call/return and before/after reads/writes.
- All35 negative CMP1 harness expectations are retained; changed padding fixtures still require the intended byte-level failures, not incidental pointer errors.

## Required controls
- Assess new minimal aggregate/move, ManuallyDrop, unsize/projection, ordinary argument, pointer parameter positives and three new ordinary argument negatives.
- No local cargo/rustc/Kani/CBMC and no Cloud submission. Native acceptance remains NOT_RUN.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 b224e419fc7ab738ab981a80bd1fc39a99464efc38257caa62d0e7da6e6fe03f)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0001.bin` (mode 100644, SHA256 d3d4a880e4cc45e50907ef0687c5f43ab0ddbf2d28f0b331429d95eceabb8921)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0002.bin` (mode 100644, SHA256 c39b007da0c092a8471f4426dd79eb64600c0faa0e5a1355bd814df7a48ad787)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 336d69f6b81a33f551bb7291a51b869be84aa8e06023d1552818fdbce5003911)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs` → `dependencies/0004.bin` (mode 100644, SHA256 0f32763a6981ae6269d4b938302ac106ff6ebaa19df9fa413765a982f1390277)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs` → `dependencies/0006.bin` (mode 100644, SHA256 9f78de44ceffa0436de11ff3a4bf789c5d9909fe8425c7de543f84cd6c37fd91)
- `kani-compiler/src/kani_middle/points_to/points_to_graph.rs` → `dependencies/0007.bin` (mode 100644, SHA256 775b43c73d1350994de789dd30847e6c0339ee6ddc4ec91d9261cb2346c027d2)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0008.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `library/kani_core/src/mem_init.rs` → `dependencies/0009.bin` (mode 100644, SHA256 d565a600e34ef6199f4c6e0a799a5eb9a224ec0ed9a563ef47da2cbbe908cc06)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Only static validation authorized locally; exact failing-instance MIR/points-to binding unavailable in bounded CMP1 excerpts.
- Build subset preserves all CMP1 selectors and adds2 selectors; review of new production is required before coordinator GO.

Do not execute source or evidence from this packet. Do not claim new proof credit.
