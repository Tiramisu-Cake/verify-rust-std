# CORR14 — COMPLETE: split снижает CBMC-пик; jobs3 прошёл

Дата: 2026-10-31. Ветка `experiment/kani-k1-corrfourteen-20261031`.
Library SHA `2bc00fceee2d6afcaca8eb136e625064e5449f73`.
Frozen library tree `1a7403c9949e5749a9040127935f86b96cf66a27`.
G1 source/GO `3144dbe11c71dd61cfe655965079e960c1179d17`, request `corr14-g1-split-scratch-u8-n14-20261031`.
G1 UUID `9abed515-6cb8-48b3-91d3-57c7f4b98710`, Cloud FAILURE, verification COMPLETE.
G2 source `382139b06a31a97b245d6d6c5a767353faa53150`, request `corr14-g2-const-leaves-jobs3-20261031`.
G2 UUID `906b886b-481f-4312-8c40-e8c1684dd6d8`, Cloud SUCCESS, verification COMPLETE.
Свои builds2/2; costs G1$0.3375 + G2$0.2295 = $0.5670 из $2.3, reserved$0.
T0 07:34:39 UTC; работа до11:04:39, закрытие до11:34:39; резерв закрытия30min.
Обе сборки закончились к08:30:23 UTC; окно, envelopes и budgets соблюдены.

G1 measurement/jobs1/controls:true; timeout600, Kani9461e07a, стандартный пул16GB.
Все имена `correct::`; VT — seconds, CBMC RSS — per-process VmHWM KiB / 2s sampler.

| Гармоника | Маршрут | Scratch | Статус | VT | CBMC RSS KiB | Covers | Checks |
|---|---|---|---|---|---|---|---|
| sorted_permutation_general_stable_u8_n14 | combined | non-const48 + general | SUCCESS | 219.973 | 2237264 | 2/2 | 0/723 |
| sorted_permutation_general_u8_n14 | general | внутренний holder48 | SUCCESS | 134.542 | 1302032 | 1/1 | 0/723 |
| sorted_permutation_stable_nonconst_u8_n14 | stable | non-const48 | SUCCESS | 160.199 | 1294980 | 1/1 | 0/721 |
| sorted_permutation_stable_const_u8_n14 | stable | const48 | SUCCESS | 146.223 | 1293300 | 1/1 | 0/721 |
| sorted_permutation_stable_aggregate_u8_n14 | stable | aggregate48 | SUCCESS | 168.579 | 1300588 | 1/1 | 0/723 |
| stable_aggregate_value_corruption_control_u8_n14 | stable | aggregate48 | FAILED | 154.990 | 1352636 | 1/1 | 1/725 |
| stable_aggregate_allocation_bounds_control_u8 | raw write | aggregate48 | FAILED | 0.064 | MISSING | 1/1 | 1/16 |

Split: general + non-const stable воспроизводят прежние ветви/input/probe combined.
Fixed-route covers1/1 +1/1 объединяют прежние2/2. Максимум CBMC RSS ниже на41.80%:
2.134GiB →1.242GiB. Сумма VT294.741s против219.973s: +33.99%, выигрыша суммы VT нет.
Это эффект split по CBMC-пику, не доказательство снижения total/driver RSS или billed cost.
Форма scratch: const против non-const VT−8.72%, RSS−0.13%; выбран const для G2.
Aggregate против non-const VT+5.23%, RSS+0.43%: выигрыша здесь не показал.
Малые RSS-различия и одиночный замер не устанавливают механизм или устойчивый эффект.
Const/aggregate сохраняют T/F/N/input/probe-домен; aggregate — другая backing-геометрия,
не proof старой array-backed fixture и не transfer. `corr14/source-map.md`.

Оба контроля целевые, ручная сверка frozen source и log-lines выполнена:

- count: единственный FAILED1/725, covers1/1, correct.rs:259, corr14_check_u8_n14.
  Это полный probe_count_unrolled assert; sortedness:257 не среди FAILED.
  Общий private opt-in checker вызывается четырьмя positive и control после output[0]^=1.
  Log подтверждает actual lt_u8 function item и оба verified stub targets.
- bounds: единственный FAILED1/16, covers1/1, ptr/mod.rs:1981, ptr::write::<u8>.
  Raw write offset48 через adapter за всей allocation; object-bounds, не safe-index panic.

G1 gate=false / expectation_met=false / measurement_ok=false: expect_check запрашивал
placeholder, Kani вывел фактическое count-expression. Запрос/результаты не переписаны.
Это текстовое несовпадение matcher; ручная целевая проверка не объявляется зелёным gate.
Остальные5 positive SUCCESS, covers SATISFIED; иных FAILED/TIMEOUT/OOM нет.
Tooling/pool/source/request/name bindings PASS; sampled driver5.354GiB, total RSS7.124GiB.
Bounds RSS MISSING: процесс короче 2s sampling. `corr14/g1.controls-review.json`, `corr14/g1.metrics.json`.

G2 diagnostic/jobs3/controls:true: gate=true, Kani exit0, covers9/9, тот же library tree.
Допуск по строкам G1: выбранные SUCCESS/covers1/1, контроли целевые, CBMC-пик снижен.
VT shared-run seconds; RSS — direct per-process attribution, без вывода о jobs1 speedup.

| Гармоника | Маршрут | Scratch/fixture | Статус | VT | CBMC RSS KiB | Covers | Checks |
|---|---|---|---|---|---|---|---|
| correct::sorted_permutation_general_u8_n14 | general | внутренний holder48 | SUCCESS | 191.850 | 1301236 | 1/1 | 0/723 |
| correct::sorted_permutation_stable_const_u8_n14 | stable | const48 | SUCCESS | 209.529 | 1292448 | 1/1 | 0/721 |
| correct::contract_insert_tail_u8_scratch | callee | initialized scratch48 | SUCCESS | 356.452 | 4553476 | 6/6 | 0/440 |
| merge::merge_contract_u8_n14 | callee | merge N14 fixture | SUCCESS | 522.734 | 2052492 | 1/1 | 0/435 |

G2 sampled total RSS10.659GiB, simultaneous CBMC7.176GiB, driver5.507GiB; OOM none_seen.
Листья SUCCESS на собственных fixtures; это ресурсная проверка без transfer на scratch48 caller.
Source/request/names/tooling/pool bindings PASS для обеих сборок; `corr14/g2.metrics.json`.

Rustfmt заданным wrapper/config --check exit0; изменённый .rs ≤100 колонок.
Static source PASS: baseline побайтово прежний; общий checker равен прежнему oracle.
В library изменён только correct.rs; private opt-in +6, ordinary+0; lane/flags/pin прежние.
G1/G2 targeted unused/dead_code/never-used: no match; upstream manifest/unstable warnings есть.
Cfg off локально не компилировался; новые items полностью исключены. Rustc/cargo/Kani локально нет.

N13/N15: отдельно измерить split при приоритете памяти, учитывая рост суммы VT.
Const — кандидат для повторного matched замера; aggregate u8 N14 здесь не продвигать.
u64: отдельно matched split/формы с тем же oracle;
historical aggregate speedup не переносить на u8. N13/N15/u64 здесь не запускали.
Conditional caller: insert_tail/merge callee premises этих доменов остаются открытыми.
Fixture48 ≠ любой backing. macOS UNKNOWN. Пригодность подтверждает только CI организаторов.
Чтение результатов только k1g; ожидание через k1g watch с завершением хода.
