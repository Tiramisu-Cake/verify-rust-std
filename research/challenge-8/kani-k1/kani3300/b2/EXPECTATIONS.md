# KANI3300 B2 — ожидания до CI

**Все outcomes ниже — прогнозы, не измерения.** Целевой запуск: Miri `nightly-2026-10-23`.
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
