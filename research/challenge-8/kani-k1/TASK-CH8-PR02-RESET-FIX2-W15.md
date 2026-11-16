# TASK — worker15: U-01 итог и пакет U-02 (одна стадия; после A1-R1 triage)

Это верификация корректности, не security-работа. Отвечай кратко.

## Итог U-01 (run 43777434715, trigger `e4bf2df0ca`, pkg `b4edbb18bc`)

- **Arm B — SUCCESS.** SEL1 `14bc57fdb9` + fix: исходный #4854 autoharness `reassemble_ptr_fragments_in_static`
  — COMPLETED SUCCESS, 154 properties, 0 failed (раньше fatal `reset is absent`); explicit companion
  `explicit_proof_observes_initialized_null` — SUCCESS 156/0. Artifact `ch8-pr02-reset-b-43777434715-1`
  (id 14187497167), export SHA256 `ed9b4c86…a7e8` / `11933e0e…eca3`.
- **Arm A — FAILURE (packaging), без artifact** (в arm A нет upload-шага). По bounded grep job-лога:
  build PR-02+fix и старого PR-02 — OK; compiler units 66/66; suites 56 passed/2 ignored и
  134 passed/4 ignored, 0 failed; затем compiletest:
  `error: couldn't find config.yml file for exec test in .../tests/script-based-pre/autoharness_entry_reset`
  → exit 101. Вложенные каталоги `autoharness_entry_reset/<case>/` в script-based-pre не поддерживаются:
  каждый тест — отдельный каталог верхнего уровня с config.yml/run.sh/expected.
  Новые регрессии и matched old PR-02 controls — NOT_RUN.

## Что сделать

1. Разложить 7 fixtures в каталоги верхнего уровня (`tests/script-based-pre/autoharness_entry_reset_<case>/`),
   содержимое/expected без изменений, если не требуется иное; новый source commit поверх `932fb8395a`
   (замена прежнего `f695f653ef` — без force/rebase опубликованных веток; это локальная work-ветка).
2. CI пакет U-02: arm A с upload bounded результатов (как в B) при любом исходе; arm B можно
   **не повторять** (уже SUCCESS на том же source patch, если код патча не меняется — подтвердить
   идентичность diff в `kani-compiler/`). Остальное — как в U-01. Review.
3. g0 `kani3300/ch8-pr02-reset/u02/`: CI-REQUEST, REVIEW, HANDOFF + RESULT-U01.md с фактами выше.
   Последней строкой `READY <ci-pkg> <g0>` или `STOP <причина>`.

## Ограничения

Без push/CI/публикаций/ledger. Без локальных cargo/rustc/Kani/CBMC. Raw logs целиком не читать.
