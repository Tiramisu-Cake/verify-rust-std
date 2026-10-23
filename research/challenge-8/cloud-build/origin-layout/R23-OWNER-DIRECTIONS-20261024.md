# Merge R23 — указания владельца (2026-10-24)

Источник решений: [PROGRESS-REVIEW §9](../../PROGRESS-REVIEW.md), редакция 2 от 23 октября 2026. Файл дополняет компактный CURRENT-TASK; полномочий сверх задания и CORE не выдаёт.

## Режим окна (разовая практика)

- Время сессии не ограничено: формальные deadlines ledger/watcher — T0+4320 мин main, +60 мин closeout — существуют только для tooling. Сессия закрывается по цели, исчерпанному бюджету или настоящей границе после проверки независимых задач миссии; окно формальной активностью не заполнять.
- Cloud budget 14400 с; envelope timeout 1200 / execute ≤780 / soft ≤765 / reserve ≥420, nested compile reserve 140; никогда не урезать. Transport измерять перед каждым submit; cap не менять. Ошибка компиляции или прогон без стадии proof исправляются статически; та же конфигурация не повторяется.
- Independent review (Luna HIGH) — один пакет на semantic candidate перед его Build/submit, не на каждый commit; delta той же границы — продолжением того же reviewer. Метаданные, receipts, views и тестовые правки review не требуют.
- Progress примерно каждые 2 часа активной работы без ожидания ответа. Спорные моменты — по CORE «Решения без владельца». Fixes для завершённого Codex worker — только через follow-up task, не send_message (R22 coordination_error).

## Порядок работы

1. **Без Cloud: три finding NEEDS_FIX** из `R22-OWNED-NLL-ADOPTION-REVIEW-20261023.json` (1f805a2c): (a) compile-only branch использует pin translator compile-профиля 65f, с focused check обоих маршрутов; (b) унаследованный `VF_EXPORT_OWNED_NLL_FACTS` удаляется из любого скопированного campaign/placement environment до direct и callback путей, с тестом inherited `=1`; (c) отдельный NLL eligibility flag только для exact registered positive target cases, false для mutation controls и derived body-isolation cases, с negative tests. Service error-path tests для затронутого runner. Один delta review.
2. **Регистрация R23** на reviewed tuple после fixes; HEAD profile `GLUE-PROFILE.json` = `3fec93b5…` (exact owned-NLL diagnostic profile, e4292270); исторически исполненный tuple R22 — tool 57812076 / profile 9496 (ledger). Перемерить transport. Ранний полный Build.
3. **Stop-loss на owned-NLL capture.** Не более **двух полных Cloud-циклов** на diagnostic capture. Критерий успеха: captured owned facts привязаны к actual MIR body/location, cross-stage mapping ESTABLISHED и пригоден как вход для checked resource conversion. При неуспехе записать точный gap (что именно UNESTABLISHED) и перейти на source-level маршрут из `R20-CALLER-AND-CONTROL-FRONTIER-20261023.md`: exact coercion kind / source-target types / lifetime identity, длина из actual array, checked array conversions и element ownership, инкапсуляция теми же ресурсами через `borrow`/`borrow_end` (`lifetime_logic.rsspec`, паттерн `str_mut_ref.rs`), `as_mut_ptr` → data component, те же ресурсы на normal и unwind. Без новой trusted borrow/memory premise.
4. **Raw caller controls.** F5 как настоящий resource negative (не static shape refusal), state-context (`unequal_address_taken_state`) и index-projection controls до их intended gates; результаты до gate — INCONCLUSIVE.
5. **Матрица.** CURRENT/backedge, false/true/panic/Drop/Resume на совместимых pins. Далее по COMPLETION-PLAN W2/W3/W5; выбор и причину каждой obligation — в CHECKPOINT `decisions`/`mission_queue`. Если полный цикл не помещается в остаток бюджета — reviewed HANDOFF.

## Для VeriFast maintainer

Поддерживать `cloud-build/origin-layout/TOOL-CHAIN.md`: опубликованные ветки форка (`merge/actual-glue-instance-20261011`, `merge/r22-*`) с exact heads, scope каждого commit-блока, profile gating и статус (admitted / prepared / NEEDS_FIX). Maintainer консолидирует tool-цепочку в integration-ветке; он не берёт proof-работу и не меняет ваши pins.
