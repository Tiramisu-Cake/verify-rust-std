# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `1cd96e354ec45346b61c245554a50a8af8cb5ce7`
- Candidate: `5fd713a200aea3ba85edcc341f48a0a20331fce2`
- Candidate tree: `a98ce921792aeebf873acd57a586e92321816e05`
- Diff SHA256: `6e4345ecea0a2832248e4601f3d88ff0c11b052752de246e3450ee5c425e2343`

## Defect

KANI3300 A1: typed MaybeUninit transfers must preserve only D(T), while raw copies retain the full storage extent.

## Applicability

Review exactly the A1 candidate delta and necessary base call sites. Static-only independent review; pinned nightly-2026-10-23 rustc_public sources /tmp/kani3300-g1r-api, hashes in ../g1r/API-SOURCES.json. Read TASK-KANI3300-A1.md and audit sections 2.1, 2.2, 4.2 as requirements, without author conclusions.

## Invariants
- Typed assignment, constants, bodyful arguments and normal returns preserve source initializedness at D(T); padding destination becomes uninitialized. A false source data byte stays false.
- Raw copy/copy_nonoverlapping retain full rustc extent, padding and partial data. Flat arrays repeat D(T) at rustc stride, N>1; flat slices use slot layout.
- Unsupported layouts reject before applying any mask. Preserve existing support limits; A2 offset/layout repair, A3 call-pairing, B1 resolver work are outside A1.
- Keep nondeterministic single-byte witness coverage, overlap and overwrite semantics; capture return identities while live. No weakened existing fixture/check/contract.
- Check model ABI vs generated calls and pinned rustc_public signatures; unused/import/borrow/type concerns under -D warnings. Inspect new regression fixtures and exact failure intent.

## Required controls
- No nested delegation. No builds, dispatch, Cloud, cargo/rustc/Kani/CBMC/Miri, Actions/PR/issues/comments, raw evidence or credentials, network mutations or Kani push.
- No production/test edits. Write only a concise REVIEW.md in this A1 research directory, with exact reviewed candidate and packet identities, concrete findings, and static limitations.
- All new harness outcomes are expectations pending coordinator CI; do not claim measured proof or GO.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 f7ace04066f08093822061f24568a0688e1d373b4e75bd5248e86f0667eac68e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0001.bin` (mode 100644, SHA256 ecaeb6e98d40bddd5f896613dac390c68f512d41dd077d71811501c352338200)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0002.bin` (mode 100644, SHA256 db408ef3264acfad8245ac52d7f3aa2e658578edce611552ef29d19b8729f28e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 6a4d519b9261a2a3e479b6b143a8f6702273ddcaeee734fa513187fc4df92723)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0004.bin` (mode 100644, SHA256 503b2c0f60762313b6f61b4308f154a90c459b3a4370aeb4ba2aa4e4a7aef6ba)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0006.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/kani_middle/kani_functions.rs` → `dependencies/0007.bin` (mode 100644, SHA256 4fc4ef480440d05432e1f5b2245be83bd7c70b3cd547c57442c901457feb3ab4)
- `library/kani_core/src/mem_init.rs` → `dependencies/0008.bin` (mode 100644, SHA256 a7e2d3e2c871bfdd32c84c5fa76a25f85eedb9a84db7aa65764abec80ca7f92a)
- `rust-toolchain.toml` → `dependencies/0009.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Compilation, MIR/Miri inspection and native verification NOT_RUN by task authorization; existing A2/A3/B1 blockers remain separate.

Do not execute source or evidence from this packet. Do not claim new proof credit.
