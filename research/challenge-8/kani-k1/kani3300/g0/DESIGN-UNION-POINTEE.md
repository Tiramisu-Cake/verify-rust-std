# KANI3300 G0 — произвольный union как raw-pointer pointee

Статический дизайн, 2026-11-11; Runtime Codex, Cloud $0; компиляция/проверка NOT_RUN, proof credit NONE.
Контракт: `TASK-KANI3300-G0.md`; прочитан весь `PLANNER-3300-SCOPE-ANSWER.md` по пути из задания, особенно п.3–5.
База G1 — часть 1 `c39cc1121cdb287d9d77c38b87cff6c84c2c8046`, main — `bf9c58e662`; CMP2 `b1f0105c03` — только исследовательский reference, не база и не accepted evidence.
Все ссылки ниже — строки **c39cc1121**, не текущего рабочего дерева Kani; `U/` = `kani-compiler/src/kani_middle/transform/check_uninit/`, `P/` = `kani-compiler/src/kani_middle/points_to/`.

## Карта запретов и готовых механизмов

- `U/mod.rs:383–389`, `build_get_and_check`: любой `PointeeLayout::Union` при raw-read → Unsupported; TODO про intersection масок не является корректным правилом чтения целого union.
- `U/mod.rs:548–577`, `build_set`: union без `operation.union_field()` → Unsupported; известное поле использует его маску, расширение до полного storage есть только у MaybeUninit.
- `U/ptr_uninit/uninit_visitor.rs:732–747`, `visit_place`: deref + чтение union-field → Unsupported, исключение только для lang-item MaybeUninit; затем CheckRef выбранного place.
- `U/ty_layout.rs:440`, `data_bytes_for_ty`: UnionAsField при рекурсивном обходе; блокирует union-in-union, union в struct/tuple/array и ManuallyDrop<union>. `visit_statement`, `uninit_visitor.rs:421–431`, сохраняет явный отказ.
- `U/ty_layout.rs:46–68,145–165`: уже есть `PointeeLayout::Union { field_layouts }`, padding-aware маски каждого поля; `maybe_size()` берёт **max размера поля**, не rustc size union с хвостом выравнивания.
- `U/ty_layout.rs:122–143`: `maybe_uninit_storage` узнаёт только MaybeUninit и плоский array/slice слотов; `for_storage` строит all-byte extent после проверки inner layout.
- `U/mod.rs:163–190,218–241`: только эти storage-типы получают constant init-mask, storage-copy и защиту от generic SetRef; arbitrary union идёт через `from_ty`. `build_copy:626`, `build_assign_union:712`, `build_argument_operation:659` зависят от `maybe_size`.
- `uninit_visitor.rs:63–78,106–108,644–658`: union уже участвует в argument store/load; **return/destination** (`508–520,696–704`) ограничены MaybeUninit. Bodyless shadow-arguments уже Unsupported (`495–505`).
- `uninit_visitor.rs:124–225,355–393`: reusable constant mask, AssignUnion, CreateUnion, field SetRef; обычный AssignUnion пока After, storage-assign захватывает адреса Before.
- Дополнительные границы: `ty_layout.rs:278–281,342–348,430–437` — niche/different-padding enum и unsupported types; `kani_intrinsics.rs:359–368` (в `kani-compiler/src/kani_middle/transform/`) — init predicates union Unsupported.

## Домен G1

- Прямые `*const U`/`*mut U`, local U и bodyful by-value argument/return U; поля: скаляры разной ширины, поддерживаемый padded struct/tuple, ManuallyDrop<T>, ZST-arm, raw-pointer, фиксированные массивы поддерживаемых элементов, включая padded/ZST элементы.
- `repr(C)` и Rust repr: размеры, alignment, stride, offsets/проекции только rustc; адрес выбранного MIR place авторитетен. Нельзя предполагать нулевой offset Rust-union поля или размер union = max(field size).
- G2: U как by-value поле struct/tuple/union или элемент array/slice, включая wrappers; это не то же самое, что array внутри U. Pointer на U внутри U не является вложенным storage и не требует обхода pointee layout.
- Unsupported: union с любым неподдерживаемым by-value полем, неподдерживаемые enum-схемы, fn-pointer/indirect/virtual call, unknown/dynamic layout, bodyless transfers без модели, typed_swap/select_unpredictable storage без модели, generic union init predicates и transmute U↔T. Неоднозначная constant mask → Unsupported.
- Проверять тип/рекурсивную форму до ABI shortcut (включая ZST/fn-pointer); поддержка layout не отменяет validity, provenance, alignment, bounds, frame и иных checks. Существующие MaybeUninit↔T transmute-исключения (`uninit_visitor.rs:228–285,819–858`) остаются lang-item-specific.

## Семантика без ложного SUCCESS

- Состояние — byte-shadow полного rustc extent U, без active tag и без единой маски «union initialized». Whole-value raw load/assign/copy/move переносит состояние, включая false bytes; не требует all-fields/union/intersection-mask. Пропуск init-check допустим только для поддержанного, парного storage-transfer, а не для произвольной операции.
- Создание/whole-overwrite `U { f: value }`: заменить **всё** состояние extent U, установить data-mask typed f после обычных source checks, padding и остальной хвост false. Whole-copy другого U переносит его состояние вместо слияния со старым destination.
- Запись `(*p).f = value` меняет только rustc extent **поля**: typed data true, padding этого поля false; байты вне него сохраняются. Запись subfield меняет его extent, не всё f/U. Инициализированный широкий хвост после narrow field-write сохраняется; после whole `U { narrow: ... }` сбрасывается.
- Чтение f требует data-mask именно читаемой проекции, не всех соседних subfields; typed padding не читается. Byte-read требует каждый затронутый байт, включая padding. Перекрывающиеся поля используют одно shadow-хранилище.
- ZST field-write не меняет payload; whole `U { z: () }` сбрасывает весь payload. Повторная инициализация/overwrite, self-copy и overlapping `ptr::copy` не сохраняют старые false/true ошибочно; `copy_nonoverlapping` сохраняет свой precondition.
- Bytewise copy переносит точный state и rustc stride/extent; bytewise write_bytes инициализирует затронутые байты. Typed field transfers не благословляют padding. Адреса/IDs source/destination фиксируются до возможного overwrite; возврат не разыменовывает умерший stack slot.
- Return-buffer: один общий predicate storage-transfer для аргумента, входа, return-index 0 и destination; index 0 forced, аргументы 1-based/nondeterministic, match consumed, размер сверяется. Сохранить witness source и reset overwritten destination из `mem_init.rs:130–152,404–453`.
- Pointer-field: initialized pointer bytes ≠ initialized pointee. При чтении pointer-value проверить его bytes; дальнейший deref — layout pointee, последующий typed local read — delayed-UB. AddressOf не читает и не инициализирует payload; generic Set/SetRef при взятии адреса, drop и delayed-UB не должны затирать storage-state.
- `P/points_to_graph.rs:131–175` уже объединяет поля в root-node и монотонно сохраняет aliases; `points_to_analysis.rs:142,388,400,448,534,608` покрывает modeled assignments/copy/aggregate/call/return. Переиспользовать эту консервативную модель; не удалять stale aliases и не добавлять assumption об initialized pointee.
- Проверить достижимость union-held pointer через create/field write/Copy/Move/arguments/return и byte-copy до delayed targets (`U/delayed_ub/mod.rs:61`); `instrumentation_visitor.rs:112–115,198–207` должен сохранять Unsupported calls и checks, но generic SetRef не должен благословлять union storage. Foreign mutation без effect model остаётся вне домена с явным отказом.

## Точки изменения, размер и интерфейсы G2

- `ty_layout.rs:PointeeInfo::{from_ty,for_storage}`, `PointeeLayout::maybe_size`: разделить storage extent и typed read-mask; хранить rustc union size и field projection/extent/mask отдельно, рекурсивно валидировать supported domain. Не заменять MaybeUninit lang-item predicate на `is_union` повсюду.
- `uninit_visitor.rs:{visit_statement,visit_ordinary_assignment,visit_place,visit_rvalue,visit_terminator,find_all}`: классифицировать whole-transfer/whole-create/field-store/address formation; обобщить return/destination/constant-buffer paths и парную source capture; сохранить unsupported intrinsic/bodyless guards.
- `mod.rs:{build_check_for_operation,build_get_and_check,build_set,build_copy,build_assign_union,build_argument_operation}` и `relevant_instruction.rs:MemoryInitOp`: explicit operation purpose/range; убрать только покрытые raw-union guards. Generic Set к union без известного смысла должен отказать, а не initialize-all.
- `library/kani_core/src/mem_init.rs:{set,copy_by_id,store_argument,load_argument}`: reuse byte-shadow и buffer, расширять лишь если необходим range/extent; сохранить nondeterministic witness, consume/size checks и DFCC exemption только MEM_INIT_STATE, не user memory.
- G2 hook: descriptor `{storage_size, projected_offset/extent, read_mask, children/field identity}` + операции whole-transfer, replace-whole, write-projection и typed-read; composition offsets/strides проверяется rustc и границами. Сегодня nested child → Unsupported; позднее recursive product/union node без изменения buffer ABI/byte semantics.
- CMP2 `ty_layout.rs:76–85,248–298,478–511` полезен разделением read/storage/padding и checked ranges; его disjoint product partition/overlap rejection нельзя переносить на перекрывающиеся union arms. Не переносить CMP2 целиком и не считать его native acceptance установленным.
- Оценка добавочной дельты: примерно 350–800 production и 450–1000 test/golden строк, 7–10 production файлов; диапазон условный до MIR-аудита raw-write/volatile/constant и native диагностики. Новый points-to model или ABI redesign может выйти за него и требует отдельного решения.
- Главные риски ложного SUCCESS: initialize-all при addr_of/field write; stale tail после ZST/whole reset; max(field size) вместо size(U); потерянный return/alias; обход validity/transmute/unsupported guard. Различающие controls и ≤20 selectors — в `TASK-DRAFT-G1.md`; G0 не подтверждает поддержку или native PASS и не закрывает весь #3300.
