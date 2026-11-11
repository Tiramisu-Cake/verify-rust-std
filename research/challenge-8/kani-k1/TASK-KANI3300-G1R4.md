# KANI3300 G1R4 — регрессия: guard «foreign mutation of union storage» ловит аллокатор

**Выдано координатором 2026-11-11.** Runtime **Codex**, одна стадия, **Cloud $0** (проверка — fork CI координатором).
`TASK-KANI3300-G1.md`, правки планера, G1R/G1R2/G1R3 остаются в силе.

## Факт (fork CI, Tiramisu-Cake/kani run 43046573933, ветка `kani-3300-g1-ci` = G1 `6bb067476` + golden fix части 1)

`regression (ubuntu-22.04)`, suite `kani`: 643 passed, **4 failed** — `kani/Uninit/atomic.rs`, `vec-read-init.rs`,
`alloc-to-slice.rs`, `alloc-zeroed-to-slice.rs` (все `-Z uninit-checks`, ожидают SUCCESS). Единственная FAILURE-проверка в каждом:
- `std::alloc::alloc.unsupported_construct.1` @ `alloc/src/alloc.rs:156:9` (3 теста);
- `std::alloc::alloc_zeroed.unsupported_construct.1` @ `alloc/src/alloc.rs:321:9` (1 тест);
- Description: "Kani does not support foreign mutation of union storage without an effect model."

Suite `expected` (включая `uninit/g1-union-pointee-negative`) **не выполнялся**: прогон остановился на suite `kani`.

## Диагноз координатора (проверить по исходнику nightly-2026-10-23)

Guard в `ptr_uninit/uninit_visitor.rs:~634` срабатывает на **любой** `instance.is_foreign_item()` вне allowlist
`__rust_alloc/realloc/alloc_zeroed/dealloc`, даже без union-аргументов. Строки 156/321 — по-видимому, вызов
`__rust_no_alloc_shim_is_unstable_v2()` (foreign, без аргументов) перед `__rust_alloc*`. Проверить точный callee по исходнику.

## Что сделать

1. Production-коммит в `/root/kani-fix-3300-g1` (автор Tiramisu-Cake через `-c`, не пушить): guard для foreign/bodyless
   срабатывает только если вызов может затронуть shadow union-хранилища (аргументы `touches_shadow` или указатели/ссылки —
   по образцу `has_unmodeled_memory_args`), а не на любой foreign item. Обосновать soundness: foreign вызов без аргументов
   и без указателей не может мутировать union-хранилище, доступное harness'у, кроме как через глобальные — оценить и описать
   этот случай (static mut union?) — ≤ 10 строк в `kani3300/g1r4/GUARD.md`. Если нужен иной критерий — обосновать там же.
2. Sweep: прочие места G1, где guard/Unsupported ставится без проверки участия union (в т.ч. стр. ~804 `is_foreign_item`)
   и могут ловить обычный код с `-Z uninit-checks` — список в `GUARD.md`.
3. Регрессионные фикстуры не менять. Если нужен новый тест (foreign вызов с union через указатель → Unsupported) — добавить.
4. Статика: rustfmt-обёртка `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`
   (`--edition 2024`), `git diff --check`; сверить сигнатуры stable_mir; `-D warnings` (неиспользуемые переменные).
5. Независимое ревью дельты (свой ревьюер).

## Результат

`kani3300/g1r4/GUARD.md` + `RESULT-KANI3300-G1R4.md` (≤ 20 строк: sha коммита Kani, diff stat, ревью). Research-коммит
`[skip ci]`, push без force. Последней строкой `G1R4 READY <sha коммита Kani>`, стоп. Сборки/dispatch не нужны.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani-репозитории. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
