# KANI3300 A1 — typed MaybeUninit transfer: preserve-mask по данным T (аудит §2.1, P0)

**Выдано координатором 2026-11-12, GO владельца.** Основание: аудит `research/challenge-8/kani-k1/AUDIT-REPORT-KANI3300-RU.md`
(§2.1, §2.2, §4.2) и ответ планера `kani3300/audit/PLANNER-AUDIT-RESPONSE.md` (стадия W1-A1) — прочитать оба. Runtime
**Codex**, одна стадия, **Cloud $0**. Проверка исполнением — fork CI координатора (узкий workflow uninit, ~10–15 мин).

## Дефект

В части 1 (`1cd96e354`) `AssignUnion`/`StoreArgument`/`LoadArgument` (и normal return) для `MaybeUninit` получают
`PointeeInfo::for_storage` с маской `true` на весь extent (`check_uninit/mod.rs:218–240`, `ty_layout.rs:132–143`), поэтому
typed transfer сохраняет shadow padding `T`. `MaybeUninit<T>` = union `{(), ManuallyDrop<T>}`: по Miri `union_data_range`
typed copy сохраняет только data bytes `T`, padding `T` сбрасывается. Риск — ложный SUCCESS.

## Что сделать

1. Kani: клон **/root/kani-fix-3300-a1**, ветка `fix/kani-3300-a1` от `1cd96e354` (автор Tiramisu-Cake через `-c`, не
   пушить; production и тесты — отдельными коммитами, нейтральные сообщения для upstream, без `[skip ci]`).
2. Разделить storage extent и typed preserve-mask: raw `copy`/`copy_nonoverlapping`/untyped — полный extent; typed
   assignment, StoreArgument/LoadArgument, normal return — маска data bytes `T` (D(T)); для плоского массива/slice слотов —
   D(T) по rustc stride слота. Маска только сохраняет исходное состояние разрешённого байта (false остаётся false), байты
   вне маски в destination становятся uninit. Неподдерживаемый layout → Unsupported до применения маски.
3. Тесты (различающие, по §2.1 «Критерий приёмки»): payload с однозначным padding (offsets подтвердить по layout);
   физически записать все байты источника; (a) raw copy сохраняет padding → чтение padding OK; (b) typed assignment →
   чтение padding = FAILURE uninit; (c) bodyful `#[inline(never)]` argument/return → FAILURE; (d) data bytes сохраняются
   (SUCCESS); (e) исходно незаписанный data byte остаётся uninit после typed transfer (FAILURE); (f) `[MaybeUninit<T>; N]`,
   N>1 — stride/offset. Существующие fixtures части 1 не ослаблять; если какие-то ожидания меняются — обосновать.
4. Статика: rustfmt-обёртка `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh
   --config-path rustfmt.toml` (все изменённые .rs, включая тесты), `git diff --check`, unused/`-D warnings` source audit,
   сигнатуры stable_mir по nightly пина. Независимое ревью (свой ревьюер).

## Результат

`kani3300/a1/NOTES.md` (≤ 30 строк: дизайн маски, затронутые call sites, тесты, ожидания) + `RESULT-KANI3300-A1.md`
(≤ 15 строк). Research-коммит `[skip ci]`, push без force. Последней строкой `A1 READY <sha последнего коммита Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
