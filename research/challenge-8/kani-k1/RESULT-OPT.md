# OPT — PARTIAL: N6 build SUCCESS; Evidence Brief недоступен

База: `c52627e090e059ae8000af23fded3d614a89a2e3`.
Library SHA: `f052d6b7ec826e4f45f7bc1522dde38d5ba16a91`.
Добавлен только opt-in блок в конце merge.rs: 8 split-гармоник u64 N6/N8.
Build ID: `993fe78c-4a34-489d-8c4e-485da048e1e2`; отправлено 1/3.
Собственные spent $0.2970/$4, reserved $0; стоимость: k1g.sh budget BUILD_UUID.
Request ID: `opt-split-n6-gate-20261030`; source `73fb790ad0`, reviewed GO.
Полный envelope N6 был 70 минут / $0.9450; jobs=1, timeout 600 с.
Перед dispatch: общий used $56.5350, reserved $1.4850; cap $73.96 не менялся.
После submit общий upper bound $58.9650; envelope + резерв помещался в окно.
Учёт собственных UUID/request_id: [opt/builds.json](opt/builds.json).

Имена ниже имеют префикс `slice::sort::shared::smallsort::verify::merge::opt_split::`.
VT — GCB Verification Time; RSS — индивидуальный пик процесса; evidence недоступен.

| Гармоника | N | Маршрут/backing | Статус | VT GCB, с | RSS GiB | Covers |
|---|---|---|---|---|---|---|
| general_direct_u64_n6 | 6 | B/general | UNKNOWN | — | — | — |
| stable_direct_u64_n6 | 6 | B/stable | UNKNOWN | — | — | — |
| general_contract_u64_n6 | 6 | A/general | UNKNOWN | — | — | — |
| stable_contract_u64_n6 | 6 | A/stable | UNKNOWN | — | — | — |
| general_direct_u64_n8 | 8 | B/general | NOT_RUN | — | — | — |
| stable_direct_u64_n8 | 8 | B/stable | NOT_RUN | — | — | — |
| general_contract_u64_n8 | 8 | A/general | NOT_RUN | — | — | — |
| stable_contract_u64_n8 | 8 | A/stable | NOT_RUN | — | — | — |

General backing: MaybeUninit<[u64;48]>; stable backing: [MaybeUninit<u64>;48].
Каждый A создаёт только одну такую аллокацию; src offset 0, префикс N initialized,
хвост uninit; отдельный initialized any dst. Requires/modifies/ensures не менялись.
Каждый B вызывает только свой реальный маршрут, без symbolic stable и без stubs.
Any значения, один arbitrary full-value probe, lt_u64, unwind(34), oracle сохранены.
Обоснование объединения доменов, covers и план gate: [opt/REVIEW.md](opt/REVIEW.md).

Baseline из RESULT-DIRECT.md; это исторические source-reported measurements:
B N6 SUCCESS 235.455 с / 6.034 GiB; A N6 SUCCESS 310.391 с / 6.583 GiB.
B N8 TIMEOUT / 9.016 GiB; A N8 SUCCESS 417.825 с / 8.813 GiB.
Baseline RSS — CBMC VmHWM, процессный пик, не суммарная физическая RAM.
Новые VT/RSS/covers недоступны; actual cost $0.2970; сумма VT неизвестна.
Без matched rerun причинный speedup не устанавливается.

Gate оценивает B и A отдельно: обе ветви SUCCESS, cover каждой SATISFIED,
измеримый спад индивидуального RSS относительно baseline. Сейчас GO ни у одной.
Кандидаты в ordinary пока НЕ определены; opt-in сохранён для всех 8 гармоник.
Индивидуальные пики CBMC/driver, их атрибуция и метод измерения: UNKNOWN.
Одновременный пик: не измерен; jobs=3 diagnostic не запускался.
Сумму RSS не трактовать как точную RAM; числовой safe-gate не назначать.
macOS UNKNOWN; пригодность устанавливает только CI организаторов.

Статическая проверка: rustfmt --check edition 2024 exit 0; строки <=100.
Python validation запроса: 4 гармоники accepted; исходный merge.rs — точный префикс.
Toolchain nightly-2026-10-12, Kani pin 9461e07a и lane-файлы не менялись.
Flags прежние: --no-assert-contracts, --object-bits 12, uninit checks off.
Локальные rustc/cargo/Kani/CBMC не запускались; proof evidence пока НЕ получен.
Контракт/oracle не менялись, новых negative controls не добавлено.

Brief exit 1: Reader report or query route is unavailable (HTTP 404).
SUCCESS от watcher — статус сборки; статусы гармоник и covers из него не следуют.
Точный отказ: [opt/n6-brief-unavailable.json](opt/n6-brief-unavailable.json).
Запрос административного аудита направлен пользователю.
check-tooling подтвердил source/pool и равенство lane-файлов базе, затем начал fetch.
Fetch остановлен SIGTERM; частичная загрузка возможна. Fetched evidence не читался.
Summary tooling binding не проверен; статусы/VT/RSS/covers остаются UNKNOWN.
Следующий шаг: разрешённый аудит/evidence; N8 не запускался, gate GO не установлен.
Typed probe / эквивалентная oracle-специализация и локальная merge-декомпозиция —
только письменные предложения, не реализованы в этой сессии.
