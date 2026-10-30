# UNSTABLE8 — FINISHED: N8 COMPLETE, optional N9 PARTIAL

Новых dispatch не делать: использованы 3/3 сборки, spent $0.9180, reserved $0 из $4.
Все UUID/request_id/source/cost находятся в builds.json; итог — в RESULT-UNSTABLE8.md.
G1 DropKey N8 SUCCESS 194.44167 с, covers 5/5, оба настоящих trait-маршрута с merge.
G1 combined Cell N8 TIMEOUT; оба negative FAILED на ожидаемых checks при корректном setup.
G2 Cell split: оба assertions SUCCESS, но covers 4/5 из-за opposite const branch.
G3 cover исправлен: Cell stable N8 SUCCESS 222.42752 с, 4/4;
Cell unstable N8 SUCCESS 206.487 с, 4/4. Дополнительный DropKey N9 TIMEOUT 600 с.
Обязательная N8-цель закрыта; общий gate G3 false из-за optional N9, не заявлять зелёным.

Library SHA 78c040559f448ea3cf05ec152ab1143014068570, соответствует G3 source b177a4bd5d.
После G3 source менялся только research/; library delta +49 строк в одном types.rs.
Ordinary не менялся: новые пять гармоник, helper и macro остаются opt-in.
Кандидаты Part 1: combined DropKey N8 и две fixed-route Cell N8.
macOS UNKNOWN; окончательную пригодность устанавливает CI организаторов.
Все oracle/domains/flags/pin/toolchain/lane-файлы прежние; check-tooling G1/G2/G3 прошёл.
Library-коммиты отдельно от research/; все commits [skip ci], push без force.
Alias dispatch experiment/kani-k1-unstable-20261030 указывает на G3 source b177a4bd5d.
Рабочая ветка experiment/kani-k1-unstable8-20261030 содержит итоговый отчёт.

Продолжение вне текущего лимита: fixed stable/unstable DropKey N9 с прежними guarantees.
Принятый неизменённый N8 не повторять; новый бюджет требуется для новых builds.
Никаких активных ожиданий после третьего уведомления нет, очередные watch не запускать.
Финальный ответ: REVIEW REQUEST <sha> и UNSTABLE8 ЗАВЕРШЁН; после маркера остановиться.
