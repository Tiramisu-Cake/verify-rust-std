# UNSTABLE8 — PARTIAL, последняя сборка ожидается

Дата: 2026-10-30. G1/G2 завершены; G3 запущен с исправленными covers Cell N8 и DropKey N9.
База: `6bbf03c764a5abafc2d4d5eeeb5f2972d6beaf46`.
Library G1: `14f60a96372172c8699b050b64f878c2b0739dd2`.
Library G2: `956a758288f483bef38d27372e08877bfbfd2212`.
Library G3: `78c040559f448ea3cf05ec152ab1143014068570`.
G1 source: `5ff343a759b87c3927f7f3f90981d15f30e9e946`.
G2 source: `2d2cdfff1fc564b9f7e3e4ab5e6a4d1f74e808cb`.
G1: `64a70b50-30b2-4d26-b25b-7ed1463b4851`, $0.3105.
G2: `93263f1d-d590-454b-a496-a3c2f479b07f`, $0.2700.
Свой ledger: 3/3 сборок, spent $0.5805, reserved $0.8100 из $4; cap $73.96 прежний.
G3: `2fbe4ddc-a6c0-4cd9-8056-12c7c828b7f8`, результат ожидается.
G3 source: `b177a4bd5d46ae30edf1d75379ff7c43a7f19720`.
Measurement, k1-standard4, jobs=1, controls:true, swap off, timeout 600 с на гармонику.
G1/G2: summary COMPLETE, GCB FAILURE; setup корректный, различные причины отказа gate.
G1 gate false из-за Cell TIMEOUT; G2 — covers 4/5 при SUCCESS assertions обоих маршрутов.

| Build | Тип | N | Маршрут | Статус | VT GCB, с | RSS KiB | Covers |
|---|---|---|---|---|---|---|---|
| G1 | DropKey | 8 | stable + unstable general | SUCCESS | 194.44167 | 487016 | 5/5 |
| G1 | Cell | 8 | stable + unstable fallback | TIMEOUT | — | 315944 | — |
| G2 | Cell | 8 | stable insertion, fixed | SUCCESS | 330.23926 | 195112 | 4/5 |
| G2 | Cell | 8 | unstable fallback, fixed | SUCCESS | 237.26244 | 193556 | 4/5 |
| G3 | Cell | 8 | stable + unstable fixed, 2 proofs | PENDING | — | — | — |
| G3 | DropKey | 9 | stable + unstable general | PENDING | — | — | — |

RSS — индивидуальный CBMC VmHWM; /proc опрашивается каждые 2 с, не сумма RAM.
Пики отдельного driver-процесса: G1 840616 KiB, G2 460812 KiB; без per-harness attribution.
Пики могут пропустить рост между samples; time -v max G1/G2 1782584/1653588 KiB за run.
CBMC peaks привязаны к гармоникам через metadata; OOM scan none_seen в обоих builds.
Числовой safe-gate не назначается.

Оба существующих отрицательных контроля G1: корректный setup, один ожидаемый отказ.
Drop N2: FAILED 1/390, 1.9809694 с; counts, types.rs:58.
Cell N2: FAILED 1/227, 0.561533 с; sortedness, types.rs:56.
Expressions совпали с expect_check; covers 0/1 после намеренного отказа у обоих.
Oracle, домены, cadical, unwind(50), flags, Kani 9461e07a и toolchain не менялись.
check-tooling G1/G2: lane-файлы и шесть summary bindings равны базе.

Доказано для DropKey N8: logical sortedness и мультимножество полных u8-значений.
Настоящие stable/unstable trait-входы, scratch48 и bidirectional_merge, без stubs.
Полный any [u8;8], any probe и stable: bool; covers обеих ветвей, unsorted и duplicate.
Cell comparator read-only; combined TIMEOUT не даёт credit, G2 даёт assertion SUCCESS.
G2 const true/false сохраняют input/probe/oracle; объединение равно исходному bool-домену.
Из кода следует: пятый cover — противоположная const-ветвь, всегда недостижимая.
G3 переносит route cover в macro: остаётся только выбранный literal, остальные covers прежние.
Это исправленный Cell N8; неизменённый принятый DropKey N8 повторно не запускается.
G3 также проверяет отдельный DropKey N9 через fixed_trait_case и исходный trait_properties.

Кандидат в ordinary Part 1: DropKey N8; Cell N8 ожидает исправленного measurement gate.
Все добавления opt-in, ordinary набор не менялся; переводит координатор.
N0..2 + N8/N9 не образуют непрерывный диапазон. macOS UNKNOWN.
Пригодность устанавливает только CI организаторов; GCB pilot не равен их CI PASS.
Вне цели: drop-счёт, unwind, generic T, стабильность по identity; uninit checks off.
G3 envelope 3 × 10 + 30 = 60 минут / $0.8100; свой spent+envelope $1.3905 из $4.
Rustfmt --check и diff-check exit 0; исходники и этот отчёт ≤100 символов/строку.
[Запросы, bounded summary, peaks и UUID](unstable8/).
