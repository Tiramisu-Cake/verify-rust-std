# Bounded candidate review packet

Review the exact committed candidate named below.
This packet is a review handoff only: it grants no proof credit, admission, or authorization.

- Baseline: `55d704a56dbd5864ffb75e3d861a544c281f8ebd`
- Candidate: `14c0a3c95b6ece62b01f96f663b455f8c5e155dc`
- Candidate tree: `8af499c3fb6c1108614e57c6ba446f66435c7d34`
- Diff SHA256: `8c7241c5a51d0dbf07da391f4bba6b89b53984a7ef556632e15412139dc1c93b`

## Defect

A3 union control correction: take raw address of byte field rather than casting pointer-to-union and seeding unrelated delayed-UB union checks.

## Applicability

Test-only continuation of review-tests-packet. Only byte-pointer source observation changes; no semantic implementation change. Review final custom MIR source/golden with all prior semantic/test dependencies.

## Invariants
- Same predicate must gate caller StoreArgument and callee LoadArgument. Reject bodyless/shim/non-Item shadow transfers early with Unsupported; no initialized fallback if no current protocol. Check instance/signature identity, count, ordered indices, selected-payload size, completion, obligatory return0, no state leaked across nested/repeated same-size calls.
- For shadow storage union/MaybeUninit Call Move, snapshot witness while live before deinit, then full-extent deinit source, including padding. Callee must preserve pre-move false bytes, not reread reset shadow. Copy/assignment/field assignment/forget/temp-original storage must retain intended semantics. Ordinary union returns should pair too.
- Audit insertion order and interaction with delayed-UB pass, pointer checks and marked verifier-private state / DFCC. Check guard reachability and existing checks preserved; identify scope limitations rather than broadening to B1.
- Audit Rust API/types/borrowing/exhaustive matches, macro feature compatibility, unused imports/code, clippy/-D warnings statically using pinned /tmp/kani3300-g1r-api. No compilation or local tools beyond Python and permitted rustfmt. Check compiler-context Ty::to_index as protocol identity under actual transform lifecycle.

## Required controls
- No nested delegation. No builds/Cloud/dispatch/cargo/rustc/Kani/CBMC/Miri/Actions/PR/issues/comments/Kani push/raw logs/archives/credentials. Do not browse network.
- No implementation edits. Write only /root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/a3/REVIEW.md. Report exact candidate/tree/diff/spec identities, actionable findings and static verdict/limits.
- No compilation/runtime/proof credit. Main will submit test-only controls after fixture worker finishes.

## Declared dependencies
- `tests/expected/uninit/maybe-uninit-call-move/main.rs` → `dependencies/0000.bin` (mode 100644, SHA256 73d7347ac7e1a9f6dc6e550ffe83b9c35711656481f68ba376859e05eead7ff0)
- `tests/expected/uninit/maybe-uninit-call-move/expected` → `dependencies/0001.bin` (mode 100644, SHA256 1d7926aeacf734436516c27ab83845a7caf5a5cc5bd3addceceb72e8dedcc132)
- `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs` → `dependencies/0002.bin` (mode 100644, SHA256 70989e979e259cdfa5bfa0811cb53776f98a8ec1147c660ceec4e3f6d93b9186)
- `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs` → `dependencies/0003.bin` (mode 100644, SHA256 d391ef37e2ba51a4b867881cb7f80f638a41daaf214de9452fda005ed724f6be)
- `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs` → `dependencies/0004.bin` (mode 100644, SHA256 46214010ffc67f498e6c175d700aac8b4f042c6747eca9eb1e782bba981c56f1)

## Scope and limitations

The packet includes the complete baseline-to-candidate Git diff and every changed path. Deleted paths are identified in metadata. Local dirty and untracked files are excluded.
Start with `metadata.json` and `inventory.json` for the compact scope and identities. Review the listed changed files and declared dependency snapshots, then consult the complete `diff.patch` where needed; the full patch is retained for inspection and need not be read all at once.
A successful `review check` means only that packet structure and committed inputs match. It is not reviewer approval, a GO decision, evidence validation, or formal verification credit.
Prior review references are handoff pointers only. A prior decision applies only when its candidate digest and baseline match; dependency changes invalidate it.

- Static only. Coordinator fork CI owns compilation and measured verification. A3 shadow-storage domain uses preexisting transfers_shadow type recognition.

Do not execute source or evidence from this packet. Do not claim new proof credit.
