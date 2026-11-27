# REV2 general/stable N16 closure · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-28. **NO-GO**, один блокер. Пины: Std `a7df430f35dca8e0a6372fe8410229277974194a` / tree `cac68fdb2a`, parent `5a8702f59a`; Control `8a7094b777061721cfcf8c7848aa55c3f901b709` / tree `0fb7318d0d`, parent `bcf4fd366d`; review-trigger `74dfd5283a`; request `bbfebcae…`, bundle `3e518a27…` (86 360 байт); задание g0 `fa8731df9e`, handoff g0 `63e106d029`.

1. **Блокер (подтверждён координатором по исходнику).** `rev2_gen_stable_n16_pilot.rs:1085`, `gen_n16_wide_fill_r48_rel5`: `for i in 0..6` индексирует `old[i]`, а `old` — `[Wide; 5]` (`:1069–1077`). На `i=5` проверка границ массива падает на каждом пути: слот даст `FAILED` вместо `VERIFIED`, итог пакета `OPEN`. rel6 (`0..6`, длина 6) и rel7 (`0..7`, длина 7) верны. Исправление — `0..5`; координаты строк не меняются, но пересоздаются blob, Std commit/tree, bundle, bindings, request и trigger. Ни source gate, ни синтетика, ни Python-модель не исполняют границы Rust-циклов.
2. Nit (как R1-2 пилота). Комментарии `:948`, `:1022`, `:1095` «Transcription of smallsort.rs:329–330» накрывают и actual `insert_tail`; в request `transcribes` только у локальной копии. Comment-only строки — можно поправить на `:329` без сдвига координат.

Проверено и в порядке: Std-дельта — check-cfg и чистое добавление `mod close` (+481), прежний модуль — побайтный префикс; геометрия левых S8 (`:299`) и S4 (`:310`), rel5–7 (`transcribes :329:17`, actual `insert_tail` как на `:330`), диспетчеризация `:81`, `:134–139 → :213–224 → :261–273`; контроли по Python-модели — `u64` 0x5555 → 0xff00 → 0xff80, единственный отказ — кратность 9≠8 на `:1168`; Wide — выход меток `[1,3,4,5,6,7,9,11,12,13,14,15,0,2,8,10]`, обмен записей v[6]/v[7] ломает только `STABLE_EQUAL_KEYS` на `:1234`; только скалярные сравнения, циклы ≤28, scratch48 интервалами ≤32; композиция (шаги 1–7) пронумерована и честно помечена внешней; roster 171 → 178, 5 VERIFIED + 2 FAILED, лимиты и часы 110-минутного job, отдельная переменная tree; nit R2 (`test_run.py:531`) исправлен; `test_run`/`test_results` 81/81; авторы, `[skip ci]`, без решётки перед цифрой.

## R2 · FIX1 (дельта, координатор)

Ревью дельты координатором 2026-11-28; остальной пакет покрыт независимым R1. **GO.** Пины: Std `e8e8af6d3b4c77ce0ee25066e9c97b6df3fd222e` / tree `f48157264e`, parent `a7df430f35`; Control `ad7e2ba127919b463a395819c94a30225b844b90` / tree `8fff1fc16152df0c6febf8bac6729199a12407be`, parent `8a7094b777`; review-trigger `f546e8873c` (тот же tree, sole parent `467af9cb8d`); request `c3049756…`, bundle `8668301c…` (87 143 байта, HEAD `e8e8af6d3b`); handoff g0 `91f1950ff8`.

- Std-дельта — один файл, 4 строки: `:1085` `for i in 0..5` (блокер R1-1 закрыт) и три comment-only `Transcription of smallsort.rs:329` (nit R1-2).
- Control: новые пины overlay/bundle/bindings, `CLOSE_R1_OVERLAY` как историческая ступень с проверкой «меняется только модуль», новый gate `check_close_fill_bounds` сверяет литеральные границы шести циклов каждого rel5/6/7 с длинами `old` и scratch48, синтетика отклоняет дрейф границ.
- На точном trigger `f546e8873c` в отдельном клоне: SHA-256 request и bundle совпали с handoff, `test_run`/`test_results` — OK.

## R3 · FIX2 (Wide witness на литеральном входе)

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-28. **GO_WITH_NITS**, блокеров нет. Пины: Std `cebdba9913d72c892eb6701d9a989bb2a9830768` / tree `eb6a2ab7…`, parent `e8e8af6d3b`; Control `274370cb7b6692543e2d7d3400951724e236108a` / tree `079d7a986f15bc2fd0acb7f32d162ea5a81e7358`, parent `ad7e2ba127`; review-trigger `46f1604664` (тот же tree, sole parent `467af9cb8d`); request `8d99d839…`, bundle `be5158b4…` (90 391 байт, HEAD `cebdba9913`); задание g0 `5151061853`, handoff g0 `41107e4b0f`.

1. Nit. Выходные проверки не различают маршрут: stable fallback дал бы тот же выход на этом входе. Маршрут general/scratch48/sort4 фиксируют константные проверки `rev2_gen_stable_n16_pilot.rs:23–33` и исходная привязка, а не прогон. Отметить одной фразой в итоговом разборе.
2. Nit. Метки `GEN_N16_WIDE_{BEFORE,AFTER}_RECORDS_BY_TAG` теперь означают позиционное равенство полных записей с `EXPECTED`/`CORRUPTED`; новая координата и selector исключают путаницу со старым корнем.
3. Операционно. Workflow читает только `CH8_REV2_GEN_STABLE_N16_CLOSE_WIDE_WITNESS_TRIGGER_TREE` — выставить `079d7a986f` при GO.

Проверено и в порядке: Std-дельта — check-cfg и добавленный модуль, старый файл (49 352 байта) — побайтный префикс; без `kani::any`, `wide_v()`, `assume`, stubs; маршрут `:1302` → `:213–224` → general; независимая Python-модель actual кода (sort4, `insert_tail`, merge с tie-правилами) дала `[1,3,4,5,6,7,9,11,12,13,14,15,0,2,8,10]` = стабильная сортировка; до обмена пять assertion истинны, после обмена v[6]/v[7] ложна только последняя `stable` (`:1323`), covers до неё — единственный отказ; только скалярные `same_wide`, циклы ≤15; честная маркировка как single-trace контроль; discovery 178 + 1, gate координат, rel5/6/7 bounds, точное сообщение `standard harness has a contract target`; часы; авторы, `[skip ci]`, без решётки; `test_results`/`test_run`/`test_telemetry` 89/89.
