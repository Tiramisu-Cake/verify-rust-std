# REV2 u64 N18/N19 providers · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **NO-GO** (только форматирование). Пины: Std `eb5b697e44` / tree `4c9908379e`, Control `d81a858793` / tree `8f6f404b4d`, review-trigger `bc7c22292e`, request `7c3dd218…8548`, handoff g0 `5ae575d332`.

1. **Blocker.** `rev2_u64_n18_n19.rs` не проходит закреплённый rustfmt (nightly-2026-11-19) с `use_small_heuristics=Max`: 8 diff-блоков на строках 92, 200, 250, 308, 324, 343, 354, 439. Регистрация в `verify.rs:311–312` после `mod types;` даёт новый diff порядка `mod`. Якоря file/line/column закреплены в request и bindings, поэтому форматирование нужно до заморозки. Исправить, пересчитать якоря, roster, bindings, bundle, request, Control и trigger; поправить handoff `:165`.
2. Nit, риск стоимости. `U64-N18/N19-PAIR-STEP` с символическими `k,a,c`: оценка 50–110 с VT, 2,3–3,2 GiB. Отсечка и разбиение up/down предусмотрены.
3. Операционно: `CH8_REV2_U64_N18_N19_TRIGGER_TREE` → tree нового Control; прогон после FIX1 N14–N17 на том же ref.

Проверено и в порядке: адреса пар совпадают с `bidirectional_merge` (`smallsort.rs:1010–1024`), все 285 сочетаний `(k,a,c)` в пределах; нечётный центр `:1027–1036`; вставка с фиксированной геометрией; 25 пар sort9 и 512 масок; циклы ≤34, только скалярные сравнения; Std-дельта 3 файла; SHA-256 входов, bundle, trigger, авторы, переменная, часы; suite 128/128.

## R2 · FIX1

Независимое повторное ревью по диффу (Claude, `smallsort-reviewer`) 2026-11-27. **GO**, замечаний нет. Пины: Std `c8eefae4c8073cff31e5576b372d5105b52797a1` / tree `4f9687a4ed`, Control `44aa6a2273588502083e47e204730dd67e0fba51` / tree `74f90d62acda5157906272454ec9d6c4bb9819db`, review-trigger `3a6597853a`, handoff g0 `5039ea2205`.

- Std: только форматирование (потоки токенов совпадают после нормализации трёх завершающих запятых) и регистрация после `mod rev2_u64_n14_n17;`; закреплённый rustfmt rc=0 на модуле, diff `verify.rs` равен унаследованному.
- Control: пересчёт строк якорей, overlay, bundle, хэшей и добавленное R1-звено цепочки `sources`; столбцы, селекторы, исходы, covers, лимиты и часы прежние. 509/509 привязок и 71/71 нативных координат совпадают с исходником.
- SHA-256 request `b4316967…3caf`, roster `2110ee32…`, bindings `d243f326…`, bundle `320e2eee…674d` (HEAD `c8eefae4c8`, prerequisite `dab03cf510`); trigger tree/parent; авторы; handoff `:165` исправлен; suite 128/128.
- Риск стоимости `PAIR-STEP` (R1-2) сохраняется как операционный.
