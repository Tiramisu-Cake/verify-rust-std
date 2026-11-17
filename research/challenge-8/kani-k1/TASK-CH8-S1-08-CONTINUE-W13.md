# TASK — w13: завершить S1-08 control package от готового source

Это верификация корректности, не security-работа. Отвечай кратко. Runtime: Codex.
Свежая сессия, модель/effort оставить установленными в pane; без вложенной делегации.
Эта выдача заменяет незавершённое TASK-CH8-S1-08-PACKAGE-W13; его ограничения на source/domain/checks сохраняются,
но не его фиксация модели. Вход g0 `118fd0774a5a7379ca12555daafb3b677e074813`.

## Уже сделано — не начинать заново

Source `/root/verify-rust-std-ch8-s1-08-w13`, commit `99e8456d200fff1299ee5756279cddb23921dc65`,
parent `5be85699b8826e3286c0bf89efb9affefac0acb5`. Два macro-assertion файла уже преобразованы; проверить diff.
Control `/root/kani-ch8-s1-08-w13` сейчас на reviewed S1-07 base `9208b373c0a08a265fa0d7493a6529e331065271`.
Tool остаётся stock `0aac16ef62da9e9d5645782d458593e5d78143ba`.
Предыдущий STOP был неполным выполнением, не архитектурным blocker. Не создавать новый stop-marker по объёму.

## Оставшаяся ограниченная работа

1. Проверить сохранение expressions/evaluation order/ветвей/domain/127 logical obligations в source99e.
   Pinned AssertHook вызывает codegen_assert_assume: проверить это и взаимодействие с post-check covers;
   отрицательные panic-path fixtures/negative oracles и все covers сохранить. Если найдена конкретная ошибка source,
   исправить минимальным новым commit поверх99e; не переписывать историю и не начинать с baseline заново.
2. Подготовить полный ROLE-MAP.json для 127 required success bindings: exact root/role/constant expected description,
   source site/hash и applicability. Новых уникальных меток 111 /21 roots; 16 уже exact bindings/semantic sets
   сохранить без ненужного one-ID требования. Conditional N0/N1 assertions не делать обязательными в ином N.
   Не угадывать будущие property IDs по ordinal, source promises не выдавать за observed CI messages.
3. Доделать control от9208: новые std/source/tree/file/payload/request pins, source-binding anchors,
   required-message manifest, CI-REQUEST.json/md и package tests. Все variant patches/hashes/source-under-test
   согласовать с новым base; негативы не переназначать по фактическому FAILURE. Admission оставить offline.
   Runner/decoder/export semantics, snapshots/location exceptions/native capture/tool/flags/checks/unwind,
   35 roots/14 groups, group order/max-parallel1/caps/preflight/shallow guarantees сохранять.
4. Выполнить малые Python static/synthetic/Git-fixture checks: equivalence исходных условий/ветвей, labels/ROLE-MAP
   coverage/uniqueness, unchanged negatives/covers/oracles, согласованность pins/bindings/variant payloads,
   missing/duplicate/wrong-role/status/harness/source fail-closed. Existing package preflight/YAML/shallow regressions.
   Эти проверки реализовать и выполнить, не ограничиться git diff --check. Компиляцию/rustfmt/verifier не запускать.
5. Компоненты U/PFC не ждать: w11 и w15 разбирают старый S1-07 параллельно и std/control не пишут.
   W13 остаётся единственным writer source smoke/model-controls для этой стадии, без изменения model API,
   sorting_model.rs, runtime algorithms или smallsort.rs attrs. Готовить кандидат, не запускать CI.

## Выход и проверки завершения

G0 `/root/verify-rust-std-kani3300-g0`: только `kani3300/ch8-s1/s1-08/` — source/control identities,
patches, ROLE-MAP.json, CI-REQUEST.json/md, VALIDATION.json, HANDOFF.md с READY_FOR_REVIEW и NOT_RUN compiler/runtime.
Source/control local commits с exact pins; общий completed package обязан существовать, одного source commit мало.
W14 выполнит independent review отдельной стадией после READY, не объявлять его пройденным.

Времени и объёма достаточно. Начать новое обычное рабочее окно по CORE с фактического старта; не наследовать
старый T0 или 15 часов простоя. Продолжать до реализации и проверок, в том числе после compaction.
Объём, контекст, оценка «этот запуск не успевает» и исправимая ошибка не основания STOP. STOP только при реальном
доказанном внешнем/scope blocker либо фактически достигнутом установленном лимите: факт времени, попытки, остаток.

Без push/CI/публикаций/ledger и budget reservation; без локальных cargo/rustc/Kani/CBMC и full raw logs/archives.
Shared g0 не reset/rebase, commit только своего каталога, не git add -A. Соседние accept-u/accept-pfc не менять.
Все commits `[skip ci]`, author Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By.
Финал `READY <g0> <std SHA> <control SHA>` либо `STOP <реальный blocker>`.
