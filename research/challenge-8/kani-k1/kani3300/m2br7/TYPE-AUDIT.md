# R7 Rust source type/signature audit — NOT_COMPILED

Authority: accepted base and committed B0/B1, exact file hashes in SOURCE-MANIFEST.json.
No local cargo/rustc/Kani/CBMC/Miri/build. Pinned rustfmt parses/formats only; review is not a compiler.
B3 E0308/E0277 remain the reason for coordinator build/fmt/clippy as the first gate.

## B0 bootstrap boundary

check_uninit/mod.rs uses KaniFunction::Model(KaniModel::InitializeMemoryInitializationState),
already defined/serialized in kani_functions.rs and resolved by TryFrom<Instance> using the exact
fn_marker. Constant type KaniFunction matches &[KaniFunction]. Existing Begin entry is preserved.
Both ptr_uninit and delayed_ub invoke UninitInstrumenter::run; the shared early guard returns the
original initializer body. No new function signature, model variant, wildcard or harness exclusion.
The skipped body contains only six scalar assignments, no input/user memory/callback. Its two
super::any() calls infer usize from the two main fields. kani_core/lib.rs::any<T:Arbitrary> calls
T::any; arbitrary.rs::trivial_arbitrary!(usize) calls any_raw_internal::<usize> and its existing hook.
Neither user Arbitrary implementations nor user referents enter this fixed closure.

## B1 runtime

MODEL-MAP gives all 15 fields/constructors, the exact twelve-field move and partial reset.
ArgumentBuffer::new()->Self is const, Self=ArgumentBuffer; main Self=MemoryInitializationState.
Every member is initialized; static mut types match their const constructors. No raw pointer,
Option, new trait bound, array, enum, cast, reference or runtime whole-record assignment is added.
All buffer field reads/writes stay in the original unsafe blocks, using scalar place access;
no &mut/& reference to ARGUMENT_BUFFER is created. Main &mut methods and their usage are unchanged.

library/kani_core/src/mem.rs::pointer_object<T:PointeeSized>(*const T)->usize and pointer_offset
with the same signature are the exact source APIs. to_raw_parts gives the existing thin pointer;
store observes it while live; load queries only the live destination. No u64/i64 object ID premise.
All offsets, relative_offset, selected index, counters, signature, LAYOUT_SIZE and array indices
are usize; masks are Layout<N>=[bool;N]. Comparison operands therefore match; assertions/guards
are bool; any() in guards infers bool. usize::MAX has the field type. Literals 0/1 infer usize
from assignments/comparisons. +=1/-=1, wrapping_sub(usize), source-range subtraction and destination
offset addition retain exact base operators/bounds/overflow instrumentation. No new usize/u64/u128
cast or truncation; target width and actual no-overflow paths still require CI. has_witness is
separate bool from saved value; saved value && layout[relative_offset] is bool && bool -> bool.
Witness range establishes relative_offset<LAYOUT_SIZE on source-follow path, while layout equality
is asserted on selected load; zero size cannot have a source witness. All generic parameter orders,
helper signatures/attributes/ABI and source-only algorithms are token-normalized against base.

## B1 compiler and lambda typing

Existing CrateDef::statics yields StaticDef; Vec<_> infers Vec<StaticDef>. iter().copied().filter
uses the same Copy StaticDef API as static_var.rs and the unchanged finalizer. Filter receives
&StaticDef; fn_marker<T:CrateDef>(*static_def)->Option<String> (attributes.rs:1390), as_deref()
gives Option<&str>, equality with Some(marker:&str) yields bool. map over [&str;2] returns
[Option<Symbol>;2], then [main,buffer] destructures it. Instance::from(StaticDef).mangled_name()
is the exact declare_static/codegen_static path. SymbolTable::lookup<T:Into<InternedString>>
(&self,T)->Option<&Symbol> (symbol_table.rs:127); cloned() owns the Symbol, ending lookup borrows.
Symbol.name is public InternedString; assert_ne compares two names without consuming Symbols.

GotocCtx.queries is QueryDb (context/goto_ctx.rs); args().ub_check is Vec<ExtraChecks>, Uninit
is PartialEq/Eq (args.rs). contains(&ExtraChecks::Uninit) is the same condition as UninitPass and
immutable registry admission. At handle_check_contract all reachable items have been declared and
emitted (compiler_interface.rs). Uninit harness reset injection references both objects; absent
objects with enabled instrumentation cause explicit failure. No-uninit + no objects yields an
empty Vec<Lambda>, rather than failing because the library contains marker definitions.

Symbol::to_expr(&self)->Expr (symbol.rs:457), Expr::member<T:Into<InternedString>>(self,T,&SymbolTable)
->Expr (expr.rs:977). The twelve (&str,Type) tuples form one homogeneous array; Type::size_t()
matches codegen UintTy::Usize, Type::c_bool() matches ty::Bool (typ.rs:604,714). target.typ()->&Type
is compared to &expected_type, then target moves into Lambda::as_contract_for(&Type,
Option<InternedString>,Expr)->Lambda (symbol.rs:76); None infers the exact Option type.
Vec<Lambda> type is fixed by the main lambda and push; the empty branch has the same inferred type.
The existing chain(shadow_memory_assign).collect::<Vec<_>>() and FunctionContract::new remain.
New Type import is used; no new lint suppression or potentially unused branch variable.

Main target stays main.to_expr(); buffer target is a typed member lvalue each iteration, never
buffer.to_expr() alone. Constructor/record field set equals the twelve target expressions by
static audit. Public modifies routing after this block, frame checks, clause handling, M1
finalizer/registry, immutable admission/seeding and all original tests have unchanged bytes.
Actual padding/whole-object write scopes are an explicit CI stop condition, not source proof.
