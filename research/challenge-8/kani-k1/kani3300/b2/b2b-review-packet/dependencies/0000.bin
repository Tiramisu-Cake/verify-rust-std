# KANI3300 B2b — in-place `Call(Move)` probe на custom MIR (дополнение к B2)

**Выдано координатором 2026-11-12.** Основание: `kani3300/b2/` (probes, EXPECTATIONS.md) и CI-результат ниже.
Runtime **Codex**, одна стадия, **Cloud $0**; исполнение (MIR + Miri на nightly-2026-10-23) — CI координатора.

## Факт: probe CI (Tiramisu-Cake/kani, ветка `probe-ci/b2-moved-from`, runs 43109689395 и 43109978880)

- Miri: чтение байтов moved-from источника через raw pointer, взятый до move, — **OK (не UB)** во всех 22 формах:
  assignment Move, Call(Move) вкл. `call_move_address_taken`, field/projection move, `mem::forget`/`intrinsics::forget`,
  union/MaybeUninit варианты, восстановленные десять G1 cases. Контроль `maybe_uninit_uninit_control` → UB uninit ✓.
- `*_reinit`: ERROR только под Stacked Borrows (указатель инвалидирован записью); без SB — OK. Это дефект пробы.
- **Ограничение:** MIR `call_move_address_taken::main`: `_3 = Word(move _4); _6 = &raw const _3; … _8 = move _3;
  _7 = consume(move _8)` — в вызов передаётся **временная** `_8`, а не наблюдаемый `_3`. In-place `Call(Move)` с
  address-taken источником этими пробами **не проверен**.

## Что сделать

1. Новые бинари в `kani3300/b2/probes/src/bin/` на **custom MIR** (`#![feature(custom_mir, core_intrinsics)]`,
   `use std::intrinsics::mir::*;`, `#[custom_mir(dialect = "runtime", phase = "optimized")]`): локал `src` инициализирован,
   `p = &raw const src`, затем `Call(_ = consume(Move(src)), ReturnTo(..), UnwindContinue())` с **тем же** `src`, после
   возврата прочитать байт через `p`. Варианты: (a) callee только читает параметр; (b) callee пишет в параметр (видна ли
   запись в источнике); (c) контроль — то же с `Copy(src)`; (d) контроль — `Move(src)` без взятия адреса не требуется.
   Использовать только формы custom MIR, документированные в `core::intrinsics::mir` на этом nightly (сверить по исходнику
   `library/core/src/intrinsics/mir.rs` пина `7189d39d9ce936881b8132c6addeaf3e295cd455`).
2. Обновить `EXPECTATIONS.md`: что ожидаем от Miri для in-place Move (деинициализация источника / UB при чтении / OK) с
   обоснованием по Miri-исходнику пина (`compiler/rustc_const_eval/src/interpret/…` — обработка `Operand::Move` аргументов
   вызова), ссылкой на файл:строку.
3. Независимое ревью проб (тот же объект, нет посторонних UB, синтаксис custom MIR по исходнику).

## Результат

Research-коммит `[skip ci]`, push без force; `kani3300/b2/RESULT-KANI3300-B2B.md` (≤ 10 строк). Последней строкой
`B2B PROBES READY <research sha>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC/Miri; Python можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
