# C1-P: compiler-input controls и границы ABI

Все пункты — **NOT_RUN / спецификация**; compile-ready snippets не заявляются, также это не наблюдение MIR или proof credit. Анализ source только read-only: `/root/kani-fix-3300-p1b1` HEAD `6134e42dd1c65dc980336e7d9455aba02d423edf`, clean. Требуется записывать compiler-produced `Instance.kind`, `body()`, `has_body()`, `fn_abi()`, terminator и MIR-local types. Название Rust функции и наличие похожего source snippet не устанавливают эти свойства.

## Общие требования к контролям

Для каждого semantic control отдельно нужны plain и обычный byte-copy seeded input. По факту фиксировать seed target count, ранее собранные targets/points-to edges и достижение каждого property; отсутствие цели в initial-target collector не заменяет local visitor. В обычном bodyful nonforeign Item caller direct `MaybeUninit<u32>` formal `local[1]` даёт требуемый entry `LoadArgument`; не выводить его из callee formal. Payload-read должен быть реальным `Operand::Copy/Move(*p):u32`; передача `&MaybeUninit<u32>` сама по себе payload не читает. Чтобы доказать достижение later Unsupported, использовать initialized scalar companion и подтвердить успешный Check до diagnostic. Отдельный partial scalar negative показывает, что operand Check реально читает; после его провала не требовать runtime continuation до Unsupported. Bodyful callee-контроли фиксируют `arg_count`, `locals[1..=arg_count]`, return `local[0]`, signature, `FnAbi.args`/PassMode и `Instance.ty()`. Actual order и property reachability подтверждаются transformed MIR/JSON, не выводятся из source spelling.

<a id="fn-def-resolution-err-empty-entry"></a>
### 1. `fn-def-resolution-err-empty-entry`

**Compiler input:** empty-body ordinary nonforeign caller (`bb0` сразу Call) с direct caller formal `local[1]:MaybeUninit<u32>`; сохранить B1IA entry `LoadArgument`. Добавить отдельный pointer formal/local `p:*const u32` и единственный pending scalar arg `Operand::Copy/Move(*p):u32`; destination `()`. `func` должен быть direct `RigidTy::FnDef(def,args)`, не FnPtr; MIR API допускает `Operand::Constant` FnDef и Copy/Move place, только если фактический place имеет FnDef type. Снять actual encoding и доказать, что `Instance::resolve(def,args)` для него вернул genuine `Err`; не конструировать Instance и не подменять resolver.

**Ожидаемое наблюдение:** `LoadArgument(local[1])` → scalar Check `*p:u32` → resolver-Err Unsupported на Call terminator. Проверить единственный Call target и сохранение прежних targets/edges. Local visitor диагностирует Err; failed resolution не становится intrinsic seed.

**Смысл / ограничение:** доказывает сохранение B1IA direct-MU load плюс scalar read до genuine Err/Unsupported. **Достижимость UNKNOWN:** pinned source подтверждает Err ветку, но не конкретный легальный Rust source, создающий direct-FnDef monomorphization Err. Фиктивный FnDef operand/Instance не является control.

<a id="bodyless-shim-and-llvm"></a>
### 2. `bodyless-shim-and-llvm`

Три отдельных subcase: (a) `kind=Shim, body()=None`; (b) `kind=LlvmIntrinsic, body()=None`; (c) `kind=Item, is_foreign_item=false, body()=None`. (c) не заменяет generated Shim. Каждый пустой nonforeign caller имеет `local[1]:MaybeUninit<u32>` (entry load), pointer `p:*const u32`, pending scalar arg `Copy/Move(*p):u32`, destination `()`. Записать actual direct FnDef operand encoding, kind, `has_body()` и `body()`, ABI и target.

**Ожидаемые исходы различны:** (a)/(c) common resolver дают bodyless-kind Unsupported; (b) common resolver даёт LlvmIntrinsic-specific Unsupported. В каждом наблюдать caller `LoadArgument` → scalar Check → соответствующий Unsupported; сохранить prior targets/edges. Не обобщать это как один body unwrap route и не требовать hidden callee effect. Empty drop glue может быть backend fast path, поэтому наличие Instance не означает runtime Call reachability.

**Смысл / ограничение:** отказ до body analysis/transfer для точного kind. **Достижимость UNKNOWN:** нужны реальные compiler-produced direct FnDef callsites с указанными kind/body/ABI; типы Instance являются source API categories, а не доказательством, что legal source достигает их. Bodyless generated Shim особенно требует MIR подтверждения.

<a id="bodyful-shim-direct-shadow-argument-only"></a>
### 3. `bodyful-shim-direct-shadow-argument-only`

**Compiler input:** входной caller сам имеет direct formal `local[1]:MaybeUninit<u16>` (для caller entry `LoadArgument`) и передаёт его одним прямым by-value аргументом настоящему nonempty `Instance { kind: Shim, body(): Some(MIR) }` (не tuple/reference/pointer); есть дополнительный scalar `Copy/Move(*p):u16`, proven initialized для scalar Check, destination `()`. Shadow source имеет initialized и false-mask pair; не делать hole-read до Call — это может замаскировать protocol boundary. Записать caller/callee signature, `FnAbi`, PassMode и locals; callee `local[1]:MaybeUninit<u16>`, `local[0]=()`.

**Caller outcome:** caller entry `LoadArgument` → initialized scalar Check → один Unsupported `without paired argument/return protocol` на Call; нет caller `BeginArgumentTransfer`, `StoreArgument`, source `SetRef(false)` или return load; prior targets/seeds не потеряны. Отдельно статически классифицировать instrumented callee entry: shadow formal Shim не получает paired `LoadArgument`, local visitor размещает Unsupported.

**Смысл / ограничение:** доказывает caller boundary для настоящего bodyful Shim с direct shadow argument и отдельно его entry classification. Не требовать runtime-достижимость callee после caller Unsupported. Tuple-layout negative gap не закрывает. **Достижимость UNKNOWN:** нужен compiler-produced bodyful Shim с таким ABI. FnOnce direct-argument route здесь не подходит: `RustCall` ABI представляет аргументы closure call tuple-ом; требуемый direct MU formal нельзя выводить из такого source. Нужен другой legal compiler-produced Shim либо честный UNKNOWN.

<a id="bodyful-shim-shadow-return-only"></a>
### 4. `bodyful-shim-shadow-return-only`

**Compiler input:** caller вызывает `kind=Shim, body()=Some(MIR)` с обычными аргументами без shadow payload и destination `MaybeUninit<u16>`; callee return `local[0]` имеет этот тип. Записать FnDef encoding, signature/`FnAbi` return pass mode, locals, terminator, точный Instance и оба тела.

**Caller outcome:** local visitor видит shadow return destination и ставит paired-protocol Unsupported до return0 `LoadArgument`/обычных transfer effects. Не требовать destination read после этой diagnostic: normal continuation может быть недостижима. Callee entry — отдельная статическая classification: Shim return local не получает paired `LoadArgument`; не объявлять это исполненным. Для сохранения false нужен отдельный bodyful nonforeign Item transfer control.

**FnOnce constraint:** return-only FnOnce closure с empty tuple args может быть legal route, но exact lowered instance может оказаться `Shim` или `Item`; pinned source fixtures сообщали `Item`, что не закрывает Shim. Записать actual kind/body/ABI, не считать source FnOnce обещанием Shim. **Достижимость Shim UNKNOWN**, если compiler MIR не даст exact instance.

<a id="by-value-dst"></a>
### 5. By-value DST

Boundary input — legal `unsized_fn_params` formal, например `[MaybeUninit<u8>]`/DST-tail, с actual MIR type, dynamic metadata (length/vtable), `FnAbi` PassMode, Instance kind/body и call/return places. Backend представляет by-value unsized argument fat pointer-ом, отдельным от обычного sized shadow payload. `&[T]` не эквивалентен DST by value. Требуется либо доказанный dynamic-extent shadow protocol, либо Unsupported до fixed-size Store/Load; неизвестный extent/return ABI остаётся UNKNOWN. Не синтезировать invalid MIR.

<a id="ordinary-union-constant"></a>
### 6. Ordinary-union constant в by-value StoreArgument

Это **не raw_eq**. Требуемый legal-MIR boundary: by-value обычный union `U` (не `MaybeUninit`) передаётся как аргумент-constant, так что caller visitor видит shadow-bearing union operand и создаёт `MemoryInitOp::StoreArgument { operand: Operand::Constant(..), ... }`. Наблюдать `StoreArgument` → `build_check_for_operation` → `operand_ty`; текущий `operand_ty` для StoreArgument требует Copy/Move place, а Constant попадает в `unreachable!`. В `build_check_for_operation` есть отдельная constant materialization ветка только для `MaybeUninit` storage, это не ordinary union workaround.

Control/spec обязан привязать точные function/argument index, constant kind, union type/layout, actual ABI, call terminator, и доказать legal compiler-produced MIR. Требуемая будущая безопасная граница — явный Unsupported до invariant либо безопасная materialization с сохранением union init mask; никакой synthetic constant/place. **Достижимость UNKNOWN:** legal direct by-value union constant operand в MIR не установлен source spelling-ом; audit answer 8 называет именно этот потенциальный `operand_ty` ICE и указывает на source test/путь, но отдельного воспроизведения не было. Не заменять его MU constant case или raw_eq.

<a id="backend-hook-return"></a>
### 7. Backend-hook intercepted return: `UntrackedDerefHook` в legal PFC

Рассматривать конкретно generated PFC путь: `kani::internal::untracked_deref<T>(&T)->T` помечена `#[kanitool::fn_marker = "UntrackedDerefHook"]`; contract macro использует её при построении modifies target. `GotocHooks::hook_applies` выбирает Kani hook по marker; `UntrackedDeref::handle` генерирует shallow dereference `*arg` в assignment destination. Это backend interception после argument ABI lowering, а не обычное выполнение MIR callee. Требовать legal PFC/modifies root, actual generated Call, marker lookup/hook identity, `T=MaybeUninit<u16>` shadow return, caller destination, exact `Instance.kind/body`, `FnAbi`, нормальный target, и runtime-seeded false-mask witness. DFCC/contract execution path и отсутствие unsupported source transformations фиксировать вместе с legal PFC control; прежний OOM/known limitation не считать семантическим outcome.

Необходимо установить, что hook реально применяется и что вызывающий uninit visitor ожидает paired protocol для этой exact Instance. Backend hook assignment должен сохранить actual source false mask; phantom callee entry Store/Load не подтверждает return. Ожидаемые доказательства — hook selection + MIR instrumentation + call-return/shadow buffer correspondence + наблюдаемая false destination; если full PFC verification недоступна, source-level property остаётся NOT_RUN. **UNKNOWN:** генерирует ли legal PFC/modifies roundtrip именно by-value shadow return через этот hook/ABI и что visitor с backend rewrite связывают return witness. Если парность для actual hook не установлена, требуется pre-effect Unsupported; текущая поддержка не заявляется. Не подменять hook mock/source-name matching.

## Pinned source references

Все digest ниже — SHA-256 полного файла в `/root/kani-fix-3300-p1b1` HEAD `6134e42dd1c65dc980336e7d9455aba02d423edf`; проверены повторным `sha256sum`.

| Путь и строки | SHA-256 | Подтверждает |
|---|---|---|
| `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:46-96, 495-528, 562-592, 666-731, 1143-1146` | `baa2013d98a84784366602ea3f9e63bbbde408816a5a947032267737014e4c5a` | entry MU load, scalar terminator read ordering, bodyless call checks, Shim Unsupported vs Item pairing predicate. |
| `kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:1092-1095` | `baa2013d98a84784366602ea3f9e63bbbde408816a5a947032267737014e4c5a` | `try_resolve_instance` resolves the actual `func.ty(locals)` through shared `resolve_call`. |
| `kani-compiler/src/kani_middle/points_to/points_to_analysis.rs:347-378` | `2ddda690dbfbd57fad47a29ac86a940ca268feb809a1f4aca812d1ff578b6f45` | `FnDef` resolver Err; distinct kind/body resolution outcomes. |
| `kani-compiler/src/kani_middle/transform/check_uninit/delayed_ub/initial_target_visitor.rs:34-53, 115-149` | `be0335143c68812418e549441fed1ac782c85592359d37083076c70c7be80dd5` | seeded Place/Static targets, failed FnDef resolution is not intrinsic seed, previous targets retained. |
| `kani-compiler/src/kani_middle/transform/check_uninit/relevant_instruction.rs:138-165, 307-315` | `e888310d3f46c1bdbfc39a091ddeebd29c9173694da25db0132f654cbf775d37` | StoreArgument `operand_ty` requires place; constant mask helper. |
| `kani-compiler/src/kani_middle/transform/check_uninit/mod.rs:185-211, 700-741` | `a9d700b10177225031d89bf3a813a1bd073fb0f05500bec00ee538874178308e` | only MU constant StoreArgument materialization; argument transfer lowering and selected argument metadata. |
| `kani-compiler/src/kani_middle/reachability.rs:263-292` | `5c285768493d14fd2d6ab6391e41688bc208f071891ea82971a6598e582016a1` | instance collection by kind; not proof that source can obtain a category. |
| `kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs:904-939, 942-1006` | `3cf2e75c171e3ffa78b68f8cf0006e7eee00756822928bdc5cfbab96e9860278` | LLVM intrinsic backend route; FnDef ABI and hook dispatch before regular call codegen. |
| `kani-compiler/src/codegen_cprover_gotoc/codegen/place.rs:394-415` | `0e39f6bcb6f8fdf6089e26f21dd5bfe21077d316b75a15ccde5cd2f1156f78b0` | by-value unsized args use fat pointer representation. |
| `kani-compiler/src/kani_middle/abi.rs:17-75` | `c561c25dc683a41604e0fd9fe36d4f6b5f76deb08baeb8123fe0f8944d517c94` | sized/unsized layout and DST-tail handling. |
| `kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs:747-789, 1700-1720` | `ad73c82580f8f9ba3528ce9b6b371c6a4f717443e31a86b1fad6bad0a2c80d64` | UntrackedDeref shallow return, marker-to-hook dispatch. |
| `library/kani_core/src/lib.rs:665-676` | `bb77d147b03f64586bb38a31edafaddc0c99e3cc3fb65a5c5c541b4fc0198649` | generic `untracked_deref<T>(&T)->T` carries exact hook marker. |
| `library/kani_macros/src/sysroot/contracts/replace.rs:125-145` | `6bd51d3234c0778c5e0a465d1009d4efdee21dc2565e626b6d309f25c6791f05` | PFC modifies macro builds target through `untracked_deref`. |
| `kani-compiler/src/codegen_cprover_gotoc/context/current_fn.rs:410-460` | `1b3843f009b1aea24572a32fefe0d41921197df5530aae6c96ffce34352224e6` | contract-generated closures are discovered via internal helper calls; generated closure semantics need exact path review. |

Матрица/fixture ownership остаётся у main agent. Этот файл задаёт input-binding и UNKNOWN criteria; он не подтверждает, что перечисленные legal MIR формы уже получены или запущены.
