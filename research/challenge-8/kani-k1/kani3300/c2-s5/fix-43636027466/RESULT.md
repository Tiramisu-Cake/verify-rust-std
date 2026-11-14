# READY 8d67298c48eb7b2381f806a6353433d1440e3d94

Fix parent 6d2e9ae621310605eda4b0c9572d34d9a7ff948d; branch fix/kani-3300-c2-s5, tree 5fb7dbaa6f79a75ca552be9d4d5c7b535cf38058.
Local source commit author Tiramisu-Cake <igkharin@gmail.com> via git -c; worktree clean.

Restore required local full-domain proof_for_contract(passthrough) companion in both
Replace inputs. Exact caller flags select replace_transfer or replace_transfer_uninitialized,
respectively; selected roots, original bodies/contracts/domains and goldens N2/N0 unchanged.
Exception explicitly authorized/documented:20 source-single-harness inputs and2 source-two-harness
inputs, all22 execute one selected root. Separate SimpleCheck oracle remains intact.

Requested rustfmt, diff whitespace, exact-source/companion/selection/golden audits PASS.
All4 sensitivity patches unchanged byte-for-byte and apply to corrected source; mutated input
hashes unchanged. Existing manifest already includes --force-rerun; prior sensitivity attempt
INVALID/skipped, not detection. Original source-full.patch preserved; separate source-fix.patch
extends it, exact final tree reconstructed in isolated Git index.

Prior CI43636027466 on6d2e9ae621: fmt/build/clippy PASS, units6/2/9, kani24/0,
expected226ok/2compile failures, ui17/0, script2/0, remaining JSON17/0 (owner summary).
New fix native build/verification/CI, valid sensitivity runs and push NOT_RUN. Research uncommitted.
Mixed-inventory limitation and post-S6/freeze three-platform gate unchanged; no S6 work.
