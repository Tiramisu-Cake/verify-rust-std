# Select-R22 — fractional callee 288fa7cd, controls/matrix, *mut T, маршрут в sort4

Task ID: `select-callee-acceptance-autonomous-2026-10-23-r22`; previous task: `select-callee-acceptance-autonomous-2026-10-23-r21`.
Owner: **Select/sort4**. Phase: `SORT4-ACTUAL-SELECT-2026-10-23-R22`. Lane: `o26-select-callee-r20`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Claude Code. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CLAUDE.md`](agent-workflow/RUNTIME-CLAUDE.md), the compact root [CLAUDE.md](../../CLAUDE.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-select-night` on branch `research/night-select-sort4-cloud-2026-10-09`; baseline `f8ef054f4c31e3edeb1a5ea76c8f3adbf48fbb6b`; source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`.
Tool worktree `/root/verifast-select-sort4-c2-bind-20261010` on `challenge8/select-sort4-c2-bound-20261010` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json` SHA-256 `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`. New ledger path: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-23-R22.json`; previous closed ledger: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-23-R21.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R22 и Builds разрешены. Цель — приёмка checked actual callee select_unpredictable (W1) через одобренный fractional-кандидат 288fa7cd: positive, controls, normal/unwind/nested-Drop; затем *mut T (P2 для Network) и маршрут в sort4. Закрыв план или упёршись в границу, агент сам ставит следующие задачи по миссии.

1. Statically recheck 288fa7cd (patch, translator pins, 113-part transport) per NEXT-WINDOW-HANDOFF, register R22, then early one full-envelope Build of the fractional positive and eight-row matrix. Optionally first: reviewed bootstrap stage receipts in control.py::config so a timeout shows its stage.
2. By result: pin callee control targets (site, message, stage, fields; now TARGET_UNPINNED), then normal/unwind/nested-Drop, ownership, leak/refinement and same-site omission controls. In parallel without Cloud: *mut T/generic unit (MUTABLE-CALLEE-NEXT) and a pinnable P2 answer for Network.
3. Then the dormant body route (BODY-C5-NEXT, 168/191) after callee acceptance/linkage and count-five control requalification. When the plan is done or blocked, pick next obligations yourself from COMPLETION-PLAN/mission (W1/W4), recording choice and reason in CHECKPOINT; else prepare a reviewed HANDOFF.

## Special bounds

- Proof Builds use timeout 1200; never shorten it to fit the remaining window: if the full envelope does not fit main, no Build. A compile error or a run without proof stage is fixed statically first; never repeat the same config. No new Build/retry after main; the 30 min only for started Builds, evidence, accounting, checkpoint, push. No cap change.
- Keep R16-R21 chain and strict R13 checks (5 calls/8 selects/4 copies, no leak relaxation). Beyond the owner-approved fractional candidate, any gate exemption, guard-own=true or broad forget summary needs an owner decision. No address-only bridge. Tool WT: pinned Git objects. coordination.py (v4) read-only.
- Use the whole main window; no admissible Build is not a boundary. An early stop lists each checked independent task and why it is unavailable in closure_reason.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Actual fractional callee proof UNKNOWN: corrected retry exited124 with incomplete stage evidence; acceptance and controls remain open.
Next: New authorized window/ledger: use NEXT-WINDOW-HANDOFF; recheck288fa7cd, then checked fractional proof and exact controls.

## References

- [R21 next-window handoff](task-history/select-callee-r21/NEXT-WINDOW-HANDOFF.md)
- [Fractional forget proposal (owner-approved)](task-history/select-callee-r21/FRACTIONAL-FORGET-PROPOSAL.md)
- [Completion plan](COMPLETION-PLAN.md)

## Отчёт агента

**select-callee-acceptance-autonomous-2026-10-23-r22 · select-sort4 · SORT4-ACTUAL-SELECT-2026-10-23-R22 · ACTIVE**
Updated: 2026-10-23T00:03:00Z. Baseline source/tool/profile: `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`.
Dates: T0 `2026-10-22T22:25:06Z`; main `2026-10-23T00:25:06Z`; absolute `2026-10-23T00:55:06Z`. Budget 3600s: 967s spent, 0s retired, 2633s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: Positive fails only function-end leak of 2 pointer-value own chunks (constructor results); omit-* target unpinned.
Next: LEAK-REPAIR-NEXT: bind constructor chunks, ghost open; fingerprint, pins, proof.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
