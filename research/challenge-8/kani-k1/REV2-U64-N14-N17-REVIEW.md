# REV2 u64 N14–N17 · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров нет. Пины: Std `53e733666ede6b256c84498a6dd350f1e84dddfb` / tree `b1d2c89975`, Control `e51c10547ddd19f1f63ec324cd1ee31fbf0c57c9` / tree `fe9dfbd9a9670cc435190210578d68fa7e363f4e`, review-trigger `7939187d40`, handoff g0 `173af2a2d5`.

1. Nit. Закреплённый rustfmt (nightly-2026-11-19) на `verify.rs:281–305` даёт diff порядка `mod`; тот же diff побайтно у parent `4d6dd50995`. Новые модули чисты. Формулировку handoff уточнить.
2. Nit, риск стоимости. Символический `r` в insert-step: `insert_tail` и циклы корня разворачиваются до 36, а не до 16; прогноз по u8 N17-INSERT-BYTES неприменим. Отсечка предусмотрена (раздельные `r`).
3. Операционно: `CH8_REV2_U64_N14_N17_TRIGGER_TREE` → `fe9dfbd9a9670cc435190210578d68fa7e363f4e`.

Проверено и в порядке: пост insert-step точно повторяет `smallsort.rs:706/725/731`, 10 covers; сквозные маски и четыре контроля с единственным отказом `SORTED_POPCOUNT`; компаратор — тот же `u64_less`; сравнения только скалярные, все циклы ≤32 итераций; Std-дельта 4 файла, N13 blob восстанавливается; пропуск submodule-проверки в синтетике штатный; SHA-256 request `6bf1706f…`, roster `1e76eb9f…`, bindings `36c08ae3…`, bundle `fbac6f36…` (HEAD `53e733666e`, prerequisite `dab03cf510`); trigger tree/parent; авторы; часы; suite 127/127. Оценка N17: 50–90 с VT, 2,5–3,2 GiB.
