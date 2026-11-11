# KANI3300 B1 — отдельный upstream-фикс: потеря операций на нерезолвимых вызовах (аудит §2.5, P0)

**Выдано координатором 2026-11-12, GO владельца.** Основание (прочитать, только чтение):
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/AUDIT-REPORT-KANI3300-RU.md` §2.5 и
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/audit/PLANNER-AUDIT-RESPONSE.md` (стадия W2-B1).
Runtime **Codex**, одна стадия, **Cloud $0**. Проверка исполнением — fork CI координатора (узкий workflow uninit).

## Дефект (чистый upstream)

`ptr_uninit/uninit_visitor.rs` (`visit_terminator`, Call): при `Err` от `try_resolve_instance` код делает
`push_target(Unsupported)` и `return` без `self.targets.push(...)` — теряется весь `current_target`, включая операции,
собранные `super_terminator`, и (в пустом entry block) ранее поставленные entry loads; `super_terminator` вызывается дважды.
Кроме того, локальный resolver может вернуть `Ok(Virtual)`/non-`Item`, который минует обработку `Item`/`Intrinsic`.
Delayed-UB instrumentation даёт свой диагноз только при наличии analysis targets, поэтому поведение зависит от контекста.

## Что сделать

1. Kani: клон **/root/kani-fix-3300-b1**, ветка `fix/kani-uninit-unresolved-call` от **upstream `bf9c58e662`** (не от части 1).
   Автор Tiramisu-Cake через `-c`, не пушить; production и тесты отдельными коммитами, нейтральные сообщения для upstream.
2. Исправление: один `super_terminator`; при Err сохранять уже собранные операции и сам target с явным Unsupported;
   явная классификация Virtual/non-Item (поддержано или Unsupported с понятной диагностикой). Один владелец диагностики
   для fn-pointer/virtual вызовов; если legacy golden (`tests/expected/uninit/delayed-ub-unsupported-call`) меняется —
   обосновать и обновить осмысленно.
3. Тесты: пустой entry block с entry loads; уже накопленные ops перед нерезолвимым вызовом; обычный FnPtr; erased/wrapped
   pointer; virtual (dyn) call; global/escaped случай; варианты с delayed-UB seeds и без. Не объявлять source-находку
   измеренным false SUCCESS — ожидания писать по семантике.
4. Статика: rustfmt-обёртка `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh
   --config-path rustfmt.toml`, `git diff --check`, `-D warnings` source audit. Независимое ревью (свой ревьюер).

## Результат

`kani3300/b1/NOTES.md` (≤ 30 строк) + `RESULT-KANI3300-B1.md` (≤ 15 строк) в этом worktree
(/root/verify-rust-std-kani3300-t0). Research-коммит `[skip ci]`, push без force. Последней строкой
`B1 READY <sha последнего коммита Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
