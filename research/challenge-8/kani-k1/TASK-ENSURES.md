# ENSURES — порядок в контрактах настоящих хелперов через модель компаратора (спайк, шаг 3)

**Выдано координатором 2026-11-05 (ночь) после RESULT-REALCONTRACTSTWO (`588c002998`).** Dispatch только после
exact-packet PRE-BUILD review/GO координатора. Runtime **Codex**, одна стадия.

## Рабочее место и лимиты

- Worktree **/root/verify-rust-std-kani-ensures**, ветка **experiment/kani-k1-ensures-20261105** от **588c002998**.
  В ветке есть `requires`/`modifies` на пяти хелперах и их PFC.
- Slug **ensures**; stable owner — свободный на момент dispatch. Request_id `ensures-*`.
- Project cap **$118.96**, свой cap **$3.50**. **До двух сборок** (G2 только с новым GO). Один compile-error
  repair на сборку. Tooling base: **59893bff1f**.
- Окно: main 240 + closeout 30 мин.

## Цель

Safety-контракты на настоящих хелперах доказаны. Для корректности до порогов 16/32 нужны `ensures` о порядке и
перестановке, чтобы `stub_verified` на настоящих местах вызова давал сортировку без повторного раскрытия тел.

Для произвольного `FnMut` порядок не определён. Поэтому `ensures` должен быть условным: он утверждает порядок,
только когда `F` — канонический компаратор с известной моделью.

## Подход (проверить осуществимость)

1. Под `cfg(kani)` в `smallsort.rs` (или в verify-модуле, если так возможно) — trait-модель компаратора:
   - blanket default impl: «модели нет»;
   - специализированный impl для канонического компаратора, например `struct` с ручным `impl FnMut(&u64, &u64)`
     для строгого порядка u64; `core` уже использует `min_specialization`, а `fn_traits`/`unboxed_closures`
     доступны.
   Если специализация в этом месте недоступна, найти другой способ: например, const-маркер в trait с default
   методом. Точную причину записать.
2. **`insert_tail`:** `ensures` при каноническом `F`: если `begin..tail` отсортирован, то `begin..=tail`
   отсортирован, и мультимножество полных значений сохранено (проба `kani::any()` по полному значению, как в
   Part 1). Для неканонического `F` `ensures` тривиален.
3. **PFC** `insert_tail` с каноническим компаратором u64, backing 5, tail 1..4. Негативный контроль: мутант
   (например, consumer, который портит одно значение после stub) должен упасть на проверке сортированности.
4. **Consumer на настоящем месте вызова:** `insertion_sort_shift_left` (или Stable blanket entry через
   `insertion_sort_shift_left`) с каноническим компаратором и `#[kani::stub_verified(insert_tail)]`. Домен
   consumer должен совпадать с доказанным доменом PFC: тип, backing, tail. Проверка: сортированность всего среза
   и перестановка. Начать с N5; при успехе N8 и N16, если домен PFC позволяет. Иначе расширить PFC.

Тела и сигнатуры runtime-функций не менять. Всё новое — под `cfg(kani)`; PFC и consumers — в opt-in
`realcontracts.rs` (или новом opt-in модуле).

## Сборки

- **G1:** kind diagnostic, `controls: true`, jobs 1, лимит 10 мин. Строки: PFC `insert_tail` с `ensures`,
  негативный контроль, consumer N5, повтор одного существующего safety-PFC (регрессия). Не больше 6 строк.
- **G2** (с GO): consumer на больших N или `bidirectional_merge` с `ensures`.

## Коммиты, ожидание, RESULT

- Library- и research-коммиты отдельно, `[skip ci]`, push без force. Последней строкой
  `PRE-BUILD REVIEW <полный sha>`, стоп до GO.
- **Ожидание: `research/challenge-8/kani-k1/tools/k1g.sh watch BUILD`**, затем завершить ход.
- **RESULT-ENSURES.md**, ≤ 35 строк:
  - механизм модели;
  - точный текст `ensures`;
  - таблица строк;
  - совпадение доменов consumer и PFC;
  - что это даёт для корректности до 16/32;
  - что не получилось и почему.

## Запреты

- Только bounded evidence; raw logs и credentials не читать.
- Никаких локальных cargo/rustc/Kani/CBMC, Actions/PR/issue.
- Только наш код, наши RESULT и документация Kani; чужие PR, их ветки и код не открывать.
- Тела runtime, workflows и tooling не менять.

Маркеры `REVIEW REQUEST <sha>` / **ENSURES ЗАВЕРШЁН**, затем стоп.
