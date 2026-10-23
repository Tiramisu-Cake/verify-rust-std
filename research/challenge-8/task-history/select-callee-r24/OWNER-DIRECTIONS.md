# Select R24 — указания владельца (2026-10-24)

Источник решений: [PROGRESS-REVIEW §9](../../PROGRESS-REVIEW.md), редакция 2 от 23 октября 2026. Этот файл дополняет компактный CURRENT-TASK; он не выдаёт полномочий сверх задания и CORE.

## Режим окна (разовая практика)

- Время сессии не ограничено: формальные deadlines ledger/watcher — T0+4320 мин main, +60 мин closeout — существуют только для tooling. Сессия закрывается по выполненной цели, исчерпанному бюджету или настоящей границе после проверки независимых задач миссии. Не заполнять окно формальной активностью.
- Cloud budget 21600 с, per-Build timeout 1200 (никогда не урезать), report reserve ≥240. Ошибка компиляции или прогон без стадии proof исправляются статически; та же конфигурация не повторяется.
- Independent review (Luna HIGH) — один пакет на semantic candidate перед его Build/submit, не на каждый commit; delta той же границы — продолжением того же reviewer. Метаданные, receipts, checkpoint views и чисто тестовые правки review не требуют.
- Короткий progress примерно каждые 2 часа активной работы, без ожидания ответа. Владелец вопросов не отвечает: спорные моменты решать по CORE «Решения без владельца».

## Порядок работы

1. **Registration.** R24 по route-marker pattern R21/R23 через существующий client; новый ledger по пути из задания, фактические T0/deadlines по окну выше.
2. **Первый Build.** Reviewed UNBUILT кандидат `a4737f9febf20ec5373eafa641268c26c6e674c7` (translator SHA-256 `103a34afa6b403760454ab42462040805f34f0cf42576b8179bc5ff368505e44`, patch `03f91fb5…`, GHOST-CFG-PROOF-PINS.json) на тех же fingerprint rows `739f982d`; новый fingerprint для translator-only кандидата не нужен. Полный envelope 1200.
3. **Если dead-code сохраняется.** Статически привязать точные diagnostic sites (S3-POSITIVE-TRACE-OBSERVATIONS, CFG-INVENTORY), сформулировать следующую фальсифицируемую гипотезу, один review на кандидат, Build. Любое изменение dead-code checker, gate exemption, guard-own=true или broad forget summary — owner-reserved: только opt-in experimental кандидат без credit плюс `open` вопрос в CHECKPOINT.
4. **Чистый positive.** Pin семи control targets (CONTROL-TARGET-PROPOSAL), normal/unwind/nested-Drop, ownership, leak/refinement, same-site omission controls на тех же identities. Callee acceptance записывать только по полной матрице. Classifier (NO_GO) и omit-* pins — только после этого.
5. **P2 mutable route до PUBLISHED.** Свежий exact `*mut` source/fingerprint, mutable translator certificates под closed opt-in, same-version mutable positive, refusal controls (const/mut substitution, pointer depth, operand/branch result, changed source/signature/cleanup), review GO, новый pinned `P2-INTERFACE.json` со статусом `PUBLISHED`, реальными Build/Brief identities и `contract_text_sha256`. Все четыре критерия из NETWORK-P2-RESPONSE обязательны. Network читает только этот файл.
6. **W4.** Dormant body route (BODY-C5-NEXT 168/191) после acceptance/linkage и count-five requalification; selectors, copies. Выбор и причину каждой следующей obligation записывать в CHECKPOINT `mission_queue`.

## Для VeriFast maintainer

Опубликовать в `task-history/select-callee-r24/TOOL-OVERLAYS.md` текущую цепочку proof-time overlays: пути patch-файлов, их SHA-256, base/final translator hashes, профиль (gating), порядок применения поверх upstream `f76012fb`. Maintainer консолидирует tool-цепочку в integration-ветке форка; он не берёт proof-работу и не меняет ваши pins.
