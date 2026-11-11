# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `3dc0227cee87d85bed32678a2209353ebdb9d2fa`
- Candidate: `85fc5cd2ca770cdc5ae1bb514c27b6da7b6d9b18`
- Candidate tree: `d178157e35b45f84afd17b86027e667716c17344`
- Diff SHA256: `b1145bb4737be6381226349344a6a3fb87c83f756f04dc7f363252b01671cedd`

## Defect

KANI3300 A2R: raw_eq must check every byte of both referenced pointees rather than reject supported layouts.

## Applicability

Review only A2R delta and required dependencies. Contract: TASK-KANI3300-A2R.md at research commit 3d5ce04887. Independent static source review; no author verdict supplied.

## Invariants
- Both raw_eq reference operands must be checked over the full size_of::<T>() extent, including padding and MaybeUninit storage. Unsupported only when pointee layout cannot be computed. Inspect pointer casts and generated masks, shadow setup, initial target selection and effects on existing initialized array equality.
- Pat offsets and enum variant-local layout comparison must remain unchanged. Existing maybe-uninit-transmute, maybe-uninit-initialized, maybe-uninit-partial-copy goldens must remain unchanged.
- Inspect fixture reachability: arrays fully initialized succeed; exactly one uninitialized byte fails on raw_eq, both operand positions; padding checks remain covered. Explain whether old transmute failures arise from fixture/rustc simplification or A2 code. No unrelated failures accepted as evidence.
- Audit Rust API, types, imports, borrowing, unused code and clippy/-D warnings statically using pinned /tmp/kani3300-g1r-api and g1r/API-SOURCES.json. No compilation. Check expected harness order/diagnostics/counts against runner source.

## Required controls
- No nested delegation; no builds/Cloud/dispatch/cargo/rustc/Kani/CBMC/Miri/Actions/PR/issues/comments/raw evidence/credentials/network mutations/Kani push.
- No code/test edits. Write only /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/a2r/REVIEW.md. Report exact candidate/tree/diff/spec identities, actionable findings, static verdict and limits.
- No proof/compilation/runtime credit. CI outcomes are unmeasured expectations for the coordinator.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 f7ace04066f08093822061f24568a0688e1d373b4e75bd5248e86f0667eac68e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0001.bin` (mode 100644, SHA256 faa4e5692c295612771e5b7f384d6ce1913155f77941d9e8b4cc046aa990e451)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0002.bin` (mode 100644, SHA256 db408ef3264acfad8245ac52d7f3aa2e658578edce611552ef29d19b8729f28e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 0a351bf31991931407c9ed4c4427713bcf94db14b5735ad17c0a0789686168e8)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0004.bin` (mode 100644, SHA256 503b2c0f60762313b6f61b4308f154a90c459b3a4370aeb4ba2aa4e4a7aef6ba)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0006.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/kani_middle/kani_functions.rs` → `dependencies/0007.bin` (mode 100644, SHA256 4fc4ef480440d05432e1f5b2245be83bd7c70b3cd547c57442c901457feb3ab4)
- `library/kani_core/src/mem_init.rs` → `dependencies/0008.bin` (mode 100644, SHA256 9ff043b57ff6aed633815bc35a185c7cdf1a94d24356c95bb74679438081c0ce)
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

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static only; no builds or local compilers are authorized.

Do not execute source or evidence from this packet. Do not claim new proof credit.
