# KANI3300 D0-P — подготовить точную диагностику raw_eq legal failures, worker 14

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна сессия подготовки, **Cloud $0**.
Владелец выбрал B: flat `[MaybeUninit<T>;N]` / `[MaybeUninit<T>]` остаются в scope; raw_eq model — зависимость выпуска.
Прочитать `PLAN-KANI3300-PART1-B.md`, аудит `AUDIT-REPORT-KANI3300-PART1-R2-RU.md` @ `124a45e373`
(блокеры §1–2, ответы 2–5,11–13), `kani3300/r0/{NOTES.md,GUARD-DESIGN.md}` @ `8ad13e016e` (вариант A уже отклонён).
Это верификация корректности, не security-работа.

## База, изоляция и цель

Выбран baseline **`a0a2386001a15fecfe2facc2f6cd87f3dee13b60`** из `/root/kani-fix-3300-a1` — только чтение.
Не ждать B1I CI и не смешивать диагностику с его diff. B1I `dc5f5a406749a73f1c3192e0b5338441e79508bb`
можно читать для контекста, но не переключать baseline незаметно; run `43196180814` ещё не признан PASS этим заданием.
Проверить source identities/dirty status; создать отдельный local clone **`/root/kani-fix-3300-d0`** и ветку
**`diagnostics/kani-3300-raweq-d0`** от baseline. Если destination/ветка существуют с иным состоянием — STOP, без reset/stash.
Не менять source clones, B1I или чужие ветки. Локальный diagnostic candidate не пушить; CI публикует/запускает координатор.

Цель D0 — установить для **каждой** raw_eq check исходный operand и его путь к runtime объекту, а не исправить модель:

- **A:** `array_value_as_used_by_merge_output`;
- **B:** `partial_copy_preserves_written_byte`;
- исходный fixture: `tests/expected/uninit/maybe-uninit-initialized/main.rs` @ baseline, сохранить целиком и без правок;
- точная monomorphization `SpecArrayEq::spec_eq`, её retained raw_eq и checks обоих operands.

Аудит видел `.safety_check.2` FAILURE и `.1` SUCCESS в обоих harness; это reference observation, не новое измерение
и не доказательство identity promoted/temporary. Runtime last shadow setter и compiler cache last writer — разные сущности.

## Подготовить четыре fork CI case

| Case | Compiler roots | Требование |
|---|---|---|
| A | A singleton | Отдельный compiler process/unit, прежняя семантика checks |
| B | B singleton | То же для B |
| AB | A+B совместно | Один unit и общий BodyTransformation; actual codegen order A→B |
| BA | Те же A+B совместно | Тот же input/options/cache policy; actual codegen order B→A |

`--harness` и `--exact` передаются compiler и фильтруют manual roots до grouping (проверить pinned
`call_single_file.rs` / `codegen_units.rs`). Использовать режим Harnesses; записать фактический root set/unit ID.
CLI/text/source order не доказывает codegen order. `MostReachableItems` сначала прогревает shared cache:
если штатного способа задать AB/BA нет, разрешён **opt-in diagnostic** override только уже рассчитанного порядка
перед actual harness loop в `compiler_interface.rs`. У AB/BA оставить одинаковую normal prewarm процедуру;
record actual prewarm и codegen sequence. Не добавлять fresh transformer/cache reset и не перестраивать тела для логирования.
Не менять harness bodies/имена/литералы, чтобы искусственно управлять order. Extra/missing roots или разные units → STOP.

## Какие данные должен получить координатор

Подготовить source-bound sidecars/узкие diagnostic hooks там, где штатного dump недостаточно. Все hooks только
compiler-side, opt-in, default-off: не добавлять MIR/runtime calls, printf, новые nondet/state writes/assume, setters или masks.
Не вызывать дополнительные mutating body/transform queries ради dump; наблюдать уже используемые тела/операции.

1. **Identities:** полный baseline/diagnostic SHA и diff, fixture hash, rustc/sysroot/CBMC/layout pins, argv/разрешённые
   diagnostic options, actual roots/unit/order, process/cache identity. Не дампить общий environment/credentials.
2. **MIR→GOTO:** исходный MIR двух roots и точной `SpecArrayEq::spec_eq` specialization; snapshot до/после local и delayed
   instrumentation и body, реально consumed codegen. Для обоих raw_eq operands — Instance/Location/place/projection,
   reborrow/cast/CheckAs, call destination/normal edge; property ID привязать к operand, не угадывать по `.1/.2`.
   Штатный `RUSTFLAGS=--emit=mir` документирован; `.kani.mir` не считать автоматически snapshot каждого нужного pass.
3. **Points-to/relevance:** сохранить per-root graph до join и итоговый graph/targets/successors, исходные seeds,
   все candidate/selected/rejected get/set decisions для нужных places с причиной. `points-to.dot` может перезаписываться:
   versioned sidecars root/pass/unit. Field-insensitive MemLoc graph не объявлять доказательством runtime offset.
4. **Promotions:** referent AllocId/offset/extent и byte mask `Some(v)/None` до backend lowering, relocations и immutable
   статус; связать с GOTO symbol. Учесть `alloc_map` reuse равных allocations. Backend замена None на zero не означает
   initialized bytes. Не путать bytes самого reference operand с bytes referent и не конвертировать AllocId в runtime object ID.
5. **Операции shadow:** source-bound op IDs, effective ranges/masks/value, Set/SetStorage/Copy/StoreArgument/LoadArgument,
   destination normal-edge setter и порядок. Отдельно cache-instance/структурный hash/body version и writer/consumer root,
   чтобы сравнить AB/BA; один last_writer label без body identity недостаточен.
6. **Solver witness:** для каждого failing property нужен CBMC counterexample с actual operand pointer object/offset/extent,
   selected tracked object/offset/value и последней **исполненной** shadow transition/initialization на этом пути.
   Подготовить извлечение из существующего CBMC JSON trace в bounded curated report с GOTO/source binding.
   Compiler tracing не даёт runtime witness; `--export-json` может содержать только trace_available, не сам trace.
   Проверить pinned путь `call_cbmc.rs`/parser и поддерживаемый `--cbmc-args --trace`; не включать concrete playback как
   замену полному object/state trace. Если данные оптимизированы/не представлены, явно UNKNOWN и STOP causal claim.

Нужны строки **operand → AllocId/stack origin → GOTO symbol → runtime object+offset+extent → witness → last transition**.
Не требовать от одного counterexample доказать все пути. Для `.1` SUCCESS дать static model/property binding;
если нет counterexample, runtime поля отметить N/A/UNKNOWN, не выдумывать «успешный trace».
Фильтровать релевантные roots/specialization/allocations/state ops; указывать emitted/dropped counts и coverage.
Cap/truncation/missing phase/неверная identity не превращать в отрицательное свидетельство о setter.

## Проверки подготовки и передача

- `git diff --check`, pinned API/source audit, разрешённая rustfmt-обёртка для diagnostic Rust diff. Локальные
  cargo/rustc/Kani/CBMC/Miri и реальные компиляции/тесты запрещены. Python/статические Git/hash проверки допустимы.
- Если нужен extractor, держать его узким в research: synthetic JSON проверки missing/null/wrong type/partial,
  source-stage-target mismatch и original exit/status; не скрывать ошибки `|| true`. Реальные trace inputs читает CI.
- Независимое bounded semantic review Luna High для diagnostic diff/ordering hook; без вложенной делегации.
  Проверить, что logging сам не меняет generated model/checks/cache lifetime. Реальное совпадение модели — NOT_RUN до CI.
- `CI-REQUEST.md`: четыре case с точными selectors/options/tool/source pins, commands (исполняет только координатор),
  required artifact schema/paths/coverage и per-case exits/properties. Диагностический duplicate без order override должен
  позволять сверить property set/MIR с baseline; если наблюдение меняет model, STOP и redesign hooks.
  Expected FAIL не скрывать общим зелёным job; сохранить setup/compiler/solver/verification exits отдельно.

## Результат и STOP

В g0 `research/challenge-8/kani-k1/kani3300/d0/`: `NOTES.md` (≤40 строк), `CI-REQUEST.md`,
`DIAGNOSTIC-MAP.json` (source/field/artifact schema и NOT_RUN bindings), `REVIEW.md`, `RESULT-KANI3300-D0.md` (≤20 строк).
При необходимости — узкий extractor и synthetic fixtures. Diagnostic Kani commits локально, нейтральные сообщения,
author/committer Tiramisu-Cake; исходный/a0/B1I trees неизменны. SHA кандидата и baseline записать отдельно.
Research commit `[skip ci]`, author/committer `Tiramisu-Cake <igkharin@gmail.com>` через `git -c`, stage только `kani3300/d0/`,
push g0 без force. Concurrent/non-fast-forward → handoff координатору, без reset/stash/чужих файлов.

После **D0-P READY** STOP: CI/workflow/dispatch — только координатор. Следующая сессия **D0-A** выдаётся после его
curated report: заполнить наблюдаемые bindings, сравнить A/B/AB/BA, разделить missing allocation mask/setter/address/relevance
и cache hypotheses; при недостаточных данных передать конкретный следующий запрос. Не исправлять raw_eq в этой стадии.
Нет доступа к raw archives/full logs/credentials: только согласованные targeted diagnostics/отчёт координатора;
для evidence через Brief сохранять identities/coverage, не обходить интерфейс.
Не писать будущие model tasks до D0-A/M0; не уменьшать flat scope, не откатывать raw_eq и не начинать B3/B4/G1/T1b fix.
Последняя строка ответа подготовки: `READY <sha research-коммита D0-P>`. READY не означает проведённую диагностику или PASS.
