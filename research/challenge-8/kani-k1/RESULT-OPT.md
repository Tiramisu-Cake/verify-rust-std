# OPT — PARTIAL: N6 B/A GO; N8 подготовлен

База: `c52627e090e059ae8000af23fded3d614a89a2e3`.
Library SHA: `f052d6b7ec826e4f45f7bc1522dde38d5ba16a91`; только новый opt-in блок.
G1 source: `73fb790ad0d78e81c5a2928651650398dbe7d673`, coordinator review GO.
G1 build: `993fe78c-4a34-489d-8c4e-485da048e1e2`, COMPLETE, gate true.
G1 request: `opt-split-n6-gate-20261030`; cost $0.2970, jobs=1, timeout 600 с.
Собственных builds 1/3; spent $0.2970/$4, reserved $0; CAP_USD=73.96 неизменён.
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
| general_direct_u64_n8 | 8 | B/G | NOT_RUN | — | — | — |
| stable_direct_u64_n8 | 8 | B/S | NOT_RUN | — | — | — |
| general_contract_u64_n8 | 8 | A/G | NOT_RUN | — | — | — |
| stable_contract_u64_n8 | 8 | A/S | NOT_RUN | — | — | — |

Baseline из RESULT-DIRECT.md: исторические source-reported measurements, оба маршрута вместе.
B N6 SUCCESS 235.455 с / 6.034 GiB; A N6 SUCCESS 310.391 с / 6.583 GiB.
B N8 TIMEOUT / 9.016 GiB; A N8 SUCCESS 417.825 с / 8.813 GiB.
N6 B GO: обе SUCCESS, covers SATISFIED; max 5.358 GiB, ниже baseline на 11.2%.
N6 A GO: обе SUCCESS, covers SATISFIED; max 6.053 GiB, ниже baseline на 8.0%.
Сумма VT: B 232.46656 с (baseline 235.455); A 471.65178 с (baseline 310.391).
У A сумма VT выросла на 52.0%; стоимость всего G1 $0.2970, по группам не разнесена.
Matched rerun отсутствует; причинный speedup не заявлен.

Метод: kernel VmHWM процессов CBMC/driver, /proc sampling каждые 2 с.
N6 max CBMC 6.053 GiB; max driver 448564 KiB = 0.428 GiB.
Одновременный sampled sum всех RSS: 6329892 KiB = 6.037 GiB при t=307 с.
Одновременный sampled CBMC RSS: 6304036 KiB = 6.012 GiB; jobs=1, solver не перекрывались.
Это сумма процессной резидентной памяти, не точная физическая RAM.
16-GiB Linux, swap off, OOM none_seen; concurrency diagnostic ещё не выполнялся.
macOS UNKNOWN; пригодность устанавливает только CI организаторов; safe-gate не назначен.

Все 4 N6 split — кандидаты в ordinary по снижению индивидуального пика при прежнем домене;
координатор решает о переносе; весь новый блок остаётся opt-in. N8 пока не кандидат.
В каждой гармонике один cover. Arbitrary значения/probe, lt_u64, unwind(34) сохранены.
A: только один backing, offset 0, prefix N initialized, tail uninit, отдельный any dst.
Requires/modifies/ensures и oracle не менялись; новые контроли не нужны.
Объединение split = прежние ветви/аллокации/значения: [opt/REVIEW.md](opt/REVIEW.md).

G1 summary/peaks/check-tooling подтверждают source/request/Kani pin и lane hashes.
Evidence: [summary](opt/n6.summary.md), [peaks](opt/n6.peaks.txt), [tooling](opt/n6.tooling.txt).
Компактные точные данные и group gate: [opt/n6.results.json](opt/n6.results.json).
Evidence Brief HTTP 404 больше не блокирует: координатор уточнил штатный путь K-1,
разрешил summary/peaks/check-tooling с fetch; это не административный аудит.

Rustfmt --check edition 2024/config exit 0; source/report строки <=100, report <=100 строк.
Kani pin 9461e07a, nightly-2026-10-12, lane-файлы прежние; local Rust/Kani/CBMC не запускались.
Flags: --no-assert-contracts, --object-bits 12, uninit checks off; proof на GCB.
Это bounded Kani evidence для u64 N6; универсальный full proof generic T не заявлен.
Следующий шаг: N8 для обеих принятых групп; четыре entries, полный envelope 70 мин/$0.9450.
С N8 резервом собственные spent+reserved будут $1.2420/$4, builds 2/3.
После N8 concurrency jobs=3 — только при оставшихся полном envelope, окне и бюджете.
Typed u64 probe / oracle-специализация либо локальная merge-декомпозиция —
только письменные следующие варианты; в этой сессии oracle не менялся.
