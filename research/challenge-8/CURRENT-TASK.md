# Network N1: запуск направления, перепривязка сетей и кандидат actual swap_if_less

Task ID: `network-bootstrap-2026-10-22-n1`; previous task: `networks-iteration-2026-10-07`.
Owner: **Network**. Phase: `NETWORK-BOOTSTRAP-2026-10-22-N1`. Lane: `network`.

## Mission

This is the first task of a newly established owner. The worktree's prior research iteration is archived under `task-history/networks-iteration-2026-10-07`; its claims keep their own dated scope.

Runtime: Claude Code. This fresh-window task follows [`CORE.md`](agent-workflow/CORE.md), the runtime profile [`RUNTIME-CLAUDE.md`](agent-workflow/RUNTIME-CLAUDE.md), the compact root [CLAUDE.md](../../CLAUDE.md), and the persistent repo guidance. Review executor and Build waiting follow that profile only.
The owner may proceed within this task and its bounds. Initial T0 NOT_SET: fix T0 once at actual work start, including preparation. This task has no Cloud lane: no coordinator request, phase registration, Build submission or proof execution. Commit reviewed candidates and handoff inputs for a later, separately authorized Cloud task.
No previous budget, T0, ledger authorization, profile acceptance, or proof credit transfers.

## Baseline and controls

Worktree `/root/verify-rust-std-networks` on branch `challenge-8/networks`; baseline `52fea043c313e3f93ee831e612afa7aa0c7002e4`; source `cd371e035c7e573760c43bf934d53e8118ee3e7d`.
Tool worktree `/root/verifast-network` on `challenge8/network-20261022` at `f76012fb518703b1d98e243ac4f487f16877cfcb`.
Profile: none (no Cloud lane). New ledger path: none; previous closed ledger: none (bootstrap).
Cloud budget: 0 seconds (no Cloud lane). Wall window: 120 minutes main + 30 minutes closeout. T0 remains NOT_SET until actual work starts.

## Goal and steps

Запустить направление Network (W7→W8): принять общие правила, перепривязать доказанную математику сетей к shared std baseline и подготовить reviewed кандидат actual swap_if_less (R4) плюс пакет Cloud-готовности для первого Cloud-задания. Контекст и границы — BOOTSTRAP-2026-10-22.

1. Адресно принять общие docs по ADOPTION (из /root/verify-rust-std-evidence-brief, branch-local PLAN/README/RUNBOOK архивировать), затем перевести library на shared baseline cd371e03 (SmallSort blob 40939f92) и статически перепроверить SOURCE-MAP: тело swap_if_less, порядок/индексы 25/45 вызовов sort9/sort13.
2. По SWAP-CONTRACT и актуальному опубликованному callback/pointer-select слою Select подготовить кандидат actual swap_if_less: generic T/F, normal/unwind, равные индексы, ZST, ManuallyDrop/read/copy ресурсы, select_unpredictable<*mut T>; required controls/negatives; независимое review; commit с HANDOFF для Cloud.
3. Подготовить Cloud-готовность как reviewed PREPARED_NOT_REGISTERED пакет: свой branch client (на базе клиента Select), phase registration и план миграции coordinator на четырёх владельцев с service tests. Ничего не регистрировать и не запускать.

## Special bounds

- Бюджет Cloud 0: без Builds, coordinator request, правок active.json и чужих клиентов/веток/ledgers; без GitHub Actions и локальных rustc/Cargo/VeriFast/Kani.
- Callback/pointer-select — потребитель слоя Select без параллельной реализации; нужное изменение — reviewed patch-кандидат на точном commit. Прежние claims сетей (stock VF 26.09, Actions) сохраняют свой scope и не дают кредита Rust R4.
- Tool-изменения только в /root/verifast-network; maintainer получает лишь готовые опубликованные патчи.

## Starting checkpoint

Read [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for the exact claims, assurance, evidence, open and rejected items, and artifact identities. UNKNOWN remains UNKNOWN.

Blocker: У network нет Cloud lane (coordinator v3 V3_OWNERS, нет branch client); source certificates на старом SmallSort blob.
Next: Шаг 1: adoption и перевод на shared baseline, затем кандидат R4 и пакет Cloud-готовности.

## References

- [Bootstrap Network 2026-10-22](network/BOOTSTRAP-2026-10-22.md)
- [swap_if_less contract](networks/SWAP-CONTRACT.md)
- [Integration obligations](networks/INTEGRATION.md)
- [Source map 9/13](networks/SOURCE-MAP.md)
- [Networks status 2026-10-07](networks/STATUS.md)

## Отчёт агента

**network-bootstrap-2026-10-22-n1 · network · NETWORK-BOOTSTRAP-2026-10-22-N1 · ACTIVE**
Updated: 2026-10-22T16:13:26Z. Baseline source/tool/profile: `cd371e035c7e573760c43bf934d53e8118ee3e7d` / `f76012fb518703b1d98e243ac4f487f16877cfcb` / `UNKNOWN`.
Dates: T0 `2026-10-22T15:07:38Z`; main `2026-10-22T17:07:38Z`; absolute `2026-10-22T17:37:38Z`. Budget 0s: 0s spent, 0s retired, 0s remaining including reservations.
Active Build IDs: none recorded; unresolved: none recorded.
Blocker: R4 blocked on Select layer: P2 (no checked select_unpredictable callee) and P1 adoption; no Network Cloud lane.
Next: Owner: pass SELECT-REQUESTS (P1 candidate, P2) to Select; decide v4 migration. First Network Cloud task: build P1 on the reproduced base, then R4 matrix; W7 after R4 acceptance.
See [STATUS.md](STATUS.md) and [CHECKPOINT.json](CHECKPOINT.json) for claims, evidence, open/rejected items, and artifact identities.
