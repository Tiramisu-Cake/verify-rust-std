# KANI3300 T1b-prep — compile-time trace контекстного ложного uninit `IndexRange::len`: реализация + пакет A

**Выдано координатором 2026-11-11, GO владельца; рамки — планер
(`/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/plan/PLANNER-T1A-RESULT-ANSWER.md` — прочитать целиком,
п.1–6 обязательны).** Основа: `kani3300/t0/DESIGN-TRACE.md`, `kani3300/t0/TASK-DRAFT-T1.md` (с поправками ниже),
`kani3300/t1a/RESULT-KANI3300-T1A.md`. Runtime **Codex**, одна стадия, **Cloud $0**: заканчивается на `PRE-BUILD REVIEW`.

## Поправки планера к TASK-DRAFT-T1 (приоритет над черновиком)

- **Только compile-time:** unit/stubs/фактический порядок codegen roots; cache hit/miss, creator/last writer, body/stage
  hashes; target-origin/relevance; выбранные/пропущенные MemoryInitOps (включая zero-ops и skip reasons); малый before/after
  MIR шага1/шага4/фактического `IndexRange::len` (instance, отсутствующий из-за inlining — отмечать явно).
- **Исключить:** runtime CBMC projection, `--cbmc-args --trace`, symbol/object mapping, `--no-slice-formula`, новые
  slicing/solver флаги, `--keep-temps` ради trace. Не запускать transformations дополнительно, не менять cache/traversal/
  порядок множеств. Payload фильтровать по функциям, но сохранять bounded origin/cache-writer witnesses из других roots и
  общий header.
- Production fix не входит. Concrete object/offset/R и полная runtime-причинность остаются UNKNOWN.

## Рабочее место

- Kani: новый клон **/root/kani-fix-3300-t1** (из `/root/kani-fix-3300-cmp`, ветка `diag/kani-3300-t1` от CMP2
  `b1f0105c03`); диагностическая delta — отдельным коммитом, production CMP2 побайтно (patch sha `46ad585f…`). Не пушить.
- Research: этот worktree (**/root/verify-rust-std-kani3300-t0**), писать `kani3300/t1b/` и tooling-расширение в
  `research/challenge-8/kani-k1/tools/` только этой ветки (KT2 `3bb5445d2a` — база; другие ветки/worktree не трогать).
- Другие клоны — только чтение.

## Что сделать

1. Диагностическая delta Kani: строго opt-in (env, например `KANI3300_TRACE_DIR` + `KANI3300_TRACE_FILTER`), opt-out —
   побайтно прежнее поведение; bounded (≤512 records/256KiB на compiler invocation, record ≤2048 B, run ≤1MiB, состояния
   PARTIAL/OVERSIZED с omission counts); не меняет verdict/exit/checks.
2. Tooling: opt-in поля запроса → валидированные env (не произвольный shell), sidecar → `summary.json.diagnostic_trace`,
   минимальный bounded reader `k1g.sh trace-field BUILD <path> <start> <count>` (≤20 records/12000 B, `next_start`,
   complete/omitted, identity binding). **Service/error-path tests** обязательны (невалидный env, oversized, отсутствие
   sidecar, opt-out). Существующие `summary/native/native-field` не менять по поведению.
3. Статика: rustfmt-обёртка `/tmp/claude-0/-root/5ce1713f-0d75-4ce2-92ab-bcf1e5df1b74/scratchpad/rustfmt.sh`
   (`--edition 2024`), `git diff --check`, лицензии; Python tooling tests (`python3 -I`). Компиляция Kani — NOT_RUN;
   учесть опыт G1 (E0308 `MachineSize`/`usize`): сверить сигнатуры stable_mir API по исходникам nightly-2026-10-23,
   неиспользуемые переменные/импорты (`-D warnings`).
4. Независимое ревью Kani delta и tooling отдельно (свой ревьюер): отсутствие семантических изменений, opt-out
   эквивалентность, bounds, identity binding.
5. Пакет **A** (9 roots CMP3, library tree `919cc3e2`, pin f046, CMP2 + diagnostic delta, KT2+extension, recipe как в T1a:
   uninit/controls on, inventory off, standard4/jobs1/3m), `kind: diagnostic`, slug `kani3300`, stage `kani3300-t1b`, owner
   `k1-merge`, request `kani3300-t1b-a-*`. Резерв `(9×3+30)×$0.0135=$0.7695`, cap **$0.80**. Пакет B (4 roots, $0.567) —
   подготовить запрос, но запускается только после разбора A и отдельного GO (п.4 планера).

## Результат

`kani3300/t1b/`: `DIAG-DIFF.md` (≤ 40 строк), `TOOLING-DIFF.md` (≤ 30 строк + tests), `PRE-BUILD.md` (≤ 30 строк:
identities, полные SHA патчей/applied tree/tooling, effective argv/env, резерв), `RUN-REQUEST.json` (A),
`RUN-REQUEST-B.json`. Коммиты `[skip ci]` (автор Tiramisu-Cake через `-c user.name/-c user.email`), push без force.
Последней строкой `PRE-BUILD REVIEW <полный research sha>`, стоп. Dispatch — только после GO координатора.

## Запреты

- Никаких сборок/dispatch/Cloud в этой стадии; локальных cargo/rustc/Kani/CBMC; Python и rustfmt-обёртка — можно.
- Raw logs/archives/credentials не читать (и локальные копии). Никаких Actions/PR/issue/комментариев, push в Kani. Без `git stash`.
- Это верификация корректности стандартной библиотеки Rust инструментом Kani, не security-работа. Отвечай кратко.

Маркеры `PRE-BUILD REVIEW <sha>` / **KANI3300 T1B ПАКЕТ ГОТОВ**, одна стадия, затем стоп.
