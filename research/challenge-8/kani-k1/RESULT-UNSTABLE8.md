# UNSTABLE8 — PARTIAL, до обязательного PRE-BUILD REVIEW

Дата: 2026-10-30. Первая proof-сборка ещё не запускалась; GO не получен.
База: `6bbf03c764a5abafc2d4d5eeeb5f2972d6beaf46`.
Library SHA: `14f60a96372172c8699b050b64f878c2b0739dd2`.
Review SHA — commit, добавляющий этот отчёт; запрос и checkpoint в [unstable8/](unstable8/).
Build ID: нет. Свои сборки 0/3; стоимость $0, reserved $0, лимит $4.
Gate request_id: `unstable8-gate-20261030`; envelope 70 минут / $0.9450.
Ledger при подготовке: spent $56.5350, reserved $0; CAP_USD $73.96 не менялся.

| Тип | N | Маршрут | Статус | VT GCB | RSS | Covers |
|---|---|---|---|---|---|---|
| DropKey | 8 | stable + unstable, general | NOT_RUN | — | — | — |
| Cell<u8> | 8 | stable insertion + unstable fallback | NOT_RUN | — | — | — |

Новые гармоники opt-in; fixed_trait_case вызывает существующий trait_properties.
Сохраняются полные символические байты, произвольный probe и stable: bool.
Общий check_output проверяет sortedness по logical value и его мультимножество.
Ожидаются covers обеих ветвей, возврата после assert, unsorted input и duplicate keys.
DropKey использует настоящие тела с merge; Cell comparator только читает значения.
Новых доказанных случаев пока нет: добавление гармоники не является PASS.

Контроли пока NOT_RUN: reject_logical_permutation_drop_n2 должен отказать на counts;
reject_logical_sortedness_cell_n2 — на sortedness при корректном setup.
Oracle и существующие контроли не менялись; gate использует controls:true, jobs=1.
Kani pin 9461e07a, toolchain, flags и lane-файлы не менялись.

После GO: gate → при TIMEOUT/OOM split только незакрытых ветвей; при успехе — отдельный N9,
если полный envelope помещается в остаток ≤4 ч и $4/3 сборки. Принятый N8 не повторять.
Измерений памяти нет; после build указать индивидуальные пики CBMC/driver и метод.
Числовой safe-gate не назначается. N0..2 + N8/N9 не образуют непрерывного диапазона.
Кандидаты в ordinary Part 1 появятся только после принятого PASS; переводит координатор.
macOS UNKNOWN; пригодность устанавливает только CI организаторов.
Вне цели: drop-счёт, unwind, generic T и доказательство стабильности по identity.
Заданный rustfmt --check и Python request validate прошли (exit 0).
