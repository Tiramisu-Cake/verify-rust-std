# START1 — PARTIAL: G1 manual gate PASS, G2 запущен

Ветка `experiment/kani-k1-startone-20261031`; исходный SHA `ebd0eac322`.
Library SHA `b98ee415fdfa69b683ebac7e627811b0ccb2aa1a`.
Library tree `6008ba7c2349d4158e2898f323089c2ef61d373c`.
Review/GO для `68f2787033` получен; G1 выполнен на этом SHA.
G1 UUID `e07bbced-be41-48cf-ad6a-0f46876e8462`; стоимость $0,486.
Лимит 2 сборки / $2,2; T0 10:37:45 MSK, deadline14:37:45 MSK, закрытие30min.

| Гармоника / tail-группа | Статус | VT | CBMC RSS | Covers | Checks |
|---|---|---|---|---|---|
| START1 baseline, 2..16 | TIMEOUT600 | MISSING | 2,856GiB | — | — |
| START1, 2..8 | SUCCESS | 328,843с | 2,851GiB | 9/9 | 0/428 |
| START1, 9..12 | SUCCESS | 307,666с | 2,853GiB | 6/6 | 0/428 |
| START1, 13..16 | SUCCESS | 356,563с | 2,856GiB | 6/6 | 0/428 |

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
Ручная сверка summary с frozen source: FAILED в общем checker network.rs:1262/1265,
не в старом insert_tail_value :1247/1250. Prefix8,054с, 1/424 checks, covers1/1, RSS0,161GiB;
suffix49,887с, 1/426 checks, covers1/1, RSS0,785GiB; других отказов в controls нет.
Сообщения — placeholder Kani; ожидаемый класс подтверждён точными locations.

G1: measurement/jobs1/controls:true; baseline expect SUCCESS согласно lane.
Manual gate: три группы SUCCESS≤600с со всеми covers, два контроля FAILED на нужных locations.
G1 summary COMPLETE; Cloud Build FAILURE, aggregate gate false: baseline TIMEOUT
и placeholder вместо expect_check текста у controls. Manual gate PASS по строкам и locations.
Группы unreachable36 каждая; controls40/36. Все шесть names/request SHA совпали; check-tooling относительно GO SHA PASS.
Sample sum RSS3,593GiB, simultaneous CBMC2,833GiB, dmesg OOM none_seen.
G1 envelope 90min/$1,215; только при gate успехе G2 diagnostic/jobs3/controls:true:
три группы + ordinary `network_safety_unstable_u64_n0_to17`, envelope70min/$0,945.
Полный максимум двух envelope160min/$2,160≤$2,2; G1 actual+G2max=$1,431.
T0/окно и резерв закрытия30min записаны, перед G2 budget/остаток окна проверяются заново.
G2 UUID `99bf7d2a-e175-437d-9ad7-7e3d525cf8f3`, source `bb7458fe52`; library tree прежний.
Jobs3/перекрытие/OOM ожидаются; source/request/UUID ledger: start1/builds.json.

Статика Python PASS: точный partition, tail covers, shared checker, неизменность исходных items.
Заданный rustfmt --check exit0; изменённый .rs ≤100 колонок; git diff --check PASS.
Локальные rustc/cargo/Kani/CBMC не запускались; G1 имеет прежние manifest/unstable warnings.
Новые items полностью opt-in; ordinary source неизменен. Targeted unused/dead_code/warning codes/errors — no match.
Pin Kani9461e07a/toolchain/flags/lane-файлы прежние, CAP_USD73.96 не изменён.
Кандидаты для Part2 — три group-PFC, принятие зависит от G1/G2; Part1 пока не предлагается.
Домен exact `[u64;17]`/START1 не равен START0/scratch17/48; macOS UNKNOWN.
Пригодность замены устанавливает только CI организаторов; proof credit пока отсутствует.
