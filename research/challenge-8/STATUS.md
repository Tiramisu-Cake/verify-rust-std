# MERGE — stale base pin: исправление подготовлено, без commit/Build

2026-10-17: владелец предоставил ограниченный admin audit Build `a7ad5ce8`
и принял причину: `provider-overlay` отказал на устаревшем base pin `run.sh`.
Сообщение full-stderr.log:2 передано владельцем; raw evidence здесь не читались.
Ожидаемый `a0ddebad…` соответствует parent `e2d8182f`/blob `a65817f5…`;
фактический `ae0aa063…` точно воспроизводится из proof `08b61d81`/blob `a7db3efd…`.
Статически base validation расположена до transforms/static-preflight/runner.
Brief v2 подтверждает mismatch, но не выполнение стадий; о запуске инструментов
и результатах верификации по этому Brief утверждений нет.

По отдельному поручению подготовлена замена одного pin в `provider-overlays.py`;
все 18 checks без изменений. Recipe связывает adapter и inputs одним PROOF_SHA,
старые commits используют свои adapter pins; override-конфигураций не найдено.
Regression test: 18 Git blob hashes, synthetic positive boundary и однобайтовый
отказ для каждого input до transforms/без изменения sources. AST/bash syntax
и static production diff checks прошли. Независимый source review GPT-6 Luna High: GO, замечаний нет; reviewer также
выполнил три regression tests и diff check: PASS. Исполняемый fix/test оставлены uncommitted для решения владельца.
Повторная сверка происхождения и три regression tests 2026-10-18: PASS.
Fix готов к фиксации и следующему отдельно разрешённому CI Build; не cloud-tested.
Новых Builds/бюджета/proof credit нет; tool/profile/ledger/verdicts сохранены,
CLOSED 103/960 s, 857 retired. Commit и Build требуют следующих решений владельца.

Предыдущие checkpoints ниже сохранены как история.

# MERGE — административный аудит: требуется ограниченная выборка

2026-10-17: продолжение от `df0a29a0`, owner merge, новых Builds/бюджета 0.
Причина отказа `a7ad5ce8` и достигнутые исполнительные стадии **не установлены**.
Reader 0.3.0 `/index` и `/receipt` подтверждают прежний неполный Brief;
executed profile unknown. Проверенные bounded diagnostic routes возвращают 404,
`run.services.list` запрещён текущей identity. Другие admin interfaces не исключены.
Raw archives/logs на VPS не скачивались; IAM, production и coordinator не менялись.

[Точный запрос администратору](cloud-build/origin-layout/ADMIN-AUDIT-REQUEST-20261017.md)
задаёт ограниченную выборку failing command/exit/excerpt, stage markers и
creation→packaging→processor для campaign/cases, с provenance.
[Отдельный результат](cloud-build/origin-layout/ADMIN-AUDIT-RESULT-20261017.json)
сохраняет исходные compact reports и hashes. Исправление без причины не подготовлено;
кандидат к следующему отдельно разрешённому Build пока не готов. Изменён только
checkpoint/документация. Исторические verdicts/pins/ledger сохранены.
Счёт CLOSED **103/960 s, 857 retired**, retry запрещён. Нового proof credit нет.
Обычные дальнейшие CI results — исключительно `smallsort-brief BUILD_UUID`.

Предыдущий checkpoint ниже сохранён как история.

# MERGE — первое comparator: CLOSED / INCONCLUSIVE

Нового normal/unwind proof credit нет. Подготовлены и независимо статически
проверены concrete-u64 HRTB, локальное восстановление первого Continue и узкая
проверка official refiner. Prefix явно обрезан перед tail.read; полное тело и
конечные posts сохранены отдельно. B2 остаётся открытым.

Build **a7ad5ce8-2cba-415e-8d7f-6d4ca78ef125**: terminal FAILURE.
`smallsort-brief`: VERIFIED_ARCHIVE_AND_INVENTORY, source NOT_ACCEPTED,
evidence_complete=False, 12 inventory files / 5 text entries; **нет campaign,
cases или стадии отказа**. Первый установленный blocker — недостаточность Brief
для определения причины. Нельзя выводить compiler/proof failure, NOT_RUN или PASS.
Raw evidence не читались, download_verified не повышался.

Proof = infra `08b61d8162b1c01c840ed573847622a004232a05`;
tool `d928cb1d7ac60c257daa537fa65577f41135f832`;
profile `300fd8a7172c1644552b43c5bfda51a7c8a620f505012abd3760772df55102e3`,
experimental-merge-first-callback-u64-v1, NOT_ACCEPTED / NOT_FOR_INTEGRATION.
Kernel/model/prelude/runtime std сохранены. История трёх сессий и прежний B1
в bounded normal domain не переписаны. Инструкции Evidence Brief сохранены в584891be.

Отдельный счёт owner merge CLOSED: **103/960 s, 857 s retired**; один Build
израсходован, carryover/retry нет. T0 00:32:42Z, main02:32:42Z,
absolute03:02:42Z; закрыт01:06:46.731264Z. Своих active/request/unresolved нет;
existing v3/max3 сохранён.

Следующий шаг требует отдельно разрешённого admin audit для определения стадии;
затем конкретное исправление и отдельно разрешённый новый Build при необходимости.
[Checkpoint](cloud-build/origin-layout/FINAL-CHECKPOINT.md) ·
[Result](cloud-build/origin-layout/FIRST-CALLBACK-RESULT-20261017.json) ·
[Pins](cloud-build/origin-layout/FIRST-CALLBACK-PINS-20261017.json) ·
[Review](cloud-build/origin-layout/FIRST-CALLBACK-REVIEW-20261017.md).
