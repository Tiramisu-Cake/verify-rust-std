# KANI3300 B1R — repair B1 после узкого fork CI

**Выдано координатором 2026-11-12.** `TASK-KANI3300-B1.md` в силе. Runtime **Codex**, одна стадия, **Cloud $0**.

## Факт: узкий fork CI `Uninit Quick`, ветка `uninit-ci/b1-resolver` (B1 `835cb4a09c` на upstream `bf9c58e662`), run 43104793815

Format, build, clippy `-D warnings` — PASS. Тесты:
1. **Регрессия существующих тестов** `kani/Uninit/vec-read-init.rs` (ждёт SUCCESS) и `expected/quantifier-capture/uninit.rs`:
   новая проверка `Failed Checks: Kani does not support memory initialization checks across calls to Shim instances.`
   B1 стал отклонять вызовы `InstanceKind::Shim` (drop glue, closure/FnOnce shims и т.п.), которые base обрабатывал
   (ветка `_ => {}` для non-Item/non-Intrinsic). Это слишком широко.
2. **Шесть новых тестов** `expected/uninit/unresolved-calls/{pending-ops,entry-partial,entry-initialized}-{plain,seeded}.rs`
   не компилируются: `error[E0433]: cannot find core in the crate root` (`use core::intrinsics::mir::*;`) и
   `cannot find macro mir` — нет `// compile-flags: --edition 2021` (edition 2015 по умолчанию). Ни один не дошёл до проверки.

## Что сделать

1. Shim: вернуть поведение base для shim-инстансов с MIR-телом (обрабатывать как обычный bodyful callee / как в base);
   явный Unsupported — только для действительно неразрешимых/bodyless форм, где shadow может теряться. Обосновать по коду,
   какие `InstanceKind` встречаются (Shim, Virtual, Intrinsic, Item) и что делает каждый путь. Регрессионные golden не менять.
2. Тесты: добавить `--edition 2021` (или `std::intrinsics::mir`), проверить feature-атрибуты custom MIR
   (`#![feature(custom_mir, core_intrinsics)]`) и что каждый тест действительно доходит до заявленной проверки.
3. rustfmt-обёртка `--config-path rustfmt.toml`, `git diff --check`, независимое ревью дельты.

## Результат

Коммиты в `/root/kani-fix-3300-b1` поверх `835cb4a09c` (не пушить). `kani3300/b1r/RESULT-KANI3300-B1R.md` (≤ 15 строк),
research-коммит `[skip ci]`, push без force. Последней строкой `B1R READY <sha Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
