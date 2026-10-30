# OPT — PARTIAL: N6/N8 доказаны; jobs=3 diagnostic отправлен

База: `c52627e090e059ae8000af23fded3d614a89a2e3`.
Library SHA: `f052d6b7ec826e4f45f7bc1522dde38d5ba16a91`; только новый opt-in блок.
G1 source: `73fb790ad0d78e81c5a2928651650398dbe7d673`, coordinator review GO.
G1 build: `993fe78c-4a34-489d-8c4e-485da048e1e2`, COMPLETE, gate true.
G1 request: `opt-split-n6-gate-20261030`; cost $0.2970, jobs=1, timeout 600 с.
G2 build: `0e44427c-18bd-4de4-95b2-e8730abec632`; N8 COMPLETE, gate true.
G2 source: `c81c10e3061e07bb83c732d81413632ada757d2c`, request opt-split-n8-20261030.
G1 cost $0.2970, G2 $0.3645; own spent $0.6615, reserved $1.4850; total $2.1465/$4.
G3 build: `64a9829e-1097-4bcf-af34-6e3be5cfdd19`, diagnostic SUBMITTED, jobs=3.
G3 source: `ae5aabe3f3e4422a35f861b889ac7436acab4216`, request opt-split-jobs3-20261030.
Отправлено 3/3; новых builds не будет; G3 полный envelope 110 минут, timeout 600 с.
CAP_USD=73.96 неизменён; G2 envelope 70 минут, jobs=1, timeout 600 с.
Список UUID/request_id/source/cost: [opt/builds.json](opt/builds.json).

Все имена имеют префикс `slice::sort::shared::smallsort::verify::merge::opt_split::`.
G = general: MaybeUninit<[u64;48]>; S = stable: [MaybeUninit<u64>;48].
B — реальный caller без stubs; A — proof_for_contract(bidirectional_merge).
RSS в таблице — индивидуальный CBMC VmHWM, GiB; VT — GCB Verification Time.

| Гармоника | N | Маршрут/backing | Статус | VT GCB, с | RSS GiB | Covers |
|---|---|---|---|---|---|---|
| general_direct_u64_n6 | 6 | B/G | SUCCESS | 70.84420 | 0.830 | 1/1 |
| stable_direct_u64_n6 | 6 | B/S | SUCCESS | 161.62236 | 5.358 | 1/1 |
| general_contract_u64_n6 | 6 | A/G | SUCCESS | 171.72945 | 1.410 | 1/1 |
| stable_contract_u64_n6 | 6 | A/S | SUCCESS | 299.92233 | 6.053 | 1/1 |
| general_direct_u64_n8 | 8 | B/G | SUCCESS | 203.04560 | 1.510 | 1/1 |
| stable_direct_u64_n8 | 8 | B/S | SUCCESS | 298.92392 | 7.932 | 1/1 |
| general_contract_u64_n8 | 8 | A/G | SUCCESS | 221.69978 | 1.860 | 1/1 |
| stable_contract_u64_n8 | 8 | A/S | SUCCESS | 349.38107 | 8.029 | 1/1 |

Baseline из RESULT-DIRECT.md: исторические source-reported measurements, оба маршрута вместе.
B N6 SUCCESS 235.455 с / 6.034 GiB; A N6 SUCCESS 310.391 с / 6.583 GiB.
B N8 TIMEOUT / 9.016 GiB; A N8 SUCCESS 417.825 с / 8.813 GiB.
N6 B GO: обе SUCCESS, covers SATISFIED; max 5.358 GiB, ниже baseline на 11.2%.
N6 A GO: обе SUCCESS, covers SATISFIED; max 6.053 GiB, ниже baseline на 8.0%.
Сумма VT: B 232.46656 с (baseline 235.455); A 471.65178 с (baseline 310.391).
У N6 A сумма VT выросла на 52.0%; стоимость G1/G2 по группам не разнесена.
N8 B: сумма VT 501.96952 с, max 7.932 GiB; baseline TIMEOUT (не completed VT).
N8 A: сумма VT 571.08085 с vs 417.825; max 8.029 GiB vs 8.813.
Обе ветви N8 SUCCESS, covers SATISFIED; B N8 теперь имеет прямое bounded доказательство.
Matched rerun отсутствует; причинный speedup не заявлен.

Метод: kernel VmHWM процессов CBMC/driver, /proc sampling каждые 2 с.
N6 max CBMC 6.053 GiB; max driver 448564 KiB = 0.428 GiB.
Одновременный sampled sum всех RSS: 6329892 KiB = 6.037 GiB при t=307 с.
Одновременный sampled CBMC RSS: 6304036 KiB = 6.012 GiB; jobs=1, solver не перекрывались.
Это сумма процессной резидентной памяти, не точная физическая RAM.
N8 max driver 789072 KiB = 0.753 GiB; sampled sum всех RSS 8797856 KiB = 8.390 GiB.
N8 simultaneous CBMC RSS 8376572 KiB = 7.989 GiB; jobs=1, solver не перекрывались.
G1/G2: 16-GiB Linux, swap off, OOM none_seen; concurrency G3 SUBMITTED.
macOS UNKNOWN; пригодность устанавливает только CI организаторов; safe-gate не назначен.

Все 8 split — кандидаты для рассмотрения ordinary: прежний домен, SUCCESS/covers, ниже пики.
General пики 0.830..1.860 GiB, stable 5.358..8.029 GiB; риски stable остаются.
Координатор решает о переносе; весь блок остаётся opt-in, macOS UNKNOWN.
В каждой гармонике один cover. Arbitrary значения/probe, lt_u64, unwind(34) сохранены.
A: только один backing, offset 0, prefix N initialized, tail uninit, отдельный any dst.
Requires/modifies/ensures и oracle не менялись; новые контроли не нужны.
Объединение split = прежние ветви/аллокации/значения: [opt/REVIEW.md](opt/REVIEW.md).

G1/G2 summary/peaks/check-tooling подтверждают source/request/Kani pin и lane hashes.
Evidence: [summary](opt/n6.summary.md), [peaks](opt/n6.peaks.txt), [tooling](opt/n6.tooling.txt).
Точные данные: [N6](opt/n6.results.json), [N8](opt/n8.results.json); output snapshots в opt/.
Evidence Brief HTTP 404 больше не блокирует: координатор уточнил штатный путь K-1,
разрешил summary/peaks/check-tooling с fetch; это не административный аудит.

Rustfmt --check edition 2024/config exit 0; source/report строки <=100, report <=100 строк.
Kani pin 9461e07a, nightly-2026-10-12, lane-файлы прежние; local Rust/Kani/CBMC не запускались.
Flags: --no-assert-contracts, --object-bits 12, uninit checks off; proof на GCB.
Это bounded Kani evidence для u64 N6/N8; универсальный full proof generic T не заявлен.
Следующий шаг: k1g.sh watch G3, завершить ход; затем evidence, фактическое overlap и итог.
С резервом собственные spent+reserved $2.1465/$4, builds 3/3; больше builds не будет.
Envelope + 15 мин closeout помещаются до консервативной границы 23:00 UTC.
Typed u64 probe / oracle-специализация либо локальная merge-декомпозиция —
только письменные следующие варианты; в этой сессии oracle не менялся.
