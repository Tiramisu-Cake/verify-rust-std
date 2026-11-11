# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `29bde289d60d9f6f36c16310f6bce697338f7641`
- Candidate: `d5f072f2bcf61a04d84bb0e8b54115f3011252fc`
- Candidate tree: `04377e8281fbe53bb3110904181125d378601783`
- Diff SHA256: `53920de4030ab0eb9b61ed5321350c6e464138634091a6c41d512f7b63edc2ae`

## Defect

Independently review the test-only B1R2 delta against TASK-KANI3300-B1R2.md at research e88d0ca43508f72d6b2b67ea40ac2b16603bcdd7. B1 and B1R task constraints remain applicable.

## Applicability

Exactly four changed test files for pending-ops plain/seeded fixtures and shim plain/seeded expected output. No production changes.

## Invariants
- Keep the Call-operand dereference check and explicit unresolved-call diagnostic; do not weaken the pending-ops named expectations.
- Fixtures must avoid raw-pointer/union interaction and expose an uninitialized byte before the unresolved call; retain plain/seeded distinction.
- Shim goldens must require the specific bodyless Shim failure and failed harness summary from the task report, using compiletest substring/consecutive-line semantics.
- No change to other controls, production, or previous stage artifacts. Check edition/features and possible -D warnings hazards statically.

## Required controls
- pending-ops pair named indirect.safety_check uninitialized-u8 failure and function-pointer Unsupported expectations unchanged.
- shim pair specific Failed Checks: bodyless Shim diagnostic, VERIFICATION:- FAILED and 0 successful / 1 failure summary.
- Static review only; do not equate source or synthetic matcher checks with compilation or executed test evidence.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0000.bin` (mode 100644, SHA256 805f4705a10f1b462e231407239a0de0095b7fb652860f9b76cd8a8863fd8951)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs` → `dependencies/0001.bin` (mode 100644, SHA256 0f32763a6981ae6269d4b938302ac106ff6ebaa19df9fa413765a982f1390277)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0002.bin` (mode 100644, SHA256 487138ede144c9cea764b1da8562a90525cfdcab7ba110e044d46a3b75ce502e)
- `tools/compiletest/src/runtest.rs` → `dependencies/0003.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)
- `kani-driver/src/cbmc_property_renderer.rs` → `dependencies/0004.bin` (mode 100644, SHA256 20b95bbc09cd7a7342e3cc9ebf14f7a6f173b7bdbf8726bd13d6de40c9aab175)
- `tests/expected/uninit/unresolved-calls/pending-ops-plain.expected` → `dependencies/0005.bin` (mode 100644, SHA256 a98cba93c04805a857c52b571a41e93a9fb459dc3ba606dba7d91153258cc01c)
- `tests/expected/uninit/unresolved-calls/pending-ops-seeded.expected` → `dependencies/0006.bin` (mode 100644, SHA256 a98cba93c04805a857c52b571a41e93a9fb459dc3ba606dba7d91153258cc01c)
- `tests/expected/uninit/unresolved-calls/shim-plain.rs` → `dependencies/0007.bin` (mode 100644, SHA256 edc9b55561880314cb4f2c2b9d7c036e8786b96c466790db4cacdd7225654fba)
- `tests/expected/uninit/unresolved-calls/shim-seeded.rs` → `dependencies/0008.bin` (mode 100644, SHA256 0029daf69fe41bf0de6e86c2aeb23b35881bcadbb25065a3bf3badb6cca6b0a6)
- `tests/expected/uninit/alloc-to-slice/alloc-to-slice.rs` → `dependencies/0009.bin` (mode 100644, SHA256 039e6f79b17b20e11c7896d9df011299f3d345abc13754c10492e8051230414e)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No builds/dispatch/Cloud/Actions or local cargo/rustc/Kani/CBMC. No raw logs/archives/credentials, network writes, Kani push or nested delegation. Python and authorized rustfmt wrapper allowed. Task CI facts are source-reported, not independently reproduced.

Do not execute source or evidence from this packet. Do not claim new proof credit.
