# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `46e46583ff112cae9c43aea1ba5dd6145e5e8387`
- Candidate: `b6f1b08eb512ff9006aff7b4924c2e8f13930d70`
- Candidate tree: `c426f0cb9be59838d217d2ec68334cbcbd9721ac`
- Diff SHA256: `66afd4a2960e45b54320c348c87f7ef925f52c15e8279a340596cab8c23ca358`

## Defect

Real std intrinsic rejected because rendered FnDef name is std re-export; long fixture artifact name and rustfmt failures in supplied quick43605855700.

## Applicability

Exact narrow classifier identity fix and control/format repairs; no local builds/push/CI.

## Invariants
- Only canonical core::intrinsics::select_unpredictable, intrinsic kind/name, usable non-overridden body, exact signature, checked_body and sized existing masks.
- Do not broaden other intrinsic/refusal domains, change runtime shadow protocol, body owner, alias modeling, masks or F5/F6/F7.
- Retain29 exact controls; rename only long overwrite selector; add core/std direct path assertion in scalar root; preserve actual failure/refusal counts.
- Replay3bb04079537dc4611d5e214586a291966905e018 binds exact new source/tree and unchanged std6075e7ce17, same six ON rows/profile/branch/serial/no-retry.

## Required controls
- Owner rustfmt wrapper and --check pass; git diff --check clean. New runtime outcomes NOT_RUN.
- 29 replay Python service tests pass; delta rebuilt and --check pass. Generator Python tests rerun on final package.

## Declared dependencies
- `kani-compiler/src/kani_middle/reachability.rs` → `dependencies/0000.bin` (mode 100644, SHA256 3070ac455b25d8c96204d54f8fbe43a53890aa7847d31deb3aee2021f98a6499)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs` → `dependencies/0001.bin` (mode 100644, SHA256 c0729827d6bb585e974dbb4b2ebf1078ecb9e829af8d9ecdc722921cfa994d7c)
- `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs` → `dependencies/0002.bin` (mode 100644, SHA256 9857ce811b154b1211ba8430eccc5bfeab7b59e6454851c2d6ce61b963235a1d)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0003.bin` (mode 100644, SHA256 11a2ced7dc5df2e907a586018c42b4c949ca9dd86fd682aa33fa870a070a3c20)
- `rust-toolchain.toml` → `dependencies/0004.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- User-supplied quick excerpts only; no CI rerun or independent proof credit.
- Existing composition FAIL debt remains unchanged. Research uncommitted.

Do not execute source or evidence from this packet. Do not claim new proof credit.
