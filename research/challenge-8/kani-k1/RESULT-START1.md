# START1 — PARTIAL: кандидат подготовлен, сборок ещё нет

Ветка `experiment/kani-k1-startone-20261031`; исходный SHA `ebd0eac322`.
Library SHA `b98ee415fdfa69b683ebac7e627811b0ccb2aa1a`.
Library tree `6008ba7c2349d4158e2898f323089c2ef61d373c`.
Стадия: обязательный pre-build review/GO; dispatch не выполнен.
Build ID отсутствует; стоимость своих сборок $0; лимит 2 сборки / $2,2.

| Гармоника / tail-группа | Статус | VT | CBMC RSS | Covers | Checks |
|---|---|---|---|---|---|
| START1 baseline, 2..16 | NOT_RUN | — | — | — | — |
| START1, 2..8 | NOT_RUN | — | — | ожидаются 9/9 | — |
| START1, 9..12 | NOT_RUN | — | — | ожидаются 6/6 | — |
| START1, 13..16 | NOT_RUN | — | — | ожидаются 6/6 | — |

Полнота: [2,8] ∪ [9,12] ∪ [13,16] = {2,…,16}; 7+4+4=15.
Пересечений нет: 8<9 и 12<13; пробелов нет: 8+1=9 и 12+1=13.
Константы требуют START=1, START<LO≤HI<17; selector отсутствует.
Backing ровно `[u64;17]`; arbitrary full u64 input/probe, `lt_u64`, unwind25.
`proof_for_contract(insert_tail)` задаёт actual requires, включая sorted prefix;
дополнительных sorted-prefix assumptions нет. Проверяются prefix до begin и suffix после tail.
Cover движения, end reached и каждый tail группы сохранены.
Новые PFC/helpers/macro только под `kani_smallsort_controls`.
Baseline `insert_tail_value`/`insert_tail_contract_case!` и остальные исходные items побайтно прежние.

Оба контроля используют тот же `insert_tail_start1_frame`, что положительный helper.
Prefix: tail2, cover перед порчей `v[0]=pre[0]^1`, ожидается prefix-frame FAILED.
Suffix: tail15, cover перед порчей `v[16]=pre[16]^1`, ожидается suffix-frame FAILED.
Ожидаемые locations общего checker: network.rs:1262 (prefix), :1265 (suffix).
Фактические locations и отсутствие иных отказов пока НЕ проверены.

G1: measurement/jobs1/controls:true; baseline expect SUCCESS согласно lane.
Manual gate: три группы SUCCESS≤600с со всеми covers, два контроля FAILED на нужных locations.
Baseline TIMEOUT может сделать aggregate gate false и не подменяет manual gate.
G1 envelope 90min/$1,215; только при gate успехе G2 diagnostic/jobs3/controls:true:
три группы + ordinary `network_safety_unstable_u64_n0_to17`, envelope70min/$0,945.
Итого160min/$2,160≤$2,2; перед dispatch нужны T0, budget, остаток окна и резерв закрытия30min.
Jobs3/перекрытие/OOM пока UNKNOWN; фактические UUID/request SHA будут записаны в start1/builds.json.

Статика Python PASS: точный partition, tail covers, shared checker, неизменность исходных items.
Заданный rustfmt --check exit0; изменённый .rs ≤100 колонок; git diff --check PASS.
Локальные rustc/cargo/Kani/CBMC не запускались; новые compiler warnings ещё не проверены.
Pin Kani9461e07a/toolchain/flags/lane-файлы прежние, CAP_USD73.96 не изменён.
Кандидаты для Part2 — три group-PFC, принятие зависит от G1/G2; Part1 пока не предлагается.
Домен exact `[u64;17]`/START1 не равен START0/scratch17/48; macOS UNKNOWN.
Пригодность замены устанавливает только CI организаторов; proof credit пока отсутствует.
