# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `0b1d68ac691cac7e03dbe73f4aec139bb5389059`
- Candidate: `585c93b2ff366f5723611a7ca944328ef62f40b5`
- Candidate tree: `15315ec46854fcb639d8c823a026090ea84a843d`
- Diff SHA256: `0023717c03680a3b5a3c3954af59ea44c9ea6fa893f23fc9280ee0cff3255847`

## Defect

KANI3300 A2R2: raw_eq must check every byte of both referenced pointees rather than reference storage; compare normal CheckRef and delayed-UB instrumentation.

## Applicability

Review exactly TASK-KANI3300-A2R2.md at research 645dbfe5a6, inheriting TASK-KANI3300-A2R.md. Static review only, no author verdict supplied. Base includes A3.

## Invariants
- Trace generated address, cast, pointee mask and later delayed-UB visitor. Both raw_eq arguments must cover size_of::<T>() bytes including padding and union storage, not the argument-reference storage. Compare normal CheckRef dereference. Preserve initialized reads and existing uninit reads; check reference Copy/Move/Constant handling and reference argument parameters.
- Preserve full byte-mask, initial targets and unknown-layout Unsupported. Existing three MU selectors, A3 protocol, Pat/enum code must remain unchanged. Raw-pointer-to-reference CheckAs behavior must remain unchanged.
- Audit fixture and golden order: initialized direct and borrowed arrays/storage/scalars/ZST expected SUCCESS, left/right one-byte hole and padding expected uninit FAILURE with [u8; N] diagnostic. No unrelated failures accepted. Three MU golden files unchanged.
- Audit Rust API/types/borrowing/exhaustiveness and clippy/-D warnings by source using pinned /tmp/kani3300-g1r-api and g1r/API-SOURCES.json. No compilation.

## Required controls
- No nested delegation, no builds/Cloud/dispatch/cargo/rustc/Kani/CBMC/Miri/Actions/PR/issues/comments/Kani push/raw evidence/credentials/network. Python/source reads allowed.
- No implementation/test edits. Write only /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/a2r2/REVIEW.md. Include exact candidate/tree/diff/spec identities, actionable findings and static limits.
- No runtime/compilation/proof credit. CI belongs to coordinator.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 a9d700b10177225031d89bf3a813a1bd073fb0f05500bec00ee538874178308e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0001.bin` (mode 100644, SHA256 b4b1edf5242be38a8079fdd5657356181dbc76eb5ba63889f72b56f72ccea52a)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0002.bin` (mode 100644, SHA256 e888310d3f46c1bdbfc39a091ddeebd29c9173694da25db0132f654cbf775d37)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 2a3f8ab01afbc966c009052a0ec774972d9d8c0d9c500b958a18965baec4d0cc)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0004.bin` (mode 100644, SHA256 d85c1adf759d9913e05c2a4effbb47cf66b3f35a11d2f198c12a9497d7d96dba)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0006.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/kani_middle/kani_functions.rs` → `dependencies/0007.bin` (mode 100644, SHA256 c991f53c452f162f153880e178f728394e679d80b3175c226baec34f57b31773)
- `library/kani_core/src/mem_init.rs` → `dependencies/0008.bin` (mode 100644, SHA256 6ecd75e2497e3b43b059c5acb83ea593c8a917b6391971ce70e38d3132a16d46)
- `rust-toolchain.toml` → `dependencies/0009.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)
- `kani-compiler/src/intrinsics.rs` → `dependencies/0010.bin` (mode 100644, SHA256 53230c07d1950d5676ed320ca30430d0f99da7cd1ba9243441a1a576a4d54c83)
- `tools/compiletest/src/runtest.rs` → `dependencies/0011.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs` → `dependencies/0012.bin` (mode 100644, SHA256 70989e979e259cdfa5bfa0811cb53776f98a8ec1147c660ceec4e3f6d93b9186)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs` → `dependencies/0013.bin` (mode 100644, SHA256 354079ebb24304c7f8dc6516ba2e50dad70f0e30466f9660d17ecece01bc7277)
- `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs` → `dependencies/0014.bin` (mode 100644, SHA256 9f78de44ceffa0436de11ff3a4bf789c5d9909fe8425c7de543f84cd6c37fd91)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/rvalue.rs` → `dependencies/0015.bin` (mode 100644, SHA256 2dada4b5963c120ce8b7b20c514571b65b1f45b88b88ae70bf970b15763dd11a)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/intrinsic.rs` → `dependencies/0016.bin` (mode 100644, SHA256 bc0f72b9efb456a1d39a4c2ce19aaa62c675303ef80fc9a5323074a69ca5d6d1)
- `kani-driver/src/harness_runner.rs` → `dependencies/0017.bin` (mode 100644, SHA256 4ddabb49fcbc59990e1cce5b6d2985eae33d12724fe1efe2af2534cc4ba0f480)
- `tests/expected/uninit/maybe-uninit-transmute/main.rs` → `dependencies/0018.bin` (mode 100644, SHA256 a8447076a637799a4f2775d1fdbf46f5ffd8ec70721806b04d5d86ba65801c48)
- `tests/expected/uninit/maybe-uninit-transmute/expected` → `dependencies/0019.bin` (mode 100644, SHA256 994b01bceeaabaf3b99bf4b3b78cc81240e53648a96e316f887c04914752759f)
- `tests/expected/uninit/maybe-uninit-initialized/main.rs` → `dependencies/0020.bin` (mode 100644, SHA256 df6292d1fdc472cb41e6e7d707a6bc4f8b190a3f206a7f208e635a8d0b5f9e5c)
- `tests/expected/uninit/maybe-uninit-initialized/expected` → `dependencies/0021.bin` (mode 100644, SHA256 daa81fb42a5d5da64451b030dcd284678138909fbbdca5675c5caf7d78f8d89e)
- `tests/expected/uninit/maybe-uninit-partial-copy/main.rs` → `dependencies/0022.bin` (mode 100644, SHA256 52d4ef75b76aba6e84152188315d7e43aaa34bcc857429b6da9729259bbbb8f2)
- `tests/expected/uninit/maybe-uninit-partial-copy/expected` → `dependencies/0023.bin` (mode 100644, SHA256 86cd97e3e413fdd50e5da87c83acd815a528127db89d43d805a782cc225466db)
- `tests/expected/uninit/raw-eq-uninit/main.rs` → `dependencies/0024.bin` (mode 100644, SHA256 a0f781ed9650af8fe8b49460b9b3af2fb051de670931a2691eaf3561f784cd52)
- `tests/expected/uninit/raw-eq-uninit/expected` → `dependencies/0025.bin` (mode 100644, SHA256 7e342d3b17850f60ba204828dcfb431d6dfd44ec11aab6c1ec44ce51b6ca7698)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static only; runtime verification NOT_RUN; Cloud $0.

Do not execute source or evidence from this packet. Do not claim new proof credit.
