# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`
- Candidate: `9dddcb1134f8a55ee3a4451df9513941ca3c8fc3`
- Candidate tree: `91608f7fd254e5588f4f0543439b58fd114b9d40`
- Diff SHA256: `7c4bd82927350f14bfb41703a83b922ccadd2b1eaf9326f41a5ce28d3034115f`

## Defect

B3 isolated upstream ZST union backend reduction; independently review tests-only dc590936c56556ecfb20fc714da06fcb13e884db and exact backend transplant of d760bad3639ea3a7c4000d41d5462508d5be14ef. Task: /root/verify-rust-std-kani3300-t0/research/challenge-8/kani-k1/TASK-KANI3300-B3.md @ 423b4721c864ee02936e43f7b46c2a05e92a1383. Revision: read AllZst.unit by reference after typed copy to remove dead-field warning risk; independently assess this delta.

## Applicability

Only B3, upstream base without G1. Static review; actual abort reproduction and fix acceptance await coordinator narrow CI at both commits.

## Invariants
- Only a zero-sized physical payload within a nonzero padded wrapper becomes the registered unit empty struct; logical UnionField type, padding width, non-ZST arms, all-ZST branch remain unchanged.
- cprover_bindings is already identical between upstream base and d760bad; do not invent changes there. Check logical/padded representation and field/index lowering compatibility.
- Test expectations must follow valid Rust semantics, never snapshot abort/Unsupported. No padding bytes read after typed transfer.

## Required controls
- Seven harnesses per mode (14 total): byte-covered array union, original padded C and Rust union shape, repr(align(8)) ZST, union at offset 8, all-ZST union, nondeterministic [();2] indexing with read/write/reference.
- Check sources identical except checks-on directive; full memset followed by typed ptr::write(&mut dst, ptr::read(&src)). Both expected files require 7 verified, zero failures.
- Clippy/-D warnings source audit only: no compiler invocations allowed; inspect imports, dead fields, mutability, unsafe usage, unit comparisons/bindings and backend borrow/signature use.

## Declared dependencies
- `cprover_bindings/src/goto_program/typ.rs` → `dependencies/0000.bin` (mode 100644, SHA256 ade325a1e884f3d6a648a64fe668c8f5e821c0ba42fcff419d4b2f9532b33871)
- `cprover_bindings/src/irep/to_irep.rs` → `dependencies/0001.bin` (mode 100644, SHA256 bda4f823aafe43d547476d540cf264e62293dc8693df861c65864566413d7b0c)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/place.rs` → `dependencies/0002.bin` (mode 100644, SHA256 0e39f6bcb6f8fdf6089e26f21dd5bfe21077d316b75a15ccde5cd2f1156f78b0)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/operand.rs` → `dependencies/0003.bin` (mode 100644, SHA256 c0a2b93a624cf4d5310f9fd61561bb1c3b92c1260da9fd6cf7ef9a363f009f8b)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/typ.rs` → `dependencies/0004.bin` (mode 100644, SHA256 87f14ac89df2f1990feff11cc7ca53f389adfc877a3463e951f4a9bc42b4d81f)
- `kani-compiler/src/codegen_cprover_gotoc/utils/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 7d9e1fbd8812ba7b0b2dee7170a47e99c31edb85edfde3e7f027417e2a7e7d26)
- `rustfmt.toml` → `dependencies/0006.bin` (mode 100644, SHA256 d1886a654a790b5f5779d12c770b32c5328e4e4eaa415fc3a024c6ba9df687b1)
- `.cargo/config.toml` → `dependencies/0007.bin` (mode 100644, SHA256 8a7317c9b5e38ee2e842086a154e99f9bae4e2bc1118cae9e5b7cd5ee7c3547c)
- `tools/compiletest/src/runtest.rs` → `dependencies/0008.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Forbidden: local cargo/rustc/Kani/CBMC, builds/dispatch/Cloud, raw logs/archives/credentials, Actions/PR/issues/comments, Kani push, stash; no network writes and no nested subagents.
- Rustfmt wrapper and Python allowed. Actual compilation/clippy/verification NOT_RUN. No runtime evidence or independent proof credit; coordinator handles CI.

Do not execute source or evidence from this packet. Do not claim new proof credit.
