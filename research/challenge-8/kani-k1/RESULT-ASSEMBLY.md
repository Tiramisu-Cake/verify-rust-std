# ASSEMBLY — ordinary inventory и пять контролей приняты; controls inventory ожидается

Дата: 2026-10-31. Ветка `experiment/kani-k1-assembly-20261031`.
Library SHA `d4e5a0907b4d3e73b251afbc32b1bcdca58c8b18`.
Library tree `954e0becf8cb6c137ea89f94ad613d83d97235e0`.
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
G1 ordinary inventory: COMPLETE, actual182 = static182, точное множество имён совпало.
Request/source/Kani/artifact/name hashes, coverage0/80/160: PASS (`g1.inventory-check.json`).

Локально: source-transfer audit PASS, source scope/helper forecast PASS в обеих cfg.
Rustfmt заданным wrapper/config --check exit0; изменённые .rs ≤100 колонок.
Исходные items сохранены кроме cfg и одного указанного control cover.
G3: новых unused/dead_code/SmallSort helper warnings не найдено; есть старые manifest/
force-warn unstable core/lib.rs warnings. G1 targeted warnings: no match; G2 ещё ожидается.
Rust/cargo/Kani/CBMC локально не запускались.
Kani9461e07a, toolchain, flags, lane-файлы прежние.

G3 measurement: COMPLETE/gate true, Kani exit1 ожидаем; jobs1/controls:true, timeout600.
Ручная сверка summary locations с frozen source выполнена, каждый control FAILED ровно один раз:

| Harness (merge::) | FAILED/checks | Covers | Фактическая location |
|---|---:|---:|---|
| general_stable_direct_value_corruption_control_u64_n2 | 1/409 | 1/1 | merge.rs:846 |
| merge_scratch48_unsorted_halves_control_u64_n4 | 1/470 | 1/1 | smallsort.rs:842 |
| stable_direct_value_corruption_control_u64_n2 | 1/409 | 1/1 | merge.rs:846 |
| merge_aggregate_unsorted_halves_control_u64_n4 | 1/472 | 1/1 | smallsort.rs:842 |
| merge_aggregate_allocation_bounds_control_u64 | 1/16 | 1/1 | ptr/mod.rs:1981 |

Оба count FAILED — общий count-assert :846; sortedness :844 среди отказов отсутствует.
Terse output не печатает отдельный sortedness SUCCESS. Оба input FAILED — requires
merge_inputs_are_sorted; bounds — raw write за всей allocation48, не safe indexing.
Covers5/5; иных FAILED/compile/unsupported/TIMEOUT нет; sampled CBMC1.20GiB; OOM none_seen.
Source/request/pin/pool/tooling связаны: check-tooling PASS относительно GO `74f064bad9`.
`assembly/g3.controls-review.json`, `g3.summary.md`, `g3.peaks.txt`, `g3.tooling.txt`.
Historical donor SUCCESS/FAILED не выдаются за proof credit итогового library SHA.

Builds3/3; G1 cost$0.5535, G3 $0.1215; ledger spent$0.6750, G2 reserved$1.2150.
GO для `74f064bad9` получен; source/request/UUID ledger: `assembly/builds.json`.
Бюджет по NOTES $3,5. Запросы: ordinary30min, controls60min (как INTEG G2/G3),
measurement5×10min; setup30min/build; общий максимальный резерв $3.1050 ≤ $3.5.
T0 взят консервативно по initial TASK commit: 01:22:44 MSK; deadline04:22:44 MSK,
резерв закрытия15min. Перед каждым dispatch — fresh budget и полный envelope по остатку окна.
При нехватке окна/бюджета — PARTIAL; timeout600 не урезать. План в `assembly/window.json`.
Только k1-standard4, CAP_USD73.96 прежний. Library tree заморожен для всех трёх запросов.
Ожидание только k1g.sh watch с завершением хода; чтение только штатным K-1 интерфейсом.
Не проверены: controls inventory и его warnings, macOS, jobs3, полный CI организаторов.
Ветки submission не затрагивались; единственный полный CI выполняет координатор.

| Build | Назначение / статус | UUID |
|---|---|---|
| g1 | ordinary182 / exact PASS | 9fbe5d64-ff03-4fb4-a0d9-9ec92687e3d6 |
| g2 | controls463 / ожидается | 8d168cb0-f60f-41b1-8a8b-8822a2c7a59b |
| g3 | пять controls / PASS | b1cc9973-6a7d-4471-8e9f-6b5002a0c36f |
