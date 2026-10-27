# Challenge 8: рабочая документация команды

Разрабатываем собственные доказательства actual std в нашем форке
`Tiramisu-Cake/verify-rust-std`. Полный Challenge пока не доказан.

| Читать | Назначение |
| --- | --- |
| [AGENTS](../../AGENTS.md) | Краткие постоянные правила и proof integrity |
| [WORK-POLICY](WORK-POLICY.md) | Миссии трёх агентов, scope патчей, режим и бюджет сессий |
| [STATUS](STATUS.md) | Компактный датированный индекс текущих blockers/evidence; собственный checkpoint рабочей ветки приоритетнее |
| [AGENT-RUNBOOK](AGENT-RUNBOOK.md) | Одна процедура входа, эксперимента, продолжения и checkpoint |
| [Cloud runbook](cloud-build/README.md), [v2](cloud-build/PARALLEL-BUILDS.md) | Exact inputs, submit/status/evidence/accounting и два slots |
| [COMPLETION-PLAN](COMPLETION-PLAN.md), [PLAN](PLAN.md) | Конечные требования и зависимости, без выдачи разрешений |
| [PROGRESS-REVIEW](PROGRESS-REVIEW.md) | Условный индекс готовности, две сессии на proof-агента и артефакты пересмотра |
| [Аудит PR #694, 2026-10-27](CH8-PR694-AUDIT-2026-10-27.md) | Для всех агентов: покрытие, ограничения, CI и сравнение с #701; без кода конкурентов, с сохранением правила чистой комнаты |
| [ADOPTION](ADOPTION.md) | Адресный перенос общих docs и принятие всеми тремя агентами |
| [INFRASTRUCTURE-TASK](INFRASTRUCTURE-TASK.md) | Поставленная отдельная работа, без реализации |
| [Архив](archive/team-procedure-2026-10-10/README-ARCHIVE.md) | Прежние инструкции и исторический bootstrap run log |

Требования: [Challenge 8](../../doc/src/challenges/0008-smallsort.md) и
[general rules](../../doc/src/general-rules.md). Actual source —
`library/core/src/slice/sort/shared/smallsort.rs`.

Компиляция/extraction/proof execution выполняются только в разрешённых Cloud
lanes. Лёгкие локальные service tests — в точных границах WORK-POLICY §4.
Docs-only задача не открывает proof-фазу и не даёт Cloud budget.
Исторические bounded i32 эксперименты, их limitations, failures и прежние next
instructions сохранены в архиве; новым actual доказательством они не стали.
Исследовательские индексы, coverage, EXPERIMENT-LOG и phase evidence живут в
собственных рабочих ветках, не переносятся целиком в main ради общих правил.
