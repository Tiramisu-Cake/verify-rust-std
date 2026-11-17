# TASK — w13: подготовить cell-u34 retry1200, без dispatch

Это верификация корректности, не security-работа. Отвечай кратко. Свежая Codex-сессия;
текущая pane-модель/effort, без субагентов. Одна компактная подготовительная стадия.
Вход g0 `929f21bb1ff386d5ad1a132795e5299c68e5d4e5`; reviewed control7c41333f9bfcfd7eb4e0ede7bd316443090c9025,
std99e8456d200fff1299ee5756279cddb23921dc65 и stock tool0aac16ef62da9e9d5645782d458593e5d78143ba неизменны.
Exact base package/pins — `kani3300/ch8-s1/s1-08-r1/`; diagnosis — `s1-08/run-44095954742/cell-diagnostic/`.
Owner разрешил только preparation/review; retry решит координатор **после terminal run и intake**.

## Контракт изменения

1. Новый изолированный control `/root/kani-ch8-s1-08-cell-retry-w13`, не менять7c/source99e или старые пакеты.
   Выполнять **только cell-u34**, ровно два прежних selectors stable_default_cell и unstable_default_cell,
   production/PFC/Cell<u8>/symbolicN0..3/unwind34. Ни один другой group/root не запускать.
   Полный baseline manifest/ROLE-MAP можно сохранить как source reference, но declared и executed scope различать;
   target selection должна fail-closed запрещать запуск остальных групп. Один job/run, jobs/max-parallel1,
   тот же fork concurrency, cancel-in-progress=false. Никаких изменений текущего run44095954742.
2. **Единственный proof-runtime delta: per-harness timeout обоих cell roots600→1200s** и необходимые derived
   group/request/cap/validation values. Compile900s и group RSS12GiB/headroom2GiB прежние. Базовый group child
   envelope900+2×1200=3300s; оставить cleanup/reserve и подходящие phase/job caps, не урезать proof time ради окна.
   Не менять resource limits других roots, если сохраняется полный manifest. Если прежние phase8100/job180min
   уже достаточны, не увеличивать их без причины. Отдельно расписать setup/group/phase/job/reserve envelope.
3. Синхронизировать actual `--harness-timeout 1200s`, request rows, parse_export expected timeout и receipts;
   не просто поменять число в manifest при прежнем argv600s. Строгое validation согласовать узко с этим profile,
   не удалять timeout/config/mode/inventory/source gates. Не делать общий compiler/runner refactor.
   Допустимы только scheduling cell-only, timeout/derived-cap changes, необходимые pins/metadata/preflight/tests.
   Source/tool/conditions/assumptions/types/geometry/solver/checks/flags/unwind/covers/messages/oracles/variants,
   raw export/decoder/native capture/snapshots/location exceptions/admission — как7c, с точным semantic diff map.
   **Не чинить missing RESULTS parser и не переводить TIMEOUT в SUCCESS/complete** в этом пакете.
4. Предпочтительно новый sibling над тем же parent9208 для сохранения reviewed ancestry/depth5; old7c не amend.
   Если выбран иной graph, вычислить достаточный shallow depth и проверить actual Git fixture; не допустить
   старую ошибку fetch-depth. Existing preflight сохранить, adaptations только для narrowly frozen retry profile.
5. Compact tests: exact selected pair/group и reject extra/missing/wrong selector; actual argv1200,
   request/parser/receipt agreement, wrong600/invalid timeout rejection,3300s+cleanup fit, invariance baseline
   proof files/ROLE-MAP/oracles/flags/RSS/snapshots/decoder, meaningful error/partial/TIMEOUT fail-closed cases,
   pins/payload/YAML/shallow. Переиспользовать существующие tests; не повторять broad unchanged suites без причины.
   Никаких local cargo/rustc/Kani/CBMC/rustfmt/actual full runner или solver experiments.

## Выход и handoff

G0 только `kani3300/ch8-s1/s1-08-cell-retry/`: CI-REQUEST.json/md, exact identities/source-control trees/payload
hashes, patch от7c с whitelist/diff map, VALIDATION.json, HANDOFF.md READY_FOR_W14_REVIEW.
Объяснить, что два доказательства1200s не устанавливают fit600s или обычный organizer cost budget, не доказывают
влияние labels; смешивать результаты двух run как same-run нельзя. Future composition/admission отдельно у координатора.
Плановый charge после нового разрешённого accepted run: item2 **9/14** (сейчас8/14); сейчас NOT_RESERVED/NOT_RUN,
auto-rerun нет, source уже опубликован и его не менять/не republish. Не считать старую incomplete группу принятой.
После READY координатор выдаст w14 независимый review; автор не объявляет его выполненным.

Времени/объёма достаточно; не STOP из-за контекста/«не успеваю». Реальный scope blocker описать точно,
не ослаблять gates ради удобства. Без dispatch/rerun/cancel/push/публикаций/ledger/reservation.
Только собственные paths, не git add -A/reset/rebase чужих изменений; commits `[skip ci]`,
author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <g0> <control SHA>` либо реальный STOP.
