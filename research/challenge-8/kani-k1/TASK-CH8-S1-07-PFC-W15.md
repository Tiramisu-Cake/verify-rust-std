# TASK — w11-B, исполнитель w15: только 22 PFC chains

Это верификация корректности, не security-работа. Отвечай кратко. Runtime: Codex.
Свежая сессия, модель/effort оставить установленными в pane; без вложенной делегации.
Вход g0 `118fd0774a5a7379ca12555daafb3b677e074813`; repo `/root/verify-rust-std-kani3300-g0`.

## Цель и уровень приёмки

Восстановить 22 exact PFC bindings S1-07 run `43923266772` по методу Profiles v4.
Координатор выбирает bounded source-reported уровень Profiles v4 с доверием pinned stock compiler;
не требовать independent AST/MIR/compiler-provenance trace, которого stock 0aac не экспортирует.
Это не caller-only замена PFC: actual target/impl/clauses/check/modifies semantics всё равно связать.
Независимый compiler/B1/B2/general proof credit не присваивать. PFC binding — компонент, не весь admission root.

Входы: `kani3300/ch8-s1/COORDINATOR-REVIEW-AFTER-S1-07.md`, S1-07 `accept/ACCEPT.json`,
`accept/{pfc,native}.py`, exact `evidence/<group>/{properties,export,binding-metadata}.json` по inventory;
`kani3300/ch8-profiles/off-ci-batch/run-43784551069/accept-v4/{BINDING.md,ACCEPTANCE.md}` и его replay.
Std `5be85699b8`, tool `0aac16ef62`, request/control namespace — exact S1-07.

## Работа и проверки

1. Для каждой из 22 rows проверить exact group/harness/crate/request/native manual target-definition link,
   attrs/type/trait/cfg и selected impl по pinned source specialization semantics.
2. Pinned producer resolution: checked_with → modifies_wrapper → AssignsContract.contracted_function_name;
   exact native/export raw symbol → demangled полный function stem двух retained diagnostics.
   Найдены single_top_level_call и no_recursive_call, обе SUCCESS, каждая description содержит exact symbol дважды.
   Перепроверить самостоятельно; не назначать роль closure по номеру и не сравнивать terminal suffix вместо full path.
3. Связать parent check с source requires/ensures/modifies и соответствующими exact property IDs/statuses/clauses.
   Сохранить различие PFC assumed requires, asserted ensures и enforced modifies. Не выдавать diagnostic pair за все
   clauses. Для variants использовать точный предобъявленный patch/hash/effective source, а не production expression.
   Activation mutants должны иметь свой sole expected FAILURE, legal companions — соответствующий SUCCESS.
4. Component replay должен проверять все доступные edges, а не hardcode removal прежнего unconditional gate.
   Сохранить точные evidence/source hashes, demangler identity/dictionary, normalization rules и предел assurance.
   Недоказанное конкретное ребро оставить PENDING с причиной; stock-provenance independent audit не добавлять
   обратно как неявное обязательство этого выбранного уровня.
5. Meaningful synthetic mutations: raw-symbol/decoded-stem/trait/type/impl/cfg/source SHA/site/clause/status,
   variant/patch/oracle/group/harness/native-ref/request mismatch, duplicate/missing diagnostic/property должны
   отклоняться. Положительные и negative-variant cases обязательны; повторный replay воспроизводит компонент.

Write scope: только новый `kani3300/ch8-s1/s1-07/run-43923266772/accept-pfc/`:
PFC.json, PFC.md, replay, tests, VALIDATION.json, HANDOFF.md. Не дублировать artifacts.
Не пересчитывать общий qualified count, не менять historical accept/accept-v2, source/tool/control/policy/ledger.
W11 параллельно пишет только accept-u; w13 пишет s1-08 и isolated candidates. Не ждать их результатов.
Координатор позже интегрирует components; review — отдельная стадия w14 после готовности.

## Продолжение и ограничения

Времени и объёма достаточно. Новое обычное рабочее окно по CORE начинается фактическим стартом этой стадии;
старое окно/простой не наследовать. Завершить replay, 22 chains и tests. Объём работы, оценка «не успеваю»,
контекст/compaction или исправимая ошибка скрипта не являются blocker. STOP — только реальный доказанный
внешний/scope blocker либо фактически достигнутый установленный лимит, с фактом времени/попыток/остатка.
Не заменять выполнимую реализацию stop-marker.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; без full raw logs/archives.
Demangling существующим c++filt допустим. Commit только своих путей, без git add -A/reset/rebase чужих изменений.
Коммит `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Финал `READY <g0>` с результатом 22 chains/tests либо `STOP <реальный blocker>`.
