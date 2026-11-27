# REV2 u64 N14–N17 · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров нет. Пины: Std `53e733666ede6b256c84498a6dd350f1e84dddfb` / tree `b1d2c89975`, Control `e51c10547ddd19f1f63ec324cd1ee31fbf0c57c9` / tree `fe9dfbd9a9670cc435190210578d68fa7e363f4e`, review-trigger `7939187d40`, handoff g0 `173af2a2d5`.

1. Nit. Закреплённый rustfmt (nightly-2026-11-19) на `verify.rs:281–305` даёт diff порядка `mod`; тот же diff побайтно у parent `4d6dd50995`. Новые модули чисты. Формулировку handoff уточнить.
2. Nit, риск стоимости. Символический `r` в insert-step: `insert_tail` и циклы корня разворачиваются до 36, а не до 16; прогноз по u8 N17-INSERT-BYTES неприменим. Отсечка предусмотрена (раздельные `r`).
3. Операционно: `CH8_REV2_U64_N14_N17_TRIGGER_TREE` → `fe9dfbd9a9670cc435190210578d68fa7e363f4e`.

Проверено и в порядке: пост insert-step точно повторяет `smallsort.rs:706/725/731`, 10 covers; сквозные маски и четыре контроля с единственным отказом `SORTED_POPCOUNT`; компаратор — тот же `u64_less`; сравнения только скалярные, все циклы ≤32 итераций; Std-дельта 4 файла, N13 blob восстанавливается; пропуск submodule-проверки в синтетике штатный; SHA-256 request `6bf1706f…`, roster `1e76eb9f…`, bindings `36c08ae3…`, bundle `fbac6f36…` (HEAD `53e733666e`, prerequisite `dab03cf510`); trigger tree/parent; авторы; часы; suite 127/127. Оценка N17: 50–90 с VT, 2,5–3,2 GiB.

## R2 · FIX1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров нет. Пины: Std `fe8444d175ec1630155b886d54ce527ebbb6c415` / tree `fe97d2dd54`, Control `087843c161d70ec36f6533ba8dd39742bae922c4` / tree `b4bf21f6578d30d40f66fd296af4258b6b0bc390`, review-trigger `3570969428`, task g0 `5f7e0e78d7`, handoff g0 `acc002dadc`.

1. Nit. Единственность `p` обоснована аргументом (p = число слов ≤x) и Python-моделью, нативно не утверждается; vacuity нет. Отметить как внешний шаг.
2. Nit. Нативного отрицательного контроля для четырёх корней нет (не требовался); пост — точное скалярное равенство на каждом индексе.
3. Операционно: `CH8_REV2_U64_N14_N17_FIX1_TRIGGER_TREE` → `b4bf21f6578d30d40f66fd296af4258b6b0bc390`.

Проверено и в порядке: actual `insert_tail` с литеральным R, предпосылки и пост `smallsort.rs:706/725/731`, frame, covers, компаратор `u64_less`; символическим остаётся только `gap_guard.dst` (R+1 вариантов), ожидаемая стоимость на 1–2 порядка ниже прежнего корня; циклы ≤34; Std-дельта 3 файла, rustfmt rc=0; SHA-256 request `a70f7208…`, roster `a6eb6158…`, bindings `90bcab91…`, bundle `b3752a87…` (HEAD `fe8444d175`); авторы; часы; suite 128/128; пять переносимых слотов 45926757103 сверены по индексу `53452e1b…`.
