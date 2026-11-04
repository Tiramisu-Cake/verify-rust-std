# SCRATCHGEOM — геометрия scratch для Stable Freeze

**Выдано координатором 2026-11-04 (ночь), пункт аудитов v7.** Dispatch только после exact-packet PRE-BUILD
review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-scratchgeom**, ветка **experiment/kani-k1-scratchgeom-20261104** от
  **59893bff1f**: upstream `233f96f66a`, Kani `cd355b0b`, library Part 1 v7, тулинг с потолком $120.
- Slug **scratchgeom**; stable owner — свободный на момент dispatch (указать в PRE-BUILD). Request_id
  `scratchgeom-*`.
- Project cap **$118.96**, свой cap **$1.40**. **Одна сборка**, retry нет. Один compile-error repair, если own spent
  + reserve ≤ cap. Tooling base: **59893bff1f**.
- Окно: main 150 + closeout 30 мин.

## Контекст

Stable Freeze (`<T as StableSmallSortTypeImpl>::small_sort(v, scratch, is_less)`) идёт в
`small_sort_general_with_scratch`. Функция:
- при `len < 2` выходит сразу, до проверки scratch;
- при `scratch.len() < len + 16` вызывает abort;
- иначе работает со scratch вызывающего.

Part 1 проверяет этот маршрут только с отдельной стековой аллокацией scratch на 48 элементов. Не проверены:
- минимальная допустимая ёмкость `len + 16`;
- другие ёмкости;
- `v` и `scratch` как непересекающиеся части одной аллокации.

## Что сделать

Новые корни в отдельном модуле `verify/scratchgeom.rs`. Регистрация в `verify.rs` — без cfg: это кандидаты в
ordinary. Тип u64, компаратор с произвольным ответом (как в safety-семействах Part 1), проверка — safety плюс
сохранение полного значения через существующие пробы, если они подходят. Каждый корень ≤ 60 с на GCB по оценке.

1. Минимальная ёмкость `scratch.len() == len + 16`: N2, N8, N17 (и N32, если оценка позволяет).
2. Ёмкость больше минимальной и не 48: например, N8 со scratch 40.
3. Одна аллокация: `v` и `scratch` — непересекающиеся части одного буфера. Например, общий
   `[MaybeUninit<u64>; N + N + 16]`, первые N инициализированы и отданы как `&mut [u64]`, остальное — как scratch.
   Взять N8, при запасе N17. Unsafe-код фикстуры с комментариями SAFETY; ordinary-корни не должны опираться на
   недоказанное.
4. Covers: возврат, и что маршрут действительно `small_sort_general_with_scratch` (например, через проверку
   `T: Freeze`, `!efficient` выбор маршрута, как в существующих dispatch-корнях).

Существующие корни и файлы v7 не менять, кроме регистрации модуля.

## Сборка и статика

- Статика: ordinary = 202 + новые; rustfmt; diff только `smallsort/verify*`.
- Kind diagnostic, `controls: false`, `inventory: true` (cfg-off список должен дать 202 + новые), jobs 1,
  `harness_timeout_minutes` 10. Строк ≤ 7.

## Коммиты, ожидание, RESULT

- Library- и research-коммиты отдельно, `[skip ci]`, push без force. Последней строкой
  `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.
- **RESULT-SCRATCHGEOM.md**, ≤ 25 строк: таблица строк (время, checks, covers), inventory, какие геометрии теперь
  проверены, кандидаты в ordinary v8 (≤ 60 с), что осталось.

## Запреты

- Только bounded evidence; raw logs и credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код и документация Kani; чужие PR не открывать.
- Runtime, workflows и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **SCRATCHGEOM ЗАВЕРШЁН**, затем стоп.
