# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `85fc5cd2ca770cdc5ae1bb514c27b6da7b6d9b18`
- Candidate: `b207847932da34ac19886c1337f5b69ace0b0843`
- Candidate tree: `3cdfc7e4ee0551211554f40968d391e3d404e27d`
- Diff SHA256: `0e185648814b3c9f3dfd2accea2cef4b9d0b059bedb833ea057ce28c8d148327`

## Defect

A2R expected-output strengthening: bind the three failures to named harness summary lines.

## Applicability

Test-only follow-up to initial A2R semantic packet c7b5900fd64467627cc99a4a47c6a1b05984586642e96168e81cefb02fba71e0. Production source unchanged.

## Invariants
- Keep exact 4 success / 3 failure / 7 total expectation and require each of the three intended negative harness names in the final failure summary. No removal or weakening of diagnostics or checks.

## Required controls
- No nested delegation; no builds/Cloud/dispatch/cargo/rustc/Kani/CBMC/Miri/Actions/PR/issues/comments/raw evidence/credentials/network mutations/Kani push.
- No code/test edits. Write only /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/a2r/REVIEW.md. Report exact candidate/tree/diff/spec identities, actionable findings, static verdict and limits.
- No proof/compilation/runtime credit. CI outcomes are unmeasured expectations for the coordinator.

## Declared dependencies
- `tests/expected/uninit/raw-eq-uninit/main.rs` → `dependencies/0000.bin` (mode 100644, SHA256 246f3ba9461867dc640bc788c47d56b8e936f5fa1784c05afb9279b02e7c81ea)
- `kani-driver/src/harness_runner.rs` → `dependencies/0001.bin` (mode 100644, SHA256 4ddabb49fcbc59990e1cce5b6d2985eae33d12724fe1efe2af2534cc4ba0f480)
- `kani-driver/src/metadata.rs` → `dependencies/0002.bin` (mode 100644, SHA256 af5cee0d4b9d3f1d3c5d7ca97d157db90f9ca6499743881edcbe5f5d0390232c)
- `tools/compiletest/src/runtest.rs` → `dependencies/0003.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static only; no builds or local compilers are authorized.

Do not execute source or evidence from this packet. Do not claim new proof credit.
