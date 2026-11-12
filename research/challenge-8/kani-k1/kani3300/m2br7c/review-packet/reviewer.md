# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c`
- Candidate: `fe36afc4a8de2709f00524b2d3fbd6da17919728`
- Candidate tree: `1f1ef86a7fb78fdc853862e6deca303458a05138`
- Diff SHA256: `a935f53ec2965349888343866ec9f4d85215e7a6c513a95fd30323cbc6d8c39e`

## Defect

Need discriminating P1/P2/private frame controls for coordinator qualification of separate private snapshot.

## Applicability

Only KANI3300 M2-B/R7-C input-validity/golden/coverage review; two new test selectors, no source changes.

## Invariants
- P1 byte-identical fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b
- Exactly four added files below private-transfer-frame; no existing controls weakened
- Inputs valid until intended read/write; semantic goldens independent of buggy base behavior; no guessed property IDs

## Required controls
- Review new lawful initialized transfer, scalar ensures and unchanged outside; Rust types/signatures/borrows and -Dwarnings
- Check reuse P2, outside-negative, clause-negative, false-state/protocol/move and M1/S3 coverage against task
- Compilation/runtime/root/property bindings remain NOT_RUN/UNKNOWN; no semantic proof from summary/golden

## Declared dependencies
- `library/kani_core/src/mem_init.rs` → `dependencies/0000.bin` (mode 100644, SHA256 383f50193d267e4d7cf1a0fbf5ef36a9ad5adf626a8be5a9acc27bdf3b6a9150)
- `library/kani_macros/src/sysroot/contracts/check.rs` → `dependencies/0001.bin` (mode 100644, SHA256 de97631cb1e6881361a66f5b0e3b633fd8162ea5171d918770315a5d5def951f)
- `library/kani_macros/src/sysroot/contracts/shared.rs` → `dependencies/0002.bin` (mode 100644, SHA256 a8df9244d86742adaf1bdfd991d1b6882962a6797b764d6824306f02024360e7)
- `rust-toolchain.toml` → `dependencies/0003.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)
- `rustfmt.toml` → `dependencies/0004.bin` (mode 100644, SHA256 d1886a654a790b5f5779d12c770b32c5328e4e4eaa415fc3a024c6ba9df687b1)
- `tests/expected/uninit/maybe-uninit-argument-buffer/main.rs` → `dependencies/0005.bin` (mode 100644, SHA256 09e5dd454f0cfcfeed1d9df436507c7d705270e85ee11592347113d58f9f1f55)
- `tests/expected/uninit/maybe-uninit-argument-return/main.rs` → `dependencies/0006.bin` (mode 100644, SHA256 345db788d839c5f40fae3454d7ec8d1a8b805a208554a8fcad04ee53027ff9b9)
- `tests/expected/uninit/maybe-uninit-call-move/main.rs` → `dependencies/0007.bin` (mode 100644, SHA256 09d0ee03eb423f60f727bc004eb20698cc03412d3de6f104dc8b5c4735d0cbec)
- `tests/expected/uninit/maybe-uninit-call-pairing/main.rs` → `dependencies/0008.bin` (mode 100644, SHA256 e4adfcd3369a6787421c1792ea659ab6d4e195ad063927003bbcd85c446fd9d3)
- `tests/expected/uninit/maybe-uninit-contract-clause/main.rs` → `dependencies/0009.bin` (mode 100644, SHA256 5fc89460489e7ac8dafe69f0ad722ae5d4d3a31776f945c0f78beda15aa38ad9)
- `tests/expected/uninit/maybe-uninit-contract-frame/expected` → `dependencies/0010.bin` (mode 100644, SHA256 778925cfde695f7899091ebab25513e7d755784dcbbd1ea92d844432bc8263ba)
- `tests/expected/uninit/maybe-uninit-contract-frame/main.rs` → `dependencies/0011.bin` (mode 100644, SHA256 f5c45585e405fe570d88eddb69b76b6299a04ebaba168cc08e2b36bb3bbb09c2)
- `tests/expected/uninit/transfer-qualification/postcondition-hole.rs` → `dependencies/0012.bin` (mode 100644, SHA256 61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759)
- `tools/compiletest/src/runtest.rs` → `dependencies/0013.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No local compiler/verifier; actual sysroot and macro expansion checked by coordinator CI
- Mixed16 fixed fixtures absent accepted base, exact existing test-only composition requested
- Existing frame var_N golden unchanged; owner updates only after actual outside-write binding

Do not execute source or evidence from this packet. Do not claim new proof credit.
