# ASSEMBLY — кандидат подготовлен, ожидается PRE-BUILD REVIEW

Дата: 2026-10-31. Ветка `experiment/kani-k1-assembly-20261031`.
Исходный HEAD `ddcc33f8370db08a316b739c5d543c4e96910b1b`.
Library SHA `a4b4a3ca33653f5563e2cc57be6e2a6f58c493b9`.
Library tree `3548f769bc3c1c68ff7aa01c56e100ba0f27fbb7`.
Изменены только `verify/merge.rs` и `verify/types.rs`; production/oracle прежние.

| Изменение относительно INTEG | Ordinary | Opt-in |
|---|---:|---:|
| UNSTABLE8: DropKey N8 combined + два Cell N8 fixed-route | +3 | 0 |
| UNSTABLE8: combined Cell N8, DropKey N9 TIMEOUT diagnostics | 0 | +2 |
| Direct general u64 N6/N7/N8 и stable aggregate N8 | +4 | 0 |
| Stable aggregate u64 N6/N7: ожидают подтверждения координатора | 0 | +2 |
| C u64 N8 → retired duplicate; C N6/N7 остаются ordinary | −1 | +1 |
| Три BACKING expected-fail controls | 0 | +3 |
| Итого | **182** | **281** |

Условность N6/N7: сообщение о SUCCESS координатора пока не получено.
В BACKING2 summary уже записаны SUCCESS, но процессный gate им не заменён.
После подтверждения: stable N6/N7 → ordinary, C N6/N7 → retired; числа сохранятся.
Прежние combined DIRECT B u64 N6/N7 и A u64 остаются positive opt-in;
combined B u64 N8 остаётся TIMEOUT opt-in. Из Part 2 в Part 1 ничего не возвращено.

Источники перенесённых блоков, только library-diff:

- UNSTABLE8 `255935369e`, library `78c040559f`: пять cases, fixed-route helper/macro.
- OPT `1354970c94`, library `f052d6b7ec`: general direct N6/N8.
- BACKING library `bff6e4863e`, BACKING2 `f28909ac02`: aggregate stable N6..8,
  general N7, adapter `scratch_view` и три negative controls.
- Полная карта старое → новое, включая controls: `assembly/rename-map.tsv`.
  `opt_split::general_direct_*` → `merge::general_direct_*`;
  `backing::general_direct_*` → `merge::general_direct_*`;
  `backing::stable_direct_*` → `merge::stable_direct_*`.

Все шесть direct bodies используют произвольные input/probe, прежний lt_u64,
unwind34 и общий full-value oracle; stubs отсутствуют. General helper объединяет
разрешённые N6/N7/N8; относительный путь поправлен после переноса в родительский модуль.
Stable вызывает тот же trait-вход с aggregate holder48; adapter сохраняет lifetime,
provenance, alignment, extent, offset0; ссылок на неинициализированный T не создаёт.
Новые ordinary proofs/helpers не зависят от cfg-модулей opt_split/backing.
UNSTABLE fixed-route helper/macro разгейтированы, комментарий-история удалён.

Статические списки: Part 1 ordinary182, controls cfg463; expected-fail controls31.
Part 2 ordinary345, controls cfg463; expected-fail controls31.
Part 2 = Part 1 + budget-gates + positive DIRECT; pending/retired/TIMEOUT/controls
не возвращает. Patch и списки: `scope/pr2-ungate.patch`, `scope/*ordinary.txt`.
Это прогноз исходника; фактического inventory итогового дерева ещё нет.
Совпадение имён требуется проверить после двух отдельных inventory builds.

Проверки локально: source-transfer audit PASS; production/comparator совпадают с donors;
исходные items сохранены кроме cfg. Rustfmt заданным wrapper/config: --check exit0.
Изменённые .rs: строки ≤100. Helper-use forecast: новых unused-кандидатов нет в обеих cfg.
Компиляторные предупреждения ещё не проверены; Rust/cargo/Kani/CBMC локально не запускались.
Kani9461e07a, toolchain, flags, lane-файлы не менялись.

Контроли на итоговом коде пока не запускались. Подготовлен measurement из пяти:

- DIRECT B: `general_stable_direct_value_corruption_control_u64_n2`;
- DIRECT A: `merge_scratch48_unsorted_halves_control_u64_n4`;
- BACKING: `stable_direct_value_corruption_control_u64_n2`,
  `merge_aggregate_unsorted_halves_control_u64_n4`,
  `merge_aggregate_allocation_bounds_control_u64`.

Для обоих count-контролей gate проверяет только placeholder. Нужна ручная сверка:
единственный FAILED на count-assert `assert_sorted_and_probe_preserved`, merge.rs:846;
sortedness-assert :844 должен пройти. Пока это ожидаемые locations, не результат.
Unsorted-halves ожидает merge_inputs_are_sorted; bounds — pointer outside object bounds.
Historical donor SUCCESS/FAILED не выдаются за proof credit итогового library SHA.

Своих builds0/3, spent$0, reserved$0; список `assembly/builds.json` пуст.
Проверены три запроса: inventory ordinary30min, controls50min, measurement5×10min,
включая setup30min на build: максимальный суммарный резерв $2.9700 ≤ $3.
Только k1-standard4; CAP_USD73.96 не менялся. Перед каждым dispatch повторить budget.
Ожидание сборок — только k1g.sh watch с завершением хода; до GO dispatch запрещён.
Результаты читать штатным K-1 summary/peaks/inventory/log-grep/log-lines/check-tooling.
Не проверены: фактические inventories, warnings/controls, macOS, jobs3 на итоговом наборе,
полный CI организаторов. Ветки submission не затрагивались.
