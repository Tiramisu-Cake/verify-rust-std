# Select-R20 — actual select_unpredictable callee and the sort4 selector path

Task ID: `select-actual-callee-autonomous-2026-10-22-r20`; previous task: `select-c3-callback-autonomous-2026-10-22-r19`.
Owner: **Select/sort4**. Phase: `SORT4-ACTUAL-SELECT-2026-10-22-R20`. Lane: `o26-sort4-c1-current-recovery`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Claude Code. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CLAUDE.md`](agent-workflow/RUNTIME-CLAUDE.md), the compact root [CLAUDE.md](../../CLAUDE.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-select-night` on branch `research/night-select-sort4-cloud-2026-10-09`; baseline `10e13a414a1b6f0efafdee36eea733c91df1ee6b`; source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`.
Tool worktree `/root/verifast-select-sort4-c2-bind-20261010` on `challenge8/select-sort4-c2-bound-20261010` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json` SHA-256 `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`. New ledger path: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-22-R20.json`; previous closed ledger: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-C3-2026-10-22-R19.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R20 и Builds разрешены. Цель — checked proof actual callee core::hint::select_unpredictable (вариант 1 SELECT-NEXT-DESIGN). Это W1 твоей миссии, решение внутри миссии, не выбор владельца. Generic по T, если возможно: покрывает *const T (sort4) и *mut T (swap_if_less, потребитель Network). Затем маршрут в actual sort4, c5 и копирования.

1. Re-check the S7 blocker (forget guard-own at std/lib.rsspec:420, frozen dead-code gate) on the current R17/R19 chain; a diagnostic Build is fine. Design a route deriving guard-own from the actual DropOnPanic construction, without a gate exemption; implement, review, Cloud.
2. Transport plan: commit closure pruning of closed routes (R17 profile, R16-only files) with closure inventory and review so c5 (192 chunks) and the selector overlay fit. No cap change without the owner.
3. Once the callee is accepted: opt-in route into the actual body with source/MIR certification, then Cloud c5 (34e37669), selectors, copies; count-independent c3/c4 control re-qualification on final pins.

## Special bounds

- Keep the R16/R17/R19 chain and strict R13 checks (5 calls/8 selects/4 copies, no leak relaxation). select_unpredictable summary only with a checked actual callee of the same version; gate exemption, guard-own=true or broad forget summary need an owner decision.
- Tool WT has foreign edits: pinned Git objects, isolated WT. Operands: checked equality or checked case split, never an address-only bridge.
- Use the whole main window: no admissible Build is not a session boundary; continue Cloud-free stages. An early stop must list in closure_reason each checked independent task and why it is unavailable.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: No such function: std::hint::select_unpredictable; actual callee proof (S7 select thread) not accepted, so no summary allowed. (verified/lib.rs(371,19-55) first selector) [Build 8916761a-a0a7-428a-b853-187e45ef4dfa]
Next: Перепроверить forget guard-own на текущей цепочке, спроектировать путь callee без исключения из gate; параллельно — план transport.

## References

- [Selector next design](task-history/select-c3-r19/SELECT-NEXT-DESIGN.md)
- [S2 Cloud evidence](task-history/select-c3-r19/S2-evidence.json)
- [c5 candidate review](task-history/select-c3-r19/C5-review.json)
- [Forget blocker (historical S7)](SORT4-SELECT-FORGET-RESULTS.md)
- [Select callee thread](SORT4-SELECT-CALLEE.md)

## Отчёт агента

**select-actual-callee-autonomous-2026-10-22-r20 · select-sort4 · SORT4-ACTUAL-SELECT-2026-10-22-R20 · HANDOFF**
Updated: 2026-10-22T16:49:00Z. Baseline source/tool/profile: `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`.
Dates: T0 `2026-10-22T15:41:28Z`; main `2026-10-22T17:41:28Z`; absolute `2026-10-22T18:11:28Z`. Budget 3600s: 738s spent, 0s retired, 2862s remaining including reservations.
Active Build IDs: 729474f9-3acf-4d52-a04d-9ffb16e1fb5a; unresolved: none recorded.
Blocker: Missing MaybeUninit_pointer_own(t, new(payload)) for select arg a; repair needs certificate-refresh tool patch. [Build `2d562718-c166-4ab5-bba3-bf9136bd56b7`]
Next: Wait R20 S2b Build 729474f9 (merged-variant fingerprint, pins 912b3f4e); ack; take SHA/unit/body-7 and MIR counts; S3 certificate refresh (draft ready).
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
