# KANI3300 U3 — статический разбор регрессии до repair
Кандидат Kani `3fd6f408e1d565ba65aaeb86c0c4ad0bbc57ab52`; база U1 `546bcf30379b9b2894f94b1305d5277cc5b4574c`, production delta +111/−13.
Вход координатора U3-REGRESSION.md: все harness Kani FAILED, включая прежние positive; точные Failed Checks пока недоступны.
Наиболее вероятен новый неподдерживаемый layout всего ghost-state при самоинструментировании setup; это гипотеза, не установленная причина build.
1. Setup вызывается в каждом harness (`kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/mod.rs:60–64,100–138`).
`InitializeMemoryInitializationStateModel` отсутствует в `check_uninit/mod.rs:72–90` SKIPPED_ITEMS; остальные основные mem-init models исключены.
Новый `MEM_INIT_STATE.argument_buffer=None` — `library/kani_core/src/mem_init.rs:231`, тип поля Option<ArgumentBuffer> — :40.
Прямое присваивание None само не вставляет общий enum-check: `check_uninit/ptr_uninit/uninit_visitor.rs:412–440,305–376`; эта часть гипотезы 1 не подтверждается.
Но raw-pointer constant со static provenance вставляет Set перед доступом (`uninit_visitor.rs:762–779`), в том числе потенциально на весь MEM_INIT_STATE.
Его новый Option имеет разные data masks None/Some; рекурсивный layout отклоняет такие enum (`check_uninit/ty_layout.rs:320–349`).
Set whole-state → layout error → Unsupported/assert false (`check_uninit/mod.rs:205–252`) объяснил бы общий ранний отказ, если MIR содержит этот static-pointer operand.
Сам operand/точка его исполнения пока не привязаны к native MIR; проверить Failed Checks на MemoryInitializationState/Option и «multiple variants ... different padding».
2. disable_checks(pointer) допустим на методах и локален: `codegen_cprover_gotoc/codegen/span.rs:140–176`, `context/current_fn.rs:126–159,216–219`.
Location cache сбрасывает function/pragmas (`codegen/span.rs:46–89`); глобального отключения нет. Это не объясняет регрессию всех harness.
3. Новый SetStorage только для Cast(Transmute) с exact T/MU или array T/N, size и Sized-mask (`uninit_visitor.rs:150–163,230–248`).
Обычные MU::uninit aggregate/repeat не изменены; MU<u8>→u8 не подходит новому matcher. Blanket Set для каждого assignment нет.
Новый no-MIR guard (:493–505) требует shadow-carrying argument; initializer без аргументов его не активирует. Исходные typed-read checks сохранены (:819–826).
4. Конкретный runtime unreachable: `library/kani_core/src/models.rs:202–208`, ToISize<usize>: TryInto Err → offset-overflow safety check → unreachable!.
OffsetModel вызывает to_isize (:110–118); MIR Offset заменяется этим model (`kani_middle/transform/rustc_intrinsics.rs:114–140`).
Условие этой ветки — offset>isize::MAX; p.add(1) сам его не удовлетворяет. Наличие Description в regular-выводе не доказывает достижимость/FAILURE.
Другой runtime site — `library/kani_core/src/lib.rs:475–480` any_modifies (контракты); источник observed сообщения остаётся UNKNOWN.
Текст формирует `library/std/src/lib.rs:218–244`; MIR Unreachable кодируется другим текстом «unreachable code» (`codegen/statement.rs:512–515`); host unreachable! не runtime property.
Минимальный fix-кандидат после подтверждения setup-пути: добавить InitializeMemoryInitializationStateModel в SKIPPED_ITEMS общего UninitInstrumenter (local+delayed).
Это исключает самоинструментирование trusted setup, сохраняет выбор tracked byte, buffer reset, numeric return transfer и все пользовательские checks; native validation ещё нужна.
Если whole-state layout достигается вне setup, вариант 2: вернуть отдельный ARGUMENT_BUFFER, дать второй private static marker и собрать оба ghost targets в `codegen_cprover_gotoc/codegen/contract.rs:142–170,229`.
User modifies targets/флаги оставить прежними; reset отдельного enum выполнять только в исключённом setup/model, иначе повторится тот же риск.
Контроли repair после reader fix: минимальный empty/uninit harness, прежние review-positive, точные Failed Checks всех пяти U1T negatives, plain/PFC/clause и outside-modifies FAILURE.
Production/request/patch не менялись; repair не подготовлен и не диспатчен. Нужны actual Failed Checks/MIR binding для выбора минимального fix, затем отдельный GO.
Координатор, вопрос
