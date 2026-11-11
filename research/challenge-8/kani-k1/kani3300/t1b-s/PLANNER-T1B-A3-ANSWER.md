Рекомендую сначала статический этап Cloud $0, затем один компактный эксперимент; девятирутовый повтор в остаток cap не помещается.
1. Для сильной гипотезы данных достаточно: наблюдаются root-scoped writer DelayedUbPass и последующий reuse изменённого IndexRange::len в том же unit.
   Статически цепочка подтверждается: shared BodyTransformation.cache ключуется Instance; DelayedUbPass анализирует текущие starting_items и перезаписывает cache; GOTO codegen читает transformer.body.
   Это устанавливает возможность переноса контекстной инструментации между roots. Но hit в проходящем into_iter_len не доказывает, какое тело использовал падающий index_range_len.
   Недостающие codegen/presence records и concrete R оставляют причинность его отказа UNKNOWN. OVERSIZED не обесценивает сохранённые записи, но запрещает выводы об отсутствующих событиях.
2. Сейчас статически разобрать compiler_interface::codegen_items, BodyTransformation::body_ref/cache, DelayedUbPass::transform и GotocCtx::codegen_function:
   где заканчивается invariant local transformation, кто изменяет body, когда повторно считается reachability и какой body фактически поступает в emission каждого root.
   Зафиксировать design исправления: свежий transformer на root либо pristine local cache + root-scoped overlay глобальных преобразований, действующий до конца GOTO emission.
   Очистка только на границе unit недостаточна — она уже есть. Не лечить это отключением CheckRef или blanket seed; сам production repair в текущую диагностику не включать.
3. До нового Cloud устранить причину потери нужных records: выбросить payload calibration/adapter, повторные неизменные MIR dumps и поинструкционные zero_ops агрегировать.
   Нужны header unit/stubs/actual order, writer→body hash→consumer, targets/witness, ops и presence/used-body hash для failing root и passing contrast.
   Проверить, различает ли producer actual GOTO consumption и обычный lookup при analysis: нынешний function_presence записывается до global passes и сам по себе не удостоверяет emission.
   При необходимости — отдельная минимальная host-only диагностическая правка с review/tests; semantic operations/cache traversal не менять. Cap 256000 B повышать первым шагом не предлагаю.
4. Один предлагаемый пакет: пять roots в одном invocation, каждому 1m:
   cmp3_into_iter_next (наблюдавшийся writer), cmp3_index_range_len (failing target), cmp3_manually_drop_unsized_len (passing contrast),
   pincheck_calibration_uninit_read_u8 и pincheck_calibration_init_read_u8. Library 919cc3e2 и production CMP2 неизменны; новое diagnostic binding фиксируется отдельно.
   Фильтры: IndexRange::len; cmp3_index_range_len; cmp3_manually_drop_unsized_len. Calibration проверять verdicts, без её MIR-payload; writer сохраняется через контекст событий len.
   Отдельный codegen header/presence и последний writer обязательны; экономить на них ради warmup нельзя. До dispatch проверить, что компактный producer сохраняет эти записи в лимитах.
5. Резерв (5×1+30)×$0.0135=$0.4725 ≤ $0.476; одна попытка, cap не выше остатка. Запас всего $0.0035, поэтому envelope/ledger нужно подтвердить без добавочного overhead.
   Девять roots даже по 1m требуют $0.5265. Не вводить скрытый aggregate timeout или дополнительные invocations ради обхода резерва.
   Root subset меняет контекст: воспроизведение не гарантировано. Если target проходит, это не опровержение исходного механизма и не исправление CMP2; нужен следующий отдельно профинансированный этап.
6. Пакет B из четырёх прежних roots по 1m тоже помещается: $0.459. Но он исключает observed writer и менее полезен для закрытия отсутствующей failing-root цепочки, поэтому сейчас не мой первый выбор.
   По одному root на invocation изолирует общий cache и убирает исследуемое взаимодействие; это будущий control, не основной следующий эксперимент.
7. Если compact trace потребует существенной переделки либо envelope не помещается, остановиться на статическом design, сохранив $0.476. Ещё один обрезанный trace не стоит остатка бюджета.
   Приёмка диагностики: сохраняются controls, есть адресуемая полная цепочка для выбранного target либо точная граница UNKNOWN. Source-reported compile-time evidence не превращать в independent B1/B2 или runtime causality.
