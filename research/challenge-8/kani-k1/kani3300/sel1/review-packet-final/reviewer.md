# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `69b13711e60a87458200833445d47488ab466344`
- Candidate: `27eba17c1d2503233dfe525da9fdb2df31685226`
- Candidate tree: `90fc9accd5ac43de45db77ad4fe3db5280ce12f9`
- Diff SHA256: `656f274f86f8e75f9e4ec8768a78b44807ac3b6f2b43b5ed75203746ed7264e7`

## Defect

Uninit local visitor rejects standard select_unpredictable while codegen executes its fallback; points-to misses aliases from that fallback.

## Applicability

Only exact standard intrinsic with usable non-overridden fallback, (bool,T,T)->T, sized existing masks; TASK-KANI3300-SEL1.md F8 contract. Static correctness review, no local compiler/verifier/CI.

## Invariants
- Fallback body is sole selected-byte transfer owner; do not union runtime initializedness or bless pointees.
- Caller/callee agree on paired argument indices/count/signature, return0 only on normal return; snapshots precede deinit of both actual Move arms, Copy retains sources.
- Preserve operand/raw/union checks and pending B1 operations; reject unsupported body/layout before partial protocol/deinit.
- Points-to follows same body and reaches referents of both arms without condition edge or extra arm-slot indirection.
- No changes to runtime buffers, DFCC, std algorithms, fn-pointer/trait-object refusal, general alias resolution, nested type support or F5/F6/F7.

## Required controls
- 29 exact native selectors in CONTROL-MANIFEST.json (12 SUCCESS/17 intended negatives proposed); all outcomes NOT_RUN.
- Six named std ON rows in CI-REQUEST.json/TARGET-GATE-MAP.md; separate std test overlay6075e7ce17179f45642c9ffe8fe09e3ec9395726.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 1371e9059e45cff62f8be3d5323cc866ce74a4e67a6f3e69bf98372462bd3853)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0001.bin` (mode 100644, SHA256 e888310d3f46c1bdbfc39a091ddeebd29c9173694da25db0132f654cbf775d37)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0002.bin` (mode 100644, SHA256 11a2ced7dc5df2e907a586018c42b4c949ca9dd86fd682aa33fa870a070a3c20)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0003.bin` (mode 100644, SHA256 ce499e6ba49657ff9469927fa69eb6ff368457c613825e493a053cfc4d9a1a2b)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs` → `dependencies/0004.bin` (mode 100644, SHA256 ecc52ea5051460be8be2bdfbff17e94d0f62fa0f7e292854c1e8ce21e3764970)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/instrumentation_visitor.rs` → `dependencies/0005.bin` (mode 100644, SHA256 53064d8de9417f1c2ffb33675a5679767a4e6e14052f0dfff233e38739408217)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0006.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `kani-compiler/src/kani_middle/transform/mod.rs` → `dependencies/0007.bin` (mode 100644, SHA256 8dc76ebe25ce1e05db3a98613011ed3258280ef57c2be336ab84ed97f7f46ba8)
- `kani-compiler/src/kani_middle/transform/contracts.rs` → `dependencies/0008.bin` (mode 100644, SHA256 06523bc56804fae5a4e6b484ef4e2ecedf34dbc046b29e02608e9ccdb3660cc9)
- `kani-compiler/src/kani_middle/points_to/mod.rs` → `dependencies/0009.bin` (mode 100644, SHA256 d0c9169a1c1f1476f1bdd5ef6d42040ed4587b9a86bb2891a1b312568aa98128)
- `library/kani_core/src/mem_init.rs` → `dependencies/0010.bin` (mode 100644, SHA256 383f50193d267e4d7cf1a0fbf5ef36a9ad5adf626a8be5a9acc27bdf3b6a9150)
- `rust-toolchain.toml` → `dependencies/0011.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No local builds, cargo/rustc/Kani/CBMC/Miri, push or CI. New outcomes NOT_RUN.
- Port to final C2 and new freeze/gates required later. No inherited proof credit for production delta.

Do not execute source or evidence from this packet. Do not claim new proof credit.
