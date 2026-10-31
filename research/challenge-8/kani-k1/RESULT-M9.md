# M9 — PARTIAL: прямые N9 успешны, non-const S9 TIMEOUT

Дата: 2026-10-31. Ветка `experiment/kani-k1-mnine-20261031`.
Library commit `b2930031d889065e89054efea16f9a10a409b048`;
library tree G1=G2 `3c5fd2134ca7ed558976b53e1216eeedd0d6b491`.
G1 source/GO `578350ad3ae7d7479b7a1abcfc98647db1089eb5`;
G2 source `fe4fa2cc4f3213bb3043c9c8d172b169864f6fb8`.
Kani pin `9461e07af7ec929f050aa4192f29363c9be07779`, flags/toolchain/lane прежние.

| Run / request_id | Build UUID | Cloud / summary / gate | USD |
|---|---|---|---:|
| G1 / m9-g1-measurement-20261031 | 06ddd32a-8b17-4b20-b3cf-3ee506400980 | FAILURE / COMPLETE / false | 0.5670 |
| G2 / m9-g2-diagnostic-jobs3-20261031 | ed6b14d6-1cfc-4af7-81ce-6d17fd8a2e1a | SUCCESS / COMPLETE / true | 0.2295 |

Всего **$0.7965 ≤ $2.30**, builds2/2, reserved$0; учёт только своих UUID.
Только k1-standard4 (Linux4CPU/16GiB, фактически15.63GiB, swap off).
Timeout600, controls:true, uninit checks off в обоих; G1 jobs1, G2 jobs3.
Все имена ниже — `slice::sort::shared::smallsort::verify::merge::`.
RSS — per-process CBMC VmHWM из sampler2s с direct metadata attribution, GiB.
Checks — failed/total; «—» означает, что итог не сообщён после TIMEOUT.

| Run / гармоника | Scratch | Статус | VT, с | CBMC RSS | Covers | Checks |
|---|---|---|---:|---:|---|---|
| G1 general_direct_u64_n9 | internal general | SUCCESS | 423.59130 | 1.602 | 1/1 | 0/407 |
| G1 stable_direct_u64_n9 | aggregate48 | SUCCESS | 434.47890 | 1.599 | 1/1 | 0/407 |
| G1 stable_direct_nonconst_u64_n9 | array48 non-const | TIMEOUT600 | — | 8.027 | — | — |
| G1 stable_direct_const_u64_n9 | array48 const | SUCCESS | 429.67825 | 0.821 | 1/1 | 0/405 |
| G1 stable_direct_const_u64_n8 | array48 const | SUCCESS | 143.88579 | 0.736 | 1/1 | 0/405 |
| G2 general_direct_u64_n9 | internal general | SUCCESS | 547.00305 | 1.597 | 1/1 | 0/407 |
| G2 stable_direct_const_u64_n9 | array48 const | SUCCESS | 555.31870 | 0.824 | 1/1 | 0/405 |
| G2 general_direct_u64_n8 | internal general | SUCCESS | 212.59853 | 1.509 | 1/1 | 0/407 |
| G2 stable_direct_u64_n8 | aggregate48 | SUCCESS | 197.86061 | 1.511 | 1/1 | 0/407 |

**N9:** matched G1 показывает низкий RSS и у const array, и у aggregate;
aggregate-представление не обязательно для наблюдаемого снижения RSS.
Const использует примерно половину RSS aggregate, VT близки; non-const TIMEOUT.
Полной успешной триады N9 нет; точный механизм и причинность внутри Kani/CBMC
не установлены. Сравнение checks405/407 сохранено, oracle не менялся.

**N8:** const SUCCESS — самостоятельный результат, независимо от TIMEOUT S9.
Историческая matched пара BACKING: source `740d22674c`, build
`b07fdcd8-fbd8-401e-9948-9e5f9e7201ad`: non-const292.468s/7.928GiB,
aggregate214.316s/1.508GiB. Const G1 143.88579s/0.736GiB — новый SHA;
это **не matched триада N8**, причинный вывод из трёх измерений не заявлен.
Одноимённую OPT G2 source `c81c10e306` с BACKING не смешивали.

G2 разрешён по строкам G1: G9 и S9 aggregate/const SUCCESS с covers;
общий false gate из-за non-const не блокировал G2. Выбрана S9 const по RSS/VT.
Реальное перекрытие jobs3 подтверждено: PID9280(G9),9285(S9const),9290(G8)
впервые наблюдаются в одной выборке70s; общая область наблюдений70..279s.
Далее PID9317(S8aggregate) перекрывает G9/S9const в285..480s.
Это sampled process-presence, точность2s; не только запрошенное --jobs=3.
Одновременный CBMC RSS max3.559GiB; sampled общий RSS max4.014GiB.
G2 driver VmHWM1.938GiB; time-v single-process max1.944GiB выше sampled peak,
он сохранён как истинный максимум отдельного процесса без приписывания CBMC.
G1 driver0.864GiB, sampled общий RSS8.619GiB. OOM none_seen в обоих.
Missing results0, memory attribution9/9 direct; G2 времена при совместной нагрузке,
не single-harness measurements и не сравнение скорости с G1.

Кандидаты в ordinary: **general_direct_u64_n9 + stable_direct_const_u64_n9**;
S9 aggregate также положительный jobs1-кандидат, его jobs3 N9 не измерялся.
Условие обеих прямых ветвей выполнено: предлагается заменить conditional
`general_stable_sorted_permutation_u64_n9` парой G9/S9const после CI организаторов.
Самостоятельно ordinary/Part2 не менялись; все пять новых entries остаются opt-in.
S8 const — отдельный кандидат оптимизации fixture; general N9 backing не менялся.

Source audit PASS: прежние items точны кроме guard6..=9; два новых private
helper-а отличаются от stable aggregate только именем/allocation/borrow.
Adapter/oracle/probe/lt_u64 равны ASSEMBLY `d4e5a0907b`; arbitrary input/probe,
snapshot, unwind34, real merge, один cover после assert сохранены; controls новые не нужны.
Это source audit, не measurement controls итогового SHA; full backing не доказан.
`check-tooling` G1/G2 PASS относительно `97fdf0a21e`; request SHA/source/UUID,
точные множества requested names5/5 и4/4, metadata pin и library trees сверены.
Rustfmt заданным wrapper/config --check exit0, Rust-строки≤100; diff-check PASS.
В controls builds targeted warnings unused/dead_code/merge.rs/error/unsupported нет;
видны прежние manifest/unstable-feature warnings. Ordinary cfg: source audit delta0,
отдельной компиляции без controls нет; новых импортов/обычных symbols нет.
Локально rustc/cargo/Kani/CBMC не запускались; tool/service код не менялся.

T0 07:37:33UTC, deadline11:37:33UTC, closing reserve30min; оба dispatch прошли
budget/full-envelope checks, cap73.96 не менялся. Оба ожидались watch с концом хода.
Данные и привязки: `m9/g*.summary.md`, `g*.rows.tsv`, `g*.peaks.txt`, `g*.tooling.txt`,
`g*.request.json`, `g*.preflight.json`, `builds.json`, `costs.json`, `validation.json`.
**Оговорки:** fixture48 ≠ любой backing; macOS UNKNOWN; окончательная пригодность —
только CI организаторов. Полный CI/ordinary inventory нового SHA не выполнялись.
