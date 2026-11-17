# TASK — w14: независимый review cell-only retry1200

PREPARED_NOT_ISSUED: выдать после committed candidate w13; координатор добавит exact g0/control SHA в сообщение.
Это верификация корректности, не security-работа. Отвечай кратко. Свежая Codex-сессия,
текущая pane-модель/effort, без субагентов; bounded delta review, не повторный полный S1 audit.

Вход: `TASK-CH8-S1-08-CELL-RETRY-PREP-W13.md`, будущий committed `kani3300/ch8-s1/s1-08-cell-retry/`,
base reviewed7c41333f9b/source99e/tool0aac, исходный review e14db2d0dd и cell diagnostic929f21bb1f.
Проверять exact выданный commit/trees/hashes и весь delta от7c, а не авторский READY.

- Исполняется ровно cell-u34 с обоими прежними roots; extra/missing/wrong group/selector fail-closed.
  Один job, jobs/max-parallel1, concurrency/cancel policy сохранены. Полный declared manifest не означает
  разрешение исполнить другие группы, даже при пропущенном CLI --groups.
- Только timeout600→1200s и необходимые derived caps/metadata/scheduling/pins/tests; actual Kani argv,
  request validation, parser/receipt expectations и3300s child envelope согласованы, reserve/shutdown сохранены.
  Не потеряны config/timeout/identity gates; bypass validator и изменение timeout лишь в JSON недопустимы.
- Source/tool/solver/flags/unwind/domain/conditions/assumptions/covers/labels/oracles/variants/RSS/checks,
  decoder/native export/snapshots/location policy/admission неизменны. Missing RESULTS/TIMEOUT parser не чинится
  в этом пакете и не превращается в accepted/complete. Resource change не требует нового proof premise.
- Payload/preflight/YAML/actual shallow ancestry согласованы; meaningful targeted mutations и static delta
  checks проверить, без compiler/rustfmt/solver/full runner. Не повторять broad неизменённые U/PFC/source audits.
  Прежние обязательные preflight/error/timeout/partial/snapshot controls не должны исчезнуть из-за single-group
  scheduling; необходимые adaptations должны сохранять проверяемые гарантии, не подменять тесты skipped/PASS.
- 1200s evidence не доказывает fit600s или причинность labels. Retry не автоматически становится частью same-run
  S1-08 acceptance: origin/profile и последующая композиция должны быть явны. No dispatch/reservation сейчас;
  conditional charge9/14 только после нового GO и принятого run, auto-rerun нет.

Output только `kani3300/ch8-s1/s1-08-cell-retry-review/`: REVIEW.json/md, VALIDATION.json, HANDOFF.md,
APPROVE/CHANGES_REQUIRED и exact reviewed pins. Localized finding — original owner через координатора;
author code не исправлять. Review ≠ GO: retry решит координатор после terminal S1-08 и intake.
Без CI/rerun/cancel/push/публикаций/ledger/cargo/rustc/Kani/CBMC; historical artifacts immutable.
Не STOP по объёму/контексту, только реальный blocker. Commit только своих paths, `[skip ci]`,
author Tiramisu-Cake <igkharin@gmail.com>. Финал `READY <g0>` с verdict либо реальный STOP.
