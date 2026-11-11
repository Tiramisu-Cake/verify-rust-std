# KANI3300 A2R2 — raw_eq: неверный уровень косвенности проверки

**Выдано координатором 2026-11-12.** `TASK-KANI3300-A2R.md` в силе. Runtime **Codex**, одна стадия, **Cloud $0**.
Выполнять **после** A3 в той же ветке `/root/kani-fix-3300-a1` (`fix/kani-3300-a1`), поверх её HEAD.

## Факт: `Uninit Quick`, ветка `uninit-ci/a2r-raw-eq` (A2R `b207847932`), run 43111242922

Format/build/clippy PASS; kani 22/22; expected 90 passed / **1 failed** — `maybe-uninit-initialized` (ждёт
`Complete - 8 successfully verified…`): harness `array_value_as_used_by_merge_output` и
`partial_copy_preserves_written_byte` → FAILED с
`<u8 as std::array::equality::SpecArrayEq<u8, 4>>::spec_eq.safety_check.2`,
`Undefined Behavior: Reading from an uninitialized pointer of type `*const [u8; 4]``
(`core/src/array/equality.rs`). `maybe-uninit-transmute` и `maybe-uninit-partial-copy` теперь проходят.

Тип в описании — `*const [u8; 4]`, а не `[u8; 4]`: проверка, по-видимому, применяется к месту, где хранится сам
аргумент-ссылка `raw_eq` (уровнем выше), а не к pointee. Ожидание: проверять **байты pointee** обоих аргументов
(`size_of::<T>()`), как обычный `CheckRef`/`Check` для `&T`.

## Что сделать

1. Исправить уровень косвенности (операнд — ссылка `&T`; проверяется `*operand`, layout `T`). Сверить с тем, как
   `uninit_visitor` строит `CheckRef` для обычного разыменования ссылки.
2. Убедиться, что тест raw_eq (полностью init → SUCCESS; 1 uninit байт → FAILURE с типом `[u8; N]`/`u8`) и три
   MU-теста согласованы. rustfmt `--config-path rustfmt.toml`, diff --check, независимое ревью.

## Результат

Коммит(ы) поверх HEAD ветки, `kani3300/a2r2/RESULT-KANI3300-A2R2.md` (≤ 10 строк), research `[skip ci]`, push без force.
Последней строкой `A2R2 READY <sha Kani>`, стоп.

## Запреты

- Никаких сборок/dispatch/Cloud; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка
  (`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`) — можно.
- Raw logs/archives/credentials не читать. Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности инструмента Kani, не security-работа. Отвечай кратко.
