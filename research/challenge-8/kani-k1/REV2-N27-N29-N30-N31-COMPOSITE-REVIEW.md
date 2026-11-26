# REV2 copy-back/frame N27/N29/N30/N31 · независимое ревью R1

**GO_WITH_NITS**, блокеров нет. Ревьюер Claude (smallsort-reviewer, read-only), 2026-11-26.

Пины:
- Std `ee9eccad17d08988300e5b9e9e18d821889cdc92` (tree `b242e0d68a`, parent `50609bb850`);
- control `17d0184168945306f80352c70993c215bef40c92` (tree `16daa4eabbb186bd4822fbe79a3d56dfb74d89a7`, parent `a02a710c0c`);
- review-trigger `f922daa92a` (тот же tree, sole parent `467af9cb8d`);
- handoff g0 `f2e6f78ba0`.

Хэши совпали: request `68289a93…`, roster `6206fc1d…`, bindings `f43a4466…`, bundle `2f3cc016…` (57 590 байт). [Задание](REV2-N27-N29-N30-N31-COMPOSITE-TASK.md) · [Handoff](REV2-N27-N29-N30-N31-COMPOSITE-HANDOFF.md)

## Неблокирующее

1. **Нет символьного сквозного натива.** Для N27/N29/N30/N31, в отличие от N26/N28/N32, сквозное нативное свидетельство — только четыре конкретные маски. В строке допуска написать прямо: positives с `RSS_LIMIT` опорой не служат, полный домен закрывает композиция.
2. **У нового корня нет своего различающего контроля** (например, `count=N−1` с ожиданием FAILED). Задание велит переиспользовать контроли. Пустоту исключает cover после assertions (`rev2_n26_n31_copy_back.rs:63`).
3. **Grouped copy ID на actual маршруте агрегируют шесть вызовов** (`smallsort.rs:362/425/722/885/918/1034`). В новом корне вызов один (`46:14`), а `ptr::read`/`ptr::write` идут не через `copy_nonoverlapping`, поэтому группа относится ровно к целевой копии. Записать в admission.
4. **Регистрация через одиночный `cfg`** вместо `all(...)`. Задание это допускает, layout-check адаптирован.

## Проверено

- **Модуль.** 4 plain-корня (N31/N27/N29/N30), `unwind(36)`. Источник произвольный, в живой scratch32 записаны только первые N байтов, хвост не читается. `v_base` из `backing[1..1+N]`. Один `ptr::copy_nonoverlapping::<u8>(scratch, v_base, N)` той же формы, что `smallsort.rs:425:9`. Посты `DEST_EQUALS_SOURCE`, `SOURCE_PREFIX_FRAME` и `V34_FRAME` побайтно, cover после них. Нет assume, stubs, Replace и loop contracts. Runtime и прежние модули побайтно прежние.
- **Граф рёбер.** Половины, вставки, пары и D[m] сходятся с `smallsort.rs:383–425` и admission половин. Маски контролей пересчитаны. Конечный пост и frame есть, недостающих рёбер нет. Внешние шаги помечены.
- **Исторические контроли.** Index `8a8ff141…`, все 16 receipt/projection совпадают. Единственный FAILURE — `.assertion.17`. Q/V34 frame SUCCESS, `AFTER_COPY_BACK` SATISFIED, copy ID SUCCESS.
- **Control.** Roster из 4 строк. Discovery: 90 исторических записей плюс 4 новых, guard `not targets`. Часы и лимиты по заданию. Trigger gate на новой переменной, `test_supervisor.py` `df63a457`, `projection_truncated` в гейте.
- **Suite и форматирование.** Suite 123/123 OK в чистом clone. rustfmt и `git diff --check` чистые, YAML разбирается, `bundle verify` PASS. Авторство в порядке.

NOT_RUN: cargo, rustc, Kani, CBMC; шкалы 1/5/60 с (у автора 123/123); `bash -n`; синтетические finish/upload на trigger; хэши исторических опор half/merge/M31 (из принятых admission).

Решение координатора: замечания 1 и 3 учесть в admission. Замечание 2 принимается, повторный FIX не нужен. Пакет передаётся на GO. Запуск — после прогона валидности 45886041869.
