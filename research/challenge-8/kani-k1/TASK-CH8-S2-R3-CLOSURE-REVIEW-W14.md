# W14 — independent source-trace / diagnostic-plan review

PREPARED_NOT_ISSUED; coordinator supplies exact committed W13 packet before issue.
Fresh idle14/current model/tier, Fast OFF; no subagents. STOP only real blocker.
Read TASK-CH8-S2-R3-CLOSURE-DIAG-W13.md for frozen inputs and scope.

Review the exact new r3-closure-diagnostic packet: stock macro generation and
contracts.rs lookup/caller/mode chain, S1/S2 source delta, all11 root/stub/provider
paths, distinguishing facts vs unobserved MIR, semantics of both workaround
proposals. Same error after normalization invalidates the earlier remedy; it
does not identify a different cause or explain historical r1 automatically.
If a bisect is needed, require small source-motivated variants, separating
predictions, controls, exact bindings, bounded error/debug reporting, stop/cost
boundaries and no unsupported free-run promise. No applied changes or CI credit.

Output only kani3300/ch8-s2/r3-closure-diagnostic-review/ (immutable):
REVIEW.md/json, exact-input hashes/manifest, HANDOFF. APPROVE or localized
CHANGES_REQUIRED with paths/evidence; unresolved scientific cause can be UNKNOWN
with a sound diagnostic plan. Review approval is not dispatch authority.
Findings to original13, immutable repair and same14 delta review; no source edits
by reviewer. No compiler/verifier/full runner/CI/rerun/cancel/push/PR/ledger/budget.
Ownpaths-only commit --only, [skip ci]. Final READY <full SHA> <verdict/blockers>.
