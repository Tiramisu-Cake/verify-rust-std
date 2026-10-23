# Network N5 — order/universal для exact N13, затем перенос R7 на baseline cd371e0 в stock-профиле

Task ID: `network-n13-exact-cloud-2026-10-24-n5`; previous task: `network-n13-exact-cloud-2026-10-23-n4`.
Owner: **Network**. Phase: `NETWORK-N13-EXACT-2026-10-24-N5`. Lane: `network-n13`.

## Mission

This is a bounded continuation of the previous task under a newly authorized window.

Runtime: Codex. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CODEX.md`](agent-workflow/RUNTIME-CODEX.md), the compact root [AGENTS.md](../../AGENTS.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. Prepare fresh-session inputs with `/usr/local/bin/smallsort-session`, obtain required independent review and register the exact phase through the assigned branch client before proof work. Registration does not restart the clock.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-networks` on branch `challenge-8/networks`; baseline `9a7a3d00e830d848ddee46d18c892bcbdb1081d2`; source `cd371e035c7e573760c43bf934d53e8118ee3e7d`.
Tool worktree `/root/verifast-network-n13` on `challenge8/network-n13-20261023` at `809de4596839b739dd999f9e462242c835e3af46`.
Profile `research/challenge-8/cloud-build/network-n13/N13-EXECUTION-PROFILE-20261023-N4-HANDOFF.json` SHA-256 `08e016f4c97d919421b5325c41c98e94ea987162d44681be04dc91b1476f6e13`. New ledger path: `research/challenge-8/cloud-build/network-n13/BUDGET-N13-20261024-N5.json`; previous closed ledger: `research/challenge-8/cloud-build/network-n13/BUDGET-N13-20261023-N4.json`.
Cloud budget: 10800 seconds. Wall window: 4320 minutes main + 60 minutes closeout (explicit window authorized by this task only; CORE main/closeout rules apply to these deadlines). Per-Build timeout ≤1200 seconds; report reserve ≥240 seconds. T0 remains NOT_SET until actual work starts.

## Goal and steps

N5 и Builds разрешены. Разовое расширенное окно: закрытие по цели, бюджету или настоящей границе, не по времени (N5-OWNER-DIRECTIONS). Цель 1 — закрыть exact N13: order negative и universal 480, полная матрица. Цель 2 — перенос R7 has_efficient_in_place_swap (75%) на baseline cd371e0 в stock-профиле 26.09 через Cloud lane. W7/W8 ждут PUBLISHED P2; W8-подготовку не расширять.

1. Register N5 on the N4-HANDOFF profile (08e016f4…). Order negative first (600 / 975+60), then standalone universal 480 (855+60) and same-unit dependency coverage; classify by exact receipts; timeout/setup/wrong-site stay INCONCLUSIVE. Record exact N13 acceptance only on the complete matrix.
2. R7 transfer: add a Cloud stage/recipe (lane network-n13 or a new network lane with its own closure inventory) extracting the live has_efficient_in_place_swap<T> from source cd371e0 (blob 40939f92) fail-closed as extract-verifast-swap-size.py does; verify the ghost-only contract req true; ens result == (size_of::<T>() <= 8) with stock 26.09 and the pinned refinement check. Result card per COMPLETION-PLAN transfer rules; no dispatch-caller credit.
3. Only with remaining budget: re-check Select P2-INTERFACE (PUBLISHED required) and prepare R4 consumption inputs; W8 stays preparation-only. Record choices and reasons in CHECKPOINT mission_queue.

## Special bounds

- Window deadlines exist only for ledger/watcher. Never shorten a timeout or case limit; setup error or no-proof run fixed statically, same config never repeated. Review once per semantic candidate (CORE 2026-10-23); progress note about every 2 h.
- Stock VeriFast 26.09 only (809de459): no tool/kernel/prelude patch, axiom or bodyless bridge; preserve every post, body inventory, return/leak/source gate; no parallel select/callback layer. R7 on the stock profile transfers an isolated theorem; it does not qualify dispatch callers.
- coordination.py v4, shared coordinator/IAM/transport, other worktrees and ledgers unchanged; no Actions dispatch (run-verifast-swap-size.sh is Actions-only); no local generator/compiler/verifier.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: Full N13 acceptance OPEN: order UNRUN, standalone universal timeout.
Next: Register N5; order negative 600/975+60, then universal 480/855+60 and coverage; then the R7 Cloud stage on stock 26.09 against source cd371e0.

## References

- [Owner directions N5](network/n13/N5-OWNER-DIRECTIONS.md)
- [N4 handoff](network/n13/N4-HANDOFF.md)
- [Historical R7 helper proof](verifast-swap-size.md)
- [Progress review §9](PROGRESS-REVIEW.md)

## Отчёт агента

**network-n13-exact-cloud-2026-10-24-n5 · network · NETWORK-N13-EXACT-2026-10-24-N5 · ACTIVE**
Updated: 2026-10-23T11:15:34Z. Baseline source/tool/profile: `cd371e035c7e573760c43bf934d53e8118ee3e7d` / `809de4596839b739dd999f9e462242c835e3af46` / `08e016f4c97d919421b5325c41c98e94ea987162d44681be04dc91b1476f6e13`.
Dates: T0 `2026-10-23T10:48:37Z`; main `2026-10-26T10:48:37Z`; absolute `2026-10-26T11:48:37Z`; window 4320 min main + 60 min closeout (explicit). Budget 10800s: 1131s spent, 0s retired, 9669s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: Universal terminal; Brief classification pending. R7 reviewed, UNRUN.
Next: Classify universal Brief; final closure/pins; submit R7 swap-size1185.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
