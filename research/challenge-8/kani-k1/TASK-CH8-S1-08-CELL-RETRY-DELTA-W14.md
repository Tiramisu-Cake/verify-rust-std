# TASK — W14: bounded delta-review W14-CELL-RETRY-01

Это верификация корректности, не security-работа. Отвечай кратко. Продолжение того же reviewer,
текущая pane-модель/effort, без субагентов. Координатор выдаёт только после exact committed r1 READY;
полный g0 package SHA в сообщении выдачи является обязательным входом.

Исторический review `ec48e6d59b552da2a9aa8d985478bf259c950073` immutable:
`kani3300/ch8-s1/s1-08-cell-retry-review/`. Единственный finding W14-CELL-RETRY-01 OPEN.
Old package9f4c37c894e7fecee0f59321ba66b65309a87606 / controlda8c766f957c576eafa44bccfba2c45490cef6d1.
Fix contract `TASK-CH8-S1-08-CELL-RETRY-FIX-W13.md`, task193b377c5cc092f1032741dbb854b0d1f77505d6.
Новый package path `kani3300/ch8-s1/s1-08-cell-retry-r1/`;
candidate control `e27ec119eeac798d43d6bc056a449fa7576a5e94`,
tree `2c4475bf17bb0354e9b204e19c652549c263f90f`, parent9208b373c0a08a265fa0d7493a6529e331065271.
Source99e/tool0aac и base7c прежние; использовать полные pins из immutable input/review.

Проверить exact committed pins/tree/hash/manifest/patch reconstruction и весь bounded delta от da8.
Подтвердить, что изменены лишь tests/preflight integration и необходимые payload metadata/hashes;
runtime/decoder/fallback/source/tool/workflow scope/timeout/derived caps не менялись относительно reviewed retry.
Переиспользовать уже установленный review ec48 для неизменённых гарантий, не повторять broad U/PFC/compiler audit.

Самостоятельно проверить адаптации прежних двух fallback controls: сохранение captured/completed row/compile
receipts и original exit/signal/exception; setup failure/mid-run interruption/terminal context и bounds.
Оба controls реально исполняются exact workflow preflight, не skipped/подменены пустым output. Ниже payload
hash gates воспроизвести различающую in-memory overwrite mutation, которую пропускал old17: captured exit42
не должен теряться незамеченным. Проверить обязательный targeted preflight, пакетные pins и достаточную shallow
ancestry. Не запускать local compiler/verifier/full runner, CI/rerun/push. Лишь Python/static/Git fixtures.

Output **только новый** `kani3300/ch8-s1/s1-08-cell-retry-review-r1/`: REVIEW.json/md, VALIDATION.json,
HANDOFF.md. Exact old/new g0/control/tree/request pins, findings OPEN/CLOSED, APPROVE/CHANGES_REQUIRED;
отдельно перечислить реально повторённые проверки и гарантии, перенесённые из ec48 по byte invariance.
Old review/candidates и intake immutable. Новый finding вернуть исходному author13 через координатора,
author code не чинить. Не STOP по объёму/контексту, только реальный blocker с evidence.

Intake `6d300f3ab9801c808612b562588af06e0f7b4ff9` готов отдельно; здесь его не ревьюировать и acceptance не выдавать.
Review не GO. Retry dispatch решает только координатор после APPROVE и intake. Current8/14,
prospective9/14 не reserved/authorized; без CI/dispatch/rerun/cancel/push/reservation/budget/ledger changes.
1200s не доказывает fit600s, labels causality UNKNOWN, future cross-run composition отдельно.
Shared g0: stage/commit только своих paths, не add -A/reset/rebase. `[skip ci]`, author
Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <full g0 SHA> <verdict> W14-CELL-RETRY-01 <status>`.
