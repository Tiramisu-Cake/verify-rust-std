# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `1dc99da6bf3c6387d8f69d9a44ffa8a8e0419139`
- Candidate: `b8c0d00ac3ab00eefaa22396274af4e9d2b15450`
- Candidate tree: `84d000bffab31216aa31cef40befdf266f047d3f`
- Diff SHA256: `353f1e0a14a5ba54aa528725455d72dfd9f783c045e5c06f659ced0046231f83`

## Defect

A2 test-only delta: new expected files must use actual driver harness headers; no semantic source changes.

## Applicability

Review exactly A2 delta with necessary A1 dependencies. Read TASK-KANI3300-A2.md at research commit a9ae7b5f6c and audit 4.1 / W1-A2 planner requirements. Static only; no author conclusions supplied.

## Invariants
- Six new golden files only; replace incorrect Test: labels with Checking harness NAME..., add positive harness labels; preserve every diagnostic, failure expectation and count. Verify headers against driver source.

## Required controls
- No nested delegation; no builds/Cloud/dispatch/cargo/rustc/Kani/CBMC/Miri/Actions/PR/issues/comments/raw evidence/credentials/network mutations/Kani push.
- No code/test edits. Write only research/challenge-8/kani-k1/kani3300/a2/REVIEW.md. Include reviewed candidate/tree/diff/spec identities, actionable findings, static verdict and limits.
- Outcomes are expectations pending coordinator CI. Do not claim measured proof, compilation, MIR/layout measurement or GO.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 f7ace04066f08093822061f24568a0688e1d373b4e75bd5248e86f0667eac68e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0001.bin` (mode 100644, SHA256 faa4e5692c295612771e5b7f384d6ce1913155f77941d9e8b4cc046aa990e451)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0002.bin` (mode 100644, SHA256 db408ef3264acfad8245ac52d7f3aa2e658578edce611552ef29d19b8729f28e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 77ecb3b77b0ec4ffd4166aca3bcbc2d1cfa7b8557f6aa7e4f7859b37d9d243fa)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0004.bin` (mode 100644, SHA256 503b2c0f60762313b6f61b4308f154a90c459b3a4370aeb4ba2aa4e4a7aef6ba)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0006.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/kani_middle/kani_functions.rs` → `dependencies/0007.bin` (mode 100644, SHA256 4fc4ef480440d05432e1f5b2245be83bd7c70b3cd547c57442c901457feb3ab4)
- `library/kani_core/src/mem_init.rs` → `dependencies/0008.bin` (mode 100644, SHA256 9ff043b57ff6aed633815bc35a185c7cdf1a94d24356c95bb74679438081c0ce)
- `rust-toolchain.toml` → `dependencies/0009.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)
- `kani-compiler/src/intrinsics.rs` → `dependencies/0010.bin` (mode 100644, SHA256 53230c07d1950d5676ed320ca30430d0f99da7cd1ba9243441a1a576a4d54c83)
- `tools/compiletest/src/runtest.rs` → `dependencies/0011.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)
- `kani-driver/src/harness_runner.rs` → `dependencies/0012.bin` (mode 100644, SHA256 4ddabb49fcbc59990e1cce5b6d2985eae33d12724fe1efe2af2534cc4ba0f480)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static review only; compiler, MIR measurement, -D warnings and coordinator CI NOT_RUN. A1 is a dependency, not newly proved.

Do not execute source or evidence from this packet. Do not claim new proof credit.
