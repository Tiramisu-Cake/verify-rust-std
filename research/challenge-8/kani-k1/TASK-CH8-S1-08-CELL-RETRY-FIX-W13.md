# TASK — W13: закрыть W14-CELL-RETRY-01, только fallback controls

Это верификация корректности, не security-работа. Отвечай кратко. Продолжение исходного автора;
текущая pane-модель/effort, без субагентов. Времени достаточно: STOP только по реальному blocker,
не из-за объёма/контекста. Одна компактная стадия подготовки, без dispatch.

## Exact вход

- Review g0 `ec48e6d59b552da2a9aa8d985478bf259c950073`,
  `kani3300/ch8-s1/s1-08-cell-retry-review/REVIEW.json` и HANDOFF.md.
- Old package g0 `9f4c37c894e7fecee0f59321ba66b65309a87606`,
  control `da8c766f957c576eafa44bccfba2c45490cef6d1`,
  tree `a0e21f185de757c05397cf32547153325012469f`, parent `9208b373c0a08a265fa0d7493a6529e331065271`.
- Base7c `7c41333f9bfcfd7eb4e0ede7bd316443090c9025`,
  source `99e8456d200fff1299ee5756279cddb23921dc65`, tool `0aac16ef62da9e9d5645782d458593e5d78143ba`.

## Исправление

Закрыть единственный OPEN finding `W14-CELL-RETRY-01` (P2): workflow исключил test_package.py,
новая cell-only selection сохранила guards/build-wrapper, но утратила две обязательные fallback гарантии:
`test_fallback_terminal_after_setup_failure_and_mid_run_interruption` и
`test_fallback_preserves_receipt_materializes_tail_and_bounds`.

Адаптировать их для exact cell pair и реально включить в workflow preflight. Проверить сохранение captured/
completed row и compile receipts, original exit/signal/exception; interruption только in-progress material;
terminal context после interruption/setup failure; bounds. Добавить различающую in-memory overwrite mutation
ниже payload hash gates: замена sole `if not receipt.exists():` на `if True:` должна быть обнаружена.
Review доказал, что прежние17 тестов пропускают exit42→null; прежний baseline preservation test ловит потерю.

Runtime/decoder/native capture/fallback implementation/source/tool не менять. Scope ровно cell-u34/два roots,
timeout1200/derived3300/phase8100/job180/RSS12GiB/reserve2GiB, все proof flags/oracles/ROLE-MAP прежние.
Допустимы только tests/preflight wiring и необходимые metadata/payload/hash/package updates. Не повторять
полные U/PFC/compiler audits. Missing RESULTS/TIMEOUT остаются UNKNOWN. Никаких local cargo/rustc/Kani/CBMC/
rustfmt/полного runner, CI/rerun/cancel/push/reservation/ledger. Текущий расход8/14, будущий9/14 не разрешён.

## Новый immutable candidate

Старые da8/9f/review ec48 и source/control7c immutable, не amend/overwrite. Новый isolated control предпочтительно
`/root/kani-ch8-s1-08-cell-retry-fix-w13`, sibling над тем же parent9208 с sufficient actual shallow check.
Новый g0 output **только** `kani3300/ch8-s1/s1-08-cell-retry-r1/`: обновлённый воспроизводимый пакет,
exact identities/patches/manifest/VALIDATION, mapping old→new, targeted tests и mutation receipt, HANDOFF.md.
Сохранить base7c и retry-da8 diff maps, чтобы reviewer проверил bounded repair без повторения старого audit.
Пакет фиксирует актуальные pins/tree/hash; payload verify и обязательный workflow preflight PASS.
Reviewer14 сам решит CLOSED/APPROVE по exact committed delta. Review не GO, retry решает координатор
после terminal run и committed intake; timing intake11 не ждём и не меняем.

G0 shared: только свои exact paths; не git add -A/reset/rebase. Commit `[skip ci]`, author
Tiramisu-Cake <igkharin@gmail.com>. Финал: `READY <g0 full SHA> <control full SHA>` и короткий список
tests/mutation, либо реальный STOP с evidence.
