# Merge-R18 — raw caller frontier, RawPtr refinement and borrow

Task ID: `merge-raw-caller-frontier-autonomous-2026-10-22-r18`; previous task: `merge-caller-refinement-autonomous-2026-10-21-r17`.
Owner: **Merge**. Phase: `MERGE-RAW-CALLER-R18-2026-10-22`. Lane: `merge`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Claude Code. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CLAUDE.md`](agent-workflow/RUNTIME-CLAUDE.md), the compact root [CLAUDE.md](../../CLAUDE.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-merge-origin` on branch `merge/incoming-origin-20261009`; baseline `83cca35d25b6b26cd698e78bb6c605716c96df89`; source `6fd50c699500cbac5c65912174d4aa49b49db19f`.
Tool worktree `/root/verifast-merge-actual-glue` on `merge/actual-glue-instance-20261011` at `a66c1d30214e463a16a325cdef30b0ec8555e0af`.
Profile `research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json` SHA-256 `947be6e0ed9aa0d2270a820dd72e5ff4c78e8d30af3e55d7228b477af700026d`. New ledger path: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R18-BUDGET-20261022.json`; previous closed ledger: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R17-BUDGET-20261021.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥420 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R18 и Builds разрешены. Автономно продвигай actual Merge caller normal/unwind и original borrow/unsize по CORE; ближайшая цель — точная диагностика RawPtr refinement2 и raw caller frontier array_inv444 (array<u64>) с checked resource conversion. Bounded body отдельно от B2; продолжай до конца main или реальной границы.

1. Diagnose RawPtr positive refinement2 by Brief message/location and fix the raw array_inv444 frontier with checked resources; smallsort-reviewer review; register R18 via the branch client. Its authorization text cites independent review per runtime profile, not Luna.
2. Cloud raw caller normal/unwind with actual callee and exact source/stage/target receipts; then original as_mut_ptr/unsize via source-bound metadata, real borrow/lifetime and checked resource conversion. A raw adapter does not replace the original prefix/caller.
3. After blockers continue CURRENT/backedge, false/true/panic/Drop/Resume and the compatible final matrix; choose further useful steps yourself. If a full Cloud cycle no longer fits, finish Cloud-free stages of the next cycle (CORE).

## Special bounds

- Full plan timeout1200/execute<=780/soft<=765/reserve>=420 with nested compile reserve140; another plan only after effective-budget review/tests. After main only finish started work, no new Builds/retries/hypotheses.
- RawPtr matching: same mutability/pointee/place/full origin; no RawPtr<->Ref, address-only ownership, broad placeholders or new borrow/trusted premises. Keep the narrow R8 allocation boundary, posts and controls; new source-preserving fixes/profiles allowed.
- Original gate/raw caller/isolated body are different claims. Missing bindings => INCONCLUSIVE; bounded/source PASS is not B2/independent credit. Keep array11/R9, publication guards/caps and foreign dirty policy/guides. Blocker is Merge's, not maintainer's.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Original caller placeholders441/249; raw caller array_inv444 missing array<u64>; RawPtr positive refinement2 diagnostic OPEN. R17 CLOSED/main expired. (P4 exact raw frontier / P5 original caller) [Build 20e8009e-458e-45b1-9974-b0abfe716675]
Next: Diagnose RawPtr refinement2 and the raw array_inv444 frontier; review; register R18; Cloud raw caller; then original borrow/unsize and CURRENT/final matrix.

## References

- [Raw caller design / next contract](cloud-build/origin-layout/R16-RAW-CALLER-DESIGN-20261021.md)
- [Original caller borrowing boundary](cloud-build/origin-layout/R16-CALLER-DESIGN-20261021.md)
- [R17 release / pins](cloud-build/origin-layout/R17-RELEASE-20261021.json)

## Отчёт агента

**merge-raw-caller-frontier-autonomous-2026-10-22-r18 · merge · MERGE-RAW-CALLER-R18-2026-10-22 · HANDOFF**
Updated: 2026-10-22T14:43:00Z. Baseline source/tool/profile: `6fd50c699500cbac5c65912174d4aa49b49db19f` / `a66c1d30214e463a16a325cdef30b0ec8555e0af` / `947be6e0ed9aa0d2270a820dd72e5ff4c78e8d30af3e55d7228b477af700026d`.
Dates: T0 `2026-10-22T14:08:51Z`; main `2026-10-22T16:08:51Z`; absolute `2026-10-22T16:38:51Z`. Budget 3600s: 0s spent, 0s retired, 3600s remaining including reservations.
Active Build IDs: e70d2723-f49d-4a8f-847e-f8da1106d36f; unresolved: none recorded.
Blocker: RawPtr refinement2 = harness --check-first-fnmut-continue abort; array_inv444 = assert auto-close not retained. Fixes at 52cef788, unverified; P1 running. [Build `2256a4c8-2a4d-4a5c-8b61-a252730eae70`]
Next: Ack P1 e70d2723 watcher; Brief RawPtr controls/raw caller frontier; next cycle or original borrow/unsize.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
