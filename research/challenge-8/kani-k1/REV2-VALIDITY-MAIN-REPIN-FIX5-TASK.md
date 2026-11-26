# REV2 валидность · repin · FIX5 по разбору фазы B

Задание для **w11**, та же стадия. Координатор принимает [разбор](REV2-VALIDITY-MAIN-REPIN-B-ANALYSIS.md) (g0 `daf13e3d1a`) и предложение FIX5 из раздела 4 целиком, включая расширение окна B на 195 с, так что `sort8` сохраняет пару OFF/ON.

1. **Overlay `validity_main.rs`** по разделу 4:
   - указатель на чтение берётся до порчи и до чтения;
   - `bool` сравнивается через `u8`-ключи, `less` передаётся в проверку;
   - у `char` ранговый домен;
   - corrupt-слот без функциональной проверки;
   - `vv_network_nonzero_n10` (no-merge) и `vv_network_nonzero_n18` (только ON, `UNSUPPORTED_PINNED`).
2. **Fixture A:** четыре probe (`bool_order_probe`, `bool_order_u8_control`, `array_elem_cast_nonzero`, `array_elem_cast_u8_control`), каждый OFF/ON. Существующие 18 слотов и их replay не меняются.
3. **Гейт:**
   - классы `ASSERTION_FAILURE_PINNED` и `UNSUPPORTED_PINNED`;
   - `read_structures` для всех корней B с перепиновкой координат;
   - non-gating `cbmc_ignoring_warnings`;
   - общее правило unsupported не ослабляется.
4. **Часы:** окно B +195 с с переносом последующих дедлайнов в пределах прежнего job limit 140 мин. Если не укладывается, обоснуй и предложи вариант. Пределы слота 180 с cold wall / 120 с VT, caps 4 GiB.
5. **Синтетика и replay:**
   - синтетика на новые классы: точное свойство, лишний FAILURE, другой тип или координата, cover reachable у `UNSUPPORTED_PINNED`;
   - офлайн-replay фазы A run 45870184232 — 18/18 без изменений;
   - replay B того же прогона должен дать ожидаемые MISMATCH или INCOMPLETE по старым корням, без падений гейта;
   - suite на штатной и свежих шкалах, YAML, `bash -n`, `git diff --check`, rustfmt нового Rust-кода.
6. **Пересоздать** Std overlay (новый коммит поверх `bc866f8dfa` и bundle), control поверх `e2a3e6d48e`, request, review-trigger с sole parent `467af9cb8dba0e3be78a8d7d07672a1943c4806b`. Kani-кандидат и Std merge не меняются.

Раздел **FIX5** в `REV2-VALIDITY-MAIN-REPIN-HANDOFF.md`: дельта, roster A+B с ожиданиями, часы, тесты, новые пины, хэши и значение `CH8_REV2_VALIDITY_REPIN_TRIGGER_TREE`. Статус `READY_FOR_REVIEW`, `go=NOT_GRANTED`, `proof_credit=NONE`. Не запускать CI, push, cargo, rustc, Kani, CBMC, Actions variables не менять, ничего не публиковать. Коммиты через `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`, `[skip ci]`, без знака решётки перед цифрой. Проверь author и committer. Сдай и остановись.
