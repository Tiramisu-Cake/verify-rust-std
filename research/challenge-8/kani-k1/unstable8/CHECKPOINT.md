# UNSTABLE8 — Cell split запущен

Рабочая ветка experiment/kani-k1-unstable8-20261030; alias для dispatch — unstable.
База `6bbf03c764a5abafc2d4d5eeeb5f2972d6beaf46`; GO на G1 source 5ff343a759 получен.
G1 build `64a70b50-30b2-4d26-b25b-7ed1463b4851`, request unstable8-gate-20261030.
G1: DropKey N8 SUCCESS, 194.44167 с, covers 5/5; Cell N8 TIMEOUT 600 с.
Оба negative FAILED на ожидаемых expressions, корректный setup; summary COMPLETE.
G1 стоимость $0.3105; registry builds.json содержит только собственные UUID/request_id.

Library split `956a758288f483bef38d27372e08877bfbfd2212`.
Добавлены opt-in fixed_route_trait_properties и macro + две Cell N8 гармоники.
STABLE — const true/false; только input [u8;8] и probe символические.
Маршруты исходные, logical_less read-only; check_output не менялся.
В каждом случае covers: возврат после assert, unsorted, duplicate и выбранный trait route.
Домен исходного harness = объединение двух fixed-route доменов, без ограничений input/probe.
Combined DropKey N8 сохранён и не запускается повторно; combined Cell остаётся opt-in.

G2 request unstable8-cell-split-20261030, measurement, controls:true, jobs=1.
Ровно две positive Cell N8; контроли G1 уже приняты, oracle не менялся.
Envelope 2 × 10 + 30 = 50 минут, $0.6750; свой spent+envelope = $0.9855 из $4, build 2/3.
Перед dispatch проверить текущий общий ledger и полный envelope; CAP_USD $73.96 прежний.
Консервативный cutoff дальнейших сборок: 2026-10-30 22:30 UTC, включая полный envelope.
После push продвинуть alias без force на тот же source SHA и dispatch.
Записать G2 UUID/request_id, вызвать k1g.sh watch BUILD и завершить ход.

После G2: сохранить любой частичный PASS; не повторять неизменённый принятый N8.
При достаточном остатке отдельный N9 выбранного типа/тех же маршрутов, третья сборка.
Не повышать timeout, не менять domains/oracle/flags/pin/toolchain/lane-файлы.
Rustfmt заданным wrapper/config exit 0, diff-check exit 0; tooling G1 равен базе.
Дальнейшие результаты/VT/RSS фиксировать в RESULT-UNSTABLE8.md (≤100 строк).

G2 build `93263f1d-d590-454b-a496-a3c2f479b07f`.
G2 source `2d2cdfff1fc564b9f7e3e4ab5e6a4d1f74e808cb`.
Budget перед G2: spent $57.1425, reserved $0.5400; вместе с G2 ≤$58.3575.
Свои spent $0.3105, reserved $0.6750, сборки 2/3; ждать watch, затем summary/peaks.
