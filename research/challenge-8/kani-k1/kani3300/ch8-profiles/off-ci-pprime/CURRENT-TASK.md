# Worker11 — Profiles P′ rebase

Runtime: Codex. Direct task TASK-CH8-PPRIME-REBASE.md, g0 input34fb6ac876.
Scope: cherry-pick872d..b5cf722e20 onto P′, rebind OFF control, exclude target/ from upload, static validation and independent review.
Source worktree: /root/verify-rust-std-ch8-profiles-w11, branch work/ch8-profiles-pprime-w11.
Control worktree: /root/kani-ch8-prof-off-w11, branch work/ch8-prof-off-pprime-w11.
Cloud budget:0; no push/CI/ledger/local cargo/rustc/Kani/CBMC.
Production #752, prior packages and historical evidence unchanged. New CI/proof results NOT_RUN.
Exact identities and handoff: CI-REQUEST.json; validation: VALIDATION.json; independent review: REVIEW.json.

Outcome: READY_SOURCE_AND_OFF_CONTROL_PPRIME; Luna HIGH GO_STATIC_REVIEW_ONLY, no findings; static checks and 26 synthetic tests PASS; proof/CI NOT_RUN.
