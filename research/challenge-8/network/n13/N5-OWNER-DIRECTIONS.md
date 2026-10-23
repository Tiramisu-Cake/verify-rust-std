# Network N5 — указания владельца (2026-10-24)

Источник решений: [PROGRESS-REVIEW §9](../../PROGRESS-REVIEW.md), редакция 2 от 23 октября 2026. Файл дополняет компактный CURRENT-TASK; полномочий сверх задания и CORE не выдаёт.

## Режим окна (разовая практика)

- Время сессии не ограничено: формальные deadlines ledger/watcher — T0+4320 мин main, +60 мин closeout — существуют только для tooling. Сессия закрывается по цели, исчерпанному бюджету или настоящей границе после проверки независимых задач миссии; окно формальной активностью не заполнять.
- Cloud budget 10800 с, per-Build timeout ≤1200, report reserve ≥240. Case limits и timeouts никогда не урезать; setup error или прогон без стадии proof исправляются статически, та же конфигурация не повторяется.
- Independent review (Luna HIGH) — один пакет на semantic candidate перед его Build/submit, не на каждый commit; delta той же границы — продолжением того же reviewer.
- Progress примерно каждые 2 часа активной работы без ожидания ответа. Спорные моменты — по CORE «Решения без владельца».

## Цель 1 — закрыть exact N13 (W7 математическая часть)

1. Регистрация N5 на профиле `N13-EXECUTION-PROFILE-20261023-N4-HANDOFF.json` (SHA-256 `08e016f4…`; exact/member/order 600, universal 480, other 180, setup 120, soft 15, report 240, queue 60). Preflight только при изменении identities.
2. Order negative (600 / Build 975 + queue 60) первым; затем standalone universal 480 (855 + 60) и оценка same-unit dependency coverage по правилу no-duplicate-checked-dependency. Timeout/setup/wrong-site остаются INCONCLUSIVE. Exact N13 acceptance записывать только по полной матрице (exact + membership + order + missing + 7 классификаторов + N9 + universal).

## Цель 2 — перенос R7 `has_efficient_in_place_swap` на актуальный baseline

Историческая isolated generic теорема (VeriFast 26.09, LP64, source `9fb89404`, Actions run 37401540878) даёт R7 75%. Перенос на текущий baseline в Cloud lane — единственный шаг индекса, не зависящий от Select P2.

3. Добавить Cloud stage/recipe (в lane `network-n13` новым stage или отдельная network lane с собственным closure inventory): извлечение live `has_efficient_in_place_swap<T>` из source `cd371e035c7e573760c43bf934d53e8118ee3e7d` (SmallSort blob `40939f922bcb6fdc7ee0d30427fa861827043827`) тем же fail-closed способом, что `extract-verifast-swap-size.py` (уникальные anchors, неизменная signature и выражение `size_of::<T>() <= 8`); verified копия добавляет только контракт `req true; ens result == (std::mem::size_of::<T>() <= 8);`; stock VeriFast 26.09 (`809de459`), pinned refinement check (ghost-strip восстанавливает original bytes). `run-verifast-swap-size.sh` — Actions-only, на VPS не запускать; Cloud-вариант строится в своей lane.
4. Критерии результата по COMPLETION-PLAN «Правила переноса»: карточка с source/blob identity, tool/profile, target LP64, Build ID, verifier и refiner exits, exactly one `Verifying function` record для `smallsort::has_efficient_in_place_swap`, statement-execution trace в body. Это компонентный перенос на итоговый source; dispatch callers и R1–R3 из него не следуют, credit только по Brief-подтверждённым receipts.

## Цель 3 — только при остатке бюджета

5. Проверить `task-history/select-callee-r24/`/`P2-INTERFACE.json` Select: при статусе `PUBLISHED` подготовить R4 consumption inputs (без R4/W7 Build в этой фазе). W8 остаётся preparation-only; новые W8-кандидаты не готовить до PUBLISHED P2 и опубликованных W3/W5 ресурсов. Выбор и причину каждой obligation — в CHECKPOINT `mission_queue`.
