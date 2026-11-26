# REV2 валидность · repin · FIX4 после ревью R3

Задание для **w11**, та же стадия. Ревью R3 FIX3 — NO-GO с одним блокером в фазе B, остальная дельта FIX3 принята. [Ревью R3](REV2-VALIDITY-MAIN-REPIN-REVIEW.md#r3--fix3) · [Handoff FIX3](REV2-VALIDITY-MAIN-REPIN-HANDOFF.md#fix3-после-run-45857466917)

1. **Структурная группа typed read для корней B с `char`** (`vv_stable_char_n09`, `vv_stable_char_n09_corrupt`, `vv_sort8_char_n08`). Правило фиксирует структуру, а не ID, поэтому ID заранее знать не нужно. На `row.read` (file + line) должно быть ровно два validity-свойства, и у обоих:
   - column равен позиции `*` из `read.text` (для `:111` это 26; вычисляй так же, как 29 в A);
   - функция F из location одна и та же;
   - ID — `fullmatch` с `re.escape(F)+r'\.safety_check\.\d+'`, и ID различны;
   - класс `safety_check` указан и в поле, и в ID;
   - description точно ``Undefined Behavior: Invalid value of type `char` ``.

   Для отрицательного слота дополнительно:
   - множество всех FAILURE равно этой паре, и обе — FAILURE;
   - нужный cover в состоянии SATISFIED;
   - terminal FAILED, exit ≠ 0.

   Если свойств 1 или 3, если отличается column, функция или тип или если есть посторонний FAILURE, результат `MISMATCH`. У положительных слотов `read_binding=OBSERVED` только при той же структуре, иначе `UNKNOWN`. Для `bool` и `NonZeroU8` оставь прежнее правило или `UNKNOWN`. Каждое утверждение сверь по `check_values.rs` кандидата и обоснуй в handoff. Особо проверь: даёт ли каждое второе чтение (`:153` и другие `internal_reads`) ту же пару.
2. **Порядок решений** (R3, неблокирующее 1): условия `MISMATCH` (FAILURE не там, где ожидается, неверный terminal) вычисляются раньше ветки `guarded and not bound_complete → UNKNOWN`.
3. **Флаги CBMC** (R3, неблокирующее 2): добавь в отсекаемые `--depth`, `--unwindset`, `--no-assertions` и `--cover`, либо обоснуй белый список.
4. **Синтетические тесты** на B-правило: пара, одно свойство, три, другой column, другая функция, другой тип, посторонний FAILURE, отсутствие cover. Плюс тест на порядок решений из п. 2. Офлайн-replay 18 receipts A должен остаться 18/18. Suite на штатной и свежих шкалах, YAML, `bash -n`, `git diff --check`.
5. **Пересоздать пакет:** control поверх `0a4f85d930`, review-trigger с sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Если правило вносится в request, пересобери его и укажи новый SHA-256. Kani, Std merge, overlay, bundles, fixture и argv не меняются.

Раздел **FIX4** в `REV2-VALIDITY-MAIN-REPIN-HANDOFF.md`: дельта, обоснование по исходникам, тесты, новые пины и значение `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE`. `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Не запускать CI, push, cargo, rustc, Kani, CBMC, не менять Actions variables. Коммиты через `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`, `[skip ci]`, без знака решётки перед цифрой. Проверь author и committer. Сдай и остановись.
