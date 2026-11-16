# TASK — worker11: fixup-коммит в наш открытый kani#5172 (одна стадия)

Это верификация корректности, не security-работа. Отвечай кратко.

Правила: STYLE-UPSTREAM-RULES.md (обязательно).

#5172: ветка `fix/kani-uninit-unresolved-call-v3` в Tiramisu-Cake/kani, голова `6fe484b300`, ревью ещё не было. Новый коммит
поверх (не rebase, не amend):
1. `resolve_call` в points-to анализе: `checked_body(tcx, …)` вместо `instance.body()` — как просит комментарий upstream в
   `kani_middle/mod.rs`. Сейчас эта правка лежит в PR-01 стека (`d82752c8bc`, диф `6fe484b300..d82752c8bc`) — перенести её сюда.
2. Вычитать комментарии и тексты диагностики, добавленные #5172, по правилам: убрать формулы «чего код не делает», внутренние
   слова («legacy union slot pairing», «Conservative admission guard for generated ABIs, not an expansion of the shadow model»,
   «unproved generated ABI», «delayed-UB seeds» и подобные). Комментарии тестов #5172, которые PR-01 переписывал, —
   тоже сюда. Поведение и expected-выводы тестов не менять; если меняется текст диагностики — обновить expected и сказать.
3. Короткий комментарий к PR о новом коммите (≤3 предложения, строка раскрытия «…this comment was prepared…»).

Выход: локальный worktree и коммит (author Tiramisu-Cake <igkharin@gmail.com>, без Co-Authored-By); g0
`kani3300/wave0/5172-fixup/`: DIFF-SUMMARY.md (что и почему), COMMENT.md, HANDOFF.md (что PR-01 теряет/должен перебазировать).
Коммит g0 [skip ci]. Последней строкой READY <g0> <commit SHA> или STOP <причина>.
Без push/CI/публикаций/ledger; без локальных cargo/rustc/Kani/CBMC.
