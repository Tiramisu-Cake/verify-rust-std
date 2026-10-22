# Network N2: миграция coordinator v4 и поддержка network в smallsort-session

Task ID: `network-coordinator-v4-2026-10-22-n2`; previous task: `network-bootstrap-2026-10-22-n1`.
Owner: **Network**. Phase: `NETWORK-COORDINATOR-V4-2026-10-22-N2`. Lane: `network`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Claude Code. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CLAUDE.md`](agent-workflow/RUNTIME-CLAUDE.md), the compact root [CLAUDE.md](../../CLAUDE.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. This task has no Cloud lane: no coordinator request, phase registration, Build submission or proof execution. Commit reviewed candidates and handoff inputs for a later, separately authorized Cloud task.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-networks` on branch `challenge-8/networks`; baseline `71b4bdef37f17e7f03dea5756ade9107fd76842f`; source `cd371e035c7e573760c43bf934d53e8118ee3e7d`.
Tool worktree `/root/verifast-network` on `challenge8/network-20261022` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile: none (no Cloud lane). New ledger path: none; previous closed ledger: none (closed zero-budget task).
Cloud budget: 0 seconds (no Cloud lane). Wall window: 120 minutes main + 30 minutes closeout. T0 remains NOT_SET until actual work starts.

## Goal and steps

Owner-authorized: перевести live coordinator на v4 с владельцами select-sort4/merge/network (verifast выведен из Cloud решением владельца 2026-10-22), cap 3; установить клиент в Select/Merge/Network и добавить network в smallsort-session, чтобы следующее задание Network могло получить Cloud budget. Ни одного Build.

1. Finalize cloud-readiness: v4 owners exactly {select-sort4, merge, network} (verifast refused in v4), cap 3, owner check in request(), transition needs three ACKs plus an idle check (no reservations/requests/unresolved submits/active Builds) and a rollback path. Service tests, independent review on the exact commit.
2. smallsort-session (/root/verify-rust-std-evidence-brief, own branch docs/evidence-brief-policy-20261017 only): network in CLOUD_OWNERS, session_prepare (first Cloud session without previous ledger/profile), watch_bindings OWNER_REPOS; accept envelope v4/cap 3 in assignment._coordination_guard and watch_bindings (now v3-only), landed before step 3. Select/Merge behaviour and default render byte-identical; all tests pass; review. Also adopt ITERATION-PROCESS.md byte-identical from that worktree.
3. Live switch at a quiet boundary: confirm no agent runs in select-night/merge-origin and coordinator idle. Commit the identical coordination.py (only that path) into cloud-build of Select and Merge, and the Network client into its cloud-build; fast-forward push each; ACKs. Then audit, migrate, readback {4,3}, one status per client. Record before/after/READBACK/REVIEW like coordinator-v3-adoption-20261012. Remaining time: PREPARED_NOT_REGISTERED design moving the 14 unchanged library/core files out of the pinned-objects payload (pinned fetch, blob-ID check), chunk estimate per lane.

## Special bounds

- Budget 0: no Build/submit/request/reservation/phase registration. Exception: active.json only via the reviewed transition after the idle check; on any doubt stop before migrate.
- In select-night/merge-origin touch only cloud-build/coordination.py; foreign dirty files, ledgers, checkpoints and control.py stay. Merge push includes its local R19 commits (owner decision 2026-10-22), no submit. If v4 needs a control.py change, stop and report.
- verifast worktrees untouched; its v3 client fails closed. Push as a standalone fast-forward command, never force. No local rustc/Cargo/VeriFast/Kani, no GitHub Actions.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Network has no Cloud lane until coordinator v4 and smallsort-session support.
Next: Step 1: finalize v4 for three owners, then smallsort-session support, then the live switch.

## References

- [Cloud readiness plan](network/cloud-readiness/PLAN.md)
- [N1 closeout](task-history/network-n1/CLOSEOUT.md)
- [Bootstrap Network 2026-10-22](network/BOOTSTRAP-2026-10-22.md)

## Отчёт агента

**network-coordinator-v4-2026-10-22-n2 · network · NETWORK-COORDINATOR-V4-2026-10-22-N2 · CLOSED**
Updated: 2026-10-22T19:22:00Z. Baseline source/tool/profile: `cd371e035c7e573760c43bf934d53e8118ee3e7d` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `UNKNOWN`.
Dates: T0 `2026-10-22T18:43:36Z`; main `2026-10-22T20:43:36Z`; absolute `2026-10-22T21:13:36Z`. Budget 0s: 0s spent, 0s retired, 0s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: Coordinator done; Network has no registered phase/recipe/ledger yet (budget 0 here).
Next: Next task with budget: prepare and register NETWORK-R4 phase/recipe/ledger, import common runner files at a pinned Select commit, run R4/W7 matrices.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
