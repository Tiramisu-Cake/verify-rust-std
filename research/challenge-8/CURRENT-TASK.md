# Merge-R22 — Cloud HANDOFF tool578/profile9496 по admission e70c9115, raw caller controls, borrow/unsize

Task ID: `merge-caller-acceptance-autonomous-2026-10-23-r22`; previous task: `merge-caller-acceptance-autonomous-2026-10-23-r21`.
Owner: **Merge**. Phase: `MERGE-CALLER-ACCEPTANCE-R22-2026-10-23`. Lane: `merge`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Codex. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CODEX.md`](agent-workflow/RUNTIME-CODEX.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-merge-origin` on branch `merge/incoming-origin-20261009`; baseline `fd4281a5f89cf313bc6d977cc401d2faa9e32909`; source `6fd50c699500cbac5c65912174d4aa49b49db19f`.
Tool worktree `/root/verifast-merge-actual-glue` on `merge/actual-glue-instance-20261011` at `578120769161e217e53bd569bafdccbd4b2e020e`.
Profile `research/challenge-8/cloud-build/origin-layout/GLUE-PROFILE.json` SHA-256 `949633103e909f27a721573ae88f4d3180278de5bcc2c60031239f93fe0b0301`. New ledger path: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R22-BUDGET-20261023.json`; previous closed ledger: `research/challenge-8/cloud-build/origin-layout/CURRENT-RECOVERY-R21-BUDGET-20261023.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥420 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R22 и Builds разрешены. Цель — Cloud-проверка reviewed HANDOFF 41d449f3 (tool 57812076, profile 9496), приёмка raw caller с controls (F5, state, index), затем исходный as_mut_ptr/unsize caller с actual borrow lifecycle и матрица CURRENT/normal/unwind. Закрыв план или упёршись в границу, агент сам ставит следующие задачи по миссии.

1. Re-register as R22 on the reviewed R21 admission e70c9115 (R21-ADMISSION-REVIEW; delta review of the R22 registration only); recheck pins and transport margin. Cloud preflight, then early one full-envelope Build: raw caller target, five R19 controls, state/index controls on the new tuple; classify by exact receipts. A compile error or a run without proof stage (R20 P3/P4) is fixed statically first; never repeat the same config.
2. By result: F5 as a real verifier negative (not a setup failure), intended state-context and index-projection controls; then original as_mut_ptr/unsize: owned NLL fact capture, source-bound borrow/reference lifecycle and checked resource conversion in the same admitted domain.
3. Then CURRENT/backedge, false/true/panic/Drop/Resume and the final matrix on compatible pins. When the plan is done or blocked, pick next obligations yourself from COMPLETION-PLAN/mission (W2/W3/W5), recording choice and reason in CHECKPOINT; if a Cloud cycle does not fit, prepare a reviewed HANDOFF.

## Special bounds

- Envelope timeout1200/execute<=780/soft<=765/reserve>=420, nested compile reserve140. Never shorten a timeout to fit the remaining window: if the full envelope does not fit main, no Build. No new Build/retry after main; the 30 min only for started Builds, evidence, accounting, checkpoint, push. Measure transport before each submit; no cap increase.
- RawPtr: same mutability/pointee/place/full origin; no RawPtr<->Ref, address-only ownership, broad placeholders or new borrow/trusted premises. Keep the R8 allocation boundary, posts and controls. cloud-build/coordination.py is the owner-adopted v4 client: do not edit it.
- Raw caller, original caller and isolated body are separate claims; missing bindings => INCONCLUSIVE; no B2/independent credit. Use the whole main window; an early stop lists each checked independent task and why it is unavailable in closure_reason.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: R21 lost to permission stall, 0 Builds; tool578 admission pending.
Next: New task: re-register on reviewed e70c9115; HANDOFF Build t1200 early.

## References

- [R21 admission design](cloud-build/origin-layout/R21-ADMISSION-DESIGN-20261023.md)
- [R21 admission review](cloud-build/origin-layout/R21-ADMISSION-REVIEW-20261023.json)
- [R20 closeout](cloud-build/origin-layout/R20-CLOSEOUT-20261023.json)
- [R20 caller and control frontier](cloud-build/origin-layout/R20-CALLER-AND-CONTROL-FRONTIER-20261023.md)
- [Completion plan](COMPLETION-PLAN.md)

## Отчёт агента

**merge-caller-acceptance-autonomous-2026-10-23-r22 · merge · MERGE-CALLER-ACCEPTANCE-R22-2026-10-23 · HANDOFF**
Updated: 2026-10-23T08:38:26Z. Baseline source/tool/profile: `6fd50c699500cbac5c65912174d4aa49b49db19f` / `578120769161e217e53bd569bafdccbd4b2e020e` / `949633103e909f27a721573ae88f4d3180278de5bcc2c60031239f93fe0b0301`.
Dates: T0 `2026-10-23T07:44:00Z`; main `2026-10-23T09:44:00Z`; absolute `2026-10-23T10:14:00Z`. Budget 3600s: 354s spent, 0s retired, 3246s remaining including reservations.
Active Build IDs: fb2529be-bf1d-4721-8632-4c5493e2fedd; unresolved: none recorded.
Blocker: Build active.
Next: Brief.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
