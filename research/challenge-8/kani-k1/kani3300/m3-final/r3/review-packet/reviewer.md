# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `aac27ed95364989bc045e5cdc227f2a97448f955`
- Candidate: `6c29e38c57fdf646bf07725c5c09008518d04255`
- Candidate tree: `cdc30da3c5327e8070ee4f61a42df37c9ea30104`
- Diff SHA256: `855881fe7dea86519548b4da7261da161bc7edf157e506ca2dadc687167dbcdc`

## Defect

Nested aggregate shadow transfer is absent; broad M3-R2 guard must not be carried into this branch.

## Applicability

Tests and user limitations only. Independent new branch directly from aac27ed95, not guard HEAD.

## Invariants
- Compiler, runtime, B1 unresolved-calls and closure-zst remain byte-identical to baseline.
- Top-level companion retains explicit Move, normal-edge return, source repair and both value assertions, plus no-repair negative.
- Existing tuple source remains intact apart from an explanatory comment. Legal failure is a known false positive, never UB detection credit.
- No claim that nested aggregate paths always fail closed; no ordinary-and-pointers-legal or guard boundary fixtures imported.

## Required controls
- Both top-level roots: legal expected SUCCESS returned=42/source=23, negative expected uninitialized u8 FAILURE.
- Tuple exact property/status/description and both failing-root summaries, 0 successful/2 failed roots.
- Unchanged B1, closure-zst, eight strong oracles, mode boundaries and shared validator.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0000.bin` (mode 100644, SHA256 ce6d36be2c059a04b1718afcf3bbb174550c2416d619b20b66211fbeab138ceb)
- `kani-compiler/src/kani_middle/transform/check_uninit/ty_layout.rs` → `dependencies/0001.bin` (mode 100644, SHA256 11a2ced7dc5df2e907a586018c42b4c949ca9dd86fd682aa33fa870a070a3c20)
- `tools/compiletest/src/runtest.rs` → `dependencies/0002.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)
- `kani-driver/src/harness_runner.rs` → `dependencies/0003.bin` (mode 100644, SHA256 4ddabb49fcbc59990e1cce5b6d2985eae33d12724fe1efe2af2534cc4ba0f480)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Only Python/static and authorized scratchpad rustfmt locally; no cargo/rustc/Kani/CBMC/push/CI.
- Top-level compile/proof and full CI NOT_RUN. Golden tuple observation supplied by task and existing STOP-R1.md, no new CI evidence.
- Expected-mode matcher uses unordered line groups; consecutive property/status/description and named failure summaries constrain observation but are not complete per-root inventories.

Do not execute source or evidence from this packet. Do not claim new proof credit.
