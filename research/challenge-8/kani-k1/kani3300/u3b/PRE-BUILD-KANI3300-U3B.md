# KANI3300 U3B — PRE-BUILD

Статус: PREPARED WITH BLOCKER; native NOT_RUN. Dispatch запрещён до exact-packet GO и устранения pinned preflight blocker.
Задание TASK-KANI3300-U3B.md; планер PLANNER-AFTER-U3-ANSWER.md, п.1–2,5–6. Одна стадия; repair не разрешён.

## Identities

- Research: experiment/kani-k1-kani3300u3-20261111; вход HEAD 538e907ad69f3c7726e39468bab9a7050f6ed5c5 (после указанного в задании 0c30efc5d2 добавлен только сам TASK).
- Kani fix/kani-3300-v2: `0ab9cc703aed799f6f73d826b60281a4632ab585`; parent `81dd85bfce67226e283fdd9a156932e32ece080b`; автор Tiramisu-Cake <igkharin@gmail.com>, отдельный test-only `[skip ci]` commit.
- Pin `f046b70644e113be0df9c22c2e6ea44a65a57566`; tooling base `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`; toolchain прежний nightly-2026-10-23.
- Patch `kani-uninit-v2-u3b.patch`, SHA256 `129fa3742499ad06700e35519a711e2b555a29d6f2eedcff5b21236c7795bb4e`.
- Request `kani3300-u3b-20261111-01`, SHA256 `cf447c650c10c2559e66d81f95f2d4f0dc53c0941c6090a66f12e6fbb5fa77db`; root request и snapshot побайтно равны.
- Applied/candidate tree `ef32d0009a730c26dc99e8ab828744128de69b15`; fresh --check --index/apply прошли внутри штатного preflight.

## Production и tests

Production diff (7 файлов) побайтно равен production-части полного U3 repair1 patch SHA256
`f3f8a82c2c22798361bf51bf6186aa60cadb1de68d0aa15b15ad62d601138c1c`.
SHA256 обоих production diff: `a4eaf382f0fde32b7f6909c8120fe34298abf09fbdd3fd126e6fec13ae994ad4`.
Git production delta от 81dd85b пустой; compiler/DFCC/ghost state/пин/toolchain/lane tooling не менялись.

Delta — только 11 test/golden файлов: четыре новых fixtures с exact harness, frame golden и terse у двух positive регрессий.
`contracted_roundtrip_harness` изолирован с choose/relay и исходным modifies(out); другие roots/clause helpers из positive не перенесены,
так как этот root не использует stub_verified/clause contracts. `contracted_uninit_read_harness` сохранён с return_second/nested_return/modifies(out).
В каждой fixture ровно один proof root. Исходные buffer positive (4 roots) и PFC negative (1 root по фактическому исходнику)
сохранены побайтно, NOT_RUN; полного повторения U3-пакета нет.
Каждая no-uninit копия отличается от соответствующей on-fixture только удалением `-Z uninit-checks`;
тело, contract, DFCC options, exact root и terse совпадают. Никаких assumes, stub additions или ослаблений goldens.

Frame остаётся regular: golden требует assigns + Status FAILURE + `Check that *var_7 is assignable` + Location main.rs:22:5,
а также подряд Failed Checks и File/line22/function. Сам main.rs не менялся: line22 — пользовательская запись *outside.
Обе усиленные группы сопоставлены с координатами сохранённого bounded excerpt build45287677;
это не новый native result. Regular сохранён ради класса assigns и подробной location, новые PFC fixtures используют terse.

## Девять selectors и ожидания

| offset | fixture | exact root / coverage | ожидание Kani |
|---:|---|---|---|
|0|u3b-pfc-positive|contracted_roundtrip_harness|SUCCESS|
|1|u3b-pfc-positive-no-uninit|contracted_roundtrip_harness|SUCCESS|
|2|u3b-pfc-negative|contracted_uninit_read_harness|uninit FAILURE u16, Failed Checks|
|3|u3b-pfc-negative-no-uninit|contracted_uninit_read_harness|SUCCESS, диагностический контроль|
|4|u3-frame-negative|frame_negative|assigns FAILURE *var_7, user line22|
|5|wrap-u3-positive|все7, включая empty_harness|SUCCESS, require_success=true|
|6|buffer-u3-plain-negative|исходный root|uninit FAILURE u16|
|7|review-positive|все7, прежний golden|SUCCESS, require_success=true|
|8|review-overwrite-copy|U1T overwrite_copy|uninit FAILURE [u8;2], Failed Checks|

Для negative без uninit-checks ожидается SUCCESS: payload u16 имеет допустимые любые битовые значения, контракт только modifies(out),
дополнительного value assertion нет, а shadow-init instrumentation выключен. Это диагностическое поведение инструмента;
программа содержит uninitialized read, и SUCCESS этого off-контроля не даёт credit её корректности.
Проверяемый negative с включённым uninit обязан дать конкретный Failed Checks; unexpected SUCCESS — blocker, стоп и «Координатор, вопрос».
OOM/timeout/error не заменяют ожидаемую uninit FAILURE и не ведут к ослаблению golden.

## Статическая проверка и блокер

[STATIC-CHECKS.json](STATIC-CHECKS.json): validate9 PASS, six Rust files rustfmt PASS, diff-check PASS, patch/control identities PASS,
исходные buffer fixtures unchanged, production equality PASS, все lane paths и pins побайтно равны KT2.
Новый independent semantic review не нужен по CORE: test-only delta сохраняет/усиливает controls, production и dependencies прежние;
существующее production review — u3/repair1/REVIEW-FLAT-BUFFER.md (его native acceptance не расширяется).

[PREFLIGHT-OBSERVATION.json](PREFLIGHT-OBSERVATION.json): штатный prepare-kani на чистом точном pin вернул exit2:
`REQUEST_INVALID: patch diffstat exceeds bounded report size`. Diffstat4483 >4096 bytes; применённое дерево совпало с candidate.
Tooling не изменён, gate не обойдён, source/test controls не удалены ради размера. Пакет НЕ dispatch-ready.
Координатор, вопрос: требуется отдельно разрешённое изменение bounded diffstat reporting с новым принятым tooling base
либо другое решение в рамках задания. Даже GO на текущий пакет не устранит этот воспроизводимый preflight отказ.

## После GO / evidence / бюджет

Native budget10min, selector150s, runner gcb-e2-standard-4. Proposed reserve(10+30)*$0.0135=$0.540 <= cap$0.60;
spend/reserve этой стадии сейчас0/0, Builds0. Подготовка пакета не регистрирует phase и не разрешает dispatch.
После отдельно разрешённого устранения blocker и exact GO: штатный dispatch; `k1g.sh watch BUILD`, затем конец хода.
После terminal — bounded summary/check-tooling/native/native-field; по offsets0–3 terminal cause, actual Failed Checks,
wall_s и все доступные memory поля. Null/missing RSS оставить UNKNOWN; отсутствие строк не означает OOM.
Сравнить on/off пару, сохранить Kani-reported OOM отдельно от измеренного RSS; не выводить конкретную причину роста из одной пары.
Неожиданный SUCCESS on-negative — немедленный стоп. Результат <=30 строк; полный v2 review-ready/known limitation/нужен фикс
решать по фактическому native evidence. Сейчас всё native NOT_RUN. Raw logs/archives/credentials не читались;
локальные cargo/rustc/Kani/CBMC не запускались. Никаких Actions/PR/issue и production changes.
