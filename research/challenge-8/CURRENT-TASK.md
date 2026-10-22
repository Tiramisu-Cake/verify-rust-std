# Merge-R19 — checked unwind cleanup on the raw caller, then original borrow/unsize

Task ID: `merge-unwind-cleanup-autonomous-2026-10-22-r19`; previous task: `merge-raw-caller-frontier-autonomous-2026-10-22-r18`.
Owner: **Merge**. Phase: `MERGE-UNWIND-CLEANUP-R19-2026-10-22`. Lane: `merge`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Claude Code. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CLAUDE.md`](agent-workflow/RUNTIME-CLAUDE.md), the compact root [CLAUDE.md](../../CLAUDE.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-merge-origin` on branch `merge/incoming-origin-20261009`; baseline `17fe08b5b4ed5b09c1d08bf56537c3d474c4ed05`; source `6fd50c699500cbac5c65912174d4aa49b49db19f`.
Tool worktree `/root/verifast-merge-actual-glue` on `merge/actual-glue-instance-20261011` at `a66c1d30214e463a16a325cdef30b0ec8555e0af`.
Profile `research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json` SHA-256 `947be6e0ed9aa0d2270a820dd72e5ff4c78e8d30af3e55d7228b477af700026d`. New ledger path: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R19-BUDGET-20261022.json`; previous closed ledger: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R18-BUDGET-20261022.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥420 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R19 и Builds разрешены. Цель — реализовать узкий checked unwind cleanup hook из дизайна R18 для вызова insert_tail в raw caller и пройти raw caller normal/unwind на Cloud; затем исходный as_mut_ptr/unsize, borrow/lifetime и final matrix по миссии.

1. Implement the R18 next-window contract (R18-RAW-CALLER-DESIGN): source-bound ghost block on the Continue unwind edge of that insert_tail call only, failing closed otherwise; 4 distinguishing controls (missing marker, other call/function, Cleanup edge, no r9_drop_u64_owners); service tests; tool commit, profile/patch pins, prove.py admission; smallsort-reviewer; register R19.
2. Cloud raw caller normal+unwind with the actual insert_tail callee and exact receipts; then original as_mut_ptr/unsize via source-bound metadata, real borrow/lifetime and checked resource conversion; LocalAddressTaken negative and index projection control.
3. Then CURRENT/backedge, false/true/panic/Drop/Resume and the final matrix; pick further useful steps yourself; Cloud-free stages if a cycle no longer fits (CORE).

## Special bounds

- Full plan timeout1200/execute<=780/soft<=765/reserve>=420, nested compile reserve140. After main only started work. An unfinished tool commit/review or no admissible Build is not a boundary; an early stop lists each checked independent task in closure_reason (CORE).
- RawPtr matching: same mutability/pointee/place/full origin; no RawPtr<->Ref, address-only ownership, broad placeholders or new borrow/trusted premises. Keep the narrow R8 allocation boundary, posts and controls; new source-preserving fixes/profiles allowed.
- Original gate/raw caller/isolated body are different claims. Missing bindings => INCONCLUSIVE; bounded/source PASS is not B2/independent credit. Keep array11/R9, publication guards/caps and foreign dirty policy/guides. Blocker is Merge's, not maintainer's.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Raw caller unwind free_locals needs array_ at verified461; needs checked source-bound unwind cleanup (tool). R18 CLOSED early at real boundary. (raw caller verified461 free_locals) [Build e70d2723-f49d-4a8f-847e-f8da1106d36f]
Next: Implement the R18 unwind cleanup rule with its four controls and service tests; review; register R19; Cloud raw caller normal/unwind.

## References

- [R18 raw caller design / unwind contract](cloud-build/origin-layout/R18-RAW-CALLER-DESIGN-20261022.md)
- [P1 result](cloud-build/origin-layout/R18-PROOF1-RESULT-20261022.json)
- [P2 RawPtr controls](cloud-build/origin-layout/R18-PROOF2-RESULT-20261022.json)
- [R18 review](cloud-build/origin-layout/R18-REVIEW-20261022.md)
- [Original caller borrowing boundary](cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md)

## Отчёт агента

**merge-unwind-cleanup-autonomous-2026-10-22-r19 · merge · MERGE-UNWIND-CLEANUP-R19-2026-10-22 · HANDOFF**
Updated: 2026-10-22T17:05:00Z. Baseline source/tool/profile: `6fd50c699500cbac5c65912174d4aa49b49db19f` / `a66c1d30214e463a16a325cdef30b0ec8555e0af` / `947be6e0ed9aa0d2270a820dd72e5ff4c78e8d30af3e55d7228b477af700026d`.
Dates: T0 `2026-10-22T16:08:18Z`; main `2026-10-22T18:08:18Z`; absolute `2026-10-22T18:38:18Z`. Budget 3600s: 0s spent, 0s retired, 3600s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: Reviewed R19 candidate 3a587cb7 not submitted: push denied by classifier; owner chose no push/submit.
Next: Owner-approved push of merge/incoming-origin-20261009, then R19 P1 (raw caller + 5 controls, timeout1200), wait; then original as_mut_ptr/unsize.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
