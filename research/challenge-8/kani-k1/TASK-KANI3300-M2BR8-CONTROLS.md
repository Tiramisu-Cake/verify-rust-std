# KANI3300 M2-B/R8-C — nonzero witness через Move/return, worker 14

**Параллельно R8 worker15; одна test-only сессия, Cloud $0**, fork CI только координатора.
Это верификация корректности, не security-работа.
R7-C **fe36afc4a8de2709f00524b2d3fbd6da17919728** уже принят: не переделывать/дублировать его P1/P2/frame controls.

## Вход и write boundary

Читать TASK-KANI3300-M2BR8.md и m2br7c/CONTROL-MAP.md. Base
**8e01eb2aff5183c53403e1d1e73e573ce28d3095**, tree **8554b019e0eb8d2daf09e5ab70bc0c0d09917de1**,
read-only `/root/kani-fix-3300-m2br7`; R7-C delta уже присутствует. Создать
**/root/kani-fix-3300-m2br8-controls**, branch **experiment/kani-3300-pointer-transfer-controls** от exact base.
Existing/dirty destination → STOP без reset/stash. Только новый **tests/expected/uninit/private-transfer-pointer/**
и research **kani3300/m2br8c/**; source/existing tests/goldens/worker15 files не менять.

## До двух selectors: meaningful witness offset, не scalar-only calibration

R7 P1/P2 u8 имеют relative0; они не исключают потерю ненулевого offset при pointer carrier/dead source metadata.
Сделать small ordinary legal/hole pair, -Zuninit-checks, без PFC/нового heap/foreign ABI:

- Canonical **MaybeUninit<Payload>**, `#[repr(C)] Payload` из3 u8 fields, **без Copy/Clone/Drop**.
  Не outer `MU<[MU<T>;N]>`; это обычный supported MU of small struct, data size3 без padding.
  Fully written positive и payload с hole только в третьем байте/поле. MU storage/reference до read valid.
- Передать по значению через inline(never) Item helper и вернуть по значению: compiler должен сохранить actual Call(Move)
  и normal-return store0/load0. Kernel snapshot берётся пока source жив, до caller Move clear; pointer metadata потом переживает
  source frame. Тип NoCopy лишь source hint — actual MIR/Slot/frame/deinit binding запросить в CI, не заявлять его observed.
- После вызова прочесть initialized первые2 fields и затем third через lawful raw field-pointer/read.
  **Нельзя assume_init всего Payload с hole**, создавать &Payload или раньше читать неинициализированный field.
  `addr_of!/addr_of_mut!` от valid MU-derived raw pointer допустимы после source/API/type audit; pointer projections не data read.
  Legal ожидает SUCCESS и useful values; hole ожидает intended third-byte u8 uninitFAIL, первые reads и protocol guards lawful.

Максимум2 новых single-root selectors,4 source/golden files; copyright/license/edition/-Dwarnings audit.
Не вызывать private Kani metadata APIs из user test и не форжить fn_marker ради контроля.
Goldens semantic, без guessed var_N/property IDs. Обычный FAIL/новый carrier guard FAIL не заменяет intended payload failure.
Такая пара различает snapshot-before-Move (legal data не становятся false после deinit) и false-transfer сохранность.
Ненулевой selected witness/after-return metadata требуют actual bound path, а не вывода из одной FAILURE.

## Передача и CI qualification request

Test-only commit на exact base; source subtree unchanged, old R7-C files unchanged/hashes.
Owner15 получает exact new-path-only delta/parent/tree/hash, импортирует только tests в R8 candidate, не ваш старый source.
Не ждать его code/переопределять carrier. Если fixture layout/ABI не supported, конкретный blocker без расширения модели.

CONTROL-MAP: все original R7-C rows reuse + два новых с actual offset2, allocated extent3/source-slot и dataflow
store-before-Move/deinit→callee param→return0/slot/frame cleanup→normal load→read. Request matched type/layout/MIR/callkind
и source property/guard binding; если backend элиминирует death/Move/offset, отметить missing qualification, не credit.
Нужны both legal/hole и отсутствие extra private frame/Unsupported/carrier invariant failure.
Для pointer private fields R8 требовать actual assigns адресов **cells в ARGUMENT_BUFFER**, не saved pointee/user allocation.
Existing lawful/outside-frame/clause/P1/P2 проверить по R7-C без копирования; failed private write не считать user frame control.

CI coordinator после R8 P1 resource gate: два ordinary new selectors по одному, затем existing controls/main G2.
Existing300s/RSS watchdog>6GiB/flags/toolchain/inputs/actual exits, cutoff INCOMPLETE, setup fail NOT_RUN.
Тесты локально не запускать; source prediction/actual MIR/verdict отдельно. Missing/capped data UNKNOWN,
raw logs/archives/full formula не читать/качать; только existing curated interface/precise bounded query.

## Результаты и review

TYPE-AUDIT: MU/raw pointers/lifetimes, !Copy payload, field offsets/types, no invalid typed value/reference,
usize counts и signatures; audit unused fields/imports/-Dwarnings, B3 E0308/E0277 помнить. Pinned rustfmt TASK-M1/hash/diff/Python можно.
Один bounded Luna High input/golden/Move/offset review без nested delegation. Local cargo/rustc/Kani/CBMC/Miri/builds запрещены.
g0 **kani3300/m2br8c/**: INPUTS.json, CONTROL-MAP.md, TYPE-AUDIT.md, TEST-MANIFEST.json, REVIEW.md,
CI-REQUEST.md, RESULT-KANI3300-M2BR8C.md (≤20 строк). Source-ready/NOT_COMPILED, proof credit0, M3 не активировать.
Local test-only commit без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, **не push**.
Research [skip ci], тот же author/committer, stage только m2br8c/, push g0 без force; concurrency → handoff без reset/stash/чужих файлов.
Без CI/Actions/Cloud dispatch/workflow/runner edits, credentials, PR/issue/комментариев/сторонних PR links.
После reviewed package STOP. Последняя строка: `READY <sha локального test-only R8-C Kani-коммита>`.
