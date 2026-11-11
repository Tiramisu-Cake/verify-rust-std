# KANI3300 B2 — ожидания до CI

**Исходная таблица B2 ниже содержит прогнозы, не измерения.** Дополнение B2b в конце
учитывает CI-сведения, переданные координатором в TASK-KANI3300-B2B.md. Целевой запуск: Miri `nightly-2026-10-23`.
Источник аудита Rust `7189d39d9ce936881b8132c6addeaf3e295cd455` — точная версия цитируемого кода;
соответствие этого SHA указанному nightly здесь не установлено, его сверяет CI через `rustc -Vv`.

## Основания и пределы

- **R-Copy/R-Move:** [Reference, moved/copied types](https://doc.rust-lang.org/reference/expressions.html#r-expr.move.deinitialization)
  различает Copy и перемещение; moved local нельзя читать до reinit. Это правило языка не устанавливает,
  меняется ли byte-init state при конкретном MIR load через raw pointer. Для partial move проверяем отдельный field.
- **M-Assign/M-Call:** [MIR Operand::Move, audit SHA](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_middle/src/mir/syntax.rs#L1311-L1328)
  прямо отмечает неуточненную operational semantics: assignment Move в описанной реализации не очищает bytes,
  а Call может передавать place in-place. Поэтому ожидаемый Miri OK после assignment — не гарантия Rust.
- **I-Call:** [eval_fn_call_argument](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_const_eval/src/interpret/step.rs#L402-L433)
  различает Copy и in-memory Move; [init_fn_call_argument](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_const_eval/src/interpret/call.rs#L434-L445)
  копирует значение перед защитой source. [Miri protection](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/src/tools/miri/src/machine.rs#L1857-L1875)
  записывает uninit в source; функция уже вернулась к моменту наблюдения. Прогноз UB требует Call(Move) именно исходного place,
  не промежуточного temporary. Raw address заранее принуждает source быть memory-backed; адрес callee не доказывает in-place.
- **F-Mem/F-Intrinsic:** [mem::forget body](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/library/core/src/mem/mod.rs#L185-L193)
  — обычный generic body с ManuallyDrop. [LowerIntrinsics::forget](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_mir_transform/src/lower_intrinsics.rs#L43-L61)
  устраняет intrinsic call. Поэтому mem wrapper и intrinsic проверяются раздельно; inlining/lowering меняет прогноз.
- **MU:** [MaybeUninit validity](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html#validity)
  разрешает перенос контейнера с uninit payload, но не чтение uninit как u8. Здесь initialized MU оборачивает non-Copy Word,
  поэтому сам контейнер non-Copy. Обычные union также без Copy. Все наблюдения читают u8, не bool/reference/discriminant.

## По каждому бинарю

`UB uninit*` = прогноз ошибки uninitialized на первом source byte read **при подтвержденном I-Call**;
иной diagnostic (alias/dangling/invalid value) не засчитывается как установленная деинициализация.
`OK*` = прогноз без uninit при подтвержденном указанном lowering.
Колонка «неочевидно» указывает формы, где необходимы MIR/lowering и pinned interpreter, а не один текст Reference.

| Бинарь | Язык / MIR и обоснование | Прогноз Miri | Неочевидно |
| --- | --- | --- | --- |
| copy_assignment | R-Copy: исходник сохраняется; assignment Copy | OK | нет |
| copy_call | R-Copy: by-value Copy не является I-Call Move | OK | проверить Operand::Copy |
| assignment_move | R-Move: local moved; M-Assign сохраняет byte state | OK* | да, язык и operational MIR различаются |
| call_move | R-Move; non-Copy bodyful call, source address взят до вызова; I-Call | UB uninit* | да, source place vs temporary |
| call_move_address_taken | R-Move/I-Call; callee также берет адрес собственного parameter | UB uninit* | да, наличие callee address не решает lowering |
| mem_forget | R-Move/F-Mem: если bodyful Call(Move source) сохранился — I-Call | UB uninit*; OK при устранении/переносе через temporary | да, inlining/MIR |
| intrinsic_forget | R-Move/F-Intrinsic: intrinsic устраняется без очистки source | OK* | да, intrinsic lowering |
| assignment_move_reinit | R-Move затем разрешенный reinit; четыре bytes переписаны в том же local | OK | проверить отсутствие StorageDead/reallocation |
| call_move_reinit | I-Call затем reinit после возврата; очищенные bytes восстановлены | OK | проверить old pointer и lifetime |
| field_projection_move | partial R-Move; M-Assign для src.first | OK* | да, byte state moved field |
| field_call_move | partial R-Move; I-Call для src.first | UB uninit* | да, исходная projection vs temporary |
| field_call_sibling | partial R-Move другого поля; sibling не передан и остается initialized | OK | I-Call не должен очистить соседние bytes |
| maybe_uninit_assignment | R-Move/M-Assign для initialized non-Copy MU | OK* | да, initialized payload, а не uninit control |
| maybe_uninit_call | R-Move/I-Call для initialized non-Copy MU | UB uninit* | да, MU не делает u8-read uninit допустимым |
| maybe_uninit_uninit_control | MU move допустим, source byte не был initialized изначально | UB uninit | это detector control, не свидетельство move-deinit |
| whole_move_source_uninit_c | исторический non-Copy union, R-Move/M-Assign | OK* | да, старое FAILURE не эталон |
| whole_move_source_uninit_rust | тот же assignment, отдельный historical union type | OK* | да, оба union default repr |
| argument_move_source_uninit_c | initialized union R-Move/I-Call | UB uninit* | да, source place vs temporary |
| argument_move_source_uninit_rust | initialized union R-Move/I-Call | UB uninit* | да, source place vs temporary |
| intrinsic_forget_move_source_uninit_c | union R-Move/F-Intrinsic | OK* | да, intrinsic lowering |
| intrinsic_forget_move_source_uninit_rust | union R-Move/F-Intrinsic | OK* | да, intrinsic lowering |
| field_move_constructor_source_uninit_c | ManuallyDrop non-Copy source → union constructor, M-Assign; F-Intrinsic касается union | OK* | да, constructor assignment не bodyful source call |
| field_move_constructor_source_uninit_rust | то же, отдельный historical union type | OK* | да, проверить source temporary |
| field_move_projection_source_uninit_c | ManuallyDrop non-Copy source → raw union field store, M-Assign; F-Intrinsic касается union | OK* | да, отличать source от union destination |
| field_move_projection_source_uninit_rust | то же, отдельный historical union type | OK* | да, оба union default repr |

Критерии интерпретации: `probes/README.md`. Source byte reads volatile, без value-printing; destination reads в assignment
probes наблюдают только заведомо initialized payload. Ни один OK здесь не устанавливает, что общий moved-from Rust code корректен.
Нет measured MIR/Miri verdicts, tool-model changes, formal proof или независимого proof credit; следующий шаг принадлежит CI координатора.

## B2b — прямой in-place Call(Move) на custom MIR

Переданные координатором результаты runs 43109689395/43109978880 записаны в
[TASK-KANI3300-B2B.md](../../TASK-KANI3300-B2B.md): 22 формы дали Miri OK, uninit detector дал UB;
reinit-ошибки оказались Stacked Borrows invalidation. Это source-reported CI facts, не самостоятельно
проверенные здесь evidence. Старые условные прогнозы таблицы B2 не следует выдавать за outcomes.
В частности, обычный `call_move_address_taken` передаёт temporary: он не проверил in-place Move наблюдаемого src.

Новые четыре бинари задают `runtime/optimized` MIR напрямую. Единственный `src: u8` получает `0x51`,
`p = addr_of!(src)` создаёт `&raw const src`, и сам `src` передаётся в `consume(Move(src))`.
После возврата `read_volatile::<u8>(p)` читает ровно этот же байт. Между этими операциями нет source
reinit, StorageDead или смены указателя. `u8` исключает padding, invalid bit patterns и pointer cast.
Copy и Move намеренно используют одинаковый Copy-тип: здесь операнд MIR выбран явно и не выводится
из trait/lowering. В Copy-бинарях `consume(src)` означает `Operand::Copy(src)`;
функции `Copy(src)` в API нет. Callee получает только значение, не `p`; write-вариант volatile пишет `0xA7`
в свой параметр и volatile читает его обратно. Оба варианта возвращают наблюдённый callee byte.

| Новый бинарь | Прогноз pinned Miri | Если исходное чтение завершится |
| --- | --- | --- |
| custom_call_move_read | source деинициализируется; UB uninitialized на post-call source read | печатает callee/source, ожидаемый callee `0x51` |
| custom_call_move_write | source остаётся uninit; UB на том же read; callee write его не восстанавливает | печатает callee/source, ожидаемый callee `0xA7`; видимость записи проверяется значением source |
| custom_call_copy_read | OK, source `0x51`, callee `0x51` | обе величины печатаются и проверяются |
| custom_call_copy_write | OK, source `0x51`, callee `0xA7` | запись в параметр не видна в исходнике; обе величины проверяются |

Обоснование — цепочка интерпретатора **того же audit pin**, а не обещание Reference:

1. [step.rs:402–433](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_const_eval/src/interpret/step.rs#L402-L433):
   Copy даёт `FnArg::Copy`; Move memory-backed place даёт `FnArg::InPlace` при любом значении
   `move_definitely_disjoint`. Взятие raw-адреса обеспечивает allocation именно `src`.
2. [call.rs:421–445](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/compiler/rustc_const_eval/src/interpret/call.rs#L421-L445):
   значение сначала копируется в отдельный callee local, затем исходный InPlace защищается.
   Поэтому callee читает initialized параметр и пишет собственный storage, не восстанавливая `src`.
3. [machine.rs:1857–1875](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/src/tools/miri/src/machine.rs#L1857-L1875):
   защита явно записывает `uninit` в исходное место, в том числе без borrow tracker;
   после возврата оно не восстанавливается. Прогноз для прямого in-place Move — UB, а не OK.

Синтаксис сверен по [mir.rs:211–252](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/library/core/src/intrinsics/mir.rs#L211-L252)
(locals/Copy/Move, assignments, addr_of!, Call) и [примеру runtime/optimized и tuple-return:123–160](https://github.com/rust-lang/rust/blob/7189d39d9ce936881b8132c6addeaf3e295cd455/library/core/src/intrinsics/mir.rs#L123-L160).
CI должен подтвердить exact MIR source place, обе callee операции и диагностическую точку source read.
Alias/dangling/compile error не устанавливает uninit-прогноз; другой diagnostic надо записать отдельно.
Фактические B2b compile/MIR/Miri outcomes здесь **NOT_RUN**, соответствие nightly audit SHA ещё сверяет CI.
Ни прогноз, ни возможный OK не дают общего Rust/Kani proof credit.
