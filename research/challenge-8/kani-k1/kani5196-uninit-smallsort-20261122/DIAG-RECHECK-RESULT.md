# kani5196 · повтор ITER/SELECT · офлайн-вердикт координатора

Run `45842925562` (trigger `cde6169113`, tree `e1791b8ff5`), tool `1c6e63b1f7`, nightly-2026-11-23, CBMC 6.11.0. Все 8 корней завершились, regular-инвентари `COMPLETE`. Вердикт пишет координатор: у планера ход дважды обрывался на фильтре контента Codex. [GO](DIAG-RECHECK-GO.md) · [Ревью](DIAG-RECHECK-REVIEW.md)

| Пара | OFF | ON | Вердикт |
| --- | --- | --- | --- |
| ITER (`iter_by_value`) | 122 SUCCESS, cover SATISFIED, без FAILURE | 2 FAILURE: `std::ptr::read::<usize>.safety_check.1/.4` на `core/src/ptr/mod.rs:1763:9` («uninitialized pointer of type `*const usize`» / «`usize`»); три `assert!` фикстуры (класс `panic`, `iter.rs:12/14/16`) SUCCESS, cover SATISFIED | **REPRODUCED** |
| ITER-INIT (`iter_initialized`) | SUCCESS | SUCCESS: оба `assume_init_read` и assertions, cover SATISFIED | контроль чист |
| SELECT (`select_pointer`) | SUCCESS, 4 covers | 1 FAILURE: `transmute_neo::<MaybeUninit<*const u64>, *const u64>.safety_check.1` на `core/src/mem/mod.rs:1279:14`; `observe` — обе assertions и проверка чтения `*selected` (`select.rs:22:22`) SUCCESS, 4 covers SATISFIED | **REPRODUCED** |
| SELECT-INIT (`select_initialized`) | SUCCESS | SUCCESS, 4 covers | контроль чист |

Повтор привязан к инициализированным операциям: OFF чисты, INIT-контроли с теми же значениями чисты с флагом, assertions и covers фикстур достигнуты. Отчёты совпадают с run `45163409005` на `bcdc1a0f8d`; исправление замыканий `cfcd2eb1d` и merge main их не изменили. Binder сохранил `INCOMPLETE` на части OFF (неоднозначность кандидатов select_call), это не влияет на вердикт по нативным свойствам.

Связь с kani5229 (ложный отчёт на `[MaybeUninit::new(1u32); 3]`, причина в `Rvalue::Repeat`): ITER — другой путь (`into_iter` массива, без Repeat), упоминаем как родственный.

Черновик комментария: `/root/smallsort-pr-drafts/COMMENT-KANI5196-ITER-SELECT-DRAFT.md`. По решению владельца 2026-11-26 — два равноправных пути: правка в PR или отдельный issue после merge.
