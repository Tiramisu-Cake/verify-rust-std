# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `69b13711e60a87458200833445d47488ab466344`
- Candidate: `9f321df1af6afd5c2e61b4eb698831a5a670caae`
- Candidate tree: `ed7ad01540b93b1883fcb3034dcbf6044a042210`
- Diff SHA256: `da68e357cb099633963439dd5611e33e5b09368f73e8b9106144a81e2715fa2a`

## Defect

Different AllocId keys for one emitted allocation may carry different frozen-origin qualification and spuriously conflict in Descriptor equality.

## Applicability

C2-S2 only: exact descriptor compatibility and qualification merge, register unit controls and direct/nested immutable reference expected fixtures.

## Invariants
- Combine qualification only for exact allocation equality (Option bytes, extent, align, mutability, provenance), identical mask and layout.
- False-to-true and true-to-false registration must preserve the same exact object and qualification; genuine admitted conflicts return Err without mutation.
- Keep whole-object supported Freeze or exact static source qualification, immutable/no-relocations admission, seal, canonical binding, target checks and reset-completion seeding.
- Preserve unrelated unqualified-conflict policy; no mutable blessing, subrange or relocation support, runtime or body-cache changes.

## Required controls
- Review unit matrix for both orderings, repeats, neither qualifying, Some(0)/None, actual storage conflicts and no overwrite after Err.
- Review four one-harness expected fixtures: minimal direct/nested use and reversed order, plus volatile companions. Own assertions SUCCESS, zero failures and final SUCCESS.
- No local compiler/verifier/test runs are permitted. Source coalescing and qualification require future coordinator baseline/candidate CI inspection; no observed fatal is claimed.

## Declared dependencies
- `kani-compiler/src/codegen_cprover_gotoc/context/immutable_allocations.rs` → `dependencies/0000.bin` (mode 100644, SHA256 3cffeefeb8992c0ea41ce33afb17c4ae1d59bef9794b4e992fb58abf177202be)
- `kani-compiler/src/kani_middle/anonymous_allocations.rs` → `dependencies/0001.bin` (mode 100644, SHA256 daacc82f429cbf3d21e877731ddbb34c55e21ef788e05d177da8656b22baeea8)
- `kani-compiler/src/codegen_cprover_gotoc/codegen/operand.rs` → `dependencies/0002.bin` (mode 100644, SHA256 add9326d0250c7645ac8570bca1357d94072e9182ea64f1c2bf1a908fd99860f)
- `kani-compiler/src/codegen_cprover_gotoc/context/goto_ctx.rs` → `dependencies/0003.bin` (mode 100644, SHA256 cf0433855bf460b679d6202effbece3dcdd4d2f920cff274b53e359cfeb21957)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0004.bin` (mode 100644, SHA256 1371e9059e45cff62f8be3d5323cc866ce74a4e67a6f3e69bf98372462bd3853)
- `kani-driver/src/cbmc_property_renderer.rs` → `dependencies/0005.bin` (mode 100644, SHA256 f2f6be1b2a2e29e340e17c5859fa5a0f5c7d90bacb9287d082af23d442737c42)
- `rust-toolchain.toml` → `dependencies/0006.bin` (mode 100644, SHA256 8ae6767838d7384b2b764bda9262793d4861a798e49e57dc965fe37ead8e65df)
- `rustfmt.toml` → `dependencies/0007.bin` (mode 100644, SHA256 d1886a654a790b5f5779d12c770b32c5328e4e4eaa415fc3a024c6ba9df687b1)
- `kani-dependencies` → `dependencies/0008.bin` (mode 100644, SHA256 94bfe751e4574561519bd26a99196280eb018c30d9db408416b231ddb6f8b7bc)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static review only. No cargo/rustc/rustfmt/Kani/CBMC/Miri/builds, push, CI or Cloud; do not spawn agents.
- Synthetic descriptor cases are unit-only and cannot establish real-source AllocId/provenance binding. Actual coalescing UNKNOWN until CI; absent coalescing is NONDISCRIMINATING.
- S1 composition JSON drift remains deferred to S5; F6/F7/SEL1 and all later C2 work are out of scope.

Do not execute source or evidence from this packet. Do not claim new proof credit.
