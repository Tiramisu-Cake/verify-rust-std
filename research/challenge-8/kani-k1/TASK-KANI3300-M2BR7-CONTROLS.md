# KANI3300 M2-B/R7-C — P1/P2/private-frame acceptance controls, worker 14

**Параллельно R7 worker15; одна test-only сессия.** Runtime **Codex**, **Cloud $0**, CI только координатора.
Это верификация корректности, не security-работа.
Цель — точные controls и property/frame qualification нового private transport; source/integration owner15, M3 пока HELD.

## Вход, clone и write boundary

Прочитать TASK-KANI3300-M2BR7.md, m2br6b/ и M2 QUALIFICATION-MAP. Base
**4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c**, tree **af28e22ec446b254cfa3a28b2882eafa58d5a458**,
read-only `/root/kani-fix-3300-m2b-seed`. Не CI-only filtered tree. Создать отдельный
**/root/kani-fix-3300-m2br7-controls**, branch **experiment/kani-3300-private-transfer-controls** от exact base.
Existing/dirty destination → STOP без reset/stash. Только **tests/expected/uninit/private-transfer-frame/**
и research **kani3300/m2br7c/**; library/compiler/existing fixture/golden/worker15 files не менять.

## Минимум новых inputs, reuse уже имеющихся

1. **P1 legal** побайтно из m2a/cases/scalar-pfc-legal.rs, hash
   **fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b**; materialize в собственном test path,
   expected all checks SUCCESS. Exact proof_for_contract root `postcondition_reads_initialized_return`, no arrays/heap/extra attrs.
2. **P2 reuse** active `transfer-qualification/postcondition-hole.rs`, hash
   **61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759**; не создавать duplicate selector.
   Intended outcome — valid MU return, первый payload read в ensures у8 FAILURE, lawful body/frame/protocol без extra failure.
3. **Новый lawful-modifies positive** — маленький sibling existing maybe-uninit-contract-frame:
   ordinary initialized MU argument/return через choose/relay, function с modifies(out) пишет только out и useful scalar
   postcondition/result assertion; separate outside input остаётся нетронутым. Ожидается PFC SUCCESS, включая все private writes.
   Без old/dynamic allocation/нового generic ABI/arrays, no initializedness premise вместо проверяемого transfer.

Новых selectors **до2** (P1 + lawful positive), semantic goldens, не guessed generated property IDs.
Сохранить copyright/license/edition/uninit+function-contracts flags и -Dwarnings audit. Bare failed summary не достаточен.
Reusable controls, source/hash/actual root/required binding записать в CONTROL-MAP:

- `maybe-uninit-contract-frame`: negative user *outside write, modifies(out); frameFAIL именно на этом user assignment,
  private Begin/store/load/init/clause writes не дают лишний frameFAIL. Existing source/golden не править заранее.
- `maybe-uninit-contract-clause`: requires helper reads returned uninit MU; intended clause uninitFAIL, не false frame.
- call-pairing/argument-buffer/argument-return/call-move: selected first/middle/last с gap indices, nested/repeated calls,
  initialized return positive, false-state preserved и snapshot-before-Move. Проверять protocol counts/signatures/return0.
- unchanged M2 out-pointer/normal-abort и full legal-pair: reuse вместо новых copies; прежние gaps/extra Failed Checks не скрывать.
- C03/S3 ensures-left/right-hole const HOLE, D0/mixed/immutable-masks/unit5: regression мост новой representation к M1/S3.

Для каждого negative — lawful input/reference до intended read/write, expected source location/class, legal companion и
extra-failure checks. Payload false ≠ no witness, unselected ≠ missing protocol; expected failure не доказывает другую ветвь.
Если bridge/root не supported по pin, вернуть exact blocker, не расширять модель/менять scope с nested MU helpers.

## Qualification request и передача owner15

Новый test-only commit на base, exact file/diff/hash/parent/tree. Отправить15/координатору SHA и new-path-only delta;
он импортирует tests в B0/B1, не переносит ваш production base поверх source. Concurrent source ожидать/дублировать не нужно.
P1 source bytes/goldens не подстраивать под base falseFAIL/OOM; oracle из семантики. Existing hard-coded var_N в frame golden
может смениться: update только после реального CI с binding actual outside user write, отдельной правкой владельца/координатора.
Ранний private assignableFAIL нельзя принять за нужный user negative.

CI-request — G1 из main task: P1B0/B1 resource comparison, затем P2/lawful/frame/clause/false controls на выбранном candidate,
один root/solver, existing timeout300s/RSS watchdog>6GiB. Перед solver inventory: reset→seed→transfer→ensures actual path,
main+buffer exact distinct private symbols, main target и полный buffer-field lambda set (не ожидать ровно2 lambdas),
caller source follow и live destination/typed mask.
Marker/source presence без emitted/reached binding не proof. Capped/no-match UNKNOWN, parser/job success не semantic PASS.
Build/fmt/clippy сначала; source/compiler/tool/input/flags/CI tree/receipt identities и all Failed Checks отдельно.
Затем G2 full Uninit Quick **без исключения legal-pair/postcondition-hole**; возможный новый count не угадывать.
Local CI/сборки не запускать и не ждать. Если R7 resource gate не проходит, новые semantic outcomes остаются NOT_RUN.

## Static review и результат

TYPE-AUDIT tests: actual MU/typed/reference lifetimes, return/ensures closure signatures, integer types/usize/u64/deref,
no invalid typed value before intended read; B3 E0308/E0277 учесть. Pinned rustfmt TASK-M1/diff/hash/Python разрешены.
Один bounded Luna High input-validity/golden/coverage review, без nested delegation/model redesign; compilation NOT_RUN.
g0 **kani3300/m2br7c/**: INPUTS.json, CONTROL-MAP.md, TEST-MANIFEST.json, TYPE-AUDIT.md, REVIEW.md,
CI-REQUEST.md, RESULT-KANI3300-M2BR7C.md (≤20 строк). Не повторять историю, перечислить gaps/NOT_RUN/bindings.
Local Kani test commit без [skip ci], author/committer Tiramisu-Cake <igkharin@gmail.com>, **не push**.
Research [skip ci], тот же author/committer, stage только m2br7c/, push g0 без force; concurrency → handoff без reset/stash/чужих файлов.
Без local cargo/rustc/Kani/CBMC/Miri/builds, CI/Actions/Cloud dispatch/workflow/runner edits, raw logs/archives/credentials,
PR/issue/комментариев/сторонних PR links. После reviewed test package STOP; M3 только по отдельному accepted handoff.
Последняя строка: `READY <sha локального test-only R7-C Kani-коммита>`.
