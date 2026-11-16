# Profiles OFF batch runner

Runtime: Codex. Direct owner task; input g0 82cc48368e.
Read CH8-RUNNER-BATCH-NOTE.md; replace global list/per-row std invocation in control 6269319aec (source 9fa2f7f977) with cfg/RUSTFLAGS batches. Keep all62 manifest rows, selectors, oracles and row caps. Synthetic tests and independent Luna HIGH review; handoff only in this directory.

Control worktree: /root/kani-ch8-prof-off-w11; branch work/ch8-prof-off-batch-r2-w11.
No push, CI, ledger or local cargo/rustc/Kani/CBMC. Prior packages and source untouched. No CI/proof credit.
Exact identities/status: CI-REQUEST.json, CHECKPOINT.json, VALIDATION.json, REVIEW.json.

Outcome: READY_STATIC_REVIEWED_NOT_RUN;32 synthetic tests PASS; Luna HIGH GO, no findings.
