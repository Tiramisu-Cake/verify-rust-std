# ASSEMBLY — кандидат подготовлен, ожидается PRE-BUILD REVIEW

Дата: 2026-10-31. Ветка `experiment/kani-k1-assembly-20261031`.
Исходный HEAD `ddcc33f8370db08a316b739c5d543c4e96910b1b`.
Учтено обязательное дополнение `TASK-ASSEMBLY-NOTES.md`, commit `3b97f7dbd0`.
Library SHA `d4e5a0907b4d3e73b251afbc32b1bcdca58c8b18`.
Library tree `954e0becf8cb6c137ea89f94ad613d83d97235e0`.
Последний library-коммит отдельно от research: `d4e5a0907b` (только cfg-переключения).
Изменены только `verify/merge.rs` и `verify/types.rs`; production/oracle прежние.

| Изменение относительно INTEG | Ordinary | Opt-in |
|---|---:|---:|
| UNSTABLE8: DropKey N8 combined + два Cell N8 fixed-route | +3 | 0 |
| UNSTABLE8: combined Cell N8, DropKey N9 TIMEOUT diagnostics | 0 | +2 |
| Direct general/stable aggregate u64 N6..8, все шесть | +6 | 0 |
| C u64 N6..8 → retired duplicate | −3 | +3 |
| Три BACKING expected-fail controls | 0 | +3 |
| Итого | **182** | **281** |

Координатор подтвердил BACKING2 general N7 и stable N6/N7: SUCCESS, covers1/1,
checks0/407, CBMC≤0,99GiB; build `33e2c5fd-27ba-4cdb-89f9-474f51a3ac39`,
source `30b8b975c5`, library `f28909ac02`. Запись: `assembly/backing2-confirmation.json`.
Все шесть direct u64 N6..8 ordinary; C u64 N6..8 retired; pending0, retired16.
Combined B u64 N6/N7 классифицированы retired duplicate, в P2 не возвращаются.
A u64 N5..8 сохранены как historical-contract opt-in, также вне P2:
реальные direct proofs не используют эти stubs; старая stable array-backed fixture
не является проверкой новой aggregate fixture. Исторические A SUCCESS сохранены в scope.
A u8 N5..8 остаются positive-direct для P2. Combined B u64 N8 остаётся TIMEOUT opt-in.
Микропакета Part 2 нет: из Part 2 в Part 1 ничего не возвращено.

Источники перенесённых блоков, только library-diff:

- UNSTABLE8 `255935369e`, library `78c040559f`: пять cases, fixed-route helper/macro;
  Cell fixed-route — финальный G3, historical covers4/4.
- OPT `1354970c94`, library `f052d6b7ec`: general direct N6/N8.
- BACKING `a3e0dc4cda`, library `bff6e4863e`, measured source `740d22674c`:
  aggregate stable N8, adapter и три controls. BACKING2 code donor `f28909ac02`:
  general N7 и stable N6/N7; process confirmation получено от координатора.
- Карта старое → новое: `assembly/rename-map.tsv`; точные donor/measurement SHA,
  historical proof trees и статусы каждого блока: `scope/scope.tsv`.

Все шесть direct bodies используют произвольные input/probe, прежний lt_u64,
unwind34 и общий full-value oracle; stubs отсутствуют. General helper объединяет
разрешённые N6/N7/N8; относительный путь поправлен после переноса в родительский модуль.
Stable direct — другая fixture с aggregate holder48, не измерение старой array-backed.
Adapter сохраняет lifetime, provenance, alignment, extent, offset0; ссылок на uninit T нет.
Новые ordinary proofs/helpers не зависят от cfg-модулей opt_split/backing.
UNSTABLE fixed-route helper/macro разгейтированы, комментарий-история удалён.
B DIRECT corruption control получил cover возврата сортировки до порчи payload;
условия, mutation и общий oracle сохранены. Это дополнительная проверка на итоговом SHA.

Статические списки: Part 1 ordinary182, controls cfg463; expected-fail controls31.
Part 2 ordinary339, controls cfg463; expected-fail controls31.
Пересчёт P2: INTEG339 +3 UNSTABLE8 +6 direct −3 C −2 combined B −4 historical A =339.
P2 снимает budget/positive gates; pending/retired/TIMEOUT/negative/unsupported/historical A
сохраняет opt-in. Static apply patch и точное множество имён: PASS, `scope/pr2-static-check.json`.
Фактического inventory итогового дерева ещё нет; нужны два отдельных inventory builds.

Локально: source-transfer audit PASS, source scope/helper forecast PASS в обеих cfg.
Rustfmt заданным wrapper/config --check exit0; изменённые .rs ≤100 колонок.
Исходные items сохранены кроме cfg и одного указанного control cover.
Компиляторные warnings ещё не проверены; Rust/cargo/Kani/CBMC локально не запускались.
Kani9461e07a, toolchain, flags, lane-файлы прежние.

Контроли итогового кода пока не запускались. Подготовлен measurement jobs1/controls:true:

- DIRECT B `general_stable_direct_value_corruption_control_u64_n2`;
- DIRECT A `merge_scratch48_unsorted_halves_control_u64_n4`;
- BACKING `stable_direct_value_corruption_control_u64_n2`,
  `merge_aggregate_unsorted_halves_control_u64_n4`, `merge_aggregate_allocation_bounds_control_u64`.

Для count-controls gate сверяет placeholder: вручную установить единственный FAILED
на count-assert общего oracle по актуальной summary location итогового SHA.
Отсутствие sortedness FAILED в terse summary не выдавать за явную строку SUCCESS.
Unsorted-halves — merge_inputs_are_sorted; bounds — raw write за всей allocation48.
Проверить covers и отсутствие иных отказов; compile/unsupported/TIMEOUT не подходят.
Historical donor SUCCESS/FAILED не выдаются за proof credit итогового library SHA.

Своих builds0/3, spent$0, reserved$0; ledger `assembly/builds.json`.
Бюджет по NOTES $3,5. Запросы: ordinary30min, controls60min (как INTEG G2/G3),
measurement5×10min; setup30min/build; общий максимальный резерв $3.1050 ≤ $3.5.
T0 взят консервативно по initial TASK commit: 01:22:44 MSK; deadline04:22:44 MSK,
резерв закрытия15min. Перед каждым dispatch — fresh budget и полный envelope по остатку окна.
При нехватке окна/бюджета — PARTIAL; timeout600 не урезать. План в `assembly/window.json`.
Только k1-standard4, CAP_USD73.96 прежний. До GO dispatch запрещён; после GO tree заморожен.
Ожидание только k1g.sh watch с завершением хода; чтение только штатным K-1 интерфейсом.
Не проверены: inventories, warnings/controls, macOS, jobs3, полный CI организаторов.
Ветки submission не затрагивались; единственный полный CI выполняет координатор.
