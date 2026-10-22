> **Короткий старт новых Select/Merge сессий (2026-10-21):** обязательное [CORE](agent-workflow/CORE.md) + своё CURRENT-TASK + CHECKPOINT/STATUS. Этот документ — подробный справочник: открывай нужные разделы, без полного перечитывания. Legacy active sessions сохраняют свои inputs/T0/счета. [Инструменты и порядок](agent-workflow/README.md).

# Самостоятельная работа proof-агентов по плану

Решение владельца от 2026-10-20. Select и Merge сами выбирают задачи и эксперименты внутри своих миссий из [WORK-POLICY](WORK-POLICY.md) и [COMPLETION-PLAN](COMPLETION-PLAN.md). Это правило для новых заданий; конкретное поручение выделяет окно, бюджет и lanes. Активные сессии сохраняют T0, inputs, счета и явно заданные границы до нового поручения. Роль VeriFast maintainer не расширяется.

## Самостоятельный выбор и исправления

- Запиши ближайшую proof-цель и короткий план; обновляй его по evidence. Blocker, порядок подзадач, fixtures и следующий полезный шаг выбирай сам. Согласовывать каждый пункт не нужно.
- Разрешены свои proof annotations/specs/леммы/resources, parser/inventory/binder/source-binding/нормализация, runner/preflight и диагностика. Реализацию проверки можно исправлять при сохранении её математического критерия и гарантий. Снятие ошибочного ограничения представления требует обоснования, а не удаления проверки ради PASS.
- Необходимые exporter/schema/decoder/translator/frontend/lowering исправления входят в миссию, если сохраняют source semantics и действующую модель. Сначала rationale и controls, затем независимый review и Cloud-проверка точного кандидата. Название компонента или новый predicate сами по себе не требуют решения владельца.
- Новые experimental profiles, tool commits и зависимые hashes/pins разрешены для этих изменений. Сохраняй baseline, состав и provenance; experimental не равен qualified. Готовые патчи публикуй в своей project branch; отсутствие tool remote не должно блокировать поддерживаемую передачу pinned patch/Git objects.
- Продолжай после промежуточного результата, пока есть полезный шаг, время и бюджет. Если основной путь заблокирован, выбери независимую задачу плана. Не закрывай сессию после одного guard/compiler error и не заполняй окно формальной активностью.

## Проверка и настоящие границы

До реализации семантического изменения запиши дефект, source applicability, сохраняемые критерий/ресурсы и различающие positives/negatives. Review актуального diff/dependencies — независимый reviewer по профилю среды ([Codex](agent-workflow/RUNTIME-CODEX.md): GPT-6 Luna HIGH; [Claude](agent-workflow/RUNTIME-CLAUDE.md): субагент `smallsort-reviewer`), без вложенной делегации и автоматической дорогой замены. Конкретное soundness-возражение нужно устранить до принятия. Review/synthetic tests не заменяют actual Cloud regressions.

Исправляй связанные места одного класса до Build. Существующий preflight → target proof → dependent controls; итоговая обязательная матрица/lifecycle полностью на совместимых финальных identities. Не собирай итоговый PASS из несовместимых кандидатов. Собственные receipts/actual callers проверяй там, где требует обязательство.

Нельзя сокращать runtime/domain/generic signatures, normal/unwind/abort posts, матрицу/negatives или критерий formal acceptance; отключать checks, добавлять непроверенные axioms/ownership bridges, считать равные адреса ресурсом. Новая memory/alias/layout model или новое доверенное допущение вне принятого метода требуют конкретного решения владельца. Обычный checked proof/исправление реализации не считать новым допущением из-за нового файла/символа.

Чужие worktrees/branches/pins и historical verdicts не менять. Runtime std/алгоритмы сохранять. Новые внешние сервисы, межсессионный cache, shared coordinator/IAM/triggers/dependencies и upstream-публикация не разрешены. Select/Merge используют прежние Cloud Build lanes; GitHub Actions разрешён роли verifast.

## Окно, остановка и отчёт

120 минут основной работы + до30 минут завершения сохраняются. После main никаких новых Builds/retries/гипотез; finishing window — начатый шаг, evidence, учёт, checkpoint. Число последовательных Builds ограничено временем, Cloud budget и slots, а не отдельным счётчиком. Новый счёт открывает конкретное поручение; закрытые остатки не переносить, отказы coordinator не обходить.

Рано завершать можно при выполненной миссии, исчерпанном бюджете либо конкретном внешнем/семантическом препятствии после проверки независимых полезных задач в scope. Нехватка остатка окна на полный цикл с Cloud — не препятствие: остаток main тратится на этапы следующего цикла без Cloud (реализация, tests, review, pins, committed кандидат), а его Builds выполняются в следующем окне по новому заданию и ledger. Повторять отказ без новой гипотезы нельзя. При настоящей границе сообщи точное недостающее решение и почему оно выходит за полномочия; разрешения на уже разрешённый шаг не спрашивай.

Примерно через час — progress без ожидания ответа. В конце один отчёт: выбранные цели, proof до→после, обслуживание отдельно, Builds/гипотезы/charge, T0/end, blocker/следующий эксперимент. Wall-clock не равен active agent time; retired headroom не равен расходу.

VPS — Git/hashes/static parsing и малые isolated synthetic service tests; actual preparation/compiler/verifier — Cloud-only. [Процесс](ITERATION-PROCESS.md), [Evidence v0.11](EVIDENCE-READER-GUIDE.md), запрет raw/full-log/GCS обхода и B1/B2/source-claim distinctions сохраняются. Это заменяет согласование каждого implementation predicate в новых заданиях, а не конечные proof-гарантии.
