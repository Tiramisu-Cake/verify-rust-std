# KANI3300 A2 — layout: offset `RigidTy::Pat` и сравнение padding вложенного enum (аудит §4.1)

**Выдано координатором 2026-11-12.** Основание: `AUDIT-REPORT-KANI3300-RU.md` §4.1 (абзац «В части 1 есть два
дополнительных риска…») и `kani3300/audit/PLANNER-AUDIT-RESPONSE.md` (W1-A2) — прочитать. Runtime **Codex**, одна стадия,
**Cloud $0**; исполнение — узкий fork CI координатора.

## Что сделать

1. Kani: **/root/kani-fix-3300-a1**, ветка `fix/kani-3300-a1` поверх A1 (`613c18831`), отдельные коммиты (автор
   Tiramisu-Cake через `-c`, не пушить, нейтральные сообщения для upstream).
2. `ty_layout.rs` (часть 1 `1cd96e354`, ~L299–375): ветка `RigidTy::Pat` передаёт `0` вместо `current_offset` — исправить
   (в G1 `cac044742` ~L462–470 это уже исправлено — свериться). Сравнение padding вариантов вложенного enum: маски строятся
   в абсолютных offsets размера enum → различающиеся диапазоны могут обрезаться и layout принимается за однородный.
   Сравнивать варианты в локальной системе offsets, затем применять смещение композиции ровно один раз.
3. Тесты: nested `Pat`/enum на **ненулевом** offset внутри `MaybeUninit`/struct; одинаковые layouts вариантов → positive;
   различающийся padding вариантов → Unsupported (с точной диагностикой). Проверить направление `[MaybeUninit<T>; N] → [T; N]`
   и `raw_eq` (читает все байты через ссылки): подтвердить покрытие тестом либо закрыть непокрытую форму явным Unsupported.
4. Статика: rustfmt-обёртка `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh
   --config-path rustfmt.toml`, `git diff --check`, `-D warnings`/clippy source audit (CI запускает
   `cargo clippy --workspace --tests -- -D warnings`), сигнатуры. Независимое ревью.

## Результат

`kani3300/a2/NOTES.md` (≤ 30 строк) + `RESULT-KANI3300-A2.md` (≤ 15 строк), research-коммит `[skip ci]`, push без force.
Последней строкой `A2 READY <sha последнего коммита Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
