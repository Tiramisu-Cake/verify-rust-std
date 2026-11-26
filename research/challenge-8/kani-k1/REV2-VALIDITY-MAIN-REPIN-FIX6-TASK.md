# REV2 валидность · repin · FIX6 после ревью R5

Задание для **w11**, та же стадия. [Ревью R5](REV2-VALIDITY-MAIN-REPIN-REVIEW.md#r5--fix5): NO-GO, блокер B1.

1. **B1.** Точное допущение для `vv_network_nonzero_n10` ON. Допускается ровно одно свойство `unsupported_construct` на `smallsort.rs:423:28`:
   - функция `small_sort_network::<…NonZero<u8>…>`;
   - точный ID;
   - описание «`mutable cast` for `*mut [… NonZero<u8>; 32]`»;
   - статус только **SUCCESS**;
   - только при подтверждённом unwind-профиле, как у guard-семейств FIX3.

   Любой иной статус (FAILURE, UNDETERMINED, ERROR), иной тип, координата или функция дают MISMATCH. Проверь по receipts run 45870184232, есть ли такое же недостижимое `:423` у других корней B, которые идут через `small_sort_network` на нишевых типах, например n03 fallback. Если есть, допусти и их тем же точным правилом. Синтетика:
   - n10 ON с недостижимым emit даёт MATCH;
   - мутации FAILURE, тип, координата, лишнее свойство дают MISMATCH;
   - n18 ON без изменений.
2. **R5-3.** Covers n18: убрать тавтологию или переименовать. Достижимость `:423` фиксирует закреплённый FAILURE.
3. **R5-6.** В `cbmc_ignoring_warnings` добавить флаг полноты захвата (по `stream_metrics`).
4. **R5-1** принято координатором: холодный cap фазы A 30 с. **R5-2** (ранговый домен `char`) — оговорка в handoff. **R5-4 и R5-5** — без изменений.
5. Офлайн-replay A (18/18) и B старых receipts без падений. Suite на штатной и свежих шкалах, YAML, `bash -n`, `git diff --check`, rustfmt.
6. Пересоздай overlay, если меняются covers, и bundle. Затем control поверх `fc3a0e654e`, request, review-trigger с sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`.

Раздел **FIX6** в `REV2-VALIDITY-MAIN-REPIN-HANDOFF.md`: дельта, синтетика, новые пины, хэши, значение `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE`. Статус `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Не запускать CI, push, cargo, rustc, Kani, CBMC, не менять Actions variables, ничего не публиковать. Коммиты через `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`, `[skip ci]`, без знака решётки перед цифрой. Проверь author и committer. Сдай и остановись.
