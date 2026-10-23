# Network N6 — RefinedRust G1: указания владельца (2026-10-24)

Решение владельца 23–24 октября: возобновить исследование RefinedRust как **ограниченный эксперимент с заранее записанными критериями выхода**, не как второй основной путь. Исходная оценка и подготовка: ветка `research/refinedrust-feasibility-20261011` @ `68671873669cd8578796ad4cb74f0fc28e622f2f`, каталог `research/challenge-8/refinedrust-feasibility/` (FEASIBILITY-REPORT, EXPERIMENT-PLAN, G1-MINIMAL-PLAN, G1-FIRST-RUN-REQUEST, пакет `g1-minimal/`). Вердикт там: CONDITIONAL для `insert_tail`, NO-GO для миграции; blocker на пине `332d945f` — frontend без slices и union ADT.

## Режим окна (расширенное, как у R24/R23)

- Время сессии не ограничено: формальные deadlines ledger/watcher — T0+4320 мин main, +60 мин closeout — только для tooling. Закрытие по цели, бюджету или настоящей границе; окно формальной активностью не заполнять.
- Cloud budget 5400 с: cold image 1740/1800 (одна попытка, без retry), warm G1 1200/1260 (до двух попыток: первая и одна evidence-driven repair). Timeouts не урезать; setup error исправлять статически; ту же конфигурацию не повторять.
- После каждого terminal Build сразу коммить и пушь учёт ledger и CHECKPOINT/STATUS, до следующего шага.
- Review (Luna HIGH) один раз на semantic candidate; progress примерно каждые 2 часа; спорные моменты по CORE «Решения без владельца».

## Вопрос эксперимента и критерии выхода

**Вопрос G1:** принимает ли unpatched RefinedRust frontend (пин `332d945f`, компилятор nightly-2026-08-28 / `e457a7b0`) exact generic `insert_tail` с actual `CopyOnDrop::drop` и реально достигнутыми callees и генерирует ли для них Radium с присутствующими cleanup-рёбрами.

| Исход | Критерий | Решение |
| --- | --- | --- |
| **GO_G2** | Frontend завершает генерацию для `insert_tail` и `CopyOnDrop::drop` без патчей RR; cleanup/unwind присутствуют в выходе; список недостающих specs/annotations конечен и закрывается штатными `#[rr::...]` без `only_spec`, shims, более сильной FnMut, Copy/Freeze/purity | Подготовить оценку стоимости G2 (one-cell cleanup proof в Rocq) и STOP до отдельного задания |
| **STOP_RR** | Нужна правка frontend/semantics RR; требуется обход slices/union; несовместимость компилятора не снимается пином; отказ на самом `insert_tail` по unsupported operation | Зафиксировать первый причинный отказ (stage/symbol/span) и STOP; больше RR-Builds не делать |
| **INCONCLUSIVE** | Отказ на постороннем core item, setup/timeout/OOM, отсутствующий image | Один routine fix и одна повторная попытка в рамках бюджета; далее STOP с точным отказом |

Генерация и SUCCESS collector не являются safety PASS и не дают proof credit; индекс готовности не меняется ни при каком исходе G1.

## Порядок работы

1. **Перенос пакета.** `git restore --source=68671873669cd8578796ad4cb74f0fc28e622f2f` только нужных файлов `research/challenge-8/refinedrust-feasibility/{g1-minimal,EXPERIMENT-PLAN.md,G1-MINIMAL-PLAN.md,G1-FIRST-RUN-REQUEST.md,G1-PINNED-FRONTEND-AUDIT.md,G1-SOURCE-RECOVERY.md}` в `research/challenge-8/network/rr/` своей ветки; чужую историю не переносить. Пин RR остаётся `332d945f` (clean clone `/root/refinedrust-feasibility-sources/refinedrust-332d945fafa14bf55c0c8390cb35ec4b0c012cff`, branch main). **Проверка свежести** только read-only (`git ls-remote`, опубликованные changelog/docs upstream, текущий HEAD `fd52421e…`): переписывать пин лишь если upstream документированно добавил slices/union ADT, через существующий `restore-rr-bundle.sh` с проверенными hashes и отдельным review; код RR на VPS не собирать.
2. **Baseline std.** Предпочтительно текущий baseline проекта `cd371e035c7e573760c43bf934d53e8118ee3e7d` (SmallSort blob `40939f92…`): перепривязать anchors `annotations.json`/`inputs.json`. Если anchors или тело `insert_tail` отличаются так, что меняют эксперимент, использовать замороженный `c7ca8c46…` и записать расхождение.
3. **Регистрация.** Новая lane `network-rr-g1` в собственном клиенте по образцу R7-stage N5: cold-recipe (image) и warm-recipe (G1), profile `cloud-build/network-rr/RR-G1-PROFILE-20261024-N6.json` (DRAFT, заполнить exact pins), ledger по заданию. Machine type/disk из `dispatcher.proposal.patch` допускаются только как branch-local reviewed config своей lane; общий coordinator, control.py других owner'ов, IAM, `coordinator-owner.proposal.patch` (четвёртый owner) **не применять** — задание выполняется под owner `network`.
4. **Cloud.** Один cold image Build (если нет совместимого image receipt); один warm G1; по результату одна repair-попытка. Brief по v0.11; не читать raw logs. Классифицировать первый причинный отказ: compiler compatibility / frontend admission или missing library spec / selected unsupported feature / generated obligations UNPROVED.
5. **Результат.** `research/challenge-8/network/rr/RR-G1-RESULT.md`: вердикт GO_G2 / STOP_RR / INCONCLUSIVE по таблице, exact identities (image digest, RR/compiler/std/package SHA, Build IDs, Brief file/index), первый причинный отказ, список недостающих specs, и для GO_G2 — оценка G2 (окон, Cloud-секунд, ручного Rocq). Обновить `FEASIBILITY-REPORT` в своей копии датированной записью; оригинал на ветке feasibility не переписывать.
6. **Границы.** Никаких патчей RR frontend/semantics, Tool Application, CI-интеграции, новых trusted premises; W7/W8 остаются заблокированными до PUBLISHED P2 (в конце проверить `task-history/select-callee-r24/` на `PUBLISHED`); stock VeriFast профиль N13/R7 не менять.
