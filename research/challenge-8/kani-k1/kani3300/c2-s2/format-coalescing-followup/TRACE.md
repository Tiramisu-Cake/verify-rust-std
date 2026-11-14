# S2 follow-up — AllocId, emitted symbol and qualification

Scope: static source reconstruction, not a compiler run. Exact Kani candidate bf8170b28afb682f8dd55a94199caa247736d8fa; production logic remains f96ad419bc. The supplied coordinator summary records four old controls PASS on both old and new register. They are NONDISCRIMINATING; it does not contain MIR, AllocId numbers, binding maps or descriptor traces. It does **not** establish that coalescing failed to occur. Numeric IDs and full symbol strings for those runs are UNKNOWN; they cannot be recovered honestly from PASS alone.

## Exact Kani mapping

- `context/goto_ctx.rs:79`: alloc_map is `FxHashMap<Allocation, String>`, not keyed by AllocId. Allocation equality includes Option bytes, provenance IDs, align and mutability, with no semantic source type. Different byte contents/holes/align/mutability/relocations cannot coalesce merely because they print similarly.
- `codegen/operand.rs:449-478`: a Memory key or anonymous Static key K is materialized using proposed name `full_crate_name()::{K:?}`. `codegen_const_allocation:573-586` returns the name already stored for an equal Allocation, ignoring the later proposed name. Both insertion and reuse call `bind_immutable_allocation(K, allocation, actual_address)`.
- `codegen/operand.rs:685-713`: emitting T's initialized pointer slot recursively materializes its referent. T[0] at runtime reads that pointer slot; T[0] is not itself a new compile-time AllocId constructor. `static_var.rs:18-29` emits T under its own mangled name. Its relocation-bearing array allocation is different from the one-byte referent and cannot be the same alloc_map key.
- `anonymous_allocations.rs:32-82`: qualification is attached to the provenance key of a MIR constant whose **carrier type** is an immutable reference to the supported whole referent, offset zero/exact extent/Freeze. It is not attached automatically just because an allocation can be read through a shared reference later.
- `immutable_allocations.rs:151-167`: prepare visits original bodies of both reachable functions **and named statics**. It does not just inspect the harness. The emitter also observes constants at `operand.rs:93-97`. Finalize looks for any exact qualifying source per key; the vector of unqualified aliases cannot cancel a qualifying origin.

Thus the source-level symbolic trace (not observed numeric trace) is:

| Object/use | Symbolic key | alloc_map / symbol | Qualification source |
| --- | --- | --- | --- |
| harness direct &5 | D, provenance of its promoted &u8 carrier | A=(bytes [Some(5)], no relocations, align 1, Not); S=alloc_map[A] | Whole u8 carrier gives frozen_origin=Some(u8) |
| T initializer's &5 / later T[0] | N, provenance in eval_initializer(T)'s pointer slot | If its Allocation equals A, same S, irrespective of D=N or D!=N | The initializer's separately visited &u8 constant can itself give Some(u8) for N |
| T itself | Named-static identity | Its mangled T symbol; pointer-slot Allocation has provenance N, so differs from A | Relocation-bearing T is not admitted as a scalar immutable seed |

If D and N are distinct with equal A, S is the first cache name, either crate::D or crate::N (or another earlier exact A cache entry). Later keys bind to that actual symbol. Exact emitted order is fingerprint-sorted by reachability, not guaranteed by let statement order. If rustc reuses D=N, there is one key with shared origin evidence instead. Either way, if both keys are qualifying, the old descriptor equality sees no false/true disagreement.

## Why the original repro can pass

The audit's informal account omitted the original static initializer body from qualification collection. Ordinary rvalue promotion turns its `&5` into a ref-typed constant, and prepare can qualify N from that body even though the runtime T[0] path supplies no origin. This gives two qualifying keys (or one already qualifying key), so coalescing is compatible on the old code as well. This is a static explanation consistent with both CI results, **not an observed account of the exact lowering**. The summary alone cannot choose it over one-key sharing or eliminated materialization. The volatile companions retain observations, but they still do not print key/origin bindings.

## Source forms that can separate the evidence

Added `aggregate-constant-initializer.rs`: `const INDIRECT: [&u8;1]=[&5]; static T:[&u8;1]=INDIRECT;`. The MIR operand in T is an array-typed constant. An array carrier fails anonymous_origins' ref-carrier match for its child N. The const item itself is not a runtime MonoItem whose body is scanned. Direct &5 still supplies a whole-u8 origin for D.

Added `const-fn-initializer.rs`: a CTFE-only `const fn nested_origin()->[&'static u8;1]{[&5]}`, with `static T=nested_origin()`. T's initializer sees a FnDef call, which supplies no allocated ref carrier; prepare does not recursively scan the callee. `reachability.rs:181-209,507-540` follows the **evaluated static allocation's relocations**, not the initializer's call graph, so this helper need not be a runtime MonoItem. Its body is consequently not another source of N's typed origin. Neither fixture calls it at runtime.

For both, the static prediction is distinct D/N, equal relocation-free A, common S, frozen(D)=true and frozen(N)=false. Exact `static_source` is false for the one-byte N because T is a different relocation-bearing object. These programs stay inside existing scalar-reference/whole-object support and assert only legal byte values/equality, with no address-equality premise or new cast.

This prediction requires checking actual MIR and selected items: if conversion exposes another qualifying N carrier, folds the relevant use, or unifies the key, the new case is also NONDISCRIMINATING. New controls have **NOT_RUN** on both baseline and candidate. No source-level fatal or new proof credit is claimed.

## Compiler identity boundary and primary references

The exact nightly-2026-10-23 compiler commit was not available from the supplied summary/local metadata. Read-only upstream investigation used nearby reference `1a2c4797ef2570bd76ca5dee34449169bc7dc457`; it is **not** asserted to be that exact compiler pin. The nightly distribution manifest was inaccessible through the web reader. These references support feasibility, not exact-run binding:

- [rustc interpret allocation IDs](https://raw.githubusercontent.com/rust-lang/rust/1a2c4797ef2570bd76ca5dee34449169bc7dc457/compiler/rustc_middle/src/mir/interpret/mod.rs): reserve_and_set_memory_alloc preserves separate IDs for equal allocation contents; reserve_and_set_memory_dedup is an explicit different route. Global uniqueness by Allocation cannot be assumed.
- [CTFE interning](https://raw.githubusercontent.com/rust-lang/rust/1a2c4797ef2570bd76ca5dee34449169bc7dc457/compiler/rustc_const_eval/src/interpret/intern.rs): intern_shallow retains ID association or generates a nested static; previously global children are not automatically re-interned as a new typed source.
- [Public Allocation and MirConst](https://raw.githubusercontent.com/rust-lang/rust/1a2c4797ef2570bd76ca5dee34449169bc7dc457/compiler/rustc_public/src/ty/tys.rs): physical Allocation fields and constant operand type are separate.
- [Body conversion](https://raw.githubusercontent.com/rust-lang/rust/1a2c4797ef2570bd76ca5dee34449169bc7dc457/compiler/rustc_public_bridge/src/builder.rs): BodyBuilder builds instance MIR and evaluates constants without replacing their operand type.
- [CTFE MIR pipeline](https://raw.githubusercontent.com/rust-lang/rust/1a2c4797ef2570bd76ca5dee34449169bc7dc457/compiler/rustc_mir_transform/src/lib.rs): inner_mir_for_ctfe uses the const/static path without the optimized runtime inliner.
- [Rvalue promotion](https://raw.githubusercontent.com/rust-lang/rust/1a2c4797ef2570bd76ca5dee34449169bc7dc457/compiler/rustc_mir_transform/src/promote_consts.rs): PromoteTemps extracts eligible borrows into typed promoted constants, including in static contexts.

Conclusion: source unreachability is **not established**; marking F5 unreachable based on four PASS cases would be unsupported. The protective register change is executed/qualified at unit level; actual differing-qualification coalescing remains unestablished. Two narrow source forms now exercise the missing initializer boundary for the coordinator to discriminate.
