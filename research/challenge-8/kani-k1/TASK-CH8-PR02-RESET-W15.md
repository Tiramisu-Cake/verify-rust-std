# TASK — worker15: PR-02 entry reset for automatic harnesses (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

## Контекст

A1 R2 (run 43772128176) показал: исходный #4854 autoharness на SEL1 даёт
`error: immutable masks: reset is absent from this model`. Статический разбор планера:
[RESET-ABSENT-ANALYSIS.md](kani3300/w0-a1/r2-43772128176/RESET-ABSENT-ANALYSIS.md) (g0 `6cb9fbfed6`).
Вывод: реальный integration-дефект PR-02 — finalizer требует reset в каждой seeded model, а
`UninitPass` вставляет entry reset только для `kanitool::proof`/`proof_for_contract`, не для
`AutomaticHarnessIntrinsic`. Координатор решил: исправление входит в PR-02 (ещё не опубликован)
отдельным новым коммитом поверх текущей головы; это исправление уже существующего стека, а не новый
compiler design (WIP-правило не нарушается).

Identities: PR-02 `932fb8395a58f8c86c0d702ba2cae835823b2962` (fork branch
`fix/kani-3300-init-02-immutable`), C2 final `8e299aa6243bc5f06a29c51e98aafa9564478220`,
SEL1 `14bc57fdb99960240c4944845a3d985c8af4dcf7`, upstream `0aac16ef62da9e9d5645782d458593e5d78143ba`.
Объекты есть в локальных клонах `/root/kani-fix-3300-c2-s5`, `/root/kani-fix-3300-sel1-c2-w15`.

## Что сделать

1. Новый worktree `/root/kani-fix-ch8-pr02-reset-w15` от `932fb8395a`, ветка `work/ch8-pr02-reset-w15`.
2. Узкий патч по рекомендации планера: `is_harness` в `ptr_uninit/mod.rs` дополнительно распознаёт
   ровно `KaniFunction::Intrinsic(KaniIntrinsic::AutomaticHarness)` (через существующий `try_from`),
   сохраняя обе attribute-ветви и fail-closed finalizer. Reset ровно один, первым действием wrapper,
   до argument generation/contract setup, только при Uninit ON. Не ставить reset в target/callee,
   не убирать fatal, не materialize reset без вызова. Если рекомендуемый путь не подходит
   (например, wrapper body/early returns), остановись и опиши причину, не придумывай другой design.
3. Регрессии в обычном стиле upstream tests этого среза (expected-файлы):
   - PR-02-native различающий repro без MU/storage: zero-arg autoharness target, возвращающий
     typed immutable byte-array reference (вариант `fn seed_only() -> &'static [u8; 4]`);
   - autoharness с аргументом + immutable seed; autoharness без seed; autoharness с контрактом;
   - autoharness uninitialized-read negative + initialized companion (hole ловится, witness nondet);
   - Uninit OFF: reset не вставляется, поведение прежнее.
   Fixtures, которые требуют поведения голов 3–7, сюда не класть.
4. Проверить, что тот же патч применяется к C2 final и SEL1 без конфликтов (git apply --check; не
   переписывать стек, ничего не rebase-ить). Записать diff-контекст, если отличается.
5. CI-only пакет (как прежние C2/SEL1 Quick, тот же checklist: push trigger на
   `uninit-ci/ch8-pr02-reset-*`; `runner.*` только в step env; fetch-depth ≥2; sibling control/export;
   нормализация путей Kani от cwd; static YAML check; stock push workflows исключены negative filter
   или удалены в CI-only коммите). Одна matrix-run = 1 dispatch:
   - arm A: PR-02+fix — fmt, build, clippy -D warnings, compiler unit tests среза, новые регрессии,
     затронутые suites (uninit/immutable/function-contracts/autoharness) + те же regressions на
     старом `932fb8395a` для matched old/new пары (на старом ожидается fatal);
   - arm B: SEL1+fix — точный исходный #4854 autoharness fixture и explicit companion из A1.
   Caps по образцу SEL1 Quick (≤120 мин/arm, jobs ограничены). Коммиты `[skip ci]`, trigger
   создаёт координатор (same-tree non-skip child). Записать CI-REQUEST с SHA/tree/patch SHA256.
6. Независимое review патча и пакета (обычный reviewer этой среды), findings исправить.
7. Итог: `kani3300/ch8-pr02-reset/` в g0 — PATCH.md (что и почему), CI-REQUEST, REVIEW, HANDOFF;
   коммит `[skip ci]`, author `Tiramisu-Cake <igkharin@gmail.com>` в команде, без смены global config.
   Последней строкой ответа: `READY <ci-package-sha> <g0-sha>` или `STOP <причина>`.

## Ограничения

Без push, CI, публикаций, правок PR-текстов и ledger. Без локальных cargo/rustc/Kani/CBMC
(компиляция проверяется в CI). Без force/rebase существующих веток. Полные raw logs не читать.
Тексты PR-02 обновит координатор после CI.
