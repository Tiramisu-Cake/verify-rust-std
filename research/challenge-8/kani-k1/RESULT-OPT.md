# OPT — COMPLETE: split измерены; jobs=3 выявил OOM

База: `c52627e090e059ae8000af23fded3d614a89a2e3`.
Library SHA: `f052d6b7ec826e4f45f7bc1522dde38d5ba16a91`; только +91 строка в конце merge.rs.
G1 source: `73fb790ad0d78e81c5a2928651650398dbe7d673`, coordinator review GO.
G1 build: `993fe78c-4a34-489d-8c4e-485da048e1e2`, measurement N6, SUCCESS, $0.2970.
G2 source: `c81c10e3061e07bb83c732d81413632ada757d2c`.
G2 build: `0e44427c-18bd-4de4-95b2-e8730abec632`, measurement N8, SUCCESS, $0.3645.
G3 source: `ae5aabe3f3e4422a35f861b889ac7436acab4216`.
G3 build: `64a9829e-1097-4bcf-af34-6e3be5cfdd19`, diagnostic jobs=3, FAILURE, $0.2565.
Всего 3/3 builds, spent $0.9180/$4, reserved $0; CAP_USD=73.96 не менялся.
Request_id и envelopes: [opt/builds.json](opt/builds.json); costs: [audit](opt/budget-final.txt).
Measurement jobs=1; timeout 600 с везде; envelopes G1/G2/G3 70/70/110 минут плюс reserve.

Имена имеют префикс `slice::sort::shared::smallsort::verify::merge::opt_split::`.
B — реальный caller без stubs; A — proof_for_contract(bidirectional_merge).
G: MaybeUninit<[u64;48]> (general), S: [MaybeUninit<u64>;48] (stable).
VT — GCB Verification Time; RSS — наблюдаемый CBMC VmHWM, GiB; G1/G2:

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

G3 diagnostic: COMPLETE summary, gate false, Kani exit 1; OOM = OUT_OF_MEMORY.
Времена G3 относятся к общей конкурентной нагрузке; OOM не даёт completed VT/covers.

| Гармоника | N | Маршрут/backing | Статус | VT GCB, с | RSS GiB | Covers |
|---|---|---|---|---|---|---|
| general_direct_u64_n6 | 6 | B/G | SUCCESS | 55.88246 | 0.830 | 1/1 |
| stable_direct_u64_n6 | 6 | B/S | SUCCESS | 129.83510 | 5.357 | 1/1 |
| general_contract_u64_n6 | 6 | A/G | SUCCESS | 206.39864 | 1.412 | 1/1 |
| stable_contract_u64_n6 | 6 | A/S | SUCCESS | 255.93724 | 6.038 | 1/1 |
| general_direct_u64_n8 | 8 | B/G | SUCCESS | 244.31534 | 1.509 | 1/1 |
| stable_direct_u64_n8 | 8 | B/S | OOM | — | 7.738 | — |
| general_contract_u64_n8 | 8 | A/G | SUCCESS | 362.54013 | 1.860 | 1/1 |
| stable_contract_u64_n8 | 8 | A/S | OOM | — | 7.855 | — |

Baseline из RESULT-DIRECT.md: исторические source-reported G+S measurements.
B N6: 235.455 с / 6.034 GiB; A N6: 310.391 с / 6.583 GiB; оба SUCCESS.
B N8: TIMEOUT / 9.016 GiB; A N8: SUCCESS 417.825 с / 8.813 GiB.
N6 B GO: обе SUCCESS, covers SATISFIED, max 5.358 GiB (-11.2% к baseline).
N6 A GO: обе SUCCESS, covers SATISFIED, max 6.053 GiB (-8.0% к baseline).
Сумма VT N6: B 232.46656 с vs 235.455; A 471.65178 с vs 310.391 (+52.0%).
Сумма VT N8: B 501.96952 с (baseline TIMEOUT); A 571.08085 с vs 417.825 (+36.7%).
N8 max B 7.932 GiB, A 8.029 GiB; B N8 теперь имеет прямое bounded доказательство.
Все 8 measurement covers SATISFIED. Стоимость по группам внутри build не разносилась.
Matched rerun отсутствует; причинный speedup не заявлен.

Метод: kernel VmHWM по /proc, sampling каждые 2 с; concurrent sum — текущий VmRSS.
G1: max CBMC 6.053, driver 0.428; sampled sum всех RSS 6.037, CBMC 6.012 GiB.
G2: max CBMC 8.029, driver 0.753; sampled sum всех RSS 8.390, CBMC 7.989 GiB.
G3: max observed CBMC 7.855, driver 1.449 GiB; time -v max child 8298596 KiB = 7.914 GiB.
G3 time -v превышает sampled peak; атрибуция этого точного пика гармонике UNKNOWN.
G3 sum всех RSS 15687304 KiB = 14.961 GiB; CBMC 14367380 KiB = 13.702 при t=588 с.
Реально перекрылись 3 CBMC: PID 9432/9497/9470 при t=588 с; /proc интервалы в audit.
Kernel global OOM-killer подтверждён; оба stable N8 — OOM, остальные 6 SUCCESS, covers 1/1.
Сумма RSS не равна точной физической RAM. Linux 16 GiB, swap off; G1/G2 OOM none_seen.
macOS UNKNOWN; пригодность устанавливает только CI организаторов; safe-gate не назначен.

Приоритетные ordinary-кандидаты: четыре general, пики 0.830..1.860 GiB, G3 SUCCESS.
Stable N6 — условные кандидаты: пики 5.358/6.053 GiB, G3 SUCCESS; нагрузка остаётся высокой.
Stable N8 пока не рекомендованы в ordinary: G3 OOM при jobs=3, индивидуально 7.932/8.029 GiB.
Координатор решает о переносе; весь блок остался opt-in. При замене нужны оба маршрута:
general отдельно не покрывает полный домен прежней G+S-гармоники.

Объединение split по коду = прежние ветви/аллокации/значения: [review](opt/REVIEW.md).
В каждой один cover; any значения/probe, lt_u64, unwind(34), oracle и контракт сохранены.
A: один backing, src offset 0, prefix N initialized, tail uninit, отдельный any dst.
Requires/modifies/ensures не менялись; новых controls не нужно. N7 был опционален и не запускался.
B1 bounded Kani evidence для u64 N6/N8; B2/full proof generic T не заявлен.

G1/G2/G3 check-tooling PASS: source/request/Kani pin/pool и lane hashes; snapshots в opt/.
Точные данные: [N6](opt/n6.results.json), [N8](opt/n8.results.json),
[G3 diagnostic](opt/diagnostic.results.json).
Чтение через штатный k1g.sh summary/peaks/check-tooling; выводы логов ограничены <=200 строк.
Rustfmt --check edition 2024/config exit 0; source/report строки <=100, report <=100 строк.
Kani pin 9461e07a, nightly-2026-10-12, lane-файлы прежние; local Rust/Kani/CBMC не запускались.
Flags: --no-assert-contracts, --object-bits 12, uninit checks off; stubs не добавлены.
Все три build ожидались через watch с завершением хода; новых builds не будет.
Следующее — только письменно: [typed u64 probe / локальная merge-декомпозиция](opt/NEXT.md).
В OPT oracle/контракт не менялись; подбор нового oracle и его controls — отдельная задача.
