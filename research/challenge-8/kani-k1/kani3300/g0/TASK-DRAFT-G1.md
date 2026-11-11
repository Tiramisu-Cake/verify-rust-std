# KANI3300 G1 — черновик задания, НЕ GO

Runtime Codex. База реализации — финальная принятая часть 1; статические координаты дизайна относятся к `c39cc1121cdb287d9d77c38b87cff6c84c2c8046`. Если финальная часть 1 изменится, до работы повторить diff/rebind, не подменять pin молча. CMP2 не upstream-база.
Цель: произвольный supported-layout union как прямой raw-pointer pointee, whole-storage transfers и bodyful arguments/returns; контракт — `DESIGN-UNION-POINTEE.md`. G2 field-of-struct/array/union и union-in-union не реализовывать. Общий checkbox #3300 остаётся открыт.
G0 выполнен только статически, Cloud $0, все будущие selectors ниже NOT_RUN. Этот документ не регистрирует phase/ledger, не разрешает Build/Actions/PR/issue/comment.

## Реализация и приёмка

1. В отдельном assigned worktree зафиксировать immutable base/tool/profile/runner pins; выписать MIR operation coverage и guards до изменения. Разделить union storage-size/field masks и whole/field operations, затем согласовать argument/return/destination protocol и points-to/delayed-UB.
2. Сохранить byte-shadow witness/copy_by_id и marked MEM_INIT_STATE; не распространять специальные MaybeUninit transmute-правила на U. Непокрытые volatile/typed_swap/select_unpredictable/bodyless/foreign effects должны оставаться явно Unsupported, а не попадать в blanket union check-skip.
3. Перед native gate — targeted static checks и независимый Luna HIGH review exact production diff/dependencies. Все локальные cargo/rustc/Kani/CBMC и builds запрещены; подготовка без dispatch. Для изменённого runner обязательны существующий Cloud preflight и service error-path checks; не менять runner без необходимости.
4. Native acceptance: каждый positive harness SUCCESS без Unsupported; каждый negative — FAILURE **в нужном harness, у нужного чтения/property и типа**, с обязательными diagnostics ниже. Unsupported/OOM/timeout/compile/setup error не засчитывать как expected uninit; mixed fixture не принимает «любую ошибку» за все controls.
5. Сохранять все harness outcomes, source/library/tool/fixture hashes, effective flags и expected-property binding. После terminal Build — Evidence Brief, затем адресные queries при необходимости; никаких raw archives/logs. Native finite outcomes не B2 и не доказательство общего домена.
6. Только после native acceptance — отдельно согласованный core replay; полная upstream regression matrix позже, по процессу итераций. Не менять существующие fixtures/assertions ради gate.

## Native manifest — ровно 20 file selectors

Paths относительно `tests/expected/`; 01–03 — предлагаемые новые fixtures, **ещё не существуют**. Один selector может содержать несколько именованных harnesses; это ограничение числа файлов, не числа obligations. Конкретные новые имена harnesses и negative properties обязательны ниже.
Общие флаги новых fixtures: `-Z uninit-checks --output-format=regular`; без отключения validity/pointer/frame checks. 04–20 сохраняют исходные flags/goldens; PFC/frame selectors сохраняют function-contracts flags.
`D(T)` = `Failed Checks: Undefined Behavior: Reading from an uninitialized pointer of type \`T\``; для legacy 19 допускается исходная property Description с тем же текстом и FAILURE (его golden не переписывать).

| № | File selector | Ожидание / обязательная диагностика |
|---|---|---|
| 01 | `uninit/g1-union-pointee-positive/main.rs` | Все positive harnesses ниже SUCCESS. |
| 02 | `uninit/g1-union-pointee-negative/main.rs` | Каждый negative harness ниже FAILURE с заданным D(T). |
| 03 | `uninit/g1-union-pointee-unsupported/main.rs` | Rejection controls ниже: Unsupported; transmute — отдельная исходная safety FAILURE. Не SUCCESS/uninit. |
| 04 | `uninit/maybe-uninit-wrap-u3-positive/main.rs` | SUCCESS. |
| 05 | `uninit/maybe-uninit-review-positive/main.rs` | SUCCESS. |
| 06 | `uninit/maybe-uninit-initialized/main.rs` | SUCCESS. |
| 07 | `uninit/maybe-uninit-wrap-u3-padding/main.rs` | D(u8). |
| 08 | `uninit/maybe-uninit-wrap-u3-source-read/main.rs` | D(u64), сохранить проверку typed source. |
| 09 | `uninit/maybe-uninit-buffer-u3-plain-negative/main.rs` | D(u16). |
| 10 | `uninit/maybe-uninit-buffer-u3-clause-pfc-negative/main.rs` | D(u16), PFC. |
| 11 | `uninit/maybe-uninit-buffer-u3-frame-negative/main.rs` | `Failed Checks: Check that *var_7 is assignable`, actual user write, frame не ослаблять. |
| 12 | `uninit/maybe-uninit-partial-copy/main.rs` | D([u8; 4]). |
| 13 | `uninit/maybe-uninit-reset-alias/main.rs` | D(u8). |
| 14 | `uninit/maybe-uninit-review-argument-return/main.rs` | D(u16). |
| 15 | `uninit/maybe-uninit-review-overwrite-copy/main.rs` | D([u8; 2]). |
| 16 | `uninit/maybe-uninit-review-overlap-copy/main.rs` | D(u8). |
| 17 | `uninit/maybe-uninit-review-repeat-local/main.rs` | D(u64). |
| 18 | `uninit/maybe-uninit-review-reset-zst/main.rs` | D(u64). |
| 19 | `uninit/unions.rs` | Исходные 7 SUCCESS + 7 FAILURE; failing names/types см. ниже. |
| 20 | `uninit/uninhabited-union-field/uninhabited-union-field.rs` | `read_init_ok` SUCCESS; `read_uninit_bytes_should_fail` D(u64), без crash. |

## Содержание 01/02: именованные пары

Использовать `#[repr(C)]` и Rust-repr U, raw const/mut pointer paths, initialized assertions с наблюдаемым результатом. Каждая указанная вариация — самостоятельный harness; suffix обозначает вариант, не wildcard selector. Unwritten payload получать через **whole** `U { z: () }`, а не неподдерживаемый MaybeUninit<U> transmute. Адреса/offsets/size использовать через rustc/MIR/стандартные layout APIs, без ручной схемы Rust repr.

| Positive harness в 01 | Negative harness в 02 | Различающее действие / диагностика negative |
|---|---|---|
| `written_c`, `written_rust` | `unwritten_c`, `unwritten_rust` | Записать u32-поле vs ZST-created payload; direct `(*p).wide` → D(u32). |
| `wide_then_narrow_field_c`, `wide_then_narrow_field_rust` | `narrow_then_wide_c`, `narrow_then_wide_rust` | Wide initialized, затем narrow field-write сохраняет хвост; свежий narrow union → wide read D(u32). |
| `whole_copy_c`, `whole_copy_rust` | `whole_copy_partial_c`, `whole_copy_partial_rust` | По отдельности `*dst = *src`, Copy/Move MIR, `ptr::copy`, `copy_nonoverlapping`; частичный source вместо initialized dest → D(u32); self/overlap positive, valid bounds/preconditions. |
| `whole_overwrite_c`, `whole_overwrite_rust` | `whole_reset_c`, `whole_reset_rust` | Whole wide constructor vs whole narrow constructor поверх старого wide state → D(u32); повторять через alias. |
| `argument_return_c`, `argument_return_rust` | `argument_return_partial_c`, `argument_return_partial_rust` | Bodyful noinline identity, два union-аргумента с разным state/size, вложенный call, повторные вызовы/переиспользование destination; partial return → D(u32). |
| `padded_typed_c`, `padded_typed_rust` | `padded_byte_c`, `padded_byte_rust` | Padded struct через ManuallyDrop и typed subfield read vs byte-read padding → D(u8); whole-copy/return не инициализируют padding. |
| `array_field_c`, `array_field_rust` | `array_field_unwritten_c`, `array_field_unwritten_rust` | Поле `[u16; 2]`, также `[Padded; 2]`/`[(); 2]`; unwritten u16 → D(u16); padding-byte вариант → D(u8). |
| `zst_field_no_reset_c`, `zst_field_no_reset_rust` | `zst_whole_reset_c`, `zst_whole_reset_rust` | Initialized wide + field `z=()` сохраняет payload; whole `U { z: () }` сбрасывает payload → D(u32). |
| `align_tail_copy_c`, `align_tail_copy_rust` | `align_tail_reset_c`, `align_tail_reset_rust` | U с `[u8; 5]`/u32 имеет rustc extent больше max field; write_bytes на полном extent, copy/return, читать хвост bytewise; whole narrow reset поверх старого full state → tail-read D(u8). |
| `address_only_c`, `address_only_rust` | `address_no_bless_c`, `address_no_bless_rust` | addr_of!(U)/addr_of!((*p).field) без чтения допустим; взятие адреса не лечит unwritten payload → D(u32). |
| `pointer_alias_c`, `pointer_alias_rust` | `pointer_pointee_uninit_c`, `pointer_pointee_uninit_rust` | U хранит initialized `*mut u32`, затем field write/copy/move/call/return; pointer-value read допустим, deref uninitialized pointee → D(u32). |
| `pointer_delayed_c`, `pointer_delayed_rust` | `pointer_delayed_partial_c`, `pointer_delayed_partial_rust` | Через union-held alias скопировать partial storage в typed u32 local; различающий последующий **local** read → D(u32); separate uninitialized pointer-field read → D(*mut u32). |

Для подвариантов copy/array/pointer использовать отдельные harness suffixes (`_assign/_move/_copy/_nonoverlap`, `_padded/_zst`, `_field_unwritten`); фиксировать их exact inventory до review/dispatch, не добавлять file selectors. Для overlap source-state захватывается до overwrite. Negative pointer-value control не должен доходить до invalid/null deref вместо нужного init-check.

## Rejection controls 03 и сохранение старой семантики

- `reject_struct_field`, `reject_array_element`, `reject_union_in_union`, `reject_manuallydrop_union`: Unsupported, `Cannot determine layout for a type that contains union ... as a field`; не считать успехом G1.
- `reject_niche_enum`, `reject_variant_padding`: Unsupported с `Enum with niche encoding` / `multiple variants that have different padding`; валидный Rust fixture должен доходить до layout rejection, не compiler error.
- `reject_fn_pointer_field`, `reject_indirect_call`, `reject_bodyless_transfer`: Unsupported type / unresolved call / shadow-carrying transfer without MIR body. Fn-pointer guard проверяется до layout shortcut; bodyless возврат без args тоже должен отказать.
- `reject_union_transmute`: сохранить существующий `TriviallyUnsafe`/FAILURE `Transmuting between types of incompatible layouts.` для generic U↔T (это текущая safety-диагностика, **не** ожидаемый uninit и не новое разрешение transmute); `reject_init_predicate`: Unsupported `using initialization predicates on unions`.
- `reject_typed_swap`, `reject_select_unpredictable`, `reject_foreign_mutation`: явный Unsupported с обязательными proposed messages соответственно `Kani does not support typed_swap of union storage.`, `Kani does not support select_unpredictable of union storage.`, `Kani does not support foreign mutation of union storage without an effect model.` Это требования к новым guards/goldens, не утверждение об их наличии в части 1; до gate закрепить exact fixture/property/message binding на immutable candidate.
- Selector 19 сохраняет failures: `basic_union_should_fail`, `union_update_should_fail`, `cross_function_union_should_fail::helper`, `multi_cross_function_union_should_fail::sub_helper`, `cross_function_multi_union_should_fail::helper` — u32; `union_complex_subfields_should_fail` — u16; `basic_multifield_union_should_fail` — u128. Остальные семь harnesses SUCCESS, как исходный golden.
- `uninit/fixme_unions.rs` — TODO без golden: pointer_should_pass/fail использовать как образец новых raw controls; его field/nested/transmute harnesses не объявлять прошедшими. Прочитаны также `union/{static_union,static_union2,union_transmute}.rs`: сохранять исходные flags/семантику, включая намеренную assertion failure static_union2. Они вне bounded manifest 20 и нужны в последующей полной регрессии; generic transmute под `uninit-checks` этим не разрешается.

Предложение cap: targeted native gate **до $0.80** при подтверждённом coordinator envelope после preflight; full matrix/core replay — отдельные разрешение, окно и cap после native acceptance. Это предложение, не резерв/авторизация и не обещание уместить любой timeout/объём harnesses; если envelope не помещается, вернуть точную оценку до dispatch, не сокращать controls или timeout ради cap.
