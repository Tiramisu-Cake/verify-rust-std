# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `585c93b2ff366f5723611a7ca944328ef62f40b5`
- Candidate: `c57314d4cf8aed4721c3170827827c6c9b9cd429`
- Candidate tree: `1985bfcdc80f2f864b56a8983ebc7e63652a1c55`
- Diff SHA256: `9fc942443b52a0092bf34665fe982c6c0bd6e1dcbf9f8ee5696fb8d0ea73f879`

## Defect

KANI3300 A3R: reported intrinsic Unsupported, invalid custom MIR, and extra uninitialized reads after A3.

## Applicability

Exactly TASK-KANI3300-A3R.md at research b9a4a9d60f893fc46db6e909426935a64c9a2e3c, inheriting TASK-KANI3300-A3.md; static source review only. Independently assess the patch, without author verdict.

## Invariants
- Audit intrinsic classification/can_skip_intrinsic/explicit models versus caller and callee transfer guards. Preserve unsupported non-Item/shim/bodyless shadow transfers; no blanket unknown-intrinsic skip.
- Audit complete argument/return protocol checks (signature/count/index/size/mandatory return0, no leftover current call state). Check changed written-count assertions and reachable transitive callees under the pinned std source.
- Audit Call(Move) reset and snapshot order: exact moved shadow place only; assignment/Copy/temp original/forget controls unchanged. Identify concrete extra-uninit causes if visible; do not infer runtime results.
- Audit custom MIR calls against pinned core::intrinsics::mir, Kani panic strategy, unchanged assertions/harnesses/goldens. Ensure error paths are not weakened.
- Clippy/-D warnings source audit: imports, locals, API signatures, type/borrow/exhaustiveness, formatting. No compiler execution.

## Required controls
- No builds/Cloud/dispatch/local cargo/rustc/Kani/CBMC/Miri/Actions/PR/issues/comments/push/raw logs/archives/credentials. Source reads/Python allowed. No nested delegation.
- Do not edit implementation or tests. Write only /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/a3r/REVIEW.md. Record candidate/tree/diff/spec identities, actionable findings and static limitations.
- No compilation/runtime/proof credit; fork CI belongs to coordinator. Pinned API source /tmp/kani3300-g1r-api, core MIR source /tmp/kani3300-b2b-source/library/core/src/intrinsics/mir.rs; research library core/cmp.rs is also available.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 a9d700b10177225031d89bf3a813a1bd073fb0f05500bec00ee538874178308e)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0001.bin` (mode 100644, SHA256 2657270bb4bed34dcbb3ac8a52a6137dff64da9aadb2fe22843ae701127708ae)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0002.bin` (mode 100644, SHA256 d85c1adf759d9913e05c2a4effbb47cf66b3f35a11d2f198c12a9497d7d96dba)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0003.bin` (mode 100644, SHA256 e888310d3f46c1bdbfc39a091ddeebd29c9173694da25db0132f654cbf775d37)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0004.bin` (mode 100644, SHA256 b4b1edf5242be38a8079fdd5657356181dbc76eb5ba63889f72b56f72ccea52a)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 dddbf5d1b29a398d79d4d2a8ad7f3e216dba4c22203bb75ade6fd6c8c8d8cc60)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs` → `dependencies/0006.bin` (mode 100644, SHA256 354079ebb24304c7f8dc6516ba2e50dad70f0e30466f9660d17ecece01bc7277)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0007.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/intrinsics.rs` → `dependencies/0008.bin` (mode 100644, SHA256 53230c07d1950d5676ed320ca30430d0f99da7cd1ba9243441a1a576a4d54c83)
- `kani-compiler/src/kani_compiler.rs` → `dependencies/0009.bin` (mode 100644, SHA256 7e6d3e1b08ae7b5efc0954c41079db0e515dad62b0072b9f7136ec3f6b9cc956)
- `kani-driver/src/call_single_file.rs` → `dependencies/0010.bin` (mode 100644, SHA256 3fc27b10a1db7705b514e7689e9c6e6b2f20516066664ad799b32f4adc23c996)
- `library/kani_core/src/mem_init.rs` → `dependencies/0011.bin` (mode 100644, SHA256 383f50193d267e4d7cf1a0fbf5ef36a9ad5adf626a8be5a9acc27bdf3b6a9150)
- `rust-toolchain.toml` → `dependencies/0012.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)
- `tests/expected/uninit/maybe-uninit-call-move/main.rs` → `dependencies/0013.bin` (mode 100644, SHA256 09d0ee03eb423f60f727bc004eb20698cc03412d3de6f104dc8b5c4735d0cbec)
- `tests/expected/uninit/maybe-uninit-call-move/expected` → `dependencies/0014.bin` (mode 100644, SHA256 b8a3c48787adbbc410957036dc20491c79004581d37113c2676416c520d7aa31)
- `tests/expected/uninit/maybe-uninit-call-pairing/main.rs` → `dependencies/0015.bin` (mode 100644, SHA256 e4adfcd3369a6787421c1792ea659ab6d4e195ad063927003bbcd85c446fd9d3)
- `tests/expected/uninit/maybe-uninit-call-pairing/expected` → `dependencies/0016.bin` (mode 100644, SHA256 336212bb2b499b05eb202c95a67b9b8183c3e85099f316b201d055585eb7146f)
- `tests/expected/uninit/maybe-uninit-call-pairing-unsupported/main.rs` → `dependencies/0017.bin` (mode 100644, SHA256 0b7441a2d1ef041c32364334a0535a566f324e4ca59d0dddb65137060feadb5d)
- `tests/expected/uninit/maybe-uninit-call-pairing-unsupported/expected` → `dependencies/0018.bin` (mode 100644, SHA256 01cbc989516b4a6d21a432a1a1c4bce3b7df00ae50c9e9ca158d52450a4693d9)
- `tests/expected/uninit/maybe-uninit-transfers/main.rs` → `dependencies/0019.bin` (mode 100644, SHA256 5587fdcd7436a63ccfed41747fc5c9ebc18ec74f46ef988d35c2e0877dba33d9)
- `tests/expected/uninit/maybe-uninit-argument-return/main.rs` → `dependencies/0020.bin` (mode 100644, SHA256 345db788d839c5f40fae3454d7ec8d1a8b805a208554a8fcad04ee53027ff9b9)
- `tests/expected/uninit/maybe-uninit-initialized/main.rs` → `dependencies/0021.bin` (mode 100644, SHA256 df6292d1fdc472cb41e6e7d707a6bc4f8b190a3f206a7f208e635a8d0b5f9e5c)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static only. Compilation/clippy/Kani/CBMC/Miri/CI NOT_RUN. Cloud $0.

Do not execute source or evidence from this packet. Do not claim new proof credit.
