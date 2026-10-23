# Network N6 — RefinedRust G1: frontend admission of exact insert_tail, bounded experiment with exit criteria

Task ID: `network-refinedrust-g1-2026-10-24-n6`; previous task: `network-n13-exact-cloud-2026-10-24-n5`.
Owner: **Network**. Phase: `NETWORK-RR-G1-2026-10-24-N6`. Lane: `network-rr-g1`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Codex. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CODEX.md`](agent-workflow/RUNTIME-CODEX.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-networks` on branch `challenge-8/networks`; baseline `e8a21ed0797f69a97c6ec76ab90fad6fbaac3369`; source `cd371e035c7e573760c43bf934d53e8118ee3e7d`.
Tool worktree `/root/refinedrust-feasibility-sources/refinedrust-332d945fafa14bf55c0c8390cb35ec4b0c012cff` on `main` at `332d945fafa14bf55c0c8390cb35ec4b0c012cff`.
Profile `research/challenge-8/cloud-build/network-rr/RR-G1-PROFILE-20261024-N6.json` SHA-256 `31df48f177be20cfebab5683eb1d90c837b0b3668603a9555ab3dab607af1e34`. New ledger path: `research/challenge-8/cloud-build/network-rr/BUDGET-RR-G1-20261024-N6.json`; previous closed ledger: `research/challenge-8/cloud-build/network-n13/BUDGET-N13-20261024-N5.json`.
Cloud budget: 5400 seconds. Wall window: 4320 minutes main + 60 minutes closeout (explicit window authorized by this task only; CORE main/closeout rules apply to these deadlines). Per-Build timeout ≤1740 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

N6 and Builds authorized. Extended window: close on goal, budget or a real boundary, not on time (N6-OWNER-DIRECTIONS). Bounded RefinedRust experiment, not a migration: run the prepared stock G1 (unpatched RR 332d945f, nightly-2026-08-28) on exact core insert_tail and answer with GO_G2 / STOP_RR / INCONCLUSIVE by the recorded exit criteria. Tool here is RefinedRust; the stock VeriFast N13/R7 profile is untouched.

1. Transfer only the G1 package files from feasibility commit 68671873 into network/rr/; keep the RR pin 332d945f (read-only freshness check of upstream; re-pin only for documented slices/union support via restore-rr-bundle with reviewed hashes). Re-anchor annotations on baseline cd371e0; fall back to c7ca8c46 only with a recorded mismatch.
2. Register lane network-rr-g1 in the own client (R7-stage pattern): cold image recipe 1740/1800 (one attempt) and warm G1 recipe 1200/1260; branch-local machine/disk config only; no shared coordinator/IAM/fourth owner. Then one cold image Build if no compatible image receipt exists, one warm G1, at most one evidence-driven repair; classify the first causal failure.
3. Write network/rr/RR-G1-RESULT.md with the verdict, exact identities, first causal failure, missing specs and, for GO_G2, a G2 cost estimate; then STOP RR work. At the end re-check Select P2-INTERFACE for PUBLISHED; W7/W8 stay bounded.

## Special bounds

- Window deadlines exist only for ledger/watcher. Never shorten a timeout; setup error fixed statically, same config never repeated. After each terminal Build commit and push ledger accounting and CHECKPOINT/STATUS before the next step. Review once per semantic candidate; progress note about every 2 h.
- No RefinedRust frontend/semantics patch, no only_spec/shim/stronger FnMut/Copy/Freeze/purity premise, no Tool Application or CI integration. Generation or collector SUCCESS is not a safety PASS; proof credit 0 under every outcome; the readiness index does not change.
- Stock VeriFast 26.09 profile, coordination.py v4, shared coordinator/IAM/transport, other worktrees and ledgers unchanged; the feasibility branch is read-only history. No local RR build or verifier on the VPS.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: RR G1 never executed: compatible image and own lane registration missing.
Next: Transfer the G1 package, register lane network-rr-g1, cold image then warm G1 once, classify, write RR-G1-RESULT.md with GO_G2/STOP_RR/INCONCLUSIVE.

## References

- [Owner directions N6 (exit criteria)](network/rr/N6-OWNER-DIRECTIONS.md)
- [Draft RR G1 profile](cloud-build/network-rr/RR-G1-PROFILE-20261024-N6.json)
- [N5 handoff](network/n13/N5-HANDOFF.md)
- [Progress review §9](PROGRESS-REVIEW.md)

## Отчёт агента

**network-refinedrust-g1-2026-10-24-n6 · network · NETWORK-RR-G1-2026-10-24-N6 · NOT_STARTED**
Updated: 2026-10-23T20:13:24Z. Baseline source/tool/profile: `cd371e035c7e573760c43bf934d53e8118ee3e7d` / `332d945fafa14bf55c0c8390cb35ec4b0c012cff` / `31df48f177be20cfebab5683eb1d90c837b0b3668603a9555ab3dab607af1e34`.
Dates: T0 `NOT_SET`; main `NOT_SET`; absolute `NOT_SET`; window 4320 min main + 60 min closeout (explicit). Budget 5400s: 0s spent, 0s retired, 5400s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: RR G1 never executed: compatible image and own lane registration missing.
Next: Transfer the G1 package, register lane network-rr-g1, cold image then warm G1 once, classify, write RR-G1-RESULT.md with GO_G2/STOP_RR/INCONCLUSIVE.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
