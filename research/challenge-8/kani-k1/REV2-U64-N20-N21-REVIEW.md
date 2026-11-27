# REV2 u64 N20/N21 providers · ревью

## R1

Независимое ревью (Claude, `smallsort-reviewer`) 2026-11-27. **GO_WITH_NITS**, блокеров нет. Пины: Std `b09c6f22bfbd1ce8eb6afccf96df6b9a2ad3c54b` / tree `a784a8d12b`, Control `c4da71875efe80ebcfe78094afe6889a902d2da5` / tree `0d0857a039e5ffa263414952de49b716e3371c25`, review-trigger `3ef1c39493`, request `48f143cc…6a6c`, handoff g0 `66fb8b9cc4`.

1. Nit. Время suite в handoff `:157` (до 81,7 с) близко к лимиту шага `pins` 90 с; повтор ревьюера — 40–44 с на всех шкалах, вероятно нагрузка машины. Следить в прогоне.
2. Nit. В допуске явно перечислить внешние шаги: перенос sort9 по длине (B01 L09→L10, B11 L11→L10, guard `smallsort.rs:538`), driver `insertion_sort_shift_left` нативно не проверен (прямой `insert_tail`), центр N21 — транскрипция `:1027–1036`.
3. Операционно: новый trigger без `[skip ci]`; `CH8_REV2_U64_N20_N21_TRIGGER_TREE` → `0d0857a039e5ffa263414952de49b716e3371c25`.

Проверено и в порядке: геометрия пар и центра против `smallsort.rs:367–425, :965–1042`; вставки с литеральными параметрами; sort9 и swap B11; компаратор `u64_less`; оценка PAIR N20/N21 — VT 75–95 с, cold 120–140 с, CBMC 0,9–1,2 GiB (в лимитах, запас по VT невелик); циклы ≤34, только скалярные сравнения; Std-дельта 3 файла, rustfmt чист; SHA-256 request, roster `efe92715…`, bindings `80fa4950…`, bundle `02e9cbbd…` (HEAD `b09c6f22bf`); 87/87 координат; trigger tree/parent; авторы; часы (8 слотов, job 110 мин); suite 128/128.
