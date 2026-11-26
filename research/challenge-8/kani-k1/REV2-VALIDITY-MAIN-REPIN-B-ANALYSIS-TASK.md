# REV2 валидность · разбор фазы B run 45870184232

Задание для **w11**, та же стадия. Нужен офлайн-разбор, нового прогона пока нет. Прогон по GO FIX4: job success, `diagnostic_status=INCOMPLETE_OR_UNEXPECTED`. [Артефакты](/root/ch8-artifacts/run-45870184232/ch8-rev2-validity-repin-Linux-X64-45870184232-1/) · [GO FIX4](REV2-VALIDITY-MAIN-REPIN-FIX4-GO.md) · [Handoff](REV2-VALIDITY-MAIN-REPIN-HANDOFF.md)

## Итог прогона (сводка координатора)

- **Фазы 0 и A — PASS, 18/18 MATCH.** Три отрицательных примера упали на привязанном typed read.
- **Setup фазы B — PASS.**
- **`vv_fallback_nonzero_n03`** OFF и ON — MATCH.
- **`vv_swap_bool_n02`** OFF и ON — MISMATCH: `VERIFICATION:- FAILED`, exit 1, wall 36–38 с. Единственный FAILURE — `validity_main::check_sorted_and_full_multiset::<bool, 2>.assertion.1` «normal return is sorted». Падает и OFF, то есть независимо от valid-value-checks.
- **`vv_network_nonzero_n19`** ON — MISMATCH. Единственный FAILURE — `small_sort_network::<NonZero<u8>, …>.unsupported_construct.1` «Kani currently doesn't support checking validity of `mutable cast` for `*mut [NonZero<u8>; 32]`». OFF — TIMEOUT.
- **TIMEOUT 180 с cold wall** (exit −15, фаза cbmc): `vv_stable_char_n09` OFF/ON, `vv_stable_char_n09_corrupt` OFF/ON, `vv_sort8_char_n08` OFF/ON, `vv_network_nonzero_n19` OFF.

## Что разобрать

1. **`swap_bool_n02` — главный вопрос.** `swap_if_less` (`smallsort.rs:468–499`) выбирает указатели через `hint::select_unpredictable` и копирует один элемент `bool`. Нужно решить, что это: ложный контрпример Kani или дефект fixture.
   - Сверь с открытым kani#5104 («False counterexample for a conditional pointer read of `[u8; 1]`») и с фикстурами array-selection из pr752.
   - Проверь, как `select_unpredictable` на `*mut bool` кодируется на кандидате `4caf097d84`: intrinsic, codegen, CBMC-выражение.
   - Ответь, почему ту же функцию для `u8`/`u64` pr752 проверяет успешно, а для `bool` нет.
   - Если по исходникам вывод не получить, предложи минимальный диагностический прогон: отдельный fixture swap `bool`/`u8`/`[u8;1]` OFF, с выводом трассы контрпримера (`--concrete-playback=print` или эквивалент в рамках argv-политики пакета). Пакет должен быть маленьким, Item 2.
2. **`mutable cast` в network ON.** Найди в `check_values.rs` место, где valid-value pass отказывается от `mutable cast` для `*mut [T; 32]`, и строку `smallsort.rs`, которая его порождает (scratch `MaybeUninit<[T; 32]>`?). Это ограничение Kani main, оно воспроизводимо и честно отмечено как unsupported. Сформулируй его для будущего описания pr752 и для решения, нужен ли upstream issue. Перед этим поищи дубликаты в model-checking/kani и приложи результат поиска. Ничего не публикуй.
3. **TIMEOUT.** Для `stable_char_n09`, `sort8_char_n08` и network n19 OFF оцени по receipts, какой длины или профиля хватит, чтобы уложиться в 120 с VT и 180 с cold wall. Смотри фазу на момент отсечки, первую CNF (если есть) и RSS. Варианты: меньшие N, отдельный `sort8` без stable-обвязки, network на минимальной длине с этим маршрутом. Цель — сохранить отрицательный контроль `char` в фазе B.
4. **Предложение следующего пакета (FIX5).** Roster, ожидания и изменения гейта. Сам пакет не собирай, пока координатор не примет разбор.

Сдай `REV2-VALIDITY-MAIN-REPIN-B-ANALYSIS.md` в g0 с координатами по пунктам 1–4. Статус `ANALYSIS_READY`, `proof_credit=NONE`. Не запускать CI, push, cargo, rustc, Kani, CBMC, не менять Actions variables. Коммит через `git -c user.name=Tiramisu-Cake -c user.email=igkharin@gmail.com`, `[skip ci]`, без знака решётки перед цифрой. Остановись после сдачи.
