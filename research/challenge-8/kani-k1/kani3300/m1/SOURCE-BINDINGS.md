# KANI3300 M1 source bindings and explicit release blockers

This is a source audit of the candidate in TEST-MANIFEST.json, not an observed MIR/GOTO/runtime report.
All concrete generated AllocIds, symbols, property IDs and runtime object numbers remain UNKNOWN/NOT_RUN.
D0-A observations @ff5cabbfca remain historical, with their original bounded/incomplete evidence limits.

| Binding | Candidate source | Static rule / remaining observation |
|---|---|---|
| Compiler identity | kani_middle/anonymous_allocations.rs::AnonymousOrigin; PointsToGraph::anonymous | Compiler-local AllocId carries original Allocation, Option mask, carrier slot, addend, requested extent, frozen source Ty. Never used as runtime object ID. |
| Origin vs carrier | anonymous_origins / referent_extent | Resolve each provenance alternative to Memory or anonymous Static referent; initialized pointer addend range, target width/endianness, typed full carrier size checked. Carrier bytes do not seed the referent. |
| Independent immutability | anonymous_origins; Descriptor::admitted | A whole-referent source ConstOperand retains its pointee type before pointer casts; rustc Ty::is_freeze with fully_monomorphized TypingEnv, actual referent Mutability::Not, no referent relocations, supported existing layout and exact extent are separate conditions. Backend const flags are checked additionally, never sufficient. |
| Type erasure | prepare_immutable_allocations + observe_immutable_origins | Scan original monomorphic bodies before emission; collect later materializing constants too. Metadata survives casts in a key-indexed per-model table, so an erased codegen view cannot supply its own missing Freeze evidence. Qualification occurs at seal after all producers. |
| Some/None | AnonymousOrigin::mask; finalize descriptor/source comparison | is_some on original referent Option bytes before codegen_allocation_data/unwrap_or(0). Some(0) true, None false. Neither D(T) nor physical GOTO zero bytes determine mask. |
| Relevance | MemLoc::Anonymous; constant_successors; both analysis constant branches; InitialTargetVisitor | Keep all anonymous alternatives, including unqualified; raw_eq operands both retained. Existing casts/helpers/joins propagate whole-object aliases. Constant carrier ranges are retained as metadata; projected/runtime byte expressions stay in unchanged MIR. A whole-object edge is never claimed as an exact offset. |
| Mutable effects | existing delayed instrumentation + existing transfer code | No existing target/edge removed; common-ancestor setters and all existing destination/copy/argument/return operations remain. No new optimistic transfer alternative, typed mask or normal/unwind setter. |
| Requested key -> emitted symbol | codegen_alloc_pointer; str/slice codegen_const_ptr; bind_immutable_allocation | Bind AFTER codegen_const_allocation returns, therefore both alloc_map miss and hit use its actual direct AddressOf(Symbol). Memory and anonymous-static paths bind; named-static/vtable policies unchanged. |
| Canonical descriptor | finalize_immutable_allocations; ImmutableAllocations::register | Compare full allocation (bytes/options/align/mutability/provenance), mask, freeze qualification and exact emitted layout across every requested key sharing a symbol. A conflict involving an admitted descriptor stops emission. Compatible reuse keeps one canonical seed. No OR/intersection/overwrite, no hash-only trust. |
| Source -> emitted layout | finalizer's one-field storage check | Only one field `0: [u8; L]`, at byte offset 0, no implicit/tail padding, emitted sizeof == L; static immutable nonextern/non-TLS storage. Every source byte i maps to emitted field0[i] of size one. Named-static typed coalescing without this layout stops admission. |
| Model closure | compiler_interface::codegen_items | New GotocCtx per model; prepare before item emission, finalize after item/contract/quantifier passes and before pretty/type/vtable snapshots, split and async export. Shared BodyTransformation/cache order unchanged. Registration after seal stops. |
| Reset and private state | KaniModel::InitializeMemoryInitializationState; KaniMemoryInitializationState marker | Reuse existing markers and original reset definition; private fields tracked_object_id/tracked_offset/value checked. Missing reset definition/normal return or ambiguous private state stops emission for nonempty seeds. No new runtime ABI. |
| Reset completion -> seed | seed_returns | Preserve every original stmt/edge, splice seed block immediately before each normal Return, retaining labels and normal return expression. Original nondet object/offset, false, argument_buffer_active/selected_argument/has_witness resets in mem_init.rs:240–247 remain. |
| Live runtime bridge | finalizer's guarded seed assignment | Address of live canonical emitted symbol -> pointer_object and pointer_offset; selected usize offset < L, base offset == 0, extent fits target usize. No offset addition/overflow. Only matched in-range witness assigns mask[offset]; unmatched/out-of-bounds unchanged. |
| Empty extent | nonempty seed filter before marker/object/mask construction | L=0 creates no seed pointer-object query or mask index. Existing independent validity/call checks stay. |
| Epoch | only reset-definition returns are patched | No seed on reference/copy/call-return/alias use; repeated reset epochs each seed only before user effects. Static objects retain original global initializer materialization. |
| DFCC | unchanged contract.rs marked-state assigns handling | Existing private state is already in verifier-private assigns scope. Actual transformed/PFC roots, frame rules and first effect order still need coordinator binding. |

## Explicit release blockers (not silent coverage claims)

1. Compilation/API/type/unused/-D warnings and all unit/model outcomes are NOT_RUN. rustfmt parse/format and source inspection cannot establish compilation.
2. Exact typed source origin -> actual Some/None mask -> returned symbol/byte layout -> reset completion -> live witness -> first user effect is NOT_RUN for each C1-T/D0/own selector. Fail acceptance if any link is absent, or required raw_eq disappears. Do not treat source spelling as emitted binding.
3. Origins that have only an erased/raw view, a partial view without a retained whole-origin certificate, unavailable/uninitialized carrier addend, unsupported/unsized extent, or relocated referent receive no positive immutable seed. Existing tracked history may cover a path, but this package does NOT certify it. Until a source-bound complete tracked history or reached pre-effect Unsupported is demonstrated, each watched such path is an explicit release blocker. No blanket rejection of unrelated vtables/statics/constants was introduced.
4. Projections/joins/helpers retain whole-object relevance and original MIR runtime pointer/range expressions; no new precise per-pointer range analysis was implemented. Exact all-alternative range/effect coverage and no-overflow at each admitted read/copy require retained MIR/runtime checks and remain release blockers where not bound. Zero extent never substitutes for a nonempty control.
5. No credit for singleton/shared AB/BA closure, contract/quantifier transformed entry placement, DFCC frame behavior, source-following false copy/argument/return paths or ordinary Item destinations until reached CI bindings. This package does not repair the D0 left temporary setter, redesign cache/export lifetime, or execute M2/M3.
6. Synthetic registry conflict tests exercise the actual register API; they are not a reachable Rust-source coalescing repro. Semantic golden text alone cannot rule out failure on the other operand or earlier UB/Unsupported.

No model completion, B1/B2 proof or independent acceptance credit is claimed. Return PREPARED/BLOCKER if any required bridge remains unestablished after coordinator CI.

## Pinned API/source audit (static only)

Rust revision `7189d39d9`, matching nightly-2026-10-23, was read from primary rust-lang/rust source without running the toolchain.
`compiler/rustc_public/src/ty/tys.rs` defines Allocation `{ bytes, provenance, align, mutability }`, initialized-range `read_partial_uint`, Ty::layout;
`mir/alloc.rs` defines compiler-local AllocId and GlobalAlloc variants; `mir/mono.rs` provides resolve/body and StaticDef::eval_initializer;
`target.rs` provides pointer width and target endian; `unstable/convert/stable/mir.rs` implements internal mir::Const -> MirConst;
`compiler/rustc_middle/src/ty/util.rs:1183` provides `Ty::is_freeze(tcx, TypingEnv)` independently of backend flags.
Candidate cprover bindings were audited for pointer_object/offset result types, integer/array index constructors, struct field layout,
statement reconstruction and symbol-table replacement. New imports and private fields were source-audited for use; type/lint/compilation status remains NOT_RUN.
Snapshots and SHA256 are recorded in TEST-MANIFEST.json; library mem_init.rs, Kani markers, contract DFCC handling, ty_layout,
local initialization/reset pass, Cargo files and toolchain pin are separately hashed and unchanged from base.
