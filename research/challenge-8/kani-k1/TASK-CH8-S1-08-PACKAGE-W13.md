# TASK — worker13: S1-08 role-label package (одна стадия, без dispatch)

Это верификация корректности, не security-работа. Отвечай кратко.
Runtime: Codex. Отдельная новая сессия; GPT-6 Luna HIGH, без вложенной делегации.
Вход g0 `82695068e4a9f02b3cf59eca01d961bd63442b44`; g0 worktree `/root/verify-rust-std-kani3300-g0`.

## Цель и входы

Подготовить локальный source/control-кандидат, который различает обязательные successful assertions по exact role label
в stock Kani. Это исправление наблюдаемости; не новый compiler, не новая proof-модель и не запуск S1-08.
Входы: `kani3300/ch8-s1/COORDINATOR-REVIEW-AFTER-S1-07.md`, S1-07 `HANDOFF.md`, `CI-REQUEST.json`,
run `43923266772` intake и `accept/POLICY-OPTIONS.md` (раздел success messages), pinned hook/codegen source.
Std base `5be85699b8826e3286c0bf89efb9affefac0acb5`; tool неизменен `0aac16ef62da9e9d5645782d458593e5d78143ba`.
Control base — reviewed S1-07 `9208b373c0a08a265fa0d7493a6529e331065271`; executed sibling `b37f6f75c5...`
имеет тот же candidate tree — сверить identities, не подставлять старые request hashes.

## Назначение writer и scope

Координатор на эту стадию назначает w13 единственным writer двух proof-harness файлов:
`library/core/src/slice/sort/shared/smallsort/verify/sorting_entry_smoke.rs` и `sorting_model_controls.rs`.
Это включает positive! diagnostics, обычно принадлежащие w11; w11 в параллельной стадии меняет только offline receipt
и std не пишет. Model API/implementation `sorting_model.rs`, runtime algorithms, smallsort.rs и его attrs не менять.
Согласование labels оформлять общим manifest/интерфейсом в своём пакете, без ожидания сообщений между агентами.

## Работа

1. Создать отдельный source worktree `/root/verify-rust-std-ch8-s1-08-w13` от exact std base; не менять S1-07 source tree.
   В положительных smoke!, smoke_exact_n!, positive! заменить неоднозначные macro assert! diagnostics на
   `kani::assert(cond, <константный root::role literal>)`, используя pinned AssertHook semantics.
   Сохранить все проверяемые выражения, число логических obligations, evaluation order, assumptions, types/comparator,
   N/geometry, условные ветки и все прежние covers. Проверить извлекаемость concat!/stringify! по pinned producer;
   не обещать observed messages до реального CI. Одна лишь уникальная строка assert! проблему placeholder не решает.
   Преобразование ограничить положительными checks; negative fixtures и panic-path control flow/oracles не менять.
   Условные N0/N1 assertions не делать безусловными и не требовать их SUCCESS в неприменимом N.
2. Проверить разницу assert!/kani::assert для abort/failure paths и post-check cover reachability. Нельзя добавлять
   assume, убирать failed assertion, менять relation/frame/model или сужать domain ради меток. Если сохранение
   гарантии требует нового архитектурного решения — STOP с точной альтернативой, не изобретать новый tool/model.
3. Подготовить `/root/kani-ch8-s1-08-w13` control от reviewed S1-07 base: только новые source/request/payload pins,
   bindings/anchors, required-message manifest и необходимые package tests. Export/decoder/runner semantics,
   binary-after finalization/location exceptions/native capture/negative oracles/checks/flags/caps не менять.
   Сохранить 35 roots /14 groups, порядок/max-parallel1, existing preflight, безопасный shallow depth и budgets.
   Freeze exact root→role→expected description mapping; source hash, request и variant payload identities согласовать.
   Требовать unique exact label ID/SUCCESS для каждой применимой обязательной роли в будущем evidence;
   отсутствующий/дублированный/mismatched label даёт UNKNOWN. Новых known property IDs не угадывать.
4. Малые Python synthetic/static/Git-fixture checks: все исходные assertion expressions и ветвления сохранены;
   manifest различает все 127 obligations (нынешних unresolved 111 /21 roots); новые root::role labels уникальны;
   прежние 16 доказанных bindings, включая exact semantic sets, сохранить без требования нового one-ID mapping;
   unchanged assertions/negatives/covers/oracles сохранены; pins/source bindings/variant patches/manifest взаимно согласованы;
   missing/duplicate/wrong-role/status/harness/source messages fail-closed; существующий package preflight/YAML/shallow.
   Не запускать cargo/rustc/Kani/CBMC, rustfmt или verifier; любые неисполненные compiler/runtime checks отметить NOT_RUN.

## Выход и передача

G0 write scope: только новый `kani3300/ch8-s1/s1-08/` — source/control identities, patches, ROLE-MAP.json,
CI-REQUEST.json/md, VALIDATION.json и HANDOFF.md с точным diff scope/remaining risks и READY_FOR_REVIEW.
ROLE-MAP содержит все 127 обязательных связей; исправлять только неоднозначные sites, не переписывать остальные без нужды.
Admission остаётся офлайн w11: runner только собирает evidence. Не переносить role-classifier внутрь runner.
S1-07 artifacts/receipts/accept-v2 и чужие task/ledger файлы не менять. W11 offline-v2 не ждать для подготовки;
его новый receipt позже определит остаток gates перед dispatch. W14 выполнит independent review готового candidate
в отдельной стадии; не назначать subagent-review и не объявлять review/CI выполненными.

Source/control commits локальные, author Tiramisu-Cake <igkharin@gmail.com>; без Co-Authored-By.
G0 commit только своего каталога, `[skip ci]`; source/control тоже `[skip ci]` до coordinator publication decision.
Shared g0 может продвинуться коммитом w11: не reset/rebase чужих изменений, не `git add -A`, не включать чужие файлы.
Последней строкой `READY <g0> <std SHA> <control SHA>` либо `STOP <точный blocker>`.
Без push/CI/публикаций/ledger и нового budget reservation; без raw logs/archives целиком.
