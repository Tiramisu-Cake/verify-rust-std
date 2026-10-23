# Select-R23 — leak repair R22b, приёмка fractional callee, controls, P2

Task ID: `select-callee-acceptance-autonomous-2026-10-23-r23`; previous task: `select-callee-acceptance-autonomous-2026-10-23-r22`.
Owner: **Select/sort4**. Phase: `SORT4-ACTUAL-SELECT-2026-10-23-R23`. Lane: `o26-select-callee-r20`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Codex. Follow CORE and RUNTIME-CODEX (review and watcher).
T0 includes preparation. Use smallsort-session; review and register exact phase before Builds.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-select-night` on branch `research/night-select-sort4-cloud-2026-10-09`; baseline `cb364c5be02b759e436f1d2af056215636bcc172`; source `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db`.
Tool worktree `/root/verifast-select-sort4-c2-bind-20261010` on `challenge8/select-sort4-c2-bound-20261010` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile `research/challenge-8/cloud-build/sort4-caller-entry-native/A1-ACTUAL-C3-R19-PROFILE-2026-10-22.json` SHA-256 `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`. New ledger path: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-23-R23.json`; previous closed ledger: `research/challenge-8/cloud-build/sort4-caller-entry-native/BUDGET-A1-ACTUAL-SELECT-2026-10-23-R22.json`.
Cloud budget: 3600 seconds. Wall window: 120 minutes main + 30 minutes closeout. Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

R23 и Builds разрешены. Цель — довести checked actual callee select_unpredictable (W1) до приёмки: устранить последний leak (R22b), закрепить controls, прогнать normal/unwind/nested-Drop; затем P2 (*mut T) для Network и маршрут в sort4. Закрыв план или упёршись в границу, агент сам ставит следующие задачи по миссии.

1. Register R23 reusing the R22 route-marker pattern. Early: R22b fingerprint Build at HEAD, rebind r22b rows from it, restore the proof entry, review, proof Build. Before the second cycle consider a reviewed way to shorten fingerprint→rows (fewer Brief requests, static binding test) without weakening the checks.
2. On a clean positive: re-observe and pin the seven control targets (CONTROL-TARGET-PROPOSAL, omit-* at lib.rsspec:462/463), then normal/unwind/nested-Drop, ownership, leak/refinement and same-site controls; record callee acceptance only on the full matrix. Without Cloud in parallel: *mut T chain (MUTABLE-GATE-INVENTORY) and P2 publication to Network.
3. Then the dormant body route (BODY-C5-NEXT, 168/191) after acceptance/linkage and count-five requalification. When the plan is done or blocked, pick next obligations yourself from COMPLETION-PLAN/mission (W1/W4), recording choice and reason in CHECKPOINT; else prepare a reviewed HANDOFF.

## Special bounds

- Proof Builds use timeout 1200; never shorten it to fit the remaining window: if the full envelope does not fit main, no Build. A compile error or a run without proof stage is fixed statically first; never repeat the same config. No new Build/retry after main; the 30 min only for started Builds, evidence, accounting, checkpoint, push. No cap change.
- Keep R16-R22 chain and strict R13 checks (5 calls/8 selects/4 copies, no leak relaxation). Beyond the owner-approved fractional candidate, any gate exemption, guard-own=true or broad forget summary needs an owner decision. No address-only bridge. Tool WT: pinned Git objects. coordination.py (v4) read-only.
- Use the whole main window; no admissible Build is not a boundary. An early stop lists each checked independent task and why it is unavailable in closure_reason.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Positive fails only function-end leak of 2 pointer-value own chunks (constructor results); omit-* target unpinned.
Next: New window: R22b fingerprint (HEAD), rebind r22b rows, proof; see NEXT-WINDOW-HANDOFF.

## References

- [R22 next-window handoff](task-history/select-callee-r22/NEXT-WINDOW-HANDOFF.md)
- [Leak repair next](task-history/select-callee-r22/LEAK-REPAIR-NEXT.md)
- [Control target proposal](task-history/select-callee-r22/CONTROL-TARGET-PROPOSAL.json)
- [Completion plan](COMPLETION-PLAN.md)

## Отчёт агента

**select-callee-acceptance-autonomous-2026-10-23-r23 · select-sort4 · SORT4-ACTUAL-SELECT-2026-10-23-R23 · HANDOFF**
Updated: 2026-10-23T08:14:13Z. Baseline source/tool/profile: `81226dafedd2e8d1dfb140ab0e4dd88556bfd7db` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `d4b1b7350d9a9966bedfd0ef50e4c7f7b4cc071ca1f6c4e08d44ba85c36ed622`.
Dates: T0 `2026-10-23T07:37:19Z`; main `2026-10-23T09:37:19Z`; absolute `2026-10-23T10:07:19Z`. Budget 3600s: 311s spent, 0s retired, 3289s remaining including reservations.
Active Build IDs: e25a96d4-25c0-416f-a55c-debb87baacb1; unresolved: none recorded.
Blocker: Positive fails only function-end leak of 2 pointer-value own chunks (constructor results); omit-* target unpinned.
Next: Ack proof watcher before checkpoint changes; Brief e25a96d4 positive/7controls. On clean positive pin full diagnostic targets and matrix. Mutable delta review17142 pending; target helper remains inactive.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
