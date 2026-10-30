# UNSTABLE8 — PARTIAL, после gate

Дата: 2026-10-30. Gate G1 завершён; Cell N8 split G2 запущен.
База: `6bbf03c764a5abafc2d4d5eeeb5f2972d6beaf46`.
Library G1: `14f60a96372172c8699b050b64f878c2b0739dd2`.
Library split: `956a758288f483bef38d27372e08877bfbfd2212`.
G1 source: `5ff343a759b87c3927f7f3f90981d15f30e9e946`.
G1 build: `64a70b50-30b2-4d26-b25b-7ed1463b4851`, стоимость $0.3105.
Свой ledger: 2/3 сборок, spent $0.3105, reserved $0.6750 из $4; cap $73.96 прежний.
G2 build `93263f1d-d590-454b-a496-a3c2f479b07f`, результат ожидается.
G2 source `2d2cdfff1fc564b9f7e3e4ab5e6a4d1f74e808cb`.
G1 GCB FAILURE: gate false из-за Cell TIMEOUT; summary COMPLETE, setup корректный.
Measurement, k1-standard4, jobs=1, controls:true, swap off, timeout 600 с на гармонику.

| Тип | N | Маршрут | Статус | VT GCB, с | RSS KiB | Covers |
|---|---|---|---|---|---|---|
| DropKey | 8 | stable + unstable general | SUCCESS | 194.44167 | 487016 | 5/5 |
| Cell<u8> | 8 | stable insertion + unstable fallback | TIMEOUT | — | 315944 | — |
| Cell<u8> | 8 | stable insertion, fixed | PENDING | — | — | — |
| Cell<u8> | 8 | unstable fallback, fixed | PENDING | — | — | — |

RSS — индивидуальный CBMC VmHWM; /proc опрашивается каждые 2 с, не сумма RAM.
G1 driver peak 840616 KiB, общий для запуска, без attribution к отдельной гармонике.
Пики могут пропустить рост между samples; time -v max 1782584 KiB относится ко всему run.
Процессный CBMC peak надёжно привязан через metadata к соответствующей гармонике.
Числовой safe-gate не назначается. OOM scan: none_seen; Cell достиг лимита времени.

Оба существующих отрицательных контроля с корректным setup и одним ожидаемым отказом:
Drop N2: FAILED 1/390, 1.9809694 с; counts, types.rs:58.
Cell N2: FAILED 1/227, 0.561533 с; sortedness, types.rs:56.
Ожидаемые expressions совпали с expect_check; covers 0/1 у обоих после намеренного отказа.
Oracle, домены, cadical, unwind(50), flags, Kani 9461e07a и toolchain не менялись.
check-tooling G1 подтвердил lane-файлы и шесть summary bindings относительно базы.

Доказано для DropKey N8: logical sortedness и мультимножество полных u8-значений.
Настоящие stable/unstable trait-входы, scratch48 и bidirectional_merge, без stubs.
Полный any [u8;8], any probe и stable: bool; covers обеих ветвей, unsorted и duplicate.
Cell comparator read-only. Combined Cell N8 TIMEOUT не даёт proof credit.
Split сохраняет any input/probe, тот же check_output и covers unsorted/duplicate.
STABLE — const true/false, скрытого any-selector нет; объединение = исходный bool-домен.
DropKey N8 не повторяется; ordinary набор не менялся, новые гармоники/helper opt-in.

Кандидат в ordinary Part 1: DropKey N8; переводит координатор после оценки CI.
N0..2 + N8/N9 не образуют непрерывный диапазон. macOS UNKNOWN.
Пригодность устанавливает только CI организаторов; Linux GCB pilot не равен их PASS.
Вне цели: drop-счёт, unwind, generic T, стабильность по identity; uninit checks off.
Продолжение: split Cell N8 (50 минут, резерв $0.6750), затем при остатке отдельный N9.
Rustfmt --check и diff-check exit 0; исходники и этот отчёт ≤100 символов/строку.
[Запросы, bounded summary, peaks и UUID](unstable8/).
