# KANI3300 SEL0 — select_unpredictable (статический дизайн)
Дата: 2026-11-11; Runtime Codex; Cloud $0; реализация/компиляция/верификация NOT_RUN.
Исследование: Kani baseline `f046b70644e113be0df9c22c2e6ea44a65a57566`, v2 snapshot `81dd85bfce67226e283fdd9a156932e32ece080b` (только `git show`, не финальная accepted base).
Core: research HEAD `becc9621ec6cae4669275e2c80568c18ea65b382`; пути ниже относительно Kani, кроме `library/core` этого worktree.
U2 RESULT сообщает U7 select Unsupported @ hint.rs:871 и два assignable failures; это source-reported контекст, не новый CI evidence/credit.

## Путь и существенная граница
- `library/core/src/hint.rs:838,844,860,871,872`: T помещён в два MaybeUninit; два intrinsic выбирают *mut T для guard/drop.
- **`hint.rs:885` вызывает третий intrinsic над MaybeUninit<T>**, затем assume_init: даже wrapper::<u8> требует storage-result transfer.
- `library/core/src/intrinsics/mod.rs:729,749`: runtime строго `if condition { a } else { b }`; intrinsic забывает второй arm; wrapper сам обеспечивает drop.
- `kani-compiler/src/intrinsics.rs:242,542`: from_instance не распознаёт имя, fallback даёт Unimplemented; добавить SelectUnpredictable, проверить `(bool,T,T)->T` и равенство T.
- `kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs:922,931` и `kani_middle/reachability.rs:279,288`: intrinsic с доступным необязательным fallback body идёт обычным вызовом/collection; иначе backend intrinsic.
- Fallback уже выражает правильный runtime-выбор; наличие конкретного MIR body/must_be_overridden в будущем запуске подтвердить, по исходнику не объявлять measured binding.
- `codegen_cprover_gotoc/codegen/intrinsic.rs:262,279,754`: исчерпывающий match требует новой ветви; на override-пути — условное выражение/ветвление с записью ровно одного arm в place, без nondet выбора и без deref pointee.

## Scope 1 и инвариант
- Разрешить обычные инициализированные scalar (bool/char/int/float) и thin raw-data-pointer значения с поддерживаемой маской; исключить fn-ptr, ref, fat-pointer, aggregate, storage/union/enum.
- Runtime возвращает конкретный arm; статически `PT(dest) ⊇ PT(a) ∪ PT(b)` до fixed point, condition не даёт alias. Учитывать Copy/Move, projections, constants, обе mutability.
- Pointer value не равен pointee: выбор не читает/не инициализирует/не сбрасывает pointee, не сливает их runtime shadow; null/dangling может быть выбран без dereference.
- Сохраняются проверки самих operand reads и последующих dereference/validity; scalar-result не оправдывает blanket initialization произвольного storage.
- Для MaybeUninit/частичного storage отдельный инвариант: `shadow(dest,i)=shadow(condition ? a : b,i)` для каждого byte, включая padding; выбранный pointer payload также сохраняет aliases.
- Пока такого transfer нет, любая storage-result форма даёт явный operator-specific Unsupported **до** generic return/buffer handling; не добавлять select безусловно в can_skip_intrinsic.
- Поэтому Scope 1 оставляет третий вызов реального hint-wrapper и U7 открытыми; wrapper SUCCESS нельзя обещать после одних pointer changes.

## Все потребители распознавания
- `kani_middle/points_to/points_to_analysis.rs:200,204,298`: intrinsic shortcut обходит обычную body propagation; Unimplemented — no-op. Новая ветвь union successors operands[1]/[2] -> destination, по существующему extend-pattern :205; не args[0].
- Тот же файл :399 описывает successors_for_operand; переносить referents, а не добавлять адреса arm-slots дополнительным уровнем indirection. Проверить alias graph для обеих branches.
- `transform/check_uninit/delayed_ub/initial_target_visitor.rs:69,105,113`: select не пишет pointee и не создаёт layout mismatch; новый target не нужен, wildcard no-effect корректен; casts/copy после select сохраняют прежние targets.
- `delayed_ub/mod.rs:70,92,113`: targets превращаются в successors points-to; неполный alias graph теряет объект instrumentation.
- `delayed_ub/instrumentation_visitor.rs:110,131,168,198`: отдельной Intrinsic-классификации нет; fnptr guard, get-intersection и set-common-ancestor оставить, новый union graph обеспечивает coverage.
- `ptr_uninit/uninit_visitor.rs:494,495,507,524,610,871`: распознать select до generic storage/buffer ветвей; Scope 1 no pointee effect, все остальные формы Unsupported. Forget исключение не расширять на select-storage.
- `ptr_uninit/uninit_visitor.rs:719,762,782`: обычный обход operands/places сохраняет raw reads/union checks; не обходить его ради поддержки select.
- `transform/rustc_intrinsics.rs:181,183`: wildcard «handled in codegen»/fallback уже корректен; новая model substitution не нужна.
- `kani_middle/codegen_units.rs:931,933`, `intrinsics.rs:192,230`: SIMD-only gate/name filter и classifiers select не затрагивает; wildcard non-SIMD корректен.
- `transform/check_values.rs:436,445,486,502,802`: отдельное распознавание по имени, wildcard no-effect корректен: select не создаёт новые битовые значения; deref/transmute validity оставить (не закрывает #3762).
- Пути: `ptr_uninit/`, `delayed_ub/` относительно `kani-compiler/src/kani_middle/transform/check_uninit/`; `transform/` относительно `kani-compiler/src/kani_middle/`; `points_to/`, `codegen_*` относительно `kani-compiler/src/` с указанным kani_middle где нужен.

## Shadow v2 и риск ложного SUCCESS
- `library/kani_core/src/mem_init.rs:19,34,113,130,400,426`: один MEM_INIT_STATE, плоские fields, copy/copy_by_id и парные argument store/load (return index 0); переиспользовать без Option/enum, второго static и изменений SKIPPED_ITEMS (`check_uninit/mod.rs:73`).
- Следующий storage scope может использовать существующий fallback и v2 Store/Load **только для этого intrinsic с подтверждённым body**, либо conditional copy из live selected source; выбрать один owner transfer, без двойного blessing/transfer и stale buffer.
- Оба варианта отдельно требуют review witness coverage для Copy/Move, overwritten destination/padding и live source IDs до переноса; generic allowance всех bodyful intrinsics запрещён.
- Контрпример: два u64; `p=select(c,&raw mut x,&raw mut y)`; cast p -> *mut Pad{u8,u32}, size 8; write Pad; прочитать x при c=true / y при c=false. Padding Pad не инициализирован, но является data u64.
- Без dest→обоим referents target cast p может иметь пустые successors, исходный u64 останется без delayed CheckRef; снятие Unsupported допускает false SUCCESS. Это статическая гипотеза, не воспроизведённый результат.
- Подмена runtime выбора union shadow, blessing обоих pointees, transfer одного arm или storage без selected-byte witness также несостоятельны.
- Микрофикстуры и source-backed ожидания: `MICROFIXTURES.rs.txt`, `TASK-DRAFT-SEL1.md`, `NATIVE-MANIFEST-DRAFT.json` (19 exact selectors); всё NOT_RUN.
