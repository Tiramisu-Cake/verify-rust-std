# TASK — worker11: S1-07 offline acceptance v2 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.
Runtime: Codex. Отдельная новая сессия; GPT-6 Luna HIGH, без вложенной делегации.
Вход g0 `82695068e4a9f02b3cf59eca01d961bd63442b44`; worktree `/root/verify-rust-std-kani3300-g0`.

## Цель и входы

Новый replayable receipt по уже собранному S1-07 run `43923266772`, без нового proof run.
Прочитать `kani3300/ch8-s1/COORDINATOR-REVIEW-AFTER-S1-07.md`, исходные `s1-07/run-43923266772/accept/`,
`ACCEPTANCE-POLICY-BATCH.md` и механизм `kani3300/ch8-profiles/off-ci-batch/run-43784551069/accept-v4/BINDING.md`.
Std `5be85699b8826e3286c0bf89efb9affefac0acb5`, stock tool `0aac16ef62da9e9d5645782d458593e5d78143ba`.
Исполненный control/request/artifact identities брать из S1-07, не S1-06. Исторические receipts неизменны.

## Работа

1. Для оставшихся 187 UNREACHABLE records проверить и записать source-local аргументы из coordinator review.
   Exact SHA/context/site/function/class/description/status обязательны; не вводить exemption по имени helper или файлу.
   50 abs_diff: larger-minus-smaller; 25 alignment: align>=1 после guard; 12 remainder: rhs!=0;
   18 allocation-size: size!=0; 28 fmt: RHS сдвига равен 1 (overflow проверяет shift count, не старшие биты);
   54 active_post: length guards/CAP=32/loop bounds/counters. Проверить условия на pinned source и producer,
   не принять эти числа как доказательство. Любой mismatch/необоснованный случай оставить PENDING.
   Status UNREACHABLE сохранять; не превращать generated safety check в доказанную sorting postcondition.
2. Для 22 PFC восстановить всю доступную v4-style source-reported цепочку: exact manual harness/target,
   concrete type/trait/specialization/cfg → checked_with/modifies wrapper по pinned producer → exact raw metadata symbol
   → demangled полный function stem → single_top_level_call/no_recursive_call → parent check/source clauses/properties.
   Во всех 22 строках найдены две SUCCESS diagnostics, exact symbol повторён дважды; перепроверить самостоятельно.
   Пара diagnostics не заменяет clause binding. Учесть variant patch: у activation mutants изменённый ensures должен
   соответствовать предобъявленному FAILURE, у legal companions — SUCCESS. Нельзя выбрать impl по terminal-name/suffix
   или назначить closure role по номеру. Demangler допустим, компиляторы — нет.
   Уровень — тот же bounded source-reported admission, что у Profiles v4; не caller-only подмена и не independent
   AST/MIR/compiler-provenance credit. Если обязательное ребро не устанавливается этим методом, оставить точный gate.
3. 111 success-message bindings не снимать по candidate count/ordinal. Закрывать лишь действительно доказанные exact
   role→property связи; прочие остаются PENDING для будущих role labels. Пересчитать named companion dependencies
   и N0..3 unions только после local gates, без переноса результатов из другого run.
4. Сохранить все прежние inventory/identity/snapshots/locations/required SAT covers/negatives/unsupported/checks gates.
   Не менять domain, source/tool, policy или исторические qualification/ledger records.

## Границы, проверки и выход

Write scope: только новый `kani3300/ch8-s1/s1-07/run-43923266772/accept-v2/` в g0.
Старые analyzers/receipts и evidence читать read-only; новые rules/replay/tests держать в новом каталоге.
Не дублировать artifacts. Std/model/core/control исходники не менять: w13 независимо готовит role-label candidate,
включая `sorting_model_controls.rs`; это назначение writer действует только для его стадии.

Выход: `ACCEPTANCE.md`, `ACCEPT.json`, replay, `VALIDATION.json`, `HANDOFF.md` с exact per-row gates и source arguments.
Receipt должен быть полностью воспроизводим, с exact inputs и различием old/new admission без переписывания старого.
Проверки: read-only replay; meaningful synthetic fail-closed mutations для source SHA/site/description/status,
raw-symbol/full-instance/clause/variant/group/harness/request namespace mismatch, missing/duplicate properties и
companion qualification. Исторический PENDING не hardcode как PASS. Review готового кандидата выполнит w14 отдельно;
в HANDOFF отметить READY_FOR_REVIEW, не объявлять независимый review выполненным.

Коммит g0 только своего каталога, `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>.
Shared g0 может продвинуться коммитом w13: не reset/rebase чужих изменений, не `git add -A`, не включать чужие файлы.
Последней строкой `READY <g0>` либо `STOP <точный blocker>`.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC; raw logs/archives целиком не читать/скачивать.
