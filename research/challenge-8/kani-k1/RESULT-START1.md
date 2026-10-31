# START1 — COMPLETE

Дата 2026-10-31; ветка `experiment/kani-k1-startone-20261031`, база `ebd0eac322`.
Library SHA `b98ee415fdfa69b683ebac7e627811b0ccb2aa1a`.
Library tree `6008ba7c2349d4158e2898f323089c2ef61d373c` одинаков для G1/G2 и финала.
Review/GO координатора получен для `68f278703397a297acd9122ce718f13766aa3f38`.

| Build | Source SHA | UUID | Стоимость |
|---|---|---|---|
| G1 measurement/jobs1 | 68f2787033 | e07bbced-be41-48cf-ad6a-0f46876e8462 | $0,4860 |
| G2 diagnostic/jobs3 | bb7458fe52 | 99bf7d2a-e175-437d-9ad7-7e3d525cf8f3 | $0,2295 |

Сборок 2/2; итого $0,7155≤$2,2, резерв $0. Обе сборки: пул k1-standard4, Linux16GiB/4CPU.
Оба запроса: controls:true, timeout600, uninit checks off. Baseline сохранён opt-in.

| G1: гармоника / tail-группа | Статус | VT, с | CBMC RSS, GiB | Covers | Checks |
|---|---|---:|---:|---:|---:|
| START1 baseline, 2..16 | TIMEOUT600 | MISSING | 2,856 | MISSING | MISSING |
| START1, 2..8 | SUCCESS | 328,843 | 2,851 | 9/9 | 0/428 |
| START1, 9..12 | SUCCESS | 307,666 | 2,853 | 6/6 | 0/428 |
| START1, 13..16 | SUCCESS | 356,563 | 2,856 | 6/6 | 0/428 |

Три положительных имени: `network::insert_tail_contract_u64_start1_tail2_to8`,
`..._tail9_to12`, `..._tail13_to16`. Каждая группа: движение + end + каждый tail cover.
Полнота: [2,8] ∪ [9,12] ∪ [13,16] = {2,…,16}; 7+4+4=15.
Пересечений нет: 8<9 и 12<13; пробелов нет: 8+1=9 и 12+1=13.
Const asserts: START=1, START<LO≤HI<17; tail any_where(LO≤t≤HI), selector отсутствует.
Backing exact `[u64;17]`; full arbitrary u64 input/probe, set_value_probe, lt_u64, unwind25.
PFC(insert_tail) задаёт actual requires, включая sorted prefix; добавленных assumptions нет.
Prefix до begin и suffix после tail проверяются общим insert_tail_start1_frame.
Новые PFC/helpers/macro только под kani_smallsort_controls; baseline/helper/macro прежние.
Остальные исходные items побайтно сохранены; library-diff только verify/network.rs (+106 строк).

Оба обязательных контроля проверены вручную по summary и frozen source G1:

| Control START1 | VT, с | Checks | Covers | CBMC RSS, GiB | FAILED location |
|---|---:|---:|---:|---:|---|
| prefix_frame_control | 8,054 | 1/424 | 1/1 | 0,161 | network.rs:1262 |
| suffix_frame_control | 49,887 | 1/426 | 1/1 | 0,785 | network.rs:1265 |

Полные имена имеют prefix `network::insert_tail_contract_u64_start1_`.
Locations именно в insert_tail_start1_frame, не в старом insert_tail_value :1247/1250.
Prefix: tail2, после вызова v[0]=pre[0]^1; suffix: tail15, v[16]=pre[16]^1 (in bounds).
Оба достигли собственного cover перед порчей и вызвали тот же checker, что positive helper.
Ровно по одному intended frame FAILED; иных отказов/compile errors у controls нет.
Kani выдал placeholder сообщения вместо текста assert; location подтверждает класс отказа.
G1 summary COMPLETE, Cloud Build FAILURE, aggregate gate false: baseline TIMEOUT и
несовпадение expect_check с placeholder. Manual gate PASS по всем строкам и locations.
Группы unreachable36 каждая, controls40/36; это отдельно от failed/checks.
G1 sampled sum RSS3,593GiB, simultaneous CBMC2,833GiB; dmesg OOM none_seen.

| G2 jobs3: группа / ordinary | Статус | VT, с | CBMC RSS, GiB | Covers | Checks |
|---|---|---:|---:|---:|---:|
| START1, 2..8 | SUCCESS | 326,295 | 2,851 | 9/9 | 0/428 |
| START1, 9..12 | SUCCESS | 334,649 | 2,855 | 6/6 | 0/428 |
| START1, 13..16 | SUCCESS | 417,469 | 2,855 | 6/6 | 0/428 |
| network_safety_unstable_u64_n0_to17 | SUCCESS | 215,043 | 3,559 | 19/19 | 0/312 |

G2 COMPLETE/SUCCESS, gate true, Kani exit0; unreachable36/36/36/18.
Наблюдались 3 CBMC одновременно: safety+9..12+13..16, затем 2..8+9..12+13..16.
Direct metadata attribution всех 4 PID однозначна; intervals/точные KiB в start1/g2.review.json.
Общий sampled RSS8,632GiB, simultaneous CBMC8,607GiB на s176; OOM none_seen, missing нет.
Sampling2s; RSS — сумма процессов, не физическая память. Время jobs3 — shared-run diagnostic.
Whole-run wall с компиляцией: G1 28:54, G2 10:10; не включает весь Cloud setup/оплату.

Source/request SHA/UUID и точные множества ожидаемых имён связаны: G1 6/6, G2 4/4.
check-tooling PASS: G1 относительно GO SHA, G2 относительно исходного ebd0eac322.
Requests, ручные reviews, budget/window/preflights: start1/; ledger: start1/builds.json.
Pin Kani9461e07a/toolchain/flags/lane-файлы и CAP_USD73.96 прежние.
Rustfmt заданным wrapper/config --check exit0; .rs ≤100 колонок; diff --check PASS.
Python static audit PASS: partition/covers/cfg/shared checker/неизменность исходных items.
В controls cfg G1/G2 targeted unused/dead_code/warning codes/errors — no match;
прежние manifest/force-warn unstable warnings сохранены. Cfg-off без новых items (static);
отдельная ordinary cfg сборка не делалась. Локальные rustc/cargo/Kani/CBMC не запускались.
Оба ожидания только k1g.sh watch с завершением хода; результаты только штатным k1g.sh.
T0 10:37:45 MSK, deadline14:37:45, резерв закрытия30min; завершено внутри окна.
До dispatch проверены полные envelope90/70min и бюджеты; итоговых затрат $0,7155.

Кандидаты для замены START1 в Part2 — все три group-PFC вместе; baseline остаётся opt-in.
Полный START1 partition доказан на этом library tree; RSS групп против baseline не уменьшился.
В Part1 не предлагаются: G1 VT308–357с выше safety215с; это не дешёвое добавление.
Только exact `[u64;17]`/START1; не START0/scratch17/48. macOS UNKNOWN, Linux не заменяет macOS.
Пригодность для submission устанавливает только CI организаторов; полный CI/P2 не запускался.
Submission-ветки и production/oracle/lane-файлы не затрагивались.
