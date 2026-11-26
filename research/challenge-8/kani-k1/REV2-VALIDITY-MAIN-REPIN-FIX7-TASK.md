# REV2 валидность · repin · FIX7: TIMEOUT фазы B

Задание для **w11**, новая стадия. Прочитай сначала раздел FIX6 в [handoff](REV2-VALIDITY-MAIN-REPIN-HANDOFF.md#fix6-после-ревью-r5), [ревью R6](REV2-VALIDITY-MAIN-REPIN-REVIEW.md) и свой [разбор фазы B](REV2-VALIDITY-MAIN-REPIN-B-ANALYSIS.md). Решение о направлении — за тобой и координатором, владелец делегировал.

## Итог run 45886041869 (сводка координатора)

[Артефакты](/root/ch8-artifacts/run-45886041869/ch8-rev2-validity-repin-Linux-X64-45886041869-1/) · строка ledger с этим run ID.

- Фаза 0 PASS, A 18/18, пробы A 8/8, setup B PASS.
- B 9/13 MATCH: `swap_bool` OFF/ON, `fallback_nonzero` OFF/ON, `stable_char_n09_corrupt` OFF MATCH и ON упал на привязанном typed read, `sort8_char` OFF/ON (VT 62/110 с), network n18 ON — `MATCH_KNOWN_LIMITATION`.
- **TIMEOUT:** `vv_stable_char_n09` OFF и ON, `vv_network_nonzero_n10` OFF и ON.

Отрицательный контроль `char` на stable-маршруте пойман. Не хватает парного положительного ON на том же маршруте и сети на нишевом типе в лимитах.

## Что сделать

1. **Разбор TIMEOUT по receipts** четырёх слотов: фаза на момент отсечки, первая CNF, если есть, RSS, VT. Сравни с `stable_char_n09_corrupt` и `sort8_char`, которые уложились.
2. **Выбрать изменения roster**, чтобы оба маршрута уложились в 120 с VT, 180 с cold wall и 4 GiB. Варианты, решай сам по данным:
   - меньшая длина на том же маршруте, если он сохраняется: stable `small_sort_general_with_scratch`, network без merge;
   - разделение корней: ON-корень только на отсутствие нарушений валидности, без функционального постусловия, а порядок и кратности — в OFF-корне;
   - иная форма входа.
   Положительный ON и отрицательный контроль должны идти по одному маршруту и проходить одни и те же места чтения. Пары, которые уже MATCH, не трогать.
3. Kani-кандидат `4caf097d84`, Std merge и workflow не менять. Gate менять только под новые слоты, с синтетикой на каждую новую ветку решения.
4. Офлайн-replay старых receipts без падений. Suite на штатной и свежих шкалах, YAML, `bash -n`, `git diff --check`, rustfmt для Rust overlay.
5. Пересоздать overlay, bundle, request и control поверх `1338213af7`, review-trigger с sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Значение `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE` укажи в handoff, менять будет координатор.

Раздел **FIX7** в `REV2-VALIDITY-MAIN-REPIN-HANDOFF.md`: разбор по п. 1 с цифрами, выбранный roster и почему, ожидания, дельта gate, тесты, пины, хэши. Статус `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`, ledger Item 2.

Не запускать CI, push, cargo, rustc, Kani, CBMC, не менять Actions variables, ничего не публиковать. Коммиты в ветку `experiment/kani-k1-kani3300g0-20261111` через `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`, `[skip ci]`, без знака решётки перед цифрой. Перед заморозкой проверь author и committer. Сдай раздел и остановись.
