# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `aac27ed95364989bc045e5cdc227f2a97448f955`
- Candidate: `a221d00cf66b723c66a5a3a928d2ab1e29e8df44`
- Candidate tree: `d79bd6fe8a8e4d76ea639792c2beff8031b3c502`
- Diff SHA256: `6ad8e26dead3af11ccb5335640426ca17bafd53f5ca8e6a42b3b42c348c98da6`

## Defect

Nested shadow carriers lack aggregate transfer at call boundaries.

## Applicability

Uninit visitor admission, user scope documentation, supported Move/return pair and isolated boundary controls only.

## Invariants
- Existing flat predicates/protocol and unsized guard remain unchanged.
- Reject nested argument/return before transfer effects; no new runtime/layout model.
- Preserve both repaired-source23 and returned42 assertions and deliberate no-reinit hole.

## Required controls
- Boundary tuple/struct/array/enum/closure/ZST/foreign controls and supported flat/pointer/Forget controls.
- Existing two-operand/mixed/masks, source-following false, frame/clause, eight strong oracles, CC1-CC4 unchanged.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0000.bin` (mode 100644, SHA256 11a2ced7dc5df2e907a586018c42b4c949ca9dd86fd682aa33fa870a070a3c20)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0001.bin` (mode 100644, SHA256 1371e9059e45cff62f8be3d5323cc866ce74a4e67a6f3e69bf98372462bd3853)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0002.bin` (mode 100644, SHA256 e888310d3f46c1bdbfc39a091ddeebd29c9173694da25db0132f654cbf775d37)
- `kani-compiler/src/kani_middle/points_to/mod.rs` → `dependencies/0003.bin` (mode 100644, SHA256 d0c9169a1c1f1476f1bdd5ef6d42040ed4587b9a86bb2891a1b312568aa98128)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static review only; no local cargo/rustc/Kani/CBMC/builds, no push.
- New compile/proof results NOT_RUN; Cloud $0, CI and push coordinator only.
- Check existing generated/RustCall/closure paths and exact diagnostics; do not bless broad rejection or source-panic fallback.
- Delta since initial review: unresolved calls now diagnose nested actual arguments/destination before resolution Unsupported; boundary expectations also require nested-slot reason. Review only that delta against prior review.

Do not execute source or evidence from this packet. Do not claim new proof credit.
