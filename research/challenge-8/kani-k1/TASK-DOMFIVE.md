# DOMFIVE — публичный англоязычный реестр доменов контрактов, привязанный к Part 1 v5 (без сборок)

Исполнитель: Codex, свежая сессия. Worktree `/root/verify-rust-std-kani-domains`, ветка
`experiment/kani-k1-domfive-20261102` от `e382287728` (library = v5 tree `cbe69760c8`, коммит Part 1 v5
`5a3009b065`). Сборок нет: GCB/Actions/CircleCI не трогать, library не менять. Evidence Brief / Select-Merge к K-1 не
относятся. Код конкурирующих PR не открывать.

Прочитать: `git show 790458b54e:research/challenge-8/kani-k1/DOMAINS-v4.md` и `domains/` той же ревизии
(реестр v4 после ревью планера; это основа), `RESULT-CLEANUP.md`, исходники `verify/**` v5. Черновик описания PR
`/root/smallsort-pr-drafts/PR-DESCRIPTION-DRAFT-v5.md` — только чтобы знать, куда реестр будет ссылаться; его не
править.

## Цель

Описание Part 1 будет ссылаться на публичный реестр: для каждой пары contract target × tag × domain — T, фактический
тип F и canonical CMP, model/order, probe (где ставится, неизменен ли), N, source/destination backing и offsets,
init, frame/modifies, проверяемые ensures, гармоники (имя и `file:line` на `5a3009b065`). Отдельно три
entry-wrappers N2.

1. Перенести записи DOMAINS-v4 на v5: все ссылки `file:line` пересчитать на `5a3009b065` (cleanup удалил
   cfg(any())-элементы и `correct.rs`; гармоника `contract_insert_tail_u8_prefix` теперь в `network.rs`). Адаптировать
   `domains/check_domains.py` к v5 и прогнать (Python only); ожидаемо 35 ordinary PFC, 0 inactive cfg(any()).
2. Написать `SMALLSORT-CONTRACT-DOMAINS.md` на английском, деловым языком, без внутренней кухни (без упоминаний
   аудитов, планера, Codex/Claude, GCB, бюджетов, конкурентов, внутренних кодов M01/Q01 и т.п. — заменить на
   читаемые имена). Структура: как читать; паспорта tags; таблица записей; раздел «requires admit vs executed
   domain»; «not established» (ровно по DOMAINS-v4 «Нельзя» 6–12 и разделу совместимости: Sort4ReadU64 ≠ LtU64,
   нет ordinary verified stubs, model-trust open для трёх array PFC со ссылкой на
   https://github.com/model-checking/kani/issues/5104). ≤ 250 строк. Утверждения о статусах только «SUCCESS in the
   organizer CI run of 5a3009b065» с плейсхолдером `<V5-KANI-RUN>` — координатор вставит ссылку.
3. Русский рабочий отчёт `DOMFIVE-v5.md` (≤ 30 строк): что перенесено, что изменилось против v4, вывод скрипта.

Commit `[skip ci]`, push без force (ветка новая). Маркеры `REVIEW REQUEST <sha>` / `DOMFIVE ЗАВЕРШЁН`. Один этап.
