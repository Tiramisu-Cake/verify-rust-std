# KANI3300 Г1 STEP0 — saved-stream census (DRAFT / NOT ISSUED)

2026-11-13. **Черновик для worker14, НЕ ВЫДАН.** Это верификация корректности, не security-работа.
Разрешение на исполнение даст координатор отдельно. Здесь нет поручения запускать анализ сейчас.
После выдачи: одна локальная Python/read-only сессия, Cloud $0; никаких compiler/verifier/CBMC/CI запусков.

## Вход и неизменность истории

Прочитать отчёт R3 @**88ca9d0294f5e6f631117aa68f56ee1e3464398d** §2,4 и `PLANNER-R3-H1-REVIEW.md`.
Исследование `kani3300/d1a/` @15276d57238f4a70b2ea5fca9141ef047cce120c; старые итоги/ledgers не переписывать.
Использовать **только уже сохранённые D1** bundles в `/root/kani3300-d1p-ci/`:
- R1+skip: d1p-r1-skip-43314208878-1 /56cbc5c4a479bc3fb25310b14fcf279d90581a02/P1/postcondition_reads_initialized_return/;
- R6-02b: d1p-r6b-43314208878-1 /405c1f059264d8f7cedeeaa01c6d4ad6867a419e/P1/postcondition_reads_initialized_return/.
Полные пути/manifest hashes подтвердить перед чтением; actual model hashes/coverage — из DATA-ACCEPTANCE/INPUTS D1-A.
Разрешены точечное чтение этих сохранённых program-only streams, selected GOTO projections/metadata и их Python census.
Это явное исключение для данных D1, не разрешение читать любые raw logs/архивы или скачивать GCS/Actions/Cloud Logging.
Если файл отсутствует/identity не сходится — STOP с конкретным полем; новый run/export/download не запрашивать автоматически.

## 1. Владение таблицами и определения

По model/symbol/function projections связать dynamic objects с DFCC allocated/deallocated/contract_frees и write-set scope.
Не считать любой dynamic_object таблицей DFCC и не переносить object$12 изR6 наR1 без binding.
Для каждой таблицы: root/type/element width/extent/capacity/source owner, actual b/W или UNKNOWN;
полный SSA version identifier с invocation/call context, ARRAY_OF/WITH/прочие definitions и ignored/retained статус.
Сохранить цепочки definitions, aliases и selected initialized/null versus unconstrained classification с основанием.
«Definition sliced» само по себе не доказывает, что converter создаст fresh full-width bits; отметить недоказанный переход.
Retained-constant и retained-symbolic/guarded версии различать: ignore=false не доказывает константный bitvector.

## 2. Census чтений — не смешать proxy и converter

Начать с существующего d1a/analyze_offline.py, расширить узко под table/read mapping, не заменять новым framework.
Парсить весь разрешённый bounded stream, не старый prefix200000 chars. Сверить исходный D1-A census как sanity,
но не подгонять числа. Отделить record kind/ignore/source PC/function/guard lines и последний видимый ASSERT.
Считать отдельно все до/после него: guard assignments (ignored и retained), retained прочие assignments/ASSUME/ASSERT,
и прочие видимые categories. Byte/index reads, WITH updates и lhs stores — разные виды, не общий regex по квадратным скобкам.

Read key: **table SSA expression/version + index expression + result type**, PC/function — provenance list, а не cache key.
И raw, и canonical views: индексPO(&x.field) можно нормализовать кPO(&x) только по подтверждённому source rule;
не стирать SSA/call suffixes, casts/widths/offsets без обоснования. Count occurrence ≠ distinct converter expression ≠ cache miss.
Зафиксировать количества first-read/free-version и repeated-read/same-version отдельно; не брать S=D автоматически.
Для каждого класса дать exact known/type-derived/heuristic/UNKNOWN, definition ownership и почему candidate read retained или proxy.

Program-only **не печатает GOTO**. Guard-symbol assignment может быть зеркалом condition, но полную coverage это не доказывает.
По сохранённым GOTO PCs/source и pinned CBMC symex/slicer/converter source сопоставить возможные mirrors,
отдельно подтвердить отсутствующие/неоднозначные связи. Не объявлять proxy census exact GOTO conversion count.
Нулевой proxy count → NEGATIVE_PROXY_RESULT/UNKNOWN_GOTO_COVERAGE, не «Г1 опровергнута», если completeness не доказана.
Наличие read также не доказывает actual converter cache miss или доминирующую память.

## 3. Проверка количественной гипотезы

Независимо от подгонки CNF получить candidate C retained reads, D free-version reads и S free table versions,
с диапазонами/UNKNOWN. Сравнить R6 prediction12 и R1 prediction~10 с данными; расхождение — finding, не parser failure по определению.
Пересчитать §2.2 отдельно по clauses и variables: kC/kV, residuals абсолютные/%, без вывода read-count из одного floor.
Для64-bit constant-index model: constant read ≈N+64 vars/65N+1 clauses;
free-read first version ≈129N+64 vars/321N+1 clauses; same-version extra read ≈65N+64 vars.
Если есть смешанные классы/cache sharing, slopesV=64S+65D+C, slopesC=321D+65C в рамках этих предположений,
а не универсальные ratio2.5–5/<10. Иные index widths/symbolic indices/caching означают другую модель/UNKNOWN.
Указать missing converter data; математический счёт gates не считать измеренными allocations/RSS или source proof.

Optional: counters legal_pfc_transfer из43232249168 — **только** если координатор уже передал локальный curated receipt
с exact root/source identity. Не искать/скачивать исторический полный журнал; отсутствие поля UNKNOWN не блокирует STEP0.
Сверить источник saturating warnings по D1: callsites lib.rs833/846, actual added parameter/use в доступном GOTO.
Source location совпала ≠ доказанная безвредность; unused write-set в exact body можно установить статически, иначе fidelity gap.

## Результат и STOP после отдельной выдачи

В `kani3300/h1-step0/`: INPUTS.json (files/hashes/coverage), TABLES.json, READ-CENSUS.json,
ATTRIBUTION.md (до200 строк/top30 плюс bounded coordinates), RESULT-H1-STEP0.md (≤35 строк), небольшой Python parser и synthetic fixtures.
Test synthetic multiline/unknown kind/ambiguous index/duplicate prefix/missing definition/cap/wrong pin; не новый exporter/framework.
Runtime budget анализа описать (например60s/512MiB), cap → INCOMPLETE; не сериализовать огромные expressions ради fingerprint.
Не менять D1 files/historical summaries, compiler/runtime/fixture source или существующие goldens.
Приёмка: независимый воспроизводимый proxy/read census + source/table/definition binding **либо** точные gaps;
конвертерная причинность остаётся PROVISIONAL. Итог SUPPORTED_PROXY / COUNTEREVIDENCE / INCONCLUSIVE, без proof credit.
Сформировать handoff, какие дополнительные флаги в STEP1 различают оставшиеся объяснения; CI не выдавать и не запускать.
После отдельной выдачи research [skip ci], Tiramisu-Cake <igkharin@gmail.com>, stage только h1-step0/, локально без push;
финальная строка исполнителя `READY <sha research-коммита>` не означает разрешения STEP1. **Сейчас NOT ISSUED.**
