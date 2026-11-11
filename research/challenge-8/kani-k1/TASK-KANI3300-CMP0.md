# KANI3300 CMP0 — статический дизайн compound storage (`IntoIter` / `PolymorphicIter` / `ManuallyDrop`) для U8/U9

**Выдано координатором 2026-11-11, ночной GO владельца; рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-AFTER-U3-ANSWER.md`, п.3–5; также
`PLANNER-U3-ANSWER.md` п.1 там же).** Только чтение и анализ, без сборок, Cloud $0. Runtime **Codex**, одна стадия.

## Рабочее место

- Worktree **/root/verify-rust-std-kani3300-cmp**, ветка **experiment/kani-k1-kani3300cmp-20261111** (от U3 `538e907ad6`).
  Писать только `research/challenge-8/kani-k1/kani3300/cmp0/`.
- Исходники (только чтение): эталон `/root/kani-src-f046b70644`; кандидат v2 — **immutable** `81dd85b` в
  `/root/kani-fix-3300-v2` (параллельно идёт U3B в tmux 15 — **не checkout/commit/не менять**, читать через
  `git -C /root/kani-fix-3300-v2 show 81dd85b:<path>`); core — `library/core/src/array/iter.rs`, `array/iter/iter_inner.rs`
  (или где лежат `InnerSized`/`PolymorphicIter`), `mem/manually_drop.rs` этого worktree.
- Контекст: U3 RESULT (`kani3300/u3/RESULT-KANI3300-U3.md`; IntoIter → Unsupported `PolymorphicIter<[MaybeUninit<usize>;2]>`
  field), U2 RESULT (`/root/verify-rust-std-kani3300-u2` → `kani3300/u2/RESULT-KANI3300-U2.md`; U8/U9 blocker @ array/iter.rs:77,
  вызов из smallsort.rs:267 `for offset in [0, len_div_2]`), SEL0 (`/root/verify-rust-std-kani3300-sel`, `kani3300/sel0/`).

## Что сделать

1. Проследить полный путь `IntoIterator::into_iter([usize; 2])` и последующих `next()` до drop в core этого дерева:
   какие типы-контейнеры (struct с полем `[MaybeUninit<T>; N]`, `ManuallyDrop`, `Range`/`alive`), какие MIR-операции над ними
   (aggregate creation, move/copy целого контейнера, field projection, argument/return, drop), где v2 сейчас выдаёт Unsupported
   (файл:строка в `81dd85b`).
2. Ограниченный product-layout: обычные поля + поля с `MaybeUninit`-storage (включая массив), реально используемые этим путём.
   Маски и offsets при aggregate creation, move/copy, field projection и argument/return. **Инвариант:** полная инициализация
   ordinary fields не должна благословлять соседнее storage; перенос — по байтам с правильными offsets; padding — false.
   Произвольные union/enum, вложенные union — вне scope (явный Unsupported).
3. Переиспользовать интерфейс v2 (плоский ghost-state, `copy_by_id`, argument buffer); без Option/enum в ghost-state, второго
   static, изменений SKIPPED_ITEMS. Отметить пересечения с SEL0 в `uninit_visitor.rs` (общий владелец production-изменений —
   последовательно, не параллельно).
4. Тестовые гипотезы (как текст, не запускать): полный `into_iter([usize;2])` + `next()` ×2 — positive; positive/negative на
   сохранение заполненных и пустых полей контейнера (пустое storage рядом с заполненным полем → чтение даёт uninit-отказ);
   move контейнера через вызов/return; критерии последующего core replay U8 (нормальный возврат, прежние проверки) и U9
   (успешное чтение scratch[3], единственный uninit-отказ на scratch[4]).

## Результат

`kani3300/cmp0/DESIGN-COMPOUND.md` (≤ 60 строк: путь, точки изменения файл:строка, инвариант, риски ложного SUCCESS) и
`kani3300/cmp0/TASK-DRAFT-CMP1.md` (native manifest ≤ 20 selectors; резерв не считать окончательно). Коммит `[skip ci]`
(автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force. Маркеры `REVIEW REQUEST <sha>` /
**KANI3300 CMP0 ЗАВЕРШЁН**, затем стоп.

## Запреты

- Никаких сборок/dispatch/Cloud, локальных cargo/rustc/Kani/CBMC; raw logs/archives/credentials не читать.
- Не трогать другие worktree и клоны Kani (только `git show`). Никаких Actions/PR/issue/комментариев.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа. Отвечай кратко.
