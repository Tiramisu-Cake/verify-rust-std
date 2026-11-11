# KANI3300 G0 — статический дизайн: произвольный union как pointee raw-указателя (поверх части 1)

**Выдано координатором 2026-11-11, GO владельца; рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-3300-SCOPE-ANSWER.md`, п.3–5 — прочитать).**
Только чтение и анализ, без сборок, Cloud $0. Runtime **Codex**, одна стадия.

## Цель

Следующий upstream PR после части 1 закрывает подзадачу kani#3300 «unions can serve as a pointee of raw pointers» для
**произвольных** union с поддерживаемыми полями (не только `MaybeUninit`). Field-of-struct/union и union-in-union — отдельный
этап G2; здесь только зафиксировать, какие интерфейсы G1 должен оставить для него.

## Рабочее место

- Worktree **/root/verify-rust-std-kani3300-g0**, ветка **experiment/kani-k1-kani3300g0-20261111** (от P1G `83dd7f7b38`).
  Писать только `research/challenge-8/kani-k1/kani3300/g0/`.
- Исходники (только чтение, через `git show <sha>:<path>`, без checkout): база — часть 1 **`c39cc1121`** в
  `/root/kani-upstream-3300` (там параллельно идёт P2 — не менять ветку/дерево); Kani main `bf9c58e662` там же; для идей
  про составные layout — CMP2 `b1f0105c03` в `/root/kani-fix-3300-cmp` (research, не upstream-база).
- Существующие union-тесты Kani (`tests/expected/uninit/` и др. в `c39cc1121`) — чтобы не сломать их семантику.

## Что сделать

1. **Карта текущих запретов** в `c39cc1121`: где union за raw pointer / deref + union-field / union как вложенное поле
   отвергаются (файл:строка), где `maybe_uninit_storage` ограничивает новые пути части 1 (return/destination, copy,
   argument buffer), где уже есть `PointeeLayout::Union` и маски полей.
2. **Поддерживаемые формы G1** и явные rejection boundaries: union с полями поддерживаемого layout (скаляры разной ширины,
   padded struct, `ManuallyDrop<T>`, ZST-arm, raw-pointer поле, массивы); что остаётся Unsupported (union-in-union и
   union как поле — до G2; enum с неподдерживаемой схемой; fn-pointer; прочее).
3. **Семантика операций** (инвариант — без ложного SUCCESS): whole-union create/assign/copy/move переносят byte-state;
   запись поля обновляет только байты этого поля, не благословляет весь union; чтение поля требует data-mask поля;
   ZST-поле не инициализирует payload; reset/overwrite поверх старого состояния; padding и хвост; перекрытия полей,
   byte vs typed reads; layout/offsets — только от rustc (repr(C) и Rust repr). Pointer-поле: инициализированный
   указатель ≠ инициализированный pointee — что нужно от points-to/delayed-UB. MaybeUninit↔T transmute-правила части 1 на
   произвольные union **не** распространять.
4. **Точки изменения** (файл:функция в `c39cc1121`) и что из части 1 переиспользуется (shadow, copy_by_id, argument
   buffer, field masks) vs что обобщается (протокол return/destination). Оценка объёма — диапазоном, с оговорками.
5. **Native матрица G1** (текстом, не запускать; ≤ 20 selectors): positive/negative пары written/unwritten,
   narrow-write→wide-read, whole-copy/overwrite/reset, argument/return, padding, ZST-arm, pointer/delayed-UB; регрессии
   части 1 (включая frame-negative) и существующих union-тестов. Для каждой negative — ожидаемая диагностика.
6. **Интерфейсы для G2**: что G1 должен оставить, чтобы field-of-struct/union и union-in-union добавлялись без переделки.

## Результат

`kani3300/g0/DESIGN-UNION-POINTEE.md` (≤ 80 строк: карта, формы, семантика, точки изменения, риски ложного SUCCESS) и
`kani3300/g0/TASK-DRAFT-G1.md` (manifest ≤ 20 selectors, cap — предложением, не окончательно). Коммит `[skip ci]`
(автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force. Маркеры `REVIEW REQUEST <sha>` /
**KANI3300 G0 ЗАВЕРШЁН**, затем стоп.

## Запреты

- Никаких сборок/dispatch/Cloud, локальных cargo/rustc/Kani/CBMC; raw logs/archives/credentials не читать.
- Не трогать другие worktree и клоны Kani (только `git show`/`git grep <sha>`). Никаких Actions/PR/issue/комментариев.
- Без `git stash`. Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
