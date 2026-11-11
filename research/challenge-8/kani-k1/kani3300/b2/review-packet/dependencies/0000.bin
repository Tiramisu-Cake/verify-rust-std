# KANI3300 B2 — moved-from storage по фактическому MIR и Miri (аудит §2.6, P0)

**Выдано координатором 2026-11-12.** Основание (только чтение):
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/AUDIT-REPORT-KANI3300-RU.md` §2.6 и
`/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/audit/PLANNER-AUDIT-RESPONSE.md` (W2-B2).
Удалённые в G1R5 десять moved-from cases: Kani `/root/kani-fix-3300-g1`, диапазон `5b2265c41..8639a651f`
(`g1-union-pointee-negative`), заметки `/root/verify-rust-std-kani3300-g0/research/challenge-8/kani-k1/kani3300/g1r5/NOTES.md`.
Runtime **Codex**, одна стадия, **Cloud $0**. Исполнение — fork CI координатора (MIR-дамп + **Miri** на nightly пина).

## Цель

Установить эталон, а не гипотезу: какие формы moved-from в Rust (MIR + Miri на `nightly-2026-10-23`) деинициализируют
источник, а какие нет, — до любых правок Kani-модели.

## Что сделать

1. Восстановить десять удалённых cases как материал: `kani3300/b2/removed-cases.md` (≤ 40 строк: имя, форма, что ждали).
2. Probe crate `kani3300/b2/probes/` (Cargo.toml без зависимостей, edition 2021, `src/bin/<name>.rs`, по одному
   сценарию на бинарь, `fn main`): после передачи значения прочитать **исходные байты через raw pointer, полученный до
   передачи** (тот же live object). Сценарии минимум: `Copy` присваивание; обычный assignment `Move` (non-Copy);
   передача by-value в `#[inline(never)]` функцию (`Call(Move)`), включая address-taken аргумент; `mem::forget` и
   `intrinsics::forget`; повторная инициализация после move; поле/проекция move; union и `MaybeUninit` варианты.
   Каждый бинарь печатает, что он проверяет. Не полагаться на UB для печати значений — достаточно факта чтения.
3. `kani3300/b2/EXPECTATIONS.md`: для каждого бинаря — ожидание по Reference/MIR-документации и что именно скажет
   Miri (UB uninit / OK), с обоснованием; пометить, где ожидание неочевидно.
4. Ничего в Kani не менять. Независимое ревью probe crate (корректность сценариев: тот же объект, нет посторонних UB).

## Результат

`kani3300/b2/` (removed-cases.md, probes/, EXPECTATIONS.md, RESULT-KANI3300-B2.md ≤ 15 строк). Research-коммит
`[skip ci]`, push без force. Последней строкой `B2 PROBES READY <research sha>`, стоп. Координатор прогонит
`rustc -Zunpretty=mir` и `cargo miri run --bin <name>` в CI и вернёт результаты отдельной стадией.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC/Miri; Python можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
