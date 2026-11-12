# KANI3300 C1-L — compile-only lowering пакет для promoted drafts, worker 15

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна сессия подготовки, **Cloud $0**, без запусков.
Независимо от M0 воркера 14: проверяем пригодность source controls, не реализуем model/guards и не активируем C1 suite.
Это верификация корректности, не security-работа.

## Вход и цель

Прочитать `kani3300/c1p/{HANDOFF-M0.md,CONTROL-MATRIX.json}` @ **`d8d3e6d4ca`**, шесть `promoted_*.rs` drafts;
`kani3300/d0a/{RESULT.md,NOTES.md}` @ **`ff5cabbfca`**, `kani3300/d0/{CI-REQUEST.md,CI-WORKFLOW.md}`.
Цель — подготовить **compile-only** fork CI request: actual lowering raw_eq, immutable AllocId/Some-None mask,
offset/extent/relocations и helper binding для каждого draft. Не требовать CBMC trace, solver outcomes или runtime witness.
После cap-ошибок D0 не повторять 64 MiB solver capture; в этом пакете solver вообще не запускается.

Первые cases: `promoted_direct_legal`, `promoted_direct_left_hole`, `promoted_direct_right_hole`,
`promoted_helper_legal`, `promoted_helper_left_hole`, `promoted_helper_right_hole` из C1-P (6 отдельных inputs).
Три flat whole-copy drafts остаются в очереди C1 после M0, здесь их не расширять. Два исходных D0 legal не перезапускать.

## Pins и допустимая работа

Diagnostic tool **`5eec235e3d0eeb99d7e432fcaef3a3135747b789`** (D0-PR) в `/root/kani-fix-3300-d0` читать,
не менять его текущую ветку/CI workflow. Этот diagnostic основан на **a0a2386001**, не на B1I-A 6134e42dd1;
это baseline lowering evidence, не acceptance актуального release tree. Record исходный base/diagnostic/input hash отдельно.
Никаких model commits из M0/B1/B3 не добавлять.

1. Проверить по source совместимость существующего D0 sidecar/filter/identity runner с 6 cases и specialization `[MU<u8>;3]`.
   `--only-codegen` есть в pinned Kani; сверить driver path, чтобы request гарантированно не запускал CBMC.
   Не использовать `--export-json` как full trace API: здесь нужен compiler-side report, не solver schema.
2. Подготовить case manifest с exact fixture SHA-256, harness selector/`--exact`, Harnesses mode, toolchain/sysroot/layout pins,
   `--emit=mir`/sidecar options, ожидаемым root set и выходами compiler/setup. Один input → свой каталог/manifest;
   source-level слово promoted не является требованием «назначить» произвольный AllocId.
3. Для каждого request получить original/consumed MIR, retained raw_eq и оба full-byte checks; caller→helper operands;
   real GlobalAlloc kind/AllocId, actual mutability, Some/None bytes, relocation spans, offset/extent и GOTO symbol/reuse.
   Результат может показать Stack/aggregate вместо promotion: это честный **LOWERING_MISMATCH**, не synthetic PASS.
   Отсутствие AllocId без полной coverage — UNKNOWN. Не выводить initializedness из backend None→zero lowering.
   Если delayed analysis не активирован из-за пустых targets, записать explicit empty/NOT_ACTIVATED с фазовым binding,
   не выдумывать graph и не подменять отсутствие фазы утверждением «writes/setters отсутствуют».
4. Если D0 guards/filters hardcoded под A/B/[u8;4], подготовить минимальный **diagnostic-only** adapter в отдельном клоне
   `/root/kani-fix-3300-c1l`, ветка `diagnostics/kani-3300-c1l` от точного diagnostic SHA; существующий clone не перезаписывать.
   Только compile-time case/filter/identity sidecars, opt-in/default-off; прежние защиты заменить точными **новыми** pins,
   не отключать. Не копировать D0 solver-capture infrastructure, order overrides или broad tracing.
   Без новых MIR calls/state writes, nondet/assume/setters/masks, mutating body queries, memory model или production changes.
   Если нужен более широкий runner/инструментальный redesign — STOP с `ADAPTER-REQUIREMENTS.md`, не строить framework.
5. Исходные drafts сохранить с hash. Можно исправить явную syntax/edition проблему отдельным diff с объяснением,
   но не переписать inputs ради желаемого promoted/unsupported outcome. Для некомпилируемой/неподходящей формы
   дать минимальный proposed replacement как новый draft, а не присвоить старому input новый observed статус.

## Bounded report и handoff

`CI-REQUEST.md` для координатора: 6 compile-only cases, source/binary/config hashes, argv, stage/status/exit fields и
узкий artifact schema. Поля/byte masks только релевантных operands/allocations; не полный sysroot MIR/граф/trace.
Явные emitted/dropped/filtered counts, required field coverage; curated packet ≤5 MiB, case ≤512 KiB,
общие metadata ≤1 MiB. Если required данные не помещаются, STOP с конкретным пересмотром фильтра/пакета до запуска,
не повышать cap автоматически и не обрезать обязательный binding молча.
Missing/capped/extra roots/wrong identity/solver accidentally run → STOP affected case. Captured opaque IDs не превращать
в runtime objects; actual runtime initializedness/reached property status остаются **NOT_RUN**.
Curator обязан сохранить compiler exit и различить setup fail, unsupported, incomplete report и successful codegen;
compile success не означает legal verification SUCCESS, а hole source не означает measured uninit failure.
Если нужен extractor — synthetic Python checks missing/null/wrong-type/partial/wrong-stage/identity, без чтения raw CI inputs локально.

Если есть diagnostic adapter, один bounded Luna High review его diff/пакета, без вложенной делегации; unchanged D0 semantics
повторно не ревьюить. Статика: diff --check, hashes/schema/API и разрешённая rustfmt-обёртка для изменённых .rs.
Локальные cargo/rustc/Kani/CBMC/Miri и компиляции запрещены. Не ждать CI в этой сессии, ничего не запускать самому.

## Результат и STOP

В g0 `research/challenge-8/kani-k1/kani3300/c1l/`: `NOTES.md` (≤30 строк), `CASE-MANIFEST.json`, `CI-REQUEST.md`,
`EXPECTED-BINDINGS.json` (semantic expectations отдельно от NOT_RUN observed fields), при необходимости adapter patch/REVIEW,
`RESULT-KANI3300-C1L.md` (≤15 строк). Новые compile facts появятся только после CI координатора и следующей аналитической сессии.
Local diagnostic commit — только при adapter, author/committer Tiramisu-Cake; не пушить Kani. Source d0/p1b1 и drafts c1p не менять.
Research commit `[skip ci]`, author/committer `Tiramisu-Cake <igkharin@gmail.com>` через `git -c`,
stage только `kani3300/c1l/`, push g0 без force; concurrent/non-fast-forward → handoff, не включать m0/d0/чужие файлы.
Нет разрешения raw archives/full logs/credentials, PR/issue/комментариям, Actions/Cloud dispatch или workflow публикации.
STOP после готового request; C1 semantic activation/model guards только после M0 и отдельного задания.
Последняя строка: `READY <sha research-коммита C1-L>`. Не CI PASS и не runtime/proof coverage.
