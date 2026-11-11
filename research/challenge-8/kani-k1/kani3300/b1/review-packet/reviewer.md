# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `bf9c58e662fd65c64381ef2ac97a6397ffc0693a`
- Candidate: `835cb4a09c4e94ac6b531d20e68f9deee7262ce1`
- Candidate tree: `4b426d96a0dc2f5b87bdbfe1c32f0e492e8461f3`
- Diff SHA256: `393f826b0f4d8552e3ec12cc4938aa43a2e774ee4b55d0ec1a28031b9dddf8b5`

## Defect

Unresolved Call drops current_target and repeats super_terminator; non-Item instances can escape classification. Review the B1 candidate independently against TASK-KANI3300-B1.md.

## Applicability

Only upstream uninitialized-memory call handling and its regression controls. No memory-model extensions, builds, dispatch, or Kani publication.

## Invariants
- Exactly one super_terminator per Call; retain entry loads and collected operand operations on resolution error.
- Every instance kind has an explicit supported or Unsupported policy.
- One pass owns fn-pointer/virtual diagnostics regardless of delayed-UB seeds; do not weaken checks.

## Required controls
- Empty entry block with union argument loads, initialized/partial controls; pending operand checks at unresolved Call.
- FnPtr, erased/wrapped pointer, virtual, global/escaped, shim, direct positive; each with and without added delayed-UB seed.
- Audit Rust warning hazards under -D warnings; local compilation is forbidden.

## Declared dependencies
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs` → `dependencies/0000.bin` (mode 100644, SHA256 acd93cd4351eaff1ba8365ccc2298b560854aa9c95311204203a3c3485afa971)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/mod.rs` → `dependencies/0001.bin` (mode 100644, SHA256 92b632cabff031938ffc2abf9fef276193ac68184edf6f65c0d8722ee87ae00c)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs` → `dependencies/0002.bin` (mode 100644, SHA256 0f32763a6981ae6269d4b938302ac106ff6ebaa19df9fa413765a982f1390277)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0003.bin` (mode 100644, SHA256 487138ede144c9cea764b1da8562a90525cfdcab7ba110e044d46a3b75ce502e)
- `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs` → `dependencies/0004.bin` (mode 100644, SHA256 326ddfe7b112e88f61f7af8606d433fc8be29fe959565ad3b4071a875f8230a9)
- `kani-compiler/src/kani_middle/transform/mod.rs` → `dependencies/0005.bin` (mode 100644, SHA256 c9b0f47bc79751ab906c443243750ae840311d87c78924147a6765df94971339)
- `kani-compiler/src/kani_middle/transform/body.rs` → `dependencies/0006.bin` (mode 100644, SHA256 930636ad1ab2290fb2b10f1970f2283f6e29c52de9a7b1696c7767c041a469d5)
- `tests/expected/uninit/delayed-ub-unsupported-call/main.rs` → `dependencies/0007.bin` (mode 100644, SHA256 b464e866a3ce94fcb20589e16b47c74589ef821ea2f7ed7e2666febf63aac1fd)
- `tests/expected/uninit/delayed-ub-unsupported-call/expected` → `dependencies/0008.bin` (mode 100644, SHA256 7008546b9c6963fdc4e6c0507852732014aaf7abf7ef05423d7a9c0806d9e89c)
- `tools/compiletest/src/runtest.rs` → `dependencies/0009.bin` (mode 100644, SHA256 dad67ded3379bcf7d3cce0e4e500159fa0c25ee513ba515f13647d5c688e394f)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- No local cargo/rustc/Kani/CBMC, builds, Actions, Cloud, raw logs/archives, credentials, or network writes. Compiler execution and measured results are reserved to coordinator fork CI.
- Source inspection and goldens are expectations, not measured false SUCCESS or proof credit.

Do not execute source or evidence from this packet. Do not claim new proof credit.
