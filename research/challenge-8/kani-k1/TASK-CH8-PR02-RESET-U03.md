# TASK — U-03: две фикстуры uninit read + matched old controls (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

## Итог U-02 (run 43780092728, trigger `235b30ffb8`, pkg `952ea771be`; artifact bounded)

PR-02 `932fb8395a` + fix (patch sha256 `d43f251e…e0cd`): old-build, fmt, build, clippy, compiler units 66/66,
compiletest-build, expected uninit 56 passed/2 ignored, expected function-contract 134 passed/4 ignored — все exit 0.
`script-based-pre autoharness_entry_reset_*`: **5 passed, 2 failed**. Падают
`autoharness_entry_reset_initialized_read` и `autoharness_entry_reset_uninit_read`: единственный failed check —
`Interaction between raw pointers and unions is not yet supported` (main.rs:14, `initialized_read`),
т. е. дефект **фикстур** (чтение через raw pointer к union/MaybeUninit), а не исправления.
После этого runner не выполнил `script-based-pre-autoharness` и `old-controls` (NOT_RUN).

## Что сделать

1. Переписать две фикстуры без union/MaybeUninit: uninit-negative через чтение байта padding структуры
   (`#[repr(C)] struct { a: u8, b: u32 }` → `*const u8` на offset 1) в autoharness target; initialized
   companion — то же чтение инициализированного байта. Ожидаемые: negative = FAILURE с uninit
   safety_check description; companion = SUCCESS. Остальные 5 фикстур не менять.
2. Runner: все gates выполняются независимо (no fail-fast между gates), `old-controls` и
   `script-based-pre-autoharness` всегда запускаются после успешной сборки; итог = агрегат.
3. Новый source commit поверх `932fb8395a` (compiler diff идентичен U-01/U-02, подтвердить sha256),
   новый CI pkg (arm A only). Review. g0 `kani3300/ch8-pr02-reset/u03/` + RESULT-U02.md с фактами выше.
   Последней строкой `READY <ci-pkg> <g0>` или `STOP <причина>`.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
