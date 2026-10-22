# Select-R21 — accept the actual select_unpredictable callee, *mut T, then the sort4 route

Task ID: `select-callee-acceptance-autonomous-2026-10-23-r21`; previous task: `select-actual-callee-autonomous-2026-10-22-r20`.
Owner: **Select/sort4**. Phase: `SORT4-ACTUAL-SELECT-2026-10-23-R21`. Lane: `o26-select-callee-r20`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Codex. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CODEX.md`](agent-workflow/RUNTIME-CODEX.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-select-night` on branch `research/night-select-sort4-cloud-2026-10-09`; baseline `44bfbdecdd61c96059fe76d8b8bff690e15dd5d6`; source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`.
Tool worktree `/root/verifast-select-sort4-c2-bind-20261010` on `challenge8/select-sort4-c2-bound-20261010` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json` SHA-256 `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`. New ledger path: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-23-R21.json`; previous closed ledger: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-22-R20.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R21 и Builds разрешены. Цель — приёмка checked actual callee core::hint::select_unpredictable (W1): positive за lib.rsspec:462, controls, normal/unwind/nested-Drop; затем *mut T/generic (P2 для Network) и маршрут в actual sort4 (c5, селекторы, копирования).

1. Build HANDOFF 0f37a0df (S2d fingerprint) on o26-select-callee-r20, then the branch-selected refresh and classified proof. Fix the payload identity lost on guard re-open (own(t,g) has no payload) by a checked step; each repair close needs a control failing at the same site. Then the callee matrix normal/unwind/nested-Drop.
2. *mut T: the same unit at *mut T or a generic proof (ACTUAL-GENERIC-SELECT-GAP). Answer Network SELECT-REQUESTS (branch challenge-8/networks): adopt or reject P1 (c760fa3b, overlay c14d8f8a) with reasons, decide the P3 marker grammar; commit the answer as a file Network can pin.
3. Transport: each new route gets its own lane with a minimal closure inventory; shrink a1-runner.py and drop the duplicate selected-proof.py recipe path. Then the opt-in route into the actual sort4 body with source/MIR certification, Cloud c5 (34e37669), selectors, copies.

## Special bounds

- Keep the R16/R17/R19/R20 chain and strict R13 checks (5 calls/8 selects/4 copies, no leak relaxation). Callee summary only from a checked actual callee of the same version; gate exemption, guard-own=true or a broad forget summary need an owner decision. No cap change: the transport limit is the Cloud Build API (191 parts).
- Tool WT has foreign edits: pinned Git objects, isolated WT. Operands: checked equality or checked case split, never an address-only bridge. cloud-build/coordination.py is the owner-adopted v4 client: do not edit it.
- Use the whole main window; no admissible Build is not a boundary. An early stop lists each checked independent task and why it is unavailable in closure_reason.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Wrapper own closed for new(true_payload) but selected cell holds new(selected_payload) after guard re-open.
Next: New window: build HANDOFF 0f37a0df S2d fingerprint on o26-select-callee-r20; then branch-selected refresh + classified proof.

## References

- [Callee route design (R20)](task-history/select-callee-r20/CALLEE-ROUTE-DESIGN.md)
- [S3b Cloud evidence](task-history/select-callee-r20/S3b-evidence.json)
- [R20 review](task-history/select-callee-r20/R20-review.json)
- [Generic select gap](overnight-assume-actual/ACTUAL-GENERIC-SELECT-GAP-2026-10-09.md)
- [c5 candidate review](task-history/select-c3-r19/C5-review.json)

## Отчёт агента

**select-callee-acceptance-autonomous-2026-10-23-r21 · select-sort4 · SORT4-ACTUAL-SELECT-2026-10-23-R21 · HANDOFF**
Updated: 2026-10-22T20:24:49Z. Baseline source/tool/profile: `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`.
Dates: T0 `2026-10-22T19:54:55Z`; main `2026-10-22T21:54:55Z`; absolute `2026-10-22T22:24:55Z`. Budget 3600s: 322s spent, 0s retired, 3278s remaining including reservations.
Active Build IDs: 1bbfc87e-8b0a-4042-b54f-71acb3690dd6; unresolved: none recorded.
Blocker: Wrapper own closed for new(true_payload) but selected cell holds new(selected_payload) after guard re-open.
Next: Ack watcher for Build1bbfc87e, then Brief rows -> checked repair/controls; same R21 window. See task-history/select-callee-r21.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
