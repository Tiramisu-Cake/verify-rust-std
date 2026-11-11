# KANI3300 A3 — протокол парности argument/return и модель in-place `Call(Move)` (аудит §2.4, §2.6)

**Выдано координатором 2026-11-12.** Основание: `AUDIT-REPORT-KANI3300-RU.md` §2.4 и §2.6, ответ планера
`kani3300/audit/PLANNER-AUDIT-RESPONSE.md` (W1-A3) — прочитать. Эталон Miri (ниже) — из `/root/verify-rust-std-kani3300-t0/
research/challenge-8/kani-k1/kani3300/b2/` (probes, EXPECTATIONS.md). Runtime **Codex**, одна стадия, **Cloud $0**;
исполнение — узкий fork CI координатора.

## Эталон Miri (nightly-2026-10-23, probe CI runs 43109689395 / 43109978880 / 43111757334)

- Чтение байт источника через raw ptr, взятый до move, — **OK (инициализировано)**: assignment `Move`, field/projection
  move, `mem::forget`/`intrinsics::forget`, обычный by-value вызов (MIR передаёт **временную** копию: `_8 = move _3;
  consume(move _8)`), union/MaybeUninit варианты.
- **custom MIR `Call(consume(Move(src)))` с тем же address-taken `src`** (callee читает или пишет параметр): после вызова
  чтение через `p` — **UB: memory is uninitialized** (и без Stacked Borrows). С `Copy(src)` — OK.
- Вывод: деинициализация источника нужна **только** для in-place `Call` с `Operand::Move(place)` этого места; blanket reset
  всех `Move` — неверно.

## Что сделать (Kani: /root/kani-fix-3300-a1, ветка fix/kani-3300-a1 поверх A2R `b207847932`)

1. **Парность caller/callee (§2.4):** общий предикат «у этого вызова есть парный transfer-протокол» для caller
   (StoreArgument) и callee (LoadArgument); ранний Unsupported для формы без протокола (bodyful non-`Item`, shim и т.п.),
   вместо fallback «initialized». Отличать «аргумент не выбран witness'ом в этом вызове» от «протокола нет». Обязательная
   запись normal return (index 0); не оставлять состояние между вызовами.
2. **In-place `Call(Move)` (§2.6):** для `Call` с аргументом `Operand::Move(place)` shadow-tracked storage — сначала передать
   witness state в callee, затем деинициализировать shadow источника `place`. Assignment/field Move, forget, temp-moves —
   без изменений. Отметить, при каких MIR (opt-level Kani) такой вызов реально возникает.
3. Тесты: несколько shadow-аргументов, вложенные и повторные вызовы с тем же размером payload, bodyless/shim путь →
   Unsupported; in-place Move (custom MIR, `--edition 2021`, `#![feature(custom_mir, core_intrinsics)]`) → чтение после
   вызова = uninit FAILURE; Copy-вариант → SUCCESS; обычный by-value вызов через temp → SUCCESS.
4. rustfmt `--config-path rustfmt.toml`, diff --check, clippy/`-D warnings` source audit, независимое ревью.

## Результат

`kani3300/a3/NOTES.md` (≤ 30 строк) + `RESULT-KANI3300-A3.md` (≤ 15 строк), research-коммит `[skip ci]`, push без force.
Последней строкой `A3 READY <sha Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC/Miri; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
