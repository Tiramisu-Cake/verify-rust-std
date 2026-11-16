# TASK — worker11: финальный кандидат PR-02 + черновик текста (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

## Итог U-03 (run 43783429976, pkg `80d0d98529`)

PR-02 + fix: fmt/build/clippy OK; compiler units 66/66; expected uninit 56/0 (2 ignored); function-contract 134/0
(4 ignored); весь `script-based-pre` autoharness набор: 54 passed, 1 failed; новые `autoharness_entry_reset_*`:
6 passed, 1 failed — `autoharness_entry_reset_uninit_read`: verification SUCCESS (exit 0) вместо ожидаемого UB
(чтение padding-байта `#[repr(C)]` struct Kani не считает uninit) — дефект фикстуры.
Matched old PR-02 `932fb8395a`: seed_only / argument_seed / contract_seed — ожидаемый fatal
`immutable masks: reset is absent from this model`; no_seed — completed, как ожидалось.
U-01 arm B: SEL1+fix — исходный #4854 autoharness SUCCESS 154/0.

Решение координатора: `uninit_read` из PR-02 убрать (обнаружение uninit-read покрыто существующим uninit-набором);
оставить 6 фикстур, прошедших в U-03 байт-в-байт. Новый CI не нужен: оставшиеся файлы и compiler diff идентичны U-03.

## Что сделать

1. Локальная ветка `work/ch8-pr02-final` от `932fb8395a`: один коммит «fix + 6 regressions» (compiler diff sha256
   совпадает с U-01..03; фикстуры байт-в-байт как в U-03 без uninit_read). Сообщение коммита — в стиле upstream Kani,
   без «[skip ci]», без Co-Authored-By, author `Tiramisu-Cake <igkharin@gmail.com>` в команде. Не пушить.
2. Сверка: `git diff` с U-03 source = только удаление каталога uninit_read; записать хэши.
3. Черновик обновлённого текста PR-02 (`kani3300/c2-slices/pr-texts/PR-02.md` — не перезаписывать, рядом
   `PR-02-v2.md`): добавить в описание исправление entry reset для automatic harnesses и в Testing — новые
   регрессии и что на старом PR-02 они дают fatal; убрать любые утверждения, не подтверждённые прогонами.
   Без ссылок на наши research-документы и внутренних имён; disclosure-строка прежняя.
4. g0 `kani3300/ch8-pr02-reset/final/`: RESULT-U03.md (факты выше), FINAL.md (SHA/tree/хэши). Последней строкой
   `READY <final-sha> <g0>` или `STOP <причина>`.

Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC. Коммить в основной g0 worktree.
