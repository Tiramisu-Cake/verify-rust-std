# UNSTABLE8 — PARTIAL: N8 закрыт для обоих типов, дополнительный N9 TIMEOUT

Дата: 2026-10-30. Обязательная цель N8 достигнута; дополнительных сборок не будет.
База worktree: `6bbf03c764a5abafc2d4d5eeeb5f2972d6beaf46`.
Итоговый library SHA: `78c040559f448ea3cf05ec152ab1143014068570`.
Library совпадает с G3 source; последующие коммиты меняют только research/.
G1 source: `5ff343a759b87c3927f7f3f90981d15f30e9e946` (review и GO до первого dispatch).
G2 source: `2d2cdfff1fc564b9f7e3e4ab5e6a4d1f74e808cb`.
G3 source: `b177a4bd5d46ae30edf1d75379ff7c43a7f19720`.
G1: `64a70b50-30b2-4d26-b25b-7ed1463b4851`, $0.3105.
G2: `93263f1d-d590-454b-a496-a3c2f479b07f`, $0.2700.
G3: `2fbe4ddc-a6c0-4cd9-8056-12c7c828b7f8`, $0.3375.
Свои сборки 3/3; spent $0.9180/$4, reserved $0; UUID/request_id в builds.json.
Цена из k1g budget по этим UUID; минуты build округляются вверх, ставка $0.0135/мин.
Полные envelopes G1/G2/G3: 70/50/60 минут, резервы $0.9450/$0.6750/$0.8100.
Budget проверен перед каждым dispatch; envelopes помещались в остаток окна ≤4 ч.
CAP_USD $73.96 прежний; общий финальный ledger $58.5870 spent, $0.8100 reserved.
Все builds: measurement, k1-merge, k1-standard4, jobs=1, controls:true, swap off.
Timeout 600 с/гармонику; cadical, unwind(50), Kani 9461e07a, toolchain/flags прежние.

| Build | Тип | N | Маршрут | Статус | VT GCB, с | CBMC RSS KiB | Covers |
|---|---|---|---|---|---|---|---|
| G1 | DropKey | 8 | stable + unstable general | SUCCESS | 194.44167 | 487016 | 5/5 |
| G1 | Cell | 8 | stable + unstable fallback | TIMEOUT | — | 315944 | — |
| G2 | Cell | 8 | stable insertion, fixed | SUCCESS | 330.23926 | 195112 | 4/5 |
| G2 | Cell | 8 | unstable fallback, fixed | SUCCESS | 237.26244 | 193556 | 4/5 |
| G3 | Cell | 8 | stable insertion, fixed | SUCCESS | 222.42752 | 195108 | 4/4 |
| G3 | Cell | 8 | unstable fallback, fixed | SUCCESS | 206.487 | 193900 | 4/4 |
| G3 | DropKey | 9 | stable + unstable general | TIMEOUT | — | 527224 | — |

Все summary COMPLETE; все GCB FAILURE. G1 gate false из-за combined Cell TIMEOUT;
G2 — только из-за covers 4/5; G3 — только из-за дополнительного DropKey N9 TIMEOUT.
У G2 assertions обоих Cell-маршрутов успешны, но противоположный const cover недостижим.
G3 переносит cover в macro с выбранным literal: все четыре требуемых covers SATISFIED.
Именно G3 даёт принятые Cell N8 measurement-строки; общий gate G3 не объявляется зелёным.

RSS — индивидуальный CBMC VmHWM; polling /proc каждые 2 с, не сумма физической RAM.
Metadata даёт direct attribution CBMC PID → harness; значения в таблице — пики процессов.
Максимальный пик одного driver-процесса G1/G2/G3: 840616/460812/483104 KiB.
Driver peak относится к build, per-harness attribution для него не заявляется.
Sampling может пропустить рост между samples; time -v max за run: 1782584/1653588/1722424 KiB.
OOM scan во всех builds: none_seen; оба TIMEOUT достигли прежнего лимита 600 с, VT неизвестен.
Числовой safe-gate не назначается. check-tooling всех трёх builds подтвердил исходные lanes.

Контроли G1: корректный setup, по одному ожидаемому отказу, expressions = expect_check.
reject_logical_permutation_drop_n2: FAILED 1/390, 1.9809694 с; counts, types.rs:58.
reject_logical_sortedness_cell_n2: FAILED 1/227, 0.561533 с; sortedness, types.rs:56.
Covers 0/1 у обоих после намеренного отказа. Oracle не менялся; новых controls не требуется.

Доказано на N8 для DropKey и Cell<u8>: sortedness по логическому ключу и мультимножество
логических u8-значений, полный any [u8;8] и произвольный any probe, comparator read-only.
Настоящие stable/unstable trait-входы, без stubs; у DropKey настоящий bidirectional_merge:
stable → general-with-scratch48; unstable → Freeze-default → general с внутренним scratch48.
Cell: stable → insertion; unstable → fallback → insertion. Пороги 32/16 соблюдены.
DropKey N8 сохранил исходный symbolic stable и covers обеих ветвей, unsorted/duplicate.
Cell split: STABLE — const true/false, скрытого any-selector нет; input/probe/oracle прежние.
Объединение двух фиксированных маршрутов равно исходному bool-домену; в каждом covers
возврата после assert, выбранного trait-входа, unsorted input и duplicate keys SATISFIED.
Не доказаны drop-счёт, unwind, generic T, стабильность по identity; uninit checks off.
DropKey N9 не закрыт; Cell N9 не запускался. N0..2+N8/N9 не равны непрерывному диапазону.

Кандидаты ordinary Part 1: DropKey N8 combined и две Cell N8 fixed-route гармоники.
Все пять новых гармоник и helper/macro opt-in; ordinary не менялся, переводит координатор.
Combined Cell N8 и DropKey N9 пока не кандидаты. macOS UNKNOWN.
Пригодность устанавливает только CI организаторов; GCB pilot не равен их CI PASS.
Продолжение вне текущих 3/3: split DropKey N9 по stable/unstable, тот же oracle/домен,
covers unsorted/duplicate и прежние flags/600 с; неизменённый принятый N8 не повторять.
Чистая library delta: +49 строк только verify/types.rs; исходные функции не менялись.
Rustfmt заданным wrapper/config --check exit 0; diff-check exit 0; исходник/отчёт ≤100 колонок.
[Запросы, bounded summaries, process peaks, tooling и реестр](unstable8/).
