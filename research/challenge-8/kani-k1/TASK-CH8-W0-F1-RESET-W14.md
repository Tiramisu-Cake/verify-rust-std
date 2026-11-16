# TASK — worker14: F1 — reset состояния инициализации в automatic harness, отдельный PR на main (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Правила: STYLE-UPSTREAM-RULES.md (обязательно).

Сейчас исправление живёт в PR-02 стека: коммит `05da1a7a8c` поверх `932fb8395a` (`/root/kani-fix-ch8-pr02-final`), вместе с
логикой масок. Нужен самостоятельный коммит прямо на upstream `0aac16ef62`: `is_harness` распознаёт automatic harness
(≈7 строк), без масок/seed/иных частей стека.

Тест: один каталог `tests/script-based-pre/<имя>`: `kani autoharness -Z uninit-checks` на двух функциях — чтение padding-байта
через сырой указатель (ожидание FAILURE, описание `Reading from an uninitialized pointer` без типа: Kani пишет тип указателя
`*const u8`) и запись байта перед чтением (SUCCESS). Удалённая ранее фикстура `autoharness_entry_reset_uninit_read`
(run 43783429976) на самом деле детектировала чтение — упала лишь на строке expected с типом `u8`; учесть.

Также: черновик текста PR (образец — смерженный kani#5153; проверка из STYLE-UPSTREAM-RULES), имя ветки нейтральное
(`fix/autoharness-uninit-reset`). Подготовить запуск полного набора стандартных workflow Kani на этой голове в форке
Tiramisu-Cake/kani — как был получен прогон 43028586621 для #5153 (выяснить механизм, ничего не запуская).

Выход: локальный worktree и коммит (author Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By, без [skip ci]);
g0 `kani3300/wave0/f1-reset/`: PR-TEXT.md, CI-PLAN.md, HANDOFF.md, коммит g0 [skip ci].
Последней строкой READY <g0> <source SHA> или STOP <причина>.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
