# KANI3300 SEL0 — статический дизайн поддержки `select_unpredictable` в uninit-checks (без сборок)

**Выдано координатором 2026-11-11, ночной GO владельца; выбор и рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-NEXT-PANE14-B-ANSWER.md` и п.3
`PLANNER-U3-ANSWER.md` там же — прочитать оба).** Только чтение и анализ, Cloud $0. Runtime **Codex**, одна стадия.

## Рабочее место

- Worktree **/root/verify-rust-std-kani3300-sel**, ветка **experiment/kani-k1-kani3300sel-20261111** (от U3 `25f4fa0cb8`).
  Писать только `research/challenge-8/kani-k1/kani3300/sel0/`.
- Исходники (только чтение): эталон `/root/kani-src-f046b70644`; текущий v2 — `/root/kani-fix-3300-v2` (идёт repair U3 в
  tmux 15: **не менять, не checkout, не commit** — читать через `git -C /root/kani-fix-3300-v2 show <sha>:<path>`; зафиксировать
  SHA, на котором читал, сейчас `81dd85b`). Core: `library/core/src/hint.rs` в этом worktree.
- Контекст U7: U2 RESULT `/root/verify-rust-std-kani3300-u2` → `kani3300/u2/RESULT-KANI3300-U2.md` (U7: intrinsic
  `select_unpredictable` Unimplemented @ hint.rs:871 + assignable-отказы, которые чинит v2).

## Что сделать

1. Путь `hint::select_unpredictable` → intrinsic → backend (codegen), включая возвращаемые указатели; где
   `Intrinsic::from_instance` даёт Unimplemented; как points-to (delayed-UB) пропускает эффекты; где uninit visitor
   вставляет Unsupported. Объяснить, почему простое снятие guard без alias-переноса даёт ложный SUCCESS (пример).
2. Scope 1: scalar и raw-data-pointer значения. Runtime — выбор одного значения; статически — консервативное объединение
   aliases обоих arms. Выбор pointer сохраняет состояние pointee. `MaybeUninit`/частично заполненный storage-result — отдельный
   перенос shadow выбранного arm; до поддержки — явный Unsupported.
3. Все потребители распознавания intrinsic: points-to, initial-target/delayed-UB, ptr-uninit, codegen, соседние validity
   проверки — где нужна новая ветвь, где семантика уже корректна. Изменения ограничить этим оператором.
4. Переиспользовать интерфейс ghost-state v2 (плоские поля в `MEM_INIT_STATE`); **никаких** новых Option/enum в
   ghost-state, второго static, изменений SKIPPED_ITEMS.
5. Тестовая постановка: обе ветки значения; выбор initialized/uninitialized pointee; delayed read после записи через
   выбранный alias; реальный `hint::select_unpredictable`-wrapper; PFC swap-контроль с узким `modifies` (нет assigns-отказов
   instrumentation). Каждое positive/negative ожидание обосновать по исходнику.

## Результат

`kani3300/sel0/DESIGN-SELECT.md` (≤ 60 строк: точки изменения файл:строка, инвариант aliases/shadow, риски ложного
SUCCESS) и `kani3300/sel0/TASK-DRAFT-SEL1.md` (черновик следующей стадии: native manifest ≤ 20 selectors, критерии core
replay U7, резерв **не** считать окончательно — пересчитает координатор после v2). Микрофикстуры — как текст в `sel0/`.
Коммит `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force. Маркеры
`REVIEW REQUEST <sha>` / **KANI3300 SEL0 ЗАВЕРШЁН**, затем стоп.

## Запреты

- Никаких сборок/dispatch/Cloud, локальных cargo/rustc/Kani/CBMC; raw logs/archives/credentials не читать.
- Не трогать другие worktree и клоны Kani (только чтение через `git show`).
- Никаких Actions/PR/issue/комментариев. Чужие PR verify-rust-std не открывать.
- Это верификация корректности инструмента Kani и стандартной библиотеки Rust, не security-работа. Отвечай кратко.
