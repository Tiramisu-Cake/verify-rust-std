# UNSTABLE8 — кандидат до первой proof-сборки

База worktree: `6bbf03c764a5abafc2d4d5eeeb5f2972d6beaf46`.
Library commit: `14f60a96372172c8699b050b64f878c2b0739dd2`.
Рабочая ветка: `experiment/kani-k1-unstable8-20261030`.
Стадия: PRE-BUILD REVIEW; GO ещё не получен, dispatch запрещён до ответа.

Добавлены только две opt-in гармоники N8 в verify/types.rs, через fixed_trait_case.
Обе наследуют trait_properties: полный any [u8; 8], any probe и any stable: bool.
Нет assume, stubs, новых helper-ов или изменений oracle; solver cadical, unwind(50).
Пять covers: возврат после assert, stable, unstable, unsorted, duplicate.
DropKey: stable → general-with-scratch48; unstable → Freeze-default → general.
При N8 обе ветви DropKey используют настоящий sort4_stable и bidirectional_merge.
Cell<u8>: stable → insertion; unstable → fallback → insertion; comparator read-only.
N8 ниже порогов 32/16; логическая sortedness и counts проверяются общим check_output.

Gate: unstable8-gate-20261030, measurement, k1-merge, k1-standard4, jobs=1.
controls:true; явный список: два positive N8 и два существующих negative N2.
Drop negative должен отказать на counts; Cell negative — на sortedness.
expect_check содержит выражение соответствующего assert, без изменения oracle.
После запуска проверить также корректный setup и отсутствие постороннего отказа.
Gate request сохранён отдельно в gate.request.json и установлен в RUN-REQUEST.json.

Envelope: 4 × 10 + 30 = 70 минут, максимум $0.9450; timeout не повышен.
Предварительный ledger: builds 99; spent $56.5350, reserved $0, cap $73.96.
Свой реестр builds.json пуст: 0/3 сборок, spent+reserved $0/$4.
Непосредственно перед dispatch повторить k1g.sh budget и пересчитать остаток окна.
Учитывать только собственные UUID/request_id: agent k1-merge общий с другими задачами.

k1g.sh dispatch допускает только буквенное имя задачи; unstable8 не проходит regex.
После GO создать и push без force alias experiment/kani-k1-unstable-20261030
на точном reviewed SHA и dispatch через него; рабочую ветку не переименовывать.
На момент подготовки alias отсутствует в origin; перед созданием проверить снова.
Lane-файлы и CAP_USD не менять. Ждать только k1g.sh watch BUILD и завершать ход.

После gate: оба SUCCESS → не разделять; при достаточном остатке выбрать N9 отдельно.
TIMEOUT/OOM → route-fixed helper только для незакрытого типа/маршрута, opt-in.
Split использует тот же input/probe/oracle; объединение stable=true/false равно bool.
Частичный PASS другого типа сохранить; неизменённый принятый N8 не повторять.
На каждом шаге проверять полный envelope, общий cap, собственные $4/3 и окно ≤4 ч.

Проверки до review: заданный rustfmt --check exit 0; git diff --check exit 0.
Python validate: request accepted, 4 harmonics; lane/toolchain/flags равны базе.
Ни rustc/cargo/Kani/CBMC, ни внешние CI локально не запускались.
Proof-результатов, измерений VT/RSS и принятого N8 пока нет.
