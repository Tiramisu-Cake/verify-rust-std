# KANI3300 M0 — контракт модели anonymous/promoted initialization, worker 14

**Выдано координатором 2026-11-12.** Runtime **Codex**, одна сессия design-only, **Cloud $0**, без запусков.
Решение B сохраняется: flat `[MaybeUninit<T>;N]` / `[MaybeUninit<T>]` остаются в scope, raw_eq model — зависимость выпуска.
Это верификация корректности, не security-работа.

## Обязательные входы и установленный диагноз

Прочитать `PLAN-KANI3300-PART1-B.md`, аудит R2 @ `124a45e373` (ответы 2–5,8,11–13),
`kani3300/d0a/{RESULT.md,NOTES.md,REVIEW.md,bridge.json,runtime.json,observations.json}` @
**`ff5cabbfca8b5108d21c27904c1f7b7e40ab25c1`**, `kani3300/c1p/HANDOFF-M0.md` и CONTROL-MATRIX @ `d8d3e6d4ca`.
Production target read-only: `/root/kani-fix-3300-p1b1` @ **`6134e42dd1c65dc980336e7d9455aba02d423edf`**,
production как `dc5f5a406749a73f1c3192e0b5338441e79508bb`. Диагностический `5eec235e3d0eeb99d7e432fcaef3a3135747b789`
и baseline `a0a2386001a15fecfe2facc2f6cd87f3dee13b60` — другие деревья, не новый production base.

- Run `43209338134`: во всех 12 harness results из 8 invocations .2 FAILURE, .1 SUCCESS; workflow success не proof PASS.
- A RHS `[1,2,3,4]` = immutable promoted AllocId9; B RHS `[9;4]` = AllocId5; offset0, extent4, Some×4.
  Runtime selected RHS byte остаётся false после harness initialization mem_init.rs:244, matching setter/transfer нет.
- Левый assume_init temporary получает SetRef(true) на normal edge, get TRUE на пути .2 counterexample.
  Missing temporary setter и ошибка адреса не объясняют эти два отказа. Не добавлять setter, которого здесь не недостаёт.
- Структурный gap: MemLoc только Stack/Heap/Static, constant successors только check_static_ptr, seeds только GlobalAlloc::Static.
- All 12 captures capped at 64 MiB; восстановлены 4 целых целевых fragments, остальные 8 UNAVAILABLE.
  Числовой AllocId не runtime object ID; extent4 mask/type-derived, runtime OBJECT_SIZE UNKNOWN; .1 не имеет отдельного witness.
  Не превращать эти ограничения в глобально полный trace или доказательство всех offset/путей.
- Singleton/baseline воспроизводят .2: K0 не нужен для причины этого отказа. У второго codegen harness +2 SUCCESS
  ptr::write safety checks — отдельная inventory-разница, не универсальная cache independence и не уже принятый cache fix.

## Что спроектировать — без production/test changes

1. **Область и invariant.** Различить доказанную immutable allocation mask, runtime initializedness изменяемого tracked storage
   и неизвестное покрытие. Это логические категории; не навязывать новый runtime tri-state без необходимости.
   Для выбранного witness каждое проверяемое byte read должно опираться на фактический init state/доказанную immutable mask.
   None/исходный false не превращаются в true; неизвестное происхождение/эффект не разрешает молчаливый skip.
2. **Identity и диапазоны.** Определить representation referent AllocId + offset + extent + mutability + relocations,
   перенос до seed/points-to/relevance и связь с фактически emitted GOTO symbol/runtime object. IDs compiler-local;
   не hardcode AllocId9/5 и не отождествлять их с object numbers. Учитывать subranges/interior pointers, dynamic choice,
   helper calls и оба raw_eq operands; одинаковый тип ссылки не доказывает origin.
3. **Маска immutable bytes.** Источник — actual referent Some/None до backend `unwrap_or(0)`, не D(T) и не byte values
   готового GOTO initializer. Указать relocation ranges/pointer-width правила, bounds/zero-size и поддержанные layouts.
   `alloc_map` может вернуть один symbol для равных Allocation: маска/identity binding должны быть согласованы при reuse;
   несовместимые маски нельзя просто объединять OR. Рассмотреть mutable allocations/UnsafeCell: source `&T` и текущий
   hardcoded interior-mutability shortcut не доказывают immutability. Непокрытое — явная граница/Unsupported.
4. **Lifecycle и placement.** Как immutable mask становится доступна проверке **после** каждого nondet witness reset
   на harness entry; что происходит в singleton/shared unit, при нескольких ссылках/aliases и coalescing.
   Сравнить не более двух узких вариантов placement, выбрать один и обосновать; init event или derived immutable query
   должны быть source-bound. Не писать глобальное true и не переинициализировать mutable/unknown bytes при каждом ref use.
   Идемпотентность для proven immutable mask надо доказать, а не предполагать по одному успешному equality.
5. **Композиция с существующей моделью.** Typed D(T) очищает padding, raw copy сохраняет extent, false data сохраняется;
   overwrite/reset/alias/offset и argument/return не могут быть затёрты новой инициализацией.
   Сохранить существующий normal-return setter левого temporary; M2 теперь coverage/qualification, новый setter только
   при отдельном достигнутом gap. Shadow-carrying return использует фактический false transfer, не blanket D(T)/true.
   Normal edge, unwind/abort, private state/DFCC и runtime/backend hooks описать отдельно, не обещать новую ABI поддержку.
6. **Eligibility/границы.** Выписать конечную таблицу: supported immutable anon/promoted, named static interaction,
   mutable/heap/foreign/realloc, relocation/unknown extent, by-value DST, compound storage и intercepted/shim calls.
   Для каждого supported пути — обязательство и diagnostic/control; для неподдержанного — достижимая граница либо release blocker.
   Flat scratch не исключать. B3/G1/B4/T1b и весь общий cache model не включать в этот fix.
7. **Implementation contract.** Минимальный набор source files/API/schema changes, source→mask→symbol→witness lifecycle,
   порядок M1/M2/M3, dependencies от B1I-A и точки review/STOP. Не требовать обязательно расширить MemLoc, если выбранный
   меньший механизм доказывает тот же контракт; не обходить missing relevance посредством type-only positive shortcut.
   M1 начинает с воспроизведённого immutable gap; M2 не является обязательной новой setter-реализацией после D0.

## Контроли и приёмка design gate

Связать invariants с C1-P и existing controls: оба D0 legal, promoted direct/helper legal и holes слева/справа,
Some/None mask, coalescing/dynamic promoted-local choice, offset/subrange/overwrite, flat whole-copy legal/hole,
typed padding/data, Item true/false returns, zero/nonzero/ZST и legal/frame/clause PFC.
Для каждого: semantic expected, требуемый retained MIR/allocation/operand/property binding и что опровергнет дизайн.
Current false failure у legal не считать доказательством будущего hole negative; baseline и model-candidate отличаются.
Новые model/control outcomes — NOT_RUN; design/review не присваивает proof credit.
Рабочие материалы C1-L могут дать дополнительные lowering facts, но **M0 их не ждёт**; неизвестное обозначить.

Один bounded независимый Luna High review контракта и implementation/controls mapping, без вложенной делегации;
устранить concrete soundness findings. Общий runtime bitmap, новый trusted premise или расширение scope не вводить исподволь.
Design gate готов, если каждый admitted path имеет обоснованный источник state, false сохраняется, lifecycle после reset
определён, unknown не становится true, варианты/выбор/граничные случаи и опровергающие контроли конкретны.
Необоснованный init/mask/identity bridge → STOP с blocker, не оптимистичный M1 handoff.

## Результат и STOP

Только g0 `research/challenge-8/kani-k1/kani3300/m0/`: `MODEL-CONTRACT.md` (≤100 строк),
`IMPLEMENTATION-PLAN.md` (≤50 строк), `CONTROL-MAP.json`, `REVIEW.md`, `RESULT-KANI3300-M0.md` (≤20 строк).
Не менять source clones, active fixtures, diagnostics/workflows или исторические d0a/c1p results. Читать curated g0
материалы; прежнее разрешение D0-A на локальные raw artifacts не переносится автоматически на новую стадию.
Локальные cargo/rustc/Kani/CBMC/Miri, builds/Actions/Cloud dispatch, raw archives/full logs/credentials запрещены;
Python/статические Git/hash/schema проверки допустимы. Никаких PR/issue/комментариев и сторонних PR links.
Research commit `[skip ci]`, author/committer `Tiramisu-Cake <igkharin@gmail.com>` через `git -c`,
stage только `kani3300/m0/`, push g0 без force; concurrent/non-fast-forward → handoff без reset/stash/чужих файлов.
STOP после reviewed design; M1/C1 activation выдаются отдельно. Последняя строка: `READY <sha research-коммита M0>`.
