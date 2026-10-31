# U8N9 — G2 запущен; ожидание через watch

Ветка: `experiment/kani-k1-ueightnine-20261031`.
Исходный SHA: `ac45675c2bdcf5629086b87b4a9a385b53df61db`.
Library SHA: `2c65b6cdd94ad22ac71be1bb301d9f4109d9035c`.
Frozen library tree G1/G2: `95a25d9241f071a8c22b6c6f5edebb3a31e45100`.
GO координатора получен для `3acc3c1997`; G1 dispatched по одобренному SHA.
Build UUID: `62f745bc-2db0-496c-812e-88107d76a4cb`.
T0 UTC `2026-10-31T10:10:25.393837+00:00`; deadline UTC `14:07:39`,
основная работа до `13:37:39`, резерв закрытия30min; `g1.preflight.json`.

G1: `RUN-REQUEST.json` = `u8n9/g1.request.json`, request_id
`u8n9-g1-measurement-20261031`: measurement, jobs1, controls:true, timeout600.
Baseline non-const combined + general + non-const stable + const stable = 4 entries.
Полный envelope 4*10+30=70 минут, максимум $0.945.
G2 только после SUCCESS general и хотя бы одной stable, все covers достижимы:
diagnostic/jobs3/controls:true; general N9, stable N9 по VT и RSS вместе,
ordinary combined u8 N8 и merge_scratch48_contract_u8_n9; тот же envelope.
Общий максимум 2 сборки / $1.890 <= $1.9; CAP_USD 73.96 прежний.
Собственный ledger `builds.json`: G1 UUID/request/source identities записаны.
G1 резерв <=$0.945, фактическая стоимость ещё неизвестна; сборок 1/2.

Перед G1 budget PASS; project used$64.2030/reserved$0; перед dispatch были
зафиксированы T0/deadline/резерв закрытия. Перед следующим dispatch:
оставшееся окно должно вмещать полный envelope и закрытие, перед каждым dispatch
вызвать `research/challenge-8/kani-k1/tools/k1g.sh budget`.
Не переносить соседние library-изменения. Перед G2 сверить frozen tree.
Каждую сборку ожидать только `k1g.sh watch UUID`, затем завершить ход.
Результаты читать только через k1g.sh summary/peaks/inventory/log-grep/log-lines/
check-tooling; строки логов <=200. Решать по строкам и covers, не aggregate gate.
После измерений записать русский RESULT-U8N9.md <=100 строк, отдельно split,
initializer, jobs3/CBMC overlap/peaks/OOM/missing, стоимость и интеграцию.
Успех одной ветви не заменяет обе; A u8 N9 автоматически не ретирить.
Оговорки: fixture48 не любой backing; macOS UNKNOWN; пригодность только CI организаторов.
Итоговые research-коммиты отдельно от library, [skip ci], push без force.
Окончательный маркер REVIEW REQUEST / U8N9 ЗАВЕРШЁН пока не отправлялся.

G1 завершён: Cloud FAILURE / summary COMPLETE / gate false из-за baseline TIMEOUT.
Все три split entries SUCCESS/covers1/1; g1.review.json связывает строки и direct RSS.
G1 стоимость$0.4185. Для G2 выбран non-const stable: VT221.65 против300.79с,
RSS0.422 против0.311GiB; преимущество VT при умеренной памяти, не оптимум CI.
G2 request `u8n9-g2-diagnostic-jobs3-20261031`, четыре entries jobs3;
библиотека прежняя. G2 допустим по TASK без нового GO; полный резерв$0.945.

G2 dispatched: `9a33a513-9346-44c0-9d05-dedfcc0c6e63`,
source `8a7c7f22b2d154eaa81c362ea9902d60cc0fef79`; tree прежний.
Сборок2/2: больше не запускать. G1 actual$0.4185 + G2 reserve$0.945 <=$1.3635.
G2 preflight UTC10:45:25, осталось202.23min: envelope70 + closure30 помещаются.
После уведомления: summary/rows/peaks, direct CBMC overlap и OOM/missing,
check-tooling относительно GO3acc3c1997; budget обоих собственных UUID.
Затем RESULT-U8N9.md <=100 строк, commit/push и финальные маркеры TASK.
