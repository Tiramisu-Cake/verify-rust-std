# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `50fa409e4dffe4fb3bd1a33b67197d3a63aa77d1`
- Candidate: `8f09ae8085e6d2884ecee1402019491038288bc7`
- Candidate tree: `97879d30bdcddde37d84ad400b17e84b3b72f708`
- Diff SHA256: `7e2c0be90e134d5730d3f75b482bd57722e3add7e0efb4eb609c723fab0c7a2e`

## Defect

Independently assess TASK-KANI3300-B2B custom MIR probes, source identity at transfer/read, syntax against pinned core MIR API, and Miri forecasts.

## Applicability

Only B2b four new diagnostic binaries and accompanying expectations/README. Static source review; no tool execution or CI.

## Invariants
- Call operand must be the original address-taken source place, with a pre-transfer raw pointer used for a post-return byte read; assess storage lifetime and unrelated UB.
- Every custom MIR construct must be documented at Rust 7189d39d9ce936881b8132c6addeaf3e295cd455 library/core/src/intrinsics/mir.rs; assess Copy-typed src with explicit Move and implicit Copy operands.
- Forecasts must follow pinned interpreter code and stay separate from measured CI, language guarantees and proof credit.

## Required controls
- Read-only callee and writing callee each have a matching Copy control; assess observable write, parameter/source separation and diagnostics.
- Check expected syntax, initialization, return locals, raw pointer validity, lack of temporary transfer/reinit and exact source:line citations by reading source only.
- Review candidate Git diff and declared dependencies; do not rely on prior B2 review verdict.

## Declared dependencies
- `research/challenge-8/kani-k1/TASK-KANI3300-B2B.md` → `dependencies/0000.bin` (mode 100644, SHA256 71582c1d32896e8efbc2516a2206f76c8b1c052aa6ca88e87c90d8f88f50deae)
- `research/challenge-8/kani-k1/kani3300/b2/probes/Cargo.toml` → `dependencies/0001.bin` (mode 100644, SHA256 1ce64b5ff4202c8aa6a81865c20b6f282bd2feb2fb484c4bef611f1694781676)
- `research/challenge-8/kani-k1/kani3300/b2/probes/rust-toolchain.toml` → `dependencies/0002.bin` (mode 100644, SHA256 7410ea2c8c514e25753899ecb12ccdd33a5bc54db88b56374cb3bc0e7fa08e44)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Forbidden: cargo/rustc/Kani/CBMC/Miri, builds/dispatch/Cloud, Actions/PR/issues/comments, Kani push, stash, raw logs/archives/credentials; no nested agents; no network writes.
- Compile/MIR/Miri outcomes are NOT_RUN and belong only to coordinator CI; audit SHA versus nightly mapping is unestablished.
- Upstream source pin may be read via GitHub; local source-only copies at /tmp/kani3300-b2b-source preserve upstream paths and may be independently fetched/hashed.

Do not execute source or evidence from this packet. Do not claim new proof credit.
