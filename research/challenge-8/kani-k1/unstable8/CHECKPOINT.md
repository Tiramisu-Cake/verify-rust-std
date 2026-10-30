# UNSTABLE8 — последняя сборка запущена

G1 DropKey N8 SUCCESS 194.44167 с, 5/5; combined Cell N8 TIMEOUT.
G2 Cell stable/unstable N8 SUCCESS 330.23926/237.26244 с, но covers 4/5 у обоих.
G2 gate false только из-за недостижимого cover противоположной const-ветви.
Из-за terse output названия отдельных covers в log-grep не напечатаны.
Диагноз следует из const true/false и двух branch-local cover при пяти общих covers.
G1/G2 source/build/request/cost сохранены в builds.json и RESULT-UNSTABLE8.md.
G1/G2 check-tooling: lane-файлы равны базе 6bbf03c764; Kani pin 9461e07a прежний.

Library G3 78c040559f448ea3cf05ec152ab1143014068570.
Исправление: route cover перенесён в macro с выбранным literal; недостижимого cover нет.
Check_output, входы, any probe, comparator, flags, timeout и solver прежние.
Гармоники Cell N8 изменены для корректного measurement gate; DropKey N8 не повторяется.
Добавлен opt-in fixed_trait_case DropKey N9 с исходным symbolic stable.

G3 request unstable8-final-20261030, measurement, controls:true, jobs=1.
Три positive: исправленные Cell stable N8 + unstable N8 и combined DropKey N9.
Контроли G1 приняты; oracle не менялся, новые negative не требуются.
Envelope 3 × 10 + 30 = 60 минут, $0.8100; свои $0.5805 + $0.8100 = $1.3905 из $4.
Это третья/последняя разрешённая сборка; дальнейших dispatch не делать.
Консервативный cutoff 2026-10-30 22:30 UTC включает полный envelope.
Перед dispatch обновить общий budget; alias unstable продвинуть без force на source G3.
После dispatch записать UUID, вызвать k1g.sh watch BUILD и завершить ход.
После G3 завершить отчёт COMPLETE/PARTIAL по реально полученным результатам и push.
Последние строки: REVIEW REQUEST <sha> и UNSTABLE8 ЗАВЕРШЁН; после маркера остановиться.

G3 build `2fbe4ddc-a6c0-4cd9-8056-12c7c828b7f8`.
G3 source `b177a4bd5d46ae30edf1d75379ff7c43a7f19720`.
Dispatcher ledger после G3: spent $57.8850, reserved $2.5650, total ≤$60.4500/$73.96.
Свои spent $0.5805, reserved $0.8100; сборки 3/3, больше не запускать.
