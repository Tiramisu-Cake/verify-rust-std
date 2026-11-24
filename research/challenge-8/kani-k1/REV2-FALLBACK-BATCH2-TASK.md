# REV2 fallback · второй диагностический пакет

Подготовь control для одного Ubuntu-only прогона шести singleton новым локальным commit поверх `06d94b37158d559e538a5c8fe93e2d8d813204f9` в `/root/kani-rev2-fallback-control-w11`. Std overlay `fb82da3c78`, bundle, stock Kani `9834c96c`, CBMC 6.11.0, supervisor-политика и все guards прежние: нужные селекторы уже есть в overlay. Это решение координатора по разбору планера: одна job вместо двух пакетов по три слота. [Разбор и план](REV2-FALLBACK-RESULTS-ANALYSIS.md#cell-n16-и-следующий-замер) · [Прежнее задание control](REV2-FALLBACK-CONTROL-TASK.md) · [Ревью control](REV2-FALLBACK-CONTROL-REVIEW.md)

## Состав и порядок

| Слот | Селектор (префикс `slice::sort::shared::smallsort::verify::fallback_rev2::`) | Object bits |
| --- | --- | --- |
| 1 | `u64_n08` | 12 |
| 2 | `u8_n12` | 12 |
| 3 | `u8_n16` | 12 |
| 4 | `cell_unstable_n08` | 12 |
| 5 | `cell_unstable_n10` | 12 |
| 6 | `cell_unstable_n16` | **11** |

Лёгкие корни идут первыми, чтобы дорогой исход Cell не отнимал у них окно. Object bits задаётся в request для каждого слота и попадает в argv только через `--cbmc-args --object-bits <n>`. Остальной argv, профиль `-Z`, `--no-assert-contracts`, выключенные uninit/validity, `--jobs=1`, холодные target/output на каждый слот не меняются. Если CBMC сообщает `too many addressed objects` на OB11, receipt фиксирует это как недопустимый профиль с исходной строкой, а не как свойство корня.

## Время, память и запись

- На слот 600 с wall, cap 6 GiB, резерв 2 GiB, `jobs=1`. Окно job поднять до **140 мин**, setup и публикация в прежних бюджетах. Пересчитай план границ так, чтобы шесть окон, setup, финализация и upload помещались с запасом. Отсечка одного слота по времени или памяти при валидном сэмплере и подтверждённом reap не останавливает следующие.
- Receipts и проекция как в первом прогоне. Дополнительно сохранить первую CNF (переменные, дизъюнкты, фазу), стадийность и, если уже доступно в коде FIX8/CAL2 без новой подсистемы, отдельный RSS/PSS процесса CBMC. Новую подсистему не добавлять. 120 с VT и 4 GiB остаются диагностическими ориентирами.
- Request, roster и summary должны явно указывать object bits каждого слота. Сравнение N16 OB11 с записанным N16 OB12 (run 45358377716) делается в разборе, а не в control.

## Проверки и handoff

Обнови синтетические тесты: шесть слотов, OB11 в argv только у слота 6, порядок, план границ при 140 мин, `NOT_STARTED` для оставшихся слотов при остановке контроля, ранний отказ входов с шестью именными `NOT_STARTED`. Tree guard прежний: будущий trigger tree координатор закрепит в `CH8_REV2_FALLBACK_TRIGGER_TREE`. Прогони весь Python suite, `git diff --check`, YAML и `bash -n`, synthetic push с точным tree и единственным parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`.

В `REV2-FALLBACK-BATCH2-HANDOFF.md` укажи control commit, tree, будущий trigger tree, хэши request и bundle, diff `06d94b3715..<новый>`, итоги проверок, план границ. Пакет `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Cargo, rustc, Kani, CBMC, CI и push не запускать. Коммиты с `[skip ci]`, автор Tiramisu-Cake <igkharin@gmail.com>, без знака решётки непосредственно перед цифрой.
